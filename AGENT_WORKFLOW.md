# Agent Workflow

## Band Room

Room name: `Change Board - Payment Retry Policy`

The human submits a change request and mentions the Intake Planner. From there, the agents coordinate through Band.

## Agents

### Intake Planner

Objective: Convert the human request into a scoped review plan.

Inputs:
- Change request text
- Repository path or uploaded diff summary
- Release deadline
- Known controls

Outputs:
- Review plan
- Task list
- Mentions to the next agents

Stop condition:
- Evidence Collector and Compliance Reviewer have clear tasks.

### Evidence Collector

Objective: Gather implementation, test, and deployment evidence.

Inputs:
- Review plan
- Repository paths
- Test command outputs
- Diff summaries

Outputs:
- Evidence bundle
- Gaps and missing checks
- Mention back to Compliance Reviewer and Release Captain

Stop condition:
- Evidence bundle is attached to the room transcript.

### Compliance Reviewer

Objective: Evaluate policy, audit, and rollback readiness.

Inputs:
- Review plan
- Evidence bundle
- Control checklist

Outputs:
- Control pass/fail table
- Escalation notes
- Required mitigations

Stop condition:
- Control decision is ready for the Release Captain.

### Release Captain

Objective: Synthesize the final decision.

Inputs:
- Review plan
- Evidence bundle
- Compliance review
- Human deadline and risk appetite

Outputs:
- Ship / hold / ship-with-conditions decision
- Release notes
- Remaining risk
- Human approval request

Stop condition:
- Final decision record is posted.

## Required Band Behaviors

- Agents communicate via `@mentions`.
- Agents share structured context in the room, not just final summaries.
- At least three agents participate in the core workflow.
- The Release Captain cannot decide before receiving evidence and compliance review.
- Human approval remains explicit before public release actions.

## Demo Flow

1. Human posts a payment retry-policy change request.
2. Intake Planner scopes the review and mentions the Evidence Collector and Compliance Reviewer.
3. Evidence Collector reports test, diff, and rollback findings.
4. Compliance Reviewer checks traceability, privacy, audit, and release controls.
5. Release Captain posts a conditional ship decision and asks the human for approval.
