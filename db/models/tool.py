import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, Boolean, DateTime, Float, ForeignKey, Integer, func, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base

class PricingModel(str, Enum):
    FREE         = "free"
    FREEMIUM     = "freemium"
    SUBSCRIPTION = "subscription"
    PAY_PER_USE  = "pay_per_use"
    ENTERPRISE   = "enterprise"

class AITool(Base):
    __tablename__ = "ai_tools"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    short_id: Mapped[str] = mapped_column(String(12), unique=True, nullable=False, index=True)

    vendor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False)
    vendor: Mapped["Vendor"] = relationship(back_populates="tools")

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="tools")

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tagline_he: Mapped[str | None] = mapped_column(String(500))
    tagline_en: Mapped[str | None] = mapped_column(String(500))
    description_he: Mapped[str | None] = mapped_column(Text)
    description_en: Mapped[str | None] = mapped_column(Text)

    pricing_model: Mapped[PricingModel] = mapped_column(SAEnum(PricingModel), nullable=False)
    price_starting_usd: Mapped[float | None] = mapped_column(Float)
    hebrew_interface: Mapped[bool] = mapped_column(Boolean, default=False)
    data_stored_in_israel: Mapped[bool] = mapped_column(Boolean, default=False)
    gdpr_compliant: Mapped[bool] = mapped_column(Boolean, default=False)

    avg_rating: Mapped[float] = mapped_column(Float, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reviews: Mapped[list["Review"]] = relationship(back_populates="tool", lazy="selectin")
