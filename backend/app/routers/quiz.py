import json
import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Question, QuizSession, AnswerRecord, ErrorBookItem, Favorite, Note,
    QuestionType, Difficulty, QuizMode, SessionStatus, User
)
from app.schemas.quiz import QuizSessionCreate, AnswerSubmit
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/quiz", tags=["答题"])


@router.post("/sessions")
def create_session(data: QuizSessionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get question pool
    query = db.query(Question).filter(Question.is_active == True)
    
    if data.mode == QuizMode.knowledge and data.knowledge_points:
        query = query.filter(Question.knowledge_point.in_(data.knowledge_points))
    elif data.mode == QuizMode.difficulty and data.difficulty:
        query = query.filter(Question.difficulty == data.difficulty)
    
    if data.question_types:
        query = query.filter(Question.question_type.in_(data.question_types))
    
    if data.question_ids:
        # For error_book/favorite mode
        query = db.query(Question).filter(Question.id.in_(data.question_ids), Question.is_active == True)
    
    pool = query.all()
    if not pool:
        raise HTTPException(status_code=404, detail="没有符合条件的题目")
    
    # Random select
    count = min(data.count, len(pool))
    selected = random.sample(pool, count)
    question_ids = [q.id for q in selected]
    
    session = QuizSession(
        user_id=current_user.id,
        mode=data.mode,
        total_count=count,
        question_ids=json.dumps(question_ids),
        status=SessionStatus.in_progress,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "session_id": session.id,
        "total_count": count,
        "mode": data.mode.value,
    }


@router.get("/sessions/{session_id}/current")
def get_current_question(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="答题会话不存在")
    if session.status != SessionStatus.in_progress:
        raise HTTPException(status_code=400, detail="答题会话已结束")
    
    question_ids = json.loads(session.question_ids)
    if session.current_index >= len(question_ids):
        raise HTTPException(status_code=400, detail="所有题目已答完")
    
    qid = question_ids[session.current_index]
    question = db.query(Question).filter(Question.id == qid).first()
    
    # Check if already answered
    existing = db.query(AnswerRecord).filter(
        AnswerRecord.session_id == session_id,
        AnswerRecord.question_id == qid,
    ).first()
    
    # Check favorite and note
    is_favorited = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.question_id == qid).first() is not None
    has_note = db.query(Note).filter(Note.user_id == current_user.id, Note.question_id == qid).first() is not None
    
    return {
        "question_index": session.current_index,
        "total_count": session.total_count,
        "question": _question_to_dict(question, include_answer=False),
        "is_answered": existing is not None,
        "user_answer": existing.user_answer if existing else None,
        "is_correct": existing.is_correct if existing else None,
        "is_favorited": is_favorited,
        "has_note": has_note,
    }


@router.post("/sessions/{session_id}/answer")
def submit_answer(session_id: int, data: AnswerSubmit, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="答题会话不存在")
    if session.status != SessionStatus.in_progress:
        raise HTTPException(status_code=400, detail="答题会话已结束")
    
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="题目不存在")
    
    # Judge
    is_correct = _judge_answer(question, data.answer)
    
    # Save answer record
    record = AnswerRecord(
        session_id=session_id,
        question_id=data.question_id,
        user_answer=data.answer,
        is_correct=1 if is_correct else 0,
        time_spent=data.time_spent,
    )
    db.add(record)
    
    if is_correct:
        session.correct_count += 1
    else:
        # Auto add to error book
        _add_to_error_book(current_user.id, data.question_id, data.answer, db)
    
    session.time_spent += data.time_spent
    session.current_index += 1
    
    # Check if all answered
    question_ids = json.loads(session.question_ids)
    if session.current_index >= len(question_ids):
        session.status = SessionStatus.completed
        from sqlalchemy.sql import func
        session.completed_at = func.now()
    
    db.commit()
    
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer,
        "explanation": question.explanation,
        "current_index": session.current_index,
        "total_count": session.total_count,
        "is_completed": session.status == SessionStatus.completed,
    }


@router.get("/sessions/{session_id}/result")
def get_result(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="答题会话不存在")
    
    records = db.query(AnswerRecord).filter(AnswerRecord.session_id == session_id).all()
    accuracy = (session.correct_count / session.total_count * 100) if session.total_count > 0 else 0
    
    error_questions = []
    for r in records:
        if r.is_correct == 0:
            q = db.query(Question).filter(Question.id == r.question_id).first()
            error_questions.append({
                "question_id": r.question_id,
                "content": q.content if q else "",
                "user_answer": r.user_answer,
                "correct_answer": q.correct_answer if q else "",
                "explanation": q.explanation if q else "",
            })
    
    return {
        "session": {
            "id": session.id,
            "mode": session.mode.value,
            "total_count": session.total_count,
            "correct_count": session.correct_count,
            "status": session.status.value,
            "time_spent": session.time_spent,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        },
        "accuracy": round(accuracy, 1),
        "error_questions": error_questions,
        "answers": [
            {
                "question_id": r.question_id,
                "user_answer": r.user_answer,
                "is_correct": r.is_correct,
                "time_spent": r.time_spent,
            }
            for r in records
        ],
    }


@router.get("/sessions/incomplete")
def get_incomplete_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    sessions = db.query(QuizSession).filter(
        QuizSession.user_id == current_user.id,
        QuizSession.status == SessionStatus.in_progress,
    ).order_by(QuizSession.started_at.desc()).all()
    return {
        "sessions": [
            {
                "id": s.id,
                "mode": s.mode.value,
                "total_count": s.total_count,
                "current_index": s.current_index,
                "started_at": s.started_at.isoformat() if s.started_at else None,
            }
            for s in sessions
        ]
    }


@router.put("/sessions/{session_id}/abandon")
def abandon_session(session_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="答题会话不存在")
    session.status = SessionStatus.abandoned
    db.commit()
    return {"message": "已放弃答题"}


def _judge_answer(question: Question, user_answer: str) -> bool:
    correct = question.correct_answer.strip().upper()
    answer = user_answer.strip().upper()
    
    if question.question_type == QuestionType.judge:
        # Normalize judge answers
        def normalize_judge(a):
            if a in ("A", "正确", "对", "TRUE", "T", "1"):
                return "A"
            elif a in ("B", "错误", "错", "FALSE", "F", "0"):
                return "B"
            return a.upper()
        return normalize_judge(answer) == normalize_judge(correct)
    
    elif question.question_type == QuestionType.multi:
        # Sort and compare
        correct_set = set(c.strip() for c in correct.replace(",", " ").split())
        answer_set = set(c.strip() for c in answer.replace(",", " ").split())
        return correct_set == answer_set
    
    else:  # single
        return answer == correct


def _add_to_error_book(user_id: int, question_id: int, user_answer: str, db: Session):
    existing = db.query(ErrorBookItem).filter(
        ErrorBookItem.user_id == user_id,
        ErrorBookItem.question_id == question_id,
    ).first()
    if existing:
        existing.error_count += 1
        existing.user_answer = user_answer
        from sqlalchemy.sql import func
        existing.last_error_at = func.now()
    else:
        item = ErrorBookItem(
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer,
        )
        db.add(item)


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
