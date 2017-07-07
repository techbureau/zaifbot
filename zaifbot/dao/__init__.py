from abc import ABCMeta, abstractmethod
from contextlib import contextmanager
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from zaifbot.common.database import Session
from zaifbot.models import OrderLogs, OhlcPrices
from zaifbot.common.logger import bot_logger


@contextmanager
def transaction():
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        bot_logger.exception(e)
        session.rollback()
        raise
    finally:
        session.close()


class DaoBase(metaclass=ABCMeta):
    _CLOSED = 1

    def __init__(self):
        self._Model = self._get_model()

    @classmethod
    def _get_session(cls):
        return Session()

    @abstractmethod
    def _get_model(self):
        raise NotImplementedError()

    def create(self, **kwargs):
        item = self.new(**kwargs)
        self.save(item)

    def delete(self, id_):
        self.find(id_).delete()

    def new(self, **kwargs):
        return self._Model(kwargs)

    def find(self, id_):
        session = self._get_session()
        return session.query(self._get_model()).filter_by(id=id_).first()

    @classmethod
    def update(cls, id_, **kwargs):
        session = cls._get_session()
        item = cls.find(id_)
        for key, value in kwargs.items():
            setattr(item, key, value)
        session.add(item)
        session.commit()

    def find_all(self):
        session = self._get_session()
        session.query(self._get_model()).all()

    @classmethod
    def save(cls, item):
        session = cls._get_session()
        session.add(item)
        # todo: flushとは何ぞや
        # session.flush()
        session.commit()


class OhlcPricesDao(DaoBase):

    def __init__(self, currency_pair, period):
        super().__init__()
        self._currency_pair = currency_pair
        self._period = period

    def _get_model(self):
        return OhlcPrices

    def get_record(self, select_query):
        return select_query.order_by(self._Model.time).all()

    def create_data(self, ohlc_prices):
        session = self._get_session()
        try:
            for record in ohlc_prices:
                record['currency_pair'] = self._currency_pair
                record['period'] = self._period
                session.merge(OhlcPrices(**record))
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            bot_logger.exception(e)
            session.rollback()
            session.close()
        return False

    def get_records(self, end_time, start_time, closed):
        session = self._get_session()
        select_query = session.query(self._Model)
        if closed:
            select_query = select_query.filter(and_(self._Model.time <= end_time,
                                                    self._Model.time > start_time,
                                                    self._Model.currency_pair == self._currency_pair,
                                                    self._Model.period == self._period,
                                                    self._Model.closed == self._CLOSED
                                                    ))
        else:
            select_query = select_query.filter(and_(self._Model.time <= end_time,
                                                    self._Model.time >= start_time,
                                                    self._Model.currency_pair == self._currency_pair,
                                                    self._Model.period == self._period
                                                    ))
        result = select_query.order_by(self._Model.time).all()
        session.close()
        return result


class OrderLogsDao(DaoBase):
    def _get_model(self):
        return OrderLogs

    def create_data(self, order_log):
        session = self._get_session()
        session.merge(OrderLogs(**order_log))
        try:
            session.commit()
            session.close()
            return True
        except SQLAlchemyError as e:
            bot_logger.exception(e)
            session.rollback()
            session.close()
        return False
