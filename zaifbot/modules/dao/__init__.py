from abc import ABCMeta, abstractmethod
from zaifbot.models import Base, engine, get_session
from zaifbot.models import moving_average, bollinger_bands


class DaoBase(metaclass=ABCMeta):
    def __init__(self):
        self.model = self.get_model()
        Base.metadata.create_all(bind=engine, tables=[self.model.__table__])

    @classmethod
    def get_session(cls):
        return get_session()

    @abstractmethod
    def get_model(self):
        raise NotImplementedError()


def init_database():
    Base.metadata.create_all(bind=engine)
