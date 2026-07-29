---
name: wos-pull
description: Use when Christian asks how the Web of Science pull is going, for a WoS crawl status update, whether the mapping/references pull is finished, or invokes /wos-pull. Reads the unattended pipeline's logs and parquet checkpoints at ~/.wos-pull (read-only) and reports progress, throughput, ETA and health.
allowed-tools: Bash, Read
---

# WoS Pull Status

Status report for the unattended Web of Science citation pull. The pipeline
runs OUTSIDE the repo at `~/.wos-pull/` (launchd agent `com.ce50.wos-pull`,
hourly + at load), because macOS TCC blocks background agents from reading
Dropbox. Everything here is **read-only** — never write into `~/.wos-pull/`
or restart the agent unless Christian explicitly asks.

## Background you need

- **The worklist was refreshed 2026-07-09 16:28** (repo script
  `72-wos_refresh_worklist.py`, atomic swap, checkpoints untouched): the
  corpus grew from 711,885 to **1,109,845 DOIs** (+397,960: pre-2000
  backfill, 2026 coverage, JFR, missing ABS 3/4/4* journals). Old worklist
  backed up as `worklist.parquet.bak-20260709-152839`. Both scripts compute
  work sets live from the parts, so phase-1 work is never redone.
- **Script 64 (mapping)**: DOI → WoS UT via the Starter API (request quota
  5,000/day — a quota-day burst maps ~200k DOIs in ~6h). Phase 1 complete
  2026-07-06: 711,885 attempted, 659,244 matched (92.6%). Phase 2 (the
  397,960 new DOIs, expected match ~93%: high 90s for 2010+, ~77% pre-2000)
  was started MANUALLY at 2026-07-09 16:32 because launchd `StartInterval`
  never fires while a previous runner instance is alive — the long 65 pass
  blocks all fires, so 64 would otherwise not run until that pass ends. A
  second manual quota-day burst around 2026-07-10 finishes it; if nobody
  bothers, the fires that resume after the 65 pass ends sweep it up anyway.
  Manual start (only with Christian's explicit go-ahead):
  `nohup /usr/bin/caffeinate -i ~/.wos-pull/.venv/bin/python ~/.wos-pull/bin/64-wos_map_dois.py >> ~/.wos-pull/data/.wos_cache/runner.log 2>&1 &`
  — safe alongside anything, it takes `64.lock`.
- **Script 65 (references)**: pulls cited-reference lists via the Expanded
  API `/references` endpoint (quota-free — verified). Since 2026-07-08 it
  runs the whole remaining work set to completion in ONE long pass (the old
  10k-paper chunks and the records-quota watchdog were removed). While that
  pass is alive launchd fires are fully suppressed (see above), and a
  leftover 0-byte `65.lock` never wedges anything — it's an `fcntl.flock`,
  dropped by the kernel on process death; a fire after a death resumes from
  the checkpoint. A running 65 reads its UT list ONCE at startup, so UTs
  mapped mid-pass enter on its NEXT start. Target: ~1,031,000 mapped UTs
  once phase-2 mapping lands (~659k from phase 1 + ~372k new) — compute the
  live number from the parts, never quote a constant. Refs/paper is NOT a
  constant — it climbs with the work set's publication year (35.8/paper over
  the earliest parts, 56.9 over the most recent; the new cohort adds a
  pre-2000 tail at ~30-38/paper). Expect **~50M reference rows total (±2M)**
  (was ~32-34M before the corpus grew). A rising rows-per-part is the
  expected shape, not an anomaly.
- Checkpoints are append-only parquet parts in `~/.wos-pull/data/wos/`:
  `ut_map__part-*` (mapping), `refs_meta__part-*` (one row per fetched paper —
  the references checkpoint) and `references__part-*` (the actual rows).
- Logs: `~/.wos-pull/data/.wos_cache/runner.log` (rotated at 10MB to
  `runner.log.old`); launchd-level errors in `launchd.log` in the same folder.
- **Full autopilot since 2026-07-09** — three extra launchd agents; everything
  posts macOS notifications and self-retires when done, so silence + agents
  still loaded = working as intended:
  - `com.ce50.wos-map-burst` (4-hourly): runs 64 bursts (needed because launchd
    never re-fires com.ce50.wos-pull while a long 65 pass is alive). State in
    `map_burst.state`; log lines in runner.log ("=== map burst ...").
  - `com.ce50.scopus-backfill` (daily 07:11): sleeps until the Scopus weekly
    quota resets (2026-07-15), then repo chain 74→75→78→77→63→72 (hole journals
    + extras into scopus.duckdb, FTS rebuild, worklist refresh). Log:
    `backfill.log`; marker `backfill.done`; self-retires on success.
  - `com.ce50.wos-finish` (daily 08:23): once backfill.done exists AND the pull
    is complete, runs repo code/73 (builds wos_map/wos_references/
    wos_cited_works), then retires ALL WoS agents incl. wos-pull, wos-report
    and itself, deleting their plists. Log: `finish.log`.
  TCC gotcha baked into these: under launchd, Dropbox-content reads succeed
  from the venv/uv PYTHON binaries but zsh builtins get "operation not
  permitted" — wrappers must route repo file access through python.

## Gather (adapt as needed, don't run blindly)

1. **Agent health**:
   `launchctl print gui/$(id -u)/com.ce50.wos-pull | grep -E "state|pid|last exit"`
   — "state = running" is the norm now (one continuous references run).
   Remember manual runs (like the phase-2 64) live OUTSIDE the agent: check
   `pgrep -fl "64-wos_map_dois|65-wos_pull_references"` to see everything.
   "not running" while references remain means the long run died; the next
   hourly fire resumes it, but read the end of `launchd.log` and `runner.log`
   to see why it died. Beware two stale signals: `last exit code` reports the
   last COMPLETED run, so while a long run is alive it shows the *previous*
   exit, and `launchd.log` is never truncated. Check both against the live
   run's start time (`ps -p <pid> -o lstart,etime`) before believing either.
   Only a failure newer than the current run, or a recurring one, is a
   problem. A parse error in `runner.sh` is worth a `zsh -n` before you
   report it — a fire that catches the script mid-edit logs one for good.

2. **Recent activity and warnings**:
   `tail -30 ~/.wos-pull/data/.wos_cache/runner.log` for the latest run, plus
   `grep -E "Aborting|free-ness|consecutive" runner.log | tail`
   for anything alarming. 429/backoff lines are routine and come in bursts
   (7 in one hour on 2026-07-09 with zero effect on the part cadence) — judge
   them by whether the minutes-per-part slips, not by counting them.
   "Aborting" or anything mentioning free-ness is not routine — flag it
   prominently. (Historical
   "quota rem=" / "quota dropped" / "Stopping: daily request quota" lines
   predate 2026-07-08 and are not signals: the records-quota watchdog was
   removed because Christian spends that quota on other projects. The only
   quota guard left is in-band: 65 aborts if a /references response itself
   ever carries a quota header.)

3. **Progress numbers** — compute from the parts with the pipeline's own venv
   (it has polars; works from any cwd):

   ```bash
   ~/.wos-pull/.venv/bin/python - <<'EOF'
   import polars as pl, glob, os
   base = os.path.expanduser("~/.wos-pull/data/wos")
   m = pl.scan_parquet(glob.glob(f"{base}/ut_map__part-*.parquet")).collect()
   total = pl.read_parquet(os.path.expanduser("~/.wos-pull/data/worklist.parquet")).height
   mapped = m.filter(pl.col("wos_ut").is_not_null()).height
   print(f"mapping: {m.height:,}/{total:,} attempted ({100*m.height/total:.1f}%), "
         f"{mapped:,} matched ({100*mapped/max(m.height,1):.1f}%)")
   meta = pl.scan_parquet(glob.glob(f"{base}/refs_meta__part-*.parquet")).collect()
   nrefs = sum(pl.scan_parquet(p).select(pl.len()).collect().item()
               for p in glob.glob(f"{base}/references__part-*.parquet"))
   print(f"references: {meta.height:,}/{mapped:,} mapped papers done "
         f"({100*meta.height/max(mapped,1):.1f}%), {nrefs:,} reference rows")
   EOF
   ```

4. **Throughput and ETA**: use file mtimes of the `refs_meta__part-*` files
   (each full part = 2,000 papers; terminal flushes are smaller) over the last
   ~24h to get papers/day, then ETA = remaining ÷ rate. Minutes-per-part drifts
   UP across the pull — more refs/paper means more `firstRecord` pagination —
   so benchmark against the recent cadence, not a fixed constant (31.1 min/part
   = 92.6k papers/day on 2026-07-09, against ~28 min earlier on). A sharp drop,
   or a gap much longer than the recent cadence, means the run is restarting or
   being throttled — check the log. Caveat the ETA: it assumes the machine
   stays on.

## Report

Lead with one plain sentence: is it healthy and roughly when will it finish.
Then a compact status — mapping % and match rate, references % and row count,
current throughput and ETA, agent state, and any warnings found. Keep it
short; no tables unless asked.

Completion handling:
- Log line "Mapping complete — nothing to do." → mapping done against the
  CURRENT worklist (check the worklist size in the same log line — 1,109,845
  is the refreshed corpus; 711,885 lines are pre-refresh history).
- Log line "References complete for all mapped UTs — nothing to do." → the
  whole pull is done ONLY if mapping is also complete; mid-phase-2 it can
  appear transiently if 65 finishes before the next mapping burst lands.
- Both complete against the 1,109,845 worklist → the pull is done. Then
  remind Christian: the build step is NOT yet written — write and run it
  ONCE as `73-build_wos_tables.py` (the docstrings in 64-67 say "68" but
  that number is now taken by `68-pull_missing_abs_high_scopus.py`; it
  builds wos_map, wos_references and derived wos_cited_works into the live
  scopus.duckdb), and the agent is retired with
  `launchctl bootout gui/$(id -u)/com.ce50.wos-pull`.
