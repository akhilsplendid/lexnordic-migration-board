# LexNordic Migration Board

Swedish migration-law consultation platform built for the Band of Agents Hackathon.

LexNordic Migration Board is a chat-first migration-law workspace where users describe their situation in natural language, receive route screening, collect required evidence, and let an AI firm assemble a source-backed case packet for private consultation.

The original scaffold was named Band Change Board. The active product direction is now LexNordic Migration Board.

## Why This Fits The Hackathon

- Uses Band as the shared coordination layer between specialized agents.
- Uses specialized legal-workflow roles: Intake, Conflict/KYC, Decision Parser, Evidence, Legal Source, Risk, Appeal Packet, and Partner Review.
- Keeps the user chat answer-first while preserving Band collaboration proof through expandable traces and dedicated proof pages.
- Targets an enterprise legal workflow with audit, source citations, review, traceability, escalation, and decision-making.

## Approved Stack

```text
Frontend:        React + Vite + TypeScript
Backend API:     Python FastAPI
Matter backend:  Supabase Postgres + Auth + Storage + Realtime
Legal retrieval: Qdrant
Agent layer:     Band Pro + Band SDK remote agents
Model layer:     AI/ML API + Featherless AI
```

See `docs/architecture/approved-stack.md`.

## Local Development

Start the backend:

```powershell
cd server
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the frontend:

```powershell
npm install
npm run dev
```

Then open [http://127.0.0.1:5173](http://127.0.0.1:5173).

Dedicated frontend pages:

- [Chat](http://127.0.0.1:5173/#/chat)
- [Matter](http://127.0.0.1:5173/#/matter)
- [Route](http://127.0.0.1:5173/#/route)
- [Evidence](http://127.0.0.1:5173/#/evidence)
- [Agents](http://127.0.0.1:5173/#/agents)
- [Theater](http://127.0.0.1:5173/#/theater)
- [Packet](http://127.0.0.1:5173/#/review)

The default product route is `/#/chat`. Supabase Auth is required before the
private workspace opens. After sign-in, the user can start multiple consultation
sessions from the left rail; sessions and chat messages are persisted in
Postgres, and each consultation can create its own Supabase-backed matter
through `POST /matters`. Uploaded documents are stored under that matter's
private Storage prefix and do not appear in other sessions.

The seeded matter (`LX-MIG-2026-001`) remains as a local development fallback
and reset target. Real user matters use `matters.user_id`, persisted
`consultation_sessions`, persisted `chat_messages`, bearer-token API calls, and
user-owned RLS policies.

Frontend code is split into API clients, hooks, pages, fallback data,
utilities, and components under `src/`. `src/App.tsx` is only the
orchestration layer.

Completed frontend pages and product areas:

- Chat-first consultation entry with free-form conversation, collapsed proof traces, route screening, and case-builder panel.
- Supabase Auth gate with sign-in/sign-up and server-verified access tokens.
- Multi-session consultation rail with persisted chat history, matter creation,
  per-matter document isolation, and user-owned RLS.
- `POST /sessions/{session_id}/chat/stream` streams live consultation checks, then persists the same answer and trace shape as `POST /sessions/{session_id}/chat` for on-demand proof.
- Matter page with cockpit, applicant brief, document center, and AI packet readiness.
- Route page with permit precheck across the 46-route catalog.
- Evidence page with document center, evidence workbench, source trail, and extraction status.
- Agents page with Band agent room, extraction feed, and review-packet assembly.
- Theater page with pixel-agent Band choreography, context-baton animation, handoff ladder, and judge-proof metrics.
- Packet page with source-backed case strategy, document context, and final packet action.
- Shared app shell with route-aware rail navigation, stage navigation, notification/profile drawers, and action feedback toasts.

## Build Check

```powershell
npm run build
```

## Backend Configuration

```powershell
copy .env.example .env.local
cd server
uv sync
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The `.env.local` file is ignored by git and should hold Qdrant, Supabase, Band, AI/ML API, and Featherless credentials.
The browser uses only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY`;
the Supabase service-role key must remain server-only.

See `docs/architecture/runtime-configuration.md`.

## Live Band Agent Path

The `agents/` folder now contains provider-backed Band SDK runners. They do not
use the old Codex adapter scaffold.

Connection flow:

1. In Band, create one remote agent per role.
2. Copy each agent UUID and API key once.
3. Copy `agents/agent_config.example.yaml` to `agents/agent_config.yaml`.
4. Fill in the credentials locally. Do not commit that file.
5. Optionally set `AIML_CHAT_MODEL` and `FEATHERLESS_CHAT_MODEL`.
6. Run each provider-backed agent process.

Dry-run example:

```powershell
cd agents
uv sync
uv run python run_band_agent.py --role evidence --dry-run
```

The current repo intentionally does not contain Band API keys or model provider API keys.

## Submission Assets

- Product demo video: `docs/submission/video/lexnordic-product-demo.mp4`
- Cover image: `docs/submission/assets/lexnordic-cover-higgsfield.png`
- Slide deck: `docs/submission/deck/lexnordic-band-of-agents-submission-redone.pptx`
- Ready-to-paste submission copy: `docs/submission/submission-form-copy.md`

The demo can run locally with the frontend and backend commands above. A hosted
public demo is optional for the hackathon submission because the repository
requires private provider credentials for Supabase, Qdrant, Band, AI/ML API,
and Featherless.
