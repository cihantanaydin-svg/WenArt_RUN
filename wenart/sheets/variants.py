"""Alternative plans of one level and the buildable variants (docs/milestone10.md §3.1 item 4, §1.1).

What: ``group(plans, brief_variants, conflicts, warnings) -> (levels, variants)`` sorts the plan regions of each
level into the base plan, its alternatives and its furniture plans, gives the alternatives their level ids
(``L-1b``, ``L-1c`` ...), names, slugs and glosses, and lists one buildable variant per alternative.

Why: an alternative (real02's open-kitchen basement) is never merged into the base: it is its own level, built and
rendered as its own variant (user decision 2: ``variants: all``).

How: within one level, a plan whose title has an alternative word (``ALTERNATİF``, ``SEÇENEK``, ``OPSİYON``,
``VARYANT``, ``ALTERNATIVE``, ``OPTION``, ``VARIANT``, ``VARIANTE``) or an extra bracket (``( Açık mutfak)``) is an
alternative named by it; the plans without one are the base (the same plan in several documents is one base read
from several documents, as in M2-M9). Two plans without an alternative word on one sheet: the first in reading order
is the base, the other an alternative ``Alternative <n>``, ``base_unclear`` with a ``variant_base_unclear``
conflict. Variant ids are ``base`` and ``<alternative level id lower case>-<slug>`` (``l-1b-acik-mutfak``). The
brief's ``variants`` (``all``, ``base`` or a list of alternative names) selects which alternatives are built; the
others are ignored and listed.
"""
from __future__ import annotations

import re
from typing import Callable

from wenart.sheets import titles as T

LETTERS = "bcdefghijklmnopqrstuvwxyz"


def group(plans: list, brief_variants, conflict: Callable, warnings: list) -> tuple[list[dict], list[dict]]:
    by_order: dict[int, list] = {}
    for r in plans:
        if r.level is not None and r.use == "read":
            by_order.setdefault(r.level["order"], []).append(r)
    levels = []
    alternatives = []                     # (base level dict, alternative entry, region)
    for order in sorted(by_order):
        regions = by_order[order]
        floors = [r for r in regions if r.cls != "furniture_plan"]
        furniture = [r for r in regions if r.cls == "furniture_plan"]
        if not floors:
            floors, furniture = furniture[:1], furniture[1:]
        named, plain = [], []
        for r in floors:
            alt = T.alternative_of(r.title["text"]) if r.title else None
            (named if alt else plain).append((r, alt))
        unclear = False
        base_regions = [r for r, _ in plain]
        if not base_regions:
            unclear = True
            base_regions = [named[0][0]]
            named = named[1:]
        extra = _same_sheet_duplicates(base_regions)
        if extra:
            unclear = True
            base_regions = [r for r in base_regions if r not in extra]
            named = named + [(r, (f"Alternative {k}", "unclear")) for k, r in enumerate(extra, start=2)]
        base = base_regions[0]
        level_id = base.level["id"]
        entry = {"id": level_id, "order": order, "label": base.level["label"], "kind": base.level["kind"],
                 "base_region": base.id, "file": base.file, "alternatives": [],
                 "furniture_regions": [r.id for r in furniture], "evidence": list(base.level.get("evidence") or [])}
        if len(base_regions) > 1:
            entry["also_drawn_in"] = [{"file": r.file, "region": r.id} for r in base_regions[1:]]
        for r in base_regions + furniture:
            r.variant = "base"
        group_id = f"vg_{level_id}" if named else None
        for k, (r, (name, how)) in enumerate(named):
            alt_id = f"{level_id}{LETTERS[k]}"
            slug = T.slug(name)
            r.level = dict(r.level, id=alt_id)
            r.variant, r.variant_slug, r.variant_gloss = name, slug, T.gloss(name)
            if r.cls == "floor_plan":
                r.cls = "alternative_floor_plan"
            alt = {"region": r.id, "variant": name, "slug": slug, "level_id": alt_id, "base_unclear": unclear}
            entry["alternatives"].append(alt)
            alternatives.append((entry, alt, r))
        if group_id:
            for r in base_regions + [r for r, _ in named] + furniture:
                r.variant_group = group_id
            for r in base_regions + furniture:
                r.variant_slug = "base"
        if unclear:
            ids = [base.id] + [r.id for r, _ in named]
            cid = conflict("variant_base_unclear", ids,
                           f"level {level_id}: {len(ids)} plans and no single plan without an alternative word or "
                           f"bracket; {base.id} (first in reading order) taken as the base",
                           "unverified: the report asks which plan is the base")
            for r in [base] + [r for r, _ in named]:
                r.status = "unverified"
                r.conflicts.append(cid)
        levels.append(entry)

    variants = [{"id": "base", "label": "Base", "base": True, "levels": [lv["id"] for lv in levels],
                 "regions": [lv["base_region"] for lv in levels]}]
    selected = _selected(brief_variants, alternatives, warnings)
    for entry, alt, r in alternatives:
        if alt["variant"] not in selected:
            r.use, r.ignored_reason = "ignored", f"alternative '{alt['variant']}' not selected (brief variants: " \
                                                 f"{brief_variants})"
            continue
        lv_ids = [alt["level_id"] if lv is entry else lv["id"] for lv in levels]
        regions = [alt["region"] if lv is entry else lv["base_region"] for lv in levels]
        label = f"{entry['label']}: {alt['variant']}" + (f" ({r.variant_gloss})" if r.variant_gloss else "")
        variants.append({"id": f"{alt['level_id'].lower()}-{alt['slug']}", "label": label, "base": False,
                         "levels": lv_ids, "regions": regions})
    return levels, variants


def _same_sheet_duplicates(regions: list) -> list:
    """Plans of one level without an alternative word drawn on the same sheet as an earlier one: the later ones."""
    seen = set()
    extra = []
    for r in sorted(regions, key=lambda r: (r.file, r.sheet.id, int(re.sub(r"\D", "", r.id) or 0))):
        key = (r.file, r.sheet.id)
        if key in seen:
            extra.append(r)
        seen.add(key)
    return extra


def _selected(brief_variants, alternatives: list, warnings: list) -> set:
    names = {alt["variant"] for _, alt, _ in alternatives}
    if brief_variants in (None, "all"):
        return names
    if brief_variants == "base":
        if names:
            warnings.append(f"brief variants: base: alternatives not built: {', '.join(sorted(names))}")
        return set()
    wanted = {T.fold(v) for v in brief_variants}
    chosen = {n for n in names if T.fold(n) in wanted}
    missing = wanted - {T.fold(n) for n in names}
    if missing:
        warnings.append(f"brief variants: {', '.join(sorted(missing))} not found among the titled alternatives "
                        f"({', '.join(sorted(names)) or 'none'})")
    return chosen
