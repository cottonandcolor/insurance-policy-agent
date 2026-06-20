# Presentation Outline — 8–10 Minutes

**Insurance Policy Comparison & Recommendation Agent**  
**For Canvas video submission**

> Target: ~9 minutes at conversational pace (~900–1,000 words spoken)

---

## Slide 1 — Title (30 sec)

**Title:** Insurance Policy Comparison & Recommendation Agent  
**Subtitle:** A grounded multi-agent system for insurance decision support  
**Your name, program, date**

**Say:**  
"Hi, I'm [Name]. My capstone project is an autonomous agent that helps consumers and brokers compare insurance plans — not just by price, but by what each plan actually pays when you file a claim."

---

## Slide 2 — Problem & User (1 min)

**Bullets:**
- 30–80 page policy documents, dense legal language
- Comparison sites rank by premium, not coverage
- Example: flood zone — one plan excludes flood, another covers with sublimit
- **Users:** consumers and insurance brokers

**Say:**  
"The real-world problem is opacity. Choosing the wrong plan can leave a household exposed to tens of thousands in out-of-pocket loss. My agent targets consumers and brokers who need scenario-based comparison grounded in actual policy language."

---

## Slide 3 — System Goal (45 sec)

**Bullets:**
- Input: user profile + insurance plans
- Output: cited comparison table + ranked recommendation
- Scope: advisory only — no binding quotes or purchases
- Data: synthetic/public policies only

**Say:**  
"The system goal is to autonomously collect user requirements, analyze plans across loss scenarios, and recommend the best fit with citations. It's decision support — not a replacement for licensed advice."

---

## Slide 4 — Architecture Overview (1.5 min)

**Show diagram:**

```
Profile Intake → Index & Extract → ToT Beam Loop → Synthesize
                      ↑                    ↓
                  Chroma RAG         Critic + Hard Gates
```

**Bullets:**
- LangGraph orchestrator
- 6 CrewAI agents
- Chroma retrieval
- ToT beam search (width 3, depth 4)

**Say:**  
"The architecture has three layers. LangGraph orchestrates the workflow. CrewAI agents handle specialized roles — intake, extraction, reasoning, criticism, and synthesis. Chroma provides grounded retrieval. The Tree-of-Thought loop in the middle explores multiple interpretations of ambiguous policy language — like whether flood is covered — before committing to a recommendation."

---

## Slide 5 — Key Design Decisions (1.5 min)

**Bullets:**
| Decision | Why |
|---|---|
| Retrieval required | Prevent hallucinated coverage |
| Multi-agent | Separate reasoning from criticism |
| ToT + beam search | Handle interpretive ambiguity |
| Fail-closed safety | Escalate when evidence is missing |

**Say:**  
"Four design decisions define the project. First, retrieval is mandatory — every claim must cite a policy chunk. Second, a separate Policy Critic agent prevents self-confirmation bias. Third, Tree-of-Thought beam search explores alternatives when clauses are ambiguous. Fourth, the system fails closed — it escalates to a human rather than guessing."

---

## Slide 6 — Design Evolution (1 min)

**Timeline:**
1. Initial concept — problem framing
2. Retrieval checkpoint — grounding strategy
3. ToT checkpoint — beam search + critic
4. Multi-agent checkpoint — six roles
5. Safety checkpoint — guardrails + escalation
6. Implementation — LangGraph + CrewAI

**Say:**  
"The design evolved across six checkpoints. Each added a testable layer — from concept to retrieval to reasoning to agents to safety to working code — without throwing away prior work."

---

## Slide 7 — Implementation Demo (1.5 min)

**Show:**
- GitHub repo URL
- `python main.py --dry-run` terminal output
- Sample recommendation snippet

**Bullets:**
- Python, LangGraph, CrewAI, Chroma, OpenAI GPT-4o-mini
- Dry-run mode for demo without API
- Unit tests for payout, gates, routing

**Say:**  
"The implementation is on GitHub at [YOUR URL]. The repo includes a LangGraph workflow, five CrewAI agents, Chroma retrieval, and a dry-run mode that runs the full pipeline without an API key. Here's a sample run comparing two synthetic flood scenarios — Plan B is recommended because it covers flood in the base form without requiring an optional endorsement."

---

## Slide 8 — Evaluation Results (1 min)

**Bullets:**
- ✅ 6/6 unit tests pass
- ✅ Dry-run E2E completes full pipeline
- ✅ Hard gates reject uncited claims
- ✅ Payout calculator: Plan B flood = $95K on $150K loss
- ⚠️ Synthetic data only — not yet validated on real carrier forms

**Say:**  
"Evaluation covers deterministic components and end-to-end workflow. Unit tests verify chunking, payout math, hard gates, and routing. The dry-run demonstrates the full agent loop. The main limitation is that all evaluation uses synthetic policies — production deployment would require validation on public insurance forms and broker review."

---

## Slide 9 — Safety & Human Oversight (45 sec)

**Bullets:**
- Guardrails: citations required, no purchase APIs, LLM budget
- Escalate when: evidence gap, low confidence, all branches pruned
- Metrics: ≥95% grounding, ≥90% payout accuracy

**Say:**  
"Safety is built in at every layer. Runtime guardrails block uncited claims and cap compute. The agent escalates to a human when evidence is missing or interpretations diverge by more than twenty-five thousand dollars. This is a decision-support layer with mandatory human review at defined thresholds."

---

## Slide 10 — Conclusion & GitHub (30 sec)

**Bullets:**
- Autonomous grounded insurance comparison agent
- Multi-agent + ToT + RAG + safety controls
- **GitHub:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)
- Questions?

**Say:**  
"In summary, this capstone delivers an autonomous insurance comparison agent that integrates retrieval, multi-agent collaboration, Tree-of-Thought reasoning, and safety guardrails. The full code and documentation are on GitHub. Thank you."

---

## Recording tips

- **Length:** Aim for 8–10 minutes; practice once with a timer
- **Screen share:** Show GitHub README + one `--dry-run` terminal execution
- **Audience:** Technical — use terms like RAG, beam search, hard gates
- **Required:** Clearly state GitHub URL verbally and on screen
- **Canvas:** Upload video file directly to the assignment

## Checklist before submitting

- [ ] Record presentation video and upload to Canvas
- [ ] Push repo to public GitHub with README and core files
- [ ] Record 8–10 min video referencing the repo
- [ ] Upload FINAL_REPORT (PDF/DOCX or text) to Canvas
- [ ] Upload presentation video to Canvas
- [ ] Verify report and presentation align on problem, architecture, and results
