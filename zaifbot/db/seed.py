from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime

from zaifbot.db.config import Base
import datetime


class Trades(Base):
    __tablename__ = 'trades'
    id_ = Column('id_', Integer, primary_key=True, autoincrement=True)
    currency_pair = Column('currency_pair', String, nullable=False)
    amount = Column('amount', Float, nullable=False)
    action = Column('action', String, nullable=False)
    entry_price = Column('entry_price', Float, nullable=False)
    entry_datetime = Column('entry_time', DateTime, default=datetime.datetime.now(), nullable=False)
    exit_price = Column('exit_price', Float)
    exit_datetime = Column('exit_time', DateTime, default=datetime.datetime.now())
    profit = Column('profit', Float)
    closed = Column('closed', Boolean, default=False, nullable=False)


class CandleSticks(Base):
    __tablename__ = 'candle_sticks'
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    period = Column('period', String, primary_key=True)
    open = Column('open', Float, nullable=False)
    high = Column('high', Float, nullable=False)
    low = Column('low', Float, nullable=False)
    close = Column('close', Float, nullable=False)
    average = Column('average', Float, nullable=False)
    volume = Column('volume', Float, nullable=False)
    closed = Column('closed', Boolean, nullable=False)


def init_database():
    Base.metadata.create_all()