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

Fix round after P4b (17 Oct 2026; the review of the P4a fix round and the P4b look review of real03):

- built decor is keyed by its own id with manifest-shaped entries (``element_id`` = the host, ``decor_id`` = the
  item): a plant on the lamp's nightstand is a crossing; the lamp takes a free spot of the top or the side falls
  through to the sconce; a decor lamp hosts the light under its own id (P3 real04 r_L0_yatak_odasi / _2);
- a hosted light reaches the room: under a decor pendant, under the shade of a parametric lamp, in the shade of a
  library lamp only; in Blender a hosted light inside a closed shade (the parametric pendant; a library lamp whose
  closed shade encloses its in-shade spot) meters more floor light on than off;
- the fixture hardware: a pendant's cord and canopy reach the ceiling (also a sloped one), a ceiling fixture's canopy
  fills its gap, a table lamp has a base and a stem; the hardware is slot 1 (not emissive), the shade slot 0.

Pass before P5 (17 Oct 2026; the review of the fix round after P4b): a hosted light the ray check moved down out of
a closed shade is recorded where it is built (``light_where`` ``below_host_surface``, the move in its reason and the
scene's ``rig_light`` entry, ``escape.from_where`` / ``from_z``, an assumed ``rig_light_moved`` entry); on CPU with a
stand-in bpy whose host is a closed box (``test_pass_p5_*``), and in the Blender test's library case.
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
    them. Now the rig light goes into the lamp, no rig mesh, the anchor and host the lamp. Fix round after P4b: in the
    shade (``RIG_HOST_LAMP_SHADE_M`` under its top) only for a library model; under the closed shade of a parametric
    lamp (``RIG_HOST_LAMP_BELOW_SHADE_M``, as ``furniture.lamp_light_point``); the scene manifest's build method wins
    over the asset (a library asset built as the parametric fallback)."""
    from wenart.blender import furniture as FU
    from wenart.blender import parametric as P
    lamps = [_piece("fl1", "floor_lamp", (0.75, 2.7), (0.45, 0.45)), _piece("fl2", "floor_lamp", (3.25, 2.7),
                                                                                  (0.45, 0.45))]
    plan = L.rig_plan(BEDROOM, [BED] + lamps, 0.0, 2.7)
    assert [f["mount"] for f in plan["fixtures"]] == ["host", "host"] and plan["dropped"] == []
    top = P.piece_bbox(lamps[0])[2]
    parts = P.build_parts("floor_lamp", 0.45, 0.45, top)
    below = FU.lamp_light_point("floor_lamp", parts, (0.75, 2.7), 0.0, 0.0)[2]
    shade_bottom = min(v[2] for p in parts if p["role"] == "shade" for v in p["verts"])
    for f in plan["fixtures"]:
        assert f["mesh"] is False and f["host_id"] == f["anchor_id"] in ("fl1", "fl2")
        assert f["light"]["center"][2] == pytest.approx(below) and below < shade_bottom - 0.04
        assert f["light_where"] == "below_shade" and "under the shade of the floor lamp" in f["reason"]
        assert L._fixture_mesh(f) == ([], []) and L._fixture_hardware(f) == ([], [])
    assert {f["host_id"] for f in plan["fixtures"]} == {"fl1", "fl2"}                 # one light per lamp
    library = [dict(p, asset={"method": "library", "bbox_m": [0.45, 0.45, 1.5]}) for p in lamps]
    plan = L.rig_plan(BEDROOM, [BED] + library, 0.0, 2.7)
    for f in plan["fixtures"]:
        assert f["light"]["center"][2] == pytest.approx(1.5 - L.RIG_HOST_LAMP_SHADE_M)
        assert f["light_where"] == "in_shade" and "in the shade of the floor lamp" in f["reason"]
        assert f["escape_low_z"] == pytest.approx(L.RIG_ESCAPE_LOW_SHARE * 1.5)
    fallback = L.rig_plan(BEDROOM, [BED] + library, 0.0, 2.7,
                          piece_methods={"fl1": "parametric (fallback: file missing)", "fl2": "library"})
    where = {f["host_id"]: f["light_where"] for f in fallback["fixtures"]}
    assert where == {"fl1": "below_shade", "fl2": "in_shade"}


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
    verts, faces, slots = L._fixture_geometry(stand)
    assert min(v[2] for v in verts) == pytest.approx(top)                            # nothing below its base
    # fix round after P4b: the base and the stem are the hardware (slot 1, not emissive), the shade is slot 0
    shade_z0 = top + stand["size_m"][2] * L.RIG_STAND_STEM_SHARE
    for f, slot in zip(faces, slots):
        zs = [verts[i][2] for i in f]
        assert (min(zs) >= shade_z0 - 1e-9) if slot == 0 else (max(zs) <= shade_z0 + 1e-9), (slot, zs)
    base = [verts[i] for f, slot in zip(faces, slots) if slot == 1 for i in f if verts[i][2] < top + 1e-9]
    assert base and max(abs(v[0] - stand["center"][0]) for v in base) == pytest.approx(L.RIG_STAND_BASE_R_M)
    assert L.rig_fixture_problems(plan["fixtures"], BEDROOM["polygon"], [BED] + stands, [lamp], 0.0) == []
    # the decor lamp is parametric here (no ``method: library``): its light sits under its closed shade
    host = by_mount["host"]
    assert host["light"]["center"][2] == pytest.approx(top + 0.55 * 0.5 - L.RIG_HOST_LAMP_BELOW_SHADE_M)


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
    # fix round after P4b: under the pendant, never in it (P4a: inside the closed bulb of abo_B07HKCRWJH)
    assert f["light"]["center"][2] == pytest.approx(1.5 - L.RIG_HOSTED_PENDANT_GAP_M)
    assert f["light_where"] == "under_host" and "under the decor pendant dec_p" in f["reason"]
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


DINING = {"id": "r1", "room_type": "dining", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
TABLE = _piece("t", "table_dining", (2.5, 2.0), (1.8, 0.9))


def _hardware_faces(fixture):
    verts, faces, slots = L._fixture_geometry(fixture)
    return verts, [f for f, s in zip(faces, slots) if s == 1], [f for f, s in zip(faces, slots) if s == 0]


def test_pendant_hangs_from_the_ceiling_by_a_cord_and_a_canopy():
    """The P4b look review (refuted fix, the verifier's better fix): all 6 rig pendants of real03's living rooms hung
    as cordless 8-sided drums about 1 m under the 2.67 m ceiling. Now the pendant records ``mount_z`` (the ceiling over
    its canopy) and has a cord from the shade's top to the canopy and a canopy whose top is on the ceiling, as
    hardware (slot 1, not emissive); no emissive face lies above the shade; a sloped ceiling is honoured; the shade
    itself is unchanged (16 vertices, 10 faces)."""
    (f,) = L.rig_plan(DINING, [TABLE], 0.0, 2.67)["fixtures"]
    assert f["mount_z"] == pytest.approx(2.67)
    shade_top = f["center"][2] + f["size_m"][2] / 2.0
    verts, hw, shade = _hardware_faces(f)
    assert len(L._fixture_mesh(f)[0]) == 16 and len(shade) == 10
    hz = [verts[i][2] for face in hw for i in face]
    assert max(hz) == pytest.approx(2.67) and min(hz) == pytest.approx(shade_top)
    assert max(verts[i][2] for face in shade for i in face) == pytest.approx(shade_top)   # nothing glows above it
    cord = [face for face in hw if max(abs(verts[i][0] - f["center"][0]) for i in face) < L.RIG_CORD_M]
    cord_z = [verts[i][2] for face in cord for i in face]
    assert min(cord_z) == pytest.approx(shade_top) and max(cord_z) == pytest.approx(2.67 - L.RIG_CANOPY_H_M)
    canopy = [verts[i] for face in hw for i in face if verts[i][2] > 2.67 - L.RIG_CANOPY_H_M + 1e-6]
    assert max(abs(v[0] - f["center"][0]) for v in canopy) == pytest.approx(L.RIG_CANOPY_R_M)
    box = L.pendant_cord_box(f)
    assert box["size"][2] == pytest.approx(2.67 - shade_top) and box["size"][0] == L.RIG_CORD_M

    def slope(x, y):
        return 3.2 - 0.1 * x

    (g,) = L.rig_plan(DINING, [TABLE], 0.0, 3.2, ceiling_fn=slope)["fixtures"]
    r = L.RIG_CANOPY_R_M
    assert g["mount_z"] == pytest.approx(min(slope(g["center"][0] + sx * r, 0.0) for sx in (-1, 0, 1)), abs=1e-4)
    verts, hw, _shade = _hardware_faces(g)
    assert max(verts[i][2] for face in hw for i in face) == pytest.approx(g["mount_z"])
    assert g["mount_z"] < slope(g["center"][0], g["center"][1]) + 1e-9                  # the canopy meets the slope


def test_ceiling_fixture_has_a_canopy_up_to_the_ceiling_and_no_cord():
    """A ceiling fixture hangs ``RIG_MOUNT_GAP_M`` under the ceiling: its canopy fills that gap (a 3 cm gap is under
    the canopy height plus ``RIG_CORD_MIN_M``, so no cord); a pendant clamped under a low ceiling gets the same."""
    hall = {"id": "r1", "room_type": "hall", "polygon": [[0, 0], [3, 0], [3, 1.5], [0, 1.5]]}
    (f,) = L.rig_plan(hall, [], 0.0, 2.6)["fixtures"]
    top = f["center"][2] + f["size_m"][2] / 2.0
    assert f["mount_z"] == pytest.approx(2.6) and 2.6 - top == pytest.approx(L.RIG_MOUNT_GAP_M)
    verts, hw, _shade = _hardware_faces(f)
    hz = [verts[i][2] for face in hw for i in face]
    assert len(hw) == 10 and min(hz) == pytest.approx(top) and max(hz) == pytest.approx(2.6)     # one prism
    assert L.pendant_cord_box(f) is None
    (low,) = L.rig_plan(DINING, [TABLE], 0.0, 1.66)["fixtures"]               # clamped under an attic's 1.66 m
    verts, hw, _shade = _hardware_faces(low)
    assert len(hw) == 10 and max(verts[i][2] for face in hw for i in face) == pytest.approx(1.66)
    strip_and_sconce = L.rig_plan(BEDROOM, [BED], 0.0, 2.7)["fixtures"]
    assert all(L._fixture_hardware(x) == ([], []) for x in strip_and_sconce)        # a sconce has no hardware


def test_pendant_whose_cord_crosses_built_decor_is_dropped():
    """The cord is checked like the shade (the verifier's optional item 5): a built item hanging between the shade
    and the ceiling over the table (here a decor shelf box) drops the pendant with the reason."""
    shelf = {"id": "dec_s", "type": "sculpture", "center": [2.5, 2.0, 2.3], "size": [0.3, 0.3, 0.1],
             "rotation_deg": 0.0, "host_id": None}
    plan = L.rig_plan(DINING, [TABLE], 0.0, 2.67, decor=[shelf])
    assert plan["fixtures"] == [] and "cord crosses sculpture dec_s" in plan["dropped"][0]["reason"]


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
                   "rotation_deg": 180.0, "host_id": None, "has_light": False, "name": None, "method": None}


def test_built_decor_boxes_key_hosted_decor_by_its_own_id():
    """Fix round after P4b: furniture.py writes hosted decor with ``element_id`` = ``wenart_id`` = the host piece and
    the item's id in ``decor_id``; the box is the item's, its host apart. An older entry without ``decor_id`` whose
    ``element_id`` names its host falls back to its object name, never the host's id."""
    objs = [{"name": "decor_n1_3", "wenart_id": "n1", "element_id": "n1", "decor_id": "dec_7", "host_id": "n1",
             "kind": "decor", "room_id": "r1", "type": "plant_small", "center": [0.8, 2.75, 0.7],
             "size": [0.2, 0.2, 0.26], "method": "library"},
            {"name": "decor_n2_4", "wenart_id": "n2", "element_id": "n2", "host_id": "n2", "kind": "decor",
             "room_id": "r1", "type": "book_set", "center": [3.2, 2.75, 0.6], "size": [0.2, 0.15, 0.05]}]
    boxes = L.built_decor_boxes(objs, "r1")
    assert [(b["id"], b["host_id"], b["name"]) for b in boxes] == [("dec_7", "n1", "decor_n1_3"),
                                                                   ("decor_n2_4", "n2", "decor_n2_4")]
    assert L.host_object_name(objs, "dec_7") == "decor_n1_3" and L.host_object_name(objs, "n1") is None


# P3 real04 r_L0_yatak_odasi in small: the decor stage put a plant at the centre of one nightstand and a table lamp on
# the other, as furniture.py records them in the scene manifest (element_id = the nightstand, decor_id = the item).
STANDS = [_piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4)), _piece("n2", "nightstand", (3.2, 2.75), (0.45, 0.4))]


def _manifest_decor(stand_top):
    return [{"name": "decor_n1_9", "wenart_id": "n1", "element_id": "n1", "decor_id": "dec_plant", "host_id": "n1",
             "kind": "decor", "room_id": "r1", "type": "plant_small", "method": "library", "support": "top",
             "center": [0.8, 2.75, stand_top + 0.13], "size": [0.22, 0.2, 0.26]},
            {"name": "decor_n2_10", "wenart_id": "n2", "element_id": "n2", "decor_id": "dec_lamp", "host_id": "n2",
             "kind": "decor", "room_id": "r1", "type": "table_lamp", "method": "library", "support": "top",
             "center": [3.2, 2.75, stand_top + 0.25], "size": [0.3, 0.3, 0.5]}]


def test_rig_lamp_never_stands_through_decor_on_its_own_nightstand():
    """The review of the P4a fix round (P3 real04 r_L0_yatak_odasi / _2, f_L0_050 / f_L0_054): the rig lamp stood at
    the centre of a nightstand through the plant on it, and nothing flagged it (the decor was keyed by the host's id,
    and the check skipped the host). Now: no rig box crosses the plant; with no free spot on the top that side falls
    through to the wall sconce and the reason names the plant; the lamp side hosts the light under the lamp's own id,
    on its nightstand; the plan's own check finds nothing."""
    from wenart.blender.parametric import piece_bbox
    top = piece_bbox(STANDS[0])[2]
    objs = _manifest_decor(top)
    decor = L.built_decor_boxes(objs, "r1")
    plant = next(d for d in decor if d["type"] == "plant_small")
    plan = L.rig_plan(BEDROOM, [BED] + STANDS, 0.0, 2.7, decor=decor)
    for f in plan["fixtures"]:
        if f["mesh"]:
            assert not L.boxes_collide(L.fixture_box(f), plant), f            # P4a's fix round: through the plant
    by_mount = {f["mount"]: f for f in plan["fixtures"]}
    assert set(by_mount) == {"wall", "host"} and plan["dropped"] == []
    assert "the top of the nightstand n1 is taken by the plant_small dec_plant" in by_mount["wall"]["reason"]
    host = by_mount["host"]
    assert host["host_id"] == host["anchor_id"] == "dec_lamp" and "table lamp dec_lamp on n2" in host["reason"]
    assert host["light_where"] == "in_shade"                                   # a library lamp: in its shade
    assert L.rig_fixture_problems(plan["fixtures"], BEDROOM["polygon"], [BED] + STANDS, decor, 0.0) == []


def test_rig_lamp_takes_a_free_spot_of_a_wide_nightstand_top():
    """A small item at the centre of a wide top: the lamp stands beside it (nearest the bed's head corner first),
    its base still on the top, its shade inside the top's edge; the reason names the item."""
    from wenart.blender.parametric import piece_bbox
    wide = [_piece("n1", "nightstand", (0.8, 2.75), (0.6, 0.45)), _piece("n2", "nightstand", (3.2, 2.75), (0.6, 0.45))]
    top = piece_bbox(wide[0])[2]
    vase = [{"name": "decor_n1_1", "wenart_id": "n1", "element_id": "n1", "decor_id": "dec_vase", "host_id": "n1",
             "kind": "decor", "room_id": "r1", "type": "vase", "center": [0.8, 2.75, top + 0.1],
             "size": [0.1, 0.1, 0.2]}]
    decor = L.built_decor_boxes(vase, "r1")
    plan = L.rig_plan(BEDROOM, [BED] + wide, 0.0, 2.7, decor=decor)
    lamp = next(f for f in plan["fixtures"] if f["anchor_id"] == "n1")
    assert lamp["mount"] == "stand" and "beside the vase dec_vase" in lamp["reason"]
    assert _bottom(lamp) == pytest.approx(top) and not L.boxes_collide(L.fixture_box(lamp), decor[0])
    half = max(lamp["size_m"][:2]) / 2.0
    bw, bd = piece_bbox(wide[0])[:2]                                          # the built top (with its handles)
    assert abs(lamp["center"][0] - 0.8) + half <= bw / 2.0 - L.RIG_STAND_EDGE_M + 1e-4
    assert abs(lamp["center"][1] - 2.75) + half <= bd / 2.0 - L.RIG_STAND_EDGE_M + 1e-4
    assert lamp["center"][0] > 0.8                                            # the side towards the bed's corner
    other = next(f for f in plan["fixtures"] if f["anchor_id"] == "n2")
    assert other["center"][:2] == [3.2, 2.75] and other["reason"] == "bedside lamp on the nightstand n2"
    assert L.rig_fixture_problems(plan["fixtures"], BEDROOM["polygon"], [BED] + wide, decor, 0.0) == []


def test_fixture_check_reads_the_nightstand_top_from_the_piece_not_its_decor():
    """The review of the P4a fix round: ``rig_fixture_problems`` without ``stand_tops`` (as a scene check calls it)
    took the nightstand's top from the last decor box keyed by its id and reported a lamp that stands correctly. With
    manifest-shaped decor a correct lamp passes and a lamp through the item on its top is flagged."""
    from wenart.blender.parametric import piece_bbox
    top = piece_bbox(STANDS[0])[2]
    objs = _manifest_decor(top)
    objs[1] = dict(objs[1], type="book_set", center=[3.0, 2.75, top + 0.03], size=[0.1, 0.15, 0.06])
    decor = L.built_decor_boxes(objs, "r1")
    lamp = {"name": "rig_r1_bedside_9", "kind": "bedside", "mount": "stand", "anchor_id": "n2", "host_id": "n2",
            "size_m": [0.24, 0.24, 0.42], "center": [3.32, 2.75, top + 0.21]}
    assert L.rig_fixture_problems([lamp], BEDROOM["polygon"], [BED] + STANDS, decor, 0.0) == []
    through = dict(lamp, name="through", anchor_id="n1", host_id="n1", center=[0.8, 2.75, top + 0.21])
    problems = L.rig_fixture_problems([through], BEDROOM["polygon"], [BED] + STANDS, decor, 0.0)
    assert [p["problem"] for p in problems] == ["crosses plant_small dec_plant"]


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

def floor_light(case, tag):
    plan, hosts = case["plan"], case.get("hosts") or []
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 8
    sc.render.resolution_x = sc.render.resolution_y = 24
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.0, 0.0, 0.0)
    me = bpy.data.meshes.new("floor")
    me.from_pydata([(-3, -3, 0), (6, -3, 0), (6, 6, 0), (-3, 6, 0)], [], [[0, 1, 2, 3]])
    sc.collection.objects.link(bpy.data.objects.new("floor", me))
    objs, assumed = [], []
    for h in hosts:                                   # the host models (closed shades), as furniture.py records them
        common.new_mesh_object(h["entry"]["name"], h["verts"], h["faces"], collection=sc.collection,
                               wenart_id=h["entry"]["wenart_id"], kind=h["entry"]["kind"], status="assumed")
        objs.append(dict(h["entry"]))
    lights = L.build_room_rig(bpy, common, sc.collection, objs, assumed, {"id": "r1"}, {"id": "L0"}, plan,
                              lambda k: M.fixture_material("rig_fixture_2700K", k))
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = 1.0
    co = bpy.data.objects.new("c", cam); co.location = (0.8, 2.0, 0.3); sc.collection.objects.link(co); sc.camera = co
    sc.render.filepath = %(out)r + f"/floor_{tag}.png"; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    px = list(bpy.data.images.load(sc.render.filepath).pixels)
    lum = sum(px[i] + px[i + 1] + px[i + 2] for i in range(0, len(px), 4)) / (len(px) / 4) / 3
    meshes = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("rig_")]
    slots = {}
    for o in meshes:
        mats = [m.name for m in o.data.materials]
        counts = [sum(1 for p in o.data.polygons if p.material_index == i) for i in range(len(mats))]
        emit = []
        for m in o.data.materials:
            nodes = m.node_tree.nodes if m.node_tree else []
            e = [n.inputs["Strength"].default_value for n in nodes if n.bl_idname == "ShaderNodeEmission"]
            e += [n.inputs["Emission Strength"].default_value for n in nodes
                  if n.bl_idname == "ShaderNodeBsdfPrincipled"]
            emit.append(max(e) if e else 0.0)
        slots[o.name] = {"materials": mats, "faces": counts, "emission": emit}
    return {"lum": lum, "meshes": [o.name for o in meshes], "shadow": [o.visible_shadow for o in meshes],
            "lights": [o.name for o in lights], "entries": [e.get("rig_box") is not None for e in objs
                                                            if e["kind"] == "decor" and e.get("method") == "rig"],
            "slots": slots, "light_z": [round(o.location.z, 4) for o in lights],
            "escape": [e["assumed"].get("escape") for e in objs if e["kind"] == "light"],
            "where": [e["assumed"].get("light_where") for e in objs if e["kind"] == "light"],
            "reasons": [e["assumed"].get("reason") for e in objs if e["kind"] == "light"],
            "rig_reasons": [a["reason"] for a in assumed if a.get("kind") == "rig_light"],
            "moved": [a for a in assumed if a.get("kind") == "rig_light_moved"],
            "enclosed": [a for a in assumed if a.get("kind") == "rig_light_enclosed"]}

out = {}
for name, case in json.loads(%(cases)r).items():
    out[name + "_on"] = floor_light(case, name + "_on")
    for f in case["plan"]["fixtures"]:
        f["light"]["energy_w"] = 0.0
    out[name + "_off"] = floor_light(case, name + "_off")
print("RESULT " + json.dumps(out))
"""


def _host_case(entry, parts, center, rot, z0):
    """A host model for the Blender script: its world mesh and its manifest entry."""
    from wenart.blender import parametric as P
    verts, faces, _keys = P.world_mesh(parts, center, rot, z0)
    return {"entry": entry, "verts": [list(v) for v in verts], "faces": [list(f) for f in faces]}


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_blender_shades_let_their_light_out_and_hosted_fixtures_build_no_mesh(tmp_path):
    """The table lamp's point light sits inside its closed drum shade (top + 0.7 h). P3/P4a: the Emission-only shade
    blocked it (bpy 5.2.2: the floor metered the same with the light on or off). With ``visible_shadow`` off the floor
    under the lamp gets its light; a hosted fixture (``mesh: False``) builds its light and no mesh.

    Fix round after P4b (17 Oct 2026; the review of the P4a fix round): a hosted light inside a closed host reached
    nothing. Now (1) the light hosted by a parametric decor pendant (a closed frustum shade and a bulb) hangs under it
    and lights the floor; (2) the light hosted by a library floor lamp whose closed shade encloses the in-shade spot is
    moved out by the ray check (``free_light_point``) and lights the floor, recorded ``escapes`` with the distance;
    (3) the table lamp's object has the emissive shade slot and the non-emissive hardware slot (base and stem)."""
    from wenart.blender import parametric as P
    stands = [_piece("n1", "nightstand", (0.8, 2.75), (0.45, 0.4)), _piece("n2", "nightstand", (3.2, 2.75),
                                                                           (0.45, 0.4))]
    plan = L.rig_plan(BEDROOM, [BED] + stands, 0.0, 2.7)
    plan["fixtures"] = plan["fixtures"][:1]                         # the lamp on n1, over the camera's patch
    plan["fixtures"][0]["light"]["energy_w"] = 5.0
    lamps = [_piece("fl1", "floor_lamp", (0.75, 2.7), (0.45, 0.45))]
    hosted = L.rig_plan(BEDROOM, [BED] + lamps, 0.0, 2.7)
    hosted["fixtures"] = [f for f in hosted["fixtures"] if f["mesh"] is False]
    # (1) a parametric decor pendant over a table under the camera's patch: a closed frustum from 1.5 m up
    pendant = {"name": "decor_dec_p", "wenart_id": "dec_p", "element_id": "dec_p", "decor_id": "dec_p",
               "host_id": None, "kind": "decor", "room_id": "r1", "type": "pendant_light",
               "method": "parametric (fallback: no asset)", "center": [0.8, 2.0, 1.85], "size": [0.45, 0.45, 0.7]}
    dining = {"id": "r1", "room_type": "dining", "polygon": [[-1, 0], [4, 0], [4, 4], [-1, 4]]}
    hung = L.rig_plan(dining, [_piece("t", "table_dining", (0.8, 2.0), (1.6, 0.9))], 0.0, 2.7,
                      decor=L.built_decor_boxes([pendant], "r1"))
    assert [(f["mesh"], f["host_id"]) for f in hung["fixtures"]] == [(False, "dec_p")]
    pend = _host_case(pendant, P.decor_parts("pendant_light", 0.45, 0.45, 0.7), (0.8, 2.0), 0.0, 1.5)
    # (2) a library floor lamp beside the bed, its model a closed shade (the parametric floor lamp's parts)
    lib = _piece("fl1", "floor_lamp", (0.8, 2.9), (0.45, 0.45), asset={"method": "library",
                                                                           "bbox_m": [0.45, 0.45, 1.6]})
    lit = L.rig_plan(BEDROOM, [BED, lib], 0.0, 2.7, piece_methods={"fl1": "library"})
    lit["fixtures"] = [f for f in lit["fixtures"] if f["mesh"] is False]
    assert [f["light_where"] for f in lit["fixtures"]] == ["in_shade"]
    in_shade = lit["fixtures"][0]["light"]["center"][2]
    lamp = _host_case({"name": "furn_fl1", "wenart_id": "fl1", "element_id": "fl1", "kind": "furniture",
                       "room_id": "r1", "type": "floor_lamp", "method": "library"},
                      P.build_parts("floor_lamp", 0.45, 0.45, 1.6), (0.8, 2.9), 0.0, 0.0)
    cases = {"lamp": {"plan": plan}, "hosted": {"plan": hosted}, "pendant": {"plan": hung, "hosts": [pend]},
             "library": {"plan": lit, "hosts": [lamp]}}
    script = RIG_SCRIPT % {"root": str(ROOT), "out": str(tmp_path), "cases": json.dumps(cases)}
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr", script],
                          capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    out = json.loads(next(ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT "))[7:])
    for name in ("lamp", "pendant", "library"):
        print(f"floor light, {name}: on {out[name + '_on']['lum']:.5f}, off {out[name + '_off']['lum']:.5f}, "
              f"light z {out[name + '_on']['light_z']}, escape {out[name + '_on']['escape']}")
    on, off = out["lamp_on"], out["lamp_off"]
    assert on["meshes"] == ["rig_r1_bedside_1"] and on["shadow"] == [False]
    assert on["entries"] == [True]
    assert on["lum"] > 1.2 * off["lum"] + 1e-4, out                         # the light reaches the floor
    assert out["hosted_on"]["meshes"] == [] and out["hosted_on"]["lights"] == ["rig_r1_bedside_1_light"]
    # (3) the shade emits, the hardware (base and stem) does not
    slot = on["slots"]["rig_r1_bedside_1"]
    assert slot["materials"] == ["rig_fixture_2700K", "rig_hardware"] and slot["faces"] == [10, 16]
    assert slot["emission"][0] > 0 and slot["emission"][1] == 0
    # (1) the parametric pendant: the light under its closed shade reaches the floor
    p_on, p_off = out["pendant_on"], out["pendant_off"]
    assert p_on["meshes"] == [] and p_on["escape"] == [{"host_object": "decor_dec_p", "escapes": True, "moved_m": 0.0}]
    assert p_on["light_z"] == [pytest.approx(1.5 - L.RIG_HOSTED_PENDANT_GAP_M)]
    assert p_on["lum"] > 1.2 * p_off["lum"] + 1e-4, out
    # (2) the library lamp's closed shade: the ray check moves the light out, under the shade, and it lights the floor
    l_on, l_off = out["library_on"], out["library_off"]
    (esc,) = l_on["escape"]
    assert esc["host_object"] == "furn_fl1" and esc["escapes"] is True and esc["moved_m"] > 0.1
    shade_bottom = 1.6 - min(0.4, 1.6 * 0.3)
    assert l_on["light_z"] == [pytest.approx(shade_bottom - L.RIG_ESCAPE_STEP_M, abs=1e-3)]
    assert l_on["light_z"][0] == pytest.approx(in_shade - esc["moved_m"], abs=1e-3) and l_on["enclosed"] == []
    assert l_on["lum"] > 1.2 * l_off["lum"] + 1e-4, out
    # pass before P5: the records say where the light is built (before: "in the shade", 0.30 m above it)
    assert esc["from_where"] == "in_shade" and esc["from_z"] == pytest.approx(in_shade)
    assert l_on["where"] == ["below_host_surface"]
    moved = f"moved {esc['moved_m']:.2f} m down by the ray check"
    assert moved in l_on["reasons"][0] and moved in l_on["rig_reasons"][0] and "furn_fl1" in l_on["reasons"][0]
    assert [a["value"] for a in l_on["moved"]] == [esc["moved_m"]]
    assert p_on["where"] == ["under_host"] and p_on["moved"] == []                  # not moved: unchanged


# --------------------------------------------------------------------------
# Pass before P5: a light the ray check moved is recorded where it is built
# --------------------------------------------------------------------------

class _Vec(tuple):
    """mathutils.Vector, as much of it as build_room_rig and the ray check use."""

    def __new__(cls, v):
        return super().__new__(cls, (float(a) for a in v))

    def normalized(self):
        n = sum(a * a for a in self) ** 0.5
        return _Vec(a / n for a in self)


class _Identity:
    """An object's matrix_world at the origin, unrotated."""

    def inverted(self):
        return self

    def to_3x3(self):
        return self

    def __matmul__(self, v):
        return _Vec(v)


class _ClosedShade:
    """A host lamp's mesh object: a closed box (a closed shade) that rays hit from inside and from outside, as
    ``bpy.types.Object.ray_cast`` hits front and back faces."""
    type = "MESH"
    matrix_world = _Identity()

    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi

    def ray_cast(self, o, d, depsgraph=None):
        t0, t1 = float("-inf"), float("inf")
        for a in range(3):
            if abs(d[a]) < 1e-12:
                if not self.lo[a] - 1e-9 <= o[a] <= self.hi[a] + 1e-9:
                    return False, None, None, None
                continue
            ta, tb = (self.lo[a] - o[a]) / d[a], (self.hi[a] - o[a]) / d[a]
            t0, t1 = max(t0, min(ta, tb)), min(t1, max(ta, tb))
        if t0 > t1 or t1 <= 1e-9:
            return False, None, None, None
        t = t0 if t0 > 1e-9 else t1
        return True, _Vec(o[i] + t * d[i] for i in range(3)), None, None


class _Ob(dict):
    """A Blender object: attributes plus custom properties."""

    def __init__(self, name, data):
        super().__init__()
        self.name, self.data, self.type = name, data, "LIGHT"
        self.location = self.rotation_euler = None
        self.visible_camera = True


class _Objects(dict):
    def new(self, name, data):
        self[name] = _Ob(name, data)
        return self[name]


def _rig_with_host(monkeypatch, shade):
    """``build_room_rig`` on the library floor lamp fl1 beside the bed (1.6 m, its light planned in its shade) with a
    stand-in bpy whose host object ``furn_fl1`` is ``shade``: (the plan's fixture, the light's manifest entry, the
    light object, the assumed list)."""
    import sys
    import types
    from types import SimpleNamespace as NS

    monkeypatch.setitem(sys.modules, "mathutils", types.ModuleType("mathutils"))
    sys.modules["mathutils"].Vector = _Vec
    lib = _piece("fl1", "floor_lamp", (0.8, 2.9), (0.45, 0.45), asset={"method": "library",
                                                                           "bbox_m": [0.45, 0.45, 1.6]})
    plan = L.rig_plan(BEDROOM, [BED, lib], 0.0, 2.7, piece_methods={"fl1": "library"})
    plan["fixtures"] = [f for f in plan["fixtures"] if f["mesh"] is False]
    assert [f["light_where"] for f in plan["fixtures"]] == ["in_shade"]
    objects = _Objects({"furn_fl1": shade})
    bpy = NS(data=NS(objects=objects, lights=NS(new=lambda name, kind: NS(name=name, type=kind))),
             context=NS(evaluated_depsgraph_get=lambda: None))
    objs = [{"name": "furn_fl1", "wenart_id": "fl1", "element_id": "fl1", "kind": "furniture", "room_id": "r1",
             "type": "floor_lamp", "method": "library"}]
    assumed: list = []
    lights = L.build_room_rig(bpy, NS(set_props=lambda ob, **kw: ob.update(kw)), NS(objects=NS(link=lambda ob: None)),
                              objs, assumed, {"id": "r1"}, {"id": "L0"}, plan, None)
    (entry,) = [o for o in objs if o["kind"] == "light"]
    (light,) = lights
    return plan["fixtures"][0], entry, light, assumed


def test_pass_p5_a_light_moved_out_of_a_closed_shade_is_recorded_where_it_is_built(monkeypatch):
    """Pass before P5 (17 Oct 2026; the review of the fix round after P4b): the light hosted by a library floor lamp
    whose model is a closed shade (z 1.20-1.60 m) is planned in the shade (z 1.45 m); the ray check moves it under
    the shade (``RIG_ESCAPE_STEP_M`` under 1.20 m). On HEAD adc3004 only the light's centre and ``escape.moved_m``
    said so: its ``light_where``, its reason and the scene's ``rig_light`` entry still said "in the shade", 0.30 m
    above where it was built. Now ``light_where`` is ``below_host_surface``, the reason adds the move, ``escape``
    keeps the planned spot and an assumed ``rig_light_moved`` entry records the distance. A shade that lets the
    light out where the plan put it changes nothing (the four library lamps of P3's real04 at their in-shade spots)."""
    in_shade = 1.6 - L.RIG_HOST_LAMP_SHADE_M
    built = 1.2 - L.RIG_ESCAPE_STEP_M
    f, entry, light, assumed = _rig_with_host(monkeypatch, _ClosedShade((0.6, 2.7, 1.2), (1.0, 3.1, 1.6)))
    a = entry["assumed"]
    assert light.location[2] == pytest.approx(built) and entry["center"][2] == pytest.approx(built)
    assert a["escape"] == {"host_object": "furn_fl1", "escapes": True, "moved_m": pytest.approx(in_shade - built),
                           "from_where": "in_shade", "from_z": pytest.approx(in_shade)}
    assert a["light_where"] == f["light_where"] == "below_host_surface"
    moved = f"moved {in_shade - built:.2f} m down by the ray check (z {in_shade:.2f} -> {built:.2f} m)"
    assert a["reason"].startswith("bedside light in the shade of the floor lamp fl1") and moved in a["reason"]
    assert "furn_fl1" in a["reason"] and "under its closed shade or bulb" in a["reason"]
    (rig,) = [x for x in assumed if x["kind"] == "rig_light"]
    assert moved in rig["reason"]
    (mv,) = [x for x in assumed if x["kind"] == "rig_light_moved"]
    assert mv["object"] == "rig_r1_bedside_1_light" and mv["value"] == pytest.approx(in_shade - built)
    assert mv["parent"] == "r1" and "furn_fl1" in mv["reason"] and f"z {built:.2f} m" in mv["reason"]
    assert [x for x in assumed if x["kind"] == "rig_light_enclosed"] == []
    # an open model (the shade's box elsewhere): the light gets out where the plan put it; no record changes
    f, entry, light, assumed = _rig_with_host(monkeypatch, _ClosedShade((2.0, 0.5, 1.2), (2.4, 0.9, 1.6)))
    a = entry["assumed"]
    assert light.location[2] == pytest.approx(in_shade)
    assert a["escape"] == {"host_object": "furn_fl1", "escapes": True, "moved_m": 0.0}
    assert a["light_where"] == "in_shade" and "moved" not in a["reason"]
    assert [x["kind"] for x in assumed] == ["rig_light"]
