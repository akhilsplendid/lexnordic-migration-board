from __future__ import annotations

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.clients.qdrant import create_qdrant_client
from app.clients.supabase import create_supabase_client
from app.settings import get_settings


def check_qdrant() -> tuple[str, str]:
    settings = get_settings()
    if not settings.qdrant_url or not settings.qdrant_api_key:
        return "qdrant", "skipped: QDRANT_URL or QDRANT_API_KEY missing"

    client = create_qdrant_client(settings)
    collections = client.get_collections()
    names = [collection.name for collection in collections.collections]
    legal_count = "missing"
    if settings.qdrant_collection_legal_sources in names:
        legal_count = str(client.count(settings.qdrant_collection_legal_sources, exact=True).count)
    return "qdrant", (
        f"ok: {len(names)} collections visible; "
        f"{settings.qdrant_collection_legal_sources}={legal_count}"
    )


def check_supabase() -> tuple[str, str]:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return "supabase", "skipped: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing"

    client = create_supabase_client(settings)
    buckets = client.storage.list_buckets()
    matter_count = "not checked"
    try:
        response = client.table("matters").select("id", count="exact").limit(1).execute()
        matter_count = str(response.count)
    except Exception as exc:
        matter_count = f"schema not ready ({exc.__class__.__name__})"
    return "supabase", f"ok: storage API reachable ({len(buckets)} buckets); matters={matter_count}"


def _check_openai_compatible_models(
    *,
    name: str,
    base_url: str,
    api_key: str | None,
) -> tuple[str, str]:
    if not api_key:
        return name, "skipped: API key missing"

    url = f"{base_url.rstrip('/')}/models"
    with httpx.Client(timeout=15) as client:
        response = client.get(url, headers={"Authorization": f"Bearer {api_key}"})

    if response.status_code != 200:
        return name, f"error: /models returned HTTP {response.status_code}"

    try:
        payload = response.json()
    except ValueError:
        return name, "ok: /models reachable"

    data = payload.get("data") if isinstance(payload, dict) else None
    count = len(data) if isinstance(data, list) else "unknown"
    return name, f"ok: /models reachable ({count} models listed)"


def check_aiml() -> tuple[str, str]:
    settings = get_settings()
    return _check_openai_compatible_models(
        name="aiml",
        base_url=settings.aiml_base_url,
        api_key=settings.secret_value(settings.aiml_api_key),
    )


def check_featherless() -> tuple[str, str]:
    settings = get_settings()
    return _check_openai_compatible_models(
        name="featherless",
        base_url=settings.featherless_base_url,
        api_key=settings.secret_value(settings.featherless_api_key),
    )


def main() -> int:
    failed = False
    for check in (check_qdrant, check_supabase, check_aiml, check_featherless):
        name = check.__name__.replace("check_", "")
        try:
            name, result = check()
        except Exception as exc:
            result = f"error: {exc.__class__.__name__}: {exc}"
        print(f"{name}: {result}")
        if result.startswith("error:"):
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
