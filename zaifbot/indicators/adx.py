import pandas as pd
from pandas import DataFrame as DF
from talib import abstract as ab
from zaifbot.exchange.candle_sticks import CandleSticks

from .indicator import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


class ADX(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, self.MAX_LENGTH)

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count = self._get_adjusted_count(count)
        candlesticks = CandleSticks(self._currency_pair, self._period)
        df = DF(candlesticks.request_data(adjusted_count, to_epoch_time))
        adx = ab.ADX(df, timeperiod=self._length, prices=[_HIGH, _LOW, _CLOSE], output_names=['adx']).rename('adx')
        adx = pd.concat([df[_TIME], adx], axis=1).dropna()
        return adx.astype(object).to_dict(orient='records')

    def _get_adjusted_count(self, count):
        count = min(count, self.MAX_COUNT)
        return 2 * self._length - 1 + count

