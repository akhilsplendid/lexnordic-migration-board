from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.clients.embeddings import AimlEmbeddingClient
from app.clients.qdrant import create_qdrant_client
from app.legal.retrieval import LegalRetriever
from app.settings import get_settings


DEFAULT_QUERIES = [
    "Where do appeals go first after a rejected Swedish work permit decision?",
    "Does the 1 June 2026 salary rule affect a first-time work permit rejection?",
    "Which MIG cases are relevant for salary or employment-condition issues?",
    "Which migration facts should be flagged as high-sensitivity risks?",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test LexNordic legal retrieval.")
    parser.add_argument("queries", nargs="*", default=DEFAULT_QUERIES)
    parser.add_argument("--limit", type=int, default=4)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    retriever = LegalRetriever(
        qdrant=create_qdrant_client(settings),
        embeddings=AimlEmbeddingClient.from_settings(settings),
        settings=settings,
    )

    for query in args.queries:
        print(f"\nQUERY: {query}")
        for result in retriever.search(query=query, limit=args.limit):
            print(
                f"- {result.score:.4f} | {result.source_type} | "
                f"{result.citation} | {result.title[:90]}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
