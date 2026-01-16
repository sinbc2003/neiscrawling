"""
일괄 실행 관리자
여러 크롤러를 동시에 실행하고 관리
"""

import os
from datetime import datetime
from typing import List, Dict

from ..models import get_db_session, Crawler, CrawlerRun, CrawlerStatus
from .process_manager import ProcessManager


class BatchManager:
    """여러 크롤러 일괄 실행 관리"""

    def __init__(self, db_path='easycrawl.db', socketio=None):
        self.db_path = db_path
        self.process_manager = ProcessManager(db_path, socketio)

    def start_batch(
        self,
        crawler_ids: List[int],
        collection_mode: str = 'from_scratch'
    ) -> Dict:
        """
        여러 크롤러 일괄 시작

        Args:
            crawler_ids: 크롤러 ID 목록
            collection_mode: 수집 모드
                - from_scratch: 처음부터 수집 (기존 데이터 유지)
                - fresh_start: 기존 데이터 삭제 후 처음부터
                - incremental: 이어서 수집 (마지막 시점부터)

        Returns:
            실행 결과
        """
        session = get_db_session(self.db_path)
        results = []

        for crawler_id in crawler_ids:
            try:
                crawler = session.query(Crawler).filter_by(id=crawler_id).first()
                if not crawler:
                    results.append({
                        'crawler_id': crawler_id,
                        'success': False,
                        'error': 'Crawler not found'
                    })
                    continue

                # 수집 모드에 따른 처리
                self._prepare_collection(crawler, collection_mode)

                # 실행 기록 생성
                run = CrawlerRun(
                    crawler_id=crawler_id,
                    status=CrawlerStatus.RUNNING,
                    started_at=datetime.utcnow(),
                    collection_mode=collection_mode,
                    log_file_path=os.path.join(
                        os.path.dirname(crawler.code_file_path),
                        'crawler.log'
                    )
                )

                session.add(run)
                session.commit()

                run_id = run.id

                # 프로세스 시작
                process = self.process_manager.start_process(
                    run_id=run_id,
                    crawler_id=crawler_id,
                    code_file_path=crawler.code_file_path,
                    log_file_path=run.log_file_path
                )

                if process:
                    results.append({
                        'crawler_id': crawler_id,
                        'success': True,
                        'run_id': run_id,
                        'pid': process.pid
                    })
                else:
                    results.append({
                        'crawler_id': crawler_id,
                        'success': False,
                        'error': 'Failed to start process'
                    })

            except Exception as e:
                results.append({
                    'crawler_id': crawler_id,
                    'success': False,
                    'error': str(e)
                })

        session.close()

        return {
            'total': len(crawler_ids),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

    def _prepare_collection(self, crawler: Crawler, mode: str):
        """수집 모드에 따른 준비 작업"""

        if mode == 'fresh_start':
            # 기존 데이터 파일 삭제
            if crawler.output_file_path and os.path.exists(crawler.output_file_path):
                os.remove(crawler.output_file_path)

            # 체크포인트 삭제
            checkpoint_file = os.path.join(
                os.path.dirname(crawler.code_file_path),
                'crawler_checkpoint.json'
            )
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)

        elif mode == 'from_scratch':
            # 체크포인트만 삭제 (데이터는 유지)
            checkpoint_file = os.path.join(
                os.path.dirname(crawler.code_file_path),
                'crawler_checkpoint.json'
            )
            if os.path.exists(checkpoint_file):
                os.remove(checkpoint_file)

        elif mode == 'incremental':
            # 아무것도 삭제하지 않음
            # 크롤러가 체크포인트를 읽어서 이어서 수집
            pass

    def stop_all(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 중지"""
        results = []

        for run_id in run_ids:
            success = self.process_manager.stop_process(run_id)
            results.append({
                'run_id': run_id,
                'success': success
            })

        return {
            'total': len(run_ids),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

    def pause_all(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 일시정지"""
        results = []

        for run_id in run_ids:
            success = self.process_manager.pause_process(run_id)
            results.append({
                'run_id': run_id,
                'success': success
            })

        return {
            'total': len(run_ids),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

    def resume_all(self, run_ids: List[int]) -> Dict:
        """여러 크롤러 일괄 재개"""
        results = []

        for run_id in run_ids:
            success = self.process_manager.resume_process(run_id)
            results.append({
                'run_id': run_id,
                'success': success
            })

        return {
            'total': len(run_ids),
            'successful': sum(1 for r in results if r['success']),
            'failed': sum(1 for r in results if not r['success']),
            'results': results
        }

    def get_batch_status(self, run_ids: List[int]) -> List[Dict]:
        """여러 크롤러 상태 조회"""
        session = get_db_session(self.db_path)

        statuses = []
        for run_id in run_ids:
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                statuses.append(run.to_dict())

        session.close()
        return statuses
