"""Functional furniture groups (docs/milestone11.md §6, contract §17.2): dining set, bed set, living set,
desk set, kitchen run. ``place_group`` places a whole group as one unit (anchor piece + members with their relative
offsets and facing) and checks it with the placer. Pure; owner: track B."""
from __future__ import annotations

GROUPS = ("dining_set", "bed_set", "living_set", "desk_set", "kitchen_run")


def place_group(building: dict, room_id: str, group: str, anchor: dict | None = None) -> dict:
    """``{"ok": bool, "pieces": [furniture dicts, added_by_ai], "failed": [str], "reason": str}``."""
    raise NotImplementedError("M11 track B")
