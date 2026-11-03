"""Voids a plan draws over the floor below (3 Nov 2026).

What: ``read_voids(texts, strokes)`` -> ``[{"label", "anchor", "polygon", "area_m2", "layers", "entities",
"bridges", "reason"}]`` (page metres): every text whose words mean a void over the floor below
(``building.is_void_label``: Turkish galeri, galeri boşluğu, boşluk; void, open to below, double height, Luftraum, vide,
vacío, vuoto) with the smallest outline the drawn strokes close around it (``levels.outdoor._faces``, free ends bridged
up to ``VOID_GAP_M``), ``VOID_AREA_M2`` large; two labels of one outline give one void.

Why: real09 (user: "each duplex flat has its inner stair (winders 1-17) and a 'galeri' void over the floor below"): the
attic plan writes 'galeri' in two drawn boxes of each flat's hall, beside the inner stair and between its arms (1.10 x
1.35 m and 1.60 x 1.65 m); the reading built a floor over them. A void is no room of its own: it is an outline inside
a room (or the whole room) with no floor.

How: the core keeps the voids with the level's site data (``site["voids"]``, shifted into the building frame with
it); the pipeline hands them to the slab builder (``sheets.to_building.void_openings``): each is an opening of the
floor slab of its level (kind ``void``, source ``drawn``), cut out of the floor and the ceiling below, with guards on
its free edges (the build's floor-opening rules).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import building as B

VOID_REACH_M = 4.0              # strokes within this of the label
VOID_AREA_M2 = (0.5, 80.0)      # a void this large (a stair's eye to a double-height living room)
VOID_GAP_M = 0.5                # free stroke ends bridged up to this
VOID_SAME_IOU = 0.8             # two labels whose outlines overlap this much: one void
VOID_ROOM_SHARE = 0.8           # a void covering less of its face than this is part of a room: its label names no room


def _iou(a, b) -> float:
    u = a.union(b).area
    return a.intersection(b).area / u if u > 0 else 0.0


def read_voids(texts: list, strokes: list) -> list[dict]:
    """The voids of a page (the module docstring); ``texts``: ``TextRun``s and ``strokes``: ``Stroke``s in page
    metres (pure)."""
    from shapely.geometry import LineString, Point, Polygon

    from wenart.levels import outdoor as OD

    labels = [t for t in texts or [] if B.is_void_label(getattr(t, "text", None))]
    if not labels:
        return []
    lines = [{"id": st.id, "pts": [tuple(p) for p in st.pts], "layer": st.layer, "closed": st.closed}
             for st in strokes or [] if st.pts and len(st.pts) >= 2 and not OD.layer_skipped(st.layer)]
    out: list[dict] = []
    shapes: list = []
    for t in labels:
        anchor = ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0)
        pt = Point(anchor)
        near = [s for s in lines if LineString(s["pts"]).distance(pt) <= VOID_REACH_M]
        faces = [f for f in OD._faces(anchor, near, None, VOID_GAP_M)
                 if VOID_AREA_M2[0] <= f["polygon"].area <= VOID_AREA_M2[1]] if near else []
        if not faces:
            out.append({"label": t.text, "anchor": [round(anchor[0], 4), round(anchor[1], 4)], "polygon": None,
                        "entity": t.id, "reason": f"no drawn outline of {VOID_AREA_M2[0]}-{VOID_AREA_M2[1]:.0f} m2 "
                                                  f"closes around the label: no void built"})
            continue
        f = min(faces, key=lambda f: f["polygon"].area)
        crossed = False
        ring = list(f["polygon"].simplify(0.01).exterior.coords)
        main = _main_angle(near)
        if any(math.dist(a, b) >= 0.3 and not _on_axes({"pts": [a, b]}, main) for a, b in zip(ring[:-1], ring[1:])):
            # 3 Nov 2026 (real07's GALERİ: a box with its diagonals drawn, the usual mark of an opening in a floor):
            # the label stands in a triangle of the cross (an outline with an edge askew to the drawing's main
            # directions); without the lines askew to those directions the box closes
            square = [s for s in near if _on_axes(s, main)]
            faces2 = [g for g in OD._faces(anchor, square, None, VOID_GAP_M)
                      if VOID_AREA_M2[0] <= g["polygon"].area <= VOID_AREA_M2[1]] if square else []
            if faces2:
                f, near, crossed = min(faces2, key=lambda g: g["polygon"].area), square, True
        poly = f["polygon"].buffer(-0.002, join_style=2).buffer(0.002, join_style=2)
        if poly.geom_type != "Polygon":
            poly = max(getattr(poly, "geoms", [f["polygon"]]), key=lambda g: g.area)
        poly = poly.simplify(0.005)
        if any(_iou(poly, other) >= VOID_SAME_IOU for other in shapes):
            continue                                           # a second label of the same void
        shapes.append(poly)
        layers = sorted({str(s.get("layer") or "") for s in near if s["id"] in f["ids"]})
        bridges = [round(b[2], 3) for b in f["bridges"]]
        out.append({"label": t.text, "anchor": [round(anchor[0], 4), round(anchor[1], 4)],
                    "polygon": [[round(x, 4), round(y, 4)] for x, y in list(Polygon(poly).exterior.coords)[:-1]],
                    "area_m2": round(poly.area, 3), "layers": layers, "entities": list(f["ids"])[:40],
                    "entity": t.id, "bridges": bridges,
                    "reason": f"the label '{t.text}' means a void over the floor below; its outline is closed from "
                              f"{len(f['ids'])} drawn stroke(s) on {', '.join(repr(x) for x in layers[:3])}"
                              + (f" ({len(bridges)} gap(s) of up to {max(bridges):.2f} m bridged)" if bridges
                                 else "") + ("; the diagonals marking it left out" if crossed else "")
                              + f": {poly.area:.2f} m2"})
    return out


def _angles(st: dict) -> list[tuple[float, float]]:
    pts = st["pts"]
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.dist(a, b)
        if L > 1e-6:
            out.append((math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0, L))
    return out


def _main_angle(strokes: list) -> float:
    """The drawing's main direction near the label (degrees modulo 90): the length-weighted mode in 2 degree bins."""
    bins: dict = {}
    for st in strokes:
        for ang, L in _angles(st):
            k = int(round(ang / 2.0)) % 45
            bins[k] = bins.get(k, 0.0) + L
    return 2.0 * max(bins, key=bins.get) if bins else 0.0


def _on_axes(st: dict, main: float, tol: float = 3.0) -> bool:
    """Every segment of the stroke runs along the main direction or across it (within ``tol`` degrees)."""
    for ang, _L in _angles(st):
        d = abs(ang - main) % 90.0
        if min(d, 90.0 - d) > tol:
            return False
    return True


def room_labels(blocks: list, voids: Optional[list], faces: list) -> tuple[list, list[str]]:
    """``(blocks, notes)``: the label blocks without the void labels whose drawn outline (``read_voids``) covers less
    than ``VOID_ROOM_SHARE`` of the face they stand in: that void is part of a room (real09's attic hall: the
    'galeri' boxes beside the inner stair and between its arms; the hall around them keeps its floor and is no
    'galeri'). A void label without an outline, or one whose outline is its whole face, stays the room's label (pure)."""
    from shapely.geometry import Point, Polygon

    shapes = [(v, Polygon(v["polygon"])) for v in voids or [] if v.get("polygon")]
    if not shapes:
        return blocks, []
    kept, notes = [], []
    for b in blocks:
        if not B.is_void_label(getattr(b, "name", None)):
            kept.append(b)
            continue
        pt = Point(b.anchor)
        own = next((poly for v, poly in shapes if poly.buffer(0.05).contains(pt)), None)
        face = next((f for f in faces if f.contains(pt)), None)
        if own is None or face is None or own.area >= VOID_ROOM_SHARE * face.area:
            kept.append(b)
            continue
        notes.append(f"the void label '{b.name}' stands in a drawn outline of {own.area:.2f} m2 inside a face of "
                     f"{face.area:.2f} m2: a void in that room, not the room's name")
    return kept, notes


def shift(voids: Optional[list], p) -> None:
    """Moves the voids with the page's origin step (``p``: a point map)."""
    for v in voids or []:
        if v.get("polygon"):
            v["polygon"] = [[round(q[0], 4), round(q[1], 4)] for q in (p(tuple(xy)) for xy in v["polygon"])]
        if v.get("anchor"):
            q = p(tuple(v["anchor"]))
            v["anchor"] = [round(q[0], 4), round(q[1], 4)]
