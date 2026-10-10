"""A room's program: its functional groups (docs/milestone12.md §4.3, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026):

- ``room_program(building: dict, room_id: str, brief: dict | None = None, choices: dict | None = None) -> dict``:
  ``{"room_id", "zones": [{"zone_id", "kind", "polygon"}], "groups": [{"group_id", "group", "anchor_id": str | None,
  "required": bool, "options": [str], "chosen": str | None, "drawn": bool}], "reason"}``. ``group`` is a key of
  ``groups.yaml``; a group whose anchor is drawn has ``drawn: true`` and is only completed. ``choices``
  (``{group_id: option}``) are the VLM's picks among ``options``; unknown keys are ignored. Pure.
"""
from __future__ import annotations

from typing import Optional


def room_program(building: dict, room_id: str, brief: Optional[dict] = None, choices: Optional[dict] = None) -> dict:
    return {"room_id": room_id, "zones": [], "groups": [], "reason": "stub"}     # stub (lead)
