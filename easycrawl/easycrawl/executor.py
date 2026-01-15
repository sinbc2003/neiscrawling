"""
크롤러 실행 엔진
생성된 크롤러를 실행하고 진행 상황을 모니터링합니다.
"""

import subprocess
import sys
import os
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.live import Live
from rich.panel import Panel
from rich.table import Table


class CrawlerExecutor:
    """크롤러 실행 및 모니터링"""

    def __init__(self, crawler_file: str):
        """
        Args:
            crawler_file: 실행할 크롤러 파일 경로
        """
        self.crawler_file = crawler_file
        self.console = Console()

    def run(self, background: bool = False) -> int:
        """
        크롤러 실행

        Args:
            background: 백그라운드 실행 여부

        Returns:
            int: 실행 결과 (0: 성공, 1: 실패)
        """
        if not os.path.exists(self.crawler_file):
            self.console.print(f"[red]오류: 크롤러 파일을 찾을 수 없습니다: {self.crawler_file}[/red]")
            return 1

        self.console.print(Panel.fit(
            f"[bold cyan]🚀 크롤러 실행 중...[/bold cyan]\n"
            f"파일: {self.crawler_file}",
            border_style="cyan"
        ))

        try:
            if background:
                # 백그라운드 실행
                process = subprocess.Popen(
                    [sys.executable, self.crawler_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.console.print(f"[green]✅ 백그라운드에서 실행 중 (PID: {process.pid})[/green]")
                self.console.print(f"[dim]로그: crawler.log 파일을 확인하세요[/dim]")
                return 0
            else:
                # 포그라운드 실행 (실시간 출력)
                process = subprocess.Popen(
                    [sys.executable, self.crawler_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                # 실시간 출력
                for line in process.stdout:
                    print(line, end='')

                process.wait()

                if process.returncode == 0:
                    self.console.print("\n[bold green]✅ 크롤링 완료![/bold green]")
                    return 0
                else:
                    self.console.print(f"\n[red]❌ 오류 발생 (exit code: {process.returncode})[/red]")
                    return 1

        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠️  사용자가 중단했습니다[/yellow]")
            return 1
        except Exception as e:
            self.console.print(f"[red]❌ 실행 오류: {e}[/red]")
            return 1

    def validate_before_run(self) -> bool:
        """
        크롤러 실행 전 검증

        Returns:
            bool: 검증 통과 여부
        """
        self.console.print("[yellow]🔍 크롤러 검증 중...[/yellow]")

        # 파일 존재 확인
        if not os.path.exists(self.crawler_file):
            self.console.print(f"[red]❌ 파일 없음: {self.crawler_file}[/red]")
            return False

        # 문법 체크
        try:
            with open(self.crawler_file, 'r', encoding='utf-8') as f:
                code = f.read()
                compile(code, self.crawler_file, 'exec')
            self.console.print("[green]✅ 문법 검사 통과[/green]")
        except SyntaxError as e:
            self.console.print(f"[red]❌ 문법 오류: {e}[/red]")
            return False

        # 필수 라이브러리 확인
        required_libs = ['requests', 'json', 'logging']
        try:
            for lib in required_libs:
                __import__(lib)
            self.console.print("[green]✅ 필수 라이브러리 확인 완료[/green]")
        except ImportError as e:
            self.console.print(f"[red]❌ 라이브러리 누락: {e}[/red]")
            self.console.print("[yellow]pip install -r requirements.txt 를 실행하세요[/yellow]")
            return False

        return True

    def show_preview(self):
        """크롤러 설정 미리보기"""
        try:
            with open(self.crawler_file, 'r', encoding='utf-8') as f:
                code = f.read()

            # 설정값 추출
            import re

            def extract_value(pattern, default="N/A"):
                match = re.search(pattern, code)
                return match.group(1) if match else default

            base_url = extract_value(r'BASE_URL = "(.+?)"')
            list_api = extract_value(r'LIST_API = "(.+?)"')
            output_format = extract_value(r'OUTPUT_FORMAT = "(.+?)"')
            request_delay = extract_value(r'REQUEST_DELAY = ([\d.]+)')

            # 테이블로 표시
            table = Table(title="크롤러 설정", border_style="cyan")
            table.add_column("항목", style="cyan", no_wrap=True)
            table.add_column("값", style="green")

            table.add_row("기본 URL", base_url)
            table.add_row("목록 API", list_api)
            table.add_row("출력 형식", output_format)
            table.add_row("요청 딜레이", f"{request_delay}초")

            self.console.print(table)

        except Exception as e:
            self.console.print(f"[yellow]설정 미리보기 실패: {e}[/yellow]")
