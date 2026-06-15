"""User profile and learning progress services."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LearningProfile, User


async def get_or_create_profile(db: AsyncSession, user_id: UUID) -> LearningProfile:
    """Retrieve the user learning profile, or create it if not present."""
    stmt = select(LearningProfile).where(LearningProfile.user_id == user_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()

    if not profile:
        profile = LearningProfile(
            user_id=user_id,
            topic_proficiency={},
            weak_topics=[],
            strong_topics=[],
            common_mistakes=[],
            total_problems_attempted=0,
            total_problems_solved=0,
            total_hints_used=0,
            updated_at=datetime.utcnow()
        )
        db.add(profile)
        await db.flush()

    return profile


async def update_proficiency(
    db: AsyncSession,
    user_id: UUID,
    topic: str,
    solved: bool,
    hints_used: int,
    mistakes: Optional[list[str]] = None
) -> LearningProfile:
    """Update user's topic proficiency and stats based on a problem attempt."""
    profile = await get_or_create_profile(db, user_id)
    
    # Update totals
    profile.total_problems_attempted += 1
    if solved:
        profile.total_problems_solved += 1
    profile.total_hints_used += hints_used

    # Update specific topic proficiency
    topic_prof = dict(profile.topic_proficiency or {})
    stats = topic_prof.get(topic, {"score": 0.5, "problems_attempted": 0, "problems_solved": 0})
    
    stats["problems_attempted"] += 1
    if solved:
        stats["problems_solved"] += 1
        # Solved: boost score. Penalty for hints.
        hint_penalty = min(0.4, hints_used * 0.1)
        stats["score"] = min(1.0, stats["score"] + (0.2 * (1.0 - hint_penalty)))
    else:
        # Failed: decrease score
        stats["score"] = max(0.0, stats["score"] - 0.15)
        
    topic_prof[topic] = stats
    profile.topic_proficiency = topic_prof

    # Re-evaluate weak/strong topics
    weak_topics = []
    strong_topics = []
    for t, data in topic_prof.items():
        score = data.get("score", 0.5)
        attempts = data.get("problems_attempted", 0)
        if attempts >= 1:
            if score < 0.4:
                weak_topics.append(t)
            elif score >= 0.7:
                strong_topics.append(t)
                
    profile.weak_topics = weak_topics
    profile.strong_topics = strong_topics

    # Track common mistakes
    if mistakes:
        curr_mistakes = list(profile.common_mistakes or [])
        for mistake in mistakes:
            found = False
            for entry in curr_mistakes:
                if entry.get("mistake") == mistake:
                    entry["count"] = entry.get("count", 0) + 1
                    found = True
                    break
            if not found:
                curr_mistakes.append({"mistake": mistake, "count": 1})
        profile.common_mistakes = curr_mistakes

    profile.updated_at = datetime.utcnow()
    await db.flush()
    return profile


async def get_learning_summary(db: AsyncSession, user_id: UUID) -> dict[str, Any]:
    """Compile a full dictionary summary of user stats and profile."""
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one()

    profile = await get_or_create_profile(db, user_id)
    
    return {
        "id": profile.id,
        "email": user.email,
        "username": user.username,
        "display_name": user.display_name,
        "current_rating": user.current_rating,
        "total_problems_attempted": profile.total_problems_attempted,
        "total_problems_solved": profile.total_problems_solved,
        "total_hints_used": profile.total_hints_used,
        "topic_proficiency": profile.topic_proficiency,
        "weak_topics": profile.weak_topics,
        "strong_topics": profile.strong_topics,
        "common_mistakes": profile.common_mistakes,
    }
