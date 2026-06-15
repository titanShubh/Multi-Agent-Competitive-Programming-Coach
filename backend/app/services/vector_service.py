"""Qdrant vector database operations for semantic search."""

import uuid
from typing import Any, Optional

from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import get_settings

settings = get_settings()
COLLECTION_NAME = "cp_problems"


def get_embeddings_model() -> OpenAIEmbeddings:
    """Return configured OpenAI embeddings model."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=settings.openai_api_key or "mock-key",
    )


def init_collection(client: QdrantClient) -> None:
    """Initialize the Qdrant collection if it doesn't exist."""
    # check if collection exists (handling errors gracefully)
    try:
        exists = client.collection_exists(COLLECTION_NAME)
    except Exception:
        exists = False

    if not exists:
        try:
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=1536,  # text-embedding-3-small size
                    distance=models.Distance.COSINE
                )
            )
        except Exception:
            # Silence error if collection was created concurrently
            pass


async def store_problem(
    client: QdrantClient,
    problem_id: uuid.UUID,
    text: str,
    metadata: dict[str, Any]
) -> None:
    """Embed problem text and store it in Qdrant."""
    embeddings = get_embeddings_model()
    # Generate embedding vector
    vector = embeddings.embed_query(text)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            models.PointStruct(
                id=str(problem_id),
                vector=vector,
                payload=metadata
            )
        ]
    )


async def find_similar_problems(
    client: QdrantClient,
    query_text: str,
    limit: int = 5,
    filter_dict: Optional[dict[str, Any]] = None
) -> list[dict[str, Any]]:
    """Search for similar problems in Qdrant."""
    embeddings = get_embeddings_model()
    vector = embeddings.embed_query(query_text)

    qdrant_filter = None
    if filter_dict:
        conditions = []
        for key, value in filter_dict.items():
            if value is not None:
                conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )
        if conditions:
            qdrant_filter = models.Filter(must=conditions)

    try:
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=vector,
            query_filter=qdrant_filter,
            limit=limit
        )
    except Exception:
        # Fallback if collection doesn't exist
        return []

    return [
        {
            "id": hit.id,
            "score": hit.score,
            "metadata": hit.payload
        }
        for hit in search_result
    ]
