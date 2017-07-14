from threading import Lock


class APIRepository:
    _instance = None
    _lock = Lock()

    def __new__(cls, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, **kwargs):
        self._public_api = kwargs.get('public_api', None)
        self._trade_api = kwargs.get('trade_api', None)
        self._stream_api = kwargs.get('stream_api', None)

    @property
    def public_api(self):
        return self._public_api

    @property
    def trade_api(self):
        return self._trade_api

    @property
    def stream_api(self):
        return self._stream_api
