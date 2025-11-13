from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, HttpUrl


class SessionRequest(BaseModel):
    origin: HttpUrl
    existing_client_secret: Optional[str] = Field(default=None, alias="existing_client_secret")


class SessionResponse(BaseModel):
    client_secret: str


class EmbedConfigResponse(BaseModel):
    options: Dict[str, Any]
