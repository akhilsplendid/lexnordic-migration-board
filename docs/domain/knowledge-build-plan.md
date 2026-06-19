# Knowledge Build Plan

Purpose: staged plan for building the legal knowledge layer before product expansion.

## Stage 1: Manual Source Pack

Create a small curated source pack for one demo matter:

- Migrationsverket appeal page.
- Migrationsverket work rejection page.
- Migrationsverket work permit employee page.
- June 2026 rule-change snapshot.
- Swedish Bar confidentiality / conflict / AML sources.
- Aliens Act overview and translation.

Store:

- URL,
- title,
- source type,
- jurisdiction,
- last checked date,
- relevant workflow stage,
- risk level.

## Stage 1.5: Local MIG Case-Law Corpus

Register the local corpus without copying it into the repo:

- path: configured locally with `MIG_CORPUS_PATH`,
- inventory: `docs/domain/migration-corpus-inventory.md`,
- corpus type: Swedish migration case law / MIG precedents,
- observed coverage: 482 records, 2006-2025,
- first seed set: work-permit cases listed in the inventory.

Normalize stale absolute paths during ingestion so public files never depend on a developer-specific Downloads directory.

Use this corpus only after the official source pack exists. The case-law layer explains reasoning and precedent; it does not define current agency process or exact deadlines.

## Stage 1.6: Current Rules Overlay

Add `docs/domain/recent-rule-changes-2026-06.md` as a required overlay before any work-permit reasoning.

Minimum rule checks for the MVP:

- Is the decision on or after 1 June 2026?
- Is this a first-time work permit or an extension?
- If extension, was the current permit granted before 1 June 2026 and is the extension application between 1 June and 1 December 2026?
- Does the occupation fall under a 75 percent salary-threshold exemption?
- Is the occupation excluded from normal work-permit eligibility?
- Does the case involve seasonal work, ICT, EU Blue Card, study-permit switch, Temporary Protection Directive, asylum, track change, return, or re-entry-ban facts?

The Risk agent blocks autonomous completion if asylum, track-change, return, detention, re-entry-ban, or Temporary Protection Directive facts appear.

## Stage 1.7: Secondary EU-Law Context

Register private secondary EU-law commentary without copying it into the repo:

- path: configured locally with `EU_MIGRATION_LAW_BOOK_PATH`,
- inventory: `docs/domain/eu-migration-law-secondary-source.md`,
- source type: secondary legal commentary,
- observed pages: 721,
- role: EU-law framing and research-question generation.

Use this only after official Swedish/EU sources and case law. Do not commit extracted text or chunks from the book. Public demo output should not reproduce book content.

## Stage 2: Structured Fixtures

Create fictional, non-sensitive documents:

- rejection decision summary,
- applicant timeline,
- employer letter,
- employment contract summary,
- missing evidence list.

The prototype should never need real personal data.

## Stage 3: Retrieval Baseline

Build a small RAG baseline:

- semantic chunks by page/section,
- case-law chunks by MIG id, heading, page, and issue,
- secondary commentary chunks only if kept in a private local index outside git,
- keyword metadata filters by permit type,
- source citations in every answer,
- top-k retrieval logs visible in developer mode.

Minimum eval questions:

- "Where do appeals go first?"
- "What facts must be read from the decision letter?"
- "Which evidence is usually needed for this work-permit appeal packet?"
- "Which facts should be flagged as sensitivity or readiness risks?"
- "Which MIG cases are potentially relevant to a work-permit income or employment-condition issue, and why?"
- "Does the 1 June 2026 salary-rule change affect this fictional work-permit rejection?"
- "Is this occupation under the 90 percent threshold, 75 percent exemption, or excluded list?"

## Stage 4: Agent Room Integration

Each Band agent receives only the source pack relevant to its role:

- Intake: matter workflow and intake fields.
- Decision Parser: decision fields and extraction schema.
- Evidence: permit requirements and evidence matrix schema.
- Legal Source: official source map, local case-law inventory, and retrieval tool.
- Risk: legal-advice boundaries and sensitivity gates.
- Partner Review: final memo template.

## Stage 5: Judge Demo

The demo should show:

1. A fictional rejection decision enters the Band matter room.
2. Agents hand off work through Band.
3. Source citations and evidence gaps are visible.
4. Risk agent blocks unsafe claims.
5. Partner Review produces a source-grounded AI case packet.

## Evaluation Criteria

- Groundedness: every legal/process claim has a source.
- Completeness: required packet sections are present.
- Safety: sensitive facts trigger explicit risk flags and product-boundary language.
- Band usage: handoffs and shared context are visible in room transcript.
- Partner-tool usage: AI/ML API and Featherless perform distinct visible jobs.
