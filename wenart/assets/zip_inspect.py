"""Inspect a zip of 3D models before it joins the library (the user's request of 3 Nov 2026: "There is a beds.zip
file in Google Drive, take a look inside and tell me if we can use the models inside in the projects. Disregard the
licence things for now").

What it answers per model: the file format, whether Blender opens it, its type from its names (``warehouse.name_type``),
its real size after the unit and up-axis choice (``warehouse.choose`` against ``wenart.furniture.sizes``: metres,
inches, centimetres, millimetres, feet), triangles, materials, textures and PBR maps (``glbmesh.measure``), a
self-contained file, and two renders (front and back 3/4 views) on a 0.5 m checker floor. It only reads the zip and
writes under ``--work`` and ``--out``; nothing is added to the catalogue.

    python -m wenart.assets.zip_inspect run --zip Z.zip --work DIR --out RESULTS [--types bed_single,bed_double]
        [--blender PATH] [--no-render]

Steps: ``scan`` (every member: extension, size; GLB members through ``warehouse.extract``; the members of other 3D
formats and their side files (textures, .mtl, .bin) extracted under safe names), ``convert`` (non-GLB models to GLB
in Blender, ``zip_blender.py``), ``measure`` (type, unit, up axis, size check, fix-up into ``<work>/fixed/``),
``render`` (``zip_blender.py``), ``sheet`` (contact sheets) and ``report`` (``inspect.json``, ``inspect.csv``,
``report.md``). ``--types``: the types the zip is expected to hold; they join every model's name candidates, so a
bed whose file name says nothing is still measured against the bed ranges.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Optional

from wenart.assets import warehouse as WH

MODEL_EXTS = (".glb", ".gltf", ".fbx", ".obj", ".dae", ".blend", ".stl", ".ply", ".3ds", ".usd", ".usda", ".usdc",
              ".usdz")
# side files a non-GLB model may need (textures, materials, buffers)
SIDE_EXTS = (".mtl", ".bin", ".png", ".jpg", ".jpeg", ".tga", ".tif", ".tiff", ".bmp", ".exr", ".hdr", ".webp",
             ".dds")
# formats Blender cannot open: listed, never converted here
UNSUPPORTED_EXTS = (".max", ".skp", ".c4d", ".ma", ".mb", ".3dm", ".rfa", ".dwg", ".lwo", ".x", ".dxf")
NAME_MAX_BYTES = 200                              # a path part longer than this is refused (file-system name limit)
UID_PREFIX = "zip_"


def uid_of(rel: str) -> str:
    return UID_PREFIX + hashlib.sha256(str(rel).encode("utf-8")).hexdigest()[:20]


def safe_rel(name: str) -> Optional[str]:
    text = str(name).replace("\\", "/")
    if text.endswith("/"):
        return None
    p = PurePosixPath(text)
    if p.is_absolute() or any(part in ("..", "") for part in p.parts) or text[1:2] == ":":
        return None
    if any(part.startswith("__MACOSX") or part.startswith("._") for part in p.parts):
        return None
    if any(len(part.encode("utf-8")) > NAME_MAX_BYTES for part in p.parts):
        return None
    return str(p)


def scan(zip_path: Path, work: Path) -> dict:
    """Every member listed; the GLBs extracted by ``warehouse.extract`` into ``<work>/glb``; other model formats and
    every side file extracted under their safe relative path into ``<work>/files``."""
    members, refused = [], []
    files = work / "files"
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = WH.member_name(info)
            ext = PurePosixPath(name.replace("\\", "/")).suffix.lower() or "(none)"
            members.append({"name": name, "ext": ext, "bytes": info.file_size})
            if ext == ".glb":
                continue                                      # warehouse.extract below
            if ext not in MODEL_EXTS + SIDE_EXTS:
                continue
            rel = safe_rel(name)
            if rel is None or WH._is_link(info):
                refused.append(name)
                continue
            target = files / rel
            if target.is_file() and target.stat().st_size == info.file_size:
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as fh:
                while True:
                    chunk = src.read(1 << 22)
                    if not chunk:
                        break
                    fh.write(chunk)
    glb = WH.extract(zip_path, work / "glb")
    by_ext: dict = {}
    for m in members:
        e = by_ext.setdefault(m["ext"], {"files": 0, "bytes": 0})
        e["files"] += 1
        e["bytes"] += m["bytes"]
    return {"members": members, "by_ext": dict(sorted(by_ext.items(), key=lambda kv: -kv[1]["bytes"])),
            "refused": refused + glb["refused"], "glb_extract": {k: v for k, v in glb.items() if k != "refused"}}


def model_list(work: Path) -> list[dict]:
    """``[{"id", "rel", "src", "format"}]``: the extracted GLBs and the other model files (a .gltf, .bin or .mtl side
    file is no model of its own; a .gltf is)."""
    out = []
    for r in WH.list_glbs(work / "glb"):
        out.append({"id": uid_of(r["rel"]), "rel": r["rel"], "src": str(work / "glb" / r["file"]), "format": ".glb"})
    files = work / "files"
    if files.is_dir():
        for p in sorted(files.rglob("*")):
            if p.is_file() and p.suffix.lower() in MODEL_EXTS and p.suffix.lower() != ".glb":
                rel = p.relative_to(files).as_posix()
                out.append({"id": uid_of(rel), "rel": rel, "src": str(p), "format": p.suffix.lower()})
    return out


def blender_run(blender: str, mode: str, jobs: list, work: Path, timeout_s: int) -> dict:
    """The jobs through ``zip_blender.py``; returns ``{id: record}`` (a crash keeps the records written so far)."""
    if not jobs:
        return {}
    jobs_path = work / f"blender_{mode}_jobs.json"
    result = work / f"blender_{mode}_result.json"
    jobs_path.write_text(json.dumps({"mode": mode, "jobs": jobs, "result": str(result)}, indent=1), encoding="utf-8")
    script = Path(__file__).with_name("zip_blender.py")
    cmd = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(script), "--", str(jobs_path)]
    log = work / f"blender_{mode}.log"
    try:
        with log.open("w", encoding="utf-8") as fh:
            subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired:
        print(f"[zip_inspect] blender {mode} timed out after {timeout_s} s", flush=True)
    if not result.is_file():
        return {}
    return {r["id"]: r for r in json.loads(result.read_text(encoding="utf-8")).get("records", [])}


def candidates_for(rel: str, extra_types: list[str]) -> tuple[dict, list[str]]:
    names = WH.name_type(rel)
    cands = [c for c in names["candidates"] if c != WH.UNTYPED_OBJECT]
    for t in extra_types:
        if t not in cands:
            cands.append(t)
    return names, cands or [WH.UNTYPED_OBJECT]


def measure_one(model: dict, glb: Path, work: Path, extra_types: list[str]) -> dict:
    from wenart.assets.audit import glbmesh as GM
    from wenart.furniture import sizes as SZ
    rec: dict = {"id": model["id"], "rel": model["rel"], "format": model["format"], "ok": False,
                 "bytes": glb.stat().st_size}
    try:
        names, cands = candidates_for(model["rel"], extra_types)
        rec.update(title=names["title"], name_types=names["candidates"], name_where=names["where"],
                   candidates=cands)
        doc, _bin = WH.read_glb(glb)
        rec["generator"] = str((doc.get("asset") or {}).get("generator") or "")
        ext = WH.external_files(doc)
        if ext:
            rec["error"] = f"names external file(s) {ext[:3]}: not self-contained"
            return rec
        m0 = GM.measure(glb)
        pick = WH.choose(cands, m0["bbox_model_m"])
        rec.update(raw_box=m0["bbox_model_m"], type=pick["type"], unit=pick["unit"], factor=pick["factor"],
                   up_fix=pick["up_fix"], fits=pick["fits"], size_error=pick["error"], box_m=pick["box_m"],
                   triangles=m0["triangles"], vertices=m0["vertices"], info=m0["info"], pbr=m0["pbr"],
                   front_stats=m0.get("stats"))
        rng = SZ.real_range(pick["type"])
        if rng:
            rec["range"] = {k: list(v) if isinstance(v, tuple) else v for k, v in rng.items()}
        fixed = work / "fixed" / f"{model['id']}.glb"
        WH.fixup(glb, fixed, pick["type"], pick["factor"], pick["up_fix"])
        m1 = GM.measure(fixed)
        rec.update(ok=True, fixed=str(fixed), fixed_box_m=m1["bbox_model_m"])
    except Exception as exc:  # noqa: BLE001 - recorded per model
        rec["error"] = f"{type(exc).__name__}: {exc}"
    return rec


def verdict(rec: dict) -> tuple[str, list[str]]:
    """``usable`` | ``usable_with_fixes`` | ``not_usable`` and the reasons, from code facts only (the renders are
    looked at separately)."""
    notes: list[str] = []
    if not rec.get("ok"):
        return "not_usable", [rec.get("error") or rec.get("convert_error") or "not measured"]
    if not rec.get("fits"):
        notes.append(f"size outside the {rec['type']} range in every unit (error {rec.get('size_error')})")
    if rec.get("unit") != "metres":
        notes.append(f"unit {rec.get('unit')} (rescaled by {rec.get('factor')})")
    if rec.get("up_fix"):
        notes.append("exported Z-up (turned)")
    info = rec.get("info") or {}
    if not info.get("textured") and not info.get("vertex_colours"):
        notes.append("no textures (flat colours only)")
    tris = rec.get("triangles") or 0
    if tris > 1_500_000:
        notes.append(f"heavy mesh ({tris:,} triangles)")
    if tris < 500:
        notes.append(f"very low poly ({tris} triangles)")
    if rec.get("format") != ".glb":
        notes.append(f"converted from {rec['format']}")
    hard = (not rec.get("fits")) or tris < 500
    if hard:
        return "not_usable", notes
    return ("usable" if not [n for n in notes if not n.startswith("converted")] else "usable_with_fixes"), notes


def contact_sheets(rows: list[dict], out: Path, per_sheet: int = 12) -> list[str]:
    from PIL import Image, ImageDraw
    tiles = [r for r in rows if r.get("render_front") and Path(r["render_front"]).is_file()]
    sheets = []
    tw, th = 640, 480
    for s in range(0, len(tiles), per_sheet):
        chunk = tiles[s:s + per_sheet]
        cols = 2                                           # front | back per model, two models per row
        rows_n = (len(chunk) + 1) // 2
        sheet = Image.new("RGB", (tw * 2 * cols, (th + 40) * rows_n), (255, 255, 255))
        draw = ImageDraw.Draw(sheet)
        for i, r in enumerate(chunk):
            x0 = (i % 2) * tw * 2
            y0 = (i // 2) * (th + 40)
            for j, key in enumerate(("render_front", "render_back")):
                p = r.get(key)
                if p and Path(p).is_file():
                    sheet.paste(Image.open(p).convert("RGB"), (x0 + j * tw, y0 + 40))
            box = r.get("box_m") or ["?", "?", "?"]
            label = (f"#{r['n']} {ascii_label(r.get('title') or r['rel'])}"
                     f" | {r.get('type')} {box[0]} x {box[1]} x {box[2]} m | {r.get('verdict')}")
            draw.text((x0 + 8, y0 + 6), label[:150], fill=(0, 0, 0))
            draw.text((x0 + 8, y0 + 22), "front view (-Y)            back view (+Y)", fill=(90, 90, 90))
        name = f"sheet_{s // per_sheet + 1:02d}.jpg"
        sheet.save(out / name, quality=85)
        sheets.append(name)
    return sheets


def ascii_label(text: str, limit: int = 60) -> str:
    t = "".join(ch if 32 <= ord(ch) < 127 else "?" for ch in str(text))
    return t if len(t) <= limit else t[:limit - 1] + "~"


def write_report(scan_rec: dict, rows: list[dict], out: Path, zip_name: str, seconds: float) -> None:
    (out / "inspect.json").write_text(json.dumps({"zip": zip_name, "scan": {k: v for k, v in scan_rec.items()
                                                                            if k != "members"},
                                                  "members": scan_rec["members"], "models": rows},
                                                 ensure_ascii=False, indent=1), encoding="utf-8")
    cols = ["n", "rel", "format", "verdict", "type", "unit", "up_fix", "fits", "size_error", "box_m", "raw_box",
            "triangles", "textured", "pbr_maps", "materials", "images", "bytes", "notes", "error"]
    with (out / "inspect.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            info, pbr = r.get("info") or {}, r.get("pbr") or {}
            maps = "+".join(k for k in ("base_colour", "metallic_roughness", "normal", "occlusion") if pbr.get(k))
            w.writerow([r.get("n"), r.get("rel"), r.get("format"), r.get("verdict"), r.get("type"), r.get("unit"),
                        r.get("up_fix"), r.get("fits"), r.get("size_error"), r.get("box_m"), r.get("raw_box"),
                        r.get("triangles"), info.get("textured"), maps, info.get("materials"), info.get("images"),
                        r.get("bytes"), "; ".join(r.get("notes") or []), r.get("error") or r.get("convert_error")])
    counts: dict = {}
    for r in rows:
        counts[r.get("verdict")] = counts.get(r.get("verdict"), 0) + 1
    lines = [f"# Inspection of {zip_name}", "", f"{len(scan_rec['members'])} files in the zip, {len(rows)} models, "
             f"{seconds / 60:.1f} min.", "", "## Files by extension", "", "| ext | files | MB |", "|---|---|---|"]
    for ext, e in scan_rec["by_ext"].items():
        lines.append(f"| {ext} | {e['files']} | {e['bytes'] / 1e6:.1f} |")
    lines += ["", "## Verdicts (code facts only)", "", "| verdict | models |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(counts.items(), key=lambda kv: str(kv[0]))]
    lines += ["", "## Models", "", "| # | model | format | type | box m (w x d x h) | unit | tris | textures | verdict | "
              "notes |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        box = r.get("box_m")
        b = f"{box[0]:.2f} x {box[1]:.2f} x {box[2]:.2f}" if box else "-"
        info, pbr = r.get("info") or {}, r.get("pbr") or {}
        tex = "+".join(k for k in ("base_colour", "metallic_roughness", "normal") if pbr.get(k)) or (
            "vertex colours" if info.get("vertex_colours") else "none")
        lines.append(f"| {r['n']} | {ascii_label(r.get('title') or r['rel'])} | {r['format']} | {r.get('type') or '-'} "
                     f"| {b} | {r.get('unit') or '-'} | {r.get('triangles') or '-'} | {tex} | {r.get('verdict')} | "
                     f"{'; '.join(r.get('notes') or [])[:160]} |")
    if scan_rec.get("refused"):
        lines += ["", f"Refused members (unsafe path or name too long): {len(scan_rec['refused'])}"]
    unsup = {e: v for e, v in scan_rec["by_ext"].items() if e in UNSUPPORTED_EXTS}
    if unsup:
        lines += ["", "Formats Blender cannot open (not inspected): " +
                  ", ".join(f"{e} ({v['files']})" for e, v in unsup.items())]
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args) -> int:
    t0 = time.time()
    zip_path, work, out = Path(args.zip), Path(args.work), Path(args.out)
    work.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    extra = [t for t in (args.types or "").split(",") if t]
    print(f"[zip_inspect] scan {zip_path.name}", flush=True)
    sc = scan(zip_path, work)
    print(f"[zip_inspect] {len(sc['members'])} members: " +
          ", ".join(f"{e} {v['files']}" for e, v in list(sc["by_ext"].items())[:12]), flush=True)
    models = model_list(work)
    print(f"[zip_inspect] {len(models)} model files", flush=True)
    conv_jobs = [{"id": m["id"], "src": m["src"], "dst": str(work / "converted" / f"{m['id']}.glb")}
                 for m in models if m["format"] != ".glb"]
    conv = blender_run(args.blender, "convert", conv_jobs, work, timeout_s=3600) if conv_jobs else {}
    rows = []
    for n, m in enumerate(models, 1):
        if m["format"] == ".glb":
            glb = Path(m["src"])
        else:
            c = conv.get(m["id"]) or {}
            if not c.get("ok"):
                rows.append({"n": n, "id": m["id"], "rel": m["rel"], "format": m["format"], "ok": False,
                             "title": WH.clean_title(PurePosixPath(m["rel"]).stem),
                             "convert_error": c.get("error") or "not converted"})
                continue
            glb = work / "converted" / f"{m['id']}.glb"
        rec = measure_one(m, glb, work, extra)
        rec["n"] = n
        if m["format"] != ".glb":
            rec["convert"] = {k: conv[m["id"]].get(k) for k in ("importer", "objects", "meshes", "images")}
        rows.append(rec)
    if not args.no_render:
        rjobs = [{"id": r["id"], "src": r["fixed"], "out_front": str(out / "renders" / f"{r['n']:03d}_front.png"),
                  "out_back": str(out / "renders" / f"{r['n']:03d}_back.png")} for r in rows if r.get("ok")]
        (out / "renders").mkdir(exist_ok=True)
        rr = blender_run(args.blender, "render", rjobs, work, timeout_s=int(args.render_minutes * 60))
        for r in rows:
            j = rr.get(r["id"]) or {}
            if j.get("ok"):
                r["render_front"] = str(out / "renders" / f"{r['n']:03d}_front.png")
                r["render_back"] = str(out / "renders" / f"{r['n']:03d}_back.png")
            elif r.get("ok"):
                r["render_error"] = j.get("error") or "not rendered"
    for r in rows:
        r["verdict"], r["notes"] = verdict(r)
        if r.get("render_error"):
            r["notes"].append(f"render failed: {r['render_error']}")
    try:
        sheets = contact_sheets(rows, out)
    except Exception as exc:  # noqa: BLE001 - the table stays useful without sheets
        print(f"[zip_inspect] contact sheets failed: {exc}", flush=True)
        sheets = []
    write_report(sc, rows, out, zip_path.name, time.time() - t0)
    print(f"[zip_inspect] done: {len(rows)} models, {len(sheets)} sheet(s), {time.time() - t0:.0f} s", flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.zip_inspect")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--zip", required=True)
    r.add_argument("--work", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--types", default="", help="expected types, comma-separated (e.g. bed_single,bed_double)")
    r.add_argument("--blender", default=os.environ.get("WENART_BLENDER", "blender"))
    r.add_argument("--no-render", action="store_true")
    r.add_argument("--render-minutes", type=float, default=60.0)
    a = ap.parse_args(argv)
    return run(a)


if __name__ == "__main__":
    sys.exit(main())
