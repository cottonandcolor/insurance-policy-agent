# Final Capstone Project Report — Section B

**Insurance Policy Comparison & Recommendation Agent**

**Author:** Preeti Dave  
**Email:** preetidav@gmail.com  
**Program:** Agentic AI — Building Autonomous Systems for Real-World Applications  
**Date:** June 2026  
**GitHub Repository:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)

---

## 1. Problem Statement and Intended User

### Real-world problem

Choosing insurance — auto, home, or life — is one of the most consequential financial decisions a household makes, yet it remains one of the most opaque. Consumers face dozens of plans across carriers, each with different coverage limits, deductibles, exclusions, waiting periods, and premium structures buried in 30–80 page policy documents written in dense legal language. Existing comparison websites rank plans primarily by premium price, ignoring the critical question: **what actually happens when I file a claim?**

A consumer in a flood zone may see two plans with similar premiums, but one excludes flood entirely while the other covers it only up to a sublimit. Without scenario-based analysis grounded in policy language, the cheaper plan can leave the household exposed to catastrophic out-of-pocket loss.

### Intended user

- **Primary:** Individual consumers comparing insurance plans for themselves or their household
- **Secondary:** Insurance brokers evaluating options for a client

The agent serves users who need decision support — not a binding quote — to compare total cost of ownership across realistic loss scenarios, identify hidden coverage gaps, and receive a justified recommendation with citations to actual policy sections.

An agent-based approach is appropriate because the task requires multi-step extraction, cross-document comparison, arithmetic scenario modeling, ambiguous clause interpretation, and adversarial validation — not a single prompt.

---

## 2. System Goal, Scope, and Constraints

### System goal

Given a user profile (age, location, assets, risk factors, priority weights) and one or more insurance policy documents, the agent autonomously:

1. Collects and structures user requirements
2. Indexes and normalizes policy documents into a comparable schema
3. Retrieves grounded evidence for coverage claims
4. Explores multiple interpretive reasoning paths (Tree-of-Thought)
5. Scores and prunes weak hypotheses with a separate critic
6. Recommends the best-fit plan with cited tradeoffs

**Successful performance looks like:** Recommendations cite specific policy sections; payout claims match deterministic validation; ambiguous clauses (e.g., flood coverage) are explored before committing; the system escalates or fails closed when evidence is insufficient.

### Scope (in)

- Auto, home, and life insurance plan comparison
- Loss-scenario payout analysis (flood, theft, liability, etc.)
- Multi-plan comparison tables with citations
- Follow-up "what if" re-scoring (e.g., add a driver, change priorities)
- Synthetic/public/anonymized policy documents only

### Scope (out)

- Binding quotes or policy purchase
- Claims filing or underwriting decisions
- Proprietary, confidential, or client-specific policy data
- Medical or health insurance suitability beyond document scope

### Constraints

- All policy data must be public, synthetic, or anonymized
- LLM budget: ≤25 calls per recommendation cycle; beam width 3, depth 4 (quick mode: width 2, depth 2)
- Original latency target: ≤45 seconds per cycle (live Ollama quick mode: ~3–5 minutes in practice)
- Agent is advisory only — human review required under defined escalation criteria
- No access to premium-binding or purchase APIs

---

## 3. Final System Architecture

The system integrates **retrieval-augmented generation (RAG)**, **Tree-of-Thought (ToT) beam search**, **multi-agent role separation**, **shared state memory**, and **safety guardrails** — orchestrated by **LangGraph** with role-specific LLM prompts executed via direct Ollama/OpenAI HTTP calls.

### Architecture diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  LANGGRAPH ORCHESTRATOR                          │
├─────────────────────────────────────────────────────────────────┤
│ Phase 1  │ Profile Intake Agent → session_profile               │
│ Phase 2  │ Chroma index + section-aware chunking                │
│ Phase 3  │ Document & Retrieval Agent → normalized_plans      │
│ Phase 4–5│ ToT beam loop:                                       │
│          │   Scenario Reasoning → Ground (RAG) → Hard gates     │
│          │   → Policy Critic → Prune/expand (depth 1–4)         │
│ Phase 6  │ Recommendation Synthesizer → final_recommendation    │
├─────────────────────────────────────────────────────────────────┤
│ Shared state: session_profile, active_branches, retrieval_cache   │
│ Interfaces: CLI (main.py) · FastAPI (api/) · React (frontend/) │
└─────────────────────────────────────────────────────────────────┘
```

### Six agent roles

| Agent | Responsibility |
|-------|----------------|
| Orchestrator | Phase routing, ToT loop control, budget enforcement |
| Profile Intake | User profile, priorities, flood-zone risk |
| Document & Retrieval | Policy normalization, Chroma retrieval |
| Scenario Reasoning | ToT branch generation, loss scenarios |
| Policy Critic | Adversarial scoring, prune recommendations |
| Recommendation Synthesizer | Markdown comparison + cited recommendation |

### How components work together

1. **Profile Intake** structures user requirements into a validated JSON profile with priority weights.
2. **Indexing** chunks synthetic policies by section and stores embeddings in Chroma for metadata-filtered retrieval.
3. **Document & Retrieval Agent** normalizes each plan into a comparable schema (limits, deductibles, exclusions, riders) with section citations.
4. **ToT loop (Phases 4–5):** The Scenario Reasoning Agent generates up to three interpretation branches per depth. Retrieval grounds each thought with chunk IDs. Hard gates reject uncited claims and arithmetic mismatches. The Policy Critic Agent scores surviving branches. The orchestrator prunes weak branches and advances beam search until depth 4 or convergence.
5. **Recommendation Synthesizer** converts the winning branch into a comparison table and ranked recommendation — only from validated, cited evidence.
6. **Safety layer** runs continuously: input validation, runtime gates, output constraints, and human escalation when evidence is insufficient.

**Memory:** `AgentState` holds `session_profile`, `active_branches` (branch store), and `retrieval_cache` across the ToT loop (MCP-ready design; in-memory for capstone).

---

## 4. Design Rationale

| Design choice | Rationale |
|---|---|
| **Retrieval required** | Policy docs exceed context windows; LLMs hallucinate coverage. Every claim must cite retrieved evidence. |
| **Multi-agent (6 roles)** | Separates intake, extraction, reasoning, criticism, and synthesis — prevents self-confirmation bias. |
| **ToT + beam search (width 3)** | Insurance comparison has high branching (plan × scenario × clause interpretation). Beam search explores alternatives without combinatorial explosion. |
| **Separate Policy Critic** | Adversarial evaluation before recommendation; enforces grounding gates independently of reasoning. |
| **LangGraph orchestrator** | Explicit state machine for phase routing, conditional ToT loop, and budget enforcement. |
| **Role-specific LLM prompts** | Each agent step uses dedicated prompts (`src/llm/prompts.py`); executed via Ollama or OpenAI HTTP client. |
| **Fail-closed safety** | Under uncertainty, escalate or clarify — do not guess. |
| **Synthetic corpus only** | Meets capstone privacy requirements; enables labeled eval scenarios. |

---

## 5. Design Evolution Across the Program

| Module / checkpoint | Key refinement | Why it improved the system |
|---|---|---|
| **M1–2: Initial concept** | Problem, user, workflow phases; why single-prompt LLM fails | Established scope and autonomous workflow structure |
| **M3: Retrieval** | Mandatory RAG, section chunking, citation gates, jurisdiction metadata | Prevented hallucinated coverage claims |
| **M4: Tree-of-Thought** | Beam search replaced linear reasoning; critic + pruning rubric | Handled ambiguous clause interpretation (flood excluded vs. sublimit) |
| **M5: Multi-agent** | Six roles; hybrid sequential + graph coordination; Reasoning ↔ Critic loop | Separated extraction from evaluation; reduced self-confirmation bias |
| **M6: Safety** | Hard gates, evaluation metrics, escalation criteria, fail-closed policy | Made reliability testable and auditable |
| **M7: Integration** | LangGraph implementation, React/FastAPI demo, Ollama live mode, 31 tests | Delivered a runnable autonomous system, not just a design |

**Key implementation change:** LLM execution moved from CrewAI to direct Ollama/OpenAI HTTP calls (`src/llm/client.py`) for Python 3.9 compatibility and local demo — agent roles and orchestration unchanged.

The design evolved from a conceptual single-agent assistant to a **grounded, multi-agent, ToT-enabled decision-support system** with explicit safety controls — each checkpoint adding a testable layer rather than replacing prior work.

---

## 6. Implementation Summary

### Tools, frameworks, and models

| Component | Technology |
|---|---|
| Orchestration | **LangGraph** (`StateGraph`, conditional edges, `AgentState`) |
| Agent prompts | Role-specific prompts in `src/llm/prompts.py` + `src/crews/runner.py` |
| LLM | **Ollama** (Mistral, default) or **OpenAI** via `src/llm/client.py` |
| API | **FastAPI** (`api/main.py`) — upload, analyze, health |
| Frontend | **React + Vite** (`frontend/`) |
| Retrieval | **ChromaDB** with section-aware chunking |
| Schemas | **Pydantic** (profile, plans, thoughts, critic scores) |
| Validation | Deterministic payout calculator + hard-gate validators |
| Config | **python-dotenv** |
| Testing | **pytest** (31 tests) + `scripts/run_tests.sh`, `scripts/smoke_test_api.sh` |

### Repository structure

```
capstone/
├── main.py                          # CLI entry point
├── api/main.py                      # FastAPI backend
├── frontend/                        # React demo UI
├── requirements.txt
├── README.md
├── data/synthetic/                  # Synthetic policy documents
├── src/
│   ├── runner.py                    # Shared run_agent()
│   ├── state.py                     # LangGraph state
│   ├── schemas.py                   # Pydantic models
│   ├── graph/workflow.py            # LangGraph orchestrator
│   ├── llm/                         # Ollama/OpenAI client + prompts
│   ├── crews/runner.py              # Agent step runners
│   ├── tools/                       # Retrieval, chunking, payout, validators
│   └── mocks/dry_run.py             # No-LLM demo mode
├── tests/
└── scripts/                         # run_tests.sh, smoke_test_api.sh
```

### Running the system

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python main.py --dry-run                    # CLI, no LLM required
uvicorn api.main:app --port 8000            # API backend
cd frontend && npm install && npm run dev   # UI at localhost:5173
python -m pytest tests/ -q                  # 31 tests
```

Set `LLM_PROVIDER=ollama` or `openai` in `.env` for live mode.

---

## 7. Evaluation and Results

### Evaluation criteria and methods

| Metric | Target | Method |
|---|---|---|
| Grounding rate | ≥95% | Verify each coverage claim has retrieved chunk ID |
| Scenario payout accuracy | ≥90% | Compare agent payout vs. deterministic calculator on synthetic labels |
| False-coverage rate | ≤2% | Check claims of coverage against known exclusions in eval set |
| Fallback success | 100% | Confirm hard-gate failures produce clarifying questions, not silent guesses |
| Unit test pass rate | 100% | pytest on routing, payout, validators, chunking, API, LLM mocks |
| Latency (design target) | ≤45s | End-to-end recommendation cycle (live Ollama: ~3–5 min quick mode) |

### Main results

**Unit tests:** **31/31 pytest tests pass** — policy chunking, flood sublimit payout ($95K for Plan B on $150K loss), hard-gate rejection of uncited claims, prune logic, ToT routing, API dry-run, mocked live workflow, and LLM client parsing.

**Dry-run end-to-end workflow:** Successfully executes full pipeline — intake → index → ingest → ToT beam loop (expand, ground, hard gate, evaluate, prune) → synthesis — producing a cited comparison recommending **plan_b** for a flood-zone profile without optional endorsements.

**Live Ollama:** Quick mode produces cited markdown comparison (~3–5 minutes; multiple sequential LLM calls).

**Strengths:**
- Every recommendation path requires citations before critic evaluation
- Separate Critic agent reduces self-confirmation bias
- ToT explores multiple clause interpretations (e.g., flood excluded vs. endorsement attached)
- Fail-closed behavior when branches are pruned
- Dry-run mode enables demo and testing without API costs
- Runnable via CLI, API, and React UI

**Limitations:**
- Evaluated on synthetic policies only — metrics may not transfer to real carrier forms
- Full grounding/false-coverage metrics not yet automated on a held-out eval set
- Live LLM output parsing relies on JSON extraction heuristics
- Live Ollama latency exceeds original 45-second design target
- MCP shared state designed but not fully deployed (in-memory state used)
- No production user study or broker validation yet

---

## 8. Safety, Reliability, and Human Oversight

### Guardrails

- **Input:** Synthetic/public data only; required profile schema; `.txt` upload validation; jurisdiction metadata
- **Runtime:** Citation-required grounding gate; arithmetic validator; no purchase APIs; LLM call budget; separate Critic agent
- **Output:** Comparison template with "not a binding quote" disclaimer; block output if all branches fail hard gates

### Monitoring and fallback

- Dry-run mode for deterministic demo and testing
- API returns 503 if Ollama is unreachable in live mode
- Critic fallback scoring when LLM JSON is malformed
- Ingest falls back to mock normalization on schema validation failure
- Payout grounding overwrites LLM arithmetic with deterministic calculator in ground node

### Human intervention triggers

Human review is required when: evidence gaps persist after expanded retrieval; confidence is low with tied scores; all ToT branches are pruned; payout interpretations differ by >$25K; user corrects a misread term; or request is out of scope (binding quote, purchase, claims).

### Integrated safety strategy

```
Input validation → Grounded retrieval → ToT + Critic → Hard gates → Metrics check → Output OR escalate
```

The system functions as a **decision-support layer**, not a replacement for licensed advice. Safety controls are testable, auditable, and aligned with the fail-closed design principle established in the safety checkpoint.

---

## 9. Limitations, Next Steps, and Conclusion

### Current limitations

- Synthetic policies only — production validation on public carrier forms not yet done
- Live Ollama inference slow vs. design latency target
- JSON parse heuristics for LLM structured output
- MCP persistent memory not deployed
- Advisory only — no licensed broker validation study

### Next steps

1. Build labeled synthetic eval set with automated grounding/false-coverage scoring
2. Deploy MCP or persistent session store for follow-up "what if" re-scoring
3. Add streaming progress UI for long live runs
4. Validate on public insurance form samples with broker review
5. Upgrade to Python 3.10+ if adopting modern CrewAI runtime

### Conclusion

This capstone delivers an autonomous **Insurance Policy Comparison & Recommendation Agent** that addresses a real consumer and broker need — comparing insurance plans by what happens at claim time, not just premium price. The final system integrates retrieval, multi-agent collaboration, Tree-of-Thought reasoning, and safety guardrails into a cohesive LangGraph implementation with a public GitHub repository, React demo UI, and 31 passing tests. Evaluation on synthetic data demonstrates correct payout logic, grounding enforcement, and end-to-end workflow execution.

---

## 10. References and Repository

- **Public GitHub Repository:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)
- **Presentation Video:** Submitted separately in Canvas (8–10 minutes)
- **Design checkpoints:** See `docs/README.md` for retrieval, ToT, multi-agent, and safety submissions

**Reviewer path:** Clone → `pip install -r requirements.txt` → `python main.py --dry-run` → `pytest tests/ -q`

---
