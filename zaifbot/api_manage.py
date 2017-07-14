from threading import Lock


class APIRepository:
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

    @property
    def public_api(self):
        return self._public_api

    @property
    def trade_api(self):
        return self._trade_api

    @property
    def stream_api(self):
        return self._stream_api
