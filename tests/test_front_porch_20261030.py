"""30 Oct 2026, lesson UL209 (user on real06 run 20261029-100801-full's front, the veranda under the balcony: "This
front section requires a huge rework, it is not elegant, columns seems cut in the middle handrails not making sense
this whole area requires a huge rework try a lot on this area"). General rules, pure tests; real06 is only the case:

- a column under a balcony that carries the roof above it is one column through the slab (``wenart.levels.columns``),
  a smooth shaft on a slim base under a slim head (``site.column_parts``);
- a lower roof and its edge beams are cut around a column that rises through them;
- an upper slab's guard stands in from its edge, one straight run per side, and stops at the columns; a glass family's
  guard there is frameless glass in a channel (``details.framed_kind``);
- a cover's edge faces are its fascia (``site.cover_face_slots``), not the roof covering;
- a deck's three-riser flight takes no handrails (four or more risers do: IRC R311.7.8);
- an outdoor sofa or armchair is an open teak lounge frame with cushions (``parametric._outdoor_sofa``);
- the model review's O7 finds a column a slab still cuts in two.
"""
import copy
import math

from wenart.blender import details as D
from wenart.blender import grading as GR
from wenart.blender import outdoor_review as OR
from wenart.blender import parametric as P
from wenart.blender import site as S
from wenart.levels import columns as LC


def _spaces():
    """real06's front in small: a veranda at 0.0 with a drawn 0.40 m round column under the balcony's corner, the
    balcony at 3.0 with the house-roof post standing on that column up to the eaves at 6.0."""
    col = {"shape": "round", "size_m": 0.4, "size_xy": [0.4, 0.4], "rotation_deg": 0.0}
    veranda = {"id": "os_ver", "z": 0.0, "posts": [dict(col, center=[4.36, -1.57], source="drawn", id="sd_9", z0=0.0,
                                                        z1=2.8, carries="the slab of os_bal")]}
    balcony = {"id": "os_bal", "z": 3.0, "posts": [dict(col, center=[4.36, -1.57], source="inferred", id=None,
                                                        z0=3.0, z1=6.0, carries="the building's roof")]}
    return [veranda, balcony]


def test_a_column_under_a_balcony_is_one_piece_through_the_slab():
    spaces = _spaces()
    why = LC.join_stacked_posts(spaces)
    ver, bal = spaces
    assert len(why) == 1 and "UL209" in why[0]
    assert ver["posts"][0]["z0"] == 0.0 and ver["posts"][0]["z1"] == 6.0 and ver["posts"][0]["through"] == ["os_bal"]
    assert bal["posts"] == [] and bal["through_posts"][0]["owner"] == "os_ver"
    assert LC.join_stacked_posts(spaces) == []                         # idempotent
    other = _spaces()
    other[1]["posts"][0].update(size_m=0.16, size_xy=[0.16, 0.16], shape="square")
    assert LC.join_stacked_posts(other) == [] and other[0]["posts"][0]["z1"] == 2.8      # another look: no join


def test_a_column_is_a_smooth_shaft_on_a_base_under_a_head():
    col = {"center": [0.0, 0.0], "shape": "round", "size_m": 0.4, "z0": 0.0, "z1": 6.0}
    parts = S.column_parts(col)
    assert len(parts) == 3
    shaft = parts[0]
    assert len(shaft[0]) == 2 * S.COLUMN["segments"]
    zs = [v[2] for v, _f in parts for v in v]
    assert min(zs) == 0.0 and max(zs) == 6.0
    base_r = max(math.hypot(v[0], v[1]) for v in parts[1][0])
    assert base_r > 0.2 + S.COLUMN["base_over"] - 1e-6
    post = S.column_parts({"center": [0, 0], "shape": "round", "size_m": 0.15, "z0": 0.0, "z1": 2.4})
    assert len(post) == 1 and len(post[0][0]) == 2 * S.COVER["post_segments"]


def test_runs_stop_at_columns_and_guards_stand_in_from_the_edge():
    runs = S.free_runs((0.0, 0.0), (4.0, 0.0), [((2.0, 0.0), 0.2)], 0.03)
    assert [(r[2], r[3]) for r in runs] == [(False, True), (True, False)]
    assert math.isclose(runs[0][1][0], 2.0 - 0.23, abs_tol=1e-6) and math.isclose(runs[1][0][0], 2.23, abs_tol=1e-6)
    # a 4 x 3 slab against walls on its north and west sides, guarded on the south and east; the south edge split
    # into pieces (subdivide_edges) is one run
    poly = [(0.0, 0.0), (2.0, 0.0), (4.0, 0.0), (4.0, 3.0), (0.0, 3.0)]
    lines = S.guard_lines(poly, [0, 1, 2], 0.05)
    assert len(lines) == 2
    (a, b), (c, d) = lines
    assert math.isclose(a[0], 0.0, abs_tol=1e-9) and math.isclose(a[1], 0.05) and math.isclose(b[0], 3.95)
    assert math.isclose(c[0], 3.95) and math.isclose(c[1], 0.05) and math.isclose(d[1], 3.0)


def test_an_upper_slabs_guard_never_passes_through_a_column():
    spaces = _spaces()
    LC.join_stacked_posts(spaces)
    pf = {"id": "os_bal", "kind": "terrace", "polygon": [(1.98, -1.57), (4.38, -1.57), (4.38, 3.3), (1.98, 3.3)],
          "holes": [], "z": 3.0, "sloped": False, "elevated": True, "railing_edges": [0, 3],
          "against_edges": [1, 2], "edge": "none", "pools": [], "posts": [],
          "through_posts": spaces[1]["through_posts"], "balustrade": "glass_posts"}
    parts = S.platform_parts(pf, {"kind": "flat", "z": 0.0})
    rail = next(p for p in parts if p["part"] == "railing")
    for x, y, _z in rail["verts"]:
        assert math.hypot(x - 4.36, y + 1.57) >= 0.2 + S.COLUMN["guard_gap_m"] - 0.06    # the clamp boxes aside
    assert D.framed_kind("glass_posts") == "glass_channel" and D.framed_kind("bars") == "bars"
    assert all(min(v[1] for v in m_v) > -1.57 for m_v, _f in [(rail["verts"], None)])   # in from the south edge


def test_a_lower_roof_is_cut_around_the_column_rising_through_it():
    outer, holes = S.roof_around_columns([(0, 0), (2, 0), (2, 2), (0, 2)], [((1.0, 1.0), 0.2)])
    assert len(holes) == 1 and len(outer) == 4
    outer, holes = S.roof_around_columns([(0, 0), (2, 0), (2, 2), (0, 2)], [((2.0, 1.0), 0.2)])
    assert not holes and len(outer) > 4 and all(math.hypot(x - 2.0, y - 1.0) >= 0.2 for x, y in outer)
    pf = {"roof": {"kind": "pitched", "polygon": [(0, 0), (2, 0), (2, 2), (0, 2)], "top_z": 3.0, "thickness": 0.18,
                   "fall": 0.1, "plane": {"origin": [2, 0], "dir": [-1, 0]},
                   "open_edges": [[[0, 0], [2, 0]]]},
          "posts": [{"center": [2.0, 0.0], "shape": "round", "size_m": 0.4, "z0": 0.0, "z1": 6.0}]}
    roof = next(p for p in S.cover_parts(pf) if p["part"] == "roof")
    assert all(math.hypot(x - 2.0, y) >= 0.2 for x, y, _z in roof["verts"])
    beams = next(p for p in S.cover_parts(pf) if p["part"] == "beams")
    assert max(x for x, _y, _z in beams["verts"]) <= 2.0 - 0.2 + 1e-6


def test_a_covers_edges_are_its_fascia():
    v, f = S.slab_with_holes([(0, 0), (2, 0), (2, 1), (0, 1)], [], 3.0, 2.8)
    slots = S.cover_face_slots(v, f)
    assert set(slots) == {0, 1, 2} and slots.count(2) == 4


def test_a_three_riser_deck_flight_has_no_handrails():
    pf = {"id": "v", "kind": "terrace", "polygon": [(0, 0), (4, 0), (4, 4), (0, 4)], "holes": [], "z": 0.5,
          "sloped": False, "steps_edge": 3, "edge": "steps", "pools": []}
    seen = set()
    for z in (0.3, 0.42, 0.48, 0.6, 0.8, 1.0, 1.2):
        fl = GR.down_flight(dict(pf, z=z), lambda x, y: 0.0)
        want = fl["count"] >= GR.GRADE["deck_rail_min_risers"] and fl["rise"] > 0.45
        assert fl["handrails"] == want, (z, fl["count"], fl["rise"])
        seen.add(fl["handrails"])
    assert seen == {True, False}
    # real06's veranda: its drawn two treads (three risers) over 0.50 m stand free
    drawn = GR.down_flight(dict(pf, steps_at={"point": [0.0, 2.0], "width": 1.3, "tread": 0.25, "treads": 2,
                                              "source": "drawn"}), lambda x, y: 0.0)
    assert drawn["count"] == 3 and not drawn["handrails"]


def test_an_outdoor_sofa_is_an_open_teak_frame_with_cushions():
    piece = {"asset": {"method": "parametric", "outdoor_build": {"wood": "wood_veneer_teak"}}}
    parts = P._sofa(2.0, 0.85, 0.85, piece=piece)
    roles = {p["role"] for p in parts}
    assert {"slat", "leg", "arm", "cushion", "back_cushion"} <= roles and "body" not in roles
    xs = [v[0] for p in parts for v in p["verts"]]
    zs = [v[2] for p in parts for v in p["verts"]]
    assert min(xs) >= -1.0 - 1e-9 and max(xs) <= 1.0 + 1e-9 and min(zs) >= 0.0 and max(zs) <= 0.85 + 1e-9
    assert {p["key"] for p in parts} == {"wood", "fabric"}
    assert "body" in {p["role"] for p in P._sofa(2.0, 0.85, 0.85, piece={})}       # inside: the upholstered sofa


def test_the_review_finds_a_column_the_slab_cuts():
    spaces = _spaces()
    pfs = [{"id": s["id"], "source": "outdoor_space", "z": s["z"], "elevated": s["z"] > 1.0, "posts": s["posts"],
            "polygon": [(1.98, -1.57), (4.38, -1.57), (4.38, 3.3), (1.98, 3.3)], "space": {"kind": "balcony"}}
           for s in spaces]
    found, _n = OR.review({}, {"site": {"platforms": copy.deepcopy(pfs)}})
    assert any("O7:" in f["message"] for f in found)
    LC.join_stacked_posts(spaces)
    for pf, s in zip(pfs, spaces):
        pf["posts"] = s["posts"]
    found, _n = OR.review({}, {"site": {"platforms": pfs}})
    assert not any("O7:" in f["message"] for f in found)
