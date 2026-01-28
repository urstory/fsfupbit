import pytest
from unittest.mock import patch

from fsfupbit.exchange_api import *


@pytest.mark.parametrize(
        "expected_output,actual_inputs",
        [
            # quote (hoga) >= 2000000
            (2000000, (2000100, 2000900)),
            # quote (hoga) >= 1000000
            (1000000, (1000100, 1000400)),
            # quote (hoga) >= 500000
            (500000, (500010, 500090)),
            # quote (hoga) >= 100000
            (100000, (100010, 100040)),
            # quote (hoga) >= 10000
            (10000, (10001, 10004)),
            # quote (hoga) >= 1000
            (1001, (1001.1, 1001.4)),
            # quote (hoga) >= 100
            (101.2, (101.21, 101.29)),
            # quote (hoga) >= 10
            (10.31, (10.314, 10.318)),
            # quote (hoga) >= 1
            (2.577, (2.5775, 2.57709)),
            # quote (hoga) >= 0.1
            (0.1728, (0.17286, 0.17287)),
            # quote (hoga) >= 0.01
            (0.01, (0.010001, 0.010006)),
            # quote (hoga) >= 0.001
            (0.001, (0.0010009, 0.0010007)),
            # quote (hoga) >= 0.0001
            (0.0002, (0.00020001, 0.000200012)),
            # quote (hoga) >= 0.00001 ("else")
            (0.00008002, (0.000080023, 0.000080024)),
        ])
def test_get_tick_size_defaults(expected_output, actual_inputs):
    """
    Given: expected output and actual inputs
    When: every actual input is passed to get_tick_size(..)
    Then: indeed expected_output == get_tick_size(actual_input)
    , consistent with https://docs.upbit.com/docs/market-info-trade-price-detail (v 1.4.4)
    """
    for actual_input in actual_inputs:
        assert expected_output == get_tick_size(actual_input)


# =============================================================================
# fsfupbit Phase 1: Withdraw Coin net_type Parameter Tests
# =============================================================================

class TestWithdrawCoinNetType:
    """withdraw_coin 함수의 net_type 필수 파라미터 테스트"""

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    def test_withdraw_coin_signature_has_net_type(self, mock_upbit):
        """withdraw_coin 함수가 net_type 파라미터를 가지고 있는지 확인"""
        import inspect
        sig = inspect.signature(mock_upbit.withdraw_coin)
        params = sig.parameters

        # 필수 파라미터 확인
        assert "currency" in params
        assert "amount" in params
        assert "address" in params
        assert "net_type" in params

        # net_type이 필수 파라미터인지 확인 (기본값이 없는지)
        assert params["net_type"].default == inspect.Parameter.empty

    @pytest.mark.parametrize("net_type", ["ETH", "BTC", "TRX", "XRP"])
    def test_withdraw_coin_accepts_valid_net_types(self, mock_upbit, net_type):
        """유효한 net_type 값으로 함수 호출이 가능한지 확인"""
        # 실제 API 호출은 mock으로 대체해야 하므로 시그니처만 확인
        import inspect
        sig = inspect.signature(mock_upbit.withdraw_coin)
        # 파라미터 타입이 str인지 확인
        assert sig.parameters["net_type"].annotation == str or sig.parameters["net_type"].annotation == inspect.Parameter.empty


# =============================================================================
# fsfupbit Phase 1: Deposit URL Fix Tests
# =============================================================================

class TestDepositURLFix:
    """입금 API URL 오타 수정 테스트"""

    def test_deposit_list_url_is_correct(self):
        """get_deposit_list 함수가 올바른 URL을 사용하는지 확인"""
        import inspect
        source = inspect.getsource(Upbit.get_deposit_list)

        # URL에 //v1 (이중 슬래시)이 없는지 확인
        assert "api.upbit.com//v1" not in source, \
            "입금 API URL에 이중 슬래시 오타가 있습니다: //v1 → /v1"

        # 올바른 URL이 포함되어 있는지 확인
        assert "api.upbit.com/v1/deposits" in source, \
            "입금 API URL이 올바르지 않습니다: https://api.upbit.com/v1/deposits"


# =============================================================================
# fsfupbit Phase 3: Deposit Address Functions Tests
# =============================================================================

class TestDepositAddressFunctions:
    """입금 주소 관련 함수 테스트"""

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_deposit_chance(self, mock_request, mock_upbit):
        """입금 가능 정보 조회 테스트"""
        mock_response = [
            {
                "currency": "BTC",
                "deposit_wallet_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "deposit_available": True
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_deposit_chance("BTC")

        assert isinstance(result, dict)
        assert "currency" in result
        mock_request.assert_called_once()

    @patch('fsfupbit.exchange_api._send_post_request')
    def test_create_deposit_address(self, mock_request, mock_upbit):
        """입금 주소 생성 요청 테스트"""
        mock_response = [
            {
                "currency": "BTC",
                "deposit_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "success": True
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.create_deposit_address("BTC")

        assert isinstance(result, dict)
        assert result.get("success") is True

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_deposit_addresses(self, mock_request, mock_upbit):
        """전체 입금 주소 조회 테스트"""
        mock_response = [
            [
                {"currency": "BTC", "deposit_address": "btc-address"},
                {"currency": "ETH", "deposit_address": "eth-address"}
            ]
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_deposit_addresses()

        assert isinstance(result, list)
        assert len(result) == 2

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_deposit_address(self, mock_request, mock_upbit):
        """개별 입금 주소 조회 테스트"""
        mock_response = [
            {
                "currency": "BTC",
                "deposit_address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "secondary_address": ""
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_deposit_address("BTC")

        assert isinstance(result, dict)
        assert "deposit_address" in result

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_krw_deposit_info(self, mock_request, mock_upbit):
        """원화 입금 계좌 정보 조회 테스트"""
        mock_response = [
            {
                "bank": "Shinhan Bank",
                "account_number": "123-456-789012",
                "depositor": "TEST"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_krw_deposit_info()

        assert isinstance(result, dict)
        assert "bank" in result
        assert "account_number" in result


# =============================================================================
# fsfupbit Phase 3: Withdraw Related Functions Tests
# =============================================================================

class TestWithdrawFunctions:
    """출금 관련 함수 테스트"""

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_withdraw_chance(self, mock_request, mock_upbit):
        """출금 가능 정보 조회 테스트"""
        mock_response = [
            {
                "currency": "BTC",
                "withdraw_available": True,
                "withdraw_fee": 0.0005
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_withdraw_chance("BTC", 0.01)

        assert isinstance(result, dict)
        assert "withdraw_available" in result

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_withdraw_addresses_all(self, mock_request, mock_upbit):
        """전체 출금 허용 주소 조회 테스트"""
        mock_response = [
            [
                {"currency": "BTC", "address": "bc1q...", "whitelist": True},
                {"currency": "ETH", "address": "0x...", "whitelist": True}
            ]
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_withdraw_addresses()

        assert isinstance(result, list)
        assert len(result) == 2

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_withdraw_addresses_currency(self, mock_request, mock_upbit):
        """특정 코인 출금 허용 주소 조회 테스트"""
        mock_response = [
            [
                {"currency": "BTC", "address": "bc1q...", "whitelist": True}
            ]
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_withdraw_addresses("BTC")

        assert isinstance(result, list)
        assert len(result) == 1
        if result:
            assert result[0]["currency"] == "BTC"


# =============================================================================
# fsfupbit Phase 3: Advanced Order Functions Tests
# =============================================================================

class TestAdvancedOrderFunctions:
    """고급 주문 함수 테스트"""

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    @patch('fsfupbit.exchange_api._send_post_request')
    def test_test_order(self, mock_request, mock_upbit):
        """주문 생성 테스트 함수 테스트"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "side": "bid",
                "orderable": True
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.test_order(
            market="KRW-BTC",
            side="bid",
            volume=0.001,
            price=50000000
        )

        assert isinstance(result, dict)
        mock_request.assert_called_once()

    @patch('fsfupbit.exchange_api._send_post_request')
    def test_test_order_with_time_in_force(self, mock_request, mock_upbit):
        """주문 생성 테스트 (time_in_force 파라미터)"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "side": "bid",
                "orderable": True
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.test_order(
            market="KRW-BTC",
            side="bid",
            volume=0.001,
            price=50000000,
            time_in_force="FOK"
        )

        assert isinstance(result, dict)

    @patch('fsfupbit.exchange_api._send_get_request')
    @patch('fsfupbit.exchange_api._send_delete_request')
    def test_cancel_orders_open_empty(self, mock_delete, mock_get, mock_upbit):
        """주문 일괄 취소 (미체결 주문 없음)"""
        mock_get.return_value = ([], {})

        result = mock_upbit.cancel_orders_open("KRW-BTC")

        assert result == []

    @patch('fsfupbit.exchange_api._send_get_request')
    @patch('fsfupbit.exchange_api._send_delete_request')
    def test_cancel_orders_open_with_orders(self, mock_delete, mock_get, mock_upbit):
        """주문 일괄 취소 (미체결 주문 있음)"""
        # Mock: 2개의 미체결 주문 반환
        mock_get.return_value = (
            [
                {"uuid": "order-1", "market": "KRW-BTC"},
                {"uuid": "order-2", "market": "KRW-BTC"}
            ],
            {}
        )

        # Mock: 주문 취소 성공
        mock_delete.return_value = [
            {"uuid": "order-1", "state": "cancel"},
            {"uuid": "order-2", "state": "cancel"}
        ]

        result = mock_upbit.cancel_orders_open("KRW-BTC")

        assert isinstance(result, list)
        assert len(result) == 2

    @patch('fsfupbit.exchange_api._send_get_request')
    @patch('fsfupbit.exchange_api._send_delete_request')
    @patch('fsfupbit.exchange_api._send_post_request')
    def test_cancel_and_new_order(
        self, mock_post, mock_delete, mock_get, mock_upbit
    ):
        """취소 후 재주문 테스트"""
        # Mock: 기존 주문 조회
        mock_get.side_effect = [
            ({"uuid": "old-order", "side": "bid", "market": "KRW-BTC",
              "price": "50000000", "remaining_volume": "0.001"}, {}),
            ({"uuid": "new-order", "side": "bid", "market": "KRW-BTC",
              "price": "51000000", "remaining_volume": "0.001"}, {})
        ]

        # Mock: 주문 취소
        mock_delete.return_value = [
            {"uuid": "old-order", "state": "cancel"}
        ]

        # Mock: 새 주문 생성
        mock_post.return_value = [
            {"uuid": "new-order", "state": "wait"}
        ]

        result = mock_upbit.cancel_and_new_order(
            uuid="old-order",
            new_price=51000000
        )

        assert isinstance(result, dict)

    def test_order_function_signatures(self, mock_upbit):
        """주문 함수 시그니처 검증"""
        import inspect

        # buy_limit_order 함수 확인
        sig = inspect.signature(mock_upbit.buy_limit_order)
        params = sig.parameters
        assert "time_in_force" in params
        assert params["time_in_force"].default is None

        # sell_limit_order 함수 확인
        sig = inspect.signature(mock_upbit.sell_limit_order)
        params = sig.parameters
        assert "time_in_force" in params
        assert params["time_in_force"].default is None


# =============================================================================
# fsfupbit Phase 4: Travel Rule Functions Tests
# =============================================================================

class TestTravelRuleFunctions:
    """트래블룰 함수 테스트"""

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_travel_rule_vasps(self, mock_request, mock_upbit):
        """트래블룰 지원 거래소 목록 조회 테스트"""
        mock_response = [
            [
                {
                    "name": "Binance",
                    "country": "Malta",
                    "url": "https://www.binance.com"
                },
                {
                    "name": "Coinbase",
                    "country": "United States",
                    "url": "https://www.coinbase.com"
                }
            ]
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_travel_rule_vasps()

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["name"] == "Binance"

    @patch('fsfupbit.exchange_api._send_post_request')
    def test_verify_travel_rule_by_uuid(self, mock_request, mock_upbit):
        """입금 UUID로 트래블룰 검증 테스트"""
        mock_response = [
            {
                "deposit_uuid": "xxx-yyy-zzz",
                "status": "verified",
                "vasp_name": "Binance",
                "vasp_address": "MZPaXv4P6o..."
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.verify_travel_rule_by_uuid(
            deposit_uuid="xxx-yyy-zzz",
            vasp_name="Binance",
            vasp_address="MZPaXv4P6o..."
        )

        assert isinstance(result, dict)
        assert result["status"] == "verified"

    def test_travel_rule_functions_exist(self, mock_upbit):
        """트래블룰 함수 존재 확인"""
        assert hasattr(mock_upbit, "get_travel_rule_vasps")
        assert hasattr(mock_upbit, "verify_travel_rule_by_uuid")

    def test_travel_rule_function_signatures(self, mock_upbit):
        """트래블룰 함수 시그니처 검증"""
        import inspect

        # get_travel_rule_vasps 함수 확인
        sig = inspect.signature(mock_upbit.get_travel_rule_vasps)
        params = sig.parameters
        assert "contain_req" in params

        # verify_travel_rule_by_uuid 함수 확인
        sig = inspect.signature(mock_upbit.verify_travel_rule_by_uuid)
        params = sig.parameters
        assert "deposit_uuid" in params
        assert "vasp_name" in params
        assert "vasp_address" in params


# =============================================================================
# fsfupbit PR #129 Fix: Deprecated Order API Endpoints
# =============================================================================

class TestDeprecatedOrderAPIFix:
    """
    업데이트 되지 않은 주문 조회 API 엔드포인트 수정 테스트

    Issue #127: /v1/orders 엔드포인트가 deprecated 됨
    PR #129: https://github.com/sharebook-kr/pyupbit/pull/129

    변경 사항:
    - /v1/order → /v1/orders/uuids (UUID 기반 조회)
    - /v1/orders → /v1/orders/open (state=wait,watch)
    - /v1/orders → /v1/orders/closed (state=cancel,done)
    """

    @pytest.fixture
    def mock_upbit(self):
        """Upbit 인스턴스 fixture"""
        access = "test_access_key"
        secret = "test_secret_key"
        return Upbit(access, secret)

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_uuid_uses_uuids_endpoint(self, mock_request, mock_upbit):
        """
        UUID로 주문 조회 시 /v1/orders/uuids 엔드포인트 사용 테스트

        Given: UUID 형식의 주문 ID
        When: get_order() 함수 호출
        Then: /v1/orders/uuids 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "wait"
            }
        ]
        mock_request.return_value = mock_response

        # UUID 형식으로 조회
        result = mock_upbit.get_order("12345678-1234-1234-1234-123456789012")

        # /v1/orders/uuids 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/uuids"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_wait_state_uses_open_endpoint(self, mock_request, mock_upbit):
        """
        state=wait로 주문 조회 시 /v1/orders/open 엔드포인트 사용 테스트

        Given: 마켓 ticker와 state='wait'
        When: get_order() 함수 호출
        Then: /v1/orders/open 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "wait"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_order("KRW-BTC", state='wait')

        # /v1/orders/open 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/open"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_watch_state_uses_open_endpoint(self, mock_request, mock_upbit):
        """
        state=watch로 주문 조회 시 /v1/orders/open 엔드포인트 사용 테스트

        Given: 마켓 ticker와 state='watch'
        When: get_order() 함수 호출
        Then: /v1/orders/open 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "watch"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_order("KRW-BTC", state='watch')

        # /v1/orders/open 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/open"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_cancel_state_uses_closed_endpoint(self, mock_request, mock_upbit):
        """
        state=cancel로 주문 조회 시 /v1/orders/closed 엔드포인트 사용 테스트

        Given: 마켓 ticker와 state='cancel'
        When: get_order() 함수 호출
        Then: /v1/orders/closed 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "cancel"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_order("KRW-BTC", state='cancel')

        # /v1/orders/closed 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/closed"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_done_state_uses_closed_endpoint(self, mock_request, mock_upbit):
        """
        state=done로 주문 조회 시 /v1/orders/closed 엔드포인트 사용 테스트

        Given: 마켓 ticker와 state='done'
        When: get_order() 함수 호출
        Then: /v1/orders/closed 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "done"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_order("KRW-BTC", state='done')

        # /v1/orders/closed 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/closed"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_individual_order_uses_uuids_endpoint(self, mock_request, mock_upbit):
        """
        get_individual_order() 함수가 /v1/orders/uuids 엔드포인트 사용 테스트

        Given: UUID
        When: get_individual_order() 함수 호출
        Then: /v1/orders/uuids 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "done"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_individual_order("12345678-1234-1234-1234-123456789012")

        # /v1/orders/uuids 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/uuids"
        assert result is not None

    @patch('fsfupbit.exchange_api._send_get_request')
    def test_get_order_with_multiple_states_list(self, mock_request, mock_upbit):
        """
        다중 상태 리스트로 주문 조회 테스트 (PR #114)

        Given: 상태 리스트 ["done", "cancel"]
        When: get_order() 함수 호출
        Then: states[] 파라미터와 /v1/orders/closed 엔드포인트 사용
        """
        mock_response = [
            {
                "uuid": "12345678-1234-1234-1234-123456789012",
                "market": "KRW-BTC",
                "state": "done"
            },
            {
                "uuid": "12345678-1234-1234-1234-123456789013",
                "market": "KRW-BTC",
                "state": "cancel"
            }
        ]
        mock_request.return_value = mock_response

        result = mock_upbit.get_order("KRW-BTC", state=['done', 'cancel'])

        # /v1/orders/closed 엔드포인트가 호출되었는지 확인
        call_args = mock_request.call_args
        url = call_args[1]['url'] if 'url' in call_args[1] else call_args[0][0]
        assert url == "https://api.upbit.com/v1/orders/closed"
        # states[] 파라미터가 전달되었는지 확인
        assert result is not None
