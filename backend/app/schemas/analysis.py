from pydantic import BaseModel
from datetime import datetime


class MasteryAnalysis(BaseModel):
    knowledge_point: str
    total_count: int
    correct_count: int
    error_count: int
    mastery_rate: float  # percentage


class WeakPoint(BaseModel):
    knowledge_point: str
    mastery_rate: float
    total_count: int
    error_count: int


class LearningProgress(BaseModel):
    total_questions: int
    total_correct: int
    total_errors: int
    overall_accuracy: float
    study_days: int
    total_sessions: int


class TrendData(BaseModel):
    date: str
    accuracy: float
    count: int


class HistoryRecord(BaseModel):
    session_id: int
    mode: str
    total_count: int
    correct_count: int
    accuracy: float
    time_spent: int
    started_at: datetime
    completed_at: datetime | None


class PracticeRecommendation(BaseModel):
    knowledge_point: str
    reason: str
    question_count: int
