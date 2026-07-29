---
name: research-idea-ground
description: "Use when Claude should ground a finance or economics research idea, paper, proposal, introduction, grant pitch, or referee response by verifying its non-literature factual premises: institutional mechanics, scale, affected populations, decision makers, market structure, policy and legal timelines, regulation, datasets, and practical stakes. Ground or challenge a candidate framing with authoritative evidence while keeping factual context separate from academic novelty, intellectual importance, final X–Y–Z–S construction, and causal identification."
---

# Research Idea — Ground

## Purpose

Establish what is factually true about a proposed research setting and its practical stakes. Verify the premises on which a research frame might depend; surface facts that weaken the story as readily as facts that support it.

This skill grounds a frame but does not construct or adjudicate it.

## Boundaries

- Do not claim academic novelty, contribution, or a literature gap.
- Do not construct final X, Y, Z, or S statements.
- Do not treat scale, growth, regulation, controversy, or policy attention as intellectual importance.
- Do not infer beliefs from an actor’s exposure, authority, title, or organisational incentives.
- Do not simulate stakeholders or create composite personas.
- Do not perform a causal identification audit or convert institutional facts into a causal claim.
- Do not invoke, hand off to, or depend on another skill.

## Source Hierarchy

Prefer:

1. official statistics, government departments, central banks, regulators, courts, parliaments, and treaty bodies;
2. laws, regulations, rulebooks, enforcement notices, consultations, official guidance, and policy statements;
3. exchanges, payment systems, registries, company filings, audited disclosures, prospectuses, and investor materials;
4. documented institutional datasets and codebooks;
5. industry associations, infrastructure providers, and professional reports;
6. media, consulting, advocacy, and blogs only as leads or clearly qualified secondary evidence.

When sources disagree, report the discrepancy and prefer the most direct authoritative source.

## Workflow

### 1. Define The Factual Setting

Specify:

- jurisdiction, market, sector, product, population, institution, and period;
- relevant firms, households, regulators, intermediaries, or platforms;
- measured objects such as prices, balances, uptake, defaults, complaints, access, or market shares; and
- whether the unit is local, national, cross-country, firm, household, transaction, or institution.

Proceed with a reasonable scope when the idea is underspecified and state the assumption.

### 2. State The Premises To Verify

Turn the proposed motivation into checkable propositions:

```text
Institutional condition claimed:
Magnitude or prevalence claimed:
Affected population claimed:
Actor with authority or exposure:
Decision or outcome said to matter:
Timing or policy change claimed:
Measurement opportunity claimed:
```

Do not search merely for supportive facts. Include propositions whose failure would narrow or contradict the story.

### 3. Build And Record The Search

Search for:

- scale, incidence, concentration, adoption, balances, flows, and geographic variation;
- institutional mechanics, eligibility, contracts, exemptions, thresholds, and enforcement;
- dated reforms, consultations, implementation, entry, exit, mergers, and reporting changes;
- named actors, documented authority, affected outcomes, and observable decision margins;
- datasets, identifiers, units, coverage, access, frequency, revisions, and breaks; and
- relevant comparators across regimes, places, firms, products, or populations.

Record search strings, source names, URLs, dates, and failed searches.

### 4. Verify Currentness And Meaning

For each material fact, record:

- publication date and date checked;
- period and population covered;
- exact units and definitions;
- whether the fact is stable, periodically revised, current as of a date, or volatile;
- pending reforms, delayed implementation, sunset clauses, or data breaks; and
- whether the source documents the fact directly or supports only an inference.

Never present a time-sensitive fact as timeless.

### 5. Extract Factual Stakes

Identify:

- who bears a documented outcome or controls a documented decision margin;
- the magnitude, prevalence, or distribution of that outcome;
- the institutional channel through which exposure or authority arises;
- which real decision could use better evidence; and
- what remains factually uncertain.

These facts may support premises behind practical importance. They do not by themselves establish why an informed academic reader should change a belief.

### 6. Test The Proposed Story

Ask:

- Which premises are directly supported?
- Which hold only for a narrower jurisdiction, period, population, or definition?
- Which facts point toward a different motivation?
- Which claims rest on industry estimates, lobbying, marketing, or advocacy?
- Which institutional detail undermines the proposed mechanism or comparator?
- Does the setting provide an actual measurement opportunity, or only an interesting narrative?

Separate facts, sourced inference, and unresolved conjecture.

### 7. Assign A Factual Verdict

Use one:

- **supported:** authoritative facts support the proposed factual premises;
- **narrower:** support exists only for a more limited setting, period, population, or claim;
- **differently-supported:** the evidence supports a materially different factual motivation;
- **insufficient:** key facts, dates, definitions, or data paths remain unresolved;
- **contradicted:** authoritative evidence conflicts with a necessary premise.

This is a verdict on factual grounding, not on academic contribution or whether the project should proceed.

## Output

Write `research-idea-ground.md` in the project folder unless the user requests another path. Include:

### Factual Premises Table

| Proposition | Evidence | Geography or institution | Period | Source | Date checked | Stability | Assessment |
|---|---|---|---|---|---|---|---|

### Institutional Map And Timeline

Explain how the product, market, rule, or institution works. List exact dates for reforms, consultations, implementation, enforcement, entry, exit, mergers, shocks, and reporting changes.

### Actors, Outcomes, And Decision Margins

Record documented exposure or authority without attributing unobserved beliefs:

| Actor or role | Documented exposure or authority | Outcome | Decision margin | Source | Limits |
|---|---|---|---|---|---|

### Candidate Datasets

For each dataset, report provider, unit, coverage, variables, frequency, access route, documentation, breaks, missingness, and the factual proposition it could measure.

### Factual Stakes

Write three to five concise paragraphs explaining the scale, affected population, institutional channel, relevant real-world decision, and remaining uncertainty. Avoid academic contribution language.

### Counterevidence And Caveats

Report unstable facts, conflicting numbers, narrower definitions, legal uncertainty, access barriers, uncovered populations, and reliance on non-primary sources.

### Source Log

Record searches, sources, dates, URLs, source types, rejected leads, and failed searches.

### Factual Verdict

State one verdict with two to four evidence-based reasons.

## Quality Bar

A strong scan makes the institutional setting inspectable, verifies dates and units, identifies documented stakes and decision margins, and reveals limiting facts.

A weak scan pads an introduction with large numbers, treats attention as importance, repeats unsourced institutional claims, or searches only for confirmation.
