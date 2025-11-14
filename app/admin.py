import json
import logging
import uuid
from pathlib import Path
from typing import Optional

import aioredis
from fastapi import FastAPI, HTTPException
from fastapi_admin.app import app as fastapi_admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Field, Model
from fastapi_admin.widgets import displays, inputs
from sqlalchemy.engine import make_url
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER, HTTP_400_BAD_REQUEST
from tortoise import Tortoise

from .admin_models import AdminUser, ChatAppAdmin
from .config import get_settings
from .parsing import OptionsParseError, parse_allowed_domains, serialize_options
from .security import EncryptionError, encrypt_secret

logger = logging.getLogger(__name__)

_initialized = False
RESOURCE_SLUG = ChatAppAdmin.__name__.lower()


class ChatAppResource(Model):
    label = "Chat Apps"
    icon = "ti ti-brand-openai"
    model = ChatAppAdmin
    page_title = "Chat Apps"
    page_pre_title = "Configuration"
    fields = [
        Field("id", label="App ID", input_=inputs.Input(placeholder="app_acme", null=True)),
        Field("name", label="Name"),
        Field("workflow_id", label="Workflow ID"),
        Field(
            "allowed_domains",
            label="Allowed Domains",
            input_=inputs.TextArea(
                help_text="Comma or newline separated. Leave blank to allow all domains.",
                placeholder="example.com, blog.example.com",
                null=True,
            ),
        ),
        Field(
            "is_active",
            label="Active",
            input_=inputs.Switch(default=True),
        ),
        Field(
            "options_json",
            label="Stored Options",
            display=displays.Json(),
            input_=inputs.DisplayOnly(),
        ),
        Field(
            "options_raw",
            label="ChatKit Options (paste JS/TS)",
            display=displays.InputOnly(),
            input_=inputs.TextArea(
                help_text="Paste the ChatKitOptions export; imports/comments supported.",
            ),
        ),
        Field(
            "openai_api_key_encrypted",
            label="Encrypted OpenAI Key",
            display=displays.InputOnly(),
            input_=inputs.DisplayOnly(),
        ),
        Field(
            "openai_api_key",
            label="OpenAI API Key",
            display=displays.InputOnly(),
            input_=inputs.Password(
                placeholder="sk-...",
                help_text="Value stored encrypted at rest.",
            ),
        ),
    ]

    @classmethod
    async def get_inputs(cls, request, obj: Optional[ChatAppAdmin] = None):
        if obj:
            # Provide a readable textarea default for edits while hiding the encrypted key.
            try:
                parsed = json.loads(obj.options_json)
                obj.options_raw = json.dumps(parsed, indent=2)
            except json.JSONDecodeError:
                obj.options_raw = obj.options_json
            obj.openai_api_key = ""
            obj.allowed_domains = "\n".join(
                domain.strip() for domain in obj.allowed_domains.split(",") if domain.strip()
            )
        return await super().get_inputs(request, obj)

    @classmethod
    async def resolve_data(cls, request, data: FormData):
        values, m2m = await super().resolve_data(request, data)
        is_create = request.url.path.endswith("/create")

        raw_options = (values.pop("options_raw", "") or "").strip()
        if raw_options:
            try:
                values["options_json"] = serialize_options(raw_options)
            except OptionsParseError as exc:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST, detail=str(exc)
                ) from exc
        elif is_create:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="ChatKit options are required.",
            )

        raw_key = (values.pop("openai_api_key", "") or "").strip()
        if raw_key:
            try:
                values["openai_api_key_encrypted"] = encrypt_secret(raw_key)
            except EncryptionError as exc:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Unable to encrypt OpenAI API key.",
                ) from exc
        elif is_create:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="OpenAI API key is required.",
            )

        domains_raw = values.get("allowed_domains", "") or ""
        domains_normalized = domains_raw.replace("\n", ",")
        domains = parse_allowed_domains(domains_normalized)
        values["allowed_domains"] = ",".join(domains)

        if is_create and not values.get("id"):
            values["id"] = f"app_{uuid.uuid4().hex[:8]}"

        return values, m2m


async def init_admin(app: FastAPI) -> None:
    global _initialized
    if _initialized:
        return

    settings = get_settings()
    tortoise_url = settings.tortoise_database_url or _to_tortoise_url(settings.database_url)
    await Tortoise.init(
        config={
            "connections": {"default": tortoise_url},
            "apps": {"models": {"models": ["app.admin_models"], "default_connection": "default"}},
        }
    )
    await Tortoise.generate_schemas(safe=True)

    redis = aioredis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)

    provider = UsernamePasswordProvider(
        admin_model=AdminUser,
        login_logo_url="https://cdn.platform.openai.com/favicon.ico",
        login_title="ChatKit Embed Admin",
    )

    fastapi_admin_app.register_resources(ChatAppResource)
    await fastapi_admin_app.configure(
        redis=redis,
        providers=[provider],
        admin_path=settings.admin_path,
        logo_url="ChatKit Embed",
        favicon_url="https://cdn.platform.openai.com/favicon.ico",
        template_folders=[str(Path(__file__).resolve().parent / "templates")],
    )

    await _ensure_default_admin(settings.admin_user)
    app.mount(settings.admin_path, fastapi_admin_app)
    _initialized = True
    logger.info("FastAPI-Admin initialized at %s", settings.admin_path)


async def _ensure_default_admin(admin_settings) -> None:
    username = admin_settings.username
    password = admin_settings.password
    existing = await AdminUser.get_or_none(username=username)
    if not existing:
        await AdminUser.create(username=username, password=password)


def _to_tortoise_url(sa_url: str) -> str:
    url = make_url(sa_url)
    dialect = url.get_backend_name()
    scheme = dialect
    if dialect == "postgresql":
        scheme = "postgres"
    if dialect == "mysql":
        scheme = "mysql"

    if scheme == "sqlite":
        database = url.database or ":memory:"
        if database.startswith("/"):
            return f"sqlite://{database}"
        return f"sqlite://{database}"

    auth = ""
    if url.username:
        auth = url.username
        if url.password:
            auth += f":{url.password}"
        auth += "@"
    host = url.host or "localhost"
    port = f":{url.port}" if url.port else ""
    database = url.database or ""
    query = ""
    if url.query:
        query = "?" + "&".join(f"{k}={v}" for k, v in url.query.items())
    return f"{scheme}://{auth}{host}{port}/{database}{query}"


@fastapi_admin_app.get("/")
async def admin_root(request: Request):
    if getattr(request.state, "admin", None):
        return RedirectResponse(
            url=f"./{RESOURCE_SLUG}/list",
            status_code=HTTP_303_SEE_OTHER,
        )
    return RedirectResponse(url="./login", status_code=HTTP_303_SEE_OTHER)
