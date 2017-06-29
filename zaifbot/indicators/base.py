from abc import ABCMeta, abstractmethod


class Indicator(metaclass=ABCMeta):
    @abstractmethod
    def request_data(self, *args, **kwargs):
        raise NotImplementedError
