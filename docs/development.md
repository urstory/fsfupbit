# fsfupbit Developer Guide

> 개발자를 위한 가이드 문서

**Version**: 1.0.0
**Updated**: 2026-01-29

---

## 목차

1. [개발 환경 설정](#개발-환경-설정)
2. [코드 스타일 가이드](#코드-스타일-가이드)
3. [테스트 가이드](#테스트-가이드)
4. [Pull Request 가이드](#pull-request-가이드)
5. [릴리스 절차](#릴리스-절차)

---

## 개발 환경 설정

### 필수 조건

- Python 3.8 이상
- pip 또는 poetry (의존성 관리)

### 의존성 설치

```bash
# pip 사용
pip install -r requirements.txt

# 또는 poetry 사용
poetry install
```

### 개발 환경 구성

```bash
# 저장소 클론
git clone https://github.com/your-org/fsfupbit.git
cd fsfupbit

# 가상환 환경 설정
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 개발용 의존성 설치
pip install pytest pytest-cov pytest-mock pytest-asyncio black flake8 mypy
```

---

## 코드 스타일 가이드

### PEP 8 준수

fsfupbit는 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 스타일 가이드를 따릅니다.

### 코드 포맷팅

```bash
# 모든 Python 파일 포맷팅
black pyupbit/

# 확인만 실행 (실제 포맷팅하지 않음)
black --check pyupbit/
```

### Linting

```bash
# flake8로 코드 스타일 검사
flake8 pyupbit/

# mypy로 타입 검사
mypy pyupbit/
```

### 명명 규칙

**함수/변수:**
```python
def get_current_price(ticker: str) -> float:
    pass
```

**클래스:**
```python
class UpbitAPIError(Exception):
    pass
```

**상수:**
```python
MAX_CALL_COUNT = 200
API_BASE_URL = "https://api.upbit.com/v1"
```

### 타입 힌트

모든 함수는 타입 힌트를 포함해야 합니다:

```python
from typing import List, Dict, Optional, Union

def get_tickers(
    fiat: str = "",
    is_details: bool = False
) -> List[str]:
    ...
```

### Docstring

모든 공개 함수는 PEP 257 기반 Docstring을 작성해야 합니다:

```python
def get_orderbook_supported_levels(markets: List[str]) -> List[Dict]:
    """
    종목별 지원 호가 모아보기 단위 조회

    Upbit API의 호가 모아보기 기능에서 지원하는 단위를 조회합니다.

    Args:
        markets: 마켓 코드 리스트 (예: ["KRW-BTC", "KRW-ETH"])

    Returns:
        종목별 지원 단위 정보
        [
            {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "KRW-ETH", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "BTC-ETH", "supported_levels": [0]}
        ]

    Raises:
        ValueError: markets 파라미터가 비어있거나 유효하지 않은 경우

    Examples:
        >>> levels = get_orderbook_supported_levels(["KRW-BTC"])
        >>> print(levels[0]["supported_levels"])
        [0, 1, 2, 3, 4, 5]

    Note:
        - KRW 마켓은 다양한 레벨을 지원합니다
        - 다른 마켓은 기본 레벨(0)만 지원합니다
    """
```

---

## 테스트 가이드

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_quotation_api.py

# 특정 테스트만 실행
pytest tests/test_quotation_api.py::test_get_tickers_defaults

# 상세 출력
pytest -v

# 커버리지 리포트 생성
pytest --cov=pyupbit --cov-report=html

# 커버리지 기준 설정 (최소 80%)
pytest --cov=pyupbit --cov-fail-under=80
```

### 테스트 작성 규칙

1. **테스트 파일 구조**
   ```
   tests/
   ├── unit/              # 단위 테스트 (Mock 사용)
   │   ├── test_quotation_api.py
   │   ├── test_exchange_api.py
   │   ├── test_websocket_api.py
   │   └── test_request_api.py
   ├── integration/       # 통합 테스트 (실제 API 호출)
   └── fixtures/          # 테스트 픽스처
   ```

2. **테스트 네이밍**
   ```python
   class TestGetTickers:
       """get_tickers 함수 테스트"""

       def test_defaults(self):
           """기본 동작 테스트"""
           tickers = get_tickers()
           assert isinstance(tickers, list)
           assert "KRW-BTC" in tickers
   ```

3. **Mock 사용**
   ```python
   from unittest.mock import patch

   @patch('pyupbit.quotation_api._call_public_api')
   def test_with_mock(self, mock_api):
       mock_api.return_value = ([], {})
       result = get_tickers()
       assert result == []
   ```

### 테스트 커버리지 목표

- 전체 커버리지: **80% 이상**
- 핵심 모듈 커버리지: **90% 이상**
  - `quotation_api.py`
  - `exchange_api.py`
  - `request_api.py`

---

## Pull Request 가이드

### PR 전 체크리스트

- [ ] 테스트 통과 (전체 테스트, 커버리지 80%+)
- [ ] 코드 스타일 검사 통과 (black, flake8)
- [ ] 타입 힌트 포함
- [ ] Docstring 작성됨
- [ ] BREAKING CHANGES가 있는 경우 문서화
- [ ] 커밋 메시지 규칙 준수

### PR 제목 규칙

```
<type>: <scope>: <subject>

type: feat (기능), fix (버그 수정), docs (문서), refactor (리팩토링), test (테스트)
scope: quotation, exchange, websocket, general
subject: 50자 이내로 작성
```

**예시:**
```
feat(quotation): add seconds candle support
fix(exchange): correct withdraw_coin net_type parameter
docs(readme): update installation guide
test(exchange): add get_deposit_address unit tests
```

### PR 본문 템플릿

```markdown
## 변경 사항

- [x] 기능 추가
- [ ] 버그 수정
- [ ] 문서 업데이트
- [ ] 테스트 추가/수정

## 테스트

- [x] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 테스트 커버리지 확인

## 체크리스트

- [ ] 타입 힌트 추가됨
- [ ] Docstring 작성됨
- [ ] PEP 8 준수
- [ ] 예외 처리됨
- [ ] 문서 업데이트됨
```

---

## 릴리스 절차

### 버전 정책

**Semantic Versioning 준수**: `MAJOR.MINOR.PATCH`

- **MAJOR**: 호환되지 않는 변경
- **MINOR**: 후향 호환되는 기능 추가
- **PATCH**: 버그 수정

### 브랜치 전략

```
main (개발 브랜치)
  ├── develop (개발 중)
  ├── release/x.x.x (릴리스 준비)
  └── feature/xxx (기능별 브랜치)
  └── fix/xxx (버그 수정 브랜치)
```

### 릴리스 절차

1. **개발**
   - feature 브랜치에서 작업
   - 커밋 메시지 규칙 준수
   - 단위 테스트 작성

2. **PR 생성**
   - pull request 템플릿 사용
   - 코드 리뷰 요청

3. **리뷰 및 병합**
   - 유지지자가 코드 리뷰
   - 변경 사항 discuss
   - 승인 후 병합

4. **릴리스**
   - develop 브랜치로 병합
   - 버전 태그 생성 (v1.0.0)
   - PyPI에 배포

### PyPI 배포

```bash
# 1. 빌드 배포 패키지 생성
python -m build

# 2. PyPI에 업로드
twine upload dist/*

# 3. GitHub 릴리스
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

---

## 기여하기

### 버그 보고

1. Issues 탭에서 버그 보고
2. 버그 재현 방법 설명
3. 환경 정보 포함

### 기능 제안

1. 먼저 이슈로 논의
2. 제안서 작성
3. Pull Request로 구현

### 코드 리뷰

Pull Request에 대한 코드 리뷰는 환영합니다!

---

## 추가 리소스

- [API 문서](api.md)
- [업데이트 로그](changelog.md)
- [Upbit Open API](https://docs.upbit.com)
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [PEP 257](https://www.python.org/dev/peps/pep-0257/)