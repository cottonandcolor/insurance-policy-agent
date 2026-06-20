# Option A: Research Assistant — Insurance Policy Comparison & Recommendation Agent

## Problem

A consumer shopping for insurance (auto, home, life) faces dozens of plans across multiple carriers. Each plan has different coverage limits, deductibles, exclusions, riders, and premium structures. Comparison sites show price but not the critical fine print — "Does this plan cover flood damage? What's the actual out-of-pocket if I total my car?"

## Intended User

Individual consumer or insurance broker comparing plans for a client.

## Agent Goal

Given a user's profile (age, location, assets, risk tolerance) and a set of insurance plans, analyze coverage gaps, compare total cost of ownership (not just premium), identify hidden exclusions, and recommend the best-fit plan with justification.

## Why a Single Prompt Fails

- Plan documents are 30–80 page PDFs with dense legal language — won't fit in one context window
- Must compare across plans (Plan A covers X but not Y, Plan B covers Y but has a $5K deductible) — requires structured extraction then cross-comparison
- Needs to calculate scenarios: "If your house floods, Plan A pays $150K after $2K deductible, Plan B pays $100K after $5K deductible, Plan C excludes flood entirely"
- Must factor in the user's specific situation (location in a flood zone, existing coverage from employer, credit score affecting premiums)
- Requires iterative refinement — user says "I don't care about roadside assistance, but I need rental car coverage" and the recommendation changes
- A single prompt hallucinates coverage details — the agent must ground every claim in the actual document

## Environment

- Insurance plan PDFs or structured data (from carrier APIs or scraped comparison sites)
- User profile questionnaire
- Location-based risk data (flood zones, crime rates, weather patterns)
- Premium calculator APIs
- A document store for extracted plan details

## Actions

1. Collect user profile (age, location, assets, existing coverage, priorities)
2. Ingest plan documents — chunk and extract key terms: coverage limits, deductibles, exclusions, waiting periods, riders
3. Normalize extracted data into a comparable schema
4. Run scenario analysis: for each major risk event (accident, theft, natural disaster, liability claim), calculate what each plan actually pays
5. Score plans against user's priorities (lowest total cost, broadest coverage, best claims reputation)
6. Generate comparison table and recommendation with citations to specific plan sections
7. User asks follow-up ("What if I add my teenage driver?") — agent recalculates

## Feedback

User marks which factors matter most, corrects any misread plan terms, asks "what if" scenarios. Agent refines recommendation and learns the user's risk tolerance.

---

# Agent Concept: Insurance Policy Comparison & Recommendation Agent

## Problem & Intended User

Choosing the right insurance policy — whether auto, home, or life — is one of the most consequential financial decisions a household makes, yet it remains one of the most opaque. Consumers face dozens of plans across carriers, each with different coverage limits, deductibles, exclusions, waiting periods, and premium structures buried in 30–80 page policy documents written in dense legal language. Existing comparison websites rank plans primarily by premium price, ignoring the critical question: what actually happens when I file a claim?

The intended user is either an individual consumer comparing plans or an insurance broker evaluating options for a client. The agent's goal is to analyze multiple insurance plans against a user's specific profile and risk exposure, compare total cost of ownership across realistic loss scenarios, identify hidden coverage gaps, and produce a justified recommendation grounded in the actual policy language — not generic summaries.

## Why a Standalone Language Model is Insufficient

A single prompt-response approach fails this problem for several structural reasons. First, policy documents exceed the context window of most language models, and even when they fit, LLMs routinely hallucinate coverage details — confidently stating a plan covers flood damage when the fine print excludes it. The agent must ground every claim in a specific document section.

Second, the task requires multi-step reasoning across documents. Comparing Plan A against Plan B is not a single extraction — it requires normalizing terminology (one carrier says "comprehensive," another says "all-perils"), aligning coverage categories, and then running scenario-based calculations: "If your house floods, Plan A pays $150,000 after a $2,000 deductible, Plan B pays $100,000 after a $5,000 deductible, and Plan C excludes flood entirely." This cross-document comparison with arithmetic cannot be reliably handled in a single pass.

Third, the problem is inherently interactive. A user's priorities shift during the conversation — "I don't care about roadside assistance, but rental car coverage is essential" — and the recommendation must adapt. This requires maintaining state across turns, re-scoring plans against updated criteria, and explaining what changed and why.

## Environment

The agent interacts with several external systems and data sources. Insurance plan documents (PDFs or structured data from carrier APIs) are the primary knowledge source, requiring parsing, chunking, and structured extraction. A user profile questionnaire captures age, location, assets, existing coverage, and risk priorities. Location-based risk databases (flood zone maps, crime statistics, wildfire indices) provide context for scenario modeling. Premium calculation APIs or rate tables allow cost comparison. Finally, the agent maintains a structured store of extracted plan details — coverage limits, deductibles, exclusions, riders — normalized into a comparable schema.

## Actions

The agent's workflow proceeds through distinct phases. It begins by collecting the user's profile and priorities through a structured interview. It then ingests each plan document, chunking large PDFs and extracting key terms: coverage types, limits, deductibles, exclusions, waiting periods, and conditions. These extracted fields are normalized into a common schema so plans can be compared directly.

Next, the agent runs scenario analysis. For each major risk event relevant to the user's profile — car accident, home burglary, natural disaster, liability lawsuit — it calculates what each plan would actually pay after deductibles and exclusions. It then scores plans against the user's stated priorities (lowest total cost, broadest coverage, fewest exclusions) and generates a comparison table with a top recommendation, citing specific policy sections as evidence.

The user can then ask follow-up questions — "What if I add my teenage driver?" or "Show me only plans that cover flooding" — and the agent recalculates and re-ranks without starting over.

## Feedback & Iterative Refinement

Feedback operates at two levels. Within a session, the user steers the agent by correcting misread terms ("actually my current policy does cover rental cars"), adjusting priorities, and asking scenario questions. The agent updates its internal comparison state and re-ranks accordingly.

Across sessions, the agent improves its extraction accuracy. If a user identifies that the agent misinterpreted an exclusion clause, that correction refines how similar clauses are parsed in future documents. Over time, the agent builds a more reliable mapping between legal language patterns and their practical coverage implications — moving from generic document understanding toward domain-specific insurance literacy.

---

# Capstone Design Update: Retrieval Decision for an Insurance Policy Recommendation Agent

*May 30*

My capstone project focuses on the development of an Insurance Policy Comparison and Recommendation Agent designed to assist users in navigating the complexities of auto, home, and life insurance. This agent moves beyond simple summarization to provide active decision support, evaluating coverage limits, exclusions, deductibles, and riders to calculate realistic out-of-pocket costs across various loss scenarios. While earlier modules established the reasoning loop and memory architecture, this update defines the retrieval strategy — determining its necessity, integration methods, and observable impact on system reliability.

## 1) Is retrieval required?

Yes, a retrieval mechanism is foundational to this use case.

A standalone language model approach is insufficient for the high-stakes nature of insurance. Policy documents are notoriously long, legally dense, and specific; critical information is often distributed across disjointed sections and endorsements. Without grounding, an LLM is prone to producing plausible yet unverified claims that fail to capture the exact nuances of a plan. Retrieval is architecturally mandated for three primary reasons:

- **Grounding:** Every plan-specific assertion must be anchored in actual policy evidence to prevent hallucinations.
- **Cross-document comparison:** The agent requires a structured way to align disparate terminology and compare multiple policies simultaneously.
- **Traceability:** Verifiable citations are essential for establishing user trust in financial recommendations.

Given the consequences of inaccurate advice, retrieval is not an enhancement but a core reliability requirement.

## 2) How retrieval is integrated

The architecture incorporates a semantic retrieval mechanism leveraging an external document store and a vector index.

To maintain data integrity, the corpus utilizes public, synthetic, or anonymized policy forms that mirror real-world structures. The retrieval workflow consists of several distinct phases: ingesting documents to extract structured text; attaching critical metadata such as policy ID and jurisdiction; chunking content into semantically coherent units; and indexing these via vector embeddings. At query time, the agent retrieves the top-k chunks based on the user's profile and intent, grounding its reasoning in this retrieved evidence and enforcing strict citations for all claims.

## 3) How retrieval changes output behavior

Retrieval significantly elevates the quality and accuracy of the agent's recommendations. For instance, when a user asks, "Does Plan C cover flood damage, and what is my likely out-of-pocket risk?" the behavior shifts dramatically:

- **Without retrieval:** The model may offer generic observations — such as noting that flood insurance often requires a separate policy — without verifying the specific terms of Plan C.
- **With retrieval:** The agent identifies specific exclusion clauses and rider options within the document. It can then provide a grounded assessment: "Plan C excludes flood damage unless the optional Water Backup rider is attached; without it, your estimated exposure in this flood zone remains high."

This illustrates that retrieval does more than add context; it fundamentally changes the decision outcome by ensuring reliability.

## 4) Key retrieval design choices

Several strategic choices were made to optimize precision and explainability:

- Section-aware chunking (approx. 300–500 tokens with 20% overlap) to preserve legal context
- Metadata-aware filtering to restrict searches by jurisdiction
- A top-k reranking strategy that selects the most relevant fragments for final reasoning
- Session-aware retrieval to guide reranking based on user-stated priorities, such as a preference for "broadest protection" over "lowest premium"

## 5) Retrieval failure mode and mitigation

A primary risk is "semantic near-miss" retrieval, where the system identifies text that sounds relevant but is legally distinct (e.g., confusing general "water damage" with "flood"). This is mitigated through a layered approach:

- Hybrid retrieval that combines vector similarity with keyword checks for high-risk legal terms
- Strict metadata constraints
- Reasoning checks that require the agent to explicitly extract coverage conditions before making a recommendation

If evidence is conflicting, the agent is programmed to ask clarifying questions rather than generating a guess.

---

# Capstone Design Update: Tree-of-Thought Reasoning Architecture

*June 2026*

This update integrates Tree-of-Thought (ToT) reasoning into the Insurance Policy Comparison and Recommendation Agent. Earlier modules established retrieval for grounding and a linear reasoning loop for extraction and normalization. ToT replaces premature single-path reasoning in the highest-uncertainty phase — scenario analysis and plan recommendation — with structured exploration, explicit evaluation, and pruning. The design maps conceptual ToT roles to CrewAI, LangChain, and MCP for implementation in later modules.

## 1) Where ToT Reasoning Improves the Agent

ToT is applied to **Phase 4–5 of the workflow: scenario analysis and plan scoring/recommendation** (after user profile collection, document ingestion, and schema normalization).

A linear chain-of-thought fails here for three structural reasons:

| Failure mode | Why linear CoT breaks | Why ToT is a better fit |
|---|---|---|
| **Premature commitment** | A single pass often locks onto the first plausible reading of an ambiguous clause (e.g., treating "water damage" as flood coverage when the policy excludes surface water). | ToT generates multiple interpretation branches and evaluates each against retrieved evidence before committing. |
| **High branching** | Comparing *N* plans across *M* risk scenarios yields combinatorial paths (plan × scenario × clause interpretation × rider attachment). Linear reasoning collapses this into one narrative and drops alternatives. | ToT explores parallel hypotheses (e.g., "Plan B covers flood" vs. "Plan B excludes flood unless Rider 12 is attached") and retains the best-scoring paths. |
| **Constraint complexity** | Final ranking must reconcile grounding citations, arithmetic scenario payouts, user priority weights, and jurisdictional metadata simultaneously. Linear chains optimize locally (e.g., lowest premium) and miss globally better options. | ToT evaluates intermediate states against a multi-criteria rubric and prunes branches that violate hard constraints (missing citations, arithmetic errors, excluded perils in a flood zone). |

ToT does **not** replace retrieval or extraction. It sits downstream of grounded document retrieval, where interpretive ambiguity and multi-plan tradeoffs are highest.

## 2) ToT Structure

### What a "thought" represents

A **thought** is a grounded intermediate reasoning step — not free-form prose. Each thought is a structured object containing:

- A **claim** (e.g., "Plan C excludes flood unless Water Backup endorsement is present")
- **Evidence** (retrieved chunk IDs and policy section references)
- A **partial state update** (coverage classification, deductible applied, estimated payout for one scenario)
- A **confidence tag** (pending evaluation)

Example thought at depth 2: *"Under a $150K flood loss in Zone AE, Plan A pays $148K after $2K deductible; citation: Plan A, Section IV, Perils Insured."*

### Nodes, branches, and depth

| Concept | Definition in this system |
|---|---|
| **Node** | A partial comparison state: `{user_profile, active_plans[], scenario_id, accumulated_thoughts[], running_scores{}, open_constraints[]}`. Each node is one point in the reasoning tree. |
| **Branch** | An alternative reasoning path from a parent node — e.g., a different clause interpretation, rider assumption, or plan-ranking hypothesis. |
| **Depth** | The number of reasoning layers from the root query. Depth is tied to workflow stages, not token count. |

**Depth layers:**

| Depth | Stage | Example branch content |
|---|---|---|
| 0 (root) | Query framing | "Recommend best home plan for flood-zone homeowner prioritizing broad coverage" |
| 1 | Peril interpretation | Branch A: flood excluded; Branch B: flood covered via endorsement; Branch C: flood covered under all-perils |
| 2 | Scenario calculation | For each interpretation, compute payout across 3–5 user-relevant loss scenarios |
| 3 | Priority-weighted scoring | Apply user weights (coverage breadth 0.4, cost 0.3, exclusions 0.3) to produce plan scores |
| 4 (leaf) | Recommendation synthesis | Final ranked plan list with citations and tradeoff summary |

### Branching factor and depth limit

- **Branching factor:** 2–3 child branches per node at depth 1 (interpretation variants); 2 at depth 2 (scenario emphasis variants, e.g., catastrophic vs. moderate loss); 1 at depth 3–4 (deterministic scoring from validated inputs). Effective average branching factor: **~2.5**.
- **Depth limit:** **4** (root → interpretation → scenario → scoring → leaf). No expansion beyond depth 4.

### Termination and final output selection

The system terminates when **any** of the following conditions is met:

1. **Beam convergence:** One branch dominates the active beam (score ≥ next-best by a margin of ≥ 0.15 on the composite rubric).
2. **Depth limit reached:** All surviving branches at depth 4 are leaf nodes ready for synthesis.
3. **Hard failure:** All branches at a depth fail grounding or arithmetic validation (triggers clarifying question to user instead of a guess).

**Final output:** The highest-scoring leaf node after critic evaluation and beam selection. The Decision Maker agent synthesizes this into a comparison table and recommendation with citations. If the top two leaves are within 0.05 composite score, both are presented with an explicit tie-break rationale (see Section 4).

## 3) Evaluation and Pruning Mechanism

### Evaluation criteria (scoring rubric)

Each candidate branch receives a composite score (0.0–1.0) across five dimensions:

| Criterion | Weight | Description |
|---|---|---|
| **Grounding** | 0.30 | Every claim cites a retrieved policy chunk; no uncited assertions. |
| **Consistency** | 0.20 | Interpretations do not contradict other evidence within the same plan document. |
| **Scenario completeness** | 0.20 | All user-relevant scenarios (from profile) are computed, not skipped. |
| **Arithmetic validity** | 0.15 | Payout calculations pass tool-based verification (deductible, limits, co-insurance). |
| **Priority alignment** | 0.15 | Weighted score reflects user-stated priorities from session memory. |

**Hard gates (instant prune regardless of score):**

- Missing citation on any coverage claim
- Arithmetic mismatch vs. calculator tool output (> $500 tolerance)
- Jurisdiction metadata mismatch (plan filtered for wrong state)

### Who performs evaluation

Evaluation is **hybrid**:

| Evaluator | Role | Tool |
|---|---|---|
| **Critic Agent** | Scores grounding, consistency, and priority alignment; flags ambiguous clauses | CrewAI — `Policy Critic` agent |
| **Heuristic checks** | Enforces hard gates (citation presence, schema validity) | LangChain — validation functions in LCEL pipeline |
| **Tool calls** | Verifies payout arithmetic and peril classification | LangChain tools + MCP-exposed premium/scenario calculator |

The Critic Agent produces a structured score vector; heuristics and tools act as **binary pass/fail gates** before the Critic's soft scores are applied.

### Pruning thresholds and failure conditions

- **Prune:** Composite score < **0.55** at depths 1–2; < **0.65** at depths 3–4 (stricter near output).
- **Prune:** Any hard gate failure.
- **Prune:** Branch duplicates an existing node state (same interpretation + same scenario outcomes) — deduplication via MCP state hash.
- **Failure condition:** Fewer than 1 branch survives after depth 2 → halt ToT, return to user with specific evidence gap ("Cannot determine flood coverage for Plan C; endorsement schedule not found in corpus").

### Tie resolution

1. **Primary:** Rerank by grounding score (highest wins).
2. **Secondary:** Critic Agent vote — if grounding is within 0.03, the Critic selects the branch with fewer unresolved ambiguities.
3. **Tertiary:** Present both top branches to the user as a tied recommendation with explicit tradeoff language; do not silently pick one.

## 4) Search Strategy Selection

**Primary strategy: Beam search (beam width = 3).**

| Strategy | Fit for this use case |
|---|---|
| BFS | Explores too broadly across plan × scenario combinations; cost scales poorly with 4+ plans. |
| DFS | Risks committing to a deep but wrong interpretation path (e.g., incorrect exclusion reading) before alternatives are considered. |
| **Beam search** | **Selected.** Maintains the top-3 branches at each depth — enough diversity to catch misread clauses without full combinatorial explosion. Aligns with financial decision-making where a small set of strong hypotheses should be compared, not every possible path. |
| Monte Carlo sampling | Poor fit for deterministic, citation-backed reasoning; introduces unnecessary stochasticity in payout calculations. |

**Compute, latency, and cost constraints:**

| Constraint | Limit | Enforcement |
|---|---|---|
| Max LLM calls per recommendation | **~25** (3 branches × 4 depths + critic evaluations) | LangChain orchestrator budget counter |
| Max latency | **45 seconds** per recommendation cycle | Timeout aborts lowest-scoring beam branch first |
| Retrieval calls per branch | **≤ 5** | Cached at node level via MCP; sibling branches reuse parent retrievals |
| Token budget per branch | **~8K** context (retrieved chunks + thought chain) | Truncate thought history to active path only |

If the 45-second budget is exceeded mid-search, the controller freezes expansion and selects the best-scoring node at the current depth (graceful degradation).

## 5) ToT Role-to-Tool Mapping

| Conceptual role | Responsibility | Primary tool | Secondary tool |
|---|---|---|---|
| **Thought Generator** | Proposes 2–3 alternative interpretations, scenario calculations, or ranking hypotheses at each tree depth | **CrewAI** — `Coverage Analyst` agent with task templates per depth layer | **LangChain** — LCEL chain invokes generator with retrieved context injected |
| **Critic / Evaluator** | Scores branches against rubric; enforces grounding and consistency; recommends prune/keep | **CrewAI** — `Policy Critic` agent (separate role from generator to avoid self-confirmation bias) | **LangChain** — hard-gate validators + arithmetic tool calls |
| **Decision Maker / Controller** | Runs beam search loop, applies pruning thresholds, selects final leaf, synthesizes user-facing output | **LangChain** — LCEL orchestration graph (branch loop, conditional edges, budget enforcement) | **CrewAI** — `Recommendation Synthesizer` agent for final narrative generation |
| **Memory / State Manager** | Stores tree structure, node states, branch scores, cached retrievals, and session priorities; enables branch deduplication and cross-turn re-scoring | **MCP** — shared state server exposing `branch_store`, `session_profile`, and `retrieval_cache` resources | **LangChain** — checkpointing for orchestrator resume after user follow-up |

### CrewAI: agent definition and task routing

Three CrewAI agents with explicit role separation:

1. **Coverage Analyst** (Thought Generator) — generates candidate thoughts; never evaluates its own output.
2. **Policy Critic** (Evaluator) — receives candidate thoughts + evidence; returns score vector and prune recommendation.
3. **Recommendation Synthesizer** (Decision Maker delegate) — converts winning leaf node into comparison table and justified recommendation.

CrewAI task routing assigns depth-specific prompts (interpretation tasks at depth 1, calculation tasks at depth 2, etc.) and passes MCP state handles between tasks.

### LangChain: control flow and orchestration

LangChain owns the **ToT loop**:

```
retrieve → normalize → [ToT loop: generate → evaluate → prune → expand] → synthesize
```

Implemented as an LCEL graph with:

- Conditional edges on critic scores (expand vs. prune vs. terminate)
- Tool integration for payout calculator and citation validator
- Budget counters for LLM calls and latency

### MCP: shared state and branch tracking

MCP provides the **branch-aware memory layer**:

- `branch_store`: tree of nodes with parent/child links, scores, and thought objects
- `session_profile`: user priorities and profile (updated on follow-up questions)
- `retrieval_cache`: keyed by `(plan_id, peril, jurisdiction)` to avoid redundant retrieval across sibling branches

When the user asks a follow-up ("What if I add my teenage driver?"), the controller updates `session_profile` via MCP and re-enters the ToT loop from depth 2 (scenario recalculation) rather than restarting from scratch.

## 6) ToT Insertion Point in Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: User profile collection          [CrewAI interview]   │
├─────────────────────────────────────────────────────────────────┤
│  Phase 2: Document ingest + chunk          [LangChain + store]  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 3: Normalize to comparable schema   [LangChain extract]  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 4–5: ★ ToT REASONING INSERTION POINT ★                   │
│    ┌─────────────────────────────────────────────────────────┐  │
│    │  LangChain beam-search controller                       │  │
│    │    → CrewAI Coverage Analyst (generate branches)        │  │
│    │    → Retrieval (ground branches)     [existing module]  │  │
│    │    → CrewAI Policy Critic (evaluate + prune)            │  │
│    │    → MCP branch_store (persist tree state)              │  │
│    │    → CrewAI Synthesizer (final output from winning leaf)│  │
│    └─────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Phase 6: User follow-up / re-score        [MCP session update] │
└─────────────────────────────────────────────────────────────────┘
```

ToT activates **only after** plans are normalized into the comparable schema and retrieval is available. Extraction and normalization remain linear pipelines; ToT governs interpretive and decision reasoning where ambiguity and tradeoffs peak.

## 7) Risk and Mitigation

### Risk: Weak evaluation signals leading to pruning the best branch

The Critic Agent may undervalue a legally correct but unusually worded branch — for example, a valid coverage path buried in endorsement cross-references that scores low on consistency because evidence spans multiple document sections. Standard semantic similarity and single-pass consistency checks can prune the branch that would produce the most accurate recommendation.

### Mitigation: Grounding-first gate with cross-section consistency check

Before any branch is pruned for low consistency score:

1. **Grounding gate:** If grounding score ≥ 0.85 and citations span ≥ 2 retrieved chunks from the same plan, the branch is **protected from consistency-based pruning** and flagged for expanded retrieval (one additional targeted query for cross-referenced endorsement sections).
2. **Cross-section linker:** A LangChain tool resolves internal policy references ("see Endorsement HO-042") by fetching linked chunks before re-evaluation.
3. **Re-score:** The Critic re-evaluates the branch with expanded evidence. Only if consistency remains < 0.50 after expansion is the branch pruned.

This prevents premature elimination of correct but structurally complex reasoning paths while still pruning genuinely unsupported branches.

---

## Testability

This architecture is designed to be testable in later modules:

| Test | Method |
|---|---|
| ToT vs. linear CoT accuracy | Run identical plan sets through both pipelines; compare grounding citation rate and scenario payout accuracy against synthetic ground-truth labels |
| Pruning precision | Inject known ambiguous clauses; verify protected branches survive grounding-first gate |
| Cost bounds | Assert LLM call count ≤ 25 and latency ≤ 45s on benchmark queries |
| Follow-up re-entry | Update session profile via MCP; confirm ToT resumes at depth 2 without full tree rebuild |
| Tie handling | Construct plans with composite scores within 0.05; verify dual recommendation output |
