from __future__ import annotations
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.logging import setup_logging
from app.core.middleware import RateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Sets up logging on startup.
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")


def create_app() -> FastAPI:
    """
    Create FastAPI application instance.
    """
    app = FastAPI(
        title="BookLineAI Car Rental Service",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Simple rate limiting: 60 requests per minute per IP
    app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
    
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()