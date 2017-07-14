from datetime import datetime
from zaifbot.errors import ZaifBotError
from zaifbot.exchange.period import Period
from zaifbot.indicators.candle_sticks import CandleSticks
from zaifbot.utils import datetime2timestamp
from pandas import DataFrame as DF
from threading import Lock


class BackTest:
    def __init__(self, strategy, from_datetime, to_datetime, *, price_interval='1m'):
        self._strategy = strategy
        self._currency_pair = self._strategy.currency_pair
        self._price_interval = Period(price_interval)
        self._strategy.regular_task = self._update_context
        self._context = Context
        self._public_api = ApiKeeper.public_api
        self._trade_api = ApiKeeper.trade_api
        self._stream_api = ApiKeeper.stream_api

        if from_datetime > datetime.now():
            raise ZaifBotError('got illegal datetime range')
        self._from_datetime = from_datetime
        self._to_datetime = to_datetime

    def start(self):
        self._before_backtest()
        self._strategy.start(sec_wait=0)

    def _before_backtest(self):
        # fixme: 分散処理させる
        self._strategy.regular_job = self._update_context
        self._context.init_price(self._from_datetime, self._to_datetime, self._currency_pair, self._price_interval)

    def _update_context(self):
        # fixme: 終了条件
        self._context.update_time()


class _BackTestContext:
    _instance = None
    _lock = Lock()
    _currency_pairs = None
    _data = None
    _length = 0

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def init_price(self, from_datetime, to_datetime, currency_pair, price_interval):
        candle_sticks = CandleSticks(currency_pair=currency_pair, period=price_interval)
        self._data = DF(candle_sticks.request_data(1500, datetime2timestamp(to_datetime)))[['time', 'close']]

    def update_time(self):
        self._length += 1

    def current_price(self):
        print(self._length)
        return self._data.ix[self._length, 'close']

    def current_time(self):
        return self._data.ix[self._length, 'time']

Context = _BackTestContext()
