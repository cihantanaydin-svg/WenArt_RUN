"""How well a library model suits an open-air room (pure, no dependencies: the fit ranks with it and the build's
architect reads it; 25 Oct 2026, user on real04's roof terrace: "is that table on the terrace ok? is it suitable for
the terrace?": an indoor turned-leg table with a drawer and indoor dining chairs stood there).

``outdoor_grade(entry)``: 0 named or built for outside (outdoor, garden, patio, bistro, teak, rattan, wicker,
aluminium) or of metal / rattan only, 1 wood, glass or stone without upholstery, 2 upholstered (fabric) or named for
inside (desk, drawer, office, velvet, leather ...). A piece in an open-air room (``OPEN_AIR_ROOMS``) ranks the models
by it (``fit.rank_key``: ``OUTDOOR_STEPS`` size steps per grade).

Outdoor rooms are dressed for outside (28 Oct 2026, user on real04 run 20261028-005318-full, the roof terrace
r_L1_teras: "makes no sense to have that table with the carpet outside, that's outside area"). What the run did: the
balcony group's table got the "Ravenna Home Traditional Dining Table ... Rustic Honey Pine" (grade 1: a wood model
without upholstery counted as "hard materials", and the ranking was only a preference: the 20 better-ranked models
failed the caps), its two chairs the "Gubi Beetle Dining Chair" (grade 0 only because the vision tags said "metal"),
and the AI decorator laid a beige wool runner rug under the table (``decor.rugs_for_room`` offered a dining rug for
every dining table, whatever the room). Rules for every project:

- ``open_air_room(room)``: a room of an open-air type (``OPEN_AIR_ROOMS``) or one marked open to the sky
  (``open_air`` / ``open_to_sky`` / ``outdoor`` true) is outside; the site's outdoor spaces are too
  (``outdoor_space`` on a piece or a decor item).
- ``outdoor_ready(entry, ftype)``: a model is made for outside only when its own words say so: a place word
  (``PLACE_WORDS``: outdoor, garden, patio, bistro, balcony, poolside ...) or an outdoor material (``MATERIAL_WORDS``:
  teak, rattan, wicker, resin, polywood ...; for a hard piece only without a fabric or leather part), and never when
  they name an inside use or finish (``INDOOR_WORDS``: indoor, desk, drawer, office, velvet, linen, upholstered,
  turned, traditional ...). The vision's material tags alone never make an outdoor model (an indoor chair on metal legs
  is tagged metal). Words are matched whole (a "Grattan" table is no rattan one). The fit takes only such models for
  the outdoor types (``OUTDOOR_FURNITURE_TYPES``) of an open-air room (``fit._fit_family``, rule ``fit.outdoor_room``);
  when none fits, the parametric family builds the piece in weather-proof materials (``OUTDOOR_BUILD``: a brushed
  steel frame with a teak top, seat and slats; ``outdoor_asset``), recorded as a library gap.
- ``floor_textile(item)``: a rug, runner, carpet or mat is an indoor textile: never on the floor of an open-air room
  or an outdoor space (``decor.rugs_for_room``, ``solver._rug_dicts``, ``outdoor_sets`` lay none;
  ``strip_outdoor_textiles`` takes out any a later rule adds, with the reason).
- ``review(building)``: the check (model review M16, Argus's sense line): every floor textile outside and every
  library model of an outdoor type in an open-air room that is not ``outdoor_ready``.
"""
from __future__ import annotations

import html
import re
from typing import Optional

OPEN_AIR_ROOMS = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")
OPEN_AIR_FLAGS = ("open_air", "open_to_sky", "outdoor")
OUTDOOR_WORDS = ("outdoor", "outdoors", "garden", "patio", "terrace", "bistro", "teak", "rattan", "wicker",
                 "aluminium", "aluminum", "deck", "lounger", "sunbed", "adirondack", "poolside", "resin", "café",
                 "cafe")
INDOOR_WORDS = ("indoor", "desk", "drawer", "office", "velvet", "leather", "upholstered", "upholstery", "dresser",
                "vanity", "nightstand", "turned", "tufted", "chesterfield", "dining room", "living room", "bedroom",
                "wheel", "castor", "caster", "swivel", "办公", "damask", "hallway", "linen", "bouclé", "boucle",
                "chenille", "management", "gaming", "traditional", "farmhouse", "nursery")
OUTDOOR_STEPS = 3
# 28 Oct 2026: the words that make a model an outdoor one (``outdoor_ready``)
PLACE_WORDS = ("outdoor", "outdoors", "outside", "garden", "patio", "terrace", "balcony", "bistro", "deck", "decking",
               "poolside", "beach", "adirondack", "lounger", "sunbed", "sun lounger", "deckchair",
               "deck chair", "parasol", "café", "cafe", "exterior", "all-weather", "all weather", "weatherproof",
               "weather-proof", "weather resistant", "weather-resistant", "garten", "bahçe", "bahce", "jardin",
               "giardino", "tuin")
MATERIAL_WORDS = ("teak", "rattan", "wicker", "polyrattan", "poly rattan", "poly-rattan", "resin", "hdpe", "polywood",
                  "powder-coated", "powder coated", "galvanised", "galvanized", "cast aluminium", "cast aluminum")
SOFT_TAGS = ("fabric", "leather")
# the furniture types that have an outdoor version; a piece of one of them in an open-air room takes an outdoor model
OUTDOOR_FURNITURE_TYPES = ("table_dining", "table_coffee", "side_table", "chair", "armchair", "sofa", "sofa_corner",
                           "bench", "chaise", "ottoman", "bar_stool")
UPHOLSTERED_TYPES = ("armchair", "sofa", "sofa_corner", "chaise", "ottoman")
# the parametric family in weather-proof materials (the builders read the design's tags and wood:
# parametric.chair_design, _table_m10): a steel frame with teak; an upholstered type a teak frame with cushions
OUTDOOR_WOOD = "wood_veneer_teak"
_TABLE = {"material_tags": ["metal"], "wood": OUTDOOR_WOOD, "what": "a teak top on brushed steel legs"}
_SEAT = {"material_tags": ["metal", "wood"], "wood": OUTDOOR_WOOD, "what": "a brushed steel frame with a teak seat"}
OUTDOOR_BUILD: dict[str, dict] = {"table_dining": _TABLE, "table_coffee": _TABLE, "side_table": _TABLE,
                                  "chair": _SEAT, "bar_stool": _SEAT, "bench": _SEAT}
OUTDOOR_BUILD_SOFT = {"material_tags": ["wood", "fabric"], "wood": OUTDOOR_WOOD,
                      "what": "a teak frame with outdoor cushions"}
OUTDOOR_RULE = "fit.outdoor_room"
# 28 Oct 2026: indoor textiles on a floor (decor types and the words of a model's title)
FLOOR_TEXTILE_TYPES = ("rug", "runner", "carpet", "mat", "bath_mat", "doormat")
TEXTILE_RULE = "decor.no_floor_textile_outside"
TEXTILE_REASON = ("an outdoor room: no rug, runner or carpet on its floor (an indoor textile outside; 28 Oct 2026, "
                  "user: \"makes no sense to have that table with the carpet outside, that's outside area\")")
REVIEW_CHECK = "M16"


def _text(entry: dict) -> str:
    return html.unescape(" ".join(str(entry.get(k) or "") for k in ("name", "title", "style_note", "style_hint"))
                         ).lower()


def named(text: str, words) -> list[str]:
    """The ``words`` (or phrases) ``text`` names as whole words, a plural ``s`` / ``es`` allowed (pure; a word of
    another script than Latin is matched as it stands)."""
    out = []
    for w in words:
        if any(ord(c) > 0x2E7F for c in w):
            if w in text:
                out.append(w)
        elif re.search(rf"(?<![^\W_]){re.escape(w)}(?:s|es)?(?![^\W_])", text):
            out.append(w)
    return out


def outdoor_grade(entry: dict) -> int:
    """How well a model suits an open-air room (pure): 0 made for outside, 1 hard materials, 2 made for inside.
    28 Oct 2026: words are matched whole (``named``)."""
    words = _text(entry)
    tags = set(entry.get("material_tags") or [])
    if named(words, OUTDOOR_WORDS):
        return 0
    if "fabric" in tags or named(words, INDOOR_WORDS):
        return 2
    if tags and tags <= {"metal", "rattan", "glass"} and tags & {"metal", "rattan"}:
        return 0
    return 1


def outdoor_ready(entry: dict, ftype: Optional[str] = None) -> tuple[bool, str]:
    """``(ready, why)``: whether a library model is made for outside (module docstring; pure). An inside word wins;
    then a place word; then an outdoor material, for a hard piece only when it has no fabric or leather part (an
    upholstered type may carry its outdoor cushions: a teak loveseat with cushions)."""
    text = _text(entry)
    tags = set(entry.get("material_tags") or [])
    inside = named(text, INDOOR_WORDS)
    if inside:
        return False, f"its name says inside ({', '.join(dict.fromkeys(inside))})"
    place = named(text, PLACE_WORDS)
    if place:
        return True, f"named for outside ({', '.join(dict.fromkeys(place))})"
    material = named(text, MATERIAL_WORDS)
    soft = sorted(tags & set(SOFT_TAGS))
    if material and (not soft or (ftype or entry.get("type")) in UPHOLSTERED_TYPES):
        return True, f"of an outdoor material ({', '.join(dict.fromkeys(material))})"
    if material:
        return False, (f"names {', '.join(dict.fromkeys(material))} but has a {', '.join(soft)} part (an indoor "
                       f"upholstered piece)")
    return False, "nothing in its name says outside (no outdoor place or material word; material tags alone do not)"


def open_air_room(room: Optional[dict]) -> bool:
    """A room that is outside (pure): its type is an open-air one (``OPEN_AIR_ROOMS``) or it is marked open to the
    sky (``OPEN_AIR_FLAGS`` true)."""
    if not isinstance(room, dict):
        return False
    return str(room.get("room_type") or "").lower() in OPEN_AIR_ROOMS or any(room.get(k) is True
                                                                           for k in OPEN_AIR_FLAGS)


def open_air_room_ids(building: dict) -> set:
    return {r.get("id") for r in building.get("rooms") or [] if open_air_room(r)}


def outside(item: dict, open_ids: set) -> bool:
    """A piece or decor item stands outside: in an open-air room (``open_ids``) or on an outdoor space of the site."""
    return bool(item.get("outdoor_space")) or item.get("open_air") is True or item.get("room_id") in open_ids


def floor_textile(item: dict) -> bool:
    """A rug, runner, carpet or mat lying on the floor (pure): its decor type, or a decor model named for one."""
    if str(item.get("type") or "").lower() in FLOOR_TEXTILE_TYPES:
        return True
    asset = item.get("asset") if isinstance(item.get("asset"), dict) else {}
    if str(asset.get("decor_type") or asset.get("target") or "").lower() in FLOOR_TEXTILE_TYPES:
        return True
    return False


def strip_outdoor_textiles(building: dict) -> list[dict]:
    """In place: the floor textiles (``floor_textile``) on an open-air room's floor or an outdoor space taken out of
    ``building["decor"]``; returns them, each with ``removed_reason`` and the rule."""
    open_ids = open_air_room_ids(building)
    kept, gone = [], []
    for d in building.get("decor") or []:
        if isinstance(d, dict) and floor_textile(d) and outside(d, open_ids):
            gone.append(dict(d, removed_reason=TEXTILE_REASON, rule=TEXTILE_RULE))
        else:
            kept.append(d)
    if gone:
        building["decor"] = kept
    return gone


def outdoor_build(ftype: str) -> Optional[dict]:
    """The weather-proof design of the parametric family for an outdoor ``ftype`` (``OUTDOOR_BUILD``), None for a
    type without an outdoor version."""
    if ftype in OUTDOOR_BUILD:
        return dict(OUTDOOR_BUILD[ftype])
    if ftype in UPHOLSTERED_TYPES:
        return dict(OUTDOOR_BUILD_SOFT)
    return None


def outdoor_asset(asset: dict, ftype: str, entry: Optional[dict] = None, style: Optional[str] = None) -> dict:
    """In place (and returned): the record of a piece of an outdoor type fitted in an open-air room (pure).
    ``asset["outdoor"] = {"rule", "ready", "reason"}``; a module or parametric piece gets ``outdoor_build`` (the
    weather-proof design the builders read, ``looks.design_for``) and, when the fit named none, a ``library_gap``
    (no library model made for outside fits)."""
    if ftype not in OUTDOOR_FURNITURE_TYPES:
        return asset
    method = asset.get("method")
    if method == "library":
        ready, why = outdoor_ready(entry or asset, ftype)
        asset["outdoor"] = {"rule": OUTDOOR_RULE, "ready": ready, "reason": why}
        return asset
    if method in ("module", "parametric"):
        build = outdoor_build(ftype)
        if build is None:
            return asset
        what = build.pop("what")
        asset["outdoor_build"] = dict(build, why=f"open-air room: {what} (weather-proof)")
        used = f"{method} family in weather-proof materials ({what})"
        asset["outdoor"] = {"rule": OUTDOOR_RULE, "ready": True,
                            "reason": f"no {ftype.replace('_', ' ')} library model made for outside fits: the {used}"}
        if not asset.get("library_gap"):
            asset["library_gap"] = {"type": ftype, "style": style, "step": method, "used": used,
                                    "reason": f"no {ftype} library model made for outside fits the drawn size "
                                              f"(rule {OUTDOOR_RULE})"}
        else:
            asset["library_gap"] = dict(asset["library_gap"], used=used, outdoor_rule=OUTDOOR_RULE)
    return asset


def _finding(severity: str, target, message: str, room_id=None, **metrics) -> dict:
    return {"check": REVIEW_CHECK, "severity": severity, "target": target, "room_id": room_id, "message": message,
            "metrics": dict(metrics, model_review=True)}


def review(building: dict) -> tuple[list[dict], int]:
    """M16 (pure): ``(findings, checked)`` over every decor item and piece outside (``outside``): a floor textile
    there (major), a library model of an outdoor type in an open-air room that is not ``outdoor_ready`` (major), each
    finding with the element, the room and the reason."""
    open_ids = open_air_room_ids(building)
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    out, n = [], 0
    for d in building.get("decor") or []:
        if not isinstance(d, dict) or not outside(d, open_ids):
            continue
        n += 1
        if floor_textile(d):
            where = d.get("room_id") or d.get("outdoor_space")
            title = ((d.get("asset") or {}).get("title") or "") if isinstance(d.get("asset"), dict) else ""
            out.append(_finding("major", d.get("id"), f"{d.get('id')} ({d.get('type')}{': ' + title if title else ''}) "
                                f"lies on the floor of {where}, an outdoor area: no rug, runner or carpet outside",
                                d.get("room_id"), rule=TEXTILE_RULE, outdoor_space=d.get("outdoor_space"),
                                kind_of_item="floor_textile"))
    for f in building.get("furniture") or []:
        if not isinstance(f, dict) or f.get("build") is False or not outside(f, open_ids):
            continue
        t = str(f.get("type") or "")
        if t not in OUTDOOR_FURNITURE_TYPES:
            continue
        n += 1
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        if asset.get("method") != "library":
            continue
        rec = asset.get("outdoor") if isinstance(asset.get("outdoor"), dict) else None
        ready, why = (bool(rec.get("ready")), str(rec.get("reason") or "")) if rec and "ready" in rec \
            else outdoor_ready(asset, t)
        if ready:
            continue
        room = rooms.get(f.get("room_id")) or {}
        where = f.get("room_id") or f.get("outdoor_space")
        out.append(_finding("major", f.get("id"), f"{f.get('id')} ({t}) in {where} "
                            f"({room.get('room_type') or 'outdoor space'}) is the indoor model {asset.get('asset_id')} "
                            f"({asset.get('title') or asset.get('name') or '?'}): {why}; an outdoor room takes "
                            f"outdoor furniture", f.get("room_id"), rule=OUTDOOR_RULE, asset_id=asset.get("asset_id"),
                            kind_of_item="indoor_model"))
    return out, n
