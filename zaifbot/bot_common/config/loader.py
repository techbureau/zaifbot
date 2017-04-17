import threading
from zaifbot.bot_common.config.property import ApiKeys, Event, System


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
        self._system = System()
        self._event = Event()

    @property
    def system(self):
        return self._system

    @property
    def event(self):
        return self._event
