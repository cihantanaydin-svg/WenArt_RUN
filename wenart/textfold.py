"""Text folding without dependencies (29 Oct 2026): ``fold_ascii`` here, so code that runs inside Blender's own Python
(no jsonschema: ``wenart.building`` imports it at the top) folds room labels too (``door_states``, ``wardrobe_fronts``).
``wenart.building.fold_ascii`` is this function."""
from __future__ import annotations

import unicodedata

TR_ASCII = str.maketrans({
    "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "²": "2",
})


def fold_ascii(text: str) -> str:
    """Turkish letters -> ASCII look-alikes, other accents stripped, lower-case."""
    folded = text.translate(TR_ASCII)
    folded = unicodedata.normalize("NFKD", folded)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return folded.lower()
