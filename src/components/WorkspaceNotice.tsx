import { AlertTriangle } from "lucide-react";

export function WorkspaceNotice({ error, warning }: { error: string | null; warning?: string }) {
  const message = error ?? warning;
  if (!message) return null;
  return (
    <div className="system-message" role="status">
      <AlertTriangle />
      <span>{message}</span>
    </div>
  );
}
