import pytest
from unittest.mock import Mock
from requests.models import Response
from fsfupbit.errors import *
from fsfupbit.errors import (
    UpbitErrorMixin,
    UpbitError,
    BAD_REQUESTS,
    UNAUTHORIZED,
    TOO_MANY_REQ,
)

bad_requests = [err.name for err in BAD_REQUESTS]
unauthorized = [err.name for err in UNAUTHORIZED]
too_many_req = [err.name for err in TOO_MANY_REQ]


def test_raise_error_with_bad_requests():
    @error_handler
    def func(resp):
        return resp

    responses = list()
    for err_name in bad_requests:
        mock = Mock(spec=Response)
        mock.json.return_value = {
            "error": {
                "name": err_name,
                "message": "test_bad_requests",
            }
        }
        mock.status_code = 400
        mock.ok = False
        responses.append(mock)

    for response in responses:
        with pytest.raises(UpbitErrorMixin) as exc:
            func(response)

        error = response.json()["error"]
        assert exc.value.name == error["name"]
        assert exc.value.code == response.status_code
        assert exc.value.msg != error["message"]


def test_raise_error_with_unauthorized():
    @error_handler
    def func(resp):
        return resp

    responses = list()
    for err_name in unauthorized:
        mock = Mock(spec=Response)
        mock.json.return_value = {
            "error": {
                "name": err_name,
                "message": "test_unauthorized",
            }
        }
        mock.status_code = 401
        mock.ok = False
        responses.append(mock)

    for response in responses:
        with pytest.raises(UpbitErrorMixin) as exc:
            func(response)

        error = response.json()["error"]
        assert exc.value.name == error["name"]
        assert exc.value.code == response.status_code
        assert exc.value.msg != error["message"]


def test_raise_error_with_too_many_req():
    @error_handler
    def func(resp):
        return resp

    responses = list()
    for err_name in too_many_req:
        mock = Mock(spec=Response)
        mock.text = err_name
        mock.status_code = 429
        mock.ok = False
        responses.append(mock)

    for response in responses:
        with pytest.raises(UpbitErrorMixin) as exc:
            func(response)

        # too_many_request error doesn't use json response but text
        assert exc.value.name == response.text
        assert exc.value.code == response.status_code


# =============================================================================
# fsfupbit Phase 1: New Exception Classes Tests
# =============================================================================

class TestUpbitAPIError:
    """UpbitAPIError 테스트"""

    def test_basic_creation(self):
        """기본 생성 테스트"""
        error = UpbitAPIError("API 호출 실패")
        assert error.message == "API 호출 실패"
        assert str(error) == "API 호출 실패"

    def test_with_status_code(self):
        """상태 코드 포함 생성 테스트"""
        error = UpbitAPIError("API 호출 실패", status_code=500)
        assert error.message == "API 호출 실패"
        assert error.status_code == 500
        assert str(error) == "[500] API 호출 실패"

    def test_with_response(self):
        """응답 데이터 포함 생성 테스트"""
        response_data = {"error": {"name": "invalid_query", "message": "잘못된 쿼리"}}
        error = UpbitAPIError("API 호출 실패", status_code=400, response=response_data)
        assert error.response == response_data
        assert error.status_code == 400

    def test_inheritance(self):
        """Exception 상속 확인"""
        error = UpbitAPIError("Test")
        assert isinstance(error, Exception)


class TestUpbitValidationError:
    """UpbitValidationError 테스트"""

    def test_basic_creation(self):
        """기본 생성 테스트"""
        error = UpbitValidationError("티커 형식이 올바르지 않습니다")
        assert error.message == "티커 형식이 올바르지 않습니다"
        assert str(error) == "티커 형식이 올바르지 않습니다"

    def test_with_field(self):
        """필드명 포함 생성 테스트"""
        error = UpbitValidationError("형식 오류", field="ticker")
        assert error.message == "형식 오류"
        assert error.field == "ticker"
        assert str(error) == "ticker: 형식 오류"

    def test_inheritance(self):
        """Exception 상속 확인"""
        error = UpbitValidationError("Test")
        assert isinstance(error, Exception)


class TestUpbitOrderError:
    """UpbitOrderError 테스트"""

    def test_basic_creation(self):
        """기본 생성 테스트"""
        error = UpbitOrderError("주문 실패")
        assert error.message == "주문 실패"
        assert str(error) == "주문 실패"

    def test_with_order_uuid(self):
        """주문 UUID 포함 생성 테스트"""
        error = UpbitOrderError("주문 실패", order_uuid="abc-123-def")
        assert error.order_uuid == "abc-123-def"
        assert "uuid=abc-123-def" in str(error)

    def test_with_order_side(self):
        """주문 종류 포함 생성 테스트"""
        error = UpbitOrderError("주문 실패", order_side="bid")
        assert error.order_side == "bid"
        assert "side=bid" in str(error)

    def test_with_all_attributes(self):
        """모든 속성 포함 생성 테스트"""
        error = UpbitOrderError(
            "주문 실패",
            order_uuid="abc-123-def",
            order_side="ask"
        )
        assert error.message == "주문 실패"
        assert error.order_uuid == "abc-123-def"
        assert error.order_side == "ask"
        result_str = str(error)
        assert "주문 실패" in result_str
        assert "side=ask" in result_str
        assert "uuid=abc-123-def" in result_str

    def test_inheritance(self):
        """Exception 상속 확인"""
        error = UpbitOrderError("Test")
        assert isinstance(error, Exception)
