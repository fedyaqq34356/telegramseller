from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from config.database import Base


class AdminSettings(Base):
    __tablename__ = 'admin_settings'

    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), unique=True)
    setting_value = Column(Text)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CryptoWallet(Base):
    __tablename__ = 'crypto_wallets'

    wallet_id = Column(Integer, primary_key=True, autoincrement=True)
    currency_name = Column(String(20))
    wallet_address = Column(String(255))
    is_active = Column(Boolean, default=True)


class PostQueue(Base):
    __tablename__ = 'posts_queue'

    queue_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    channel_id = Column(Integer, ForeignKey('channels.channel_id'))
    content_type = Column(String(20))
    content = Column(Text)  # JSON
    scheduled_time = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed


class CirclesUsage(Base):
    __tablename__ = 'video_circles_usage'

    usage_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    date = Column(DateTime, default=datetime.utcnow)
    count = Column(Integer, default=1)


class PostingUsage(Base):
    __tablename__ = 'posting_usage'

    usage_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    date = Column(DateTime, default=datetime.utcnow)
    count = Column(Integer, default=1)