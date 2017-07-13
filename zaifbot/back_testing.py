from datetime import datetime
from zaifbot.errors import ZaifBotError
from zaifbot.exchange.period import Period
from zaifbot.indicators.candle_sticks import CandleSticks
from zaifbot.utils import datetime2timestamp
from pandas import DataFrame as DF
from zaifbot.api_manage import APIRepository


class BackTestTradeApi:
    def __init__(self):
        self._time = None
        self._price = None

    def trade(self):
        print('trade')


class BackTestPublicApi:
    def __init__(self):
        self._time = None
        self._price = None

    def last_price(self, currency_pair):
        return {'last_price': self._price}


class BackTestStreamApi:
    def __init__(self):
        self._time = None
        self._price = None

    def _execute(self):
        print('execute')


class BackTest:
    def __init__(self, strategy, from_datetime, to_datetime, *, price_interval='1m'):
        self._strategy = strategy
        self._currency_pair = self._strategy.currency_pair
        self._price_interval = Period(price_interval)
        self._strategy.regular_task = self._update_context
        self._public_api = BackTestPublicApi()
        self._trade_api = BackTestTradeApi()
        self._stream_api = BackTestStreamApi()
        self._repository = APIRepository(self._public_api, self._trade_api, self._stream_api)
        self._length = 0
        self._data = None

        if from_datetime > datetime.now():
            raise ZaifBotError('got illegal datetime range')
        self._from_datetime = from_datetime
        self._to_datetime = to_datetime

    def start(self):
        self._before_backtest()
        self._strategy.start(sec_wait=0)

    def _before_backtest(self):
        # fixme: 分散処理させる
        candle_sticks = CandleSticks(currency_pair=self._currency_pair, period=self._price_interval)
        self._data = DF(candle_sticks.request_data(1500, datetime2timestamp(self._to_datetime)))[['time', 'close']]

    def _update_context(self):
        # fixme: 終了条件
        self._public_api._time = self._data.ix[self._length, 'time']
        self._trade_api._time = self._data.ix[self._length, 'time']
        self._stream_api._time = self._data.ix[self._length, 'time']

        self._public_api._price = self._data.ix[self._length, 'price']
        self._trade_api._price = self._data.ix[self._length, 'price']
        self._stream_api._price = self._data.ix[self._length, 'price']

        self._length += 1
