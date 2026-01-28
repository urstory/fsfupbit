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

import websockets
import asyncio
import json
import uuid
import multiprocessing as mp
import jwt
from typing import Optional, List, Dict, Any

class WebSocketClient:
    def __init__(self, type: str, codes: list, queue: mp.Queue):
        self.type = type
        self.codes = codes
        self.queue = queue
        self.run()

    async def connect_socket(self):
        uri = "wss://api.upbit.com/websocket/v1"
        async for websocket in websockets.connect(uri, ping_interval=60):
            try:
                data = [{
                    "ticket": str(uuid.uuid4())[:6]
                }, {
                    "type": self.type,
                    "codes": self.codes,
                    "isOnlyRealtime": True
                }]
                await websocket.send(json.dumps(data))

                while True:
                    recv_data = await websocket.recv()
                    recv_data = recv_data.decode('utf8')
                    self.queue.put(json.loads(recv_data))
            except websockets.ConnectionClosed:
                self.queue.put('ConnectionClosedError')
                continue

    def run(self):
        asyncio.run(self.connect_socket())


class WebSocketManager(mp.Process):
    """웹소켓을 관리하는 클래스

        사용 예제:

            >> wm = WebSocketManager("ticker", ["BTC_KRW"])
            >> for i in range(3):
                data = wm.get()
                print(data)
            >> wm.terminate()

        주의 :

           재귀적인 호출을 위해 다음의 guard를 반드시 추가해야 한다.
           >> if __name__ == "__main__"

    """
    def __init__(self, type: str, codes: list, qsize: int = 1000):
        """웹소켓을 컨트롤하는 클래스의 생성자

        Args:
            type   (str           ): 구독 메시지 종류 (ticker/trade/orderbook)
            codes  (list          ): 구독할 암호 화폐의 리스트 [BTC_KRW, ETH_KRW, …]
            qsize  (int , optional): 메시지를 저장할 Queue의 크기
        """
        self.__q = mp.Queue(qsize)
        self.alive = False

        self.type = type
        self.codes = codes

        super().__init__()

    async def __connect_socket(self):
        uri = "wss://api.upbit.com/websocket/v1"
        async for websocket in websockets.connect(uri, ping_interval=60):
            try:
                data = [{
                    "ticket": str(uuid.uuid4())[:6]
                }, {
                    "type": self.type,
                    "codes": self.codes,
                    "isOnlyRealtime": True
                }]
                await websocket.send(json.dumps(data))

                while self.alive:
                    recv_data = await websocket.recv()
                    recv_data = recv_data.decode('utf8')
                    self.__q.put(json.loads(recv_data))
            except websockets.ConnectionClosed:
                self.__q.put('ConnectionClosedError')
                continue

    def run(self):
        #self.__aloop = asyncio.get_event_loop()
        #self.__aloop.run_until_complete(self.__connect_socket())
        asyncio.run(self.__connect_socket())

    def get(self):
        if self.alive is False:
            self.alive = True
            self.start()
        return self.__q.get()

    def terminate(self):
        self.alive = False
        super().terminate()


if __name__ == "__main__":
    wm = WebSocketManager("ticker", ["KRW-BTC", ])
    while True:
        data = wm.get()
        print(data)
    wm.terminate()


class PrivateWebSocketManager(mp.Process):
    """개인용 WebSocket 관리자

    개인 데이터(주문, 자산 등)를 실시간으로 수신하기 위한 WebSocket 관리자입니다.
    JWT 토큰을 사용하여 인증이 필요합니다.

    사용 예제:

        >> access = "your_access_key"
        >> secret = "your_secret_key"
        >> pwm = PrivateWebSocketManager(access, secret, "MyOrder")
        >> for i in range(3):
            >>     data = pwm.get()
            >>     print(data)
        >> pwm.terminate()

    주의:

       재귀적인 호출을 위해 다음의 guard를 반드시 추가해야 한다.
       >> if __name__ == "__main__"

    Args:
        access_key: Upbit API Access Key
        secret_key: Upbit API Secret Key
        type: 구독 메시지 종류
            - "MyOrder": 내 주문 정보
            - "MyAsset": 내 자산 정보
        codes: 구독할 암호화폐 코드 리스트 (선택사항)
            - 예: ["KRW-BTC", "KRW-ETH"]
        qsize: 메시지를 저장할 Queue의 크기 (기본값: 1000)

    Examples:
        >>> # 내 주문 정보 실시간 수신
        >>> pwm = PrivateWebSocketManager(
        ...     "access_key",
        ...     "secret_key",
        ...     "MyOrder"
        ... )
        >>> data = pwm.get()

        >>> # 내 자산 정보 실시간 수신
        >>> pwm = PrivateWebSocketManager(
        ...     "access_key",
        ...     "secret_key",
        ...     "MyAsset"
        ... )
        >>> data = pwm.get()

    Note:
        - PrivateWebSocketManager는 개인용 WebSocket으로 인증이 필요합니다
        - type 파라미터에 따라 수신 가능한 데이터가 다릅니다
        - "MyOrder": 주문 체결, 변경, 완료 등의 이벤트
        - "MyAsset": 자산 변동 정보
    """

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        type: str,
        codes: Optional[List[str]] = None,
        qsize: int = 1000
    ):
        """개인용 WebSocket 관리자 생성자

        Args:
            access_key: Upbit API Access Key
            secret_key: Upbit API Secret Key
            type: 구독 메시지 종류 ("MyOrder", "MyAsset")
            codes: 구독할 암호화폐 코드 리스트 (선택사항)
            qsize: 메시지를 저장할 Queue의 크기
        """
        self.__q = mp.Queue(qsize)
        self.alive = False

        self.access_key = access_key
        self.secret_key = secret_key
        self.type = type
        self.codes = codes if codes is not None else []

        super().__init__()

    def _generate_jwt_token(self) -> str:
        """JWT 토큰 생성

        Returns:
            str: JWT 토큰
        """
        payload = {
            "access_key": self.access_key,
            "nonce": str(uuid.uuid4())
        }
        jwt_token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return f'Bearer {jwt_token}'

    async def __connect_socket(self):
        """WebSocket 연결 및 메시지 수신"""
        uri = "wss://api.upbit.com/websocket/v1/private"

        headers = {
            "Authorization": self._generate_jwt_token()
        }

        async for websocket in websockets.connect(
            uri,
            ping_interval=60,
            extra_headers=headers
        ):
            try:
                # 구독 요청 데이터 생성
                data = [{
                    "ticket": str(uuid.uuid4())[:8]
                }, {
                    "type": self.type,
                    "codes": self.codes
                }]

                await websocket.send(json.dumps(data))

                while self.alive:
                    recv_data = await websocket.recv()
                    recv_data = recv_data.decode('utf8')
                    self.__q.put(json.loads(recv_data))
            except websockets.ConnectionClosed:
                self.__q.put('ConnectionClosedError')
                continue
            except Exception as e:
                self.__q.put(f'Error: {str(e)}')
                continue

    def run(self):
        """WebSocket 연결 실행"""
        asyncio.run(self.__connect_socket())

    def get(self) -> Dict[str, Any]:
        """메시지 수신

        Returns:
            dict: 수신된 메시지 데이터
        """
        if self.alive is False:
            self.alive = True
            self.start()
        return self.__q.get()

    def terminate(self):
        """WebSocket 연결 종료"""
        self.alive = False
        super().terminate()
