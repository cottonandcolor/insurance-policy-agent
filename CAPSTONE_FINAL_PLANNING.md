# Capstone Final Planning — Module 7 Checkpoint

**Insurance Policy Comparison & Recommendation Agent**  
**Author:** Preeti Dave · preetidav@gmail.com  
**GitHub:** [github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent)  
**Date:** June 2026

> **Purpose:** Consolidate Modules 1–6 checkpoints into one design story for the final report, GitHub repository, and 8–10 minute presentation. No submission required for this checkpoint — use this document to prepare final deliverables.

---

## 1. Cohesive Design Story (One Paragraph)

Consumers compare insurance by premium, but the real risk is **what happens at claim time** — exclusions, sublimits, and riders buried in long policy documents. A single-prompt LLM cannot solve this: documents exceed context windows, comparisons require structured extraction and arithmetic, and ambiguous clauses need multiple interpretations before recommending. My capstone evolved from **problem framing** → **grounded retrieval** → **Tree-of-Thought reasoning with a separate critic** → **six-agent role separation** → **fail-closed safety and human escalation** → **working implementation** (LangGraph orchestrator, Chroma RAG, specialist agent prompts, React demo UI, Ollama live mode, 31 pytest cases). The result is an **advisory, citation-backed decision-support system** — not a quote engine or purchase flow — built entirely on synthetic/public data.

---

## 2. Module Checkpoint Map

| Module / checkpoint | Artifact in repo | Key decision | Carried into final system |
|---|---|---|---|
| **M1–2: Initial concept** | `option-a-insurance-policy-comparison-agent.md` | Insurance comparison problem; user = consumer/broker; why single prompt fails | Problem statement, scope, workflow phases |
| **M3: Retrieval** | Same doc (retrieval section) | Section-aware chunking, Chroma, citation-required claims, jurisdiction metadata | `src/tools/chunking.py`, `src/tools/retrieval.py`, hard grounding gates |
| **M4: Reasoning / ToT** | Same doc (ToT section) | Beam search (width 3, depth 4), critic scoring, prune thresholds, branch state | `src/graph/workflow.py` ToT loop, `src/graph/routing.py` |
| **M5: Multi-agent** | `multi-agent-architecture-submission.md` | 6 roles; hybrid sequential + graph coordination; Reasoning ↔ Critic two-way loop | LangGraph phases + `src/crews/` role prompts |
| **M6: Safety & evaluation** | `safety-guardrails-submission.md` | Hard gates, metrics, escalation criteria, fail-closed output | `src/tools/validators.py`, `src/tools/payout.py`, intervention rules in report |
| **M7: Integration** | `FINAL_REPORT.md`, `README.md`, `api/`, `frontend/` | Runnable system: CLI + FastAPI + React; Ollama local LLM; test suite | End-to-end demo, public GitHub |

---

## 3. What Changed Since Earlier Checkpoints

| Area | Original plan | Current implementation | Report/presentation note |
|---|---|---|---|
| **LLM runtime** | CrewAI + OpenAI | Direct Ollama/OpenAI HTTP (`src/llm/client.py`); role separation via prompts | *Agent roles unchanged; execution layer simplified for Python 3.9 + local demo* |
| **Demo surface** | CLI only | CLI + FastAPI + React UI | Show UI in video; dry-run for speed |
| **Tests** | 6 core tests | 31 tests + smoke scripts | Update evaluation slide |
| **Latency target** | ≤45s | Live Ollama quick mode ~3–5 min; dry-run &lt;10s | Acknowledge as limitation; use dry-run in video |
| **MCP memory** | Designed | In-memory `AgentState` (MCP-ready, not deployed) | List as future work |
| **Data** | Synthetic only | Unchanged — `data/synthetic/plan_a.txt`, `plan_b.txt` | Compliant with privacy rule |

---

## 4. Final Report Planning (Template Mapping)

Use `FINAL_REPORT.md` as the base. Map to typical PDF/Word template sections:

| Template section | Source / status | Action before submit |
|---|---|---|
| **Title & author** | Report § header | ✅ Done |
| **Problem & user** | Report §1 | ✅ Done |
| **System goal & scope** | Report §2 | ✅ Done |
| **Architecture** | Report §3 + diagram | ⚠️ Update: mention `src/llm/`, React/FastAPI, Ollama |
| **Design rationale** | Report §4 | ⚠️ Replace “CrewAI workers” with “role-specific LLM prompts + LangGraph” |
| **Evolution across program** | Report §5 | ✅ Add row: “Demo UI + Ollama integration” |
| **Implementation** | Report §6 | ⚠️ Update stack table, repo tree, run instructions from `README.md` |
| **Evaluation & results** | Report §7 | ⚠️ Change “6/6 tests” → “31/31 tests”; note smoke script |
| **Safety & human oversight** | Report §8 | ✅ Done |
| **Conclusion** | Report §9 | ⚠️ Mention live + dry-run modes |
| **References & repo link** | Report §10 | ✅ GitHub public |

**Export:** Copy into course Word/PDF template → export PDF/DOCX for Canvas.

---

## 5. Final Presentation Plan (8–10 Minutes)

Use `PRESENTATION_OUTLINE.md` and `presentation.html`. Recommended flow for a **technical audience**:

| Time | Slide | Focus | Demo |
|---|---|---|---|
| 0:00–0:30 | Title | Name, project, GitHub URL on screen | — |
| 0:30–1:30 | Problem | Flood-zone example; premium vs payout | — |
| 1:30–2:15 | Goal | Input/output; advisory scope; synthetic data | — |
| 2:15–3:45 | Architecture | LangGraph → agents → Chroma → ToT loop → gates | Show diagram |
| 3:45–5:15 | Design decisions | RAG, multi-agent, ToT, fail-closed | — |
| 5:15–6:15 | Evolution | M1→M6 timeline (one slide, not six docs) | — |
| 6:15–8:00 | **Demo** | React UI **or** `python main.py --dry-run` | **Dry-run** (reliable in 10s) |
| 8:00–9:00 | Evaluation | 31 tests; flood payout $95K; limitations | Terminal: `pytest -q` |
| 9:00–9:45 | Safety | Guardrails + escalation triggers | — |
| 9:45–10:00 | Close | GitHub URL again; thank you | — |

**Recording tips:**
- Lead demo with **dry-run** (guaranteed finish on camera); mention live Ollama as optional follow-up.
- State GitHub URL verbally and on slide 1 and 10.
- Screen-share: README → UI or CLI → one recommendation snippet citing plan_b.

---

## 6. GitHub Repository Readiness

| Item | Status | Notes |
|---|---|---|
| Public repo | ✅ | `cottonandcolor/insurance-policy-agent` |
| README with quick start | ✅ | CLI, API, React, Ollama, dry-run |
| Runnable entry points | ✅ | `main.py`, `api/main.py`, `frontend/` |
| Synthetic data only | ✅ | No proprietary data |
| Tests | ✅ | `./scripts/run_tests.sh` → 31 passed |
| Design docs linked | ✅ | `docs/README.md` |
| `.env` not committed | ✅ | `.env.example` provided |
| Ignore local tooling | ⚠️ | Add `.node/`, `.ollama/`, `tsconfig.tsbuildinfo` to `.gitignore` if desired |

**Reviewer path:** README → `docs/` → `python main.py --dry-run` → `pytest tests/ -q`

---

## 7. Planning Questions — Self-Assessment

| Question | Answer |
|---|---|
| **Does the report show how pieces fit together?** | Yes in §3 architecture + §5 evolution. Update §6 for current stack. |
| **Does the presentation focus on key ideas?** | Yes if you limit to problem → architecture → 4 decisions → demo → eval → safety. Avoid reading weekly docs. |
| **Is GitHub public and understandable?** | Yes. README is the on-ramp. |
| **Do results support claims?** | Partially. Deterministic tests strong; full grounding/false-coverage metrics on synthetic labels still qualitative. Be explicit about limitations. |
| **Can you explain strengths and limitations?** | **Strengths:** citations, critic separation, ToT, fail-closed, runnable demo. **Limits:** synthetic only, live latency, JSON parse heuristics, MCP not deployed. |

---

## 8. Pre-Submission Checklist

### Report
- [ ] Update `FINAL_REPORT.md` §6–7 for Ollama, React, 31 tests
- [ ] Export to PDF/DOCX via course template
- [ ] Upload to Canvas

### Presentation
- [ ] Practice with timer (8–10 min)
- [ ] Record video (screen + voice)
- [ ] Show GitHub URL and one dry-run demo
- [ ] Upload video to Canvas

### Repository
- [ ] Confirm `main` pushed and public
- [ ] Run `./scripts/run_tests.sh` once before recording
- [ ] Verify no secrets in repo

### Alignment
- [ ] Problem, architecture, and flood example consistent across report, slides, and README
- [ ] Same GitHub URL everywhere

---

## 9. Strengths vs. Limitations (For Q&A)

**Strengths**
- Real problem with concrete flood scenario
- Integrated stack: retrieval + ToT + multi-role agents + guardrails
- Deterministic payout validator backs LLM arithmetic
- Runnable without API (dry-run) or with local Ollama
- Testable: 31 pytest cases + API smoke script

**Limitations**
- Synthetic policies only — not validated on real carrier forms
- Live Ollama exceeds original 45s latency target
- Full safety metrics (grounding rate, false-coverage) not automated on eval set yet
- Advisory only — no production broker study

---

## 10. File Index for Final Deliverables

| Deliverable | Primary file |
|---|---|
| Final report | `FINAL_REPORT.md` → export PDF/DOCX |
| Presentation slides | `presentation.html` |
| Presentation script | `PRESENTATION_OUTLINE.md` |
| Code & demo | GitHub repo + `README.md` |
| Design history | `docs/README.md` + checkpoint `.md` files |
| This planning doc | `CAPSTONE_FINAL_PLANNING.md` |

---

*Use this checkpoint to align report, video, and repo before the graded capstone submission.*
