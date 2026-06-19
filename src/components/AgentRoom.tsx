import { UsersRound } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { AgentActivity, BusyAction } from "../types";
import { agentInitials, agentTone } from "../utils/workspace";

export function AgentRoom({
  active,
  agents,
  busyAction,
  isBusy,
  onRunReview,
}: {
  active: boolean;
  agents: AgentActivity[];
  busyAction: BusyAction;
  isBusy: boolean;
  onRunReview: () => void;
}) {
  return (
    <section className={`agent-room ${active ? "panel-active" : ""}`} id="agents-section" aria-label="Band agent room">
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">Band room</span>
          <h2>Specialists working the matter</h2>
        </div>
        <button className="secondary-action" type="button" onClick={onRunReview} disabled={isBusy}>
          <UsersRound />
          <span>{busyAction === "agent-run" ? "Running review" : "Run agent review"}</span>
        </button>
      </div>

      <div className="agent-timeline">
        {agents.map((agentItem) => (
          <article className="agent-event" key={agentItem.agent_role}>
            <div className="agent-avatar">{agentInitials(agentItem.name)}</div>
            <div>
              <div className="agent-event-header">
                <strong>{agentItem.name}</strong>
                <StatusPill tone={agentTone(agentItem.status_label)}>{agentItem.status_label}</StatusPill>
              </div>
              <p>{agentItem.summary}</p>
              <small>{agentItem.next_action}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
