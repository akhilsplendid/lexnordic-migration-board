from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.clients.postgres import connect_postgres
from app.clients.supabase import create_supabase_client
from app.matters.workspace import default_agent_runs, default_evidence_rows
from app.settings import get_settings


MIGRATIONS_DIR = ROOT / "database" / "migrations"
DEMO_MATTER_NUMBER = "LX-MIG-2026-001"


def apply_migrations() -> list[str]:
    settings = get_settings()
    applied: list[str] = []
    migration_paths = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_paths:
        raise RuntimeError(f"No SQL migrations found in {MIGRATIONS_DIR}")

    with connect_postgres(settings) as connection:
        for path in migration_paths:
            sql = path.read_text(encoding="utf-8")
            with connection.transaction():
                connection.execute(sql)
            applied.append(path.name)
    return applied


def ensure_storage_bucket() -> str:
    settings = get_settings()
    bucket_name = settings.supabase_storage_bucket
    client = create_supabase_client(settings)
    buckets = client.storage.list_buckets()
    existing = {getattr(bucket, "id", None) or getattr(bucket, "name", None) for bucket in buckets}

    options = {
        "public": False,
        "file_size_limit": 20 * 1024 * 1024,
        "allowed_mime_types": [
            "application/pdf",
            "image/png",
            "image/jpeg",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ],
    }

    if bucket_name in existing:
        client.storage.update_bucket(bucket_name, options)
        return "updated"

    client.storage.create_bucket(bucket_name, options=options)
    return "created"


def cleanup_demo_storage() -> int:
    settings = get_settings()
    bucket = create_supabase_client(settings).storage.from_(settings.supabase_storage_bucket)
    try:
        objects = bucket.list(DEMO_MATTER_NUMBER)
    except Exception:
        return 0
    paths = [
        f"{DEMO_MATTER_NUMBER}/{name}"
        for item in objects
        if (name := _storage_object_name(item))
    ]
    if paths:
        bucket.remove(paths)
    return len(paths)


def seed_demo_matter() -> str:
    settings = get_settings()
    with connect_postgres(settings) as connection:
        row = connection.execute(
            """
            insert into public.matters (
              matter_number,
              title,
              case_type,
              status,
              jurisdiction,
              permit_type,
              applicant_alias,
              employer_name,
              band_room_id,
              qdrant_collection,
              summary,
              metadata
            )
            values (
              %(matter_number)s,
              'Fictional work-permit refusal appeal readiness',
              'work_permit_appeal',
              'intake',
              'SE',
              'work_permit',
              'Applicant A',
              'Nordic Systems AB',
              %(band_room_id)s,
              %(qdrant_collection)s,
              'Demo matter for the Band hackathon: prepare an appeal-readiness packet for a fictional Swedish work-permit refusal.',
              '{"fixture": true, "contains_real_personal_data": false}'::jsonb
            )
            on conflict (matter_number) do update
            set
              band_room_id = excluded.band_room_id,
              qdrant_collection = excluded.qdrant_collection,
              updated_at = now()
            returning id
            """,
            {
                "matter_number": DEMO_MATTER_NUMBER,
                "band_room_id": settings.band_room_id,
                "qdrant_collection": settings.qdrant_collection_legal_sources,
            },
        ).fetchone()

        matter_id = row[0]
        seed_workspace_items(connection, matter_id)
        connection.execute(
            """
            insert into public.audit_events (matter_id, actor_type, actor_id, event_type, payload)
            values (
              %(matter_id)s,
              'script',
              'setup_supabase.py',
              'matter.seeded',
              '{"matter_number": "LX-MIG-2026-001"}'::jsonb
            )
            """,
            {"matter_id": matter_id},
        )
        return str(matter_id)


def seed_workspace_items(connection, matter_id: str) -> None:
    connection.execute(
        """
        update public.matters
        set status = 'evidence',
            metadata = metadata || %(metadata)s::jsonb
        where id = %(matter_id)s
        """,
        {
            "matter_id": matter_id,
            "metadata": json.dumps(
                {
                    "fixture": True,
                    "contains_real_personal_data": False,
                    "public_demo_safe": True,
                    "readiness_score": 42,
                    "route_id": "work_student_found_work",
                    "route_label": "Work Permit (Higher Ed)",
                    "state_label": "In-Progress / Evidence Gathering",
                    "known_facts": ["KTH Master's degree", "Current Residence Permit"],
                    "missing_facts": ["Job offer start date", "Monthly gross salary"],
                    "applicant_next_step": "Secure employment contract",
                }
            ),
        },
    )
    connection.execute(
        """
        delete from public.matter_documents
        where matter_id = %(matter_id)s
        """,
        {"matter_id": matter_id},
    )
    connection.execute(
        """
        delete from public.evidence_items
        where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
        """,
        {"matter_id": matter_id},
    )
    for item in default_evidence_rows():
        connection.execute(
            """
            insert into public.evidence_items (
              matter_id, label, description, status, priority, metadata
            )
            values (
              %(matter_id)s, %(label)s, %(description)s, %(status)s, %(priority)s, %(metadata)s::jsonb
            )
            """,
            {
                "matter_id": matter_id,
                "label": item["label"],
                "description": item["description"],
                "status": item["status"],
                "priority": item["priority"],
                "metadata": json.dumps(item["metadata"]),
            },
        )

    connection.execute(
        """
        delete from public.review_decisions
        where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
        """,
        {"matter_id": matter_id},
    )
    connection.execute(
        """
        delete from public.packet_versions
        where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
        """,
        {"matter_id": matter_id},
    )
    connection.execute(
        """
        delete from public.legal_source_refs
        where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
        """,
        {"matter_id": matter_id},
    )
    connection.execute(
        """
        delete from public.agent_runs
        where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
        """,
        {"matter_id": matter_id},
    )
    for run in default_agent_runs():
        connection.execute(
            """
            insert into public.agent_runs (
              matter_id, band_room_id, agent_role, status, model_provider, model_name,
              input, output, citations, completed_at, metadata
            )
            select
              %(matter_id)s, band_room_id, %(agent_role)s, %(status)s, %(model_provider)s,
              'seeded-demo', '{"trigger": "setup_supabase"}'::jsonb,
              %(output)s::jsonb, '[]'::jsonb,
              case when %(status)s in ('completed', 'failed', 'needs_review') then now() else null end,
              '{"fixture": true, "fixture_seed": true, "public_demo_safe": true}'::jsonb
            from public.matters
            where id = %(matter_id)s
            """,
            {
                "matter_id": matter_id,
                "agent_role": run["agent_role"],
                "status": run["status"],
                "model_provider": run["model_provider"],
                "output": json.dumps(run["output"]),
            },
        )


def _storage_object_name(item) -> str | None:
    if isinstance(item, dict):
        return item.get("name")
    return getattr(item, "name", None)


def main() -> int:
    applied = apply_migrations()
    bucket_status = ensure_storage_bucket()
    cleaned_objects = cleanup_demo_storage()
    matter_id = seed_demo_matter()

    print(f"migrations: ok ({', '.join(applied)})")
    print(f"storage_bucket: ok ({bucket_status})")
    print(f"demo_storage_cleanup: ok ({cleaned_objects} object(s))")
    print(f"demo_matter: ok ({DEMO_MATTER_NUMBER}, id={matter_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
