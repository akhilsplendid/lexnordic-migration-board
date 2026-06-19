from __future__ import annotations

from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.settings import Settings, get_settings


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    id: str
    email: str | None
    access_token: str


def require_auth_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser:
    user = optional_auth_user(credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Supabase sign-in required")
    return user


def optional_auth_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthUser | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    token = credentials.credentials.strip()
    if not token:
        return None
    return verify_supabase_token(token, get_settings())


def verify_supabase_token(token: str, settings: Settings) -> AuthUser:
    if not settings.supabase_url:
        raise HTTPException(status_code=503, detail="Supabase Auth is not configured")

    api_key = (
        settings.secret_value(settings.supabase_publishable_key)
        or settings.secret_value(settings.supabase_anon_key)
        or settings.secret_value(settings.supabase_service_role_key)
    )
    if not api_key:
        raise HTTPException(status_code=503, detail="Supabase Auth key is not configured")

    try:
        response = httpx.get(
            f"{settings.supabase_url.rstrip('/')}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": api_key,
            },
            timeout=10,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Supabase Auth verification unavailable") from exc

    if response.status_code in {401, 403}:
        raise HTTPException(status_code=401, detail="Invalid or expired Supabase session")
    if response.status_code >= 400:
        raise HTTPException(status_code=503, detail="Supabase Auth verification failed")

    payload = response.json()
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid Supabase session")

    return AuthUser(id=user_id, email=payload.get("email"), access_token=token)
