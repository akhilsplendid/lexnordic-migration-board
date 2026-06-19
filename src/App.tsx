import { useEffect, useMemo, useRef, useState } from "react";

import { createMatterSession, requestDocumentTypeForEvidence } from "./api/workspaceApi";
import { ActionToast } from "./components/ActionToast";
import { AuthGate } from "./components/AuthGate";
import { MatterHeader } from "./components/MatterHeader";
import { RailNavigation } from "./components/RailNavigation";
import { SideDrawer } from "./components/SideDrawer";
import { StageBoard } from "./components/StageBoard";
import { WorkspaceNotice } from "./components/WorkspaceNotice";
import { MATTER_NUMBER } from "./config";
import { useAuthSession } from "./hooks/useAuthSession";
import { useConsultationSessions } from "./hooks/useConsultationSessions";
import { usePermitMatcher } from "./hooks/usePermitMatcher";
import { useWorkspace } from "./hooks/useWorkspace";
import { AgentsPage } from "./pages/AgentsPage";
import { ChatPage } from "./pages/ChatPage";
import { EvidencePage } from "./pages/EvidencePage";
import { MatterPage } from "./pages/MatterPage";
import { ReviewPage } from "./pages/ReviewPage";
import { RoutePage } from "./pages/RoutePage";
import { TheaterPage } from "./pages/TheaterPage";
import type { AgentChatStreamEvent, ChatAgentTraceStep, EvidenceItem, SectionId, SidePanelKind } from "./types";
import { pageFromHash, pageFromStage, setPageHash, stageFromPage } from "./utils/navigation";
import { groupEvidence } from "./utils/workspace";

const PAGE_DOCUMENT_TITLES: Record<SectionId, string> = {
  chat: "Chat",
  matter: "Matter",
  route: "Route",
  evidence: "Evidence",
  agents: "Agents",
  theater: "Theater",
  review: "Packet",
};

export function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const auth = useAuthSession();
  const sessionsState = useConsultationSessions(auth.accessToken);
  const activeMatterNumber = sessionsState.activeSession?.matterNumber ?? MATTER_NUMBER;
  const { workspace, busyAction, error, notice, isBusy, clearNotice, loadWorkspace, postWorkspace, uploadFile } =
    useWorkspace(activeMatterNumber, auth.accessToken, Boolean(auth.accessToken));
  const permitMatcher = usePermitMatcher();
  const [activeSection, setActiveSection] = useState<SectionId>(() => pageFromHash(window.location.hash));
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [sidePanel, setSidePanel] = useState<SidePanelKind | null>(null);
  const [sessionAction, setSessionAction] = useState<"create-matter" | null>(null);
  const [chatAgentTrace, setChatAgentTrace] = useState<ChatAgentTraceStep[]>([]);
  const [isChatting, setIsChatting] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const groupedEvidence = useMemo(() => groupEvidence(workspace.evidence_items), [workspace.evidence_items]);
  const gateUnlocked = workspace.readiness.packet_gate.state === "unlocked";

  const selectedEvidence = useMemo(
    () => selectEvidence(workspace.evidence_items, selectedEvidenceId),
    [selectedEvidenceId, workspace.evidence_items],
  );
  const selectedSource = useMemo(
    () => workspace.source_bundle.find((source) => source.id === selectedSourceId) ?? workspace.source_bundle[0],
    [selectedSourceId, workspace.source_bundle],
  );

  useEffect(() => {
    if (!selectedEvidenceId && workspace.evidence_items.length) {
      setSelectedEvidenceId(selectDefaultEvidence(workspace.evidence_items).id);
    }
  }, [selectedEvidenceId, workspace.evidence_items]);

  useEffect(() => {
    if (!selectedSourceId && workspace.source_bundle.length) {
      setSelectedSourceId(workspace.source_bundle[0].id);
    }
  }, [selectedSourceId, workspace.source_bundle]);

  const activeStage = stageFromPage(activeSection);

  useEffect(() => {
    const syncPageFromLocation = () => setActiveSection(pageFromHash(window.location.hash));
    window.addEventListener("hashchange", syncPageFromLocation);
    window.addEventListener("popstate", syncPageFromLocation);
    if (!window.location.hash) setPageHash("chat");

    return () => {
      window.removeEventListener("hashchange", syncPageFromLocation);
      window.removeEventListener("popstate", syncPageFromLocation);
    };
  }, []);

  useEffect(() => {
    document.title = `${PAGE_DOCUMENT_TITLES[activeSection]} | LexNordic Migration Board`;
    window.scrollTo({ top: 0, left: 0 });
  }, [activeSection]);

  useEffect(() => {
    if (activeSection === "chat") {
      permitMatcher.reset();
      permitMatcher.setQuery(sessionsState.activeSession?.query ?? "");
    }
  }, [activeSection, sessionsState.activeSession?.id]);

  function navigate(page: SectionId) {
    setActiveSection(page);
    setPageHash(page);
  }

  async function createNewSession() {
    await sessionsState.createSession();
    permitMatcher.reset();
    navigate("chat");
  }

  function selectSession(sessionId: string) {
    sessionsState.selectSession(sessionId);
    navigate("chat");
  }

  function updateChatQuery(query: string) {
    permitMatcher.setQuery(query);
    sessionsState.updateActiveSession({ query });
  }

  async function analyzeActiveSession() {
    const session = sessionsState.activeSession;
    const query = permitMatcher.query.trim();
    if (!session || !query) return;

    setIsChatting(true);
    setChatError(null);
    setChatAgentTrace(pendingAgentTrace(query));
    try {
      const response = await sessionsState.sendAgentChat(session.id, {
        message: query,
        facts: permitMatcher.requestFacts,
        documents: permitMatcher.documents,
      }, handleChatStreamEvent);
      setChatAgentTrace(response.agentTrace);
      permitMatcher.applyResults(query, response.routeResults);
      permitMatcher.setQuery("");
    } catch (caught) {
      setChatError(caught instanceof Error ? caught.message : "Unable to run agent consultation");
    } finally {
      setIsChatting(false);
    }
  }

  function handleChatStreamEvent(event: AgentChatStreamEvent) {
    if (event.event === "started" || event.event === "trace" || event.event === "answering") {
      setChatAgentTrace(event.data.agentTrace);
    }
    if (event.event === "complete") {
      setChatAgentTrace(event.data.agentTrace);
    }
  }

  async function openSessionWorkspace() {
    const session = sessionsState.activeSession;
    if (!session) return;
    if (session.matterNumber) {
      navigate("matter");
      return;
    }

    setSessionAction("create-matter");
    try {
      const primary = permitMatcher.results[0];
      const created = await createMatterSession({
        consultation_session_id: session.id,
        title: primary?.route.name ?? session.title,
        initial_query: session.query || permitMatcher.query,
        route_id: primary?.route.route_id,
        route_label: primary?.route.name,
      }, auth.accessToken);
      sessionsState.attachMatter(session.id, created.matter);
      navigate("matter");
    } finally {
      setSessionAction(null);
    }
  }

  function handleEvidenceSelect(item: EvidenceItem) {
    setSelectedEvidenceId(item.id);
    navigate("evidence");
  }

  function handleSourceSelect(sourceId: string) {
    setSelectedSourceId(sourceId);
    navigate("review");
  }

  const generateDocumentRequest = () =>
    void postWorkspace(`/matters/${activeMatterNumber}/document-request`, "document-request");
  const uploadSelectedEvidence = () => fileInputRef.current?.click();
  const runAgentReview = () => void postWorkspace(`/matters/${activeMatterNumber}/agent-room/run-demo`, "agent-run");
  const approveReview = () => void postWorkspace(`/matters/${activeMatterNumber}/review/approve`, "approve");

  if (auth.isLoading || !auth.user || !auth.accessToken) {
    return (
      <AuthGate
        error={auth.error}
        isConfigured={auth.isConfigured}
        isLoading={auth.isLoading}
        message={auth.message}
        onSignIn={auth.signIn}
        onSignUp={auth.signUp}
      />
    );
  }

  if (sessionsState.isLoading || !sessionsState.activeSession) {
    return (
      <main className="auth-shell">
        <section className="auth-panel" aria-label="Preparing workspace">
          <div className="brand-lockup auth-brand">
            <div className="brand-mark">LN</div>
            <div>
              <strong>LexNordic</strong>
              <span>Migration Board</span>
            </div>
          </div>
          <div className="auth-copy">
            <span className="section-kicker">Secure client workspace</span>
            <h1>Preparing your consultations</h1>
            <p>Loading your matter sessions and protected chat history.</p>
          </div>
          {sessionsState.error && <p className="auth-error">{sessionsState.error}</p>}
        </section>
      </main>
    );
  }

  const activeSession = sessionsState.activeSession;

  return (
    <main className="product-shell">
      <RailNavigation
        activeSection={activeSection}
        matterNumber={workspace.matter.matter_number}
        activeSessionId={activeSession.id}
        sessions={sessionsState.sessions}
        onCreateSession={() => void createNewSession()}
        onSelect={navigate}
        onSelectSession={selectSession}
      />

      <section className="workspace-shell">
        <MatterHeader
          activeSection={activeSection}
          gateUnlocked={gateUnlocked}
          matter={workspace.matter}
          onOpenNotifications={() => setSidePanel("notifications")}
          onOpenProfile={() => setSidePanel("profile")}
        />

        <WorkspaceNotice error={error} warning={workspace.backend_warning} />

        {activeSection !== "chat" && activeSection !== "theater" && (
          <StageBoard
            activeStage={activeStage}
            agentCount={workspace.agent_activity.length}
            blockerCount={workspace.readiness.blocker_count}
            factCount={workspace.known_facts.length}
            gateUnlocked={gateUnlocked}
            onSelect={(stage) => navigate(pageFromStage(stage))}
          />
        )}

        {activeSection === "chat" && (
          <ChatPage
            matcher={permitMatcher}
            session={activeSession}
            workspace={workspace}
            isCreatingMatter={sessionAction === "create-matter"}
            isChatting={isChatting}
            liveAgentTrace={chatAgentTrace}
            messages={activeSession.messages}
            chatError={chatError}
            onAnalyze={() => void analyzeActiveSession()}
            onQueryChange={updateChatQuery}
            onOpenEvidence={async () => {
              await openSessionWorkspace();
              navigate("evidence");
            }}
            onOpenMatter={() => void openSessionWorkspace()}
            onOpenRoute={() => navigate("route")}
          />
        )}

        {activeSection === "matter" && (
          <MatterPage
            busyAction={busyAction}
            gateUnlocked={gateUnlocked}
            isBusy={isBusy}
            selectedEvidence={selectedEvidence}
            selectedSource={selectedSource}
            workspace={workspace}
            onApprove={approveReview}
            onGenerateRequest={generateDocumentRequest}
            onSelectEvidence={handleEvidenceSelect}
            onSelectSource={handleSourceSelect}
            onUploadEvidence={uploadSelectedEvidence}
            onRunReview={runAgentReview}
          />
        )}

        {activeSection === "route" && (
          <RoutePage matcher={permitMatcher} workspace={workspace} onOpenMatter={() => navigate("matter")} />
        )}

        {activeSection === "evidence" && (
          <EvidencePage
            busyAction={busyAction}
            gateUnlocked={gateUnlocked}
            groupedEvidence={groupedEvidence}
            isBusy={isBusy}
            selectedEvidence={selectedEvidence}
            selectedSource={selectedSource}
            workspace={workspace}
            onApprove={approveReview}
            onGenerateRequest={generateDocumentRequest}
            onRefresh={() => void loadWorkspace()}
            onSelectEvidence={handleEvidenceSelect}
            onSelectSource={handleSourceSelect}
            onUploadEvidence={uploadSelectedEvidence}
            onRunReview={runAgentReview}
          />
        )}

        {activeSection === "agents" && (
          <AgentsPage
            agents={workspace.agent_activity}
            busyAction={busyAction}
            gateUnlocked={gateUnlocked}
            isBusy={isBusy}
            workspace={workspace}
            onApprove={approveReview}
            onRunReview={runAgentReview}
          />
        )}

        {activeSection === "theater" && (
          <TheaterPage
            busyAction={busyAction}
            isBusy={isBusy}
            workspace={workspace}
            onOpenPacket={() => navigate("review")}
            onRunReview={runAgentReview}
          />
        )}

        {activeSection === "review" && (
          <ReviewPage
            busyAction={busyAction}
            gateUnlocked={gateUnlocked}
            isBusy={isBusy}
            selectedEvidence={selectedEvidence}
            selectedSource={selectedSource}
            workspace={workspace}
            onApprove={approveReview}
            onGenerateRequest={generateDocumentRequest}
            onSelectEvidence={handleEvidenceSelect}
            onSelectSource={handleSourceSelect}
            onUploadEvidence={uploadSelectedEvidence}
            onRunReview={runAgentReview}
          />
        )}

        <input
          ref={fileInputRef}
          className="sr-only"
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.txt,.docx"
          onChange={(event) => {
            const file = event.currentTarget.files?.[0];
            if (file) {
              void uploadFile(file, requestDocumentTypeForEvidence(selectedEvidence));
            }
          }}
        />
      </section>

      <SideDrawer
        kind={sidePanel}
        userEmail={auth.user.email}
        workspace={workspace}
        onClose={() => setSidePanel(null)}
        onOpenRoute={() => {
          setSidePanel(null);
          navigate("route");
        }}
        onSignOut={() => void auth.signOut()}
      />
      <ActionToast message={notice} onDismiss={clearNotice} />
    </main>
  );
}

function pendingAgentTrace(query: string): ChatAgentTraceStep[] {
  const roles = [
    ["intake", "LexNordic Intake", "featherless", "Reading the user's question"],
    ["conflict_kyc", "Conflict KYC", "featherless", "Checking private-workspace boundaries"],
    ["decision_parser", "Decision Parser", "featherless", "Mapping facts to permit routes"],
    ["legal_source", "Legal Source", "aiml", "Selecting source trail"],
    ["evidence", "Evidence", "featherless", "Finding missing documents"],
    ["risk", "Risk", "featherless", "Checking deadlines and sensitivity"],
    ["appeal_packet", "Appeal Packet", "aiml", "Preparing answer structure"],
    ["partner_review", "Partner Review", "aiml", "Verifying product boundary"],
  ] as const;
  return roles.map(([agentRole, agentName, provider, summary], index) => ({
    id: `pending-${agentRole}`,
    agentRole,
    agentName,
    provider,
    status: index === 0 ? "running" : "queued",
    summary,
    output: index === 0 ? query : "Waiting for shared room context.",
    nextAction: "Pass context to the next agent.",
  }));
}

function selectDefaultEvidence(items: EvidenceItem[]): EvidenceItem {
  return (
    items.find((item) => item.status_class === "missing" || item.status_class === "warning") ??
    items[0]
  );
}

function selectEvidence(items: EvidenceItem[], selectedId: string | null): EvidenceItem | undefined {
  if (!items.length) return undefined;
  return items.find((item) => item.id === selectedId) ?? selectDefaultEvidence(items);
}
