# Presentation Outline — 8–10 Minutes (Activity 7.1)

**Insurance Policy Comparison & Recommendation Agent**  
**Author:** Preeti Dave  
**Audience:** Technical  
**Target:** ~9:45 at conversational pace  
**GitHub:** [github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)  
**Slides:** `presentation.html`

---

## 1. Opening and project overview (~1 min)

**Slide 1 — Title**

**Bullets:**
- Insurance Policy Comparison & Recommendation Agent
- Preeti Dave — Agentic AI Capstone — June 2026
- **GitHub:** github.com/cottonandcolor/insurance-policy-agent

**Say:**
> Hi, I'm Preeti Dave. My capstone is an autonomous Insurance Policy Comparison & Recommendation Agent — a decision-support system for consumers and brokers.
>
> The problem: people compare insurance by premium, but the real question is what each plan pays when you file a claim.
>
> The users: consumers shopping for home, auto, or life insurance — and brokers comparing options for clients.
>
> The goal: given a user profile and policy documents, the agent ingests plans, runs loss-scenario analysis, explores ambiguous interpretations, and recommends a best-fit plan with citations — advisory only, not a binding quote.

---

## 2. Why this problem matters (~1 min)

**Slide 2 — Problem & User**

**Bullets:**
- 30–80 page policies; comparison sites rank by price
- Flood example: Plan A excludes flood; Plan B covers with sublimit
- Wrong plan → zero payout on a $150K loss
- Single prompt fails: too long, needs math, needs multiple interpretations

**Say:**
> This problem matters because the financial stakes are high and the information is buried. A consumer in a flood zone might see two plans with similar premiums — but one excludes flood unless you buy a rider, while another covers flood only up to a sublimit.
>
> A single LLM prompt can't solve this. That's why an agent-based approach — with retrieval, reasoning loops, and guardrails — is appropriate.

---

## 3. System architecture (~2 min)

**Slide 3 — Goal** · **Slide 4 — Architecture**

**Diagram:**
```
Profile Intake → Index & Normalize → ToT Beam Loop → Synthesize
                         ↑                  ↓
                    Chroma RAG         Critic + Hard Gates
```

**Bullets:**
- LangGraph orchestrator (state machine + conditional ToT loop)
- 6 specialist roles: intake, retrieval, reasoning, critic, synthesizer, orchestrator
- Chroma RAG + Pydantic schemas
- ToT: expand → ground → hard gates → critic → prune
- Shared state: profile, branches, retrieval cache
- CLI + FastAPI + React UI

**Say:**
> LangGraph orchestrates the workflow. Six specialist roles handle intake, normalization, reasoning, criticism, and synthesis. Chroma provides section-aware retrieval. The ToT loop generates interpretation branches, grounds them with evidence, runs hard gates on citations and arithmetic, scores with a separate critic, and prunes weak paths before synthesis.
>
> Users interact via CLI, FastAPI, or a React demo UI.

---

## 4. Key design decisions (~1.5 min)

**Slide 5 — Design Decisions**

| Decision | Why |
|----------|-----|
| Retrieval required | Prevent hallucinated coverage |
| Multi-agent (separate Critic) | Reduce self-confirmation bias |
| ToT + beam search | Handle ambiguous clauses |
| Fail-closed safety | Escalate when evidence is missing |

**Say:**
> Four decisions from across the program define the design. Retrieval is mandatory — no citation, no claim. A separate Policy Critic evaluates branches the Reasoning agent proposed. Tree-of-Thought beam search explores alternatives when language is ambiguous. The system fails closed — it escalates rather than guessing.
>
> Also: hybrid coordination — sequential intake, iterative ToT graph, sequential synthesis. Synthetic data only for privacy.

---

## 5. Evaluation and results (~1.5 min)

**Slide 6 — Evolution** (brief) · **Slide 8 — Evaluation**

**Evolution (30 sec):** Concept → Retrieval → ToT → Multi-agent → Safety → Runnable implementation (31 tests, React UI, Ollama).

**Results bullets:**
- ✅ 31/31 pytest tests pass
- ✅ Dry-run E2E completes full pipeline (<10 sec)
- ✅ Hard gates reject uncited claims
- ✅ Plan B flood payout: $95K on $150K loss; recommended for flood-zone profile
- ⚠️ Synthetic data only
- ⚠️ Live Ollama quick mode ~3–5 min (exceeds 45s design target)

**Say:**
> I evaluated on three levels. Unit tests: 31 cases pass. Deterministic scenario: Plan B pays $95,000 after sublimit and deductible on a $150,000 flood loss; dry-run recommends Plan B. End-to-end dry-run completes in under ten seconds. Live Ollama works but takes several minutes.
>
> Limitations I'll state honestly: synthetic policies only; full grounding-rate automation on a held-out eval set is still in progress.

---

## 6. Repository and implementation (~1.5 min)

**Slide 7 — Demo** · **Slide 10 — GitHub**

**Show:**
- GitHub README
- `python main.py --dry-run` terminal output
- Recommendation snippet (plan_b, citations)

**Bullets:**
- Python, LangGraph, Chroma, Ollama/OpenAI
- `main.py`, `api/`, `frontend/`, `tests/`
- `docs/README.md` — design checkpoints M1–M6

**Say:**
> The full implementation is public on GitHub at github.com/cottonandcolor/insurance-policy-agent. Run `python main.py --dry-run` for an instant full-pipeline demo. `pytest tests/ -q` runs 31 tests. Here's a sample run — Plan B is recommended because it covers flood in the base form without requiring an optional endorsement.

**Demo plan:** Use **dry-run** on camera (reliable, <10s). Mention React UI + Ollama live mode as optional.

---

## 7. Closing reflection (~45 sec)

**Slide 9 — Safety** (brief) · **Slide 10 — Conclusion**

**Safety (15 sec):** Citations required, no purchase APIs, escalate on evidence gap or all branches pruned.

**Closing bullets:**
- Takeaway: grounded multi-agent design beats single-prompt comparison
- Worked: flood through-line, payout validator, dry-run demo
- Next: eval automation, faster inference, real-form validation
- **GitHub:** github.com/cottonandcolor/insurance-policy-agent

**Say:**
> The main takeaway: insurance comparison is a real problem where grounded, multi-step agent design matters more than a clever prompt. What worked well: the flood scenario as a through-line, deterministic payout validation, and dry-run mode for demos. What I'd improve next: automated safety metrics, faster live inference, and validation on public carrier forms.
>
> Thank you — code and docs are on GitHub.

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
- [ ] Screen-share: README + `python main.py --dry-run`
- [ ] Practice with timer (stay under 10 min)
- [ ] Upload video to Canvas
- [ ] Verify alignment with `FINAL_REPORT.md`
