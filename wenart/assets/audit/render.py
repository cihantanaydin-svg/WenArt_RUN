"""The audit's renders (docs/milestone12.md §6.1 thumbnails, pod P2): every model at its catalogue scale in four views
with a scale reference, the dimensions printed, and its mesh measured; every texture set as a 1 m sample.

What:

- ``reference_layout(box, settings)``: the scene around a model in the piece frame (front -Y, floor z = 0): a floor
  with a grid (0.5 m; 0.1 m for items below ``small_item_m``), a 1.75 m person silhouette and a 0.45 m seat-height
  bar on the model's left (-X: they hide nothing in the side view from +X), all as boxes.
- ``camera_specs(layout, settings)``: front 3/4 (perspective, from the front turned toward the model's left), side
  (orthographic from +X), top (orthographic) and back (perspective, from +Y).
- ``render_jobs(...)``: one job per model (its file, ``unit_scale``, ``origin_offset``, the re-orientation, the
  layout, the cameras, the output paths); a job whose measurement is current (same ``job_sha``) is skipped (resume).
- ``run_render(...)``: ``blender -b --python wenart/assets/audit/blender_audit.py -- <jobs>`` in ``workers``
  processes (jobs dealt round-robin, deterministic), until ``deadline``.
- ``compose_sheet(...)``: the 2 x 2 sheet (1024 px) with a header band: id, type, source, licence, the dimensions
  and the scale reference, the title (ASCII); ``texture_overlay(...)``: a 10 cm grid on a texture sample.

Why: the M8-M10 judges saw 256 px tiles framed on the model with no scale and no title (§1.6); a stretched table lamp
passed as a floor lamp. Next to a person and a seat bar on a metric grid a wrong size shows.

How: everything but the Blender process is pure Python (CPU tests); the Blender side builds boxes from the layout,
imports the model, applies ``unit_scale``, ``-origin_offset`` and the turn of ``catalog.reorient_rotation_deg``,
measures the mesh with ``meshstats.analyse`` and renders (Cycles, GPU when available). Layout and cameras are
computed from the catalogue box, so a model whose mesh disagrees with its catalogue box shows it.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import EXIT_DEADLINE, EXIT_NOTHING, EXIT_OK, HERE

BLENDER_SCRIPT = HERE / "blender_audit.py"
VIEWS = ("front34", "side", "top", "back")
VIEW_LABELS = ("0 front 3/4", "1 side (+X)", "2 top", "3 back")
RENDER_VERSION = "m12.1"


# --------------------------------------------------------------------------
# Scale reference and cameras (pure)
# --------------------------------------------------------------------------

def person_boxes(height: float = 1.75, x: float = 0.0, y: float = 0.0) -> list[dict]:
    """A standing person as boxes (legs, torso, arms, neck, head) whose top is exactly ``height``, centred on ``x``,
    ``y``, facing -Y. Proportions of an adult (head 1/8 of the height)."""
    k = height / 1.75
    half_t = 0.06 * k                                        # thickness / 2

    def b(x0, x1, z0, z1, t=half_t):
        return {"min": [round(x + x0 * k, 4), round(y - t, 4), round(z0 * k, 4)],
                "max": [round(x + x1 * k, 4), round(y + t, 4), round(z1 * k, 4)]}
    return [b(-0.17, -0.03, 0.0, 0.84), b(0.03, 0.17, 0.0, 0.84),          # legs
            b(-0.21, 0.21, 0.84, 1.45),                                      # torso
            b(-0.29, -0.215, 0.80, 1.43), b(0.215, 0.29, 0.80, 1.43),        # arms
            b(-0.05, 0.05, 1.45, 1.53),                                      # neck
            b(-0.095, 0.095, 1.53, 1.75, t=0.095 * k)]                       # head


def seat_bar_boxes(height: float = 0.45, x: float = 0.0, y: float = 0.0) -> list[dict]:
    """A post with a crossbar whose top is at ``height`` (a chair seat's height)."""
    return [{"min": [round(x - 0.015, 4), round(y - 0.015, 4), 0.0], "max": [round(x + 0.015, 4), round(y + 0.015, 4),
                                                                             round(height, 4)]},
            {"min": [round(x - 0.15, 4), round(y - 0.02, 4), round(height - 0.03, 4)],
             "max": [round(x + 0.15, 4), round(y + 0.02, 4), round(height, 4)]}]


def grid_lines(xmin: float, xmax: float, ymin: float, ymax: float, step: float, width: float) -> list[dict]:
    """Thin boxes on the floor every ``step`` metres (lines at multiples of ``step``, so the origin is on a line)."""
    out = []
    i0, i1 = math.floor(xmin / step + 1e-9), math.ceil(xmax / step - 1e-9)
    j0, j1 = math.floor(ymin / step + 1e-9), math.ceil(ymax / step - 1e-9)
    h = 0.0015
    for i in range(i0, i1 + 1):
        xv = round(i * step, 4)
        out.append({"min": [round(xv - width / 2, 5), round(j0 * step, 4), 0.0],
                    "max": [round(xv + width / 2, 5), round(j1 * step, 4), h]})
    for j in range(j0, j1 + 1):
        yv = round(j * step, 4)
        out.append({"min": [round(i0 * step, 4), round(yv - width / 2, 5), 0.0],
                    "max": [round(i1 * step, 4), round(yv + width / 2, 5), h]})
    return out


def _union(boxes: list[dict]) -> dict:
    return {"min": [min(b["min"][i] for b in boxes) for i in range(3)],
            "max": [max(b["max"][i] for b in boxes) for i in range(3)]}


def reference_layout(box, settings: dict) -> dict:
    """The scene around a model of size ``box`` (w, d, h) standing at the piece origin: ``model`` (its box),
    ``person`` and ``bar`` boxes on its left, ``grid`` lines, the ``floor`` box and the ``frame`` box the cameras
    show. Items whose largest side is below ``small_item_m`` get no person (it would shrink them to a few pixels) and a
    0.1 m grid."""
    w, d, h = (max(float(v), 1e-3) for v in box)
    small = max(w, d, h) < float(settings.get("small_item_m", 0.6))
    gap = float(settings.get("reference_gap_m", 0.3))
    model = {"min": [-w / 2, -d / 2, 0.0], "max": [w / 2, d / 2, h]}
    bar_x = -w / 2 - gap - 0.15
    bar = seat_bar_boxes(float(settings.get("seat_bar_m", 0.45)), bar_x, 0.0)
    person = [] if small else person_boxes(float(settings.get("person_height_m", 1.75)), bar_x - 0.15 - gap - 0.3, 0.0)
    frame = _union([model] + bar + person)
    step = 0.1 if small else float(settings.get("grid_m", 0.5))
    pad = step
    gx0, gx1 = frame["min"][0] - pad, frame["max"][0] + pad
    gy0, gy1 = min(frame["min"][1], -d / 2) - pad, max(frame["max"][1], d / 2) + pad
    lines = grid_lines(gx0, gx1, gy0, gy1, step, 0.004 if small else 0.012)
    floor = {"min": [math.floor(gx0 / step) * step, math.floor(gy0 / step) * step, -0.01],
             "max": [math.ceil(gx1 / step) * step, math.ceil(gy1 / step) * step, 0.0]}
    return {"model": model, "person": person, "bar": bar, "grid": lines, "grid_m": step, "floor": floor,
            "frame": frame, "small": small}


def camera_distance(extents, lens_mm: float, sensor_mm: float = 36.0, margin: float = 1.1) -> float:
    """Distance at which a sphere around the box fills the frame (perspective)."""
    radius = 0.5 * math.sqrt(sum(float(e) ** 2 for e in extents))
    half_fov = math.atan(sensor_mm / (2.0 * lens_mm))
    return margin * radius / math.sin(half_fov)


def camera_specs(layout: dict, settings: dict) -> list[dict]:
    """The four cameras: ``{"view", "type": persp | ortho, "location", "target", "lens_mm"?, "ortho_scale"?}``."""
    fr = layout["frame"]
    centre = [(a + b) / 2.0 for a, b in zip(fr["min"], fr["max"])]
    ext = [b - a for a, b in zip(fr["min"], fr["max"])]
    lens, sensor = float(settings.get("lens_mm", 50)), float(settings.get("sensor_mm", 36))
    margin = float(settings.get("margin", 1.1))
    el = math.radians(float(settings.get("elevation_deg", 22)))
    dist = camera_distance(ext, lens, sensor, margin)

    def persp(az_deg: float, view: str) -> dict:
        az = math.radians(az_deg)                 # 0 = from -Y (the front); positive turns toward -X
        dx, dy = -math.sin(az), -math.cos(az)
        loc = [centre[0] + dist * math.cos(el) * dx, centre[1] + dist * math.cos(el) * dy,
               centre[2] + dist * math.sin(el)]
        return {"view": view, "type": "persp", "location": [round(v, 4) for v in loc],
                "target": [round(v, 4) for v in centre], "lens_mm": lens}
    side_scale = margin * max(ext[1], ext[2])
    top_scale = margin * max(ext[0], ext[1])
    far = 2.0 * max(ext) + 5.0
    return [persp(-float(settings.get("front_azimuth_deg", -35)), "front34"),
            {"view": "side", "type": "ortho", "location": [round(fr["max"][0] + far, 4), round(centre[1], 4),
                                                           round(centre[2], 4)],
             "target": [round(v, 4) for v in centre], "ortho_scale": round(side_scale, 4)},
            {"view": "top", "type": "ortho", "location": [round(centre[0], 4), round(centre[1], 4),
                                                          round(fr["max"][2] + far, 4)],
             "target": [round(centre[0], 4), round(centre[1], 4), 0.0], "ortho_scale": round(top_scale, 4)},
            persp(180.0 + float(settings.get("front_azimuth_deg", -35)), "back")]


def reorient_deg(item: dict) -> float:
    from wenart.furniture import catalog as C
    return float(C.reorient_rotation_deg({"front_axis": item.get("front_axis", "-Y")}))


# --------------------------------------------------------------------------
# Jobs and the Blender run
# --------------------------------------------------------------------------

def job_sha(item: dict, settings: dict, file_sha: Optional[str]) -> str:
    body = {"v": RENDER_VERSION, "file": file_sha, "unit_scale": item.get("unit_scale", 1.0),
            "origin_offset": item.get("origin_offset"), "front_axis": item.get("front_axis"), "box": item.get("bbox_m"),
            "settings": {k: settings.get(k) for k in sorted(settings) if k not in ("workers", "seconds_per_item")}}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode("utf-8")).hexdigest()


def measure_path(work: Path, iid: str) -> Path:
    return Path(work) / "measure" / f"{iid}.json"


def view_paths(work: Path, iid: str) -> list[Path]:
    return [Path(work) / "views" / f"{iid}_{i}.png" for i in range(len(VIEWS))]


def measure_done(work: Path, iid: str, sha: str) -> bool:
    p = measure_path(work, iid)
    if not p.is_file():
        return False
    try:
        rec = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return False
    return rec.get("job_sha") == sha and (not rec.get("ok") or all(v.is_file() for v in view_paths(work, iid)))


def render_jobs(items: list[dict], assets: Path, work: Path, settings: dict, deadline: Optional[float] = None
                ) -> dict:
    """``{"settings", "deadline", "work", "jobs": [...], "skipped": [...], "missing": [...]}``: a job per item whose
    model file is in ``assets`` and whose measurement is not current."""
    from wenart.assets.audit.items import model_file
    jobs, skipped, missing = [], [], []
    for it in items:
        rel = model_file(it)
        path = Path(assets) / rel if rel else None
        if path is None or not path.is_file():
            missing.append({"id": it["id"], "file": str(rel)})
            continue
        sha = job_sha(it, settings, it.get("sha256_glb") or str(rel))
        if measure_done(work, it["id"], sha):
            skipped.append(it["id"])
            continue
        box = it.get("bbox_m") or [1.0, 1.0, 1.0]
        layout = reference_layout(box, settings)
        jobs.append({"id": it["id"], "type": it["type"], "kind": it["kind"], "file": str(path), "job_sha": sha,
                     "unit_scale": float(it.get("unit_scale", 1.0)), "origin_offset": it.get("origin_offset")
                     or [0.0, 0.0, 0.0], "rot_deg": reorient_deg(it), "layout": layout,
                     "cameras": camera_specs(layout, settings),
                     "measure": str(measure_path(work, it["id"])),
                     "views": [str(p) for p in view_paths(work, it["id"])]})
    return {"version": RENDER_VERSION, "settings": settings, "deadline": deadline, "work": str(work), "jobs": jobs,
            "skipped": skipped, "missing": missing}


def deal(jobs: list, workers: int) -> list[list]:
    """Round-robin split of the jobs over ``workers`` processes (deterministic)."""
    workers = max(1, int(workers))
    return [jobs[i::workers] for i in range(workers) if jobs[i::workers]]


def blender_command(blender: str, jobs_path: Path) -> list[str]:
    return [str(blender), "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(BLENDER_SCRIPT), "--",
            str(jobs_path)]


def run_render(doc: dict, blender: str, work: Path, workers: int = 1, log: Callable = print,
               popen: Callable = subprocess.Popen) -> int:
    """Run the jobs of ``doc`` in ``workers`` Blender processes; exit 0 all done, 3 deadline, 1 Blender failed."""
    work = Path(work)
    (work / "jobs").mkdir(parents=True, exist_ok=True)
    chunks = deal(doc["jobs"], workers)
    if not chunks:
        log("audit render: nothing to render")
        return EXIT_OK
    procs = []
    for n, chunk in enumerate(chunks):
        jp = work / "jobs" / f"jobs_{n}.json"
        jp.write_text(json.dumps(dict(doc, jobs=chunk, worker=n), indent=1), encoding="utf-8")
        lp = work / "jobs" / f"blender_{n}.log"
        fh = open(lp, "w", encoding="utf-8")
        procs.append((popen(blender_command(blender, jp), stdout=fh, stderr=subprocess.STDOUT), fh, n))
        log(f"audit render: worker {n}: {len(chunk)} job(s), log {lp}")
    codes = []
    for proc, fh, n in procs:
        codes.append(proc.wait())
        fh.close()
    log(f"audit render: worker exit codes {codes}")
    if any(c == EXIT_DEADLINE for c in codes):
        return EXIT_DEADLINE
    return EXIT_OK if all(c == 0 for c in codes) else EXIT_NOTHING


def read_measures(work: Path) -> dict:
    """``{id: measurement}`` of every ``measure/<id>.json`` in ``work``."""
    out = {}
    for p in sorted((Path(work) / "measure").glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            continue
        out[rec.get("id") or p.stem] = rec
    return out


# --------------------------------------------------------------------------
# Sheets (CPU, after Blender)
# --------------------------------------------------------------------------

def ascii_text(text: str, limit: int = 110) -> str:
    """The title for cv2's Hershey font: accents folded, other characters dropped."""
    import unicodedata
    t = unicodedata.normalize("NFKD", str(text or ""))
    t = "".join(c for c in t if not unicodedata.combining(c) and 32 <= ord(c) < 127)
    t = " ".join(t.split())
    return t if len(t) <= limit else t[:limit - 3] + "..."


def header_lines(item: dict, box, grid_m: float, small: bool) -> list[str]:
    w, d, h = (float(v) for v in box)
    ref = "seat bar 0.45 m" if small else "person 1.75 m, seat bar 0.45 m"
    return [ascii_text(f"{item['id']} | {item['type']} | {item.get('source')} | {item.get('licence')}", 120),
            f"W {w:.2f} x D {d:.2f} x H {h:.2f} m (catalogue scale) | {ref} | grid {grid_m:g} m",
            ascii_text(item.get("title") or "", 120)]


def compose_sheet(view_files: list[Path], lines: list[str], out_path: Path, tile: int = 512, quality: int = 88
                  ) -> dict:
    """The 2 x 2 sheet with a header band (``lines``) and a label per tile; JPEG. Returns its pixel hash."""
    import cv2
    import numpy as np
    from PIL import Image
    band = 26 * len(lines) + 12
    sheet = np.full((band + 2 * tile, 2 * tile, 3), 255, dtype=np.uint8)
    for i, path in enumerate(view_files):
        img = Image.open(path).convert("RGB")
        if img.size != (tile, tile):
            img = img.resize((tile, tile), Image.LANCZOS)
        r, c = divmod(i, 2)
        sheet[band + r * tile:band + (r + 1) * tile, c * tile:(c + 1) * tile] = np.asarray(img, dtype=np.uint8)
    sheet = np.ascontiguousarray(sheet)
    for n, line in enumerate(lines):
        cv2.putText(sheet, line, (8, 24 + 26 * n), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_8)
    for i, label in enumerate(VIEW_LABELS[:len(view_files)]):
        r, c = divmod(i, 2)
        x, y = c * tile, band + r * tile
        cv2.rectangle(sheet, (x + 4, y + 4), (x + 150, y + 30), (255, 255, 255), -1, cv2.LINE_8)
        cv2.putText(sheet, label, (x + 8, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_8)
    sheet[band + tile - 1:band + tile + 1, :] = 40
    sheet[band:, tile - 1:tile + 1] = 40
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = out_path.with_name(out_path.name + ".tmp.jpg")
    Image.fromarray(sheet).save(tmp, format="JPEG", quality=int(quality))
    tmp.replace(out_path)
    from wenart.assets.objaverse import pixels_sha256
    return pixels_sha256(out_path)


def texture_overlay(image, size_px: int, step_m: float = 0.1, sample_m: float = 1.0):
    """A ``size_px`` square RGB array of a 1 m texture sample with a grid line every ``step_m`` (pure numpy)."""
    import numpy as np
    arr = np.array(image, dtype=np.uint8, copy=True)
    n = int(round(sample_m / step_m))
    for k in range(n + 1):
        p = min(size_px - 1, int(round(k * size_px / n)))
        arr[:, max(0, p - 1):p + 1] = (255, 255, 255)
        arr[max(0, p - 1):p + 1, :] = (255, 255, 255)
    return arr


def sheet_path(audit: Path, item: dict) -> Path:
    return Path(audit) / "sheets" / item["type"] / f"{item['id']}.jpg"


def compose_all(items: list[dict], work: Path, audit: Path, settings: dict, log: Callable = print) -> dict:
    """A sheet per measured item (``sheets/<type>/<id>.jpg``) and ``measure.json`` (every measurement, no views);
    sheets already newer than their views are kept."""
    measures = read_measures(work)
    made = kept = 0
    index = {}
    for it in items:
        m = measures.get(it["id"])
        if not m or not m.get("ok"):
            continue
        views = view_paths(work, it["id"])
        if not all(v.is_file() for v in views):
            continue
        out = sheet_path(audit, it)
        lay = reference_layout(it.get("bbox_m") or m.get("size"), settings)
        if out.is_file() and out.stat().st_mtime >= max(v.stat().st_mtime for v in views) and m.get("sheet_sha256"):
            kept += 1
        else:
            px = compose_sheet(views, header_lines(it, m.get("size") or it["bbox_m"], lay["grid_m"], lay["small"]),
                               out, int(settings.get("resolution", 512)), int(settings.get("sheet_jpeg_quality", 88)))
            m["sheet_sha256"] = px["sha256"]
            measure_path(work, it["id"]).write_text(json.dumps(m, indent=1), encoding="utf-8")
            made += 1
        index[it["id"]] = str(out.relative_to(audit))
    doc = {"version": RENDER_VERSION, "measures": {k: {kk: vv for kk, vv in v.items() if kk != "views"}
                                                   for k, v in sorted(measures.items())}, "sheets": index}
    Path(audit).mkdir(parents=True, exist_ok=True)
    (Path(audit) / "measure.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"audit render: {made} sheet(s) made, {kept} kept, {len(measures)} measurement(s) -> {audit}")
    return doc


# --------------------------------------------------------------------------
# Texture samples
# --------------------------------------------------------------------------

def texture_jobs(manifest: dict, assets: Path, work: Path) -> list[dict]:
    """A 1 m sample job per texture set of the assets manifest (``textures``: ``files`` albedo / normal / roughness
    relative to the assets folder, ``size_m`` the real size one image covers)."""
    jobs = []
    for tid, t in sorted((manifest.get("textures") or {}).items()):
        files = {k: str(Path(assets) / v) for k, v in (t.get("files") or {}).items() if v}
        if not files.get("albedo") or not Path(files["albedo"]).is_file():
            continue
        out = Path(work) / "textures" / f"{tid}.png"
        if out.is_file():
            continue
        jobs.append({"id": tid, "files": files, "size_m": t.get("size_m") or [1.0, 1.0], "out": str(out)})
    return jobs


def overlay_textures(work: Path, audit: Path, settings: dict, log: Callable = print) -> int:
    from PIL import Image
    n = 0
    px = int(settings.get("texture_px", 512))
    for p in sorted((Path(work) / "textures").glob("*.png")):
        out = Path(audit) / "textures" / f"{p.stem}.jpg"
        if out.is_file() and out.stat().st_mtime >= p.stat().st_mtime:
            continue
        img = Image.open(p).convert("RGB").resize((px, px), Image.LANCZOS)
        arr = texture_overlay(img, px, float(settings.get("texture_grid_m", 0.1)))
        out.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(arr).save(out, format="JPEG", quality=88)
        n += 1
    log(f"audit render: {n} texture sample(s) with the 10 cm grid -> {Path(audit) / 'textures'}")
    return n


def deadline_of(value) -> Optional[float]:
    if value is None:
        value = os.environ.get("WENART_DEADLINE")
    try:
        return float(value) if value not in (None, "") else None
    except ValueError:
        return None


def now() -> float:
    return time.time()


def default_blender() -> str:
    return os.environ.get("WENART_BLENDER") or "blender"


def python_exe() -> str:
    return sys.executable
