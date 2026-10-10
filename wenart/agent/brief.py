"""The room brief of the planner (docs/milestone12.md §5.2 D17; §1.4 "the model works blind on raw coordinates").

What: ``room_brief(building, room_id, findings=..., memory=..., image_of=...)`` returns what the planner needs to
decide without reading anything else (it replaces the M11 ``room`` + ``plausibility`` reads):

| part | content |
|---|---|
| ``room`` | id, label, type, area, level, doors (width, swing into this room), windows (sill) |
| ``pieces`` | the BUILT pieces: id, type, source, size ``[w, d]``, height, centre, rotation, ``front_deg`` (never null: a front taken from the rotation is flagged ``front_inferred``), lock state and ``allowed`` (per tool: allowed / why not / move allowance left), group membership, library gap |
| ``not_built`` | ids, types and sizes of the pieces that are not built (in no render, not editable; B5) |
| ``groups`` | the program (``program.room_program``), each group's members, missing partners and G-check results |
| ``free_wall_spans`` | id, wall id, start, end, length, the direction into the room and what may stand there |
| ``findings`` | ``fixable`` (each with the tools that can fix it) and ``not_yours`` (locked, not built, needs review, or no tool) |
| ``memory`` | this room's earlier accepted and rejected edits with reasons, candidates tried, the open checklist |
| ``candidates`` | the solver's top 3 layouts (``solver.solve_room``) with score, terms and a top-down image id |

``classify(findings, ...)`` is the rule that decides "fixable" vs "not yours" (§5.2; real03 run 3: 53 of 73 rejected
edits aimed at pieces no tool may change): a finding is fixable when a tool of ``CHECK_TOOLS[check]`` may act on its
target (a piece tool only when ``allowed`` says so for that piece; a group tool only for a piece in a group; a
re-layout only when the solver has candidates or the room has AI pieces). Unfixable findings are never sent to the
planner as work (the loop gives them as "not yours").

How: the other tracks' functions are called through their frozen contracts (§13.2) and may be stubs: an empty
answer (or an exception, noted in ``notes``) leaves that part empty. ``edit_ops.allowed_edits`` (track G) gives
the lock state; while it answers ``{}`` (its stub) ``allowed_fallback`` applies the M11 rules of CLAUDE.md (fixed
equipment: only a front fix or the U1 fixture fix; drawn pieces: ≤ 0.3 m move, ≤ 1.2 m wall snap, front, real size,
type within the room, not-furniture with evidence; AI pieces: free). Pure apart from ``image_of`` (the caller draws
the candidates' top-down images). Deterministic: pieces, spans and findings in a fixed order.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

SEVERITY_WEIGHT = {"critical": 9.0, "major": 3.0, "minor": 1.0}
SPAN_MIN_M = 0.4                    # shorter free wall pieces are not listed
SPAN_PIECE_GAP_M = 0.15             # a piece within this of a wall occupies it
DOOR_CLEAR_M = 0.10                 # beside a door frame
BUILT_HEIGHT_DEFAULT = 0.8

# The M12 tool names (§5.3); ``*_TOOLS`` say on what a tool acts.
# rotate_piece turns a piece (track G's ``rotate``); set_front gives a drawn piece without a front one along a side.
PIECE_TOOLS = ("move_piece", "rotate_piece", "set_front", "resize_piece", "retype_piece", "mark_not_furniture",
               "fix_fixture", "remove_piece", "swap_model")
GROUP_TOOLS = ("move_group", "complete_group")
ROOM_TOOLS = ("relayout_room", "place_group", "set_room_type", "set_lighting", "report_library_gap")
LEVEL_TOOLS = ("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")
VIEW_TOOLS = ("set_camera", "add_camera", "remove_camera")
BUILDING_TOOLS = ("set_exterior", "set_material", "correct_geometry")
# edit_ops op -> the tool name (track G may key ``allowed_edits`` by either).
TOOL_OF_OP = {"move": "move_piece", "rotate": "rotate_piece", "resize": "resize_piece", "change_type": "change_type",
              "swap_model": "swap_model", "add": "add_piece", "add_group": "add_group", "remove": "remove_piece"}

# check -> the tools that can fix a finding of it (§5.3; the brief keeps those allowed for the target).
CHECK_TOOLS: dict[str, tuple[str, ...]] = {
    "F1": ("retype_piece", "mark_not_furniture", "remove_piece", "set_room_type"),
    "F2": ("resize_piece", "fix_fixture", "retype_piece"),
    "F3": ("move_piece", "move_group", "rotate_piece", "set_front", "relayout_room"),
    "F4": ("rotate_piece", "set_front", "move_group", "relayout_room"),
    "F5": ("complete_group", "place_group", "relayout_room"),
    "F6": ("move_piece", "move_group", "remove_piece", "relayout_room"),
    "F7": ("move_piece", "move_group", "fix_fixture", "mark_not_furniture", "remove_piece", "relayout_room"),
    "F8": ("move_piece", "move_group", "remove_piece", "relayout_room"),
    "F9": ("retype_piece", "mark_not_furniture", "swap_model", "remove_piece"),
    "R1": ("set_room_type",),
    "R3": ("move_piece", "move_group", "fix_fixture", "relayout_room"),
    "R4": ("set_material",),
    "R5": ("set_lighting",),
    "G1": ("move_group", "rotate_piece", "set_front", "relayout_room"),
    "G2": ("move_group", "complete_group", "relayout_room"),
    "G3": ("rotate_piece", "set_front", "move_group", "relayout_room"),
    "G4": ("complete_group", "move_piece", "move_group", "relayout_room"),     # missing or misplaced nightstand
    "G5": ("move_group", "rotate_piece", "set_front", "relayout_room"),
    "G6": ("complete_group", "rotate_piece", "set_front", "move_piece", "relayout_room"),     # chairs
    "G7": ("complete_group", "move_group", "relayout_room"),
    "G8": ("relayout_room", "fix_fixture"),
    "G9": ("place_group", "complete_group", "retype_piece"),
    "G10": ("place_group", "complete_group", "fix_fixture", "retype_piece"),
    "G11": ("move_group", "move_piece", "remove_piece", "relayout_room"),
    "G12": ("move_piece", "move_group", "relayout_room"),
    "G13": ("move_piece", "move_group", "relayout_room"),
    "G14": ("retype_piece", "mark_not_furniture", "remove_piece", "set_room_type"),
    "S1": ("swap_model",),
    "S2": ("move_piece", "move_group", "swap_model"),
    "S3": ("swap_model", "rotate_piece", "set_front"),
    "S4": ("swap_model", "resize_piece"),
    "S6": ("retype_piece", "swap_model", "report_library_gap"),
    "LG": ("report_library_gap", "swap_model", "retype_piece"),
    "L1": ("set_entrance", "set_ground_point"),
    "L2": ("set_entrance",),
    "L3": ("set_ground_point", "set_terrain", "set_room_floor"),
    "L4": ("set_mark_kind", "set_room_floor", "set_ground_point"),
    "L5": ("set_entrance",),
    "L6": ("set_terrain",),
    "L7": ("add_camera", "set_camera"),
    "X1": ("correct_geometry",),
    "X2": ("set_exterior",), "X3": ("set_exterior",), "X4": ("set_exterior",), "X7": ("set_exterior",),
    "X6": ("set_camera", "add_camera"),
    "X8": ("set_material",),
    "V1": ("set_camera", "remove_camera"),
    "D1": ("move_piece", "swap_model"),
    "D2": ("swap_model", "report_library_gap"),
}
# Measured by code with no tool behind it: listed as "not yours" with this reason.
NOT_YOURS_REASON = {"S5": "decor rest is placed by the decor stage on the built mesh (S5): no agent tool",
                    "V3": "debug markers are a build setting, not an agent edit",
                    "V2": "the render/JSON match is checked by the final check", "X5": "storey and door sizes come "
                    "from the drawings", "R2": "ceiling heights come from the drawings"}


def _f(v, n=3):
    try:
        return round(float(v), n)
    except (TypeError, ValueError):
        return None


def built(piece: dict) -> bool:
    """Built in the scene (``topdown.is_built``: track S's ``decor.piece_is_built``; ``unknown`` and library gaps
    are not built)."""
    from wenart.agent import topdown as TD
    return TD.is_built(piece)


def front_of(piece: dict) -> tuple[float, bool]:
    """``(front_deg, inferred)``: the drawn/AI front, else ``rotation_deg - 90`` (the stage convention, M11 §1.2)."""
    if piece.get("front_deg") is not None:
        return float(piece["front_deg"]) % 360.0, False
    rot = float((piece.get("footprint") or {}).get("rotation_deg") or 0.0)
    return (rot - 90.0) % 360.0, True


# --------------------------------------------------------------------------
# Lock state
# --------------------------------------------------------------------------

def _yes(move_left=None):
    return {"allowed": True, "why": "", "move_left_m": move_left}


def _no(why):
    return {"allowed": False, "why": why, "move_left_m": None}


def allowed_fallback(building: dict, piece: dict) -> dict:
    """The M11 rules of CLAUDE.md per tool (module docstring), used while ``edit_ops.allowed_edits`` is a stub."""
    from wenart.furniture import schemas
    room = next((r for r in building.get("rooms") or [] if r.get("id") == piece.get("room_id")), {})
    ftype = str(piece.get("type") or "unknown")
    if not built(piece):
        # in no render; an untyped one is listed for review by the reading stage (track R), never the agent's work
        return {t: _no("not built: it is in no render") for t in PIECE_TOOLS}
    if piece.get("source") == "added_by_ai":
        return {t: (_no("an AI piece is never 'not furniture': remove it") if t == "mark_not_furniture"
                    else _no("fix_fixture is for drawn fixed equipment") if t == "fix_fixture" else _yes())
                for t in PIECE_TOOLS}
    if ftype in schemas.FIXED_TYPES:
        why = "drawn fixed equipment: type, place and footprint are locked"
        out = {t: _no(why) for t in PIECE_TOOLS}
        out["set_front"] = _yes()          # only a front into the wall (validated)
        out["rotate_piece"] = _yes()       # the same: a clear front error only
        out["fix_fixture"] = _yes(0.5)     # U1: a misread size or a piece through a wall / in a door swing
        out["swap_model"] = _yes()
        if schemas.misplaced_fixed(ftype, room.get("room_type")):
            out["retype_piece"] = _yes()
            out["mark_not_furniture"] = _yes()
        return out
    drawn = (piece.get("drawn_footprint") or {}).get("center")
    now = (piece.get("footprint") or {}).get("center")
    moved = math.dist([float(c) for c in drawn[:2]], [float(c) for c in now[:2]]) if drawn and now else 0.0
    left = round(max(0.0, 0.3 - moved), 3)
    out = {t: _yes() for t in PIECE_TOOLS}
    out["move_piece"] = _yes(left) if left > 0 else _no(f"drawn piece already moved {moved:.2f} m (limit 0.3 m; "
                                                        f"a wall snap may go to {schemas.WALL_SNAP_MAX_M} m)")
    out["remove_piece"] = _no(DRAWN_REMOVE_HINT)
    out["fix_fixture"] = _no("fix_fixture is for drawn fixed equipment")
    return out


def normalise_allowed(answer: Optional[dict]) -> dict:
    """``allowed_edits`` keyed by tool name (op names mapped), values ``{allowed, why, move_left_m}``."""
    out = {}
    for k, v in (answer or {}).items():
        if not isinstance(v, dict):
            continue
        out[TOOL_OF_OP.get(k, k)] = {"allowed": bool(v.get("allowed")), "why": str(v.get("why") or ""),
                                    "move_left_m": _f(v.get("move_left_m"))}
    return out


def allowed_of(building: dict, piece: dict, allowed_fn: Optional[Callable] = None) -> tuple[dict, str]:
    """``(allowed per tool, source)``: track G's ``allowed_edits`` (source ``edit_ops``), else the fallback."""
    fn = allowed_fn
    if fn is None:
        try:
            from wenart.furniture import edit_ops
            fn = edit_ops.allowed_edits
        except ImportError:
            fn = None
    got = {}
    if fn is not None:
        try:
            got = normalise_allowed(fn(building, piece.get("id")))
        except Exception:  # noqa: BLE001 - a broken validator answer falls back to the M11 rules
            got = {}
    if got:
        return a_rules(piece, got), "edit_ops"
    return allowed_fallback(building, piece), "fallback"


DRAWN_REMOVE_HINT = "a drawn piece is removed only as not furniture: use mark_not_furniture with evidence"


def a_rules(piece: dict, allowed: dict) -> dict:
    """Track G's answer with the agent's stricter rule on top (CLAUDE.md: a drawn piece is removed only when it is
    clearly not furniture, logged with the plan crop as evidence): ``remove_piece`` of a drawn piece points to
    ``mark_not_furniture`` instead."""
    out = dict(allowed)
    if piece.get("source") == "from_documents" and (out.get("remove_piece") or {}).get("allowed"):
        out["remove_piece"] = _no(DRAWN_REMOVE_HINT)
    return out


def lock_text(allowed: dict) -> str:
    """One line: what the model may do with the piece."""
    yes = [t for t in PIECE_TOOLS if (allowed.get(t) or {}).get("allowed")]
    if not yes:
        whys = sorted({(allowed.get(t) or {}).get("why") for t in PIECE_TOOLS if (allowed.get(t) or {}).get("why")})
        return "locked: " + ("; ".join(whys) if whys else "no edit allowed")
    mv = (allowed.get("move_piece") or {}).get("move_left_m")
    return "may: " + ", ".join(yes) + (f" (move_piece up to {mv} m)" if mv is not None else "")


# --------------------------------------------------------------------------
# Free wall spans
# --------------------------------------------------------------------------

def _wall_of(building: dict, room: dict, a, b) -> Optional[str]:
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    ux, uy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(ux, uy) or 1.0
    best = None
    for w in building.get("walls") or []:
        if w.get("level_id") != room.get("level_id"):
            continue
        (sx, sy), (ex, ey) = w["start"][:2], w["end"][:2]
        wx, wy = ex - sx, ey - sy
        wl = math.hypot(wx, wy)
        if wl < 1e-6 or abs(ux * wy - uy * wx) / (n * wl) > 0.05:
            continue
        t = max(0.0, min(1.0, ((mid[0] - sx) * wx + (mid[1] - sy) * wy) / (wl * wl)))
        d = math.hypot(sx + t * wx - mid[0], sy + t * wy - mid[1])
        if d <= float(w.get("thickness") or 0.2) / 2.0 + 0.1 and (best is None or d < best[0]):
            best = (d, w.get("id"))
    return best[1] if best else None


def _minus(free: list, lo: float, hi: float) -> list:
    out = []
    for a, b in free:
        if hi <= a or lo >= b:
            out.append((a, b))
            continue
        if lo > a:
            out.append((a, lo))
        if hi < b:
            out.append((hi, b))
    return out


def wall_spans(building: dict, room_id: str, spans_fn: Optional[Callable] = None) -> list[dict]:
    """The room's free wall spans for the brief: track G's ``edit_ops.free_spans`` (its ``span_id`` is what
    ``move_group`` takes), each with the direction into the room and the window parts where only pieces below the
    sill fit; ``free_wall_spans`` when track G's function is missing or fails."""
    from shapely.geometry import LineString
    from wenart.furniture import placer
    fn = spans_fn
    if fn is None:
        try:
            from wenart.furniture import edit_ops
            fn = edit_ops.free_spans
        except ImportError:
            fn = None
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if fn is None or room is None:
        return free_wall_spans(building, room_id)
    try:
        raw = fn(building, room_id) or []
        ctx = placer.room_context(building, room)
    except Exception:  # noqa: BLE001 - the brief's own spans then
        return free_wall_spans(building, room_id)
    out = []
    for s in raw:
        try:
            a, b = ctx.segments[int(s["edge"])]
        except (KeyError, IndexError, TypeError, ValueError):
            continue
        length = math.dist(a, b)
        if length <= 0:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        line = LineString([a, b])
        lo, hi = float(s.get("start") or 0.0), float(s.get("end") or length)
        notes = []
        for w in ctx.windows:
            if line.distance(_pt(w.inner_point)) > 0.2:
                continue
            t = (w.inner_point[0] - a[0]) * ux + (w.inner_point[1] - a[1]) * uy
            w0, w1 = max(lo, t - w.width / 2), min(hi, t + w.width / 2)
            if w1 - w0 > 0.05:
                notes.append(f"{w0 - lo:.2f}-{w1 - lo:.2f} m along it only below the sill {_f(w.sill, 2)} m "
                             f"(window {w.id})")
        out.append({"id": s.get("span_id"), "wall_id": s.get("wall_id"), "start": s.get("from"), "end": s.get("to"),
                    "length_m": _f(s.get("length"), 2),
                    "into_room_deg": _f(math.degrees(math.atan2(ux, -uy)) % 360.0, 1),
                    "fits": "; ".join(notes) or "any piece"})
    return out


def free_wall_spans(building: dict, room_id: str) -> list[dict]:
    """The wall pieces of the room where a back-to-wall piece can stand: each boundary segment minus door frames,
    built floor pieces against it; window bands are listed with their sill (only lower pieces fit there)."""
    from shapely.geometry import LineString
    from wenart.furniture import placer
    from wenart.agent import topdown as TD
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        return []
    try:
        ctx = placer.room_context(building, room)
    except Exception:  # noqa: BLE001 - a broken polygon has no spans
        return []
    pieces = []
    for p in TD.room_pieces(building, room_id):
        if not built(p) or p.get("mount_bottom_m"):
            continue
        try:
            pieces.append(TD.piece_polygon(p))
        except Exception:  # noqa: BLE001
            continue
    spans = []
    for i, (a, b) in enumerate(ctx.segments):
        length = math.dist(a, b)
        if length < SPAN_MIN_M:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy, ux                                    # CCW ring: the left normal points into the room
        line = LineString([a, b])

        def along(pt):
            return (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy

        free = [(0.0, length)]
        low: list = []
        for d in ctx.doors:
            if line.distance(_pt(d.inner_point)) <= 0.2:
                t = along(d.inner_point)
                free = _minus(free, t - d.width / 2 - DOOR_CLEAR_M, t + d.width / 2 + DOOR_CLEAR_M)
        for w in ctx.windows:
            if line.distance(_pt(w.inner_point)) <= 0.2:
                t = along(w.inner_point)
                low.append((t - w.width / 2, t + w.width / 2, w.sill, w.id))
        for poly in pieces:
            if poly.distance(line) <= SPAN_PIECE_GAP_M:
                ts = [along(c) for c in poly.exterior.coords]
                free = _minus(free, min(ts), max(ts))
        k = 0
        for lo, hi in free:
            # split at the window bands: the window part only takes pieces below its sill
            cuts = [(lo, hi, None, None)]
            for wl, wh, sill, wid in sorted(low):
                nxt = []
                for c0, c1, s, i_ in cuts:
                    if s is not None or wh <= c0 or wl >= c1:
                        nxt.append((c0, c1, s, i_))
                        continue
                    if wl > c0:
                        nxt.append((c0, wl, None, None))
                    nxt.append((max(c0, wl), min(c1, wh), sill, wid))
                    if wh < c1:
                        nxt.append((wh, c1, None, None))
                cuts = nxt
            for c0, c1, sill, wid in cuts:
                if c1 - c0 < SPAN_MIN_M:
                    continue
                k += 1
                start = (a[0] + ux * c0, a[1] + uy * c0)
                end = (a[0] + ux * c1, a[1] + uy * c1)
                spans.append({"id": f"{room_id}:s{i + 1}.{k}", "wall_id": _wall_of(building, room, a, b),
                              "start": [_f(start[0]), _f(start[1])], "end": [_f(end[0]), _f(end[1])],
                              "length_m": _f(c1 - c0, 2),
                              "into_room_deg": _f(math.degrees(math.atan2(ny, nx)) % 360.0, 1),
                              "fits": "any piece" if sill is None else f"only below the sill {_f(sill, 2)} m "
                                                                         f"(window {wid})"})
    return spans


def _pt(xy):
    from shapely.geometry import Point
    return Point(float(xy[0]), float(xy[1]))


# --------------------------------------------------------------------------
# Findings: fixable or not yours
# --------------------------------------------------------------------------

def _check_tools(check: str) -> tuple[str, ...]:
    return CHECK_TOOLS.get(check) or ()


def classify(findings: list[dict], building: dict, room_id: Optional[str], allowed: dict, group_of: dict,
             room_tools_ok: dict) -> tuple[list[dict], list[dict]]:
    """``(fixable, not_yours)`` (module docstring). ``allowed``: piece id -> allowed per tool; ``group_of``: piece id
    -> group id; ``room_tools_ok``: room tool -> bool (relayout possible, a group to place / complete)."""
    pieces = {p.get("id"): p for p in building.get("furniture") or []}
    fixable, not_yours = [], []
    for f in findings:
        check, target = str(f.get("check")), f.get("target")
        base = {"id": f.get("id"), "check": check, "severity": f.get("severity"), "target": target,
                "message": f.get("message")}
        tools = _check_tools(check)
        if not tools:
            not_yours.append(dict(base, why=NOT_YOURS_REASON.get(check, f"no agent tool fixes {check}")))
            continue
        piece = pieces.get(target)
        ok: list = []
        whys: list = []
        if piece is not None:
            if not built(piece):
                not_yours.append(dict(base, why="not built: it is in no render; leave it"))
                continue
            for t in tools:
                if t in PIECE_TOOLS:
                    a = (allowed.get(target) or {}).get(t) or {}
                    if a.get("allowed"):
                        ok.append(t)
                    elif a.get("why"):
                        whys.append(f"{t}: {a['why']}")
                elif t in GROUP_TOOLS:
                    if group_of.get(target) or (t == "complete_group" and room_tools_ok.get("complete_group")):
                        ok.append(t)
                elif t == "relayout_room":
                    # a re-layout moves the AI pieces: it fixes an AI piece, or a group around a drawn anchor
                    if room_tools_ok.get(t, True) and (piece.get("source") == "added_by_ai" or check.startswith("G")
                                                       or check == "F5"):
                        ok.append(t)
                elif t in ROOM_TOOLS:
                    if room_tools_ok.get(t, True):
                        ok.append(t)
                else:
                    ok.append(t)
        else:
            # the room, an opening, a view, a wall or the building: room / view / building tools; piece tools only
            # when some piece of the room may take them (a door swing hit: move the pieces in the swing)
            for t in tools:
                if t in PIECE_TOOLS or t in GROUP_TOOLS:
                    if any((allowed.get(pid) or {}).get(t, {}).get("allowed") for pid in allowed) or \
                            (t in GROUP_TOOLS and room_tools_ok.get(t)):
                        ok.append(t)
                elif room_tools_ok.get(t, True):
                    ok.append(t)
        if ok:
            fixable.append(dict(base, tools=ok))
        else:
            not_yours.append(dict(base, why="locked: " + ("; ".join(whys[:3]) if whys else "no allowed tool")))
    order = {"critical": 0, "major": 1, "minor": 2}
    key = lambda f: (order.get(f.get("severity"), 3), str(f.get("check")), str(f.get("target")))  # noqa: E731
    return sorted(fixable, key=key), sorted(not_yours, key=key)


def fixable_weight(fixable: list[dict], area: float) -> float:
    """The room's rank weight: sum of the fixable critical / major findings' severity weights x area (§5.4)."""
    return sum(SEVERITY_WEIGHT.get(f.get("severity"), 0.0) for f in fixable
               if f.get("severity") in ("critical", "major")) * max(1.0, float(area or 0.0))


# --------------------------------------------------------------------------
# The brief
# --------------------------------------------------------------------------

def _call(notes: list, what: str, fn: Callable, default):
    try:
        out = fn()
    except NotImplementedError as exc:
        notes.append(f"{what}: not built yet ({exc})")
        return default
    except Exception as exc:  # noqa: BLE001 - one missing part never stops the brief
        notes.append(f"{what}: {type(exc).__name__}: {exc}")
        return default
    return default if out is None else out


def compact_allowed(allowed: dict) -> dict:
    """``{tool: true | "why not"}`` for the piece tools (what the brief shows)."""
    return {t: True if (allowed.get(t) or {}).get("allowed") else str((allowed.get(t) or {}).get("why") or "no")
            for t in PIECE_TOOLS if t in allowed}


def is_allowed(piece_line: dict, tool: str) -> bool:
    """Whether a brief piece line allows ``tool``."""
    return (piece_line.get("allowed") or {}).get(tool) is True


def _piece_line(p: dict, allowed: dict, group: Optional[dict]) -> dict:
    fp = p.get("footprint") or {}
    front, inferred = front_of(p)
    out = {"id": p.get("id"), "type": p.get("type"), "source": p.get("source"),
           "size": [_f(s, 2) for s in (fp.get("size") or [])[:2]], "height": _f(p.get("height"), 2),
           "center": [_f(c, 2) for c in (fp.get("center") or [])[:2]], "rotation_deg": _f(fp.get("rotation_deg"), 1),
           "front_deg": _f(front, 1), "lock": lock_text(allowed), "allowed": compact_allowed(allowed)}
    move_left = (allowed.get("move_piece") or {}).get("move_left_m")
    if move_left is not None:
        out["move_left_m"] = move_left
    if inferred:
        out["front_inferred"] = True
    if group:
        out["group"] = group
    for k in ("adjusted_by_ai", "inferred", "completes_room"):
        if p.get(k):
            out.setdefault("labels", []).append(k)
    if p.get("library_gap"):
        out["library_gap"] = p["library_gap"]
    return out


def room_brief(building: dict, room_id: str, *, findings: Optional[list] = None, memory=None,
               image_of: Optional[Callable] = None, allowed_fn: Optional[Callable] = None,
               program_fn: Optional[Callable] = None, members_fn: Optional[Callable] = None,
               group_checks_fn: Optional[Callable] = None, solver_fn: Optional[Callable] = None,
               spans_fn: Optional[Callable] = None, k: int = 3) -> dict:
    """The brief of ``room_id`` (module docstring). ``findings``: the round's findings of this room (code and kept
    vision); ``memory``: ``memory.Memory``; ``image_of(rank, candidate) -> image id``; the ``*_fn`` arguments
    replace the other tracks' functions (tests)."""
    from wenart.agent import topdown as TD
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        return {"error": f"no room {room_id}"}
    notes: list = []
    if program_fn is None or members_fn is None or group_checks_fn is None or solver_fn is None:
        from wenart.furniture import group_checks, groups, program, solver
        program_fn = program_fn or program.room_program
        members_fn = members_fn or groups.group_members
        group_checks_fn = group_checks_fn or group_checks.check_room
        solver_fn = solver_fn or solver.solve_room
    all_pieces = TD.room_pieces(building, room_id)
    pieces = [p for p in all_pieces if built(p)]
    members = _call(notes, "groups", lambda: members_fn(building, room_id), []) or []
    group_of: dict = {}
    for g in members:
        for pid in [g.get("anchor_id")] + list(g.get("member_ids") or []):
            if pid:
                group_of[pid] = g.get("group_id")
    allowed: dict = {}
    allowed_source = set()
    for p in all_pieces:
        a, src = allowed_of(building, p, allowed_fn)
        allowed[p.get("id")] = a
        allowed_source.add(src)
    g_viol = _call(notes, "group checks", lambda: group_checks_fn(building, room_id), []) or []
    prog = _call(notes, "program", lambda: program_fn(building, room_id), {}) or {}
    cands = _call(notes, "solver", lambda: solver_fn(building, room_id, k=k), []) or []
    groups_out = []
    for g in members:
        ids = {g.get("group_id"), g.get("anchor_id"), *(g.get("member_ids") or [])}
        groups_out.append({"group_id": g.get("group_id"), "group": g.get("group"), "anchor_id": g.get("anchor_id"),
                           "member_ids": list(g.get("member_ids") or []), "missing": list(g.get("missing") or []),
                           "checks": [f"{v.get('check')} {v.get('severity')}: {v.get('message')}" for v in g_viol
                                      if v.get("target") in ids]})
    program_groups = [{k2: g.get(k2) for k2 in ("group_id", "group", "anchor_id", "required", "options", "chosen",
                                                 "drawn")} for g in prog.get("groups") or []]
    present = {g.get("group") for g in members}
    # Without group data (track G's stubs) a group tool is offered and the validator decides.
    room_tools_ok = {
        "relayout_room": bool(cands) or any(p.get("source") == "added_by_ai" for p in pieces),
        "place_group": any(g.get("group") not in present for g in program_groups) if program_groups else True,
        "complete_group": any(g.get("missing") for g in members) if members else True,
        "move_group": bool(members),
    }
    fixable, not_yours = classify(list(findings or []), building, room_id,
                                  {pid: a for pid, a in allowed.items()}, group_of, room_tools_ok)
    candidates = []
    for c in cands[:k]:
        rank = int(c.get("rank") or len(candidates) + 1)
        entry = {"candidate": rank, "score": _f(c.get("score"), 2),
                 "terms": {str(t): _f(v, 2) for t, v in sorted((c.get("terms") or {}).items())},
                 "groups": [{"group": g.get("group"), "anchor_id": g.get("anchor_id"),
                             "members": len(g.get("member_ids") or [])} for g in c.get("groups") or []],
                 "pieces": len(c.get("pieces") or []),
                 "hard_failures": list(c.get("hard_failures") or [])[:5],
                 "group_findings": [f"{v.get('check')} {v.get('severity')}" for v in c.get("group_violations") or []][:8]}
        if image_of is not None:
            entry["image"] = _call(notes, f"candidate {rank} image", lambda c=c, rank=rank: image_of(rank, c), None)
        candidates.append(entry)
    try:
        from wenart.furniture import placer
        doors, windows = placer.room_openings(building, room)
    except Exception:  # noqa: BLE001
        doors, windows = [], []
    out = {
        "room": {"id": room_id, "label": room.get("label"), "type": room.get("room_type"),
                 "level_id": room.get("level_id"), "area_m2": _f(room.get("area_computed"), 1),
                 "doors": [{"id": d.get("id"), "width": _f(d.get("width"), 2),
                            "swings_into_room": d.get("swing_side") == room_id} for d in doors],
                 "windows": [{"id": w.get("id"), "width": _f(w.get("width"), 2), "sill": _f(w.get("sill_height"), 2)}
                             for w in windows]},
        "conventions": "metres; front_deg = the direction the front faces, degrees counter-clockwise from +x; "
                       "size = [width along the front, depth]",
        "pieces": [_piece_line(p, allowed[p.get("id")],
                               ({"group_id": group_of[p["id"]]} if p.get("id") in group_of else None)
                               or (p.get("group") if isinstance(p.get("group"), dict) else None))
                   for p in pieces],
        "not_built": [{"id": p.get("id"), "type": p.get("type"),
                       "size": [_f(s, 2) for s in ((p.get("footprint") or {}).get("size") or [])[:2]]}
                      for p in all_pieces if not built(p)],
        "program": {"groups": program_groups, "reason": prog.get("reason")},
        "groups": groups_out,
        "room_checks": [f"{v.get('check')} {v.get('severity')}: {v.get('message')}" for v in g_viol
                        if v.get("target") in (room_id, None)],
        "free_wall_spans": wall_spans(building, room_id, spans_fn),
        "findings": {"fixable": fixable, "not_yours": not_yours},
        "memory": memory.summary(room_id) if memory is not None else {},
        "candidates": candidates,
        "allowed_source": sorted(allowed_source),
    }
    if notes:
        out["notes"] = notes
    return out


def findings_of_room(findings: list[dict], building: dict, room_id: str) -> list[dict]:
    """The findings that belong to ``room_id``: its own and those of its pieces, openings and views."""
    pieces = {p.get("id"): p.get("room_id") for p in building.get("furniture") or []}
    return [f for f in findings if f.get("room_id") == room_id or pieces.get(f.get("target")) == room_id
            or f.get("target") == room_id]
