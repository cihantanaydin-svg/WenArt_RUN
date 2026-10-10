#!/usr/bin/env bash
# Milestone 12 pod P3: the library audit, part B (docs/milestone12.md §6.1 D21, §6.4 D24, §8): the vision question
# per model (the model of check.yaml the bake-off picked; a second pass only where code cannot confirm the type),
# then keep / fix / remove, the contact sheets per type, the gap report and the catalogue fields written into COPIES
# of the catalogues (the lead copies them into wenart/furniture/ after the user's OK of the removals, D22).
# Needs pod P2's audit folder on the volume (AUDIT_ROOT/audit/measure.json and the sheets). Run by
# scripts/pod_entry.sh (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE set).
#
#   scripts/gpu_run.py run --job scripts/jobs/library_audit_judge.sh --gpu 'RTX PRO 6000' --disk 150 \
#     --max-minutes 80 --env AUDIT_MODEL_KEY=agent --purpose "M12 P3: library audit B (vision, decisions, gaps)"
#
# (a 2-GPU model of the bake-off: add --gpu-count 2 --over-5-ok and the model's key.)
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. setup: vLLM + the model of AUDIT_MODEL_KEY (scripts/pod_setup_polish.sh, part check; HF_HOME on the
#      container disk);
#   2. ask: python -m wenart.assets audit ask --serve --pass both (pass 1 for every model with a sheet, then pass 2
#      for the models without title evidence that pass 1 accepts; one server session; answers reused after a cut);
#   3. decide, sheets, gaps (python -m wenart.assets audit ...);
#   4. write: the audit fields and flags into copies of catalog_library.json and catalog.json
#      (AUDIT_ROOT/audit/catalogue/), validated; the session's files are not touched;
#   5. gpu-tests: pytest -m gpu tests/gpu/test_library.py -k audit_judge.
# After every step the audit's small files are copied to $WENART_RESULTS/library/audit.
#
# Env (all optional): AUDIT_ROOT (default /workspace/library-audit), AUDIT_MODEL_KEY (default: audit.yaml
# ask.model_key), AUDIT_ASK_WORKERS (default: audit.yaml ask.workers).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-library_audit_judge}"
LOG=$LOGS/library_audit_judge-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
AUDIT_ROOT="${AUDIT_ROOT:-$WS/library-audit}"
AUDIT="$AUDIT_ROOT/audit"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
export WENART_AUDIT="$RESULTS/library/audit"
MODEL_KEY="${AUDIT_MODEL_KEY:-$("$PY" -c 'from wenart.assets.audit import load_config; print((load_config().get("ask") or {}).get("model_key", "agent"))')}"
FAILED=()
START_STAMP=$LOGS/library_audit_judge-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] library_audit_judge: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

copy_results() {
  local dst="$RESULTS/library/audit"
  mkdir -p "$dst" "$RESULTS/logs"
  if [ -d "$AUDIT" ]; then
    (cd "$AUDIT" && find . -type f \( -name '*.json' -o -name '*.md' -o -name '*.csv' -o -name '*.jpg' \) -print0 \
      | while IFS= read -r -d '' f; do mkdir -p "$dst/$(dirname "$f")"; cp -f "$f" "$dst/$f"; done) \
      || log "copy of $AUDIT failed"
  fi
  local f
  for f in "$LOGS"/vllm-*.log "$LOGS"/hf-download-*.log "$LOGS"/setup-polish-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

# kill_vllm: a server left behind by a step that died (the pid file of wenart.run.servers).
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
  local rc=$?
  trap - ERR
  set +e
  kill_vllm
  copy_results
  log "job $JOB ends with exit code $rc"
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
  kill_vllm
  copy_results
  return 0
}

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$JOB_DIR"
log "job $JOB: audit $AUDIT, model key $MODEL_KEY, deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
if [ ! -f "$AUDIT/measure.json" ]; then
  log "no $AUDIT/measure.json: run pod P2 (scripts/jobs/library_audit_render.sh) first"
  exit 1
fi

ASK_ARGS=(--out "$AUDIT_ROOT" --model-key "$MODEL_KEY" --serve --job-dir "$JOB_DIR" --pass both)
if [ -n "${WENART_DEADLINE:-}" ]; then ASK_ARGS+=(--deadline "$WENART_DEADLINE"); fi
if [ -n "${AUDIT_ASK_WORKERS:-}" ]; then ASK_ARGS+=(--workers "$AUDIT_ASK_WORKERS"); fi

run_step setup env AGENT_MODELS="$MODEL_KEY" POLISH_RECOG_PARTS="vllm models" POLISH_MODE=final \
  POLISH_PHASES="check" bash scripts/pod_setup_polish.sh
export HF_HUB_OFFLINE=1
run_step ask "$PY" -m wenart.assets audit ask "${ASK_ARGS[@]}"
run_step decide "$PY" -m wenart.assets audit decide --out "$AUDIT_ROOT" --model-key "$MODEL_KEY"
run_step sheets "$PY" -m wenart.assets audit sheets --out "$AUDIT_ROOT"
run_step gaps "$PY" -m wenart.assets audit gaps --out "$AUDIT_ROOT"
mkdir -p "$AUDIT/catalogue"
cp -f wenart/furniture/catalog_library.json wenart/furniture/catalog.json "$AUDIT/catalogue/"
run_step write "$PY" -m wenart.assets audit write --out "$AUDIT_ROOT" --catalog "$AUDIT/catalogue/catalog_library.json" \
  --polyhaven "$AUDIT/catalogue/catalog.json"
run_step gpu-tests env WENART_AUDIT="$AUDIT" AUDIT_MODEL_KEY="$MODEL_KEY" "$PY" -m pytest -m gpu \
  tests/gpu/test_library.py -k audit_judge -v -ra --junitxml="$RESULTS/junit-library-audit-judge.xml"

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
