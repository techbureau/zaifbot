# from threading import Lock
#
#
# class _APIKeeper:
#     _instance = None
#     _lock = Lock()
#     _public_api = None
#     _trade_api = None
#     _stream_api = None
#
#     def __new__(cls):
#         with cls._lock:
#             if cls._instance is None:
#                 cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def register_public(self, public_api):
#         self._public_api = public_api
#
#     def register_trade(self, trade_api):
#         self._public_api = trade_api
#
#     def register_stream(self, stream_api):
#         self._stream_api = stream_api
#
#     @property
#     def public_api(self):
#         return self._public_api
#
#     @property
#     def trade_api(self):
#         return self._trade_api
#
#     @property
#     def stream_api(self):
#         return self._stream_api
#
#
# def initialize_api(key, secret, mode='real'):
#     if mode == 'real':
#         pass
#     if mode == 'backtest':
#         api_keeper = _APIKeeper()
#         from zaifbot.backtest.api import BackTestStreamApi, BackTestTradeApi, BackTestPublicApi
#         api_keeper.register_public(BackTestPublicApi())
#         api_keeper.register_trade(BackTestTradeApi())
#         api_keeper.register_stream(BackTestStreamApi())
#     else:
#         raise ValueError('illegal argument')
#
# ApiKeeper = _APIKeeper()
