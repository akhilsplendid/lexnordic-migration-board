# Permit Route Catalog

Purpose: define the broad Swedish migration-consulting route coverage for LexNordic.

Last checked: 2026-06-13

This is not legal advice. It is a product route map and readiness framework for a consulting/workflow platform.

## Product Position

LexNordic should support every major route family now, while route depth can improve over time.

Core output:

- route discovery,
- required facts,
- required evidence,
- deadline/risk flags,
- official source bundle,
- readiness packet for the AI consultation workspace.

The system may prepare packets autonomously. It must not submit applications, sign forms, or promise outcome.

## Implemented Route Families

Implemented in `server/app/permits/catalog.py`.

- Visiting Sweden: Schengen visa up to 90 days, visitor residence permit over 90 days.
- Work: employee, self-employed, former student who found work, EU Blue Card, ICT, researcher, athlete/coach, artist/tour staff, seafarer, apply after visiting employer.
- Work family: family of employee/self-employed/researcher/ICT/EU Blue Card holder.
- Temporary work: au pair, seasonal worker, berry picker, volunteer, working holiday, traineeship/internship, self-employed temporary assignment, temporary work contracting.
- Study: higher education, higher education extension, doctoral studies, mobility studies, contract/specialisation education, other/upper-secondary studies, post-study look-for-work, student family.
- Family: partner/child/parent/relative, child residence, other ties to Sweden.
- Permanent / long-term: permanent residence, long-term resident status in Sweden, long-term resident in another EU country, family of long-term resident in another EU country.
- EU/EEA / Swiss / British: right of residence information path, Swiss citizen residence, British residence-status route.
- Protection: asylum/international protection, Temporary Protection Directive, alien passport/travel document.
- Citizenship: adult citizenship, child citizenship, Nordic citizen notification.
- Appeal: appeal/rejection route.

## API

```text
GET  /permits/routes
GET  /permits/routes/{route_id}
POST /permits/match
```

`POST /permits/match` accepts a natural-language goal plus optional facts and document keys. It returns candidate routes, readiness score, missing facts, missing evidence, risk flags, and source bundle.

## Official Source Anchors

- Migrationsverket apply overview: https://www.migrationsverket.se/en/you-want-to-apply.html
- Migrationsverket extend overview: https://www.migrationsverket.se/en/you-want-to-extend.html
- Visiting Sweden: https://www.migrationsverket.se/en/you-want-to-apply/visiting-sweden.html
- Work overview: https://www.migrationsverket.se/en/you-want-to-apply/work.html
- Employee/self-employed overview: https://www.migrationsverket.se/en/you-want-to-apply/work/employee-or-self-employed.html
- Temporary work overview: https://www.migrationsverket.se/en/you-want-to-apply/work/temporary-work-in-sweden.html
- Study overview: https://www.migrationsverket.se/en/you-want-to-apply/study.html
- Live with someone: https://www.migrationsverket.se/en/you-want-to-apply/live-with-someone.html
- Permanent residence: https://www.migrationsverket.se/en/you-want-to-apply/permanent-residence-permit.html
- Swedish citizenship: https://www.migrationsverket.se/en/you-want-to-apply/swedish-citizenship.html
- Long-term residents in Sweden: https://www.migrationsverket.se/en/you-want-to-apply/long-term-residents-in-sweden.html
- Long-term residents in another EU country: https://www.migrationsverket.se/en/you-want-to-apply/long-term-residents-in-another-eu-country.html
- Appeal a decision: https://www.migrationsverket.se/en/word-explanations/appeal-a-decision.html

## Agent Use

- Intake Agent calls `/permits/match` from the user's goal.
- Eligibility Agent checks required facts.
- Evidence Agent turns missing evidence into document tasks.
- Legal Source Agent uses source bundle plus `/legal/search`.
- Risk Agent handles expiry, removal, asylum/protection, children, and court-stage flags.
- Packet Agent creates application/consultation packet.
- Partner Review Agent gates the packet before user-facing consultation output.
