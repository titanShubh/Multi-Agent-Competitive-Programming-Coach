"""User profile and learning progress endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.dependencies import get_db, get_current_user
from app.schemas.profile import ProfileResponse
from app.services.user_service import get_learning_summary

router = APIRouter()


@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve learning statistics and profile for the current authenticated user."""
    summary = await get_learning_summary(db, current_user.id)
    return summary
