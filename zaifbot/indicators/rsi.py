import pandas as pd
from .indicator import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


class RSI(Indicator):
    _NAME = 'rsi'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        super().__init__(currency_pair, period)
        self._length = self._bounded_length(length)

    def request_data(self, count=100, to_epoch_time=None):
        candlesticks_df = self._get_candlesticks_df(count, to_epoch_time)

        rsi = self._exec_talib_func(candlesticks_df, price=_CLOSE, timeperiod=self._length).rename('rsi')
        formatted_rsi = self._formatting(candlesticks_df[_TIME], rsi)
        return formatted_rsi

    def _required_candlesticks_count(self, count):
        return self._bounded_count(count) + self._length

    @staticmethod
    def _formatting(time_df, rsi):
        rsi = pd.concat([time_df, rsi], axis=1).dropna()
        return rsi.astype(object).to_dict(orient='records')
