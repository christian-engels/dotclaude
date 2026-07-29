# Runbook

The active/standby blocks below were exercised on `2026-07-27`. The official
read-only Scopus DuckDB MCP release is live at implementation and runtime SHA
`a23de94`: all 175 tests passed, local Pro passed Ask and AI Search, and Christian's
authenticated hosted Ask and AI Search passed. The MCP readiness race and Linux
same-process initialization-lock race are fixed. Only multi-user/two-real-account
coauthor acceptance remains. Two shorthands used throughout:

```sh
M4REPO=/Users/ce50/lattice
ENVF="--env-file deploy/private/production.env"
```

and on the far side, always:

```sh
ssh -o ConnectTimeout=15 -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  ...
'
```

---

## 1. Status — run this before anything else

```sh
M4REPO=/Users/ce50/lattice

echo "=== M4 containers (expect none) ==="
docker ps --format '  {{.Names}}  {{.Status}}'

echo "=== M4 Pro mode ==="
curl -sS -o /dev/null -w '  127.0.0.1:8766/healthz -> %{http_code}\n' --max-time 8 \
  http://127.0.0.1:8766/healthz 2>/dev/null || echo '  not running'

echo "=== Intel Mac ==="
ssh -o ConnectTimeout=15 -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  cd ~/lattice
  printf "  repo SHA: "; git rev-parse --short HEAD
  # The daemon first. Everything below is meaningless without it, and after a
  # reboot it is the thing most likely to be missing.
  docker info --format "  daemon {{.ServerVersion}}, {{.ContainersRunning}} running" \
    2>&1 | head -2
  docker compose --env-file deploy/private/production.env ps 2>&1 | tail -5
'

echo "=== public hostname — NOT an origin check, see below ==="
curl -sS -o /dev/null -w '  lattice.christianengels.net/healthz -> %{http_code}\n' \
  --max-time 20 https://lattice.christianengels.net/healthz
```

Read it as: **exactly one host may show a `cloudflared` container.** Two is a
split-brain and must be resolved before anything else. Zero means the service is down.

> **The public hostname does not tell you whether Lattice is up.** An anonymous
> request is refused by Cloudflare Access at the edge, before it is proxied anywhere,
> so **401 is returned identically whether the origin is healthy or completely
> absent**. On 2026-07-28 it read 401 for over an hour while the Intel Mac had no
> Docker daemon, no containers and no `cloudflared` process at all. This block used to
> label that line "401 = healthy"; it was a false green on the first check anyone runs.
>
> The container lines above are the origin check. If the daemon line fails, the
> service is down no matter what the hostname says — go to `troubleshooting.md` #16.

Deeper check on the public side — that Access is fronting the right application:

```sh
curl -sS --max-time 20 \
  https://lattice.christianengels.net/.well-known/cloudflare-access-protected-resource \
  | python3 -c 'import sys,json;print("  team_domain:",json.load(sys.stdin).get("team_domain"))'
```

---

## 2. Pro mode on the M4

Since `2026-07-27` this is a **LaunchAgent** — `com.ce50.lattice-pro`, installed at
`~/Library/LaunchAgents/` and versioned at `deploy/launchd/` in the lattice repo. It
starts at login and restarts within ~15 s of any exit, so the normal answer to "is Pro
mode running" is yes. Do not start it by hand; that would fight the agent for the port.

```sh
A=gui/$(id -u)/com.ce50.lattice-pro

launchctl print $A | grep -E 'state =|pid =|last exit code'   # status
launchctl kickstart -k $A                                     # restart
launchctl bootout $A                                          # stop until reloaded
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ce50.lattice-pro.plist

curl -sS -o /dev/null -w 'pro mode -> %{http_code}\n' --max-time 10 \
  http://127.0.0.1:8766/healthz
tail -20 ~/Library/Logs/lattice-pro.log
```

Open `http://127.0.0.1:8766`; the badge in the UI reads which mode it is in.

**After a pull that changes dependencies**, resync and restart — the agent runs
`.venv/bin/lattice` directly, so it uses whatever is in `.venv`:

```sh
cd "$M4REPO" && uv sync --all-groups && launchctl kickstart -k gui/$(id -u)/com.ce50.lattice-pro
```

This includes `mcp-server-motherduck`: Pro mode launches the executable beside
`.venv/bin/python` as the persistent `scopus` stdio server, without `uvx` or run-time
dependency resolution. Before restarting a release that changes DuckDB, ensure the
managed DuckDB home contains the matching FTS extension:

```sh
SCOPUS_DUCKDB_HOME=/Users/ce50/.lattice-next/duckdb-home
mkdir -p "$SCOPUS_DUCKDB_HOME"
"$M4REPO/.venv/bin/python" - "$SCOPUS_DUCKDB_HOME" <<'PY'
import duckdb
import sys

connection = duckdb.connect(":memory:")
connection.execute("SET home_directory = ?", [sys.argv[1]])
connection.execute("INSTALL fts")
connection.execute("LOAD fts")
connection.close()
PY
```

Run that after `uv sync` and before the LaunchAgent restart. The service loads the
preinstalled extension, then applies bounded threads, memory and temporary storage;
disables automatic/community extension loading and external access; and locks its
configuration. A missing or mismatched extension is a failed release, not permission
to let an Ask job install one.

**After the repo directory is renamed or moved, delete `.venv` first.** `uv sync`
rewrites the project's own console script but leaves every third-party one pointing at
the old interpreter, and the failure is misleading: `uv run ruff` still works (native
binary, no shebang) while `uv run pytest` reports `Failed to spawn: pytest — No such
file or directory`, naming the script rather than the interpreter that is missing. The
gates then look healthy while nothing has actually run.

```sh
head -1 "$M4REPO/.venv/bin/pytest"     # must name the current path
cd "$M4REPO" && rm -rf .venv && uv sync --all-groups
```

For a one-off foreground debugging run, `bootout` the agent first, then:

```sh
LATTICE_MODE=local uv run lattice   # the corpus default is absolute since the move
```

> **Never `pkill -f lattice`.** The legacy scopus-db app on `8765` runs as
> `~/.lattice-venv/bin/python -u app/server.py` and matches that pattern — so does the
> Claude Agent SDK process it spawns. Use `launchctl`, or kill by port
> (`lsof -nP -ti tcp:8766 -sTCP:LISTEN`), never by name.

Pro mode reads `~/.lattice-next` and reaches the corpus through its persistent
read-only stdio server; it does not touch the hosted state under
`~/.lattice-next/hosted/state`. It is safe to run while the Intel Mac serves the
public site.

---

## 3. Start and stop the public stack

On whichever host is active. The `public` profile is what adds `cloudflared`.

```sh
# start (corpus sidecar + application + tunnel)
docker compose $ENVF --profile public up -d
docker compose $ENVF --profile public ps

# stop everything
docker compose $ENVF --profile public down

# application pair only, no tunnel — this is what a warmed standby runs
docker compose $ENVF up -d corpus-mcp lattice
```

**Before starting the public profile anywhere, confirm the other host has no
`cloudflared`.** Run block 1.

---

## 4. Ship a code change to the Intel Mac

The Intel Mac cannot pull images (see `troubleshooting.md` #2), so both the
application and corpus-MCP images are cross-built on the M4 and shipped as one
tarball. Never deploy only one half of the pair.

**a. Gates, on the M4:**

```sh
cd "$M4REPO"
uv run ruff format --check src tests
uv run ruff check .
uv run pytest
docker compose $ENVF config --quiet && echo 'compose config OK'
```

**b. Publish the code:**

```sh
git ls-files deploy/private | head        # MUST be empty
git push origin feat/friendly-onboarding-v0.2.0
```

**c. Cross-build both images for amd64 and prove both architectures:**

```sh
docker buildx build --platform linux/amd64 -t lattice-private:local-amd64 --load .
docker buildx build --target corpus-mcp --platform linux/amd64 \
  -t lattice-corpus-mcp:local-amd64 --load .
docker image inspect lattice-private:local-amd64 --format 'arch: {{.Architecture}} {{.Os}}'
docker image inspect lattice-corpus-mcp:local-amd64 --format 'arch: {{.Architecture}} {{.Os}}'
# both must print: arch: amd64 linux — stop if either says arm64
```

**d. Ship and load:**

```sh
docker save lattice-private:local-amd64 lattice-corpus-mcp:local-amd64 \
  -o /tmp/lattice-images-amd64.tar
rsync -a --partial /tmp/lattice-images-amd64.tar \
  remote-mac-ts:/tmp/lattice-images-amd64.tar

ssh -o ConnectTimeout=20 -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  set -e
  docker load -i /tmp/lattice-images-amd64.tar | tail -4
  docker tag lattice-private:local-amd64 lattice-private:local
  docker tag lattice-corpus-mcp:local-amd64 lattice-corpus-mcp:local
  docker image inspect lattice-private:local --format "arch: {{.Architecture}} {{.Os}}"
  docker image inspect lattice-corpus-mcp:local --format "arch: {{.Architecture}} {{.Os}}"
'
```

**e. Restart on the Intel Mac** — the tag already exists, so this does not rebuild:

```sh
ssh -o ConnectTimeout=20 -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  cd ~/lattice
  git pull --ff-only
  docker compose --env-file deploy/private/production.env config --quiet
  docker compose --env-file deploy/private/production.env --profile public up -d
  docker compose --env-file deploy/private/production.env ps | tail -5
'
```

**f. Verify and tidy:**

```sh
# 401 only confirms Access is fronting the hostname — it cannot see the origin.
# The `ps` above is what proves the deploy took.
curl -sS -o /dev/null -w 'public -> %{http_code}\n' --max-time 25 \
  https://lattice.christianengels.net/healthz
rm -f /tmp/lattice-images-amd64.tar
ssh -o BatchMode=yes remote-mac-ts 'rm -f /tmp/lattice-images-amd64.tar'
```

If the base images ever need refreshing on the Intel Mac (a Dockerfile `FROM` bump,
or a new `cloudflared` tag), ship those the same way — resolve the amd64 digest first:

```sh
docker buildx imagetools inspect python:3.12-slim | grep -B2 'linux/amd64'
docker pull --platform linux/amd64 "python@sha256:<digest>"
docker tag  "python@sha256:<digest>" lattice-xfer/python:3.12-slim
docker image inspect lattice-xfer/python:3.12-slim --format '{{.Architecture}}'  # amd64
docker save lattice-xfer/python:3.12-slim -o /tmp/lattice-base-amd64.tar
# rsync, docker load, then retag to the plain name on the far side
```

---

## 5. Switch hosts / fail back to the M4

**Decide the state question before you start, not during.** The M4's hosted state is
frozen at the 2026-07-27 switch and is stale the moment the Intel Mac serves one
request. Either copy the live state back first, or accept older data and say so.

```sh
# 1. take the public stack down on the OLD active host (tunnel dies with it)
ssh -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  cd ~/lattice && docker compose --env-file deploy/private/production.env --profile public down
'

# 2. with BOTH stacks stopped, copy the state back (skip only if accepting the snapshot)
rsync -a --partial remote-mac-ts:/Users/ce50/.lattice-next/hosted/state/ \
  ~/.lattice-next/hosted/state/

# 3. build both images natively on the M4 (arm64 — no cross-build needed here)
cd "$M4REPO"
docker compose $ENVF build lattice corpus-mcp

# 4. bring the M4 up as the public host
docker compose $ENVF --profile public up -d
docker compose $ENVF --profile public ps

# 5. verify — containers up here, zero on the other host. The hostname's 401 is
#    not evidence either way; only the container lines are.
curl -sS -o /dev/null -w 'public -> %{http_code}\n' --max-time 25 \
  https://lattice.christianengels.net/healthz
ssh -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  docker ps --format "{{.Names}}" | wc -l
'
```

Going the other way (M4 → Intel) is the same sequence with the hosts swapped, except
step 3 becomes the cross-build of block 4c–4d.

Do not switch while jobs are running. No DNS or Cloudflare change is ever needed.

---

## 6. Refresh the corpus

After `scopus.duckdb` is rebuilt. It is 14 GB; the transfer is the slow part (roughly
20 minutes over Tailscale).

> **Check the symlink first.** `scopus-db/data/scopus.duckdb` is no longer the corpus
> — it is a symlink to `~/lattice-data/scopus.duckdb`, kept for the legacy 8765 app. A
> rebuild that *writes through* it updates the real file, which is what you want; one
> that unlinks and recreates leaves a fresh 14 GB file in Dropbox and a corpus nobody
> is reading. Confirm with `ls -l` before trusting either outcome, and if it was
> replaced, move the new file to `~/lattice-data/` and restore the symlink.

```sh
SRC=/Users/ce50/lattice-data/scopus.duckdb
ls -l /Users/ce50/Library/CloudStorage/Dropbox/PLAY/working-repos/scopus-db/data/scopus.duckdb

# 1. stop the application and its corpus sidecar on the far side
ssh -o BatchMode=yes remote-mac-ts '
  export PATH=/usr/local/bin:$PATH
  export DOCKER_HOST=unix:///Users/ce50/.docker/run/docker.sock
  cd ~/lattice && docker compose --env-file deploy/private/production.env --profile public down
'

# 2. transfer — run this in the background, it is long
rsync -a --partial --progress "$SRC" remote-mac-ts:/Users/ce50/lattice-data/scopus.duckdb

# 3. compare hashes on both sides — they must match exactly
shasum -a 256 "$SRC"
ssh -o BatchMode=yes remote-mac-ts 'shasum -a 256 ~/lattice-data/scopus.duckdb'

# 4. restart, then record the new hash in the lattice progress log
```

macOS ships rsync 2.6.9. **`--info=progress2` and `--append-verify` do not exist
there** and fail the whole transfer. `-a --partial --progress` is the portable set.

**Then prove the other readers still resolve** — five skill symlinks, Pro mode's
stdio server, hosted `corpus-mcp`, the standalone MCP configuration and the legacy app
all point at this file (`topology.md`, "Who reads the corpus"). Open each rather than
reading its link, then run block 10:

```sh
# Not the system python3 — it has no duckdb. The repo venv does.
"$M4REPO/.venv/bin/python" - <<'PY'
import glob, os, duckdb
paths = glob.glob(os.path.expanduser(
    "~/Library/CloudStorage/Dropbox/PLAY/working-repos/research-repos/*/skills/*/scopus.duckdb"))
for p in paths + [os.path.expanduser("~/.claude/skills/search-literature/scopus.duckdb")]:
    try:
        con = duckdb.connect(p, read_only=True)
        print(f"{con.execute('select count(*) from articles').fetchone()[0]:>9}  {p}")
        con.close()
    except Exception as exc:
        print(f"   FAILED  {p}: {exc}")
PY
```

---

## 7. State — inspect, back up

**Inspect** (content-free: integrity plus row counts, no IDs, emails or prompts):

```sh
cd "$M4REPO"
python3 scripts/state-inventory.py ~/.lattice-next/hosted/state/lattice.sqlite3

ssh -o BatchMode=yes remote-mac-ts '
  D=~/.lattice-next/hosted/state/lattice.sqlite3
  for t in tenants chats messages workspaces integrations; do
    printf "  %-14s " "$t"; sqlite3 -readonly "$D" "SELECT count(*) FROM $t"
  done
'
```

**Back up.** Working since `2026-07-27`, and **scheduled** — `com.ce50.lattice-backup`
runs `scripts/backup-state.sh` daily at 03:15 on the active host, keeping the most
recent 30 archives in `~/.lattice-backups`. It does not require stopping the
application: the database goes through SQLite's own backup, which is safe against a
live writer.

```sh
# on the active host — one immediate backup
ssh remote-mac-ts 'export PATH=/usr/local/bin:$PATH; cd ~/lattice && sh scripts/backup-state.sh'

# check the schedule
ssh remote-mac-ts 'launchctl print gui/$(id -u)/com.ce50.lattice-backup | grep -E "runs =|last exit code"'
ssh remote-mac-ts 'tail -3 ~/Library/Logs/lattice-backup.log'
```

**The identity lives on the standby host, deliberately** — the machine holding the
live data cannot decrypt its own backups. `~/.lattice-backup-identity.txt` is on the
**M4** (`0600`, never copied anywhere); only the public
`~/.lattice-backup-recipients.txt` is on both. If the active/standby roles swap, move
the identity to whichever host is passive.

**Restore — on the M4, the only host that can:**

```sh
rsync -a remote-mac-ts:/Users/ce50/.lattice-backups/lattice-state-<stamp>.tar.gz.age /tmp/
T=$(mktemp -d)
age -d -i ~/.lattice-backup-identity.txt /tmp/lattice-state-<stamp>.tar.gz.age | tar -C "$T" -xzf -
sqlite3 "$T/lattice.sqlite3" 'PRAGMA integrity_check'
```

To put a restored copy back into service: stop the application, swap the state
directory, start. The archive holds a single self-contained `lattice.sqlite3` with no
`-wal`/`-shm` — Lattice re-enables WAL when it opens it.

Copying a state directory by hand (rsync, `cp`) is different: **stop the application
first.** A running container is a live SQLite writer, and its `-wal` currently holds
half a megabyte the main file does not.

---

## 8. Prune

```sh
docker builder prune -f              # build cache — reclaimed 13.76 GB last time
docker images lattice-private --format '{{.Tag}}  {{.Size}}'
```

Nine older `lattice-private:*` development tags sit on the M4, about 6.5 GB
(`v0.2.0-arm64`, `amd64-check`, `legacy-ui-check` and similar). They are build
history, not the deployment. Ask before removing them.

---

## 9. Release gates, for a real release

From `docs/OPERATIONS.md` — the full battery, not the quick gates in block 4a:

```sh
uv run ruff format --check src tests
uv run ruff check .
uv run pytest
scripts/verify-source-integrity.sh
docker compose $ENVF config --quiet
docker build --platform linux/arm64 -t lattice-private:v0.2.0-arm64 .
docker build --target corpus-mcp --platform linux/arm64 \
  -t lattice-corpus-mcp:v0.2.0-arm64 .
docker build --platform linux/amd64 -t lattice-private:v0.2.0-amd64 .
docker build --target corpus-mcp --platform linux/amd64 \
  -t lattice-corpus-mcp:v0.2.0-amd64 .
```

Live Anthropic, Zotero, LibKey, Cloudflare, Scopus MCP and two-account checks cannot
all be automated — the manual parts belong in `deploy/POST_CUTOVER_CHECKLIST.md`.

---

## 10. Scopus MCP — status and release smoke test

Hosted has a separate, corpus-only sidecar. It must be healthy before Lattice starts,
must have no published port, and must share a network only with the application:

```sh
docker compose $ENVF ps corpus-mcp lattice
docker compose $ENVF logs --tail=30 corpus-mcp
docker inspect "$(docker compose $ENVF ps -q corpus-mcp)" \
  --format 'health={{.State.Health.Status}} ports={{json .NetworkSettings.Ports}}'
```

An empty host-port mapping is correct. The sidecar has no secrets, state or Lattice
source; its only host mount is the corpus at `/data/scopus.duckdb:ro`. Do not expose
port 8000 to make a smoke test easier.

For Pro mode, the LaunchAgent log must show the persistent stdio server starting from
the project environment. During an Ask run, `ps` should show
`mcp-server-motherduck`; no `uvx` process should appear.

**Verified 2026-07-28:** all 175 tests and source-integrity checks passed, both images
built for ARM64 and AMD64, local Pro restarted, and local Ask plus AI Search queried
Scopus successfully. On Intel at implementation and runtime SHA `a23de94`, the
application and sidecar are healthy, the direct HTTP MCP handshake/security checks
passed, and both the MCP readiness race and Linux same-process initialization-lock
race are fixed.

The authenticated release smoke battery below passed for Christian in Pro and hosted;
repeat it with the remaining allowlisted coauthor and complete the two-real-account
checks:

1. list databases, tables and columns, including `articles`, every `wos_*` object and
   the FTS schema;
2. run a small FTS query plus a join, CTE, aggregate and window query;
3. confirm tool chips say `Scopus · …` while PDF/web/findings/working-paper/Zotero
   actions say `Lattice · …`;
4. confirm DDL, DML, `SET`, `COPY`, `ATTACH`, `CALL`, `INSTALL`, `LOAD`, file/URL reads
   and database switching fail without revealing a host path;
5. exercise 10,000 rows, 500,000 characters and 120 seconds per query and the hosted
   5,000,000-character cumulative cap;
6. run two hosted readers together and confirm they serialize, including after
   cancellation or a forced worker exit;
7. compare corpus SHA-256 before and after.

The Search tab's ✦ AI run gets only the four Scopus tools. It must curate results
without asking for a working directory, invoking a Lattice action or creating an
empty Ask chat.

Christian's authenticated hosted Ask exposed all four Scopus tools, including working
table discovery and SQL reporting 1,160,915 articles with latest year 2026. Hosted AI
Search also completed and curated 12 papers. **Still pending:** multi-user/
two-real-account coauthor acceptance and the corresponding remainder of the
allowlisted-user checklist.
