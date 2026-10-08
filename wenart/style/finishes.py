"""Milestone 10 material, finish, exterior and lighting tables (docs/milestone10.md §4.3, §4.8, §4.9; track C).

What: tables in the shape of ``wenart/style/vocabulary.py``'s own, merged into it by the vocabulary (the lead's
wiring): ``MATERIALS`` and ``FURNITURE_MATERIALS`` entries (``source``/``asset`` verified against the live APIs, or
``source: "procedural"`` with ``asset: None`` and a ``procedural`` node-group name; every entry carries ``kind``,
``flat`` (linear RGB) and ``roughness``), ``LIGHTING`` moods (with their Poly Haven HDRI), and keyword tables that
extend the vocabulary's (``FLOOR_WORDS``, ``WALL_WORDS``, ``LIGHT_WORDS``). A slug never carries a colour
(§1.6b row 14): colours are ``wenart/style/colours.py`` names.

Why a separate module: the vocabulary is lead-owned and read by every stage (and by Blender's Python, which has no
PyYAML: this module stays pure Python); track C fills these tables without touching it.

The lead's stub (8 Oct 2026): every table is empty; the vocabulary merges them unchanged.
"""
from __future__ import annotations

MATERIALS: dict[str, dict] = {}
FURNITURE_MATERIALS: dict[str, dict] = {}
LIGHTING: dict[str, dict] = {}
FLOOR_WORDS: list[tuple[str, str]] = []
WALL_WORDS: list[tuple[str, str]] = []
LIGHT_WORDS: list[tuple[str, str]] = []
