import pandas as pd
from .indicator import Indicator


class ADX(Indicator):
    _NAME = 'adx'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        super().__init__(currency_pair, period)
        self._length = self._bounded_length(length)

    def request_data(self, count=100, to_epoch_time=None):
        candlesticks_df = self._get_candlesticks_df(count, to_epoch_time)

        adx = self._exec_talib_func(candlesticks_df,
                                    timeperiod=self._length,
                                    prices=['high', 'low', 'close'])

        formatted_adx = self._formatting(candlesticks_df, adx)
        return formatted_adx

    def _required_candlesticks_count(self, count):
        return 2 * self._length - 1 + self._bounded_count(count)

    def _formatting(self, candlesticks_df, adx):
        adx.rename(self.name, inplace=True)
        adx_with_time = pd.concat([candlesticks_df['time'], adx], axis=1)
        adx_with_time.dropna(inplace=True)
        dict_adx = adx_with_time.astype(object).to_dict(orient='records')
        return dict_adx
