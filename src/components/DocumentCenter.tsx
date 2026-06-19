import { ClipboardCheck, FileSearch, FileUp, ShieldCheck } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { BusyAction, EvidenceItem, WorkspaceDocument } from "../types";

export function DocumentCenter({
  selectedEvidence,
  evidenceItems,
  documents,
  busyAction,
  isBusy,
  onSelectEvidence,
  onUploadEvidence,
  onGenerateRequest,
}: {
  selectedEvidence?: EvidenceItem;
  evidenceItems: EvidenceItem[];
  documents: WorkspaceDocument[];
  busyAction: BusyAction;
  isBusy: boolean;
  onSelectEvidence: (item: EvidenceItem) => void;
  onUploadEvidence: () => void;
  onGenerateRequest: () => void;
}) {
  return (
    <section className="document-center" aria-labelledby="document-center-heading">
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">Document center</span>
          <h2 id="document-center-heading">Evidence files and applicant requests</h2>
        </div>
        <button className="secondary-action" type="button" onClick={onGenerateRequest} disabled={isBusy}>
          <ClipboardCheck />
          <span>{busyAction === "document-request" ? "Preparing" : "Request missing docs"}</span>
        </button>
      </div>

      <div className="document-center-grid">
        <div className="selected-evidence-panel">
          <span className="section-kicker">Selected requirement</span>
          {selectedEvidence ? (
            <>
              <h3>{selectedEvidence.requirement}</h3>
              <dl>
                <div>
                  <dt>Status</dt>
                  <dd>{selectedEvidence.status_label}</dd>
                </div>
                <div>
                  <dt>Basis</dt>
                  <dd>{selectedEvidence.basis}</dd>
                </div>
                <div>
                  <dt>Owner</dt>
                  <dd>{selectedEvidence.agent_name}</dd>
                </div>
              </dl>
              <button className="primary-action full" type="button" onClick={onUploadEvidence} disabled={isBusy}>
                <FileUp />
                <span>{busyAction === "upload" ? "Uploading" : `Upload ${selectedEvidence.requirement}`}</span>
              </button>
            </>
          ) : (
            <p className="empty-note">Select an evidence card to prepare the upload target.</p>
          )}
        </div>

        <div className="document-list-panel">
          <span className="section-kicker">Attached files</span>
          <div className="document-list">
            {documents.length ? (
              documents.map((document) => (
                <article className="document-row" key={document.id}>
                  <FileSearch />
                  <div>
                    <strong>{document.filename}</strong>
                    <span>{document.document_type.replaceAll("_", " ")}</span>
                  </div>
                  <StatusPill tone="good">
                    <ShieldCheck />
                    Stored
                  </StatusPill>
                </article>
              ))
            ) : (
              <p className="empty-note">No applicant files are attached yet.</p>
            )}
          </div>
        </div>

        <div className="request-list-panel">
          <span className="section-kicker">Request queue</span>
          <div className="request-list">
            {evidenceItems
              .filter((item) => ["missing", "warning", "active"].includes(item.status_class))
              .map((item) => (
                <button
                  className={`request-row ${selectedEvidence?.id === item.id ? "selected" : ""}`}
                  type="button"
                  key={item.id}
                  onClick={() => onSelectEvidence(item)}
                >
                  <span>{item.requirement}</span>
                  <small>{item.status_label}</small>
                </button>
              ))}
          </div>
        </div>
      </div>
    </section>
  );
}
