import {
  ArrowRight,
  Activity,
  Bot,
  CheckCircle2,
  FileText,
  FolderKanban,
  MessageSquareText,
  RadioTower,
  Route,
  ShieldCheck,
  Workflow,
} from "lucide-react";

import { StatusPill } from "../components/StatusPill";
import type { usePermitMatcher } from "../hooks/usePermitMatcher";
import type { ChatAgentTraceStep, ChatMessage, ConsultationSession, PermitMatchResult, Workspace } from "../types";

type Matcher = ReturnType<typeof usePermitMatcher>;

const PROMPTS = [
  "I finished higher education in Sweden and found a job",
  "My Swedish migration decision was rejected and I need to appeal",
  "I want to move to Sweden for work with a job offer",
  "I want to live with my partner or family in Sweden",
];

const FOCUS_PROMPTS = [
  { label: "Documents", prompt: "What documents should I prepare first for my situation?" },
  { label: "Risks", prompt: "What could make my case sensitive or time critical?" },
  { label: "Sources", prompt: "Which official source should I rely on for this route?" },
  { label: "Packet", prompt: "What would go into my private case packet?" },
];

const CONSULTATION_CHECKS = [
  {
    id: "route",
    label: "Route",
    roles: ["decision_parser"],
    fallback: "Identifies the likely permit or appeal route.",
  },
  {
    id: "documents",
    label: "Documents",
    roles: ["evidence"],
    fallback: "Lists the evidence the user should collect next.",
  },
  {
    id: "sources",
    label: "Sources",
    roles: ["legal_source"],
    fallback: "Links the answer to official migration-law sources.",
  },
  {
    id: "risks",
    label: "Risks",
    roles: ["conflict_kyc", "risk"],
    fallback: "Flags urgency, sensitivity, and missing facts.",
  },
  {
    id: "packet",
    label: "Packet",
    roles: ["appeal_packet", "partner_review"],
    fallback: "Checks whether the consultation is ready for a case packet.",
  },
];

export function ChatPage({
  matcher,
  session,
  workspace,
  isCreatingMatter,
  isChatting,
  liveAgentTrace,
  messages,
  chatError,
  onAnalyze,
  onQueryChange,
  onOpenMatter,
  onOpenEvidence,
  onOpenRoute,
}: {
  matcher: Matcher;
  session: ConsultationSession;
  workspace: Workspace;
  isCreatingMatter: boolean;
  isChatting: boolean;
  liveAgentTrace: ChatAgentTraceStep[];
  messages: ChatMessage[];
  chatError: string | null;
  onAnalyze: () => void;
  onQueryChange: (query: string) => void;
  onOpenMatter: () => void;
  onOpenEvidence: () => void;
  onOpenRoute: () => void;
}) {
  const primary = matcher.results[0];
  const sources = sourceRows(primary, workspace);

  return (
    <section className="page-grid chat-page" aria-label="LexNordic intake chat">
      <section className="chat-panel" aria-labelledby="chat-heading">
        <div className="chat-panel-header">
          <div>
            <span className="section-kicker">New consultation</span>
            <h2 id="chat-heading">Tell LexNordic what you need</h2>
          </div>
          <div className="chat-status-stack">
            <StatusPill tone="active" icon={<ShieldCheck />}>
              AI consultation active
            </StatusPill>
            <StatusPill tone="ready" icon={<RadioTower />}>
              Proof available
            </StatusPill>
          </div>
        </div>

        <div className="consultation-flow-strip" aria-label="Consultation workflow">
          {["Chat", "Route", "Documents", "Sources", "Packet"].map((step, index) => (
            <span className={index === 0 ? "active" : ""} key={step}>
              <Workflow />
              {step}
            </span>
          ))}
        </div>

        <div className="chat-thread" aria-label="Conversation">
          <article className="chat-message assistant">
            <div className="chat-avatar">
              <Bot />
            </div>
            <div>
              <strong>LexNordic</strong>
              <p>
                Describe your Swedish migration situation in normal language. I will identify likely routes, ask for
                missing facts, point to sources, and keep your documents organized in a private workspace.
              </p>
            </div>
          </article>

          {messages.map((message) => (
            <article className={`chat-message ${message.role}`} key={message.id}>
              {message.role === "assistant" && (
                <div className="chat-avatar">
                  <Bot />
                </div>
              )}
              <div>
                <strong>{message.role === "user" ? "You" : assistantLabel(message)}</strong>
                <p>{message.text}</p>
                {message.role === "assistant" && agentTrace(message).length > 0 && (
                  <WorkDisclosure trace={agentTrace(message)} />
                )}
              </div>
            </article>
          ))}

          {isChatting && (
            <article className="chat-message assistant active-agent-turn">
              <div className="chat-avatar">
                <Bot />
              </div>
              <div>
                <strong>LexNordic is checking your question</strong>
                <p>Route, documents, sources, risks, and packet readiness are being checked.</p>
                <ConsultationChecks trace={liveAgentTrace} live />
                {liveAgentTrace.length > 0 && (
                  <details className="chat-work-disclosure live">
                    <summary>
                      <span>
                        <strong>Show live proof</strong>
                        <small>Internal coordination trace for judges</small>
                      </span>
                      <span className="work-count-pill">{completedCount(liveAgentTrace)}/{liveAgentTrace.length}</span>
                    </summary>
                    <AgentTrace trace={liveAgentTrace} live />
                  </details>
                )}
              </div>
            </article>
          )}

          {!messages.length && !isChatting && (
            <article className="chat-message assistant">
              <div className="chat-avatar">
                <Route />
              </div>
              <div>
                <strong>Route screening</strong>
                <p>Ask a question or choose a starting point to begin this consultation session.</p>
              </div>
            </article>
          )}
        </div>

        <div className="prompt-grid" aria-label="Common starting points">
          {PROMPTS.map((prompt) => (
            <button className="prompt-chip" type="button" key={prompt} onClick={() => onQueryChange(prompt)}>
              {prompt}
            </button>
          ))}
        </div>

        <div className="agent-prompt-strip" aria-label="Focused consultation prompts">
          {FOCUS_PROMPTS.map((prompt) => (
            <button className="agent-prompt-chip" type="button" key={prompt.label} onClick={() => onQueryChange(prompt.prompt)}>
              <Activity />
              <span>{prompt.label}</span>
            </button>
          ))}
        </div>

        <div className="chat-composer">
          <label>
            <span className="sr-only">Describe your migration situation</span>
            <textarea
              value={matcher.query}
              onChange={(event) => onQueryChange(event.currentTarget.value)}
              rows={4}
              placeholder="Ask a follow-up, describe a change, or tell LexNordic what document you have..."
            />
          </label>
          {(matcher.error || chatError) && <p className="route-error">{chatError ?? matcher.error}</p>}
          <div className="chat-actions">
            <button className="primary-action" type="button" onClick={onAnalyze} disabled={isChatting || !matcher.query.trim()}>
              <MessageSquareText />
              <span>{isChatting ? "Checking" : "Send"}</span>
            </button>
            <button className="secondary-action" type="button" onClick={onOpenMatter} disabled={isCreatingMatter}>
              <FolderKanban />
              <span>{isCreatingMatter ? "Creating workspace" : session.matterNumber ? "Open workspace" : "Create workspace"}</span>
            </button>
          </div>
        </div>
      </section>

      <aside className="case-builder-panel" aria-label="Case builder">
        <div className="case-builder-card case-status-card">
          <span className="section-kicker">Case builder</span>
          <h2>{primary?.route.name ?? session.routeName ?? workspace.matter.route}</h2>
          <p>{primary?.route.summary ?? (session.query || "Start with a question and LexNordic will build the route plan.")}</p>
          <div className="case-score-row">
            <div>
              <small>Route match</small>
              <strong>{primary ? `${primary.match_score}%` : session.routeName ? "Saved" : "--"}</strong>
            </div>
            <div>
              <small>Readiness</small>
              <strong>{primary ? `${primary.readiness.score}%` : `${session.readiness ?? workspace.readiness.score}%`}</strong>
            </div>
          </div>
        </div>

        <div className="case-builder-card">
          <div className="panel-header">
            <span className="section-kicker">Next questions</span>
            <CheckCircle2 />
          </div>
          <ul className="compact-list">
            {(primary?.next_questions.length ? primary.next_questions : workspace.missing_facts).slice(0, 4).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="case-builder-card">
          <div className="panel-header">
            <span className="section-kicker">Documents to collect</span>
            <FileText />
          </div>
          <ul className="compact-list">
            {(primary?.missing_evidence.length
              ? primary.missing_evidence.map((item) => item.label)
              : workspace.evidence_items
                  .filter((item) => ["missing", "warning", "active"].includes(item.status_class))
                  .map((item) => item.requirement)
            )
              .slice(0, 5)
              .map((item) => (
                <li key={item}>{item}</li>
              ))}
          </ul>
          <button className="text-action full" type="button" onClick={onOpenEvidence}>
            <span>Open evidence checklist</span>
            <ArrowRight />
          </button>
        </div>

        <div className="case-builder-card">
          <div className="panel-header">
            <span className="section-kicker">Legal sources</span>
            <Route />
          </div>
          <div className="source-mini-list">
            {sources.slice(0, 3).map((source) => (
              <button className="mini-source-row" type="button" key={`${source.title}-${source.detail}`} onClick={onOpenRoute}>
                <span>{source.title}</span>
                <small>{source.detail}</small>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </section>
  );
}

function agentTrace(message: ChatMessage): ChatAgentTraceStep[] {
  return message.metadata?.agentTrace ?? message.metadata?.agent_trace ?? [];
}

function assistantLabel(message: ChatMessage): string {
  const addressed = message.metadata?.addressed_agent;
  if (!addressed) return "LexNordic";
  return focusLabel(addressed);
}

function focusLabel(role: string): string {
  return (
    {
      intake: "LexNordic intake",
      conflict_kyc: "LexNordic risk check",
      decision_parser: "LexNordic route check",
      legal_source: "LexNordic source check",
      evidence: "LexNordic document check",
      risk: "LexNordic risk check",
      appeal_packet: "LexNordic packet check",
      partner_review: "LexNordic final check",
    }[role] ?? "LexNordic"
  );
}

function WorkDisclosure({ trace }: { trace: ChatAgentTraceStep[] }) {
  if (!trace.length) return null;
  return (
    <details className="chat-work-disclosure">
      <summary>
        <span>
          <strong>Show how this was checked</strong>
          <small>Route, documents, sources, risk, and packet readiness</small>
        </span>
        <span className="work-count-pill">{completedCount(trace)}/{trace.length}</span>
      </summary>
      <ConsultationChecks trace={trace} />
      <details className="judge-trace-disclosure">
        <summary>Judge proof: full Band trace</summary>
        <AgentTrace trace={trace} />
      </details>
    </details>
  );
}

function ConsultationChecks({ trace, live = false }: { trace: ChatAgentTraceStep[]; live?: boolean }) {
  const checks = CONSULTATION_CHECKS.map((check) => {
    const steps = trace.filter((step) => check.roles.includes(step.agentRole));
    const active = steps.find((step) => step.status === "running") ?? steps[0];
    const status = steps.length && steps.every((step) => step.status === "completed")
      ? "checked"
      : steps.some((step) => step.status === "running" || step.status === "completed")
        ? "checking"
        : live
          ? "queued"
          : "pending";
    return {
      ...check,
      status,
      detail: active?.summary ?? check.fallback,
    };
  });

  return (
    <div className={`consultation-check-grid ${live ? "live" : ""}`} aria-label="Consultation checks">
      {checks.map((check) => (
        <div className={`consultation-check ${check.status}`} key={check.id}>
          <CheckCircle2 />
          <span>{check.label}</span>
          <small>{check.detail}</small>
        </div>
      ))}
    </div>
  );
}

function completedCount(trace: ChatAgentTraceStep[]): number {
  return trace.filter((step) => step.status === "completed").length;
}

function AgentTrace({ trace, live = false }: { trace: ChatAgentTraceStep[]; live?: boolean }) {
  if (!trace.length) return null;
  return (
    <div className={`chat-agent-trace ${live ? "live" : ""}`} aria-label="Internal Band work trace">
      <div className="chat-agent-trace-header">
        <span>{live ? "Working now" : "Band coordination trace"}</span>
        <small>{completedCount(trace)}/{trace.length} complete</small>
      </div>
      <div className="chat-agent-steps">
        {trace.map((step, index) => (
          <div className={`chat-agent-step ${step.status} ${step.isFocus ? "focus" : ""}`} key={step.id}>
            <div className="agent-step-index">{String(index + 1).padStart(2, "0")}</div>
            <div className="agent-step-copy">
              <strong>{step.agentName}</strong>
              <span>{step.summary}</span>
              <p>{step.output}</p>
              {step.citations?.length ? <small>Sources: {step.citations.join(", ")}</small> : null}
            </div>
            <div className="agent-step-provider">{step.provider}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function sourceRows(result: PermitMatchResult | undefined, workspace: Workspace): Array<{ title: string; detail: string }> {
  if (result?.source_bundle.length) {
    return result.source_bundle.map((source) => ({ title: source.title, detail: "Official source" }));
  }
  return workspace.source_bundle.map((source) => ({
    title: source.title,
    detail: source.citation ?? "Source attached",
  }));
}
