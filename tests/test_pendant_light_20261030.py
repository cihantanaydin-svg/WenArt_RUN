"""The user's review of real04 run 20261030-043021-full (30 Oct 2026; user rule of 26 Oct 2026: every fix is general):

- UL170, "These 2 lights together not making sense, keep the black one and make it give light": the L0 hall's black
  4-light mesh pendant dec_L0_019 hung 1.41 m from each of the rig's two white flush fixtures and gave no light. A
  decor pendant is its zone's light: the rig hangs no ceiling fixture within ``lighting.PENDANT_ZONE_M`` of its
  footprint, the fixture's light goes into the pendant, shared over its bulbs, warm; every pendant gives light
  (``lighting.pendant_lights``), a library pendant's bulbs glow (``glow``), a parametric pendant's bulb parts glow in
  every mood (``furniture.bulb_glows``); the decor stage hangs no flush light within the same distance of any pendant's
  footprint (``ceiling_lights.clash``).
- The model review's M14 on the same run: six L1 flush lights under the roof slope hung with their top centre 0.04 m
  under the ceiling plane (placed under the slope's lowest point over their box, then tilted about their top). A light
  mounted on a slope has its top centre on the plane over its centre (``furniture.slope_seat``), tilted onto it, and a
  hang record that says so.
CPU only.
"""
from __future__ import annotations

import math

from wenart.blender import furniture as FB
from wenart.blender import geom2d
from wenart.blender import lighting as L
from wenart.furniture import ceiling_lights as CL

HALL = {"id": "r_hall", "room_type": "hall", "polygon": [[0, 0], [1.5, 0], [1.5, 5.06], [0, 5.06]]}


def mesh_pendant(**kw):
    """The run's pendant: a black 4-light mesh pendant (a library model), 0.45 x 0.10 x 0.51 m."""
    d = {"id": "dec_L0_019", "type": "pendant_light", "center": [0.75, 2.53, 2.2557], "size": [0.45, 0.1011, 0.5114],
         "rotation_deg": 0.0, "method": "library", "title": "Stone & Beam Mesh 4-Light Pendant Chandelier, Black",
         "name": "decor_dec_L0_019"}
    d.update(kw)
    return d


def spots_of(plan):
    return [f for f in plan["fixtures"] if f.get("mesh") is not False and f["kind"] == "ceiling"]


def test_a_pendant_replaces_the_rig_ceiling_fixtures_of_its_zone():
    before = L.rig_plan(HALL, [], 0.0, 3.0)
    assert len(spots_of(before)) == 2                            # the long hall's two flush fixtures
    plan = L.rig_plan(HALL, [], 0.0, 3.0, decor=[mesh_pendant()])
    assert spots_of(plan) == []                                  # no flush fixture beside the pendant
    replaced = [d for d in plan["dropped"] if d.get("rule") == L.PENDANT_ZONE_RULE]
    assert len(replaced) == 2 and all(d["replaced_by"] == "dec_L0_019" and d["distance_m"] <= L.PENDANT_ZONE_M
                                      for d in replaced)
    assert all("UL170" in d["reason"] for d in replaced)
    lights = [f for f in plan["fixtures"] if f.get("host_id") == "dec_L0_019"]
    assert len(lights) == 4 and all(f["mount"] == "host" and f["mesh"] is False for f in lights)   # one per bulb
    assert {f["kind"] for f in lights} == {"ceiling"}             # the room's ceiling light, moved into the pendant
    assert math.isclose(sum(f["light"]["energy_w"] for f in lights),
                        sum(f["light"]["energy_w"] for f in before["fixtures"]), rel_tol=1e-6)   # same light
    assert math.isclose(sum(f["lumens"] for f in lights), sum(f["lumens"] for f in spots_of(before)), rel_tol=1e-6)
    assert all(f["temperature_k"] == L.RIG_WARM_K for f in lights)                       # warm bulbs
    xs = sorted(f["light"]["center"][0] for f in lights)
    assert xs[0] > 0.75 - 0.225 and xs[-1] < 0.75 + 0.225 and len(set(xs)) == 4          # along the pendant
    assert all(len(f["glow"]) == 1 for f in lights)                                       # its bulbs glow
    assert L.rig_replaces_fill(plan, "no window")                                         # the fill rule holds


def test_a_far_pendant_leaves_the_fixture_and_still_gives_light():
    far = mesh_pendant(center=[0.75, 4.6, 2.2557])
    plan = L.rig_plan(dict(HALL, polygon=[[0, 0], [1.5, 0], [1.5, 9.0], [0, 9.0]]), [], 0.0, 3.0, decor=[far])
    assert spots_of(plan)                                       # the fixtures beyond 1.5 m stay
    own = [f for f in plan["fixtures"] if f.get("host_id") == far["id"]]
    assert own and sum(f["lumens"] for f in own) >= L.PENDANT_LUMENS - 1e-6


def test_every_pendant_gives_light_and_a_parametric_one_has_no_glow_meshes():
    room = {"id": "r_bed", "room_type": "bedroom", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}
    pend = mesh_pendant(id="dec_p", center=[2.0, 2.0, 2.3], size=[0.45, 0.45, 0.6], method="parametric (fallback)",
                        title="")
    plan = L.rig_plan(room, [], 0.0, 2.8, decor=[pend])
    own = [f for f in plan["fixtures"] if f.get("host_id") == "dec_p"]
    assert len(own) == 1 and own[0]["kind"] == "pendant" and math.isclose(own[0]["lumens"], L.PENDANT_LUMENS)
    assert not own[0].get("glow")                               # its own bulb part glows (furniture.bulb_glows)
    assert FB.bulb_glows("pendant_light", "bulb") and not FB.bulb_glows("pendant_light", "shade")
    assert not FB.bulb_glows("table_lamp", "bulb")              # a lamp keeps the mood's rule


def test_bulb_counts_and_places():
    assert L.pendant_bulb_count({"title": "5-Light Chandelier", "size": [0.5, 0.5, 0.7]}) == 5
    assert L.pendant_bulb_count({"title": "Mesh 4-Light Pendant", "size": [0.45, 0.1, 0.5]}) == 4
    assert L.pendant_bulb_count({"title": "Mid-Century Pendant", "size": [0.4, 0.4, 0.7]}) == 1
    assert L.pendant_bulb_count({"fixture": "linear_pendant", "size": [1.8, 0.08, 1.35]}) == 3
    track = {"fixture": "track_pendants", "size": [2.2, 0.12, 1.3], "track": {"pendants": 2}, "center": [0, 0, 2],
             "rotation_deg": 90.0}
    assert L.pendant_bulb_count(track) == 2
    pts = L.pendant_bulbs(track)                                # along the track, turned with it
    assert len(pts) == 2 and all(abs(x) < 1e-6 for x, _y in pts) and pts[0][1] != pts[1][1]
    boxes = L.built_decor_boxes([{"kind": "decor", "room_id": "r", "type": "pendant_light", "center": [0, 0, 2],
                                  "size": [1, 0.1, 0.5], "decor_id": "d", "track": {"pendants": 3},
                                  "asset": {"title": "4-Light"}}], "r")
    assert boxes[0]["title"] == "4-Light" and boxes[0]["track"] == {"pendants": 3}


def test_the_decor_stage_hangs_no_flush_light_beside_any_pendant():
    row = CL.pendant_foot({"type": "pendant_light", "center": [0.0, 0.0], "size": [1.8, 0.08], "rotation_deg": 0.0})
    # a flush light 1.3 m from a linear pendant's footprint (2.2 m from its centre): beside it
    why = CL.clash((2.2, 0.0), "ceiling_light", False, (0.0, 0.0), "pendant_light", False, foot_q=row)
    assert why and "UL170" in why
    assert CL.clash((2.6, 0.0), "ceiling_light", False, (0.0, 0.0), "pendant_light", False, foot_q=row) is None
    # a counter run's work light stays (a task light)
    assert CL.clash((2.2, 0.0), "ceiling_light", False, (0.0, 0.0), "pendant_light", False, task_p=True,
                    foot_q=row) is None
    assert CL.pendant_foot({"type": "ceiling_light", "center": [0, 0], "size": [0.4, 0.4]}) is None


def test_a_light_on_a_slope_sits_with_its_top_on_the_plane():
    a, b, c = 0.0, 0.199814, 4.606663 - 3.15          # the run's plane over r_L1_oyun (floor at 0 here)
    item = {"type": "ceiling_light", "slope_mount": {"plane": [a, b, c], "tilt_deg": 11.3}}
    assert FB.slope_seated(item, "ceiling_light") and not FB.slope_seated(item, "pendant_light")
    x, y, w, h = 5.56, 4.062, 0.4, 0.12                   # the item box the build measured the slope over
    low = min(geom2d.plane_z((a, b, c), x + sx * w / 2, y + sy * w / 2) for sx in (-1, 1) for sy in (-1, 1))
    verts = [(x + sx * w / 2, y + sy * w / 2, z) for sx in (-1, 1) for sy in (-1, 1) for z in (low - h, low)]
    top_c = geom2d.plane_z((a, b, c), x, y)
    assert top_c - low > 0.03                            # the old seat: the top centre 0.04 m under the plane
    moved, z_above, hang = FB.slope_seat(item, verts, 0.0, low - h, top_c)
    tilted = FB.slope_verts(item, moved)
    tops = sorted(tilted, key=lambda v: -v[2])[:4]
    assert all(abs(v[2] - geom2d.plane_z((a, b, c), v[0], v[1])) < 2e-3 for v in tops)   # the top in the plane
    assert hang["gap_left_m"] == 0.0 and hang["cord_m"] == 0.0 and "sloped ceiling" in hang["how"]
    assert math.isclose(z_above, top_c - h, abs_tol=1e-4)
