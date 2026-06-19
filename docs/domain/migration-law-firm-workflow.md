# Migration Law Firm Workflow

Purpose: translate real law-firm matter handling into a product workflow.

## Matter Lifecycle

```text
Lead or inquiry
  -> preliminary intake
  -> confidentiality notice
  -> conflict check
  -> KYC / identity / authority check
  -> scope and fee proposal
  -> engagement accepted
  -> matter plan
  -> evidence collection
  -> legal-source review
  -> draft advice / AI case packet
  -> packet-quality gate
  -> user confirmation
  -> user-owned next action outside the platform
  -> archive and close
```

## What The Firm Needs To Know Before Work Starts

- Applicant name and identifying details.
- Permit category.
- Decision date and date received.
- Case/control number.
- Whether appeal is possible according to the decision.
- Deadline stated in the decision.
- Current location and right-to-remain facts.
- Applicant family/employer/school context.
- Representative authority or power of attorney status.
- Uploaded decision letter and appendix.
- Existing evidence already submitted.
- Missing documents.
- Language needs.
- Any urgent/sensitive flags.

## Hard Gates

### Confidentiality Gate

Agents treat uploaded documents and intake facts as confidential matter data. Product copy must say the system prepares AI consultation material and does not file, sign, or contact authorities.

### Conflict Gate

Before substantive advice, the firm checks:

- client/applicant identity,
- employer/sponsor identity,
- opposing authority or related parties,
- related former/current clients,
- representative or organizational conflicts.

Agents may prepare conflict-check inputs but must not clear conflicts autonomously.

### KYC / Authority Gate

The firm must know who the client is and whether the person instructing the firm has authority.

For migration cases this may involve:

- applicant identity,
- employer contact identity,
- family sponsor identity,
- representative authorization,
- power of attorney status.

### Sensitivity Gate

Escalate immediately for:

- asylum/protection,
- deportation/expulsion,
- detention,
- unaccompanied children,
- trafficking or domestic violence,
- statelessness,
- urgent deadline under 48 hours,
- mental-health or trauma-heavy narrative,
- suspected forged documents,
- criminality/security facts.

## Core Workstream For MVP

MVP matter:

> A fictional applicant asks about a Swedish work-permit route and receives an AI consultation packet.

Workflow:

1. Intake agent creates matter summary and deadline table.
2. Decision parser extracts rejection grounds and cited missing requirements.
3. Evidence agent maps submitted evidence against required evidence.
4. Legal source agent retrieves relevant official pages and source chunks.
5. Risk agent flags uncertainty, sensitivity, and unsupported claims.
6. Appeal packet agent drafts a source-grounded packet structure.
7. Partner review agent creates the final memo and user question list.

## Final Output Packet

- Matter summary.
- Timeline and deadline warnings.
- Rejection-ground table.
- Evidence submitted vs missing.
- Source-backed requirement checklist.
- Risk register.
- Draft route or appeal structure.
- User questions.
- Packet readiness checklist.

## What The Product Must Not Do

- It must not claim to be a licensed legal representative.
- It must not guarantee outcome.
- It must not file appeals.
- It must not sign forms.
- It must not contact Migrationsverket.
- It must not tell users to stay, leave, work, travel, or ignore a decision.
