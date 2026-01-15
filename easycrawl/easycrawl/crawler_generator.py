"""
크롤러 코드 자동 생성기
LLM 분석기가 추출한 사양을 기반으로 실제 동작하는 Python 크롤러 코드를 생성합니다.
"""

import os
from typing import Dict, Optional
from .llm_analyzer import CrawlerSpec


class CrawlerGenerator:
    """크롤러 코드 생성기"""

    def __init__(self, spec: CrawlerSpec):
        """
        Args:
            spec: LLM 분석기가 추출한 크롤러 사양
        """
        self.spec = spec

    def generate_code(
        self,
        output_format: str = "jsonl",
        request_delay: float = 0.5,
        project_name: str = "my_crawler"
    ) -> str:
        """
        크롤러 Python 코드 생성

        Args:
            output_format: 출력 형식 (json, jsonl, csv)
            request_delay: 요청 간 딜레이 (초)
            project_name: 프로젝트 이름

        Returns:
            str: 생성된 Python 코드
        """
        spec = self.spec

        # 헤더와 쿠키를 Python dict 형식으로 변환
        headers_code = self._dict_to_python(spec.headers, indent=1)
        cookies_code = self._dict_to_python(spec.cookies, indent=1)
        auth_data_code = self._dict_to_python(spec.auth_data, indent=2) if spec.auth_data else "{}"

        # 페이지네이션 로직 생성
        pagination_code = self._generate_pagination_code()

        # 데이터 추출 로직 생성
        data_extraction_code = self._generate_data_extraction_code()

        # 전체 코드 템플릿
        code = f'''"""
{project_name} - EasyCrawl로 자동 생성된 크롤러

사용법:
1. 하단의 COOKIES, HEADERS 값을 브라우저에서 복사한 값으로 업데이트
2. python {project_name}.py 실행

생성 시간: 자동 생성됨
출력 형식: {output_format.upper()}
"""

import requests
import json
import time
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List

# ============================================================
# 설정 영역 - 필요시 수정하세요
# ============================================================

# 기본 URL
BASE_URL = "{spec.base_url}"

# API 엔드포인트
LIST_API = "{spec.list_endpoint.url}"
DETAIL_API = "{spec.detail_endpoint.url if spec.detail_endpoint else ""}"

# HTTP 헤더
HEADERS = {headers_code}

# 쿠키 (브라우저에서 복사)
COOKIES = {cookies_code}

# 크롤링 설정
REQUEST_DELAY = {request_delay}  # 요청 간 딜레이 (초)
PAGE_SIZE = {spec.pagination.get('page_size', 10)}  # 한 페이지당 항목 수
OUTPUT_FORMAT = "{output_format}"  # json, jsonl, csv
OUTPUT_FILE = "{project_name}_data.{output_format}"

# ============================================================

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class {self._to_class_name(project_name)}:
    """자동 생성된 크롤러"""

    def __init__(self, cookies: Dict[str, str], headers: Dict[str, str]):
        self.session = requests.Session()

        # 쿠키 설정
        for name, value in cookies.items():
            self.session.cookies.set(name, value)

        # 헤더 설정
        self.session.headers.update(headers)

        # 체크포인트 파일
        self.checkpoint_file = "crawler_checkpoint.json"
        self.output_file = OUTPUT_FILE

    def get_list(self, {self._get_pagination_params()}) -> Optional[Dict]:
        """목록 조회"""
        {self._generate_payload_code()}

        try:
            response = self.session.{spec.list_endpoint.method.lower()}(
                f"{{BASE_URL}}{{LIST_API}}",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"목록 조회 실패: {{response.status_code}}")
                return None
        except Exception as e:
            logger.error(f"목록 조회 오류: {{e}}")
            return None

    {self._generate_detail_method() if spec.detail_endpoint else ""}

    def extract_data(self, response: Dict) -> List[Dict]:
        """응답에서 데이터 추출"""
        {data_extraction_code}

    def save_data(self, data: Dict):
        """데이터 저장"""
        if OUTPUT_FORMAT == "jsonl":
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\\n')
        elif OUTPUT_FORMAT == "json":
            # JSON 배열로 저장
            existing_data = []
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except:
                        pass
            existing_data.append(data)
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
        elif OUTPUT_FORMAT == "csv":
            import csv
            import io
            # CSV로 저장 (첫 번째 데이터로 헤더 생성)
            file_exists = os.path.exists(self.output_file)
            with open(self.output_file, 'a', encoding='utf-8', newline='') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data.keys())
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow(data)

    def save_checkpoint(self, page: int, total_collected: int):
        """진행 상황 저장"""
        checkpoint = {{
            "page": page,
            "total_collected": total_collected,
            "timestamp": datetime.now().isoformat()
        }}
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)

    def load_checkpoint(self) -> Optional[Dict]:
        """체크포인트 불러오기"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def crawl_all(self, total_items: Optional[int] = None):
        """전체 데이터 크롤링"""
        # 체크포인트 확인
        checkpoint = self.load_checkpoint()
        if checkpoint:
            start_page = checkpoint['page']
            collected_count = checkpoint['total_collected']
            logger.info(f"체크포인트에서 재개: {{collected_count}}개 수집 완료")
        else:
            start_page = 1
            collected_count = 0

        logger.info("크롤링 시작!")

        current_page = start_page
        {pagination_code}

        while True:
            # 목록 조회
            result = self.get_list({self._get_pagination_call_params()})

            if not result:
                logger.error(f"페이지 {{current_page}} 조회 실패")
                time.sleep(5)
                continue

            # 데이터 추출
            items = self.extract_data(result)

            if not items:
                logger.info("더 이상 데이터 없음 - 크롤링 완료")
                break

            # 각 항목 처리
            for item in items:
                # 상세 조회가 필요한 경우
                {self._generate_detail_call() if spec.detail_endpoint else "pass"}

                # 저장
                self.save_data(item)
                collected_count += 1

                time.sleep(REQUEST_DELAY)

            # 진행 상황 저장
            self.save_checkpoint(current_page, collected_count)
            logger.info(f"페이지 {{current_page}} 완료 | 수집: {{collected_count}}개")

            # 전체 개수를 알고 있다면 체크
            if total_items and collected_count >= total_items:
                logger.info(f"목표 달성! {{collected_count}}개 수집 완료")
                break

            # 다음 페이지
            current_page += 1
            {self._generate_pagination_update()}
            time.sleep(REQUEST_DELAY)

        logger.info(f"크롤링 완료! 총 {{collected_count}}개 수집")
        return collected_count


if __name__ == "__main__":
    print("=" * 60)
    print("{project_name} - 크롤러 시작")
    print("=" * 60)

    # 크롤러 실행
    crawler = {self._to_class_name(project_name)}(
        cookies=COOKIES,
        headers=HEADERS
    )

    # 크롤링 시작
    total = crawler.crawl_all({f"total_items={spec.total_items}" if spec.total_items else ""})

    print(f"\\n완료! 총 {{total}}개 데이터 수집")
    print(f"저장 위치: {{OUTPUT_FILE}}")
'''

        return code

    def save_to_file(
        self,
        code: str,
        output_dir: str = ".",
        filename: Optional[str] = None
    ) -> str:
        """
        생성된 코드를 파일로 저장

        Args:
            code: 생성된 크롤러 코드
            output_dir: 출력 디렉토리
            filename: 파일명 (없으면 자동 생성)

        Returns:
            str: 저장된 파일 경로
        """
        if not filename:
            filename = "generated_crawler.py"

        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)

        return filepath

    # ============================================================
    # 헬퍼 메서드
    # ============================================================

    def _to_class_name(self, name: str) -> str:
        """프로젝트 이름을 클래스 이름으로 변환"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def _dict_to_python(self, d: Dict, indent: int = 0) -> str:
        """Dict을 Python 코드로 변환"""
        if not d:
            return "{}"

        indent_str = "    " * indent
        lines = ["{"]
        for key, value in d.items():
            lines.append(f'{indent_str}    "{key}": "{value}",')
        lines.append(f"{indent_str}}}")
        return "\n".join(lines)

    def _get_pagination_params(self) -> str:
        """페이지네이션 파라미터 생성"""
        pag = self.spec.pagination
        if pag['type'] == 'offset':
            return f"{pag['start_param']}: int = 0, {pag['page_param']}: int = 1"
        elif pag['type'] == 'page':
            return f"{pag['page_param']}: int = 1"
        else:  # cursor
            return f"cursor: str = ''"

    def _get_pagination_call_params(self) -> str:
        """페이지네이션 호출 파라미터"""
        pag = self.spec.pagination
        if pag['type'] == 'offset':
            return f"{pag['start_param']}=current_offset, {pag['page_param']}=current_page"
        elif pag['type'] == 'page':
            return f"{pag['page_param']}=current_page"
        else:
            return "cursor=current_cursor"

    def _generate_pagination_code(self) -> str:
        """페이지네이션 초기화 코드"""
        pag = self.spec.pagination
        if pag['type'] == 'offset':
            return f"current_offset = (start_page - 1) * PAGE_SIZE"
        return ""

    def _generate_pagination_update(self) -> str:
        """페이지네이션 업데이트 코드"""
        pag = self.spec.pagination
        if pag['type'] == 'offset':
            return "current_offset += PAGE_SIZE"
        return ""

    def _generate_payload_code(self) -> str:
        """API 요청 payload 생성 코드"""
        pag = self.spec.pagination

        if pag['type'] == 'offset':
            return f'''payload = {{
            "data": {{
                "{pag['start_param']}": {pag['start_param']},
                "{pag['page_param']}": {pag['page_param']}
            }}
        }}'''
        else:
            return '''payload = {}  # 필요에 따라 수정하세요'''

    def _generate_data_extraction_code(self) -> str:
        """데이터 추출 코드 생성"""
        path_parts = self.spec.data_path.split('.')

        code = "try:\n"
        code += "            data = response\n"
        for part in path_parts:
            code += f"            data = data.get('{part}', [])\n"
        code += "            return data if isinstance(data, list) else []\n"
        code += "        except Exception as e:\n"
        code += "            logger.error(f'데이터 추출 오류: {e}')\n"
        code += "            return []"

        return code

    def _generate_detail_method(self) -> str:
        """상세 조회 메서드 생성"""
        if not self.spec.detail_endpoint:
            return ""

        return f'''def get_detail(self, item_id: str) -> Optional[Dict]:
        """상세 정보 조회"""
        payload = {{
            "data": {{
                "{self.spec.id_field}": item_id
            }}
        }}

        try:
            response = self.session.{self.spec.detail_endpoint.method.lower()}(
                f"{{BASE_URL}}{{DETAIL_API}}",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"상세 조회 실패 ({{item_id}}): {{response.status_code}}")
                return None
        except Exception as e:
            logger.error(f"상세 조회 오류 ({{item_id}}): {{e}}")
            return None
    '''

    def _generate_detail_call(self) -> str:
        """상세 조회 호출 코드"""
        return f'''item_id = item.get('{self.spec.id_field}')
                if item_id:
                    detail = self.get_detail(item_id)
                    if detail:
                        item.update(detail)'''
