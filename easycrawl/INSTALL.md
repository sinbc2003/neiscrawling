# EasyCrawl 설치 가이드

## 🎯 설치 방법

### 방법 1: PyPI에서 설치 (권장)

```bash
pip install easycrawl
```

### 방법 2: 소스에서 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/easycrawl.git
cd easycrawl

# 설치
pip install -e .
```

### 방법 3: 특정 버전 설치

```bash
# 최신 안정 버전
pip install easycrawl==0.1.0

# 최신 개발 버전
pip install git+https://github.com/yourusername/easycrawl.git
```

---

## 🔧 시스템 요구사항

### 필수 요구사항

- **Python**: 3.8 이상
- **운영체제**: Windows, macOS, Linux 모두 지원
- **인터넷 연결**: API 호출을 위해 필요

### Python 설치 확인

```bash
python --version
# 또는
python3 --version
```

Python이 없다면:
- Windows: [Python 공식 사이트](https://www.python.org/downloads/)에서 다운로드
- macOS: `brew install python3`
- Linux: `sudo apt-get install python3` (Ubuntu/Debian)

---

## 📦 의존성 패키지

EasyCrawl은 다음 패키지들을 사용합니다:

```
requests>=2.31.0      # HTTP 요청
anthropic>=0.39.0     # Claude AI
rich>=13.7.0          # 터미널 UI
pydantic>=2.0.0       # 데이터 검증
click>=8.1.0          # CLI 프레임워크
```

이들은 자동으로 설치됩니다!

---

## 🌍 가상환경 사용 (권장)

시스템 Python을 깨끗하게 유지하려면 가상환경을 사용하세요:

### venv 사용 (Python 내장)

```bash
# 가상환경 생성
python -m venv easycrawl-env

# 활성화
# Windows
easycrawl-env\Scripts\activate

# Linux/Mac
source easycrawl-env/bin/activate

# 설치
pip install easycrawl

# 사용 후 비활성화
deactivate
```

### conda 사용

```bash
# 환경 생성
conda create -n easycrawl python=3.10

# 활성화
conda activate easycrawl

# 설치
pip install easycrawl

# 비활성화
conda deactivate
```

---

## 🔑 API 키 설정

### 옵션 1: 환경변수 (권장)

```bash
# Linux/Mac (현재 세션)
export ANTHROPIC_API_KEY="your-api-key-here"

# Linux/Mac (영구적)
echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Windows CMD (현재 세션)
set ANTHROPIC_API_KEY=your-api-key-here

# Windows CMD (영구적)
setx ANTHROPIC_API_KEY "your-api-key-here"

# Windows PowerShell (현재 세션)
$env:ANTHROPIC_API_KEY="your-api-key-here"

# Windows PowerShell (영구적)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'your-api-key-here', 'User')
```

### 옵션 2: .env 파일

```bash
# 프로젝트 디렉토리에 .env 파일 생성
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env

# easycrawl이 자동으로 읽습니다
```

### 옵션 3: 실행시 입력

환경변수가 없으면 실행할 때 입력하라고 물어봅니다.

---

## ✅ 설치 확인

### 1. 버전 확인

```bash
easycrawl --version
# 또는
python -c "import easycrawl; print(easycrawl.__version__)"
```

### 2. 도움말 확인

```bash
easycrawl --help
```

### 3. 테스트 실행

```bash
easycrawl
```

환영 메시지가 나오면 성공! 🎉

---

## 🐛 문제 해결

### "easycrawl: command not found"

**원인**: pip 설치 경로가 PATH에 없음

**해결**:
```bash
# pip 설치 경로 확인
python -m pip show easycrawl

# 직접 실행
python -m easycrawl.cli

# 또는 PATH 추가 (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# Windows는 시스템 환경변수 편집에서 추가
```

### "No module named 'easycrawl'"

**원인**: Python 버전 혼재 또는 가상환경 미활성화

**해결**:
```bash
# 어떤 pip를 사용하는지 확인
which pip  # Linux/Mac
where pip  # Windows

# 명시적으로 설치
python -m pip install easycrawl

# 또는 python3 사용
python3 -m pip install easycrawl
```

### "SSL Certificate Error"

**원인**: 회사 방화벽, 오래된 인증서

**해결**:
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 인증서 확인 비활성화 (임시)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org easycrawl
```

### "Permission Denied"

**원인**: 시스템 디렉토리에 쓰기 권한 없음

**해결**:
```bash
# 사용자 디렉토리에 설치
pip install --user easycrawl

# 또는 가상환경 사용 (권장)
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
pip install easycrawl
```

---

## 🔄 업데이트

### 최신 버전으로 업데이트

```bash
pip install --upgrade easycrawl
```

### 특정 버전으로 다운그레이드

```bash
pip install easycrawl==0.1.0
```

---

## 🗑️ 제거

```bash
pip uninstall easycrawl
```

---

## 💡 다음 단계

설치가 완료되었나요? 이제 [빠른 시작 가이드](examples/QUICKSTART.md)를 따라해보세요!

```bash
easycrawl
```

**Happy Crawling! 🚀**
