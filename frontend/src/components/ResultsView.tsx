import ReactMarkdown from "react-markdown";
import type { AnalyzeResponse } from "../api";

interface Props {
  result: AnalyzeResponse;
}

export function ResultsView({ result }: Props) {
  if (result.error && !result.recommendation) {
    return (
      <div className="card results">
        <h2>Analysis Error</h2>
        <p className="banner error">{result.error}</p>
      </div>
    );
  }

  return (
    <div className="card results">
      <h2>Recommendation</h2>
      <div className="meta-row">
        <span className="badge">Mode: {result.mode}</span>
        <span>LLM calls: {result.llm_call_count}</span>
        {result.winning_branch?.composite_score != null && (
          <span>Score: {result.winning_branch.composite_score.toFixed(2)}</span>
        )}
        {result.winning_branch?.branch_id && (
          <span>Branch: {result.winning_branch.branch_id}</span>
        )}
        {result.thread_id && <span>Session: {result.thread_id}</span>}
      </div>
      {result.external_enrichment?.flood_zone_code && (
        <p className="help-text">
          FEMA NFHL zone: <strong>{String(result.external_enrichment.flood_zone_code)}</strong>
          {result.external_enrichment.flood_zone_subtype
            ? ` (${String(result.external_enrichment.flood_zone_subtype)})`
            : ""}
        </p>
      )}
      <div className="markdown-body">
        <ReactMarkdown>{result.recommendation || "No recommendation generated."}</ReactMarkdown>
      </div>
      <p className="disclaimer">
        This is decision support only — not a binding insurance quote. Use synthetic or
        public policy data. Consult a licensed broker before purchasing coverage.
      </p>
    </div>
  );
}
