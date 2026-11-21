"""The Swiss Dwellings converter and the Turkish drafting profile (21 Nov 2026, user OK: dataset test bench).

The converter writes a valid DXF, its truth matches its own drawing (labels in their rooms, area texts, a swing arc
per door, walls drawn where the truth lists them, the truth scores 100 against itself), and the profile decides the
drawing's conventions (layer names, tag forms).
"""
from __future__ import annotations

import copy
import math
import json
import random
import re

import ezdxf
import pytest
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from wenart.datasets import style as ST
from wenart.datasets import swiss_convert as SCV
from wenart.datasets import turkish_profile as TP
from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

ANGLE = 17.0


def _row(sub, etype, poly, area_id="", unit="u1"):
    g = affinity.rotate(poly, ANGLE, origin=(100.0, 50.0))
    return {"apartment_id": "a1", "area_id": area_id, "building_id": "424242", "entity_subtype": sub,
            "entity_type": etype, "floor_id": "9001", "geometry": g.wkt, "site_id": "7", "unit_id": unit}


def _flat_rows() -> list:
    """An 8 x 5 m flat (outer walls 25 cm, an inner wall of 12 cm at x = 4), a door in the inner wall, a window in the
    bottom wall, a living room and a bedroom, a stair flight; drawn rotated by ``ANGLE`` like the dataset."""
    t = 0.25
    walls = [box(0, 0, 8, t), box(0, 5 - t, 8, 5), box(0, 0, t, 5), box(8 - t, 0, 8, 5), box(3.94, t, 4.06, 5 - t)]
    rows = [_row("WALL", "separator", w) for w in walls]
    rows.append(_row("DOOR", "opening", box(3.94, 2.05, 4.06, 2.95)))
    rows.append(_row("WINDOW", "opening", box(1.5, 0.0, 2.7, t)))
    rows.append(_row("LIVING_ROOM", "area", box(t, t, 3.94, 5 - t), "1"))
    rows.append(_row("BEDROOM", "area", box(4.06, t, 8 - t, 5 - t), "2"))
    rows.append(_row("STAIRS", "feature", box(0.5, 1.0, 1.5, 3.8)))
    return rows


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    out = tmp_path_factory.mktemp("swiss")
    truth = SCV.convert_building({"9001": _flat_rows()}, out, "swiss-test", seed=5,
                                 overrides={"unit": "cm", "insunits": 5, "dims_as_entities": True})
    return out / "swiss-test", truth


def _to_building(truth, xy):
    upm = truth["drawing"]["units_per_metre"]
    o = truth["drawing"]["plans"][0]["origin_m"]
    return (xy[0] / upm - o[0], xy[1] / upm - o[1])


def test_dxf_is_valid_and_truth_counts(project):
    pdir, truth = project
    doc = ezdxf.readfile(str(pdir / "plan.dxf"))
    assert not doc.audit().has_errors
    lv = truth["per_level"]["L0"]
    assert [r["room_type"] for r in sorted(lv["rooms"], key=lambda r: r["centroid"][0])] == ["living", "bedroom"]
    assert len(lv["doors"]) == 1 and len(lv["windows"]) == 1 and len(lv["stairs"]) == 1
    assert len(lv["walls"]) == 5
    assert lv["doors"][0]["width"] == pytest.approx(0.9)
    assert lv["windows"][0]["width"] == pytest.approx(1.2)
    # the rotation is undone: every wall runs along an axis, the frame starts at the walls' min corner
    for w in lv["walls"]:
        assert w["start"][0] == pytest.approx(w["end"][0]) or w["start"][1] == pytest.approx(w["end"][1])
    rects = unary_union([LineString([w["start"], w["end"]]).buffer(w["thickness"] / 2, cap_style=2)
                         for w in lv["walls"]])
    assert rects.bounds[0] == pytest.approx(0.0, abs=0.006) and rects.bounds[1] == pytest.approx(0.0, abs=0.006)
    assert (pdir / "ATTRIBUTION.md").read_text(encoding="utf-8").count("CC BY 4.0") >= 1


def test_truth_matches_its_drawing(project):
    pdir, truth = project
    doc = ezdxf.readfile(str(pdir / "plan.dxf"))
    st = truth["style"]
    lay = st["layers"]
    msp = doc.modelspace()
    lv = truth["per_level"]["L0"]
    rooms = [(Polygon(r["polygon"]), r) for r in lv["rooms"]]
    labels = [e for e in msp.query("TEXT") if e.dxf.layer == lay["room_label"]
              and any(e.dxf.text == r["label"] for _p, r in rooms)]
    for poly, r in rooms:
        at = [_to_building(truth, (e.dxf.align_point.x, e.dxf.align_point.y)) for e in labels
              if e.dxf.text == r["label"]]
        assert any(poly.contains(Point(p)) for p in at), r["label"]
        area = ST.area_text(r["area"], ST.Style(**{k: v for k, v in st.items() if k != "seed"}, seed=st["seed"]))
        assert any(e.dxf.text == area for e in msp.query("TEXT")), area
    # one swing arc per door, its radius the door's width, its centre at an end of the door's gap
    arcs = [e for e in msp.query("ARC") if e.dxf.layer == lay["door"]]
    assert len(arcs) == len(lv["doors"])
    d = lv["doors"][0]
    c = _to_building(truth, (arcs[0].dxf.center.x, arcs[0].dxf.center.y))
    assert arcs[0].dxf.radius / truth["drawing"]["units_per_metre"] == pytest.approx(d["width"], abs=1e-6)
    assert abs(Point(c).distance(Point(d["center"])) - d["width"] / 2) < 0.2
    # the drawn wall faces stand where the truth lists walls, the gaps where it lists openings
    rings = [Polygon([_to_building(truth, (x, y)) for x, y, *_ in e.get_points()]) for e in msp.query("LWPOLYLINE")
             if e.dxf.layer == lay["wall"]]
    outer = max(rings, key=lambda p: p.area)
    body = outer.difference(unary_union([p for p in rings if p is not outer]))
    for w in lv["walls"]:
        mid = ((w["start"][0] + w["end"][0]) / 2, (w["start"][1] + w["end"][1]) / 2)
        off = [Point(mid).distance(Point(o["center"])) for o in lv["doors"] + lv["windows"]]
        if min(off) > 0.8:
            assert body.buffer(0.002).contains(Point(mid)), w["id"]
    for o in lv["doors"] + lv["windows"]:
        assert not body.buffer(-0.01).contains(Point(o["center"])), o["id"]


def test_truth_scores_100_against_itself(project):
    pdir, _truth = project
    truth = TR.synthetic_truth("swiss-test", pdir / "truth" / "reading_truth.json")
    read = copy.deepcopy(truth)
    res = SC.match(truth, read)
    assert res["total"] == 100.0
    for k in ("rooms", "doors", "windows", "walls", "stairs"):
        assert res[k]["f1"] == 1.0, k


def test_profile_decides_the_conventions(tmp_path):
    prof = TP.load()
    assert prof["projects"] >= 10 and prof["layers"]["wall"] and prof["room_labels"]
    test = json.loads(json.dumps(prof))
    test["layers"]["wall"] = {"ZZ_DUVAR_TEST": {"share": 1.0, "projects": 9}}
    test["shapes"]["door_tag"] = {"K:99/999": {"share": 1.0, "projects": 9}}
    test["assumed"]["two_text_tag_share"] = 0.0
    truth = SCV.convert_building({"9001": _flat_rows()}, tmp_path, "swiss-prof", profile=test, seed=11,
                                 overrides={"unit": "cm", "insunits": 5})
    doc = ezdxf.readfile(str(tmp_path / "swiss-prof" / "plan.dxf"))
    assert truth["style"]["layers"]["wall"] == "ZZ_DUVAR_TEST"
    assert any(e.dxf.layer == "ZZ_DUVAR_TEST" for e in doc.modelspace().query("LWPOLYLINE"))
    assert any(re.fullmatch(r"K:90/210", e.dxf.text) for e in doc.modelspace().query("TEXT"))


def test_styles_vary_within_the_profile():
    prof = TP.load()
    styles = [ST.sample_style(prof, random.Random(s), s) for s in range(60)]
    walls = [s.layers["wall"] for s in styles]
    assert max(set(walls), key=walls.count) == max(prof["layers"]["wall"],
                                                   key=lambda k: prof["layers"]["wall"][k]["projects"])
    for field in ("door_tag", "window_tag", "area_tpl", "unit"):
        assert len({getattr(s, field) for s in styles}) >= 2, field
    assert len({s.layers["door"] for s in styles}) >= 3


def _angled_rows() -> list:
    """The flat of ``_flat_rows`` with its right-hand side cut by a wall at 30 degrees, a window in that wall (user, 21
    Nov 2026: "include slanted walls in the bench too")."""
    t = 0.25
    slant = LineString([(6.0, 0.0), (8.0, 3.4641)])                  # 60 degrees from the x axis
    slanted = slant.buffer(t / 2, cap_style=2)
    walls = [box(0, 0, 6.0, t), box(0, 5 - t, 8, 5), box(0, 0, t, 5), box(8 - t, 3.4641, 8, 5),
             box(3.94, t, 4.06, 5 - t), slanted]
    rows = [_row("WALL", "separator", w) for w in walls]
    mid = slant.interpolate(0.5, normalized=True)
    win = affinity.rotate(box(mid.x - 0.6, mid.y - t / 2, mid.x + 0.6, mid.y + t / 2), 60.0, origin=mid)
    rows.append(_row("WINDOW", "opening", win))
    rows.append(_row("DOOR", "opening", box(3.94, 2.05, 4.06, 2.95)))
    rows.append(_row("LIVING_ROOM", "area", box(t, t, 3.94, 5 - t), "1"))
    rows.append(_row("BEDROOM", "area", box(4.3, 0.5, 6.5, 4.5), "2"))
    return rows


def test_angled_walls_are_drawn_at_their_angle(tmp_path):
    truth = SCV.convert_building({"9001": _angled_rows()}, tmp_path, "swiss-angled", seed=3,
                                 overrides={"unit": "cm", "insunits": 5})
    lv = truth["per_level"]["L0"]
    assert truth["dataset"]["bench_class"] == "angled" and truth["dataset"]["angled_share"] > 0.1
    angles = [math.degrees(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0])) % 180 for w in
              lv["walls"]]
    assert any(abs(a - 60.0) < 1.0 for a in angles)
    assert len(lv["windows"]) == 1 and len(lv["rooms"]) == 2
    win = lv["windows"][0]
    slanted = next(w for w, a in zip(lv["walls"], angles) if abs(a - 60.0) < 1.0)
    assert LineString([slanted["start"], slanted["end"]]).distance(Point(win["center"])) < 0.01
    doc = ezdxf.readfile(str(tmp_path / "swiss-angled" / "plan.dxf"))
    tag_layer = truth["style"]["layers"]["window_tag"]
    rots = [e.dxf.rotation for e in doc.modelspace().query("TEXT") if e.dxf.layer == tag_layer
            and re.fullmatch(r"[A-Z:]*\s?120.*|120", e.dxf.text)]
    assert rots and all(abs(r - 60.0) < 1.0 for r in rots)          # the tag runs along its slanted wall
    # the bench aligns a reading that is turned and moved back onto the truth frame
    from wenart.datasets import bench as BE
    t2 = TR.synthetic_truth("swiss-angled", tmp_path / "swiss-angled" / "truth" / "reading_truth.json")
    moved = copy.deepcopy(t2)
    moved["per_level"]["L0"] = BE._shift_level(t2["per_level"]["L0"], 0.4, -0.3, 0.0)
    back, moves = BE.align(t2, moved)
    assert moves["L0"]["shift_m"] == pytest.approx([-0.4, 0.3], abs=0.01)
    assert SC.match(t2, back)["total"] == 100.0


@pytest.mark.parametrize("text,kind", [("K:90/210", "door_tag"), ("90/210", "door_tag"), ("P:150/150", "window_tag"),
                                       ("a:4.2m2", "area"), ("+3.00", "level"), ("ZEMİN KAT PLANI", "title"),
                                       ("YATAK ODASI", "room_label"), ("Ö:1/50", "scale")])
def test_profile_text_kinds(text, kind):
    assert TP.text_kind(text, None) == kind


# --- the bench's wall coverage and line-shift alignment (21 Nov 2026) ------------------------------------------------
def _w(a, b, t=0.2, wid=None):
    return {"id": wid, "start": list(a), "end": list(b), "thickness": t}


def test_wall_split_at_t_junctions_is_full_coverage_but_one_match():
    from wenart.datasets import bench as BE
    long_ = _w((0, 0), (10, 0), wid="t1")
    cross = _w((4, 0), (4, 5), 0.1, wid="t2")
    pieces = [_w((0, 0), (4, 0)), _w((4, 0), (7, 0)), _w((7, 0), (10, 0)), cross]
    truth = {"per_level": {"L0": {"walls": [long_, cross]}}}
    read = {"per_level": {"L0": {"walls": pieces}}}
    c = BE.wall_coverage(truth, read)
    assert c["truth_m"] == c["covered_m"] == 15.0 and c["read_m"] == c["on_truth_m"] == 15.0
    assert len(SC.match_walls([long_, cross], pieces)) == 2                     # one to one: two of four pieces
    thick = [_w((0, 0), (10, 0), 0.4)]
    assert BE.covered_length(long_, thick) == 0.0                               # another solid: not covered


def test_align_lays_wall_lines_on_the_truth_when_the_min_corners_differ():
    from wenart.datasets import bench as BE
    walls = [_w((0, 0), (10, 0)), _w((10, 0), (10, 8)), _w((10, 8), (0, 8)), _w((0, 8), (0, 0)),
             _w((4, 0), (4, 8), 0.1)]
    truth = {"per_level": {"L0": {"walls": walls + [_w((-1.5, 3), (0, 3), 0.1)]}}}       # a stub the reading misses
    moved = [_w((w["start"][0] + 0.6, w["start"][1] + 0.3), (w["end"][0] + 0.6, w["end"][1] + 0.3), w["thickness"])
             for w in walls]
    read = {"per_level": {"L0": {"walls": moved}}}
    out, moves = BE.align(truth, read)
    assert moves["L0"]["shift_m"] == [0.6, 0.3]
    assert len(SC.match_walls(truth["per_level"]["L0"]["walls"], out["per_level"]["L0"]["walls"])) == 5
