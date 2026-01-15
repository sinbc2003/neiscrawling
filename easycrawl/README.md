# 🎉 EasyCrawl - AI가 만들어주는 웹 크롤러

**코딩을 몰라도 괜찮아요!** AI가 자동으로 웹 크롤러를 만들어드립니다. 😊

할머니, 할아버지도 따라할 수 있을 정도로 쉬운 웹 크롤링 도구입니다.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 📖 이게 뭔가요?

**EasyCrawl**은 웹사이트에서 데이터를 수집하는 "크롤러"를 자동으로 만들어주는 도구입니다.

### 이런 분들께 추천합니다:
- 🎓 연구를 위해 웹 데이터가 필요한 학생/교수님
- 💼 업무 자동화가 필요한 직장인
- 📊 데이터 분석을 하고 싶은데 코딩은 어려운 분
- 🤔 크롤링은 필요한데 Selenium은 너무 복잡한 개발자

### 기존 방식 vs EasyCrawl

| 항목 | 기존 방식 | EasyCrawl |
|------|----------|-----------|
| 코딩 필요? | ✅ Python 숙련도 필요 | ❌ 코딩 몰라도 OK |
| 소요 시간 | 2-3시간 | 5분 |
| 브라우저 자동화 | Selenium (느리고 불안정) | API 직접 호출 (빠르고 안정적) |
| 난이도 | ⭐⭐⭐⭐⭐ | ⭐ |

---

## 🚀 빠른 시작 (5분이면 끝!)

### 1단계: 설치하기

터미널(명령 프롬프트)을 열고 다음 명령어를 입력하세요:

```bash
pip install easycrawl
```

> 💡 **Python이 없으신가요?**
> [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드하세요.
> 설치할 때 "Add Python to PATH" 체크박스를 꼭 선택하세요!

### 2단계: Claude API 키 받기

1. [Claude Console](https://console.anthropic.com/)에 접속
2. 회원가입 또는 로그인
3. Settings > API Keys에서 새 API 키 생성
4. 복사해두기 (나중에 사용)

> 💳 **비용이 궁금하신가요?**
> Claude API는 무료 크레딧을 제공합니다. 크롤러 1개 생성에 약 $0.01 정도 소요됩니다.

### 3단계: EasyCrawl 실행하기

터미널에서 다음 명령어를 입력하세요:

```bash
easycrawl
```

그럼 친절한 AI 가이드가 시작됩니다! 화면에 나오는 질문에 차근차근 답하기만 하면 됩니다. 🎯

---

## 📚 자세한 사용법

### 전체 과정 미리보기

```
1. easycrawl 명령어 실행
   ↓
2. API 키 입력
   ↓
3. 프로젝트 이름 정하기
   ↓
4. 브라우저에서 curl 명령어 복사
   ↓
5. 붙여넣기
   ↓
6. 설정 선택 (속도, 형식 등)
   ↓
7. AI가 자동으로 크롤러 생성! ✨
   ↓
8. 생성된 파일 실행
   ↓
9. 데이터 수집 완료! 🎉
```

### 4단계가 어려우신가요? 걱정 마세요!

**브라우저에서 curl 명령어 복사하는 법 (초보자용)**

1. **크롬 브라우저 열기**
   - 크롤링하고 싶은 웹사이트에 접속합니다

2. **개발자도구 열기**
   - 키보드에서 `F12` 키를 누르거나
   - 웹페이지에서 우클릭 > "검사" 선택

3. **Network 탭 클릭**
   - 개발자도구 상단에 있는 "Network" (네트워크) 탭을 클릭합니다
   - 빨간 녹화 버튼(●)이 켜져 있는지 확인하세요

4. **데이터 불러오기 동작하기**
   - 웹사이트에서 데이터를 불러오는 동작을 해봅니다
   - 예: 검색하기, 다음 페이지 클릭, 목록 보기 등

5. **API 호출 찾기**
   - Network 탭에 여러 요청이 나타납니다
   - "Fetch/XHR" 버튼을 클릭하면 API 호출만 볼 수 있습니다
   - 이름이나 Preview를 보고 데이터가 들어있는 요청을 찾습니다

6. **curl 명령어 복사**
   - 해당 요청을 우클릭 > "Copy" > "Copy as cURL"
   - 클립보드에 복사되었습니다! 🎉

7. **EasyCrawl에 붙여넣기**
   - easycrawl 화면으로 돌아와서 붙여넣기 (Ctrl+V 또는 Cmd+V)
   - Enter 두 번 누르면 완료!

---

## 🎯 실전 예제

### 예제 1: 나이스 지원포털 QA 크롤링

```bash
$ easycrawl

# 1단계: API 키 입력
API 키를 입력하세요: sk-ant-xxxxx

# 2단계: 프로젝트 이름
프로젝트 이름: neis_qa_crawler

# 3단계: curl 명령어 붙여넣기
📋 curl 명령어를 붙여넣으세요:
curl 'https://help.neis.go.kr/nip_usp_pg01_002.do' \
  -H 'Content-Type: application/json' \
  --data-raw '{"data":{"search":{"startCount":"0"}}}'

# 4단계: 추가 정보 (선택)
전체 데이터 개수를 알고 계신가요? Yes
전체 데이터 개수: 123700

# 5단계: 출력 설정
출력 형식: jsonl
크롤링 속도: 보통 (권장)

# 6단계: AI가 크롤러 생성!
🤖 AI가 API를 분석하고 있습니다...
✅ 분석 완료!
🛠️  크롤러 코드를 생성하고 있습니다...
✅ 크롤러 생성 완료!
  📁 위치: neis_qa_crawler/neis_qa_crawler.py
```

### 예제 2: 자동화 (비대화형 모드)

CI/CD나 자동화 스크립트에서 사용할 때:

```bash
# curl 명령어를 파일로 저장
echo "curl 'https://api.example.com/data' -H 'Authorization: Bearer xxx'" > curl.txt

# 비대화형 모드로 실행
easycrawl \
  --api-key sk-ant-xxxxx \
  --curl-file curl.txt \
  --project-name my_crawler \
  --output-format jsonl \
  --speed normal \
  --non-interactive
```

---

## ⚙️ 설정 옵션

### 출력 형식

| 형식 | 설명 | 언제 사용? |
|------|------|----------|
| **JSONL** | 한 줄에 하나의 JSON 객체 | 대용량 데이터, 스트리밍 처리 (권장) |
| **JSON** | 하나의 JSON 배열 | 소규모 데이터, 가독성 중요할 때 |
| **CSV** | 엑셀에서 열 수 있는 표 형식 | 엑셀 분석, 비개발자에게 공유 |

### 크롤링 속도

| 속도 | 딜레이 | 설명 |
|------|--------|------|
| **느림** | 1.0초 | 가장 안전, 서버 부담 최소 |
| **보통** (권장) | 0.5초 | 속도와 안정성의 균형 |
| **빠름** | 0.2초 | 빠르지만 차단 위험 있음 |

> ⚠️ **주의**: 너무 빠른 속도는 서버에 부담을 주고 IP 차단당할 수 있습니다.

---

## 🎓 고급 사용법

### 생성된 크롤러 커스터마이징

EasyCrawl이 생성한 크롤러는 일반 Python 파일이므로 자유롭게 수정할 수 있습니다:

```python
# 생성된 크롤러 파일 열기
# my_crawler/my_crawler.py

# 1. 쿠키 업데이트 (로그인 필요시)
COOKIES = {
    "JSESSIONID": "여기에_브라우저에서_복사한_쿠키",
    "session_id": "xxx",
}

# 2. 수집 속도 조정
REQUEST_DELAY = 0.3  # 초 단위

# 3. 페이지 크기 변경
PAGE_SIZE = 20

# 4. 데이터 후처리 추가
def format_qa_data(self, item):
    # 여기에 원하는 데이터 변환 로직 추가
    item['timestamp'] = datetime.now().isoformat()
    return item
```

### 체크포인트 기능

크롤링 중 중단되어도 걱정 없어요! 자동으로 진행 상황이 저장됩니다:

```python
# 크롤링 중단되면 자동으로 저장됨
# crawler_checkpoint.json

# 다시 실행하면 중단된 지점부터 재개
python my_crawler.py
```

### 환경변수 설정 (편의 기능)

매번 API 키 입력하기 귀찮다면:

```bash
# Linux/Mac
export ANTHROPIC_API_KEY="sk-ant-xxxxx"

# Windows (CMD)
set ANTHROPIC_API_KEY=sk-ant-xxxxx

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

그러면 easycrawl이 자동으로 환경변수에서 API 키를 읽습니다!

---

## 🔧 문제 해결

### Q1: "pip install easycrawl" 이 안 돼요

```bash
# Python 버전 확인 (3.8 이상이어야 함)
python --version

# pip 업그레이드
python -m pip install --upgrade pip

# 다시 시도
pip install easycrawl
```

### Q2: API 키를 입력했는데 오류가 나요

- API 키가 정확한지 확인하세요 (복사할 때 공백이 들어가지 않았는지)
- [Claude Console](https://console.anthropic.com/)에서 API 키 상태를 확인하세요
- 크레딧이 남아있는지 확인하세요

### Q3: curl 명령어가 너무 길어요

- 그대로 붙여넣으면 됩니다! 몇 천 줄이어도 괜찮습니다
- 붙여넣은 후 빈 줄에서 Enter를 **두 번** 누르세요

### Q4: 생성된 크롤러가 실행이 안 돼요

```bash
# 1. 필수 라이브러리 설치 확인
pip install requests

# 2. 파일에서 COOKIES 설정 확인
# my_crawler.py 파일을 열어서 COOKIES 변수 업데이트

# 3. 로그 파일 확인
cat crawler.log  # Linux/Mac
type crawler.log  # Windows
```

### Q5: 세션이 만료되었대요

일부 웹사이트는 로그인 세션이 짧습니다:

1. 브라우저에서 다시 로그인
2. 개발자도구에서 새 쿠키 복사
3. 생성된 크롤러 파일의 COOKIES 변수 업데이트
4. 다시 실행

---

## 🤝 기여하기

이 프로젝트를 더 좋게 만드는데 함께해주세요!

1. Fork 하기
2. 기능 브랜치 만들기 (`git checkout -b feature/amazing-feature`)
3. 커밋하기 (`git commit -m 'Add amazing feature'`)
4. Push 하기 (`git push origin feature/amazing-feature`)
5. Pull Request 열기

### 개발 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yourusername/easycrawl.git
cd easycrawl

# 개발 모드로 설치
pip install -e .

# 테스트 실행
pytest tests/
```

---

## 📜 라이선스

MIT License - 자유롭게 사용하세요!

---

## 🙏 감사의 말

- [Anthropic](https://www.anthropic.com/) - Claude API 제공
- [Rich](https://github.com/Textualize/rich) - 아름다운 터미널 UI
- [Click](https://click.palletsprojects.com/) - CLI 프레임워크
- 그리고 이 프로젝트를 사용해주시는 모든 분들께 감사드립니다! 💖

---

## 📞 문의 및 지원

- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/yourusername/easycrawl/issues)
- 💬 **질문하기**: [GitHub Discussions](https://github.com/yourusername/easycrawl/discussions)
- 📧 **이메일**: easycrawl@example.com

---

## ⭐ 도움이 되셨나요?

GitHub에서 ⭐ 스타를 눌러주세요! 큰 힘이 됩니다 😊

**Happy Crawling! 🚀**
