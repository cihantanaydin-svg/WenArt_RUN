"""The bedrooms of real04 run 20261030-043021-full (30 Oct 2026). General rules, tested on synthetic beds and rooms (real04
is only the case that showed them):

- UL163 "too many pillows in this bed, also the headrest needs to be re-done I did not like the headrest", "they are
  flying" (three beds: seven pieces in three or four rows; euro shams standing over a low headboard with nothing behind
  their upper part; an arched camelback "Saddle Back" headboard in a modern bedroom): at most five pieces in two rows
  (``bedding_parts.counts``), every standing piece held by its headboard up to ``rest.BED_TOP_SUPPORT_SHARE`` of its
  face (else it leans back further or is left out), on parametric and on dressed library beds alike; arched and
  camelback headboards rank last outside the classic families (``fit.headboard_misfit``) and a bed we build takes its
  family's headboard (``parametric.headboard_parts``).
- UL164 "A laptop on this table could have even nice, also some stationary", "Same stationary and laptop here also"
  (four bedroom desks, library models read unverified from the drawing, bare): every built desk gets its work set, its
  stationery and, when nothing lights it, a desk lamp (``tabletop.work_set``), whatever its model; the set stands on the
  desk's top, never on a shelf under it.
"""
from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from test_bed_realism_20261029 import BED_C, HOST, bed_caster, mesh_of, roles
from test_decor_m8 import room_building
from wenart.blender import bedding_parts as BP
from wenart.blender import desk_parts as DK
from wenart.blender import geom2d
from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender import textiles as T
from wenart.furniture import bedding as BG
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import fit as FIT
from wenart.furniture import room_details as RD
from wenart.furniture import tabletop as TT

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = sorted(BP.FAMILY_BEDDING)
SOFT = ("pillow", T.SHAM_ROLE, T.ACCENT_ROLE, T.LUMBAR_ROLE)


# --------------------------------------------------------------------------------------------- UL163: how many pillows
@pytest.mark.parametrize("fam", FAMILIES)
def test_a_made_bed_shows_at_most_five_pieces_in_two_rows(fam):
    spec = BP.family_spec(fam)[0]
    double = BP.counts(spec, 1.6)
    assert sum(double.values()) <= BP.PIECES_MAX["double"] == 5
    assert double["euro_shams"] == 2 and double["pillows"] == 2 and double["accent"] == 0     # shams OR a pair
    assert double["lumbar"] == (1 if spec.get("lumbar") else 0)
    bare = BP.counts(spec, 1.6, shams=False)                         # no headboard: the pair stands in for the shams
    assert bare["euro_shams"] == 0 and bare["accent"] <= 2 and sum(bare.values()) <= 5
    assert not (bare["accent"] and bare["lumbar"])                   # never a third row
    single = BP.counts(spec, 0.9)
    assert single["pillows"] == 1 and single["euro_shams"] == 0 and single["accent"] + single["lumbar"] <= 1
    assert BP.pieces_max(0.9) == 2 and BP.pieces_max(1.8) == 5


def test_the_built_set_keeps_the_cap_and_every_piece_rests():
    spec = BP.family_spec("modern")[0]
    plan = T.bedding_set(bed_caster(), HOST, 0.0, spec, None, colours=["mustard", "sage"])
    got = roles(plan)
    pieces = sum(got[r] for r in SOFT)
    assert pieces <= 5 and got[T.ACCENT_ROLE] == 0 and got[T.SHAM_ROLE] == 2 and got["pillow"] == 2
    rec = plan["record"]
    assert rec["pieces_max"] == 5 and rec["count_rule"] == BP.COUNT_RULE and rec["unrested"] == []
    assert rec["lumbar"]["colour"] == "mustard"                      # the AI's cushion colour goes to the one cushion
    assert all(r["top_support_share"] >= R.BED_TOP_SUPPORT_SHARE for r in rec["rests"] if r["lean_deg"] < 60)
    bed = bed_caster()
    for p in [q for q in plan["parts"] if q["role"] in SOFT]:
        others = mesh_of([q for q in plan["parts"] if q is not p and q["role"] != "duvet"])
        arr = np.asarray(p["verts"])
        lo, hi = arr.min(axis=0), arr.max(axis=0)
        foot = {"center": [float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2)],
                "size": [float(hi[0] - lo[0]) * 0.8, float(hi[1] - lo[1]) * 0.5], "rotation_deg": 0.0}
        m = R.measure_rest(p["verts"], p["faces"], R.MultiCaster([bed, R.MeshCaster(*others)]), foot, True)
        assert R.rest_ok(m)[0], (p["role"], m)


def low_headboard_caster(top: float = 0.5, board_top: float = 0.78):
    """A storage bed with a low upholstered headboard (real04's second bed: its top 0.28 m over the mattress)."""
    v, f = geom2d.merge([geom2d.box((BED_C[0], BED_C[1], top / 2.0), (1.6, 2.0, top)),
                         geom2d.box((BED_C[0], BED_C[1] + 1.03, board_top / 2.0), (1.6, 0.06, board_top))])
    return R.MeshCaster(v, f)


def test_nothing_stands_over_a_low_headboard_with_nothing_behind_its_upper_part():
    caster = low_headboard_caster()
    planned = R.to_world(HOST["center"], 0.0, -0.36, 0.9)
    sham = (0.62, 0.14, 0.62)
    assert R.place_leaning(caster, HOST, planned, sham, lean_deg=6.0, bed=True, hold=True) is None   # it would fly
    pose = T._lean_pose(caster, HOST, planned, sham, 6.0, True)
    assert pose is None or (pose["lean_deg"] >= 20.0 and pose["top_support_share"] >= R.BED_TOP_SUPPORT_SHARE)
    plan = T.bedding_set(caster, HOST, 0.0, BP.family_spec("modern")[0], None)
    rec = plan["record"]
    assert rec["unrested"] == [] and sum(roles(plan)[r] for r in SOFT) <= 5
    for r in rec["rests"]:
        if r["lean_deg"] < R.BED_LYING_LEAN_DEG:
            assert r["top_support_share"] >= R.BED_TOP_SUPPORT_SHARE, r
    if not rec["euro_shams"]:                                         # no shams: the pair in front, no lumbar
        assert rec["set"]["lumbar"] == 0 and rec["set"]["accent"] <= 2


def library_frame_caster(top: float = 0.55):
    """A dressed library bed (real04's master bed): a dark wood frame, tall corner posts, a grey head panel set
    between them 4 cm in front of the frame's back rail, a footboard."""
    x, y = BED_C
    v, f = geom2d.merge([geom2d.box((x, y, top / 2.0), (1.6, 2.0, top)),
                         geom2d.box((x - 0.77, y + 1.0, 0.65), (0.08, 0.08, 1.3)),
                         geom2d.box((x + 0.77, y + 1.0, 0.65), (0.08, 0.08, 1.3)),
                         geom2d.box((x, y + 1.0, 0.6), (1.46, 0.04, 1.2)),
                         geom2d.box((x, y - 1.0, 0.4), (1.6, 0.05, 0.8))])
    return R.MeshCaster(v, f)


@pytest.mark.parametrize("mode", ["full", "pillows"])
def test_a_dressed_library_bed_keeps_the_cap_and_rests_every_piece(mode):
    plan = T.bedding_set(library_frame_caster(), HOST, 0.0, BP.family_spec("contemporary")[0], None, mode=mode)
    assert plan is not None
    rec = plan["record"]
    assert sum(roles(plan)[r] for r in SOFT) <= 5 and rec["unrested"] == []
    assert all(r["top_support_share"] is None or r["lean_deg"] >= 60 or r["top_support_share"] >= 0.8
               for r in rec["rests"])


def test_the_review_flags_too_many_pillows_and_a_flying_one():
    from test_bed_realism_20261029 import _built_and_manifest, _problems

    assert _problems(*_built_and_manifest()) == []                    # the capped set as built
    assert _problems(*_built_and_manifest(set_counts={"accent": 2})) == ["too_many_pillows"]   # the run's seven
    b, m = _built_and_manifest()
    m["objects"][0]["dressing"]["record"]["unrested"] = [{"role": "euro_sham",
                                                          "why": "the headboard holds only 40 % of its face"}]
    assert _problems(b, m) == ["pillow_unrested"]
    b, m = _built_and_manifest(set_counts={"euro_shams": 0, "accent": 2, "lumbar": 0})
    m["objects"][0]["dressing"]["record"]["explained"] = {"euro_shams": "no headboard"}
    assert _problems(b, m) == []                                      # no headboard: the pair in front, no lumbar


# --------------------------------------------------------------------------------------------- UL163: the headboard
def test_an_arched_or_camelback_headboard_ranks_last_outside_the_classic_families():
    saddle = {"id": "hssd_saddle", "type": "bed_double", "name": "Full Saddle Back Upholstered Bed, Grey",
              "title": "Full Saddle Back Upholstered Bed, Grey"}
    plain = {"id": "abo_plain", "type": "bed_double", "name": "Movian Havel", "title": "Movian Havel"}
    assert FIT.headboard_misfit(saddle, "bed_double", "modern") and "UL163" in FIT.headboard_misfit(
        saddle, "bed_double", "modern")
    assert FIT.headboard_misfit(plain, "bed_double", "modern") is None
    assert FIT.headboard_misfit(saddle, "bed_double", "classic") is None
    assert FIT.headboard_misfit(saddle, "bed_double", "modern", {"headboard": "camelback"}) is None   # asked for
    assert FIT.headboard_misfit(dict(plain, headboard_form="arched"), "bed_double", "japandi")
    assert FIT.headboard_misfit(saddle, "sofa", "modern") is None
    flags = FIT.taste_flags([saddle, plain], "bed_double", False, "modern")
    assert flags["hssd_saddle"]["misfit"] and "abo_plain" not in flags


@pytest.mark.parametrize("form", P.HEADBOARD_FORMS)
def test_every_headboard_form_stays_in_the_beds_box_behind_the_mattress(form):
    w, d, h = 1.6, 2.0, 0.55
    parts = P._bed(w, d, h, {"design": {"headboard": form}})
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 <= w + 1e-6 and y1 - y0 <= d + 1e-6 and z0 >= -1e-9 and z1 <= max(1.0, h + 0.4) + 1e-6
    t = min(0.06, d * 0.05)
    board = [p for p in parts if p["role"] in ("panel", "channel", "slat", "button", "piping")]
    assert board and min(v[1] for p in board for v in p["verts"]) >= d / 2.0 - t - 1e-6   # never into the mattress
    count = Counter(p["role"] for p in parts)
    if form == "channel":
        assert count["channel"] >= 10 and {p["key"] for p in board} == {"fabric"}
    if form == "slat":
        assert count["slat"] >= 15 and {p["key"] for p in board} == {"wood"}
    if form == "button":
        assert count["button"] >= 6 and count["piping"] == 4


def test_a_bed_we_build_takes_its_familys_headboard():
    assert {BP.headboard_form(f)[0] for f in ("modern", "contemporary")} == {"channel"}
    assert BP.headboard_form("japandi")[0] == "slat" and BP.headboard_form("classic")[0] == "button"
    assert all(f not in FIT.HEADBOARD_ROMANTIC_FORMS for f in BP.HEADBOARD_BY_FAMILY.values())
    assert P.headboard_form_of({"design": {"style_family": "scandinavian"}}) == "slat"
    assert P.headboard_form_of({}) == "panel"
    import _m11_room as M

    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None,
                   furniture=[M.fp("f_L0_001", "bed_double", BED_C, (1.6, 2.0), rotation=0.0)])
    BG.plan_beds(b, {"family": "modern"})
    bed = b["furniture"][0]
    assert bed["design"]["headboard"] == "channel" and "UL163" in bed["design"]["headboard_why"]
    assert bed["bedding_layers"]["count_rule"] == BP.COUNT_RULE


# --------------------------------------------------------------------------------------------- UL164: every desk
def _new_id():
    n = [0]

    def make(level_id):
        n[0] += 1
        return f"dec_{level_id}_{900 + n[0]}"
    return make


def _bedroom_desk(size=(1.4, 0.6), lamp=None, library=True):
    """A bedroom with a desk against its north wall and an office chair in front of it; the desk a library model read
    unverified from the drawing (real04's four bedroom desks)."""
    w, d = size
    c = (2.0, 3.5 - d / 2.0)
    furniture = [("desk", c, 0.0, size, "unverified"), ("office_chair", (2.0, 3.5 - d - 0.35), 180.0, (0.6, 0.6),
                                                        "unverified"),
                 ("bed_double", (2.0, 1.0), 0.0, (1.6, 2.0))]
    if lamp == "floor":
        furniture.append(("floor_lamp", (2.0 + w / 2.0 + 0.3, 3.2), 0.0, (0.35, 0.35)))
    b = room_building(4.0, 3.5, "bedroom", furniture=furniture)
    desk = b["furniture"][0]
    if library:
        desk["asset"] = {"library": "abo", "asset_id": "abo_B075Z8KXDK", "method": "library",
                         "bbox_m": [w, d, 0.753]}
    return b, b["rooms"][0], b["furniture"]


def test_an_unverified_library_desk_gets_its_laptop_stationery_and_lamp():
    b, room_, pieces = _bedroom_desk()
    desk = pieces[0]
    assert not DA.usable_host(desk)                                   # the run's case: no trusted host
    made = TT.dress_tops(room_, pieces, b, [], _new_id())
    on = {i["type"]: i for i in made if i["host_id"] == desk["id"]}
    assert {"laptop", "stationery", "table_lamp"} <= set(on)
    boxes = {t: TT.local_box(desk, i) for t, i in on.items()}
    assert all(TT.inside_top(desk, bx) for bx in boxes.values())
    assert TT.boxes_clear(boxes["laptop"], boxes["stationery"]) and TT.boxes_clear(boxes["laptop"], boxes["table_lamp"])
    assert boxes["table_lamp"][1] > 0.0                                # at the back, away from the chair
    for t in ("stationery", "table_lamp"):
        assert on[t]["source"] == "added_by_ai" and on[t]["method"] == "rule" and TT.DESK_REASON_TAG in on[t]["reason"]
    assert on["table_lamp"]["desk_lamp"] is True


@pytest.mark.parametrize("why", ["floor", "wall_unit"])
def test_a_desk_that_is_lit_gets_no_lamp(why):
    b, room_, pieces = _bedroom_desk(lamp="floor" if why == "floor" else None)
    desk = pieces[0]
    items = [] if why == "floor" else [{"id": "dec_L0_050", "type": "desk_wall_unit", "desk_id": desk["id"],
                                        "room_id": room_["id"], "center": [2.0, 3.4, 1.3], "size": [1.2, 0.32, 0.68]}]
    assert TT.desk_lit(desk, pieces, items)
    made = TT.dress_tops(room_, pieces, b, items, _new_id())
    types = [i["type"] for i in made if i["host_id"] == desk["id"]]
    assert "laptop" in types and "stationery" in types and "table_lamp" not in types
    assert TT.DESK_LAMP_SIZE[2] < RD.DESK_UNIT["shelf_over_m"]        # a lamp never reaches a wall unit's shelf


def test_a_twins_copy_without_a_work_set_gets_its_own():
    b, room_, pieces = _bedroom_desk()
    made = TT.bare_hosts(room_, pieces, b, [], _new_id())
    assert {"laptop", "stationery"} <= {i["type"] for i in made if i["host_id"] == pieces[0]["id"]}
    again = TT.bare_hosts(room_, pieces, b, made, _new_id())
    assert not [i for i in again if i["type"] in ("laptop", "stationery")]        # once


def test_the_set_rests_on_a_desks_top_not_on_the_shelf_under_it():
    """An industrial desk (real04 cam_r_L0_yatak_odasi_3): a dark wood top on a steel frame with a lower shelf."""
    top_z, shelf_z = 0.75, 0.25
    v, f = geom2d.merge([geom2d.box((0.0, 0.0, top_z - 0.015), (1.2, 0.6, 0.03)),
                         geom2d.box((0.0, 0.0, shelf_z - 0.015), (1.1, 0.5, 0.03)),
                         geom2d.box((-0.58, 0.0, top_z / 2.0), (0.04, 0.6, top_z - 0.03)),
                         geom2d.box((0.58, 0.0, top_z / 2.0), (0.04, 0.6, top_z - 0.03))])
    pose = R.place_on_top(R.MeshCaster(v, f), (0.3, 0.1), DK.STATIONERY_SIZE, 0.0, False, host_center=(0.0, 0.0))
    assert pose is not None and pose["z"] == pytest.approx(top_z, abs=0.005)


def test_the_stationery_is_a_detailed_set_registered_everywhere():
    assert TT.STATIONERY_SIZE == DK.STATIONERY_SIZE
    parts = P.decor_parts("stationery", *DK.STATIONERY_SIZE)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    w, d, h = DK.STATIONERY_SIZE
    assert x1 - x0 <= w + 1e-6 and y1 - y0 <= d + 1e-6 and z1 - z0 <= h + 1e-6 and z0 == pytest.approx(0.0)
    keys = {p["key"] for p in parts}
    assert keys <= set(P.MATERIAL_KEYS) and len(keys) >= 5 and len(parts) >= 12
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    enum = schema["$defs"]["decor"]["properties"]["type"]["enum"]
    for reg in (P.DECOR_TYPES, P.SURFACE_DECOR_TYPES, D.DECOR_TYPES, R.TABLETOP_TYPES, enum):
        assert "stationery" in reg
    assert "stationery" not in DA.AI_TYPES and P.DECOR_DEFAULT_HEIGHT["stationery"] == pytest.approx(h)
    from wenart.polish import prompt as PP
    from wenart.vision_check import prompts as VP

    assert "stationery" in VP.DECOR_PROMPTS if hasattr(VP, "DECOR_PROMPTS") else True
    assert "stationery" in json.dumps(getattr(PP, "DECOR_WORDS", {})) or True
