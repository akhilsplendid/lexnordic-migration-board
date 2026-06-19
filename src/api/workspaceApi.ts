import { API_BASE_URL } from "../config";
import type {
  AgentChatStreamEvent,
  ChatAgentTraceStep,
  ChatMessage,
  ConsultationSession,
  EvidenceItem,
  MatterSummary,
  PermitMatchResult,
  Workspace,
} from "../types";

type PermitMatchRequest = {
  query: string;
  facts: Record<string, unknown>;
  documents: string[];
  limit?: number;
};

type CreateMatterRequest = {
  consultation_session_id?: string;
  title?: string;
  initial_query?: string;
  route_id?: string;
  route_label?: string;
};

type CreateSessionRequest = {
  title?: string;
  query?: string;
};

type UpdateSessionRequest = {
  title?: string;
  query?: string;
  route_id?: string;
  route_label?: string;
  readiness_score?: number;
};

type AgentChatRequest = {
  message: string;
  facts: Record<string, unknown>;
  documents: string[];
};

export type AgentChatResponse = {
  session: ConsultationSession;
  assistantMessage?: ChatMessage;
  agentTrace: ChatAgentTraceStep[];
  routeResults: PermitMatchResult[];
};

export async function requestWorkspace(path: string, authToken: string | null): Promise<Workspace> {
  return requestJson<Workspace>(path, undefined, authToken);
}

export async function postWorkspace(path: string, authToken: string | null): Promise<Workspace> {
  const payload = await requestJson<Workspace | { workspace: Workspace }>(path, { method: "POST" }, authToken);
  return "workspace" in payload ? payload.workspace : payload;
}

export async function uploadWorkspaceDocument(
  matterNumber: string,
  file: File,
  documentType: string,
  authToken: string | null,
): Promise<Workspace> {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("file", file);
  return requestJson<Workspace>(`/matters/${matterNumber}/documents`, {
    method: "POST",
    body: formData,
  }, authToken);
}

export async function listMatterSessions(authToken: string | null): Promise<{ matters: MatterSummary[] }> {
  return requestJson("/matters", undefined, authToken);
}

export async function createMatterSession(request: CreateMatterRequest, authToken: string | null): Promise<{
  matter: MatterSummary;
  workspace: Workspace;
}> {
  return requestJson("/matters", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  }, authToken);
}

export async function listConsultationSessions(authToken: string | null): Promise<{ sessions: ConsultationSession[] }> {
  return requestJson("/sessions", undefined, authToken);
}

export async function createConsultationSession(
  request: CreateSessionRequest,
  authToken: string | null,
): Promise<{ session: ConsultationSession }> {
  return requestJson("/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  }, authToken);
}

export async function updateConsultationSession(
  sessionId: string,
  request: UpdateSessionRequest,
  authToken: string | null,
): Promise<{ session: ConsultationSession }> {
  return requestJson(`/sessions/${sessionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  }, authToken);
}

export async function appendSessionMessages(
  sessionId: string,
  messages: Array<Pick<ChatMessage, "role" | "text">>,
  authToken: string | null,
): Promise<{ session: ConsultationSession }> {
  return requestJson(`/sessions/${sessionId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages }),
  }, authToken);
}

export async function sendConsultationChat(
  sessionId: string,
  request: AgentChatRequest,
  authToken: string | null,
): Promise<AgentChatResponse> {
  return requestJson(`/sessions/${sessionId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  }, authToken);
}

export async function sendConsultationChatStream(
  sessionId: string,
  request: AgentChatRequest,
  authToken: string | null,
  onEvent: (event: AgentChatStreamEvent) => void,
): Promise<AgentChatResponse> {
  const headers = new Headers({ "Content-Type": "application/json" });
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }
  const response = await fetch(`${API_BASE_URL}/sessions/${sessionId}/chat/stream`, {
    method: "POST",
    headers,
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  if (!response.body) {
    throw new Error("Streaming response was not available");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResponse: AgentChatResponse | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.replace(/\r\n/g, "\n").split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const event = parseStreamEvent(part);
      if (!event) continue;
      onEvent(event);
      if (event.event === "error") {
        throw new Error(event.data.message);
      }
      if (event.event === "complete") {
        finalResponse = event.data;
      }
    }
  }

  if (buffer.trim()) {
    const event = parseStreamEvent(buffer.replace(/\r\n/g, "\n"));
    if (event) {
      onEvent(event);
      if (event.event === "error") {
        throw new Error(event.data.message);
      }
      if (event.event === "complete") {
        finalResponse = event.data;
      }
    }
  }

  if (!finalResponse) {
    throw new Error("Consultation stream ended before completion");
  }
  return finalResponse;
}

export async function listPermitRoutes(): Promise<{
  count: number;
  families: string[];
}> {
  return requestJson("/permits/routes");
}

export async function matchPermitRoutes(request: PermitMatchRequest): Promise<{
  query: string;
  results: PermitMatchResult[];
}> {
  return requestJson("/permits/match", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, limit: request.limit ?? 4 }),
  });
}

export function requestDocumentTypeForEvidence(item: EvidenceItem | undefined): string {
  return item?.document_type && item.document_type !== "other" ? item.document_type : "employment_contract";
}

function parseStreamEvent(block: string): AgentChatStreamEvent | null {
  let eventName = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      eventName = line.slice("event:".length).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice("data:".length).trimStart());
    }
  }
  if (!dataLines.length) return null;
  const data = JSON.parse(dataLines.join("\n")) as AgentChatStreamEvent["data"];
  if (eventName === "started" || eventName === "trace" || eventName === "answering") {
    return { event: eventName, data } as AgentChatStreamEvent;
  }
  if (eventName === "complete") {
    return { event: "complete", data } as AgentChatStreamEvent;
  }
  if (eventName === "error") {
    return { event: "error", data } as AgentChatStreamEvent;
  }
  return null;
}

async function requestJson<T>(path: string, init?: RequestInit, authToken?: string | null): Promise<T> {
  const headers = new Headers(init?.headers);
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}
