export type PolicyPreset = "synthetic" | "public_ho3" | "public_flood" | "upload";

export interface AnalyzeResponse {
  recommendation: string | null;
  winning_branch: {
    branch_id?: string;
    composite_score?: number;
    interpretation?: string;
  } | null;
  normalized_plans: unknown[];
  session_profile: Record<string, unknown>;
  llm_call_count: number;
  indexed_chunks?: number;
  mode: string;
  error: string | null;
}

export interface HealthResponse {
  status: string;
  llm_provider: string;
  ollama_reachable: boolean;
  configured_model: string;
}

export interface ProfileInput {
  age: number;
  location: string;
  flood_zone: boolean;
  home_value: number;
  coverage_breadth: number;
  low_cost: number;
  few_exclusions: number;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error("API unreachable");
  return res.json();
}

export async function analyzePlans(
  profile: ProfileInput,
  files: File[],
  options: { dryRun: boolean; quick: boolean; policyPreset: PolicyPreset }
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("age", String(profile.age));
  form.append("location", profile.location);
  form.append("flood_zone", String(profile.flood_zone));
  form.append("home_value", String(profile.home_value));
  form.append("coverage_breadth", String(profile.coverage_breadth));
  form.append("low_cost", String(profile.low_cost));
  form.append("few_exclusions", String(profile.few_exclusions));
  form.append("policy_preset", options.policyPreset);
  form.append("use_defaults", String(options.policyPreset === "synthetic"));

  for (const file of files) {
    form.append("policies", file);
  }

  const params = new URLSearchParams({
    dry_run: String(options.dryRun),
    quick: String(options.quick),
  });

  const res = await fetch(`/api/analyze?${params}`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Analysis failed");
  }

  return res.json();
}
