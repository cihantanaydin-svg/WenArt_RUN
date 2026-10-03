"""Furniture: library assets on the drawn footprints, AI layout for empty rooms (Milestone 4).

- ``catalog`` / ``catalog.json``: furniture type -> CC0 Poly Haven models with
  measured bounding boxes and the re-orientation into the piece frame; from
  Milestone 7 with ``styles`` and ``has_mattress``, merged with the Objaverse
  models of ``catalog_objaverse.json`` (CC0 / CC BY 4.0).
- ``fit``: choose and scale an asset per piece (or the parametric fallback),
  never touching the footprint; fit report. CLI ``python -m wenart.furniture.fit``
  (``--style style.json`` for refit: library models of the project's style family only).
- ``schemas``: answer schema of the layout model, size options, heights, allowed
  types per room type (one source for prompts, placer and tests).
- ``prompts``: the layout prompt per room type (English, Turkish label).
- ``placer``: deterministic shapely checks and repairs of a proposal.
- ``layout``: two model passes -> placer -> ``added_by_ai`` pieces.
- ``decor``: rule-based cushions, books and plants.
"""
