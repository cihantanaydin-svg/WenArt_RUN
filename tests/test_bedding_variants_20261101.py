"""1 Nov 2026 (lessons UL236 and UL238; user on real04 run 20261031-194116-full): bedding and cushion sets with variety,
real sizes and real detail; no second set on a made-up library bed; sofa cushions on the seat leaning on the back,
arranged for the piece; the seat throw never a stiff board; a top's item never under a seat (CPU only)."""
from __future__ import annotations

from collections import Counter

import numpy as np
import pytest

import _m11_room as M
from wenart.blender import bedding_parts as BP
from wenart.blender import geom2d
from wenart.blender import rest as R
from wenart.blender import seat_throw as ST
from wenart.blender import soft_sets as SS
from wenart.blender import textiles as T
from wenart.style import colours as COL

BED_C = (2.5, 3.0)
SOFT = ("pillow", T.SHAM_ROLE, T.ACCENT_ROLE, T.LUMBAR_ROLE)


# ------------------------------------------------------------------------------------------------------ helpers
def bed_caster(center=BED_C, w: float = 1.6, d: float = 2.0, top: float = 0.5, head_h: float = 1.1,
               headboard_at: str = "head") -> R.MeshCaster:
    """A bed: a mattress box (top ``top``) and a 6 cm headboard ``head_h`` tall at its head (+y) or at its foot."""
    cx, cy = center
    y = cy + d / 2.0 - 0.03 if headboard_at == "head" else cy - d / 2.0 + 0.03
    v, f = geom2d.merge([geom2d.box((cx, cy, top / 2.0), (w, d, top)),
                         geom2d.box((cx, y, head_h / 2.0), (w, 0.06, head_h))])
    return R.MeshCaster(v, f)


def host_fp(center=BED_C, w: float = 1.6, d: float = 2.0) -> dict:
    return {"center": list(center), "size": [w, d], "rotation_deg": 0.0}


def house(n_rooms: int = 4, ensuite: int | None = None, child: int | None = None, widths=None) -> dict:
    """A row of bedrooms 4 x 4 m on one level, one double bed in each (head on the north wall), a bathroom east of the
    ``ensuite`` room with a door between them."""
    rooms, beds, openings, walls = [], [], [], []
    for k in range(n_rooms):
        x0 = 4.2 * k
        rid = f"r_bed_{k}"
        rooms.append({"id": rid, "level_id": "L0", "room_type": "child" if k == child else "bedroom",
                      "polygon": [[x0, 0.0], [x0 + 4.0, 0.0], [x0 + 4.0, 4.0], [x0, 4.0]], "area_computed": 16.0})
        w = (widths or {}).get(k, 1.6)
        beds.append({"id": f"f_bed_{k}", "level_id": "L0", "room_id": rid, "type": "bed_double",
                     "footprint": {"center": [x0 + 2.0, 3.0], "size": [w, 2.0], "rotation_deg": 0.0},
                     "front_deg": 270.0})
    if ensuite is not None:                                  # a bathroom south of the room, a door between them
        x0 = 4.2 * ensuite
        rooms.append({"id": "r_bath", "level_id": "L0", "room_type": "bathroom",
                      "polygon": [[x0 + 1.0, -2.1], [x0 + 3.0, -2.1], [x0 + 3.0, -0.1], [x0 + 1.0, -0.1]],
                      "area_computed": 4.0})
        openings.append({"id": "d_en", "type": "door", "level_id": "L0", "center": [x0 + 2.0, -0.05], "width": 0.8})
    return {"rooms": rooms, "furniture": beds, "openings": openings, "walls": walls, "decor": []}


# ---------------------------------------------------------------------------------- 1. variants per bed, deterministic
def test_every_bed_of_a_house_gets_its_own_set_the_same_every_run():
    b = house(6)
    first = SS.house_bed_variants(b["furniture"], b, "modern", ["mustard", "cream"])
    again = SS.house_bed_variants(b["furniture"], b, "modern", ["mustard", "cream"])
    assert first == again                                                              # deterministic (by the ids)
    sigs = [tuple(v["variant"]["signature"]) for v in first.values()]
    assert len(set(sigs)) == len(sigs) == 6                                            # no two beds alike
    tex, pal = SS.textiles_of("modern"), SS.palette_of("modern", ["mustard", "cream"])
    for spec in first.values():
        assert spec["arrangement"] in SS.ARRANGEMENTS and spec["variant"]["rule"] == SS.RULE_BED
        assert spec["duvet"]["look"] in tex["duvet"] + ("cotton",) and spec["shams"]["look"] in tex["shams"] + \
            tex["pillows"]
        assert all(a["look"] in tex["accent"] and COL.known(a["colour"]) for a in spec["accent"])
        assert spec["duvet"]["colour"] in pal["duvet"] and COL.known(spec["throw"]["colour"])
        assert spec["throw"]["style"] in SS.THROW_STYLES_BY_RANK[3] + SS.THROW_STYLES_BY_RANK[2]
        assert all(look in BP.LOOK_SLUGS for look in (spec["duvet"]["look"], spec["sheet"]["look"],
                                                      spec["pillows"]["look"], spec["shams"]["look"]))
        assert sum(spec["expected"].values()) <= BP.PIECES_MAX["double"]                # UL195: five at most
    # the houses differ in more than the colours: arrangements, duvets or throws vary over the six beds
    assert len({v["arrangement"] for v in first.values()}) >= 2
    assert len({(v["duvet"]["look"], v["duvet"].get("quilt")) for v in first.values()}) >= 2
    # another family's palette gives its own looks
    jap = SS.house_bed_variants(b["furniture"], b, "japandi")
    assert all(v["duvet"]["look"] in SS.textiles_of("japandi")["duvet"] + ("cotton",) for v in jap.values())


def test_the_decor_stage_plans_each_beds_variant_and_its_own_throw():
    from wenart.furniture import bedding as BG

    b = M.building(w=5.0, h=4.0, room_type="bedroom", furniture=[
        M.fp("f_L0_001", "bed_double", BED_C, (1.6, 2.0))])
    twin = M.fp("f_L0_002", "bed_double", (2.5, 3.0), (1.6, 2.0))
    b["furniture"].append(dict(twin, room_id=M.ROOM_ID))
    # a twin's copied throw keeps its partner's slot: its host decides whose throw it is
    b["decor"] = [{"id": "dec_1", "type": "throw", "host_id": "f_L0_001", "slot": "f_L0_001.throw",
                   "center": [2.5, 2.3], "size": [1.5, 0.5, 0.05]},
                  {"id": "dec_2", "type": "throw", "host_id": "f_L0_002", "slot": "f_L0_001.throw",
                   "center": [2.5, 2.3], "size": [1.5, 0.5, 0.05], "colour": "beige"}]
    BG.plan_beds(b, {"family": "modern"})
    one, two = (p["bedding_layers"] for p in b["furniture"])
    assert one["variant"]["id"] != two["variant"]["id"] and one["set"]["arrangement"] in SS.ARRANGEMENTS
    t1, t2 = b["decor"]
    assert t1["weave"]["variant"] == one["variant"]["id"] and t2["weave"]["variant"] == two["variant"]["id"]
    assert t2["colour"] == two["set"]["throw"]["colour"] and t2["ai_colour"] == "beige"
    assert b["bedding"]["beds"]["f_L0_001"]["variant"] == one["variant"]["id"]
    # the build gives a twin's copy made later its own bed's throw too
    from wenart.blender import furniture as F

    stale = dict(t2, weave=dict(t1["weave"]))
    fixed = F.bed_throw_item(stale, b["furniture"][1])
    assert fixed["weave"]["variant"] == two["variant"]["id"] and fixed["colour"] == two["set"]["throw"]["colour"]
    assert F.bed_throw_item(t1, b["furniture"][0]) is t1                                 # already its own


# ------------------------------------------------------------------------------------- 2. a single bed's set, sizes
def test_a_single_bed_gets_one_pillow_never_two_squeezed_in():
    spec = SS.bed_variant("f_single", "modern", 0.9, rank=1)
    assert spec["arrangement"] == "single_plain" and spec["expected"]["pillows"] == 1
    assert spec["expected"]["euro_shams"] == 0 and sum(spec["expected"].values()) <= BP.PIECES_MAX["single"]
    assert spec["sizes"]["class"] == "single" and spec["sizes"]["pillow"][0] <= 0.9 - 0.2 + 1e-9
    wide = SS.bed_variant("f_single_w", "modern", 1.2, rank=1, single=True)            # a wide single bed is single
    assert wide["arrangement"] == "single_plain" and wide["sizes"]["class"] == "single"
    b = house(1)
    b["furniture"][0].update(type="bed_single", footprint={"center": [2.0, 3.0], "size": [1.2, 2.0],
                                                           "rotation_deg": 0.0})
    v = SS.house_bed_variants(b["furniture"], b, "modern")["f_bed_0"]
    assert v["expected"]["pillows"] == 1 and v["variant"]["rank"] == 1
    rich = SS.bed_variant("f_single", "modern", 0.9, rank=3)
    assert rich["arrangement"] == "single_sham" and rich["expected"] == {"euro_shams": 1, "pillows": 1, "accent": 0,
                                                                        "lumbar": 0}
    # built on a single bed with a headboard: one pillow, centred, inside the mattress
    plan = T.bedding_set(bed_caster(w=0.9), host_fp(w=0.9), 0.0, spec)
    rec = plan["record"]
    assert rec["set"]["pillows"] == 1 and rec["set"]["euro_shams"] == 0
    pillows = [p for p in plan["parts"] if p["role"] == "pillow"]
    assert len(pillows) == 1
    x = np.asarray(pillows[0]["verts"])[:, 0] - BED_C[0]
    assert x.min() > -0.45 and x.max() < 0.45 and abs((x.min() + x.max()) / 2.0) < 0.02
    plan3 = T.bedding_set(bed_caster(w=0.9), host_fp(w=0.9), 0.0, rich)
    assert plan3["record"]["set"]["euro_shams"] == 1 and plan3["record"]["set"]["pillows"] == 1


def test_pillow_sizes_and_counts_follow_the_mattress():
    want = {"euro_shams": 2, "pillows": 2, "accent": 1, "lumbar": 1}
    small, queen, king = (SS.bed_sizes(w, want) for w in (1.4, 1.6, 1.8))
    assert (small["class"], queen["class"], king["class"]) == ("small_double", "queen", "king")
    assert small["pillow"][0] <= 0.60 and queen["pillow"][0] == pytest.approx(0.65)
    assert king["pillow"][0] == pytest.approx(min(0.85, (1.8 - 0.1) / 2 - 0.04)) and king["pillow"][2] == 0.50
    assert king["lumbar"][0] > queen["lumbar"][0] > small["lumbar"][0]
    for s in (small, queen, king):
        assert 2 * s["pillow"][0] + SS.PILLOW_GAP_M <= {"small_double": 1.4, "queen": 1.6, "king": 1.8}[s["class"]]
    three = SS.bed_sizes(1.8, {"euro_shams": 3, "pillows": 2})
    assert 3 * three["sham"][0] <= 1.8 - 0.1                                            # three shams on a king
    # built: a king bed's pillows are king pillows, a queen's standard ones
    spec = dict(SS.bed_variant("f_k", "modern", 1.8, rank=2))
    spec.update(arrangement="pair_plain", expected=SS.arrangement_counts("pair_plain"),
                sizes=SS.bed_sizes(1.8, SS.arrangement_counts("pair_plain")))
    plan = T.bedding_set(bed_caster(w=1.8), host_fp(w=1.8), 0.0, spec)
    assert plan["record"]["pillow_size_m"][0] == pytest.approx(0.81, abs=0.01)
    spec_q = dict(spec, sizes=SS.bed_sizes(1.6, SS.arrangement_counts("pair_plain")))
    plan_q = T.bedding_set(bed_caster(), host_fp(), 0.0, spec_q)
    assert plan_q["record"]["pillow_size_m"][0] == pytest.approx(0.65, abs=0.01)


# ------------------------------------------------------------------------------------------ 3. the master's richer
def test_the_master_bedroom_gets_the_richest_set_a_childs_the_plainest():
    b = house(3, ensuite=0, child=2)
    beds = {p["id"]: p for p in b["furniture"]}
    assert SS.bed_rank(beds["f_bed_0"], b)[0] == 3 and "own bathroom" in SS.bed_rank(beds["f_bed_0"], b)[1]
    assert SS.bed_rank(beds["f_bed_1"], b)[0] == 2 and SS.bed_rank(beds["f_bed_2"], b)[0] == 1
    v = SS.house_bed_variants(b["furniture"], b, "modern")
    pieces = {k: sum(s["expected"].values()) for k, s in v.items()}
    assert SS.ARRANGEMENTS[v["f_bed_0"]["arrangement"]]["rank"] == 3
    assert SS.ARRANGEMENTS[v["f_bed_2"]["arrangement"]]["rank"] == 1
    assert pieces["f_bed_0"] > pieces["f_bed_2"]
    assert v["f_bed_0"]["throw"]["style"] in SS.THROW_STYLES_BY_RANK[3]
    assert v["f_bed_2"]["throw"]["style"] in SS.THROW_STYLES_BY_RANK[1]
    # without a bathroom the widest bed in the largest bedroom is the master
    b2 = house(3, widths={1: 1.8})
    assert SS.bed_rank({p["id"]: p for p in b2["furniture"]}["f_bed_1"], b2)[0] == 3


# --------------------------------------------------------------------------- 4. never two sets on a made-up library bed
def _top_grid(head_bump: float, wrinkle: float, at: str = "head", n: int = 40):
    xs, ys = np.meshgrid(np.linspace(-0.75, 0.75, n), np.linspace(-0.95, 0.95, n), indexing="ij")
    z = 0.5 + wrinkle * np.sin(xs * 23.0) * np.sin(ys * 17.0)
    zone = ys > 0.55 if at == "head" else ys < -0.55
    z = z + np.where(zone, head_bump, 0.0)
    return np.stack([xs + BED_C[0], ys + BED_C[1], z], axis=-1).reshape(-1, 3)


def test_a_made_up_bed_never_gets_a_second_set_over_its_own():
    made_up = {"has_bedding": True, "has_pillows": True}
    # the run's case: a modelled duvet whose pillows the audit sees but the head zone's measure missed: kept
    missed = BP.bedding_relief(_top_grid(0.0, 0.012), BED_C, 0.0, (1.6, 2.0))
    mode, why = BP.dress_mode(made_up, missed, width=1.6)
    assert mode is None and "never two sets" in why
    # a flat cover (a mattress box of a few faces) under its own pillows: our duvet only, its pillows stay
    box_v, faces = geom2d.box((BED_C[0], BED_C[1], 0.25), (1.6, 2.0, 0.5))
    v = np.asarray(box_v)
    tris = [[q[0], q[k], q[k + 1]] for q in faces for k in range(1, len(q) - 1)]
    pillow = np.stack(np.meshgrid(np.linspace(-0.6, 0.6, 13), np.linspace(0.55, 0.78, 8), indexing="ij"), axis=-1)
    pillow = np.c_[pillow.reshape(-1, 2) + np.array(BED_C), np.full(13 * 8, 0.64)]
    rel = BP.bedding_relief(np.concatenate([v, BP.surface_samples(v, tris), pillow]), BED_C, 0.0, (1.6, 2.0))
    assert rel["pillow_vertices"] >= BP.PILLOW_VERTS_MIN and rel["pillow_front_y"] == pytest.approx(0.55, abs=0.02)
    mode, why = BP.dress_mode(made_up, rel, width=1.6)
    assert mode == "duvet" and "never two sets" in why
    # our duvet under its pillows: no pillow, sham or cushion of ours, the duvet ends before the model's pillows
    spec = SS.bed_variant("f_x", "modern", 1.6, rank=3)
    plan = T.bedding_set(bed_caster(), host_fp(), 0.0, spec, mode="duvet", pillow_front_y=rel["pillow_front_y"])
    roles = Counter(p["role"] for p in plan["parts"])
    assert not any(roles[r] for r in SOFT) and roles["duvet"] == 1 and roles["turndown"] == 1
    assert plan["record"]["set"] == {"euro_shams": 0, "pillows": 0, "accent": 0, "lumbar": 0}
    assert plan["record"]["duvet_rect_local"][3] <= rel["pillow_front_y"] - 0.03 + 1e-6
    assert all("never two sets" in v for v in plan["record"]["explained"].values())


def test_a_bed_turned_the_wrong_way_is_found_by_its_headboard_or_its_pillows_at_the_foot():
    verts = np.asarray(geom2d.merge([geom2d.box((BED_C[0], BED_C[1], 0.25), (1.6, 2.0, 0.5)),
                                     geom2d.box((BED_C[0], BED_C[1] - 0.97, 0.55), (1.6, 0.06, 1.1))])[0])
    rel = BP.bedding_relief(verts, BED_C, 0.0, (1.6, 2.0))
    assert rel["foot_end_top_m"] - rel["head_end_top_m"] >= BP.TURNED_RISE_M
    mode, why = BP.dress_mode({"has_bedding": True, "has_pillows": True}, rel)
    assert mode == "turn" and "turned the wrong way" in why
    right = BP.bedding_relief(np.asarray(geom2d.merge([
        geom2d.box((BED_C[0], BED_C[1], 0.25), (1.6, 2.0, 0.5)),
        geom2d.box((BED_C[0], BED_C[1] + 0.97, 0.55), (1.6, 0.06, 1.1))])[0]), BED_C, 0.0, (1.6, 2.0))
    assert BP.turned_reason(right) is None
    # its own pillows at the foot and none at the head: turned
    at_foot = BP.bedding_relief(_top_grid(0.35, 0.012, at="foot"), BED_C, 0.0, (1.6, 2.0))
    assert "foot" in BP.turned_reason(at_foot)
    # the build turns its model by its front axis (once: the record says so)
    from wenart.blender import furniture as F

    asset = {"asset_id": "x", "front_axis": "+Y", "up_axis": "+Z"}
    new = F.turned_asset(asset, why)
    assert new["front_axis"] == "-Y" and new["turned_by_build"]["from"] == "+Y" and asset["front_axis"] == "+Y"
    assert new["turned_by_build"]["source"] == "adjusted_by_ai" and BP.opposite_axis("-X") == "+X"
    assert F.library_bed({"type": "bed_double", "asset": asset}, {"method": "library"})


# -------------------------------------------------------------------------------------------- 5. better models
def test_cushions_have_their_finish_and_the_trim_moves_with_the_body():
    body_only = SS.cushion_parts(0.45, 0.15, 0.45, "velvet", "knife")
    assert len(body_only) == 1 and body_only[0]["key"] == BP.textile_key("velvet")
    piped = SS.cushion_parts(0.45, 0.15, 0.45, "linen", "piping", "velvet")
    assert [p["role"] for p in piped] == ["cushion", "piping"] and piped[1]["key"] == BP.runner_key("velvet")
    ring = np.asarray(piped[1]["verts"])
    assert ring[:, 2].min() >= -SS.PIPING_R_M - 1e-6 and ring[:, 2].max() <= 0.45 + SS.PIPING_R_M + 1e-6
    assert abs(ring[:, 1]).max() <= SS.PIPING_R_M + 1e-6                               # along the seam (y = 0)
    tufted = SS.cushion_parts(0.45, 0.15, 0.45, "boucle", "buttons")
    assert [p["role"] for p in tufted] == ["cushion", "button", "button"]
    v = np.asarray(tufted[0]["verts"])
    mid = np.hypot(v[:, 0], v[:, 2] - 0.225) < 0.02
    assert np.abs(v[mid, 1]).max() < 0.075 * (1.0 - SS.TUFT_DEPTH) + 0.01               # pulled in at the centre
    tassels = SS.cushion_parts(0.45, 0.15, 0.45, "linen", "tassels")
    assert sum(1 for p in tassels if p["role"] == "tassel") == 4
    flange = SS.cushion_parts(0.65, 0.14, 0.62, "linen", "flange")
    assert np.asarray(flange[0]["verts"])[:, 0].max() == pytest.approx(0.325, abs=0.01)
    # placed by a lean, the trim keeps to the body (the body's lift)
    pose = {"center": [0.0, 0.0], "z": 0.5, "rotation_deg": 0.0, "lean_deg": 20.0}
    placed = T.placed_parts(piped, pose, "cream", "navy")
    b, p = np.asarray(placed[0]["verts"]), np.asarray(placed[1]["verts"])
    assert placed[0]["colour"] == "cream" and placed[1]["colour"] == "navy"
    assert p[:, 2].min() >= b[:, 2].min() - 0.01 and p[:, 2].max() <= b[:, 2].max() + 0.01


def test_a_quilted_coverlet_has_stitch_lines_and_the_throws_have_thickness():
    xs, ys = np.meshgrid(np.linspace(-0.5, 0.5, 101), np.linspace(-0.5, 0.5, 101), indexing="ij")
    for kind in ("channel", "box", "diamond"):
        q = SS.quilt_depth(xs, ys, kind, SS.QUILT_PITCH_M[kind])
        assert q.max() == pytest.approx(1.0, abs=0.05) and q.min() < 0.05 and 0.02 < q.mean() < 0.5
    assert not SS.quilt_depth(xs, ys, None, None).any()
    # every throw style is a cloth with its thickness and its soft roll, never a flat sheet
    sides = {s: {"free": True} for s in BP.SIDES}
    for style in T.STYLE_THROWS:
        item = {"id": "t", "type": "throw", "center": [2.5, 2.3], "size": [1.5, 0.5, 0.05],
                "weave": {"style": style, "look": "chunky_knit", "pattern": "houndstooth", "fringe": True,
                          "fringe_ends": ["left", "right"]}}
        got = T.throw_parts(bed_caster(), host_fp(), item, 0.0, sides=sides)
        assert got is not None and got["weave"]["style"] == style, style
        cloth = np.asarray(got["parts"][0]["verts"])
        assert got["parts"][0]["role"] == "throw"
        assert cloth[:, 2].min() < 0.5 - 0.15                                         # it hangs down the sides
        assert got["weave"]["thickness_m"] >= 0.012
        if style == "corner_drape":
            assert cloth[:, 0].min() > BED_C[0] - 0.8 + 0.4                             # one corner only
        if style == "quilt_fold":
            assert not got["weave"]["fringe"] and got["weave"]["quilt"] == "diamond"
        else:
            assert got["weave"]["fringe_strands"] > 10
    folded = SS.folded_throw_parts(0.46, 0.34, 4, 0.011)[0]
    v = np.asarray(folded["verts"])
    assert v[:, 2].min() == pytest.approx(0.0) and v[:, 2].max() == pytest.approx(0.044, abs=0.004)
    assert v[:, 0].max() - v[:, 0].min() == pytest.approx(0.46, abs=0.01)


def test_a_variant_set_is_built_with_its_sizes_finishes_and_its_duvet():
    spec = SS.bed_variant("f_master", "modern", 1.6, rank=3)
    spec.update(arrangement="shams_accent", expected=SS.arrangement_counts("shams_accent"),
                sizes=SS.bed_sizes(1.6, SS.arrangement_counts("shams_accent")))
    spec["shams"] = dict(spec["shams"], finish="piping")
    spec["duvet"] = dict(spec["duvet"], quilt="box", quilt_pitch_m=0.30, look="cotton", thickness_m=0.035,
                         fold_back="sheet")
    plan = T.bedding_set(bed_caster(), host_fp(), 0.0, spec)
    rec = plan["record"]
    assert rec["set"] == {"euro_shams": 2, "pillows": 2, "accent": 1, "lumbar": 0}
    assert rec["arrangement"] == "shams_accent" and rec["variant"]["rule"] == SS.RULE_BED
    assert rec["duvet"]["quilt"]["kind"] == "box" and rec["finishes"]["shams"] == "piping"
    roles = Counter(p["role"] for p in plan["parts"])
    assert roles[T.SHAM_ROLE] == 2 and roles["piping"] >= 2 and roles["pillow"] == 2
    assert sum(roles[r] for r in SOFT) <= BP.PIECES_MAX["double"]
    # the shams in the variant's look and colour, the duvet stitched
    shams = [p for p in plan["parts"] if p["role"] == T.SHAM_ROLE]
    assert shams[0]["key"] == BP.textile_key(spec["shams"]["look"]) and shams[0]["colour"] == spec["shams"]["colour"]
    duvet = np.asarray([p for p in plan["parts"] if p["role"] == "duvet"][0]["verts"])
    assert duvet.shape[0] > 100


# --------------------------------------------------------------------------- 6. sofa cushions (UL238)
def low_sofa(center=(3.0, 2.0), w: float = 2.1, d: float = 0.9, seat: float = 0.40, back_top: float = 0.51):
    """A low lounge sofa: a base, a seat (top ``seat``), a low back (top ``back_top``) 0.2 m deep, two arms."""
    cx, cy = center
    parts = [geom2d.box((cx, cy, (seat - 0.08) / 2.0), (w, d, seat - 0.08)),
             geom2d.box((cx, cy - 0.1, seat - 0.04), (w - 0.3, d - 0.2, 0.08)),
             geom2d.box((cx, cy + d / 2.0 - 0.1, back_top / 2.0), (w, 0.2, back_top))]
    for s in (-1, 1):
        parts.append(geom2d.box((cx + s * (w / 2.0 - 0.075), cy, (seat + 0.08) / 2.0), (0.15, d, seat + 0.08)))
    return R.MeshCaster(*geom2d.merge(parts))


def sofa_piece(center=(3.0, 2.0), w: float = 2.1, d: float = 0.9, ftype: str = "sofa", pid: str = "f_L1_017",
               height: float = 0.51, chaise: str | None = None) -> dict:
    asset = {"bbox_m": [w, d, height]}
    if chaise:
        asset["chaise_side"] = chaise
    return {"id": pid, "type": ftype, "level_id": "L1", "room_id": "r_live",
            "footprint": {"center": list(center), "size": [w, d], "rotation_deg": 0.0}, "asset": asset}


def test_a_cushion_on_a_low_back_sits_on_the_seat_leaning_on_the_back_never_on_it():
    host = sofa_piece()
    caster = low_sofa()
    low = R.seat_profile(caster, {"center": [3.0, 2.0], "size": [2.1, 0.9], "rotation_deg": 0.0}, 0.0, 0.40)
    assert low["rise"] == pytest.approx(0.11, abs=0.01) and low["face_y"] == pytest.approx(0.25, abs=0.02)
    from wenart.blender import parametric as P

    item = {"id": "dec_L1_007", "type": "cushion", "host_id": host["id"], "center": [3.4, 2.3],
            "size": [0.46, 0.14, 0.44]}
    parts = P.decor_parts("cushion", 0.46, 0.14, 0.44, item)
    verts, faces, _keys = P.world_mesh(parts, (0.0, 0.0), 0.0, 0.0)
    plan = R.plan_decor(item, host, caster, verts, faces, "back")
    assert "not_rested" not in plan, plan.get("not_rested")
    pose = plan["pose"]
    arr = np.asarray(plan["verts"])
    assert pose["z"] <= 0.40 + 0.01                                                    # its base on the seat ...
    assert arr[:, 2].min() < 0.42                                                       # ... never on the back (0.51)
    assert pose["top_over_back_m"] <= max(R.SEAT_OVER_M, R.SEAT_OVER_SHARE * pose["size"][2]) + 1e-6
    assert arr[:, 2].max() <= 0.51 + max(R.SEAT_OVER_M, R.SEAT_OVER_SHARE * 0.44) + 0.01
    assert "low back" in pose["how"] or "sized down" in pose["how"] or pose["lean_deg"] > R.LEAN_DEG


def test_a_seats_cushions_are_sized_to_its_back_and_seat():
    normal = SS.seat_cushion_size(0.40, 0.75)
    assert normal["kind"] == "square" and 0.42 <= normal["size"][0] <= 0.50 and normal["lean_deg"] == 20.0
    lower = SS.seat_cushion_size(0.29, 0.75)
    assert lower["kind"] == "square" and lower["size"][0] < normal["size"][0]
    lounge = SS.seat_cushion_size(0.11, 0.70)
    assert lounge["kind"] == "lumbar" and lounge["size"][2] <= 0.30
    assert lounge["top_over_back_m"] <= SS.allowance(lounge["size"][2]) + 1e-9
    assert SS.seat_cushion_size(0.0, 0.7)["kind"] is None
    lay = SS.seat_layout(sofa_piece())
    assert lay["back_top_m"] == 0.51 and lay["back_rise_m"] == pytest.approx(0.51 - 0.78 * 0.51, abs=0.01)


def test_a_straight_sofa_gets_symmetric_cushions_inside_its_arms():
    host = sofa_piece(height=0.82, w=2.2)
    plan = SS.seat_cushion_plan(host, "modern", ["mustard", "cream"])
    xs = sorted(it["lx"] for it in plan["items"] if it["kind"] == "square")
    assert len(xs) in (2, 4) and xs == pytest.approx([-x for x in reversed(xs)], abs=1e-6)   # symmetric
    inner = 2.2 / 2.0 - SS.ARM_W_M["sofa"] - 0.02
    for it in plan["items"]:
        assert abs(it["lx"]) + it["size"][0] / 2.0 <= inner + 1e-6                    # inside the arms
        assert it["look"] in SS.SEAT_LOOKS["modern"] and it["finish"] in SS.SEAT_FINISHES + ("knife",)
    assert plan["items"][0]["colour"] == "mustard"                                     # the decor stage's first
    assert SS.seat_cushion_plan(host, "modern", ["mustard", "cream"]) == plan          # deterministic
    other = SS.seat_cushion_plan(dict(host, id="f_other"), "modern", ["mustard", "cream"],
                                 taken=[tuple(plan["signature"])])
    assert tuple(other["signature"]) != tuple(plan["signature"])                       # no two seats alike


def test_a_corner_sofa_gets_a_corner_group_and_a_pair_at_its_open_end():
    host = sofa_piece(w=4.38, d=1.97, ftype="sofa_corner", pid="f_L-1_053", height=0.72, chaise="right")
    plan = SS.seat_cushion_plan(host, "modern", ["cream", "mustard"])
    groups = Counter(it["group"] for it in plan["items"])
    assert groups["corner"] in (2, 3) and groups["open"] in (1, 2) and not groups.get("middle")
    corner = [it["lx"] for it in plan["items"] if it["group"] == "corner"]
    opened = [it["lx"] for it in plan["items"] if it["group"] == "open"]
    assert min(corner) > 0.8 and max(opened) < -0.8                                    # the chaise's end, the other
    # a group stands side by side, never overlapping, the larger at the end
    for grp in (sorted(corner, reverse=True), sorted(opened)):
        items = sorted([it for it in plan["items"] if it["lx"] in grp], key=lambda it: abs(it["lx"]), reverse=True)
        for a, b in zip(items, items[1:]):
            assert abs(a["lx"] - b["lx"]) >= (a["size"][0] + b["size"][0]) / 2.0 + SS.CUSHION_GAP_M - 1e-6
            assert a["size"][0] >= b["size"][0]
    sizes = {it["size"][0] for it in plan["items"]}
    assert all(0.30 <= s <= 0.50 for s in sizes)                                       # in proportion to the seat


def test_the_decor_stage_replaces_the_library_cushions_with_the_seats_set():
    from wenart.furniture import seat_cushions as SC

    host = sofa_piece(w=4.38, d=1.97, ftype="sofa_corner", pid="f_L-1_053", height=0.72, chaise="right")
    host["level_id"] = "L-1"
    cushions = [{"id": f"dec_{k}", "type": "cushion", "host_id": host["id"], "level_id": "L-1", "room_id": "r_live",
                 "center": [3.0 - 2.0 + k, 2.5], "size": [0.45, 0.15, 0.45], "colour": c,
                 "asset": {"asset_id": f"abo_{k}", "title": "Floral Throw Pillow"}}
                for k, c in enumerate(["cream", "mustard", "cream", "mustard", "cream", "mustard"])]
    b = {"furniture": [host], "decor": cushions, "rooms": []}
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_new_{n[0]}"
    SC.dress_seats(b, {"family": "modern"}, new_id)
    mine = [d for d in b["decor"] if d.get("host_id") == host["id"]]
    assert 3 <= len(mine) <= 5 and all(d["asset"] is None and d["cushion_set"]["rule"] == SS.RULE_SEAT for d in mine)
    assert all(d["replaced_asset"]["asset_id"].startswith("abo_") for d in mine if d["id"].startswith("dec_"))
    assert b["seat_cushions"]["seats"][host["id"]]["arrangement"].startswith("corner")
    assert len(b["seat_cushions"]["removed"]) == 6 - len([d for d in mine if not d["id"].startswith("dec_new")])
    # the build makes each one our filled cushion with its finish (no library model)
    from wenart.blender import furniture as F

    local = F.local_decor_mesh(mine[0], "cushion", "back")
    assert BP.textile_key(mine[0]["cushion_set"]["look"]) in local["keys"]


# ----------------------------------------------------------------------- 7. the seat throw and the top's items (UL238)
def test_a_corner_sofas_back_return_is_no_arm_for_the_throw():
    """The run's corner sofa: at the chaise's end a 27 cm block whose front is 1 m behind the chaise's front (the
    back's return); the throw went over it as a stiff board. It is no arm: the throw goes over the long part's arm."""
    cx, cy, w, d = 3.0, 2.0, 2.6, 1.6
    parts = [geom2d.box((cx, cy + 0.35, 0.21), (w, 0.9, 0.30)),
             geom2d.box((cx + 0.9, cy, 0.21), (0.8, d, 0.30)),
             geom2d.box((cx + 0.1, cy + 0.23, 0.40), (2.4, 0.66, 0.08)),
             geom2d.box((cx + 0.9, cy - 0.12, 0.40), (0.8, 1.36, 0.08)),
             geom2d.box((cx + 0.1, cy + 0.68, 0.62), (2.4, 0.24, 0.52)),
             geom2d.box((cx - 1.2, cy + 0.35, 0.33), (0.2, 0.9, 0.54)),
             geom2d.box((cx + 1.165, cy + 0.4, 0.38), (0.27, 0.8, 0.70))]               # the back's return
    caster = R.MeshCaster(*geom2d.merge(parts))
    fp = {"center": [cx, cy], "size": [w, d], "rotation_deg": 0.0}
    assert ST.measure_arm(caster, fp, "right", 0.44) is None
    host = {"id": "f_L0_011", "type": "sofa_corner", "footprint": fp}
    look = ST.throw_look("modern", "light grey", ["mustard"], side="right")
    item = {"id": "t", "type": "throw", "host_id": host["id"], "center": [cx + 0.9, cy], "size": [0.5, 0.45, 0.05],
            "colour": "mustard", "seat_throw": look}
    plan = R.plan_throw(item, host, caster, 0.0)
    assert "not_rested" not in plan and plan["weave"]["drape"] == "arm" and plan["weave"]["side"] == "left"
    assert ST.THROW_T_M >= 0.025 and ST.WRINKLE_M >= 0.012                               # softer, deeper folds


def test_a_throw_folds_flat_on_a_seat_without_an_arm_or_a_seat_end():
    caster = low_sofa(back_top=0.80)
    fp = {"center": [3.0, 2.0], "size": [2.1, 0.9], "rotation_deg": 0.0}
    got = ST.folded_throw(caster, fp, "right", 0.40, None, {"look": "knit"})
    assert got is not None and got["drape_kind"] == "folded"
    v = np.asarray(got["parts"][0]["verts"])
    assert v[:, 2].min() == pytest.approx(0.396, abs=0.01) and v[:, 2].max() < 0.40 + 0.06
    assert v[:, 0].max() <= 3.0 + 1.05


def test_a_trays_spot_under_a_sofa_moves_onto_the_free_part_of_the_coffee_table():
    """The run's coffee table was drawn partly under the sofa's seat and its tray took that end of it: an item on a low
    top moves out of what a seat's built model covers (decor stage), else it leaves; the build checks the real mesh
    (``rest.clash_with``: a corner sofa's box holds its open notch, where a coffee table stands)."""
    from shapely.geometry import Polygon

    from wenart import geometry as G
    from wenart.furniture import tabletop as TT

    sofa = {"id": "f_sofa", "type": "sofa", "level_id": "L-1",
            "footprint": {"center": [3.08, 3.27], "size": [4.38, 1.97], "rotation_deg": 270.0},
            "asset": {"bbox_m": [4.38, 1.737, 0.72], "scaling": "uniform"}}
    table = {"id": "f_table", "type": "table_coffee", "level_id": "L-1", "height": 0.45,
             "footprint": {"center": [2.309, 3.175], "size": [1.30, 0.63], "rotation_deg": 90.0}}
    tray = {"id": "dec_tray", "type": "tray", "host_id": "f_table", "room_id": "r", "center": [2.455, 2.757],
            "size": [0.4, 0.28, 0.05], "rotation_deg": 90.0}
    bowl = {"id": "dec_bowl", "type": "bowl", "host_id": "f_table", "room_id": "r", "center": [2.15, 3.3],
            "size": [0.3, 0.3, 0.1], "rotation_deg": 90.0}
    built = Polygon(TT.built_box(sofa))
    assert built.bounds[0] == pytest.approx(2.095 + (1.97 - 1.737), abs=0.01)          # the model: back-aligned
    b = {"furniture": [sofa, table], "decor": [tray, bowl]}
    out = TT.clear_of_seats(b)
    assert [r["id"] for r in out["moved"]] == ["dec_tray"] and not out["dropped"]
    t = Polygon(G.rotated_rectangle(tray["center"], tray["size"][:2], 90.0))
    assert built.intersection(t).area < 1e-4 and tray["moved_for"]["rule"] == TT.CLEAR_RULE
    assert bowl["center"] == [2.15, 3.3]                                                 # clear already: untouched
    # a top the seat covers whole: the item leaves; a corner sofa's box is left to the build's mesh check
    small = dict(table, footprint={"center": [3.0, 3.27], "size": [0.5, 0.5], "rotation_deg": 0.0})
    b2 = {"furniture": [sofa, small], "decor": [dict(tray, center=[3.0, 3.27])]}
    assert TT.clear_of_seats(b2)["dropped"] and not b2["decor"]
    corner = dict(sofa, type="sofa_corner")
    b3 = {"furniture": [corner, table], "decor": [dict(tray)]}
    assert not TT.clear_of_seats(b3)["moved"]
    # the build's check on the real meshes: an item inside another built piece is found
    seat = R.MeshCaster(*geom2d.box((3.0, 3.0, 0.2), (1.0, 1.0, 0.4)))
    inside = np.asarray(geom2d.box((2.7, 3.0, 0.38), (0.3, 0.2, 0.05))[0])
    beside = inside + np.array([-0.6, 0.0, 0.0])
    neigh = [("f_seat", seat, ((2.5, 2.5, 0.0), (3.5, 3.5, 0.4)))]
    assert R.clash_with(inside, neigh)[0] == "f_seat" and R.clash_with(beside, neigh) is None

