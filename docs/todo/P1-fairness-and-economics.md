# P1 — Fairness & Economics

This is the core "make it more fair" work. The estimate is currently **gameable**
(anyone can inflate it), **domain-biased** (web apps over-scored, hard non-web code
under-scored), **verbosity-rewarding** (LOC anchor), **language-biased**, and
**English-only** — and the cost layer double-counts overhead and presents an
unfalsifiable range. Each fix below targets one of those.

---

## A. Stop the Intellectual-Effort system from being gameable

### P1-1 🔴 Keyword padding inflates a file's tier and equivalent LOC ~30× with zero added information
*verified: confirmed (reproduced end-to-end) — the single strongest finding*

- **Claim:** Tier is driven by `DENSITY_PERMILLE = signal_lines*1000/lines` plus raw count
  gates. Stuffing trigger words (`must/never/always/if/when/constraint/architecture/
  "you are"/"step N"/"example:"`) into each line inflates every signal. The text need not be
  meaningful, and the T4 confirmation gate (`INST≥12 AND CONS≥8`) is satisfied by the
  padding itself.
- **Evidence:** Ran the exact Step 1.5c awk + 1.5d tree on two 100-line files. Plain prose:
  `DENS=0 → T1 → 10 equiv LOC`. Same 100 lines keyword-padded: `DENS=5000 → T4 → 300 equiv
  LOC` — a 30× jump. There is **no** anti-gaming/diversity/anomaly logic anywhere. Because
  T1 is excluded from the IE total (`:952,959`), net contribution is actually 0→300, so 30×
  understates it.
- **Impact:** The headline valuation is directly forgeable — unsafe for any
  acquisition/grant/portfolio use where someone has an incentive to inflate.
- **Fix:** Replace raw keyword frequency with stuffing-resistant signals: (a) per-family
  contribution caps / log-scaling, (b) require *lexical diversity* (distinct trigger lemmas,
  not repeats), (c) weight by surrounding unique tokens so a line that is 90% keywords scores
  *low*, (d) add an anomaly check that *demotes* statistically anomalous keyword density.

### P1-2 🟠 Frontmatter override lets an author self-assign Tier 4 (3.0×) with one comment line
*verified: confirmed*

- **Claim:** `<!-- intellectual-effort-tier: 4 -->` in the first 3 lines bypasses all signal
  detection and credits 3.0× (`:457-462`, `:511-528`), with no check that the content
  justifies it.
- **Fix:** Treat the override as an *upper bound that still requires corroboration*
  (`min(declared, computed+1)`), or require a maintainer-signed manifest *outside* the
  analyzed repo. Always surface overridden files in the report ("tier self-declared, not
  measured").

### P1-3 🟠 Short-file floor (Tier 3+ under 30 lines → 150 equiv LOC) is an invented constant with a 15× stub payoff
*verified: confirmed*

- **Claim:** Any Tier-3+ file under 30 lines is floored to 150 equiv LOC (`:592-599`,`:684`).
  A 10-line dense stub (natural 15 equiv LOC) is credited 150 — 15×, and the floor stacks
  across files (five 10-line stubs = 750 equiv LOC). No source for 150 or the 30-line cutoff.
- **Fix:** Remove the absolute floor. If a minimum is wanted, make it proportional and small
  (`max(equiv, 2*lines)`) and cap how many floored files can contribute.

### P1-4 🟡 Git-revision promotion (≥10 revisions → T3→T4) rewards churn, not effort, and is trivially farmed
*verified: confirmed*

- **Claim:** A T3 file with ≥10 commits auto-promotes to T4 (1.5×→3.0×), doubling equiv LOC
  (`:680-688`). Ten one-character commits achieve it; it also penalizes clean single-commit
  documents.
- **Fix:** Drop revision count as a promotion signal, or replace with a hard-to-farm
  churn-quality proxy (distinct authors / net substantive lines) and make it strictly
  advisory — able to *demote* but never to double the multiplier or move the dollar headline.

### P1-5 🟠 Signal regex counts per-LINE (not per-occurrence) and misses end-of-line keywords — density is line-wrapping noise
*verified: confirmed*

- **Claim:** Each awk rule fires once per line regardless of keyword count, and several
  patterns require a trailing space (`/must /`, `/never /`, `/rule /`), so an end-of-line
  keyword never matches. Reflowing the same text to one keyword per line can multiply the
  signal ~13×; the trailing-space requirement silently zeroes terse lists; patterns are
  lowercase-only so sentence-initial capitalized words are missed.
- **Evidence:** `:465-473`; `printf 'You must always\n' | awk '/always /'` → no match.
- **Fix:** Use word-boundary anchors (`\<always\>`), `gsub()` to count occurrences per line,
  `tolower($0)` for case-insensitivity, and normalize by token count (not physical lines) so
  wrapping can't move the tier.

---

## B. Stop prose from out-valuing code

### P1-6 🟠 Crediting prose at 0.5×–3.0× the rate of production source code, blended into one headline
*verified: partially-confirmed → framing softened, conclusion stands; severity high*

- **Claim:** Phase 1.5 converts prose lines to "equivalent effort LOC" at up to 3.0× and
  folds them into COCOMO at the project's own hours/KLOC rate, asserting a line of markdown
  ≈ 1.5–3 lines of compiling/tested code. *(Correction from verification: the agent's "80×
  per-line" was wrong — that was the total ratio across 1,397 prose vs 29 code lines;
  per-line is ~1.7×. And IE is a COCOMO-anchored hybrid, not free-standing. The real
  distortion is the **additive blend into a single COCOMO-framed headline**, not the
  multiplier size.)*
- **Fix:** Cap the prose multiplier at ≤ source rate (≤0.3×, the weight already used for
  CONFIG_ONLY; never >1×). Better: estimate prose effort with an independent technical-
  authoring throughput model, decoupled from COCOMO's code-calibrated hours/KLOC, and report
  it as a **separate, non-additive** line item.

### P1-7 🟠 IE blends additively into "Combined Base Effort" and silently dominates the headline
*verified: confirmed (self-referential inflation)*

- **Claim:** `Total_Effort_Hours = COCOMO + IE_Hours` (`:996-1002`) feeds every cost table and
  the "team of N engineers" headline. When IE is large the headline *is* the IE number, but
  it's presented as a code-build estimate. On the self-report, 98.6% of the $73K is one
  markdown file scored by the tool's own rules; re-scoring just that file moves the headline
  T1→$5.8K, T3→$73K, T4→$145K.
- **Fix:** Report IE and code effort as two separate, clearly-labeled estimates; never sum
  into one COCOMO-framed headline. If a combined figure is shown, attach an automatic
  sensitivity line ("X% of this estimate is non-code intellectual-effort credit at multiplier
  M; at 0.1× weighting it would be $Y"). Suppress the "team of N engineers" framing whenever
  IE share > ~40%. Require some source code before IE can be booked, so a pure-docs repo
  can't return a large "build cost."

### P1-8 🟡 Config/markup excluded from FP but re-admitted as full IE credit — inconsistent treatment

- **Claim:** Markdown/YAML/JSON are excluded from KLOC/FP as "non-functional" (`:1031`) yet
  the same files are credited up to 3.0× via Phase 1.5 (`:347,358`). A file is "effort-
  irrelevant" for the primary model and simultaneously the dominant effort source.
- **Fix:** One consistent treatment; cap total IE at ≤30% of code-derived effort.

---

## C. Make complexity scoring domain-fair

### P1-9 🔴 All 8 complexity factors grep web-SaaS-backend signals — under-scores compilers, ML, games, embedded, DSP, kernels, HDL, algorithmic code as "Simple"
*verified: confirmed*

- **Claim:** Every factor is a web/cloud idiom probe: Integrations=HTTP clients,
  Data=ORMs/Redis/Kafka, Auth=jwt/oauth/bcrypt, Infra=Docker/Terraform/k8s,
  Observability=sentry/datadog/winston, Security=helmet/cors/CSP. Software with none scores 1
  on six of eight factors → ~1.1/5 "Simple," driving EAF and the estimate down. A boilerplate
  CRUD app trips Data+Auth+Infra → "Moderate/Complex." The self-report proves it: a 1,400-line
  expert artifact scores 1.1/5.
- **Evidence:** `:743,750,757,771,780,799`; under-scored archetypes — compiler/interpreter,
  CUDA/PyTorch training loop, numerical/DSP/FFT lib, game engine, firmware/RTOS, OS kernel,
  competitive-algorithm code, pure-SQL/Spark pipelines, HDL, quant models.
- **Fix:** Add domain-general signals scored as `MAX(web-probe, domain-probe)`: math/numerical
  density (matrix/vector/FFT/SIMD/`<cmath>`/numpy/eigen), concurrency/parallelism
  (threads/atomics/mutexes/CUDA/OpenMP/MPI), low-level/systems (pointers/manual memory/inline
  asm/`volatile`/MMIO), parser/compiler (lexer/parser/AST/grammar/IR/bytecode), state-machine/
  protocol complexity, per-function cyclomatic complexity. Detect archetype first and select a
  factor panel. Replace the hard score-1 floor (`:805`) with archetype-aware defaults.

### P1-10 🟡 File-count score mapping entrenches a second volume bias

- **Claim:** Every factor maps a *count of files* to 1–5 (`:745,752,766,775,794,801`), so "how
  many files contain a web idiom" beats depth; a 200-file shallow microservice outscores a
  10-file numerical core.
- **Fix:** Score factors on intensity/depth (complexity distribution, call-graph depth,
  concurrency/recursion/math presence) rather than file counts.

### P1-11 🟠 Language coverage gaps — whole languages invisible to the effort anchor
*verified: confirmed*

- **Claim:** `SOURCE_EXTENSIONS` (`:30`) and the LOC/FP table (`:1008-1030`) omit Julia,
  Solidity, GLSL/shaders, CUDA, Verilog/SystemVerilog/VHDL, Fortran, COBOL, Assembly, F#,
  OCaml/Reason, Objective-C++, MATLAB, Perl, Scheme/Racket, and the C++ alternates `.cc/.cxx/
  .hpp/.hh`. `.cc` appears *only* inside the generated `*.pb.cc` pattern, so ordinary `.cc`
  C++ is never counted. `.m` is ambiguous (Obj-C / MATLAB / Mathematica).
- **Fix:** Delegate LOC + language detection to `cloc` (already classifies most of these);
  expand `SOURCE_EXTENSIONS`; content-sniff `.m`; add FP ratios for the new languages
  (Assembly ~200, COBOL ~90, MATLAB ~30, Julia ~40, Solidity ~50, Fortran ~90) instead of the
  blanket 50 default.

### P1-12 🟡 English-only signal/complexity regex under-values non-English codebases

- **Claim:** Every Phase 1.5 signal and Phase 2 grep is English-keyword-based (`:493` admits
  it). Non-English repos land every artifact in Tier 1 and score "Simple," getting a lower
  dollar figure for equal work; the only escape is a per-file English override tag.
- **Fix:** Detect predominantly-non-English repos and warn loudly that the estimate is biased
  low; support localized keyword sets, or fall back to language-agnostic structural signals
  (nesting, list density, cross-references).

---

## D. Fix the cost / valuation layer

### P1-13 🟠 Overhead multiplier double-counts a rate already declared "fully-loaded"
*verified: confirmed*

- **Claim:** `Cost = Hours × Blended Rate × Overhead(1.0–1.65×)` (`:1072`) multiplies a rate
  the methodology calls "fully-loaded … not salary equivalents" (`:1340`) by an overhead
  factor that covers "hiring/onboarding, coordination, compliance" (`:1067`) — the exact items
  a fully-loaded rate already bills. Enterprise is inflated 65% for nothing.
- **Fix:** Pick one: keep fully-loaded rates and set all overhead to 1.0× (delete the
  multiplier), or relabel rates as unburdened and keep overhead. Model team size in the
  schedule path, not as a markup on invariant hours.

### P1-14 🟠 Org-overhead multiplier is incoherent on top of COCOMO's already-superlinear effort
*verified: confirmed*

- **Claim:** `2.94 × KLOC^E` with E>1 already encodes size-driven diseconomies; multiplying
  fixed person-hours again by a headcount-overhead factor charges for size overhead a third
  time (exponent, then EAF, then OH). Effort-hours don't change with how many people you
  assign — that's a schedule effect, not a cost markup.
- **Fix:** Drop the team-size overhead from the cost equation; model team size only in
  Calendar-Time via Effective Devs. If coordination loss must be modeled, do it once with a
  cited term.

### P1-15 🔴 Headline valuation spans 4.6×–5.1× → unfalsifiable
*verified: confirmed*

- **Claim:** Conservative = Solo×0.6×; Premium = Enterprise×1.6×1.65 OH → effective
  $75–$383/hr (5.1× with template rates; 4.65× with sample rates). A band this wide "confirms"
  any number a reader proposes.
- **Fix:** Replace the cherry-picked min-cell/max-cell tiers with a single honest point
  estimate (one method, mid rate, no overhead double-count) plus an explicit, symmetric,
  sourced uncertainty band. (Real probabilistic band = P2.)

### P1-16 🟠 "Team of N engineers over Tdev months" implies absurd utilization
*verified: confirmed*

- **Claim:** The headline pairs a fixed Effective-Devs constant (6.5) with the Tdev schedule.
  For the self-report: 6.5 × 4.6 mo × 152 = 4,545 h capacity for 330 h of work = 7.3%
  utilization (`sample-report.md:105`). Also Tdev is computed from the *combined* prose-
  inflated PM, not the COCOMO software PM, inflating the schedule ~4×.
- **Fix:** Derive headcount from effort/schedule (`avg staff = PM/Tdev`); flag/suppress the
  team-size claim when implied utilization is <25%; compute Tdev strictly from the COCOMO
  software PM, with IE time as a separate additive line outside the schedule equation.

### P1-17 ⚪ Calendar-time and the 55/20/12/8/5 activity split are fixed, presented to one decimal

- **Claim:** `Calendar Time = max(naive, Tdev)` printed to one decimal as if precise; when
  Tdev floors all profiles they all show the identical month figure (non-informative). The
  activity split is constant regardless of the measured factor scores (a repo scoring 1/5 on
  Testing still gets 20% Testing & QA).
- **Fix:** Show Calendar Time as a range; when Tdev floors all profiles, say so. Derive the
  activity split from the measured factors, or label it a generic industry default with a
  citation.

---

## E. Disclose the conflict of interest

### P1-18 🟠 Undisclosed structural conflict of interest + self-flattering flagship example
*verified: confirmed (design)*

- **Claim:** The author ships a tool that introduces a non-COCOMO system crediting prose/
  prompts up to 3.0× code rate, then showcases it on its own prompt-heavy repo where it
  self-reports $73K, 98.6% of which is its own `SKILL.md`. A prompt artifact built a method
  that happens to value prompt artifacts highly, demonstrated by valuing itself — undisclosed,
  and in a sub-500-LOC regime the model itself flags as low-confidence.
- **Fix:** Disclose openly in the README ("this tool's IE design favors prose/prompt artifacts
  like itself; the self-referential example is illustrative, not a neutral benchmark"), and
  ship a **primary example on a conventional code repo** of independently-known build cost so
  readers can calibrate against a non-self-serving case.

### P1-19 🟠 Sub-2-KLOC / single-author / prose-dominated repos are out of COCOMO's domain — suppress precise figures
*verified: partially-confirmed (related: exponent inversion is contained)*

- **Claim:** COCOMO II is calibrated on multi-person application projects above ~2 KLOC; the
  flagship use is the opposite (1 author, 0.03 KLOC, markdown-dominated), disclosed only as a
  "low confidence" note while full point-dollar tables are still printed. Separately: below
  1 KLOC the isolated `KLOC^E` term inverts (a real but **contained** defect — E and EAF
  co-move, so end-to-end Complex still computes more; no Complex-cheaper-than-Simple output is
  emitted).
- **Fix:** When out-of-domain (KLOC<2, contributors=1, or config/prose-dominated), suppress
  precise dollar tables and the AI multiplier; emit only a bounded order-of-magnitude with the
  PRED caveat. Clamp the KLOC base to ≥1 before exponentiation to neutralize the inverted
  factor. Don't print 4-significant-figure costs under a "low confidence" banner.

### P1-20 🟡 `E=1.26` (SF_total=35) is unreachable in real COCOMO II; "Simple" (E=1.06) is below all-Nominal

- **Claim:** COCOMO II's 5 scale factors max at Σ≈31.62 → `E_max≈1.226`; the skill hard-codes
  SF_total=35 → E=1.26, outside the model's range (`:842`). "Simple" (15.0 → E=1.06) is below
  the all-Nominal sum (18.97 → E≈1.10).
- **Fix:** Bound the three buckets inside the real range: Simple≈19 (E≈1.10), Moderate≈25
  (E≈1.16), Complex≈31 (E≈1.226). Don't emit an exponent COCOMO II cannot produce. *(Deeper
  fix — actually measuring scale factors — is P2.)*
