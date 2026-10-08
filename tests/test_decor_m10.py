"""Milestone 10 decor (docs/milestone10.md §4.6, §1.6b rows 18, 20; wenart/furniture/decor.py, decor_ai.py; track F).

The 12 new decor types get M9-style slots: ``window`` slots (curtains for windows at least 0.9 m wide, never over a
door, sill length over furniture; a roller blind for every window), ``ceiling`` slots (pendants over a dining or
coffee table and a bed, a ceiling light at the room centre), throws on sofas and beds, cushions along a corner sofa,
on a chaise, an ottoman and a bench, the top slots of sideboards and console tables, a wall clock, floor corners for
large plants; the brief's words (cushion colours in turn, plant species and pots, lamps on in the interior evening)
win over the AI's; a corner sofa's rug lies in its inner corner and the new storage blocks rugs; second twins and
``same_as`` rooms are not asked and get a mirrored copy of their partner's decor (``mirrored_from``).
"""
from __future__ import annotations

import json

import pytest

from wenart import building as B
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA

from test_decor_ai import STYLE, FakeClient, applied, by_id, choose, slots_of
from test_decor_m8 import EV, RID, room_building

PROFILE = {"lighting": {"mood": "interior evening"},
           "decor": {"plant_species": ["palm", "monstera", "fern"], "plant_amount": "many",
                     "pots": [{"material": "rattan", "colour": None}, {"material": None, "colour": "cream"}],
                     "cushion_colours": ["cream", "mustard"], "throw_colours": [], "curtain_colour": "off white",
                     "rug_colours": []}}


# --------------------------------------------------------------------------
# Window slots
# --------------------------------------------------------------------------

def test_window_slots_take_curtains_and_blinds_never_over_a_door():
    b = room_building(furniture=[("table_coffee", (3.0, 2.5), 0.0, (1.0, 0.6))],
                      windows=[("win_big", "s", 2.0, 1.6), ("win_small", "e", 2.5, 0.6)],
                      doors=[("d_1", "s", 3.6, 0.9, True)])
    slots, notes = slots_of(b)
    ids = by_id(slots)
    big, small = ids["window:win_big"], ids["window:win_small"]
    assert big.kind == small.kind == "window" and big.types == ("curtain", "blind") and small.types == ("blind",)
    assert not any(s.id.startswith("window:d_") for s in slots)                # doors get no slot
    curtain = big.items["curtain"]
    # The rod would run 0.2 m past the window; on the door's side it stops 0.1 m before the door (2.8 + 0.45 + 0.1).
    left = curtain["wall_point"][0] - curtain["size"][0] / 2.0
    right = curtain["wall_point"][0] + curtain["size"][0] / 2.0
    assert left == pytest.approx(2.0 - 0.8 - 0.2, abs=1e-6) and right <= 3.6 - 0.45 - D.OPENING_MARGIN_M + 1e-6
    assert curtain["window_id"] == "win_big" and curtain["center"][2] == DA.CURTAIN_FLOOR_GAP_M
    assert curtain["size"][2] == pytest.approx(0.9 + 1.2 + DA.CURTAIN_ROD_ABOVE_M - DA.CURTAIN_FLOOR_GAP_M)
    assert curtain["rotation_deg"] == pytest.approx(180.0) and curtain["center"][1] == pytest.approx(DA.CURTAIN_WALL_GAP_M)
    blind = small.items["blind"]
    assert blind["size"][0] == pytest.approx(0.6 + DA.BLIND_WIDTH_EXTRA_M)
    assert blind["rotation_deg"] == pytest.approx(270.0)                           # facing -X from the east wall
    top = blind["center"][2] + blind["size"][2]
    assert top == pytest.approx(0.9 + 1.2 + DA.BLIND_ROLLER_ABOVE_M)


def test_a_curtain_over_furniture_ends_at_the_sill():
    b = room_building(furniture=[("sofa", (3.0, 0.45), 180.0, (2.2, 0.9))], windows=[("win", "s", 3.0, 1.6)])
    curtain = by_id(slots_of(b)[0])["window:win"].items["curtain"]
    assert curtain["center"][2] == pytest.approx(0.9 - DA.CURTAIN_SILL_DROP_M) and "sill length" in curtain["reason"]


# --------------------------------------------------------------------------
# Ceiling, soft, top, wall and floor slots
# --------------------------------------------------------------------------

def test_ceiling_slots_over_tables_beds_and_the_room_centre():
    b = room_building(room_type="dining", furniture=[("table_dining", (2.0, 2.5), 0.0, (1.6, 0.9))])
    ids = by_id(slots_of(b)[0])
    over = ids["ceiling:over_f_L0_001"]
    assert over.kind == "ceiling" and over.types == ("pendant_light",) and over.host_id == "f_L0_001"
    pendant = over.items["pendant_light"]
    assert pendant["center"][2] == pytest.approx(D.placer_bbox_height(b["furniture"][0]) + DA.PENDANT_OVER_TABLE_M)
    assert pendant["size"][2] == pytest.approx(2.7 - pendant["center"][2])        # the cord reaches the ceiling
    centre = ids[f"ceiling:centre_{RID}"]
    assert set(centre.types) == {"ceiling_light", "pendant_light"}
    assert centre.items["ceiling_light"]["center"][2] == pytest.approx(2.7 - DA.CEILING_LIGHT_SIZE[2])
    low = room_building(furniture=[("table_coffee", (3.0, 2.5), 0.0, (1.0, 0.6))], ceiling=2.2)
    ids = by_id(slots_of(low)[0])
    assert ids["ceiling:over_f_L0_001"].types == ("ceiling_light",)              # no pendant to bump into
    near = room_building(furniture=[("table_coffee", (3.0, 2.5), 0.0, (1.0, 0.6))])
    assert f"ceiling:centre_{RID}" not in by_id(slots_of(near)[0])               # too near the coffee table light


def test_soft_top_wall_and_floor_slots_of_the_new_types():
    b = room_building(width=7.0, depth=6.0, furniture=[
        ("sofa_corner", (3.0, 5.2), 0.0, (2.6, 1.6)), ("sideboard", (6.75, 3.0), 270.0, (1.6, 0.45)),
        ("ottoman", (1.0, 2.0), 0.0, (0.6, 0.6)), ("bench", (4.0, 1.0), 0.0, (1.2, 0.4))])
    b["furniture"][0].update(shape="L", chaise_side="right", chaise_depth=1.6)
    ids = by_id(slots_of(b)[0])
    cushions = ids["f_L0_001.cushions"].items["cushion"]
    assert len(cushions) == int(2.6 / D.CORNER_SOFA_CUSHION_PITCH_M)              # along the L's back
    throw = ids["f_L0_001.throw"].items["throw"][0]
    assert throw["center"][0] > 3.0                                               # on the chaise (right)
    assert ids["f_L0_002.left"].types[0] == "table_lamp" and "tray" in ids["f_L0_002.left"].types
    assert set(ids["f_L0_002.wall"].types) <= {"wall_art", "mirror", "clock"} and "clock" in ids["f_L0_002.wall"].types
    clock = ids["f_L0_002.wall"].items["clock"]
    assert clock["size"][0] == DA.CLOCK_WIDTH[0] and clock["type"] == "clock"
    assert len(ids["f_L0_003.cushions"].items["cushion"]) == 1 and len(ids["f_L0_004.cushions"].items["cushion"]) == 2
    floors = [s for s in by_id(slots_of(b)[0]).values() if s.kind == "floor"]
    assert floors and any("plant_large" in s.types for s in floors)
    large = next(s for s in floors if "plant_large" in s.types).items["plant_large"]
    assert large["size"] == list(DA.FLOOR_ITEM_SIZES["plant_large"])
    bed = room_building(room_type="bedroom", furniture=[("bed_double", (3.0, 3.9), 0.0, (1.6, 2.0))])
    throw = by_id(slots_of(bed)[0])["f_L0_001.throw"].items["throw"][0]
    assert throw["size"][0] == pytest.approx(1.6 * 0.95) and throw["center"][1] < 3.9 - 0.5


def test_corner_sofa_rug_lies_in_the_inner_corner_and_storage_blocks_rugs():
    b = room_building(width=7.0, depth=6.0, furniture=[("sofa_corner", (3.0, 5.2), 0.0, (2.6, 1.6)),
                                                       ("table_coffee", (2.6, 3.2), 0.0, (1.0, 0.6))])
    b["furniture"][0].update(shape="L", chaise_side="right", chaise_depth=1.6)
    rugs, notes = D.rugs_for_room(b["rooms"][0], b["furniture"], b)
    assert len(rugs) == 1 and rugs[0]["anchor_ids"] == ["f_L0_001", "f_L0_002"]
    x0, x1 = rugs[0]["center"][0] - rugs[0]["size"][0] / 2.0, rugs[0]["center"][0] + rugs[0]["size"][0] / 2.0
    assert x1 <= 3.0 + 1.3 - 0.9 + D.RUG_MARGIN_M + 1e-6                         # not under the chaise (right)
    assert x0 < 2.6 - 0.5                                                          # the coffee table is on it
    assert {"tall_cabinet", "wall_cabinet", "shoe_cabinet", "display_cabinet", "sideboard"} <= set(D.RUG_BLOCKER_TYPES)


# --------------------------------------------------------------------------
# Apply: the brief's words, lights, the schema
# --------------------------------------------------------------------------

def test_apply_builds_the_new_types_with_the_brief_looks():
    b = room_building(width=7.0, depth=6.0, furniture=[("sofa", (3.0, 5.5), 0.0, (2.2, 0.9)),
                                                       ("table_coffee", (3.0, 3.6), 0.0, (1.0, 0.6))],
                      windows=[("win", "s", 3.0, 1.6)])
    answer = choose(("f_L0_001.cushions", "cushion", "navy"), ("window:win", "curtain", "sage green"),
                    ("ceiling:over_f_L0_002", "pendant_light", "brass"), ("corner1", "plant_large", "olive"),
                    ("corner2", "plant_large", "olive"), ("f_L0_001.throw", "throw", "rust"),
                    ("f_L0_002.centre", "candle", "white"))
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answers.json"
        client = FakeClient(answer)
        DA.ask(b, STYLE, client, path, client.model, log=lambda *a: None)
        out, records = DA.apply(b, STYLE, DA.read_answers(path), style=PROFILE)
    B.validate(out)
    ai = [d for d in out["decor"] if d["method"] == "ai"]
    cushions = [d for d in ai if d["type"] == "cushion"]
    assert [c["colour"] for c in cushions] == ["cream", "mustard"]                  # the brief's colours in turn
    assert all(c["colour_ai"] == "navy" and c["colour_source"] == "brief" for c in cushions)
    curtain = next(d for d in ai if d["type"] == "curtain")
    assert curtain["colour"] == "off white" and curtain["window_id"] == "win" and curtain["host_id"] is None
    pendant = next(d for d in ai if d["type"] == "pendant_light")
    assert pendant["light_on"] is True and pendant["anchor_ids"] == ["f_L0_002"]
    plants = [d for d in ai if d["type"] == "plant_large"]
    assert [p["species"] for p in plants] == ["palm", "monstera"][:len(plants)] and plants
    assert plants[0]["pot"] == {"material": "rattan", "colour": None}
    throw = next(d for d in ai if d["type"] == "throw")
    assert throw["colour"] == "rust" and throw["host_id"] == "f_L0_001"            # no throw colour in the brief
    assert next(d for d in ai if d["type"] == "candle")["host_id"] == "f_L0_002"
    daylight, _ = DA.apply(b, STYLE, {"answers": {}}, style={"lighting": {"mood": "warm daylight"}})
    assert all(not d.get("light_on") for d in daylight["decor"])
    broken = json.loads(json.dumps(out))
    next(d for d in broken["decor"] if d["type"] == "plant_large")["species"] = "cactus"
    with pytest.raises(Exception):
        B.validate(broken)


def test_brief_words_helpers():
    assert DA.brief_colour(PROFILE, "cushion", 3) == "mustard" and DA.brief_colour(PROFILE, "throw", 0) is None
    assert DA.brief_colour(PROFILE, "blind", 0) == "off white" and DA.brief_colour({}, "rug", 0) is None
    assert DA.plant_look(PROFILE, 4)[:2] == ("monstera", {"material": "rattan", "colour": None})
    assert DA.plant_look({}, 0)[:2] == (None, None)
    assert DA.lamps_on_of(PROFILE) and not DA.lamps_on_of({})


# --------------------------------------------------------------------------
# Partners: twins and same_as rooms get a copy
# --------------------------------------------------------------------------

def _twins(kind: str = "twin") -> dict:
    """Two 6 x 5 m living rooms mirrored about x = 6.1 (a party wall), a sofa against each north wall and a window
    in each south wall; the second room is the first one's twin (or its ``same_as``)."""
    b = room_building(furniture=[("sofa", (2.0, 4.5), 0.0, (2.2, 0.9)), ("table_coffee", (2.0, 3.0), 0.0, (1.0, 0.6))],
                      windows=[("win_a", "s", 2.0, 1.6)])
    mirror = lambda x: 12.2 - x                                               # noqa: E731
    t = 0.2
    for w in [w for w in b["walls"]]:
        if w["id"] == "w_e":
            continue
        b["walls"].append(dict(w, id=w["id"] + "_b", start=[mirror(w["start"][0]), w["start"][1]],
                               end=[mirror(w["end"][0]), w["end"][1]]))
    b["openings"].append(dict(b["openings"][0], id="win_b", wall_id="w_s_b", center=[mirror(2.0), -t / 2]))
    room_b = dict(b["rooms"][0], id="r_b", label="Room B",
                  polygon=[[mirror(x), y] for x, y in reversed(b["rooms"][0]["polygon"])])
    room_b["twin_of" if kind == "twin" else "same_as"] = RID
    b["rooms"].append(room_b)
    for f in list(b["furniture"]):
        g = json.loads(json.dumps(f))
        g.update(id=f["id"] + "_b", room_id="r_b")
        g["footprint"]["center"] = [mirror(f["footprint"]["center"][0]), f["footprint"]["center"][1]]
        b["furniture"].append(g)
    B.validate(b)
    return b


@pytest.mark.parametrize("kind", ["twin", "same_as"])
def test_partners_are_not_asked_and_get_a_mirrored_copy(kind):
    b = _twins(kind)
    if kind == "same_as":                                   # a same_as room maps by identity: a room on another level
        for key in ("walls", "openings"):
            for e in b[key]:
                if e["id"].endswith("_b"):
                    e["level_id"] = "L1"
        b["levels"].append(dict(b["levels"][0], id="L1", label="L1", order=1))
        for f in b["furniture"]:
            if f["id"].endswith("_b"):
                f["level_id"] = "L1"
                f["footprint"]["center"][0] = 12.2 - f["footprint"]["center"][0]
        rb = next(r for r in b["rooms"] if r["id"] == "r_b")
        rb.update(level_id="L1", polygon=b["rooms"][0]["polygon"])
        for o in b["openings"]:
            if o["id"] == "win_b":
                o["center"] = [2.0, -0.1]
        for w in b["walls"]:
            if w["id"].endswith("_b"):
                w["start"][0], w["end"][0] = 12.2 - w["start"][0], 12.2 - w["end"][0]
        B.validate(b)
    targets, notes = D.copy_targets(b)
    assert list(targets) == ["r_b"] and not notes
    assert [q.room["id"] for q in DA.room_questions(b, STYLE)] == [RID]
    out, records = applied(b, choose(("f_L0_001.cushions", "cushion", "sage green"), ("window:win_a", "curtain", "sage green"),
                                     ("f_L0_002.centre", "vase", "terracotta")))
    B.validate(out)
    mine = [d for d in out["decor"] if d["room_id"] == RID]
    copies = [d for d in out["decor"] if d["room_id"] == "r_b"]
    assert copies and len(copies) == len(mine)
    by_src = {d["mirrored_from"]: d for d in copies}
    for d in mine:
        c = by_src[d["id"]]
        if d.get("host_id"):
            assert c["host_id"] == d["host_id"] + "_b"
        if d.get("window_id"):
            assert c["window_id"] == "win_b"
        expect_x = 12.2 - d["center"][0] if kind == "twin" else d["center"][0]
        assert c["center"][0] == pytest.approx(expect_x, abs=1e-3) and c["center"][1] == pytest.approx(d["center"][1])
        assert c["level_id"] == ("L0" if kind == "twin" else "L1") and c["id"] != d["id"]
    rec = next(r for r in records if r.room_id == "r_b")
    assert any(f"copied from {RID}" in n for n in rec.notes)
    rules, rows = D.add_decor(b)                                              # the rules copy the same way
    assert any(d.get("mirrored_from") for d in rules["decor"]) and any("decor copied" in r["note"] for r in rows)


def test_twins_are_asked_themselves_with_twin_rooms_all():
    b = _twins()
    b["project"]["brief"] = {"render": {"twin_rooms": "all"}}
    assert D.partner_rooms(b) == {}
    assert {q.room["id"] for q in DA.room_questions(b, STYLE)} == {RID, "r_b"}
