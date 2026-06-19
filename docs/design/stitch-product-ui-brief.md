# LexNordic Product UI Brief

Date: 2026-06-13

## Screen Job

The first screen must help an applicant move from a messy migration question to a clear next action:

1. ask or choose a migration goal,
2. answer lightweight facts,
3. see the likely route and readiness gaps,
4. create a secure matter,
5. follow document, agent, and review steps.

This is an operational legal-consulting workspace, not a marketing landing page.

## Primary User Flow

```text
User question
-> route goal selection
-> known-facts check
-> route readiness result
-> secure matter creation
-> document upload tasks
-> Band agent preparation
-> AI packet gate
-> final action plan
```

## UI Model

- Left: applicant communication and structured intake.
- Center: route result, readiness, missing facts, missing documents, risk callout, primary actions.
- Right: process state, trust boundary, official source bundle.
- Bottom: secure matter workspace with tabs for overview, documents, agent room, and review packet.

## Visual Direction

- Serious, calm, work-focused legal technology.
- Neutral surfaces, dark ink text, restrained teal action color, blue source accents, amber risk states, red only for high-risk states.
- Dense but readable information hierarchy.
- No marketing hero, no decorative background, no card nesting.
- Mobile stacks into one continuous application path.

## Stitch Prompt

```text
Design a production-grade web app screen for LexNordic Migration Board, a Swedish migration-law consulting platform.

The screen is not a landing page. It is the first usable product workspace for an applicant.

Build a calm legal-tech interface with:
- applicant question textarea,
- permit goal options: Work, Study, Family, Visit, Appeal, Permanent, Citizenship,
- known-facts checklist,
- route readiness result for "Work permit after higher education",
- readiness score, missing facts, missing documents, risk callout,
- primary action "Create secure matter",
- applicant process stepper,
- trust boundary notice,
- official source bundle,
- secure matter workspace with tabs: Overview, Documents, Agent room, Review packet,
- visible Band agent activity cards.

Style: serious, accessible, work-focused, compact, high trust. Use neutral surfaces, dark text, teal primary actions, blue source accents, amber warnings. Avoid decorative hero sections, gradients, floating orbs, oversized marketing copy, and playful visuals.

Responsive behavior:
- desktop uses a three-column operational layout plus bottom matter workspace,
- mobile stacks into one clear path with tabs wrapping into two columns.
```

## Stitch Iteration

The first Stitch screen was useful, but we did not stop there. We generated targeted alternatives around distinct product jobs:

- `LexNordic Applicant Workspace`: applicant route pre-check and matter creation.
- `Applicant First Route Intake`: sharper first answer for user-facing route pre-check.
- `Band Agent Matter Room`: strongest hackathon-visible Band coordination story.
- `Evidence Readiness Workspace`: strongest real product surface for migration-law case preparation.
- `Consultant Review Dashboard`: strongest law-firm supervisor surface.

Selection: implement `Evidence Readiness Workspace` as the primary UI direction, while keeping the compact Band agent activity strip visible. This best connects applicant action, legal basis, document status, risk, source citations, and agent ownership in one screen.

Downloaded Stitch references:

- `.agent-context/stitch/lexnordic-stitch.png`
- `.agent-context/stitch/variant-applicant-route-intake.png`
- `.agent-context/stitch/variant-band-agent-room.png`
- `.agent-context/stitch/variant-evidence-readiness.png`
- `.agent-context/stitch/variant-consultant-review.png`

## Current Implementation

The React UI now follows the selected Stitch `Evidence Readiness Workspace` visual structure as the source of truth.

Implemented in:

- `src/App.tsx`
- `src/styles.css`
- `index.html`

Current implementation screenshots:

- `.agent-context/screenshots/lexnordic-evidence-stitch-desktop.png`
- `.agent-context/screenshots/lexnordic-evidence-stitch-mobile.png`
- `.agent-context/screenshots/lexnordic-live-api-desktop.png`
- `.agent-context/screenshots/lexnordic-live-api-mobile.png`
- `.agent-context/screenshots/lexnordic-e2e-complete-desktop.png`

The latest implementation is API-backed. It fetches the workspace from FastAPI,
falls back to a public-safe local fixture when the backend is unavailable, and
wires the primary actions to document-request generation, private Supabase upload,
demo agent-room execution, and review-packet approval.

Product reality pass:

- The latest UI moved beyond a single-file prototype into a componentized matter
  cockpit with a persistent rail, route precheck, stage navigation, selected
  evidence preview, document center, source details, review packet panel,
  notifications/profile drawers, Band activity, extraction status, and human
  gate.
- Frontend structure now separates `src/api`, `src/hooks`, `src/components`,
  `src/data`, `src/utils`, `src/types.ts`, and the orchestration-only `src/App.tsx`.
- Latest verification screenshots:
  - `.agent-context/screenshots/lexnordic-componentized-e2e-desktop.png`
  - `.agent-context/screenshots/lexnordic-componentized-mobile.png`
  - `.agent-context/screenshots/lexnordic-frontend-complete-desktop.png`
  - `.agent-context/screenshots/lexnordic-frontend-complete-mobile.png`
  - `.agent-context/screenshots/lexnordic-frontend-complete-clean-desktop.png`
  - `.agent-context/screenshots/lexnordic-frontend-complete-clean-mobile.png`

Earlier custom-code interpretation screenshots, kept only as historical context:

- `.agent-context/screenshots/lexnordic-desktop-v2.png`
- `.agent-context/screenshots/lexnordic-mobile-v2.png`
- `.agent-context/screenshots/lexnordic-stitch-implemented-desktop-final.png`
- `.agent-context/screenshots/lexnordic-stitch-implemented-mobile-final.png`

## Stitch Artifact

Generated on 2026-06-13 with Stitch MCP after a shorter second prompt.

- Project: `LexNordic Migration Board`
- Project ID: `10308171654193505733`
- Design system: `LexNordic Operational System`
- Design system asset: `assets/98bd57f73eea4dd8b29e2526eabd2a0e`
- Screen: `LexNordic Applicant Workspace`
- Screen ID: `538092e97d0b4fc78132712d8cfb89c1`
- Screen resource: `projects/10308171654193505733/screens/538092e97d0b4fc78132712d8cfb89c1`
- Screenshot: https://lh3.googleusercontent.com/aida/AP1WRLu4pR_W_kU6WP-uUtftu8hr659gl4rkvp4SMnzp-r0F_lKsFiXg4KDPiHowyCsjRYWgUGq2Rptt_qgzVH0q1f5BNukK_KhICgW2fyO-U25h3Oa2XD7crWarjNQbde2TBoASBXvncFQhdSG3Houi8rG4C60HKdfPOPCfn6RfrdYo4OZq7LAqd-EymBZ5FeBNykDsehfV52M92PfaIH4iIlZb3oFYCnZZfQ2vPHHY8FRUAzogl2LSHC8eq5PF

Additional generated screens:

- `Applicant First Route Intake`: `262abf3d9183401b8ac07c20d8ac2f1a`
- `Band Agent Matter Room`: `7e5df5ea154d4709b24eff545d750460`
- `Evidence Readiness Workspace`: `c9abddd1f80b4288aaf913833c77652a`
- `Consultant Review Dashboard`: `0ad46450ed1f4cc2950a4c6afecb69a2`

Notes:

- First Stitch generation attempt timed out and did not produce a visible screen.
- Second attempt used a shorter prompt and `GEMINI_3_FLASH`.
- `get_screen` can retrieve the screen by ID; `list_screens` returned an empty object immediately after generation.
- The current app now mirrors the selected Stitch evidence workspace model: top route/status bar, left applicant context rail, central evidence matrix, right upload/source/review panel, compact Band agent strip, Material Symbols, Inter, flat legal-tech surfaces, teal primary action, blue source links, amber warning, and red blockers only.
