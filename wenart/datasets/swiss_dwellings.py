"""Swiss Dwellings floors -> Turkish-style DXF test projects with their exact reading truth (21 Nov 2026, user OK).

What: ``convert_building(rows_by_floor, out_dir, name, profile)`` takes the rows of one building's floors from the
Swiss Dwellings ``geometries.csv`` (Zenodo record 7070952, CC BY 4.0: apartment_id, area_id, building_id,
entity_subtype, entity_type, floor_id, geometry as WKT, site_id, unit_id) and writes ``plan.dxf``, ``brief.yaml``,
``truth/reading_truth.json`` and ``ATTRIBUTION.md`` into ``out_dir/name``. The DXF draws, with a style sampled from the
Turkish profile (``wenart.datasets.style``): walls as double lines (the outline of the wall union with the opening gaps
cut) with a hatch, columns on the column layer, doors as a leaf and a 90 degree swing arc with a size tag, windows as
frame and glass lines with a size tag, Turkish room labels with area texts, stairs with their treads, sanitary and
kitchen pieces, exterior dimension chains, an optional axis grid, and per floor a title, a scale note and a level mark;
the floors of a building side by side on one sheet.

Why: a large test bench of real room layouts with exact answers for the reader (later training data). The truth is
computed from the same regularised layout that is drawn, so it is exact for the drawing, whatever the source's own
errors.

How (building metres):
- one rotation per building puts its dominant wall direction on the axes (walls within 2 degrees are snapped);
- every wall polygon becomes its minimum rotated rectangle (99.8 % of them are rectangles), rounded to 5 mm;
  collinear rectangles of one thickness that touch, or whose gap another wall or a column fills, are one wall (the
  reader's walls run on through junctions); railings become 1 m parapet walls (truth ``parapet: true``);
- rooms are the holes of the union of walls, parapets and columns (walls run on through openings), closed by 1.5 cm,
  at least ``ROOM_MIN_M2``; a room's label comes from the dataset areas inside it (the largest; a living and a kitchen
  area in one room give ``SALON + MUTFAK``), its type from ``building.room_type_for`` of that label;
- each door and window sits on the wall it overlaps most, centred where its polygon's centre projects, its width
  snapped to 5 cm; overlapping openings on one wall keep the first;
- the frame: x right, y up, origin at the min corner of the first floor's walls (the reader's reference frame);
  the truth's ``levels`` are L0.. in floor order (Swiss floor ids ascending), elevation = order x storey height.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from shapely import affinity, wkt
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import polylabel, unary_union

from wenart import building as B
from wenart.datasets import style as ST
from wenart.synthetic import failure_classes as FC

DATASET = {"id": "swiss_dwellings", "name": "Swiss Dwellings", "version": "3.0.0",
           "url": "https://zenodo.org/records/7070952", "licence": "CC BY 4.0",
           "licence_url": "https://creativecommons.org/licenses/by/4.0/", "licence_declared_by": "publisher",
           "licence_flag": "none", "commercial_safe": "yes",
           "attribution": "Swiss Dwellings: An extensive dataset of building geometries (Archilyse AG, 2022), "
                          "CC BY 4.0; floors redrawn as Turkish-style DXF plans by WenArt (geometry regularised, "
                          "labels translated, drafting conventions added)."}
ROUND_M = 0.005
SNAP_DEG = 2.0
ROOM_MIN_M2 = 0.5
CLOSE_M = 0.015
PARAPET_H = 1.0
MERGE_GAP_M = 0.02
MAX_FILL_GAP_M = 0.6
PLAN_SPACING_M = 14.0
LIVING = {"LIVING_ROOM", "LIVING_DINING", "STUDIO"}
TYPE_OF = {"LIVING_ROOM": "living", "LIVING_DINING": "living", "STUDIO": "living", "ROOM": "bedroom",
           "BEDROOM": "bedroom", "KITCHEN": "kitchen", "KITCHEN_DINING": "kitchen", "DINING": "dining",
           "BATHROOM": "bathroom", "CORRIDOR": "hall", "STOREROOM": "storage", "BALCONY": "balcony",
           "LOGGIA": "balcony", "TERRACE": "balcony", "PATIO": "balcony", "SHAFT": "shaft", "ELEVATOR": "shaft",
           "STAIRCASE": "stair", "VOID": "shaft", "LIGHTWELL": "shaft", "OUTDOOR_VOID": "shaft",
           "TECHNICAL_AREA": "technical", "WINTERGARTEN": "other", "GARDEN": "other"}
CIRCULATION = {"hall", "stair", "balcony"}
SANITARY = {"TOILET", "BATHTUB", "SHOWER", "SINK", "WASHING_MACHINE"}
FURNITURE = {"KITCHEN", "BUILT_IN_FURNITURE"}


def r5(v: float) -> float:
    return round(round(float(v) / ROUND_M) * ROUND_M, 4)


# --- the layout of one floor ------------------------------------------------------------------------------------------

@dataclass
class Floor:
    floor_id: str
    walls: list            # FC.Wall (runs), parapets carry truth {"parapet": True, ...}
    columns: list          # Polygons
    openings: list         # FC.Opening on walls
    areas: list            # (subtype, Polygon, unit_id)
    features: list         # (subtype, Polygon)
    union: object = None   # walls + parapets + columns, closed
    faces: list = field(default_factory=list)       # (Polygon, label, room_type, label_point)


def _rect(poly: Polygon) -> Optional[tuple]:
    """(cx, cy, ux, uy, length, thickness) of a polygon's minimum rotated rectangle, snapped near the axes."""
    m = poly.minimum_rotated_rectangle
    if m.geom_type != "Polygon":
        return None
    c = list(m.exterior.coords)
    e0 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e1 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    l0, l1 = math.hypot(*e0), math.hypot(*e1)
    (ux, uy), L, t = ((e0[0] / l0, e0[1] / l0), l0, l1) if l0 >= l1 else ((e1[0] / l1, e1[1] / l1), l1, l0)
    if L < 1e-6:
        return None
    ang = math.degrees(math.atan2(uy, ux)) % 180.0
    for axis in (0.0, 90.0, 180.0):
        if abs(ang - axis) <= SNAP_DEG:
            ang = axis % 180.0
            ux, uy = (1.0, 0.0) if ang == 0.0 else (0.0, 1.0)
    if ux < -1e-9 or (abs(ux) < 1e-9 and uy < 0):
        ux, uy = -ux, -uy
    ctr = m.centroid
    return (r5(ctr.x), r5(ctr.y), ux, uy, r5(L), max(0.04, r5(t)))


def _merge_runs(rects: list, cover) -> list:
    """Collinear rectangles of one thickness merged into runs: ``[(a, b, t, kind)]`` (kind wall | parapet)."""
    groups: dict = {}
    for cx, cy, ux, uy, L, t, kind in rects:
        key = (round(math.degrees(math.atan2(uy, ux)), 1), kind)
        off = -uy * cx + ux * cy                    # the signed offset of the centre line
        s = ux * cx + uy * cy
        groups.setdefault(key, []).append([off, s - L / 2, s + L / 2, t, ux, uy])
    runs = []
    for (_ang, kind), items in groups.items():
        items.sort(key=lambda q: (round(q[0], 2), round(q[3], 2), q[1]))
        cur = None
        for it in items:
            if cur and abs(it[0] - cur[0]) <= 0.015 and abs(it[3] - cur[3]) <= 0.011:
                gap = it[1] - cur[2]
                fill = False
                if MERGE_GAP_M < gap <= MAX_FILL_GAP_M:
                    ux, uy = cur[4], cur[5]
                    a = (ux * (cur[2] + 0.004) - uy * cur[0], uy * (cur[2] + 0.004) + ux * cur[0])
                    b = (ux * (it[1] - 0.004) - uy * cur[0], uy * (it[1] - 0.004) + ux * cur[0])
                    g = LineString([a, b])
                    fill = cover.covers(g)
                if gap <= MERGE_GAP_M or fill:
                    cur[2] = max(cur[2], it[2])
                    continue
            if cur:
                runs.append((cur, kind))
            cur = list(it)
        if cur:
            runs.append((cur, kind))
    out = []
    for (off, s0, s1, t, ux, uy), kind in runs:
        a = (r5(ux * s0 - uy * off), r5(uy * s0 + ux * off))
        b = (r5(ux * s1 - uy * off), r5(uy * s1 + ux * off))
        if math.dist(a, b) >= 0.05:
            out.append((a, b, t, kind))
    out.sort(key=lambda q: (q[3], round(min(q[0][1], q[1][1]), 3), round(min(q[0][0], q[1][0]), 3)))
    return out


def dominant_angle(polys: list) -> float:
    """The building's dominant wall direction (degrees in [0, 90)), length-weighted, 0.5 degree bins refined."""
    hist: dict = {}
    for p in polys:
        r = _rect_raw(p)
        if r:
            a, L = r
            k = round(a * 2) / 2 % 90
            hist[k] = hist.get(k, 0.0) + L
    if not hist:
        return 0.0
    peak = max(hist, key=hist.get)
    num = den = 0.0
    for p in polys:
        r = _rect_raw(p)
        if r:
            a, L = r
            d = (a - peak + 45) % 90 - 45
            if abs(d) <= 1.0:
                num += d * L
                den += L
    return (peak + (num / den if den else 0.0)) % 90


def _rect_raw(p: Polygon):
    m = p.minimum_rotated_rectangle
    if m.geom_type != "Polygon":
        return None
    c = list(m.exterior.coords)
    e0 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e1 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    e = e0 if math.hypot(*e0) >= math.hypot(*e1) else e1
    return math.degrees(math.atan2(e[1], e[0])) % 90, math.hypot(*e)


def _geom(row) -> Optional[Polygon]:
    try:
        g = wkt.loads(row["geometry"])
    except Exception:                                    # noqa: BLE001 - a broken row is skipped
        return None
    if g.geom_type == "MultiPolygon":
        g = max(g.geoms, key=lambda q: q.area)
    return g if g.geom_type == "Polygon" and g.area > 1e-4 else None


def build_floor(rows: list, angle: float, shift: tuple) -> Floor:
    """One floor's regularised layout (the module docstring) in the building frame."""
    def T(g):
        g = affinity.rotate(g, -angle, origin=(0.0, 0.0))
        return affinity.translate(g, -shift[0], -shift[1])

    wall_polys, rail_polys, cols, ops, areas, feats = [], [], [], [], [], []
    for row in rows:
        g = _geom(row)
        if g is None:
            continue
        g = T(g)
        st, et = row["entity_subtype"], row["entity_type"]
        if st == "WALL":
            wall_polys.append(g)
        elif st == "RAILING":
            rail_polys.append(g)
        elif st == "COLUMN":
            r = _rect(g)
            if r:
                cols.append(_rect_poly(r))
        elif et == "opening":
            ops.append((st, g))
        elif et == "area":
            areas.append((st, g, row.get("unit_id") or ""))
        elif et == "feature":
            feats.append((st, g))
    rects = []
    for polys, kind in ((wall_polys, "wall"), (rail_polys, "parapet")):
        for g in polys:
            r = _rect(g)
            if r:
                rects.append(r + (kind,))
    cover = unary_union([_rect_poly(r[:6]) for r in rects] + cols).buffer(0.003)
    walls = []
    for i, (a, b, t, kind) in enumerate(_merge_runs(rects, cover)):
        walls.append(FC.Wall(f"w{i + 1}", a, b, t, truth={"parapet": True, "height": PARAPET_H}
                             if kind == "parapet" else {}))
    fl = Floor(rows[0]["floor_id"] if rows else "", walls, cols, [], areas, feats)
    _place_openings(fl, ops)
    u = unary_union([w.rect() for w in walls] + cols)
    fl.union = u.buffer(CLOSE_M, join_style=2).buffer(-CLOSE_M, join_style=2)
    return fl


def _rect_poly(r) -> Polygon:
    cx, cy, ux, uy, L, t = r[:6]
    nx, ny = -uy, ux
    hl, ht = L / 2, t / 2
    return Polygon([(cx - ux * hl - nx * ht, cy - uy * hl - ny * ht), (cx + ux * hl - nx * ht, cy + uy * hl - ny * ht),
                    (cx + ux * hl + nx * ht, cy + uy * hl + ny * ht), (cx - ux * hl + nx * ht, cy - uy * hl + ny * ht)])


def _place_openings(fl: Floor, ops: list) -> None:
    placed: dict = {}
    rects = [(w, w.rect()) for w in fl.walls if not w.truth.get("parapet")]
    for st, g in sorted(ops, key=lambda q: (round(q[1].centroid.y, 3), round(q[1].centroid.x, 3))):
        best, share = None, 0.0
        for w, r in rects:
            if not r.intersects(g):
                continue
            s = r.intersection(g).area / g.area
            if s > share:
                best, share = w, s
        if best is None or share < 0.3:
            continue
        w = best
        ux, uy = w.u
        proj = [(x - w.a[0]) * ux + (y - w.a[1]) * uy for x, y in g.exterior.coords]
        lo, hi = max(0.0, min(proj)), min(w.length, max(proj))
        kind = "window" if st == "WINDOW" else "door"
        width = round((hi - lo) / 0.05) * 0.05
        width = max(0.6 if kind == "door" else 0.4, width)
        if width > w.length - 0.04:
            continue
        s = min(max((lo + hi) / 2, width / 2 + 0.02), w.length - width / 2 - 0.02)
        s = r5(s)
        busy = placed.setdefault(w.id, [])
        if any(abs(s - s2) < (width + w2) / 2 + 0.05 for s2, w2 in busy):
            continue
        busy.append((s, width))
        op = FC.Opening(f"o{len(fl.openings) + 1}", kind, w.id, s, round(width, 2))
        op.truth_type = kind
        op.entrance = st == "ENTRANCE_DOOR"
        fl.openings.append(op)


# --- rooms and labels -----------------------------------------------------------------------------------------------

def label_rooms(fl: Floor, profile: dict, style: ST.Style, rng: random.Random) -> None:
    polys = [fl.union] if fl.union.geom_type == "Polygon" else list(fl.union.geoms)
    faces = [Polygon(h.coords) for p in polys for h in p.interiors]
    faces = [f for f in faces if f.area >= ROOM_MIN_M2]
    faces.sort(key=lambda f: (round(f.centroid.y, 3), round(f.centroid.x, 3)))
    living_units = {u for st, _g, u in fl.areas if st in LIVING}
    biggest_room: dict = {}
    for st, g, u in fl.areas:
        if st == "ROOM" and u not in living_units and g.area > biggest_room.get(u, (0, None))[0]:
            biggest_room[u] = (g.area, g)
    as_living = {id(v[1]) for v in biggest_room.values()}
    stairs = unary_union([g for st, g in fl.features if st == "STAIRS"]) if any(
        st == "STAIRS" for st, _ in fl.features) else None
    entrance_pts = [fl_wall_point(fl, op) for op in fl.openings if getattr(op, "entrance", False)]
    for f in faces:
        inside = [(st, g, u) for st, g, u in fl.areas if f.contains(g.representative_point())]
        if not inside:
            fl.faces.append((f, "", "other", None))
            continue
        inside.sort(key=lambda q: -q[1].area)
        st, g, u = inside[0]
        rtype = "living" if id(g) in as_living else TYPE_OF.get(st, "other")
        if rtype == "bathroom":
            feats = {fs for fs, fg in fl.features if f.contains(fg.representative_point())}
            if f.area < 2.5 and not feats & {"BATHTUB", "SHOWER"}:
                rtype = "wc"
        if rtype == "hall" and stairs is not None and f.intersection(stairs).area > 0.25 * f.area:
            rtype = "stair"
        kinds = {TYPE_OF.get(s2, "other") for s2, _g, _u in inside}
        if rtype == "hall" and any(f.buffer(0.4).contains(Point(p)) for p in entrance_pts if p):
            text = ST.spell("ANTRE", style)
        else:
            text = ST.label_for(profile, rtype, rng, style)
        if rtype == "living" and "kitchen" in kinds:
            text = f"{text} + {ST.label_for(profile, 'kitchen', rng, style)}"
        part = f.intersection(g)
        part = part if part.geom_type == "Polygon" and part.area > 0.3 else f
        at = polylabel(part, tolerance=0.05)
        fl.faces.append((f, text, B.room_type_for(text, f.area), (at.x, at.y)))


def fl_wall_point(fl: Floor, op) -> Optional[tuple]:
    w = next((w for w in fl.walls if w.id == op.wall), None)
    return w.at(op.s) if w else None


# --- the truth ------------------------------------------------------------------------------------------------------

WALL_LIST_MIN_M = 0.30       # a wall piece shorter than this, or than 1.5 times its thickness, is drawn but not listed


def is_listed_wall(w: FC.Wall) -> bool:
    """A wall the truth lists: not a stub or a pier (a corner filler, a jamb piece) shorter than ``WALL_LIST_MIN_M``
    or than 1.5 times its thickness; those are drawn (they close the rooms) but a reader may fairly fold them into
    their neighbours."""
    return w.length >= WALL_LIST_MIN_M and w.length >= 1.5 * w.t


def floor_truth(fl: Floor, lid: str) -> dict:
    rooms = []
    for i, (f, text, rtype, _at) in enumerate(fl.faces):
        ring = FC._canon(list(f.exterior.coords)[:-1])
        rooms.append({"id": f"r_{lid}_{i + 1:03d}", "label": text, "room_type": rtype if text else "other",
                      "area": round(f.area, 4), "centroid": FC.rp((f.centroid.x, f.centroid.y)),
                      "polygon": [FC.rp(q) for q in ring]})
    doors, windows = [], []
    for op in fl.openings:
        w = next(w for w in fl.walls if w.id == op.wall)
        rec = {"id": "", "width": FC.r6(op.width), "center": FC.rp(w.at(op.s)), "type": op.truth_type}
        if getattr(op, "entrance", False):
            rec["flat_entrance"] = True
        (doors if op.truth_type == "door" else windows).append(rec)
    for prefix, items in (("d", doors), ("win", windows)):
        for i, rec in enumerate(items):
            rec["id"] = f"{prefix}_{lid}_{i + 1:03d}"
    listed = [w for w in fl.walls if is_listed_wall(w)]
    walls = [{"id": f"w_{lid}_{i + 1:03d}", "start": FC.rp(w.a), "end": FC.rp(w.b), "thickness": FC.r6(w.t),
              **w.truth} for i, w in enumerate(listed)]
    stairs = []
    for i, (grp, risers) in enumerate(stair_groups(fl)):
        x0, y0, x1, y1 = grp.bounds
        stairs.append({"id": f"s_{lid}_{i + 1:03d}", "kind": "flight", "center": FC.rp(((x0 + x1) / 2, (y0 + y1) / 2)),
                       "risers": risers, "box": [FC.rp((x0, y0)), FC.rp((x1, y1))]})
    return {"rooms": rooms, "doors": doors, "windows": windows, "openings": [], "walls": walls, "stairs": stairs}


TREAD_M = 0.28


def stair_groups(fl: Floor) -> list:
    """The stairs of a floor: the dataset's STAIRS polygons grouped where they touch; risers from the treads drawn."""
    polys = [g for st, g in fl.features if st == "STAIRS"]
    if not polys:
        return []
    u = unary_union([p.buffer(0.03) for p in polys])
    comps = [u] if u.geom_type == "Polygon" else list(u.geoms)
    out = []
    for c in sorted(comps, key=lambda q: (round(q.bounds[1], 3), round(q.bounds[0], 3))):
        members = [p for p in polys if c.contains(p.representative_point())]
        if not members or sum(p.area for p in members) < 0.5:
            continue
        risers = sum(len(stair_treads(p, members)) + 1 for p in members) if not _tread_polys(members) else \
            len(members) + 1
        out.append((unary_union(members), risers))
    return out


def _tread_polys(members: list) -> bool:
    return len(members) >= 4 and max(p.area for p in members) < 1.2


def building_layout(floors: dict, profile: dict, style: ST.Style, rng: random.Random) -> dict:
    """``floors``: {floor_id: rows} -> ``{"floors": [Floor], "floor_ids", "rotation_deg", "shift_m",
    "building_id", "site_id"}``: one rotation and one origin (the first floor's wall union's min corner) for all."""
    fids = sorted(floors, key=lambda f: int(float(f)))
    first = floors[fids[0]]
    raw = [g for g in (_geom(r) for r in first if r["entity_subtype"] == "WALL") if g is not None]
    angle = dominant_angle(raw)
    ref = build_floor(first, angle, (0.0, 0.0))
    b = unary_union([w.rect() for w in ref.walls]).bounds if ref.walls else (0.0, 0.0, 0.0, 0.0)
    shift = (b[0], b[1])
    built, used = [], []
    for f in fids:
        fl = build_floor(floors[f], angle, shift)
        if fl.walls:
            label_rooms(fl, profile, style, rng)
            built.append(fl)
            used.append(f)
    return {"floors": built, "floor_ids": used, "rotation_deg": round(angle, 4),
            "shift_m": [round(shift[0], 4), round(shift[1], 4)],
            "building_id": first[0]["building_id"] if first else None,
            "site_id": first[0].get("site_id") if first else None}


def truth_of(name: str, layout: dict, style: ST.Style) -> dict:
    """The project's reading truth (``wenart.reading_check.truth.synthetic_truth`` reads it)."""
    levels, per_level = [], {}
    for k, fl in enumerate(layout["floors"]):
        lid = f"L{k}"
        levels.append({"id": lid, "label": "Zemin Kat" if k == 0 else f"{k}. Kat",
                       "elevation": round(k * style.storey_m, 3), "order": k})
        per_level[lid] = floor_truth(fl, lid)
    return {"project": name, "source": "synthetic", "status": "accepted",
            "units": "building metres (outer wall faces from the origin of each plan)",
            "levels": levels, "per_level": per_level, "failure_class": "dataset_swiss_dwellings", "lesson": None,
            "summary": f"Swiss Dwellings building {layout['building_id']}, {len(levels)} floor(s), redrawn in a "
                       f"Turkish drafting style",
            "dataset": dict(DATASET, building_id=layout["building_id"], site_id=layout["site_id"],
                            floor_ids=layout["floor_ids"], rotation_deg=layout["rotation_deg"],
                            shift_m=layout["shift_m"]),
            "style": style.summary()}


def read_rows(csv_path: Path, floor_ids: Optional[set] = None) -> dict:
    """``{building_id: {floor_id: [rows]}}`` of a geometries CSV (plain or .gz), only ``floor_ids`` when given."""
    import csv
    import gzip

    csv.field_size_limit(10 ** 9)
    opener = gzip.open if str(csv_path).endswith(".gz") else open
    out: dict = {}
    with opener(csv_path, "rt", newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if floor_ids is not None and row["floor_id"] not in floor_ids:
                continue
            out.setdefault(row["building_id"], {}).setdefault(row["floor_id"], []).append(row)
    return out


def stair_treads(p: Polygon, members: list) -> list:
    """Tread lines across a flight polygon every ``TREAD_M`` along its long axis (none when the polygons are treads)."""
    if _tread_polys(members):
        return []
    r = _rect(p)
    if not r:
        return []
    cx, cy, ux, uy, L, t = r
    nx, ny = -uy, ux
    n = int(L / TREAD_M)
    out = []
    for k in range(1, n):
        s = -L / 2 + k * L / n
        a = (cx + ux * s - nx * t / 2, cy + uy * s - ny * t / 2)
        b = (cx + ux * s + nx * t / 2, cy + uy * s + ny * t / 2)
        out.append((a, b))
    return out
