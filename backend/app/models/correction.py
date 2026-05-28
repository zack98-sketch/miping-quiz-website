from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class CorrectionType(str, enum.Enum):
    content = "content"         # 题目内容错误
    option = "option"           # 选项错误
    answer = "answer"           # 答案错误
    explanation = "explanation" # 解析错误
    other = "other"             # 其他


class CorrectionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Correction(Base):
    __tablename__ = "corrections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False, index=True)
    correction_type = Column(Enum(CorrectionType), nullable=False)
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    status = Column(Enum(CorrectionStatus), nullable=False, default=CorrectionStatus.pending)
    admin_comment = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="corrections", foreign_keys="Correction.user_id")
    reviewer = relationship("User", foreign_keys="Correction.reviewed_by")
    question = relationship("Question", back_populates="corrections")
