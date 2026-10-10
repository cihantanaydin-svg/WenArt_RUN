"""The pipeline's level step (docs/milestone12.md §3.1–§3.3, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026): ``apply_levels(build, works) -> None`` is called by ``pipeline.run_project`` once every
level is assembled, before ``reading.read_furniture`` and the type inference. It reads every level mark of the
project's drawings (texts, block attributes, mark symbols; ``wenart.levels.marks``) into ``building["level_marks"]``,
moves furniture pieces that are level-mark symbols to ``building["symbols"]`` (kind ``level_mark``) and fills the
level fields of §3.2 (``wenart.levels.model.infer_levels``). ``works``: ``{page key: PageWork}`` of the pipeline.
"""
from __future__ import annotations


def apply_levels(build, works: dict) -> None:
    return None                             # stub (lead)
