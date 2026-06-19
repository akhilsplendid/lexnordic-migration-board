import { BookOpenCheck, ExternalLink, FileCheck2, Gavel, ShieldCheck, Sparkles } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { BusyAction, EvidenceItem, SourceRef, Workspace, WorkspaceDocument } from "../types";

export function ReviewPanel({
  active,
  readiness,
  gateUnlocked,
  isBusy,
  busyAction,
  sources,
  selectedSource,
  selectedEvidence,
  documents,
  onApprove,
  onRunReview,
  onSelectSource,
}: {
  active: boolean;
  readiness: Workspace["readiness"];
  gateUnlocked: boolean;
  isBusy: boolean;
  busyAction: BusyAction;
  sources: SourceRef[];
  selectedSource?: SourceRef;
  selectedEvidence?: EvidenceItem;
  documents: WorkspaceDocument[];
  onApprove: () => void;
  onRunReview: () => void;
  onSelectSource: (sourceId: string) => void;
}) {
  return (
    <aside className={`review-panel ${active ? "panel-active" : ""}`} aria-label="AI packet panel">
      <section className="review-section">
        <div className="panel-header">
          <span className="section-kicker">AI packet status</span>
          {gateUnlocked ? <ShieldCheck /> : <Sparkles />}
        </div>
        <p>{packetStatusCopy(readiness, gateUnlocked)}</p>
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
                  ? "Finalize packet"
                  : "Run AI review"}
          </span>
        </button>
      </section>

      <section className="review-section">
        <div className="panel-header">
          <span className="section-kicker">Source trail</span>
          <BookOpenCheck />
        </div>
        <div className="source-stack">
          {sources.slice(0, 4).map((source) => (
            <button
              className={`source-card ${selectedSource?.id === source.id ? "selected" : ""}`}
              type="button"
              key={source.id}
              onClick={() => onSelectSource(source.id)}
            >
              <span>{source.title}</span>
              <small>{source.citation ?? "Official source"}</small>
              <ExternalLink />
            </button>
          ))}
        </div>
        {selectedSource && (
          <div className="source-detail">
            <strong>{selectedSource.title}</strong>
            <p>{selectedSource.snippet ?? selectedSource.citation ?? "Selected source is attached to the review trail."}</p>
            {selectedSource.url && (
              <a href={selectedSource.url} target="_blank" rel="noreferrer">
                Open official source
              </a>
            )}
          </div>
        )}
      </section>

      <section className="review-section document-preview">
        <div className="panel-header">
          <span className="section-kicker">Evidence preview</span>
          <FileCheck2 />
        </div>
        <div className="document-frame" aria-label="Document preview">
          <span />
          <b />
          <i />
          <i />
          <em />
        </div>
        <p>
          {selectedEvidence
            ? `${selectedEvidence.requirement}: ${selectedEvidence.status_label}`
            : "Select an evidence card to preview its packet state."}
        </p>
        <StatusPill tone={documents.length ? "good" : "idle"}>
          {documents.length ? `${documents.length} secure file attached` : "No secure files attached"}
        </StatusPill>
      </section>
    </aside>
  );
}

function packetStatusCopy(readiness: Workspace["readiness"], gateUnlocked: boolean): string {
  if (gateUnlocked) return "The AI packet has enough evidence to finalize for this private workspace.";
  return `The AI firm can keep working. Current packet readiness is ${readiness.score}%; the final packet target is ${readiness.packet_gate.threshold}%.`;
}
