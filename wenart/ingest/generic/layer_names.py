"""What a CAD layer's name means, in the languages of our drawings (2 Nov 2026).

What: ``layer_role(name)``: ``wall`` (masonry: duvar, wall, Mauer, mur, pared ...), ``plaster`` (the faces of a wall:
sıva, plaster, Putz, enduit ...), ``structure`` (columns and concrete walls: kolon, column, Stütze, poteau, betonarme,
perde, concrete ...) or None; ``WALL_ROLES`` are the three that draw a building's walls.

Why: real10 (user: "kolon, SIVA and DUVAR are the Turkish words translate into English and it will make sense"): the
2nd basement's reinforced-concrete outer walls were on the column layer ``kolon``; the reader chose wall layers by
evidence only, took the document's plaster (``SIVA``) and masonry (``DUVAR``) layers, left the outer ring open and the
level out. Column, plaster and wall layers all draw walls.

How: the folded name (ASCII, upper; ``_`` ``-`` ``.`` and digits split words) is matched word by word; the short
words (BA, RC, COL) only as a whole word. 22 Nov 2026 (S5, UL355): ``layer_role`` / ``layer_roles`` fall back on the
role the layer's geometry shows (``geometry_role``, registered by ``layer_geometry``) only in a drawing whose layer names
say nothing; ``name_role`` is the name's alone.
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
               "VENTANAS", "FINESTRA", "FINESTRE", "DOGRAMA", "GLAZING", "GLAZ"),     # GLAZ: the AIA layer A-GLAZ
    # 2 Nov 2026 (real03: the windbreak's glass screen on 'MYD - CAM-PER', its sliding doors on 'MYD - CAM')
    "glass": ("CAM", "CAMLAR", "CAMLI", "GLASS", "GLAS", "VERRE", "VETRO", "VIDRIO", "CURTAIN", "CURT", "GIYDIRME",
              "VITRIN", "CAMEKAN", "STOREFRONT"),       # 12 Nov 2026 (review B2 FC-09): CURT, the AIA curtain-wall word
    # 3 Nov 2026 (real09: the kitchens' and bathrooms' tile grids on 'karo' were read as stairs)
    "finish": ("KARO", "SERAMIK", "FAYANS", "KAPLAMA", "TILE", "TILES", "TILING", "FLIESEN", "FLIESE", "CARRELAGE",
               "PISO", "PAVIMENTO", "PARKE", "PARQUET", "LAMINAT", "LAMINATE", "MERMER", "MARBLE"),
    "furniture": ("TEFRIS", "TEF", "MOBILYA", "FURNITURE", "FURN", "MOEBEL", "MOBEL", "MOBILIER", "MUEBLE",
                  "MUEBLES", "ARREDO", "ARREDI", "ESYA"),
    "dimension": ("DIM", "DIMS", "DIMH", "DIMV", "DH", "DV", "OLCU", "OLCULER", "COTA", "COTAS", "BEMASSUNG",
                  "MASSE", "COTE", "COTES", "QUOTA", "QUOTE", "DIMENSION", "DIMENSIONS"),
    "axis": ("AKS", "AKSLAR", "AXIS", "AXES", "GRID", "GRIDS", "ACHSE", "ACHSEN", "RASTER", "EKSEN", "ASSE", "EJE"),
    "stair": ("MERDIVEN", "MERD", "STAIR", "STAIRS", "TREPPE", "ESCALIER", "ESCALERA", "SCALA", "BASAMAK"),
    "section": ("KESIT", "SECTION", "SCHNITT", "COUPE", "CORTE", "SEZIONE"),
    "text": ("TEXT", "TEXTS", "YAZI", "YAZILAR", "TEXTE", "TEXTO", "TESTO", "NOTE", "NOTES", "ANNO"),
    "hatch": ("HATCH", "TARAMA", "SCHRAFFUR", "HACHURE", "RAYADO", "TRATTEGGIO"),
    "site": ("VAZIYET", "SITE", "LAGEPLAN", "PLAN-MASSE", "EMPLAZAMIENTO", "PLANIMETRIA", "PEYZAJ", "LANDSCAPE"),
    # 3 Nov 2026 (real07: the WCs and basins on 'S-TEF', sıhhi tefriş): sanitary ware differs from floor to floor. Last:
    # any other word of the name decides first (real03's '00_VİTRİFİYE AKS' draws axis lines)
    "sanitary": ("VITRIFIYE", "SIHHI", "SANITARY", "SANITAER", "SANITAR", "SANITAIRE", "SANITARIO", "SANITARIOS",
                 "SANITARI", "PLUMBING"),
    # 12 Nov 2026 (review B2 FC-01/FC-04, real06: its windows' sills on 'DENIZLIK' on both faces): a window sill
    "sill": ("DENIZLIK", "DENIZLIKLER", "SILL", "SILLS", "FENSTERBANK", "APPUI", "APPUIS", "DAVANZALE", "ALFEIZAR"),
})
WALL_ROLES: tuple[str, ...] = ("wall", "plaster", "structure")
_WORD_RE = re.compile(r"[A-Z]+(?:-[A-Z]+)?")


def _words(name: str) -> set[str]:
    folded = B.fold_ascii(str(name)).upper().replace("_", " ").replace(".", " ")
    return set(_WORD_RE.findall(folded)) | set(w for part in _WORD_RE.findall(folded) for w in part.split("-"))


def name_role(name: Optional[str]) -> Optional[str]:
    """The meaning of a layer name by its words alone (the module docstring), None when no word of it is known."""
    if not name:
        return None
    words = _words(name)
    for role, vocab in ROLES.items():
        if words & set(vocab):
            return role
    return None


def layer_role(name: Optional[str]) -> Optional[str]:
    """The meaning of a layer: its name's (``name_role``), else, in a document whose layer names say nothing, the role
    its geometry and blocks show (``geometry_role``, 22 Nov 2026, S5)."""
    return name_role(name) or geometry_role(name)


def layer_roles(name: Optional[str]) -> set[str]:
    """12 Nov 2026 (review B-OPN-09): every role a word of the name has ('DUVAR-PENC': wall and window), where
    ``layer_role`` gives the first only. A word written as a wall word and a word of another role in one ('DUVARCAM',
    review B2 FC-09) has both roles."""
    if not name:
        return set()
    words = _words(name)
    roles = {role for role, vocab in ROLES.items() if words & set(vocab)}
    for w in words:
        for head in ROLES["wall"]:
            if len(w) > len(head) and w.startswith(head):
                roles |= {role for role, vocab in ROLES.items() if w[len(head):] in vocab} | {"wall"}
    if not roles:
        geo = geometry_role(name)               # 22 Nov 2026 (S5): a layer whose name says nothing
        if geo:
            roles = {geo}
    return roles


def draws_walls(name: Optional[str]) -> bool:
    return layer_role(name) in WALL_ROLES


# --- 22 Nov 2026 (S5, the user's pick "build S5, S3, S4, S6"): roles by geometry where the names say nothing ---------
# ``layer_geometry.infer_roles`` reads a document whose layer names give no role to its drawing (layers renamed L1, L2
# ..., numbered or pen-width layers) and finds each layer's role from what it draws (face pairs that close the rooms,
# door swings, dimension texts, grid bubbles, tread runs ...) and from the names of the blocks drawn on it.
# ``dxf_generic.read_page_info`` registers the result per file; ``pipeline.run_project`` clears it before a project.
# The name always comes first: a layer whose name has a role never takes one from its geometry.
_GEOMETRY: dict[str, dict[str, str]] = {}       # file -> {folded layer name: role}


def _key(name: str) -> str:
    return B.fold_ascii(str(name)).upper().strip()


def set_geometry_roles(file: str, roles: Optional[dict]) -> None:
    """Register the roles ``layer_geometry.infer_roles`` found for the layers of ``file`` whose names say nothing
    (``{layer: role}`` or ``{layer: {"role": ...}}``; an empty dict still marks the file as one whose names say
    nothing); None removes the file's entry."""
    if roles is None:
        _GEOMETRY.pop(str(file), None)
        return
    out = {}
    for k, v in roles.items():
        role = v.get("role") if isinstance(v, dict) else v
        if role:
            out[_key(k)] = role
    _GEOMETRY[str(file)] = out


def clear_geometry_roles() -> None:
    _GEOMETRY.clear()


def geometry_role(name: Optional[str]) -> Optional[str]:
    """The role the geometry gave a layer whose name says nothing (``set_geometry_roles``), None when none did or two
    documents of the project disagree about a layer of that name."""
    if not name or not _GEOMETRY:
        return None
    key = _key(name)
    found = {roles[key] for roles in _GEOMETRY.values() if key in roles}
    return found.pop() if len(found) == 1 else None


def names_silent() -> bool:
    """True while the roles of a document whose layer names say nothing are registered (``set_geometry_roles``)."""
    return bool(_GEOMETRY)
