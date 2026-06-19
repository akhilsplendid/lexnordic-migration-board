from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx
import yaml
from band import AgentRuntime, AgentTools, BandLink, SessionConfig
from band.platform.event import MessageEvent
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(__file__).with_name("agent_config.example.yaml")
PROMPT_DIR = Path(__file__).with_name("prompts")
DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"
DEMO_MATTER_NUMBER = "LX-MIG-2026-001"

ROLE_PROVIDERS = {
    "intake": "featherless",
    "conflict_kyc": "featherless",
    "decision_parser": "featherless",
    "evidence": "featherless",
    "legal_source": "aiml",
    "risk": "featherless",
    "appeal_packet": "aiml",
    "partner_review": "aiml",
}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run a LexNordic Band remote agent.")
    parser.add_argument("--role", choices=sorted(ROLE_PROVIDERS), required=True)
    parser.add_argument("--message", default="Review the current LexNordic demo matter.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--backend-url", default=os.getenv("LEXNORDIC_BACKEND_URL", DEFAULT_BACKEND_URL))
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env.local")
    load_dotenv(PROJECT_ROOT / ".env")
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.dry_run:
        workspace = await fetch_workspace(args.backend_url)
        print(await build_reply(args.role, args.message, workspace))
        return

    role_config = load_role_config(args.role)
    agent_id = os.getenv(role_config["agent_id_env"])
    api_key = os.getenv(role_config["api_key_env"])
    if not agent_id or not api_key:
        raise SystemExit(
            f"Missing Band credentials for {args.role}: "
            f"{role_config['agent_id_env']} / {role_config['api_key_env']}"
        )

    band_room_id = os.getenv("BAND_ROOM_ID")
    ws_url = os.getenv("BAND_WS_URL", "wss://app.band.ai/api/v1/socket/websocket")
    rest_url = os.getenv("BAND_API_BASE_URL", "https://app.band.ai")

    async def on_execute(ctx: Any, event: Any) -> None:
        if not isinstance(event, MessageEvent) or not event.payload:
            return
        if event.payload.sender_id == agent_id:
            return
        workspace = await fetch_workspace(args.backend_url)
        reply = await build_reply(args.role, event.payload.content, workspace)
        await AgentTools.from_context(ctx).send_message(reply)

    link = BandLink(agent_id=agent_id, api_key=api_key, ws_url=ws_url, rest_url=rest_url)
    runtime = AgentRuntime(
        link=link,
        agent_id=agent_id,
        on_execute=on_execute,
        room_filter=(lambda room: not band_room_id or str(room.get("id")) == band_room_id),
        session_config=SessionConfig(max_context_messages=40),
    )
    logging.info("Running LexNordic Band agent role=%s", args.role)
    await runtime.run()


async def build_reply(role: str, message: str, workspace: dict[str, Any]) -> str:
    provider = ROLE_PROVIDERS[role]
    prompt = read_prompt(role)
    deterministic = deterministic_reply(role, workspace)
    model_reply = await complete_with_provider(
        provider=provider,
        role=role,
        system_prompt=prompt,
        message=message,
        workspace=workspace,
    )
    reply = model_reply or deterministic
    return f"{reply}\n\nCoordination status: `{role}` completed its Band handoff. No authority filing is triggered automatically."


async def complete_with_provider(
    *,
    provider: str,
    role: str,
    system_prompt: str,
    message: str,
    workspace: dict[str, Any],
) -> str | None:
    if provider == "aiml":
        api_key = os.getenv("AIML_API_KEY")
        base_url = os.getenv("AIML_BASE_URL", "https://api.aimlapi.com/v1")
        model = os.getenv("AIML_CHAT_MODEL")
    else:
        api_key = os.getenv("FEATHERLESS_API_KEY")
        base_url = os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1")
        model = os.getenv("FEATHERLESS_CHAT_MODEL")

    if not api_key or not model:
        return None

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "role": role,
                        "incoming_message": message,
                        "workspace": compact_workspace(workspace),
                    },
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
        data = response.json()
        return str(data["choices"][0]["message"]["content"]).strip()
    except Exception as exc:
        logging.warning("Provider call failed for %s/%s: %s", provider, role, exc.__class__.__name__)
        return None


async def fetch_workspace(backend_url: str) -> dict[str, Any]:
    url = f"{backend_url.rstrip('/')}/matters/{DEMO_MATTER_NUMBER}/workspace"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception:
        return {
            "matter": {"matter_number": DEMO_MATTER_NUMBER, "route": "Work Permit (Higher Ed)"},
            "readiness": {"score": 42, "packet_gate": {"state": "locked"}},
            "missing_facts": ["Job offer start date", "Monthly gross salary"],
            "evidence_items": [],
            "source_bundle": [],
            "agent_activity": [],
        }


def deterministic_reply(role: str, workspace: dict[str, Any]) -> str:
    readiness = workspace.get("readiness", {})
    evidence = workspace.get("evidence_items", [])
    missing = [
        item.get("requirement", "evidence")
        for item in evidence
        if item.get("status_label") in {"Missing", "Requested", "Risk found"}
    ]
    score = readiness.get("score", 0)
    source_count = len(workspace.get("source_bundle", []))
    if role == "intake":
        return f"Intake normalized the route as {workspace.get('matter', {}).get('route')}. Readiness is {score}%."
    if role == "evidence":
        return f"Evidence check found open items: {', '.join(missing) or 'none'}."
    if role == "legal_source":
        return f"Legal source review attached {source_count} source references for the route."
    if role == "risk":
        return f"Risk review marks packet readiness as {readiness.get('packet_gate', {}).get('state')}; threshold evidence controls final packet status."
    if role == "appeal_packet":
        return "AI case packet assembled from evidence, source bundle, and risk notes."
    if role == "partner_review":
        return "Partner review marks the packet as saved consultation material; no autonomous filing."
    if role == "conflict_kyc":
        return "Conflict/KYC screen is clear for fictional demo data only."
    return "Decision parser extracted route, facts, documents, and review blockers."


def compact_workspace(workspace: dict[str, Any]) -> dict[str, Any]:
    return {
        "matter": workspace.get("matter"),
        "readiness": workspace.get("readiness"),
        "missing_facts": workspace.get("missing_facts", []),
        "evidence_items": workspace.get("evidence_items", [])[:8],
        "source_bundle": workspace.get("source_bundle", [])[:5],
        "review_packet": workspace.get("review_packet"),
    }


def read_prompt(role: str) -> str:
    path = PROMPT_DIR / f"{role}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "You are a LexNordic migration-law workflow agent. Be concise, sourced, and cautious."


def load_role_config(role: str) -> dict[str, str]:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    return config[role]


if __name__ == "__main__":
    asyncio.run(main())
