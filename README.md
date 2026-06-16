# cost-estimate

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that analyzes any codebase and produces a cost estimation report using a simplified parametric model based on COCOMO II.

Point it at a repo, get an order-of-magnitude breakdown of what it would cost a human team to **reproduce the current codebase** from scratch — with effort ranges, team profiles, and an optional (illustrative) AI speed comparison.

> ⚠️ This is an automated, order-of-magnitude estimate for curiosity — **not a professional
> appraisal or valuation.** It measures the surviving file snapshot (not historical effort),
> and parametric estimates are commonly off by ±50–100%. Don't use it to set prices or to
> support acquisition/investment/legal decisions.

## What it produces

- **Codebase profile** — languages, LOC (via `cloc` or fallback), git history, tech stack detection
- **8-factor complexity assessment** — external integrations, data layer, auth, testing, infra, error handling, docs, security — each scored 1–5. The grep/find *file counts* are deterministic and map to scores via fixed thresholds; the model then interprets those counts (tier classification, EM mapping, COCOMO math, justifications), so re-runs may yield slightly different scores
- **Parametric effort estimation** — Simplified COCOMO II (A=2.94, Scale Factor-based exponent E in the model's real range, 5 mapped Effort Multipliers), person-months, person-hours, function points — computed on **source code only**
- **Cost** — a single honest **deterministic point** with a **Monte-Carlo P10–P90 band** (10,000 seeded triangular draws over size + productivity; the productivity spread reflects the ~100% mean error of uncalibrated parametric models), shown across 4 team rates ($115–$145/hr). The band is right-skewed (software overruns asymmetrically), so its P50 sits above the point — the **headline is the point, not P50**. **No overhead multiplier** — rates are fully loaded, so team size affects the *schedule*, not the cost
- **Estimator ensemble (cross-checks)** — alongside COCOMO-on-LOC, **structural** size measures (IFPUG Function Points from routes/entities, COSMIC data movements, Use-Case Points) run as **archetype-gated** cross-checks that render **N/A** on non-transactional code (compilers, ML, numerical) rather than a misleading zero — and **never move the headline**. Putnam SLIM is cited but not computed (its productivity parameter is unmeasurable from a snapshot)
- **Measured vs parametric** — when the analyzed dir is the git root with real history, a **git session reconstruction** gives a *measured* effort anchor and an **AI-authorship share** (`Co-Authored-By` trailers) next to the parametric from-scratch number — reported separately, never in the headline; a high AI share flags the "from-scratch human" baseline as increasingly hypothetical
- **Three valuation lenses** — the output is explicitly the **cost approach** (reproduction cost), distinct from value/income and market/comparable; a low-cost artifact can have high value and vice-versa
- **Empirical accuracy bounds** — the methodology states the published accuracy of uncalibrated parametric models (MMRE ≈ 1.0, PRED(25) ≈ 0), so the band is honestly wide
- **Domain-fair complexity** — each of the 8 factors takes `MAX(web-idiom, domain-general)` signals (math/concurrency/low-level/parser/state-machine) plus a depth/intensity term, so compilers, ML, games, embedded, HDL, and numerical code aren't scored "Simple"
- **Intellectual-effort artifacts** — prose/prompt/config artifacts are scored by a **stuffing-resistant** heuristic and reported as a **separate, clearly-labeled line — never folded into the dollar headline**
- **Out-of-domain honesty** — below ~2 KLOC of code (or config-only), figures are rendered **order-of-magnitude only** (1 significant figure), and the band collapses to a single decade bucket — not false-precision tables
- **Optional local calibration** (off by default) — set `COST_ESTIMATE_CORPUS` to accumulate past analyses (outside the repo) for reference-class forecasting; supply a real actual via `COST_ESTIMATE_ACTUAL_HOURS` for a single-datum-capped Bayesian productivity update
- **AI speed comparison** (optional, illustrative) — a self-reported AI build time next to the model's *code-only* human estimate, framed by the METR/DORA/GitClear evidence; both inputs unverified — an anecdote, not a measurement
- **Report output** — Markdown saved **outside the analyzed repo** (`~/.cost-estimate-reports/<repo>/` by default; override with `COST_ESTIMATE_OUT`) + PDF if pandoc/xelatex are installed

### Example output

Two example reports are shipped:

- [examples/sample-report.md](examples/sample-report.md) — **self-referential** (the skill run on this repo's own shipped files)
- [examples/sample-report-codebase.md](examples/sample-report-codebase.md) — a **neutral, code-dominated** calibration case (a small ~2 KLOC interpreter under [examples/calibration-codebase/](examples/calibration-codebase/))

> ⚠️ **Conflict of interest (disclosed).** This tool's intellectual-effort design credits
> prose/prompt artifacts (up to 3.0×), and this repo is itself prose/prompt-heavy — so the
> self-referential example is **illustrative, not a neutral benchmark** (a tool valuing itself).
> That is exactly why intellectual effort is reported **separately and kept out of the dollar
> headline**, and why the code-dominated calibration example is shipped for a non-self
> comparison. The self example is generated on this repo's shipped files only (`skill/`,
> `README.md`, install scripts — the internal `docs/` notes are excluded), so every number is
> reproducible. PDFs are produced on demand when `pandoc` + `xelatex` are installed.

## Installation

### Option 1: Install script (recommended)

```bash
git clone https://github.com/mlamp/cost-estimate.git
cd cost-estimate
chmod +x install.sh && ./install.sh
```

This creates a symlink at `~/.claude/skills/cost-estimate` pointing to the repo's `skill/` directory.

### Option 2: Manual symlink

```bash
git clone https://github.com/mlamp/cost-estimate.git ~/cost-estimate
mkdir -p ~/.claude/skills
ln -s ~/cost-estimate/skill ~/.claude/skills/cost-estimate
```

### Option 3: Per-project

Copy into any project's `.claude/skills/` directory:

```bash
mkdir -p .claude/skills/cost-estimate
curl -sL https://raw.githubusercontent.com/mlamp/cost-estimate/main/skill/SKILL.md \
  -o .claude/skills/cost-estimate/SKILL.md
```

### Option 4: Direct download (no git)

```bash
mkdir -p ~/.claude/skills/cost-estimate
curl -sL https://raw.githubusercontent.com/mlamp/cost-estimate/main/skill/SKILL.md \
  -o ~/.claude/skills/cost-estimate/SKILL.md
```

## Usage

In any Claude Code session:

```
/cost-estimate
```

With AI comparison (optional argument):

```
/cost-estimate 30 hours with Claude
```

This adds an illustrative section placing the self-reported AI build time next to the model's hypothetical human estimate (both unverified — not a controlled measurement).

## How it works

1. **Pre-flight checks** — Detects OS, verifies tool availability (cloc, pandoc, git), counts files, checks for monorepo structure, sets decision flags (TINY_REPO, CONFIG_ONLY, EMPTY_REPO, etc.)
2. **Data collection** — Counts lines of code (via `cloc` or `find + wc -l` fallback with 0.7x multiplier), reads git history, detects tech stack from config files, identifies and excludes generated/vendored code
3. **Complexity scoring** — grep/find searches produce deterministic file counts, each factor taking `MAX(web-idiom, domain-general)` signals plus a depth/intensity term; mapped to 1–5 and classified Simple/Moderate/Complex. The model interprets the counts (re-runs may differ slightly)
4. **Parametric estimation** — COCOMO II base equation (Effort = 2.94 × KLOC^E × EAF) on **source code only**, with 5 Effort Multipliers (CPLX, DATA, RELY, PLEX, DOCU) mapped from complexity scores; remaining 12 EMs default to Nominal (1.0). Intellectual-effort artifacts are estimated **separately** and never summed into this figure
5. **Structural cross-checks & uncertainty** — IFPUG/COSMIC/UCP structural sizes are computed as archetype-gated cross-checks (Phase 2.5); a seeded 10,000-iteration Monte-Carlo over triangular size/productivity inputs produces the P10–P90 band (Phase 3.9); an optional git-effort/AI-provenance anchor and corpus-based reference-class/Bayesian calibration run when available (Phase 3.95). None of the cross-checks or anchors move the deterministic headline (only a genuine user-supplied actual does, capped)
6. **Cost projection** — Cost = Person-Hours × fully-loaded rate (**no overhead multiplier** — team size is a schedule effect, not a markup); the deterministic point with the Monte-Carlo P10–P90 band; schedule via the COCOMO II Tdev formula on the code-only PM. Below ~2 KLOC, figures are order-of-magnitude only
7. **Report generation** — Outputs formatted markdown to chat, saves it outside the analyzed repo (`~/.cost-estimate-reports/<repo>/` by default), generates PDF via pandoc + xelatex if available

## Optional dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `cloc` | Accurate LOC counting by language | `brew install cloc` / `apt install cloc` |
| `pandoc` + `xelatex` | PDF report generation | `brew install pandoc` + MacTeX |

The skill works without these — it falls back to `find + wc -l` for LOC counting and skips PDF generation.

## Self-check (development)

The report is generated by an LLM following `skill/SKILL.md`, so it can't be byte-regenerated by a
script — but the **deterministic machinery and sample consistency** are guarded by
[`scripts/self-check.sh`](scripts/self-check.sh) (run in CI via
[`.github/workflows/self-check.yml`](.github/workflows/self-check.yml)):

```bash
bash scripts/self-check.sh
```

It verifies every embedded `bash` block parses, audits for nondeterminism/network/install/stale
design, confirms the Monte-Carlo band is byte-reproducible, checks the structural-FP archetype gate
stays N/A on the non-web calibration fixture, and flags when the shipped sample reports drift from
the fixture's LOC or lose the current framing (a reminder to regenerate them via the frozen
temp-dir method). It is read-only and degrades gracefully without `cloc`/`jq`.

## Uninstall

```bash
./uninstall.sh
```

Or manually: `rm ~/.claude/skills/cost-estimate`

## License

MIT
