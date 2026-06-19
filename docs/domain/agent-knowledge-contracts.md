# Agent Knowledge Contracts

Purpose: define what each Band agent may know, retrieve, produce, and hand off.

## Shared Ground Rules

- Use Band as the coordination room.
- Cite source URLs or uploaded document IDs.
- Separate facts from interpretation.
- Label uncertainty and missing evidence.
- Do not provide final legal advice.
- Do not file, submit, sign, email, or contact authorities.
- Flag sensitive cases with explicit risk and product-boundary language.

## Intake Agent

Job:

- Convert inquiry into a matter card.
- Identify permit type, deadline, client role, and urgent flags.

Inputs:

- user intake text,
- uploaded decision letter metadata,
- applicant/employer/family context.

Outputs:

- matter summary,
- missing intake questions,
- sensitivity flags,
- handoff to Decision Parser and Conflict/KYC Agent.

Stop condition:

- matter card is complete enough for triage or flagged as impossible without more user facts.

## Conflict / KYC Agent

Job:

- Prepare firm-facing conflict and authority checklist.

Inputs:

- applicant identity,
- employer/sponsor identity,
- representative details,
- parties named in documents.

Outputs:

- conflict-check packet,
- KYC/authority missing items,
- "do not proceed" flag if identity/authority is unclear.

Stop condition:

- the platform can approve, block, or request more user data.

## Decision Parser Agent

Job:

- Extract structured data from decision/rejection documents.

Inputs:

- decision letter,
- appendix,
- translation if available.

Outputs:

- decision date,
- receipt date if known,
- appeal instructions,
- case number,
- rejection grounds,
- cited requirements,
- authority/court routing notes.

Stop condition:

- every extracted claim has a document reference or is marked unknown.

## Evidence Agent

Job:

- Map evidence against the permit category and rejection grounds.

Inputs:

- decision parser output,
- uploaded evidence,
- Migrationsverket requirement pages.

Outputs:

- evidence matrix,
- missing evidence checklist,
- questions for client/employer/sponsor.

Stop condition:

- missing-evidence list is ready for user-facing document requests.

## Legal Source Agent

Job:

- Retrieve and summarize official legal/process sources.

Inputs:

- permit category,
- rejection grounds,
- source map.

Outputs:

- source bundle,
- cited process summary,
- "source confidence" note.

Stop condition:

- sources are sufficient for an AI consultation packet or gaps are explicit.

## Risk & Sensitivity Agent

Job:

- Challenge the packet before drafting.

Inputs:

- intake summary,
- decision parser output,
- evidence matrix,
- legal sources.

Outputs:

- sensitivity flags,
- unsupported-claim list,
- deadline risk,
- legal-advice boundary warnings.

Stop condition:

- final risk gate is posted to Band.

## Appeal Packet Agent

Job:

- Prepare an AI consultation packet, not a submittable final appeal.

Inputs:

- all prior agent outputs.

Outputs:

- draft route or appeal outline,
- factual timeline,
- argument candidates,
- evidence exhibits list,
- unresolved user questions.

Stop condition:

- packet is ready for Partner Review.

## Partner Review Agent

Job:

- Synthesize final AI consultation packet state.

Inputs:

- complete matter packet,
- risk gate,
- source bundle.

Outputs:

- proceed / blocked / urgent / high-sensitivity status,
- final memo,
- next action checklist,
- final user action checklist.

Stop condition:

- final memo is posted and no autonomous external action remains.
