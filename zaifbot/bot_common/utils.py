import json
import threading
from websocket import create_connection
from zaifapi.impl import ZaifPublicApi
from zaifbot.bot_common.config import load_config


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
            except:
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
