# 💰 Codebase Cost Estimation Report

> **Repository:** `cost-estimate`
> **Analysis Date:** 2026-03-06
> **Methodology:** Simplified Parametric Model based on COCOMO II

---

## 📊 Codebase Profile

| Metric | Value |
|--------|-------|
| **Languages** | Markdown (1,278), Shell (29) |
| **Total Lines of Code** | 1,307 |
| **Effective KLOC** | 0.03 KLOC (source code only) |
| **Configuration LOC** | 1,278 (Markdown -- reported for context, not used in COCOMO) |
| **Total Files** | 9 |
| **Git Commits** | 1 |
| **Contributors** | 1 (Margus Lamp) |
| **Repository Age** | New (same day) |
| **Active Development** | 2026-03-06 → 2026-03-06 |
| **Tech Stack** | Shell/Bash, Markdown documentation, Claude Code skill |

> **Note:** This codebase is under 500 effective LOC. The parametric model is calibrated for projects above 2 KLOC. The estimates below have low confidence and should be treated as rough order-of-magnitude only.

## 🔍 Complexity Assessment

| Factor | Score | Justification |
|--------|-------|---------------|
| External Integrations | ⬛⬜⬜⬜⬜ 1/5 | No HTTP clients or API calls found |
| Data Layer | ⬛⬜⬜⬜⬜ 1/5 | No database or ORM patterns found |
| Auth & Authorization | ⬛⬜⬜⬜⬜ 1/5 | No auth patterns found |
| Testing Maturity | ⬛⬜⬜⬜⬜ 1/5 | No test files found |
| Infrastructure/DevOps | ⬛⬜⬜⬜⬜ 1/5 | No Docker, CI/CD, or IaC files found |
| Error Handling | ⬛⬜⬜⬜⬜ 1/5 | No observability or error handling patterns |
| Documentation | ⬛⬛⬜⬜⬜ 2/5 | README.md present with usage instructions |
| Security Posture | ⬛⬜⬜⬜⬜ 1/5 | No security patterns found |
| **Average** | **1.1/5** | **Simple** |

## Intellectual Effort Artifacts

Non-code files representing significant domain expertise, prompt engineering, or encoded methodology.

| Classification | Files | Physical Lines | Equiv. Effort LOC | Key Files |
|----------------|-------|---------------|-------------------|-----------|
| Domain Expertise (T3, 1.5x) | 1 | 1,397 | 2,096 | SKILL.md |
| Boilerplate (T1, 0.1x) | 2 | 245 | 24 | (not listed) |
| **Total** | **3** | **1,642** | **2,120** | |

> Intellectual effort artifacts add **2,096** equivalent LOC to the project,
> representing **98.6%** of total estimated effort.

## ⚙️ Effort Estimation

| Parameter | Value |
|-----------|-------|
| Effective KLOC | 0.03 (Shell source code) |
| Project Type | Simple (avg complexity 1.1/5) |
| Exponent E | 1.06 |
| Effort Multipliers | CPLX=0.73, DATA=0.90, RELY=0.82, PLEX=0.87, DOCU=0.91 |
| EAF (product of EMs) | 0.43 |
| **Source Code Effort** | **0.0 person-months (4 hours)** |
| **Intellectual Effort Artifacts** | **2.1 person-months (323 hours)** |
| **Combined Base Effort** | **2.2 person-months (330 hours)** |
| Estimated Function Points | 53 FP (1 Source Code + 52 IE) |
| Schedule (Tdev) | 4.6 months (ideal) |

### Effort Range

| | Low (0.6x) | Mid (1.0x) | High (1.6x) |
|---|-----------|-----------|------------|
| **Person-Months** | 1.3 | 2.2 | 3.4 |
| **Person-Hours** | 200 | 330 | 520 |

## 💵 Cost Estimation

### By Team Configuration

| Team Profile | Low | Mid | High | Calendar Time (Mid) |
|-------------|-----|-----|------|-------------------|
| 👤 Solo Senior ($175/hr) | $34K | $57K | $92K | 4.6 months |
| 🚀 Lean Startup ($150/hr, 1.15x OH) | $34K | $56K | $90K | 4.6 months |
| 📈 Growth Co ($165/hr, 1.35x OH) | $44K | $73K | $117K | 4.6 months |
| 🏢 Enterprise ($185/hr, 1.65x OH) | $60K | $100K | $160K | 4.6 months |

### Effort Allocation (Mid Estimate)

| Activity | % | Hours | Cost (Growth Co) |
|----------|---|-------|-----------------|
| Development & Coding | 55% | 180 | $40K |
| Testing & QA | 20% | 70 | $16K |
| Project Management | 12% | 40 | $9K |
| DevOps & Infrastructure | 8% | 30 | $7K |
| Documentation | 5% | 20 | $4K |

## 🏷️ Headline Valuation

| Tier | Estimate | Basis |
|------|----------|-------|
| **Conservative** | **$34K** | Solo senior, low complexity (0.6x) |
| **Realistic** | **$73K** | Growth company, mid estimate |
| **Premium** | **$160K** | Enterprise team, high estimate (1.6x) |

> **If someone asked "what would it cost to build this from scratch?"**
> The realistic answer is **$44K - $117K** with a team of 6.5 engineers over 4.6 months.
> This includes **323 hours** of intellectual effort in non-code artifacts (prompts, domain configs, methodology documents).

## 🤖 AI Speed Comparison

| Metric | Human Team | AI-Assisted |
|--------|-----------|-------------|
| Build Time | 330 hours | 3 hours |
| Speed Multiple | 1x | 110x faster |
| Cost (at Growth Co rates) | $73K | $700 |
| Cost Savings | -- | 99% |

> AI-assisted development completed in **AI 2h Claude 4.6, human 1h** what would take a human team **330 hours** -- a **110x speedup**.

## 📋 Methodology & Assumptions

- **Model:** Simplified parametric model based on COCOMO II (Boehm et al., 2000). Uses the COCOMO II base equation (A=2.94, exponent E from Scale Factors) with 5 of 17 Effort Multipliers mapped from automated codebase analysis; remaining EMs default to Nominal (1.0). This is an automated approximation -- full COCOMO II requires expert calibration of all 22 drivers.
- **Working Hours:** 152 hours/month (19 productive days x 8 hours, accounting for holidays and administrative time)
- **LOC Measurement:** cloc (code lines only, excluding comments and blanks)
- **Rates:** Fully-loaded US consulting/agency rates (2025-2026), not salary equivalents
- **Overhead:** Accounts for hiring/onboarding, organizational coordination, compliance processes, and institutional overhead beyond direct development (see Team Profiles note)
- **Exclusions:** Generated code, lock files, vendored dependencies, build artifacts, config/markup files (from KLOC)
- **Intellectual Effort:** Non-code artifacts (prompts, domain configs, rubrics) estimated using a 4-tier classification system (Boilerplate 0.1x, Structured Knowledge 0.5x, Domain Expertise 1.5x, Novel Methodology 3.0x) based on automated signal detection (conditional language density, constraint patterns, instructional density). Constants derived from Jones, *Applied Software Measurement* (3rd ed., 2008) and IFPUG SNAP Assessment Practices Manual v2.4 (2017). Intellectual effort estimation is a supplementary methodology, not part of standard COCOMO II.
- **Conservative bias:** Estimates lean toward underestimation; actual costs often exceed parametric predictions for novel or poorly-defined projects
- **Schedule:** COCOMO II Tdev formula: Tdev = 3.67 * PM^F where F = 0.28 + 0.2*(E-0.91); Calendar Time is the greater of naive parallelization (hours / headcount / 152) and Tdev, since Tdev represents the minimum feasible schedule regardless of staffing
- **Small project caveat:** Model is calibrated for 2+ KLOC projects; sub-500 LOC estimates are low-confidence

*Sources: Boehm, B. et al. (2000). Software Cost Estimation with COCOMO II. Prentice Hall. Jones, C. Applied Software Measurement, 3rd ed. McGraw-Hill. ZipRecruiter, FullStack Labs, Rise 2026 Contractor Rates.*

---

*Generated by [cost-estimate](https://github.com/mlamp/cost-estimate) -- a Claude Code skill using a simplified parametric model based on COCOMO II*
