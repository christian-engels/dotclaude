---
name: bibcheck
description: Many-agent bibliography audit. Verify each citation in a .bib file by spawning narrow-focus agents that confirm DOI/URL and cross-check that all fields belong to the same paper. Catches mixed-up entries (one paper's title with another's authors), wrong years, journal misattributions, and unverifiable references. Use when reviewing a manuscript's bibliography for accuracy before submission, after literature review, or when inheriting a .bib from a coauthor.
allowed-tools: Bash(claude*), Bash(ls*), Bash(cat*), Bash(wc*), Bash(grep*), Bash(mkdir*), Bash(cp*), Read, Write, Edit, WebSearch, WebFetch, Agent
argument-hint: '[--by-citation|--by-field] <path-to-bib-or-tex> [--max-parallel N]'
---

# Bibcheck: Many-Agent Bibliography Audit

You are running `/bibcheck` — a verification routine that audits a bibliography by spawning many narrow-focus agents, one per citation (or one per field), so each agent operates on a small task with low risk of attention decay over a long context.

## Why narrow agents

A single agent asked to audit 80 citations in one pass tends to drift: early entries get careful treatment; later entries get pattern-matched. Splitting the work — one agent per entry, or one specialist per field across all entries — keeps each agent focused on something small and verifiable. The bottleneck shifts from agent attention to orchestration, which is what cheap parallel agents are for.

See `methodology.md` for the full rationale.

## Step 0: Read your full methodology

1. Read `methodology.md` in this skill directory — it explains the gradient-decay rationale and the audit standard for both modes.
2. Confirm you understand which mode the user invoked.

## Step 1: Parse arguments

Modes:

| Argument | Mode | What it does |
|----------|------|--------------|
| `--by-citation <file>` (default if omitted) | **Per-citation** | One Agent subagent per bib entry. Each fully audits its one entry. |
| `--by-field <file>` | **Per-field** | One CLI subprocess per field (title, year, journal, authors, volume/issue, pages, DOI). Each specialist reads the whole bibliography but checks only its field. |
| `--max-parallel N` | Optional | Cap concurrent subagents/subprocesses. Default 8. |

Input file:
- `.bib` — use directly
- `.tex` — extract `\bibitem{}` blocks or read the linked `.bib` from `\bibliography{}`. If both a `.tex` and a `.bib` are in the same folder, prefer the `.bib`.

If the user invoked `/bibcheck` with no arguments, ask:
- Which mode? (per-citation is the default; per-field is for adversarial cross-checks)
- Path to the .bib or .tex?

Do not guess.

## Step 2: Set up the run directory

Create a working folder next to the input file:

```
<bib_dir>/bibcheck_<timestamp>/
  ├── input.bib              # copy of source
  ├── entries/               # split entries (one .bib per entry)
  ├── reports/               # per-agent JSON/markdown outputs
  ├── bibcheck_report.md     # final consolidated report
  └── corrected.bib          # drop-in replacement
```

The timestamped folder means re-runs do not clobber prior audits.

## Step 3a: Per-citation mode

1. **Split the .bib into per-entry files.** A robust splitter: read the .bib, walk for `@type{key,` openers, balance braces to find each entry's close, write to `entries/<key>.bib`.

2. **Launch agents in waves of `--max-parallel`.** For each entry, dispatch one Agent subagent (subagent_type: general-purpose) with this brief:

   ```
   You are auditing one bibliography entry. The entry is:

   <paste the .bib block>

   Your job:
   1. Identify the cited paper. Use WebSearch (and WebFetch if needed) to find it.
   2. Locate a canonical anchor: DOI, journal landing page URL, or author working-paper URL.
   3. Cross-check every field in the .bib block against the canonical source:
      - title, authors, year, journal/booktitle, volume, number, pages, publisher, DOI
   4. Specifically test for "field mixing" — e.g., the title belongs to one paper but the authors or year belong to another. This is the most common silent error in inherited .bib files.
   5. Output JSON to <reports/<key>.json> with:
      - status: "clean" | "corrected" | "unverifiable"
      - one_sentence: plain-language description of the paper (one sentence)
      - canonical_url: DOI or URL
      - issues: list of {field, original, corrected, reason}
      - corrected_bib: the corrected entry (or the original if status=clean)

   You do NOT modify the input file. You only write the report and the corrected entry.
   ```

3. **Final reviewer pass.** When all entries are done, dispatch a single reviewer agent that:
   - Reads every `reports/*.json`.
   - Spot-checks any entry marked "unverifiable" (does a quick second WebSearch).
   - Adjudicates conflicts where a corrected field looks suspicious.
   - Writes `bibcheck_report.md` with a summary table (Clean / Corrected / Unverifiable counts) and per-entry detail.
   - Concatenates the corrected_bib fields into `corrected.bib`.

## Step 3b: Per-field mode

The point of this mode is **isolation**: each specialist agent should not see what the others are concluding. We achieve that by launching each specialist as a separate `claude -p` subprocess. Each subprocess is a fresh CLI session.

For each field in the list `[title, year, journal, authors, volume_issue, pages, doi]`:

1. Build a prompt for the specialist that contains:
   - The full input.bib content
   - The field name
   - Instructions: "For each entry in this .bib, check ONLY the {field}. Compare against the canonical paper found via WebSearch. Output JSON to stdout: a list of {key, status, original, corrected, reason}."

2. Launch the specialist via Bash:
   ```bash
   claude --dangerously-skip-permissions -p "<the specialist prompt>" > reports/field_<field>.json 2>reports/field_<field>.log
   ```

3. Run subprocesses in parallel up to `--max-parallel`. Wait for all to complete.

4. **Final reviewer pass.** A consolidator agent reads all `field_*.json`, joins by entry key, and produces:
   - `bibcheck_report.md` — disagreements across specialists are flagged (e.g., title-specialist says X, year-specialist disagrees about which paper is being cited)
   - `corrected.bib` — applies a field-level fix only if the relevant specialist flagged it AND the cross-field consensus supports the fix

## Step 4: Present the result to the user

Show the user:

```
bibcheck complete.

  Clean:        N entries
  Corrected:    M entries (see bibcheck_report.md)
  Unverifiable: K entries (need human eyes)

Drop-in replacement: corrected.bib
Full audit:          bibcheck_report.md
```

Do not auto-overwrite the user's source `.bib`. They review, then move `corrected.bib` into place themselves.

## Defaults and tone

- Default mode is **per-citation** unless the user asks for `--by-field`.
- Default `--max-parallel` is **8**. Bump on request.
- This is a verification skill — never *write* citations from scratch. Only audit and correct.
- If a citation is genuinely unverifiable (paywalled, dead URL, ambiguous match), say so. Do not invent a DOI.

## When to suggest the other mode

After per-citation completes, if 3+ entries came back as unverifiable, suggest the user re-run with `--by-field` for those specific entries — a field-specialist sometimes catches what a citation-generalist missed (e.g., a wrong year hiding behind a correct title).
