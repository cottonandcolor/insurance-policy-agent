import { useState } from "react";
import "./App.css";
import { analyzePlans, type AnalyzeResponse, type ProfileInput } from "./api";
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
  const [useDefaults, setUseDefaults] = useState(true);
  const [dryRun, setDryRun] = useState(true);
  const [quick, setQuick] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await analyzePlans(profile, files, {
        dryRun,
        quick,
        useDefaults,
      });
      setResult(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>Insurance Policy Comparison Agent</h1>
        <p>
          Upload synthetic policy documents, compare coverage across loss scenarios, and
          get a grounded recommendation.
        </p>
      </header>

      <HealthBanner />

      <div className="grid">
        <ProfileForm profile={profile} onChange={setProfile} />
        <PolicyUpload
          files={files}
          useDefaults={useDefaults}
          onFilesChange={setFiles}
          onUseDefaultsChange={setUseDefaults}
        />
      </div>

      <div className="card" style={{ marginTop: 20 }}>
        <h2>Run Agent</h2>
        <div className="options">
          <label>
            <input
              type="checkbox"
              checked={dryRun}
              onChange={(e) => setDryRun(e.target.checked)}
            />
            Dry-run (no LLM — instant demo)
          </label>
          <label>
            <input
              type="checkbox"
              checked={quick}
              onChange={(e) => setQuick(e.target.checked)}
            />
            Quick mode (shorter ToT loop)
          </label>
        </div>
        <div className="actions">
          <button
            className="btn-primary"
            onClick={runAnalysis}
            disabled={loading || (!useDefaults && files.length === 0)}
          >
            {loading ? "Analyzing…" : "Analyze Plans"}
          </button>
        </div>
        {loading && (
          <p className="loading">
            Running LangGraph workflow (intake → index → ToT → synthesis)…
            {dryRun ? " Dry-run is usually under 10 seconds." : " Ollama may take several minutes."}
          </p>
        )}
        {error && <div className="banner error">{error}</div>}
      </div>

      {result && <ResultsView result={result} />}
    </div>
  );
}
