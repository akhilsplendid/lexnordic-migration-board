import { CompetitionProofPanel } from "../components/CompetitionProofPanel";
import { DocumentCenter } from "../components/DocumentCenter";
import { EvidenceWorkbench } from "../components/EvidenceWorkbench";
import { ExtractionPanel } from "../components/ExtractionPanel";
import { ReviewPanel } from "../components/ReviewPanel";
import type { BusyAction, EvidenceGroups, EvidenceItem, SourceRef, Workspace } from "../types";

export function EvidencePage({
  workspace,
  groupedEvidence,
  selectedEvidence,
  selectedSource,
  busyAction,
  isBusy,
  gateUnlocked,
  onRefresh,
  onGenerateRequest,
  onUploadEvidence,
  onSelectEvidence,
  onSelectSource,
  onApprove,
  onRunReview,
}: {
  workspace: Workspace;
  groupedEvidence: EvidenceGroups;
  selectedEvidence?: EvidenceItem;
  selectedSource?: SourceRef;
  busyAction: BusyAction;
  isBusy: boolean;
  gateUnlocked: boolean;
  onRefresh: () => void;
  onGenerateRequest: () => void;
  onUploadEvidence: () => void;
  onSelectEvidence: (item: EvidenceItem) => void;
  onSelectSource: (sourceId: string) => void;
  onApprove: () => void;
  onRunReview: () => void;
}) {
  return (
    <section className="page-grid evidence-page" aria-label="Evidence page">
      <CompetitionProofPanel workspace={workspace} compact />
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
      <EvidenceWorkbench
        active
        groupedEvidence={groupedEvidence}
        isBusy={isBusy}
        selectedEvidenceId={selectedEvidence?.id}
        onRefresh={onRefresh}
        onSelectEvidence={onSelectEvidence}
      />
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
      <ExtractionPanel extraction={workspace.extraction_feed} />
    </section>
  );
}
