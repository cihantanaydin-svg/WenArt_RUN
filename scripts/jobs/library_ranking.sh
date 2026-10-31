#!/usr/bin/env bash
# 31 Oct 2026 (lesson UL217, the user's ranking of the library models): the ranking studio. Every model the fit may use
# of RANK_TYPES (default bed_double, sofa, armchair) built by the scene builder itself (bedding, fabric dressing, the
# file's own shading) and photographed in one neutral studio (same light, same front 3/4 camera, the distance
# following the size); the lettered sheets (A-T, 20 a sheet) and one tile per model for the scoring page
# (python -m wenart.assets.audit.studio; Blender side wenart/assets/audit/blender_studio.py).
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE
# set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender). The watchdog and the self-stop
# are pod_entry.sh's.
#
#   scripts/gpu_run.py run --job scripts/jobs/library_ranking.sh --max-minutes 60 \
#     --purpose "UL217: ranking studio (beds, sofas, armchairs)"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. models: the Poly Haven models of the ranked types into the assets folder (idempotent; the library GLBs are on
#      the volume already);
#   2. smoke: 1 model per type (a Blender side that fails here stops the job early);
#   3. render: every model (RANK_WORKERS Blender processes, resumable: a model whose image is current is skipped);
#      then the sheets and the tiles into $WENART_RESULTS/library/ranking (tiles/<type>/<id>.jpg, sheets/<sheet>.jpg,
#      ranking_index.json, studio_results.json).
# The studio's PNGs stay on the volume (RANK_ROOT, default /workspace/library-ranking).
#
# Env (all optional): RANK_TYPES (comma list), RANK_WORKERS (default 4), RANK_ROOT, RANK_SAMPLES, WENART_ASSETS.
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-library_ranking}"
LOG=$LOGS/library_ranking-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
PY="${WENART_PY:-$WS/venv/bin/python}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
RANK_ROOT="${RANK_ROOT:-$WS/library-ranking}"
WORK="$RANK_ROOT/work"
OUT="$RESULTS/library/ranking"
RANK_TYPES="${RANK_TYPES:-bed_double,sofa,armchair}"
RANK_WORKERS="${RANK_WORKERS:-4}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_ASSETS="$ASSETS"
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] library_ranking: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

copy_logs() {
  mkdir -p "$RESULTS/logs"
  for f in "$WORK"/jobs/blender_*.log; do
    [ -f "$f" ] && tail -n 300 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  copy_logs
  log "job $JOB ends with exit code $rc: $(find "$OUT" -type f 2>/dev/null | wc -l) result file(s)"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

run_step() {
  local name=$1; shift
  local t0 rc=0
  t0=$(date +%s)
  log "step start: $name"
  "$@" || rc=$?
  log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  copy_logs
  return 0
}

cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR" "$WORK" "$OUT" "$ASSETS"
log "job $JOB: types [$RANK_TYPES], workers $RANK_WORKERS, root $RANK_ROOT, assets $ASSETS," \
    "deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

ARGS=(--types "$RANK_TYPES" --assets "$ASSETS" --work "$WORK" --out "$OUT" --workers "$RANK_WORKERS"
      --blender "$WENART_BLENDER")
if [ -n "${WENART_DEADLINE:-}" ]; then ARGS+=(--deadline "$WENART_DEADLINE"); fi
if [ -n "${RANK_SAMPLES:-}" ]; then ARGS+=(--samples "$RANK_SAMPLES"); fi

# the Poly Haven models of the ranked types (the library GLBs are on the volume)
read -r -a PH_IDS <<< "$("$PY" -c 'import sys
from wenart.assets.audit import studio as S
print(" ".join(e["id"] for e in S.rank_entries(sys.argv[1].split(",")) if e.get("gltf")))' "$RANK_TYPES")"
if [ "${#PH_IDS[@]}" -gt 0 ]; then
  run_step models "$PY" -m wenart.assets models fetch --assets "$ASSETS" --size 1k --ids "${PH_IDS[@]}"
fi
run_step plan "$PY" -m wenart.assets.audit.studio plan "${ARGS[@]}"
smoke_rc=0
"$PY" -m wenart.assets.audit.studio render "${ARGS[@]}" --limit 1 || smoke_rc=$?
copy_logs
if [ "$smoke_rc" -ne 0 ]; then
  log "smoke render failed (rc $smoke_rc): no full render (see logs/blender_*.log)"
  exit 1
fi
run_step render "$PY" -m wenart.assets.audit.studio render "${ARGS[@]}"
"$PY" - "$OUT/studio_results.json" <<'EOF' || FAILED+=("results")
import json, sys
r = json.load(open(sys.argv[1]))
print(f"ranking studio: {r['ok']} of {r['models']} model(s) rendered, {r['failed']} failed")
sys.exit(0 if r["models"] and r["ok"] >= 0.9 * r["models"] else 1)
EOF

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
