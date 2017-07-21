from abc import ABCMeta
import pandas as pd
from zaifbot.utils import int_time
from .indicator import Indicator


class _MA(Indicator, metaclass=ABCMeta):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = currency_pair
        self._period = period
        self._length = min(length, self._MAX_LENGTH)

    def _adjust_count(self, count):
        min(count, self._MAX_COUNT)
        return count + self._length - 1

    def _pre_processing(self, count, to_epoch_time):
        count = self._adjust_count(count)
        to_epoch_time = to_epoch_time or int_time()
        return count, to_epoch_time

    @staticmethod
    def _formatting(time_df, ma):
        return pd.concat([time_df, ma], axis=1).dropna().astype(object).to_dict(orient='records')


class EMA(_MA):
    _NAME = 'ema'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    @property
    def name(self):
        return self._NAME

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count, adjusted_to_epoch_time = self._pre_processing(count, to_epoch_time)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period, adjusted_count,
                                                    adjusted_to_epoch_time)

        ema = self._execute_talib(self.name, candlesticks_df, timeperiod=self._length).rename(self.name).dropna()
        formatted_ema = self._formatting(candlesticks_df['time'], ema)
        return formatted_ema

    def is_increasing(self):
        previous, last = self.request_data(2, int_time())
        return last['ema'] > previous['ema']

    def is_decreasing(self):
        return not self.is_increasing()


class SMA(_MA):
    _NAME = 'sma'

    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        super().__init__(currency_pair, period, length)

    @property
    def name(self):
        return self._NAME

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count, adjusted_to_epoch_time = self._pre_processing(count, to_epoch_time)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period, adjusted_count,
                                                    adjusted_to_epoch_time)

        sma = self._execute_talib(self.name, candlesticks_df, timeperiod=self._length).rename(self.name).dropna()
        formatted_sma = self._formatting(candlesticks_df['time'], sma)
        return formatted_sma

    def is_increasing(self):
        previous, last = self.request_data(2, int_time())
        return last['sma'] > previous['sma']

    def is_decreasing(self):
        return not self.is_increasing()
