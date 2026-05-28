from pydantic import BaseModel
from datetime import datetime
from app.models.correction import CorrectionType, CorrectionStatus


class CorrectionCreate(BaseModel):
    question_id: int
    correction_type: CorrectionType
    description: str
    suggestion: str | None = None


class CorrectionReview(BaseModel):
    status: CorrectionStatus  # approved or rejected
    admin_comment: str | None = None
    suggestion: str | None = None  # Updated content for the question


class CorrectionResponse(BaseModel):
    id: int
    question_id: int
    correction_type: CorrectionType
    description: str
    suggestion: str | None
    status: CorrectionStatus
    admin_comment: str | None
    reviewed_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True
