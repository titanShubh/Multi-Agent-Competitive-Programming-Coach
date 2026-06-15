"""Problem schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProblemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    statement: str = Field(..., min_length=10)
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    sample_io: Optional[list[dict[str, Any]]] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_rating: Optional[int] = None
    categories: list[str] = []
    tags: list[str] = []


class ProblemResponse(BaseModel):
    id: UUID
    title: str
    statement: str
    constraints: Optional[str] = None
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    sample_io: Optional[list[dict[str, Any]]] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_rating: Optional[int] = None
    categories: list[str] = []
    tags: list[str] = []
    created_at: datetime

    class Config:
        from_attributes = True
