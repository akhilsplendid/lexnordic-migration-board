from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.settings import Settings


SEED_MIG_IDS = {
    "MIG 2017:2",
    "MIG 2017:16",
    "MIG 2017:18",
    "MIG 2017:24",
    "MIG 2017:25",
    "MIG 2025:1",
}


OFFICIAL_SOURCE_PACK: list[dict[str, str]] = [
    {
        "source_id": "official:migrationsverket:appeal-decision",
        "source_type": "official_rule",
        "title": "Migrationsverket: Appeal a decision",
        "citation": "Migrationsverket, Appeal a decision",
        "url": "https://www.migrationsverket.se/en/word-explanations/appeal-a-decision.html",
        "workflow_stage": "appeal",
        "summary": "Official appeal-process source. Decision-specific instructions and deadlines control.",
    },
    {
        "source_id": "official:migrationsverket:work-rejection",
        "source_type": "official_rule",
        "title": "Migrationsverket: Work application rejected",
        "citation": "Migrationsverket, Work application rejected",
        "url": "https://www.migrationsverket.se/en/you-have-received-a-decision/work/your-application-has-been-rejected.html",
        "workflow_stage": "appeal",
        "summary": "Official source for rejected work-permit decisions and appeal handling.",
    },
    {
        "source_id": "official:migrationsverket:work-employees",
        "source_type": "official_rule",
        "title": "Migrationsverket: Work permit for employees",
        "citation": "Migrationsverket, Work permit for employees",
        "url": "https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/employees.html",
        "workflow_stage": "requirements",
        "summary": "Official source for employee work-permit requirements and evidence checks.",
    },
    {
        "source_id": "official:migrationsverket:salary-requirements",
        "source_type": "official_rule",
        "title": "Migrationsverket: Salary requirements for a work permit",
        "citation": "Migrationsverket, Salary requirements for a work permit",
        "url": "https://www.migrationsverket.se/en/word-explanations/salary-requirements-for-a-work-permit.html",
        "workflow_stage": "requirements",
        "summary": "Official source for current salary threshold categories and transition rules.",
    },
    {
        "source_id": "official:migrationsverket:occupation-exemptions-2026",
        "source_type": "official_rule",
        "title": "Migrationsverket: Labour immigration occupation exemptions",
        "citation": "Migrationsverket, occupation exemptions, 2026-05-25",
        "url": "https://www.migrationsverket.se/en/news-archive/news/2026-05-25-new-rules-for-labour-immigration---these-occupations-are-exempted.html",
        "workflow_stage": "requirements",
        "summary": "Official source for occupations and groups exempted from the 90 percent salary threshold.",
    },
    {
        "source_id": "official:migrationsverket:work-permit-rules-2026-06-01",
        "source_type": "official_rule",
        "title": "Migrationsverket: New rules for work permits now apply",
        "citation": "Migrationsverket news, 2026-06-01",
        "url": "https://www.migrationsverket.se/nyheter/news-archive/2026-06-01-new-rules-for-work-permits-now-apply.html",
        "workflow_stage": "current_rules",
        "summary": "Official source for work-permit rule changes that apply from 1 June 2026.",
    },
    {
        "source_id": "official:government:aliens-act-overview",
        "source_type": "statute",
        "title": "Government of Sweden: Aliens Act overview",
        "citation": "Government Offices of Sweden, Aliens Act overview",
        "url": "https://www.government.se/government-policy/migration-and-asylum/aliens-act/",
        "workflow_stage": "legal_system",
        "summary": "Official government overview for statutory grounding and source hierarchy.",
    },
    {
        "source_id": "official:bar:code-of-conduct",
        "source_type": "guidance",
        "title": "Swedish Bar Association: Code of Conduct",
        "citation": "Swedish Bar Association, Code of Conduct",
        "url": "https://www.advokatsamfundet.com/rules-and-regulations/code-of-conduct/",
        "workflow_stage": "law_firm_controls",
        "summary": "Professional conduct source for confidentiality, independence, conflicts, and AI packet governance.",
    },
]


LOCAL_SOURCE_DOCS: list[dict[str, str]] = [
    {
        "source_id": "local:rules:swedish-migration-june-2026",
        "source_type": "official_rule",
        "title": "Recent Swedish Migration Rule Changes - June 2026",
        "citation": "LexNordic source note, checked 2026-06-12",
        "path": "docs/domain/recent-rule-changes-2026-06.md",
        "workflow_stage": "current_rules",
    },
    {
        "source_id": "local:source-map:swedish-migration",
        "source_type": "guidance",
        "title": "Swedish Migration Source Map",
        "citation": "LexNordic source map",
        "path": "docs/domain/swedish-migration-source-map.md",
        "workflow_stage": "source_hierarchy",
    },
    {
        "source_id": "local:corpus:mig-inventory",
        "source_type": "guidance",
        "title": "Migration Corpus Inventory",
        "citation": "LexNordic migration corpus inventory",
        "path": "docs/domain/migration-corpus-inventory.md",
        "workflow_stage": "case_law",
    },
    {
        "source_id": "local:secondary:eu-migration-law-note",
        "source_type": "secondary_context",
        "title": "EU Migration Law Secondary Source Note",
        "citation": "LexNordic private secondary-source note",
        "path": "docs/domain/eu-migration-law-secondary-source.md",
        "workflow_stage": "background",
    },
]


@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    source_type: str
    title: str
    citation: str
    text: str
    url: str | None = None
    source_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LegalChunk:
    chunk_id: str
    source_id: str
    chunk_index: int
    text: str
    payload: dict[str, Any]


def repair_mojibake(text: str) -> tuple[str, str]:
    markers = ("\u00c3", "\u00c2", "\u00e2\u20ac", "\ufffd")
    original_score = sum(text.count(marker) for marker in markers)
    if original_score == 0:
        return text, "clean"

    try:
        repaired = text.encode("cp1252").decode("utf-8")
    except UnicodeError:
        return text, "suspect"

    repaired_score = sum(repaired.count(marker) for marker in markers)
    if repaired_score < original_score:
        return repaired, "repaired_mojibake"
    return text, "suspect"


def folded_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return normalized.encode("ascii", "ignore").decode("ascii").lower()


def load_local_source_documents(project_root: Path) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for item in LOCAL_SOURCE_DOCS:
        path = project_root / item["path"]
        text = path.read_text(encoding="utf-8")
        documents.append(
            SourceDocument(
                source_id=item["source_id"],
                source_type=item["source_type"],
                title=item["title"],
                citation=item["citation"],
                text=text,
                source_path=str(path),
                metadata={
                    "jurisdiction": "SE",
                    "workflow_stage": item["workflow_stage"],
                    "source_priority": _source_priority(item["source_type"]),
                    "last_checked": "2026-06-12",
                    "private_source_text": item["source_type"] == "secondary_context",
                },
            )
        )
    return documents


def load_official_source_pack(fetch: bool = True) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    for item in OFFICIAL_SOURCE_PACK:
        metadata: dict[str, Any] = {
            "jurisdiction": "SE",
            "workflow_stage": item["workflow_stage"],
            "source_priority": _source_priority(item["source_type"]),
            "last_checked": "2026-06-13",
        }
        text = item["summary"]
        if fetch:
            fetched_text, fetch_status = _fetch_url_text(item["url"])
            metadata["fetch_status"] = fetch_status
            if fetched_text:
                text = f"{item['summary']}\n\n{fetched_text}"
        documents.append(
            SourceDocument(
                source_id=item["source_id"],
                source_type=item["source_type"],
                title=item["title"],
                citation=item["citation"],
                text=text,
                url=item["url"],
                metadata=metadata,
            )
        )
    return documents


def load_mig_documents(
    *,
    settings: Settings,
    scope: str = "seed",
    max_records: int | None = None,
) -> list[SourceDocument]:
    corpus_root = settings.mig_corpus_path
    index_path = corpus_root / "master_index.json"
    records = json.loads(index_path.read_text(encoding="utf-8"))
    selected = _select_mig_records(records, scope=scope)
    if max_records is not None:
        selected = selected[:max_records]

    documents: list[SourceDocument] = []
    for record in selected:
        mig_id = str(record.get("mig", "")).strip()
        text_path = _normalize_corpus_path(record.get("text_path"), corpus_root)
        if not mig_id or not text_path or not text_path.exists():
            continue

        raw_text = text_path.read_text(encoding="utf-8", errors="replace")
        text, encoding_quality = repair_mojibake(raw_text)
        title_summary = str(record.get("title_summary") or "")
        year = _mig_year(mig_id)
        source_family = _mig_source_family(record)
        permit_type, legal_issue = _classify_mig_case(title_summary, text)
        risk_flags = _risk_flags(title_summary + "\n" + text[:6000])
        url = record.get("source_url") or record.get("page_url")

        documents.append(
            SourceDocument(
                source_id=f"mig:{mig_id}",
                source_type="mig_case",
                title=f"{mig_id}: {title_summary}" if title_summary else mig_id,
                citation=mig_id,
                text=text,
                url=str(url) if url else None,
                source_path=str(text_path),
                metadata={
                    "jurisdiction": "SE",
                    "language": "sv",
                    "source_priority": 3,
                    "mig_id": mig_id,
                    "year": year,
                    "decision_date": record.get("decision_date"),
                    "permit_type": permit_type,
                    "legal_issue": legal_issue,
                    "risk_flags": risk_flags,
                    "source_family": source_family,
                    "title_summary": title_summary,
                    "encoding_quality": encoding_quality,
                    "workflow_stage": "case_law",
                    "law_change_review_required": year is not None and year < 2026,
                },
            )
        )
    return documents


def build_source_documents(
    *,
    settings: Settings,
    project_root: Path,
    mig_scope: str,
    max_mig_records: int | None,
    fetch_official: bool,
) -> list[SourceDocument]:
    documents: list[SourceDocument] = []
    documents.extend(load_official_source_pack(fetch=fetch_official))
    documents.extend(load_local_source_documents(project_root))
    documents.extend(
        load_mig_documents(settings=settings, scope=mig_scope, max_records=max_mig_records)
    )
    return documents


def chunk_documents(
    documents: Iterable[SourceDocument],
    *,
    max_chars: int = 760,
    overlap_chars: int = 120,
) -> list[LegalChunk]:
    chunks: list[LegalChunk] = []
    for document in documents:
        chunks.extend(
            _chunk_document(document, max_chars=max_chars, overlap_chars=overlap_chars)
        )
    return chunks


def _chunk_document(
    document: SourceDocument,
    *,
    max_chars: int,
    overlap_chars: int,
) -> list[LegalChunk]:
    text = _normalize_text(document.text)
    if not text:
        return []

    chunks: list[LegalChunk] = []
    buffer: list[str] = []
    current_section: str | None = None
    current_page: int | None = None
    chunk_start = 0
    cursor = 0

    for block in _iter_blocks(text):
        page = _page_number(block)
        if page is not None:
            current_page = page
        heading = _heading_text(block)
        if heading:
            current_section = heading

        block_len = len(block) + 2
        current_len = sum(len(part) + 2 for part in buffer)
        if buffer and current_len + block_len > max_chars:
            chunk_text = "\n\n".join(buffer).strip()
            chunks.append(
                _make_chunk(
                    document=document,
                    chunk_index=len(chunks),
                    text=chunk_text,
                    section=current_section,
                    page=current_page,
                    start_char=chunk_start,
                    end_char=cursor,
                )
            )
            tail = _tail(chunk_text, overlap_chars)
            buffer = [tail] if tail else []
            chunk_start = max(0, cursor - len(tail))

        if len(block) > max_chars:
            for hard_chunk in _hard_split(block, max_chars=max_chars, overlap_chars=overlap_chars):
                chunks.append(
                    _make_chunk(
                        document=document,
                        chunk_index=len(chunks),
                        text=hard_chunk,
                        section=current_section,
                        page=current_page,
                        start_char=cursor,
                        end_char=cursor + len(hard_chunk),
                    )
                )
            buffer = []
        else:
            buffer.append(block)
        cursor += block_len

    if buffer:
        chunk_text = "\n\n".join(buffer).strip()
        chunks.append(
            _make_chunk(
                document=document,
                chunk_index=len(chunks),
                text=chunk_text,
                section=current_section,
                page=current_page,
                start_char=chunk_start,
                end_char=len(text),
            )
        )
    return chunks


def _make_chunk(
    *,
    document: SourceDocument,
    chunk_index: int,
    text: str,
    section: str | None,
    page: int | None,
    start_char: int,
    end_char: int,
) -> LegalChunk:
    chunk_id = f"{document.source_id}#chunk-{chunk_index:04d}"
    payload = {
        "chunk_id": chunk_id,
        "source_id": document.source_id,
        "source_type": document.source_type,
        "title": document.title,
        "citation": document.citation,
        "url": document.url,
        "source_path": document.source_path,
        "chunk_index": chunk_index,
        "section": section,
        "page": page,
        "start_char": start_char,
        "end_char": end_char,
        "text": text,
        **document.metadata,
    }
    return LegalChunk(
        chunk_id=chunk_id,
        source_id=document.source_id,
        chunk_index=chunk_index,
        text=text,
        payload={key: value for key, value in payload.items() if value is not None},
    )


def _fetch_url_text(url: str) -> tuple[str, str]:
    try:
        response = httpx.get(
            url,
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "LexNordicMigrationBoard/0.1"},
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return "", f"error:{exc.__class__.__name__}"

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type:
        return "", f"skipped_content_type:{content_type[:40]}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    lines = []
    seen: set[str] = set()
    for line in soup.get_text("\n").splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if len(cleaned) < 3 or cleaned in seen:
            continue
        seen.add(cleaned)
        lines.append(cleaned)
    return "\n".join(lines[:900]), "fetched"


def _select_mig_records(records: list[dict[str, Any]], *, scope: str) -> list[dict[str, Any]]:
    if scope == "seed":
        return [record for record in records if str(record.get("mig")) in SEED_MIG_IDS]
    if scope == "work":
        return [record for record in records if _looks_work_related(record)]
    if scope == "all":
        return records
    raise ValueError("mig scope must be one of: seed, work, all")


def _looks_work_related(record: dict[str, Any]) -> bool:
    haystack = folded_text(
        " ".join(
            str(record.get(key) or "")
            for key in ("mig", "title_summary", "source", "source_url", "page_url")
        )
    )
    keywords = (
        "arbet",
        "anstall",
        "forsorj",
        "lon",
        "semester",
        "kollektivavtal",
        "sasonsarbete",
        "uppehalls- och arbetstillstand",
    )
    return any(keyword in haystack for keyword in keywords)


def _normalize_corpus_path(raw_path: Any, corpus_root: Path) -> Path | None:
    if not raw_path:
        return None
    raw = Path(str(raw_path))
    parts = list(raw.parts)
    lowered = [part.lower() for part in parts]
    if "mig_corpus" in lowered:
        index = lowered.index("mig_corpus")
        relative = Path(*parts[index + 1 :])
        return corpus_root / relative
    if raw.is_absolute():
        return raw
    return corpus_root / raw


def _classify_mig_case(title_summary: str, text: str) -> tuple[str | None, str | None]:
    sample = folded_text(f"{title_summary}\n{text[:8000]}")
    permit_type = None
    if "arbetstillstand" in sample or "arbeta" in sample or "arbete" in sample:
        permit_type = "work_permit"
    elif "asyl" in sample:
        permit_type = "asylum"
    elif "stud" in sample:
        permit_type = "study"
    elif "anknytning" in sample or "familj" in sample:
        permit_type = "family"

    issue_checks = [
        ("salary_conditions", ("lon", "forsorj", "ersattning", "kollektivavtal")),
        ("union_preference", ("unionsforetrade", "annonsering")),
        ("extension", ("forlang", "langre an fyra ar")),
        ("return_ban", ("aterreseforbud", "utvisning", "avvisning")),
        ("employer_capacity", ("arbetsgivarens ekonomiska", "anstalla")),
        ("conduct_security", ("brott", "sakerhet", "levnadssatt")),
    ]
    legal_issue = None
    for issue, keywords in issue_checks:
        if any(keyword in sample for keyword in keywords):
            legal_issue = issue
            break
    return permit_type, legal_issue


def _risk_flags(text: str) -> list[str]:
    sample = folded_text(text)
    checks = {
        "asylum": ("asyl", "skyddsbehov", "flykting"),
        "return_or_removal": ("utvisning", "avvisning", "verkstallighet"),
        "return_ban": ("aterreseforbud",),
        "detention": ("forvar",),
        "children": ("barn", "minderarig"),
        "crime_or_security": ("brott", "sakerhet"),
    }
    return [flag for flag, keywords in checks.items() if any(keyword in sample for keyword in keywords)]


def _mig_year(mig_id: str) -> int | None:
    match = re.search(r"MIG\s+(\d{4})", mig_id)
    return int(match.group(1)) if match else None


def _mig_source_family(record: dict[str, Any]) -> str:
    source = folded_text(str(record.get("source") or ""))
    if "lagen" in source:
        return "lagen_nu_legacy"
    return "domstol"


def _source_priority(source_type: str) -> int:
    return {
        "official_rule": 1,
        "statute": 2,
        "mig_case": 3,
        "guidance": 4,
        "secondary_context": 5,
    }.get(source_type, 9)


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def _iter_blocks(text: str) -> Iterable[str]:
    for block in re.split(r"\n\s*\n", text):
        cleaned = block.strip()
        if cleaned:
            yield cleaned


def _heading_text(block: str) -> str | None:
    first_line = block.splitlines()[0].strip()
    markdown_heading = re.match(r"^#{1,6}\s+(.+)$", first_line)
    if markdown_heading:
        return markdown_heading.group(1).strip()
    if first_line.isupper() and len(first_line) <= 120:
        return first_line
    return None


def _page_number(block: str) -> int | None:
    match = re.match(r"^=+\s*PAGE\s+(\d+)\s*=+", block, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def _hard_split(text: str, *, max_chars: int, overlap_chars: int) -> Iterable[str]:
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        yield text[start:end].strip()
        if end == len(text):
            break
        start = max(start + 1, end - overlap_chars)


def _tail(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return ""
    tail = text[-max_chars:]
    sentence_break = max(tail.rfind(". "), tail.rfind("\n"))
    if sentence_break > 40:
        return tail[sentence_break + 1 :].strip()
    return tail.strip()
