# dotclaude

Personal Claude Code configuration: global instructions (`CLAUDE.md`), slash commands, four personal skills, and tracked symlinks that wire the shared skills in from the private [claude-plugins](https://github.com/christian-engels/claude-plugins) marketplace repo.

## Layout

- `CLAUDE.md` — user-scoped global instructions loaded every session. Opinionated for empirical finance/economics research; adapt before adopting.
- `commands/` — slash commands (`compiletex`, `new-session`).
- `skills/` — four personal skills as real directories (`lattice`, `create-quiz`, `newbook`, `voice-extractor`) plus 24 tracked symlinks into `~/claude-plugins/plugins/*/skills/*`.

## Machine bootstrap (mine)

Order matters — the skill symlinks point at `~/claude-plugins`, so clone that first:

```bash
git clone git@github.com:christian-engels/claude-plugins.git ~/claude-plugins
# then clone or pull this repo as ~/.claude
~/claude-plugins/install-local.sh   # links the Scopus corpus, lists missing .env files
```

## Sharing

Shared skills are distributed through the private claude-plugins marketplace, not by copying this repo — see its README for the coauthor install (`/plugin marketplace add christian-engels/claude-plugins`, then `/plugin install <bundle>@engels`).

## Provenance

`newbook` derives from [scunning1975/MixtapeTools](https://github.com/scunning1975/MixtapeTools). Skills in the marketplace bundles carry their provenance in their own `SKILL.md` files.
