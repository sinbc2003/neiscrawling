"""
크롤러 관리자 (통합 인터페이스)
실제 기능은 managers 패키지로 위임
"""

import os
from typing import Optional, Dict, List

from .models import get_db_session, Crawler, CrawlerRun, CrawlerStatus
from .managers import ProcessManager, BatchManager
from ..llm_analyzer import LLMAnalyzer
from ..crawler_generator import CrawlerGenerator


class CrawlerManager:
    """크롤러 생성 및 실행 관리 (통합 인터페이스)"""

    def __init__(self, db_path='easycrawl.db', socketio=None):
        self.db_path = db_path
        self.socketio = socketio

        # 하위 관리자들
        self.process_manager = ProcessManager(db_path, socketio)
        self.batch_manager = BatchManager(db_path, socketio)

    def get_session(self):
        """DB 세션 가져오기"""
        return get_db_session(self.db_path)

    # ============================================================
    # 크롤러 CRUD
    # ============================================================

    def create_crawler(
        self,
        name: str,
        curl_command: str,
        api_key: str,
        website_url: str = "",
        description: str = "",
        output_format: str = "jsonl",
        request_delay: int = 500,
        additional_info: str = "",
        tags: List[str] = None
    ) -> Dict:
        """새 크롤러 생성"""
        session = self.get_session()

        try:
            # LLM으로 분석
            analyzer = LLMAnalyzer(api_key=api_key)
            spec = analyzer.analyze_curl(curl_command, additional_info)

            # 크롤러 코드 생성
            generator = CrawlerGenerator(spec)
            code = generator.generate_code(
                output_format=output_format,
                request_delay=request_delay / 1000.0,
                project_name=name
            )

            # 파일 저장
            output_dir = os.path.join('crawlers', name)
            os.makedirs(output_dir, exist_ok=True)

            code_file = os.path.join(output_dir, f'{name}.py')
            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(code)

            output_file = os.path.join(output_dir, f'{name}_data.{output_format}')

            # DB에 저장
            crawler = Crawler(
                name=name,
                website_url=website_url,
                description=description,
                spec=spec.dict(),
                output_format=output_format,
                request_delay=request_delay,
                code_file_path=code_file,
                output_file_path=output_file,
                tags=','.join(tags) if tags else ''
            )

            session.add(crawler)
            session.commit()

            result = crawler.to_dict()
            session.close()

            return {'success': True, 'crawler': result}

        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'error': str(e)}

    def list_crawlers(self, search: str = "", tag: str = "") -> List[Dict]:
        """크롤러 목록 조회"""
        session = self.get_session()

        query = session.query(Crawler)

        if search:
            query = query.filter(
                Crawler.name.contains(search) |
                Crawler.description.contains(search)
            )

        if tag:
            query = query.filter(Crawler.tags.contains(tag))

        crawlers = query.order_by(Crawler.created_at.desc()).all()
        result = [c.to_dict() for c in crawlers]

        session.close()
        return result

    def get_crawler(self, crawler_id: int) -> Optional[Dict]:
        """크롤러 상세 정보"""
        session = self.get_session()
        crawler = session.query(Crawler).filter_by(id=crawler_id).first()

        if not crawler:
            session.close()
            return None

        result = crawler.to_dict()

        # 최근 실행 기록 추가
        runs = session.query(CrawlerRun).filter_by(crawler_id=crawler_id).order_by(
            CrawlerRun.created_at.desc()
        ).limit(10).all()

        result['recent_runs'] = [r.to_dict() for r in runs]

        session.close()
        return result

    def delete_crawler(self, crawler_id: int) -> Dict:
        """크롤러 삭제"""
        session = self.get_session()

        try:
            crawler = session.query(Crawler).filter_by(id=crawler_id).first()
            if not crawler:
                return {'success': False, 'error': 'Crawler not found'}

            # 실행 기록도 삭제
            session.query(CrawlerRun).filter_by(crawler_id=crawler_id).delete()

            # 파일 삭제
            if crawler.code_file_path and os.path.exists(crawler.code_file_path):
                os.remove(crawler.code_file_path)

            session.delete(crawler)
            session.commit()
            session.close()

            return {'success': True}

        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'error': str(e)}

    # ============================================================
    # 단일 크롤러 실행 제어
    # ============================================================

    def start_crawler(
        self,
        crawler_id: int,
        from_scratch: bool = False,
        collection_mode: str = 'from_scratch'
    ) -> Dict:
        """
        크롤러 시작

        Args:
            crawler_id: 크롤러 ID
            from_scratch: 처음부터 시작 (하위 호환성 유지)
            collection_mode: 수집 모드
                - from_scratch: 처음부터 수집
                - fresh_start: 데이터 삭제 후 처음부터
                - incremental: 이어서 수집
        """
        # from_scratch가 True면 collection_mode 덮어쓰기
        if from_scratch:
            collection_mode = 'from_scratch'

        return self.batch_manager.start_batch([crawler_id], collection_mode)['results'][0]

    def pause_crawler(self, run_id: int) -> Dict:
        """크롤러 일시정지"""
        success = self.process_manager.pause_process(run_id)
        return {'success': success}

    def resume_crawler(self, run_id: int) -> Dict:
        """크롤러 재개"""
        success = self.process_manager.resume_process(run_id)
        return {'success': success}

    def stop_crawler(self, run_id: int) -> Dict:
        """크롤러 중지"""
        success = self.process_manager.stop_process(run_id)
        return {'success': success}

    def get_run_status(self, run_id: int) -> Optional[Dict]:
        """실행 상태 조회"""
        session = self.get_session()
        run = session.query(CrawlerRun).filter_by(id=run_id).first()

        if not run:
            session.close()
            return None

        result = run.to_dict()
        session.close()
        return result

    # ============================================================
    # 일괄 실행 제어 (BatchManager로 위임)
    # ============================================================

    def start_batch(self, crawler_ids: List[int], collection_mode: str = 'from_scratch') -> Dict:
        """여러 크롤러 일괄 시작"""
        return self.batch_manager.start_batch(crawler_ids, collection_mode)

    def stop_batch(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 중지"""
        return self.batch_manager.stop_all(run_ids)

    def pause_batch(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 일시정지"""
        return self.batch_manager.pause_all(run_ids)

    def resume_batch(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 재개"""
        return self.batch_manager.resume_all(run_ids)

    def get_batch_status(self, run_ids: List[int]) -> List[Dict]:
        """여러 크롤러 상태 조회"""
        return self.batch_manager.get_batch_status(run_ids)
