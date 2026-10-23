#!/usr/bin/env bash
# Milestone 13 pod P2 (docs/milestone13.md §5.1 phase 2, §13.1 track T7, §13.6; user decisions D1, D2, D6 of 12 Oct
# 2026) on top of Milestone 12 pod P4: the library growth by drawn demand. New steps (python -m wenart.assets growth
# run <step>, wenart/assets/audit/growth_run.py):
#   demands, size-grid   the drawn demands of real02/03/04 and the coverage per licence mode BEFORE the growth
#                        (results copied: demands.json, size_grid.json, coverage.json, gaps_demand.md)
#   speed-probe          the first ABO downloads timed (15 min cap, GROWTH_PROBE_MIN): the MB/s decides the pick
#                        counts within the targets of audit.yaml growth (speed.json)
#   ingest-hssd          HSSD objects of results/library/growth/candidates_hssd.json (approved_hssd.json: the rule of
#                        D2), CC BY-NC 4.0, gated: needs HF_TOKEN in the environment (the RunPod secret hf_token,
#                        never printed); without it, or on a 403 from the Hub (terms not accepted), the step is
#                        SKIPPED with a clear log line and the job goes on
#   ingest-abo-m13       ABO by size grid (candidates_abo_m13.json, 8 parallel downloads)
#   ingest-polyhaven-m13 Poly Haven vegetation and furniture at 2K, and the Milestone 12 furniture fetched again at
#                        2K (GROWTH_PH_SIZE, default 2k; the 1K files stay)
#   ingest-ambientcg     the ambientCG shell sets (2K-JPG) for wenart.blender.materials SHELL_SLOTS
#   coverage             the coverage per licence mode AFTER the audit (the catalogue copies), the demand gaps
# Everything under /workspace/assets and /workspace/library-growth (the volume); nothing is deleted; every step
# keeps present files (a second run resumes). The catalogue copies are written with the counts per source, per
# licence flag and per licence mode (report step).
#
# Milestone 13 round 3 (docs/milestone13.md §14.6, after pod P2):
#   refetch              the current file of every catalogue entry waiting for a re-audit (audit pending with a
#                        `reaudit` record: an asset republished upstream, vintage_wooden_drawer_01 on 16 Oct 2026);
#                        the older files are kept beside (<name>.superseded-<sha12>); the catalogue step puts the
#                        entry into new_ids.json once its current file is on the volume, so this audit judges it again
#   steps.tsv            a fourth column: the last line a failed step printed (P2 had `preview 1 0` and nothing else)
#   GROWTH_ONLY=hssd     pod P2b: the HSSD layer alone, once the user has accepted the HSSD terms with the account
#                        whose token is the RunPod secret hf_token (P2 got HTTP 403). Runs setup-check, ingest-hssd,
#                        refetch, catalogue --only hssd (every other entry stays as the repo's catalogues have it;
#                        new_ids.json = the HSSD ids, the earlier ids kept as kept_ids), render of the new ids, code,
#                        ask, decide, write, vision-fields, gaps, coverage, report and the GPU tests. No other
#                        download, conversion or catalogue step runs; nothing on the volume is deleted; a second run
#                        resumes (present HSSD files kept, renders by job_sha, answers by input hash). About 50 min
#                        for the 874 picks at P2's rates (render 1.42 s per model with 3 workers: ~21 min; ask 884
#                        requests in 1296 s incl. the server start: ~21 min; the rest a few minutes):
#     python3 scripts/gpu_run.py run --job scripts/jobs/library_growth.sh --disk 150 --max-minutes 90 --over-5-ok \
#       --env GROWTH_ONLY=hssd --env AUDIT_MODEL_KEY=agent --purpose "M13 P2b: HSSD layer"
#   The ask needs the 52 GB agent/judge server (docs/milestone13.md §8: P2 on the RTX PRO 6000). Without --gpu the
#   runner's GPU_PRIORITY falls back to the RTX 5090 (32 GB, CLAUDE.md: cannot host it) when the 6000 is out of
#   stock; add --gpu 'RTX PRO 6000' to the command above if that must not happen (the lead's call).
#   GROWTH_ONLY=3dwh     the 3D Warehouse layer (the user's request of 23 Oct 2026; wenart/assets/warehouse.py): ONE pod
#                        downloads the user's Google Drive zip "3D Warehouse Furniture.zip" (6.26 GB; the file must be
#                        shared as "anyone with the link": drive.usercontent.google.com with confirm=t; resumed with
#                        curl -C -, the size checked against the Drive file) into $WH_ROOT/zip/, then ingest-3dwh
#                        (the GLBs extracted safely to $WH_ROOT/glb/<uid>.glb, typed from their folder and file names,
#                        measured, unit / up axis / origin / double-sided faces / roughness fixed into
#                        $ASSETS/models/3dwh/), catalogue --only 3dwh (furniture and decor entries; trees, doors and
#                        windows as previews), render, code, ask (the m13.2 question: the logo and print fields),
#                        decide, write, vision-fields, sheets, gaps, coverage, preview, report and the GPU tests.
#                        Nothing on the volume is deleted; a second run resumes (zip by size, GLBs by size, fixes by
#                        source sha256, renders by job_sha, answers by input hash). About 400 models per hour of audit
#                        on the RTX PRO 6000 (HSSD's rate):
#     python3 scripts/gpu_run.py run --job scripts/jobs/library_growth.sh --gpu 'RTX PRO 6000' --disk 150 \
#       --max-minutes 180 --over-5-ok --env GROWTH_ONLY=3dwh --env AUDIT_MODEL_KEY=agent \
#       --purpose "3D Warehouse layer: download, fix-ups, audit"
#
# Milestone 12 pod P4: the library growth (docs/milestone12.md §6.4 D24, §14.3; docs/m12_tracks/P4.md). The four lists
# the user approved on 11 Oct 2026 (results/library/growth/approved_*.json, read through growth.approved, the
# ingest gate) are downloaded or generated, put into COPIES of the catalogues (never wenart/furniture/*.json: the
# lead copies them in), and audited like the rest of the library (P2's render with the scale reference, the code
# checks, the vision question of P3, decide.py with user decision 1a). The 4 P3 models still pending get their
# second vision pass. Needs P2/P3's audit folder on the volume (AUDIT_ROOT, /workspace/library-audit). Run by
# scripts/pod_entry.sh (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE set; HF_TOKEN in the
# environment, never printed).
#
#   python3 scripts/gpu_run.py run --job scripts/jobs/library_growth.sh --gpu 'RTX PRO 6000' --disk 150 \
#     --max-minutes 210 --over-5-ok --env AUDIT_MODEL_KEY=agent --purpose "M13 P2: library growth by demand + audit"
#   (Milestone 12: --max-minutes 110 --purpose "M12 P4: library growth")
#
# Steps (each timed into $GROWTH/report/steps.tsv; a failed step is recorded and the next independent one still
# runs; exit 1 when any failed or was skipped for lack of time). Expected minutes (EU-RO-1, ~1 GB/s from HF / CDN):
#   background, from the start (explicit pids, never a bare wait):
#     setup-check       vLLM + the model of AUDIT_MODEL_KEY (scripts/pod_setup_polish.sh, part check)    8-12
#     infinigen         uv + Python 3.11 + princeton-vl/infinigen v1.19.0 and its submodules infinigen_gpl,
#                       OcMesher (uv sync --frozen: bpy 4.2.0, scikit-image built from source) 5-10, then
#                       30 assets (CPU bake at 1024 px; a trial here on 4 CPUs: 11-22 s, the plant pot ~2 min)
#                       5-20, capped at INFINIGEN_CAP_MIN (40) after the job start; a failure is recorded
#                       and the rest goes on                                                             <= 40
#     ingest-polyhaven  88 approved models, glTF 1k (what the fit resolves), sequential                  1-3
#     ingest-abo        232 GLBs, 7.8 GB, 8 parallel downloads                                           2-6
#     ingest-gso        36 archives, 0.24 GB                                                             < 1
#   foreground:
#     gso-licence       unpack, CC BY 4.0 evidence per object (archive files, Gazebo Fuel record)        1
#     convert-gso       OBJ -> GLB in Blender 5.2                                                       1-2
#     catalogue         every new model measured (numpy), entries, catalogue copies validated           2-4
#     render-a          P2's render step on the new models (--ids-file), 3 Blender workers, ~4 s each   8-14
#     (join infinigen)  waits for the capped Infinigen part
#     convert-infinigen, catalogue-b, render-b  the Infinigen models                                  1-3
#     code              code checks (duplicates against the whole library)                              1
#     ask               one vLLM server session: P4 pass 1 + 2, P3 pass 2 of the pending models        4-8
#     decide, write, vision-fields, pending, sheets, gaps, preview, report                              2-4
#     gpu-tests         pytest -m gpu tests/gpu/test_library.py -k growth                              1-2
# Expected 50-65 min; worst case ~85 min (Infinigen cap 40 + 30 after it + slow downloads), inside the pod's
# 95-minute WENART_DEADLINE. A cut pod (or a step skipped near the deadline) is finished by a second run of the same
# command: downloads keep complete files, conversions and measurements are reused by sha256, renders by job_sha,
# answers by their input hash, Infinigen jobs by their result.json, and nothing is set up that is not needed.
# After every step the small files are copied: $WENART_RESULTS/library/growth/ (ingest, GSO licence evidence,
# Infinigen commit, factories and jobs, conversion, catalogue, growth.md, steps) and $WENART_RESULTS/library/audit/
# p4/ (audit.json/.csv/.md of the new models, answers, contact sheets, gaps, pending_p3, the catalogue copies).
#
# Env (all optional): AUDIT_MODEL_KEY (default audit.yaml ask.model_key), AUDIT_ROOT (/workspace/library-audit),
# GROWTH_ROOT (/workspace/library-growth), WENART_ASSETS (/workspace/assets), AUDIT_WORKERS (3), INFINIGEN_CAP_MIN
# (40), INFINIGEN_TEX_RES (1024), GROWTH_PH_SIZE (2k since Milestone 13; 1k in M12), GROWTH_PROBE_MIN (15),
# GROWTH_MIN_FREE_GB (30: the M13 downloads are about 18 GB), HF_TOKEN (the HSSD gate; from the pod secret),
# GROWTH_ONLY (empty or all: every step; hssd: the HSSD layer alone; 3dwh: the 3D Warehouse layer alone, see above),
# WH_ROOT (/workspace/library/3dwh), WH_WORKERS (16: fix-up processes), WH_FILE_ID / WH_BYTES (the Drive file).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-library_growth}"
LOG=$LOGS/library_growth-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
GROWTH="${GROWTH_ROOT:-$WS/library-growth}"
AUDIT_ROOT="${AUDIT_ROOT:-$WS/library-audit}"
P4="$AUDIT_ROOT/p4"
P4A="$P4/audit"
AUDIT_WORKERS="${AUDIT_WORKERS:-3}"
INFINIGEN_CAP_MIN="${INFINIGEN_CAP_MIN:-40}"
INFINIGEN_TEX_RES="${INFINIGEN_TEX_RES:-1024}"
GROWTH_PH_SIZE="${GROWTH_PH_SIZE:-2k}"
GROWTH_PROBE_MIN="${GROWTH_PROBE_MIN:-15}"
GROWTH_ONLY="${GROWTH_ONLY:-all}"
# the 3D Warehouse layer (GROWTH_ONLY=3dwh; = wenart.assets.warehouse DRIVE_FILE_ID, ZIP_BYTES, ZIP_NAME, LIBRARY_ROOT)
WH_ROOT="${WH_ROOT:-$WS/library/3dwh}"
WH_FILE_ID="${WH_FILE_ID:-1nSHF5dvjLLcpruowus8zZUx8kSiDxkjD}"
WH_BYTES="${WH_BYTES:-6261344770}"
WH_ZIP="3D Warehouse Furniture.zip"
WH_WORKERS="${WH_WORKERS:-16}"
# Infinigen, pinned (wenart/assets/audit/growth_infinigen.py: tag v1.19.0, read with git ls-remote on 11 Oct 2026)
IG_URL=https://github.com/princeton-vl/infinigen
IG_COMMIT=01c39c7f7adcf7363ccbcc57c64410c69f4a4e7c
IG_GPL_COMMIT=10c1d76f5c35003e919be7265185c9c355e3b70c        # submodule infinigen/infinigen_gpl (git ls-tree)
IG_OCMESHER_COMMIT=bb895a01b8f574da10be1df470210df7463a75c7   # submodule infinigen/OcMesher (git ls-tree)
IG_DIR=$FAST/infinigen
IG_VENV=$FAST/venv-infinigen
UV_VERSION=0.12.18                  # PyPI, released 22 Sep 2026
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY" WENART_ASSETS="$ASSETS"
MODEL_KEY="${AUDIT_MODEL_KEY:-$("$PY" -c 'from wenart.assets.audit import load_config; print((load_config().get("ask") or {}).get("model_key", "agent"))')}"
COPY_LIB="$P4A/catalogue/catalog_library.json"
COPY_PH="$P4A/catalogue/catalog.json"
STEPS_TSV="$GROWTH/report/steps.tsv"
START_STAMP=$LOGS/library_growth-$JOB.start
JOB_T0=$(date +%s)
FAILED=()
declare -A BG_PID=() BG_T0=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] library_growth: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

# gr <step> [args]: a step of python -m wenart.assets growth run with the job's folders.
gr() {
  local step=$1; shift
  "$PY" -m wenart.assets growth run "$step" "$@" --growth "$GROWTH" --assets "$ASSETS" --p4 "$P4" \
    --p3 "$AUDIT_ROOT" ${WENART_DEADLINE:+--deadline "$WENART_DEADLINE"}
}
# au <step> [args]: python -m wenart.assets audit on the catalogue copies.
au() {
  local step=$1; shift
  "$PY" -m wenart.assets audit "$step" "$@" --out "$P4" --catalog "$COPY_LIB" --polyhaven "$COPY_PH"
}

time_left() {
  if [ -z "${WENART_DEADLINE:-}" ]; then echo 999999; else echo $(( ${WENART_DEADLINE%.*} - $(date +%s) )); fi
}

record() {  # name rc seconds [reason]: one row of steps.tsv (the reason: a failed step's last line)
  mkdir -p "$(dirname "$STEPS_TSV")"
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "${4:-}" >> "$STEPS_TSV"
  if [ "$2" -ne 0 ]; then FAILED+=("$1"); fi
}

# reason_of <log>: the last line a step printed that says something (the error trap's own line left out), tabs
# folded, at most 200 characters: the reason column of steps.tsv (round 3: P2's `preview 1 0` had none)
reason_of() {
  { grep -v -e '^[[:space:]]*$' -e 'library_growth: ERROR at line' "$1" 2>/dev/null || true; } | tail -n 1 \
    | tr '\t' ' ' | cut -c1-200
}

# need <seconds> <name>: false (and recorded) when too little time is left before WENART_DEADLINE.
need() {
  local left
  left=$(time_left)
  if [ "$left" -lt "$1" ]; then
    log "skip $2: $left s left before the deadline, it needs about $1 s (a second run finishes it)"
    record "$2 (no time)" 1 0
    return 1
  fi
  return 0
}

copy_results() {
  local g="$RESULTS/library/growth" a="$RESULTS/library/audit/p4" f
  mkdir -p "$g" "$a" "$RESULTS/logs"
  if [ -d "$GROWTH/report" ]; then
    find "$GROWTH/report" -maxdepth 1 -type f \( -name '*.json' -o -name '*.md' -o -name '*.tsv' \) \
      -exec cp -f {} "$g/" \; 2>/dev/null || log "copy of $GROWTH/report failed"
  fi
  if [ -d "$GROWTH/infinigen" ]; then
    mkdir -p "$g/infinigen"
    for f in jobs.json factories.json check.json setup.json; do
      [ -f "$GROWTH/infinigen/$f" ] && cp -f "$GROWTH/infinigen/$f" "$g/infinigen/" 2>/dev/null
    done
    for f in "$GROWTH"/infinigen/infinigen_*/result.json; do
      [ -f "$f" ] && cp -f "$f" "$g/infinigen/$(basename "$(dirname "$f")").json" 2>/dev/null
    done
  fi
  if [ -d "$P4A" ]; then      # small files only: the per-model sheets and every model file stay on the volume
    (cd "$P4A" && find . -path ./sheets -prune -o -type f \( -name '*.json' -o -name '*.md' -o -name '*.csv' \
      -o -name '*.jpg' \) -print0 | while IFS= read -r -d '' f; do
        mkdir -p "$a/$(dirname "$f")"; cp -f "$f" "$a/$f"; done) || log "copy of $P4A failed"
  fi
  # a JSON file over the runner's 20 MB download limit (COLLECT_MAX_FILE: the 3D Warehouse ingest records and the
  # catalogue copy with its 2,592 entries, pod of 23 Oct 2026) also goes as .json.gz (about a tenth of the size)
  find "$g" "$a" -type f -name '*.json' -size +15M -print0 2>/dev/null | while IFS= read -r -d '' f; do
    if [ ! -f "$f.gz" ] || [ "$f" -nt "$f.gz" ]; then
      gzip -c -6 "$f" > "$f.gz.part" && mv -f "$f.gz.part" "$f.gz" || log "gzip of $f failed"
    fi
  done
  for f in "$LOGS"/growth-*-"$JOB".log "$GROWTH"/*/work/convert_*.log "$LOGS"/vllm-*.log "$LOGS"/setup-polish-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

kill_tree() {  # pid: the process and its children (a background step's python and Blender processes)
  local c kids
  # `|| true` inside: ps exits 1 without children, and the ERR trap (set -E) would print into the substitution
  kids=$(ps -o pid= --ppid "$1" 2>/dev/null || true)
  for c in $kids; do
    if [[ "$c" =~ ^[0-9]+$ ]]; then kill_tree "$c"; fi
  done
  kill -TERM "$1" 2>/dev/null || true
}

kill_vllm() {
  local pid
  [ -f "$JOB_DIR/vllm.pid" ] || return 0
  pid=$(cat "$JOB_DIR/vllm.pid" 2>/dev/null) || pid=""
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    log "stopping vllm (pid $pid) left by a step"
    kill -TERM -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    sleep 10
    kill -KILL -- "-$pid" 2>/dev/null || true
  fi
  rm -f "$JOB_DIR/vllm.pid"
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$? name
  trap - ERR
  set +e
  for name in "${!BG_PID[@]}"; do
    log "stopping background step $name (pid ${BG_PID[$name]}) at the end of the job"
    kill_tree "${BG_PID[$name]}"
  done
  kill_vllm
  copy_results
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_step <name> <command...>: timed, its output also in $LOGS/growth-step-<name>-$JOB.log, failure recorded with
# the step's last line as the reason, the job goes on, results flushed.
run_step() {
  local name=$1; shift
  local t0 rc=0 out="$LOGS/growth-step-$name-$JOB.log" why="" tee_pid n
  t0=$(date +%s)
  log "step start: $name"
  { "$@" || rc=$?; } > >(tee "$out") 2>&1
  tee_pid=$!
  # the tee has written the step's last lines when it ends; at most 10 s (a child left running with the step's
  # stdout would keep it open: never wait for that)
  for n in $(seq 1 50); do kill -0 "$tee_pid" 2>/dev/null || break; sleep 0.2; done
  if [ "$rc" -ne 0 ]; then
    why=$(reason_of "$out")
    log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s: ${why:-no output}"
  else
    log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  fi
  record "$name" "$rc" "$(( $(date +%s) - t0 ))" "${why:-}"
  kill_vllm
  copy_results
  return 0
}

# start_bg <name> <command...>: a step in the background (its own log); join_bg <name> waits for that pid only.
start_bg() {
  local name=$1; shift
  BG_T0[$name]=$(date +%s)
  log "step start (background): $name, log $LOGS/growth-$name-$JOB.log"
  ( "$@" ) > "$LOGS/growth-$name-$JOB.log" 2>&1 &
  BG_PID[$name]=$!
}
join_bg() {
  local name=$1 rc=0 pid secs why
  pid="${BG_PID[$name]:-}"
  [ -n "$pid" ] || return 0
  wait "$pid" || rc=$?
  unset "BG_PID[$name]"
  secs=$(( $(date +%s) - ${BG_T0[$name]} ))
  log "step end: $name rc=$rc in $secs s (background)"
  tail -n 12 "$LOGS/growth-$name-$JOB.log" 2>/dev/null | sed "s/^/  [$name] /" || true
  if [ "$rc" -ne 0 ]; then why=$(reason_of "$LOGS/growth-$name-$JOB.log"); else why=""; fi
  record "$name" "$rc" "$secs" "$why"
  copy_results
  return 0
}
stop_bg() {  # a background step that is no longer needed
  local name=$1 pid
  pid="${BG_PID[$name]:-}"
  [ -n "$pid" ] || return 0
  log "stopping background step $name: not needed"
  kill_tree "$pid"
  wait "$pid" 2>/dev/null || true
  unset "BG_PID[$name]"
}

# --- Infinigen (background, capped) -----------------------------------------------------------------------------
infinigen_setup() {  # cap_end: Python 3.11 + the locked deps of the pinned commit on the container disk
  local cap_end=$1 t0 left head gpl
  t0=$(date +%s)
  if [ ! -x "$FAST/venv-uv/bin/uv" ]; then
    python3 -m venv "$FAST/venv-uv" && "$FAST/venv-uv/bin/pip" install -q "uv==$UV_VERSION" || return 1
  fi
  head=$(git -C "$IG_DIR" rev-parse HEAD 2>/dev/null) || head=""
  if [ "$head" != "$IG_COMMIT" ]; then
    rm -rf "$IG_DIR"
    git init -q "$IG_DIR" && git -C "$IG_DIR" remote add origin "$IG_URL" \
      && git -C "$IG_DIR" fetch -q --depth 1 origin "$IG_COMMIT" && git -C "$IG_DIR" checkout -q --detach FETCH_HEAD \
      || { echo "infinigen: fetch of $IG_COMMIT failed"; return 1; }
    head=$(git -C "$IG_DIR" rev-parse HEAD 2>/dev/null) || head=""
  fi
  [ "$head" = "$IG_COMMIT" ] || { echo "infinigen: checkout is $head, not $IG_COMMIT"; return 1; }
  # two submodules at the commits the tag pins (found by a trial import, docs/m12_tracks/P4.md): infinigen_gpl
  # (GPL-3.0; infinigen/assets/materials/__init__.py imports its snow surface) and OcMesher (BSD-3-Clause;
  # infinigen/terrain/core.py, reached through core.placement.camera). Run on the pod only, never copied.
  for sub in "infinigen/infinigen_gpl:$IG_GPL_COMMIT" "infinigen/OcMesher:$IG_OCMESHER_COMMIT"; do
    gpl=$(git -C "$IG_DIR/${sub%%:*}" rev-parse HEAD 2>/dev/null) || gpl=""
    if [ "$gpl" != "${sub##*:}" ]; then
      git -C "$IG_DIR" submodule update --init --depth 1 -- "${sub%%:*}" >/dev/null 2>&1 \
        || { echo "infinigen: the submodule ${sub%%:*} did not check out"; return 1; }
      gpl=$(git -C "$IG_DIR/${sub%%:*}" rev-parse HEAD 2>/dev/null) || gpl=""
    fi
    [ "$gpl" = "${sub##*:}" ] || { echo "infinigen: ${sub%%:*} is $gpl, not ${sub##*:}"; return 1; }
  done
  if ! command -v gcc >/dev/null 2>&1; then          # scikit-image 0.19.3 (uv.lock) has no cp311 wheel
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends build-essential >/dev/null \
      || echo "infinigen: no gcc (scikit-image is built from source)"
  fi
  left=$(( cap_end - $(date +%s) ))
  [ "$left" -gt 240 ] || { echo "infinigen: no time left for uv sync"; return 1; }
  if ! (cd "$IG_DIR" && UV_PROJECT_ENVIRONMENT="$IG_VENV" UV_PYTHON_INSTALL_DIR="$FAST/uv-python" \
      UV_CACHE_DIR="$FAST/uv-cache" INFINIGEN_MINIMAL_INSTALL=True \
      timeout --kill-after=30 "$left" "$FAST/venv-uv/bin/uv" sync --frozen --no-install-project --python 3.11); then
    # scikit-image 0.19.3 builds from source; Infinigen imports it for clouds, corals and terrain only
    echo "infinigen: uv sync failed; once more without scikit-image"
    left=$(( cap_end - $(date +%s) ))
    [ "$left" -gt 180 ] || { echo "infinigen: no time left for a second uv sync"; return 1; }
    (cd "$IG_DIR" && UV_PROJECT_ENVIRONMENT="$IG_VENV" UV_PYTHON_INSTALL_DIR="$FAST/uv-python" \
      UV_CACHE_DIR="$FAST/uv-cache" INFINIGEN_MINIMAL_INSTALL=True \
      timeout --kill-after=30 "$left" "$FAST/venv-uv/bin/uv" sync --frozen --no-install-project \
      --no-install-package scikit-image --python 3.11) || { echo "infinigen: uv sync failed"; return 1; }
  fi
  "$IG_VENV/bin/python" - "$GROWTH/infinigen/setup.json" "$IG_COMMIT" "$UV_VERSION" "$(( $(date +%s) - t0 ))" \
    "$IG_GPL_COMMIT" <<'PY' || { echo "infinigen: the venv does not import bpy"; return 1; }
import json, sys
import bpy
path, commit, uv, secs, gpl = sys.argv[1:6]
json.dump({"ok": True, "commit": commit, "tag": "v1.19.0", "python": sys.version.split()[0],
           "bpy": bpy.app.version_string, "uv": uv, "seconds": int(secs),
           "submodules": {"infinigen/infinigen_gpl": {"commit": gpl, "licence": "GPL-3.0 (run on the pod only)"},
                          "infinigen/OcMesher": {"commit": "bb895a01b8f574da10be1df470210df7463a75c7",
                                                 "licence": "BSD-3-Clause"}}},
          open(path, "w"), indent=1)
print("infinigen setup:", open(path).read())
PY
}

infinigen_part() {
  local cap_end out todo left rc=0 driver="$REPO/wenart/assets/audit/infinigen_driver.py"
  cap_end=$(( JOB_T0 + INFINIGEN_CAP_MIN * 60 ))
  if [ -n "${WENART_DEADLINE:-}" ] && [ "$cap_end" -gt $(( ${WENART_DEADLINE%.*} - 1800 )) ]; then
    cap_end=$(( ${WENART_DEADLINE%.*} - 1800 ))      # 30 min stay for the conversion, the audit and the copies
  fi
  mkdir -p "$GROWTH/infinigen"
  out=$(gr infinigen-plan) || return 1
  echo "$out"
  todo=$(sed -n 's/^growth infinigen-plan: todo \([0-9]*\).*/\1/p' <<< "$out")
  if [ "${todo:-1}" -eq 0 ]; then
    echo "infinigen: no job left to generate (resume): setup skipped"
    return 0
  fi
  infinigen_setup "$cap_end" || { echo "infinigen: setup failed"; return 1; }
  gr infinigen-list --repo "$IG_DIR" || return 1
  gr infinigen-plan || return 1
  (cd "$IG_DIR" && timeout 600 "$IG_VENV/bin/python" "$driver" check --repo "$IG_DIR" \
    --jobs "$GROWTH/infinigen/jobs.json" --out "$GROWTH/infinigen/check.json") \
    || echo "infinigen: a factory does not import (check.json); its jobs fail and are recorded"
  left=$(( cap_end - $(date +%s) ))
  [ "$left" -gt 150 ] || { echo "infinigen: no time left for the generation"; return 1; }
  (cd "$IG_DIR" && timeout --kill-after=60 "$left" "$IG_VENV/bin/python" "$driver" generate --repo "$IG_DIR" \
    --jobs "$GROWTH/infinigen/jobs.json" --deadline "$cap_end" --tex-res "$INFINIGEN_TEX_RES" --job-timeout 600 \
    --min-job-s 90) || rc=$?
  gr infinigen-plan || true
  return "$rc"
}

# --- the job ----------------------------------------------------------------------------------------------------
: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR" "$GROWTH/report" "$P4A" "$ASSETS"
: > "$STEPS_TSV"
log "job $JOB: growth $GROWTH, audit $P4 (P3 at $AUDIT_ROOT), assets $ASSETS, model key $MODEL_KEY," \
    "Infinigen cap $INFINIGEN_CAP_MIN min, deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
# The downloads (M12 about 8.5 GB; M13 about 18 GB more: ABO size grid 12.5, Poly Haven 2K 2.8, HSSD 2.4, ambientCG
# 0.4) and the converted GLBs need the room: stop before any download when less than GROWTH_MIN_FREE_GB is free
# (nothing is ever deleted to make room; CLAUDE.md).
free_gb=$(df -Pk "$WS" 2>/dev/null | awk 'NR == 2 {printf "%d", $4 / 1048576}')
if [ -n "$free_gb" ] && [ "$free_gb" -lt "${GROWTH_MIN_FREE_GB:-30}" ]; then
  log "only ${free_gb} GB free on $WS (need ${GROWTH_MIN_FREE_GB:-30} GB): no download; ask the user before" \
      "anything is deleted or the volume grows"
  exit 1
fi
log "volume: ${free_gb:-?} GB free on $WS"
if [ ! -f "$AUDIT_ROOT/audit/measure.json" ]; then
  log "no $AUDIT_ROOT/audit/measure.json: the P3 pending models cannot get their pass 2 (pods P2/P3 first);" \
      "the growth goes on"
fi

RENDER_ARGS=(--assets "$ASSETS" --work "$P4/work" --workers "$AUDIT_WORKERS" --blender "$WENART_BLENDER"
             --ids-file "$P4A/new_ids.json")
if [ -n "${WENART_DEADLINE:-}" ]; then RENDER_ARGS+=(--deadline "$WENART_DEADLINE"); fi

start_setup_check() {  # vLLM + the audit model, in the background from the start (the ask needs it last)
  start_bg setup-check env AGENT_MODELS="$MODEL_KEY" POLISH_RECOG_PARTS="vllm models" POLISH_MODE=final \
    POLISH_PHASES="check" bash scripts/pod_setup_polish.sh
}

# ask_step: one vLLM server session for the requests without a current answer; none left: no server, the setup
# step still running is stopped, not waited for.
ask_step() {
  local ask_plan
  ask_plan=$(gr ask --plan-only --model-key "$MODEL_KEY" 2>&1) || true
  echo "$ask_plan" | tail -n 3
  if grep -q '^growth ask: unanswered 0$' <<< "$ask_plan"; then
    log "ask: every request has a current answer: no server"
    stop_bg setup-check
  else
    join_bg setup-check
    if need 900 ask; then
      run_step ask env HF_HUB_OFFLINE=1 "$PY" -m wenart.assets growth run ask --model-key "$MODEL_KEY" \
        --job-dir "$JOB_DIR" --growth "$GROWTH" --assets "$ASSETS" --p4 "$P4" --p3 "$AUDIT_ROOT" \
        ${WENART_DEADLINE:+--deadline "$WENART_DEADLINE"}
    fi
  fi
}

# download_3dwh: the user's zip from Google Drive (GROWTH_ONLY=3dwh). A present zip of the Drive file's size is kept;
# a partial one is resumed (curl -C -; a server without ranges: the next try starts over). A download that is not the
# zip (an HTML page: the file is not shared as "anyone with the link") is moved aside, never deleted, and the step
# fails with the reason.
download_3dwh() {
  local dir="$WH_ROOT/zip" zip part url size t0 attempt rc
  zip="$dir/$WH_ZIP"
  part="$zip.part"
  url="https://drive.usercontent.google.com/download?id=${WH_FILE_ID}&export=download&confirm=t"
  mkdir -p "$dir"
  if [ -f "$zip" ] && [ "$(stat -c %s "$zip")" = "$WH_BYTES" ]; then
    echo "3dwh download: $zip present ($WH_BYTES bytes): kept"
    return 0
  fi
  t0=$(date +%s)
  for attempt in 1 2 3 4; do
    rc=0
    curl -L --fail --silent --show-error --retry 3 --retry-delay 5 --connect-timeout 30 -C - -o "$part" "$url" \
      || rc=$?
    [ "$rc" -eq 0 ] && break
    echo "3dwh download: attempt $attempt failed (curl exit $rc)"
    if [ "$rc" -eq 33 ] && [ -f "$part" ]; then         # no byte ranges: start over (our own partial file)
      mv -f "$part" "$part.norange-$(date -u +%Y%m%dT%H%M%SZ)"
    fi
    sleep $(( attempt * 10 ))
  done
  size=$(stat -c %s "$part" 2>/dev/null || echo 0)
  if [ "$size" != "$WH_BYTES" ]; then
    if [ -f "$part" ] && head -c 2048 "$part" | grep -qi '<html'; then
      mv -f "$part" "$part.html-$(date -u +%Y%m%dT%H%M%SZ)"
      echo "3dwh download: FAILED: Google Drive sent an HTML page, not the zip (is the file shared as 'anyone with" \
           "the link'?)"
    else
      echo "3dwh download: FAILED: $size of $WH_BYTES bytes after 4 attempts"
    fi
    return 1
  fi
  mv -f "$part" "$zip"
  echo "3dwh download: $WH_BYTES bytes in $(( $(date +%s) - t0 )) s -> $zip"
}

case "$GROWTH_ONLY" in
  all|hssd|3dwh) log "mode: GROWTH_ONLY=$GROWTH_ONLY" ;;
  *) log "GROWTH_ONLY='$GROWTH_ONLY' is not a mode of this job (all | hssd | 3dwh): nothing done"
     record "mode (GROWTH_ONLY=$GROWTH_ONLY unknown)" 1 0 "GROWTH_ONLY must be all, hssd or 3dwh"
     exit 1 ;;
esac

if [ "$GROWTH_ONLY" = hssd ]; then
  # --- GROWTH_ONLY=hssd (pod P2b): the HSSD layer alone; every other download and entry stays as it is ----------
  log "GROWTH_ONLY=hssd: ingest-hssd, refetch, catalogue --only hssd, render, code, ask, decide, write," \
      "vision-fields, gaps, coverage, report, GPU tests; every other download and catalogue entry stays as it is" \
      "on the volume"
  if [ -z "${HF_TOKEN:-}" ]; then
    log "ingest-hssd: SKIPPED: HF_TOKEN is not set in the environment (the RunPod secret hf_token): GROWTH_ONLY=hssd" \
        "has nothing to do; the HSSD layer needs the account that accepted the terms at" \
        "https://huggingface.co/datasets/hssd/hssd-models (D2)"
    record "ingest-hssd (skipped: no HF_TOKEN)" 1 0 "HF_TOKEN is not set"
    exit 1
  fi
  start_setup_check
  run_step ingest-hssd gr ingest --source hssd --workers 8 --token-env HF_TOKEN
  if ! compgen -G "$ASSETS/models/hssd/hssd_*.glb" > /dev/null; then
    log "GROWTH_ONLY=hssd: no HSSD model on the volume (the reason is in the ingest-hssd lines above): nothing to" \
        "audit; the rest of the library stays as it is"
    stop_bg setup-check
    run_step report gr report --steps "$STEPS_TSV"
    exit 1
  fi
  run_step refetch gr refetch
  run_step catalogue gr catalogue --only hssd
  if need 300 render; then run_step render au render "${RENDER_ARGS[@]}"; fi
  run_step code au code --work "$P4/work" --ids-file "$P4A/new_ids.json"
  ask_step
  run_step decide au decide --model-key "$MODEL_KEY" --ids-file "$P4A/new_ids.json"
  run_step write au write
  run_step vision-fields gr vision-fields --model-key "$MODEL_KEY"
  run_step gaps gr gaps
  run_step coverage gr size-grid
elif [ "$GROWTH_ONLY" = 3dwh ]; then
  # --- GROWTH_ONLY=3dwh (23 Oct 2026): the 3D Warehouse layer alone; every other entry stays as it is ------------
  log "GROWTH_ONLY=3dwh: download-3dwh, ingest-3dwh, catalogue --only 3dwh, render, code, ask, decide, write," \
      "vision-fields, sheets, gaps, coverage, preview, report, GPU tests; every other catalogue entry stays as it is"
  start_setup_check
  run_step download-3dwh download_3dwh
  run_step ingest-3dwh gr ingest --source 3dwh --library "$WH_ROOT" --workers "$WH_WORKERS"
  if ! compgen -G "$ASSETS/models/3dwh/3dwh_*.glb" > /dev/null; then
    log "GROWTH_ONLY=3dwh: no fixed 3D Warehouse model on the volume (the reason is in the download-3dwh and" \
        "ingest-3dwh lines above): nothing to audit"
    stop_bg setup-check
    run_step report gr report --steps "$STEPS_TSV"
    exit 1
  fi
  run_step catalogue gr catalogue --only 3dwh
  if need 300 render; then run_step render au render "${RENDER_ARGS[@]}"; fi
  run_step code au code --work "$P4/work" --ids-file "$P4A/new_ids.json"
  ask_step
  run_step decide au decide --model-key "$MODEL_KEY" --ids-file "$P4A/new_ids.json"
  run_step write au write
  run_step vision-fields gr vision-fields --model-key "$MODEL_KEY"
  run_step sheets au sheets
  run_step gaps gr gaps
  run_step coverage gr size-grid
  if need 300 preview; then run_step preview gr preview --blender "$WENART_BLENDER" --workers "$AUDIT_WORKERS"; fi
else
  # --- Milestone 13: the demands and the coverage before the growth, then the speed probe (foreground, CPU) ----
  run_step demands gr demands
  run_step size-grid gr size-grid
  run_step speed-probe timeout --kill-after=30 $(( GROWTH_PROBE_MIN * 60 )) "$PY" -m wenart.assets growth run \
    speed-probe --workers 8 --growth "$GROWTH" --assets "$ASSETS" --p4 "$P4" --p3 "$AUDIT_ROOT"

  start_setup_check
  start_bg infinigen infinigen_part
  start_bg ingest-polyhaven gr ingest --source polyhaven --size "$GROWTH_PH_SIZE"
  start_bg ingest-abo gr ingest --source abo --workers 8
  start_bg ingest-gso gr ingest --source gso --workers 8
  # --- Milestone 13 ingests (background; present files are kept) --------------------------------------------------
  if [ -n "${HF_TOKEN:-}" ]; then
    start_bg ingest-hssd gr ingest --source hssd --workers 8 --token-env HF_TOKEN
  else
    log "ingest-hssd: SKIPPED: HF_TOKEN is not set in the environment (the RunPod secret hf_token); the HSSD layer" \
        "needs the account that accepted the terms at https://huggingface.co/datasets/hssd/hssd-models (D2)"
    record "ingest-hssd (skipped: no HF_TOKEN)" 0 0
  fi
  start_bg ingest-abo-m13 gr ingest --source abo --m13 --workers 8
  start_bg ingest-polyhaven-m13 gr ingest --source polyhaven --m13 --size "$GROWTH_PH_SIZE"
  start_bg ingest-ambientcg gr ingest --source ambientcg --size "$GROWTH_PH_SIZE"

  join_bg ingest-gso
  run_step gso-licence gr gso-licence --workers 8
  run_step convert-gso gr convert --source gso --blender "$WENART_BLENDER"
  join_bg ingest-polyhaven
  join_bg ingest-abo
  join_bg ingest-hssd
  join_bg ingest-abo-m13
  join_bg ingest-polyhaven-m13
  join_bg ingest-ambientcg
  run_step refetch gr refetch
  run_step catalogue gr catalogue
  if need 600 render-a; then run_step render-a au render "${RENDER_ARGS[@]}"; fi

  join_bg infinigen
  run_step convert-infinigen gr convert --source infinigen --blender "$WENART_BLENDER"
  run_step catalogue-b gr catalogue
  if need 300 render-b; then run_step render-b au render "${RENDER_ARGS[@]}"; fi
  run_step code au code --work "$P4/work" --ids-file "$P4A/new_ids.json"
  ask_step
  run_step decide au decide --model-key "$MODEL_KEY" --ids-file "$P4A/new_ids.json"
  run_step write au write
  run_step vision-fields gr vision-fields --model-key "$MODEL_KEY"
  run_step pending gr pending --model-key "$MODEL_KEY"
  run_step sheets au sheets
  run_step gaps gr gaps
  run_step coverage gr size-grid
  if need 180 preview; then run_step preview gr preview --blender "$WENART_BLENDER"; fi
fi
run_step report gr report --steps "$STEPS_TSV"
if need 240 gpu-tests; then
  run_step gpu-tests env WENART_AUDIT_P4="$P4A" WENART_GROWTH="$GROWTH" WENART_ASSETS="$ASSETS" \
    AUDIT_MODEL_KEY="$MODEL_KEY" "$PY" -m pytest -m gpu tests/gpu/test_library.py -k growth -v -ra \
    --junitxml="$RESULTS/junit-library-growth.xml"
fi
gr report --steps "$STEPS_TSV" > /dev/null || true

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
