import { useEffect, useMemo, useState } from "react";

import {
  appendSessionMessages,
  createConsultationSession,
  listConsultationSessions,
  sendConsultationChat,
  sendConsultationChatStream,
  updateConsultationSession,
} from "../api/workspaceApi";
import type { AgentChatStreamEvent, ChatMessage, ConsultationSession, MatterSummary } from "../types";

export function useConsultationSessions(authToken: string | null) {
  const [sessions, setSessions] = useState<ConsultationSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(Boolean(authToken));
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    if (!authToken) {
      setSessions([]);
      setActiveSessionId(undefined);
      setIsLoading(false);
      return;
    }

    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const listed = await listConsultationSessions(authToken);
        let nextSessions = normalizeSessions(listed.sessions);
        if (!nextSessions.length) {
          const created = await createConsultationSession({ title: "New consultation" }, authToken);
          nextSessions = normalizeSessions([created.session]);
        }
        if (cancelled) return;
        setSessions(nextSessions);
        setActiveSessionId((current) =>
          current && nextSessions.some((session) => session.id === current) ? current : nextSessions[0]?.id,
        );
      } catch (caught) {
        if (!cancelled) setError(messageFrom(caught));
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [authToken]);

  useEffect(() => {
    if (sessions.length && !sessions.some((session) => session.id === activeSessionId)) {
      setActiveSessionId(sessions[0].id);
    }
  }, [activeSessionId, sessions]);

  const activeSession = useMemo(
    () => sessions.find((session) => session.id === activeSessionId) ?? sessions[0],
    [activeSessionId, sessions],
  );

  async function createSession(initial?: Partial<ConsultationSession>) {
    if (!authToken) throw new Error("Supabase sign-in required");
    const created = await createConsultationSession(
      {
        title: initial?.title ?? "New consultation",
        query: initial?.query ?? "",
      },
      authToken,
    );
    const session = normalizeSession({ ...created.session, messages: initial?.messages ?? created.session.messages });
    setSessions((current) => [session, ...current]);
    setActiveSessionId(session.id);
    return session;
  }

  function updateSession(sessionId: string, patch: Partial<ConsultationSession>) {
    setSessions((current) =>
      current.map((session) =>
        session.id === sessionId ? { ...session, ...patch, updatedAt: new Date().toISOString() } : session,
      ),
    );
  }

  function updateActiveSession(patch: Partial<ConsultationSession>) {
    const target = activeSession;
    if (!target) return;
    updateSession(target.id, patch);
  }

  async function persistSession(sessionId: string, patch: Partial<ConsultationSession>) {
    if (!authToken) throw new Error("Supabase sign-in required");
    updateSession(sessionId, patch);
    const updated = await updateConsultationSession(
      sessionId,
      {
        title: patch.title,
        query: patch.query,
        route_id: patch.routeId,
        route_label: patch.routeName,
        readiness_score: patch.readiness,
      },
      authToken,
    );
    updateSession(sessionId, normalizeSession(updated.session));
  }

  async function appendMessagesToSession(sessionId: string, messages: ChatMessage[]) {
    if (!authToken) throw new Error("Supabase sign-in required");
    setSessions((current) =>
      current.map((session) =>
        session.id === sessionId
          ? {
              ...session,
              messages: [...session.messages, ...messages],
              updatedAt: new Date().toISOString(),
            }
          : session,
      ),
    );
    const saved = await appendSessionMessages(
      sessionId,
      messages.map((message) => ({ role: message.role, text: message.text })),
      authToken,
    );
    updateSession(sessionId, normalizeSession(saved.session));
  }

  async function sendAgentChat(
    sessionId: string,
    request: { message: string; facts: Record<string, unknown>; documents: string[] },
    onStreamEvent?: (event: AgentChatStreamEvent) => void,
  ) {
    if (!authToken) throw new Error("Supabase sign-in required");
    const response = onStreamEvent
      ? await sendConsultationChatStream(sessionId, request, authToken, onStreamEvent)
      : await sendConsultationChat(sessionId, request, authToken);
    updateSession(sessionId, normalizeSession(response.session));
    return response;
  }

  function attachMatter(sessionId: string, matter: MatterSummary) {
    updateSession(sessionId, {
      matterNumber: matter.matter_number,
      title: matter.title,
      routeName: matter.route_label ?? undefined,
      readiness: matter.readiness_score,
      documentCount: matter.document_count,
    });
  }

  return {
    activeSession,
    activeSessionId,
    error,
    isLoading,
    sessions,
    appendMessages: appendMessagesToSession,
    attachMatter,
    createSession,
    persistSession,
    selectSession: setActiveSessionId,
    sendAgentChat,
    updateActiveSession,
    updateSession,
  };
}

export function makeChatMessage(role: ChatMessage["role"], text: string): ChatMessage {
  return {
    id: newId(),
    role,
    text,
    createdAt: new Date().toISOString(),
  };
}

function normalizeSessions(sessions: ConsultationSession[]): ConsultationSession[] {
  return sessions.map(normalizeSession);
}

function normalizeSession(session: ConsultationSession): ConsultationSession {
  return {
    ...session,
    query: session.query ?? "",
    title: session.title || "New consultation",
    messages: session.messages ?? [],
  };
}

function newId(): string {
  return globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function messageFrom(caught: unknown): string {
  return caught instanceof Error ? caught.message : "Unable to load consultation sessions";
}
