from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.clients.embeddings import AimlEmbeddingClient
from app.clients.qdrant import create_qdrant_client
from app.legal.retrieval import ensure_legal_collection, upsert_legal_chunks
from app.legal.source_documents import build_source_documents, chunk_documents
from app.settings import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest legal sources into Qdrant.")
    parser.add_argument(
        "--mig-scope",
        choices=("seed", "work", "all"),
        default="seed",
        help="MIG corpus scope to ingest. Default keeps the hackathon seed set small.",
    )
    parser.add_argument("--max-mig-records", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--overlap-chars", type=int, default=120)
    parser.add_argument("--skip-official-fetch", action="store_true")
    parser.add_argument("--recreate", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    project_root = ROOT.parent

    qdrant = create_qdrant_client(settings)
    embedder = AimlEmbeddingClient.from_settings(settings)
    ensure_legal_collection(qdrant=qdrant, settings=settings, recreate=args.recreate)

    documents = build_source_documents(
        settings=settings,
        project_root=project_root,
        mig_scope=args.mig_scope,
        max_mig_records=args.max_mig_records,
        fetch_official=not args.skip_official_fetch,
    )
    max_chars = args.max_chars or max(300, settings.legal_embedding_max_chars - 40)
    chunks = chunk_documents(
        documents,
        max_chars=max_chars,
        overlap_chars=args.overlap_chars,
    )

    document_counts = Counter(document.source_type for document in documents)
    chunk_counts = Counter(chunk.payload["source_type"] for chunk in chunks)
    print(f"documents={len(documents)} {dict(sorted(document_counts.items()))}")
    print(f"chunks={len(chunks)} {dict(sorted(chunk_counts.items()))}")

    for start in range(0, len(chunks), args.batch_size):
        batch = chunks[start : start + args.batch_size]
        vectors = embedder.embed_texts([chunk.text for chunk in batch])
        upsert_legal_chunks(qdrant=qdrant, settings=settings, chunks=batch, vectors=vectors)
        print(f"upserted={start + len(batch)}/{len(chunks)}")

    count = qdrant.count(settings.qdrant_collection_legal_sources, exact=True).count
    print(f"collection={settings.qdrant_collection_legal_sources} points={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
