import re
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from db.models.review import VerificationStatus

LINKEDIN_PATTERN = re.compile(
    r"^https://(www\.)?linkedin\.com/in/[a-zA-Z0-9\-_%]+/?$"
)

class ReviewCreate(BaseModel):
    tool_id:              UUID
    rating:               int = Field(..., ge=1, le=5)
    title:                str | None = Field(None, max_length=300)
    body:                 str = Field(..., min_length=50, max_length=5000)
    pros:                 str | None = Field(None, max_length=1000)
    cons:                 str | None = Field(None, max_length=1000)
    linkedin_profile_url: str
    screenshot_proof_url: str

    @field_validator("linkedin_profile_url")
    @classmethod
    def validate_linkedin(cls, v: str) -> str:
        if not LINKEDIN_PATTERN.match(v):
            raise ValueError("כתובת LinkedIn אינה תקינה")
        return v

    @field_validator("body")
    @classmethod
    def no_spam_patterns(cls, v: str) -> str:
        spam_keywords = ["לחץ כאן", "click here", "bit.ly", "goo.gl"]
        if any(kw in v.lower() for kw in spam_keywords):
            raise ValueError("הביקורת מכילה תוכן חשוד")
        return v

class ReviewResponse(BaseModel):
    id:                   UUID
    tool_id:              UUID
    rating:               int
    title:                str | None
    body:                 str
    pros:                 str | None
    cons:                 str | None
    linkedin_profile_url: str
    verification_status:  VerificationStatus
    created_at:           datetime
    author_name:          str
    model_config = {"from_attributes": True}

class ReviewAdminAction(BaseModel):
    status:           VerificationStatus
    rejection_reason: str | None = None

    @field_validator("rejection_reason")
    @classmethod
    def reason_required_for_rejection(cls, v: str | None, info) -> str | None:
        if info.data.get("status") == VerificationStatus.REJECTED and not v:
            raise ValueError("חובה לספק סיבת דחייה")
        return v
