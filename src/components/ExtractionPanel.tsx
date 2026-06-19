import { FileText, SearchCheck } from "lucide-react";
import type { CSSProperties } from "react";

import { FactLine } from "./FactLine";
import type { Workspace } from "../types";

export function ExtractionPanel({ extraction }: { extraction: Workspace["extraction_feed"] }) {
  return (
    <section className="extraction-panel">
      <div className="panel-header">
        <span className="section-kicker">Extraction status</span>
        <SearchCheck />
      </div>
      <div className="extraction-progress">
        <span>{extraction.message}</span>
        <strong>{extraction.progress}%</strong>
      </div>
      <div className="progress-line" style={{ "--progress": `${extraction.progress}%` } as CSSProperties}>
        <span />
      </div>
      <div className="field-stack">
        {extraction.fields.length ? (
          extraction.fields.slice(0, 3).map((field) => <FactLine icon={<FileText />} label={field} key={field} tone="neutral" />)
        ) : (
          <p className="empty-note">Extraction will start after the applicant uploads a document.</p>
        )}
      </div>
    </section>
  );
}
