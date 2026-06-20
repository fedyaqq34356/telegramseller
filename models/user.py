from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Float
from datetime import datetime
from config.database import Base


class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    language = Column(String(10), default='ru')  # ru/en
    system_language = Column(String(10), nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    demo_used = Column(Boolean, default=False)
    total_earned = Column(Float, default=0.0)
    is_blocked = Column(Boolean, default=False)