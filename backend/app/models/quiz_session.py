from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class QuizMode(str, enum.Enum):
    single = "single"       # 单题模式
    mixed = "mixed"         # 混合模式
    knowledge = "knowledge" # 知识点模式
    difficulty = "difficulty" # 难度模式
    error_book = "error_book" # 错题重做
    favorite = "favorite"   # 收藏练习


class SessionStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(Enum(QuizMode), nullable=False)
    total_count = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0)
    current_index = Column(Integer, default=0)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.in_progress)
    time_spent = Column(Integer, default=0)
    question_ids = Column(String(2000), nullable=False)  # JSON list of question IDs
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    answer_records = relationship("AnswerRecord", back_populates="session", cascade="all, delete-orphan", lazy="dynamic")


class AnswerRecord(Base):
    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    user_answer = Column(String(200), nullable=False)
    is_correct = Column(Integer, nullable=False)  # 1=correct, 0=incorrect
    time_spent = Column(Integer, default=0)
    answered_at = Column(DateTime, server_default=func.now())

    # Relationships
    session = relationship("QuizSession", back_populates="answer_records")
    question = relationship("Question")
