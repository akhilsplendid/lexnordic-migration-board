# Migration Corpus Inventory

Purpose: describe the local migration-law corpus added for LexNordic Migration Board and define how agents may use it.

This document is not legal advice. It is a build-time inventory for a hackathon prototype that prepares AI consultation packets.

## Local Corpus

Path: configured locally with `MIG_CORPUS_PATH`.

Observed on 2026-06-12:

- 482 MIG records covering 2006-2025.
- 314 legacy records from `lagen.nu via r.jina.ai`.
- 168 Domstol page records.
- 481 records with `text_path` in `master_index.json`.
- 167 records with `pdf_path` in `master_index.json`.
- Top-level indexes: `summary.json`, `master_index.json`, `master_index.csv`, `index.json`, `index.csv`, `sitemap.xml`.
- Content folders: `legacy_lagennu`, `pages`, `pdfs`, `texts`.

The corpus appears to combine older legacy lagen.nu case texts with newer official Domstol pages/PDF-derived texts. Treat it as a case-law corpus, not as an official current-process checklist.

## Source Role

Use this corpus for:

- precedent discovery,
- identifying legal reasoning patterns,
- finding similar facts,
- building source-grounded case-packet citations,
- testing retrieval over Swedish migration-law cases.

Do not use this corpus alone for:

- appeal deadlines,
- current Migrationsverket process instructions,
- current application requirements,
- filing instructions,
- user-facing legal conclusions.

Current agency pages, statutes, and the decision letter remain controlling for process and deadlines.

## Data Caveats

- Index files may contain stale absolute paths; ingestion must normalize them to the configured `MIG_CORPUS_PATH`.
- Some PDF-extracted text has character-encoding artifacts. Retrieval should keep links to PDF/page originals so a reviewer can verify the original text.
- `master_index.json` reports one record without `text_path` and one fewer `pdf_path` than Domstol page records. Ingestion should log missing files instead of failing silently.
- Case-law relevance must be filtered by permit type, date, legal issue, and whether the law has changed since the decision.
- No private client facts should be added to this corpus.

## MVP Seed Cases

For the rejected work-permit appeal demo, start with a small curated seed set:

- `MIG 2017:2`: work permit as prerequisite for work in Sweden; Union preference and job-advertising timing.
- `MIG 2017:16`: work-permit conditions where a return-ban issue intersects with work-permit eligibility.
- `MIG 2017:18`: special reasons for extending a work permit beyond four years.
- `MIG 2017:24`: holistic assessment of employment conditions for permanent residence after work permits.
- `MIG 2017:25`: holistic assessment where wages were below collective-agreement level for part of an earlier permit period.
- `MIG 2025:1`: good-support requirement for work permits; whether recurring compensation beyond base salary can count and whether a forward-looking assessment can use a longer period than month-by-month.

These are seed cases only. The Legal Source agent must retrieve and cite the relevant source chunks before using any case in an appeal packet.

## Retrieval Design

Chunking:

- Split by case, then by headings such as summary, facts, legal regulation, court reasoning, and outcome when available.
- Preserve page numbers for PDF-derived texts.
- Keep short sentence windows around matched legal propositions.

Metadata:

- `mig_id`
- `year`
- `source_family`: `domstol` or `lagen_nu_legacy`
- `source_url` / `page_url`
- `pdf_path`
- `text_path`
- `decision_date`
- `permit_type`
- `legal_issue`
- `risk_flags`
- `encoding_quality`

Retrieval baseline:

- Use keyword search first for Swedish legal terms and case identifiers.
- Add dense retrieval only after the seed set is manually checked.
- Apply metadata filters for work-permit matters before reranking.
- Require source snippets in agent output, never unsupported summaries.

## Agent Rules

- Legal Source agent may surface case-law candidates, not final legal conclusions.
- Risk agent must flag old cases where statutes or Migrationsverket requirements may have changed.
- Appeal Packet agent must label precedent sections as source-grounded background, not guaranteed outcomes.
- Partner Review agent must verify any cited case against the original page/PDF before demo submission.
