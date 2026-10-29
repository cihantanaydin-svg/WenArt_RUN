"""The bathroom and WC details of the user's reference photos (29 Oct 2026; lessons UL114: "Look at the details in the
toilet analyze implement into the projects", "As much detail as you can digest"; UL123: "Look how beautiful is this
bathroom"; UL124: "Look how beautiful is this render take inspiration"; docs/reference_details_20261029.md B1-B26):
the rules that give every bathroom and WC the set its style family gets (the family table and the parts:
``wenart.blender.bath_parts``).

What (pure; shapely for the placements):

1. ``plan_building`` (the layout stage, after the room fill): the look of each fixture of a wet room
   (``piece["bath_look"]``). Drawn sanitary ware is fixed equipment (CLAUDE.md furniture rules): its type, position,
   orientation and footprint stay; only its look changes, recorded with the family, the rule and the reason:
   - a WC: wall-hung with its flush plate in the wall-hung families (B1), else as fitted;
   - a washbasin: the family's floating vanity (stone slab B3, fluted B12, curved B21, with its basin B15 / B23 and its
     top's material B13) where the drawn basin is a vanity's size (``bath_parts.vanity_fits``: the drawing has room for
     it), else as drawn (the reason says why);
   - the storage column (UL102, a tall cabinet): the open lit niche column with its toiletries (B5);
   - a shower: the walk-in enclosure with its fittings (B16), every family;
   - every piece: the family's fixture finish and the room's towel colour (B26).
   A made-to-measure piece (``made_to_measure``) is built from code by design (``fit.bath_made_fit``). One feature wall
   per room (B13 or B24): the fluted wall behind a wall-hung WC is planned here (its span on the WC's wall, clear of
   the openings and the other pieces' backs), so the WC hangs on its face (``wall_offset_m``).
2. ``dress`` (the decor stage, after the professional dressing): the room's accessories as decor items
   (``added_by_ai``, ``method: rule``, ``rule``, the lesson and the reason; real sizes; each placed by code: inside the
   room, on a wall stretch clear of the doors and windows, off the other pieces and the door swings):
   - B2 a paper holder on the wall beside every WC (a side wall within reach, else its back wall) at 0.70 m and a brush
     on the floor beside it;
   - B7 a towel rail on a free wall of every bathroom (near the bath or the shower, never in the shower or behind the
     door), B18 a towel shelf beside it, B25 towel bars at the door and at the shower;
   - B4 / B14 / B22 the basin's mirror in the family's kind (an LED band, backlit, a round oak frame; the framed one of
     the classic families stays);
   - B13 the feature panel behind a fluted vanity, B24 the fluted wall behind the WC (planned in step 1);
   - B9 the room's ceiling lights as recessed downlights (square for the modern families) and, where the ceiling is
     flat and high enough, a cove light over the vanity wall that wraps the corner along the shower's wall (B17);
   - B26 every towel in the room's accent colour (``towel_colour``).
   ``building["bath_details"]`` records the family, the rooms' finish (B20: the door helper reads ``room_finish``),
   their towel colour, feature wall and what each got or why not.
3. ``review`` (model review M26, Argus U30): a wet room missing the set its family gets: a WC without its paper
   holder or brush, a basin without its mirror or (where the drawing has room) its vanity, a bathroom without a towel
   rail or a towel shelf or bar, a wall-hung family's WC or a shower not built in the family's design, a mirror not of
   the family's kind. Minor; kind ``taste``.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G
from wenart.blender import bath_parts as BT
from wenart.furniture import placer

RULE = BT.RULE
LESSONS = BT.LESSONS
REVIEW_CHECK = "M26"
ARGUS_CHECK = "U30"
REACH_M = 1.0                    # an accessory this close to its WC or basin belongs to it
SIDE_WALL_M = 0.45               # a wall this close to a WC's side is its side wall (the paper holder's place)
HOLDER_FWD_M = 0.12              # the paper holder this far behind the WC's front edge on the side wall
BRUSH_GAP_M = 0.06
EDGE_M = 0.03                    # a wall item this far inside its wall stretch's ends
OPENING_MARGIN_M = 0.05
PIECE_GAP_M = 0.02
COVE_SIDE_M = 0.30               # the cove band runs this far past the vanity at both ends
WC_PANEL_SIDE_M = 0.25           # the fluted wall runs this far past the WC at both ends (B24)
WC_PANEL_MIN_EXTRA_M = 0.10
TOWEL_BAR_DOOR_GAP_M = 0.05
TOWEL_BAR_REACH_M = 1.2          # a towel bar within this of the door's or the shower's edge (B25)
TALL_FOR_SHELF_M = 1.3           # a piece taller than this stands under the towel shelf's height


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _wet(room: dict) -> bool:
    return room.get("room_type") in BT.WET_ROOM_TYPES and len(room.get("polygon") or []) >= 3


def _built(f: dict) -> bool:
    return f.get("build") is not False and bool(f.get("footprint")) and f.get("type") not in (None, "unknown")


def _pieces(building: dict, room_id: str, types=None) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and _built(f)
            and (types is None or f.get("type") in types)]


def _level(building: dict, level_id) -> dict:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})


def _ceiling(building: dict, room: dict) -> float:
    return float(_level(building, room.get("level_id")).get("ceiling_height") or 2.7)


def _decor_module():
    """``wenart.furniture.decor``, imported by name: the decor stage's (``dress``) only; the layout stage's planner
    (``plan_building``) and the review never need it, so the layout's code list stays its own."""
    import importlib

    return importlib.import_module("wenart.furniture.decor")


def _decor_mode(building: dict) -> str:
    """= ``decor_ai.decor_mode``: ``off`` for ``brief.decor: false``, else ``on``."""
    value = ((building.get("project") or {}).get("brief") or {}).get("decor", True)
    return "off" if value is False or str(value).strip().lower() in ("false", "off", "none", "no") else "on"


def _flat_ceiling(building: dict, room: dict) -> bool:
    D = _decor_module()

    try:
        return not D.ceiling_planes(building, room["level_id"])
    except Exception:  # noqa: BLE001 - no roof model: a flat ceiling
        return True


def _front(f: dict) -> tuple[float, tuple[float, float]]:
    """``(rotation, (width along the wall, depth))`` of a piece in the frame of its front."""
    return placer.front_frame(f["footprint"], f.get("front_deg"))


def _frame(f: dict):
    """``(centre, u along the piece's width, f into the room (its front), width, depth)``."""
    rot, (w, d) = _front(f)
    r = math.radians(rot)
    u = (math.cos(r), math.sin(r))
    fwd = (math.sin(r), -math.cos(r))                 # local -Y: the front
    c = (float(f["footprint"]["center"][0]), float(f["footprint"]["center"][1]))
    return c, u, fwd, w, d


def _poly(f: dict):
    return placer.piece_from_furniture(f).polygon()


def _box(c, u, n, w: float, d: float):
    """A ``w`` (along ``u``) x ``d`` (along ``n``) rectangle centred on ``c``."""
    from shapely.geometry import Polygon

    hw, hd = w / 2.0, d / 2.0
    return Polygon([(c[0] - u[0] * hw - n[0] * hd, c[1] - u[1] * hw - n[1] * hd),
                    (c[0] + u[0] * hw - n[0] * hd, c[1] + u[1] * hw - n[1] * hd),
                    (c[0] + u[0] * hw + n[0] * hd, c[1] + u[1] * hw + n[1] * hd),
                    (c[0] - u[0] * hw + n[0] * hd, c[1] - u[1] * hw + n[1] * hd)])


def _segment_at(ctx, point, normal=None, max_dist: float = 0.15) -> Optional[int]:
    """The room boundary segment nearest ``point`` within ``max_dist`` (its inward normal along ``normal`` when given)."""
    best = None
    for k, (a, b) in enumerate(ctx.segments):
        dist = G.point_segment_distance(point, a, b)
        if dist > max_dist:
            continue
        if normal is not None:
            n = ctx.segment_normal(k)
            if n[0] * normal[0] + n[1] * normal[1] < 0.9:
                continue
        if best is None or dist < best[0]:
            best = (dist, k)
    return None if best is None else best[1]


def _seg(ctx, k: int):
    a, b = ctx.segments[k]
    length = G.distance(a, b)
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    return a, u, ctx.segment_normal(k), length


def _t_of(ctx, k: int, p) -> float:
    a, u, _n, _l = _seg(ctx, k)
    return (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]


def _opening_spans(ctx, k: int) -> list[tuple[float, float]]:
    from wenart.furniture import room_fill as RF

    return RF._opening_spans(ctx, k)


def _span_free(ctx, k: int, t0: float, t1: float, openings: bool = True) -> bool:
    _a, _u, _n, length = _seg(ctx, k)
    if t0 < EDGE_M - 1e-9 or t1 > length - EDGE_M + 1e-9:
        return False
    if openings and any(s0 - OPENING_MARGIN_M < t1 and s1 + OPENING_MARGIN_M > t0 for s0, s1 in _opening_spans(ctx, k)):
        return False
    return True


def _evidence(text: str) -> list[dict]:
    return [{"file": "rule", "method": "inferred", "confidence": 0.7, "model": "rule", "pass": 1, "text": text}]


def _clear(poly, others, ctx, swings: bool = True) -> bool:
    """``poly`` inside the room, off the other pieces (``others``: polygons) and (``swings``) the door swings."""
    if not ctx.polygon.buffer(0.005).contains(poly):
        return False
    if any(poly.intersects(q.buffer(PIECE_GAP_M)) for q in others):
        return False
    if swings and any(z.swing is not None and not z.swing.is_empty and poly.intersection(z.swing).area > 1e-6
                      for z in ctx.doors):
        return False
    return True


def family_spec(building: dict, style: Optional[dict] = None) -> tuple[dict, str]:
    """The family's bathroom row (``bath_parts.spec_of``) of the style, else of the building's recorded details."""
    fam = BT.family_name(style) or ((building.get("bath_details") or {}).get("family"))
    return BT.spec_of(fam)


def room_finish(building: dict, room_id: str) -> Optional[str]:
    """B20: the fixture finish of a wet room (black, brass, chrome) the door helper reads for its door frames; None for
    a room without a bathroom record."""
    rec = ((building.get("bath_details") or {}).get("rooms") or {}).get(room_id)
    return rec.get("finish") if isinstance(rec, dict) else None


def _record(building: dict, spec: dict, why: str) -> dict:
    rec = building.setdefault("bath_details", {})
    rec.update({"rule": RULE, "lessons": list(LESSONS), "family": spec["family"], "why": why})
    rec.setdefault("rooms", {})
    rec.setdefault("notes", [])
    return rec


# --------------------------------------------------------------------------
# 1. The fixtures' looks (the layout stage)
# --------------------------------------------------------------------------

def _base_look(spec: dict, why: str) -> dict:
    return {"family": spec["family"], "finish": spec["finish"], "towel_colour": spec["towel_colour"], "rule": RULE,
            "lessons": list(LESSONS), "source": "inferred", "why": why}


def _drop_mount(piece: dict) -> None:
    """A made-to-measure piece is built from the floor by its own heights: the fit's hanging height goes."""
    if piece.get("mount_bottom_m") is not None:
        piece["bath_look"]["mount_dropped"] = piece.pop("mount_bottom_m")
        piece.pop("mount_source", None)


def vanity_look(piece: dict, spec: dict) -> tuple[Optional[dict], str]:
    """``(look keys, why)`` of a washbasin in the family's floating vanity, or ``(None, why not)``."""
    if spec["vanity"] not in BT.VANITY_KINDS:
        return None, f"the {spec['family']} family keeps the drawn basin's look (its framed classic vanity)"
    if piece.get("front_deg") is None:
        return None, "the basin has no front: no wall to hang a vanity on"
    _rot, (w, d) = _front(piece)
    why_not = BT.vanity_fits(w, d)
    if why_not:
        return None, why_not
    height = piece.get("height")
    top = float(height) if isinstance(height, (int, float)) and 0.75 <= float(height) <= 0.95 else BT.VANITY_TOP_DEFAULT_M
    kind = spec["vanity"]
    basin = spec["basin"] if kind != "stone_slab" else "integrated"
    top_key = BT.PANEL_KEYS.get(str(spec.get("panel") or ""), spec["top_key"]) if kind == "fluted" else spec["top_key"]
    look = {"vanity": kind, "basin": basin, "rounded": bool(spec["rounded"]), "top_key": top_key,
            "top_m": round(top, 3), "made_to_measure": True}
    if kind == "curved":
        look["apron_key"] = BT.PANEL_KEYS.get(str(spec.get("apron") or "terrazzo"), "terrazzo")
    words = {"stone_slab": "a floating vanity with a thick stone top and an integrated basin (B3)",
             "fluted": "a fluted floating vanity" + (" with rounded ends" if spec["rounded"] else "")
                       + f" and a {basin.replace('_', ' ')} basin (B12, B15)",
             "curved": "a curved white floating vanity under a dark stone top in a terrazzo apron, with a white "
                       "vessel basin and a wall spout (B21, B23)"}[kind]
    return look, f"{words} on the drawn {w:.2f} x {d:.2f} m basin (the drawing has room for it)"


def _wc_panel(building: dict, room: dict, wc: dict, pieces: list[dict]) -> Optional[dict]:
    """B24: the fluted wall's span behind a wall-hung WC (on its back wall, ``WC_PANEL_SIDE_M`` past it at both ends,
    clipped to the free stretch between the openings and the other pieces' backs on that wall), or None."""
    ctx = placer.room_context(building, room)
    c, u, fwd, w, d = _frame(wc)
    back = (c[0] - fwd[0] * d / 2.0, c[1] - fwd[1] * d / 2.0)
    k = _segment_at(ctx, back, fwd, 0.10)
    if k is None:
        return None
    a, su, n, length = _seg(ctx, k)
    tc = _t_of(ctx, k, back)
    lo, hi = max(0.0, tc - w / 2.0 - WC_PANEL_SIDE_M), min(length, tc + w / 2.0 + WC_PANEL_SIDE_M)
    blocks = list(_opening_spans(ctx, k))
    for p in pieces:
        if p is wc:
            continue
        pc, pu, pf, pw, pd = _frame(p)
        pback = (pc[0] - pf[0] * pd / 2.0, pc[1] - pf[1] * pd / 2.0)
        if G.point_segment_distance(pback, ctx.segments[k][0], ctx.segments[k][1]) <= 0.30:
            t = _t_of(ctx, k, pc)
            half = abs(pw * (pu[0] * su[0] + pu[1] * su[1])) / 2.0 + abs(pd * (pf[0] * su[0] + pf[1] * su[1])) / 2.0
            blocks.append((t - half, t + half))
    for s0, s1 in blocks:
        if s1 <= tc - w / 2.0 + 1e-6:
            lo = max(lo, s1 + 0.02)
        elif s0 >= tc + w / 2.0 - 1e-6:
            hi = min(hi, s0 - 0.02)
        else:
            return None                                   # the WC stands on an opening or another piece's span
    if hi - lo < w + WC_PANEL_MIN_EXTRA_M - 1e-9:
        return None
    t = (lo + hi) / 2.0
    wp = (a[0] + su[0] * t, a[1] + su[1] * t)
    th = BT.FLUTED_WALL_T_M
    return {"segment": k, "span": [round(lo, 4), round(hi, 4)], "width": round(hi - lo, 4),
            "wall_point": [round(wp[0], 4), round(wp[1], 4)],
            "center": [round(wp[0] + n[0] * th / 2.0, 4), round(wp[1] + n[1] * th / 2.0, 4)],
            "rotation_deg": round(placer._rotation_for_normal(n), 3), "thickness": th, "anchor": wc["id"]}


def plan_room(building: dict, room: dict, spec: dict, why: str) -> dict:
    """In place: the looks of one wet room's fixtures (module docstring, step 1); returns the room's record."""
    pieces = _pieces(building, room["id"])
    rec = {"family": spec["family"], "finish": spec["finish"], "towel_colour": spec["towel_colour"], "pieces": {},
           "feature": None, "feature_why": None}
    vanity_panel = False
    for p in sorted(pieces, key=lambda f: f["id"]):
        look = _base_look(spec, why)
        ftype = p.get("type")
        note = None
        if ftype == "toilet":
            if spec["wc"] == "wall_hung":
                look.update(wc="wall_hung", made_to_measure=True)
                note = "a wall-hung WC with the flush plate of its concealed cistern on the wall (B1)"
            else:
                look.update(wc="close_coupled")
                note = f"the {spec['family']} family keeps a close-coupled WC (as fitted)"
        elif ftype == "washbasin":
            extra, note = vanity_look(p, spec)
            if extra is not None:
                look.update(extra)
                if extra["vanity"] == "fluted" and spec.get("panel"):
                    vanity_panel = True
            else:
                look["vanity"] = "as_drawn"
        elif ftype == "tall_cabinet":
            if spec["column"] == "open_lit":
                look.update(column="open_lit", made_to_measure=True)
                note = "the storage column as an open lit niche column with its toiletries (B5)"
            else:
                note = f"the {spec['family']} family keeps a closed storage column"
        elif ftype == "shower":
            look.update(shower="walk_in", made_to_measure=True)
            note = "a walk-in glass enclosure with a rain head, a hand shower, a mixer and a linear drain (B16)"
        elif ftype not in ("bathtub", "washing_machine"):
            continue
        look["reason"] = f"{note or ftype}; {why} (UL114)"
        p["bath_look"] = look
        if look.get("made_to_measure"):
            _drop_mount(p)
        rec["pieces"][p["id"]] = {k: look[k] for k in ("wc", "vanity", "basin", "column", "shower", "made_to_measure")
                                  if k in look}
        rec["pieces"][p["id"]]["why"] = note
    # one feature wall per room (B13 or B24)
    if vanity_panel:
        rec["feature"], rec["feature_why"] = "vanity_panel", (f"a {spec['panel']} panel behind the fluted vanity, "
                                                              "floor to ceiling (B13)")
    elif spec.get("feature") == "wc_fluted":
        for wc in [p for p in pieces if p.get("type") == "toilet" and BT.bath_look(p).get("wc") == "wall_hung"]:
            panel = _wc_panel(building, room, wc, pieces)
            if panel is None:
                rec["feature_why"] = f"no free wall stretch behind {wc['id']} for the fluted wall (B24)"
                continue
            panel["material"] = f"fluted_{'wood' if spec.get('fluted_key') == 'wood' else 'dark'}"
            wc["bath_look"]["wall_offset_m"] = panel["thickness"]
            rec["feature"], rec["feature_panel"] = "wc_fluted", panel
            rec["feature_why"] = (f"a {panel['material'].replace('_', ' ')} wall {panel['width']:.2f} m wide behind "
                                  f"the WC {wc['id']}, its flush plate and paper holder on it (B24)")
            break
    return rec


def plan_building(building: dict, style: Optional[dict] = None) -> tuple[dict, list[dict]]:
    """In place (module docstring, step 1): every wet room's fixtures in the family's look; ``(building, records)``,
    a record per room (``room_id``, the pieces' looks, the feature wall)."""
    spec, why = family_spec(building, style)
    out = _record(building, spec, why)
    records = []
    for room in building.get("rooms") or []:
        if not _wet(room):
            continue
        rec = plan_room(building, room, spec, why)
        out["rooms"][room["id"]] = rec
        records.append(dict(rec, room_id=room["id"]))
    return building, records


# --------------------------------------------------------------------------
# 2. The accessories (the decor stage)
# --------------------------------------------------------------------------

def _item(room: dict, dtype: str, center, rot: float, size, why: str, spec: dict, new_id: Callable[[str], str],
          anchors: Optional[list] = None, wall_point=None, **extra) -> dict:
    colour = BT.FINISH_COLOUR.get(spec["finish"])
    out = {"id": new_id(room["level_id"]), "kind": "decor", "type": dtype, "level_id": room["level_id"],
           "room_id": room["id"], "asset": None, "host_id": None,
           "source": "added_by_ai", "method": "rule", "rule": RULE, "slot": f"bath:{dtype}", "colour": colour,
           "towel_colour": spec["towel_colour"], "confidence": 0.7, "status": "verified", "evidence": _evidence(why),
           "reason": f"{why} (UL114)", "center": [round(float(v), 4) for v in center],
           "rotation_deg": round(float(rot), 3), "size": [round(float(v), 4) for v in size]}
    if anchors:              # the schema: a list of at least one piece, else no key (a towel rail on a free wall)
        out["anchor_ids"] = list(anchors)
    if wall_point is not None:
        out["wall_point"] = [round(float(wall_point[0]), 4), round(float(wall_point[1]), 4)]
    out.update(extra)
    return out


def panel_offset(rec: Optional[dict], k: int, t0: float, t1: float) -> float:
    """The thickness of the room's fluted wall (B24) when a wall item's span ``t0..t1`` on segment ``k`` lies over it,
    else 0: the item hangs on the panel's face."""
    pnl = (rec or {}).get("feature_panel") if (rec or {}).get("feature") == "wc_fluted" else None
    if not pnl or pnl.get("segment") != k:
        return 0.0
    lo, hi = pnl["span"]
    return float(pnl["thickness"]) if t0 < hi and t1 > lo else 0.0


def _wall_place(ctx, k: int, t: float, size, bottom: float, offset: float = 0.0):
    """``(centre with its height, rotation, wall point, footprint)`` of a wall item ``size`` at ``t`` along segment
    ``k`` (its back ``offset`` in front of the wall face: a feature wall)."""
    a, u, n, _l = _seg(ctx, k)
    w, d = float(size[0]), float(size[1])
    wp = (a[0] + u[0] * t, a[1] + u[1] * t)
    off = offset + d / 2.0 + 0.002
    c = (wp[0] + n[0] * off, wp[1] + n[1] * off)
    return [c[0], c[1], bottom], placer._rotation_for_normal(n), wp, _box(c, u, n, w, d)


def _others(pieces: list[dict], skip=()) -> list:
    out = []
    for p in pieces:
        if p.get("id") in skip:
            continue
        try:
            out.append(_poly(p))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _item_box(d: dict):
    """The plan box of a decor item (its width along its rotation, its depth)."""
    r = math.radians(float(d.get("rotation_deg") or 0.0))
    return _box(d["center"][:2], (math.cos(r), math.sin(r)), (math.sin(r), -math.cos(r)), float(d["size"][0]),
                float(d["size"][1]))


def _decor_boxes(items: list[dict], types) -> list:
    return [_item_box(d) for d in items
            if d.get("type") in types and len(d.get("size") or []) >= 2 and d.get("center")]


def _paper_holder(room, wc, ctx, pieces, spec, new_id, panel) -> tuple[Optional[dict], str]:
    """B2: the paper holder of a WC (module docstring); ``(item, why)``."""
    c, u, fwd, w, d = _frame(wc)
    size = BT.PAPER_HOLDER_SIZE
    bottom = BT.PAPER_HOLDER_Z_M - size[2] / 2.0
    others = _others(pieces, {wc["id"]})
    cands = []
    for side in (1.0, -1.0):                           # a side wall within reach, at the bowl's front part
        edge = (c[0] + u[0] * side * w / 2.0, c[1] + u[1] * side * w / 2.0)
        k = _segment_at(ctx, edge, (-u[0] * side, -u[1] * side), SIDE_WALL_M)
        if k is not None:
            p = (c[0] + fwd[0] * (d / 2.0 - HOLDER_FWD_M), c[1] + fwd[1] * (d / 2.0 - HOLDER_FWD_M))
            cands.append((k, _t_of(ctx, k, p), 0.0, "on the side wall beside the WC"))
    back = (c[0] - fwd[0] * d / 2.0, c[1] - fwd[1] * d / 2.0)
    kb = _segment_at(ctx, back, fwd, 0.10)
    if kb is not None:
        tb = _t_of(ctx, kb, back)
        for side in (1.0, -1.0):
            t = tb + side * (w / 2.0 + 0.08 + size[0] / 2.0)
            on_panel = panel is not None and panel["segment"] == kb and panel["span"][0] <= t - size[0] / 2.0 \
                and t + size[0] / 2.0 <= panel["span"][1]
            cands.append((kb, t, panel["thickness"] if on_panel else 0.0,
                          "on the fluted wall beside the WC" if on_panel else "on the wall beside the WC"))
    for k, t, off, where in cands:
        if not _span_free(ctx, k, t - size[0] / 2.0, t + size[0] / 2.0):
            continue
        centre, rot, wp, poly = _wall_place(ctx, k, t, size, bottom, off)
        if not _clear(poly, others, ctx):
            continue
        why = f"a paper holder {where} {wc['id']} at {BT.PAPER_HOLDER_Z_M:.2f} m (B2)"
        return _item(room, "toilet_paper_holder", centre, rot, size, why, spec, new_id, [wc["id"]],
                     None if off or k != kb else wp), "ok"
    return None, f"no free wall within reach of {wc['id']} for its paper holder"


def _brush(room, wc, ctx, pieces, spec, new_id) -> tuple[Optional[dict], str]:
    c, u, fwd, w, d = _frame(wc)
    size = BT.TOILET_BRUSH_SIZE
    others = _others(pieces, {wc["id"]}) + [_poly(wc)]
    back = (c[0] - fwd[0] * d / 2.0, c[1] - fwd[1] * d / 2.0)
    for side in (-1.0, 1.0):
        for depth, gap in ((0.10, BRUSH_GAP_M), (0.10, 0.012), (0.25, BRUSH_GAP_M)):
            off = w / 2.0 + gap + size[0] / 2.0
            p = (back[0] + u[0] * side * off + fwd[0] * depth, back[1] + u[1] * side * off + fwd[1] * depth)
            poly = _box(p, u, fwd, size[0], size[1])
            if any(poly.intersects(q.buffer(0.005)) for q in others) or not ctx.polygon.buffer(-0.01).contains(poly):
                continue
            if any(z.swing is not None and not z.swing.is_empty and poly.intersects(z.swing) for z in ctx.doors) \
                    or any(poly.intersects(z.zone) for z in ctx.doors):
                continue
            rot = float(_front(wc)[0])
            why = f"a toilet brush in its holder on the floor beside the WC {wc['id']} (B2)"
            return _item(room, "toilet_brush", [p[0], p[1], 0.0], rot, size, why, spec, new_id, [wc["id"]]), "ok"
    return None, f"no free floor beside {wc['id']} for its brush"


def _wall_spot(building, room, ctx, size, pieces, near=None, near_max=None, bottom: float = 0.0,
               avoid=(), tall_only: Optional[float] = None, swings: bool = True, rec: Optional[dict] = None):
    """The first wall place for a wall item ``size`` (``room_fill.wall_spots``: clear of the openings) whose footprint
    is off the pieces (``tall_only``: only those taller than it) and the door swings; ``(centre, rot, wp, k)``."""
    from wenart.furniture import room_fill as RF
    from wenart.blender import parametric as P

    blockers = []
    for p in pieces:
        if tall_only is not None:
            try:
                if float(P.piece_bbox(p)[2]) <= tall_only:
                    continue
            except (KeyError, TypeError, ValueError):
                pass
        try:
            blockers.append(_poly(p))
        except (KeyError, TypeError, ValueError):
            continue
    blockers += list(avoid)
    for s in RF.wall_spots(building, room, [tuple(size[:2])], near, near_max)[:200]:
        k = s["segment"]
        a, u, n, _l = _seg(ctx, k)
        c = s["center"]
        t = _t_of(ctx, k, c)
        off = panel_offset(rec, k, t - size[0] / 2.0, t + size[0] / 2.0)
        centre, rot, wp, poly = _wall_place(ctx, k, t, size, bottom, off)
        if _clear(poly, blockers, ctx, swings):
            return centre, rot, (None if off else wp), k
    return None


def _towels(building, room, ctx, pieces, items, spec, new_id, rec: Optional[dict] = None
            ) -> tuple[list[dict], list[str]]:
    """B7 / B18 / B25: the towel rail, the towel shelf beside it and the towel bars at the door and the shower."""
    out, notes = [], []
    if room.get("room_type") not in BT.TOWEL_RAIL_ROOM_TYPES:
        return out, notes
    have = {d.get("type") for d in items if d.get("room_id") == room["id"]}
    wet_zone = [p for p in pieces if p.get("type") in ("shower", "bathtub")]
    near = _poly(wet_zone[0]) if wet_zone else None
    decor_walls = _decor_boxes(items, ("mirror",))
    rail = None
    if "towel_rail" not in have:
        spot = _wall_spot(building, room, ctx, BT.TOWEL_RAIL_SIZE, pieces, near,
                          bottom=BT.TOWEL_RAIL_BOTTOM_M, avoid=decor_walls, rec=rec)
        if spot is None:
            notes.append(f"{room['id']}: no free wall for a towel rail (B7)")
        else:
            centre, rot, wp, k = spot
            where = f" near the {wet_zone[0]['type']} {wet_zone[0]['id']}" if wet_zone else ""
            rail = _item(room, "towel_rail", centre, rot, BT.TOWEL_RAIL_SIZE,
                         f"a heated towel rail (ladder) on a free wall{where}, never in the shower or behind the door "
                         f"(B7)", spec, new_id, wall_point=wp, segment=k)
            out.append(rail)
    if "towel_shelf" not in have and rail is not None:
        k = rail.pop("segment")
        size = BT.TOWEL_SHELF_SIZE
        t_rail = _t_of(ctx, k, rail["center"][:2])
        blockers = [_poly(p) for p in pieces if _taller(p, TALL_FOR_SHELF_M)] + decor_walls
        placed = None
        for side in (1.0, -1.0):
            t = t_rail + side * (BT.TOWEL_RAIL_SIZE[0] / 2.0 + 0.10 + size[0] / 2.0)
            if not _span_free(ctx, k, t - size[0] / 2.0, t + size[0] / 2.0):
                continue
            off = panel_offset(rec, k, t - size[0] / 2.0, t + size[0] / 2.0)
            centre, rot, wp, poly = _wall_place(ctx, k, t, size, BT.TOWEL_SHELF_BOTTOM_M, off)
            if _clear(poly, blockers, ctx, swings=False):
                placed = (centre, rot, None if off else wp)
                break
        if placed is None:
            spot = _wall_spot(building, room, ctx, size, pieces, _item_box(rail).buffer(0.01),
                              bottom=BT.TOWEL_SHELF_BOTTOM_M, avoid=decor_walls + [_item_box(rail)],
                              tall_only=TALL_FOR_SHELF_M, swings=False, rec=rec)
            placed = spot[:3] if spot else None
        if placed is None:
            notes.append(f"{room['id']}: no wall beside the towel rail for a towel shelf (B18)")
        else:
            out.append(_item(room, "towel_shelf", placed[0], placed[1], size,
                             "a towel shelf with a rail under it beside the towel rail (B18)", spec, new_id,
                             wall_point=placed[2]))
    elif rail is not None:
        rail.pop("segment", None)
    # B25: towel bars at the door and at the shower
    bars = 0
    if "towel_bar" not in have:
        size = BT.TOWEL_BAR_SIZE
        taken = [_item_box(d) for d in out] + decor_walls
        targets = []
        if ctx.doors:
            door = ctx.doors[0]
            from shapely.geometry import Point
            targets.append(("door", Point(door.inner_point).buffer(door.width / 2.0 + TOWEL_BAR_DOOR_GAP_M),
                            f"beside the door {door.id}"))
        showers = [p for p in pieces if p.get("type") == "shower"]
        if showers:
            targets.append(("shower", _poly(showers[0]), f"at the shower {showers[0]['id']}"))
        for what, near_poly, where in targets:
            spot = _wall_spot(building, room, ctx, size, pieces, near_poly, TOWEL_BAR_REACH_M,
                              bottom=BT.TOWEL_BAR_BOTTOM_M, avoid=taken, rec=rec)
            if spot is None:
                notes.append(f"{room['id']}: no free wall {where} for a towel bar (B25)")
                continue
            centre, rot, wp, k = spot
            bar = _item(room, "towel_bar", centre, rot, size, f"a towel bar {where} (B25)", spec, new_id,
                        wall_point=wp)
            out.append(bar)
            taken.append(_item_box(bar))
            bars += 1
    return out, notes


def _taller(p: dict, h: float) -> bool:
    from wenart.blender import parametric as P

    try:
        return float(P.piece_bbox(p)[2]) > h
    except (KeyError, TypeError, ValueError):
        return True


def _mirrors(building, room, pieces, items, spec, rec) -> list[str]:
    """B4 / B14 / B22: the basins' mirrors in the family's kind (in place); notes."""
    notes = []
    kind = spec["mirror"]
    if kind == "framed":
        return notes
    fixture = {"led": "led_mirror", "backlit": "backlit_mirror", "round_oak": "round_mirror"}[kind]
    basins = {p["id"]: p for p in pieces if p.get("type") == "washbasin"}
    for d in items:
        if d.get("type") != "mirror" or d.get("room_id") != room["id"]:
            continue
        anchor = next((a for a in d.get("anchor_ids") or [] if a in basins), None)
        if anchor is None:
            continue
        basin = basins[anchor]
        _rot, (bw, _bd) = _front(basin)
        look = BT.bath_look(basin)
        w = float(d["size"][0])
        if fixture == "backlit_mirror":
            w = min(BT.BACKLIT_MIRROR_MAX_W, max(w, 0.9 * bw))
        elif fixture == "round_mirror":
            w = min(BT.ROUND_MIRROR_D_M[1], max(BT.ROUND_MIRROR_D_M[0], min(w, 0.85 * bw + 0.1)))
        d.update(fixture=fixture, asset=None, size=[round(w, 3)] + list(d["size"][1:]),
                 rounded=bool(spec.get("mirror_round")) if fixture == "backlit_mirror" else None)
        if look.get("basin") in BT.VESSEL_BASINS:
            d["gap_m"] = 0.40                             # over a vessel and its tall mixer
        if rec.get("feature") == "vanity_panel" and d.get("wall_point") and look.get("vanity") == "fluted":
            r = math.radians(float(d.get("rotation_deg") or 0.0))
            nx, ny = math.sin(r), -math.cos(r)
            t = BT.FEATURE_PANEL_T_M
            d["wall_point"] = [round(d["wall_point"][0] + nx * t, 4), round(d["wall_point"][1] + ny * t, 4)]
            d["center"] = [round(d["center"][0] + nx * t, 4), round(d["center"][1] + ny * t, 4)] + list(d["center"][2:])
        d["reason"] = f"{d.get('reason') or 'mirror'}; the {spec['family']} family's {kind.replace('_', ' ')} mirror " \
                      f"(UL114 B4, UL123 B14, UL124 B22)"
        d["bath_detail"] = RULE
        notes.append(f"{room['id']}: {d.get('id')} a {kind.replace('_', ' ')} mirror over {anchor}")
    return notes


def _lights(building, room, items, spec) -> list[str]:
    """B9: the room's ceiling lights (the rule's, on a flat ceiling) as recessed downlights, square in the modern
    families (in place)."""
    notes = []
    flat = _ceiling(building, room)
    if not _flat_ceiling(building, room):
        return notes
    square = str(spec.get("downlight") or "").startswith("square")
    for d in items:
        if d.get("room_id") != room["id"] or d.get("type") != "ceiling_light" or d.get("slope_mount"):
            continue
        if d.get("fixture") not in (None, "downlight"):
            continue
        size = BT.SQUARE_DOWNLIGHT_SIZE if square else (0.09, 0.09, 0.012)
        d.update(fixture="downlight", size=list(size), center=[*d["center"][:2], round(flat - size[2], 3)],
                 asset=None)
        if square:
            d["trim"] = spec["downlight"]
        d["reason"] = f"{d.get('reason') or 'light'}; a recessed {'square ' if square else ''}downlight (UL114 B9)"
        notes.append(f"{room['id']}: {d.get('id')} a recessed {'square ' if square else ''}downlight")
    return notes


def _cove(building, room, ctx, pieces, spec, new_id) -> tuple[list[dict], list[str]]:
    """B9 / B17: the cove light over the vanity wall, wrapping the corner along the shower's wall."""
    out, notes = [], []
    if not spec.get("cove"):
        return out, notes
    ceiling = _ceiling(building, room)
    if ceiling < BT.COVE_MIN_CEILING_M - 1e-9 or not _flat_ceiling(building, room):
        notes.append(f"{room['id']}: no cove light (the ceiling is sloped or under {BT.COVE_MIN_CEILING_M:.2f} m)")
        return out, notes
    basins = sorted((p for p in pieces if p.get("type") == "washbasin"),
                    key=lambda p: (not BT.bath_look(p).get("made_to_measure"), p["id"]))
    for basin in basins[:1]:
        c, u, fwd, w, d = _frame(basin)
        back = (c[0] - fwd[0] * d / 2.0, c[1] - fwd[1] * d / 2.0)
        k = _segment_at(ctx, back, fwd, 0.10)
        if k is None:
            notes.append(f"{room['id']}: the basin {basin['id']} is not on a wall: no cove")
            continue
        a, su, n, length = _seg(ctx, k)
        tc = _t_of(ctx, k, back)
        lo, hi = max(0.0, tc - w / 2.0 - COVE_SIDE_M), min(length, tc + w / 2.0 + COVE_SIDE_M)
        depth, drop = BT.COVE_DEPTH_M, BT.COVE_DROP_M
        corners = []
        # B17: a shower on the next wall at a corner the band reaches: the band runs into that corner
        for sh in (p for p in pieces if p.get("type") == "shower"):
            sc, su2, sf, sw, sd = _frame(sh)
            sback = (sc[0] - sf[0] * sd / 2.0, sc[1] - sf[1] * sd / 2.0)
            k2 = _segment_at(ctx, sback, sf, 0.15)
            if k2 is None or k2 == k:
                continue
            a2, u2, n2, l2 = _seg(ctx, k2)
            b = (a[0] + su[0] * length, a[1] + su[1] * length)
            b2 = (a2[0] + u2[0] * l2, a2[1] + u2[1] * l2)
            if G.distance(b, a2) < 0.05 and length - hi < 1.0:          # our end meets the shower wall's start
                hi = length
                t0, t1 = depth, min(l2, _t_of(ctx, k2, sc) + sw / 2.0 + 0.05)
                corners.append((k2, t0, t1, sh))
            elif G.distance(a, b2) < 0.05 and lo < 1.0:                  # our start meets the shower wall's end
                lo = 0.0
                t0, t1 = max(0.0, _t_of(ctx, k2, sc) - sw / 2.0 - 0.05), l2 - depth
                corners.append((k2, t0, t1, sh))
        t = (lo + hi) / 2.0
        span = hi - lo
        wp = (a[0] + su[0] * t, a[1] + su[1] * t)
        centre = [wp[0] + n[0] * depth / 2.0, wp[1] + n[1] * depth / 2.0, round(ceiling - drop, 3)]
        first = _item(room, "cove_light", centre, placer._rotation_for_normal(n), (span, depth, drop),
                      f"a lowered ceiling band with an indirect LED line over the vanity wall of {basin['id']} (B9)",
                      spec, new_id, [basin["id"]])
        out.append(first)
        for k2, t0, t1, sh in corners:
            if t1 - t0 < 0.3:
                continue
            a2, u2, n2, _l2 = _seg(ctx, k2)
            tm = (t0 + t1) / 2.0
            wp2 = (a2[0] + u2[0] * tm, a2[1] + u2[1] * tm)
            c2 = [wp2[0] + n2[0] * depth / 2.0, wp2[1] + n2[1] * depth / 2.0, round(ceiling - drop, 3)]
            out.append(_item(room, "cove_light", c2, placer._rotation_for_normal(n2), (t1 - t0, depth, drop),
                             f"the cove light wraps the corner along the shower wall of {sh['id']} (B17)", spec,
                             new_id, [sh["id"]], wraps=first["id"]))
    return out, notes


def _feature_panels(building, room, ctx, pieces, spec, rec, new_id) -> tuple[list[dict], list[str]]:
    """B13 (the panel behind the fluted vanity) or B24 (the fluted wall behind the WC, planned by ``plan_room``)."""
    out, notes = [], []
    ceiling = _ceiling(building, room)
    if rec.get("feature") == "wc_fluted" and rec.get("feature_panel"):
        pnl = rec["feature_panel"]
        out.append(_item(room, "feature_panel", [*pnl["center"], 0.0], pnl["rotation_deg"],
                         (pnl["width"], pnl["thickness"], round(ceiling - 0.005, 3)), rec["feature_why"], spec, new_id,
                         [pnl["anchor"]], material=pnl["material"]))
    elif rec.get("feature") == "vanity_panel":
        for basin in (p for p in pieces if p.get("type") == "washbasin"
                      and BT.bath_look(p).get("vanity") == "fluted"):
            c, u, fwd, w, d = _frame(basin)
            back = (c[0] - fwd[0] * d / 2.0, c[1] - fwd[1] * d / 2.0)
            k = _segment_at(ctx, back, fwd, 0.10)
            if k is None:
                continue
            _a, _su, n, _l = _seg(ctx, k)
            t = BT.FEATURE_PANEL_T_M
            centre = [back[0] + n[0] * t / 2.0, back[1] + n[1] * t / 2.0, 0.0]
            out.append(_item(room, "feature_panel", centre, placer._rotation_for_normal(n),
                             (w, t, round(ceiling - 0.005, 3)), rec["feature_why"], spec, new_id, [basin["id"]],
                             material=spec.get("panel") or "terrazzo"))
            break
    return out, notes


def dress(building: dict, style: Optional[dict], new_id: Callable[[str], str]) -> tuple[dict, list[str]]:
    """In place (module docstring, step 2): every wet room's accessories; ``(building, notes)``. Idempotent: a room
    that has an accessory of a kind keeps it and gets no second one."""
    D = _decor_module()

    spec, why = family_spec(building, style)
    rec_all = _record(building, spec, why)
    decor = building.setdefault("decor", [])
    notes: list[str] = []
    for room in building.get("rooms") or []:
        if not _wet(room) or not D.room_takes_decor(room):
            continue
        rec = rec_all["rooms"].get(room["id"])
        if rec is None:                                   # the layout stage did not plan it: plan it now
            rec = plan_room(building, room, spec, why)
            rec_all["rooms"][room["id"]] = rec
        ctx = placer.room_context(building, room)
        pieces = _pieces(building, room["id"])
        mine = [d for d in decor if d.get("room_id") == room["id"]]
        have = {d.get("type") for d in mine}
        made: list[dict] = []
        panel = rec.get("feature_panel") if rec.get("feature") == "wc_fluted" else None
        for wc in (p for p in pieces if p.get("type") == "toilet"):
            held = {d.get("type") for d in mine if wc["id"] in (d.get("anchor_ids") or [])}
            if "toilet_paper_holder" not in held:
                item, w = _paper_holder(room, wc, ctx, pieces, spec, new_id, panel)
                if item is not None:
                    made.append(item)
                else:
                    notes.append(f"{room['id']}: {w}")
            if "toilet_brush" not in held:
                item, w = _brush(room, wc, ctx, pieces, spec, new_id)
                if item is not None:
                    made.append(item)
                else:
                    notes.append(f"{room['id']}: {w}")
        towels, more = _towels(building, room, ctx, pieces, mine + made, spec, new_id, rec)
        made += towels
        notes += more
        if "feature_panel" not in have:
            panels, more = _feature_panels(building, room, ctx, pieces, spec, rec, new_id)
            made += panels
            notes += more
        notes += _mirrors(building, room, pieces, mine, spec, rec)
        notes += _lights(building, room, mine, spec)
        if "cove_light" not in have:
            coves, more = _cove(building, room, ctx, pieces, spec, new_id)
            made += coves
            notes += more
        decor.extend(made)
        rec["decor"] = sorted({d["type"] for d in made} | {d.get("type") for d in mine
                                                            if d.get("bath_detail") or d.get("rule") == RULE})
    rec_all["notes"] = list(rec_all.get("notes") or []) + notes
    return building, notes


# --------------------------------------------------------------------------
# 3. The review (model review M26, Argus U30)
# --------------------------------------------------------------------------

def _near(item: dict, piece: dict, reach: float = REACH_M) -> bool:
    if piece["id"] in (item.get("anchor_ids") or []) or item.get("host_id") == piece["id"]:
        return True
    c = item.get("center") or []
    if len(c) < 2:
        return False
    return G.distance((float(c[0]), float(c[1])), tuple(piece["footprint"]["center"][:2])) <= reach + 1e-9


def review(building: dict, check: str = REVIEW_CHECK) -> tuple[list[dict], int]:
    """M26 / U30 (module docstring, step 3; pure): ``(findings, wet rooms checked)``."""
    spec, _why = family_spec(building)
    decor_on = _decor_mode(building) != "off" and bool(building.get("decor"))
    out, n = [], 0

    def f(element, room, message, missing):
        out.append({"check": check, "severity": "minor", "target": element, "room_id": room["id"],
                    "message": message, "missing": missing, "lesson": "UL114",
                    "metrics": {"model_review": check.startswith("M"), "rule": RULE, "lesson": "UL114",
                                "family": spec["family"], "missing": missing}})

    for room in building.get("rooms") or []:
        if not _wet(room):
            continue
        n += 1
        pieces = _pieces(building, room["id"])
        items = [d for d in building.get("decor") or [] if d.get("room_id") == room["id"]]
        for wc in (p for p in pieces if p.get("type") == "toilet"):
            if spec["wc"] == "wall_hung" and BT.bath_look(wc).get("wc") != "wall_hung":
                f(wc["id"], room, f"the WC {wc['id']} in {room['id']} is not the {spec['family']} family's wall-hung "
                                  f"WC with its flush plate (B1)", "wall_hung_wc")
            if decor_on:
                for dtype, word in (("toilet_paper_holder", "paper holder"), ("toilet_brush", "brush")):
                    if not any(d.get("type") == dtype and _near(d, wc) for d in items):
                        f(wc["id"], room, f"the WC {wc['id']} in {room['id']} has no {word} (B2)", dtype)
        for basin in (p for p in pieces if p.get("type") == "washbasin"):
            if decor_on and not any(d.get("type") == "mirror" and _near(d, basin) for d in items):
                f(basin["id"], room, f"the basin {basin['id']} in {room['id']} has no mirror (B4)", "mirror")
            elif decor_on and spec["mirror"] != "framed":
                fixture = {"led": "led_mirror", "backlit": "backlit_mirror", "round_oak": "round_mirror"}[spec["mirror"]]
                mirror = next((d for d in items if d.get("type") == "mirror" and _near(d, basin)), None)
                if mirror is not None and mirror.get("fixture") != fixture:
                    f(basin["id"], room, f"the mirror over {basin['id']} in {room['id']} is not the {spec['family']} "
                                         f"family's {spec['mirror'].replace('_', ' ')} mirror (B4, B14, B22)",
                      "mirror_kind")
            if spec["vanity"] in BT.VANITY_KINDS and basin.get("front_deg") is not None:
                _rot, (w, d) = _front(basin)
                if BT.vanity_fits(w, d) is None and not BT.bath_look(basin).get("made_to_measure"):
                    f(basin["id"], room, f"the basin {basin['id']} in {room['id']} stands bare: the drawing has room "
                                         f"for the {spec['family']} family's floating vanity (B3, B12, B21)", "vanity")
        for sh in (p for p in pieces if p.get("type") == "shower"):
            if BT.bath_look(sh).get("shower") != "walk_in":
                f(sh["id"], room, f"the shower {sh['id']} in {room['id']} has no walk-in enclosure with its fittings "
                                  f"(B16)", "walk_in_shower")
        if decor_on and room.get("room_type") in BT.TOWEL_RAIL_ROOM_TYPES:
            types = {d.get("type") for d in items}
            if "towel_rail" not in types:
                f(room["id"], room, f"the bathroom {room['id']} has no towel rail (B7)", "towel_rail")
            if not types & {"towel_shelf", "towel_bar"}:
                f(room["id"], room, f"the bathroom {room['id']} has no towel shelf or towel bar (B18, B25)",
                  "towel_shelf")
    return out, n
