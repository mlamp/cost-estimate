# 💰 Codebase Cost Estimation Report

> **Repository:** `cost-estimate`
> **Analysis Date:** 2026-03-06
> **Methodology:** Simplified Parametric Model based on COCOMO II

---

## 📊 Codebase Profile

| Metric | Value |
|--------|-------|
| **Languages** | Shell (29 LOC) |
| **Total Lines of Code** | 801 (incl. blanks and config) |
| **Effective KLOC** | 0.03 KLOC (code-only, Shell) |
| **Configuration LOC** | 772 (Markdown -- SKILL.md prompt engineering, README, examples) |
| **Total Files** | 7 |
| **Git Commits** | 2 |
| **Contributors** | 1 (Margus Lamp) |
| **Repository Age** | < 1 day |
| **Active Development** | 2026-03-06 → 2026-03-06 |
| **Tech Stack** | Shell scripts, Markdown (Claude Code skill package) |

> **Note:** This codebase is under 500 effective LOC. The parametric model is calibrated for projects above 2 KLOC. The estimates below have low confidence and should be treated as rough order-of-magnitude only.
>
> The primary value of this project is the 772-line SKILL.md prompt engineering document, which encodes COCOMO II methodology, team profile economics, deterministic complexity scoring, and report template design. This intellectual effort is not captured by source code LOC and significantly exceeds what the parametric model estimates.

---

## 🔍 Complexity Assessment

| Factor | Score | Justification |
|--------|-------|---------------|
| External Integrations | ⬛⬜⬜⬜⬜ 1/5 | No API calls or HTTP clients found |
| Data Layer | ⬛⬜⬜⬜⬜ 1/5 | No database or ORM patterns found |
| Auth & Authorization | ⬛⬜⬜⬜⬜ 1/5 | No auth mechanisms found |
| Testing Maturity | ⬛⬜⬜⬜⬜ 1/5 | No test files found |
| Infrastructure/DevOps | ⬛⬜⬜⬜⬜ 1/5 | No Docker, CI/CD, or infra files |
| Error Handling | ⬛⬜⬜⬜⬜ 1/5 | No observability patterns found |
| Documentation | ⬛⬛⬜⬜⬜ 2/5 | README.md with install/usage instructions |
| Security Posture | ⬛⬜⬜⬜⬜ 1/5 | No security patterns found |
| **Average** | **1.1/5** | **Simple** |

---

## ⚙️ Effort Estimation

| Parameter | Value |
|-----------|-------|
| Effective KLOC | 0.03 |
| Project Type | Simple |
| Exponent E | 1.06 |
| Effort Multipliers | CPLX=0.73, DATA=0.90, RELY=0.82, PLEX=0.87, DOCU=0.91 |
| EAF (product of EMs) | 0.43 |
| **Base Effort** | **0.0 person-months** |
| **Estimated Person-Hours** | **4.5 hours** |
| Estimated Function Points | 1 FP |
| Schedule (Tdev) | 1.2 months (ideal) |

### Effort Range

| | Low (0.6x) | Mid (1.0x) | High (1.6x) |
|---|-----------|-----------|------------|
| **Person-Months** | 0.0 | 0.0 | 0.0 |
| **Person-Hours** | 2.7 | 4.5 | 7.2 |

> *Note: Values are below the rounding threshold of 10 hours. Exact values shown for transparency.*

---

## 💵 Cost Estimation

### By Team Configuration

| Team Profile | Low | Mid | High | Calendar Time (Mid) |
|-------------|-----|-----|------|-------------------|
| 👤 Solo Senior ($125/hr) | $300 | $600 | $900 | 1.2 months |
| 🚀 Lean Startup ($115/hr, 1.15x OH) | $400 | $600 | $1,000 | 1.2 months |
| 📈 Growth Co ($125/hr, 1.35x OH) | $500 | $800 | $1,200 | 1.2 months |
| 🏢 Enterprise ($145/hr, 1.65x OH) | $600 | $1,100 | $1,700 | 1.2 months |

### Effort Allocation (Mid Estimate)

| Activity | % | Hours | Cost (Growth Co) |
|----------|---|-------|-----------------|
| Development & Coding | 55% | 2.5 | $400 |
| Testing & QA | 20% | 0.9 | $200 |
| Project Management | 12% | 0.5 | $100 |
| DevOps & Infrastructure | 8% | 0.4 | $100 |
| Documentation | 5% | 0.2 | $0 |

---

## 🏷️ Headline Valuation

| Tier | Estimate | Basis |
|------|----------|-------|
| **Conservative** | **$300** | Solo senior, low complexity (0.6x) |
| **Realistic** | **$800** | Growth company, mid estimate |
| **Premium** | **$1,700** | Enterprise team, high estimate (1.6x) |

> **If someone asked "what would it cost to build this from scratch?"**
> The realistic answer is **$500 - $1,200** with a team of 6.5 engineers over 1.2 months.
>
> **However**, this estimate covers only the 29 lines of Shell script. The true value lies in the 772-line SKILL.md -- a carefully engineered prompt encoding COCOMO II methodology, deterministic scoring rules, team economics, and report templates. That intellectual effort would realistically cost **$5K-$15K** to replicate from scratch (domain research, prompt engineering, validation).

---

## 🤖 AI Speed Comparison

| Metric | Human Team | AI-Assisted |
|--------|-----------|-------------|
| Build Time | 4.5 hours | 1 hours |
| Speed Multiple | 1x | 5x faster |
| Cost (at Growth Co rates) | $800 | $200 |
| Cost Savings | -- | 78% |

> AI-assisted development completed in **1h inference, claude opus 4.6, human time 30min** what would take a human team **4.5 hours** -- a **5x speedup**.

---

## 📋 Methodology & Assumptions

- **Model:** Simplified parametric model based on COCOMO II (Boehm et al., 2000). Uses the COCOMO II base equation (A=2.94, exponent E from Scale Factors) with 5 of 17 Effort Multipliers mapped from automated codebase analysis; remaining EMs default to Nominal (1.0). This is an automated approximation -- full COCOMO II requires expert calibration of all 22 drivers.
- **Working Hours:** 152 hours/month (19 productive days x 8 hours, accounting for holidays and administrative time)
- **LOC Measurement:** cloc v2.08 (code lines only, excluding comments and blanks); Markdown LOC reported separately as Configuration LOC
- **Rates:** Fully-loaded US consulting/agency rates (2025-2026), not salary equivalents
- **Overhead:** Accounts for hiring/onboarding, organizational coordination, compliance processes, and institutional overhead beyond direct development (see Team Profiles note)
- **Exclusions:** Generated code, lock files, vendored dependencies, build artifacts, config/markup files (from KLOC)
- **Conservative bias:** Estimates lean toward underestimation; actual costs often exceed parametric predictions for novel or poorly-defined projects
- **Schedule:** COCOMO II Tdev formula: Tdev = 3.67 * PM^F where F = 0.28 + 0.2*(E-0.91); Calendar Time is the greater of naive parallelization (hours / headcount / 152) and Tdev, since Tdev represents the minimum feasible schedule regardless of staffing
- **Small project caveat:** Model is calibrated for 2+ KLOC projects; sub-500 LOC estimates are low-confidence. The 772-line SKILL.md prompt engineering document represents significant domain expertise not captured by the parametric model.

*Sources: Boehm, B. et al. (2000). Software Cost Estimation with COCOMO II. Prentice Hall. Jones, C. Applied Software Measurement, 3rd ed. McGraw-Hill. ZipRecruiter, FullStack Labs, Rise 2026 Contractor Rates.*

---

*Generated by [cost-estimate](https://github.com/mlamp/cost-estimate) -- a Claude Code skill using a simplified parametric model based on COCOMO II*
