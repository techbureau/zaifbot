from threading import Lock


class APIRepository:
    _instance = None
    _lock = Lock()

    def __new__(cls, public_api, trade_api, stream_api):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, public_api, trade_api, stream_api):
        self._public_api = public_api
        self._trade_api = trade_api
        self._stream_api = stream_api

    @property
    def public_api(self):
        return self._public_api

    @property
    def trade_api(self):
        return self._trade_api

    @property
    def stream_api(self):
        return self._stream_api
