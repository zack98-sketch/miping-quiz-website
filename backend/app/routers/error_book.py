import random
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ErrorBookItem, Question, QuizSession, SessionStatus, QuizMode, MasteryStatus, User
from app.schemas.error_book import ErrorBookUpdate, ErrorBookPractice
from app.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/error-book", tags=["错题本"])


@router.get("")
def get_error_book(
    knowledge_point: Optional[str] = None,
    question_type: Optional[str] = None,
    mastery_status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ErrorBookItem).filter(ErrorBookItem.user_id == current_user.id)
    if knowledge_point:
        query = query.join(Question).filter(Question.knowledge_point == knowledge_point)
    if question_type:
        query = query.join(Question).filter(Question.question_type == question_type)
    if mastery_status:
        try:
            ms = MasteryStatus(mastery_status)
            query = query.filter(ErrorBookItem.mastery_status == ms)
        except ValueError:
            pass
    
    total = query.count()
    items = query.order_by(ErrorBookItem.last_error_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    result_items = []
    for item in items:
        q = db.query(Question).filter(Question.id == item.question_id).first()
        result_items.append({
            "id": item.id,
            "question_id": item.question_id,
            "user_answer": item.user_answer,
            "personal_note": item.personal_note,
            "mastery_status": item.mastery_status.value if item.mastery_status else None,
            "error_count": item.error_count,
            "last_error_at": item.last_error_at.isoformat() if item.last_error_at else None,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "question_content": q.content if q else None,
            "question_type": q.question_type.value if q and q.question_type else None,
            "knowledge_point": q.knowledge_point if q else None,
            "correct_answer": q.correct_answer if q else None,
            "explanation": q.explanation if q else None,
            "options": [
                {"id": o.id, "label": o.label, "content": o.content}
                for o in sorted(q.options, key=lambda x: x.sort_order)
            ] if q else [],
        })
    
    return {"total": total, "page": page, "page_size": page_size, "items": result_items}


@router.put("/{item_id}")
def update_error_book_item(item_id: int, data: ErrorBookUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ErrorBookItem).filter(ErrorBookItem.id == item_id, ErrorBookItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    if data.personal_note is not None:
        item.personal_note = data.personal_note
    if data.mastery_status is not None:
        item.mastery_status = data.mastery_status
    db.commit()
    return {"message": "更新成功"}


@router.delete("/{item_id}")
def delete_error_book_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(ErrorBookItem).filter(ErrorBookItem.id == item_id, ErrorBookItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    db.delete(item)
    db.commit()
    return {"message": "删除成功"}


@router.post("/practice")
def practice_error_book(data: ErrorBookPractice, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(ErrorBookItem).filter(ErrorBookItem.user_id == current_user.id)
    
    if data.item_ids:
        items = query.filter(ErrorBookItem.id.in_(data.item_ids)).all()
    else:
        items = query.all()
    
    if not items:
        raise HTTPException(status_code=404, detail="没有可练习的错题")
    
    if data.count:
        items = random.sample(items, min(data.count, len(items)))
    
    question_ids = [item.question_id for item in items]
    
    session = QuizSession(
        user_id=current_user.id,
        mode=QuizMode.error_book,
        total_count=len(question_ids),
        question_ids=json.dumps(question_ids),
        status=SessionStatus.in_progress,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"session_id": session.id, "total_count": len(question_ids), "mode": "error_book"}


@router.get("/stats")
def get_error_book_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from sqlalchemy import func
    # Stats by knowledge point
    rows = db.query(
        Question.knowledge_point,
        func.count(ErrorBookItem.id),
    ).join(Question, ErrorBookItem.question_id == Question.id).filter(
        ErrorBookItem.user_id == current_user.id,
    ).group_by(Question.knowledge_point).all()
    
    return {
        "total_errors": sum(r[1] for r in rows),
        "by_knowledge_point": {r[0]: r[1] for r in rows if r[0]},
    }
