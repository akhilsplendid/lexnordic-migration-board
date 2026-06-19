import { AgentTelemetryPanel } from "../components/AgentTelemetryPanel";
import { AgentRoom } from "../components/AgentRoom";
import { CompetitionProofPanel } from "../components/CompetitionProofPanel";
import { ExtractionPanel } from "../components/ExtractionPanel";
import { ReviewPacketPanel } from "../components/ReviewPacketPanel";
import type { AgentActivity, BusyAction, Workspace } from "../types";

export function AgentsPage({
  agents,
  workspace,
  busyAction,
  isBusy,
  gateUnlocked,
  onRunReview,
  onApprove,
}: {
  agents: AgentActivity[];
  workspace: Workspace;
  busyAction: BusyAction;
  isBusy: boolean;
  gateUnlocked: boolean;
  onRunReview: () => void;
  onApprove: () => void;
}) {
  return (
    <section className="page-grid agents-page" aria-label="Agents page">
      <AgentRoom
        active
        agents={agents}
        busyAction={busyAction}
        isBusy={isBusy}
        onRunReview={onRunReview}
      />
      <AgentTelemetryPanel
        agents={agents}
        busyAction={busyAction}
        isBusy={isBusy}
        workspace={workspace}
        onRunReview={onRunReview}
      />
      <CompetitionProofPanel workspace={workspace} compact />
      <ExtractionPanel extraction={workspace.extraction_feed} />
      <ReviewPacketPanel
        busyAction={busyAction}
        gateUnlocked={gateUnlocked}
        isBusy={isBusy}
        packet={workspace.review_packet}
        readiness={workspace.readiness}
        onApprove={onApprove}
        onRunReview={onRunReview}
      />
    </section>
  );
}
