import { CompetitionProofPanel } from "../components/CompetitionProofPanel";
import { DocumentCenter } from "../components/DocumentCenter";
import { ReviewPacketPanel } from "../components/ReviewPacketPanel";
import { ReviewPanel } from "../components/ReviewPanel";
import type { BusyAction, EvidenceItem, SourceRef, Workspace } from "../types";

export function ReviewPage({
  workspace,
  busyAction,
  isBusy,
  gateUnlocked,
  selectedEvidence,
  selectedSource,
  onGenerateRequest,
  onUploadEvidence,
  onSelectEvidence,
  onSelectSource,
  onApprove,
  onRunReview,
}: {
  workspace: Workspace;
  busyAction: BusyAction;
  isBusy: boolean;
  gateUnlocked: boolean;
  selectedEvidence?: EvidenceItem;
  selectedSource?: SourceRef;
  onGenerateRequest: () => void;
  onUploadEvidence: () => void;
  onSelectEvidence: (item: EvidenceItem) => void;
  onSelectSource: (sourceId: string) => void;
  onApprove: () => void;
  onRunReview: () => void;
}) {
  return (
    <section className="page-grid review-page" aria-label="Review page">
      <ReviewPacketPanel
        busyAction={busyAction}
        gateUnlocked={gateUnlocked}
        isBusy={isBusy}
        packet={workspace.review_packet}
        readiness={workspace.readiness}
        onApprove={onApprove}
        onRunReview={onRunReview}
      />
      <CompetitionProofPanel workspace={workspace} compact />
      <ReviewPanel
        active
        busyAction={busyAction}
        documents={workspace.documents}
        gateUnlocked={gateUnlocked}
        isBusy={isBusy}
        readiness={workspace.readiness}
        selectedEvidence={selectedEvidence}
        selectedSource={selectedSource}
        sources={workspace.source_bundle}
        onApprove={onApprove}
        onRunReview={onRunReview}
        onSelectSource={onSelectSource}
      />
      <DocumentCenter
        busyAction={busyAction}
        documents={workspace.documents}
        evidenceItems={workspace.evidence_items}
        isBusy={isBusy}
        selectedEvidence={selectedEvidence}
        onGenerateRequest={onGenerateRequest}
        onSelectEvidence={onSelectEvidence}
        onUploadEvidence={onUploadEvidence}
      />
    </section>
  );
}
