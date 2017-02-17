from zaifbot.bot_common.config.property.event import *


class ApiKeys:
    def __init__(self, config_json):
        self._api_keys = config_json['api_keys']

    @property
    def key(self):
        return self._api_keys['key']

    @property
    def secret(self):
        return self._api_keys['secret']


class System:
    def __init__(self, config_json):
        self._system = config_json['system']

    @property
    def sleep_time(self):
        return self._system['sleep_time']

    @property
    def currency_pair(self):
        return self._system['currency_pair']


class Event:
    def __init__(self, config_json):
        self._loss_cut = LossCut(config_json)

    @property
    def loss_cut(self):
        return self._loss_cut
