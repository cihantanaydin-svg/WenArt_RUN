"""The ranking studio (31 Oct 2026, lesson UL217; user: "Is it possible to do furniture ranking system? we render the
furnitures and I ranked them from 10 to 0 based purely on the look? ... pod renders for example 10 beds or 20 and give
alphabetic order I gave that order a rank from 0 to 10?", then "page with score buttons, start with beds sofas
armchairs").

What:

- ``rank_entries(types)``: the models the fit may use of each type (``catalog.usable`` in the licence mode, the fit's
  bed rule ``fit.bed_usable``, a model file), in a fixed order (type, then id);
- ``studio_piece(entry)``: the piece the scene builder builds for a model: its catalogue size at scale 1, the fit's
  own asset record (``fit.model_asset``), so a bed frame gets its bedding and a sofa its fabric dressing exactly as
  in a house render;
- ``plan(...)``: one Blender job per model whose image is not current (``job_sha``), the sheets of ``PER_SHEET``
  models with the letters ``A``-``T``, the index (``ranking_index.json``: type -> sheets -> letter -> id, title,
  source);
- ``fit_distance(...)``, ``camera(...)``: the front 3/4 view that frames the built model's box (the same camera for
  every model: azimuth, elevation, lens; only the distance follows the size);
- ``compose_sheets(...)``: the lettered sheets (``sheets/<type>-NN.jpg``) and one tile per model
  (``tiles/<type>/<id>.jpg``) for the scoring page.

Why: the user ranks the models on their look alone: one studio, one light, one camera angle, a neutral floor and
backdrop; the score goes to ``results/library/user_ranks.json`` and the fit prefers the higher rank
(``wenart.furniture.user_ranks``).

How: pure Python but the drawing (PIL); the Blender side is ``blender_studio.py`` run by ``render.run_render``
(``script=STUDIO_SCRIPT``: workers, resume, a model that kills Blender recorded as failed). CLI:
``python -m wenart.assets.audit.studio plan|render|sheets``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import string
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import HERE

STUDIO_SCRIPT = HERE / "blender_studio.py"
STUDIO_VERSION = "ul217.1"
RANK_TYPES = ("bed_double", "sofa", "armchair")      # the user's first three types
# 31 Oct 2026 (user: "Give some other items for me to rank"): every other furniture type, by room (living, dining,
# bedroom, work, hall, plants, bathroom, kitchen), the first three last (already ranked)
ALL_TYPES = ("sofa_corner", "table_coffee", "side_table", "tv_unit", "floor_lamp", "ottoman", "bookshelf",
             "console_table", "sideboard", "display_cabinet", "chaise", "table_dining", "chair", "bar_stool", "bench",
             "nightstand", "wardrobe", "dresser", "bed_single", "bunk_bed", "crib", "desk", "office_chair",
             "shoe_cabinet", "tall_cabinet", "potted_plant", "washbasin", "toilet", "bathtub", "shower",
             "washing_machine", "stove", "sink_kitchen", "fridge") + RANK_TYPES
PER_SHEET = 20
LETTERS = string.ascii_uppercase[:PER_SHEET]          # A .. T
SETTINGS = {"resolution": 640, "samples": 96, "lens_mm": 50.0, "sensor_mm": 36.0, "azimuth_deg": 35.0,
            "elevation_deg": 16.0, "margin": 1.12, "floor_rgb": [0.72, 0.70, 0.67], "world": 0.5,
            "tile_px": 480, "sheet_tile_px": 384, "jpeg_quality": 86, "device": "auto"}
STYLE = {"source_text": "ranking studio: neutral", "family": "", "floor": {"material": "wood_oak_light"},
         "walls": {"material": "plaster_white"}, "ceiling": {"material": "plaster_white"},
         "lighting": {"mood": "studio"}}


# --------------------------------------------------------------------------
# The models and their pieces (pure)
# --------------------------------------------------------------------------

def catalogue_entries(library: Optional[dict] = None, polyhaven: Optional[dict] = None) -> list[dict]:
    """The furniture model entries of both catalogues (library ``entries``, then the Poly Haven models)."""
    from wenart.assets.audit import items as I
    library = library if library is not None else I.read_json(I.LIBRARY_PATH)
    polyhaven = polyhaven if polyhaven is not None else I.read_json(I.POLYHAVEN_PATH)
    out = []
    for doc in (library, polyhaven):
        for e in (doc or {}).get("entries") or []:
            if isinstance(e, dict) and e.get("id") and not e.get("parametric") and (e.get("glb") or e.get("gltf")):
                out.append(e)
    return out


def rank_entries(types=RANK_TYPES, mode: str = "relaxed", entries: Optional[list[dict]] = None) -> list[dict]:
    """The models of ``types`` the fit may use in licence ``mode``, ordered by the order of ``types``, then id."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F
    types = list(types)
    rows = [e for e in (entries if entries is not None else catalogue_entries())
            if e.get("type") in types and e.get("bbox_m") and C.usable(e, mode) and F.bed_usable(e)]
    return sorted(rows, key=lambda e: (types.index(e["type"]), str(e["id"])))


def studio_piece(entry: dict) -> dict:
    """The piece of a model in the studio: its catalogue box at scale 1, centred on the origin, front -Y, with the
    fit's asset record (``fit.model_asset``)."""
    from wenart.furniture import fit as F
    w, d, h = (float(v) for v in entry["bbox_m"])
    asset = F.model_asset(entry, entry["type"], w, d, [1.0, 1.0, 1.0])
    return {"id": "studio_piece", "type": entry["type"], "level_id": "L0", "room_id": "studio",
            "footprint": {"center": [0.0, 0.0], "size": [round(w, 4), round(d, 4)], "rotation_deg": 0.0},
            "height": round(h, 4), "front_deg": 270.0, "status": "verified", "source": "from_documents",
            "evidence": {"method": "inferred", "file": "ranking studio", "confidence": 1.0}, "asset": asset}


def job_sha(entry: dict, settings: dict) -> str:
    keys = ("glb", "gltf", "sha256_glb", "bbox_m", "unit_scale", "origin_offset", "front_axis", "up_axis",
            "bed_frame", "deck_height_m", "has_mattress", "has_bedding", "has_cushions", "material_slots")
    body = {"v": STUDIO_VERSION, "entry": {k: entry.get(k) for k in keys}, "settings": settings}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def image_path(work: Path, iid: str) -> Path:
    return Path(work) / "studio" / f"{iid}.png"


def sheet_plan(entries: list[dict], per_sheet: int = PER_SHEET) -> list[dict]:
    """``[{"sheet": "<type>-NN", "type", "number", "of", "letters": {letter: id}}]``: each type's models in order,
    ``per_sheet`` to a sheet, lettered from ``A``."""
    sheets: list[dict] = []
    by_type: dict[str, list[dict]] = {}
    for e in entries:
        by_type.setdefault(e["type"], []).append(e)
    for ftype, rows in by_type.items():
        count = math.ceil(len(rows) / per_sheet)
        for n in range(count):
            chunk = rows[n * per_sheet:(n + 1) * per_sheet]
            sheets.append({"sheet": f"{ftype}-{n + 1:02d}", "type": ftype, "number": n + 1, "of": count,
                           "letters": {LETTERS[i]: e["id"] for i, e in enumerate(chunk)}})
    return sheets


def index_doc(entries: list[dict], sheets: list[dict]) -> dict:
    """``ranking_index.json``: the sheets and every model's letter, title, source and size."""
    from wenart.assets.audit.render import ascii_text
    by_id = {e["id"]: e for e in entries}
    models = {}
    for s in sheets:
        for letter, iid in s["letters"].items():
            e = by_id[iid]
            models[iid] = {"type": e["type"], "sheet": s["sheet"], "letter": letter, "source": e.get("source"),
                           "title": ascii_text(e.get("title") or e.get("name") or "", 90),
                           "size_m": [round(float(v), 2) for v in e["bbox_m"]]}
    return {"schema_version": 1, "kind": "ranking_index", "version": STUDIO_VERSION, "lesson": "UL217",
            "per_sheet": PER_SHEET, "types": list(dict.fromkeys(s["type"] for s in sheets)), "sheets": sheets,
            "models": models}


def plan(entries: list[dict], assets: Path, work: Path, settings: Optional[dict] = None,
         deadline: Optional[float] = None) -> dict:
    """The Blender jobs (``render.run_render``'s doc) for the models whose image is not current, the sheets and the
    models whose file is missing."""
    from wenart.assets.audit import render as R
    settings = dict(SETTINGS, **(settings or {}))
    jobs, skipped, missing = [], [], []
    for e in entries:
        rel = e.get("glb") or e.get("gltf")
        path = Path(assets) / rel
        if not path.is_file():
            missing.append({"id": e["id"], "file": str(rel)})
            continue
        sha = job_sha(e, settings)
        rec = R.read_measure(work, e["id"])
        if rec and rec.get("job_sha") == sha and (
                (rec.get("ok") and image_path(work, e["id"]).is_file())
                or (not rec.get("ok") and int(rec.get("attempts", 1)) >= R.MAX_ATTEMPTS)):
            skipped.append(e["id"])
            continue
        attempt = int(rec.get("attempts", 1)) + 1 if rec and rec.get("job_sha") == sha and not rec.get("ok") else 1
        jobs.append({"id": e["id"], "type": e["type"], "file": str(path), "job_sha": sha, "attempt": attempt,
                     "piece": studio_piece(e), "measure": str(R.measure_path(work, e["id"])),
                     "image": str(image_path(work, e["id"]))})
    return {"version": STUDIO_VERSION, "settings": settings, "style": STYLE, "deadline": deadline,
            "work": str(work), "assets": str(assets), "jobs": jobs, "skipped": skipped, "missing": missing}


# --------------------------------------------------------------------------
# The camera (pure)
# --------------------------------------------------------------------------

def view_basis(azimuth_deg: float, elevation_deg: float) -> tuple[list[float], list[float], list[float]]:
    """``(forward, right, up)`` unit vectors of a camera looking at the model from the front (-Y) turned
    ``azimuth_deg`` toward the model's left (-X) and ``elevation_deg`` down."""
    az, el = math.radians(azimuth_deg), math.radians(elevation_deg)
    to_cam = [-math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)]
    forward = [-v for v in to_cam]
    right = [forward[1], -forward[0], 0.0]                     # forward x Z, horizontal
    n = math.hypot(right[0], right[1]) or 1.0
    right = [right[0] / n, right[1] / n, 0.0]
    up = [right[1] * forward[2] - right[2] * forward[1], right[2] * forward[0] - right[0] * forward[2],
          right[0] * forward[1] - right[1] * forward[0]]
    return forward, right, up


def fit_distance(corners: list, target: list, basis, lens_mm: float, sensor_mm: float, margin: float) -> float:
    """The distance from ``target`` along the view at which every corner lies inside the square frame with
    ``margin`` (pinhole camera, square sensor of ``sensor_mm``)."""
    forward, right, up = basis
    tan_half = (sensor_mm / 2.0) / lens_mm
    need = 0.0
    for c in corners:
        rel = [float(c[i]) - float(target[i]) for i in range(3)]
        x = sum(rel[i] * right[i] for i in range(3))
        y = sum(rel[i] * up[i] for i in range(3))
        z = sum(rel[i] * forward[i] for i in range(3))   # toward the far side: further from the camera
        need = max(need, z + abs(x) * margin / tan_half, z + abs(y) * margin / tan_half)
    return need


def camera(box_min: list, box_max: list, settings: Optional[dict] = None) -> dict:
    """``{"location", "target", "lens_mm"}`` of the front 3/4 view that frames the box."""
    s = dict(SETTINGS, **(settings or {}))
    target = [(float(a) + float(b)) / 2.0 for a, b in zip(box_min, box_max)]
    corners = [[x, y, z] for x in (box_min[0], box_max[0]) for y in (box_min[1], box_max[1])
               for z in (box_min[2], box_max[2])]
    basis = view_basis(float(s["azimuth_deg"]), float(s["elevation_deg"]))
    dist = fit_distance(corners, target, basis, float(s["lens_mm"]), float(s["sensor_mm"]), float(s["margin"]))
    loc = [target[i] - basis[0][i] * dist for i in range(3)]
    return {"location": [round(v, 4) for v in loc], "target": [round(v, 4) for v in target],
            "lens_mm": float(s["lens_mm"]), "distance": round(dist, 4)}


# --------------------------------------------------------------------------
# Sheets and tiles (PIL)
# --------------------------------------------------------------------------

def _font(size: int):
    from PIL import ImageFont
    for name in ("DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _tile(path: Optional[Path], px: int):
    from PIL import Image
    if path is None or not Path(path).is_file():
        img = Image.new("RGB", (px, px), (205, 205, 205))
        from PIL import ImageDraw
        ImageDraw.Draw(img).text((px // 2 - 60, px // 2 - 10), "not rendered", fill=(90, 90, 90), font=_font(20))
        return img
    return Image.open(path).convert("RGB").resize((px, px), Image.LANCZOS)


def compose_sheets(index: dict, work: Path, out: Path, settings: Optional[dict] = None,
                   log: Callable = print) -> dict:
    """``sheets/<sheet>.jpg`` (5 x 4 tiles, the letter in each corner, the sheet name on top) and
    ``tiles/<type>/<id>.jpg``; returns ``{"sheets": n, "tiles": n, "missing": [ids]}``."""
    from PIL import Image, ImageDraw
    s = dict(SETTINGS, **(settings or {}))
    out = Path(out)
    px, tpx, q = int(s["sheet_tile_px"]), int(s["tile_px"]), int(s["jpeg_quality"])
    cols, rows, head = 5, 4, 56
    missing: list[str] = []
    tiles = 0
    for sheet in index["sheets"]:
        img = Image.new("RGB", (cols * px, head + rows * px), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        draw.text((12, 12), f"{sheet['type']}  sheet {sheet['number']} of {sheet['of']}  ({sheet['sheet']})",
                  fill=(0, 0, 0), font=_font(28))
        for i, (letter, iid) in enumerate(sheet["letters"].items()):
            src = image_path(work, iid)
            if not src.is_file():
                missing.append(iid)
            t = _tile(src if src.is_file() else None, px)
            r, c = divmod(i, cols)
            img.paste(t, (c * px, head + r * px))
            draw.rectangle((c * px + 8, head + r * px + 8, c * px + 62, head + r * px + 62), fill=(20, 20, 20))
            draw.text((c * px + 20, head + r * px + 14), letter, fill=(255, 255, 255), font=_font(36))
            if src.is_file():
                tile_out = out / "tiles" / sheet["type"] / f"{iid}.jpg"
                tile_out.parent.mkdir(parents=True, exist_ok=True)
                _tile(src, tpx).save(tile_out, format="JPEG", quality=q)
                tiles += 1
        for c in range(1, cols):
            draw.line((c * px, head, c * px, head + rows * px), fill=(255, 255, 255), width=2)
        for r in range(1, rows):
            draw.line((0, head + r * px, cols * px, head + r * px), fill=(255, 255, 255), width=2)
        path = out / "sheets" / f"{sheet['sheet']}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(path, format="JPEG", quality=q)
    log(f"ranking studio: {len(index['sheets'])} sheet(s), {tiles} tile(s), {len(missing)} model(s) not rendered "
        f"-> {out}")
    return {"sheets": len(index["sheets"]), "tiles": tiles, "missing": missing}


def results_doc(index: dict, work: Path) -> dict:
    """The run's record (``studio_results.json``): per model ok / failed with the Blender record's method, warnings
    and seconds."""
    from wenart.assets.audit import render as R
    rows = {}
    for iid in index["models"]:
        rec = R.read_measure(work, iid) or {}
        rows[iid] = {k: rec.get(k) for k in ("ok", "error", "method", "fallback_reason", "seconds", "warnings",
                                             "dressing", "box_min", "box_max") if k in rec}
        rows[iid]["rendered"] = image_path(work, iid).is_file()
    ok = sum(1 for r in rows.values() if r.get("ok") and r.get("rendered"))
    return {"version": STUDIO_VERSION, "models": len(rows), "ok": ok, "failed": len(rows) - ok, "rows": rows}


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    from wenart.assets.audit import EXIT_OK
    from wenart.assets.audit import render as R
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.audit.studio", description=__doc__.split("\n\n")[0])
    ap.add_argument("action", choices=("plan", "render", "sheets"))
    ap.add_argument("--types", default=",".join(RANK_TYPES))
    ap.add_argument("--mode", default="relaxed")
    ap.add_argument("--assets", default="/workspace/assets")
    ap.add_argument("--work", default="/workspace/library-ranking/work")
    ap.add_argument("--out", default="results/library/ranking")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--blender", default=None)
    ap.add_argument("--deadline", default=None)
    ap.add_argument("--limit", type=int, default=0, help="at most this many models per type (a smoke run)")
    ap.add_argument("--samples", type=int, default=None)
    a = ap.parse_args(argv)
    types = [t for t in a.types.split(",") if t]
    entries = rank_entries(types, a.mode)
    if a.limit:
        kept: dict = {}
        entries = [e for e in entries if kept.setdefault(e["type"], []).append(e) or len(kept[e["type"]]) <= a.limit]
    sheets = sheet_plan(entries)
    index = index_doc(entries, sheets)
    out, work = Path(a.out), Path(a.work)
    out.mkdir(parents=True, exist_ok=True)
    (out / "ranking_index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    settings = {"samples": a.samples} if a.samples else None
    doc = plan(entries, Path(a.assets), work, settings, R.deadline_of(a.deadline))
    print(f"ranking studio: {len(entries)} model(s) of {types}: {len(doc['jobs'])} to render, {len(doc['skipped'])} "
          f"current, {len(doc['missing'])} file(s) missing; {len(sheets)} sheet(s)")
    if a.action == "plan":
        (out / "studio_plan.json").write_text(json.dumps({k: v for k, v in doc.items() if k != "jobs"} | {
            "jobs": [j["id"] for j in doc["jobs"]]}, indent=1) + "\n", encoding="utf-8")
        return EXIT_OK
    code = EXIT_OK
    if a.action == "render":
        t0 = time.time()
        code = R.run_render(doc, a.blender or R.default_blender(), work, a.workers, script=STUDIO_SCRIPT)
        print(f"ranking studio: render exit {code} in {time.time() - t0:.0f} s")
    compose_sheets(index, work, out, settings)
    res = results_doc(index, work)
    res["missing_files"] = doc["missing"]
    (out / "studio_results.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(f"ranking studio: {res['ok']} of {res['models']} model(s) rendered, {res['failed']} failed")
    return code


if __name__ == "__main__":
    sys.exit(main())
