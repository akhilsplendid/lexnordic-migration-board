# LexNordic FastAPI Server

This server is the control plane between the React dashboard, Supabase, Qdrant, Band agents, AI/ML API, and Featherless.

## Local Setup

```powershell
cd <project-root>
copy .env.example .env.local
```

Fill `.env.local` with local credentials. The file is ignored by git.

Run:

```powershell
cd server
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Connection checks:

```powershell
uv run python scripts/check_connections.py
```

Legal source ingestion:

```powershell
uv run python scripts/ingest_legal_sources.py --mig-scope seed --recreate
uv run python scripts/eval_legal_retrieval.py
```

The seed scope indexes the public official source pack, local rule/source notes, and curated work-permit MIG cases. Use `--mig-scope work` or `--mig-scope all` only when intentionally spending more provider credits on embeddings.

Legal retrieval endpoints:

```text
GET  /legal/collection
POST /legal/search
POST /legal/citation-bundle
```

Permit route catalog:

```powershell
uv run python scripts/eval_permit_routes.py
```

Permit route endpoints:

```text
GET  /permits/routes
GET  /permits/routes/{route_id}
POST /permits/match
```

The route catalog covers broad Swedish migration-consulting intake: visiting, work, temporary work, study, family, permanent/long-term, EU/Swiss/British, protection, citizenship, and appeals. `/permits/match` returns candidate routes, readiness score, missing facts, missing evidence, risk flags, and official source links for the AI consultation workspace.

Matter workspace endpoints:

```text
GET  /sessions
POST /sessions
PATCH /sessions/{session_id}
POST /sessions/{session_id}/messages
GET  /matters
POST /matters
GET  /matters/{matter_number}/workspace
POST /matters/{matter_number}/document-request
POST /matters/{matter_number}/documents
POST /matters/{matter_number}/agent-room/run-demo
POST /matters/{matter_number}/review/approve
```

The private session/matter endpoints require a Supabase bearer token. The default
fictional matter is `LX-MIG-2026-001` and remains available for local workspace
smoke tests. Real user matters are linked to `auth.users.id`, consultation
sessions, persisted chat messages, and RLS ownership policies.

These endpoints back the React Evidence Readiness Workspace: document-request
generation, private Storage upload, evidence status updates, RAG/source
attachment, agent-room demo sequence, packet assembly, and AI packet approval.

Matter workspace smoke test:

```powershell
uv run python scripts/eval_matter_workspace.py
```

Private local PDF analysis:

```powershell
uv run python scripts/analyze_private_pdf.py --glob "<local-private-pdf-glob>"
```

This prints structural JSON only by default. It does not save raw extracted text. Use `--include-redacted-snippets` only for local debugging.

## Secret Rules

- Do not commit `.env.local`.
- Do not commit private local PDFs or raw extracted text.
- Do not expose Supabase service-role keys to the browser.
- Use only the Supabase publishable key in Vite/browser code.
- Do not store real client documents in the demo.
- Rotate any hackathon keys after the event.
