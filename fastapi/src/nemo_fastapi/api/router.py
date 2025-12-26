"""Shared API router for the FastAPI backend."""

from fastapi import APIRouter

from nemo_fastapi.api.v1.endpoints import health, legacy

api_router = APIRouter()
api_router.include_router(health.router, prefix="/api/v1")
api_router.include_router(legacy.router, prefix="/api/v1")
