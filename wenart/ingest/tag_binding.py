"""One binding step for the size tags of a building (27 Nov 2026, audit fix round 5a, rule R09).

What: ``bind(b, texts_by_level) -> list[dict]`` runs after the openings are read (in ``completion``, before the core
rules): every size tag of a level (``tag_grammar.parse``; never one on a dimension or axis layer, never a stair
formula) binds to exactly one opening: the nearest whose wall it faces (within the opening's half width plus
``BIND_REACH_M`` along the wall and the wall's half thickness plus ``BIND_REACH_M`` across it), nearest pairs first, one
tag an opening. A tag a reader already bound to an opening (its evidence holds the tag's text) stays that opening's.
Then the tag sets, in place and logged:

- the pieces of one window it spans: two or more windows on its wall, end to end (gaps under ``PIECE_GAP_M``: a
  mullion), whose extent is the tag's width within ``PIECE_TOL_M``, are one opening (the others go to
  ``openings_merged``): one window block insert split at its mullion is one window;
- the width, when the opening's agrees within ``WIDTH_AGREE_M`` (else the read gap wins and a finding says so);
- the height, when the reading assumed it or gave none (a drawn height that differs by more than
  ``HEIGHT_FINDING_M`` is a finding);
- floor-level glass: a window whose tag is a French window's ('FRANSIZ PENCERE') or at least ``tag_grammar
  .FULL_HEIGHT_CM`` high has its sill at the floor (``sill_height_source`` names the tag, so the architect's W3 keeps
  it as a French window with a guard over a drop); when a balcony, a terrace or a room lies outside it, or its storey
  stands at grade, it is a glazed door (something to step onto: no guard, the space reachable); a tag whose code or
  words say door does the same for a window of door height;
- the door's record: ``door_tags`` and an evidence entry (rule ``own_door_tag``, as before), ``size_tag`` on every
  bound opening.

Why: real15's 'CK3 260/240' glass doors were built as 1.20 m windows, its garage bay 'CK3 350/220' as two windows,
real17's '180/210 FRANSIZ PENCERE' as two 0.8 x 1.2 m windows at sill 0.90, real10's '70/150' bound to nothing: every
reader bound tags its own way, and none set the height and the type from the tag.

How: pure geometry on the building JSON (``completion.Level`` for what lies on either side), no AI.
"""
from __future__ import annotations

import copy
import math
from typing import Callable, Optional

from wenart.ingest import tag_grammar as TG

BIND_REACH_M = 0.8              # a tag binds to an opening within its half width plus this along its wall, and the
#                                 wall's half thickness plus this across it
WIDTH_AGREE_M = 0.15            # the tag sets the width when the read width agrees within this
HEIGHT_FINDING_M = 0.30         # a drawn height this far off the tag's is a finding
HEIGHT_TOL_M = 0.02
PIECE_GAP_M = 0.25              # pieces of one window this close end to end (a mullion) ...
PIECE_TOL_M = 0.15              # ... whose extent is the tag's width within this (or ``PIECE_TOL_SHARE`` of it, the
PIECE_TOL_SHARE = 0.05          # larger: a wide glass wall's frame) are one opening
DOOR_HIGH_CM = TG.DOOR_HIGH_CM
DOOR_LIKE_MAX_W_CM = 120        # a bare tag this narrow and door-high names a door, never a window
AT_GRADE_M = 0.60               # a storey whose floor stands this close to the ground is at grade
DOOR_MAX_W_M = 3.0              # a floor-level glazed opening this wide at most is a balcony's door (a tag saying door:
#                                 any width, a garage or a glass wall)
READER_RULES = ("size_tag", "size_tag_jamb", "size_tag_leaf_door", "own_door_tag", "door_tag", "framed_window")


def _axis(w: dict):
    (ax, ay), (bx, by) = w["start"][:2], w["end"][:2]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return None
    return (ax, ay), ((bx - ax) / length, (by - ay) / length), length


def _local(p, axis) -> tuple[float, float]:
    (ax, ay), (ux, uy), _ = axis
    dx, dy = p[0] - ax, p[1] - ay
    return dx * ux + dy * uy, -dx * uy + dy * ux


def facing_distance(tag_xy, o: dict, wall: dict, reach: float = BIND_REACH_M) -> Optional[float]:
    """The distance from a tag at ``tag_xy`` to opening ``o``'s span when the tag faces the opening's wall within
    ``reach`` (module docstring), else None (pure)."""
    axis = _axis(wall) if wall else None
    c = o.get("center")
    if axis is None or not c:
        return None
    s_t, n_t = _local(tag_xy, axis)
    s_o, n_o = _local(c[:2], axis)
    half = float(o.get("width") or 0.0) / 2.0
    if abs(n_t - n_o) > float(wall.get("thickness") or 0.2) / 2.0 + reach:
        return None
    along = max(0.0, abs(s_t - s_o) - half)
    if along > reach:
        return None
    return math.hypot(along, abs(n_t - n_o))


def kind_agrees(tag: TG.SizeTag, o: dict) -> bool:
    """A tag may bind to an opening of this type (pure): a door takes a door-high tag (``DOOR_HIGH_CM``) or one whose
    code or words say door, never one that says window; a window takes no low tag that says door (a door-high one
    may make it a door); a gap takes any."""
    if o.get("type") == "door":
        return not tag.says_window and (tag.says_door or tag.h_cm >= DOOR_HIGH_CM)
    if o.get("type") == "window":
        # a bare door-high, door-wide tag ('90/210') beside a window is a door's (the generic reader's door-like tag)
        door_like = tag.bare and tag.h_cm >= DOOR_HIGH_CM and tag.w_cm <= DOOR_LIKE_MAX_W_CM
        return not (tag.says_door and tag.h_cm < DOOR_HIGH_CM) and not door_like
    return True


def _reader_tag(o: dict) -> Optional[str]:
    """The tag text a reader bound to ``o`` (its evidence), or None."""
    for e in o.get("evidence") or []:
        if not isinstance(e, dict) or e.get("rule") not in READER_RULES:
            continue
        for k in ("tag", "text"):
            v = e.get(k)
            if v and TG.parse(v) is not None:
                return str(v)
        reason = str(e.get("reason") or "")
        if "'" in reason:
            v = reason.split("'")[1]
            if TG.parse(v) is not None:
                return v
    return None


def merge_pieces(openings: list, walls: dict, tag: TG.SizeTag, tag_xy) -> Optional[tuple[dict, list]]:
    """``(host, pieces)``: the windows on one wall that the tag at ``tag_xy`` spans as one opening split at a mullion
    (module docstring), the host the piece nearest the tag; None when there are fewer than two (pure)."""
    best = None
    for o in openings:
        if o.get("type") != "window" or o.get("virtual") or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        d = facing_distance(tag_xy, o, w) if w else None
        if d is not None and (best is None or d < best[0]):
            best = (d, o, w)
    if best is None:
        return None
    _d, host, wall = best
    axis = _axis(wall)
    s_tag, _n = _local(tag_xy, axis)
    _s, n_host = _local(host["center"][:2], axis)
    spans = []
    for o in openings:
        if o.get("type") != "window" or o.get("virtual") or not o.get("center"):
            continue
        w2 = walls.get(o.get("wall_id"))
        if w2 is None:
            continue
        s, n = _local(o["center"][:2], axis)
        if abs(n - n_host) > float(wall.get("thickness") or 0.2) / 2.0 + 0.05:
            continue
        half = float(o.get("width") or 0.0) / 2.0
        spans.append((s - half, s + half, o))
    spans.sort(key=lambda x: x[0])
    # the chain of pieces end to end through the host
    k = next(i for i, x in enumerate(spans) if x[2] is host)
    lo_i = hi_i = k
    while lo_i > 0 and spans[lo_i][0] - spans[lo_i - 1][1] <= PIECE_GAP_M and spans[lo_i - 1][1] <= spans[lo_i][0] + 0.05:
        lo_i -= 1
    while hi_i < len(spans) - 1 and spans[hi_i + 1][0] - spans[hi_i][1] <= PIECE_GAP_M \
            and spans[hi_i + 1][0] >= spans[hi_i][1] - 0.05:
        hi_i += 1
    # the pieces inside the tag's width around the tag's place on the wall
    chain = spans[lo_i:hi_i + 1]
    chain = [x for x in chain if x[0] >= s_tag - tag.w / 2.0 - PIECE_TOL_M - tag.w / 2.0
             and x[1] <= s_tag + tag.w / 2.0 + PIECE_TOL_M + tag.w / 2.0]
    if len(chain) < 2:
        return None
    lo, hi = min(x[0] for x in chain), max(x[1] for x in chain)
    if abs((hi - lo) - tag.w) > max(PIECE_TOL_M, PIECE_TOL_SHARE * tag.w) \
            or any(x[1] - x[0] > tag.w - 0.2 for x in chain):
        return None
    return host, [x[2] for x in chain if x[2] is not host]


def _merge(b: dict, host: dict, pieces: list, wall: dict, tag: TG.SizeTag, why: str) -> None:
    """Host takes the pieces' extent (in place); the pieces go to ``openings_merged``."""
    axis = _axis(wall)
    spans = []
    for o in [host] + pieces:
        s, _n = _local(o["center"][:2], axis)
        half = float(o.get("width") or 0.0) / 2.0
        spans.append((s - half, s + half))
    lo, hi = min(a for a, _ in spans), max(c for _, c in spans)
    (ax, ay), (ux, uy), _ = axis
    _s, n = _local(host["center"][:2], axis)
    mid = (lo + hi) / 2.0
    cz = host["center"][2:] if len(host["center"]) > 2 else []
    host.setdefault("drawn_width", host.get("width"))
    host["width"] = round(hi - lo, 4)
    host["center"] = [round(ax + ux * mid - uy * n, 4), round(ay + uy * mid + ux * n, 4)] + list(cz)
    ids = {o["id"] for o in pieces}
    b["openings"] = [o for o in b.get("openings") or [] if o.get("id") not in ids]
    for o in pieces:
        b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o), merged_into=host["id"], corrected_by_ai={
            "by": "code", "rule": "size_tag_pieces", "evidence": [host["id"], o["id"]], "reason": why}))
    ev = host.setdefault("evidence", [])
    if isinstance(ev, list):
        ev.append({"file": _ev_file(host), "method": "vector", "confidence": 0.85, "rule": "size_tag_pieces",
                   "tag": tag.text, "note": why})


def _ev_file(o: dict) -> str:
    return next((e.get("file") for e in o.get("evidence") or [] if isinstance(e, dict) and e.get("file")), "") or ""


def _ground_zs(b: dict) -> list[float]:
    try:
        from wenart.ingest import core_rules as CR
        return list(CR.ground_zs(b))
    except Exception:  # noqa: BLE001 - no ground known: nothing stands at grade
        return []


def _outside_kind(level, o: dict) -> list:
    """What lies on either side of ``o`` (``completion.Level.kind_at`` at both faces), [] without its wall."""
    from wenart.ingest import completion as CP

    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return []
    a, u, _ = CP._axis(w)
    n = (-u[1], u[0])
    reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
    c = o["center"]
    return [level.kind_at((c[0] + k * n[0] * reach, c[1] + k * n[1] * reach), "") for k in (1, -1)]


def bind(b: dict, texts_by_level: Optional[dict], warn: Optional[Callable] = None) -> list[dict]:
    """The binding step (module docstring), in place. Returns one record per bound tag
    ``{"opening", "level_id", "tag", "set": [...], "finding"?}``; the findings also go to ``warn``."""
    from wenart.ingest import completion as CP

    out: list[dict] = []
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    grounds = _ground_zs(b)
    for lid, texts in sorted((texts_by_level or {}).items()):
        lv = levels.get(lid)
        if lv is None:
            continue
        tags = []
        for t in texts or []:
            tg = TG.parse(t.get("text"), t.get("layer"))
            if tg is not None and t.get("x") is not None and t.get("y") is not None:
                tags.append((t, tg))
        walls = {w["id"]: w for w in b.get("walls") or [] if w.get("level_id") == lid and w.get("start")}
        ops = [o for o in b.get("openings") or [] if o.get("level_id") == lid and not o.get("virtual")
               and o.get("type") in ("door", "window", "opening") and o.get("center") and o.get("wall_id") in walls
               and not o.get("lift_door")]
        if not ops:
            continue
        # 1. the pieces of one window a tag spans
        for t, tg in tags:
            if tg.says_door and tg.h_cm < DOOR_HIGH_CM:
                continue
            got = merge_pieces([o for o in ops if o.get("id") in {x.get("id") for x in b.get("openings") or []}],
                               walls, tg, (float(t["x"]), float(t["y"])))
            if got is None:
                continue
            host, pieces = got
            why = (f"{host['id']} and {', '.join(p['id'] for p in pieces)} lie end to end in one wall gap and the "
                   f"size tag '{tg.text}' gives their extent ({tg.w:.2f} m): one opening split at its mullion")
            _merge(b, host, pieces, walls[host["wall_id"]], tg, why)
            ops = [o for o in ops if o not in pieces]
            out.append({"opening": host["id"], "level_id": lid, "tag": tg.text, "set": ["pieces"], "reason": why})
        # 2. one tag an opening, nearest facing pairs first; a reader's binding stands
        bound: dict = {}
        used_t: set = set()
        texts_of = {i: str(t.get("text") or "").strip() for i, (t, _tg) in enumerate(tags)}
        for o in ops:
            rt = _reader_tag(o)
            if rt is None:
                continue
            i = next((i for i, s in texts_of.items() if i not in used_t and s == rt.strip()
                      and facing_distance((float(tags[i][0]["x"]), float(tags[i][0]["y"])), o,
                                          walls[o["wall_id"]], 2.0 * BIND_REACH_M) is not None), None)
            bound[o["id"]] = (i, TG.parse(rt), 0.0)
            if i is not None:
                used_t.add(i)
        pairs = []
        for i, (t, tg) in enumerate(tags):
            if i in used_t:
                continue
            for o in ops:
                if o["id"] in bound or not kind_agrees(tg, o):
                    continue
                d = facing_distance((float(t["x"]), float(t["y"])), o, walls[o["wall_id"]])
                if d is not None:
                    # an opening of the tag's width first (within the width tolerance), then the nearest
                    wd = abs(float(o.get("width") or 0) - tg.w)
                    pairs.append((wd > WIDTH_AGREE_M, d, wd, i, o["id"]))
        by_id = {o["id"]: o for o in ops}
        for _off, d, _wd, i, oid in sorted(pairs):
            if i in used_t or oid in bound:
                continue
            used_t.add(i)
            bound[oid] = (i, tags[i][1], d)
        if not bound:
            continue
        level = None
        for oid, (i, tg, d) in sorted(bound.items()):
            o = by_id[oid]
            if tg is None:
                continue
            t = tags[i][0] if i is not None else {}
            if level is None:
                level = CP.Level(b, lid, texts)
            rec = _apply(b, o, tg, t, d, level, lv, grounds)
            if rec.get("finding") and warn:
                warn(f"size tags: {rec['finding']}")
            out.append(dict(rec, level_id=lid))
        out += _same_tag_same_type(lid, bound, by_id)
    return out


SPACE_PROBE_M = 0.30            # a door opens onto an outdoor space when this far past its face lies on it


def space_doors(b: dict) -> list[dict]:
    """The outdoor spaces' door lists after the doors the tags (and the core rules) made (in place): a door of a level
    whose probe past one face lies on an outdoor space of that level (within ``SPACE_PROBE_M``) is one of the space's
    doors (its landing). Returns ``[{"space", "door"}]`` for the doors added."""
    from shapely.geometry import Point, Polygon

    out = []
    walls = {w["id"]: w for w in b.get("walls") or [] if w.get("start") and w.get("end")}
    spaces = [s for s in ((b.get("site") or {}).get("outdoor_spaces") or []) if len(s.get("polygon") or []) >= 3]
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("virtual") or not o.get("center") or o.get("wall_id") not in walls:
            continue
        w = walls[o["wall_id"]]
        axis = _axis(w)
        if axis is None:
            continue
        (_ax, _ay), (ux, uy), _l = axis
        reach = float(w.get("thickness") or 0.2) / 2.0 + SPACE_PROBE_M
        c = o["center"]
        for s in spaces:
            if s.get("level_id") != o.get("level_id") or o["id"] in (s.get("doors") or []):
                continue
            poly = Polygon([tuple(p[:2]) for p in s["polygon"]]).buffer(0.05)
            if any(poly.contains(Point(c[0] - k * uy * reach, c[1] + k * ux * reach)) for k in (1, -1)):
                s.setdefault("doors", []).append(o["id"])
                out.append({"space": s.get("id"), "door": o["id"]})
    return out


def _same_tag_same_type(lid: str, bound: dict, by_id: dict) -> list[dict]:
    """One tag, one product (in place): the openings of a level bound to the same door-high tag that says door or is
    floor-level ('CK3 350/220' on both garage bays) are one type; a window among doors of that tag is a door."""
    out = []
    groups: dict = {}
    for oid, (_i, tg, _d) in bound.items():
        # a product code or words name one product; a bare 'W/H' only a size many doors share
        if tg is not None and not tg.bare and (tg.says_door or tg.floor_level) and tg.h_cm >= DOOR_HIGH_CM:
            groups.setdefault((tg.code, tg.number, tg.w_cm, tg.h_cm), []).append(by_id[oid])
    for _key, members in sorted(groups.items()):
        doors = [o for o in members if o.get("type") == "door"]
        if not doors:
            continue
        for o in members:
            if o.get("type") != "window" or abs(float(o.get("width") or 0.0) - _key[2] / 100.0) > WIDTH_AGREE_M:
                continue                                  # a window the tag does not fit stays as read (a finding)
            st = o.get("size_tag") or {}
            why = (f"{o['id']} carries the size tag '{st.get('text')}' as the door(s) "
                   f"{', '.join(x['id'] for x in doors)} do: one tag, one product, a door")
            o.update(drawn_type=o.get("drawn_type") or "window", type="door", sill_height=None,
                     glazed=bool(o.get("glazed") or st.get("glazed")), operation=o.get("operation")
                     or doors[0].get("operation") or "swing", operation_source="size_tag",
                     adjusted_by_ai={"by": "code", "rule": "size_tag_same_type", "reason": why,
                                     "changed": {"type": "window", "sill_height": o.get("sill_height")}})
            for k in ("french_window", "sill_height_source"):
                o.pop(k, None)
            out.append({"opening": o["id"], "level_id": lid, "tag": st.get("text"), "set": ["type door"],
                        "reason": why})
    return out


SECOND_LEAF_MAX_M = 1.0         # a door narrower than its tag by at most this ...
SECOND_LEAF_NEAR_M = 0.6        # ... with a door leaf symbol this close to its wall, beside it in the tag's span


def second_leaf(b: dict, level, o: dict, tg: TG.SizeTag) -> Optional[dict]:
    """``{"id", "center"}``: the second, smaller leaf of an unequal double door (pure): ``o`` is narrower than its tag
    by more than ``WIDTH_AGREE_M`` and at most ``SECOND_LEAF_MAX_M``, a door leaf symbol (``symbols`` kind door_arc, or
    a door-layer piece of the door's own drawn entity) stands within ``SECOND_LEAF_NEAR_M`` of its wall beside it, inside
    the tag's width, and the widened door stays on its wall and clear of the wall's other openings. ``center`` is the
    widened door's; None otherwise."""
    w = float(o.get("width") or 0.0)
    if not WIDTH_AGREE_M < tg.w - w <= SECOND_LEAF_MAX_M:
        return None
    wall = level.walls.get(o.get("wall_id"))
    axis = _axis(wall) if wall else None
    if axis is None or not o.get("center"):
        return None
    s_o, n_o = _local(o["center"][:2], axis)
    lo, hi = s_o - w / 2.0, s_o + w / 2.0
    rest = tg.w - w
    base = {":".join(str(x).strip().split(":")[:2]) + ":" for e in o.get("evidence") or [] if isinstance(e, dict)
            for x in str(e.get("entity") or "").split(",") if str(x).count(":") >= 2}
    for s in b.get("symbols") or []:
        if s.get("level_id") != o.get("level_id") or s.get("kind") != "door_arc":
            continue
        c = (s.get("footprint") or {}).get("center")
        if not c:
            continue
        sa, sn = _local(c[:2], axis)
        own = any(str(e.get("entity") or "").startswith(tuple(base)) for e in s.get("evidence") or []
                  if isinstance(e, dict)) if base else False
        if abs(sn - n_o) > float(wall.get("thickness") or 0.2) / 2.0 + SECOND_LEAF_NEAR_M and not own:
            continue
        if hi - 0.05 <= sa <= hi + rest + 0.05:
            nlo, nhi = lo, hi + rest
        elif lo - rest - 0.05 <= sa <= lo + 0.05:
            nlo, nhi = lo - rest, hi
        else:
            continue
        a0, _n = _local(wall["start"][:2], axis)
        a1, _n = _local(wall["end"][:2], axis)
        wa, wb = min(a0, a1), max(a0, a1)
        if tg.w > wb - wa + 0.05:
            continue                                    # the door would leave its wall
        if nlo < wa:                                    # the larger leaf read off-centre in the gap: the door keeps
            nlo, nhi = wa, wa + tg.w                    # to its wall
        elif nhi > wb:
            nlo, nhi = wb - tg.w, wb
        clash = False
        for x in level.openings:
            if x is o or x.get("wall_id") != o.get("wall_id") or not x.get("center") or x.get("virtual"):
                continue
            xs, _xn = _local(x["center"][:2], axis)
            if abs(xs - (nlo + nhi) / 2.0) < (nhi - nlo + float(x.get("width") or 0.0)) / 2.0 - 0.02:
                clash = True
        if clash:
            continue
        (ax, ay), (ux, uy), _l = axis
        mid = (nlo + nhi) / 2.0
        cz = list(o["center"][2:])
        return {"id": s.get("id"), "center": [round(ax + ux * mid - uy * n_o, 4), round(ay + uy * mid + ux * n_o, 4)]
                + cz}
    return None


def _apply(b: dict, o: dict, tg: TG.SizeTag, t: dict, d: float, level, lv: dict, grounds: list) -> dict:
    """What the bound tag ``tg`` sets on opening ``o`` (module docstring), in place; its record."""
    done, finding = [], None
    o["size_tag"] = dict(tg.as_dict(), entity=t.get("entity"), distance=round(float(d), 3))
    w = float(o.get("width") or 0.0)
    if abs(w - tg.w) <= WIDTH_AGREE_M:
        if abs(w - tg.w) > 0.005:
            o.setdefault("drawn_width", o.get("width"))
            o["width"] = round(tg.w, 4)
            done.append("width")
    elif o.get("type") == "door" and second_leaf(b, level, o, tg) is not None:
        leaf = second_leaf(b, level, o, tg)
        why = (f"{o['id']}: read {w:.2f} m wide from its larger leaf; its size tag '{tg.text}' gives {tg.w:.2f} m and "
               f"the second, smaller leaf {leaf['id']} is drawn in the same gap: one unequal double door")
        o.setdefault("drawn_width", o.get("width"))
        o.update(width=round(tg.w, 4), center=leaf["center"], operation="double", operation_source="size_tag",
                 leaves=[round(w, 3), round(tg.w - w, 3)])
        o["adjusted_by_ai"] = {"by": "code", "rule": "size_tag_double_leaf", "reason": why,
                               "changed": {"width": w, "operation": "swing"}}
        done.append("width (unequal double door)")
    else:
        # the read gap wins: the tag is recorded and the disagreement is a finding; it sets nothing else (a tag that
        # does not fit the opening may be another opening's)
        finding = (f"{o['id']} is read {w:.2f} m wide, its size tag '{tg.text}' says {tg.w:.2f} m: the read gap is "
                   f"kept")
        return {"opening": o["id"], "tag": tg.text, "set": [], "finding": finding}
    listed = list(o.get("assumed") or []) if isinstance(o.get("assumed"), (list, tuple)) else []
    h = o.get("height")
    h = float(h) if isinstance(h, (int, float)) and not isinstance(h, bool) else None
    if h is None or "height" in listed:
        if h is None or abs(h - tg.h) > HEIGHT_TOL_M:
            o.setdefault("drawn_height", o.get("height"))
            o["height"] = round(tg.h, 4)
            done.append("height")
        o["assumed"] = [f for f in listed if f != "height"]
        listed = o["assumed"]
    elif abs(h - tg.h) > HEIGHT_FINDING_M and not finding:
        finding = f"{o['id']} is drawn {h:.2f} m high, its size tag '{tg.text}' says {tg.h:.2f} m"
    if "height" in done or (h is not None and abs(h - tg.h) <= HEIGHT_TOL_M):
        o["height_source"] = o.get("height_source") or f"size tag '{tg.text}'"
    if o.get("type") == "window" and (tg.floor_level or (tg.says_door and tg.h_cm >= DOOR_HIGH_CM)):
        kinds = _outside_kind(level, o)
        z = lv.get("elevation")
        at_grade = isinstance(z, (int, float)) and any(abs(g - float(z)) <= AT_GRADE_M for g in grounds)
        # a tag saying door on the ground storey (order 0) is a door to the garden whatever ground the reading has
        at_grade = at_grade or (tg.says_door and lv.get("order") == 0 and not lv.get("base_level_id"))
        onto = None
        if "room" in kinds and "balcony" in kinds and tg.w <= DOOR_MAX_W_M + (9.0 if tg.says_door else 0.0):
            onto = "a balcony or terrace"            # a floor-level opening onto an outdoor space is its door
        elif tg.says_door and "room" in kinds and kinds.count("outside") == 1 and at_grade:
            onto = "the ground at grade"
        elif tg.says_door and kinds.count("room") == 2:
            onto = "the next room"
        if onto is not None:
            why = (f"{o['id']}: its size tag '{tg.text}' gives a floor-level "
                   f"{'door' if tg.says_door else 'glazed opening'} ({tg.w:.2f} x {tg.h:.2f} m) onto {onto}: a "
                   f"glazed door")
            o.update(drawn_type=o.get("drawn_type") or "window", type="door", sill_height=None, glazed=True,
                     operation=tg.operation or o.get("operation") or "swing",
                     operation_source="size_tag" if tg.operation else "assumed",
                     adjusted_by_ai={"by": "code", "rule": "size_tag_door", "reason": why,
                                     "changed": {"type": "window", "sill_height": o.get("sill_height")}})
            done.append("type door")
        elif any(k in ("outside", "light_well", "balcony", "void") for k in kinds) or not kinds:
            if o.get("sill_height") is None or float(o.get("sill_height") or 0.0) > 0.0:
                o.setdefault("drawn_sill_height", o.get("sill_height"))
                o["sill_height"] = 0.0
                done.append("sill 0 (French window)")
            o["sill_height_source"] = f"size tag '{tg.text}'"
            o["french_window"] = True
            o["assumed"] = [f for f in listed if f != "sill_height"]
    if o.get("type") == "door" and tg.h_cm >= DOOR_HIGH_CM and not tg.says_window:
        o["door_tags"] = [tg.text]
    ev = o.setdefault("evidence", [])
    if isinstance(ev, list) and not any(isinstance(e, dict) and e.get("rule") in ("own_door_tag", "size_tag_bound")
                                        for e in ev):
        rule = "own_door_tag" if o.get("type") == "door" else "size_tag_bound"
        ev.append({"file": _ev_file(o), "method": "vector", "confidence": 0.9, "rule": rule,
                   "entity": t.get("entity"), "tag": tg.text,
                   "note": f"its size tag '{tg.text}' {d:.2f} m from its span" + (f"; set: {', '.join(done)}"
                                                                                  if done else "")})
    rec = {"opening": o["id"], "tag": tg.text, "set": done}
    if finding:
        rec["finding"] = finding
    return rec
