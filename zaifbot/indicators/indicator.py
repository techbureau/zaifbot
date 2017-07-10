from abc import ABCMeta, abstractmethod


class Indicator(metaclass=ABCMeta):
    MAX_LENGTH = 100
    MAX_COUNT = 1000

    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError
