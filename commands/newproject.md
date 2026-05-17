---
name: newproject
description: Scaffold a new research project with standard structure, CLAUDE.md, and documented README. Use at the start of every new project.
allowed-tools: Bash(mkdir*), Bash(cp*), Write, Read
argument-hint: [project-name]
---

# New Project Scaffold

Create a new research project folder with Scott's standard structure.

## Usage

```
/newproject craigslist-media-bias
```

## What Gets Created

```
[project-name]/
├── CLAUDE.md              # Permanent research rules (copied from template)
├── README.md              # Project-specific overview (auto-generated)
├── code/
│   ├── R/
│   ├── python/
│   └── stata/
├── data/
│   ├── raw/               # Original source data (never modify)
│   └── clean/             # Cleaned/merged datasets
├── output/
│   ├── tables/
│   └── figures/
├── documents/             # Outside PDFs, papers (use /split-pdf on these)
├── decks/                 # Beamer presentations (rhetoric of decks)
├── notes/                 # Scratch notes, random ideas, misc
└── progress_logs/         # Session continuity across Claude conversations
```

## Steps

1. **Get the project name**
   - From argument, or ask user
   - Convert spaces to hyphens if needed

2. **Determine location**
   - Default: current directory
   - Ask user to confirm if unclear

3. **Create directory structure**
   ```bash
   mkdir -p [project-name]/{code/{R,stata,python},data/{raw,clean},output/{figures,tables},documents,decks,notes,progress_logs}
   ```

4. **Create CLAUDE.md from template**

   Copy the template from `~/mixtapetools/claude/CLAUDE.md` and update:
   - Replace `[Your Name]` with `Scott`
   - Update project overview section with project name

5. **Create README.md**

   Generate a README that includes the visual directory tree and explains each folder:

   ````markdown
   # [Project Name]

   ## Project Structure

   ```
   [project-name]/
   ├── CLAUDE.md              # Research rules & estimation philosophy (permanent)
   ├── README.md              # This file — project-specific notes
   ├── code/
   │   ├── R/                 # R scripts
   │   ├── python/            # Python scripts
   │   └── stata/             # Stata do-files
   ├── data/
   │   ├── raw/               # Original source data (never modify these)
   │   └── clean/             # Cleaned and merged datasets
   ├── output/
   │   ├── tables/            # Generated tables (LaTeX, CSV)
   │   └── figures/           # Generated figures (PDF, PNG)
   ├── documents/             # Outside papers and PDFs (split with /split-pdf)
   ├── decks/                 # Beamer presentations (rhetoric of decks philosophy)
   ├── notes/                 # Scratch notes, ideas, miscellaneous
   └── progress_logs/         # Session logs for continuity across Claude conversations
   ```

   ## How This Project Is Organized

   **Two configuration files serve different purposes:**
   - `CLAUDE.md` contains permanent research rules — estimation philosophy, coding conventions, and instructions that apply across all sessions. It is copied from a master template at `~/mixtapetools/claude/CLAUDE.md` and edited as the project evolves.
   - `README.md` (this file) is project-specific documentation — what the project is about, who's involved, current status, and key decisions.

   **Session continuity:** The `progress_logs/` directory maintains a running record of work across Claude Code sessions. If a session is lost or a new conversation starts, the latest log provides context to resume seamlessly.

   **Documents and decks:** Outside papers go in `documents/` and can be split for safe reading using the `/split-pdf` skill. Presentations are built in `decks/` following the rhetoric of decks philosophy from `~/mixtapetools/presentations/rhetoric_of_decks.md`.

   ## Overview

   [To be filled in]

   ## Collaborators

   - Scott Cunningham

   ## Status

   Phase: Setup

   ## Key Files

   | Purpose | Location |
   |---------|----------|
   | Analysis code | `code/` |
   | Source data | `data/raw/` |
   | Results | `output/` |
   | Presentations | `decks/` |
   ````

6. **Create initial progress log**

   Create `progress_logs/YYYY-MM-DD_setup.md`:

   ```markdown
   # Progress Log

   ## [Today's Date] — Project Created

   Initial project setup. Directory structure created with `/newproject`.

   ### Next steps
   - [ ] Define research question in README.md
   - [ ] Update CLAUDE.md with project-specific details
   - [ ] Place raw data in data/raw/
   - [ ] Place reference papers in documents/
   ```

7. **Report success**
   - Show the created structure using `ls -la`
   - Remind user to update CLAUDE.md with project-specific details

## Example

```
User: /newproject texas-fertility-study

Claude: Created project structure at ./texas-fertility-study/

texas-fertility-study/
├── CLAUDE.md
├── README.md
├── code/
│   ├── R/
│   ├── python/
│   └── stata/
├── data/
│   ├── raw/
│   └── clean/
├── output/
│   ├── tables/
│   └── figures/
├── documents/
├── decks/
├── notes/
└── progress_logs/
    └── 2026-02-19_setup.md

Next steps:
1. Update CLAUDE.md with your research question and identification strategy
2. Add collaborator information to README.md
3. Place raw data files in data/raw/
4. Place reference papers in documents/
```
