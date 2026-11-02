"""2 Nov 2026 (house score item 4b, "layered lighting"): a living room's lamps are lit
(wenart/blender/lighting.py, the comment above ``RIG_LAMP_LUMENS``).

The living rig had only an optional dining pendant and an optional kitchen strip; a floor or table lamp gave its own
light (``furniture.LAMP_LIGHTS``) only in the evening mood, so in daylight a living room's lamps were dark props.
These CPU tests pin:

- the living rig has an optional ``lamp`` fixture (800 lm table lamp, 1100 lm floor lamp, x ``RIG_GAIN``);
- every floor and table lamp of a living room (a furniture piece or a built decor lamp) hosts a rig light: no rig
  mesh, the light in or under its shade as a bedside light (``_host_lamps`` / ``_host_light_z``), at the warm
  ``rig_temperature_for`` colour, with the rule in its record and its reason;
- at most ``RIG_LAMP_MAX`` per room, floor lamps first; the others are listed under ``dropped`` with the reason;
- no lamp, no light and no record; bedrooms keep their bedside rule; ``LAMP_LIGHTS`` and the daylight ``light_on``
  stay as they were;
- ``build_room_rig`` records each lamp light like every rig light (stand-in bpy, no Blender).
"""
import sys
import types
from types import SimpleNamespace as NS

import pytest

from wenart.blender import furniture as FU
from wenart.blender import lighting as L
from wenart.blender import parametric as P

LIVING = {"id": "r_liv", "room_type": "living", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]}
DAYLIGHT = {"colour_temperature_k": 5200}


def _piece(pid, ftype, center, size, front=270.0, rot=0.0, room="r_liv", asset=None):
    p = {"id": pid, "type": ftype, "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
         "front_deg": front, "room_id": room}
    if asset is not None:
        p["asset"] = asset
    return p


def _decor(did, dtype, center, size, host=None, method=None, fixture=None):
    d = {"id": did, "type": dtype, "center": list(center), "size": list(size), "rotation_deg": 0.0,
         "host_id": host, "has_light": False, "method": method}
    if fixture:
        d["fixture"] = fixture
    return d


def _lamps(plan):
    return [f for f in plan["fixtures"] if f["kind"] == L.RIG_LAMP_KIND]


def test_living_rig_has_an_optional_lamp_fixture():
    kinds = [f["kind"] for f in L.room_rig("living")]
    assert kinds == ["pendant", "strip", "lamp"] and L.RIG_LAMP_KIND in L.RIG_KINDS
    (spec,) = [f for f in L.room_rig("living") if f["kind"] == "lamp"]
    assert spec["optional"] is True and spec["count"] == L.RIG_LAMP_MAX
    assert spec["lumens"] == L.RIG_LAMP_LUMENS["table_lamp"] == 800.0
    assert spec["lumens_by_type"] == {"table_lamp": 800.0, "floor_lamp": 1100.0}
    assert spec["watts_applied"] == pytest.approx(L.watts_for_lumens(800.0) * L.RIG_GAIN)
    assert L.RIG_LAMP_LUMENS["floor_lamp"] > L.RIG_LAMP_LUMENS["table_lamp"]       # a floor lamp a bit more
    assert 1 <= L.RIG_LAMP_MAX <= 6
    # only living rooms: the other rigs have no lamp kind (bedrooms keep their bedside lamps)
    for room_type in L.ROOM_RIGS:
        if room_type != "living":
            assert "lamp" not in [f["kind"] for f in L.room_rig(room_type)], room_type


def test_floor_and_table_lamps_of_a_living_room_host_a_rig_light():
    """A parametric floor lamp piece and a decor table lamp on a side table: one rig light each, no mesh, the light
    under the closed parametric shade (``_host_light_z``), floor lamp 1100 lm, table lamp 800 lm, warm 2700 K under
    a daylight style; the rule and the reason name item 4b; the fixture check passes."""
    floor = _piece("fl1", "floor_lamp", (0.5, 3.5), (0.45, 0.45))
    side = _piece("st1", "side_table", (5.5, 3.5), (0.5, 0.5))
    top = P.piece_bbox(side)[2]
    table = _decor("dec_tl", "table_lamp", (5.5, 3.5, top + 0.25), (0.3, 0.3, 0.5), host="st1")
    plan = L.rig_plan(LIVING, [floor, side], 0.0, 2.7, lighting=DAYLIGHT, decor=[table])
    lamps = _lamps(plan)
    assert plan["dropped"] == [] and len(lamps) == len(plan["fixtures"]) == 2
    hosts = L._host_lamps([floor, side], [table], 0.0)
    by_host = {f["host_id"]: f for f in lamps}
    assert set(by_host) == {"fl1", "dec_tl"} and [f["host_id"] for f in lamps] == ["fl1", "dec_tl"]
    for f in lamps:
        rec = next(h for h in hosts if h["id"] == f["host_id"])
        assert f["mount"] == "host" and f["mesh"] is False and f["anchor_id"] == f["host_id"]
        assert f["light"]["type"] == "POINT" and f["light"]["center"] == pytest.approx([*rec["xy"], rec["light_z"]])
        assert f["light_where"] == rec["light_where"] == "below_shade"
        assert f["escape_low_z"] == pytest.approx(rec["top"] - (1.0 - L.RIG_ESCAPE_LOW_SHARE) * rec["height"])
        assert f["temperature_k"] == L.rig_temperature_for("living", DAYLIGHT) == 2700.0
        assert f["rule"] == L.RIG_LAMP_RULE and f["reason"].startswith(L.RIG_LAMP_REASON)
        assert "2 Nov 2026, house score item 4b: a living room's lamps are lit" in f["reason"]
        assert f["gain"] == L.RIG_GAIN and f["name"].startswith("rig_r_liv_lamp_")
        assert L._fixture_mesh(f) == ([], []) and L._fixture_hardware(f) == ([], [])
    fl, tl = by_host["fl1"], by_host["dec_tl"]
    assert fl["lumens"] == 1100.0 and fl["watts_radiometric"] == L.watts_for_lumens(1100.0)
    assert fl["light"]["energy_w"] == pytest.approx(L.watts_for_lumens(1100.0) * L.RIG_GAIN)
    assert tl["lumens"] == 800.0 and tl["light"]["energy_w"] == pytest.approx(2.1 * L.RIG_GAIN)
    assert "floor lamp fl1" in fl["reason"] and "table lamp dec_tl on st1" in tl["reason"]
    # never the evening props' wattage (LAMP_LIGHTS: floor 25 W, table 15 W, uncalibrated against the rig)
    assert fl["light"]["energy_w"] != FU.LAMP_LIGHTS["floor_lamp"][0]
    assert tl["light"]["energy_w"] != FU.LAMP_LIGHTS["table_lamp"][0]
    assert L.rig_fixture_problems(plan["fixtures"], LIVING["polygon"], [floor, side], [table], 0.0) == []


def test_a_library_lamp_keeps_its_light_in_the_shade_and_the_agent_factor_scales_it():
    lib = _piece("fl1", "floor_lamp", (0.5, 3.5), (0.45, 0.45),
                 asset={"method": "library", "bbox_m": [0.45, 0.45, 1.6]})
    (f,) = _lamps(L.rig_plan(LIVING, [lib], 0.0, 2.7, piece_methods={"fl1": "library"}))
    assert f["light_where"] == "in_shade" and "in the shade of the floor lamp fl1" in f["reason"]
    assert f["light"]["center"][2] == pytest.approx(1.6 - L.RIG_HOST_LAMP_SHADE_M)
    (g,) = _lamps(L.rig_plan(LIVING, [lib], 0.0, 2.7, piece_methods={"fl1": "library"}, agent_factor=1.5))
    assert g["light"]["energy_w"] == pytest.approx(f["light"]["energy_w"] * 1.5, abs=1e-3)
    # a style warmer than 2700 K (the evening rule) keeps the lamps at its colour
    (h,) = _lamps(L.rig_plan(LIVING, [lib], 0.0, 2.7, lighting={"colour_temperature_k": 2200}))
    assert h["temperature_k"] == 2200.0


def test_lamps_over_the_cap_stay_unlit_and_are_listed_with_the_reason():
    tables = [_decor(f"dec_t{k}", "table_lamp", (1.0 + k * 0.7, 1.0, 0.8), (0.3, 0.3, 0.5)) for k in range(4)]
    floors = [_piece(f"fl{k}", "floor_lamp", (0.5 + k * 1.5, 3.5), (0.4, 0.4)) for k in range(2)]
    plan = L.rig_plan(LIVING, floors, 0.0, 2.7, decor=tables)
    lamps = _lamps(plan)
    assert len(lamps) == L.RIG_LAMP_MAX == 4
    assert [f["host_id"] for f in lamps] == ["fl0", "fl1", "dec_t0", "dec_t1"]          # floor lamps first, then id
    assert [d["host_id"] for d in plan["dropped"]] == ["dec_t2", "dec_t3"]
    for d in plan["dropped"]:
        assert d["kind"] == "lamp" and d["rule"] == L.RIG_LAMP_RULE
        assert d["reason"].startswith(L.RIG_LAMP_REASON) and "at most 4 per room" in d["reason"]
        assert "stays unlit" in d["reason"] and "r_liv" in d["reason"]


def test_no_lamp_no_light_no_record_and_a_dining_pendant_is_no_lamp():
    assert L.rig_plan(LIVING, [], 0.0, 2.7) == {"fixtures": [], "dropped": []}
    sofa = _piece("so1", "sofa", (3.0, 3.5), (2.2, 0.9))
    assert L.rig_plan(LIVING, [sofa], 0.0, 2.7) == {"fixtures": [], "dropped": []}
    # the dining pendant of an open living room keeps its own branch; the floor lamp gets the lamp light
    table = _piece("t1", "table_dining", (3.0, 1.5), (1.6, 0.9))
    floor = _piece("fl1", "floor_lamp", (0.5, 3.5), (0.45, 0.45))
    plan = L.rig_plan(LIVING, [table, floor], 0.0, 2.7)
    assert [f["kind"] for f in plan["fixtures"]] == ["pendant", "lamp"]
    assert plan["fixtures"][1]["host_id"] == "fl1" and plan["dropped"] == []


def test_bedroom_lamps_keep_the_bedside_rule():
    bedroom = {"id": "r1", "room_type": "bedroom", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    bed = _piece("bed", "bed_double", (2.0, 2.0), (1.8, 2.0), room="r1")
    lamps = [_piece("fl1", "floor_lamp", (0.75, 2.7), (0.45, 0.45), room="r1"),
             _piece("fl2", "floor_lamp", (3.25, 2.7), (0.45, 0.45), room="r1"),
             _piece("fl3", "floor_lamp", (3.6, 0.4), (0.4, 0.4), room="r1")]       # a reading lamp in a corner
    plan = L.rig_plan(bedroom, [bed] + lamps, 0.0, 2.7)
    assert [f["kind"] for f in plan["fixtures"]] == ["bedside", "bedside"]
    assert {f["host_id"] for f in plan["fixtures"]} == {"fl1", "fl2"}


def test_rig_lamp_hosts_takes_floor_and_table_lamps_once_and_skips_taken_ones():
    lamps = [{"id": "t2", "type": "table_lamp"}, {"id": "f1", "type": "floor_lamp"},
             {"id": "p1", "type": "pendant_light"},            # a decor pendant serving as a bedside lamp: no lamp
             {"id": "t1", "type": "table_lamp"}, {"id": "t1", "type": "table_lamp"}, {"id": "f0", "type": "floor_lamp"}]
    lit, left = L.rig_lamp_hosts(lamps, taken={"f0", None}, cap=2)
    assert [x["id"] for x in lit] == ["f1", "t1"] and [x["id"] for x in left] == ["t2"]
    lit, left = L.rig_lamp_hosts(lamps, cap=0)
    assert lit == [] and [x["id"] for x in left] == ["f0", "f1", "t1", "t2"]
    assert L.rig_lamp_hosts([], cap=4) == ([], [])


def test_lamp_lights_and_the_daylight_light_on_rule_are_unchanged():
    """The rig light is separate: the props' own light (LAMP_LIGHTS) still comes only with the evening mood or
    ``light_on``; tests/test_decor_m10.py and tests/test_cabinets.py pin the same from the decor and build side."""
    assert FU.LAMP_LIGHTS["floor_lamp"][0] == 25.0 and FU.LAMP_LIGHTS["table_lamp"][0] == 15.0
    assert FU.decor_lit({"type": "floor_lamp"}, False) is False
    assert FU.decor_lit({"type": "table_lamp", "light_on": False}, True) is False
    assert FU.decor_lit({"type": "table_lamp"}, True) is True
    assert FU.lamps_on({"lighting": {"mood": "warm daylight"}}) is False


# --------------------------------------------------------------------------
# build_room_rig: the lamp lights are recorded like every rig light (stand-in bpy, no Blender)
# --------------------------------------------------------------------------

class _Vec(tuple):
    def __new__(cls, v):
        return super().__new__(cls, (float(a) for a in v))


class _Ob(dict):
    def __init__(self, name, data):
        super().__init__()
        self.name, self.data, self.type = name, data, "LIGHT"
        self.location = self.rotation_euler = None
        self.visible_camera = True


class _Objects(dict):
    def new(self, name, data):
        self[name] = _Ob(name, data)
        return self[name]


def test_build_room_rig_records_each_lamp_light_with_the_rule(monkeypatch):
    monkeypatch.setitem(sys.modules, "mathutils", types.ModuleType("mathutils"))
    sys.modules["mathutils"].Vector = _Vec
    tables = [_decor(f"dec_t{k}", "table_lamp", (1.0 + k * 0.7, 1.0, 0.8), (0.3, 0.3, 0.5)) for k in range(5)]
    plan = L.rig_plan(LIVING, [], 0.0, 2.7, decor=tables)
    assert len(plan["fixtures"]) == L.RIG_LAMP_MAX and len(plan["dropped"]) == 1
    bpy = NS(data=NS(objects=_Objects(), lights=NS(new=lambda name, kind: NS(name=name, type=kind))),
             context=NS(evaluated_depsgraph_get=lambda: None))
    objs: list = []
    assumed: list = []
    lights = L.build_room_rig(bpy, NS(set_props=lambda ob, **kw: ob.update(kw)), NS(objects=NS(link=lambda ob: None)),
                              objs, assumed, {"id": "r_liv"}, {"id": "L0"}, plan, None)
    assert len(lights) == L.RIG_LAMP_MAX and all(ob["wenart_rig"] == "lamp" for ob in lights)
    assert all(ob.data.energy == pytest.approx(2.1 * L.RIG_GAIN) for ob in lights)
    assert all(ob.data.temperature == 2700.0 for ob in lights)
    entries = [o for o in objs if o["kind"] == "light"]
    assert len(entries) == L.RIG_LAMP_MAX and not [o for o in objs if o["kind"] == "decor"]     # no rig mesh
    for e in entries:
        a = e["assumed"]
        assert a["rig"] == "lamp" and a["mesh"] is False and a["host_id"].startswith("dec_t")
        assert a["lumens"] == 800.0 and a["reason"].startswith(L.RIG_LAMP_REASON)
    rig = [x for x in assumed if x["kind"] == "rig_light"]
    assert len(rig) == L.RIG_LAMP_MAX and all(L.RIG_LAMP_REASON in x["reason"] for x in rig)
    (dropped,) = [x for x in assumed if x["kind"] == "rig_dropped"]
    assert dropped["field"] == "rig_lamp" and "dec_t4" in dropped["reason"]
