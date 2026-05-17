# Claude Code: Skills and Commands

Personal collection of Claude Code skills and slash commands for empirical research in finance and economics.

## Install

Skills and slash commands are loaded by Claude Code from your user-scoped config directory:

| OS | Path |
|---|---|
| macOS / Linux | `~/.claude/` |
| Windows | `%USERPROFILE%\.claude\` (i.e. `C:\Users\<you>\.claude\`) |

Clone into that directory:

```bash
# macOS / Linux
git clone https://github.com/christian-engels/dotclaude.git ~/.claude-dotclaude
cp -R ~/.claude-dotclaude/skills/* ~/.claude/skills/
cp -R ~/.claude-dotclaude/commands/* ~/.claude/commands/
```

```powershell
# Windows (PowerShell)
git clone https://github.com/christian-engels/dotclaude.git "$env:USERPROFILE\.claude-dotclaude"
Copy-Item "$env:USERPROFILE\.claude-dotclaude\skills\*" "$env:USERPROFILE\.claude\skills\" -Recurse
Copy-Item "$env:USERPROFILE\.claude-dotclaude\commands\*" "$env:USERPROFILE\.claude\commands\" -Recurse
```

Or, if you don't already have a `~/.claude/` you want to keep, clone directly into it. Restart Claude Code so it picks up the new skills and commands.

## Skills

### My own

- [`ai-text-detect`](skills/ai-text-detect) — locate every LLM-cliché word in a .tex/.pdf/.txt with sentence context
- [`ai-text-metrics`](skills/ai-text-metrics) — readability and AI-style linguistic metrics for academic drafts
- [`ai-text-verify-refs`](skills/ai-text-verify-refs) — verify references via Web of Science → Scopus → OpenAlex cascade
- [`ai-text-writing`](skills/ai-text-writing) — draft academic prose in Cochrane/Jacobsen style, avoiding LLM markers

### From [scunning1975/MixtapeTools](https://github.com/scunning1975/MixtapeTools)

- [`beautiful_deck`](skills/beautiful_deck) — end-to-end Beamer deck creation
- [`bibcheck`](skills/bibcheck) — many-agent bibliography audit
- [`blindspot`](skills/blindspot) — peripheral vision audit for empirical output
- [`check-section-numbers`](skills/check-section-numbers) — verify prose matches referenced tables/figures
- [`compiledeck`](skills/compiledeck) — compile Beamer presentations
- [`newbook`](skills/newbook) — scaffold a new book project
- [`newproject`](skills/newproject) — scaffold a new research project
- [`referee2`](skills/referee2) — systematic audit by Referee 2 (deck or code mode)
- [`split-pdf`](skills/split-pdf) — read academic PDFs in chunks
- [`tikz`](skills/tikz) — visual-collision check for TikZ and rendered figures

### From [grandamenium/dream-skill](https://github.com/grandamenium/dream-skill)

- [`dream`](skills/dream) — memory consolidation; auto-triggers via a Stop hook every 24h

See each skill's `SKILL.md` for full usage notes.

## Commands

Slash commands live in [`commands/`](commands).

## Global instructions

[`CLAUDE.md`](CLAUDE.md) is the user-scoped instructions file Claude Code loads every session. The copy in this repo is tailored to empirical finance/economics research — folder conventions (replication-pack ↔ paper one-way flow), workflow rules (single source of truth for numbers vs. presentation, iteration discipline), behaviour rules (no guessing, always show full tables, report output paths), and version-control discipline (lab-book commits, squash-merge, no `Co-Authored-By` lines). Opinionated; adapt before adopting.

The install commands above do **not** copy `CLAUDE.md` to avoid overwriting your existing global instructions. Copy it manually if you want the whole thing, or open it and merge the parts that fit your workflow.
