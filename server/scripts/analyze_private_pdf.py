from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.documents.private_pdf import analyze_private_pdf, summarize_analysis


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a private local PDF without saving raw extracted text."
    )
    parser.add_argument("pdf_path", nargs="?", help="Exact local PDF path.")
    parser.add_argument(
        "--glob",
        dest="glob_pattern",
        help="Glob pattern for filenames that are awkward to type exactly.",
    )
    parser.add_argument(
        "--include-redacted-snippets",
        action="store_true",
        help="Include short snippets with obvious identifiers redacted.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Print full structural analysis instead of compact summary.",
    )
    return parser.parse_args()


def resolve_pdf_path(args: argparse.Namespace) -> Path:
    if args.glob_pattern:
        pattern = Path(args.glob_pattern)
        if pattern.is_absolute():
            matches = list(pattern.parent.glob(pattern.name))
        else:
            matches = list(Path().glob(args.glob_pattern))
        if len(matches) != 1:
            raise SystemExit(f"Expected exactly one match for --glob, found {len(matches)}")
        return matches[0]
    if not args.pdf_path:
        raise SystemExit("Provide a PDF path or --glob pattern")
    return Path(args.pdf_path)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    logging.getLogger("pypdf").setLevel(logging.ERROR)

    args = parse_args()
    analysis = analyze_private_pdf(
        resolve_pdf_path(args),
        include_redacted_snippets=args.include_redacted_snippets,
    )
    payload = analysis if args.full else summarize_analysis(analysis)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
