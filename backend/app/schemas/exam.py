from pydantic import BaseModel
from datetime import datetime


class ExamCreate(BaseModel):
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    time_limit: int  # minutes
    question_config: dict  # {"types": [...], "count": N, "knowledge_points": [...]}


class ExamResponse(BaseModel):
    id: int
    title: str
    description: str | None
    start_time: datetime
    end_time: datetime
    time_limit: int
    question_config: dict
    is_active: bool
    created_at: datetime
    # Computed
    status: str | None = None  # upcoming/ongoing/ended
    has_participated: bool = False

    class Config:
        from_attributes = True


class ExamSubmitAnswer(BaseModel):
    question_id: int
    answer: str


class ExamParticipationResponse(BaseModel):
    id: int
    exam_id: int
    score: float | None
    correct_count: int | None
    total_count: int | None
    time_spent: int | None
    submitted_at: datetime | None

    class Config:
        from_attributes = True
