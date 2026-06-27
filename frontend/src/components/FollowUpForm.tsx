import { useState } from "react";
import { followUpAnalysis, type AnalyzeResponse } from "../api";

interface Props {
  threadId: string;
  dryRun: boolean;
  quick: boolean;
  onResult: (result: AnalyzeResponse) => void;
  onError: (message: string) => void;
}

export function FollowUpForm({ threadId, dryRun, quick, onResult, onError }: Props) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    const text = message.trim();
    if (!text || loading) return;

    setLoading(true);
    onError("");
    try {
      const response = await followUpAnalysis(threadId, text, { dryRun, quick });
      if (response.error && !response.recommendation) {
        onError(response.error);
      } else {
        onResult(response);
        setMessage("");
        if (response.error) {
          onError(response.error);
        }
      }
    } catch (e) {
      onError(e instanceof Error ? e.message : "Follow-up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card follow-up" data-testid="follow-up-section">
      <h2>Follow-up question</h2>
      <p className="help-text">
        Session memory keeps your profile, normalized plans, and retrieval cache. Follow-ups
        re-run ToT scoring at shallow depth — no full re-ingest.
      </p>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder='e.g. "I care more about lowest cost" or "What if hail damage is $40K?"'
        rows={3}
        data-testid="follow-up-input"
      />
      <div className="actions">
        <button
          className="btn-secondary"
          onClick={submit}
          disabled={loading || !message.trim()}
          data-testid="follow-up-button"
        >
          {loading ? "Updating…" : "Ask follow-up"}
        </button>
      </div>
    </div>
  );
}
