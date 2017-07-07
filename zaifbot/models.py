from sqlalchemy import Column, Integer, Float, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from zaifbot.common.database import metadata

Base = declarative_base(metadata=metadata)


class OhlcPrices(Base):
    __tablename__ = 'ohlc_prices'
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


class OrderLogs(Base):
    __tablename__ = 'order_logs'
    order_id = Column('id', Integer, primary_key=True)
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    action = Column('action', String, nullable=False)
    price = Column('price', Float, nullable=False)
    amount = Column('amount', Float, nullable=False)
    limit = Column('limit', Float)
    received = Column('received', Float)
    remains = Column('remains', Float)
    comment = Column('comment', Text)


