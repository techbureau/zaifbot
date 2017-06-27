from datetime import datetime, timedelta
from threading import Thread, Event, Lock
from zaifapi.impl import ZaifPublicStreamApi

from zaifbot.bot_common.errors import ZaifBotError
from zaifbot.bot_common.logger import logger
from zaifbot.api.wrapper import BotPublicApi


class CurrencyPair:
    _lock = Lock()
    _instances = {}

    def __new__(cls, pair):
        with cls._lock:
            if cls._instances.get(pair, None) is None:
                cls._instances[pair] = super().__new__(cls)
        return cls._instances[pair]

    def __init__(self, pair):
        self._name = pair
        self._info = _ZaifCurrencyPairsCache()[pair]
        self._last_price = _ZaifLastPrice()

    def __str__(self):
        return self._name

    def is_token(self):
        return self._info['is_token']

    def last_price(self):
        return self._last_price.last_price(self._name)

    def get_round_amount(self, amount):
        rounded_amount = amount - (amount % self._info['item_unit_step'])
        digits = len(str(self._info['item_unit_step'])) - 2
        return round(rounded_amount, digits)

    def get_buyable_amount(self, amount, price):
        buyable_amount = amount / price
        return self.get_round_amount(buyable_amount)

    def get_more_executable_price(self, price, *, is_buy):
        if is_buy:
            return price + (self._info['aux_unit_step'] -
                            (price % self._info['aux_unit_step']))
        else:
            return price - (price % self._info['aux_unit_step'])


class _ZaifCurrencyPairsCache:
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


class _ZaifLastPrice:
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
        return cls._instance

    def _get_target_thread(self, currency_pair):
        def create_stream_thread():
            stop_event = Event()
            error_event = Event()
            thread_obj = _StreamThread(currency_pair, stop_event, error_event)
            thread_obj.start()
            self._threads[currency_pair] = thread_obj
            self._stop_events[currency_pair] = stop_event
        if currency_pair not in self._threads:
            create_stream_thread()
        if self._threads[currency_pair].is_error_happened:
            create_stream_thread()
        if self._threads[currency_pair].is_alive() is False:
            raise ZaifBotError('thread is dead')
        return self._threads[currency_pair]

    def last_price(self, currency_pair):
        def get_token_last_price():
            api = BotPublicApi()
            last_price = api.last_price(currency_pair)['last_price']
            jst_time = datetime.utcnow() + timedelta(hours=9)
            jst_time_str = jst_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            return {'timestamp': jst_time_str, 'last_price': last_price}

        def is_token():
            currency_pairs = _ZaifCurrencyPairsCache()
            currency_pair_rec = currency_pairs[currency_pair]
            if currency_pair_rec:
                return currency_pair_rec['is_token']
            raise ZaifBotError('illegal currency pair:{}'.format(currency_pair))
        if is_token():
            return get_token_last_price()
        receive = self._get_target_thread(currency_pair).last_receive
        return {'timestamp': receive['timestamp'], 'last_price': receive['last_price']['price']}

    def close_all_socket(self):
        [event.set() for event in self._stop_events.values()]
        [thread.join() for thread in self._threads.values()]


class _StreamThread(Thread):

    def __init__(self, currency_pair, stop_event, error_event):
        super(_StreamThread, self).__init__(name='{}_wss_stream'.format(currency_pair), daemon=True)
        self._currency_pair = currency_pair
        self._stop_event = stop_event
        self._last_receive = None
        self._stream_api = ZaifPublicStreamApi()
        self._set_first_last_price()
        self._error_event = error_event

    def run(self):
        try:
            for receive in self._stream_api.execute(self._currency_pair):
                self._last_receive = receive
                if self._stop_event.is_set():
                    self._stream_api.stop()
        except Exception as e:
            logger.error(e, exc_info=True)
            self._error_event.set()

    def _set_first_last_price(self):
        self._last_receive = next(self._stream_api.execute(self._currency_pair))

    @property
    def last_receive(self):
        return self._last_receive

    @property
    def is_error_happened(self):
        return self._error_event.is_set()
