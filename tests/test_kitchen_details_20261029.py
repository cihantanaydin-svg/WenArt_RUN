"""The kitchen details of the user's reference photos (29 Oct 2026; lessons UL115, kitchen part, and UL118;
docs/reference_details_20261029.md K1-K15, G3; the user: "look at all these details I want these details", "As much
detail as you can digest", "look at this beautiful kitchen").

The rules are general (every project, by style family: ``wenart.blender.kitchen_details.FAMILY_KITCHEN``); the
synthetic kitchens are the test cases, and real06's kitchen of run 20261029-100801-full (main repository) shows what a
real house gets:

- K1 a tall-unit column (a French-door fridge and an oven tower) at the free end of a counter run, its fronts to the
  ceiling, the ovens out of the hob unit; a window or a corner at the end: no column, an under-counter fridge instead;
- K2 / K15 waterfall ends on an island, G3 knee space for the stools at its back;
- K3 a cylinder hood in a hanging shelf frame over an island hob; K4 fluted handle-less uppers; K7 a pull-down tap in
  the handles' metal; G3 a utensil rail beside the hob, off the windows;
- K5 / G3 the splashback's stone or subway tiles, K11 glossy large tiles on a modern kitchen's floor;
- K6 / K14 the styling sets: one mesh each, inside their real box, placed with the code checks;
- K8 the rig's strip under a wall cabinet beside a hood is no longer dropped;
- the model review's M27 and Argus U31 flag what is left.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import kitchen_details as KD
from wenart.blender import lighting as LI
from wenart.blender import model_review as MR
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.furniture import decor as D
from wenart.furniture import fit as F

ROOT = Path(__file__).resolve().parents[1]
REAL06 = Path("/home/user/WenArt_RUN/runs/20261029-100801-full/results/renders/real06")
ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def kitchen(window=(0.9, 1.0), sill=1.05, island=False, island_stove=False, stools=True, fridge=False,
            length=4.2) -> dict:
    """A 5.0 x 3.5 m kitchen: counter A (4.2 m) on the north wall from the west wall with a drawn sink under the window
    and a drawn 0.75 m stove; optionally an island 2.0 x 0.9 m (its front to the counter) with two stools at its back
    and a drawn stove in it, and a drawn fridge (on the west wall)."""
    pieces = [fp("kA", "kitchen_counter", (length / 2.0, 3.2), (length, 0.6), 270.0, height=0.9),
              fp("sk", "sink_kitchen", (0.9, 3.2), (0.8, 0.5), 270.0),
              fp("st", "stove", (2.0, 3.22), (0.75, 0.55), 270.0)]
    if island:
        pieces.append(fp("iA", "kitchen_island", (2.4, 1.6), (2.0, 0.9), 90.0, height=0.9))
        if stools:
            pieces += [fp("s1", "bar_stool", (2.0, 0.93), (0.42, 0.42), 90.0, height=0.75),
                       fp("s2", "bar_stool", (2.8, 0.93), (0.42, 0.42), 90.0, height=0.75)]
        if island_stove:
            pieces.append(fp("st2", "stove", (2.4, 1.6), (0.6, 0.5), 90.0))
    if fridge:
        pieces.append(fp("fr", "fridge", (0.36, 1.2), (0.7, 0.7), 0.0, height=1.8))
    return M.building(w=5.0, h=3.5, room_type="kitchen", window=window, sill=sill, door_x=1.0, furniture=pieces)


def by_id(b: dict) -> dict:
    return {f["id"]: f for f in b["furniture"]}


def fitted(b: dict, family: str) -> dict:
    """The kitchen runs with their module plans as the fit makes them (``style`` with ``family``): the pre-pass's hints
    and its kitchen details' hints (``fit.run_hints``), the fit's design (the family's kitchen look)."""
    style = {"family": family}
    k = F.kitchen_built_ins(b)
    for p in b["furniture"]:
        if p["type"] in ("kitchen_counter", "kitchen_island"):
            hints = F.run_hints(k, p["id"]) or {}
            design = F.design_of(p, style)
            plan = MOD.plan_kitchen_run(dict(p, module_hints=hints, design=design), style)
            p["asset"] = {"method": "module", "module_plan": plan, "module_hints": hints, "style_family": family,
                          "asset_id": f"module:{p['type']}:kitchen_run"}
    return b


def plan_of(b: dict, pid: str) -> dict:
    return by_id(b)[pid]["asset"]["module_plan"]


# --------------------------------------------------------------------------
# The family table
# --------------------------------------------------------------------------

def test_every_family_has_one_row_of_kitchen_details_with_its_reason():
    keys = {"upper_fronts", "upper_handleless", "waterfall", "island_hood", "hood_metal", "shelf_frame", "splashback",
            "tall_column", "floor", "rail", "styling", "why"}
    from wenart.style import vocabulary as V
    families = {f for f, _row in V.STYLE_FAMILIES}
    assert families <= set(KD.FAMILY_KITCHEN)
    for fam, row in KD.FAMILY_KITCHEN.items():
        assert keys <= set(row), fam
        assert row["splashback"] in KD.SPLASHBACK_KINDS and row["island_hood"] in KD.ISLAND_HOODS
        assert set(row["styling"]) <= set(KD.STYLING_TYPES) and row["styling"] and len(row["why"].split()) >= 6
        assert row["upper_fronts"] in (None, "fluted") and row["floor"] in (None, KD.FLOOR_TILE_SLUG)
    assert KD.family_rule("unknown family")["family"] == "unknown family"
    assert KD.family_rule(None)["family"] == "default" and KD.family_rule("Modern")["upper_fronts"] == "fluted"
    # no style at all: no family, the plan of before (the 28 Oct tests keep their kitchens)
    assert KD.family_from(None) is None and KD.family_from({}) == "default"
    assert KD.family_from(None, {"family": "industrial"}) == "industrial"
    # K2: the framed-front families have their framed fronts on every cabinet, the island too
    from wenart.blender import looks as LO
    for fam in ("modern classic", "transitional", "farmhouse", "classic", "rustic"):
        assert LO.KITCHEN_FAMILY_LOOKS[fam]["front_style"] == "shaker", fam


# --------------------------------------------------------------------------
# K1 the tall-unit column
# --------------------------------------------------------------------------

def test_a_kitchen_with_room_gets_a_tall_unit_column_to_the_ceiling_and_the_hob_loses_its_oven():
    b = fitted(kitchen(), "modern")
    k = F.kitchen_built_ins(b)
    col = k["details"]["kA"]["column"]
    assert col["end"] == "right" and col["kinds"] == ["fridge_french", "oven_tower"]      # 4.2 m run: a 90 cm fridge
    assert col["top_m"] == pytest.approx(2.7) and "no fridge" in col["why"]
    assert k["details"]["kA"]["oven_in_column"] is True
    assert "column" not in (k["hints"].get("kA") or {})                                  # the old contract stays
    plan = plan_of(b, "kA")
    talls = [m for m in plan["modules"] if m["kind"] == "tall_unit"]
    assert [m["front"] for m in talls] == ["oven_tower", "fridge_french"]                # the fridge at the run's end
    assert all(m.get("column") for m in talls)
    top = max(m["z_m"] + m["size_m"][2] for m in talls)
    assert top == pytest.approx(2.69, abs=1e-3)                                          # fronts to the ceiling
    assert talls[-1]["pos_m"][0] + talls[-1]["size_m"][0] / 2.0 == pytest.approx(2.1)    # flush at the run's end
    hob = next(m for m in plan["modules"] if m.get("holds") == "hob")
    assert hob["front"] == "drawers" and "tall unit" in hob["product"]                    # the ovens in the tower
    # the worktop and the plinth stop at the column's side
    col_x0 = min(m["pos_m"][0] - m["size_m"][0] / 2.0 for m in talls)
    for m in plan["modules"]:
        if m["kind"] in ("worktop", "plinth"):
            assert m["pos_m"][0] + m["size_m"][0] / 2.0 <= col_x0 + 1e-6
    det = plan["details"]
    assert det["family"] == "modern" and det["column_top_m"] == pytest.approx(2.69)
    assert [a["what"] for a in det["applied"] if a["detail"] == "K1"] == ["oven_tower", "fridge_french"]
    assert all(a["source"] == "inferred" and a["reason"] for a in det["applied"])
    parts = MOD.module_parts(plan)
    roles = [p["role"] for p in parts]
    assert roles.count("window") >= 2 and roles.count("knob") >= 4                       # two ovens with knobs
    zs = [v[2] for p in parts if p["role"] in ("front", "body") for v in p["verts"]]
    assert max(zs) <= 2.69 + 1e-6
    rec = MOD.module_record(plan)
    assert rec["details"]["column_top_m"] == pytest.approx(2.69)
    # the completion's wall cabinets stop at the column (complete.wall_cabinets_for blocks its rectangles)
    rects = KD.tall_unit_rects(by_id(b)["kA"])
    assert len(rects) == 2 and all(r[1][1] == pytest.approx(0.6) for r in rects)
    assert min(r[0][0] - r[1][0] / 2.0 for r in rects) == pytest.approx(2.7, abs=1e-3)


def test_no_column_in_front_of_a_window_or_at_a_corner_an_under_counter_fridge_instead():
    b = kitchen(window=(3.6, 1.0), sill=1.05)          # a window behind the run's free end
    k = F.kitchen_built_ins(b)
    det = k["details"].get("kA") or {}
    assert "column" not in det
    assert det.get("fridge_x_m") is not None and "no fridge" in det["fridge_why"]
    plan = MOD.plan_kitchen_run(dict(by_id(b)["kA"], module_hints=F.run_hints(k, "kA")), {"family": "modern"})
    fridge = [m for m in plan["modules"] if m.get("holds") == "fridge"]
    assert len(fridge) == 1 and fridge[0]["front"] == "fridge" and fridge[0]["kind"] == "base_unit"
    assert any(a["what"] == "under-counter fridge" for a in plan["details"]["applied"])
    # a kitchen with its own fridge gets the oven tower only
    k2 = F.kitchen_built_ins(kitchen(fridge=True))
    assert k2["details"]["kA"]["column"]["kinds"] == ["oven_tower"]
    assert "fridge_x_m" not in k2["details"]["kA"]
    # without a style the plan ignores the column and keeps the oven under the hob (the plan of before)
    b3 = kitchen()
    k3 = F.kitchen_built_ins(b3)
    plain = MOD.plan_kitchen_run(dict(by_id(b3)["kA"], module_hints=F.run_hints(k3, "kA")))
    assert not [m for m in plain["modules"] if m["kind"] == "tall_unit"] and "details" not in plain
    assert next(m for m in plain["modules"] if m.get("holds") == "hob")["front"] == "oven"


def test_run_end_kinds_wall_open_and_corner():
    b = kitchen()
    run = by_id(b)["kA"]
    assert F.run_end_kind(b, run, [run], "left") == "wall" and F.run_end_kind(b, run, [run], "right") == "open"
    other = fp("kB", "kitchen_counter", (4.5, 2.3), (1.8, 0.6), 180.0)     # an L: kB meets kA's right end
    assert F.run_end_kind(b, run, [run, other], "right") == "corner"


# --------------------------------------------------------------------------
# K2 / K15 waterfall ends, G3 knee space, K3 the island hood
# --------------------------------------------------------------------------

def test_an_island_gets_waterfall_ends_and_knee_space_for_the_stools_at_its_back():
    b = fitted(kitchen(island=True), "modern")
    assert F.kitchen_built_ins(b)["details"]["iA"]["seat_side"] == "back"
    plan = plan_of(b, "iA")
    falls = [m for m in plan["modules"] if m["kind"] == "waterfall"]
    assert len(falls) == 2 and all(m["material"] == "worktop" and m["size_m"][1] == pytest.approx(0.9) for m in falls)
    assert falls[0]["size_m"][2] == pytest.approx(0.86)                              # floor up to the worktop
    units = [m for m in plan["modules"] if m["kind"] == "base_unit"]
    assert all(m["size_m"][1] == pytest.approx(0.6) and m["pos_m"][1] == pytest.approx(-0.15) for m in units)
    assert plan["details"]["overhang_m"] == pytest.approx(0.3)
    inner = [m["pos_m"][0] + s * m["size_m"][0] / 2.0 for m in units + [x for x in plan["modules"]
                                                                       if x["kind"] == "filler"] for s in (-1, 1)]
    assert min(inner) >= -1.0 + KD.WATERFALL_T_M - 1e-6 and max(inner) <= 1.0 - KD.WATERFALL_T_M + 1e-6
    parts = MOD.module_parts(plan)
    body_back = max(v[1] for p in parts if p["role"] in ("body", "front", "panel") for v in p["verts"])
    assert body_back <= 0.15 + 1e-6                                                  # the knee space stays free
    assert {"waterfall", "panel"} <= {p["role"] for p in parts}
    # a family without waterfall ends (industrial) keeps the plain island
    plain = plan_of(fitted(kitchen(island=True), "industrial"), "iA")
    assert not [m for m in plain["modules"] if m["kind"] == "waterfall"]


def test_an_island_hob_gets_a_cylinder_hood_in_a_hanging_shelf_frame_with_jars():
    b = fitted(kitchen(island=True, island_stove=True), "modern")
    plan = plan_of(b, "iA")
    hood = plan["hood"]
    assert hood["kind"] == "island" and hood["style"] == "cylinder" and hood["top_m"] == pytest.approx(2.7)
    assert hood["frame"]["z_hi_m"] + KD.SHELF_FRAME["ceiling_clear"] <= 2.7 + 1e-6
    parts = MOD.module_parts(plan)
    roles = [p["role"] for p in parts]
    assert roles.count("jar") == 6 and "rod" in roles and "plume" in roles and "frame" in roles
    assert max(v[2] for p in parts for v in p["verts"]) <= 2.7 + 1e-6             # up to the ceiling, not through
    jar_keys = {p["key"] for p in parts if p["role"] in ("jar", "lid", "contents")}
    assert {"glass", "wood"} <= jar_keys and jar_keys <= set(P.MATERIAL_KEYS)
    assert any(a["detail"] == "K3" for a in plan["details"]["applied"])
    # no overhang with a hob in the island; a classic kitchen keeps the box hood, without a frame
    assert "overhang_m" not in plan["details"]
    classic = plan_of(fitted(kitchen(island=True, island_stove=True), "classic"), "iA")
    assert classic["hood"]["style"] == "box" and "frame" not in classic["hood"]
    # a low ceiling leaves no room for the frame
    low = kitchen(island=True, island_stove=True)
    low["levels"][0]["ceiling_height"] = 2.4
    lp = plan_of(fitted(low, "modern"), "iA")
    assert "frame" not in lp["hood"] and any("no shelf frame" in n for n in lp["notes"])


# --------------------------------------------------------------------------
# K4 fluted uppers, K7 the tap, G3 the rail
# --------------------------------------------------------------------------

def _wall_cabinet(width=1.2):
    return fp("wc", "wall_cabinet", (3.0, 3.325), (width, 0.35), 270.0, height=0.7, mount_bottom_m=1.45)


def test_the_uppers_follow_the_family_fluted_and_handle_less_or_framed_with_handles():
    cab = _wall_cabinet()
    modern = MOD.plan_wall_run(cab, {"family": "modern"})
    parts = MOD.module_parts(modern)
    roles = [p["role"] for p in parts]
    assert roles.count("flute") > 40 and "handle" not in roles                         # push-to-open fluted fronts
    assert modern["details"]["applied"][0]["detail"] == "K4"
    nordic = MOD.module_parts(MOD.plan_wall_run(cab, {"family": "scandinavian"}))
    assert "flute" not in {p["role"] for p in nordic} and "handle" in {p["role"] for p in nordic}
    before = MOD.module_parts(MOD.plan_wall_run(cab))                                  # no style: as before
    assert [p["role"] for p in before] == [p["role"] for p in nordic]
    for p in parts:                                                                    # inside the cabinet's box
        assert all(-0.6 - 1e-6 <= v[0] <= 0.6 + 1e-6 and -0.175 - 1e-6 <= v[1] <= 0.175 + 1e-6 for v in p["verts"])
    # the build's cut at a window of the building as built keeps the family's uppers
    b = kitchen(window=(3.0, 0.5), sill=1.2)
    cut, rec = MOD.clear_windows(dict(cab, asset={"method": "module", "module_plan": modern}), b)
    assert rec["built"] and cut["asset"]["module_plan"]["details"]["family"] == "modern"


def test_the_tap_is_a_pull_down_spray_tap_in_the_handles_metal():
    plan = plan_of(fitted(kitchen(), "modern"), "kA")
    taps = [p for p in MOD.module_parts(plan) if p["role"] == "tap"]
    assert len(taps) >= 10 and {p["key"] for p in taps} == {"handle"}
    top = max(v[2] for p in taps for v in p["verts"])
    assert 0.9 + 0.25 < top <= 0.9 + 0.30 + 1e-9
    head = min(v[2] for p in taps for v in p["verts"] if v[1] < 0.20)
    assert head >= 0.9 + 0.10                                                          # the spray head over the bowl


def test_an_industrial_kitchen_gets_a_utensil_rail_beside_the_hob_off_the_windows():
    b = fitted(kitchen(fridge=True), "industrial")        # the oven tower at the run's free end, the rail before it
    plan = plan_of(b, "kA")
    rail = plan["details"]["rail_m"]
    windows = F.kitchen_built_ins(b)["details"]["kA"]["windows_m"]
    assert all(rail[1] <= w0 or rail[0] >= w1 for w0, w1 in windows)
    hob = next(m for m in plan["modules"] if m.get("holds") == "hob")
    h0, h1 = hob["pos_m"][0] - hob["size_m"][0] / 2.0, hob["pos_m"][0] + hob["size_m"][0] / 2.0
    assert rail[1] <= h0 - KD.RAIL["hob_clear"] + 1e-6 or rail[0] >= h1 + KD.RAIL["hob_clear"] - 1e-6
    assert KD.RAIL["len_min"] - 1e-6 <= rail[1] - rail[0] <= KD.RAIL["len_max"] + 1e-6
    roles = [p["role"] for p in MOD.module_parts(plan)]
    assert roles.count("utensil") >= 4 and "rail" in roles and "hook" in roles
    # a worktop item under the rail that would reach its utensils is blocked (decor and build); a low one is not
    run = by_id(b)["kA"]
    mid = 2.1 + (rail[0] + rail[1]) / 2.0                  # the run's centre is x 2.1 (its frame is the world's)
    item = {"type": "coffee_machine", "center": [mid, 3.2 + 0.3 - 0.19 - 0.04], "size": [0.24, 0.38, 0.35],
            "host_id": "kA"}
    assert "utensil rail" in KD.item_blocked(item, run)
    low = dict(item, size=[0.12, 0.12, 0.10], center=[mid, 3.2 + 0.3 - 0.06 - 0.04])
    assert KD.item_blocked(low, run) is None
    # the ovens stand in the tower: the hob unit holds pot drawers
    hob_unit = next(m for m in plan["modules"] if m.get("holds") == "hob")
    assert hob_unit["front"] == "drawers"


# --------------------------------------------------------------------------
# K5 / G3 the splashback, K11 the floor
# --------------------------------------------------------------------------

def test_the_splashback_and_the_kitchen_floor_follow_the_family():
    assert KD.splashback_look("industrial")["material"] == "tiles_subway"
    assert KD.splashback_look("industrial")["colour"] == "white"
    assert KD.splashback_look("modern", [{"worktop": "stone"}])["material"] == "stone_worktop"
    assert KD.splashback_look("modern", [{"worktop": "wood"}])["material"] == "marble_slab"
    assert KD.splashback_look("scandinavian") is None                                  # the wet walls' tiles
    from wenart.style import vocabulary as V
    for look in (KD.splashback_look("farmhouse"), KD.splashback_look("classic", [{"worktop": "terrazzo"}])):
        assert look["material"] in V.FLAT_COLOURS and look["reason"]
    assert KD.floor_look("modern")["material"] == KD.FLOOR_TILE_SLUG and KD.floor_look("rustic") is None
    assert V.MATERIALS[KD.FLOOR_TILE_SLUG]["wet_safe"] and V.ROUGHNESS[KD.FLOOR_TILE_SLUG] < 0.1
    room = {"room_type": "kitchen"}
    slot, wet = SH.floor_style(room, {"family": "modern", "floor": {"material": "wood_oak_light"}})
    assert slot["material"] == KD.FLOOR_TILE_SLUG and wet
    slot, _wet = SH.floor_style(room, {"family": "modern", "floor": {"material": "terrazzo"}})
    assert slot["material"] == "terrazzo"                                              # the brief's wet-safe floor
    slot, _wet = SH.floor_style(room, {"family": "scandinavian", "floor": {"material": "wood_oak_light"},
                                       "wet_floor": {"material": "tiles_light"}})
    assert slot["material"] == "tiles_light"                                           # the rule of before
    b = fitted(kitchen(), "industrial")
    assert SH.splashback_family_look(b, b["levels"][0], {"family": "industrial"})["material"] == "tiles_subway"


# --------------------------------------------------------------------------
# K6 / K14 the styling sets
# --------------------------------------------------------------------------

def test_the_styling_sets_are_one_mesh_each_inside_their_real_box_in_every_word_table():
    from wenart.polish import prompt as PR
    from wenart.vision_check import prompts as VP
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    enum = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    assert set(KD.STYLING_TYPES) == set(D.STYLING_TYPES) == set(P.STYLING_DECOR_TYPES)
    for t in KD.STYLING_TYPES:
        w, d, h = KD.STYLING_SIZES[t]
        assert D.KITCHEN_DECOR_SIZES[t] == (w, d, h) and P.DECOR_DEFAULT_HEIGHT[t] == pytest.approx(h)
        assert t in enum and t in PR.DECOR_WORDS and len(VP.HINTS[t].split()) >= 3
        assert t in P.SURFACE_DECOR_TYPES and t in P.KITCHEN_DECOR_TYPES and t in D.KITCHEN_DECOR_TYPES
        assert max(w, d, h) <= P.DECOR_MAX_M
        parts = P.decor_parts(t, w, d, h)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= w + 1e-6 and y1 - y0 <= d + 1e-6 and z1 - z0 <= h + 1e-6 and abs(z0) < 1e-9, t
        assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS) and len({p["key"] for p in parts}) >= 2, t
        assert sum(len(p["verts"]) for p in parts) < 1200, t                          # light meshes (UL111)


def _dress(b: dict, family: str) -> list:
    room = b["rooms"][0]
    pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"]]
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"

    items = D.kitchen_worktop_decor(b, room, pieces, new_id)
    return items + D.kitchen_styling_decor(b, room, pieces, new_id, existing=items, family=family)


def test_a_modern_kitchen_is_styled_with_sets_that_pass_the_code_checks():
    b = fitted(kitchen(window=(0.9, 1.0), sill=1.05, island=True, fridge=True, length=4.8), "modern")
    items = _dress(b, "modern")
    sets = [i for i in items if i["type"] in D.STYLING_TYPES]
    types = [i["type"] for i in sets]
    assert len(sets) >= 3 and len(set(types)) == len(types)
    cook = next(i for i in sets if i["type"] == "cookware")
    assert cook["host_id"] == "kA" and cook["center"][0] == pytest.approx(2.0) and cook["size"][0] <= 0.58 + 1e-9
    room = b["rooms"][0]
    pieces = by_id(b)
    for item in sets:
        host = pieces[item["host_id"]]
        assert item["source"] == "added_by_ai" and item["method"] == "rule" and "UL118" in item["reason"]
        assert len(item["size"]) == 3 and item["room_id"] == ROOM
        if item["type"] != "cookware":
            others = [o for o in items if o is not item]
            assert D.worktop_item_ok(item, host, b["furniture"], D.worktop_windows(host, b, room), others) is None
    # the island holds the plates or the dried grass; the jars and the boards stand against the splashback
    assert {i["host_id"] for i in sets if i["type"] in ("cutting_boards", "storage_jars")} <= {"kA"}
    b["decor"] = items
    assert _dress(b, "modern") == []                                                 # dressed once
    # the build rests them on the plan's worktop line, the pot and pan on the hob's rings (no ray per item)
    run = pieces["kA"]
    for item in sets:
        z = KD.worktop_z(item, pieces[item["host_id"]])
        assert z == pytest.approx(0.9 + (0.0065 if item["type"] == "cookware" else 0.0)), item["type"]
    inside = {"type": "kettle", "center": [4.5, 3.2], "size": [0.22, 0.16, 0.25], "host_id": "kA"}
    assert KD.worktop_z(inside, run) is None and "tall unit" in KD.item_blocked(inside, run)


def test_no_tall_set_under_a_wall_cabinet_it_would_reach():
    b = kitchen(window=None)
    b["furniture"].append(fp("wc", "wall_cabinet", (2.1, 3.325), (4.2, 0.35), 270.0, height=0.7, mount_bottom_m=1.40,
                             source="added_by_ai"))
    b = fitted(b, "scandinavian")
    items = _dress(b, "scandinavian")
    vase = [i for i in items if i["type"] == "dried_grass_vase"]
    assert not vase                                                 # 0.55 m under a cabinet 0.50 m over the worktop
    run = by_id(b)["kA"]
    probe = {"type": "dried_grass_vase", "center": [0.25, 3.34], "size": [0.20, 0.20, 0.55], "rotation_deg": 0.0,
             "host_id": "kA"}
    assert "wall cabinet" in D.worktop_item_ok(probe, run, b["furniture"], [], [])
    assert D.wall_cabinet_clear(probe, run, b["furniture"]) == pytest.approx(0.5)


# --------------------------------------------------------------------------
# K8 the strips under the wall cabinets
# --------------------------------------------------------------------------

def test_a_kitchen_run_is_its_worktop_box_and_its_hood_box_for_the_light_rig():
    b = fitted(kitchen(), "scandinavian")
    run = by_id(b)["kA"]
    boxes = KD.run_boxes(run, 0.0)
    assert boxes[0]["size"][2] == pytest.approx(0.9) and len(boxes) >= 2
    hood = next(bx for bx in boxes[1:] if bx["center"][2] - bx["size"][2] / 2.0 > 1.0)    # not the tall units
    assert hood["center"][0] == pytest.approx(2.0, abs=0.01) and hood["center"][2] + hood["size"][2] / 2.0 \
        == pytest.approx(2.7, abs=1e-3)
    # a strip under a wall cabinet beside the hood crosses only the air over the worktop: no problem (before: the
    # run's one box up to the hood's top); one in front of the tall units still crosses them
    strip = {"name": "rig_s", "kind": "strip", "center": [1.0, 3.2, 1.44], "size_m": [1.0, 0.02, 0.015],
             "length_m": 0.6, "rotation_deg": 0.0, "anchor_id": "wc"}
    room = b["rooms"][0]
    got = LI.rig_fixture_problems([strip], room["polygon"], [run], [], 0.0)
    assert not [g for g in got if "crosses" in g["problem"]]
    over_column = dict(strip, center=[3.4, 3.2, 1.44])
    assert [g for g in LI.rig_fixture_problems([over_column], room["polygon"], [run], [], 0.0) if "crosses" in
            g["problem"]]
    assert KD.run_boxes(by_id(b)["sk"], 0.0) is None
    # an open-plan living or dining room with a kitchen run gets the strip (optional: none and no record without one)
    assert any(s["kind"] == "strip" and s.get("optional") for s in LI.room_rig("living"))
    assert any(s["kind"] == "strip" and s.get("optional") for s in LI.room_rig("dining"))


# --------------------------------------------------------------------------
# M27 / U31
# --------------------------------------------------------------------------

def test_model_review_m27_and_argus_u31_flag_what_the_family_rule_gives_a_kitchen():
    assert "M27" in MR.CHECKS and K.CHECK_KIND["M27"] == "taste" and K.CHECK_KIND["U31"] == "taste"
    assert LS.CHECK_LESSONS["U31"] == ("UL115", "UL118") and CS.CHECK_CAUSE["M27"] == "kitchen_design"
    b = fitted(kitchen(island=True, island_stove=True), "modern")
    got, n = KD.review(b, None, "M27")
    assert n == 1 and {g["problem"] for g in got} == {"styling"}                    # the fridge is in the column
    # an island hob whose plan lost its hood, a run planned before the rule, no fridge in the kitchen
    broken = copy.deepcopy(b)
    island = by_id(broken)["iA"]["asset"]["module_plan"]
    island["modules"] = [m for m in island["modules"] if m["kind"] != "hood"]
    run = by_id(broken)["kA"]["asset"]["module_plan"]
    run["modules"] = [m for m in run["modules"] if m["kind"] != "tall_unit"]
    del run["details"]
    got, _n = KD.review(broken, None, "M27")
    probs = {g["problem"]: g for g in got}
    assert probs["island_hood"]["severity"] == "major" and probs["fridge"]["severity"] == "major"
    assert probs["details"]["severity"] == "minor" and probs["fridge"]["lesson"] == "UL118"
    # a strip the rig dropped (the scene manifest)
    manifest = {"lighting": {"rig": {"rooms": {ROOM: {"fixtures": [], "dropped": [
        {"kind": "strip", "name": "rig_x", "reason": "LED strip under the wall cabinet wc: crosses kitchen_counter kA"}]}}}}}
    got, _n = KD.review(b, manifest, "M27")
    assert any(g["problem"] == "led" and g["severity"] == "major" for g in got)
    # the model review and Argus run the same rule
    review = MR.review(b)
    assert review["checks"]["M27"]["checked"] == 1
    assert any(f["check"] == "M27" for f in review.get("findings") or review.get("violations") or [])
    u31 = LS.kitchen_details(broken)
    assert {f["check"] for f in u31} == {"U31"} and all(f["evidence"]["lesson"] in ("UL115", "UL118") for f in u31)
    assert all(f["kind"] == "taste" and f["fix"].startswith("rerun_stage") for f in u31)
    audit = LS.audit(broken)
    assert audit["checked"]["U31"] == len(u31)


def test_the_lessons_are_built():
    data = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in (data["lessons"] if isinstance(data, dict) else data)}
    for lid in ("UL115", "UL118"):
        assert rows[lid]["status"] == "built" and rows[lid]["checks"] == ["build"]
        assert "M27" in rows[lid]["lesson"] and "U31" in rows[lid]["lesson"]
    assert "kitchen part" in rows["UL115"]["lesson"]


# --------------------------------------------------------------------------
# real06's kitchen (run 20261029-100801-full, main repository)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not (REAL06 / "building_built.json").exists(), reason="real06 run 20261029-100801-full not here")
def test_what_real06s_kitchen_gets():
    b = json.loads((REAL06 / "building_built.json").read_text(encoding="utf-8"))
    style = json.loads((REAL06 / "style.json").read_text(encoding="utf-8"))
    family = style.get("family")
    k = F.kitchen_built_ins(b)
    runs = [p for p in b["furniture"] if p["type"] in ("kitchen_counter", "kitchen_island")
            and p.get("build", True) is not False and p.get("asset", {}).get("method") == "module"]
    report = {}
    for p in runs:
        plan = MOD.plan_kitchen_run(dict(p, module_hints=F.run_hints(k, p["id"]) or {}, design=F.design_of(p, style)),
                                    style)
        p["asset"] = dict(p["asset"], module_plan=plan, style_family=family)
        report[p["id"]] = {"type": p["type"], "applied": [(a["detail"], a["what"]) for a in plan["details"]["applied"]],
                           "kinds": sorted({m["kind"] for m in plan["modules"]}), "notes": plan["notes"]}
    room = next(r for r in b["rooms"] if r.get("room_type") == "kitchen" and any(p.get("room_id") == r["id"]
                                                                               for p in runs))
    pieces = [p for p in b["furniture"] if p.get("room_id") == room["id"]]
    b["decor"] = [d for d in b.get("decor") or [] if d.get("room_id") != room["id"]]
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_t{n[0]:03d}"

    items = D.kitchen_worktop_decor(b, room, pieces, new_id)
    sets = D.kitchen_styling_decor(b, room, pieces, new_id, existing=items, family=family)
    print(f"\nreal06 kitchen ({family}): column / fridge / waterfall / knee space per run:")
    for rid, rec in report.items():
        print(f"  {rid} {rec['type']}: {rec['applied']}; modules {rec['kinds']}")
    print("  worktop:", [(i["type"], i["host_id"]) for i in items + sets])
    b["decor"] = list(b["decor"]) + items + sets
    got, _n = KD.review(b, None, "M27")
    print("  M27 left:", [(g["problem"], g["message"][:80]) for g in got])
    # K8: the strip under the wall cabinet beside the hood (dropped in run 100801: "crosses kitchen_counter") stays
    level = next(lv for lv in b["levels"] if lv["id"] == room["level_id"])
    rig = LI.rig_plan(room, [p for p in pieces if p.get("build", True) is not False], 0.0,
                      float(level.get("ceiling_height") or 2.7))
    strips = [f["name"] for f in rig["fixtures"] if f["kind"] == "strip"]
    print("  LED strips:", strips, "dropped:", [d for d in rig["dropped"] if d["kind"] == "strip"])
    cabinets = [p for p in pieces if p["type"] == "wall_cabinet" and p.get("build", True) is not False]
    assert len(strips) == len(cabinets) and not [d for d in rig["dropped"] if d["kind"] == "strip"]
    applied = {rid: {w for _d, w in rec["applied"]} for rid, rec in report.items()}
    islands = [rid for rid, rec in report.items() if rec["type"] == "kitchen_island"]
    assert islands and all({"waterfall ends", "knee space for the stools"} <= applied[i] for i in islands)
    assert any("under-counter fridge" in a or "fridge" in " ".join(a) for a in applied.values())   # a fridge at last
    assert any(i["type"] == "cookware" for i in sets) and all(i["type"] in D.STYLING_TYPES for i in sets)
    assert not [g for g in got if g["severity"] == "major"]
