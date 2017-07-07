from contextlib import contextmanager
from sqlalchemy import Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from zaifbot.common.database import engine


Session = sessionmaker(bind=engine)


@contextmanager
def transaction():
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


class ActiveRecord(object):

    id = Column(Integer, primary_key=True)

    @classmethod
    def find(cls, id_):
        session = cls._get_session()
        return session.query(cls).filter_by(id=id_).first()

    @classmethod
    def find_by(cls, **kwargs):
        session = cls._get_session()
        return session.query(cls).filter_by(**kwargs).first()

    def insert(self):
        session = self._get_session()
        session.add(self)
        return self.id

    def update(self, id_, **kwargs):
        session = self._get_session()
        entry = self.find(id_)
        for key, value in kwargs.items():
            setattr(entry, key, value)
        session.add(entry)

    def delete(self):
        session = self._get_session()
        session.delete(self)

    @classmethod
    def _get_session(cls):
        return Session()
