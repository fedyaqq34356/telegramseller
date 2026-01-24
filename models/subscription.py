from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Boolean, ForeignKey, Float
from datetime import datetime
from config.database import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    subscription_type = Column(String(50)) 
    tariff = Column(String(50), nullable=True) 
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)


class Tariff(Base):
    __tablename__ = 'tariffs'

    tariff_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    views_count = Column(Integer)
    reactions_count = Column(Integer)
    price_1m = Column(Float)
    price_3m = Column(Float)
    price_6m = Column(Float)
    price_12m = Column(Float)