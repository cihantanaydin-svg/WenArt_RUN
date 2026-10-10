"""The agent's validated level edits (docs/milestone12.md §3.6, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``LEVEL_EDIT_OPS``: ``("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")``.
- ``LEVEL_EDIT_SCHEMAS``: op -> strict JSON schema of its arguments (``reason`` required; ``evidence`` where §3.6
  says so).
- ``apply_level_edit(building: dict, edit: dict) -> dict`` with the result of ``edit_ops.apply_edit``:
  ``{"accepted", "failed_checks", "score_before", "score_after", "building", "changed_ids", "rerun_from",
  "message"}``; the score is the number of critical + major L-findings (lower is better; an edit must not raise
  it); ``rerun_from`` is ``"build"``; pure.
"""
from __future__ import annotations

LEVEL_EDIT_OPS: tuple[str, ...] = ("set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance", "set_terrain")
LEVEL_EDIT_SCHEMAS: dict[str, dict] = {op: {"type": "object"} for op in LEVEL_EDIT_OPS}   # stub (lead)


def apply_level_edit(building: dict, edit: dict) -> dict:
    return {"accepted": False, "failed_checks": ["not_built_yet"], "score_before": 0.0, "score_after": 0.0,
            "building": None, "changed_ids": [], "rerun_from": "build", "message": "level edits: stub"}
