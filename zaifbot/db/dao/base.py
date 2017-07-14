from abc import ABCMeta, abstractmethod
from contextlib import contextmanager

from sqlalchemy.exc import SQLAlchemyError

from zaifbot.db.config import Session
from zaifbot.logger import bot_logger


class DaoBase(metaclass=ABCMeta):
    # todo transaction実装を見直す。
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
        return self.save(item)

    def create_multiple(self, items):
        with self._transaction() as s:
            for item in items:
                new_record = self.new(**item)
                s.merge(new_record)

    def new(self, **kwargs):
        return self._Model(**kwargs)

    def find(self, id_):
        with self._session() as s:
            return s.query(self._Model).filter_by(id=id_).first()

    def update(self, id_, **kwargs):
        with self._transaction() as s:
            item = self.find(id_)
            for key, value in kwargs.items():
                setattr(item, key, value)
                s.merge(item)

    def find_all(self):
        with self._session() as s:
            return s.query(self._Model).all()

    @classmethod
    def save(cls, item):
        with cls._session() as s:
            s.add(item)
            s.commit()
            s.refresh(item)
            return item
