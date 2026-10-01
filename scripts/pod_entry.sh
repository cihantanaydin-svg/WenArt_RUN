#!/usr/bin/env bash
# Entry script for every WenArt RunPod pod. Started by scripts/gpu_run.py as the
# container command. It never relies on the session: a watchdog and the end of
# the job both stop the pod from inside.
#
# Env (set by gpu_run.py):  JOB_ID JOB_TOKEN JOB_CMD REPO_URL REPO_COMMIT
#                           MAX_RUNTIME_S GRACE_S   (HF_TOKEN from the RunPod secret)
# Env (set by RunPod):      RUNPOD_POD_ID RUNPOD_API_KEY (pod-scoped) RUNPOD_VOLUME_ID
set -Eeuo pipefail

JOB_ID="${JOB_ID:-job}"
MAX_RUNTIME_S="${MAX_RUNTIME_S:-7200}"
GRACE_S="${GRACE_S:-120}"
WS=/workspace
LOGS=$WS/logs
JOB_DIR=$WS/jobs/$JOB_ID
PUBLIC=$WS/public
REPO_DIR=$WS/repo
mkdir -p "$LOGS" "$JOB_DIR/results" "$PUBLIC"
LOG=$LOGS/$JOB_ID.log
exec > >(tee -a "$LOG") 2>&1

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] entry: $*"; }

stop_pod() {
  log "stopping pod ${RUNPOD_POD_ID:-?} ($1)"
  sync || true
  if command -v runpodctl >/dev/null 2>&1; then
    runpodctl pod stop "$RUNPOD_POD_ID" && return 0
    log "runpodctl failed, trying REST"
  fi
  curl -sS -m 30 -X POST "https://api.runpod.io/v2/pods/$RUNPOD_POD_ID/action" \
    -H "Authorization: Bearer ${RUNPOD_API_KEY:-}" -H "Content-Type: application/json" \
    -d '{"action":"stop"}' >/dev/null && return 0
  log "REST stop failed too; retrying every 30 s"
  while true; do
    sleep 30
    curl -sS -m 30 -X POST "https://api.runpod.io/v2/pods/$RUNPOD_POD_ID/action" \
      -H "Authorization: Bearer ${RUNPOD_API_KEY:-}" -H "Content-Type: application/json" \
      -d '{"action":"stop"}' >/dev/null && return 0
  done
}

write_status() {  # state exit_code
  python3 - "$1" "$2" "$JOB_ID" "$JOB_DIR/status.json" <<'PY'
import json, sys, time, os
state, code, job, path = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
d = {"job_id": job, "state": state, "exit_code": code,
     "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
     "pod_id": os.environ.get("RUNPOD_POD_ID"), "dc": os.environ.get("RUNPOD_DC_ID")}
tmp = path + ".tmp"
json.dump(d, open(tmp, "w"), indent=1); os.replace(tmp, path)
PY
}

finish() {  # exit_code reason
  local code=$1
  write_status "done" "$code"
  cp -f "$LOG" "$JOB_DIR/job.log" || true
  log "job finished with exit code $code ($2); pod stops in ${GRACE_S}s"
  sleep "$GRACE_S"
  stop_pod "job end"
  exit "$code"
}
on_error() { log "ERROR at line $1"; finish 1 "trap"; }
trap 'on_error $LINENO' ERR

log "pod ${RUNPOD_POD_ID:-?} dc ${RUNPOD_DC_ID:-?} volume ${RUNPOD_VOLUME_ID:-none} job $JOB_ID"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || log "nvidia-smi failed"

# 1. Watchdog: hard stop at the max runtime, whatever happens below.
( sleep "$MAX_RUNTIME_S"; echo "[$(ts)] WATCHDOG: max runtime ${MAX_RUNTIME_S}s reached"; \
  cp -f "$LOG" "$JOB_DIR/job.log" 2>/dev/null; stop_pod "watchdog" ) &
WATCHDOG_PID=$!
log "watchdog armed: ${MAX_RUNTIME_S}s (pid $WATCHDOG_PID)"

# 2. Status server on port 8000 (token-protected path, root shows nothing).
: > "$PUBLIC/index.html"
ln -sfn "$JOB_DIR" "$PUBLIC/$JOB_TOKEN"
write_status "starting" 0
( cd "$PUBLIC" && python3 -m http.server 8000 --bind 0.0.0.0 >"$LOGS/http-$JOB_ID.log" 2>&1 ) &
log "status server on :8000 /<token>/status.json"

# 3. Code: clone the repo at the given commit (idempotent).
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone -q "$REPO_URL" "$REPO_DIR"
fi
cd "$REPO_DIR"
git fetch -q origin "$REPO_COMMIT" || git fetch -q origin
git checkout -q --detach "$REPO_COMMIT"
log "repo at $(git rev-parse --short HEAD)"

# 4. Setup (venv, Blender, tools) – skips what is already on the volume.
write_status "setup" 0
bash scripts/pod_setup.sh

# 5. The job.
write_status "running" 0
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$JOB_DIR/results" HF_HOME=$WS/hf
export PATH=$WS/venv/bin:$WS/tools/blender:$PATH
set +e
bash -c "$JOB_CMD"
code=$?
set -e
finish "$code" "job"
