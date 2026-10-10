"""Group checks G1–G14 (docs/milestone12.md §4.6, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026); pure, no I/O, the building is never changed:

- ``CHECKS``: ``("G1", ..., "G14")``.
- ``check_room(building: dict, room_id: str) -> list[Violation]`` and ``check_building(building: dict) ->
  {"rooms": {room_id: [Violation]}, "counts": {"critical": n, "major": n, "minor": n}}`` with the M11
  ``Violation = {"check", "severity", "target", "room_id", "message", "metrics"}``; the messages name the numbers
  ("TV unit 52° off the sofa axis, needs ≤ 10°").
"""
from __future__ import annotations

CHECKS: tuple[str, ...] = tuple(f"G{i}" for i in range(1, 15))


def check_room(building: dict, room_id: str) -> list[dict]:
    return []                               # stub (lead)


def check_building(building: dict) -> dict:
    return {"rooms": {}, "counts": {"critical": 0, "major": 0, "minor": 0}}    # stub (lead)
