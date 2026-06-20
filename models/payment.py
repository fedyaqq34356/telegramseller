from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Float, ForeignKey
from datetime import datetime
from config.database import Base


class Payment(Base):
    __tablename__ = 'payments'

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    amount = Column(Float)
    currency = Column(String(10), nullable=True)
    payment_method = Column(String(20))  # crypto, stars
    transaction_hash = Column(String(255), nullable=True)
    invoice_id = Column(String(255), nullable=True)
    subscription_type = Column(String(50))
    subscription_period = Column(Integer)  # months
    tariff = Column(String(50), nullable=True)
    status = Column(String(20), default='pending')  # pending, confirmed, rejected
    created_date = Column(DateTime, default=datetime.utcnow)