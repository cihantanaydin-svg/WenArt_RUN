"""Hand-made rooms for the Milestone 11 layout-engine tests (plausibility, groups, edits, inference).

A rectangular room ``w`` x ``h`` m with 0.1 m walls around it (ids w_s, w_e, w_n, w_w), a door on the south wall
(0.9 m, opening into the room) and optionally a window on the north wall; ``fp`` makes a furniture dict.
"""
from __future__ import annotations

from typing import Optional

ROOM_ID = "r_L0_oda"


def building(w: float = 5.0, h: float = 4.0, room_type: str = "bedroom", door_x: float = 1.0,
             window: Optional[tuple[float, float]] = (2.5, 1.2), sill: Optional[float] = 0.9,
             furniture: Optional[list] = None, subtype=None) -> dict:
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [0.0, -0.05], "end": [w, -0.05], "thickness": 0.1,
         "exterior": True, "status": "verified", "evidence": []},
        {"id": "w_e", "level_id": "L0", "start": [w + 0.05, 0.0], "end": [w + 0.05, h], "thickness": 0.1,
         "exterior": True, "status": "verified", "evidence": []},
        {"id": "w_n", "level_id": "L0", "start": [0.0, h + 0.05], "end": [w, h + 0.05], "thickness": 0.1,
         "exterior": True, "status": "verified", "evidence": []},
        {"id": "w_w", "level_id": "L0", "start": [-0.05, 0.0], "end": [-0.05, h], "thickness": 0.1,
         "exterior": True, "status": "verified", "evidence": []},
    ]
    openings = [{"id": "d1", "type": "door", "level_id": "L0", "wall_id": "w_s", "center": [door_x, -0.05],
                 "width": 0.9, "swing_side": ROOM_ID, "status": "verified", "evidence": []}]
    if window is not None:
        openings.append({"id": "win1", "type": "window", "level_id": "L0", "wall_id": "w_n",
                         "center": [window[0], h + 0.05], "width": window[1], "sill_height": sill,
                         "status": "verified", "evidence": []})
    room = {"id": ROOM_ID, "level_id": "L0", "label": "Oda", "label_raw": "Oda", "room_type": room_type,
            "room_subtype": subtype, "polygon": [[0.0, 0.0], [w, 0.0], [w, h], [0.0, h]], "area_computed": w * h,
            "area_label": None, "has_documented_furniture": bool(furniture), "status": "verified",
            "evidence": [{"file": "plan.dxf", "method": "derived", "confidence": 1.0}]}
    return {"schema_version": "1", "project": {"name": "m11"},
            "levels": [{"id": "L0", "label": "Zemin Kat", "elevation": 0.0, "ceiling_height": 2.7}],
            "walls": walls, "openings": openings, "rooms": [room], "furniture": list(furniture or []),
            "decor": [], "conflicts": [], "unverified": [], "warnings": []}


def fp(pid: str, ftype: str, center, size, rotation: float = 0.0, front: Optional[float] = "auto",
       source: str = "from_documents", status: str = "verified", **extra) -> dict:
    """A furniture dict; ``front`` "auto" = the footprint's own front ((270 + rotation) mod 360), None = no front."""
    if front == "auto":
        front = (270.0 + rotation) % 360.0
    item = {"id": pid, "level_id": "L0", "room_id": ROOM_ID, "type": ftype, "type_raw": None, "source": source,
            "footprint": {"center": [float(center[0]), float(center[1])], "size": [float(size[0]), float(size[1])],
                          "rotation_deg": float(rotation)},
            "front_deg": front, "height": None, "asset": None, "status": status,
            "evidence": [{"file": "plan.dxf", "method": "vector", "confidence": 1.0, "entity": pid}]}
    item.update(extra)
    return item
