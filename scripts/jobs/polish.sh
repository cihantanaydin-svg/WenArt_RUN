#!/usr/bin/env bash
# Milestone 5 job: Cycles look, AI polish, change gate, final vision check, report and GPU tests
# (docs/milestone5.md §8.2). Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo,
# WENART_RESULTS and WENART_DEADLINE set, /workspace/venv has the CPU deps, Blender at
# /workspace/tools/blender/blender). Run 2 (§8.3) is split into pods that each end before
# WENART_DEADLINE; every pod resumes from the volume (polish attempts, gate results, check answers):
#
#   2a, one project per pod; the same command again until outputs/<p>/polish/polish_manifest.json
#   has "incomplete": false (synthetic-03, 57 views, likely needs two pods):
#   scripts/gpu_run.py run --job scripts/jobs/polish.sh --gpu 'RTX PRO 4500' --disk 130 --grace 600 \
#     --env POLISH_MODE=final --env POLISH_PHASES='look polish' --env POLISH_PROJECTS=synthetic-01
#   2b, both projects (again if the deadline cut it: the answers resume):
#   scripts/gpu_run.py run --job scripts/jobs/polish.sh --gpu 'RTX PRO 4500' --disk 130 --grace 600 \
#     --env POLISH_MODE=final --env POLISH_PHASES='check report tests'
#
# ('RTX PRO 4000' when the 4500 has no stock; never L4: diffusion there is 2-3x slower.) One pod
# for 'look polish check report tests' of both projects (87 views) does not fit: at run 0/0b's
# speeds the polish alone takes 3.5-5 h and the check of both VLMs about 70 min. --grace 600: the
# runner fetches the results with 8 parallel requests (one at a time took 0.81 s per file in runs
# 0/0b), so the 500-1000 files of a run arrive in about 2 min.
#
# Env: POLISH_PROJECTS (default "synthetic-01 synthetic-03"), POLISH_MODE smoke|sweep|final
# (default final), POLISH_PHASES (default per mode: smoke "look polish check", sweep "look
# controls polish gate report", final "look polish check report tests"; a check-only sweep run
# uses "check report tests"), RENDER_SAMPLES (128), FORCE_RENDER=1 (re-render), FORCE_POLISH=1
# (no reuse of polish attempts), CHECK_MODELS (check.yaml model keys, default "qwen glm"),
# SMOKE_VIEWS (cameras for the polish smoke, comma separated; default auto), CHECK_KINDS /
# CHECK_PREF_KINDS (override the image kinds of `vision_check run` / `preference`), POLISH_THREADS
# (CPU threads per process; default: the pod's cgroup CPU quota, see below).
#
# CPU threads: os.cpu_count() and /proc/meminfo show the host (run 0b: 112 CPUs, 251 GiB) while the
# pod runs under a cgroup CPU quota; numpy/OpenBLAS, OpenCV and torch each started 112 threads and
# the gate's CPU work ran 10-50x slower. The job exports OMP_NUM_THREADS, OPENBLAS_NUM_THREADS,
# MKL_NUM_THREADS, NUMEXPR_NUM_THREADS, VECLIB_MAXIMUM_THREADS and OPENCV_FOR_THREADS_NUM (OpenCV's
# own variable; it ignores OMP_NUM_THREADS) = the quota from /sys/fs/cgroup/cpu.max (v2) or
# cpu/cpu.cfs_quota_us / cpu.cfs_period_us (v1), rounded up, at most nproc; nproc without a quota.
# Every stage inherits them (torch sizes its intra-op pool from OMP_NUM_THREADS); the setup records
# them with the quota and the cgroup memory limit in setup_polish.json (pod_limits).
#
# Phases, always in this order (cwd /workspace/repo; PY=/workspace/venv/bin/python,
# POLISH_PY=/opt/wenart/venv-polish/bin/python):
#   setup     bash scripts/pod_setup_polish.sh (venv-polish, polish + gate models, vLLM + the two
#             VLMs, each only when a phase needs it); afterwards HF_HUB_OFFLINE=1
#   look      PY  wenart.style projects/<p> -> outputs/<p>/style.json; wenart.assets fetch (all
#                 projects first); wenart.blender.cli build --reuse from outputs/<p>/building_final.json;
#                 render --cameras all --samples $RENDER_SAMPLES --res 1920x1080 --exposure auto
#                 --white-balance auto [--force]
#   controls  PY  wenart.vision_check select-controls; render --hide-sets <from its CONTROL lines>
#                 --look-from outputs/<p>/renders/render_manifest.json -> outputs/<p>/controls/hide_<id>/
#   polish    POLISH_PY  wenart.polish run (final) | sweep --views auto --grid sweep (sweep) |
#                 smoke --views $SMOKE_VIEWS (smoke)
#   gate      POLISH_PY  wenart.gate calibrate
#   check     PY  wenart.vision_check expected, plan-crops; per model key of CHECK_MODELS: vLLM up
#                 (port 8001), run (+ preference; both with --workers = the server's sequences:
#                 2 below 40 GB of VRAM, 4 above), style-photo of the project photos and of
#                 tests/fixtures/style_photo_synthetic-03_salon.jpg -> check/style_photo_test.json),
#                 vLLM down; then combine, calibrate and wenart.style.photos combine of the project
#                 photos (-> check/style_photo_terms.json, read by the next look phase through
#                 wenart.style --photo-terms) and of the test photo
#   report    PY  wenart.report final (final) | sweep (sweep, smoke)
#   tests     PY  pytest -m gpu tests/gpu/test_render.py tests/gpu/test_check.py;
#             POLISH_PY  pytest -m gpu tests/gpu/test_polish.py tests/gpu/test_polish_backend.py
#                 (junit files into the results; the backend test loads the pinned polish models,
#                 which the setup therefore downloads for the tests phase too)
# vLLM flags as in bakeoff.sh / furnish.sh (vLLM 0.30.0): --limit-mm-per-prompt '{"image":2}'
# (render + source-plan crop), fp8 weights, 8192 context and 2 sequences below 40 GB of VRAM,
# VLLM_USE_FLASHINFER_SAMPLER=0, the per-model flags of check.yaml (GLM: --reasoning-parser
# glm45), the pinned --revision of check.yaml and --served-model-name <id> (the check's client
# asks for the repo id; with HF_HUB_OFFLINE vLLM resolves the model to its local snapshot).
#
# Deadline: pod_entry.sh exports WENART_DEADLINE (epoch s = start + MAX_RUNTIME_S - 900). The heavy
# CLIs read it and start nothing new after it; this job starts no new heavy stage (look, controls,
# polish, gate, check) after it, still runs report, tests and the results copy, and exits 1 with
# the skipped stages listed.
# Inputs: outputs/<p>/building_final.json on the volume; when the volume has none, the committed
# results/furniture/<p>/building_final.json is copied there (§1.1). style.json is regenerated
# before every build; a project whose style stage failed is not built.
# Results: copy_results mirrors the committed layout into $WENART_RESULTS: renders/<p>/ (+
# controls/hide_<id>/), polish/<p>/ (+ sweep/, smoke/), gate/<p>/, check/<p>/, final/<p>/: JSON,
# MD, *_preview.jpg, *_gate.jpg, *_check.jpg, *_plan.jpg, contact_*.jpg (each <= 300 KB), log
# tails (+ controls/render.log), junit. It runs after every stage, from the EXIT trap and every 300 s
# in the background (under flock): the pod_entry.sh watchdog stops the pod without signalling the
# job. Each copy takes only the files changed since the last one (stamp on the volume, 2 s back for
# 1 s timestamps), many files per cp: run 0b paid about 45 ms per file and every copy took every
# file again (25-40 min in run 2). The job's first copy and the one from the EXIT trap are full.
# From /workspace/logs (shared by every pod) only what this job wrote: its vLLM, pip and download
# logs and setup_polish.json; style_<n>.json only when written together with this style.json.
# Every stage is timed; a failing stage is recorded and the later stages still run (exit 1).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"           # WENART_WS / WENART_FAST: CPU tests only
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-polish}"
LOG=$LOGS/polish-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
FAST="${WENART_FAST:-/opt/wenart}"     # container disk (see pod_setup_polish.sh)
PY="${WENART_PY:-$WS/venv/bin/python}"
POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"
VENV_VLLM=$FAST/venv-vllm
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
VLM_PORT="${VLM_PORT:-8001}"
VLM_SERVER="http://127.0.0.1:$VLM_PORT/v1"
SERVER_WAIT_S="${SERVER_WAIT_S:-1500}"
SAMPLES="${RENDER_SAMPLES:-128}"
RES="${RENDER_RES:-1920x1080}"
MODE="${POLISH_MODE:-final}"
SMOKE_VIEWS="${SMOKE_VIEWS:-auto}"
STYLE_TEST_PHOTO=tests/fixtures/style_photo_synthetic-03_salon.jpg
CHECK_YAML=wenart/vision_check/check.yaml
COPY_EVERY_S="${POLISH_COPY_EVERY_S:-300}"
LOCK=$LOGS/polish-$JOB.copy.lock
START_STAMP=$LOGS/polish-$JOB.start     # files older than this were written by earlier jobs
COPY_STAMP=$LOGS/polish-$JOB.copied     # start of the last finished results copy (minus the overlap)
COPY_OVERLAP_S=2                        # stamps lie 2 s back: the volume's timestamps may have 1 s steps
CGROUP="${WENART_CGROUP:-/sys/fs/cgroup}"   # CPU tests only
FORCE_RENDER_ARG=()
if [ "${FORCE_RENDER:-0}" = "1" ]; then FORCE_RENDER_ARG=(--force); fi
FORCE_POLISH_ARG=()
if [ "${FORCE_POLISH:-0}" = "1" ]; then FORCE_POLISH_ARG=(--force); fi

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] polish: $*"; }

ALL_PHASES="look controls polish gate check report tests"
case "$MODE" in
  smoke) DEFAULT_PHASES="look polish check" ;;
  sweep) DEFAULT_PHASES="look controls polish gate report" ;;
  final) DEFAULT_PHASES="look polish check report tests" ;;
  *) log "unknown POLISH_MODE '$MODE' (smoke|sweep|final)"; exit 2 ;;
esac
read -r -a PHASES <<< "${POLISH_PHASES:-$DEFAULT_PHASES}"
for phase in "${PHASES[@]}"; do
  case " $ALL_PHASES " in
    *" $phase "*) ;;
    *) log "unknown phase '$phase' in POLISH_PHASES (known: $ALL_PHASES)"; exit 2 ;;
  esac
done
read -r -a PROJECTS <<< "${POLISH_PROJECTS:-synthetic-01 synthetic-03}"
read -r -a CHECK_KEYS <<< "${CHECK_MODELS:-qwen glm}"
export POLISH_MODE="$MODE" POLISH_PHASES="${PHASES[*]}" CHECK_MODELS="${CHECK_KEYS[*]}"
case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

FAILED=()      # stages that failed in this run
SKIPPED=()     # heavy stages not started because the deadline had passed
DONE=()        # stages that ran and succeeded in this run
ACTIVE=()      # projects with a building_final.json
POLISHED=()    # projects whose polish run stage ran in this run (final mode)
CHECKED=()     # projects whose vision-check stages ran in this run
VLLM_PID=""
COPY_PID=""

in_list() { local x=$1; shift; local f; for f in "$@"; do [ "$f" = "$x" ] && return 0; done; return 1; }
has_phase() { in_list "$1" "${PHASES[@]}"; }
stage_ok() { in_list "$1" "${DONE[@]}"; }
stage_failed() { in_list "$1" "${FAILED[@]}"; }

past_deadline() {
  [ -n "${WENART_DEADLINE:-}" ] || return 1
  [ "$(date +%s)" -ge "${WENART_DEADLINE%.*}" ]
}
deadline_left() {
  if [ -n "${WENART_DEADLINE:-}" ]; then echo "$(( ${WENART_DEADLINE%.*} - $(date +%s) )) s to the deadline"
  else echo "no deadline"; fi
}

# stamp <file>: an empty file whose mtime is the volume's own time minus COPY_OVERLAP_S, so a file
# written in the same second as the stamp still counts as newer (and the stamp shares the volume's
# clock with the files it is compared with).
stamp() {
  local t
  rm -f "$1" 2>/dev/null || true
  : > "$1" || return 1
  t=$(stat -c %Y "$1" 2>/dev/null) || return 0
  touch -d "@$(( t - COPY_OVERLAP_S ))" "$1" 2>/dev/null || true
}

# changed <file>: true when COPY_SINCE (set by copy_results) is empty or <file> is newer than it.
changed() { [ -z "${COPY_SINCE:-}" ] || [ "$1" -nt "$COPY_SINCE" ]; }

# copy_files <src dir> <dst dir>: JSON and markdown (< 8 MB), log tails and the small JPEGs that
# changed since COPY_SINCE (all of them when it is empty); one cp per batch, not one per file.
copy_files() {
  local src=$1 dst=$2 f
  [ -d "$src" ] || return 0
  local -a newer=() files=()
  if [ -n "${COPY_SINCE:-}" ]; then newer=(-newer "$COPY_SINCE"); fi
  mapfile -d '' files < <(find "$src" -maxdepth 1 -type f \( \
      \( \( -name '*.json' -o -name '*.md' \) -size -8000k \) -o \
      \( \( -name '*_preview.jpg' -o -name '*_gate.jpg' -o -name '*_check.jpg' -o -name '*_plan.jpg' \
         -o -name 'contact_*.jpg' \) -size -301k \) \) "${newer[@]}" -print0 2>/dev/null) || true
  if [ "${#files[@]}" -gt 0 ]; then
    mkdir -p "$dst" 2>/dev/null || return 0
    if cp -f -t "$dst/" "${files[@]}" 2>/dev/null; then COPIED=$(( COPIED + ${#files[@]} )); fi
  fi
  for f in "$src"/*.log; do
    if [ -f "$f" ] && changed "$f"; then
      mkdir -p "$dst" 2>/dev/null || return 0
      tail -n 400 "$f" > "$dst/$(basename "$f")" 2>/dev/null && COPIED=$(( COPIED + 1 ))
    fi
  done
  return 0
}

# copy_results [full]: small files only, in the layout of the committed results/<area>/<p>/ folders
# (full-size PNGs, EXR passes and model files stay on the volume / container disk). Only the files
# changed since the last finished copy; the job's first copy and 'full' (EXIT trap) copy all of them.
# Logs and setup_polish.json only when this job wrote them (/workspace/logs keeps every earlier pod's).
copy_results() {
  mkdir -p "$RESULTS" 2>/dev/null || return 0
  local p src d f COPY_SINCE="" COPIED=0
  if [ "${1:-}" != "full" ] && [ -f "$COPY_STAMP" ]; then COPY_SINCE=$COPY_STAMP; fi
  stamp "$COPY_STAMP.next" 2>/dev/null || true      # before the scan: files written during it go next time
  for p in "${PROJECTS[@]}"; do
    src=$REPO/outputs/$p
    [ -d "$src" ] || continue
    copy_files "$src/renders" "$RESULTS/renders/$p"
    copy_files "$src/scene" "$RESULTS/renders/$p"
    # style_<n>.json (a brief with several styles) only when written together with style.json: an
    # older brief's extra profile stays on the volume.
    for f in "$src"/style*.json; do
      [ -f "$f" ] && [ -f "$src/style.json" ] && changed "$f" || continue
      if [ "$f" = "$src/style.json" ] || ! [ "$f" -ot "$src/style.json" ]; then
        mkdir -p "$RESULTS/renders/$p" 2>/dev/null && cp -f "$f" "$RESULTS/renders/$p/" 2>/dev/null \
          && COPIED=$(( COPIED + 1 ))
      fi
    done
    copy_files "$src/controls" "$RESULTS/renders/$p/controls"     # render.log of the control renders
    for d in "$src"/controls/hide_*; do
      if [ -d "$d" ]; then copy_files "$d" "$RESULTS/renders/$p/controls/$(basename "$d")"; fi
    done
    copy_files "$src/polish" "$RESULTS/polish/$p"
    copy_files "$src/polish/sweep" "$RESULTS/polish/$p/sweep"
    copy_files "$src/polish/smoke" "$RESULTS/polish/$p/smoke"
    copy_files "$src/gate" "$RESULTS/gate/$p"
    copy_files "$src/check" "$RESULTS/check/$p"
    copy_files "$src/final" "$RESULTS/final/$p"
  done
  mkdir -p "$RESULTS/logs" 2>/dev/null || true
  for f in "$LOGS"/vllm-*.log "$LOGS"/setup-polish-*.log "$LOGS"/hf-download-*.log "$LOGS/setup_polish.json"; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ] && changed "$f"; then
      case "$f" in
        *.json) cp -f "$f" "$RESULTS/" 2>/dev/null || true ;;
        *) tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true ;;
      esac
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  mv -f "$COPY_STAMP.next" "$COPY_STAMP" 2>/dev/null || true
  if [ -n "$COPY_SINCE" ]; then
    log "results copied to $RESULTS: $COPIED changed file(s)"
  else
    log "results copied to $RESULTS (full copy): $COPIED file(s)"
  fi
}

# copy_results_locked [wait_s] [full]: one copy at a time (stages, the background loop, the EXIT trap).
copy_results_locked() {
  if command -v flock >/dev/null 2>&1; then
    ( flock -w "${1:-120}" 9 || { log "results copy busy, skipped"; exit 0; }; copy_results "${2:-}" ) 9>"$LOCK"
  else
    copy_results "${2:-}"
  fi
}

# cpu_budget: the CPUs this pod may use: its cgroup CPU quota (v2 cpu.max '<quota> <period>' or
# 'max ...'; v1 cpu/cpu.cfs_quota_us and cpu.cfs_period_us, -1 = none) rounded up, at most the CPUs
# this process may run on (nproc, without the OMP_* variables nproc honours), at least 1. Run 0b:
# os.cpu_count() saw the host's 112 CPUs; numpy/OpenBLAS, OpenCV and torch each started that many
# threads under a much smaller quota and the gate's CPU work ran 10-50x slower.
cpu_budget() {
  local n quota="" period=""
  n=$(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc 2>/dev/null) || n=1
  if [ -r "$CGROUP/cpu.max" ]; then
    read -r quota period < "$CGROUP/cpu.max" || true
  elif [ -r "$CGROUP/cpu/cpu.cfs_quota_us" ] && [ -r "$CGROUP/cpu/cpu.cfs_period_us" ]; then
    quota=$(cat "$CGROUP/cpu/cpu.cfs_quota_us" 2>/dev/null) || quota=""
    period=$(cat "$CGROUP/cpu/cpu.cfs_period_us" 2>/dev/null) || period=""
  fi
  if [[ "$quota" =~ ^[0-9]+$ ]] && [[ "$period" =~ ^[0-9]+$ ]] && [ "$quota" -gt 0 ] && [ "$period" -gt 0 ]; then
    local q=$(( (quota + period - 1) / period ))
    if [ "$q" -lt "$n" ]; then n=$q; fi
  fi
  if ! [[ "$n" =~ ^[0-9]+$ ]] || [ "$n" -lt 1 ]; then n=1; fi
  echo "$n"
}

# set_threads: export the thread budget (POLISH_THREADS, else cpu_budget) to every stage: OpenMP
# (torch intra-op, libgomp), OpenBLAS (numpy), MKL (torch on x86), numexpr, Accelerate, and OpenCV
# (OPENCV_FOR_THREADS_NUM; opencv-python-headless 4.14.0.94 ignores OMP_NUM_THREADS, checked
# 2 Oct 2026). WENART_CPU_THREADS goes into setup_polish.json.
set_threads() {
  local n="${POLISH_THREADS:-}" src="POLISH_THREADS" quota="none"
  if ! [[ "$n" =~ ^[1-9][0-9]*$ ]]; then
    if [ -n "$n" ]; then log "POLISH_THREADS '$n' is not a positive number: ignored"; fi
    n=$(cpu_budget); src="cgroup CPU quota / nproc"
  fi
  if [ -r "$CGROUP/cpu.max" ]; then quota="cpu.max '$(cat "$CGROUP/cpu.max" 2>/dev/null)'"
  elif [ -r "$CGROUP/cpu/cpu.cfs_quota_us" ]; then
    quota="cfs_quota_us $(cat "$CGROUP/cpu/cpu.cfs_quota_us" 2>/dev/null)"
    quota+=" / cfs_period_us $(cat "$CGROUP/cpu/cpu.cfs_period_us" 2>/dev/null)"
  fi
  local cpus; cpus=$(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc 2>/dev/null) || cpus="?"
  export WENART_CPU_THREADS=$n OMP_NUM_THREADS=$n OPENBLAS_NUM_THREADS=$n MKL_NUM_THREADS=$n \
    NUMEXPR_NUM_THREADS=$n VECLIB_MAXIMUM_THREADS=$n OPENCV_FOR_THREADS_NUM=$n
  log "CPU budget: $n thread(s) per process (from $src; $quota; nproc $cpus," \
      "host $(nproc --all 2>/dev/null || echo ?)): OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/OPENCV_FOR_THREADS_NUM=$n"
}

copy_loop() {
  trap - ERR
  set +e
  while true; do
    sleep "$COPY_EVERY_S" </dev/null >/dev/null 2>&1
    copy_results_locked 60
  done
}

stop_server() {
  if [ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null; then
    log "stopping vllm (pid $VLLM_PID)"
    kill "$VLLM_PID" 2>/dev/null || true
    for _ in $(seq 1 30); do kill -0 "$VLLM_PID" 2>/dev/null || break; sleep 2; done
    kill -9 "$VLLM_PID" 2>/dev/null || true
  fi
  VLLM_PID=""
}

on_error() { log "ERROR at line $1"; exit 1; }
trap 'on_error $LINENO' ERR
on_exit() {
  trap - ERR
  stop_server
  if [ -n "$COPY_PID" ]; then
    kill "$COPY_PID" 2>/dev/null || true
    wait "$COPY_PID" 2>/dev/null || true
  fi
  copy_results_locked 300 full      # one full copy at the end, in case a timestamp misled a copy
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_stage <name> <command...>: timed, failure recorded, job continues, results flushed.
run_stage() {
  local name=$1; shift
  local t0; t0=$(date +%s)
  log "stage start: $name"
  local rc=0
  "$@" || rc=$?      # exempt from errexit and the ERR trap
  log "stage end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); else DONE+=("$name"); fi
  copy_results_locked
  return 0
}

# heavy <name> <command...>: a run_stage that is not started once the deadline has passed.
heavy() {
  local name=$1; shift
  if past_deadline; then
    log "deadline passed ($(deadline_left)): $name not started"
    SKIPPED+=("$name")
    return 0
  fi
  run_stage "$name" "$@"
}

# capture_to <file> <command...>: the command's stdout into <file> (and the log); its exit code.
capture_to() {
  local file=$1; shift
  mkdir -p "$(dirname "$file")"
  local rc=0
  "$@" > "$file" || rc=$?
  cat "$file"
  return "$rc"
}

# hide_sets_from <select-controls output>: 'cam:id;cam:id+plug;...' from the lines
# CONTROL\t<id>\t<camera>\t<0|1>\t<dir> (docs/milestone5.md §5.5).
hide_sets_from() {
  awk -F'\t' '$1 == "CONTROL" && NF >= 4 { printf "%s%s:%s%s", sep, $3, $2, ($4 == "1" ? "+plug" : ""); sep = ";" }' "$1"
}

# polish_venv_ready: venv-polish exists and pod_setup_polish.sh stamped it good on this pod.
polish_venv_ready() {
  local venv; venv=$(dirname "$(dirname "$POLISH_PY")")
  [ -x "$POLISH_PY" ] && compgen -G "$venv/.polish-*" >/dev/null
}

gpu_mem_mib() { nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo 0; }

# check_field <model key> <field>: one value of check.yaml models.<key> (empty when unset).
check_field() {
  "$PY" - "$CHECK_YAML" "$1" "$2" <<'PY'
import sys

import yaml

with open(sys.argv[1], encoding="utf-8") as fh:
    value = yaml.safe_load(fh)["models"][sys.argv[2]].get(sys.argv[3])
print("" if value is None else value)
PY
}

# server_seqs: sequences the vLLM server takes at once (2 below 40 GB of VRAM, else 4); `vision_check
# run` and `preference` send that many calls at once (--workers).
server_seqs() {
  local mem; mem=$(gpu_mem_mib)
  if [ "${mem:-0}" -lt 40000 ]; then echo 2; else echo 4; fi
}

# Size flags as in bakeoff.sh: fp8 weights, 8192 context and 2 sequences below 40 GB of VRAM.
server_args() {
  if [ "$(server_seqs)" = "2" ]; then
    echo "--quantization fp8 --max-model-len 8192 --max-num-seqs 2"
  else
    echo "--max-model-len 16384 --max-num-seqs 4"
  fi
}

# start_server <model key>: `vllm serve` for check.yaml models.<key>; waits for /health.
start_server() {
  local key=$1 model rev flags extra slog t0
  model=$(check_field "$key" id) || model=""
  if [ -z "$model" ]; then log "no model '$key' in $CHECK_YAML"; return 1; fi
  rev=$(check_field "$key" revision) || rev=""
  flags=$(check_field "$key" server_flags) || flags=""
  extra=$(server_args)
  local -a rev_arg=()
  if [ -n "$rev" ]; then rev_arg=(--revision "$rev"); fi
  slog="$LOGS/vllm-$key.log"
  log "starting vllm serve $model ${rev_arg[*]} --port $VLM_PORT $flags $extra (log $slog)"
  # VLLM_USE_FLASHINFER_SAMPLER=0: FlashInfer's sampler failed on sm_120 (bake-off run 3).
  # shellcheck disable=SC2086
  VLLM_USE_FLASHINFER_SAMPLER=0 "$VENV_VLLM/bin/vllm" serve "$model" "${rev_arg[@]}" --served-model-name "$model" \
    --port "$VLM_PORT" --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization 0.90 $flags $extra \
    > "$slog" 2>&1 &
  VLLM_PID=$!
  t0=$(date +%s)
  while true; do
    if curl -sf -m 5 "http://127.0.0.1:$VLM_PORT/health" >/dev/null 2>&1; then
      log "vllm ready for $model after $(( $(date +%s) - t0 )) s"
      return 0
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
      log "vllm exited early for $model; last log lines:"; tail -n 40 "$slog"; VLLM_PID=""; return 1
    fi
    if [ $(( $(date +%s) - t0 )) -gt "$SERVER_WAIT_S" ]; then
      log "vllm not ready after ${SERVER_WAIT_S}s for $model"; stop_server; return 1
    fi
    if past_deadline; then
      log "deadline passed while vllm was starting for $model"; stop_server; return 1
    fi
    sleep 10
  done
}

# ensure_buildings: every project needs outputs/<p>/building_final.json; the committed
# results/furniture/<p>/building_final.json is copied there when the volume has none (§1.1).
ensure_buildings() {
  local p dst src
  for p in "${PROJECTS[@]}"; do
    dst=outputs/$p/building_final.json
    src=results/furniture/$p/building_final.json
    if [ ! -f "$dst" ]; then
      if [ -f "$src" ]; then
        mkdir -p "outputs/$p"
        cp -f "$src" "$dst"
        log "$p: no $dst on the volume; copied the committed $src"
      else
        log "$p: neither $dst nor $src exists: project skipped"
        FAILED+=("building-$p")
        continue
      fi
    fi
    ACTIVE+=("$p")
  done
}

phase_look() {
  local p out terms
  for p in "${ACTIVE[@]}"; do
    # Agreed terms of the project's style photos (check phase of an earlier run, §6) fill only the
    # slots the brief leaves open.
    terms=outputs/$p/check/style_photo_terms.json
    local -a terms_arg=()
    if [ -f "$terms" ]; then terms_arg=(--photo-terms "$terms"); fi
    heavy "style-$p" "$PY" -m wenart.style "projects/$p" --out "outputs/$p/style.json" "${terms_arg[@]}"
  done
  for p in "${ACTIVE[@]}"; do      # textures and HDRIs of every project before any build
    stage_ok "style-$p" || continue
    heavy "assets-$p" "$PY" -m wenart.assets fetch --style "outputs/$p/style.json" --assets "$ASSETS" --size 2k
  done
  for p in "${ACTIVE[@]}"; do
    out=outputs/$p
    if ! stage_ok "style-$p"; then log "$p: style.json not regenerated in this run: build and render skipped"; continue; fi
    heavy "build-$p" "$PY" -m wenart.blender.cli build --building "$out/building_final.json" \
      --style "$out/style.json" --assets "$ASSETS" --out "$out/scene" --preview-samples 32 --reuse
    if ! stage_ok "build-$p"; then
      log "$p: no build in this run (failed or deadline): render skipped (scene.blend could be stale)"; continue
    fi
    heavy "render-$p" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" --out "$out/renders" \
      --cameras all --samples "$SAMPLES" --res "$RES" --exposure auto --white-balance auto "${FORCE_RENDER_ARG[@]}"
    if [ -f "$out/renders/render.log" ]; then
      grep -E "^(DEVICE|RENDERED|RERENDER|SKIP)" "$out/renders/render.log" | tail -n 5 || true
    fi
  done
}

phase_controls() {
  local p out ctl sets
  for p in "${ACTIVE[@]}"; do
    out=outputs/$p
    if [ ! -f "$out/renders/render_manifest.json" ] || [ ! -f "$out/scene/scene.blend" ]; then
      log "$p: no renders or scene.blend: controls skipped"; FAILED+=("controls-$p"); continue
    fi
    ctl=$out/check/select_controls.txt
    heavy "select-controls-$p" capture_to "$ctl" "$PY" -m wenart.vision_check select-controls --project-out "$out"
    stage_ok "select-controls-$p" || continue
    sets=$(hide_sets_from "$ctl")
    if [ -z "$sets" ]; then log "$p: no control selected, no hidden renders"; continue; fi
    log "$p: hide sets $sets"
    heavy "controls-render-$p" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" \
      --out "$out/controls" --hide-sets "$sets" --look-from "$out/renders/render_manifest.json" \
      --samples "$SAMPLES" --res "$RES"
  done
}

phase_polish() {
  local p
  local -a args=()
  case "$MODE" in
    final) args=(run) ;;
    sweep) args=(sweep --views auto --grid sweep) ;;
    smoke) args=(smoke --views "$SMOKE_VIEWS") ;;
  esac
  if ! polish_venv_ready; then
    log "venv-polish is not ready (pod_setup_polish.sh did not stamp it): polish skipped"
    FAILED+=("polish-venv"); return 0
  fi
  if stage_failed setup-polish; then log "warning: setup-polish failed (see setup_polish.json); trying the polish anyway"; fi
  for p in "${ACTIVE[@]}"; do
    heavy "polish-$p" env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      "$POLISH_PY" -m wenart.polish "${args[@]}" --project-out "outputs/$p" "${FORCE_POLISH_ARG[@]}"
    if [ "$MODE" = "final" ] && in_list "polish-$p" "${DONE[@]}" "${FAILED[@]}"; then POLISHED+=("$p"); fi
  done
}

phase_gate() {
  local p
  if ! polish_venv_ready; then
    log "venv-polish is not ready: gate calibration skipped"; FAILED+=("gate-venv"); return 0
  fi
  for p in "${ACTIVE[@]}"; do
    heavy "gate-$p" env PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      "$POLISH_PY" -m wenart.gate calibrate --project-out "outputs/$p"
  done
}

phase_check() {
  local p out key kinds pref workers
  case "$MODE" in
    final) kinds=cycles,polished; pref=polished ;;
    sweep) kinds=cycles,controls,plan_ab; pref=sweep ;;
    smoke) kinds=cycles; pref="" ;;
  esac
  kinds=${CHECK_KINDS:-$kinds}
  pref=${CHECK_PREF_KINDS-$pref}
  for p in "${ACTIVE[@]}"; do
    heavy "expected-$p" "$PY" -m wenart.vision_check expected --project-out "outputs/$p"
    heavy "plan-crops-$p" "$PY" -m wenart.vision_check plan-crops --project-out "outputs/$p"
  done
  # One server at a time (each holds 90 % of the VRAM); every project per server.
  for key in "${CHECK_KEYS[@]}"; do
    if past_deadline; then log "deadline passed: no vllm server for $key"; SKIPPED+=("check-$key"); continue; fi
    if ! start_server "$key"; then FAILED+=("vllm-serve-$key"); continue; fi
    workers=$(server_seqs)
    for p in "${ACTIVE[@]}"; do
      out=outputs/$p
      heavy "check-run-$key-$p" "$PY" -m wenart.vision_check run --project-out "$out" \
        --model-key "$key" --server "$VLM_SERVER" --kinds "$kinds" --workers "$workers"
      if [ -n "$pref" ]; then
        heavy "preference-$key-$p" "$PY" -m wenart.vision_check preference --project-out "$out" \
          --model-key "$key" --server "$VLM_SERVER" --kinds "$pref" --workers "$workers"
      fi
      heavy "style-photo-$key-$p" "$PY" -m wenart.vision_check style-photo --project-out "$out" \
        --model-key "$key" --server "$VLM_SERVER"
      heavy "style-photo-test-$key-$p" "$PY" -m wenart.vision_check style-photo --project-out "$out" \
        --model-key "$key" --server "$VLM_SERVER" --photo "$STYLE_TEST_PHOTO" --out "$out/check/style_photo_test.json"
      in_list "$p" "${CHECKED[@]}" || CHECKED+=("$p")
    done
    stop_server
  done
  # Combining the stored answers is CPU work of seconds: it runs even after the deadline, so
  # the report sees every answer that was given.
  for p in "${ACTIVE[@]}"; do
    out=outputs/$p
    if ! compgen -G "$out/check/answers_*.json" >/dev/null; then log "$p: no vision-check answers to combine"; continue; fi
    run_stage "check-combine-$p" "$PY" -m wenart.vision_check combine --project-out "$out"
    run_stage "check-calibrate-$p" "$PY" -m wenart.vision_check calibrate --project-out "$out"
    if [ -f "$out/check/style_photos.json" ]; then
      run_stage "style-photos-terms-$p" "$PY" -m wenart.style.photos combine "$out/check/style_photos.json" \
        --out "$out/check/style_photo_terms.json"
    fi
    if [ -f "$out/check/style_photo_test.json" ]; then
      run_stage "style-photo-terms-$p" "$PY" -m wenart.style.photos combine "$out/check/style_photo_test.json" \
        --out "$out/check/style_photo_test_terms.json"
    fi
  done
}

phase_report() {
  local p kind=sweep
  if [ "$MODE" = "final" ]; then kind=final; fi
  for p in "${ACTIVE[@]}"; do
    run_stage "report-$p" "$PY" -m wenart.report "$kind" --project-out "outputs/$p"
  done
}

phase_tests() {
  local p
  local -a render=() check=() polish=()
  for p in "${ACTIVE[@]}"; do
    if [ -f "outputs/$p/renders/render_manifest.json" ]; then render+=("$p"); fi
    if in_list "$p" "${CHECKED[@]}" || [ -f "outputs/$p/check/check_manifest.json" ]; then check+=("$p"); fi
    if in_list "$p" "${POLISHED[@]}" || [ -f "outputs/$p/polish/polish_manifest.json" ]; then polish+=("$p"); fi
  done
  export WENART_OUTPUTS="$REPO/outputs"
  export RENDER_TEST_PROJECTS="${render[*]}" CHECK_TEST_PROJECTS="${check[*]}" POLISH_TEST_PROJECTS="${polish[*]}"
  log "GPU tests: render [${render[*]}], check [${check[*]}] (models ${CHECK_MODELS}), polish [${polish[*]}]"
  if [ "${#render[@]}" -gt 0 ] || [ "${#check[@]}" -gt 0 ]; then
    run_stage gpu-tests-render-check "$PY" -m pytest -m gpu tests/gpu/test_render.py tests/gpu/test_check.py \
      -v -ra --junitxml="$RESULTS/junit-render-check.xml"
  else
    log "no rendered or checked project: render/check GPU tests skipped"
  fi
  if [ "${#polish[@]}" -eq 0 ]; then
    log "no polished project: polish GPU tests skipped"
  elif [ ! -x "$POLISH_PY" ]; then
    log "no venv-polish ($POLISH_PY): polish GPU tests not run"; FAILED+=("gpu-tests-polish")
  else
    # test_polish_backend.py loads the pinned polish models (about 20 GiB of VRAM) and forces the CUDA
    # OOM retry: it runs here, after the check phase stopped its vLLM server (the GPU is free).
    run_stage gpu-tests-polish "$POLISH_PY" -m pytest -m gpu tests/gpu/test_polish.py tests/gpu/test_polish_backend.py \
      -v -ra --junitxml="$RESULTS/junit-polish.xml"
  fi
}

stamp "$START_STAMP" || log "warning: no start stamp $START_STAMP: earlier jobs' logs may be copied"
rm -f "$COPY_STAMP" "$COPY_STAMP.next"      # the job's first results copy is a full one
cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" outputs
log "job $JOB: mode $MODE, phases: ${PHASES[*]}; projects: ${PROJECTS[*]}; check models: ${CHECK_KEYS[*]};" \
    "samples $SAMPLES, res $RES; $(deadline_left)"
set_threads
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
copy_loop &
COPY_PID=$!

ensure_buildings
run_stage setup-polish bash scripts/pod_setup_polish.sh
export HF_HUB_OFFLINE=1       # every model is in HF_HOME now; nothing is fetched behind our back

if [ "${#ACTIVE[@]}" -eq 0 ]; then
  log "no project with a building_final.json: nothing to do"
else
  if has_phase look; then phase_look; fi
  if has_phase controls; then phase_controls; fi
  if has_phase polish; then phase_polish; fi
  if has_phase gate; then phase_gate; fi
  if has_phase check; then phase_check; fi
  if has_phase report; then phase_report; fi
  if has_phase tests; then phase_tests; fi
fi

copy_results_locked
if [ "${#SKIPPED[@]}" -gt 0 ]; then
  log "INCOMPLETE: the deadline stopped ${#SKIPPED[@]} stage(s): ${SKIPPED[*]}"
fi
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
fi
if [ "${#FAILED[@]}" -gt 0 ] || [ "${#SKIPPED[@]}" -gt 0 ]; then
  exit 1
fi
log "all stages ok"
