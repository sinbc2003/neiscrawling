# EasyCrawl 아키텍처 설명

## 🏗️ 프로젝트 구조

```
easycrawl/
├── easycrawl/              # 메인 패키지
│   ├── __init__.py         # 패키지 초기화
│   ├── cli.py              # CLI 인터페이스 (사용자 상호작용)
│   ├── llm_analyzer.py     # LLM 기반 API 분석기
│   ├── crawler_generator.py # 크롤러 코드 생성기
│   └── executor.py         # 크롤러 실행 엔진
├── examples/               # 예제 및 가이드
│   ├── QUICKSTART.md       # 빠른 시작 가이드
│   └── example_curl.txt    # 예제 curl 명령어
├── setup.py                # 패키지 설정
├── requirements.txt        # 의존성 목록
├── README.md               # 메인 문서
├── INSTALL.md              # 설치 가이드
├── LICENSE                 # MIT 라이선스
├── .gitignore              # Git 제외 파일
└── MANIFEST.in             # 패키지 포함 파일 설정
```

---

## 🔄 작동 원리

### 1. 사용자 입력 (cli.py)

```
사용자
  ↓
easycrawl 명령어 실행
  ↓
대화형 인터페이스
  - API 키 입력
  - 프로젝트 이름
  - curl 명령어 붙여넣기
  - 설정 (속도, 형식)
```

### 2. AI 분석 (llm_analyzer.py)

```
curl 명령어
  ↓
Claude API (LLM)
  ↓
분석 결과 (CrawlerSpec)
  - base_url
  - API 엔드포인트
  - 헤더/쿠키
  - 페이지네이션 방식
  - 데이터 경로
```

### 3. 크롤러 생성 (crawler_generator.py)

```
CrawlerSpec
  ↓
Python 코드 생성
  - requests 기반
  - 에러 핸들링
  - 체크포인트 기능
  - 설정 가능한 파라미터
  ↓
{project_name}.py 파일 저장
```

### 4. 실행 (executor.py - 선택사항)

```
생성된 크롤러
  ↓
검증 (문법, 라이브러리)
  ↓
실행
  ↓
실시간 모니터링
  ↓
데이터 수집 완료
```

---

## 🧩 주요 컴포넌트

### LLMAnalyzer (llm_analyzer.py)

**역할**: curl 명령어를 분석하여 크롤러 사양 추출

**핵심 메서드**:
- `analyze_curl()`: curl 명령어를 LLM으로 분석
- `analyze_interactive()`: 대화형으로 정보 수집
- `enhance_spec_with_sample()`: 실제 응답으로 사양 개선

**데이터 모델**:
- `CrawlerSpec`: 크롤러 사양 (URL, 헤더, 페이지네이션 등)
- `APIEndpoint`: API 엔드포인트 정보

### CrawlerGenerator (crawler_generator.py)

**역할**: 크롤러 사양을 Python 코드로 변환

**핵심 메서드**:
- `generate_code()`: 전체 크롤러 코드 생성
- `save_to_file()`: 파일로 저장

**생성하는 기능**:
- API 호출 로직
- 페이지네이션 처리
- 에러 핸들링
- 체크포인트 저장/복원
- 다양한 출력 형식 (JSON, JSONL, CSV)

### CrawlerExecutor (executor.py)

**역할**: 생성된 크롤러 실행 및 모니터링

**핵심 메서드**:
- `run()`: 크롤러 실행
- `validate_before_run()`: 실행 전 검증
- `show_preview()`: 설정 미리보기

### CLI (cli.py)

**역할**: 사용자 인터페이스

**주요 기능**:
- 단계별 가이드 제공
- 브라우저 사용법 안내
- Rich 라이브러리로 아름다운 UI
- 대화형/비대화형 모드 지원

---

## 🎨 설계 철학

### 1. 사용자 중심

- **할머니도 쓸 수 있게**: 기술 용어 최소화
- **단계별 가이드**: 각 단계마다 명확한 설명
- **시각적 피드백**: Rich 라이브러리로 예쁜 UI

### 2. 안정성

- **에러 핸들링**: 모든 단계에서 예외 처리
- **체크포인트**: 중단 후 재개 가능
- **검증**: 실행 전 코드 문법 검사

### 3. 확장성

- **모듈화**: 각 기능이 독립적인 모듈
- **커스터마이징 가능**: 생성된 코드를 자유롭게 수정 가능
- **다양한 출력 형식**: JSON, JSONL, CSV 지원

### 4. AI 활용

- **자동 분석**: curl 명령어를 LLM이 이해
- **지능적 추론**: 페이지네이션 패턴 자동 감지
- **유연한 대응**: 다양한 API 구조 지원

---

## 🔐 보안 고려사항

### API 키 관리

- 환경변수 사용 권장
- 파일에 하드코딩 금지
- `.gitignore`에 secrets 파일 포함

### 쿠키 보안

- 생성된 크롤러에 쿠키 노출
- 사용자가 직접 관리 필요
- 공개 저장소에 커밋 주의

### Rate Limiting

- 기본적으로 적절한 딜레이 설정
- 서버 부담 최소화
- 사용자가 속도 조절 가능

---

## 🚀 향후 계획

### v0.2.0 목표

- [ ] GUI 버전 추가 (tkinter/PyQt)
- [ ] 더 많은 페이지네이션 패턴 지원
- [ ] 크롤링 스케줄러 기능
- [ ] 데이터 검증 및 정제 기능

### v0.3.0 목표

- [ ] 분산 크롤링 지원
- [ ] 프록시/VPN 자동 설정
- [ ] 웹훅 알림 기능
- [ ] 대시보드 UI

### 장기 비전

- AI가 웹사이트 구조를 자동으로 분석
- 로그인 자동화
- CAPTCHA 처리
- 웹 크롤링 표준 프레임워크로 성장

---

## 🤝 기여 가이드

### 개발 환경 설정

```bash
git clone https://github.com/yourusername/easycrawl.git
cd easycrawl
pip install -e .
```

### 코드 스타일

- PEP 8 준수
- Type hints 사용
- Docstring 작성 (Google 스타일)

### 테스트

```bash
pytest tests/
```

### Pull Request

1. Feature 브랜치 생성
2. 코드 작성 및 테스트
3. 문서 업데이트
4. PR 생성

---

## 📚 참고 자료

- [Claude API 문서](https://docs.anthropic.com/)
- [Rich 라이브러리](https://github.com/Textualize/rich)
- [requests 문서](https://requests.readthedocs.io/)
- [Click 문서](https://click.palletsprojects.com/)

---

**설계 및 구현**: EasyCrawl Team
**버전**: 0.1.0
**업데이트**: 2026-01-15
