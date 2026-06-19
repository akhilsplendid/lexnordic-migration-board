import type { ReactNode } from "react";

export function FactLine({
  icon,
  label,
  tone,
}: {
  icon: ReactNode;
  label: string;
  tone: "good" | "risk" | "neutral";
}) {
  return (
    <div className={`fact-line ${tone}`}>
      {icon}
      <span>{label}</span>
    </div>
  );
}
