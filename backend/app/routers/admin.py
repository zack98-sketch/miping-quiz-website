import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Question, Option, QuestionType, Difficulty, SystemConfig, User, UserRole
from app.dependencies import require_admin
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["管理"])


@router.post("/questions/import")
async def import_questions(file: UploadFile = File(...), admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="仅支持.xlsx文件")
    
    # Save file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        from app.importers.excel_importer import import_excel
        result = import_excel(tmp_path, db)
        return result
    finally:
        os.unlink(tmp_path)


@router.get("/config")
def get_config(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    configs = db.query(SystemConfig).all()
    return {"items": [{"key": c.key, "value": c.value, "description": c.description} for c in configs]}


@router.put("/config")
def update_config(data: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    for key, value in data.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = str(value)
        else:
            config = SystemConfig(key=key, value=str(value))
            db.add(config)
    db.commit()
    return {"message": "配置更新成功"}


@router.post("/config")
def set_config(data: dict, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """设置单个配置项"""
    key = data.get("key")
    value = data.get("value")
    if not key:
        raise HTTPException(status_code=400, detail="key is required")
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if config:
        config.value = str(value)
    else:
        config = SystemConfig(key=key, value=str(value), description=data.get("description", ""))
        db.add(config)
    db.commit()
    return {"message": "配置保存成功"}


@router.get("/dashboard")
def get_dashboard(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    from sqlalchemy import func
    total_questions = db.query(Question).count()
    total_users = db.query(User).filter(User.role == UserRole.user).count()
    active_users_today = 0  # Simplified
    
    return {
        "total_questions": total_questions,
        "total_users": total_users,
        "active_users_today": active_users_today,
    }
