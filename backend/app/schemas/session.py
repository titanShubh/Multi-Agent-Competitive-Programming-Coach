"""Session schemas."""

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    problem_statement: str = Field(..., min_length=10)
    constraints: Optional[str] = None
    session_mode: Literal["learning", "contest"] = "learning"
    timer_duration_minutes: Optional[int] = Field(None, ge=1, le=180)


class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    problem_id: Optional[UUID] = None
    problem_statement: str
    status: str
    session_mode: str
    hint_level: int
    max_hint_used: int
    problem_analysis: Optional[dict[str, Any]] = None
    timer_start: Optional[datetime] = None
    timer_duration_minutes: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int
