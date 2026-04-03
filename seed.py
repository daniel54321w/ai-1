"""
הרצה מקומית:  python seed.py
דרישות:       pip install -r requirements.txt
              .env עם DATABASE_URL=postgresql+asyncpg://...
"""
import asyncio
import uuid
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from db.base import Base
from db.models.user import User
from db.models.vendor import Vendor
from db.models.category import Category
from db.models.tool import AITool, PricingModel
from db.models.review import Review, VerificationStatus
from core.short_id import generate_short_id, tool_url

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("seed")

engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
AsyncSession_ = async_sessionmaker(engine, expire_on_commit=False)

VENDORS = [
    {
        "id": uuid.UUID("00000001-0000-0000-0000-000000000001"),
        "company_name": "Kaleidoscope AI",
        "company_name_he": "קליידוסקופ בינה מלאכותית",
        "website_url": "https://kaleidoscope-ai.co.il",
        "description_he": "חברה ישראלית המפתחת כלי AI לשיווק דיגיטלי עם תמיכה מלאה בעברית.",
        "description": "Israeli company developing AI tools for digital marketing with full Hebrew support.",
        "contact_email": "hello@kaleidoscope-ai.co.il",
        "is_verified": True,
        "verified_at": datetime(2025, 1, 15, tzinfo=timezone.utc),
    },
    {
        "id": uuid.UUID("00000001-0000-0000-0000-000000000002"),
        "company_name": "DataBridge Solutions",
        "company_name_he": 'דאטהברידג\' פתרונות בע"מ',
        "website_url": "https://databridge.co.il",
        "description_he": "סטארטאפ ישראלי המתמחה באוטומציה שיווקית חכמה, משרת 500+ עסקים.",
        "description": "Israeli startup specializing in smart marketing automation, serving 500+ SMBs.",
        "contact_email": "support@databridge.co.il",
        "is_verified": True,
        "verified_at": datetime(2025, 2, 1, tzinfo=timezone.utc),
    },
]

CATEGORY = {
    "id": uuid.UUID("00000002-0000-0000-0000-000000000001"),
    "slug": "marketing",
    "name_he": "שיווק ופרסום",
    "name_en": "Marketing & Advertising",
    "parent_id": None,
}

TOOL1_UUID = uuid.UUID("00000003-0000-0000-0000-000000000001")
TOOL2_UUID = uuid.UUID("00000003-0000-0000-0000-000000000002")

def build_tools(category_id: uuid.UUID) -> list[dict]:
    return [
        {
            "id": TOOL1_UUID,
            "short_id": generate_short_id(TOOL1_UUID),
            "vendor_id": uuid.UUID("00000001-0000-0000-0000-000000000001"),
            "category_id": category_id,
            "name": "CopyBot Pro",
            "slug": "copybot-pro",
            "tagline_he": "כותב שיווקי בעברית, מונע בינה מלאכותית",
            "tagline_en": "AI-powered Hebrew marketing copywriter",
            "description_he": "CopyBot Pro מייצר תוכן שיווקי מקצועי בעברית בשניות. תומך RTL מלא.",
            "description_en": "CopyBot Pro generates professional Hebrew marketing copy in seconds.",
            "pricing_model": PricingModel.FREEMIUM,
            "price_starting_usd": 29.0,
            "hebrew_interface": True,
            "data_stored_in_israel": True,
            "gdpr_compliant": True,
            "avg_rating": 4.7,
            "review_count": 3,
            "is_active": True,
        },
        {
            "id": TOOL2_UUID,
            "short_id": generate_short_id(TOOL2_UUID),
            "vendor_id": uuid.UUID("00000001-0000-0000-0000-000000000002"),
            "category_id": category_id,
            "name": "SocialAI Manager",
            "slug": "socialai-manager",
            "tagline_he": "ניהול סושיאל מדיה על טייס אוטומטי",
            "tagline_en": "Social media management on autopilot",
            "description_he": "מנתח קהל יעד ומייצר לוח תוכן חודשי בעברית עם אינטגרציה לפייסבוק ואינסטגרם.",
            "description_en": "Analyzes your audience and generates a monthly Hebrew content plan.",
            "pricing_model": PricingModel.SUBSCRIPTION,
            "price_starting_usd": 49.0,
            "hebrew_interface": True,
            "data_stored_in_israel": False,
            "gdpr_compliant": True,
            "avg_rating": 4.2,
            "review_count": 1,
            "is_active": True,
        },
    ]

async def clear_tables(session: AsyncSession) -> None:
    log.info("מנקה טבלאות...")
    for tbl in ("reviews", "ai_tools", "categories", "vendors", "users"):
        await session.execute(text(f"DELETE FROM {tbl}"))
    await session.commit()

async def seed_vendors(session: AsyncSession) -> None:
    for data in VENDORS:
        session.add(Vendor(**data))
    await session.commit()
    log.info("✓ %d ספקים", len(VENDORS))

async def seed_category(session: AsyncSession) -> uuid.UUID:
    session.add(Category(**CATEGORY))
    await session.commit()
    log.info("✓ קטגוריה '%s'", CATEGORY["name_he"])
    return CATEGORY["id"]

async def seed_tools(session: AsyncSession, category_id: uuid.UUID) -> None:
    tools = build_tools(category_id)
    for data in tools:
        session.add(AITool(**data))
        log.info("  ✓ %s | short_id: %s | %s",
                 data["name"], data["short_id"], tool_url(data["short_id"]))
    await session.commit()
    log.info("✓ %d כלים", len(tools))

async def seed_demo_user_and_review(session: AsyncSession) -> None:
    user = User(
        id=uuid.UUID("00000004-0000-0000-0000-000000000001"),
        email="demo@example.co.il",
        full_name="יוסי כהן",
        linkedin_id="yossi-cohen-demo",
        linkedin_profile_url="https://www.linkedin.com/in/yossi-cohen-demo/",
        linkedin_verified_at=datetime(2025, 3, 1, tzinfo=timezone.utc),
    )
    session.add(user)

    review = Review(
        id=uuid.UUID("00000005-0000-0000-0000-000000000001"),
        tool_id=TOOL1_UUID,
        user_id=user.id,
        rating=5,
        title="חסך לי שעות של עבודה בשבוע",
        body=(
            "השתמשתי ב-CopyBot Pro לכתיבת מודעות לקמפיין פייסבוק של המסעדה שלי. "
            "בתוך 10 דקות קיבלתי 5 גרסאות מעולות בעברית שמדברות ישר ללקוחות שלי. "
            "ממליץ בחום לכל בעל עסק קטן."
        ),
        pros="תמיכה מעולה בעברית, ממשק פשוט, תוצאות מהירות",
        cons="הגרסה החינמית מוגבלת ל-5 יצירות בחודש",
        linkedin_profile_url="https://www.linkedin.com/in/yossi-cohen-demo/",
        screenshot_proof_url="https://res.cloudinary.com/demo/image/upload/seed_proof_yossi.jpg",
        verification_status=VerificationStatus.APPROVED,
    )
    session.add(review)
    await session.commit()
    log.info("✓ משתמש דמו + ביקורת מאושרת")

async def main() -> None:
    log.info("=" * 45)
    log.info("  אי של אמון — Seed Script")
    log.info("=" * 45)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        log.info("סכמת DB נוצרה / אומתה")

    async with AsyncSession_() as session:
        await clear_tables(session)
        await seed_vendors(session)
        cat_id = await seed_category(session)
        await seed_tools(session, cat_id)
        await seed_demo_user_and_review(session)

    log.info("=" * 45)
    log.info("  Seed הושלם בהצלחה!")
    log.info("=" * 45)

if __name__ == "__main__":
    asyncio.run(main())
