import json
import random
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import (
    Exam, ExamParticipation, ExamAnswer, Question, QuizSession,
    SessionStatus, QuestionType, User
)
from app.dependencies import get_current_user, require_admin

router = APIRouter(prefix="/api/exams", tags=["在线考试"])


@router.post("")
def create_exam(data: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    exam = Exam(
        title=data["title"],
        description=data.get("description"),
        start_time=datetime.fromisoformat(data["start_time"]),
        end_time=datetime.fromisoformat(data["end_time"]),
        time_limit=data["time_limit"],
        question_config=data["question_config"],
        created_by=admin.id,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return {"id": exam.id, "message": "考试创建成功"}


@router.get("")
def get_exams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Exam).filter(Exam.is_active == True)
    total = query.count()
    exams = query.order_by(Exam.start_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    now = datetime.utcnow()
    items = []
    for e in exams:
        status = "upcoming" if now < e.start_time else ("ongoing" if now < e.end_time else "ended")
        has_participated = db.query(ExamParticipation).filter(
            ExamParticipation.exam_id == e.id,
            ExamParticipation.user_id == current_user.id,
        ).first() is not None
        items.append({
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "start_time": e.start_time.isoformat(),
            "end_time": e.end_time.isoformat(),
            "time_limit": e.time_limit,
            "is_active": e.is_active,
            "status": status,
            "has_participated": has_participated,
        })
    
    return {"total": total, "items": items}


@router.get("/{exam_id}")
def get_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    return {
        "id": exam.id,
        "title": exam.title,
        "description": exam.description,
        "start_time": exam.start_time.isoformat(),
        "end_time": exam.end_time.isoformat(),
        "time_limit": exam.time_limit,
        "question_config": exam.question_config,
    }


@router.post("/{exam_id}/enter")
def enter_exam(exam_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="考试不存在")
    
    now = datetime.utcnow()
    if now < exam.start_time:
        raise HTTPException(status_code=400, detail="考试未开始")
    if now > exam.end_time:
        raise HTTPException(status_code=400, detail="考试已结束")
    
    # Check if already participated
    existing = db.query(ExamParticipation).filter(
        ExamParticipation.exam_id == exam_id,
        ExamParticipation.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已参加该考试")
    
    # Generate questions based on config
    config = exam.question_config
    query = db.query(Question).filter(Question.is_active == True)
    if config.get("types"):
        types = [QuestionType(t) for t in config["types"]]
        query = query.filter(Question.question_type.in_(types))
    if config.get("knowledge_points"):
        query = query.filter(Question.knowledge_point.in_(config["knowledge_points"]))
    
    pool = query.all()
    count = min(config.get("count", 20), len(pool))
    selected = random.sample(pool, count)
    question_ids = [q.id for q in selected]
    
    participation = ExamParticipation(
        exam_id=exam_id,
        user_id=current_user.id,
        total_count=count,
    )
    db.add(participation)
    db.commit()
    db.refresh(participation)
    
    return {
        "participation_id": participation.id,
        "questions": [
            {
                "id": q.id,
                "content": q.content,
                "question_type": q.question_type.value,
                "options": [{"id": o.id, "label": o.label, "content": o.content} for o in sorted(q.options, key=lambda x: x.sort_order)],
            }
            for q in selected
        ],
        "time_limit": exam.time_limit,
    }


@router.post("/{exam_id}/submit")
def submit_exam(exam_id: int, data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    participation = db.query(ExamParticipation).filter(
        ExamParticipation.exam_id == exam_id,
        ExamParticipation.user_id == current_user.id,
    ).first()
    if not participation:
        raise HTTPException(status_code=404, detail="未参加该考试")
    if participation.submitted_at:
        raise HTTPException(status_code=400, detail="已提交答卷")
    
    answers = data.get("answers", [])
    correct_count = 0
    
    for ans in answers:
        q = db.query(Question).filter(Question.id == ans["question_id"]).first()
        is_correct = 0
        if q:
            is_correct = 1 if _judge_answer(q, ans["answer"]) else 0
            if is_correct:
                correct_count += 1
        
        exam_answer = ExamAnswer(
            participation_id=participation.id,
            question_id=ans["question_id"],
            user_answer=ans["answer"],
            is_correct=is_correct,
        )
        db.add(exam_answer)
    
    participation.correct_count = correct_count
    participation.score = (correct_count / participation.total_count * 100) if participation.total_count > 0 else 0
    participation.time_spent = data.get("time_spent", 0)
    participation.submitted_at = datetime.utcnow()
    db.commit()
    
    return {
        "score": participation.score,
        "correct_count": correct_count,
        "total_count": participation.total_count,
    }


@router.get("/my-history")
def get_my_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    participations = db.query(ExamParticipation).filter(
        ExamParticipation.user_id == current_user.id,
        ExamParticipation.submitted_at != None,
    ).all()
    
    items = []
    for p in participations:
        exam = db.query(Exam).filter(Exam.id == p.exam_id).first()
        items.append({
            "exam_id": p.exam_id,
            "title": exam.title if exam else "",
            "score": p.score,
            "correct_count": p.correct_count,
            "total_count": p.total_count,
            "time_spent": p.time_spent,
            "submitted_at": p.submitted_at.isoformat() if p.submitted_at else None,
        })
    
    return {"items": items}


def _judge_answer(question: Question, user_answer: str) -> bool:
    correct = question.correct_answer.strip().upper()
    answer = user_answer.strip().upper()
    if question.question_type == QuestionType.judge:
        def normalize_judge(a):
            if a in ("A", "正确", "对", "TRUE", "T", "1"):
                return "A"
            elif a in ("B", "错误", "错", "FALSE", "F", "0"):
                return "B"
            return a.upper()
        return normalize_judge(answer) == normalize_judge(correct)
    elif question.question_type == QuestionType.multi:
        correct_set = set(c.strip() for c in correct.replace(",", " ").split())
        answer_set = set(c.strip() for c in answer.replace(",", " ").split())
        return correct_set == answer_set
    else:
        return answer == correct
