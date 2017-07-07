from abc import ABCMeta, abstractmethod
from zaifbot.models import get_session


class DaoBase(metaclass=ABCMeta):
    _CLOSED = 1

    def __init__(self):
        self.model = self.get_model()

    @classmethod
    def get_session(cls):
        return get_session()

    @abstractmethod
    def get_model(self):
        raise NotImplementedError()
