from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    time_limit = Column(Integer, nullable=False)  # minutes
    question_config = Column(JSON, nullable=False)  # {"types": [...], "count": N, "knowledge_points": [...]}
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    participations = relationship("ExamParticipation", back_populates="exam", lazy="dynamic")


class ExamParticipation(Base):
    __tablename__ = "exam_participations"
    __table_args__ = (UniqueConstraint("exam_id", "user_id", name="uq_exam_user"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    score = Column(Float, nullable=True)
    correct_count = Column(Integer, nullable=True)
    total_count = Column(Integer, nullable=True)
    time_spent = Column(Integer, nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    # Relationships
    exam = relationship("Exam", back_populates="participations")
    user = relationship("User", back_populates="exam_participations")
    answers = relationship("ExamAnswer", back_populates="participation", cascade="all, delete-orphan", lazy="dynamic")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    participation_id = Column(Integer, ForeignKey("exam_participations.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(200), nullable=True)
    is_correct = Column(Integer, nullable=True)  # 1=correct, 0=incorrect

    # Relationships
    participation = relationship("ExamParticipation", back_populates="answers")
    question = relationship("Question")
