"""The source inventory: every item of the documents the reading saw, as ``<out>/source_items.json`` (26 Oct 2026).

What: the pipeline writes a compact inventory of the source documents beside ``building.json``; the source ledger
(``wenart.audit.ledger``, line 1 of the auditor) checks that every meaningful item is accounted for: an element of
the model uses it (its ``evidence[].entity``), or a logged reason says why not.

Why (the user, 26 Oct 2026): "the audit is very weak, only the looks being judged, everything needs to be judged".
real06's DWG has the texts ``VERANDA`` / ``22,80m²`` (TEXT:29585C / TEXT:29585D, layer ``YAZıMAHAL``); the reading
recorded them as a site area without an outline, nothing later looked at it, and the veranda vanished silently.
Nothing checked the model against the full list of what the documents hold. This module makes that list; it changes
nothing the reading builds.

How:
- ``page_summary(page)`` is called by the pipeline (``_extract_generic``) on every generic page model before the page
  is dropped, in page units, with the ids the reading uses for its evidence: the layers with their entity counts and
  ids (a stroke inside a block keeps its block path, ``INSERT:4B/3``; a polyline piece and a hatch path are their
  entity, ``LWPOLYLINE:2F``, ``HATCH:5C``), every block instance at every depth (``INSERT:4B``, ``INSERT:4B/3`` for a
  CHAIR nested in DINING-6: name, layer, box, depth), the hatches and the closed outlines with the instance that
  holds them.
- ``inventory(build, records, works)`` at the end of the run: every page record (read or not, with its skip reason
  and, on a multi-region sheet, its region's class, use and counts from ``sheets.json``); every text of every read
  page (``LevelExtraction.texts``: value, layer, block chain, attribute tag, position in building metres, the reading's
  role and the label block it belongs to, with the part: name, size or area); the texts the classifier read of a
  page that was not extracted; the block instances grouped by name: the top-level ones, except that a block larger
  than ``CONTAINER_M`` (a whole plan or sheet drawn as one block, real03) is a *container* whose child instances are
  listed instead (containers are listed apart); the layers per page (and the entity boxes of small layers, for the
  ledger's outline hints); the hatches and closed outlines of at least ``MIN_REGION_M2`` that belong to no listed
  block (building-metre polygons, simplified).
- ``write(build, records, works, out_dir)`` writes the JSON (``SCHEMA``); ``load(path)`` reads it back.

Format (``SCHEMA`` ``wenart.source_items/1``)::

    {"schema", "project", "pages": [{"id": "p1", "file", "page", "format", "kind", "class", "region_id",
       "region_class", "region_use", "region_features", "level_id", "read", "skip_reason", "units_to_m",
       "transform_to_building", "units"}],
     "texts": [{"id": "TEXT:29585C", "page": "p1", "text", "layer", "block", "tag", "pos": [x, y], "height_m",
       "rotation_deg", "role", "label", "label_part", "label_id"}],
     "blocks": [{"name", "count", "inserts": [{"id": "INSERT:4B", "page", "layer", "pos", "size", "depth",
       "nested", "strokes"}]}],
     "containers": [{"id", "name", "page", "size", "children"}],
     "layers": [{"name", "page", "entities", "types": {"LINE": n}, "ids": [...], "ids_truncated", "boxes"}],
     "hatches": [{"id": "HATCH:5C", "page", "layer", "block", "filled", "paths", "area_m2", "pos", "polygon"}],
     "outlines": [{"id": "LWPOLYLINE:2F", "page", "layer", "block", "area_m2", "pos", "polygon"}],
     "counts": {"pages", "pages_read", "texts", "blocks", "inserts", "containers", "layers", "hatches", "outlines"}}

Positions and polygons are building metres (the page's ``transform_to_building``); a page without one (no scale)
keeps page units, lists no blocks, hatches or outlines, and says so (``units: "page"``).
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Optional

SCHEMA = "wenart.source_items/1"
FILE_NAME = "source_items.json"
MIN_REGION_M2 = 1.0           # hatches and closed outlines smaller than this are counted, not listed
CONTAINER_M = 10.0            # a block instance larger than this (either side) holding other blocks is a container
MAX_LAYER_IDS = 20000         # entity ids listed per layer and page (beyond: ``ids_truncated``)
LAYER_BOX_MAX = 300           # layers with at most this many entities list each entity's box
MAX_POLYGON_POINTS = 64       # polygons are simplified to at most this many points
ROUND = 3


def entity_id(stroke_id: str) -> str:
    """The evidence entity of a stroke: the hatch path (``#k``) and the polyline piece (``:k``) dropped, the block path
    kept (``INSERT:4B/3``, ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``)."""
    base = stroke_id.split("#")[0]
    parts = base.split("/")
    last = parts[-1]
    if last.count(":") >= 2:
        parts[-1] = ":".join(last.split(":")[:2])
    return "/".join(parts)


def _shoelace(pts) -> float:
    n = len(pts)
    if n < 3:
        return 0.0
    s = 0.0
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


def _bbox(pts) -> list[float]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def _union_box(a: Optional[list], b: list) -> list:
    if a is None:
        return list(b)
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def _instances(stroke_id: str, chain: Optional[str]) -> list[tuple[str, str]]:
    """(instance path, block name) of every block a stroke lies in, outermost first: ``INSERT:4B/3/0`` with the chain
    ``DINING-6/CHAIR`` -> [(``INSERT:4B``, DINING-6), (``INSERT:4B/3``, CHAIR)]."""
    if not chain or not stroke_id.startswith("INSERT:"):
        return []
    parts = stroke_id.split("#")[0].split("/")
    names = chain.split("/")
    out = []
    for k, name in enumerate(names):
        if len(parts) < k + 2:
            break
        out.append(("/".join(parts[:k + 1]), name))
    return out


def page_summary(page) -> dict:
    """The strokes of one ``GenericPage`` as a compact summary in page units (taken before the pipeline drops the
    page model): layers with their entity ids, block instances at every depth, hatches and closed outlines."""
    layers: dict[str, dict] = {}
    inserts: dict[str, dict] = {}
    hatches: dict[str, dict] = {}
    outlines: list[dict] = []
    for st in page.strokes or []:
        if not st.pts:
            continue
        eid = entity_id(st.id)
        head = eid.split("/")[0]
        kind = head.split(":", 1)[0] if ":" in head else "?"
        if "/" in eid:
            kind = "HATCH" if "#" in st.id else st.kind.upper()
        layer = st.layer or "-"
        box = _bbox(st.pts)
        entry = layers.setdefault(layer, {"ids": {}, "types": Counter()})
        if eid not in entry["ids"]:
            entry["ids"][eid] = list(box)
            entry["types"][kind] += 1
        else:
            entry["ids"][eid] = _union_box(entry["ids"][eid], box)
        chain = _instances(st.id, st.block)
        for depth, (path, name) in enumerate(chain):
            ins = inserts.setdefault(path, {"name": name, "layers": Counter(), "box": None, "nested": set(),
                                            "strokes": 0, "depth": depth,
                                            "parent": chain[depth - 1][0] if depth else None})
            ins["nested"].update(n for _, n in chain[depth + 1:])
            ins["layers"][layer] += 1
            ins["box"] = _union_box(ins["box"], box)
            ins["strokes"] += 1
        owner = chain[-1][0] if chain else None
        if "#" in st.id or head.startswith("HATCH:"):
            h = hatches.setdefault(eid, {"layer": layer, "block": st.block, "owner": owner, "filled": False,
                                         "paths": []})
            h["filled"] = h["filled"] or st.fill is not None
            h["paths"].append([tuple(p) for p in st.pts])
            continue
        if st.closed and len(st.pts) >= 3:
            outlines.append({"id": eid, "layer": layer, "block": st.block, "owner": owner,
                             "pts": [tuple(p) for p in st.pts]})
    out_layers = []
    for name, entry in sorted(layers.items()):
        ids = list(entry["ids"])
        row = {"name": name, "entities": len(ids), "types": dict(sorted(entry["types"].items())),
               "ids": ids[:MAX_LAYER_IDS], "ids_truncated": len(ids) > MAX_LAYER_IDS}
        if len(ids) <= LAYER_BOX_MAX:
            row["boxes"] = [entry["ids"][i] for i in ids]
        out_layers.append(row)
    out_inserts = []
    for path, ins in inserts.items():
        out_inserts.append({"id": path, "name": ins["name"] or "?",
                            "layer": ins["layers"].most_common(1)[0][0] if ins["layers"] else None,
                            "box": ins["box"], "nested": sorted(ins["nested"]), "strokes": ins["strokes"],
                            "depth": ins["depth"], "parent": ins["parent"]})
    out_hatches = []
    for eid, h in hatches.items():
        main = max(h["paths"], key=_shoelace)
        out_hatches.append({"id": eid, "layer": h["layer"], "block": h["block"], "owner": h["owner"],
                            "filled": h["filled"], "paths": len(h["paths"]), "area": _shoelace(main), "pts": main})
    return {"layers": out_layers, "inserts": out_inserts, "hatches": out_hatches,
            "outlines": [dict(o, area=_shoelace(o["pts"])) for o in outlines]}


# --------------------------------------------------------------------------
# The inventory
# --------------------------------------------------------------------------

def _affine(m6, p) -> tuple[float, float]:
    a, b, c, d, e, f = (float(v) for v in m6)
    return (a * p[0] + b * p[1] + c, d * p[0] + e * p[1] + f)


def _pt(m6, p) -> list[float]:
    q = _affine(m6, p) if m6 else (float(p[0]), float(p[1]))
    return [round(q[0], ROUND), round(q[1], ROUND)]


def _box_m(m6, box) -> list[float]:
    lo, hi = _pt(m6, (box[0], box[1])), _pt(m6, (box[2], box[3]))
    return [min(lo[0], hi[0]), min(lo[1], hi[1]), max(lo[0], hi[0]), max(lo[1], hi[1])]


def _simplify(pts: list, tol: float) -> list:
    """At most ``MAX_POLYGON_POINTS`` points (shapely's simplify, growing the tolerance until it fits)."""
    if len(pts) <= MAX_POLYGON_POINTS:
        return pts
    try:
        from shapely.geometry import Polygon

        poly = Polygon(pts)
        t = tol
        for _ in range(12):
            simple = poly.simplify(t, preserve_topology=False)
            coords = list(getattr(simple, "exterior", simple).coords)[:-1] if not simple.is_empty else []
            if 3 <= len(coords) <= MAX_POLYGON_POINTS:
                return [tuple(c) for c in coords]
            t *= 2.0
    except Exception:                        # noqa: BLE001 - a degenerate ring: keep every n-th point
        pass
    step = math.ceil(len(pts) / MAX_POLYGON_POINTS)
    return pts[::step]


def _units_scale(m6) -> float:
    return math.hypot(float(m6[0]), float(m6[3])) if m6 else 1.0


def _region_info(build, record) -> tuple[Optional[str], Optional[dict]]:
    sheets = getattr(build, "sheets", None) or {}
    for r in sheets.get("regions") or []:
        if r.get("id") == record.region_id and r.get("file") == record.file:
            feats = r.get("features") or {}
            keep = {k: feats[k] for k in ("texts", "room_labels", "area_labels", "level_marks", "door_swings")
                    if k in feats}
            return r.get("use"), keep
    return None, None


def _label_parts(ex) -> dict[str, tuple[str, str, str]]:
    """Text id -> (label name, part, label id) for every run of the page's label blocks (part: name, size or area;
    label id: the id of the block's first name run)."""
    out: dict[str, tuple[str, str, str]] = {}
    for item in getattr(ex, "labels", None) or []:
        block = getattr(item, "block", None)
        if block is None:
            if item.entity:
                out.setdefault(item.entity, (item.text, "name", item.entity))
            continue
        name_runs = list(getattr(block, "name_runs", []) or [])
        name_ids = {r.id for r in name_runs}
        label_id = name_runs[0].id if name_runs else item.entity
        size_text = (getattr(block, "size_text", None) or "").strip()
        for run in getattr(block, "runs", []) or name_runs:
            if run.id in name_ids:
                part = "name"
            elif size_text and run.text.strip() == size_text:
                part = "size"
            else:
                part = "area"
            out.setdefault(run.id, (block.name, part, label_id))
    return out


def text_rows(ex, page_id: str, m6) -> list[dict]:
    """The text rows of one extracted page (the inventory's ``texts`` format: position in building metres through
    ``m6``, the reading's role and label part). 26 Oct 2026: the reading's furniture name texts are read from the same
    rows (``generic.reading.furniture_texts``), so their ids and positions are the inventory's."""
    parts = _label_parts(ex)
    s = _units_scale(m6) if m6 else None
    rows = []
    seen = set()
    for t in getattr(ex, "texts", None) or []:
        text = str(t.text or "").strip()
        if not text or t.entity in seen:
            continue
        seen.add(t.entity)
        ev = t.evidence or {}
        box = t.box or [t.start[0], t.start[1], t.start[0], t.start[1]]
        centre = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
        label = parts.get(t.entity)
        row = {"id": t.entity, "page": page_id, "text": text, "layer": ev.get("layer"), "block": ev.get("block"),
               "tag": ev.get("attrib_tag"), "pos": _pt(m6, centre),
               "height_m": round(float(t.height or 0.0) * s, 3) if s else None,
               "rotation_deg": round(float(t.rotation_deg or 0.0), 1), "role": t.role,
               "label": label[0] if label else None, "label_part": label[1] if label else None,
               "label_id": label[2] if label else None}
        if ev.get("method") not in (None, "vector"):
            row["method"] = ev.get("method")
        rows.append(row)
    return rows


def _listed_instances(inserts: list[dict], m6) -> tuple[list[dict], list[dict]]:
    """(listed instances, containers): from the top level down, an instance larger than ``CONTAINER_M`` with child
    instances is a container and its children are looked at instead."""
    children: dict[Optional[str], list[dict]] = {}
    for ins in inserts:
        children.setdefault(ins.get("parent"), []).append(ins)
    listed, containers = [], []
    todo = list(children.get(None, []))
    while todo:
        ins = todo.pop(0)
        bx = _box_m(m6, ins["box"])
        size = [round(bx[2] - bx[0], ROUND), round(bx[3] - bx[1], ROUND)]
        kids = children.get(ins["id"], [])
        if max(size) > CONTAINER_M and kids:
            containers.append({"id": ins["id"], "name": ins["name"], "size": size, "children": len(kids)})
            todo.extend(kids)
            continue
        listed.append(dict(ins, pos=[round((bx[0] + bx[2]) / 2.0, ROUND), round((bx[1] + bx[3]) / 2.0, ROUND)],
                           size=size))
    return listed, containers


def _region_rows(items: list[dict], page_id: str, m6, key: str, in_block) -> list[dict]:
    if not m6:
        return []                            # no scale: the areas mean nothing, the page is listed as not read
    s = _units_scale(m6)
    rows = []
    for item in items:
        if in_block(item.get("owner")):
            continue                         # a hatch or outline of a listed block (a rug, a basin) is that block
        area = float(item.get("area") or 0.0) * s * s
        if area < MIN_REGION_M2:
            continue
        pts = [tuple(_pt(m6, p)) for p in item["pts"]]
        bx = _bbox(pts)
        row = {"id": item["id"], "page": page_id, "layer": item.get("layer"), "block": item.get("block"),
               "area_m2": round(area, 2),
               "pos": [round((bx[0] + bx[2]) / 2.0, ROUND), round((bx[1] + bx[3]) / 2.0, ROUND)],
               "polygon": [[round(x, ROUND), round(y, ROUND)] for x, y in _simplify(pts, 0.02)]}
        if key == "hatches":
            row.update({"filled": item.get("filled"), "paths": item.get("paths")})
        rows.append(row)
    return rows


def inventory(build, records: list, works: dict) -> dict:
    """The inventory of every page record (``records``) and the read pages (``works``: page key -> ``PageWork``);
    ``build.source_pages`` holds the stroke summaries ``page_summary`` took."""
    summaries = getattr(build, "source_pages", None) or {}
    pages, texts, layers, hatches, outlines, containers = [], [], [], [], [], []
    blocks: dict[str, dict] = {}
    seen_keys = set()
    for record in records:
        key = record.key
        if key in seen_keys:
            continue
        seen_keys.add(key)
        page_id = f"p{len(pages) + 1}"
        work = works.get(key)
        ex = work.extraction if work is not None else None
        m6 = list(ex.transform_to_building) if ex is not None and ex.transform_to_building else None
        use, feats = _region_info(build, record) if record.region_id is not None else (None, None)
        units = None
        if ex is not None and ex.report and ex.report.get("units_to_m"):
            units = float(ex.report["units_to_m"])
        elif m6:
            units = _units_scale(m6)
        pages.append({"id": page_id, "file": record.file, "page": record.page, "format": record.format,
                      "kind": record.kind, "class": record.page_class, "region_id": record.region_id,
                      "region_class": record.region_class, "region_use": use, "region_features": feats,
                      "level_id": record.level_id, "read": work is not None, "skip_reason": record.skip_reason,
                      "units_to_m": units, "transform_to_building": m6, "units": "m" if m6 else "page"})
        if ex is not None:
            texts.extend(text_rows(ex, page_id, m6))
        else:
            # A page the pipeline did not extract: the texts its classifier read (DXF TEXT / MTEXT, PDF words).
            for t in record.texts or []:
                text = str(getattr(t, "text", "") or "").strip()
                if not text:
                    continue
                texts.append({"id": t.entity, "page": page_id, "text": text, "layer": None, "block": None,
                              "tag": None, "pos": [round(float(t.start[0]), ROUND), round(float(t.start[1]), ROUND)],
                              "height_m": None, "rotation_deg": round(float(t.rotation_deg or 0.0), 1),
                              "role": t.role, "label": None, "label_part": None, "label_id": None})
        summary = summaries.get(key)
        if not summary or "error" in summary:
            if summary and "error" in summary:
                pages[-1]["summary_error"] = summary["error"]
            continue
        for lay in summary["layers"]:
            row = dict(lay, page=page_id)
            if "boxes" in row:
                row["boxes"] = [_box_m(m6, b) for b in row["boxes"]] if m6 else None
            layers.append(row)
        if not m6:
            pages[-1]["note"] = "no scale: positions in page units, no blocks, hatches or outlines"
            continue
        listed, conts = _listed_instances(summary["inserts"], m6)
        listed_ids = {i["id"] for i in listed}

        def in_block(owner: Optional[str]) -> bool:
            p = owner
            while p:
                if p in listed_ids:
                    return True
                p = p.rsplit("/", 1)[0] if "/" in p else None
            return False

        for c in conts:
            containers.append(dict(c, page=page_id))
        for ins in listed:
            row = {"id": ins["id"], "page": page_id, "layer": ins["layer"], "pos": ins["pos"], "size": ins["size"],
                   "depth": ins["depth"], "nested": ins["nested"], "strokes": ins["strokes"]}
            b = blocks.setdefault(ins["name"], {"name": ins["name"], "count": 0, "inserts": []})
            b["count"] += 1
            b["inserts"].append(row)
        hatches.extend(_region_rows(summary["hatches"], page_id, m6, "hatches", in_block))
        outlines.extend(_region_rows(summary["outlines"], page_id, m6, "outlines", in_block))
    block_rows = sorted(blocks.values(), key=lambda b: (-b["count"], b["name"]))
    project = (getattr(build, "building", None) or {}).get("project") or {}
    return {"schema": SCHEMA, "project": project.get("id"), "pages": pages, "texts": texts, "blocks": block_rows,
            "containers": containers, "layers": layers, "hatches": hatches, "outlines": outlines,
            "counts": {"pages": len(pages), "pages_read": sum(1 for p in pages if p["read"]), "texts": len(texts),
                       "blocks": len(block_rows), "inserts": sum(b["count"] for b in block_rows),
                       "containers": len(containers), "layers": len({lay["name"] for lay in layers}),
                       "hatches": len(hatches), "outlines": len(outlines)}}


def write(build, records: list, works: dict, out_dir) -> Path:
    """``<out_dir>/source_items.json``."""
    path = Path(out_dir) / FILE_NAME
    data = inventory(build, records, works)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def load(path) -> dict:
    """The inventory a run wrote (a folder or the file itself)."""
    p = Path(path)
    if p.is_dir():
        p = p / FILE_NAME
    return json.loads(p.read_text(encoding="utf-8"))


