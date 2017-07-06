from abc import ABCMeta, abstractmethod
from zaifbot.models import Base, engine, get_session, moving_average, bollinger_bands, ohlc_prices, order_log


class DaoBase(metaclass=ABCMeta):
    _CLOSED = 1

    def __init__(self):
        self.model = self.get_model()

    @staticmethod
    def get_session():
        return get_session()

    @abstractmethod
    def get_model(self):
        raise NotImplementedError()


def init_database():
    Base.metadata.create_all(bind=engine)
