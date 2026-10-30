"""Curtains and blinds follow their windows as built (30 Oct 2026, lesson UL181; user on real04 run
20261030-112241-full, the top-floor play room: "This window and curtain arrangement needs a rework").

What the run had: the decor stage (``wenart.furniture.decor_ai.window_items``) fitted the play room's curtain to the drawn
window, 2.00 m wide: a rod 0.20 m past each side, 2.40 m. The build then carried out the architect's answers
(``architect_actions``: glass to 1/10 of the floor and the W5 tall window), which widened the window to 4.00 m and
lowered its sill to 0.20 m. The curtain stayed 2.40 m wide on the window's centre, so its two panels hung in the middle
of the 4 m glazing, and its rod sat just under the new head.

What (pure: the building JSON's dicts, no bpy, no shapely: ``build.prepare`` runs it in Blender after the architect's
answers and the roof clips, ``refit``):

- a curtain or blind (a decor item with ``window_id``) that still spans its window as built (``covers``: its rod
  ``CURTAIN_MIN_OVERLAP_M`` past each side of the glazing, a blind its width, its top over the window's head) is left
  as it is (the dressing's depth, drop, track and layers stay);
- else its span along the wall is fitted again by ``decor_ai.window_items``'s rules: the window's width and
  ``CURTAIN_OVERLAP_M`` past each side (a blind ``BLIND_WIDTH_EXTRA_M`` wider than the window), narrowed by 0.05 m
  steps to stay ``OPENING_MARGIN_M`` off the other openings of its wall and ``WALL_END_MARGIN_M`` inside the wall's
  room face, its panels stacked at the two ends of the whole glazing (``parametric.curtain_parts``); a curtain that
  keeps less than ``CURTAIN_MIN_OVERLAP_M`` on a side, or a blind that no longer fits, is not built (its reason);
- its drop stays unless the window's head rose over its rod: then the rod stands ``CURTAIN_ROD_ABOVE_M`` over the
  head (a blind's roller ``BLIND_ROLLER_ABOVE_M``), at most ``CEILING_CLEAR_M`` under the ceiling, under a slope
  ``SLOPE_CLEAR_M`` under it, the curtain's foot where it was;
- every change is recorded on the item (``refit``: rule, lesson, the former values, why) and returned.

Constants mirror ``wenart.furniture.decor_ai`` and ``wenart.furniture.decor`` (that package needs jsonschema, which
Blender's Python lacks; ``tests/test_windows_curtains_20261030.py`` keeps them equal).
"""
from __future__ import annotations

import math
from typing import Optional

RULE = "window_decor.refit"
LESSON = "UL181"
WINDOW_DECOR_TYPES: tuple[str, ...] = ("curtain", "blind")
CURTAIN_OVERLAP_M = 0.2             # = decor_ai.CURTAIN_OVERLAP_M
CURTAIN_MIN_OVERLAP_M = 0.05        # = decor_ai.CURTAIN_MIN_OVERLAP_M
CURTAIN_ROD_ABOVE_M = 0.15          # = decor_ai.CURTAIN_ROD_ABOVE_M
BLIND_WIDTH_EXTRA_M = 0.1           # = decor_ai.BLIND_WIDTH_EXTRA_M
BLIND_ROLLER_ABOVE_M = 0.06         # = decor_ai.BLIND_ROLLER_ABOVE_M
CEILING_CLEAR_M = 0.10              # = decor_ai.CEILING_CLEAR_M
SLOPE_CLEAR_M = 0.02                # = decor.WINDOW_DECOR_CEILING_CLEAR_M
OPENING_MARGIN_M = 0.1              # = decor.OPENING_MARGIN_M
WALL_END_MARGIN_M = 0.05            # = decor.WALL_END_MARGIN_M
STEP_M = 0.05


def _window_heights(win: dict) -> tuple[float, float]:
    sill = float(win.get("sill_height") if win.get("sill_height") is not None else 0.9)
    return sill, sill + float(win.get("height") or 1.2)


def _frame(wall: dict) -> tuple[tuple[float, float], tuple[float, float], float]:
    """``(start, unit direction, length)`` of a wall's centre line."""
    a, b = wall["start"], wall["end"]
    dx, dy = float(b[0]) - float(a[0]), float(b[1]) - float(a[1])
    length = math.hypot(dx, dy) or 1e-9
    return (float(a[0]), float(a[1])), (dx / length, dy / length), length


def _s(p, a, u) -> float:
    return (float(p[0]) - a[0]) * u[0] + (float(p[1]) - a[1]) * u[1]


def covers(item: dict, win: dict, wall: dict) -> bool:
    """Whether a curtain's rod (a blind's roller) still spans its window along the wall and its top stands over the
    window's head (pure)."""
    a, u, _length = _frame(wall)
    s_i, s_w = _s(item["center"], a, u), _s(win["center"], a, u)
    half_i, half_w = float(item["size"][0]) / 2.0, float(win.get("width") or 0.0) / 2.0
    margin = CURTAIN_MIN_OVERLAP_M if item.get("type") == "curtain" else 0.0
    spans = s_i - half_i <= s_w - half_w - margin + 1e-3 and s_i + half_i >= s_w + half_w + margin - 1e-3
    bottom = float(item["center"][2]) if len(item["center"]) > 2 else 0.0
    return spans and bottom + float(item["size"][2]) >= _window_heights(win)[1] - 1e-3


def _ceiling_rel(level: Optional[dict], points) -> float:
    """The ceiling over ``points`` above the level's floor (its sloped planes when lower)."""
    if not level:
        return 2.7
    from wenart.blender import feature_walls as FW

    return FW._ceiling_z(level, points) - float(level.get("elevation") or 0.0)


def _span(s_w: float, half: float, left: float, right: float, length: float, end: float,
          blocked: list[tuple[float, float]]) -> Optional[tuple[float, float]]:
    """The rod's ``(s0, s1)``: ``left`` / ``right`` past the window, narrowed by ``STEP_M`` off the wall's ends and the
    blocked spans; None when a side keeps less than ``CURTAIN_MIN_OVERLAP_M``."""
    while left >= CURTAIN_MIN_OVERLAP_M - 1e-9 and right >= CURTAIN_MIN_OVERLAP_M - 1e-9:
        s0, s1 = s_w - half - left, s_w + half + right
        if s0 < end:
            left -= STEP_M
        elif s1 > length - end:
            right -= STEP_M
        elif any(s0 < b1 - 1e-9 and b0 < s_w for b0, b1 in blocked):
            left -= STEP_M
        elif any(s1 > b0 + 1e-9 and b1 > s_w for b0, b1 in blocked):
            right -= STEP_M
        else:
            return s0, s1
    return None


def refit(building: dict) -> list[dict]:
    """In place (module docstring): the curtains and blinds of ``building`` that no longer span their windows fitted
    again; returns ``[{"id", "window_id", "type", "was", "now", "why"}]`` of the items it changed or left unbuilt."""
    openings = [o for o in building.get("openings") or [] if isinstance(o, dict)]
    windows = {o.get("id"): o for o in openings if o.get("type") == "window"}
    walls = {w.get("id"): w for w in building.get("walls") or [] if isinstance(w, dict)}
    levels = {lv.get("id"): lv for lv in building.get("levels") or [] if isinstance(lv, dict)}
    out: list[dict] = []
    for it in building.get("decor") or []:
        if not isinstance(it, dict) or it.get("type") not in WINDOW_DECOR_TYPES or it.get("build") is False:
            continue
        win = windows.get(it.get("window_id"))
        wall = walls.get((win or {}).get("wall_id"))
        if win is None or wall is None or len(it.get("size") or []) < 3 or len(it.get("center") or []) < 2:
            continue
        center = [float(v) for v in it["center"]] + [0.0] * (3 - len(it["center"]))
        it_c = dict(it, center=center)
        if covers(it_c, win, wall):
            continue
        a, u, length = _frame(wall)
        s_w, half = _s(win["center"], a, u), float(win.get("width") or 0.0) / 2.0
        end = float(wall.get("thickness") or 0.2) / 2.0 + WALL_END_MARGIN_M
        blocked = []
        for o in openings:
            if o is win or o.get("wall_id") != wall.get("id") or not o.get("center"):
                continue
            s_o, h_o = _s(o["center"], a, u), float(o.get("width") or 0.0) / 2.0
            blocked.append((s_o - h_o - OPENING_MARGIN_M, s_o + h_o + OPENING_MARGIN_M))
        sill, top = _window_heights(win)
        what = f"window {win['id']} as built: {2.0 * half:.2f} m wide, sill {sill:.2f} m, head {top:.2f} m"
        if it["type"] == "curtain":
            span = _span(s_w, half, CURTAIN_OVERLAP_M, CURTAIN_OVERLAP_M, length, end, blocked)
        else:
            extra = BLIND_WIDTH_EXTRA_M / 2.0
            span = (s_w - half - extra, s_w + half + extra)
            if span[0] < end or span[1] > length - end or any(span[0] < b1 and span[1] > b0 for b0, b1 in blocked):
                span = None
        was = {"center": list(it["center"]), "size": list(it["size"]), "wall_point": it.get("wall_point")}
        if span is None:
            it.update(build=False, not_built_reason=f"its {what} leaves no room for the {it['type']} (doors, wall "
                                                    f"ends) ({LESSON})")
            out.append({"id": it.get("id"), "window_id": win["id"], "type": it["type"], "was": was, "now": None,
                        "why": it["not_built_reason"]})
            continue
        s0, s1 = span
        delta = (s0 + s1) / 2.0 - _s(center, a, u)
        cx, cy = center[0] + u[0] * delta, center[1] + u[1] * delta
        size = [round(s1 - s0, 3), float(it["size"][1]), float(it["size"][2])]
        z = center[2]
        if z + size[2] < top - 1e-3:                  # the head rose over its rod (roller): the top moves up
            hw, hd = size[0] / 2.0, size[1] / 2.0
            corners = [(cx + u[0] * i * hw - u[1] * j * hd, cy + u[1] * i * hw + u[0] * j * hd)
                       for i in (-1, 1) for j in (-1, 1)]
            ceiling = _ceiling_rel(levels.get(it.get("level_id") or win.get("level_id")), [(cx, cy)] + corners)
            flat = float((levels.get(it.get("level_id") or win.get("level_id")) or {}).get("ceiling_height") or 2.7)
            clear = SLOPE_CLEAR_M if ceiling < flat - 1e-6 else CEILING_CLEAR_M
            above = CURTAIN_ROD_ABOVE_M if it["type"] == "curtain" else BLIND_ROLLER_ABOVE_M
            new_top = max(top, min(top + above, ceiling - clear))
            if it["type"] == "curtain":
                size[2] = round(new_top - z, 3)
            else:
                z = round(z + new_top - (z + size[2]), 3)
        now = {"center": [round(cx, 3), round(cy, 3), z], "size": size}
        if it.get("wall_point"):
            wp = it["wall_point"]
            now["wall_point"] = [round(float(wp[0]) + u[0] * delta, 3), round(float(wp[1]) + u[1] * delta, 3)]
        why = (f"fitted again to its {what}: a {size[0]:.2f} m rod past both sides of the whole glazing, its panels "
               f"at the glazing's ends ({LESSON})")
        it.update(now)
        it["refit"] = {"rule": RULE, "lesson": LESSON, "was": was, "why": why}
        out.append({"id": it.get("id"), "window_id": win["id"], "type": it["type"], "was": was, "now": now,
                    "why": why})
    return out
