from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    quiz_sessions = relationship("QuizSession", back_populates="user", lazy="dynamic")
    error_book_items = relationship("ErrorBookItem", back_populates="user", lazy="dynamic")
    favorites = relationship("Favorite", back_populates="user", lazy="dynamic")
    corrections = relationship("Correction", back_populates="user", lazy="dynamic", foreign_keys="Correction.user_id")
    notes = relationship("Note", back_populates="user", lazy="dynamic")
    exam_participations = relationship("ExamParticipation", back_populates="user", lazy="dynamic")
