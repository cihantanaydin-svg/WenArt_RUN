"""Levels of the plan regions (docs/milestone10.md §3.1 item 3).

What: ``assign_levels(plans, needs_review, warnings)`` gives every plan region (``use: read``) its level from its
title: order, label, kind (``basement``, ``floor``, ``attic``) and how it was decided (``title`` or ``assumed``).

Why: the pipeline stacks the levels by order and the heights map the section's slab bands to them bottom-up.

How: ``titles.level_of`` reads the level word (``BODRUM`` = -1, ``ZEMİN`` = 0, ``1. KAT`` = 1, ...). An attic
(``ÇATI KAT``, ``ATTIC``, ``DACHGESCHOSS``, ``COMBLES``) is the top level: one above the highest other titled level
(at least 1). An untitled plan gets a level only when it is the project's only plan (``L0`` "Ground floor", as M7)
or when exactly one level between the titled ones is free (``assumed``, listed); otherwise it needs review.
"""
from __future__ import annotations

from wenart import building as B
from wenart.sheets import titles as T

ASSUMED_GROUND = ("Ground floor", 0)


def assign_levels(plans: list, needs_review: list, warnings: list) -> None:
    words = {}
    for r in plans:
        lw = T.level_of(r.title["text"]) if r.title else None
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
