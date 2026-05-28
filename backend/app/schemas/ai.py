from pydantic import BaseModel
from app.models.ai_hint import HintLevel


class AIHintRequest(BaseModel):
    question_id: int
    level: HintLevel = HintLevel.light


class AIHintResponse(BaseModel):
    hint_content: str
    hint_level: HintLevel
    remaining_count: int
