from sqlalchemy import Column, Integer, Float, Boolean

from zaifbot.models import Base


class AutoTrade(Base):
    __tablename__ = 'auto_trade'
    start_time = Column('start_time', Integer, primary_key=True)
    sell_active = Column('sell_active', Boolean, nullable=False)
    buy_active = Column('buy_active', Boolean, nullable=False)
    to_currency_amount = Column('to_currency_amount', Float, nullable=False)
    from_currency_amount = Column('from_currency_amount', Float, nullable=False)