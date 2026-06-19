import { useCallback, useEffect, useMemo, useState } from "react";

import { listPermitRoutes, matchPermitRoutes } from "../api/workspaceApi";
import type { PermitMatchResult } from "../types";
import { messageFrom } from "../utils/workspace";

const DEFAULT_QUERY = "";
const DEFAULT_DOCUMENTS: string[] = [];

export function usePermitMatcher() {
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [facts, setFacts] = useState({
    is_student: false,
    completed_studies: false,
    has_job_offer: false,
    has_rejection: false,
    has_family_in_sweden: false,
  });
  const [visitDays, setVisitDays] = useState("0");
  const [documents, setDocuments] = useState<string[]>(DEFAULT_DOCUMENTS);
  const [routeCount, setRouteCount] = useState<number | null>(null);
  const [families, setFamilies] = useState<string[]>([]);
  const [results, setResults] = useState<PermitMatchResult[]>([]);
  const [isMatching, setIsMatching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requestFacts = useMemo(() => {
    const visitValue = Number.parseInt(visitDays, 10);
    return {
      ...facts,
      ...(Number.isFinite(visitValue) && visitValue > 0 ? { visit_days: visitValue } : {}),
    };
  }, [facts, visitDays]);

  const runMatch = useCallback(async () => {
    if (!query.trim()) {
      setResults([]);
      return [];
    }
    setIsMatching(true);
    setError(null);
    try {
      const payload = await matchPermitRoutes({
        query,
        facts: requestFacts,
        documents,
        limit: 4,
      });
      setResults(payload.results);
      return payload.results;
    } catch (caught) {
      setError(messageFrom(caught));
      return [];
    } finally {
      setIsMatching(false);
    }
  }, [documents, query, requestFacts]);

  useEffect(() => {
    void listPermitRoutes()
      .then((payload) => {
        setRouteCount(payload.count);
        setFamilies(payload.families);
      })
      .catch((caught) => setError(messageFrom(caught)));
  }, []);

  function toggleFact(key: keyof typeof facts) {
    setFacts((current) => ({ ...current, [key]: !current[key] }));
  }

  function toggleDocument(document: string) {
    setDocuments((current) =>
      current.includes(document) ? current.filter((item) => item !== document) : [...current, document],
    );
  }

  function reset() {
    setQuery(DEFAULT_QUERY);
    setVisitDays("0");
    setDocuments(DEFAULT_DOCUMENTS);
    setResults([]);
    setError(null);
    setFacts({
      is_student: false,
      completed_studies: false,
      has_job_offer: false,
      has_rejection: false,
      has_family_in_sweden: false,
    });
  }

  function applyResults(nextQuery: string, nextResults: PermitMatchResult[]) {
    setQuery(nextQuery);
    setResults(nextResults);
    setError(null);
  }

  return {
    query,
    facts,
    requestFacts,
    visitDays,
    documents,
    routeCount,
    families,
    results,
    isMatching,
    error,
    setQuery,
    setVisitDays,
    toggleFact,
    toggleDocument,
    runMatch,
    applyResults,
    reset,
  };
}
