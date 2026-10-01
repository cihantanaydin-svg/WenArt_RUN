#!/usr/bin/env bash
# One-time setup on a RunPod pod. Idempotent: everything lands under /workspace
# (the Network Volume), so later pods skip the finished steps.
# Base image: runpod/pytorch:1.4.0-cu1281-torch291-ubuntu2404 (torch 2.9.1 system-wide).
set -Eeuo pipefail
trap 'echo "[setup] ERROR at line $LINENO" >&2' ERR
WS=/workspace
mkdir -p $WS/logs $WS/hf $WS/tools $WS/jobs
log() { echo "[$(date -u +%H:%M:%S)] setup: $*"; }

# --- OS packages (container disk, fast) ---------------------------------------
STAMP_APT=/var/lib/wenart-apt-done
if [ ! -f $STAMP_APT ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends git curl xz-utils ca-certificates \
    libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 libsm6 libice6 \
    libglib2.0-0 poppler-utils >/dev/null
  touch $STAMP_APT
  log "apt packages installed"
fi

# --- Blender 5.2.2 LTS (sha256 verified, on the volume) -----------------------
BL_VER=5.2.2
BL_SHA=84098912789dc450e95697c4184fb8a90acbe5111c2ba4aede3fecb57806a168
BL_DIR=$WS/tools/blender-$BL_VER-linux-x64
if [ ! -x "$BL_DIR/blender" ]; then
  log "downloading Blender $BL_VER"
  TAR=$WS/tools/blender-$BL_VER-linux-x64.tar.xz
  curl -sSL --retry 3 -o "$TAR" "https://download.blender.org/release/Blender5.2/blender-$BL_VER-linux-x64.tar.xz"
  echo "$BL_SHA  $TAR" | sha256sum -c - >/dev/null
  tar -xJf "$TAR" -C $WS/tools
  rm -f "$TAR"
  log "Blender $BL_VER ready"
fi
ln -sfn "$BL_DIR" $WS/tools/blender

# --- Python venv (reuses the image's torch via system site packages) ----------
REQ_HASH=$(sha256sum "$(dirname "$0")/pod_requirements.txt" | cut -c1-16)
VENV=$WS/venv
if [ ! -f "$VENV/.req-$REQ_HASH" ]; then
  [ -x "$VENV/bin/python" ] || python3 -m venv --system-site-packages "$VENV"
  "$VENV/bin/pip" install -q --upgrade pip
  "$VENV/bin/pip" install -q -r "$(dirname "$0")/pod_requirements.txt"
  rm -f "$VENV"/.req-*; touch "$VENV/.req-$REQ_HASH"
  log "venv updated"
fi

log "done: python $("$VENV/bin/python" -V 2>&1), blender $("$BL_DIR/blender" --version 2>/dev/null | head -1)"
