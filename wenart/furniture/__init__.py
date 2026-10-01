"""Furniture: library assets on the drawn footprints, AI layout for empty rooms (Milestone 4).

- ``catalog`` / ``catalog.json``: furniture type -> CC0 Poly Haven models with
  measured bounding boxes and the re-orientation into the piece frame.
- ``fit``: choose and scale an asset per piece (or the parametric fallback),
  never touching the footprint; fit report. CLI ``python -m wenart.furniture.fit``.
- ``layout`` / ``placer`` / ``prompts`` / ``schemas`` / ``decor``: AI layout for
  rooms the documents leave empty, deterministic checks, rule-based decor.
"""
