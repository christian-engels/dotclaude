---
name: ai-text-verify-refs
description: Verify an academic reference by cascading through Web of Science → Scopus → OpenAlex, stopping at the earliest stage that leaves no doubt. Accepts a free-text citation snippet (as messy as needed) or a .bib file path. Claude interprets the input, plans a search, escalates between sources only when the previous stage's result is missing or ambiguous, discusses results with the user, and offers a suggested BibTeX entry to copy. Use before submitting a manuscript or when cross-checking any reference.
allowed-tools: Agent, Read, Bash(curl*), Bash(jq*), Bash(cat*), Bash(ls*), Bash(~/.claude/skills/ai-text-verify-refs/helpers/*), WebSearch, WebFetch
argument-hint: '[free-text reference OR path to .bib]'
---

# ai-text-verify-refs: cross-check a reference against Scopus, WoS, and OpenAlex

The user hands you something ragged — a hand-typed line, a paper snippet, a half-remembered citation, a `.bib` entry, a list of several — and expects you to interpret it, look each reference up, and return a clean BibTeX entry per reference.

This skill is not a deterministic parser. Interpretation, query planning, reconciliation, and web fallback are all judgement calls that a Claude agent makes per reference.

The work splits in two:
- **Main session (orchestrator)**: parses input → spawns one `opus` subagent per reference → stitches the returned blocks into one reply.
- **Subagent (one per reference)**: follows Steps 2–6 below to verify a single reference and returns a markdown block.

Read the **Orchestration** section next if you are the main session; skip straight to **Step 2** if you are a subagent spawned by the orchestrator.

---

## Scope

This skill finds *the specific reference(s)* the user has in mind and verifies them.

It does **not** do topical literature search. When the user's input is a bare topic phrase (e.g. `"financial literacy and fraud detection"`) with no author, year, title, or DOI anchor:

- Do **not** present a menu that includes "literature search" as an option. Literature search is out of scope.
- Assume the user has a specific paper in mind. Try to identify it.
- Use whatever you have: the topic phrase itself (run a search and inspect the top hits), any author/year/venue/DOI hints elsewhere in the conversation, and — if the user is plausibly asking about their own work — the user profile (memory / CLAUDE.md / git `user.email`).
- If a single plausible candidate emerges, treat it as the reference and continue with the normal verify-and-output flow. In your write-up, tell the user what you identified and ask them to confirm or correct.
- Only ask for more detail (author/year/title) if no plausible candidate surfaces after a reasonable search attempt.

If the input genuinely describes multiple papers (separate lines, a numbered list, several `@article{...}` blocks, or phrasing like "these three papers"), verify each one individually using the normal multi-reference output format.

---

## Orchestration (main session only — read this first)

The **main session** is an orchestrator. It does not run any API calls itself. It parses the input, spawns one subagent per reference, stitches the returned blocks into a single reply, and appends a summary line. All searching, all API calls, all web fallback happen inside subagents.

### Main-session workflow

1. **Parse input → list of references.** See Step 1 below. For a `.bib` file, enumerate entries. For free text, split on blank lines / numbered items. For a single citation, wrap it as a list of one.

2. **For each reference, spawn one subagent** via the `Agent` tool, in a single assistant message with one `Agent` call per reference so they run in parallel. Parameters:
   - `subagent_type`: `general-purpose`
   - `model`: `sonnet`
   - `description`: e.g. `Verify reference [3]: Baker Wurgler 2006`
   - `prompt`: use the template below.

3. **Subagent prompt template** (fill in `<REFERENCE>` and optionally `<CITEKEY>`):

   ```
   You are verifying ONE academic reference by cascading through Web of Science → Scopus → OpenAlex, with a web-search fallback for books / reports / grey literature. Stop the cascade at the earliest stage that leaves no doubt — do not query later stages unless the previous one's result is missing, incomplete, or ambiguous. The playbook also describes a routing rule that skips straight to OpenAlex or to the web fallback when the input's smell clearly warrants it (working papers / books / policy reports).

   **Playbook**: read /Users/ce50/.claude/skills/ai-text-verify-refs/SKILL.md (Steps 2 through 6) and /Users/ce50/.claude/skills/ai-text-verify-refs/api_reference.md. Follow the playbook for this one reference.

   **Reference to verify** (verbatim from user):
   <REFERENCE>

   **Citation key** (preserve this in the suggested BibTeX if non-empty): <CITEKEY>

   **Constraints**:
   - You are a subagent. You cannot ask the user clarifying questions. If something is ambiguous, make your best call and note the assumption in the discrepancies section.
   - Do NOT pivot to a topical literature search. The user has a specific paper in mind; identify it, or report Not found.
   - Respect the cascade: never query later stages "just to be sure" when the earlier stage returned a clean DOI-level match. Token saving is the whole point.
   - Use the web-search fallback (Step 4b) when the cascade exhausts itself without a credible hit.
   - Return ONLY the Step 6 markdown block (verdict + per-source bullets + discrepancies + BibTeX). No preamble, no sign-off, no mention of being a subagent. The orchestrator will stitch your block into the final reply.
   ```

4. **Collate** all subagent returns. Prepend each with a header `### [N] <citekey-or-shortlabel> — <status>` where `<status>` is taken from the subagent's verdict line.

5. **Append a one-line summary**: `N verified, N probable, N conflict, N found via web, N not found.`

6. **Never** run `curl`, `jq`, the helper scripts, `WebSearch`, or `WebFetch` yourself as the orchestrator. The subagents do that.

### When the subagents report blocking issues

If a subagent's returned block says the `.env` is missing or the API keys are unset (see the "If the user hasn't set up keys yet" section below), don't re-run the reference — surface the message to the user so they can fix the config, then stop.

---

## Step 1: Accept input (orchestration)

The orchestrator performs this step to produce the list of references, then delegates each to a subagent.

- **If the argument is a path to a `.bib` file** → read it with the `Read` tool; each `@article{...}` / `@book{...}` / `@inproceedings{...}` etc. entry becomes one subagent. Preserve the original citation key and pass it to the subagent as `<CITEKEY>`.
- **If the argument is free text that looks like a single citation** (author, year, title, DOI, venue combination) → one subagent.
- **If the argument is a bare topic phrase** (no anchor) → see the **Scope** rules. Treat as one reference and delegate to one subagent, which will attempt identification. Do not offer a literature search.
- **If multiple references are clearly separated** (blank lines, a numbered list, several `@article{...}` blocks) → one subagent per reference, fired in parallel.
- **If no argument** → ask the user to paste the reference(s) they want verified.

Steps 2 through 6 below are the **subagent's playbook**, not the orchestrator's. The orchestrator does not run them.

---

## Step 2: Plan the search

For each reference, spend a moment identifying the strongest handles:

- **Strongest**: a DOI. Always lead with a DOI query if one is present.
- **Strong**: a distinctive multi-word title phrase (3–5 words, ideally including an unusual noun) + year.
- **Medium**: first-author surname + year.
- **Disambiguators**: co-author, journal, pages, volume.

Also decide where in the Step 3 cascade to start: a journal-article-looking reference starts at WoS; a working paper / SSRN / NBER / arXiv / policy-report smell routes straight to OpenAlex; a book / chapter / thesis routes straight to the web fallback (Step 4b). Write a one-line plan before calling anything so the user can see your thinking. Example:

> **Plan:** Journal article, no DOI. Starting cascade at **WoS** with title phrase `"investor sentiment" "cross-section"` + author `Baker` + year `2006`.

## Step 3: Query sources sequentially (cascade)

Goal: stop at the earliest stage that leaves no doubt. Only escalate when the previous stage returned nothing, returned a match without a DOI, returned multiple plausible candidates, or any key field (title / first author / year) failed to match cleanly. Every stage you skip is saved tokens.

The default order puts the highest-quality metadata first: **Web of Science → Scopus → OpenAlex → web fallback (Step 4b)**. Do **not** fire these in parallel.

### Routing: skip stages the input can't plausibly hit

Before calling any API, read the input carefully. Route around stages that obviously won't index the item:

- **Working paper / grey-literature smell** (SSRN, NBER, CEPR, IZA, BIS, ECB, IMF, arXiv, "mimeo", "working paper", `@techreport`, `@misc`, a ssrn.com / arxiv.org / repec.org URL) → **skip WoS and Scopus; start at Stage 3 (OpenAlex)**. WoS and Scopus don't index this material, so calling them is pure token waste.
- **Book / book chapter / thesis / policy brief / white paper** (publisher name, ISBN, `@book`, `@incollection`, `@phdthesis`) → **skip all three APIs; go straight to the web-search fallback (Step 4b)**.
- **Otherwise** (looks like a journal article) → start at Stage 1 below.

### Stage 1: Web of Science

Narrowest index, highest metadata quality. Query WoS first for plain journal articles.

```bash
# DOI
~/.claude/skills/ai-text-verify-refs/helpers/wos_search.sh 'DO=<doi>'

# Title + year
~/.claude/skills/ai-text-verify-refs/helpers/wos_search.sh 'TI="<phrase>" AND PY=<year>'
```

**Stop the cascade here if**: exactly one hit whose DOI, title, first author, and year all match the user's input cleanly.

**Escalate to Stage 2 if**: no hits after refinement (Step 4), multiple plausible hits with no clear winner, a match without a DOI, or any field mismatches in a way that leaves doubt.

### Stage 2: Scopus

Broader than WoS, still well-curated. Query Scopus only if Stage 1 left doubt.

```bash
# DOI
~/.claude/skills/ai-text-verify-refs/helpers/scopus_search.sh 'DOI(<doi>)'

# Title + year
~/.claude/skills/ai-text-verify-refs/helpers/scopus_search.sh 'TITLE("<phrase>") AND PUBYEAR IS <year>'
```

See `api_reference.md` for full query syntax and response field paths.

**Stop the cascade here if**: Scopus returns a clean match on its own, or Scopus's top hit confirms Stage 1's ambiguous hit (same DOI).

**Escalate to Stage 3 if**: Scopus is also empty, still ambiguous, or disagrees with Stage 1 (different DOI for apparently the same reference).

### Stage 3: OpenAlex (no API key)

Broadest coverage, free, aggregates Crossref (so DOI-level lookups are authoritative). Query OpenAlex only if the first two stages left doubt — or if the routing rule above sent you here directly.

Use the `CONTACT_EMAIL` from the skill's `.env`. Read it once with:

```bash
grep '^CONTACT_EMAIL=' ~/.claude/skills/ai-text-verify-refs/.env | cut -d= -f2
```

Then construct:

```bash
# DOI path
curl -s "https://api.openalex.org/works/doi:<DOI>?mailto=<EMAIL>" | jq '.'

# Search path
curl -sG "https://api.openalex.org/works" \
    --data-urlencode 'search=<title phrase>' \
    --data-urlencode "per_page=5" \
    --data-urlencode "mailto=<EMAIL>" | jq '.results'
```

**Stop the cascade here if**: OpenAlex returns a clean match (ideally DOI-level).

**Escalate to Step 4b (web fallback) if**: OpenAlex is also empty after refinement — the item is probably a book, report, or other non-journal material.

### Reading responses

For each raw JSON response, pipe through `jq` to extract just the fields you need (see `api_reference.md` for exact paths). Do **not** dump the full JSON into the conversation — extract the fields, keep it tight.

If a helper exits non-zero because a key is missing, report that stage as unavailable and proceed to the next stage.

## Step 4: Refine within a stage before escalating

When a stage returns nothing or an ambiguous result, try refining the query on the *same* stage first. A focused refinement returns less JSON than a fresh broad query at the next stage.

For each response ask yourself:

- Did the API return anything?
- Does the top hit's title, year, and first author match the user's input? (Fuzzy is fine — a typo or an author initial swap shouldn't disqualify a match.)
- If nothing matched, try again: drop the year filter, try a shorter or different title phrase, try author+year alone, check for obvious typos in the user's input.

Allow up to **2 refinement attempts per stage** before escalating to the next stage. Escalation is usually cheaper than a third refinement, because the next source may have the item indexed differently and find it on the first try.

If the user's input contains a DOI that returns no hits in the stage you're in, don't keep hammering that stage — escalate. If the DOI returns no hits in *any* stage you try, it's probably wrong — mention this and try title/author as a fallback in whatever stage the cascade is on.

## Step 4b: Web-search fallback (for books, reports, grey literature)

If — after refinement — **all three APIs return no plausible match**, do not jump to "not found". The reference may be a book, book chapter, working paper, policy report, thesis, or other grey-literature item that Scopus/WoS/OpenAlex don't index well.

Fall back to `WebSearch`:

1. Construct a search query from the strongest handles: the full citation string if short, or `"<title>" <author> <year>`. Add venue/publisher if you have it (e.g. `"Princeton University Press"`, `"SSRN"`, `"NBER"`, `"BIS"`).
2. Inspect the top hits. Trust these domains in roughly this order:
   - Publisher pages (CUP, OUP, Springer, Elsevier, Wiley, MIT Press, Princeton UP, etc.)
   - Google Scholar / Google Books
   - Repositories: SSRN, NBER, CEPR, IZA, BIS, RePEc / IDEAS, arXiv
   - Institutional repositories (author's university), author home pages
   - DOI.org resolutions
3. If a single hit is clearly the right item, optionally use `WebFetch` on the landing page to extract precise bibliographic fields (title, authors, year, publisher, place, ISBN, pages).
4. If nothing credible turns up (only blog snippets, vendor listings with no details, or clearly wrong results), stop — do not fabricate. Report "not found" in Step 6.

### Infer the right BibTeX entry type from what you find

- Book → `@book` — needs author/editor, title, year, publisher, address (city), ISBN if available.
- Edited volume chapter → `@incollection` — author, title, editor, booktitle, year, publisher, pages.
- Working paper / technical report → `@techreport` — author, title, institution, number, year. For SSRN, keep `url` + `urldate`.
- PhD thesis → `@phdthesis` — author, title, school, year.
- Policy brief / white paper / anything else → `@misc` — author, title, howpublished (e.g. `{BIS Working Paper No.~987}`), year, url.

Always include a `url` field for the web-fallback source so the user can click through.

## Step 5: Reconcile

Synthesise what the stages you queried returned. Under the cascade, "Verified" from a single stage is acceptable when the evidence is strong — that is the whole reason for stopping early.

| Status | Criterion |
|---|---|
| **Verified** | The stage that stopped the cascade returned a clean DOI-level match (DOI + title + first author + year all align cleanly). OR — if the cascade escalated — ≥2 stages agreed on the same work. |
| **Probable** | A match was found but without a DOI, or title+year matched but authors disagreed on initials/order, or only OpenAlex returned a hit for a paper that *should* have been in WoS/Scopus. |
| **Conflict** | Two stages were queried and returned *different* works (different DOIs for what looks like the same input). Do not collapse quietly — report both candidates. |
| **Found via web** | Step 4b identified the item on a credible page — use this for books, reports, working papers, theses. |
| **Not found** | No plausible match from the cascade and the web fallback turned up nothing credible. |

Pick the canonical record: the stage that stopped the cascade is the canonical source. If escalation happened and stages disagreed, prefer the DOI-majority result; when tied, prefer WoS > Scopus > OpenAlex. For `Found via web`, use the publisher/repository page as the canonical source. Note any discrepancies between the user's input and the canonical record (wrong year, typo in title, different page range, missing DOI, wrong author order, etc.).

## Step 6: Return your block (subagent output format)

**Do not write a file.** Do not address the user directly. Return a single markdown block in your final message — the orchestrator will stitch it together with any sibling blocks.

Include:

### 1. One-line verdict

Examples:
- "**Verified** — WoS returned a clean DOI-level match; cascade stopped at Stage 1."
- "**Verified** — WoS ambiguous, Scopus confirmed with same DOI; cascade stopped at Stage 2."
- "**Probable** — OpenAlex hit only; WoS and Scopus both empty (possibly a working paper)."
- "**Conflict** — WoS and Scopus returned different papers. Details below."
- "**Found via web** — not in WoS/Scopus/OpenAlex, but identified on the publisher page. Looks like a book/report/working paper."
- "**Not found** — no plausible match across the cascade and web fallback turned up nothing credible."

### 2. What each source said

Short bullets, one line each, in cascade order: WoS, Scopus, OpenAlex. Include DOI, year, journal+volume/issue, pages. Say "same" if a source agrees with the one above. For stages the cascade skipped, write "not queried — <reason>" so it's obvious why — this is the visible proof of token saving.

Examples:

> - WoS: Baker & Wurgler (2006), *Journal of Finance* 61(4), 1645–1680, DOI `10.1111/j.1540-6261.2006.00885.x`
> - Scopus: not queried — WoS returned a clean DOI-level match.
> - OpenAlex: not queried — cascade stopped at WoS.

Or when escalation happened:

> - WoS: no hits (tried DOI and title+year).
> - Scopus: Baker & Wurgler (2006), *Journal of Finance* 61(4), 1645–1680, DOI `10.1111/j.1540-6261.2006.00885.x` — clean match, cascade stopped here.
> - OpenAlex: not queried — Scopus resolved it.

Or when routing skipped straight to OpenAlex:

> - WoS: not queried — SSRN working paper, not indexed by WoS.
> - Scopus: not queried — same reason.
> - OpenAlex: Engels (2024), SSRN working paper 4567890, DOI `10.2139/ssrn.4567890`.

If this was a web-fallback, replace the three bullets with the source you used and a link, e.g.:
> - Scopus / WoS / OpenAlex: no hits.
> - Web: Princeton University Press catalogue — https://press.princeton.edu/books/paperback/... — confirmed ISBN, author, year, publisher.

### 3. Discrepancies vs the user's input

Only include if there are any. Keep it short:

> **Flagged**: user had year `2007`; correct is `2006`.

### 4. Suggested BibTeX entry

A clean `@article{...}` block in a fenced code block. Populate from the canonical record. Prefer DOI + ISSN + full author list + full page range.

Citation key conventions:
- If the user's input was a `.bib` entry with a key, **preserve that key**.
- Otherwise use `firstauthorLastYear` camelCase (e.g. `bakerWurgler2006`, `bolton2019`).

```bibtex
@article{bakerWurgler2006,
  author  = {Baker, Malcolm and Wurgler, Jeffrey},
  title   = {Investor Sentiment and the Cross-Section of Stock Returns},
  journal = {Journal of Finance},
  year    = {2006},
  volume  = {61},
  number  = {4},
  pages   = {1645--1680},
  doi     = {10.1111/j.1540-6261.2006.00885.x},
  issn    = {0022-1082}
}
```

### If not found

Do **not** fabricate a BibTeX entry. Instead, report the nearest near-misses (if any) and ask the user to confirm or correct. Example:

> Couldn't find this paper in any source. Closest near-miss: *Smith (2023)* "The Real Effect of ..." — was that perhaps what you meant?

### Multiple references

Not your concern as a subagent — you verify one reference. The orchestrator prepends the `### [N] <citekey> — <status>` header and appends the final summary line across all references.

---

## File layout (for your reference)

```
~/.claude/skills/ai-text-verify-refs/
├── SKILL.md                # this file
├── api_reference.md        # per-source query syntax + response field paths
├── .env                    # API keys — git-ignored, mode 600
├── .env.example            # template
├── .gitignore              # excludes .env
└── helpers/
    ├── scopus_search.sh    # sources ../.env, adds Scopus auth headers
    └── wos_search.sh       # sources ../.env, adds WoS auth header
```

Consult `api_reference.md` when you need exact query syntax or the field path to parse out of a JSON response.

## If the user hasn't set up keys yet

A helper script exiting with "Error: ~/.claude/skills/verify-refs/.env not found" or "Error: SCOPUS_API_KEY is not set" means the user hasn't populated `.env`. Tell them:

> Before first use, run:
> ```
> cp ~/.claude/skills/ai-text-verify-refs/.env.example ~/.claude/skills/ai-text-verify-refs/.env
> chmod 600 ~/.claude/skills/ai-text-verify-refs/.env
> ```
> then edit `.env` and paste your Scopus and WoS API keys.

Then proceed with whatever sources are available (OpenAlex always works — it needs no key).
