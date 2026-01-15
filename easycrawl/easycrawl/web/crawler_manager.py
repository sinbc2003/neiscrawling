"""
크롤러 관리자
크롤러의 생성, 실행, 일시정지, 재개, 취소 등을 관리
"""

import os
import subprocess
import signal
import json
import threading
import time
from datetime import datetime
from typing import Optional, Dict, List

from .models import get_db_session, Crawler, CrawlerRun, CrawlerStatus
from ..llm_analyzer import LLMAnalyzer
from ..crawler_generator import CrawlerGenerator


class CrawlerManager:
    """크롤러 생성 및 실행 관리"""

    def __init__(self, db_path='easycrawl.db', socketio=None):
        self.db_path = db_path
        self.socketio = socketio
        self.running_processes = {}  # {run_id: subprocess.Popen}
        self.monitor_threads = {}    # {run_id: threading.Thread}

    def get_session(self):
        """DB 세션 가져오기"""
        return get_db_session(self.db_path)

    def create_crawler(
        self,
        name: str,
        curl_command: str,
        api_key: str,
        description: str = "",
        output_format: str = "jsonl",
        request_delay: int = 500,
        additional_info: str = "",
        tags: List[str] = None
    ) -> Dict:
        """
        새 크롤러 생성

        Args:
            name: 크롤러 이름
            curl_command: curl 명령어
            api_key: Claude API 키
            description: 설명
            output_format: 출력 형식
            request_delay: 요청 딜레이 (밀리초)
            additional_info: 추가 정보
            tags: 태그 목록

        Returns:
            생성된 크롤러 정보
        """
        session = self.get_session()

        try:
            # LLM으로 분석
            analyzer = LLMAnalyzer(api_key=api_key)
            spec = analyzer.analyze_curl(curl_command, additional_info)

            # 크롤러 코드 생성
            generator = CrawlerGenerator(spec)
            code = generator.generate_code(
                output_format=output_format,
                request_delay=request_delay / 1000.0,  # 초로 변환
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

        # 검색
        if search:
            query = query.filter(
                Crawler.name.contains(search) |
                Crawler.description.contains(search)
            )

        # 태그 필터
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

    def start_crawler(self, crawler_id: int, from_scratch: bool = False) -> Dict:
        """
        크롤러 시작

        Args:
            crawler_id: 크롤러 ID
            from_scratch: 처음부터 시작 (체크포인트 무시)
        """
        session = self.get_session()

        try:
            crawler = session.query(Crawler).filter_by(id=crawler_id).first()
            if not crawler:
                return {'success': False, 'error': 'Crawler not found'}

            # 실행 기록 생성
            run = CrawlerRun(
                crawler_id=crawler_id,
                status=CrawlerStatus.RUNNING,
                started_at=datetime.utcnow(),
                log_file_path=os.path.join(
                    os.path.dirname(crawler.code_file_path),
                    'crawler.log'
                )
            )

            session.add(run)
            session.commit()

            run_id = run.id

            # 체크포인트 삭제 (처음부터 시작)
            if from_scratch:
                checkpoint_file = os.path.join(
                    os.path.dirname(crawler.code_file_path),
                    'crawler_checkpoint.json'
                )
                if os.path.exists(checkpoint_file):
                    os.remove(checkpoint_file)

            # 크롤러 실행
            process = subprocess.Popen(
                ['python', crawler.code_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            run.pid = process.pid
            session.commit()

            # 프로세스 저장
            self.running_processes[run_id] = process

            # 모니터링 스레드 시작
            monitor_thread = threading.Thread(
                target=self._monitor_crawler,
                args=(run_id, crawler_id, process),
                daemon=True
            )
            monitor_thread.start()
            self.monitor_threads[run_id] = monitor_thread

            session.close()

            return {'success': True, 'run_id': run_id, 'pid': process.pid}

        except Exception as e:
            session.rollback()
            session.close()
            return {'success': False, 'error': str(e)}

    def pause_crawler(self, run_id: int) -> Dict:
        """크롤러 일시정지"""
        if run_id not in self.running_processes:
            return {'success': False, 'error': 'Process not found'}

        try:
            process = self.running_processes[run_id]
            os.kill(process.pid, signal.SIGSTOP)

            session = self.get_session()
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.PAUSED
                run.paused_at = datetime.utcnow()
                session.commit()
            session.close()

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def resume_crawler(self, run_id: int) -> Dict:
        """크롤러 재개"""
        if run_id not in self.running_processes:
            return {'success': False, 'error': 'Process not found'}

        try:
            process = self.running_processes[run_id]
            os.kill(process.pid, signal.SIGCONT)

            session = self.get_session()
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.RUNNING
                session.commit()
            session.close()

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def stop_crawler(self, run_id: int) -> Dict:
        """크롤러 중지"""
        if run_id not in self.running_processes:
            return {'success': False, 'error': 'Process not found'}

        try:
            process = self.running_processes[run_id]
            process.terminate()
            process.wait(timeout=5)

            session = self.get_session()
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.CANCELLED
                run.completed_at = datetime.utcnow()
                session.commit()
            session.close()

            del self.running_processes[run_id]

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': str(e)}

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

    def _monitor_crawler(self, run_id: int, crawler_id: int, process: subprocess.Popen):
        """크롤러 모니터링 (별도 스레드)"""
        session = self.get_session()

        while True:
            # 프로세스 종료 확인
            if process.poll() is not None:
                # 프로세스 종료됨
                run = session.query(CrawlerRun).filter_by(id=run_id).first()
                if run:
                    if process.returncode == 0:
                        run.status = CrawlerStatus.COMPLETED
                    else:
                        run.status = CrawlerStatus.FAILED
                        # 에러 메시지 읽기
                        stderr = process.stderr.read() if process.stderr else ""
                        run.error_message = stderr[:1000]  # 처음 1000자만

                    run.completed_at = datetime.utcnow()
                    session.commit()

                # 웹소켓으로 알림
                if self.socketio:
                    self.socketio.emit('crawler_finished', {
                        'run_id': run_id,
                        'status': run.status.value if run else 'unknown'
                    })

                if run_id in self.running_processes:
                    del self.running_processes[run_id]

                break

            # 체크포인트 읽기
            crawler = session.query(Crawler).filter_by(id=crawler_id).first()
            if crawler:
                checkpoint_file = os.path.join(
                    os.path.dirname(crawler.code_file_path),
                    'crawler_checkpoint.json'
                )

                if os.path.exists(checkpoint_file):
                    try:
                        with open(checkpoint_file, 'r') as f:
                            checkpoint = json.load(f)

                        run = session.query(CrawlerRun).filter_by(id=run_id).first()
                        if run:
                            run.checkpoint = checkpoint
                            run.collected_items = checkpoint.get('total_collected', 0)
                            session.commit()

                            # 웹소켓으로 진행상황 전송
                            if self.socketio:
                                self.socketio.emit('crawler_progress', {
                                    'run_id': run_id,
                                    'collected': run.collected_items,
                                    'progress': run.to_dict()['progress']
                                })

                    except Exception as e:
                        pass

            time.sleep(2)  # 2초마다 체크

        session.close()
