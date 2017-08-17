from threading import Lock
from zaifbot.exchange.api.http import BotPublicApi


class CurrencyPair:
    _lock = Lock()
    _instances = {}

    def __new__(cls, name):
        with cls._lock:
            name = str(name)
            if cls._instances.get(name, None) is None:
                cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, pair):
        self._name = str(pair)
        self._info = _ZaifCurrencyPairsInfo()[self._name]

    def __str__(self):
        return self._name

    def __getnewargs__(self):
        return (self._name,)

    @property
    def name(self):
        return self._name

    @property
    def info(self):
        return self._info

    @property
    def is_token(self):
        return self._info['is_token']


class _ZaifCurrencyPairsInfo:
    _instance = None
    _lock = Lock()
    _currency_pairs = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                api = BotPublicApi()
                cls._currency_pairs = api.currency_pairs('all')
        return cls._instance

    def __getitem__(self, currency_pair):
        record = list(filter(lambda x: x['currency_pair'] == currency_pair, self._currency_pairs))
        if record:
            return record[0]
        return KeyError('the pair does not exist')
