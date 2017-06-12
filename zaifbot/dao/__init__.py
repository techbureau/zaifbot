from abc import ABCMeta, abstractmethod
from zaifbot.models import Base, engine, get_session


from .ohlc_prices import OhlcPricesDao
from .moving_average import MovingAverageDao
from .bollinger_bands import BollingerBandsDao

__all__ = [OhlcPricesDao,
           MovingAverageDao,
           BollingerBandsDao]


class DaoBase(metaclass=ABCMeta):
    def __init__(self):
        self.model = self.get_model()

    @classmethod
    def get_session(cls):
        return get_session()

    @abstractmethod
    def get_model(self):
        raise NotImplementedError()


def init_database():
    Base.metadata.create_all(bind=engine)
