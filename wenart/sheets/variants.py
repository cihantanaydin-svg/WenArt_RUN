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

Two drawings of one level in one document that differ in size (real04: ground floor r5 17.17 x 12.00 m, bulging out,
and r16 15.17 x 12.00 m, the size of the basement r11) are not the same plan drawn twice: the one whose outline matches
the levels above and below (``SAME_SIZE_M``) is the base, and a drawing of another size is not used
(``ignored``, an ``outline_mismatch`` conflict; user decision of 23 Oct 2026). Nothing changes when no drawing matches
an adjacent level, or when the drawings come from different documents (a DXF and its PDF).
"""
from __future__ import annotations

import re
from typing import Callable

from wenart import building as B
from wenart.sheets import titles as T

LETTERS = "bcdefghijklmnopqrstuvwxyz"
SAME_SIZE_M = 0.30          # two drawings of a level within this (each side) are the same plan


def _rank(r) -> tuple:
    """Trust order of a plan region: CAD before PDF, then document, then reading order."""
    page = r.sheet.generic_page
    cad = 0 if page is not None and page.source_kind == "dxf" else 1
    return (cad, r.file, int(re.sub(r"\D", "", r.id) or 0))


def _ev(r) -> list[dict]:
    return [dict(e) for e in r.evidence[:1]]


def footprint(r):
    """(x, y) size in metres of the plan's outline (dimension lines and the roof outline left out; the entities'
    box when no outline is found); None without a drawing unit."""
    mpu = getattr(r, "metres_per_unit", None)
    if not mpu or getattr(r, "kind", "drawing") == "raster":
        return None
    if not hasattr(r, "_footprint"):
        from wenart.sheets import register as RG
        poly = RG.outline(r, mpu, set(RG.enclosing_outlines(r, mpu)) | RG.cut_line_entities(r)) if r.ents else None
        b = poly.bounds if poly is not None else r.geometry_box
        r._footprint = ((b[2] - b[0]) * mpu, (b[3] - b[1]) * mpu)
    return r._footprint


def _size_gap(a, b) -> float:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def _size_text(size) -> str:
    return f"{size[0]:.2f} x {size[1]:.2f} m"


def _matching(order: int, plain: list, plain_of: dict, conflict: Callable, warnings: list) -> list:
    """``plain`` (the level's plans without an alternative word, in trust order) with the drawing that matches the
    adjacent levels first and the base document's drawings of another size left out (see the module text)."""
    base = plain[0]
    same_doc = [r for r in plain if r.file == base.file]
    sizes = {id(r): footprint(r) for r in same_doc}
    if len(same_doc) < 2 or any(v is None for v in sizes.values()) or \
            max(_size_gap(sizes[id(a)], sizes[id(b)]) for a in same_doc for b in same_doc) <= SAME_SIZE_M:
        return plain
    others = sorted((o for o in plain_of if o != order), key=lambda o: (abs(o - order), o))
    near = [o for o in others if abs(o - order) == abs(others[0] - order)] if others else []
    refs = [(r, footprint(r)) for o in near for r in plain_of[o] if r.use == "read"]
    refs = [(r, size) for r, size in refs if size is not None]
    if not refs:
        return plain

    def score(r):
        return min((_size_gap(sizes[id(r)], size), ref.id) for ref, size in refs)

    chosen = min(same_doc, key=lambda r: score(r)[0])
    gap, ref_id = score(chosen)
    if gap > SAME_SIZE_M:
        warnings.append(f"level {base.level['id']}: {len(same_doc)} drawings of different sizes in {base.file} "
                        f"({', '.join(f'{r.id} {_size_text(sizes[id(r)])}' for r in same_doc)}); none matches an "
                        f"adjacent level: {base.id} (first in trust order) is the base")
        return plain
    dropped = [r for r in same_doc if _size_gap(sizes[id(r)], sizes[id(chosen)]) > SAME_SIZE_M]
    ref = next(r for r, _ in refs if r.id == ref_id)
    text = (f"level {base.level['id']}: {len(same_doc)} drawings in {base.file}; {chosen.id} "
            f"({_size_text(sizes[id(chosen)])}) matches {ref_id} of level {ref.level['id']} "
            f"({_size_text(footprint(ref))}) and is read; "
            f"{', '.join(f'{r.id} ({_size_text(sizes[id(r)])})' for r in dropped)} not used")
    cid = conflict("outline_mismatch", [chosen.id] + [r.id for r in dropped], text,
                   f"{chosen.id} read (its outline matches the adjacent level); "
                   f"{', '.join(r.id for r in dropped)} ignored")
    warnings.append(text)
    for r in dropped:
        r.use = "ignored"
        r.ignored_reason = (f"another drawing of level {base.level['id']} whose outline "
                            f"({_size_text(sizes[id(r)])}) does not match the adjacent levels; {chosen.id} "
                            f"({_size_text(sizes[id(chosen)])}, as {ref_id}) is read")
        r.conflicts.append(cid)
    chosen.conflicts.append(cid)
    return [chosen] + [r for r in plain if r is not chosen and r not in dropped]


def group(plans: list, brief_variants, conflict: Callable, warnings: list) -> tuple[list[dict], list[dict]]:
    by_order: dict[int, list] = {}
    for r in plans:
        if r.level is not None and r.use == "read":
            by_order.setdefault(r.level["order"], []).append(r)
    levels = []
    alternatives = []                     # (base level dict, alternative entry, region)
    split = {}
    for order in sorted(by_order):
        regions = sorted(by_order[order], key=_rank)
        floors = [r for r in regions if r.cls != "furniture_plan"]
        furniture = [r for r in regions if r.cls == "furniture_plan"]
        if not floors:
            floors, furniture = furniture[:1], furniture[1:]
        named = {id(r): T.alternative_of(r.title["text"]) if r.title else None for r in floors}
        split[order] = (floors, furniture, named, [r for r in floors if named[id(r)] is None])
    plain_of = {order: v[3] for order, v in split.items() if v[3]}
    for order in sorted(by_order):
        floors, furniture, named, plain = split[order]
        if len(plain) > 1:
            plain = _matching(order, plain, plain_of, conflict, warnings)
            floors = [r for r in floors if r.use == "read"]
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
