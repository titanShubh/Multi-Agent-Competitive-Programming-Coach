"""Shared state definition for the multi-agent coaching graph."""

from typing import Annotated, Any, Literal, Optional, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ReasoningFrame(TypedDict, total=False):
    """Structured pedagogical reasoning exposed to the student."""
    current_understanding: str
    key_observation: str
    why_it_matters: str
    possible_approaches: list[str]
    rejected_approaches: list[dict[str, str]]  # [{"approach": ..., "reason": ...}]
    guiding_question: str
    next_learning_objective: str


class ProblemAnalysis(TypedDict, total=False):
    """Structured output from the Problem Analyzer agent."""
    title: str
    summary: str
    categories: list[str]
    difficulty: str
    estimated_rating: int
    constraints: dict[str, Any]
    key_observations: list[str]
    hidden_observations: list[str]
    expected_complexity: str
    brute_force_complexity: str
    similar_problems: list[str]


class CoachState(TypedDict):
    """Central state shared across all agents in the coaching graph."""
    messages: Annotated[list[AnyMessage], add_messages]
    problem_statement: str
    problem_analysis: Optional[ProblemAnalysis]
    hint_level: int
    max_hint_used: int
    session_mode: Literal["learning", "contest"]
    current_agent: str
    next_agent: str
    reasoning_frame: Optional[ReasoningFrame]
    user_profile: Optional[dict[str, Any]]
    user_code: Optional[str]
    code_language: Optional[str]
    session_id: str
    user_id: str
