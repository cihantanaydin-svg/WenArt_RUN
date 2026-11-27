"""Door validity (26 Nov 2026, audit rule R05; real10, real17, real06): every door and doorless opening is checked
before it is built, after the reading's topology and again in the build's plan (``blender.build.prepare_once``).

What (``check(building, stage)``, mutates the building; ``voids_check(building, slab_plan)`` in the build):

1. **Inside its wall**: its centre lies within its host wall's span (``SPAN_TOL_M``). A door read from its own symbol
   drawn at its place (``drawn_symbol``: a swing, a leaf, a block, kept when a size tag re-sized it) keeps it: only its
   host wall may be the wrong one (synthetic-16's drawn door between a wall stub's end and the next wall; real10's
   d_L0_028); in no bay at its wall's end it is listed (``door_outside_wall``, built). Any other door outside its wall:
   a. **in the bay at its wall's end** (27 Nov 2026, audit O2: ``bay_of``): its span lies between its host's end and the
      next wall on the host's line, a bay at most ``BAY_SLACK_M`` wider than the door: the door is that bay's door; it
      keeps its place and its host is extended to the next wall (the wall labelled ``corrected_by_ai`` with its drawn
      ends);
   b. else at its **mirror twin's** place (``_twin_place``; 27 Nov 2026, audit O3: only with the plan's strict mirror
      axis, ``facade.MIRROR_FIX_SHARE``; a twin door of the same width within ``TWIN_WIDTH_TOL_M`` whose mirror lies
      within ``TWIN_REACH_M`` of it, on a wall parallel to its host whose span holds the door's whole width and where no
      other opening stands; the swing side and the rotation are taken again from the new wall), labelled
      ``corrected_by_ai`` (by code) with its drawn centre;
   c. else it is not built (``building["openings_not_built"]`` with the reason) and a finding is listed
      (``needs_review``): a frame is never built in free space.
2. **Two spaces**: a door with the same room on both sides (probed ``PROBE_M`` off both faces) is a finding (real17's
   d_L1_018 through a 5 cm slit between the landing and a flat's hall); the rooms are not split again here.
3. **A free passage**: a wall parallel to the door's wall standing glued to its face (``GLUED_GAP_M``) across the
   door's width blocks it (real10's 7 cm wall 4 cm behind the escape stair's 1.40 m door): listed in the reading; the
   build cuts the door through it (``blender.shell.foreign_cuts``) unless it is a column or a pier
   (``column_piece``, the one rule of both: 27 Nov 2026, audit O5): then the finding says so.
4. **A floor on both sides** (the build's slab plan; 27 Nov 2026, audit O4, ``voids_check``): each side is probed at
   three points across the door's width, ``PROBE_M`` and twice that off its face. A probe over an opening of the slab
   under the storey is floor when the stair of the level below stands there within ``STAIR_HEAD_M`` under the floor
   (the stair's head: a door onto its top), or when a room of this storey lies there and this storey's own plan draws
   no stair there (the opening is the level below's stair's, not confirmed by this plan: the drawn room wins). A side
   whose every probe column is over the void is a certain drop: the door is not built (real06's 25 Oct d_L1_004, its
   inner side over the stair's turn); most of them: listed, built.

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
TWIN_FREE_M = 0.10         # ... where no other opening's span comes this close to the door's span
TWIN_WIDTH_TOL_M = 0.10    # 27 Nov 2026 (O3): a mirror twin is a door of the same width within this
TWIN_PARALLEL_DEG = 3.0    # ... on a wall parallel to the door's host within this
BAY_TOL_M = 0.10           # 27 Nov 2026 (O2): a door's span may stand this far past the ends of the bay it fills ...
BAY_SLACK_M = 0.30         # ... a bay at most this much wider than the door
LINE_TOL_M = 0.03          # a wall meets the host's line where its band (half its thickness plus this) crosses it ...
END_TOL_M = 0.15           # ... or its end stops this short of the line (a corner closes the bay: synthetic-16)
PROBE_M = 0.30             # the two sides are probed this far off the door's faces
PROBE_ALONG = (-0.3, 0.0, 0.3)   # 27 Nov 2026 (O4): ... at these shares of the width along the door
STAIR_HEAD_M = 0.50        # ... a stair's top this close under the floor is the stair's head: a floor to step onto
GLUED_GAP_M = 0.10         # a parallel wall this close to a door's face stands in its passage
COLUMN_PIECE_MAX_M = 1.0   # R03 e: a wall piece shorter than this (``twin_walls.MIN_COPY_M``) ...
COLUMN_THICKER_M = 0.01    # ... and thicker than an opening's wall by more than this is a column or a pier
DOOR_TYPES = ("door", "opening")
STAIR_TYPES = ("stair",)   # = ``blender.parametric.SHELL_TYPES``


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


def span_inside(o: dict, wall: dict, tol: float = SPAN_TOL_M) -> bool:
    """27 Nov 2026 (audit O3): whether the opening's whole width (its centre plus and minus half its width along the
    wall) lies within the wall's span (pure)."""
    ax = _axis(wall)
    if ax is None or not o.get("center"):
        return False
    t, half = _along(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
    return -tol <= t - half and t + half <= ax[2] + tol


PLACED_RULES = ("size_tag", "size_tag_jamb", "size_tag_leaf_door", "ranker", "framed_window")


def _evidence(o: dict) -> list:
    ev = o.get("evidence") or []
    return [e for e in (ev if isinstance(ev, list) else [ev]) if isinstance(e, dict)]


def drawn_symbol(o: dict) -> bool:
    """A door read from its own symbol drawn at its place (the gap classifier's swing, leaf or block: vector or raster
    evidence without a placing rule), none of its evidence inferred: its place is the drawing's, only its host wall may
    be the wrong one (a drawn door between a wall's end and another wall), so check 1 leaves it. 27 Nov 2026 (audit O2:
    real10's d_L0_028, read from its swing ARC:14F743, lost that evidence when its '110/230' re-sized it and was moved
    into a solid wall): a size tag that re-sized a drawn door keeps the door's own evidence after its own
    (``generic.core._door_tags``), and the door stays drawn. A door only a size tag, the ranker or a window frame placed
    (``PLACED_RULES``, no symbol of its own) is checked (pure)."""
    ev = _evidence(o)
    return any(e.get("method") in ("vector", "raster") and not e.get("rule") for e in ev) and \
        not any(e.get("method") == "inferred" for e in ev)


def column_piece(wall: dict, host: Optional[dict] = None) -> bool:
    """26 Nov 2026 (R03 e): whether ``wall`` is a column (or a pier) that no other wall's door or window cuts (pure): a
    piece shorter than ``COLUMN_PIECE_MAX_M`` drawn on a structure layer (its evidence's layer: KOLON, COLUMN,
    BETONARME ...), or thicker than the opening's wall ``host`` by more than ``COLUMN_THICKER_M`` (a short, thicker
    block in a wall is never a copy of it: ``twin_walls``). 27 Nov 2026 (audit O5): the one rule of the build's cut
    (``blender.shell.foreign_cuts``) and of check 3's finding."""
    try:
        length = math.dist([float(v) for v in wall["start"][:2]], [float(v) for v in wall["end"][:2]])
    except (KeyError, TypeError, ValueError):
        return False
    if length >= COLUMN_PIECE_MAX_M:
        return False
    from wenart.ingest.generic import layer_names as LN       # no jsonschema: Blender's Python reads it (audit O1)

    ev = wall.get("evidence") or []
    if any(isinstance(e, dict) and LN.name_role(e.get("layer")) == "structure" for e in (ev if isinstance(ev, list)
                                                                                       else [ev])):
        return True
    return host is not None and float(wall.get("thickness") or 0.0) > float(host.get("thickness") or 0.0) + \
        COLUMN_THICKER_M


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


def _line_hit(ax, w: dict) -> Optional[tuple[float, float]]:
    """The stretch ``(s0, s1)`` of the line of axis ``ax`` (along it) that wall ``w``'s band (its length plus
    ``END_TOL_M`` at each end, half its thickness plus ``LINE_TOL_M``) covers, or None (pure)."""
    wx = _axis(w)
    if wx is None:
        return None
    (ax0, ay0), (ux, uy), _ = ax
    (wx0, wy0), (vx, vy), wl = wx
    hw = float(w.get("thickness") or 0.0) / 2.0 + LINE_TOL_M
    dx, dy = ax0 - wx0, ay0 - wy0
    lo, hi = -math.inf, math.inf
    # along w: x(s) = (d + s u) . v in [-end, wl + end]; across w: y(s) = cross(v, d + s u) in [-hw, hw]
    for c, k, a, b in ((dx * vx + dy * vy, ux * vx + uy * vy, -END_TOL_M, wl + END_TOL_M),
                       (vx * dy - vy * dx, vx * uy - vy * ux, -hw, hw)):
        if abs(k) < 1e-9:
            if not a <= c <= b:
                return None
            continue
        s0, s1 = sorted(((a - c) / k, (b - c) / k))
        lo, hi = max(lo, s0), min(hi, s1)
    return (lo, hi) if lo <= hi else None


def bay_of(o: dict, host: dict, level_walls: list) -> Optional[dict]:
    """27 Nov 2026 (audit O2): the bay a door outside its host's span fills (pure): its span lies between the host's end
    (or start) and the next wall that meets the host's line beyond it (``_line_hit``; walls at the host's end itself
    are passed), within ``BAY_TOL_M``, and the bay is at most ``BAY_SLACK_M`` wider than the door. ``{"side": "end" |
    "start", "near", "far", "wall_id"}`` (along the host: ``near`` the bay's start at the host, ``far`` the next wall's
    face) or None."""
    ax = _axis(host)
    if ax is None or not o.get("center"):
        return None
    t, half = _along(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
    if abs(_across(ax, o["center"])) > float(host.get("thickness") or 0.0) / 2.0 + TWIN_SNAP_M or half <= 0:
        return None
    length = ax[2]
    side = "end" if t > length else "start"
    hits = []
    for w in level_walls:
        if w is host or w.get("id") == host.get("id"):
            continue
        h = _line_hit(ax, w)
        if h is None:
            continue
        a, b = (h if side == "end" else (-h[1], -h[0]))           # measured outward from the host's end
        a, b = (a - length, b - length) if side == "end" else (a, b)
        if b > -SPAN_TOL_M:
            hits.append((a, b, w.get("id")))
    near, far, wid = 0.0, None, None
    for a, b, i in sorted(hits):
        if a <= near + LINE_TOL_M:
            near = max(near, b)                                   # a wall at the host's end: the bay starts past it
            continue
        far, wid = a, i
        break
    if far is None:
        return None
    lo, hi = (t - half - length, t + half - length) if side == "end" else (-(t + half), -(t - half))
    if lo < near - BAY_TOL_M or hi > far + BAY_TOL_M or far - near > 2.0 * half + BAY_SLACK_M:
        return None
    if side == "end":
        return {"side": side, "near": round(length + near, 4), "far": round(length + far, 4), "wall_id": wid}
    return {"side": side, "near": round(-near, 4), "far": round(-far, 4), "wall_id": wid}


def _parallel(a: dict, b: dict, tol_deg: float = TWIN_PARALLEL_DEG) -> bool:
    ax, bx = _axis(a), _axis(b)
    return ax is not None and bx is not None and \
        abs(ax[1][0] * bx[1][1] - ax[1][1] * bx[1][0]) <= math.sin(math.radians(tol_deg))


def _twin_place(o: dict, host: dict, level_walls: list, level_doors: list, axis) -> Optional[tuple]:
    """``(wall, centre, twin)``: the place of ``o``'s mirror twin (module docstring, 1b), or None (pure)."""
    if axis is None:
        return None
    which, v = axis
    c = (float(o["center"][0]), float(o["center"][1]))
    half = float(o.get("width") or 0.0) / 2.0
    best = None
    for p in level_doors:
        if p is o or not p.get("center") or p.get("type") != "door":
            continue
        if abs(float(p.get("width") or 0.0) - 2.0 * half) > TWIN_WIDTH_TOL_M + 1e-9:
            continue                                            # another door, not its twin (audit O3)
        px, py = float(p["center"][0]), float(p["center"][1])
        m = (2.0 * v - px, py) if which == "x" else (px, 2.0 * v - py)
        d = math.dist(m, c)
        if d > TWIN_REACH_M:
            continue
        for w in level_walls:
            ax = _axis(w)
            if ax is None or not _parallel(w, host) or \
                    abs(_across(ax, m)) > float(w.get("thickness") or 0.0) / 2.0 + TWIN_SNAP_M:
                continue
            t = _along(ax, m)
            if not (-SPAN_TOL_M <= t - half and t + half <= ax[2] + SPAN_TOL_M):
                continue                                        # the whole door on the wall (audit O3)
            if any(q is not o and q.get("wall_id") == w["id"] and q.get("center") and
                   abs(_along(ax, q["center"]) - t) < half + float(q.get("width") or 0.0) / 2.0 + TWIN_FREE_M
                   for q in level_doors):
                continue
            centre = (round(ax[0][0] + ax[1][0] * t, 4), round(ax[0][1] + ax[1][1] * t, 4))
            if best is None or d < best[0]:
                best = (d, w, centre, p)
    return best[1:] if best else None


def _swing_after(o: dict, old: dict, new: dict, centre, rooms: list) -> Optional[str]:
    """The room a door re-seated from wall ``old`` to the parallel wall ``new`` swings into: the room on the side of the
    new wall facing the way it swung on the old one (pure; audit O3)."""
    swing = o.get("swing_side")
    oax, nax = _axis(old), _axis(new)
    if not swing or oax is None or nax is None:
        return None
    s_old = sides(o, old, rooms)
    k = next((i for i, r in enumerate(s_old) if r is not None and r.get("id") == swing), None)
    if k is None:
        return None
    sgn = 1.0 if k == 0 else -1.0
    n_old = (-oax[1][1] * sgn, oax[1][0] * sgn)                 # the way it swung (``sides``: index 0 is +normal)
    n_new = (-nax[1][1], nax[1][0])
    j = 0 if n_old[0] * n_new[0] + n_old[1] * n_new[1] >= 0 else 1
    r = sides(dict(o, center=list(centre)), new, rooms)[j]
    return r["id"] if r is not None else None


def _finding(b: dict, oid: str, kind: str, reason: str, level: Optional[str]) -> None:
    rows = b.setdefault("needs_review", [])
    if not any(r.get("id") == oid and r.get("kind") == kind for r in rows):
        rows.append({"id": oid, "kind": kind, "reason": reason, "crop": None, "level_id": level})


def _extend(b: dict, host: dict, bay: dict, oid: str, stage: str) -> dict:
    """``host`` extended over the bay a door fills (a new wall dict replaces it in ``b["walls"]``: a build's plan shares
    its walls with the caller's building), labelled ``corrected_by_ai`` with its drawn ends (pure but for ``b``)."""
    ax = _axis(host)
    s = bay["far"]
    p = [round(ax[0][0] + ax[1][0] * s, 4), round(ax[0][1] + ax[1][1] * s, 4)]
    new = dict(host)
    key = "end" if bay["side"] == "end" else "start"
    new[key] = p + list(host[key][2:])
    reason = (f"the door {oid} fills the bay from its {bay['side']} to the next wall"
              + (f" {bay['wall_id']}" if bay.get("wall_id") else "") +
              f" ({abs(bay['far'] - bay['near']):.2f} m; {stage}): the wall is extended over it, the door keeps its place")
    new["corrected_by_ai"] = {"by": "code", "rule": RULE, "reason": reason,
                              "before": {"start": list(host["start"]), "end": list(host["end"])}}
    b["walls"] = [new if w is host else w for w in b.get("walls") or []]
    return new


def check(b: dict, stage: str = "reading", warn: Callable[[str], None] = lambda _m: None,
          mirror_axis: Optional[Callable] = None) -> dict:
    """The door checks 1-3 of the module docstring on ``b`` (mutated). ``mirror_axis(walls)``: the plan's mirror axis
    (``facade.mirror_axis`` at ``MIRROR_FIX_SHARE``; the reading passes it, the build's import closure stays small);
    without it a door outside its wall is never re-seated. Returns ``{"reseated", "extended", "not_built", "listed"
    (drawn doors past their wall's end in no bay: built, a finding), "same_room", "blocked", "notes"}``."""
    out: dict = {"reseated": [], "extended": [], "not_built": [], "listed": [], "same_room": [], "blocked": [],
                 "notes": []}
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
        if not in_span(o, host) and drawn_symbol(o) and bay_of(o, host, walls_by.get(lid) or []) is None:
            # 27 Nov 2026 (audit O2): a drawn door keeps the drawing's place, but a frame standing past its wall's end in
            # no bay is never silent (real10's d_L-1_022, a 45° door read straight, past the chamfer wall)
            ax = _axis(host)
            past = max(-_along(ax, o["center"]), _along(ax, o["center"]) - ax[2]) if ax else 0.0
            reason = (f"drawn at its place (its own symbol), its centre {past:.2f} m past the end of its wall "
                      f"{host['id']}, in no bay at the wall's end ({stage}): built where the drawing has it; its wall "
                      f"is to review")
            _finding(b, o["id"], "door_outside_wall", reason, lid)
            out["listed"].append(o["id"])
            out["notes"].append(f"{o['id']}: {reason}")
            warn(f"door check: {o['id']}: {reason}")
        if not in_span(o, host) and not drawn_symbol(o):
            ax = _axis(host)
            past = max(-_along(ax, o["center"]), _along(ax, o["center"]) - ax[2]) if ax else 0.0
            bay = bay_of(o, host, walls_by.get(lid) or [])
            twin = None
            if bay is None:
                if lid not in axes:
                    lw = walls_by.get(lid) or []
                    axes[lid] = mirror_axis(lw) if mirror_axis is not None and len(lw) >= 4 else None
                twin = _twin_place(o, host, walls_by.get(lid) or [], [q for q in ops if q.get("level_id") == lid],
                                   axes[lid])
            if bay is not None:
                new = _extend(b, host, bay, o["id"], stage)
                by_id[new["id"]] = new
                walls_by[lid] = [new if w is host else w for w in walls_by.get(lid) or []]
                reason = new["corrected_by_ai"]["reason"]
                out["extended"].append([o["id"], new["id"]])
                out["notes"].append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
                host = new
            elif twin is not None:
                w, centre, p = twin
                swing = _swing_after(o, host, w, centre, rooms_by.get(lid) or [])
                reason = (f"its centre stood {past:.2f} m past the end of its wall {host['id']} ({stage}): re-seated "
                          f"at the place of its mirror twin {p['id']} on {w['id']} (the same width, a parallel wall)")
                before = {"center": list(o["center"]), "wall_id": host["id"], "swing_side": o.get("swing_side")}
                o.setdefault("drawn_center", list(o["center"]))
                o["center"], o["wall_id"] = list(centre), w["id"]
                o["swing_side"] = swing
                if "rotation_deg" in o:
                    wax = _axis(w)
                    before["rotation_deg"] = o["rotation_deg"]
                    o["rotation_deg"] = round(math.degrees(math.atan2(wax[1][1], wax[1][0])), 3)
                o["corrected_by_ai"] = {"by": "code", "rule": RULE, "reason": reason, "before": before}
                out["reseated"].append(o["id"])
                out["notes"].append(f"{o['id']}: {reason}")
                warn(f"door check: {o['id']}: {reason}")
                host = w
            else:
                reason = (f"its centre stands {past:.2f} m past the end of its wall {host['id']}, in no bay at the "
                          f"wall's end, and no mirror twin gives its place ({stage}): not built (a frame is never built "
                          f"in free space)")
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
                if column_piece(w, host):
                    what = ("a column or a pier (shorter than "
                            f"{COLUMN_PIECE_MAX_M:.1f} m, on a structure layer or thicker than the door's wall): it is "
                            "never cut, the door is built facing it; to review")
                else:
                    what = "the door is cut through it"
                reason = (f"the wall {w['id']} stands {glued_gap(host, w):.2f} m off its face across its "
                          f"{float(o.get('width') or 0):.2f} m passage ({stage}): {what}")
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


def _stairs_of(b: dict, level_id: Optional[str]) -> list:
    """The footprints (polygons) of the stairs ``level_id``'s own plan draws (pure; check 4)."""
    out = []
    for f in b.get("furniture") or []:
        fp = f.get("footprint") if isinstance(f, dict) else None
        if f.get("level_id") != level_id or f.get("type") not in STAIR_TYPES or not isinstance(fp, dict) \
                or not fp.get("center") or not fp.get("size"):
            continue
        try:
            out.append(G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0)))
        except (TypeError, ValueError, IndexError):
            continue
    return out


def _probe(p, voids: list, own_stairs: list, rooms: list, level_id, stair_z) -> str:
    """What a door's probe point stands on (pure; check 4): ``floor`` (no opening of the slab under it), ``stair``
    (the head of the level below's stair: its top within ``STAIR_HEAD_M`` under the floor), ``room`` (an opening this
    storey's plan does not confirm, no stair of it drawn there, under a room of it), ``drop``."""
    if not any(G.point_in_polygon(p, v) for v in voids):
        return "floor"
    z = stair_z(level_id, p) if stair_z is not None else None
    if z is not None and z >= -STAIR_HEAD_M:
        return "stair"
    if any(G.point_in_polygon(p, s) for s in own_stairs):
        return "drop"                        # this storey's plan draws the stair there: the opening is confirmed
    return "room" if _room_at(rooms, p) is not None else "drop"


def voids_check(b: dict, slabs: Optional[dict], stage: str = "build",
                warn: Callable[[str], None] = lambda _m: None,
                stair_z: Optional[Callable] = None) -> list[str]:
    """Check 4 of the module docstring: each side of a door is probed at ``PROBE_ALONG`` shares of its width, ``PROBE_M``
    and twice that off its face, against the openings of the floor slab under its storey (the build's slab plan
    ``slabs["by_level"][level]["under"]["voids"]``; ``_probe``). A side whose every column of probes stands over a
    drop is a certain drop: the door is not built (``openings_not_built``, a finding ``door_over_void``); a side with
    most of its columns over a drop is listed (``door_over_void``, built); a door kept only because a room of its storey
    lies over the opening gets a note. ``stair_z(level_id, point)``: the top of the level below's stairs at a point,
    from the floor of ``level_id`` (negative under it), None where no stair stands (the build passes it). Mutates ``b``;
    returns one note per door."""
    by_level = (slabs or {}).get("by_level") or {}
    by_id = {w["id"]: w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")}
    rooms_by: dict = {}
    for r in b.get("rooms") or []:
        rooms_by.setdefault(r.get("level_id"), []).append(r)
    stairs: dict = {}
    notes, gone = [], []
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("virtual") or not o.get("center"):
            continue
        lid = o.get("level_id")
        under = (by_level.get(lid) or {}).get("under") or {}
        voids = [v for v in under.get("voids") or [] if len(v) >= 3]
        host = by_id.get(o.get("wall_id"))
        ax = _axis(host) if host else None
        if not voids or ax is None:
            continue
        if lid not in stairs:
            stairs[lid] = _stairs_of(b, lid)
        (_x0, _y0), (ux, uy), _ = ax
        t = _along(ax, o["center"])
        width = float(o.get("width") or 0.0)
        half_t = float(host.get("thickness") or 0.0) / 2.0
        polys = [[tuple(q[:2]) for q in v] for v in voids]
        rooms = rooms_by.get(lid) or []
        worst, by_room = None, False
        for s in (1.0, -1.0):
            cols = []
            for f in PROBE_ALONG:
                cx, cy = ax[0][0] + ux * (t + f * width), ax[0][1] + uy * (t + f * width)
                kinds = [_probe((cx - uy * s * (half_t + k * PROBE_M), cy + ux * s * (half_t + k * PROBE_M)), polys,
                                stairs[lid], rooms, lid, stair_z) for k in (1, 2)]
                cols.append(kinds)
            drops = sum(1 for kinds in cols if all(k == "drop" for k in kinds))
            by_room = by_room or any("room" in kinds for kinds in cols)
            if worst is None or drops > worst:
                worst = drops
        if worst == len(PROBE_ALONG):
            reason = (f"one of its sides opens over an opening of the floor slab under {lid} across its whole width: no "
                      f"stair head there, and {lid}'s own plan draws its stair there or no room lies there (a drop, no "
                      f"floor) ({stage}): not built")
            gone.append(o)
            b.setdefault("openings_not_built", []).append(dict(o, not_built={"by": "code", "rule": RULE,
                                                                             "reason": reason}))
            _finding(b, o["id"], "door_over_void", reason, lid)
        elif worst and worst * 2 > len(PROBE_ALONG):
            reason = (f"one of its sides opens over an opening of the floor slab under {lid} across most of its width "
                      f"({worst} of {len(PROBE_ALONG)} probes) ({stage}): built, to review")
            _finding(b, o["id"], "door_over_void", reason, lid)
        elif by_room:
            reason = (f"the opening of the floor slab under {lid} in front of it (the level below's stair) lies under a "
                      f"room of {lid}'s plan, which draws no stair there ({stage}): the drawn room wins, the door is "
                      f"built; the opening is to review")
        else:
            continue
        notes.append(f"{o['id']}: {reason}")
        warn(f"door check: {o['id']}: {reason}")
    if gone:
        b["openings"] = [o for o in b.get("openings") or [] if not any(o is g for g in gone)]
    return notes
