import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from db.base import get_session
from db.models.review import Review, VerificationStatus
from db.models.tool import AITool
from schemas.review import ReviewCreate, ReviewResponse, ReviewAdminAction

log = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def submit_review(
    payload: ReviewCreate,
    session: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    tool = await session.get(AITool, payload.tool_id)
    if not tool or not tool.is_active:
        raise HTTPException(status_code=404, detail="כלי AI לא נמצא")

    review = Review(
        id=uuid.uuid4(),
        tool_id=payload.tool_id,
        user_id=uuid.UUID("00000004-0000-0000-0000-000000000001"),
        rating=payload.rating,
        title=payload.title,
        body=payload.body,
        pros=payload.pros,
        cons=payload.cons,
        linkedin_profile_url=payload.linkedin_profile_url,
        screenshot_proof_url=payload.screenshot_proof_url,
        verification_status=VerificationStatus.PENDING,
    )
    session.add(review)
    await session.commit()
    await session.refresh(review)
    log.info("ביקורת חדשה | tool_id=%s | status=pending", payload.tool_id)
    return ReviewResponse.model_validate(review)

@router.get("/tool/{tool_id}", response_model=list[ReviewResponse])
async def get_tool_reviews(
    tool_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[ReviewResponse]:
    result = await session.execute(
        select(Review)
        .where(Review.tool_id == tool_id, Review.verification_status == VerificationStatus.APPROVED)
        .order_by(Review.created_at.desc())
    )
    return [ReviewResponse.model_validate(r) for r in result.scalars().all()]

@router.patch("/{review_id}/verify", response_model=ReviewResponse, summary="[Admin] אישור/דחייה")
async def admin_verify_review(
    review_id: UUID,
    action: ReviewAdminAction,
    session: AsyncSession = Depends(get_session),
) -> ReviewResponse:
    review = await session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="ביקורת לא נמצאה")

    review.verification_status = action.status
    review.rejection_reason    = action.rejection_reason

    if action.status == VerificationStatus.APPROVED:
        await _update_tool_rating(review.tool_id, session)

    await session.commit()
    await session.refresh(review)
    log.info("ביקורת עודכנה | review_id=%s | status=%s", review_id, action.status.value)
    return ReviewResponse.model_validate(review)

async def _update_tool_rating(tool_id: UUID, session: AsyncSession) -> None:
    from sqlalchemy import func as sqlfunc
    result = await session.execute(
        select(sqlfunc.avg(Review.rating).label("avg"),
               sqlfunc.count(Review.id).label("count"))
        .where(Review.tool_id == tool_id, Review.verification_status == VerificationStatus.APPROVED)
    )
    row = result.one()
    await session.execute(
        update(AITool).where(AITool.id == tool_id)
        .values(avg_rating=round(row.avg or 0, 2), review_count=row.count)
    )
