#
# fsfupbit - Enhanced Python wrapper for Upbit API
#
# Based on pyupbit (https://github.com/sharebook-kr/pyupbit)
# Original Copyright (c) 2021 sharebook-kr
# Modifications Copyright (c) 2025 Full Stack Research Lab (풀스택연구소)
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for the full text of the license.
#

"""
fsfupbit - Upbit API Wrapper Library

업비트(Upbit) 거래소의 API를 쉽게 사용할 수 있는 Python 라이브러리입니다.
pyupbit를 기반으로 하여 최신 API 기능을 추가하고 코드 품질을 개선하였습니다.
"""

__version__ = "1.0.0"
__author__ = "Full Stack Research Lab (풀스택연구소)"

from .quotation_api import (
    get_tickers,
    get_ohlcv,
    get_ohlcv_from,
    get_current_price,
    get_orderbook,
    get_orderbook_supported_levels,
)

from .exchange_api import Upbit

from .websocket_api import WebSocketManager, WebSocketClient, PrivateWebSocketManager

__all__ = [
    # 시세 조회
    "get_tickers",
    "get_ohlcv",
    "get_ohlcv_from",
    "get_current_price",
    "get_orderbook",
    "get_orderbook_supported_levels",
    # 거래/자산 관리
    "Upbit",
    # WebSocket
    "WebSocketManager",
    "WebSocketClient",
    "PrivateWebSocketManager",
]
