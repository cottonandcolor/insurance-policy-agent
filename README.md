# Insurance Policy Comparison & Recommendation Agent

Autonomous multi-agent system for comparing insurance plans using grounded retrieval, Tree-of-Thought reasoning, and safety guardrails.

**Capstone Project — Section B Final Submission**

---

## Problem

Consumers and brokers comparing auto, home, or life insurance face dozens of plans with different coverage limits, deductibles, exclusions, and riders buried in dense policy documents. This agent goes beyond premium comparison to analyze **what each plan actually pays** in realistic loss scenarios — with citations to policy language.

## Architecture

| Layer | Technology | Role |
|---|---|---|
| Orchestrator | LangGraph | State machine, ToT beam loop, budget enforcement |
| Agents | CrewAI | Profile intake, document extraction, reasoning, critic, synthesis |
| Retrieval | ChromaDB | Section-aware chunking over synthetic policies |
| Validation | Pydantic + hard gates | Schema enforcement, citation checks, payout calculator |
| Safety | Fail-closed design | Escalation to human when evidence is insufficient |

### Six-agent workflow

1. **Profile Intake** — collect user profile and priority weights  
2. **Document & Retrieval** — normalize plans into comparable schema  
3. **Scenario Reasoning** — generate ToT interpretation branches  
4. **Policy Critic** — score and prune branches  
5. **Recommendation Synthesizer** — produce cited comparison table  
6. **Orchestrator (LangGraph)** — route phases and enforce budgets  

## Quick start

### Prerequisites

- Python 3.9+
- OpenAI API key (optional for dry-run mode)

### Setup

```bash
git clone https://github.com/cottonandcolor/insurance-policy-agent.git
cd insurance-policy-agent

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # Add OPENAI_API_KEY for live mode
```

### Run

```bash
# Dry-run — no API key required
python main.py --dry-run

# Live mode with OpenAI
export OPENAI_API_KEY=your_key
python main.py

# Build retrieval index only
python main.py --build-index

# Run unit tests
python -m pytest tests/ -q
```

### Example output

The agent compares synthetic Plan A and Plan B for a flood-zone homeowner and recommends the plan with better flood coverage for the user's stated priorities — with cited policy sections and scenario payouts.

## Project structure

```
├── main.py                    # CLI entry point
├── FINAL_REPORT.md            # Final capstone report (Section B)
├── PRESENTATION_OUTLINE.md    # 8–10 min video script
├── requirements.txt
├── data/synthetic/            # Synthetic policy documents (public)
├── src/
│   ├── graph/workflow.py      # LangGraph orchestrator
│   ├── crews/                 # CrewAI agents and tasks
│   ├── tools/                 # Retrieval, payout, validators
│   ├── schemas.py             # Pydantic models
│   └── mocks/dry_run.py       # Demo mode without API
├── tests/                     # Unit tests
└── docs/                      # Checkpoint design documents
```

## Design documents

| Document | Description |
|---|---|
| `option-a-insurance-policy-comparison-agent.md` | Initial concept + retrieval + ToT design |
| `multi-agent-architecture-submission.md` | Multi-agent roles and coordination |
| `safety-guardrails-submission.md` | Safety metrics and human intervention |
| `IMPLEMENTATION.md` | CrewAI + LangGraph implementation guide |

## Evaluation

- **Unit tests:** chunking, payout calculator, hard gates, ToT routing
- **Dry-run E2E:** full pipeline without API calls
- **Metrics targets:** ≥95% grounding rate, ≥90% payout accuracy, ≤2% false-coverage rate

## Safety

- Synthetic/anonymized data only — no proprietary or client information
- No binding quotes or policy purchase
- Human escalation when evidence is missing or confidence is low
- Fail-closed: clarify or escalate under uncertainty — never guess

## License

MIT (or your chosen license)

## Author

Preeti Dave — preetidav@gmail.com — June 2026
