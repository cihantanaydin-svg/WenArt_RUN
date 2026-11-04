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
# the common hall's floor when the brief names none (``style["common_floor"]`` wins): large stone-look porcelain
COMMON_FLOOR = {"material": "tiles_large_porcelain", "colour": "grey",
                "params": {"pattern": "grid", "tile_size_m": [0.6, 0.6], "grout_m": 0.002, "grout_colour": "grey"},
                "reason": "a common area (shared hall, UL305): hard-wearing stone-look porcelain 60 x 60 cm"}

# ... its walls (``style["common_walls"]`` wins): a washable satin paint in greige, not the flats' wall colour ...
COMMON_WALLS = {"material": "plaster_white", "colour": "greige",
                "reason": "a common area (shared hall, UL305): washable satin wall paint in greige"}
# ... and its ceiling (``style["common_ceiling"]`` wins): plain matte plaster in light grey (the user: "ceiling also could
# be different if you understand roofing as ceiling")
COMMON_CEILING = {"material": "plaster_white", "colour": "light grey",
                  "reason": "a common area (shared hall, UL305): plain matte plaster ceiling in light grey"}

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
