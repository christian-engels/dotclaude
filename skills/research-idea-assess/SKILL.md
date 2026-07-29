---
name: research-idea-assess
description: Use when Claude should assess whether a finance or economics research idea, proposal, or paper addresses a question of sufficiently broad interest and makes a sufficient leap over existing literature. Interrogate breadth, importance, originality, contribution, general-interest appeal, or gap claims through Socratic questioning and a narrative assessment. Automatically obtain an auditable comparator map with search-literature when factual novelty requires it and adequate current comparators are absent. Exclude audits of identification, measurement, methods, and execution.
---

# Research Idea — Assess

## Purpose

Interrogate two distinct questions: whether the project matters broadly enough and
whether it changes knowledge enough relative to the closest work. Treat neither
criterion as a numerical score and do not let strength on one silently compensate
for failure on the other.

Evaluate the strongest supplied or user-confirmed formulation. The charitable
formulation checkpoint below prevents assessment of a straw man; it is not a
substitute for constructing a new research frame.

## Load the Framework

Before substantive assessment, read these files completely:

- `references/evidence-framework.md` for the two-criterion diagnostic.
- `references/dialogue-protocol.md` for idea mode, draft mode, and questioning.
- `references/narrative-assessment.md` for the final assessment.
- `references/corpus-provenance.md` for source scope and citation provenance.

Do not substitute memory, outside literature, or other repository syntheses for
these references. Keep their 18-source diagnostic corpus frozen. Candidate-specific
comparator evidence may come from the user's materials or from `search-literature`
under the controlled workflow below; it never alters the framework.

## Enforce the Boundary

- Assess broad interest and sufficient leap only.
- Invoke only `search-literature`, and only under the comparator-evidence rules
  below. Do not hand off the assessment itself.
- Assume correctness. Do not audit identification, measurement, causal claims,
  methods, data quality, power, robustness, or execution.
- Never browse or search databases ad hoc. Route all candidate-specific external
  literature discovery through `search-literature`.
- Use project materials, user-supplied closest work, and adequate
  `search-literature` artefacts only for the candidate-specific assessment.
- Keep the assessor's diagnostic sources distinct from searched comparators.
- Cite framework claims by author-year and PDF page. Cite candidate-specific
  claims to the supplied idea, draft, supplied closest paper, or verified
  literature-map entry.
- Treat the framework as an expert-derived diagnostic, not a validated predictor
  of publication or impact.

## Obtain Comparator Evidence

Run `search-literature` automatically when both conditions hold:

1. the requested assessment includes sufficient leap, factual novelty,
   originality, or a gap claim; and
2. no current, adequately scoped literature map or comparator set is available.

Do not search for a broad-interest-only assessment. Do not search when Christian
explicitly requests a source-bounded assessment. Reuse an adequate supplied or
project-local map rather than rerunning it.

Treat a literature map as adequate only when:

- its seed and versions covered match the idea and claimed contribution;
- layers 1, 2, and 3 ran;
- known-item validation is `pass` or `partial` with a corpus-boundary explanation,
  never `fail`; and
- layer 4 ran when books or grey literature are materially relevant.

Also check that its search date is current enough for the frontier-sensitive claim
being assessed and that its field and source-type scope match the intended
audience. Do not impose a mechanical expiry date.

Before searching, establish enough of the question, audience, and claimed
contribution to define the seed. Then launch an isolated subagent with the
Agent tool (a fresh general-purpose agent, never a fork, so it inherits no
conversation context) and instruct it to invoke the `search-literature` skill,
write `literature-search-map.md` and
`literature-search-log.md` in the agreed project or temporary output directory,
and return only its `Handoff` block. Pass only the search seed, scope cues, output
directory, and skill name; do not pass the assessor's tentative judgment.

After the subagent finishes, read the map's Seed And Versions Covered, Evidence
Quality, comparator sections, Open Questions, and Handoff. Read only the relevant
known-item and reference-verification evidence from the log when needed; never
import the raw search transcript into the assessment context.

If the search fails or coverage is partial, continue to assess the articulated
contribution. State exactly which factual novelty claim remains unverified and
which missing field, source type, layer, date range, or validation failure causes
the limit.

## Run the Assessment

1. **Choose the mode.**
   - Use idea mode for a seed, pitch, or underdeveloped proposal.
   - Use draft mode when a proposal, paper, or substantial project document is
     supplied.
2. **Establish the case.**
   - In idea mode, establish the research question, intended scholarly audience
     or outlet, and claimed contribution.
   - In draft mode, first extract what the documents already establish about the
     question, audience, stakes, closest work, and exact contribution. Ask only
     about unresolved points.
3. **Establish the comparator basis.** Reuse adequate supplied evidence or run
   the isolated `search-literature` workflow above when its two trigger conditions
   hold.
4. **Question adaptively.** Ask one concise question at a time. Move between broad
   interest and sufficient leap according to the weakest or most uncertain
   premise. Challenge false proxies explicitly.
5. **Formulate before judging.** Present the strongest defensible version of the
   question and contribution. Ask the user to correct it and wait for the
   correction or confirmation.
6. **Write the assessment.** After the formulation is confirmed or corrected,
   return the required narrative assessment. Use no numerical score and no fixed
   verdict category.

## Handle Scope Conflicts

- If the user requests a correctness audit, explain that correctness is assumed
  here and keep any assessment limited to the two criteria. Do not perform the
  audit under this skill.
- If the user requests an external novelty search as part of this assessment,
  use `search-literature`; do not browse independently.
- If the user's documents answer a question, do not ask it again.
- If an answer exposes a false proxy—fashion, scale, surprise, a new setting,
  technical difficulty, or novelty without utility—name the proxy and ask for the
  missing substantive case.

## Preserve the Interaction

- Keep each turn short enough for the user to answer one thing.
- Do not announce a verdict during questioning.
- Do not turn the framework into a checklist interview; adapt to prior answers.
- Distinguish a question's attractiveness from verified novelty.
- Preserve uncertainty and competing interpretations.
- End the completed assessment with one most informative revision or evidence
  request, not a diffuse list of generic improvements.
