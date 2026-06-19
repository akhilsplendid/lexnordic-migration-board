import {
  Bot,
  FileCheck2,
  FileText,
  LockKeyhole,
  Mail,
  RadioTower,
  Route,
  ShieldCheck,
} from "lucide-react";
import { useState } from "react";
import type { FormEvent, ReactNode } from "react";

type AuthGateProps = {
  isConfigured: boolean;
  isLoading: boolean;
  error: string | null;
  message: string | null;
  onSignIn: (email: string, password: string) => Promise<void>;
  onSignUp: (email: string, password: string) => Promise<void>;
};

export function AuthGate({
  isConfigured,
  isLoading,
  error,
  message,
  onSignIn,
  onSignUp,
}: AuthGateProps) {
  const [mode, setMode] = useState<"sign-in" | "sign-up">("sign-in");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      if (mode === "sign-in") {
        await onSignIn(email.trim(), password);
      } else {
        await onSignUp(email.trim(), password);
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-entry" aria-labelledby="auth-heading">
        <div className="auth-trust-panel">
          <div className="brand-lockup auth-brand">
            <div className="brand-mark">LN</div>
            <div>
              <strong>LexNordic</strong>
              <span>Migration Board</span>
            </div>
          </div>

          <div className="auth-hero-copy">
            <span className="section-kicker">Private AI consultation</span>
            <h1 id="auth-heading">Source-grounded Swedish migration support</h1>
            <p>
              A secure workspace where route screening, evidence collection, Band agent coordination, and AI packet
              assembly stay tied to your own consultation session.
            </p>
          </div>

          <div className="trust-feature-grid">
            <TrustFeature
              icon={<ShieldCheck />}
              title="Source-grounded AI"
              detail="Official sources and legal references stay attached to the packet."
            />
            <TrustFeature
              icon={<LockKeyhole />}
              title="Private workspace"
              detail="Supabase Auth and user-owned RLS isolate sessions and documents."
            />
            <TrustFeature
              icon={<RadioTower />}
              title="Band coordination"
              detail="Specialist agents share context through the Band room."
            />
          </div>

          <div className="auth-flow-preview" aria-label="Consultation workflow preview">
            <span>
              <Bot /> Chat
            </span>
            <span>
              <Route /> Route
            </span>
            <span>
              <FileText /> Evidence
            </span>
            <span>
              <RadioTower /> Band
            </span>
            <span>
              <FileCheck2 /> Packet
            </span>
          </div>
        </div>

        <div className="auth-panel">
          <div className="auth-copy">
            <span className="section-kicker">Secure access</span>
            <h2>{mode === "sign-in" ? "Open your consultation" : "Create private workspace"}</h2>
            <p>
              Use email/password for the local hackathon workspace. Chat history, matters, and files stay separated per
              account.
            </p>
          </div>

          {!isConfigured ? (
            <div className="auth-warning">
              <LockKeyhole />
              <div>
                <strong>Private workspace auth is not configured</strong>
                <span>Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` to `.env.local`.</span>
              </div>
            </div>
          ) : (
            <form className="auth-form" onSubmit={submit}>
              <label>
                <span>Email</span>
                <input
                  autoComplete="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.currentTarget.value)}
                  required
                />
              </label>
              <label>
                <span>Password</span>
                <input
                  autoComplete={mode === "sign-in" ? "current-password" : "new-password"}
                  minLength={6}
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.currentTarget.value)}
                  required
                />
              </label>

              <div className="auth-message-slot">
                {error && <p className="auth-error">{error}</p>}
                {message && <p className="auth-message">{message}</p>}
              </div>

              <button className="primary-action full" type="submit" disabled={isLoading || isSubmitting}>
                {mode === "sign-in" ? <ShieldCheck /> : <Mail />}
                <span>{isSubmitting ? "Working" : mode === "sign-in" ? "Continue" : "Create workspace"}</span>
              </button>
              <button
                className="text-action full"
                type="button"
                onClick={() => setMode(mode === "sign-in" ? "sign-up" : "sign-in")}
              >
                <span>{mode === "sign-in" ? "Create a private test workspace" : "Use an existing workspace"}</span>
              </button>
            </form>
          )}

          <p className="session-privacy-note">
            Session privacy: data remains in your private matter vault until you manually export it. No automatic filing
            with migration authorities is performed.
          </p>
        </div>
      </section>
    </main>
  );
}

function TrustFeature({
  icon,
  title,
  detail,
}: {
  icon: ReactNode;
  title: string;
  detail: string;
}) {
  return (
    <article className="trust-feature">
      {icon}
      <div>
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
    </article>
  );
}
