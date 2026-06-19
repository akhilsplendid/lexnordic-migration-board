import { CheckCircle2, FileCheck2, Gavel, Sparkles } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { BusyAction, Workspace } from "../types";

export function ReviewPacketPanel({
  packet,
  readiness,
  gateUnlocked,
  busyAction,
  isBusy,
  onApprove,
  onRunReview,
}: {
  packet: Workspace["review_packet"];
  readiness: Workspace["readiness"];
  gateUnlocked: boolean;
  busyAction: BusyAction;
  isBusy: boolean;
  onApprove: () => void;
  onRunReview: () => void;
}) {
  const checklist = packet.document_checklist?.length
    ? packet.document_checklist
    : ["Passport copies", "Current permit card", "Degree certificate", "Employment contract", "Salary evidence"];

  return (
    <section className="review-packet-panel" aria-labelledby="review-packet-heading">
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">AI case packet</span>
          <h2 id="review-packet-heading">Source-backed case strategy</h2>
        </div>
        <StatusPill tone={gateUnlocked ? "ready" : "active"} icon={gateUnlocked ? <CheckCircle2 /> : <Sparkles />}>
          {gateUnlocked ? "Packet ready" : `${readiness.score}% ready`}
        </StatusPill>
      </div>

      <p className="packet-summary">{packet.summary}</p>

      <div className="packet-grid">
        <div>
          <span className="section-kicker">Checklist</span>
          <ul className="packet-list">
            {checklist.map((item) => (
              <li key={item}>
                <FileCheck2 />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <span className="section-kicker">Next actions</span>
          <ul className="packet-list">
            {packet.next_actions.map((action) => (
              <li key={action}>
                <CheckCircle2 />
                <span>{action}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {packet.applicant_message && <p className="applicant-message">{packet.applicant_message}</p>}

      <button
        className={gateUnlocked ? "primary-action full" : "secondary-action full"}
        type="button"
        disabled={isBusy}
        onClick={gateUnlocked ? onApprove : onRunReview}
      >
        {gateUnlocked ? <Gavel /> : <Sparkles />}
        <span>
          {busyAction === "approve"
            ? "Finalizing packet"
            : busyAction === "agent-run"
              ? "AI review running"
              : gateUnlocked
                ? "Finalize AI packet"
                : "Run AI packet review"}
        </span>
      </button>
    </section>
  );
}
