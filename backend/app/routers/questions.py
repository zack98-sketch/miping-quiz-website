from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from app.database import get_db
from app.models import Question, Option, QuestionType, Difficulty, User, UserRole
from app.schemas.question import QuestionResponse, QuestionStats, OptionResponse
from app.dependencies import get_current_user, require_admin
from typing import Optional

router = APIRouter(prefix="/api/questions", tags=["题库"])


@router.get("")
def get_questions(
    question_type: Optional[str] = None,
    knowledge_point: Optional[str] = None,
    difficulty: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Question).filter(Question.is_active == True)
    if question_type:
        try:
            qt = QuestionType(question_type)
            query = query.filter(Question.question_type == qt)
        except ValueError:
            pass
    if knowledge_point:
        query = query.filter(Question.knowledge_point == knowledge_point)
    if difficulty:
        try:
            d = Difficulty(difficulty)
            query = query.filter(Question.difficulty == d)
        except ValueError:
            pass
    if keyword:
        query = query.filter(Question.content.contains(keyword))
    total = query.count()
    questions = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_question_to_dict(q) for q in questions],
    }


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Question).filter(Question.is_active == True).count()
    single_count = db.query(Question).filter(Question.question_type == QuestionType.single, Question.is_active == True).count()
    multi_count = db.query(Question).filter(Question.question_type == QuestionType.multi, Question.is_active == True).count()
    judge_count = db.query(Question).filter(Question.question_type == QuestionType.judge, Question.is_active == True).count()
    
    # Knowledge points
    kp_rows = db.query(Question.knowledge_point, func.count(Question.id)).filter(Question.is_active == True).group_by(Question.knowledge_point).all()
    knowledge_points = {row[0]: row[1] for row in kp_rows if row[0]}
    
    # Difficulties
    diff_rows = db.query(Question.difficulty, func.count(Question.id)).filter(Question.is_active == True).group_by(Question.difficulty).all()
    difficulties = {row[0].value if row[0] else "unknown": row[1] for row in diff_rows}
    
    return QuestionStats(
        total=total, single_count=single_count, multi_count=multi_count, judge_count=judge_count,
        knowledge_points=knowledge_points, difficulties=difficulties,
    )


@router.get("/knowledge-points")
def get_knowledge_points(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    kps = db.query(Question.knowledge_point).filter(Question.is_active == True).distinct().all()
    return {"knowledge_points": [kp[0] for kp in kps if kp[0]]}


@router.get("/search")
def search_questions(
    keyword: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """模糊搜索题目、答案、解析"""
    like_pattern = f"%{keyword}%"
    query = db.query(Question).filter(
        Question.is_active == True,
        or_(
            Question.content.like(like_pattern),
            Question.correct_answer.like(like_pattern),
            Question.explanation.like(like_pattern),
            Question.knowledge_point.like(like_pattern),
        )
    )
    total = query.count()
    questions = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_question_to_dict(q) for q in questions],
    }


@router.get("/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    return _question_to_dict(q, include_answer=True)


def _question_to_dict(q: Question, include_answer: bool = False):
    result = {
        "id": q.id,
        "content": q.content,
        "question_type": q.question_type.value if q.question_type else None,
        "difficulty": q.difficulty.value if q.difficulty else None,
        "knowledge_point": q.knowledge_point,
        "options": [
            {"id": o.id, "label": o.label, "content": o.content, "sort_order": o.sort_order}
            for o in sorted(q.options, key=lambda x: x.sort_order)
        ],
    }
    if include_answer:
        result["correct_answer"] = q.correct_answer
        result["explanation"] = q.explanation
    return result
