# Demo Script

## 30-Second Pitch

LexNordic Migration Board came from a foreign-student problem: visa rules,
document requirements, changing deadlines, and reliable support were hard to
understand, and that uncertainty created real stress before the application work
even began. LexNordic turns that moment into a Swedish migration-law AI
consultation workspace where specialized pixel agents coordinate through Band.
A messy applicant question becomes route screening, evidence gaps, legal source
references, risk flags, and an AI case packet.

## 3-Minute Walkthrough

1. Open [http://127.0.0.1:5173/#/chat](http://127.0.0.1:5173/#/chat), sign in with a prepared test account, and ask a free-form question such as `I finished higher education in Sweden and found a job offer. What can go wrong?`
2. Send the question and show the live Route/Documents/Sources/Risks/Packet checks updating while LexNordic works. After the answer appears, expand `Show how this was checked` to reveal five plain-language checks, and expand `Judge proof: full Band trace` to reveal Intake, Conflict KYC, Decision Parser, Legal Source, Evidence, Risk, Appeal Packet, and Partner Review.
3. Show route screening, next questions, source bundle, and evidence checklist beside the chat.
4. Create/open the private workspace.
5. Open [Band Ops Theater](http://127.0.0.1:5173/#/theater).
6. Click `Run Band theater` and show the case-file baton moving from Intake to Evidence, Sources, Risk, and Packet.
7. Point at the Judge Proof panel: Band room, remote agents, visible handoffs, source refs, readiness, and payload.
8. Open the Packet page and show the AI case packet updated from the Band-coordinated run.
9. Show the Band room or agent dry-runs to prove the roles map to Band remote agents and provider-backed runners.

## Judge-Facing Points

- Band is the coordination layer: each role has a remote-agent identity, room-oriented responsibility, and visible handoff in the theater.
- Supabase stores matter state, documents, packet versions, review decisions, and audit events.
- Qdrant grounds legal-source retrieval over official sources, the June 2026 rule overlay, and seed MIG cases.
- AI/ML API handles legal-source synthesis and packet/review work; Featherless handles extraction and risk/precheck-style roles.
- The UI makes the coordination visible: applicant-facing chat, pixel-agent handoffs, cited sources, proof metrics, and packet output.
- The founder story is clear: the product exists because foreign students and migrants need reliable route, evidence, and rule-change support before stress turns into avoidable mistakes.
- The product has a future business path as a migration-consulting platform across Swedish permit routes, while the hackathon demo stays fictional and public-safe.
