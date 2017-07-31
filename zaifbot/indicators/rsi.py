import pandas as pd
from .indicator import Indicator


class RSI(Indicator):
    _NAME = 'rsi'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=14):
        super().__init__(currency_pair, period)
        self._length = self._bounded_length(length)

    def request_data(self, count=100, to_epoch_time=None):
        candlesticks_df = self._get_candlesticks_df(count, to_epoch_time)

        rsi = self._exec_talib_func(candlesticks_df, price='close', timeperiod=self._length)
        formatted_rsi = self._formatting(candlesticks_df, rsi)
        return formatted_rsi

    def _required_candlesticks_count(self, count):
        return self._bounded_count(count) + self._length

    def _formatting(self, candlesticks, rsi):
        rsi.rename(self.name, inplace=True)
        rsi_with_time = pd.concat([candlesticks['time'], rsi], axis=1)
        rsi_with_time.dropna(inplace=True)
        dict_rsi = rsi_with_time.astype(object).to_dict(orient='records')
        return dict_rsi
