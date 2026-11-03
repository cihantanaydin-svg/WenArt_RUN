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


NESTED_MAX_BYTES = 400_000_000                   # a nested zip above this is listed, not opened
NESTED_DEPTH = 3
LISTED_EXTS = (".skp", ".json")                   # extracted for their facts (SketchUp version and preview, metadata)


def _copy(zf: zipfile.ZipFile, info: zipfile.ZipInfo, target: Path) -> None:
    if target.is_file() and target.stat().st_size == info.file_size:
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    with zf.open(info) as src, target.open("wb") as fh:
        while True:
            chunk = src.read(1 << 22)
            if not chunk:
                break
            fh.write(chunk)


def _scan_zip(zf: zipfile.ZipFile, prefix: str, depth: int, files: Path, out: dict) -> None:
    for info in zf.infolist():
        if info.is_dir():
            continue
        name = prefix + WH.member_name(info)
        ext = PurePosixPath(name.replace("\\", "/")).suffix.lower() or "(none)"
        out["members"].append({"name": name, "ext": ext, "bytes": info.file_size, "depth": depth})
        if ext not in MODEL_EXTS + SIDE_EXTS + LISTED_EXTS + (".zip",):
            continue
        rel = safe_rel(name)
        if rel is None or WH._is_link(info):
            if not any(part.startswith("__MACOSX") or part.startswith("._") for part in name.split("/")):
                out["refused"].append(name)
            continue
        if ext == ".zip":
            if depth >= NESTED_DEPTH or info.file_size > NESTED_MAX_BYTES:
                out["nested_skipped"].append(name)
                continue
            import io
            try:
                with zipfile.ZipFile(io.BytesIO(zf.read(info))) as inner:
                    out["nested"].append(name)
                    _scan_zip(inner, rel + "/", depth + 1, files, out)
            except zipfile.BadZipFile:
                out["nested_bad"].append(name)
            continue
        _copy(zf, info, files / rel)


def scan(zip_path: Path, work: Path) -> dict:
    """Every member listed, nested zips opened (``NESTED_DEPTH`` levels; a nested member's name is the zip's path,
    a slash and its own name); model files, side files (textures, .mtl, .bin), SketchUp files and JSON metadata
    extracted under their safe relative path into ``<work>/files``."""
    out: dict = {"members": [], "refused": [], "nested": [], "nested_skipped": [], "nested_bad": []}
    with zipfile.ZipFile(zip_path) as zf:
        _scan_zip(zf, "", 0, work / "files", out)
    by_ext: dict = {}
    for m in out["members"]:
        e = by_ext.setdefault(m["ext"], {"files": 0, "bytes": 0})
        e["files"] += 1
        e["bytes"] += m["bytes"]
    out["by_ext"] = dict(sorted(by_ext.items(), key=lambda kv: -kv[1]["bytes"]))
    return out


def model_list(work: Path) -> list[dict]:
    """``[{"id", "rel", "src", "format"}]``: every model file under ``<work>/files`` (a .bin or .mtl side file is no
    model of its own; a .gltf is), SketchUp files included (listed, not converted)."""
    out = []
    files = work / "files"
    if files.is_dir():
        for p in sorted(files.rglob("*")):
            if p.is_file() and p.suffix.lower() in MODEL_EXTS + (".skp",):
                rel = p.relative_to(files).as_posix()
                out.append({"id": uid_of(rel), "rel": rel, "src": str(p), "format": p.suffix.lower()})
    return out


def meta_for(rel: str, work: Path) -> dict:
    """The ``meta.json`` nearest to a model (its folder, then the parents inside the zip), or {}."""
    files = work / "files"
    parts = PurePosixPath(rel).parts[:-1]
    for i in range(len(parts), 0, -1):
        p = files.joinpath(*parts[:i], "meta.json")
        if p.is_file():
            try:
                return json.loads(p.read_text(encoding="utf-8", errors="replace"))
            except json.JSONDecodeError:
                return {"_unreadable": str(p.name)}
    return {}


def meta_title(meta: dict) -> Optional[str]:
    for k in ("name", "title", "product", "product_name", "model"):
        v = meta.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            for kk in ("name", "title"):
                if isinstance(v.get(kk), str):
                    return v[kk]
    return None


def skp_info(path: Path, preview_out: Optional[Path]) -> dict:
    """What a SketchUp file tells without SketchUp: the header ("SketchUp Model" in UTF-16 and the version in
    braces) and the embedded preview PNG (the largest PNG stream in the file, written to ``preview_out``)."""
    data = path.read_bytes()
    rec: dict = {"bytes": len(data)}
    head = data[:200]
    try:
        text = head.decode("utf-16-le", errors="ignore")
    except Exception:  # noqa: BLE001
        text = ""
    rec["header"] = "".join(ch for ch in text if 32 <= ord(ch) < 127)[:60]
    import re
    m = re.search(r"\{(\d+)\.(\d+)\.(\d+)\}", rec["header"])
    if m:
        rec["version"] = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
        rec["sketchup_year"] = (2000 + int(m.group(1))) if int(m.group(1)) >= 13 else None
    best = None
    i = 0
    sig = b"\x89PNG\r\n\x1a\n"
    while True:
        a = data.find(sig, i)
        if a < 0:
            break
        b = data.find(b"IEND", a)
        if b < 0:
            break
        b += 8
        if best is None or (b - a) > (best[1] - best[0]):
            best = (a, b)
        i = b
    if best and preview_out is not None:
        preview_out.parent.mkdir(parents=True, exist_ok=True)
        preview_out.write_bytes(data[best[0]:best[1]])
        rec["preview"] = str(preview_out)
        rec["preview_bytes"] = best[1] - best[0]
    return rec


def assimp_convert(src: Path, dst: Path, timeout_s: int = 300) -> dict:
    """``assimp export <src> <dst> -fglb2`` (the Open Asset Import Library's command-line tool, BSD-3), then the
    textures it names by path embedded (``embed_images``). ``{"ok", "tool", "error", "images"}``."""
    import shutil
    exe = shutil.which("assimp")
    if not exe:
        return {"ok": False, "error": "assimp not installed"}
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        p = subprocess.run([exe, "export", str(src), str(dst), "-fglb2"], capture_output=True, text=True,
                           timeout=timeout_s, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "tool": "assimp", "error": f"timed out after {timeout_s} s"}
    if p.returncode != 0 or not dst.is_file():
        return {"ok": False, "tool": "assimp", "error": (p.stdout + p.stderr)[-400:]}
    emb = embed_images(dst, src.parent)
    return {"ok": True, "tool": "assimp", "images": emb}


GREY_PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de0000000c4944415408d763"
                         "68686800000304018119e1b7e00000000049454e44ae426082")


def _find_file(name: str, base: Path) -> Optional[Path]:
    name = name.replace("\\", "/")
    p = base / name
    if p.is_file():
        return p
    stem = PurePosixPath(name).name.lower()
    for q in base.rglob("*"):
        if q.is_file() and q.name.lower() == stem:
            return q
    return None


TEXTURE_MAX_PX = 2048                   # a larger texture is scaled down (a library model needs no more)


def texture_bytes(data: bytes) -> tuple[bytes, str, Optional[str]]:
    """``(bytes, mime, change)`` of one texture as Blender's glTF importer reads it (3 Nov 2026, the Furnitures zips:
    CMYK JPEGs and TIFFs rendered magenta): a PNG or an RGB / grey JPEG under ``TEXTURE_MAX_PX`` stays as it is;
    anything else Pillow opens is written again (RGB JPEG, or PNG when it has alpha), scaled down to
    ``TEXTURE_MAX_PX``; what Pillow cannot open becomes the grey PNG. ``change`` says what was done (None: nothing)."""
    import io
    try:
        from PIL import Image
    except ImportError:                                   # no Pillow: keep PNG and JPEG, grey for the rest
        if data[:4] == b"\x89PNG":
            return data, "image/png", None
        if data[:2] == b"\xff\xd8":
            return data, "image/jpeg", None
        return GREY_PNG, "image/png", "not png/jpeg (no Pillow): grey"
    try:
        im = Image.open(io.BytesIO(data))
        im.load()
    except Exception:  # noqa: BLE001 - an unreadable texture becomes grey
        return GREY_PNG, "image/png", "unreadable image: grey"
    fmt, mode = (im.format or "").upper(), im.mode
    big = max(im.size) > TEXTURE_MAX_PX
    if not big and ((fmt == "PNG" and mode in ("RGB", "RGBA", "L", "LA", "P")) or
                    (fmt == "JPEG" and mode in ("RGB", "L"))):
        return data, "image/png" if fmt == "PNG" else "image/jpeg", None
    alpha = mode in ("RGBA", "LA") or (mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if alpha else "RGB")
    if big:
        im.thumbnail((TEXTURE_MAX_PX, TEXTURE_MAX_PX))
    buf = io.BytesIO()
    if alpha:
        im.save(buf, "PNG", optimize=True)
        mime = "image/png"
    else:
        im.save(buf, "JPEG", quality=88)
        mime = "image/jpeg"
    return buf.getvalue(), mime, f"{fmt or '?'} {mode}{' scaled' if big else ''} -> {mime}"


def embed_images(glb: Path, base: Path) -> dict:
    """Every image a GLB names by an external URI embedded into its binary chunk (the file searched under ``base``,
    case-insensitively by name); a missing one becomes a 1 x 1 grey PNG so the file stays self-contained."""
    doc, binary = WH.read_glb(glb)
    binary = bytearray(binary or b"")
    rec = {"embedded": 0, "missing": []}
    for img in doc.get("images") or []:
        uri = img.get("uri")
        if not uri or str(uri).startswith("data:"):
            continue
        import urllib.parse
        f = _find_file(urllib.parse.unquote(str(uri)), base)
        data = f.read_bytes() if f else GREY_PNG
        if f is None:
            rec["missing"].append(str(uri))
        data, mime, change = texture_bytes(data)
        if change:
            rec.setdefault("converted", []).append(f"{uri}: {change}")
        binary += b"\x00" * (-len(binary) % 4)
        views = doc.setdefault("bufferViews", [])
        views.append({"buffer": 0, "byteOffset": len(binary), "byteLength": len(data)})
        binary += data
        img.pop("uri", None)
        img["bufferView"] = len(views) - 1
        img["mimeType"] = mime
        if f is not None:
            rec["embedded"] += 1
    for img in doc.get("images") or []:                 # images already in the file (bufferView): the same check
        bv = img.get("bufferView")
        if not isinstance(bv, int) or img.get("_wenart_done"):
            continue
        view = doc["bufferViews"][bv]
        start = int(view.get("byteOffset", 0))
        data = bytes(binary[start:start + int(view["byteLength"])])
        new_data, mime, change = texture_bytes(data)
        if change:
            binary += b"\x00" * (-len(binary) % 4)
            doc["bufferViews"].append({"buffer": 0, "byteOffset": len(binary), "byteLength": len(new_data)})
            binary += new_data
            img["bufferView"] = len(doc["bufferViews"]) - 1
            img["mimeType"] = mime
            rec.setdefault("converted", []).append(f"image {bv}: {change}")
    bufs = doc.setdefault("buffers", [{}])
    if not bufs:
        bufs.append({})
    bufs[0].pop("uri", None)
    bufs[0]["byteLength"] = len(binary)
    WH.write_glb(glb, doc, bytes(binary))
    return rec


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
    if rec.get("format") == ".skp":
        sk = rec.get("skp") or {}
        return "needs_sketchup_export", [f"SketchUp {sk.get('sketchup_year') or sk.get('version') or '?'} file"
                                         + (", preview image saved" if sk.get("preview") else "")]
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
    for r in rows:                                     # a SketchUp file shows its own preview image
        prev = (r.get("skp") or {}).get("preview")
        if not r.get("render_front") and prev and Path(prev).is_file():
            r["render_front"] = prev
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
                    im = Image.open(p).convert("RGB")
                    im.thumbnail((tw, th))
                    sheet.paste(im, (x0 + j * tw, y0 + 40))
            box = r.get("box_m") or ["?", "?", "?"]
            label = (f"#{r['n']} {ascii_label(r.get('title') or r['rel'])}"
                     f" | {r.get('type')} {box[0]} x {box[1]} x {box[2]} m | {r.get('verdict')}")
            draw.text((x0 + 8, y0 + 6), label[:150], fill=(0, 0, 0))
            draw.text((x0 + 8, y0 + 22), "SketchUp preview (embedded in the file)" if r.get("format") == ".skp"
                      else "front view (-Y)            back view (+Y)", fill=(90, 90, 90))
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
    lines += ["", f"Nested zips opened: {len(scan_rec.get('nested') or [])}; skipped (too big or too deep): "
              f"{len(scan_rec.get('nested_skipped') or [])}; unreadable: {len(scan_rec.get('nested_bad') or [])}"]
    skps = [r for r in rows if r.get("format") == ".skp"]
    if skps:
        lines += ["", "## SketchUp files", "", "| # | model | version | file MB | preview |", "|---|---|---|---|---|"]
        for r in skps:
            sk = r.get("skp") or {}
            lines.append(f"| {r['n']} | {ascii_label(r.get('title') or r['rel'])} | {sk.get('version') or '?'} | "
                         f"{(sk.get('bytes') or 0) / 1e6:.1f} | {'yes' if sk.get('preview') else 'no'} |")
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
    conv: dict = {}
    for m in models:                                   # 3DS: Assimp first (Blender 5.2 has no 3DS importer built in)
        if m["format"] == ".3ds":
            try:
                r = assimp_convert(Path(m["src"]), work / "converted" / f"{m['id']}.glb")
            except Exception as exc:  # noqa: BLE001 - one model never stops the run (3 Nov 2026)
                r = {"ok": False, "tool": "assimp", "error": f"{type(exc).__name__}: {exc}"}
            if r.get("ok"):
                conv[m["id"]] = dict(r, importer="assimp")
            else:
                conv[m["id"] + ":assimp"] = r
    conv_jobs = [{"id": m["id"], "src": m["src"], "dst": str(work / "converted" / f"{m['id']}.glb")}
                 for m in models if m["format"] not in (".glb", ".skp") and m["id"] not in conv]
    if conv_jobs:
        conv.update(blender_run(args.blender, "convert", conv_jobs, work, timeout_s=3600))
    rows = []
    for n, m in enumerate(models, 1):
        meta = meta_for(m["rel"], work)
        title = meta_title(meta) or WH.clean_title(PurePosixPath(m["rel"]).parent.name or PurePosixPath(m["rel"]).stem)
        if m["format"] == ".skp":
            try:
                info = skp_info(Path(m["src"]), out / "skp_previews" / f"{n:03d}.png")
            except OSError as exc:
                info = {"error": str(exc)}
            rows.append({"n": n, "id": m["id"], "rel": m["rel"], "format": ".skp", "ok": False, "title": title,
                         "meta": meta, "skp": info,
                         "convert_error": "SketchUp file: no open-source reader on Linux; export to GLB or COLLADA "
                                          "from SketchUp first"})
            continue
        if m["format"] == ".glb":
            glb = Path(m["src"])
        else:
            c = conv.get(m["id"]) or {}
            if not c.get("ok"):
                err = c.get("error") or "not converted"
                a = conv.get(m["id"] + ":assimp")
                if a:
                    err = f"assimp: {a.get('error')}; blender: {err}"
                rows.append({"n": n, "id": m["id"], "rel": m["rel"], "format": m["format"], "ok": False,
                             "title": title, "meta": meta, "convert_error": err})
                continue
            glb = work / "converted" / f"{m['id']}.glb"
        try:
            rec = measure_one(m, glb, work, extra)
        except Exception as exc:  # noqa: BLE001 - one model never stops the run
            rec = {"id": m["id"], "rel": m["rel"], "format": m["format"], "ok": False,
                   "error": f"{type(exc).__name__}: {exc}"}
        rec.update(n=n, meta=meta, title=title)
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
    metas = {}
    for mp in sorted((work / "files").rglob("meta.json")) if (work / "files").is_dir() else []:
        try:
            metas[mp.relative_to(work / "files").as_posix()] = json.loads(mp.read_text(encoding="utf-8",
                                                                                      errors="replace"))
        except json.JSONDecodeError:
            metas[mp.relative_to(work / "files").as_posix()] = {"_unreadable": True}
    (out / "meta_all.json").write_text(json.dumps(metas, ensure_ascii=False, indent=1), encoding="utf-8")
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
