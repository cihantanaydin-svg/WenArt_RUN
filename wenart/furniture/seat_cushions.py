"""The seats' cushions at the decor stage: arranged for the piece, sized to it, a set of its own (1 Nov 2026, lesson
UL238).

User on real04 run 20261031-194116-full: "This pillow going over the sofa, when you are bedding the sofas or beds
consider the sizes and the final look, try to use better more detailed models with better textures, and realistic
looking pillows, this pillow marked not looking realistic" (a 46 x 44 cm library cushion stood on the back of a low
sofa, far over it, beside the model's own smaller cushions), and on the white corner sofa of the living room: "Same
comment as before related to bedding on this sofa, better model better texture, more logical placement" (four
cushions evenly spaced along a 4.4 m L, one leaning, one floating near the corner).

What (``dress_seats``; pure, the decor stage): every sofa, corner sofa, chaise and armchair the decor stage gave
cushions gets its own set (``soft_sets.seat_cushion_plan``): arranged for its shape (symmetric graded pairs at the ends
of a straight sofa inside its arms, a group in the corner of an L and a pair at its open end, one on an armchair),
sized to the back's height and the seat's depth (the build keeps every top near the back's top on the real mesh:
``rest.plan_decor``), each cushion our own filled model with its finish (piping, a flange, a knife edge, a tufted
centre with buttons, tassels) in a fabric of the family (velvet, boucle, linen, knit ... with their scans or weaves),
coloured from the decor stage's colours (each item keeps its own). The count is the decor stage's (a mirrored twin
keeps its partner's count and each cushion the place nearest to where it stood, so the copies still mirror); the
library cushion it replaces is named on the item (``replaced_asset``); a cushion beyond the shape's arrangement leaves
(``removed``). No two seats of the house alike in their looks and finishes; deterministic from the seat's id.
``building["seat_cushions"]`` records each seat's plan.
"""
from __future__ import annotations

from typing import Callable, Optional

from wenart.blender import bedding_parts as BP
from wenart.blender import soft_sets as SS

RULE = SS.RULE_SEAT
LESSON = SS.LESSON_SEAT
BACK_INSET_M = 0.10              # = decor.host_decor: a cushion's centre this far in front of the back edge (+ half t)


def _local_to_building(host: dict, x: float, y: float) -> list[float]:
    from wenart.furniture import decor as D

    return D._local_to_building(host, x, y)


def _local_x(host: dict, item: dict) -> float:
    """An item's x along its host's width (pure; its host frame)."""
    from wenart import geometry as G

    fp = host["footprint"]
    c = item.get("center") or fp["center"]
    centre = tuple(float(v) for v in fp["center"][:2])
    p = G.rotate_point((float(c[0]), float(c[1])), -float(fp["rotation_deg"]), centre)
    return round(p[0] - float(fp["center"][0]), 6)


def _evidence(text: str) -> list[dict]:
    return [{"file": "building.json", "method": "inferred", "rule": RULE, "confidence": 0.7, "text": text}]


def dress_seats(building: dict, style: Optional[dict], new_id: Callable[[str], str],
                quiet: Optional[set] = None) -> tuple[dict, list[str]]:
    """The seats' cushion sets (module docstring; in place): ``(building, notes)``. A seat without decor cushions is
    left as the decor stage left it (it judged the room and the model: its own scatter cushions, no cushion slot).
    ``quiet``: rooms whose notes are their partner's (a twin's copy): no note of their own."""
    quiet = set(quiet or ())
    fam = str((style or {}).get("family") or "").lower()
    scheme = BP.scheme_colours(style)
    decor = building.setdefault("decor", [])
    seats = sorted([p for p in building.get("furniture") or [] if p.get("type") in SS.SEAT_TYPES
                    and p.get("footprint") and p.get("build", True) is not False], key=lambda p: str(p.get("id")))
    notes: list[str] = []
    record: dict = {}
    taken: set = set()
    gone: set = set()
    for seat in seats:
        mine = [d for d in decor if d.get("type") == "cushion" and d.get("host_id") == seat.get("id")]
        if not mine:
            continue
        colours: list[str] = []
        for d in mine:
            c = d.get("colour")
            if c and c not in colours:
                colours.append(str(c))
        plan = SS.seat_cushion_plan(seat, fam, colours, scheme, taken, count=len(mine))
        if plan.get("signature"):
            taken.add(tuple(plan["signature"]))
        lay = plan["layout"]
        record[seat["id"]] = {"arrangement": plan.get("arrangement"), "size": plan["size"], "layout": lay,
                              "cushions": len(plan["items"]), "why": plan["why"]}
        if not plan["items"]:
            for d in mine:
                d["removed_reason"] = f"{plan['why']} ({LESSON})"
                gone.add(d.get("id"))
            if seat.get("room_id") not in quiet:
                notes.append(f"{seat.get('room_id')}: no cushion on {seat['id']}: {plan['why']}")
            continue
        d_host = float(seat["footprint"]["size"][1])
        rot = float(seat["footprint"]["rotation_deg"])
        # each cushion takes the place nearest to where it stood (by its x along the seat): a mirrored twin's copies
        # keep mirroring their partner's
        mine = sorted(mine, key=lambda d: (_local_x(seat, d), str(d.get("id"))))
        order = sorted(range(len(plan["items"])), key=lambda i: plan["items"][i]["lx"])
        plan["items"] = [plan["items"][i] for i in order]
        for k, spec in enumerate(plan["items"]):
            if k < len(mine):
                it = mine[k]
            else:
                it = {"id": new_id(seat["level_id"]), "kind": "decor", "type": "cushion",
                      "level_id": seat["level_id"], "room_id": seat.get("room_id"), "host_id": seat["id"],
                      "slot": f"{seat['id']}.cushions", "source": "added_by_ai", "status": "verified",
                      "confidence": 0.7}
                decor.append(it)
            old = it.get("asset") if isinstance(it.get("asset"), dict) else None
            t = float(spec["size"][1])
            colour = it.get("colour") or spec["colour"]          # the decor stage's colour stays (the AI's, the brief)
            accent = spec["accent_colour"] if spec["accent_colour"] != colour else spec["colour"]
            text = (f"{spec['kind']} cushion {k + 1} of {len(plan['items'])} ({spec['group']}): {spec['look']} with "
                    f"{spec['finish']} in {colour}; {plan['why']}")
            it.update(center=_local_to_building(seat, float(spec["lx"]), d_host / 2.0 - t / 2.0 - BACK_INSET_M),
                      rotation_deg=rot, size=list(spec["size"]), asset=None, colour=colour, accent_colour=accent,
                      cushion_set={"look": spec["look"], "finish": spec["finish"], "trim_look": spec["trim_look"],
                                   "kind": spec["kind"], "group": spec["group"], "lean_deg": spec["lean_deg"],
                                   "arrangement": plan["arrangement"], "rule": RULE},
                      reason=f"{it['reason']}; {text}" if it.get("reason") and k < len(mine) else text)
            if not it.get("evidence"):
                it["evidence"] = _evidence(text)
            if not it.get("method"):
                it.update(method="rule", rule=RULE)
            if old is not None:
                it["replaced_asset"] = {"asset_id": old.get("asset_id"), "title": old.get("title"),
                                        "reason": "our own filled cushion with its finish, sized to the seat "
                                                  f"({LESSON}: 'realistic looking pillows')"}
            it.pop("host_frame", None)                 # attach_host_frames measures it again
        for d in mine[len(plan["items"]):]:
            d["removed_reason"] = f"beyond the seat's arrangement ({plan['arrangement']}; {LESSON})"
            gone.add(d.get("id"))
        if seat.get("room_id") not in quiet:
            notes.append(f"{seat.get('room_id')}: {seat['id']} {len(plan['items'])} cushion(s), "
                         f"{str(plan['arrangement']).replace('_', ' ')} ({LESSON})")
    removed = [d for d in decor if d.get("id") in gone]
    building["decor"] = [d for d in decor if d.get("id") not in gone]
    building["seat_cushions"] = {"rule": RULE, "lesson": LESSON, "seats": record, "notes": notes,
                                 "removed": [{"id": d.get("id"), "host_id": d.get("host_id"),
                                              "reason": d.get("removed_reason")} for d in removed]}
    return building, notes
