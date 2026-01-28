# fsfupbit Documentation

> Enhanced Python wrapper for Upbit API - A maintained fork of pyupbit

**Version**: 1.0.0
**Updated**: 2026-01-29

---

## ⚠️ About This Fork

**fsfupbit**은 [pyupbit](https://github.com/sharebook-kr/pyupbit)를 기반으로 **풀스택패밀리 연구소**가 유지보수하는 포크 버전입니다.

### 포크 사유 (Why We Forked)

- 원본 pyupbit 저장소가 **2년 이상 업데이트되지 않음** (2024년 마지막 릴리스)
- 중요한 기능과 버그 수정을 포함한 여러 **Pull Request가 미해결 상태**
- 최신 Upbit API 기능이 반영되지 않음
- 활발한 유지보수와 커뮤니티 지원 필요

이러한 문제를 해결하고 최신 Upbit API 기능을 포함하는 활발하게 유지보드되는 버전을 제공하기 위해 풀스택패밀리 연구소에서 이 포크를 생성했습니다.

---

## 📚 Documentation

### User Documentation

| 문서 | 설명 |
|------|------|
| [API Reference](api.md) | 전체 API 함수 참조 |
| [pyupbit PRs](pyupbit_prs.md) | pyupbit 미해결 PR 처리 현황 |
| [Changelog](changelog.md) | 버전별 변경 사항 및 마이그레이션 가이드 |
| [Examples](#examples) | 사용 예제 코드 |

### Developer Documentation

| 문서 | 설명 |
|------|------|
| [Development Guide](development.md) | 개발 환경 설정, 코드 스타일, PR 프로세스 |
| [Deployment Guide](deployment.md) | PyPI 배포 절차 |
| [Deployment Summary](deployment_summary.md) | 배포 준비 상태 요약 |

---

## 🚀 Quick Start

### Installation

```bash
pip install fsfupbit
```

### Basic Usage

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

## 🆔 What's New in fsfupbit

### New Features (Not in pyupbit)

| Category | Features |
|----------|----------|
| **호가 모아보기** | `get_orderbook_supported_levels()`, `get_orderbook(level=...)` |
| **입금 주소 관리** | `get_deposit_chance()`, `create_deposit_address()`, `get_deposit_address()`, `get_deposit_addresses()`, `get_krw_deposit_info()` |
| **출금 기능** | `get_withdraw_chance()`, `get_withdraw_addresses()` |
| **고급 주문** | `test_order()`, `cancel_orders_open()`, `cancel_and_new_order()`, `time_in_force` |
| **캔들 확장** | 초 캔들 (`seconds/*`), 연 캔들 (`years`), `converting_price_unit` |
| **개인용 WebSocket** | `PrivateWebSocketManager` (JWT 인증) |
| **트래블룰** | `get_travel_rule_vasps()`, `verify_travel_rule_by_uuid()` |
| **예외 처리** | `UpbitAPIError`, `UpbitValidationError`, `UpbitOrderError` |

### Code Quality Improvements

- ✅ 전체 함수에 타입 힌트 추가
- ✅ PEP 257 기반 Docstring 작성
- ✅ 단위 테스트 87개 (56% 커버리지)
- ✅ 일관된 반환 타입

### Bug Fixes

- ✅ 입금 API URL 오타 수정 (`api.upbit.com//v1` → `api.upbit.com/v1`)
- ✅ `withdraw_coin()`에 `net_type` 필수 파라미터 추가 (자산 손실 방지)

---

## 📖 Examples

### 1. 시세 조회

```python
import fsfupbit

# 티커 조회
tickers = fsfupbit.get_tickers(fiat="KRW")
print(tickers)  # ['KRW-BTC', 'KRW-ETH', ...]

# 현재가 조회
price = fsfupbit.get_current_price("KRW-BTC")
print(price)  # 95000000.0

# 캔들 조회 (일봉)
df = fsfupbit.get_ohlcv("KRW-BTC", interval="day", count=30)
print(df)

# 호가 조회 (모아보기)
orderbook = fsfupbit.get_orderbook("KRW-BTC", level=10000)
print(orderbook)
```

### 2. 입금 주소 관리

```python
import fsfupbit

upbit = fsfupbit.Upbit(access_key, secret_key)

# 입금 가능 정보 조회
chance = upbit.get_deposit_chance("BTC")
print(chance)

# 입금 주소 생성
address = upbit.create_deposit_address("BTC")
print(address)

# 입금 주소 조회
addr = upbit.get_deposit_address("BTC")
print(addr)

# 전체 입금 주소 조회
addrs = upbit.get_deposit_addresses()
print(addrs)
```

### 3. 주문 및 취소

```python
import fsfupbit

upbit = fsfupbit.Upbit(access_key, secret_key)

# 주문 생성 테스트
result = upbit.test_order(
    market="KRW-BTC",
    side="bid",
    volume=0.001,
    price=50000000
)
print(result)

# 지정가 매수
order = upbit.buy_limit_order(
    "KRW-BTC",
    0.001,
    50000000,
    time_in_force="FOK"  # 새로운 파라미터
)
print(order)

# 미체결 주문 일괄 취소
canceled = upbit.cancel_orders_open("KRW-BTC")
print(canceled)
```

### 4. 개인용 WebSocket

```python
import fsfupbit

# 개인용 WebSocket 관리자
pwm = fsfupbit.PrivateWebSocketManager(
    access_key,
    secret_key,
    "MyOrder"  # 또는 "MyAsset"
)

# 데이터 수신
data = pwm.get()
print(data)
```

---

## 🔄 Migration from pyupbit

### Import Change

```python
# 기존
import pyupbit

# 변경
import fsfupbit

# 또는 (패키지 내부 구조는 동일)
from fsfupbit import get_ohlcv, Upbit
```

### Breaking Changes

```python
# withdraw_coin() net_type 필수 파라미터 추가
# 기존
upbit.withdraw_coin("BTC", 0.1, "address...")

# 변경
upbit.withdraw_coin("BTC", 0.1, "address...", net_type="BTC")
```

---

## 📄 License

```
Apache License, Version 2.0

**Original Copyright (c) 2021 sharebook-kr (pyupbit)**
**Modifications Copyright (c) 2025 풀스택패밀리 연구소**
```

---

## 📞 Contact

**풀스택패밀리 연구소**

- Website: https://www.fullstackfamily.com/
- GitHub: https://github.com/urstory/fsfupbit

---

## 🔗 Related Links

- [Upbit Open API Documentation](https://docs.upbit.com)
- [pyupbit Original Repository](https://github.com/sharebook-kr/pyupbit)
- [Upbit API Review Notes](https://github.com/fullstack-research-lab/enjoyTrading/tree/main/docs/upbit_apis_reviews)
