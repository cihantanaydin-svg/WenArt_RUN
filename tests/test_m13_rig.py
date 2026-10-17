"""Fix round after P4a (17 Oct 2026): the light rig's fixtures have a host and cross nothing
(wenart/blender/lighting.py; pod P4a rendered real02 with the Milestone 11 cameras replayed).

The look review of P4a found the rig bedside lamps floating beside the beds (a stem ending 22 cm above the floor in
r_L0_yatak_odasi and _3, half in the head wall), standing inside the AI's floor lamps in e_yatak_odasi / _2, and the
bathroom mirror light running across the decor mirrors (r_L1_banyo, r_L0_banyo_2). These CPU tests pin:

- the host order of a bedside lamp: a lamp already there (no rig mesh, the light in its shade), a nightstand (the
  lamp on its top, the stem from the top up), a wall sconce on the head wall (never over a door or a window, never
  past the end of the wall, never through a piece), else no lamp with the reason; no fixture floats;
- the mirror light above the decor mirror or the vanity under it, or dropped under a low ceiling;
- a pendant or ceiling fixture under a built decor light uses it as host; ceiling fixtures follow the sloped
  ceiling at their own spot;
- ``polylabel`` keeps holes beyond the room outside (P4a: r_L0_merdiven's fixture hung in the other stair's
  opening);
- ``rig_fixture_problems`` on hand-made fixtures and on the rig of the committed real01-04 buildings;
- in Blender (skipped without a binary): every shade has ``visible_shadow`` off, so the light inside a closed drum
  reaches the floor (P3/P4a: it never left the drum), and a hosted fixture builds a light and no mesh.
"""
import json
import subprocess
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import cli
from wenart.blender import lighting as L

ROOT = Path(__file__).resolve().parents[1]
BLENDER = cli.find_blender()


def _piece(pid, ftype, center, size, front=270.0, rot=0.0, room="r1", height=None, asset=None):
    p = {"id": pid, "type": ftype, "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
         "front_deg": front, "room_id": room}
    if height is not None:
        p["height"] = height
    if asset is not None:
        p["asset"] = asset
    return p


def _decor(did, dtype, center, size, rot=0.0, host=None):
    return {"id": did, "type": dtype, "center": list(center), "size": list(size), "rotation_deg": rot,
            "host_id": host, "has_light": False}


BEDROOM = {"id": "r1", "room_type": "bedroom", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
BED = _piece("bed", "bed_double", (2.0, 2.0), (1.8, 2.0), front=270.0)      # the head against the +y wall (y = 3)


def _bottom(f):
    box = L.fixture_box(f)
    return box["center"][2] - box["size"][2] / 2.0


# --------------------------------------------------------------------------
# Bedside lamps: a host per side, never the air
# --------------------------------------------------------------------------

def test_bedside_lamp_without_a_nightstand_is_a_wall_sconce_on_the_head_wall():
    """P4a: without a nightstand the lamp stood 0.35 m beside the head corner with its base at 0.60 m and the stem
    ending 22 cm above the floor. Now a sconce: on the head wall (back 5 mm off it), 0.2 m beyond each corner,
    bottom above 0.9 m, no stem, the light in front of the shade; names and anchors as before."""
    plan = L.rig_plan(BEDROOM, [BED], 0.0, 2.7)
    assert [f["name"] for f in plan["fixtures"]] == ["rig_r1_bedside_1", "rig_r1_bedside_2"] and plan["dropped"] == []
    for f in plan["fixtures"]:
        assert f["mount"] == "wall" and f["mesh"] is True and f["anchor_id"] == "bed"
        assert f["size_m"] == list(L.RIG_SCONCE_SIZE_M)
        assert f["center"][2] == pytest.approx(L.RIG_SCONCE_Z_M)
        assert _bottom(f) >= L.RIG_BEDSIDE_MIN_WALL_Z_M
        back = f["center"][1] + L.RIG_SCONCE_SIZE_M[1] / 2.0
        assert 3.0 - back == pytest.approx(L.RIG_SCONCE_WALL_GAP_M, abs=1e-4)          # its back on the wall face
        assert f["light"]["center"][1] < f["center"][1] - L.RIG_SCONCE_SIZE_M[1] / 2.0  # the light in front of it
    xs = sorted(f["center"][0] for f in plan["fixtures"])
    assert xs == pytest.approx([1.1 - L.RIG_SCONCE_BEYOND_M, 2.9 + L.RIG_SCONCE_BEYOND_M])
    assert L.rig_fixture_problems(plan["fixtures"], BEDROOM["polygon"], [BED], [], 0.0) == []
    verts, faces = L._fixture_mesh(plan["fixtures"][0])
    assert len(verts) == 16 and len(faces) == 10                                     # a drum, no stem
    assert min(v[2] for v in verts) == pytest.approx(L.RIG_SCONCE_Z_M - L.RIG_SCONCE_SIZE_M[2] / 2.0)
    assert max(v[1] for v in verts) <= 3.0 - L.RIG_SCONCE_WALL_GAP_M + 1e-6          # nothing in the wall


def test_bedside_light_goes_into_a_floor_lamp_already_beside_the_bed():
    """P4a: e_yatak_odasi / _2 have the AI's floor lamps beside the bed head (f_L0_031..034); the rig lamp stood inside
    them. Now the rig light sits in the lamp's shade (``RIG_HOST_LAMP_SHADE_M`` under its top), no rig mesh, the
    anchor and host the lamp."""
    lamps = [_piece("fl1", "floor_lamp", (0.75, 2.7), (0.45, 0.45)), _piece("fl2", "floor_lamp", (3.25, 2.7),
                                                                                  (0.45, 0.45))]
    plan = L.rig_plan(BEDROOM, [BED] + lamps, 0.0, 2.7)
    assert [f["mount"] for f in plan["fixtures"]] == ["host", "host"] and plan["dropped"] == []
    from wenart.blender.parametric import piece_bbox
    top = piece_bbox(lamps[0])[2]
    for f in plan["fixtures"]:
        assert f["mesh"] is False and f["host_id"] == f["anchor_id"] in ("fl1", "fl2")
        assert f["light"]["center"][2] == pytest.approx(top - L.RIG_HOST_LAMP_SHADE_M)
        assert L._fixture_mesh(f) == ([], [])
    assert {f["host_id"] for f in plan["fixtures"]} == {"fl1", "fl2"}                 # one light per lamp


def test_a_decor_table_lamp_on_the_nightstand_hosts_the_light_and_gets_no_second_lamp():
    """A table lamp of the decor stage on a nightstand comes before the nightstand: the rig never puts its drum next to
    it. The other side keeps its nightstand lamp, standing on the top with the stem from the top up (P3/P4a: the stem
    hung under the base into the nightstand)."""
    stands = [_piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4)), _piece("n2", "nightstand", (3.2, 2.75),
                                                                           (0.45, 0.4))]
    from wenart.blender.parametric import piece_bbox
    top = piece_bbox(stands[0])[2]
    lamp = _decor("dec_lamp", "table_lamp", (0.8, 2.75, top + 0.25), (0.3, 0.3, 0.5), host="n1")
    plan = L.rig_plan(BEDROOM, [BED] + stands, 0.0, 2.7, decor=[lamp])
    by_mount = {f["mount"]: f for f in plan["fixtures"]}
    assert set(by_mount) == {"host", "stand"} and plan["dropped"] == []
    assert by_mount["host"]["host_id"] == "dec_lamp" and by_mount["host"]["mesh"] is False
    stand = by_mount["stand"]
    assert stand["anchor_id"] == stand["host_id"] == "n2"
    assert _bottom(stand) == pytest.approx(top)
    verts, _faces = L._fixture_mesh(stand)
    assert min(v[2] for v in verts) == pytest.approx(top)                            # nothing below its base
    assert L.rig_fixture_problems(plan["fixtures"], BEDROOM["polygon"], [BED] + stands, [lamp], 0.0) == []


def test_bed_away_from_every_wall_gets_no_lamp_and_says_why():
    island = _piece("bed", "bed_double", (2.0, 1.5), (1.6, 2.0), front=270.0, rot=0.0)
    room = dict(BEDROOM, polygon=[[0, 0], [5, 0], [5, 4], [0, 4]])
    plan = L.rig_plan(room, [island], 0.0, 2.7)
    assert plan["fixtures"] == [] and len(plan["dropped"]) == 2
    assert all("not against a wall" in d["reason"] for d in plan["dropped"])


def test_wall_sconce_never_covers_a_window_or_door_nor_runs_past_the_wall_or_through_a_piece():
    window = {"id": "w_head", "type": "window", "center": [0.9, 3.1], "width": 0.5, "height": 1.2, "sill_height": 0.9}
    plan = L.rig_plan(BEDROOM, [BED], 0.0, 2.7, openings=[window])
    assert len(plan["fixtures"]) == 1 and plan["fixtures"][0]["center"][0] == pytest.approx(3.1)
    assert "cover the window w_head" in plan["dropped"][0]["reason"]
    low = {"id": "w_low", "type": "window", "center": [0.9, 3.1], "width": 0.5, "height": 0.3, "sill_height": 1.9}
    assert len(L.rig_plan(BEDROOM, [BED], 0.0, 2.7, openings=[low])["fixtures"]) == 2   # a high window: free
    corner = _piece("bed", "bed_double", (0.9, 2.0), (1.8, 2.0), front=270.0)            # its side on the x = 0 wall
    plan = L.rig_plan(BEDROOM, [corner], 0.0, 2.7)
    assert len(plan["fixtures"]) == 1 and "past the end of the head wall" in plan["dropped"][0]["reason"]
    wardrobe = _piece("wd", "wardrobe", (3.45, 2.7), (1.0, 0.6), front=270.0)
    plan = L.rig_plan(BEDROOM, [BED, wardrobe], 0.0, 2.7)
    assert len(plan["fixtures"]) == 1 and "cross the wardrobe wd" in plan["dropped"][0]["reason"]
    attic = L.rig_plan(BEDROOM, [BED], 0.0, 2.7, ceiling_fn=lambda x, y: 1.3)
    assert attic["fixtures"] == [] and all("reach the ceiling" in d["reason"] for d in attic["dropped"])


# --------------------------------------------------------------------------
# The mirror light above the mirror; hosts under decor lights; the slope
# --------------------------------------------------------------------------

BATH = {"id": "r1", "room_type": "bathroom", "polygon": [[0, 0], [2.5, 0], [2.5, 2], [0, 2]]}
BASIN = _piece("b", "washbasin", (1.0, 1.75), (0.6, 0.5), front=270.0)


def test_mirror_light_sits_above_the_decor_mirror_or_is_dropped_under_a_low_ceiling():
    """P4a: the bar at 1.95 m ran across the diamond mirror dec_L1_010 (r_L1_banyo) and the top of dec_L0_017
    (r_L0_banyo_2, top 1.95 m). Now above the top of the mirror under it, or dropped with the reason."""
    plain = L.rig_plan(BATH, [BASIN], 0.0, 2.5)["fixtures"][0]
    assert plain["kind"] == "mirror" and plain["center"][2] == pytest.approx(L.RIG_MIRROR_LIGHT_Z_M)
    mirror = _decor("dec_m", "mirror", (1.0, 1.97, 1.55), (0.6, 0.04, 0.9), rot=180.0)      # top 2.0 m
    bar = L.rig_plan(BATH, [BASIN], 0.0, 2.7, decor=[mirror])["fixtures"][0]
    assert bar["kind"] == "mirror" and _bottom(bar) == pytest.approx(2.0 + L.RIG_MIRROR_LIGHT_GAP_M)
    assert "above the mirror dec_m" in bar["reason"]
    assert not L.boxes_collide(L.fixture_box(bar), mirror)
    plan = L.rig_plan(BATH, [BASIN], 0.0, 2.15, decor=[mirror])
    assert [f["kind"] for f in plan["fixtures"]] == ["ceiling"]
    assert "the mirror dec_m reaches 2.00 m" in plan["dropped"][0]["reason"]
    aside = _decor("dec_art", "wall_art", (2.2, 1.97, 1.55), (0.4, 0.04, 0.9), rot=180.0)   # beside, not under
    assert L.rig_plan(BATH, [BASIN], 0.0, 2.7, decor=[aside])["fixtures"][0]["center"][2] == \
        pytest.approx(L.RIG_MIRROR_LIGHT_Z_M)
    vanity = dict(BASIN, asset={"method": "library", "bbox_m": [0.6, 0.5, 2.05]})          # a basin with its mirror
    bar = L.rig_plan(BATH, [vanity], 0.0, 2.7)["fixtures"][0]
    assert _bottom(bar) == pytest.approx(2.05 + L.RIG_MIRROR_LIGHT_GAP_M)


def test_pendant_and_ceiling_fixture_use_a_built_decor_light_as_host():
    """P4a: the rig drum of r_L-1_salon hung at the decor pendant dec_L-1_002 over the same table, and the bathroom
    rig fixtures at the decor ceiling lights. A built decor light now hosts the rig light (no second mesh); a decor
    pendant hanging through the table (its shade under ``RIG_HOSTED_MIN_Z_M``) hosts nothing."""
    dining = {"id": "r1", "room_type": "dining", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    table = _piece("t", "table_dining", (2.5, 2.0), (1.8, 0.9))
    pendant = _decor("dec_p", "pendant_light", (2.5, 2.0, 1.5 + 0.35), (0.45, 0.45, 0.7))
    (f,) = L.rig_plan(dining, [table], 0.0, 2.7, decor=[pendant])["fixtures"]
    assert f["mesh"] is False and f["host_id"] == "dec_p" and f["anchor_id"] == "t"
    assert f["light"]["center"][2] == pytest.approx(1.5 + L.RIG_HOSTED_PENDANT_MAX_M)
    sunk = _decor("dec_p", "pendant_light", (2.5, 2.0, 0.244 + 0.97), (0.45, 0.45, 1.94))  # through the table (P4a)
    plan = L.rig_plan(dining, [table], 0.0, 2.7, decor=[sunk])
    assert plan["fixtures"] == [] and "crosses pendant_light dec_p" in plan["dropped"][0]["reason"]
    light = _decor("dec_c", "ceiling_light", (1.25, 1.0, 2.5 - 0.06), (0.25, 0.25, 0.12))
    fixtures = L.rig_plan(BATH, [BASIN], 0.0, 2.5, decor=[light])["fixtures"]
    ceiling = next(x for x in fixtures if x["kind"] == "ceiling")
    assert ceiling["mesh"] is False and ceiling["host_id"] == "dec_c"
    assert ceiling["light"]["center"][2] == pytest.approx(2.5 - 0.12 - L.RIG_HOSTED_CEILING_GAP_M)
    assert L.rig_replaces_fill({"fixtures": fixtures}, "room has no window") is True   # still the room's fixture


def test_ceiling_fixtures_hang_under_the_sloped_ceiling_at_their_own_spot():
    hall = {"id": "r1", "room_type": "hall", "polygon": [[0, 0], [3, 0], [3, 1.5], [0, 1.5]]}

    def slope(x, y):
        return 3.0 - 0.2 * x

    (f,) = L.rig_plan(hall, [], 0.0, 2.9, ceiling_fn=slope)["fixtures"]
    r = f["size_m"][0] / 2.0
    expected = min(slope(f["center"][0] + sx * r, f["center"][1]) for sx in (-1, 1)) - L.RIG_MOUNT_GAP_M \
        - f["size_m"][2] / 2.0
    assert f["center"][2] == pytest.approx(expected, abs=1e-3)
    assert f["center"][2] + f["size_m"][2] / 2.0 < slope(f["center"][0], f["center"][1])


def test_polylabel_keeps_holes_beyond_the_room_outside():
    """P4a: real02's r_L0_merdiven got its ceiling fixture at (8.40, 8.24), in the other stair's opening of
    r_L0_merdiven_2 (the even-odd rule counted a hole beyond the room as inside). The real02 L0 geometry."""
    room = [(4.718, 7.594), (7.386, 7.594), (7.386, 9.736), (4.718, 9.736)]
    holes = [[(6.14, 7.59), (6.14, 9.7), (7.42, 9.7), (7.42, 7.59)], [(5.01, 8.74), (5.01, 9.7), (6.14, 9.7),
                                                                       (6.14, 8.74)],
             [(7.76, 7.59), (7.76, 9.7), (8.98, 9.7), (8.98, 8.55), (10.38, 8.55), (10.38, 7.59)]]
    x, y, d = L.polylabel(room, holes=holes)
    assert G.point_in_polygon((x, y), room) and d > 0.3
    assert not any(G.point_in_polygon((x, y), h) for h in holes)
    assert L._signed_distance(8.4, 8.24, room, holes) < 0                 # beyond the room, in a hole: outside
    assert L._signed_distance(5.3, 8.1, room, holes) > 0


# --------------------------------------------------------------------------
# The fixture check
# --------------------------------------------------------------------------

def test_rig_fixture_problems_flags_floating_lamps_crossings_and_bad_mounts():
    stand = _piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4))
    floor_lamp = _piece("fl", "floor_lamp", (3.25, 2.7), (0.45, 0.45))
    base = {"kind": "bedside", "size_m": [0.24, 0.24, 0.42], "anchor_id": "bed", "host_id": None}
    floating = dict(base, name="p4a_floating", center=[3.25, 3.35, 0.81])          # the P4a lamp: no mount
    inside = dict(base, name="in_lamp", mount="wall", center=[3.25, 2.7, 1.15], size_m=list(L.RIG_SCONCE_SIZE_M))
    hovering = dict(base, name="hover", mount="stand", host_id="n1", anchor_id="n1", center=[0.8, 2.75, 0.0])
    from wenart.blender.parametric import piece_bbox
    top = piece_bbox(stand)[2]
    hovering["center"][2] = top + 0.02 + 0.21
    low = dict(base, name="low", mount="wall", center=[1.0, 2.935, 0.6], size_m=list(L.RIG_SCONCE_SIZE_M))
    hosted = dict(base, name="hosted", mesh=False, center=[3.25, 2.7, 1.2])
    problems = L.rig_fixture_problems([floating, inside, hovering, low, hosted], BEDROOM["polygon"],
                                      [BED, stand, floor_lamp], [], 0.0)
    by = {}
    for p in problems:
        by.setdefault(p["name"], []).append(p["problem"])
    assert any("outside the room" in p for p in by["p4a_floating"])
    assert any("no nightstand or wall" in p for p in by["p4a_floating"])
    assert any("crosses floor_lamp fl" in p for p in by["in_lamp"])
    assert any("sconce back" in p for p in by["in_lamp"])
    assert any("not on the top of its nightstand n1" in p for p in by["hover"])
    assert any("sconce bottom" in p for p in by["low"])
    assert by["hosted"] == ["no mesh and no host"]


def test_built_decor_boxes_reads_the_manifest_of_the_room():
    objs = [{"kind": "decor", "type": "mirror", "room_id": "r1", "element_id": "d1", "center": [1, 2, 1.5],
             "size": [0.6, 0.04, 0.9], "rotation_deg": 180.0},
            {"kind": "decor", "type": "rig_mirror", "method": "rig", "room_id": "r1", "name": "rig_x"},
            {"kind": "decor", "type": "cushion", "room_id": "r2", "element_id": "d2", "center": [0, 0, 0.5],
             "size": [0.4, 0.4, 0.1]},
            {"kind": "decor", "type": "table_lamp", "room_id": "r1", "element_id": "d3", "center": [0.5, 0.5],
             "size": [0.3, 0.3, 0.5]},
            {"kind": "furniture", "type": "bed_double", "room_id": "r1", "element_id": "f1", "center": [2, 2, 0.25],
             "size": [1.6, 2.0, 0.5]}]
    (box,) = L.built_decor_boxes(objs, "r1")
    assert box == {"id": "d1", "type": "mirror", "center": [1.0, 2.0, 1.5], "size": [0.6, 0.04, 0.9],
                   "rotation_deg": 180.0, "host_id": None, "has_light": False}


def _committed_rigs(project: str):
    """The rig of every rig room of a committed building, as ``build_lighting`` plans it (no built decor)."""
    from wenart.blender.cameras import room_openings
    from wenart.blender.shell import piece_built
    from wenart.furniture import decor as D

    b = json.loads((ROOT / "results" / "furniture" / project / "building_final.json").read_text(encoding="utf-8"))
    out = []
    for level in b["levels"]:
        floor_z = float(level["elevation"])
        ceil_z = floor_z + float(level["ceiling_height"])
        planes = D.ceiling_planes(b, level["id"])

        def ceiling_fn(x, y, planes=planes, ceil_z=ceil_z):
            return min([ceil_z] + [a * x + bb * y + c for a, bb, c in planes])

        for room in b["rooms"]:
            if room["level_id"] != level["id"] or not L.room_rig(room.get("room_type")):
                continue
            polygon = [tuple(p[:2]) for p in room["polygon"]]
            room_floor = floor_z + float(room.get("floor_offset_m") or 0.0)
            pieces = [p for p in b.get("furniture") or [] if p.get("room_id") == room["id"]
                      and p.get("kind") != "decor" and piece_built(p) and p.get("footprint")]
            plan = L.rig_plan(room, pieces, room_floor, min(ceil_z, ceiling_fn(*G.polygon_centroid(polygon))),
                              holes=L.stair_openings(b, level), openings=room_openings(room, polygon, b),
                              ceiling_fn=ceiling_fn)
            out.append((room, pieces, room_floor, plan))
    return out


@pytest.mark.parametrize("project", ["real01", "real02", "real03", "real04"])
def test_the_rig_of_the_committed_buildings_passes_the_fixture_check(project):
    """Every planned fixture of the committed buildings passes ``rig_fixture_problems``; no bedside lamp floats (its
    bottom under ``RIG_BEDSIDE_MIN_WALL_Z_M`` only on a nightstand top); every fixture with a mesh is in its room."""
    rigs = _committed_rigs(project)
    assert rigs
    bedside = 0
    for room, pieces, floor_z, plan in rigs:
        assert L.rig_fixture_problems(plan["fixtures"], room["polygon"], pieces, [], floor_z) == [], room["id"]
        for f in plan["fixtures"]:
            assert f["mount"] in ("ceiling", "stand", "wall", "host", "cabinet"), f
            if f["kind"] == "bedside":
                bedside += 1
                assert f["mount"] in ("stand", "wall", "host"), f
                if f["mesh"] and f["mount"] != "stand":
                    assert _bottom(f) >= floor_z + L.RIG_BEDSIDE_MIN_WALL_Z_M - 1e-6, f
            if f["mesh"]:
                assert G.point_in_polygon(f["center"][:2], [tuple(p[:2]) for p in room["polygon"]]), f
    assert bedside >= 2


def test_real02_bedrooms_get_sconces_and_the_floor_lamps_host_the_light():
    """real02 (committed building): the beds of r_L0_yatak_odasi_3 and _4 stand against the wall without nightstands
    (P4a: floating lamps, and _4's lamps dropped as 'outside the room'): two sconces each; e_yatak_odasi / _2 light the
    AI's floor lamps f_L0_031..034; r_L0_merdiven's ceiling fixture is in its own room."""
    rigs = {room["id"]: plan for room, _p, _z, plan in _committed_rigs("real02")}
    for rid in ("r_L0_yatak_odasi_3", "r_L0_yatak_odasi_4"):
        assert [f["mount"] for f in rigs[rid]["fixtures"]] == ["wall", "wall"], rigs[rid]
    hosts = {f["host_id"] for rid in ("r_L0_e_yatak_odasi", "r_L0_e_yatak_odasi_2") for f in rigs[rid]["fixtures"]}
    assert hosts == {"f_L0_031", "f_L0_032", "f_L0_033", "f_L0_034"}
    (stair,) = rigs["r_L0_merdiven"]["fixtures"]
    assert stair["center"][0] < 7.386                                       # P4a: x 8.40, in r_L0_merdiven_2


# --------------------------------------------------------------------------
# Blender: shades let their light out; hosted fixtures build no mesh
# --------------------------------------------------------------------------

RIG_SCRIPT = r"""
import bpy, json, sys
sys.path.insert(0, %(root)r)
from wenart.blender import common, lighting as L, materials as M

def floor_light(plan, tag):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 8
    sc.render.resolution_x = sc.render.resolution_y = 24
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.0, 0.0, 0.0)
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(-3, -3, 0), (6, -3, 0), (6, 6, 0), (-3, 6, 0)], [], [[0, 1, 2, 3]])
    sc.collection.objects.link(bpy.data.objects.new("floor", me))
    objs, assumed = [], []
    lights = L.build_room_rig(bpy, common, sc.collection, objs, assumed, {"id": "r1"}, {"id": "L0"}, plan,
                              lambda k: M.fixture_material("rig_fixture_2700K", k))
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = 1.0
    co = bpy.data.objects.new("c", cam); co.location = (0.8, 2.0, 0.3); sc.collection.objects.link(co); sc.camera = co
    sc.render.filepath = %(out)r + f"/floor_{tag}.png"; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    px = list(bpy.data.images.load(sc.render.filepath).pixels)
    lum = sum(px[i] + px[i + 1] + px[i + 2] for i in range(0, len(px), 4)) / (len(px) / 4) / 3
    meshes = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("rig_")]
    return {"lum": lum, "meshes": [o.name for o in meshes], "shadow": [o.visible_shadow for o in meshes],
            "lights": [o.name for o in lights], "entries": [e.get("rig_box") is not None for e in objs
                                                            if e["kind"] == "decor"]}

plan = json.loads(%(plan)r)
on = floor_light(plan, "on")
for f in plan["fixtures"]:
    f["light"]["energy_w"] = 0.0
off = floor_light(plan, "off")
hosted = json.loads(%(hosted)r)
host = floor_light(hosted, "host")
print("RESULT " + json.dumps({"on": on, "off": off, "host": host}))
"""


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_blender_shades_let_their_light_out_and_hosted_fixtures_build_no_mesh(tmp_path):
    """The table lamp's point light sits inside its closed drum shade (top + 0.7 h). P3/P4a: the Emission-only shade
    blocked it (bpy 5.2.2: the floor metered the same with the light on or off). With ``visible_shadow`` off the floor
    under the lamp gets its light; a hosted fixture (``mesh: False``) builds its light and no mesh."""
    stands = [_piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4)), _piece("n2", "nightstand", (3.2, 2.75),
                                                                           (0.45, 0.4))]
    plan = L.rig_plan(BEDROOM, [BED] + stands, 0.0, 2.7)
    plan["fixtures"] = plan["fixtures"][:1]                         # the lamp on n1, over the camera's patch
    plan["fixtures"][0]["light"]["energy_w"] = 5.0
    lamps = [_piece("fl1", "floor_lamp", (0.75, 2.7), (0.45, 0.45))]
    hosted = L.rig_plan(BEDROOM, [BED] + lamps, 0.0, 2.7)
    hosted["fixtures"] = [f for f in hosted["fixtures"] if f["mesh"] is False]
    script = RIG_SCRIPT % {"root": str(ROOT), "out": str(tmp_path), "plan": json.dumps(plan),
                           "hosted": json.dumps(hosted)}
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", script],
                          capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    out = json.loads(next(ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT "))[7:])
    print(f"floor under the table lamp: light on {out['on']['lum']:.5f}, off {out['off']['lum']:.5f}")
    assert out["on"]["meshes"] == ["rig_r1_bedside_1"] and out["on"]["shadow"] == [False]
    assert out["on"]["entries"] == [True]
    assert out["on"]["lum"] > 1.2 * out["off"]["lum"] + 1e-4, out          # the light reaches the floor
    assert out["host"]["meshes"] == [] and out["host"]["lights"] == ["rig_r1_bedside_1_light"]
