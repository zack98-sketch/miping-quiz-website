from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class QuestionType(str, enum.Enum):
    single = "single"   # 单选题
    multi = "multi"     # 多选题
    judge = "judge"     # 判断题


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False, index=True)
    difficulty = Column(Enum(Difficulty), nullable=False, default=Difficulty.medium, index=True)
    knowledge_point = Column(String(100), nullable=False, index=True)
    correct_answer = Column(String(200), nullable=False)
    explanation = Column(Text, nullable=True)
    source_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan", lazy="joined")
    corrections = relationship("Correction", back_populates="question", lazy="dynamic")


class Option(Base):
    __tablename__ = "options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    label = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    sort_order = Column(Integer, nullable=False)

    # Relationships
    question = relationship("Question", back_populates="options")
