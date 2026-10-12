#!/usr/bin/env bash
# Volume cleanup (user OK of 12 Oct 2026: "clean old outputs and increase the size to 400gb, and then stop no
# rerun"). Run by scripts/pod_entry.sh:
#
#   scripts/gpu_run.py run --job scripts/jobs/volume_clean.sh --gpu 'RTX PRO 4500' --max-minutes 40 --grace 300 \
#     --purpose "volume: clean old outputs (user OK 12 Oct 2026)"
#
# Deletes the OLD OUTPUTS only: every project's outputs ($WS/outputs/<p>: scenes, renders with their EXR passes, 3D
# exports, stage records) and every earlier job folder ($WS/jobs/<job>: the results copies the runner collected),
# except the newest real04 run (KEEP_PROJECTS, KEEP_JOBS) and this job; plus $WS/outputs-archive and the repos
# pod_entry.sh moved aside ($WS/.repo-broken-*). Never touched: the library assets, the growth downloads, the audit
# sheets, the model caches, the tools, the venvs, the private projects and their results, the logs.
# Results ($WENART_RESULTS): volume_clean.txt (df and du before and after, every deleted path with its size).
set -Eeuo pipefail
trap 'echo "[volume_clean] ERROR at line $LINENO: $BASH_COMMAND" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
LOGS=$WS/logs
KEEP_PROJECTS="${KEEP_PROJECTS:-real04}"
KEEP_JOBS="${KEEP_JOBS:-20261011-153030-full} ${JOB_ID:-}"
DRY_RUN="${DRY_RUN:-0}"
mkdir -p "$LOGS" "$RESULTS"
exec > >(tee -a "$LOGS/volume_clean-${JOB_ID:-job}.log") 2>&1
OUT=$RESULTS/volume_clean.txt
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

usage() {
  echo "== df $(ts)"
  df -h "$WS" 2>/dev/null || true
  echo "== du -sh $WS/* $WS/.[!.]* (largest first)"
  timeout 900 du -sh "$WS"/* "$WS"/.[!.]* 2>/dev/null | sort -rh | head -40 || true
  for d in outputs jobs; do
    [ -d "$WS/$d" ] || continue
    echo "== du -sh $WS/$d/* (largest first)"
    timeout 600 du -sh "$WS/$d"/* 2>/dev/null | sort -rh | head -60 || true
  done
}

keep() {   # keep <name> <list>
  local n=$1; shift
  for k in $*; do [ "$n" = "$k" ] && return 0; done
  return 1
}

remove() {   # remove <path>: logged with its size; DRY_RUN=1 only lists
  local p=$1 size
  [ -e "$p" ] || return 0
  case "$p" in "$WS"/outputs/*|"$WS"/jobs/*|"$WS"/outputs-archive|"$WS"/.repo-broken-*) ;;
    *) echo "refused (outside the cleanup set): $p"; return 0 ;;
  esac
  size=$(timeout 300 du -sh "$p" 2>/dev/null | cut -f1 || echo "?")
  if [ "$DRY_RUN" = "1" ]; then echo "would delete $size $p"; return 0; fi
  rm -rf -- "$p" && echo "deleted $size $p"
}

{
  echo "volume clean $(ts): keep projects [$KEEP_PROJECTS], keep jobs [$KEEP_JOBS], dry run $DRY_RUN"
  echo; echo "######## BEFORE"
  usage
  echo; echo "######## DELETING"
  if [ -d "$WS/outputs" ]; then
    for p in "$WS"/outputs/*; do
      [ -e "$p" ] || continue
      keep "$(basename "$p")" $KEEP_PROJECTS && { echo "kept $p"; continue; }
      remove "$p"
    done
  fi
  if [ -d "$WS/jobs" ]; then
    for p in "$WS"/jobs/*; do
      [ -e "$p" ] || continue
      keep "$(basename "$p")" $KEEP_JOBS && { echo "kept $p"; continue; }
      remove "$p"
    done
  fi
  remove "$WS/outputs-archive"
  for p in "$WS"/.repo-broken-*; do [ -e "$p" ] && remove "$p"; done
  echo; echo "######## AFTER"
  usage
  echo; echo "done $(ts)"
} > "$OUT" 2>&1
grep -E "^(deleted|would delete|kept|refused)" "$OUT" | head -80 || true
echo "[volume_clean] $(ts) done: $(grep -c '^deleted' "$OUT" || true) path(s) deleted; report $OUT"
