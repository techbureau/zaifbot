from abc import ABCMeta, abstractmethod
from talib import abstract
from pandas import DataFrame
from zaifbot.exchange.candle_sticks import CandleSticks


class Indicator(metaclass=ABCMeta):
    _MAX_LENGTH = 100
    _MAX_COUNT = 1000
    _NAME = None

    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _execute_talib(name, *args, **kwargs):
        return abstract.Function(name)(*args, **kwargs)

    @staticmethod
    def _get_candlesticks_df(currency_pair, period, count, to_epoch_time):
        candle_sticks_data = CandleSticks(currency_pair, period).request_data(count, to_epoch_time)
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
