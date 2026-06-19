# LexNordic Narrated Demo Script

Target length: 2 to 3 minutes.

## 0:00-0:20 - Founder Hook

I built LexNordic from a problem I lived. As a foreign student, I and many friends faced the same stress: visa rules were hard to understand, requirements changed, documents were scattered, and it was not clear where to get reliable support before a mistake became serious.

LexNordic Migration Board turns that confusion into a private AI consultation workspace for Swedish migration questions.

## 0:20-0:45 - Product Entry

The user starts like they would in ChatGPT or Claude: by asking a normal question. They do not need to know whether this is a work permit, study route, extension, appeal, or family case. The platform creates a user-owned consultation session, keeps the chat thread, and starts screening the situation.

While the answer is being prepared, the user sees simple live checks: route, documents, sources, risks, and packet. The full Band trace is still available for judges, but normal users are not forced to understand agent internals.

## 0:45-1:15 - Case Builder

The consultation becomes a structured matter. LexNordic shows likely permit routes, missing facts, required evidence, and source references. The user can upload fictional test evidence in the demo; in a real product, this becomes their private document vault.

The important point is that the user gets a next action, not just a paragraph.

## 1:15-1:55 - Band Coordination

This is the hackathon proof point. Band is the coordination layer. Intake, Conflict KYC, Decision Parser, Legal Source, Evidence, Risk, Appeal Packet, and Partner Review each have a role in the same room.

The Band Ops Theater makes that visible. Pixel agents pass a case-file baton, the handoff ladder moves, the proof panel shows source references and readiness, and judges can expand the full Band trace behind the user-friendly answer.

## 1:55-2:25 - AI Case Packet

The output is an AI consultation packet: route summary, evidence checklist, risk flags, source trail, and next actions. The boundary is explicit: LexNordic does not file automatically with an authority. It prepares a source-grounded packet that a user can understand and continue from.

## 2:25-2:50 - Stack

The stack is React and FastAPI for the product, Supabase for auth, user-owned sessions, matters, chat threads, and private storage, Qdrant for legal retrieval, Band for agent coordination, AI/ML API for synthesis and drafting, and Featherless for extraction, classification, and checking.

## 2:50-3:00 - Close

The bigger vision is a migration consulting platform for people who are stressed before the legal process even begins: work, study, family, visit, EU residence, permanent residence, citizenship, protection screening, appeals, and extensions.
