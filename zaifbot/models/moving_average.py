from sqlalchemy import Column, Integer, Float, String

from zaifbot.models import Base


class MovingAverages(Base):
    __tablename__ = 'moving_averages'
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    period = Column('period', String, primary_key=True)
    length = Column('length', Integer, primary_key=True)
    sma = Column('sma', Float, nullable=False)
    ema = Column('ema', Float, nullable=False)
    closed = Column('closed', Integer, nullable=False)
