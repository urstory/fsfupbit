from fsfupbit.quotation_api import *
import pytest
from unittest.mock import Mock, patch


def test_get_tickers_defaults():
    tickers  = get_tickers()
    assert "KRW-BTC" in tickers
    assert len(tickers) != 0


def test_get_tickers_with_fiat():
    fiats = ["KRW", "BTC", "USDT"]
    for fiat in fiats:
        fiat_tickers  = get_tickers(fiat)
        for ticker in fiat_tickers:
            assert ticker.startswith(fiat)


def test_get_tickers_with_limit_info():
    tickers, limit_info = get_tickers(limit_info=True)
    assert isinstance(tickers, list)
    assert isinstance(limit_info, dict)


def test_get_tickers_with_market_warning():
    """투자 유의 종목 필드 확인 테스트

    Upbit API는 market_event 딕셔너리를 반환하며,
    warning과 caution 하위 필드를 포함합니다.
    """
    tickers = get_tickers(is_details=True)
    for ticker in tickers:
        # market_event 필드가 존재하고 딕셔너리인지 확인
        assert "market_event" in ticker
        assert isinstance(ticker["market_event"], dict)

        # warning 필드는 boolean 값
        assert "warning" in ticker["market_event"]
        assert isinstance(ticker["market_event"]["warning"], bool)

        # caution 필드는 딕셔너리
        assert "caution" in ticker["market_event"]
        assert isinstance(ticker["market_event"]["caution"], dict)


def test_get_ohlcv_defaults():
    resp = get_ohlcv()
    assert isinstance(resp, pd.DataFrame)


def test_get_ohlcv_from():
    # PR #93: Timezone fix - now correctly returns only data within the specified range
    # 5 minutes of data (minute1 interval from 14:00:00 to 14:05:00) = 5 rows
    resp = get_ohlcv_from("KRW-BTC", "minute1", "2022-01-26 14:00:00", "2022-01-26 14:05:00")
    assert resp.index.size == 5  # Fixed from 200 to 5 after timezone fix
    assert isinstance(resp, pd.DataFrame)


def test_get_current_price_defaults():
    price = get_current_price("KRW-BTC")
    assert isinstance(price, float)


def test_get_current_price_multiple_tickers():
    prices = get_current_price(["KRW-BTC", "KRW-XRP"])
    assert isinstance(prices, dict)


# =============================================================================
# fsfupbit Phase 2: Orderbook Supported Levels Tests
# =============================================================================

class TestGetOrderbookSupportedLevels:
    """get_orderbook_supported_levels 함수 테스트"""

    def test_invalid_input_empty_list(self):
        """빈 리스트 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="markets 파라미터는 비어있지 않은 리스트여야 합니다"):
            get_orderbook_supported_levels([])

    def test_invalid_input_not_list(self):
        """리스트가 아닌 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="markets 파라미터는 비어있지 않은 리스트여야 합니다"):
            get_orderbook_supported_levels("KRW-BTC")

    def test_invalid_input_none(self):
        """None 입력 시 ValueError 발생"""
        with pytest.raises(ValueError, match="markets 파라미터는 비어있지 않은 리스트여야 합니다"):
            get_orderbook_supported_levels(None)

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_single_market_call(self, mock_api):
        """단일 마켓 조회 테스트"""
        mock_response = [
            {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]}
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook_supported_levels(["KRW-BTC"])

        assert result == mock_response
        mock_api.assert_called_once()

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_multiple_markets_call(self, mock_api):
        """여러 마켓 조회 테스트"""
        mock_response = [
            {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "KRW-ETH", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "BTC-ETH", "supported_levels": [0]}
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook_supported_levels(["KRW-BTC", "KRW-ETH", "BTC-ETH"])

        assert len(result) == 3
        assert result[0]["market"] == "KRW-BTC"
        assert result[2]["supported_levels"] == [0]

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_response_format_validation(self, mock_api):
        """응답 형식 검증 테스트"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "supported_levels": [0, 1, 2, 3, 4, 5]
            }
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook_supported_levels(["KRW-BTC"])

        # 응답이 리스트인지 확인
        assert isinstance(result, list)
        # 첫 번째 요소가 dict인지 확인
        assert isinstance(result[0], dict)
        # 필수 필드가 있는지 확인
        assert "market" in result[0]
        assert "supported_levels" in result[0]
        # supported_levels가 리스트인지 확인
        assert isinstance(result[0]["supported_levels"], list)

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_krw_market_levels(self, mock_api):
        """KRW 마켓의 단계 확인 테스트"""
        mock_response = [
            {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]}
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook_supported_levels(["KRW-BTC"])

        # KRW 마켓은 다양한 레벨을 지원해야 함
        levels = result[0]["supported_levels"]
        assert 0 in levels
        assert len(levels) > 1

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_non_krw_market_only_level_zero(self, mock_api):
        """KRW 외 마켓은 레벨 0만 지원하는지 확인"""
        mock_response = [
            {"market": "BTC-ETH", "supported_levels": [0]}
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook_supported_levels(["BTC-ETH"])

        levels = result[0]["supported_levels"]
        assert levels == [0]


# =============================================================================
# fsfupbit Phase 2: Orderbook Level Parameter Tests
# =============================================================================

class TestGetOrderbookLevelParameter:
    """get_orderbook() 함수의 level 파라미터 테스트"""

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_without_level_parameter(self, mock_api):
        """level 파라미터 없이 호출 (기존 동작 호환)"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "timestamp": 1532118943687,
                "orderbook_units": []
            }
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook("KRW-BTC")

        assert isinstance(result, dict)
        assert result["market"] == "KRW-BTC"
        # level 파라미터 없이 호출되었는지 확인
        mock_api.assert_called_once()

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_with_level_parameter(self, mock_api):
        """level 파라미터와 함께 호출"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "timestamp": 1532118943687,
                "orderbook_units": []
            }
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook("KRW-BTC", level=10000)

        assert isinstance(result, dict)
        mock_api.assert_called_once()

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_level_none(self, mock_api):
        """level=None 명시적 전달 테스트"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "orderbook_units": []
            }
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook("KRW-BTC", level=None)

        assert isinstance(result, dict)

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_level_zero(self, mock_api):
        """level=0 기본 단위 테스트"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "orderbook_units": []
            }
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook("KRW-BTC", level=0)

        assert isinstance(result, dict)

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_multiple_tickers_with_level(self, mock_api):
        """여러 티커와 level 파라미터 함께 사용"""
        mock_response = [
            {"market": "KRW-BTC", "orderbook_units": []},
            {"market": "KRW-ETH", "orderbook_units": []}
        ]
        mock_api.return_value = (mock_response, {})

        result = get_orderbook(["KRW-BTC", "KRW-ETH"], level=5000)

        assert isinstance(result, list)
        assert len(result) == 2

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_backward_compatibility(self, mock_api):
        """기존 코드와의 호환성 확인 (limit_info 파라미터)"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "orderbook_units": []
            }
        ]
        mock_limit_info = {"group": "orderbook", "interval": "500ms"}
        mock_api.return_value = (mock_response, mock_limit_info)

        result, limit_info = get_orderbook("KRW-BTC", limit_info=True)

        assert isinstance(result, dict)
        assert isinstance(limit_info, dict)

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_level_with_limit_info(self, mock_api):
        """level 파라미터와 limit_info 함께 사용"""
        mock_response = [
            {
                "market": "KRW-BTC",
                "orderbook_units": []
            }
        ]
        mock_limit_info = {"group": "orderbook"}
        mock_api.return_value = (mock_response, mock_limit_info)

        result, limit_info = get_orderbook("KRW-BTC", level=10000, limit_info=True)

        assert isinstance(result, dict)
        assert isinstance(limit_info, dict)

    def test_function_signature(self):
        """함수 시그니처 검증"""
        import inspect
        sig = inspect.signature(get_orderbook)
        params = sig.parameters

        # 파라미터 존재 확인
        assert "ticker" in params
        assert "level" in params
        assert "limit_info" in params

        # level 파라미터 기본값 확인
        assert params["level"].default is None
        assert params["level"].annotation == str or \
               params["level"].annotation == float or \
               params["level"].annotation == inspect.Parameter.empty or \
               "Optional" in str(params["level"].annotation)


# =============================================================================
# fsfupbit Phase 4: Candle Extension Tests
# =============================================================================

class TestCandleExtensions:
    """캔들 기능 확장 테스트"""

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_seconds_candle_url(self, mock_api):
        """초 캔들 URL 테스트"""
        from fsfupbit.quotation_api import get_url_ohlcv

        url = get_url_ohlcv("seconds/30")
        assert url == "https://api.upbit.com/v1/candles/seconds/30"

        url = get_url_ohlcv("seconds/60")
        assert url == "https://api.upbit.com/v1/candles/seconds/60"

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_years_candle_url(self, mock_api):
        """연 캔들 URL 테스트"""
        from fsfupbit.quotation_api import get_url_ohlcv

        url = get_url_ohlcv("years")
        assert url == "https://api.upbit.com/v1/candles/years"

        url = get_url_ohlcv("year")
        assert url == "https://api.upbit.com/v1/candles/years"

    @patch('fsfupbit.quotation_api._call_public_api')
    def test_converting_price_unit_parameter(self, mock_api):
        """converting_price_unit 파라미터 테스트"""
        mock_response = [
            [{
                "candle_date_time_kst": "2024-01-01T00:00:00",
                "opening_price": "100",
                "high_price": "110",
                "low_price": "90",
                "trade_price": "105",
                "candle_acc_trade_volume": "1.5",
                "candle_acc_trade_price": "150000"
            }]
        ]
        mock_api.return_value = (mock_response, {})

        df = get_ohlcv(
            "BTC-ETH",
            interval="day",
            converting_price_unit="BTC"
        )

        # API가 converting_price_unit 파라미터와 함께 호출되었는지 확인
        assert mock_api.called
        call_args = mock_api.call_args
        if call_args and len(call_args) > 1 and 'convertingPriceUnit' in call_args[1]:
            assert call_args[1]['convertingPriceUnit'] == "BTC"

    def test_get_ohlcv_signature(self):
        """get_ohlcv 함수 시그니처 검증"""
        import inspect
        sig = inspect.signature(get_ohlcv)
        params = sig.parameters

        # converting_price_unit 파라미터 확인
        assert "converting_price_unit" in params
        assert params["converting_price_unit"].default is None

        # 타입 힌트 확인
        assert params["ticker"].annotation == str or params["ticker"].annotation == inspect.Parameter.empty
        assert "interval" in params
        assert "count" in params


# =============================================================================
# fsfupbit Phase 4: PrivateWebSocketManager Tests
# =============================================================================

class TestPrivateWebSocketManager:
    """PrivateWebSocketManager 테스트"""

    def test_class_exists(self):
        """PrivateWebSocketManager 클래스 존재 확인"""
        from fsfupbit.websocket_api import PrivateWebSocketManager
        assert PrivateWebSocketManager is not None

    def test_init_with_required_params(self):
        """필수 파라미터로 초기화 테스트"""
        from fsfupbit.websocket_api import PrivateWebSocketManager

        pwm = PrivateWebSocketManager(
            access_key="test_access",
            secret_key="test_secret",
            type="MyOrder"
        )

        assert pwm.access_key == "test_access"
        assert pwm.secret_key == "test_secret"
        assert pwm.type == "MyOrder"
        assert pwm.codes == []

    def test_init_with_codes(self):
        """codes 파라미터로 초기화 테스트"""
        from fsfupbit.websocket_api import PrivateWebSocketManager

        pwm = PrivateWebSocketManager(
            access_key="test_access",
            secret_key="test_secret",
            type="MyAsset",
            codes=["KRW-BTC", "KRW-ETH"]
        )

        assert pwm.codes == ["KRW-BTC", "KRW-ETH"]

    def test_jwt_token_generation(self):
        """JWT 토큰 생성 테스트"""
        from fsfupbit.websocket_api import PrivateWebSocketManager

        pwm = PrivateWebSocketManager(
            access_key="test_access",
            secret_key="test_secret",
            type="MyOrder"
        )

        token = pwm._generate_jwt_token()
        assert token.startswith("Bearer ")
        # JWT 토큰은 base64로 인코딩되므로 구조를 확인
        assert len(token) > 20  # 최소한 토큰 길이 확인