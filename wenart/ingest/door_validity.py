"""Door validity (26 Nov 2026, audit rule R05; real10, real17, real06): every door and doorless opening is checked
before it is built, after the reading's topology and again in the build's plan (``blender.build.prepare_once``).

What (``check(building, stage)``, mutates the building; ``voids_check(building, slab_plan)`` in the build):

1. **Inside its wall**: its centre lies within its host wall's span (``SPAN_TOL_M``). Else it is re-seated at its mirror
   twin's place (a door of the same storey whose mirror about the plan's mirror axis, ``facade.mirror_axis``, lies
   within ``TWIN_REACH_M`` of it, on a wall whose span holds it and where no opening stands yet), labelled
   ``corrected_by_ai`` (by code) with its drawn centre; failing that it is not built (``building["openings_not_built"]``
   with the reason) and a finding is listed (``needs_review``): a frame is never built in free space (real10's
   d_L0_028, 0.58 m past the end of its wall, the salon on both sides). A door read from its own symbol drawn at its
   place (``drawn_symbol``: a swing, a leaf, a block) keeps it: only its host wall may be the wrong one
   (synthetic-16's drawn door between a wall stub's end and the next wall).
2. **Two spaces**: a door with the same room on both sides (probed ``PROBE_M`` off both faces) is a finding (real17's
   d_L1_018 through a 5 cm slit between the landing and a flat's hall); the rooms are not split again here.
3. **A free passage**: a wall parallel to the door's wall standing glued to its face (``GLUED_GAP_M``) across the
   door's width blocks it (real10's 7 cm wall 4 cm behind the escape stair's 1.40 m door): listed in the reading; the
   build cuts the door through it (``blender.shell.foreign_cuts``).
4. **A floor on both sides** (the build's slab plan): a door of an upper storey whose side lies over an opening of the
   floor slab under it (a stair void) opens onto a drop: it is not built (real06's d_L1_009 onto the stair void).

Why: the review's model checks (M1, M9) only reported such doors, and the build built them.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

RULE = "reading.door_validity"
SPAN_TOL_M = 0.05          # a door's centre may stand this far past its wall's end
TWIN_REACH_M = 1.0         # its mirror twin's place lies this close to it
TWIN_SNAP_M = 0.15         # ... on a wall whose centre line passes this close to the mirrored centre (plus its half)
TWIN_FREE_M = 0.5          # ... where no opening of that wall stands this close
PROBE_M = 0.30             # the two sides are probed this far off the door's faces
GLUED_GAP_M = 0.10         # a parallel wall this close to a door's face stands in its passage
DOOR_TYPES = ("door", "opening")


def _axis(w: dict):
    (x0, y0), (x1, y1) = [float(v) for v in w["start"][:2]], [float(v) for v in w["end"][:2]]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-9:
        return None
    return (x0, y0), ((x1 - x0) / length, (y1 - y0) / length), length


def _along(ax, p) -> float:
    (x0, y0), (ux, uy), _ = ax
    return (float(p[0]) - x0) * ux + (float(p[1]) - y0) * uy


def _across(ax, p) -> float:
    (x0, y0), (ux, uy), _ = ax
    return -(float(p[0]) - x0) * uy + (float(p[1]) - y0) * ux


def in_span(o: dict, wall: dict, tol: float = SPAN_TOL_M) -> bool:
    """Whether the opening's centre lies within its host wall's span (pure)."""
    ax = _axis(wall)
    if ax is None or not o.get("center"):
        return False
    t = _along(ax, o["center"])
    return -tol <= t <= ax[2] + tol


PLACED_RULES = ("size_tag", "size_tag_jamb", "size_tag_leaf_door", "ranker", "framed_window")


def drawn_symbol(o: dict) -> bool:
    """A door read from its own symbol drawn at its place (the gap classifier's swing, leaf or block: vector or raster
    evidence without a placing rule, none inferred): its place is the drawing's, only its host wall may be the wrong
    one (a drawn door between a wall's end and another wall), so check 1 leaves it; a door a size tag, the ranker or a
    window frame placed is checked (pure)."""
    ev = o.get("evidence") or []
    ev = [e for e in (ev if isinstance(ev, list) else [ev]) if isinstance(e, dict)]
    return any(e.get("method") in ("vector", "raster") and not e.get("rule") for e in ev) and \
        not any(e.get("method") == "inferred" or e.get("rule") in PLACED_RULES for e in ev)


def _room_at(rooms: list, p) -> Optional[dict]:
    return next((r for r in rooms if len(r.get("polygon") or []) >= 3 and G.point_in_polygon(p, r["polygon"])), None)


def sides(o: dict, wall: dict, rooms: list, probe: float = PROBE_M) -> list:
    """The rooms (or None) a door's two sides open into, probed ``probe`` off its faces (pure)."""
    ax = _axis(wall)
    if ax is None:
        return [None, None]
    (_x0, _y0), (ux, uy), _ = ax
    t = _along(ax, o["center"])
    cx, cy = ax[0][0] + ux * t, ax[0][1] + uy * t
    reach = float(wall.get("thickness") or 0.0) / 2.0 + probe
    return [_room_at(rooms, (cx - uy * s * reach, cy + ux * s * reach)) for s in (1.0, -1.0)]


def _twin_place(o: dict, level_walls: list, level_doors: list, axis) -> Optional[tuple]:
    """``(wall, centre, twin)``: the place of ``o``'s mirror twin (module docstring), or None (pure)."""
    if axis is None:
        return None
    which, v = axis
    c = (float(o["center"][0]), float(o["center"][1]))
    best = None
    for p in level_doors:
        if p is o or not p.get("center") or p.get("type") != "door":
            continue
        px, py = float(p["center"][0]), float(p["center"][1])
        m = (2.0 * v - px, py) if which == "x" else (px, 2.0 * v - py)
        d = math.dist(m, c)
        if d > TWIN_REACH_M:
            continue
        for w in level_walls:
            ax = _axis(w)
            if ax is None or abs(_across(ax, m)) > float(w.get("thickness") or 0.0) / 2.0 + TWIN_SNAP_M:
                continue
            t = _along(ax, m)
            if not -SPAN_TOL_M <= t <= ax[2] + SPAN_TOL_M:      # the twin's place passes the check its door must
                continue
            if any(q is not o and q.get("wall_id") == w["id"] and q.get("center")
                   and abs(_along(ax, q["center"]) - t) < TWIN_FREE_M for q in level_doors):
                continue
            centre = (round(ax[0][0] + ax[1][0] * t, 4), round(ax[0][1] + ax[1][1] * t, 4))
            if best is None or d < best[0]:
                best = (d, w, centre, p)
    return best[1:] if best else None


def _finding(b: dict, oid: str, kind: str, reason: str, level: Optional[str]) -> None:
    rows = b.setdefault("needs_review", [])
    if not any(r.get("id") == oid and r.get("kind") == kind for r in rows):
        rows.append({"id": oid, "kind": kind, "reason": reason, "crop": None, "level_id": level})


def check(b: dict, stage: str = "reading", warn: Callable[[str], None] = lambda _m: None,
          mirror_axis: Optional[Callable] = None) -> dict:
    """The door checks 1-3 of the module docstring on ``b`` (mutated). ``mirror_axis(walls)``: the plan's mirror axis
    (``facade.mirror_axis``; the reading passes it, the build's import closure stays small); without it a door outside
    its wall is never re-seated. Returns ``{"reseated", "not_built", "same_room", "blocked", "notes"}``."""
    out: dict = {"reseated": [], "not_built": [], "same_room": [], "blocked": [], "notes": []}
    walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")]
    by_id = {w["id"]: w for w in walls}
    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    walls_by: dict = {}
    for w in walls:
        walls_by.setdefault(w.get("level_id"), []).append(w)
    axes: dict = {}
    ops = [o for o in b.get("openings") or [] if isinstance(o, dict)]
    gone = []
    for o in ops:
        if o.get("type") not in DOOR_TYPES or o.get("virtual") or not o.get("center"):
            continue
        host = by_id.get(o.get("wall_id"))
        if host is None:
            continue
        lid = o.get("level_id")
        if not in_span(o, host) and not drawn_symbol(o):
            if lid not in axes:
                lw = walls_by.get(lid) or []
                axes[lid] = mirror_axis(lw) if mirror_axis is not None and len(lw) >= 4 else None
            ax = _axis(host)
            past = max(-_along(ax, o["center"]), _along(ax, o["center"]) - ax[2]) if ax else 0.0
            twin = _twin_place(o, walls_by.get(lid) or [], [q for q in ops if q.get("level_id") == lid], axes[lid])
            if twin is not None:
                w, centre, p = twin
                reason = (f"its centre stood {past:.2f} m past the end of its wall {host['id']} ({stage}): re-seated "
                          f"at the place of its mirror twin {p['id']} on {w['id']}")
                o.setdefault("drawn_center", list(o["center"]))
                o["corrected_by_ai"] = {"by": "code", "rule": RULE, "reason": reason,
                                        "before": {"center": list(o["center"]), "wall_id": host["id"]}}
                o["center"], o["wall_id"] = list(centre), w["id"]
                out["reseated"].append(o["id"])
                out["notes"].append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
                host = w
            else:
                reason = (f"its centre stands {past:.2f} m past the end of its wall {host['id']} and no mirror twin "
                          f"gives its place ({stage}): not built (a frame is never built in free space)")
                gone.append(o)
                b.setdefault("openings_not_built", []).append(dict(o, not_built={"by": "code", "rule": RULE,
                                                                                 "reason": reason}))
                _finding(b, o["id"], "door_outside_wall", reason, lid)
                out["not_built"].append(o["id"])
                out["notes"].append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
                continue
        rooms = rooms_by.get(lid) or []
        s = sides(o, host, rooms)
        if s[0] is not None and s[1] is not None and s[0]["id"] == s[1]["id"]:
            reason = (f"the room {s[0]['id']} lies on both of its sides ({stage}): a leak in the walls (a slit) or a "
                      f"misplaced door, to review")
            _finding(b, o["id"], "door_same_room", reason, lid)
            out["same_room"].append(o["id"])
            out["notes"].append(f"{o['id']}: {reason}")
            warn(f"door check: {o['id']}: {reason}")
        if o.get("type") == "door":
            for w in blocking_walls(o, host, walls_by.get(lid) or []):
                reason = (f"the wall {w['id']} stands {glued_gap(host, w):.2f} m off its face across its "
                          f"{float(o.get('width') or 0):.2f} m passage ({stage}): the door is cut through it")
                _finding(b, o["id"], "door_passage_blocked", reason, lid)
                out["blocked"].append([o["id"], w["id"]])
                out["notes"].append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
    if gone:
        b["openings"] = [o for o in b.get("openings") or [] if not any(o is g for g in gone)]
    return out


def glued_gap(host: dict, w: dict) -> float:
    """The gap between the facing faces of two parallel walls (negative when they overlap in depth; pure)."""
    ax = _axis(host)
    if ax is None:
        return math.inf
    mid = [(float(w["start"][i]) + float(w["end"][i])) / 2.0 for i in (0, 1)]
    return abs(_across(ax, mid)) - (float(host.get("thickness") or 0.0) + float(w.get("thickness") or 0.0)) / 2.0


def blocking_walls(o: dict, host: dict, level_walls: list, tol_deg: float = 3.0) -> list:
    """The walls parallel to the door's wall standing glued to one of its faces (a gap of 0 to ``GLUED_GAP_M``) across
    at least half of the door's width: a wall in its passage (pure; check 3)."""
    ax = _axis(host)
    if ax is None:
        return []
    t, half = _along(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
    out = []
    for w in level_walls:
        if w is host or w.get("id") == host.get("id"):
            continue
        wx = _axis(w)
        if wx is None or abs(ax[1][0] * wx[1][1] - ax[1][1] * wx[1][0]) > math.sin(math.radians(tol_deg)):
            continue
        gap = glued_gap(host, w)
        if not -1e-6 <= gap <= GLUED_GAP_M:
            continue
        lo, hi = sorted((_along(ax, w["start"]), _along(ax, w["end"])))
        if min(hi, t + half) - max(lo, t - half) >= half:
            out.append(w)
    return out


def voids_check(b: dict, slabs: Optional[dict], stage: str = "build",
                warn: Callable[[str], None] = lambda _m: None) -> list[str]:
    """Check 4 of the module docstring: a door of a storey whose side, probed ``PROBE_M`` and twice that off its face,
    lies in an opening of the floor slab under that storey (the build's slab plan
    ``slabs["by_level"][level]["under"]["voids"]``) is not built (``openings_not_built``, a finding). Mutates ``b``;
    returns one note per door."""
    by_level = (slabs or {}).get("by_level") or {}
    by_id = {w["id"]: w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")}
    notes, gone = [], []
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("virtual") or not o.get("center"):
            continue
        under = (by_level.get(o.get("level_id")) or {}).get("under") or {}
        voids = [v for v in under.get("voids") or [] if len(v) >= 3]
        host = by_id.get(o.get("wall_id"))
        ax = _axis(host) if host else None
        if not voids or ax is None:
            continue
        (_x0, _y0), (ux, uy), _ = ax
        t = _along(ax, o["center"])
        cx, cy = ax[0][0] + ux * t, ax[0][1] + uy * t
        half_t = float(host.get("thickness") or 0.0) / 2.0
        polys = [[tuple(q[:2]) for q in v] for v in voids]
        for s in (1.0, -1.0):
            # both a step (PROBE_M) and two steps out lie over the opening: no floor to stand on in front of the door
            probes = [(cx - uy * s * (half_t + k * PROBE_M), cy + ux * s * (half_t + k * PROBE_M)) for k in (1, 2)]
            if all(any(G.point_in_polygon(p, v) for v in polys) for p in probes):
                reason = (f"one of its sides opens over an opening of the floor slab under {o.get('level_id')} (a "
                          f"drop, no floor) ({stage}): not built")
                gone.append(o)
                b.setdefault("openings_not_built", []).append(dict(o, not_built={"by": "code", "rule": RULE,
                                                                                 "reason": reason}))
                _finding(b, o["id"], "door_over_void", reason, o.get("level_id"))
                notes.append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
                break
    if gone:
        b["openings"] = [o for o in b.get("openings") or [] if not any(o is g for g in gone)]
    return notes
