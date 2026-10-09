"""Plausibility of rooms and furniture (docs/milestone11.md §4.2, §4.3, §6, contract §17.2).

What: ``score_room(building, room_id)`` and ``score_building(building)`` measure the checklist items F1–F9 and
R1–R4 that code can measure (back to the wall, fronts facing their group, groups complete, real sizes,
clearances, blocked doors and windows, floating pieces, room type vs size and fixtures). The agent's code critic,
the edit validator (``edit_ops.apply_edit``) and the tests use the same functions.

Contract (frozen; owner: track B): pure functions, no I/O, the building is never changed; under 50 ms per room.

``Violation = {"check": "F3", "severity": "critical" | "major" | "minor", "target": <piece/room/opening id>,
"room_id": <id>, "message": <one sentence>, "metrics": {<numbers that prove it>}}``
"""
from __future__ import annotations

SEVERITIES = ("critical", "major", "minor")

# id -> {"severity": default severity, "what": one line}; track B fills in the table (§4.2, §4.3).
CHECKS: dict[str, dict] = {}


def score_room(building: dict, room_id: str) -> dict:
    """``{"room_id", "score": 0..100, "violations": [Violation]}``."""
    raise NotImplementedError("M11 track B")


def score_building(building: dict) -> dict:
    """``{"rooms": {room_id: score_room(...)}, "mean": float, "counts": {"critical": n, "major": n, "minor": n}}``."""
    raise NotImplementedError("M11 track B")
