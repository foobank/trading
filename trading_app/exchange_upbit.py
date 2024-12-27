# trading_app/exchange_upbit.py
import os
import uuid
import requests
import jwt
import hashlib
from urllib.parse import urlencode

UPBIT_ACCESS_KEY = os.environ.get('UPBIT_ACCESS_KEY')
UPBIT_SECRET_KEY = os.environ.get('UPBIT_SECRET_KEY')
UPBIT_SERVER_URL = "https://api.upbit.com"

class UpbitClient:
    def __init__(self):
        self.access_key = UPBIT_ACCESS_KEY
        self.secret_key = UPBIT_SECRET_KEY
        self.server_url = UPBIT_SERVER_URL

    def _make_headers(self, query=None):
        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4())
        }

        if query:
            query_string = urlencode(query)
            m = hashlib.sha512()
            m.update(query_string.encode())
            query_hash = m.hexdigest()
            payload['query_hash'] = query_hash
            payload['query_hash_alg'] = 'SHA512'

        jwt_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        headers = {
            'Authorization': f'Bearer {jwt_token}',
        }
        return headers

    def get_ticker(self, market="KRW-BTC"):
        """현재가 조회"""
        url = f"{self.server_url}/v1/ticker"
        params = {'markets': market}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data[0]['trade_price']  # 마지막 체결가
        return None

    def get_balances(self):
        """보유 자산 조회"""
        url = f"{self.server_url}/v1/accounts"
        headers = self._make_headers()
        resp = requests.get(url, headers=headers)
        return resp.json()

    def create_order(self, market="KRW-BTC", side="bid", volume=None, price=None, ord_type="limit"):
        """
        업비트 주문 요청
        side: bid(매수), ask(매도)
        ord_type: limit, price(시장가 매수), market(시장가 매도) 등
        volume, price는 ord_type에 따라 달라짐
        """
        url = f"{self.server_url}/v1/orders"
        query = {
            'market': market,
            'side': side,
            'ord_type': ord_type,
        }
        if volume:
            query['volume'] = volume
        if price:
            query['price'] = price

        headers = self._make_headers(query)
        resp = requests.post(url, headers=headers, params=query)
        return resp.json()
