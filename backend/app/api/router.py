"""Main API router aggregating all sub-routers."""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.problems import router as problems_router
from app.api.profile import router as profile_router
from app.api.sessions import router as sessions_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(sessions_router, prefix="/sessions", tags=["sessions"])
api_router.include_router(problems_router, prefix="/problems", tags=["problems"])
api_router.include_router(profile_router, prefix="/profile", tags=["profile"])
