# Implementing the Capstone Agent with CrewAI + LangGraph

## Who does what

| Layer | Tool | Responsibility |
|---|---|---|
| **Orchestrator** | **LangGraph** | State machine, phase routing, ToT beam loop, budget caps, conditional edges |
| **Workers** | **CrewAI** | Agent personas, task prompts, role-separated LLM calls |
| **Memory (later)** | **MCP** | Replace in-memory `retrieval_cache` / `session_profile` with shared server |
| **Retrieval (later)** | **LangChain** | Vector store, hybrid search, reranking tools |

**Rule of thumb:** LangGraph decides *when* and *which path*; CrewAI decides *how each role thinks*.

## Architecture mapping

```
LangGraph nodes                    CrewAI crew invoked inside node
─────────────────────────────────────────────────────────────────
intake          ───────────────►  Profile Intake Agent
ingest          ───────────────►  Document & Retrieval Agent (per plan)
tot_expand      ───────────────►  Scenario Reasoning Agent
evaluate        ───────────────►  Policy Critic Agent
synthesize      ───────────────►  Recommendation Synthesizer

LangGraph-only nodes (no LLM):
  tot_init, ground, prune_beam, advance_depth, should_continue_tot
```

## Project layout

```
capstone/
├── main.py                 # entry point
├── requirements.txt
├── data/synthetic/         # public/synthetic policies only
├── src/
│   ├── state.py            # AgentState TypedDict
│   ├── graph/workflow.py   # LangGraph StateGraph
│   ├── crews/
│   │   ├── agents.py       # CrewAI Agent definitions
│   │   └── tasks.py        # CrewAI Task definitions
│   └── tools/retrieval.py  # stub → Chroma later
```

## Setup

```bash
cd /Users/preetidave/capstone
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
python main.py
```

## ToT beam loop (LangGraph)

Your design's Phases 4–5 map to this cycle:

```
tot_init → tot_expand → ground → evaluate → prune_beam → advance_depth
                ↑__________________________________________|
                     (if depth <= max_depth and branches survive)
                └──────────────────→ synthesize → END
```

- **tot_expand:** CrewAI Scenario Reasoning Agent proposes 2–3 branches
- **ground:** retrieval tool attaches `evidence_ids` (hard gate input)
- **evaluate:** CrewAI Policy Critic returns scores + prune flag
- **prune_beam:** keep top-3 by `composite_score`
- **should_continue_tot:** stop at depth 4, empty beam, or LLM budget

## Follow-up queries

For "What if I add my teenage driver?":

1. Update `session_profile` in state
2. Re-invoke graph from `tot_init` with `depth=2` (skip intake/ingest if plans unchanged)

```python
result = app.invoke({
    **prior_state,
    "follow_up": "add teenage driver",
    "depth": 2,
})
```

## Next implementation steps

1. **Retrieval:** Replace `retrieve_evidence()` with LangChain + Chroma over chunked PDFs
2. **Structured output:** Use Pydantic models + `crew.kickoff()` JSON parsing instead of raw strings
3. **Hard gates:** Add LangChain validators before critic (citation required, arithmetic tool)
4. **MCP:** Move `AgentState` fields to MCP resources (`branch_store`, `session_profile`)
5. **Tests:** Unit-test prune logic and routing without LLM calls

## Common pitfalls

- **Don't run the full Crew inside one mega-agent** — defeats role separation
- **Don't put beam search inside CrewAI** — LangGraph conditional edges are the right control plane
- **Don't skip grounding between expand and evaluate** — matches your retrieval design
- **Use synthetic policies only** until corpus and privacy review are complete
