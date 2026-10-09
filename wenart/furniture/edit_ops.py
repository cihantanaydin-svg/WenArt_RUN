"""Validated furniture and room edits of the agent (docs/milestone11.md §3.2, §5, contract §17.2).

What: ``apply_edit(building, edit)`` applies one edit (move, rotate, resize, change_type, swap_model, add,
add_group, remove, relayout_room, set_room_type) to a COPY of the building and accepts it only when the code checks
pass (inside the room, no overlap, clearances, door swing, window band, walkway, drawn-piece rules of CLAUDE.md)
and the room's plausibility score does not drop.

Contract (frozen; owner: track B):

- ``EDIT_SCHEMAS``: op -> JSON schema of the edit's arguments (the agent's tool parameters). Every edit also
  carries ``reason`` (str), ``round`` (int), ``log_seq`` (int), ``model`` (str).
- ``apply_edit(building, edit, *, catalog=None) -> {"accepted": bool, "failed_checks": [str],
  "score_before": float, "score_after": float, "building": <new building> | None, "changed_ids": [str],
  "rerun_from": "refit" | "layout", "message": str}``; pure: the input is never changed.
- Labels: a changed drawn piece keeps ``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height``
  and gets ``adjusted_by_ai = {reason, round, log_seq, model, changed}``; an added piece is ``added_by_ai``;
  an inferred value sets ``inferred: true``.
"""
from __future__ import annotations

EDIT_OPS = ("move", "rotate", "resize", "change_type", "swap_model", "add", "add_group", "remove",
            "relayout_room", "set_room_type")

# op -> JSON schema of the arguments; track B fills it in.
EDIT_SCHEMAS: dict[str, dict] = {}


def apply_edit(building: dict, edit: dict, *, catalog=None) -> dict:
    raise NotImplementedError("M11 track B")
