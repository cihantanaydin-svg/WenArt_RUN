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
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import Polygon

from wenart.furniture import groups as GR
from wenart.furniture import schemas

NOT_FURNISHED = ("prayer", "stair", "shaft", "storage", "unknown")
ROOM_ZONE_KIND = {"living": "living", "bedroom": "sleeping", "kitchen": "kitchen", "dining": "dining",
                  "bathroom": "bath", "wc": "bath", "hall": "hall", "other": "work", "balcony": "balcony"}
ZONE_ROOM_TYPE = {"living": "living", "sleeping": "bedroom", "kitchen": "kitchen", "dining": "dining",
                  "work": "other", "bath": "bathroom", "hall": "hall", "balcony": "balcony"}
MIN_HALL_WIDTH_M = 1.10            # a hall narrower than this takes no piece (0.30 deep piece + 0.80 walkway)


def _room(building: dict, room_id: str) -> dict:
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    return room


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
        if area >= 2.5 and min_width(polygon) >= MIN_HALL_WIDTH_M:
            rows.append(("entrance", False, ["shoe_cabinet", "console"]))
    elif kind == "other":
        if area >= 6.0:
            rows.append(("work", False, ["desk"]))
    elif kind == "balcony":
        if area >= 2.5:
            rows.append(("balcony", False, ["table_2_chairs"]))
    return rows


def _option_of_anchor(group: str, anchor_type: str, options: list[str]) -> list[str]:
    """The options a drawn anchor allows (a drawn corner sofa: the corner-sofa option)."""
    t = GR.load_groups()[group]
    keep = [o for o in options if t["options"][o].get("anchor") in (None, anchor_type)]
    return keep or options


def room_program(building: dict, room_id: str, brief: Optional[dict] = None, choices: Optional[dict] = None) -> dict:
    room = _room(building, room_id)
    rtype = room.get("room_type") or "unknown"
    out = {"room_id": room_id, "zones": [], "groups": [], "reason": ""}
    zones = [z for z in room.get("zones") or [] if len(z.get("polygon") or []) >= 3]
    out["zones"] = [{"zone_id": z.get("zone_id") or f"{room_id}.z{k}", "kind": z.get("kind"),
                     "polygon": z["polygon"]} for k, z in enumerate(zones)]
    if len(room.get("polygon") or []) < 3:
        out["reason"] = "the room has no polygon"
        return out
    brief = brief if brief is not None else ((building.get("project") or {}).get("brief") or {})
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
        options = (same or {}).get("options") or list(GR.load_groups()[name]["options"])
        if GR.load_groups()[name]["layout"] == "anchored":
            options = _option_of_anchor(name, anchor["type"], options)
        unsure = anchor.get("status") == "unverified"
        drawn_members = [m for m in g["member_ids"] if (drawn.get(m) or {}).get("source") == "from_documents"]
        entry = _entry(room_id, name, True, options, zone_id=(same or {}).get("zone_id"),
                       area=(same or {}).get("area", area), anchor_id=anchor["id"], drawn=True,
                       members=drawn_members, missing=[] if unsure else g.get("missing", []),
                       note="unverified anchor: nothing added" if unsure else "")
        if same is not None:
            rows.remove(same)
        if any(r["group_id"] == entry["group_id"] for r in rows):
            entry["group_id"] = f"{entry['group_id']}.{anchor['id']}"
        rows.append(entry)
        notes.append(f"{name} completed around drawn {anchor['type']} {anchor['id']}")
    # A room whose drawn pieces already hold its anchor type never gets a second anchor.
    roles = set(schemas.ANCHOR_TYPES.get(rtype, ())) | set(schemas.anchor_types(rtype, subtype))
    if any(f.get("type") in roles and f.get("source") == "from_documents" for f in drawn.values()):
        for r in list(rows):
            t = GR.load_groups()[r["group"]]
            if not r["drawn"] and t["layout"] == "anchored" and set(t["anchor"]["types"]) & roles:
                rows.remove(r)
                notes.append(f"{r['group']} left out: the room's drawn {'/'.join(sorted(roles))} is its anchor")
    # 3. Choices (the VLM's or the agent's picks).
    for r in rows:
        pick = (choices or {}).get(r["group_id"])
        if pick in r["options"]:
            r["chosen"] = pick
    rows.sort(key=lambda r: (-r["priority"], r["group_id"]))
    out["groups"] = rows
    out["reason"] = "; ".join(notes) or f"{rtype} {area:.1f} m²: {', '.join(r['group'] for r in rows) or 'nothing'}"
    return out
