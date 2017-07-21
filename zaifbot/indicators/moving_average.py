import pandas as pd
from zaifbot.utils import int_time
from .indicator import Indicator


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
        count, to_epoch_time = self._pre_processing(count, to_epoch_time)

        candlesticks_df = self.get_candlesticks_df(self._currency_pair, self._period, count, to_epoch_time)
        ma = self.execute_function(name, candlesticks_df, timeperiod=self._length).rename(name).dropna()

        formatted_ma = self._formatting(candlesticks_df['time'], ma)
        return formatted_ma

    def _pre_processing(self, count, to_epoch_time):
        count = self._get_adjusted_count(count)
        to_epoch_time = to_epoch_time or int_time()
        return count, to_epoch_time

    @staticmethod
    def _formatting(time_df, ma):
        return pd.concat([time_df, ma], axis=1).dropna().astype(object).to_dict(orient='records')


class EMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    def request_data(self, count=100, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'ema')

    def is_increasing(self):
        previous, last = self.request_data(2, int_time())
        return last['ema'] > previous['ema']

    def is_decreasing(self):
        return not self.is_increasing()


class SMA(MA):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    def request_data(self, count=100, to_epoch_time=None):
        return self._get_ma(count, to_epoch_time, 'sma')

    def is_increasing(self):
        previous, last = self.request_data(2, int_time())
        return last['sma'] > previous['sma']

    def is_decreasing(self):
        return not self.is_increasing()
