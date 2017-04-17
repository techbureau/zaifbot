class ApiKeys:
    def __init__(self, key='', secret=''):
        self._api_keys = {'key': key, 'secret': secret}

    @property
    def key(self):
        return self._api_keys['key']

    @key.setter
    def key(self, key):
        self._api_keys['key'] = key

    @property
    def secret(self):
        return self._api_keys['secret']

    @secret.setter
    def secret(self, secret):
        self._api_keys['secret'] = secret

class System:
    def __init__(self, sleep_time='1m', currency_pair='btc_jpy', api_domain='api.zaif.jp', retry_count=5):
        self._system = {'sleep_time': sleep_time, 'currency_pair': currency_pair, 'api_domain': api_domain, 'retry_count': retry_count}
        self._socket = _Socket()

    @property
    def sleep_time(self):
        return self._system['sleep_time']

    @sleep_time.setter
    def sleep_time(self, time):
        self._system['sleep_time'] = time

    @property
    def currency_pair(self):
        return self._system['currency_pair']

    @currency_pair.setter
    def currency_pair(self, pair):
        self._system['currency_pair'] = pair

    @property
    def api_domain(self):
        return self._system['api_domain']

    @property
    def retry_count(self):
        return self._system['retry_count']

    @retry_count.setter
    def retry_count(self, count):
        self._system['retry_count'] = count

    @property
    def socket(self):
        return self._socket

class _Socket:
    def __init__(self):
        self._socket = {'port': 8888}

    @property
    def port(self):
        return self._socket['port']
