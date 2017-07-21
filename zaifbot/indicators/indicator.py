from abc import ABCMeta, abstractmethod
from talib import abstract


class Indicator(metaclass=ABCMeta):
    MAX_LENGTH = 100
    MAX_COUNT = 1000

    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError

    @staticmethod
    def execute_function(name, *args, **kwargs):
        return abstract.Function(name, *args, **kwargs)
