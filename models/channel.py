from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, JSON, Boolean
from datetime import datetime
from config.database import Base


class Channel(Base):
    __tablename__ = 'channels'

    channel_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    channel_username = Column(String(255))
    channel_title = Column(String(255))
    channel_tg_id = Column(BigInteger)
    added_date = Column(DateTime, default=datetime.utcnow)


class UserBot(Base):
    __tablename__ = 'user_bots'

    bot_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    bot_token = Column(String(255))
    bot_username = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)


class ReactionsSettings(Base):
    __tablename__ = 'reactions_settings'

    settings_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    channel_id = Column(Integer, ForeignKey('channels.channel_id'))
    reaction_pool = Column(JSON)
    interval_minutes = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)