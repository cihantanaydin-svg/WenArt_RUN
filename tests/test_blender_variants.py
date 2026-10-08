"""Tests of the whole building (docs/milestone10.md §3.2, §3.3, §1.6): the pure parts on the CPU (slab plan,
corners, the outside looks, sills, railings, ``build.prepare``) and, with ``WENART_BLENDER``, the build of
``docs/examples/building_m10.example.json`` for both variants (object counts per kind, slab, roof, wall and
ceiling z ranges against the contract's numbers, the terrace without roof or ceiling, the site, the ``ext_*``
cameras, the manifest's variant and assumed entries) and one small CPU render of an exterior camera."""
import copy
import json
import math
import textwrap
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart import views as V
from wenart.blender import build as B
from wenart.blender import cli, geom2d, schemas, shell
from wenart.blender import exterior as E

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PATH = ROOT / "docs" / "examples" / "building_m10.example.json"
EXAMPLE = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
ALT = "l-1b-acik-mutfak"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, /workspace/tools/blender, "
                                                           "/opt/wenart/blender, PATH)")


# --------------------------------------------------------------------------
# Pure parts (CPU)
# --------------------------------------------------------------------------

def test_slab_plan_of_the_example():
    vb = V.variant_building(EXAMPLE, "base")
    plan = shell.slab_plan(vb, vb["levels"], 0.20, True)
    slabs = {s["id"]: s for s in plan["slabs"]}
    assert list(slabs) == ["sl_L-1", "sl_L0", "sl_L1"] and not plan["warnings"] and not plan["assumed"]
    assert [(s["z_top"], s["thickness"]) for s in slabs.values()] == [(-3.0, 0.2), (0.0, 0.2), (3.0, 0.2)]
    assert slabs["sl_L0"]["stairs"] == ["f_L-1_001"] and len(slabs["sl_L0"]["voids"]) == 1
    assert slabs["sl_L1"]["stairs"] == ["f_L0_001"]
    assert plan["by_level"]["L0"]["under"]["id"] == "sl_L0" and plan["by_level"]["L0"]["above"]["id"] == "sl_L1"
    assert plan["by_level"]["L1"]["above"] is None
    verts, faces = shell.slab_solid(slabs["sl_L0"])
    zs = [v[2] for v in verts]
    assert (min(zs), max(zs)) == pytest.approx((-0.2 + shell.SLAB_FACE_GAP, -shell.SLAB_FACE_GAP))
    tops = [f for f in faces if geom2d.face_normal(verts, f)[2] > 0.9]
    area = sum(abs(G.polygon_signed_area([verts[i][:2] for i in f])) for f in tops)
    inset = 10.25 - 2 * shell.SLAB_EDGE_INSET, 8.25 - 2 * shell.SLAB_EDGE_INSET
    assert area == pytest.approx(inset[0] * inset[1] - 1.1 * 3.1, abs=1e-6)        # minus the stair opening


def test_missing_slabs_and_openings_are_derived_and_assumed():
    b = copy.deepcopy(EXAMPLE)
    b["slabs"] = [s for s in b["slabs"] if s["id"] != "sl_L1"]
    for s in b["slabs"]:
        if s["id"] == "sl_L0":
            s["openings"] = []                     # no opening drawn over the basement stair
            s["thickness"] = None
    vb = V.variant_building(b, "base")
    plan = shell.slab_plan(vb, vb["levels"], 0.20, True)
    slabs = {s["id"]: s for s in plan["slabs"]}
    assert slabs["sl_L1"]["source"] == "derived" and slabs["sl_L1"]["status"] == "assumed"
    assert slabs["sl_L1"]["thickness"] == 0.20 and slabs["sl_L1"]["z_top"] == 3.0
    assert slabs["sl_L0"]["thickness"] == 0.20 and len(slabs["sl_L0"]["voids"]) == 1
    assert any("no opening over stair f_L-1_001" in w for w in plan["warnings"])
    reasons = " ".join(a["reason"] for a in plan["assumed"])
    assert "slab_thickness" in reasons and "derived from the wall outline" in reasons
    assert "opening for stair f_L-1_001 added" in reasons


def test_a_stair_arriving_outside_the_opening_is_a_warning():
    plan = {"flights": [{"start": [9.35, 4.5], "end": [9.35, 7.5]}]}
    void = [[8.8, 4.45], [9.9, 4.45], [9.9, 7.55], [8.8, 7.55]]
    assert shell.stair_arrivals(plan, [void]) == []
    assert shell.stair_arrivals({"flights": [{"start": [2, 1], "end": [2, 3]}]}, [void])[0].startswith("arrives at")


def test_corner_joins_close_the_outer_corners():
    walls = [w for w in EXAMPLE["walls"] if w["level_id"] == "L0"]
    ext = shell.corner_extensions(walls)
    assert ext["w_L0_001"] == {"start": [0.0, 0.125], "end": [10.25, 0.125]}      # to the outer wall faces
    assert ext["w_L0_004"] == {"start": [0.125, 8.25], "end": [0.125, 0.0]}
    assert "w_L0_005" not in ext                   # a T-join (its ends meet no wall end) stays as drawn
    trims = shell.trim_wall_overlaps([dict(w, **ext.get(w["id"], {})) for w in walls])
    rects = []
    for w in walls:
        if w["exterior"]:
            quad = G.centerline_to_rectangle(trims[w["id"]]["start"], trims[w["id"]]["end"], w["thickness"])
            xs, ys = [p[0] for p in quad], [p[1] for p in quad]
            rects.append((min(xs), min(ys), max(xs), max(ys)))
    loops = geom2d.rect_union_outline(rects)
    outer = max(loops, key=G.polygon_area)
    assert G.polygon_area(outer) == pytest.approx(10.25 * 8.25)    # the four corners are closed


def test_track_f_look_wrappers_give_the_m9_looks():
    # docs/milestone10.md §1.6b row 20: shell.py calls these; until wenart/blender/looks.py (track F) exists they
    # return the style slots as the M3-M9 shell used them
    style = json.loads(STYLE.read_text(encoding="utf-8"))
    assert shell.wall_face_material(style) == {"material": "plaster_white", "asset": "white_plaster_02", "tint": None}
    assert shell.wet_wall_look(style, {"room_type": "bathroom"})["material"] == "tiles_light"
    assert shell.wet_wall_look({"walls": {"material": "plaster_white"}})["material"] == "plaster_white"
    assert shell.accent_walls(EXAMPLE, EXAMPLE["levels"][0], style) == {}
    door = shell.door_look(style, {"id": "d", "type": "door"})
    assert (door["material"], door["asset"]) == shell.door_leaf_material(style["door"])
    assert shell.window_frame_look(style, {"id": "w"})["material"] == "painted_metal_white"
    looks = E.resolve_looks(EXAMPLE, style)
    assert shell.facade_look(looks, EXAMPLE["walls"][0]) is looks["facade"]
    from wenart.style import colours                                    # track C's cited table (Milestone 10)
    assert shell.colour_rgb("greige") == pytest.approx(colours.linear_rgb("greige"), abs=1e-3)   # shell rounds to 4
    assert shell.colour_rgb("not a colour") is None


def test_facade_faces_go_to_the_walls_of_their_side():
    vb = V.variant_building(EXAMPLE, "base")
    outlines = {lv["id"]: geom2d.wall_outline([w for w in vb["walls"] if w["level_id"] == lv["id"]])[0]
                for lv in vb["levels"]}
    faces, warnings = B.facade_faces(vb, outlines)
    assert list(faces) == ["w_L-1_001"] and not warnings                 # the south wall of the basement only
    assert faces["w_L-1_001"][0]["direction"] == pytest.approx([0.0, -1.0])
    b = copy.deepcopy(vb)
    b["facade"]["faces"] = [dict(vb["facade"]["faces"][0], side="all", level_id=None, z_range=None),
                            dict(vb["facade"]["faces"][0], side="west", level_id="L0"),
                            dict(vb["facade"]["faces"][0], side="north", level_id="L9")]
    faces, warnings = B.facade_faces(b, outlines)
    outer = {w["id"] for w in b["walls"] if shell.outward_side(w, outlines[w["level_id"]],
                                                              G.segment_midpoint(w["start"], w["end"]))}
    assert set(faces) == outer                                            # side "all": every outer wall
    assert faces["w_L0_004"][-1]["side"] == "west" and faces["w_L0_004"][0]["direction"] is None
    assert sum(len(v) for v in faces.values()) == len(outer) + 1 and not warnings     # L9 is not built


def test_outside_sill_and_balcony_railing():
    wall = next(w for w in EXAMPLE["walls"] if w["id"] == "w_L0_001")
    win = next(o for o in EXAMPLE["openings"] if o["id"] == "win_L0_001")
    level = next(lv for lv in EXAMPLE["levels"] if lv["id"] == "L0")
    verts, _faces, info = shell.sill_box(win, wall, level, True, (0.0, -1.0))
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    assert min(ys) == pytest.approx(0.0 - shell.SILL["projection"])           # proud of the facade (y = 0)
    assert max(ys) == pytest.approx(0.125 - 0.041)                            # from the frame's outer edge
    assert max(zs) == pytest.approx(0.9 + shell.SILL["rise"]) and info["width"] == pytest.approx(1.6 + 0.06)
    balcony = {"id": "r_b", "level_id": "L0", "room_type": "balcony",
               "polygon": [[0.25, -1.375], [3.125, -1.375], [3.125, 0.0], [0.25, 0.0]]}
    walls = [w for w in EXAMPLE["walls"] if w["level_id"] == "L0"]
    edges = shell.railing_edges(balcony, walls)
    assert len(edges) == 3                       # the outer edge and both free sides; the facade side is closed
    lengths = sorted(round(G.distance(p, q), 2) for p, q in edges)
    assert lengths[-1] == pytest.approx(2.875, abs=0.01)
    assert all(max(p[1], q[1]) < 0.0 - 0.04 for p, q in edges)        # nothing along the wall face


def test_prepare_the_whole_building():
    prep = B.prepare(EXAMPLE, "base")
    assert prep["whole"] and [lv["id"] for lv in prep["building"]["levels"]] == ["L-1", "L0", "L1"]
    attic = prep["building"]["levels"][-1]
    assert len(attic["ceiling_planes"]) == 3 and attic["ceiling_planes"][-1] == [0.0, 0.0, 5.4]
    assert prep["open_rooms"] == {"r_L1_teras"} and prep["site"]["mode"] == "full"
    assert list(prep["faces"]) == ["w_L-1_001"] and prep["faces"]["w_L-1_001"][0]["material"] == "stone_cladding"
    assert G.polygon_area(prep["ground_outline"]) == pytest.approx(10.25 * 8.25)
    assert prep["brief"]["site"] == {"value": "full", "assumed": False}               # the building's stored brief
    assert prep["brief"]["slab_thickness"] == {"value": 0.20, "assumed": True}
    assert prep["site"]["terrain"]["changes"][0]["opening_ids"] == ["d_L-1_001"]      # the basement door's side
    alt = B.prepare(EXAMPLE, ALT)
    assert alt["faces"]["w_L-1b_001"][0]["level_moved_from"] == "L-1" and alt["views"]["exterior"] is False
    ground = B.prepare(EXAMPLE, "base", {"values": {"site": "ground", "slab_thickness": 0.25}, "assumed": []})
    assert ground["site"]["mode"] == "ground" and ground["brief"]["slab_thickness"]["value"] == 0.25
    legacy = {k: v for k, v in EXAMPLE.items() if k not in ("slabs", "roof", "variants")}
    assert B.prepare(legacy)["whole"] is False
    with pytest.raises(KeyError):
        B.prepare(EXAMPLE, "nope")
    # no roof evidence (roof: null): an assumed flat roof over the top level
    flat = B.prepare(dict(EXAMPLE, roof=None), "base")
    assert flat["roof"]["type"] == "flat" and flat["roof"]["over_level_id"] == "L1"
    assert any("flat roof over the top level" in w for w in flat["warnings"])
    assert B.interior_camera_fields({"name": "c"}, ALT) == {"name": "c", "kind": "interior", "variant": ALT,
                                                             "view": None, "sides": [], "region_id": None,
                                                             "dropped_reason": None}


def test_an_opening_drawn_above_the_knee_wall_is_a_warning():
    from wenart.blender import roof as R

    prep = B.prepare(EXAMPLE, "base")
    attic = prep["building"]["levels"][-1]
    cut = R.wall_cut(prep["roof"])
    assert B.openings_through_roof(prep["building"], attic, cut) == []        # the gable window fits
    b = copy.deepcopy(prep["building"])
    for o in b["openings"]:
        if o["id"] == "win_L1_001":
            o["wall_id"], o["center"] = "w_L1_001", [3.0, 0.125]             # moved onto the 0.87 m knee wall
    assert any(w.startswith("win_L1_001: its top") for w in B.openings_through_roof(b, attic, cut))
    # a 2.1 m wardrobe against the knee wall shows through the sloped ceiling: listed
    b["furniture"].append({"id": "f_L1_w", "level_id": "L1", "room_id": "r_L1_oyun_odasi", "type": "wardrobe",
                           "source": "added_by_ai", "height": 2.1, "status": "verified", "evidence": [],
                           "footprint": {"center": [3.0, 0.6], "size": [1.8, 0.6], "rotation_deg": 0.0}})
    # a wall cabinet hung at 1.45 m (mount_bottom_m) reaches 2.15 m: under the flat part it fits, at the knee wall not
    b["furniture"].append({"id": "f_L1_c", "level_id": "L1", "room_id": "r_L1_oyun_odasi", "type": "wall_cabinet",
                           "source": "added_by_ai", "height": 0.7, "mount_bottom_m": 1.45, "status": "verified",
                           "evidence": [], "footprint": {"center": [3.0, 4.0], "size": [1.0, 0.35],
                                                         "rotation_deg": 0.0}})
    assert B.pieces_above_ceiling(prep["building"], attic) == []
    assert [w.split(":")[0] for w in B.pieces_above_ceiling(b, attic)] == ["f_L1_w"]
    b["furniture"][-1]["footprint"]["center"] = [3.0, 0.45]
    assert [w.split(":")[0] for w in B.pieces_above_ceiling(b, attic)] == ["f_L1_w", "f_L1_c"]


def test_camera_headroom_under_a_sloped_ceiling():
    from wenart.blender import camsearch

    prep = B.prepare(EXAMPLE, "base")
    attic = prep["building"]["levels"][-1]
    assert camsearch.headroom_ok(attic, (3.0, 4.0))            # under the flat part
    assert not camsearch.headroom_ok(attic, (3.0, 0.5))        # next to the knee wall
    room = next(r for r in prep["building"]["rooms"] if r["id"] == "r_L1_oyun_odasi")
    points, _ = camsearch.candidate_positions(room, prep["building"])
    assert points and all(camsearch.headroom_ok(attic, p) for p in points)


# --------------------------------------------------------------------------
# Blender: the example building, both variants
# --------------------------------------------------------------------------

DUMP = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for ob in bpy.data.objects:
        row = {"type": ob.type, "kind": ob.get("wenart_kind"), "status": ob.get("wenart_status"),
               "camera_kind": ob.get("wenart_camera_kind")}
        if ob.type == "MESH" and len(ob.data.vertices):
            mw = ob.matrix_world
            zs = [(mw @ v.co).z for v in ob.data.vertices]
            row["z"] = [min(zs), max(zs)]
            row["faces"] = [{"c": list(mw @ p.center), "n": list(p.normal),
                             "m": ob.data.materials[p.material_index].name if ob.data.materials else None}
                            for p in ob.data.polygons]
        if ob.type == "CAMERA":
            row["shift_y"] = ob.data.shift_y
            row["lens"] = ob.data.lens
            row["location"] = list(ob.location)
        rows[ob.name] = row
    json.dump(rows, open(out, "w"))
""")


@pytest.fixture(scope="module")
def example_builds(tmp_path_factory):
    """Both variants built as the scheduler would: the explicit --out of each (§1.6b row 9); the alternative with
    a brief whose exterior words name the window frames (dark bronze aluminium)."""
    tmp = tmp_path_factory.mktemp("m10e")
    out = tmp / "outputs" / "example" / "scene"
    brief = tmp / "brief.json"
    brief.write_text(json.dumps({"values": {"exterior": {"window_frame": "dark bronze aluminium"}}, "assumed": []}),
                     encoding="utf-8")
    built = {}
    (tmp / "dump.py").write_text(DUMP, encoding="utf-8")
    for variant in ("base", ALT):
        path = cli.build(EXAMPLE_PATH, cli.variant_path(out, variant), style=STYLE, no_textures=True,
                         preview_samples=1, camera_policy="search", variant=variant,
                         brief=brief if variant == ALT else None)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        dump = tmp / f"objects_{variant}.json"
        cli.run_blender(tmp / "dump.py", [str(dump)], blend=str(path.parent / "scene.blend"))
        built[variant] = {"path": path, "manifest": manifest, "objects": json.loads(dump.read_text(encoding="utf-8"))}
    built["tmp"] = tmp
    return built


@needs_blender
def test_example_manifest_validates_and_lands_in_the_variant_folders(example_builds):
    base, alt = example_builds["base"], example_builds[ALT]
    assert base["path"].parent.name == "scene" and base["path"].parent.parent.name == "example"
    assert alt["path"].parent == example_builds["tmp"] / "outputs" / "example" / "variants" / ALT / "scene"
    for b in (base, alt):
        schemas.validate_scene_manifest(b["manifest"])
        assert (b["path"].parent / "scene.blend").is_file() and b["manifest"]["build_args"]["variant"] in ("base", ALT)
    # the brief: the stored one for the base, the --brief file for the alternative (its values in the fingerprint)
    assert base["manifest"]["build_args"]["brief"]["exterior"]["assumed"] is True
    assert alt["manifest"]["build_args"]["brief"]["exterior"]["value"]["window_frame"] == "dark bronze aluminium"
    assert (alt["path"].parent / cli.BRIEF_FILE).is_file()
    assert cli.build_fingerprint(str(EXAMPLE_PATH), str(STYLE), None, None, True, 1, False, "search", None, ALT,
                                 cli.load_brief_arg(example_builds["tmp"] / "brief.json")) == \
        alt["manifest"]["build_fingerprint"]


@needs_blender
def test_example_object_counts_per_kind(example_builds):
    m = example_builds["base"]["manifest"]
    kinds = {}
    for o in m["objects"]:
        kinds.setdefault(o["kind"], set()).add(o["wenart_id"])
    levels = {"L-1", "L0", "L1"}
    assert kinds["wall"] >= {w["id"] for w in EXAMPLE["walls"] if w["level_id"] in levels}
    assert not any(w["wenart_id"].startswith("w_L-1b") for w in m["objects"] if w["kind"] == "wall")
    assert kinds["slab"] == {"sl_L-1", "sl_L0", "sl_L1"} and kinds["roof"] == {"roof"}
    # §1.6b row 11: the site kinds
    assert kinds["terrain"] == {"ground"} and kinds["site_wall"] == {"sw_L0_001", "sw_L0_002", "sw_L0_003", "sw_L0_004"}
    assert kinds["site_area"] == {"sp_001", "spk_001"} and kinds["site_decor"] == {"tree_sd_L0_001"}
    assert "site" not in kinds and "light_well" not in kinds          # the south side is open: no light well
    sills = [o for o in m["objects"] if o["name"].endswith("_sill")]
    windows = {o["id"] for o in EXAMPLE["openings"] if o["type"] == "window" and o["level_id"] in levels}
    assert {o["wenart_id"] for o in sills} == windows and all(o["status"] == "assumed" for o in sills)
    ceilings = {o["wenart_id"] for o in m["objects"] if o["kind"] == "ceiling"}
    rooms = {r["id"] for r in EXAMPLE["rooms"] if r["level_id"] in levels}
    assert ceilings == rooms - {"r_L1_teras"}                        # the roof terrace is open to the sky
    floor = next(o for o in m["objects"] if o["kind"] == "floor" and o["wenart_id"] == "r_L1_teras")
    assert floor.get("open_to_sky") is True
    parking = next(o for o in m["objects"] if o["wenart_id"] == "spk_001")
    assert parking["area_id"] == "sa_L0_otopark" and parking["slug"] == "paving" and parking["colour"] == "grey"


@needs_blender
def test_example_z_ranges_against_the_contract(example_builds):
    objs = example_builds["base"]["objects"]
    gap = shell.SLAB_FACE_GAP
    for sid, z_top in (("sl_L-1", -3.0), ("sl_L0", 0.0), ("sl_L1", 3.0)):
        assert objs[sid]["z"] == pytest.approx([z_top - 0.2 + gap, z_top - gap], abs=1e-4)
    assert objs["roof"]["z"] == pytest.approx([3.65 - 0.25 / math.cos(math.radians(35.0)), 6.888], abs=2e-3)
    # walls of the lower levels run to the next floor; the attic walls end at the roof underside
    assert objs["w_L-1_001"]["z"] == pytest.approx([-3.0, 0.0], abs=1e-4)
    assert objs["w_L0_002"]["z"] == pytest.approx([0.0, 3.0], abs=1e-4)
    under_ridge = 6.888 - 0.25 / math.cos(math.radians(35.0))
    assert objs["w_L1_002"]["z"] == pytest.approx([3.0, under_ridge], abs=2e-3)       # gable end
    # the south attic wall: a 0.87 m knee wall, under the roof terrace a 1.00 m parapet (§1.6b row 13)
    south = objs["w_L1_001"]["faces"]
    knee = [f for f in south if f["n"][2] > 0.1 and f["c"][0] < 6.0]
    parapet = [f for f in south if f["n"][2] > 0.9 and f["c"][0] > 6.3]
    assert knee and all(f["c"][2] < 3.0 + 0.870 + 0.01 for f in knee)
    assert parapet and all(f["c"][2] == pytest.approx(4.0, abs=1e-4) for f in parapet)
    entry = next(o for o in example_builds["base"]["manifest"]["objects"] if o["name"] == "w_L1_001")
    assert [p["z_top"] for p in entry["parapet"]] == [4.0]
    # floors at the level elevations; the hall above the basement stair is cut by the opening
    assert objs["r_L0_hol_floor"]["z"] == pytest.approx([0.0, 0.0], abs=2e-3)
    void = next(s for s in B.prepare(EXAMPLE)["slabs"]["slabs"] if s["id"] == "sl_L0")["voids"][0]
    x0, y0, x1, y1 = G.bbox(void)
    hall = objs["r_L0_hol_floor"]["faces"]
    assert not any(x0 < f["c"][0] < x1 and y0 < f["c"][1] < y1 for f in hall)
    assert "f_L-1_001_void" not in objs and "f_L0_001_void" not in objs              # no capped shaft
    # the site: the ground from the basement floor (south, the basement door's side) to 0.00
    assert objs["ground"]["z"] == pytest.approx([-3.0, 0.0], abs=1e-4)
    assert objs["sw_L0_001"]["z"][0] == pytest.approx(-3.1, abs=1e-4)


@needs_blender
def test_example_attic_ceiling_slopes_the_plinth_is_stone_and_the_frames(example_builds):
    objs = example_builds["base"]["objects"]
    ceiling = objs["r_L1_oyun_odasi_ceiling"]
    nz = [f["n"][2] for f in ceiling["faces"]]
    assert all(n < 0 for n in nz) and any(n > -0.99 for n in nz) and any(n < -0.999 for n in nz)
    assert ceiling["z"][1] == pytest.approx(5.4, abs=1e-4) and ceiling["z"][0] < 4.0
    hall = objs["r_L0_hol_ceiling"]
    assert all(f["n"][2] < -0.999 for f in hall["faces"])         # a floor below the roof keeps a flat ceiling
    # the south basement wall: stone cladding from -3 to -2 (facade.faces: side south, z_range), render above
    south = [f for f in objs["w_L-1_001"]["faces"] if f["n"][1] < -0.9]
    low = {f["m"].split(".")[0] for f in south if f["c"][2] < -2.0}
    high = {f["m"].split(".")[0] for f in south if f["c"][2] > -2.0}
    assert low == {"stone_cladding"} and high == {"render"}
    west = [f for f in objs["w_L-1_004"]["faces"] if f["n"][0] < -0.9]  # another side: no plinth
    assert west and {f["m"].split(".")[0] for f in west} == {"render"}
    # the wall between the attic hall and the roof terrace shows the facade on the terrace side
    terrace_side = [f for f in objs["w_L1_006"]["faces"] if f["n"][1] < -0.9 and 6.3 < f["c"][0] < 10.0]
    assert terrace_side and {f["m"].split(".")[0] for f in terrace_side} == {"render"}
    # window frames: the base has no outside look of its own (the fallback "interior"); the alternative's brief
    # names dark bronze aluminium, on the outer faces only
    m = example_builds["base"]["manifest"]
    assert m["whole_building"]["outside"]["frames_outside"] == 0
    assert m["exterior_looks"]["window_frame"]["source"] == "fallback"
    alt = example_builds[ALT]
    look = alt["manifest"]["exterior_looks"]["window_frame"]
    assert (look["material"], look["colour"], look["source"]) == ("aluminium", "dark bronze", "brief")
    frame = alt["objects"]["win_L0_001_frame"]["faces"]
    out = {f["m"].split(".")[0] for f in frame if f["n"][1] < -0.5}
    inside = {f["m"].split(".")[0] for f in frame if f["n"][1] > 0.5}
    assert out == {"aluminium"} and "aluminium" not in inside


@needs_blender
def test_example_cameras_per_variant(example_builds):
    base, alt = example_builds["base"]["manifest"], example_builds[ALT]["manifest"]
    ext = [c for c in base["cameras"] if c.get("kind") == "exterior"]
    assert len(ext) >= 5 and all(c["name"].startswith("ext_") for c in ext)
    assert all(c["variant"] == "base" and c["dropped_reason"] is None for c in base["cameras"])
    assert {c["region_id"] for c in ext if c["view"] == "elevation"} == {"r7", "r8"}
    inside = [c for c in base["cameras"] if c.get("kind") == "interior"]
    assert {c["room_id"] for c in inside} == {r["id"] for r in EXAMPLE["rooms"] if r["level_id"] in ("L-1", "L0", "L1")}
    assert all(c["view"] is None and c["sides"] == [] for c in inside)
    objs = example_builds["base"]["objects"]
    for c in ext:
        assert objs[c["name"]]["camera_kind"] == "exterior" and objs[c["name"]]["shift_y"] == pytest.approx(c["shift_y"])
    dropped = base["cameras_dropped"]
    assert len(ext) + len(dropped) == 7 and all(d["dropped_reason"] for d in dropped)
    assert not {d["name"] for d in dropped} & set(objs)                  # no camera object for a dropped view
    assert base["whole_building"]["exterior_cameras"]["dropped"] == [d["name"] for d in dropped]
    # the alternative renders only its changed room and lists the base views for the rest
    assert {c["room_id"] for c in alt["cameras"]} == {"r_L-1b_salon_acik_mutfak"}
    assert all(c["variant"] == ALT for c in alt["cameras"])
    assert alt["variant"]["rooms_changed"] == ["r_L-1b_salon_acik_mutfak"] and alt["variant"]["exterior_changed"] is False
    reasons = {r["room_id"]: r["reason"] for r in alt["rooms_without_view"]}
    assert reasons["r_L-1b_hol"] == "same as r_L-1_hol" and reasons["r_L0_hol"] == "unchanged in variant"
    assert alt["whole_building"]["exterior_cameras"]["planned"] == [] and alt["cameras_dropped"] == []
    assert alt["whole_building"]["exterior_cameras"]["from"] == "base"
    assert [v["id"] for v in base["variants"]] == ["base", ALT]
    assert not any(n.startswith("w_L-1_") for n in example_builds[ALT]["objects"])


@needs_blender
def test_example_assumed_entries(example_builds):
    m = example_builds["base"]["manifest"]
    fields = {(a["object"], a["field"]) for a in m["assumed"]}
    assert ("roof", "thickness") in fields and ("roof", "parapet_height:ro_001") in fields
    assert ("w_L1_001,w_L1_002", "parapet") in fields
    assert ("site", "terrain_slope") in fields and ("site", "ground:-y") in fields       # the basement door's side
    assert ("sw_L0_001", "height") in fields and ("tree_sd_L0_001", "tree") in fields
    assert ("exterior", "facade") in fields and ("exterior", "roof") in fields          # the fallback looks
    assert any(a["field"] == "sill" for a in m["assumed"])
    roof = m["whole_building"]["roof"]
    assert roof["planes_source"] == "building" and roof["derived_check"]["equivalent"] is True
    assert set(roof["parapets"]) == {"w_L1_001", "w_L1_002"} and roof["knee_wall_check"]["drawn"] == 1.0
    assert m["site"]["built"] is True and m["site"]["terrain"]["kind"] == "sides"
    assert m["site"]["terrain"]["changes"][0]["opening_ids"] == ["d_L-1_001"] and m["site"]["light_wells"] == []
    assert m["exterior_looks"]["facade"]["material"] == "render" and m["brief"]["site"]["value"] == "full"
    sun = next(o for o in m["objects"] if o["name"] == "sun")
    assert sun["assumed"]["north_deg"] == 0.0 and sun["assumed"]["azimuth_building_deg"] == pytest.approx(210.0)


@needs_blender
def test_small_cpu_render_of_an_exterior_camera(example_builds):
    m = example_builds["base"]["manifest"]
    cam = next(c["name"] for c in m["cameras"] if c.get("kind") == "exterior" and c["view"] == "corner")
    scene = example_builds["base"]["path"].parent / "scene.blend"
    out = example_builds["tmp"] / "outputs" / "example" / "renders"
    manifest_path = cli.render(scene, out, cameras=cam, samples=8, res="320x180", device="cpu")
    rm = json.loads(manifest_path.read_text(encoding="utf-8"))
    schemas.validate_render_manifest(rm)
    entry = next(e for e in rm["renders"] if e["camera"] == cam)
    assert entry["room_id"] is None and entry["level_id"] is None
    assert entry["exposure"]["meter"]["metered"] == "facade" and entry["exposure"]["ev"] < 0.0
    from PIL import Image

    with Image.open(out / f"{cam}.png") as img:
        assert img.size == (320, 180)
        lo, hi = img.convert("L").getextrema()
        assert hi - lo > 40                     # a picture, not a flat frame
