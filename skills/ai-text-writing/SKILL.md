---
name: ai-text-writing
description: Draft or rewrite academic prose in finance/economics following the operational style rules of Cochrane (2005) and Jacobsen (2015), and avoiding every word or phrase on the LLM-cliché lists used by ai-text-detect (Walther & Dutordoir 22-root list, Liang et al. 200 adjectives/adverbs, and Wikipedia "Signs of AI writing" words + phrases). Use when the user asks you to write, draft, rewrite, polish, or edit a paragraph, abstract, introduction, or section of an academic paper, or says things like "write in my style", "follow Cochrane/Jacobsen", "rewrite without AI words", or "remove the LLM markers from this paragraph".
---

# AI-text writing

Generate or rewrite academic prose that obeys two operational style guides and contains zero hits from the AI-marker word lists tracked by `ai-text-detect`.

## When to use

- Drafting fresh prose for an academic paper (intro, abstract, paragraph, section, response-to-referees text).
- Rewriting or polishing existing prose for the same.
- The user explicitly asks for "house style", "Cochrane/Jacobsen style", "no AI words", or similar.
- Any prose-generation task on an academic manuscript belonging to this user.

Companion to `ai-text-detect` (locate cliché words) and `ai-text-metrics` (score readability and AI-likeness).

## Procedure

1. **Load the rules.** Read both into context if not already loaded:
   - `~/.claude/skills/ai-text-writing/cochrane_writing_lessons.md`
   - `~/.claude/skills/ai-text-writing/jacobsen_writing_lessons.md`

2. **Draft the prose.** Apply the rules at every scale (word, sentence, paragraph). Avoid every word on the forbidden lists below.

3. **Self-audit (mandatory before delivering anything > 50 words).**
   - Write the draft to a temp file:
     ```
     /tmp/ai-text-writing-draft.txt
     ```
   - Run the detector:
     ```
     uv run --script ~/.claude/skills/ai-text-detect/detect.py /tmp/ai-text-writing-draft.txt
     ```
   - If `n_matches > 0`, rewrite to remove every match. Do not negotiate — even one match means rewrite.
   - Repeat until `n_matches == 0`.
   - **Then re-read the draft against the pattern rules** (negative parallelism, copula avoidance, sentence-final participle tail) and the formatting/tone rules below. The detector catches literal words and phrases but not sentence-grammar patterns or formatting/tone tics; these require a manual pass.

4. **Deliver the prose.** No commentary unless the user asked for it. If you had to substitute several words during the audit, mention the count in one short sentence at the end ("audit clean; replaced 3 forbidden words during drafting").

## Compact rule summary

### Word level (Cochrane + Jacobsen)
- Simple short words. "Use" not "utilize". "People" not "agents". "Several" not "diverse".
- No adjectives for your own work ("striking", "novel", "important").
- No acronyms — write the full term and let it shorten naturally.
- No technique names in story prose ("OLS", "GARCH").
- "Where" = a place; "in which" = a model.
- Hyphens for true compound modifiers before a noun (after-tax income, risk-free rate); not when the modifier ends in -ly.
- Italics sparingly; if you reach for emphasis, restructure the sentence.
- Greek letters: define clearly, give a name, repeat the name periodically.
- No abbreviated author names ("Fama and French", not "FF").
- Precise modifiers: "oil price changes" not "oil prices".
- "I" is fine on a sole-authored paper. "We" only if there is a co-author or if it means "you and I".

### Sentence level
- Subject–verb–object.
- Active voice. Search for "is" and "are" to root out passives.
- Present tense throughout. "Fama and French (1993) find that…", not "found".
- Anything before "that" is usually deletable. "It should be noted that…" → just say it. "We find that X" → "X".
- Cut "In this paper…" — yes, where else?
- No naked "this". Always "this regression…", "this estimate…".
- Each sentence: subject, verb, object. No fragments.
- Halve the length when you can.
- Examples first, then generalise.
- Vary sentence shape — don't reuse the same template for every result.
- One direction is enough on signs: "when X goes up, Y goes down" + "and vice versa". Drop the parentheticals.
- Don't say "I leave x for future research." Don't write "illustrative test".
- "Assume" only modifies reality (no shifts in the demand curve…). For model features, write "consumers have power utility", not "I assume…".
- **No negative parallelism.** "Not just X, but Y" and "not X, but Y" are near-signatures of post-2024 AI text. Just say Y, or "X and also Y". *Exception*: a genuine contrast where both halves carry weight ("statistically significant, not economically large") is fine — the tell is when the construction is *decorative*.
- **No copula avoidance.** Don't write "X serves as Y", "X stands as Y", "X represents a Y", or "X features / offers / maintains Y" when "X is Y" or "X has Y" would do. The detector won't catch these — they read as obvious LLM prose.
- **No sentence-final present-participle tails** of significance ("…contributing to the regional economy", "…underscoring its role", "…shaping the field"). If the claim matters, make it a full sentence. If it doesn't, drop it.

### Paragraph level
- First sentence of the abstract = the punch line (the main finding).
- No throat-clearing opening paragraph. Every claim must be defensible with a source.
- Show, don't tell. Open in the middle of the action ("Laws prohibiting insider trading came late to Germany").
- Research question + main result by paragraph 2 of the introduction at the latest.
- Give magnitudes, not just significance. "An oil price shock of one s.d. (~10%) lowers world market returns by 1%."
- Order within paragraph: what you do → why → comparison to alternatives. Most writers do this in reverse.
- Don't repeat. "In other words" is a sign the first version was wrong — fix it instead.
- Justify every choice that could look arbitrary ("data starts in 1715 because that is when the series begin"). If genuinely arbitrary, say so and announce the robustness check.
- Avoid previews and recalls ("As we will see in section 4…") — they signal poor organisation.
- **No significance-puffery closers.** Don't end a factual paragraph with a "broader trends" sentence that gestures at importance without adding content.
- **No lists as substitute for analysis.** Multi-item bullet lists of "key takeaways" / "key layers" / "key issues" where prose would carry the point. Use a list when the items are genuinely parallel and unordered; use prose otherwise.

### Formatting
- Em dashes sparingly. Default to commas, parentheses, or colons; reach for em dashes only when the parenthetical is a genuine syntactic break.
- No mechanical bold-for-emphasis. Bold belongs to defined terms and theorem names, not to "key" phrases throughout the prose.
- Avoid inline-header bullet lists (`- **Bold header:** descriptive text.`) as the dominant list form. Either write prose, or use a clean list without bold headers.
- Sentence case in section headings. Not "Sustainable Development And Environmental Law".
- No emoji as section or bullet decoration.
- No thematic breaks (`---`) before headings; the heading is itself the break.

### Tone
- No brochure register. Travel-guide / press-release language ("nestled in the heart of", "stands as a vibrant") sneaks in even when the topic is neutral.
- No canned good-faith assurances ("I am committed to…", "my intention is to…", "aligned with the mission of…").
- No knowledge-cutoff hedges in finished prose ("as of my last knowledge update", "based on available information"). If a number is dated, give the date.
- No false-neutrality scaffolding ("there are valid perspectives on both sides") unless the prose genuinely needs to present competing views.
- No over-helpful sign-offs ("I hope this helps", "let me know if you'd like more detail") — these belong in chat, not in delivered prose.

### Tables
- Self-contained captions; not novel-length.
- Regression tables: caption gives the equation and variable names, especially the LHS.
- No number in a table that isn't discussed in the text.
- Two to three significant figures. Every important number with a standard error.
- Sensible units. Percentages over decimals.

## Forbidden words (auto-audit catches these)

Drawn from `ai-text-detect/word_lists/`. Do not type any of these in a draft.

### Walther & Dutordoir 22 stemmed roots
Match anything stemming to one of these (so "delve", "delves", "delving", "delved" all hit `delv`):

`nuanc`, `delv`, `unravel`, `compel`, `underpin`, `pivot`, `catalyst`, `intertwin`, `shed`, `intrigu`, `comprehens`, `dive`, `interplay`, `intric`, `lacuna`, `meticul`, `supercharg`, `foster`, `demystifi`, `engag`, `action`, `underscor`

Common surface forms to never write: *delve, delves, delving, intricate, intricately, nuanced, unravel, unravels, compelling, underpin, underpins, pivotal, catalyst, intertwined, sheds light, intriguing, comprehensive, dive into, interplay, lacuna, meticulous, meticulously, supercharge, foster, demystify, engaging, actionable, underscore, underscores*.

### Liang et al. 200 (adjectives + adverbs, literal match)
Full lists in:
- `~/.claude/skills/ai-text-detect/word_lists/liang_2024_adjectives_100.txt`
- `~/.claude/skills/ai-text-detect/word_lists/liang_2024_adverbs_100.txt`

The most common offenders: *commendable, innovative, notable, versatile, noteworthy, invaluable, potent, ingenious, cogent, profound, methodical, laudable, seamless, holistic, robust, salient, paramount, indispensable, formidable, exemplary, esteemed, multifaceted, dynamic, nuanced, novel, cutting-edge*; *meticulously, reportedly, lucidly, aptly, methodically, excellently, compellingly, impressively, undoubtedly, intriguingly, intelligently, profoundly, deftly, robustly, palpably, eloquently, succinctly, efficaciously, intricately, scrupulously*.

When the auto-audit fires, the JSON output names the exact forms — read them off and rewrite.

### Wikipedia "Signs of AI writing" (WP-words + WP-phrases)

Drawn from the Wikipedia article "Signs of AI writing" and added to `ai-text-detect` as the `WP-words` and `WP-phrases` lists. The auto-audit catches both — so a clean detector pass means these are clean. Reproduced here so a draft can avoid them from the start rather than relying on the rewrite pass.

Single words: *tapestry, vibrant, boasts, bolstered, garner, showcase / showcasing, enhance / enhancing, highlight / highlighting (verb), enduring, nestled, renowned, groundbreaking, exemplifies*.

Phrases: *stands as, serves as, refers to, plays a key / pivotal role, reflects broader, contributing to the…, setting the stage for, evolving landscape, regulatory landscape, indelible mark, valuable insights, a testament to, align with / aligns with, resonate with / resonates with, diverse array, diverse range of, in the heart of, generated debate, prompted broader reflection, raises philosophical questions, continues to thrive, faces several challenges, despite these challenges, based on available information, maintains a low profile, deeply rooted, concrete evidence / concrete examples, rich cultural heritage, rich tapestry*.

## Substitution patterns (quick rewrites)

| Forbidden | Plain alternative |
|---|---|
| delve into | study, examine, look at |
| nuanced | careful, mixed, qualified |
| intricate | detailed, complex, hard |
| unravel | sort out, take apart |
| compelling | strong, persuasive, hard to ignore |
| underpin | support, drive, cause |
| pivotal | key, central, important |
| underscore | show, point to, make clear |
| comprehensive | full, complete, broad |
| meticulous(ly) | careful(ly), close, exact |
| foster | help, encourage, raise |
| robust | reliable, steady, holds up |
| novel / innovative | new, different, first |
| notable / noteworthy | worth noting, striking, large |
| profound | large, deep, wide |
| paramount / indispensable | essential, central, required |
| seamless | smooth, clean, without breaks |
| holistic | full, end-to-end |
| dynamic | changing, time-varying |
| reportedly | apparently, said to |
| undoubtedly | clearly, plainly, surely |
| effectively | in effect, in practice |
| tapestry / rich tapestry of | mix, range, set, body |
| vibrant | active, busy, lively (or drop) |
| boasts (a) | has |
| bolstered | strengthened, raised, backed |
| garner | get, attract, draw, win |
| showcase / showcasing | show, display, present |
| enhance / enhancing | raise, improve, add to |
| highlight / highlighting (verb) | show, point out, note |
| enduring | lasting, long-running |
| valuable insights | useful findings (or drop "insights") |
| landscape (abstract) | setting, conditions, market, environment |
| testament to | shows, proves, signals |
| nestled (in the heart of) | in, located in, on |
| renowned | well-known, famous |
| groundbreaking | new, first, novel (or drop) |
| exemplifies | shows, is an example of |
| deeply rooted | long-standing, old |
| stands as / serves as | is |
| marks / represents a | is |
| features / offers / maintains (a) | has |
| refers to | is |
| plays a key / pivotal role | matters, drives, causes |
| underscores its importance | shows that it matters |
| sheds light on | shows, makes clear |
| reflects broader | is part of, fits with |
| contributing to the … | adds to, raises |
| setting the stage for | leads to, opens the way for |
| evolving landscape | changing market / setting |
| align with / resonate with | match, fit, agree with |
| diverse array / diverse range of | many, several, a range of |
| in the heart of | in, at the centre of |
| generated debate / prompted reflection | led to debate, started a debate |
| faces several challenges, including… | rewrite as a plain list of the problems |
| despite these challenges, … continues to thrive | rewrite without the boilerplate |
| not just X, but Y | rewrite: just say Y, or "X and also Y" |
| not X, but Y | rewrite: just say Y |
| it's important / worth noting that | drop; state the point |
| as of my last knowledge update | drop; if dated, give the date |
| based on available information | drop |
| concrete evidence / examples | evidence / examples |

If none of these fits, rewrite the sentence so it does not need the word.

## Output expectation

Return only the prose. If the user asked for an edit, return the edited version (a diff if explicitly requested, otherwise the full new text). Do not narrate the rules you applied. The audit step runs silently; only mention substitutions if there were many.

## Caveats

- The detector is sentence-level and case-insensitive. Stems mean "delve", "delved", "delving" all hit; spelling matters less than root.
- The Liang list flags some legitimate words ("present", "current"). The detector treats them as literal hits — if a flagged word is unavoidable in context (e.g., quoting another paper), tell the user and leave it; do not silently keep it.
- The skill assumes finance/economics conventions. Adjust word substitutions for other fields if the user is writing outside those areas.
