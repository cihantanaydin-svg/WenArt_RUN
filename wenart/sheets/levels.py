"""Levels of the plan regions (docs/milestone10.md §3.1 item 3).

What: ``assign_levels(plans, needs_review, warnings)`` gives every plan region (``use: read``) its level from its
title: order, label, kind (``basement``, ``floor``, ``attic``) and how it was decided (``title`` or ``assumed``).

Why: the pipeline stacks the levels by order and the heights map the section's slab bands to them bottom-up.

How: ``level_of`` reads the level word through the M10 level-word table here (Turkish, English, German, French;
``wenart.building.normalise_level_label`` of M2-M9 is unchanged): ``BODRUM`` = -1, ``ZEMİN`` = 0, ``1. KAT`` = 1, ...
An attic (``ÇATI KAT``, ``ATTIC``, ``DACHGESCHOSS``, ``COMBLES``) is the top level: one above the highest other
titled level (at least 1). An untitled plan gets a level only when it is the project's only plan (``L0``
"Ground floor", as M7), when exactly one level between the titled ones is free, or (real06, 24 Oct 2026: two
untitled plans) when no plan is titled and the plans' own floor marks order them: each plan's floor mark (its most
frequent level mark, ``floor_mark``) at least ``FLOOR_STEP_M`` apart, the lowest one within ``GROUND_BAND_M`` of
±0.00 the ground floor, the others counted from it (``assumed``, listed as inferred); otherwise it needs review.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from wenart import building as B

# Level words (§3.1 item 3): (order or "top", kind, label, pattern, language).
LEVEL_WORDS: list[tuple[object, str, str, str, str]] = [
    ("top", "attic", "Çatı Katı", r"\bCATI KATI?\b", "tr"),
    ("top", "attic", "Attic", r"\bATTIC\b|\bLOFT\b", "en"),
    ("top", "attic", "Dachgeschoss", r"\bDACHGESCHOSS\b", "de"),
    ("top", "attic", "Combles", r"\bCOMBLES\b", "fr"),
    (-1, "basement", "Bodrum Kat", r"\bBODRUM\b", "tr"),
    (-1, "basement", "Basement", r"\bBASEMENT\b", "en"),
    (-1, "basement", "Untergeschoss", r"\bUNTERGESCHOSS\b|\bKELLER(?:GESCHOSS)?\b", "de"),
    (-1, "basement", "Sous-sol", r"\bSOUS-SOL\b|\bSOUS SOL\b", "fr"),
    (0, "floor", "Zemin Kat", r"\bZEMIN\b", "tr"),
    (0, "floor", "Ground Floor", r"\bGROUND\b", "en"),
    (0, "floor", "Erdgeschoss", r"\bERDGESCHOSS\b", "de"),
    (0, "floor", "Rez-de-chaussée", r"\bREZ-DE-CHAUSSEE\b|\bREZ DE CHAUSSEE\b", "fr"),
]
_LEVEL_RE = [(o, k, lab, re.compile(p), lang) for o, k, lab, p, lang in LEVEL_WORDS]
_NTH_RE = [
    (re.compile(r"\b(\d{1,2})\s*\.\s*KAT\b"), "tr", "{n}. Kat"),
    (re.compile(r"\b(\d{1,2})\s*(?:ST|ND|RD|TH)\s+FLOOR\b"), "en", "{n}th Floor"),
    (re.compile(r"\b(FIRST|SECOND|THIRD|FOURTH)\s+FLOOR\b"), "en", "{w} Floor"),
    (re.compile(r"\b(\d{1,2})\s*\.\s*(?:OG|OBERGESCHOSS)\b"), "de", "{n}. Obergeschoss"),
    (re.compile(r"\b(\d{1,2})\s*(?:ER|E|EME)\s+ETAGE\b"), "fr", "{n}e étage"),
]
_ORDINALS = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4}


@dataclass
class LevelWord:
    order: Optional[int]          # None = the top level (attic)
    kind: str                     # basement | floor | attic
    label: str
    word: str
    language: str


def level_of(text: str) -> Optional[LevelWord]:
    """The level a title names: basement -1, ground 0, ``n. KAT`` / ``n-th FLOOR`` / ``n. OG`` n, attic = the top."""
    folded = _fold(text)
    for order, kind, label, pattern, lang in _LEVEL_RE:
        m = pattern.search(folded)
        if m:
            return LevelWord(order=None if order == "top" else int(order), kind=kind, label=label, word=m.group(0),
                             language=lang)
    for pattern, lang, label in _NTH_RE:
        m = pattern.search(folded)
        if m:
            g = m.group(1)
            n = _ORDINALS[g] if g in _ORDINALS else int(g)
            if n == 0:
                continue
            text_label = label.format(n=n, w=g.capitalize())
            if lang == "en" and label.startswith("{n}"):
                text_label = f"{n}{_suffix(n)} Floor"
            return LevelWord(order=n, kind="floor", label=text_label, word=m.group(0), language=lang)
    return None


def _suffix(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _fold(text: str) -> str:
    return " ".join(B.fold_ascii(text).upper().split())


ASSUMED_GROUND = ("Ground floor", 0)
FLOOR_STEP_M = 2.0                  # untitled plans ordered by floor marks: marks >= one storey apart
GROUND_BAND_M = (-1.2, 1.5)         # the lowest floor mark in this band (metres from ±0.00) is the ground floor


def floor_mark(region) -> Optional[float]:
    """The floor level a plan's level marks give (real06: ``+0,50`` three times and ``±0,00`` outside -> 0.50): the
    most frequent value among the marks that point at a mark symbol, the highest one on a tie; None without one."""
    from wenart.sheets import units_check as UC

    segs = UC.segments(region.strokes())
    values = [round(rec["value"], 2) for t, rec in UC.mark_records(region.texts) if UC.mark_point(t, segs)]
    if not values:
        return None
    counts = Counter(values)
    return max(counts, key=lambda v: (counts[v], v))


def _by_floor_marks(untitled: list, warnings: list) -> bool:
    """Levels of untitled plans from their floor marks (no plan titled); False (nothing set) when a plan has no
    floor mark, two marks are less than a storey apart, or no mark is near ±0.00."""
    marks = {id(r): floor_mark(r) for r in untitled}
    if any(m is None for m in marks.values()):
        return False
    ordered = sorted(untitled, key=lambda r: marks[id(r)])
    values = [marks[id(r)] for r in ordered]
    if any(b - a < FLOOR_STEP_M for a, b in zip(values, values[1:])):
        return False
    ground = next((i for i, v in enumerate(values) if GROUND_BAND_M[0] <= v <= GROUND_BAND_M[1]), None)
    if ground is None:
        return False
    for i, r in enumerate(ordered):
        order = i - ground
        label = ASSUMED_GROUND[0] if order == 0 else f"Level {order}"
        r.level = {"order": order, "label": label, "id": B.level_id(order), "kind": _kind("floor", order),
                   "method": "assumed", "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title: level {B.level_id(order)} '{label}' inferred "
                        f"from its floor mark {values[i]:+.2f} m ({len(ordered)} untitled plans ordered by their "
                        f"floor marks)")
    return True


def assign_levels(plans: list, needs_review: list, warnings: list) -> None:
    words = {}
    for r in plans:
        lw = level_of(r.title["text"]) if r.title else None
        words[id(r)] = lw
    orders = [lw.order for lw in words.values() if lw is not None and lw.order is not None]
    top = max(max(orders) + 1, 1) if orders else 0
    untitled = [r for r in plans if words[id(r)] is None]
    for r in plans:
        lw = words[id(r)]
        if lw is None:
            continue
        order = top if lw.order is None else lw.order
        ev = [dict(r.evidence[0])] if r.evidence else []
        r.level = {"order": order, "label": lw.label, "id": B.level_id(order), "kind": _kind(lw.kind, order),
                   "method": "title", "evidence": ev}
    if not untitled:
        return
    titled = sorted({r.level["order"] for r in plans if r.level})
    if not titled and len(untitled) == 1:
        r = untitled[0]
        r.level = {"order": 0, "label": ASSUMED_GROUND[0], "id": "L0", "kind": "floor", "method": "assumed",
                   "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title, the project's only plan: level L0 "
                        f"'{ASSUMED_GROUND[0]}' assumed")
        return
    if not titled and len(untitled) >= 2 and _by_floor_marks(untitled, warnings):
        return
    free = [o for o in range(titled[0], titled[-1] + 1) if o not in titled] if titled else []
    if len(untitled) == 1 and len(free) == 1:
        r = untitled[0]
        order = free[0]
        r.level = {"order": order, "label": f"Level {order}", "id": B.level_id(order), "kind": _kind("floor", order),
                   "method": "assumed", "evidence": [dict(e) for e in r.evidence[:1]]}
        warnings.append(f"{r.file} {r.id}: plan without a level title in the only free level slot: level "
                        f"{B.level_id(order)} assumed")
        return
    for r in untitled:
        r.use, r.ignored_reason = "ignored", "plan without a level title (its level cannot be told)"
        needs_review.append({"region": r.id, "file": r.file,
                             "reason": f"{r.file} {r.id}: plan without a level title; {len(untitled)} untitled plans, "
                                       f"{len(free)} free level slot(s)"})


def _kind(kind: str, order: int) -> str:
    if kind == "attic":
        return "attic"
    return "basement" if order < 0 else "floor"
