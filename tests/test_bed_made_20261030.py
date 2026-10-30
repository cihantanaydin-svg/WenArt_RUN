"""A real made bed (30 Oct 2026; user on real04 run 20261029-201533-full; lessons UL136 "I did not like this bed",
UL137 "head section of this bed needs a rework", UL146 the inspiration photo P14, docs/reference_details_20261029.md
R38).

The rules, for every style family: a smooth duvet with a few soft wide folds over a quilted or uneven mattress, a
rounded edge then straight down one plane per side to one level hem (``bedding_parts.cover_grid``,
``textiles.drape_cover``), its look measured on every build (``bedding_parts.cover_smoothness``; M30 / U34 flag a
lumpy duvet or a wavy hem), a thin turned-down sheet band folded round the duvet's head edge, plump pillows with crisp
flanged edges standing in rows against the headboard, a headboard found behind a gap or on posts and the gap closed
(``rest.bed_head``, ``textiles.gap_sheet``), a made-up model with flat pillows dressed with our standing set, the P14
throw pair (the blanket over the foot, the patterned throw at one side). CPU only: synthetic beds on the pure ray
caster (``rest.MeshCaster``)."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

from wenart.blender import bedding_parts as BP
from wenart.blender import geom2d
from wenart.blender import rest as R
from wenart.blender import textiles as T

ROOT = Path(__file__).resolve().parents[1]
C = (2.5, 3.0)                                       # a 1.6 x 2.0 m bed, its head at local +Y
HOST = {"center": list(C), "size": [1.6, 2.0], "rotation_deg": 0.0}
SPEC = BP.family_spec("modern")[0]


def boxes(spec):
    """World mesh of local boxes ``(x0, y0, z0, x1, y1, z1)`` about the bed's centre ``C``."""
    parts = [geom2d.box((C[0] + (b[0] + b[3]) / 2.0, C[1] + (b[1] + b[4]) / 2.0, (b[2] + b[5]) / 2.0),
                        (b[3] - b[0], b[4] - b[1], b[5] - b[2])) for b in spec]
    return geom2d.merge(parts)


def quilt(x0, x1, y0, y1, z, amp=0.012, pitch=0.16, step=0.04):
    """A quilted mattress top (a library mattress's own relief): a grid sheet with bumps every ``pitch``."""
    xs, ys = np.arange(x0, x1 + 1e-9, step), np.arange(y0, y1 + 1e-9, step)
    verts = [(C[0] + x, C[1] + y, z + amp * (0.5 + 0.5 * np.sin(2 * np.pi * x / pitch) * np.sin(2 * np.pi * y / pitch)))
             for x in xs for y in ys]
    n = len(ys)
    faces = [[i * n + j, (i + 1) * n + j, (i + 1) * n + j + 1, i * n + j + 1]
             for i in range(len(xs) - 1) for j in range(n - 1)]
    return verts, faces


def bed(gap=0.0, posts=False, headboard=True, quilted=False, frame_out=0.0, footboard=False, roll=False):
    """A bed model: a base, a mattress (its top at 0.5 m; ``gap`` short of the headboard), a headboard (``posts``: a
    panel raised on two posts), a quilted top, a frame ``frame_out`` wider than the mattress below 0.30 m, a
    footboard, a roll lying across the mattress before the head zone."""
    spec = [(-0.8 - frame_out, -1.0, 0.05, 0.8 + frame_out, 0.94, 0.30),
            (-0.8, -1.0, 0.30, 0.8, 0.94 - gap, 0.50)]
    if headboard:
        if posts:
            spec += [(-0.8, 0.94, 0.75, 0.8, 1.0, 1.15), (-0.8, 0.94, 0.0, -0.74, 1.0, 1.15),
                     (0.74, 0.94, 0.0, 0.8, 1.0, 1.15)]
        else:
            spec.append((-0.8, 0.94, 0.0, 0.8, 1.0, 1.15))
    if footboard:
        spec.append((-0.8, -1.06, 0.0, 0.8, -1.0, 0.75))
    if roll:
        spec.append((-0.6, 0.12, 0.50, 0.6, 0.28, 0.58))
    v, f = boxes(spec)
    if quilted:
        qv, qf = quilt(-0.8, 0.8, -1.0, 0.94 - gap, 0.50)
        v, f = geom2d.merge([(v, f), (qv, qf)])
    return v, f


def caster(**kw):
    return R.MeshCaster(*bed(**kw))


def part(plan, role):
    return next(p for p in plan["parts"] if p["role"] == role)


def local(verts):
    a = np.asarray(verts, dtype=float).reshape(-1, 3)
    return a - np.array([C[0], C[1], 0.0])


# --------------------------------------------------------------------------
# UL136: the duvet (a smooth cover, a rounded edge, straight down, a level hem)
# --------------------------------------------------------------------------

def test_the_duvet_is_smooth_with_a_level_straight_hem_on_a_quilted_mattress():
    """The 29 Oct duvet followed every ray hit of the host and fluted its sides (22 mm every 18 cm): "the duvet's
    hanging sides ripple in big lumpy waves like melted foam, the hem is uneven and wavy"."""
    cast = caster(quilted=True, frame_out=-0.01)                 # a base 1 cm inside the mattress
    plan = T.bedding_set(cast, HOST, 0.0, SPEC, None)
    rec = plan["record"]
    look = rec["duvet"]["smoothness"]
    assert not look["lumpy"] and not look["wavy_hem"], look
    assert look["top_lump_m"] <= BP.LUMP_MAX_M and set(look["sides"]) == {"left", "right", "foot"}
    assert all(v["side_lump_m"] <= BP.LUMP_MAX_M and v["hem_wave_m"] <= BP.HEM_WAVE_MAX_M
               for v in look["sides"].values())
    duvet = part(plan, "duvet")
    loc = local(duvet["verts"])
    hem = SPEC["duvet"]["hem_m"]
    assert loc[:, 2].min() == pytest.approx(hem, abs=1e-6)                                 # one level hem
    for side in BP.SIDES:
        assert rec["drops"][side]["hem_over_floor_m"] == pytest.approx(hem, abs=1e-3)
    # straight down one plane on the right side: out of the mattress by the rounded edge, at most the folds more
    rho = T.CLOTH_OFFSET_M + SPEC["duvet"]["thickness_m"]
    top_n = len(loc) // 2
    hang = loc[:top_n][(loc[:top_n, 0] > 0.8) & (loc[:top_n, 2] < 0.35) & (np.abs(loc[:top_n, 1]) < 0.6)]
    assert hang[:, 0].min() >= 0.8 + rho - 1e-6
    assert hang[:, 0].max() <= 0.8 + rho + BP.SIDE_FOLD_AMP_M[1] + 1e-6
    assert 0.003 < float(np.ptp(hang[:, 0]))                                               # soft folds, not a board
    assert R.penetration(cast, duvet["verts"]) <= 0.002                                    # never into the bed
    # the cloth thins to its seam: the hem's thickness a share of the duvet's
    bottom = loc[top_n:]
    at_hem = np.abs(loc[:top_n, 2] - hem) < 1e-6
    gap = np.linalg.norm(loc[:top_n][at_hem] - bottom[at_hem], axis=1)
    assert gap.max() <= SPEC["duvet"]["thickness_m"] * BP.RIM_SHARE + 1e-6


def test_the_measure_flags_the_29_oct_flutes_and_a_wavy_hem():
    xs, ys = np.linspace(-0.8, 0.8, 41), np.linspace(-1.0, 0.5, 38)
    host = np.full((len(xs), len(ys)), 0.5)
    cover = BP.cover_grid(xs, ys, host, {"left": 0.5, "right": 0.5, "foot": 0.5}, 0.06, 0.005, 0.065, 0.009)
    args = (cover["local"], cover["on_top"], cover["edges"])
    good = BP.cover_smoothness(cover["grid"], *args)
    assert not good["lumpy"] and not good["wavy_hem"]
    # the flutes of 29 Oct: 22 mm out of the side every 18 cm
    g = cover["grid"].copy()
    down = (~cover["on_top"]) & (cover["hang_s"] > cover["arc_m"])
    edge = cover["edge_local"]
    delta = 0.022 * (0.5 + 0.5 * np.sin(2.0 * np.pi * (edge[..., 0] + edge[..., 1]) / 0.18 + 0.6))
    g[..., 0] += np.where(down, delta * cover["out_dir"][..., 0], 0.0)
    g[..., 1] += np.where(down, delta * cover["out_dir"][..., 1], 0.0)
    lumpy = BP.cover_smoothness(g, *args)
    assert lumpy["lumpy"] and max(v["side_lump_m"] for v in lumpy["sides"].values()) > BP.LUMP_MAX_M
    # a hem 3 cm higher every other point (rows hung from edge points of different heights)
    g2 = cover["grid"].copy()
    g2[-1, ::2, 2] += 0.03
    assert BP.cover_smoothness(g2, *args)["wavy_hem"]
    # lumps on the top (a duvet following a quilted mattress)
    g3 = cover["grid"].copy()
    g3[..., 2] += np.where(cover["on_top"], 0.012 * np.sin(2 * np.pi * cover["local"][..., 0] / 0.16)
                           * np.sin(2 * np.pi * cover["local"][..., 1] / 0.16), 0.0)
    assert BP.cover_smoothness(g3, *args)["top_lump_m"] > BP.LUMP_MAX_M


def test_a_wider_frame_below_is_cleared_and_a_footboard_stops_the_duvet():
    wide = caster(frame_out=0.04)                                 # the frame 4 cm out of the mattress below 0.30 m
    plan = T.bedding_set(wide, HOST, 0.0, SPEC, None)
    duvet = part(plan, "duvet")
    assert R.penetration(wide, duvet["verts"]) <= 0.002
    measure = plan["record"]["duvet"]["measure"]
    assert set(measure["flare"]) == {"left", "right"}
    loc = local(duvet["verts"])
    low = loc[(loc[:, 0] > 0.8) & (loc[:, 2] < 0.25) & (np.abs(loc[:, 1]) < 0.6)]
    assert low[:, 0].min() >= 0.84                                                         # outside the frame
    # the bed's own footboard rising over the mattress: the duvet ends before it, no hang at the foot
    foot = caster(footboard=True)
    plan2 = T.bedding_set(foot, HOST, 0.0, SPEC, None)
    rec = plan2["record"]
    assert "foot" in rec["duvet"]["measure"]["own_rails"] and rec["drops"]["foot"]["drop_m"] == 0.0
    assert local(part(plan2, "duvet")["verts"])[:, 1].min() >= -1.0 - 1e-6
    assert R.penetration(foot, part(plan2, "duvet")["verts"]) <= 0.002


def test_the_turned_down_band_is_a_thin_sheet_folded_round_the_duvets_head():
    """29 Oct: "the turned-down band at the head is a thick rigid slab" (3.9 cm thick, 3.75 cm over the duvet)."""
    plan = T.bedding_set(caster(), HOST, 0.0, SPEC, None)
    band = part(plan, "turndown")
    v = np.asarray(band["verts"])
    n = len(v) // 2
    assert np.linalg.norm(v[:n] - v[n:], axis=1).max() <= BP.SHEET_T_M + 1e-6           # a sheet, not a slab
    rec = plan["record"]["duvet"]["band"]
    assert 0.02 <= rec["fold_m"] <= 0.045 and rec["width_m"] == T.TURN_DOWN_M
    # it lies on the duvet (its underside over the duvet's top) and wraps the duvet's head end
    duvet = local(part(plan, "duvet")["verts"])
    head_y = plan["record"]["duvet_rect_local"][3]
    lb = local(v)
    assert lb[:, 1].max() > head_y + 0.005 and lb[:, 1].max() <= head_y + 0.03          # the fold round the edge
    mid = (np.abs(lb[:n, 0]) < 0.3) & (lb[:n, 1] < head_y - 0.08)
    top = (np.abs(duvet[:, 0]) < 0.3) & (duvet[:, 1] > head_y - T.TURN_DOWN_M) & (duvet[:, 1] < head_y - 0.08)
    assert lb[n:][mid][:, 2].min() >= duvet[top][:, 2].max() - 0.012                      # on it, not floating
    assert lb[:n][mid][:, 2].max() <= duvet[top][:, 2].max() + 0.02


def test_pillows_are_plump_with_crisp_flanged_edges():
    sham = BP.plump_cushion(0.65, 0.14, 0.62, key="x", role=T.SHAM_ROLE)
    v = np.asarray(sham["verts"])
    centre = (np.abs(v[:, 0]) < 0.05) & (np.abs(v[:, 2] - 0.31) < 0.05)
    assert np.ptp(v[centre, 1]) > 0.13                                                    # full in the middle
    flange = np.abs(v[:, 0]) > 0.325 - BP.FLANGE_M[T.SHAM_ROLE] * 0.99                    # the flat border
    assert np.ptp(v[flange, 1]) <= BP.FLANGE_T_M + 1e-9
    edges = Counter()
    for f in sham["faces"]:
        for a, b in zip(f, f[1:] + f[:1]):
            edges[tuple(sorted((a, b)))] += 1
    assert set(edges.values()) == {2}                                                    # closed
    pillow = np.asarray(BP.plump_cushion(0.65, 0.15, 0.45, key="x", role="pillow")["verts"])
    assert (np.abs(pillow[:, 0]) > 0.325 - BP.FLANGE_M["pillow"] * 0.99).any()
    plain = np.asarray(BP.plump_cushion(0.45, 0.15, 0.45, key="x", role="x")["verts"])
    assert len(plain) < len(pillow)                                                       # a role without a flange


# --------------------------------------------------------------------------
# UL137: the head (a headboard behind a gap or on posts, the gap closed)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("posts", [False, True])
def test_a_headboard_behind_a_gap_or_on_posts_is_found_and_the_gap_closed(posts):
    cast = caster(gap=0.08, posts=posts)
    plan = T.bedding_set(cast, HOST, 0.0, SPEC, None)
    rec = plan["record"]
    assert rec["set"]["euro_shams"] == 2 and rec["pillows_upright"] is True and rec["explained"] == {}
    head = rec["head"]
    assert head["headboard"] and head["gap_m"] == pytest.approx(0.08, abs=0.02) and head["closed_by"]
    for sham in [p for p in plan["parts"] if p["role"] == T.SHAM_ROLE]:
        loc = local(sham["verts"])
        assert loc[:, 1].max() <= 0.94 + 1e-3                                              # at the headboard's face
        assert loc[:, 2].min() >= 0.5 - R.SOFT_SINK_M - 1e-3                               # on the mattress
    sheet = local(part(plan, T.GAP_SHEET_ROLE)["verts"])
    assert 0.93 <= sheet[:, 1].max() < 0.94 and sheet[:, 1].min() < 0.94 - 0.08           # to the headboard's face
    assert sheet[:, 2].min() > 0.5 - 0.03                                                  # over the gap, a little sag
    # no gap: no sheet
    plain = T.bedding_set(caster(), HOST, 0.0, SPEC, None)
    assert T.GAP_SHEET_ROLE not in {p["role"] for p in plain["parts"]} and plain["record"]["head"]["gap_m"] < 0.02


def test_a_raised_section_nearer_the_middle_no_longer_hides_the_headboard():
    cast = caster(roll=True)
    planned = R.to_world(C, 0.0, -0.36, 0.86)
    pose = R.place_leaning(cast, HOST, planned, (0.61, 0.14, 0.62), lean_deg=T.SHAM_LEAN_DEG, bed=True)
    assert pose is not None and not pose["how"].startswith("no backrest hit")
    y = R.to_local(C, 0.0, *pose["center"])[1]
    assert 0.94 - 0.2 < y < 0.94


def test_lying_pillows_without_a_headboard_stay_on_the_bed():
    """29 Oct: a pillow lying 14 degrees off flat had its middle at the head edge and poked 0.2 m past the bed."""
    plan = T.bedding_set(caster(headboard=False), HOST, 0.0, SPEC, None)
    for p in [q for q in plan["parts"] if q["role"] == "pillow"]:
        assert local(p["verts"])[:, 1].max() <= 1.0 + 0.01


def test_a_made_up_bed_with_flat_pillows_gets_our_standing_set_on_them():
    """The real04 f_L0_007 case: a made-up model, two flat pillows low in front of a panel raised on posts, a gap."""
    v, f = bed(gap=0.06, posts=True)
    own = boxes([(-0.8, -1.0, 0.50, 0.8, 0.3, 0.53), (-0.7, 0.42, 0.50, -0.05, 0.88, 0.62),
                 (0.05, 0.42, 0.50, 0.7, 0.88, 0.62)])
    cast = R.MeshCaster(*geom2d.merge([(v, f), own]))
    plan = T.bedding_set(cast, HOST, 0.0, SPEC, None, mode="pillows")
    rec = plan["record"]
    assert rec["set"]["euro_shams"] == 2 and rec["pillows_upright"]
    assert "duvet" not in {p["role"] for p in plan["parts"]}
    for sham in [p for p in plan["parts"] if p["role"] == T.SHAM_ROLE]:
        loc = local(sham["verts"])
        assert loc[:, 2].min() >= 0.5 - R.SOFT_SINK_M - 1e-3 and loc[:, 1].max() <= 0.94 + 1e-3


# --------------------------------------------------------------------------
# UL146: the P14 layers (the blanket over the foot, the patterned throw at one side)
# --------------------------------------------------------------------------

def test_the_p14_layers_on_a_dressed_bed():
    cast = caster()
    plan = T.bedding_set(cast, HOST, 0.0, SPEC, None)
    dv, df = [], []
    for p in plan["parts"]:
        off = len(dv)
        dv += [tuple(x) for x in p["verts"]]
        df += [[i + off for i in q] for q in p["faces"]]
    dressed = R.MultiCaster([cast, R.MeshCaster(dv, df)])
    item = {"id": "t", "type": "throw", "center": [C[0], C[1] - 0.72], "size": [1.52, 0.5, 0.05], "layers": 2,
            "colour": "cream", "accent_colour": "charcoal", "rotation_deg": 0.0,
            "weave": dict(BP.throw_weave("modern"), fringe_ends=["left", "right"])}
    host = {"id": "b", "type": "bed_double", "footprint": HOST,
            "bedding_layers": {"sides": {s: {"free": True} for s in BP.SIDES}}}
    got = R.plan_throw(item, host, dressed, 0.0)
    assert "not_rested" not in got, got
    weave = got["weave"]
    assert weave["layout"] == "p14" and weave["throw_side"] == "right" and weave["fringe_strands"] > 60
    assert not weave["blanket_look"]["lumpy"] and not weave["blanket_look"]["wavy_hem"]
    blanket, throw = (local(p["verts"]) for p in got["parts"][:2])
    duvet = local(part(plan, "duvet")["verts"])
    assert blanket[:, 2].max() > duvet[:, 2].max() - 0.02                                   # over the duvet
    assert blanket[:, 2].min() == pytest.approx(duvet[(np.abs(duvet[:, 0]) < 0.5)][:, 2].max() - T.BLANKET_DROP_M,
                                                abs=0.05)
    assert throw[:, 0].min() > 0.0 and throw[:, 1].max() > blanket[:, 1].max()               # at the side
    assert R.penetration(dressed, got["parts"][0]["verts"]) <= 0.007


# --------------------------------------------------------------------------
# the checks and the lessons
# --------------------------------------------------------------------------

def test_the_review_flags_a_lumpy_duvet_a_wavy_hem_and_an_open_head_gap():
    import _m11_room as M

    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None,
                   furniture=[M.fp("f_L0_001", "bed_double", C, (1.6, 2.0), rotation=0.0)])
    b["dressing"] = {"family": "modern"}
    full = BP.counts(SPEC, 1.6)

    def manifest(look=None, head=None, blanket=None):
        rec = {"set": dict(full), "explained": {}, "mode": "full", "sides": {s: {"free": True} for s in BP.SIDES},
               "drops": {s: {"drop_m": 0.44, "hem_over_floor_m": 0.06} for s in BP.SIDES},
               "duvet": {"smoothness": look} if look else {}, "head": head or {}}
        weave = {"pattern": "houndstooth", "fringe": True, "fringe_strands": 80}
        if blanket:
            weave["blanket_look"] = blanket
        return {"objects": [{"kind": "furniture", "wenart_id": "f_L0_001", "type": "bed_double",
                             "dressing": {"record": rec}},
                            {"kind": "decor", "type": "throw", "host_id": "f_L0_001", "weave": weave}],
                "style_profile": {"family": "modern"}}

    ok = {"top_lump_m": 0.003, "sides": {"left": {"side_lump_m": 0.003, "hem_wave_m": 0.004}}, "lumpy": False,
          "wavy_hem": False}
    assert BP.review(b, manifest(ok))[0] == []
    bad = dict(ok, sides={"left": {"side_lump_m": 0.013, "hem_wave_m": 0.03}}, lumpy=True, wavy_hem=True)
    got, _n = BP.review(b, manifest(bad))
    assert sorted(g["problem"] for g in got) == ["lumpy_duvet", "wavy_hem"] and {g["lesson"] for g in got} == {"UL136"}
    got, _n = BP.review(b, manifest(ok, head={"gap_m": 0.08}))
    assert [(g["problem"], g["lesson"]) for g in got] == [("head_gap", "UL137")]
    assert BP.review(b, manifest(ok, head={"gap_m": 0.08, "closed_by": "a sheet"}))[0] == []
    got, _n = BP.review(b, manifest(ok, blanket=bad))
    assert {g["problem"] for g in got} == {"lumpy_duvet", "wavy_hem"} and "blanket" in got[0]["message"]


def test_lessons_ul136_ul137_ul146_are_built():
    rows = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    got = {x["id"]: x for x in rows["lessons"] if x["id"] in ("UL136", "UL137", "UL146")}
    assert set(got) == {"UL136", "UL137", "UL146"}
    for ul in got.values():
        assert ul["status"] == "built" and ul["checks"] == ["build"], ul["id"]
    assert "cover_grid" in got["UL136"]["lesson"] and "bed_head" in got["UL137"]["lesson"]
    assert "p14_throw_parts" in got["UL146"]["lesson"]
    from wenart.audit import lessons as AL

    cov = AL.coverage()
    assert all("U34" in cov[k]["code"] for k in ("UL136", "UL137", "UL146"))


def test_the_bedding_is_one_mesh_of_a_few_parts():
    plan = T.bedding_set(caster(gap=0.08), HOST, 0.0, SPEC, None)
    assert len(plan["parts"]) <= 14
    from wenart.blender import furniture as F

    verts, faces, keys = F.dressing_mesh(plan["parts"])
    assert len(set(keys)) <= 9 and len(verts) < 20000
    assert plan["record"]["duvet"]["measure"]["rays"] < 2500                              # rays of the duvet's drape
