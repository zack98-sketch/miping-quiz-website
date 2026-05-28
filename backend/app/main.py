from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db, SessionLocal
from app.models import User, UserRole
from app.utils.security import get_password_hash

# Import routers
from app.routers import auth, questions, quiz, error_book, favorites, corrections, notes, analysis, exam, ai_hint, admin

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(quiz.router)
app.include_router(error_book.router)
app.include_router(favorites.router)
app.include_router(corrections.router)
app.include_router(notes.router)
app.include_router(analysis.router)
app.include_router(exam.router)
app.include_router(ai_hint.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup():
    init_db()
    _create_default_admin()


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


def _create_default_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.ADMIN_USERNAME,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()
