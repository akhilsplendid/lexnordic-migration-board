from __future__ import annotations

from collections import OrderedDict
from typing import Any


DEMO_MATTER_NUMBER = "LX-MIG-2026-001"

STATUS_LABELS = {
    "reviewed": "Verified",
    "received": "Uploaded",
    "requested": "Requested",
    "needed": "Missing",
    "missing": "Missing",
    "waived": "Waived",
}

AGENT_NAMES = {
    "intake": "Intake Agent",
    "conflict_kyc": "Conflict KYC",
    "decision_parser": "Decision Parser",
    "evidence": "Evidence Checker",
    "legal_source": "Legal Source Agent",
    "risk": "Risk Assessor",
    "appeal_packet": "Review Packet Agent",
    "partner_review": "Partner Review",
}


def workspace_from_rows(
    *,
    matter: dict[str, Any],
    evidence_items: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    agent_runs: list[dict[str, Any]],
    legal_sources: list[dict[str, Any]],
    packet: dict[str, Any] | None,
) -> dict[str, Any]:
    metadata = matter.get("metadata") or {}
    readiness_score = int(metadata.get("readiness_score", _readiness_from_evidence(evidence_items)))
    blockers = _blockers(evidence_items)
    latest_agents = _latest_agent_runs(agent_runs)
    extraction = _extraction_feed(documents=documents, agent_runs=agent_runs)

    return {
        "matter": {
            "id": str(matter["id"]),
            "matter_number": matter["matter_number"],
            "title": matter["title"],
            "status": matter["status"],
            "route": metadata.get("route_label", "Work Permit (Higher Ed)"),
            "route_id": metadata.get("route_id", "work_student_found_work"),
            "state_label": metadata.get("state_label", "In-Progress / Evidence Gathering"),
            "applicant_alias": matter.get("applicant_alias") or "Applicant A",
            "employer_name": matter.get("employer_name") or "Nordic Systems AB",
            "summary": matter.get("summary"),
            "band_room_id": str(matter["band_room_id"]) if matter.get("band_room_id") else None,
            "qdrant_collection": matter.get("qdrant_collection"),
        },
        "readiness": {
            "score": readiness_score,
            "blocker_count": len(blockers),
            "applicant_next_step": metadata.get(
                "applicant_next_step",
                _next_step_from_evidence(evidence_items),
            ),
            "packet_gate": {
                "threshold": 80,
                "state": "unlocked" if readiness_score >= 80 else "locked",
                "label": (
                    "AI packet is ready to finalize"
                    if readiness_score >= 80
                    else f"Packet target is 80% readiness. Currently at {readiness_score}%."
                ),
            },
        },
        "known_facts": metadata.get(
            "known_facts",
            ["KTH Master's degree", "Current Residence Permit"],
        ),
        "missing_facts": metadata.get(
            "missing_facts",
            ["Job offer start date", "Monthly gross salary"],
        ),
        "evidence_items": [_serialize_evidence(item) for item in evidence_items],
        "documents": [_serialize_document(document) for document in documents],
        "source_bundle": [_serialize_source(source) for source in legal_sources] or _fallback_sources(),
        "extraction_feed": extraction,
        "agent_activity": [_serialize_agent(role, run) for role, run in latest_agents.items()],
        "review_packet": _serialize_packet(packet),
    }


def demo_workspace_fixture(error: str | None = None) -> dict[str, Any]:
    matter = {
        "id": "fixture",
        "matter_number": DEMO_MATTER_NUMBER,
        "title": "Fictional work-permit refusal appeal readiness",
        "status": "evidence",
        "applicant_alias": "Applicant A",
        "employer_name": "Nordic Systems AB",
        "band_room_id": None,
        "qdrant_collection": "lexnordic_legal_sources",
        "summary": "Local fallback fixture. Backend storage is not reachable.",
        "metadata": {
            "readiness_score": 42,
            "route_label": "Work Permit (Higher Ed)",
            "state_label": "In-Progress / Evidence Gathering",
            "applicant_next_step": "Secure employment contract",
            "known_facts": ["KTH Master's degree", "Current Residence Permit"],
            "missing_facts": ["Job offer start date", "Monthly gross salary"],
        },
    }
    workspace = workspace_from_rows(
        matter=matter,
        evidence_items=default_evidence_rows(),
        documents=[],
        agent_runs=default_agent_runs(),
        legal_sources=[],
        packet=None,
    )
    if error:
        workspace["backend_warning"] = error
    return workspace


def default_evidence_rows() -> list[dict[str, Any]]:
    return [
        _fixture_evidence("Passport copies", "reviewed", "IDENTITY", "Ch. 2, 1 A", "Low", "intake", "identity"),
        _fixture_evidence(
            "Current permit card",
            "received",
            "RESIDENCE",
            "Ch. 5, 5",
            "Low",
            "evidence",
            "current_permit",
            status_label="Analyzing",
        ),
        _fixture_evidence(
            "Degree certificate",
            "received",
            "STUDIES",
            "Ch. 6b, 1",
            "Low",
            "evidence",
            "degree_certificate",
        ),
        _fixture_evidence(
            "Job offer",
            "missing",
            "EMPLOYMENT",
            "Ch. 6, 2",
            "High",
            "legal_source",
            "employment_contract",
        ),
        _fixture_evidence(
            "Salary specification",
            "needed",
            "SALARY / INSURANCE",
            "Ch. 6, 3 MA",
            "Low threshold",
            "risk",
            "salary_evidence",
            status_label="Risk found",
        ),
    ]


def default_agent_runs() -> list[dict[str, Any]]:
    return [
        _fixture_agent("intake", "completed", "manual", "Known facts captured."),
        _fixture_agent("evidence", "running", "featherless", "Extracting passport expiry."),
        _fixture_agent("legal_source", "queued", "aiml", "Ready to retrieve source bundle."),
        _fixture_agent("risk", "completed", "featherless", "Salary threshold risk identified."),
    ]


def document_type_for_evidence_label(label: str) -> str:
    lowered = label.lower()
    if "passport" in lowered or "identity" in lowered:
        return "identity"
    if "salary" in lowered or "insurance" in lowered:
        return "salary_evidence"
    if "offer" in lowered or "contract" in lowered:
        return "employment_contract"
    return "other"


def _serialize_evidence(item: dict[str, Any]) -> dict[str, Any]:
    metadata = item.get("metadata") or {}
    status = item.get("status") or "needed"
    label = metadata.get("status_label") or STATUS_LABELS.get(status, status.title())
    risk = metadata.get("risk_level", "Medium")
    agent_role = metadata.get("agent_role", "evidence")
    return {
        "id": str(item.get("id")),
        "group": metadata.get("group", "EVIDENCE"),
        "requirement": item["label"],
        "description": item.get("description"),
        "document_type": metadata.get("document_type") or document_type_for_evidence_label(item["label"]),
        "status": status,
        "status_label": label,
        "status_class": _status_class(status, label),
        "basis": metadata.get("basis", "Source review"),
        "risk_level": risk,
        "risk_class": _risk_class(risk),
        "agent_role": agent_role,
        "agent_name": AGENT_NAMES.get(agent_role, agent_role.replace("_", " ").title()),
        "action_label": metadata.get("action_label") or _action_label(status),
        "priority": item.get("priority", 3),
    }


def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(document["id"]),
        "document_type": document["document_type"],
        "filename": document["filename"],
        "content_type": document.get("content_type"),
        "size_bytes": document.get("size_bytes"),
        "extracted_text_status": document.get("extracted_text_status"),
        "metadata": document.get("metadata") or {},
        "created_at": _iso(document.get("created_at")),
    }


def _serialize_source(source: dict[str, Any]) -> dict[str, Any]:
    metadata = source.get("metadata") or {}
    return {
        "id": str(source.get("id")),
        "title": source["title"],
        "citation": source.get("citation"),
        "url": source.get("url"),
        "source_type": source.get("source_type"),
        "score": metadata.get("score"),
        "snippet": metadata.get("snippet"),
    }


def _serialize_agent(role: str, run: dict[str, Any] | None) -> dict[str, Any]:
    if not run:
        return {
            "agent_role": role,
            "name": AGENT_NAMES.get(role, role.replace("_", " ").title()),
            "status": "queued",
            "status_label": "Idle",
            "model_provider": None,
            "model_name": None,
            "confidence": None,
            "summary": "Waiting for matter state.",
            "next_action": "Await trigger",
            "updated_at": None,
        }

    output = run.get("output") or {}
    metadata = run.get("metadata") or {}
    return {
        "agent_role": role,
        "name": AGENT_NAMES.get(role, role.replace("_", " ").title()),
        "status": run.get("status", "queued"),
        "status_label": _agent_status_label(run.get("status", "queued")),
        "model_provider": run.get("model_provider"),
        "model_name": run.get("model_name"),
        "confidence": output.get("confidence") or metadata.get("confidence"),
        "summary": output.get("summary") or metadata.get("summary") or "No output yet.",
        "next_action": output.get("next_action") or metadata.get("next_action") or "Continue review",
        "updated_at": _iso(run.get("completed_at") or run.get("updated_at") or run.get("created_at")),
    }


def _serialize_packet(packet: dict[str, Any] | None) -> dict[str, Any]:
    if not packet:
        return {
            "version_no": 0,
            "status": "not_started",
            "summary": "AI case packet will be generated after agent alignment.",
            "document_checklist": [],
            "applicant_message": "",
            "next_actions": ["Upload employment contract", "Resolve salary threshold evidence"],
        }
    body = packet.get("packet") or {}
    return {
        "version_no": packet.get("version_no"),
        "status": packet.get("status"),
        "summary": body.get("summary", "AI case packet is ready to finalize."),
        "document_checklist": body.get("document_checklist", []),
        "applicant_message": body.get("applicant_message", ""),
        "next_actions": body.get("next_actions", []),
    }


def _latest_agent_runs(agent_runs: list[dict[str, Any]]) -> OrderedDict[str, dict[str, Any] | None]:
    roles = OrderedDict(
        (role, None)
        for role in ("intake", "evidence", "legal_source", "risk", "appeal_packet", "partner_review")
    )
    for run in sorted(agent_runs, key=lambda item: str(item.get("created_at") or ""), reverse=True):
        role = run.get("agent_role")
        if role in roles and roles[role] is None:
            roles[role] = run
    return roles


def _extraction_feed(*, documents: list[dict[str, Any]], agent_runs: list[dict[str, Any]]) -> dict[str, Any]:
    latest_doc = documents[0] if documents else None
    latest_evidence_run = next((run for run in agent_runs if run.get("agent_role") == "evidence"), None)
    if latest_doc:
        metadata = latest_doc.get("metadata") or {}
        return {
            "status": latest_doc.get("extracted_text_status", "complete"),
            "progress": int(metadata.get("progress", 100)),
            "message": metadata.get("message", f"Validated {latest_doc['filename']}"),
            "document_id": str(latest_doc["id"]),
            "fields": metadata.get("fields", []),
        }
    if latest_evidence_run:
        output = latest_evidence_run.get("output") or {}
        return {
            "status": latest_evidence_run.get("status", "running"),
            "progress": int(output.get("progress", 65)),
            "message": output.get("summary", "Extracting passport expiry..."),
            "document_id": None,
            "fields": output.get("fields", ["Degree OCR validated: KTH Royal Institute"]),
        }
    return {
        "status": "idle",
        "progress": 0,
        "message": "Waiting for evidence upload.",
        "document_id": None,
        "fields": [],
    }


def _blockers(evidence_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item
        for item in evidence_items
        if item.get("status") in {"needed", "missing", "requested"}
        and int(item.get("priority") or 3) <= 2
    ]


def _readiness_from_evidence(evidence_items: list[dict[str, Any]]) -> int:
    if not evidence_items:
        return 42
    complete = sum(1 for item in evidence_items if item.get("status") in {"received", "reviewed", "waived"})
    blockers = len(_blockers(evidence_items))
    return max(25, min(95, round((complete / len(evidence_items)) * 100) - blockers * 8))


def _next_step_from_evidence(evidence_items: list[dict[str, Any]]) -> str:
    for item in evidence_items:
        if item.get("status") in {"needed", "missing", "requested"}:
            return f"Provide {item['label'].lower()}"
    return "Confirm AI case packet"


def _status_class(status: str, label: str) -> str:
    if status == "reviewed":
        return "verified"
    if status == "received":
        return "active" if label.lower() == "analyzing" else "uploaded"
    if status in {"needed", "missing"}:
        return "missing" if label.lower() == "missing" else "warning"
    if status == "requested":
        return "warning"
    return "uploaded"


def _risk_class(risk: str) -> str:
    lowered = risk.lower()
    if "high" in lowered or "block" in lowered:
        return "high"
    if "threshold" in lowered or "medium" in lowered or "risk" in lowered:
        return "warning"
    return "low"


def _action_label(status: str) -> str:
    if status == "reviewed":
        return "View file"
    if status == "received":
        return "Verify"
    if status == "requested":
        return "Track"
    return "Request"


def _agent_status_label(status: str) -> str:
    return {
        "queued": "Idle",
        "running": "Active",
        "completed": "Done",
        "blocked": "Blocked",
        "failed": "Failed",
        "needs_review": "Review",
    }.get(status, status.title())


def _fixture_evidence(
    label: str,
    status: str,
    group: str,
    basis: str,
    risk: str,
    agent_role: str,
    document_type: str,
    *,
    status_label: str | None = None,
) -> dict[str, Any]:
    return {
        "id": label.lower().replace(" ", "_"),
        "label": label,
        "description": "",
        "status": status,
        "priority": 1 if status in {"missing", "needed"} else 3,
        "metadata": {
            "fixture": True,
            "group": group,
            "basis": basis,
            "risk_level": risk,
            "agent_role": agent_role,
            "document_type": document_type,
            **({"status_label": status_label} if status_label else {}),
        },
    }


def _fixture_agent(role: str, status: str, provider: str, summary: str) -> dict[str, Any]:
    return {
        "agent_role": role,
        "status": status,
        "model_provider": provider,
        "model_name": None,
        "output": {
            "summary": summary,
            "confidence": 0.88,
            "next_action": "Continue matter preparation",
        },
        "metadata": {"fixture": True},
        "created_at": "",
        "updated_at": "",
    }


def _fallback_sources() -> list[dict[str, Any]]:
    return [
        {
            "id": "migration-act-2005",
            "title": "Migration Act (2005:716)",
            "citation": "Work and residence permit basis",
            "url": (
                "https://www.riksdagen.se/sv/dokument-och-lagar/dokument/"
                "svensk-forfattningssamling/utlanningslag-2005716_sfs-2005-716/"
            ),
            "source_type": "statute",
            "score": None,
            "snippet": None,
        },
        {
            "id": "salary-2026",
            "title": "June 2026 salary threshold",
            "citation": "90 percent salary-threshold overlay",
            "url": None,
            "source_type": "official_rule",
            "score": None,
            "snippet": None,
        },
    ]


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else value
