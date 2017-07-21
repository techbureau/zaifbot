from abc import ABCMeta, abstractmethod
from talib import abstract
from pandas import DataFrame
from zaifbot.exchange.candle_sticks import CandleSticks


class Indicator(metaclass=ABCMeta):
    _MAX_LENGTH = 100
    _MAX_COUNT = 1000
    _NAME = None

    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period

    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _exec_talib_func(cls, *args, **kwargs):
        return abstract.Function(cls.name)(*args, **kwargs)

    def _get_candlesticks_df(self, count, to_epoch_time):
        candle_sticks = CandleSticks(self._currency_pair, self._period)
        candle_sticks_data = candle_sticks.request_data(count, to_epoch_time)
        return DataFrame(candle_sticks_data)

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @classmethod
    def _bounded_length(cls, value):
        return min(max(value, 0), cls._MAX_LENGTH)

    @classmethod
    def _bounded_count(cls, value):
        return min(max(value, 0), cls._MAX_COUNT)
