from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from zaifbot.common.database import Session
from zaifbot.models import OrderLogs, OhlcPrices
from zaifbot.common.logger import bot_logger


class DaoBase(metaclass=ABCMeta):
    def __init__(self):
        self._Model = self._get_model()

    @staticmethod
    @contextmanager
    def _transaction():
        s = Session()
        try:
            yield s
            s.commit()
        except SQLAlchemyError as e:
            bot_logger.exception(e)
            s.rollback()
            raise
        finally:
            s.close()

    @staticmethod
    @contextmanager
    def _session():
        s = Session()
        try:
            yield s
        except SQLAlchemyError as e:
            bot_logger.exception(e)
            raise
        finally:
            s.close()

    @abstractmethod
    def _get_model(self):
        raise NotImplementedError()

    def create(self, **kwargs):
        item = self.new(**kwargs)
        self.save(item)

    def new(self, **kwargs):
        return self._Model(**kwargs)

    def find(self, id_):
        with self._session() as s:
            return s.query(self._Model).filter_by(id=id_).first()

    @classmethod
    def update(cls, id_, **kwargs):
        with cls._transaction() as s:
            item = cls.find(id_)
            for key, value in kwargs.items():
                setattr(item, key, value)
                s.add(item)

    def find_all(self):
        with self._session() as s:
            return s.query(self._get_model()).all()

    @classmethod
    def save(cls, item):
        with cls._transaction() as s:
            s.add(item)


class OhlcPricesDao(DaoBase):
    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period

    def _get_model(self):
        return OhlcPrices

    def get_records(self, start_time, end_time, *, closed=False):
        with self._session() as s:
            result = s.query(self._Model).filter(
                and_(self._Model.time <= end_time,
                     self._Model.time > start_time,
                     self._Model.currency_pair == self._currency_pair,
                     self._Model.period == self._period,
                     self._Model.closed == int(closed)
                     )
            ).order_by(self._Model.time).all()
        return result


class OrderLogsDao(DaoBase):
    def _get_model(self):
        return OrderLogs
