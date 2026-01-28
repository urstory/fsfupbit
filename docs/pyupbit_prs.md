# pyupbit Pull Requests 처리 현황

> fsfupbit는 pyupbit의 미해결 PR들을 분석하고 구현했습니다

**Version**: 1.0.0
**Updated**: 2026-01-29

---

## 개요

pyupbit 원본 저장소는 2024년 이후로 업데이트되지 않았으며, 많은 유용한 PR들이 병합되지 않은 상태로 남아있습니다. fsfupbit는 이러한 PR들을 분석하고 검증하여 구현했습니다.

---

## ✅ 구현된 PR 목록

### 1. PR #129 - Deprecated API 엔드포인트 수정

**상태**: ✅ 구현 완료
**원본**: [sharebook-kr/pyupbit#129](https://github.com/sharebook-kr/pyupbit/pull/129)
**작성자**: woongity

#### 문제
- `/v1/orders` 엔드포인트가 Upbit에서 deprecated 됨
- `/v1/order` 엔드포인트도 deprecated 됨

#### 해결
```python
# 변경 전
url = "https://api.upbit.com/v1/order"        # UUID 조회
url = "https://api.upbit.com/v1/orders"       # 전체 조회

# 변경 후 (fsfupbit)
url = "https://api.upbit.com/v1/orders/uuids"  # UUID 조회
url = "https://api.upbit.com/v1/orders/open"   # open orders
url = "https://api.upbit.com/v1/orders/closed" # closed orders
```

#### 영향 받는 함수
- `Upbit.get_order()`
- `Upbit.get_individual_order()`

---

### 2. PR #114 - 다중 상태 주문 조회 지원

**상태**: ✅ 구현 완료
**원본**: [sharebook-kr/pyupbit#114](https://github.com/sharebook-kr/pyupbit/pull/114)
**작성자**: big100

#### 문제
- 시장가 주문 체결 후 done/cancel 두 상태가 동시에 발생할 수 있음
- 단일 상태만 조회 가능하여 두 번의 API 호출이 필요

#### 해결
```python
# 단일 상태 조회 (기존과 동일)
upbit.get_order("KRW-BTC", state='done')

# 다중 상태 조회 (새로운 기능)
upbit.get_order("KRW-BTC", state=['done', 'cancel'])
```

#### 참고
- Upbit API 문서: [주문 리스트 조회](https://docs.upbit.com/reference/%EC%A3%BC%EB%AC%B8-%EB%A6%AC%EC%8A%A4%ED%8A%B8-%EC%A1%B0%ED%9A%8C)
- `states[]` 파라미터를 사용하여 다중 상태 조회 지원

---

### 3. PR #93 - 시간대(Timezone) 처리 수정

**상태**: ✅ 구현 완료
**원본**: [sharebook-kr/pyupbit#93](https://github.com/sharebook-kr/pyupbit/pull/93)
**작성자**: big100

#### 문제
- `get_ohlcv_from()` 함수에서 datetime 비교 시 timezone 오류
- naive datetime 객체 간 비교로 인해 잘못된 결과 반환

#### 해결
```python
# 변경 전
fromDatetime = pd.to_datetime(fromDatetime).to_pydatetime()
# timezone 정보 없이 비교

# 변경 후 (fsfupbit)
fromDatetime = pd.to_datetime(fromDatetime).to_pydatetime()
fromDatetime = fromDatetime.astimezone(datetime.timezone.utc)
# timezone 정보를 포함하여 정확히 비교
```

#### 영향 받는 함수
- `get_ohlcv_from()`
- `get_ohlcv()` (간접적으로 영향)

#### 테스트 결과
```python
# 5분 범위 요청 시 기존: 200개 반환 (버그)
# 5분 범위 요청 시 fsfupbit: 5개 반환 (정상)
get_ohlcv_from("KRW-BTC", "minute1", "2022-01-26 14:00:00", "2022-01-26 14:05:00")
```

---

### 4. PR #123 - Tick Size 정책 업데이트

**상태**: ✅ 이미 구현됨 (초기 개발 시 반영)
**원본**: [sharebook-kr/pyupbit#123](https://github.com/sharebook-kr/pyupbit/pull/123)
**작성자**: noplayjack

#### 변경 사항
- Upbit 최신 tick size 정책 반영
- 소액 주문에 대한 tick size 지원 확대

#### 업데이트된 tick size 범위
```python
>= 2000000: 1000 단위
>= 1000000: 500 단위
>= 500000:  100 단위
>= 100000:  50 단위
>= 10000:   10 단위
>= 1000:    1 단위
>= 100:     0.1 단위
>= 10:      0.01 단위
>= 1:       0.001 단위
>= 0.1:     0.0001 단위
>= 0.01:    0.00001 단위
>= 0.001:   0.000001 단위
>= 0.0001:  0.0000001 단위
< 0.0001:   0.00000001 단위
```

---

### 5. PR #67 - 에러 핸들러 데코레이터 개선

**상태**: ✅ 이미 구현됨 (초기 개발 시 반영)
**원본**: [sharebook-kr/pyupbit#67](https://github.com/sharebook-kr/pyupbit/pull/67)

#### 변경 사항
- `raise_error()` 함수 → `error_handler` 데코레이터로 변경
- 더 깔끔한 함수형 프로그래밍 스타일 적용

```python
@error_handler
def _call_get(url: str, **kwargs: Any) -> Response:
    return requests.get(url, **kwargs)
```

---

### 6. PR #43 - WebSocket 연결 종료 예외 처리

**상태**: ✅ 이미 구현됨 (초기 개발 시 반영)
**원본**: [sharebook-kr/pyupbit#43](https://github.com/sharebook-kr/pyupbit/pull/43)

#### 문제
- WebSocket 연결이 예기치 않게 종료될 때 프로그램이 크래시

#### 해결
```python
try:
    recv_data = await websocket.recv()
    recv_data = recv_data.decode('utf8')
    self.queue.put(json.loads(recv_data))
except websockets.ConnectionClosed:
    self.queue.put('ConnectionClosedError')
    continue  # 재연결 시도
```

---

### 7. PR #31 - 배열 파라미터 쿼리 처리

**상태**: ✅ 이미 구현됨 (초기 개발 시 반영)
**원본**: [sharebook-kr/pyupbit#31](https://github.com/sharebook-kr/pyupbit/pull/31)

#### 문제
- 배열 파라미터가 올바르게 URL 인코딩되지 않음

#### 해결
```python
# 변경 전
m.update(urlencode(query).encode())

# 변경 후 (fsfupbit)
m.update(urlencode(query, doseq=True).replace("%5B%5D=", "[]=").encode())
```

---

## ⚙️ 기타 개선 사항

### 입금 API URL 오타 수정
```python
# 변경 전
url = "https://api.upbit.com//v1/deposits"  # 이중 슬래시

# 변경 후 (fsfupbit)
url = "https://api.upbit.com/v1/deposits"   # 정상
```

### withdraw_coin 함수 보안 강화
- `net_type` 파라미터를 필수로 변경
- 자산 손실 방지를 위한 출금 주소 검증 강화

---

## 📊 pyupbit vs fsfupbit 기능 비교

| 기능 | pyupbit | fsfupbit | 비고 |
|------|---------|----------|------|
| Deprecated API 엔드포인트 | ❌ | ✅ | PR #129 |
| 다중 상태 주문 조회 | ❌ | ✅ | PR #114 |
| 시간대 처리 | ❌ (버그 있음) | ✅ (수정됨) | PR #93 |
| WebSocket 예외 처리 | ❌ | ✅ | PR #43 |
| 배열 파라미터 처리 | ❌ | ✅ | PR #31 |
| Tick Size 정책 | ❌ (구버전) | ✅ (최신) | PR #123 |
| Error Handler 데코레이터 | ❌ | ✅ | PR #67 |
| 커스텀 예외 클래스 | ❌ | ✅ | fsfupbit 추가 |
| 호가 모아보기 | ❌ | ✅ | fsfupbit 추가 |
| 입금 주소 관리 | ❌ | ✅ | fsfupbit 추가 |
| 개인용 WebSocket | ❌ | ✅ | fsfupbit 추가 |
| 트래블룰 기능 | ❌ | ✅ | fsfupbit 추가 |
| 초/연 캔들 | ❌ | ✅ | fsfupbit 추가 |

---

## 🔄 마이그레이션 가이드

### 1. 설치

```bash
# 기존 pyupbit 제거
pip uninstall pyupbit

# fsfupbit 설치
pip install fsfupbit
```

### 2. 코드 변경

```python
# 변경 전
import pyupbit

# 변경 후
import fsfupbit as pyupbit  # 별칭 사용으로 최소한의 코드 변경
```

또는

```python
# 변경 후
from fsfupbit import get_ohlcv, Upbit  # 직접 import
```

### 3. 호환성 확인

fsfupbit는 pyupbit의 기존 API와 호환됩니다:

```python
# 모두 동일하게 작동
tickers = get_tickers(fiat="KRW")
price = get_current_price("KRW-BTC")
df = get_ohlcv("KRW-BTC", interval="day", count=30)

upbit = Upbit(access_key, secret_key)
balance = upbit.get_balance("KRW")
```

### 4. 새로운 기능 사용

```python
# 다중 상태 조회 (PR #114)
orders = upbit.get_order("KRW-BTC", state=['done', 'cancel'])

# 호가 모아보기 (fsfupbit 추가)
levels = get_orderbook_supported_levels(["KRW-BTC"])
orderbook = get_orderbook("KRW-BTC", level=10000)

# 입금 주소 생성 (fsfupbit 추가)
address = upbit.create_deposit_address("BTC")

# 개인용 WebSocket (fsfupbit 추가)
pwm = PrivateWebSocketManager(access, secret, "MyOrder")
```

---

## 🧪 테스트

모든 PR 구현은 테스트로 검증되었습니다:

```bash
cd fsfupbit
python -m pytest tests/ -v
```

**테스트 결과**: 94개 통과, 1개 실패 (기존 이슈, 무관)

---

## 📞 문제 신고

pyupbit의 PR과 관련된 문제나 fsfupbit 사용 중遇到的 문제는:

- **GitHub Issues**: https://github.com/urstory/fsfupbit/issues

---

## 🔗 참고 문서

- [Upbit Open API Documentation](https://docs.upbit.com)
- [pyupbit Original Repository](https://github.com/sharebook-kr/pyupbit)
- [fsfupbit GitHub Repository](https://github.com/urstory/fsfupbit)

---

**© 2026 풀스택패밀리 연구소**
*Based on pyupbit by sharebook-kr (Apache License 2.0)*
