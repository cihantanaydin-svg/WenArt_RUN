"""The deterministic group solver (docs/milestone12.md §4.4, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026); deterministic (same input, same output: no random, no wall clock), pure:

- ``solve_room(building: dict, room_id: str, program: dict | None = None, *, k: int = 3,
  fixed_ids: list[str] | None = None) -> list[Candidate]`` (best first, at most ``k``). ``program`` defaults to
  ``program.room_program(building, room_id)``; ``fixed_ids``: pieces that must not move (drawn pieces always are).
  ``Candidate = {"rank": int, "score": float, "terms": {name: float}, "pieces": [furniture dicts, added_by_ai],
  "groups": [{"group_id", "group", "anchor_id", "member_ids"}], "hard_failures": [], "group_violations":
  [Violation]}``.
- ``apply_candidate(building: dict, room_id: str, candidate: dict) -> dict``: a new building with the room's
  ``added_by_ai`` pieces replaced by the candidate's pieces (drawn pieces untouched), each piece carrying
  ``group = {"group_id", "group", "role": "anchor" | "partner"}``.
"""
from __future__ import annotations

import copy
from typing import Optional


def solve_room(building: dict, room_id: str, program: Optional[dict] = None, *, k: int = 3,
               fixed_ids: Optional[list[str]] = None) -> list[dict]:
    return []                               # stub (lead)


def apply_candidate(building: dict, room_id: str, candidate: dict) -> dict:
    return copy.deepcopy(building)          # stub (lead)
