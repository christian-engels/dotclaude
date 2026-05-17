---
name: ai-text-metrics
description: Compute readability and AI-style linguistic metrics for an academic paper given as a .tex file (with \input/\include resolution) or a .pdf, and write a short interpreted report. Use when the user wants to score a draft for "AI-likeness", check Flesch-Kincaid / Gunning-Fog readability, or measure how heavily a piece of text relies on LLM-cliché word choice. Implements the metric battery from Walther & Dutordoir (2025) and Liang et al. (2024).
allowed-tools: Agent, Read, Write, Bash(ls*)
---

# AI-text metrics

Score a paper for readability and likely LLM influence, then produce a short written report.

## When to use this skill

- The user asks you to "score this paper for AI-likeness", "check how AI-sounding this draft is", "compute readability", "run the Walther / Liang metrics", or similar.
- The user supplies a path to a `.tex` file (typically `main.tex`, possibly with `\input{...}` or `\include{...}` to other files), a `.pdf`, or a plain `.txt`.

## How this works

This skill delegates the work (running the script, parsing JSON, drafting the report) to a subagent. The subagent writes the report to disk **next to the source file** (e.g. `main.tex` → `main.tex_ai-metrics.md`) and also returns it inline. The main session never sees the full paper text — only the report.

## Procedure

1. **Get the path.** If the user hasn't given an absolute path, ask for one or resolve it from context. Confirm the file exists.

2. **Spawn one `general-purpose` subagent** via the `Agent` tool. Use this prompt, with `<PATH>` replaced by the absolute path:

   ```
   Run the AI-text metrics script on <PATH>, save the report next to the source file, and return the report inline.

   Output path:
     REPORT_PATH = <PATH>_ai-metrics.md
   It sits in the same directory as the source file. Overwrite if it already exists.

   Steps:
   1. Run: `uv run --script ~/.claude/skills/ai-text-metrics/compute.py <PATH>`
      It is a self-contained PEP 723 script — `uv` will fetch dependencies the first time.
      For .tex it recursively resolves \input/\include/\subfile, drops preamble, strips math/tables/figures/bib commands.
      For .pdf it extracts text via pypdf.
      Output is a JSON object with metric values, n_words, n_sentences, source path, and a short text preview.
   2. Sanity-check: if n_words < 200 or the preview looks garbled, flag this at the top of the report (LaTeX strip dropped too much, or PDF extraction failed).
   3. Compose the report in markdown, under ~400 words:
      - One headline sentence (readable / borderline / heavy LLM markers).
      - Markdown table with columns: metric, value (rounded), pre-ChatGPT mean, deviation in SDs.
      - Short interpretation paragraph per group: readability, AI-word density, lexical diversity.
      - One trailing line on caveats if any (short text, PDF issues, math-heavy paper).
      - Rounding: FKI/GFI to 1 dp; AI-word densities as percentages with 2 dp; TTR to 2 dp; MTLD to 0 dp.

   Benchmarks (Walther & Dutordoir 2025, Table 1; n = 41,489 finance journal articles 2000–2025):

   | Metric | Pre-ChatGPT mean | SD | Mean post-ChatGPT shift |
   |---|---|---|---|
   | FKI (Flesch-Kincaid grade) | 14.17 | 1.64 | +0.95 |
   | GFI (Gunning-Fog grade) | 17.39 | 1.94 | +1.15 |
   | W/S (words/sentence) | 21.08 | 2.84 | ≈ 0 |
   | Syl/W (syllables/word) | 1.83 | 0.10 | +0.08 |
   | CW/W (complex-word ratio) | 0.236 | 0.039 | +0.028 |
   | AI words (10-list) | 0.01% | 0.03% | +0.02 pp |
   | AI words (22-list) | 0.06% | 0.11% | +0.07 pp |
   | AI words (200-list, Liang) | 2.56% | 1.23% | +0.78 pp |

   Interpretation cues:
   - FKI / GFI: years of formal education needed. FKI > 16 ≈ master's; > 18 ≈ post-graduate. >2 SDs above pre-ChatGPT mean = unusually dense for finance.
   - AI words (10/22): rare in pre-ChatGPT writing. Above ~0.3% is striking; above ~1% is glaring.
   - AI words (200, Liang): higher baseline (~2.6%); flag above ~5%. List flags stylistic words ("notable", "particularly", "effectively") so high score reflects style as much as authorship.
   - TTR / MTLD: lexical diversity. MTLD < 60 narrow vocab (typical of unedited LLM); 80–120 typical for edited academic prose. TTR is length-sensitive — only compare across texts of similar length.
   - W/S, Syl/W, CW/W: FKI/GFI components. High CW/W (>0.30) with normal W/S = long words rather than long sentences — LLM-polished signature.

   4. Write the report to <REPORT_PATH> via the Write tool.

   Return your reply in this exact format (no other text):

   REPORT_PATH: <REPORT_PATH>
   ---
   <the markdown report>
   ```

3. **Parse the subagent's reply.** The first line gives `REPORT_PATH`. Relay everything below the `---` to the user, prefixed with one short line: "Saved to `<REPORT_PATH>`."

## Output expectation

The report is always written to disk next to the source file (overwriting any prior run) and also relayed inline. No `analysis-outputs/` redirection — co-locating with the source means re-running the skill automatically supersedes the old artefact.
