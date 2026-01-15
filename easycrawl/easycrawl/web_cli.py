"""
EasyCrawl 웹 UI CLI
웹 서버를 실행하는 명령어
"""

import click
import os
import webbrowser
import threading
import time


@click.command()
@click.option('--host', default='127.0.0.1', help='서버 호스트')
@click.option('--port', default=5000, type=int, help='서버 포트')
@click.option('--debug', is_flag=True, help='디버그 모드')
@click.option('--no-browser', is_flag=True, help='브라우저 자동 열기 비활성화')
@click.option('--db-path', default='easycrawl.db', help='데이터베이스 파일 경로')
def main(host, port, debug, no_browser, db_path):
    """
    EasyCrawl 웹 UI 시작

    ChatGPT/Claude 스타일의 고급스러운 웹 인터페이스에서
    크롤러를 생성하고 관리할 수 있습니다.

    사용법:
        easycrawl-web               # 기본 설정으로 실행
        easycrawl-web --port 8000   # 다른 포트 사용
        easycrawl-web --debug       # 디버그 모드
    """
    from .web import run_web_server

    # 브라우저 자동 열기
    if not no_browser and not debug:
        def open_browser():
            time.sleep(1.5)  # 서버가 시작할 시간 대기
            webbrowser.open(f'http://{host}:{port}')

        threading.Thread(target=open_browser, daemon=True).start()

    # 웹 서버 실행
    try:
        run_web_server(
            host=host,
            port=port,
            debug=debug,
            db_path=db_path
        )
    except KeyboardInterrupt:
        print("\n\n👋 EasyCrawl을 종료합니다. 안녕히 가세요!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n문제가 계속되면 GitHub Issues에 문의해주세요:")
        print("https://github.com/yourusername/easycrawl/issues")


if __name__ == '__main__':
    main()
