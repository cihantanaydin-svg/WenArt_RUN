"""30 Oct 2026, lesson UL214. The user on the UL209 preview of real06's front: "The front of real06 with veranda could
be more elegant columns up to the roof is too thick maybe there are better solutions"; of seven rendered options the
user chose D+A: slender round steel posts (EN 10219 circular hollow sections sized by height, about 1:25-1:30, on base
and cap plates) and a crisp deep edge band on a balcony's exposed edges (none along a wall, none where a lower roof
meets the edge). Pure; real06 is only the test case."""
import copy
import math

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import outdoor_review as OR
from wenart.blender import site as S
from wenart.levels import columns as LC


def _col(**kw):
    return dict({"shape": "round", "size_m": 0.4, "size_xy": [0.4, 0.4], "rotation_deg": 0.0, "center": [4.36, -1.57],
                 "source": "drawn", "id": "sd_9", "z0": 0.0, "z1": 6.0}, **kw)


def test_a_column_taller_than_a_storey_is_a_slender_round_steel_post_sized_by_its_height():
    assert LC.slender_section(6.0) == 0.2191 and 6.0 / 0.2191 < 30.0          # 1:27
    assert LC.slender_section(4.5) == 0.1683 and LC.slender_section(3.0) == 0.1143
    assert LC.slender_section(9.5) == LC.CHS_M[-1] and LC.slender_section(6.0, 0.15) == 0.15
    q = _col()
    why = LC.design_post(q)
    assert q["shape"] == "round" and q["size_m"] == 0.2191 and q["finish"] == "steel" and q["detail"] == "plate"
    assert q["drawn_look"]["size_m"] == 0.4 and q["drawn_look"]["shape"] == "round"
    assert q["adjusted_by_ai"]["lesson"] == "UL214" and "user chose" in why and "1:27" in why
    assert LC.design_post(q) is None and q["size_m"] == 0.2191                    # idempotent


def test_which_posts_change():
    light = _col(size_m=0.15, size_xy=[0.15, 0.15], z1=2.4, id=None, source="inferred")
    assert LC.design_post(light) is None and "finish" not in light               # a veranda roof's post: as it is
    thick = _col(z1=2.8)                                                          # a drawn 0.40 m single-storey column
    assert LC.design_post(thick) and thick["size_m"] == LC.CHS_M[0]
    joined = _col(z1=3.2, through=["os_bal"], size_m=0.2, size_xy=[0.2, 0.2])     # joined through a slab (UL209)
    assert LC.design_post(joined) and joined["size_m"] == LC.CHS_M[0]
    slim = _col(size_m=0.16, size_xy=[0.16, 0.16])                               # drawn slimmer than the rule
    assert LC.design_post(slim) is None and slim["size_m"] == 0.16


def test_the_family_decides_and_through_posts_follow():
    def spaces():
        ver = {"id": "os_ver", "z": 0.0, "posts": [_col(through=["os_bal"])]}
        bal = {"id": "os_bal", "z": 3.0, "posts": [],
               "through_posts": [{k: v for k, v in _col().items() if k != "source"} | {"owner": "os_ver"}]}
        return [ver, bal]
    for fam in ("classic", "rustic", "mediterranean", "traditional", None):
        sp = spaces()
        assert LC.design_columns(sp, fam) == [] and sp[0]["posts"][0]["size_m"] == 0.4
    for fam in ("scandinavian", "modern", "japandi", "industrial", "minimal", "contemporary"):
        sp = spaces()
        assert len(LC.design_columns(sp, fam)) == 1
        assert sp[1]["through_posts"][0]["size_m"] == 0.2191 and sp[1]["through_posts"][0]["finish"] == "steel"
    # a slender post still joins the post drawn on it (UL209 compares the drawn looks)
    ver = {"id": "os_ver", "z": 0.0, "posts": [_col(z1=2.8)]}
    LC.design_columns([ver], "modern")
    bal = {"id": "os_bal", "z": 3.0, "posts": [_col(z0=3.0, z1=6.0, source="inferred", id=None)]}
    assert LC.join_stacked_posts([ver, bal]) and ver["posts"][0]["z1"] == 6.0


def test_the_steel_post_is_a_shaft_between_a_base_plate_and_a_cap_plate():
    q = _col()
    LC.design_post(q)
    parts = S.steel_post_parts(q)
    assert len(parts) == 3 and len(parts[0][0]) == 2 * S.COLUMN["segments"]
    zs = [v[2] for verts, _f in parts for v in verts]
    assert min(zs) == 0.0 and max(zs) == 6.0
    r = max(math.hypot(v[0] - 4.36, v[1] + 1.57) for v in parts[0][0])
    assert abs(r - 0.2191 / 2.0) < 1e-6
    plate = max(abs(v[0] - 4.36) for v in parts[1][0])
    assert abs(plate - (0.2191 / 2.0 + S.POST_DETAIL["plate_over"])) < 1e-6
    assert abs(S.post_radius(q) - 0.2191 / 2.0) < 1e-9                         # guards and roofs stop at it
    pf = {"posts": [q], "roof": None}
    assert [p["part"] for p in S.cover_parts(pf)] == ["posts"]


def _front():
    """real06's front in small: the balcony at 3.0 over the veranda; the veranda's pitched roof meets the balcony's west
    edge (x = 1.98); the columns stand at the balcony's front corners."""
    bal_poly = [(1.98, -1.57), (4.38, -1.57), (4.38, 3.3), (1.98, 3.3)]
    col = _col(center=[4.3, -1.5], through=["os_bal"])
    LC.design_post(col)
    ver = {"id": "os_ver", "source": "outdoor_space", "z": 0.0, "elevated": False, "railing_edges": [],
           "polygon": [(-0.97, -1.82), (4.4, -1.82), (4.4, 3.5), (-0.97, 3.5)], "posts": [col],
           "roof": {"kind": "pitched", "polygon": [(-0.97, -1.82), (1.98, -1.82), (1.98, 3.3), (-0.97, 3.3)],
                    "z": 3.0, "plane": {"dir": [-1.0, 0.0], "fall": 0.25}}}
    bal = {"id": "os_bal", "source": "outdoor_space", "z": 3.0, "elevated": True, "railing_edges": [0, 1, 3],
           "polygon": bal_poly, "posts": [],
           "through_posts": [{k: col[k] for k in ("center", "shape", "size_m", "size_xy", "z0", "z1")}]}
    return ver, bal


def test_the_edge_band_runs_on_the_exposed_edges_only():
    ver, bal = _front()
    assert S.over_lower_space(bal, [ver, bal]) and not S.over_lower_space(ver, [ver, bal])
    orig = S.roof_z
    S.roof_z = lambda roof, p: 3.0 - 0.1 * (1.98 - float(p[0]))                # the lean-to falls away from the slab
    try:
        edges = S.fascia_edges(bal, [ver, bal])
    finally:
        S.roof_z = orig
    assert edges == [0, 1]           # front and east side; the west edge (3) meets the veranda roof; edge 2: a wall
    bal["fascia_edges"] = edges
    boxes = S.fascia_parts(bal)
    zs = [v[2] for verts, _f in boxes for v in verts]
    assert abs(max(zs) - (3.0 + S.FASCIA["over_floor"])) < 1e-9
    assert abs(max(zs) - min(zs) - S.FASCIA["depth"]) < 1e-9 and 0.40 <= S.FASCIA["depth"] <= 0.45
    # the band stops short of the column standing on its line, and stands outside the slab
    c, r = (4.3, -1.5), 0.2191 / 2.0
    for verts, _f in boxes:
        cx = sum(v[0] for v in verts) / len(verts)
        cy = sum(v[1] for v in verts) / len(verts)
        assert not G.point_in_polygon((cx, cy), geom2d.ccw(bal["polygon"]))
    pts = [(v[0], v[1]) for verts, _f in boxes for v in verts]
    assert all(math.hypot(p[0] - c[0], p[1] - c[1]) >= r - 0.08 for p in pts)
    # flush where the next edge has no band: never into the house's wall (edge 2), never over the lower roof (edge 3)
    assert max(p[1] for p in pts) <= 3.3 + 1e-9 and min(p[0] for p in pts) >= 1.98 - 1e-9
    # the outer corner of two bands is closed (the front run reaches the east band's outer face)
    far = S.fascia_parts(dict(bal, through_posts=[]))
    assert abs(max(v[0] for verts, _f in far for v in verts) - (4.38 + S.FASCIA["t"])) < 1e-9
    parts = S.platform_parts(bal, {"kind": "flat", "z": 0.0})
    assert "fascia" in [p["part"] for p in parts]


def test_the_review_notes_a_column_slimmer_than_drawn():
    ver, bal = _front()
    ver["space"], bal["space"] = {"kind": "veranda"}, {"kind": "balcony"}
    found, _n = OR.review({}, {"site": {"platforms": [ver, bal]}})
    notes = [f for f in found if f["metrics"].get("rule") == "O8"]
    assert notes and notes[0]["severity"] == "info" and "UL214" in notes[0]["message"]
    assert notes[0]["metrics"]["drawn_m"] == 0.4 and notes[0]["metrics"]["built_m"] == 0.2191
    assert not any("O7:" in f["message"] for f in found)
    drawn = copy.deepcopy(ver)
    drawn["posts"] = [_col()]
    found, _n = OR.review({}, {"site": {"platforms": [drawn]}})
    assert not any(f["metrics"].get("rule") == "O8" for f in found)
