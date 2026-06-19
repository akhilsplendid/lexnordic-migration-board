# Project Brief

## Outcome

Build a competition-ready hackathon demo that shows multiple AI agents coordinating through Band to review a regulated software change.

## Target User

Enterprise engineering, security, compliance, and release teams that need traceable review before shipping changes in high-stakes systems.

## First Usable Milestone

A local dashboard replays a realistic change-review workflow with four agents:

- Intake Planner
- Evidence Collector
- Compliance Reviewer
- Release Captain

The UI must make the Band-mediated handoffs visible and explainable in a 3-minute demo.

## Live Integration Milestone

Connect the four agents as Band remote agents using the Band SDK Codex adapter. Each role runs locally and participates in a shared Band chat room. Agents should pass work with `@mentions`, report progress, and produce a decision record.

## Constraints

- Do not commit secrets.
- Do not require paid cloud credentials unless explicitly approved.
- Use Codex-native access where possible.
- Keep the demo deployable as a static frontend.
- Keep Band as the real collaboration layer in the live path.

## Winning Angle

This is not a chatbot. It is an enterprise change-control board where agents divide work, challenge each other, gather evidence, and produce an auditable release decision.

## Risks

- Band remote-agent credentials are created manually and displayed once.
- Multiple live Codex agents may be heavy to run; the static replay must remain demoable.
- The dashboard must not overclaim compliance automation. It should present decision support and traceability, not legal approval.

## Acceptance Checks

- `npm run build` passes.
- Dashboard works on mobile and desktop.
- `agents/agent_config.yaml` is ignored.
- Live setup instructions are clear enough to wire during the hackathon.
