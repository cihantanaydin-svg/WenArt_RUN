"""The library models that are only a photo card (1 Nov 2026, lesson UL237; user on real04 run 20261031-194116-full:
"This is only a photo if that's the case don't use this model ever again").

What: ``results/library/photo_cards.json`` holds ``{"cards": {model id: record}, "cleared": {...}}``, written by
``python -m wenart.assets.audit.photocard`` (the CPU rule from the audit's committed measurements, the pod's mesh
check of the model files). ``card(entry)`` is a model's record when it applies; ``reason(entry)`` the sentence
``catalog.unusable_reason`` gives. A card is never used, in any licence mode (``catalog.usable``), like a model the
user rejected.

Why: a flat board carrying a product photo renders as a picture of a piece, not as the piece; the user saw one in a
render (the "Wood and Epoxy Coffee Table"), the ranking sheets of 31 Oct 2026 show more; code finds them before a
render does.

How: pure; the file is read once per path (cached; ``reset()`` for tests); a missing or broken file means no cards.
A record names the file it was measured on (``sha256_glb``): a republished model (another file) is not judged by an
old record. A fitted asset dict is looked up by ``asset_id`` like a catalogue entry by ``id``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

PHOTO_CARDS_PATH = Path(__file__).resolve().parents[2] / "results" / "library" / "photo_cards.json"
RULE = "photo_card (UL237)"
_CACHE: dict = {}


def reset() -> None:
    _CACHE.clear()


def cards(path: Optional[Path] = None) -> dict[str, dict]:
    """``{model id: record}`` of the store's cards (cached per path)."""
    p = Path(path) if path is not None else PHOTO_CARDS_PATH
    key = str(p)
    if key not in _CACHE:
        rows: dict[str, dict] = {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for iid, rec in (data.get("cards") or {}).items():
                if isinstance(rec, dict) and rec.get("card", True):
                    rows[str(iid)] = rec
        except (OSError, ValueError, AttributeError):
            rows = {}
        _CACHE[key] = rows
    return _CACHE[key]


def card(entry: dict, path: Optional[Path] = None) -> Optional[dict]:
    """The photo-card record of a catalogue entry or a fitted asset (by ``id``, ``asset_id`` or ``uid``), None when it
    is none or the record was measured on another file than the entry's ``sha256_glb``."""
    rows = cards(path)
    if not rows or not isinstance(entry, dict):
        return None
    for key in ("id", "asset_id", "uid"):
        value = entry.get(key)
        if value and str(value) in rows:
            rec = rows[str(value)]
            sha, own = rec.get("sha256_glb"), entry.get("sha256_glb")
            if sha and own and sha != own:
                return None
            return rec
    return None


def reason(entry: dict, path: Optional[Path] = None) -> Optional[str]:
    """Why a photo card is never used, None when the entry is none."""
    rec = card(entry, path)
    if rec is None:
        return None
    how = "the mesh check of its file" if rec.get("source") == "mesh" else "the audit's measurement of its mesh"
    why = str(rec.get("reason") or "a photo card, not a 3D object (UL237)")
    if "UL237" not in why:
        why = f"a photo card, not a 3D object (UL237): {why}"
    return f"{why} ({how}; never used on any project, {RULE}, results/library/photo_cards.json)"
