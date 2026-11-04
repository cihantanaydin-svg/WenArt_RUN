"""The common areas of a building with several dwellings (4 Nov 2026, lesson UL305).

User on real10: "for the kat holu (hall halls) ares like that, here 26 is not a living area, this is common use area for
people to reach to their houses, flooring roofing and any furniture should be different, this is a general rule".

The shared halls in front of the stair core and the lifts, landings, the building's entrance hall and lobbies are not a
flat's rooms: a hard-wearing stone-look floor, their own wall finish and ceiling, no furniture or decor (the user: "I was
trying to say flooring and the walls", then "ceiling also could be different if you understand roofing as ceiling"). No imports
beyond the standard library: the Blender build uses it too.
"""
from __future__ import annotations

import unicodedata
from typing import Optional

COMMON_SUBTYPE = "common"
COMMON_ROOM_WORDS = ("KAT HOLU", "BINA GIRISI", "BINA GIRIS HOLU", "APARTMAN GIRISI", "ORTAK ALAN", "MERDIVEN HOLU",
                     "ASANSOR HOLU", "ASANSOR ONU", "LOBI", "LOBBY", "LANDING", "COMMON HALL", "COMMON AREA",
                     "STAIR HALL", "LIFT LOBBY", "ELEVATOR LOBBY", "ENTRANCE LOBBY", "TREPPENHAUS", "HALL D'ENTREE")
# 4 Nov 2026 (user on real10: "THis 21 oda hall ... needs to have unique flooring and ceiling and walls"; the first
# greige paint, grey porcelain and light grey plaster read like a flat's bathroom and hall): a lobby's finishes, none of
# them used in the flats. Each slot of the style wins (``style["common_floor"]``, ``common_walls``, ``common_ceiling``).
# The floor: polished light grey marble ...
COMMON_FLOOR = {"material": "marble_slab", "colour": "light grey",
                "reason": "a common area (shared hall, UL305, UL316): polished light grey marble, a lobby's floor"}
# ... the walls: greige venetian (polished) plaster ...
COMMON_WALLS = {"material": "venetian_plaster", "colour": "greige",
                "reason": "a common area (shared hall, UL305, UL316): greige venetian plaster, a lobby's walls"}
# ... and the ceiling: warm wood slats (the user: "ceiling also could be different if you understand roofing as
# ceiling")
COMMON_CEILING = {"material": "wood_slat", "colour": None,
                  "reason": "a common area (shared hall, UL305, UL316): a wood slat ceiling, a lobby's ceiling"}

_TR = str.maketrans({"ı": "i", "İ": "I", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o",
                     "Ö": "O", "ç": "c", "Ç": "C"})


def _fold(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text or "").translate(_TR))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).upper().split())


def is_common_room(room: Optional[dict]) -> bool:
    """A building's common area (``COMMON_SUBTYPE``, a shared hall the reading inferred, or a ``COMMON_ROOM_WORDS``
    name), not a dwelling's room."""
    if not room:
        return False
    if room.get("room_subtype") == COMMON_SUBTYPE:
        return True
    if (room.get("label_inferred") or {}).get("method") == "shared_hall":
        return True
    words = " " + " ".join(_fold(room.get(k) or "") for k in ("label", "label_raw")) + " "
    return any(f" {w} " in words for w in COMMON_ROOM_WORDS)
