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
# Env (all optional): RANK_TYPES (comma list), RANK_WORKERS (default 4), RANK_ROOT, RANK_SAMPLES, WENART_ASSETS;
# RANK_PROCEDURAL=1 renders our own builds instead (every parametric and module builder in the projects' styles,
# 31 Oct 2026), RANK_PROC_TAG (default ours) names them: ranking_index_<tag>.json, studio_results_<tag>.json.
# RANK_BATCH=syncronia (3 Nov 2026, the user's beds.zip): ingest the proper models of the zip, then their own tab:
#   scripts/gpu_run.py run --job scripts/jobs/library_ranking.sh --env RANK_BATCH=syncronia --max-minutes 40 \
#     --purpose "beds.zip: library intake of the proper models and their ranking tab"
# RANK_BATCH=remaining (31 Oct 2026, user: "include all remaining library models for ranking after the real04 run"):
# every library model the pipeline may use that no committed sheet shows (the decor models, the extras the fit takes
# first, the small items' models, any other furniture type), each on the stage of its kind (studio.decor_stage: a
# plinth, the floor, a backdrop wall, a ceiling panel); RANK_TYPES then narrows it (types or the groups decor,
# textiles, lights, wall, plants, tabletop, electronics); ranking_index_remaining.json, studio_results_remaining.json,
# new sheets named by type (the committed sheets keep their names, ids and letters).
#
#   scripts/gpu_run.py run --job scripts/jobs/library_ranking.sh --env RANK_BATCH=remaining --max-minutes 45 \
#     --purpose "UL217 batch 3: ranking studio of the remaining library models (decor, extras)"
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
RANK_BATCH="${RANK_BATCH:-}"
RANK_TYPES="${RANK_TYPES:-}"
if [ -z "$RANK_TYPES" ] && [ -z "$RANK_BATCH" ]; then RANK_TYPES="bed_double,sofa,armchair"; fi
RANK_WORKERS="${RANK_WORKERS:-4}"
RANK_PROCEDURAL="${RANK_PROCEDURAL:-0}"
RANK_PROC_TAG="${RANK_PROC_TAG:-ours}"
RESULTS_FILE="$OUT/studio_results.json"
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

df -h "${WENART_WS:-/workspace}" 2>/dev/null | tail -1 | sed 's/^/[volume] /' || true   # the user may grow it to 600 GB (3 Nov 2026)
cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR" "$WORK" "$OUT" "$ASSETS"
log "job $JOB: batch [${RANK_BATCH:-none}], types [${RANK_TYPES:-all of the batch}], workers $RANK_WORKERS," \
    "root $RANK_ROOT, assets $ASSETS," \
    "deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

ARGS=(--assets "$ASSETS" --work "$WORK" --out "$OUT" --workers "$RANK_WORKERS" --blender "$WENART_BLENDER")
if [ -n "$RANK_TYPES" ]; then ARGS+=(--types "$RANK_TYPES"); fi
if [ -n "$RANK_BATCH" ] && [ "$RANK_PROCEDURAL" != "1" ]; then
  ARGS+=(--batch "$RANK_BATCH")
  RESULTS_FILE="$OUT/studio_results_${RANK_BATCH}.json"
fi
if [ -n "${WENART_DEADLINE:-}" ]; then ARGS+=(--deadline "$WENART_DEADLINE"); fi
if [ -n "${RANK_SAMPLES:-}" ]; then ARGS+=(--samples "$RANK_SAMPLES"); fi
if [ "$RANK_PROCEDURAL" = "1" ]; then
  ARGS+=(--procedural --proc-tag "$RANK_PROC_TAG")
  RESULTS_FILE="$OUT/studio_results_${RANK_PROC_TAG}.json"
fi

# 3 Nov 2026 (the user: "Include into the library (the proper ones) and also open up a new ranking tab"): a source
# batch that brings its own models first ingests them (RANK_BATCH=syncronia: the user's beds.zip, on the volume since
# the inspection pod; downloaded again when missing): converted, part materials, <assets>/models/syncronia/, the
# entries merged (audit pending) into this checkout's catalogue for the studio, and returned in
# $RESULTS/library/syncronia/ (syncronia_entries.json, ingest_syncronia.json, parts/) for the session to review
if [ "$RANK_BATCH" = "syncronia" ]; then
  if ! command -v assimp >/dev/null 2>&1; then
    apt-get install -y -qq --no-install-recommends assimp-utils >/dev/null 2>&1 \
      || { apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq --no-install-recommends assimp-utils >/dev/null 2>&1; } \
      || log "assimp-utils could not be installed"
  fi
  # every zip of wenart.assets.syncronia.ZIPS (beds.zip, then the user's Drive folder Furnitures, 3 Nov 2026)
  while IFS=: read -r SY_ID SY_BYTES SY_NAME; do
    SY_ZIP="$WS/library/inbox/$SY_ID/$SY_NAME"
    if [ "$(stat -c %s "$SY_ZIP" 2>/dev/null || echo 0)" != "$SY_BYTES" ]; then
      mkdir -p "$(dirname "$SY_ZIP")"
      curl -fsSL --retry 3 -C - -o "$SY_ZIP" \
        "https://drive.usercontent.google.com/download?id=$SY_ID&export=download&confirm=t" \
        || log "$SY_NAME download failed"
    fi
    rm -rf "/opt/wenart/syncronia/${SY_NAME%.zip}/files"    # the container disk's scratch of an earlier zip only
    run_step "ingest-${SY_NAME%.zip}" "$PY" -m wenart.assets.syncronia ingest --zip "$SY_ZIP" --zip-name "$SY_NAME" \
      --work "/opt/wenart/syncronia/${SY_NAME%.zip}" --cache "$RANK_ROOT/syncronia/${SY_NAME%.zip}/cache" \
      --assets "$ASSETS" \
      --out "$RESULTS/library/syncronia/${SY_NAME%.zip}" --blender "$WENART_BLENDER" --merge-catalog
    rm -rf "/opt/wenart/syncronia/${SY_NAME%.zip}"            # the zip's scratch (the GLBs are in the assets)
  done < <("$PY" -c 'from wenart.assets import syncronia as S
for i, b, n in S.ZIPS: print(f"{i}:{b}:{n}")')
fi

# the Poly Haven models of the ranked types or batch (the library GLBs are on the volume)
read -r -a PH_IDS <<< "$("$PY" -c 'import sys
from wenart.assets.audit import studio as S
types = [t for t in sys.argv[1].split(",") if t]
print(" ".join(e["id"] for e in S.batch_entries(sys.argv[2], types) if e.get("gltf")))' "$RANK_TYPES" "$RANK_BATCH")"
if [ "${#PH_IDS[@]}" -gt 0 ] && [ "$RANK_PROCEDURAL" != "1" ]; then
  run_step models "$PY" -m wenart.assets models fetch --assets "$ASSETS" --size 1k --ids "${PH_IDS[@]}"
fi
if [ "$RANK_PROCEDURAL" = "1" ] || [ "$RANK_BATCH" = "syncronia" ]; then
  # our builds wear the projects' textures (3 Nov 2026: so do the intake's part materials of a source batch,
  # furniture.PART_DRESS: the linen, veneer, leather, marble and metal scans): the latest projects' style sets and every furniture texture set of the
  # vocabulary (wenart.assets.fetch.fetch_for_style; idempotent, 2k, CC0)
  for st in "$REPO"/results/baseline/latest/run/*/style.json; do
    [ -f "$st" ] && run_step "textures-$(basename "$(dirname "$st")")" "$PY" -m wenart.assets fetch --style "$st" \
      --assets "$ASSETS" --size 2k
  done
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
"$PY" - "$RESULTS_FILE" <<'EOF' || FAILED+=("results")
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
