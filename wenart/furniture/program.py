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
| balcony | balcony (plants in big pots, no table and chairs: UL130) from 2.5 m² |

   Stair rooms, shafts, prayer rooms and rooms the brief switches off get no group (``reason`` says why).
   23 Oct 2026 (user: "increase the group furniture options 10x"): each row also gets the group's *extra* options
   whose area window (``min_area`` / ``max_area``, ``min_wall``, ``min_width``, ``subtype`` in ``groups.yaml``) the
   room or zone allows (``groups.extra_options``: 263 options in all, 26 before), and the groups that have only
   extras (``reading_corner``, ``bedroom_chest``) come as optional rows; a drawn group keeps the core options
   (``drawn_options``) and an ``auto: false`` option (a bunk bed, a crib) comes only as a choice.
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

Fix round of 26 Oct 2026 (user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"). What: (B) a room with zones plans its zones' rows and, outside the zones, its own type's rows on the area
the zones leave (``rest_place``; not when a zone is of the room's own kind); a drawn anchor outside the zone of its
row is completed in the room (``_in_zone``). (C) At most one dining group per room: of several dining rows only the
room's own stays (``one_dining_row``), none beside a drawn table set; of several drawn table sets the main one
(``primary_table``: the most drawn chairs, then the largest table) is completed, every other gets nothing added and is
not re-solved, with ``out["second_tables"]`` naming it (the layout writes the warning). Drawn tables that touch are
merged before the program by the completion (``groups.merge_touching_tables``). Why: real06's r_L1_oda_2 (a bedroom
whose two misread counters made a kitchen zone) was planned as the zone only and got no bed; its living room had four
drawn table sets (armchairs read as tables) and each got its own dining group with chairs.

Dressing rooms of 26 Oct 2026 (user: "fix should be general"). What: a ``dressing`` kind (``TEMPLATE_KINDS``; no
building-schema room type has it): a storage / other / unknown room whose label names a dressing room or walk-in
closet (``groups.yaml`` ``room_aliases.dressing``: soyunma, giyinme, dressing, walk-in, closet, vestiaire, Ankleide,
cabina armadio, vestidor, ...) or whose every door opens into a bedroom (``dressing_room``, ``door_neighbours``; 1.5 to
8 m²) gets the ``dressing`` row (wardrobe runs along its free walls, a bench where it fits); a storage room read so is
no longer left out ("storage room: no furniture groups"). Why: real06's 5.9 m² "Soyunma Odası" (other) got "no groups
for this room (other 5.9 m²: nothing)" and rendered as a bare shell.

Density of 29 Oct 2026 (user on real06 run 20261028-154514-full, cam_r_L0_salon_1: "This scene I like it but a bit
more furniture would be nice", lesson UL98). What: a room with drawn furniture keeps the groups that only have extra
options (a reading corner, a bedroom chest) as optional rows when it is under its furniture density
(``room_fill.under_density``: the share of its floor its pieces cover, measured, against ``room_fill.DENSITY_TARGET``
of its kind, for rooms of at least ``room_fill.DENSITY_MIN_M2``); the row's note gives the measured share. Before, a
furnished room was "completed only" whatever its size. Why: real06's 55.6 m² living and dining room had 18 % of its
floor furnished and wide empty floor between the seating and the table; the solver adds what fits and the walkways
decide.
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
# 26 Oct 2026: ``dressing`` (a dressing room or walk-in closet) is a kind only: no building-schema room type has it.
TEMPLATE_KINDS = ("living", "bedroom", "kitchen", "dining", "bathroom", "wc", "hall", "other", "balcony", "dressing")
# 26 Oct 2026: the room types a dressing room is read from (its label words or its bedroom door, ``dressing_room``).
DRESSING_FROM = ("storage", "other", "unknown", None, "")
DOOR_PROBES_M = (0.35, 0.5, 0.7)   # the other side of a door: this far behind the inner wall face
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
    if dressing_room(building, room):
        return "dressing"                          # 26 Oct 2026: a small room whose every door opens into a bedroom
    return rtype if rtype in TEMPLATE_KINDS else "other"


def door_neighbours(building: dict, room: dict) -> list[Optional[str]]:
    """26 Oct 2026: the id of the room on the other side of each door or opening of ``room`` (its level's rooms; None
    where no room lies behind it), in the order of ``placer.room_context``'s doors."""
    if len(room.get("polygon") or []) < 3:
        return []
    try:
        ctx = placer.room_context(building, room)
    except (KeyError, TypeError, ValueError):
        return []
    from shapely.geometry import Point

    others = []
    for r in building.get("rooms") or []:
        if r.get("id") == room.get("id") or r.get("level_id") != room.get("level_id") \
                or len(r.get("polygon") or []) < 3:
            continue
        try:
            others.append((r["id"], Polygon(r["polygon"]).buffer(0)))
        except (KeyError, TypeError, ValueError):
            continue
    out: list[Optional[str]] = []
    for door in ctx.doors:
        n = door.normal
        if n is None:
            out.append(None)
            continue
        hit = None
        for k in DOOR_PROBES_M:
            p = Point(door.inner_point[0] - n[0] * k, door.inner_point[1] - n[1] * k)
            hit = next((rid for rid, poly in others if poly.contains(p)), None)
            if hit is not None:
                break
        out.append(hit)
    return out


def _bedroom_by_label(room: dict) -> bool:
    """A bedroom by its type or the words of its label (no door rule: no recursion between neighbours)."""
    if room.get("room_type") == "bedroom":
        return True
    spec = GR.room_aliases().get("bedroom") or {}
    key = _alias_hit(_label_words(room), list(spec.get("words") or []))
    generic = {str(w) for w in GR.room_aliases().get("generic") or []}
    return key is not None and key not in generic and (spec.get("min_area") is None or _area(room) >= float(
        spec["min_area"]) - 1e-9)


def dressing_room(building: dict, room: dict) -> bool:
    """26 Oct 2026 (user: "fix should be general"): a storage / other / unknown room (``DRESSING_FROM``) of
    ``room_aliases.dressing.min_area`` .. ``off_bedroom_max_area`` m² whose every door opens into a bedroom (at least
    one door) is a dressing room or walk-in closet, whatever its label says (the label words of ``room_aliases``
    are read first by ``room_kind``). Why: a closet off a bedroom is often labelled only "Oda", "Depo" or nothing."""
    if room.get("room_type") not in DRESSING_FROM:
        return False
    spec = GR.room_aliases().get("dressing") or {}
    area = _area(room)
    lo, hi = float(spec.get("min_area") or 0.0), float(spec.get("off_bedroom_max_area") or 0.0)
    if not (lo - 1e-9 <= area <= hi + 1e-9):
        return False
    sides = door_neighbours(building, room)
    if not sides or any(s is None for s in sides):
        return False
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    return all(_bedroom_by_label(rooms[s]) for s in sides if s in rooms) and all(s in rooms for s in sides)


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
    """``(group, required, options)`` rows for a room or zone of ``kind`` (a room type): the rule table's rows
    (``_core_rows``) with the extra options of each group the room's size allows (``groups.extra_options``; none
    where the small-room rule narrows the options), then one optional row per group without core options whose
    ``room_types`` name the kind and whose extras the room allows (the reading corner, the bedroom chest; 23 Oct
    2026, user: "increase the group furniture options 10x")."""
    rows = _core_rows(kind, area, polygon, building, room, subtype)
    narrowed = {"seating"} if kind == "living" and (GR.small_room("living", area) or {}).get("options") else set()
    longest, width = longest_wall(polygon), min_width(polygon)
    out = []
    for group, required, options in rows:
        extra = [] if group in narrowed else GR.extra_options(group, area, longest, width, subtype)
        out.append((group, required, list(dict.fromkeys(list(options) + extra))))
    have = {r[0] for r in out}
    for group, template in GR.load_groups().items():
        if group in have or kind not in template["room_types"] or GR.core_options(group):
            continue
        extra = GR.extra_options(group, area, longest, width, subtype)
        if extra:
            out.append((group, False, extra))
    return out


# 25 Oct 2026 (user: "furniture groups are not sufficient"): a drawn group is completed with the accessories a
# designer adds (CLAUDE.md: the AI adds the pieces the room type misses, never a second anchor): an extra option of
# the room's size whose counts only add these types, take nothing away and leave the drawn anchor's size alone.
ACCESSORY_TYPES = ("side_table", "floor_lamp", "potted_plant", "bench", "dresser", "armchair", "ottoman")


def _accessory_option(group: str, opt: dict) -> bool:
    if opt.get("sizes") or opt.get("partner_sizes") or opt.get("auto") is False:
        return False                          # accessories add pieces; they never resize the anchor or the core
    template = GR.load_groups()[group]
    partners = {p["type"]: p for p in template.get("partners") or []}
    core = [o for o in template["options"].values() if GR.is_core(o)]
    for ftype, n in (opt.get("counts") or {}).items():
        p = partners.get(ftype)
        # the fewest of the type a core option leaves (the core options choose 0-2 armchairs, a bench or none)
        base = min([int((o.get("counts") or {}).get(ftype)) for o in core if ftype in (o.get("counts") or {})]
                   or [int((p or {}).get("default", (p or {}).get("max", 1)) or 0)])
        if int(n) < base or (int(n) > base and ftype not in ACCESSORY_TYPES):
            return False
    return True


def core_only(group: str, options: list[str]) -> list[str]:
    """The core options of ``options`` (else ``options``): a drawn group re-solved as one unit is put right, not
    accessorised in the same step."""
    opts = GR.load_groups()[group]["options"]
    return [o for o in options if o in opts and GR.is_core(opts[o])] or list(options)


def drawn_options(group: str, options: list[str]) -> list[str]:
    """The options a drawn group is completed with: the core ones of ``options`` (else all core options of the
    group) and, since 25 Oct 2026, the extras of ``options`` that only add accessories (``ACCESSORY_TYPES``: end
    tables, a floor lamp, a plant, a bench, a dresser, an armchair) and keep the drawn anchor's size."""
    opts = GR.load_groups()[group]["options"]
    core = [o for o in options if o in opts and GR.is_core(opts[o])] or GR.core_options(group) or list(options)
    extra = [o for o in options if o in opts and not GR.is_core(opts[o]) and _accessory_option(group, opts[o])]
    return list(dict.fromkeys(core + extra))


def _core_rows(kind: str, area: float, polygon: Polygon, building: dict, room: dict,
               subtype: Optional[str]) -> list[tuple]:
    """``(group, required, core options)`` rows of the rule table for a room or zone of ``kind``."""
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
        if area >= 2.5:                     # 30 Oct 2026 (UL130): plants in big pots, no table and chairs
            rows.append(("balcony", False, ["planters"]))
    elif kind == "dressing":
        # 26 Oct 2026: a dressing room or walk-in closet: wardrobe runs along its free walls (groups.yaml dressing)
        rows.append(("dressing", True, ["wardrobe_runs"]))
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


REST_MIN_M2 = 0.5                  # 26 Oct 2026: a room part outside its zones smaller than this holds no groups


def rest_place(rtype: str, polygon: Polygon, area: float, zone_polys: list, zone_kinds: list) -> Optional[tuple]:
    """26 Oct 2026 (fix B, user: "fix should be general"): ``(None, rtype, area, polygon)`` of the part of a zoned
    room outside its zones, which keeps the room's own type's groups, or None when a zone already is of the room's own
    kind (``ROOM_ZONE_KIND``: an open plan with a living zone) or nothing is left. What: the area is the room's area
    less what its zones cover (the size variants read it), the polygon the largest part of the rest (its walls and
    width). Why: ``room_program`` planned only the zones of a zoned room, so a bedroom whose drawing the reading gave
    a kitchen zone (real06's r_L1_oda_2, two misread counters) got no bed, and a living room with an open kitchen
    zone and no drawn sofa would get no seating. The solver places these groups anywhere in the room (zone None)."""
    if ROOM_ZONE_KIND.get(rtype) in set(zone_kinds) or not zone_polys:
        return None
    from shapely.ops import unary_union

    try:
        covered = unary_union(zone_polys).intersection(polygon)
        rest = polygon.difference(covered)
    except Exception:  # noqa: BLE001 - an odd zone geometry: the room as it is
        return None
    rest_area = float(area) * rest.area / polygon.area if polygon.area > 1e-9 else 0.0
    if rest.is_empty or rest_area < REST_MIN_M2:
        return None
    parts = [g for g in getattr(rest, "geoms", [rest]) if g.geom_type == "Polygon" and g.area > 1e-6]
    poly = max(parts, key=lambda g: g.area) if parts else polygon
    return (None, rtype, round(rest_area, 3), poly)


def one_dining_row(rows: list[dict]) -> list[dict]:
    """26 Oct 2026 (fix C): at most one dining group per room: of several dining rows (a kitchen zone's and the
    room's own), the room's own one stays (the solver's ``related_near`` term still pulls it towards the kitchen),
    else the first; a drawn dining group replaces them all (``room_program``)."""
    dining = [r for r in rows if r["group"] == "dining"]
    if any(r["drawn"] for r in dining):
        return [r for r in rows if r["group"] != "dining" or r["drawn"]]
    if len(dining) <= 1:
        return rows
    keep = next((r for r in dining if r.get("zone_id") is None), dining[0])
    return [r for r in rows if r["group"] != "dining" or r is keep]


def _in_zone(piece: dict, zones: list[dict], zone_id: str) -> bool:
    """26 Oct 2026: the drawn piece's centre lies in the zone ``zone_id`` (within 0.10 m); True when the zone or the
    centre is unknown (as before)."""
    zone = next((z for z in zones if z.get("zone_id") == zone_id), None)
    centre = (piece.get("footprint") or {}).get("center")
    if zone is None or not centre:
        return True
    from shapely.geometry import Point

    return Polygon(zone["polygon"]).buffer(0.1).contains(Point(float(centre[0]), float(centre[1])))


def primary_table(entries: list[dict], drawn: dict) -> Optional[str]:
    """26 Oct 2026 (fix C): the anchor id of the room's main drawn table set among drawn dining ``entries``: a sure
    anchor before an unsure one (``unsure_anchor``), then the most drawn chairs, the largest table, the id."""
    def key(e):
        f = drawn.get(e["anchor_id"]) or {}
        size = (f.get("footprint") or {}).get("size") or [0.0, 0.0]
        return (unsure_anchor(f), -len(e.get("members") or []), -float(size[0]) * float(size[1]), str(e["anchor_id"]))
    return min(entries, key=key)["anchor_id"] if entries else None


def _density(building: dict, room: dict, rtype: str) -> tuple[bool, float, float]:
    """29 Oct 2026 (UL98): ``(under, share, target)`` of ``room_fill.under_density`` (``target`` 0 without one)."""
    from wenart.furniture import room_fill as RF

    if rtype not in RF.DENSITY_TARGET:
        return False, 0.0, 0.0
    under, share, target = RF.under_density(building, room, rtype)
    return under, share, float(target or 0.0)


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
        # 26 Oct 2026: a storage room read as a dressing room (its label, its bedroom door) is furnished as one
        if not (own_type == "storage" and room_kind(building, room) == "dressing"):
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
        else:
            # 26 Oct 2026 (fix B): the rest of the room keeps its own type's groups (a living room with an open
            # kitchen zone keeps its seating, a bedroom its bed) unless a zone already is of the room's own kind.
            rest = rest_place(rtype, polygon, area, [Polygon(z["polygon"]).buffer(0) for z in zones],
                              [z.get("kind") for z in zones])
            if rest is not None:
                places.append(rest)
    rows: list[dict] = []
    for zone_id, kind, a, poly in places:
        for group, required, options in _rows(kind, a, poly, building, room, subtype):
            rows.append(_entry(room_id, group, required, options, zone_id=zone_id, area=a))
    rows = one_dining_row(rows)            # 26 Oct 2026 (fix C): at most one dining group in a room
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
        options = drawn_options(name, own or list(template["options"]))
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
        # 26 Oct 2026 (fix B): a drawn anchor outside the zone of its row's group is completed in the room, not in
        # the zone (a drawn table in the living part of a room with a kitchen zone)
        zone_id = (same or {}).get("zone_id")
        if zone_id is not None and not _in_zone(anchor, out["zones"], zone_id):
            zone_id = None
        entry = _entry(room_id, name, True, options, zone_id=zone_id,
                       area=(same or {}).get("area", area), anchor_id=anchor["id"], drawn=True,
                       members=drawn_members, missing=[] if (unsure or foreign) else g.get("missing", []), note=note)
        if same is not None:
            rows.remove(same)
        if any(r["group_id"] == entry["group_id"] for r in rows):
            entry["group_id"] = f"{entry['group_id']}.{anchor['id']}"
        rows.append(entry)
        notes.append(f"{name} completed around drawn {anchor['type']} {anchor['id']}")
    # 26 Oct 2026 (fix C, user: "fix should be general"): at most one dining group per room. The main drawn table
    # set (``primary_table``) is completed; every other drawn table set of the room is reported (``second_tables``,
    # a warning of the layout) and gets nothing added or re-solved; no dining group is planned beside a drawn one.
    rows = one_dining_row(rows)
    drawn_sets = GR.drawn_groups(building, room_id)
    table_sets = [{"anchor_id": g["anchor_id"], "members": list(g["members"])} for g in drawn_sets
                  if g["template"] == "dining"]
    table_sets += [{"anchor_id": r["anchor_id"], "members": list(r["members"])} for r in rows
                   if r["drawn"] and r["group"] == "dining" and r["anchor_id"] not in {t["anchor_id"] for t in table_sets}]
    main_table = primary_table(table_sets, drawn)
    second = {t["anchor_id"] for t in table_sets if t["anchor_id"] != main_table}
    out["second_tables"] = [
        {"anchor_id": t["anchor_id"], "main": main_table, "members": t["members"],
         "reason": f"drawn table_dining {t['anchor_id']} is a second table set in the room beside {main_table}: "
                   "nothing added to it (at most one dining group per room); listed for review"}
        for t in sorted(table_sets, key=lambda t: str(t["anchor_id"])) if t["anchor_id"] in second]
    for r in rows:
        if r["drawn"] and r["group"] == "dining" and r["anchor_id"] in second:
            r["missing"] = []
            r["note"] = (f"second drawn table set in the room (main: {main_table}): nothing added, at most one "
                         "dining group per room (reported)")
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
    for g in drawn_sets:
        anchor = drawn[g["anchor_id"]]
        if unsure_anchor(anchor):                      # fix round after P4a: a code-typed anchor is re-solved too
            continue
        if g["anchor_id"] in second:
            continue                                   # 26 Oct 2026 (fix C): a second table set is only reported
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
            options = _option_of_anchor(g["template"], anchor["type"], drawn_options(
                g["template"], list((same or {}).get("options") or template["options"])))
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
        entry["options"] = core_only(g["template"], entry["options"])   # a re-solve fixes the drawn group only
        entry["members"] = sorted(set(entry.get("members") or []) | set(g["members"]))
        entry["missing"] = GR._expected_missing(g["template"], anchor, [drawn[m] for m in entry["members"]
                                                                       if m in drawn], room, building)
        entry["note"] = f"re-solved as one unit around the drawn anchor: {reason}"
        notes.append(f"{g['template']} re-solved around drawn {anchor['type']} {anchor['id']}: {reason}")
    # 23 Oct 2026 (group options 10x): a room with drawn furniture is completed with what its type misses; the
    # groups that only have extra options (a reading corner, a bedroom chest) are additions, never a completion.
    if any(r["drawn"] for r in rows):
        extra_only = [r for r in rows if not r["drawn"] and not GR.core_options(r["group"])]
        # 29 Oct 2026 (user on real06: "a bit more furniture would be nice", UL98): a furnished room under its
        # furniture density (room_fill.under_density: the share of its floor its pieces cover) keeps them as optional
        # rows: the solver adds what fits, the walkways and clearances decide
        under, share, target = _density(building, room, rtype)
        if under and extra_only:
            for r in extra_only:
                r["note"] = (f"density: {share * 100:.0f} % of the floor is furnished, under {target * 100:.0f} % for "
                             f"a {rtype} room of {area:.1f} m² (room_fill.under_density, UL98)")
            notes.append(f"{', '.join(r['group'] for r in extra_only)} kept: the room is {share * 100:.0f} % furnished "
                         f"(under {target * 100:.0f} %)")
            extra_only = []
        for r in extra_only:
            rows.remove(r)
        if extra_only:
            notes.append(f"no {', '.join(r['group'] for r in extra_only)} (drawn furniture: completed only)")
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
        opts = GR.load_groups()[r["group"]]["options"]
        if pick not in r["options"] and not r["drawn"] and (opts.get(pick) or {}).get("auto") is False:
            r["options"].append(pick)              # an option offered only on request (a bunk bed, a crib)
        if pick in r["options"]:
            r["chosen"] = pick
    rows.sort(key=lambda r: (-r["priority"], r["group_id"]))
    out["groups"] = rows
    if rtype != own_type:
        notes.insert(0, f"{own_type} room read as {rtype} (label '{room.get('label')}' / drawn pieces)")
    out["reason"] = "; ".join(notes) or f"{rtype} {area:.1f} m²: {', '.join(r['group'] for r in rows) or 'nothing'}"
    return out
