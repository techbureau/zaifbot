from sqlalchemy import Column, Integer, Float, String
from zaifbot.models import Base


class _TradeLogBase:
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    open = Column('open', Float, nullable=False)
    high = Column('high', Float, nullable=False)
    low = Column('low', Float, nullable=False)
    close = Column('close', Float, nullable=False)
    average = Column('average', Float, nullable=False)
    volume = Column('volume', Float, nullable=False)
    closed = Column('closed', Integer, nullable=False)


class TradeLog1d(Base, _TradeLogBase):
    __tablename__ = "trade_logs_1d"


class TradeLog1h(Base, _TradeLogBase):
    __tablename__ = "trade_logs_1h"
