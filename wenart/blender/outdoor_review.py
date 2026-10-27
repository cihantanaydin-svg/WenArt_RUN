"""The outdoor spaces as a visitor uses them (27 Oct 2026, user, looking at real06's veranda and the balcony over it:
"Veranda still not looks like a veranda and balcony on top is not looking logical, need auditor to make logic and looks
check as I would do and correct the things" ... "The project needs to find these kind of things by itself without my
input" ... "Make argus catch these kind of things before me").

What: ``review(built, prep)`` measures every labelled outdoor space (``site.outdoor_spaces`` as the build plans it:
``prep["site"]["platforms"]`` of source ``outdoor_space``) and returns ``(findings, checked)`` in the model review's
format (check M10, ``model_review._v``):

- O1 a person can step out onto it: at least one door or doorless opening (never a window) of its level opens onto
  it (critical for a raised space: a balcony nobody can reach; major on the ground, where steps may do);
- O2 nobody falls: every edge of a raised space that no wall of its level backs has a guard (a railing edge of its
  platform) where the drop is ``DROP_GUARD_M`` or more (critical);
- O3 its floor is an outdoor floor of its kind: never the garden's paving with grass in its joints, never grass or a
  green roof (major; ``site.outdoor_floor_look``);
- O4 a covered kind (a veranda, porch, loggia, winter garden) or a space the documents cover is covered: its own cover,
  a raised space over it or the house's roof cover at least ``COVER_SHARE`` of it (major);
- O5 a roof is no floor: a light roof whose top is within ``SAME_LEVEL_M`` of a raised space's floor beside it, along
  an edge that space does not guard, is a roof a visitor steps onto from the balcony (major);
- O6 one post language: the posts of one space have one shape and sizes within ``POST_SIZE_RATIO`` (a 0.53 m round
  column beside a 0.15 m square stick reads as a mistake; minor).

Why: the renders of real06 showed a veranda like a carport (paving with grass joints, a bare concrete underside) and a
balcony on top of its roof with no logic between them; nothing in the pipeline measured either. Each finding names the
space, the edge or the post, and the number that fails; the findings go to the agent loop and to Argus with the rest of
the model review, and the fix rules live where the platforms are planned (``site.space_platform``, ``site.build_site``).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

DROP_GUARD_M = 0.5               # an open edge over a drop this high needs a guard
WALL_BACK_M = 0.35               # an edge this close to a wall of its level is backed by the building
WALL_BACK_SHARE = 0.8            # ... over this share of its length
COVER_SHARE = 0.8                # a covered kind is covered over at least this share of its area
SAME_LEVEL_M = 0.30              # a roof top this close to a floor beside it reads as the same surface
TOUCH_M = 0.10                   # a roof and a floor this close in plan share an edge
POST_SIZE_RATIO = 1.5            # the posts of one space differ in size by at most this factor
COVERED_KINDS = ("veranda", "porch", "loggia", "winter_garden")
GARDEN_FLOORS = ("paving", "grass", "green_roof")
RAISED_M = 1.0                   # a space more than this over the ground under it is raised


def _v(check: str, severity: str, target, message: str, room_id=None, **metrics) -> dict:
    from wenart.blender import model_review as MR

    return MR._v(check, severity, target, message, room_id, **metrics)


def _poly(pts):
    from shapely.geometry import Polygon

    try:
        p = Polygon([tuple(q[:2]) for q in pts or []])
        return p if p.is_valid else p.buffer(0)
    except (ValueError, TypeError):
        return None


def _edges(poly: list) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    n = len(poly)
    return [(tuple(poly[i][:2]), tuple(poly[(i + 1) % n][:2])) for i in range(n)]


def wall_backed(a, b, walls: list[dict]) -> float:
    """The share of the edge ``a``-``b`` that a wall of the list runs along (within ``WALL_BACK_M``; pure)."""
    length = G.distance(a, b)
    if length < 1e-6:
        return 1.0
    steps = max(2, int(length / 0.1))
    hit = 0
    for k in range(steps + 1):
        t = k / steps
        p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        if any(G.point_segment_distance(p, tuple(w["start"][:2]), tuple(w["end"][:2]))
               <= float(w.get("thickness") or 0.2) / 2.0 + WALL_BACK_M for w in walls):
            hit += 1
    return hit / (steps + 1)


def _shape(q: dict) -> str:
    """A post's shape as ``site.cover_parts`` builds it."""
    return "round" if q.get("shape") == "round" or (q.get("source") == "drawn" and float(q["size_m"]) >= 0.2) \
        else "square"


def space_label(pf: dict) -> str:
    sp = pf.get("space") or {}
    return f"{sp.get('kind') or 'outdoor space'} {sp.get('label') or pf['id']} ({pf['id']})"


def _floor_slug(pf: dict) -> Optional[str]:
    from wenart.blender import site as S

    look = S.outdoor_floor_look(pf)
    return (look or {}).get("material") or pf.get("material")


def review(built: dict, prep: Optional[dict]) -> tuple[list[dict], int]:
    """``(findings, checked)`` of check M10 (module docstring) on the build plan ``prep`` of ``built``."""
    site = (prep or {}).get("site") or {}
    spaces = [pf for pf in site.get("platforms") or [] if pf.get("source") == "outdoor_space"]
    if not spaces:
        return [], 0
    openings = {o["id"]: o for o in built.get("openings") or []}
    walls_by_level: dict = {}
    for w in built.get("walls") or []:
        if w.get("start") and w.get("end"):
            walls_by_level.setdefault(w.get("level_id"), []).append(w)
    roof_outline = ((prep or {}).get("roof") or {}).get("outline") or (built.get("roof") or {}).get("outline")
    roof_poly = _poly(roof_outline) if roof_outline else None
    out: list[dict] = []
    for pf in spaces:
        sp = pf.get("space") or {}
        kind = str(sp.get("kind") or "").lower()
        level = sp.get("level_id")
        name = space_label(pf)
        poly = pf.get("polygon") or []
        shape = _poly(poly)
        ground = (pf.get("ground") or {}).get("min")
        drop = float(pf["z"]) - float(ground) if isinstance(ground, (int, float)) else float(pf.get("drop_m") or 0.0)
        raised = bool(pf.get("elevated")) or drop > RAISED_M
        # O1 a way out onto it
        doors = [openings.get(d) for d in sp.get("doors") or []]
        ways = [o for o in doors if o is not None and o.get("type") != "window" and o.get("build", True) is not False]
        if not ways and not (not raised and (pf.get("steps_drawn") or pf.get("steps_edge") is not None)):
            named = ", ".join(f"{d} ({(openings.get(d) or {}).get('type', 'missing')})" for d in sp.get("doors") or [])
            out.append(_v("M10", "critical" if raised else "major", pf["id"],
                          f"O1: nobody can step out onto the {name}: no door or opening of {level} opens onto it"
                          + (f" (its openings: {named})" if named else ""),
                          rule="O1", openings=list(sp.get("doors") or []), raised=raised))
        # O2 guards on the open edges of a raised space
        if raised and len(poly) >= 3:
            rails = set(pf.get("railing_edges") or [])
            walls = walls_by_level.get(level) or []
            for i, (a, b) in enumerate(_edges(poly)):
                length = G.distance(a, b)
                if length < 0.3 or i in rails:
                    continue
                backed = wall_backed(a, b, walls)
                if backed >= WALL_BACK_SHARE:
                    continue
                if drop >= DROP_GUARD_M:
                    out.append(_v("M10", "critical", pf["id"],
                                  f"O2: the {name}'s edge {i} ({length:.2f} m, from {a[0]:.2f}, {a[1]:.2f} to "
                                  f"{b[0]:.2f}, {b[1]:.2f}) is open over a {drop:.2f} m drop: no guard, no wall "
                                  f"behind it ({backed:.0%} backed)", rule="O2", edge=i, length_m=round(length, 3),
                                  drop_m=round(drop, 3), backed=round(backed, 3)))
        # O3 an outdoor floor of its kind
        slug = _floor_slug(pf)
        if slug in GARDEN_FLOORS:
            out.append(_v("M10", "major", pf["id"],
                          f"O3: the {name}'s floor is the garden's {slug.replace('_', ' ')}: a {kind or 'space'} "
                          f"needs a deck or outdoor tiles", rule="O3", slug=slug))
        # O4 a covered kind is covered
        if shape is not None and shape.area > 0.5 and (kind in COVERED_KINDS or sp.get("cover")):
            covers = []
            roof = pf.get("roof") if isinstance(pf.get("roof"), dict) else None
            if roof and roof.get("polygon"):
                covers.append(_poly(roof["polygon"]))
            for other in spaces:
                if other is not pf and float(other["z"]) > float(pf["z"]) + 2.0 and other.get("polygon"):
                    covers.append(_poly(other["polygon"]))
            if roof_poly is not None and str(level) != str(((prep or {}).get("roof") or {}).get("over_level_id")):
                covers.append(roof_poly)
            covers = [c for c in covers if c is not None]
            covered = 0.0
            if covers:
                from shapely.ops import unary_union

                covered = shape.intersection(unary_union(covers)).area / shape.area
            if covered < COVER_SHARE:
                out.append(_v("M10", "major", pf["id"],
                              f"O4: the {name} is {'a covered kind' if kind in COVERED_KINDS else 'covered in the documents'}"
                              f" but only {covered:.0%} of its {shape.area:.1f} m2 is under a roof, a space above or "
                              f"the house's roof", rule="O4", covered=round(covered, 3), area_m2=round(shape.area, 2)))
        # O5 a roof beside a raised floor at the same level, along an unguarded edge
        roof = pf.get("roof") if isinstance(pf.get("roof"), dict) else None
        if roof and roof.get("polygon") and isinstance(roof.get("top_z"), (int, float)):
            rpoly = _poly(roof["polygon"])
            for other in spaces:
                if other is pf or not other.get("elevated") or not other.get("polygon") or rpoly is None:
                    continue
                if abs(float(other["z"]) - float(roof["top_z"])) > SAME_LEVEL_M:
                    continue
                rails = set(other.get("railing_edges") or [])
                for i, (a, b) in enumerate(_edges(other["polygon"])):
                    if i in rails or G.distance(a, b) < 0.3:
                        continue
                    from shapely.geometry import LineString

                    shared = LineString([a, b]).intersection(rpoly.buffer(TOUCH_M)).length
                    if shared >= 0.3:
                        out.append(_v("M10", "major", other["id"],
                                      f"O5: from the {space_label(other)} a visitor steps onto the roof of the "
                                      f"{name} over {shared:.2f} m of edge {i}: the roof's top "
                                      f"({float(roof['top_z']):.2f} m) is the balcony's floor level "
                                      f"({float(other['z']):.2f} m) and nothing guards the edge",
                                      rule="O5", edge=i, shared_m=round(shared, 3), roof_of=pf["id"]))
        # O6 one post language
        posts = [q for q in pf.get("posts") or [] if isinstance(q.get("size_m"), (int, float))]
        if len(posts) >= 2:
            sizes = [float(q["size_m"]) for q in posts]
            shapes = {_shape(q) for q in posts}
            if max(sizes) / max(1e-6, min(sizes)) > POST_SIZE_RATIO or len(shapes) > 1:
                out.append(_v("M10", "minor", pf["id"],
                              f"O6: the {name}'s posts do not match: "
                              + ", ".join(f"{q.get('id') or 'inferred'} {float(q['size_m']):.2f} m "
                                          f"{_shape(q)}"
                                          for q in posts), rule="O6", sizes=sizes, shapes=sorted(shapes)))
    return out, len(spaces)
