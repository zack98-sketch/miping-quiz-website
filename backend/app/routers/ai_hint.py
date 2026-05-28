from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AIHintRecord, Question, SystemConfig, HintLevel, User
from app.schemas.ai import AIHintRequest, AIHintResponse
from app.dependencies import get_current_user
from app.config import settings

router = APIRouter(prefix="/api/ai-hint", tags=["AI提示"])


@router.post("/request")
def request_hint(data: AIHintRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Check limit
    used_count = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.question_id == data.question_id,
    ).count()
    
    limit = settings.AI_HINT_LIMIT_PER_QUESTION
    if used_count >= limit:
        raise HTTPException(status_code=429, detail="本题提示次数已用完")
    
    remaining = limit - used_count - 1
    
    # Generate hint
    if not settings.AI_API_KEY or not settings.AI_API_ENDPOINT:
        # Fallback: generate basic hint from question data
        hint_content = _generate_fallback_hint(question, data.level)
    else:
        try:
            hint_content = _generate_ai_hint(question, data.level)
        except Exception:
            hint_content = _generate_fallback_hint(question, data.level)
    
    # Record
    record = AIHintRecord(
        user_id=current_user.id,
        question_id=data.question_id,
        hint_level=data.level,
        hint_content=hint_content,
    )
    db.add(record)
    db.commit()
    
    return AIHintResponse(
        hint_content=hint_content,
        hint_level=data.level,
        remaining_count=remaining,
    )


@router.get("/usage")
def get_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(AIHintRecord).filter(AIHintRecord.user_id == current_user.id).count()
    return {"total_hints_used": total}


@router.get("/remaining/{question_id}")
def get_remaining(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    used = db.query(AIHintRecord).filter(
        AIHintRecord.user_id == current_user.id,
        AIHintRecord.question_id == question_id,
    ).count()
    return {"remaining": settings.AI_HINT_LIMIT_PER_QUESTION - used}


def _generate_fallback_hint(question: Question, level: HintLevel) -> str:
    kp = question.knowledge_point
    if level == HintLevel.light:
        return f"这道题涉及的知识点是「{kp}」，请回顾相关概念和基本原理。"
    elif level == HintLevel.medium:
        qt = question.question_type.value
        return f"这道题是{qt}，涉及知识点「{kp}」。请仔细分析每个选项，排除明显不合理的选项，注意题目中的关键词。"
    else:
        return f"这道题涉及知识点「{kp}」。建议从基本定义出发，逐步推导。注意题目中的限定条件和特殊表述，这些往往是解题的关键线索。"


def _generate_ai_hint(question: Question, level: HintLevel) -> str:
    # Placeholder for actual AI API call
    import httpx
    level_text = {"light": "轻度", "medium": "中度", "deep": "深度"}[level.value]
    prompt = f"请为以下题目提供{level_text}提示（不要直接给出答案）：\n{question.content}"
    
    # This would call the actual AI API
    # For now, return fallback
    return _generate_fallback_hint(question, level)
