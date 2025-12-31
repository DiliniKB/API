from sqlalchemy import Column, String, DateTime, Date, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    
    # Birth info for astrology
    birth_date = Column(Date)
    birth_time = Column(Time)
    birth_location = Column(String(255))
    timezone = Column(String(50), default="UTC")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    entities = relationship("Entity", back_populates="user", cascade="all, delete-orphan")
    context_windows = relationship("ContextWindow", back_populates="user", cascade="all, delete-orphan")
    user_patterns = relationship("UserPattern", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan") 
