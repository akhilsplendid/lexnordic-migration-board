export type BusyAction = "loading" | "upload" | "document-request" | "agent-run" | "approve" | null;

export type SectionId = "chat" | "matter" | "route" | "evidence" | "agents" | "theater" | "review";

export type StageId = "intake" | "evidence" | "agent_review" | "packet_final";

export type SidePanelKind = "notifications" | "profile";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  metadata?: ChatMessageMetadata;
  createdAt: string;
};

export type ChatMessageMetadata = {
  mode?: string;
  addressed_agent?: string | null;
  agent_trace?: ChatAgentTraceStep[];
  agentTrace?: ChatAgentTraceStep[];
  route_results?: PermitMatchResult[];
  routeResults?: PermitMatchResult[];
  source_bundle?: Array<{ title: string; url?: string; citation?: string }>;
};

export type ChatAgentTraceStep = {
  id: string;
  agentRole: string;
  agentName: string;
  provider: "aiml" | "featherless" | "manual" | string;
  status: "queued" | "running" | "completed" | "blocked";
  isFocus?: boolean;
  summary: string;
  output: string;
  nextAction: string;
  citations?: string[];
};

export type AgentChatStreamEvent =
  | {
      event: "started" | "trace" | "answering";
      data: {
        message?: string;
        phase?: string;
        step?: ChatAgentTraceStep;
        agentTrace: ChatAgentTraceStep[];
      };
    }
  | {
      event: "complete";
      data: {
        session: ConsultationSession;
        assistantMessage?: ChatMessage;
        agentTrace: ChatAgentTraceStep[];
        routeResults: PermitMatchResult[];
      };
    }
  | {
      event: "error";
      data: {
        message: string;
      };
    };

export type ConsultationSession = {
  id: string;
  title: string;
  query: string;
  matterNumber?: string;
  routeId?: string;
  routeName?: string;
  readiness?: number;
  documentCount?: number;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
};

export type MatterSummary = {
  id: string;
  matter_number: string;
  title: string;
  status: string;
  route_id?: string | null;
  route_label?: string | null;
  readiness_score: number;
  document_count: number;
  created_at?: string | null;
  updated_at?: string | null;
};

export type EvidenceItem = {
  id: string;
  group: string;
  requirement: string;
  document_type: string;
  status_label: string;
  status_class: string;
  basis: string;
  risk_level: string;
  risk_class: string;
  agent_name: string;
  action_label: string;
};

export type SourceRef = {
  id: string;
  title: string;
  citation?: string | null;
  url?: string | null;
  source_type?: string | null;
  snippet?: string | null;
};

export type AgentActivity = {
  agent_role: string;
  name: string;
  status: string;
  status_label: string;
  model_provider?: string | null;
  confidence?: number | null;
  summary: string;
  next_action: string;
};

export type WorkspaceDocument = {
  id: string;
  filename: string;
  document_type: string;
  content_type?: string | null;
  size_bytes?: number | null;
};

export type Workspace = {
  matter: {
    id?: string;
    matter_number: string;
    title?: string;
    status?: string;
    route: string;
    route_id?: string;
    state_label: string;
    applicant_alias: string;
    employer_name?: string | null;
    summary?: string | null;
    band_room_id?: string | null;
    qdrant_collection?: string | null;
  };
  readiness: {
    score: number;
    blocker_count: number;
    applicant_next_step: string;
    packet_gate: {
      threshold: number;
      state: "locked" | "unlocked";
      label: string;
    };
  };
  known_facts: string[];
  missing_facts: string[];
  evidence_items: EvidenceItem[];
  documents: WorkspaceDocument[];
  source_bundle: SourceRef[];
  extraction_feed: {
    status: string;
    progress: number;
    message: string;
    fields: string[];
  };
  agent_activity: AgentActivity[];
  review_packet: {
    version_no?: number;
    status: string;
    summary: string;
    applicant_message?: string;
    document_checklist?: string[];
    next_actions: string[];
  };
  backend_warning?: string;
};

export type EvidenceGroups = {
  verified: EvidenceItem[];
  review: EvidenceItem[];
  blocking: EvidenceItem[];
};

export type PermitRoute = {
  route_id: string;
  family: string;
  phase: string;
  name: string;
  summary: string;
  tags: string[];
  required_facts: Array<{ key: string; label: string; reason: string }>;
  required_evidence: Array<{ key: string; label: string; reason: string }>;
  risk_flags: string[];
  sources: Array<{ title: string; url: string }>;
  agent_path: string[];
};

export type PermitMatchResult = {
  route: PermitRoute;
  match_score: number;
  matched_signals: string[];
  readiness: {
    score: number;
    status: string;
    autonomous_output: string;
    packet_gate: string;
  };
  present_evidence: Array<{ key: string; label: string; reason: string }>;
  missing_evidence: Array<{ key: string; label: string; reason: string }>;
  missing_facts: Array<{ key: string; label: string; reason: string }>;
  risk_flags: string[];
  next_questions: string[];
  source_bundle: Array<{ title: string; url: string }>;
};
