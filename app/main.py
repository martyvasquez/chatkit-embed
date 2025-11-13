from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .admin import init_admin
from .config import get_settings
from .database import init_db
from .routes import chatkit, embed

settings = get_settings()

app = FastAPI(title="ChatKit Embed Host", version="0.1.0")

if settings.allowed_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.allowed_cors_origins],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(embed.router)
app.include_router(chatkit.router)


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    await init_admin(app)
