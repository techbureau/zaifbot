import json
import threading
from websocket import create_connection
from zaifapi.impl import ZaifPublicApi, ZaifPrivateApi
from zaifbot.bot_common.config import load_config
from zaifbot.bot_common.save_order_log import save_order_log


class _ZaifWebSocket:
    _WEB_SOCKET_API_URI = 'ws://{}:{}/stream?currency_pair={}'
    _instance = None
    _lock = threading.Lock()
    _ws = None
    _config = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._config = load_config()
                cls._ws = cls._get_connection()
        return cls._instance

    def __del__(self):
        self._ws.close()

    @property
    def last_price(self):
        for count in range(self._config.system.retry_count):
            try:
                result = self._ws.recv()
                json_obj = json.loads(result)
                return json_obj['last_price']['price']
            except Exception:
                self._ws = self._get_connection()
        api = ZaifPublicApi()
        return api.last_price(self._config.system.currency_pair)['last_price']

    @classmethod
    def _get_connection(cls):
        return create_connection(cls._WEB_SOCKET_API_URI.format(cls._config.system.api_domain,
                                                                cls._config.system.socket.port,
                                                                cls._config.system.currency_pair))


def get_current_last_price():
    api = _ZaifWebSocket()
    return api.last_price


class ZaifOrder:
    def __init__(self):
        self._config = load_config()
        self._private_api = ZaifPrivateApi(self._config.api_keys.key, self._config.api_keys.secret)

    def get_active_orders(self):
        try:
            return self._private_api.active_orders(currency_pair=self._config.system.currency_pair,
                                                   is_token_both=True)
        except Exception:
            return {}

    def trade(self, action, price, amount):
        try:
            trade_result = self._private_api.trade(currency_pair=self._config.system.currency_pair,
                                                   action=action,
                                                   price=price,
                                                   amount=amount)
            save_order_log(trade_result)
            if trade_result['received'] > 0.0:
                return {'success': 1, 'return': trade_result}
            return {'success': 0, 'return': trade_result}
        except Exception:
            return {'success': 0, 'return': {'order_id': None}}

    def cancel_order(self, order_id):
        try:
            cancel_result = self._private_api.cancel_order(order_id=order_id)
            save_order_log(cancel_result)
        except Exception:
            return False
