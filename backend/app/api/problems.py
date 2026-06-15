"""Problem management API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from qdrant_client import QdrantClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Problem, User
from app.dependencies import get_current_user, get_db, get_qdrant_client
from app.schemas.problem import ProblemCreate, ProblemResponse
from app.services.vector_service import store_problem

router = APIRouter()


@router.post("/", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    data: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    qdrant: QdrantClient = Depends(get_qdrant_client),
):
    """Create a new problem, save to DB, and index in Qdrant."""
    problem = Problem(
        title=data.title,
        statement=data.statement,
        constraints=data.constraints,
        input_format=data.input_format,
        output_format=data.output_format,
        sample_io=data.sample_io,
        source=data.source,
        source_id=data.source_id,
        source_url=data.source_url,
        difficulty=data.difficulty,
        estimated_rating=data.estimated_rating,
        categories=data.categories,
        tags=data.tags
    )
    db.add(problem)
    await db.flush()  # Populates problem.id

    # Index in Qdrant for similarity search
    # Construct index text: title + statement + categories + tags
    categories_str = ", ".join(data.categories)
    tags_str = ", ".join(data.tags)
    index_text = f"Title: {data.title}\nStatement: {data.statement}\nCategories: {categories_str}\nTags: {tags_str}"
    
    metadata = {
        "title": data.title,
        "difficulty": data.difficulty,
        "estimated_rating": data.estimated_rating,
        "categories": data.categories,
        "tags": data.tags,
    }
    
    try:
        await store_problem(qdrant, problem.id, index_text, metadata)
    except Exception as e:
        # We don't fail the HTTP request if vector indexing fails, but log it
        print(f"Qdrant indexing failed: {e}")

    return problem


@router.get("/", response_model=list[ProblemResponse])
async def list_problems(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve problems with optional category and difficulty filtering."""
    stmt = select(Problem)
    if category:
        stmt = stmt.where(Problem.categories.any(category))
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    
    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a single problem by its unique ID."""
    stmt = select(Problem).where(Problem.id == problem_id)
    result = await db.execute(stmt)
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found"
        )
    return problem
