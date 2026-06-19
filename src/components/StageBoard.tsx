import { CheckCircle2, ChevronRight, CircleDashed } from "lucide-react";
import type { ReactNode } from "react";

import type { StageId } from "../types";

export function StageBoard({
  activeStage,
  factCount,
  blockerCount,
  agentCount,
  gateUnlocked,
  onSelect,
}: {
  activeStage: StageId;
  factCount: number;
  blockerCount: number;
  agentCount: number;
  gateUnlocked: boolean;
  onSelect: (stage: StageId) => void;
}) {
  const stages: Array<{ id: StageId; number: string; title: string; detail: string; done?: boolean }> = [
    { id: "intake", number: "01", title: "Intake", detail: `${factCount} facts captured`, done: true },
    { id: "evidence", number: "02", title: "Evidence", detail: `${blockerCount} blocker checks` },
    { id: "agent_review", number: "03", title: "Agent review", detail: `${agentCount} agents linked` },
    {
      id: "packet_final",
      number: "04",
      title: "AI packet",
      detail: gateUnlocked ? "Ready to finalize" : "Building strategy",
    },
  ];

  return (
    <section className="stage-board" aria-label="Matter stages">
      {stages.map((stage) => (
        <button
          className={`stage-item ${activeStage === stage.id ? "active" : ""} ${stage.done ? "done" : ""}`}
          type="button"
          aria-pressed={activeStage === stage.id}
          key={stage.id}
          onClick={() => onSelect(stage.id)}
        >
          <span>{stage.done ? <CheckCircle2 /> : activeStage === stage.id ? <CircleDashed /> : stage.number}</span>
          <div>
            <strong>{stage.title}</strong>
            <small>{stage.detail}</small>
          </div>
          <ChevronRight />
        </button>
      ))}
    </section>
  );
}
