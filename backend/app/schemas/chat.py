"""Chat and streaming schemas."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    include_code: Optional[str] = None
    language: Optional[str] = None


class RejectedApproach(BaseModel):
    approach: str
    reason: str


class ReasoningFrame(BaseModel):
    current_understanding: str = ""
    key_observation: str = ""
    why_it_matters: str = ""
    possible_approaches: list[str] = []
    rejected_approaches: list[RejectedApproach] = []
    guiding_question: str = ""
    next_learning_objective: str = ""


class ChatResponse(BaseModel):
    content: str
    agent_name: str
    reasoning_frame: Optional[ReasoningFrame] = None
    hint_level: int = 0
    session_mode: str = "learning"


class StreamEvent(BaseModel):
    type: str  # token, agent_start, agent_end, reasoning_frame, done, error
    content: Optional[str] = None
    agent: Optional[str] = None
    reasoning_frame: Optional[dict[str, Any]] = None
    hint_level: Optional[int] = None
