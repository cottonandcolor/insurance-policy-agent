# Capstone Design Update: Multi-Agent Architecture

**Insurance Policy Comparison & Recommendation Agent**

---

## Problem and Why Multi-Agent

My capstone agent helps consumers and brokers compare auto, home, and life insurance plans by analyzing coverage limits, exclusions, deductibles, and realistic out-of-pocket costs across loss scenarios — grounded in actual policy language, not premium rankings alone.

A single agent cannot reliably perform this work. Policy comparison spans distinct competencies: structured user interviewing, long-document extraction, semantic retrieval across legal text, multi-path interpretive reasoning, arithmetic scenario modeling, and adversarial quality review. Combining these in one agent increases hallucination risk, blurs accountability for errors, and makes it impossible to enforce grounding gates before recommendations are issued. A multi-agent design separates concerns so each agent has a narrow, testable mandate — similar to how a research workflow benefits from distinct planner, researcher, and writer roles.

## Agent Count and Rationale

The system includes **six agents**, determined by task decomposition rather than arbitrary expansion:

| Agent | Core responsibility |
|---|---|
| **Orchestrator** | Workflow routing, phase transitions, beam-search budget enforcement |
| **Profile Intake Agent** | Collects user profile, assets, location risks, and priority weights |
| **Document & Retrieval Agent** | Ingests policy PDFs, normalizes schema, retrieves grounded evidence |
| **Scenario Reasoning Agent** | Generates ToT branches, interprets clauses, computes loss scenarios |
| **Policy Critic Agent** | Scores branches, enforces citation/arithmetic gates, prunes weak paths |
| **Recommendation Synthesizer** | Produces comparison table, ranked recommendation, and citations |

Six agents map to six workflow phases with minimal overlap. Fewer agents would merge extraction with evaluation (self-confirmation bias). More agents — e.g., separate chunking, embedding, and reranking agents — would add coordination overhead without proportional accuracy gains at this design stage.

## Coordination Strategy

The architecture uses a **hybrid coordination model**:

- **Sequential (Phases 1–3):** Profile Intake → Document & Retrieval → normalized plan store. This assembly-line flow ensures downstream agents operate on validated, structured inputs.
- **Iterative graph (Phases 4–5):** The Orchestrator runs a beam-search loop: Scenario Reasoning generates branches → Document & Retrieval grounds them → Policy Critic evaluates → Orchestrator prunes or expands. This graph resembles a project network with feedback edges, not a single pass.
- **Sequential (Phase 6):** Recommendation Synthesizer converts the winning branch into user-facing output; Orchestrator handles follow-up re-entry at depth 2 without rebuilding the full tree.

## Communication Strategy

Communication is **mixed by phase**:

- **One-way (Orchestrator → workers):** Task assignments, depth-layer prompts, and budget limits flow top-down for efficiency.
- **Two-way (Reasoning ↔ Critic):** The Scenario Reasoning Agent submits candidate thoughts; the Policy Critic returns score vectors and prune/keep decisions. This validation loop prevents unchecked interpretive drift.
- **Shared state (all agents via MCP):** `session_profile`, `branch_store`, and `retrieval_cache` enable agents to read consistent context without passing full document history on every turn.

LangChain orchestrates control flow; CrewAI defines agent roles and task routing; MCP maintains branch-aware memory across the ToT loop.

## Trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Separate Critic Agent | Reduces self-confirmation bias; improves grounding enforcement | +1 agent, added latency per branch |
| Hybrid sequential + graph coordination | Reliable preprocessing; flexible reasoning where ambiguity peaks | Higher implementation complexity vs. pure pipeline |
| Two-way Reasoning–Critic loop | Catches misread exclusions before recommendation | ~25 LLM calls and up to 45s per cycle |
| MCP shared state | Consistent branch tracking; efficient follow-up re-scoring | State synchronization risk if schemas drift |

Feedback loops improve reliability at the cost of latency — acceptable for high-stakes financial recommendations where incorrect coverage advice outweighs wait time.

## Scalability

The architecture scales horizontally by design:

- **More plans:** Document & Retrieval Agent parallelizes per-plan ingestion; retrieval cache deduplicates sibling branch queries.
- **More scenarios:** Orchestrator caps beam width (3) and depth (4), preventing combinatorial explosion as plan count grows.
- **Follow-up queries:** MCP session updates trigger partial ToT re-entry (depth 2), not full pipeline restarts.
- **New insurance types:** Normalized schema and role separation allow adding life or auto modules without redesigning the Critic or Synthesizer.

Each agent is independently testable — extraction accuracy, retrieval precision, pruning recall, and synthesis citation rate — making the system evolvable across later implementation modules without architectural rework.

---

*Word count: ~560*
