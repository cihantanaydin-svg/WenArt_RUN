"""Alternative plans of one level, copies of a level, and the buildable variants (docs/milestone10.md §3.1 item 4,
§1.1, §1.6b rows 4, 7, 8).

What: ``group(plans, brief_variants, conflict, warnings) -> (levels, variants)`` sorts the plan regions of each
level into the base plan (``base_region``), its copies (``secondary_regions``), its alternatives and its furniture
plans; gives the alternatives their level ids (``L-1b``, ``L-1c`` ...), names, slugs and glosses; and lists one
buildable variant per selected alternative.

Why: an alternative (real02's open-kitchen basement) is never merged into the base: it is its own level, built and
rendered as its own variant (user decision 2: ``variants: all``). A level drawn twice (a DXF and its PDF, as
synthetic-04) is one level read from two documents (the M7 cross-check), never an alternative.

How: the base of a level is its plan without an alternative word (``ALTERNATİF``, ``SEÇENEK``, ``OPSİYON``,
``VARYANT``, ``ALTERNATIVE``, ``OPTION``, ``VARIANT``, ``VARIANTE``) or extra bracket (``( Açık mutfak)``), the first
in trust order (DWG/DXF before PDF, then document and reading order). Every other plan without such a word is a copy
(``secondary_regions``). A plan with such a word in the base's document is an alternative named by it; in another
document it is read as a copy (listed). A level whose plans all carry such words takes the first in reading order as
the base (``base_unclear``, a ``variant_base_unclear`` conflict). Variant ids and slugs come from
``wenart.building.variant_id`` / ``variant_slug``. The brief's ``variants``: ``all``; ``base`` (the alternatives are
read but not listed as variants); or a list of names (kept when the name, slug, gloss or variant id matches after
``fold_ascii``; unknown names are a warning).
"""
from __future__ import annotations

import re
from typing import Callable

from wenart import building as B
from wenart.sheets import titles as T

LETTERS = "bcdefghijklmnopqrstuvwxyz"


def _rank(r) -> tuple:
    """Trust order of a plan region: CAD before PDF, then document, then reading order."""
    page = r.sheet.generic_page
    cad = 0 if page is not None and page.source_kind == "dxf" else 1
    return (cad, r.file, int(re.sub(r"\D", "", r.id) or 0))


def _ev(r) -> list[dict]:
    return [dict(e) for e in r.evidence[:1]]


def group(plans: list, brief_variants, conflict: Callable, warnings: list) -> tuple[list[dict], list[dict]]:
    by_order: dict[int, list] = {}
    for r in plans:
        if r.level is not None and r.use == "read":
            by_order.setdefault(r.level["order"], []).append(r)
    levels = []
    alternatives = []                     # (base level dict, alternative entry, region)
    for order in sorted(by_order):
        regions = sorted(by_order[order], key=_rank)
        floors = [r for r in regions if r.cls != "furniture_plan"]
        furniture = [r for r in regions if r.cls == "furniture_plan"]
        if not floors:
            floors, furniture = furniture[:1], furniture[1:]
        named = {id(r): T.alternative_of(r.title["text"]) if r.title else None for r in floors}
        plain = [r for r in floors if named[id(r)] is None]
        unclear = not plain
        base = plain[0] if plain else floors[0]
        copies = [r for r in plain if r is not base]
        alts = []
        for r in floors:
            if r is base or r in copies:
                continue
            if r.file != base.file:
                copies.append(r)
                warnings.append(f"{r.file} {r.id}: titled as an alternative of {base.level['id']} but drawn in "
                                f"another document than its base ({base.file} {base.id}): read as a copy of the level")
                continue
            alts.append((r, named[id(r)] or (f"Alternative {len(alts) + 2}", "unclear")))
        level_id = base.level["id"]
        entry = {"id": level_id, "order": order, "label": base.level["label"], "kind": base.level["kind"],
                 "base_region": base.id, "secondary_regions": [r.id for r in copies], "alternatives": [],
                 "furniture_regions": [r.id for r in furniture], "evidence": list(base.level.get("evidence") or [])}
        for r in [base] + copies + furniture:
            r.variant = "base"
            r.variant_slug = "base"
        group_id = f"vg_{level_id}" if alts else None
        for k, (r, (name, how)) in enumerate(alts):
            alt_id = f"{level_id}{LETTERS[k]}"
            slug = B.variant_slug(name)
            r.level = dict(r.level, id=alt_id)
            r.variant, r.variant_slug, r.variant_gloss = name, slug, T.gloss(name)
            if r.cls == "floor_plan":
                r.cls = "alternative_floor_plan"
            alt = {"region": r.id, "variant": name, "slug": slug, "level_id": alt_id, "base_unclear": unclear}
            entry["alternatives"].append(alt)
            alternatives.append((entry, alt, r))
        if group_id:
            for r in [base] + copies + furniture + [r for r, _ in alts]:
                r.variant_group = group_id
        if unclear and alts:
            ids = [base.id] + [r.id for r, _ in alts]
            cid = conflict("variant_base_unclear", ids,
                           f"level {level_id}: {len(ids)} plans, each titled as an alternative; {base.id} (first in "
                           f"reading order) taken as the base",
                           "unverified: the report asks which plan is the base")
            for r in [base] + [r for r, _ in alts]:
                r.status = "unverified"
                r.conflicts.append(cid)
        levels.append(entry)

    variants = [{"id": "base", "label": "Base", "base": True, "levels": [lv["id"] for lv in levels],
                 "regions": [lv["base_region"] for lv in levels]}]
    selected = _selected(brief_variants, alternatives, warnings)
    for entry, alt, r in alternatives:
        vid = B.variant_id(alt["level_id"], alt["slug"])
        if vid not in selected:
            r.notes.append(f"alternative '{alt['variant']}' read but not built as a variant (brief variants: "
                           f"{brief_variants})")
            continue
        lv_ids = [alt["level_id"] if lv is entry else lv["id"] for lv in levels]
        regions = [alt["region"] if lv is entry else lv["base_region"] for lv in levels]
        label = f"{entry['label']}: {alt['variant']}" + (f" ({r.variant_gloss})" if r.variant_gloss else "")
        variants.append({"id": vid, "label": label, "base": False, "levels": lv_ids, "regions": regions,
                         "evidence": _ev(r)})
    return levels, variants


def _selected(brief_variants, alternatives: list, warnings: list) -> set:
    """Variant ids the brief keeps."""
    ids = {B.variant_id(alt["level_id"], alt["slug"]): (alt, r) for _, alt, r in alternatives}
    if brief_variants in (None, "all"):
        return set(ids)
    if brief_variants == "base":
        if ids:
            warnings.append(f"brief variants: base: alternatives read, not built: {', '.join(sorted(ids))}")
        return set()

    def key(text) -> str:
        return " ".join(B.fold_ascii(str(text)).lower().strip(" ()").split())

    wanted = {key(v) for v in brief_variants}
    chosen, matched = set(), set()
    for vid, (alt, r) in ids.items():
        names = {key(alt["variant"]), key(alt["slug"]), key(r.variant_gloss or ""), key(vid)} - {""}
        hit = names & wanted
        if hit:
            chosen.add(vid)
            matched |= hit
    missing = wanted - matched
    if missing:
        warnings.append(f"brief variants: {', '.join(sorted(missing))} not found among the alternatives "
                        f"({', '.join(sorted(a['variant'] for _, a, _ in alternatives)) or 'none'})")
    return chosen
