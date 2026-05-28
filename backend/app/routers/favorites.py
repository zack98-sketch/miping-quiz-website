import json
import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Favorite, Question, QuizSession, SessionStatus, QuizMode, User
from app.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/favorites", tags=["收藏"])


@router.post("")
def add_favorite(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.question_id == question_id).first()
    if existing:
        return {"message": "已收藏"}
    fav = Favorite(user_id=current_user.id, question_id=question_id)
    db.add(fav)
    db.commit()
    return {"message": "收藏成功"}


@router.delete("/{question_id}")
def remove_favorite(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.question_id == question_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="未收藏该题")
    db.delete(fav)
    db.commit()
    return {"message": "取消收藏成功"}


@router.get("")
def get_favorites(
    knowledge_point: Optional[str] = None,
    question_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)
    if knowledge_point:
        query = query.join(Question).filter(Question.knowledge_point == knowledge_point)
    if question_type:
        query = query.join(Question).filter(Question.question_type == question_type)
    
    total = query.count()
    favs = query.order_by(Favorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for fav in favs:
        q = db.query(Question).filter(Question.id == fav.question_id).first()
        items.append({
            "id": fav.id,
            "question_id": fav.question_id,
            "created_at": fav.created_at.isoformat() if fav.created_at else None,
            "question_content": q.content if q else None,
            "question_type": q.question_type.value if q and q.question_type else None,
            "knowledge_point": q.knowledge_point if q else None,
            "difficulty": q.difficulty.value if q and q.difficulty else None,
            "correct_answer": q.correct_answer if q else None,
            "explanation": q.explanation if q else None,
            "options": [
                {"id": o.id, "label": o.label, "content": o.content}
                for o in sorted(q.options, key=lambda x: x.sort_order)
            ] if q else [],
        })
    
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("/practice")
def practice_favorites(question_ids: list[int], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not question_ids:
        # Get all favorite question IDs
        favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
        question_ids = [f.question_id for f in favs]
    
    if not question_ids:
        raise HTTPException(status_code=404, detail="没有可练习的收藏题目")
    
    session = QuizSession(
        user_id=current_user.id,
        mode=QuizMode.favorite,
        total_count=len(question_ids),
        question_ids=json.dumps(question_ids),
        status=SessionStatus.in_progress,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {"session_id": session.id, "total_count": len(question_ids), "mode": "favorite"}


@router.get("/check/{question_id}")
def check_favorite(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    is_favorited = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.question_id == question_id).first() is not None
    return {"is_favorited": is_favorited}
