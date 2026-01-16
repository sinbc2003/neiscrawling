"""
API 라우트
"""

from flask import render_template, request, jsonify, send_file
import os


def register_routes(app, crawler_manager):
    """API 라우트 등록"""

    @app.route('/')
    def index():
        """메인 페이지"""
        return render_template('index.html')

    @app.route('/api/crawlers', methods=['GET'])
    def list_crawlers():
        """크롤러 목록 조회"""
        search = request.args.get('search', '')
        tag = request.args.get('tag', '')
        crawlers = crawler_manager.list_crawlers(search=search, tag=tag)
        return jsonify({'crawlers': crawlers})

    @app.route('/api/crawlers', methods=['POST'])
    def create_crawler():
        """새 크롤러 생성"""
        data = request.json

        required_fields = ['name', 'curl_command', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        result = crawler_manager.create_crawler(
            name=data['name'],
            curl_command=data['curl_command'],
            api_key=data['api_key'],
            website_url=data.get('website_url', ''),
            description=data.get('description', ''),
            output_format=data.get('output_format', 'jsonl'),
            request_delay=data.get('request_delay', 500),
            additional_info=data.get('additional_info', ''),
            tags=data.get('tags', [])
        )

        return jsonify(result)

    @app.route('/api/crawlers/<int:crawler_id>', methods=['GET'])
    def get_crawler(crawler_id):
        """크롤러 상세 조회"""
        crawler = crawler_manager.get_crawler(crawler_id)
        if not crawler:
            return jsonify({'error': 'Crawler not found'}), 404
        return jsonify({'crawler': crawler})

    @app.route('/api/crawlers/<int:crawler_id>', methods=['DELETE'])
    def delete_crawler(crawler_id):
        """크롤러 삭제"""
        result = crawler_manager.delete_crawler(crawler_id)
        return jsonify(result)

    @app.route('/api/crawlers/<int:crawler_id>/start', methods=['POST'])
    def start_crawler(crawler_id):
        """크롤러 시작"""
        data = request.json or {}
        from_scratch = data.get('from_scratch', False)
        collection_mode = data.get('collection_mode', 'from_scratch')

        result = crawler_manager.start_crawler(
            crawler_id,
            from_scratch=from_scratch,
            collection_mode=collection_mode
        )
        return jsonify(result)

    @app.route('/api/batch/start', methods=['POST'])
    def start_batch():
        """여러 크롤러 일괄 시작"""
        data = request.json or {}
        crawler_ids = data.get('crawler_ids', [])
        collection_mode = data.get('collection_mode', 'from_scratch')

        if not crawler_ids:
            return jsonify({'success': False, 'error': 'No crawler IDs provided'}), 400

        result = crawler_manager.start_batch(crawler_ids, collection_mode)
        return jsonify(result)

    @app.route('/api/batch/stop', methods=['POST'])
    def stop_batch():
        """여러 크롤러 일괄 중지"""
        data = request.json or {}
        run_ids = data.get('run_ids', [])

        if not run_ids:
            return jsonify({'success': False, 'error': 'No run IDs provided'}), 400

        result = crawler_manager.stop_batch(run_ids)
        return jsonify(result)

    @app.route('/api/batch/pause', methods=['POST'])
    def pause_batch():
        """여러 크롤러 일괄 일시정지"""
        data = request.json or {}
        run_ids = data.get('run_ids', [])

        if not run_ids:
            return jsonify({'success': False, 'error': 'No run IDs provided'}), 400

        result = crawler_manager.pause_batch(run_ids)
        return jsonify(result)

    @app.route('/api/batch/resume', methods=['POST'])
    def resume_batch():
        """여러 크롤러 일괄 재개"""
        data = request.json or {}
        run_ids = data.get('run_ids', [])

        if not run_ids:
            return jsonify({'success': False, 'error': 'No run IDs provided'}), 400

        result = crawler_manager.resume_batch(run_ids)
        return jsonify(result)

    @app.route('/api/runs/<int:run_id>/pause', methods=['POST'])
    def pause_crawler(run_id):
        """크롤러 일시정지"""
        result = crawler_manager.pause_crawler(run_id)
        return jsonify(result)

    @app.route('/api/runs/<int:run_id>/resume', methods=['POST'])
    def resume_crawler(run_id):
        """크롤러 재개"""
        result = crawler_manager.resume_crawler(run_id)
        return jsonify(result)

    @app.route('/api/runs/<int:run_id>/stop', methods=['POST'])
    def stop_crawler(run_id):
        """크롤러 중지"""
        result = crawler_manager.stop_crawler(run_id)
        return jsonify(result)

    @app.route('/api/runs/<int:run_id>/status', methods=['GET'])
    def get_run_status(run_id):
        """실행 상태 조회"""
        status = crawler_manager.get_run_status(run_id)
        if not status:
            return jsonify({'error': 'Run not found'}), 404
        return jsonify({'run': status})

    @app.route('/api/crawlers/<int:crawler_id>/download', methods=['GET'])
    def download_data(crawler_id):
        """수집된 데이터 다운로드"""
        crawler = crawler_manager.get_crawler(crawler_id)
        if not crawler:
            return jsonify({'error': 'Crawler not found'}), 404

        output_file = crawler.get('output_file_path')
        if not output_file or not os.path.exists(output_file):
            return jsonify({'error': 'Data file not found'}), 404

        return send_file(
            output_file,
            as_attachment=True,
            download_name=os.path.basename(output_file)
        )

    @app.route('/api/crawlers/<int:crawler_id>/code', methods=['GET'])
    def view_code(crawler_id):
        """생성된 코드 보기"""
        crawler = crawler_manager.get_crawler(crawler_id)
        if not crawler:
            return jsonify({'error': 'Crawler not found'}), 404

        code_file = crawler.get('code_file_path')
        if not code_file or not os.path.exists(code_file):
            return jsonify({'error': 'Code file not found'}), 404

        with open(code_file, 'r', encoding='utf-8') as f:
            code = f.read()

        return jsonify({'code': code})

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """헬스 체크"""
        return jsonify({'status': 'ok'})
