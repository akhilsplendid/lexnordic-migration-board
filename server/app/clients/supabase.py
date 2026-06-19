from supabase import Client, create_client

from app.settings import Settings


def create_supabase_client(settings: Settings, *, service_role: bool = True) -> Client:
    if not settings.supabase_url:
        raise RuntimeError("SUPABASE_URL is not configured")

    secret = settings.supabase_service_role_key if service_role else (
        settings.supabase_publishable_key or settings.supabase_anon_key
    )
    key = settings.secret_value(secret)
    if not key:
        key_name = (
            "SUPABASE_SERVICE_ROLE_KEY"
            if service_role
            else "SUPABASE_PUBLISHABLE_KEY or SUPABASE_ANON_KEY"
        )
        raise RuntimeError(f"{key_name} is not configured")

    return create_client(settings.supabase_url, key)
