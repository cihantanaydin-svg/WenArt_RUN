"""Fix round after P5 (22 Oct 2026; pod P5, real04), track K_ceiling: what hangs from a sloped ceiling and the cameras
under it.

What: CPU tests of
- the 2.0 m rule for decor ceiling lights under a slope (``decor.MIN_LIGHT_BOTTOM_M``): the AI decorator does not
  offer one (``decor_ai.ceiling_items``) and the builder does not build one (``build.decor_under_roof``, now also
  for a light already hung flush under the slope; a light with no height counts as flush);
- the light rig's ceiling fixtures: none whose bottom would be under ``lighting.RIG_CEILING_MIN_BOTTOM_M`` (1.55 m,
  camera height + headroom) and none without a ceiling over it (``lighting.rig_ceiling_holes`` with the slab
  openings of ``build.ceiling_voids``); a dining pendant keeps its 1.5 m bottom;
- the camera search: roof terraces open to the sky (``level["open_rooms"]`` from ``build.prepare``) have no sloped
  ceiling in the model and no headroom filter (``camsearch.sloped_level``); the fallback camera keeps away from decor
  at camera height and keeps its headroom under a slope (``camsearch.fallback_position``); the search sees only the
  decor that is built (``build.camera_building``);
- the lens check on the built scene (``camsearch.lens_clearance``, warning only).
Why: P5's cam_r_L1_banyo_1 stood 1.5 cm over the decor ceiling light dec_L1_011 hung 1.155 m above the floor (3 GPU
tests failed); without that light the rig's own fixture would have hung at 1.21-1.29 m around the same lens; the L0
stair cores' fixtures floated in the slab opening (a white disc in two L1 hall views); both roof terraces got one
view each, framed on the parapet corner (0.23 and 0.25). Every test fails on 29e54d0 (BASE) or on the mutation its
docstring names.
How: small hand-made rooms and the committed real04 building with the agent's 45 degree roof override removed (the
drawn 32.5 degree section roof P5 rendered); P5's three low lights are copied from
runs/20261017-224848-full/results/furniture/real04/building_final.json (the run folder is not in git; the tests that
read it directly skip without it). No Blender.
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

import _m11_room as M
from wenart import geometry as G
from wenart.blender import build as B
from wenart.blender import camsearch as CS
from wenart.blender import geom2d
from wenart.blender import lighting as L
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA

ROOT = Path(__file__).resolve().parents[1]
P5 = ROOT / "runs" / "20261017-224848-full" / "results"

# P5's three decor ceiling lights hung flush under the drawn slope (building_final.json of the P5 run; the fields the
# builder and the camera search read)
P5_LOW_LIGHTS = [
    {"id": "dec_L1_009", "kind": "decor", "type": "ceiling_light", "level_id": "L1", "room_id": "r_L1_koridor_2",
     "center": [13.614, 9.9, 1.716], "size": [0.4, 0.4, 0.12], "rotation_deg": 0.0, "host_id": None},
    {"id": "dec_L1_011", "kind": "decor", "type": "ceiling_light", "level_id": "L1", "room_id": "r_L1_banyo",
     "center": [7.053, 10.867, 1.155], "size": [0.4, 0.4, 0.12], "rotation_deg": 0.0, "host_id": None},
    {"id": "dec_L1_013", "kind": "decor", "type": "ceiling_light", "level_id": "L1", "room_id": "r_L1_banyo_2",
     "center": [10.12, 10.867, 1.155], "size": [0.4, 0.4, 0.12], "rotation_deg": 0.0, "host_id": None},
]


def _real04_drawn_roof(**brief) -> dict:
    """The committed real04 building as P5 built it: the agent's roof override (P3's 45 degree mansard) removed, the
    committed L1 ceiling lights replaced by P5's three; ``prepare`` of it (``brief``: brief values)."""
    b = json.loads((ROOT / "results" / "furniture" / "real04" / "building_final.json").read_text(encoding="utf-8"))
    ((b.get("agent_overrides") or {}).get("exterior") or {}).pop("roof", None)
    b["decor"] = [d for d in b.get("decor") or []
                  if not (d.get("type") == "ceiling_light" and d.get("level_id") == "L1")] + copy.deepcopy(P5_LOW_LIGHTS)
    return B.prepare(b, "base", brief or None)


@pytest.fixture(scope="module")
def real04():
    return _real04_drawn_roof()


def _level(building: dict, level_id: str) -> dict:
    return next(lv for lv in building["levels"] if lv["id"] == level_id)


def _room(building: dict, room_id: str) -> dict:
    return next(r for r in building["rooms"] if r["id"] == room_id)


def _ceiling_at(level, x, y):
    """``build.main``'s ceiling_at: the flat ceiling or the sloped one under it."""
    flat = float(level["elevation"]) + float(level["ceiling_height"])
    return min([flat] + [a * x + b * y + c for a, b, c in level.get("ceiling_planes") or []])


def _rig(prep: dict, room_id: str, decor=()) -> dict:
    """``lighting.rig_plan`` of one room as ``build_lighting`` calls it (holes: the stairs' openings and the slab
    openings above the level)."""
    from wenart.blender.cameras import room_openings
    from wenart.blender.shell import piece_built

    vb = prep["building"]
    room = _room(vb, room_id)
    level = _level(vb, room["level_id"])
    floor_z = float(level["elevation"])
    polygon = [tuple(p[:2]) for p in room["polygon"]]
    room_floor = floor_z + float(room.get("floor_offset_m") or 0.0)
    room_ceil = min(floor_z + float(level["ceiling_height"]), _ceiling_at(level, *G.polygon_centroid(polygon)))
    pieces = [p for p in vb.get("furniture") or [] if p.get("room_id") == room_id and p.get("kind") != "decor"
              and piece_built(p) and p.get("footprint")]
    holes = L.rig_ceiling_holes(L.stair_openings(vb, level), level, B.ceiling_voids(prep["slabs"]))
    return L.rig_plan(room, pieces, room_floor, room_ceil, holes=holes, decor=list(decor),
                      openings=room_openings(room, polygon, vb),
                      ceiling_fn=lambda x, y, _lv=level: _ceiling_at(_lv, x, y))


def _bottom(f: dict) -> float:
    box = L.fixture_box(f)
    return box["center"][2] - box["size"][2] / 2.0


# --------------------------------------------------------------------------
# One rule: the constants
# --------------------------------------------------------------------------

def test_the_light_bounds_are_the_shared_rules():
    """The builder's copy of the decor light bound (Blender's Python has no shapely, so build.py cannot import
    wenart.furniture.decor) equals the decor stage's; the rig's ceiling bound is the camera height plus the headroom
    the camera search keeps under a slope (not the 2.0 m decor rule: real04's L1 hall fixtures hang at 1.94 m)."""
    assert B.MIN_LIGHT_BOTTOM_M == D.MIN_LIGHT_BOTTOM_M == 2.0
    assert L.RIG_CEILING_MIN_BOTTOM_M == pytest.approx(CS.CAMERA_HEIGHT + CS.HEADROOM_M)


# --------------------------------------------------------------------------
# Decor stage: no ceiling light offered under a low slope
# --------------------------------------------------------------------------

def test_the_decorator_offers_no_ceiling_light_whose_bottom_is_under_2_m_under_a_slope():
    """P5: ``ceiling_items`` hung the room-centre light of r_L1_banyo flush under the 1.27 m slope, 1.155 m above
    the floor. Under a 1.4 m slope the centre slot gets no light (and no pendant: no drop) and the note says why;
    under a 2.2 m slope it hangs flush with its bottom at 2.08 m; a flat ceiling is as before."""
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[])
    room = b["rooms"][0]
    ceiling = DA._ceiling(b, room)
    sid = f"ceiling:centre_{room['id']}"
    flat = dict(DA.ceiling_items(room, [], ceiling, building=b))
    assert flat[sid]["ceiling_light"]["center"][2] == pytest.approx(ceiling - DA.CEILING_LIGHT_SIZE[2])
    low = dict(DA.ceiling_items(room, [], ceiling, building=b, planes=[[0.0, 0.0, 1.4]]))
    assert sid not in low
    notes: list = []
    DA.ceiling_items(room, [], ceiling, building=b, planes=[[0.0, 0.0, 1.4]], notes=notes)
    assert len(notes) == 1 and "at the room centre" in notes[0] and "1.28 m above the floor (< 2 m)" in notes[0]
    high = dict(DA.ceiling_items(room, [], ceiling, building=b, planes=[[0.0, 0.0, 2.2]]))
    light = high[sid]["ceiling_light"]
    assert light["center"][2] == pytest.approx(2.2 - DA.CEILING_LIGHT_SIZE[2])
    assert light["center"][2] >= D.MIN_LIGHT_BOTTOM_M and "sloped ceiling 2.20 m" in light["reason"]


def test_room_slots_carry_the_note_of_the_light_left_out(monkeypatch):
    """The slot notes (decor_ai.json 'Places left out') name the light left out under the slope."""
    b = M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[])
    monkeypatch.setattr(D, "ceiling_planes", lambda building, level_id: [[0.0, 0.0, 1.4]])
    slots, notes = DA.room_slots(b["rooms"][0], [], b)
    assert not any(s.id.startswith("ceiling:") for s in slots)
    assert any("ceiling light at the room centre" in n and "left out" in n for n in notes)


# --------------------------------------------------------------------------
# Builder: decor_under_roof holds every hostless ceiling light to 2.0 m
# --------------------------------------------------------------------------

def _attic(plane_c: float) -> dict:
    """A level whose sloped ceiling is ``plane_c`` m above its floor everywhere (``furniture.ceiling_above``)."""
    return {"id": "L1", "elevation": 0.0, "ceiling_height": 2.7, "ceiling_planes": [[0.0, 0.0, plane_c]]}


def _light(did: str, center) -> dict:
    return {"id": did, "type": "ceiling_light", "level_id": "L1", "room_id": "r1", "center": list(center),
            "size": [0.4, 0.4, 0.12], "rotation_deg": 0.0, "host_id": None}


def test_a_light_hung_flush_under_a_low_slope_is_not_built():
    """BASE kept a light whose given height fits under the slope at any height (the 2.0 m check ran only for a
    light reaching over the ceiling)."""
    level = _attic(1.27)
    flush = _light("dec_a", (1.0, 1.0, 1.15))                       # P5's dec_L1_011: fits, bottom 1.15 m
    over = _light("dec_b", (2.0, 1.0, 2.33))                        # the M11 case: reaches over the ceiling
    kept, warnings, not_built = B.decor_under_roof({"decor": [flush, over]}, level)
    assert kept == [] and [n["id"] for n in not_built] == ["dec_a", "dec_b"]
    assert "its bottom is 1.15 m above the floor (< 2.0 m)" in not_built[0]["reason"]
    assert "its bottom would be 1.15 m above the floor" in not_built[1]["reason"]
    assert all(w.endswith("not built") for w in warnings)


def test_a_light_with_no_height_counts_as_flush_never_as_zero():
    """A light without ``center[2]`` hangs flush (the builder hangs it at ceiling - h): kept under a 2.3 m slope
    (bottom 2.18 m), not built under a 1.4 m one. The verifier's formula with z = 0 would have dropped every one."""
    zless = _light("dec_z", (1.0, 1.0))
    kept, _w, not_built = B.decor_under_roof({"decor": [zless]}, _attic(2.3))
    assert kept == [zless] and not_built == []
    kept, _w, not_built = B.decor_under_roof({"decor": [zless]}, _attic(1.4))
    assert kept == [] and "its bottom would be 1.28 m" in not_built[0]["reason"]


def test_lights_that_keep_2_m_and_hosted_lights_are_kept():
    """Mutation guard (every hostless or hosted ceiling light dropped under a slope): a light whose bottom keeps
    2.0 m and a hosted light are not this rule's."""
    level = _attic(2.45)
    ok = _light("dec_ok", (1.0, 1.0, 2.33))                          # bottom 2.33 m: kept as it is
    hosted = dict(_light("dec_h", (1.0, 1.0, 1.0)), host_id="f_1")  # hosted decor is not this rule's
    kept, warnings, not_built = B.decor_under_roof({"decor": [ok, hosted]}, level)
    assert kept == [ok, hosted] and warnings == [] and not_built == []


def test_p5s_three_low_lights_are_not_built(real04):
    """P5 built dec_L1_009 (hall, bottom 1.716 m), dec_L1_011 and dec_L1_013 (baths, 1.155 m); BASE's
    decor_under_roof kept all three."""
    vb = real04["building"]
    _kept, _w, not_built = B.decor_under_roof(vb, _level(vb, "L1"))
    assert sorted(n["id"] for n in not_built) == ["dec_L1_009", "dec_L1_011", "dec_L1_013"]
    assert all("(< 2.0 m)" in n["reason"] for n in not_built)


@pytest.mark.skipif(not (P5 / "furniture" / "real04" / "building_final.json").is_file(),
                    reason="the P5 run folder is not in git")
def test_p5s_own_building_gives_the_three_lights_not_built():
    b = json.loads((P5 / "furniture" / "real04" / "building_final.json").read_text(encoding="utf-8"))
    vb = B.prepare(b, "base", None)["building"]
    _kept, _w, not_built = B.decor_under_roof(vb, _level(vb, "L1"))
    assert sorted(n["id"] for n in not_built) == ["dec_L1_009", "dec_L1_011", "dec_L1_013"]


# --------------------------------------------------------------------------
# Light rig: no ceiling fixture at eye height, none in a slab opening
# --------------------------------------------------------------------------

BATH = {"id": "r_b", "room_type": "bathroom", "polygon": [[0, 0], [2.4, 0], [2.4, 2.0], [0, 2.0]]}
HALL = {"id": "r_h", "room_type": "hall", "polygon": [[0, 0], [3.0, 0], [3.0, 1.5], [0, 1.5]]}
STAIR = {"id": "r_s", "room_type": "stair", "polygon": [[0, 0], [2.6, 0], [2.6, 2.1], [0, 2.1]]}


def test_a_rig_ceiling_fixture_under_a_low_slope_is_dropped_and_the_fill_light_stays():
    """P5 r_L1_banyo without dec_L1_011: rig_r_L1_banyo_ceiling hung at 1.21-1.29 m around the lens of
    cam_r_L1_banyo_1 (BASE built it). Dropped with the heights in the reason; with no ceiling fixture the rig does
    not replace the room's fill light."""
    plan = L.rig_plan(BATH, [], 0.0, 1.32, ceiling_fn=lambda x, y: 1.32)
    assert [f for f in plan["fixtures"] if f["kind"] == "ceiling"] == []
    (why,) = [d["reason"] for d in plan["dropped"] if d["kind"] == "ceiling"]
    assert "the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m" in why
    assert L.rig_replaces_fill(plan, "room has no window") is False


def test_the_rig_bound_is_camera_height_plus_headroom_not_2_m():
    """Mutation guard (bound 2.0 m): real04's L1 hall fixtures (bottom 1.94 m, 0.69 m over any lens) stay; so does
    one at exactly 1.55 m."""
    (f,) = L.rig_plan(HALL, [], 0.0, 2.05, ceiling_fn=lambda x, y: 2.05)["fixtures"]
    assert f["mount"] == "ceiling" and f["mesh"] and _bottom(f) == pytest.approx(2.05 - L.RIG_MOUNT_GAP_M - 0.08)
    edge = L.RIG_CEILING_MIN_BOTTOM_M + L.RIG_MOUNT_GAP_M + 0.08
    (f,) = L.rig_plan(HALL, [], 0.0, edge, ceiling_fn=lambda x, y: edge)["fixtures"]
    assert _bottom(f) == pytest.approx(L.RIG_CEILING_MIN_BOTTOM_M)


def test_a_dining_pendant_keeps_its_bottom_over_the_table():
    """Mutation guard (the bound applied to pendants): the pendant over the table hangs at 1.5 m by design."""
    dining = {"id": "r_d", "room_type": "dining", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    table = {"id": "t", "type": "table_dining", "room_id": "r_d", "front_deg": 270.0,
             "footprint": {"center": [2.5, 2.0], "size": [1.8, 0.9], "rotation_deg": 0.0}}
    (f,) = L.rig_plan(dining, [table], 0.0, 2.7)["fixtures"]
    assert f["kind"] == "pendant" and f["mesh"] and _bottom(f) == pytest.approx(L.RIG_TABLE_TOP_M
                                                                                + L.RIG_PENDANT_OVER_TABLE_M)


def test_a_ceiling_fixture_needs_a_ceiling_over_it():
    """P5's r_L0_merdiven lies under the slab's opening to L1 over its whole floor; BASE hung its fixture in the void
    (a white disc below the L1 floor in two L1 hall views). A room open above gets no ceiling fixture; with the
    opening over half of it the fixture moves to the half with a ceiling."""
    void = [[-0.02, -0.02], [2.62, -0.02], [2.62, 2.12], [-0.02, 2.12]]
    plan = L.rig_plan(STAIR, [], 0.0, 2.9, holes=[void])
    assert plan["fixtures"] == []
    assert "no ceiling over a fixture in r_s" in plan["dropped"][0]["reason"]
    half = [[-0.02, -0.02], [1.3, -0.02], [1.3, 2.12], [-0.02, 2.12]]
    (f,) = L.rig_plan(STAIR, [], 0.0, 2.9, holes=[half])["fixtures"]
    assert f["center"][0] - 0.15 >= 1.3 - 1e-6


def test_rig_ceiling_holes_add_the_slab_openings_above_the_level():
    stair_hole = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)]
    slab = [[2.0, 2.0, 0.0], [3.0, 2.0, 0.0], [3.0, 3.0, 0.0], [2.0, 3.0, 0.0]]
    holes = L.rig_ceiling_holes([stair_hole], {"id": "L0"}, {"L0": [slab], "L1": [slab]})
    assert holes == [list(stair_hole), [(2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0)]]
    assert L.rig_ceiling_holes([stair_hole], {"id": "L0"}, None) == [list(stair_hole)]
    plans = {"by_level": {"L0": {"above": {"voids": [slab, [[0, 0], [1, 1]]]}}, "L1": {"above": None}}}
    assert B.ceiling_voids(plans) == {"L0": [[[2.0, 2.0], [3.0, 2.0], [3.0, 3.0], [2.0, 3.0]]], "L1": []}
    assert B.ceiling_voids(None) == {}


def test_real04_stair_cores_get_no_fixture_and_the_halls_keep_theirs(real04):
    """real04 with the drawn roof: the L0 stair cores are under the slab opening (no fixture, BASE built one in the
    void); the L1 bathrooms drop theirs (bottom 1.21 m) even without the decor light; the L1 hall keeps its fixture
    at 1.94 m; the L-1 hall beside the stair opening keeps its fixture, off the opening."""
    from shapely.geometry import Point, Polygon

    voids = B.ceiling_voids(real04["slabs"])
    for rid in ("r_L0_merdiven", "r_L0_merdiven_2"):
        poly = Polygon([p[:2] for p in _room(real04["building"], rid)["polygon"]])
        assert sum(poly.intersection(Polygon(v)).area for v in voids["L0"]) > 0.95 * poly.area
        plan = _rig(real04, rid)
        assert [f for f in plan["fixtures"] if f["kind"] == "ceiling"] == []
        assert "no ceiling over a fixture" in plan["dropped"][0]["reason"]
    for rid in ("r_L1_banyo", "r_L1_banyo_2"):
        plan = _rig(real04, rid)
        assert [f for f in plan["fixtures"] if f["kind"] == "ceiling"] == []
        assert any("its bottom would be 1.21 m above the floor" in d["reason"] for d in plan["dropped"])
    (hall,) = _rig(real04, "r_L1_koridor")["fixtures"]
    assert _bottom(hall) - 3.15 == pytest.approx(1.936, abs=2e-3)
    (low,) = _rig(real04, "r_L-1_koridor")["fixtures"]
    assert all(not Polygon(v).buffer(0.15).contains(Point(low["center"][:2])) for v in voids["L-1"])


# --------------------------------------------------------------------------
# Camera search: roof terraces open to the sky, the fallback under a slope
# --------------------------------------------------------------------------

def test_prepare_lists_the_open_rooms_on_each_level(real04):
    assert {lv["id"]: lv["open_rooms"] for lv in real04["building"]["levels"]} == \
        {"L-1": [], "L0": [], "L1": ["r_L1_teras", "r_L1_teras_2"]}
    json.dumps(real04["building"]["levels"])                    # a list, not a set: the level stays JSON


def test_roof_terraces_open_to_the_sky_get_their_views_back(real04):
    """P5 (drawn 32.5 degree roof): the roof's ceiling planes stood 1.13 m over the terrace floors in the camera
    model, only the inner corner passed the headroom filter and each terrace got one view on the parapet corner
    (0.23, 0.25). Now at least 2 views per terrace score over 2 and one of them frames the terrace's table; the ray
    model has no ceiling over them (mutation: the model keeps the planes, the ceiling share is 0.13-0.14 against
    0.02-0.04)."""
    vb = real04["building"]
    level = _level(vb, "L1")
    for rid, table in (("r_L1_teras", "f_L1_040"), ("r_L1_teras_2", "f_L1_037")):
        room = _room(vb, rid)
        assert CS.sloped_level(level, room) is None
        assert CS.RoomModel(room, vb, level).ceiling_planes == []
        plans, _n = CS.plan_room(room, vb, level)
        good = [p for p in plans if p["score"]["total"] > 2.0]
        assert len(good) >= 2, [(p["position"], p["score"]["total"]) for p in plans]
        assert any(table in p["visible_furniture"] for p in good)
        assert all(p["score"]["shares"]["ceiling"] < 0.08 for p in plans)
    assert CS.RoomModel(_room(vb, "r_L1_banyo"), vb, level).ceiling_planes      # a room under the roof keeps them


def test_a_terrace_the_brief_keeps_closed_keeps_its_sloped_ceiling():
    """Mutation guard (keying on room type 'balcony' or on roof.openings): with roof_terraces 'closed' the shell
    builds the sloped ceiling over the terraces, so their camera points keep the headroom filter."""
    prep = _real04_drawn_roof(roof_terraces="closed")
    vb = prep["building"]
    level = _level(vb, "L1")
    assert prep["open_rooms"] == set() and level["open_rooms"] == []
    room = _room(vb, "r_L1_teras")
    assert CS.sloped_level(level, room) is level
    points, _warning = CS.candidate_positions(room, vb)
    assert points and all(CS.headroom_ok(level, p) for p in points)


def _cramped_bath(plane, decor=()) -> tuple[dict, dict]:
    """A 2.4 x 2.0 m bath filled by a low tub (no free camera point) under a ceiling sloping along y."""
    room = {"id": "r_b", "level_id": "L1", "room_type": "bathroom",
            "polygon": [[0.0, 0.0], [2.4, 0.0], [2.4, 2.0], [0.0, 2.0]]}
    tub = {"id": "f_tub", "room_id": "r_b", "level_id": "L1", "type": "bathtub", "source": "from_documents",
           "footprint": {"center": [1.2, 1.0], "size": [1.6, 1.2], "rotation_deg": 0.0}, "height": 0.55}
    level = {"id": "L1", "elevation": 0.0, "ceiling_height": 2.7, "ceiling_planes": [list(plane)] if plane else []}
    b = {"levels": [level], "rooms": [room], "walls": [], "openings": [], "furniture": [tub], "decor": list(decor)}
    return b, room


def test_the_fallback_camera_keeps_away_from_a_low_ceiling_light_and_keeps_its_headroom():
    """P5's cam_r_L1_banyo_1: no free point, so the fallback anchored at the room's inner point, 1.5 cm over the
    ceiling light hung 1.155 m above the floor at that point, with 0.15 m of ceiling over the lens. The light is a
    tall obstacle of the fallback now, and the point passes the search's own headroom rule."""
    light = {"id": "dec_l", "room_id": "r_b", "type": "ceiling_light", "center": [1.2, 1.0, 1.155],
             "size": [0.4, 0.4, 0.12]}
    b, room = _cramped_bath((0.0, -0.6, 2.0), decor=[light])            # 2.0 m at y = 0, 1.4 m at the inner point
    level = b["levels"][0]
    (p,), warning = CS.candidate_positions(room, b)
    assert geom2d.distance_to_rect(p, light["center"][:2], light["size"][:2], 0.0) >= CS.OBSTACLE_CLEARANCE - 1e-9
    assert CS.headroom_ok(level, p) and warning.startswith("no free camera point in the room")
    (q,), why = CS.candidate_positions(room, dict(b, decor=[]))         # without the light: headroom moves it
    x, y, _d = L.polylabel(room["polygon"])
    assert not CS.headroom_ok(level, (x, y)) and CS.headroom_ok(level, q)
    assert "moved to the nearest point with 0.3 m of headroom" in why and math.dist(q, (x, y)) < 0.5


def test_with_no_point_of_headroom_the_fallback_takes_the_most_ceiling():
    b, room = _cramped_bath((0.0, -0.1, 1.5))                           # under 1.55 m everywhere
    level = b["levels"][0]
    (p,), warning = CS.candidate_positions(room, b)
    clear = geom2d.free_points(CS.room_polygon(room), [], wall_clearance=CS.WALL_CLEARANCE,
                               obstacle_clearance=CS.OBSTACLE_CLEARANCE)
    assert CS.ceiling_above_floor(level, p) == pytest.approx(max(CS.ceiling_above_floor(level, q) for q in clear))
    assert "no point with 0.3 m of headroom under the sloped ceiling, moved to the point with the most" in warning


def test_a_flat_room_keeps_its_fallback_point():
    """Mutation guard (the fallback anchored at another point in every room): real02 and real03's fallback rooms
    under flat ceilings keep their cameras (the inner point; simulated on the P4a and P4b buildings: no fallback
    camera of a flat room moves)."""
    b, room = _cramped_bath(None)
    (p,), warning = CS.candidate_positions(room, b)
    x, y, _d = L.polylabel(room["polygon"])
    assert p == (round(x, 9), round(y, 9)) and warning == "no free camera point in the room; camera at the room's " \
                                                            "inner point"


def test_real04_bath_camera_moves_to_headroom_and_the_search_sees_only_built_decor(real04):
    """real04 r_L1_banyo with P5's drawn roof: with dec_L1_011 not built (``camera_building``) the fallback camera
    stands at (7.02, 10.63) with 1.55 m of ceiling (P5: the inner point (7.05, 10.87), 0.15 m over the lens, 1.5 cm
    over the light); with the light still listed the camera keeps 0.2 m from it, at (7.02, 10.43)."""
    vb = real04["building"]
    level = _level(vb, "L1")
    _kept, _w, not_built = B.decor_under_roof(vb, level)
    seen = B.camera_building(vb, not_built)
    assert {d["id"] for d in vb["decor"]} - {d["id"] for d in seen["decor"]} == \
        {"dec_L1_009", "dec_L1_011", "dec_L1_013"}
    assert B.camera_building(vb, []) is vb
    room = _room(vb, "r_L1_banyo")
    (plan,), _n = CS.plan_room(room, seen, level)
    assert plan["position"][:2] == pytest.approx([7.0185, 10.6341], abs=1e-3)
    assert CS.headroom_ok(level, plan["position"][:2]) and not plan["score"]["blocked"]
    (listed,), _n = CS.plan_room(room, vb, level)
    assert listed["position"][:2] == pytest.approx([7.0185, 10.4341], abs=1e-3)


# --------------------------------------------------------------------------
# The lens check on the built scene (warning only)
# --------------------------------------------------------------------------

def _box(name, kind, center, size, rot=0.0):
    return {"name": name, "wenart_id": name, "kind": kind,
            "box3d": {"center": list(center), "size": list(size), "rotation_deg": rot}}


def test_lens_clearance_names_the_box_at_a_searched_lens_and_moves_nothing():
    """P5: cam_r_L1_banyo_1 stood 0.015 m over dec_L1_011 and only the GPU tests saw it."""
    cam = {"name": "cam_b_1", "room_id": "r_b", "kind": "interior", "source": "searched",
           "position": [7.0525, 10.8671, 4.40], "target": [6.0, 10.8671, 4.40]}
    light = _box("dec_L1_011", "decor", (7.053, 10.867, 4.345), (0.34, 0.34, 0.08))
    behind = _box("dec_behind", "decor", (7.20, 10.8671, 4.40), (0.1, 0.1, 0.1))     # 0.10 m behind the lens
    wall = {"name": "w", "kind": "wall"}
    before = copy.deepcopy(cam)
    (hit,) = CS.lens_clearance([cam], [light, behind, wall])
    assert hit["object"] == "dec_L1_011" and hit["distance_m"] == pytest.approx(0.015, abs=1e-3)
    assert "cam_b_1: the lens is 0.015 m from the decor dec_L1_011" in hit["warning"] and cam == before
    assert CS.lens_clearance([cam], [behind]) == []
    for other in ({"source": "replayed"}, {"kind": "exterior"}, {"room_id": None}):
        assert CS.lens_clearance([dict(cam, **other)], [light]) == []
    assert CS.lens_clearance([cam], [_box("far", "furniture", (7.05, 10.867, 4.0), (0.3, 0.3, 0.3))]) == []


@pytest.mark.skipif(not (P5 / "renders" / "real04" / "scene_manifest.json").is_file(),
                    reason="the P5 run folder is not in git")
def test_lens_clearance_on_p5s_scene_lists_only_the_bath_camera():
    m = json.loads((P5 / "renders" / "real04" / "scene_manifest.json").read_text(encoding="utf-8"))
    hits = CS.lens_clearance(m["cameras"], m["objects"])
    assert [(h["camera"], h["object"]) for h in hits] == [("cam_r_L1_banyo_1", "dec_L1_011")]
