# P1 Implementation Plan — Fairness & Economics

Plan to resolve all 20 findings in `P1-fairness-and-economics.md`. Line numbers refer to
`skill/SKILL.md`, `README.md`, `examples/sample-report.md` **as of the current working tree
(post-P0)**. This plan is the contract the implementation is reviewed against.

P1 builds on the already-implemented P0 working tree (consolidated IE block at Step 3.6b,
source/config split by extension, untrusted-input hygiene, reproduction-cost framing). The
deeper research redesigns (Monte-Carlo band, measured scale factors, archetype-panel
selection, per-function cyclomatic, independent technical-authoring throughput model) are
explicitly **P2** and out of scope here; where a finding's "deeper fix" is P2, P1 takes the
contained option and says so.

## User design decisions (locked before planning — these drive everything)

| # | Decision | Resolves | Chosen option |
|---|----------|----------|---------------|
| D1 | **Intellectual-Effort (IE) is a separate, non-additive estimate.** The COCOMO dollar headline is **code-only**; IE is its own clearly-labeled line item, never summed into the reproduction-cost headline. | P1-6, P1-7, P1-8 | "Separate, non-additive" |
| D2 | **Drop the overhead multiplier.** Keep fully-loaded rates; set all overhead to 1.0×; model team size only in the schedule path. | P1-13, P1-14 | "Drop overhead (keep loaded rates)" |
| D3 | **Headline = single point estimate + symmetric sourced band.** Remove the cherry-picked Conservative(Solo×0.6)/Premium(Enterprise×1.6×OH) tiers. Real probabilistic band = P2. | P1-15 | "Point estimate + symmetric band" |
| D4 | **Complexity = contained domain probes.** `score = MAX(web-probe, domain-probe)`, broaden language + FP coverage, soften the hard score-1 floor. Archetype-panel selection + cyclomatic = P2. | P1-9, P1-10, P1-11, P1-12 | "Contained: add domain probes" |

Environment confirmed on this machine (drives the test plan): **cloc 2.04, jq, git, pandoc,
xelatex all present** (so both the cloc path AND PDF regeneration are exercisable here — a
change from P0, where pandoc/xelatex were absent). This repo: 3 commits, 1 contributor
(`mlamp`), `skill/SKILL.md` 1,444 lines, source = ~29 LOC Shell → **out-of-domain** (KLOC<2,
1 contributor) under PS6.

---

## 0. Structural decisions (these drive multiple fixes)

### PS1 — IE becomes a SEPARATE, NON-ADDITIVE estimate; code is COCOMO-only *(D1; resolves P1-6, P1-7, P1-8)*

The single biggest change. Today `Total_Effort_Hours = COCOMO(adjusted KLOC) + IE_HOURS`
feeds one COCOMO-framed headline that IE dominates (98.6% of the self-report's $73K). New
architecture:

- **The reproduction-cost headline is code-only.** It uses COCOMO on the source KLOC. IE
  hours/PM/FP/cost are reported in their **own section**, explicitly labeled *not added to the
  headline* and *the least-grounded, heuristic part of the tool*.
- **One file is either code or a non-code artifact, never both** (this is the consistent
  treatment P1-8 asks for). IE candidates are **non-source files only** — any file whose
  extension is in `SOURCE_EXTENSIONS` (incl. `.tf`/`.hcl`/`.sql`/`.sh`) is **excluded from IE
  candidacy** because it already counts in COCOMO KLOC. Markdown/prose/`.json`/`.yaml`/`.toml`
  (not in COCOMO) remain IE candidates.
- **Consequence: dedup is removed entirely.** With zero overlap between COCOMO files and IE
  candidates, there is nothing to de-duplicate. Delete `ORIGINAL_LOC`, `DEDUP_LINES_SUBTRACTED`,
  `ADJUSTED_LOC`, the by-file source manifest, and the **second COCOMO pass**. COCOMO is now
  computed **once** on the source KLOC. This is a large simplification of Step 3.6b.
- **IE hours rate.** IE equiv-LOC → hours still uses the project's COCOMO-derived
  `hours/KLOC` (so it scales with project complexity); the model injects `COCOMO_PERSON_HOURS`
  and `COCOMO_KLOC` into the block as before, but **not** `ORIGINAL_LOC`. The independent
  technical-authoring throughput model (full decoupling, P1-6 "Better") is **P2**; for P1 we
  keep the COCOMO-derived rate but report it separately and caveat it heavily.
- **Sensitivity disclosure (P1-8 residual).** The IE section prints the IE-hours-as-%-of-code-
  effort ratio, so a reader sees how large the heuristic supplement is relative to the grounded
  code estimate — without it touching the headline. No ≤30% cap is imposed (capping a
  separately-reported, clearly-labeled heuristic is unnecessary once it is out of the headline;
  the disclosure is the honest lever).
- **FP:** headline `Total_FP = Source_Code_FP` only. `IE_FP` is shown in the IE section,
  labeled separate/heuristic.
- **CONFIG_ONLY interaction:** unchanged in spirit — when there is no source code, config LOC
  ×0.3 is the COCOMO basis and IE stays descriptive-only (already the case). With IE now always
  separate, CONFIG_ONLY simply means the headline is the config-derived COCOMO number and IE is
  its usual separate descriptive line.

### PS2 — Drop the overhead multiplier *(D2; resolves P1-13, P1-14)*

- Team Profiles: **Overhead = 1.0× for every profile.** Keep the fully-loaded blended rates.
- Cost formula: `Total Cost = Person-Hours × Blended Rate` (no overhead term).
- Team size affects **only** Calendar Time (via Effective Devs), never the dollar figure —
  effort-hours don't change with how many people you assign (that's a schedule effect).
- Update the Team Profiles table, the cost formula, the Phase-4 note, the methodology
  "Overhead" bullet (becomes "no overhead multiplier — rates are fully loaded; team size is a
  schedule effect, not a cost markup"), and README.

### PS3 — Single point estimate + symmetric sourced band *(D3; resolves P1-15)*

- **Remove** the cherry-picked Headline Valuation tiers (Conservative = Solo×0.6, Premium =
  Enterprise×1.6×1.65 OH). They spanned 4.6–5.1× and "confirmed" any number.
- **Headline = one realistic point + one band.** Point = code-only Source-Code-Effort hours ×
  **$125/hr** (the mid blended rate, no overhead). Band = **point × 0.5 to point × 2.0**,
  labeled *"typical parametric error (≈ −50% / +100%); NOT a statistical confidence interval —
  a real probabilistic band is future work."* This is the sourced, non-cherry-picked band.
- **Effort:** report a single point person-hours/PM + the same ×0.5–×2.0 band. The Phase-3.8
  Low/Mid/High **scenario** table (0.6/1.0/1.6) is **removed as a headline driver**; scenario
  sensitivity is folded into the single band (scenario assumptions and parametric error were
  two different things presented as one; we keep the honest parametric error band).
- **Cost table** (Phase 4) becomes **rate sensitivity**, not a range: one column = cost at the
  point estimate per profile (`point hours × rate`), plus Calendar Time. Clearly labeled "rate
  sensitivity across team profiles — not the uncertainty band." The band is shown once, on the
  realistic point.
- Net effect: the cost spread across profiles is now only the rate spread ($115–$145 ≈ 1.26×),
  and the uncertainty is one honest ±band — falsifiable.

### PS4 — Stuffing-resistant, repetition/wrap-proof IE signal model *(resolves P1-1, P1-5; structural half of P1-12)*

Replace the per-line, trailing-space, lowercase-only, count-driven signal model with a
deterministic single-`awk`-pass model that is invariant to repetition and line-wrapping and
actively demotes keyword stuffing.

**Tokenization & matching (P1-5).** Lowercase the whole file (`tolower`). Split into word
tokens on `[^a-z0-9]+`. Match trigger lemmas with **word boundaries** (a lemma matches a
whole token, so end-of-line / sentence-initial / terse-list keywords all count; no trailing
space required, case-insensitive). Counting is done by tokenizing, not by per-line regex —
**re-wrapping the same text cannot change any count.**

**Distinct, capped signal (P1-1a,b).** For each of the families below, count the number of
**distinct lemmas** present (each lemma counts once no matter how many times it repeats), and
cap each family's contribution at its lexicon size (a natural per-family cap). Let
`S = Σ_families (distinct lemmas present)`. Repetition adds **zero** to `S` — this alone
defeats the documented padding attack.

**Token-normalized density (P1-1c, P1-5).** `density_permille = S × 1000 / max(W, 1)` where
`W` = total word tokens. A padded file inflates `W` (many appended trigger words) while `S`
stays at the small number of distinct lemmas → density **drops**. Worked check of the exact
documented attack: 100 lines of plain prose (~1,000 tokens, S≈0) → density 0 → **T1**. Same
text with 6 trigger words appended to every line: `S ≈ 6` distinct, `W ≈ 1,600` →
`density ≈ 4` permille → **T1** (was T4). Attack neutralized; 30× inflation → ~0×.

**Diversity requirement (P1-1b).** High tiers require breadth, not one spammed family. Let
`F` = number of families with ≥1 distinct lemma. T4 requires `F ≥ 4`; T3 requires `F ≥ 3`
(in addition to density). You cannot reach T4 by maxing a single family.

**Anomaly demotion (P1-1d).** Compute `KO` = total raw trigger occurrences (via `gsub`) and
`keyword_fraction = KO / max(W,1)`. If `keyword_fraction > 0.5` (the file is majority trigger
tokens — implausible for genuine content) **OR** `distinct_words / max(W,1) < 0.2` (extreme
repetition), **demote one tier** (floor T1). This catches a determined stuffer who uses many
distinct lemmas in a tiny all-keyword file.

**Language-agnostic structural family (P1-12 structural half).** Add a 6th family,
**STRUCTURE**, counted language-agnostically: markdown headings (`^#+ `), list items
(`^\s*[-*0-9]`), fenced code blocks, table rows (`^\s*|`), and cross-reference links
(`\[.*\]\(` / `\[\[`). This contributes to `S`/`F` so a well-structured non-English doc is not
forced to T1. (Full localized keyword sets = P2.)

**Families & lemma lists (word-boundary, lowercase).** Carried over and de-duplicated from the
current 5 awk rules, expressed as lemma sets:
- COND (conditional logic): if, when, unless, else, otherwise, must, never, always, only, except, provided, case, decision, choose, depending, whenever
- CONS (constraints): constraint, requirement, rule, invariant, precondition, postcondition, boundary, limit, threshold, maximum, minimum, exactly, "at least", "at most", forbidden, mandatory, required
- DOM (domain expertise): architecture, pattern, antipattern, tradeoff, "failure mode", "edge case", fallback, degradation, scaling, latency, throughput, consistency, availability, partition, idempotent, concurrency
- INST (instructions): "you are", "your role", "your task", respond, output, format, "do not", step, phase, stage, generate, produce, return, ensure
- EXAM (examples): example, "e.g.", "for instance", "such as", template, format, schema, sample, placeholder-braces `{...}`/`<...>`
- STRUCT (structure, language-agnostic): heading, list-item, code-fence, table-row, cross-ref (counted from line shapes, not English words)

Multi-word lemmas ("at least", "failure mode") are matched as adjacent-token sequences in the
same `awk` pass. Thresholds (density cut points and the `F` gates) are **calibrated during
implementation/testing** against this repo + crafted genuine/padded fixtures and the **final
locked values are recorded in the plan's outcome section and in SKILL.md**. Provisional start
points: T4 ≥ 120‰ & F≥4; T3 ≥ 60‰ & F≥3; T2 ≥ 25‰; else T1; T0 unchanged (auto-gen / lock /
license / trivial README).

### PS5 — Domain-fair complexity, language & FP coverage *(D4; resolves P1-9, P1-10, P1-11, P1-12 warn)*

- **P1-9 (MAX(web, domain)).** For each grep-based factor add a domain-general probe and set
  `score = MAX(web_probe_score, domain_probe_score)`. Domain probe families (new
  `DOMAIN_PROBES`): math/numerical (`matrix|vector|tensor|fft|simd|<cmath>|numpy|eigen|blas|
  lapack|gemm|conv`), concurrency/parallelism (`thread|atomic|mutex|cuda|openmp|<mpi|mpi_|
  goroutine|rayon|async|spinlock`), low-level/systems (`malloc|free|mmap|volatile|inline asm|
  __asm|register|pointer arithmetic|MMIO|ioctl|syscall`), parser/compiler (`lexer|parser|ast|
  grammar|bytecode|opcode|tokenize|codegen|ir\b`), state-machine/protocol (`state machine|
  transition|opcode|protocol|handshake|frame|packet`). Map: Integrations += systems/IPC/FFI;
  Data Layer += math/numerical/format-parsing; CPLX (driven by Integrations + Auth) takes MAX
  with the algorithmic panel (math+concurrency+low-level+parser). Replace the hard "score 1 if
  no web evidence" floor with **archetype-aware defaults**: if domain probes fire but web
  probes don't, the relevant factor takes the domain score (never auto-1).
- **P1-10 (depth, not just breadth).** For grep factors compute an **intensity** signal in
  addition to file count: `total_matches` (`grep -c` summed) and `intensity = total_matches /
  max(matching_files,1)`. Final factor score considers both breadth (files) and intensity
  (matches/file) so a 10-file numerical core with deep usage is not beaten by a 200-file
  shallow microservice. Concretely: `score = clamp(MAX(breadth_score, domain_breadth_score) +
  intensity_bump)` where `intensity_bump = +1` if intensity ≥ a defined threshold (capped at
  5). Call-graph depth = P2.
- **P1-11 (languages + FP).** Expand `SOURCE_EXTENSIONS`, every inlined `find`/`grep` include
  list, both `SOURCE_EXT_RE` copies, `ext_lang()`, and the LOC/FP table to add: Julia `.jl`
  (40), Solidity `.sol` (50), CUDA `.cu/.cuh` (55), shaders `.glsl/.vert/.frag/.comp` (40),
  Verilog/SV/VHDL `.v/.sv/.svh/.vhd/.vhdl` (HDL ~50), Fortran `.f/.f90/.f95/.f03/.f08` (90),
  COBOL `.cob/.cbl/.cpy` (90), Assembly `.asm/.s/.S` (200), F# `.fs/.fsx/.fsi` (40),
  OCaml/Reason `.ml/.mli/.re` (40), Objective-C++ `.mm` (45), Perl `.pl/.pm` (35),
  Scheme/Racket `.scm/.rkt/.ss` (35), MATLAB (`.m` via content-sniff) (30), and the **C++
  alternates `.cc/.cxx/.c++/.cpp`, headers `.hpp/.hh/.hxx/.h`** (97). Fix the `.cc`-only-in-
  `*.pb.cc` gap (ordinary `.cc` now counts). Content-sniff `.m`: Objective-C if
  `@interface|@implementation|#import|#include`, else MATLAB if `function .*end|^\s*%|^\s*function`,
  else default Objective-C (status quo). On the cloc path, cloc already disambiguates `.m`
  (MATLAB vs Objective-C vs MUMPS) and classifies most new languages — the extension-driven
  split (P0 A14) means new source extensions are counted automatically; the FP table additions
  cover the per-language ratios. Default for an unlisted source language stays 50 LOC/FP.
- **P1-12 (non-English warn).** Detect a predominantly-non-English repo: across all IE
  candidates, if total trigger signal `S` is ≈0 **and** substantial prose volume exists
  (total candidate tokens above a threshold) and the non-ASCII-alpha token fraction is high,
  set a `NON_ENGLISH` flag → emit a **loud report warning**: "Signal/complexity detection is
  English-keyword-based; this repo appears predominantly non-English, so IE and complexity are
  likely **biased low**. Use the `intellectual-effort-tier` override tag for known artifacts."
  The STRUCTURE family (PS4) already gives non-English docs a language-agnostic signal path.

### PS6 — Honest small / out-of-domain handling; real-range exponents *(resolves P1-19, P1-20)*

- **P1-19 (out-of-domain suppression).** Add an `OUT_OF_DOMAIN` flag = (Effective KLOC < 2)
  OR (contributors ≤ 1) OR (config/prose-dominated: Source LOC < 20% of total counted LOC).
  When set:
  - The dollar headline and all cost figures are rendered as **order-of-magnitude buckets**
    (one significant figure / "~$Xk", or a decade band like "$1k–$10k"), **not** 3–4-sig-fig
    tables under a "low confidence" banner.
  - The AI Speed Comparison **ratio is suppressed** (show context only, no multiple).
  - A prominent **PRED caveat**: "Below ~2 KLOC / single-author / config-or-prose-dominated,
    this is outside COCOMO II's calibrated domain; only an order-of-magnitude is reported."
  - TINY_REPO becomes a subset of / is folded into this flag's messaging (kept for the <500
    LOC wording).
  - **KLOC^E inversion:** documented as *contained* (per the finding, E and EAF co-move so no
    Complex-cheaper-than-Simple output is ever emitted). We do **NOT** clamp the KLOC base to
    ≥1 (that would inflate a 0.03-KLOC repo to ~1.25 PM via `1^E`, a worse error). Because
    OUT_OF_DOMAIN already emits order-of-magnitude only, the residual sub-KLOC inversion is
    immaterial to any emitted figure. *(This is a deliberate, documented deviation from the
    finding's literal "clamp to ≥1"; flagged for the plan red-team to pressure-test.)*
- **P1-20 (real COCOMO II exponent range).** Re-bound the three buckets inside COCOMO II's
  achievable range (5 scale factors, max Σ≈31.62 → E_max≈1.226; all-Nominal Σ≈18.97 → E≈1.10):
  - Simple → SF_total **19.0** → E = 0.91 + 0.01×19 = **1.10**
  - Moderate → SF_total **25.0** → E = **1.16**
  - Complex → SF_total **31.0** → E = 0.91 + 0.01×31 = **1.226**

  Update Step 3.3, the schedule `F = 0.28 + 0.2*(E-0.91)`, and the methodology. Measuring the
  five scale factors directly = P2.

### PS7 — Schedule & headcount sanity *(resolves P1-16, P1-17)*

- **P1-16.** Tdev is computed **strictly from the COCOMO software PM** (code-only), not the
  IE-inflated combined PM (which no longer exists after PS1). Derive headline headcount from
  `avg staff = software PM / Tdev` (rounded, ≥1) instead of the fixed 6.5. **Suppress** the
  "team of N engineers over T months" phrasing when implied utilization
  `software_PM / (N × Tdev) < 25%`; instead say "a small / part-time team." IE, if it has any
  schedule, is a separate additive line outside the COCOMO schedule equation (we report IE
  hours, not an IE schedule, to keep it simple).
- **P1-17 (⚪ low; addressed via labeling — not a Medium+ blocker).** Show Calendar Time as a
  range; when Tdev floors all profiles, state "Tdev dominates at this size; all profiles show
  the same minimum schedule." Label the 55/20/12/8/5 activity split explicitly as a **generic
  industry default (cite)**, not a measured split. (Deriving the split from measured factors =
  P2.)

### PS8 — Disclose the conflict of interest; ship a neutral example *(resolves P1-18)*

- **Disclosure (mandatory, the substantive 🟠 fix).** README + every generated report state:
  "This tool's IE design credits prose/prompt artifacts (up to 3.0×); the self-referential
  example is **illustrative, not a neutral benchmark** — the tool valuing itself is a known
  structural conflict of interest." Place it near the self-example link in README and in the
  report's IE section / methodology.
- **Neutral calibration example.** Ship a **code-dominated** example so readers calibrate
  against a non-self case. Create a small but genuine conventional code repo as a fixture under
  `examples/calibration-codebase/` (a real, idiomatic ~300–500 LOC program, code >> prose) and
  generate `examples/sample-report-codebase.md` from the corrected skill. It is labeled
  honestly as "a small conventional code repo for calibration; **no external market price is
  claimed**" (we cannot honestly assert an "independently-known build cost" without a real
  third-party project and network access, which Constraints forbid — so we provide a neutral
  *code-dominated* contrast case, which is the substance of the ask). `examples/` is excluded
  from the self-report scope (A17), so the fixture does not pollute the self example.

---

## 1. Per-issue fixes (cross-referenced to the structural decisions)

| Finding | Sev | Resolved by | Notes |
|---|---|---|---|
| P1-1 keyword padding inflates tier ~30× | 🔴 | **PS4** | distinct-capped lemmas + token-normalized density + diversity + anomaly demotion; verified against the documented attack |
| P1-2 frontmatter override self-assigns T4 | 🟠 | **§1 P1-2** | `effective = min(declared, computed+1)`; always surfaced as "self-declared, not measured" |
| P1-3 short-file 150-LOC floor | 🟠 | **§1 P1-3** | remove the absolute floor entirely (round-to-nearest already prevents zero); no invented constant |
| P1-4 git-revision promotion farms churn | 🟡 | **§1 P1-4** | remove the git-revision adjustment entirely (farmable both ways; churn-quality proxy = P2) |
| P1-5 per-line / trailing-space / case regex | 🟠 | **PS4** | tokenized, word-boundary, `tolower`, `gsub`, token-normalized — wrap-invariant |
| P1-6 prose credited at code rate, blended | 🟠 | **PS1** | separation is P1-6's "Better" (separate non-additive line); decoupled throughput model = P2 |
| P1-7 IE additively dominates headline | 🟠 | **PS1** | headline is code-only; IE separate, with %-of-code sensitivity disclosure |
| P1-8 config excluded from FP but full IE credit | 🟡 | **PS1** | one consistent treatment: a file is code XOR artifact; IE FP separate |
| P1-9 web-only complexity factors | 🔴 | **PS5** | MAX(web, domain) probes + archetype-aware floor |
| P1-10 file-count volume bias | 🟡 | **PS5** | intensity (matches/file) bump alongside breadth |
| P1-11 language/FP coverage gaps | 🟠 | **PS5** | +18 languages/ext groups, FP ratios, `.cc` fix, `.m` sniff |
| P1-12 English-only regex | 🟡 | **PS4 + PS5** | STRUCTURE family (language-agnostic) + NON_ENGLISH warn |
| P1-13 overhead double-counts loaded rate | 🟠 | **PS2** | overhead → 1.0× |
| P1-14 org-overhead on superlinear COCOMO | 🟠 | **PS2** | team size → schedule only |
| P1-15 unfalsifiable 4.6–5.1× headline span | 🔴 | **PS3** | single point + ×0.5–×2.0 sourced band |
| P1-16 team-of-N absurd utilization | 🟠 | **PS7** | Tdev from software PM; headcount = PM/Tdev; suppress <25% util |
| P1-17 fixed calendar/activity split, false precision | ⚪ | **PS7** | range + labels (low; not a Medium+ blocker) |
| P1-18 undisclosed COI + self-flattering example | 🟠 | **PS8** | disclosure + neutral code-dominated example |
| P1-19 sub-2-KLOC out-of-domain precise figures | 🟠 | **PS6** | OUT_OF_DOMAIN → order-of-magnitude only; AI ratio suppressed |
| P1-20 unreachable E=1.26 / Simple below Nominal | 🟡 | **PS6** | E buckets 1.10 / 1.16 / 1.226 |

### P1-2 — override as a corroborated upper bound
- Compute signals/`computed` tier **even when an override tag is present**. Effective tier =
  `min(declared, computed + 1)` (an author may claim at most one tier above the measured
  evidence). EQUIV = `round(lines × mult(effective) / 1000)`, **no floor** (PS3 removed it),
  **immune to git-revision** (the whole git step is removed by P1-4 anyway).
- The IE table marks override rows: tier value annotated `(self-declared, capped at
  measured+1)`; report text notes "N file(s) used an author-declared tier (corroborated cap)."
- Still grep-parsed deterministically (never model-interpreted) — consistent with the
  untrusted-DATA Execution Rule. Reconciliation note added there.

### P1-3 — remove the short-file floor
- Delete every `EQUIV=150 / FLOOR=Yes` site (main path; the override path was already exempt;
  the git-revision recompute path is deleted with P1-4). EQUIV is always
  `round(lines × mult / 1000)`. Drop the `Floor` column from `TIER_DETAIL` and the report, and
  the `*`-for-floored-files note. Round-to-nearest already prevents a dense tiny file from
  truncating to zero (e.g., 2-line T4 → 6), so no proportional floor is needed.

### P1-4 — remove git-revision adjustment
- Delete the entire "Git Revision History Signal" subsection and the in-block git-revision
  loop. Files are classified purely by the (now stuffing-resistant) signal model + override.
  Churn-quality proxies (distinct authors / net substantive lines, demote-only) = P2. Note in
  methodology that revision count is intentionally **not** used (it rewards churn and is
  farmable).

---

## 2. Sites to edit (so nothing is half-applied)

- **`skill/SKILL.md`:** frontmatter description (already reproduction-cost); Canonical
  Reference Lists (`SOURCE_EXTENSIONS`, `SRC_EXTS_FIND`, `SRC_EXTS_GREP`, `SOURCE_EXT_RE` ×2)
  → language expansion (P1-11); Phase 0 unchanged except any new flag echoes; Phase 1a cloc &
  wc paths (ext lists, `.m` sniff); Phase 2 all 8 factors → domain probes + intensity +
  archetype floor (PS5); Phase 1.5 spec → new signal model (PS4), override (P1-2), remove
  floor (P1-3) & git-revision (P1-4); Step 3.1 (KLOC, OUT_OF_DOMAIN); Step 3.3 (E buckets,
  PS6); Step 3.6 (single COCOMO pass; Tdev from software PM, PS7); Step 3.6b (massive
  simplification — remove dedup/ADJUSTED/manifest/second-pass; separate IE; PS1); Step 3.7 (FP
  table P1-11; IE_FP separate); Step 3.8 (remove Low/Mid/High headline driver; PS3 band);
  Phase 4 (overhead→1.0, rate-sensitivity table, PS2/PS3); Phase 5 report template (IE
  separate section, code-only headline, point+band, OUT_OF_DOMAIN OOM rendering, COI
  disclosure, NON_ENGLISH warn, headcount/utilization, calendar range); Methodology bullets
  (overhead, IE-separate, accuracy band, E range, revision-not-used, COI); Execution Rules
  (override reconciliation; remove dedup/floor references); Constraints unchanged.
- **`README.md`:** reproduction-cost wording already done; update "what it produces" (IE
  separate, no overhead, point+band), team-profile line (no overhead), COI disclosure near the
  example link, link the new neutral example, "how it works" steps (overhead removed, IE
  separate).
- **`examples/sample-report.md`:** regenerate via **A17** (copy shipped files + real `.git`
  into a temp dir; scope = shipped tool; AI arg `"3 hours with Claude"`). Now also regenerate
  the **PDF** (pandoc+xelatex present).
- **`examples/calibration-codebase/` + `examples/sample-report-codebase.md`:** new neutral
  example (PS8).

---

## 3. Test plan (against THIS repo — cloc path is primary here; wc path also exercised)

1. **Static audit:** grep SKILL.md for removed constructs (`ADJUSTED_LOC`,
   `DEDUP_LINES_SUBTRACTED`, `phase1a-manifest`, `FLOOR=Yes`, `git revision`, `Overhead
   Multiplier` ≠ 1.0, `Conservative`/`Premium` headline tiers, `IE_HOURS_FOR_TOTAL` summed into
   headline). Confirm `SOURCE_EXTENSIONS` and every inlined list are in sync (single-source
   audit). Confirm E buckets are 1.10/1.16/1.226 everywhere.
2. **Anti-gaming proof (PS4):** run the new signal `awk` on (a) 100 lines plain prose, (b) the
   same padded with trigger words per line, (c) the same re-wrapped one-keyword-per-line,
   (d) a 5-line all-keyword stub. Assert: (a)=T1, (b)=T1 (not T4), (c) identical tier to (b)
   (wrap-invariant), (d) demoted by the anomaly guard. Record the locked thresholds.
3. **Override (P1-2):** a file with `<!-- intellectual-effort-tier: 4 -->` over low-signal
   content → effective tier = computed+1 (not 4); a genuinely T3 file with declared 4 → T4.
   Both surfaced as self-declared.
4. **Complexity domain-fairness (PS5):** craft a tiny numerical/concurrency C file (no web
   idioms) → relevant factors score >1 via the domain probe (not auto-1). A `.jl`/`.sol`/`.cc`
   file is counted in LOC and FP (P1-11). `.m` sniff picks MATLAB vs Obj-C correctly.
5. **Economics (PS2/PS3):** cost = hours × rate (no overhead); profiles differ only by rate;
   headline = one point + ×0.5–×2.0 band; no Conservative/Premium cherry-pick.
6. **Out-of-domain (PS6):** this repo (KLOC 0.029, 1 contributor) → OUT_OF_DOMAIN → headline
   rendered order-of-magnitude; AI ratio suppressed; E uses the new buckets.
7. **IE separation (PS1):** the consolidated block runs end-to-end (cloc + wc), writes nothing
   into the repo, tmpdir cleaned; IE reported separately; headline excludes IE; no dedup/second
   pass remain; CONFIG_ONLY still descriptive-only.
8. **End-to-end numbers:** compute the full self-report by hand-running the bash + documented
   formulas; assert internal consistency (PM↔hours, table↔prose, headline rate matches the
   profile table, IE %-of-code disclosure correct).
9. **Regenerate** `examples/sample-report.md` (+PDF) via A17 on the pinned shipped snapshot;
   verify every cell is reproducible and the headline is code-only with IE separate.
10. **Neutral example (PS8):** generate `examples/sample-report-codebase.md` on the new fixture
    (a real code path: cloc counts actual source; not OUT_OF_DOMAIN if ≥2 KLOC, else labeled).
11. **No Medium+ remaining** per the implementation red-team workflow.

---

## 4. Risks / open decisions (for the plan red-team to pressure-test)

- **R1 (KLOC^E clamp deviation):** PS6 deliberately does **not** clamp the KLOC base to ≥1
  (would over-inflate sub-KLOC repos); it relies on OUT_OF_DOMAIN OOM-only output to make the
  contained inversion immaterial. Red-team must confirm no emitted figure is corrupted and that
  this is more honest than the literal clamp.
- **R2 (signal-threshold calibration):** new density/diversity thresholds are calibrated
  empirically (test step 2). Risk: over-fit to this repo. Mitigation: calibrate against crafted
  generic fixtures too; record locked values + rationale.
- **R3 (IE rate still COCOMO-derived):** P1-6's full decoupling is P2; risk that a separate IE
  line using the code-calibrated hours/KLOC is still mildly misleading. Mitigation: heavy
  caveat + %-of-code disclosure + "least-grounded part" labeling.
- **R4 (neutral example honesty):** we cannot claim an "independently-known build cost"
  (no network / no third-party repo). Mitigation: ship a *code-dominated* neutral contrast,
  explicitly disclaiming any market-price claim. Red-team to confirm this satisfies P1-18's
  intent (calibrate against a non-self case) without overclaiming.
- **R5 (scope vs P2):** several findings have a deeper P2 fix; risk of under-fixing a Medium+.
  Each contained fix above is a *real* behavior change (not a deferral) for every 🔴/🟠; only
  ⚪/some 🟡 depth aspects are deferred, and those are explicitly labeled.
- **R6 (self-referential sample):** editing SKILL.md changes the sample's numbers; MUST
  regenerate via A17 from the frozen file after all edits (see [[sample-report-is-self-referential]]).

---

## 5. Red-team Round 1 — Amendments (AUTHORITATIVE; supersede any conflicting text above)

A 6-lens adversarial review (37 findings; each Medium+ independently refute-verified) confirmed
**23 Medium+** defects. They cluster into 8 amendments below. All were validated in a `/tmp`
prototype lab before being locked here (the signal model was empirically run on plain/padded/
wrapped/stub/boilerplate/structured/rubric/README/SKILL fixtures + the crafted attacks).

### A1 — IE signal model: richness+breadth+support tier gate, **token-based EQUIV**, LOCKED thresholds *(closes findings 1, 2, 3, 13 — the 🔴 P1-1 core)*

The PS4 *density-over-tokens* tier model is **superseded** by a richness model (density-as-
primary crushed genuine large docs to T1 and a distinct-lemma stuffer still passed). Locked,
validated model (one `awk` pass, mawk/gawk/BSD-portable — only `tolower/index/split/gsub/
for-in/user-funcs`):

- **Tokenize:** `tolower($0)`, split on `[^a-z0-9]+`. `W` = total tokens, `DWc` = distinct
  tokens. Match lemmas as **whole tokens / adjacent-token phrases** via
  `index(" "norm" ", " "lemma" ")` (so EOL/sentence-initial/terse keywords all match; wrap-
  and case-invariant). STRUCTURE + `{...}`/`<...>` placeholders detected on the **raw line**.
- **Per-family distinct, capped richness:** for each family, count **distinct** lemmas present
  (repetition adds nothing), cap each at `CAP=8` (STRUCTURE capped at `SCAP=5`).
  `R = Σ capped-distinct`. 6 families: COND, CONS, DOM, INST, EXAM, STRUCT.
- **Breadth** `F` = families with ≥1 distinct lemma.
- **Support** `support = DWc − distinct_trigger_tokens` = distinct **non-trigger** vocabulary
  (P1-1c): repeated/identical filler → low support; genuine prose → high support.
- **Anomaly backstop** `kf = KO/W` (raw trigger-token fraction); `kf > 0.50` ⇒ demote one tier
  (floor T1). (The `ur<0.2` guard is **dropped** — Heaps' law makes long genuine docs low-`ur`,
  a false positive that wrongly demoted SKILL.md.)
- **LOCKED tier gates:** T4: `R≥38 & F≥5 & support≥50`; T3: `R≥18 & F≥4 & support≥25`;
  T2: `R≥8 & F≥2`; else T1. T0 unchanged (auto-gen / lock / license / trivial README).
- **EQUIV is TOKEN-BASED, not line-based** *(the end-to-end fix for finding 1/13)*:
  `EQUIV = round( (W / TPL) × mult / 1000 )`, `TPL=9` tokens/line, `mult` permille
  (T1=100, T2=500, T3=1500, T4=3000). Physical line count is **never** used for EQUIV. This
  makes credit **layout-invariant and content-proportional**: padding, one-token-per-line, and
  file-splitting cannot inflate it; larger credit requires genuinely more content.
  For normally-wrapped prose (`≈9 tok/line`) token-EQUIV ≈ the old line-EQUIV, so honest docs
  are undisturbed.

**Validated anti-gaming results (locked into test step 2):** plain→T1; keyword-padded→T1;
re-wrapped(1-kw/line)→identical tier to padded (wrap-invariant); all-keyword stub→T1
(kf demote); boilerplate config→T1; structured config→T2; README→T2; rubric→T3; this repo's
P1 findings doc→T3; SKILL.md→T4. **Distinct-filler one-token-per-line attack** (513 tokens,
70 lemmas + distinct filler): reaches at most T3 (support/cap held it under T4) and yields
**EQUIV_tok = 86 whether one-token-per-line or wrapped** (line-based would have been 770);
its **10-way split sums to 18, not 86** (splitting *reduces* credit). The anti-gaming property
is now: *cheap layout/padding/repetition/splitting tricks yield nothing; high credit requires
writing a large, genuinely diverse document* — and IE is a separate, caveated, non-headline
line regardless. The locked lemma lists (post-tokenization token sequences, e.g. `anti pattern`,
`trade off`, `e g`, `at least`) go verbatim into SKILL.md.

### A2 — Re-wire the AI Speed Comparison AND Effort Allocation to the code-only point; drop embedded overhead *(closes findings 6, 11, 12, 16, 17, 19, 21, 22)*

PS1/PS3 delete "Combined Base Effort", the Low/Mid/High Effort Range, and the "Mid" column —
which orphaned two report tables. Binding fixes (added to the §2 edit-site list):
- **AI Speed Comparison (SKILL.md ~1342–1372):** human baseline = the **code-only point
  person-hours** (the same Source-Code-Effort hours that drive the headline) — drop every
  "Mid"/"combined" token. AI cost cell = `parsed_hours × $125` (**drop the `×1.35` overhead**,
  PS2). Ratio = `point_hours / parsed_hours`. Under OUT_OF_DOMAIN the ratio is shown
  **order-of-magnitude** (per A4), not suppressed, so the self-example still illustrates it.
- **Effort Allocation Breakdown (SKILL.md ~1088–1098, 1310–1318):** activity hours =
  `code-only point person-hours × {55/20/12/8/5}%`; cost column = at the **$125 point rate, no
  overhead**. Relabel the 55/20/12/8/5 split as a **generic industry default (cited)**, not a
  measured split (PS7/P1-17). Remove "for the Mid estimate" wording.

### A3 — Neutral calibration example must be IN-domain (≥2 KLOC, ≥2 authors) *(closes findings 9, 20)*

A 300–500 LOC single-author fixture trips OUT_OF_DOMAIN (KLOC<2 **and** ≤1 contributor) → it
would render OOM-only, defeating its calibration purpose. **Spec:** the fixture is a genuine,
idiomatic **≥2 KLOC** multi-file program with a real `.git` carrying **≥2 author identities**
and ≥3 commits, so it is firmly in-domain and exercises the full precise headline + cost
tables + a real AI ratio. It is **code-dominated** (code ≫ prose) to contrast the prose-heavy
self-example. Chosen fixture: a small **stack-VM + assembler + lexer/parser + REPL** (Python),
which *also* doubles as the PS5 domain-probe test (parser/bytecode/state-machine signals, zero
web idioms). Still labeled "no external market price is claimed." Test step 10 updated to
assert it is **not** OUT_OF_DOMAIN.

### A4 — Pin OUT_OF_DOMAIN rendering, the IE %-of-code disclosure, the AI ratio, and the prose-dominance trigger *(closes findings 5, 10, 18, 23)*

- **Prose-dominance trigger (finding 23):** `OUT_OF_DOMAIN = (Effective KLOC < 2) OR
  (contributors ≤ 1) OR (Source LOC < 20% of TOTAL_COUNTED_LOC **AND** Effective KLOC < 2)`.
  `TOTAL_COUNTED_LOC = SOURCE_CODE_LOC + CONFIG_MARKUP_LOC + OTHER_NONSOURCE_LOC` (defined
  explicitly). So a large, well-documented code repo (≥2 KLOC source) is **never** suppressed
  for shipping lots of docs; only genuinely small *and* prose-dominated repos trip it.
- **OOM rendering (finding 5):** when OUT_OF_DOMAIN, render the **point** to **1 significant
  figure** (`$500 → "~$500"`, `$1,240 → "~$1,000"`, round-half-up on the leading digit), and
  render the **band** as the decade bracket `[10^floor(log10(point×0.5)), 10^ceil(log10(point×2))]`
  (e.g. point $1,200 → band "$1,000–$10,000"). Cost-by-profile and headline both use this.
  Worked: code point 4 h × $125 = $500 → headline "~$500 (order-of-magnitude; $100–$1,000)".
- **IE %-of-code disclosure (finding 18):** in-domain → `round(IE_hours / code_hours × 100)%`
  (1 sig fig if >1000%). Under OUT_OF_DOMAIN → render **qualitatively** ("IE effort ≫ code
  effort (heuristic; both order-of-magnitude)"), never a 3-sig-fig %. Under CONFIG_ONLY the
  denominator is the config-derived COCOMO hours; if those are ~0, **omit** the ratio.
- **AI ratio under OUT_OF_DOMAIN (finding 10):** show it as a **bucketed order-of-magnitude
  multiple** ("~100× (order-of-magnitude; both inputs unverified)"), not full suppression — so
  the A17-regenerated flagship still demonstrates the section. P1-19's "suppress the AI
  multiplier" is thus realized as "render order-of-magnitude," consistent with all other OOM
  output.

### A5 — E-bucket arithmetic made formula-consistent *(closes finding 4)*

`0.91 + 0.01×31 = 1.22`, not 1.226. Locked, all formula-exact and within COCOMO II's range
(all-Nominal Σ≈18.97→E≈1.10; max Σ≈31.62→E≈1.226): **Simple SF=19 → E=1.10**, **Moderate
SF=25 → E=1.16**, **Complex SF=31 → E=1.22**. Schedule `F = 0.28 + 0.2×(E−0.91)` recomputed
from these. Update Step 3.3 + methodology.

### A6 — Regex-safe extensions + lemma normalization *(closes findings 7, 8)*

- Drop the rare `.c++`/`.h++` from the source set (they break unescaped regex); keep the
  full real-world C++ set `.cc .cxx .cpp .hpp .hh .hxx .h`. Any genuinely needed `+` in a
  regex is written `\+`; `*` extensions stay only in `find -name`/cloc `--include` globs.
- Lemma lists are specified in **post-tokenization form** (multi-word lemmas as adjacent
  tokens: `anti pattern`, `trade off`, `failure mode`, `at least`, `e g`); `{...}`/`<...>`
  placeholder and STRUCTURE detection run on the **raw line**, not the tokenized stream.

### A7 — P1-10 intensity is a real re-weighting, not an additive bump *(closes finding 14)*

For each grep factor, map **matches-per-matching-file** onto a 1–5 `intensity_score`, then
`factor_score = MAX(web_breadth_score, domain_breadth_score, intensity_score)`. A deep 10-file
numerical core can reach 5 on intensity alone; a 200-file shallow web app is held down by low
intensity. Test asserts the deep-core ≥ shallow-app ordering.

### A8 — Override × non-English reconciliation *(closes finding 15)*

`effective_tier = min(declared, computed+1)` normally; **exempt from the +1 cap when
`NON_ENGLISH` is set** (English-keyword signals are unreliable there, so the author override is
honored up to its declared tier — still surfaced as "self-declared, not measured"). Update the
override wording in SKILL.md and the P1-12 escape-hatch note so they no longer contradict.

### A9 — Test-plan additions (fold into §3)

Add: (2b') distinct-filler dense doc + (2f') one-token-per-line + (2g') 10-way split + (2h')
fake-markdown-structure doc — assert each is T1/T2 **or**, if it reaches T3, that EQUIV_tok is
content-bounded and split-invariant (the locked A1 results). (4b') a `.cc`/`.jl`/`.sol` file is
counted as source on both paths; `.m` sniff. (5b') AI cost has no `×1.35`; AI baseline is
code-only. (6b') OUT_OF_DOMAIN OOM rendering matches A4's worked example. (10b') the neutral
fixture is in-domain and shows precise tables + a real AI ratio.

---

## 6. Red-team Round 2 — Amendments (AUTHORITATIVE; supersede any conflicting text above, incl. Round 1)

Round 2 (5 lenses; each Medium+ refute-verified) confirmed **19 Medium+**, which de-duplicate
to ~10 distinct fixes (4 were the same A4 decade-band example bug; 2 the same E=1.226-vs-1.22
audit bug). All code-affecting fixes were re-validated in the `/tmp` lab before locking here.

### A10 — EQUIV is content-bounded AND support-capped; correct A1's overstated "at most T3" *(closes findings 1, 19 — the P1-1 residual)*

A1's token-EQUIV is linear in `W`, and the tier gates are fixed floors, so a one-time seed could
clear a gate and then non-trigger padding inflated `W` (hence IE hours/FP/%). Also the documented
distinct-filler attack actually reaches **T4** (not "at most T3"). **Locked fix:** cap credited
tokens by the genuine, hard-to-pad non-trigger vocabulary `support`:
```
credW = min(W, KSUP × support)          # KSUP = 15
EQUIV = round( (credW / TPL) × mult / 1000 )   # TPL = 9
```
Validated (lab): genuine docs are **uncapped** (all have `W < 15×support`: SKILL W/support≈8.0,
README≈2.3, rubric≈1.7) so their EQUIV is unchanged; the **repetition-padding** attack
(seed + `data`×5000) → support=1 → `credW=15` → **EQUIV=1** (and the support gate also demotes
it to T2); the **distinct-padding** attack only earns credit *proportional to genuinely
producing thousands of distinct words*, lands at most T3 for a seed-sized lemma set, and is a
**separate, off-headline, caveated** figure that any reader sees enumerated in the IE key-files.
A1's "at most T3 / EQUIV 86" wording is **corrected**: the distinct-filler attack *may* reach
T4, but EQUIV is content-proportional and support-capped, so cheap layout/padding/repetition/
split/seed-then-pad tricks yield ≈0; only genuine large *and* lexically-diverse writing earns
large credit, and never touches the cost headline. Fully distinguishing "diverse but
meaningless" text from genuine prose is **P2**. Add `pad_rep`/`pad_distinct` fixtures to test
step 2 with these locked expectations.

### A11 — NON_ENGLISH override exemption is per-FILE and content-gated *(closes finding 2)*

A8's repo-wide exemption let an author trip the repo-level NON_ENGLISH flag (bulk non-English
filler) then self-declare T4 on *any* file with no corroboration. **Locked fix:** the override
may exceed `computed+1` **only when the declaring file is itself** predominantly non-ASCII/
non-English **and** non-trivial (≥ ~50 tokens). An English or empty file in a NON_ENGLISH repo
stays bound by `min(declared, computed+1)`. (Override remains grep-parsed, floor-free, and
surfaced as "self-declared, not measured".)

### A12 — Lemma families are mutually disjoint (no cross-family double-firing) *(closes finding 3)*

Each token/phrase belongs to **exactly one** family for both `R` and `F`. Locked
de-duplications: remove standalone `case` from COND (the conditional sense is covered by
`if/when/unless`; keep `edge case` in DOM); remove `format` from EXAM (keep it in INST). The
verbatim locked lemma lists going into SKILL.md carry this; state explicitly "a token
contributes to at most one family."

### A13 — Decade band = the point's OWN decade (drop ×0.5/×2); fix the worked examples *(closes findings 4, 5, 9, 10)*

A4's band formula `[10^floor(log10(point×0.5)), 10^ceil(log10(point×2))]` contradicted its own
worked example and was discontinuous. **Locked, validated (lab `decade_lo`):**
`lo = 10^floor(log10(point))` (exact integer loop, no `log/exp` FP error), `hi = lo × 10`.
Always exactly one decade; 1-sig-fig point via round-half-up on the leading digit. Worked:
`$500 → ~$500 ($100–$1,000)`; `$1,200 → ~$1,000 ($1,000–$10,000)`; `$4,500 → ~$5,000
($1,000–$10,000)`; `$95 → ~$100 ($10–$100)`. (FP note: compute the decade with a pure
`while(m*10<=p) m*=10` integer loop, **not** `exp(floor(log10))`, which mis-rounds $4,500→$4,000
and $95→$90.)

### A14 — E = 1.10 / 1.16 / 1.22 everywhere (formula-consistent) *(closes findings 8, 12)*

`0.91 + 0.01×31 = 1.22`. Update **all** sites to 1.22: test step 1 (was "1.226 everywhere"),
the §1 table row P1-20, and PS6's bullet. Keep `E_max ≈ 1.226 at Σ≈31.62` only as the stated
theoretical range ceiling (it is correct as a ceiling, wrong as the emitted Complex value).

### A15 — §1 P1-2 / P1-3 use the A10 token-EQUIV (no line-based formula anywhere) *(closes finding 11)*

Replace the line-based `round(lines × mult / 1000)` in §1 P1-2 (override) and §1 P1-3 with
"EQUIV per A10 (token-based, support-capped)". The override path therefore also resists
line-padding. No EQUIV site in the plan or SKILL.md remains line-based.

### A16 — Intensity (P1-10) re-weighting: locked thresholds + repetition-safe + per-file cap *(closes finding 13)*

For the **5 grep-based factors** (Integrations, Data, Auth, Observability, Security):
`intensity = total_matching_LINES / matching_files` (`grep -c` counts matching *lines*, so
repeating a token on one line cannot inflate it), with each file's matching-line count **capped
at 50** (one giant file cannot dominate). Map `intensity → 1–5`: `≤1→1, ≤2→2, ≤4→3, ≤8→4, >8→5`.
`factor_score = clamp(1, 5, round( (MAX(web_breadth, domain_breadth) + intensity_score) / 2 ))`.
The find-count factors (Testing, Infra, Docs) keep breadth scoring (intensity is not meaningful
for artifact counts). Test asserts a deep 10-file core out-scores a 200-file shallow web app.

### A17′ — NON_ENGLISH detection is script-independent and stated in A1 terms *(closes finding 14)*

The detector triggers when **`R ≈ 0` across all IE candidates AND total candidate tokens are
substantial** (a real, prose-heavy repo with no English signal) — the non-ASCII-fraction
conjunct is **dropped** (A1's tokenizer splits on `[^a-z0-9]+`, so non-ASCII is stripped and
that fraction is ≈0 for every script; the conjunct made the warn unreachable, esp. for
Latin-script languages). Restate the trigger using A1's `R`/`support`, not the superseded `S`.
A11's per-file exemption keys off the **file's own** non-ASCII content (raw bytes), not this
repo flag.

### A18′ — OUT_OF_DOMAIN drops the contributors gate (advisory note only); fixture is git-independent *(closes finding 15)*

A nested real `.git` under `examples/` is committed as a **gitlink** and is **empty on clone**,
so the calibration fixture would have 0 source + 0 contributors → OUT_OF_DOMAIN → defeated.
**Locked fix:** `OUT_OF_DOMAIN = (Effective KLOC < 2) OR (Source LOC < 20% of TOTAL_COUNTED_LOC
AND Effective KLOC < 2)`. The **contributors ≤ 1** clause is **removed from the hard trigger**
(it over-suppressed legitimate solo ≥2-KLOC repos and broke the fixture); single-author is now
an **advisory methodology note** only ("COCOMO assumes multi-person teams; this is single-
author"). The calibration fixture is shipped as **plain source files** (no nested `.git`, ≥2
KLOC, code-dominated) so it is in-domain on any clone; its report is generated A17-style in a
temp dir (with a throwaway multi-author `.git` for the git-context fields) and the method is
documented. `TOTAL_COUNTED_LOC = SOURCE_CODE_LOC + CONFIG_MARKUP_LOC + OTHER_NONSOURCE_LOC`.

### A19′ — Under OUT_OF_DOMAIN, render EVERY figure order-of-magnitude; sub-10h hours rule; AI ratio honesty *(closes findings 6, 7, 16, 17, 18)*

- **OOM scope:** when OUT_OF_DOMAIN, render to 1 sig fig (A13) **all** of: code headline,
  cost-by-profile table, **IE section** (hours/PM/FP/$), **AI Speed Comparison** table (human
  Build-Time hours, both Cost cells) and the **AI ratio**. No figure (least of all the
  least-grounded IE numbers) is shown more precisely than the code headline, so the
  "order-of-magnitude only" banner is truthful.
- **Sub-10h display:** person-hours `< 10` render as `≈N hours` (1 sig fig), never the
  nearest-10 `0`. The headline dollar and AI ratio use the **unrounded** hours for arithmetic
  (so 3.88 h × $125 ≈ $485 → `~$500`, not `$0`).
- **AI ratio:** bucket via `10^round(log10(ratio))`. On the prose-dominated self-report the
  code-only baseline (~4 h) vs a 3 h AI self-report gives ratio ≈ 1× — this is the **correct,
  honest** result of D1 (IE is excluded from the baseline); the report says so plainly
  ("at this scale the human and AI times are comparable; IE is excluded by design"). The
  **in-domain calibration fixture** (A18′) is the meaningful AI-ratio demonstration. Update the
  A4 worked example (it cited a stale "~100×") and test steps 5b'/9 to expect the ~1× self
  value.

---

## 7. Red-team Round 3 — Amendments (AUTHORITATIVE; supersede any conflicting text above)

Round 3 (4 lenses) confirmed **8 Medium+** (down from 19 → 8; trend 23→19→8). None corrupt the
code-only dollar headline; all are off-headline (IE/non-English), OOM-rendering, or
methodology-text issues. They de-duplicate to 6 fixes.

### A20 — Script-independent content tokenization for W/support/EQUIV (the non-English cluster) *(closes findings 1, 6, 8)*

A1's `[a-z0-9]` tokenizer (correct for English lemma matching) zeroes `W` for non-Latin
scripts, so A10's `EQUIV = round((min(W,15×support)/9)×mult/1000)` collapses to **0** for
Russian/CJK/etc. — the override escape hatch granted a tier but credited nothing. **Locked
two-tokenizer split:**
- **Signal/lemma detection** (`R`, `F`, `KO`, trigger lemmas) stays on the lowercased
  `[a-z0-9]`-normalized line (English keywords). Unchanged.
- **Content volume** `W`, distinct vocabulary `DWc`, and `support` are counted on
  **whitespace-split tokens** (script-independent; strip surrounding ASCII punctuation, keep
  any inner bytes), with `W = max(whitespace_tokens, line_count)` so any non-empty file has
  `W ≥ 1`. `EQUIV` and the support-cap use this `W`. Validated (lab): Russian `[a-z0-9]`-W=0 →
  whitespace-W=18; German works either way; CJK (no spaces) floors to line count.
- **A11 per-file override exemption** is re-keyed: a file may exceed `computed+1` when **its own
  English signal `R ≈ 0` AND its content size `W ≥ 50`** (drop the "predominantly non-ASCII raw
  bytes" requirement and the undefined "≥50 tokens" unit). This is **reachable for Latin-script
  non-English** (a German doc: `R≈0`, `W≥50` → declared tier honored, EQUIV non-zero). Anti-
  gaming preserved: an English or trivial file (`R>0` or `W<50`) in a NON_ENGLISH repo still
  cannot self-declare above `computed+1`.
- **Documented residual (P2):** non-space-separated scripts (CJK) are approximated by line
  count; precise Unicode word segmentation + localized keyword sets are P2. The NON_ENGLISH
  loud-warning (A17′) discloses the biased-low estimate regardless.

### A21 — Sub-10h person-months display; suspend the paired rule under OOM *(closes finding 2)*

A19′ fixed sub-10h **hours** ("≈N hours") but the Step 3.6 paired rule
(`PM_display = round(hours_display/152, 1)`) still printed `0.0` PM beside it. **Locked:** under
OUT_OF_DOMAIN (or whenever hours render via the "≈N hours" path) the paired-reconciliation rule
is **suspended**; person-months renders to 1 significant figure from the **unrounded** PM (e.g.
`0.03`), or as `<0.1 person-months` — never a bare `0.0` next to non-zero hours.

### A22 — OUT_OF_DOMAIN simplified to `(KLOC < 2) OR CONFIG_ONLY`; prose-dominance is subsumed *(closes finding 3)*

A18′'s second clause `(Source LOC < 20% AND KLOC < 2)` is a strict subset of `KLOC < 2`
(Boolean-dead). **Locked:** `OUT_OF_DOMAIN = (Effective KLOC < 2) OR CONFIG_ONLY`. P1-19's
prose-dominance concern is now **subsumed by the code-only headline (D1)**: a prose-dominated
repo has `<2 KLOC` of code → already suppressed; a repo with `≥2 KLOC` code has a *valid
code-only headline regardless of how much documentation it ships* (Round-2 finding 23 — do not
over-suppress). `CONFIG_ONLY` (zero source code) is always out of the application-software
domain → OOM. Single-author stays an **advisory note** (A18′), not a trigger. Reconcile the A4
"≥2 KLOC source is never suppressed" wording with this.

### A23 — Rewrite the "Bias direction (honest)" methodology bullet for the new model *(closes finding 4)*

SKILL.md's bias-direction bullet still names overhead (≤1.65×), scenario tiers (0.6/1.6×), and
IE-in-headline (≤3.0×) — all removed by PS1/PS2/PS3. **Add it to §2's methodology edit list**
and rewrite: "No overhead multiplier, no cherry-picked scenario tiers. The headline is a single
mid-rate ($125), code-only point with a symmetric ×0.5–×2.0 parametric band. Intellectual-
effort credit is reported **separately and never enters the headline**. Honest levers: the band
top (×2.0) is the only upward lever and the band bottom (×0.5) the only downward one; the point
is neither conservative nor inflated."

### A24 — A19′ OOM scope includes Schedule (Tdev) and Calendar Time *(closes finding 5)*

Add Schedule (Tdev) and Calendar Time to the OUT_OF_DOMAIN OOM render set: render months to
1 significant figure / qualitatively (e.g. "~1 month; schedule dominates at this size"), so no
schedule figure is shown more precisely than the OOM headline. (Month OOM rule: 1 sig fig,
round-half-up, same as the dollar/hours rule.)

### A25 — Specify the calibration fixture's AI argument *(closes finding 7)*

The in-domain fixture's report (PS8/A18′) is generated with an explicit AI arg
**`"8 hours with Claude"`** (a plausible value for the ~2 KLOC fixture) so the AI Speed
Comparison section actually renders and is the **meaningful** (in-domain, precise) AI-ratio
demonstration A19′ designates, satisfying test step 10b'. The self-example keeps
`"3 hours with Claude"` (its ratio is the honest ~1× per A19′).

---

## 8. Convergence note

Adversarial trajectory on the plan: **R1 23 → R2 19 → R3 8**, each round's findings narrower
and lower-blast-radius than the last (R3 = zero headline-affecting defects; all off-headline IE/
non-English, OOM-rendering, or methodology-text). The remaining fixes (A20–A25) are localized
and validated. A Round-4 confirmation pass is run; if it surfaces only ≤Low items the plan is
declared converged and implementation proceeds. **The four locked user decisions and the
code-only headline are stable across all three rounds — no amendment has reopened them.**

## 9. Red-team Round 4 — Amendments (AUTHORITATIVE; supersede any conflicting text above)

Round 4 (3 lenses) confirmed **3 Medium+**, **all self-inflicted by A20** (my non-English fix)
and all off-headline (IE only; the code-only dollar headline is untouched). Root insight:
**without a language detector (P2), no deterministic gate distinguishes bland English filler
(`R≈0`, ~0% non-ASCII) from Latin-script non-English (`R≈0`, ~few% non-ASCII)** — so any
"non-English override exemption" is either gameable by English filler (drop the non-ASCII gate)
or excludes Latin-script non-English (keep it). The exemption is therefore unsound in P1 and is
**removed**. The two fixes:

### A26 — Remove the non-English override exemption (uniform cap); clamp support/credW non-negative *(closes all 3 Round-4 findings)*

- **Override is uniformly `effective_tier = min(declared, computed+1)` for ALL files.** The
  per-file NON_ENGLISH exemption (A8 "exempt when NON_ENGLISH", A11/A17′/A20's per-file
  carve-out) is **deleted** — it let English lemma-free filler (`R≈0`, `W≥50`) self-declare T4
  (Round-4 findings 1, 3) and could not be made script-fair without a language detector. The
  override stays grep-parsed, surfaced as "self-declared, not measured", and now corroboration-
  capped with **no exemption**. *(Closes findings 1, 3 by eliminating the attack surface
  entirely; the override can never exceed the measured tier by more than one.)*
- **P1-12 non-English support is therefore: (a) the loud `NON_ENGLISH` warning (A17′) that the
  estimate is biased-low, and (b) the language-agnostic STRUCTURE family.** Full non-English
  credit (localized keyword sets / Unicode-aware language detection) is **explicitly P2**. This
  still satisfies P1-12's stated fix ("warn loudly … or fall back to language-agnostic
  structural signals"); the override was always a secondary, unsound extra. Correct A20's false
  rationale sentence (an English file does NOT always have `R>0`).
- **Keep A20's two-tokenizer split** (whitespace `W`/`DWc`/`support` for content volume; `[a-z0-9]`
  for lemma detection) so non-English files still earn **non-zero** EQUIV at their (capped)
  tier. But the cross-tokenizer subtraction can go negative, so **clamp**:
  `support = max(0, DWc − distinct_trigger_lemmas_present)` and
  `credW = max(0, min(W, 15 × support))`. `distinct_trigger_lemmas_present` is the count of
  distinct English trigger lemmas detected (bounded ≤ ~70); the clamp guarantees `support ≥ 0`
  and `EQUIV ≥ 0` even for terse slash-joined trigger lines like `if/when/unless/must`. *(Closes
  finding 2.)* Add a terse slash-joined-trigger fixture and a Russian/German fixture to test
  step 2 asserting `support ≥ 0`, `EQUIV ≥ 0`, and (for the non-English files) `EQUIV > 0`.

---

## 10. Convergence — plan is FINAL

Adversarial trajectory: **R1 23 → R2 19 → R3 8 → R4 3**, monotonically decreasing, with the
blast radius shrinking each round (R3–R4 = zero headline-affecting defects; every remaining
item was off-headline IE / non-English / OOM-rendering / methodology-text). Round-4's 3 were all
introduced by a single Round-3 amendment (A20) and are closed by **A26's simplification**
(removing the unsound exemption *reduces* attack surface and code paths rather than adding any),
plus two standard `max(0,…)` clamps. No new logic is introduced that could spawn a fresh class
of defect, and the four locked user decisions + the code-only headline have been stable across
all four rounds. **The plan is declared converged; implementation proceeds against the full
contract (body + A1–A9 + A10–A19′ + A20–A25 + A26).**

A consolidated "locked values" cheat-sheet for implementation:
- **IE signal model:** lemmas on lowercased `[a-z0-9]`; `R`=Σ per-family distinct (cap 8;
  STRUCT cap 5); `F`=families present; content `W`/`DWc`/`support` on whitespace tokens with
  `W=max(whitespace_tokens, lines)`; `support=max(0, DWc − distinct_trigger_lemmas)`;
  `kf=KO/W`. Tiers: **T4** `R≥38 & F≥5 & support≥50`; **T3** `R≥18 & F≥4 & support≥25`;
  **T2** `R≥8 & F≥2`; else **T1**; `kf>0.5` demotes one tier; T0 = auto-gen/lock/license/trivial
  README. `EQUIV=round((credW/9)×mult/1000)`, `credW=max(0, min(W, 15×support))`,
  mult permille {T1 100, T2 500, T3 1500, T4 3000}. Override: `min(declared, computed+1)`,
  no exemption, no floor. **No dedup, no git-revision, no short-file floor.**
- **IE candidates:** non-source files only (exclude every `SOURCE_EXTENSIONS` member incl.
  `.tf/.hcl/.sql/.sh`). IE is reported **separately**, never in the dollar headline.
- **Complexity:** grep factors `score = clamp(1,5, round((MAX(web_breadth, domain_breadth) +
  intensity)/2))`, intensity from matches-per-file (per-file cap 50): ≤1→1,≤2→2,≤4→3,≤8→4,>8→5;
  find-count factors unchanged. Domain probes: math/concurrency/low-level/parser/state-machine.
- **E buckets:** Simple 1.10, Moderate 1.16, Complex 1.22. Schedule `F=0.28+0.2(E−0.91)`.
- **Cost:** `Cost = Hours × Rate`, overhead 1.0× all profiles. Headline = code-only point ×
  $125 + symmetric ×0.5–×2.0 parametric band. No Conservative/Premium tiers.
- **OUT_OF_DOMAIN** = `(Effective KLOC < 2) OR CONFIG_ONLY`. When set: render headline,
  cost table, IE section, AI table, AI ratio, **Schedule, Calendar** all order-of-magnitude
  (1 sig fig; decade band `[10^floor(log10 p), ×10]`); sub-10h → "≈N hours" + PM 1 sig fig
  (paired rule suspended); AI ratio bucketed `10^round(log10 ratio)`; the self-report ratio is
  the honest ~1×.
- **Schedule/headcount:** Tdev from code-only PM; headcount = PM/Tdev; suppress "team of N"
  when utilization < 25%; calendar a range; activity split = cited generic default.
- **Examples:** self-report regenerated via A17 (`"3 hours with Claude"`); neutral in-domain
  fixture `examples/calibration-codebase/` (≥2 KLOC, code-dominated, `"8 hours with Claude"`).
- **COI** disclosed in README + report.

---

## 11. Implementation outcome (record)

All 20 P1 findings implemented in `skill/SKILL.md` + `README.md`. `examples/sample-report.md`
regenerated via A17 (shipped-files scope + real `.git`, AI arg `"3 hours with Claude"`) — now an
honest OUT_OF_DOMAIN order-of-magnitude report (code headline ~$500; IE ~600 h in a separate
section; AI ratio ~1×). New `examples/calibration-codebase/` (a genuine ~2 KLOC stacklang
interpreter: lexer/parser/compiler/stack-VM/assembler/REPL, 67 passing tests) + its in-domain
report `examples/sample-report-codebase.md` (headline $93K; Auth/CPLX driven to 5/5 by the parser
**domain probe** — the P1-9 fix demonstrated on a non-self case). `.gitignore` extended for
`__pycache__/` + `*.pyc`.

**Adversarial trajectory (each finding independently refute-verified):**
- Plan red-team: **R1 23 → R2 19 → R3 8 → R4 3 → converged** (each round narrower, lower blast
  radius; R3–R4 = zero headline-affecting defects). Amendments A1–A26.
- Implementation red-team: **round 1 9 Medium+** (1 real bash bug `$KF` undefaulted; intensity
  50-cap not implementable + computed only on the web probe; stale `SRC_EXTS_*`; 2 pending
  deliverables = the two regenerated examples) → all fixed → **final-verification round 3** (2
  real: calibration `__pycache__` inflating the Testing count → wrong Simple/Moderate cascade,
  and Total-Files; 1 false positive: Lean cost cell, where the verifier used the *displayed*
  KLOC 0.03 instead of the full-precision 0.029 the skill computes with — `$400` is correct).
  All real issues fixed; reports recomputed and reconciled.
- Empirically validated in a `/tmp` lab: the anti-gaming signal model against keyword-padding,
  line-wrapping, all-keyword stubs, file-splitting, sophisticated distinct-filler, and
  distinct/repetition padding (token-EQUIV support-capped holds); override corroboration cap;
  English-filler-with-`tier:4` correctly capped; non-English EQUIV non-zero + NON_ENGLISH warn;
  domain probes lifting a non-web parser repo; OOM rendering; both report regenerations; all 19
  SKILL.md bash blocks `bash -n` clean; the consolidated IE block writes nothing into the repo.

**Self-referential caveat** (see [[sample-report-is-self-referential]]): editing `SKILL.md`
changes its line count and therefore `examples/sample-report.md`'s IE numbers — regenerate via
A17 from the frozen file after any change.
