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
| Agents | CrewAI | Profile intake, extraction, reasoning, critic, synthesis |
| LLM | **Ollama** (Mistral / Llama) or OpenAI | Local open-source models by default |
| Retrieval | ChromaDB | Section-aware chunking over policy documents |

---

## Quick start — React demo

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Ollama](https://ollama.com) (optional — use dry-run mode without it)

### 1. Backend setup

```bash
git clone https://github.com/cottonandcolor/insurance-policy-agent.git
cd insurance-policy-agent

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
```

### 2. Ollama (local open-source models)

```bash
ollama pull mistral          # or: ollama pull llama3.1:8b
ollama serve                 # usually runs automatically on Mac
```

Set in `.env`:
```
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
```

### 3. Start API

```bash
uvicorn api.main:app --reload --port 8000
```

### 4. Start React UI

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

- Check **Dry-run** for instant demo (no Ollama needed)
- Uncheck dry-run + run Ollama for live local AI
- Upload `.txt` policy files or use bundled synthetic plans

---

## CLI (original)

```bash
python main.py --dry-run
python main.py                    # uses LLM_PROVIDER from .env
python -m pytest tests/ -q
```

---

## LLM providers

| Provider | Env | Notes |
|---|---|---|
| **Ollama** (default) | `LLM_PROVIDER=ollama` | Free, local, private — Mistral 7B, Llama 2/3 |
| **OpenAI** | `LLM_PROVIDER=openai` | Set `OPENAI_API_KEY` |
| **Dry-run** | UI checkbox or `--dry-run` | No LLM; mock responses |

---

## Project structure

```
├── api/main.py              # FastAPI backend
├── frontend/                # React + Vite UI
├── main.py                  # CLI entry point
├── src/
│   ├── runner.py            # Shared run_agent()
│   ├── graph/workflow.py    # LangGraph orchestrator
│   ├── crews/               # CrewAI agents (Ollama/OpenAI)
│   └── tools/               # Retrieval, payout, validators
├── data/synthetic/          # Bundled demo policies
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
