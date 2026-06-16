"""Authentication endpoints."""


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.dependencies import get_db
from app.schemas.auth import Token, UserLogin, UserRegister
from app.services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user and return an access token."""
    # Check if email exists
    email_stmt = select(User).where(User.email == data.email)
    email_res = await db.execute(email_stmt)
    if email_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    username_stmt = select(User).where(User.username == data.username)
    username_res = await db.execute(username_stmt)
    if username_res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    new_user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        display_name=data.display_name or data.username,
        current_rating=0
    )
    db.add(new_user)
    await db.flush()  # Populates new_user.id

    access_token = create_access_token(data={"sub": str(new_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user credentials and return an access token."""
    stmt = select(User).where(User.email == data.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
