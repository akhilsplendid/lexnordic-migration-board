import { FileCheck2, FileText, FolderKanban, Gamepad2, MessageSquareText, Plus, Route, Workflow } from "lucide-react";
import type { ReactNode } from "react";

import type { ConsultationSession, SectionId } from "../types";

const ITEMS: Array<{ id: SectionId; icon: ReactNode; label: string }> = [
  { id: "chat", icon: <MessageSquareText />, label: "Chat" },
  { id: "matter", icon: <FolderKanban />, label: "Matter" },
  { id: "route", icon: <Route />, label: "Route" },
  { id: "evidence", icon: <FileText />, label: "Evidence" },
  { id: "agents", icon: <Workflow />, label: "Agents" },
  { id: "theater", icon: <Gamepad2 />, label: "Theater" },
  { id: "review", icon: <FileCheck2 />, label: "Packet" },
];

export function RailNavigation({
  activeSection,
  activeSessionId,
  matterNumber,
  sessions,
  onSelect,
  onSelectSession,
  onCreateSession,
}: {
  activeSection: SectionId;
  activeSessionId?: string;
  matterNumber: string;
  sessions: ConsultationSession[];
  onSelect: (section: SectionId) => void;
  onSelectSession: (sessionId: string) => void;
  onCreateSession: () => void;
}) {
  return (
    <aside className="app-rail" aria-label="Product navigation">
      <div className="brand-lockup">
        <div className="brand-mark">LN</div>
        <div>
          <strong>LexNordic</strong>
          <span>Migration Board</span>
        </div>
      </div>

      <nav className="rail-nav" aria-label="Workspace sections">
        {ITEMS.map((item) => (
          <button
            className={`rail-item ${activeSection === item.id ? "active" : ""}`}
            type="button"
            aria-current={activeSection === item.id ? "page" : undefined}
            aria-pressed={activeSection === item.id}
            key={item.id}
            title={item.label}
            onClick={() => onSelect(item.id)}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <section className="session-switcher" aria-label="Consultation sessions">
        <div className="session-switcher-header">
          <span>Sessions</span>
          <button className="mini-icon-button" type="button" aria-label="Start new consultation" onClick={onCreateSession}>
            <Plus />
          </button>
        </div>
        <div className="session-list">
          {sessions.slice(0, 6).map((session) => (
            <button
              className={`session-row ${session.id === activeSessionId ? "active" : ""}`}
              type="button"
              key={session.id}
              onClick={() => onSelectSession(session.id)}
            >
              <span>{session.title}</span>
              <small>
                {session.matterNumber
                  ? `${session.matterNumber}${typeof session.readiness === "number" ? ` - ${session.readiness}%` : ""}`
                  : "Private intake"}
              </small>
            </button>
          ))}
        </div>
      </section>

      <div className="rail-footer">
        <span>{activeSection === "chat" ? "Secure workspace" : "Active matter"}</span>
        <strong>{activeSection === "chat" ? "Private intake" : matterNumber}</strong>
      </div>
    </aside>
  );
}
