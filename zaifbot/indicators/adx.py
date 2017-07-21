import pandas as pd

from .indicator import Indicator

_HIGH = 'high'
_LOW = 'low'
_CLOSE = 'close'
_TIME = 'time'


class ADX(Indicator):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        self._currency_pair = currency_pair
        self._period = period
        self._length = self._bounded_length(length)

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count = self._get_adjusted_count(count)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period,
                                                    adjusted_count,
                                                    to_epoch_time)

        adx = self._execute_talib(candlesticks_df, timeperiod=self._length, prices=[_HIGH, _LOW, _CLOSE], output_names=['adx']).rename('adx')

        formatted_adx = self._formatting(candlesticks_df[_TIME], adx)
        return formatted_adx

    def _get_adjusted_count(self, count):
        return 2 * self._length - 1 + self._bounded_count(count)

    def _formatting(self, time_df, adx):
        adx = pd.concat([time_df, adx], axis=1).dropna()
        return adx.astype(object).to_dict(orient='records')
