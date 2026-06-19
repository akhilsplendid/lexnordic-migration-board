import { ClipboardCheck, FileUp } from "lucide-react";
import type { CSSProperties } from "react";

import type { BusyAction, Workspace } from "../types";

export function NextActionPanel({
  readiness,
  missingFacts,
  busyAction,
  isBusy,
  onUploadEvidence,
  onGenerateRequest,
}: {
  readiness: Workspace["readiness"];
  missingFacts: string[];
  busyAction: BusyAction;
  isBusy: boolean;
  onUploadEvidence: () => void;
  onGenerateRequest: () => void;
}) {
  return (
    <section className="next-action-panel" id="matter-section">
      <div className="score-orbit" style={{ "--score": `${readiness.score}%` } as CSSProperties}>
        <strong>{readiness.score}%</strong>
        <span>ready</span>
      </div>

      <div className="next-action-copy">
        <span className="section-kicker">Applicant next move</span>
        <h2>{readiness.applicant_next_step}</h2>
        <p>The AI firm can draft a stronger case packet as soon as the key employment and salary evidence is resolved.</p>
      </div>

      <div className="action-column">
        <div className="action-stack">
          <button className="primary-action" type="button" onClick={onUploadEvidence} disabled={isBusy}>
            <FileUp />
            <span>{busyAction === "upload" ? "Uploading evidence" : "Upload selected evidence"}</span>
          </button>
          <button className="secondary-action" type="button" onClick={onGenerateRequest} disabled={isBusy}>
            <ClipboardCheck />
            <span>{busyAction === "document-request" ? "Preparing request" : "Generate request checklist"}</span>
          </button>
        </div>
        <div className="next-action-insights" aria-label="Matter control summary">
          <div>
            <small>Blocking evidence</small>
            <strong>{readiness.blocker_count} open</strong>
          </div>
          <div>
            <small>Packet target</small>
            <strong>{readiness.packet_gate.threshold}% ready</strong>
          </div>
          <div className="insight-wide">
            <small>Missing now</small>
            <span>{missingFacts.length ? missingFacts.slice(0, 2).join(" + ") : "No missing facts"}</span>
          </div>
        </div>
      </div>
    </section>
  );
}
