from sqlalchemy import Column, Integer, Float, String

from zaifbot.models import Base


class OrderLogs(Base):
    __tablename__ = 'order_logs'
    id = Column('id', Integer, primary_key=True)
    time = Column('time', Integer, primary_key=True)
    currency_pair = Column('currency_pair', String, primary_key=True)
    action = Column('action', String, nullable=False)
    price = Column('price', Float, nullable=False)
    amount = Column('amount', Float, nullable=False)
    limit = Column('limit', Float)
    received = Column('received', Float)
    remains = Column('remains', Float)
