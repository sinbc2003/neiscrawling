# EasyCrawl 빠른 시작 가이드

## 5분 만에 첫 크롤러 만들기

### 준비물
- ✅ Python 3.8 이상
- ✅ Claude API 키
- ✅ 크롤링할 웹사이트

---

## 단계별 가이드

### 1️⃣ 설치

```bash
pip install easycrawl
```

### 2️⃣ API 키 설정

환경변수로 설정하면 편리합니다:

```bash
# Linux/Mac
export ANTHROPIC_API_KEY="your-api-key-here"

# Windows CMD
set ANTHROPIC_API_KEY=your-api-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

### 3️⃣ 브라우저에서 curl 복사

1. 크롬에서 F12 (개발자도구)
2. Network 탭
3. 원하는 데이터 불러오기 (검색, 목록 보기 등)
4. API 호출 찾기 (Fetch/XHR 탭)
5. 우클릭 > Copy > Copy as cURL

### 4️⃣ EasyCrawl 실행

```bash
easycrawl
```

화면에 나오는 질문에 답하세요:

```
1. API 키 입력 (환경변수 설정했으면 자동)
2. 프로젝트 이름: my_first_crawler
3. curl 명령어 붙여넣기
4. 추가 정보 (선택)
5. 출력 형식: jsonl
6. 속도: 보통 (권장)
```

### 5️⃣ 생성된 크롤러 실행

```bash
cd my_first_crawler
python my_first_crawler.py
```

**중요**: 실행 전에 파일을 열어서 `COOKIES` 변수를 업데이트하세요!

---

## 실전 팁

### 쿠키 복사하는 법

1. 개발자도구 > Application 탭
2. 왼쪽 Storage > Cookies > 해당 도메인
3. 필요한 쿠키 복사
4. 생성된 크롤러의 `COOKIES` dict에 추가

예시:
```python
COOKIES = {
    "JSESSIONID": "abc123...",
    "session_id": "xyz789...",
}
```

### 크롤링이 막혔을 때

1. **속도 늦추기**: `REQUEST_DELAY`를 늘려보세요
2. **User-Agent 확인**: 브라우저와 동일한지 확인
3. **쿠키 갱신**: 세션 만료시 새 쿠키로 교체
4. **로그 확인**: `crawler.log` 파일 열어보기

### 대용량 데이터

- **체크포인트**: 자동으로 진행 상황 저장됨
- **중단 후 재개**: 그냥 다시 실행하면 됨
- **JSONL 추천**: 메모리 효율적

---

## 예제 시나리오

### 시나리오 1: 게시판 크롤링

```
목표: 커뮤니티 게시판 글 수집
방법:
1. 게시판 목록 페이지 접속
2. F12 > Network
3. "다음 페이지" 클릭
4. 목록 API 호출 찾기 (보통 list, board, posts 등)
5. Copy as cURL
6. easycrawl 실행
```

### 시나리오 2: 검색 결과 수집

```
목표: 검색 결과 데이터 수집
방법:
1. 검색어 입력 후 검색
2. F12 > Network > XHR
3. search 또는 query API 찾기
4. Copy as cURL
5. easycrawl에서 "전체 개수" 입력하면 더 정확함
```

### 시나리오 3: 로그인이 필요한 사이트

```
목표: 로그인 후 데이터 수집
방법:
1. 브라우저에서 먼저 로그인
2. 로그인 상태에서 curl 복사
3. easycrawl로 크롤러 생성
4. 생성된 파일에서 COOKIES를 브라우저의 쿠키로 업데이트
5. 실행
```

---

## 문제 해결

### ❌ "No module named 'easycrawl'"

```bash
pip install easycrawl
# 또는
python -m pip install easycrawl
```

### ❌ "Invalid API key"

- API 키 확인: https://console.anthropic.com/
- 환경변수 설정 확인: `echo $ANTHROPIC_API_KEY`
- 공백이나 따옴표 없이 입력

### ❌ "Connection error"

- 인터넷 연결 확인
- 방화벽/VPN 확인
- 프록시 설정 필요시 환경변수 설정

### ❌ 크롤러가 빈 데이터 반환

- curl 명령어가 정확한지 확인
- 쿠키가 필요한 API인지 확인
- Network 탭에서 실제 응답 데이터 확인

---

## 다음 단계

더 자세한 내용은 [메인 README](../README.md)를 참고하세요!

**Happy Crawling! 🚀**
