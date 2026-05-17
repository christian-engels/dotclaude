---
name: ai-text-detect
description: Find and locate every LLM-cliché word or phrase in a paper given as a .tex (with \input/\include resolution), .pdf, or .txt, and show the user where each one occurs with sentence context. Use when the user asks to "find AI-words", "highlight LLM markers", "locate AI cliches", "show me where the AI words are", or wants to edit them out of a draft. Word lists drawn from Walther & Dutordoir (2025), Liang et al. (2024), and the Wikipedia article "Signs of AI writing".
allowed-tools: Agent, Read, Write, Bash(ls*), Bash(jq*)
---

# AI-text detect

Locate every occurrence of an LLM-cliché word in a paper and show the user where each one is, with sentence context, so they can review or edit.

## When to use

- The user wants to *see* the AI-list words in a draft, not just a metric. Typical phrasings: "find the AI words", "where are the LLM cliches", "highlight the words from the Walther/Liang lists", "show me what to edit".
- Companion to `ai-text-metrics` (which only returns aggregate scores).

## How this works

The detector produces a lot of JSON for long papers — every match plus its sentence context. To keep the main session light, the script runs inside a subagent which writes the full JSON, the markdown report, and the cleaned prose to disk **next to the source file** (e.g. `main.tex` → `main.tex_ai-detect.json`, `main.tex_ai-detect.md`, `main.tex_prose.txt`) and returns only the report inline. Follow-ups spawn another subagent that reads from the saved artefacts. The full paper text never enters the main context.

The regex pass catches literal words and phrases. Three follow-ups extend it: a specific word lookup, a "rewrite" pass that suggests non-cliché alternatives in context, and a "patterns" pass that runs an LLM scan for sentence-grammar tells (negative parallelism, participle puffery), paragraph-level patterns (significance closers, lists as analysis), and tonal markers (brochure register, false neutrality) that regex can't catch.

## Procedure

1. **Get the path** — a `.tex`, `.pdf`, or `.txt` file. Confirm it exists.

2. **Spawn one `general-purpose` subagent** via the `Agent` tool. Use this prompt, with `<PATH>` replaced by the absolute path:

   ```
   Run the AI-text detector on <PATH>, save outputs next to the source file, and return ONLY a formatted markdown report.

   Output paths (derive from <PATH>):
     JSON_PATH   = <PATH>_ai-detect.json
     REPORT_PATH = <PATH>_ai-detect.md
     PROSE_PATH  = <PATH>_prose.txt
   These sit in the same directory as the source file. Overwrite if they already exist.

   Steps:
   1. Run: `uv run --script ~/.claude/skills/ai-text-detect/detect.py <PATH> --prose-out <PROSE_PATH> > <JSON_PATH>`
   2. Read the JSON. It contains:
      - source, n_sentences, n_matches
      - summary: word → {count, stem, lists}, sorted by descending count
      - matches: every occurrence as {word, stem, lists, sentence_idx, context}
   3. Compose the markdown report:

      # AI-list words in <basename>

      <one-line summary, e.g.: "47 hits across 8 distinct words in 1,293 sentences (3.6% of sentences contain at least one). Full JSON: <JSON_PATH>">

      ## Summary

      | Word | Count | Lists |
      |---|---|---|
      | delve | 12 | WD-10, WD-22 |
      ...

      ## Occurrences

      ### delve (12, WD-10 + WD-22)
      1. "We **delve** into the question of whether…"
      2. "These results allow us to **delve** deeper into…"
      ...

      ### intricate (8, WD-22 + Liang-200)
      ...

   4. Write the report to <REPORT_PATH> via the Write tool.

   Rules:
   - Group occurrences by word, sorted by total count.
   - Bold the matched word inside each context sentence with markdown **…**. Match case-insensitively.
   - Cap each group at 10 contexts; if more, end with `… and N more (see JSON)`.
   - If the document has > 80 total occurrences, show only the top 15 most-frequent words by default and add a line: "X more words in the JSON — ask if you want to see them."

   List labels:
   - WD-10 — Walther & Dutordoir 10-word root list
   - WD-22 — Walther & Dutordoir 22-word extended root list
   - Liang-200 — Liang et al. 100 adjectives + 100 adverbs
   - WP-words — Wikipedia "Signs of AI writing" single-word list (literal)
   - WP-phrases — Wikipedia "Signs of AI writing" phrase list (case-insensitive, word-boundary)

   Caveats to mention if relevant:
   - For .tex input, matching runs on prose only — math, tables, figures, citations, bibliography are stripped.
   - For .pdf input, extraction includes the references list — may pick up stray hits (e.g. "delve" in a paper title in the bibliography). Mention this if many hits cluster at the document end.
   - WD-22 uses Porter stemming (delve / delves / delving / delved → delv). Liang-200 and WP-words are literal (common morphological forms enumerated).
   - WP-phrases are case-insensitive word-boundary substring matches. Some entries fire on legitimate prose ("refers to", "serves as", "stands as") — review in context before rewriting.

   Return your reply in this exact format (no other text):

   JSON_PATH: <JSON_PATH>
   REPORT_PATH: <REPORT_PATH>
   PROSE_PATH: <PROSE_PATH>
   ---
   <the markdown report>
   ```

3. **Parse the subagent's reply.** The first three lines give `JSON_PATH`, `REPORT_PATH`, and `PROSE_PATH` — remember all three for follow-ups. Relay everything below the `---` to the user as the report, and tell the user the file paths in one short line at the top: "Saved to `<REPORT_PATH>` (full JSON: `<JSON_PATH>`)."

4. **Offer next steps** in one short line at the end:
   - "Reply with a word to see all its occurrences, 'rewrite' for non-cliché alternatives in context, or 'patterns' for an LLM scan of sentence-grammar and tonal tells that regex can't catch (~1 min, separate report)."

## Follow-up handling (same session)

If the user asks for more detail on a specific word or for rewrites, spawn another `general-purpose` subagent rather than reading the JSON yourself. This keeps the main context light.

**"Show all occurrences of <word>"** — subagent prompt:

```
Read <JSON_PATH> and print every match where match.word equals "<word>" (case-insensitive).
Format: numbered list of context sentences, with the matched word bolded with **…**.
Return only the list — no preamble.
```

**"Rewrite these"** — subagent prompt:

```
Read <JSON_PATH>. For each unique word in the matches, suggest 2–3 non-cliché alternatives that fit academic finance/economics prose, then for each context sentence show the original and a rewritten version side by side. Keep meaning intact; do not introduce new claims.
Return: a markdown table per word (Original → Rewrite), then a one-paragraph note on words that are hard to replace.
```

**"Patterns"** — derive `PATTERNS_PATH = <PROSE_PATH with '_prose.txt' replaced by '_ai-patterns.md'>`. Then spawn a subagent with this prompt (with `<PROSE_PATH>` and `<PATTERNS_PATH>` filled in):

```
Read <PROSE_PATH> and scan it for AI-writing pattern tells that don't show up in literal word matching. Write the report to <PATTERNS_PATH>.

For each instance found, report:
- The pattern type
- A short sentence quote (or paragraph quote if context is needed)
- One line explaining why it's flagged

Do NOT suggest rewrites. Just flag. Rewrites are a separate follow-up.

Patterns to scan for:

1. **Negative parallelism** — "not just X, but Y" / "not X, but Y" / "no X, no Y, just Z" constructions. Flag only when decorative — the construction adds rhetorical flourish but the underlying claim could be made directly. Skip when both halves carry substantive weight ("statistically significant, not economically large" is a genuine contrast — leave it).

2. **Sentence-final present-participle puffery** — sentences ending in "-ing" tails that gesture at significance without adding content ("…contributing to regional development", "…underscoring its role as a hub", "…shaping the field"). Skip participle phrases that carry actual information.

3. **Significance-puffery paragraph closer** — paragraphs ending with a "broader trends" or "wider importance" sentence that doesn't add substance to the factual content above.

4. **Lists as substitute for analysis** — bullet lists of "key takeaways" / "key issues" where prose would carry the point. Skip lists that are genuinely parallel and unordered (enumeration of variables, criteria, robustness checks, etc.).

5. **Brochure register** — passages where the tone slips into travel-guide or press-release language. Symptoms: "nestled in", "stands as a vibrant", "thriving community", positivity-by-default.

6. **False-neutrality scaffolding** — sentences like "there are valid perspectives on both sides" forced into otherwise factual paragraphs, especially when the paper is taking a substantive position.

7. **Knowledge-cutoff hedges** — framings like "as of [date]", "based on available information", "while specific details are limited" used to fill gaps the author should just acknowledge directly.

Report structure:

# Pattern scan: <basename>

<one-line summary: total flagged, breakdown by pattern type>

## Negative parallelism

1. (location hint if possible — e.g., "section 3, ~halfway through")
   "<sentence quote>"
   — <one-line reason>

(repeat per instance, per pattern type)

If a pattern type has zero instances, write "_None flagged._" under its heading.

**Be conservative.** The author has likely written legitimate prose that uses some of these constructions in non-decorative ways. When in doubt, do NOT flag — false positives waste the author's time. Flag confidently only when the pattern is *decorative* / *puff* / *evasive* in the AI-prose sense.

Return your reply in this exact format (no other text):

PATTERNS_PATH: <PATTERNS_PATH>
---
<the markdown report>
```

After the subagent returns, relay: "Pattern scan saved to `<PATTERNS_PATH>`." plus the full markdown report below. Mention these two caveats once (not on every follow-up):
- LLM pattern scans are non-deterministic — two runs may differ slightly. If a flag looks borderline, ask for a second pass.
- If the prose was drafted by `ai-text-writing` using the same model now scanning it, blind spots may align. For high-stakes drafts, a human editor pass is still warranted.

## Output expectation

The report and JSON are always written to disk next to the source file (overwriting any prior run). The report is also relayed inline in the conversation. No `analysis-outputs/` redirection — co-locating with the source means re-running the skill automatically supersedes the old artefacts.
