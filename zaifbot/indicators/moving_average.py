from abc import ABCMeta
import pandas as pd
from .indicator import Indicator
from zaifbot.exchange.currency_pairs import CurrencyPair
from zaifbot.exchange.period import Period


class _MA(Indicator, metaclass=ABCMeta):
    def __init__(self, currency_pair='btc_jpy', period='1d', length=25):
        self._currency_pair = CurrencyPair(currency_pair)
        self._period = Period(period)
        self._length = self._bounded_length(length)

    @property
    def name(self):
        return self._NAME

    def request_data(self, count=100, to_epoch_time=None):
        adjusted_count = self._adjust_count(count)
        candlesticks_df = self._get_candlesticks_df(self._currency_pair,
                                                    self._period, adjusted_count,
                                                    to_epoch_time)

        ma = self._execute_talib(self.name, candlesticks_df, timeperiod=self._length)
        formatted_ma = self._formatting(candlesticks_df['time'], ma)
        return formatted_ma

    def is_increasing(self):
        previous, last = self.request_data(count=2)
        return last[self.name] > previous[self.name]

    def is_decreasing(self):
        return not self.is_increasing()

    def _adjust_count(self, count):
        return self._bounded_count(count) + self._length - 1

    def _formatting(self, time_df, ma):
        ma = ma.rename(self.name).dropna()
        return pd.concat([time_df, ma], axis=1).dropna().astype(object).to_dict(orient='records')


class EMA(_MA):
    _NAME = 'ema'


class SMA(_MA):
    _NAME = 'sma'
