"""
LLM 기반 API 분석기
사용자가 제공한 curl 명령어나 브라우저 정보를 분석하여
크롤러 생성에 필요한 정보를 추출합니다.
"""

import json
import re
from typing import Dict, List, Optional
from anthropic import Anthropic
from pydantic import BaseModel, Field


class APIEndpoint(BaseModel):
    """API 엔드포인트 정보"""
    url: str
    method: str = "POST"
    description: str


class CrawlerSpec(BaseModel):
    """크롤러 사양"""
    base_url: str = Field(description="기본 URL (예: https://help.neis.go.kr)")
    list_endpoint: APIEndpoint = Field(description="목록 조회 API")
    detail_endpoint: Optional[APIEndpoint] = Field(None, description="상세 조회 API")

    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP 헤더")
    cookies: Dict[str, str] = Field(default_factory=dict, description="쿠키")

    auth_data: Dict = Field(default_factory=dict, description="인증 데이터")

    pagination: Dict = Field(
        default_factory=lambda: {
            "type": "offset",  # offset, page, cursor
            "start_param": "startCount",
            "page_param": "pageIndex",
            "page_size": 10
        },
        description="페이지네이션 방식"
    )

    data_path: str = Field("data.items", description="응답에서 데이터 배열 경로")
    id_field: str = Field("id", description="각 항목의 고유 ID 필드")

    total_items: Optional[int] = Field(None, description="전체 데이터 개수")


class LLMAnalyzer:
    """LLM을 사용하여 curl 명령어나 API 정보를 분석"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Anthropic API 키 (없으면 환경변수에서 읽음)
        """
        self.client = Anthropic(api_key=api_key)

    def analyze_curl(self, curl_command: str, additional_info: str = "") -> CrawlerSpec:
        """
        curl 명령어를 분석하여 크롤러 사양 추출

        Args:
            curl_command: 브라우저에서 복사한 curl 명령어
            additional_info: 추가 설명 (전체 데이터 개수, 페이지네이션 방식 등)

        Returns:
            CrawlerSpec: 크롤러 사양
        """
        prompt = f"""
당신은 웹 크롤러 전문가입니다. 사용자가 브라우저 개발자도구에서 복사한 curl 명령어를 분석하여
크롤러를 만드는데 필요한 정보를 JSON 형식으로 추출해주세요.

<curl_command>
{curl_command}
</curl_command>

{f"<additional_info>{additional_info}</additional_info>" if additional_info else ""}

다음 정보를 JSON 형식으로 추출해주세요:

1. base_url: 기본 URL (프로토콜 + 도메인)
2. list_endpoint: 목록 조회 API
   - url: 엔드포인트 경로
   - method: HTTP 메서드
   - description: 이 API가 하는 일
3. headers: HTTP 헤더 (dict)
4. cookies: 쿠키 (dict)
5. pagination: 페이지네이션 정보
   - type: "offset", "page", "cursor" 중 하나
   - start_param: 시작 위치 파라미터 이름
   - page_param: 페이지 번호 파라미터 이름
   - page_size: 한 페이지당 항목 수
6. data_path: 응답 JSON에서 데이터 배열이 있는 경로 (예: "data.items", "result.list")
7. id_field: 각 항목의 고유 ID 필드명

응답은 반드시 다음 JSON 스키마를 따라주세요:
{{
  "base_url": "https://example.com",
  "list_endpoint": {{
    "url": "/api/list",
    "method": "POST",
    "description": "목록 조회"
  }},
  "headers": {{}},
  "cookies": {{}},
  "pagination": {{
    "type": "offset",
    "start_param": "start",
    "page_param": "page",
    "page_size": 10
  }},
  "data_path": "data.items",
  "id_field": "id"
}}

**중요**: JSON만 출력하고 다른 설명은 붙이지 마세요.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        # 응답에서 JSON 추출
        content = response.content[0].text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("LLM 응답에서 JSON을 찾을 수 없습니다.")

        spec_data = json.loads(json_match.group())
        return CrawlerSpec(**spec_data)

    def analyze_interactive(self) -> CrawlerSpec:
        """
        대화형으로 사용자에게 정보를 받아 크롤러 사양 생성

        Returns:
            CrawlerSpec: 크롤러 사양
        """
        from rich.console import Console
        from rich.prompt import Prompt, Confirm

        console = Console()

        console.print("\n[bold cyan]🤖 AI가 크롤러 정보를 분석합니다![/bold cyan]\n")

        # curl 명령어 입력
        console.print("[yellow]1단계: curl 명령어 붙여넣기[/yellow]")
        console.print("   브라우저 개발자도구(F12) > Network 탭 > API 호출 우클릭")
        console.print("   > Copy > Copy as cURL 선택 후 붙여넣으세요\n")

        curl_lines = []
        console.print("[dim]여러 줄 입력 후 빈 줄에서 Enter를 누르면 완료됩니다.[/dim]")
        while True:
            line = input()
            if not line.strip():
                break
            curl_lines.append(line)

        curl_command = "\n".join(curl_lines)

        # 추가 정보
        console.print("\n[yellow]2단계: 추가 정보 (선택사항)[/yellow]")

        has_additional = Confirm.ask("전체 데이터 개수나 페이지네이션 정보를 알고 계신가요?", default=False)
        additional_info = ""

        if has_additional:
            total_items = Prompt.ask("전체 데이터 개수", default="모름")
            pagination_info = Prompt.ask("페이지네이션 방식 설명", default="모름")
            additional_info = f"전체 개수: {total_items}\n페이지네이션: {pagination_info}"

        # LLM 분석
        console.print("\n[green]🔍 AI가 분석 중입니다...[/green]")
        spec = self.analyze_curl(curl_command, additional_info)

        console.print("\n[bold green]✅ 분석 완료![/bold green]")
        console.print(f"기본 URL: {spec.base_url}")
        console.print(f"API 엔드포인트: {spec.list_endpoint.url}")

        return spec

    def enhance_spec_with_sample(self, spec: CrawlerSpec, sample_response: str) -> CrawlerSpec:
        """
        실제 API 응답 샘플을 보고 data_path와 id_field를 더 정확하게 추출

        Args:
            spec: 기존 크롤러 사양
            sample_response: 실제 API 응답 JSON

        Returns:
            CrawlerSpec: 개선된 크롤러 사양
        """
        prompt = f"""
다음은 API의 실제 응답입니다. 데이터 배열이 어디 있는지, ID 필드가 무엇인지 찾아주세요.

<response>
{sample_response[:2000]}  # 처음 2000자만
</response>

JSON 형식으로 답해주세요:
{{
  "data_path": "응답에서 데이터 배열 경로 (예: data.items)",
  "id_field": "각 항목의 ID 필드명",
  "sample_item": "첫 번째 항목 샘플 (dict)"
}}
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.content[0].text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            enhanced = json.loads(json_match.group())
            spec.data_path = enhanced.get("data_path", spec.data_path)
            spec.id_field = enhanced.get("id_field", spec.id_field)

        return spec
