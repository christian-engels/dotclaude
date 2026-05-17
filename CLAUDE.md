# Empirical Work in Finance and Economics

The user is an academic researcher focused on empirical work in finance and economics. Your primary aim is to support exploratory data analysis and research for academic papers.

The aspiration is to publish in the top three finance journals and the top five economics journals, though publication in other reputable outlets is also valued.

## Folder Structure

Folders are numbered to make the workflow and priority clear at a glance. The separation between `things-we-tried/`, `replication-pack/` and `paper/` is the load-bearing piece.

### 0-admin/

Project management: AI feedback reports, conference tracker, submission materials. Not part of the research itself.

### 1-replication-pack/

Self-contained reproducible analysis. Should cleanly reproduce all paper results from raw data. The execution order should be immediately clear to anyone reading the filenames.

- `code/` — the numbered script pipeline: `01-clean_data.py`, `02-estimate_model.R`, `03-figure_1.py`, etc. Each script produces one output. No flags, arg parsers, or config systems. No cross-script imports — each script is self-contained.
- `data/` — raw and (where reproducible) intermediate data.
- `_outputs/` — **everything scripts produce lands here, never in `2-paper/` directly**:
  - `_outputs/intermediate/` — script-to-script handoffs (`.parquet`, `.rds`).
  - `_outputs/figures/` — figures written by `03-figure_*.py` etc.
  - `_outputs/tables/` — `.tex` table files written by `04-table_*.R` etc.
- Use `.env` for paths, API keys, secrets; commit a `.env.example` showing required variables without values.

### 2-paper/

LaTeX manuscript: `sections/`, `figures/`, `tables/`, `references.bib`. Receives only the **blessed subset** of `1-replication-pack/_outputs/`. Promotion is manual via Claude Code: figures are copied verbatim; tables are copied and then formatted for the paper (captions, panel labels, column specs, footnotes, sizing). Numbers are never touched by hand.

### 3-articles/

Reference literature PDFs, plus split versions for LLM reading.

### 4-things-we-tried/

Exploratory work, coauthor communications, slide decks, and reference repos. Each trial is its own folder:

```
4-things-we-tried/
├── [trial-name]/
│   ├── README.md     # goal, status, findings
│   ├── code/         # use _v1, _v2 suffixes to compare design alternatives
│   └── output/       # trial outputs — never read by 2-paper/
└── ARCHIVE/
    ├── completed_[trial]/   # graduated to 1-replication-pack/; note which scripts carry the logic
    └── abandoned_[trial]/   # short note on why
```

Archive rather than delete: `git log` doesn't surface *why* a trial was abandoned.

### Workflow

**One-way flow**: Scripts in `1-replication-pack/code/` write to `1-replication-pack/_outputs/`. A separate, explicit promotion step copies the blessed subset to `2-paper/`. No other path is permitted.

**Single source of truth — numbers vs. presentation**: The script owns the numbers; the paper owns the presentation.
- *Numbers* (estimates, SEs, p-values, stars, N) — script-side only. If something looks wrong, fix the script and re-run.
- *Formatting* (captions, panel labels, column specs, footnotes, sizing) — paper-side. Edit freely in `2-paper/tables/`.

**Iteration**: Re-running a script overwrites `_outputs/`, not `2-paper/`. The paper keeps using the old artifact until you re-promote — so you can iterate without churning the manuscript mid-draft. When re-promoting a table after a number change, diff `_outputs/tables/XX.tex` against the prior version and carry only the number changes into `2-paper/tables/XX.tex`; preserve the paper-side formatting.

**Trial to production**: New analyses start in `4-things-we-tried/[trial-name]/`. Once validated, the logic is refactored into numbered scripts in `1-replication-pack/code/`; the trial folder moves to `4-things-we-tried/ARCHIVE/completed_[trial]/` with a note pointing to the new scripts. Only then do its outputs flow into `2-paper/`.

**Writing prose**: Any prose written into or edited within `2-paper/sections/` — or returned as a draft paragraph, abstract, section, caption, or response-to-referees for the manuscript — goes through the `ai-text-writing` skill. Conversational answers *about* the paper (explanations in chat, summaries for the user to read) do not.

**Slide decks**: When asked to construct a slide deck, invoke the `beautiful_deck` skill.

**Wrangling data**: When writing or editing data-wrangling code (joins, filters, mutates, pivots, aggregations, type coercions) under `1-replication-pack/code/` or `4-things-we-tried/*/code/`, invoke the `wrangle` skill.

**Estimating models**: When writing or editing estimation code (regressions, IVs, panel models, DiD/event studies) under the same paths, invoke the `estimate` skill.

## Using Python, R and Stata

Never use global package installations except for Stata. It is fine to combine R and Python in a single project — `renv` and `uv` coexist happily in one directory.

### R
- Use `rig` to manage R versions and `renv` for per-project environments.
- Core packages: `duckdb`, `dbplyr`, `tidyverse`, `fixest`.

### Python
- Use `uv` for environments and dependencies; one virtual environment per project.
- Core packages: `duckdb`, `polars`, `pyfixest`.

### Stata

Prefer R or Python. Use Stata only when its specialised tooling has no practical equivalent in either. Organise via `.stpr` projects.

### MCP first, scripts second

Before writing any code to disk, use available MCP servers (e.g., filesystem, duckdb-ram) to inspect data: file sizes, directory contents, database schemas, first few rows of a CSV/Parquet, simple summary statistics. Goal: gain enough context to write the correct numbered script the first time, without leaving temporary `.py` or `.ipynb` files behind.

## How Claude Should Work

- **Pre-verify → execute → post-verify, every time.** Before changing state — files, code, data, git history — check the inputs. Execute. Verify the outputs match expectations. Don't trust silent success. For data work, this discipline is encoded in the `wrangle` and `estimate` skills; outside data work it still applies (read before edit, `git status` before commit, dry-run before destructive operation, etc.).
- **No guessing.** If a specification is unclear, ask before proceeding.
- **Always display the full regression or summary table** so the exact specification is visible.
- **View figures** through image capabilities so we can discuss them.
- **Always report where outputs are stored** (full file paths).

## Version Control

- Commit regularly with descriptive messages. Each commit on `main` should encapsulate a complete, coherent piece of work — like an entry in a lab book. Concise first line; detailed body explaining what was done and what was found.
- For exploratory work that spans many small commits, squash-merge into `main` as a single commit with the same format: concise first line, detailed body covering what was tried, what was found, and what decisions were made.
- Never include `Co-Authored-By` lines (or any variation) in commit messages.
- `.gitignore` essentials: `.venv/`, `venv/`, `renv/`, `.env`, caches, large datasets. Always commit `.env.example`.
