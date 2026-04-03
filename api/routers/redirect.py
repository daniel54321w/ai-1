import logging
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import get_session
from db.models.tool import AITool

log = logging.getLogger(__name__)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://frontend.domain.co.il")
router = APIRouter(prefix="/t", tags=["Short Links"])

@router.get("/{short_id}", response_class=RedirectResponse, status_code=302)
async def redirect_short_link(
    short_id: str,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    result = await session.execute(
        select(AITool.id, AITool.is_active).where(AITool.short_id == short_id)
    )
    row = result.one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail=f"כלי עם מזהה '{short_id}' לא קיים")
    if not row.is_active:
        raise HTTPException(status_code=404, detail="כלי זה אינו זמין כרגע")

    target = f"{FRONTEND_URL}/tools/{row.id}"
    log.info("redirect | %s → %s", short_id, target)
    return RedirectResponse(url=target, status_code=302)
