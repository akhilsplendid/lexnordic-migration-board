import { CompetitionProofPanel } from "../components/CompetitionProofPanel";
import { RouteCatalogBoard } from "../components/RouteCatalogBoard";
import { RoutePrecheckPanel } from "../components/RoutePrecheckPanel";
import type { usePermitMatcher } from "../hooks/usePermitMatcher";
import type { Workspace } from "../types";

export function RoutePage({
  matcher,
  workspace,
  onOpenMatter,
}: {
  matcher: ReturnType<typeof usePermitMatcher>;
  workspace: Workspace;
  onOpenMatter: () => void;
}) {
  return (
    <section className="single-page route-page" aria-label="Route page">
      <RoutePrecheckPanel active matcher={matcher} onOpenMatter={onOpenMatter} />
      <RouteCatalogBoard matcher={matcher} onOpenMatter={onOpenMatter} />
      <CompetitionProofPanel workspace={workspace} />
    </section>
  );
}
