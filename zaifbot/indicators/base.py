from abc import ABCMeta, abstractmethod


class Indicator(metaclass=ABCMeta):
    @abstractmethod
    def get_data(self):
        raise NotImplementedError
