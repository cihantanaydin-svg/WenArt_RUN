"""A roof outline drawn on the top plan, or the sheet's frame? (20 Nov 2026; audit rule R13 of the building-sense audit:
"a sheet frame or title block is never a roof"; pre-pod review R20-01 / BP-03: real20's double sheet border on layer
ROL_CEPHE, 1.15-2.15 m off the walls and holding '3406 PARSEL', 'AHMET KAYA CADDESİ' and the area table, was read as a
mansard roof and turned the inferred top storey into an attic).

What: ``reject(top, mpu, outline_ent, opoly, inner) -> Optional[str]``: why a closed outline that encloses the whole
top plan is no roof outline, or None. It is no roof when

- an edge stands more than ``MAX_OVERHANG_M`` (about 1.5 m) off the plan's walls (the outline of the plan's strokes,
  the candidate and the loops inside it left out); or
- the ring between the outline and the walls holds a street, parcel, area-table or title text (a frame holds the
  sheet's texts; an eaves loop holds at most an eaves word, a slope or a mark).

``break_inside(...)``: a mansard break line (a closed loop inside the outline) is one only when it lies inside the walls,
or at most at their outer face (``BREAK_OUT_M``); a 'break' outside the walls is no mansard.

How: pure geometry on the sheets region (source units); no project data.
"""
from __future__ import annotations

import re
from typing import Optional

from shapely.geometry import Point, Polygon

MAX_OVERHANG_M = 1.5            # a roof's eaves stand at most about this far off the top storey's outer walls
SAMPLE_M = 0.5                  # the outline is probed every this far
BREAK_OUT_M = 0.30              # a break line may stand this far out of the wall outline (the wall face)
FRAME_TEXT_RE = re.compile(
    r"(?<![a-z])(?:cadde\w*|cad|sokag\w*|sokak\w*|sok|sk|yanyol\w*|bulvar\w*|parsel\w*|ada|pafta\w*|oturum\w*|"
    r"normal|brut|toplam|olcek\w*|street|road|avenue|parcel|plot|scale|m2|m²)(?![a-z])")


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def _walls(top, mpu: float, skip: set):
    """The plan's outline (``register.outline``) without the candidate loops."""
    from wenart.sheets import register as RG

    return RG.outline(top, mpu, set(skip) | RG.cut_line_entities(top))


def reject(top, mpu: float, outline_ent, opoly: Polygon, inner: list, walls=None) -> Optional[str]:
    """Why the closed outline ``outline_ent`` (``opoly``) around the top plan is no roof outline, or None (the module
    docstring). ``inner``: the entities of the closed loops inside it."""
    walls = walls if walls is not None else _walls(top, mpu, {outline_ent.id} | {e.id for e in inner})
    if walls is None or walls.is_empty:
        return None
    ring = opoly.exterior
    n = max(8, int(ring.length * mpu / SAMPLE_M))
    far = max(walls.distance(ring.interpolate(k / n, normalized=True)) for k in range(n)) * mpu
    if far > MAX_OVERHANG_M + 1e-6:
        return (f"the closed outline {outline_ent.id} around the top plan stands up to {far:.2f} m off the plan's walls "
                f"(a roof's eaves at most about {MAX_OVERHANG_M:.1f} m): no roof outline (R13: a sheet frame)")
    inside = walls.buffer(0.3 / mpu)
    texts = []
    for t in getattr(top, "texts", None) or []:
        p = getattr(t, "point", None)
        if p is None:
            continue
        q = Point(p[0], p[1])
        if opoly.contains(q) and not inside.contains(q) and FRAME_TEXT_RE.search(_fold(getattr(t, "text", ""))):
            texts.append(str(t.text))
    if texts:
        return (f"the ring between the closed outline {outline_ent.id} and the plan's walls holds the sheet's texts "
                f"({', '.join(repr(x) for x in texts[:4])}): a sheet frame, no roof outline (R13)")
    return None


def break_inside(top, mpu: float, outline_ent, inner_ent, inner_poly: Polygon, walls=None) -> bool:
    """Whether a closed loop inside the roof outline lies inside the walls (at most at their outer face)."""
    walls = walls if walls is not None else _walls(top, mpu, {outline_ent.id, inner_ent.id})
    if walls is None or walls.is_empty:
        return True
    return walls.buffer(BREAK_OUT_M / mpu).contains(inner_poly)
