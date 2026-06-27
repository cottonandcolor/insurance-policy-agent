# Insurance Policy Comparison & Recommendation Agent

Autonomous multi-agent system for comparing insurance plans using grounded retrieval, Tree-of-Thought reasoning, and safety guardrails — with a **React demo UI**, **local Ollama**, or **cloud LLMs** (OpenRouter, Groq, etc.).

**Capstone Project — Section B Final Submission**

---

## Problem

Consumers and brokers comparing auto, home, or life insurance face dozens of plans with different coverage limits, deductibles, exclusions, and riders buried in dense policy documents. This agent goes beyond premium comparison to analyze **what each plan actually pays** in realistic loss scenarios — with citations to policy language.

## Architecture

| Layer | Technology | Role |
|---|---|---|
| Frontend | React + Vite | Upload policies, profile form, results display |
| API | FastAPI | File upload, `/api/analyze`, health checks |
| Orchestrator | LangGraph | State machine, ToT beam loop, budget enforcement |
| Agents | Role-specific LLM prompts | Intake, extraction, reasoning, critic, synthesis |
| LLM | **Ollama** (local) or **OpenAI-compatible** (OpenRouter, Groq, Together) | Mistral/Llama locally, or cloud models via API key |
| Retrieval | ChromaDB | Section-aware chunking over policy documents |

---

## Quick start — React demo

You need **two terminals**: one for the Python API (port 8000), one for the React UI (port 5173).

| Terminal | Directory | What runs |
|----------|-----------|-----------|
| 1 | project root (`capstone/`) | FastAPI backend (Python) |
| 2 | `frontend/` | React dev server (Node.js) |

### Prerequisites

- Python 3.9+
- Node.js 18+
- **One live LLM option** (optional — use **Dry-run** in the UI without any):
  - [Ollama](https://ollama.com) — free, local, private
  - [OpenRouter](https://openrouter.ai) — free/low-cost cloud models (API key)
  - Groq, Together, or OpenAI — same env vars as OpenRouter (see below)

### 1. Backend setup (terminal 1 — project root)

```bash
git clone https://github.com/cottonandcolor/insurance-policy-agent.git
cd insurance-policy-agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
```

Your prompt should show `(.venv)` before running Python commands.

### 2. LLM setup (pick one — optional for dry-run)

#### Option A — Ollama (local, default in `.env.example`)

Install from [ollama.com](https://ollama.com) if `ollama` is not on your PATH. Then:

```bash
ollama pull mistral
# ollama serve   # Mac app often starts this automatically
curl http://localhost:11434/api/tags   # verify — should return JSON
```

Set in `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

#### Option B — OpenRouter (cloud, no local GPU)

Sign up at [openrouter.ai](https://openrouter.ai), create an API key, then set in `.env`:

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemma-3-4b-it
```

OpenRouter is often **faster than local Ollama** for Quick mode runs. Free models are available; paid models avoid rate limits.

Other OpenAI-compatible hosts use the same three vars — change `OPENAI_BASE_URL` and `OPENAI_MODEL` only:

| Host | `OPENAI_BASE_URL` | Example model |
|------|-------------------|---------------|
| OpenRouter | `https://openrouter.ai/api/v1` | `google/gemma-3-4b-it` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Together | `https://api.together.xyz/v1` | (see their model list) |

See also [LLM providers](#llm-providers) for timeout/retry settings on slow free tiers.

### 3. Start API (terminal 1 — stay in project root, venv active)

```bash
source .venv/bin/activate   # if not already active
uvicorn api.main:app --reload --port 8000
```

If `uvicorn: command not found`, use:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Verify (new tab):

```bash
curl http://localhost:8000/api/health
```

Expect `"status":"ok"`. When using Ollama, `"ollama_reachable":true` confirms the local server is up. With OpenRouter/Groq, `llm_provider` is `"openai"` and `configured_model` shows your cloud model — `ollama_reachable` is ignored for live runs.

**Leave this terminal running.**

### 4. Start React UI (terminal 2 — must be in `frontend/`)

```bash
cd frontend
npm install    # first time only
npm run dev
```

Do **not** run `npm run dev` from the project root — `package.json` is inside `frontend/`.

Open **http://localhost:5173**

- **Dry-run** checked → instant demo, no LLM (~10 sec)
- **Dry-run** unchecked + **Quick mode** → live LLM (~1–5 min; OpenRouter often faster than local Ollama)
- Upload `.txt` policy files, use **public specimen** presets, or bundled synthetic plans

**Public specimen policies** (from state regulators + FEMA) live in `data/public/`. Each file header includes the source URL and attribution. In the UI, choose **Public HO-3** or **Public flood pair** under Policy Documents.

**Upload your own policies (UI):**
1. Open the React UI → **Policy Documents**
2. Pick a preset (synthetic, public HO-3, public flood) or select **Upload my policies**
3. Optionally download sample `.txt` files (synthetic format, Travelers HO-3, FEMA NFIP)
4. Click **Analyze Plans**

**Upload via API:** See [API reference](#api-reference) below for all endpoints, form fields, and sample responses.

**CLI with custom files:**
```bash
python main.py --dry-run --policies data/synthetic/plan_a.txt data/synthetic/plan_b.txt
python main.py --policies data/public/travelers_ho3_nv.txt data/public/fema_nfip_dwelling_2021.txt
```

---

## Jupyter notebook (workflow inspection)

Run the agent **directly in Python** — no FastAPI or React server required. Chunking and Chroma indexing run in-process; only LLM calls go over the network (Ollama or OpenRouter).

**Notebook:** `notebooks/agent_workflow.ipynb`

### Setup (one time)

```bash
cd ~/capstone          # or your clone path
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # configure LLM_PROVIDER / API keys
```

Install Jupyter if needed:

```bash
pip install notebook
```

### Open and run

```bash
jupyter notebook notebooks/agent_workflow.ipynb
```

Or from VS Code: open `notebooks/agent_workflow.ipynb` and run cells top to bottom.

**Headless check (no Jupyter GUI):**

```bash
python scripts/verify_notebook.py
```

### What you get

| Cell | Purpose |
|------|---------|
| Setup | Loads `.env`, prints LLM provider and model |
| LLM ping | Quick connectivity test (few seconds) |
| Streaming run | Prints each LangGraph step as it completes (`intake` → `index` → `ingest` → ToT → `synthesize`) |
| Inspect | Session profile, normalized plans, branch scores, winning branch |
| Recommendation | Final markdown report |

Live inference with **Quick mode** (`beam_width=2`, `max_depth=2`) usually takes **1–5 minutes** depending on provider (OpenRouter often faster than local Ollama).

**Note:** The notebook does **not** call `localhost:8000`. Use the React UI when you want the web demo; use the notebook when you want step-by-step workflow visibility.

---

## CLI (no UI)

From project root with `source .venv/bin/activate`:

```bash
python main.py --dry-run                              # instant, no LLM
python main.py --beam-width 2 --max-depth 2           # live LLM (Ollama or OpenRouter)
python -m pytest tests/ -q                            # 41 tests
```

---

## API reference

Base URL: `http://localhost:8000` (React UI proxies `/api/*` from port 5173).

**Content type:** `POST` endpoints use `multipart/form-data` (form fields + optional file uploads).  
**Authentication:** none (local demo).  
**CORS:** allowed from `http://localhost:5173` and `http://127.0.0.1:5173`.

### Endpoint summary

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/health` | Backend status and Ollama reachability |
| `GET` | `/api/models` | Configured LLM provider and model names |
| `GET` | `/api/samples/{filename}` | Download bundled sample policy `.txt` files |
| `POST` | `/api/analyze` | Run full comparison pipeline (first run) |
| `POST` | `/api/follow-up` | Refinement question on an existing session |

### Typical flow

```
GET /api/health          → confirm API is up
GET /api/samples/...     → (optional) download demo policies
POST /api/analyze        → returns thread_id + recommendation
POST /api/follow-up      → same thread_id, updated recommendation (repeat)
```

### Shared response schema (`/api/analyze` and `/api/follow-up`)

Both `POST` endpoints return the same JSON shape:

| Field | Type | Description |
|-------|------|-------------|
| `thread_id` | string | Session ID — save for follow-up calls |
| `recommendation` | string | Final markdown report |
| `winning_branch` | object | ToT winner: `branch_id`, `interpretation`, `composite_score`, `thoughts[]` with per-plan payouts |
| `normalized_plans` | array | Extracted plan structs (`plan_id`, `carrier`, limits, deductibles, perils) |
| `session_profile` | object | Intake profile: age, location, `flood_zone`, `priority_weights` |
| `external_enrichment` | object | Census geocode + FEMA flood zone lookup (when APIs respond) |
| `conversation_history` | array | Last turns: `{ "role": "user"\|"assistant", "content": "..." }` |
| `llm_call_count` | int | LLM calls this run (1 in dry-run; ~9+ live quick mode) |
| `indexed_chunks` | int | Chroma chunks indexed for this run |
| `mode` | string | `"dry_run"` or provider label e.g. `"openai/google/gemma-3-4b-it"` |
| `error` | string \| null | Non-fatal pipeline error; `null` on success |

### Modes and timing

| Mode | Query param | LLM required | Typical duration |
|------|-------------|--------------|------------------|
| Dry-run | `dry_run=true` | No | ~1–10 sec |
| Live quick | `dry_run=false&quick=true` | Yes (Ollama or OpenRouter) | ~1–2 min (OpenRouter) / ~3–5 min (Ollama) |
| Live full | `dry_run=false&quick=false` | Yes | ~5–15+ min |

**Quick mode** sets `beam_width=2`, `max_depth=2`. **Full mode** uses `beam_width=3`, `max_depth=4`.

### Policy sources (for `/api/analyze`)

Policies are chosen in this priority order:

1. **Uploaded files** — `policies` form field (`.txt` only)
2. **`policy_preset`** — bundled public pairs (see table)
3. **`use_defaults=true`** or `policy_preset=synthetic` — bundled synthetic `plan_a` + `plan_b`

| `policy_preset` | Plans compared |
|-----------------|----------------|
| `synthetic` (default) | `data/synthetic/plan_a.txt` + `plan_b.txt` |
| `public_ho3` | Travelers HO-3 (NV) + State Farm HO-3 (OK) |
| `public_flood` | Travelers HO-3 (NV) + FEMA NFIP dwelling policy |

Upload limits: **max 3 files**, **500 KB each**, `.txt` extension only.

---

### `GET /api/health`

Liveness check for the FastAPI backend. Does not run the agent pipeline.

```bash
curl http://localhost:8000/api/health
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `status` | Always `"ok"` when the API process is running |
| `llm_provider` | `"ollama"` or `"openai"` (OpenRouter/Groq use `"openai"`) |
| `ollama_reachable` | `true` if `localhost:11434` responds (ignored for cloud providers) |
| `configured_model` | Active model label from `.env` |

**Sample response (OpenRouter):**

```json
{
  "status": "ok",
  "llm_provider": "openai",
  "ollama_reachable": false,
  "configured_model": "openai/google/gemma-3-4b-it"
}
```

With Ollama configured, `llm_provider` is `"ollama"` and `configured_model` is e.g. `"ollama/mistral"`. Dry-run works regardless of `ollama_reachable`.

---

### `GET /api/models`

Returns LLM configuration (useful for UI labels and debugging).

```bash
curl http://localhost:8000/api/models
```

**Response fields:**

| Field | Description |
|-------|-------------|
| `provider` | `LLM_PROVIDER` from `.env` |
| `ollama_model` | `OLLAMA_MODEL` (even when using OpenRouter) |
| `openai_model` | `OPENAI_MODEL` (OpenRouter/Groq model slug) |
| `label` | Human-readable active model |

**Sample response:**

```json
{
  "provider": "openai",
  "ollama_model": "mistral",
  "openai_model": "google/gemma-3-4b-it",
  "label": "openai/google/gemma-3-4b-it"
}
```

---

### `GET /api/samples/{filename}`

Download synthetic or public specimen policies for upload testing.

**Available filenames:**

| File | Source |
|------|--------|
| `plan_a.txt`, `plan_b.txt` | Synthetic demo pair |
| `travelers_ho3_nv.txt` | Public specimen — Nevada DOI |
| `statefarm_hw2136_ok.txt` | Public specimen — Oklahoma DOI |
| `shelter_ho3_ok.txt` | Public specimen — Oklahoma DOI |
| `fema_nfip_dwelling_2021.txt` | Public specimen — FEMA NFIP |

```bash
curl -O http://localhost:8000/api/samples/plan_a.txt
head -3 plan_a.txt
```

**Response:** `Content-Type: text/plain`, HTTP 200. Unknown filename → HTTP 404 `{ "detail": "Sample not found" }`.

---

### `POST /api/analyze`

Run the full agent pipeline:

`intake` → `enrich` (Census + FEMA) → `index` (Chroma) → `ingest` → ToT (`expand` → `ground` → `hard_gate` → `evaluate` → `prune`) → `synthesize`

**Query parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `dry_run` | `false` | Mock responses — no LLM or API key |
| `quick` | `false` | Shorter ToT (`beam_width=2`, `max_depth=2`) |

**Form fields (`multipart/form-data`):**

| Field | Default | Description |
|-------|---------|-------------|
| `age` | `35` | User age |
| `location` | `Cedar Park, TX` | Address for geocode / flood enrichment |
| `flood_zone` | `true` | Flood-zone risk flag |
| `home_value` | `350000` | Home value in dollars |
| `coverage_breadth` | `0.4` | Priority weight (0–1) |
| `low_cost` | `0.3` | Priority weight (0–1) |
| `few_exclusions` | `0.3` | Priority weight (0–1; should sum ~1.0) |
| `use_defaults` | `true` | Use bundled synthetic plans when no upload/preset |
| `policy_preset` | `synthetic` | `synthetic`, `public_ho3`, or `public_flood` |
| `policies` | — | Optional `.txt` uploads (max 3 files, 500 KB each) |

**Example — dry-run, bundled synthetic (fastest):**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=true&quick=true" \
  -F "use_defaults=true" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true" \
  -F "home_value=350000" \
  -F "coverage_breadth=0.4" \
  -F "low_cost=0.3" \
  -F "few_exclusions=0.3"
```

**Example — live OpenRouter (requires `.env` API key):**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=false&quick=true" \
  -F "use_defaults=true" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true"
```

**Example — public HO-3 preset:**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=true&quick=true" \
  -F "policy_preset=public_ho3" \
  -F "use_defaults=false" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true"
```

**Example — public flood pair (HO-3 vs NFIP):**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=true&quick=true" \
  -F "policy_preset=public_flood" \
  -F "use_defaults=false" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true"
```

**Example — upload custom policies:**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=true&quick=true" \
  -F "policies=@data/synthetic/plan_a.txt" \
  -F "policies=@data/synthetic/plan_b.txt" \
  -F "age=35" \
  -F "location=Cedar Park, TX" \
  -F "flood_zone=true" \
  -F "home_value=350000" \
  -F "coverage_breadth=0.4" \
  -F "low_cost=0.3" \
  -F "few_exclusions=0.3" \
  -F "use_defaults=false"
```

**Sample response (dry-run):**

```json
{
  "thread_id": "3251303162e6",
  "recommendation": "# Insurance Recommendation (Synthetic Dry Run)\n\n## Recommendation\n**Preferred plan:** plan_b for flood-zone profile without optional endorsements.\n...",
  "winning_branch": {
    "branch_id": "root-d1-0-d2-0",
    "interpretation": "Plan A excludes flood without HO-FLD; Plan B covers flood with sublimit",
    "composite_score": 0.77,
    "thoughts": [
      {
        "plan_id": "plan_a",
        "scenario_id": "flood",
        "claim": "Plan A pays $0 for flood without HO-FLD endorsement",
        "evidence_ids": ["plan_a:2"],
        "payout": 0.0,
        "deductible_applied": 0.0
      },
      {
        "plan_id": "plan_b",
        "scenario_id": "flood",
        "claim": "Plan B pays $95000 after $5K deductible on $100K sublimit",
        "evidence_ids": ["plan_b:1"],
        "payout": 95000.0,
        "deductible_applied": 5000.0
      }
    ],
    "scores": {
      "grounding": 0.9,
      "consistency": 0.85,
      "scenario_completeness": 0.8,
      "arithmetic_validity": 0.88,
      "priority_alignment": 0.75
    }
  },
  "normalized_plans": [
    {
      "plan_id": "plan_a",
      "carrier": "Synthetic Mutual",
      "dwelling_limit": 350000.0,
      "deductible": 2000.0
    },
    {
      "plan_id": "plan_b",
      "carrier": "Synthetic Shield",
      "dwelling_limit": 350000.0,
      "deductible": 5000.0
    }
  ],
  "session_profile": {
    "age": 35,
    "location": "Cedar Park, TX",
    "jurisdiction": "TX",
    "flood_zone": true,
    "priority_weights": {
      "coverage_breadth": 0.4,
      "low_cost": 0.3,
      "few_exclusions": 0.3
    }
  },
  "external_enrichment": {
    "location_query": "Cedar Park, TX"
  },
  "conversation_history": [
    { "role": "user", "content": "I'm 35, live in a flood zone in Cedar Park, TX..." },
    { "role": "assistant", "content": "# Insurance Recommendation..." }
  ],
  "llm_call_count": 1,
  "indexed_chunks": 54,
  "mode": "dry_run",
  "error": null
}
```

Save `thread_id` for follow-up calls. Live mode returns the same shape with `mode` set to your provider label and higher `llm_call_count`.

---

### `POST /api/follow-up`

Re-score with **session memory** — reuses `normalized_plans` and retrieval cache (skips full re-index/re-ingest). Appends your message to `conversation_history` and re-runs ToT at shallow depth.

**Query parameters:**

| Param | Default | Description |
|-------|---------|-------------|
| `dry_run` | `false` | Mock responses |
| `quick` | `true` | Shorter ToT (default `true` for follow-ups) |

**Form fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `thread_id` | yes | From a prior `/api/analyze` response |
| `message` | yes | Follow-up question or priority change |

**Good follow-up messages:**

- *"Prioritize lowest premium over coverage breadth."*
- *"What if the flood loss is $200K instead?"*
- *"Does Plan A cover water backup?"*

**Example — dry-run:**

```bash
curl -X POST "http://127.0.0.1:8000/api/follow-up?dry_run=true&quick=true" \
  -F "thread_id=3251303162e6" \
  -F "message=I care more about lowest cost than coverage breadth."
```

**Example — live OpenRouter:**

```bash
curl -X POST "http://127.0.0.1:8000/api/follow-up?dry_run=false&quick=true" \
  -F "thread_id=3251303162e6" \
  -F "message=Prioritize lowest premium over coverage breadth."
```

**Sample response:** Same JSON shape as `/api/analyze`, with the **same** `thread_id` and an updated `recommendation`. Session data is persisted under `data/sessions/{thread_id}.json`.

**Errors:**

| Condition | HTTP | Detail |
|-----------|------|--------|
| Unknown `thread_id` | 404 | `Unknown session thread_id=...` |
| Blank `message` | 400 | `Message is required.` |
| Missing form field | 422 | FastAPI validation error |

---

### HTTP error codes

| Code | When |
|------|------|
| 400 | Non-`.txt` upload, too many files (>3), file >500 KB, missing policies/preset, blank follow-up message |
| 404 | Unknown sample filename or `thread_id` |
| 422 | Malformed or missing required form fields |
| 502 | LLM provider returned an error |
| 503 | Ollama not running (live + `LLM_PROVIDER=ollama`), OpenRouter 429 rate limit, or invalid API key |
| 504 | LLM request timed out — retry with `quick=true` |

Error responses use FastAPI format: `{ "detail": "..." }`.

### Testing the API

**Smoke test (dry-run, no API key):**

```bash
bash scripts/smoke_test_api.sh
```

Covers `GET /api/health`, `GET /api/models`, and `POST /api/analyze?dry_run=true&quick=true`.

**Full pytest API suite:**

```bash
python -m pytest tests/test_api.py -q
```

**Manual live test (OpenRouter or Ollama configured in `.env`):**

```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=false&quick=true" \
  -F "use_defaults=true" -F "flood_zone=true"
# Use thread_id from response:
curl -X POST "http://127.0.0.1:8000/api/follow-up?dry_run=false&quick=true" \
  -F "thread_id=YOUR_THREAD_ID" \
  -F "message=Prioritize lowest cost."
```

### Browser E2E tests (Playwright)

Headless UI tests in `e2e/tests/ui.spec.ts` cover the React app: health banner, dry-run analyze, public HO-3 preset, quick-mode toggle, and upload validation.

Playwright **starts API + Vite automatically** (or reuses servers already on ports 8000 / 5173).

**One command (installs Chromium if needed):**

```bash
bash scripts/run_browser_tests.sh
```

**Manual steps:**

```bash
cd e2e
npm install
npx playwright install chromium   # first time only
npm test
```

**Tests run:**

| Test | What it verifies |
|------|------------------|
| loads health banner and profile form | Page renders, API health banner visible |
| dry-run analyze with quick mode | Full UI → API dry-run → recommendation shown |
| public HO-3 preset dry-run | Public specimen preset completes |
| quick mode checkbox toggles | Checkbox state without starting analysis |
| upload mode disables analyze | Analyze button disabled until file selected |

**Headed mode (watch the browser):**

```bash
cd e2e && npm run test:headed
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uvicorn: command not found` | `source .venv/bin/activate` or `python -m uvicorn api.main:app --reload --port 8000` |
| `npm` / `package.json` not found | Run `npm run dev` from `frontend/`, not project root |
| `ollama: command not found` | Use OpenRouter/Groq in `.env`, or install Ollama for local runs |
| API 503 on live analyze | Ollama not running (if `LLM_PROVIDER=ollama`), or invalid/missing `OPENAI_API_KEY` for cloud |
| UI can't reach API | Terminal 1 must have uvicorn on port 8000 |
| OpenRouter 429 rate limit | Retry after a minute, use Quick mode, or switch model |
| Playwright `Executable doesn't exist` | Run `cd e2e && npx playwright install chromium` or `bash scripts/run_browser_tests.sh` |

---

## LLM providers

| Provider | Env | Notes |
|---|---|---|
| **Ollama** (default in `.env.example`) | `LLM_PROVIDER=ollama` | Free, local, private — Mistral 7B, Llama 2/3 |
| **OpenRouter** | `LLM_PROVIDER=openai` + `OPENAI_BASE_URL=https://openrouter.ai/api/v1` | Cloud; free and paid models; often faster than local Ollama |
| **Groq / Together / OpenAI** | Same as OpenRouter — change `OPENAI_BASE_URL` + `OPENAI_MODEL` | OpenAI-compatible API |
| **Dry-run** | UI checkbox or `--dry-run` | No LLM; mock responses |

**OpenRouter** (recommended if you don't want to install Ollama):

```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=google/gemma-3-4b-it
```

**Ollama** (recommended for fully local / private runs):

```
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

Slow free-tier models: increase timeouts in `.env`:

```
LLM_READ_TIMEOUT=600
LLM_MAX_RETRIES=3
```

---

## Session memory and follow-up

After the first **Analyze Plans** run, the API returns a `thread_id`. Use the follow-up box in the UI or `POST /api/follow-up` (see [API reference](#post-apifollow-up)) to ask refinement questions. Session memory persists:

- `normalized_plans` and `retrieval_cache` (no full re-ingest)
- `session_profile` and `conversation_history` (last 8 turns)
- LangGraph checkpointer state keyed by `thread_id`

**Location enrichment:** On each run, the `enrich` node calls the US Census Geocoder and FEMA NFHL ArcGIS REST API to infer flood zone codes when the APIs respond.

---

## Project structure

```
├── api/main.py              # FastAPI backend
├── frontend/                # React + Vite UI
├── main.py                  # CLI entry point
├── notebooks/
│   └── agent_workflow.ipynb # Jupyter: streaming steps + branch inspection
├── src/
│   ├── runner.py            # Shared run_agent()
│   ├── graph/workflow.py    # LangGraph orchestrator
│   ├── crews/               # CrewAI agents (Ollama/OpenAI)
│   ├── memory/              # Checkpointer + session JSON store
│   └── tools/               # Retrieval, payout, validators, location APIs
├── data/synthetic/          # Bundled demo policies
├── data/public/             # Public specimen policies (NV/OK DOI, FEMA NFIP)
└── tests/
```

---

## Safety

- Synthetic/anonymized data only — no proprietary or client information
- No binding quotes or policy purchase
- Human escalation when evidence is missing or confidence is low

## Author

Preeti Dave — preetidav@gmail.com — June 2026

**GitHub:** https://github.com/cottonandcolor/insurance-policy-agent
