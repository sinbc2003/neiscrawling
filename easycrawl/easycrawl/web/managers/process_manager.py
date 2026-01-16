"""
프로세스 관리자
크롤러 프로세스의 시작, 중지, 일시정지, 재개를 담당
"""

import os
import subprocess
import signal
import threading
import time
import json
from datetime import datetime
from typing import Dict, Optional

from ..models import get_db_session, CrawlerRun, CrawlerStatus


class ProcessManager:
    """크롤러 프로세스 관리"""

    def __init__(self, db_path='easycrawl.db', socketio=None):
        self.db_path = db_path
        self.socketio = socketio
        self.running_processes = {}  # {run_id: subprocess.Popen}
        self.monitor_threads = {}    # {run_id: threading.Thread}

    def start_process(
        self,
        run_id: int,
        crawler_id: int,
        code_file_path: str,
        log_file_path: str
    ) -> Optional[subprocess.Popen]:
        """
        크롤러 프로세스 시작

        Args:
            run_id: 실행 기록 ID
            crawler_id: 크롤러 ID
            code_file_path: 크롤러 코드 파일 경로
            log_file_path: 로그 파일 경로

        Returns:
            subprocess.Popen 또는 None
        """
        try:
            # 프로세스 시작
            process = subprocess.Popen(
                ['python', code_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # 프로세스 저장
            self.running_processes[run_id] = process

            # DB 업데이트
            session = get_db_session(self.db_path)
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.pid = process.pid
                run.status = CrawlerStatus.RUNNING
                session.commit()
            session.close()

            # 모니터링 시작
            self._start_monitoring(run_id, crawler_id, process)

            return process

        except Exception as e:
            print(f"프로세스 시작 오류: {e}")
            return None

    def pause_process(self, run_id: int) -> bool:
        """프로세스 일시정지"""
        if run_id not in self.running_processes:
            return False

        try:
            process = self.running_processes[run_id]
            os.kill(process.pid, signal.SIGSTOP)

            # DB 업데이트
            session = get_db_session(self.db_path)
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.PAUSED
                run.paused_at = datetime.utcnow()
                session.commit()
            session.close()

            return True

        except Exception as e:
            print(f"프로세스 일시정지 오류: {e}")
            return False

    def resume_process(self, run_id: int) -> bool:
        """프로세스 재개"""
        if run_id not in self.running_processes:
            return False

        try:
            process = self.running_processes[run_id]
            os.kill(process.pid, signal.SIGCONT)

            # DB 업데이트
            session = get_db_session(self.db_path)
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.RUNNING
                session.commit()
            session.close()

            return True

        except Exception as e:
            print(f"프로세스 재개 오류: {e}")
            return False

    def stop_process(self, run_id: int) -> bool:
        """프로세스 중지"""
        if run_id not in self.running_processes:
            return False

        try:
            process = self.running_processes[run_id]
            process.terminate()
            process.wait(timeout=5)

            # DB 업데이트
            session = get_db_session(self.db_path)
            run = session.query(CrawlerRun).filter_by(id=run_id).first()
            if run:
                run.status = CrawlerStatus.CANCELLED
                run.completed_at = datetime.utcnow()
                session.commit()
            session.close()

            # 프로세스 제거
            if run_id in self.running_processes:
                del self.running_processes[run_id]

            return True

        except Exception as e:
            print(f"프로세스 중지 오류: {e}")
            return False

    def is_running(self, run_id: int) -> bool:
        """프로세스 실행 중인지 확인"""
        if run_id not in self.running_processes:
            return False

        process = self.running_processes[run_id]
        return process.poll() is None

    def get_process_status(self, run_id: int) -> Optional[str]:
        """프로세스 상태 조회"""
        if run_id not in self.running_processes:
            return None

        process = self.running_processes[run_id]
        if process.poll() is None:
            return "running"
        else:
            return "finished"

    def _start_monitoring(self, run_id: int, crawler_id: int, process: subprocess.Popen):
        """프로세스 모니터링 시작"""
        monitor_thread = threading.Thread(
            target=self._monitor_process,
            args=(run_id, crawler_id, process),
            daemon=True
        )
        monitor_thread.start()
        self.monitor_threads[run_id] = monitor_thread

    def _monitor_process(self, run_id: int, crawler_id: int, process: subprocess.Popen):
        """프로세스 모니터링 (별도 스레드)"""
        session = get_db_session(self.db_path)

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
                        run.error_message = stderr[:1000]

                    run.completed_at = datetime.utcnow()
                    session.commit()

                # 웹소켓 알림
                if self.socketio:
                    self.socketio.emit('crawler_finished', {
                        'run_id': run_id,
                        'status': run.status.value if run else 'unknown'
                    })

                # 프로세스 제거
                if run_id in self.running_processes:
                    del self.running_processes[run_id]

                break

            # 체크포인트 읽기 및 진행상황 업데이트
            self._update_progress(session, run_id, crawler_id)

            time.sleep(2)  # 2초마다 체크

        session.close()

    def _update_progress(self, session, run_id: int, crawler_id: int):
        """진행 상황 업데이트"""
        from ..models import Crawler

        crawler = session.query(Crawler).filter_by(id=crawler_id).first()
        if not crawler:
            return

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

                    # 마지막 수집 항목 정보 업데이트
                    if 'last_id' in checkpoint:
                        run.last_collected_id = checkpoint['last_id']
                    if 'last_date' in checkpoint:
                        run.last_collected_date = checkpoint['last_date']

                    session.commit()

                    # 웹소켓으로 진행 상황 전송
                    if self.socketio:
                        self.socketio.emit('crawler_progress', {
                            'run_id': run_id,
                            'collected': run.collected_items,
                            'progress': run.to_dict()['progress']
                        })

            except Exception as e:
                pass

    def cleanup_finished_processes(self):
        """종료된 프로세스 정리"""
        finished_runs = []
        for run_id, process in self.running_processes.items():
            if process.poll() is not None:
                finished_runs.append(run_id)

        for run_id in finished_runs:
            del self.running_processes[run_id]
