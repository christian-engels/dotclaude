---
name: estimate
description: Write or refactor estimation code (regressions, IVs, panel models, DiD / event studies, GMM) so it is human-readable and self-verifying. INVOKE BEFORE typing any of `lm`, `glm`, `feols`, `fixest::*`, `did_imputation`, `att_gt`, `pyfixest.feols`, `statsmodels.OLS/Logit`, Stata `reg`/`xtreg`/`reghdfe`/`ivreghdfe` in a `.R`/`.py`/`.do` file. Use when writing or editing scripts that fit models — typically `04-estimate_*.R` or similar under `1-replication-pack/code/` or `4-things-we-tried/*/code/`, or when refactoring existing estimation code. Enforces explicit specifications (no formulae built from strings, no looped specs, no nested model calls), pre / execute / post verification for each estimator (OLS, FE panel, IV, DiD), and language guardrails (R fixest: explicit cluster always; Python pyfixest: explicit vcov; Stata: vce(cluster ...) always).
---

# Estimate

Write estimation code that a coauthor — or you in six months — can read line by line. Every model object has a name that documents the spec. Every spec comes with its sample, SE method, and identification preconditions visible inline.

## When to use

- Writing or editing scripts that fit statistical models (regressions, IVs, panels, DiD, event studies, GMM) under `1-replication-pack/code/` or `4-things-we-tried/*/code/`.
- Refactoring estimation code that built specs from string concatenation or for-loops.
- The user describes a model: "run this regression", "add firm FE", "instrument X with Z", "estimate the DiD".
- **Self-trigger:** if you find yourself about to type `lm(`, `glm(`, `feols(`, `fixest::`, `did_imputation(`, `att_gt(`, `pyfixest.feols(`, `statsmodels.OLS(` / `.Logit(`, or Stata `reg`/`xtreg`/`reghdfe`/`ivreghdfe` in a `.R`/`.py`/`.do` file, **stop and invoke this skill before writing the line**. Do not rely on the user to remind you.

## Mandatory first step on every invocation: audit the file

Before writing or editing any estimation code in this file:

1. Read the entire file end to end.
2. List every existing violation:
   - `as.formula(paste(...))` or any other string-built formula
   - Generic model names (`m`, `m1`, `m2`, `mod`, `fit`, `result`, `res`, `out`, `output`, `bjs`, `m_fs`, `m_iv`)
   - Loops constructing specifications
   - Missing `summary(model)` / `print(model)` after a fit
   - Implicit cluster (no `cluster =` arg on panel data; no `vcov = ` in pyfixest; no `vce(cluster ...)` in Stata)
   - String-interpolated `vcov` / `cluster` args
3. Refactor each before adding new code. The new code must not perpetuate existing violations. If the user asked for a small change, the refactor is part of the small change — do not scope the skill to "just the new lines."

## When NOT to use

- Pure data wrangling (use `wrangle`).
- Output table formatting / pulling fitted estimates into LaTeX (`stargazer`, `modelsummary`, `fixest::etable`) — that's a separate concern, lives in `04-table_*.R` or `05-table_*.R`.
- Summary-stat tables for descriptives (use `wrangle` or a small dedicated script).

## Core principles

1. **Human-readable first.** One model per named object. The script reads top to bottom; a coauthor can match each table column to the spec that produced it.
2. **Pre-verify → execute → post-verify, every time.** Before fitting: sample N, key variable distributions, identification preconditions. Fit. After: full coefficient table, sign/magnitude against priors, effective N after FE absorption. **Never halt** with `stopifnot()` or `assert`: print the actual value next to the expected one (e.g., `cat("first-stage F:", fs_f, "(expect >= 10)\n")`) so the script runs end-to-end and Claude reads the log to spot mismatches.

## Readability rules

- **No formulae built from strings.** Always write the formula as a literal R/Python expression. The realistic trap is having a `CONTROL_COLS <- c("is_bank", "fee500_dum")` constant somewhere and being tempted to interpolate it — if a constant exists *only* to be pasted into a formula, delete it; it exists to enable the violation.

  ```r
  # WRONG (string-built, opaque to readers; hides the spec from search/grep)
  CONTROL_COLS <- c("is_bank", "fee500_dum")
  fmla <- as.formula(paste("y ~", paste(CONTROL_COLS, collapse = " + "),
                           "| corridor + qdate"))
  m <- feols(fmla, data = d, cluster = ~source_code)

  # RIGHT (literal, self-documenting; greppable)
  m_baseline_corridor_qdate <- feols(
    y ~ is_bank + fee500_dum | corridor + qdate,
    data    = d,
    cluster = ~source_code
  )

  # RIGHT for many specs that share most of the formula — update() preserves
  # literal-ness because the modification is visible:
  m_base    <- feols(y ~ is_bank + fee500_dum | corridor + qdate,
                     data = d, cluster = ~source_code)
  m_firm_fe <- update(m_base, . ~ . | firm + qdate)
  ```

  Same rule applies to `did_imputation`'s `first_stage = ` argument and any other formula-taking interface — write the literal formula, never paste.
- **No looping over specifications.** Don't iterate over a config to build a list of models. Each spec gets its own named line.
- **No nested model calls.** `summary(feols(...))` is fine for a one-off check; for any stored model, assign first: `m1 <- feols(...); summary(m1)`.
- **No magic strings in `vcov` / `cluster` args.** Use literal column names, not `paste0(...)` or `get()`.
- **One model per assignment, name documents the spec.** Not `m1`, `m2`, `m3` — use `m_baseline`, `m_firm_fe`, `m_iv_distance`, etc.

### Naming smells (never use these as model names)

`m`, `m1`, `m2`, `m3`, `mod`, `model`, `fit`, `result`, `res`, `output`, `out`, `bjs`, `m_fs`, `m_iv`, `m_ols`. They tell a reader nothing about what was estimated. A good name compresses *what the model is* into 3–5 underscore-separated tokens:

```
m_<estimator>_<fe-shorthand>_<variant>
```

Examples: `m_baseline_corridor_qdate`, `bjs_firm_qdate_anticipated`, `m_iv_distance_first_stage`, `m_event_twoway_no_anticipation`. If your name is shorter than three tokens, you are probably hiding a spec choice — add the FE and the variant.

Before saving the file, re-read every model name. If any are on the smells list, rename before continuing.

## Pre / execute / post for common estimators

**Hard rule before the examples below:** every fitted model must be followed by `summary(model)` — or `print(model)` / the package equivalent (`didimputation::did_imputation` returns a tibble — `print()` it; `pyfixest` models use `.summary()`; Stata: `estimates table` after `estimates store`). Custom `cat()` lines printing individual stats (R², N, one coefficient) do NOT substitute. The full coefficient table belongs in the run log so the user can read signs, magnitudes, SEs, and stars without re-running.

### OLS

```r
# Pre: sample size, DV distribution, key regressor, NA counts on RHS
cat("panel N:", nrow(panel),
    " NAs in log_assets:", sum(is.na(panel$log_assets)),
    " NAs in post_treat:", sum(is.na(panel$post_treat)),
    " NAs in leverage:",   sum(is.na(panel$leverage)), "\n")
summary(panel$log_assets)
table(panel$post_treat, useNA = "always")

# Execute
m_baseline <- feols(
  log_assets ~ post_treat + leverage,
  data    = panel,
  cluster = ~sic_code
)

# Post: full table + effective N + sign/magnitude vs prior
summary(m_baseline)
cat("model nobs:", m_baseline$nobs,
    "(panel N", nrow(panel), "— diff = rows dropped on RHS NAs)\n")
# Sign expectation: post_treat coef expected positive — flag if negative.
```

### Panel fixed effects

```r
# Pre: panel structure + singletons
cat("Distinct firms:",  n_distinct(panel$firm_id),
    " distinct years:", n_distinct(panel$year),
    " panel N:",        nrow(panel), "\n")
n_singletons <- panel |> dplyr::count(firm_id) |> dplyr::filter(n == 1) |> nrow()
cat("Singleton firms (will be absorbed by firm FE):", n_singletons, "\n")

# Execute — FE explicit in formula, cluster matches the smallest FE dim
m_firm_year_fe <- feols(
  log_assets ~ post_treat + leverage | firm_id + year,
  data    = panel,
  cluster = ~firm_id
)

# Post
summary(m_firm_year_fe)
cat("Within R²:", round(fitstat(m_firm_year_fe, "wr2")$wr2, 4), "\n")
cat("Effective N after FE absorption:", m_firm_year_fe$nobs, "\n")
```

### IV / 2SLS

```r
# Pre: instrument relevance (first-stage F) + exclusion logic IN A COMMENT
# Exclusion: distance affects log_assets only through treatment intensity, conditional on FE.
# Relevance: first-stage F on distance must be >= 10 (rule of thumb).
m_first_stage <- feols(treatment ~ distance + leverage | sic_code,
                       data = panel, cluster = ~sic_code)
fs_f <- fitstat(m_first_stage, "ivf1")$ivf1
cat("First-stage F on distance:", round(fs_f, 2),
    "(expect >= 10; if 10–20, also report Anderson–Rubin CI below)\n")

# Execute
m_iv <- feols(
  log_assets ~ leverage | sic_code | treatment ~ distance,
  data    = panel,
  cluster = ~sic_code
)

# Post: full first + second stage; if F is borderline (10–20), report weak-IV-robust CI
summary(m_iv, stage = 1:2)
# fixest::iv_AR(m_iv)   # Anderson–Rubin if F < ~20
```

### DiD / event study

```r
# Pre: treatment/control composition over time
treat_n   <- panel |> dplyr::filter(treated == 1) |> dplyr::count(year)
control_n <- panel |> dplyr::filter(treated == 0) |> dplyr::count(year)
print(treat_n); print(control_n)
# Save a parallel-trends plot to _outputs/figures/pretrends.pdf before estimating.

# Execute: explicit event-time indicators, baseline period = -1
m_event <- feols(
  log_assets ~ i(event_time, ref = -1) + leverage | firm_id + year,
  data    = panel,
  cluster = ~firm_id
)

# Post: pre-trend coefs near zero, dynamic coefs in expected direction
summary(m_event)
iplot(m_event)   # save to _outputs/figures/event_study.pdf
```

## Language-specific guardrails

### R (fixest is the workhorse; lfe and plm acceptable)

- **`cluster = ~var` always.** Never omit; default iid SEs are almost never right for panel/grouped data.
- **Multiple FE: `feols(y ~ x | fe1 + fe2, data)`** — explicit pipe syntax, not `+ factor(fe1) + factor(fe2)`.
- **Weights: `weights = ~weight_var`** — explicit; print weighted N afterwards.
- **Save fitted models** to `_outputs/intermediate/` with `saveRDS()`, named after the spec. *Exception:* figure-only scripts (`03-fig_*.R`) whose model objects are consumed inline to draw a single plot and never reused — do not save these; note in a one-line comment that the model is figure-local.
- **For tables in `04-table_*.R`**: `modelsummary` or `fixest::etable` — but that's the *next* script, not this one.

### Python (pyfixest)

- Mirror discipline: `feols("y ~ x | fe1 + fe2", data=df, vcov={"CRV1": "cluster_var"})`.
- Save fitted models with `pickle` to `_outputs/intermediate/`.

### Stata

- `reghdfe` for FE; `vce(cluster X)` always explicit.
- `ivreghdfe` for IV + FE; report first-stage F via `weakivtest` or equivalent.
- `estimates store` for downstream table building.

## Warnings worth investigating (do not silence)

Estimation packages emit warnings that are real diagnostic signals about identification, conditioning, or specification. Note them in the user-facing summary AND attempt a diagnosis — do not move on after a one-line acknowledgement.

| Warning (R / Python) | Likely cause | First diagnostic step |
|---|---|---|
| `The VCOV matrix is not positive semi-definite and was 'fixed'` (`didimputation`, `fixest`) | Ill-conditioning at the cluster × FE interaction; collinear controls; singleton-treated cells | Tabulate treated cells per cluster; check rank of the control matrix within each FE bin; consider a coarser cluster |
| `Convergence issue` / `Algorithm did not converge` (`feols`, `glm`) | Sparse FE structure; perfect prediction; collinear instruments | Drop singletons explicitly (`fixest::feols(..., fixef.rm = "both")`); inspect the FE crossing |
| `First-stage F < 10` (any IV) | Weak instrument | Report Anderson–Rubin CI; consider weak-IV-robust inference (`fixest::iv_AR`); reconsider the instrument |
| `Singletons absorbed: N` (`fixest`) | Within-FE clusters with one observation | Confirm intent; if N is large relative to sample, the FE is too granular |
| `NaN standard errors` | Negative diagonal in the SE matrix; degenerate cluster | Switch cluster level; check for treated-cell singletons |
| `dropped because of collinearity` (`fixest`, `lfe`) | Linear dependence among regressors or FE | Inspect which variable was dropped; if it's a control of interest, the spec is wrong |

If a warning fires and you cannot diagnose it in one pass, surface it to the user with the diagnostic step you tried — do not let it stay in the log unaddressed.

## Script skeleton (R, for `1-replication-pack/code/`)

```r
# 04-estimate_main_specs.R
# Main regression specifications for the firm-year panel.

library(arrow)
library(dplyr)
library(fixest)
library(here)

panel <- read_parquet(here("_outputs/intermediate/panel.parquet"))

# --- Pre-check: inputs ------------------------------------------------------
cat("panel N:", nrow(panel),
    " NAs in log_assets:", sum(is.na(panel$log_assets)),
    " NAs in post_treat:", sum(is.na(panel$post_treat)),
    " NAs in leverage:",   sum(is.na(panel$leverage)), "\n")
summary(panel$log_assets)
table(panel$post_treat, useNA = "always")

# --- Specifications ---------------------------------------------------------
m_baseline <- feols(log_assets ~ post_treat + leverage,
                    data = panel, cluster = ~sic_code)
m_firm_fe  <- feols(log_assets ~ post_treat + leverage | firm_id,
                    data = panel, cluster = ~firm_id)
m_twoway   <- feols(log_assets ~ post_treat + leverage | firm_id + year,
                    data = panel, cluster = ~firm_id)

# --- Effective N per spec ---------------------------------------------------
cat("baseline N:", m_baseline$nobs, "\n",
    " firm-fe N:", m_firm_fe$nobs,  "(diff = singletons absorbed)\n",
    " two-way N:", m_twoway$nobs,   "(diff = + year-singletons absorbed)\n")

# --- Print full results (per ~/.claude/CLAUDE.md: always show full table) ---
summary(m_baseline)
summary(m_firm_fe)
summary(m_twoway)

# --- Save fitted models ----------------------------------------------------
saveRDS(m_baseline, here("_outputs/intermediate/m_baseline.rds"))
saveRDS(m_firm_fe,  here("_outputs/intermediate/m_firm_fe.rds"))
saveRDS(m_twoway,   here("_outputs/intermediate/m_twoway.rds"))
cat("Saved 3 models to _outputs/intermediate/\n")
```

## When refactoring an existing estimation script

1. Read end to end. Identify each fitted model and its purpose.
2. Look for constructed formulae or specification loops — unroll into named, literal lines.
3. Add the pre-check (sample N, key variable summary, identification preconditions) and post-check (full coef table, sign/magnitude sanity, effective N) for each model.
4. Run the refactored script and compare estimates to the original — they must match to within rounding unless the underlying data changed.

## Output expectation

Write or edit estimation code that follows the rules above. Apply them; do not narrate them. If a refactor changed something material (FE structure, cluster level), call it out in one short sentence — e.g. "the previous spec didn't cluster — added `cluster = ~firm_id`; SEs roughly doubled."
