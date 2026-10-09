"""Type inference for drawn pieces the documents leave unclear (docs/milestone11.md §6, CLAUDE.md furniture rules,
contract §17.2): an unknown footprint that holds other pieces is a rug or a group outline; one that matches a
type's size table, room and position rule gets that type, marked ``inferred``. Pure; owner: track B."""
from __future__ import annotations


def infer_types(building: dict) -> list[dict]:
    """``[{"piece_id", "type", "reason", "confidence", "evidence": {...}}]`` (proposals; the building is unchanged)."""
    raise NotImplementedError("M11 track B")


def apply_inferences(building: dict, proposals: list[dict]) -> dict:
    """A copy of the building with the proposals applied (``inferred: true``, evidence method ``inferred``)."""
    raise NotImplementedError("M11 track B")
