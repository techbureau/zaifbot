from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime

from zaifbot.db.config import Base
import datetime
import os


class Trades(Base):
    __tablename__ = 'trades'
    id_ = Column('id_', Integer, primary_key=True, autoincrement=True)
    currency_pair = Column('currency_pair', String, nullable=False)
    amount = Column('amount', Float, nullable=False)
    action = Column('action', String, nullable=False)
    entry_price = Column('entry_price', Float, nullable=False)
    entry_datetime = Column('entry_time', DateTime, default=datetime.datetime.now(), nullable=False)
    exit_price = Column('exit_price', Float)
    exit_datetime = Column('exit_time', DateTime)
    strategy_name = Column('strategy_name', String, nullable=True)
    process_id = Column('process_id', String, nullable=True)
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
    db = os.path.join(os.path.dirname(__file__), 'zaifbot.db')
    if os.path.exists(db):
        print('Database already exists')
        return
    Base.metadata.create_all()
    print('Database was created, successfully ')


def clear_database():
    db = os.path.join(os.path.dirname(__file__), 'zaifbot.db')
    if not os.path.exists(db):
        print("you haven't created db yet, run init_database")
        return

    answer = input('Really want to clear db? All trade data will lost [y/n]')
    if answer in ('y', 'yes'):
        os.remove(db)
        print('Database was deleted, successfully')
        return True
    print('canceled')
    return False


def refresh_database():
    if clear_database():
        init_database()
