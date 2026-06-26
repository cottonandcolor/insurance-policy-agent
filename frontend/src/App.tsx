import { useEffect, useRef, useState } from "react";
import "./App.css";
import {
  analyzePlans,
  fetchHealth,
  type AnalyzeResponse,
  type HealthResponse,
  type PolicyPreset,
  type ProfileInput,
} from "./api";
import { HealthBanner } from "./components/HealthBanner";
import { PolicyUpload } from "./components/PolicyUpload";
import { ProfileForm } from "./components/ProfileForm";
import { ResultsView } from "./components/ResultsView";

const defaultProfile: ProfileInput = {
  age: 35,
  location: "Cedar Park, TX",
  flood_zone: true,
  home_value: 350000,
  coverage_breadth: 0.4,
  low_cost: 0.3,
  few_exclusions: 0.3,
};

export default function App() {
  const [profile, setProfile] = useState<ProfileInput>(defaultProfile);
  const [files, setFiles] = useState<File[]>([]);
  const [policyPreset, setPolicyPreset] = useState<PolicyPreset>("synthetic");
  const [dryRun, setDryRun] = useState(true);
  const [quick, setQuick] = useState(true);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const ollamaRequired = !dryRun && health?.llm_provider === "ollama";
  const ollamaBlocked = ollamaRequired && health !== null && !health.ollama_reachable;
  const uploadBlocked = policyPreset === "upload" && files.length === 0;
  const analyzeDisabled = loading || uploadBlocked || ollamaBlocked;

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    if (!loading) {
      setElapsedSec(0);
      return;
    }
    const started = Date.now();
    const timer = window.setInterval(() => {
      setElapsedSec(Math.floor((Date.now() - started) / 1000));
    }, 1000);
    return () => window.clearInterval(timer);
  }, [loading]);

  useEffect(() => {
    if (result && resultsRef.current) {
      resultsRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [result]);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await analyzePlans(profile, files, {
        dryRun,
        quick,
        policyPreset,
      });
      if (response.error && !response.recommendation) {
        setError(response.error);
      } else {
        setResult(response);
        if (response.error) {
          setError(response.error);
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const loadingHint = dryRun
    ? "Dry-run usually finishes in under 10 seconds."
    : quick
      ? "Live Ollama + quick mode typically takes 3–5 minutes. Keep this tab open."
      : "Live Ollama full mode can take 10+ minutes. Consider Dry-run or Quick mode for demos.";

  return (
    <div className="app">
      <header>
        <h1>Insurance Policy Comparison Agent</h1>
        <p>
          Upload <strong>.txt</strong> policy documents (or use bundled demo plans), compare
          coverage across loss scenarios, and get a grounded recommendation.
        </p>
      </header>

      <HealthBanner health={health} />

      <div className="grid">
        <ProfileForm profile={profile} onChange={setProfile} />
        <PolicyUpload
          files={files}
          policyPreset={policyPreset}
          onFilesChange={setFiles}
          onPolicyPresetChange={setPolicyPreset}
        />
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h2>Run Agent</h2>
        <p className="help-text run-hint">
          Check options below, then click <strong>Analyze Plans</strong>. Quick mode only changes
          ToT depth when analysis runs — it does not start on its own.
        </p>
        <div className="options">
          <label>
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
              data-testid="dry-run-checkbox"
            />
            Dry-run (no LLM — instant demo)
          </label>
          <label>
            <input
              type="checkbox"
              checked={quick}
              onChange={(e) => setQuick(e.target.checked)}
              data-testid="quick-mode-checkbox"
            />
            Quick mode (beam 2, depth 2 — faster ToT)
          </label>
        </div>
        <div className="actions">
          <button
            className="btn-primary"
            onClick={runAnalysis}
            disabled={analyzeDisabled}
            data-testid="analyze-button"
          >
            {loading ? `Analyzing… (${elapsedSec}s)` : "Analyze Plans"}
          </button>
        </div>
        {ollamaBlocked && (
          <div className="banner warn" style={{ marginTop: 12 }}>
            Ollama is not running. Enable <strong>Dry-run</strong> for an instant result, or run{" "}
            <code>ollama serve</code> before live analysis.
          </div>
        )}
        {loading && (
          <p className="loading">
            Running LangGraph workflow (intake → index → ToT → synthesis)… {loadingHint}
          </p>
        )}
        {error && <div className="banner error">{error}</div>}
      </div>

      {result && (
        <div ref={resultsRef} data-testid="results-section">
          <ResultsView result={result} />
        </div>
      )}
    </div>
  );
}
