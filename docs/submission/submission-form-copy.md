# LexNordic Migration Board - Submission Form Copy

Use this as the ready-to-paste baseline for the lablab.ai submission form.

## Project Title

LexNordic Migration Board

## Short Description

A Band-coordinated Swedish migration-law consultation workspace, born from foreign-student visa stress, where pixel agents turn an applicant question into route screening, evidence tasks, cited legal sources, risk flags, and an AI case packet.

## Long Description

LexNordic Migration Board is an AI migration consultation platform for Swedish permit, visa, appeal, and residence questions. A user can start with a natural-language question, create a private consultation session, attach documents, and receive route screening, evidence requirements, legal source references, risk flags, and an AI-generated case packet.

The idea comes from a real founder problem: as a foreign student, I and many friends struggled to understand visa rules, document requirements, rule changes, deadlines, and where to get reliable support. The uncertainty created stress before the actual application work even started. LexNordic turns that confusing journey into a private consultation workspace where the user can ask naturally, collect evidence, see sources, and understand the next action without needing to know the legal route first.

The core hackathon story is Band coordination. The platform does not hide the multi-agent workflow behind a single chat response. It exposes a Band Ops Theater where specialized pixel agents pass a case-file baton through Intake, Route, Evidence, Legal Source, Risk, and Packet roles. The judge can see the Band room, remote agent count, handoffs, readiness state, cited sources, and structured payload moving across the room.

The implementation uses Band as the coordination layer for remote agents, Supabase for user-owned sessions, matters, chat threads, documents, and audit state, Qdrant for legal retrieval, FastAPI for the source and agent services, AI/ML API for legal synthesis and packet drafting, and Featherless AI for extraction, classification, and precheck-style roles.

LexNordic focuses on a regulated, high-stakes workflow: Swedish migration law. It is designed as a future consulting platform, not a static demo. It supports consultation flows across work permits, study permits, family reunification, visitor routes, EU-related residence routes, permanent residence, citizenship, protection/asylum-style screening, appeals, and extension cases. The product boundary is explicit: the system prepares an AI consultation packet and evidence plan, but it does not file automatically with an authority.

## Technology And Category Tags

Band, Band SDK, multi-agent systems, remote agents, legal tech, migration law, regulated workflows, Supabase, Postgres, RLS, Qdrant, RAG, FastAPI, React, TypeScript, AI/ML API, Featherless AI, document AI, source-grounded generation, pixel agents, agent coordination.

## Cover Image

`docs/submission/assets/lexnordic-cover.png`

## Slide Presentation

`docs/submission/deck/lexnordic-band-of-agents-submission-redone.pptx`

## Video Presentation

Final local video: `docs/submission/video/lexnordic-product-demo.mp4`

Public upload/link pending explicit approval. The video is a silent product walkthrough with on-screen captions. It shows the real app flow: sign-in, chat consultation, live checks, proof expansion, matter workspace, Band Ops Theater, and final AI case packet.

## Public GitHub Repository

https://github.com/akhilsplendid/lexnordic-migration-board

## Demo Application Platform

Pending explicit approval to deploy. Current verified local demo:

- Frontend: `http://127.0.0.1:5173/#/chat`
- Band Ops Theater: `http://127.0.0.1:5173/#/theater`
- Backend: `http://127.0.0.1:8000`

## Application URL

Pending explicit approval to deploy.

## Judge-Facing One-Liner

Band is not a final notification bus in LexNordic. It is the visible coordination layer that turns a Swedish migration question into a source-grounded, multi-agent consultation packet.
