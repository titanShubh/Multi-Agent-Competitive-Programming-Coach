"""Coaching session database operations."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CoachingSession, Message
from app.schemas.session import SessionCreate


async def create_session(db: AsyncSession, user_id: UUID, data: SessionCreate) -> CoachingSession:
    """Create a new coaching session."""
    session = CoachingSession(
        user_id=user_id,
        problem_statement=data.problem_statement,
        session_mode=data.session_mode,
        timer_duration_minutes=data.timer_duration_minutes,
        timer_start=datetime.utcnow() if data.timer_duration_minutes else None,
        status="active",
        started_at=datetime.utcnow(),
    )
    db.add(session)
    await db.flush()
    return session


async def get_session(db: AsyncSession, session_id: UUID, user_id: UUID) -> Optional[CoachingSession]:
    """Retrieve a coaching session by ID and user ID."""
    stmt = select(CoachingSession).where(
        CoachingSession.id == session_id,
        CoachingSession.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_sessions(
    db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 10
) -> tuple[list[CoachingSession], int]:
    """List coaching sessions with pagination and total count."""
    count_stmt = select(func.count()).select_from(CoachingSession).where(CoachingSession.user_id == user_id)
    count_res = await db.execute(count_stmt)
    total = count_res.scalar_one()

    stmt = (
        select(CoachingSession)
        .where(CoachingSession.user_id == user_id)
        .order_by(desc(CoachingSession.started_at))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    sessions = list(result.scalars().all())
    return sessions, total


async def update_session(
    db: AsyncSession, session_id: UUID, user_id: UUID, updates: dict[str, Any]
) -> Optional[CoachingSession]:
    """Update attributes of an existing session."""
    session = await get_session(db, session_id, user_id)
    if not session:
        return None

    for key, value in updates.items():
        if hasattr(session, key):
            setattr(session, key, value)

    await db.flush()
    return session


async def save_message(
    db: AsyncSession,
    session_id: UUID,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> Message:
    """Save a chat message in a session."""
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        agent_name=agent_name,
        message_metadata=metadata,
        created_at=datetime.utcnow(),
    )
    db.add(message)
    await db.flush()
    return message


async def get_messages(db: AsyncSession, session_id: UUID) -> list[Message]:
    """Get all messages for a coaching session sorted by creation time."""
    stmt = select(Message).where(Message.session_id == session_id).order_by(Message.created_at)
    result = await db.execute(stmt)
    return list(result.scalars().all())
