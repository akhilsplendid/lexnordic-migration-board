# Stitch Page Pass

Last updated: 2026-06-18

Purpose: record the Stitch MCP design references used for the competition polish pass and how each product page maps to the generated direction.

## Stitch Project

- Project: LexNordic Migration Board
- Project ID: `10308171654193505733`
- Design system: LexNordic Operational System
- Design system asset: `assets/98bd57f73eea4dd8b29e2526eabd2a0e`

## Page Mapping

| Product surface | Stitch reference | Screen ID | Implementation result |
| --- | --- | --- | --- |
| Auth gate | LexNordic Auth Gate | `f6291ee26e7c4fba8339e0ff82d0644c` | Two-column trust/auth entry with workflow preview, private workspace boundary, and compact sign-in form. |
| Chat | Migration Counsel AI Chat Workspace | `702ef01567044ba08f002182a33c3cd0` | ChatGPT-style consultation page with workflow strip, Band-ready status, case-builder panel, and live stack proof. |
| Matter | Band Agent Matter Room | `7e5df5ea154d4709b24eff545d750460` | Matter cockpit now includes stack proof and a matter ledger for facts, evidence, Band state, and next actions. |
| Route | Applicant First Route Intake | `262abf3d9183401b8ac07c20d8ac2f1a` | Route page now has a route catalog board, candidate comparison, next-question lane, and June 2026 rule overlay. |
| Evidence | Evidence Readiness Workspace | `c9abddd1f80b4288aaf913833c77652a` | Evidence page keeps document center/workbench/review panel and adds competition proof tied to sources and private vault. |
| Agents | Band Agent Matter Room | `7e5df5ea154d4709b24eff545d750460` | Agents page now adds provider lanes, remote-agent roster, shared payload view, and visible Band alignment control. |
| Theater | LexNordic Band Ops Theater | `2813ea7499da4fbcab782193fd441e11` | Theater page now has pixel-agent choreography, judge proof, remote roster, payload JSON, and interactive pause/replay/speed controls. |
| Packet | Consultant Review Dashboard | `0ad46450ed1f4cc2950a4c6afecb69a2` | Packet page now combines source-backed packet strategy, proof panel, source trail, document preview, and request queue. |

## Tool Notes

Two fresh long-form Stitch generations for Matter and Route exceeded the two-minute MCP call limit and did not appear through `list_screens`. The implementation therefore used the already retrieved Stitch references for those surfaces, while Theater and Auth were generated successfully in this pass.

Higgsfield CLI was checked for the requested asset/content pass, but the local session is not authenticated. The CLI returned `Not authenticated` / `Run: hf auth login`, so no Higgsfield credits were spent in this pass.

## Verification

- `npm run build` passed after the page-pass implementation.
- Browser smoke with disposable Supabase Auth users passed for desktop `1440x1000` and mobile `390x844`.
- Checked pages: Chat, Matter, Route, Evidence, Agents, Theater, Packet.
- Results: no console warnings/errors, no horizontal overflow, no horizontally offscreen buttons, and no undersized visible buttons.
- Theater controls were clicked during smoke: pause/resume, replay baton, and speed toggle.
