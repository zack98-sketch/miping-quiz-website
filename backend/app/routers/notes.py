from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Note, Question, User
from app.dependencies import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/notes", tags=["备注"])


@router.post("")
def upsert_note(question_id: int, content: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if len(content) > 2000:
        raise HTTPException(status_code=400, detail="备注内容不能超过2000字符")
    
    existing = db.query(Note).filter(Note.user_id == current_user.id, Note.question_id == question_id).first()
    if existing:
        existing.content = content
    else:
        note = Note(user_id=current_user.id, question_id=question_id, content=content)
        db.add(note)
    db.commit()
    return {"message": "保存成功"}


@router.delete("/{note_id}")
def delete_note(note_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="备注不存在")
    db.delete(note)
    db.commit()
    return {"message": "删除成功"}


@router.get("")
def get_notes(
    knowledge_point: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Note).filter(Note.user_id == current_user.id)
    if knowledge_point:
        query = query.join(Question).filter(Question.knowledge_point == knowledge_point)
    
    total = query.count()
    notes = query.order_by(Note.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    items = []
    for note in notes:
        q = db.query(Question).filter(Question.id == note.question_id).first()
        items.append({
            "id": note.id,
            "question_id": note.question_id,
            "content": note.content,
            "created_at": note.created_at.isoformat() if note.created_at else None,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
            "question_content": q.content[:100] if q else None,
            "question_type": q.question_type.value if q and q.question_type else None,
            "knowledge_point": q.knowledge_point if q else None,
        })
    
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/question/{question_id}")
def get_question_note(question_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.user_id == current_user.id, Note.question_id == question_id).first()
    if not note:
        return {"note": None}
    return {
        "note": {
            "id": note.id,
            "content": note.content,
            "updated_at": note.updated_at.isoformat() if note.updated_at else None,
        }
    }
