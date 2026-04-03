import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from db.base import get_session
from db.models.tool import AITool
from schemas.tool import ToolFeatured

log = logging.getLogger(__name__)
router = APIRouter(prefix="/tools", tags=["Tools"])

@router.get("/featured", response_model=list[ToolFeatured], summary="10 כלים מובילים לדף הבית")
async def get_featured_tools(
    limit: int = Query(default=10, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> list[ToolFeatured]:
    result = await session.execute(
        select(AITool)
        .options(joinedload(AITool.vendor))
        .where(AITool.is_active == True, AITool.review_count > 0)
        .order_by(AITool.avg_rating.desc())
        .limit(limit)
    )
    tools = result.scalars().all()
    log.info("featured tools | returned=%d", len(tools))
    return [ToolFeatured.model_validate(t) for t in tools]

@router.get("/{tool_id}", response_model=ToolFeatured, summary="פרטי כלי לפי UUID")
async def get_tool_by_id(
    tool_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ToolFeatured:
    result = await session.execute(
        select(AITool)
        .options(joinedload(AITool.vendor))
        .where(AITool.id == tool_id, AITool.is_active == True)
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="כלי לא נמצא")
    return ToolFeatured.model_validate(tool)
