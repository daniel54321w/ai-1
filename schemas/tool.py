import os
from pydantic import BaseModel, computed_field
from uuid import UUID
from db.models.tool import PricingModel

FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://frontend.domain.co.il")
SHORT_BASE   = os.environ.get("SHORT_BASE",   "https://ai.co.il")

class VendorBrief(BaseModel):
    id:              UUID
    company_name:    str
    company_name_he: str | None
    website_url:     str
    is_verified:     bool
    model_config = {"from_attributes": True}

class ToolFeatured(BaseModel):
    id:                    UUID
    short_id:              str
    name:                  str
    slug:                  str
    tagline_he:            str | None
    tagline_en:            str | None
    pricing_model:         PricingModel
    price_starting_usd:    float | None
    hebrew_interface:      bool
    data_stored_in_israel: bool
    gdpr_compliant:        bool
    avg_rating:            float
    review_count:          int
    vendor:                VendorBrief

    @computed_field
    @property
    def share_url(self) -> str:
        return f"{SHORT_BASE}/t/{self.short_id}"

    @computed_field
    @property
    def canonical_url(self) -> str:
        return f"{FRONTEND_URL}/tools/{self.id}"

    model_config = {"from_attributes": True}
