from fastapi import APIRouter

from app.settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, object]:
    settings = get_settings()
    return {
        "ok": True,
        "app": settings.app_name,
        "environment": settings.app_env,
        "configured": {
            "supabase_url": bool(settings.supabase_url),
            "supabase_publishable_key": bool(settings.supabase_publishable_key),
            "supabase_service_role_key": bool(settings.supabase_service_role_key),
            "qdrant_url": bool(settings.qdrant_url),
            "qdrant_api_key": bool(settings.qdrant_api_key),
            "aiml_api_key": bool(settings.aiml_api_key),
            "featherless_api_key": bool(settings.featherless_api_key),
            "band_room_id": bool(settings.band_room_id),
        },
    }
