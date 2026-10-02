"""Expected elements per view (docs/milestone5.md §1.4, §5.1): the binding signatures.

What: for every view, the doors, windows, furniture and decor the Cycles
render shows (from the object-index pass via ``wenart.views``), each with its
role (required / optional / ignore), boxes, visibility and evidence, plus a
non-circular cross-check against the building JSON projected with a depth
test. The polish prompt, the gate's CPU negatives, the controls selection and
the vision check all read this.

Imports only stdlib, numpy, yaml, ``wenart.views`` and ``wenart.geometry``
(no PIL at import time, no torch). Written as a skeleton by F0; area D fills
the bodies.

Contract (§1.4):

- ``expected_view(view, scene_manifest, building, cfg=None) -> {"camera",
  "room_id", "room_type", "size": [W, H], "elements": [...],
  "json_crosscheck": {...}}``; elements sorted by descending pixels; ``cfg``
  None = ``check.yaml`` of this package.
- ``expected_views(project_out, render_dir=None) -> {camera: expected_view}``:
  pure (only the ``expected`` subcommand writes ``check/expected_views.json``).
- ``sweep_views(expected_views, n) -> [camera]``: the views with the most
  required elements, at most one per room, ties by camera name.
- ``largest_required(expected) -> element | None``.
"""
from __future__ import annotations

from typing import Optional

from wenart import geometry, views  # noqa: F401  (used by the implementation, area D)


def expected_view(view: "views.View", scene_manifest: dict, building: dict, cfg: Optional[dict] = None) -> dict:
    """Expected elements of one view and its building-JSON cross-check (§5.1)."""
    raise NotImplementedError("wenart.vision_check.expected.expected_view: area D")


def expected_views(project_out, render_dir=None) -> dict:
    """``{camera: expected_view(...)}`` for every view of the project (pure, writes nothing)."""
    raise NotImplementedError("wenart.vision_check.expected.expected_views: area D")


def sweep_views(expected_views: dict, n: int) -> list:
    """Up to ``n`` cameras with the most required elements, at most one per room, ties by camera name."""
    raise NotImplementedError("wenart.vision_check.expected.sweep_views: area D")


def largest_required(expected: dict) -> Optional[dict]:
    """The required element with the most pixels of one ``expected_view`` result, or None."""
    raise NotImplementedError("wenart.vision_check.expected.largest_required: area D")
