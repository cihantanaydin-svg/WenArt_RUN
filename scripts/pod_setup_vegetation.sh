#!/usr/bin/env bash
# Milestone 13 (docs/milestone13.md §13.1, track T6): the vegetation setup on a RunPod pod. Idempotent and crash-safe:
# every step checks what is there before it does anything, a failed step is recorded, the others still run, and the
# result goes to a JSON status file (exit 1 when a required step failed).
#
# What:
#   1. the Sapling Tree Gen add-on (extension id ``sapling_tree_gen``, GPL-3.0-or-later, maintainer "Community",
#      Blender 4.4+; the 5.2 manual's "Extensions Command Line Arguments":
#      ``blender --command extension install [-s] [-e] PACKAGES`` installs from the enabled remote repositories
#      (``-s`` syncs the extensions platform first, ``-e`` enables; ``--online-mode`` allows the internet access the
#      sync needs) into the user repository ``user_default`` (``$HOME/.config/blender/5.2/extensions/user_default/``
#      on Linux, the 5.2 manual's directory layout); ``blender --command extension install-file -r user_default -e
#      FILE`` installs a package zip offline when ``WENART_SAPLING_ZIP`` names one (a mirror of the extension). The
#      add-on then runs as an installed program through ``bpy.ops.curve.tree_add`` (wenart/blender/vegetation.py);
#      nothing of it is copied into the repository. A folder with the add-on package (``WENART_SAPLING_DIR``) is the
#      last resort the build itself can load.
#   2. the Poly Haven CC0 tree, shrub and grass models of ``wenart.blender.vegetation.POLYHAVEN_MODELS`` through the
#      existing downloader ``python -m wenart.assets models fetch --ids ... --size 2k`` (wenart/assets/models.py:
#      glTF + textures into ``<assets>/models/<id>/``, recorded in ``<assets>/manifest.json`` with the measured box);
#      never a new downloader.
#   3. the ambientCG CC0 leaf atlases and bark of ``vegetation.LEAF_ATLASES`` (+ Bark014) through the existing
#      ``wenart.assets.fetch.fetch_texture`` (Color, NormalGL, Roughness into ``<assets>/textures/<id>/``).
#   4. a status JSON (``$ASSETS/vegetation_status.json`` and ``$WENART_RESULTS/vegetation_status.json`` when set):
#      the Sapling state (how it was installed, whether ``CURVE_OT_tree_add`` is registered in the pod's Blender),
#      every model and texture with its size, the failures.
#
# Why: the site build makes real trees (Poly Haven instances near the cameras, Sapling species-look trees elsewhere)
# and leaf-card hedges only when these are on the volume; without them it falls back to leaf-card trees (never a
# primitive) and says so in the scene manifest.
#
# How: run after scripts/pod_setup.sh (Blender 5.2.2 at /workspace/tools/blender, the venv at /workspace/venv, the
# repo at /workspace/repo). Logs in /workspace/logs/setup_vegetation.log. Env: WENART_ASSETS (/workspace/assets),
# WENART_BLENDER, WENART_PY, WENART_REPO, WENART_RESULTS, WENART_SAPLING_ZIP (optional offline package),
# VEG_MODEL_SIZE (2k), VEG_SKIP_MODELS=1 / VEG_SKIP_TEXTURES=1 / VEG_SKIP_SAPLING=1 to skip a step.
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
mkdir -p "$LOGS"
LOG=$LOGS/setup_vegetation.log
exec > >(tee -a "$LOG") 2>&1
REPO="${WENART_REPO:-$WS/repo}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
PY="${WENART_PY:-$WS/venv/bin/python}"
BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
SIZE="${VEG_MODEL_SIZE:-2k}"
STATUS="$ASSETS/vegetation_status.json"
EXT_ID="sapling_tree_gen"
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] setup_vegetation: $*"; }
on_error() { log "ERROR at line $1"; }
trap 'on_error $LINENO' ERR

cd "$REPO"
mkdir -p "$ASSETS"
export PYTHONPATH="$REPO${PYTHONPATH:+:$PYTHONPATH}"
log "assets $ASSETS, blender $("$BLENDER" --version 2>/dev/null | head -1 || echo missing), python $("$PY" --version 2>&1)"

# --- 1. Sapling Tree Gen ---------------------------------------------------------------------------------------
SAPLING_HOW="skipped"
sapling_registered() {
  # True when the pod's Blender registers the operator at start-up (the installed, enabled extension).
  "$BLENDER" -b --python-exit-code 1 --python-expr "import bpy, sys; sys.exit(0 if hasattr(bpy.types, 'CURVE_OT_tree_add') else 3)" >/dev/null 2>&1
}
if [ "${VEG_SKIP_SAPLING:-0}" = "1" ]; then
  log "sapling: skipped (VEG_SKIP_SAPLING=1)"
elif [ ! -x "$BLENDER" ]; then
  log "sapling: no Blender binary at $BLENDER"
  SAPLING_HOW="no blender"
  FAILED+=("sapling")
elif sapling_registered; then
  log "sapling: already registered ($EXT_ID)"
  SAPLING_HOW="already installed"
else
  if [ -n "${WENART_SAPLING_ZIP:-}" ] && [ -f "$WENART_SAPLING_ZIP" ]; then
    log "sapling: installing from the package file $WENART_SAPLING_ZIP into user_default"
    if "$BLENDER" --command extension install-file -r user_default -e "$WENART_SAPLING_ZIP"; then
      SAPLING_HOW="install-file"
    fi
  fi
  if [ "$SAPLING_HOW" = "skipped" ]; then
    log "sapling: installing $EXT_ID from extensions.blender.org (sync, enable; online mode)"
    if "$BLENDER" --online-mode --command extension install -s -e "$EXT_ID"; then
      SAPLING_HOW="extensions.blender.org"
    else
      log "sapling: the platform install failed (offline pod or a changed listing)"
      SAPLING_HOW="failed"
    fi
  fi
  if sapling_registered; then
    log "sapling: CURVE_OT_tree_add registered"
  else
    log "sapling: NOT registered after the install ($SAPLING_HOW); the build falls back to leaf-card trees"
    SAPLING_HOW="$SAPLING_HOW (not registered)"
    FAILED+=("sapling")
  fi
fi

# --- 2. Poly Haven tree, shrub and grass models (existing downloader) --------------------------------------------
MODEL_IDS=$("$PY" -c "from wenart.blender.vegetation import POLYHAVEN_MODELS as M; print(' '.join(M))")
MODELS_RC=0
if [ "${VEG_SKIP_MODELS:-0}" = "1" ]; then
  log "models: skipped (VEG_SKIP_MODELS=1)"
else
  log "models: $MODEL_IDS ($SIZE)"
  # shellcheck disable=SC2086
  "$PY" -m wenart.assets models fetch --assets "$ASSETS" --ids $MODEL_IDS --size "$SIZE" --strict || MODELS_RC=$?
  if [ "$MODELS_RC" -ne 0 ]; then
    log "models: some downloads failed (rc $MODELS_RC); the build uses what is there"
    FAILED+=("models")
  fi
fi

# --- 3. Leaf atlases and bark (existing texture fetcher) --------------------------------------------------------
TEX_RC=0
if [ "${VEG_SKIP_TEXTURES:-0}" = "1" ]; then
  log "textures: skipped (VEG_SKIP_TEXTURES=1)"
else
  "$PY" - "$ASSETS" "$SIZE" <<'PY' || TEX_RC=$?
import sys
from pathlib import Path
from wenart.assets import fetch, web
from wenart.blender.vegetation import LEAF_ATLASES
assets, size = Path(sys.argv[1]), sys.argv[2]
ids = sorted(set(LEAF_ATLASES.values())) + ["Bark014"]
failed = 0
for aid in ids:
    try:
        entry = fetch.fetch_texture(aid, assets, size)
        print(f"texture {aid}: {sorted(entry['files'])} ({entry.get('size_m')} m)")
    except (web.NetworkError, web.HTTPStatusError, fetch.AssetNotFound, KeyError) as exc:
        failed += 1
        print(f"texture {aid}: FAILED {type(exc).__name__}: {exc}")
sys.exit(1 if failed else 0)
PY
  if [ "$TEX_RC" -ne 0 ]; then
    log "textures: some fetches failed (rc $TEX_RC)"
    FAILED+=("textures")
  fi
fi

# --- 4. The status file -----------------------------------------------------------------------------------------
"$PY" - "$ASSETS" "$STATUS" "$SAPLING_HOW" "$SIZE" "$(IFS=,; echo "${FAILED[*]:-}")" "$("$BLENDER" --version 2>/dev/null | head -1 || echo missing)" <<'PY'
import json, sys, time
from pathlib import Path
from wenart.blender.vegetation import LEAF_ATLASES, POLYHAVEN_MODELS
assets, status, how, size, failed, blender = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
try:
    manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
except (OSError, ValueError):
    manifest = {}
models = {}
for aid in POLYHAVEN_MODELS:
    entry = (manifest.get("models") or {}).get(aid) or {}
    rel = (entry.get("files") or {}).get("gltf")
    path = assets / rel if rel else None
    models[aid] = {"ok": bool(path and path.is_file()), "gltf": rel, "bbox_m": entry.get("bbox_m"),
                   "polycount": entry.get("polycount"), "licence": entry.get("licence"),
                   "bytes": sum((assets / p).stat().st_size for p in (entry.get("files") or {}).values()
                                if (assets / p).is_file())}
textures = {}
for aid in sorted(set(LEAF_ATLASES.values())) + ["Bark014"]:
    entry = (manifest.get("textures") or {}).get(aid) or {}
    files = entry.get("files") or {}
    textures[aid] = {"ok": bool(files) and all((assets / p).is_file() for p in files.values()),
                     "maps": sorted(files), "licence": entry.get("licence"), "size_m": entry.get("size_m")}
out = {"written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "blender": blender,
       "sapling": {"extension_id": "sapling_tree_gen", "how": how, "registered": "not registered" not in how
                   and how not in ("failed", "no blender", "skipped")},
       "models": models, "models_ok": sum(1 for m in models.values() if m["ok"]), "models_total": len(models),
       "textures": textures, "textures_ok": sum(1 for t in textures.values() if t["ok"]),
       "model_size": size, "failed_steps": [f for f in failed.split(",") if f]}
status.parent.mkdir(parents=True, exist_ok=True)
status.write_text(json.dumps(out, indent=1), encoding="utf-8")
print(json.dumps({k: out[k] for k in ("sapling", "models_ok", "models_total", "textures_ok", "failed_steps")}))
PY
if [ -n "${WENART_RESULTS:-}" ]; then
  mkdir -p "$WENART_RESULTS"
  cp -f "$STATUS" "$WENART_RESULTS/vegetation_status.json"
fi
log "status written to $STATUS"
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]} (the build falls back where an asset is missing)"
  exit 1
fi
log "done"
