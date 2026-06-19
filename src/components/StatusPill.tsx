import type { ReactNode } from "react";

export function StatusPill({
  children,
  tone,
  icon,
}: {
  children: ReactNode;
  tone: "good" | "watch" | "risk" | "ready" | "locked" | "neutral" | "active" | "done" | "idle";
  icon?: ReactNode;
}) {
  return (
    <span className={`status-token ${tone}`}>
      {icon}
      {children}
    </span>
  );
}
