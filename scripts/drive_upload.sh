#!/usr/bin/env bash
# Upload the 3D files of finished projects (outputs/<p>/export/*.blend, *.glb) from the pod to the user's Google
# Drive with rclone (user request of 10 Oct 2026; docs/setup.md step 6). Called by scripts/jobs/full.sh after the
# run and by scripts/jobs/drive_upload.sh for files already on the volume.
#
#   bash scripts/drive_upload.sh <outputs root> <project> [<project> ...]
#
# Env: RCLONE_CONF (the RunPod secret rclone_conf: the user's rclone.conf with a Google Drive remote; passed by
#      scripts/gpu_run.py --drive-upload), DRIVE_REMOTE (default: the first remote of the config),
#      DRIVE_FOLDER (default WenArt), DRIVE_TIMEOUT_S (default 1200).
#
# Rules (CLAUDE.md secrets): the config is written to the container disk only (/opt/wenart, mode 600), never to
# /workspace, never printed, and deleted on exit; rclone runs without -v so it logs no request headers. rclone
# v1.75.2 (git tag of github.com/rclone/rclone, checked 10 Oct 2026; MIT licence) is downloaded to the container
# disk and checked against the release's SHA256SUMS. A missing secret or a failed upload is a warning: the run
# and its results stay as they are.
set -Eeuo pipefail

RCLONE_VERSION="v1.75.2"
FAST="${WENART_FAST:-/opt/wenart}"
LOGS="${WENART_LOGS:-/workspace/logs}"
BIN_DIR="$FAST/rclone-$RCLONE_VERSION"
CONF="$FAST/rclone-upload.conf"
ZIP="rclone-$RCLONE_VERSION-linux-amd64.zip"
mkdir -p "$LOGS"
LOG="$LOGS/drive-upload-$(date -u +%Y%m%d-%H%M%S).log"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] drive_upload: $*" | tee -a "$LOG"; }
cleanup() { rm -f "$CONF"; }
trap cleanup EXIT
trap 'log "ERROR at line $LINENO"; exit 1' ERR

OUTPUTS="${1:?usage: drive_upload.sh <outputs root> <project> ...}"
shift
if [ "$#" -eq 0 ]; then log "no project given: nothing to upload"; exit 0; fi
if [ -z "${RCLONE_CONF:-}" ] || [[ "${RCLONE_CONF}" == *"RUNPOD_SECRET"* ]]; then
  log "warning: no rclone config (RunPod secret rclone_conf not passed): skipped"
  exit 0
fi

install_rclone() {
  if [ -x "$BIN_DIR/rclone" ]; then return 0; fi
  local tmp; tmp=$(mktemp -d)
  local base url
  for base in "https://downloads.rclone.org/$RCLONE_VERSION" \
              "https://github.com/rclone/rclone/releases/download/$RCLONE_VERSION"; do
    if curl -fsSL --max-time 300 -o "$tmp/$ZIP" "$base/$ZIP" \
        && curl -fsSL --max-time 60 -o "$tmp/SHA256SUMS" "$base/SHA256SUMS"; then
      url=$base
      break
    fi
  done
  if [ -z "${url:-}" ]; then log "warning: rclone $RCLONE_VERSION download failed"; return 1; fi
  local want got
  want=$(grep -E " \*?$ZIP\$" "$tmp/SHA256SUMS" | awk '{print $1}' | head -n 1)
  got=$(sha256sum "$tmp/$ZIP" | awk '{print $1}')
  if [ -z "$want" ] || [ "$want" != "$got" ]; then
    log "warning: rclone $ZIP checksum mismatch (want ${want:-none}, got $got): not installed"
    rm -rf "$tmp"; return 1
  fi
  (cd "$tmp" && python3 -m zipfile -e "$ZIP" .)
  mkdir -p "$BIN_DIR"
  install -m 755 "$tmp/rclone-$RCLONE_VERSION-linux-amd64/rclone" "$BIN_DIR/rclone"
  rm -rf "$tmp"
  log "rclone $RCLONE_VERSION installed from $url (sha256 ok)"
}

if ! install_rclone; then exit 0; fi
RCLONE="$BIN_DIR/rclone"

( umask 077; printf '%s\n' "$RCLONE_CONF" > "$CONF" )
REMOTE="${DRIVE_REMOTE:-$("$RCLONE" --config "$CONF" listremotes 2>/dev/null | head -n 1 | tr -d ':')}"
if [ -z "$REMOTE" ]; then log "warning: the rclone config has no remote: skipped"; exit 0; fi
FOLDER="${DRIVE_FOLDER:-WenArt}"
STAMP=$(date -u +%Y-%m-%d_%H%M)
rc=0
for p in "$@"; do
  src="$OUTPUTS/$p/export"
  files=()
  for f in "$src"/*.blend "$src"/*.glb; do [ -f "$f" ] && files+=("$(basename "$f")"); done
  if [ "${#files[@]}" -eq 0 ]; then log "$p: no 3D files in $src: skipped"; continue; fi
  dest="$REMOTE:$FOLDER/$p/$STAMP"
  log "$p: uploading ${files[*]} to $FOLDER/$p/$STAMP"
  if timeout "${DRIVE_TIMEOUT_S:-1200}" "$RCLONE" --config "$CONF" copy "$src" "$dest" \
      --include "*.blend" --include "*.glb" --drive-chunk-size 64M --transfers 2 --stats-one-line \
      --stats 30s >>"$LOG" 2>&1; then
    log "$p: uploaded"
  else
    log "warning: $p: upload failed (see $LOG)"
    rc=1
  fi
done
if [ "$rc" -ne 0 ]; then log "some uploads failed"; fi
exit 0
