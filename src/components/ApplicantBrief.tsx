import { AlertTriangle, BadgeCheck, CheckCircle2 } from "lucide-react";

import { FactLine } from "./FactLine";

export function ApplicantBrief({ knownFacts, missingFacts }: { knownFacts: string[]; missingFacts: string[] }) {
  return (
    <section className="intake-panel" aria-label="Applicant brief">
      <div className="panel-header">
        <span className="section-kicker">Applicant brief</span>
        <BadgeCheck />
      </div>
      <div className="fact-grid">
        {knownFacts.map((fact) => (
          <FactLine key={fact} icon={<CheckCircle2 />} label={fact} tone="good" />
        ))}
        {missingFacts.map((fact) => (
          <FactLine key={fact} icon={<AlertTriangle />} label={fact} tone="risk" />
        ))}
      </div>
    </section>
  );
}
