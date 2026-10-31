"""The library first for a host's small items (31 Oct 2026; user on real04 run 20261030-181158-full, a bathroom's open
shelf column: "This little items needs a lot better models, check the library of similar things exist to use if not
create them with better texture and more detailed way"; the rule of lesson UL215, "Library models if exist and better
than procedural generation should be used", carried from the decor items to the small items inside a host).

What (pure): a host that carries small items (a bathroom's open niche column, a vanity's top, shelf and cubbies, a
towel shelf, an installation wall's niches: ``wenart.blender.bath_parts``) leaves a reserved box per item
(``bath_objects.placed`` with ``bath_objects.ALL``: every item a library slot; ``parametric.library_slots``). For each
kind of item among them (``bath_objects.SMALL_ITEM_KINDS``) ``plan`` picks the best library model that

- is of that kind: a decor model of the kind's own decor types (``ITEMS[kind]["types"]``: a basket, a candle, a small
  plant), or a decor or extras model of the kind's ``titled`` types whose title names the item (``words``: a soap
  dispenser, a perfume flacon, an apothecary jar, a reed diffuser, a soap dish);
- is audited and usable in the licence mode (``catalog.usable``: never a rejected model or one the user ranked 0-2), a
  real product, of the style family (``fit.decor_styles_match``), with no part off it (``open_parts``: a basket's lid
  leaning beside it does not read as the item on a shelf);
- is rated good: the user's rank of it from ``user_ranks.GOOD_FROM`` (6) up, else (unranked) the audit's vision quality
  at least ``MIN_QUALITY`` (4), as the decor items' library first (``fit.LIBRARY_FIRST_MIN_QUALITY``);
- fits every reserved box of that kind (``slot_fit``): one uniform scale puts it inside the box (turned a quarter when
  that fills it better), it fills at least ``MIN_FILL`` of the box's width, depth and height (its proportions are the
  item's) and its scaled size is a real product's of that kind (``ITEMS[kind]["range"]``).

The best: the highest user rank, then vision quality, no logo, the fullest fit, the id (deterministic). Else the kind
keeps our procedural model and the record holds a ``library_gap`` for it (none of that kind, none rated good, none
fits) that the fit report lists. The record (``small_items`` on the host's asset, or on a decor item; on a vanity's
module plan too) is ``{"rule", "picks": {kind: asset}, "gaps": {kind: {"why", ...}}, "slots": {kind: n}}``; the build
fills a picked kind's slots with the model (``furniture.place_slot_models``), and the credits and licence flags read
the picks (``assets_of``).
"""
from __future__ import annotations

import re
from typing import Iterable, Optional

from wenart.blender import bath_objects as BO
from wenart.furniture import catalog as C

RULE = "small_items_library_first (31 Oct 2026)"
MIN_QUALITY = 4
MIN_FILL = 0.6
REFUSED_LISTED = 12               # a gap note names this many refused models with their reasons, then a count
TITLED_TYPES = ("decor_vase", "decor_bowl", "decor_tray", "bathroom_set", "untyped_object")
# per kind: the decor types of the kind itself (``decor_type`` without its ``decor_`` prefix), the types whose models
# count only when their title names the item, those words, and a real product's (width, depth, height) in metres
ITEMS: dict[str, dict] = {
    "pump_bottle": {"types": (), "titled": TITLED_TYPES,
                    "words": ("soap dispenser", "lotion dispenser", "pump bottle", "soap pump", "lotion pump"),
                    "range": ((0.04, 0.12), (0.04, 0.13), (0.10, 0.28))},
    "perfume_bottle": {"types": (), "titled": TITLED_TYPES,
                       "words": ("perfume", "fragrance", "flacon", "cologne", "parfum", "eau de"),
                       "range": ((0.025, 0.12), (0.015, 0.10), (0.05, 0.20))},
    "apothecary_jar": {"types": (), "titled": TITLED_TYPES,
                       "words": ("apothecary", "storage jar", "glass jar", "canister", "bath jar", "cotton jar",
                                 "lidded jar"),
                       "range": ((0.05, 0.16), (0.05, 0.16), (0.06, 0.26))},
    "reed_diffuser": {"types": (), "titled": TITLED_TYPES, "words": ("diffuser",),
                      "range": ((0.04, 0.26), (0.04, 0.26), (0.12, 0.42))},
    "potted_plant": {"types": ("plant_small",), "titled": ("decor_plant",),
                     "words": ("plant", "succulent", "fern", "pothos", "flower pot", "planter"),
                     "range": ((0.07, 0.32), (0.07, 0.32), (0.08, 0.42))},
    "candle_glass": {"types": ("candle",), "titled": (), "words": (),
                     "range": ((0.04, 0.14), (0.04, 0.14), (0.04, 0.16))},
    "soap_dish": {"types": (), "titled": TITLED_TYPES, "words": ("soap dish", "soap holder", "soap tray", "soap saver"),
                  "range": ((0.07, 0.17), (0.05, 0.14), (0.012, 0.06))},
    "woven_basket": {"types": ("basket",), "titled": (), "words": (),
                     "range": ((0.15, 0.46), (0.12, 0.40), (0.06, 0.30))},
}


def _title(entry: dict) -> str:
    return str(entry.get("title") or entry.get("name") or "").casefold()


def names_item(entry: dict, kind: str) -> Optional[str]:
    """The word of ``ITEMS[kind]["words"]`` the model's title names (as a word), None when it names none."""
    title = _title(entry)
    for w in ITEMS[kind]["words"]:
        if re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", title):
            return w
    return None


def candidates(kind: str, catalog, mode: str) -> list[dict]:
    """The library models of ``kind`` usable in licence ``mode`` (the module docstring's first two points, before the
    rating and the fit), by id."""
    from wenart.furniture import fit as F

    spec = ITEMS[kind]
    found: dict[str, dict] = {}
    for dtype in spec["types"]:
        for e in F.decor_entries(catalog, dtype, mode):
            found.setdefault(str(e["id"]), e)
    titled = set(spec["titled"])
    if titled:
        pool = list(getattr(catalog, "decor", None) or []) + list(getattr(catalog, "extras", None) or [])
        for e in pool:
            if (isinstance(e, dict) and e.get("type") in titled and e.get("id") and e.get("glb") and e.get("bbox_m")
                    and names_item(e, kind) and C.usable(e, mode)):
                found.setdefault(str(e["id"]), e)
    return [found[k] for k in sorted(found)]


def rating(entry: dict) -> tuple[bool, str]:
    """``(good, why)``: the user's rank (from ``user_ranks.GOOD_FROM`` up) when ranked, else the audit's vision quality
    (at least ``MIN_QUALITY``)."""
    from wenart.furniture import fit as F
    from wenart.furniture import user_ranks as UR

    rank = UR.rank_of(entry)
    if rank is not None:
        return rank >= UR.GOOD_FROM, f"the user's rank {rank} (good from {UR.GOOD_FROM})"
    q = F.vision_quality_of(entry)
    if q is None:
        return False, "no vision quality and no user rank"
    return q >= MIN_QUALITY, f"vision quality {q:g} (good from {MIN_QUALITY})"


def slot_fit(entry: dict, kind: str, box) -> Optional[dict]:
    """The uniform fit of a model into one reserved ``box`` (w, d, h): ``{"scale", "turned_deg", "bbox_m", "fill"}``
    with the scale that puts it inside the box (turned 90 degrees when that fills it better), or None when it fills
    less than ``MIN_FILL`` of the box on an axis or its scaled size is no real product of ``kind``."""
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    sw, sd, sh = (float(v) for v in box[:3])
    if min(bw, bd, bh, sw, sd, sh) <= 0:
        return None
    (w0, w1), (d0, d1), (h0, h1) = ITEMS[kind]["range"]
    lo, hi = min(w0, d0), max(w1, d1)                    # a plan size either way round
    best = None
    for turned, (mw, md) in ((0.0, (bw, bd)), (90.0, (bd, bw))):
        s = min(sw / mw, sd / md, sh / bh)
        w, d, h = mw * s, md * s, bh * s
        fill = min(w / sw, d / sd, h / sh)
        if fill < MIN_FILL - 1e-9:
            continue
        if not (lo - 1e-6 <= min(w, d) and max(w, d) <= hi + 1e-6 and h0 - 1e-6 <= h <= h1 + 1e-6):
            continue
        cand = {"scale": round(s, 5), "turned_deg": turned, "bbox_m": [round(w, 4), round(d, 4), round(h, 4)],
                "fill": round(fill, 4)}
        if best is None or cand["fill"] > best["fill"] + 1e-9:
            best = cand
    return best


def pick(kind: str, boxes: list, catalog, style_family: Optional[str], mode: str) -> tuple[Optional[dict], dict]:
    """``(asset, note)``: the library model for the ``kind``'s reserved ``boxes`` (module docstring) and how it was
    chosen, or None and the ``library_gap`` note."""
    from wenart.furniture import fit as F
    from wenart.furniture import user_ranks as UR

    pool = candidates(kind, catalog, mode)
    note = {"type": kind, "candidates": len(pool), "rule": RULE}
    name = kind.replace("_", " ")
    if not pool:
        note["why"] = f"no audited library model of {'an' if name[0] in 'aeiou' else 'a'} {name} usable in {mode} mode"
        return None, note
    refused: dict[str, str] = {}
    fits = []
    for e in pool:
        good, why = rating(e)
        if not good:
            refused[str(e["id"])] = why
            continue
        if e.get("real_product") is False:
            refused[str(e["id"])] = "not a real product (audit)"
            continue
        if not F.decor_styles_match(e, style_family):
            refused[str(e["id"])] = f"not of the {style_family} style family"
            continue
        if e.get("open_parts"):
            refused[str(e["id"])] = "a part off it (open_parts: a lid beside it, a prop): not the item on a shelf"
            continue
        per = [slot_fit(e, kind, b) for b in boxes]
        if not per or any(f is None for f in per):
            refused[str(e["id"])] = "does not fit the reserved box(es) in the real size of the item"
            continue
        fits.append((e, per))
    note["refused"] = dict(sorted(refused.items())[:REFUSED_LISTED])     # the building JSON stays small
    if len(refused) > REFUSED_LISTED:
        note["refused_more"] = len(refused) - REFUSED_LISTED
    if not fits:
        rated = sum(1 for e in pool if rating(e)[0])
        note["why"] = (f"none of {len(pool)} {kind.replace('_', ' ')} model(s) is rated good (the user's rank "
                       f">= {UR.GOOD_FROM}, else vision quality >= {MIN_QUALITY}): our model is better" if not rated
                       else f"none of the {rated} good {kind.replace('_', ' ')} model(s) suits the item (style, parts, "
                            f"size or the reserved box)")
        return None, note

    def rank(pair):
        e, per = pair
        user = UR.rank_of(e)
        return (-(user if user is not None else UR.UNRANKED), -(F.vision_quality_of(e) or 0), bool(C.logo_flagged(e)),
                -round(min(f["fill"] for f in per), 4), str(e["id"]))

    entry, per = sorted(fits, key=rank)[0]
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    asset = {"library": entry.get("source") or "3dwh", "asset_id": entry["id"], "licence": entry.get("licence"),
             "license": entry.get("licence"), "method": "library", "small_item": kind,
             "bbox_m": [round(bw, 4), round(bd, 4), round(bh, 4)], "target": "within",
             "front_axis": entry.get("front_axis", "-Y"), "up_axis": entry.get("up_axis", "+Z"),
             "origin_offset": list(entry.get("origin_offset") or [0.0, 0.0, 0.0]),
             "unit_scale": float(entry.get("unit_scale") or 1.0), "styles": list(entry.get("styles") or []),
             "style_family": style_family, "quality": F.vision_quality_of(entry), "user_rank": UR.rank_of(entry),
             "slot_fits": per,
             "pick": {"rule": RULE, "ids": [e["id"] for e, _p in sorted(fits, key=rank)], "of_kind": len(pool)}}
    asset.update({k: entry[k] for k in F.GLB_ASSET_FIELDS if k in entry})
    asset["licence_flag"] = C.licence_flag_of(entry)
    asset["commercial_safe"] = C.commercial_safe(asset)
    asset["licence_mode"] = mode
    note.pop("why", None)
    return asset, note


def plan(slots: Iterable[dict], catalog, style_family: Optional[str], mode: str) -> Optional[dict]:
    """The ``small_items`` record of a host (module docstring) from its reserved boxes (``parametric.library_slots``
    of its parts built with ``bath_objects.ALL``); None when the host has no small item."""
    by_kind: dict[str, list] = {}
    for s in slots:
        if s.get("kind") in ITEMS:
            by_kind.setdefault(s["kind"], []).append(s["box"])
    if not by_kind:
        return None
    mode = C.check_mode(mode)
    record = {"rule": RULE, "picks": {}, "gaps": {}, "slots": {k: len(v) for k, v in sorted(by_kind.items())}}
    for kind in sorted(by_kind):
        asset, note = pick(kind, by_kind[kind], catalog, style_family, mode)
        if asset is not None:
            record["picks"][kind] = asset
        else:
            record["gaps"][kind] = note
    return record


def host_slots(kind: str, w: float, d: float, h: float, look: Optional[dict] = None,
               item: Optional[dict] = None) -> list[dict]:
    """The reserved boxes of a host's small items in its frame: ``kind`` ``column`` (the open niche column), ``vanity``
    (``look``: its bath look, ``h`` its top), ``towel_shelf`` or ``install_wall`` (``item``: the decor item)."""
    from wenart.blender import bath_parts as BT
    from wenart.blender import parametric as P

    item = dict(item or {}, small_items=BO.ALL)
    if kind == "column":
        parts = BT.open_column_parts(w, d, h, BO.ALL)
    elif kind == "vanity":
        parts = BT.vanity_parts(w, d, h, look or {}, BO.ALL)
    elif kind in ("towel_shelf", "install_wall"):
        parts = BT.decor_parts(kind, w, d, h, item)
    else:
        return []
    return P.library_slots(parts)


def records(building: dict) -> list[dict]:
    """The ``small_items`` records of a building: its pieces' assets' and its decor items', each with ``host`` (the
    piece's or the item's id)."""
    out = []
    for p in (building or {}).get("furniture") or []:
        rec = (p.get("asset") or {}).get("small_items") if isinstance(p, dict) and isinstance(p.get("asset"), dict) \
            else None
        if isinstance(rec, dict):
            out.append(dict(rec, host=str(p.get("id"))))
    for d in (building or {}).get("decor") or []:
        if isinstance(d, dict) and isinstance(d.get("small_items"), dict):
            out.append(dict(d["small_items"], host=str(d.get("id"))))
    return out


def assets_of(record) -> list[dict]:
    """The library assets a ``small_items`` record picked (for the credits and the licence flags), by kind."""
    if not isinstance(record, dict) or not isinstance(record.get("picks"), dict):
        return []
    return [record["picks"][k] for k in sorted(record["picks"]) if isinstance(record["picks"][k], dict)]


def gaps_of(record) -> list[dict]:
    """The ``library_gap`` notes of a ``small_items`` record, by kind."""
    if not isinstance(record, dict) or not isinstance(record.get("gaps"), dict):
        return []
    return [dict(record["gaps"][k], type=k) for k in sorted(record["gaps"])]
