#!/usr/bin/env bash
# Entry script for every WenArt RunPod pod. Started by scripts/gpu_run.py as the
# container command. It never relies on the session: a watchdog (armed first) and
# the end of the job both stop the pod from inside, and a stop is only trusted
# once the API confirms it.
#
# Env (set by gpu_run.py):  JOB_ID JOB_TOKEN JOB_SCRIPT REPO_URL REPO_COMMIT
#                           MAX_RUNTIME_S GRACE_S WENART_IMAGE WENART_EXPECT_VOLUME
#                           (HF_TOKEN from the RunPod secret)
# Env (set by RunPod):      RUNPOD_POD_ID RUNPOD_API_KEY (pod-scoped) RUNPOD_VOLUME_ID RUNPOD_DC_ID
set -Eeuo pipefail

JOB_ID="${JOB_ID:-job}"
MAX_RUNTIME_S="${MAX_RUNTIME_S:-7200}"
GRACE_S="${GRACE_S:-120}"
LOGS=/workspace/logs
JOB_DIR=/workspace/jobs/$JOB_ID
PUBLIC=/tmp/wenart-public          # per pod, on the container disk: tokens never persist
REPO_DIR=/workspace/repo
LOG=/tmp/pod_entry-$JOB_ID.log     # moved under /workspace/logs once that is writable

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] entry: $*"; }

# stop_pod never gives up and never returns before the API confirms EXITED/TERMINATED.
stop_pod() {
  set +e; trap - ERR
  local reason=$1 n=0 code status
  log "stopping pod ${RUNPOD_POD_ID:-?} ($reason)"
  sync 2>/dev/null
  while true; do
    n=$((n + 1))
    if command -v runpodctl >/dev/null 2>&1; then
      runpodctl pod stop "${RUNPOD_POD_ID:-}" >/dev/null 2>&1 && log "runpodctl stop sent"
    fi
    code=$(curl -sS -m 30 -o /dev/null -w '%{http_code}' -X POST \
      "https://api.runpod.io/v2/pods/${RUNPOD_POD_ID:-}/action" \
      -H "Authorization: Bearer ${RUNPOD_API_KEY:-}" -H "Content-Type: application/json" \
      -H "User-Agent: wenart-pod/0.2" -d '{"action":"stop"}' 2>/dev/null)
    log "REST stop attempt $n -> HTTP ${code:-none}"
    sleep 5
    status=$(curl -sS -m 30 "https://api.runpod.io/v2/pods/${RUNPOD_POD_ID:-}" \
      -H "Authorization: Bearer ${RUNPOD_API_KEY:-}" -H "User-Agent: wenart-pod/0.2" 2>/dev/null \
      | python3 -c 'import json,sys; print(json.load(sys.stdin).get("status",""))' 2>/dev/null)
    log "pod status now: ${status:-unknown}"
    case "$status" in EXITED|TERMINATED) return 0 ;; esac
    sleep $(( n < 6 ? n * 10 : 60 ))
  done
}

write_status() {  # state exit_code  (never fatal)
  python3 - "$1" "$2" "$JOB_ID" "$JOB_DIR/status.json" <<'PY' 2>/dev/null || true
import json, sys, time, os
state, code, job, path = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
d = {"job_id": job, "state": state, "exit_code": code,
     "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
     "pod_id": os.environ.get("RUNPOD_POD_ID"), "dc": os.environ.get("RUNPOD_DC_ID"),
     "volume": os.environ.get("RUNPOD_VOLUME_ID")}
os.makedirs(os.path.dirname(path), exist_ok=True)
tmp = path + ".tmp"
json.dump(d, open(tmp, "w"), indent=1); os.replace(tmp, path)
PY
}

# 1. Safety net first: the watchdog and the error trap exist before anything can fail.
( sleep "$MAX_RUNTIME_S"
  echo "[$(ts)] WATCHDOG: max runtime ${MAX_RUNTIME_S}s reached" | tee -a "$LOG"
  write_status "timeout" 124
  cp -f "$LOG" "$JOB_DIR/job.log" 2>/dev/null
  sleep 45   # longer than two runner polls, so the runner can collect job.log
  stop_pod "watchdog" ) &
WATCHDOG_PID=$!

finish() {  # exit_code reason
  set +e; trap - ERR
  local code=$1
  write_status "done" "$code"
  cp -f "$LOG" "$JOB_DIR/job.log" 2>/dev/null
  log "job finished with exit code $code ($2); pod stops in ${GRACE_S}s"
  sleep "$GRACE_S"
  find /tmp/wenart-public -mindepth 1 -maxdepth 1 -type l -delete 2>/dev/null
  stop_pod "job end"
  exit "$code"
}
on_error() { set +e; trap - ERR; log "ERROR at line $1"; finish 1 "trap"; }
trap 'on_error $LINENO' ERR

mkdir -p "$LOGS" "$JOB_DIR/results" "$PUBLIC"
if [ -w "$LOGS" ]; then
  cat "$LOG" >> "$LOGS/$JOB_ID.log" 2>/dev/null || true
  LOG=$LOGS/$JOB_ID.log
fi
exec > >(tee -a "$LOG") 2>&1
log "pod ${RUNPOD_POD_ID:-?} dc ${RUNPOD_DC_ID:-?} volume ${RUNPOD_VOLUME_ID:-none} job $JOB_ID image ${WENART_IMAGE:-?}"
log "watchdog armed: ${MAX_RUNTIME_S}s (pid $WATCHDOG_PID)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || log "nvidia-smi failed"
if [ "${WENART_EXPECT_VOLUME:-0}" = "1" ] && [ -z "${RUNPOD_VOLUME_ID:-}" ]; then
  log "expected a network volume but RUNPOD_VOLUME_ID is empty"; finish 3 "no volume"
fi

# 2. Job script name: a committed file under scripts/jobs/, nothing else is executed.
JOB_SCRIPT="${JOB_SCRIPT:-}"
if ! [[ "$JOB_SCRIPT" =~ ^scripts/jobs/[A-Za-z0-9_.-]+\.sh$ ]]; then
  log "invalid JOB_SCRIPT '$JOB_SCRIPT'"; finish 2 "bad job script"
fi

# 3. Status server on port 8000: token path on the container disk, root shows nothing,
#    no access log. Stale symlinks from older pods (volumes created before this change) go.
find /workspace/public -mindepth 1 -maxdepth 1 -type l -delete 2>/dev/null || true
: > "$PUBLIC/index.html"
ln -sfn "$JOB_DIR" "$PUBLIC/$JOB_TOKEN"
write_status "starting" 0
( cd "$PUBLIC" && python3 -m http.server 8000 --bind 0.0.0.0 >/dev/null 2>&1 ) &
log "status server on :8000 /<token>/status.json"

# 4. Code: clone or self-heal the repo on the volume, then check out the given commit.
repo_fresh_clone() {
  cd /
  [ -d /workspace/repo ] && mv /workspace/repo "/workspace/.repo-broken-$(date +%s)"
  git clone -q "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
}
if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
  find /workspace/repo/.git -maxdepth 1 -name '*.lock' -delete 2>/dev/null || true
  git remote set-url origin "$REPO_URL" || true
  if ! { git fetch -q origin "$REPO_COMMIT" 2>/dev/null || git fetch -q origin; } \
     || ! git checkout -q --force --detach "$REPO_COMMIT"; then
    log "repo on the volume is broken; cloning again"; repo_fresh_clone
  fi
else
  repo_fresh_clone
fi
git checkout -q --force --detach "$REPO_COMMIT"
git clean -fdxq -e results/ -e outputs/ || true   # pipeline outputs on the volume stay
log "repo at $(git rev-parse --short HEAD)"
if [ ! -f "$JOB_SCRIPT" ]; then log "job script $JOB_SCRIPT is not in the repo"; finish 2 "missing job script"; fi

# 5. Setup (venv, Blender, tools) – skips what is already on the volume.
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$JOB_DIR/results" HF_HOME=/workspace/hf
write_status "setup" 0
bash scripts/pod_setup.sh

# 6. The job (exempt from the ERR trap so its own exit code is kept).
write_status "running" 0
export PATH=/workspace/venv/bin:/workspace/tools/blender:$PATH
code=0
bash "$JOB_SCRIPT" || code=$?
finish "$code" "job"
