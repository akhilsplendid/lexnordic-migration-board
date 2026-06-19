# Swedish Migration Source Map

Purpose: authoritative source inventory for LexNordic Migration Board.

This document is not legal advice. It is a build-time source map for a hackathon prototype that prepares AI consultation packets.

## Source Priority

1. Swedish Migration Agency / Migrationsverket official pages.
2. Swedish statutes and government legal material.
3. Swedish courts, official appeal-process material, and curated MIG case law.
4. Swedish Bar Association ethics and confidentiality guidance.
5. Secondary legal/commentary/practice sources for workflow and EU-law context only.

## Core Official Sources

### Migrationsverket: Main Entry Points

- Apply for a permit to be in Sweden: https://www.migrationsverket.se/en/you-want-to-apply.html
- After a decision has been made: https://www.migrationsverket.se/en/you-have-received-a-decision.html
- Appeal a decision: https://www.migrationsverket.se/en/word-explanations/appeal-a-decision.html
- Recent rule changes, June 2026: `docs/domain/recent-rule-changes-2026-06.md`

Use for:

- application categories,
- appeal routing,
- decision-aftercare,
- deadline warnings,
- applicant-facing requirements,
- freshness checks when rules changed after a cited case.

### Rejection / Appeal Pages For MVP-Safe Cases

- Work rejection: https://www.migrationsverket.se/en/you-have-received-a-decision/work/your-application-has-been-rejected.html
- Study rejection: https://www.migrationsverket.se/en/you-have-received-a-decision/study/your-application-has-been-rejected.html
- Live-with-someone rejection: https://www.migrationsverket.se/en/you-have-received-a-decision/live-with-someone/your-application-has-been-rejected.html

Use for:

- first-pass appeal eligibility language,
- reminder that decision-specific appeal instructions control,
- product copy around court review.

### Permit Requirement Pages For MVP-Safe Cases

- Work permit for employees: https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed/employees.html
- Residence permit for higher education studies: https://www.migrationsverket.se/en/you-want-to-apply/study/higher-education.html
- Live with a partner: https://www.migrationsverket.se/en/you-want-to-apply/live-with-someone/live-with-a-partner-child-or-other-relative/live-with-a-partner.html
- Permanent residence permit: https://www.migrationsverket.se/en/you-want-to-apply/permanent-residence-permit.html
- Maintenance requirement: https://www.migrationsverket.se/en/word-explanations/maintenance-requirement-for-the-person-in-sweden.html

Use for:

- requirement extraction,
- evidence checklists,
- missing-document analysis,
- controlled user-facing summaries.

### Sensitive / Future Scope

- Asylum rejection: https://www.migrationsverket.se/en/you-have-received-a-decision/asylum/your-application-has-been-rejected.html
- Family reunification after protection decision: https://www.migrationsverket.se/en/you-have-received-a-decision/asylum/family-reunification.html

Use only for:

- product roadmap and safe escalation patterns.

Do not use asylum as the hackathon MVP demo unless a high-sensitivity scenario is explicitly shaped.

### Statutory / Legal System Sources

- Aliens Act overview: https://www.government.se/government-policy/migration-and-asylum/aliens-act/
- Aliens Act PDF translation: https://www.government.se/contentassets/784b3d7be3a54a0185f284bbb2683055/aliens-act-2005_716.pdf
- Swedish Code of Statutes: https://svenskforfattningssamling.se/english.html

Use for:

- legal-source citations,
- source hierarchy,
- statutory grounding.

The official authentic statute versions are in Swedish. English translations are useful for demo comprehension but must not be treated as controlling if they diverge from official Swedish text.

### Local Case-Law Corpus

- Local path: configured with `MIG_CORPUS_PATH`
- Inventory: `docs/domain/migration-corpus-inventory.md`

Use for:

- precedent discovery,
- legal-reasoning patterns,
- similar-fact comparison,
- source-grounded case-packet citation candidates.

Do not use for:

- current process instructions,
- exact appeal deadlines,
- current Migrationsverket requirement values,
- direct user-facing legal conclusions.

The case-law corpus supports the Legal Source agent. It does not replace Migrationsverket pages, statutes, the decision letter, or explicit product-boundary language.

### Secondary EU-Law Commentary

- Local source note: `docs/domain/eu-migration-law-secondary-source.md`
- Local file: configured privately with `EU_MIGRATION_LAW_BOOK_PATH`

Use for:

- EU-law conceptual background,
- Common European Asylum System context,
- legal migration / return / border-control framing,
- research-question generation for the Legal Source agent.

Do not use for:

- current Swedish work-permit thresholds,
- appeal deadlines,
- final legal conclusions,
- public-demo content copied from the book.

This is a private secondary commentary source. It must be down-ranked below official legal sources, case law, and the June 2026 current-rules overlay.

### Law-Firm Ethics / Professional Controls

- Swedish Bar Association Code of Conduct: https://www.advokatsamfundet.com/rules-and-regulations/code-of-conduct/
- Code PDF: https://www.advokatsamfundet.com/globalassets/advokatsamfundet_eng/code-of-professional-conduct-swedish-bar-association-2024.pdf
- AML guidance PDF: https://www.advokatsamfundet.se/globalassets/advokatsamfundet_eng/vagledning_penningtvattsregleringen_version_2-advb1-8.pdf

Use for:

- confidentiality gate,
- prospective-client caution,
- conflict/KYC checks,
- legal-advice boundary,
- no direct filing/submission by agents.

## MVP Source Bundle

The first source bundle should support one demo matter:

> Swedish work-permit question for a fictional applicant who wants a source-grounded AI case packet.

Bundle:

1. Appeal a decision.
2. Work rejection.
3. Work permit employees.
4. Permanent residence permit only if the fictional rejection involves extension/permanent-residence facts.
5. Swedish Bar confidentiality / conflict / AML sources.
6. Aliens Act overview and PDF translation for legal-system grounding.
7. Curated work-permit MIG seed cases from the local corpus, starting with `MIG 2017:2`, `MIG 2017:16`, `MIG 2017:18`, `MIG 2017:24`, `MIG 2017:25`, and `MIG 2025:1`.
8. June 2026 rule-change snapshot for salary thresholds, exemptions, excluded occupations, study/research changes, the EU Migration and Asylum Pact, and track-change risk.
9. Secondary EU-law commentary source note for background only.

## Source Rules For Agents

- Cite every legal/process claim to a source URL or uploaded source chunk.
- Prefer "the decision letter controls the exact deadline" over generic deadline claims.
- Never say an appeal will succeed.
- Never instruct a user to ignore a removal/return instruction.
- Never submit, sign, or file anything.
- Mark uncertainty explicitly.
- Check the dated rule-change snapshot before using older case law.
- Down-rank secondary commentary below official sources and case law.
- Flag asylum, child, detention, deportation, violence, trafficking, statelessness, or immediate-removal facts as high-sensitivity risks.
