# P2 — Research-backed Redesign: Implementation Plan

Plan to implement all 14 findings in `P2-research-redesign.md`. Line numbers refer to
`skill/SKILL.md`, `README.md`, `examples/sample-report.md`, and
`examples/sample-report-codebase.md` **as of the current working tree (post-P0, post-P1)**.
This plan follows the P0/P1 house style: §0 structural decisions (S-prefixed), §1 per-item
fixes (severity, **Verify** blocks, exact bash/awk), §2 test plan, §3 risks / open decisions,
§4+ red-team rounds whose **Amendments (A-prefixed) are AUTHORITATIVE and supersede conflicting
body text**, and a final §N implementation outcome.

> **Scope (locked with the user):** implement **all 14** P2 items, **including** P2-7
> (reference-class forecasting) and P2-8 (Bayesian calibration), which requires adding an
> **optional local calibration corpus** that lives **outside** the analyzed repo. For the FP
> redesign (P2-1/P2-2), the replace-LOC-vs-alongside fork was left to "decide during planning";
> §0 S2 resolves it to **alongside, archetype-gated** on decisive empirical evidence (R1), and
> §3 R1 records it for red-team confirmation.

> **Self-referential caveat (`[[sample-report-is-self-referential]]`):** the flagship
> `examples/sample-report.md` is produced by running the skill on this repo's own shipped files,
> so editing `SKILL.md` changes its line/token counts and therefore the sample's numbers. Both
> `sample-report.md` (self) and `sample-report-codebase.md` (the neutral
> `examples/calibration-codebase/` stack-VM) MUST be regenerated from a **frozen copy** of the
> shipped files after implementation (copy shipped files + a throwaway `.git` into a temp dir,
> run the pipeline there — the P0 "A17 temp-dir method").

---

## Grounding evidence (measured before planning)

Two feasibility experiments were run against the two shipped fixtures; they drive S2 and S4.

**E1 — structural-FP signals collapse on non-web code.** `examples/calibration-codebase/` is a
2,014-LOC Python stack-VM/compiler. Greps for the artifacts the IFPUG/COSMIC mappings need:

| signal | calibration VM | meaning |
|---|---|---|
| mutating routes (POST/PUT/PATCH/DELETE) | **0** | → 0 EI |
| GET/read routes | **0** | → 0 EQ/EO |
| ORM entities / models | **0** | → 0 ILF |
| SQL CREATE TABLE / migrations | **0** | → 0 ILF |
| DB read/write calls | **0** | → 0 COSMIC Read/Write |
| queue ops | **0** | → 0 COSMIC Entry/Exit |
| CLI commands (argparse `add_parser` subcommands) | 6 | UCP "use case" proxy exists |
| public functions / classes | 121 / 55 | interface surface exists |

A naïve "size = structural FP from web artifacts" would estimate **~0 FP → ~$0** for a genuinely
complex interpreter — re-introducing, *worse*, the web-app bias P1 removed. **Decisive
conclusion:** structural FP/COSMIC **must not** be the size anchor; LOC stays the only universal
size measure (it is the foundation of the P1 domain-fairness MAX logic). FP/COSMIC run
**alongside, archetype-gated** (suppressed as "N/A — not transaction-oriented" when their signal
is below a floor, never reported as a misleading tiny number). UCP is gated on detectable
use-cases (CLI/handlers).

**E2 — git-effort needs a history floor.** `git log` session reconstruction (per-author,
120-min intra-session gap, +120-min first-commit charge) runs read-only in awk. On this repo
(3 commits, a squashed export) it returns 6.0 h — meaningless; the calibration fixture has no
`.git` at all. **Conclusion:** git-effort + #NoEstimates are **gated contextual anchors**
(require ≥ a minimum commit/contributor/age threshold), never the headline. Provenance works:
2/3 commits here carry `Co-Authored-By: Claude`.

---

## §0 Structural decisions

These are the root-cause designs that several findings hang off. Each names the findings it
closes and the SKILL.md surface it touches. The unifying frame: **the tool stops emitting one
COCOMO-on-LOC number and instead emits a single, explicitly-labeled cost-approach reproduction
estimate that is (a) cross-checked by an archetype-gated ensemble of independent estimators,
(b) wrapped in a real Monte-Carlo probability band, (c) anchored against a measured git-effort
actual, and (d) optionally calibrated to a local corpus.** COCOMO-on-LOC remains the headline
*engine*; everything else corroborates, bands, or labels it.

### S1 — Reframe every output as a *cost-approach reproduction estimate* (three lenses) *(closes P2-14; front-half done in P0-17/P0-23)*

The report already says "reproduction cost ≠ value." S1 makes the **three valuation lenses**
explicit and load-bearing, once, near the top, and threads the label through:

- **(1) Reproduction / replacement cost (cost approach)** — *what this tool computes*: parametric
  cost to rebuild equivalent functionality from scratch.
- **(2) Value / income approach** — worth from revenue/users/strategic value; **decoupled** from
  build cost (a 1,000-line script can underpin a $10M business; most code has near-zero standalone
  market value).
- **(3) Market / comparable approach** — benchmarked against comparable asset/acquisition prices.

Surface: a new short "**What this is (and is not)**" callout after the top disclaimer; rename the
"Headline Valuation" section to "**Headline: Reproduction-Cost Estimate**" (the word *Valuation*
falsely implies lens 2/3); one Methodology bullet citing IVS 2025 / FASB ASC 350-40. **Text-only,
no math change.**

### S2 — Estimator ensemble with LOC as the universal anchor; FP/COSMIC/UCP as archetype-gated cross-checks *(closes P2-1, P2-2, P2-9, P2-10; resolves R1)*

Per E1, **LOC stays the size anchor and COCOMO-on-LOC stays the headline engine.** Add a new
**Phase 2.5 (Structural Size & Estimator Ensemble)** and an "Estimator Ensemble" report section.
Members, each producing an effort-hours estimate:

| Estimator | Size input | Availability | Independent of LOC? |
|---|---|---|---|
| **COCOMO II** (existing) | Effective KLOC | always | anchor |
| **Putnam SLIM** (P2-9) | — | **citation-only** (no computed number, no ensemble row — A3) | n/a |
| **IFPUG UFP → effort** (P2-1) | UFP from routes/entities | gated: `transaction_signal ≥ floor` | **yes** (structural) |
| **COSMIC CFP → effort** (P2-2) | data movements | gated: `movement_signal ≥ floor` | **yes** (structural) |
| **Use-Case Points → effort** (P2-10) | UCP from actors+use-cases | gated: `usecase_signal ≥ floor` | **yes** (structural) |
| **Backfired FP** (LOC/gearing) | LOC | always | **no — labeled "≈LOC in disguise"** |

The ensemble's purpose (Cluster 3, "stop claiming to be *the* answer"): show whether the
**structure-anchored** estimators agree or disagree with the **LOC-anchored** ones, as a **separate
qualitative remark only** — **no "convergence → confidence" claim** (A4); per A2 it does NOT
numerically widen the MC band. On a non-transactional codebase the ensemble offers at most one
independent cross-check (UCP) and the headline rests on COCOMO alone. Gated-out estimators render
"**N/A — codebase is not
{transaction/use-case}-oriented; this method does not apply**", never a number. The headline is
**never** the mean of the ensemble (that would let a collapsed-to-0 structural estimator drag a
compiler's cost down); it is the **deterministic COCOMO point estimate** (identical to today's
number — A2); P50 is a secondary band landmark only. **Resolves the FP fork → alongside+gated** (R1).

### S3 — Replace the ×0.5–×2.0 band with a Monte-Carlo probability distribution; state empirical accuracy bounds *(closes P2-5, P2-6; supersedes P1-15's symmetric band)*

Add **Phase 3.9 (Monte-Carlo uncertainty)**: express the load-bearing drivers as **triangular**
three-point inputs (triangular inverse-CDF; Beta-PERT is **citation-only, not a runtime path** — A1)
and simulate in **seeded awk** (find-derived integer seed → reproducible reports) to produce a
cost CDF with **P10 / P50 / P80 / P90**. Drivers and their O/M/P spreads:

- **Size** (KLOC): ±(generated/vendored/measurement error). *(The ensemble spread does NOT feed
  the band — A2; it is a separate qualitative note.)*
- **Productivity** (hours/KLOC equivalently EAF): the dominant uncertainty; spread reflects the
  uncalibrated-model error from P2-5.
- **Rate is NOT sampled** (A2): it lives only in the Phase-4 four-profile rate-sensitivity table, so
  the MC varies only size + productivity at the fixed mid rate (avoids the H6 double-count).

The **headline = the deterministic COCOMO point**; the **band = P10–P90** (replacing the
cherry-pick-free but invented ×0.5–×2.0), with **P50 a secondary landmark sitting modestly above the
point by right-skew** (≈×1.0–1.3 = expected overrun risk, not a continuity failure — A2). A
Methodology subsection states the **empirical accuracy bounds** (P2-5): uncalibrated
parametric models routinely show **MMRE ≈ 1.0 (~100 % mean error)** and **PRED(25) ≈ 0–30 %** on
real datasets, so the band is wide by construction and the P50 is an order-of-magnitude. Under
`OUT_OF_DOMAIN` the four-column band is **suppressed** and a single decade bucket is emitted (e.g.
"~$500; treat P10–P90 as within one decade") — **not** four separately-rounded percentiles (A9/M7).

### S4 — Measured-actual anchor: git-effort reconstruction, AI provenance, throughput forecast *(closes P2-11, P2-13)*

Use the git data Phase 1b already collects (no new repo reads beyond `git log`). Add a
**"Measured vs Parametric" section**:

- **git-effort (P2-11):** session-reconstruction person-hours (git2effort defaults: per-author,
  120-min intra-session gap, +120-min first-commit charge) → a **measured** actual-effort anchor
  to compare against the parametric *from-scratch* number. **Gated** (E2): require ≥ `MIN_COMMITS`
  and a non-trivial age, else "N/A — insufficient git history".
- **Provenance (P2-11):** `Co-Authored-By:` / AI-trailer fraction → estimate of AI-assisted share;
  cite the 2025 ~41–42 % self-reported figure; flag the "from-scratch human" baseline as
  increasingly **fictional** when AI share is high.
- **#NoEstimates throughput (P2-13):** Monte-Carlo over the repo's **demonstrated weekly commit
  cadence** → an empirical completion-time forecast, as a foil to the from-scratch schedule.
  Gated identically.

These are **context anchors, never folded into the dollar headline** (same discipline as IE).

### S5 — Optional local calibration corpus → reference-class forecasting + Bayesian update *(closes P2-7, P2-8)*

Add an **opt-in** corpus that lives **outside** the analyzed repo (Constraint 2 preserved),
mirroring the report-output policy:

- Location: `${COST_ESTIMATE_CORPUS:-$HOME/.cost-estimate/corpus.jsonl}`. **Append is opt-in:** the
  skill only writes a record when `COST_ESTIMATE_CORPUS` is **set** (default-file existence enables
  **READ only** — A7; so default behavior is unchanged and nothing is created or appended silently).
  Each record is one JSON line:
  `{date, repo(basename), kloc, fp, stack, complexity_avg, estimate_p50_hours, actual_git_hours}`.
- **Reference-class forecasting (P2-7):** when the corpus holds ≥ `MIN_CLASS` (e.g. 5) records in a
  similar class (size band × stack × complexity), build the distribution of their outcomes, place
  the current estimate on it, and report an **outside-view** central + uplift. Else: "N/A — need ≥
  N comparable past analyses; outside view unavailable".
- **Bayesian calibration (P2-8):** treat the model's productivity (hours/KLOC) as a **log-normal
  prior**; update with the corpus's local actual hours/KLOC via a precision-weighted blend on the
  log scale → posterior productivity, which shifts the MC P50/band. Disclose prior, data, posterior.
- All corpus features **degrade gracefully to today's behavior** when absent.

### S6 — Map the 8 non-functional factors to SNAP (ISO/IEC/IEEE 32430:2025) *(closes P2-3)*

The 8 complexity factors are mostly **non-functional** (auth, infra, error handling, security,
data ops). Map them to SNAP categories/sub-categories and report a **SNAP-point** size **alongside**
FP (functional + non-functional = the IFPUG pair). SNAP feeds the report as context and, for the
transaction-app path only, can add to the FP→effort cross-check. Cite the **current 2025** standard
(replaces the P0-14 stray SNAP v2.4 name-drop). Heuristic mapping; disclosed as such.

### S7 — Ground the AI-speed claims in verified 2025 evidence *(closes P2-12; mostly done, extend)*

The AI Speed Comparison already cites METR/DORA/GitClear. S7 **verifies and pins the exact
figures** (METR Jul 2025 RCT arXiv:2507.09089 — 19 % *slower*; DORA 2024 — +25 % AI ↔ −1.5 %
throughput / −7.2 % stability; GitClear — refactoring < 10 %, churn/clone up; Copilot lab ~55 %
greenfield-only) and connects them to the new measured-vs-parametric anchor (S4) so the ratio is
framed as "self-report vs hypothetical," not a measurement.

### S0 — Honesty & uncertainty discipline (cross-cutting)

Every new estimator/anchor ships **with its disclosed approximation and a "heuristic / uncalibrated"
note**, matching the existing house style. New numbers never silently widen the headline: the
ensemble and anchors corroborate or band, they do not sum. Determinism is mandatory — the only
randomness (S3 Monte Carlo) uses a **fixed seed**. No new network/installs; analyzed repo stays
read-only; the corpus is the one new write target and it is outside the repo and opt-in.

---

## §1 — Per-item fixes

Every new estimator carries a **Disclosed limitation** line (the heart of S0): the canonical
method needs data a static snapshot lacks, so each ships as a *labeled approximation*. Severities:
🔴 critical, 🟠 high, 🟡 medium, ⚪ low.

---

### P2-14 🟠 Name the three valuation lenses; relabel "Headline Valuation" *(S1; front-half P0-17/P0-23)*

Pure labeling, largest payoff/cost ratio — do first so every later number inherits the frame.

- **Report:** after the top ⚠️ disclaimer add a compact callout:
  > **What this is — and is not.** Three independent lenses can put a number on software:
  > **(1) reproduction/replacement cost** *(this tool)* — parametric cost to rebuild equivalent
  > functionality from scratch; **(2) value/income** — worth from revenue/users/strategy,
  > *decoupled* from build cost; **(3) market/comparable** — comparable-sale benchmarks. A
  > 1,000-line script can underpin a $10M business, and most code has near-zero standalone market
  > value, so reproduction cost ≠ value and ≠ price.
- Rename `## 🏷️ Headline Valuation` → `## 🏷️ Headline: Reproduction-Cost Estimate (cost approach)`
  (`:1305`). Keep the existing in-block wording.
- **Methodology bullet:** add one citing IVS 2025 / FASB ASC 350-40 for the three approaches.
- **Disclosed limitation:** none new — this *removes* an overclaim.
- **Verify:** grep the rendered report for "Valuation" → only appears inside the lens explainer,
  never as a standalone headline; the three lenses appear exactly once near the top.
- **Files:** `SKILL.md` (report template + 1 methodology bullet), `README.md` (mirror the frame).

---

### P2-5 🟠 State empirical accuracy bounds — MMRE / PRED *(S3; drop-in, front-half P0-18)*

- **What:** add a Methodology subsection **"How accurate is this, really?"** stating the
  published accuracy of *uncalibrated* parametric models, as **literal constants** (nothing
  computed at runtime): uncalibrated COCOMO on real data scores **MMRE ≈ 1.0 (~100 % mean error)**
  and **PRED(25) ≈ 0** (Jeklin/Saad/Ekawati 2025 over 63 NASA projects; basic-COCOMO MMRE
  0.9996, PRED(0.25)=0). The "acceptable" bar is **MMRE ≤ 0.25 and PRED(25) ≥ 75 %** (Conte/Boehm),
  which uncalibrated models miss badly; *calibrated* COCOMO II reaches PRED(30) ≈ 52–64 %, and the
  Bayesian variant 75–80 % — motivating S5.
- **Honest framing:** "We cannot report THIS repo's MMRE/PRED — that needs many completed projects
  with audited actuals; a snapshot is n = 1. The figures above are a property of the *method class*
  and are why the band below (P2-6) is wide and the P50 is order-of-magnitude."
- **Disclosed limitation:** stated inline (above).
- **Verify:** the subsection cites MMRE ≈ 1.0 and PRED(25) ≈ 0 with the source and the n = 1 caveat;
  no per-repo MMRE/PRED is ever printed.
- **Files:** `SKILL.md` (Methodology), `README.md` (limitations).

---

### P2-6 🔴 Monte-Carlo probability band replaces the ×0.5–×2.0 band *(S3; supersedes P1-15)*

The single highest-leverage change. New **Phase 3.9**, run after Step 3.8, in **one seeded awk
block** (determinism is mandatory — a re-run on the same repo must give identical percentiles).

- **Linear-multiplier design (A1):** precompute the **deterministic point cost `C0` once**; each of
  `N=10000` iterations multiplies `C0` by **linear** triangular draws `m_size × m_prod`. **Rate is
  NOT sampled** (A2 — rate lives only in the Phase-4 four-profile table). The only transcendental in
  the loop is the triangular `sqrt`.
- **Multiplier three-points (O/M/P)** — explicit per A11:
  - **`m_size`:** `O = 1 − genfrac − 0.10`, `M = 1`, `P = 1.30` (generated/vendored + measurement
    uncertainty on size; `genfrac` per A11 #5 — see below). The ensemble spread does **NOT** widen
    this (A2).
  - **`m_prod`:** `O = 0.5`, `M = 1`, `P = 2.0` — the *old* ×0.5/×2.0 becomes the productivity
    multiplier three-point, justified directly by P2-5's MMRE ≈ 1.0.
  - **`genfrac` (defined per A11 #5):** `genfrac = (GENERATED_TOTAL_LOC + vendored_LOC) /
    raw_source_LOC_before_exclusions`, clamped to `[0,0.5]` (how much was removed, on the
    pre-exclusion raw total). Apply the M10 optimistic-endpoint clamp from A1.
- **Sampler:** **triangular inverse-CDF** (A1; Beta-PERT is citation-only, not a runtime path):
  `Fc=(M−O)/(P−O)`; `U<Fc → X=O+√(U·(P−O)·(M−O))`, else `X=P−√((1−U)·(P−O)·(P−M))`. Guard `P==O`,
  `P==M`, `M==O` (degenerate → constant).
- **PRNG (the single PRNG site — A1):** **Park–Miller minimal-standard with Schrage** (no double
  overflow): `m=2147483647`, `a=16807`, `q=127773`, `r=2836`. **Seed = pure function of
  find-derived integer, tool-invariant signals** (A11 #1), never time/`$RANDOM`/`srand()`-no-arg:
  `SEED = ((CODE_FILE_COUNT*1000003 + TOTAL_FILE_COUNT*10007 + COMPLEXITY_SUM*101) % 2147483647)`,
  forced ≥ 1. `SOURCE_CODE_LOC` is **dropped from the seed** (cloc-vs-wc divergent — cloc=2014 vs
  wc-raw=2736 on the VM).
- **N = 10,000** iterations; `cost_i = C0 × m_size_i × m_prod_i`. **Round each sample to integer
  dollars** (`printf "%.0f"`) then `LC_ALL=C sort -n` (the single ranking method — A11 #6; no in-awk
  quicksort). Integer-guarded percentile index (A1): `idx=int(p*n); if(idx<p*n)idx++; clamp 1..n`
  over 1-indexed arrays, for **P10/P50/P80/P90**.
- **Headline (A2):** the published headline is the **deterministic COCOMO point** (= today's
  number); the **band = P10–P90**; **P50 is a secondary band landmark only**, sitting ≈×1.0–1.3
  above the point by right-skew (= expected overrun risk). The old `× 0.5 / × 2.0` headline text
  (`:977`–`:991`, `:1269`, `:1313`, `:1372`) is replaced; the band is now labeled *"Monte-Carlo
  P10–P90 over triangular size/productivity inputs at the fixed mid rate; productivity spread set
  from the ~100 % MMRE of uncalibrated parametric models (P2-5) — a model-uncertainty band, not an
  elicited risk distribution."*
- **OUT_OF_DOMAIN (A9):** suppress the four-column band and emit a **single decade bucket** (e.g.
  *"~$500; treat P10–P90 as within one decade"*), **NOT** four separately-rounded 1-sig-fig
  percentiles.
- **Disclosed limitation:** the O/M/P spread is a **heuristic multiplier on measured size**, not
  expert-elicited per AACE 57R-09; percentiles are only as meaningful as that spread. Single-driver
  (no input correlation) is the honest simplification. Stated in Methodology.
- **Verify:** (a) run the awk block twice on this repo → byte-identical P10/P50/P80/P90
  (determinism). (b) `P10 ≤ P50 ≤ P80 ≤ P90` always. (c) the published **deterministic point** equals
  the pre-P2 point (±0 by construction — A2), and P50 sits ≈×1.0–1.3 above the point (expected
  right-skew, not a continuity failure). (d) degenerate inputs (`KLOC` tiny) don't divide-by-zero or
  emit NaN. (e) seed differs between this repo and the calibration codebase (different find-derived
  signals).
- **Files:** `SKILL.md` (new Phase 3.9; edits to Step 3.8, Effort/Cost/Headline templates,
  Methodology), `README.md`.

---

### P2-1 🟠 IFPUG Unadjusted Function Points from structure — archetype-gated cross-check *(S2; resolves R1)*

Kills the circular `FP = LOC ÷ ratio` *as the FP definition*; the LOC-ratio backfire survives only
as an explicitly-labeled "≈ LOC" row. New work lives in **Phase 2.5**.

- **Count UFP from detected artifacts** — patterns are **framework-anchored, word-bounded,
  case-sensitive, and scoped to web/app SOURCE extensions via `--include` (NEVER `.md`/`.txt`)**.
  *(Prototype-validated mandate: scanning docs false-positives — this very repo's `SKILL.md`/sample
  reports/this plan contain illustrative `@app.post`, `CREATE TABLE`, `class X(Base)` strings that
  un-gate a non-web repo if `.md` is grepped; source-scoping yields the correct N/A. Also exclude
  the `DISPATCH` compiler idiom from bare-verb matching — H2.)* (occurrence counts, `LC_ALL=C`):
  - **EI** = mutating route handlers (`@(app|router)\.(post|put|patch|delete)\b`, Rails
    `\b(create|update|destroy)\b` in `*_controller.rb`, `@(Post|Put|Patch|Delete)Mapping\b`…) +
    queue producers.
  - **EQ** = read-only `GET` handlers with no derived-output signal.
  - **EO** = `GET`/report handlers with derived signals (`aggregate|sum|report|export|group_by|
    chart`). If indistinguishable, classify all reads as EQ (conservative) + note.
  - **ILF** = distinct owned entities/models/migrations (`CREATE TABLE`, ORM model classes,
    migration files, deduped).
  - **EIF** = distinct external data sources referenced-not-owned (often 0 from a snapshot → 0 + note).
  - **Complexity column** is **not** statically recoverable (needs DET/RET/FTR) → fixed rule:
    default every instance to **Average** (`EI×4, EO×5, EQ×4, ILF×10, EIF×7`); optionally push ILF
    to High (15) when Data-Layer factor ≥ 4. Deterministic.
  - `UFP = 4·EI + 5·EO + 4·EQ + 10·ILF + 7·EIF` (IFPUG CPM 4.x / ISO/IEC 20926 weights). Skip VAF
    (judgment-based, deprecated by ISO 20926).
- **UFP → effort:** `Effort_hours = UFP × PDR`, PDR band **LOW 4 / MID 10 / HIGH 15 h/FP** (ISBSG
  Practical Guide 2019: avg 6.3, P25 2.6, median 3.6, P90 13.6; worked Java new-dev 10.2; 3GL
  median 13.3). Report the MID as the FP estimator's effort, LOW/HIGH feeding the ensemble spread.
- **Backfired FP (the old metric, relabeled):** keep `FP ≈ Σ LOC_lang / gearing_lang` but **label
  it "≈ LOC in disguise — not independent."** Per A4 the **report's "Estimated Function Points" keeps
  the existing Jones Step-3.7 LOC/ratio table unchanged** (continuity — FP is non-load-bearing); QSM
  gearing (Java 53, C 99, C++ 53, C# 59, JS 53, SQL 21, COBOL 55, default 55) is mentioned only as a
  methodology footnote for this backfired row, not substituted into the reported FP value.
  **Point-of-display caveat (closes R3-M5 labeling gap):** the reported "Estimated Function Points"
  value carries, inline at its point of display, *"≈ LOC ÷ language gearing — a restatement of size,
  not an independent functional count; the structure-derived FP cross-check is reported separately
  (N/A on non-transactional code)"*, so a reader cannot mistake the LOC-derived number for the real
  functional count the section title implies.
- **ARCHETYPE GATE (the E1 fix; un-gate composition per A11 #2):** compute
  `transaction_signal = EI+EQ+EO+ILF`. **Un-gate (structural FP applies) only when**
  `transaction_signal ≥ FP_FLOOR` (= 3) **AND** (**≥ 2 distinct artifact kinds present** — e.g. a
  route AND an ILF — **OR** a single kind clearing a higher single-kind floor of **≥ 5**, e.g. ≥ 5
  routes). This ensures a **routes-only API (ILF = 0, 5 routes) is NOT wrongly gated out**. Otherwise
  the structural-FP estimator renders **"N/A — not a transaction-oriented codebase; IFPUG FP does not
  apply (this is normal for compilers, numerical/ML, games, embedded, libraries)."** It is **excluded
  from the ensemble** (and per A2 the band never reflects the ensemble anyway), never reported as a
  misleading small number. The backfired-FP "≈LOC" row may still show (it always exists) but is
  clearly the dependent one.
- **Disclosed limitation:** complexity Low/Avg/High and EIF are not statically measurable; EI/EQ/EO
  splits are heuristic; PDR is an org constant (4–15 h/FP swings effort ~4×). Backfiring "varies
  500 % across languages" (Capers Jones) and is not endorsed by any FP association → order-of-magnitude.
- **Verify:** (a) calibration VM → `transaction_signal = 0` → structural FP renders N/A, **not $0**,
  and the headline is unchanged from today. (b) a synthetic 5-route + 3-model Flask app → nonzero
  UFP with EI/EQ/ILF counts matching a hand count. (c) UFP arithmetic exact in awk.
- **Files:** `SKILL.md` (new Phase 2.5; add structural UFP + relabeled backfire in Phase 2.5; leave
  Step 3.7's report FP value unchanged — A4 continuity; Effort/Methodology), `README.md`.

---

### P2-2 🟡 COSMIC data-movement size (CFP) — archetype-gated cross-check *(S2)*

- **Count** Entry/Exit/Read/Write at **1 CFP each** (ISO/IEC 19761): routes → `2 × route_count`
  (Entry+Exit), read-verbs (`SELECT|find|query|redis GET`) → Read, write-verbs
  (`INSERT|UPDATE|save|persist|migrate|publish|enqueue|redis SET`) → Write, queue-consume → Entry.
  `CFP = E+X+R+W`; floor `CFP = max(CFP, 2×functional_processes)` (min process = 2 CFP). Cap
  per-verb-per-file occurrences to damp loop inflation.
- **CFP → effort:** reuse the FP PDR band as a rough hours/CFP (no canonical CFP→hours constant);
  label heuristic.
- **Same archetype gate** as P2-1 (calibration VM → CFP signal 0 → N/A).
- **Disclosed limitation (prominent):** **not ISO-19761-conformant from a snapshot** — canonical
  COSMIC is requirements-level; code cannot identify functional-process boundaries, objects of
  interest, or data-group granularity; naive grep violates the uniqueness rule and inflates R/W; no
  published MMRE for repo-grep COSMIC. Label `CFP_APPROX`.
- **Verify:** calibration VM → N/A; a CRUD app → CFP in plausible 2× range of UFP×~ small factor;
  determinism (pure counting).
- **Files:** `SKILL.md` (Phase 2.5), `README.md`.

---

### P2-3 🟡 Map the 8 non-functional factors to SNAP (ISO/IEC/IEEE 32430:2025) *(S6; fixes P0-14 name-drop)*

- **What (per A9/M2 — NO aggregate total):** report SNAP as a **qualitative non-functional
  checklist**, **never an aggregate-summed SNAP-point number** (12 of 14 sub-category weights are
  paywalled, so a total would be ~86 % invented). Map each of the 8 factors and the domain probes to
  SNAP sub-categories (Security grep→1.1 Data-Entry Validations; MATH probe→1.2 Logical/Math Ops;
  entities/Data-Layer→1.4/1.5; queue→3.3; Infra factor→3.1; routes→2.x) and report **which
  categories are present** at what tier (≤2 Low, 3 Avg, ≥4 High). It is **paired with** FP for
  context and **never added to FP, the headline, or the FP→effort cross-check** (the "off by
  default" add is **not implemented** — A9/M2).
- **Weights / numbers:** if any number is shown it is **only the 2 public-weight sub-categories**
  (1.1 = 2/3/4; 1.2 Logical 4/6/10, Math 3/4/7), labeled *"partial SNAP: 2 of 14 scored; the other
  12 require the paywalled APM v2.4 / ISO 32430 tables."* No SNAP→hours constant. The ISO/IEC/IEEE
  32430:2025 citation appears in the Methodology note as *the standard the mapping references*, never
  as a computed number's provenance.
- **Disclosed limitation:** SNAP is defined over requirements/design intent; code-grep DET proxies
  systematically mis-size; only 2 of 14 weight tables are public; IFPUG doesn't endorse automated
  SNAP. Heuristic, reported for transparency.
- **Verify:** SNAP section cites the 2025 ISO/IEC/IEEE 32430 standard; the old stray "SNAP v2.4"
  multiplier reference (P0-14) is gone; SNAP points never enter the dollar headline.
- **Files:** `SKILL.md` (Phase 2.5 + report section + fix P0-14 line), `README.md`.

---

### P2-4 ⚪ Automated FP/COSMIC counting bridge — realized by P2-1/P2-2 *(S2)*

Not a separate computation: P2-4 ("emit a transaction / data-movement inventory and feed an
automated counter, keeping point-and-get-a-number UX") **is** the grep-based EI/EO/EQ/ILF/EIF and
E/X/R/W inventories built in P2-1/P2-2. Deliverable: Phase 2.5 prints the raw **inventory table**
(counts per category with the files that drove them) so the FP/COSMIC numbers are auditable, not a
black box. **Verify:** the inventory line items sum to the UFP/CFP inputs. **Files:** `SKILL.md`.

---

### P2-9 🟠 Putnam SLIM — citation-only second parametric family *(S2; A3)*

Per **A3**, SLIM cannot produce a defensible number from a snapshot (PP is unmeasurable; the `·B`
form scales effort 2.5–6×; SLOC-vs-KSLOC is a unit hazard; effort ∝ Size³ is a cubic gameability
lever; `Time` from a same-day git span makes effort ∝ Time⁻⁴ explode/`NaN`). **P2-9 is therefore
implemented as citation-only:**

- **Citation only — NO computed number, NO ensemble row.** Cite **Putnam SLIM / the Rayleigh model**
  as a second parametric *family*, and explain the schedule↔effort trade-off **qualitatively**:
  effort ∝ Time⁻⁴ (a 15 % schedule compression roughly doubles effort), which is why aggressive
  schedules are disproportionately expensive. No `^3` / `^(4/3)` enters the awk-math surface.
- **Disclosed limitation:** PP is an organizational, back-calibrated constant a snapshot cannot
  measure; the super-cubic-in-size form would reward LOC-stuffing and diverge on large/verbose
  codebases — which is exactly why no number is emitted here.
- **Verify:** the report cites Putnam SLIM/Rayleigh as a second family and states the Time⁻⁴
  trade-off qualitatively; **no SLIM number is printed and no SLIM ensemble row appears.**
- **Files:** `SKILL.md` (Methodology note + ensemble narrative), `README.md`.

---

### P2-10 🟡 Use-Case Points + SEER-SEM note — gated cross-check *(S2)*

- **UCP** `= (UAW + UUCW) × TCF × ECF`, `Effort = UCP × PF`:
  - **UAW** (actors): simple/API=1, average/external-system=2, complex/GUI=3 — from distinct
    external clients (HTTP/gRPC/broker/DB/SDK) and front-end frameworks.
  - **UUCW**: use-cases ≈ route/handler endpoints grouped by controller/resource; transactions per
    use-case ≈ DB read/write + queue ops in scope → 1–3 → 5, 4–7 → 10, ≥8 → 15.
  - **TCF** `= 0.6 + 0.01·Σ(w·r)` over the 13 technical factors (weights T1=2, T2–5=1, T6/7=0.5,
    T8=2, T9–13=1), ratings driven from the 8 complexity scores (clamped 0–5).
  - **ECF** `= 1.4 − 0.03·Σ(w·r)` — team factors are **unobservable** → default all ratings to 3
    → ECF ≈ 0.995, disclosed.
  - **PF** = Schneider&Winters rule (count of low-E1..E6 / high-E7,E8 → 20 / 28 / 36 h/UCP); default
    Karner **20 h/UCP**.
- **Gate:** if no use-case signal (endpoints/handlers ≈ 0), UCP renders **N/A** (CLI commands count
  as use-cases — the calibration VM's **6 argparse subcommands** clear `USECASE_FLOOR=3`, giving it a
  *valid* UCP path, unlike FP). With 6 use-cases (each ≤ 3 transactions → simple) the **UUCW = 6 × 5
  = 30** (simple tier), before TCF/ECF.
- **SEER-SEM:** **citation only** (no compute) — note SEER's vendor accuracy claim (~within 30 %
  ~62 % of the time, Galorath & Evans 2006; independents lower, PRED(30) ≈ 49 %) as evidence that
  *any* such number is imprecise.
- **Disclosed limitation:** "use case ≠ endpoint" is the dominant variance; transactions are
  spec-level (don't exist in code); PF (15–36) swings effort 2.4× and is an unmeasurable org
  constant; UCP MMRE often 0.3–1.0+.
- **Verify:** calibration VM → UCP computed from its 6 argparse subcommands (not N/A); a web app →
  UCP from routes; ECF defaulting disclosed; determinism.
- **Files:** `SKILL.md` (Phase 2.5/ensemble), `README.md`.

---

### P2-11 🟠 Git-history effort + AI provenance — the measured anchor *(S4)*

- **Measured effort (git-hours algorithm):** per author, sorted commit epochs; for consecutive
  pairs `diffMin = (t[i+1]−t[i])/60`: if `diffMin < 120` add `diffMin/60` h, else add **2 h**
  (first-commit-of-session charge); round per author; sum → **measured person-hours**. Tie-break
  equal timestamps by commit hash for determinism. Also offer the **git2effort** PM form
  (`round(commits/75 × 6, 2)` capped at 6 per author per 6-month period) as a cross-check; convert
  PM→hours via the explicit 152 h/month.
- **Provenance:** `ai_fraction = commits_with_AI_trailer / total_commits`, AI trailer =
  `Co-Authored-By:` matching `claude|copilot|gpt|gemini|cursor|codex|aider|devin|noreply@anthropic`.
  Cite the **2025 Sonar State of Code ~42 %** self-reported AI-assisted figure as context (used as
  a fallback flag only, never as a computed number). When `ai_fraction` is high, **flag the
  from-scratch-human baseline as increasingly fictional**, directly serving the P2-14 framing.
- **Report:** a **"Measured vs Parametric"** block: "git-reconstructed actual effort ≈ N h
  (measured, from M commits over the repo's life) vs parametric from-scratch ≈ P50 h. AI-assisted
  share ≈ X %." Both numbers, side by side.
- **GATE (E2):** require `commits ≥ MIN_COMMITS` (e.g. ≥ 10) and a non-trivial age; else
  **"N/A — insufficient git history for effort reconstruction"** (this repo's 3 commits → N/A;
  shallow clones → N/A). Never in the dollar headline (same discipline as IE).
- **Disclosed limitation (prominent):** absolute accuracy is **unvalidated** (no MMRE/PRED);
  commits ≠ person-months (squash/micro-commit/bot bias); the 120/120 constants are arbitrary and
  ignore reading/design/meeting time; AI trailers are self-reported/forgeable → a **lower bound**;
  best for **relative** comparison only. The git2effort threshold=75 calibration is not reproducible
  (borrow the default, disclose).
- **Verify:** (a) this repo (3 commits) → "N/A — insufficient history", `ai_fraction` still
  computed (2/3) and disclosed. (b) a repo with ≥ 10 commits → plausible hours; re-run identical
  (determinism via hash tie-break). (c) measured-vs-parametric never feeds the headline/cost tables.
- **Files:** `SKILL.md` (extend Phase 1b usage + new report block + Methodology), `README.md`.

---

### P2-12 🟡 Verify & pin the METR/DORA/GitClear figures *(S7; mostly present)*

- **Pin exact figures** in the AI Speed Comparison caveat (replace any soft wording):
  **METR** RCT arXiv:2507.09089 (2025-07-10), 16 experienced OSS devs, 246 tasks on mature repos
  (Cursor + Claude 3.5/3.7) → **+19 % completion time (≈19 % slower)** while they *felt* ~20 %
  faster (point estimate; **no CI in the abstract** — state as such). **DORA 2024** (correlational,
  ~3,000): per +25 % AI adoption, throughput **−1.5 %**, delivery stability **−7.2 %**, docs
  **+7.5 %** — explicitly label **correlational, with countervailing positives** (no cherry-pick).
  **GitClear 2025** (211M LOC, 2020–2024): refactored lines **25 %→<10 %**, copy/paste clones
  **8.3 %→12.3 %**. **Copilot lab** arXiv:2302.06590: **+55 %** on an *isolated greenfield* task
  (95 % CI 21–89 %) — non-generalizing.
- **Repo-specific tie-in:** classify the analyzed repo as METR-regime (mature: routes/entities/age
  present) vs Copilot-regime (greenfield) and cite the matching study; compare the self-reported AI
  ratio against the measured-vs-parametric anchor (S4).
- **Disclosed limitation:** these figures are from *other* codebases — they contextualize, they are
  **not** measured here; the poor-accuracy warning attaches to the *parametric estimate*, not to
  these well-run studies. Update the Methodology sources line (use 211M, not 153M; add arXiv IDs).
- **Verify:** every figure matches the cards/sources; "correlational" appears on the DORA line;
  METR shown as a point (no fabricated CI).
- **Files:** `SKILL.md` (AI Speed Comparison + sources line), `README.md`.

---

### P2-13 🟡 #NoEstimates throughput Monte-Carlo — descriptive cadence side-metric *(S4)*

- **Method (descriptive only — A9):** emit **no** completion-time percentiles, **no** bootstrap, **no
  PRNG**, and **no invented backlog `N`** (a finished repo has no backlog). Build per-week commit
  counts (`git log --date=format:'%Y-%U'`), fill zero-commit weeks between first/last commit, and
  report only the **measured fact**: *"demonstrated cadence ≈ X commits/week over its M-week active
  life."* This **removes the second PRNG entirely** (only the MC band remains random).
- **Output is a descriptive cadence statistic, NEVER folded into the dollar headline.** Shown only in
  the measured-vs-parametric block.
- **GATE:** git-root + `MIN_COMMITS` + `MIN_NONZERO_WEEKS` (= 6); rendered 1-sig-fig under OOM; flag
  **low-confidence if < 6 non-zero weeks**.
- **Disclosed limitation (prominent):** a finished repo has no backlog and no story-completion data,
  so **no forecast is attempted**; throughput is **proxied** by commits (≠ stories). Applied to a
  *completed* repo this **re-describes historical cadence**, it does not forecast reproduction cost;
  gameable by commit padding/squashing (PR cadence mitigates). No published MMRE/PRED for the proxy.
- **Verify:** this repo (3 commits / few weeks) → low-confidence flag or N/A; a repo with steady
  cadence → a single descriptive commits/week statistic (no percentiles, no PRNG); never appears in
  cost tables.
- **Files:** `SKILL.md` (measured-vs-parametric block), `README.md`.

---

### P2-7 🟠 Reference-class forecasting via an optional local corpus *(S5)*

- **Corpus mechanism** (see §1a below for the spec): an **opt-in**, plain user-editable JSONL
  **outside the analyzed repo** appended via `>>`. Each prior run contributes one record; over time it
  becomes the reference class. **WRITE requires `COST_ESTIMATE_CORPUS` set** (default-file existence
  enables **READ only** — A7).
- **RCF:** when the corpus holds ≥ `MIN_CLASS` (default 5) records in a **similar class** (size band
  × stack × complexity, by fixed weighted-L1 similarity), compute `overrun_i = actual_i / estimated_i`
  over the class, take the empirical quantile (nearest-rank `idx=ceil(p·n)`), and report an
  **outside-view** central + uplift: `Adjusted = inside_view × Quantile_{1−r}(overrun)`, default
  `r = 0.20 → P80`. Else: **"N/A — outside view needs ≥ N comparable past analyses (have M)."**
- **Determinism:** empirical quantiles need no PRNG; similarity ties broken by record id sort.
- **Disclosed limitation (prominent):** **RCF's premise — a distribution of *actual* outcomes — does
  not exist in a code snapshot.** Without back-filled actuals the corpus stores only the skill's own
  *estimates* (and, when available, the git-measured effort as a proxy actual), so out of the box
  this is "RCF in name only" / inside-view-on-analogies until real actuals accrue. Cold-start n = 0;
  transport-sector uplift tables have **no software basis** (the corpus is the only valid table).
  **Inline trust disclosure (A8):** the corpus is a **plain user-editable JSONL with no
  tamper-resistance** — RCF/Bayesian outputs are only as trustworthy as that file; the report
  discloses the matched **class size + provenance** alongside any number. RCF uses **integer
  nearest-rank quantiles (no transcendentals) → it is NOT gated by the awk-math probe.**
- **Verify:** n = 0 corpus → N/A, behavior identical to today; a seeded test corpus of ≥ 5 similar
  records → an uplift applied with the class size and percentile disclosed; corpus path is outside
  the repo; nothing written unless opt-in.
- **Files:** `SKILL.md` (Phase 3.95 RCF + corpus read/write + report + Methodology), `README.md`,
  §1a corpus spec.

---

### P2-8 🟠 Bayesian calibration of productivity to local data *(S5)*

- **Scalar log-A update** (the only automatable special case; full Chulani–Boehm–Steece matrix needs
  a multi-project design matrix): treat log-productivity as normal-normal conjugate on the log scale.
  Prior **μ0 = ln(2.94) = 1.07841**, **σ0 = ln(1.5) = 0.40546** (τ0 = 6.0833); per-datum log-noise
  **σ = ln(1.7) = 0.53063** (git-proxy datum gets **σ_git = ln(2.5)**, larger). For each local datum
  `θ_i = ln( PM_i / (KLOC_i^E · EAF_i) )`. Posterior `τ_post = τ0 + Σ 1/σ_i²`,
  `μ_post = (τ0·μ0 + Σ θ_i/σ_i²)/τ_post`, `Â = exp(μ_post)`. Predictive percentiles
  `PM_q = exp(μ_post + ln(KLOC^E·EAF) + z_q·√(σ_post² + σ²))` — **standardized to P10/P50/P80/P90**
  with z = (−1.2816, 0, +0.8416, +1.2816) (A8/A11).
- **Data sources:** (a) a **genuine human actual via the distinct flagged input
  `COST_ESTIMATE_ACTUAL_HOURS`** (PM = h/152) — the only headline-moving datum. **`$ARGUMENTS`
  (AI-build hours) is AI-only and NEVER a Bayesian datum** (feeding it is the C10 category error);
  (b) corpus records' git-measured effort is **excluded from the headline-moving posterior** (H4),
  shown only as an informational "alternate posterior (git-proxy; not in headline)". **n = 0 (no
  genuine human actual) → posterior = prior → Â = 2.94, skill unchanged.**
- **Determinism:** **closed-form lognormal, no PRNG** (A8 — the predictive percentiles are computed
  from the closed-form z-grid, not sampled).
- **Containment (single-datum cap, A8):** clamp `|μ_post − μ0| ≤ 0.5·σ0` (= 0.2027 in log →
  **`Â ∈ [2.40, 3.60]`**) until **≥ 2 corroborating genuine actuals** exist, so one tiny
  self-reported "actual hours" can't pull `Â` arbitrarily.
- **Log→linear mapping when the headline moves (A11 #4):** when a genuine actual moves the headline,
  the widened **productivity** triangular endpoints are `m_prod_O/P = exp(±z·√(σ_post² + σ²))`
  computed **once outside the MC loop** (and `Â = exp(μ_post)` also once), so the per-iteration draw
  stays **linear + sqrt-only**.
- **Disclosed limitation (prominent):** a snapshot is at best **one noisy (size, effort) pair**, so
  only the scalar log-A update is honest and it **returns the prior unchanged without a real
  actual**; git-effort is a **weak** likelihood (commits ≠ person-months → large σ_git); σ0/σ are
  engineering choices, not published; `exp(μ_post)` is the **median**, not the mean (Jensen gap).
  Don't show 3-sig-fig posteriors below 2 KLOC.
- **Verify:** no data → `Â = 2.94`, headline identical to today; **`$ARGUMENTS '200 hours'` leaves
  `Â = 2.94`** (AI hours are not a Bayesian datum — C10); the **human-actual shift is tested via
  `COST_ESTIMATE_ACTUAL_HOURS`** on a known KLOC → `Â` shifts toward the implied productivity with
  prior/data/posterior all printed, but the **single-datum cap holds `Â ∈ [2.40, 3.60]`** until ≥ 2
  corroborating actuals; a tiny bogus "1 hour" actual is capped (Â ≥ 2.40); determinism.
- **Files:** `SKILL.md` (Phase 3.95 Bayesian + Methodology), `README.md`, §1a corpus spec.

---

### §1a — The optional local calibration corpus (shared mechanism for P2-7 / P2-8)

- **Path:** `${COST_ESTIMATE_CORPUS:-$HOME/.cost-estimate/corpus.jsonl}`. **Opt-in write (A7):** a
  record is appended **only if `COST_ESTIMATE_CORPUS` is set** (default-file existence enables **READ
  only**) — so default runs create nothing and behave exactly as today (privacy + zero-surprise).
- **Record (one JSON line):** `{"date","repo","kloc","fp_structural","stack","complexity_avg",
  "estimate_p50_hours","git_measured_hours"|null,"actual_hours"|null}`. `actual_hours` is only ever
  set from an explicit user-provided actual; the skill never invents it.
- **Append mechanism:** write via `>>` to the file after the report is produced. Created with
  `mkdir -p` on the parent (outside the analyzed repo — Constraint 2 preserved). **No
  tamper-resistance is claimed** — this is a plain user-editable JSONL (per A8 the prior "append-only
  / never rewrite / RCF integrity" claims are dropped; a user can edit it freely).
- **Read:** RCF/Bayesian parse the JSONL with `jq` when available, else a tolerant awk reader; a
  malformed/older record is skipped, not fatal.
- **Disclosed limitation:** the corpus accumulates **estimates** (and git-proxy actuals); it becomes
  a genuine reference class only once real `actual_hours` are back-filled. Because it is plain
  user-editable JSONL, **RCF/Bayesian are only as trustworthy as the corpus** — the report discloses
  class size + provenance. Documented in README.
- **Verify:** unset env + no file → no write, RCF/Bayesian both N/A; set env → one well-formed JSON
  line appended outside the repo; corrupt line → skipped; second run sees the first run's record.

---

## §2 — Test plan

Run after implementation, before regenerating samples. The two shipped fixtures are the primary
oracles; their archetypes are deliberately opposite.

1. **Static audit.** Re-grep `SKILL.md` for the removed signature: the live `× 0.5 / × 2.0` headline
   band text is gone from the headline path (the `× 0.6 / × 1.6` string is P1 historical-narrative —
   do **not** assert its removal — A10); "Headline Valuation" no longer stands alone (no false
   "P0-14 SNAP v2.4" claim — it never existed, R1-C11). Confirm no new `srand()` without an
   explicit numeric seed, no `$RANDOM`, no `date +%s`-seeded randomness, no network/install/test/run
   commands, no writes inside the analyzed repo (only `$OUT_DIR` and the opt-in corpus path).
2. **Determinism (the load-bearing test).** Execute Phase 2.5 + 3.9 + 3.95 in isolation **twice** on
   each fixture → **byte-identical MC band percentiles (P10/P50/P80/P90)** — the single randomized
   output (A1). FP/COSMIC/UCP (integer counting), RCF (integer quantiles), Bayesian (closed-form)
   are deterministic by construction with no PRNG; SLIM is citation-only. Any divergence in the MC
   band = a seeding/PRNG bug (fail).
3. **Calibration VM (`examples/calibration-codebase/`, 2.0 KLOC parser/VM — the non-web oracle).**
   Assert: structural IFPUG FP and COSMIC render **N/A — not transaction-oriented** (E1), **not $0**;
   UCP **is** computed (6 argparse subcommands ≥ USECASE_FLOOR=3 give a valid use-case path); **SLIM
   is citation-only** (no number, Time⁻⁴ stated qualitatively); **the deterministic COCOMO point
   headline is essentially unchanged from the shipped ~$93K** (the redesign must not move a
   domain-fair result); **FP/COSMIC N/A on the VM**; git-effort **N/A** (the fixture's `.git` is the
   parent's — repo-root guard, A6); ensemble shows COCOMO vs UCP with the gates.
4. **This repo (self-referential, ~29 shell LOC + prose — the prose-heavy oracle).** Assert: code
   headline stays tiny (~$500, OUT_OF_DOMAIN, 1 sig fig); under OOM the MC band **suppresses to a
   single decade bucket** (A9), not four separately-rounded percentiles; git-effort **N/A** (3 commits
   < MIN_COMMITS) but `ai_fraction` computed (2/3) and disclosed; IE channel unchanged and still
   separate; FP/COSMIC N/A (2 shell files, ~0 transaction signal).
5. **Synthetic transaction app.** Build a throwaway temp repo with ~5 mutating + 5 read routes and
   ~3 ORM models → structural UFP nonzero with EI/EQ/ILF matching a hand count; COSMIC CFP nonzero;
   UCP from routes; FP→effort lands within the ensemble band. **Routes-only un-gate assertion (A11
   #2):** a routes-only service (ILF = 0, **5 routes**) **un-gates** (single kind clears the ≥5
   single-kind floor) — structural FP is computed, NOT wrongly gated to N/A. (Temp dir, removed
   after.)
6. **Monte-Carlo invariants.** Assert **deterministic-point continuity** (published headline = pre-P2
   point ±0) and **band monotonicity** `P10 ≤ P50 ≤ P80 ≤ P90` with `P10 ≥ 0.5×point` and
   `P90 ≤ 2.0×point`, and that **P50 sits ≈×1.0–1.3 above the point** (expected right-skew, not a
   continuity failure); no NaN/inf/divide-by-zero on degenerate inputs (KLOC→0, single language,
   P==O).
7. **Corpus lifecycle.** (a) unset env, no file → zero writes, RCF + Bayesian both N/A, output ==
   today. (b) `COST_ESTIMATE_CORPUS=$tmp/corpus.jsonl` → exactly one well-formed JSON line appended
   outside the repo; run twice → two records; RCF still N/A (< MIN_CLASS). (c) seed a 6-record
   similar-class corpus → RCF uplift applied with class size + percentile disclosed; Bayesian Â
   shifts and prints prior/data/posterior. (d) corrupt line → skipped, not fatal.
8. **Bayesian data paths.** No data → `Â = 2.94`, headline identical. **`$ARGUMENTS '200 hours'`
   leaves `Â = 2.94`** (AI hours are never a Bayesian datum — C10). The **human-actual shift is tested
   via `COST_ESTIMATE_ACTUAL_HOURS`** → Â shifts toward implied productivity, with the single-datum
   cap holding `Â ∈ [2.40, 3.60]` until ≥ 2 corroborating actuals. Bogus `"1 hour"` → cap keeps
   `Â ≥ 2.40`.
9. **Adversarial / gameability.** (a) LOC-stuffing: duplicating a source file ×4 raises COCOMO
   ~KLOC^E but **moves no cross-check into the headline** (A2 — the band ignores the ensemble; SLIM is
   citation-only and emits no number). (b) route-padding: add 50 no-op GET stubs → structural FP
   rises but the **deterministic-point headline barely moves** because FP is a non-load-bearing
   cross-check, not the anchor. (c) commit-padding: split
   one change into 30 commits → git-effort inflates but is gated/contextual and never in the headline.
   (d) fake `Co-Authored-By` trailers → ai_fraction is disclosed as a self-reported lower bound.
10. **Error resilience & honesty.** No git, no jq, no cloc, timeouts → graceful N/A per item, never an
    abort (except EMPTY_REPO). Every new estimator prints its **Disclosed limitation**; no new metric
    is shown to more sig figs than OUT_OF_DOMAIN allows.
11. **Regenerate both samples** from a frozen copy (A17 temp-dir method) and eyeball for internal
    consistency (P50 between P10 and P90; ensemble gates correct; measured-vs-parametric present only
    where git history qualifies). Remove the stale claim in any doc that "function points = LOC/ratio".

---

## §3 — Risks / open decisions (for red-team)

- **R1 — FP: replace vs alongside (the deferred fork).** **Resolved → alongside, archetype-gated**,
  on evidence E1 (structural FP/COSMIC collapse to 0 on the 2-KLOC calibration VM; making them the
  anchor would re-introduce a worse web bias and zero-cost a complex interpreter). LOC stays the
  universal anchor; FP/COSMIC/UCP are gated cross-checks; SLIM is demoted to **citation-only** (no
  computed number, no ensemble row, cannot widen the band — A3). *Red-team to confirm or break this.*
- **R2 — Does the redesign move the domain-fair headline?** It must not. The calibration VM's ~$93K
  and the self-repo's ~$500 should be **unchanged — deterministic-point continuity** (the published
  headline = the pre-P2 COCOMO point ±0; A2). If the ensemble or MC shifts them materially, the
  design has leaked a cross-check into the anchor — fail.
- **R3 — Determinism surface.** **One PRNG (the MC band)** + one sort-order dependence (git
  tie-break) — #NoEstimates is descriptive (no PRNG, A9) and Bayesian is closed-form (no PRNG, A8).
  The PRNG seeds from static find-derived repo signals and uses overflow-safe integer arithmetic
  (Schrage for Park–Miller). Risk: cross-awk (mawk vs gawk vs BWK) float drift in transcendentals →
  mitigated by the linear design + integer-dollar grid (`printf "%.0f" | LC_ALL=C sort -n`).
- **R4 — Honesty vs feature-count.** Adding 6 estimators risks *implying* more precision, the
  opposite of P2's intent. Mitigation: every item is gated + carries a Disclosed limitation, the
  headline stays a **single labeled cost-approach deterministic point**, and the band is explicitly
  "model uncertainty, not elicited risk." Red-team should check the report doesn't read as false rigor.
- **R5 — Corpus privacy/footprint.** Opt-in write only (`COST_ESTIMATE_CORPUS` set — A7), outside the
  repo; contains repo basename + metrics. **No integrity/tamper-resistance is claimed** — it is a
  plain user-editable JSONL (the "append-only integrity" mitigation is dropped, A8); trust is
  disclosed inline (class size + provenance). Risk: silent accumulation or PII in `repo`/`stack`.
  Mitigation: document it, opt-in gate, store only basename, never file contents.
- **R6 — Skill length & maintainability.** SKILL.md ~doubles. Risk: shell-state-doesn't-persist bugs
  across the many new Bash blocks (the recurring P0/P1 failure mode). Mitigation: each new phase is a
  single consolidated block that re-inlines `SOURCE_EXT_RE`/excludes and substitutes prior-phase
  scalars at the top, exactly like Step 3.6b.
- **R7 — SLIM cubic gameability (called out in P2-9).** Effort ∝ Size³. **Resolved: SLIM demoted to
  citation-only per A3** (cubic-in-size hazard avoided — no SLIM number is ever computed, so it cannot
  leak into the headline or widen the band).
- **R8 — Self-referential regeneration drift.** Editing SKILL.md changes the self-sample's numbers
  *and* its IE tier scoring (more methodology prose → larger T4 credit). Regenerate from frozen copy;
  expect the IE channel to grow — that's correct and stays out of the headline.

---

## §4+ — Red-team rounds

*(Amendments A1, A2, … are appended here by the adversarial review; each is AUTHORITATIVE and
supersedes conflicting body text above. Implementation proceeds only against the converged
contract = body + all amendments, once a round surfaces no Medium+ issues.)*

### Red-team Round 1 — Amendments (closes 11 critical + 11 high + 10 medium + 4 low)

Round 1 ran 7 adversarial lenses; three load-bearing claims were independently reproduced on this
box: (i) `git rev-parse --show-toplevel` from `examples/calibration-codebase/` returns the **parent**
repo (the fixture has no own `.git`, so parent history leaks); (ii) `busybox awk` aborts with "Math
support is not compiled in"; (iii) `LC_ALL=C sort -n` orders `1e+06`/`5e+05` **below** `999999`;
(iv) the VM has **6** `add_parser` subcommands (not 14) and bare-verb greps match `DISPATCH` (→ `PATCH`).
The amendments below are the converged contract. The overarching move: **demote the over-reaching
estimators to honest forms** (SLIM → citation-only; #NoEstimates → descriptive cadence, no forecast;
SNAP → qualitative checklist, no computed total; RCF → suppressed without real actuals) and **shrink
the determinism surface to a single seeded PRNG behind a math-capability gate**.

#### A1 — One deterministic numeric kernel *(closes C2, C3, C4, C5, H3, M8, M9, M10; low: seed entropy)*

All runtime numerics that need randomness or transcendentals obey ONE spec:

- **Single PRNG = Park–Miller minimal-standard + Schrage**: `a=16807, m=2147483647, q=127773,
  r=2836` (`hi=int(s/q); lo=s%q; s=a*lo−r*hi; if(s<=0)s+=m`). Intermediates ≤ 2.15e9 < 2^53 → exact
  in IEEE doubles. **No glibc LCG anywhere** (it overflows 2^53 — C2). `U=s/m`. After A9 there is at
  most **one** PRNG site (the MC band); if a second is ever needed it uses this construction with a
  distinct integer salt.
- **Seed = pure function of find-derived integer, tool-invariant signals**, computed inside awk
  (never bash `$(())` for the > 2^31 mix, never time/`$RANDOM`/`srand()`-no-arg):
  `SEED = ((CODE_FILE_COUNT*1000003 + TOTAL_FILE_COUNT*10007 + COMPLEXITY_SUM*101) % 2147483647)`,
  forced ≥ 1. **`SOURCE_CODE_LOC` is dropped from the seed** (A11 #1): it is **not** tool-invariant —
  cloc=2014 vs wc-raw=2736 on the VM, so a host without cloc would seed differently. All three
  retained signals are **find-derived integer counts** (CODE_FILE_COUNT, TOTAL_FILE_COUNT,
  COMPLEXITY_SUM), invariant to cloc-vs-wc. **Multipliers are kept small on purpose** so every
  product stays < 2^53 even for a huge repo (`2e6 files × 1000003 ≈ 2e12 ≪ 9.0e15`); large
  2^31-scale multipliers would re-introduce the very overflow C2 forbids. The mix is reduced `% m`
  once after summing (the sum stays < 2^53). **`COMPLEXITY_SUM` is hereby defined** = the integer sum
  of the 8 factor scores (range 8–40) — *not* the rounded mean. **Never seed from float KLOC or
  SOURCE_CODE_LOC** (cloc-vs-wc divergence makes them machine-dependent — H3 / A11 #1).
  Forge-resistance is explicitly **not** a goal (the seed is derivable from public signals;
  disclosed). The seed is printed in the report's environment block.
- **awk-math capability probe (Phase 0) gates ONLY the transcendental paths** (A11): `AWK_MATH=$(awk
  'BEGIN{print (sqrt(4)==2)?"yes":"no"}' 2>/dev/null)`; if the call errors or ≠ "yes" set
  `AWK_MATH=no`. When `AWK_MATH=no` (BusyBox/Alpine), the **MC band (triangular `sqrt`) and the
  closed-form Bayesian (`exp`/`log`) render "N/A — awk math unavailable on this host"** and the
  headline falls back to the **deterministic MMRE-justified `×0.5 / ×2.0` band** (model-computed,
  labeled "rule-of-thumb band; Monte-Carlo unavailable on this host"). **RCF is NOT gated by
  awk-math** — it uses integer nearest-rank quantiles with no transcendentals, so it still runs when
  `AWK_MATH=no`. No block ever aborts (Execution Rule 11).
- **Linear-multiplier MC (no per-iteration `KLOC^E`)** — C4: precompute the deterministic point cost
  `C0` once (model/awk). Each of `N=10000` iterations multiplies `C0` by **linear** triangular draws
  `m_size × m_prod` (rate is NOT sampled — A2); the only transcendental is the triangular `sqrt`.
  **Explicit multiplier three-points (A11):** `m_size` O=`1−genfrac−0.10` / M=`1` / P=`1.30`;
  `m_prod` O=`0.5` / M=`1` / P=`2.0`. `genfrac` per A11 #5 = `(GENERATED_TOTAL_LOC + vendored_LOC) /
  raw_source_LOC_before_exclusions`, clamped `[0,0.5]`.
- **Triangular inverse-CDF only** (drop Beta-PERT as a runtime path — M8; PERT is citation-only):
  `Fc=(M−O)/(P−O)`; `U<Fc → X=O+sqrt(U·(P−O)·(M−O))`, else `X=P−sqrt((1−U)·(P−O)·(P−M))`.
- **Integer-dollar grid before ranking** — C5: emit each sample via `printf "%.0f"` (no scientific
  notation possible), then `LC_ALL=C sort -n` — **the single mandated ranking method** (A11 #6). The
  in-awk Lomuto quicksort option is **dropped** (O(n²) on the heavy-duplicate integer-dollar grid);
  `asort` is gawk-only and also not used. Set `CONVFMT=OFMT="%.6f"` at BEGIN. Rounding to integer
  dollars also absorbs sub-ULP `sqrt` differences so ranks are stable across awk/libm.
- **Integer-guarded percentile index** (no `ceil` on a float product — M9): `idx=int(p*n);
  if(idx<p*n)idx++; if(idx<1)idx=1; if(idx>n)idx=n;` over **1-indexed** arrays. Same rule for every
  percentile site. Pin `LC_ALL=C` on every sort.
- **Degenerate/positivity guards** (M10): clamp the optimistic size endpoint
  `O=max(K·(1−min(genfrac,0.5)−0.10), 0.05·K)`; clamp every sampled value to a positive floor before
  use; guard `P==O`, `P==M`, `M==O` (→ constant). No `NaN`/`-nan` can reach the sort.
- **Drop the "immune to transcendental drift" wording** from §0 S3 / P2-6; the guarantee now comes
  from the linear design + integer-dollar grid, not from the sampler being closed-form.

#### A2 — The headline never moves without new data; MC is band-only; rate has one home *(closes C1, H6; enforces R2)*

- **Headline = the deterministic COCOMO point estimate** (identical to today's number). The Monte-Carlo
  layer produces **only the asymmetric P10–P90 band** that replaces the invented `×0.5 / ×2.0`. There
  is **no "headline = P50."** P50 is shown as a secondary band landmark with the note *"P50 > point
  reflects right-skew = overrun risk."* This makes R2 / §2-test-6 / the old Verify(c) consistent.
- **Rate lives in exactly one place:** the existing Phase 4 four-profile rate-sensitivity table.
  **Rate is NOT sampled in the MC** (removes the double-count H6); the MC varies only size +
  productivity at the fixed `$125` mid rate, so the band is "model + size uncertainty," and the
  Phase-4 table is the orthogonal rate axis, exactly as the current skill separates them.
- **The ensemble spread does NOT numerically widen the published band.** The band depends solely on
  the size + productivity three-points (justified by P2-5's MMRE ≈ 1.0). Ensemble agreement/
  disagreement is a **separate qualitative note**, never folded into P10–P90. *(Supersedes the S3
  clause "widened by the ensemble spread" and the P2-6 size-driver "widened by the ensemble spread".)*
- **Executed §2 assertion (new):** on BOTH shipped fixtures the published headline equals the pre-P2
  deterministic point (±0 by construction); the band is monotone with **`P10 ≥ 0.5×point` and
  `P90 ≤ 2.0×point`** (the band lies INSIDE the rule-of-thumb extremes), **scoped to the in-domain
  calibration VM**; for the **OOM self-repo** assert the **suppressed decade bucket is byte-identical
  across the two A17 regenerations**. (The literal `×0.5 / ×2.0` band is reserved for the
  `AWK_MATH=no` fallback only.) Fail the build otherwise.

#### A3 — Putnam SLIM demoted to citation-only *(closes C6, C7; sanctioned by R7)*

SLIM cannot produce a defensible number from a snapshot: PP is unmeasurable (textbook 2000/8000/11000
guess spans orders of magnitude), the `·B` form silently scales effort 2.5–6× (a P0-14-style
borrowed-constant failure), SLOC-vs-KSLOC is a unit hazard, effort ∝ Size³ is a cubic gameability
lever, and `Time` from a same-day git span makes effort ∝ Time⁻⁴ explode/`NaN`. **Therefore P2-9 is
implemented as citation-only:** cite Putnam SLIM / the Rayleigh model as a second parametric *family*
and explain the schedule↔effort trade-off (`effort ∝ Time⁻⁴`) **qualitatively**, with **no computed
SLIM number and no ensemble row.** This removes C6/C7 entirely and drops `^3` / `^(4/3)` from the
awk-math surface. *(Supersedes all compute/Verify/ensemble-member text in P2-9 and §0 S2's SLIM row.)*

#### A4 — Ensemble honesty: no "convergence = confidence"; FP value unchanged *(closes H6-part, M5; enforces R4)*

- The independent ensemble members are now **COCOMO (anchor) + structural IFPUG-FP + COSMIC + UCP
  (each archetype-gated)** only. Backfired-FP is a **redundant LOC restatement**, labeled as such, and
  is **excluded from any convergence narrative**. On a non-transactional codebase (the VM) FP/COSMIC
  are N/A, so the report states plainly: *"the ensemble offers at most one independent cross-check
  (UCP) here; the headline rests on COCOMO alone."* No "convergence → confidence" claim anywhere.
- **The report's "Estimated Function Points" keeps the existing Jones Step-3.7 table** (continuity —
  the self-sample's FP must not change silently, M5). QSM gearing is mentioned only as a methodology
  footnote for the backfired row. FP is marked **non-load-bearing** (feeds nothing into the headline).
  *(Supersedes P2-1's "use QSM gearing instead of the current Jones table for this row.")*

#### A5 — Anchored transaction greps + locked gate constants *(closes H2, H1, H9, H10)*

- **Structural greps must be framework-anchored, word-bounded, case-sensitive, and web/app-scoped**
  — never bare verbs. EI/EQ/EO match route decorators/registrations only
  (`@(app|router)\.(post|put|patch|delete)\b`, `@(Post|Put|Patch|Delete)Mapping`, Rails
  `\b(create|update|destroy)\b` inside `*_controller.rb`, etc.), explicitly excluding `_?DISPATCH`;
  ILF matches ORM-model/`CREATE TABLE`/migration contexts; R/W verbs (P2-2) must **co-occur with a
  data-layer symbol on the same line**; per-file occurrences are capped. **Un-gate only when
  `transaction_signal ≥ FP_FLOOR` AND (≥ 2 distinct artifact kinds are present — e.g. a route AND an
  ILF — OR a single kind clears the higher single-kind floor of ≥ 5, e.g. ≥ 5 routes)** (A11 #2), so
  a routes-only API (ILF = 0, 5 routes) is **not** wrongly gated out; never un-gate on a single fuzzy hit.
- **Gate constants are locked, named §0 literals** (referenced by name, never redefined per-site):
  `FP_FLOOR=3` (transaction_signal = EI+EQ+EO+ILF), `MOVEMENT_FLOOR=3` (CFP), `USECASE_FLOOR=3` (UCP),
  `MIN_COMMITS=10`, `MIN_AGE_DAYS=14`, `MIN_CLASS=5`, `MIN_NONZERO_WEEKS=6`. `OUT_OF_DOMAIN` is strict
  `Effective KLOC < 2.0`.
- **H1 correction:** the calibration VM has **6** `add_parser` subcommands (not "14"). Fix the E1
  table, S2, P2-10, and §2 tests 3/4 to say "6 argparse subcommands"; `6 ≥ USECASE_FLOOR` so the VM
  still has a valid UCP path. UUCW tier recomputed from 6 use-cases.
- **H10:** the VM is 2.01 KLOC (0.5 % above the OOM cliff). Phase 2.5 is **purely additive and must
  not change Effective KLOC**; the generated-code/wc paths are untouched. Add a §2 assertion that the
  VM remains `≥ 2.0 KLOC` (not OUT_OF_DOMAIN) — **conditioned on `CLOC_AVAILABLE=yes`** (A11 #3): on
  the wc fallback the VM is `2736 × 0.7 = 1915 → 1.915 KLOC → OUT_OF_DOMAIN`, so the ≥ 2.0 KLOC
  assertion holds only on the cloc path; note this straddle explicitly.
- **Verify:** run the literal anchored patterns against the shipped VM → **0** per FP/COSMIC category
  (so structural FP/COSMIC render N/A, not $0); padding CLI subcommands or verb lines does not move
  the headline (guaranteed by A2 — band ignores the ensemble) — assert it anyway.

#### A6 — Git phase: repo-root guard, explicit epoch read, deterministic sort *(closes C8, H7; part of C9)*

- **Repo-root guard:** the git phase first checks `[ "$(git rev-parse --show-toplevel 2>/dev/null)" =
  "$(pwd)" ]`; if not (a parent-owned `.git`, as the calibration fixture proves — C8), treat as
  **NO_GIT** and suppress git-effort, #NoEstimates, and `ai_fraction` (no mis-attribution of parent
  commits). §2 test 3 asserts the gate fires for **this** reason on the VM.
- **Explicit read added to Phase 1b** (S4 reworded from "data already collected" to "one added git
  log read"): `git log --no-merges --format='%at|%an|%H' <rev>` piped through
  `LC_ALL=C sort -t'|' -k1,1n -k2,2 -k3,3` (numeric epoch primary — mandatory because `git log`
  emits graph order, not time order — then author, then hash for exact-tie determinism), feeding the
  awk gap pass in one block.
- Specify the charge precisely: **each session (first commit, and each commit > 120 min after the
  prior) adds 2 h; within-session gaps < 120 min add `gap/60` h**; per-author rounding; summed. The
  git2effort cap is "**max 6 PM within any rolling 6-month window**," with a worked example.

#### A7 — A17 regeneration determinism + corpus opt-in tightened *(closes C9, M6)*

- **A17 regeneration** explicitly `unset COST_ESTIMATE_CORPUS` and points it at an empty temp file, and
  runs in a dir whose `.git` (if any) is a throwaway — so git-effort/#NoEstimates render **N/A** (both
  fixtures gate < 10 commits / parent-root) and RCF/Bayesian render **N/A** and **append nothing**.
  **§3 R8 updated:** git-derived anchors + corpus are **excluded from the byte-identical guarantee**;
  the MC band (seeded from static LOC/file/complexity signals) **is** byte-identical. Add a §2-step-11
  assertion that two regenerations are byte-identical with anchors + corpus neutralized.
- **Corpus WRITE requires `COST_ESTIMATE_CORPUS` set** (default-file existence enables **READ only**)
  — removes the silent-accumulation surprise (M6). Records store only repo **basename** + coarse stack
  (no contents/paths). The JSONL reader, when `jq` is absent, extracts each numeric key with
  `match($0,/"key":(null|-?[0-9.]+)/)`, treats `null`/absent as missing, **skips any record missing a
  required numeric** (never parses string values with the numeric regex); §2 test 7 asserts the `jq`
  and awk paths extract identically on a fixture that includes a `null`-field and a malformed line.

#### A8 — Bayesian: human-actuals-only, hard cap, no anchor leak; RCF needs real actuals *(closes C10, H4, H5)*

- **The headline-moving Bayesian likelihood uses ONLY genuine user-supplied human `actual_hours`.**
  `$ARGUMENTS` (AI-build time) **never** feeds productivity — that is a category error (C10) and would
  contaminate the human-from-scratch baseline P2-14 keeps separate. A human actual, if wanted, comes
  from a distinct, explicitly-flagged input (e.g. `COST_ESTIMATE_ACTUAL_HOURS`); `$ARGUMENTS` stays
  AI-only.
- **git-proxy effort is EXCLUDED from the headline-moving posterior** (H4) — shown only as an
  informational "alternate posterior (git-proxy; not in headline)". So commit-splitting cannot move
  P50. §2 test 9c asserts it.
- **Concrete single-datum cap (C10):** clamp `|μ_post − μ0| ≤ 0.5·σ0` (= 0.2027 in log → `Â ∈
  [2.40, 3.60]`) whenever fewer than **2** corroborating genuine actuals exist. Re-derive the Verify
  numerically: a bogus `"1 hour"` actual ⇒ `Â ≥ 2.40` (was −92 % → 0.23 without the cap). Guard
  `log(0)`/÷0: skip any datum with `actual_hours ≤ 0`, `estimate ≤ 0`, or `KLOC ≤ 0`.
- **RCF (H5):** when the matched class contains **zero** genuine user actuals, **suppress the uplift
  number** entirely → *"outside view unavailable — corpus holds estimates/git-proxies, not audited
  actuals."* Drop the unenforceable "append-only integrity" claim; instead **disclose inline** the
  class size + provenance and state the numbers are only as trustworthy as the user-editable corpus.
- **Percentile-grid + integration (M3):** standardize on **P10/P50/P80/P90** across cost band, RCF, and
  Bayesian. Bayesian predictive percentiles are **closed-form lognormal** (z = −1.2816/0/+0.8416/
  +1.2816), **no PRNG**. When ≥ 1 genuine actual exists, the posterior median `Â` replaces `2.94` in
  the deterministic point **and** the MC `C0`, and the productivity triangular widens by
  `sqrt(σ_post²+σ²)` — this is the *only* sanctioned way the headline moves, and only with real data.

#### A9 — False-rigor controls; demote fabricated forecasts *(closes M1, M2, M4, M7, H11; enforces R4)*

- **#NoEstimates (P2-13) → descriptive only (M1):** emit **no** completion-time percentiles and **no**
  bootstrap (the backlog `N` is invented for a finished repo). Report only *"demonstrated cadence ≈ X
  commits/week over its M-week active life"* — a measured fact — gated behind the git-root + MIN_COMMITS
  + MIN_NONZERO_WEEKS rules, rendered 1-sig-fig under OOM, never in the headline. **This removes the
  second PRNG entirely** (only the MC band remains random). *(Supersedes P2-13's MC/percentile spec.)*
- **SNAP (P2-3) → qualitative checklist, no computed total (M2):** do **not** emit an aggregate
  SNAP-point number built from ~86 %-placeholder weights. Map the 8 factors to SNAP categories as a
  **non-functional checklist**; if any number is shown it is the **2 public-weight sub-categories only**
  ("partial SNAP: 2 of 14 scored; remainder require the paywalled APM tables"). The ISO/IEC/IEEE
  32430:2025 citation appears in the methodology note as *the standard the mapping references*, never
  as a computed number's provenance. SNAP is **not** added to FP→effort ("off by default" →
  "not implemented"). *(Supersedes P2-3's aggregate-SP and "off by default" text.)*
- **Inline caveats (M4):** each estimator's one-line **Disclosed limitation renders in its own report
  section immediately under its number** (mirroring the IE ⚠️ callout), in addition to Methodology.
  §2 Verify greps the rendered report and asserts a heuristic/uncalibrated/N-A token within a few lines
  of every ensemble/anchor figure; gated-out N/A rows render with their reason *before* any computed row.
- **OOM band collapse (M7):** enforce `P10 ≤ P50 ≤ P80 ≤ P90` on the **raw pre-rounding** percentiles;
  under OUT_OF_DOMAIN **suppress the four-column band** and emit a single decade bucket (*"~$500; treat
  P10–P90 as within one decade — distribution not meaningful below COCOMO's domain"*). §2 test 4 asserts
  suppression (not four separately-rounded, possibly-colliding numbers).
- **OOM 1-sig-fig everywhere (H11):** add the explicit "under OUT_OF_DOMAIN render to 1 significant
  figure" line to **every** new numeric estimator (UFP, CFP, UCP, git-hours, cadence, Bayesian `Â` and
  its percentiles, RCF) — matching the IE block's retrofit.

#### A10 — Operational hardening *(closes H8; lows on test wording & provenance framing)*

- **Timeout class extended (H8):** every new grep/find is `timeout 30`; **each new consolidated awk
  block is `timeout 60`** with a defined fallback (that estimator → N/A + methodology note). No new
  long-running work is unbounded.
- **Single-block discipline (H8/R6):** Phase 2.5, 3.9, and 3.95 are each **exactly one Bash block**
  that re-substitutes every earlier-phase scalar as a top-of-block literal (enumerated: `KLOC`, `E`,
  `EAF`, point hours, `CODE_FILE_COUNT`, `TOTAL_FILE_COUNT`, `COMPLEXITY_SUM`, `genfrac`, per-category
  counts, `AWK_MATH`, `SEED`) and re-inlines `SOURCE_EXT_RE`/`STD_EXCLUDES` verbatim. **The MC SEED is
  derived from `CODE_FILE_COUNT`, `TOTAL_FILE_COUNT`, `COMPLEXITY_SUM` only — `SOURCE_CODE_LOC` is NOT
  a seed input** (A11 #1; it remains available for KLOC/genfrac but never seeds the PRNG).
  §2 static-audit: no new phase references a variable it didn't define or substitute in-block.
- **Provenance framing (low):** the "fictional from-scratch baseline" framing is gated behind
  git-root + `MIN_COMMITS` + ≥ 2 contributors; trailers are disclosed as **unverifiable, forgeable
  lower-bound** signals.
- **§2 test wording (low):** the static-audit checks removal of the live `×0.5 / ×2.0` headline band
  only; the `×0.6 / ×1.6` string is historical-narrative (P1) — reword, don't assert its removal.
  Restate the self-repo oracle as *"≈ 4 hours / 0.03 PM / ~$500 at 1 sig fig (OOM bucket)"*, tolerating
  the decade bucket rather than an exact `$500`.

**Round-1 outcome:** all 11 critical + 11 high + 10 medium findings are addressed by A1–A10 (several by
demotion to an honest form). A Round-2 confirmation pass follows; if it surfaces only ≤ Low items the
plan is declared converged and implementation proceeds against **body + A1–A10**.

---

### Red-team Round 2 — Amendments (A11) — reconciliation + 6 new-defect fixes + 5 low

Round 2 found A1–A10 were superseding the body **by reference only** — the stale body text was never
struck, leaving 4 high + 13 medium literal contradictions (headline=P50 vs A2; SLIM ensemble row /
compute vs A3; "14 CLI commands" vs A5; "Three PRNGs" vs A1/A8/A9; bootstrap-MC #NoEstimates vs A9;
$ARGUMENTS-as-Bayesian-datum vs A8; 5/10/50/90/95 grid vs A8; ensemble-widens-band vs A2; append-only
integrity vs A8; RCF in the awk-math gate; QSM-replaces-Jones vs A4; rate-sampled vs A2).

- **Reconciliation (done):** the body §0/§1/§2/§3 text was edited **in place** to match A1–A10 — no
  design change, only wording. Every contradicted site above now states the converged contract.

- **Six new-defect fixes (applied + recorded):**
  1. **SEED tool-invariance** — A1's seed now uses **only find-derived integers**:
     `SEED = ((CODE_FILE_COUNT*1000003 + TOTAL_FILE_COUNT*10007 + COMPLEXITY_SUM*101) % 2147483647)`,
     forced ≥ 1. `SOURCE_CODE_LOC` is **dropped** (cloc-vs-wc divergent: cloc=2014 vs wc-raw=2736 on
     the VM). A1's "tool-invariant signals" wording and A10's substituted-scalar list updated to
     match (CODE_FILE_COUNT, TOTAL_FILE_COUNT, COMPLEXITY_SUM for the seed — not SOURCE_CODE_LOC).
  2. **FP un-gate composition** — structural FP un-gates when `transaction_signal ≥ FP_FLOOR` **AND**
     (≥ 2 distinct artifact kinds **OR** a single kind clearing a higher single-kind floor of ≥ 5,
     e.g. ≥ 5 routes), so a routes-only API (ILF = 0, 5 routes) is NOT wrongly gated out. §2 test 5
     asserts the routes-only un-gate.
  3. **wc OOM cliff** — the §2 "VM remains ≥ 2.0 KLOC" assertion holds only under `CLOC_AVAILABLE=yes`;
     on wc fallback the VM is `2736 × 0.7 = 1915 → 1.915 KLOC → OUT_OF_DOMAIN`. The assertion is now
     conditioned on the cloc path and the straddle is noted.
  4. **Bayesian log→linear mapping** — when a genuine actual moves the headline, the widened
     productivity triangular endpoints `m_prod_O/P = exp(±z·√(σ_post² + σ²))` (and `Â = exp(μ_post)`)
     are computed **once outside the MC loop**, so the per-iteration draw stays linear + sqrt-only.
  5. **`genfrac` defined** — `genfrac = (GENERATED_TOTAL_LOC + vendored_LOC) /
     raw_source_LOC_before_exclusions`, clamped `[0,0.5]` (how much was removed, on the pre-exclusion
     raw total); referenced by this definition wherever the size three-point uses it.
  6. **Drop in-awk Lomuto quicksort** (O(n²) on the heavy-duplicate integer-dollar grid); the single
     mandated ranking method is `printf "%.0f" | LC_ALL=C sort -n`.

- **Five low fixes:** drop the in-awk quicksort option (also #6); add explicit `m_size`/`m_prod`
  three-points to A1 (`m_size` O=`1−genfrac−0.10`/M=`1`/P=`1.30`, `m_prod` O=`0.5`/M=`1`/P=`2.0`);
  P2-6 OOM → single decade bucket (not four 1-sig-fig percentiles); P2-8 grid → P10/P50/P80/P90 with
  z = (−1.2816, 0, +0.8416, +1.2816); RCF **not** awk-math-gated (integer quantiles, no
  transcendentals).

**Round-2 outcome: 4 high + 13 medium + 5 low addressed; design unchanged, body reconciled.**

### Red-team Round 3 — Plan convergence

A focused 3-lens confirmation pass over the reconciled plan found **0 critical, 0 high, 5 medium**
— all the same class (stale §0 summary text not matching the amendments: Beta-PERT/rate-as-driver/
per-percentile-OOM/"convergence→confidence"/FP display caveat) — which were edited in place, plus a
final convergence check that found **4 more medium** stragglers (R1 SLIM band-driver, S5 corpus
write trigger, A5 un-gate composition, P2-3 aggregate SNAP), all fixed. **Plan declared converged**
against **body + A1–A11**; implementation proceeded.

---

## §N — Implementation outcome (record)

All 14 P2 items implemented in `skill/SKILL.md` (1438 → ~1839 lines), `README.md`, and both sample
reports regenerated (A17 frozen-copy method).

- **Phase 0:** `AWK_MATH` capability probe + `GIT_IS_ROOT` repo-root guard.
- **Phase 2.5 (new):** archetype-gated structural ensemble — IFPUG UFP, COSMIC `CFP_APPROX`, UCP
  (source-scoped anchored greps; N/A on non-transactional code), SNAP qualitative checklist.
- **Step 3.6c (new):** Bayesian headline calibration (the only headline-mover; `Â∈[2.40,3.60]` cap;
  default `Â=2.94`, headline unchanged).
- **Step 3.9 (new):** seeded Monte-Carlo P10–P90 band (Park–Miller+Schrage, find-derived integer
  seed, linear multipliers, integer-dollar grid, external `LC_ALL=C sort -n`) replacing the invented
  ×0.5–×2.0; `AWK_MATH=no` falls back to the deterministic band.
- **Step 3.95 (new):** git session-reconstruction effort + AI-provenance + descriptive cadence
  (gated on `GIT_IS_ROOT` + ≥10 commits + ≥14 d + ≥6 weeks), and the opt-in reference-class corpus
  (RCF). SLIM is citation-only; #NoEstimates is descriptive-only.
- **Phase 5 / Methodology:** three-lens "what this is/is not" callout, renamed "Headline:
  Reproduction-Cost Estimate", Estimator Ensemble + Measured-vs-Parametric sections, empirical
  accuracy bounds (MMRE≈1.0/PRED(25)≈0), pinned METR/DORA/GitClear figures, updated Sources.

**Implementation red-team (3 rounds):** R1 `1 critical + 1 high + 4 medium` (RCF/Bayesian/corpus
were prose-only → added runnable code; COSMIC route double-count + co-occurrence; Phase-4 stale band
label; cadence gate) → R2 `2 high + 1 medium` (calibrated headline not wired into all consumers +
MC ignored calibration → introduced Step 3.6c headline-point definition + MC widening; numeric
`h+0<=0` guard) → R3 `0 critical, 0 high, 1 medium` (MC seed not echoed → added `MC_SEED`) + lows.

**A post-implementation repo audit** additionally caught and fixed: Phase 1b git stats not gated by
`GIT_IS_ROOT` (a checked-in subdir would report the parent repo's history); the MC band dollar/hours
unit note; the headline `AWK_MATH=no` branch; the Decision-Rules table missing the two new flags;
and stale `docs/todo/README.md` framing.

**Verification:** all 22 embedded bash blocks pass `bash -n`; the Monte-Carlo band is byte-identical
across re-runs (determinism); validated against both shipped fixtures (calibration VM → $93K with
FP/COSMIC N/A + UCP cross-check; self-repo → ~$500 code-only, IE 789 h separate, all structural
N/A); adversarial checks (route-padding/SLIM cannot move the headline; Bayesian cap holds against a
bogus 1-hour actual); static audit clean (no `srand()`/`$RANDOM`/time-seeding, no network/installs).

**Honestly deferred to a future P3 "depth" pass** (disclosed in-product): structure-anchored
AST-level sizing to actually remove the LOC anchor; seeding the reference class from a public dataset
(ISBSG/SEACRAFT); measured (not bucketed) scale factors; per-function cyclomatic/call-graph depth; an
independent technical-authoring throughput model for IE; localized non-English keyword sets.

