from threading import Lock
from zaifbot.exchange.api.http import BotTradeApi, BotPublicApi
from zaifbot.backtest.api import BackTestStreamApi, BackTestTradeApi, BackTestPublicApi


class _APIKeeper:
    _instance = None
    _lock = Lock()
    _public_api = None
    _trade_api = None
    _stream_api = None

    def __new__(cls, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        self._public_api = self._public_api or kwargs.get('public_api')
        self._trade_api = self._trade_api or kwargs.get('trade_api')
        self._stream_api = self._stream_api or kwargs.get('stream_api')

    def register_public(self):
        pass

    @property
    def public_api(self):
        return self._public_api

    @property
    def trade_api(self):
        return self._trade_api

    @property
    def stream_api(self):
        return self._stream_api


def api_maker(key, secret, mode='real'):
    if mode == 'real':
        pass
    if mode == 'backtest':
        return _APIKeeper(public_api=BackTestPublicApi(), trade_api=BackTestTradeApi(), stream_api=BackTestStreamApi())
    else:
        raise ValueError('illegal argument')
