from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.clients.embeddings import AimlEmbeddingClient
from app.clients.qdrant import create_qdrant_client
from app.legal.retrieval import LegalRetriever
from app.settings import get_settings


router = APIRouter(prefix="/legal", tags=["legal"])


class LegalSearchRequest(BaseModel):
    query: str = Field(min_length=3)
    limit: int = Field(default=8, ge=1, le=25)
    source_types: list[str] | None = None
    permit_type: str | None = None
    mig_id: str | None = None
    legal_issue: str | None = None


class CitationBundleRequest(BaseModel):
    queries: list[str] = Field(min_length=1, max_length=8)
    limit_per_query: int = Field(default=5, ge=1, le=10)
    source_types: list[str] | None = None
    permit_type: str | None = None


@router.get("/collection")
def legal_collection() -> dict[str, Any]:
    settings = get_settings()
    try:
        qdrant = create_qdrant_client(settings)
        exists = qdrant.collection_exists(settings.qdrant_collection_legal_sources)
        count = (
            qdrant.count(settings.qdrant_collection_legal_sources, exact=True).count
            if exists
            else 0
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Qdrant unavailable: {exc}") from exc

    return {
        "collection": settings.qdrant_collection_legal_sources,
        "exists": exists,
        "points": count,
        "embedding_model": settings.legal_embedding_model,
        "embedding_dimension": settings.legal_embedding_dimension,
    }


@router.post("/search")
def legal_search(request: LegalSearchRequest) -> dict[str, Any]:
    retriever = _retriever()
    try:
        results = retriever.search(
            query=request.query,
            limit=request.limit,
            source_types=request.source_types,
            permit_type=request.permit_type,
            mig_id=request.mig_id,
            legal_issue=request.legal_issue,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Legal retrieval failed: {exc}") from exc

    return {
        "query": request.query,
        "results": [_serialize_result(result) for result in results],
    }


@router.post("/citation-bundle")
def citation_bundle(request: CitationBundleRequest) -> dict[str, Any]:
    retriever = _retriever()
    try:
        results = retriever.citation_bundle(
            queries=request.queries,
            limit_per_query=request.limit_per_query,
            source_types=request.source_types,
            permit_type=request.permit_type,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Citation bundle failed: {exc}") from exc

    return {
        "queries": request.queries,
        "results": [_serialize_result(result) for result in results],
    }


def _retriever() -> LegalRetriever:
    settings = get_settings()
    return LegalRetriever(
        qdrant=create_qdrant_client(settings),
        embeddings=AimlEmbeddingClient.from_settings(settings),
        settings=settings,
    )


def _serialize_result(result: Any) -> dict[str, Any]:
    return {
        "point_id": result.point_id,
        "score": result.score,
        "chunk_id": result.chunk_id,
        "source_id": result.source_id,
        "source_type": result.source_type,
        "title": result.title,
        "citation": result.citation,
        "url": result.url,
        "snippet": _snippet(result.text),
        "metadata": result.metadata,
    }


def _snippet(text: str, max_chars: int = 700) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "..."
