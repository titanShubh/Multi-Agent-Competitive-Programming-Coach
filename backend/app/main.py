"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient

from app.api.router import api_router
from app.config import get_settings
from app.services.vector_service import init_collection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    try:
        from app.db.database import engine
        from app.db.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize database tables: {e}")

    # Startup: Seed demo user if not exists
    try:
        from sqlalchemy import select
        from app.db.database import async_session_factory
        from app.db.models import User
        from app.services.auth_service import hash_password
        
        async with async_session_factory() as session:
            stmt = select(User).where(User.email == "demo@coach.com")
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                demo_user = User(
                    email="demo@coach.com",
                    username="demo_user",
                    password_hash=hash_password("demopass123"),
                    display_name="Demo Candidate",
                    current_rating=1200
                )
                session.add(demo_user)
                await session.commit()
                print("Demo user seeded successfully (demo@coach.com / demopass123).")
            else:
                print("Demo user already exists.")
    except Exception as e:
        print(f"Failed to seed demo user: {e}")

    # Startup: Initialize Qdrant collection
    try:
        if settings.qdrant_api_key:
            qdrant = QdrantClient(
                url=f"https://{settings.qdrant_host}" if not settings.qdrant_host.startswith("http") else settings.qdrant_host,
                api_key=settings.qdrant_api_key,
            )
        else:
            qdrant = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        init_collection(qdrant)
    except Exception as e:
        print(f"Failed to initialize Qdrant collection: {e}")
    yield
    # Shutdown: Clean up connections if needed


app = FastAPI(
    title="Multi-Agent Competitive Programming Coach API",
    description="Backend API for Socratic CP mentoring and code review",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "Welcome to the Multi-Agent Competitive Programming Coach API.",
        "docs": "/docs"
    }
