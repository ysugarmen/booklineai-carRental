from __future__ import annotations
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.infra.storage.json_store import JsonStore

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Sets up logging on startup.
    """
    setup_logging()
    store = JsonStore(path=settings.DATA_FILE_PATH)

    yield


def create_app() -> FastAPI:
    """
    Create FastAPI application instance.
    """
    app = FastAPI(
        title="BookLineAI Car Rental Service",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()