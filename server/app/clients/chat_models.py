from __future__ import annotations

import json
from typing import Any

import httpx

from app.clients.model_router import ModelProvider
from app.settings import Settings


def complete_chat(
    *,
    settings: Settings,
    provider: ModelProvider,
    system_prompt: str,
    user_payload: dict[str, Any],
    max_tokens: int = 700,
) -> str | None:
    """Optional provider call for wording. Deterministic app logic owns decisions."""
    if provider == ModelProvider.AIML:
        api_key = settings.secret_value(settings.aiml_api_key)
        base_url = settings.aiml_base_url
        model = settings.aiml_chat_model
    else:
        api_key = settings.secret_value(settings.featherless_api_key)
        base_url = settings.featherless_base_url
        model = settings.featherless_chat_model

    if not api_key or not model:
        return None

    try:
        with httpx.Client(timeout=35) as client:
            response = client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                    ],
                    "temperature": 0.2,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
    except Exception:
        return None

    data = response.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    return str(content).strip() or None
