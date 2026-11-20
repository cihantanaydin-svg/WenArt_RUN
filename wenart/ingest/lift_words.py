"""The machine-room test for a lift-named label (13 Nov 2026, review CODE-05; 19 Nov 2026, merge of reader A: one test,
``building.machine_room``, with this branch's cases added as extra conditions).

What: ``machine_room(text) -> bool``: the label names a lift's machine room by ``building.machine_room`` (reader A's
test: ASANSÖR MAK..., MAKİNA DAİRESİ, MAKN., MAK. DAİR., machine room ...; it exempts 'without a machine room':
makinesiz, makinasız, makine dairesiz, MRL), or, for a lift-named label only, by the reader's old words (MAKİNA /
MAKİNE alone, MAHAL as in 'asansör mahali', Maschinen-, machinerie, MOTOR). Used by ``completion.is_lift``,
``sheets.storeys.plan_signals`` and ``twins.lift_doors`` (its ``_machine``).

How: pure, regular expressions on the ASCII-folded, lower-cased label; no project data.
"""
from __future__ import annotations

import re

from wenart import building as B

EXTRA_RE = re.compile(r"(?<![a-z])(?:makin[ae]\w*|mahal\w*|maschinen\w*|machinerie|motor(?:\s*room)?)(?![a-z])")


def fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def machine_room(text) -> bool:
    """Whether a (lift-named) label names a lift's machine room (the module docstring; pure)."""
    label = fold(text)
    return B.machine_room(label) or bool(EXTRA_RE.search(B.MACHINE_LESS_RE.sub(" ", label)))
