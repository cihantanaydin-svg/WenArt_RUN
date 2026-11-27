"""An upper floor that reaches past the walls under it must stand on something (27 Nov 2026, audit fix round 5b).

What: ``check(b)`` runs at the end of the reading (``apply(build)`` from ``wenart.ingest.pipeline.run_project``). An
outdoor floor of an upper level (a balcony, a terrace, a deck: ``site.outdoor_spaces``; never a canopy, porch roof or
pergola) that reaches more than
``CANTILEVER_M`` past the outline of the level under it needs drawn walls or columns under that part; without them it is
checked against the drawings:

- an outline no line draws (inferred around its label: "no drawn outline closes around the label") is not built when
  the drawn roof (the roof's outline, the roof plan's other roofs) covers most of its part over the floor below (the
  plan above draws a roof there, no terrace); else it keeps only its part over the floor below and within
  ``CANTILEVER_M`` of its walls (a terrace on the lower roof, a cantilever), and nothing when no such part is left;
- a drawn outline, or an inferred one whose area the drawing writes beside its label, is kept and listed (a
  cantilever that needs columns the drawings do not show).

Every decision is a warning and a record (``level_inference.upper_support``).

Why: real15's first-floor 'TERAS' had no drawn outline; a 204 m2 rectangle was inferred around the label, 119 m2 of it
up to 5.5 m past the ground floor's walls with nothing under it, and its part over the ground floor stood under the roof
plan's drawn roof: the exteriors showed a big floating slab and the top-down view white plates on the ground.

How: pure geometry (shapely) on the building JSON; no AI.
"""
from __future__ import annotations

import re
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

CANTILEVER_M = 2.0           # an upper floor may reach this far past the walls under it without drawn supports
REACH_TOL_M = 0.25           # ... and this much more before it is checked (an inferred outline's tolerance)
STACK_SANITY_M = 6.0         # a space this far past the walls below: the levels do not stack as read (not checked)
ROOF_COVER_SHARE = 0.5       # the drawn roof covers this share of the part over the floor below: no terrace there
MIN_KEEP_M2 = 1.0            # a part over the floor below smaller than this keeps no terrace
SUPPORT_TYPES = ("column", "pillar", "pier", "post")
WALKABLE_KINDS = ("balcony", "terrace", "deck")   # the upper floors people stand on (a canopy or porch roof is none)
UNDRAWN_WORDS = ("no drawn outline", "rectangle in the inner corner")


def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    p = Polygon(points)
    p = p if p.is_valid else p.buffer(0)
    return p if not p.is_empty and p.area > 0 else None


AREA_TEXT_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*m\s*(?:2|²)", re.I)
AREA_MATCH_SHARE = 0.05      # a written area this close to the outline's area gives the outline's size


def drawn(space: dict) -> bool:
    """False when the space's outline was inferred with no drawn line around its label (pure). An inferred outline whose
    area the drawing writes beside its label ('A:12.30m²', within ``AREA_MATCH_SHARE``) is sized by the drawing: it
    counts as drawn (kept, listed)."""
    texts = [str((e or {}).get("text") or (e or {}).get("reason") or "") for e in space.get("evidence") or []]
    if not any(w in t.lower() for t in texts for w in UNDRAWN_WORDS):
        return True
    poly = _poly(space.get("polygon"))
    for t in texts:
        if any(w in t.lower() for w in UNDRAWN_WORDS):
            continue                                   # the inference's own note, not a text of the drawing
        for m in AREA_TEXT_RE.finditer(t):
            try:
                v = float(m.group(1).replace(",", "."))
            except ValueError:
                continue
            if poly is not None and v > 0 and abs(poly.area - v) <= AREA_MATCH_SHARE * v:
                return True
    return False


def _supports(b: dict, below_id: str, part) -> list:
    """The walls and columns of the level under ``part`` (its ids)."""
    inner = part.buffer(-0.05)
    if inner.is_empty:
        return []
    out = []
    for w in b.get("walls") or []:
        if w.get("level_id") != below_id or not w.get("start") or not w.get("end"):
            continue
        if LineString([w["start"][:2], w["end"][:2]]).intersects(inner):
            out.append(w["id"])
    for f in b.get("furniture") or []:
        c = (f.get("footprint") or {}).get("center")
        if f.get("level_id") == below_id and str(f.get("type") or "") in SUPPORT_TYPES and c is not None \
                and inner.contains(Point(c[:2])):
            out.append(f["id"])
    return out


def _roof_polys(b: dict) -> list:
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else None
    if roof is None or roof.get("type") in (None, "flat"):
        return []
    polys = [p for p in [_poly(roof.get("outline"))] if p is not None]
    for o in (roof.get("roof_plan_outline") or {}).get("others") or []:
        p = _poly(o.get("points"))
        if p is not None:
            polys.append(p)
    return polys


def check(b: dict) -> list:
    """The upper outdoor spaces past the walls under them (module docstring; changes ``b`` in place). Returns the
    records ``{"space", "level_id", "below", "reach_m", "past_m2", "action", "reason"}``."""
    from wenart.levels import model as LMO
    site = b.get("site") if isinstance(b.get("site"), dict) else None
    if not site or not site.get("outdoor_spaces"):
        return []
    levels = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                    key=lambda lv: float(lv.get("elevation") or 0.0))
    below_of = {lv["id"]: levels[i - 1]["id"] for i, lv in enumerate(levels) if i > 0}
    outlines: dict = {}
    roofs = _roof_polys(b)
    out, gone = [], set()
    for sp in site["outdoor_spaces"]:
        if str(sp.get("kind") or "") not in WALKABLE_KINDS:
            continue                                   # a canopy, a porch roof or a pergola is no floor to stand on
        lid = sp.get("level_id")
        below = below_of.get(lid)
        poly = _poly(sp.get("polygon"))
        if below is None or poly is None:
            continue
        if below not in outlines:
            outlines[below] = _poly(LMO.level_outline(b, below))
        under = outlines[below]
        if under is None:
            continue
        past = poly.difference(under)
        if past.area < 0.5:
            continue
        reach = max((under.exterior.distance(Point(c)) for g in getattr(past, "geoms", [past])
                     for c in g.exterior.coords), default=0.0)
        if reach <= CANTILEVER_M + REACH_TOL_M:
            continue
        if reach > STACK_SANITY_M:
            out.append({"space": sp.get("id"), "level_id": lid, "below": below, "reach_m": round(reach, 2),
                        "past_m2": round(past.area, 2), "area_m2": round(poly.area, 2), "action": "not_checked",
                        "reason": f"{sp.get('id')} ({sp.get('label')}) of {lid} stands {reach:.1f} m past the walls of "
                                  f"{below}: the two levels do not stack as read (a reading problem, not a cantilever); "
                                  f"not checked, kept as read (listed)"})
            continue
        sup = _supports(b, below, past)
        if sup:
            continue
        rec = {"space": sp.get("id"), "level_id": lid, "below": below, "reach_m": round(reach, 2),
               "past_m2": round(past.area, 2), "area_m2": round(poly.area, 2)}
        if drawn(sp):
            rec["action"] = "kept"
            rec["reason"] = (f"{sp.get('id')} ({sp.get('label')}) of {lid} reaches {reach:.2f} m past the walls of "
                             f"{below} ({past.area:.1f} m2 past them) with no wall or column drawn under it: kept as "
                             f"drawn, a cantilever over {CANTILEVER_M:.1f} m that needs supports the drawings do not "
                             f"show (listed)")
            out.append(rec)
            continue
        over = poly.intersection(under)
        covered = sum(over.intersection(r).area for r in roofs) if roofs and not over.is_empty else 0.0
        covered = min(covered, over.area)
        head = (f"{sp.get('id')} ({sp.get('label')}) of {lid} has no drawn outline (inferred around its label, "
                f"{poly.area:.1f} m2) and reaches {reach:.2f} m past the walls of {below} with nothing drawn under it")
        keep = None
        if not over.is_empty and over.area >= MIN_KEEP_M2 and covered >= ROOF_COVER_SHARE * over.area:
            why = (f"the drawn roof covers {covered:.1f} of its {over.area:.1f} m2 over {below}: the plan above draws a "
                   f"roof there, no terrace")
        else:
            keep = poly.intersection(under.buffer(CANTILEVER_M, join_style=2))
            if keep.geom_type in ("MultiPolygon", "GeometryCollection"):
                keep = max((g for g in getattr(keep, "geoms", []) if g.geom_type == "Polygon"), key=lambda g: g.area,
                           default=None)
            why = f"no part of it stands within {CANTILEVER_M:.1f} m of {below}'s walls"
            if keep is not None and (keep.is_empty or keep.area < MIN_KEEP_M2):
                keep = None
        if keep is None:
            rec["action"] = "dropped"
            rec["reason"] = f"{head}; {why}: not built (listed)"
            gone.add(sp.get("id"))
        else:
            sp["polygon"] = [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(keep.exterior.coords)[:-1]]
            rec["action"] = "clipped"
            rec["reason"] = (f"{head}: only its {keep.area:.1f} m2 over {below} and within {CANTILEVER_M:.1f} m of its "
                             f"walls is kept (a cantilever, or a terrace on the lower roof; listed)")
        out.append(rec)
    if gone:
        site["outdoor_spaces"] = [s for s in site["outdoor_spaces"] if s.get("id") not in gone]
    return out


def apply(build) -> list:
    """``check`` on the pipeline's building, logged (a warning per record, ``level_inference.upper_support``)."""
    b = build.building
    try:
        recs = check(b)
    except Exception as exc:  # noqa: BLE001 - logged: the spaces stay as read
        build.warn(f"upper outdoor spaces not checked for their supports ({type(exc).__name__}: {exc})")
        return []
    for r in recs:
        build.warn(f"upper support: {r['reason']}")
    if recs:
        b.setdefault("level_inference", {})["upper_support"] = recs
    return recs
