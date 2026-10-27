"""Doors and windows that fit the house's style, and guards around the stair voids (26 Oct 2026, user on real06, a
Scandinavian house: a glazed door with a busy black-and-white lattice, dark six-panel doors on the facade, a black
traditional sash among white sliding windows, an unguarded stair void at the upper landing; "The house needs to make
sense and needs to look very stylish"; "fix should be general, it is not a fix for real06"). CPU, pure."""
import json
import math
import struct
from pathlib import Path

import pytest

from wenart.assets.audit import growth_entries as GE
from wenart.blender import details as D
from wenart.blender import opening_build as OB
from wenart.blender import opening_models as OM
from wenart.blender import parametric as P

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "results" / "baseline" / "latest" / "furniture" / "real06" / "building_final.json"


# --------------------------------------------------------------------------
# styles reach the catalogue's extras (B2)
# --------------------------------------------------------------------------

def _door(i, title, styles=("neutral",), w=0.95, h=2.05, kind="door", status="keep", textured=True):
    return {"id": f"m{i}", "type": kind, "kind": "opening", "title": title, "glb": f"m{i}.glb",
            "bbox_m": [w, 0.12, h], "styles": list(styles), "audit": {"status": status}, "licence_flag": "none",
            "textured": textured}


def test_vision_fields_style_the_extras_and_the_audit_styles_only_neutral_entries():
    doc = {"entries": [], "extras": [_door(1, "Front Door"), _door(2, "Rustic Sliding Barn Door", ("rustic",))]}
    got = GE.apply_vision_fields(doc, {"m1": {"styles": ["modern", "minimal", "neutral"]}}, {"m1"})
    assert got["styled"] == 1 and doc["extras"][0]["styles"] == ["minimal", "modern"]
    audit = {"items": [{"id": "m1", "vision": {"styles": ["classic"]}},
                       {"id": "m2", "vision": {"styles": ["modern"]}}, {"id": "m3", "vision": None}]}
    assert set(GE.audit_answers(audit)) == {"m1", "m2"}
    doc2 = {"extras": [_door(1, "Front Door"), _door(2, "Rustic Barn Door", ("rustic",))]}
    assert GE.neutral_ids(doc2) == {"m1"}
    GE.apply_audit_styles(doc2, audit, ("extras",))
    assert doc2["extras"][0]["styles"] == ["classic"]                       # the placeholder took the answer
    assert doc2["extras"][1]["styles"] == ["rustic"]                        # named styles stay


def test_load_extras_takes_the_audit_styles(tmp_path):
    cat = tmp_path / "catalog_library.json"
    cat.write_text(json.dumps({"extras": [_door(1, "Front Door"), _door(2, "Window", kind="window")]}))
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"items": [{"id": "m1", "vision": {"styles": ["modern", "scandinavian"]}}]}))
    got = OM.load_extras(cat, audits=[audit])
    assert got[0]["styles"] == ["modern", "scandinavian"] and got[1]["styles"] == ["neutral"]
    assert OM.load_extras(cat, audits=[])[0]["styles"] == ["neutral"]


def test_the_repository_catalogue_reaches_the_build_with_door_styles():
    extras = OM.load_extras(ROOT / "wenart" / "furniture" / "catalog_library.json")
    doors = [e for e in extras if e.get("type") in ("door", "window") and (e.get("audit") or {}).get("status")
             in ("keep", "fix")]
    if not doors:
        pytest.skip("no door or window extras in the catalogue")
    styled = [e for e in doors if OM.entry_styles(e)]
    assert len(styled) >= 0.8 * len(doors)


# --------------------------------------------------------------------------
# the look of a style family (OPENING_LOOK)
# --------------------------------------------------------------------------

def test_a_modern_house_leaves_out_period_doors_and_a_classic_house_modern_ones():
    light = OM.look_of({"family": "scandinavian"})
    assert light["name"] == "light" and OM.look_of("Classic")["name"] == "period" and OM.look_of(None) is None
    assert OM.look_of({"family": "unknown"}) is None
    out = [_door(1, "Interior Door 80x32 6 Panel w 4.5 Frame"), _door(2, "Classical Georgian Front Door"),
           _door(3, "Andersen Windows - Craftsman Bungelow Style Single Casement", kind="window"),
           _door(4, "Front Door", ("classic", "rustic")), _door(5, "Window1 1", ("classic", "modern"), kind="window"),
           _door(6, "Double Hung Windows", kind="window"), _door(7, "Entry Door 80x32 2 Panels 9 Lite")]
    for e in out:
        assert OM.look_fit(e, light)[0] is None, e["title"]
    assert OM.look_fit(_door(8, "Pella Reserve Contemporary Sliding Door - 4-Panel"), light)[0] is not None
    assert OM.look_fit(_door(9, "Glass Door Sliding Door 4 Panel on 2 Tracks"), light)[0] is not None
    assert OM.look_fit(_door(10, "Research Door"), light)[0] is not None    # "arch" is a word, not a part of one
    ranks = [OM.look_fit(_door(11, "Door", s), light)[0] for s in
             (("scandinavian", "modern"), ("modern", "minimal"), ("neutral",), ("classic", "minimal", "modern"))]
    assert ranks == [0, 1, 2, 3]
    period = OM.look_of({"family": "rustic"})
    assert OM.look_fit(_door(12, "Aluminium Sliding Door"), period)[0] is None
    assert OM.look_fit(_door(13, "Sliding Window", ("modern", "minimal"), kind="window"), period)[0] is None
    assert OM.look_fit(_door(14, "Interior Door 6 Panel", ("classic",)), period)[0] == 1
    assert OM.look_fit(_door(15, "Front Door", ("classic", "rustic")), None) == (0, "no style family: every look")


def test_the_variants_of_one_series_are_one_family():
    k = OM.family_key
    assert k(_door(1, "Window1 1", kind="window")) == k(_door(2, "Window1 3", kind="window"))
    assert k(_door(3, "Valdi - Folding Sliding Door - 3 Door White")) == \
        k(_door(4, "Valdi - Folding Sliding Door - 4 Door Timber"))
    assert k(_door(5, "Front Door")) != k(_door(6, "Front Door"))            # two models of one name
    assert k(_door(7, "MHB - SL30 Steel Door - Double - Sliding")) == "id:m7"


# --------------------------------------------------------------------------
# one door and window language per building (B1, B4)
# --------------------------------------------------------------------------

def _outer(oid, kind, width, bottom, top):
    return {"opening": {"id": oid, "type": kind, "width": width}, "bottom": bottom, "top": top, "outward": [0, -1]}


def test_one_window_family_and_the_odd_window_stays_parametric():
    """real06: a moved 0.95 x 1.2 m window took a black traditional sash (another model) while the others were
    white sliders; now every window is of the building's family, and one it cannot fit stays parametric."""
    extras = [_door(1, "Sliding Window", ("modern", "minimal"), w=0.9, h=1.5, kind="window"),
              _door(2, "Single Casement Window", ("modern", "scandinavian", "minimal"), w=0.9, h=1.5, kind="window"),
              _door(3, "Window", ("modern",), w=1.0, h=1.25, kind="window", textured=False),
              _door(4, "Andersen Windows - Craftsman Bungelow Style", ("rustic", "classic"), w=0.95, h=1.2,
                    kind="window")]
    outer = [_outer(f"w{i}", "window", 0.72, 0.9, 2.1) for i in range(5)] + [_outer("odd", "window", 0.95, 0.9, 2.1)]
    notes = []
    plan = OM.plan({"site": {}}, outer, extras, style={"family": "scandinavian"}, notes=notes)
    assert {plan[f"w{i}"]["asset"]["asset_id"] for i in range(5)} == {"m2"}        # the Scandinavian one
    assert plan["w0"]["look"]["rank"] == 0 and "scandinavian" in plan["w0"]["reason"]
    assert "odd" not in plan                                                     # not m3: one language
    param = [n for n in notes if n["kind"] == "parametric"]
    assert [n["id"] for n in param] == ["odd"] and "one door and window language" in param[0]["reason"]
    left = next(n for n in notes if n["kind"] == "left_out")
    assert "m4" in left["models"]
    # without a style the old order holds (textured, title words, proportions)
    plain = OM.plan({"site": {}}, outer, extras)
    assert plain["w0"]["asset"]["asset_id"] in ("m1", "m2") and plain["w0"]["look"] is None


def test_a_family_takes_its_member_that_fits_and_the_dark_panelled_door_ranks_last():
    extras = [_door(1, "Valdi - Folding Sliding Door - 3 Door White", ("modern", "minimal"), w=2.3, h=2.1),
              _door(2, "Valdi - Folding Sliding Door - 4 Door Timber", ("modern", "scandinavian"), w=3.0, h=2.1),
              _door(3, "Front Door", ("modern", "classic", "minimal"), w=0.95, h=2.05),
              _door(4, "Modern Single Door", ("modern", "minimal"), w=1.07, h=2.44)]
    b = {"site": {"entrances": [{"door_id": "e", "main": True}]}}
    outer = [_outer("g1", "door", 2.3, 0.0, 2.1), _outer("g2", "door", 3.0, 0.0, 2.1),
             _outer("e", "door", 0.9, 0.0, 2.1), _outer("d1", "door", 0.8, 0.0, 2.1)]
    plan = OM.plan(b, outer, extras, style={"family": "scandinavian"})
    assert plan["g1"]["asset"]["asset_id"] == "m1" and plan["g2"]["asset"]["asset_id"] == "m2"
    assert plan["g1"]["family"] == plan["g2"]["family"]
    assert plan["d1"]["asset"]["asset_id"] == "m4"                    # not the partly classic "Front Door"


# --------------------------------------------------------------------------
# the panes of a model (B5): glazing bars, patterned glass
# --------------------------------------------------------------------------

def _glb(path, materials, prims):
    """A GLB with one mesh: ``prims`` = [(material index, [(x0, z0, x1, z1, y, flip)])] quads in the x-z plane."""
    binc = bytearray()
    views, accs, out = [], [], []
    for mat, quads in prims:
        pos, idx = [], []
        for x0, z0, x1, z1, y, flip in quads:
            b = len(pos)
            pos += [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
            idx += [b, b + 2, b + 1, b, b + 3, b + 2] if flip else [b, b + 1, b + 2, b, b + 2, b + 3]
        off = len(binc)
        binc += struct.pack(f"<{len(pos) * 3}f", *[c for p in pos for c in p])
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(pos) * 12})
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(pos), "type": "VEC3",
                     "min": [min(p[k] for p in pos) for k in range(3)], "max": [max(p[k] for p in pos) for k in range(3)]})
        off = len(binc)
        binc += struct.pack(f"<{len(idx)}I", *idx)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(idx) * 4})
        accs.append({"bufferView": len(views) - 1, "componentType": 5125, "count": len(idx), "type": "SCALAR"})
        out.append({"attributes": {"POSITION": len(accs) - 2}, "indices": len(accs) - 1, "material": mat})
    doc = {"asset": {"version": "2.0"}, "materials": materials, "meshes": [{"primitives": out}],
           "nodes": [{"mesh": 0, "translation": [5.0, 0.0, 0.0]}], "scenes": [{"nodes": [0]}], "scene": 0,
           "buffers": [{"byteLength": len(binc)}], "bufferViews": views, "accessors": accs}
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    binc += b"\0" * (-len(binc) % 4)
    total = 12 + 8 + len(js) + 8 + len(binc)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                     + struct.pack("<II", len(binc), 0x004E4942) + bytes(binc))
    return path


def _lattice(cols, rows, w=1.8, h=2.1, bar=0.06, twins=True):
    quads = []
    lw, lh = (w - bar * (cols + 1)) / cols, (h - bar * (rows + 1)) / rows
    for i in range(cols):
        for j in range(rows):
            x0, z0 = bar + i * (lw + bar), bar + j * (lh + bar)
            quads.append((x0, z0, x0 + lw, z0 + lh, 0.0, False))
            if twins:                                    # a SketchUp pane: its back face at the same place
                quads.append((x0, z0, x0 + lw, z0 + lh, 0.0, True))
    return quads


def test_glazing_bars_and_patterned_glass_are_read_from_the_file(tmp_path):
    frame = [(0.0, 0.0, 1.8, 2.1, 0.03, False)]
    mats = [{"name": "Frame_dark"}, {"name": "Glass"}]
    french = OM.glb_panes(_glb(tmp_path / "f.glb", mats, [(0, frame), (1, _lattice(4, 4))]))
    assert french["lites"] == 16 and french["per_m2"] == pytest.approx(16 / (1.8 * 2.1), rel=1e-3)
    assert not french["patterned"]
    clear = OM.glb_panes(_glb(tmp_path / "c.glb", mats, [(0, frame), (1, _lattice(2, 1))]))
    assert clear["lites"] == 2
    pat = OM.glb_panes(_glb(tmp_path / "p.glb", [{"name": "Frame"}, {"name": "Glass_pattern",
                                                                       "pbrMetallicRoughness": {"baseColorTexture":
                                                                                                {"index": 0}}}],
                            [(0, frame), (1, _lattice(1, 1))]))
    assert pat["patterned"] and pat["lites"] == 1
    assert OM.glb_panes(tmp_path / "missing.glb") is None
    light = OM.look_of({"family": "modern"})
    e = _door(1, "French Door", ("modern",), w=1.8, h=2.1)
    assert OM.look_fit(e, light, french, "glazed_door")[0] is None
    assert OM.look_fit(e, light, clear, "glazed_door")[0] == 0
    assert OM.look_fit(e, light, pat, "glazed_door")[0] is None
    assert OM.look_fit(e, OM.look_of({"family": "classic"}), french, "glazed_door")[0] is not None   # bars allowed


def test_the_plan_skips_the_lattice_door_with_the_files(tmp_path):
    frame = [(0.0, 0.0, 1.8, 2.1, 0.03, False)]
    mats = [{"name": "Frame"}, {"name": "Glass"}]
    (tmp_path / "models").mkdir()
    _glb(tmp_path / "models" / "f.glb", mats, [(0, frame), (1, _lattice(4, 4))])
    _glb(tmp_path / "models" / "s.glb", mats, [(0, frame), (1, _lattice(2, 1))])
    french = dict(_door(1, "French Door", ("modern", "industrial"), w=1.8, h=2.1), glb="models/f.glb")
    slider = dict(_door(2, "Sliding Double Door", ("minimal",), w=2.4, h=2.1), glb="models/s.glb")
    outer = [_outer("g", "door", 2.15, 0.0, 2.1)]
    plan = OM.plan({"site": {}}, outer, [french, slider], style={"family": "scandinavian"}, assets_dir=tmp_path)
    assert plan["g"]["asset"]["asset_id"] == "m2"


# --------------------------------------------------------------------------
# the style's finish on the model; the back of a pane is glass (B3, B5)
# --------------------------------------------------------------------------

class _Img:
    image = object()
    type = "TEX_IMAGE"


class _Tree:
    def __init__(self, textured):
        self.nodes = [_Img()] if textured else []


class _Mat:
    def __init__(self, name, textured=False):
        self.name = name
        self.use_nodes = textured
        self.node_tree = _Tree(textured) if textured else None


def test_textured_frames_and_large_metals_take_the_finish_hardware_stays():
    wood, alu, handle, small, glass = (_Mat("Wood_dark", True), _Mat("Aluminium_frame"), _Mat("Door_Handle"),
                                       _Mat("metal_hinge_plate"), _Mat("Glass_clear"))
    scene_glass, finish = _Mat("scene_glass"), _Mat("painted_metal_white")
    mats = [wood, alu, handle, small, glass]
    got = OB.material_map(mats, scene_glass, finish, [0.5, 0.3, 0.01, 0.01, 0.18])
    assert got == [finish, finish, handle, small, scene_glass]
    assert OB.material_map(mats, scene_glass, finish) == [wood, alu, handle, small, scene_glass]   # the old rule
    assert OB.material_map(mats, scene_glass, None, [0.5, 0.3, 0.01, 0.01, 0.18])[0] is wood
    verts = [(0, 0, 0), (2, 0, 0), (2, 0, 1), (0, 0, 1), (0, 0, 2), (1, 0, 2), (1, 0, 3), (0, 0, 3)]
    shares = OB.material_shares(2, verts, [[0, 1, 2, 3], [4, 5, 6, 7]], [0, 1])
    assert shares == pytest.approx([2 / 3, 1 / 3])


def test_the_opaque_back_of_a_pane_is_glass():
    t = 0.0002                                            # furniture.separate_twins moved each copy this far
    verts = [(0, -t, 0), (1, -t, 0), (1, -t, 1), (0, -t, 1),            # the pane, facing -y
             (0, t, 0), (0, t, 1), (1, t, 1), (1, t, 0),                # its back, facing +y, another material
             (2, 0, 0), (3, 0, 0), (3, 0, 1), (2, 0, 1),                # a frame face elsewhere
             (0, 0.05, 0), (0, 0.05, 1), (1, 0.05, 1), (1, 0.05, 0)]    # a face 5 cm behind the pane: not its back
    faces = [[0, 3, 2, 1], [4, 7, 6, 5], [8, 11, 10, 9], [12, 15, 14, 13]]
    assert OB.glass_twins(verts, faces, [True, False, False, False]) == {1}
    assert OB.glass_twins(verts, faces, [False, False, False, False]) == set()
    assert OB.glass_faces([_Mat("Glass"), _Mat("Frame")], [0, 1, None, 1]) == [True, False, False, False]


# --------------------------------------------------------------------------
# guards around the floor openings (C)
# --------------------------------------------------------------------------

WALL_L = {"id": "wl", "start": [-0.1, -1.0], "end": [-0.1, 4.0], "thickness": 0.2}     # face at x = 0


def test_void_guard_runs_skip_the_wall_and_the_arrival_and_meet_at_the_corner():
    void = [(0.0, 0.0), (2.0, 0.0), (2.0, 3.0), (0.0, 3.0)]
    arrival = [((0.0, 3.0), (1.0, 3.0))]                   # the stair comes up on the left half of the top edge
    runs = D.void_guard_runs(void, [WALL_L], arrival)
    inset = D.GUARD["inset"]
    by_side = {}
    for p, q in runs:
        if abs(p[1] - q[1]) < 1e-9:
            by_side.setdefault("y=%.2f" % p[1], []).append((p, q))
        else:
            by_side.setdefault("x=%.2f" % p[0], []).append((p, q))
    assert set(by_side) == {f"y={-inset:.2f}", f"x={2 + inset:.2f}", f"y={3 + inset:.2f}"}
    (p, q), = by_side[f"y={-inset:.2f}"]                   # the bottom edge: from the wall face to the corner
    assert min(p[0], q[0]) == pytest.approx(D.GUARD["wall_body"], abs=0.002)
    assert max(p[0], q[0]) == pytest.approx(2 + inset)
    (p, q), = by_side[f"x={2 + inset:.2f}"]                # the right edge, mitred at both corners
    assert sorted((p[1], q[1])) == pytest.approx([-inset, 3 + inset])
    (p, q), = by_side[f"y={3 + inset:.2f}"]                # the top edge: only the right half (the arrival is open)
    assert sorted((p[0], q[0]))[0] == pytest.approx(1.0 + D.GUARD["step"], abs=0.002)
    assert not any(abs(p[0] + inset) < 1e-6 and abs(q[0] + inset) < 1e-6 for p, q in runs)   # nothing on the wall
    metal, glass, again = D.void_guards(void, [WALL_L], arrival, 3.0, "glass_posts")
    assert again == runs and metal and glass
    top = max(v[2] for verts, _f in metal + glass for v in verts)
    assert top == pytest.approx(3.0 + D.GUARD["height"], abs=0.005)
    assert D.void_guard_runs(void, [WALL_L], [((0.0, 0.0), (2.0, 0.0)), ((0.0, 3.0), (2.0, 3.0)),
                                              ((2.0, 0.0), (2.0, 3.0))]) == []


def test_a_gallery_void_without_a_stair_is_guarded_all_round():
    runs = D.void_guard_runs([(0, 0), (3, 0), (3, 2), (0, 2)], [], [])
    assert len(runs) == 4
    length = sum(math.dist(p, q) for p, q in runs)
    assert length == pytest.approx(2 * (3 + 2) + 8 * D.GUARD["inset"])


def _straight(rise=3.0):
    piece = {"id": "s", "type": "stair", "footprint": {"center": [0.5, 1.5], "size": [1.0, 3.0], "rotation_deg": 0.0},
             "stair": {"flights": [{"start": [0.5, 0.0], "end": [0.5, 2.8], "width": 1.0, "lines": 17}],
                       "landing": None, "direction": [0.0, 1.0]}}
    return P.stair_plan(piece, rise, 2.8, rise - 0.005)


def test_the_balustrade_runs_to_the_top_when_the_stair_comes_up_through_the_floor():
    plan = dict(_straight(), balustrade="bars")
    cut = [p for p in P.stair_parts(plan) if p["role"] == "rail"]
    full = [p for p in P.stair_parts(dict(plan, rail_limit=3.0 + P.STAIR_RAIL_HEIGHT + 0.03)) if p["role"] == "rail"]
    top_cut = max(v[2] for p in cut for v in p["verts"]) if cut else 0.0
    top_full = max(v[2] for p in full for v in p["verts"])
    assert top_cut <= plan["cap_z"] - P.STAIR_CAP_CLEARANCE + 1e-6
    assert top_full == pytest.approx(3.0 + P.STAIR_RAIL_HEIGHT - 0.05 * plan["riser_m"] / plan["flights"][0]["going"],
                                     abs=0.01)


def test_an_apron_closes_the_gap_between_the_top_step_and_the_floor():
    plan = _straight()
    hole = [(0.0, 0.0), (1.0, 0.0), (1.0, 3.1), (0.0, 3.1)]              # the opening goes on 0.30 m past the top
    assert P.arrival_apron(plan, [hole]) == pytest.approx(0.30)
    assert P.arrival_apron(plan, [[(0.0, 0.0), (1.0, 0.0), (1.0, 2.8), (0.0, 2.8)]]) == 0.0     # meets the top
    assert P.arrival_apron(plan, [[(0.0, 0.0), (1.0, 0.0), (1.0, 5.0), (0.0, 5.0)]]) == 0.0     # a gallery
    parts = P.stair_parts(dict(plan, top_apron=0.30))
    apron = [p for p in parts if p.get("apron")]
    assert len(apron) == 1
    ys = [v[1] for v in apron[0]["verts"]]
    zs = [v[2] for v in apron[0]["verts"]]
    assert min(ys) == pytest.approx(2.8) and max(ys) == pytest.approx(3.1)
    assert max(zs) == pytest.approx(3.0 - P.STAIR_APRON_UNDER_M)
    slots = P.stair_face_slots(parts)
    assert len(slots) == sum(len(p["faces"]) for p in parts)


@pytest.mark.skipif(not REAL06.is_file(), reason="no committed real06 building")
def test_real06_upper_floor_guards_its_stair_void():
    from wenart.blender import build as BU
    from wenart.blender import shell as SH

    prep = BU.prepare(json.loads(REAL06.read_text(encoding="utf-8")), "base", None, style_family="scandinavian")
    vb = prep["building"]
    l0 = next(lv for lv in vb["levels"] if lv["id"] == "L0")
    l1 = next(lv for lv in vb["levels"] if lv["id"] == "L1")
    stair = next(i["plan"] for i in SH.plan_stairs(vb, l0, slab_void=True) if i["plan"])
    # 27 Oct 2026 (stair_access, the architect's K4): the stair read from the L1 plan arrives in the hall's south part
    # and its opening ends at its last riser: no apron any more (the 0.30 m apron led onto the cut-off strip)
    assert prep["stair_access"]["fixed"] == 1
    assert not stair.get("top_apron") and stair["rail_limit"] > stair["rise_m"]
    voids = prep["slabs"]["by_level"]["L1"]["under"]["voids"]
    guards = SH.floor_void_guards(vb, l1, voids)
    # the free edges of the opening are now the edges of the floor over the first flight's low steps (1.2 + 0.45 m)
    assert len(guards) == 1 and guards[0]["arrives_from"] == ["f_L0_001"] and guards[0]["length_m"] > 1.2
    arrival = SH.stair_arrival_edges(vb, l1)[0]
    for p, q in guards[0]["runs"]:                     # no guard across the top of the stair
        mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
        assert not (min(arrival["p"][0], arrival["q"][0]) <= mid[0] <= max(arrival["p"][0], arrival["q"][0])
                    and abs(mid[1] - arrival["p"][1]) < 0.2)
