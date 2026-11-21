"""21 Nov 2026 (user OK: "Make sense of the building"): RC18, the Turkish building and fire regulations
(``wenart.reading_check.regulations``), on small hand-made buildings (no project data).

What: a five-storey block of two flats a storey around a shared core (hall, stair, lift) that keeps every limit raises
nothing; each rule then raises its finding when one element of that block breaks its limit (a narrow living room, a
bedroom without a window, a small light well, a narrow or steep common stair, no lift, a low storey, a narrow common
hall, a narrow flat door, a tall block with one stair, a flat too deep), and stays quiet where its article exempts the
building (four storeys or fewer for the travel distance, the stair inside one dwelling at 1.00 m).
"""
from __future__ import annotations

import copy

from shapely.geometry import Polygon

from wenart.reading_check import regulations as RG


def rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def mirror(poly):
    return [[20.0 - x, y] for x, y in poly]


def room(rid, label, rtype, poly, lid):
    return {"id": f"r_{lid}_{rid}", "level_id": lid, "label": label, "room_type": rtype, "polygon": poly,
            "area_computed": round(Polygon(poly).area, 3)}


def wall(wid, a, b, lid, exterior=False):
    return {"id": f"w_{lid}_{wid}", "level_id": lid, "start": list(a), "end": list(b), "thickness": 0.2,
            "exterior": exterior}


def door(oid, wid, c, lid, kind="door", width=1.0):
    return {"id": f"{'d' if kind == 'door' else 'win'}_{lid}_{oid}", "type": kind, "level_id": lid,
            "wall_id": f"w_{lid}_{wid}", "center": list(c), "width": width}


def stair(sid, lid, cx=10.0, cy=9.5, width=1.25, spacing=0.28, lines=9, landing=1.4, steps=18):
    return {"id": f"f_{lid}_{sid}", "level_id": lid, "type": "stair", "build": True,
            "footprint": {"center": [cx, cy], "size": [3.6, 4.6], "rotation_deg": 0.0},
            "stair": {"flights": [{"start": [cx - 1.0, cy - 2.2], "end": [cx - 1.0, cy + 0.8], "width": width,
                                   "lines": lines, "spacing": spacing},
                                  {"start": [cx + 1.0, cy + 0.8], "end": [cx + 1.0, cy - 2.2], "width": width,
                                   "lines": lines, "spacing": spacing}],
                      "landing": {"polygon": rect(cx - 1.8, cy + 0.9, cx + 1.8, cy + 0.9 + landing),
                                  "depth": landing},
                      "landing_assumed": False, "turn": "U", "steps_drawn": steps}}


def storey(k: int):
    """Storey ``k`` of the block: 20 x 12 m, flat A west (x 0-8), the core (x 8-12), flat B its mirror east."""
    lid = f"L{k}"
    lv = {"id": lid, "label": f"{k}. Kat", "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7,
          "ceiling_height_source": "section", "floor_to_floor": {"value": 3.0, "method": "vector"}, "kind": "floor"}
    walls = [wall("s", (0, 0), (20, 0), lid, True), wall("e", (20, 0), (20, 12), lid, True),
             wall("n", (20, 12), (0, 12), lid, True), wall("w", (0, 12), (0, 0), lid, True),
             wall("c2", (8, 2), (12, 2), lid), wall("c3", (10, 0), (10, 2), lid), wall("c7", (8, 7), (12, 7), lid)]
    rooms, ops = [], []
    for side, fx in (("a", lambda x: x), ("b", lambda x: 20.0 - x)):
        def pr(p):
            return p if side == "a" else mirror(p)
        walls += [wall(f"{side}55", (fx(5.5), 0), (fx(5.5), 12), lid), wall(f"{side}6", (0 if side == "a" else 20, 6),
                                                                             (fx(5.5), 6), lid),
                  wall(f"{side}3", (fx(5.5), 3), (fx(8), 3), lid), wall(f"{side}9", (fx(5.5), 9), (fx(8), 9), lid),
                  wall(f"{side}8", (fx(8), 0), (fx(8), 12), lid)]
        rooms += [room(f"salon_{side}", "Salon", "living", pr(rect(0.1, 0.1, 5.4, 5.9)), lid),
                  room(f"yatak_{side}", "Yatak Odası", "bedroom", pr(rect(0.1, 6.1, 5.4, 11.9)), lid),
                  room(f"antre_{side}", "Antre", "hall", pr(rect(5.6, 3.1, 7.9, 8.9)), lid),
                  room(f"mutfak_{side}", "Mutfak", "kitchen", pr(rect(5.6, 0.1, 7.9, 2.9)), lid),
                  room(f"banyo_{side}", "Banyo", "bathroom", pr(rect(5.6, 9.1, 7.9, 11.9)), lid)]
        ops += [door(f"{side}1", f"{side}55", (fx(5.5), 4.5), lid), door(f"{side}2", f"{side}55", (fx(5.5), 7.5), lid),
                door(f"{side}3", f"{side}3", (fx(6.75), 3.0), lid), door(f"{side}4", f"{side}9", (fx(6.75), 9.0), lid),
                door(f"{side}5", f"{side}8", (fx(8.0), 5.0), lid),
                door(f"{side}6", "s", (fx(2.75), 0.0), lid, "window", 1.5),
                door(f"{side}7", "n", (fx(2.75), 12.0), lid, "window", 1.5),
                door(f"{side}8", "s", (fx(6.75), 0.0), lid, "window", 1.0)]
    rooms += [room("kat_holu", "Kat Holü", "hall", rect(8.1, 2.1, 11.9, 6.9), lid),
              room("merdiven", "Merdiven", "stair", rect(8.1, 7.1, 11.9, 11.9), lid),
              room("asansor", "Asansör", "shaft", rect(8.1, 0.1, 9.9, 1.9), lid),
              room("saft", "Şaft", "shaft", rect(10.1, 0.1, 11.9, 1.9), lid)]
    ops += [door("c1", "c2", (9.0, 2.0), lid), door("c2", "c7", (10.0, 7.0), lid)]
    return lv, walls, rooms, ops, [stair("001", lid)]


def block(n: int = 5) -> dict:
    b = {"levels": [], "walls": [], "rooms": [], "openings": [], "furniture": [], "slabs": [], "warnings": [],
         "site": {}, "level_inference": {}}
    for k in range(n):
        lv, w, r, o, f = storey(k)
        b["levels"].append(lv)
        b["walls"] += w
        b["rooms"] += r
        b["openings"] += o
        b["furniture"] += f
    return b


def rules(b) -> dict:
    out: dict = {}
    for f in RG.findings(b):
        out.setdefault(f["rule"], []).append(f)
    return out


def _room(b, rid):
    return next(r for r in b["rooms"] if r["id"] == rid)


def _set_poly(b, rid, poly):
    r = _room(b, rid)
    r["polygon"] = poly
    r["area_computed"] = round(Polygon(poly).area, 3)


def test_the_limits_file_carries_two_sources_and_an_article_for_every_limit():
    limits = RG.load_limits()
    assert len(limits) >= 15
    for lid, lim in limits.items():
        assert lim["article"] and lim["quote_tr"] and lim["rule"] in RG.RULES, lid
        assert len(lim["sources"]) >= 2 and all(s.startswith("https://") for s in lim["sources"]), lid


def test_a_block_that_keeps_every_limit_raises_nothing():
    b = block()
    ctx = RG.Context(b, RG.load_limits())
    assert ctx.multi and ctx.residential and ctx.lift and len(ctx.storeys) == 5
    assert all(ctx.common_stair(f"L{k}", f) for k, f in enumerate(b["furniture"]))
    assert len(ctx.flats()) == 10 and all(len(doors) == 1 for _l, _m, doors in ctx.flats())
    assert RG.findings(b) == []


def test_a_narrow_living_room_is_under_the_minimum_and_a_drawn_area_text_marks_a_reading_error():
    b = block()
    _set_poly(b, "r_L0_salon_a", rect(0.1, 3.1, 5.4, 5.9))          # 2.80 m narrow side (min 3.00), its door kept
    found = rules(b)["room_min_size"]
    assert [f["element_ids"] for f in found] == [["r_L0_salon_a"]] and "Madde 29(1)" in found[0]["message"]
    assert not found[0]["reading_suspect"]
    _set_poly(b, "r_L0_salon_a", rect(2.1, 2.6, 5.4, 5.6))          # 9.9 m2, and the drawing says 12.5 m2
    _room(b, "r_L0_salon_a")["area_label"] = 12.5
    f = rules(b)["room_min_size"][0]
    assert f["reading_suspect"] and "12.50" in f["message"]


def test_a_bedroom_without_a_window_and_a_kitchen_without_one_break_the_daylight_rule():
    b = block()
    b["openings"] = [o for o in b["openings"] if o["id"] not in ("win_L0_a7", "win_L0_a8")]
    found = {f["part"]: f for f in rules(b)["light_air"]}
    assert set(found) == {"bedroom", "kitchen"} and "Madde 32(1)" in found["bedroom"]["message"]
    assert found["bedroom"]["element_ids"] == ["r_L0_yatak_a"] and found["kitchen"]["element_ids"] == ["r_L0_mutfak_a"]


def test_a_dwelling_whose_only_living_room_has_no_window_breaks_the_daylight_rule():
    b = block()
    b["openings"] = [o for o in b["openings"] if o["id"] != "win_L1_b6"]
    found = rules(b)["light_air"]
    assert [(f["part"], f["element_ids"]) for f in found] == [("living", ["r_L1_salon_b"])]


def test_a_small_light_well_and_a_small_air_shaft_are_findings_a_large_well_is_not():
    b = block()
    b["rooms"] += [room("isiklik", "Işıklık", "shaft", rect(30, 0, 31.2, 3.0), "L0"),          # 3.6 m2, 1.20 m
                   room("isiklik_2", "Işıklık", "shaft", rect(40, 0, 42.0, 2.5), "L0"),        # 5.0 m2, 2.00 m
                   room("hava", "Hava Bacası", "shaft", rect(50, 0, 50.5, 0.5), "L0")]         # 0.25 m2
    found = rules(b)["light_well_size"]
    assert sorted(f["element_ids"][0] for f in found) == ["r_L0_hava", "r_L0_isiklik"]
    assert {f["limit"] for f in found} == {"paiy32_light_well", "paiy32_air_shaft"}


def test_a_narrow_common_stair_and_its_short_half_landing_are_findings():
    b = block()
    b["furniture"][2] = stair("001", "L2", width=1.10, landing=1.0)
    found = {f["part"] for f in rules(b)["stair_width"]}
    assert found == {"flight", "landing"}


def test_the_stair_inside_one_dwelling_needs_one_metre():
    b = block(1)
    b["rooms"] = [r for r in b["rooms"] if not r["id"].endswith("_b")]                      # one flat: a house
    b["furniture"][0] = stair("001", "L0", width=1.05)
    assert "stair_width" not in rules(b)
    b["furniture"][0] = stair("001", "L0", width=0.90)
    f = rules(b)["stair_width"][0]
    assert "inside the dwelling" in f["message"] and "1.00" in f["message"]


def test_a_shallow_tread_and_a_steep_riser_on_the_common_stair_are_findings():
    b = block()
    b["furniture"][1] = stair("001", "L1", spacing=0.25)
    b["furniture"][3] = stair("001", "L3", steps=14)                 # 3.0 m over 14-15 risers: 0.20-0.21 m
    found = {f["level_id"]: f["message"] for f in rules(b)["stair_steps"]}
    assert set(found) == {"L1", "L3"} and "tread 0.250" in found["L1"] and "riser" in found["L3"]


def test_four_storeys_without_a_lift_need_one():
    b = block(4)
    b["rooms"] = [r for r in b["rooms"] if "asansor" not in r["id"]]
    found = rules(b)["lift_required"]
    assert len(found) == 1 and "Madde 34(1)" in found[0]["message"]
    b3 = block(3)
    b3["rooms"] = [r for r in b3["rooms"] if "asansor" not in r["id"]]
    assert "lift_required" not in rules(b3)


def test_a_low_storey_is_under_the_interior_height():
    b = block()
    b["levels"][1]["ceiling_height"] = 2.50
    b["levels"][2]["ceiling_height"] = 2.30
    found = {f["level_id"]: f["part"] for f in rules(b)["storey_height"]}
    assert found == {"L1": "below_min", "L2": "below_air_obstacle_min"}
    b["levels"][1]["ceiling_height_source"] = "assumed_default"      # no section: nothing to judge
    assert "L1" not in {f["level_id"] for f in rules(b)["storey_height"]}


def test_a_common_hall_narrower_than_an_escape_route_is_a_finding():
    b = block()
    _set_poly(b, "r_L0_kat_holu", rect(8.1, 4.5, 11.9, 5.5))       # 1.00 m wide, both flat doors still on it
    found = rules(b)["corridor_width"]
    assert [f["element_ids"] for f in found] == [["r_L0_kat_holu"]]


def test_a_narrow_flat_door_is_a_finding():
    b = block()
    next(o for o in b["openings"] if o["id"] == "d_L0_a5")["width"] = 0.65
    found = rules(b)["entrance_door_width"]
    assert [f["element_ids"] for f in found] == [["d_L0_a5"]] and "Madde 47(1)" in found[0]["message"]


def test_a_tall_block_with_one_stair_and_no_fire_lobby_breaks_the_escape_rules():
    b = block()
    b["levels"][4]["elevation"] = 22.0
    assert {f["part"] for f in rules(b)["escape_stairs"]} == {"two_stairs"}
    b["levels"][4]["elevation"] = 52.0
    assert {f["part"] for f in rules(b)["escape_stairs"]} == {"two_stairs", "fire_lobby"}
    b["furniture"].append(stair("002", "L3", cy=4.5))                # a second stair on a storey, and a fire lobby
    b["rooms"].append(room("ygh", "Yangın Güvenlik Holü", "hall", rect(8.1, 12.1, 11.9, 13.9), "L3"))
    assert "escape_stairs" not in rules(b)


def test_a_flat_too_deep_for_its_door_is_a_finding_only_over_four_storeys():
    b = block()
    _set_poly(b, "r_L0_yatak_a", rect(-30.0, 6.1, 5.4, 11.9))
    found = rules(b)["travel_distance"]
    assert [f["element_ids"][0] for f in found] == ["r_L0_yatak_a"] and found[0]["distance_m"] > 30
    b4 = copy.deepcopy(b)
    b4["levels"] = b4["levels"][:4]
    b4["rooms"] = [r for r in b4["rooms"] if r["level_id"] != "L4"]
    assert "travel_distance" not in rules(b4)
