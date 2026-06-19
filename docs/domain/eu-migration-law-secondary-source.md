# EU Migration Law Secondary Source

Purpose: register a private secondary EU migration-law book as background EU-law context for LexNordic Migration Board.

This document is not legal advice. It is a build-time source note for a hackathon prototype that prepares AI consultation packets.

## Private Source Registration

The source file stays outside the repository. Configure its local path with
`EU_MIGRATION_LAW_BOOK_PATH` only when running a private local ingestion.

Observed on 2026-06-12:

- Title: `European Migration Law`
- Author: Daniel Thym
- Publisher: Oxford University Press
- Series: Oxford EU Law Library
- First edition: 2023
- DOI shown in front matter: `10.1093/oso/9780192894274.001.0001`
- PDF pages: 721
- File size: 8,589,412 bytes

## Source Role

Use this book for:

- EU migration-law background,
- terminology and conceptual framing,
- understanding the relationship between EU law, national migration systems, asylum, return, borders, visas, legal migration, and integration,
- shaping the Legal Source agent's internal research questions,
- explaining why the EU Migration and Asylum Pact matters for Swedish practice.

Do not use this book for:

- current Swedish process instructions,
- current work-permit salary thresholds,
- exact appeal deadlines,
- direct advice to applicants,
- public demo snippets copied from the text,
- replacing official Swedish or EU legal sources.

For the MVP, this is a secondary commentary source. Official Migrationsverket pages, Swedish statutes, EU legal acts, court decisions, and the fictional decision letter remain higher-priority sources.

## Copyright And Repository Rules

- Do not copy the PDF into the repo.
- Do not commit extracted book text or generated chunks from the book.
- Do not quote more than short fair-use excerpts in internal notes.
- Public demo outputs should cite secondary commentary only as background, not reproduce its content.
- If the retrieval system indexes the book locally, keep that index outside the public repo and mark it as a private secondary source.

## Relevant Parts For The Product

Based on the table of contents, the most relevant chapters for our migration-law product are:

- Chapter 5: Human rights and state sovereignty.
- Chapter 6: Doctrinal foundations of the case law.
- Chapter 7: Administrative dimension.
- Chapter 9: Databases.
- Chapter 13: Common European Asylum System.
- Chapter 14: Legal migration.
- Chapter 15: Integration and settlement.
- Chapter 16: Irregular presence and return.
- Chapter 18: International cooperation with third states.

The MVP should mainly use Chapter 14 for legal-migration framing and Chapter 16 only as a risk-escalation context if return/removal facts appear.

## Agent Use

- Legal Source agent: may use the book to identify EU-law concepts and questions to check against official sources.
- Risk agent: may use the book as background for why asylum, return, detention, and border-procedure facts require escalation.
- Appeal Packet agent: should not cite this book as the primary authority for any Swedish work-permit claim.
- Partner Review agent: should verify any concept from this book against official legal sources before it appears in an AI case packet.

## Retrieval Design

If locally indexed later:

- Store metadata only in the repo.
- Keep full extracted text outside git.
- Chunk by chapter and section heading.
- Require page-level references in retrieval results.
- Label all results as `secondary_commentary`.
- Down-rank this source below official rules, statutes, court decisions, and the current-rules overlay.

## MVP Constraint

The book strengthens our understanding, but it should not expand the MVP scope. The hackathon demo remains:

> Fictional Swedish work-permit consultation, prepared as an AI case packet with cited sources and evidence-readiness flags.
