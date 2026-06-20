# Final Capstone Project Report — Section B

**Insurance Policy Comparison & Recommendation Agent**

**Author:** Preeti Dave  
**Email:** preetidav@gmail.com  
**Program:** Capstone — Agent Development  
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

---

## 2. System Goal, Scope, and Constraints

### System goal

Given a user profile (age, location, assets, risk tolerance, priorities) and a set of insurance plans, autonomously:

1. Collect and structure user requirements
2. Ingest and normalize policy documents
3. Retrieve grounded evidence for coverage claims
4. Explore multiple interpretive reasoning paths (Tree-of-Thought)
5. Score and prune weak hypotheses
6. Recommend the best-fit plan with cited tradeoffs

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
- LLM budget: ≤25 calls and ≤45 seconds per recommendation cycle
- Beam search: width 3, depth 4
- Agent is advisory only — human review required under defined escalation criteria
- No access to premium-binding or purchase APIs

---

## 3. Final System Architecture

The system is an integrated autonomous workflow combining **retrieval-augmented generation (RAG)**, **Tree-of-Thought (ToT) beam search**, **multi-agent role separation**, and **safety guardrails** — orchestrated by LangGraph and implemented with CrewAI agents.

### Architecture diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     LANGGRAPH ORCHESTRATOR                               │
├─────────────────────────────────────────────────────────────────────────┤
│ Phase 1   │ Profile Intake Agent (CrewAI)                               │
│ Phase 2   │ Chroma Index + Section-Aware Chunking                       │
│ Phase 3   │ Document & Retrieval Agent (CrewAI) → Normalized Schema     │
│ Phase 4–5 │ ToT Beam Loop:                                                │
│           │   Scenario Reasoning Agent → Ground (Retrieval)             │
│           │   → Hard Gates → Policy Critic Agent → Prune/Expand         │
│ Phase 6   │ Recommendation Synthesizer Agent (CrewAI)                   │
├─────────────────────────────────────────────────────────────────────────┤
│ Shared State: session_profile, branch_store, retrieval_cache (MCP-ready)│
└─────────────────────────────────────────────────────────────────────────┘
```

### How components work together

1. **Profile Intake** structures user requirements into a validated JSON profile with priority weights.
2. **Indexing** chunks synthetic policies by section and stores embeddings in Chroma for metadata-filtered retrieval.
3. **Document & Retrieval Agent** normalizes each plan into a comparable schema (limits, deductibles, exclusions, riders) with section citations.
4. **ToT loop (Phases 4–5):** The Scenario Reasoning Agent generates up to three interpretation branches per depth. Retrieval grounds each thought with chunk IDs. Hard gates reject uncited claims and arithmetic mismatches. The Policy Critic Agent scores surviving branches. The orchestrator prunes weak branches and advances beam search until depth 4 or convergence.
5. **Recommendation Synthesizer** converts the winning branch into a comparison table and ranked recommendation — only from validated, cited evidence.
6. **Safety layer** runs continuously: input validation, runtime gates, output constraints, and human escalation when evidence is insufficient.

---

## 4. Design Rationale

| Design choice | Rationale |
|---|---|
| **Retrieval required** | Policy docs exceed context windows; LLMs hallucinate coverage. Every claim must cite retrieved evidence. |
| **Multi-agent (6 roles)** | Separates intake, extraction, reasoning, criticism, and synthesis — prevents self-confirmation bias. |
| **ToT + beam search (width 3)** | Insurance comparison has high branching (plan × scenario × clause interpretation). Beam search explores alternatives without combinatorial explosion. |
| **Separate Policy Critic** | Adversarial evaluation before recommendation; enforces grounding gates independently of reasoning. |
| **LangGraph orchestrator** | Explicit state machine for phase routing, conditional ToT loop, and budget enforcement. |
| **CrewAI workers** | Role-specific personas and task prompts for each agent. |
| **Fail-closed safety** | Under uncertainty, escalate or clarify — do not guess. |
| **Synthetic corpus only** | Meets capstone privacy requirements; enables labeled eval scenarios. |

---

## 5. Design Evolution Across the Program

| Checkpoint | Key refinement |
|---|---|
| **Initial concept** | Defined insurance comparison problem, user, workflow phases, and why single-prompt LLM fails |
| **Retrieval decision** | Mandated RAG with section-aware chunking, jurisdiction metadata, hybrid retrieval, and citation enforcement |
| **Tree-of-Thought** | Replaced linear reasoning in Phases 4–5 with beam search, critic evaluation, pruning rubric, and MCP branch state |
| **Multi-agent architecture** | Defined six agents, hybrid sequential + graph coordination, and mixed communication (one-way, two-way, shared state) |
| **Safety & human oversight** | Added guardrails, evaluation metrics, escalation criteria, and fail-closed intervention policy |
| **Implementation** | Built LangGraph workflow, CrewAI agents, Chroma retrieval, hard gates, payout validator, dry-run mode, and unit tests |

The design evolved from a conceptual single-agent assistant to a **grounded, multi-agent, ToT-enabled decision-support system** with explicit safety controls — each checkpoint adding a testable layer rather than replacing prior work.

---

## 6. Implementation Summary

### Tools, frameworks, and models

| Component | Technology |
|---|---|
| Orchestration | **LangGraph** (`StateGraph`, conditional edges, `AgentState`) |
| Agent roles | **CrewAI** (5 specialist agents + orchestrator node) |
| LLM | **OpenAI GPT-4o-mini** (via CrewAI / LangChain) |
| Retrieval | **ChromaDB** with section-aware chunking |
| Schemas | **Pydantic** (profile, plans, thoughts, critic scores) |
| Validation | Deterministic payout calculator + hard-gate validators |
| Config | **python-dotenv** |
| Testing | **pytest** (routing, payout, hard gates, chunking) |

### Repository structure

```
capstone/
├── main.py                          # CLI entry point
├── requirements.txt
├── README.md
├── data/synthetic/                  # Synthetic policy documents
├── src/
│   ├── state.py                     # LangGraph state
│   ├── schemas.py                   # Pydantic models
│   ├── graph/workflow.py            # LangGraph orchestrator
│   ├── crews/                       # CrewAI agents, tasks, runner
│   ├── tools/                       # Retrieval, chunking, payout, validators
│   └── mocks/dry_run.py             # No-API demo mode
└── tests/
```

### Running the system

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --dry-run          # No API key required
python main.py                    # Live mode with OPENAI_API_KEY
python -m pytest tests/ -q        # Unit tests
```

---

## 7. Evaluation

### Evaluation criteria and methods

| Metric | Target | Method |
|---|---|---|
| Grounding rate | ≥95% | Verify each coverage claim has retrieved chunk ID |
| Scenario payout accuracy | ≥90% | Compare agent payout vs. deterministic calculator on synthetic labels |
| False-coverage rate | ≤2% | Check claims of coverage against known exclusions in eval set |
| Fallback success | 100% | Confirm hard-gate failures produce clarifying questions, not silent guesses |
| Latency P95 | ≤45s | Measure end-to-end recommendation cycle |
| Unit test pass rate | 100% | pytest on routing, payout, validators, chunking |

### Main results

**Unit tests (deterministic components):** Six tests pass covering policy chunking (≥3 sections extracted), flood sublimit payout calculation ($95K for Plan B on $150K loss), hard-gate rejection of uncited claims, prune logic, and ToT routing (continue vs. synthesize).

**Dry-run end-to-end workflow:** Successfully executes full pipeline — intake → index → ingest → ToT beam loop (expand, ground, hard gate, evaluate, prune) → synthesis — producing a cited comparison recommending Plan B for a flood-zone profile without optional endorsements.

**Strengths:**
- Every recommendation path requires citations before critic evaluation
- Separate Critic agent reduces self-confirmation bias
- ToT explores multiple clause interpretations (e.g., flood excluded vs. endorsement attached)
- Fail-closed behavior when branches are pruned
- Dry-run mode enables demo and testing without API costs

**Limitations:**
- Evaluated on synthetic policies only — metrics may not transfer to real carrier forms
- Live LLM output parsing still relies on JSON extraction heuristics
- MCP shared state designed but not fully deployed (in-memory state used)
- No production user study or broker validation yet
- Auto and life insurance modules extend the schema but were not fully benchmarked

---

## 8. Safety, Reliability, and Human Oversight

### Guardrails

- **Input:** Synthetic/public data only; required profile schema; jurisdiction metadata
- **Runtime:** Citation-required grounding gate; arithmetic validator; no purchase APIs; LLM/latency budget; separate Critic agent
- **Output:** Comparison template with disclaimer; block output if all branches fail hard gates

### Human intervention triggers

Human review is required when: evidence gaps persist after expanded retrieval; confidence is low with tied scores; all ToT branches are pruned; payout interpretations differ by >$25K; user corrects a misread term; or request is out of scope (binding quote, purchase, claims).

### Integrated safety strategy

```
Input validation → Grounded retrieval → ToT + Critic → Hard gates → Metrics check → Output OR escalate
```

The system functions as a **decision-support layer**, not a replacement for licensed advice. Safety controls are testable, auditable, and aligned with the fail-closed design principle established in the safety checkpoint.

---

## 9. Conclusion

This capstone delivers an autonomous **Insurance Policy Comparison & Recommendation Agent** that addresses a real consumer and broker need — comparing insurance plans by what happens at claim time, not just premium price. The final system integrates retrieval, multi-agent collaboration, Tree-of-Thought reasoning, and safety guardrails into a cohesive LangGraph + CrewAI implementation. Evaluation on synthetic data demonstrates correct payout logic, grounding enforcement, and end-to-end workflow execution, with clear paths for production hardening (MCP deployment, expanded eval corpus, human-in-the-loop UI).

---

## 10. References and Repository

- **Public GitHub Repository:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)
- **Presentation Video:** [Submitted separately in Canvas — 8–10 minutes]
- **Design checkpoints:** See `docs/` folder for retrieval, ToT, multi-agent, and safety submissions

---

