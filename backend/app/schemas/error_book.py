from pydantic import BaseModel
from datetime import datetime
from app.models.error_book import MasteryStatus


class ErrorBookItemResponse(BaseModel):
    id: int
    question_id: int
    user_answer: str | None
    personal_note: str | None
    mastery_status: MasteryStatus
    error_count: int
    last_error_at: datetime
    created_at: datetime
    # Question info
    question_content: str | None = None
    question_type: str | None = None
    knowledge_point: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    options: list[dict] | None = None

    class Config:
        from_attributes = True


class ErrorBookUpdate(BaseModel):
    personal_note: str | None = None
    mastery_status: MasteryStatus | None = None


class ErrorBookPractice(BaseModel):
    item_ids: list[int] | None = None
    count: int | None = None  # Random count
