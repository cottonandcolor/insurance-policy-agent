import { useEffect, useState } from "react";
import { fetchHealth, type HealthResponse } from "../api";

export function HealthBanner({ health: healthProp }: { health?: HealthResponse | null }) {
  const [health, setHealth] = useState<HealthResponse | null>(healthProp ?? null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (healthProp !== undefined) {
      setHealth(healthProp);
      return;
    }
    fetchHealth()
      .then(setHealth)
      .catch(() => setError("Backend API is not running. Start with: uvicorn api.main:app --reload --port 8000"));
  }, [healthProp]);

  if (error) {
    return <div className="banner error">{error}</div>;
  }

  if (!health) {
    return <div className="banner warn">Checking API health…</div>;
  }

  if (health.llm_provider === "ollama" && !health.ollama_reachable) {
    return (
      <div className="banner warn">
        Ollama is not running. Use <strong>Dry-run mode</strong> for instant demo, or run{" "}
        <code>ollama serve</code> for local AI ({health.configured_model}).
      </div>
    );
  }

  return (
    <div className="banner ok">
      API connected · Model: <strong>{health.configured_model}</strong>
      {health.ollama_reachable && " · Ollama ready"}
    </div>
  );
}
