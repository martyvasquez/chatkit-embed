import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..domain import extract_host, is_domain_allowed
from ..models import ChatApp
from ..schemas import EmbedConfigResponse

router = APIRouter(prefix="/embed", tags=["embed"])


@router.get("/config/{app_id}", response_model=EmbedConfigResponse)
async def get_embed_config(
    app_id: str,
    origin: str = Query(..., description="Origin making the request."),
    session: AsyncSession = Depends(get_session),
) -> EmbedConfigResponse:
    result = await session.execute(select(ChatApp).where(ChatApp.id == app_id))
    chat_app = result.scalar_one_or_none()
    if not chat_app or not chat_app.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")

    host = extract_host(origin)
    allowed = [item.strip() for item in chat_app.allowed_domains.split(",") if item.strip()]
    if not host or not is_domain_allowed(host, allowed):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized domain"
        )

    return EmbedConfigResponse(options=json.loads(chat_app.options_json))
