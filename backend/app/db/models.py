"""SQLAlchemy ORM models."""

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ARRAY, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_rating: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions: Mapped[list["CoachingSession"]] = relationship("CoachingSession", back_populates="user", cascade="all, delete-orphan")
    learning_profile: Mapped[Optional["LearningProfile"]] = relationship("LearningProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    attempts: Mapped[list["ProblemAttempt"]] = relationship("ProblemAttempt", back_populates="user", cascade="all, delete-orphan")


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    input_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_format: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sample_io: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)  # List of dicts [{"input": ..., "output": ...}]
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sessions: Mapped[list["CoachingSession"]] = relationship("CoachingSession", back_populates="problem")
    attempts: Mapped[list["ProblemAttempt"]] = relationship("ProblemAttempt", back_populates="problem")


class CoachingSession(Base):
    __tablename__ = "coaching_sessions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("problems.id", ondelete="SET NULL"), nullable=True, index=True)
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # active, completed, abandoned
    session_mode: Mapped[str] = mapped_column(String(50), default="learning", nullable=False)  # learning, contest
    hint_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_hint_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    problem_analysis: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)  # Structured analysis JSON
    timer_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    timer_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    problem: Mapped[Optional["Problem"]] = relationship("Problem", back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    attempts: Mapped[list["ProblemAttempt"]] = relationship("ProblemAttempt", back_populates="session", cascade="all, delete-orphan")
    hint_progressions: Mapped[list["HintProgression"]] = relationship("HintProgression", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("coaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message_metadata: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)  # For reasoning_frame, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session: Mapped["CoachingSession"] = relationship("CoachingSession", back_populates="messages")


class LearningProfile(Base):
    __tablename__ = "learning_profiles"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    topic_proficiency: Mapped[Any] = mapped_column(JSONB, default=dict, nullable=False)  # {"DP": 0.8, "Graphs": 0.4}
    weak_topics: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    strong_topics: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    common_mistakes: Mapped[Any] = mapped_column(JSONB, default=list, nullable=False)  # List of {"mistake": ..., "count": ...}
    total_problems_attempted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_problems_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="learning_profile")


class ProblemAttempt(Base):
    __tablename__ = "problem_attempts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id: Mapped[Optional[uuid.UUID]] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("problems.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("coaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    solved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hints_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_hint_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    code_submitted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mistakes_made: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    solved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="attempts")
    problem: Mapped[Optional["Problem"]] = relationship("Problem", back_populates="attempts")
    session: Mapped["CoachingSession"] = relationship("CoachingSession", back_populates="attempts")


class HintProgression(Base):
    __tablename__ = "hint_progressions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("coaching_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    hint_level: Mapped[int] = mapped_column(Integer, nullable=False)
    hint_type: Mapped[str] = mapped_column(String(100), nullable=False)  # observation, direction, algorithm, pseudocode, solution
    hint_content: Mapped[str] = mapped_column(Text, nullable=False)
    revealed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    was_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Relationships
    session: Mapped["CoachingSession"] = relationship("CoachingSession", back_populates="hint_progressions")
