# Capstone Design Update: Safety Guardrails, Evaluation Metrics, and Human Intervention

**Insurance Policy Comparison & Recommendation Agent**

---

## Agent Purpose and Safety Risks

My capstone agent compares auto, home, and life insurance plans for consumers and brokers. It extracts coverage terms from policy documents, runs loss-scenario analysis, and recommends a best-fit plan with citations. Because recommendations affect financial protection decisions, the primary risks are not generic "AI failure" but domain-specific harm: **hallucinated coverage claims** (stating flood is covered when an exclusion applies), **incorrect payout arithmetic** (understating out-of-pocket exposure), **overconfident ranking** (recommending the cheapest plan while ignoring critical exclusions), **stale or mismatched policy data** (wrong jurisdiction or outdated form), and **proceeding without sufficient evidence** when endorsement schedules or rider attachments are missing.

## Guardrails

Guardrails operate at input, runtime, and output layers:

| Layer | Guardrail | Purpose |
|---|---|---|
| **Input** | Synthetic/public/anonymized corpus only; reject uploads without plan metadata (jurisdiction, effective date) | Prevents privacy leakage and jurisdiction mismatches |
| **Input** | Structured profile schema with required fields (location, risk factors, priority weights) | Blocks incomplete scenario modeling |
| **Runtime** | Hard grounding gate — no coverage claim without retrieved chunk citation | Prevents hallucinated policy language |
| **Runtime** | Arithmetic validator — payout tool must match agent calculation within tolerance | Catches deductible/limit errors |
| **Runtime** | Tool access limits — retrieval-only during reasoning; no premium binding or purchase APIs | Agent advises; it does not transact |
| **Runtime** | LLM call and latency budget (≤25 calls, ≤45s per cycle) | Prevents runaway ToT branch explosion |
| **Runtime** | Policy Critic agent separated from Reasoning agent | Reduces self-confirmation bias |
| **Output** | Recommendation template requires: comparison table, cited tradeoffs, confidence tag, and "not a binding quote" disclaimer | Constrains format and sets user expectations |
| **Output** | Block final output if all ToT branches fail hard gates | Fail closed, not guess |

## Evaluation Metrics

| Metric | Target | Measures |
|---|---|---|
| **Grounding rate** | ≥95% of coverage claims cite retrieved chunks | Factual reliability |
| **Scenario payout accuracy** | ≥90% vs. synthetic ground-truth labels | Correctness |
| **False-coverage rate** | ≤2% (claims covered when policy excludes) | Safety |
| **Escalation rate** | Track % of sessions routed to human | Appropriate deference |
| **Calibration** | High-confidence recommendations correct ≥85% on eval set | Trustworthiness of confidence tags |
| **Pruning precision** | Protected branches with cross-section citations survive ≥80% | ToT safety gate quality |
| **Latency P95** | ≤45 seconds per recommendation cycle | Efficiency |
| **Fallback success** | 100% of hard-gate failures produce clarifying question, not silent guess | Fail-safe behavior |
| **User correction rate** | Track post-hoc corrections to misread terms | Extraction quality over time |

Metrics are evaluated on a held-out set of synthetic policies with labeled flood, liability, and theft scenarios before any live-facing demo.

## Human Intervention Criteria

The system **must defer to a human** (licensed broker or clearly labeled human review step) when any of the following is true:

1. **Evidence gap:** Required endorsement or exclusion section not found in corpus after expanded retrieval
2. **Low confidence:** Top two plans within 0.05 composite score *and* grounding score <0.80 on either branch
3. **Hard-gate failure cluster:** All ToT branches pruned at depth ≤2
4. **High-impact ambiguity:** Peril interpretation differs by >$25K payout across surviving branches (e.g., flood covered vs. excluded)
5. **User correction:** User flags a misread term — agent pauses autonomous re-ranking until human confirms corrected interpretation
6. **Out-of-scope request:** Binding quote, policy purchase, claims filing, or medical/health underwriting questions
7. **Regulatory sensitivity:** Life insurance suitability or employer-benefit coordination beyond document scope

When triggered, the agent outputs a **partial analysis** (what is known, what is missing, cited evidence) and a structured handoff prompt — not a final recommendation.

## Integrated Safety Strategy

Guardrails, evaluation, and human intervention form a **layered control loop**:

```
Input validation → Grounded retrieval → ToT + Critic → Hard gates → Metrics check → Output OR escalate
```

Runtime guardrails prevent unsafe outputs from being generated. Metrics monitor whether guardrails hold under test loads. Human intervention criteria define the boundary where autonomous completion is unsafe despite guardrails — typically when evidence is incomplete or stakes are high. Together, they implement a **fail-closed** design: the default action under uncertainty is clarification or escalation, not recommendation.

## Trade-offs

| Decision | Benefit | Cost |
|---|---|---|
| Fail-closed on missing evidence | Avoids catastrophic coverage advice | Higher escalation rate; more user friction |
| Separate Critic + hard gates | Stronger reliability | Added latency (~25 LLM calls) |
| Confidence-based escalation | Human attention where it matters | Requires calibrated scoring on eval set |
| No purchase/bind tools | Clear advisory boundary | Agent cannot complete end-to-end buying flow |
| Synthetic corpus only (capstone) | Safe development | Metrics may not transfer until validated on public forms |

Increasing oversight improves reliability but reduces autonomy and speed — acceptable for high-stakes insurance decisions where a wrong recommendation exceeds the cost of human review.

## Real-World Deployment Support

This plan supports dependable deployment by making safety **testable and auditable**: every recommendation traceable to retrieved citations, every escalation tied to explicit criteria, every metric measurable on synthetic ground truth before production. In a real-world context, the agent functions as a **decision-support layer** — not a replacement for licensed advice — with bounded tool access, documented failure modes, and mandatory human review when ambiguity or financial impact exceeds defined thresholds.

---

*Word count: ~580*
