# cost-estimate

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that analyzes any codebase and produces a professional cost estimation report using a simplified parametric model based on COCOMO II.

Point it at a repo, get a detailed breakdown of what it would cost a human team to build from scratch — with effort ranges, team profiles, and optional AI speed comparison.

## What it produces

- **Codebase profile** — languages, LOC (via `cloc` or fallback), git history, tech stack detection
- **8-factor complexity assessment** — external integrations, data layer, auth, testing, infra, error handling, docs, security — each scored 1–5 with deterministic grep/find-based scoring
- **Parametric effort estimation** — Simplified COCOMO II (A=2.94, Scale Factor-based exponent E, 5 mapped Effort Multipliers), person-months, person-hours, function points
- **Cost tables** — 4 team profiles (Solo Senior $125/hr, Lean Startup $115/hr, Growth Co $125/hr, Enterprise $145/hr) with overhead multipliers
- **Low / Mid / High ranges** for every estimate
- **Headline valuation** — conservative, realistic, and premium tiers
- **AI speed comparison** (optional) — compare AI-assisted build time against the COCOMO human estimate
- **Report output** — Markdown saved to `tmp/` + PDF if pandoc/xelatex are installed

### Example output

See the full self-referential report (generated on this repo itself):

- [examples/sample-report.md](examples/sample-report.md) — Markdown
- [examples/sample-report.pdf](examples/sample-report.pdf) — PDF

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

This adds a section comparing AI-assisted build time against the COCOMO human estimate.

## How it works

1. **Pre-flight checks** — Detects OS, verifies tool availability (cloc, pandoc, git), counts files, checks for monorepo structure, sets decision flags (TINY_REPO, CONFIG_ONLY, EMPTY_REPO, etc.)
2. **Data collection** — Counts lines of code (via `cloc` or `find + wc -l` fallback with 0.7x multiplier), reads git history, detects tech stack from config files, identifies and excludes generated/vendored code
3. **Complexity scoring** — Deterministic grep/find searches score 8 factors on a 1–5 scale, mapped to file-count thresholds; classifies project as Simple (1.0–2.0), Moderate (2.1–3.5), or Complex (3.6–5.0)
4. **Parametric estimation** — COCOMO II base equation (Effort = 2.94 × KLOC^E × EAF) with 5 Effort Multipliers (CPLX, DATA, RELY, PLEX, DOCU) mapped from complexity scores; remaining 12 EMs default to Nominal (1.0)
5. **Cost projection** — Applies 4 team profiles with blended hourly rates and overhead multipliers (1.0x–1.65x), produces Low/Mid/High ranges; schedule via COCOMO II Tdev formula
6. **Report generation** — Outputs formatted markdown to chat, saves to `tmp/`, generates PDF via pandoc + xelatex if available

## Optional dependencies

| Tool | Purpose | Install |
|------|---------|---------|
| `cloc` | Accurate LOC counting by language | `brew install cloc` / `apt install cloc` |
| `pandoc` + `xelatex` | PDF report generation | `brew install pandoc` + MacTeX |

The skill works without these — it falls back to `find + wc -l` for LOC counting and skips PDF generation.

## Uninstall

```bash
./uninstall.sh
```

Or manually: `rm ~/.claude/skills/cost-estimate`

## License

MIT
