import threading
from zaifapi.impl import ZaifPublicApi
from zaifbot.bot_common.config.config_object import *
from zaifbot.bot_common.config.property import ApiKeys, Event, System



def load_config():
    return _ConfigLoader()

def _read_config():
    return Config(SystemValue(), ApiKeysValue(), EventValue())


class _ConfigLoader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        config_json = _read_config()
        self._api_keys = ApiKeys(config_json)
        self._system = System(config_json)
        self._event = Event(config_json)

    @property
    def api_keys(self):
        return self._api_keys

    @property
    def system(self):
        return self._system

    @property
    def event(self):
        return self._event
