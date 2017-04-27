from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from zaifbot.models import Base


class Nonce(Base):
    __tablename__ = 'nonces'
    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    nonce = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
