from __future__ import annotations

import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from pypdf import PdfReader


PERSON_ID_RE = re.compile(r"\b(?:(?:19|20)?\d{6}[-+]\d{4}|\d{8}[-+]\d{4})\b")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{6,}\d)(?!\d)")
CASE_REF_RE = re.compile(r"\b[A-Z]{1,3}\s*\d{1,6}[-/]\d{2,4}\b")


def analyze_private_pdf(path: Path, *, include_redacted_snippets: bool = False) -> dict[str, Any]:
    pdf_path = path.resolve()
    reader = PdfReader(str(pdf_path))
    page_texts = [(page.extract_text() or "") for page in reader.pages]
    full_text = "\n\n".join(page_texts)
    folded = _fold(full_text)

    analysis: dict[str, Any] = {
        "file": {
            "name": pdf_path.name,
            "bytes": pdf_path.stat().st_size,
            "sha256_prefix": _sha256_prefix(pdf_path),
            "pages": len(reader.pages),
            "encrypted": bool(reader.is_encrypted),
            "text_chars": len(full_text),
            "extractable_text": len(full_text.strip()) > 0,
        },
        "privacy": {
            "raw_text_saved": False,
            "contains_personal_identifier": bool(PERSON_ID_RE.search(full_text)),
            "contains_email": bool(EMAIL_RE.search(full_text)),
            "contains_phone_like_number": bool(PHONE_RE.search(full_text)),
            "safe_for_public_demo": False,
            "recommended_public_use": "derive a sanitized fictional fixture; do not show this PDF raw",
        },
        "classification": {
            "document_type": _document_type(folded),
            "language": _language(folded),
            "procedural_stage": _procedural_stage(folded),
            "permit_signals": _permit_signals(folded),
            "risk_flags": _risk_flags(folded, full_text),
            "high_sensitivity_review_required": True,
        },
        "extracted_structure": {
            "case_refs": sorted(set(CASE_REF_RE.findall(full_text))),
            "dates": _extract_dates(full_text),
            "authorities_mentioned": _authorities_mentioned(folded),
            "headings": _headings(full_text),
            "page_char_counts": [len(text) for text in page_texts],
        },
        "agent_plan": _agent_plan(),
    }

    if include_redacted_snippets:
        analysis["redacted_snippets"] = _redacted_snippets(full_text)

    return analysis


def _sha256_prefix(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()[:16]


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def _document_type(folded: str) -> str:
    if "overklagande" in folded:
        return "appeal"
    if "dom" in folded and "migrationsdomstol" in folded:
        return "court_decision"
    if "beslut" in folded and "migrationsverket" in folded:
        return "agency_decision"
    return "unknown_migration_document"


def _language(folded: str) -> str:
    swedish_markers = ("overklagande", "yrkande", "grunder", "migrationsverket")
    return "sv" if any(marker in folded for marker in swedish_markers) else "unknown"


def _procedural_stage(folded: str) -> str:
    if "migrationsoverdomstol" in folded or "provningstillstand" in folded:
        return "migration_court_of_appeal"
    if "migrationsdomstol" in folded:
        return "migration_court"
    if "migrationsverket" in folded:
        return "agency"
    return "unknown"


def _permit_signals(folded: str) -> list[str]:
    signals: list[str] = []
    checks = {
        "higher_education_studies": ("studier inom hogre utbildning", "hogre utbildning"),
        "post_study_job_search": ("soka arbete", "efter avslutade studier"),
        "work_permit": ("arbetstillstand", "uppehallstillstand for arbete"),
        "removal_or_expulsion": ("utvisning", "avvisning"),
    }
    for signal, markers in checks.items():
        if any(marker in folded for marker in markers):
            signals.append(signal)
    return signals


def _risk_flags(folded: str, text: str) -> list[str]:
    flags: list[str] = []
    if PERSON_ID_RE.search(text):
        flags.append("real_personal_identifier")
    if "utvisning" in folded or "avvisning" in folded:
        flags.append("removal_or_expulsion_order")
    if "migrationsoverdomstol" in folded or "provningstillstand" in folded:
        flags.append("court_of_appeal_stage")
    if "anst" in folded or "anstund" in folded:
        flags.append("extension_or_deadline_sensitive")
    if "ombud" in folded or "advokat" in folded:
        flags.append("represented_party")
    return flags


def _extract_dates(text: str) -> list[str]:
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s+(?:januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s+\d{4}\b",
    ]
    dates: list[str] = []
    for pattern in patterns:
        dates.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return sorted(set(dates))


def _authorities_mentioned(folded: str) -> list[str]:
    checks = {
        "Migrationsverket": "migrationsverket",
        "Migrationsdomstolen": "migrationsdomstol",
        "Migrationsöverdomstolen": "migrationsoverdomstol",
        "Förvaltningsrätten": "forvaltningsratten",
    }
    return [label for label, marker in checks.items() if marker in folded]


def _headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        cleaned = " ".join(line.split())
        if not cleaned or len(cleaned) > 100:
            continue
        if re.match(r"^\d+(?:\.\d+)*\s+[A-Z0-9A-ZÅÄÖa-zåäö ,.-]+$", cleaned):
            headings.append(_redact(cleaned))
        elif cleaned.isupper() and len(cleaned) >= 5:
            headings.append(_redact(cleaned))
    return _dedupe_preserve_order(headings)[:25]


def _redacted_snippets(text: str, *, max_snippets: int = 5) -> list[str]:
    snippets: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        cleaned = " ".join(block.split())
        if len(cleaned) < 30:
            continue
        snippets.append(_redact(cleaned[:500]))
        if len(snippets) >= max_snippets:
            break
    return snippets


def _redact(text: str) -> str:
    redacted = PERSON_ID_RE.sub("[PERSON_ID]", text)
    redacted = EMAIL_RE.sub("[EMAIL]", redacted)
    redacted = PHONE_RE.sub("[PHONE]", redacted)
    return redacted


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _agent_plan() -> list[dict[str, str]]:
    return [
        {
            "agent": "Decision Parser",
            "job": "Extract procedural posture, claims, case refs, dates, and permit categories.",
        },
        {
            "agent": "Evidence",
            "job": "Turn claims into missing-evidence checklist for studies, job-search, or work basis.",
        },
        {
            "agent": "Legal Source",
            "job": "Use Qdrant /legal routes to build source bundle with official rules and MIG candidates.",
        },
        {
            "agent": "Risk",
            "job": "Flag real identity, court-stage, deadline, and removal/expulsion sensitivity.",
        },
        {
            "agent": "Partner Review",
            "job": "Gate final output as private AI packet material only; never file or submit automatically.",
        },
    ]


def summarize_analysis(analysis: dict[str, Any]) -> dict[str, Any]:
    """Return a compact count-oriented view for logs and test output."""
    structure = analysis["extracted_structure"]
    classification = analysis["classification"]
    return {
        "file": analysis["file"],
        "privacy": analysis["privacy"],
        "classification": classification,
        "counts": {
            "case_refs": len(structure["case_refs"]),
            "dates": len(structure["dates"]),
            "headings": len(structure["headings"]),
            "authorities": len(structure["authorities_mentioned"]),
        },
        "top_permit_signal": _most_common(classification["permit_signals"]),
    }


def _most_common(values: list[str]) -> str | None:
    if not values:
        return None
    return Counter(values).most_common(1)[0][0]
