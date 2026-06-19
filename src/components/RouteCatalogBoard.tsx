import { ArrowRight, FileWarning, ListChecks, Route, Scale, SearchCheck } from "lucide-react";

import { StatusPill } from "./StatusPill";
import type { usePermitMatcher } from "../hooks/usePermitMatcher";

type Matcher = ReturnType<typeof usePermitMatcher>;

const ROUTE_FAMILIES = [
  "work",
  "study",
  "family",
  "appeals",
  "visiting",
  "protection",
  "permanent",
  "citizenship",
  "EU/Swiss/British",
];

export function RouteCatalogBoard({
  matcher,
  onOpenMatter,
}: {
  matcher: Matcher;
  onOpenMatter: () => void;
}) {
  const primary = matcher.results[0];
  const visibleFamilies = matcher.families.length ? matcher.families : ROUTE_FAMILIES;

  return (
    <section className="route-catalog-board" aria-label="Route intelligence board">
      <div className="route-family-panel">
        <div className="section-heading compact">
          <div>
            <span className="section-kicker">Permit route catalog</span>
            <h2>46 routes across Swedish migration families</h2>
          </div>
          <StatusPill tone="active" icon={<Route />}>
            {matcher.routeCount ?? 46} routes
          </StatusPill>
        </div>

        <div className="route-family-grid">
          {visibleFamilies.slice(0, 12).map((family) => (
            <button className="route-family-tile" type="button" key={family} onClick={() => matcher.setQuery(family)}>
              <span>{family}</span>
              <small>{routeFamilyHint(family)}</small>
            </button>
          ))}
        </div>
      </div>

      <div className="route-compare-panel">
        <div className="section-heading compact">
          <div>
            <span className="section-kicker">Candidate comparison</span>
            <h2>{primary?.route.name ?? "Run screening to rank routes"}</h2>
          </div>
          <Scale />
        </div>

        <div className="route-compare-list">
          {(matcher.results.length ? matcher.results : fallbackRoutes()).slice(0, 4).map((result) => (
            <article className="route-compare-row" key={result.route.route_id}>
              <div>
                <strong>{result.route.name}</strong>
                <p>{result.route.summary}</p>
                <span>{result.route.family}</span>
              </div>
              <div className="route-compare-score">
                <b>{result.match_score}%</b>
                <small>{result.readiness.score}% ready</small>
              </div>
            </article>
          ))}
        </div>
      </div>

      <aside className="route-risk-panel">
        <div className="section-heading compact">
          <div>
            <span className="section-kicker">Next questions</span>
            <h2>Facts that change the route</h2>
          </div>
          <SearchCheck />
        </div>

        <ul className="route-question-list">
          {(primary?.next_questions.length
            ? primary.next_questions
            : [
                "What permit do you hold today and when does it expire?",
                "Do you have a signed job offer with salary and insurance terms?",
                "Was there a rejected decision and when was it served?",
                "Which family, study, work, or protection facts can be documented?",
              ]
          )
            .slice(0, 5)
            .map((question) => (
              <li key={question}>
                <ListChecks />
                <span>{question}</span>
              </li>
            ))}
        </ul>

        <div className="route-source-box">
          <FileWarning />
          <div>
            <strong>June 2026 rule overlay active</strong>
            <p>Salary threshold, employer controls, transition rules, and route-sensitive evidence are checked before packet output.</p>
          </div>
        </div>

        <button className="primary-action full" type="button" onClick={onOpenMatter}>
          <span>Open matter workspace</span>
          <ArrowRight />
        </button>
      </aside>
    </section>
  );
}

function routeFamilyHint(family: string): string {
  const lowered = family.toLowerCase();
  if (lowered.includes("work")) return "salary, offer, insurance";
  if (lowered.includes("study")) return "admission, progress, funds";
  if (lowered.includes("family")) return "relationship and support";
  if (lowered.includes("appeal")) return "deadline and decision";
  if (lowered.includes("visit")) return "duration and purpose";
  if (lowered.includes("citizen")) return "residence and conduct";
  return "facts, documents, source basis";
}

function fallbackRoutes() {
  return [
    {
      route: {
        route_id: "work_permit",
        family: "work",
        name: "Work permit with job offer",
        summary: "Employment contract, salary terms, insurance, and employer controls must be checked.",
      },
      match_score: 0,
      readiness: { score: 0 },
    },
    {
      route: {
        route_id: "student_to_work",
        family: "study",
        name: "Former student found work",
        summary: "Post-study route depends on completed higher education and a qualifying job offer.",
      },
      match_score: 0,
      readiness: { score: 0 },
    },
    {
      route: {
        route_id: "appeal",
        family: "appeals",
        name: "Appeal after rejection",
        summary: "Decision date, service date, grounds, and evidence gaps drive the strategy.",
      },
      match_score: 0,
      readiness: { score: 0 },
    },
  ];
}
