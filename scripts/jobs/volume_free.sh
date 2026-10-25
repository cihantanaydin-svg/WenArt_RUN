#!/usr/bin/env bash
# Free the network volume (user OK of 25 Oct 2026: "Both": grow it to 500 GB and clean old data). Run by
# scripts/pod_entry.sh:
#
#   scripts/gpu_run.py run --job scripts/jobs/volume_free.sh --gpu 'RTX 5090' --max-minutes 30 --grace 300 \
#     --purpose "volume: restore the repo, delete outputs-archive, old job folders and pip-cache (user OK 25 Oct 2026)"
#
# 1. Restores the repo a failed pod moved aside: the newest $WS/.repo-broken-* goes back to $WS/repo when $WS/repo is
#    missing (a move, nothing deleted; it holds every project's pipeline outputs).
# 2. Deletes exactly what the user agreed to: $WS/outputs-archive (old outputs set aside since Milestone 6), the job
#    folders under $WS/jobs except this job's (their results were collected by the runner), $WS/pip-cache (pip
#    downloads them again). Nothing else is touched.
# Results ($WENART_RESULTS): volume_free.txt (df and du before and after, every moved and deleted path with its size).
# DRY_RUN=1 lists without changing anything.
set -Eeuo pipefail
trap 'echo "[volume_free] ERROR at line $LINENO: $BASH_COMMAND" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
DRY_RUN="${DRY_RUN:-0}"
mkdir -p "$RESULTS"
OUT=$RESULTS/volume_free.txt
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
usage() {
  echo "== df $(ts)"
  df -h "$WS" 2>/dev/null || true
  echo "== du -sh $WS/* $WS/.[!.]* (largest first)"
  timeout 900 du -sh "$WS"/* "$WS"/.[!.]* 2>/dev/null | sort -rh | head -30 || true
}
drop() {   # drop <path>: delete it, logging its size first
  local p=$1
  [ -e "$p" ] || return 0
  echo "delete $(du -sh "$p" 2>/dev/null | cut -f1) $p"
  if [ "$DRY_RUN" != "1" ]; then rm -rf --one-file-system "$p"; fi
}
{
  echo "volume_free $(ts) job ${JOB_ID:-?} dry_run=$DRY_RUN"
  usage
  echo "== 1. restore the repo"
  if [ ! -e "$WS/repo" ]; then
    broken=$(ls -d "$WS"/.repo-broken-* 2>/dev/null | sort | tail -1 || true)
    if [ -n "$broken" ]; then
      echo "move $broken -> $WS/repo"
      if [ "$DRY_RUN" != "1" ]; then mv "$broken" "$WS/repo"; fi
    else
      echo "no .repo-broken-* to restore"
    fi
  else
    echo "$WS/repo exists: nothing to restore"
  fi
  echo "== 2. delete outputs-archive, old job folders, pip-cache"
  drop "$WS/outputs-archive"
  for d in "$WS"/jobs/*; do
    [ -d "$d" ] || continue
    [ "$(basename "$d")" = "${JOB_ID:-}" ] && continue
    drop "$d"
  done
  drop "$WS/pip-cache"
  usage
  echo "volume_free done $(ts)"
} > "$OUT" 2>&1
cat "$OUT"
