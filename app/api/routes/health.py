"""Health check endpoints for monitoring and container orchestration."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """
    Health check endpoint for load balancers and container orchestration.
    
    Returns service status and version information.
    """
    return HealthResponse(status="healthy", version="1.0.0")
