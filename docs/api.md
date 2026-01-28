# fsfupbit API Documentation

> Enhanced Python wrapper for Upbit API - Complete API Reference

**Version**: 1.0.0
**Updated**: 2026-01-29

Based on [Upbit Open API Documentation](https://docs.upbit.com) with the latest updates through 2026.

---

## Table of Contents

- [시세 조회 API](#시세-조회-api)
- [거래/자산 관리 API](#거래자산-관리-api)
- [입출금 API](#입출금-api)
- [WebSocket API](#websocket-api)
- [예외 처리](#예외-처리)

---

## 시세 조회 API

### get_tickers

업비트 전체 또는 특정 마켓의 티커 목록을 조회합니다.

**API Endpoint**: `GET /v1/market/all`

```python
get_tickers(
    fiat: str = "",
    is_details: bool = False,
    limit_info: bool = False,
    verbose: bool = False
) -> Union[List[str], List[Dict], Tuple]
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `fiat` | str | `""` | 필터링할 법정화폐 (KRW, BTC, USDT) |
| `is_details` | bool | `False` | 마켓 정보 포함 여부 |
| `limit_info` | bool | `False` | Rate Limit 정보 반환 |
| `verbose` | bool | `False` | 원본 API 응답 전체 반환 |

**Returns:**

- `verbose=False, is_details=False`: `List[str]` - 티커 리스트
- `verbose=False, is_details=True`: `List[Dict]` - 마켓 정보 포함
- `verbose=True`: `Tuple` - (데이터, Limit 정보)

**Examples:**

```python
import fsfupbit

# 전체 티커
tickers = fsfupbit.get_tickers()
# ['KRW-BTC', 'KRW-ETH', 'BTC-ETH', ...]

# KRW 마켓만
krw_tickers = fsfupbit.get_tickers(fiat="KRW")
# ['KRW-BTC', 'KRW-ETH', ...]

# 상세 정보
markets = fsfupbit.get_tickers(is_details=True)
# [{'market': 'KRW-BTC', 'korean_name': '비트코인', ...}]

# Rate Limit 정보 포함
tickers, limit_info = fsfupbit.get_tickers(limit_info=True)
print(limit_info)
# {'group': 'market', 'interval': 'sec', 'remaining': '598', ...}
```

**API Reference:**
- [Upbit API - 마켓 코드 조회](https://docs.upbit.com/reference/%EB%A7%88%EC%BC%93-%EC%BD%94%EB%93%9C-%EC%A1%B0%ED%9A%8C)
- [Upbit API Review - market_all](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/market_all.md)

---

### get_current_price

현재가 정보를 조회합니다.

**API Endpoint**: `GET /v1/ticker`

```python
get_current_price(
    ticker: Union[str, List[str]],
    limit_info: bool = False,
    verbose: bool = False
) -> Union[float, Dict[str, float], List[Dict]]
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `ticker` | str | List[str] | - | 티커 또는 티커 리스트 |
| `limit_info` | bool | `False` | Rate Limit 정보 반환 |
| `verbose` | bool | `False` | 원본 API 응답 전체 반환 |

**Returns:**

- 단일 티커 + verbose=False: `float` - 현재가
- 복수 티커 + verbose=False: `Dict[str, float]` - {티커: 현재가}
- verbose=True: `List[Dict]` - 전체 API 응답

**Examples:**

```python
# 단일 티커
price = fsfupbit.get_current_price("KRW-BTC")
print(price)  # 95000000.0

# 복수 티커
prices = fsfupbit.get_current_price(["KRW-BTC", "KRW-ETH"])
print(prices)  # {'KRW-BTC': 95000000.0, 'KRW-ETH': 3500000.0}

# 전체 응답
data = fsfupbit.get_current_price("KRW-BTC", verbose=True)
print(data)
# [{'market': 'KRW-BTC', 'trade_date': '20260129', 'trade_time': '123456', 'trade_price': 95000000, ...}]
```

**API Reference:**
- [Upbit API - 현재가 정보](https://docs.upbit.com/reference/%ED%98%84%EC%9E%AC%EA%B0%80-%EC%A0%95%EB%B3%B4)
- [Upbit API Review - ticker](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/ticker.md)

---

### get_ohlcv

캔들 데이터를 조회합니다. (분, 일, 주, 월, 초, 연 캔들 지원)

**API Endpoint**: `GET /v1/candles/{unit}`

```python
get_ohlcv(
    ticker: str = "KRW-BTC",
    interval: str = "minute1",
    count: int = 200,
    to: Optional[str] = None,
    converting_price_unit: Optional[str] = None
) -> pd.DataFrame
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `ticker` | str | `"KRW-BTC"` | 티커 |
| `interval` | str | `"minute1"` | 캔들 종류 (minute1~240, day, week, month, seconds, years) |
| `count` | int | `200` | 조회 개수 (1~200) |
| `to` | Optional[str] | `None` | 마지막 캔들 시각 (YYYY-MM-DD HH:MM:SS) |
| `converting_price_unit` | Optional[str] | `None` | 가격 단위 (일 캔들만 지원) ⭐ |

**Interval Options:**

| Unit | Values | Description |
|------|--------|-------------|
| 분 캔들 | `minute1`, `minute3`, `minute5`, `minute10`, `minute15`, `minute30`, `minute60`, `minute240` | 1분~240분 |
| 일 캔들 | `day` | 일봉 |
| 주 캔들 | `week` | 주봉 |
| 월 캔들 | `month` | 월봉 |
| 초 캔들 ⭐ NEW | `seconds/1`, `seconds/3`, `seconds/5`, `seconds/10`, `seconds/15`, `seconds/30`, `seconds/60`, `seconds/240` | 2024-2025 추가 |
| 연 캔들 ⭐ NEW | `years`, `year` | 2024-2025 추가 |

**Returns:**

`pd.DataFrame` - 캔들 데이터

| 컬럼 | 설명 |
|------|------|
| `open` | 시가 |
| `high` | 고가 |
| `low` | 저가 |
| `close` | 종가 |
| `volume` | 거래량 |
| `value` | 거래대금 |

**Examples:**

```python
# 30일 일봉
df = fsfupbit.get_ohlcv("KRW-BTC", interval="day", count=30)
print(df.tail())

# 15분 캔들 (최근 100개)
df = fsfupbit.get_ohlcv("KRW-BTC", interval="minute15", count=100)

# 특정 시간까지 조회
df = fsfupbit.get_ohlcv("KRW-BTC", to="2026-01-29 00:00:00", count=30)

# 초 캔들 ⭐ NEW
df = fsfupbit.get_ohlcv("KRW-BTC", interval="seconds/30", count=100)

# 연 캔들 ⭐ NEW
df = fsfupbit.get_ohlcv("KRW-BTC", interval="years")

# 가격 단위 변환 (일 캔들만 지원) ⭐ NEW
df = fsfupbit.get_ohlcv("BTC-ETH", interval="day", converting_price_unit="BTC")
```

**API Reference:**
- [Upbit API - 캔들 조회](https://docs.upbit.com/reference/%EC%BA%94%EB%93%A4-%EC%A1%B0%ED%9A%8C)
- [Upbit API Review - candles](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/candles.md)

---

### get_orderbook

호가 정보를 조회합니다. (호가 모아보기 지원)

**API Endpoint**: `GET /v1/orderbook`

```python
get_orderbook(
    ticker: Union[str, List[str]],
    level: Optional[float] = None,
    limit_info: bool = False
) -> Union[Dict, List[Dict], Tuple]
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `ticker` | str | List[str] | - | 티커 또는 티커 리스트 |
| `level` ⭐ NEW | Optional[float] | `None` | 호가 모아보기 단위 (KRW 마켓만) |
| `limit_info` | bool | `False` | Rate Limit 정보 반환 |

**Level Parameter ⭐ NEW:**

호가를 지정한 단위로 묶어서 보여줍니다. (2024년 추가 기능)

| Level | 설명 | 지원 마켓 |
|-------|------|----------|
| `0` | 기본 호가 단위 (매수/매도 1~15호) | 전체 |
| `1` | 1,000원 단위 | KRW 마켓 |
| `2` | 5,000원 단위 | KRW 마켓 |
| `3` | 10,000원 단위 | KRW 마켓 |
| `4` | 50,000원 단위 | KRW 마켓 |
| `5` | 100,000원 단위 | KRW 마켓 |
| 사용자 지정 | 10000, 5000 등 | KRW 마켓 |

**Examples:**

```python
# 기본 호가
orderbook = fsfupbit.get_orderbook("KRW-BTC")
print(orderbook)
# {'market': 'KRW-BTC', 'timestamp': 1532118943687, 'orderbook_units': [...]}

# 호가 모아보기 (1만원 단위) ⭐ NEW
orderbook = fsfupbit.get_orderbook("KRW-BTC", level=10000)

# 복수 티커
orderbooks = fsfupbit.get_orderbook(["KRW-BTC", "KRW-ETH"])
print(orderbooks)
```

**API Reference:**
- [Upbit API - 호가 정보 조회](https://docs.upbit.com/reference/%ED%98%B8%EA%B0%80-%EC%A0%95%EB%B3%B4-%EC%A1%B0%ED%9A%8C)
- [Upbit API Review - orderbook_levels](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/orderbook_levels.md)

---

### get_orderbook_supported_levels ⭐ NEW

종목별 지원 호가 모아보기 단위를 조회합니다. (2024년 추가)

**API Endpoint**: `GET /v1/orderbook/supported_levels`

```python
get_orderbook_supported_levels(
    markets: List[str]
) -> List[Dict]
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `markets` | List[str] | 마켓 코드 리스트 |

**Returns:**

```python
[
    {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]},
    {"market": "KRW-ETH", "supported_levels": [0, 1, 2, 3, 4, 5]},
    {"market": "BTC-ETH", "supported_levels": [0]}  # KRW 외에는 0만
]
```

**Examples:**

```python
levels = fsfupbit.get_orderbook_supported_levels(["KRW-BTC", "KRW-ETH", "BTC-ETH"])
print(levels)
# [
#     {'market': 'KRW-BTC', 'supported_levels': [0, 1, 2, 3, 4, 5]},
#     {'market': 'KRW-ETH', 'supported_levels': [0, 1, 2, 3, 4, 5]},
#     {'market': 'BTC-ETH', 'supported_levels': [0]}
# ]
```

**Raises:**

| 예외 | 설명 |
|------|------|
| `ValueError` | markets가 빈 리스트이거나 유효하지 않은 경우 |

**API Reference:**
- [Upbit API Review - orderbook_levels](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/orderbook_levels.md)

---

## 거래/자산 관리 API

### Upbit 클래스

거래소 API를 사용하기 위한 클래스입니다.

```python
upbit = Upbit(access_key: str, secret_key: str)
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `access_key` | str | Upbit API Access Key |
| `secret_key` | str | Upbit API Secret Key |

---

### get_balance

보유 자산을 조회합니다.

**API Endpoint**: `GET /v1/accounts`

```python
get_balance(currency: Optional[str] = None) -> Union[float, Dict[str, float]]
```

**Parameters:**

| 파라미터 | 타입 | 기본값 | 설명 |
|----------|------|--------|------|
| `currency` | Optional[str] | `None` | 조회할 코인 심볼 (None: 전체) |

**Returns:**

- `currency=None`: `Dict[str, float]` - {코인: 보유량}
- `currency 지정`: `float` - 해당 코인 보유량

**Examples:**

```python
upbit = fsfupbit.Upbit(access_key, secret_key)

# 전체 보유 자산
balances = upbit.get_balance()
print(balances)
# {'KRW': 1000000.0, 'BTC': 0.5, 'ETH': 10.0}

# 원화 잔고
krw = upbit.get_balance("KRW")
print(krw)  # 1000000.0

# 비트코인 잔고
btc = upbit.get_balance("BTC")
print(btc)  # 0.5
```

---

### buy_limit_order / sell_limit_order

지정가 매수/매도 주문을 실행합니다.

**API Endpoint**: `POST /v1/orders`

```python
buy_limit_order(
    market: str,
    volume: Union[float, str],
    price: Union[float, str],
    ord_type: str = "limit",
    time_in_force: Optional[str] = None,  # ⭐ NEW
    identifier: Optional[str] = None
) -> Dict

sell_limit_order(
    market: str,
    volume: Union[float, str],
    price: Union[float, str],
    ord_type: str = "limit",
    time_in_force: Optional[str] = None,  # ⭐ NEW
    identifier: Optional[str] = None
) -> Dict
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `market` | str | 마켓 코드 (예: "KRW-BTC") |
| `volume` | float, str | 주문 수량 |
| `price` | float, str | 주문 가격 |
| `ord_type` | str | 주문 유형 (기본값: "limit") |
| `time_in_force` ⭐ NEW | Optional[str] | 주문 실행 조건 (2024년 추가) |
| `identifier` | Optional[str] | 사용자 식별자 |

**time_in_force Options ⭐ NEW:**

| 값 | 설명 |
|-----|------|
| `FOK` | Fill Or Kill - 체결 즉시 가능 여부 |
| `MAK` | Maker Or Kill - 즉시 체결 없으면 취소 (수수료 면제) |

**Examples:**

```python
# 기본 지정가 매수
order = upbit.buy_limit_order("KRW-BTC", 0.001, 95000000)
print(order)

# MAK 주문 (수수료 면제) ⭐ NEW
order = upbit.buy_limit_order(
    "KRW-BTC",
    0.001,
    95000000,
    time_in_force="MAK"
)
```

**API Reference:**
- [Upbit API Review - orders](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/orders.md)

---

### test_order ⭐ NEW

주문 생성 테스트를 수행합니다. (실제 체결 없음, 2024년 추가)

**API Endpoint:** `POST /v1/orders`

```python
test_order(
    market: str,
    side: str,
    volume: Union[float, str],
    price: Union[float, str],
    ord_type: str = "limit",
    time_in_force: Optional[str] = None
) -> Dict
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `market` | str | 마켓 코드 |
| `side` | str | 주문 종류 (bid: 매수, ask: 매도) |
| `volume` | float, str | 주문 수량 |
| `price` | float, str | 주문 가격 |
| `ord_type` | str | 주문 유형 |
| `time_in_force` | Optional[str] | 주문 실행 조건 |

**Returns:**

```python
{
    'market': 'KRW-BTC',
    'side': 'bid',
    'orderable': True  # 주문 가능 여부
}
```

**Examples:**

```python
# 주문 가능 여부 테스트
result = upbit.test_order(
    market="KRW-BTC",
    side="bid",
    volume=0.001,
    price=95000000
)
print(result)
```

---

### cancel_orders_open ⭐ NEW

미체결 주문을 일괄 취소합니다. (2024년 추가)

```python
cancel_orders_open(market: str) -> List[Dict]
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `market` | str | 마켓 코드 |

**Returns:**

```python
[
    {'uuid': 'order-uuid-1', 'state': 'cancel'},
    {'uuid': 'order-uuid-2', 'state': 'cancel'}
]
```

**Examples:**

```python
# KRW-BTC 미체결 주문 모두 취소
canceled = upbit.cancel_orders_open("KRW-BTC")
print(canceled)
```

---

### cancel_and_new_order ⭐ NEW

기존 주문을 취소하고 재주문합니다. (2024년 추가)

```python
cancel_and_new_order(
    uuid: str,
    new_price: Optional[Union[float, str]] = None,
    new_volume: Optional[Union[float, str]] = None
) -> Dict
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `uuid` | str | 취소할 주문 UUID |
| `new_price` | Optional[float, str] | 새 주문 가격 |
| `new_volume` | Optional[float, str] | 새 주문 수량 |

**Examples:**

```python
# 주문 취소 후 재주문 (가격 변경)
new_order = upbit.cancel_and_new_order(
    uuid="old-order-uuid",
    new_price=96000000
)
```

---

## 입출금 API

### 입금 주소 관리 ⭐ NEW

#### get_deposit_chance

입금 가능 정보를 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/orders/chance`

```python
get_deposit_chance(currency: str) -> Dict
```

**Examples:**

```python
chance = upbit.get_deposit_chance("BTC")
print(chance)
# {'currency': 'BTC', 'deposit_wallet_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'deposit_available': True}
```

---

#### create_deposit_address

입금 주소를 생성합니다. (2024년 추가)

**API Endpoint:** `POST /v1/deposits/generate_coin_address`

```python
create_deposit_address(currency: str) -> Dict
```

**Examples:**

```python
address = upbit.create_deposit_address("BTC")
print(address)
# {'currency': 'BTC', 'deposit_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'success': True}
```

---

#### get_deposit_address

개별 입금 주소를 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/deposits/coin_address`

```python
get_deposit_address(currency: str) -> Dict
```

**Examples:**

```python
addr = upbit.get_deposit_address("BTC")
print(addr)
# {'currency': 'BTC', 'deposit_address': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'secondary_address': ''}
```

---

#### get_deposit_addresses

전체 입금 주소 목록을 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/deposits/coin_addresses`

```python
get_deposit_addresses() -> List[Dict]
```

**Examples:**

```python
addrs = upbit.get_deposit_addresses()
print(addrs)
# [{'currency': 'BTC', 'deposit_address': '...'}, {'currency': 'ETH', 'deposit_address': '0x...'}]
```

---

#### get_krw_deposit_info

원화 입금 계좌 정보를 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/deposits/krw`

```python
get_krw_deposit_info() -> Dict
```

**Examples:**

```python
info = upbit.get_krw_deposit_info()
print(info)
# {'bank': 'Shinhan Bank', 'account_number': '123-456-789012', 'depositor': 'TEST'}
```

**API Reference:**
- [Upbit API Review - deposits](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/deposits.md)

---

### 출금 관리

#### withdraw_coin ⚠️ (Breaking Change)

코인을 출금합니다.

**API Endpoint:** `POST /v1/withdraws/coin`

```python
withdraw_coin(
    currency: str,
    amount: Union[float, str],
    address: str,
    net_type: str,  # ⚠️ 필수 파라미터 (보안 강화)
    secondary_address: Optional[str] = None,
    transaction_type: str = "default",
    contain_req: bool = False
) -> Dict
```

**Parameters:**

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `currency` | str | 코인 심볼 |
| `amount` | float, str | 출금 수량 |
| `address` | str | 출금 주소 |
| `net_type` ⚠️ | str | **필수** 네트워크 타입 (보안 강화) |
| `secondary_address` | Optional[str] | 2차 주소 |
| `transaction_type` | str | 거래 유형 |
| `contain_req` | bool | 요청 정보 포함 여부 |

**⚠️ Breaking Change (보안 강화):**
`net_type`은 필수 파라미터입니다. 자산 손실 방지를 위해 출금하려는 코인이 지원하는 네트워크 타입을 반드시 확인해야 합니다.

**Examples:**

```python
# 변경 전 (pyupbit 0.2.34) - 보안 위험 ⚠️
# upbit.withdraw_coin("BTC", 0.1, "address...")

# 변경 후 (fsfupbit 1.0.0) - 보안 강화 ✅
upbit.withdraw_coin(
    "BTC",
    0.1,
    "bc1q...",
    net_type="BTC"  # 필수! 자산 손실 방지
)
```

**net_type Examples:**

| Coin | net_type | 설명 |
|------|----------|------|
| BTC | `BTC` | Bitcoin 네트워크 |
| ETH | `ETH` | Ethereum 네트워크 |
| XRP | `XRP` | Ripple 네트워크 (Tag 필요 시 secondary_address) |
| TRX | `TRX` | TRON 네트워크 |

**API Reference:**
- [Upbit API Review - withdrawals](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/withdrawals.md)

---

#### get_withdraw_chance ⭐ NEW

출금 가능 정보를 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/withdraws/chance`

```python
get_withdraw_chance(currency: str, amount: Union[float, str]) -> Dict
```

**Examples:**

```python
chance = upbit.get_withdraw_chance("BTC", 0.01)
print(chance)
# {'currency': 'BTC', 'withdraw_available': True, 'withdraw_fee': 0.0005}
```

---

#### get_withdraw_addresses ⭐ NEW

출금 허용 주소 목록을 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/withdraws/addresses`

```python
get_withdraw_addresses(currency: Optional[str] = None) -> List[Dict]
```

**Examples:**

```python
# 전체 출금 허용 주소
all_addrs = upbit.get_withdraw_addresses()

# 특정 코인 출금 허용 주소
btc_addrs = upbit.get_withdraw_addresses("BTC")
```

---

## WebSocket API

### WebSocketManager

공개용 WebSocket 관리자입니다.

```python
ws = WebSocketManager(type: str, codes: List[str])
```

**Type Options:**

| 값 | 설명 |
|-----|------|
| `ticker` | 현재가 정보 |
| `orderbook` | 호가 정보 |
| `trade` | 체결 정보 |

**Examples:**

```python
# 현재가 WebSocket
ws = fsfupbit.WebSocketManager("ticker", ["KRW-BTC", "KRW-ETH"])
ws.start()

while True:
    data = ws.get()
    print(data)
```

---

### PrivateWebSocketManager ⭐ NEW

개인용 WebSocket 관리자입니다. (2024년 추가)

JWT 토큰 인증을 사용하여 개인 데이터를 실시간으로 수신합니다.

```python
pwm = PrivateWebSocketManager(
    access_key: str,
    secret_key: str,
    type: str,
    codes: Optional[List[str]] = None
)
```

**Type Options:**

| 값 | 설명 |
|-----|------|
| `MyOrder` | 내 주문 정보 |
| `MyAsset` | 내 자산 정보 |

**Examples:**

```python
# 내 주문 정보 실시간 수신
pwm = fsfupbit.PrivateWebSocketManager(
    access_key,
    secret_key,
    "MyOrder"
)
pwm.start()

while True:
    data = pwm.get()
    print(data)
```

**API Reference:**
- [Upbit API Review - websocket](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/websocket.md)

---

## 트래블룰 API ⭐ NEW

### get_travel_rule_vasps

트래블룰 지원 거래소 목록을 조회합니다. (2024년 추가)

**API Endpoint:** `GET /v1/travel-rule/vasps`

```python
get_travel_rule_vasps() -> List[Dict]
```

**Examples:**

```python
vasps = upbit.get_travel_rule_vasps()
print(vasps)
# [{'name': 'Binance', 'country': 'Malta', 'url': 'https://www.binance.com'}, ...]
```

---

### verify_travel_rule_by_uuid

입금 UUID로 트래블룰을 검증합니다. (2024년 추가)

**API Endpoint:** `POST /v1/travel-rule/:deposit_uuid`

```python
verify_travel_rule_by_uuid(
    deposit_uuid: str,
    vasp_name: str,
    vasp_address: str
) -> Dict
```

**Examples:**

```python
result = upbit.verify_travel_rule_by_uuid(
    deposit_uuid="xxx-yyy-zzz",
    vasp_name="Binance",
    vasp_address="MZPaXv4P6o..."
)
print(result)
```

**API Reference:**
- [Upbit API Review - services](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/upbit_apis/services.md)

---

## 예외 처리

### 커스텀 예외 클래스 ⭐ NEW

fsfupbit는 구체적인 예외 처리를 제공합니다. (2024년 추가)

```python
from fsfupbit.errors import (
    UpbitAPIError,
    UpbitValidationError,
    UpbitOrderError
)
```

#### UpbitAPIError

API 호출 에러

```python
try:
    tickers = fsfupbit.get_tickers()
except UpbitAPIError as e:
    print(f"API 에러: {e.message}")
    print(f"상태 코드: {e.status_code}")
    print(f"응답: {e.response}")
```

#### UpbitValidationError

입력값 검증 에러

```python
try:
    levels = fsfupbit.get_orderbook_supported_levels([])
except UpbitValidationError as e:
    print(f"검증 에러: {e.message}")
    print(f"필드: {e.field}")
```

#### UpbitOrderError

주문 관련 에러

```python
try:
    order = upbit.buy_limit_order("KRW-BTC", 0.001, 95000000)
except UpbitOrderError as e:
    print(f"주문 에러: {e.message}")
    print(f"주문 UUID: {e.order_uuid}")
    print(f"주문 종류: {e.order_side}")
```

---

## References

- [Upbit Open API Documentation](https://docs.upbit.com)
- [pyupbit Original Repository](https://github.com/sharebook-kr/pyupbit)
- [Upbit API Review Notes](https://github.com/fullstack-research-lab/enjoyTrading/tree/main/docs/upbit_apis_reviews)
- [fsfupbit Development Plan](https://github.com/fullstack-research-lab/enjoyTrading/blob/main/docs/fsfupbit_plan.md)
