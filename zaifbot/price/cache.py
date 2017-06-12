from threading import Lock

from zaifbot.api.wrapper import BotPublicApi


class ZaifCurrencyPairs:
    _instance = None
    _lock = Lock()
    _threads = {}
    _stop_events = {}
    _last_prices = {}
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
        return None
