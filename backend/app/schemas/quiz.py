from pydantic import BaseModel
from datetime import datetime
from app.models.question import QuestionType, Difficulty
from app.models.quiz_session import QuizMode, SessionStatus


class QuizSessionCreate(BaseModel):
    mode: QuizMode
    count: int = 10
    question_types: list[QuestionType] | None = None
    knowledge_points: list[str] | None = None
    difficulty: Difficulty | None = None
    question_ids: list[int] | None = None  # For error_book/favorite mode


class AnswerSubmit(BaseModel):
    question_id: int
    answer: str
    time_spent: int = 0  # seconds


class AnswerRecordResponse(BaseModel):
    id: int
    question_id: int
    user_answer: str
    is_correct: int
    time_spent: int
    answered_at: datetime
    question_content: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None

    class Config:
        from_attributes = True


class QuizSessionResponse(BaseModel):
    id: int
    mode: QuizMode
    total_count: int
    correct_count: int
    current_index: int
    status: SessionStatus
    time_spent: int
    started_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class QuizResultResponse(BaseModel):
    session: QuizSessionResponse
    answers: list[AnswerRecordResponse]
    accuracy: float
    error_questions: list[dict]


class CurrentQuestionResponse(BaseModel):
    question_index: int
    total_count: int
    question: dict  # QuestionResponse as dict
    is_answered: bool = False
    user_answer: str | None = None
    is_correct: int | None = None
