import { ApplicantBrief } from "../components/ApplicantBrief";
import { CompetitionProofPanel } from "../components/CompetitionProofPanel";
import { DocumentCenter } from "../components/DocumentCenter";
import { MatterLedger } from "../components/MatterLedger";
import { NextActionPanel } from "../components/NextActionPanel";
import { ReviewPanel } from "../components/ReviewPanel";
import type { BusyAction, EvidenceItem, SourceRef, Workspace } from "../types";

export function MatterPage({
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
    <section className="page-grid matter-page" aria-label="Matter page">
      <NextActionPanel
        busyAction={busyAction}
        isBusy={isBusy}
        missingFacts={workspace.missing_facts}
        readiness={workspace.readiness}
        onGenerateRequest={onGenerateRequest}
        onUploadEvidence={onUploadEvidence}
      />
      <CompetitionProofPanel workspace={workspace} compact />
      <ApplicantBrief knownFacts={workspace.known_facts} missingFacts={workspace.missing_facts} />
      <MatterLedger
        busyAction={busyAction}
        isBusy={isBusy}
        workspace={workspace}
        onGenerateRequest={onGenerateRequest}
        onRunReview={onRunReview}
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
    </section>
  );
}
