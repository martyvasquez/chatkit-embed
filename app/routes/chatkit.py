from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..chatkit import ChatKitError, create_chatkit_session
from ..database import get_session
from ..domain import extract_host, is_domain_allowed
from ..models import ChatApp
from ..schemas import SessionRequest, SessionResponse
from ..security import decrypt_secret, EncryptionError

router = APIRouter(prefix="/api/chatkit", tags=["chatkit"])


@router.post("/session/{app_id}", response_model=SessionResponse)
async def create_session(
    app_id: str,
    payload: SessionRequest,
    session: AsyncSession = Depends(get_session),
) -> SessionResponse:
    result = await session.execute(select(ChatApp).where(ChatApp.id == app_id))
    chat_app = result.scalar_one_or_none()
    if not chat_app or not chat_app.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="App not found")

    host = extract_host(str(payload.origin))
    allowed = [item.strip() for item in chat_app.allowed_domains.split(",") if item.strip()]
    if allowed:
        if not host or not is_domain_allowed(host, allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized domain"
            )

    try:
        api_key = decrypt_secret(chat_app.openai_api_key_encrypted)
    except EncryptionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secret unavailable",
        )

    try:
        client_secret = create_chatkit_session(api_key=api_key, workflow_id=chat_app.workflow_id)
    except ChatKitError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to create ChatKit session",
        )

    return SessionResponse(client_secret=client_secret)
