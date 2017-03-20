from sqlalchemy import Column, Integer, Float, String

from zaifbot.models import Base


class BollingerBands(Base):
    __tablename__ = 'bollinger_bands'
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    period = Column('period', String, primary_key=True)
    length = Column('length', Integer, primary_key=True)
    sd1p = Column('sd1p', Float, nullable=False)
    sd2p = Column('sd2p', Float, nullable=False)
    sd3p = Column('sd3p', Float, nullable=False)
    sd1n = Column('sd1n', Float, nullable=False)
    sd2n = Column('sd2n', Float, nullable=False)
    sd3n = Column('sd3n', Float, nullable=False)
    closed = Column('closed', Integer, nullable=False)
