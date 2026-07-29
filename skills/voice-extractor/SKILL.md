---
name: voice-extractor
description: Read a corpus of the user's published papers (PDFs) and produce a VOICE.md style guide capturing recurring phrasing, sentence rhythm, hedging style, structural moves, and a ban list. Triggers when the user asks to "extract my voice", "build a voice file from these papers", or runs /voice-extractor.
args:
  papers_dir: directory of PDFs (default: sample-papers/)
  output: output path (default: output/VOICE.md)
---

# voice-extractor

A four-phase skill. Each phase ends with a checkpoint the user can interrupt.

## Phase 1 -- discover

List PDFs in `papers_dir`. If fewer than 3 files, **stop and ask** for more -- voice extraction needs a corpus, not a single sample.

For each PDF, read the prose body. Skip the references section, appendices, and the contents of tables -- voice lives in the running text. Note which sections each paper has (intro / data / methodology / results / robustness / conclusion) so Phase 2 can sample from comparable slots across papers.

## Phase 2 -- extract patterns

For each paper, jot (in working memory, not on disk):
- 3 representative opening sentences of major sections
- 3 representative transitions or hedges (e.g., "Importantly, ...", "We caution that ...")
- 1 example each of: introducing a new result, qualifying a claim, citing prior work, framing the contribution
- sentence-length distribution (qualitative: short / medium / long, with a rough ratio)
- notable diction: favored verbs, recurring phrases, characteristic qualifiers

If a paper is co-authored with very different voices, note that and weigh it less.

## Phase 3 -- synthesize

Write a single `VOICE.md` with these sections:
1. **Stance** -- first/third person, hedging level, formality, audience
2. **Sentence rhythm** -- typical lengths, parallel-construction habits, paragraph openers
3. **Recurring phrases** -- annotated examples, each tagged with the paper of origin
4. **Structural moves** -- how openings / contributions / robustness paragraphs are framed
5. **Diction preferences** -- favored verbs, qualifiers, transitions
6. **Ban list** -- words/phrases that **don't** appear (negative space matters)
7. **Worked example** -- one short paragraph rewritten in this voice

## Phase 4 -- verify

Re-read the VOICE.md you just wrote. For each entry under **Recurring phrases**, confirm that phrase actually appears in at least 2 of the source PDFs (use Grep over the extracted text). If a claim fails, drop or weaken it.

In the final message to the user, list any phrases that were dropped or weakened in this verify step. **This is the pedagogical point of the skill** -- the gate must be visible.
