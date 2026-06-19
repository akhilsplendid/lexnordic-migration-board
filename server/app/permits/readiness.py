from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Any

from app.permits.catalog import PERMIT_ROUTES, ROUTES_BY_ID, EvidenceItem, PermitRoute


def match_routes(
    *,
    query: str | None,
    route_id: str | None,
    facts: dict[str, Any],
    documents: list[str],
    limit: int = 8,
) -> list[dict[str, Any]]:
    if route_id:
        route = ROUTES_BY_ID[route_id]
        return [assess_route(route=route, query=query, facts=facts, documents=documents)]

    scored = [
        assess_route(route=route, query=query, facts=facts, documents=documents)
        for route in PERMIT_ROUTES
    ]
    scored.sort(key=lambda item: (item["match_score"], item["readiness"]["score"]), reverse=True)
    positive = [item for item in scored if item["match_score"] > 0]
    return (positive or scored)[:limit]


def assess_route(
    *,
    route: PermitRoute,
    query: str | None,
    facts: dict[str, Any],
    documents: list[str],
) -> dict[str, Any]:
    matched_signals = _matched_signals(route, query, facts)
    missing_facts = [fact for fact in route.required_facts if not _fact_present(facts, fact.key)]
    present, missing = _split_evidence(route.required_evidence, documents)
    risks = _risk_flags(route, facts)

    score = max(0, 100 - (len(missing_facts) * 9) - (len(missing) * 7) - (len(risks) * 4))
    status = _status(score=score, missing_facts=missing_facts, missing_evidence=missing, risks=risks)
    return {
        "route": route.to_dict(),
        "match_score": _match_score(route, query, facts),
        "matched_signals": matched_signals,
        "readiness": {
            "score": score,
            "status": status,
            "autonomous_output": "readiness_packet",
            "packet_gate": "ai_packet_gate_before_external_action",
        },
        "present_evidence": [asdict(item) for item in present],
        "missing_evidence": [asdict(item) for item in missing],
        "missing_facts": [asdict(item) for item in missing_facts],
        "risk_flags": risks,
        "next_questions": _next_questions(missing_facts),
        "source_bundle": [asdict(source) for source in route.sources],
    }


def _match_score(route: PermitRoute, query: str | None, facts: dict[str, Any]) -> int:
    score = 0
    haystack = " ".join((route.name, route.summary, route.family, route.phase, *route.tags)).lower()
    haystack_tokens = set(_tokens(haystack))
    query_text = (query or "").lower()
    needles = []
    if query:
        needles.extend(_tokens(query))
    for key in ("goal", "permit_type", "current_status", "route_hint"):
        value = facts.get(key)
        if isinstance(value, str):
            needles.extend(_tokens(value))
    for token in needles:
        if token in haystack_tokens:
            score += 8
    if facts.get("has_rejection") and route.family == "appeal":
        score += 35
    if facts.get("has_job_offer") and "work" in route.family:
        score += 25
    if facts.get("has_job_offer") and route.route_id == "work_student_found_work":
        score += 35
    if facts.get("has_job_offer") and route.route_id == "study_post_study_look_for_work":
        score -= 20
    if facts.get("is_student") and "study" in route.family:
        score += 20
    if facts.get("completed_studies") and "post_study" in route.tags:
        score += 30
    if facts.get("completed_studies") and route.route_id == "work_student_found_work":
        score += 25
    if facts.get("has_family_in_sweden") and "family" in route.family:
        score += 25
    if facts.get("visit_days") and route.family == "visiting":
        visit_days = _as_int(facts.get("visit_days"))
        if visit_days is not None and visit_days > 90:
            score += 45 if route.route_id == "visit_residence_over_90" else -25
        elif visit_days is not None:
            score += 45 if route.route_id == "visit_schengen_visa_90" else -15
        else:
            score += 20

    if route.route_id == "visit_residence_over_90" and _has_any_phrase(
        query_text,
        ("over 90", "more than 90", "longer than 90", "six months", "6 months", "half a year"),
    ):
        score += 40
    if route.route_id == "visit_schengen_visa_90" and _has_any_phrase(
        query_text,
        ("over 90", "more than 90", "longer than 90", "six months", "6 months", "half a year"),
    ):
        score -= 25
    if route.route_id == "visit_schengen_visa_90" and _has_any_phrase(
        query_text,
        ("up to 90", "less than 90", "short stay", "schengen visa"),
    ):
        score += 35

    if route.route_id == "work_student_found_work" and _has_any_phrase(
        query_text,
        ("found a job", "job offer", "employment contract", "start work", "work after studies"),
    ):
        score += 40
    if route.route_id == "study_post_study_look_for_work" and _has_any_phrase(
        query_text,
        ("look for work", "search for work", "start a business", "job search"),
    ):
        score += 40
    if route.family == "temporary_work" and not _has_any_phrase(
        query_text,
        ("temporary", "seasonal", "au pair", "berry", "volunteer", "working holiday", "trainee", "intern"),
    ):
        score -= 15
    if route.route_id == "work_after_visiting_employer" and not (
        facts.get("has_job_offer") or facts.get("has_employer") or facts.get("employer_and_role")
    ):
        score -= 20

    if route.route_id == "family_partner_child_relative" and _has_any_phrase(
        query_text,
        ("partner", "spouse", "wife", "husband", "cohabitant", "sambo"),
    ):
        score += 35
    if route.route_id == "family_child_residence" and _has_any_phrase(
        query_text,
        ("child", "children", "parent", "adoption", "born in sweden"),
    ):
        score += 30
    if route.route_id == "appeal_decision" and _has_any_phrase(
        query_text,
        ("appeal", "rejected", "refused", "denied", "decision"),
    ):
        score += 35

    return max(0, min(score, 100))


def _matched_signals(route: PermitRoute, query: str | None, facts: dict[str, Any]) -> list[str]:
    signals: list[str] = []
    if query:
        query_tokens = set(_tokens(query))
        signals.extend(tag for tag in route.tags if tag.replace("_", "") in query_tokens or tag in query_tokens)
    for key in ("has_rejection", "has_job_offer", "is_student", "completed_studies", "has_family_in_sweden"):
        if facts.get(key):
            signals.append(key)
    return sorted(set(signals))


def _tokens(value: str) -> list[str]:
    stopwords = {
        "and",
        "apply",
        "application",
        "been",
        "day",
        "days",
        "for",
        "had",
        "has",
        "have",
        "month",
        "months",
        "more",
        "need",
        "permit",
        "residence",
        "sweden",
        "swedish",
        "than",
        "the",
        "was",
        "will",
        "with",
        "want",
    }
    tokens: list[str] = []
    for raw_token in value.replace("-", " ").replace("/", " ").replace("_", " ").split():
        token = raw_token.strip(".,;:()[]{}!?").lower()
        if token and len(token) >= 3 and token not in stopwords:
            tokens.append(token)
    return tokens


def _fact_present(facts: dict[str, Any], key: str) -> bool:
    if key not in facts:
        return False
    value = facts[key]
    return value is not None and value != "" and value != []


def _split_evidence(
    required: tuple[EvidenceItem, ...],
    documents: list[str],
) -> tuple[list[EvidenceItem], list[EvidenceItem]]:
    doc_tokens = {_normalize(document) for document in documents}
    present: list[EvidenceItem] = []
    missing: list[EvidenceItem] = []
    for item in required:
        candidates = {_normalize(item.key), *(_normalize(alias) for alias in item.aliases)}
        if any(candidate in doc_tokens for candidate in candidates):
            present.append(item)
            continue
        if any(
            candidate and any(candidate in document or document in candidate for document in doc_tokens)
            for candidate in candidates
        ):
            present.append(item)
            continue
        missing.append(item)
    return present, missing


def _normalize(value: str) -> str:
    return value.lower().replace(" ", "_").replace("-", "_").strip()


def _has_any_phrase(value: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in value for phrase in phrases)


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _risk_flags(route: PermitRoute, facts: dict[str, Any]) -> list[str]:
    risks = list(route.risk_flags)
    if facts.get("has_removal_order") or facts.get("has_expulsion_order"):
        risks.append("removal_or_expulsion_order")
    if facts.get("current_permit_expired"):
        risks.append("current_permit_already_expired")
    if facts.get("permit_expires_within_30_days"):
        risks.append("permit_expires_within_30_days")
    if facts.get("has_criminal_record"):
        risks.append("conduct_or_security_review")
    if facts.get("has_asylum_or_protection_history") and route.family not in {"protection", "appeal"}:
        risks.append("protection_history_affects_route")
    if facts.get("deadline_date"):
        try:
            deadline = date.fromisoformat(str(facts["deadline_date"]))
            if deadline < date.today():
                risks.append("deadline_appears_past")
        except ValueError:
            risks.append("deadline_format_unverified")
    return sorted(set(risks))


def _status(
    *,
    score: int,
    missing_facts: list[Any],
    missing_evidence: list[Any],
    risks: list[str],
) -> str:
    high_risk = any(
        risk in risks
        for risk in (
            "removal_or_expulsion_order",
            "deadline_appears_past",
            "high_sensitivity_boundary_review",
            "do_not_autonomously_complete_final_claim",
        )
    )
    if high_risk:
        return "high_risk_review"
    if missing_facts or missing_evidence:
        return "needs_information"
    if score >= 85:
        return "packet_ready_for_review"
    return "consultation_recommended"


def _next_questions(missing_facts: list[Any]) -> list[str]:
    return [f"{item.label}: {item.reason}" for item in missing_facts[:8]]
