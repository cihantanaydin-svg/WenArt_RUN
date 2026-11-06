"""The raster second opinion RC13 (5 Nov 2026, Milestone 14 track R4; user, 4 Nov 2026: "some AI or something else to
give the feedbacks by itself instead of me").

What: a hand-made DXF region (two rooms, a door, a window) is rendered and its pixel -> building transform checked; the
raster reading of that render, mapped back, lies within 0.1 m of the drawn walls; the comparison of hand-made reading
pairs (a wall only on one side, an opening only on one side, a room only one side closes, a type difference), the
grouping, the judging against a truth, the trust (``apply_trust``) and the trust file's shape; one end-to-end run on
synthetic-04 (a DXF, fast) records its counts.

Why: the opinion gates nothing until it earns trust; what it computes must be exact where it can be (the transform,
the mapping), and its findings must come from real disagreements, not from fragments the other reader splits.

How: ezdxf writes the DXF; the raster reading is the pipeline's own (Tesseract, OpenCV), no AI, no pod.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from wenart.reading_check import raster_opinion as RO
from wenart.reading_check import truth as TR

ROOT = Path(__file__).resolve().parents[1]
TF_MM = [0.001, 0.0, 0.0, 0.0, 0.001, 0.0]          # drawing millimetres -> building metres
BOX = [-500.0, -500.0, 7500.0, 5500.0]              # the region (drawing units)
# The drawn walls' centre lines in building metres (0.2 m thick): the outer ring and the wall between the rooms.
WALLS_M = [((0.1, 0.1), (6.9, 0.1)), ((6.9, 0.1), (6.9, 3.9)), ((6.9, 3.9), (0.1, 3.9)), ((0.1, 3.9), (0.1, 0.1)),
           ((4.0, 0.2), (4.0, 3.8))]
DOOR_M = (4.0, 1.45)
WINDOW_M = (5.6, 0.1)


def _two_rooms(path: Path) -> Path:
    """Two rooms (3.7 x 3.6 m and 2.7 x 3.6 m inside), 0.2 m walls drawn as face lines, a 0.9 m door in the wall
    between them (leaf and swing), a 1.2 m window in the bottom wall of the right room, room labels, a title and the
    drawing's own scale note (which the render must leave out)."""
    import ezdxf

    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()
    for name in ("DUVAR", "KAPI", "PENCERE", "YAZI"):
        doc.layers.add(name)

    def line(a, b, layer="DUVAR"):
        msp.add_line(a, b, dxfattribs={"layer": layer})

    # outer faces (the bottom one broken by the window)
    line((0, 0), (5000, 0)); line((6200, 0), (7000, 0)); line((7000, 0), (7000, 4000))
    line((7000, 4000), (0, 4000)); line((0, 4000), (0, 0))
    # left room's inner faces (its right side broken by the door)
    line((200, 200), (3900, 200)); line((3900, 200), (3900, 1000)); line((3900, 1900), (3900, 3800))
    line((3900, 3800), (200, 3800)); line((200, 3800), (200, 200))
    # right room's inner faces (bottom broken by the window, left by the door)
    line((4100, 200), (5000, 200)); line((6200, 200), (6800, 200)); line((6800, 200), (6800, 3800))
    line((6800, 3800), (4100, 3800)); line((4100, 3800), (4100, 1900)); line((4100, 1000), (4100, 200))
    # door jambs, leaf and swing
    line((3900, 1000), (4100, 1000)); line((3900, 1900), (4100, 1900))
    line((4100, 1000), (5000, 1000), "KAPI")
    msp.add_arc((4100, 1000), 900, 0, 90, dxfattribs={"layer": "KAPI"})
    # window jambs and glass lines
    line((5000, 0), (5000, 200)); line((6200, 0), (6200, 200))
    line((5000, 80), (6200, 80), "PENCERE"); line((5000, 120), (6200, 120), "PENCERE")
    # the wall bodies filled (poché), as many plans draw them
    for x0, y0, x1, y1 in ((0, 0, 5000, 200), (6200, 0, 7000, 200), (0, 3800, 7000, 4000), (0, 200, 200, 3800),
                           (6800, 200, 7000, 3800), (3900, 200, 4100, 1000), (3900, 1900, 4100, 3800)):
        hatch = msp.add_hatch(color=7, dxfattribs={"layer": "DUVAR"})
        hatch.paths.add_polyline_path([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], is_closed=True)
    for text, at, h in (("SALON", (1300, 2000), 250), ("YATAK ODASI", (4500, 2800), 250),
                        ("ZEM\\U+0130N KAT PLANI", (500, 4500), 350), ("ÖLÇEK 1/50", (500, 5050), 200)):
        msp.add_text(text, height=h, dxfattribs={"layer": "YAZI", "insert": at})
    doc.saveas(path)
    return path


@pytest.fixture(scope="module")
def rendered(tmp_path_factory):
    import ezdxf

    d = tmp_path_factory.mktemp("raster_opinion")
    dxf = _two_rooms(d / "two_rooms.dxf")
    doc = ezdxf.readfile(str(dxf))
    ents = list(doc.modelspace())
    render = RO.render_level(doc, ents, BOX, TF_MM, d / "plan_L0.png")
    return d, render


@pytest.fixture(scope="module")
def raster_read(rendered):
    d, render = rendered
    rr = RO.read_raster(Path(render["png"]), d / "read")
    return rr, render


# ------------------------------------------------------------------------------------------------------------ render
def test_the_render_has_the_known_size_metadata_and_transform(rendered):
    from PIL import Image

    _d, r = rendered
    im = Image.open(r["png"])
    assert r["px_per_m"] == RO.PX_PER_M
    m = int(round(2 * RO.RENDER_MARGIN_M * RO.PX_PER_M))                  # white paper around the region's box
    assert im.size == (800 + m, 600 + m + RO.NOTE_BAND_PX) == tuple(r["size"])
    assert im.mode == "L"
    assert abs(im.info["dpi"][0] - 0.0254 * RO.PX_PER_M * RO.NOTE_RATIO) < 0.01           # pHYs: 254 dpi
    assert r["note"] == f"SCALE 1/{RO.NOTE_RATIO}"
    assert any("1/50" in t for t in r["scale_notes_hidden"])                              # the drawing's own note
    assert r["texts_decoded"] == 1                                                        # ZEM\\U+0130N -> ZEMİN
    # the transform: pixel centre (u, v) -> building metres, 0.01 m a pixel, y down
    tf = r["pixel_to_building"]
    assert tf[0] == pytest.approx(0.01) and tf[4] == pytest.approx(-0.01) and tf[1] == tf[3] == 0.0
    x0, y0 = RO._apply(tf, (0.0, RO.NOTE_BAND_PX))          # the first drawing pixel's centre
    edge = RO.RENDER_MARGIN_M
    assert x0 == pytest.approx(-0.5 - edge + 0.005) and y0 == pytest.approx(5.5 + edge - 0.005)


def test_the_drawn_lines_fall_where_the_transform_says(rendered):
    """Every drawn wall face is found in the image within one pixel of where ``pixel_to_building`` puts it
    (matplotlib snaps a line to whole pixels: at 100 px/m that is 1 cm)."""
    from PIL import Image

    _d, r = rendered
    a = np.asarray(Image.open(r["png"]))
    inv = RO._invert(r["pixel_to_building"])
    for x_m in (0.0, 0.2, 3.9, 4.1, 6.8, 7.0):                    # vertical faces, read along the row at y = 3.0 m
        u_pred, v = RO._apply(inv, (x_m, 3.0))
        row = a[int(round(v))]
        dark = [u for u in range(int(u_pred) - 4, int(u_pred) + 5) if row[u] < 128]
        assert dark and min(abs(u - u_pred) for u in dark) <= 1.0, (x_m, u_pred, dark)
    for y_m in (4.0, 3.8):                                         # horizontal faces, along the column at x = 2 m
        u, v_pred = RO._apply(inv, (2.0, y_m))
        col = a[:, int(round(u))]
        dark = [v for v in range(int(v_pred) - 4, int(v_pred) + 5) if col[v] < 128]
        assert dark and min(abs(v - v_pred) for v in dark) <= 1.0, (y_m, v_pred, dark)
    assert (a[:RO.NOTE_BAND_PX, 300:] > 250).all()                 # the band holds the note only (at its left)


def test_pixel_transform_composes_the_page_transform():
    tf = [0.0254, 0.0, -12.0, 0.0, 0.0254, -6.0]                    # inches, shifted (synthetic-06's kind)
    p2b = RO.pixel_transform([100.0, 50.0, 400.0, 300.0], 0.5, 10, tf)
    # pixel (0, 10) is the top-left drawing pixel: its centre is 0.25 units in from (100, 300)
    x, y = RO._apply(p2b, (0.0, 10.0))
    assert x == pytest.approx(0.0254 * 100.25 - 12.0) and y == pytest.approx(0.0254 * 299.75 - 6.0)
    assert RO._apply(RO._invert(p2b), (x, y)) == pytest.approx((0.0, 10.0))


# ------------------------------------------------------------------------------------------------------- raster read
def _offset_to_drawn(w) -> float:
    """The lateral offset of a wall's centre line from the drawn centre line it runs along (inf when none)."""
    best = math.inf
    for a, b in WALLS_M:
        if RO._angle_deg(w["start"], w["end"], a, b) > RO.WALL_ANGLE_DEG:
            continue
        ln = RO._seg_len(a, b)
        ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
        ts = [(p[0] - a[0]) * ux + (p[1] - a[1]) * uy for p in (w["start"], w["end"])]
        if max(ts) < 0 or min(ts) > ln:
            continue
        best = min(best, max(abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) for p in (w["start"], w["end"])))
    return best


def test_the_raster_reading_maps_back_within_a_decimetre(raster_read):
    rr, render = raster_read
    assert rr["page"] is not None, rr["reasons"]
    assert rr["scale_used"]["method"] == "pdf_scale_text"                # the printed note at the verified pixel size
    # (the reader may read the page resampled to its working resolution: the scale is per PNG pixel then)
    assert RO.scale_off_pct(rr, render) == pytest.approx(0.0, abs=1e-3)
    f = RO.raster_to_level(rr["page"], render["pixel_to_building"])
    assert RO._length_factor(f) == pytest.approx(1.0, abs=1e-3)      # a resampled page: whole-pixel rounding
    b = RO.map_building(rr["building"], f, "L0")
    walls = b["walls"]
    assert len(walls) >= 4
    # (the reader's stubs under 0.3 m, a corner nub, are no wall to place)
    offsets = [_offset_to_drawn(w) for w in walls if RO._seg_len(w["start"], w["end"]) >= 0.3]
    assert len(offsets) >= 4 and max(offsets) <= 0.1, offsets
    for w in walls:
        assert abs(float(w["thickness"]) - 0.2) <= 0.1
    outer = [{"start": a, "end": b, "thickness": 0.2} for a, b in WALLS_M[:4]]
    assert sum(RO.wall_cover_share(w, walls) >= 0.8 for w in outer) == 4
    rooms = [r for r in b["rooms"] if len(r["polygon"]) >= 3]
    assert len(rooms) == 2
    assert sorted(round(r["area_computed"], 1) for r in rooms) == pytest.approx([9.7, 13.3], abs=0.3)
    doors = [o for o in b["openings"] if o["type"] == "door"]
    assert any(math.dist(o["center"], DOOR_M) <= 0.1 for o in doors), [o["center"] for o in doors]


# ------------------------------------------------------------------------------------------------------- comparison
def _wall(i, a, b, t=0.2):
    return {"id": i, "start": list(a), "end": list(b), "thickness": t}


def _room(i, poly, label=None):
    return {"id": i, "label": label, "polygon": [list(p) for p in poly], "centroid": TR.centroid(poly)}


def _op(i, c, w=0.9, **kw):
    return dict({"id": i, "center": list(c), "width": w}, **kw)


def _level(walls=(), rooms=(), doors=(), windows=(), openings=()):
    return {"walls": list(walls), "rooms": list(rooms), "doors": list(doors), "windows": list(windows),
            "openings": list(openings), "stairs": []}


def test_a_wall_only_on_one_side_is_a_finding_and_fragments_are_not():
    a, b = ((0, 0), (6, 0)), ((6, 0), (6, 4))
    vec = _level(walls=[_wall("w1", *a), _wall("w2", *b)])
    # the raster reads w1 in two pieces (a fragment the matcher leaves is covered: no finding) and lacks w2
    ras = _level(walls=[_wall("r1", (0, 0.02), (2.9, 0.02)), _wall("r2", (3.1, 0.0), (6, 0.0)),
                        _wall("r3", (0, 3), (3, 3))])
    raw = RO.raw_differences(vec, ras)
    kinds = sorted(r["kind"] for r in raw)
    assert kinds == ["wall_raster_only", "wall_vector_only"]
    v = next(r for r in raw if r["kind"] == "wall_vector_only")
    assert v["ids"] == ["w2"] and v["size"] == pytest.approx(4.0)
    r = next(r for r in raw if r["kind"] == "wall_raster_only")
    assert r["ids"] == ["raster:r3"] and r["what"]["vector"] == "no wall"
    # a wall both have with another thickness is no finding (geometry decides, as for the truth)
    assert RO.raw_differences(_level(walls=[_wall("w", (0, 0), (5, 0), 0.30)]),
                              _level(walls=[_wall("r", (0, 0.04), (5, 0.04), 0.20)])) == []


def test_only_the_uncovered_piece_of_a_wall_is_reported():
    vec = _level(walls=[_wall("w1", (0, 0), (10, 0))])
    ras = _level(walls=[_wall("r1", (0, 0), (6, 0))])
    raw = RO.raw_differences(vec, ras)
    assert len(raw) == 1 and raw[0]["kind"] == "wall_vector_only"
    assert raw[0]["geom"][1] == [6.0, 0.0] and raw[0]["geom"][2] == [10.0, 0.0]
    # a piece shorter than WALL_PIECE_MIN_M (a junction difference) is none
    short = RO.raw_differences(_level(walls=[_wall("w", (0, 0), (6.3, 0))]), _level(walls=[_wall("r", (0, 0), (6, 0))]))
    assert short == []


def test_openings_by_centre_and_class():
    vec = _level(doors=[_op("d1", (1, 0)), _op("d2", (5, 0))], windows=[_op("win1", (3, 4), 1.2)],
                 openings=[_op("o1", (8, 8), virtual=True)])
    ras = _level(doors=[_op("rd1", (1.1, 0.05))], windows=[_op("rw1", (5.05, 0), 1.0), _op("rw2", (9, 1), 1.2)])
    raw = RO.raw_differences(vec, ras)
    by = {r["kind"]: r for r in raw}
    assert sorted(by) == ["opening_raster_only", "opening_type_differs", "opening_vector_only"]
    assert by["opening_type_differs"]["ids"] == ["d2", "raster:rw1"]
    assert by["opening_type_differs"]["raster_class"] == "window"
    assert by["opening_raster_only"]["ids"] == ["raster:rw2"]
    assert by["opening_vector_only"]["ids"] == ["win1"]                      # the virtual separator is not compared


def test_a_room_only_one_side_closes_and_a_split_room_is_none():
    big = [(0, 0), (6, 0), (6, 4), (0, 4)]
    vec = _level(rooms=[_room("r_a", big, "SALON"), _room("r_b", [(10, 0), (13, 0), (13, 3), (10, 3)], "BANYO")])
    # the raster splits SALON in two (covered: no finding), lacks BANYO, closes a room the vector has not
    ras = _level(rooms=[_room("x1", [(0, 0), (3, 0), (3, 4), (0, 4)]), _room("x2", [(3, 0), (6, 0), (6, 4), (3, 4)]),
                        _room("x3", [(20, 0), (24, 0), (24, 4), (20, 4)], "ODA")])
    raw = RO.raw_differences(vec, ras)
    by = {r["kind"]: r for r in raw}
    assert sorted(by) == ["room_raster_only", "room_vector_only"]
    assert by["room_vector_only"]["ids"] == ["r_b"] and by["room_vector_only"]["size"] == pytest.approx(9.0)
    assert by["room_raster_only"]["ids"] == ["raster:x3"] and by["room_raster_only"]["cover"] == 0.0


# --------------------------------------------------------------------------------------------------------- grouping
def _raw_seg(a, b, kind="wall_raster_only"):
    return {"kind": kind, "geom": ("seg", list(a), list(b)), "size": RO._seg_len(a, b), "ids": [f"raster:{a}"],
            "what": {"vector": "no wall", "raster": "wall"}}


def _raw_pt(p, kind="opening_raster_only"):
    return {"kind": kind, "geom": ("pt", list(p)), "size": 1.0, "ids": [f"raster:{p}"], "raster_class": "door",
            "what": {"vector": "no opening", "raster": "door"}}


def test_grouping_joins_one_place_and_keeps_walls_at_a_corner_apart():
    pieces = [_raw_seg((0, 0), (2, 0)), _raw_seg((2.3, 0.05), (4, 0.05)),       # one line, 0.3 m apart: one finding
              _raw_seg((4.2, 0.2), (4.2, 3)),                                    # a corner: its own finding
              _raw_seg((10, 0), (12, 0))]                                        # far away: its own
    groups = RO.group(pieces)
    assert sorted(len(g) for g in groups) == [1, 1, 2]
    assert len(RO.group([_raw_pt((0, 0)), _raw_pt((0.4, 0))])) == 1
    assert len(RO.group([_raw_pt((0, 0)), _raw_pt((0.8, 0))])) == 2
    assert len(RO.group([_raw_pt((0, 0)), _raw_pt((0.1, 0), "opening_vector_only")])) == 2   # kinds stay apart
    found = RO.findings_of("L0", pieces)
    assert len(found) == 3
    joined = next(f for f in found if f["members"] == 2)
    assert joined["size"] == pytest.approx(2.0 + 1.7) and joined["severity_by_size"] == "major"
    assert joined["check"] == "RC13" and joined["advisory"] is True and joined["sources"] == ["vector", "raster"]
    assert joined["place"] == {"x": 1.0, "y": 0.0}                              # the middle of its longest piece
    assert len(joined["element_ids"]) == 2 and len(joined["pieces"]) == 2


# ------------------------------------------------------------------------------------------------------------ trust
def test_judging_against_the_truth():
    truth = _level(walls=[_wall("t1", (0, 0), (5, 0))], rooms=[_room("tr", [(0, 0), (4, 0), (4, 4), (0, 4)])],
                   doors=[_op("td", (2, 0))])
    f = RO.findings_of("L0", [_raw_seg((0, 0.05), (5, 0.05))])[0]
    assert RO.judge(f, truth) is True                                        # the truth has the wall the raster saw
    f = RO.findings_of("L0", [_raw_seg((0, 2), (5, 2), "wall_vector_only")])[0]
    assert RO.judge(f, truth) is True                                        # ... and not the one only the vector has
    f = RO.findings_of("L0", [_raw_seg((0, 0), (5, 0), "wall_vector_only")])[0]
    assert RO.judge(f, truth) is False
    f = RO.findings_of("L0", [_raw_pt((2.1, 0))])[0]
    assert RO.judge(f, truth) is True
    f = RO.findings_of("L0", [_raw_pt((2.1, 0), "opening_vector_only") | {"vector_class": "door"}])[0]
    assert RO.judge(f, truth) is False
    room = {"kind": "room_raster_only", "geom": ("poly", [[0, 0], [4, 0], [4, 4], [0, 4]]), "size": 16.0,
            "ids": ["raster:x"], "what": {"vector": "no room", "raster": "room"}}
    assert RO.judge(RO.findings_of("L0", [room])[0], truth) is True


def test_apply_trust_lowers_the_kinds_below_the_threshold():
    trust = {"threshold": 0.5, "kinds": {"wall_raster_only": {"findings": 20, "right": 16, "precision": 0.8},
                                         "wall_vector_only": {"findings": 30, "right": 3, "precision": 0.1}}}
    found = RO.findings_of("L0", [_raw_seg((0, 0), (5, 0)), _raw_seg((0, 3), (5, 3), "wall_vector_only"),
                                  _raw_pt((9, 9))])
    RO.apply_trust(found, trust)
    by = {f["kind"]: f for f in found}
    assert by["wall_raster_only"]["severity"] == "major" and by["wall_raster_only"]["trust"]["precision"] == 0.8
    assert by["wall_vector_only"]["severity"] == "info" and "0.10" in by["wall_vector_only"]["message"]
    assert by["wall_vector_only"]["severity_by_size"] == "major"
    assert by["opening_raster_only"]["severity"] == "info" and "not calibrated" in by["opening_raster_only"]["message"]
    # a new trust file applies afresh (``retrust``): the severity by size comes back, the old note goes
    trust["kinds"]["wall_vector_only"] = {"findings": 30, "right": 27, "precision": 0.9}
    RO.apply_trust(found, trust)
    assert by["wall_vector_only"]["severity"] == "major"
    assert "info only" not in by["wall_vector_only"]["message"] and "0.90" in by["wall_vector_only"]["message"]
    assert by["wall_vector_only"]["message"].count("[") == 1


def test_the_trust_file_shape():
    per = {"p1": {"raster_score": 50.0, "vector_score": 90.0, "findings": dict.fromkeys(RO.KINDS, 2),
                  "right": dict.fromkeys(RO.KINDS, 1), "unjudged": dict.fromkeys(RO.KINDS, 0), "seconds": 3.0}}
    t = RO.trust_from(per, "abc")
    assert set(t) >= {"note", "commit", "date", "threshold", "projects", "kinds", "per_project"}
    assert t["projects"] == ["p1"] and t["commit"] == "abc" and t["threshold"] == RO.TRUST_MIN
    assert set(t["kinds"]) == set(RO.KINDS)
    assert t["kinds"]["wall_raster_only"] == {"findings": 2, "right": 1, "precision": 0.5, "trusted": True}
    stored = RO.load_trust()
    if stored is not None:                                    # the committed file has the same shape
        assert set(stored["kinds"]) == set(RO.KINDS) and stored["threshold"] == RO.TRUST_MIN
        assert stored["projects"] and stored["commit"]
        for k, v in stored["kinds"].items():
            assert set(v) == {"findings", "right", "precision", "trusted"}
            assert (v["precision"] is None) == (v["findings"] == 0)


# --------------------------------------------------------------------------------------------------- end to end
@pytest.mark.slow
def test_synthetic_04_end_to_end(tmp_path):
    folder = TR.reading("synthetic-04", tmp_path / "work")
    res = RO.opinion(folder, work=tmp_path / "raster", trust={})
    assert [rec["level"] for rec in res["levels"]] == ["L3"]
    rec = res["levels"][0]
    assert rec["raster"]["read"] is True, rec["raster"]
    assert set(rec["raster"]["counts"]) == set(TR.ELEMENT_TYPES) and rec["raster"]["counts"]["walls"] > 0
    assert set(res["counts_by_kind"]) == set(RO.KINDS)
    assert sum(res["counts"].values()) == len(res["findings"])
    assert all(f["check"] == "RC13" and f["advisory"] for f in res["findings"])
    saved = json.loads((folder / "reading_check" / "raster_opinion.json").read_text(encoding="utf-8"))
    assert saved["counts"] == res["counts"] and "vector" not in saved["levels"][0]
    assert (folder / "reading_check" / "raster_L3.jpg").is_file()
    assert not (tmp_path / "raster" / "L3").exists()                        # the render and the reading are removed
    truth = TR.load_truth("synthetic-04")
    cal = RO.calibrate_project("synthetic-04", res, truth)
    assert cal["raster_score"] is not None and set(cal["findings"]) == set(RO.KINDS)
