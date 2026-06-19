import { BrainCircuit, Network, PlugZap, ServerCog } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { AgentActivity, BusyAction, Workspace } from "../types";
import { agentTone } from "../utils/workspace";

const REMOTE_ROLES = [
  "Intake",
  "Conflict KYC",
  "Decision Parser",
  "Evidence",
  "Legal Source",
  "Risk",
  "Appeal Packet",
  "Partner Review",
];

export function AgentTelemetryPanel({
  agents,
  workspace,
  busyAction,
  isBusy,
  onRunReview,
}: {
  agents: AgentActivity[];
  workspace: Workspace;
  busyAction: BusyAction;
  isBusy: boolean;
  onRunReview: () => void;
}) {
  return (
    <aside className="agent-telemetry-panel" aria-label="Band telemetry panel">
      <div className="section-heading compact">
        <div>
          <span className="section-kicker">Band telemetry</span>
          <h2>Remote agents and provider lanes</h2>
        </div>
        <Network />
      </div>

      <div className="provider-lane-grid">
        <article>
          <BrainCircuit />
          <div>
            <strong>AI/ML API</strong>
            <span>reasoning, route screening, drafting</span>
          </div>
        </article>
        <article>
          <ServerCog />
          <div>
            <strong>Featherless</strong>
            <span>open-model extraction and checks</span>
          </div>
        </article>
        <article>
          <PlugZap />
          <div>
            <strong>Band SDK</strong>
            <span>shared room context and handoffs</span>
          </div>
        </article>
      </div>

      <div className="remote-agent-list">
        {REMOTE_ROLES.map((role) => {
          const activity = agents.find((agent) => agent.name.toLowerCase().includes(role.toLowerCase().split(" ")[0]));
          return (
            <article className="remote-agent-row" key={role}>
              <span>{role}</span>
              <StatusPill tone={activity ? agentTone(activity.status_label) : "idle"}>
                {activity?.status_label ?? "Ready"}
              </StatusPill>
            </article>
          );
        })}
      </div>

      <div className="telemetry-payload">
        <span className="section-kicker">Shared payload</span>
        <code>
          {JSON.stringify(
            {
              matter: workspace.matter.matter_number,
              route: workspace.matter.route,
              readiness: workspace.readiness.score,
              sources: workspace.source_bundle.length,
              packet_gate: workspace.readiness.packet_gate.state,
            },
            null,
            2,
          )}
        </code>
      </div>

      <button className="primary-action full" type="button" onClick={onRunReview} disabled={isBusy}>
        <Network />
        <span>{busyAction === "agent-run" ? "Band alignment running" : "Run visible Band alignment"}</span>
      </button>
    </aside>
  );
}
