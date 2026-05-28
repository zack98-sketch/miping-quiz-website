from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Correction, Question, CorrectionType, CorrectionStatus, User, UserRole
from app.schemas.correction import CorrectionCreate, CorrectionReview
from app.dependencies import get_current_user, require_admin
from typing import Optional

router = APIRouter(prefix="/api/corrections", tags=["纠错"])


@router.post("")
def submit_correction(data: CorrectionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # 24-hour limit
    recent = db.query(Correction).filter(
        Correction.user_id == current_user.id,
        Correction.question_id == data.question_id,
        Correction.created_at >= datetime.utcnow() - timedelta(hours=24),
    ).first()
    if recent:
        raise HTTPException(status_code=429, detail="您已提交过纠错，请等待审核")
    
    correction = Correction(
        user_id=current_user.id,
        question_id=data.question_id,
        correction_type=data.correction_type,
        description=data.description,
        suggestion=data.suggestion,
    )
    db.add(correction)
    db.commit()
    return {"message": "纠错提交成功", "id": correction.id}


@router.get("/my")
def get_my_corrections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Correction).filter(Correction.user_id == current_user.id)
    total = query.count()
    items = query.order_by(Correction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [_correction_to_dict(c) for c in items],
    }


@router.get("/pending")
def get_pending_corrections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Correction).filter(Correction.status == CorrectionStatus.pending)
    total = query.count()
    items = query.order_by(Correction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "items": [_correction_to_dict(c) for c in items],
    }


@router.put("/{correction_id}/review")
def review_correction(correction_id: int, data: CorrectionReview, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    correction = db.query(Correction).filter(Correction.id == correction_id).first()
    if not correction:
        raise HTTPException(status_code=404, detail="纠错记录不存在")
    if correction.status != CorrectionStatus.pending:
        raise HTTPException(status_code=400, detail="该纠错已审核")
    
    correction.status = data.status
    correction.admin_comment = data.admin_comment
    correction.reviewed_by = admin.id
    correction.reviewed_at = datetime.utcnow()
    
    if data.status == CorrectionStatus.approved and data.suggestion:
        # Update the question
        question = db.query(Question).filter(Question.id == correction.question_id).first()
        if question:
            if correction.correction_type == CorrectionType.content:
                question.content = data.suggestion
            elif correction.correction_type == CorrectionType.answer:
                question.correct_answer = data.suggestion
            elif correction.correction_type == CorrectionType.explanation:
                question.explanation = data.suggestion
    
    db.commit()
    return {"message": "审核完成"}


@router.get("/question/{question_id}")
def get_question_corrections(question_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    corrections = db.query(Correction).filter(
        Correction.question_id == question_id,
        Correction.status == CorrectionStatus.approved,
    ).all()
    return {"items": [_correction_to_dict(c) for c in corrections]}


def _correction_to_dict(c: Correction):
    return {
        "id": c.id,
        "question_id": c.question_id,
        "correction_type": c.correction_type.value if c.correction_type else None,
        "description": c.description,
        "suggestion": c.suggestion,
        "status": c.status.value if c.status else None,
        "admin_comment": c.admin_comment,
        "reviewed_at": c.reviewed_at.isoformat() if c.reviewed_at else None,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
