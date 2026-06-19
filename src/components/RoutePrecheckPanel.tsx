import { ArrowRight, Route, SearchCheck } from "lucide-react";

import type { usePermitMatcher } from "../hooks/usePermitMatcher";

type Matcher = ReturnType<typeof usePermitMatcher>;

const FACT_OPTIONS: Array<{ key: keyof Matcher["facts"]; label: string }> = [
  { key: "is_student", label: "Current or former student" },
  { key: "completed_studies", label: "Completed higher education" },
  { key: "has_job_offer", label: "Has job offer" },
  { key: "has_rejection", label: "Has rejected decision" },
  { key: "has_family_in_sweden", label: "Family in Sweden" },
];

const DOCUMENT_OPTIONS = [
  ["passport_copy", "Passport"],
  ["study_progress", "Study proof"],
  ["employment_contract", "Contract"],
  ["salary_terms", "Salary terms"],
  ["decision_letter", "Decision letter"],
  ["relationship_proof", "Relationship proof"],
] as const;

export function RoutePrecheckPanel({
  active,
  matcher,
  onOpenMatter,
}: {
  active: boolean;
  matcher: Matcher;
  onOpenMatter: () => void;
}) {
  return (
    <section className={`route-precheck ${active ? "panel-active expanded" : ""}`} aria-label="Permit route precheck">
      <div className="route-precheck-copy">
        <span className="section-kicker">Route precheck</span>
        <h2>Test any permit path before opening a matter</h2>
        <p>
          Compare the applicant facts against Swedish permit families before creating or changing the case workspace.
        </p>
      </div>

      <div className="route-form">
        <label>
          Applicant question
          <textarea value={matcher.query} onChange={(event) => matcher.setQuery(event.currentTarget.value)} rows={3} />
        </label>

        <div className="chip-grid" aria-label="Facts">
          {FACT_OPTIONS.map((option) => (
            <button
              className={`toggle-chip ${matcher.facts[option.key] ? "selected" : ""}`}
              type="button"
              aria-pressed={matcher.facts[option.key]}
              key={option.key}
              onClick={() => matcher.toggleFact(option.key)}
            >
              {option.label}
            </button>
          ))}
        </div>

        <label>
          Visit days, if relevant
          <input
            inputMode="numeric"
            min="0"
            type="number"
            value={matcher.visitDays}
            onChange={(event) => matcher.setVisitDays(event.currentTarget.value)}
          />
        </label>

        <div className="chip-grid" aria-label="Documents">
          {DOCUMENT_OPTIONS.map(([key, label]) => (
            <button
              className={`toggle-chip ${matcher.documents.includes(key) ? "selected" : ""}`}
              type="button"
              aria-pressed={matcher.documents.includes(key)}
              key={key}
              onClick={() => matcher.toggleDocument(key)}
            >
              {label}
            </button>
          ))}
        </div>

        <button className="primary-action full" type="button" onClick={() => void matcher.runMatch()} disabled={matcher.isMatching}>
          <SearchCheck />
          <span>{matcher.isMatching ? "Checking routes" : "Run precheck"}</span>
        </button>
      </div>

      <div className="route-results">
        <div className="route-stats">
          <Route />
          <span>{matcher.routeCount ?? "--"} routes</span>
          <small>{matcher.families.length} families</small>
        </div>
        {matcher.error && <p className="route-error">{matcher.error}</p>}
        {matcher.results.length ? (
          matcher.results.slice(0, 3).map((result) => (
            <article className="route-result" key={result.route.route_id}>
              <div>
                <strong>{result.route.name}</strong>
                <p>{result.route.summary}</p>
              </div>
              <div className="route-result-score">
                <span>{result.match_score}% match</span>
                <b>{result.readiness.score}% ready</b>
              </div>
            </article>
          ))
        ) : (
          <div className="route-empty-state">
            <strong>Ready to rank candidate routes</strong>
            <p>Run the precheck to compare permit families, source basis, missing facts, evidence, and risk flags.</p>
          </div>
        )}
        <button className="text-action route-open-matter" type="button" onClick={onOpenMatter}>
          <span>Return to matter workflow</span>
          <ArrowRight />
        </button>
      </div>
    </section>
  );
}
