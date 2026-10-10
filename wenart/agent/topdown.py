"""The top-down image of one room for the agent (docs/milestone11.md §3.1 ``room_topdown``).

What: ``draw_room(building, room_id, path)`` writes a PNG made on the CPU with matplotlib: the room polygon, every
piece of the room as its footprint with its id and type and an arrow for its front, the doors with their swing,
the window bands, and the checks the code failed in red (the piece outline and the check ids next to it; room-level
checks in the title). The vision critic gets it as image 1 of a room, the planner through the ``room_topdown`` tool,
and the log keeps one before and one after image per edit.

Why its own module: ``wenart.furniture.layout.draw_room_png`` draws the layout's proposals (passes, repairs) and
belongs to track B; this one draws the building as it is, with the same geometry helpers
(``placer.room_context`` for door swings and window bands, ``placer.Piece`` for footprints) and without changing
the furniture package.

How: front = ``front_deg`` (degrees, counter-clockwise from +x), else ``rotation_deg - 90`` (the convention of every
stage file, M11 §1.2); green = from the documents, orange = added by AI, blue = adjusted by AI, dashed = unverified;
the room context is optional (a broken polygon still gets its outline drawn).

Milestone 12 (docs/milestone12.md §5.2, bug B5): a piece with ``build: false`` is never drawn (it is in no render;
real03 run 3: 6 critical "giant box" findings on two unbuilt clusters). ``draw_candidate`` draws one solver
candidate (``solver.apply_candidate`` of track G) with its rank and score in the title, for the brief and for the
model's choice between candidates.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Optional

SOURCE_COLOURS = {"from_documents": "tab:green", "added_by_ai": "tab:orange"}
ADJUSTED_COLOUR = "tab:blue"
FAIL_COLOUR = "red"


def piece_front_deg(piece: dict) -> float:
    if piece.get("front_deg") is not None:
        return float(piece["front_deg"])
    return float((piece.get("footprint") or {}).get("rotation_deg") or 0.0) - 90.0


def piece_polygon(piece: dict):
    """The footprint polygon of a building-JSON piece (``placer.Piece`` geometry)."""
    from wenart.furniture import placer
    fp = piece.get("footprint") or {}
    size = tuple(float(s) for s in (fp.get("size") or (0.4, 0.4))[:2])
    center = tuple(float(c) for c in (fp.get("center") or (0.0, 0.0))[:2])
    return placer.Piece(str(piece.get("type") or "unknown"), center, float(fp.get("rotation_deg") or 0.0), size,
                        False).polygon()


def room_pieces(building: dict, room_id: str) -> list[dict]:
    """Every piece of the room, built or not (the brief lists the unbuilt ones apart)."""
    return [f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("room_id") == room_id]


def built_pieces(building: dict, room_id: str) -> list[dict]:
    """The pieces of the room that are built (``build`` is not false): the only ones drawn or shown (B5)."""
    return [f for f in room_pieces(building, room_id) if f.get("build", True) is not False]


def draw_candidate(building: dict, room_id: str, candidate: dict, path, apply_fn=None, dpi: int = 90) -> Path:
    """The room with solver candidate ``candidate`` applied (``solver.apply_candidate``), titled with its rank and
    score."""
    if apply_fn is None:
        from wenart.furniture import solver
        apply_fn = solver.apply_candidate
    b = apply_fn(building, room_id, candidate)
    room = next((r for r in b.get("rooms") or [] if r.get("id") == room_id), {})
    title = (f"candidate {candidate.get('rank')} score {candidate.get('score')}: {room.get('label')} ({room_id})")
    return draw_room(b, room_id, path, list(candidate.get("group_violations") or []), title=title, dpi=dpi)


def draw_room(building: dict, room_id: str, path, violations: Iterable[dict] = (), title: Optional[str] = None,
              annotate: bool = True, dpi: int = 90) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon

    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id}")
    fails: dict = {}
    room_fails: list[str] = []
    for v in violations or []:
        if v.get("target") == room_id or v.get("target") is None:
            room_fails.append(str(v.get("check")))
        else:
            fails.setdefault(v.get("target"), []).append(str(v.get("check")))
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    poly = [(float(x), float(y)) for x, y in room.get("polygon") or []]
    if poly:
        ax.add_patch(MplPolygon(poly, closed=True, fill=False, lw=2, color="black"))
    ctx = None
    try:
        from wenart.furniture import placer
        ctx = placer.room_context(building, room)
    except Exception:  # noqa: BLE001 - an odd polygon: the outline and the pieces are still drawn
        ctx = None
    if ctx is not None:
        for door in ctx.doors:
            colour = FAIL_COLOUR if door.id in fails else "tab:orange"
            if door.zone is not None and not door.zone.is_empty and door.zone.geom_type == "Polygon":
                ax.add_patch(MplPolygon(list(door.zone.exterior.coords), closed=True, color=colour, alpha=0.25))
            if door.swing is not None and not door.swing.is_empty and door.swing.geom_type == "Polygon":
                ax.add_patch(MplPolygon(list(door.swing.exterior.coords), closed=True, color=colour, alpha=0.15))
            if annotate:
                ax.text(door.inner_point[0], door.inner_point[1], door.id, fontsize=6, color=colour)
        for win in ctx.windows:
            if win.band is not None and not win.band.is_empty and win.band.geom_type == "Polygon":
                ax.add_patch(MplPolygon(list(win.band.exterior.coords), closed=True, color="tab:blue", alpha=0.25))
            if annotate:
                ax.text(win.inner_point[0], win.inner_point[1], win.id, fontsize=6, color="tab:blue")
    for piece in built_pieces(building, room_id):
        try:
            shape = piece_polygon(piece)
        except Exception:  # noqa: BLE001 - a piece without a usable footprint is listed, not drawn
            continue
        pid = piece.get("id")
        colour = ADJUSTED_COLOUR if piece.get("adjusted_by_ai") else SOURCE_COLOURS.get(piece.get("source"), "grey")
        failed = pid in fails
        coords = list(shape.exterior.coords) if shape.geom_type == "Polygon" else []
        if coords:
            ax.add_patch(MplPolygon(coords, closed=True, color=colour, alpha=0.35))
            ax.add_patch(MplPolygon(coords, closed=True, fill=False, lw=2.2 if failed else 1.0,
                                    color=FAIL_COLOUR if failed else colour,
                                    ls="--" if piece.get("status") == "unverified" else "-"))
        fp = piece.get("footprint") or {}
        cx, cy = (float(c) for c in (fp.get("center") or (0.0, 0.0))[:2])
        depth = float((fp.get("size") or (0.4, 0.4))[1])
        f = math.radians(piece_front_deg(piece))
        length = max(0.25, 0.6 * depth)
        ax.annotate("", xy=(cx + math.cos(f) * length, cy + math.sin(f) * length), xytext=(cx, cy),
                    arrowprops={"arrowstyle": "->", "color": FAIL_COLOUR if failed else "black", "lw": 1.2})
        if annotate:
            label = f"{pid}\n{piece.get('type')}"
            if failed:
                label += "\n" + ",".join(sorted(set(fails[pid])))
            ax.text(cx, cy, label, ha="center", va="center", fontsize=6,
                    color=FAIL_COLOUR if failed else "black")
    head = title or f"{room.get('label')} ({room_id}, {room.get('room_type')})"
    if room_fails:
        head += "  failed: " + ",".join(sorted(set(room_fails)))
    ax.set_title(head, fontsize=9, color=FAIL_COLOUR if room_fails else "black")
    if poly:
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        ax.set_xlim(min(xs) - 0.6, max(xs) + 0.6)
        ax.set_ylim(min(ys) - 0.6, max(ys) + 0.6)
    ax.grid(True, lw=0.3, alpha=0.4)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
    return path
