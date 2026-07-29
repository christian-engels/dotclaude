# Empirical Work in Finance and Economics

The user is an academic researcher focused on empirical work in finance and economics. Your primary aim is to support exploratory data analysis and research for academic papers.

The aspiration is to publish in the top three finance journals and the top five economics journals, though publication in other reputable outlets is also valued.

## Style

- British English, no Oxford commas.
- Figures and tables follow the conventions and norms of finance and economics journals.

## Project Layout

Research projects follow one of two taxonomies, and layouts differ slightly by repo — each repo's own CLAUDE.md and its actual tree are authoritative. Whatever the folder names, the separation between trials, the replication pack and the paper is the load-bearing piece.

**Numbered layout** (newer projects). Folders are numbered to make the workflow and priority clear at a glance:

- `0-admin/` — project management: AI feedback reports, conference tracker, submission materials. Not part of the research itself.
- `1-replication-pack/` — self-contained reproducible analysis: `code/` (the numbered script pipeline), `data/` (raw and, where reproducible, intermediate data) and `_outputs/` with `intermediate/`, `figures/` and `tables/`. Should cleanly reproduce all paper results from raw data.
- `2-paper/` — LaTeX manuscript: `sections/`, `figures/`, `tables/`, `references.bib`. Receives only the **blessed subset** of `_outputs/`.
- `3-articles/` — reference literature PDFs, plus split versions for LLM reading.
- `4-things-we-tried/` — exploratory work, coauthor communications, slide decks. Each trial is its own folder with a README (goal, status, findings), `code/` and `output/`; `ARCHIVE/completed_[trial]/` and `ARCHIVE/abandoned_[trial]/` hold graduated and dropped trials.

**Simple layout** (older projects): `code/`, `data/raw/`, `data/processed/`, `analysis-outputs/`, `notebooks/`, `articles/` — the same roles under flat names.

### Invariants (any layout)

- **One-way flow**: scripts write to the outputs directory, never into the paper. A separate, explicit promotion step copies the blessed subset to the paper: figures are copied verbatim; tables are copied and then formatted for the paper. Numbers are never touched by hand. No other path is permitted.
- **Single source of truth — numbers vs. presentation**: The script owns the numbers; the paper owns the presentation.
  - *Numbers* (estimates, SEs, p-values, stars, N) — script-side only. If something looks wrong, fix the script and re-run.
  - *Formatting* (captions, panel labels, column specs, footnotes, sizing) — paper-side. Edit freely in the paper's tables.
- **Iteration**: re-running a script overwrites the outputs directory, not the paper. The paper keeps using the old artifact until you re-promote — so you can iterate without churning the manuscript mid-draft. When re-promoting a table after a number change, diff against the prior version and carry only the number changes; preserve the paper-side formatting.
- **Numbered, self-contained scripts**: `01-clean_data.py`, `02-estimate_model.R`, `03-figure_1.py`, etc. Each script produces one output. No flags, arg parsers, or config systems. No cross-script imports — each script is self-contained.
- **Trial to production**: new analyses start as trials outside the replication pack; trial outputs are never read by the paper. Once validated, the logic is refactored into numbered pipeline scripts; the trial folder is archived with a note pointing to the new scripts. Only then do its outputs flow into the paper.
- **Archive rather than delete**: `git log` doesn't surface *why* a trial was abandoned.
- Use `.env` for paths, API keys, secrets; always commit a `.env.example` showing required variables without values.

## Skills

- **Writing prose**: any prose written into or edited within the manuscript source — wherever the paper's LaTeX lives — or returned as a draft paragraph, abstract, section, caption, or response-to-referees for the manuscript — goes through the `ai-text-writing` skill. Conversational answers *about* the paper (explanations in chat, summaries for the user to read) do not.
- **Slide decks**: when asked to construct a slide deck, invoke the `beautiful_deck` skill.
- **Wrangling data**: when writing or editing data-wrangling code (joins, filters, mutates, pivots, aggregations, type coercions) in any analysis script, invoke the `wrangle` skill.
- **Estimating models**: when writing or editing estimation code (regressions, IVs, panel models, DiD/event studies) in any analysis script, invoke the `estimate` skill.

## Using Python, R and Stata

Never use global package installations except for Stata. It is fine to combine R and Python in a single project — `renv` and `uv` coexist happily in one directory.

### R
- Use `rig` to manage R versions and `renv` for per-project environments.
- Core packages: `duckdb`, `dbplyr`, `tidyverse`, `fixest`.

### Python
- Use `uv` for environments and dependencies; one virtual environment per project.
- Core packages: `duckdb`, `polars`, `pyfixest`, `plotnine`.

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
- `.gitignore` essentials: `.venv/`, `venv/`, `renv/`, `.env`, caches, large datasets.
