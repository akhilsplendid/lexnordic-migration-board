from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx

from app.main import app
from app.matters.workspace import DEMO_MATTER_NUMBER


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test the LexNordic matter workspace API.")
    parser.add_argument("--matter-number", default=DEMO_MATTER_NUMBER)
    return parser.parse_args()


async def fetch_workspace(matter_number: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(f"/matters/{matter_number}/workspace")


def main() -> int:
    args = parse_args()
    response = asyncio.run(fetch_workspace(args.matter_number))
    if response.status_code != 200:
        print(response.text)
        return 1

    workspace = response.json()
    required_keys = {
        "matter",
        "readiness",
        "evidence_items",
        "source_bundle",
        "extraction_feed",
        "agent_activity",
        "review_packet",
    }
    missing = sorted(required_keys - set(workspace))
    if missing:
        print(f"missing workspace keys: {missing}")
        return 1
    if not workspace["evidence_items"]:
        print("workspace has no evidence items")
        return 1
    if not workspace["agent_activity"]:
        print("workspace has no agent activity")
        return 1

    summary = {
        "matter_number": workspace["matter"]["matter_number"],
        "readiness": workspace["readiness"]["score"],
        "packet_gate": workspace["readiness"]["packet_gate"]["state"],
        "evidence_items": len(workspace["evidence_items"]),
        "agent_activity": len(workspace["agent_activity"]),
        "source_bundle": len(workspace["source_bundle"]),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
