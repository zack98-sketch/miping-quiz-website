import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "密评题库答题网站"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/quiz.db"

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_REFRESH_TOKEN_EXPIRE_HOURS: int = 24

    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # AI
    AI_API_KEY: str = ""
    AI_API_ENDPOINT: str = ""
    AI_HINT_LIMIT_PER_QUESTION: int = 3

    # Export
    EXPORT_DIR: str = "./data/exports"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
