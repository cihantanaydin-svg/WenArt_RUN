"""Milestone 10 named colours (docs/milestone10.md §4.2; track C).

What: ``NAMES`` (the colour names, lower case, single spaces), ``MODIFIERS``, ``ALIASES`` (other spellings -> a
name) and, from track C, the documented sRGB value and source of each name with ``linear_rgb(name, modifiers=())``
(IEC 61966-2-1 transfer; CIELAB modifiers). Every name is a §4.2 colour with a cited sRGB value; unknown words are
listed by the style profile, never guessed.

The lead's stub (8 Oct 2026): empty tables; consumers fall back to their own lists until track C fills this module.
"""
from __future__ import annotations

NAMES: tuple[str, ...] = ()
MODIFIERS: tuple[str, ...] = ("light", "dark", "pale", "deep", "warm", "cool", "muted")
ALIASES: dict[str, str] = {}
