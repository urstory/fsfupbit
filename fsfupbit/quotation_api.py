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
pyupbit.quotation_api

This module provides quatation api of the Upbit API.
"""

import datetime
import pandas as pd
import time
from typing import List, Dict, Optional, Union
from fsfupbit.request_api import _call_public_api


def get_tickers(fiat="", is_details=False, limit_info=False, verbose=False):
    """업비트 티커 조회

    Args:
        fiat (str, optional): Fiat (KRW, BTC, USDT). Defaults to empty string.
        limit_info (bool, optional): True: 요청 수 제한 정보 리턴, False: 요청 수 제한 정보 리턴 받지 않음. Defaults to False.

    Returns:
        tuple/list: limit_info가 True이면 튜플, False이면 리스트 객체
    """  # pylint: disable=line-too-long # noqa: E501

    url = "https://api.upbit.com/v1/market/all"
    detail = "true" if is_details else "false"
    markets, req_limit_info = _call_public_api(url, isDetails=detail)

    if verbose or is_details:
        tickers = [x for x in markets if x['market'].startswith(fiat)]
    else:
        tickers = [
            x['market'] for x in markets if x['market'].startswith(fiat)
        ]

    if limit_info:
        return tickers, req_limit_info
    else:
        return tickers


def get_url_ohlcv(interval):
    """ohlcv 요청을 위한 url을 리턴하는 함수

    Args:
        interval (str): 캔들 간격
            - 초: "seconds/1", "seconds/3", "seconds/5", "seconds/10", "seconds/15", "seconds/30", "seconds/60", "seconds/240"
            - 분: "minute1", "minute3", "minute5", "minute10", "minute15", "minute30", "minute60", "minute240"
            - 일: "day", "days"
            - 주: "week", "weeks"
            - 월: "month", "months"
            - 년: "year", "years"

    Returns:
        str: upbit api url
    """

    if interval in ["day", "days"]:
        url = "https://api.upbit.com/v1/candles/days"
    elif interval in ["minute1", "minutes1"]:
        url = "https://api.upbit.com/v1/candles/minutes/1"
    elif interval in ["minute3", "minutes3"]:
        url = "https://api.upbit.com/v1/candles/minutes/3"
    elif interval in ["minute5", "minutes5"]:
        url = "https://api.upbit.com/v1/candles/minutes/5"
    elif interval in ["minute10", "minutes10"]:
        url = "https://api.upbit.com/v1/candles/minutes/10"
    elif interval in ["minute15", "minutes15"]:
        url = "https://api.upbit.com/v1/candles/minutes/15"
    elif interval in ["minute30", "minutes30"]:
        url = "https://api.upbit.com/v1/candles/minutes/30"
    elif interval in ["minute60", "minutes60"]:
        url = "https://api.upbit.com/v1/candles/minutes/60"
    elif interval in ["minute240", "minutes240"]:
        url = "https://api.upbit.com/v1/candles/minutes/240"
    elif interval in ["week",  "weeks"]:
        url = "https://api.upbit.com/v1/candles/weeks"
    elif interval in ["month", "months"]:
        url = "https://api.upbit.com/v1/candles/months"
    elif interval in ["year", "years"]:
        url = "https://api.upbit.com/v1/candles/years"
    elif interval.startswith("seconds/"):
        # 초 캔들 (예: "seconds/1", "seconds/3", etc.)
        unit = interval.split("/")[1]
        url = f"https://api.upbit.com/v1/candles/seconds/{unit}"
    else:
        url = "https://api.upbit.com/v1/candles/days"

    return url


def get_ohlcv(
    ticker: str = "KRW-BTC",
    interval: str = "day",
    count: int = 200,
    to: Union[str, datetime.datetime] = None,
    period: float = 0.1,
    converting_price_unit: str = None
):
    """
    캔들 데이터 조회

    Args:
        ticker: 마켓 티커 (기본값: "KRW-BTC")
        interval: 캔들 간격
            - 초: "seconds/1", "seconds/3", "seconds/5", "seconds/10", "seconds/15", "seconds/30", "seconds/60", "seconds/240"
            - 분: "minute1", "minute3", "minute5", "minute10", "minute15", "minute30", "minute60", "minute240"
            - 일: "day", "days"
            - 주: "week", "weeks"
            - 월: "month", "months"
            - 년: "year", "years"
        count: 조회 갯수 (기본값: 200)
        to: 조회 마지막 시점 (datetime 또는 str)
        period: 조회 시간 간격 (초 단위, 기본값: 0.1)
        converting_price_unit: 파라미터 (선택사항, 일봉만 지원)
            - KRW 마켓이 아닌 마켓의 일봉을 원화로 환산하여 조회
            - 예: "KRW", "BTC"

    Returns:
        DataFrame: OHLCV 데이터
        - open: 시가
        - high: 고가
        - low: 저가
        - close: 종가
        - volume: 거래량
        - value: 거래대금

    Examples:
        >>> # 기본 일봉 조회
        >>> df = get_ohlcv("KRW-BTC")

        >>> # 초봉 조회
        >>> df = get_ohlcv("KRW-BTC", interval="seconds/30")

        >>> # 연봉 조회
        >>> df = get_ohlcv("KRW-BTC", interval="years")

        >>> # BTC-ETH 일봉을 BTC 기준으로 환산 조회
        >>> df = get_ohlcv("BTC-ETH", interval="day", converting_price_unit="BTC")

    Note:
        - converting_price_unit은 일봉에서만 사용 가능합니다
        - 조회 데이터가 200개 이상인 경우 자동으로 여러 번 호출됩니다
    """
    MAX_CALL_COUNT = 200
    try:
        url = get_url_ohlcv(interval=interval)

        if to is None:
            to = datetime.datetime.now(datetime.timezone.utc)
            to = to.replace(tzinfo=None)
        elif isinstance(to, str):
            to = pd.to_datetime(to).to_pydatetime()
        elif isinstance(to, pd._libs.tslibs.timestamps.Timestamp):
            to = to.to_pydatetime()

        #to = to.astimezone(datetime.timezone.utc)

        dfs = []
        count = max(count, 1)
        for pos in range(count, 0, -200):
            query_count = min(MAX_CALL_COUNT, pos)

            to = to.strftime("%Y-%m-%d %H:%M:%S")

            query_params = {"market": ticker, "count": query_count, "to": to}
            if converting_price_unit is not None:
                query_params["convertingPriceUnit"] = converting_price_unit

            contents, _ = _call_public_api(url, **query_params)

            dt_list = []
            for x in contents:
                dt = datetime.datetime.strptime(
                    x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S")
                #dt_list.append(dt.astimezone())
                dt_list.append(dt)

            df = pd.DataFrame(contents,
                              columns=[
                                  'opening_price',
                                  'high_price',
                                  'low_price',
                                  'trade_price',
                                  'candle_acc_trade_volume',
                                  'candle_acc_trade_price'],
                              index=dt_list)
            df = df.sort_index()
            if df.shape[0] == 0:
                break
            dfs += [df]

            to = datetime.datetime.strptime(
                contents[-1]['candle_date_time_utc'], "%Y-%m-%dT%H:%M:%S")

            if pos > 200:
                time.sleep(period)

        df = pd.concat(dfs).sort_index()
        df = df.rename(columns={"opening_price": "open",
                                "high_price": "high",
                                "low_price": "low",
                                "trade_price": "close",
                                "candle_acc_trade_volume": "volume",
                                "candle_acc_trade_price": "value"})
        return df
    except Exception:
        return None


def get_ohlcv_from(ticker="KRW-BTC", interval="day", fromDatetime=None,
                   to=None, period=0.1):
    MAX_CALL_COUNT = 200
    try:
        url = get_url_ohlcv(interval=interval)

        if fromDatetime is None:
            fromDatetime = datetime.datetime(2000, 1, 1, 0, 0, 0)
        elif isinstance(fromDatetime, str):
            fromDatetime = pd.to_datetime(fromDatetime).to_pydatetime()
        elif isinstance(fromDatetime, pd._libs.tslibs.timestamps.Timestamp):
            fromDatetime = fromDatetime.to_pydatetime()
        fromDatetime = fromDatetime.astimezone(datetime.timezone.utc)

        if to is None:
            to = datetime.datetime.now()
        elif isinstance(to, str):
            to = pd.to_datetime(to).to_pydatetime()
        elif isinstance(to, pd._libs.tslibs.timestamps.Timestamp):
            to = to.to_pydatetime()
        to = to.astimezone(datetime.timezone.utc)

        dfs = []
        while to > fromDatetime:
            query_count = MAX_CALL_COUNT

            to = to.strftime("%Y-%m-%d %H:%M:%S")

            contents, _ = _call_public_api(
                url, market=ticker, count=query_count, to=to)

            dt_list = []
            for x in contents:
                dt = datetime.datetime.strptime(
                    x['candle_date_time_kst'], "%Y-%m-%dT%H:%M:%S")
                dt_list.append(dt.astimezone())
            # set timezone for time comparison
            # timezone will be removed before DataFrame returned

            df = pd.DataFrame(contents,
                              columns=[
                                  'opening_price',
                                  'high_price',
                                  'low_price',
                                  'trade_price',
                                  'candle_acc_trade_volume',
                                  'candle_acc_trade_price'],
                              index=dt_list)
            df = df.sort_index()
            if df.shape[0] == 0:
                break
            dfs += [df]

            to = datetime.datetime.strptime(
                contents[-1]['candle_date_time_utc'], "%Y-%m-%dT%H:%M:%S")
            to = to.replace(tzinfo=datetime.timezone.utc)
            # to compare fromTs and to, set tzinfo
            # timezone will be removed before DataFrame returned

            if to > fromDatetime:
                time.sleep(period)

        df = pd.concat(dfs).sort_index()
        df = df[df.index >= fromDatetime]
        df.index = df.index.tz_localize(None)
        # remove timezone, return DataFrame whose index has no timezone
        #   like get_ohlcv method
        df = df.rename(columns={"opening_price": "open",
                                "high_price": "high",
                                "low_price": "low",
                                "trade_price": "close",
                                "candle_acc_trade_volume": "volume",
                                "candle_acc_trade_price": "value"})
        return df
    except Exception:
        return None


def get_daily_ohlcv_from_base(ticker="KRW-BTC", base=0):
    try:
        df = get_ohlcv(ticker, interval="minute60")
        df = df.resample('24H', base=base).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
        return df
    except Exception:
        return None


def _get_current_price(ticker="KRW-BTC", limit_info=False, verbose=False):    
    url = "https://api.upbit.com/v1/ticker"
    return _call_public_api(url, markets=ticker)    
    
def get_current_price(ticker="KRW-BTC", limit_info=False, verbose=False):
    """현재가 정보 조회

    Args:
        ticker (str/list, optional): 단일 티커 또는 티커 리스트 Defaults to "KRW-BTC".
        limit_info (bool, optional): True: 요청 제한 정보 리턴. Defaults to False.
        verbose (bool, optional): True: 원본 API 파라미터 리턴. Defaults to False.

    Returns:
        [type]: [description]
    """
    if isinstance(ticker, str) or (isinstance(ticker, list) and len(ticker) == 1):
        price, req_limit_info = _get_current_price(ticker, limit_info, verbose)        
        if verbose is False:
            price = price[0]['trade_price']
        
    else:
        slice_size = 200
        price = []
        for idx in range(0, len(ticker), slice_size):
            ticker_sliced = ticker[idx: idx+slice_size]
            price_sliced, req_limit_info = _get_current_price(ticker_sliced, limit_info, verbose)        
            price += price_sliced

        if verbose is False:
            price = {x['market']: x['trade_price'] for x in price}
    
    if limit_info:
        return price, req_limit_info
    else:
        return price  


def get_orderbook_supported_levels(markets: List[str]) -> List[Dict]:
    """
    종목별 지원 호가 모아보기 단위 조회

    Upbit API의 호가 모아보기 기능에서 지원하는 단위를 조회합니다.
    KRW 마켓은 다양한 단위를 지원하며, 다른 마켓은 기본 단위(0)만 지원합니다.

    Args:
        markets: 마켓 코드 리스트 (예: ["KRW-BTC", "KRW-ETH", "BTC-ETH"])

    Returns:
        종목별 지원 단위 정보 리스트
        [
            {"market": "KRW-BTC", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "KRW-ETH", "supported_levels": [0, 1, 2, 3, 4, 5]},
            {"market": "BTC-ETH", "supported_levels": [0]}  # KRW 외에는 0만
        ]

    Raises:
        ValueError: markets 파라미터가 비어있거나 유효하지 않은 경우

    Examples:
        >>> levels = get_orderbook_supported_levels(["KRW-BTC"])
        >>> print(levels[0]["supported_levels"])
        [0, 1, 2, 3, 4, 5]

        >>> levels = get_orderbook_supported_levels(["KRW-BTC", "KRW-ETH"])
        >>> for level_info in levels:
        ...     print(f"{level_info['market']}: {level_info['supported_levels']}")
    """
    if not markets or not isinstance(markets, list):
        raise ValueError("markets 파라미터는 비어있지 않은 리스트여야 합니다")

    # API 호출
    url = "https://api.upbit.com/v1/orderbook/supported_levels"

    # markets 파라미터를 쿼리 스트링으로 변환
    # Upbit API는 여러 마켓을 쿼리 파라미터로 전달
    query_params = {"market": markets}

    try:
        response, _ = _call_public_api(url, **query_params)
        return response
    except Exception as e:
        raise ValueError(f"호가 모아보기 단위 조회 실패: {e}")


def get_orderbook(
    ticker: Union[str, List[str]] = "KRW-BTC",
    level: Optional[float] = None,
    limit_info: bool = False
):
    """호가 정보 조회 (호가 모아보기 지원)

    Args:
        ticker: 티커 또는 티커 리스트 (기본값: "KRW-BTC")
        level: 호가 모아보기 단위 (KRW 마켓만 지원, 선택사항)
            - None: 기본 호가 단위
            - 0: 기본 호가 단위
            - 양수: 지정된 단위로 호가 모아보기 (예: 10000 = 1만원 단위)
            - 지원하는 단위는 get_orderbook_supported_levels()로 확인 가능
        limit_info: 요청 수 제한 정보 포함 여부 (기본값: False)

    Returns:
        list 또는 dict: 호가 정보
        단일 티커 조회 시 dict, 복수 티커 조회 시 list 반환

        단일 티커 예시:
        {
            'market': 'KRW-BTC',
            'timestamp': 1532118943687,
            'total_ask_size': 17.08116346,
            'total_bid_size': 3.07150192,
            'orderbook_units': [
                {'ask_price': 8390000.0, 'bid_price': 8389000.0, ...},
                ...
            ]
        }

    Examples:
        >>> # 기본 호가 조회
        >>> ob = get_orderbook("KRW-BTC")
        >>> print(ob['orderbook_units'][0])

        >>> # 1만원 단위 호가 모아보기 (KRW 마켓만 지원)
        >>> ob = get_orderbook("KRW-BTC", level=10000)

        >>> # 여러 종목 조회
        >>> obs = get_orderbook(["KRW-BTC", "KRW-ETH"])
        >>> for ob in obs:
        ...     print(ob['market'], ob['total_ask_size'])

    Note:
        - level 파라미터는 KRW 마켓에서만 사용 가능합니다
        - level 값이 유효하지 않은 경우 API에서 에러를 반환할 수 있습니다
        - 호가 모아보기 단위는 get_orderbook_supported_levels()로 먼저 확인을 권장합니다
    """  # pylint: disable=line-too-long # noqa: E501

    url = "https://api.upbit.com/v1/orderbook"

    # level 파라미터가 있는 경우 쿼리 파라미터에 추가
    if level is not None:
        orderbook, req_limit_info = _call_public_api(
            url, markets=ticker, level=str(level)
        )
    else:
        orderbook, req_limit_info = _call_public_api(url, markets=ticker)

    if isinstance(ticker, str) or \
            (isinstance(ticker, list) and len(ticker) == 1):
        orderbook = orderbook[0]

    if limit_info:
        return orderbook, req_limit_info
    else:
        return orderbook


if __name__ == "__main__":
    # 모든 티커 목록 조회
    # all_tickers = get_tickers()
    # print(len(all_tickers))

    # all_tickers = get_tickers(fiat="KRW")
    # print(len(all_tickers))

    # all_tickers = get_tickers(fiat="KRW", verbose=True)
    # print(all_tickers)

    #  krw_tickers = get_tickers(fiat="KRW")
    #  print(krw_tickers, len(krw_tickers))

    # btc_tickers = get_tickers(fiat="BTC")
    # print(btc_tickers, len(btc_tickers))

    # usdt_tickers = get_tickers(fiat="USDT")
    # print(usdt_tickers, len(usdt_tickers))

    # 요청 수 제한 얻기
    # all_tickers, limit_info = get_tickers(limit_info=True)
    # print(limit_info)

    # print(get_tickers(fiat="KRW"))
    # print(get_tickers(fiat="BTC"))
    # print(get_tickers(fiat="USDT"))

    # ------------------------------------------------------
    # print(get_ohlcv("KRW-BTC"))
    # print(get_ohlcv("KRW-BTC", interval="day", count=5))
    # print(get_ohlcv("KRW-BTC", interval="day", to="2020-01-01 00:00:00"))
    df = get_ohlcv('KRW-XRP', interval='minute5', count=1000)
    print(type(df.index))
    print(df)

    # to = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
    # df = get_ohlcv(ticker="KRW-BTC", interval="day", to=to)
    # print(df)

    # string Test
    # df = get_ohlcv("KRW-BTC", interval="minute1", to="2018-08-25 12:00:00")
    # print(df)

    # time stamp Test
    # df = get_ohlcv("KRW-BTC", interval="minute1")
    # print(df)
    # df = get_ohlcv("KRW-BTC", interval="minute1", count=401)
    # df = get_ohlcv("KRW-BTC", interval="minute1", count=400)
    # df = get_ohlcv("KRW-BTC", interval="minute1", count=4)
    # print(len(df))
    # print(get_ohlcv("KRW-BTC", interval="minute1", to=df.index[0]))

    # # DateTime Test
    # now = datetime.datetime.now() - datetime.timedelta(days=1000)
    # print(get_ohlcv("KRW-BTC", interval="minute1", to=now))
    # print(get_ohlcv("KRW-BTC", interval="minute1", to="2018-01-01 12:00:00"))
    # print(get_ohlcv("KRW-BTC", interval="minute3"))
    # print(get_ohlcv("KRW-BTC", interval="minute5"))
    # print(get_ohlcv("KRW-BTC", interval="minute10"))
    # print(get_ohlcv("KRW-BTC", interval="minute15"))
    # print(get_ohlcv("KRW-BTC", interval="minute30"))
    # print(get_ohlcv("KRW-BTC", interval="minute60"))
    # print(get_ohlcv("KRW-BTC", interval="minute240"))
    # print(get_ohlcv("KRW-BTC", interval="week"))
    # print(get_daily_ohlcv_from_base("KRW-BTC", base=9))
    # print(get_ohlcv("KRW-BTC", interval="day", count=5))

    tickers = get_tickers()
    print(len(tickers))
    prices1 = get_current_price(tickers)
    print(prices1)
    # krw_tickers1 = krw_tickers[:100]
    # krw_tickers2 = krw_tickers[100:]

    # prices1 = get_current_price(krw_tickers1)
    # prices2 = get_current_price(krw_tickers2)

    # print(prices1)
    # print(prices2)

    # price = get_current_price("KRW-BTC")
    # print(price)
    # price, limit = get_current_price("KRW-BTC", limit_info=True)
    # print(price, limit)
    # price = get_current_price(["KRW-BTC", "KRW-XRP"])
    # print(price)
    # price, limit = get_current_price(["KRW-BTC", "KRW-XRP"], limit_info=True)
    # print(price, limit)
    # price = get_current_price("KRW-BTC", verbose=True)
    # print(price)
    # price = get_current_price(["KRW-BTC", "KRW-XRP"], verbose=True)
    # print(price)

    # print(get_current_price(["KRW-BTC", "KRW-XRP"]))

    # orderbook
    # orderbook = get_orderbook(ticker="KRW-BTC")
    # print(orderbook)

    # orderbook, req_limit_info = get_orderbook(
    #     ticker="KRW-BTC", limit_info=True)
    # print(orderbook, req_limit_info)

    # orderbook = get_orderbook(ticker=["KRW-BTC", "KRW-XRP"])
    # for ob in orderbook:
    #    print(ob)
