import pandas as pd
from .indicator import Indicator


class BBANDS(Indicator):
    _NAME = 'bbands'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period)
        self._length = self._bounded_length(length)

    def request_data(self, count=100, lowbd=2, upbd=2, to_epoch_time=None):
        candlesticks_df = self._get_candlesticks_df(count, to_epoch_time)
        bbands = self._exec_talib_func('bbands', candlesticks_df, timeperiod=self._length, nbdevup=upbd, nbdevdn=lowbd, matype=0).dropna()
        formatted_bbands = self._formatting(candlesticks_df['time'], bbands)
        return formatted_bbands

    def _required_candlesticks_count(self, count):
        return self._length + self._bounded_count(count) - 1

    @staticmethod
    def _formatting(time_df, bbands):
        bbands = bbands.dropna()
        formatted_bbands = pd.concat([time_df, bbands[['lowerband', 'upperband']]], axis=1).dropna().astype(object).to_dict(orient='records')
        return formatted_bbands
