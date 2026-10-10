"""Level checks L1–L7 (docs/milestone12.md §3.5, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``CHECKS``: ``("L1", ..., "L7")``.
- ``check_levels(building: dict, scene_manifest: dict | None = None, render_manifest: dict | None = None)
  -> list[Violation]`` with ``Violation = {"check", "severity", "target", "room_id", "message", "metrics"}``
  (the M11 format); pure, no I/O; L7 needs the manifests and is skipped without them.
"""
from __future__ import annotations

from typing import Optional

CHECKS: tuple[str, ...] = ("L1", "L2", "L3", "L4", "L5", "L6", "L7")


def check_levels(building: dict, scene_manifest: Optional[dict] = None,
                 render_manifest: Optional[dict] = None) -> list[dict]:
    return []                               # stub (lead)
