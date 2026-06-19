# Submission Plan

## Project Title

LexNordic Migration Board

## Short Description

A Band-coordinated Swedish migration-law workspace, born from foreign-student
visa stress, where pixel agents turn an applicant question into route screening,
evidence tasks, legal sources, risk flags, and an AI case packet.

## Long Description Draft

LexNordic Migration Board is a hackathon-grade AI migration consultation workspace
for Swedish permit questions. A user arrives with a visa, permit, or appeal
question; the platform identifies the likely route, opens a private matter,
requests missing evidence, retrieves official legal sources, and coordinates
specialized agents through Band. The demo makes Band visible through `Band Ops
Theater`: pixel agents carry a case-file baton from intake to evidence, legal
sources, risk, and final packet assembly while the right rail shows room metrics,
handoff count, source count, and the structured payload moving through the room.

The product story comes from lived experience: as a foreign student, the founder
and friends struggled to understand visa rules, changing requirements, documents,
deadlines, and where to get reliable support. LexNordic is designed to reduce
that first layer of confusion by giving a user a private, source-grounded place
to ask, prepare, and understand next actions.

The agent roles are LexNordic Intake, Conflict KYC, Decision Parser, Evidence,
Legal Source, Risk, Appeal Packet, and Partner Review. They are configured as
Band remote agents and can run through the provider-backed Band SDK runner. AI/ML
API is used for legal synthesis and drafting-style work, Featherless is used for
extraction/classification/risk-precheck roles, Supabase stores matter state and
private documents, and Qdrant powers legal retrieval over official sources, the
June 2026 rule overlay, and seed MIG case-law chunks.

## Category Tags

Multi-agent systems, legal tech, migration law, Band, Supabase, Qdrant, RAG,
AI/ML API, Featherless, pixel agents, agent coordination.

## Required Assets

- Public GitHub repository with secrets removed.
- Demo URL or local demo recording.
- 2-3 minute video showing chat intake, Band Ops Theater, and AI packet assembly.
- Slide deck explaining workflow, architecture, Band coordination, and business value.
- Cover image or product screenshot.

## Video Beats

1. Founder hook: foreign-student visa stress, confusing rules, scattered documents, and unclear support.
2. The workspace: chat-first consultation, route context, evidence matrix, legal-source panel, and AI packet target.
3. The applicant action: live chat checks, document requests, and fictional evidence upload.
4. The Band coordination: pixel agents pass the case baton through Band and update proof metrics.
5. The product boundary: the system saves an AI case packet and does not trigger authority filing automatically.
6. The business value: scalable consulting intake for work, study, family, visit, appeal, permanent residence, citizenship, protection, and EU-related routes.
