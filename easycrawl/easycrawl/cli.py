"""
EasyCrawl CLI - 할머니도 쓸 수 있는 크롤러 생성 도구

사용법:
    easycrawl              # 대화형 모드로 시작
    easycrawl --help       # 도움말 보기
"""

import os
import sys
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from .llm_analyzer import LLMAnalyzer
from .crawler_generator import CrawlerGenerator
from .executor import CrawlerExecutor


console = Console()


def print_welcome():
    """환영 메시지"""
    welcome = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║           🎉 EasyCrawl 에 오신 것을 환영합니다!          ║
    ║                                                       ║
    ║       AI가 자동으로 웹 크롤러를 만들어드립니다            ║
    ║         코딩을 몰라도 괜찮아요! 따라만 하세요 😊          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(welcome, style="bold cyan")


def print_step(step_num: int, total_steps: int, title: str, description: str = ""):
    """단계 제목 출력"""
    console.print(f"\n[bold yellow]━━━ 단계 {step_num}/{total_steps}: {title} ━━━[/bold yellow]")
    if description:
        console.print(f"[dim]{description}[/dim]\n")


def guide_browser_devtools():
    """브라우저 개발자도구 사용법 안내"""
    guide = """
    📖 **브라우저 개발자도구 사용법**

    1️⃣  크롬 브라우저에서 크롤링할 웹사이트를 엽니다
    2️⃣  F12 키를 누르거나 우클릭 > 검사 를 선택합니다
    3️⃣  위쪽 탭에서 **Network** (네트워크) 탭을 클릭합니다
    4️⃣  빨간 녹화 버튼이 켜져 있는지 확인합니다
    5️⃣  웹사이트에서 데이터를 불러오는 동작을 합니다
        (예: 검색하기, 다음 페이지 클릭 등)
    6️⃣  Network 탭에 여러 요청이 나타납니다
    7️⃣  **데이터를 가져오는 요청**을 찾습니다
        (Fetch/XHR 탭을 보거나, json이 포함된 요청을 찾으세요)
    8️⃣  해당 요청을 우클릭 > Copy > **Copy as cURL** 선택
    9️⃣  복사 완료! 이제 붙여넣기만 하면 됩니다 ✨
    """
    console.print(Panel(Markdown(guide), border_style="blue", box=box.ROUNDED))


def get_multiline_input(prompt_text: str, guide_func=None) -> str:
    """여러 줄 입력 받기"""
    console.print(f"\n[cyan]{prompt_text}[/cyan]")

    if guide_func:
        show_guide = Confirm.ask("📖 사용법을 먼저 보시겠어요?", default=True)
        if show_guide:
            guide_func()

    console.print("\n[dim]💡 팁: 여러 줄을 붙여넣은 후 빈 줄에서 Enter를 두 번 누르면 완료됩니다[/dim]\n")
    console.print("[green]➤[/green] ", end="")

    lines = []
    empty_line_count = 0

    while True:
        try:
            line = input()
            if not line.strip():
                empty_line_count += 1
                if empty_line_count >= 2:  # 빈 줄 2번 연속이면 종료
                    break
            else:
                empty_line_count = 0
                lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)


def interactive_mode():
    """대화형 모드"""
    print_welcome()

    console.print("\n[bold]시작하기 전에 준비물을 확인해주세요:[/bold]")
    console.print("  ✅ 크롬 브라우저")
    console.print("  ✅ 크롤링할 웹사이트 주소")
    console.print("  ✅ Claude API 키 (https://console.anthropic.com/에서 발급)")

    if not Confirm.ask("\n준비가 되셨나요?", default=True):
        console.print("\n[yellow]준비가 되면 다시 'easycrawl' 명령어를 실행해주세요![/yellow]")
        return

    # ====== 1단계: API 키 입력 ======
    print_step(1, 6, "Claude API 키 입력", "AI가 분석하려면 API 키가 필요해요")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        console.print(f"[green]✅ 환경변수에서 API 키를 찾았습니다[/green]")
        use_env_key = Confirm.ask("이 키를 사용하시겠어요?", default=True)
        if not use_env_key:
            api_key = Prompt.ask("API 키를 입력하세요", password=True)
    else:
        console.print("[yellow]환경변수에 ANTHROPIC_API_KEY가 없습니다[/yellow]")
        console.print("[dim]API 키는 https://console.anthropic.com/ 에서 발급받을 수 있습니다[/dim]")
        api_key = Prompt.ask("API 키를 입력하세요", password=True)

    # ====== 2단계: 프로젝트 이름 ======
    print_step(2, 6, "프로젝트 이름 정하기", "크롤러의 이름을 정해주세요")

    project_name = Prompt.ask(
        "프로젝트 이름 (영문, 숫자, _ 만 사용)",
        default="my_crawler"
    )
    project_name = project_name.replace(" ", "_").replace("-", "_")

    # ====== 3단계: curl 명령어 입력 ======
    print_step(3, 6, "API 정보 붙여넣기", "브라우저에서 복사한 curl 명령어를 붙여넣으세요")

    curl_command = get_multiline_input(
        "📋 curl 명령어를 붙여넣으세요:",
        guide_func=guide_browser_devtools
    )

    if not curl_command.strip():
        console.print("[red]❌ curl 명령어가 비어있습니다. 다시 시도해주세요.[/red]")
        return

    # ====== 4단계: 추가 정보 입력 ======
    print_step(4, 6, "추가 정보 (선택)", "더 정확한 크롤러를 만들기 위한 정보")

    additional_info = ""

    has_total = Confirm.ask("전체 데이터 개수를 알고 계신가요?", default=False)
    if has_total:
        total_items = IntPrompt.ask("전체 데이터 개수")
        additional_info += f"전체 데이터: {total_items}개\n"

    has_pagination = Confirm.ask("페이지네이션 방식을 아시나요? (예: 10개씩, 오프셋 방식 등)", default=False)
    if has_pagination:
        pagination_info = Prompt.ask("페이지네이션 설명")
        additional_info += f"페이지네이션: {pagination_info}\n"

    # ====== 5단계: 출력 설정 ======
    print_step(5, 6, "출력 설정", "데이터를 어떤 형식으로 저장할지 선택하세요")

    output_format = Prompt.ask(
        "출력 형식",
        choices=["jsonl", "json", "csv"],
        default="jsonl"
    )

    speed_options = {
        "느림 (안전)": 1.0,
        "보통 (권장)": 0.5,
        "빠름 (주의)": 0.2,
    }
    speed_choice = Prompt.ask(
        "크롤링 속도",
        choices=list(speed_options.keys()),
        default="보통 (권장)"
    )
    request_delay = speed_options[speed_choice]

    # ====== 6단계: AI 분석 및 크롤러 생성 ======
    print_step(6, 6, "AI가 크롤러를 만들고 있어요", "잠시만 기다려주세요...")

    try:
        # LLM 분석
        console.print("[yellow]🤖 AI가 API를 분석하고 있습니다...[/yellow]")
        analyzer = LLMAnalyzer(api_key=api_key)
        spec = analyzer.analyze_curl(curl_command, additional_info)

        console.print("[green]✅ 분석 완료![/green]")
        console.print(f"  - 기본 URL: {spec.base_url}")
        console.print(f"  - API 엔드포인트: {spec.list_endpoint.url}")

        # 크롤러 생성
        console.print("\n[yellow]🛠️  크롤러 코드를 생성하고 있습니다...[/yellow]")
        generator = CrawlerGenerator(spec)
        code = generator.generate_code(
            output_format=output_format,
            request_delay=request_delay,
            project_name=project_name
        )

        # 파일 저장
        output_dir = project_name
        filename = f"{project_name}.py"
        filepath = generator.save_to_file(code, output_dir, filename)

        console.print(f"[green]✅ 크롤러 생성 완료![/green]")
        console.print(f"  📁 위치: {filepath}")

        # ====== 완료 및 다음 단계 안내 ======
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "[bold green]🎉 축하합니다! 크롤러가 준비되었습니다![/bold green]\n\n"
            "[bold]다음 단계:[/bold]\n"
            f"1️⃣  생성된 파일을 열어주세요: [cyan]{filepath}[/cyan]\n"
            f"2️⃣  COOKIES 변수에 브라우저 쿠키를 붙여넣으세요\n"
            f"3️⃣  터미널에서 실행하세요: [cyan]python {filepath}[/cyan]\n\n"
            "[dim]💡 쿠키는 브라우저 개발자도구 > Application > Cookies 에서 복사할 수 있습니다[/dim]",
            border_style="green",
            box=box.DOUBLE
        ))

        # 바로 실행 옵션
        run_now = Confirm.ask("\n지금 바로 크롤러를 실행해볼까요?", default=False)
        if run_now:
            console.print("\n[yellow]⚠️  실행 전에 파일에서 COOKIES를 먼저 설정해주세요![/yellow]")
            ready = Confirm.ask("COOKIES 설정을 완료하셨나요?", default=False)

            if ready:
                executor = CrawlerExecutor(filepath)
                if executor.validate_before_run():
                    executor.show_preview()
                    if Confirm.ask("\n이 설정으로 실행하시겠어요?", default=True):
                        executor.run()
            else:
                console.print("[cyan]나중에 다음 명령어로 실행하세요:[/cyan]")
                console.print(f"  python {filepath}")

    except Exception as e:
        console.print(f"\n[red]❌ 오류가 발생했습니다: {e}[/red]")
        console.print("[yellow]다시 시도해주세요. 문제가 계속되면 GitHub Issues에 문의해주세요.[/yellow]")
        return

    console.print("\n[bold cyan]EasyCrawl을 사용해주셔서 감사합니다! 🙏[/bold cyan]")


@click.command()
@click.option('--api-key', envvar='ANTHROPIC_API_KEY', help='Claude API 키')
@click.option('--curl-file', type=click.Path(exists=True), help='curl 명령어가 저장된 파일')
@click.option('--project-name', default='my_crawler', help='프로젝트 이름')
@click.option('--output-format', type=click.Choice(['json', 'jsonl', 'csv']), default='jsonl', help='출력 형식')
@click.option('--speed', type=click.Choice(['slow', 'normal', 'fast']), default='normal', help='크롤링 속도')
@click.option('--non-interactive', is_flag=True, help='비대화형 모드 (자동화용)')
def main(api_key, curl_file, project_name, output_format, speed, non_interactive):
    """
    EasyCrawl - AI 기반 웹 크롤러 자동 생성 도구

    코딩 없이 누구나 쉽게 웹 크롤러를 만들 수 있습니다!
    """
    if non_interactive:
        # 비대화형 모드 (CLI 옵션만 사용)
        if not api_key:
            console.print("[red]❌ --api-key 옵션이 필요합니다[/red]")
            sys.exit(1)
        if not curl_file:
            console.print("[red]❌ --curl-file 옵션이 필요합니다[/red]")
            sys.exit(1)

        # curl 파일 읽기
        with open(curl_file, 'r', encoding='utf-8') as f:
            curl_command = f.read()

        # 속도 설정
        speed_map = {'slow': 1.0, 'normal': 0.5, 'fast': 0.2}
        request_delay = speed_map[speed]

        # 분석 및 생성
        try:
            analyzer = LLMAnalyzer(api_key=api_key)
            spec = analyzer.analyze_curl(curl_command)
            generator = CrawlerGenerator(spec)
            code = generator.generate_code(
                output_format=output_format,
                request_delay=request_delay,
                project_name=project_name
            )
            filepath = generator.save_to_file(code, project_name, f"{project_name}.py")
            console.print(f"[green]✅ 크롤러 생성 완료: {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]❌ 오류: {e}[/red]")
            sys.exit(1)
    else:
        # 대화형 모드
        interactive_mode()


if __name__ == "__main__":
    main()
