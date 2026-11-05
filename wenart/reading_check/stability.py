"""The stability test of the reader (5 Nov 2026, Milestone 14 track R8; user: "I want structure recognition to be
cumulatively better with the feedbacks I am giving").

What: ``python -m wenart.reading_check.stability --projects synthetic-06,real07 [--variants mirror,rotate90,mm,layers,
nodims] [--work DIR] [--json OUT]`` reads each project again after five changes of its DXF and scores every variant's
reading against the ORIGINAL reading as its truth, with the matcher of ``score.py`` (its constants are not touched):

- ``mirror``: x scaled by -1 about the drawing's centre; ``rotate90``: turned 90 degrees about the centre;
- ``mm``: every entity scaled to millimetres and ``$INSUNITS`` set to 4 (a cm, inch or m drawing; a mm drawing is
  skipped); dimension texts stay as written, so the reader must decide the unit from the header and the door widths;
  the result records the unit the reader chose;
- ``layers``: every layer renamed ``L1, L2, ...`` (layer ``0`` and ``Defpoints`` keep their names: CAD gives them a
  meaning), also inside blocks;
- ``nodims``: TEXT / MTEXT that are bare numbers, dimension values, level marks or lie on a layer whose name means
  dimension are removed; room labels, titles and size tags like ``90/210`` stay; the count removed is recorded;
- ``identity`` (not in the default list): the DXF unchanged, the control that shows the noise of reading the converted
  DXF again.

Before matching, the variant's elements are mapped back into the original frame (mirror and rotation about the
aligned centres of each level's walls; the registration may shift the building frame) and the variant's levels get
the original level ids (by elevation). A median shift of matched wall mid-points removes what the centre of two
slightly different wall sets leaves (``REFINE``). Findings: one per element of the original that no variant element
matches (``lost``) and one per element the variant adds (``added``), grouped per level in ``fragile`` of
``work/stability/<project>.json``; the table prints the counts per variant.

Why: the reader has about 40,000 lines of rules, many keyed on one drafter's habits (layer names, text layers,
orientation, units). A reading that changes when the same drawing is mirrored, rotated, rescaled or has its layers
renamed is fragile at that spot, and nobody could see it. A place that changes is a finding and a ranker example.

How: ezdxf (MIT) transforms; ``regress.read_project`` and ``pipeline.run_project(no_ai=True)`` read; pure functions
for the transforms, the mapping and the findings; nothing is written under ``projects/`` or ``results/``.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import shutil
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Optional

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

REPO = Path(__file__).resolve().parents[2]
PROJECTS_DIR = REPO / "projects"
VARIANTS = ("mirror", "rotate90", "mm", "layers", "nodims")
ALL_VARIANTS = VARIANTS + ("identity",)
GEOMETRIC = ("mirror", "rotate90")
MM_INSUNITS = 4
LAYERS_KEEP = ("0", "defpoints")
DIM_LAYER_WORDS = ("OLCU", "DIM", "DIMENSION", "KOT", "COTE", "MASS")
NUMBER_RE = re.compile(r"^[+\-±−]?\s*\d+(?:[.,]\d+)?(?:\s*(?:cm|mm|m))?$", re.I)
LEVEL_MARK_RE = re.compile(r"^(?:kot|elev\.?|el\.?|level)?\s*[+\-±−]\s*\d+(?:[.,]\d+)?$", re.I)
SIZE_TAG_RE = re.compile(r"^\d+(?:[.,]\d+)?\s*[/xX*]\s*\d+(?:[.,]\d+)?$")
ELEVATION_TOL_M = 0.05
REFINE = True
REFINE_RADIUS_M = 2.0
REFINE_MIN_M = 0.01
ZERO_HEIGHT_PLACEHOLDER = 1.0
TYPE_ORDER = ("rooms", "doors", "windows", "walls", "stairs", "openings")


# --- text and layer rules (pure) ------------------------------------------------------------------------------------

def is_dimension_text(text: str, layer: str = "") -> bool:
    """True when a text is a dimension, a bare number, a level mark, or sits on a dimension layer; a size tag such
    as ``90/210`` is never one (it names a door or window)."""
    t = " ".join((text or "").replace("\\P", " ").split())
    if SIZE_TAG_RE.match(t):
        return False
    if NUMBER_RE.match(t) or LEVEL_MARK_RE.match(t):
        return True
    up = (layer or "").upper()
    return any(w in up for w in DIM_LAYER_WORDS)


def layer_map(names: list[str]) -> dict:
    """``{old: new}`` with ``L1, L2 ...`` in the order given (distinct, stable); the layers of ``LAYERS_KEEP`` stay."""
    out, n = {}, 0
    for name in names:
        if name.lower() in LAYERS_KEEP:
            out[name] = name
        else:
            n += 1
            out[name] = f"L{n}"
    return out


# --- DXF transforms -------------------------------------------------------------------------------------------------

def _matrix(kind: str, centre) -> object:
    from ezdxf.math import Matrix44

    cx, cy = float(centre[0]), float(centre[1])
    to0, back = Matrix44.translate(-cx, -cy, 0), Matrix44.translate(cx, cy, 0)
    core = Matrix44.scale(-1, 1, 1) if kind == "mirror" else Matrix44.z_rotate(math.pi / 2)
    return Matrix44.chain(to0, core, back)


def centre_of(doc) -> tuple:
    """The centre of the modelspace extents (the point the mirror and the rotation use)."""
    try:
        from ezdxf import bbox
        box = bbox.extents(doc.modelspace(), fast=True)
        if box.has_data:
            return (float(box.center.x), float(box.center.y))
    except Exception:
        pass
    return (0.0, 0.0)


def transform_modelspace(doc, m) -> dict:
    """Apply a Matrix44 to every modelspace entity (blocks follow through their INSERTs); the failures are counted."""
    done, failed = 0, []
    zero = []                                  # MTEXT with height 0 (also inside dimension blocks): ezdxf divides by it
    for layout in (doc.modelspace(), *doc.blocks):
        for e in layout:
            if e.dxftype() == "MTEXT" and float(e.dxf.get("char_height", 1.0) or 0.0) <= 0.0:
                zero.append(e)
                e.dxf.char_height = ZERO_HEIGHT_PLACEHOLDER
    for e in list(doc.modelspace()):
        try:
            e.transform(m)
            done += 1
        except Exception as exc:                                    # an entity ezdxf cannot transform this way
            failed.append(f"{e.dxftype()}:{type(exc).__name__}")
    for e in zero:
        e.dxf.char_height = 0.0
    try:                                                            # keep the header extents true
        from ezdxf import bbox
        box = bbox.extents(doc.modelspace(), fast=True)
        if box.has_data:
            doc.header["$EXTMIN"] = tuple(box.extmin)
            doc.header["$EXTMAX"] = tuple(box.extmax)
    except Exception:
        pass
    return {"transformed": done, "failed": failed}


def apply_geometry(doc, kind: str) -> dict:
    """``mirror`` or ``rotate90`` about the extents' centre (in place)."""
    return transform_modelspace(doc, _matrix(kind, centre_of(doc)))


def mm_factor(doc) -> Optional[float]:
    """Drawing units -> millimetres for the header unit (None: already mm, or no unit)."""
    from ezdxf import units as U

    code = int(doc.header.get("$INSUNITS", 0) or 0)
    if code in (0, MM_INSUNITS) or code not in U.METER_FACTOR:
        return None
    return float(U.conversion_factor(code, MM_INSUNITS))


def apply_mm(doc) -> dict:
    """Scale to millimetres and set ``$INSUNITS`` to 4; ``{"skipped": reason}`` when the drawing is mm or unitless."""
    from ezdxf import units as U
    from ezdxf.math import Matrix44

    f = mm_factor(doc)
    code = int(doc.header.get("$INSUNITS", 0) or 0)
    if f is None:
        return {"skipped": "already mm" if code == MM_INSUNITS else f"no usable header unit ($INSUNITS={code})"}
    res = transform_modelspace(doc, Matrix44.scale(f, f, f))
    doc.header["$INSUNITS"] = MM_INSUNITS
    res.update({"from_unit": str(U.decode(code)), "factor": f})
    return res


def apply_layers(doc) -> dict:
    """Rename every layer to ``L<n>`` in the table, in the layouts and inside the blocks."""
    names = [lay.dxf.name for lay in doc.layers]
    mp = layer_map(names)
    clash = {v for k, v in mp.items() if v != k} & set(names)
    if clash:                                                       # an existing "L1": go through temporary names
        tmp = {k: f"__wen{i}" for i, k in enumerate(names) if mp[k] != k}
        for lay in list(doc.layers):
            if lay.dxf.name in tmp:
                lay.dxf.name = tmp[lay.dxf.name]
        _remap_entities(doc, tmp)
        mp = {tmp.get(k, k): v for k, v in mp.items()}
    for lay in list(doc.layers):
        new = mp.get(lay.dxf.name)
        if new and new != lay.dxf.name:
            lay.dxf.name = new
    _remap_entities(doc, mp)
    try:                                                            # the layer table is keyed by name
        entries = getattr(doc.layers, "entries", None)
        if isinstance(entries, dict):
            for key in list(entries):
                ent = entries[key]
                if ent.dxf.name.lower() != key.lower():
                    entries[ent.dxf.name.lower()] = entries.pop(key)
    except Exception:
        pass
    return {"layers": len(names), "renamed": sum(1 for k, v in mp.items() if k != v)}


def _remap_entities(doc, mp: dict) -> None:
    low = {k.lower(): v for k, v in mp.items()}

    def fix(e):
        cur = e.dxf.get("layer", None)
        if cur is not None and cur.lower() in low:
            e.dxf.layer = low[cur.lower()]
        for att in getattr(e, "attribs", []) or []:
            fix(att)

    for layout in doc.layouts:
        for e in layout:
            fix(e)
    for block in doc.blocks:
        for e in block:
            fix(e)


def text_of(e) -> str:
    try:
        return e.plain_text() if e.dxftype() == "MTEXT" else (e.dxf.get("text", "") or "")
    except Exception:
        return e.dxf.get("text", "") or ""


def apply_nodims(doc) -> dict:
    """Remove the dimension TEXT / MTEXT of the modelspace (``is_dimension_text``); counts what stays."""
    msp = doc.modelspace()
    removed, kept = [], 0
    for e in list(msp):
        if e.dxftype() not in ("TEXT", "MTEXT"):
            continue
        text = text_of(e)
        if is_dimension_text(text, e.dxf.get("layer", "")):
            removed.append(text)
            msp.delete_entity(e)
        else:
            kept += 1
    return {"removed": len(removed), "kept": kept, "examples": removed[:8]}


def apply_variant(doc, variant: str) -> dict:
    """Apply one variant to a DXF document in place; returns the notes (``skipped`` when it does not apply)."""
    if variant in GEOMETRIC:
        return apply_geometry(doc, variant)
    if variant == "mm":
        return apply_mm(doc)
    if variant == "layers":
        return apply_layers(doc)
    if variant == "nodims":
        return apply_nodims(doc)
    if variant == "identity":
        return {}
    raise ValueError(f"unknown variant {variant!r}")


def read_dxf(path: Path):
    import ezdxf
    from ezdxf import recover

    try:
        return ezdxf.readfile(str(path))
    except Exception:
        doc, _aud = recover.readfile(str(path))
        return doc


# --- sources and the variant folder ---------------------------------------------------------------------------------

def dxf_sources(project: str, original_dir: Path, projects_dir: Path = PROJECTS_DIR) -> list[Path]:
    """The DXF files the original reading used: ``<original>/converted/*.dxf`` (DWG projects), else the project's own
    ``.dxf`` files (not the truth or output folders)."""
    conv = sorted((Path(original_dir) / "converted").glob("*.dxf"))
    if conv:
        return conv
    own = []
    for p in sorted((projects_dir / project).rglob("*.dxf")):
        if any(part in ("truth", "outputs") for part in p.relative_to(projects_dir / project).parts):
            continue
        own.append(p)
    return own


def write_variant(project: str, sources: list[Path], variant: str, vdir: Path,
                  projects_dir: Path = PROJECTS_DIR) -> dict:
    """``vdir`` = brief.yaml + the transformed DXFs. Returns the notes (per file); ``skipped`` when none applies."""
    shutil.rmtree(vdir, ignore_errors=True)
    vdir.mkdir(parents=True)
    brief = projects_dir / project / "brief.yaml"
    if brief.is_file():
        shutil.copy(brief, vdir / "brief.yaml")
    notes, skipped = {}, []
    for src in sources:
        doc = read_dxf(src)
        n = apply_variant(doc, variant)
        if n.get("skipped"):
            skipped.append(f"{src.name}: {n['skipped']}")
        notes[src.name] = n
        doc.saveas(str(vdir / src.name))
    out = {"files": notes}
    if skipped and len(skipped) == len(sources):
        out["skipped"] = "; ".join(skipped)
    return out


# --- mapping the variant's reading back to the original frame (pure) -------------------------------------------------

def _level_points(ext: dict, lid: str) -> list:
    lv = (ext.get("per_level") or {}).get(lid) or {}
    pts = []
    for w in lv.get("walls") or []:
        pts += [w["start"], w["end"]]
    if not pts:
        for r in lv.get("rooms") or []:
            pts += list(r.get("polygon") or [])
    return pts


def level_centre(ext: dict, lid: str) -> Optional[tuple]:
    """The bounding-box centre of a level's walls (else its rooms); None when it has neither."""
    pts = _level_points(ext, lid)
    if not pts:
        return None
    xs, ys = [float(p[0]) for p in pts], [float(p[1]) for p in pts]
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)


def forward_point(kind: str, p, c_o, c_v) -> list:
    """An original point seen in the variant's frame (``c_o`` / ``c_v``: the aligned centres)."""
    x, y = float(p[0]) - c_o[0], float(p[1]) - c_o[1]
    if kind == "mirror":
        return [c_v[0] - x, c_v[1] + y]
    if kind == "rotate90":
        return [c_v[0] - y, c_v[1] + x]
    return [c_v[0] + x, c_v[1] + y]


def inverse_point(kind: str, q, c_o, c_v) -> list:
    """A variant point seen in the original's frame (the inverse of ``forward_point``)."""
    x, y = float(q[0]) - c_v[0], float(q[1]) - c_v[1]
    if kind == "mirror":
        return [c_o[0] - x, c_o[1] + y]
    if kind == "rotate90":
        return [c_o[0] + y, c_o[1] - x]
    return [c_o[0] + x, c_o[1] + y]


def map_points(ext_level: dict, fn) -> dict:
    """A copy of one level's element lists with every point moved by ``fn`` (rooms, openings, walls, stairs)."""
    out = copy.deepcopy(ext_level)
    for r in out.get("rooms") or []:
        if r.get("polygon"):
            r["polygon"] = [fn(p) for p in r["polygon"]]
        if r.get("centroid"):
            r["centroid"] = fn(r["centroid"])
    for kind in ("doors", "windows", "openings"):
        for o in out.get(kind) or []:
            if o.get("center"):
                o["center"] = fn(o["center"])
    for w in out.get("walls") or []:
        w["start"], w["end"] = fn(w["start"]), fn(w["end"])
    for s in out.get("stairs") or []:
        if s.get("center"):
            s["center"] = fn(s["center"])
        for fl in s.get("flights") or []:
            fl["start"], fl["end"] = fn(fl["start"]), fn(fl["end"])
    return out


def level_id_map(orig: dict, var: dict) -> dict:
    """``{variant level id: original level id}`` by elevation (then by the same id, then by order); a variant level
    the original has no partner for keeps its own id."""
    o_levels = list(orig.get("levels") or [])
    mp, used = {}, set()
    for lv in var.get("levels") or []:
        best, bd = None, ELEVATION_TOL_M
        for ol in o_levels:
            if ol["id"] in used or lv.get("elevation") is None or ol.get("elevation") is None:
                continue
            d = abs(float(lv["elevation"]) - float(ol["elevation"]))
            if d <= bd:
                best, bd = ol, d
        if best is not None:
            mp[lv["id"]] = best["id"]
            used.add(best["id"])
    for lv in var.get("levels") or []:
        if lv["id"] in mp:
            continue
        for ol in o_levels:
            if ol["id"] not in used and ol["id"] == lv["id"]:
                mp[lv["id"]] = ol["id"]
                used.add(ol["id"])
                break
        else:
            for ol in o_levels:
                if ol["id"] not in used and ol.get("order") is not None and ol.get("order") == lv.get("order"):
                    mp[lv["id"]] = ol["id"]
                    used.add(ol["id"])
                    break
    return mp


def relabel_levels(var: dict, mp: dict) -> dict:
    """The variant extract with its level ids renamed through ``mp``."""
    out = copy.deepcopy(var)
    out["levels"] = [dict(lv, id=mp.get(lv["id"], lv["id"])) for lv in var.get("levels") or []]
    out["per_level"] = {mp.get(k, k): v for k, v in (var.get("per_level") or {}).items()}
    return out


def _wall_mids(level: dict) -> list:
    return [((w["start"][0] + w["end"][0]) / 2, (w["start"][1] + w["end"][1]) / 2) for w in level.get("walls") or []]


def refine_shift(orig_level: dict, mapped_level: dict) -> Optional[tuple]:
    """The median offset (dx, dy) that brings the mapped wall mid-points onto the nearest original ones (within
    ``REFINE_RADIUS_M``); None when fewer than 3 pairs or it is below ``REFINE_MIN_M``."""
    o, v = _wall_mids(orig_level), _wall_mids(mapped_level)
    if len(o) < 3 or len(v) < 3:
        return None
    dxs, dys = [], []
    for q in v:
        near = min(o, key=lambda p: math.hypot(p[0] - q[0], p[1] - q[1]))
        if math.hypot(near[0] - q[0], near[1] - q[1]) <= REFINE_RADIUS_M:
            dxs.append(near[0] - q[0])
            dys.append(near[1] - q[1])
    if len(dxs) < 3:
        return None
    dx, dy = statistics.median(dxs), statistics.median(dys)
    return (dx, dy) if math.hypot(dx, dy) >= REFINE_MIN_M else None


def map_back(orig: dict, var: dict, kind: str, refine: bool = REFINE) -> dict:
    """The variant's extract in the original's frame and with the original's level ids (pure)."""
    var = relabel_levels(var, level_id_map(orig, var))
    out = copy.deepcopy(var)
    for lid, lvl in (var.get("per_level") or {}).items():
        co, cv = level_centre(orig, lid), level_centre(var, lid)
        if co is None or cv is None:
            co, cv = (0.0, 0.0), (0.0, 0.0)
        moved = map_points(lvl, lambda q, co=co, cv=cv: inverse_point(kind, q, co, cv))
        if refine and lid in (orig.get("per_level") or {}):
            sh = refine_shift(orig["per_level"][lid], moved)
            if sh:
                moved = map_points(moved, lambda q, sh=sh: [q[0] + sh[0], q[1] + sh[1]])
        out["per_level"][lid] = moved
    return out


def forward(orig: dict, kind: str, c_v_offset=(3.0, -2.0)) -> dict:
    """The original reading as a variant would show it (the forward transform with a shifted frame): the helper that
    makes ``map_back(forward(x)) == x`` checkable without a second reading."""
    out = copy.deepcopy(orig)
    for lid, lvl in (orig.get("per_level") or {}).items():
        co = level_centre(orig, lid) or (0.0, 0.0)
        cv = (co[0] + c_v_offset[0], co[1] + c_v_offset[1])
        out["per_level"][lid] = map_points(lvl, lambda p, co=co, cv=cv: forward_point(kind, p, co, cv))
    return out


# --- findings (pure) ------------------------------------------------------------------------------------------------

def _matches(kind: str, tt: list, rr: list) -> list:
    if kind == "rooms":
        return SC.match_rooms(tt, rr)
    if kind == "walls":
        return SC.match_walls(tt, rr)
    if kind == "stairs":
        return SC.match_points(tt, rr, SC.STAIR_CENTER_M)
    return SC.match_points(tt, rr, SC.OPENING_CENTER_M)


def place_of(kind: str, el: dict) -> dict:
    """A short, JSON-able place: the label or the id and the position in metres."""
    if kind == "rooms":
        pos = el.get("centroid")
    elif kind == "walls":
        pos = [(el["start"][0] + el["end"][0]) / 2, (el["start"][1] + el["end"][1]) / 2]
    else:
        pos = el.get("center")
    out = {"id": el.get("id"), "at": [round(float(pos[0]), 2), round(float(pos[1]), 2)] if pos else None}
    if el.get("label"):
        out["label"] = el["label"]
    if kind == "walls":
        out["length_m"] = round(SC._dist(el["start"], el["end"]), 2)
    if kind in ("doors", "windows", "openings") and el.get("width"):
        out["width_m"] = el["width"]
    return out


def findings(orig: dict, mapped: dict, variant: str) -> list[dict]:
    """``lost`` (an original element no variant element matches), ``added`` (a variant element no original one
    matches) and ``level_lost`` / ``level_added`` entries."""
    out = []
    o_ids = [lv["id"] for lv in orig.get("levels") or []]
    v_ids = [lv["id"] for lv in mapped.get("levels") or []]
    for lid in o_ids:
        if lid not in v_ids:
            out.append({"change": "level_lost", "kind": "levels", "level": lid, "variant": variant, "place": {}})
    for lid in v_ids:
        if lid not in o_ids:
            out.append({"change": "level_added", "kind": "levels", "level": lid, "variant": variant, "place": {}})
    for lid in o_ids:
        ol = (orig.get("per_level") or {}).get(lid) or {}
        vl = (mapped.get("per_level") or {}).get(lid) or {}
        for kind in TR.ELEMENT_TYPES:
            tt, rr = ol.get(kind) or [], vl.get(kind) or []
            pairs = _matches(kind, tt, rr)
            mi, mj = {i for i, _ in pairs}, {j for _, j in pairs}
            for i, el in enumerate(tt):
                if i not in mi:
                    out.append({"change": "lost", "kind": kind, "level": lid, "variant": variant,
                                "place": place_of(kind, el)})
            for j, el in enumerate(rr):
                if j not in mj:
                    out.append({"change": "added", "kind": kind, "level": lid, "variant": variant,
                                "place": place_of(kind, el)})
    return out


def group_fragile(all_findings: list[dict]) -> dict:
    """``{level: [finding, ...]}``; a place that several variants lose is listed once with all their names."""
    per: dict = {}
    seen: dict = {}
    for f in all_findings:
        key = (f["level"], f["change"], f["kind"], json.dumps(f["place"].get("at")), f["place"].get("label"))
        if key in seen:
            seen[key]["variants"].append(f["variant"])
            continue
        entry = {"change": f["change"], "kind": f["kind"], "place": f["place"], "variants": [f["variant"]]}
        seen[key] = entry
        per.setdefault(f["level"], []).append(entry)
    return per


# --- the reader's unit ------------------------------------------------------------------------------------------------

def reader_unit(building: dict) -> dict:
    """What the reader decided as the unit of the drawing: the metres per unit of the floor-plan pages with the method
    that gave it (``dxf_insunits`` means the header was trusted), and the building's unit system."""
    seen = []
    for d in building.get("documents") or []:
        for pg in d.get("pages") or []:
            sc = pg.get("scale") or {}
            if pg.get("class") == "floor_plan" and sc.get("metres_per_unit"):
                seen.append((float(sc["metres_per_unit"]), sc.get("method")))
    return {"metres_per_unit": sorted({m for m, _ in seen}), "methods": sorted({str(m) for _, m in seen}),
            "unit_system": (building.get("project") or {}).get("unit_system")}


# --- running --------------------------------------------------------------------------------------------------------

def row_of(score: dict) -> dict:
    def g(k):
        return round(100 * score[k]["f1"], 1)
    return {"total": score["total"], "levels_read": score["levels"]["read"], "levels_truth": score["levels"]["truth"],
            "rooms": g("rooms"), "doors": g("doors"), "windows": g("windows"), "walls": g("walls")}


def original_reading(project: str, work: Path, fresh: bool = False) -> Path:
    """``work/<project>`` (reused when ``building.json`` is there), else read now."""
    out = Path(work) / project
    if (out / "building.json").is_file() and not fresh:
        return out
    from wenart.reading_check import regress as RG
    return RG.read_project(project, work)


def stability_project(project: str, work: Path, variants=VARIANTS, fresh: bool = False,
                      projects_dir: Path = PROJECTS_DIR) -> dict:
    """The stability result of one project (the module docstring)."""
    work = Path(work)
    res: dict = {"project": project, "variants": {}, "skipped": None}
    orig_dir = original_reading(project, work, fresh)
    sources = dxf_sources(project, orig_dir, projects_dir)
    if not sources:
        res["skipped"] = "no DXF or DWG document (PDF or raster only): the variants are DXF transforms"
        return res
    from wenart.ingest import pipeline as PL

    ob = json.loads((orig_dir / "building.json").read_text(encoding="utf-8"))
    orig = TR.extract(ob, project=project)
    res["original"] = {"counts": TR.counts(orig), "unit": reader_unit(ob), "files": [s.name for s in sources]}
    all_f = []
    for v in variants:
        vdir = work / "variants" / f"{project}__{v}"
        vout = work / "variants" / f"{project}__{v}__out"
        notes = write_variant(project, sources, v, vdir, projects_dir)
        entry = {"notes": notes}
        if notes.get("skipped"):
            entry["skipped"] = notes["skipped"]
            res["variants"][v] = entry
            continue
        shutil.rmtree(vout, ignore_errors=True)
        vout.mkdir(parents=True)
        try:
            PL.run_project(vdir, vout, no_ai=True)
            vb = json.loads((vout / "building.json").read_text(encoding="utf-8"))
        except Exception as exc:
            entry["error"] = f"{type(exc).__name__}: {exc}"
            res["variants"][v] = entry
            continue
        var = TR.extract(vb, project=project)
        mapped = map_back(orig, var, v) if v in GEOMETRIC else relabel_levels(var, level_id_map(orig, var))
        score = SC.match(orig, mapped)
        fnd = findings(orig, mapped, v)
        all_f += fnd
        entry.update({"score": score, "row": row_of(score), "unit": reader_unit(vb), "counts": TR.counts(var),
                      "findings": len(fnd),
                      "finding_counts": {c: sum(1 for f in fnd if f["change"] == c)
                                         for c in ("lost", "added", "level_lost", "level_added")}})
        res["variants"][v] = entry
    res["fragile"] = group_fragile(all_f)
    return res


def table(results: list[dict]) -> str:
    head = ("project", "variant", "total", "levels", "rooms", "doors", "windows", "walls", "lost", "added",
            "unit (m/unit)")
    rows = [head]
    for r in results:
        if r.get("skipped"):
            rows.append((r["project"], "-", "skipped: " + r["skipped"], "", "", "", "", "", "", "", ""))
            continue
        for v, e in r["variants"].items():
            if e.get("skipped") or e.get("error"):
                rows.append((r["project"], v, "skipped: " + (e.get("skipped") or e["error"]), "", "", "", "", "",
                             "", "", ""))
                continue
            x, fc = e["row"], e["finding_counts"]
            unit = ",".join(f"{m:g}" for m in e["unit"]["metres_per_unit"]) or "?"
            rows.append((r["project"], v, f"{x['total']:.1f}", f"{x['levels_read']}/{x['levels_truth']}",
                         f"{x['rooms']:.0f}", f"{x['doors']:.0f}", f"{x['windows']:.0f}", f"{x['walls']:.0f}",
                         str(fc["lost"] + fc["level_lost"]), str(fc["added"] + fc["level_added"]), unit))
    w = [max(len(str(row[i])) for row in rows) for i in range(len(head))]
    lines = ["  ".join(str(c).ljust(w[i]) for i, c in enumerate(row)) for row in rows]
    lines.insert(1, "  ".join("-" * x for x in w))
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check.stability", description=__doc__.split("\n")[0])
    ap.add_argument("--projects", required=True, help="comma-separated project names")
    ap.add_argument("--variants", default=",".join(VARIANTS), help=f"from {', '.join(ALL_VARIANTS)}")
    ap.add_argument("--work", default=None, help="work directory (default: a temporary one)")
    ap.add_argument("--json", default=None, help="write all results to this file")
    ap.add_argument("--fresh", action="store_true", help="read the original again even when work has it")
    args = ap.parse_args(argv)
    variants = [v.strip() for v in args.variants.split(",") if v.strip()]
    bad = [v for v in variants if v not in ALL_VARIANTS]
    if bad:
        print(f"unknown variants: {bad}")
        return 2
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_stability_"))
    results = []
    for p in [x.strip() for x in args.projects.split(",") if x.strip()]:
        r = stability_project(p, work, variants, fresh=args.fresh)
        results.append(r)
        out = work / "stability" / f"{p}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{p}: done -> {out}", file=sys.stderr)
    print(table(results))
    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
