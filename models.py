from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Связь многие-ко-многим между пользователями и каналами
user_subscribed_channels = Table(
    'user_subscribed_channels',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('channel_id', Integer, ForeignKey('channels.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String)
    last_name = Column(String, nullable=True)
    
    # Настройки пользователя
    target_chat_id = Column(Integer, nullable=True)  # Куда отправлять новости
    
    # Связи
    filters = relationship("Filter", back_populates="user", cascade="all, delete-orphan")
    subscribed_channels = relationship("Channel", secondary=user_subscribed_channels, back_populates="subscribers")

class Filter(Base):
    __tablename__ = "filters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)  # Название фильтра
    keywords = Column(Text)  # Ключевые слова через запятую
    theme = Column(String, nullable=True)  # Тема (опционально)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="filters")

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String, unique=True, nullable=True)
    title = Column(String)
    is_public = Column(Boolean, default=True)  # Доступен ли для подписки всем
    
    subscribers = relationship("User", secondary=user_subscribed_channels, back_populates="subscribed_channels")