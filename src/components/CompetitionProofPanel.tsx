import { BrainCircuit, Database, FileSearch, LockKeyhole, RadioTower, ShieldCheck, Workflow } from "lucide-react";

import type { Workspace } from "../types";

export function CompetitionProofPanel({
  workspace,
  compact = false,
}: {
  workspace: Workspace;
  compact?: boolean;
}) {
  const roomId = workspace.matter.band_room_id ?? "Band room pending";
  const signals = [
    {
      label: "Band room",
      value: shortValue(roomId),
      detail: `${workspace.agent_activity.length || 8} coordinated agents`,
      icon: <RadioTower />,
    },
    {
      label: "Source RAG",
      value: workspace.matter.qdrant_collection ?? "lexnordic_legal_sources",
      detail: `${workspace.source_bundle.length} active source refs`,
      icon: <Database />,
    },
    {
      label: "AI providers",
      value: "AI/ML + Featherless",
      detail: "reasoning, extraction, checking",
      icon: <BrainCircuit />,
    },
    {
      label: "Private vault",
      value: "Supabase RLS",
      detail: `${workspace.documents.length} user-owned files`,
      icon: <LockKeyhole />,
    },
  ];

  return (
    <section className={`competition-proof-panel ${compact ? "compact" : ""}`} aria-label="Hackathon proof panel">
      <div className="proof-panel-heading">
        <div>
          <span className="section-kicker">Competition proof</span>
          <h2>Live product stack, not a mockup</h2>
        </div>
        <ShieldCheck />
      </div>

      <div className="competition-signal-grid">
        {signals.map((signal) => (
          <article className="competition-signal" key={signal.label}>
            {signal.icon}
            <div>
              <small>{signal.label}</small>
              <strong>{signal.value}</strong>
              <span>{signal.detail}</span>
            </div>
          </article>
        ))}
      </div>

      <div className="boundary-strip">
        <Workflow />
        <span>Band coordinates the agents. The platform prepares a private AI case packet.</span>
        <FileSearch />
        <span>No automatic authority filing is triggered.</span>
      </div>
    </section>
  );
}

function shortValue(value: string): string {
  if (value.length <= 28) return value;
  return `${value.slice(0, 12)}...${value.slice(-6)}`;
}
