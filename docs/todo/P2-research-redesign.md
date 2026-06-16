# P2 — Research-backed Redesign

P0 makes the tool honest; P1 makes it fair. P2 replaces the load-bearing ad-hoc
heuristics with established (and newer) estimation methods. These are larger reworks,
listed by adoption cost. Several P0 honesty fixes are the cheap front-half of a P2
method (e.g. stating PRED/MMRE bounds now; doing real Monte Carlo later).

The honest framing to adopt throughout: the tool computes **reproduction / replacement
cost** (what it would cost to rebuild the surviving artifact with a human team) — which
is **not** market value, **not** what it actually cost to produce, and — in an era where
~40%+ of code is AI-assisted — built on an increasingly **fictional "from-scratch human"
baseline** that should be stated, not hidden behind a 110× headline.

---

## Cluster 1 — Escape LOC: size from structure, not lines

### P2-1 Count real IFPUG Function Points from transactions/data functions (not `LOC ÷ ratio`)
*adoption: major-rework*

- **Problem it fixes:** Current "Function Points" are `LOC / ratio` (`:1035`), so they carry
  zero information beyond LOC and are circular — they cannot corroborate a LOC-based estimate
  because they *are* it. FPA exists to be language-independent: count External Inputs/Outputs/
  Inquiries (transactions) and Internal/External Files (data) from the design, then derive
  effort *from* FP.
- **How here:** Approximate EI/EO/EQ from detected route/endpoint/handler counts and ILF/EIF
  from detected entities/migrations (data the Data-Layer factor already greps). Feed published
  FP→effort productivity tables instead of LOC→effort. A 500-line Python service and a
  1,500-line Java service implementing the same endpoints then get similar FP — killing the
  verbosity reward (P1-6, P1-9).
- **Source:** IFPUG Counting Practices Manual v4.3.1; ISO/IEC 20926:2009; Capers Jones,
  *Applied Software Measurement* (already cited).

### P2-2 COSMIC Function Points (ISO/IEC 19761) from data movements
*adoption: major-rework*

- **What:** Sizes software by counting data movements (Entry/Exit/Read/Write) across
  functional-process boundaries — no arbitrary complexity-weight tables, scales to apps,
  real-time, and infra. Active research automates CFP from source (regex/AST extractors);
  ScopeMaster reports automated counts typically within ~15% of manual.
- **Why here:** Implementation-independent and far harder to game by padding lines; much of
  what it counts (HTTP handlers, DB read/writes, queue ops) the tool already greps in Phase 2.
- **Source:** ISO/IEC 19761:2011; Soubra/Abran et al., "Automated COSMIC Function Points
  Measurement Using Regular Expressions," IWSM-Mensura 2022; ScopeMaster docs (2024).

### P2-3 Map the non-functional factors to IFPUG SNAP (now ISO/IEC/IEEE 32430:2025)
*adoption: moderate*

- **What:** SNAP sizes *non-functional* requirements (data ops, interface design, technical
  environment, architecture) in SNAP Points, complementary to FP — and is now an international
  standard (ISO/IEC/IEEE 32430:2025).
- **Why here:** The tool's 8 factors (auth, infra/DevOps, error handling, security) are almost
  all non-functional — exactly what SNAP quantifies — yet are currently squeezed into COCOMO
  EMs ad hoc. Mapping them to SNAP sub-categories gives a principled standardized size and lets
  the tool cite a *current 2025* standard rather than name-dropping SNAP v2.4 for an unrelated
  multiplier (see P0-14).
- **Source:** IFPUG SNAP APM v2.4; ISO/IEC/IEEE 32430:2025.

### P2-4 Automated / AI-assisted FP counting
*adoption: moderate*

- **What:** The bridge that makes P2-1/P2-2 adoptable in an automated skill — emit a
  data-movement / transaction inventory and feed an automated counter, keeping the
  "point-and-get-a-number" UX while replacing LOC-derived FP with a real functional count.
- **Source:** ScopeMaster (2024); Soubra & Abran automated-COSMIC papers (2019–2022).

---

## Cluster 2 — Honest uncertainty (replace the 0.6/1.0/1.6× band)

### P2-5 Report empirical accuracy bounds — PRED(25)/PRED(30) and MMRE
*adoption: drop-in (front-half is P0-18)*

- **What:** Uncalibrated parametric models routinely score MMRE ≈ 1.0 (~100% avg error) and
  PRED(25)=0 on real datasets. Stating this in the methodology converts the "$73K realistic"
  false precision into an honest order-of-magnitude.
- **Source:** Foss/Stensrud/Kitchenham/Myrtveit, IEEE TSE 2003; Port & Korte, ESEM 2008;
  multiple COCOMO-accuracy studies 2020–2024.

### P2-6 Monte Carlo over three-point / PERT inputs → a real cost distribution
*adoption: moderate*

- **What:** Express each uncertain driver (size, productivity, rate) as optimistic/most-likely/
  pessimistic, fit Beta-PERT (`mean=(O+4M+P)/6`) or triangular, run thousands of iterations →
  a cost CDF with P50/P80/P90. KLOC, EAF, rate, and the team spread become distributions
  instead of fixed scalars.
- **Why here:** Turns "Low/Mid/High = ×0.6/×1.0/×1.6" into a defensible probabilistic
  statement — the single highest-leverage replacement for the fake band (P1-15).
- **Source:** PMI PMBOK (three-point/Monte Carlo); AACE RP 57R-09; Beta-PERT (Malcolm 1959).

### P2-7 Reference-class forecasting (outside view) instead of a fixed multiplier
*adoption: major-rework*

- **What:** Build a distribution of *actual* outcomes for a reference class of similar past
  projects, place the current one on it, apply an empirical uplift for optimism bias. The de
  facto debiasing technique for cost/schedule forecasting.
- **Why here:** A skill that runs on many repos can use its own corpus of past analyses (or
  ISBSG/SEACRAFT) as the reference class: "projects of this size/stack/complexity historically
  cost X with this spread." Data-anchored range, not an arbitrary multiplier.
- **Source:** Flyvbjerg, "From Nobel Prize to Project Management" (2006); Flyvbjerg & Bester
  (2021); RCF review, *Production Planning & Control* (2025).

### P2-8 Bayesian calibration to local data
*adoption: major-rework*

- **What:** Treat A, E, productivity, $/hr, AI factors as priors and update them with whatever
  local actuals exist (git-derived effort, the org's past estimate-vs-actual pairs, ISBSG).
  Directly addresses COCOMO's core requirement — calibrate to local data — which the tool
  currently ignores by hardcoding A=2.94 (see P1-19/P1-20).
- **Source:** Mendes & Mosley (Bayesian web effort); Stamelos et al. (BBN for effort, 2003);
  probabilistic-effort-estimation systematic review (2019).

---

## Cluster 3 — Cross-checks & ensemble (stop claiming to be "the" answer)

### P2-9 Putnam SLIM (Rayleigh) as a second parametric estimate
*adoption: moderate*

- **What:** `Size = Productivity × Effort^(1/3) × Time^(4/3)`; effort rises steeply as
  schedule compresses (`effort ∝ 1/Time^4`). Running it alongside COCOMO yields a second
  independent estimate and an explicit schedule/effort trade-off; where the two families
  disagree, that spread is honest uncertainty. Its productivity parameter can be calibrated
  from the repo's own git history (P2-11).
- **Source:** Putnam & Myers, *Five Core Metrics* (2003); Putnam, IEEE TSE (1978).

### P2-10 SEER-SEM and Use-Case Points as alternative families
*adoption: moderate*

- **What:** SEER-SEM (~30% accuracy ~62% of the time) and UCP (sizes from actors + use cases).
  UCP maps naturally to a repo — detected endpoints/handlers ≈ use cases/transactions — giving
  a size that doesn't reward verbose/AI-bloated code. Lets the tool report a model-ensemble
  spread and calibrates user expectations about how precise *any* such number can be.
- **Source:** Galorath & Evans (2006); Karner UCP (1993); Ochodek et al. (2011).

---

## Cluster 4 — Ground the AI-era claims in real data

### P2-11 Git-history effort reconstruction + provenance (replace the from-scratch fiction)
*adoption: moderate*

- **What:** (a) Infer actual person-hours from commit timestamps grouped into work sessions
  (`git-hours`, `git2effort`) — a *measured* actual-effort anchor to compare against and
  calibrate the parametric reproduction estimate. (b) Provenance: estimate how much of the repo
  was AI-generated (commit-trailer / `Co-Authored-By` attribution, AI-authorship classifiers);
  devs self-report ~41–42% AI-assisted code in 2025.
- **Why here:** Turns the AI section from a fabricated "110×" into "git-reconstructed actual
  effort ≈ N hours vs parametric-from-scratch ≈ M hours," and makes the human-baseline
  assumption explicit (if 42% is AI-generated, "what a human team would charge" is hypothetical
  and should be flagged). Both run from data the read-only git phase already collects.
- **Source:** Robles et al., git2effort (arXiv:2203.09898); `kimmobrunfeldt/git-hours`;
  AI-generated-code provenance studies & SLSA (2024–2025).

### P2-12 METR 2025 RCT + DORA 2024/25 + GitClear — ground or kill the AI-speed headline
*adoption: drop-in (this is the evidence base for P0-19)*

- **What:** METR (Jul 2025, randomized, 16 experienced devs, 246 real tasks): AI made them
  **19% slower** while they believed they were ~20% faster. DORA 2024: every +25% AI adoption
  correlated with −1.5% throughput and −7.2% delivery stability (positive only near ~90%
  adoption in 2025, stability still suffers). GitClear (211M LOC): churn/clone rose sharply,
  refactoring fell below 10%. Earlier Copilot lab study: ~55% faster on an *isolated greenfield*
  task — which does not generalize to end-to-end delivery.
- **Why here:** The tool's most screenshot-able output ("330 human hours vs 3 AI = 110×") is its
  most indefensible. Cite this to show single-task lab speedups don't generalize and
  self-reported AI hours are an unreliable baseline.
- **Source:** METR, arXiv:2507.09089 (Jul 2025); DORA 2024 + State of AI-assisted Software
  Development 2025; GitClear 2024/2025.

### P2-13 #NoEstimates — throughput / cycle-time Monte Carlo from actual history
*adoption: moderate*

- **What:** Where a repo has real git history, forecast from its own demonstrated cadence
  (commits/PRs/issues per week) by Monte-Carlo-simulating completion, instead of pretending to
  rebuild it from scratch. Uses real local data and is honest about what was actually expended —
  the natural empirical foil to the speculative from-scratch baseline.
- **Source:** Vacanti, *Actionable Agile Metrics* (2015); Duarte, *#NoEstimates* (2016).

---

## Cluster 5 — Name the concept (pure labeling, large payoff)

### P2-14 Reproduction/replacement cost vs value vs market-comparable
*adoption: drop-in (front-half is P0-17 / P0-23)*

- **What:** Three distinct lenses: (1) **reproduction/replacement cost** — rebuild equivalent
  functionality from scratch (cost approach) — *what this tool actually computes*; (2)
  **value/income** — worth from revenue/users/strategic value, decoupled from build cost; (3)
  **market/comparable** — benchmarked against comparable assets/acquisitions.
- **Why here:** The tool blurs "what it would cost to build" into a "Headline Valuation"
  implying worth. Labeling the output explicitly as a *cost-approach reproduction estimate* —
  and noting value can be far higher OR lower (most code has near-zero standalone market value;
  a 1,000-line script can underpin a $10M business) — prevents the most damaging misuse.
- **Source:** International Valuation Standards (IVS) 2025; software/intangible-asset valuation
  literature; FASB ASC 350-40.

---

## Suggested sequencing within P2

1. **Drop-in now (do alongside P0):** P2-5 (accuracy bounds), P2-12 (AI evidence), P2-14
   (cost-vs-value labeling).
2. **Next, moderate, high payoff:** P2-6 (Monte Carlo band), P2-11 (git-effort + provenance),
   P2-3 (SNAP mapping), P2-9/P2-10 (SLIM/UCP cross-check), P2-13 (#NoEstimates).
3. **The real redesign:** P2-1/P2-2 (FP-from-structure → effort), P2-7 (reference-class
   forecasting), P2-8 (Bayesian calibration). This is what finally removes the LOC anchor and
   the uncalibrated-A problem at the root.
