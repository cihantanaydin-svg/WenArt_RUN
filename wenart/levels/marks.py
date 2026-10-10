"""Level marks (KOT) in every form the drawings use (docs/milestone12.md §3.1, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``parse_mark(text: str) -> dict | None``: one text or attribute value -> ``{"value": float, "relative": bool,
  "absolute": float | None, "kind_hint": str | None, "raw": str}`` or None when it is no level mark. ``kind_hint``
  comes from the keyword (``floor``, ``slab_top``, ``ground_natural``, ``ground_finished``, ``plinth``, ``entrance``,
  ``slope_top``, ``datum``) or None. Pure, no I/O. Track R uses it to keep marks out of the furniture.
- ``MARK_ATTRIBUTE_TAGS``: block attribute tags that hold level marks (``KOT``, ``KOT2``, ``KOT-BINA``, ...).
"""
from __future__ import annotations

import re
from typing import Optional

MARK_ATTRIBUTE_TAGS: tuple[str, ...] = ("KOT", "KOT2", "KOT-BINA", "KOT-ARAZI", "BDK", "TZK", "SBK", "ELEV", "LEVEL")

# Stub (lead): the forms of today's sheets reader (units_check.MARK_RE); track L widens it to §3.1.
_SIMPLE = re.compile(r"^\s*(?:KOT\s*)?([±+\-]?)\s*(\d{1,4}[.,]\d{2,3})\s*(?:M)?\s*$", re.IGNORECASE)


def parse_mark(text: str) -> Optional[dict]:
    m = _SIMPLE.match(text or "")
    if not m:
        return None
    sign = -1.0 if m.group(1) == "-" else 1.0
    value = sign * float(m.group(2).replace(",", "."))
    relative = bool(m.group(1)) or abs(value) < 100.0
    return {"value": value, "relative": relative, "absolute": None if relative else value, "kind_hint": None,
            "raw": text}
