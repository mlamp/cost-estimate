---
name: cost-estimate
description: Analyze codebase and estimate human team build cost (Simplified Parametric Model based on COCOMO II)
tags: ["analysis", "estimation", "cocomo", "cost"]
allowed-tools:
  - Bash
  - Glob
  - Grep
  - Read
argument-hint: "[optional: AI build hours, e.g. '30 hours with Claude']"
---

You are a senior software cost estimation analyst. Analyze the current repository and produce a professional cost estimation report using a simplified parametric model based on COCOMO II.

**AI comparison argument (if provided):** $ARGUMENTS

**Parsing $ARGUMENTS:** Extract the numeric hours value using the pattern `(\d+\.?\d*)`. Examples:
- `'30 hours with Claude'` -> 30
- `'2.5 hours'` -> 2.5
- `'Built it over a weekend'` -> no number found

If no numeric value can be extracted, display the AI Speed Comparison section with the raw text only and omit all numeric comparison rows (Speed Multiple, Cost, Cost Savings).

---

## Canonical Reference Lists

The following extensions are considered **source code** throughout this document. Every bash command that filters by source code extension uses this same set:

**SOURCE_EXTENSIONS:** `.py`, `.js`, `.ts`, `.tsx`, `.jsx`, `.rb`, `.go`, `.rs`, `.java`, `.kt`, `.swift`, `.c`, `.cpp`, `.h`, `.cs`, `.php`, `.vue`, `.svelte`, `.sql`, `.sh`, `.bash`, `.zsh`, `.lua`, `.ex`, `.exs`, `.erl`, `.hs`, `.scala`, `.clj`, `.r`, `.R`, `.m`, `.dart`, `.zig`, `.nim`, `.tf`, `.hcl`

The following directory exclusion set is used by every `find` and `grep` command in this document (referred to as "standard exclusion list"):

**STANDARD_EXCLUDES (for find):** `-not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*'`

**STANDARD_EXCLUDES (for grep):** `--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__`

**Timeout policy:** All `cloc` commands are prefixed with `timeout 60`. All `find` and `grep` commands are prefixed with `timeout 30`. If any command times out, treat its output as empty, record a `TIMEOUT` flag for that step, and add a methodology note: "Data collection for {step} timed out; that metric is omitted."

---

## PHASE 0: Pre-Flight Checks

Before collecting data, verify the environment and export shell variables for reuse. Run this single Bash block:

```bash
# Homebrew init (macOS Apple Silicon) — ensures cloc, pandoc, etc. are in PATH
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"

echo "=== REPO ROOT ==="
pwd

echo "=== GIT CHECK ==="
if git rev-parse --is-inside-work-tree 2>/dev/null; then
  echo "GIT_AVAILABLE=yes"
else
  echo "GIT_AVAILABLE=no"
fi

echo "=== CLOC CHECK ==="
if command -v cloc &>/dev/null; then
  echo "CLOC_AVAILABLE=yes"
else
  echo "CLOC_AVAILABLE=no"
fi

echo "=== PANDOC CHECK ==="
if command -v pandoc &>/dev/null; then
  echo "PANDOC_AVAILABLE=yes"
else
  echo "PANDOC_AVAILABLE=no"
fi

echo "=== OS DETECTION ==="
if [[ "$(uname)" == "Darwin" ]]; then
  echo "OS=macOS"
  echo "MAIN_FONT=Helvetica"
  echo "MONO_FONT=Menlo"
elif [[ "$(uname)" == "Linux" ]]; then
  echo "OS=Linux"
  echo "MAIN_FONT=DejaVu Sans"
  echo "MONO_FONT=DejaVu Sans Mono"
else
  echo "OS=Other"
  echo "MAIN_FONT=DejaVu Sans"
  echo "MONO_FONT=DejaVu Sans Mono"
fi

echo "=== SHELL VARIABLES ==="
# Export reusable variables for subsequent commands
export SRC_EXTS_FIND="\( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.rb' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.kt' -o -name '*.swift' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.cs' -o -name '*.php' -o -name '*.vue' -o -name '*.svelte' -o -name '*.sql' -o -name '*.sh' -o -name '*.bash' -o -name '*.zsh' -o -name '*.lua' -o -name '*.ex' -o -name '*.exs' -o -name '*.erl' -o -name '*.hs' -o -name '*.scala' -o -name '*.clj' -o -name '*.r' -o -name '*.R' -o -name '*.m' -o -name '*.dart' -o -name '*.zig' -o -name '*.nim' -o -name '*.tf' -o -name '*.hcl' \)"

export SRC_EXTS_GREP="--include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.swift' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl'"

export STD_EXCLUDES_FIND="-not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*'"

export STD_EXCLUDES_GREP="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__"

echo "Variables exported: SRC_EXTS_FIND, SRC_EXTS_GREP, STD_EXCLUDES_FIND, STD_EXCLUDES_GREP"

echo "=== CODE FILE COUNT ==="
CODEFILES=$(timeout 30 find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.rb' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.kt' -o -name '*.swift' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.cs' -o -name '*.php' -o -name '*.vue' -o -name '*.svelte' -o -name '*.sql' -o -name '*.sh' -o -name '*.bash' -o -name '*.zsh' -o -name '*.lua' -o -name '*.ex' -o -name '*.exs' -o -name '*.erl' -o -name '*.hs' -o -name '*.scala' -o -name '*.clj' -o -name '*.r' -o -name '*.R' -o -name '*.m' -o -name '*.dart' -o -name '*.zig' -o -name '*.nim' -o -name '*.tf' -o -name '*.hcl' \) -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' 2>/dev/null | wc -l | tr -d ' ')
echo "CODE_FILE_COUNT=$CODEFILES"

echo "=== TOTAL FILE COUNT ==="
TOTALFILES=$(timeout 30 find . -type f -not -path '*/.git/*' 2>/dev/null | wc -l | tr -d ' ')
echo "TOTAL_FILE_COUNT=$TOTALFILES"

echo "=== MONOREPO CHECK ==="
MONOREPO_DETECTED=no
if [ -f "lerna.json" ]; then echo "LERNA=yes"; MONOREPO_DETECTED=yes; else echo "LERNA=no"; fi
if [ -f "pnpm-workspace.yaml" ]; then echo "PNPM_WORKSPACES=yes"; MONOREPO_DETECTED=yes; else echo "PNPM_WORKSPACES=no"; fi
if grep -q '"workspaces"' package.json 2>/dev/null; then echo "NPM_WORKSPACES=yes"; MONOREPO_DETECTED=yes; else echo "NPM_WORKSPACES=no"; fi
echo "MONOREPO_DETECTED=$MONOREPO_DETECTED"
```

**Important:** Shell state does not persist between Bash tool calls. In each subsequent Bash command, you must inline the full `find`/`grep` arguments rather than referencing `$SRC_EXTS_FIND` etc. The exported variables above serve as the **canonical definitions** — copy their values verbatim into each command. The Canonical Reference Lists section above is the single source of truth; these variables are a convenience alias for that same content.

### Pre-Flight Decision Rules

Record these flags for use in later phases:

| Flag | Condition | Effect |
|------|-----------|--------|
| `NO_GIT` | `GIT_AVAILABLE=no` | Skip Phase 1b entirely. In report: show "N/A -- no git history" for all git metrics. |
| `NO_CLOC` | `CLOC_AVAILABLE=no` | Use `find + wc -l` fallback in Phase 1a. Apply 0.7x multiplier. |
| `EMPTY_REPO` | `CODE_FILE_COUNT=0` AND no config files with nonzero LOC (see `CONFIG_ONLY` below) | Abort analysis. Output: "This repository contains no source code files. Cost estimation requires at least one code file." |
| `CONFIG_ONLY` | `CODE_FILE_COUNT=0` (Source Code LOC = 0) AND Config/Markup LOC > 0 | Do NOT abort. Use Config LOC * 0.3x as the Effective KLOC (config files require less effort per line than application code). Add note: "This repository consists primarily of configuration/infrastructure-as-code. KLOC is derived from config LOC at 0.3x weighting. The parametric model is designed for application software; estimates may not reflect actual effort accurately." |
| `TINY_REPO` | Effective KLOC < 0.5 (determined after Phase 1a) | Complete the analysis but prepend a disclaimer: "This codebase is under 500 effective LOC. The parametric model is calibrated for projects above 2 KLOC; estimates below that threshold have low confidence." |
| `LARGE_REPO` | `TOTAL_FILE_COUNT > 100000` | Add note: "Large repository detected. File counts are sampled. LOC counts from cloc/wc are authoritative." |
| `MONOREPO` | `MONOREPO_DETECTED=yes` (requires at least one workspace config: lerna.json, pnpm-workspace.yaml, or npm workspaces field in package.json) | Analyze as a single project (sum all code). Add a "Monorepo Structure" subsection listing detected packages/modules (max 15). Note in methodology: "Monorepo analyzed as single aggregate project." |
| `TIMEOUT` | Any bash command exceeds its timeout limit | Record which step timed out. Treat output as empty for that step. Add methodology note. |

If `EMPTY_REPO` is true (and `CONFIG_ONLY` is false), stop here and output only the abort message. Otherwise continue.

---

## PHASE 1: Data Collection

Run steps 1a, 1b (if git available), 1c, and 1d in parallel where possible using Bash.

### 1a. Lines of Code

**If CLOC_AVAILABLE=yes:**

```bash
# Homebrew init (macOS Apple Silicon)
[ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"

timeout 60 cloc . --quiet --hide-rate \
  --exclude-dir=node_modules,.git,vendor,dist,build,.next,__pycache__,.venv,venv,env,.tox,.mypy_cache,.pytest_cache,coverage,.nyc_output,target,out,bin,obj,packages,.dart_tool,.pub-cache,Pods,DerivedData,generated,gen,__generated__,.generated \
  --exclude-ext=lock,sum,svg,png,jpg,jpeg,gif,ico,woff,woff2,ttf,eot,map,min.js,min.css,bundle.js,chunk.js \
  --json 2>/dev/null

# Generate per-file manifest for Phase 1.5 deduplication
timeout 60 cloc --by-file --csv . \
  --exclude-dir=node_modules,.git,vendor,dist,build,.next,__pycache__,.venv,venv,env,.tox,.mypy_cache,.pytest_cache,coverage,.nyc_output,target,out,bin,obj,packages,.dart_tool,.pub-cache,Pods,DerivedData,generated,gen,__generated__,.generated \
  --exclude-ext=lock,sum,svg,png,jpg,jpeg,gif,ico,woff,woff2,ttf,eot,map,min.js,min.css,bundle.js,chunk.js \
  2>/dev/null | tail -n +2 | awk -F',' '{print $2"|"$1"|"$5}' > phase1a-manifest.txt
```

If the cloc command fails (non-zero exit, empty output, output not valid JSON, or times out), fall back to the wc method below. If the `phase1a-manifest.txt` generation fails, Phase 1.5 deduplication will be disabled (a warning will be emitted).

**If CLOC_AVAILABLE=no or cloc failed:**

Run two separate counts -- source code files and config/markup files:

```bash
echo "=== SOURCE CODE LOC ==="
# Uses SOURCE_EXTENSIONS and standard exclusion list
timeout 30 find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.rb' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.kt' -o -name '*.swift' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.cs' -o -name '*.php' -o -name '*.vue' -o -name '*.svelte' -o -name '*.sql' -o -name '*.sh' -o -name '*.bash' -o -name '*.zsh' -o -name '*.lua' -o -name '*.ex' -o -name '*.exs' -o -name '*.erl' -o -name '*.hs' -o -name '*.scala' -o -name '*.clj' -o -name '*.r' -o -name '*.R' -o -name '*.m' -o -name '*.dart' -o -name '*.zig' -o -name '*.nim' -o -name '*.tf' -o -name '*.hcl' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' \
  -exec wc -l {} + 2>/dev/null | tail -1

echo "=== CONFIG/MARKUP LOC ==="
timeout 30 find . -type f \( -name '*.html' -o -name '*.css' -o -name '*.scss' -o -name '*.sass' -o -name '*.less' -o -name '*.yml' -o -name '*.yaml' -o -name '*.toml' -o -name '*.json' -o -name '*.xml' -o -name '*.md' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' \
  -exec wc -l {} + 2>/dev/null | tail -1
```

Only the Source Code LOC contributes to KLOC for the parametric model. Config/Markup LOC is reported separately in the Codebase Profile as "Configuration LOC."

**If Source Code LOC = 0 but Config/Markup LOC > 0:** Set the `CONFIG_ONLY` flag. Use Config LOC * 0.3x as Effective KLOC (see Pre-Flight Decision Rules).

**If the wc fallback also fails** (e.g., permission denied on all files), report: "Unable to count lines of code due to filesystem errors. Cannot produce estimation." and stop.

#### Generated Code Detection and Exclusion

Exclude files matching ANY of these patterns from LOC counts (cloc's `--exclude-dir` handles most; for wc fallback, add to `-not -path`):

| Pattern | Reason |
|---------|--------|
| Directories named `generated`, `gen`, `__generated__`, `.generated` | Code generation output |
| Files containing `DO NOT EDIT` or `AUTO-GENERATED` in the first 3 lines | Generator markers |
| `*.pb.go`, `*.pb.cc`, `*.pb.h`, `*_pb2.py` | Protobuf generated |
| `*.generated.go`, `*_gen.go`, `*.gen.ts` | Go/TS code generation |
| `mock_*.go` | Go mock generation |
| `*.g.dart`, `*.freezed.dart` | Dart code generation |
| `*.graphql.ts`, `*.graphql.tsx` | GraphQL codegen |
| `swagger-*.json`, `openapi-*.json` (files > 500 lines) | API spec generated |

When using cloc, these directory exclusions are already in the command. When using wc fallback, after getting the raw count, run these additional checks:

```bash
echo "=== GENERATED FILE CHECK (by filename pattern) ==="
# Count LOC in files matching generated-code filename patterns
timeout 30 find . -type f \( -name '*.pb.go' -o -name '*.pb.cc' -o -name '*.pb.h' -o -name '*_pb2.py' -o -name '*.g.dart' -o -name '*.freezed.dart' -o -name '*.graphql.ts' -o -name '*.graphql.tsx' -o -name '*.generated.go' -o -name '*_gen.go' -o -name '*.gen.ts' -o -name 'mock_*.go' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' \
  2>/dev/null -exec wc -l {} + 2>/dev/null | tail -1

echo "=== GENERATED FILE CHECK (by header markers) ==="
# Check first 3 lines of source files for DO NOT EDIT / AUTO-GENERATED markers
GENERATED_HEADER_LOC=0
while IFS= read -r file; do
  if head -3 "$file" 2>/dev/null | grep -qiE '(DO NOT EDIT|AUTO[- ]GENERATED|GENERATED BY|THIS FILE IS GENERATED)'; then
    LOC=$(wc -l < "$file" 2>/dev/null | tr -d ' ')
    GENERATED_HEADER_LOC=$((GENERATED_HEADER_LOC + LOC))
    echo "GENERATED_HEADER: $file ($LOC lines)"
  fi
done < <(timeout 30 find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.jsx' -o -name '*.rb' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.kt' -o -name '*.swift' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.cs' -o -name '*.php' -o -name '*.vue' -o -name '*.svelte' -o -name '*.dart' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' 2>/dev/null)
echo "GENERATED_HEADER_TOTAL_LOC=$GENERATED_HEADER_LOC"
```

Subtract both the filename-pattern generated LOC and the header-marker generated LOC from the source code wc total before applying the 0.7x multiplier.

#### Vendored / Checked-In Dependencies Detection

Check for vendored code and exclude it:

```bash
echo "=== VENDORED CODE CHECK ==="
for dir in vendor third_party third-party thirdparty external deps lib/vendor; do
  if [ -d "$dir" ]; then
    echo "VENDORED_DIR=$dir"
    timeout 30 find "$dir" -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.go' -o -name '*.rs' -o -name '*.java' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' -o -name '*.rb' -o -name '*.php' \) 2>/dev/null -exec wc -l {} + 2>/dev/null | tail -1
  fi
done
```

If vendored directories are found, subtract their LOC from the total. Note in the report methodology section which directories were excluded as vendored.

### 1b. Git Statistics

**Skip entirely if `NO_GIT` flag is set.** If git is available:

```bash
echo "=== COMMITS ===" && git log --oneline 2>/dev/null | wc -l
echo "=== CONTRIBUTORS ===" && git shortlog -sn --no-merges 2>/dev/null | head -20
echo "=== FIRST COMMIT ===" && git log --reverse --format="%ai" 2>/dev/null | head -1
echo "=== LAST COMMIT ===" && git log -1 --format="%ai" 2>/dev/null
echo "=== COMMITS PER MONTH ===" && git log --format="%Y-%m" 2>/dev/null | sort | uniq -c | tail -12
```

**If any git sub-command fails** (e.g., shallow clone missing history), use whatever data was returned and mark missing fields as "N/A (limited git history)" in the report.

**If commits = 0** (initialized repo with no commits), treat as `NO_GIT` for reporting purposes.

### 1c. File and Directory Counts

```bash
echo "=== TOTAL FILES ===" && timeout 30 find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' 2>/dev/null | wc -l
echo "=== TOP-LEVEL DIRS ===" && ls -d */ 2>/dev/null
echo "=== FILE TYPES ===" && timeout 30 find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' 2>/dev/null | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

**If find fails** (permission errors), report partial results and note the error.

### 1d. Stack Detection

Use Glob to check for these config files (check them all in parallel):
- `package.json`, `tsconfig.json`, `next.config.*`, `nuxt.config.*`, `vite.config.*`, `webpack.config.*`
- `Cargo.toml`, `go.mod`, `go.sum`, `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`
- `Gemfile`, `composer.json`, `pom.xml`, `build.gradle*`, `*.sln`, `*.csproj`
- `docker-compose.yml`, `docker-compose.yaml`, `Dockerfile*`, `*.dockerfile`
- `terraform/*.tf`, `*.tf`, `pulumi.*`, `serverless.yml`
- `ansible.cfg`, `playbook*.yml`, `ansible/`
- `.github/workflows/*`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/*`
- `kubernetes/`, `k8s/`, `helm/`, `Chart.yaml`
- `pubspec.yaml`, `Package.swift`, `build.zig`
- `.env*`, `*.config.js`, `*.config.ts`

Read the primary config files (package.json, Cargo.toml, go.mod, pyproject.toml, etc.) to identify frameworks, dependencies, and project metadata.

**If a config file exists but cannot be read** (binary, too large, permissions), skip it silently and note the stack as "detected via config file presence" rather than "detected via config file contents."

---

## PHASE 1.5: Intellectual Effort Artifact Detection

This phase runs after Phase 1a (LOC counting) and can run in parallel with Phases 1b, 1c, and 1d. It does not replace any existing phase; it adds a parallel data stream that merges into Phase 3.

**What Phase 1.5 does:** Scans the repository for non-code files (prompts, configs, rubrics, domain rules), classifies each into one of 5 tiers based on intellectual effort density, and converts physical lines into "equivalent effort LOC" using tier-specific multipliers.

**The 5 tiers at a glance:**

| Tier | Name | Multiplier | One-liner |
|------|------|------------|-----------|
| T0 | Excluded | 0x | Auto-generated, lock files, trivial READMEs |
| T1 | Boilerplate | 0.1x | Standard configs with no decision logic |
| T2 | Structured Knowledge | 0.5x | Configs with constraints or conditional logic |
| T3 | Domain Expertise | 1.5x | Agent instructions, rubrics, architecture decisions |
| T4 | Novel Methodology | 3.0x | Dense prompt engineering, decision trees, novel frameworks |

**OUTPUT:** A single structured block `INTELLECTUAL_EFFORT_SUMMARY` (format specified in Phase 1.5 Output Format section below) containing per-file tier classification with equivalent effort LOC and totals for integration into Phase 3.

**CONTEXT BUDGET:** Phase 1.5 output MUST fit within ~2KB typical, 5KB hard cap. TIER_DETAIL table capped at 30 rows (top 30 by equivalent effort LOC descending). Remaining files summarized as a single aggregate row.

**FAILURE MODES:**
- If zero candidate files found: emit `INTELLECTUAL_EFFORT_SUMMARY` with all counts zero and note "No intellectual effort artifacts detected." Skip integration steps in Phase 3.
- If grep or find commands fail (permissions, filesystem errors): log the error, classify the affected file as Tier 1 (safe fallback), and continue. Never halt the pipeline for a single file failure.
- If Phase 1a manifest is missing: emit a warning "Phase 1a manifest not found; deduplication disabled" and proceed without deduplication (all intellectual effort LOC treated as additive).
- On pipeline abort or error: the cleanup trap (set in Step 1.5a) removes all temporary files automatically.

**Shell Environment Requirement:** All Phase 1.5 bash blocks (Steps 1.5a through 1.5d and the git revision check) MUST execute in the same shell session so that `IE_TMPDIR` and all derived paths (`CANDIDATE_LIST`, `AUTO_GENERATED_LIST`, `SIGNALS_FILE`, `CLASSIFICATION_FILE`) remain accessible across steps.

### Step 1.5a: Candidate File Discovery

Run this single bash block to find all non-source-code files that may contain intellectual effort. Output is saved to a temp file for use in subsequent steps:

```bash
echo "=== INTELLECTUAL EFFORT ARTIFACT SCAN ==="

# Create temp directory and set cleanup trap
IE_TMPDIR=$(mktemp -d)
trap 'rm -rf "$IE_TMPDIR"' EXIT
CANDIDATE_LIST="$IE_TMPDIR/candidates.txt"
> "$CANDIDATE_LIST"

# Common exclusion arguments (reused per find invocation)
COMMON_EXCLUDES=(
  -not -path '*/.git/*'
  -not -path '*/node_modules/*'
  -not -path '*/vendor/*'
  -not -path '*/dist/*'
  -not -path '*/build/*'
  -not -path '*/.venv/*'
  -not -path '*/CHANGELOG*'
  -not -path '*/LICENSE*'
  -not -path '*/CONTRIBUTING*'
  -not -name 'LICENSE*'
  -not -name 'CHANGELOG*'
)

# Category 1: Prompt and agent instruction files
echo "--- PROMPT_FILES ---"
find . -maxdepth 8 -type f \( -name '*.md' -o -name '*.txt' -o -name '*.prompt' -o -name '*.system' \) \
  "${COMMON_EXCLUDES[@]}" \
  2>/dev/null | while IFS= read -r f; do
    LINES=$(wc -l < "$f" 2>/dev/null | tr -d ' ')
    LINES=${LINES:-0}; LINES=$((LINES + 0))
    echo "PROMPT_CANDIDATE|$f|$LINES"
    echo "$f|$LINES" >> "$CANDIDATE_LIST"
done

# Category 2: Configuration-as-knowledge files
echo "--- CONFIG_KNOWLEDGE_FILES ---"
find . -maxdepth 8 -type f \( -name '*.yml' -o -name '*.yaml' -o -name '*.toml' -o -name '*.json' -o -name '*.hcl' -o -name '*.tf' -o -name '*.tfvars' \) \
  "${COMMON_EXCLUDES[@]}" \
  -not -name 'package-lock.json' -not -name 'yarn.lock' -not -name 'pnpm-lock.yaml' \
  -not -name '*.min.json' \
  2>/dev/null | while IFS= read -r f; do
    LINES=$(wc -l < "$f" 2>/dev/null | tr -d ' ')
    LINES=${LINES:-0}; LINES=$((LINES + 0))
    echo "CONFIG_CANDIDATE|$f|$LINES"
    echo "$f|$LINES" >> "$CANDIDATE_LIST"
done

# Category 3: Domain rule and rubric files
echo "--- RULE_FILES ---"
find . -maxdepth 8 -type f \( -name '*.rules' -o -name '*.rubric' -o -name '*.criteria' -o -name '*.schema' \
  -o -name 'CLAUDE.md' -o -name '.cursorrules' -o -name '.windsurfrules' \
  -o -name 'AGENTS.md' -o -name 'CONVENTIONS.md' -o -name 'CODING_STANDARDS.md' \) \
  "${COMMON_EXCLUDES[@]}" \
  2>/dev/null | while IFS= read -r f; do
    LINES=$(wc -l < "$f" 2>/dev/null | tr -d ' ')
    LINES=${LINES:-0}; LINES=$((LINES + 0))
    echo "RULE_CANDIDATE|$f|$LINES"
    echo "$f|$LINES" >> "$CANDIDATE_LIST"
done

TOTAL_CANDIDATES=$(wc -l < "$CANDIDATE_LIST" | tr -d ' ')
echo "TOTAL_CANDIDATES=$TOTAL_CANDIDATES"

# Hard cap: if >100 candidates, keep only top 100 by line count for full classification.
# Remaining files are auto-classified as Tier 1.
if [ "$TOTAL_CANDIDATES" -gt 100 ]; then
  echo "WARNING: $TOTAL_CANDIDATES candidates exceed 100-file cap. Classifying top 100 by line count; rest default to Tier 1."
  sort -t'|' -k2 -rn "$CANDIDATE_LIST" | head -100 > "$IE_TMPDIR/top.txt"
  sort -t'|' -k2 -rn "$CANDIDATE_LIST" | tail -n +101 > "$IE_TMPDIR/overflow.txt"
  mv "$IE_TMPDIR/top.txt" "$CANDIDATE_LIST"
fi
```

### Step 1.5b: Auto-Generation Detection

Before classifying any candidate, check if it was auto-generated:

```bash
echo "=== AUTO-GENERATION CHECK ==="
AUTO_GENERATED_LIST="$IE_TMPDIR/autogen.txt"
> "$AUTO_GENERATED_LIST"

while IFS='|' read -r FILE LINES; do
  HEADER=$(head -5 "$FILE" 2>/dev/null)
  if echo "$HEADER" | grep -qiE '(auto.?generated|do not edit|generated by|this file is generated|machine generated)'; then
    echo "AUTO_GENERATED|$FILE|$LINES"
    echo "$FILE" >> "$AUTO_GENERATED_LIST"
  fi
done < "$CANDIDATE_LIST"

# Check for very large JSON/YAML that are likely generated (>50KB)
while IFS='|' read -r FILE LINES; do
  case "$FILE" in
    *.json|*.yaml|*.yml)
      SIZE=$(wc -c < "$FILE" 2>/dev/null | tr -d ' ')
      if [ "$SIZE" -gt 51200 ]; then
        echo "LARGE_DATA_FILE|$FILE|$LINES"
        echo "$FILE" >> "$AUTO_GENERATED_LIST"
      fi
      ;;
  esac
done < "$CANDIDATE_LIST"
```

**Decision rules for auto-generated files:**
- Files with `AUTO_GENERATED` marker: classify as Tier 0 (excluded) -- zero effort credit
- Files flagged as `LARGE_DATA_FILE` (>50KB of JSON/YAML): classify as Tier 0 unless they contain evidence of hand-crafted structure (see Step 1.5c signal detection; if CONDITIONAL_COUNT + CONSTRAINT_COUNT >= 10, reclassify using standard tier rules)

### Step 1.5c: Signal Detection

For each candidate file NOT excluded as auto-generated, detect classification signals. All five signal counts are computed per file in a single awk pass to avoid sequential grep overhead:

```bash
echo "=== CLASSIFICATION SIGNALS ==="
SIGNALS_FILE="$IE_TMPDIR/signals.txt"
> "$SIGNALS_FILE"

while IFS='|' read -r FILE LINES; do
  # Skip auto-generated files
  if grep -qFx "$FILE" "$AUTO_GENERATED_LIST" 2>/dev/null; then
    continue
  fi

  # Size guard: skip files over 1MB to prevent hangs
  FILE_SIZE=$(wc -c < "$FILE" 2>/dev/null | tr -d ' ')
  FILE_SIZE=${FILE_SIZE:-0}
  if [ "$FILE_SIZE" -gt 1048576 ]; then
    echo "SKIPPED_OVERSIZE|$FILE|$LINES|${FILE_SIZE}bytes"
    echo "$FILE|$LINES|0|0|0|0|0|0|" >> "$SIGNALS_FILE"
    continue
  fi

  # Validate LINES is numeric
  LINES=${LINES:-0}; LINES=$((LINES + 0))

  # Check for frontmatter override tag in first 3 lines
  OVERRIDE_TIER=$(head -3 "$FILE" 2>/dev/null | grep -oE 'intellectual-effort-tier: *[0-4]' | grep -oE '[0-4]')
  if [ -n "$OVERRIDE_TIER" ]; then
    echo "$FILE|$LINES|OVERRIDE|OVERRIDE|OVERRIDE|OVERRIDE|OVERRIDE|OVERRIDE|$OVERRIDE_TIER" >> "$SIGNALS_FILE"
    continue
  fi

  # Single awk pass for all signal counts, with 5-second timeout
  read CONDITIONAL CONSTRAINT DOMAIN_TERM INSTRUCTION EXAMPLE <<< $(timeout 5 awk '
    BEGIN { cond=0; cons=0; dom=0; inst=0; exam=0 }
    /if |when |unless |must |never |always |only when|except |provided that|in case of|decision:|choose / { cond++ }
    /constraint|requirement|rule |invariant|precondition|postcondition|boundary|limit|threshold|maximum|minimum|exactly|at least|at most|no more than|no fewer than/ { cons++ }
    /architecture|pattern|anti-?pattern|trade-?off|failure mode|edge case|fallback|degradation|scaling|latency|throughput|consistency|availability|partition/ { dom++ }
    /you (are|will|must|should)|your (role|task|job)|respond with|output (format|as|in)|do not|never |always |(step|phase|stage) [0-9]/ { inst++ }
    /example:|e\.g\.|for instance|such as|template:|format:|schema:|sample:|\{[a-z_]+\}|<[a-z_]+>/ { exam++ }
    END { print cond, cons, dom, inst, exam }
  ' "$FILE" 2>/dev/null)

  CONDITIONAL=${CONDITIONAL:-0}
  CONSTRAINT=${CONSTRAINT:-0}
  DOMAIN_TERM=${DOMAIN_TERM:-0}
  INSTRUCTION=${INSTRUCTION:-0}
  EXAMPLE=${EXAMPLE:-0}

  # Density as integer permille (signals per 1000 lines)
  TOTAL_SIGNALS=$((CONDITIONAL + CONSTRAINT + DOMAIN_TERM + INSTRUCTION + EXAMPLE))
  if [ "$LINES" -gt 0 ]; then
    DENSITY_PERMILLE=$(( TOTAL_SIGNALS * 1000 / LINES ))
  else
    DENSITY_PERMILLE=0
  fi

  echo "$FILE|$LINES|$CONDITIONAL|$CONSTRAINT|$DOMAIN_TERM|$INSTRUCTION|$EXAMPLE|$DENSITY_PERMILLE|" >> "$SIGNALS_FILE"
done < "$CANDIDATE_LIST"
```

**Language limitation:** Signal detection regex patterns are English-only. For non-English repositories, authors can add a frontmatter override tag in the first 3 lines of the file: `<!-- intellectual-effort-tier: 3 -->`. Valid values: 0, 1, 2, 3, 4.

### Step 1.5d: Tier Classification

This step reads the signals file from Step 1.5c and applies the complete decision tree:

```bash
echo "=== TIER CLASSIFICATION ==="
CLASSIFICATION_FILE="$IE_TMPDIR/classifications.txt"
> "$CLASSIFICATION_FILE"

# Header: FILE|LINES|TIER|MULTIPLIER|EQUIV_LOC|FLOOR_APPLIED|DENSITY_PERMILLE
while IFS='|' read -r FILE LINES COND CONS DOM INST EXAM DENS OVERRIDE_TIER; do

  # Validate LINES is numeric
  LINES=${LINES:-0}; LINES=$((LINES + 0))

  # --- Frontmatter override ---
  if [ "$COND" = "OVERRIDE" ]; then
    TIER="$OVERRIDE_TIER"
    case "$TIER" in
      0) MULT=0 ;;
      1) MULT=100 ;;
      2) MULT=500 ;;
      3) MULT=1500 ;;
      4) MULT=3000 ;;
    esac
    EQUIV=$(( LINES * MULT / 1000 ))
    FLOOR="No"
    if [ "$TIER" -ge 3 ] && [ "$LINES" -lt 30 ]; then
      if [ "$EQUIV" -lt 150 ]; then
        EQUIV=150
        FLOOR="Yes"
      fi
    fi
    echo "$FILE|$LINES|$TIER|$MULT|$EQUIV|$FLOOR|OVERRIDE" >> "$CLASSIFICATION_FILE"
    continue
  fi

  # --- Tier 0 checks (ANY of these) ---
  IS_TIER0="no"

  case "$(basename "$FILE")" in
    package-lock.json|yarn.lock|pnpm-lock.yaml|CHANGELOG*|LICENSE*) IS_TIER0="yes" ;;
  esac

  # README under 20 lines with very low density
  case "$(basename "$FILE")" in
    README*|readme*)
      if [ "$LINES" -lt 20 ] && [ "$DENS" -lt 30 ]; then
        IS_TIER0="yes"
      fi
      ;;
  esac

  if [ "$IS_TIER0" = "yes" ]; then
    echo "$FILE|$LINES|0|0|0|No|$DENS" >> "$CLASSIFICATION_FILE"
    continue
  fi

  # --- Tier assignment by density (primary) with count confirmation ---
  if [ "$DENS" -ge 200 ]; then
    # Candidate Tier 4: Novel Methodology
    if [ "$INST" -ge 12 ] && [ "$CONS" -ge 8 ]; then
      TIER=4; MULT=3000
    elif [ "$INST" -lt 8 ] && [ "$CONS" -lt 5 ]; then
      TIER=3; MULT=1500
    else
      TIER=3; MULT=1500
    fi

  elif [ "$DENS" -ge 100 ]; then
    # Candidate Tier 3: Domain Expertise
    if [ "$INST" -lt 4 ] && [ "$CONS" -lt 3 ]; then
      TIER=2; MULT=500
    else
      TIER=3; MULT=1500
    fi

  elif [ "$DENS" -ge 30 ]; then
    # Candidate Tier 2: Structured Knowledge
    if [ "$CONS" -lt 3 ] && [ "$COND" -lt 3 ]; then
      TIER=1; MULT=100
    else
      TIER=2; MULT=500
    fi

  else
    # density < 30: Candidate Tier 1 (Boilerplate)
    if [ "$INST" -ge 3 ] || [ "$COND" -ge 3 ]; then
      TIER=2; MULT=500
    else
      TIER=1; MULT=100
    fi
  fi

  # --- Compute equivalent effort LOC ---
  EQUIV=$(( LINES * MULT / 1000 ))

  # --- Short file floor for Tier 3+ ---
  FLOOR="No"
  if [ "$TIER" -ge 3 ] && [ "$LINES" -lt 30 ]; then
    if [ "$EQUIV" -lt 150 ]; then
      EQUIV=150
      FLOOR="Yes"
    fi
  fi

  echo "$FILE|$LINES|$TIER|$MULT|$EQUIV|$FLOOR|$DENS" >> "$CLASSIFICATION_FILE"
done < "$SIGNALS_FILE"

# --- Handle overflow files (defaulted to Tier 1) ---
if [ -f "$IE_TMPDIR/overflow.txt" ]; then
  while IFS='|' read -r FILE LINES; do
    LINES=${LINES:-0}; LINES=$((LINES + 0))
    EQUIV=$(( LINES * 100 / 1000 ))
    echo "$FILE|$LINES|1|100|$EQUIV|No|0" >> "$CLASSIFICATION_FILE"
  done < "$IE_TMPDIR/overflow.txt"
fi

echo "=== CLASSIFICATION COMPLETE ==="
wc -l < "$CLASSIFICATION_FILE" | tr -d ' ' | xargs -I{} echo "FILES_CLASSIFIED={}"
```

#### Tier Decision Tree (Reference)

Density thresholds use permille (per-1000) integer values:
- 30 permille = 0.03 density
- 100 permille = 0.10 density
- 200 permille = 0.20 density

Multipliers are also stored as integer permille (100 = 0.1x, 500 = 0.5x, 1500 = 1.5x, 3000 = 3.0x).

```
DECISION: Intellectual Effort Tier
|
+-- CHECK: Does file have frontmatter override tag?
|   YES -> Use declared tier. Skip remaining checks.
|
+-- TIER 0: Excluded (multiplier = 0)
|  Criteria (ANY of):
|    - Auto-generated marker in first 5 lines
|    - JSON/YAML file > 50KB with CONDITIONAL + CONSTRAINT < 10
|    - Lock files, changelog, license files
|    - README under 20 lines with density_permille < 30
|
+-- TIER 1: Boilerplate (multiplier = 0.1x)
|  Criteria:
|    - density_permille < 30 (primary)
|    - Confirmed by: INSTRUCTION < 3 AND CONDITIONAL < 3
|    - If density < 30 but INSTRUCTION >= 3 OR CONDITIONAL >= 3, promote to Tier 2
|
+-- TIER 2: Structured Knowledge (multiplier = 0.5x)
|  Criteria:
|    - density_permille 30-99 (primary)
|    - Confirmed by: CONSTRAINT >= 3 OR CONDITIONAL >= 3
|    - If density 30-99 but CONSTRAINT < 3 AND CONDITIONAL < 3, demote to Tier 1
|
+-- TIER 3: Domain Expertise (multiplier = 1.5x)
|  Criteria:
|    - density_permille 100-199 (primary)
|    - Demotion: if INSTRUCTION < 4 AND CONSTRAINT < 3, demote to Tier 2
|
+-- TIER 4: Novel Methodology (multiplier = 3.0x)
   Criteria:
     - density_permille >= 200 (primary)
     - Confirmed by: INSTRUCTION >= 12 AND CONSTRAINT >= 8
     - If confirmation fails: demote to Tier 3
```

#### Git Revision History Signal (optional, advisory only)

Git history is used ONLY as a promotion/demotion signal. It is NOT required for any tier classification. If git is unavailable, skip this step entirely.

```bash
echo "=== REVISION DEPTH CHECK (ADVISORY) ==="
# Only run if git is available
if git rev-parse --git-dir > /dev/null 2>&1; then
  REVISED_FILE="$IE_TMPDIR/classifications_revised.txt"
  > "$REVISED_FILE"

  while IFS='|' read -r FILE LINES TIER MULT EQUIV FLOOR DENS; do
    # Only check Tier 3+ files for revision-based adjustments
    if [ "$TIER" -ge 3 ]; then
      REVISIONS=$(git log --oneline -- "$FILE" 2>/dev/null | wc -l | tr -d ' ')
      echo "REVISIONS|$FILE|$REVISIONS|TIER=$TIER"

      if [ "$REVISIONS" -ge 10 ] && [ "$TIER" -eq 3 ]; then
        # Promote Tier 3 -> Tier 4
        TIER=4; MULT=3000
        EQUIV=$(( LINES * MULT / 1000 ))
        if [ "$LINES" -lt 30 ] && [ "$EQUIV" -lt 150 ]; then
          EQUIV=150
          FLOOR="Yes"
        fi
        echo "PROMOTED|$FILE|T3->T4 (10+ revisions)"
      elif [ "$REVISIONS" -le 1 ] && [ "$TIER" -eq 4 ]; then
        # Demote Tier 4 -> Tier 3
        TIER=3; MULT=1500
        EQUIV=$(( LINES * MULT / 1000 ))
        if [ "$LINES" -lt 30 ] && [ "$EQUIV" -lt 150 ]; then
          EQUIV=150
          FLOOR="Yes"
        fi
        echo "DEMOTED|$FILE|T4->T3 (0-1 revisions)"
      fi
    fi
    echo "$FILE|$LINES|$TIER|$MULT|$EQUIV|$FLOOR|$DENS" >> "$REVISED_FILE"
  done < "$CLASSIFICATION_FILE"

  # Replace original with revised version
  mv "$REVISED_FILE" "$CLASSIFICATION_FILE"
else
  echo "SKIP: git not available or not a git repository. Revision check skipped."
fi
```

### Phase 1.5 Output Format

Produce a structured summary for use in Phase 3. Cap TIER_DETAIL to 30 rows (top 30 by equivalent effort LOC descending); summarize remaining files as a single aggregate row.

```
INTELLECTUAL_EFFORT_SUMMARY:
  total_candidates: {N}
  excluded_auto_generated: {N}
  overflow_defaulted_to_t1: {N or 0}
  tier_counts: [T0: {N}, T1: {N}, T2: {N}, T3: {N}, T4: {N}]

  TIER_DETAIL (top 30 by equiv effort LOC):
  | File | Lines | Tier | Multiplier (permille) | Density (permille) | Equivalent Effort LOC | Floor Applied |
  |------|-------|------|-----------------------|--------------------|----------------------|---------------|
  | path/to/file.md | 450 | T3 | 1500 | 140 | 675 | No |
  | path/to/short.md | 15 | T3 | 1500 | 250 | 150* | Yes |
  | (remaining N files) | {sum} | - | - | - | {sum} | - |

  total_physical_lines: {sum of all classified file lines}
  total_equivalent_effort_loc: {sum of equivalent_effort_LOC for each file}
```

---

## PHASE 2: Complexity Assessment

Using Grep and Read, assess each factor on a 1-5 scale. For each factor, run the specified grep commands, count unique matching files, and map the count to a score.

**Deterministic search commands and scoring:**

#### Factor 1: External Integrations
```bash
echo "=== EXTERNAL INTEGRATIONS ==="
timeout 30 grep -rl --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.swift' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl' -E '(fetch\(|axios\.|httpClient|requests\.(get|post|put|delete)|HttpClient|http\.Get|http\.Post|urllib|aiohttp|got\(|ky\(|superagent|RestTemplate|WebClient|Faraday|HTTPoison|reqwest)' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__ 2>/dev/null | sort -u | wc -l
```
Score mapping (unique files with matches): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

#### Factor 2: Data Layer
```bash
echo "=== DATA LAYER ==="
timeout 30 grep -rl --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl' -E '(prisma|sequelize|typeorm|sqlalchemy|ActiveRecord|gorm\.Open|diesel::|mongoose|knex|drizzle|createConnection|createPool|pgPool|redis\.|Redis\(|amqp|kafka|RabbitMQ|Celery|Bull|BullMQ|entity\(|Repository|migration)' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__ 2>/dev/null | sort -u | wc -l
```
Score mapping (unique files): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

#### Factor 3: Auth & Authorization
```bash
echo "=== AUTH ==="
timeout 30 grep -rl --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl' -E '(jwt|JWT|oauth|OAuth|passport|devise|guardian|auth0|firebase\.auth|cognito|session\.(get|set|create|destroy)|bcrypt|argon2|RBAC|ABAC|permission|role.*check|canActivate|authorize|@RequiresPermission)' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__ 2>/dev/null | sort -u | wc -l
```
Score mapping (unique files): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

#### Factor 4: Testing Maturity
```bash
echo "=== TESTING ==="
timeout 30 find . -type f \( -name '*.test.*' -o -name '*.spec.*' -o -name 'test_*' -o -name '*_test.go' -o -name '*_test.py' -o -name '*Test.java' -o -name '*_test.rs' \) -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' 2>/dev/null | wc -l
```
Score mapping (test files): 0 = 1, 1-3 = 2, 4-10 = 3, 11-25 = 4, 26+ = 5

#### Factor 5: Infrastructure/DevOps
```bash
echo "=== INFRA ==="
timeout 30 find . -type f \( -name 'Dockerfile*' -o -name 'docker-compose*' -o -name '*.tf' -o -name '*.hcl' -o -name 'Jenkinsfile' -o -name '.gitlab-ci.yml' -o -name 'Chart.yaml' -o -name 'skaffold.yaml' -o -name 'kustomization.yaml' \) -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/.next/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/out/*' -not -path '*/bin/*' -not -path '*/obj/*' -not -path '*/Pods/*' -not -path '*/DerivedData/*' -not -path '*/.dart_tool/*' -not -path '*/generated/*' -not -path '*/__generated__/*' 2>/dev/null | wc -l
WORKFLOW_COUNT=$(timeout 30 find . -path '*/.github/workflows/*.yml' -o -path '*/.github/workflows/*.yaml' -o -path '*/.circleci/*' 2>/dev/null | wc -l | tr -d ' ')
echo "INFRA_EXTRAS=$WORKFLOW_COUNT"
```
Score mapping (total infra files + workflow files): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

#### Factor 6: Error Handling & Observability
```bash
echo "=== OBSERVABILITY ==="
timeout 30 grep -rl --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl' -E '(sentry|Sentry|datadog|DataDog|newrelic|NewRelic|winston|pino|bunyan|log4j|logrus|zap\.Logger|structlog|ErrorBoundary|error_handler|circuit.?breaker|retry.*policy|@Retry|tenacity)' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__ 2>/dev/null | sort -u | wc -l
```
Score mapping (unique files): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

#### Factor 7: Documentation
```bash
echo "=== DOCS ==="
DOC_COUNT=0
[ -f "README.md" ] || [ -f "README.rst" ] || [ -f "readme.md" ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -d "docs" ] || [ -d "doc" ] || [ -d "documentation" ] && DOC_COUNT=$((DOC_COUNT + 2))
timeout 30 find . -maxdepth 3 -type f \( -name 'openapi.*' -o -name 'swagger.*' -o -name '*.apib' \) 2>/dev/null | head -1 | grep -q . && DOC_COUNT=$((DOC_COUNT + 1))
timeout 30 find . -maxdepth 2 -type d -name 'adr' -o -name 'decisions' 2>/dev/null | head -1 | grep -q . && DOC_COUNT=$((DOC_COUNT + 1))
echo "DOC_SCORE_RAW=$DOC_COUNT"
```
Score mapping (DOC_COUNT): 0 = 1, 1 = 2, 2 = 3, 3-4 = 4, 5 = 5

#### Factor 8: Security Posture
```bash
echo "=== SECURITY ==="
timeout 30 grep -rl --include='*.py' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.go' --include='*.java' --include='*.rb' --include='*.rs' --include='*.php' --include='*.cs' --include='*.kt' --include='*.dart' --include='*.vue' --include='*.svelte' --include='*.sql' --include='*.sh' --include='*.bash' --include='*.zsh' --include='*.lua' --include='*.ex' --include='*.exs' --include='*.hs' --include='*.scala' --include='*.clj' --include='*.r' --include='*.R' --include='*.m' --include='*.zig' --include='*.nim' --include='*.tf' --include='*.hcl' --include='*.yaml' --include='*.yml' --include='*.json' -E '(helmet|cors\(|rateLimit|rate.?limit|CSP|Content-Security-Policy|sanitize|validator|DOMPurify|escape.*html|parameterize|prepared.?statement|sql.?injection|XSS|CSRF|csrf|dependabot|snyk|trivy|secret.*manager|vault|SOPS)' . --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor --exclude-dir=dist --exclude-dir=build --exclude-dir=.next --exclude-dir=__pycache__ --exclude-dir=.venv --exclude-dir=venv --exclude-dir=target --exclude-dir=out --exclude-dir=bin --exclude-dir=obj --exclude-dir=Pods --exclude-dir=DerivedData --exclude-dir=.dart_tool --exclude-dir=generated --exclude-dir=__generated__ 2>/dev/null | sort -u | wc -l
```
Score mapping (unique files): 0 = 1, 1-2 = 2, 3-5 = 3, 6-9 = 4, 10+ = 5

**Scoring rules:**
- Each score MUST be a whole integer from 1 to 5. No half points.
- If no evidence is found for a factor, score it 1.
- Justification must cite a specific file, directory, or pattern found (or "no evidence found" for score 1).

**If Grep or Read fails for a specific search** (e.g., binary file, permission error), skip that search and base the score on other available evidence. If no searches succeed for a factor, score it 1 with justification "unable to assess -- filesystem errors."

---

## PHASE 3: Parametric Estimation (Simplified COCOMO II)

This model uses the COCOMO II base equation with simplified driver mappings. Where full COCOMO II requires 5 Scale Factors and 17 Effort Multipliers rated by human experts, this automated model maps the 8 codebase complexity factors to the most relevant Effort Multipliers, defaulting unobservable drivers to Nominal (1.0).

### Step 3.1: Effective KLOC

- **If cloc was used:** Sum the `code` lines across all languages from the cloc JSON output (exclude comments and blanks). Divide by 1000. This is your Effective KLOC.
- **If cloc returned valid JSON but all languages had code: 0:** Set `EMPTY_REPO` and abort with: "cloc found no code lines in any language. Cost estimation requires at least one line of code." (Exception: if `CONFIG_ONLY` applies, do not abort -- use Config LOC * 0.3x instead.)
- **If wc fallback was used:** Take the source code raw total (NOT config/markup), subtract any generated/vendored lines found in Phase 1a, multiply by **0.7** (to estimate code-only lines excluding blanks/comments), then divide by 1000 for KLOC.
- **If `CONFIG_ONLY` flag is set:** Use Config/Markup LOC * **0.3** / 1000 for KLOC.
- **Rounding:** Round KLOC to 1 decimal place (e.g., 12.3 KLOC). If KLOC < 1.0, show 2 decimal places (e.g., 0.45 KLOC).

### Step 3.2: Language Breakdown for Function Points

Record each language and its code-line count. Rules:

- **Maximum languages in report:** List the top 8 languages by LOC. Group all remaining languages under "Other" with their combined LOC.
- **If cloc was used:** Use the per-language `code` values directly.
- **If wc fallback was used:** Group by file extension. Map extensions to language names. Apply the 0.7x multiplier to each language's raw line count individually.

### Step 3.3: Scale Factors and Exponent E

COCOMO II uses 5 Scale Factors (SF) to compute the exponent E. Since we cannot interview the team, use the project classification to set aggregate SF values:

Compute the **arithmetic mean** of all 8 complexity scores from Phase 2. Round to 1 decimal place.

| Average Score | Classification | Sum of Scale Factors (SF_total) | Exponent E |
|---------------|----------------|--------------------------------|------------|
| 1.0 - 2.0 | **Simple** -- Small scope, well-understood problem | 15.0 | 0.91 + 0.01 * 15.0 = 1.06 |
| 2.1 - 3.5 | **Moderate** -- Medium scope, mixed complexity | 25.0 | 0.91 + 0.01 * 25.0 = 1.16 |
| 3.6 - 5.0 | **Complex** -- Large scope, tight constraints, high reliability | 35.0 | 0.91 + 0.01 * 35.0 = 1.26 |

### Step 3.4: Effort Multipliers (EM)

Map the 8 complexity factors to COCOMO II Effort Multipliers. Factors that don't map to a published EM contribute context to the report but do not affect the EAF calculation.

**CPLX Score-to-EM lookup table** (used by both External Integrations and Auth & Authorization):

| Score | CPLX EM Value |
|-------|---------------|
| 1 | 0.73 |
| 2 | 0.87 |
| 3 | 1.00 |
| 4 | 1.17 |
| 5 | 1.34 |

**Full EM mapping:**

| Factor | COCOMO II EM Mapping | Score-to-EM Value |
|--------|---------------------|-------------------|
| External Integrations | CPLX (Product Complexity) | Use CPLX lookup table above |
| Data Layer | DATA (Database Size) | 1->0.90, 2->0.93, 3->1.00, 4->1.10, 5->1.28 |
| Auth & Authorization | CPLX supplement (see combining rule below) | Uses same CPLX lookup table above |
| Testing Maturity | RELY (Required Reliability) -- inverted: more tests = higher reliability req | 1->0.82, 2->0.92, 3->1.00, 4->1.10, 5->1.26 |
| Infrastructure/DevOps | PLEX (Platform Experience) -- inverted: complex infra = less familiarity | 1->0.87, 2->0.91, 3->1.00, 4->1.09, 5->1.19 |
| Error Handling & Observability | Contextual only | 1.00 (Nominal -- not multiplied) |
| Documentation | DOCU (Documentation Match) | 1->0.81, 2->0.91, 3->1.00, 4->1.11, 5->1.23 |
| Security Posture | Contextual only | 1.00 (Nominal -- not multiplied) |

**EM values are from Boehm et al. (2000), Table 2.16 (published rating scales).**

**Auth & Authorization combining rule:** Auth uses the same CPLX lookup table as External Integrations. If the Auth score differs from the External Integrations score by more than 1 point, compute the CPLX EM as the **geometric mean** of both scores' CPLX values. Otherwise, use the External Integrations score alone for CPLX.

**Worked example:** Integrations = 2 (CPLX = 0.87), Auth = 5 (CPLX = 1.34). Difference = 3 > 1, so use geometric mean: CPLX_EM = sqrt(0.87 * 1.34) = sqrt(1.1658) = 1.08.

Remaining 12 COCOMO II EMs not mapped above default to Nominal (1.0).

### Step 3.5: Effort Adjustment Factor (EAF)

```
EAF = CPLX_EM * DATA_EM * RELY_EM * PLEX_EM * DOCU_EM
```

(Product of the 5 mapped EMs. All unmapped EMs are 1.0 and drop out.)

### Step 3.6: Core Calculations

```
Effort (person-months) = 2.94 * (KLOC ^ E) * EAF
Person-Hours = Effort * 152
```

**Schedule (Tdev):**
```
Tdev (months) = 3.67 * (Effort ^ F)
where F = 0.28 + 0.2 * (E - 0.91)
```

**Rounding rules for all calculations:**
- Person-months: 1 decimal place (e.g., 14.3)
- Person-hours: round to nearest 10 (e.g., 2170)
- Tdev: 1 decimal place (e.g., 6.2)
- All intermediate calculations: use full precision; only round final displayed values.

### Step 3.6b: Intellectual Effort Integration

After computing the COCOMO base effort, integrate intellectual effort artifacts. This step runs the deduplication against the Phase 1a manifest and computes the combined effort.

```bash
echo "=== PHASE 3: INTELLECTUAL EFFORT INTEGRATION ==="

# --- Input validation ---
ORIGINAL_LOC=${ORIGINAL_LOC:-0}
if [ "$ORIGINAL_LOC" -eq 0 ]; then
  echo "WARNING: ORIGINAL_LOC is 0 or not set. Skipping COCOMO LOC adjustment."
  SKIP_COCOMO_ADJUSTMENT="yes"
else
  SKIP_COCOMO_ADJUSTMENT="no"
fi

# --- Step 3a: Deduplication against Phase 1a manifest ---
MANIFEST="phase1a-manifest.txt"
DEDUP_SUBTRACT="$IE_TMPDIR/dedup_subtract.txt"
> "$DEDUP_SUBTRACT"
IE_TOTAL_EQUIV=0
DEDUP_LINES_SUBTRACTED=0

if [ -f "$MANIFEST" ]; then
  echo "Phase 1a manifest found. Deduplication enabled."

  while IFS='|' read -r FILE LINES TIER MULT EQUIV FLOOR DENS; do
    LINES=${LINES:-0}; LINES=$((LINES + 0))
    EQUIV=${EQUIV:-0}; EQUIV=$((EQUIV + 0))

    if [ "$TIER" -ge 2 ]; then
      # Normalize path: strip leading ./ from both sides for matching
      NORM_FILE=$(echo "$FILE" | sed 's|^\./||')
      MANIFEST_MATCH=$(awk -F'|' -v f="$NORM_FILE" '{gsub(/^\.\//,"",$2)} $2==f {print $1"|"$3}' "$MANIFEST")

      if [ -n "$MANIFEST_MATCH" ]; then
        # File is in COCOMO count -- subtract its lines from COCOMO, add equiv to IE
        COCOMO_LANG=$(echo "$MANIFEST_MATCH" | cut -d'|' -f1)
        COCOMO_LINES=$(echo "$MANIFEST_MATCH" | cut -d'|' -f2)
        COCOMO_LINES=${COCOMO_LINES:-0}; COCOMO_LINES=$((COCOMO_LINES + 0))
        echo "$COCOMO_LANG|$COCOMO_LINES" >> "$DEDUP_SUBTRACT"
        DEDUP_LINES_SUBTRACTED=$((DEDUP_LINES_SUBTRACTED + COCOMO_LINES))
        echo "DEDUP_RECLASSIFY|$FILE|subtract $COCOMO_LINES COCOMO lines ($COCOMO_LANG)|add $EQUIV equiv LOC"
      fi
      IE_TOTAL_EQUIV=$((IE_TOTAL_EQUIV + EQUIV))
    fi
    # Tier 0 and Tier 1 files: leave in COCOMO, do not add to IE total
  done < "$CLASSIFICATION_FILE"
else
  echo "WARNING: Deduplication disabled; Phase 1a manifest not found."
  # Add all Tier 2+ equiv LOC without subtracting from COCOMO
  while IFS='|' read -r FILE LINES TIER MULT EQUIV FLOOR DENS; do
    EQUIV=${EQUIV:-0}; EQUIV=$((EQUIV + 0))
    if [ "$TIER" -ge 2 ]; then
      IE_TOTAL_EQUIV=$((IE_TOTAL_EQUIV + EQUIV))
    fi
  done < "$CLASSIFICATION_FILE"
fi

echo "DEDUP_LINES_SUBTRACTED=$DEDUP_LINES_SUBTRACTED"
echo "IE_TOTAL_EQUIV_LOC=$IE_TOTAL_EQUIV"

# --- Step 3b: Compute adjusted KLOC for COCOMO ---
if [ "$SKIP_COCOMO_ADJUSTMENT" = "yes" ]; then
  ADJUSTED_LOC=$ORIGINAL_LOC
  echo "ADJUSTED_LOC=$ADJUSTED_LOC (no adjustment)"
else
  ADJUSTED_LOC=$((ORIGINAL_LOC - DEDUP_LINES_SUBTRACTED))
  if [ "$ADJUSTED_LOC" -lt 0 ]; then
    echo "WARNING: ADJUSTED_LOC went negative. Clamping to 0."
    ADJUSTED_LOC=0
  fi
  echo "ADJUSTED_LOC=$ADJUSTED_LOC (original $ORIGINAL_LOC minus $DEDUP_LINES_SUBTRACTED reclassified)"
fi

# --- Step 3c: Compute intellectual effort hours ---
# HOURS_PER_KLOC derived from COCOMO: COCOMO_person_hours / COCOMO_KLOC
HOURS_PER_KLOC=${HOURS_PER_KLOC:-100}  # fallback: 100 hours/KLOC if not set
IE_HOURS=$(( IE_TOTAL_EQUIV * HOURS_PER_KLOC / 1000 ))
IE_PM=$(( IE_HOURS * 100 / 15200 ))  # person-months * 100 for 2-decimal precision
IE_PM_INT=$((IE_PM / 100))
IE_PM_FRAC=$((IE_PM % 100))

echo "IE_HOURS=$IE_HOURS"
echo "IE_PERSON_MONTHS=${IE_PM_INT}.${IE_PM_FRAC}"
echo "=== PHASE 3 INTEGRATION COMPLETE ==="
```

**Adjusted KLOC:** After deduplication, recompute KLOC = ADJUSTED_LOC / 1000 and re-run the COCOMO formula with this adjusted value. The adjusted COCOMO effort plus the intellectual effort hours gives the combined total.

**Combined effort:**
```
Total_Effort_Hours = COCOMO_Effort_Hours (using adjusted KLOC) + IE_Hours
Total_Effort_PM = Total_Effort_Hours / 152
```

The IE_Hours use the project's own COCOMO-derived hours/KLOC rate (`COCOMO_person_hours / COCOMO_KLOC`), so intellectual effort scales with project complexity.

### Step 3.7: Function Points (secondary metric)

Use these LOC-per-FP ratios to estimate function points from code lines (source: Jones, C. Applied Software Measurement, 3rd ed. McGraw-Hill):

| Language | LOC/FP |
|----------|--------|
| Python | 40 |
| JavaScript/TypeScript | 47 |
| Ruby | 40 |
| Go | 50 |
| Rust | 55 |
| Java | 53 |
| C# | 54 |
| C/C++ | 97 |
| PHP | 50 |
| Swift/Kotlin | 45 |
| Dart | 45 |
| Elixir/Erlang | 35 |
| Haskell/Scala | 35 |
| SQL | 30 |
| Shell/Bash | 50 |
| Terraform/HCL | 55 |
| Lua | 45 |
| Zig/Nim | 55 |
| R | 40 |
| Clojure | 35 |

**Excluded from FP calculation:** HTML, CSS, SCSS, SASS, LESS, YAML, JSON, XML, Markdown. These represent markup/configuration, not functional requirements. Report their LOC in the Codebase Profile but do not convert to FP.

**Multi-language function point calculation:**

1. For each source-code language detected, divide that language's code lines by its LOC/FP ratio to get that language's function points.
2. Sum all per-language function points. This is the Source Code FP.
3. **If a language is not in the table above**, use a default of **50 LOC/FP**.
4. **Intellectual Effort FP:** `IE_FP = total_equivalent_effort_LOC / 40` (unified ratio for all IE artifacts; midpoint between declarative language density ~50 LOC/FP per Jones 2008 and specification density ~30 LOC/FP per IFPUG SNAP v2.4).
5. `Total_FP = Source_Code_FP + IE_FP`
6. Round total FP to the nearest whole number.

### Step 3.8: Effort Ranges

| Range | Multiplier | Use |
|-------|------------|-----|
| **Low** | 0.6x | Well-understood domain, experienced team, clean requirements |
| **Mid** | 1.0x | Baseline estimate |
| **High** | 1.6x | Novel domain, team ramp-up, evolving requirements |

Apply these multipliers to Effort (person-months) and Person-Hours. Round using the same rules as Step 3.6.

---

## PHASE 4: Cost Calculation

Apply these four team profiles to the person-hours from Phase 3.

### Team Profiles

| Profile | Blended $/hr | Overhead Multiplier | Effective Devs | Description |
|---------|-------------|---------------------|-----------------|-------------|
| **Solo Senior** | $125 | 1.0x | 1 | One expert doing everything |
| **Lean Startup** | $115 | 1.15x | 2-3 | Small focused team, minimal process |
| **Growth Company** | $125 | 1.35x | 5-8 | Mid-size team, some process overhead |
| **Enterprise** | $145 | 1.65x | 10+ | Large team, full SDLC process |

**Note:** The parametric effort estimates include direct development activities. The overhead multiplier covers activities outside the model's scope: hiring/onboarding, organizational coordination, compliance processes, and institutional overhead that scales with team size. For Solo Senior (1.0x), no additional overhead is applied because the model's baseline assumes a single-contributor context.

### Calculation per profile

```
Total Cost = Person-Hours * Blended Rate * Overhead Multiplier
Naive Calendar Time = Person-Hours / (Effective Devs * 152)
Calendar Time = max(Naive Calendar Time, Tdev)
```

**Calendar Time** is the greater of naive parallelization (hours / headcount / 152) and COCOMO II schedule estimate (Tdev). Tdev represents the minimum feasible schedule regardless of staffing; adding more people does not reduce it below Tdev.

**For Calendar Time, use these exact values for Effective Devs:**
- Solo Senior: 1
- Lean Startup: 2.5
- Growth Company: 6.5
- Enterprise: 12

**Produce Low / Mid / High for each profile.**

**Rounding rules:**
- Costs under $10,000: round to nearest $100, display as "$X,XXX" (e.g., "$4,200")
- Costs $10,000 - $999,999: round to nearest $1,000, display as "$XXXK" (e.g., "$247K")
- Costs $1,000,000+: round to nearest $10,000, display as "$X.XXM" (e.g., "$1.24M")
- Calendar time: 1 decimal place in months (e.g., "6.2 months")

### Effort Allocation Breakdown (for the Mid estimate)

Show how effort distributes across activities. Use the Growth Company mid-estimate cost as the cost column basis:

| Activity | Percentage |
|----------|------------|
| Development & Coding | 55% |
| Testing & QA | 20% |
| Project Management | 12% |
| DevOps & Infrastructure | 8% |
| Documentation | 5% |

---

## PHASE 5: Report Output

**Output the full report directly in chat AND save it to a file.**

### File Output

After generating the report, save it and optionally generate a PDF:

1. Create the output directory if needed: `mkdir -p tmp`
2. Write the report to `tmp/cost-estimation-YYYY-MM-DD.md` (using today's date)
3. If a file with the same date already exists, append a sequence number: `tmp/cost-estimation-YYYY-MM-DD-2.md`
4. If `PANDOC_AVAILABLE=yes`, generate a PDF using the detected OS fonts:
   ```bash
   # Homebrew init (macOS Apple Silicon)
   [ -x /opt/homebrew/bin/brew ] && eval "$(/opt/homebrew/bin/brew shellenv)"

   # Use OS-appropriate fonts detected in Phase 0
   sed 's/[⬛⬜💰📊🔍⚙️💵🏷️🤖📋👤🚀📈🏢]//g' tmp/cost-estimation-YYYY-MM-DD.md | \
   pandoc -o tmp/cost-estimation-YYYY-MM-DD.pdf \
     --pdf-engine=xelatex \
     -V geometry:margin=1in \
     -V mainfont="${MAIN_FONT}" \
     -V monofont="${MONO_FONT}" \
     -V fontsize=11pt \
     -V colorlinks=true \
     -V linkcolor=NavyBlue \
     -V urlcolor=NavyBlue \
     -V header-includes='\usepackage{booktabs}\usepackage{longtable}\usepackage{fancyhdr}\pagestyle{fancy}\fancyhead[L]{Codebase Cost Estimation}\fancyhead[R]{\today}\fancyfoot[C]{\thepage}\usepackage{titlesec}\titleformat{\section}{\Large\bfseries\color{NavyBlue}}{}{0em}{}\titleformat{\subsection}{\large\bfseries}{}{0em}{}' \
     --from markdown
   ```
   Where `${MAIN_FONT}` and `${MONO_FONT}` are the values detected in Phase 0 (macOS: Helvetica/Menlo, Linux: DejaVu Sans/DejaVu Sans Mono).
   If the pandoc command fails (non-zero exit), report: "PDF generation failed (pandoc/xelatex error). Markdown report saved successfully."
5. Report the file paths at the end of the output:
   ```
   ---
   **Files saved:**
   - 📄 `tmp/cost-estimation-YYYY-MM-DD.md`
   - 📑 `tmp/cost-estimation-YYYY-MM-DD.pdf` (generated via pandoc + xelatex)
   ```
   If pandoc is not available or PDF generation failed, only show the MD line and note: `(install pandoc + xelatex for automatic PDF generation)`

### Report Template

Format the report as clean markdown with exactly this structure. Every field derivation is annotated below in `[brackets]` -- these annotations must NOT appear in the final report. Replace every `{...}` placeholder with a computed value. If a value cannot be computed, use the specified fallback shown after the `||` symbol.

---

```markdown
# 💰 Codebase Cost Estimation Report

> **Repository:** `{repo name from basename of pwd}`
> **Analysis Date:** {YYYY-MM-DD, today's date}
> **Methodology:** Simplified Parametric Model based on COCOMO II

---

## 📊 Codebase Profile

| Metric | Value |
|--------|-------|
| **Languages** | {top N languages (max 8) with LOC each, e.g. "TypeScript (12,400), Python (3,200), Shell (800)" || "Unable to determine"} |
| **Total Lines of Code** | {raw total lines before any multiplier || "Unable to count"} |
| **Effective KLOC** | {code-only KLOC from Step 3.1, e.g. "12.3 KLOC" || "Unable to compute"} |
| **Configuration LOC** | {HTML/CSS/YAML/JSON/XML/Markdown lines -- reported for context, not used in COCOMO calculation || "0"} |
| **Total Files** | {from Phase 1c || "Unable to count"} |
| **Git Commits** | {from Phase 1b || "N/A -- no git history"} |
| **Contributors** | {count from Phase 1b || "N/A -- no git history"} |
| **Repository Age** | {duration between first and last commit, e.g. "2 years, 3 months" || "N/A -- no git history"} |
| **Active Development** | {first commit date} -> {last commit date} || "N/A -- no git history" |
| **Tech Stack** | {detected frameworks/tools from Phase 1d, max 10 items, comma-separated} |
```

[If `MONOREPO` flag is set, add this subsection immediately after the Codebase Profile table:]

```markdown
### Monorepo Structure

This repository is a monorepo. The following packages/modules were detected:

| Package | Path |
|---------|------|
| {package name} | {relative path} |
...

(List max 15 packages. If more exist, add row: "... and {N} more packages")

All packages are analyzed as a single aggregate project for cost estimation purposes.
```

[If `TINY_REPO` flag is set, add this notice immediately after the Codebase Profile table:]

```markdown
> **Note:** This codebase is under 500 effective LOC. The parametric model is calibrated for projects above 2 KLOC. The estimates below have low confidence and should be treated as rough order-of-magnitude only.
```

[If `CONFIG_ONLY` flag is set, add this notice immediately after the Codebase Profile table:]

```markdown
> **Note:** This repository consists primarily of configuration/infrastructure-as-code. KLOC is derived from config LOC at 0.3x weighting. The parametric model is designed for application software; estimates may not reflect actual effort accurately.
```

```markdown
## 🔍 Complexity Assessment

| Factor | Score | Justification |
|--------|-------|---------------|
| External Integrations | ⬛⬛⬜⬜⬜ 2/5 | {max 15 words citing evidence} |
| Data Layer | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Auth & Authorization | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Testing Maturity | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Infrastructure/DevOps | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Error Handling | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Documentation | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| Security Posture | {⬛/⬜ bar} {N}/5 | {max 15 words} |
| **Average** | **{X.X}/5** | **{Simple/Moderate/Complex}** |
```

[Score bars: use N filled ⬛ followed by (5-N) empty ⬜, e.g. score 3 = ⬛⬛⬛⬜⬜]

[If any Tier 2+ intellectual effort artifacts were found, include this section. If no Tier 2+ files found, collapse to a single line: "No significant intellectual effort artifacts detected beyond standard configuration."]

```markdown
## Intellectual Effort Artifacts

Non-code files representing significant domain expertise, prompt engineering, or encoded methodology.

| Classification | Files | Physical Lines | Equiv. Effort LOC | Key Files |
|----------------|-------|---------------|-------------------|-----------|
| Novel Methodology (T4, 3.0x) | {N} | {N} | {N} | {top 3 file names} |
| Domain Expertise (T3, 1.5x) | {N} | {N} | {N} | {top 3 file names} |
| Structured Knowledge (T2, 0.5x) | {N} | {N} | {N} | {top 3 file names} |
| Boilerplate (T1, 0.1x) | {N} | {N} | {N} | (not listed) |
| Excluded (T0) | {N} | {N} | 0 | (not listed) |
| **Total** | **{N}** | **{N}** | **{N}** | |

> Intellectual effort artifacts add **{equivalent_effort_LOC}** equivalent LOC to the project,
> representing **{percentage of total effort}%** of total estimated effort.
```

[Display rules: Only show tiers that have >= 1 file. Tiers ordered descending: T4, T3, T2, T1, T0. List "Key Files" for Tier 2+ only (max 3 files per tier, sorted by equivalent_effort_LOC descending). Files with short file floor applied are marked with *.]

```markdown
## ⚙️ Effort Estimation

| Parameter | Value |
|-----------|-------|
| Effective KLOC | {from Step 3.1} |
| Project Type | {from Step 3.3} |
| Exponent E | {from Step 3.3} |
| Effort Multipliers | CPLX={val}, DATA={val}, RELY={val}, PLEX={val}, DOCU={val} |
| EAF (product of EMs) | {from Step 3.5} |
| **Source Code Effort** | **{COCOMO effort using adjusted KLOC, e.g. "12.1 person-months (1,840 hours)"}** |
| **Intellectual Effort Artifacts** | **{IE_PM person-months (IE_Hours hours)}** |
| **Combined Base Effort** | **{Total_Effort_PM person-months (Total_Effort_Hours hours)}** |
| Estimated Function Points | {from Step 3.7, e.g. "270 FP" (Source Code FP + IE FP)} |
| Schedule (Tdev) | {from Step 3.6, e.g. "6.2 months"} (ideal) |

### Effort Range

| | Low (0.6x) | Mid (1.0x) | High (1.6x) |
|---|-----------|-----------|------------|
| **Person-Months** | {Low} | {Mid} | {High} |
| **Person-Hours** | {Low} | {Mid} | {High} |

## 💵 Cost Estimation

### By Team Configuration

| Team Profile | Low | Mid | High | Calendar Time (Mid) |
|-------------|-----|-----|------|-------------------|
| 👤 Solo Senior ($125/hr) | {cost} | {cost} | {cost} | {time} |
| 🚀 Lean Startup ($115/hr, 1.15x OH) | {cost} | {cost} | {cost} | {time} |
| 📈 Growth Co ($125/hr, 1.35x OH) | {cost} | {cost} | {cost} | {time} |
| 🏢 Enterprise ($145/hr, 1.65x OH) | {cost} | {cost} | {cost} | {time} |

### Effort Allocation (Mid Estimate)

| Activity | % | Hours | Cost (Growth Co) |
|----------|---|-------|-----------------|
| Development & Coding | 55% | {Mid Person-Hours * 0.55, rounded to nearest 10} | {cost} |
| Testing & QA | 20% | {Mid Person-Hours * 0.20, rounded to nearest 10} | {cost} |
| Project Management | 12% | {Mid Person-Hours * 0.12, rounded to nearest 10} | {cost} |
| DevOps & Infrastructure | 8% | {Mid Person-Hours * 0.08, rounded to nearest 10} | {cost} |
| Documentation | 5% | {Mid Person-Hours * 0.05, rounded to nearest 10} | {cost} |

## 🏷️ Headline Valuation

| Tier | Estimate | Basis |
|------|----------|-------|
| **Conservative** | **{Solo Senior, Low cost}** | Solo senior, low complexity (0.6x) |
| **Realistic** | **{Growth Company, Mid cost}** | Growth company, mid estimate |
| **Premium** | **{Enterprise, High cost}** | Enterprise team, high estimate (1.6x) |

> **If someone asked "what would it cost to build this from scratch?"**
> The realistic answer is **{Growth Co Low cost} - {Growth Co High cost}** with a team of {Effective Devs for Growth Co} engineers over {Growth Co Calendar Time Mid} months.
> {If IE_Hours > 0: "This includes **{IE_Hours} hours** of intellectual effort in non-code artifacts (prompts, domain configs, methodology documents)."}
```

[ONLY if $ARGUMENTS is non-empty, include the following section. Parse the numeric hours value from the argument string using regex `(\d+\.?\d*)`. If no numeric value is found, show the section with the raw argument text but omit all numeric rows (Speed Multiple, Cost, Cost Savings).]

[Case 1: Numeric value WAS parsed from $ARGUMENTS:]

```markdown
## 🤖 AI Speed Comparison

| Metric | Human Team | AI-Assisted |
|--------|-----------|-------------|
| Build Time | {Mid Person-Hours from Step 3.6} hours | {parsed hours from $ARGUMENTS} hours |
| Speed Multiple | 1x | {Mid Person-Hours / AI hours, rounded to nearest whole number}x faster |
| Cost (at Growth Co rates) | {Growth Co Mid cost} | {AI hours * $125 * 1.35, formatted per rounding rules} |
| Cost Savings | -- | {percentage reduction, rounded to nearest 1%}% |

> AI-assisted development completed in **{$ARGUMENTS}** what would take a human team **{Mid Person-Hours} hours** -- a **{speed multiple}x speedup**.
```

[Case 2: No numeric value could be parsed from $ARGUMENTS:]

```markdown
## 🤖 AI Speed Comparison

> AI-assisted build context: **{raw $ARGUMENTS text}**
>
> A numeric hours value could not be extracted from the input. The human team baseline is **{Mid Person-Hours from Step 3.6} hours** ({Growth Co Mid cost} at Growth Company rates). Provide a numeric hours value (e.g., "30 hours") for a quantitative comparison.
```

[End conditional section]

```markdown
## 📋 Methodology & Assumptions

- **Model:** Simplified parametric model based on COCOMO II (Boehm et al., 2000). Uses the COCOMO II base equation (A=2.94, exponent E from Scale Factors) with 5 of 17 Effort Multipliers mapped from automated codebase analysis; remaining EMs default to Nominal (1.0). This is an automated approximation -- full COCOMO II requires expert calibration of all 22 drivers.
- **Working Hours:** 152 hours/month (19 productive days x 8 hours, accounting for holidays and administrative time)
- **LOC Measurement:** {if cloc: "cloc (code lines only, excluding comments and blanks)" | if wc: "wc -l with 0.7x adjustment for blanks/comments, source code files only"}
- **Rates:** Fully-loaded US consulting/agency rates (2025-2026), not salary equivalents
- **Overhead:** Accounts for hiring/onboarding, organizational coordination, compliance processes, and institutional overhead beyond direct development (see Team Profiles note)
- **Exclusions:** Generated code, lock files, vendored dependencies, build artifacts, config/markup files (from KLOC){if vendored dirs found: ", vendored directories: {list}"}
- **Intellectual Effort:** Non-code artifacts (prompts, domain configs, rubrics) estimated using a 4-tier classification system (Boilerplate 0.1x, Structured Knowledge 0.5x, Domain Expertise 1.5x, Novel Methodology 3.0x) based on automated signal detection (conditional language density, constraint patterns, instructional density). Constants derived from Jones, *Applied Software Measurement* (3rd ed., 2008) and IFPUG SNAP Assessment Practices Manual v2.4 (2017). Intellectual effort estimation is a supplementary methodology, not part of standard COCOMO II.
- **Conservative bias:** Estimates lean toward underestimation; actual costs often exceed parametric predictions for novel or poorly-defined projects
- **Schedule:** COCOMO II Tdev formula: Tdev = 3.67 * PM^F where F = 0.28 + 0.2*(E-0.91); Calendar Time is the greater of naive parallelization (hours / headcount / 152) and Tdev, since Tdev represents the minimum feasible schedule regardless of staffing
{if MONOREPO: "- **Monorepo:** Analyzed as single aggregate project; individual package estimates not provided"}
{if TINY_REPO: "- **Small project caveat:** Model is calibrated for 2+ KLOC projects; sub-500 LOC estimates are low-confidence"}
{if CONFIG_ONLY: "- **Config-only repo:** KLOC derived from configuration LOC at 0.3x weighting; model is designed for application software"}
{if NO_GIT: "- **No git history:** Git-dependent metrics (commits, contributors, age) unavailable"}
{if any TIMEOUT: "- **Data collection timeout:** {list steps that timed out}; those metrics are omitted from the analysis"}

*Sources: Boehm, B. et al. (2000). Software Cost Estimation with COCOMO II. Prentice Hall. Jones, C. Applied Software Measurement, 3rd ed. McGraw-Hill. ZipRecruiter, FullStack Labs, Rise 2026 Contractor Rates.*

---

*Generated by [cost-estimate](https://github.com/mlamp/cost-estimate) -- a Claude Code skill using a simplified parametric model based on COCOMO II*
```

---

## Execution Rules

These rules govern the entire analysis. They are not suggestions.

1. **Parallelism:** Run all Phase 1 data collection steps (1a, 1b, 1c, 1d) in parallel. Phase 1.5 runs after Phase 1a completes, but can run in parallel with 1b, 1c, and 1d.
2. **Precision:** Show actual calculated values in the report. Never leave a `{placeholder}` or `...` in the output.
3. **Currency formatting:** Follow the rounding rules from Phase 4 exactly.
4. **Number formatting:** Use commas for thousands separators in all numbers (e.g., 2,170 not 2170).
5. **Rounding summary:**
   - KLOC: 1 decimal (or 2 if < 1.0)
   - Person-months: 1 decimal
   - Person-hours: nearest 10
   - Costs: see Phase 4 rounding rules
   - Calendar time: 1 decimal in months
   - Function points: nearest whole number
   - Complexity average: 1 decimal
   - Speed multiple (AI comparison): nearest whole number
6. **Language cap:** Maximum 8 languages listed individually. Remainder grouped as "Other."
7. **Justification cap:** Maximum 15 words per complexity factor justification.
8. **Conditional sections:** The AI Speed Comparison section appears ONLY if `$ARGUMENTS` is non-empty. Parse hours using regex `(\d+\.?\d*)`. If no number found, show text-only variant.
9. **Error resilience:** If any single Bash command or tool call fails, continue with remaining data. Never abort the entire analysis due to a single failed command (except for the `EMPTY_REPO` abort condition).
10. **Timeouts:** All `cloc` commands use `timeout 60`. All `find` and `grep` commands use `timeout 30`. If a command times out, treat output as empty and record a TIMEOUT flag for that step.
11. **Intellectual effort rounding:** Equivalent effort LOC: round to nearest whole number. All density and multiplier values in integer permille.
12. **Intellectual effort omission:** If no Tier 2+ intellectual effort artifacts are found, omit the Intellectual Effort Artifacts section from the report and show only: "No significant intellectual effort artifacts detected beyond standard configuration."

---

## Constraints

These are hard constraints on what this skill must NOT do during analysis:

1. **Do not install packages.** Never run `npm install`, `pip install`, `brew install`, `apt install`, `cargo install`, or any package manager install command. Use only tools already present on the system.
2. **Do not modify repository files.** Never write to, edit, or delete any file in the repository being analyzed. The only files this skill creates are the report files in `tmp/`.
3. **Do not run test suites.** Never execute `npm test`, `pytest`, `cargo test`, `go test`, or any test runner. Assess testing maturity by counting test files and searching for test patterns only.
4. **Do not execute application code.** Never run `node`, `python`, `go run`, `cargo run`, or any command that executes the project's own code. Analysis is read-only.
5. **Do not make network requests.** Never use `curl`, `wget`, `fetch`, or any command that makes outbound HTTP/network requests. All analysis is performed using local filesystem inspection and git history.
6. **Do not run destructive commands.** Never use `rm`, `git clean`, `git checkout`, `git reset`, or any command that could alter the working tree or git state.
