"""A room's program: its functional groups (docs/milestone12.md §4.3, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026):

- ``room_program(building: dict, room_id: str, brief: dict | None = None, choices: dict | None = None) -> dict``:
  ``{"room_id", "zones": [{"zone_id", "kind", "polygon"}], "groups": [{"group_id", "group", "anchor_id": str | None,
  "required": bool, "options": [str], "chosen": str | None, "drawn": bool}], "reason"}``. ``group`` is a key of
  ``groups.yaml``; a group whose anchor is drawn has ``drawn: true`` and is only completed. ``choices``
  (``{group_id: option}``) are the VLM's picks among ``options``; unknown keys are ignored. Pure.

What: a rule table turns the room type, area, shape, doors, windows, the brief and the drawn pieces into the groups
the solver places (each with its options), in priority order. Extra keys of each group: ``zone_id`` (the zone it
stands in, None = the whole room), ``area`` (the room or zone area the size variants use), ``priority``, ``members``
(drawn pieces already in the group) and ``missing`` (what the drawn group lacks).

Why: Milestone 11 asked a text-only model for single pieces with coordinates (§1.2); now the program says what
belongs in the room and the solver says where.

How:

1. Drawn pieces first (``groups.group_members``): a drawn sofa is the seating anchor, a drawn bed the sleeping anchor,
   a drawn table the dining anchor, drawn sanitary ware the bathroom set, a drawn counter the kitchen run. Such a
   group is ``drawn: true`` and only completed (its missing partners; never a second anchor, CLAUDE.md). A drawn
   anchor that is ``unverified`` or not built makes its group ``drawn`` with nothing to complete.
2. Then the groups the room type calls for and the documents leave out (rows below; a zone of an open plan,
   ``rooms[].zones`` of track R, gets the rows of its kind: a kitchen zone of a living room its kitchen run):

| Room (zone) | Groups (options) |
|---|---|
| living | seating (sofa + 2 / 1 / 0 armchairs, corner sofa from 12 m²) required; dining (4 / 6 seats) from 18 m² when the level has no dining room; living storage (sideboard / bookshelf) from 16 m² |
| bedroom | double sleeping (+ bench from 14 m²) from 9 m², else (and in a child's room) single sleeping; storage (wardrobe) from 7 m²; work (desk) in a child's room or from 14 m² |
| kitchen | kitchen run (I, L, galley, U by the room's shape); dining (4 seats) from 10 m²; island from 16 m² |
| dining | dining (4 / 6 / 8 seats by area) required; living storage from 12 m² |
| bathroom | bathroom set (shower / bathtub when a wall takes 1.7 m and the room has 4 m²; washer option) |
| wc | wc set |
| hall | entrance (shoe cabinet / console) from 2.5 m² when the hall is 1.10 m wide |
| other | work from 6 m² |
| balcony | balcony (table + 2 chairs) from 2.5 m² |

   Stair rooms, shafts, prayer rooms and rooms the brief switches off get no group (``reason`` says why).
3. ``choices`` pick one option of a group (a VLM pick or the agent's ``relayout_room``); a group whose drawn anchor
   fixes the option (a drawn corner sofa) has that option only.

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §13.2; track T3; user decisions D5 of 12 Oct 2026):

4. **Room kinds** (``room_kind``): a room the ingest left ``other`` or ``unknown`` is read by the words of its label
   (``groups.yaml`` ``room_aliases``: "Oyun Aktivite Ve Dinlenme Odası" is a living room, a plain "Oda" of 7 m² a
   bedroom) and, failing that, by its drawn anchors (two drawn sofas make a living room). The rule table, the group
   templates' ``room_types``, the checks (G14 / F1) and the solver's allowed types all read the kind, so the drawn
   sofas of real04's play room get a seating group instead of a wrong-type finding. A hall whose drawn stair covers
   more than ``room_aliases.stair_cover`` of the floor is a landing and gets no program (real04's r_L0_merdiven).
5. **Room-size variants** (R14, ``groups.yaml`` ``small_rooms``): a living room under 12 m² gets the ``sofa`` option
   only; a bedroom under 10 m² lets one long side of the bed stand on the wall (the solver and G5 read it).
6. **Drawn groups as one unit** (D5): the drawn groups (``groups.drawn_groups``, built or not) whose anchor is
   missing (not built: a library gap), misread (its size outside the product grid, ``sizes.snap_size``) or fails the
   placer checks as drawn (outside the room, on a door strip, overlapping a drawn piece outside its group) are marked
   ``resolve`` = ``{"reason", "anchor_id", "members", "centre", "template"}``: the solver re-solves the whole group
   around the drawn anchor's centre (every member within ``groups.GROUP_MEMBER_MOVE_MAX_M``), logs the moved pieces
   ``adjusted_by_ai`` and still adds the missing partners. Such an anchor no longer suppresses its group (the old
   "never a second anchor" rule kept the room without a bed). Off with ``furnished_rooms: keep``,
   ``furnished_rooms_keep_size`` or a room in ``furnished_rooms_keep`` (``resolve_allowed``; the ``brief`` argument or
   the building's ``project.brief`` carry the keys).

Fix round after P4a (17 Oct 2026; pod P4a, real02). What: a drawn anchor is "unsure" (``unsure_anchor``: its group
gets nothing added, it is not re-solved, the solver never uses it as drawn) only when it is ``unverified`` because
the reading could not agree on it, or when it is a type proposal of the completion (``type_proposal``, as before); a
vector-drawn anchor the reading typed by code (``infer.CODE_TYPE_METHODS``: the twin room, another level, the block
name, the room's missing anchor) is completed like a verified one. Why: the reading types such anchors by code and
withdraws their VLM question, and code typing keeps ``status: unverified``; real02's four
beds f_L0_019-022 (typed "the bedroom misses its bed" and by their twins) got "unverified anchor: nothing added", so
r_L0_yatak_odasi, _2, _3 and _4 lost their nightstands (and the bed group's rug); in Milestone 11 both VLMs had
agreed ``bed_double`` and the beds were verified. The U10 rule (no chairs around an unverified table,
``groups._expected_missing``) is unchanged.

Fix round after P4b (17 Oct 2026; the review of the P4a fix round). What: a drawn anchor that is a duplicate outline
(``duplicate_anchor``: a larger built drawn piece of its family holds it, ``edit_ops.family_host_of``) gets nothing
added (note "duplicate outline: drawn inside ...") and is never re-solved. Why: real02's 1.30 m "sofa" f_L-1_061 is
the seat segment of the corner sofa f_L-1_053's block, typed by the group-member rule; since the P4a fix it counted
as a sure anchor, so its seating group was marked for a re-solve (a TV unit and a coffee table around a phantom); the
solver found no place and the phantom stayed. It is listed for review and the agent may mark it (the edit lock lets
a duplicate outline through).
"""
from __future__ import annotations

import math
from typing import Optional

import re

from shapely.geometry import Polygon

from wenart.furniture import groups as GR
from wenart.furniture import placer, schemas

NOT_FURNISHED = ("prayer", "stair", "shaft", "storage", "unknown")
ROOM_ZONE_KIND = {"living": "living", "bedroom": "sleeping", "kitchen": "kitchen", "dining": "dining",
                  "bathroom": "bath", "wc": "bath", "hall": "hall", "other": "work", "balcony": "balcony"}
ZONE_ROOM_TYPE = {"living": "living", "sleeping": "bedroom", "kitchen": "kitchen", "dining": "dining",
                  "work": "other", "bath": "bathroom", "hall": "hall", "balcony": "balcony"}
MIN_HALL_WIDTH_M = 1.10            # a hall narrower than this takes no piece (0.30 deep piece + 0.80 walkway)
# Milestone 13: the room types the templates know; ``other`` and ``unknown`` are read through the aliases.
TEMPLATE_KINDS = ("living", "bedroom", "kitchen", "dining", "bathroom", "wc", "hall", "other", "balcony")
ALIAS_KINDS = ("other", "unknown", None, "")
RESOLVE_OVERLAP_M2 = 0.05          # a drawn anchor overlapping a drawn piece outside its group by this fails the checks
RESOLVE_OUTSIDE_M2 = 0.02          # ... or reaching this far through the room outline
# Storage runs are built at any drawn length (modules, T2): only their depth can be misread, never their length (a
# wardrobe drawn from wall to wall is a built-in run, not a misread 3.2 m product).
RUN_LIKE_TYPES = ("wardrobe", "bookshelf", "sideboard", "display_cabinet", "tall_cabinet", "console_table", "dresser",
                  "shoe_cabinet", "tv_unit", "kitchen_counter")


def unsure_anchor(anchor: Optional[dict]) -> bool:
    """Fix round after P4a (module docstring): True for an ``unverified`` drawn anchor the reading could not agree on
    (its group gets nothing added) and for a type proposal of the completion (``type_proposal``); False for a
    verified one and for a vector-drawn anchor the reading typed by code (``type_method`` in
    ``infer.CODE_TYPE_METHODS``), which is completed like a verified one."""
    if not anchor or anchor.get("status") != "unverified":
        return False
    if anchor.get("type_proposal") is True:
        return True                                 # typed by code in the completion: a proposal, nothing added
    from wenart.furniture import infer as INF      # lazy: infer reads the program (room kinds)

    vector = any(isinstance(e, dict) and e.get("method") == "vector" for e in anchor.get("evidence") or [])
    return not (vector and anchor.get("type_method") in INF.CODE_TYPE_METHODS)


def duplicate_anchor(building: dict, anchor: Optional[dict]) -> Optional[str]:
    """Fix round after P4b (module docstring): the id of the larger drawn piece of the anchor's family whose footprint
    holds the drawn anchor (``edit_ops.family_host_of``: a seat segment of a corner sofa's block read as a sofa), else
    None. Such an anchor gets nothing added and is not re-solved."""
    if not anchor or anchor.get("source") != "from_documents":
        return None
    from wenart.furniture import edit_ops as E     # lazy: edit_ops reads the program

    return E.family_host_of(building, anchor)


def _room(building: dict, room_id: str) -> dict:
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    return room


# --------------------------------------------------------------------------
# Milestone 13: room kinds (aliases), settings
# --------------------------------------------------------------------------

def _label_words(room: dict) -> list[str]:
    from wenart import building as B

    text = " ".join(str(room.get(k) or "") for k in ("label", "label_raw"))
    return [w for w in re.split(r"[^a-z0-9]+", B.fold_ascii(text).lower()) if w]


def _alias_hit(words: list[str], alias_words: list[str]) -> Optional[str]:
    """The first alias word in a label's words, or None: a Turkish keyword matches at the start of a word (``yatak``
    in ``yatak odasi``), an English or a two-word keyword as whole words in order."""
    text = " " + " ".join(words) + " "
    for key in alias_words:
        parts = key.split()
        if len(parts) > 1:
            if f" {' '.join(parts)} " in text:
                return key
        elif any(w.startswith(key) for w in words):
            return key
    return None


def _alias_hits(words: list[str], alias_words: list[str]) -> bool:
    return _alias_hit(words, alias_words) is not None


def room_kind(building: dict, room: dict) -> str:
    """The room type the templates use for a room: its ``room_type`` when the templates know it (not ``other`` /
    ``unknown``); else the kind its label words name (``groups.yaml`` ``room_aliases``, with ``min_area``); else the
    kind its drawn anchors name (``room_aliases.content``: drawn sofas make a living room); else its ``room_type``
    (``other`` for a room nobody can read)."""
    rtype = room.get("room_type") or "unknown"
    if rtype in TEMPLATE_KINDS and rtype not in ALIAS_KINDS:
        return rtype
    aliases = GR.room_aliases()
    words = _label_words(room)
    area = _area(room)
    hits: list[tuple[str, str]] = []
    for kind in TEMPLATE_KINDS:
        spec = aliases.get(kind)
        key = _alias_hit(words, list(spec.get("words") or [])) if spec else None
        if key is None:
            continue
        if spec.get("min_area") is not None and area < float(spec["min_area"]) - 1e-9:
            continue
        hits.append((kind, key))
    # Review fix (15 Oct 2026): a generic word (``room_aliases.generic``: "oda", any room) yields to a specific word
    # of another kind: a "Çalışma Odası" is a study (other), a "Çamaşır Odası" a utility room, not a bedroom.
    generic = {str(w) for w in aliases.get("generic") or []}
    specific = [kind for kind, key in hits if key not in generic]
    # Integration (15 Oct 2026): a room whose type the ingest read (storage, corridor, ...; a type without a
    # template) keeps it against a generic word alone: a "Depo"/"Oda" storage room is no bedroom (the ingest's room
    # type is source data, CLAUDE.md trust order); a specific word of another kind still wins as above.
    if rtype not in ALIAS_KINDS and not specific:
        hits = []
    if hits:
        return (specific or [hits[0][0]])[0]
    content = aliases.get("content") or {}
    drawn = [f for f in building.get("furniture") or [] if f.get("room_id") == room.get("id")
             and f.get("source") == "from_documents" and f.get("build") is not False and not f.get("inferred_as")]
    kinds: dict[str, int] = {}
    for f in drawn:
        kind = content.get(f.get("type") or "")
        if kind:
            kinds[kind] = kinds.get(kind, 0) + 1
    if kinds:
        # Seating and sleeping anchors say more than a table or a desk (a dining table stands in a living room too).
        order = {"living": 0, "bedroom": 0, "bathroom": 1, "kitchen": 1, "dining": 2, "other": 3}
        return sorted(kinds, key=lambda k: (order.get(k, 9), -kinds[k], k))[0]
    return rtype if rtype in TEMPLATE_KINDS else "other"


def room_kinds(building: dict, room: dict) -> list[str]:
    """``room_kind`` first, then the room's own type when it differs (an aliased ``other`` room keeps the work
    group of ``other`` too)."""
    kind = room_kind(building, room)
    rtype = room.get("room_type") or "unknown"
    out = [kind]
    if rtype in TEMPLATE_KINDS and rtype != kind:
        out.append(rtype)
    return out


def settings_of(building: dict, brief: Optional[dict] = None) -> dict:
    """``{"mode": keep | complete, "keep": [room ids or labels], "keep_size": bool}`` from ``brief`` (a dict with the
    brief keys, e.g. ``complete.Settings.brief_values()``) or the building's ``project.brief``; the code defaults of
    ``wenart/defaults.yaml`` otherwise."""
    src = brief if brief is not None else ((building.get("project") or {}).get("brief") or {})
    mode = str(src.get("furnished_rooms") or "complete")
    keep = [str(v) for v in (src.get("furnished_rooms_keep") or [])]
    return {"mode": mode, "keep": keep, "keep_size": bool(src.get("furnished_rooms_keep_size", False))}


def resolve_allowed(building: dict, room: dict, brief: Optional[dict] = None) -> tuple[bool, str]:
    """Whether a drawn group of ``room`` may be re-solved as one unit (D5): off with ``furnished_rooms: keep``,
    ``furnished_rooms_keep_size`` or a room named in ``furnished_rooms_keep`` (by id or label)."""
    s = settings_of(building, brief)
    if s["mode"] == "keep":
        return False, "furnished_rooms: keep"
    if s["keep_size"]:
        return False, "furnished_rooms_keep_size"
    names = {room.get("id"), room.get("label"), room.get("label_raw")}
    from wenart import building as B

    folded = {B.fold_ascii(str(n)).lower() for n in names if n}
    for k in s["keep"]:
        if k in names or B.fold_ascii(k).lower() in folded:
            return False, f"furnished_rooms_keep: {k}"
    return True, ""


def _area(room: dict) -> float:
    if room.get("area_computed"):
        return float(room["area_computed"])
    return Polygon(room["polygon"]).area if len(room.get("polygon") or []) >= 3 else 0.0


def min_width(polygon: Polygon) -> float:
    """The room's smaller side of its minimum rotated rectangle (a corridor's width)."""
    rect = polygon.minimum_rotated_rectangle
    pts = list(rect.exterior.coords)
    sides = sorted(math.dist(pts[i], pts[i + 1]) for i in range(4))
    return sides[0] if sides else 0.0


def longest_wall(polygon: Polygon) -> float:
    pts = list(polygon.exterior.coords)
    return max((math.dist(a, b) for a, b in zip(pts, pts[1:])), default=0.0)


def _level_has_dining(building: dict, room: dict) -> bool:
    return any(r.get("room_type") == "dining" and r.get("level_id") == room.get("level_id")
               for r in building.get("rooms") or [])


def _entry(room_id: str, group: str, required: bool, options: list[str], *, zone_id=None, area=0.0,
           anchor_id=None, drawn=False, members=(), missing=(), note: str = "") -> dict:
    t = GR.load_groups()[group]
    return {"group_id": f"{room_id}.{group}" if zone_id is None else f"{zone_id}.{group}", "group": group,
            "anchor_id": anchor_id, "required": required, "options": list(options), "chosen": None, "drawn": drawn,
            "zone_id": zone_id, "area": round(float(area), 2), "priority": int(t["priority"]) + (100 if drawn else 0),
            "members": list(members), "missing": list(missing), "note": note}


def _rows(kind: str, area: float, polygon: Polygon, building: dict, room: dict, subtype: Optional[str]) -> list[tuple]:
    """``(group, required, options)`` rows of the rule table for a room or zone of ``kind`` (a room type)."""
    rows: list[tuple] = []
    if kind == "living":
        seat = ["sofa_2_armchairs", "sofa_armchair", "sofa"] if area >= 14.0 else ["sofa", "sofa_armchair"]
        if area >= 12.0:
            seat.append("corner_sofa")
        small = GR.small_room("living", area)
        if small and small.get("options"):
            seat = [o for o in small["options"] if o in GR.load_groups()["seating"]["options"]] or seat
        rows.append(("seating", True, seat))
        if area >= 18.0 and not _level_has_dining(building, room):
            rows.append(("dining", False, ["seats_4", "seats_6"] if area >= 24.0 else ["seats_4"]))
        if area >= 16.0:
            rows.append(("living_storage", False, ["sideboard", "bookshelf"]))
    elif kind == "bedroom":
        child = subtype == "child"
        if area >= 9.0 and not child:
            rows.append(("sleeping_double", True, ["bed_nightstands", "bed_nightstands_bench"] if area >= 14.0
                         else ["bed_nightstands"]))
        else:
            rows.append(("sleeping_single", True, ["bed_nightstand"]))
        if area >= 7.0:
            rows.append(("storage", area >= 9.0, ["wardrobe"]))
        if child or area >= 14.0:
            rows.append(("work", False, ["desk"]))
    elif kind == "kitchen":
        shapes = ["I", "L"]
        if min_width(polygon) >= 2.1:
            shapes.append("galley")
        if area >= 9.0:
            shapes.append("U")
        rows.append(("kitchen_run", True, shapes))
        if area >= 10.0:
            rows.append(("dining", False, ["seats_4"]))
        if area >= 16.0:
            rows.append(("island", False, ["island"]))
    elif kind == "dining":
        opts = ["seats_4"] + (["seats_6"] if area >= 12.0 else []) + (["seats_8"] if area >= 18.0 else [])
        rows.append(("dining", True, opts))
        if area >= 12.0:
            rows.append(("living_storage", False, ["sideboard", "bookshelf"]))
    elif kind == "bathroom":
        opts = ["shower"]
        if longest_wall(polygon) >= 1.75 and area >= 4.0:
            opts.append("bathtub")
        if area >= 4.5:
            opts.append("shower_washer")
        rows.append(("bathroom_set", True, opts))
    elif kind == "wc":
        rows.append(("wc_set", True, ["wc"]))
    elif kind == "hall":
        if area >= 2.5 and min_width(polygon) >= MIN_HALL_WIDTH_M and stair_cover(building, room) <= float(
                GR.room_aliases().get("stair_cover", 1.0)) + 1e-9:
            rows.append(("entrance", False, ["shoe_cabinet", "console"]))
    elif kind == "other":
        if area >= 6.0:
            rows.append(("work", False, ["desk"]))
    elif kind == "balcony":
        if area >= 2.5:
            rows.append(("balcony", False, ["table_2_chairs"]))
    return rows


def stair_cover(building: dict, room: dict) -> float:
    """The share of the room's floor its drawn stairs cover (0 without a stair): a landing the stair fills gets no
    program (real04's r_L0_merdiven: 398 anchor positions, all blocked)."""
    if len(room.get("polygon") or []) < 3:
        return 0.0
    poly = Polygon(room["polygon"]).buffer(0)
    if poly.area <= 1e-9:
        return 0.0
    covered = 0.0
    for f in building.get("furniture") or []:
        if f.get("room_id") != room.get("id") or f.get("type") != "stair" or not f.get("footprint"):
            continue
        try:
            covered += placer.drawn_piece(f).polygon().intersection(poly).area
        except (KeyError, TypeError, ValueError):
            continue
    return round(covered / poly.area, 4)


def _resolve_reason(building: dict, room: dict, g: dict, polys: dict) -> Optional[str]:
    """Why a drawn group is re-solved as one unit (None: it stays as drawn): its anchor is missing (not built),
    misread (its size outside the product grid) or fails the checks as drawn."""
    from wenart.furniture import sizes

    by_id = {f["id"]: f for f in building.get("furniture") or []}
    anchor = by_id.get(g["anchor_id"])
    if anchor is None:
        return None
    if not GR.piece_is_built(anchor):
        asset = anchor.get("asset") if isinstance(anchor.get("asset"), dict) else {}
        why = anchor.get("not_built_reason") or asset.get("fallback_reason") or asset.get("library_gap") \
            or ("asset.method none" if asset.get("method") == "none" else "build false")
        return f"the drawn {anchor['type']} {anchor['id']} is not built ({why})"
    try:
        piece = placer.drawn_piece(anchor)
    except (KeyError, TypeError, ValueError):
        return None
    snap = sizes.snap_size(anchor["type"], piece.size)
    misread = bool(snap.get("changed"))
    if misread and anchor["type"] in RUN_LIKE_TYPES:
        misread = abs(float(snap["footprint"][1]) - float(piece.size[1])) > 0.01     # the depth only
    if misread:
        return (f"the drawn {anchor['type']} {anchor['id']} is misread: {piece.size[0]:.2f} x {piece.size[1]:.2f} m "
                f"is outside the product grid ({snap.get('reason')})")
    poly = polys.get(anchor["id"])
    if poly is None:
        return None
    ctx = placer.room_context(building, room)
    outside = poly.difference(ctx.polygon.buffer(0.01, join_style="mitre")).area
    if outside > RESOLVE_OUTSIDE_M2:
        return f"the drawn {anchor['type']} {anchor['id']} reaches {outside:.2f} m² through the room outline"
    if placer._opening_blocked(piece, ctx):
        return f"the drawn {anchor['type']} {anchor['id']} stands on a door strip, a door swing or a window band"
    members = set(g.get("members") or [])
    for pid, other in polys.items():
        if pid == anchor["id"] or pid in members:
            continue
        area = poly.intersection(other).area
        if area > RESOLVE_OVERLAP_M2:
            return (f"the drawn {anchor['type']} {anchor['id']} overlaps {by_id[pid]['type']} {pid} by {area:.2f} m² "
                    f"(outside its group)")
    return None


def _option_of_anchor(group: str, anchor_type: str, options: list[str]) -> list[str]:
    """The options a drawn anchor allows (a drawn corner sofa: the corner-sofa option)."""
    t = GR.load_groups()[group]
    keep = [o for o in options if t["options"][o].get("anchor") in (None, anchor_type)]
    return keep or options


def _may_be(ftype: str, size) -> bool:
    """An unknown footprint fits the product sizes of ``ftype`` (either way round; types without sizes never)."""
    from wenart.furniture import plausibility as PL     # lazy: plausibility imports the group modules

    if ftype not in PL._size_table():
        return False
    w, d = float(size[0]), float(size[1])
    return PL.oriented_fit(ftype, (w, d))["fits"] or PL.oriented_fit(ftype, (d, w))["fits"]


def room_program(building: dict, room_id: str, brief: Optional[dict] = None, choices: Optional[dict] = None) -> dict:
    room = _room(building, room_id)
    own_type = room.get("room_type") or "unknown"
    out = {"room_id": room_id, "zones": [], "groups": [], "reason": ""}
    zones = [z for z in room.get("zones") or [] if len(z.get("polygon") or []) >= 3]
    out["zones"] = [{"zone_id": z.get("zone_id") or f"{room_id}.z{k}", "kind": z.get("kind"),
                     "polygon": z["polygon"]} for k, z in enumerate(zones)]
    if len(room.get("polygon") or []) < 3:
        out["reason"] = "the room has no polygon"
        return out
    brief = brief if brief is not None else ((building.get("project") or {}).get("brief") or {})
    if own_type in schemas.NOT_FURNISHED_ROOM_TYPES or own_type in ("prayer", "stair", "shaft", "storage"):
        out["reason"] = f"{own_type} room: no furniture groups"
        return out
    # Milestone 13: the kind the templates use (aliases for ``other`` / ``unknown`` rooms).
    rtype = room_kind(building, room)
    out["kind"] = rtype
    if rtype in NOT_FURNISHED or rtype in schemas.NOT_FURNISHED_ROOM_TYPES:
        out["reason"] = f"{rtype} room: no furniture groups"
        return out
    polygon = Polygon(room["polygon"]).buffer(0)
    area = _area(room)
    subtype = room.get("room_subtype")
    # 1. Groups by zone (or the room as one zone).
    places = [(None, rtype, area, polygon)]
    if zones:
        places = []
        for z, zz in zip(zones, out["zones"]):
            kind = ZONE_ROOM_TYPE.get(z.get("kind") or "", None)
            if kind:
                zp = Polygon(z["polygon"]).buffer(0)
                places.append((zz["zone_id"], kind, zp.area, zp))
        if not places:
            places = [(None, rtype, area, polygon)]
    rows: list[dict] = []
    for zone_id, kind, a, poly in places:
        for group, required, options in _rows(kind, a, poly, building, room, subtype):
            rows.append(_entry(room_id, group, required, options, zone_id=zone_id, area=a))
    # 2. Drawn groups: the matched groups of the drawn pieces take the program's place (or join it).
    drawn = {f["id"]: f for f in building.get("furniture") or [] if f.get("room_id") == room_id}
    matched = [g for g in GR.group_members(building, room_id)
               if (drawn.get(g["anchor_id"]) or {}).get("source") == "from_documents"]
    notes = []
    for g in matched:
        anchor = drawn[g["anchor_id"]]
        name = g["group"]
        if name not in GR.load_groups():
            continue
        same = next((r for r in rows if r["group"] == name and not r["drawn"]), None)
        if same is None and name in ("sleeping_double", "sleeping_single"):
            same = next((r for r in rows if r["group"] in ("sleeping_double", "sleeping_single") and not r["drawn"]),
                        None)
        template = GR.load_groups()[name]
        # the row of the other sleeping group (a drawn double bed in a room under 9 m², whose row is sleeping_single)
        # has that group's options: the drawn group takes its own (P8 test: KeyError 'bed_nightstand')
        own = (same or {}).get("options") if (same or {}).get("group") == name else None
        options = own or list(template["options"])
        if template["layout"] == "anchored":
            options = _option_of_anchor(name, anchor["type"], options)
        host = duplicate_anchor(building, anchor) if template["layout"] == "anchored" else None   # after P4b
        unsure = (unsure_anchor(anchor) or host is not None) and template["layout"] == "anchored"   # after P4a
        kinds = set(room_kinds(building, room)) | {ZONE_ROOM_TYPE.get(z.get("kind") or "") for z in zones}
        foreign = not (set(template["room_types"]) & kinds)
        note = (f"duplicate outline: drawn inside the {drawn[host]['type'] if host in drawn else 'piece'} {host}, "
                f"nothing added (listed for review)" if host is not None else
                "unverified anchor: nothing added" if unsure else
                f"no completion: a {name} group does not belong in a {rtype} room" if foreign else "")
        drawn_members = [m for m in g["member_ids"] if (drawn.get(m) or {}).get("source") == "from_documents"]
        entry = _entry(room_id, name, True, options, zone_id=(same or {}).get("zone_id"),
                       area=(same or {}).get("area", area), anchor_id=anchor["id"], drawn=True,
                       members=drawn_members, missing=[] if (unsure or foreign) else g.get("missing", []), note=note)
        if same is not None:
            rows.remove(same)
        if any(r["group_id"] == entry["group_id"] for r in rows):
            entry["group_id"] = f"{entry['group_id']}.{anchor['id']}"
        rows.append(entry)
        notes.append(f"{name} completed around drawn {anchor['type']} {anchor['id']}")
    # Milestone 13 (D5): drawn groups whose anchor is missing, misread or fails the checks are re-solved as one
    # unit around the drawn anchor's centre (the whole group, built or not: groups.drawn_groups), never suppressed.
    allowed, why_not = resolve_allowed(building, room, brief)
    polys = {}
    for k, f in enumerate(drawn.values()):
        if f.get("source") == "from_documents" and f.get("footprint") and f.get("type") not in ("unknown",) \
                and f.get("build") is not False and f.get("type") not in schemas.MOUNTED_TYPES:
            try:
                polys[f["id"]] = placer.drawn_piece(f, k).polygon()
            except (KeyError, TypeError, ValueError):
                continue
    for g in GR.drawn_groups(building, room_id):
        anchor = drawn[g["anchor_id"]]
        if unsure_anchor(anchor):                      # fix round after P4a: a code-typed anchor is re-solved too
            continue
        if duplicate_anchor(building, anchor) is not None:
            continue                                   # fix round after P4b: a duplicate outline is never re-solved
        kinds = set(room_kinds(building, room)) | {ZONE_ROOM_TYPE.get(z.get("kind") or "") for z in zones}
        template = GR.load_groups()[g["template"]]
        if not (set(template["room_types"]) & kinds):
            continue
        reason = _resolve_reason(building, room, g, polys)
        if reason is None:
            continue
        if not allowed:
            notes.append(f"{g['template']} around {anchor['id']} not re-solved ({reason}): {why_not}")
            continue
        entry = next((r for r in rows if r["drawn"] and r["anchor_id"] == anchor["id"]), None)
        if entry is None:
            same = next((r for r in rows if r["group"] == g["template"] and not r["drawn"]), None)
            options = _option_of_anchor(g["template"], anchor["type"], list((same or {}).get("options")
                                                                             or template["options"]))
            entry = _entry(room_id, g["template"], True, options, zone_id=(same or {}).get("zone_id"),
                           area=(same or {}).get("area", area), anchor_id=anchor["id"], drawn=True,
                           members=list(g["members"]))
            if same is not None:
                rows.remove(same)
            if any(r["group_id"] == entry["group_id"] for r in rows):
                entry["group_id"] = f"{entry['group_id']}.{anchor['id']}"
            rows.append(entry)
        entry["resolve"] = {"reason": reason, "anchor_id": anchor["id"], "members": list(g["members"]),
                            "centre": list(g["centre"]), "template": g["template"]}
        entry["members"] = sorted(set(entry.get("members") or []) | set(g["members"]))
        entry["missing"] = GR._expected_missing(g["template"], anchor, [drawn[m] for m in entry["members"]
                                                                       if m in drawn], room, building)
        entry["note"] = f"re-solved as one unit around the drawn anchor: {reason}"
        notes.append(f"{g['template']} re-solved around drawn {anchor['type']} {anchor['id']}: {reason}")
    resolving = {r["anchor_id"] for r in rows if r.get("resolve")}
    # A room whose drawn pieces already hold its anchor type never gets a second anchor (a drawn anchor that is
    # re-solved is rebuilt at its place, so it counts too).
    roles = set(schemas.ANCHOR_TYPES.get(rtype, ())) | set(schemas.anchor_types(rtype, subtype))
    if any(f.get("type") in roles and f.get("source") == "from_documents" for f in drawn.values()):
        for r in list(rows):
            t = GR.load_groups()[r["group"]]
            if not r["drawn"] and t["layout"] == "anchored" and set(t["anchor"]["types"]) & roles:
                rows.remove(r)
                notes.append(f"{r['group']} left out: the room's drawn {'/'.join(sorted(roles))} is its anchor"
                             + (" (re-solved)" if resolving else ""))
    # An unknown drawn piece with the size of a missing anchor may be that anchor (reading could not tell): its group
    # gets nothing added, never a second anchor beside it; the agent's retype_piece settles it.
    unknown = [f for f in drawn.values() if f.get("source") == "from_documents" and f.get("type") == "unknown"
               and f.get("build") is not False and (f.get("footprint") or {}).get("size")]
    for r in rows:
        t = GR.load_groups()[r["group"]]
        if r["drawn"] or t["layout"] != "anchored":
            continue
        f = next((u for u in unknown if any(_may_be(a, u["footprint"]["size"]) for a in t["anchor"]["types"])), None)
        if f is not None:
            unknown.remove(f)
            r.update(drawn=True, anchor_id=f["id"], missing=[], note=f"unverified anchor: nothing added (unknown "
                     f"{f['id']} has the size of a {'/'.join(t['anchor']['types'])})")
            notes.append(f"{r['group']}: unknown {f['id']} may be its anchor, nothing added")
    # 3. Choices (the VLM's or the agent's picks).
    for r in rows:
        pick = (choices or {}).get(r["group_id"])
        if pick in r["options"]:
            r["chosen"] = pick
    rows.sort(key=lambda r: (-r["priority"], r["group_id"]))
    out["groups"] = rows
    if rtype != own_type:
        notes.insert(0, f"{own_type} room read as {rtype} (label '{room.get('label')}' / drawn pieces)")
    out["reason"] = "; ".join(notes) or f"{rtype} {area:.1f} m²: {', '.join(r['group'] for r in rows) or 'nothing'}"
    return out
