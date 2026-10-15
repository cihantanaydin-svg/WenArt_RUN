#!/usr/bin/env bash
# Milestone 13 site A/B job (docs/milestone13.md §13.3, track T6; pod P1 runs it through scripts/jobs/m13_p1.sh).
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and
# WENART_DEADLINE set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender; the vegetation
# assets and the Sapling extension from scripts/pod_setup_vegetation.sh).
#
# What: for every site variant of WENART_SITE_VARIANT (wenart/blender/site.py site_levers: base = every lever off (the
# Milestone 12 site layout; its trees are still leaf-card shrubs at the crown-class height, never a primitive),
# hedge, instances, sapling, platforms, pools, sky = one lever on, all = everything on) the 3 fixed exterior views of
# real04 (ext_1 corner, ext_5 aerial, ext_7 site view: searched, no camera records are committed) and of real02 (ext_1,
# ext_5, ext_6 replayed from the committed Milestone 11 scene manifest with WENART_CAMERAS_FROM) are built from the
# committed baseline building (results/furniture/<p>/building_final.json through wenart.run.ab m13-prepare) and
# rendered at AB_SAMPLES (128) into outputs/<p>/ab_m13/site/<variant>/; the render manifest (seconds, EV, VRAM per
# view), the previews, the site block of the scene manifest (hedges, platforms, vegetation per source, levers) and the
# variant's nvidia-smi peak go to $RESULTS/ab_m13/site/<variant>/<p>/, one contact sheet per project and view (every
# variant side by side) to $RESULTS/ab_m13/site/sheets/ and the numbers to $RESULTS/ab_m13/site/summary.{json,md}.
# The GPU tests of the track (tests/gpu/test_m13_site.py) run at the end when time is left.
#
# Why: the lead decides from these images and numbers which site levers stay on (P1), and sees the cost of the
# Poly Haven instances and the Sapling trees in seconds and VRAM per view; every variant renders the same cameras.
#
# How: one Blender build and one render per project and variant (the build fingerprint carries the brief and the
# camera file, not the site variant: the site output folder is per variant, so --reuse never mixes them); every stage
# is timed, a failing stage is recorded and the job goes on (exit 1 at the end); results are copied after every stage
# and from the EXIT trap. The deadline (WENART_DEADLINE, epoch seconds) is checked before every variant with
# AB_VARIANT_EST_S (default 240 s per project and variant); the pod_entry.sh watchdog stops the pod at MAX_RUNTIME_S
# whatever happens here. Idempotent: outputs and renders live on the volume.
#
# Env: AB_PROJECTS (default "real04 real02"), AB_VARIANTS (default all eight), AB_SAMPLES (128), AB_RES (1920x1080),
#      AB_VARIANT_EST_S (240), AB_GPU_TESTS (1 = run tests/gpu/test_m13_site.py at the end), AB_BASELINE_DIR (default
#      results/renders/{name}: the committed baseline files of real02; real04 has none), WENART_LICENCE_MODE (unset =
#      the project brief), WENART_ASSETS (/workspace/assets), SITE_AB_VIEWS_<project> (the camera names, comma
#      separated; defaults above).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-site_ab}"
LOG=$LOGS/site_ab-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
export WENART_ASSETS="$ASSETS"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export WENART_OUTPUTS="$REPO/outputs"
if [ -n "${WENART_LICENCE_MODE:-}" ]; then export WENART_LICENCE_MODE; fi
SAMPLES="${AB_SAMPLES:-128}"
RES="${AB_RES:-1920x1080}"
EST_S="${AB_VARIANT_EST_S:-240}"
BASELINE_DIR="${AB_BASELINE_DIR:-$REPO/results/renders/{name}}"
read -r -a PROJECTS <<< "${AB_PROJECTS:-real04 real02}"
read -r -a VARIANTS <<< "${AB_VARIANTS:-base hedge instances sapling platforms pools sky all}"
AB_OUT=$RESULTS/ab_m13/site
FAILED=()
SKIPPED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] site_ab: $*"; }

# views_for <project>: the 3 fixed exterior views (SITE_AB_VIEWS_<project> overrides).
views_for() {
  local var="SITE_AB_VIEWS_$1"
  if [ -n "${!var:-}" ]; then echo "${!var}"; return; fi
  case "$1" in
    real04) echo "ext_1,ext_5,ext_7" ;;
    real02) echo "ext_1,ext_5,ext_6" ;;
    *) echo "ext_1,ext_5,ext_6" ;;
  esac
}

seconds_left() {
  case "${WENART_DEADLINE:-}" in
    ''|*[!0-9.]*) echo 999999 ;;
    *) echo $(( ${WENART_DEADLINE%.*} - $(date +%s) )) ;;
  esac
}

copy_results() {
  # Small files only: the render manifest, the previews, the site block of the scene manifest, the VRAM peak and the
  # logs. Full-size PNGs and EXR passes stay on the volume.
  mkdir -p "$AB_OUT"
  local p v src dst
  for p in "${PROJECTS[@]}"; do
    for v in "${VARIANTS[@]}"; do
      src=$REPO/outputs/$p/ab_m13/site/$v
      [ -d "$src" ] || continue
      dst=$AB_OUT/$v/$p
      mkdir -p "$dst"
      if [ -d "$src/renders" ]; then
        find "$src/renders" -maxdepth 1 -type f \( -name 'render_manifest.json' -o -name '*.log' -o -name 'vram.json' \) \
          -exec cp -f {} "$dst/" \;
        find "$src/renders" -maxdepth 1 -type f -name '*_preview.jpg' -size -400k -exec cp -f {} "$dst/" \;
      fi
      if [ -f "$src/scene/scene_manifest.json" ]; then
        "$PY" - "$src/scene/scene_manifest.json" "$dst/site.json" <<'PY' || true
import json, sys
m = json.load(open(sys.argv[1]))
whole = m.get("whole_building") or {}
site = whole.get("site") or {}
cams = [c for c in m.get("cameras") or [] if c.get("kind") == "exterior"]
keep = {"levers": site.get("levers"), "climate": site.get("climate"), "hedges": site.get("hedges"),
        "platforms": site.get("platforms"), "vegetation": site.get("vegetation"), "grass": site.get("grass"),
        "facade_details": whole.get("facade_details"),
        "cameras": [{k: c.get(k) for k in ("name", "view", "position", "target", "lens_mm", "pitch_deg", "horizon_frac",
                                             "score", "source", "dropped_reason")} for c in cams],
        "objects_by_kind": {}}
for o in m.get("objects") or []:
    k = o.get("kind") or "?"
    keep["objects_by_kind"][k] = keep["objects_by_kind"].get(k, 0) + 1
json.dump(keep, open(sys.argv[2], "w"), indent=1)
PY
        cp -f "$src/scene/build.log" "$dst/" 2>/dev/null || true
      fi
    done
    # the baseline previews of the fixed views (the "before" column of the sheets), where committed
    local base=${BASELINE_DIR//\{name\}/$p}
    if [ -d "$base" ]; then
      mkdir -p "$AB_OUT/baseline/$p"
      for cam in $(views_for "$p" | tr ',' ' '); do
        cp -f "$base/${cam}_preview.jpg" "$AB_OUT/baseline/$p/" 2>/dev/null || true
      done
    fi
  done
  cp -f "$LOG" "$AB_OUT/" 2>/dev/null || true
  log "results copied to $AB_OUT: $(find "$AB_OUT" -type f | wc -l) files"
}

on_error() { log "ERROR at line $1"; exit 1; }
trap 'on_error $LINENO' ERR
on_exit() { trap - ERR; copy_results; }
trap 'on_exit' EXIT
trap 'exit 143' TERM

run_stage() {
  local name=$1; shift
  local t0; t0=$(date +%s)
  log "stage start: $name"
  local rc=0
  "$@" || rc=$?
  log "stage end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  copy_results
  return 0
}

stage_failed() {
  local f
  for f in "${FAILED[@]}"; do [ "$f" = "$1" ] && return 0; done
  return 1
}

vram_sampler() {
  local file=$1
  : > "$file"
  while true; do
    nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 >> "$file" || true
    sleep 1
  done
}

write_vram_json() {
  local samples=$1 out=$2
  "$PY" - "$samples" "$out" <<'PY' || true
import json, sys
vals = []
for line in open(sys.argv[1]):
    line = line.strip()
    if line.replace(".", "").isdigit():
        vals.append(int(float(line)))
json.dump({"peak_mib": max(vals) if vals else None, "samples": len(vals), "source": "nvidia-smi memory.used, 1 s"},
          open(sys.argv[2], "w"), indent=1)
PY
}

cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" outputs "$AB_OUT"
log "job $JOB, projects: ${PROJECTS[*]}, variants: ${VARIANTS[*]}, samples $SAMPLES, res $RES, deadline in $(seconds_left) s, blender $("$WENART_BLENDER" --version 2>/dev/null | head -1)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
[ -f "$ASSETS/vegetation_status.json" ] && log "vegetation assets: $(cat "$ASSETS/vegetation_status.json" | tr -d '\n' | cut -c1-300)" \
  || log "no vegetation_status.json in $ASSETS (scripts/pod_setup_vegetation.sh not run): leaf-card trees only"

# 1. The baseline files of every project into outputs/<p>/ab/m13/ (the committed building; real02's cameras).
for p in "${PROJECTS[@]}"; do
  base=${BASELINE_DIR//\{name\}/$p}
  if [ -d "$base" ]; then
    run_stage "prepare-$p" "$PY" -m wenart.run.ab m13-prepare --project "$p" --project-out "outputs/$p" --from "$base"
  else
    run_stage "prepare-$p" "$PY" -m wenart.run.ab m13-prepare --project "$p" --project-out "outputs/$p"
  fi
  m13=outputs/$p/ab/m13
  mkdir -p "$m13"
  if [ ! -f "$m13/building_final.json" ] && [ -f "results/furniture/$p/building_final.json" ]; then
    cp -f "results/furniture/$p/building_final.json" "$m13/building_final.json"
    log "$p: the committed results/furniture/$p/building_final.json stands in for the baseline building"
  fi
  if [ -f "$m13/style.json" ]; then
    run_stage "assets-$p" "$PY" -m wenart.assets fetch --style "$m13/style.json" --assets "$ASSETS" --size 2k
  fi
done

# 2. Build and render per project and variant.
for v in "${VARIANTS[@]}"; do
  for p in "${PROJECTS[@]}"; do
    m13=outputs/$p/ab/m13
    if [ ! -f "$m13/building_final.json" ]; then
      log "$p: no baseline building (prepare failed?), variant $v skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    left=$(seconds_left)
    if [ "$left" -lt "$EST_S" ]; then
      log "$p $v: $left s left before WENART_DEADLINE (< $EST_S s): skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    views=$(views_for "$p")
    out=outputs/$p/ab_m13/site/$v
    mkdir -p "$out"
    export WENART_SITE_VARIANT="$v"
    if [ -f "$m13/scene_manifest.json" ]; then
      export WENART_CAMERAS_FROM="$m13/scene_manifest.json"     # real02: the Milestone 11 cameras replayed
    else
      unset WENART_CAMERAS_FROM                                  # real04: searched (no records committed)
    fi
    unset WENART_CAMERAS_EXTRA
    STYLE_ARG=(); [ -f "$m13/style.json" ] && STYLE_ARG=(--style "$m13/style.json")
    ASSET_ARG=(); [ -f "$ASSETS/manifest.json" ] && ASSET_ARG=(--assets "$ASSETS")
    run_stage "build-$p-$v" "$PY" -m wenart.blender.cli build --building "$m13/building_final.json" \
      "${STYLE_ARG[@]}" "${ASSET_ARG[@]}" --out "$out/scene" --preview-samples 4 --camera-policy search \
      --brief "projects/$p"
    if stage_failed "build-$p-$v" || [ ! -f "$out/scene/scene.blend" ]; then
      log "$p $v: build failed, render skipped"
      continue
    fi
    # the fixed views that exist in this build (a dropped camera is reported, not an error)
    have=$("$PY" - "$out/scene/scene_manifest.json" "$views" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
names = {c.get("name") for c in m.get("cameras") or []}
want = sys.argv[2].split(",")
print(",".join(w for w in want if w in names))
PY
)
    if [ -z "$have" ]; then
      log "$p $v: none of the views $views exist in the scene manifest; render skipped"
      FAILED+=("views-$p-$v"); continue
    fi
    [ "$have" != "$views" ] && log "$p $v: views $views -> $have (missing ones were dropped by the camera search)"
    mkdir -p "$out/renders"
    vram_sampler "$out/renders/vram_samples.txt" &
    SAMPLER=$!
    run_stage "render-$p-$v" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" \
      --out "$out/renders" --cameras "$have" --samples "$SAMPLES" --res "$RES" \
      --exposure auto --white-balance project --preview-quality 85
    kill "$SAMPLER" 2>/dev/null || true
    wait "$SAMPLER" 2>/dev/null || true
    write_vram_json "$out/renders/vram_samples.txt" "$out/renders/vram.json"
    [ -f "$out/renders/render.log" ] && grep -E "^(DEVICE|RENDERED|RERENDER|SKIP|RENDER_INCOMPLETE)" "$out/renders/render.log" || true
    copy_results
  done
done
unset WENART_SITE_VARIANT WENART_CAMERAS_FROM

# 3. Contact sheets (one per project and view, the variants side by side, PIL) and the summary.
"$PY" - "$AB_OUT" "$(IFS=,; echo "${PROJECTS[*]}")" "$(IFS=,; echo "${VARIANTS[*]}")" "$(views_for real04)" "$(views_for real02)" <<'PY' || FAILED+=("sheets")
import json, sys
from pathlib import Path
out = Path(sys.argv[1]); projects = sys.argv[2].split(","); variants = sys.argv[3].split(",")
views = {"real04": sys.argv[4].split(","), "real02": sys.argv[5].split(",")}
try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
summary = {"projects": {}, "variants": variants, "samples": None}
sheets = out / "sheets"; sheets.mkdir(parents=True, exist_ok=True)
for p in projects:
    summary["projects"][p] = {}
    for cam in views.get(p) or views["real02"]:
        tiles = []
        base = out / "baseline" / p / f"{cam}_preview.jpg"
        if base.is_file():
            tiles.append(("m11 baseline", base))
        for v in variants:
            f = out / v / p / f"{cam}_preview.jpg"
            if f.is_file():
                tiles.append((v, f))
            try:
                rm = json.load(open(out / v / p / "render_manifest.json"))
                rec = next((r for r in (rm.get("renders") or rm.get("cameras") or []) if r.get("name") == cam or r.get("camera") == cam), None)
            except (OSError, ValueError):
                rec = None
            try:
                vram = json.load(open(out / v / p / "vram.json")).get("peak_mib")
            except (OSError, ValueError):
                vram = None
            summary["projects"][p].setdefault(cam, {})[v] = {
                "seconds": (rec or {}).get("seconds"), "ev": ((rec or {}).get("exposure") or {}).get("ev") if isinstance((rec or {}).get("exposure"), dict) else (rec or {}).get("ev"),
                "vram_mib_view": (rec or {}).get("vram_mib"), "vram_peak_mib": vram, "preview": f.is_file()}
        if Image is not None and tiles:
            w = 480
            ims = []
            for label, f in tiles:
                im = Image.open(f).convert("RGB")
                im = im.resize((w, max(1, round(im.height * w / im.width))), Image.Resampling.LANCZOS)
                ims.append((label, im))
            h = max(im.height for _, im in ims)
            sheet = Image.new("RGB", (len(ims) * (w + 8) + 8, h + 36), (24, 24, 24))
            draw = ImageDraw.Draw(sheet)
            for k, (label, im) in enumerate(ims):
                x = 8 + k * (w + 8)
                sheet.paste(im, (x, 28))
                draw.text((x + 4, 6), f"{p} {cam} {label}", fill=(240, 240, 240))
            sheet.save(sheets / f"{p}_{cam}.jpg", quality=85)
json.dump(summary, open(out / "summary.json", "w"), indent=1)
lines = ["# Site A/B (Milestone 13, T6)", "", "| project | view | variant | seconds | EV | VRAM view MiB | VRAM peak MiB |", "|---|---|---|---|---|---|---|"]
for p, cams in summary["projects"].items():
    for cam, vs in cams.items():
        for v, r in vs.items():
            lines.append(f"| {p} | {cam} | {v} | {r['seconds']} | {r['ev']} | {r['vram_mib_view']} | {r['vram_peak_mib']} |")
(out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"site_ab: {len(list(sheets.glob('*.jpg')))} sheets, summary in {out}")
PY

# 4. The track's GPU tests (small scenes; skipped when the deadline is near).
if [ "${AB_GPU_TESTS:-1}" = "1" ] && [ "$(seconds_left)" -gt "$EST_S" ]; then
  run_stage gpu-tests "$PY" -m pytest -m gpu tests/gpu/test_m13_site.py -v -ra --junitxml="$RESULTS/junit-m13-site.xml"
else
  log "GPU tests skipped (AB_GPU_TESTS=${AB_GPU_TESTS:-1}, $(seconds_left) s left)"
fi

copy_results
if [ "${#SKIPPED[@]}" -gt 0 ]; then log "skipped (deadline or missing baseline): ${SKIPPED[*]}"; fi
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
  exit 1
fi
log "all stages ok"
