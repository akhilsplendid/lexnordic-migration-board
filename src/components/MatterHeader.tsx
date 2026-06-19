import { Bell, CheckCircle2, Sparkles } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { SectionId, Workspace } from "../types";

const PAGE_HEADERS: Record<SectionId, { label: string; title: string; description: string }> = {
  chat: {
    label: "Chat",
    title: "Ask LexNordic",
    description: "Describe your Swedish migration situation. LexNordic screens routes, asks for missing facts, and builds the case workspace.",
  },
  matter: {
    label: "Matter",
    title: "Active matter workspace",
    description: "Applicant facts, blockers, document state, and readiness for the selected route.",
  },
  route: {
    label: "Route",
    title: "Permit route planner",
    description: "Screen Swedish migration routes before opening or changing a matter strategy.",
  },
  evidence: {
    label: "Evidence",
    title: "Evidence vault",
    description: "Collect, classify, and reconcile applicant documents against the active route checklist.",
  },
  agents: {
    label: "Agents",
    title: "Band agent room",
    description: "Coordinate specialist agents, extraction status, and AI packet assembly.",
  },
  theater: {
    label: "Theater",
    title: "Band Ops Theater",
    description: "Watch the case file move through live agent handoffs, source retrieval, risk checks, and packet assembly.",
  },
  review: {
    label: "Packet",
    title: "AI case packet",
    description: "Inspect the source-backed case strategy, document checklist, and next actions.",
  },
};

export function MatterHeader({
  matter,
  activeSection,
  gateUnlocked,
  onOpenNotifications,
  onOpenProfile,
}: {
  matter: Workspace["matter"];
  activeSection: SectionId;
  gateUnlocked: boolean;
  onOpenNotifications: () => void;
  onOpenProfile: () => void;
}) {
  const page = PAGE_HEADERS[activeSection];
  const isChat = activeSection === "chat";

  return (
    <header className="matter-header">
      <div className="matter-title">
        <span className="breadcrumb">
          {isChat ? "New consultation / Swedish migration" : `${matter.matter_number} / ${page.label}`}
        </span>
        <h1>{page.title}</h1>
        <p>{page.description}</p>
      </div>

      <div className="header-actions">
        <StatusPill tone={isChat ? "active" : gateUnlocked ? "ready" : "active"} icon={isChat || gateUnlocked ? <CheckCircle2 /> : <Sparkles />}>
          {isChat ? "AI consultation" : gateUnlocked ? "AI packet ready" : "AI firm working"}
        </StatusPill>
        <button className="icon-button" type="button" aria-label="Open notifications" onClick={onOpenNotifications}>
          <Bell />
        </button>
        <button className="avatar-button" type="button" aria-label="Open applicant profile" onClick={onOpenProfile}>
          {matter.applicant_alias.slice(0, 2).toUpperCase()}
        </button>
      </div>
    </header>
  );
}
