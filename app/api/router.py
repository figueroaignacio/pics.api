"""Aggregate API router."""

from fastapi import APIRouter

from app.api.routes.categories import router as categories_router
from app.api.routes.health import router as health_router
from app.api.routes.photos import router as photos_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(categories_router)
api_router.include_router(photos_router)
