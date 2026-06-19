import { AlertTriangle, CheckCircle2, Route, X } from "lucide-react";

import type { SidePanelKind, Workspace } from "../types";

export function SideDrawer({
  kind,
  workspace,
  userEmail,
  onClose,
  onOpenRoute,
  onSignOut,
}: {
  kind: SidePanelKind | null;
  workspace: Workspace;
  userEmail?: string | null;
  onClose: () => void;
  onOpenRoute: () => void;
  onSignOut: () => void;
}) {
  if (!kind) return null;
  const isNotifications = kind === "notifications";
  return (
    <div className="drawer-backdrop" role="presentation" onClick={onClose}>
      <aside className="side-drawer" role="dialog" aria-modal="true" aria-label={isNotifications ? "Notifications" : "Applicant profile"} onClick={(event) => event.stopPropagation()}>
        <header>
          <div>
            <span className="section-kicker">{isNotifications ? "Matter signals" : "Applicant profile"}</span>
            <h2>{isNotifications ? "What needs attention" : workspace.matter.applicant_alias}</h2>
          </div>
          <button className="icon-button" type="button" aria-label="Close panel" onClick={onClose}>
            <X />
          </button>
        </header>

        {isNotifications ? (
          <div className="drawer-list">
            <DrawerItem icon={<AlertTriangle />} title="Open blockers" detail={`${workspace.readiness.blocker_count} evidence blockers remain.`} />
            <DrawerItem icon={<Route />} title="Route confidence" detail={`Current route: ${workspace.matter.route}.`} />
            <DrawerItem icon={<CheckCircle2 />} title="AI packet status" detail={packetStatusCopy(workspace)} />
            <button className="primary-action full" type="button" onClick={onOpenRoute}>
              <Route />
              <span>Open route precheck</span>
            </button>
          </div>
        ) : (
          <div className="drawer-list">
            <DrawerItem title="Signed in as" detail={userEmail ?? "Authenticated user"} />
            <DrawerItem title="Matter number" detail={workspace.matter.matter_number} />
            <DrawerItem title="Current state" detail={workspace.matter.state_label} />
            <DrawerItem title="Known facts" detail={workspace.known_facts.join(", ")} />
            <DrawerItem title="Missing facts" detail={workspace.missing_facts.join(", ") || "None"} />
            <button className="secondary-action full" type="button" onClick={onSignOut}>
              <span>Sign out</span>
            </button>
          </div>
        )}
      </aside>
    </div>
  );
}

function DrawerItem({ icon, title, detail }: { icon?: React.ReactNode; title: string; detail: string }) {
  return (
    <article className="drawer-item">
      {icon}
      <div>
        <strong>{title}</strong>
        <p>{detail}</p>
      </div>
    </article>
  );
}

function packetStatusCopy(workspace: Workspace): string {
  const readiness = workspace.readiness;
  if (readiness.packet_gate.state === "unlocked") return "Packet is ready to finalize in this workspace.";
  return `${readiness.score}% ready. Run AI review after the missing evidence is added.`;
}
