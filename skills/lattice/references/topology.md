# Topology

Verified `2026-07-28`. This is a **starting hypothesis, not a fact** — the status
block in `runbook.md` is what establishes the truth on the day.

## The two halves

Lattice is one codebase run two ways.

| | Hosted (public) | Pro mode (local) |
|---|---|---|
| Who uses it | Christian + allowlisted coauthors | Christian only |
| Where | Intel Mac, in Docker | M4, native |
| Reached at | `https://lattice.christianengels.net` | `http://127.0.0.1:8766` |
| Auth | Cloudflare Access | none — loopback only |
| Claude | Anthropic API key, per tenant | the Claude Code subscription |
| Agent tools | managed Scopus + Lattice MCP only; no skills, subagents or shell | Scopus + Lattice MCP, skills, subagents, shell and configured MCP |
| State | `~/.lattice-next/hosted/state` on the Intel Mac | `~/.lattice-next` on the M4 |
| Tool approval | per call | **trusted by default** — tools just run |
| Where a run starts | a per-job directory in the container | **stated per chat, required** — except `ai-search`, below |
| Live output | streams through the public worker path; Ask and AI Search verified for Christian, coauthor acceptance pending | streams token by token; Ask and AI Search verified |
| Lifecycle | Docker `restart: unless-stopped` | LaunchAgent, `KeepAlive` |

Pro mode exists because local mode gets the whole toolbox. Hosted mode gets only two
managed MCP surfaces: `scopus` for full-schema, read-only DuckDB analysis and
`lattice` for controlled web-metadata, PDF, findings, working-paper and staged Zotero
actions. Pro mode receives those two plus the Claude Code set, including
`Agent`/`Task`, and Christian's other configured MCP servers. Hosted denies the
local-only names before any local configuration is considered, so widening Pro mode
cannot widen a coauthor's run.

Every Pro-mode chat must name a working directory before it can send —
`chats.cwd`, set through the control beside model and think, validated by
`POST /api/workspace/check`, and recorded per run in `jobs.cwd`. It was
`Path.cwd()`, which is wherever the LaunchAgent started, so runs and their
subagents began inside the Lattice repo. There is no default and home is not one.

**`ai-search` is the exception, and it is the kind that is not a chat.** The
Search tab's ✦ AI curation is fired by a search box: no chat, no directory
control, one run per search. Requiring one there refused every curation with
advice — "set one for the chat before sending" — that had no chat to set it on,
so from 2026-07-27 the kind is exempt at `_workspace_for`, `jobs.cwd` stays
NULL, and `worker._local_cwd` starts it in `state_dir/workers/<job_id>`, the
same shape hosted gives every run. It is also the one kind cut back to
the four Scopus MCP tools in **both** modes: it has no shell, application action or
filesystem to want, and a question it asked would reach a search box that cannot
answer it.

`local_trusted_bypass` defaults **on** in local mode (`config.py`) — that is what lets
the permanent service run unattended, it is loopback-only, and hosted mode rejects the
flag outright. `LATTICE_LOCAL_TRUSTED_BYPASS=0` in the plist restores approvals.

## Active — the Intel Mac

- `MCC02CV3EJMD6R`, x86_64, macOS. Reached over Tailscale as **`remote-mac-ts`**
  (`100.75.112.70`, user `ce50`). It has no Dropbox.
- Repo `~/lattice`, branch `feat/friendly-onboarding-v0.2.0`; deployed Scopus
  implementation and runtime SHA `a23de94`.
- Corpus `~/lattice-data/scopus.duckdb` (14 GB, read-only, transferred by rsync).
- The hosted corpus is served by the internal `corpus-mcp` container; only the
  Lattice application can reach it, on `http://corpus-mcp:8000/mcp`.
- The application and sidecar are healthy, and the direct sidecar MCP handshake
  and security checks passed on 2026-07-28.
- Christian's authenticated hosted Ask and AI Search acceptance passed after the MCP
  readiness and Linux same-process initialization-lock races were fixed.
- Hosted state `~/.lattice-next/hosted/state`.
- Secrets `~/lattice/deploy/private/` — copied out of band, `0600`.
- Homebrew is Intel-prefix: **`/usr/local/bin`**, not `/opt/homebrew/bin`.

**Every remote command needs this preamble.** Without it `docker` is not on PATH and
the CLI cannot find the daemon:

```sh
export PATH=/usr/local/bin:$PATH
export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
```

## Standby — the M4

- Repo `/Users/ce50/lattice` — moved out of Dropbox on 2026-07-27, because a file
  provider made the suite hang for 14+ minutes and stopped launchd spawning the
  service at all. `~/Documents` is TCC-protected and will not work for an agent.
- Corpus `~/lattice-data/scopus.duckdb`, same path as the Intel Mac — it followed
  the repo out of Dropbox once disk was freed. SHA-256
  `3f75edea972caf937de8ff66c9bb578c001f514a4248707e8220f9b1abf0a8f9`.
  The old `scopus-db/data/scopus.duckdb` is now a **symlink** to it, carrying
  `com.dropbox.ignored=1`, kept only for the legacy 8765 app which reads that path
  through relative paths in its own source. Everything else was repointed at the
  real file — see below.
- Hosted state `~/.lattice-next/hosted/state` — **frozen at the moment of the
  2026-07-27 switch**, and stale from the first request the Intel Mac served.
- Secrets `deploy/private/` — present, gitignored, never committed.
- Runs Pro mode permanently as the LaunchAgent `com.ce50.lattice-pro`. Runs no
  containers.
- Holds `~/.lattice-backup-identity.txt` — the **only** copy of the key that
  decrypts the active host's state backups. `0600`, never copied anywhere.

## Who reads the corpus

Moving it means updating all of these. As of `2026-07-28` every one points at
`~/lattice-data/scopus.duckdb` directly, except the last:

| Consumer | How it resolves |
|---|---|
| Lattice Pro mode | launches the locked `mcp-server-motherduck` executable beside the Lattice interpreter as a persistent read-only stdio server named `scopus`; `LATTICE_CORPUS_PATH` in the plist selects the file |
| Lattice hosted reading room (Intel) | `LATTICE_CORPUS_FILE` mounts into the application at `/data/scopus.duckdb:ro` for the legacy HTTP routes |
| Lattice hosted agent (Intel) | the same immutable file also mounts into `corpus-mcp`; Lattice reaches `LATTICE_SCOPUS_MCP_URL=http://corpus-mcp:8000/mcp` |
| `search-literature`, `top-finance-bar-audit`, `scopus-novelty-scan`, `novelty-scan` | a `scopus.duckdb` symlink inside each skill folder — five across four bundles, Claude and Codex |
| standalone `duckdb` MCP outside Lattice | `--db-path` in `scopus-db/.mcp.json`; Lattice does not consume this configuration |
| legacy 8765 app | relative `data/scopus.duckdb` in its own source — **the one thing still using the compatibility symlink** |

`claude-research-discovery-skills/install.sh` recreates the skill symlink, so its
default matters: it prefers `~/lattice-data`, falls back to the old sibling-repo path,
and honours `SCOPUS_DB_PATH`. Check a link by opening it, not by reading it —
`duckdb.connect(path, read_only=True)` and count rows. The corpus has **1,160,915**
rows in `articles`.

## Scheduled services

| Agent | Host | What |
|---|---|---|
| `com.ce50.lattice-pro` | M4 | Pro mode on 8766, `RunAtLoad` + `KeepAlive`; log `~/Library/Logs/lattice-pro.log` |
| `com.ce50.lattice-backup` | Intel (active) | `backup-state.sh` daily 03:15, keeps 30 in `~/.lattice-backups`; log `~/Library/Logs/lattice-backup.log` |
| `com.ce50.docker-desktop` | Intel (active) | `open -a Docker` at login, `RunAtLoad`, no `KeepAlive`; log `~/Library/Logs/docker-desktop-autostart.log` |

All three are versioned at `deploy/launchd/` in the lattice repo. They are user agents,
not daemons, because all need the login session.

**`restart: unless-stopped` is enforced by the daemon, so it does nothing when the
daemon is absent.** That is what made the 2026-07-28 reboot a silent hour-long outage:
Docker Desktop did not start, so nothing was there to restart the containers. The
Docker agent closes the gap but cannot close all of it — Docker Desktop asks for an
administrator password through a **GUI dialog** when its privileged helper needs
configuring, and launchd cannot answer that. See `troubleshooting.md`.

## Public endpoint

- `https://lattice.christianengels.net` — an unauthenticated **401 proves only that
  Cloudflare Access is in front of the hostname. It says nothing about the origin.**
  Access refuses the anonymous request at the edge, before proxying anywhere, so the
  401 is identical whether the stack behind it is healthy or entirely absent. On
  2026-07-28 this returned 401 for over an hour while the Intel Mac had no Docker
  daemon, no containers and no `cloudflared` at all.

  **The honest origin check is `docker compose ps` on the active host**, or whether a
  `cloudflared` process exists anywhere. A 000 still means the hostname itself is
  unreachable, and a 502/530 still means the origin is down — but only a
  *post-authentication* request can produce those, so an anonymous curl will never
  show you either.
- Team domain `lattice-christianengels.cloudflareaccess.com`
- Application `85fa6216-b2db-4459-a7ad-5aeb3f302a38`
- AUD `661a5b2a4751f473621c4e9bda49d9ba2ba5b865db692d7b26496e5a737ef034`
- Account `218d8c81fcb228bdd50789cf7863968c`
- One-time-PIN IdP `f99d4ad2-922e-4af2-b171-9c5478386ede`
- Parked replacement application `663e0061-5ff2-4ce6-bffe-55273d1c38e0` — retained
  deliberately; do not delete it while the callback incident is open.
- Reusable policy `Lattice approved users`,
  `ae87f28d-5a54-4baa-ab71-10354f4ad284` — an `Emails` include rule listing each
  address exactly, `AND` a `Login Methods` require rule of One-time PIN. Both
  applications share it, so one edit covers both.

**Adding a coauthor is two edits and a recreate**, and either edit alone fails
closed. Put the address in the reusable policy *and* in `LATTICE_ALLOWED_EMAILS`
on **both** hosts, then recreate the application container. Cloudflare alone
yields a valid JWT and a `403 email is not allowlisted` from `auth.py`, raised
before `resolve_tenant`, so no tenant row appears; Lattice alone never sees the
request. The allowlist is read once at process start, so `docker compose restart`
does nothing — only `up -d` recreates with the new environment, and it leaves
`cloudflared` and `corpus-mcp` up, so the tunnel does not drop. Check the state
database for queued or running jobs first. Nothing else is needed: the tenant,
its state directory and its onboarding row are created on first request, and
there is no add-user script. The new account must supply its own Anthropic key —
hosted mode refuses a process-global one.

The Zero Trust dashboard **moved in 2026**. `one.dash.cloudflare.com/<account>/
access/apps/edit/<app>` now 404s; the live path is
`dash.cloudflare.com/<account>/one/access-controls/` with `apps` and `policies`
beneath it.

Both Macs share **one** named tunnel, one URL, one Access application and one
audience. Switching hosts therefore needs no DNS or Cloudflare change at all.

## Code bridge

Private repo `github.com/christian-engels/lattice`, created 2026-07-27 because the
Intel Mac has no Dropbox. `main` and `feat/friendly-onboarding-v0.2.0` are level.
**Verify a push against `git ls-remote`, not the exit code** — `git push origin main`
while another branch is checked out pushes the *local* `main` ref and reports
success without sending the commit you just made.

Nothing under `deploy/private/` has ever been committed. The only token-shaped file in
git is `tests/fixtures/cloudflared_token`, containing the literal string
`not-a-real-cloudflare-token`.

## Configuration

`deploy/private/production.env` (gitignored, both hosts) carries:

```
LATTICE_CF_ISSUER  LATTICE_CF_AUDIENCE  LATTICE_ALLOWED_EMAILS
LATTICE_CORPUS_FILE  LATTICE_STATE_DIR  LATTICE_PUBLIC_URL
LATTICE_MASTER_KEY_FILE  CLOUDFLARED_TOKEN_FILE
LATTICE_ZOTERO_CONSUMER_KEY  LATTICE_ZOTERO_CONSUMER_SECRET_FILE
```

The two hosts differ in **`LATTICE_CORPUS_FILE` only**. Issuer, audience, allowlist,
master key and tunnel token are identical by design — that is what makes the hosts
interchangeable.

Compose, not `production.env`, fixes
`LATTICE_SCOPUS_MCP_URL=http://corpus-mcp:8000/mcp`; it is internal topology, not an
operator-selectable destination.

Secret files alongside it: `lattice_master_key`, `cloudflared_token`,
`zotero_consumer_secret`. Never print, echo, diff or copy these into a chat.

## Ports

| Port | What |
|---|---|
| 8766 | Lattice — Pro mode on the M4, and the container's internal port |
| 8765 | the **legacy** scopus-db app (`python app/server.py`) — a different program |
| 8000 | `corpus-mcp` HTTP transport inside `lattice-corpus` only; never published |

Neither hosted application service publishes a host port. `cloudflared` shares
`lattice-edge` only with Lattice; `corpus-mcp` shares `lattice-corpus` only with
Lattice and cannot see the edge.

## Scopus MCP boundary

All allowlisted hosted users and local Pro can discover every schema, table, view and
column and issue analytical queries. Both use `mcp-server-motherduck==1.0.7` with
DuckDB 1.5.3. The visible tools are
`mcp__scopus__list_databases`, `mcp__scopus__list_tables`,
`mcp__scopus__list_columns` and `mcp__scopus__execute_query`. Each query is limited
to 10,000 rows, 500,000 output characters and 120 seconds; hosted runs additionally
stop at 5,000,000 cumulative Scopus-output characters.

Hosted accepts only parsed `SELECT` and `EXPLAIN`. It rejects DDL, DML, `SET`, `COPY`,
`ATTACH`, `CALL`, `INSTALL`, `LOAD`, external file/URL access and database switching,
and redacts the host corpus path. The sidecar has no Lattice source, state, secrets or
credentials, publishes no port, runs UID/GID 10002 with read-only root, 2 CPUs, 4 GB
memory and a 1 GiB no-exec tmpfs, and sees only `/data/scopus.duckdb:ro`. Lattice
serializes hosted calls with a process-safe lock. Pro mode uses the same query limits
over stdio but has no per-run cumulative cap.

## Scopus rollout status

The official read-only Scopus DuckDB MCP release is deployed, not pending. On the M4,
all 175 tests and source-integrity checks passed, the application and sidecar images
built for ARM64 and AMD64, Pro mode restarted, and real local Ask and AI Search
smokes queried Scopus successfully. On the active Intel host, implementation and
runtime SHA `a23de94` is running with healthy application and sidecar containers; the
direct HTTP MCP handshake and sidecar security checks passed.

The worker now waits for every injected MCP server before submitting the first
prompt, fixing the readiness race, and same-process Scopus calls serialize before
DuckDB initialization on Linux. Christian's authenticated hosted Ask exposed all four
Scopus tools, including successful table discovery and SQL reporting 1,160,915
articles with latest year 2026; hosted AI Search completed and curated 12 papers.
Only multi-user/two-real-account coauthor acceptance remains pending.

## Where the written record lives

In the lattice repo:

- `deploy/README.md` — compose invocations, the `public` profile, first-start setup
- `docs/OPERATIONS.md` — release checks, cutover order, recovery modes
- `docs/ARCHITECTURE.md` — trust boundaries
- `deploy/POST_CUTOVER_CHECKLIST.md` — the acceptance gate
- `progress_logs/2026-07-27-read-only-scopus-mcp.md` — implementation and rollout
  status
- `progress_logs/2026-07-27-public-lattice-moves-to-the-intel-mac.md` — the move
- `progress_logs/2026-07-27-cloudflare-access-callback-incident.md` — the cookie bug

## How a run reaches the screen

The worker sends events over its pipe as it produces them; `JobManager` buffers
them per job in memory; `GET /api/jobs/{id}/stream?cursor=N` serves them as
NDJSON, each line carrying its own index. The client renders them and, on a
dropped connection or a page reload, reattaches at the index it stopped on.

The stream is **decoration**. `waitForChatJob` still owns the job's lifecycle,
so if the stream 404s, stalls or is buffered by a proxy the Ask tab behaves as
it did before it existed — a spinner, then the answer. That is the intended
failure mode, not a bug to chase.

Three consequences worth knowing:

- **Subagent output never enters the answer.** Deltas carrying
  `parent_tool_use_id` surface as activity under the chip of the Agent call
  that spawned them. If a fan-out's prose ever appears inline, that routing has
  broken.
- **The buffer is ephemeral.** It holds the last 8 finished jobs for 10
  minutes, capped at 20,000 events / 8 MB per run, and says `trunc` if it hits
  either. Reopening a chat from the database still shows prose only; thinking
  and tool chips live in the browser's own workspace state.
- **`Cache-Control` on that route is deliberate.** The security middleware sets
  `no-store` on everything else but must not overwrite the stream's
  `no-store, no-transform` — without `no-transform` a proxy may coalesce it,
  which shows up only in production, through the tunnel.

## Questions a run can ask

`AskUserQuestion` reaches `can_use_tool` even under `bypassPermissions` — an
explicit exception, and the only reason the feature works in Pro mode at all.
The answer goes back as
`PermissionResultAllow(updated_input={"questions": …, "answers": …})`, keyed by
question text.

The question is parked on `jobs.question_request` as well as being emitted to
the stream, so it survives a reload and still arrives when the stream does not.
Hosted may answer its own questions — unlike tool approvals that is not a
privilege — but its `PreToolUse` hook must return **no decision** for the tool:
an `allow` decision satisfies the permission check and skips `can_use_tool`,
swallowing the question silently. Hosted waits 15 minutes then continues
without an answer, because a coauthor who closes the tab would otherwise hold
one of only two global worker slots.
