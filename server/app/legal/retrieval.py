from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient, models

from app.clients.embeddings import AimlEmbeddingClient
from app.legal.source_documents import LegalChunk
from app.settings import Settings


PAYLOAD_INDEXES: dict[str, models.PayloadSchemaType] = {
    "source_type": models.PayloadSchemaType.KEYWORD,
    "permit_type": models.PayloadSchemaType.KEYWORD,
    "mig_id": models.PayloadSchemaType.KEYWORD,
    "legal_issue": models.PayloadSchemaType.KEYWORD,
    "workflow_stage": models.PayloadSchemaType.KEYWORD,
    "source_id": models.PayloadSchemaType.KEYWORD,
    "year": models.PayloadSchemaType.INTEGER,
}


@dataclass(frozen=True)
class LegalSearchResult:
    point_id: str
    score: float
    chunk_id: str
    source_id: str
    source_type: str
    title: str
    citation: str
    text: str
    url: str | None
    metadata: dict[str, Any]


def ensure_legal_collection(
    *,
    qdrant: QdrantClient,
    settings: Settings,
    recreate: bool = False,
) -> None:
    collection_name = settings.qdrant_collection_legal_sources
    exists = qdrant.collection_exists(collection_name)
    if exists and recreate:
        qdrant.delete_collection(collection_name)
        exists = False

    if not exists:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=settings.legal_embedding_dimension,
                distance=models.Distance.COSINE,
            ),
        )
    ensure_payload_indexes(qdrant=qdrant, collection_name=collection_name)


def ensure_payload_indexes(*, qdrant: QdrantClient, collection_name: str) -> None:
    for field_name, field_schema in PAYLOAD_INDEXES.items():
        try:
            qdrant.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=field_schema,
                wait=True,
            )
        except Exception as exc:
            message = str(exc).lower()
            if "already exists" not in message and "already has" not in message:
                raise


def point_id_for_chunk(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"lexnordic:{chunk_id}"))


def upsert_legal_chunks(
    *,
    qdrant: QdrantClient,
    settings: Settings,
    chunks: list[LegalChunk],
    vectors: list[list[float]],
) -> None:
    if len(chunks) != len(vectors):
        raise ValueError("chunks and vectors must have the same length")

    points = [
        models.PointStruct(
            id=point_id_for_chunk(chunk.chunk_id),
            vector=vector,
            payload={
                **chunk.payload,
                "qdrant_point_id": point_id_for_chunk(chunk.chunk_id),
                "embedding_model": settings.legal_embedding_model,
            },
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]
    qdrant.upsert(
        collection_name=settings.qdrant_collection_legal_sources,
        points=points,
        wait=True,
    )


class LegalRetriever:
    def __init__(
        self,
        *,
        qdrant: QdrantClient,
        embeddings: AimlEmbeddingClient,
        settings: Settings,
    ) -> None:
        self.qdrant = qdrant
        self.embeddings = embeddings
        self.settings = settings

    def search(
        self,
        *,
        query: str,
        limit: int | None = None,
        source_types: list[str] | None = None,
        permit_type: str | None = None,
        mig_id: str | None = None,
        legal_issue: str | None = None,
    ) -> list[LegalSearchResult]:
        vector = self.embeddings.embed_texts([query])[0]
        response = self.qdrant.query_points(
            collection_name=self.settings.qdrant_collection_legal_sources,
            query=vector,
            query_filter=_build_filter(
                source_types=source_types,
                permit_type=permit_type,
                mig_id=mig_id,
                legal_issue=legal_issue,
            ),
            limit=limit or self.settings.legal_retrieval_default_limit,
            with_payload=True,
            with_vectors=False,
        )
        return [_result_from_point(point) for point in response.points]

    def citation_bundle(
        self,
        *,
        queries: list[str],
        limit_per_query: int = 5,
        source_types: list[str] | None = None,
        permit_type: str | None = None,
    ) -> list[LegalSearchResult]:
        seen: set[str] = set()
        bundle: list[LegalSearchResult] = []
        for query in queries:
            for result in self.search(
                query=query,
                limit=limit_per_query,
                source_types=source_types,
                permit_type=permit_type,
            ):
                if result.point_id in seen:
                    continue
                seen.add(result.point_id)
                bundle.append(result)
        bundle.sort(key=lambda item: item.score, reverse=True)
        return bundle


def _build_filter(
    *,
    source_types: list[str] | None,
    permit_type: str | None,
    mig_id: str | None,
    legal_issue: str | None,
) -> models.Filter | None:
    conditions: list[models.FieldCondition] = []
    if source_types:
        conditions.append(_match_condition("source_type", source_types))
    if permit_type:
        conditions.append(_match_condition("permit_type", [permit_type]))
    if mig_id:
        conditions.append(_match_condition("mig_id", [mig_id]))
    if legal_issue:
        conditions.append(_match_condition("legal_issue", [legal_issue]))

    if not conditions:
        return None
    return models.Filter(must=conditions)


def _match_condition(key: str, values: list[str]) -> models.FieldCondition:
    clean_values = [value for value in values if value]
    if len(clean_values) == 1:
        return models.FieldCondition(
            key=key,
            match=models.MatchValue(value=clean_values[0]),
        )
    return models.FieldCondition(
        key=key,
        match=models.MatchAny(any=clean_values),
    )


def _result_from_point(point: Any) -> LegalSearchResult:
    payload = point.payload or {}
    known_keys = {
        "chunk_id",
        "source_id",
        "source_type",
        "title",
        "citation",
        "text",
        "url",
    }
    metadata = {key: value for key, value in payload.items() if key not in known_keys}
    return LegalSearchResult(
        point_id=str(point.id),
        score=float(point.score),
        chunk_id=str(payload.get("chunk_id", "")),
        source_id=str(payload.get("source_id", "")),
        source_type=str(payload.get("source_type", "")),
        title=str(payload.get("title", "")),
        citation=str(payload.get("citation", "")),
        text=str(payload.get("text", "")),
        url=payload.get("url"),
        metadata=metadata,
    )
