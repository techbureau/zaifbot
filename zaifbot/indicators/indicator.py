from abc import ABCMeta, abstractmethod
from talib import abstract
from pandas import DataFrame
from zaifbot.exchange.candle_sticks import CandleSticks


class Indicator(metaclass=ABCMeta):
    MAX_LENGTH = 100
    MAX_COUNT = 1000

    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def execute_function(name, *args, **kwargs):
        return abstract.Function(name)(*args, **kwargs)

    @staticmethod
    def get_candlesticks_df(currency_pair, period, count, to_epoch_time):
        candle_sticks_data = CandleSticks(currency_pair, period).request_data(count, to_epoch_time)
        return DataFrame(candle_sticks_data)

