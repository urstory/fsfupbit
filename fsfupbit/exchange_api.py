#
# fsfupbit - Enhanced Python wrapper for Upbit API
#
# Based on pyupbit (https://github.com/sharebook-kr/pyupbit)
# Original Copyright (c) 2021 sharebook-kr
# Modifications Copyright (c) 2025 풀스택패밀리 연구소
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for the full text of the license.
#

# -*- coding: utf-8 -*-

"""
pyupbit.exchange_api

This module provides exchange api of the Upbit API.
"""

import math
import jwt          # PyJWT
import re
import uuid
import hashlib
from typing import Optional, Union, List, Dict, Any
from urllib.parse import urlencode
from fsfupbit.request_api import _send_get_request, _send_post_request, _send_delete_request


def get_tick_size(price, method="floor"):
    """원화마켓 주문 가격 단위
    TODO: rename this to adjust_price_per_tick_table?
    tick size is by definition the minimum allowed price increment.
    FIXME: tick size is updated. https://docs.upbit.com/docs/market-info-trade-price-detail

    Args:
        price (float]): 주문 가격 
        method (str, optional): 주문 가격 계산 방식. Defaults to "floor".

    Returns:
        float: 업비트 원화 마켓 주문 가격 단위로 조정된 가격 
    """
    if method == "floor":
        func = math.floor
    elif method == "round":
        func = round 
    else:
        func = math.ceil 

    if price >= 2000000:
        tick_size = func(price / 1000) * 1000
    elif price >= 1000000:
        tick_size = func(price / 500) * 500
    elif price >= 500000:
        tick_size = func(price / 100) * 100
    elif price >= 100000:
        tick_size = func(price / 50) * 50
    elif price >= 10000:
        tick_size = func(price / 10) * 10
    elif price >= 1000:
        tick_size = func(price / 1) * 1
    elif price >= 100:
        tick_size = func(price / 0.1) / 10
    elif price >= 10:
        tick_size = func(price / 0.01) / 100
    elif price >= 1:
        tick_size = func(price / 0.001) / 1000
    elif price >= 0.1:
        tick_size = func(price / 0.0001) / 10000
    elif price >= 0.01:
        tick_size = func(price / 0.00001) / 100000
    elif price >= 0.001:
        tick_size = func(price / 0.000001) / 1000000
    elif price >= 0.0001:
        tick_size = func(price / 0.0000001) / 10000000
    else:
        tick_size = func(price / 0.00000001) / 100000000

    return tick_size


class Upbit:
    def __init__(self, access, secret):
        self.access = access
        self.secret = secret


    def _request_headers(self, query=None):
        payload = {
            "access_key": self.access,
            "nonce": str(uuid.uuid4())
        }

        if query is not None:
            m = hashlib.sha512()
            m.update(urlencode(query, doseq=True).replace("%5B%5D=", "[]=").encode())
            query_hash = m.hexdigest()
            payload['query_hash'] = query_hash
            payload['query_hash_alg'] = "SHA512"

        #jwt_token = jwt.encode(payload, self.secret, algorithm="HS256").decode('utf-8')
        jwt_token = jwt.encode(payload, self.secret, algorithm="HS256")     # PyJWT >= 2.0
        authorization_token = 'Bearer {}'.format(jwt_token)
        headers = {"Authorization": authorization_token}
        return headers


    #--------------------------------------------------------------------------
    # 자산 
    #--------------------------------------------------------------------------
    #     전체 계좌 조회
    def get_balances(self, contain_req=False):
        """
        전체 계좌 조회
        :param contain_req: Remaining-Req 포함여부
        :return: 내가 보유한 자산 리스트
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        url = "https://api.upbit.com/v1/accounts"
        headers = self._request_headers()
        result = _send_get_request(url, headers=headers)
        if contain_req:
            return result
        else:
            return result[0]


    def get_balance(self, ticker="KRW", verbose=False, contain_req=False):
        """
        특정 코인/원화의 잔고를 조회하는 메소드
        :param ticker: 화폐를 의미하는 영문 대문자 코드
        :param verbose: False: only the balance, True: original dictionary 
        :param contain_req: Remaining-Req 포함여부
        :return: 주문가능 금액/수량 (주문 중 묶여있는 금액/수량 제외)
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        try:
            # fiat-ticker
            # KRW-BTC
            fiat = "KRW"
            if '-' in ticker:
                fiat, ticker = ticker.split('-')

            balances, req = self.get_balances(contain_req=True)

            # search the current currency
            balance = 0
            for x in balances:
                if x['currency'] == ticker and x['unit_currency'] == fiat:
                    if verbose is True:
                        balance = x 
                    else:
                        balance = float(x['balance'])
                    break

            if contain_req:
                return balance, req
            else:
                return balance
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def get_balance_t(self, ticker='KRW', contain_req=False):
        """
        특정 코인/원화의 잔고 조회(balance + locked)
        :param ticker: 화폐를 의미하는 영문 대문자 코드
        :param contain_req: Remaining-Req 포함여부
        :return: 주문가능 금액/수량 (주문 중 묶여있는 금액/수량 포함)
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        try:
            # KRW-BTC
            if '-' in ticker:
                ticker = ticker.split('-')[1]

            balances, req = self.get_balances(contain_req=True)

            balance = 0
            locked = 0
            for x in balances:
                if x['currency'] == ticker:
                    balance = float(x['balance'])
                    locked = float(x['locked'])
                    break

            if contain_req:
                return balance + locked, req
            else:
                return balance + locked
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def get_avg_buy_price(self, ticker='KRW', contain_req=False):
        """
        특정 코인/원화의 매수평균가 조회
        :param ticker: 화폐를 의미하는 영문 대문자 코드
        :param contain_req: Remaining-Req 포함여부
        :return: 매수평균가
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        try:
            # KRW-BTC
            if '-' in ticker:
                ticker = ticker.split('-')[1]

            balances, req = self.get_balances(contain_req=True)

            avg_buy_price = 0
            for x in balances:
                if x['currency'] == ticker:
                    avg_buy_price = float(x['avg_buy_price'])
                    break
            if contain_req:
                return avg_buy_price, req
            else:
                return avg_buy_price

        except Exception as x:
            print(x.__class__.__name__)
            return None

    def get_amount(self, ticker, contain_req=False):
        """
        특정 코인/원화의 매수금액 조회
        :param ticker: 화폐를 의미하는 영문 대문자 코드 (ALL 입력시 총 매수금액 조회)
        :param contain_req: Remaining-Req 포함여부
        :return: 매수금액
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        try:
            # KRW-BTC
            if '-' in ticker:
                ticker = ticker.split('-')[1]

            balances, req = self.get_balances(contain_req=True)

            amount = 0
            for x in balances:
                if x['currency'] == 'KRW':
                    continue

                avg_buy_price = float(x['avg_buy_price'])
                balance = float(x['balance'])
                locked = float(x['locked'])

                if ticker == 'ALL':
                    amount += avg_buy_price * (balance + locked)
                elif x['currency'] == ticker:
                    amount = avg_buy_price * (balance + locked)
                    break
            if contain_req:
                return amount, req
            else:
                return amount
        except Exception as x:
            print(x.__class__.__name__)
            return None

    # endregion balance


    #--------------------------------------------------------------------------
    # 주문 
    #--------------------------------------------------------------------------
    #     주문 가능 정보
    def get_chance(self, ticker, contain_req=False):
        """
        마켓별 주문 가능 정보를 확인.
        :param ticker:
        :param contain_req: Remaining-Req 포함여부
        :return: 마켓별 주문 가능 정보를 확인
        [contain_req == True 일 경우 Remaining-Req가 포함]
        """
        try:
            url = "https://api.upbit.com/v1/orders/chance"
            data = {"market": ticker}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None
    

    #    개별 주문 조회
    def get_order(self, ticker_or_uuid, state='wait', page=1, limit=100, contain_req=False):
        """
        주문 리스트 조회
        :param ticker: market
        :param state: 주문 상태(wait, watch, done, cancel) 또는 상태 리스트(["done", "cancel"] 등)
        :param kind: 주문 유형(normal, watch)
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        # TODO : states, identifiers 관련 기능 추가 필요
        try:
            p = re.compile(r"^\w+-\w+-\w+-\w+-\w+$")
            # 정확히는 입력을 대문자로 변환 후 다음 정규식을 적용해야 함
            # - r"^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$"
            is_uuid = len(p.findall(ticker_or_uuid)) > 0
            if is_uuid:
                # PR #129: /v1/order → /v1/orders/uuids (deprecated API fix)
                url = "https://api.upbit.com/v1/orders/uuids"
                data = {'uuid': ticker_or_uuid}
                headers = self._request_headers(data)
                result = _send_get_request(url, headers=headers, data=data)
            else:
                # PR #129: /v1/orders → /v1/orders/open or /v1/orders/closed (deprecated API fix)
                # PR #114: Support multiple states with 'states[]' parameter
                # state가 리스트인 경우 여러 상태 동시 조회 가능 (예: ["done", "cancel"])
                states = state if isinstance(state, list) else [state]

                # 엔드포인트 결정: cancel/done이 포함되어 있으면 closed, 아니면 open
                has_closed_state = any(s in ['cancel', 'done'] for s in states)
                has_open_state = any(s in ['wait', 'watch'] for s in states)

                if has_closed_state and has_open_state:
                    # 열림/닫힘 상태가 혼합된 경우, 개별 API 호출 후 병합 필요
                    # 현재는 간단히 /v1/orders/closed를 사용 (두 상태 모두 포함)
                    url = "https://api.upbit.com/v1/orders/closed"
                elif has_closed_state:
                    url = "https://api.upbit.com/v1/orders/closed"
                else:
                    url = "https://api.upbit.com/v1/orders/open"

                data = {
                    'market': ticker_or_uuid,
                    'page': page,
                    'limit': limit,
                    'order_by': 'desc'
                }
                # PR #114: 'states[]' 파라미터로 다중 상태 지원
                # Upbit API는 states[] 파라미터로 다중 상태를 받음
                # requests 라이브러리는 리스트를 자동으로 states[]=done&states[]=cancel로 변환
                data['states[]'] = states if len(states) > 1 else states[0]

                headers = self._request_headers(data)
                result = _send_get_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None


    def get_individual_order(self, uuid, contain_req=False):
        """
        주문 리스트 조회
        :param uuid: 주문 id
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        # TODO : states, uuids, identifiers 관련 기능 추가 필요
        try:
            # PR #129: /v1/order → /v1/orders/uuids (deprecated API fix)
            url = "https://api.upbit.com/v1/orders/uuids"
            data = {'uuid': uuid}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #    주문 취소 접수
    def cancel_order(self, uuid, contain_req=False):
        """
        주문 취소
        :param uuid: 주문 함수의 리턴 값중 uuid
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/order"
            data = {"uuid": uuid}
            headers = self._request_headers(data)
            result = _send_delete_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None


    #     주문
    def buy_limit_order(
        self,
        ticker: str,
        price: Union[float, str],
        volume: Union[float, str],
        time_in_force: str = None,
        contain_req: bool = False
    ):
        """
        지정가 매수

        Args:
            ticker: 마켓 티커 (예: "KRW-BTC")
            price: 주문 가격
            volume: 주문 수량
            time_in_force: 주문 시간 강제 (선택사항)
                - None: 기존 동작
                - "FOK": Fill Or Kill - 즉시 체결, 불완전 시 전체 취소
                - "IOC": Immediate Or Cancel - 즉시 체결, 불완분분 취소
                - "MARKET": 시장가 주문 (지정가와 시장가 혼합)
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 주문 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # 기본 지정가 매수
            >>> order = upbit.buy_limit_order("KRW-BTC", 50000000, 0.001)

            >>> # FOK 주문
            >>> order = upbit.buy_limit_order("KRW-BTC", 50000000, 0.001, time_in_force="FOK")
        """
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {
                "market": ticker,
                "side": "bid",
                "volume": str(volume),
                "price": str(price),
                "ord_type": "limit"
            }

            if time_in_force is not None:
                data["time_in_force"] = time_in_force

            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def buy_market_order(self, ticker, price, contain_req=False):
        """
        시장가 매수
        :param ticker: ticker for cryptocurrency
        :param price: KRW
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {"market": ticker,  # market ID
                    "side": "bid",  # buy
                    "price": str(price),
                    "ord_type": "price"}
            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def sell_market_order(self, ticker, volume, contain_req=False):
        """
        시장가 매도 메서드
        :param ticker: 가상화폐 티커
        :param volume: 수량
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {"market": ticker,  # ticker
                    "side": "ask",  # sell
                    "volume": str(volume),
                    "ord_type": "market"}
            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    def sell_limit_order(
        self,
        ticker: str,
        price: Union[float, str],
        volume: Union[float, str],
        time_in_force: str = None,
        contain_req: bool = False
    ):
        """
        지정가 매도

        Args:
            ticker: 마켓 티커 (예: "KRW-BTC")
            price: 주문 가격
            volume: 주문 수량
            time_in_force: 주문 시간 강제 (선택사항)
                - None: 기존 동작
                - "FOK": Fill Or Kill - 즉시 체결, 불완전 시 전체 취소
                - "IOC": Immediate Or Cancel - 즉시 체결, 불완분분 취소
                - "MARKET": 시장가 주문 (지정가와 시장가 혼합)
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 주문 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # 기본 지정가 매도
            >>> order = upbit.sell_limit_order("KRW-BTC", 50000000, 0.001)

            >>> # FOK 주문
            >>> order = upbit.sell_limit_order("KRW-BTC", 50000000, 0.001, time_in_force="FOK")
        """
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {
                "market": ticker,
                "side": "ask",
                "volume": str(volume),
                "price": str(price),
                "ord_type": "limit"
            }

            if time_in_force is not None:
                data["time_in_force"] = time_in_force

            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #    주문 생성 테스트
    def test_order(
        self,
        market: str,
        side: str,
        volume: Union[float, str],
        price: Union[float, str] = None,
        ord_type: str = "limit",
        time_in_force: str = None,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        주문 생성 테스트

        실제 주문을 생성하지 않고 주문 가능 여부만 테스트합니다.

        Args:
            market: 마켓 티커 (예: "KRW-BTC")
            side: 주문 종류 ("bid"=매수, "ask"=매도)
            volume: 주문 수량
            price: 주문 가격 (ord_type="limit"인 경우 필수)
            ord_type: 주문 타입 ("limit", "price", "market", "best")
            time_in_force: 주문 시간 강제 ("FOK", "IOC", "MARKET")
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 주문 테스트 결과
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # 지정가 매수 테스트
            >>> result = upbit.test_order("KRW-BTC", "bid", 0.001, 50000000)

            >>> # 시장가 매도 테스트
            >>> result = upbit.test_order("KRW-BTC", "ask", 0.001, ord_type="market")

        Note:
            - 실제 주문이 체결되지 않습니다
            - 주문 가능 여부만 확인합니다
        """
        try:
            url = "https://api.upbit.com/v1/orders"
            data = {
                "market": market,
                "side": side,
                "volume": str(volume),
                "ord_type": ord_type
            }

            if price is not None:
                data["price"] = str(price)

            if time_in_force is not None:
                data["time_in_force"] = time_in_force

            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #    주문 일괄 취소
    def cancel_orders_open(
        self,
        market: str,
        contain_req: bool = False
    ) -> Union[List[Dict[str, Any]], tuple]:
        """
        주문 일괄 취소

        특정 마켓의 모든 미체결 주문을 취소합니다.

        Args:
            market: 마켓 티커 (예: "KRW-BTC")
            contain_req: Remaining-Req 포함여부

        Returns:
            list 또는 tuple: 취소된 주문 정보 리스트
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # KRW-BTC의 모든 미체결 주문 취소
            >>> cancelled = upbit.cancel_orders_open("KRW-BTC")
            >>> print(f"{len(cancelled)} orders cancelled")

        Note:
            - 미체결 주문만 취소됩니다
            - 이미 체결된 주문은 취소할 수 없습니다
        """
        try:
            # 먼저 미체결 주문 조회
            url = "https://api.upbit.com/v1/orders"
            data = {"market": market, "state": "wait"}
            headers = self._request_headers(data)
            orders = _send_get_request(url, headers=headers, data=data)

            if not orders:
                return [] if not contain_req else ([], {})

            # 모든 주문 취소
            cancelled_orders = []
            for order in orders[0]:
                cancel_result = self.cancel_order(order["uuid"], contain_req=False)
                if cancel_result:
                    cancelled_orders.append(cancel_result)

            if contain_req:
                # 마지막 요청의 limit_info 반환
                return cancelled_orders, orders[1] if len(orders) > 1 else {}
            else:
                return cancelled_orders
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #    취소 후 재주문
    def cancel_and_new_order(
        self,
        uuid: str,
        new_price: Union[float, str] = None,
        new_volume: Union[float, str] = None,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        취소 후 재주문

        기존 주문을 취소하고 새로운 주문을 생성합니다.
        주의: 원자성이 보장되지 않으므로 취소 후 재주문 사이에
        다른 사용자의 주문이 체결될 수 있습니다.

        Args:
            uuid: 취소할 주문의 UUID
            new_price: 새로운 주문 가격 (None인 경우 기존 가격 유지)
            new_volume: 새로운 주문 수량 (None인 경우 기존 수량 유지)
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 새로운 주문 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # 주문 수정 (가격만 변경)
            >>> new_order = upbit.cancel_and_new_order(
            ...     uuid="xxx-yyy-zzz",
            ...     new_price=51000000
            ... )

            >>> # 주문 수정 (수량만 변경)
            >>> new_order = upbit.cancel_and_new_order(
            ...     uuid="xxx-yyy-zzz",
            ...     new_volume=0.002
            ... )

        Note:
            - 취소와 재주문은 별도의 트랜잭션으로 처리됩니다
            - 원자성이 보장되지 않으므로 주의가 필요합니다
            - 기존 주문 정보를 먼저 조회해야 합니다
        """
        try:
            # 1. 기존 주문 조회
            url = "https://api.upbit.com/v1/order"
            data = {"uuid": uuid}
            headers = self._request_headers(data)
            order_info = _send_get_request(url, headers=headers, data=data)

            if not order_info or not order_info[0]:
                raise ValueError(f"주문을 찾을 수 없습니다: {uuid}")

            order = order_info[0]

            # 2. 주문 취소
            cancel_result = self.cancel_order(uuid, contain_req=False)
            if not cancel_result:
                raise ValueError(f"주문 취소 실패: {uuid}")

            # 3. 새로운 주문 생성
            new_price = new_price if new_price is not None else order.get("price")
            new_volume = new_volume if new_volume is not None else order.get("remaining_volume")

            if order["side"] == "bid":
                new_order = self.buy_limit_order(
                    order["market"],
                    new_price,
                    new_volume,
                    contain_req=False
                )
            else:
                new_order = self.sell_limit_order(
                    order["market"],
                    new_price,
                    new_volume,
                    contain_req=False
                )

            if contain_req:
                # 취소 주문의 limit_info 반환
                return new_order, order_info[1] if len(order_info) > 1 else {}
            else:
                return new_order
        except Exception as x:
            print(x.__class__.__name__)
            return None


    #--------------------------------------------------------------------------
    # 출금
    #--------------------------------------------------------------------------
    def get_withdraw_list(self, currency: str, contain_req=False):
        """
        출금 리스트 조회
        :param currency: Currency 코드
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/withdraws"
            data = {"currency": currency}
            headers = self._request_headers(data)

            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     개별 출금 조회
    def get_individual_withdraw_order(self, uuid: str, currency: str, contain_req=False):
        """
        개별 출금 조회
        :param uuid: 출금 UUID
        :param currency: Currency 코드
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/withdraw"
            data = {"uuid": uuid, "currency": currency}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None


    #     코인 출금하기
    def withdraw_coin(
        self,
        currency: str,
        amount: Union[float, str],
        address: str,
        net_type: str,
        secondary_address: Optional[str] = None,
        transaction_type: str = "default",
        contain_req: bool = False
    ):
        """
        코인 출금

        Args:
            currency: Currency symbol (e.g., "BTC", "ETH")
            amount: 출금 수량 (float 또는 str 타입)
            address: 출금 지갑 주소
            net_type: 네트워크 타입 (필수 파라미터)
                - 예: "ETH", "TRX", "XRP" 등 (코인별로 지원하는 네트워크 상이)
                - Upbit API에서 필수로 요구하는 파라미터로, 자산 손실 방지를 위해 반드시 필요
            secondary_address: 2차 출금주소 (필요한 코인에 한해서, XRP 등)
            transaction_type: 출금 유형 (기본값: "default")
            contain_req: Remaining-Req 포함여부

        Returns:
            dict: 출금 주문 정보

        Raises:
            ValueError: 필수 파라미터 누락 시

        Examples:
            >>> upbit.withdraw_coin("BTC", 0.001, "bc1q...", "BTC")
            >>> upbit.withdraw_coin("XRP", 100, "r...", "XRP", secondary_address="123456789")

        Note:
            net_type은 Upbit API에서 필수 파라미터입니다.
            출금하려는 코인이 지원하는 네트워크 타입을 확인해야 합니다.
        """
        try:
            url = "https://api.upbit.com/v1/withdraws/coin"
            data = {
                "currency": currency,
                "amount": str(amount),
                "address": address,
                "net_type": net_type,
                "transaction_type": transaction_type
            }
            if secondary_address:
                data["secondary_address"] = secondary_address

            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None


    #     원화 출금하기
    def withdraw_cash(self, amount: str, contain_req=False):
        """
        현금 출금
        :param amount: 출금 액수
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/withdraws/krw"
            data = {"amount": amount}
            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     출금 가능 정보 조회
    def get_withdraw_chance(
        self,
        currency: str,
        amount: Union[float, str],
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        출금 가능 정보 조회

        특정 코인의 출금이 가능한지 확인하고 출금에 필요한 정보를 조회합니다.

        Args:
            currency: Currency 코드 (예: "BTC", "ETH")
            amount: 출금 수량
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 출금 가능 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> info = upbit.get_withdraw_chance("BTC", 0.01)
            >>> print(info['withdraw_available'])
            True

        Note:
            - 출금 가능 여부, 수수료, 최소/최대 출금 금액 등을 확인할 수 있습니다
        """
        try:
            url = "https://api.upbit.com/v1/orders/chance"
            data = {"market": f"KRW-{currency}", "amount": str(amount)}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     출금 허용 주소 목록 조회
    def get_withdraw_addresses(
        self,
        currency: str = None,
        contain_req: bool = False
    ) -> Union[List[Dict[str, Any]], tuple]:
        """
        출금 허용 주소 목록 조회

        등록된 출금 허용 주소(화이트리스트) 목록을 조회합니다.
        특정 코인의 주소만 조회하거나 전체 목록을 조회할 수 있습니다.

        Args:
            currency: Currency 코드 (선택사항, None인 경우 전체 조회)
            contain_req: Remaining-Req 포함여부

        Returns:
            list 또는 tuple: 출금 허용 주소 정보 리스트
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> # 전체 출금 허용 주소 조회
            >>> addresses = upbit.get_withdraw_addresses()

            >>> # 특정 코인의 출금 허용 주소 조회
            >>> btc_addresses = upbit.get_withdraw_addresses("BTC")
            >>> for addr in btc_addresses:
            ...     print(f"{addr['address']} ({addr['currency']})")

        Note:
            - 출금 허용 주소는 화이트리스트로 등록된 주소입니다
            - 출금 허용 주소로만 출금이 가능합니다
        """
        try:
            url = "https://api.upbit.com/v1/withdraws/whitelist_addresses"
            data = {}
            if currency is not None:
                data["currency"] = currency

            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0] if result else []
        except Exception as x:
            print(x.__class__.__name__)
            return None


    #--------------------------------------------------------------------------
    # 입금
    #--------------------------------------------------------------------------
    #     입금 리스트 조회 
    def get_deposit_list(self, currency: str, contain_req=False):
        """
        입금 리스트 조회
        :currency: Currency 코드
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/deposits"
            data = {"currency": currency}
            headers = self._request_headers(data)

            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None
            
    #     개별 입금 조회
    def get_individual_deposit_order(self, uuid: str, currency: str, contain_req=False):
        """
        개별 입금 조회
        :param uuid: 입금 UUID
        :param currency: Currency 코드
        :param contain_req: Remaining-Req 포함여부
        :return:
        """
        try:
            url = "https://api.upbit.com/v1/deposit"
            data = {"uuid": uuid, "currency": currency}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)
            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     입금 가능 정보 조회
    def get_deposit_chance(
        self,
        currency: str,
        amount: Union[float, str] = None,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        입금 가능 정보 조회

        특정 코인의 입금이 가능한지 확인하고 입금에 필요한 정보를 조회합니다.

        Args:
            currency: Currency 코드 (예: "BTC", "ETH")
            amount: 입금 수량 (선택사항, 일부 코인의 경우 필수)
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 입금 가능 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> upbit.get_deposit_chance("BTC")
            {'currency': 'BTC', 'deposit_wallet_address': '...', ...}

            >>> upbit.get_deposit_chance("BTC", 0.01)
        """
        try:
            url = "https://api.upbit.com/v1/orders/chance"
            data = {"market": f"KRW-{currency}"}

            if amount is not None:
                data["amount"] = str(amount)

            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     입금 주소 생성 요청
    def create_deposit_address(
        self,
        currency: str,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        입금 주소 생성 요청

        입금 주소가 없는 코인의 경우 입금 주소 생성을 요청합니다.
        생성된 입금 주소는 해당 코인의 첫 입금 요청 시 자동으로 생성되므로,
        별도의 생성 요청이 필요 없는 경우도 있습니다.

        Args:
            currency: Currency 코드 (예: "BTC", "ETH")
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 생성된 입금 주소 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> result = upbit.create_deposit_address("BTC")
            >>> print(result['deposit_address'])
            '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'

        Note:
            - 일부 코인은 입금 주소가 자동으로 생성되므로 별도 요청이 필요 없습니다
            - 2차 보안 비밀번호가 설정된 경우 필요할 수 있습니다
        """
        try:
            url = "https://api.upbit.com/v1/deposits/generate_coin_address"
            data = {"currency": currency}
            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     전체 입금 주소 조회
    def get_deposit_addresses(
        self,
        contain_req: bool = False
    ) -> Union[List[Dict[str, Any]], tuple]:
        """
        전체 입금 주소 목록 조회

        모든 코인의 입금 주소 정보를 조회합니다.

        Args:
            contain_req: Remaining-Req 포함여부

        Returns:
            list 또는 tuple: 입금 주소 정보 리스트
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> addresses = upbit.get_deposit_addresses()
            >>> for addr in addresses:
            ...     print(f"{addr['currency']}: {addr['deposit_address']}")

        Note:
            - 입금 주소가 없는 코인은 포함되지 않을 수 있습니다
        """
        try:
            url = "https://api.upbit.com/v1/deposits/coin_addresses"
            headers = self._request_headers()
            result = _send_get_request(url, headers=headers)

            if contain_req:
                return result
            else:
                return result[0] if result else []
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     개별 입금 주소 조회
    def get_deposit_address(
        self,
        currency: str,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        개별 입금 주소 조회

        특정 코인의 입금 주소 정보를 조회합니다.

        Args:
            currency: Currency 코드 (예: "BTC", "ETH")
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 입금 주소 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> info = upbit.get_deposit_address("BTC")
            >>> print(info['deposit_address'])
            '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
            >>> print(info['secondary_address'])
            '123456'

        Note:
            - 일부 코인(XRP 등)은 2차 주소(secondary_address)가 필요할 수 있습니다
        """
        try:
            url = "https://api.upbit.com/v1/deposits/coin_address"
            data = {"currency": currency}
            headers = self._request_headers(data)
            result = _send_get_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     원화 입금 계좌 정보 조회
    def get_krw_deposit_info(
        self,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        원화 입금 계좌 정보 조회

        업비트에서 원화 입금을 위한 은행 계좌 정보를 조회합니다.

        Args:
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 입금 계좌 정보
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> info = upbit.get_krw_deposit_info()
            >>> print(info['bank'])
            'Shinhan Bank'
            >>> print(info['account_number'])
            '123-456-789012'

        Note:
            - 입금 계좌는 사용자별로 할당됩니다
            - 입금자명과 일치해야 입금이 처리됩니다
        """
        try:
            url = "https://api.upbit.com/v1/deposits/krw"
            headers = self._request_headers()
            result = _send_get_request(url, headers=headers)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     원화 입금하기 (기존 주석 유지)
    #     전체 입금 주소 조회
    #     개별 입금 주소 조회


    #--------------------------------------------------------------------------
    # 서비스 정보 
    #--------------------------------------------------------------------------
    #     입출금 현황 
    def get_deposit_withdraw_status(self, contain_req=False):
        url = "https://api.upbit.com/v1/status/wallet"
        headers = self._request_headers()
        result = _send_get_request(url, headers=headers)
        if contain_req:
            return result
        else:
            return result[0]


    #     API키 리스트 조회
    def get_api_key_list(self, contain_req=False):
        url = "https://api.upbit.com/v1/api_keys"
        headers = self._request_headers()
        result = _send_get_request(url, headers=headers)
        if contain_req:
            return result
        else:
            return result[0]


    #--------------------------------------------------------------------------
    # 트래블룰 (Travel Rule)
    #--------------------------------------------------------------------------
    #     트래블룰 지원 거래소 목록 조회
    def get_travel_rule_vasps(
        self,
        contain_req: bool = False
    ) -> Union[List[Dict[str, Any]], tuple]:
        """
        트래블룰 지원 거래소 목록 조회

        여러 금융정보기관의 자금세탁방지 업무 협조를 위한
        트래블룰(Travel Rule) 지원 거래소 목록을 조회합니다.

        Args:
            contain_req: Remaining-Req 포함여부

        Returns:
            list 또는 tuple: 트래블룰 지원 거래소 정보 리스트
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> vasps = upbit.get_travel_rule_vasps()
            >>> for vasp in vasps:
            ...     print(f"{vasp['name']}: {vasp['country']}")

        Note:
            - 트래블룰은 자금세탁방지를 위한 국제 규정입니다
            - 입금 시 거래소 정보가 필요할 수 있습니다
        """
        try:
            url = "https://api.upbit.com/v1/travel_rule/vasps"
            headers = self._request_headers()
            result = _send_get_request(url, headers=headers)

            if contain_req:
                return result
            else:
                return result[0] if result else []
        except Exception as x:
            print(x.__class__.__name__)
            return None

    #     입금 UUID로 트래블룰 검증
    def verify_travel_rule_by_uuid(
        self,
        deposit_uuid: str,
        vasp_name: str,
        vasp_address: str,
        contain_req: bool = False
    ) -> Union[Dict[str, Any], tuple]:
        """
        입금 UUID로 트래블룰 검증

        특정 입금 요청에 대한 트래블룰 정보를 검증하고 등록합니다.

        Args:
            deposit_uuid: 입금 UUID
            vasp_name: VASP (가상자산거래소사업자) 이름
            vasp_address: VASP 주소
            contain_req: Remaining-Req 포함여부

        Returns:
            dict 또는 tuple: 트래블룰 검증 결과
            contain_req=True인 경우 (result, req_limit_info) 튜플 반환

        Examples:
            >>> result = upbit.verify_travel_rule_by_uuid(
            ...     deposit_uuid="xxx-yyy-zzz",
            ...     vasp_name="Binance",
            ...     vasp_address="MZPaXv4P6o..."  # VASP 주소
            ... )
            >>> print(result['status'])

        Note:
            - 트래블룰 검증은 입금 전에 수행해야 합니다
            - VASP 정보는 정확해야 합니다
        """
        try:
            url = "https://api.upbit.com/v1/travel_rule/verify"
            data = {
                "deposit_uuid": deposit_uuid,
                "vasp_name": vasp_name,
                "vasp_address": vasp_address
            }
            headers = self._request_headers(data)
            result = _send_post_request(url, headers=headers, data=data)

            if contain_req:
                return result
            else:
                return result[0]
        except Exception as x:
            print(x.__class__.__name__)
            return None


if __name__ == "__main__":
    import pprint

    #-------------------------------------------------------------------------
    # api key
    #-------------------------------------------------------------------------
    with open("../upbit.key") as f:
        lines = f.readlines()
        access = lines[0].strip()
        secret = lines[1].strip()

    upbit = Upbit(access, secret)
    #print(upbit.get_balances())
    print(upbit.get_balance("KRW-BTC", verbose=True))

    # order 
    resp = upbit.buy_limit_order("KRW-XRP", 500, 10)
    print(resp)


    #-------------------------------------------------------------------------
    # 자산 
    #     전체 계좌 조회 
    #balance = upbit.get_balances()
    #pprint.pprint(balance)

    #balances = upbit.get_order("KRW-XRP")
    #pprint.pprint(balances)

    # order = upbit.get_order('50e184b3-9b4f-4bb0-9c03-30318e3ff10a')
    # print(order)
    # # 원화 잔고 조회
    # print(upbit.get_balance(ticker="KRW"))          # 보유 KRW
    # print(upbit.get_amount('ALL'))                  # 총매수금액
    # print(upbit.get_balance(ticker="KRW-BTC"))      # 비트코인 보유수량
    # print(upbit.get_balance(ticker="KRW-XRP"))      # 리플 보유수량

    #-------------------------------------------------------------------------
    # 주문
    #     주문 가능 정보 
    #pprint.pprint(upbit.get_chance('KRW-BTC'))

    #     개별 주문 조회
    #print(upbit.get_order('KRW-BTC'))

    # 매도
    # print(upbit.sell_limit_order("KRW-XRP", 1000, 20))

    # 매수
    # print(upbit.buy_limit_order("KRW-XRP", 200, 20))

    # 주문 취소
    # print(upbit.cancel_order('82e211da-21f6-4355-9d76-83e7248e2c0c'))

    # 시장가 주문 테스트
    # upbit.buy_market_order("KRW-XRP", 10000)

    # 시장가 매도 테스트
    # upbit.sell_market_order("KRW-XRP", 36)


    #-------------------------------------------------------------------------
    # 서비스 정보
    #     입출금 현황
    #resp = upbit.get_deposit_withdraw_status()
    #pprint.pprint(resp)

    #     API키 리스트 조회
    #resp = upbit.get_api_key_list()
    #print(resp)