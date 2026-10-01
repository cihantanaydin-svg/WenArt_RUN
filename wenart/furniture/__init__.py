"""Milestone 4 furniture: catalogue fitting, AI layout for empty rooms, decor.

Layout and decor (this package, docs/milestone4.md sections 3 and 4):

- ``schemas.py``  answer schema of the layout model, size options, heights,
  allowed types per room type (one source for prompts, placer and tests);
- ``prompts.py``  the layout prompt per room type (English, Turkish label);
- ``placer.py``   deterministic shapely checks and repairs of a proposal;
- ``layout.py``   two model passes -> placer -> ``added_by_ai`` pieces;
- ``decor.py``    rule-based cushions, books and plants.
"""
