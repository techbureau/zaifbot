import threading
from zaifbot.bot_common.config.property import ApiKeys, System


def load_config():
    return _Config()

class _Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._api_keys = ApiKeys()
        self._system = System()

    @property
    def api_keys(self):
        return self._api_keys

    @property
    def system(self):
        return self._system
