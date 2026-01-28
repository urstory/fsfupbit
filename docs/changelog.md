# fsfupbit Changelog

> All notable changes from pyupbit to fsfupbit

**Version**: 1.0.0
**Release Date**: 2026-01-29

---

## [Unreleased]

---

## [1.0.0] - 2026-01-29

### Added

#### 호가 모아보기 기능
- `get_orderbook_supported_levels()`: 종목별 지원 호가 모아보기 단위 조회
- `get_orderbook()` `level` 파라미터: 호가 모아보기 단위 지정

#### 입금 주소 관리
- `Upbit.get_deposit_chance()`: 입금 가능 정보 조회
- `Upbit.create_deposit_address()`: 입금 주소 생성 요청
- `Upbit.get_deposit_address()`: 개별 입금 주소 조회
- `Upbit.get_deposit_addresses()`: 전체 입금 주소 목록 조회
- `Upbit.get_krw_deposit_info()`: 원화 입금 계좌 정보 조회

#### 출금 관련 기능
- `Upbit.get_withdraw_chance()`: 출금 가능 정보 조회
- `Upbit.get_withdraw_addresses()`: 출금 허용 주소 목록 조회

#### 주문 고급 기능
- `Upbit.test_order()`: 주문 생성 테스트 (실제 체결 없음)
- `Upbit.cancel_orders_open()`: 주문 일괄 취소
- `Upbit.cancel_and_new_order()`: 취소 후 재주문
- `Upbit.buy_limit_order()`, `Upbit.sell_limit_order()` `time_in_force` 파라미터 추가

#### 캔들 기능 확장
- 초 캔들 지원: `seconds/1`, `seconds/3`, `seconds/5`, `seconds/10`, `seconds/15`, `seconds/30`, `seconds/60`, `seconds/240`
- 연 캔들 지원: `years`, `year`
- `get_ohlcv()` `converting_price_unit` 파라미터: 일봉 원화 환산 지원

#### WebSocket 개인 데이터 지원
- `PrivateWebSocketManager`: 개인용 WebSocket 관리자
  - JWT 토큰 인증
  - `MyOrder`: 내 주문 정보 실시간 수신
  - `MyAsset`: 내 자산 정보 실시간 수신

#### 트래블룰 기능
- `Upbit.get_travel_rule_vasps()`: 트래블룰 지원 거래소 목록 조회
- `Upbit.verify_travel_rule_by_uuid()`: 입금 UUID로 트래블룰 검증

#### 커스텀 예외 클래스
- `UpbitAPIError`: API 호출 에러 (상태 코드, 응답 데이터 포함)
- `UpbitValidationError`: 입력값 검증 에러
- `UpbitOrderError`: 주문 관련 에러

### Changed

#### 전체 함수에 타입 힌트 추가
- 모든 공개 함수에 완전한 타입 힌트 적용
- `Optional`, `Union`, `List`, `Dict`, `Any` 타입 적극적으로 사용

#### 전체 함수에 Docstring 작성
- PEP 257 기반 상세 Docstring 작성
- Args, Returns, Examples, Raises, Note 섹션 포함
- 실제 사용 예제 코드 포함

#### 예외 처리 개선
- 구체적인 예외 클래스로 디버깅 용이성 확보
- 에러 시 `None` 반환 대신 예외 발생하도록 변경
- 상태 코드, 응답 데이터 포함

#### API 호출 개선
- `_call_public_api()`의 반환 타입을 튜플로 명시화
- 쿼리 파라미터를 `**kwargs`로 전달하도록 개선

### Breaking Changes

#### withdraw_coin() 함수 시그니처 변경

**변경 전:**
```python
withdraw_coin(self, currency, amount, address, secondary_address='None',
              transaction_type='default', contain_req=False)
```

**변경 후:**
```python
withdraw_coin(self, currency: str, amount: Union[float, str],
              address: str, net_type: str,  # 새로운 필수 파라미터
              secondary_address: Optional[str] = None,
              transaction_type: str = "default",
              contain_req: bool = False)
```

**마이그레이션 가이드:**
```python
# 기존 코드
upbit.withdraw_coin("BTC", 0.1, "address...")

# 변경 후 코드 (net_type 추가 필요)
upbit.withdraw_coin("BTC", 0.1, "address...", net_type="BTC")
```

**⚠️ 중요:** `net_type`은 필수 파라미터입니다. 출금하려는 코인이 지원하는 네트워크 타입을 확인해야 합니다.

---

## [0.2.33] - pyupbit 원본 버전

- pyupbit의 기본 기능 포함

---

## Migration Guide from pyupbit

### 1. 임포트 변경

```python
# 기존
import pyupbit

# 변경 (fsfupbit는 패키지 동일하므로 기존 코드와 호환)
import pyupbit  # 또는 import fsfupbit
```

### 2. withdraw_coin() 호출 수정

```python
# 기존
upbit.withdraw_coin("BTC", 0.1, "address...")

# 변경 (net_type 필수 파라미터 추가)
upbit.withdraw_coin("BTC", 0.1, "address...", net_type="BTC")
```

### 3. 새로운 기능 활용

```python
# 호가 모아보기
from fsfupbit import get_orderbook_supported_levels, get_orderbook

levels = get_orderbook_supported_levels(["KRW-BTC"])
ob = get_orderbook("KRW-BTC", level=10000)

# 입금 주소 관리
upbit = fsfupbit.Upbit(access, secret)
addr = upbit.get_deposit_address("BTC")

# 개인용 WebSocket
from fsfupbit import PrivateWebSocketManager

pwm = PrivateWebSocketManager(access, secret, "MyOrder")
data = pwm.get()
```

---

## Removed Features

없음 (pyupbit의 모든 기능이 유지됨)

---

## Known Issues

1. **test_get_tickers_with_market_warning** 실패
   - 원인: API 응답에 `market_warning` 필드가 항상 포함되지 않음
   - 영향: 없음 (단위 테스트의 문제)

---

## Deprecations

없음

---

## Contributors

- fsfupbit Development Team

---

## References

- [Upbit Open API Documentation](https://docs.upbit.com)
- [pyupbit Original Repository](https://github.com/sharebook-kr/pyupbit)