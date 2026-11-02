"""What a CAD layer's name means, in the languages of our drawings (2 Nov 2026).

What: ``layer_role(name)``: ``wall`` (masonry: duvar, wall, Mauer, mur, pared ...), ``plaster`` (the faces of a wall:
sıva, plaster, Putz, enduit ...), ``structure`` (columns and concrete walls: kolon, column, Stütze, poteau, betonarme,
perde, concrete ...) or None; ``WALL_ROLES`` are the three that draw a building's walls.

Why: real10 (user: "kolon, SIVA and DUVAR are the Turkish words translate into English and it will make sense"): the
2nd basement's reinforced-concrete outer walls were on the column layer ``kolon``; the reader chose wall layers by
evidence only, took the document's plaster (``SIVA``) and masonry (``DUVAR``) layers, left the outer ring open and the
level out. Column, plaster and wall layers all draw walls.

How: the folded name (ASCII, upper; ``_`` ``-`` ``.`` and digits split words) is matched word by word; the short
words (BA, RC, COL) only as a whole word.
"""
from __future__ import annotations

import re
from typing import Optional

from wenart import building as B

ROLES: dict[str, tuple[str, ...]] = {
    "wall": ("DUVAR", "DUVARLAR", "WALL", "WALLS", "A-WALL", "MUR", "MURS", "MAUER", "MAUERWERK", "WAND", "WANDE",
             "WAENDE", "PARED", "PAREDES", "MURO", "MURI", "PARETE", "PARETI", "TUGLA", "BRICK", "MASONRY", "GAZBETON",
             "YTONG"),
    "plaster": ("SIVA", "PLASTER", "PUTZ", "ENDUIT", "INTONACO", "ENLUCIDO", "REVOQUE", "SIVALAR"),
    "structure": ("KOLON", "KOLONLAR", "COLUMN", "COLUMNS", "COL", "COLS", "STUTZE", "STUETZE", "STUTZEN", "POTEAU",
                  "POTEAUX", "PILAR", "PILARES", "COLONNA", "COLONNE", "PILASTRO", "BETONARME", "BA", "PERDE",
                  "BETON", "CONCRETE", "RC", "STAHLBETON", "STB", "VOILE", "SHEAR", "TASIYICI", "STRUCTURE",
                  "STRUCTURAL", "STRUKTUR"),
}
WALL_ROLES: tuple[str, ...] = ("wall", "plaster", "structure")
_WORD_RE = re.compile(r"[A-Z]+(?:-[A-Z]+)?")


def layer_role(name: Optional[str]) -> Optional[str]:
    """The meaning of a layer name (the module docstring), None when no word of it is known."""
    if not name:
        return None
    folded = B.fold_ascii(str(name)).upper().replace("_", " ").replace(".", " ")
    words = set(_WORD_RE.findall(folded)) | set(w for part in _WORD_RE.findall(folded) for w in part.split("-"))
    for role, vocab in ROLES.items():
        if words & set(vocab):
            return role
    return None


def draws_walls(name: Optional[str]) -> bool:
    return layer_role(name) in WALL_ROLES
