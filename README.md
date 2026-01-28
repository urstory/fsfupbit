# fsfupbit

> Enhanced Python wrapper for Upbit API - A maintained fork of pyupbit

[![PyPI version](https://badge.fury.io/py/fsfupbit)](https://badge.fury.io/pyfupbit)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

업비트(Upbit) 거래소의 API를 쉽게 사용할 수 있는 Python 라이브러리입니다.

---

## ⚠️ About This Fork (이 포크에 대하여)

**fsfupbit**은 [pyupbit](https://github.com/sharebook-kr/pyupbit)를 기반으로 **풀스택패밀리 연구소 (Full Stack Research Lab)**가 유지보수하는 포크 버전입니다.

### 포크 사유 (Why We Forked)

- 원본 pyupbit 저장소가 **2년 이상 업데이트되지 않음** (2021년 마지막 릴리스)
- 중요한 기능과 버그 수정을 포함한 여러 **Pull Request가 미해결 상태**
- 최신 Upbit API 기능이 반영되지 않음
- 활발한 유지보수와 커뮤니티 지원 필요

이러한 문제를 해결하고 최신 Upbit API 기능을 포함하는 활발하게 유지보드되는 버전을 제공하기 위해 풀스택패밀리 연구소에서 이 포크를 생성했습니다.

---

## 🚀 특징

- **최신 API 반영**: 2024-2025년 업데이트된 최신 Upbit API 지원
- **타입 힌트**: 완전한 타입 힌트로 IDE 자동완성 지원
- **개선된 에러 처리**: 구체적인 예외 클래스로 디버깅 용이
- **철저한 테스트**: 단위 테스트와 테스트 커버리지 제공
- **문서화**: 상세한 Docstring과 예제 코드
- **활발한 유지보수**: 버그 수정과 신규 기능 지원

---

## 📦 설치

```bash
pip install fsfupbit
```

### 의존성

- Python 3.8+
- pyjwt >= 2.0
- pandas >= 1.0
- requests >= 2.25
- websockets >= 10.0

---

## 🔧 빠른 시작

```python
import fsfupbit

# 현재가 조회
price = fsfupbit.get_current_price("KRW-BTC")
print(f"비트코인 현재가: {price:,}원")

# 캔들 조회
df = fsfupbit.get_ohlcv("KRW-BTC", interval="day", count=30)
print(df.tail())

# 거래소 로그인
upbit = fsfupbit.Upbit(access_key, secret_key)
balance = upbit.get_balance("KRW")
print(f"보유 원화: {balance:,}원")
```

---

## 🔒 보안 (Security)

### API 키 관리

**⚠️ 중요**: API 키를 절대 코드에 직접 작성하거나 버전 관리 시스템에 커밋하지 마세요.

#### 환경 변수 사용 (권장)

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일에 API 키 입력
UPBIT_ACCESS_KEY=your_access_key_here
UPBIT_SECRET_KEY=your_secret_key_here
```

```python
import os
from fsfupbit import Upbit

access = os.getenv("UPBIT_ACCESS_KEY")
secret = os.getenv("UPBIT_SECRET_KEY")

upbit = Upbit(access, secret)
```

#### 보안 best practices

1. **API 키 보관**: `.env` 파일은 `.gitignore`에 포함되어 git에 커밋되지 않습니다
2. **키 rotation**: 주기적으로 API 키를 변경하세요
3. **IP 허용**: Upbit 개발자 페이지에서 접속 가능한 IP를 제한하세요
4. **권한 최소화**: 필요한 권한만 부여하세요 (거래/조회 등)

---

## 📚 문서

- [API 문서](docs/api.md)
- **[pyupbit PR 처리 현황](docs/pyupbit_prs.md)** ⭐
- **[보안 검사 보고서](docs/security_audit.md)** 🔒
- [개발 가이드](docs/development.md)
- [업데이트 로그](docs/changelog.md)
- [배포 가이드](docs/deployment.md)

---

## 🆔 pyupbit와의 차이점

### 새로 추가된 기능

| 기능 | pyupbit | fsfupbit |
|------|---------|----------|
| 호가 모아보기 단위 조회 | ❌ | ✅ `get_orderbook_supported_levels()` |
| 호가 레벨 파라미터 | ❌ | ✅ `get_orderbook(level=...)` |
| 입금 가능 정보 조회 | ❌ | ✅ `get_deposit_chance()` |
| 입금 주소 생성 | ❌ | ✅ `create_deposit_address()` |
| 입금 주소 조회 | ❌ | ✅ `get_deposit_address()`, `get_deposit_addresses()` |
| 원화 입금 계좌 조회 | ❌ | ✅ `get_krw_deposit_info()` |
| 출금 가능 정보 조회 | ❌ | ✅ `get_withdraw_chance()` |
| 출금 허용 주소 목록 | ❌ | ✅ `get_withdraw_addresses()` |
| 주문 생성 테스트 | ❌ | ✅ `test_order()` |
| 주문 일괄 취소 | ❌ | ✅ `cancel_orders_open()` |
| 취소 후 재주문 | ❌ | ✅ `cancel_and_new_order()` |
| time_in_force 파라미터 | ❌ | ✅ |
| 초/연 캔들 지원 | ❌ | ✅ `seconds/*`, `years` |
| 가격 단위 변환 | ❌ | ✅ `converting_price_unit` |
| 개인용 WebSocket | ❌ | ✅ `PrivateWebSocketManager` |
| 트래블룰 검증 | ❌ | ✅ `get_travel_rule_vasps()`, `verify_travel_rule_by_uuid()` |
| 커스텀 예외 클래스 | ❌ | ✅ `UpbitAPIError`, `UpbitValidationError`, `UpbitOrderError` |

### 코드 품질 개선

- ✅ 전체 함수에 타입 힌트 추가
- ✅ PEP 257 기반 Docstring 작성
- ✅ 커스텀 예외 클래스 도입
- ✅ 단위 테스트 추가 (87개 테스트, 56% 커버리지)
- ✅ 일관된 반환 타입

### 버그 수정

- ✅ 입금 API URL 오타 수정 (`api.upbit.com//v1` → `api.upbit.com/v1`)
- ✅ `withdraw_coin()`에 `net_type` 필수 파라미터 추가 (자산 손실 방지)

---

## 📄 라이선스

```
Apache License, Version 2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

**Original Copyright (c) 2021 sharebook-kr (pyupbit)**
**Modifications Copyright (c) 2025 Full Stack Research Lab (풀스택연구소)**

---

## 🙇 Acknowledgments (감사의 말)

이 프로젝트는 [pyupbit](https://github.com/sharebook-kr/pyupbit)를 기반으로 하여 개선되었습니다.

- **Original Authors**: Jonghun Yoo, Brayden Jo
- **Original Repository**: https://github.com/sharebook-kr/pyupbit
- **License**: Apache License 2.0

---

## 📞 Contact (연락처)

**Full Stack Research Lab (풀스택패밀리 연구소)**

- Website: https://www.fullstackfamily.com/
- GitHub: https://github.com/fullstack-research-lab/fsfupbit
- Repository: https://github.com/fullstack-research-lab/fsfupbit

---

## 🔗 Links

- [Upbit Open API Documentation](https://docs.upbit.com)
- [pyupbit Original Repository](https://github.com/sharebook-kr/pyupbit)
