import { AlertTriangle, ArrowRight, CheckCircle2, RefreshCw, XCircle } from "lucide-react";
import type { ReactNode } from "react";

import { StatusPill } from "./StatusPill";
import type { EvidenceGroups, EvidenceItem } from "../types";
import { statusTone } from "../utils/workspace";

export function EvidenceWorkbench({
  groupedEvidence,
  selectedEvidenceId,
  active,
  isBusy,
  onRefresh,
  onSelectEvidence,
}: {
  groupedEvidence: EvidenceGroups;
  selectedEvidenceId?: string;
  active: boolean;
  isBusy: boolean;
  onRefresh: () => void;
  onSelectEvidence: (item: EvidenceItem) => void;
}) {
  return (
    <section
      className={`evidence-flow ${active ? "panel-active" : ""}`}
      id="evidence-section"
      aria-labelledby="evidence-heading"
    >
      <div className="section-heading">
        <div>
          <span className="section-kicker">Evidence workbench</span>
          <h2 id="evidence-heading">Move the case from missing to packet-ready</h2>
        </div>
        <button className="text-action" type="button" onClick={onRefresh} disabled={isBusy}>
          <RefreshCw />
          <span>Refresh workspace</span>
        </button>
      </div>

      <div className="evidence-columns">
        <EvidenceColumn title="Verified" count={groupedEvidence.verified.length} tone="good">
          {groupedEvidence.verified.map((item) => (
            <EvidenceCard
              item={item}
              key={item.id}
              selected={selectedEvidenceId === item.id}
              onSelect={() => onSelectEvidence(item)}
            />
          ))}
        </EvidenceColumn>
        <EvidenceColumn title="In review" count={groupedEvidence.review.length} tone="watch">
          {groupedEvidence.review.map((item) => (
            <EvidenceCard
              item={item}
              key={item.id}
              selected={selectedEvidenceId === item.id}
              onSelect={() => onSelectEvidence(item)}
            />
          ))}
        </EvidenceColumn>
        <EvidenceColumn title="Blocking" count={groupedEvidence.blocking.length} tone="risk">
          {groupedEvidence.blocking.map((item) => (
            <EvidenceCard
              item={item}
              key={item.id}
              selected={selectedEvidenceId === item.id}
              onSelect={() => onSelectEvidence(item)}
            />
          ))}
        </EvidenceColumn>
      </div>
    </section>
  );
}

function EvidenceColumn({
  title,
  count,
  tone,
  children,
}: {
  title: string;
  count: number;
  tone: "good" | "watch" | "risk";
  children: ReactNode;
}) {
  return (
    <section className={`evidence-column ${tone}`}>
      <header>
        <strong>{title}</strong>
        <span>{count}</span>
      </header>
      <div className="evidence-card-list">{count > 0 ? children : <p className="empty-note">No items in this lane.</p>}</div>
    </section>
  );
}

function EvidenceCard({ item, selected, onSelect }: { item: EvidenceItem; selected: boolean; onSelect: () => void }) {
  return (
    <button
      className={`evidence-card ${item.status_class} ${selected ? "selected" : ""}`}
      type="button"
      aria-pressed={selected}
      onClick={onSelect}
    >
      <div className="evidence-card-main">
        <small>{item.group}</small>
        <strong>{item.requirement}</strong>
      </div>
      <div className="evidence-card-meta">
        <StatusPill tone={statusTone(item.status_class)} icon={statusGlyph(item.status_class)}>
          {item.status_label}
        </StatusPill>
        <span>{item.basis}</span>
      </div>
      <footer>
        <span>{item.agent_name}</span>
        <span className="mini-link">
          {item.action_label}
          <ArrowRight />
        </span>
      </footer>
    </button>
  );
}

function statusGlyph(statusClass: string): ReactNode {
  if (statusClass === "missing") return <XCircle />;
  if (statusClass === "active") return <RefreshCw />;
  if (statusClass === "warning") return <AlertTriangle />;
  return <CheckCircle2 />;
}
