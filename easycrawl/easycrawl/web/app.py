"""
EasyCrawl 웹 애플리케이션
ChatGPT/Claude 스타일의 고급스러운 웹 UI
"""

import os
import sys
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

from .models import init_db, get_db_session
from .routes import register_routes
from .crawler_manager import CrawlerManager

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(db_path='easycrawl.db'):
    """Flask 앱 생성"""

    # Flask 앱 초기화
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # 설정
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'easycrawl-secret-key-change-in-production')
    app.config['DB_PATH'] = db_path

    # CORS 활성화
    CORS(app)

    # SocketIO 초기화 (실시간 업데이트용)
    socketio = SocketIO(app, cors_allowed_origins="*")

    # 데이터베이스 초기화
    try:
        session = init_db(db_path)
        logger.info(f"데이터베이스 초기화 완료: {db_path}")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

    # 크롤러 매니저 초기화
    crawler_manager = CrawlerManager(db_path=db_path, socketio=socketio)
    app.crawler_manager = crawler_manager

    # API 라우트 등록
    register_routes(app, crawler_manager)

    # 웹소켓 이벤트
    @socketio.on('connect')
    def handle_connect():
        logger.info('클라이언트 연결됨')
        emit('connected', {'status': 'ok'})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('클라이언트 연결 해제됨')

    # 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    app.socketio = socketio

    return app


def run_web_server(host='127.0.0.1', port=5000, debug=False, db_path='easycrawl.db'):
    """웹 서버 실행"""

    print("=" * 60)
    print("🎉 EasyCrawl 웹 UI 시작!")
    print("=" * 60)
    print(f"\n🌐 브라우저에서 열기: http://{host}:{port}")
    print("\n💡 팁:")
    print("  - Ctrl+C 를 눌러 종료")
    print("  - 크롤러 히스토리는 사이드바에서 확인")
    print("  - 실행 중인 크롤러는 실시간으로 진행상황 표시")
    print("\n" + "=" * 60 + "\n")

    app = create_app(db_path=db_path)

    # SocketIO로 실행
    app.socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )


if __name__ == '__main__':
    run_web_server(debug=True)
