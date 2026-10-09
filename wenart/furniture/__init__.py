"""Furniture: library assets on the drawn footprints, AI layout for empty rooms (Milestone 4).

- ``catalog`` / ``catalog.json``: furniture type -> CC0 Poly Haven models with
  measured bounding boxes and the re-orientation into the piece frame; from
  Milestone 7 with ``styles`` and ``has_mattress``, merged with the Objaverse
  models of ``catalog_objaverse.json`` (CC0 / CC BY 4.0).
- ``fit``: choose and scale an asset per piece (or the parametric fallback),
  never touching the footprint; fit report. CLI ``python -m wenart.furniture.fit``
  (``--style style.json`` for refit: library models of the project's style family only).
  Milestone 8: ranked by real size, judge quality, aspect, source (generated last);
  bed frames with a deck; library decor (cushion, plant, rug, wall art) by host id.
- ``schemas``: answer schema of the layout model, size options, heights, allowed
  types per room type (one source for prompts, placer and tests).
- ``prompts``: the layout prompt per room type (English, Turkish label).
- ``placer``: deterministic shapely checks and repairs of a proposal.
- ``layout``: two model passes -> placer -> ``added_by_ai`` pieces.
- ``decor``: rule-based cushions, books and plants; Milestone 8: rugs under furniture
  groups and wall art above sofas, beds and dressers.
- Milestone 11 (docs/milestone11.md §6, contract §17.2): ``plausibility`` (the code critic: checks F1-F9, R1-R4 and
  a score per room), ``edit_ops`` (the agent's validated edits), ``groups`` (functional groups placed as one unit),
  ``infer`` (types of unclear drawn pieces, rug outlines).
"""
