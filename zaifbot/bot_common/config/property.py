class ApiKeys:
    def __init__(self, api_keys={'key': 'key', 'secret': 'secret'}):
        self._api_keys = api_keys

    @property
    def key(self):
        return self._api_keys['key']

    @property
    def secret(self):
        return self._api_keys['secret']


class System:
    def __init__(self):
        self._system = {'sleep_time': '1m', 'currency_pair': 'btc_jpy', 'api_domain': "api.zaif.jp", 'retry_count': 5}
        self._socket = _Socket()

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
    def __init__(self):
        self._buy = _Buy()
        self._sell = _Sell()

    @property
    def buy(self):
        return self._buy

    @property
    def sell(self):
        return self._sell


class _Buy:
    def __init__(self):
        self._buy = {'target_value': 100000}

    @property
    def target_value(self):
        return self._buy['target_value']


class _Sell:
    def __init__(self):
        self._sell = {'target_value': 110000}

    @property
    def target_value(self):
        return self._sell['target_value']


class _Socket:
    def __init__(self):
        self._socket = {'port': 8888}

    @property
    def port(self):
        return self._socket['port']
