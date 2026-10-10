"""Levels inferred where the documents are silent (docs/milestone12.md §3.3, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026); every function is pure (returns a new building) and marks what it infers with
``inferred: true`` and evidence method ``inferred``:

- ``infer_levels(building: dict, brief: dict | None = None) -> dict``: room ``floor_offset_m``, door ``threshold_z``,
  ``site.ground.points``, ``site.terrain``, ``site.entrances``, ``site.plinth`` from ``building["level_marks"]`` and
  the rules of §3.3 (D3a: 0.15 m rise when nothing about the ground is drawn).
"""
from __future__ import annotations

import copy
from typing import Optional


def infer_levels(building: dict, brief: Optional[dict] = None) -> dict:
    return copy.deepcopy(building)          # stub (lead): unchanged until track L builds §3.3
