"""31 Oct 2026 (user on real04 run 20261030-181158-full): "Better bedding needed here" (every dressed bed had two
pillows lying flat and no shams: "no headboard the rays find", its head against the wall), "bedding on this sofa could
have been a lot better not just pillows maybe include some comfortals" (a small cream sheet on the white corner sofa),
"This bag requires a lot more detail and a lot better texture for example black leather like suite" (a grey box with tan
straps). The rules: the wall behind a bed's head holds its shams and pillows; a layered, coordinated set (a coloured
duvet under a white top sheet, the room's cushion colours); a folded throw over a sofa's arm or across a seat end; a
black (or style-coloured) leather holdall with stitching, keepers, buckles, a pad and feet. CPU only: synthetic beds,
sofas and rooms on the pure ray caster (``rest.MeshCaster``)."""
from __future__ import annotations

import copy
import math
from collections import Counter

import numpy as np
import pytest

import _m11_room as M
from wenart.blender import bedding_parts as BP
from wenart.blender import geom2d
from wenart.blender import holdall as HD
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import seat_throw as ST
from wenart.blender import textiles as T
from wenart.style import colours as COL

BED_C = (2.5, 3.0)                   # a 1.6 x 2.0 m bed, its head on the north wall face (y = 4.0) of the 5 x 4 m room
HOST = {"center": list(BED_C), "size": [1.6, 2.0], "rotation_deg": 0.0}
SOFT = ("pillow", T.SHAM_ROLE, T.ACCENT_ROLE, T.LUMBAR_ROLE)
STYLE = {"family": "modern", "decor": {"cushion_colours": ["cream", "mustard"], "throw_colours": []},
         "colours": {"cushions": ["cream", "mustard"], "sofa": ["light grey"]},
         "furniture": {"by_type": {"sofa_corner": {"fabric_colour": "light grey"}}}}


def platform_caster(center=BED_C, top: float = 0.5) -> R.MeshCaster:
    """A platform bed without a headboard (the real04 models the rays found none on)."""
    v, f = geom2d.merge([geom2d.box((center[0], center[1], top / 2.0), (1.6, 2.0, top))])
    return R.MeshCaster(v, f)


def bed_piece(center=BED_C, rotation: float = 0.0, pid: str = "f_L0_001"):
    return M.fp(pid, "bed_double", center, (1.6, 2.0), rotation=rotation)


def room(*pieces, window=None, sill=0.9) -> dict:
    return M.building(w=5.0, h=4.0, room_type="bedroom", window=window, sill=sill, furniture=list(pieces))


def mesh_of(parts) -> tuple[list, list]:
    verts, faces = [], []
    for p in parts:
        off = len(verts)
        verts += [tuple(v) for v in p["verts"]]
        faces += [[i + off for i in f] for f in p["faces"]]
    return verts, faces


def wall_caster(head: dict) -> R.MeshCaster:
    return R.MeshCaster(head["verts"], head["faces"])


# --------------------------------------------------------------------------------------------- the bed's head wall
def test_the_wall_behind_a_beds_head_is_found_as_its_headboard():
    bed = bed_piece()
    head = BP.head_wall(bed, room(bed), 0.0, 0.5)
    assert head is not None and head["by"] == ["w_n"] and head["rule"] == BP.HEAD_WALL_RULE
    assert head["face_y"] == pytest.approx(1.0) and head["gap_m"] == pytest.approx(0.0) and head["share"] == 1.0
    v = np.asarray(head["verts"])
    assert v[:, 1].min() == pytest.approx(4.0) and v[:, 2].min() == pytest.approx(0.0)
    assert v[:, 2].max() == pytest.approx(0.5 + BP.HEAD_WALL_ABOVE_M)                  # a metre over the mattress
    assert v[:, 0].min() >= BED_C[0] - 0.8 - 1e-9 and v[:, 0].max() <= BED_C[0] + 0.8 + 1e-9
    # a bed pulled 10 cm off the wall still has it; 30 cm off, none
    assert BP.head_wall(bed_piece(center=(2.5, 2.9)), room(), 0.0, 0.5)["gap_m"] == pytest.approx(0.1)
    assert BP.head_wall(bed_piece(center=(2.5, 2.7)), room(), 0.0, 0.5) is None
    # a turned bed (its front to the west, its head on the east wall) finds the east wall, a bed in the middle none
    east = bed_piece(center=(4.0, 2.0), rotation=270.0)
    assert BP.head_wall(east, room(east), 0.0, 0.5)["by"] == ["w_e"]
    assert BP.head_wall(bed_piece(center=(2.5, 2.0)), room(), 0.0, 0.5) is None


def test_the_head_wall_ends_under_a_window_sill_and_finds_the_feature_panel():
    bed = bed_piece()
    head = BP.head_wall(bed, room(bed, window=(2.5, 1.0), sill=0.9), 0.0, 0.5)
    wall = wall_caster(head)

    def face_at(x: float, z: float):
        return wall.ray((x, 3.5, z), (0.0, 1.0, 0.0), 1.0)
    assert face_at(2.5, 0.8) is not None and face_at(2.5, 1.0) is None                # under the sill only
    assert face_at(1.9, 1.4) is not None and face_at(3.1, 1.4) is not None            # full height beside it
    plain = BP.head_wall(bed, room(bed), 0.0, 0.5)
    # the room's feature panel on that wall (3 cm in front of it) stands at the head; a panel on a side wall does not
    assert BP.near_head(bed, (0.0, 3.97, 0.0), (5.0, 4.0, 2.7), plain)
    assert not BP.near_head(bed, (4.97, 0.0, 0.0), (5.0, 4.0, 2.7), plain)


def test_a_platform_bed_against_a_wall_gets_shams_standing_pillows_and_a_cushion():
    bed = bed_piece()
    head = BP.head_wall(bed, room(bed), 0.0, 0.5)
    spec = BP.family_spec("modern")[0]
    colours = BP.scheme_colours(STYLE, against=spec["pillows"]["colour"])
    plan = T.bedding_set(platform_caster(), HOST, 0.0, spec, None, colours=colours, head_caster=wall_caster(head))
    rec = plan["record"]
    assert rec["set"] == {"euro_shams": 2, "pillows": 2, "accent": 0, "lumbar": 1} and rec["explained"] == {}
    assert rec["pillows_upright"] is True and rec["head_wall"] is True and rec["head"]["headboard"] is True
    assert rec["lumbar"]["colour"] == "mustard"                                        # the brief's, against white
    got = Counter(p["role"] for p in plan["parts"])
    assert sum(got[r] for r in SOFT) == 5 <= BP.PIECES_MAX["double"]
    # the turned-down band is the white top sheet over the greige linen duvet
    band = [p for p in plan["parts"] if p["role"] == "turndown"]
    duvet = [p for p in plan["parts"] if p["role"] == "duvet"]
    assert band and band[0]["key"] == BP.textile_key("cotton") and band[0]["colour"] == "white"
    assert duvet[0]["key"] == BP.textile_key("linen") and duvet[0]["colour"] == "greige"
    assert rec["sheet"] == {"look": "cotton", "colour": "white"}
    # every standing piece rests on the bed, the wall and the others, and never goes into the wall
    wall = wall_caster(head)
    for p in [q for q in plan["parts"] if q["role"] in SOFT]:
        others = mesh_of([q for q in plan["parts"] if q is not p and q["role"] != "duvet"])
        host = R.MultiCaster([platform_caster(), wall, R.MeshCaster(*others)])
        arr = np.asarray(p["verts"])
        lo, hi = arr.min(axis=0), arr.max(axis=0)
        foot = {"center": [float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2)],
                "size": [float(hi[0] - lo[0]) * 0.8, float(hi[1] - lo[1]) * 0.5], "rotation_deg": 0.0}
        m = R.measure_rest(p["verts"], p["faces"], host, foot, True)
        assert R.rest_ok(m)[0], (p["role"], m)
        assert hi[1] <= 4.0 + 1e-6                                                     # the wall's face
    # without the wall the same bed keeps the set of before (no headboard: no shams), said why
    bare = T.bedding_set(platform_caster(), HOST, 0.0, spec, None, colours=colours)
    assert bare["record"]["euro_shams"] == 0 and "headboard" in bare["record"]["explained"]["euro_shams"]
    assert bare["record"]["head_wall"] is False


def test_a_family_without_a_lumbar_shows_one_accent_cushion_in_front_of_the_shams():
    for fam in ("japandi", "minimal", "modern minimal"):
        spec = BP.family_spec(fam)[0]
        assert spec["lumbar"] is None
        assert BP.counts(spec, 1.6) == {"euro_shams": 2, "pillows": 2, "accent": 1, "lumbar": 0}
    spec = BP.family_spec("japandi")[0]
    bed = bed_piece()
    plan = T.bedding_set(platform_caster(), HOST, 0.0, spec, None,
                         head_caster=wall_caster(BP.head_wall(bed, room(bed), 0.0, 0.5)))
    rec = plan["record"]
    assert rec["set"] == {"euro_shams": 2, "pillows": 2, "accent": 1, "lumbar": 0} and rec["explained"] == {}
    (acc,) = [p for p in plan["parts"] if p["role"] == T.ACCENT_ROLE]
    x = np.asarray(acc["verts"])[:, 0]
    assert abs(float(x.mean()) - BED_C[0]) < 0.03                                     # centred in front


def test_every_family_makes_a_layered_coordinated_bed():
    for fam, row in BP.FAMILY_BEDDING.items():
        sheet = row["sheet"]
        assert sheet["look"] in BP.LOOKS and COL.known(sheet["colour"]), fam
        assert row["duvet"]["colour"] != "white", fam                                  # not all white
        assert row["duvet"]["colour"] != sheet["colour"], fam                          # the sheet shows over it
        assert row["shams"]["colour"] != row["pillows"]["colour"], fam
        assert row["duvet"]["wrinkle_m"] >= 0.008, fam
    assert BP.family_spec("modern")[0]["duvet"]["look"] == "linen"                     # the scan's weave


def test_the_schemes_cushion_colours_follow_the_brief_and_stand_out_from_the_pillows():
    assert BP.scheme_colours(STYLE) == ["cream", "mustard"]
    assert BP.scheme_colours(STYLE, against="white") == ["mustard", "cream"]
    assert BP.scheme_colours({"decor": {"cushion_colours": ["Sage", "no such colour"], "throw_colours": ["rust"]}}) \
        == ["sage", "rust"]
    assert BP.scheme_colours(None) == [] and BP.scheme_colours({}) == []


def test_the_bedding_cloth_creases_but_the_sofa_upholstery_does_not():
    from wenart.blender import materials as MAT

    assert BP.crease_of("colour_textile_linen") == BP.CREASE_BY_LOOK["linen"] > BP.crease_of("textile_cotton") > 0
    assert BP.crease_of("colour_runner_knit") == BP.CREASE_BY_LOOK["knit"]
    assert BP.crease_of("colour_textile_houndstooth") == BP.CREASE_BY_LOOK[BP.PATTERN_WEAVE]   # as its weave
    assert BP.crease_of("textile_boucle") is None                                      # its loops, no creases
    for key in ("fabric", "colour_fabric", "duvet", "bedding", "leather", "towel_band"):
        assert BP.crease_of(key) is None, key                                          # never the sofa's fabric
    assert MAT.crease_suffix(0.45) == "__crease45" and MAT.crease_suffix(None) == ""
    assert set(BP.CREASE_BY_LOOK) == set(BP.LOOKS)


def test_a_bed_we_build_takes_the_family_set_instead_of_its_thin_bedding():
    from wenart.blender import furniture as F

    piece = bed_piece()
    parts = P.build_parts("bed_double", 1.6, 2.0, 0.5, piece=piece)
    kept, dressed = F.parametric_bed_parts(parts, piece, True)
    roles = Counter(p["role"] for p in kept)
    assert dressed and roles["mattress"] == 1 and not (roles["pillow"] or roles["duvet"] or roles["turndown"])
    assert any(p["role"] in ("panel", "back") for p in kept)                           # its headboard stays
    assert F.parametric_bed_parts(parts, piece, False) == (parts, False)               # not dressed: as before
    sofa_parts = P.build_parts("sofa", 2.0, 0.9, 0.8, piece=sofa())
    assert F.parametric_bed_parts(sofa_parts, sofa(), True) == (sofa_parts, False)
    assert F.needs_dressing(piece, {"method": "parametric (fallback: x)", "dress_bedding": True})
    assert not F.needs_dressing(piece, {"method": "parametric (fallback: x)"})
    assert not F.needs_dressing(sofa(), {"dress_bedding": True})


def test_the_decor_stage_records_the_scheme_and_the_head_wall():
    from wenart.furniture import bedding as BG

    b = room(bed_piece())
    BG.plan_beds(b, STYLE)
    bl = b["furniture"][0]["bedding_layers"]
    assert bl["cushion_colours"] == ["mustard", "cream"]
    assert bl["head_wall"]["by"] == ["w_n"] and "verts" not in bl["head_wall"]
    assert bl["set"]["sheet"] == {"look": "cotton", "colour": "white"}


# ------------------------------------------------------------------------------------------------- the sofa throw
SOFA_C, SOFA_W, SOFA_D = (3.0, 2.0), 2.2, 0.95
SEAT_Z, ARM_Z = 0.44, 0.60


def sofa_caster(arms=("left", "right"), rot: float = 0.0, center=SOFA_C) -> R.MeshCaster:
    """A sofa: a base, one seat cushion (top 0.44 m), the back cushions, and arms (top 0.60 m, 20 cm wide)."""
    cx, cy = center
    inner = SOFA_W - 0.40 if arms else SOFA_W
    parts = [geom2d.box((cx, cy, 0.21), (SOFA_W, SOFA_D, 0.30)),
             geom2d.box((cx, cy - 0.05, 0.40), (inner, SOFA_D - 0.25, 0.08)),
             geom2d.box((cx, cy + SOFA_D / 2 - 0.12, 0.62), (inner, 0.24, 0.52))]
    for side in arms:
        s = 1 if side == "right" else -1
        parts.append(geom2d.box((cx + s * (SOFA_W / 2 - 0.10), cy, 0.33), (0.20, SOFA_D, 0.54)))
    v, f = geom2d.merge(parts)
    if rot:
        a = math.radians(rot)
        arr = np.asarray(v) - np.array([cx, cy, 0.0])
        arr = np.stack([math.cos(a) * arr[:, 0] - math.sin(a) * arr[:, 1],
                        math.sin(a) * arr[:, 0] + math.cos(a) * arr[:, 1], arr[:, 2]], axis=1) + [cx, cy, 0.0]
        v = [tuple(p) for p in arr.tolist()]
    return R.MeshCaster(v, f)


def sofa(rot: float = 0.0, ftype: str = "sofa", center=SOFA_C) -> dict:
    return {"id": "f_L0_010", "type": ftype, "room_id": M.ROOM_ID, "level_id": "L0",
            "footprint": {"center": list(center), "size": [SOFA_W, SOFA_D], "rotation_deg": rot}}


def throw_on(host: dict, look: dict, side_x: float = 0.8) -> dict:
    fp = host["footprint"]
    c = R.to_world(fp["center"], fp["rotation_deg"], side_x, 0.0)
    return {"id": "dec_L0_50", "type": "throw", "host_id": host["id"], "center": [c[0], c[1]],
            "size": [0.5, 0.45, 0.05], "colour": look["colour"], "seat_throw": look}


def local(points, host: dict) -> np.ndarray:
    fp = host["footprint"]
    return BP.to_local_arr(fp["center"], fp["rotation_deg"], points)


def test_the_seat_throw_look_stands_out_from_the_sofa():
    look = ST.throw_look("modern", "light grey", ["cream", "mustard"], side="right")
    assert look["look"] == "knit" and look["colour"] == "mustard" and look["drape"] == "arm"     # cream is too close
    assert look["side"] == "right" and look["rule"] == ST.RULE and "comfortals" in look["why"]
    assert ST.throw_look("modern", "light grey", [])["colour"] == "charcoal"           # the family's dark contrast
    assert ST.throw_look("modern", "charcoal", ["black"])["colour"] == "cream"         # ... its light one
    assert ST.throw_look("modern", None, ["sage"])["colour"] == "sage"                 # no sofa colour: the item's
    assert ST.throw_look("scandinavian", "white", [])["fringe"] is True
    assert ST.throw_look("baroque", "white", [])["family"] == ST.DEFAULT_FAMILY
    for row in ST.FAMILY_SEAT_THROW.values():
        assert row["look"] in BP.LOOKS and all(COL.known(c) for c in row["contrast"]) and row["why"]
    assert ST.colour_distance("light grey", "cream") < ST.CONTRAST_DE < ST.colour_distance("light grey", "mustard")
    # the seat's colour: its design's, then the style's for its type, then the brief's sofa colour
    host = sofa(ftype="sofa_corner")
    assert ST.sofa_colour(host, STYLE) == "light grey"
    assert ST.sofa_colour(dict(host, design={"fabric_colour": "navy"}), STYLE) == "navy"
    assert ST.sofa_colour(sofa(), {"colours": {"sofa": ["olive"]}}) == "olive"
    assert ST.sofa_colour(sofa(), {}) is None


def test_a_throw_folded_over_the_arm_rests_over_it_and_falls_onto_the_seat():
    host = sofa()
    look = ST.throw_look("modern", "light grey", ["cream", "mustard"], side="right")
    caster = sofa_caster()
    arm = ST.measure_arm(caster, host["footprint"], "right", SEAT_Z)
    assert arm["top_z"] == pytest.approx(ARM_Z) and arm["width"] == pytest.approx(0.2, abs=0.02)
    assert arm["x_in"] == pytest.approx(0.9, abs=0.02) and arm["x_out"] == pytest.approx(1.1, abs=0.01)
    plan = R.plan_throw(throw_on(host, look), host, caster, 0.0)
    assert "not_rested" not in plan, plan.get("not_rested")
    w = plan["weave"]
    assert w["drape"] == "arm" and w["side"] == "right" and w["look"] == "knit" and w["rule"] == ST.RULE
    assert R.rest_ok(plan["rest"])[0] and plan["rest"]["penetration_m"] == 0.0
    cloth = local(plan["parts"][0]["verts"], host)
    assert plan["parts"][0]["key"] == BP.textile_key("knit")
    outer = cloth[cloth[:, 0] > 1.1]                                                    # outside the arm
    assert len(outer) and outer[:, 2].min() == pytest.approx(ARM_Z - ST.ARM_DROP_M, abs=0.03)
    inner = cloth[cloth[:, 0] < 0.9]                                                    # inside, over the seat
    assert len(inner) and inner[:, 2].min() >= SEAT_Z - 1e-6 and inner[:, 2].min() < SEAT_Z + 0.03
    assert cloth[:, 2].max() == pytest.approx(ARM_Z + T.CLOTH_OFFSET_M + ST.THROW_T_M, abs=0.01)
    assert cloth[:, 1].min() >= -SOFA_D / 2.0 - 0.06 and cloth[:, 1].max() - cloth[:, 1].min() <= ST.THROW_W_M + 0.1
    # the left arm when the item lies on the left
    left = R.plan_throw(throw_on(host, dict(look, side=None), side_x=-0.8), host, caster, 0.0)
    assert left["weave"]["side"] == "left"


def test_an_armless_sofa_gets_the_throw_across_its_seat_end_with_its_fringe():
    host = sofa()
    look = ST.throw_look("scandinavian", "light grey", [], side="right")
    plan = R.plan_throw(throw_on(host, look), host, sofa_caster(arms=()), 0.0)
    assert "not_rested" not in plan, plan.get("not_rested")
    w = plan["weave"]
    assert w["drape"] == "seat_end" and w["fringe"] is True and w["fringe_strands"] > 20
    cloth = local(plan["parts"][0]["verts"], host)
    assert cloth[:, 2].min() == pytest.approx(SEAT_Z - ST.SEAT_DROP_M, abs=0.03)       # down the front
    assert cloth[:, 1].min() < -SOFA_D / 2.0 + 0.05
    assert cloth[:, 0].min() > 0.4 and cloth[:, 0].max() <= SOFA_W / 2.0 + 0.05       # at its right end
    fringe = [p for p in plan["parts"] if p["role"] == "fringe"]
    assert fringe and min(v[2] for p in fringe for v in p["verts"]) < SEAT_Z - ST.SEAT_DROP_M


def test_a_corner_sofa_gets_the_throw_over_the_arm_of_its_long_part():
    """An L corner sofa: the long part along the back with an arm at its left end, the chaise at the right running to
    the front (no arm there): the throw put on the chaise goes over the long part's arm, measured where its seat is."""
    cx, cy, w, d = 3.0, 2.0, 2.6, 1.6
    parts = [geom2d.box((cx, cy + 0.35, 0.21), (w, 0.9, 0.30)),                       # the long part: y -0.1 .. 0.8
             geom2d.box((cx + 0.9, cy, 0.21), (0.8, d, 0.30)),                         # the chaise: x 0.5 .. 1.3
             geom2d.box((cx + 0.1, cy + 0.23, 0.40), (2.4, 0.66, 0.08)),               # long seat (top 0.44)
             geom2d.box((cx + 0.9, cy - 0.12, 0.40), (0.8, 1.36, 0.08)),               # chaise seat
             geom2d.box((cx + 0.1, cy + 0.68, 0.62), (2.4, 0.24, 0.52)),               # back cushions
             geom2d.box((cx - 1.2, cy + 0.35, 0.33), (0.2, 0.9, 0.54))]                # the left arm (top 0.60)
    caster = R.MeshCaster(*geom2d.merge(parts))
    host = {"id": "f_L0_011", "type": "sofa_corner", "footprint": {"center": [cx, cy], "size": [w, d],
                                                                     "rotation_deg": 0.0}}
    assert ST.measure_arm(caster, host["footprint"], "right", SEAT_Z) is None             # the chaise end: no arm
    arm = ST.measure_arm(caster, host["footprint"], "left", SEAT_Z)
    assert arm is not None and arm["top_z"] == pytest.approx(ARM_Z) and arm["y_front"] > -0.15
    look = ST.throw_look("modern", "light grey", ["mustard"], side="right")
    plan = R.plan_throw(throw_on(host, look, side_x=0.9), host, caster, 0.0)
    assert "not_rested" not in plan and plan["weave"]["drape"] == "arm" and plan["weave"]["side"] == "left"


def test_a_turned_sofa_gets_the_same_throw():
    look = ST.throw_look("modern", "light grey", ["mustard"], side="right")
    plans = []
    for rot in (0.0, 90.0):
        host = sofa(rot)
        plan = R.plan_throw(throw_on(host, look), host, sofa_caster(rot=rot), 0.0)
        assert "not_rested" not in plan
        plans.append(local(plan["parts"][0]["verts"], host))
    for f in (np.min, np.max):                                                          # the same drape in its frame
        assert np.allclose(f(plans[0], axis=0), f(plans[1], axis=0), atol=0.01)


def test_the_decor_stage_dresses_every_seat_throw_and_the_build_falls_back():
    from wenart.blender import furniture as F
    from wenart.furniture import dressing as DR

    host = sofa(ftype="sofa_corner")
    bed = bed_piece(center=(1.0, 1.5), pid="f_L0_002")
    b = M.building(room_type="living", window=None, furniture=[host, bed])
    seat_throw = {"id": "dec_L0_60", "type": "throw", "host_id": host["id"], "room_id": M.ROOM_ID, "level_id": "L0",
                  "center": [SOFA_C[0] - 0.8, SOFA_C[1]], "size": [0.5, 0.45, 0.05], "colour": "cream"}
    bed_throw = {"id": "dec_L0_61", "type": "throw", "host_id": bed["id"], "room_id": M.ROOM_ID, "level_id": "L0",
                 "center": [1.0, 0.8], "size": [1.5, 0.5, 0.05], "colour": "cream"}
    b["decor"] += [seat_throw, bed_throw]
    notes = DR.dress_seat_throws(b, STYLE)
    st = seat_throw["seat_throw"]
    assert st["colour"] == "mustard" and seat_throw["colour"] == "mustard" and st["side"] == "left"
    assert seat_throw["colour_before_contrast"] == "cream" and len(notes) == 1
    assert "seat_throw" not in bed_throw                                                # a bed's throw keeps its pair
    assert DR.dress_seat_throws(b, STYLE) == []                                         # idempotent
    # the build: a decor output from before the rule gets the family's throw; a dressed item stays as it is
    old = {"id": "dec_L0_62", "type": "throw", "host_id": host["id"], "center": [SOFA_C[0] + 0.8, SOFA_C[1]],
           "colour": "cream"}
    got = F.seat_throw_item(old, host, "modern", STYLE)
    assert got["seat_throw"]["look"] == "knit" and got["colour"] == "mustard" and got["seat_throw"]["side"] == "right"
    assert "seat_throw" not in old
    assert F.seat_throw_item(got, host, "modern", STYLE) is got
    assert F.seat_throw_item(bed_throw, bed, "modern", STYLE) is bed_throw


# -------------------------------------------------------------------------------------------------- the leather bag
def _bag(item=None, box=(0.55, 0.30, 0.30)):
    return P.decor_parts("bag", *box, item if item is not None else {"colour": "black"})


def test_the_leather_bag_has_stitching_keepers_buckles_a_pad_and_feet():
    parts = _bag()
    roles = Counter(p["role"] for p in parts)
    assert roles["stitch"] >= 20 and sum(p.get("stitches", 0) for p in parts) >= 500     # every seam and strap
    assert roles["keeper"] == 4 and roles["buckle"] == 2 and roles["pad"] == 1 and roles["foot"] == 4
    assert roles["pull"] >= 2 and roles["piping"] == 4 and roles["handle"] == 2 and roles["ring"] == 2
    look = HD.bag_look({"colour": "black"})
    assert look["body"] == HD.LEATHER_COLOURED and look["trim"] == look["body"] and look["metal"] == HD.BRASS
    by_role = {p["role"]: p["key"] for p in parts}
    assert by_role["body"] == by_role["handle"] == by_role["piping"] == HD.LEATHER_COLOURED
    assert by_role["stitch"] == HD.THREAD and by_role["foot"] == by_role["buckle"] == HD.BRASS
    # every part is closed outwards (the stitches too: each dash a little box on the leather)
    assert all(HD.volume(p) > 0.0 for p in parts if p["role"] not in ("body", "base"))
    stitch = next(p for p in parts if p["role"] == "stitch")
    v = np.asarray(stitch["verts"]).reshape(-1, 8, 3)
    size = np.ptp(v, axis=1).max(axis=1)
    assert size.max() <= HD.BAG["stitch_len"] + 1e-3                                  # dashes, not a line
    # soft bulging panels: the body is wider at mid height than at its top, and sags between the handles
    body = np.asarray(next(p for p in parts if p["role"] == "body")["verts"])
    mid = body[np.abs(body[:, 0]) < 0.03]
    ends = body[np.abs(np.abs(body[:, 0]) - 0.18) < 0.03]
    assert np.ptp(mid[:, 1]) > np.ptp(ends[:, 1]) + 0.01
    assert mid[:, 2].max() < ends[:, 2].max() - 0.005
    # no colour named: black leather; a canvas item keeps the canvas bag with tan trim; a pale leather takes steel
    assert {p["key"] for p in _bag({})} >= {HD.LEATHER_DARK, HD.BRASS}
    assert HD.bag_look({"colour": "white"})["metal"] == HD.METAL
    assert HD.bag_look({"colour": "camel", "hardware": "steel"})["metal"] == HD.METAL
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 <= 0.55 + 1e-9 and y1 - y0 <= 0.30 + 1e-9 and z1 - z0 <= 0.30 + 1e-9 and abs(z0) < 1e-9


def test_the_bags_materials_are_real_slugs_with_the_leather_scan():
    from wenart.blender import furniture as F
    from wenart.polish import prompt as PR
    from wenart.style import vocabulary as V

    keys, _ = F.style_material_keys({})
    assert keys["leather_dark"][0] == "leather_black" and keys["brass"][0] == "metal_brass"
    assert keys["thread"][0] == "thread_waxed" and keys["leather_dark"][1] == "brown_leather"
    for key in ("leather_dark", "brass", "thread"):
        assert key in P.MATERIAL_KEYS
        slug = keys[key][0]
        assert slug in V.FLAT_COLOURS and slug in V.ROUGHNESS and slug in PR.MATERIAL_WORDS
    e = V.FURNITURE_MATERIALS["leather_black"]
    assert e["asset"] == "brown_leather" and V.albedo_mode("leather_black")[0] == "flat"
    assert max(e["flat"]) < 0.05
    assert P.part_bevel_radius(next(p for p in _bag() if p["role"] == "stitch")) == 0.0


def test_the_familys_bag_is_its_leather():
    from wenart.furniture import room_details as RD

    assert RD.tones("modern")["bag"] == "black" and RD.tones("scandinavian")["bag"] == "camel"
    item = RD._toned({"type": "bag"}, "modern")
    assert item["colour"] == "black" and HD.bag_look(item)["body"] == HD.LEATHER_COLOURED
    for fam in RD.FAMILY_TONES:
        assert COL.known(RD.tones(fam)["bag"]), fam
    kept = RD._toned({"type": "bag", "colour": "navy"}, "modern")
    assert kept["colour"] == "navy"
    assert copy.deepcopy(RD.FAMILY_TONES["modern"])["objects"] == "white"              # the other tones stay
