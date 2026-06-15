"""User profile and learning schemas."""

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class TopicProficiency(BaseModel):
    topic: str
    score: float
    problems_attempted: int = 0
    problems_solved: int = 0


class ProfileResponse(BaseModel):
    id: UUID
    email: str
    username: str
    display_name: Optional[str] = None
    current_rating: int = 0
    total_problems_attempted: int = 0
    total_problems_solved: int = 0
    total_hints_used: int = 0
    topic_proficiency: dict[str, Any] = {}
    weak_topics: list[str] = []
    strong_topics: list[str] = []
    common_mistakes: list[dict[str, Any]] = []

    class Config:
        from_attributes = True
