from sqlalchemy import Column, Integer, Float, String, Boolean
from zaifbot.models import Base


class Trade(Base):
    __tablename__ = 'trades'
    currency_pair = Column('currency_pair', String, primary_key=True)
    amount = Column('amount', Float, nullable=False)
    action = Column('action', String, nullable=False)
    entry_price = Column('entry_price', Float, nullable=False)
    entry_time = Column('entry_time', Integer, primary_key=False)
    exit_price = Column('exit_price', Float, nullable=True)
    exit_time = Column('exit_time', Integer, primary_key=False)
    profit = Column('profit', Float, nullable=True)
    closed = Column('closed', Boolean, nullable=False)
