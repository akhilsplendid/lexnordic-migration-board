import { ClipboardList, Clock3, FileCheck2, FileWarning, Gauge, Sparkles, Workflow } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { BusyAction, Workspace } from "../types";

export function MatterLedger({
  workspace,
  busyAction,
  isBusy,
  onGenerateRequest,
  onRunReview,
}: {
  workspace: Workspace;
  busyAction: BusyAction;
  isBusy: boolean;
  onGenerateRequest: () => void;
  onRunReview: () => void;
}) {
  const missingEvidence = workspace.evidence_items.filter((item) =>
    ["missing", "warning"].includes(item.status_class),
  );
  const latestAgent = workspace.agent_activity[workspace.agent_activity.length - 1];
  const ledgerRows = [
    {
      title: "Consultation workspace",
      detail: workspace.matter.title ?? workspace.matter.summary ?? "Private Swedish migration-law consultation.",
      icon: <ClipboardList />,
    },
    {
      title: "Route and facts",
      detail: `${workspace.matter.route} with ${workspace.known_facts.length} known facts and ${workspace.missing_facts.length} unresolved facts.`,
      icon: <Gauge />,
    },
    {
      title: "Evidence operations",
      detail: `${missingEvidence.length} evidence items still need attention before the packet is strongest.`,
      icon: <FileWarning />,
    },
    {
      title: "Band activity",
      detail: latestAgent ? `${latestAgent.name}: ${latestAgent.next_action}` : "Agents are queued for alignment.",
      icon: <Workflow />,
    },
  ];

  return (
    <section className="matter-ledger-panel" aria-label="Matter ledger">
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">Matter ledger</span>
          <h2>What the AI firm knows now</h2>
        </div>
        <StatusPill tone={workspace.readiness.packet_gate.state === "unlocked" ? "ready" : "active"} icon={<Clock3 />}>
          {workspace.readiness.score}% packet readiness
        </StatusPill>
      </div>

      <div className="matter-ledger-list">
        {ledgerRows.map((row) => (
          <article className="matter-ledger-row" key={row.title}>
            <div className="ledger-icon">{row.icon}</div>
            <div>
              <strong>{row.title}</strong>
              <p>{row.detail}</p>
            </div>
          </article>
        ))}
      </div>

      <div className="matter-ledger-actions">
        <button className="secondary-action" type="button" onClick={onGenerateRequest} disabled={isBusy}>
          <FileCheck2 />
          <span>{busyAction === "document-request" ? "Building request" : "Request missing docs"}</span>
        </button>
        <button className="primary-action" type="button" onClick={onRunReview} disabled={isBusy}>
          <Sparkles />
          <span>{busyAction === "agent-run" ? "Aligning agents" : "Run Band alignment"}</span>
        </button>
      </div>
    </section>
  );
}
