from threading import Lock
from .web import BotPublicApi


class CurrencyPair:
    _lock = Lock()
    _instances = {}

    def __new__(cls, pair):
        with cls._lock:
            pair = str(pair)
            if cls._instances.get(pair, None) is None:
                cls._instances[pair] = super().__new__(cls)
        return cls._instances[pair]

    def __init__(self, pair):
        self._name = pair
        self._info = _ZaifCurrencyPairsInfo()[pair]

    def __str__(self):
        return self._name

    @property
    def info(self):
        return self._info

    @property
    def is_token(self):
        return self._info['is_token']
    #
    # def get_round_amount(self, amount):
    #     rounded_amount = amount - (amount % self._info['item_unit_step'])
    #     digits = len(str(self._info['item_unit_step'])) - 2
    #     return round(rounded_amount, digits)
    #
    # def get_buyable_amount(self, amount, price):
    #     buyable_amount = amount / price
    #     return self.get_round_amount(buyable_amount)
    #
    # def get_more_executable_price(self, price, *, is_buy):
    #     # todo: incorrect processing
    #     if is_buy:
    #         return price + (self._info['aux_unit_step'] -
    #                         (price % self._info['aux_unit_step']))
    #     else:
    #         return price - (price % self._info['aux_unit_step'])


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
