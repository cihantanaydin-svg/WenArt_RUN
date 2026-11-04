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
# 2 Nov 2026 (the reading's conventions record, wenart.reading_check.conventions): the other layers of a drawing, for
# the record and the checks only (the walls' choice uses the three wall roles above)
ROLES.update({
    "door": ("KAPI", "KAPILAR", "DOOR", "DOORS", "TUR", "TUER", "TUEREN", "PORTE", "PORTES", "PUERTA", "PUERTAS",
             "PORTA", "PORTE-FENETRE"),
    # 4 Nov 2026 (real17: the window size tags on 'penc-yazi'): PENC, the short form of PENCERE
    "window": ("PENCERE", "PENCERELER", "PENC", "WINDOW", "WINDOWS", "FENSTER", "FENETRE", "FENETRES", "VENTANA",
               "VENTANAS", "FINESTRA", "FINESTRE", "DOGRAMA", "GLAZING"),
    # 2 Nov 2026 (real03: the windbreak's glass screen on 'MYD - CAM-PER', its sliding doors on 'MYD - CAM')
    "glass": ("CAM", "CAMLAR", "GLASS", "GLAS", "VERRE", "VETRO", "VIDRIO", "CURTAIN", "GIYDIRME", "VITRIN", "CAMEKAN",
              "STOREFRONT"),
    # 3 Nov 2026 (real09: the kitchens' and bathrooms' tile grids on 'karo' were read as stairs)
    "finish": ("KARO", "SERAMIK", "FAYANS", "KAPLAMA", "TILE", "TILES", "TILING", "FLIESEN", "FLIESE", "CARRELAGE",
               "PISO", "PAVIMENTO", "PARKE", "PARQUET", "LAMINAT", "LAMINATE", "MERMER", "MARBLE"),
    "furniture": ("TEFRIS", "TEF", "MOBILYA", "FURNITURE", "FURN", "MOEBEL", "MOBEL", "MOBILIER", "MUEBLE",
                  "MUEBLES", "ARREDO", "ARREDI", "ESYA"),
    "dimension": ("DIM", "DIMS", "DIMH", "DIMV", "DH", "DV", "OLCU", "OLCULER", "COTA", "COTAS", "BEMASSUNG",
                  "MASSE", "COTE", "COTES", "QUOTA", "QUOTE", "DIMENSION", "DIMENSIONS"),
    "axis": ("AKS", "AKSLAR", "AXIS", "AXES", "GRID", "GRIDS", "ACHSE", "ACHSEN", "RASTER", "EKSEN", "ASSE", "EJE"),
    "stair": ("MERDIVEN", "STAIR", "STAIRS", "TREPPE", "ESCALIER", "ESCALERA", "SCALA", "BASAMAK"),
    "section": ("KESIT", "SECTION", "SCHNITT", "COUPE", "CORTE", "SEZIONE"),
    "text": ("TEXT", "TEXTS", "YAZI", "YAZILAR", "TEXTE", "TEXTO", "TESTO", "NOTE", "NOTES", "ANNO"),
    "hatch": ("HATCH", "TARAMA", "SCHRAFFUR", "HACHURE", "RAYADO", "TRATTEGGIO"),
    "site": ("VAZIYET", "SITE", "LAGEPLAN", "PLAN-MASSE", "EMPLAZAMIENTO", "PLANIMETRIA", "PEYZAJ", "LANDSCAPE"),
    # 3 Nov 2026 (real07: the WCs and basins on 'S-TEF', sıhhi tefriş): sanitary ware differs from floor to floor. Last:
    # any other word of the name decides first (real03's '00_VİTRİFİYE AKS' draws axis lines)
    "sanitary": ("VITRIFIYE", "SIHHI", "SANITARY", "SANITAER", "SANITAR", "SANITAIRE", "SANITARIO", "SANITARIOS",
                 "SANITARI", "PLUMBING"),
})
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
