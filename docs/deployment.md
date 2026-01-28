# fsfupbit Deployment Guide

> PyPI 배포 가이드

**Version**: 1.0.0
**Updated**: 2026-01-29

---

## 목차

1. [배포 준비](#배포-준비)
2. [PyPI 배포 절차](#pypi-배포-절차)
3. [검증 단계](#검증-단계)
4. [문제 해결](#문제-해결)

---

## 배포 준비

### 필수 조건

- Python 3.8 이상
- PyPI 계정 (https://pypi.org/account/register/)
- API Token 생성 (PyPI 계정 설정에서 생성)

### 배포용 패키지 설치

```bash
pip install build twine
```

### 배포 전 체크리스트

- [ ] 모든 테스트 통과 (`pytest`)
- [ ] 코드 커버리지 80% 이상 (`pytest --cov=pyupbit`)
- [ ] setup.py 버전 확인 (1.0.0)
- [ ] CHANGELOG.md 업데이트
- [ ] README.md 업데이트
- [ ] API 문서 작성 완료

---

## PyPI 배포 절차

### 1. 패키지 빌드

```bash
# 프로젝트 루트 디렉토리에서
cd /path/to/fsfupbit

# 빌드 디렉토리 정소 (기존 빌드가 있는 경우)
rm -rf dist/ build/ *.egg-info

# 패키지 빌드
python -m build
```

**빌드 결과물:**
```
dist/
├── fsfupbit-1.0.0.tar.gz       # 소스 배포판
└── fsfupbit-1.0.0-py3-none-any.whl  # 휠 배포판
```

### 2. 패키지 검증

```bash
# twine으로 패키지 검증
twine check dist/*
```

**예상 출력:**
```
Checking dist/fsfupbit-1.0.0.tar.gz: PASSED
Checking dist/fsfupbit-1.0.0-py3-none-any.whl: PASSED
```

### 3. TestPyPI에 테스트 배포 (선택)

```bash
# TestPyPI에 업로드
twine upload --repository testpypi dist/*

# TestPyPI에서 설치 테스트
pip install --index-url https://test.pypi.org/simple/ fsfupbit
```

### 4. PyPI에 공식 배포

```bash
# PyPI에 업로드
twine upload dist/*
```

**인증:**
- 첫 업로드 시 사용자명과 암호 입력 (또는 API Token)
- API Token 사용 시: `__token__` as username, token value as password

### 5. 배포 확인

```bash
# PyPI 웹사이트에서 확인
# https://pypi.org/project/fsfupbit/

# 설치 테스트
pip install fsfupbit
```

---

## 검증 단계

### 설치 테스트

```bash
# 가상환경 생성
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# test_env\Scripts\activate  # Windows

# 패키지 설치
pip install fsfupbit

# 기본 기능 테스트
python -c "
import fsfupbit
print('fsfupbit version:', fsfupbit.__version__)
tickers = fsfupbit.get_tickers()
print('Tickers loaded:', len(tickers))
"
```

### 기능 테스트

```python
import fsfupbit

# 1. 기존 기능 호환성 테스트
tickers = fsfupbit.get_tickers()
assert "KRW-BTC" in tickers

price = fsfupbit.get_current_price("KRW-BTC")
assert isinstance(price, float)

# 2. 새로운 기능 테스트
# 호가 모아보기
levels = fsfupbit.get_orderbook_supported_levels(["KRW-BTC"])
assert len(levels) > 0

# 개인용 WebSocket (인증 필요)
# pwm = fsfupbit.PrivateWebSocketManager(access, secret, "MyOrder")
```

---

## 문제 해결

### 일반적인 문제

**문제 1: HTTP 400 오류 - 패키지 이름 이미 존재**
```bash
# 해결: setup.py에서 name을 고유한 이름으로 변경
name='fsfupbit-yourusername'
```

**문제 2: README 렌더링 오류**
```bash
# 해결: long_description_content_type 설정 확인
long_description_content_type="text/markdown"
```

**문제 3: 파일이 포함되지 않음**
```bash
# 해결: MANIFEST.in 파일 확인 및 수정
include README.md
recursive-include docs *.md
```

**문제 4: 버전 충돌**
```bash
# 해결: 기존 버전 삭제 불가능, 새 버전으로 배포
version='1.0.1'  # 버전 번호 증가
```

### 롤백 절차

**실수로 배포한 경우:**
1. PyPI 웹사이트에서 패키지 삭제 (48시간 이내 가능)
2. 또는 새 버전(yank 후 재배포)으로 수정 배포

```bash
# Yank 처리 (PyPI 웹사이트에서)
# Settings → Release → Yank this version

# 수정 후 새 버전 배포
# setup.py에서 version='1.0.1'로 변경 후 재배포
```

---

## 자동화 배포 (GitHub Actions)

### .github/workflows/publish.yml

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

### GitHub Secrets 설정

1. GitHub Repository → Settings → Secrets and variables → Actions
2. New repository secret 추가:
   - Name: `PYPI_API_TOKEN`
   - Value: PyPI API Token (pypi-...)

---

## 추가 리소스

- [PyPI Packaging Tutorial](https://packaging.python.org/tutorials/packaging-projects/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [setuptools Documentation](https://setuptools.pypa.io/)
