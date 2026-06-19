from qdrant_client import QdrantClient

from app.settings import Settings


def create_qdrant_client(settings: Settings) -> QdrantClient:
    if not settings.qdrant_url:
        raise RuntimeError("QDRANT_URL is not configured")

    api_key = settings.secret_value(settings.qdrant_api_key)
    return QdrantClient(url=settings.qdrant_url, api_key=api_key)
