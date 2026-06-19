from __future__ import annotations

import json
import time
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from app.auth import AuthUser, require_auth_user
from app.clients.chat_models import complete_chat
from app.clients.model_router import ModelProvider
from app.clients.postgres import connect_postgres
from app.permits.readiness import match_routes
from app.settings import get_settings


router = APIRouter(prefix="/sessions", tags=["sessions"])

AGENT_ROLES: tuple[dict[str, str], ...] = (
    {"role": "intake", "name": "LexNordic Intake", "provider": "featherless"},
    {"role": "conflict_kyc", "name": "Conflict KYC", "provider": "featherless"},
    {"role": "decision_parser", "name": "Decision Parser", "provider": "featherless"},
    {"role": "legal_source", "name": "Legal Source", "provider": "aiml"},
    {"role": "evidence", "name": "Evidence", "provider": "featherless"},
    {"role": "risk", "name": "Risk", "provider": "featherless"},
    {"role": "appeal_packet", "name": "Appeal Packet", "provider": "aiml"},
    {"role": "partner_review", "name": "Partner Review", "provider": "aiml"},
)

AGENT_MENTION_ALIASES: dict[str, str] = {
    "@intake": "intake",
    "@kyc": "conflict_kyc",
    "@conflict": "conflict_kyc",
    "@decision": "decision_parser",
    "@route": "decision_parser",
    "@legal": "legal_source",
    "@source": "legal_source",
    "@evidence": "evidence",
    "@documents": "evidence",
    "@risk": "risk",
    "@packet": "appeal_packet",
    "@appeal": "appeal_packet",
    "@partner": "partner_review",
    "@review": "partner_review",
}


class CreateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    query: str | None = Field(default=None, max_length=4000)


class UpdateSessionRequest(BaseModel):
    title: str | None = Field(default=None, max_length=160)
    query: str | None = Field(default=None, max_length=4000)
    route_id: str | None = Field(default=None, max_length=120)
    route_label: str | None = Field(default=None, max_length=180)
    readiness_score: int | None = Field(default=None, ge=0, le=100)


class ChatMessageInput(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    text: str = Field(min_length=1, max_length=4000)


class AppendMessagesRequest(BaseModel):
    messages: list[ChatMessageInput] = Field(min_length=1, max_length=8)


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    facts: dict[str, Any] = Field(default_factory=dict)
    documents: list[str] = Field(default_factory=list, max_length=24)


@router.get("")
def list_sessions(user: AuthUser = Depends(require_auth_user)) -> dict[str, Any]:
    sessions, messages = _load_user_sessions(user.id)
    messages_by_session: dict[str, list[dict[str, Any]]] = {}
    for message in messages:
        messages_by_session.setdefault(str(message["session_id"]), []).append(_message_summary(message))
    return {
        "sessions": [
            _session_summary(session, messages_by_session.get(str(session["id"]), []))
            for session in sessions
        ]
    }


@router.post("")
def create_session(
    request: CreateSessionRequest,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    title = _clean_title(request.title, request.query)
    query = (request.query or "").strip()
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            session = cursor.execute(
                """
                insert into public.consultation_sessions (user_id, title, query)
                values (%(user_id)s, %(title)s, %(query)s)
                returning *
                """,
                {"user_id": user.id, "title": title, "query": query},
            ).fetchone()
    return {"session": _session_summary(dict(session), [])}


@router.patch("/{session_id}")
def update_session(
    session_id: UUID,
    request: UpdateSessionRequest,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    fields = request.model_dump(exclude_unset=True)
    if not fields:
        return {"session": _get_session_summary(str(session_id), user.id)}

    assignments = [f"{field} = %({field})s" for field in fields]
    params: dict[str, Any] = {"session_id": str(session_id), "user_id": user.id, **fields}
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            session = cursor.execute(
                f"""
                update public.consultation_sessions
                set {", ".join(assignments)}
                where id = %(session_id)s and user_id = %(user_id)s
                returning *
                """,
                params,
            ).fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Unknown consultation session")
    return {"session": _session_summary(dict(session), _session_messages(str(session_id), user.id))}


@router.post("/{session_id}/messages")
def append_messages(
    session_id: UUID,
    request: AppendMessagesRequest,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    session_id_text = str(session_id)
    _assert_session_owner(session_id_text, user.id)
    with connect_postgres(get_settings()) as connection:
        with connection.transaction():
            for message in request.messages:
                connection.execute(
                    """
                    insert into public.chat_messages (session_id, user_id, role, content)
                    values (%(session_id)s, %(user_id)s, %(role)s, %(content)s)
                    """,
                    {
                        "session_id": session_id_text,
                        "user_id": user.id,
                        "role": message.role,
                        "content": message.text,
                    },
                )
            connection.execute(
                """
                update public.consultation_sessions
                set updated_at = now()
                where id = %(session_id)s and user_id = %(user_id)s
                """,
                {"session_id": session_id_text, "user_id": user.id},
            )
    return {"session": _get_session_summary(session_id_text, user.id)}


@router.post("/{session_id}/chat")
def run_agent_chat(
    session_id: UUID,
    request: AgentChatRequest,
    user: AuthUser = Depends(require_auth_user),
) -> dict[str, Any]:
    session_id_text = str(session_id)
    session = _assert_session_owner(session_id_text, user.id)
    prepared = _prepare_agent_chat(session=session, request=request)
    return _persist_agent_chat(
        session_id=session_id_text,
        user_id=user.id,
        session=session,
        prepared=prepared,
    )


@router.post("/{session_id}/chat/stream")
def stream_agent_chat(
    session_id: UUID,
    request: AgentChatRequest,
    user: AuthUser = Depends(require_auth_user),
) -> StreamingResponse:
    session_id_text = str(session_id)
    session = _assert_session_owner(session_id_text, user.id)

    def events():
        message = " ".join(request.message.split())
        focus_role = _infer_agent_focus(message)
        try:
            yield _sse(
                "started",
                {
                    "message": "LexNordic started checking the consultation.",
                    "agentTrace": _pending_agent_trace(message=message, focus_role=focus_role),
                },
            )

            results = match_routes(
                query=message,
                route_id=None,
                facts=request.facts,
                documents=request.documents,
                limit=4,
            )
            agent_trace = _build_agent_trace(
                message=message,
                results=results,
                facts=request.facts,
                documents=request.documents,
                focus_role=focus_role,
            )

            for index, step in enumerate(agent_trace):
                running_trace = _trace_with_progress(agent_trace, running_index=index)
                yield _sse(
                    "trace",
                    {
                        "phase": "checking",
                        "step": running_trace[index],
                        "agentTrace": running_trace,
                    },
                )
                time.sleep(0.08)
                completed_trace = _trace_with_progress(agent_trace, completed_through=index + 1)
                yield _sse(
                    "trace",
                    {
                        "phase": "checked",
                        "step": completed_trace[index],
                        "agentTrace": completed_trace,
                    },
                )

            yield _sse(
                "answering",
                {
                    "message": "LexNordic is writing the answer.",
                    "agentTrace": _trace_with_progress(agent_trace, completed_through=len(agent_trace)),
                },
            )

            answer = _build_chat_answer(
                message=message,
                session=session,
                results=results,
                agent_trace=agent_trace,
                focus_role=focus_role,
            )
            response = _persist_agent_chat(
                session_id=session_id_text,
                user_id=user.id,
                session=session,
                prepared={
                    "message": message,
                    "agent_focus": focus_role,
                    "results": results,
                    "primary": results[0] if results else None,
                    "agent_trace": agent_trace,
                    "answer": answer,
                },
            )
            yield _sse("complete", response)
        except Exception:
            yield _sse("error", {"message": "Unable to run agent consultation stream."})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _prepare_agent_chat(*, session: dict[str, Any], request: AgentChatRequest) -> dict[str, Any]:
    message = " ".join(request.message.split())
    agent_focus = _infer_agent_focus(message)
    results = match_routes(
        query=message,
        route_id=None,
        facts=request.facts,
        documents=request.documents,
        limit=4,
    )
    primary = results[0] if results else None
    agent_trace = _build_agent_trace(
        message=message,
        results=results,
        facts=request.facts,
        documents=request.documents,
        focus_role=agent_focus,
    )
    answer = _build_chat_answer(
        message=message,
        session=session,
        results=results,
        agent_trace=agent_trace,
        focus_role=agent_focus,
    )
    return {
        "message": message,
        "agent_focus": agent_focus,
        "results": results,
        "primary": primary,
        "agent_trace": agent_trace,
        "answer": answer,
    }


def _persist_agent_chat(
    *,
    session_id: str,
    user_id: str,
    session: dict[str, Any],
    prepared: dict[str, Any],
) -> dict[str, Any]:
    message = prepared["message"]
    agent_focus = prepared["agent_focus"]
    results = prepared["results"]
    primary = prepared["primary"]
    agent_trace = prepared["agent_trace"]
    answer = prepared["answer"]
    with connect_postgres(get_settings()) as connection:
        with connection.transaction():
            _insert_chat_message(
                connection=connection,
                session_id=session_id,
                user_id=user_id,
                role="user",
                content=message,
                metadata={
                    "mode": "agent_consultation",
                    "addressed_agent": agent_focus,
                },
            )
            _insert_chat_message(
                connection=connection,
                session_id=session_id,
                user_id=user_id,
                role="assistant",
                content=answer,
                metadata={
                    "mode": "agent_consultation",
                    "addressed_agent": agent_focus,
                    "agent_trace": agent_trace,
                    "route_results": results[:4],
                    "source_bundle": _source_bundle(results),
                },
            )
            connection.execute(
                """
                update public.consultation_sessions
                set
                  title = %(title)s,
                  query = %(query)s,
                  route_id = %(route_id)s,
                  route_label = %(route_label)s,
                  readiness_score = %(readiness_score)s,
                  metadata = coalesce(metadata, '{}'::jsonb) || %(metadata)s,
                  updated_at = now()
                where id = %(session_id)s and user_id = %(user_id)s
                """,
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "title": _next_title(session, primary, message),
                    "query": message,
                    "route_id": primary["route"]["route_id"] if primary else session.get("route_id"),
                    "route_label": primary["route"]["name"] if primary else session.get("route_label"),
                    "readiness_score": (
                        primary["readiness"]["score"] if primary else session.get("readiness_score")
                    ),
                    "metadata": Jsonb(
                        {
                            "last_agent_trace": agent_trace,
                            "last_agent_focus": agent_focus,
                            "last_chat_mode": "agent_consultation",
                        }
                    ),
                },
            )

    session_summary = _get_session_summary(session_id, user_id)
    assistant_message = next(
        (
            message
            for message in reversed(session_summary["messages"])
            if message["role"] == "assistant"
        ),
        None,
    )
    return {
        "session": session_summary,
        "assistantMessage": assistant_message,
        "agentTrace": agent_trace,
        "routeResults": results,
    }


def _load_user_sessions(user_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            sessions = cursor.execute(
                """
                select
                  s.*,
                  m.matter_number,
                  count(d.id) as document_count
                from public.consultation_sessions s
                left join public.matters m on m.id = s.matter_id
                left join public.matter_documents d on d.matter_id = m.id
                where s.user_id = %(user_id)s
                group by s.id, m.matter_number
                order by s.updated_at desc
                limit 100
                """,
                {"user_id": user_id},
            ).fetchall()
            messages = cursor.execute(
                """
                select cm.*
                from public.chat_messages cm
                join public.consultation_sessions s on s.id = cm.session_id
                where s.user_id = %(user_id)s
                order by cm.created_at asc
                """,
                {"user_id": user_id},
            ).fetchall()
    return [dict(row) for row in sessions], [dict(row) for row in messages]


def _get_session_summary(session_id: str, user_id: str) -> dict[str, Any]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            session = cursor.execute(
                """
                select
                  s.*,
                  m.matter_number,
                  count(d.id) as document_count
                from public.consultation_sessions s
                left join public.matters m on m.id = s.matter_id
                left join public.matter_documents d on d.matter_id = m.id
                where s.id = %(session_id)s and s.user_id = %(user_id)s
                group by s.id, m.matter_number
                """,
                {"session_id": session_id, "user_id": user_id},
            ).fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Unknown consultation session")
    return _session_summary(dict(session), _session_messages(session_id, user_id))


def _session_messages(session_id: str, user_id: str) -> list[dict[str, Any]]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            rows = cursor.execute(
                """
                select cm.*
                from public.chat_messages cm
                join public.consultation_sessions s on s.id = cm.session_id
                where cm.session_id = %(session_id)s and s.user_id = %(user_id)s
                order by cm.created_at asc
                """,
                {"session_id": session_id, "user_id": user_id},
            ).fetchall()
    return [_message_summary(dict(row)) for row in rows]


def _assert_session_owner(session_id: str, user_id: str) -> dict[str, Any]:
    with connect_postgres(get_settings()) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            session = cursor.execute(
                """
                select *
                from public.consultation_sessions
                where id = %(session_id)s and user_id = %(user_id)s
                """,
                {"session_id": session_id, "user_id": user_id},
            ).fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Unknown consultation session")
    return dict(session)


def _session_summary(session: dict[str, Any], messages: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": str(session["id"]),
        "title": session["title"],
        "query": session.get("query") or "",
        "matterNumber": session.get("matter_number"),
        "routeName": session.get("route_label"),
        "routeId": session.get("route_id"),
        "readiness": session.get("readiness_score"),
        "documentCount": int(session.get("document_count") or 0),
        "messages": messages,
        "createdAt": _iso(session.get("created_at")),
        "updatedAt": _iso(session.get("updated_at")),
    }


def _message_summary(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(message["id"]),
        "role": message["role"],
        "text": message["content"],
        "metadata": message.get("metadata") or {},
        "createdAt": _iso(message.get("created_at")),
    }


def _insert_chat_message(
    *,
    connection: Any,
    session_id: str,
    user_id: str,
    role: str,
    content: str,
    metadata: dict[str, Any],
) -> None:
    connection.execute(
        """
        insert into public.chat_messages (session_id, user_id, role, content, metadata)
        values (%(session_id)s, %(user_id)s, %(role)s, %(content)s, %(metadata)s)
        """,
        {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "metadata": Jsonb(metadata),
        },
    )


def _sse(event: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"event: {event}\ndata: {payload}\n\n"


def _pending_agent_trace(*, message: str, focus_role: str | None) -> list[dict[str, Any]]:
    trace: list[dict[str, Any]] = []
    for index, role in enumerate(AGENT_ROLES):
        status = "running" if index == 0 else "queued"
        trace.append(
            {
                "id": f"pending-{role['role']}",
                "agentRole": role["role"],
                "agentName": role["name"],
                "provider": role["provider"],
                "status": status,
                "isFocus": focus_role == role["role"],
                "summary": "Reading the question." if index == 0 else "Waiting for shared context.",
                "output": _trim(message, 160) if index == 0 else "Queued in the consultation flow.",
                "nextAction": "Pass context to the next check.",
                "citations": [],
            }
        )
    return trace


def _trace_with_progress(
    agent_trace: list[dict[str, Any]],
    *,
    running_index: int | None = None,
    completed_through: int = 0,
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for index, step in enumerate(agent_trace):
        next_step = dict(step)
        if index < completed_through:
            next_step["status"] = "completed"
        elif running_index is not None and index == running_index:
            next_step["status"] = "running"
        else:
            next_step["status"] = "queued"
        projected.append(next_step)
    return projected


def _infer_agent_focus(message: str) -> str | None:
    lower = message.lower()
    for alias, role in AGENT_MENTION_ALIASES.items():
        if alias in lower:
            return role
    if "risk" in lower:
        return "risk"
    if "document" in lower or "evidence" in lower:
        return "evidence"
    if "source" in lower or "law" in lower or "legal" in lower:
        return "legal_source"
    if "appeal" in lower or "packet" in lower:
        return "appeal_packet"
    return None


def _build_agent_trace(
    *,
    message: str,
    results: list[dict[str, Any]],
    facts: dict[str, Any],
    documents: list[str],
    focus_role: str | None,
) -> list[dict[str, Any]]:
    primary = results[0] if results else None
    missing_facts = primary.get("missing_facts", []) if primary else []
    missing_evidence = primary.get("missing_evidence", []) if primary else []
    risks = primary.get("risk_flags", []) if primary else []
    sources = _source_bundle(results)

    summaries = {
        "intake": f"Captured the question and normalized {len(facts)} structured facts.",
        "conflict_kyc": "Kept the consultation private and bounded to user-provided facts.",
        "decision_parser": (
            f"Best current route: {primary['route']['name']} at {primary['match_score']}% match."
            if primary
            else "No strong route yet; more facts needed."
        ),
        "legal_source": (
            f"Attached {len(sources)} official/source references for this turn."
            if sources
            else "No source bundle attached yet."
        ),
        "evidence": (
            f"Found {len(missing_evidence)} missing evidence items and {len(documents)} supplied document signals."
        ),
        "risk": (
            f"Flagged {len(risks)} route risk signals."
            if risks
            else "No high-risk signal from this message alone."
        ),
        "appeal_packet": (
            f"Packet readiness is {primary['readiness']['score']}% for the current route."
            if primary
            else "Packet cannot be assembled until route and facts are clearer."
        ),
        "partner_review": "Checked product boundary: private AI packet, no automatic authority filing.",
    }
    outputs = {
        "intake": _trim(message, 160),
        "conflict_kyc": "No filing, account action, or external submission was triggered.",
        "decision_parser": _route_output(primary),
        "legal_source": _source_output(sources),
        "evidence": _evidence_output(missing_evidence, missing_facts),
        "risk": _risk_output(risks),
        "appeal_packet": _packet_output(primary),
        "partner_review": "Continue the conversation here, create a workspace, or upload evidence when ready.",
    }

    trace: list[dict[str, Any]] = []
    for index, role in enumerate(AGENT_ROLES, start=1):
        is_focus = focus_role == role["role"]
        trace.append(
            {
                "id": f"{index:02d}-{role['role']}",
                "agentRole": role["role"],
                "agentName": role["name"],
                "provider": role["provider"],
                "status": "completed",
                "isFocus": is_focus,
                "summary": summaries[role["role"]],
                "output": outputs[role["role"]],
                "nextAction": _next_action(role["role"], primary),
                "citations": [source["title"] for source in sources[:2]] if role["role"] == "legal_source" else [],
            }
        )
    return trace


def _build_chat_answer(
    *,
    message: str,
    session: dict[str, Any],
    results: list[dict[str, Any]],
    agent_trace: list[dict[str, Any]],
    focus_role: str | None,
) -> str:
    primary = results[0] if results else None
    deterministic = _deterministic_chat_answer(
        message=message,
        session=session,
        primary=primary,
        agent_trace=agent_trace,
        focus_role=focus_role,
    )
    settings = get_settings()
    provider = ModelProvider.AIML if settings.aiml_api_key else ModelProvider.FEATHERLESS
    model_answer = complete_chat(
        settings=settings,
        provider=provider,
        system_prompt=(
            "You are LexNordic, a private Swedish migration-law AI consultation workspace. "
            "Answer conversationally. Use the supplied agent trace and route result. "
            "Do not claim authority filing, guaranteed outcomes, or final legal advice. "
            "Invite the user to keep asking natural follow-up questions, choose Documents/Risks/Sources/Packet prompts, "
            "or create a private workspace when ready."
        ),
        user_payload={
            "user_message": message,
            "existing_session": {
                "title": session.get("title"),
                "route_id": session.get("route_id"),
                "route_label": session.get("route_label"),
                "readiness_score": session.get("readiness_score"),
            },
            "primary_route": primary,
            "agent_trace": agent_trace,
        },
    )
    return model_answer or deterministic


def _deterministic_chat_answer(
    *,
    message: str,
    session: dict[str, Any],
    primary: dict[str, Any] | None,
    agent_trace: list[dict[str, Any]],
    focus_role: str | None,
) -> str:
    focus_agent = next((step for step in agent_trace if step["agentRole"] == focus_role), None)
    if primary:
        route = primary["route"]
        readiness = primary["readiness"]
        next_questions = primary.get("next_questions", [])[:3]
        missing_evidence = [item["label"] for item in primary.get("missing_evidence", [])[:3]]
        lines = [
            (
                f"{_focus_answer_label(focus_role)}: {focus_agent['output']}"
                if focus_agent
                else f"I can keep this as an open consultation. Current best route: {route['name']}."
            ),
            f"Route match is {primary['match_score']}% and packet readiness is {readiness['score']}%.",
        ]
        if route.get("summary"):
            lines.append(route["summary"])
        if missing_evidence:
            lines.append(f"Evidence still needed: {', '.join(missing_evidence)}.")
        if next_questions:
            lines.append(f"Next facts I need: {' '.join(next_questions)}")
        lines.append("You can keep asking here. For focused help, use Documents, Risks, Sources, or Packet below.")
        return "\n\n".join(lines)

    route_label = session.get("route_label") or "the migration route"
    return (
        f"I can continue the consultation around {route_label}, but I need a bit more detail from your message: "
        f"{message}. Tell me your current permit/status, deadline or expiry date, and the outcome you want."
    )


def _route_output(primary: dict[str, Any] | None) -> str:
    if not primary:
        return "Route unclear."
    return f"{primary['route']['name']} / readiness {primary['readiness']['score']}%."


def _source_output(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "No legal source rows were selected for this turn."
    return "; ".join(source["title"] for source in sources[:3])


def _evidence_output(missing_evidence: list[dict[str, Any]], missing_facts: list[dict[str, Any]]) -> str:
    labels = [item["label"] for item in missing_evidence[:3]]
    facts = [item["label"] for item in missing_facts[:2]]
    if labels:
        return f"Collect: {', '.join(labels)}."
    if facts:
        return f"Need facts first: {', '.join(facts)}."
    return "No obvious evidence blocker from this message."


def _risk_output(risks: list[str]) -> str:
    if not risks:
        return "No high-risk flag from this turn; still verify deadlines and current status."
    return ", ".join(risks[:4]).replace("_", " ")


def _packet_output(primary: dict[str, Any] | None) -> str:
    if not primary:
        return "Packet waits for route selection."
    state = "ready to organize" if primary["readiness"]["score"] >= 80 else "needs more facts/evidence"
    return f"Private case packet is {state}; no authority filing is triggered."


def _focus_answer_label(role: str | None) -> str:
    return (
        {
            "intake": "Intake check",
            "conflict_kyc": "Risk boundary check",
            "decision_parser": "Route check",
            "legal_source": "Source check",
            "evidence": "Document check",
            "risk": "Risk check",
            "appeal_packet": "Packet check",
            "partner_review": "Final check",
        }.get(role or "", "Focused check")
    )


def _next_action(role: str, primary: dict[str, Any] | None) -> str:
    if role == "evidence":
        return "Upload or list the strongest documents."
    if role == "legal_source":
        return "Open Route or Packet to review sources."
    if role == "risk":
        return "Verify deadline, current status, and adverse decision facts."
    if role == "appeal_packet":
        return "Create a workspace when the user is ready."
    if primary:
        return "Continue the consultation with a follow-up question."
    return "Ask for current permit/status and goal."


def _source_bundle(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    sources: list[dict[str, Any]] = []
    for result in results:
        for source in result.get("source_bundle", []):
            key = source.get("url") or source.get("title")
            if not key or key in seen:
                continue
            seen.add(key)
            sources.append(source)
    return sources[:6]


def _next_title(session: dict[str, Any], primary: dict[str, Any] | None, message: str) -> str:
    current = str(session.get("title") or "")
    if current and current != "New consultation":
        return current
    if primary:
        return str(primary["route"]["name"])[:160]
    return _clean_title(None, message)


def _trim(value: str, max_chars: int) -> str:
    return value if len(value) <= max_chars else value[: max_chars - 1].rstrip() + "..."


def _clean_title(title: str | None, query: str | None) -> str:
    candidate = (title or "").strip()
    if candidate:
        return candidate[:160]
    candidate = " ".join((query or "").split())
    if candidate:
        return candidate[:120] + ("..." if len(candidate) > 120 else "")
    return "New consultation"


def _iso(value: Any) -> str | None:
    return value.isoformat() if hasattr(value, "isoformat") else value
