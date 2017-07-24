import pandas as pd
from talib import MA_Type
from .indicator import Indicator


class BBANDS(Indicator):
    _NAME = 'bbands'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=25, matype=MA_Type.EMA):
        super().__init__(currency_pair, period)
        self._length = self._bounded_length(length)
        self._matype = matype

    def request_data(self, count=100, lowbd=2, upbd=2, to_epoch_time=None):
        candlesticks_df = self._get_candlesticks_df(count, to_epoch_time)
        bbands = self._exec_talib_func(candlesticks_df,
                                       timeperiod=self._length,
                                       nbdevup=upbd,
                                       nbdevdn=lowbd,
                                       matype=self._matype)

        formatted_bbands = self._formatting(candlesticks_df, bbands)
        return formatted_bbands

    def _required_candlesticks_count(self, count):
        return self._length + self._bounded_count(count) - 1

    @staticmethod
    def _formatting(candlesticks_df, bbands):
        bbands_with_time = pd.concat([candlesticks_df['time'], bbands[['lowerband', 'upperband']]], axis=1)
        bbands_with_time.dropna(inplace=True)
        dict_bands = bbands_with_time.astype(object).to_dict(orient='records')
        return dict_bands
