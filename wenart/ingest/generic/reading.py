"""The pipeline's furniture reading step (docs/milestone12.md §4.1, contract §13.2; owner: track R).

Contract (frozen 10 Oct 2026): ``read_furniture(build, works) -> None`` is called by ``pipeline.run_project`` after
``levels.apply_levels`` and before the type inference. It moves non-furniture symbols (room-number circles, north
arrows, axis bubbles, section marks, door-swing arcs, dimension outlines, text frames) from
``building["furniture"]`` to ``building["symbols"]`` with kind and evidence; types pieces by block names, cluster
splits and context rules; fixes misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026); and leaves no
untyped piece built (``build: false`` + ``needs_review`` list in the report).
"""
from __future__ import annotations


def read_furniture(build, works: dict) -> None:
    return None                             # stub (lead)
