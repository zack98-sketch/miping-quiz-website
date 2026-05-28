from pydantic import BaseModel
from datetime import datetime
from app.models.question import QuestionType, Difficulty


class OptionResponse(BaseModel):
    id: int
    label: str
    content: str
    sort_order: int

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: int
    content: str
    question_type: QuestionType
    difficulty: Difficulty
    knowledge_point: str
    correct_answer: str
    explanation: str | None
    options: list[OptionResponse] = []
    is_favorited: bool = False
    has_note: bool = False

    class Config:
        from_attributes = True


class QuestionBrief(BaseModel):
    id: int
    content: str
    question_type: QuestionType
    difficulty: Difficulty
    knowledge_point: str

    class Config:
        from_attributes = True


class QuestionStats(BaseModel):
    total: int
    single_count: int
    multi_count: int
    judge_count: int
    knowledge_points: dict[str, int]
    difficulties: dict[str, int]


class QuestionFilter(BaseModel):
    question_type: QuestionType | None = None
    knowledge_point: str | None = None
    difficulty: Difficulty | None = None
    keyword: str | None = None
    page: int = 1
    page_size: int = 20
