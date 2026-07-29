# Dialogue Protocol

## Contents

- [Governing Rule](#governing-rule)
- [Establish the Evidence Boundary](#establish-the-evidence-boundary)
- [Select a Mode](#select-a-mode)
- [Acquire Comparator Evidence](#acquire-comparator-evidence)
- [Maintain an Internal Case Map](#maintain-an-internal-case-map)
- [Reconstruct the Epistemic Anatomy](#reconstruct-the-epistemic-anatomy)
- [Ask Adaptive Questions](#ask-adaptive-questions)
- [Move Between the Two Criteria](#move-between-the-two-criteria)
- [Know When to Stop Asking](#know-when-to-stop-asking)
- [Present the Strongest Defensible Formulation](#present-the-strongest-defensible-formulation)
- [Handle Sparse or Resistant Cases](#handle-sparse-or-resistant-cases)
- [Citation Discipline](#citation-discipline)

## Governing Rule

Run a Socratic assessment, not a questionnaire or instant referee report. Ask one
adaptive question at a time, use each answer to choose the next question, and
withhold the verdict until the user has corrected or confirmed the strongest
defensible formulation.

## Establish the Evidence Boundary

At the outset:

- use only the frozen framework for diagnostic claims;
- use project materials, user-supplied closest work, and adequate
  `search-literature` artefacts for candidate-specific claims;
- do not browse or search databases ad hoc;
- assume methodological correctness;
- separate factual novelty from the articulation of a novelty claim; and
- identify missing evidence rather than filling it with inference.

If the user explicitly requests a source-bounded assessment, do not search. If
the user asks for a correctness audit, say that identification, measurement,
methods, and execution are outside scope. Continue only with broad interest and
sufficient leap.

## Select a Mode

### Idea mode

Use idea mode when the user supplies a seed, paragraph, pitch, or underdeveloped
proposal.

First establish, one item at a time:

1. the research question;
2. the intended scholarly audience or outlet; and
3. the claimed contribution relative to what that audience already knows.

Do not request all three in a single barrage. If one answer supplies several
items, record them and ask only for the remaining uncertainty.

### Draft mode

Use draft mode when the user supplies a proposal, paper, substantial memo, or
folder containing project materials.

Before asking a question:

1. read the supplied draft;
2. read supplied closest papers and any current literature map, or their relevant
   sections;
3. extract an evidence ledger; and
4. identify which framework questions the documents already answer.

The evidence ledger should contain:

| Field | Extract from the documents |
|---|---|
| Research question | The most specific answerable formulation |
| Audience or outlet | Named field, subfield, or outlet |
| Prior | What an informed reader currently believes |
| Stakes | Scientific, economic, practical, or institutional consequence |
| Scope | Why the insight travels beyond the immediate setting |
| Claimed contribution | The exact knowledge or capability change |
| Closest work | Supplied or searched comparators and their established results |
| Delta | What changes relative to each comparator |
| Hypothesis provenance | Premises and deductive, imported-prior, abductive/ex-post, or unknown status |
| Counterfactual scope | Treatment, mechanism/design, and intellectual counterfactuals |
| Prior map | Expected sign, timing, allocation, margins, heterogeneity, mechanism, and stakes |
| Contribution-bearing result | The finding that carries the largest useful knowledge change |
| Claim ladder | Outcome-to-behaviour-to-harm-to-welfare-to-policy transitions and their status |
| Coherence conflicts | Predictions or interpretations that conflict across the supplied documents |
| Result dependence | What preferred, conventional, null, and heterogeneous results teach |
| Unverified claims | Assertions the supplied evidence cannot establish |

Cite each extracted item to a page, section, or explicit user statement. Do not
ask the user to restate what the documents already show.

### Mixed mode

If a developed draft is supplied without adequate closest-work evidence, use
draft mode and run the controlled search below unless the request is
broad-interest-only or explicitly source-bounded.

## Acquire Comparator Evidence

After establishing enough of the question, audience, and claimed contribution to
define a search seed, decide whether comparator discovery is required.

Run `search-literature` automatically when the assessment concerns sufficient
leap, factual novelty, originality, or a gap claim and no current, adequately
scoped map or comparator set exists. Do not search for a broad-interest-only
assessment. Do not search when Christian requests a source-bounded assessment.
Reuse an adequate map rather than rerunning it.

Treat a map as adequate only when:

- Seed And Versions Covered matches the candidate and claimed contribution;
- layers 1, 2, and 3 ran;
- known-item validation did not fail; and
- layer 4 ran when books or grey literature are materially relevant.

Also inspect its date, fields, source types, and stated limits. Frontier-sensitive
claims require a map current enough to bear them, but no mechanical expiry rule
substitutes for judgment. An adequately scoped user-supplied comparator set can
also satisfy the requirement when it permits a direct delta against the closest
two or three works or a defensible triangular comparator set.

Run a missing search in a clean context by launching a fresh general-purpose
subagent with the Agent tool (never a fork, so it inherits no conversation
context). Pass only the search seed, relevant scope cues, output
directory, and the `search-literature` skill name; instruct the subagent to write
`literature-search-map.md` and `literature-search-log.md` and return only the
Handoff block.

On return, read the map's Seed And Versions Covered, Evidence Quality, closest
precedents, frontier, neighboring literature or field map, Open Questions, and
Handoff. Consult only the known-item validation and reference-verification
entries needed from the log. Do not read or reproduce the raw search transcript.

If the search fails or coverage is partial, continue the Socratic assessment of
the articulated contribution. Record exactly which factual novelty remains
unverified and whether the cause is a missing field, source type, layer, date
range, known-item failure, or unresolved reference.

## Maintain an Internal Case Map

Track four kinds of statements:

- **Established:** directly supported by project material, supplied closest work,
  or a verified searched comparator, with its provenance retained.
- **Claimed:** asserted by the user or draft but not independently supported.
- **Inferred:** a charitable interpretation needed to connect the argument.
- **Unknown:** material to the assessment and not yet answered.

Do not expose the full ledger unless useful. Use it to prevent repetition and to
distinguish evidence from interpretation.

## Reconstruct the Epistemic Anatomy

Before asking a question in draft mode, run the epistemic-anatomy pass in
`evidence-framework.md` internally:

1. trace each load-bearing prediction to its minimum supplied premises;
2. distinguish treatment, mechanism/design, and intellectual counterfactuals;
3. map the informed prior across the dimensions the candidate actually changes;
4. identify the contribution-bearing result rather than assuming it is the
   headline result;
5. assign distinct roles to a small admissible comparator set when no single
   twin exists; and
6. trace the claim ladder from measured outcome through any harm, welfare, or
   policy claim.

Do not turn this pass into another checklist interview. If the documents resolve
an item, record it. If an unknown could materially change the assessment, ask
only the single highest-value question. Surface a compact prior-to-update table
only when it makes the knowledge change materially easier to see.

## Ask Adaptive Questions

Ask the question whose answer has the greatest chance of changing the eventual
assessment. Prefer a focused challenge over a generic prompt.

### Broad-interest question bank

Use these as possibilities, not a script:

- Which scholarly audience should revise a belief because of this project?
- What real outcome, decision, institution, or scientific bottleneck is affected?
- What would matter if the answer were conventional rather than surprising?
- Why does the question travel beyond this country, sample, event, or platform?
- What could a researcher, household, firm, or policymaker do or understand
  differently?
- Which credible follow-on questions exist even if the headline result is null?
- Would this result belong in a future survey, and in what role?
- What is the first-order stake in the specific relation, not merely in the
  fashionable topic surrounding it?
- Which transition from the measured outcome to behaviour, harm, welfare, or
  policy carries the stakes, and what supplied evidence supports it?

### Sufficient-leap question bank

- What is the single closest comparator, and what exactly does it already
  establish?
- Complete: “Before this project we know ___; afterward we know or can do ___.”
- Which assumption in the closest work changes?
- Is the contribution a question, result, mechanism, measure, dataset, method,
  capability, synthesis, adjudication, or boundary condition?
- What becomes newly explainable, testable, measurable, or usable?
- Why is this more than the same relation in a new setting?
- What does the null or conventional result change relative to the closest work?
- Who can use the contribution as a new point of departure?
- If the project consolidates rather than displaces prior work, why is that
  consolidation valuable?
- Which finding survives an informed reader's “of course” objection?
- What minimum premises generate the load-bearing prediction, and did those
  premises also predict its timing, margin, or heterogeneity?
- Does the claimed distinctive mechanism require a comparison with an
  economically equivalent alternative that the supplied evidence does not make?
- If no single closest paper is a twin, what are the treatment sibling,
  conceptual predecessor, and outcome or method mirror?

### Proxy challenges

When the user relies on a proxy, name it neutrally and ask for the missing case.

Examples:

- “The topic is economically large, but that does not yet establish the stakes of
  this specific question. Which decision or belief would change?”
- “A new country is a setting difference. What theoretically useful contrast
  makes it a knowledge difference?”
- “Technical difficulty establishes effort, not contribution. What new insight
  or reusable capability does the technique create?”
- “A surprising sign creates attention. What would an unsurprising or null result
  teach?”
- “An empty literature cell establishes absence, not value. Why should the cell
  be occupied?”
- “The novelty claim is clear. What scientific or practical utility follows from
  it?”

Do not accuse the user of making a weak argument. Treat the proxy as a hypothesis
that needs its substantive link supplied.

## Move Between the Two Criteria

Do not finish all broad-interest questions before considering the leap. Alternate
when an answer creates a dependency.

Examples:

- If the user identifies a major stake, ask whether the closest literature has
  already resolved it.
- If the user identifies a large leap, ask who benefits from that knowledge
  change.
- If the contribution depends on a method, ask both what capability it creates
  and which consequential question that capability unlocks.
- If the setting creates external validity, ask which prior changes because the
  boundary is newly revealed.

## Know When to Stop Asking

Move to formulation when:

- the question, audience, and claimed contribution are explicit;
- the strongest case and strongest objection for each criterion are visible;
- the intellectual prior, contribution-bearing result, and counterfactual scope
  are explicit;
- any load-bearing hypothesis-provenance or claim-ladder uncertainty has been
  identified;
- additional answers would mainly add detail rather than change the assessment;
  and
- comparator coverage and any remaining factual-novelty limit have been clearly
  identified.

Do not force every question in the bank. A short dialogue can be sufficient when
the documents are rich.

## Present the Strongest Defensible Formulation

Before any verdict, write a compact formulation containing:

1. the question;
2. the audience and stakes;
3. the informed prior and relevant counterfactual scope;
4. the closest-work baseline;
5. the contribution-bearing result;
6. the exact knowledge, interpretation, or capability change; and
7. why the two criteria reinforce each other.

Use this pattern:

> **Strongest defensible formulation**
>
> [Two or three concise paragraphs stating the best evidence-supported case.]
>
> Is this a fair statement of the project at its strongest, or what should I
> correct?

Wait. Do not append the final assessment to this checkpoint.

If the user corrects it, revise the formulation internally and use the corrected
version. If the user confirms it, proceed. If the user supplies material new
enough to change the case, ask one further adaptive question only if necessary.

## Handle Sparse or Resistant Cases

If the evidence cannot establish an audience, stake, prior, closest comparator,
or contribution:

- record the absence as evidence;
- ask one clarifying question if a useful answer remains possible; and
- do not manufacture the missing premise.

If the user declines further questions, present the strongest formulation that
the existing record supports and ask for confirmation. The final assessment
remains unavailable until that opportunity to correct has been given.

## Citation Discipline

For framework claims, use author-year plus physical PDF page:

`(Edmans, 2025, PDF p. 3)`

For candidate claims:

- cite a draft by filename and page or section;
- cite a closest paper by author-year and supplied PDF page;
- cite a searched comparator to `literature-search-map.md`, its section, and its
  verified DOI or primary URL;
- cite an idea as `(user-supplied idea, current conversation)`; and
- label charitable synthesis as inference.

Never imply that a framework source establishes a candidate-specific novelty
claim.
