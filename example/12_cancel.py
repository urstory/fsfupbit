import pyupbit
import pprint
import os

# 환경 변수에서 API 키를 읽어옵니다
# .env 파일에 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정하세요
access = os.getenv("UPBIT_ACCESS_KEY")
secret = os.getenv("UPBIT_SECRET_KEY")

if not access or not secret:
    print("환경 변수 UPBIT_ACCESS_KEY와 UPBIT_SECRET_KEY를 설정해주세요.")
    print("예: export UPBIT_ACCESS_KEY='your_access_key'")
    print("    export UPBIT_SECRET_KEY='your_secret_key'")
    exit(1)

upbit = pyupbit.Upbit(access, secret)
uuid = '116d25b3-37ba-4687-bdcb-e3d09a8675b3'  # 취소하고자하는 주문의 uuid
resp = upbit.cancel_order(uuid)
pprint.pprint(resp)