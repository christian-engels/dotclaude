---
name: research-idea-explore
description: Use when Claude should explore beyond the academic literature for emerging issues, weak signals, contradictions, “flying pigs,” practitioner concerns, policy shifts, market anomalies, new technologies, or institutional details that may supply raw material for a finance or economics research problem. Surface candidate tensions, revealing boundaries, possible interpretations, and verification needs while keeping the output speculative; do not construct a final X–Y–Z–S frame, claim academic novelty, or decide contribution.
---

# Research Idea — Explore

## Purpose

Expand the space of possible research problems by finding concrete external-world signals that are strange, contradictory, newly consequential, or difficult to reconcile with a plausible baseline.

Treat the scan as disciplined abduction, not academic evidence. Generate possibilities; do not adjudicate the final research frame.

## Boundaries

- Label every output speculative.
- Separate documented facts from interpretations and possible research uses.
- Do not claim a literature gap, novelty, publishability, welfare effect, or causal mechanism.
- Do not construct final X, Y, Z, or S statements.
- Do not turn market size, media attention, controversy, or one unusual anecdote into importance.
- Do not invoke, hand off to, or depend on another skill.

## Source Strategy

Prefer primary and near-primary sources:

1. regulation, legislation, consultations, enforcement, court records, and official statistics;
2. company filings, earnings calls, investor materials, product documentation, and market infrastructure rules;
3. industry and practitioner reports with identifiable methods and sources;
4. journalism, newsletters, podcasts, blogs, and social media only as leads unless their factual basis can be verified.

Search relevant domains:

- regulation, litigation, policy debate, enforcement, and regulatory arbitrage;
- earnings calls, filings, risk factors, investor questions, and product launches;
- data releases, APIs, reporting changes, new identifiers, and measurement technologies;
- complaints, workarounds, grey markets, outages, fraud, churn, defaults, and unusual adoption;
- contract terms, incentives, governance arrangements, legacy systems, and jurisdictional exceptions.

## Workflow

### 1. Define The Focal Area And Baseline

State:

- the market, institution, actor, behaviour, or policy being scanned;
- the likely informed baseline or conventional intuition;
- the period and jurisdictions in scope; and
- what kind of signal would genuinely challenge or complicate that baseline.

Keep the academic baseline brief. This is not a literature review.

### 2. Generate Search Angles

Translate the focal area into practitioner and institutional language. Search across:

- actors and counterparties;
- products, contracts, technologies, and decision margins;
- rules, exemptions, loopholes, failures, complaints, bans, pilots, settlements, and workarounds;
- newly observable data and measurement changes; and
- adjacent markets or boundaries through which effects may propagate.

Record actual search strings, sources, dates, and jurisdictions.

### 3. Collect And Verify Signals

For each candidate, record:

- what happened or exists;
- source, date, market, and actor;
- whether the fact is verified, partly verified, or only a lead;
- why it is new, growing, contradictory, underexplained, or unusually measurable; and
- whether another source independently corroborates it.

Reject generic trends and uncheckable anecdotes.

### 4. Identify Flying Pigs

Treat a signal as a flying pig only when it:

- conflicts with a reasonable baseline, policy intent, common theory, or market design;
- is specific enough to verify;
- has at least one plausible economic interpretation; and
- could matter beyond the colourful fact itself.

Use:

| Signal | Source and status | Baseline contradicted | Why strange | Possible interpretations | Verification needed | Curiosity risk |
|---|---|---|---|---|---|---|

### 5. Interpret Without Closing

For each strong signal:

- propose no more than three plausible interpretations;
- identify the actor, constraint, incentive, resource, or boundary each interpretation requires;
- distinguish a descriptive fact from a causal explanation;
- state what evidence would discriminate among the interpretations; and
- name the main reason the signal may fail as a research lead.

### 6. Extract Framing-Relevant Observations

Do not write the research frame. Instead record:

```text
Baseline intuition apparently contradicted:
Possible economic tension:
Potentially revealing institution or boundary:
Actors and decision margins implicated:
Fact that must be verified:
Evidence needed to distinguish interpretations:
Reason the signal may remain a curiosity:
```

These are candidate inputs, not conclusions.

### 7. Triage

Assign one scan-specific status:

- **discard:** weak, unverified, unsurprising, or unlikely to travel beyond the anecdote;
- **monitor:** potentially meaningful but too early or poorly evidenced;
- **investigate:** sufficiently grounded and consequential to justify targeted verification or empirical exploration.

Keep the triage separate from enthusiasm.

## Output

Write `research-idea-explore.md` in the project folder unless the user requests another path. Include:

1. **Scope and baseline**
2. **Strongest signals**
3. **Flying-pigs table**
4. **Framing-relevant observations**
5. **Possible interpretations**
6. **Verification and discriminating evidence needed**
7. **Source log and coverage limits**
8. **Triage**

When proposing future directions, describe them as hypotheses about what may be worth investigating. Do not claim academic novelty.

## Quality Bar

A strong scan is surprising but disciplined. It supplies exact institutional details, makes the contradicted baseline explicit, separates facts from interpretations, and shows how the signal could be verified or killed.

A weak scan is a list of trends, news stories, fashionable technologies, or generic research opportunities.
