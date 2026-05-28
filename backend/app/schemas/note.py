acfrom pydantic import BaseModel
from datetime import datetime


class NoteCreate(BaseModel):
    question_id: int
    content: str


class NoteResponse(BaseModel):
    id: int
    question_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    # Question info
    question_content: str | None = None
    question_type: str | None = None
    knowledge_point: str | None = None

    class Config:
        from_attributes = True
