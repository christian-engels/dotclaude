# Troubleshooting

Every entry here cost real time at least once. Read the **tell** first — most of these
present as something else entirely.

---

## 1. "Unable to find your Access organization!" — a 404 after a successful sign-in

**Tell.** Cloudflare's Access log records the decision as **Allowed**, the browser
lands on `/cdn-cgi/access/authorized`, and shows HTTP 404 with that message. No
one-time PIN is ever requested. It survives creating a replacement application with a
new ID and AUD, and reproduces from Cloudflare's own App Launcher.

**Cause.** A stuck `CF_AppSession` cookie on `lattice.christianengels.net`, in one
browser profile. Not a Cloudflare defect and not a configuration error. Cloudflare
mints a new `CF_AppSession` only when the browser presents none, so the bad state is
self-sustaining — and neither logout endpoint clears it (the team-domain logout is
scoped to the wrong host; the application-host logout returns the organization error
itself).

**Fix.** Clear site data for `lattice.christianengels.net`, then sign in again. A
private window or a fresh profile also works. The cookie is `HttpOnly`, so nothing
else can remove it.

**One-call triage.** Same host, same path, the only difference being cookies:

```sh
curl -sS --max-time 20 https://lattice.christianengels.net/cdn-cgi/access/logout
```

A healthy `200 "No Access cookie found. Please login first."` here, while the browser
404s, proves the cookie is at fault and no configuration change is needed.

**Do not** start changing Access applications, policies or identity providers on this
symptom. That was tried; it changed nothing, because the poison is in the browser.

Full write-up: `progress_logs/2026-07-27-cloudflare-access-callback-incident.md`.

---

## 2. The Intel Mac cannot pull Docker images over SSH — at all

**Tell.** `docker pull` or `docker compose build` fails with `error getting
credentials` / `the current session does not allow user interaction`.

**Cause.** Docker Desktop's credential service needs the login keychain, which a
non-interactive SSH session cannot unlock. This is **not fixable from the client
side.** All of these were tried and failed identically:

- an isolated `DOCKER_CONFIG` with `{}`;
- an explicitly empty `credsStore`;
- unlocking the login keychain from a console Terminal on that machine
  (`security unlock-keychain`) — macOS security sessions are separate.

**Fix.** Do not retry any of the above. Cross-build the Lattice and corpus-MCP images
on the M4 and ship them together as a tarball — `runbook.md` block 4. The Intel Mac
then never contacts a registry.

---

## 3. `docker pull --platform linux/amd64` is a silent no-op

**Tell.** It cheerfully reports "Image is up to date" and you end up with an arm64
image on an Intel machine — which only fails much later, at run time.

**Cause.** When the tag already exists locally at *any* architecture, the platform
flag does not force a re-fetch.

**Fix.** Resolve the platform-specific digest and pull that instead, then assert:

```sh
docker buildx imagetools inspect python:3.12-slim | grep -B2 'linux/amd64'
docker pull --platform linux/amd64 "python@sha256:<digest>"
docker image inspect python:3.12-slim --format '{{.Architecture}}'
```

**Never ship an image without checking `.Architecture` first.** It is one command and
it is the difference between a deployment and a broken deployment.

---

## 4. Loading an image into the daemon does not satisfy BuildKit

**Tell.** `python:3.12-slim` is present in `docker images`, and the build still fails
trying to resolve it from the registry.

**Cause.** BuildKit re-resolves base tags against the registry regardless. Switching
builders does not help — both builders already use the docker driver.

**Fix.** Do not fight it. Build the whole image where the registry is reachable (the
M4), with `--platform linux/amd64 --load`, and ship the finished image.

---

## 5. Overriding `DOCKER_CONFIG` makes `docker compose` disappear

**Tell.** `docker: 'compose' is not a docker command`.

**Cause.** `DOCKER_CONFIG` relocates where the CLI looks for `cli-plugins`, not just
credentials.

**Fix.** Symlink them back, or drop the override entirely (it does not help anyway —
see #2):

```sh
ln -sfn /Users/ce50/.docker/cli-plugins /tmp/lattice-dockercfg/cli-plugins
```

---

## 6. Pro mode is not running

**Tell.** `curl 127.0.0.1:8766/healthz` refuses the connection.

**Cause.** Since `2026-07-27` a LaunchAgent keeps it up, so this now means the agent
is unloaded, or it is crash-looping. The most common reason for the latter is a
`.venv` that no longer matches the code after a pull.

**Fix.** Diagnose in this order:

```sh
launchctl print gui/$(id -u)/com.ce50.lattice-pro | grep -E 'state =|last exit code'
tail -20 ~/Library/Logs/lattice-pro.log
cd "$M4REPO" && uv sync --all-groups && launchctl kickstart -k gui/$(id -u)/com.ce50.lattice-pro
```

If the agent is absent entirely, `bootstrap` it from
`~/Library/LaunchAgents/com.ce50.lattice-pro.plist` — `runbook.md` block 2.

**Two spawn failures worth recognising**, both from 2026-07-27:

- `last exit code = 78: EX_CONFIG` — launchd could not spawn the executable at all.
  Not a config typo: the binary was momentarily *unreadable*, which is what a cloud
  file provider does under load. This is why the repo left Dropbox.
- `PermissionError: [Errno 1] Operation not permitted: …/.venv/pyvenv.cfg` — the repo
  is somewhere TCC-protected (`~/Documents`, `~/Desktop`, `~/Downloads`). The file is
  readable from your terminal and not from the agent; that asymmetry is the tell.
  Move it somewhere unprotected rather than granting Full Disk Access, which binds to
  a binary `uv sync` will replace.

**Related, and worth knowing:** local mode sets `local_trusted_bypass` **on** by
default (`config.py`), so the permanently-running service executes tools without
per-call approval. That is the design — it is one trusted Mac on the Claude Code
subscription, on loopback only, and hosted mode rejects the flag outright. Set
`LATTICE_LOCAL_TRUSTED_BYPASS=0` in the plist to get approval prompts back.

---

## 7. Split-brain: two tunnels, or two writable states

**Tell.** Coauthors see different data, or changes vanish between refreshes.

**Cause.** Both Macs share one named tunnel. If both run `cloudflared`, Cloudflare
balances across two origins with **divergent local state** — chats, integrations,
jobs, uploads and reports all live in the host's own SQLite.

**Fix.** Prevention is the whole answer. Run the status block before starting anything
with `--profile public`, and take the old host down *before* bringing the new one up.
If it has already happened, stop both, decide which state is authoritative, copy it,
and start exactly one.

---

## 8. macOS rsync flag failures

**Tell.** `rsync: --info=progress2: unknown option`, and the transfer never starts.

**Cause.** macOS ships rsync 2.6.9 (2006). `--info`, `--append-verify` and several
other modern flags do not exist.

**Fix.** Use `-a --partial --progress`. For the 14 GB corpus run it in the background
and poll the far side with `ls -lh`.

---

## 9. A fresh SQLite snapshot will not open read-only

**Tell.** `sqlite3 -readonly <fresh backup>` returns `Error: in prepare, unable to
open database file (14)` — which reads as "the file is missing" when the file is
plainly there.

**Cause.** The snapshot inherits `journal_mode=wal`, and opening a WAL database
read-only requires an existing `-shm` sidecar, which a fresh `.backup` has not
created. Any earlier read-write open masks this, so it is easy to "verify" the wrong
thing.

**Fix.** Check the snapshot read-write — you own the temp copy — and convert it while
you are there, which also makes the archived file self-contained:

```sh
sqlite3 "$snapshot" 'PRAGMA journal_mode=delete; PRAGMA integrity_check;' | tail -1
```

`scripts/backup-state.sh` already does this.

---

## 10. An Ask answer stops mid-search and looks complete

**Tell.** The reply ends early — often mid-way through a search — and the job is
recorded as `succeeded`, so nothing flags it as truncated. Check
`jobs.cost_usd` against `jobs.budget_usd`: at or above is the tell.

**Cause — but only in hosted mode, since `2026-07-27`.** Four profiles in
`config.JOB_PROFILES` bound every job on three axes. Defaults are what a run gets;
ceilings are how far the Ask tab's controls let a user raise it:

| Kind | Turns (default → ceiling) | Time | Budget (default → ceiling) |
|---|---|---|---|
| `chat` — the Ask tab | 20 → 400 | 10 min → 2 h | $1.50 → $25 |
| `zotero` | 20 → 400 | 10 min → 2 h | $1.50 → $25 |
| `search-literature` | 80 → 800 | 45 min → 4 h | $5.00 → $50 |
| `ai-search` | 8 → 200 | 5 min → 1 h | $0.50 → $10 |

**Pro mode has none of these.** Turns and budget are stored as `UNLIMITED` (0) and
reach the SDK as `None`; only a six-hour wall clock remains, to reclaim a worker
that wedges. So a local run stopping early is a genuine failure or the six hours,
never a cap.

**In hosted mode**, raise it in the UI — three selects beside `model` and `think`
at the top of the composer. A request above a ceiling is a 400 naming the limit.
This is separate from Scopus MCP output limits. If a tool call—not the whole answer—
reports 10,000 rows, 500,000 characters, 120 seconds or the hosted
5,000,000-character cumulative cap, see #15; raising the job budget cannot change it.

```sh
sqlite3 -readonly <state>/lattice.sqlite3 \
  "SELECT kind,status,budget_usd,cost_usd,max_rounds,timeout_seconds FROM jobs
   ORDER BY created_at DESC LIMIT 5"
```

---

## 11. Onboarding: "cannot pick a library", LibKey errors

**Tell.** The Zotero step connects but the library list is not selectable; the LibKey
step accepts `490` and errors; a valid entry gives no sense that it was accepted.

**Cause.** These were UI defects in the setup flow, fixed on
`feat/friendly-onboarding-v0.2.0` (2026-07-27) along with clearer per-step
confirmation. If they reappear, the deployed image is older than the branch.

**Fix.** Check what the running container actually is before debugging the
integration:

```sh
ssh -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  cd ~/lattice && git log --oneline -1
  docker image inspect lattice-private:local --format "{{.Created}} {{.Architecture}}"
'
```

The St Andrews LibKey library id is **490**.

## 12. ✦ AI in the Search tab asks for a working directory

**Tell.** Toasting `AI curation failed: this run needs a working directory — set
one for the chat before sending`, in Pro mode, from a tab that has no chat and
no directory control. Empty chats titled "Curate the strongest corpus results
for this search: …" accumulate in the Ask tab, one per attempt.

**Cause.** Not a directory problem. The requirement introduced by `566bfbb` was
enforced at `JobManager.enqueue`, which every kind passes through, and verified
through the Ask tab — the one caller that can comply. `aiCurate` posts
`kind:'ai-search'` with no `chat_id` and no `cwd`, so it was refused every time
the feature had ever been used. The chats are the second half of it: `create_job`
created one *before* `enqueue` validated, and did not take it back.

**Fixed 2026-07-27**, so this is a description of a shape rather than a live
problem: `ai-search` is exempt at `_workspace_for` and starts in
`state_dir/workers/<job_id>`. The pattern is worth recognising, though — a rule
correct for the caller it was designed around, applied at a choke point that
catches one that cannot satisfy it. The tell is advice that names a control the
failing screen does not have.

**Check it works** without touching the running service — start a second
instance on its own port and state directory, which shares the read-only corpus:

```sh
LATTICE_PORT=8790 LATTICE_STATE_DIR=/tmp/lat-verify \
LATTICE_CORPUS_PATH=~/lattice-data/scopus.duckdb ~/lattice/.venv/bin/lattice
```

A curation should return 202 with `"cwd": null`, leave `workers/<job_id>` empty,
and stay out of `GET /api/chats` while remaining readable at
`GET /api/chats/<id>`. Note `/api/search` and `/api/papers` are **GET** — POST
returns "Method Not Allowed", which reads like a broken corpus if you are
checking in a hurry.

---

## 13. A skill's helper prints nothing and exits 0

**Symptom.** A skill loads, `SKILL.md` is read, and then its helper script
produces no output at all — not even for `--help` — while exiting successfully.
Reading the file directly gives `OSError: [Errno 11] Resource deadlock avoided`.
Reported as "the `/zotero` skill doesn't work in Pro mode" on 2026-07-27.

**Cause.** Not the skill and not Lattice. The file was a **Dropbox online-only
placeholder** — macOS flags `compressed,dataless` — and with Dropbox stopped
nothing could hydrate it, so every read returned `EDEADLK`. It is the same file
provider failure that drove Lattice and the corpus out of Dropbox.

**Check** before suspecting the code:

```sh
ls -lO ~/.claude/skills/<skill>/references/<helper>.py   # look for 'dataless'
find <repo> -type f -flags +dataless | wc -l
```

**Fix (done 2026-07-27).** All **eight** skill bundles left Dropbox — the four
`claude-*` ones and the four `codex-*` mirrors — and now live at `~/claude-*`
and `~/codex-*`, each with a private GitHub remote under `christian-engels`.
The 20 symlinks in `~/.claude/skills` and the 20 in `~/.codex/skills` were
repointed. Nothing in Lattice changed. If a helper ever behaves this way again,
the repo is back inside a file provider, or something else is: hydrate with
`find <repo> -type f -exec cat {} + >/dev/null` and check the flags again.

The `claude-*` originals were deleted from Dropbox; the `codex-*` originals were
**kept**, so those four now exist twice and will drift.

The `.env` files in `zotero` and `top-finance-bar-audit` are gitignored, so they
travelled with the copy but were never pushed. A fresh clone of these repos on
another machine has no keys until those are placed by hand.

---

## 14. Ask cannot see Scopus, or every Scopus call fails

**Tell.** Tool discovery has no `Scopus · …` actions, or a call fails before DuckDB
returns a query error. In hosted mode `lattice` may still be healthy because the
public edge reaches the application, not the private corpus sidecar.

**Hosted diagnosis — read-only first:**

```sh
docker compose $ENVF ps corpus-mcp lattice
docker compose $ENVF logs --tail=40 corpus-mcp
docker inspect "$(docker compose $ENVF ps -q corpus-mcp)" \
  --format 'health={{.State.Health.Status}} ports={{json .NetworkSettings.Ports}}'
```

The expected shape is a healthy `corpus-mcp`, no published port and an internal URL
of `http://corpus-mcp:8000/mcp`. A missing sidecar image after a deploy usually means
only `lattice-private:local` was shipped; block 4 always transfers and tags both
images. Get confirmation before restarting the public pair.

**A healthy sidecar is not the whole path.** On 2026-07-28, Intel's application and
sidecar were healthy and a direct MCP handshake/security check passed, while the
first authenticated hosted worker smoke still exposed an MCP readiness race: the
first prompt could be submitted while remote Scopus was still `pending`, fixing that
turn's tool surface too early. Linux also needed an in-process lock because a file
lock alone did not serialize sibling Scopus calls in one worker during DuckDB
initialization.

Both races are fixed in implementation and runtime SHA `a23de94`: the worker waits
for every injected MCP server before the first prompt and serializes same-process
Scopus calls. Christian's authenticated hosted Ask exposed all four tools and hosted
AI Search completed successfully. If the same symptom returns at `a23de94` or later,
capture MCP status plus application/worker logs before restarting. Multi-user/
two-real-account coauthor acceptance remains open, but Christian's hosted worker path
is accepted.

**Pro diagnosis:**

```sh
launchctl print gui/$(id -u)/com.ce50.lattice-pro | grep -E 'state =|last exit code'
tail -40 ~/Library/Logs/lattice-pro.log
ps ax -o pid=,command= | grep '[m]cp-server-motherduck'
```

Pro launches the executable from Lattice's `.venv`, not `uvx`. After a dependency or
DuckDB change, `uv sync --all-groups`, ensure the managed DuckDB home has the matching
FTS extension, then restart the LaunchAgent. Do not enable run-time extension
installation as a shortcut.

---

## 15. A Scopus query is rejected, truncated or stops after repeated calls

**Tell.** The Scopus tool reports one of four limits: 10,000 rows, 500,000 output
characters, 120 seconds for one query, or 5,000,000 cumulative output characters for
one hosted run. The last limit does not apply in Pro mode.

**Cause.** This is the deliberate analytical boundary, not an Anthropic budget or a
broken database. It prevents an allowlisted account from reconstructing the licensed
corpus through repeated tool output. Hosted also accepts only parsed `SELECT` and
`EXPLAIN`; writes, `SET`, `COPY`, `ATTACH`, `CALL`, extension loading, file/URL reads
and database switching are rejected before DuckDB runs them.

**Fix.** Make the query do more work: aggregate, rank and filter in SQL; select only
the columns needed for the answer; split independent analyses across deliberate runs
only when that serves the research question. Never raise a limit, expose the sidecar
port, reveal its database path or turn the Ask interface into an export route.

---

## 16. Hosted Lattice is down after a reboot, and the hostname still says 401

**Tell.** Nobody can reach the reading room, but
`curl https://lattice.christianengels.net/healthz` returns **401** — the code the
status block used to call healthy. On the active host, `docker ps` answers
`Cannot connect to the Docker daemon`, and `~/.docker/run/docker.sock` exists but is
dated days earlier.

**Cause, part one — the 401 is not evidence.** Cloudflare Access refuses an anonymous
request at the edge, before proxying, so it answers identically when nothing at all is
running behind it. Only an authenticated request can produce the 502/530 that would
reveal a dead origin. Never conclude the service is up from an anonymous curl.

**Cause, part two — nothing started Docker.** The containers carry
`restart: unless-stopped`, which reads as self-healing but is enforced *by the daemon*.
No daemon, no restarts. Docker Desktop had no LaunchAgent on the Intel Mac, so a
reboot left the stack down indefinitely with no signal. Fixed by
`com.ce50.docker-desktop` in `deploy/launchd/`.

**Cause, part three — `open -a Docker` can hang forever.** Docker Desktop configures a
privileged helper through a **GUI dialog**, "Docker Desktop requires privileged access
to configure privileged port mapping", running
`config --user ce50 set-vmnetd set-docker-socket`. Until someone types an admin
password on that machine's screen, the daemon never appears. The tell is an
`osascript` process whose command line contains `docker-desktop-privileged`, with a
large `etime`:

```sh
ps -o pid,etime,command= -p "$(pgrep -f docker-desktop-privileged | head -1)"
```

That is also what leaves the stale socket: `set-docker-socket` never completed.

**Fix.** Approve the dialog on the console or over Screen Sharing — it cannot be
answered remotely, and it must not be answered by an agent. Then bring the stack up
with block 3. If the dialog was dismissed, quit Docker Desktop and reopen it to raise
it again.

**Diagnose in this order**, because the first two answers are cheap and the hostname
is worthless here:

```sh
docker info                 # daemon alive at all?
pgrep -f docker-desktop-privileged   # blocked on the password dialog?
docker compose ... ps       # containers, and which ones
```
