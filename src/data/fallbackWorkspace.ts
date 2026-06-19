import { MATTER_NUMBER } from "../config";
import type { AgentActivity, EvidenceItem, Workspace } from "../types";

export const fallbackWorkspace: Workspace = {
  matter: {
    matter_number: MATTER_NUMBER,
    route: "Work Permit after Higher Education",
    state_label: "Evidence gathering",
    applicant_alias: "JD",
  },
  readiness: {
    score: 42,
    blocker_count: 3,
    applicant_next_step: "Secure employment contract",
    packet_gate: {
      threshold: 80,
      state: "locked",
      label: "Packet target is 80% readiness. Currently at 42%.",
    },
  },
  known_facts: ["KTH Master's degree", "Current residence permit"],
  missing_facts: ["Job offer start date", "Monthly gross salary"],
  evidence_items: [
    row("IDENTITY", "Passport copies", "identity", "Verified", "verified", "Ch. 2, 1 A", "Low", "low", "Intake", "View file"),
    row("RESIDENCE", "Current permit card", "current_permit", "Analyzing", "active", "Ch. 5, 5", "Low", "low", "Evidence", "Details"),
    row("STUDIES", "Degree certificate", "degree_certificate", "Uploaded", "uploaded", "Ch. 6b, 1", "Low", "low", "Evidence", "Verify"),
    row("EMPLOYMENT", "Job offer", "employment_contract", "Missing", "missing", "Ch. 6, 2", "High", "high", "Legal", "Request"),
    row(
      "SALARY / INSURANCE",
      "Salary specification",
      "salary_evidence",
      "Risk found",
      "warning",
      "Ch. 6, 3 MA",
      "Low threshold",
      "warning",
      "Risk Assessor",
      "Review",
    ),
  ],
  documents: [],
  source_bundle: [
    { id: "migration-act", title: "Migration Act (2005:716)", citation: "Work and residence permit basis" },
    { id: "salary-2026", title: "June 2026 salary threshold", citation: "Current-rule overlay" },
  ],
  extraction_feed: {
    status: "running",
    progress: 65,
    message: "Extracting passport expiry",
    fields: ["Degree OCR validated: KTH Royal Institute"],
  },
  agent_activity: [
    agent("intake", "Intake Agent", "Idle", "Known facts captured."),
    agent("evidence", "Evidence Checker", "Active", "Extracting passport expiry."),
    agent("legal_source", "Legal Source Agent", "Idle", "Ready to retrieve source bundle."),
    agent("risk", "Risk Assessor", "Done", "Salary threshold risk identified."),
  ],
  review_packet: {
    status: "not_started",
    summary: "AI case packet will be generated after the specialist agents align on evidence, risk, and sources.",
    next_actions: ["Upload employment contract", "Resolve salary threshold evidence"],
  },
};

function row(
  group: string,
  requirement: string,
  documentType: string,
  statusLabel: string,
  statusClass: string,
  basis: string,
  riskLevel: string,
  riskClass: string,
  agentName: string,
  actionLabel: string,
): EvidenceItem {
  return {
    id: requirement,
    group,
    requirement,
    document_type: documentType,
    status_label: statusLabel,
    status_class: statusClass,
    basis,
    risk_level: riskLevel,
    risk_class: riskClass,
    agent_name: agentName,
    action_label: actionLabel,
  };
}

function agent(role: string, name: string, statusLabel: string, summary: string): AgentActivity {
  return {
    agent_role: role,
    name,
    status: statusLabel.toLowerCase(),
    status_label: statusLabel,
    summary,
    next_action: "Continue review",
  };
}
