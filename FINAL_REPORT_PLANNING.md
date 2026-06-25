# Final Capstone Report Planning Template (Activity 7.1)

**Author:** Preeti Dave · preetidav@gmail.com  
**Program:** Agentic AI — Building Autonomous Systems for Real-World Applications  
**Date:** June 2026

---

## 1. Project title

**Insurance Policy Comparison & Recommendation Agent**

A grounded, multi-agent decision-support system that compares insurance plans by scenario-based payouts and cited policy language — not premium price alone.

---

## 2. Problem and user

**Real-world problem:** Choosing auto, home, or life insurance is a high-stakes financial decision, but comparison tools focus on premium while ignoring what happens at claim time. Policy documents are 30–80 pages of dense legal language. Two similarly priced plans can behave very differently — e.g., in a flood zone, one plan may exclude flood unless an optional rider is purchased, while another covers flood only up to a sublimit.

**Intended users:**
- **Primary:** Individual consumers comparing plans for their household
- **Secondary:** Insurance brokers evaluating options for a client

**Why it matters:** Without scenario-based analysis grounded in actual policy text, consumers can select a cheaper plan that leaves them exposed to tens of thousands in out-of-pocket loss. An agent-based approach is appropriate because the task requires multi-step extraction, cross-document comparison, arithmetic scenario modeling, ambiguous clause interpretation, and adversarial validation — not a single prompt.

---

## 3. System goal and scope

**What the system does:** Given a user profile (age, location, assets, risk factors, priority weights) and one or more insurance policy documents, the agent autonomously:

1. Structures user requirements (intake)
2. Indexes and normalizes policy documents into a comparable schema
3. Retrieves grounded evidence for coverage claims
4. Explores multiple interpretive paths via Tree-of-Thought beam search
5. Scores and prunes weak hypotheses with a separate critic
6. Produces a cited comparison table and ranked recommendation

**Successful performance looks like:** Recommendations cite specific policy sections; payout claims match deterministic validation; ambiguous clauses (e.g., flood coverage) are explored before committing; the system escalates or fails closed when evidence is insufficient.

**Boundaries and constraints:**
- **In scope:** Loss-scenario comparison, multi-plan tables, synthetic/public/anonymized policies, advisory output
- **Out of scope:** Binding quotes, policy purchase, claims filing, proprietary/client data, medical underwriting
- **Compute budget:** ≤25 LLM calls per cycle; beam width 3, depth 4 (quick mode: width 2, depth 2)
- **Data:** Synthetic corpus only for capstone (privacy compliant)

---

## 4. Final system architecture

The system integrates **retrieval**, **Tree-of-Thought reasoning**, **multi-agent role separation**, **shared state memory**, and **safety guardrails** — orchestrated by **LangGraph**.

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
│ Shared state: session_profile, active_branches, retrieval_cache │
│ Interfaces: CLI (main.py) · FastAPI (api/) · React UI (frontend/)│
└─────────────────────────────────────────────────────────────────┘
```

**Six agent roles:**

| Agent | Responsibility |
|-------|----------------|
| Orchestrator | Phase routing, ToT loop control, budget enforcement |
| Profile Intake | User profile, priorities, flood-zone risk |
| Document & Retrieval | Policy normalization, Chroma retrieval |
| Scenario Reasoning | ToT branch generation, loss scenarios |
| Policy Critic | Adversarial scoring, prune recommendations |
| Recommendation Synthesizer | Markdown comparison + cited recommendation |

**How components work together:** Intake and ingestion run sequentially to produce validated structured inputs. The ToT loop runs iteratively: reasoning proposes interpretations, retrieval attaches chunk IDs, hard gates block uncited or arithmetically wrong claims, the critic scores survivors, and the orchestrator prunes or expands until depth limit or convergence. Synthesis runs only on the winning validated branch.

**Memory:** `AgentState` holds `session_profile`, `active_branches` (branch store), and `retrieval_cache` across the ToT loop (MCP-ready design; in-memory for capstone).

**Human intervention:** Escalate when evidence is missing, all branches are pruned, scores are tied with low grounding, or payout interpretations diverge by >$25K.

---

## 5. Design evolution across the program

| Module / checkpoint | Refinement | Why it improved the system |
|---------------------|------------|----------------------------|
| **M1–2: Initial concept** | Problem, user, workflow phases; why single-prompt LLM fails | Established scope and autonomous workflow structure |
| **M3: Retrieval** | Mandatory RAG, section chunking, citation gates, jurisdiction metadata | Prevented hallucinated coverage claims |
| **M4: Tree-of-Thought** | Beam search replaced linear reasoning; critic + pruning rubric | Handled ambiguous clause interpretation (flood excluded vs. sublimit) |
| **M5: Multi-agent** | Six roles; hybrid sequential + graph coordination; Reasoning ↔ Critic loop | Separated extraction from evaluation; reduced self-confirmation bias |
| **M6: Safety** | Hard gates, evaluation metrics, escalation criteria, fail-closed policy | Made reliability testable and auditable |
| **M7: Integration** | LangGraph implementation, React/FastAPI demo, Ollama live mode, 31 tests | Delivered a runnable autonomous system, not just a design |

**Key change during implementation:** LLM execution moved from CrewAI to direct Ollama/OpenAI HTTP calls (`src/llm/client.py`) for Python 3.9 compatibility and local demo — **agent roles and orchestration unchanged**.

---

## 6. Implementation overview

| Component | Technology |
|-----------|------------|
| Orchestration | LangGraph (`StateGraph`, conditional edges) |
| Agent prompts | Role-specific prompts in `src/llm/prompts.py` + `src/crews/runner.py` |
| LLM | Ollama (Mistral, default) or OpenAI via `src/llm/client.py` |
| Retrieval | ChromaDB + section-aware chunking |
| Schemas | Pydantic (profile, plans, thoughts, critic scores) |
| Validation | Deterministic payout calculator + hard-gate validators |
| API | FastAPI (`api/main.py`) — upload, analyze, health |
| Frontend | React + Vite (`frontend/`) |
| Testing | pytest (31 tests) + `scripts/run_tests.sh`, `scripts/smoke_test_api.sh` |

**Run instructions:**
```bash
python main.py --dry-run              # CLI, no LLM
uvicorn api.main:app --port 8000      # API
cd frontend && npm run dev            # UI at localhost:5173
python -m pytest tests/ -q            # Tests
```

---

## 7. Evaluation and results

**Criteria and methods:**

| Metric | Target | Method |
|--------|--------|--------|
| Grounding rate | ≥95% | Verify coverage claims have retrieved chunk IDs |
| Payout accuracy | ≥90% | Compare vs. deterministic calculator on synthetic labels |
| False-coverage rate | ≤2% | Check claims against known exclusions |
| Fallback success | 100% | Hard-gate failures → clarify/escalate, not silent guess |
| Unit tests | 100% pass | pytest on chunking, payout, gates, routing, API |

**Main results:**
- **31/31 pytest tests pass** (core logic, API dry-run, mocked live workflow, LLM client)
- **Dry-run E2E:** Full pipeline completes; recommends **plan_b** for flood-zone profile (Plan A excludes flood without HO-FLD; Plan B covers with $100K sublimit → $95K payout after $5K deductible on $150K loss)
- **Hard gates:** Uncited claims rejected; arithmetic mismatches flagged
- **Live Ollama:** Quick mode produces cited markdown comparison (~3–5 min)

**Strengths:** Citation discipline, separate critic, ToT for ambiguity, fail-closed behavior, runnable demo without API key (dry-run).

**Limitations:** Synthetic policies only; full grounding/false-coverage metrics not yet automated on held-out eval set; live latency exceeds original 45s target.

---

## 8. Safety and reliability considerations

**Guardrails:**
- **Input:** Synthetic/public data only; required profile schema; `.txt` upload validation
- **Runtime:** Citation-required grounding gate; payout arithmetic validator; no purchase/bind APIs; LLM call budget; separate Policy Critic agent
- **Output:** Comparison template with “not a binding quote” disclaimer; block final output if all ToT branches fail hard gates

**Monitoring / fallback:** Dry-run mode for deterministic demo; API returns 503 if Ollama unreachable in live mode; critic fallback scoring when LLM JSON is malformed; ingest falls back to mock normalization on schema failure.

**Human oversight triggers:** Evidence gap after expanded retrieval; low confidence with tied scores; all branches pruned; >$25K payout divergence across branches; user correction of misread term; out-of-scope requests (binding quote, purchase, claims).

**Safety flow:**
```
Input validation → Grounded retrieval → ToT + Critic → Hard gates → Output OR escalate
```

---

## 9. Limitations and next steps

**Current limitations:**
- Evaluated on synthetic policies only — metrics may not transfer to real carrier forms
- Live Ollama inference is slow (~3–5 min quick mode) vs. design target of ≤45s
- LLM JSON output parsing uses extraction heuristics
- MCP shared state designed but not fully deployed
- No production user study or licensed broker validation
- Auto/life modules extend schema but flood home scenario is primary benchmark

**Next steps:**
1. Build labeled synthetic eval set with automated grounding/false-coverage scoring
2. Deploy MCP or persistent session store for follow-up “what if” re-scoring
3. Add streaming progress UI for long live runs
4. Validate on public insurance form samples with broker review
5. Upgrade to Python 3.10+ for modern CrewAI if desired

---

## 10. Public GitHub repository

**URL:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)

**Repository contents:**

| Requirement | Location |
|-------------|----------|
| README (problem, architecture, setup, usage) | `README.md` |
| Main code | `main.py`, `src/`, `api/`, `frontend/` |
| Sample inputs | `data/synthetic/plan_a.txt`, `plan_b.txt` |
| Evaluation artifacts | `tests/`, `scripts/run_tests.sh` |
| Design history | `docs/README.md`, checkpoint `.md` files |
| Run instructions | README Quick start + CLI section |

**Reviewer path:** Clone → `pip install -r requirements.txt` → `python main.py --dry-run` → `pytest tests/ -q`

---

*Copy sections into the course Word/PDF template for final Canvas submission.*
