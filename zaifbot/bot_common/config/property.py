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
        self._socket = _Socket(config_json)

    @property
    def sleep_time(self):
        return self._system['sleep_time']

    @property
    def currency_pair(self):
        return self._system['currency_pair']

    @property
    def api_domain(self):
        return self._system['api_domain']

    @property
    def retry_count(self):
        return self._system['retry_count']

    @property
    def socket(self):
        return self._socket


class Event:
    def __init__(self, config_json):
        self._buy = _Buy(config_json)
        self._sell = _Sell(config_json)

    @property
    def buy(self):
        return self._buy

    @property
    def sell(self):
        return self._sell


class _Buy:
    def __init__(self, config_json):
        self._buy = config_json['event']['buy']

    @property
    def target_value(self):
        return self._buy['target_value']


class _Sell:
    def __init__(self, config_json):
        self._sell = config_json['event']['sell']

    @property
    def target_value(self):
        return self._sell['target_value']


class _Socket:
    def __init__(self, config_json):
        self._socket = config_json['system']['socket']

    @property
    def port(self):
        return self._socket['port']
