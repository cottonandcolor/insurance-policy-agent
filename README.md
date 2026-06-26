# Insurance Policy Comparison & Recommendation Agent

Autonomous multi-agent system for comparing insurance plans using grounded retrieval, Tree-of-Thought reasoning, and safety guardrails — with a **React demo UI** and **local Ollama** support.

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
| LLM | **Ollama** (Mistral / Llama) or OpenAI | Local open-source models by default |
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
- [Ollama](https://ollama.com) (optional — use **Dry-run** in the UI without it)

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

### 2. Ollama (optional — for live AI, not dry-run)

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

Expect `"status":"ok"` and `"ollama_reachable":true` when Ollama is running.

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
- **Dry-run** unchecked + **Quick mode** → live Ollama (~3–5 min)
- Upload `.txt` policy files, use **public specimen** presets, or bundled synthetic plans

**Public specimen policies** (from state regulators + FEMA) live in `data/public/`. See `data/public/SOURCES.md` for URLs and attribution. In the UI, choose **Public HO-3** or **Public flood pair** under Policy Documents.

**Upload your own policies (UI):**
1. Open the React UI → **Policy Documents**
2. Pick a preset (synthetic, public HO-3, public flood) or select **Upload my policies**
3. Optionally download sample `.txt` files (synthetic format, Travelers HO-3, FEMA NFIP)
4. Click **Analyze Plans**

**Upload via API:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analyze?dry_run=true&quick=true" \
  -F "policies=@/path/to/your_plan.txt" \
  -F "policies=@/path/to/another_plan.txt" \
  -F "age=35" -F "location=Cedar Park, TX" -F "flood_zone=true" \
  -F "home_value=350000" -F "coverage_breadth=0.4" \
  -F "low_cost=0.3" -F "few_exclusions=0.3"
```

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

Or from VS Code / Cursor: open `notebooks/agent_workflow.ipynb` and run cells top to bottom.

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
python main.py --beam-width 2 --max-depth 2           # live Ollama (quick)
python -m pytest tests/ -q                            # 31 tests
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uvicorn: command not found` | `source .venv/bin/activate` or `python -m uvicorn api.main:app --reload --port 8000` |
| `npm` / `package.json` not found | Run `npm run dev` from `frontend/`, not project root |
| `ollama: command not found` | Install Ollama app, or verify with `curl localhost:11434/api/tags` |
| API 503 on live analyze | Ollama not running — start Ollama app or check health endpoint |
| UI can't reach API | Terminal 1 must have uvicorn on port 8000 |

---

## LLM providers

| Provider | Env | Notes |
|---|---|---|
| **Ollama** (default) | `LLM_PROVIDER=ollama` | Free, local, private — Mistral 7B, Llama 2/3 |
| **OpenAI-compatible** | `LLM_PROVIDER=openai` + `OPENAI_BASE_URL` | OpenRouter, Groq, Together — set `OPENAI_API_KEY` and model |
| **Dry-run** | UI checkbox or `--dry-run` | No LLM; mock responses |

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
│   └── tools/               # Retrieval, payout, validators
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
