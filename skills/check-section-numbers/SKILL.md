---
name: check-section-numbers
description: For an academic LaTeX paper, dispatch one sub-agent per \section to check that the prose still matches the tables and figures it references. Each sub-agent reads the section body, reads the referenced tables/figures directly, and makes surgical edits where the prose disagrees with the artefacts (a digit, a star, a direction word). Larger rewrites are flagged, not attempted. Use after regenerating tables or figures, before re-reading the paper. NOT for grammar/style (use a proofread skill) and NOT for cross-paper citation fact-checking (different job).
argument-hint: "[main.tex path]"
allowed-tools: ["Read", "Grep", "Glob", "Task", "Edit", "Bash"]
---

# /check-section-numbers

Orchestrator that checks whether the body text of each `\section` in a LaTeX paper is still consistent with the tables and figures it references. Spawns one sub-agent per section in parallel. Each sub-agent has write access to `main.tex` but is bound to a surgical-edits-only policy.

**Input:** `$ARGUMENTS` — path to the paper's main `.tex` file. If omitted, search for `main.tex` / `paper.tex` in the current working directory.

## Protocol

### Phase 0 — Pre-flight

1. Confirm the .tex file exists and is readable.
2. Identify the paper root (directory containing main.tex) — all relative `\input{}` and `\includegraphics{}` paths resolve from here.
3. Warn the user if the file is dirty in git (uncommitted changes). Surgical edits are safer to review against a clean working tree.

### Phase 1 — Inventory sections

```bash
grep -nE '^\\section\{' <main.tex>
```

Build a list of `(section_title, start_line, end_line)` tuples. `end_line` = line before the next `\section` (or EOF). Skip appendix sections if they sit inside `\appendix`, unless the user passed `--include-appendix`.

### Phase 2 — Resolve ground-truth artefacts per section

For each section, within its line range:

- Extract every `\ref{...}`, `\Cref{...}`, `\autoref{...}`, `\eqref{...}`.
- For each referenced label, grep the repo for its `\label{...}` definition — both in main.tex and in `\input{}`-ed files (`tables/*.tex`, `figures/*.tex`, etc.). Record the file path.
- Also extract any direct `\input{tables/...}` or `\includegraphics{figures/...}` that appear inside the section range — those are artefacts too, even without a `\ref`.
- Resolve figure paths against common extensions (`.pdf`, `.png`, `.jpg`, `.tex` for TikZ).

Each section now has a list of artefact file paths. If a ref can't be resolved, note it in the final report and continue — do not fail the section.

### Phase 3 — Dispatch sub-agents (body first, framing last)

Split the section list into two waves:

- **Wave A (body)** — every section whose title is NOT one of (case-insensitive): "Introduction", "Conclusion", "Conclusions", "Concluding remarks".
- **Wave B (framing)** — the introduction and conclusion.

**Why two waves:** the introduction and conclusion typically restate and synthesise numbers from the body. Running them after the body has been corrected means their prose can be aligned against the now-settled body, and the framing agents can be told which body claims were flagged as needing a rewrite — so they can flag the corresponding framing sentences.

**Wave A** — spawn body agents **in parallel** via `Task` (subagent_type=general-purpose), one Task call per section, all in a single tool-use block. Each receives the standard prompt template below.

**Wave B** — after Wave A returns, spawn intro + conclusion agents in parallel. In addition to the standard prompt, pass each a `## Body flags from Wave A` block listing every flag and every major edit from Wave A (one line each: section, issue). The framing agents use this to recognise when their own prose restates something the body flagged.

Pass each sub-agent:
- The main.tex path (so it can Edit directly)
- The section's line range
- The resolved artefact file paths
- The edit policy (copied in full — do not rely on the sub-agent to remember it)
- (Wave B only) the Wave A flag digest

### Phase 4 — Aggregate

Collect each sub-agent's structured return. Produce one combined report:

```markdown
## Section-Number Check — <main.tex>

| Section | Edits applied | Flagged for review | Unresolved refs |
|---------|---------------|--------------------|-----------------|
| Introduction | 0 | 0 | 0 |
| Baseline results | 3 | 1 | 0 |
| ... | ... | ... | ... |

### Edits applied
- **Baseline results** (L352): "1.63%" → "1.68%" (Table 2 col (3))
- ...

### Flagged (surgical edit not sufficient)
- **Baseline results**: coefficient on `hate_crime` flipped sign in Table 2 col (2); the paragraph at L368–L374 interprets it as positive. Needs manual rewrite of ~3 sentences.
- ...

### Unresolved references
- `fig:placebo-v2` — no \label found.
```

## Sub-agent prompt template

Fill the placeholders and pass this as the sub-agent's prompt:

````text
You are checking one section of a LaTeX paper for numerical consistency with its tables and figures. Your job is narrow and surgical.

**Section:** {section_title}
**File:** {main_tex_path}
**Line range:** {start_line}–{end_line}
**Artefacts referenced in this section:**
{bulleted list of resolved artefact paths, with type: .tex table / figure PDF / TikZ .tex / etc.}

## What to do

1. Read lines {start_line}–{end_line} of {main_tex_path}. This is the prose you are auditing.
2. Read every artefact file in the list above. For figure PDFs/PNGs, read them as images — Claude Code supports this.
3. For every concrete numerical or directional claim in the prose, find the corresponding value in the artefact:
   - Point estimates, standard errors, t-stats, p-values
   - Sample sizes, counts, percentages
   - Significance stars / "significant at the 1% level" phrasing
   - Direction words: "positive", "negative", "increases", "decreases", "larger than", "smaller than"
   - Magnitude descriptors: "roughly", "approximately X%"
   - **Check footnotes with the same rigour as main text.** Stale numbers often hide inside `\footnote{...}`. Do not skim past them.
4. For each claim, classify:
   - **MATCH** — prose agrees with artefact. Do nothing.
   - **SURGICAL** — prose disagrees but a one-token fix is enough: a digit, a star count, a single direction word, a percentage. Apply via Edit.
   - **FLAG** — prose disagrees AND the fix needs more than a token: a sign change that propagates through the interpretation, a significance change that invalidates the claim in the paragraph, a magnitude shift that changes the economic narrative. Do NOT attempt the rewrite. Record as a flag.

## Edit policy (non-negotiable)

- Change the minimum number of characters possible.
- Do not restructure sentences, reorder clauses, or add hedges.
- Do not "improve" prose, fix typos, or adjust tone.
- British English, no Oxford commas (project convention).
- Preserve LaTeX markup exactly — if the original says `$-1.63$\%`, your edit output must also say `$-<new>$\%`.
- If you cannot find the corresponding value in the artefact (e.g. the prose mentions a subsample not in the table you're looking at), record as "unresolved-in-artefact" — do not guess.

## Return format

Return a single structured block:

```yaml
section: {section_title}
edits_applied:
  - line: <line number in main.tex>
    old: "<old substring>"
    new: "<new substring>"
    artefact: "<file path>"
    reason: "<one sentence>"
flags:
  - location: "L<line>–L<line>"
    issue: "<one sentence describing why surgical edit is insufficient>"
    suggested_fix: "<one sentence pointer — not a rewrite>"
unresolved:
  - claim: "<quoted prose>"
    reason: "<what you tried and why it failed>"
```

Do not return any other prose. The orchestrator will aggregate.
````

## Edit policy (orchestrator's own copy)

The orchestrator itself must not edit main.tex. Only sub-agents edit. The orchestrator's job is inventory → dispatch → aggregate.

## What this skill does NOT do

- **Grammar / style / typos.** Different lens.
- **Check claims against cited literature.** That's `/verify-claims`-style external fact-checking.
- **Re-run the analysis.** Assumes tables/figures in the paper directory are the current truth. If they're stale, re-run your pipeline first.
- **Big rewrites.** If the story has changed, the skill flags and stops. You rewrite.

## Cross-references

- Paper-level numeric audit with tolerance thresholds (heavier): see Sant'Anna's `/audit-reproducibility` in [pedrohcgs/claude-code-my-workflow](https://github.com/pedrohcgs/claude-code-my-workflow). This skill is the lighter, section-by-section alternative.
