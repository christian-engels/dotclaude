---
name: newbook
description: Scaffold a new book project — folders, memoir-based LaTeX skeleton, custom style with voiced sidebars, bibliography stub, CLAUDE.md, README, and a chapter-per-file structure that converts cleanly to HTML later. Use at the start of a book project to get a compileable skeleton in one step. Parallel to /newproject and /bibcheck.
allowed-tools: Bash(mkdir*), Bash(cp*), Bash(ls*), Bash(pdflatex*), Bash(touch*), Read, Write, Edit
argument-hint: '[book-slug] [optional --title="Title"] [optional --chapters=N]'
---

# Newbook: Scaffold a Book Project

Scaffold the standard structure Scott uses for a long-form book: memoir-based LaTeX, Palatino body, Gov-2001 palette, voiced-sidebar callouts, one chapter per file, a bibliography stub, a CLAUDE.md with voice and lineage rules, and a README.

This is the skill that produced *AI Agents and the Research Worker*. Use it any time a book-shaped project is starting.

## When this skill is invoked

The user is starting a book or book-shaped manuscript. They will give a slug (the folder name) and optionally a title and a chapter count.

## Step 1: Get the arguments

1. **Slug** (required): the folder name. Convert spaces to dashes; lowercase. If absent, ask.
2. **Title** (optional, default = title-case of the slug): the book's working title.
3. **Chapter count** (optional, default = 11): how many numbered chapters to scaffold (plus `00_frontmatter` and an unnumbered conclusion).

If unclear, ask before scaffolding. Do not guess.

## Step 2: Confirm location

Default location is the current working directory. Confirm if the user has not stated where. If a folder with the slug already exists and is non-empty, **stop** and ask whether to continue (this skill never overwrites).

## Step 3: Create the directory structure

```bash
mkdir -p <slug>/{chapters,style,bibliography,correspondence,decks,figures,code,drafts,progress_logs,substacks}
```

## Step 4: Write the core files

Each file below is written from a template in this skill's `templates/` directory. Substitute `__TITLE__`, `__SLUG__`, `__AUTHOR__`, `__DATE__`, and `__CHAPTERS__` per the arguments.

| File | Source template |
|---|---|
| `<slug>/book.tex` | `templates/book.tex.tmpl` |
| `<slug>/style/<slug>.sty` | `templates/style.sty.tmpl` |
| `<slug>/CLAUDE.md` | `templates/CLAUDE.md.tmpl` |
| `<slug>/README.md` | `templates/README.md.tmpl` |
| `<slug>/bibliography/<slug>.bib` | `templates/bib.bib.tmpl` |
| `<slug>/decks/README.md` | `templates/decks_README.md.tmpl` |
| `<slug>/chapters/00_frontmatter.tex` | `templates/00_frontmatter.tex.tmpl` |
| `<slug>/chapters/NN_<name>.tex` (one per chapter) | `templates/chapter.tex.tmpl` |
| `<slug>/progress_logs/__DATE__-setup.md` | `templates/progress_log.md.tmpl` |

For the chapter stubs, generate `01.tex` through `<N>.tex` (default 11) with placeholder titles like `Chapter <n>` that the user will replace. Each stub contains a `\chapter{}`, a `% SUBSTACK MAP:` placeholder block, a TODO bullet list, and one example `\voice{Verifier}{...}` sidebar.

## Step 5: Sanity compile

Run `pdflatex book.tex` once and report whether it compiled. Do not require zero warnings on the first compile — the skeleton is a starting point, not a finished book.

## Step 6: Report

Show the user:

```
<slug>/ scaffolded.

  Title:     <title>
  Chapters:  <N> + frontmatter + conclusion stub
  Compile:   <pdflatex book.tex> succeeded / had warnings (see book.log)

Next steps:
  - Open CLAUDE.md and edit the voice cast and lineage rules for this book.
  - Open chapters/01.tex and replace the placeholder title.
  - Run /bibcheck bibliography/<slug>.bib once you have real entries.
```

## Design decisions baked into the templates

- **memoir** as the document class. Maximum flexibility; converts cleanly to HTML for online versions.
- **Palatino** via `mathpazo` (Palatino math is included; no `eulervm` because it's not in TinyTeX by default).
- **Gov 2001 palette** (charcoal, slate, ocean, forest, crimson, warmgray, lightbg).
- **Voiced sidebars** via `\voice{<name>}{<text>}` — named voices have fixed colors; unknown voices fall to charcoal.
- **`idea` and `warn` callouts** as `tcolorbox` environments.
- **One chapter per file** under `chapters/`, all `\input`-ed from `book.tex`. Enables HTML conversion later.
- **`\graphicspath{{figures/}{substacks/}}`** — figures from either folder work without per-include path.
- **`\flushbottom`** + `\emergencystretch=3em` — fewer overfull-hbox warnings on book-length text.
- **`\documentclass[..., openany]{memoir}`** — chapters do not force right-side opens (cleaner page count for skeleton).

## Voice cast (default — user customizes via CLAUDE.md)

| Voice | Color |
|---|---|
| Fisher | slate |
| Ricardo / Thompson | warmgray |
| Skeptic | charcoal |
| Manager | ocean |
| IC | forest |
| Verifier | crimson |
| Goldin / Katz / Autor / Acemoglu | ocean |
| Schumpeter | warmgray |

User adds or renames voices in `style/<slug>.sty` and documents the cast in `CLAUDE.md`.

## What this skill does NOT do

- It does not write prose. It writes stubs.
- It does not invent citations. The `.bib` is empty until the user provides entries.
- It does not run `biber` or process bibliography. The first compile is `pdflatex` only; once entries exist, the user runs the full chain.
- It does not push to GitHub. That is a separate user action.
