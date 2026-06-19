import { CheckCircle2, X } from "lucide-react";

export function ActionToast({ message, onDismiss }: { message: string | null; onDismiss: () => void }) {
  if (!message) return null;
  return (
    <div className="action-toast" role="status">
      <CheckCircle2 />
      <span>{message}</span>
      <button className="toast-close" type="button" aria-label="Dismiss status message" onClick={onDismiss}>
        <X />
      </button>
    </div>
  );
}
