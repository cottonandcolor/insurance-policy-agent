# Final Presentation Planning Outline (Activity 7.1)

**Insurance Policy Comparison & Recommendation Agent**  
**Author:** Preeti Dave  
**Audience:** Technical  
**Target length:** 8–10 minutes (~1,000 words spoken)  
**GitHub:** [github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)

---

## 1. Opening and project overview (~1 min)

**Slide:** Title, name, GitHub URL

**Say:**
> Hi, I'm Preeti Dave. My capstone is an autonomous **Insurance Policy Comparison & Recommendation Agent** — a decision-support system for consumers and brokers.
>
> **The problem:** People compare insurance by premium, but the real question is what each plan pays when you file a claim.
>
> **The user:** Consumers shopping for home, auto, or life insurance — and brokers comparing options for clients.
>
> **The goal:** Given a user profile and policy documents, the agent autonomously ingests plans, runs loss-scenario analysis, explores ambiguous interpretations, and recommends a best-fit plan **with citations** — advisory only, not a binding quote.

**Bullets:**
- Problem: opacity in policy documents
- Users: consumers + brokers
- Goal: cited, scenario-based recommendation

---

## 2. Why this problem matters (~1 min)

**Slide:** Flood-zone example — Plan A vs. Plan B

**Say:**
> This problem matters because the financial stakes are high and the information is buried. A consumer in a flood zone might see two plans with similar premiums — but Plan A excludes flood unless you buy a rider, while Plan B covers flood only up to a sublimit. Picking the wrong plan can mean zero payout on a $150,000 loss.
>
> A single LLM prompt can't solve this: documents are too long, comparisons need structured extraction and math, and ambiguous clauses need multiple interpretations before recommending. That's why an **agent-based** approach — with retrieval, reasoning loops, and guardrails — is appropriate.

**Bullets:**
- 30–80 page policies; comparison sites rank by price
- Flood example: exclude vs. sublimit
- Single prompt → hallucination risk; needs RAG + multi-step reasoning

---

## 3. System architecture (~2 min)

**Slide:** Architecture diagram

```
Profile Intake → Index & Normalize → ToT Beam Loop → Synthesize
                         ↑                  ↓
                    Chroma RAG         Critic + Hard Gates
```

**Say:**
> The architecture has four layers working together.
>
> **LangGraph** orchestrates the workflow as a state machine with a conditional ToT loop.
>
> **Six specialist roles** handle intake, document normalization, scenario reasoning, adversarial criticism, and synthesis — plus the orchestrator.
>
> **Chroma** provides section-aware retrieval so every claim can cite a policy chunk.
>
> **The ToT loop** in the middle generates interpretation branches, grounds them with evidence, runs hard gates on citations and arithmetic, scores with a separate critic, and prunes weak paths before synthesis.
>
> Shared state — profile, branch store, retrieval cache — carries memory across the loop. Users interact via CLI, FastAPI, or a React demo UI.

**Bullets:**
- LangGraph orchestrator
- 6 agents / roles
- Chroma RAG + Pydantic schemas
- ToT: expand → ground → gate → critic → prune
- CLI + FastAPI + React

---

## 4. Key design decisions (~1.5 min)

**Slide:** Four decisions table

| Decision | Why |
|----------|-----|
| Retrieval required | Prevent hallucinated coverage |
| Multi-agent (separate Critic) | Reduce self-confirmation bias |
| ToT + beam search | Handle ambiguous clauses |
| Fail-closed safety | Escalate when evidence is missing |

**Say:**
> Four decisions from across the program define the design.
>
> **Retrieval is mandatory** — no citation, no claim.
>
> **A separate Policy Critic** evaluates branches the Reasoning agent proposed — they don't grade their own work.
>
> **Tree-of-Thought beam search** explores alternatives when language is ambiguous — like whether flood is covered in the base form.
>
> **Fail-closed safety** — if all branches fail hard gates, the system escalates or clarifies; it doesn't guess.

**Also mention (briefly):** hybrid coordination (sequential intake → iterative graph → sequential synthesis); synthetic data only for privacy.

---

## 5. Evaluation and results (~1.5 min)

**Slide:** Results + limitations side by side

**Say:**
> I evaluated on three levels.
>
> **Unit tests:** 31 pytest cases pass — chunking, payout math, hard gates, routing, API, and mocked live workflow.
>
> **Deterministic scenario:** On a $150,000 flood loss, Plan B pays $95,000 after sublimit and deductible; Plan A pays zero without an optional endorsement. The dry-run pipeline recommends Plan B for a flood-zone profile.
>
> **End-to-end:** Dry-run completes the full intake → index → ToT → synthesis loop in under ten seconds. Live Ollama quick mode works but takes several minutes.
>
> **Limitations I'll state honestly:** synthetic policies only; full grounding-rate automation on a held-out eval set is still in progress; live latency exceeds my original 45-second target.

**Bullets:**
- ✅ 31/31 tests pass
- ✅ Hard gates reject uncited claims
- ✅ E2E dry-run recommends plan_b
- ⚠️ Synthetic data only
- ⚠️ Live Ollama ~3–5 min

---

## 6. Repository and implementation (~1.5 min)

**Slide:** GitHub screenshot + terminal demo

**Say:**
> The full implementation is public on GitHub at **github.com/cottonandcolor/insurance-policy-agent**.
>
> The README explains setup. You can run **`python main.py --dry-run`** for an instant full-pipeline demo, or start the React UI with the FastAPI backend. **`pytest tests/ -q`** runs 31 tests. Design checkpoints from Modules 1–6 are linked from `docs/README.md`.
>
> *[Screen share: run dry-run, show recommendation snippet with plan_b and citations]*

**Demo plan (choose one):**
- **Recommended for video:** `python main.py --dry-run` (reliable, <10s)
- **Optional mention:** React UI + Ollama live mode

**Bullets:**
- Python, LangGraph, Chroma, Ollama/OpenAI
- `main.py`, `api/`, `frontend/`, `tests/`
- Synthetic policies in `data/synthetic/`

---

## 7. Closing reflection (~45 sec)

**Slide:** Takeaway + GitHub URL

**Say:**
> The main takeaway: insurance comparison is a real problem where **grounded, multi-step agent design** matters more than a clever prompt. Integrating retrieval, Tree-of-Thought, multi-agent criticism, and fail-closed guardrails produced a system that actually runs and can be tested.
>
> What worked well: the flood scenario as a through-line, deterministic payout validation backing the LLM, and dry-run mode for demos.
>
> What I'd improve next: automated safety metrics on a labeled eval set, faster live inference, and validation on public carrier forms with broker review.
>
> Thank you — code and docs are on GitHub.

**Bullets:**
- Takeaway: grounded multi-agent decision support beats single-prompt comparison
- Worked: RAG + critic + ToT + runnable demo
- Next: eval automation, latency, real-form validation
- **GitHub:** github.com/cottonandcolor/insurance-policy-agent

---

## Timing summary

| Section | Time |
|---------|------|
| 1. Opening | 1:00 |
| 2. Why it matters | 1:00 |
| 3. Architecture | 2:00 |
| 4. Design decisions | 1:30 |
| 5. Evaluation | 1:30 |
| 6. Repository + demo | 1:30 |
| 7. Closing | 0:45 |
| **Total** | **~9:45** |

---

## Recording checklist

- [ ] GitHub URL on title slide and closing slide
- [ ] State URL verbally at least once
- [ ] Screen-share: README + dry-run terminal output
- [ ] Practice with timer (stay under 10 min)
- [ ] Upload video to Canvas

---

*Use with `presentation.html` slides. Copy into course PDF template if required.*
