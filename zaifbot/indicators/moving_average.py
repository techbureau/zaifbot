import time
import pandas as pd
from pandas import DataFrame as DF
from zaifbot.price.ohlc_prices import OhlcPrices
from talib import abstract as ab
from zaifbot.bot_common.bot_const import LIMIT_COUNT, LIMIT_LENGTH
from .base import Indicator

__all__ = ['EMA', 'SMA']


# TODO: 不可能なcountの場合の処理
class MA(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, LIMIT_LENGTH)

    def get_data(self, count, to_epoch_time):
        raise NotImplementedError

    def _calc_price_count(self, count):
        return count + self._length - 1

    def _get_ma(self, count, to_epoch_time, name):
        count = self._calc_price_count(min(count, LIMIT_COUNT))
        to_epoch_time = to_epoch_time or int(time.time())
        ohlcs = DF(OhlcPrices(self._currency_pair, self._period).fetch_data(count, to_epoch_time))
        ma = ab.Function(name)(ohlcs, timeperiod=self._length).rename(name).dropna()
        formatted_ma = pd.concat([ohlcs['time'], ma], axis=1).dropna().astype(object).to_dict(orient='records')

        return {'success': 1, 'return': {name: formatted_ma}}


class EMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        super().__init__(currency_pair, period, length)

    def get_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'ema')


class SMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=LIMIT_LENGTH):
        super().__init__(currency_pair, period, length)

    def get_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'sma')
