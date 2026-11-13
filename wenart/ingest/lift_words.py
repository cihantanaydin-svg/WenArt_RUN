"""One machine-room test for a lift-named label (13 Nov 2026, review CODE-05: the reader, the storey signals and the
completion each had their own machine-room words, and 'MAKİNESİZ ASANSÖR', 'Makinasız', 'Makine Dairesiz' (a lift
with no machine room) were taken for a machine room in some of them and for a lift in others).

What: ``machine_room(text) -> bool``: the label names a lift's machine room (MAKİNA / MAKİNE, MAK. DAİR., MAKN,
MAHAL (asansör mahali), machine room, Maschinen-, machinerie, motor room, MOTOR), unless it says the lift has none
(makinesiz, makinasız, makine dairesiz, MRL). Used by ``completion.is_lift``, ``sheets.storeys.plan_signals`` and
``twins.lift_doors``.

How: pure, regular expressions on the ASCII-folded, lower-cased label; no project data.
"""
from __future__ import annotations

import re

from wenart import building as B

MACHINE_RE = re.compile(r"(?<![a-z])(?:makin[ae]\w*|mak\.?\s*dair\w*|makn|mahal\w*|machine\s*rooms?|maschinen\w*"
                        r"|machinerie|motor(?:\s*room)?)(?![a-z])")
MACHINE_LESS_RE = re.compile(r"(?<![a-z])(?:makin[ae]s[iu]z\w*|makin[ae]\s*dairesiz\w*|mak\.?\s*dairesiz\w*|mrl)"
                             r"(?![a-z])")


def fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def machine_room(text) -> bool:
    """Whether a label names a lift's machine room (the module docstring; pure)."""
    return bool(MACHINE_RE.search(MACHINE_LESS_RE.sub(" ", fold(text))))
