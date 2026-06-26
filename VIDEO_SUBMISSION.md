# Capstone Presentation Video Submission

**Author:** Preeti Dave  
**Email:** preetidav@gmail.com  
**Program:** Agentic AI — Building Autonomous Systems for Real-World Applications  
**Project:** Insurance Policy Comparison & Recommendation Agent  
**Date:** June 2026

---

## Presentation Video Link

**[REPLACE WITH YOUR VIDEO URL BEFORE UPLOADING TO CANVAS]**

Example hosts: YouTube (unlisted), Vimeo, or Loom

Suggested URL format:
`https://www.youtube.com/watch?v=YOUR_VIDEO_ID`

---

## Brief Summary of Presentation

This 8–10 minute technical presentation covers my capstone: an **Insurance Policy Comparison & Recommendation Agent** — a grounded, multi-agent decision-support system for consumers and insurance brokers.

**Problem and significance:** People compare insurance by premium, but the real risk is what each plan pays at claim time. Policy documents are 30–80 pages of dense legal language; two similarly priced plans can behave very differently (e.g., flood excluded vs. sublimited coverage).

**System goal:** Given a user profile and policy documents, the agent autonomously ingests plans, runs loss-scenario analysis, explores ambiguous interpretations with Tree-of-Thought beam search, and produces a cited comparison and ranked recommendation. The system is advisory only — not a binding quote or purchase flow.

**Architecture:** LangGraph orchestrates six specialist roles across six phases: Profile Intake → Chroma indexing → Document & Retrieval → ToT beam loop (Scenario Reasoning, RAG grounding, hard gates, Policy Critic, prune/expand) → Recommendation Synthesizer. Users interact via CLI, FastAPI, or a React demo UI. The LLM runs locally through Ollama (Mistral) or optionally through OpenAI.

**Key design decisions:** Mandatory retrieval (no citation, no claim); separate Policy Critic to reduce self-confirmation bias; Tree-of-Thought for ambiguous clauses; fail-closed safety with human escalation when evidence is insufficient.

**Evaluation and results:** 34/34 pytest tests pass. Dry-run end-to-end completes in under 10 seconds and recommends Plan B for a flood-zone profile ($95K payout on $150K loss after sublimit and deductible). Live Ollama quick mode produces cited comparisons in ~3–5 minutes.

**GitHub repository:** [https://github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent) — includes README, main code (`main.py`, `src/`, `api/`, `frontend/`), synthetic and public specimen policies, and tests.

**Strengths:** Citation discipline, separate critic, ToT for ambiguity, deterministic payout validation, runnable demo without an API key.

**Limitations and next steps:** Synthetic policies as primary benchmark; automated grounding metrics on a held-out eval set in progress; live latency exceeds original 45-second target; broker validation on public carrier forms as future work.

**Demo shown in video:** `python main.py --dry-run` — full pipeline recommending plan_b for flood-zone synthetic policies.

---

## Related Submissions (Canvas)

| Deliverable | File / location |
|-------------|-----------------|
| Final capstone report | `FINAL_REPORT.md` or PDF export from `FINAL_REPORT.html` |
| Public GitHub repository | [github.com/cottonandcolor/insurance-policy-agent](https://github.com/cottonandcolor/insurance-policy-agent) |
| Presentation slides | `presentation.html` (open in browser, full screen) |
| Speaker script | `PRESENTATION_SPEAKER_SCRIPT.txt` |

---

## Recording Details

| Item | Value |
|------|-------|
| Target length | 8–10 minutes |
| Recording tool | *(e.g., Loom, QuickTime, OBS)* |
| Host platform | *(e.g., YouTube Unlisted)* |
| Actual runtime | *(fill in after recording)* |

---

*Before uploading to Canvas: replace the video URL placeholder above, fill in recording details, and export this document to PDF or Word if required.*
