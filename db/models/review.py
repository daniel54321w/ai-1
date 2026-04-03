import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func, Enum as SAEnum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class VerificationStatus(str, Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class Review(Base):
    __tablename__ = "reviews"

    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_rating_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    tool_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_tools.id", ondelete="CASCADE"), nullable=False)
    tool: Mapped["AITool"] = relationship(back_populates="reviews")

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="reviews")

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str | None] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text, nullable=False)
    pros: Mapped[str | None] = mapped_column(Text)
    cons: Mapped[str | None] = mapped_column(Text)

    linkedin_profile_url: Mapped[str] = mapped_column(String(500), nullable=False)
    screenshot_proof_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    verification_status: Mapped[VerificationStatus] = mapped_column(
        SAEnum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_by_admin_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
