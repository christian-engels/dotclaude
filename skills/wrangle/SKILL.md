---
name: wrangle
description: Write or refactor data-wrangling code (joins, filters, pivots, aggregations, type changes) so it is human-readable and self-verifying. Use when writing or editing scripts under `1-replication-pack/code/` or `4-things-we-tried/*/code/`, or when refactoring existing wrangling scripts that are hard to read. Enforces explicit programming (no constructed column names, no loops where vectorisation works, no deep nesting), per-operation before/after verification, and language-specific guardrails (R: no float ==, explicit na.rm, TRUE/FALSE; Python: explicit pl.col / .loc; Stata: explicit merge cardinality).
---

# Wrangle

Write data-wrangling code that a coauthor — or you in six months — can read line by line, and that prints enough at each step to verify itself.

## When to use

- Writing or editing scripts under `1-replication-pack/code/` (production pipeline) or `4-things-we-tried/[trial]/code/` (exploration).
- Refactoring an existing wrangling script that is hard to read.
- The user describes a data operation: "merge this into that", "filter to 2020 onwards", "pivot to wide".

## When NOT to use

- One-off data inspection via MCP (use MCP-first per `~/.claude/CLAUDE.md`; no script needed).
- Pure estimation code (regressions, IVs, panel models) — that's the future `estimate` skill.
- Pure plotting code with no data operations.

## Core principles

1. **Human-readable first.** Explicit beats clever. A junior coauthor should read the script top to bottom and follow what happened.
2. **Pre-verify → execute → post-verify, every time.** Every data operation — joins, filters, derived columns, type coercions, pivots, aggregations — gets a pre-check (what do the inputs look like?), the operation itself, then a post-check (did the output match expectations?). For multi-step constructions, name the intermediates and check each. **Never halt** with `stopifnot()` or `assert`: print the actual value next to the expected one (e.g., `cat("dups:", n_dup, "(expect 0)\n")`) so the script runs end-to-end and Claude reads the log to spot mismatches.
3. **One operation per pipe step.** When a pipe gets long or branches, break to a named intermediate object.

## Readability rules

**Do not** do any of these. They are the standard reasons scripts become unreadable:

- **No constructed column names.** `paste0("var_", i)` to build a column name → write the literal column names. If there are too many to type, the schema design is wrong.
- **No loops where vectorisation works.** `for (i in seq_len(n)) df$x[i] <- ...` → use `mutate()`, `case_when()`, or vectorised arithmetic. Loops are fine for genuinely iterative work (bootstrap, optimisation) — not for column construction.
- **No deeply nested functions.** Three or more deep (`f(g(h(j(x))))`) → extract intermediate names with `<-` (R) or `=` (Python).
- **No `select(-x, -y, -z)` on a wide table.** Negation lists what you don't want; list what you do want instead.
- **No `mutate(across(...))` with complex predicates.** Spell out the columns. `across()` is fine for `everything()` or small named lists.
- **No string-built code.** `eval(parse(text = paste0(...)))` is always a red flag. So is constructing file paths by `paste0("data/", year, ".csv")` when `here()` or `file.path()` works.

**Do** do these:

- One operation per line in a pipe, with an inline comment explaining *why* (not what).
- Name intermediate objects when a pipe runs longer than ~5 steps or branches.
- One verb per step: `select` then `filter` then `mutate` then `arrange`, in that order when possible.
- Prefer `join_by(a == b)` over `by = c("a" = "b")` — explicit equality.

## Per-operation verification

After every data operation, print enough to confirm it did what you expected.

### Joins (the highest-bug-rate operation)

```r
# Before
n_dup_right <- sum(duplicated(firms$firm_id))    # unique join key on at least one side
cat("left rows:",   nrow(filings),
    " right rows:", nrow(firms),
    " right key dups:", n_dup_right, "(expect 0)\n",
    " key NAs left:",  sum(is.na(filings$firm_id)),
    " right:",         sum(is.na(firms$firm_id)), "\n")

# Operation
panel <- filings |> left_join(firms, join_by(firm_id))

# After
cat("joined rows:", nrow(panel), "(expect", nrow(filings), "— left join must not multiply)\n",
    " rows missing right-side data:", sum(is.na(panel$sic_code)), "\n")
```

- Always specify join type explicitly: `left_join`, `inner_join`, `full_join`. Never default.
- For many-to-many joins, set `relationship = "many-to-many"` explicitly — and stop to confirm intent.
- After every join: row count vs. expected, NA count on joined columns, distinct keys.

### Filters

```r
n_before <- nrow(df)
df <- df |> filter(year >= 2010, year <= 2024)
cat("Filter year in [2010, 2024]: kept", nrow(df), "of", n_before, "rows\n")
```

- Always log `n_before`, `n_after`, and the reason in a comment.
- If the drop exceeds 10%, note it explicitly.

### New columns and derived variables

This is where most silent bugs hide. Apply pre / execute / post, and for anything built in steps, name the intermediates.

**Simple construction (single expression):**

```r
# Pre: are the inputs sane for this operation?
summary(df$assets)
sum(df$assets <= 0 | is.na(df$assets))           # log() fails on 0, negatives, NA

# Execute
df <- df |> mutate(log_assets = log(assets))

# Post: did the output match expectation?
sum(is.na(df$log_assets))                        # silent NAs from log(non-positive)
sum(!is.finite(df$log_assets), na.rm = TRUE)     # -Inf from log(0)
summary(df$log_assets)                           # eyeball the distribution
```

**Multi-step construction:** name the intermediates so you can inspect *during*, not just before and after.

```r
# Don't: leverage = (total_debt + short_term_debt - cash) / total_assets   (one opaque expression)
# Do:
df <- df |> mutate(
  gross_debt = total_debt + short_term_debt,     # intermediate
  net_debt   = gross_debt - cash,                # intermediate
  leverage   = net_debt / total_assets           # final
)
summary(df$gross_debt)
summary(df$net_debt)
summary(df$leverage)
```

**`case_when`:** verify each branch fires:

```r
df <- df |> mutate(
  firm_size = case_when(
    employees < 100   ~ "small",
    employees < 1000  ~ "medium",
    employees >= 1000 ~ "large",
    .default = NA_character_                     # explicit default — never silent
  )
)
table(df$firm_size, useNA = "always")            # branch counts + NA mix
```

**Common construction-time failure modes:**

| Operation | Pre-check | Post-check |
|---|---|---|
| `log(x)`, `log1p(x)` | any `x <= 0` or NA? | new NAs, `-Inf` |
| `x / y` | any `y == 0` or NA? | `Inf`, `NaN` |
| `as.numeric(chr)` | what does the chr column look like? | new NAs from silent coercion failure |
| date arithmetic (`a - b`) | both date types, no NAs, ordering | negative durations |
| `coalesce(a, b)` | NA counts in a and b | source contribution |
| `case_when` | distribution of the keying var | branch counts + NA mix |
| string ops (`substr`, `str_extract`) | string-length distribution | silent truncation, new NAs |
| indicator (`as.integer(cond)`) | NAs in the condition (become NA, not 0) | 0/1/NA mix |

### Pivots

```r
cat("long:", dim(df), "\n")
df_wide <- df |> pivot_wider(names_from = year, values_from = revenue)
cat("wide:", dim(df_wide), "\n")
# Expected wide rows = long rows / n_distinct(year). Verify.
```

- Print dimensions before and after. Compute the expected dimension from first principles.

### Type coercions

```r
n_na_before <- sum(is.na(df$amount))
df <- df |> mutate(amount = as.numeric(amount))
n_na_after <- sum(is.na(df$amount))
cat("NA in df$amount before:", n_na_before,
    " after:", n_na_after,
    " (expect equal — new NAs are silent coercion failures)\n")
```

Any new NAs after a type coercion are bugs unless explicitly expected.

### Aggregations

```r
n_groups <- df |> distinct(firm, year) |> nrow()
agg <- df |> summarise(.by = c(firm, year), revenue = sum(revenue, na.rm = TRUE))
cat("aggregated rows:", nrow(agg), "(expect", n_groups, "— one row per firm-year)\n")
```

- Verify group count matches a pre-computed expectation.
- Always specify `.by =` (or `group_by(...) |> ... |> ungroup()`) explicitly.
- Always specify `na.rm = TRUE/FALSE` — never the default.

## Language-specific guardrails

### R (apply in every R script)

- **No float equality on doubles.** Never `df$x == 0.1`. Use `dplyr::near(df$x, 0.1)` or `abs(df$x - 0.1) < 1e-9`.
- **Always set `na.rm = TRUE/FALSE` explicitly** for `mean`, `sd`, `sum`, `median`, etc. Defaults vary and bite silently.
- **`TRUE` / `FALSE`, never `T` / `F`.** `T` and `F` are variables — they can be overwritten.
- **Pre-allocate vectors** before genuine loops (`numeric(n)`, `vector("list", n)`). Never grow with `c()`.
- **Native pipe `|>`, not magrittr `%>%`** unless the project predates R 4.1.

### Python (polars / pandas)

- **Polars**: `pl.col("x")` always; never `df.x` (ambiguous with attributes).
- **Pandas**: avoid chained assignment (`df[x][y] = z` triggers `SettingWithCopyWarning` and may silently fail). Use `df.loc[x, y] = z`.
- **Joins**: pass `validate="1:1"` / `"1:m"` / `"m:1"` — the equivalent of Stata merge cardinality.
- **Type coercion**: use `pd.to_numeric(..., errors="coerce")` deliberately; check `isna().sum()` before and after.

### Stata

- **Merges**: always explicit cardinality (`merge 1:1`, `merge m:1`, `merge 1:m`). Never `merge` alone.
- **After every merge**: `tab _merge`; assert the expected mix; drop `_merge` before saving.
- **`gen` vs `egen`**: prefer `gen` with explicit formulae; reserve `egen` for genuine aggregations.

## Script skeleton (R, for `1-replication-pack/code/`)

```r
# 02-clean_panel.R
# Build the firm-year panel from raw_firms.parquet and raw_filings.parquet.

library(arrow)
library(dplyr)
library(here)

set.seed(20260517)   # YYYYMMDD

# --- Inputs --------------------------------------------------------------------
firms   <- read_parquet(here("data/raw_firms.parquet"))
filings <- read_parquet(here("data/raw_filings.parquet"))
cat("Inputs:\n",
    "  firms:  ", nrow(firms),   "rows,", ncol(firms),   "cols\n",
    "  filings:", nrow(filings), "rows,", ncol(filings), "cols\n")

# --- Step 1: filter to sample window -------------------------------------------
n_before <- nrow(filings)
filings <- filings |> filter(year >= 2010, year <= 2024)
cat("Filter year in [2010, 2024]: kept", nrow(filings), "of", n_before, "rows\n")

# --- Step 2: join firm metadata onto filings -----------------------------------
cat("firms$firm_id duplicates:", sum(duplicated(firms$firm_id)), "(expect 0)\n")
panel <- filings |> left_join(firms, join_by(firm_id))
cat("panel rows after join:", nrow(panel), "(expect", nrow(filings),
    "— left join must not multiply);",
    " rows missing firm metadata:", sum(is.na(panel$sic_code)), "\n")

# --- Step 3: derive analytic vars ----------------------------------------------
# Pre-check: inputs sane for what we're about to do?
cat("assets <= 0:", sum(panel$assets <= 0, na.rm = TRUE),
    "(expect 0 — log requires positive);",
    " treat_year NA:", sum(is.na(panel$treat_year)),
    "(NA propagates to post_treat)\n")

panel <- panel |> mutate(
  log_assets = log(assets),                    # natural log
  leverage   = total_debt / assets,            # book leverage
  post_treat = as.integer(year >= treat_year)  # NA propagates if treat_year NA
)

# Post-check: outputs match expectation?
cat("log_assets non-finite (excl. NA):",
    sum(!is.finite(panel$log_assets) & !is.na(panel$log_assets)),
    "(expect 0)\n")
summary(panel$leverage)                                     # expect mostly [0, 1]
cat("post_treat: 0 =", sum(panel$post_treat == 0, na.rm = TRUE),
    " 1 =",  sum(panel$post_treat == 1, na.rm = TRUE),
    " NA =", sum(is.na(panel$post_treat)), "\n")

# --- Output --------------------------------------------------------------------
out_path <- here("_outputs/intermediate/panel.parquet")
write_parquet(panel, out_path)
cat("Wrote", out_path, "—", nrow(panel), "rows,", ncol(panel), "cols\n")
```

Shape: input audit → one operation per step with verification → save and print path.

## When refactoring an existing script

1. Read the script end to end before changing anything.
2. Identify the operations (joins, filters, pivots, aggregations).
3. For each operation: lift out of any nesting, add before/after verification, name intermediate objects if the pipe gets long.
4. Replace constructed names with literals; replace loops with vectorised forms.
5. Run the refactored script and compare the saved output to the original byte-for-byte (or by hash) — refactoring must not change the numbers.

## Output expectation

Write or edit code that follows the rules above. Do not narrate the rules in the response — apply them. If you refactored an existing script, mention in one short sentence what bug-class the rules caught (e.g., "the left_join was many-to-many; added a duplicate-key check and switched to inner_join after confirming intent").
