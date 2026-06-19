import type { SectionId, StageId } from "../types";

export const PAGES: SectionId[] = ["chat", "matter", "route", "evidence", "agents", "theater", "review"];

export function pageFromHash(hash: string): SectionId {
  const value = hash.replace(/^#\/?/, "").trim().toLowerCase();
  return PAGES.includes(value as SectionId) ? (value as SectionId) : "chat";
}

export function setPageHash(page: SectionId) {
  const next = `#/${page}`;
  if (window.location.hash !== next) {
    window.history.pushState(null, "", next);
  }
}

export function stageFromPage(page: SectionId): StageId {
  if (page === "agents") return "agent_review";
  if (page === "review") return "packet_final";
  if (page === "evidence") return "evidence";
  return "intake";
}

export function pageFromStage(stage: StageId): SectionId {
  if (stage === "agent_review") return "agents";
  if (stage === "packet_final") return "review";
  if (stage === "evidence") return "evidence";
  return "matter";
}
