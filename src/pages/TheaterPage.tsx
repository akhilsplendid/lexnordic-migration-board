import { ArrowRight, BadgeCheck, FileCheck2, Gauge, Pause, Play, RadioTower, RotateCcw, Sparkles, Workflow } from "lucide-react";
import type { CSSProperties } from "react";
import { useState } from "react";

import { StatusPill } from "../components/StatusPill";
import type { AgentActivity, BusyAction, Workspace } from "../types";

type TheaterAgent = {
  role: string;
  name: string;
  station: string;
  payload: string;
  x: number;
  y: number;
  tone: "mint" | "blue" | "amber" | "red" | "violet";
};

const THEATER_AGENTS: TheaterAgent[] = [
  {
    role: "intake",
    name: "Intake",
    station: "front desk",
    payload: "facts",
    x: 13,
    y: 18,
    tone: "mint",
  },
  {
    role: "evidence",
    name: "Evidence",
    station: "document vault",
    payload: "missing docs",
    x: 31,
    y: 66,
    tone: "blue",
  },
  {
    role: "legal_source",
    name: "Sources",
    station: "law library",
    payload: "official rules",
    x: 50,
    y: 16,
    tone: "violet",
  },
  {
    role: "risk",
    name: "Risk",
    station: "red board",
    payload: "threshold flags",
    x: 69,
    y: 64,
    tone: "amber",
  },
  {
    role: "appeal_packet",
    name: "Packet",
    station: "case printer",
    payload: "final packet",
    x: 84,
    y: 22,
    tone: "red",
  },
];

const REMOTE_AGENT_ROSTER = [
  "Intake",
  "Conflict KYC",
  "Decision Parser",
  "Evidence",
  "Legal Source",
  "Risk",
  "Appeal Packet",
  "Partner Review",
];

export function TheaterPage({
  workspace,
  busyAction,
  isBusy,
  onRunReview,
  onOpenPacket,
}: {
  workspace: Workspace;
  busyAction: BusyAction;
  isBusy: boolean;
  onRunReview: () => void;
  onOpenPacket: () => void;
}) {
  const [isPaused, setIsPaused] = useState(false);
  const [isFast, setIsFast] = useState(false);
  const [replayKey, setReplayKey] = useState(0);
  const agentMap = new Map(workspace.agent_activity.map((agent) => [agent.agent_role, agent]));
  const completed = workspace.agent_activity.filter((agent) => /done|complete|review/i.test(agent.status_label)).length;
  const active = workspace.agent_activity.find((agent) => /active|running/i.test(agent.status_label));
  const roomId = workspace.matter.band_room_id ?? "local Band room";
  const handoffCount = Math.max(4, workspace.agent_activity.length + workspace.source_bundle.length);

  return (
    <section className="theater-page" aria-label="Band Ops Theater">
      <section className="theater-stage-card" aria-labelledby="theater-stage-heading">
        <div className="theater-stage-header">
          <div>
            <span className="section-kicker">Hackathon mode</span>
            <h2 id="theater-stage-heading">Pixel agents carrying the case through Band</h2>
          </div>
          <StatusPill tone={active ? "active" : "ready"} icon={<RadioTower />}>
            {active ? `${active.name} live` : "Band trace ready"}
          </StatusPill>
        </div>

        <div
          className={`pixel-stage ${isPaused ? "paused" : ""} ${isFast ? "fast" : ""}`}
          aria-label="Animated Band coordination stage"
        >
          <div className="pixel-grid" />
          <div className="band-hub">
            <Workflow />
            <strong>Band Room</strong>
            <span>{shortRoom(roomId)}</span>
          </div>
          <div className="context-baton" aria-hidden="true" key={replayKey}>
            <span />
          </div>

          {THEATER_AGENTS.map((agent, index) => (
            <PixelAgent
              agent={agent}
              index={index}
              key={agent.role}
              run={agentMap.get(agent.role)}
            />
          ))}
        </div>

        <div className="theater-action-row">
          <button className="primary-action" type="button" onClick={onRunReview} disabled={isBusy}>
            <Sparkles />
            <span>{busyAction === "agent-run" ? "Running Band theater" : "Run Band theater"}</span>
          </button>
          <button className="secondary-action" type="button" onClick={onOpenPacket}>
            <FileCheck2 />
            <span>Open AI packet</span>
          </button>
        </div>

        <div className="theater-control-strip" aria-label="Theater animation controls">
          <button className="secondary-action" type="button" onClick={() => setIsPaused((current) => !current)}>
            {isPaused ? <Play /> : <Pause />}
            <span>{isPaused ? "Resume sprites" : "Pause sprites"}</span>
          </button>
          <button className="secondary-action" type="button" onClick={() => setReplayKey((current) => current + 1)}>
            <RotateCcw />
            <span>Replay baton</span>
          </button>
          <button className="secondary-action" type="button" onClick={() => setIsFast((current) => !current)}>
            <Gauge />
            <span>{isFast ? "Normal speed" : "Judge speed"}</span>
          </button>
        </div>
      </section>

      <aside className="judge-proof-panel" aria-labelledby="judge-proof-heading">
        <div className="section-heading compact">
          <div>
            <span className="section-kicker">Judge proof</span>
            <h2 id="judge-proof-heading">Band is doing the coordination</h2>
          </div>
          <BadgeCheck />
        </div>

        <div className="proof-grid">
          <ProofStat label="Remote agents" value="8" />
          <ProofStat label="Visible handoffs" value={String(handoffCount)} />
          <ProofStat label="Source refs" value={String(workspace.source_bundle.length)} />
          <ProofStat label="Readiness" value={`${workspace.readiness.score}%`} />
        </div>

        <div className="theater-agent-roster" aria-label="Remote agent roster">
          {REMOTE_AGENT_ROSTER.map((agent) => (
            <span key={agent}>{agent}</span>
          ))}
        </div>

        <div className="payload-card">
          <span className="section-kicker">Context baton payload</span>
          <code>
            {JSON.stringify(
              {
                room: shortRoom(roomId),
                matter: workspace.matter.matter_number,
                route: workspace.matter.route,
                owner: active?.name ?? "Appeal Packet Agent",
                next: workspace.readiness.applicant_next_step,
              },
              null,
              2,
            )}
          </code>
        </div>

        <div className="event-ladder" aria-label="Band event ladder">
          {eventRows(workspace.agent_activity, completed).map((event) => (
            <article className="event-step" key={`${event.title}-${event.detail}`}>
              <span>{event.index}</span>
              <div>
                <strong>{event.title}</strong>
                <p>{event.detail}</p>
              </div>
              <ArrowRight />
            </article>
          ))}
        </div>
      </aside>
    </section>
  );
}

function PixelAgent({ agent, run, index }: { agent: TheaterAgent; run?: AgentActivity; index: number }) {
  const status = run?.status_label ?? "Queued";
  const delay = `${index * 0.22}s`;
  return (
    <article
      className={`pixel-agent ${agent.tone}`}
      style={{ left: `${agent.x}%`, top: `${agent.y}%`, "--agent-delay": delay } as CSSProperties}
      aria-label={`${agent.name} agent at ${agent.station}`}
    >
      <div className="sprite-body" aria-hidden="true">
        <span className="sprite-head" />
        <span className="sprite-torso" />
        <span className="sprite-leg left" />
        <span className="sprite-leg right" />
      </div>
      <div className="agent-speech">
        <strong>{agent.name}</strong>
        <span>{agent.payload}</span>
      </div>
      <small>{status}</small>
    </article>
  );
}

function ProofStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="proof-stat">
      <small>{label}</small>
      <strong>{value}</strong>
    </div>
  );
}

function eventRows(agents: AgentActivity[], completed: number) {
  const fallback = [
    ["Intake posts facts", "Applicant facts enter the shared Band room."],
    ["Evidence claims tasks", "Missing documents become assigned work."],
    ["Sources attach law", "Official rules and source snippets join the case."],
    ["Risk stamps flags", "Salary and permit risks are reviewed before packet output."],
    ["Packet prints", "The AI case packet becomes ready to inspect."],
  ];
  const source = agents.length
    ? agents.map((agent) => [agent.name, agent.summary || agent.next_action])
    : fallback;

  return source.slice(0, 6).map(([title, detail], index) => ({
    index: `${String(index + 1).padStart(2, "0")}`,
    title,
    detail: index < completed ? detail : detail,
  }));
}

function shortRoom(roomId: string): string {
  if (roomId.length <= 18) return roomId;
  return `${roomId.slice(0, 8)}...${roomId.slice(-4)}`;
}
