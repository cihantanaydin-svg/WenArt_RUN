#!/usr/bin/env bash
# 1 Nov 2026 (lesson UL237; user on real04 run 20261031-194116-full: "This is only a photo if that's the case don't use
# this model ever again"): the photo-card mesh check of every library model file on the volume. A model whose visible
# surface is mostly one or two flat, thin panels carrying an image (a product photo on a board, a photo panel behind a
# lamp) is a photo card, not a 3D object (wenart.assets.audit.photocard: numpy only, no Blender, no GPU work; the GLBs
# exist only on the volume, so the scan runs on a pod). The merged store comes back as a result file; the session
# commits it (results/library/photo_cards.json) and catalog.usable refuses every card.
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE
# set; /workspace/venv has the CPU deps). The watchdog and the self-stop are pod_entry.sh's.
#
#   scripts/gpu_run.py run --job scripts/jobs/library_photo_card.sh --max-minutes 30 \
#     --purpose "UL237: photo-card mesh check of every library model file"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. scan: python -m wenart.assets.audit.photocard scan (PC_WORKERS processes, resumable: a model whose record of the
#      same file and version is in the output is not read again) -> $RESULTS/library/photo_card/photo_card_mesh.json;
#   2. merge: the committed store (results/library/photo_cards.json at the pod's commit) with the scan merged into it
#      -> $RESULTS/library/photo_card/photo_cards.json (a mesh card is added; a CPU card the mesh check does not
#      confirm is kept with the mesh numbers for review; the summary by type and the review list are in the log).
# Back on the session: python -m wenart.assets.audit.photocard merge --mesh <results>/library/photo_card/
# photo_card_mesh.json (or copy the merged store), check the new cards on the ranking sheets, commit.
# The Poly Haven glTFs (catalog.json) are fetched per run, not kept on the volume: they are listed as missing (CC0
# studio models, no card expected).
#
# Env (all optional): PC_WORKERS (default: the CPU count, at most 16), WENART_ASSETS (default /workspace/assets),
# PC_IDS (space-separated model ids: scan only these).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-library_photo_card}"
LOG=$LOGS/library_photo_card-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
PY="${WENART_PY:-$WS/venv/bin/python}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
OUT="$RESULTS/library/photo_card"
CPUS="$(nproc 2>/dev/null || echo 4)"
PC_WORKERS="${PC_WORKERS:-$(( CPUS > 16 ? 16 : CPUS ))}"
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_ASSETS="$ASSETS"
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] library_photo_card: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
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
  return 0
}

cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR" "$OUT"
log "job $JOB: assets $ASSETS, workers $PC_WORKERS of $CPUS CPU(s), deadline ${WENART_DEADLINE:-none}"

ARGS=(--assets "$ASSETS" --out "$OUT/photo_card_mesh.json" --workers "$PC_WORKERS")
if [ -n "${WENART_DEADLINE:-}" ]; then
  # 3 minutes for the merge and the copy-back before the watchdog
  ARGS+=(--deadline "$(( ${WENART_DEADLINE%.*} - 180 ))")
fi
if [ -n "${PC_IDS:-}" ]; then
  read -r -a IDS <<< "$PC_IDS"
  ARGS+=(--ids "${IDS[@]}")
fi
run_step scan "$PY" -m wenart.assets.audit.photocard scan "${ARGS[@]}"

if [ -f "$OUT/photo_card_mesh.json" ]; then
  cp -f "$REPO/results/library/photo_cards.json" "$OUT/photo_cards.json" 2>/dev/null || true
  run_step merge "$PY" -m wenart.assets.audit.photocard merge --mesh "$OUT/photo_card_mesh.json" \
    --store "$OUT/photo_cards.json"
else
  log "no scan output: nothing to merge"
  FAILED+=("merge")
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
