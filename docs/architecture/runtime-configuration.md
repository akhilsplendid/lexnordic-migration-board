# Runtime Configuration

Purpose: define how LexNordic Migration Board stores and uses provider credentials.

Last updated: 2026-06-13

## Local Files

Committed:

- `.env.example`
- `server/app/settings.py`
- `server/app/clients/embeddings.py`
- `server/app/clients/qdrant.py`
- `server/app/clients/supabase.py`
- `server/app/clients/postgres.py`
- `server/app/clients/model_router.py`
- `server/app/legal/source_documents.py`
- `server/app/legal/retrieval.py`
- `server/app/routes/legal.py`
- `server/app/routes/matters.py`
- `server/app/matters/workspace.py`
- `server/scripts/check_connections.py`
- `server/scripts/setup_supabase.py`
- `server/scripts/ingest_legal_sources.py`
- `server/scripts/eval_legal_retrieval.py`
- `server/scripts/eval_matter_workspace.py`
- `server/database/migrations/001_initial_schema.sql`
- `server/database/migrations/002_auth_sessions_rls.sql`

Ignored:

- `.env`
- `.env.*`
- `agents/agent_config.yaml`

Use `.env.local` for local secrets.

## Qdrant

Configured field names:

```text
QDRANT_URL
QDRANT_API_KEY
QDRANT_COLLECTION_LEGAL_SOURCES
LEGAL_EMBEDDING_MODEL
LEGAL_EMBEDDING_DIMENSION
LEGAL_EMBEDDING_MAX_CHARS
LEGAL_RETRIEVAL_DEFAULT_LIMIT
```

Current cluster URL is set in `.env.example`; the API key must stay in `.env.local`.
Qdrant credentials are provider-specific and must not be reused for AI/ML API,
Featherless, Band, or Supabase.

Verified on 2026-06-13:

- Qdrant endpoint is reachable with the key from `.env.local`.
- Legal source collection `lexnordic_legal_sources` exists with 394 seed chunks.
- Payload indexes exist for `source_type`, `permit_type`, `mig_id`, `legal_issue`, `workflow_stage`, `source_id`, and `year`.
- `GET /legal/collection`, `POST /legal/search`, and `POST /legal/citation-bundle` return 200 in local FastAPI tests.
- `uv run python scripts/eval_legal_retrieval.py` returns the expected source families for appeal route, June 2026 salary rules, work-permit MIG cases, and sensitivity/risk queries.

Use Qdrant for:

- legal source chunks,
- current-rule chunks,
- MIG case-law chunks,
- source metadata filters,
- citation-bundle retrieval.

Current seed source mix:

- Public official pages fetched at ingestion time from Migrationsverket, Government Offices of Sweden, and Swedish Bar Association.
- Local current-rule overlay `docs/domain/recent-rule-changes-2026-06.md`.
- Local source-map and corpus-inventory notes.
- Curated work-permit MIG seed cases: `MIG 2017:2`, `MIG 2017:16`, `MIG 2017:18`, `MIG 2017:24`, `MIG 2017:25`, and `MIG 2025:1`.
- Private secondary EU-law source note only; private PDF text is not committed or indexed in this seed.

## Supabase

Configured field names:

```text
SUPABASE_PROJECT_REF
SUPABASE_URL
SUPABASE_PUBLISHABLE_KEY
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
SUPABASE_DATABASE_URL
SUPABASE_DB_HOST
SUPABASE_DB_PORT
SUPABASE_DB_NAME
SUPABASE_DB_USER
SUPABASE_DB_SSLMODE
SUPABASE_DB_PASSWORD
SUPABASE_STORAGE_BUCKET
VITE_SUPABASE_URL
VITE_SUPABASE_PUBLISHABLE_KEY
VITE_API_BASE_URL
```

Supabase project details found through the attached dashboard tab on 2026-06-13:

```text
Project name: Migration Project
Project ref: cckykunswdzriungnapg
Project URL: https://cckykunswdzriungnapg.supabase.co
```

The publishable key and database password are stored only in ignored `.env.local`.

Database connection details confirmed on 2026-06-13:

```text
Session pooler host: aws-0-eu-west-1.pooler.supabase.com
Session pooler user: postgres.cckykunswdzriungnapg
Port: 5432
Database: postgres
SSL mode: require
```

Verified on 2026-06-13:

- Supabase project endpoint is reachable with the publishable key.
- Supabase service-role/admin access is reachable through the Storage API with the key stored in ignored `.env.local`.
- Supabase session pooler accepts Postgres connections from the local environment.
- Initial schema migration `001_initial_schema.sql` applied successfully.
- Auth/session migration `002_auth_sessions_rls.sql` applied successfully.
- Private Storage bucket `matter-documents` was created.
- Eleven public tables exist with RLS enabled: `matters`, `matter_documents`, `agent_runs`, `evidence_items`, `legal_source_refs`, `packet_versions`, `review_decisions`, `matter_deadlines`, `audit_events`, `consultation_sessions`, and `chat_messages`.
- Fictional demo matter `LX-MIG-2026-001` exists as a `work_permit_appeal`, points at the Band room, and references Qdrant collection `lexnordic_legal_sources`.
- Supabase Auth protects the browser workspace. Frontend sign-in uses only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`.
- FastAPI verifies bearer tokens against Supabase Auth before private session/matter actions.
- `matters.user_id`, `consultation_sessions.user_id`, and `chat_messages.user_id` reference `auth.users(id)`.
- RLS policies use `(select auth.uid()) = user_id` on owned rows, and child workflow tables are readable only through owner-matched matters.
- `anon` table grants were revoked for private matter/session tables; `authenticated` and `service_role` are limited to `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

The service-role key must stay server-only. Never expose it through Vite, browser bundles, `NEXT_PUBLIC_*` variables, or committed config.

Browser clients should use FastAPI endpoints for workflow actions. Direct Supabase REST access is RLS-protected and was verified with two disposable users: user one saw only their own consultation row, while user two saw zero rows.

Use Supabase for:

- matter records,
- authenticated user ownership,
- consultation sessions,
- chat messages,
- document metadata,
- private document storage,
- Band room IDs,
- agent runs,
- packet versions,
- review decisions,
- audit events,
- realtime UI updates.

## Model Providers

Configured field names:

```text
AIML_API_KEY
AIML_BASE_URL
LEGAL_EMBEDDING_MODEL
LEGAL_EMBEDDING_DIMENSION
LEGAL_EMBEDDING_MAX_CHARS
LEGAL_RETRIEVAL_DEFAULT_LIMIT
FEATHERLESS_API_KEY
FEATHERLESS_BASE_URL
AIML_CHAT_MODEL
FEATHERLESS_CHAT_MODEL
```

Routing:

- AI/ML API: legal synthesis, appeal packet drafting, partner review.
- AI/ML API embeddings: legal-source query and document embeddings with `voyage-law-2`.
- Featherless: extraction, classification, source tagging, risk prechecks.

Configured on 2026-06-13:

- `AIML_API_KEY` is stored in ignored `.env.local`.
- `FEATHERLESS_API_KEY` is stored in ignored `.env.local`.
- `LEGAL_EMBEDDING_MODEL=voyage-law-2`, `LEGAL_EMBEDDING_DIMENSION=1024`, and `LEGAL_EMBEDDING_MAX_CHARS=800`.
- The first AI/ML key generated during setup was only visible as a masked table row afterward, so a second runtime key was created and captured for local use.
- `AIML_CHAT_MODEL` and `FEATHERLESS_CHAT_MODEL` are optional. If they are unset, the Band runner returns deterministic bounded workflow output instead of failing.

## Band

Configured field names:

```text
BAND_API_BASE_URL
BAND_WS_URL
BAND_ROOM_ID
BAND_*_AGENT_ID
BAND_*_AGENT_API_KEY
```

Band credentials remain local and ignored. The old Codex adapter runner has been removed; `agents/run_band_agent.py` is the provider-backed Band SDK path.

Remote agents created on 2026-06-13:

- LexNordic Intake
- LexNordic Conflict KYC
- LexNordic Decision Parser
- LexNordic Evidence
- LexNordic Legal Source
- LexNordic Risk
- LexNordic Appeal Packet
- LexNordic Partner Review

Each agent's UUID and regenerated remote-agent API key are stored in `.env.local`. Public directory listing was turned off during configuration.

A first Band chat room was created on 2026-06-13. `BAND_ROOM_ID` is the UUID segment in the Band chat URL:

```text
https://app.band.ai/chat/<BAND_ROOM_ID>
```

The current room ID is stored in ignored `.env.local`.

Local runner verification:

```powershell
cd .\agents
uv sync
uv run python run_band_agent.py --role evidence --dry-run
uv run python run_band_agent.py --role legal_source --dry-run
uv run python run_band_agent.py --role partner_review --dry-run
```

Dry-run mode reads the FastAPI matter workspace when the backend is running and
falls back to a public-safe fixture if it is not. Live mode requires the Band agent
UUID/API key env vars and can filter events to `BAND_ROOM_ID`.

## Matter Workspace API

The React workspace uses FastAPI rather than direct browser access to Supabase.
This keeps the service-role key server-side.

```text
GET  /matters/{matter_number}/workspace
POST /matters/{matter_number}/document-request
POST /matters/{matter_number}/documents
POST /matters/{matter_number}/agent-room/run-demo
POST /matters/{matter_number}/review/approve
```

Current demo matter:

```text
LX-MIG-2026-001
```

The upload endpoint stores files in the private `matter-documents` bucket, records
document metadata in Postgres, updates evidence readiness, writes an agent run,
and returns the refreshed workspace contract.

## Browser Bridge Status

The Codex Browser Bridge relay was checked on 2026-06-13.

- Direct MCP bridge tools were not exposed by `tool_search`; only the in-app Playwright browser was exposed, and that browser showed `about:blank`.
- The local bridge relay at `127.0.0.1:45123` was then queried directly with the documented `x-bridge-token` header.
- Attached Supabase and Qdrant sessions were available through that relay.
- Qdrant tab confirmed cluster `crossbring`, cluster ID `e246fb68-6d51-4fe0-a08b-3714a7d1b873`, version `v1.18.2`, healthy free-tier status, and the configured endpoint.
- Supabase tab confirmed project name `Migration Project` and project ref `cckykunswdzriungnapg`.

## Verification

After filling `.env.local`, run:

```powershell
cd .\server
uv sync
uv run python scripts/setup_supabase.py
uv run python scripts/ingest_legal_sources.py --mig-scope seed --recreate
uv run python scripts/eval_legal_retrieval.py
uv run python scripts/eval_matter_workspace.py
uv run python scripts/check_connections.py
```

The script prints only connection status and counts. It does not print API keys.
