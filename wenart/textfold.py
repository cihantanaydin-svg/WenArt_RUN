"""Text folding without dependencies (29 Oct 2026): ``fold_ascii`` here, so code that runs inside Blender's own Python
(no jsonschema: ``wenart.building`` imports it at the top) folds room labels too (``door_states``, ``wardrobe_fronts``).
``wenart.building.fold_ascii`` is this function."""
from __future__ import annotations

import re
import unicodedata

TR_ASCII = str.maketrans({
    "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "²": "2",
})


# 4 Nov 2026 (real07, user: "where is the havuz (pool) ?", "there should have been 2 villas right?"): the drawing writes
# its labels letter-spaced ('H A V U Z', '12.00 Y O L'); three or more single letters a space apart are one word
_SPACED = re.compile(r"(?<!\S)(?:[^\W\d_] ){2,}[^\W\d_](?!\S)")


def despaced(text: str) -> str:
    """``text`` with its letter-spaced words joined (``'H A V U Z'`` -> ``'HAVUZ'``, ``'12.00 Y O L'`` ->
    ``'12.00 YOL'``); any other text as it is."""
    return _SPACED.sub(lambda m: m.group(0).replace(" ", ""), text) if " " in text else text


def fold_ascii(text: str) -> str:
    """Turkish letters -> ASCII look-alikes, other accents stripped, lower-case; letter-spaced words joined
    (``despaced``)."""
    folded = despaced(text).translate(TR_ASCII)
    folded = unicodedata.normalize("NFKD", folded)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return folded.lower()
