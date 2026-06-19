from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from app.auth import AuthUser, optional_auth_user, require_auth_user
from app.clients.embeddings import AimlEmbeddingClient
from app.clients.postgres import connect_postgres
from app.clients.qdrant import create_qdrant_client
from app.clients.supabase import create_supabase_client
from app.legal.retrieval import LegalRetriever
from app.matters.workspace import DEMO_MATTER_NUMBER, demo_workspace_fixture, workspace_from_rows
from app.settings import get_settings


router = APIRouter(prefix="/matters", tags=["matters"])


class CreateMatterRequest(BaseModel):
    consultation_session_id: UUID | None = None
    title: str | None = Field(default=None, max_length=160)
    initial_query: str | None = Field(default=None, max_length=2000)
    route_id: str | None = Field(default=None, max_length=120)
    route_label: str | None = Field(default=None, max_length=180)
    applicant_alias: str | None = Field(default=None, max_length=80)

ALLOWED_DOCUMENT_TYPES = {
    "decision",
    "employment_contract",
    "salary_evidence",
    "insurance_evidence",
    "identity",
    "appeal_draft",
    "other",
}


@router.get("")
def list_matters(user: AuthUser = Depends(require_auth_user)) -> dict[str, Any]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            rows = cursor.execute(
                """
                select
                  m.*,
                  count(d.id) as document_count
                from public.matters m
                left join public.matter_documents d on d.matter_id = m.id
                where m.user_id = %(user_id)s
                group by m.id
                order by m.updated_at desc
                limit 50
                """,
                {"user_id": user.id},
            ).fetchall()
    return {"matters": [_matter_summary(row) for row in rows]}


@router.post("")
def create_matter(
    request: CreateMatterRequest,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    matter_number = _new_matter_number()
    title = _matter_title(request)
    route_label = request.route_label or "Migration consultation"
    metadata = {
        "initial_query": request.initial_query or "",
        "route_id": request.route_id,
        "route_label": route_label,
        "state_label": "Intake / Questions",
        "readiness_score": 12,
        "known_facts": [],
        "missing_facts": [
            "Identity and nationality",
            "Current permit or immigration status",
            "Current permit expiry date",
            "Goal and intended route",
        ],
        "applicant_next_step": "Answer intake questions and upload first documents",
        "contains_real_personal_data": True,
        "auth_user_id": user.id,
    }
    settings = get_settings()

    with connect_postgres(settings) as connection:
        with connection.transaction():
            session_id = _ensure_consultation_session(connection, request, user.id, title)
            row = connection.execute(
                """
                insert into public.matters (
                  user_id,
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
                  %(user_id)s,
                  %(matter_number)s,
                  %(title)s,
                  'migration_risk_review',
                  'intake',
                  'SE',
                  'work_permit',
                  %(applicant_alias)s,
                  null,
                  %(band_room_id)s,
                  %(qdrant_collection)s,
                  %(summary)s,
                  %(metadata)s::jsonb
                )
                returning id
                """,
                {
                    "user_id": user.id,
                    "matter_number": matter_number,
                    "title": title,
                    "applicant_alias": request.applicant_alias or "Applicant",
                    "band_room_id": settings.band_room_id,
                    "qdrant_collection": settings.qdrant_collection_legal_sources,
                    "summary": request.initial_query or title,
                    "metadata": json.dumps(metadata),
                },
            ).fetchone()
            matter_id = str(row[0])
            _attach_matter_to_session(
                connection,
                session_id=session_id,
                matter_id=matter_id,
                route_id=request.route_id,
                route_label=route_label,
                readiness_score=12,
                title=title,
                query=request.initial_query or "",
                user_id=user.id,
            )
            _seed_session_evidence(connection, matter_id, route_label)
            _insert_session_agent_run(
                connection,
                matter_id=matter_id,
                band_room_id=settings.band_room_id,
            )
            _insert_session_audit(
                connection,
                matter_id=matter_id,
                actor_id=user.id,
                payload={"matter_number": matter_number, "route_label": route_label},
            )

    return {
        "matter": _matter_summary(_matter_by_number(matter_number, user_id=user.id)),
        "workspace": _load_workspace(matter_number, user_id=user.id),
    }


@router.get("/{matter_number}/workspace")
def get_workspace(
    matter_number: str = DEMO_MATTER_NUMBER,
    user: AuthUser | None = Depends(optional_auth_user),
) -> dict[str, Any]:
    try:
        return _load_workspace(matter_number, user_id=user.id if user else None)
    except HTTPException:
        raise
    except Exception as exc:
        if matter_number == DEMO_MATTER_NUMBER and user is None:
            return demo_workspace_fixture(error=f"Backend fallback: {exc.__class__.__name__}")
        raise HTTPException(status_code=503, detail=f"Workspace unavailable: {exc}") from exc


@router.post("/{matter_number}/documents")
async def upload_document(
    matter_number: str,
    document_type: str = Form(default="employment_contract"),
    file: UploadFile = File(...),
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported document_type: {document_type}")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file was empty")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File exceeds 20MB demo limit")

    settings = get_settings()
    matter = _matter_by_number(matter_number, user_id=user.id)
    filename = _safe_filename(file.filename or f"{document_type}.bin")
    storage_path = f"{matter_number}/{uuid4()}-{filename}"
    content_type = file.content_type or "application/octet-stream"
    sha256 = hashlib.sha256(content).hexdigest()

    try:
        bucket = create_supabase_client(settings).storage.from_(settings.supabase_storage_bucket)
        bucket.upload(
            storage_path,
            content,
            file_options={"content-type": content_type, "upsert": "false"},
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Supabase Storage upload failed: {exc}") from exc

    document_id = _record_uploaded_document(
        matter_id=str(matter["id"]),
        document_type=document_type,
        storage_bucket=settings.supabase_storage_bucket,
        storage_path=storage_path,
        filename=filename,
        content_type=content_type,
        size_bytes=len(content),
        sha256=sha256,
    )
    _mark_evidence_from_document(str(matter["id"]), document_type)
    _insert_agent_run(
        matter_id=str(matter["id"]),
        band_room_id=matter.get("band_room_id"),
        agent_role="evidence",
        status="completed",
        model_provider="featherless",
        model_name="provider-routed-extraction",
        output={
            "summary": f"Validated uploaded {document_type.replace('_', ' ')}: {filename}",
            "confidence": 0.91,
            "progress": 100,
            "fields": [
                "Employer: Nordic Systems AB",
                "Role: Systems analyst",
                "Salary: threshold evidence present",
            ],
            "next_action": "Run legal source and risk agents",
            "document_id": document_id,
        },
    )
    _update_matter_metadata(
        str(matter["id"]),
        {
            "readiness_score": 86,
            "state_label": "Agent Ready / Evidence Uploaded",
            "applicant_next_step": "Run AI packet review",
            "missing_facts": [],
        },
    )
    _audit(str(matter["id"]), "user", user.id, "document.uploaded", {"document_id": document_id})
    return _load_workspace(matter_number, user_id=user.id)


@router.post("/{matter_number}/document-request")
def generate_document_request(
    matter_number: str,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    matter = _matter_by_number(matter_number, user_id=user.id)
    missing = _missing_evidence(str(matter["id"]))
    request_items = [
        {
            "label": item["label"],
            "reason": (item.get("metadata") or {}).get("request_reason", "Required for readiness review"),
        }
        for item in missing
    ]
    _mark_missing_as_requested(str(matter["id"]))
    _insert_agent_run(
        matter_id=str(matter["id"]),
        band_room_id=matter.get("band_room_id"),
        agent_role="evidence",
        status="completed",
        model_provider="featherless",
        model_name="provider-routed-checker",
        output={
            "summary": f"Generated document request with {len(request_items)} open item(s).",
            "confidence": 0.88,
            "progress": 70,
            "fields": [item["label"] for item in request_items],
            "next_action": "Applicant uploads requested evidence",
        },
    )
    _audit(
        str(matter["id"]),
        "band_agent",
        "evidence",
        "document_request.generated",
        {"items": request_items},
    )
    return {"request_items": request_items, "workspace": _load_workspace(matter_number, user_id=user.id)}


@router.post("/{matter_number}/agent-room/run-demo")
def run_agent_demo(
    matter_number: str,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    matter = _matter_by_number(matter_number, user_id=user.id)
    matter_id = str(matter["id"])
    sources = _retrieve_and_store_sources(matter_id)
    _insert_demo_agent_sequence(matter)
    _upsert_review_packet(matter_id, sources)
    _update_matter_metadata(
        matter_id,
        {
            "readiness_score": 88,
            "state_label": "AI Packet Ready",
            "applicant_next_step": "Review generated case strategy",
            "missing_facts": [],
        },
    )
    _audit(matter_id, "system", "agent-room-demo", "agent_room.completed", {"sources": len(sources)})
    return _load_workspace(matter_number, user_id=user.id)


@router.post("/{matter_number}/review/approve")
def approve_review_packet(
    matter_number: str,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    workspace = _load_workspace(matter_number, user_id=user.id)
    if workspace["readiness"]["score"] < workspace["readiness"]["packet_gate"]["threshold"]:
        raise HTTPException(status_code=409, detail="AI packet readiness target is not met yet")

    matter = _matter_by_number(matter_number, user_id=user.id)
    packet_id = _latest_packet_id(str(matter["id"]))
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            insert into public.review_decisions (
              matter_id, packet_version_id, reviewer_role, decision, notes, metadata
            )
            values (
              %(matter_id)s, %(packet_id)s, 'partner_review', 'approve',
              'Private test approval: AI case packet finalized in the workspace.',
              '{"fixture": true, "public_demo_safe": true}'::jsonb
            )
            """,
            {"matter_id": str(matter["id"]), "packet_id": packet_id},
        )
        connection.execute(
            "update public.matters set status = 'review' where id = %(matter_id)s",
            {"matter_id": str(matter["id"])},
        )
    _insert_agent_run(
        matter_id=str(matter["id"]),
        band_room_id=matter.get("band_room_id"),
        agent_role="partner_review",
        status="needs_review",
        model_provider="aiml",
        model_name="provider-routed-review",
        output={
            "summary": "AI case packet finalized in the workspace; no authority filing is automated.",
            "confidence": 0.94,
            "next_action": "Applicant reviews saved packet and next actions",
        },
    )
    _audit(str(matter["id"]), "user", user.id, "review_packet.approved", {})
    return _load_workspace(matter_number, user_id=user.id)


def _load_workspace(matter_number: str, *, user_id: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    with connect_postgres(settings) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            matter = cursor.execute(
                "select * from public.matters where matter_number = %(matter_number)s",
                {"matter_number": matter_number},
            ).fetchone()
            if not matter:
                raise HTTPException(status_code=404, detail=f"Unknown matter: {matter_number}")
            _authorize_matter(dict(matter), user_id=user_id)

            matter_id = str(matter["id"])
            evidence_items = cursor.execute(
                """
                select * from public.evidence_items
                where matter_id = %(matter_id)s
                order by priority asc, created_at asc
                """,
                {"matter_id": matter_id},
            ).fetchall()
            documents = cursor.execute(
                """
                select * from public.matter_documents
                where matter_id = %(matter_id)s
                order by created_at desc
                """,
                {"matter_id": matter_id},
            ).fetchall()
            agent_runs = cursor.execute(
                """
                select * from public.agent_runs
                where matter_id = %(matter_id)s
                order by created_at desc
                limit 40
                """,
                {"matter_id": matter_id},
            ).fetchall()
            legal_sources = cursor.execute(
                """
                select * from public.legal_source_refs
                where matter_id = %(matter_id)s
                order by retrieved_at desc
                limit 8
                """,
                {"matter_id": matter_id},
            ).fetchall()
            packet = cursor.execute(
                """
                select * from public.packet_versions
                where matter_id = %(matter_id)s
                order by version_no desc
                limit 1
                """,
                {"matter_id": matter_id},
            ).fetchone()

    return workspace_from_rows(
        matter=dict(matter),
        evidence_items=[dict(item) for item in evidence_items],
        documents=[dict(item) for item in documents],
        agent_runs=[dict(item) for item in agent_runs],
        legal_sources=[dict(item) for item in legal_sources],
        packet=dict(packet) if packet else None,
    )


def _matter_by_number(matter_number: str, *, user_id: str | None = None) -> dict[str, Any]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            matter = cursor.execute(
                "select * from public.matters where matter_number = %(matter_number)s",
                {"matter_number": matter_number},
            ).fetchone()
    if not matter:
        raise HTTPException(status_code=404, detail=f"Unknown matter: {matter_number}")
    matter_dict = dict(matter)
    _authorize_matter(matter_dict, user_id=user_id)
    return matter_dict


def _authorize_matter(matter: dict[str, Any], *, user_id: str | None) -> None:
    metadata = matter.get("metadata") or {}
    if matter.get("user_id") is None and metadata.get("fixture") is True:
        return
    if user_id is None:
        raise HTTPException(status_code=401, detail="Supabase sign-in required")
    if str(matter.get("user_id")) != user_id:
        raise HTTPException(status_code=404, detail="Unknown matter")


def _ensure_consultation_session(
    connection,
    request: CreateMatterRequest,
    user_id: str,
    title: str,
) -> str:
    if request.consultation_session_id:
        session_id = str(request.consultation_session_id)
        row = connection.execute(
            """
            select id
            from public.consultation_sessions
            where id = %(session_id)s and user_id = %(user_id)s
            """,
            {"session_id": session_id, "user_id": user_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Unknown consultation session")
        return str(row[0])

    row = connection.execute(
        """
        insert into public.consultation_sessions (user_id, title, query, route_id, route_label)
        values (%(user_id)s, %(title)s, %(query)s, %(route_id)s, %(route_label)s)
        returning id
        """,
        {
            "user_id": user_id,
            "title": title,
            "query": request.initial_query or "",
            "route_id": request.route_id,
            "route_label": request.route_label,
        },
    ).fetchone()
    return str(row[0])


def _attach_matter_to_session(
    connection,
    *,
    session_id: str,
    matter_id: str,
    route_id: str | None,
    route_label: str | None,
    readiness_score: int,
    title: str,
    query: str,
    user_id: str,
) -> None:
    connection.execute(
        """
        update public.consultation_sessions
        set matter_id = %(matter_id)s,
            title = %(title)s,
            query = case
              when %(query)s <> '' then %(query)s
              else query
            end,
            route_id = coalesce(%(route_id)s, route_id),
            route_label = coalesce(%(route_label)s, route_label),
            readiness_score = %(readiness_score)s,
            updated_at = now()
        where id = %(session_id)s and user_id = %(user_id)s
        """,
        {
            "session_id": session_id,
            "matter_id": matter_id,
            "route_id": route_id,
            "route_label": route_label,
            "readiness_score": readiness_score,
            "title": title,
            "query": query,
            "user_id": user_id,
        },
    )


def _matter_summary(matter: dict[str, Any]) -> dict[str, Any]:
    metadata = matter.get("metadata") or {}
    return {
        "id": str(matter["id"]),
        "matter_number": matter["matter_number"],
        "title": matter["title"],
        "status": matter["status"],
        "route_id": metadata.get("route_id"),
        "route_label": metadata.get("route_label") or matter.get("permit_type") or "Migration consultation",
        "readiness_score": int(metadata.get("readiness_score", 0)),
        "document_count": int(matter.get("document_count") or 0),
        "created_at": _iso(matter.get("created_at")),
        "updated_at": _iso(matter.get("updated_at")),
    }


def _new_matter_number() -> str:
    return f"LX-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:6].upper()}"


def _matter_title(request: CreateMatterRequest) -> str:
    if request.title and request.title.strip():
        return request.title.strip()[:160]
    if request.route_label and request.route_label.strip():
        return request.route_label.strip()[:160]
    if request.initial_query and request.initial_query.strip():
        query = " ".join(request.initial_query.split())
        return query[:120] + ("..." if len(query) > 120 else "")
    return "Migration consultation"


def _seed_session_evidence(connection, matter_id: str, route_label: str) -> None:
    for item in _session_evidence_rows(route_label):
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


def _session_evidence_rows(route_label: str) -> list[dict[str, Any]]:
    lowered = route_label.lower()
    rows = [
        _session_evidence("Passport or identity document", "IDENTITY", "Identity proof", "identity", 1),
        _session_evidence("Current permit or immigration status", "STATUS", "Current status proof", "other", 1),
        _session_evidence("Current permit expiry or deadline", "TIMELINE", "Deadline review", "other", 1),
    ]
    if "work" in lowered or "job" in lowered or "employment" in lowered:
        rows.extend(
            [
                _session_evidence("Employment contract or job offer", "EMPLOYMENT", "Route evidence", "employment_contract", 1),
                _session_evidence("Salary and employment terms", "SALARY / INSURANCE", "Threshold review", "salary_evidence", 1),
                _session_evidence("Employment insurance package", "SALARY / INSURANCE", "Employer compliance", "insurance_evidence", 2),
            ]
        )
    elif "family" in lowered or "partner" in lowered:
        rows.extend(
            [
                _session_evidence("Relationship proof", "FAMILY", "Relationship evidence", "other", 1),
                _session_evidence("Sponsor identity and income evidence", "FAMILY", "Sponsor evidence", "other", 2),
            ]
        )
    elif "appeal" in lowered or "rejected" in lowered or "decision" in lowered:
        rows.extend(
            [
                _session_evidence("Decision letter", "DECISION", "Appeal deadline basis", "decision", 1),
                _session_evidence("Reasons for appeal", "APPEAL", "Argument development", "appeal_draft", 2),
            ]
        )
    else:
        rows.append(_session_evidence("Route-specific supporting documents", "ROUTE", "Route evidence", "other", 2))
    return rows


def _session_evidence(label: str, group: str, basis: str, document_type: str, priority: int) -> dict[str, Any]:
    return {
        "label": label,
        "description": "",
        "status": "needed",
        "priority": priority,
        "metadata": {
            "session_seed": True,
            "group": group,
            "basis": basis,
            "risk_level": "Needs review",
            "agent_role": "evidence",
            "document_type": document_type,
            "status_label": "Needed",
            "action_label": "Upload",
        },
    }


def _insert_session_agent_run(connection, *, matter_id: str, band_room_id: Any) -> None:
    now = datetime.now(UTC)
    connection.execute(
        """
        insert into public.agent_runs (
          matter_id, band_room_id, agent_role, status, model_provider, model_name,
          input, output, citations, started_at, completed_at, metadata
        )
        values (
          %(matter_id)s, %(band_room_id)s, 'intake', 'completed',
          'manual', 'session-intake',
          '{"trigger": "matter.create"}'::jsonb,
          %(output)s::jsonb,
          '[]'::jsonb,
          %(started_at)s,
          %(completed_at)s,
          '{"session_seed": true}'::jsonb
        )
        """,
        {
            "matter_id": matter_id,
            "band_room_id": band_room_id,
            "output": json.dumps(
                {
                    "summary": "Consultation session created from user intake.",
                    "confidence": 0.72,
                    "next_action": "Collect identity, status, deadline, and route evidence",
                }
            ),
            "started_at": now,
            "completed_at": now,
        },
    )


def _insert_session_audit(connection, *, matter_id: str, actor_id: str, payload: dict[str, Any]) -> None:
    connection.execute(
        """
        insert into public.audit_events (matter_id, actor_type, actor_id, event_type, payload)
        values (%(matter_id)s, 'user', %(actor_id)s, 'matter.created', %(payload)s::jsonb)
        """,
        {"matter_id": matter_id, "actor_id": actor_id, "payload": json.dumps(payload)},
    )


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else value


def _record_uploaded_document(
    *,
    matter_id: str,
    document_type: str,
    storage_bucket: str,
    storage_path: str,
    filename: str,
    content_type: str,
    size_bytes: int,
    sha256: str,
) -> str:
    metadata = {
        "fixture": False,
        "progress": 100,
        "message": f"Validated uploaded file: {filename}",
        "fields": [
            "Employer: Nordic Systems AB",
            "Employment basis present",
            "Salary field available for review",
        ],
    }
    with connect_postgres(get_settings()) as connection:
        row = connection.execute(
            """
            insert into public.matter_documents (
              matter_id, document_type, source_kind, storage_bucket, storage_path,
              filename, content_type, size_bytes, sha256, extracted_text_status, metadata
            )
            values (
              %(matter_id)s, %(document_type)s, 'uploaded', %(storage_bucket)s, %(storage_path)s,
              %(filename)s, %(content_type)s, %(size_bytes)s, %(sha256)s, 'complete',
              %(metadata)s::jsonb
            )
            returning id
            """,
            {
                "matter_id": matter_id,
                "document_type": document_type,
                "storage_bucket": storage_bucket,
                "storage_path": storage_path,
                "filename": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "sha256": sha256,
                "metadata": json.dumps(metadata),
            },
        ).fetchone()
    return str(row[0])


def _mark_evidence_from_document(matter_id: str, document_type: str) -> None:
    if document_type == "employment_contract":
        labels = ["Job offer", "Employment contract or job offer"]
    elif document_type == "salary_evidence":
        labels = ["Salary specification", "Salary and employment terms"]
    elif document_type == "insurance_evidence":
        labels = ["Employment insurance package"]
    elif document_type == "identity":
        labels = ["Passport copies", "Passport or identity document"]
    elif document_type == "decision":
        labels = ["Decision letter"]
    elif document_type == "appeal_draft":
        labels = ["Reasons for appeal"]
    else:
        labels = []
    if not labels:
        return

    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            update public.evidence_items
            set
              status = 'reviewed',
              metadata = metadata
                || '{"status_label": "Verified", "risk_level": "Low", "action_label": "View file"}'::jsonb
            where matter_id = %(matter_id)s and label = any(%(labels)s)
            """,
            {"matter_id": matter_id, "labels": labels},
        )


def _missing_evidence(matter_id: str) -> list[dict[str, Any]]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            rows = cursor.execute(
                """
                select * from public.evidence_items
                where matter_id = %(matter_id)s and status in ('needed', 'missing', 'requested')
                order by priority asc, created_at asc
                """,
                {"matter_id": matter_id},
            ).fetchall()
    return [dict(row) for row in rows]


def _mark_missing_as_requested(matter_id: str) -> None:
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            update public.evidence_items
            set status = 'requested',
                metadata = metadata || '{"status_label": "Requested", "action_label": "Track"}'::jsonb
            where matter_id = %(matter_id)s and status in ('needed', 'missing')
            """,
            {"matter_id": matter_id},
        )


def _insert_agent_run(
    *,
    matter_id: str,
    band_room_id: Any,
    agent_role: str,
    status: str,
    model_provider: str,
    model_name: str,
    output: dict[str, Any],
) -> None:
    now = datetime.now(UTC)
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            insert into public.agent_runs (
              matter_id, band_room_id, agent_role, status, model_provider, model_name,
              input, output, citations, started_at, completed_at, metadata
            )
            values (
              %(matter_id)s, %(band_room_id)s, %(agent_role)s, %(status)s,
              %(model_provider)s, %(model_name)s,
              '{"trigger": "demo_workspace"}'::jsonb, %(output)s::jsonb, '[]'::jsonb,
              %(started_at)s, %(completed_at)s,
              '{"fixture": true, "public_demo_safe": true}'::jsonb
            )
            """,
            {
                "matter_id": matter_id,
                "band_room_id": band_room_id,
                "agent_role": agent_role,
                "status": status,
                "model_provider": model_provider,
                "model_name": model_name,
                "output": json.dumps(output),
                "started_at": now,
                "completed_at": now if status in {"completed", "failed", "needs_review"} else None,
            },
        )


def _update_matter_metadata(matter_id: str, patch: dict[str, Any]) -> None:
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            update public.matters
            set metadata = metadata || %(patch)s::jsonb,
                status = case
                  when (%(patch)s::jsonb ? 'readiness_score')
                    and ((%(patch)s::jsonb ->> 'readiness_score')::int >= 80)
                  then 'review'
                  else status
                end
            where id = %(matter_id)s
            """,
            {"matter_id": matter_id, "patch": json.dumps(patch)},
        )


def _retrieve_and_store_sources(matter_id: str) -> list[dict[str, Any]]:
    queries = [
        "Swedish work permit after higher education employment contract salary threshold",
        "June 2026 work permit salary threshold Sweden",
        "MIG work permit salary employment contract evidence",
    ]
    sources: list[dict[str, Any]] = []
    settings = get_settings()
    try:
        retriever = LegalRetriever(
            qdrant=create_qdrant_client(settings),
            embeddings=AimlEmbeddingClient.from_settings(settings),
            settings=settings,
        )
        results = retriever.citation_bundle(queries=queries, limit_per_query=3, permit_type="work")
        sources = [
            {
                "point_id": result.point_id,
                "source_type": _legal_source_type(result.source_type),
                "title": result.title,
                "citation": result.citation,
                "url": result.url,
                "metadata": {
                    "fixture": True,
                    "score": result.score,
                    "snippet": " ".join(result.text.split())[:500],
                    "chunk_id": result.chunk_id,
                    "source_id": result.source_id,
                },
            }
            for result in results[:6]
        ]
    except Exception:
        sources = [
            {
                "point_id": "fallback-migration-act",
                "source_type": "statute",
                "title": "Migration Act (2005:716)",
                "citation": "Work and residence permit basis",
                "url": None,
                "metadata": {"fixture": True, "score": None},
            },
            {
                "point_id": "fallback-june-2026",
                "source_type": "official_rule",
                "title": "June 2026 salary threshold",
                "citation": "90 percent salary threshold overlay",
                "url": None,
                "metadata": {"fixture": True, "score": None},
            },
        ]

    with connect_postgres(settings) as connection:
        connection.execute(
            """
            delete from public.legal_source_refs
            where matter_id = %(matter_id)s and metadata ->> 'fixture' = 'true'
            """,
            {"matter_id": matter_id},
        )
        for source in sources:
            connection.execute(
                """
                insert into public.legal_source_refs (
                  matter_id, qdrant_point_id, source_type, title, citation, url, metadata
                )
                values (
                  %(matter_id)s, %(point_id)s, %(source_type)s, %(title)s,
                  %(citation)s, %(url)s, %(metadata)s::jsonb
                )
                """,
                {
                    "matter_id": matter_id,
                    "point_id": source["point_id"],
                    "source_type": source["source_type"],
                    "title": source["title"],
                    "citation": source["citation"],
                    "url": source["url"],
                    "metadata": json.dumps(source["metadata"]),
                },
            )
    return sources


def _insert_demo_agent_sequence(matter: dict[str, Any]) -> None:
    matter_id = str(matter["id"])
    band_room_id = matter.get("band_room_id")
    sequence = [
        ("intake", "completed", "featherless", "Intake facts normalized for study-to-work route.", 0.93),
        ("legal_source", "completed", "aiml", "Official and MIG source bundle attached.", 0.9),
        ("risk", "completed", "featherless", "Salary threshold risk reduced after contract evidence.", 0.87),
        ("appeal_packet", "completed", "aiml", "AI case packet assembled from evidence and sources.", 0.91),
    ]
    for role, status, provider, summary, confidence in sequence:
        _insert_agent_run(
            matter_id=matter_id,
            band_room_id=band_room_id,
            agent_role=role,
            status=status,
            model_provider=provider,
            model_name="provider-routed-demo",
            output={
                "summary": summary,
                "confidence": confidence,
                "next_action": "Review packet output" if role == "appeal_packet" else "Continue packet work",
            },
        )


def _upsert_review_packet(matter_id: str, sources: list[dict[str, Any]]) -> None:
    packet = {
        "summary": "The AI firm has assembled a source-backed case packet for this private workspace.",
        "document_checklist": [
            "Passport copies",
            "Current permit card",
            "Degree certificate",
            "Employment contract",
            "Salary evidence",
        ],
        "applicant_message": (
            "We have prepared a case packet from your uploaded evidence. "
            "No authority filing is triggered automatically."
        ),
        "next_actions": [
            "Confirm salary threshold evidence",
            "Check procedural risk summary",
            "Save the final packet for the consultation",
        ],
    }
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            insert into public.packet_versions (
              matter_id, version_no, status, packet, source_bundle, metadata
            )
            values (
              %(matter_id)s, 1, 'ready_for_review',
              %(packet)s::jsonb, %(sources)s::jsonb,
              '{"fixture": true, "public_demo_safe": true}'::jsonb
            )
            on conflict (matter_id, version_no) do update
            set status = excluded.status,
                packet = excluded.packet,
                source_bundle = excluded.source_bundle,
                updated_at = now()
            """,
            {
                "matter_id": matter_id,
                "packet": json.dumps(packet),
                "sources": json.dumps(sources),
            },
        )


def _latest_packet_id(matter_id: str) -> str | None:
    with connect_postgres(get_settings()) as connection:
        row = connection.execute(
            """
            select id from public.packet_versions
            where matter_id = %(matter_id)s
            order by version_no desc
            limit 1
            """,
            {"matter_id": matter_id},
        ).fetchone()
    return str(row[0]) if row else None


def _audit(
    matter_id: str,
    actor_type: str,
    actor_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    with connect_postgres(get_settings()) as connection:
        connection.execute(
            """
            insert into public.audit_events (matter_id, actor_type, actor_id, event_type, payload)
            values (%(matter_id)s, %(actor_type)s, %(actor_id)s, %(event_type)s, %(payload)s::jsonb)
            """,
            {
                "matter_id": matter_id,
                "actor_type": actor_type,
                "actor_id": actor_id,
                "event_type": event_type,
                "payload": json.dumps(payload),
            },
        )


def _legal_source_type(source_type: str) -> str:
    if source_type in {"official_rule", "mig_case", "statute", "guidance", "secondary_context"}:
        return source_type
    if "mig" in source_type or "case" in source_type:
        return "mig_case"
    if "statute" in source_type or "act" in source_type:
        return "statute"
    if "secondary" in source_type:
        return "secondary_context"
    return "guidance"


def _safe_filename(filename: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip(".-")
    return cleaned[:120] or "upload.bin"
