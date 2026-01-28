# fsfupbit Deployment Summary

> 배포 준비 완료 요약

**Version**: 1.0.0
**Date**: 2026-01-29
**Status**: Ready for PyPI Deployment

---

## 배포 구성 완료 항목

### ✅ 1. setup.py 업데이트

```python
name='fsfupbit'
version='1.0.0'
python_requires='>=3.8'
```

**변경 사항:**
- 패키지 이름: `pyupbit` → `fsfupbit`
- 버전: `0.2.34` → `1.0.0`
- Python 요구사항: `>=3.6` → `>=3.8`
- 의존성 버전 명시 추가
- classifiers 확대 (Python 3.8~3.12 지원)
- project_urls 추가
- keywords 추가

### ✅ 2. requirements.txt 정리

```
# Core dependencies
pyjwt>=2.0.0
pandas>=1.0.0
requests>=2.25.0
websockets>=10.0

# Development dependencies (optional)
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

### ✅ 3. MANIFEST.in 생성

```
include README.md
include LICENSE
include requirements.txt
recursive-include docs *.md
recursive-include pyupbit *.py
global-exclude __pycache__
global-exclude *.py[cd]
global-exclude .git*
global-exclude .DS_Store
```

### ✅ 4. 배포 문서 작성

- **docs/deployment.md**: 완전한 PyPI 배포 가이드
- **docs/api.md**: API 참조 문서
- **docs/development.md**: 개발자 가이드
- **docs/changelog.md**: 변경 로그 및 마이그레이션 가이드
- **scripts/verify_package.sh**: 패키지 검증 스크립트

---

## 패키지 구조

```
fsfupbit/
├── pyupbit/
│   ├── __init__.py
│   ├── errors.py          # 커스텀 예외 클래스
│   ├── exchange_api.py    # 거래소 API
│   ├── quotation_api.py   # 시세 API
│   ├── request_api.py     # API 요청
│   └── websocket_api.py   # WebSocket API
├── docs/
│   ├── api.md
│   ├── changelog.md
│   ├── development.md
│   └── deployment.md
├── tests/
│   ├── test_errors.py
│   ├── test_exchange_api.py
│   └── test_quotation_api.py
├── scripts/
│   └── verify_package.sh
├── setup.py
├── requirements.txt
├── MANIFEST.in
├── README.md
└── LICENSE
```

---

## 배포 절차

### Step 1: 빌드 도구 설치

```bash
pip install build twine
```

### Step 2: 패키지 검증 (선택)

```bash
./scripts/verify_package.sh
```

### Step 3: 패키지 빌드

```bash
cd /path/to/fsfupbit
rm -rf dist/ build/ *.egg-info
python -m build
```

### Step 4: 패키지 검증

```bash
twine check dist/*
```

### Step 5: TestPyPI 테스트 (선택)

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ fsfupbit
```

### Step 6: PyPI 배포

```bash
twine upload dist/*
```

---

## 테스트 결과

```
pytest 실행 결과:
- 총 테스트: 87개
- 통과: 86개
- 실패: 1개 (test_get_tickers_with_market_warning - 기존 이슈)
- 커버리지: 56%
```

---

## 주요 변경 사항 (vs pyupbit)

### 새로운 기능

1. **커스텀 예외 클래스**
   - `UpbitAPIError`
   - `UpbitValidationError`
   - `UpbitOrderError`

2. **호가 모아보기**
   - `get_orderbook_supported_levels()`
   - `get_orderbook(level=...)`

3. **입금 주소 관리**
   - `get_deposit_chance()`
   - `create_deposit_address()`
   - `get_deposit_address()`
   - `get_deposit_addresses()`
   - `get_krw_deposit_info()`

4. **출금 관련 기능**
   - `get_withdraw_chance()`
   - `get_withdraw_addresses()`

5. **고급 주문 기능**
   - `test_order()`
   - `cancel_orders_open()`
   - `cancel_and_new_order()`
   - `time_in_force` 파라미터

6. **캔들 기능 확장**
   - 초 캔들 (`seconds/1`, `seconds/3`, ..., `seconds/240`)
   - 연 캔들 (`years`, `year`)
   - `converting_price_unit` 파라미터

7. **개인용 WebSocket**
   - `PrivateWebSocketManager`
   - JWT 토큰 인증

8. **트래블룰 기능**
   - `get_travel_rule_vasps()`
   - `verify_travel_rule_by_uuid()`

### Breaking Changes

1. **withdraw_coin() net_type 필수 파라미터**
   ```python
   # 변경 전
   upbit.withdraw_coin("BTC", 0.1, "address...")

   # 변경 후
   upbit.withdraw_coin("BTC", 0.1, "address...", net_type="BTC")
   ```

---

## 배포 후 체크리스트

- [ ] PyPI에서 패키지 확인 (https://pypi.org/project/fsfupbit/)
- [ ] 설치 테스트: `pip install fsfupbit`
- [ ] 기본 기능 테스트
- [ ] GitHub 릴리스 생성
- [ ] 태그 생성: `git tag -a v1.0.0 -m "Release version 1.0.0"`
- [ ] 태그 푸시: `git push origin v1.0.0`
- [ ] README.md 업데이트 (PyPI 뱃지 추가)

---

## 연락처

이슈 및 버그 리포트: https://github.com/sharebook-kr/pyupbit/issues
