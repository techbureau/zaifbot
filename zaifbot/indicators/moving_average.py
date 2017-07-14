import time

import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab

from .indicator import Indicator
from .candle_sticks import CandleSticks


class MA(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, self.MAX_LENGTH)

    def request_data(self, count, to_epoch_time):
        raise NotImplementedError

    def _get_adjusted_count(self, count):
        min(count, self.MAX_COUNT)
        return count + self._length - 1

    def _get_ma(self, count, to_epoch_time, name):
        count = self._get_adjusted_count(count)
        to_epoch_time = to_epoch_time or int(time.time())
        candlesticks = DF(CandleSticks(self._currency_pair, self._period).request_data(count, to_epoch_time))
        ma = ab.Function(name)(candlesticks, timeperiod=self._length).rename(name).dropna()
        formatted_ma = pd.concat([candlesticks['time'], ma], axis=1).dropna().astype(object).to_dict(orient='records')
        return formatted_ma


class EMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    def request_data(self, count=100, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'ema')

    # todo: 抽象化
    def is_increasing(self):
        previous, last = self.request_data(2, int(time.time()))
        return last['ema'] > previous['ema']

    def is_decreasing(self):
        return not self.is_increasing()


class SMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    def request_data(self, count=100, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'sma')

    def is_increasing(self):
        previous, last = self.request_data(2, int(time.time()))
        return last['sma'] > previous['sma']

    def is_decreasing(self):
        return not self.is_increasing()
