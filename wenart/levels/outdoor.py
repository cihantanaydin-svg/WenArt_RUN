"""Labelled outdoor spaces and the drawn site symbols (26 Oct 2026; CLAUDE.md: every fix a rule for every project).

Why: real06's DWG labels a "VERANDA 22,80m²" in the inner corner of its L-shaped ground floor and a "BALKON 11,80m²"
over it on the upper floor; neither has walls around it, so the reading recorded both as label-only site areas
(``polygon: null``) and nothing was built: the 2.95 m garden door and the house's door opened onto a stepped entrance
platform, the upper doors into the air. The user: "the issue is not just veranda; think to solve issues like
veranda". The same reading left real06's 42 drawn site symbols (grid bubbles, columns, sills, level marks, the
veranda's steps) untyped: nothing said what they were.

What (pure; every item ``inferred`` with its evidence and listed in ``level_inference.inferred``; the drawn values
stay):

- ``space_kind``: one vocabulary table (``SPACE_WORDS``: Turkish, English, German, French) of the labelled outdoor
  spaces: veranda, porch (sundurma), loggia, winter garden (kış bahçesi), pergola (çardak), balcony (balkon),
  terrace (teras), deck, patio, courtyard (avlu); each with its cover (``roof`` a light roof on posts, ``glass``,
  ``pergola``, ``building`` (a loggia under the floor above), None open). Parking, pool and garden words are not
  spaces (their own rules build them).
- ``stated_area``: the area written with the label (``22,80m²``, ``24 m2``, ``110 sq ft``).
- ``close_region`` (the reading, page metres): the region the label sits in, closed from the drawn strokes around
  it (``read_outline``): one pass per layer (a layer named for an outdoor space first, then by stroke count, then
  all layers together; hatches, texts, dimensions, doors, furniture, axes and level marks never), the building's
  facade (the walls' outline) as a boundary, every free stroke end bridged to the next stroke or free end within
  ``SPACE["gap_m"]`` (a column between two edge lines, an edge line that stops short of the facade); the face that
  holds the label and whose area is nearest the stated area (within ``area_tol``) wins; without a stated area only a
  layer named for an outdoor space may close it. ``drawn_steps``: parallel lines outside an edge of the face at a
  tread's spacing are its drawn steps.
- ``rectangle_space``: no closed region: a rectangle in the inner corner the label sits in (both facades its sides,
  the label at its centre), else against the nearest facade (the label at its centre, as deep as twice the label's
  distance); scaled to the stated area; the building cut out.
- ``outdoor_spaces``: one record per labelled space that no room and no built surface holds, on every level
  (``site.outdoor_spaces``): its polygon and method, the doors that open onto it, its floor level (a level mark
  inside it, else the doors' thresholds, else its level's floor), ``elevated`` (over ``elevated_min`` above the
  ground: a slab with a guard on its open edges, no base walls or steps), its drawn steps, its drawn columns and its
  ``roof`` (``roof_plan``: the part no floor or space above covers, a light roof, glass roof or pergola at the floor
  line of the level above (else its level's eaves), falling ``roof_fall`` away from the facade, kept under the
  windows above; drawn columns as posts, an inferred post at every open corner more than ``post_reach`` from a
  support). The site build makes them platforms (``wenart.blender.site.platforms``), the entrances use them
  (``wenart.levels.model``: a door onto a space has no steps of its own; the space's steps lead down).
- ``type_site_decor``: every drawn site symbol is typed (``inferred_as`` with the reason): by its layer or block
  name first (``DECOR_WORDS``: axis bubbles, columns, sills, level marks, doors, annotation, lamps, bollards, posts,
  planters, outdoor-space details, steps, hatches, walls, furniture, cars; plant words make it vegetation), then by
  its shape: a circle on the extension of a wall axis (three or more) is a grid bubble, a circle of at least
  ``plant_min_m`` across is a tree (CLAUDE.md vegetation rule: a row of >= 5 equal circles is a hedge, single
  symbols are trees, a crown under 1.5 m radius a shrub; built by the Milestone 13 vegetation), anything else stays
  unbuilt with its reason.
"""
from __future__ import annotations

import math
import re
from typing import Optional, Sequence

from wenart import building as B
from wenart import geometry as G

# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

# (kind, cover, pattern on fold_ascii lower text). Turkish words match at a word start (inflected forms:
# "balkonu", "terası"); English, German and French words as whole words. The first hit wins (a winter garden before
# a garden word, a porch before a terrace).
SPACE_WORDS: tuple[tuple[str, Optional[str], str], ...] = (
    ("winter_garden", "glass", r"\b(kis bahce|winter ?gardens?\b|wintergarten|jardin d.?hiver|conservatory\b|"
                               r"sun ?room\b|sera\b)"),
    ("veranda", "roof", r"\b(veranda|verandah)"),
    ("porch", "roof", r"\b(sundurma|portik|porch(es)?\b|portico\b|porche\b|vordach\b|saçak alti)"),
    ("loggia", "building", r"\b(loggia|lodzi|lojya)"),
    ("pergola", "pergola", r"\b(pergola|cardak|kameriye)"),
    ("balcony", None, r"\b(balkon|balcony\b|balconies\b|balcon\b)"),
    ("terrace", None, r"\b(teras|terrace|terrasse|dachterrasse|sit ?out\b|otla\b|guneslenme)"),
    ("deck", None, r"\b(deck\b|decks\b|sundeck\b|guverte)"),
    ("patio", None, r"\b(patio\b|patios\b)"),
    ("courtyard", None, r"\b(avlu|courtyard\b|innenhof\b)"),
)
# Words that name something else outdoors (built by their own rules): parking, pools, gardens and lawns.
NOT_SPACE_RE = re.compile(r"\b(otopark|park yeri|garaj|car porch|carport|parking|garage|stellplatz|havuz|pool|piscine|"
                          r"schwimmbad)\b")
_SPACE_RE = [(kind, cover, re.compile(p)) for kind, cover, p in SPACE_WORDS]
# Layer names that say a stroke draws an outdoor space's edge (the closing pass tries these layers first).
SPACE_LAYER_RE = re.compile(r"(BALKON|BALCON|TERAS|TERRAC|VERANDA|SUNDURMA|PORCH|DECK|PATIO|LOGGIA|PERGOLA|AVLU)")

# Layers that never close a space: hatches, texts, dimensions, doors and windows, furniture, axes, level marks,
# sections, plants (upper-case folded words; keys of up to three letters only as a whole word).
SKIP_LAYER_WORDS = ("TARAMA", "HATCH", "YAZI", "TEXT", "ANNO", "DIM", "OLCU", "KOTA", "KOT", "LEVEL", "KAPI", "DOOR",
                    "PENCERE", "WINDOW", "TEFRIS", "MOBILYA", "FURN", "AKS", "AXIS", "GRID", "KESIT", "SECTION",
                    "AGAC", "TREE", "PLANT", "BITKI", "PEYZAJ")

SPACE = {
    "area_tol": 0.15,          # a closed region within 15 % of the stated area is the space
    "gap_m": 0.5,              # free stroke ends are bridged up to this (a column, a short stop at the facade)
    "reach_min": 4.0, "reach_max": 15.0,   # strokes within this of the label (2.5 x the side of the stated area)
    "min_area": 1.5, "max_area": 400.0,
    "label_reach_m": 1.5,      # a built surface or room this close to the label already holds it
    "door_probe": 0.3,         # a door opens onto a space when its probe (this far out of the face) is on it
    "door_reach": 0.3,         # ... or this close to it
    "door_level_tol": 0.2,     # ... and its threshold is this close to the space's floor
    "mark_reach": 0.3,
    "elevated_min": 1.5,       # a space this far above the ground under it is a slab with a guard
    "slab_t": 0.20,            # an elevated space's slab
    "roof_t": 0.18, "roof_fall": 0.02, "min_clear": 2.3, "sill_gap": 0.15, "eaves_extra": 0.20,
    "post_reach": 1.5,         # an open roof corner farther than this from a support gets a post
    "post_span": 4.0,          # posts along an open edge at most this far apart
    "post_size": 0.15,
    "column_reach": 0.4,       # a drawn column this close to a space supports it
    "rect_reach": 8.0,         # the rectangle fallback looks for a facade this close to the label
    "rect_depth": (1.2, 6.0),  # its depth range (twice the label's distance, clamped)
    "rect_width": 3.0,         # its width with no stated area and no door
    "corner_dot": 0.15,        # two facade edges this close to perpendicular make an inner corner ...
    "corner_gap": 0.5,         # ... when their lines meet this close to both
    "tread": (0.22, 0.45),     # drawn steps: parallel lines at a tread's spacing outside an edge
    "plant_min_m": 0.3,        # a circle symbol at least this wide may be a plant
    "axis_tol": 0.03, "axis_min": 3,
    "overlap_m2": 0.25,        # a space reaching this far into the level's wall outline gets the building cut out
    "flush_m": 0.15,           # a space at most this far over the garden needs no steps (site.PLATFORM level_tol)
}


def fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).split())


def space_kind(label) -> Optional[dict]:
    """``{"kind", "cover", "word"}`` of an outdoor-space label (``SPACE_WORDS``), or None (not a space, or a parking,
    pool or garage word)."""
    text = fold(label)
    if not text or NOT_SPACE_RE.search(text):
        return None
    for kind, cover, pattern in _SPACE_RE:
        m = pattern.search(text)
        if m:
            return {"kind": kind, "cover": cover, "word": m.group(0).strip()}
    return None


AREA_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(m²|m2|m\^2|sqm|qm|sq\.? ?ft|sft|ft²|ft2)(?![a-z])", re.I)
SQFT_M2 = 0.09290304


def parse_area(text) -> Optional[float]:
    """The area written in a text (m², or sq ft converted), or None."""
    m = AREA_RE.search(str(text or "").replace(" ", " "))
    if not m:
        return None
    value = float(m.group(1).replace(",", "."))
    unit = m.group(2).lower()
    if "ft" in unit:
        value *= SQFT_M2
    return round(value, 3) if value > 0 else None


def stated_area(area: dict) -> Optional[dict]:
    """``{"m2", "text", "entity"}``: the area written with a site label (the reading's ``stated_area_m2``, else an
    evidence text or the label itself), or None."""
    if isinstance(area.get("stated_area_m2"), (int, float)) and area["stated_area_m2"] > 0:
        return {"m2": float(area["stated_area_m2"]), "text": area.get("area_text"), "entity": None}
    for ev in area.get("evidence") or []:
        if isinstance(ev, dict):
            v = parse_area(ev.get("text"))
            if v:
                return {"m2": v, "text": ev.get("text"), "entity": ev.get("entity")}
    for key in ("label_raw", "label"):
        v = parse_area(area.get(key))
        if v:
            return {"m2": v, "text": area.get(key), "entity": None}
    return None


def _words(name) -> list[str]:
    folded = B.fold_ascii(re.split(r"[$|]", str(name or ""))[-1]).upper()
    return [w for w in re.split(r"[^A-Z0-9]+", folded) if w]


def _hit(key: str, words: list[str]) -> bool:
    return key in words if len(key) <= 3 else any(key in w for w in words)


def layer_skipped(layer) -> bool:
    words = _words(layer)
    return any(_hit(k, words) for k in SKIP_LAYER_WORDS)


# --------------------------------------------------------------------------
# The region the label sits in (the reading: drawn strokes, page metres)
# --------------------------------------------------------------------------

def _segments_of(pts) -> list:
    return [(tuple(pts[i]), tuple(pts[i + 1])) for i in range(len(pts) - 1) if G.distance(pts[i], pts[i + 1]) > 1e-6]


def _bridges(strokes: list[dict], fixed_lines, gap: float) -> list[tuple]:
    """Bridging segments for the free ends of ``strokes`` (pure, shapely): an end that touches no other stroke or
    boundary line is extended along its direction to the first stroke or line within ``gap``, else joined to the
    nearest other free end within ``gap``. ``[(p, q, length)]``."""
    from shapely import STRtree
    from shapely.geometry import LineString, Point

    geoms = [LineString(s["pts"]) for s in strokes] + list(fixed_lines)
    tree = STRtree(geoms)
    ends = []
    for k, s in enumerate(strokes):
        pts = s["pts"]
        if s.get("closed") or len(pts) < 2 or G.distance(pts[0], pts[-1]) < 1e-6:
            continue
        for p, q in ((pts[-1], pts[-2]), (pts[0], pts[1])):
            ends.append((k, tuple(p), tuple(q)))

    def touching(k, geom, tol):
        return [j for j in tree.query(geom.buffer(tol) if tol > 0 else geom) if j != k
                and geoms[j].distance(geom) <= tol + 1e-9]

    free = [(k, p, q) for k, p, q in ends if not touching(k, Point(p), 0.002)]
    out = []
    used = set()
    for k, p, q in free:
        d = G.distance(q, p)
        if d <= 1e-9:
            continue
        ux, uy = (p[0] - q[0]) / d, (p[1] - q[1]) / d
        ray = LineString([p, (p[0] + ux * gap, p[1] + uy * gap)])
        best = None
        for j in touching(k, ray, 0.0):
            hit = ray.intersection(geoms[j])
            for g in getattr(hit, "geoms", [hit]):
                for c in (list(g.coords) if hasattr(g, "coords") and not g.is_empty else []):
                    dist = G.distance(p, c)
                    if dist > 1e-6 and (best is None or dist < best[0]):
                        best = (dist, c)
        if best is not None:
            out.append((p, tuple(best[1]), round(best[0], 3)))
            continue
        near = [(G.distance(p, p2), j, p2) for j, (k2, p2, _q2) in enumerate(free) if k2 != k
                and G.distance(p, p2) <= gap]
        if near:
            dist, j, p2 = min(near)
            key = tuple(sorted((p, p2)))
            if key not in used:
                used.add(key)
                out.append((p, p2, round(dist, 3)))
    return out


def _faces(anchor, strokes: list[dict], facade, gap: float) -> list[dict]:
    """The faces holding ``anchor`` that ``strokes`` (with their free ends bridged) and the facade close (pure,
    shapely): ``[{"polygon": shapely Polygon, "bridges", "ids"}]``, outside the facade."""
    from shapely.geometry import LineString, Point
    from shapely.ops import polygonize, unary_union

    pt = Point(anchor)
    fixed = []
    if facade is not None and not facade.is_empty:
        for poly in getattr(facade, "geoms", [facade]):
            fixed.append(poly.exterior)
    lines = [LineString(s["pts"]) for s in strokes if len(s["pts"]) >= 2]
    bridges = _bridges(strokes, fixed, gap)
    lines += [LineString([p, q]) for p, q, _ in bridges]
    if not lines:
        return []
    merged = unary_union(lines + fixed)
    out = []
    for face in polygonize(merged):
        if not face.is_valid or face.area <= 1e-6 or not face.contains(pt):
            continue
        if facade is not None and not facade.is_empty and facade.buffer(1e-6).contains(face.representative_point()):
            continue
        ring = face.exterior
        ids = sorted({s["id"] for s, g in zip(strokes, lines) if g.distance(ring) <= 0.01
                      and g.length > 0.05 and ring.buffer(0.01).intersection(g).length >= 0.5 * min(g.length, 0.5)})
        out.append({"polygon": face, "bridges": [b for b in bridges if ring.distance(Point(b[0])) <= 0.01],
                    "ids": ids})
    return out


def close_region(anchor: Sequence[float], strokes: Sequence[dict], facade=None, stated: Optional[float] = None,
                 gap: float = SPACE["gap_m"]) -> Optional[dict]:
    """The region a site label sits in, closed from the drawn strokes around it (pure, shapely; module docstring).
    ``strokes``: ``[{"id", "pts", "layer", "closed"}]`` (metres, the label's frame); ``facade``: the building's
    filled outline (a shapely polygon) or None. Returns ``{"polygon": [[x, y]], "area_m2", "stated_m2", "off",
    "layers", "entities", "bridges": [m], "pass", "reason"}`` or None."""
    from shapely.geometry import LineString, Point

    pt = Point(anchor)
    reach = SPACE["reach_min"] if not stated else min(SPACE["reach_max"], max(SPACE["reach_min"],
                                                                                2.5 * math.sqrt(stated)))
    near = []
    for s in strokes:
        pts = [tuple(p) for p in s.get("pts") or []]
        if len(pts) < 2 or layer_skipped(s.get("layer")):
            continue
        if LineString(pts).distance(pt) > reach:
            continue
        near.append(dict(s, pts=pts))
    if not near:
        return None
    by_layer: dict = {}
    for s in near:
        by_layer.setdefault(str(s.get("layer") or ""), []).append(s)
    named = [ly for ly in by_layer if SPACE_LAYER_RE.search(B.fold_ascii(ly).upper())]
    rest = sorted((ly for ly in by_layer if ly not in named), key=lambda ly: (-len(by_layer[ly]), ly))
    passes = [(ly, by_layer[ly], True) for ly in sorted(named)] + [(ly, by_layer[ly], False) for ly in rest]
    if len(by_layer) > 1:
        passes.append(("*", near, False))
    tol = SPACE["area_tol"]
    for name, group, space_layer in passes:
        faces = _faces(anchor, group, facade, gap)
        if not faces:
            continue
        if stated:
            f = min(faces, key=lambda f: abs(f["polygon"].area - stated))
            off = abs(f["polygon"].area - stated) / stated
            if off > tol:
                continue
        else:
            if not space_layer:
                continue
            f = min(faces, key=lambda f: f["polygon"].area)
            off = None
            if not SPACE["min_area"] <= f["polygon"].area <= SPACE["max_area"]:
                continue
        # a face whose ring runs along the facade and back has a hair-thin sliver: a tiny opening (shrink, then grow
        # back with square corners) removes it
        poly = f["polygon"].buffer(-0.002, join_style=2).buffer(0.002, join_style=2)
        if poly.geom_type != "Polygon":
            poly = max(getattr(poly, "geoms", [f["polygon"]]), key=lambda g: g.area)
        poly = poly.simplify(0.005)
        coords = [[round(x, 4), round(y, 4)] for x, y in list(poly.exterior.coords)[:-1]]
        layers = sorted({str(s.get("layer") or "") for s in group if s["id"] in f["ids"]}) or [name]
        what = (f"the {len(f['ids'])} stroke(s) on layer(s) {', '.join(repr(x) for x in layers[:3])} around the label"
                + (" and the facade" if facade is not None else "")
                + (f", {len(f['bridges'])} gap(s) of up to {max(b[2] for b in f['bridges']):.2f} m closed"
                   if f["bridges"] else ""))
        area = round(poly.area, 3)
        return {"polygon": coords, "area_m2": area, "stated_m2": stated, "off": None if off is None else round(off, 4),
                "layers": layers, "entities": f["ids"][:40], "bridges": [b[2] for b in f["bridges"]],
                "pass": name, "method": "strokes",
                "reason": f"closed from {what}: {area:.2f} m²"
                          + (f", {off * 100:.1f} % off the stated {stated:.2f} m² (within {tol * 100:.0f} %)"
                             if stated else " (no stated area; a layer named for an outdoor space)")}
    return None


def drawn_steps(polygon: Sequence[Sequence[float]], strokes: Sequence[dict]) -> Optional[dict]:
    """Steps drawn outside an edge of a space (pure): two or more lines parallel to an edge, outside it, each at a
    tread's spacing (``SPACE["tread"]``) from the one before (the first from the edge), overlapping the edge by at
    least 0.6 m. ``{"edge": [p0, p1] (the stretch of the edge the flight leaves from), "dir": outward, "treads",
    "tread_m", "width_m", "entities", "reason"}`` or None."""
    poly = [tuple(map(float, p)) for p in polygon]
    if len(poly) < 3:
        return None
    if G.polygon_signed_area(poly) < 0:
        poly = poly[::-1]
    segs = []
    for s in strokes:
        for a, b in _segments_of(s.get("pts") or []):
            segs.append((s.get("id"), a, b))
    t0, t1 = SPACE["tread"]
    best = None
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 0.6:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = uy, -ux                                     # counter-clockwise: the right side is outside
        lines = []
        for sid, p, q in segs:
            dp = (p[0] - a[0]) * nx + (p[1] - a[1]) * ny
            dq = (q[0] - a[0]) * nx + (q[1] - a[1]) * ny
            if abs(dp - dq) > 0.01 or dp < 0.05 or dp > 2.5:
                continue
            sp = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
            sq = (q[0] - a[0]) * ux + (q[1] - a[1]) * uy
            lo, hi = max(min(sp, sq), 0.0), min(max(sp, sq), length)
            if hi - lo < 0.6:
                continue
            lines.append((round(dp, 3), lo, hi, sid))
        lines.sort()
        chain, prev = [], 0.0
        for d, lo, hi, sid in lines:
            if chain and abs(d - chain[-1][0]) < 0.01:
                continue
            if t0 <= d - prev <= t1:
                chain.append((d, lo, hi, sid))
                prev = d
            elif d - prev > t1:
                break
        if len(chain) < 2:
            continue
        lo = max(c[1] for c in chain)
        hi = min(c[2] for c in chain)
        if hi - lo < 0.6:
            continue
        tread = chain[-1][0] / len(chain)
        rec = {"edge": [[round(a[0] + ux * lo, 4), round(a[1] + uy * lo, 4)],
                        [round(a[0] + ux * hi, 4), round(a[1] + uy * hi, 4)]],
               "dir": [round(nx, 6), round(ny, 6)], "treads": len(chain), "tread_m": round(tread, 3),
               "width_m": round(hi - lo, 3), "entities": sorted({str(c[3]) for c in chain}),
               "reason": f"{len(chain)} drawn tread line(s) {tread:.2f} m apart outside the edge, {hi - lo:.2f} m "
                         f"wide: the space's steps as drawn"}
        if best is None or rec["treads"] > best["treads"]:
            best = rec
    return best


def read_outline(area: dict, strokes: Sequence[dict], facade=None) -> Optional[dict]:
    """The reading's step for one site area (page metres; ``wenart.ingest.generic.core``): an outdoor-space label
    without a closed face gets ``outline_inferred`` (``close_region``, with its ``steps`` when drawn) when its
    strokes close; the area's drawn ``polygon`` stays None. Returns the record (also set on the area) or None."""
    label = area.get("label_raw") or area.get("label")
    if area.get("polygon") or space_kind(label) is None or not area.get("anchor"):
        return None
    st = stated_area(area)
    rec = close_region(area["anchor"], strokes, facade, st["m2"] if st else None)
    if rec is None:
        return None
    steps = drawn_steps(rec["polygon"], [s for s in strokes if not layer_skipped(s.get("layer"))
                                         and str(s.get("layer") or "") in rec["layers"]])
    if steps is not None:
        rec["steps"] = steps
    rec["inferred"] = True
    area["outline_inferred"] = rec
    return rec


# --------------------------------------------------------------------------
# The rectangle fallback (building frame)
# --------------------------------------------------------------------------

def _ccw(poly) -> list[tuple[float, float]]:
    pts = [(float(p[0]), float(p[1])) for p in poly]
    return pts if G.polygon_signed_area(pts) >= 0 else pts[::-1]


def _edges(ring) -> list[dict]:
    out = []
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        length = G.distance(a, b)
        if length < 0.2:
            continue
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        out.append({"i": i, "a": a, "b": b, "u": u, "n": (u[1], -u[0]), "len": length})
    return out


def _front_of(p, e) -> tuple[float, float]:
    """(distance out of the edge's line, position along it) of point ``p``."""
    rx, ry = p[0] - e["a"][0], p[1] - e["a"][1]
    return rx * e["n"][0] + ry * e["n"][1], rx * e["u"][0] + ry * e["u"][1]


def rectangle_space(anchor: Sequence[float], outline: Sequence[Sequence[float]], stated: Optional[float] = None,
                    doors: Sequence[dict] = ()) -> Optional[dict]:
    """The space a label names when no drawn strokes close it (pure; module docstring): ``{"polygon", "method",
    "area_m2", "reason"}`` or None (no facade within ``rect_reach``)."""
    from shapely.geometry import Point, Polygon

    ring = _ccw(outline)
    if len(ring) < 3:
        return None
    edges = _edges(ring)
    p = (float(anchor[0]), float(anchor[1]))
    reach = SPACE["rect_reach"]
    facing = []
    for e in edges:
        d, t = _front_of(p, e)
        if 0.05 < d <= reach and -0.5 <= t <= e["len"] + 0.5:
            facing.append((d, t, e))
    if not facing:
        return None
    lo_d, hi_d = SPACE["rect_depth"]
    building = Polygon(ring)
    rect, method = None, None
    # an inner corner: two facing edges, nearly perpendicular, whose lines meet within corner_gap of both (a pier or
    # a wall end may jog the outline there) at a reflex corner (the building on both sides behind it) with the label
    # in front of both
    front = [(d, t, e) for e in edges for d, t in [_front_of(p, e)] if 0.05 < d <= reach]
    corners = []
    for d1, t1, e1 in front:
        for d2, t2, e2 in front:
            if e1 is e2 or abs(e1["u"][0] * e2["u"][0] + e1["u"][1] * e2["u"][1]) > SPACE["corner_dot"]:
                continue
            den = e1["u"][0] * e2["u"][1] - e1["u"][1] * e2["u"][0]
            if abs(den) < 1e-9:
                continue
            rx, ry = e2["a"][0] - e1["a"][0], e2["a"][1] - e1["a"][1]
            s = (rx * e2["u"][1] - ry * e2["u"][0]) / den
            corner = (e1["a"][0] + e1["u"][0] * s, e1["a"][1] + e1["u"][1] * s)
            if G.point_segment_distance(corner, e1["a"], e1["b"]) > SPACE["corner_gap"] or \
                    G.point_segment_distance(corner, e2["a"], e2["b"]) > SPACE["corner_gap"]:
                continue
            n1, n2 = e1["n"], e2["n"]
            probes = [(corner[0] + (n2[0] - n1[0]) * 0.3, corner[1] + (n2[1] - n1[1]) * 0.3),
                      (corner[0] + (n1[0] - n2[0]) * 0.3, corner[1] + (n1[1] - n2[1]) * 0.3)]
            if not all(building.contains(Point(q)) for q in probes):
                continue
            # the rectangle from the corner out along both normals, the label at its centre
            a_len = 2.0 * d2                                  # along e2's normal (away from e2) ... = across e1
            b_len = 2.0 * d1
            if stated:
                s = math.sqrt(stated / max(a_len * b_len, 1e-6))
                a_len, b_len = a_len * s, b_len * s
            n1, n2 = e1["n"], e2["n"]
            c = corner
            pts = [c, (c[0] + n2[0] * a_len, c[1] + n2[1] * a_len),
                   (c[0] + n2[0] * a_len + n1[0] * b_len, c[1] + n2[1] * a_len + n1[1] * b_len),
                   (c[0] + n1[0] * b_len, c[1] + n1[1] * b_len)]
            cand = Polygon(pts)
            if cand.is_valid and cand.buffer(0.01).contains(Point(p)):
                corners.append((G.distance(p, corner), cand))
    if corners:
        rect, method = min(corners, key=lambda x: x[0])[1], "rectangle in the inner corner"
    if rect is None:
        d, t, e = min(facing, key=lambda x: x[0])
        depth = min(hi_d, max(lo_d, 2.0 * d))
        mine = [dr for dr in doors if abs(_front_of(dr["face"], e)[0]) <= 0.05
                and -0.2 <= _front_of(dr["face"], e)[1] <= e["len"] + 0.2]
        if stated:
            width = stated / depth
            t0 = t - width / 2.0
        elif mine:
            ts = [_front_of(dr["face"], e)[1] for dr in mine]
            ws = [float(dr.get("width") or 0.9) / 2.0 for dr in mine]
            lo = min(tt - w for tt, w in zip(ts, ws)) - 0.5
            hi = max(tt + w for tt, w in zip(ts, ws)) + 0.5
            lo, hi = min(lo, t - 1.0), max(hi, t + 1.0)
            t0, width = lo, hi - lo
        else:
            width = min(max(SPACE["rect_width"], 0.0), e["len"] + 1.0)
            t0 = t - width / 2.0
        a0 = (e["a"][0] + e["u"][0] * t0, e["a"][1] + e["u"][1] * t0)
        pts = [a0, (a0[0] + e["u"][0] * width, a0[1] + e["u"][1] * width),
               (a0[0] + e["u"][0] * width + e["n"][0] * depth, a0[1] + e["u"][1] * width + e["n"][1] * depth),
               (a0[0] + e["n"][0] * depth, a0[1] + e["n"][1] * depth)]
        rect, method = Polygon(pts), "rectangle against the facade"
    piece = rect.difference(building)
    parts = [g for g in getattr(piece, "geoms", [piece]) if g.geom_type == "Polygon" and g.area > 0.05]
    if not parts:
        return None
    keep = next((g for g in parts if g.buffer(0.01).contains(Point(p))), max(parts, key=lambda g: g.area))
    keep = keep.simplify(0.005)
    coords = [[round(x, 4), round(y, 4)] for x, y in list(keep.exterior.coords)[:-1]]
    area = round(keep.area, 3)
    return {"polygon": coords, "method": method, "area_m2": area,
            "reason": f"no drawn outline closes around the label: a {method} holding the label at its centre"
                      + (f", scaled to the stated {stated:.2f} m²" if stated else "") + f" ({area:.2f} m², inferred)"}


# --------------------------------------------------------------------------
# The drawn site symbols
# --------------------------------------------------------------------------

# (key, inferred_as) on the folded upper-case words of a symbol's layer and block names; the first hit wins (a
# planter before a plant, an axis bubble before a text, a level mark's "KOTA" before "KOT").
DECOR_WORDS: tuple[tuple[str, str], ...] = (
    ("SAKSI", "planter"), ("PLANTER", "planter"), ("JARDINIERE", "planter"), ("PFLANZKUBEL", "planter"),
    ("AGAC", "vegetation"), ("BITKI", "vegetation"), ("PEYZAJ", "vegetation"), ("CALI", "vegetation"),
    ("CICEK", "vegetation"), ("TREE", "vegetation"), ("PLANT", "vegetation"), ("LANDSCAP", "vegetation"),
    ("VEGET", "vegetation"), ("SHRUB", "vegetation"), ("BUSH", "vegetation"), ("HEDGE", "vegetation"),
    ("FOLIAGE", "vegetation"), ("BAUM", "vegetation"), ("PFLANZ", "vegetation"), ("ARBRE", "vegetation"),
    ("ARBUST", "vegetation"), ("GREEN", "vegetation"),
    ("KOLON", "column"), ("COLUMN", "column"), ("SUTUN", "column"), ("PILLAR", "column"), ("STUTZE", "column"),
    ("POTEAU", "column"),
    ("AKS", "axis_bubble"), ("AXIS", "axis_bubble"), ("GRID", "axis_bubble"), ("RASTER", "axis_bubble"),
    ("DENIZLIK", "window_sill"), ("SILL", "window_sill"), ("PARAPET", "window_sill"),
    ("KOTA", "annotation"), ("KOT", "level_mark"), ("LEVEL", "level_mark"),
    ("KAPI", "door_symbol"), ("DOOR", "door_symbol"), ("PENCERE", "window_symbol"), ("WINDOW", "window_symbol"),
    ("YAZI", "annotation"), ("TEXT", "annotation"), ("ANNO", "annotation"), ("DIM", "annotation"),
    ("OLCU", "annotation"), ("NOTE", "annotation"),
    ("KESIT", "section_mark"), ("SECTION", "section_mark"), ("KUZEY", "north_arrow"), ("NORTH", "north_arrow"),
    ("LAMBA", "lamp"), ("AYDINLATMA", "lamp"), ("LAMP", "lamp"), ("LIGHT", "lamp"), ("LUMINAIRE", "lamp"),
    ("BOLLARD", "bollard"), ("BABA", "bollard"), ("DIREK", "post"), ("POST", "post"), ("POLE", "post"),
    ("MERDIVEN", "steps"), ("BASAMAK", "steps"), ("STAIR", "steps"), ("STEP", "steps"),
    ("BALKON", "outdoor_space_detail"), ("BALCON", "outdoor_space_detail"), ("TERAS", "outdoor_space_detail"),
    ("TERRAC", "outdoor_space_detail"), ("VERANDA", "outdoor_space_detail"), ("DECK", "outdoor_space_detail"),
    ("SUNDURMA", "outdoor_space_detail"), ("PERGOLA", "outdoor_space_detail"),
    ("TARAMA", "hatch"), ("HATCH", "hatch"),
    ("DUVAR", "wall_detail"), ("WALL", "wall_detail"), ("SIVA", "wall_detail"), ("BETON", "wall_detail"),
    ("TEFRIS", "furniture"), ("MOBILYA", "furniture"), ("FURN", "furniture"),
    ("ARABA", "car"), ("CAR", "car"), ("VEHICLE", "car"),
)
DECOR_WHAT = {
    "axis_bubble": "a structural grid bubble (the axis label), drawing annotation",
    "column": "a column", "window_sill": "a window sill or coping line", "level_mark": "a level mark symbol",
    "door_symbol": "a door symbol", "window_symbol": "a window symbol", "annotation": "drawing annotation",
    "section_mark": "a section mark", "north_arrow": "the north arrow", "lamp": "an outdoor lamp",
    "bollard": "a bollard", "post": "a post", "planter": "a planter", "steps": "steps",
    "outdoor_space_detail": "a detail of an outdoor space (its edge or steps)", "hatch": "a hatch",
    "wall_detail": "a wall or plaster detail", "furniture": "a furniture symbol", "car": "a car",
    "marker": "a small marker (too small for a plant)", "unidentified": "an unidentified site symbol (lines)",
    "tree": "a tree or shrub", "hedge": "a hedge member",
}
# What the site build makes of a typed symbol (the rest is recorded, not built).
DECOR_BUILT = ("tree", "hedge")


def _entities(item: dict) -> list[str]:
    out = []
    for ev in item.get("evidence") or []:
        if isinstance(ev, dict):
            out += [x for x in str(ev.get("entity") or "").split(",") if x]
    return out


def _names(item: dict) -> list[str]:
    out = []
    for ev in item.get("evidence") or []:
        if isinstance(ev, dict):
            for key in ("layer", "block"):
                for name in str(ev.get(key) or "").split(","):
                    if name.strip():
                        out.append(name.strip())
    return out


def decor_word(item: dict) -> Optional[tuple[str, str]]:
    """``(inferred_as, name)`` of a site symbol by its layer or block names (``DECOR_WORDS``, in the table's order
    over all its names: a hatched column on "TARAMA" and "KOLON" is a column, a level mark's circle with its hatch a
    level mark), or None."""
    named = [(name, _words(name)) for name in _names(item)]
    for key, what in DECOR_WORDS:
        for name, words in named:
            if _hit(key, words):
                return what, name
    return None


def _round_symbol(item: dict) -> bool:
    size = [float(v) for v in (item.get("size") or [0, 0])[:2]]
    if min(size) <= 0:
        return False
    ents = _entities(item)
    circle = any(e.upper().startswith(("CIRCLE", "ARC")) for e in ents) or not ents
    return circle and min(size) / max(size) >= 0.8


def _axis_coords(walls: Sequence[dict]) -> tuple[list[float], list[float]]:
    xs, ys = [], []
    for w in walls or []:
        s, e = w.get("start"), w.get("end")
        if not s or not e:
            continue
        if abs(s[0] - e[0]) <= 0.01:
            xs.append(float(s[0]))
        elif abs(s[1] - e[1]) <= 0.01:
            ys.append(float(s[1]))
    return xs, ys


def type_site_decor(building: dict, outline: Sequence[Sequence[float]] = ()) -> list[dict]:
    """Types every drawn site symbol of ``building["site"]["decor"]`` (mutated; module docstring). Each untyped item
    (``kind`` other, or no ``inferred_as`` yet) gets ``drawn_kind`` (kept), ``inferred_as``, ``type_reason``,
    ``inferred: true`` and, for vegetation, ``kind: tree`` (the site build's trees and hedges). Returns the
    ``level_inference.inferred`` entries (one per kind)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    items = [d for d in site.get("decor") or [] if isinstance(d, dict)]
    if not items:
        return []
    ground = None
    levels = sorted((lv for lv in building.get("levels") or [] if isinstance(lv, dict)),
                    key=lambda lv: (lv.get("order") is None, lv.get("order") or 0))
    if levels:
        ground = levels[0].get("id")
    xs, ys = _axis_coords([w for w in building.get("walls") or [] if w.get("level_id") in (None, ground)])
    tol = SPACE["axis_tol"]
    ring = _ccw(outline) if len(outline or []) >= 3 else []
    bx = (min(p[0] for p in ring), max(p[0] for p in ring)) if ring else None
    by = (min(p[1] for p in ring), max(p[1] for p in ring)) if ring else None

    def on_axis(d) -> bool:
        cx, cy = float(d["center"][0]), float(d["center"][1])
        if bx is None:
            return False
        beyond_y = cy < by[0] - 0.3 or cy > by[1] + 0.3
        beyond_x = cx < bx[0] - 0.3 or cx > bx[1] + 0.3
        return (beyond_y and any(abs(cx - x) <= tol for x in xs)) or (beyond_x and any(abs(cy - y) <= tol for y in ys))

    todo = [d for d in items if d.get("inferred_as") is None and d.get("kind") in (None, "other")]
    round_axis = [d for d in todo if _round_symbol(d) and decor_word(d) is None and on_axis(d)]
    bubbles = {id(d) for d in round_axis} if len(round_axis) >= SPACE["axis_min"] else set()
    for d in todo:
        d.setdefault("drawn_kind", d.get("kind"))
        size = [float(v) for v in (d.get("size") or [0, 0])[:2]]
        word = decor_word(d)
        if word is not None and word[0] != "vegetation":
            what, why = word[0], f"drawn on {word[1]!r}: {DECOR_WHAT.get(word[0], word[0])}"
        elif word is not None:
            what, why = "tree", (f"drawn on {word[1]!r} (a plant layer): a tree, by the crown {max(size):.2f} m "
                                 f"(CLAUDE.md vegetation rule)")
        elif id(d) in bubbles:
            what, why = "axis_bubble", (f"a {max(size):.2f} m circle on the extension of a wall axis, one of "
                                        f"{len(bubbles)} such: a structural grid bubble, drawing annotation")
        elif _round_symbol(d) and max(size) >= SPACE["plant_min_m"]:
            what, why = "tree", (f"a single {max(size):.2f} m circle symbol outside the building that no layer or "
                                 f"block names: a tree or shrub by the crown (CLAUDE.md vegetation rule)")
        elif _round_symbol(d):
            what, why = "marker", f"a {max(size):.2f} m circle: {DECOR_WHAT['marker']}"
        else:
            what, why = "unidentified", (f"{max(size or [0]):.2f} m of lines that no layer, block or shape rule "
                                         f"types: {DECOR_WHAT['unidentified']}, not built")
        d["inferred_as"] = what
        d["inferred"] = True
        if what == "tree":
            d["kind"] = "tree"
            why += "; built by the site's vegetation (species inferred)"
        else:
            why += "; not built" if "not built" not in why else ""
        d["type_reason"] = why
    # rows of equal circles: hedges (the site build's hedges_of takes them; the record says so)
    trees = [d for d in items if d.get("inferred_as") == "tree"]
    if len(trees) >= 5:
        from wenart.blender.vegetation import hedge_rows
        for row in hedge_rows(trees):
            for sid in row["symbol_ids"]:
                d = next((x for x in trees if str(x.get("id")) == str(sid)), None)
                if d is not None:
                    d["inferred_as"] = "hedge"
                    d["type_reason"] = (f"one of {row['count']} equal circles of {row['width_m']:.2f} m in a row at a "
                                        f"pitch of {row['pitch_m']:.2f} m: a hedge (CLAUDE.md vegetation rule); built "
                                        f"by the site's vegetation")
    return decor_summary(building)


def decor_summary(building: dict) -> list[dict]:
    """The ``level_inference.inferred`` entries of the typed site symbols: one per ``inferred_as``, built or not
    (a column a space builds as its post, a space's drawn steps: ``built_by``)."""
    counts: dict = {}
    for d in (building.get("site") or {}).get("decor") or []:
        if isinstance(d, dict) and d.get("inferred_as") and d.get("type_reason"):
            counts.setdefault(d["inferred_as"], []).append(d)
    out = []
    for what, items in sorted(counts.items()):
        ids = [str(d.get("id")) for d in items]
        used = sorted({str(d["built_by"]) for d in items if d.get("built_by")})
        built = "; built" if what in DECOR_BUILT else (f"; built with {', '.join(used)}" if used else "; not built")
        out.append({"item": f"site symbols: {what}", "value": len(ids),
                    "reason": f"{len(ids)} drawn site symbol(s) typed {what} ({DECOR_WHAT.get(what, what)}{built}): "
                              f"{', '.join(ids[:8])}" + (" ..." if len(ids) > 8 else "")})
    return out


def mark_decor_used(building: dict, spaces: Sequence[dict]) -> None:
    """The site symbols the outdoor spaces build (mutated): a drawn column a space's post stands on, a detail drawn on
    the space's own layer at its edge (its steps): ``built_by`` and the reason."""
    from shapely.geometry import Point

    decor = [d for d in (building.get("site") or {}).get("decor") or [] if isinstance(d, dict)]
    for s in spaces:
        posts = {str(q.get("id")) for q in s.get("posts") or [] if q.get("id")}
        layers = set((s.get("outline") or {}).get("layers") or [])
        sp = _shp(s["polygon"])
        for d in decor:
            if str(d.get("id")) in posts and not d.get("built_by"):
                d["built_by"] = s["id"]
                d["type_reason"] = (d.get("type_reason") or "").replace("; not built", "") + \
                    f"; built as a post of the {s['kind']} {s['id']}"
            elif d.get("inferred_as") in ("outdoor_space_detail", "steps") and not d.get("built_by") and \
                    d.get("center") and sp.distance(Point(d["center"])) <= 0.6 and \
                    (not layers or layers & set(_names(d))):
                d["built_by"] = s["id"]
                d["type_reason"] = (d.get("type_reason") or "").replace("; not built", "") + \
                    f"; built with the {s['kind']} {s['id']} (its drawn steps or edge)"


def same_symbols(upper: Sequence[dict], ground: Sequence[dict], tol: float = 0.1) -> dict:
    """``{upper id: ground id}``: the symbols of an upper plan drawn at the same place and size as one of the ground
    plan's (the upper plan repeats the grid, the columns and the sills)."""
    out = {}
    for u in upper or []:
        if not isinstance(u, dict) or not u.get("center"):
            continue
        for g in ground or []:
            if not isinstance(g, dict) or not g.get("center"):
                continue
            su, sg = u.get("size") or [0, 0], g.get("size") or [0, 0]
            if G.distance(u["center"], g["center"]) <= tol and all(abs(float(a) - float(b)) <= tol
                                                                    for a, b in zip(su[:2], sg[:2])):
                out[str(u.get("id"))] = str(g.get("id"))
                break
    return out


# --------------------------------------------------------------------------
# The spaces (building frame)
# --------------------------------------------------------------------------

def _shp(poly):
    from shapely.geometry import Polygon
    p = Polygon([tuple(map(float, q)) for q in poly])
    return p if p.is_valid else p.buffer(0)


def _coords(g) -> list[list[float]]:
    if g.geom_type != "Polygon":
        g = max(getattr(g, "geoms", []), key=lambda x: x.area)
    return [[round(x, 4), round(y, 4)] for x, y in list(g.exterior.coords)[:-1]]


def space_doors(poly, level_id: str, doors: Sequence[dict]) -> list[dict]:
    """The outside doors of ``level_id`` that open onto ``poly``: their probe (``door_probe`` out of the face) lies
    on it or within ``door_reach``."""
    from shapely.geometry import Point

    sp = _shp(poly)
    out = []
    for d in doors:
        if d.get("level_id") != level_id:
            continue
        f, o = d["face"], d["outward"]
        probe = (f[0] + o[0] * SPACE["door_probe"], f[1] + o[1] * SPACE["door_probe"])
        if sp.distance(Point(probe)) <= SPACE["door_reach"]:
            out.append(d)
    return out


def _held_by(a: dict, building: dict, level_id: str) -> Optional[str]:
    """What already holds a space label: a room of its level, or a built site surface near it."""
    from shapely.geometry import Point

    p = Point(a["anchor"])
    for r in building.get("rooms") or []:
        if r.get("level_id") == level_id and len(r.get("polygon") or []) >= 3 and _shp(r["polygon"]).contains(p):
            return f"the room {r['id']}"
    site = building.get("site") or {}
    for key in ("paving", "grass", "parking", "pools"):
        for s in site.get(key) or []:
            if not isinstance(s, dict) or s.get("build") is False or len(s.get("polygon") or []) < 3:
                continue
            if s.get("area_id") and s.get("area_id") == a.get("id") and _shp(s["polygon"]).distance(p) <= \
                    SPACE["label_reach_m"]:
                return f"the {key} surface {s.get('id')}"
            if _shp(s["polygon"]).distance(p) <= 0.05:
                return f"the {key} surface {s.get('id')}"
    return None


def _columns(building: dict) -> list[dict]:
    """The drawn columns of the site symbols (``type_site_decor``: ``inferred_as`` column), one per place."""
    out = []
    for d in (building.get("site") or {}).get("decor") or []:
        if isinstance(d, dict) and d.get("inferred_as") == "column" and d.get("center"):
            if any(G.distance(c["center"], d["center"]) <= 0.1 for c in out):
                continue
            out.append(d)
    return out


def outdoor_spaces(building: dict, levels: Sequence[dict], outlines: dict, marks: Sequence[dict],
                   doors: Sequence[dict], gz, inferred: list, warnings: list) -> list[dict]:
    """``site.outdoor_spaces`` (pure apart from ``inferred`` / ``warnings``; module docstring). ``levels``: the base
    levels; ``outlines``: each level's wall outline; ``marks``: the level marks; ``doors``: the outside doors
    (``{"id", "level_id", "face", "outward", "threshold", "width"}``); ``gz(x, y)``: the ground."""
    from shapely.geometry import Point

    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    by_id = {lv["id"]: lv for lv in levels}
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    ground_lv = next((lv for lv in order if lv.get("order") == 0), None) or \
        next((lv for lv in order if float(lv["elevation"]) >= -0.5), order[0] if order else None)
    ground_id = ground_lv["id"] if ground_lv else None
    out: list[dict] = []
    seen_ids: dict = {}
    for a in site.get("areas") or []:
        if not isinstance(a, dict) or not a.get("anchor"):
            continue
        sk = space_kind(a.get("label_raw") or a.get("label"))
        if sk is None:
            continue
        if a.get("level_id") and a["level_id"] not in by_id:
            a["space"] = {"built": False, "reason": f"its level {a['level_id']} is no base level (an alternative)"}
            continue
        level_id = a.get("level_id") or ground_id
        if level_id is None:
            continue
        lv = by_id[level_id]
        held = _held_by(a, building, level_id)
        if held is not None:
            a["space"] = {"built": False, "reason": f"held by {held}"}
            continue
        st = stated_area(a)
        outline = outlines.get(level_id) or []
        poly, method, why, extra = None, None, "", {}
        if len(a.get("polygon") or []) >= 3:
            poly, method = a["polygon"], "drawn face"
            why = "the closed face the reading found around the label"
        elif isinstance(a.get("outline_inferred"), dict) and len(a["outline_inferred"].get("polygon") or []) >= 3:
            rec = a["outline_inferred"]
            poly, method, why = rec["polygon"], "strokes", rec.get("reason") or "closed from the drawn strokes"
            extra = {"layers": rec.get("layers"), "entities": rec.get("entities"), "bridges": rec.get("bridges")}
        else:
            mine = [d for d in doors if d.get("level_id") == level_id]
            rect = rectangle_space(a["anchor"], outline, st["m2"] if st else None, mine)
            if rect is not None:
                poly, method, why = rect["polygon"], rect["method"], rect["reason"]
        if poly is None:
            warnings.append(f"outdoor space {a.get('id')} ({a.get('label')}): no drawn outline and no facade within "
                            f"{SPACE['rect_reach']:g} m of the label: not built (to review)")
            a["space"] = {"built": False, "reason": "no outline and no facade near the label"}
            continue
        sp = _shp(poly)
        # the building cut out where the outline overlaps it (a rectangle; a drawn face that reaches into the walls)
        if len(outline) >= 3 and sp.intersection(_shp(outline)).area > SPACE["overlap_m2"]:
            rest = sp.difference(_shp(outline))
            if not rest.is_empty and rest.area > 0.05:
                parts = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "Polygon"]
                sp = next((g for g in parts if g.buffer(0.01).contains(Point(a["anchor"]))),
                          max(parts, key=lambda g: g.area))
        poly = _coords(sp)
        area = round(sp.area, 3)
        on = space_doors(poly, level_id, doors)
        # the floor: a level mark inside, else the doors' thresholds, else the level's floor
        inside = [m for m in marks if m.get("level_id") in (None, level_id) and m.get("point") is not None
                  and m.get("z") is not None and m.get("kind") in ("threshold", "floor", "entrance")
                  and sp.distance(Point(m["point"])) <= SPACE["mark_reach"]]
        if inside:
            z = sum(float(m["z"]) for m in inside) / len(inside)
            z_src = f"the level mark(s) {', '.join(str(m.get('raw') or m['id']) for m in inside)} inside it"
        elif on:
            zs = sorted(float(d["threshold"]) for d in on)
            z = zs[len(zs) // 2]
            z_src = f"the threshold of the door(s) {', '.join(d['id'] for d in on)} that open onto it"
        else:
            z = float(lv["elevation"])
            z_src = f"the floor of {level_id} (no door or level mark on it)"
        z = round(z, 3)
        on = [d for d in on if abs(float(d["threshold"]) - z) <= SPACE["door_level_tol"] + 1e-9]
        samples = [tuple(q) for q in poly] + [sp.representative_point().coords[0]]
        gzs = [gz(x, y) for x, y in samples]
        g = {"min": round(min(gzs), 3), "mean": round(sum(gzs) / len(gzs), 3), "max": round(max(gzs), 3)}
        # an upper floor's space high over the ground is a slab with a guard; a ground-floor space over a slope keeps
        # its base (retaining walls, stepped bands, a railing over a drop: the platform rules)
        upper = ground_lv is not None and float(lv["elevation"]) > float(ground_lv["elevation"]) + 0.5
        elevated = upper and z - g["min"] > SPACE["elevated_min"]
        base = str(a.get("id") or f"sa_{level_id}_{B.slugify(a.get('label') or 'space')}").replace("sa_", "os_", 1)
        seen_ids[base] = seen_ids.get(base, 0) + 1
        sid = base if seen_ids[base] == 1 else f"{base}_{seen_ids[base]}"
        if seen_ids[base] == 2:                         # the first of a repeated id gets its number too
            first = next(s for s in out if s["id"] == base)
            first["id"] = f"{base}_1"
        ev = [dict(e) for e in a.get("evidence") or [] if isinstance(e, dict)][:3]
        ev.append({"file": (ev[0].get("file") if ev else "") or "", "method": "inferred", "confidence": 0.6,
                   "rule": "outdoor_space", "text": f"{method}: {why}"})
        rec = {"id": sid, "area_id": a.get("id"), "label": a.get("label"), "kind": sk["kind"], "cover": sk["cover"],
               "word": sk["word"], "level_id": level_id, "polygon": poly, "area_m2": area,
               "stated_area_m2": st["m2"] if st else None, "stated_text": st["text"] if st else None,
               "method": method, "z": z, "z_source": z_src, "ground": g, "elevated": elevated,
               "doors": [d["id"] for d in on], "steps": None, "columns": [], "roof": None, "inferred": True,
               "evidence": ev, **({"outline": extra} if extra else {})}
        drawn = (a.get("outline_inferred") or {}).get("steps") if method == "strokes" else None
        if drawn and not elevated:
            rec["steps"] = dict(drawn, source="drawn")
        out.append(rec)
        a["space"] = {"built": True, "id": sid}
    if not out:
        return out
    cols = _columns(building)
    for s in out:
        sp = _shp(s["polygon"])
        s["columns"] = [{"id": c.get("id"),
                         "center": [round(float(c["center"][0]), 4), round(float(c["center"][1]), 4)],
                         "size_m": round(max(float(v) for v in (c.get("size") or [0.3, 0.3])[:2]), 3)}
                        for c in cols if sp.distance(Point(c["center"])) <= SPACE["column_reach"]]
    for s in out:
        s["roof"] = roof_plan(s, out, levels, outlines, building, doors)
    assign_posts(out, gz)
    for s in out:
        sz = f"{s['area_m2']:.2f} m²" + (f" (stated {s['stated_area_m2']:.2f} m²)" if s["stated_area_m2"] else "")
        what = (f"{s['kind']} '{s['label']}' on {s['level_id']}: {sz}, {s['method']}; floor {s['z']:+.2f} m "
                f"({s['z_source']})"
                + (f"; doors {', '.join(s['doors'])} open onto it (it is their landing)" if s["doors"] else
                   "; no door opens onto it")
                + ("; a slab with a guard on its open edges" if s["elevated"] else
                   f"; its edge and steps down to the ground {s['ground']['min']:+.2f} m"
                   + (" (the drawn steps)" if s.get("steps") else "")
                   if s["z"] - s["ground"]["min"] > SPACE["flush_m"] else
                   f"; at most {s['z'] - s['ground']['min']:.2f} m over the garden (reached from it)")
                + (f"; {s['roof']['kind'].replace('_', ' ')} over {s['roof']['area_m2']:.2f} m², top "
                   f"{s['roof']['top_z']:+.2f} m" if s.get("roof") else "")
                + (f"; {len(s['posts'])} post(s) ({sum(1 for q in s['posts'] if q['source'] == 'drawn')} drawn "
                   f"column(s))" if s.get("posts") else "")
                + " (inferred)")
        s["reason"] = what
        inferred.append({"item": f"outdoor space {s['id']}", "value": s["polygon"], "reason": what})
    return out


def assign_posts(spaces: Sequence[dict], gz) -> None:
    """Every space's ``posts`` (mutated): its roof's posts, and the drawn columns under the slab of a space above
    (real06: the two columns at the veranda's front edge carry the balcony over it), each built once by the lowest
    space it stands on (else by the space above it, from the ground): ``{"center", "size_m", "source", "id", "z0",
    "z1", "carries"}``."""
    from shapely.geometry import Point

    for s in spaces:
        s["posts"] = [dict(q) for q in (s.get("roof") or {}).get("posts") or []]
    for up in sorted(spaces, key=lambda s: float(s["z"])):
        poly = _shp(up["polygon"]).buffer(SPACE["column_reach"])
        under = round(float(up["z"]) - SPACE["slab_t"], 3)
        for c in up.get("columns") or []:
            if not poly.contains(Point(c["center"])):
                continue
            have = next((q for s in spaces for q in s["posts"] if G.distance(q["center"], c["center"]) <= 0.1), None)
            if have is not None:
                if have["z1"] > under > have["z0"]:
                    have["z1"] = under
                    have["carries"] = f"the slab of {up['id']}"
                continue
            low = [s for s in spaces if s is not up and float(s["z"]) < float(up["z"]) - 1.0
                   and _shp(s["polygon"]).buffer(SPACE["column_reach"]).contains(Point(c["center"]))]
            owner = min(low, key=lambda s: float(s["z"])) if low else up
            z0 = float(owner["z"]) if low else gz(*c["center"])
            if under - z0 < 1.0:
                continue
            owner["posts"].append({"center": list(c["center"]), "size_m": c["size_m"], "source": "drawn",
                                   "id": c["id"], "z0": round(z0, 3), "z1": under,
                                   "carries": f"the slab of {up['id']}"})


def roof_plan(space: dict, spaces: Sequence[dict], levels: Sequence[dict], outlines: dict, building: dict,
              doors: Sequence[dict] = ()) -> Optional[dict]:
    """The cover of a space (pure; module docstring): ``{"kind": light_roof | glass_roof | pergola, "polygon",
    "area_m2", "top_z", "thickness", "fall", "posts": [{"center", "size_m", "source", "id", "z0", "z1"}],
    "reason"}`` or None (an open kind, or the floors and spaces above cover it all)."""
    cover = space.get("cover")
    if cover not in ("roof", "glass", "pergola", "building"):
        return None
    from shapely.geometry import Point
    from shapely.ops import unary_union

    z = float(space["z"])
    sp = _shp(space["polygon"])
    lv = next((x for x in levels if x["id"] == space["level_id"]), None)
    above_lvls = sorted((x for x in levels if float(x["elevation"]) > z + 1.0), key=lambda x: float(x["elevation"]))
    covers = [_shp(outlines[x["id"]]) for x in above_lvls if len(outlines.get(x["id"]) or []) >= 3]
    upper = [s for s in spaces if s is not space and float(s["z"]) > z + 1.0]
    covers += [_shp(s["polygon"]) for s in upper]
    rest = sp.difference(unary_union(covers)) if covers else sp
    parts = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "Polygon" and g.area >= 0.5]
    if not parts:
        return None
    region = max(parts, key=lambda g: g.area)
    if cover == "building" and region.area < 0.5:
        return None
    kind = {"roof": "light_roof", "glass": "glass_roof", "pergola": "pergola", "building": "light_roof"}[cover]
    nxt = above_lvls[0] if above_lvls else None
    own = _shp(outlines.get(space["level_id"]) or []) if len(outlines.get(space["level_id"]) or []) >= 3 else None
    if nxt is not None:
        top = float(nxt["elevation"])
        why = f"its top at the floor line of {nxt['id']} ({top:+.2f} m)"
    else:
        h = float((lv or {}).get("ceiling_height") or 2.8)
        top = float((lv or {}).get("elevation") or z) + h + SPACE["eaves_extra"]
        why = f"its top at the eaves of {space['level_id']} ({top:+.2f} m)"
    # kept under the windows above it (a sill within 0.5 m of the roof)
    sills = []
    for o in building.get("openings") or []:
        if o.get("type") != "window" or o.get("level_id") == space["level_id"] or not o.get("center"):
            continue
        olv = next((x for x in levels if x["id"] == o.get("level_id")), None)
        if olv is None or float(olv["elevation"]) <= z + 1.0:
            continue
        if region.distance(Point(o["center"])) <= 0.5:
            sills.append(float(olv["elevation"]) + float(o.get("sill_height") or 0.9))
    if sills and min(sills) - SPACE["sill_gap"] < top:
        top = min(sills) - SPACE["sill_gap"]
        why += f", lowered under the window sill above ({min(sills):+.2f} m)"
    t = SPACE["roof_t"]
    fall = SPACE["roof_fall"]
    # the fall: away from the building (its walls and the floors above) towards the open side, so the rain runs off
    # the free edge (CLAUDE.md Q8)
    from shapely.ops import nearest_points
    walls = [g for g in ([own] if own is not None else []) + covers[:len(covers) - len(upper)]
             if g is not None and not g.is_empty]
    c0 = region.centroid
    fx, fy = 0.0, -1.0
    if walls:
        near = nearest_points(unary_union(walls), c0)[0]
        dx, dy = c0.x - near.x, c0.y - near.y
        if math.hypot(dx, dy) > 1e-6:
            fx, fy = dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    ring = _ccw(_coords(region))
    origin = min(ring, key=lambda p: p[0] * fx + p[1] * fy)
    plane = {"origin": [round(origin[0], 4), round(origin[1], 4)], "dir": [round(fx, 6), round(fy, 6)]}
    low = min(top - fall * max(0.0, (p[0] - origin[0]) * fx + (p[1] - origin[1]) * fy) for p in ring)
    if low - t - z < SPACE["min_clear"]:
        top += z + SPACE["min_clear"] + t - low
        why += f" (raised to a {SPACE['min_clear']:.1f} m clear height at its low edge)"

    def top_at(p) -> float:
        return top - fall * max(0.0, (p[0] - origin[0]) * fx + (p[1] - origin[1]) * fy)

    # supports: the building, the drawn columns, the slab above's edge
    support = [g for g in ([own] if own is not None else []) + covers if g is not None and not g.is_empty]
    posts = []
    for c in space.get("columns") or []:
        if region.buffer(SPACE["column_reach"]).contains(Point(c["center"])):
            posts.append({"center": list(c["center"]), "size_m": c["size_m"], "source": "drawn", "id": c["id"]})
    # 27 Oct 2026 (real06: a 0.15 m square stick stood beside the veranda's drawn 0.53 m round column; Argus O6): an
    # inferred post takes the shape and the size of the space's drawn columns (their median), one post language
    post_size, post_shape = post_look(space.get("columns") or [])
    ring = _ccw(_coords(region))
    for p in ring:
        pt = Point(p)
        if any(g.distance(pt) <= SPACE["post_reach"] for g in support):
            continue
        if any(G.distance(p, q["center"]) <= SPACE["post_reach"] for q in posts):
            continue
        inset = post_size / 2.0 + 0.02
        cx, cy = region.centroid.x, region.centroid.y
        d = G.distance(p, (cx, cy)) or 1.0
        c = (p[0] + (cx - p[0]) / d * inset, p[1] + (cy - p[1]) / d * inset)
        posts.append({"center": [round(c[0], 4), round(c[1], 4)], "size_m": post_size, "source": "inferred",
                      "id": None, "shape": post_shape})
    # long open edges: posts at most post_span apart
    for a, b in zip(ring, ring[1:] + ring[:1]):
        length = G.distance(a, b)
        mid = G.segment_midpoint(a, b)
        if length <= SPACE["post_span"] or any(g.distance(Point(mid)) <= 0.3 for g in support):
            continue
        k = int(math.ceil(length / SPACE["post_span"]))
        for j in range(1, k):
            q = G.point_along_segment(a, b, j / k)
            if any(G.distance(q, x["center"]) <= SPACE["post_span"] / 2.0 for x in posts):
                continue
            posts.append({"center": [round(q[0], 4), round(q[1], 4)], "size_m": post_size,
                          "source": "inferred", "id": None, "shape": post_shape})
    for q in posts:
        q["z0"] = round(z, 3)
        q["z1"] = round(top_at(q["center"]) - t, 3)
        q["carries"] = f"the roof of {space['id']}"
    # the open edges (no wall, floor or slab above within 0.3 m) carry a beam under the roof's edge
    open_edges = [[list(a), list(b)] for a, b in zip(ring, ring[1:] + ring[:1])
                  if not any(g.distance(Point(G.segment_midpoint(a, b))) <= 0.3 for g in support)]
    n_in = sum(1 for q in posts if q["source"] == "inferred")
    reason = (f"{kind.replace('_', ' ')} over {region.area:.2f} m² of the {space['kind']} (the part no floor or "
              f"space above covers), {why}, {t:.2f} m thick, falling {fall * 100:.0f} % away from the building; "
              f"{len(posts) - n_in} drawn column(s)" + (f" and {n_in} inferred post(s)" if n_in else "")
              + " (inferred)")
    return {"kind": kind, "polygon": [[round(x, 4), round(y, 4)] for x, y in ring], "area_m2": round(region.area, 3),
            "top_z": round(top, 3), "thickness": t, "fall": fall, "plane": plane, "open_edges": open_edges,
            "posts": posts, "reason": reason, "inferred": True}


def post_look(columns: list) -> tuple[float, str]:
    """The size and shape of a space's inferred posts (pure; 27 Oct 2026): the median size of its drawn columns and
    ``round`` (a drawn column of 0.2 m or more is built round, ``site.cover_parts``), else ``SPACE["post_size"]``
    ``square``."""
    sizes = sorted(float(c["size_m"]) for c in columns if isinstance(c.get("size_m"), (int, float)))
    if not sizes:
        return SPACE["post_size"], "square"
    mid = sizes[len(sizes) // 2] if len(sizes) % 2 else (sizes[len(sizes) // 2 - 1] + sizes[len(sizes) // 2]) / 2.0
    return round(mid, 3), "round" if mid >= 0.2 else "square"
