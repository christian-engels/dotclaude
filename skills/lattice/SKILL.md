---
name: lattice
description: Run, ship to, and maintain the Lattice deployment — the public reading room at lattice.christianengels.net, served from the Intel Mac over Tailscale, and Pro mode on the M4. Use for "is lattice up", "start/stop lattice", "restart lattice", "deploy this change to lattice", "switch lattice back to the M4", "lattice is down", "Scopus tools are down", "coauthors cannot sign in", "back up lattice state", "refresh the corpus", or /lattice. Knows the live active/standby topology, the application plus read-only corpus-MCP sidecar, the cross-build route the Intel Mac requires because it cannot pull Docker images, the Cloudflare Access cookie failure that looks like a Cloudflare outage, and where the state actually lives.
allowed-tools: Bash(ssh*), Bash(docker*), Bash(rsync*), Bash(curl*), Bash(git*), Bash(shasum*), Bash(sqlite3*), Bash(uv*), Bash(python3*), Bash(nohup*), Bash(lsof*), Bash(ps*), Bash(kill*), Bash(cd*), Bash(ls*), Bash(cat*), Bash(grep*), Bash(sed*), Bash(tail*), Bash(rm*), Read, Write, Grep, Glob
argument-hint: [what to do — e.g. "status", "start pro mode", "deploy", "fail back to the M4", "back up the state"]
---

# Lattice operations

Lattice runs two ways at once: a **hosted** reading room behind Cloudflare Access for
Christian and his coauthors, and **Pro mode** on the M4 that reaches the Claude Code
subscription, the user skills and Chrome. Different hosts, different state, different
failure modes.

This is a **playbook, not a pipeline**. Establish the truth, pick the block, confirm
before you disturb anything anyone else is using.

Both halves are meant to be self-healing — Docker restarts the hosted stack, a
LaunchAgent restarts Pro mode, and the active host backs its state up nightly. So
"it is down" usually means something stopped it from coming back, not that nobody
started it. Look at the exit reason before starting anything by hand.

## Read first, always

**Run the status block before any action.** `references/runbook.md` block 1. It
answers the only three questions that matter: which host holds the tunnel, is Pro
mode up, what does the public hostname return.

`references/topology.md` records where things were on 2026-07-28. Treat it as a
starting hypothesis that the status block confirms or overturns — hosts get switched,
and a stale assumption here causes a split-brain.

The official read-only Scopus DuckDB MCP release is deployed at implementation and
runtime SHA `a23de94`. All 175 tests passed; local Pro Ask/AI Search and Christian's
authenticated hosted Ask/AI Search passed. The MCP readiness race and Linux
same-process initialization-lock race are fixed. Only multi-user/two-real-account
coauthor acceptance remains; do not describe the release or Christian's hosted worker
path as pending.

## Four invariants

1. **Exactly one `cloudflared` in existence, ever.** Both Macs share one named tunnel.
   Two connectors means Cloudflare balances users across two divergent copies of the
   state. Confirm the other host is down *before* starting `--profile public`.
2. **State has one writer.** Copy it only with both stacks stopped. A running
   container is a live SQLite writer.
3. **The corpus is read-only**, travels separately from the code, and is verified by
   SHA-256 on arrival. The hosted **agent** reaches it only through the isolated
   `corpus-mcp` sidecar; the application retains a separate read-only mount for the
   legacy reading-room routes, and Pro mode uses the matching persistent stdio
   server. Neither agent path permits mutation, external access, host-path disclosure
   or bulk reconstruction. It is never part of a state backup.
4. **`deploy/private/` has never been committed and must stay that way.** Check with
   `git ls-files deploy/private` — empty — before any push. Never print, echo, diff or
   paste the master key, tunnel token or Zotero secret.

## Confirm before you disturb

Run without asking: status, health checks, `state-inventory.py`, reading logs, `git
status`, architecture inspection.

Propose and get a yes first: anything that stops or starts the public stack, moves or
overwrites state, switches hosts, pushes to GitHub, or deletes images. Say what will
break and for how long — a host switch is a real outage for whoever is signed in.

## Task index

All blocks are in `references/runbook.md`.

| Ask | Block |
|---|---|
| "is lattice up", "what's running" | 1 — status |
| "pro mode is down", "restart pro mode" | 2 — the M4 LaunchAgent |
| "start/stop/restart the public site" | 3 — the public stack |
| "deploy this change", "ship it" | 4 — cross-build and ship both images to Intel |
| "switch hosts", "fail back to the M4" | 5 — switchover |
| "the corpus was rebuilt" | 6 — corpus refresh |
| "back it up", "how big is the state" | 7 — state |
| "reclaim disk" | 8 — prune |
| "cut a release" | 9 — the full gate battery |
| "Scopus tools are down", "verify read-only SQL" | 10 — Scopus MCP |
| "add a coauthor", "give X access" | `topology.md`, "Adding a coauthor" — two edits and a recreate |

`references/troubleshooting.md` covers failures that have actually happened, each
written tell-first. Check it **before** diagnosing from scratch — several present as
something they are not, and #1 in particular has already cost a night and a withdrawn
Cloudflare support case.

## Two decisions that need Christian, not a default

**Failing back to the M4 carries a state trade.** The M4's hosted state is frozen at
the 2026-07-27 switch and is stale from the first request the Intel Mac serves. Either
copy the live state back first, or accept older data. Ask which — before starting, not
during.

**Shipping images between hosts departs from the native-build default.** The rule
guards against architecture mismatch and stale virtualenvs; explicit
`--platform linux/amd64` builds satisfy both, and they are required because that Mac
cannot reach a registry at all. Build, ship and assert `.Architecture` for both
`lattice-private:local` and `lattice-corpus-mcp:local`; one without the other is not a
release.

## When this skill and the repo docs disagree

The runbook wins on **topology** — which host is active, what the paths are. The repo
docs win on **procedure** — `deploy/README.md` for compose and first-start setup,
`docs/OPERATIONS.md` for release checks and recovery, `deploy/POST_CUTOVER_CHECKLIST.md`
for acceptance. The `progress_logs/` are the record of what actually happened and why.

If you find drift, fix the docs in the lattice repo rather than working around them,
and note it in a progress log.
