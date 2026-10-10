#!/usr/bin/env bash
# Milestone 12 pod P2: the library audit, part A (docs/milestone12.md §6.1 D21, §8): every furniture and decor model of
# the catalogue rendered at its catalogue scale (4 views, the 1.75 m person, the 0.45 m seat bar, a metric grid, the
# dimensions printed), its mesh measured, every texture set as a 1 m sample with a 10 cm grid, then the code checks.
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE
# set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender). The watchdog and the self-stop
# are pod_entry.sh's.
#
#   scripts/gpu_run.py run --job scripts/jobs/library_audit_render.sh --gpu 'RTX PRO 6000' --max-minutes 110 \
#     --purpose "M12 P2: library audit A (renders with scale reference, mesh and code checks)"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. models: the Poly Haven models of catalog.json into the assets folder (idempotent, CC0, the catalogue's own
#      models: no growth download); the library GLBs are on the volume already (/workspace/assets/models/<source>/);
#   2. render: python -m wenart.assets audit render (AUDIT_WORKERS Blender processes, resumable: a model whose
#      measurement is current is not rendered again; the sheets are composed after Blender), after a smoke render of
#      4 models (one per source) that stops the job when the Blender side fails;
#   3. code: python -m wenart.assets audit code (the checks with the measurements);
#   4. gpu-tests: pytest -m gpu tests/gpu/test_library.py -k audit_render.
# The audit folder lives on the volume (AUDIT_ROOT, default /workspace/library-audit: views and measurements in
# work/, the sheets and tables in audit/); after every step its small files are copied to
# $WENART_RESULTS/library/audit (sheets, measure.json, code.json, render_plan.json, textures; never the views), so a
# cut pod keeps what it finished and the same command resumes.
#
# Env (all optional): AUDIT_ROOT, AUDIT_WORKERS (default 3), AUDIT_TYPES (comma list), AUDIT_TEXTURES (1 = render the
# texture samples, default 1), WENART_ASSETS (default /workspace/assets).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-library_audit_render}"
LOG=$LOGS/library_audit_render-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
PY="${WENART_PY:-$WS/venv/bin/python}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
AUDIT_ROOT="${AUDIT_ROOT:-$WS/library-audit}"
WORK="$AUDIT_ROOT/work"
AUDIT_WORKERS="${AUDIT_WORKERS:-3}"
AUDIT_TEXTURES="${AUDIT_TEXTURES:-1}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_ASSETS="$ASSETS"
export WENART_AUDIT="$RESULTS/library/audit"
FAILED=()
START_STAMP=$LOGS/library_audit_render-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] library_audit_render: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

# copy_results: the audit's small files to $RESULTS/library/audit (cp -f, idempotent; the views stay on the volume).
copy_results() {
  local src="$AUDIT_ROOT/audit" dst="$RESULTS/library/audit"
  mkdir -p "$dst" "$RESULTS/logs"
  if [ -d "$src" ]; then
    (cd "$src" && find . -path ./work -prune -o -type f \( -name '*.json' -o -name '*.md' -o -name '*.csv' \
      -o -name '*.jpg' \) -print0 | while IFS= read -r -d '' f; do
        mkdir -p "$dst/$(dirname "$f")"; cp -f "$f" "$dst/$f"; done) || log "copy of $src failed"
  fi
  for f in "$WORK"/jobs/blender_*.log; do
    [ -f "$f" ] && tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
  done
  for f in "$WORK"/jobs/status_*.json; do
    [ -f "$f" ] && cp -f "$f" "$RESULTS/logs/" 2>/dev/null || true
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  copy_results
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_step <name> <command...>: timed, failure recorded, the job goes on, results flushed.
run_step() {
  local name=$1; shift
  local t0 rc=0
  t0=$(date +%s)
  log "step start: $name"
  "$@" || rc=$?
  log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  copy_results
  return 0
}

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR" "$AUDIT_ROOT/audit" "$WORK" "$ASSETS"
log "job $JOB: audit root $AUDIT_ROOT, assets $ASSETS, workers $AUDIT_WORKERS, types [${AUDIT_TYPES:-all}]," \
    "textures $AUDIT_TEXTURES, deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

RENDER_ARGS=(--assets "$ASSETS" --out "$AUDIT_ROOT" --work "$WORK" --workers "$AUDIT_WORKERS"
             --blender "$WENART_BLENDER")
if [ -n "${WENART_DEADLINE:-}" ]; then RENDER_ARGS+=(--deadline "$WENART_DEADLINE"); fi
if [ -n "${AUDIT_TYPES:-}" ]; then RENDER_ARGS+=(--types "$AUDIT_TYPES"); fi
if [ "$AUDIT_TEXTURES" = "1" ]; then RENDER_ARGS+=(--textures); fi

# the Poly Haven ids of catalog.json only (the library GLBs are no Poly Haven assets)
read -r -a PH_IDS <<< "$("$PY" -c 'from wenart.assets.audit import items as I
print(" ".join(i["id"] for i in I.load_items() if i["catalog"] == "polyhaven"))')"
run_step models "$PY" -m wenart.assets models fetch --assets "$ASSETS" --size 1k --ids "${PH_IDS[@]}"
run_step plan "$PY" -m wenart.assets audit render "${RENDER_ARGS[@]}" --plan
# smoke: 4 models (one per source) before the full run; a Blender side that fails here stops the pod early
smoke_rc=0
"$PY" -m wenart.assets audit render "${RENDER_ARGS[@]}" --smoke 4 || smoke_rc=$?
copy_results
if [ "$smoke_rc" -ne 0 ]; then
  log "smoke render failed (rc $smoke_rc): no full render (see logs/blender_*.log)"
  exit 1
fi
run_step render "$PY" -m wenart.assets audit render "${RENDER_ARGS[@]}"
run_step code "$PY" -m wenart.assets audit code --out "$AUDIT_ROOT" --work "$WORK"
run_step gpu-tests env WENART_AUDIT="$AUDIT_ROOT/audit" "$PY" -m pytest -m gpu tests/gpu/test_library.py \
  -k audit_render -v -ra --junitxml="$RESULTS/junit-library-audit-render.xml"

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
