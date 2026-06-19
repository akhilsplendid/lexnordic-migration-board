import type { EvidenceGroups, EvidenceItem, SectionId, StageId } from "../types";

export function groupEvidence(items: EvidenceItem[]): EvidenceGroups {
  const verified = items.filter((item) => ["verified", "uploaded"].includes(item.status_class));
  const blocking = items.filter(
    (item) => ["missing", "warning"].includes(item.status_class) || item.risk_class === "high",
  );
  const review = items.filter((item) => !verified.includes(item) && !blocking.includes(item));
  return { verified, review, blocking };
}

export function sectionFromStage(stage: StageId): SectionId {
  if (stage === "intake") return "route";
  if (stage === "evidence") return "evidence";
  if (stage === "agent_review") return "agents";
  return "review";
}

export function statusTone(statusClass: string): "good" | "watch" | "risk" | "active" {
  if (statusClass === "verified" || statusClass === "uploaded") return "good";
  if (statusClass === "missing") return "risk";
  if (statusClass === "active") return "active";
  return "watch";
}

export function agentTone(statusLabel: string): "active" | "done" | "watch" | "idle" | "risk" {
  const lowered = statusLabel.toLowerCase();
  if (lowered.includes("active") || lowered.includes("running")) return "active";
  if (lowered.includes("done") || lowered.includes("complete")) return "done";
  if (lowered.includes("review")) return "watch";
  if (lowered.includes("block") || lowered.includes("fail")) return "risk";
  return "idle";
}

export function agentInitials(name: string): string {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function messageFrom(error: unknown): string {
  if (error instanceof Error) {
    return error.message.slice(0, 240);
  }
  return "Unexpected workspace error";
}
