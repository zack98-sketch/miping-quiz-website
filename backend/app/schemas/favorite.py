from pydantic import BaseModel
from datetime import datetime


class FavoriteCreate(BaseModel):
    question_id: int


class FavoriteResponse(BaseModel):
    id: int
    question_id: int
    created_at: datetime
    # Question info
    question_content: str | None = None
    question_type: str | None = None
    knowledge_point: str | None = None
    difficulty: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    options: list[dict] | None = None

    class Config:
        from_attributes = True
