import json
import sys
import threading
from zaifapi.impl import ZaifPublicApi
from zaifbot.bot_common.config.config_object import *
from zaifbot.bot_common.config.property import ApiKeys, Event, System



def load_config():
    return _ConfigLoader()


def _get_current_last_price(currency_pairs):
    api = ZaifPublicApi()
    return api.last_price(currency_pairs)['last_price']


def _read_config():
    return Config(SystemValue(), ApiKeysValue(), EventValue())


class _ConfigLoader:
    _instance = None
    _lock = threading.Lock()
    _start_time_last_price = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                config_json = _read_config()
                system = System(config_json)
                cls._start_time_last_price = _get_current_last_price(system.currency_pair)
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

    @property
    def start_time_last_price(self):
        return self._start_time_last_price
