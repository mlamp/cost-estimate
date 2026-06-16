# cost-estimate — Improvement Backlog (P0 / P1 / P2 all IMPLEMENTED)

This directory captures the findings from a multi-angle adversarial review of the
`cost-estimate` skill (methodology validity, fairness/gameability, implementation
bugs, the cost/valuation layer, LOC bias, internal consistency, and a scan of newer
research). Findings were clustered by priority — **all three clusters have since been
implemented** in `skill/SKILL.md` (each `*-implementation-plan.md` carries the per-cluster
amendments and outcome record):

- **[P0 — Correctness & Honesty](P0-correctness-and-honesty.md)** — broken/contradictory/
  overstated items. **✅ Implemented** (all 24 findings + 2 bonus git bugs). Headline numbers
  are now reproducible from the skill's own code.
- **[P1 — Fairness & Economics](P1-fairness-and-economics.md)** — the design changes that make
  the estimate *fair*: ungameable, domain-neutral, language-neutral, not biased toward verbose
  prose/web apps. **✅ Implemented** (all 20 findings).
- **[P2 — Research-backed Redesign](P2-research-redesign.md)** — larger reworks replacing ad-hoc
  heuristics with established estimation methods (FP/COSMIC/UCP cross-checks, Monte-Carlo band,
  reproduction-vs-value labeling, METR/DORA evidence, git-effort anchor, optional Bayesian/RCF
  calibration). **✅ Implemented** (all 14 items; see `P2-implementation-plan.md`).

## How these findings were produced

7 adversarial lenses + 1 web-research scan generated 65 findings; the 20
highest-severity ones were then **adversarially re-verified against the source**
(an independent agent tried to *refute* each). Where verification lowered a claim,
that is noted inline as `verified: partially-confirmed → severity lowered`. Where it
held, it is noted `verified: confirmed`. The strongest single finding (keyword-padding
gameability) was reproduced end-to-end.

## Severity legend

| Severity | Meaning |
|----------|---------|
| 🔴 critical | Breaks output correctness, reproducibility, or makes the headline forgeable/meaningless |
| 🟠 high | Materially wrong or misleading number, or a real fairness/trust defect |
| 🟡 medium | Real defect with bounded impact or lower frequency |
| ⚪ low | Cosmetic / polish |

## The three structural problems everything traced back to (all since ADDRESSED)

At review time the tool had three structural problems; each is now fixed in the shipped skill:

1. **COCOMO was run backwards.** It is an *a-priori* model (effort from a size predicted
   *before* building); measuring surviving LOC and back-computing "cost to build" rewards
   verbose code, ignores rework, and answers neither the historical cost nor a defensible
   forward estimate. → **Fixed:** reframed throughout as **reproduction cost** (the cost
   approach), with the three valuation lenses stated up front (P0-17/P0-23/P2-14).
2. **The headline was driven by the least-grounded component** — the "Intellectual Effort
   Artifacts" prose multiplier. At review the self-report's `$73K` was ~98% one markdown file.
   → **Fixed:** IE is reported on its **own** line and **never** summed into the dollar
   headline, which is now code-only (the self sample's headline is ~$500, with IE shown
   separately) (P1-6/P1-7).
3. **It was a web-app appraiser posing as a general one** — LOC anchor + 8 web-idiom factors
   under-valued dense/non-web code. → **Fixed:** each factor takes `MAX(web-idiom,
   domain-general)` plus a depth/intensity term, and the structural FP/COSMIC cross-checks are
   archetype-gated so non-web code is not zero-cost (P1-9; P2-1/2).

> Note: line numbers in the evidence below predate the P0/P1/P2 landing (review-time snapshot,
> ~commit `73e95e0`) and are indicative only — `skill/SKILL.md` has since grown substantially.
