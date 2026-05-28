from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MasteryStatus(str, enum.Enum):
    not_mastered = "not_mastered"
    partially = "partially"
    mastered = "mastered"


class ErrorBookItem(Base):
    __tablename__ = "error_book_items"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_error_book_user_question"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    user_answer = Column(String(200), nullable=True)
    personal_note = Column(Text, nullable=True)
    mastery_status = Column(Enum(MasteryStatus), default=MasteryStatus.not_mastered)
    error_count = Column(Integer, default=1)
    last_error_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="error_book_items")
    question = relationship("Question")
