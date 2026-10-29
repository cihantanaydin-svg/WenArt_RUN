"""The roof as the roof plan draws it (27 Oct 2026; user, on real06's renders: "In the plan roof is covering this
balcony also and there is a small roof on top of the rest of the veranda", "The project needs to find these kind of
things by itself without my input", "Make argus catch these kind of things before me").

Every rule is checked on a synthetic roof plan first (a house with a roof wing over a first-floor balcony, a gutter, a
drawn wall line, a tile hatch, a dimension chain and a lower roof beside it), then on real06's roof plan
(``tests/fixtures/real06_roof_plan_20261027.json``: only the coordinates the rules need):

- the reading (``wenart.sheets.exterior.roof_plan_outline``): the eaves loop the hip and valley lines end on, the drawn
  wall line inside it (the overhang), the other roofs beside it; hatch and dimension layers never count;
- the building (``wenart.sheets.to_building.roof_outline_record`` / ``roof_block``): the loop put on the top level's
  walls, used as the outline when it fits, covers the walls and reaches only over a drawn outdoor space;
- the build (``wenart.blender.roof``): a hip roof over a stepped outline, every eaves edge level, valleys at the inner
  corners, walls cut by the part over them;
- the spaces (``wenart.levels.outdoor``): a space under the drawn roof is covered, gets no light roof of its own;
- Argus (``wenart.blender.model_review`` M11, ``wenart.audit.plan_vs_model.roof_outline_findings``): an assumed
  outline while a roof plan draws it, a drawn-covered space left open, a footprint far from the drawn one.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart import geometry as G
from wenart.blender import model_review as MR
from wenart.blender import roof as R
from wenart.ingest.generic.model import Stroke
from wenart.audit import plan_vs_model as PV
from wenart.levels import outdoor as OD
from wenart.sheets import exterior as EX
from wenart.sheets import to_building as TB
from wenart.sheets.model import Ent, Region, Txt

FIXTURE = Path(__file__).parent / "fixtures" / "real06_roof_plan_20261027.json"
SHIFT = (10.0, 20.0)                  # the synthetic building frame: the roof plan's metres + this


# --------------------------------------------------------------------------
# A synthetic roof plan (its own metres, 1 unit = 1 m)
# --------------------------------------------------------------------------

EAVES = [(-0.5, -0.5), (1.5, -0.5), (1.5, -2.5), (5.5, -2.5), (5.5, -0.5), (8.5, -0.5), (8.5, 12.5), (-0.5, 12.5)]
WALL_LINE = [(0.0, 0.0), (2.0, 0.0), (2.0, -2.0), (5.0, -2.0), (5.0, 0.0), (8.0, 0.0), (8.0, 12.0), (0.0, 12.0)]
GUTTER = [(-0.7, -0.7), (1.3, -0.7), (1.3, -2.7), (5.7, -2.7), (5.7, -0.7), (8.7, -0.7), (8.7, 12.7), (-0.7, 12.7)]


def _ent(eid: str, a, b, layer: str) -> Ent:
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _loop(prefix: str, pts, layer: str) -> list[Ent]:
    return [_ent(f"LINE:{prefix}{k}", pts[k], pts[(k + 1) % len(pts)], layer) for k in range(len(pts))]


def _region(ents: list[Ent], texts: list[Txt], box=None) -> Region:
    xs = [p[0] for e in ents for st in e.strokes for p in st.pts]
    ys = [p[1] for e in ents for st in e.strokes for p in st.pts]
    box = box or (min(xs), min(ys), max(xs), max(ys))
    r = Region(id="rp", file="t.dxf", sheet=SimpleNamespace(page=1), box=box, geometry_box=box, ents=ents, texts=texts)
    r.metres_per_unit = 1.0
    r.cls = "roof_plan"
    return r


def synthetic_plan(lower_roof: bool = True) -> Region:
    """The roof plan of an 8 x 12 m house whose hip roof reaches 2 m out over a 3 m wide first-floor balcony (its own
    hip end, valleys where it meets the main roof), drawn with its gutter 0.2 m outside the eaves, the wall line 0.5 m
    inside, hips from every corner, a ridge, a tile hatch, a dimension chain and (``lower_roof``) a lower roof west of
    the wing whose north and east sides are the main roof's gutter."""
    ents = _loop("E", EAVES, "ROOF") + _loop("W", WALL_LINE, "ROOF") + _loop("G", GUTTER, "ROOF")
    # hips from the convex corners, valleys from the inner ones (45 degrees, 1.5 m on the plan)
    k = 0
    for (x, y), (dx, dy) in (((-0.5, -0.5), (1, 1)), ((1.5, -2.5), (1, 1)), ((5.5, -2.5), (-1, 1)),
                             ((8.5, -0.5), (-1, 1)), ((8.5, 12.5), (-1, -1)), ((-0.5, 12.5), (1, -1)),
                             ((1.5, -0.5), (1, 1)), ((5.5, -0.5), (-1, 1))):
        k += 1
        ents.append(_ent(f"LINE:H{k}", (x, y), (x + 1.5 * dx, y + 1.5 * dy), "ROOF"))
    ents.append(_ent("LINE:R1", (4.0, 4.0), (4.0, 8.0), "ROOF"))                        # the ridge
    for i in range(60):                                                                 # the tile hatch
        x = 0.3 + (i % 10) * 0.7
        y = 1.0 + (i // 10) * 1.5
        ents.append(_ent(f"LINE:T{i}", (x, y), (x + 0.15, y + 0.15), "HATCH-TILES"))
    for x in (-0.5, 1.5, 5.5, 8.5):                                                     # a dimension chain
        ents.append(_ent(f"LINE:D{x}", (x, -4.2), (x, -3.0), "DIMS"))
    ents.append(_ent("LINE:DL", (-0.5, -4.0), (8.5, -4.0), "DIMS"))
    ents.append(_ent("LINE:DM", (-0.5, -3.6), (8.5, -3.6), "DIMS"))
    texts = [Txt(id=f"TEXT:{k}", text=v, box=(k, -3.9, k + 0.5, -3.7), height=0.2, layer="DIMS")
             for k, v in enumerate(("200", "400", "300"))]
    texts.append(Txt(id="TEXT:S", text="SLOPE 30%", box=(3, 3, 4, 3.2), height=0.2, layer="TEXT"))
    if lower_roof:
        ents += [_ent("LINE:L1", (-1.0, -0.7), (-1.0, -2.3), "CANOPY"),
                 _ent("LINE:L2", (-1.0, -2.3), (1.3, -2.3), "CANOPY"),
                 _ent("LINE:L3", (-1.0, -0.7), (-0.7, -0.7), "CANOPY")]
    return _region(ents, texts)


def _walls(x0: float, y0: float, w: float, d: float, level: str = "L1", t: float = 0.2) -> list[dict]:
    """Four walls whose outer faces run x0..x0+w, y0..y0+d (centre lines half a thickness in)."""
    h = t / 2.0
    pts = [(x0 + h, y0 + h), (x0 + w - h, y0 + h), (x0 + w - h, y0 + d - h), (x0 + h, y0 + d - h)]
    return [{"id": f"w_{level}_{k}", "level_id": level, "start": list(pts[k]), "end": list(pts[(k + 1) % 4]),
             "thickness": t, "exterior": True} for k in range(4)]


LEVELS = [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.8},
          {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.8}]
BALCONY_AREA = {"id": "sa_bal", "level_id": "L1", "label": "BALKON", "anchor": [13.5, 19.0]}


# --------------------------------------------------------------------------
# Reading
# --------------------------------------------------------------------------

def test_the_eaves_loop_the_hips_end_on_is_the_roof_outline():
    rec, why = EX.roof_plan_outline(synthetic_plan())
    assert why == "" and rec is not None
    x0, y0 = -1.0, -4.2                                     # the region's geometry box corner: the record's origin
    got = [(round(x + x0, 3), round(y + y0, 3)) for x, y in rec["points"]]
    assert sorted(got) == sorted(EAVES)                     # the eaves loop, not the gutter or the wall line
    assert rec["hip_lines"] == 8 and rec["layers"] == ["ROOF"]
    assert rec["overhang_m"] == pytest.approx(0.5)          # the drawn wall line 0.5 m inside
    assert sorted((round(x + x0, 3), round(y + y0, 3)) for x, y in rec["wall_line"]) == sorted(WALL_LINE)
    # the lower roof beside it (closed by the main roof's gutter); the hatch and the dimension chain are no roofs
    assert len(rec["others"]) == 1
    other = rec["others"][0]
    assert other["touches_main"] and other["area_m2"] == pytest.approx(2.3 * 1.6, abs=0.01)
    assert "CANOPY" in other["layers"]
    assert not any("DIMS" in o["layers"] or "HATCH-TILES" in o["layers"] for o in rec["others"])


def test_any_number_of_separate_roofs_is_read():
    """A carport roof drawn apart from the house (its own hips) and a canopy beside the main roof: two other roofs."""
    ents = list(synthetic_plan().ents)
    carport = [(12.0, 0.0), (16.0, 0.0), (16.0, 6.0), (12.0, 6.0)]
    ents += _loop("C", carport, "ROOF")
    ents += [_ent("LINE:CH1", (12.0, 0.0), (13.5, 1.5), "ROOF"), _ent("LINE:CH2", (16.0, 6.0), (14.5, 4.5), "ROOF")]
    # no roofs: the plot line around everything and a box drawn apart without hips (a legend, a north arrow's frame)
    ents += _loop("P", [(-6.0, -9.0), (20.0, -9.0), (20.0, 18.0), (-6.0, 18.0)], "SITE")
    ents += _loop("B", [(17.0, 10.0), (19.5, 10.0), (19.5, 12.0), (17.0, 12.0)], "SITE")
    rec, _ = EX.roof_plan_outline(_region(ents, synthetic_plan().texts))
    assert len(rec["points"]) == 8                           # the house's hip roof stays the main one (most hips)
    areas = sorted(o["area_m2"] for o in rec["others"])
    assert areas == pytest.approx([3.68, 24.0], abs=0.01)
    carport_rec = next(o for o in rec["others"] if o["area_m2"] > 20)
    assert not carport_rec["touches_main"] and carport_rec["hip_lines"] == 2


def test_a_stepped_outline_at_other_angles_keeps_the_enclosing_rectangle():
    outline = [[0.0, 0.0], [9.0, 0.0], [9.0, 12.0], [4.0, 14.0], [0.0, 12.0]]          # a gable-like pentagon
    assert R.hip_parts(outline, (1.0, 0.0), 6.0, 0.5) is None
    roof = {"type": "hip", "type_source": "roof_plan", "over_level_id": "L1", "outline": outline,
            "eaves_height": {"value": 6.0, "method": "vector", "confidence": 1.0},
            "pitches_deg": [{"value": 30.0, "method": "vector", "confidence": 1.0}], "planes": [], "openings": [],
            "assumed": [], "evidence": [{"rule": "roof_plan_outline"}]}
    model = R.roof_model(roof, _building(roof, walls=_walls(0.5, 0.5, 8.0, 11.0)))
    assert not model.get("parts") and any(a["field"] == "outline_rectangle" for a in model["assumed"])


def test_a_thin_l_keeps_its_own_axes():
    """The smallest rectangle around a thin L lies along its hull's diagonal; the L's edges give the axes."""
    ell = [[0.0, 0.0], [10.0, 0.0], [10.0, 2.0], [2.0, 2.0], [2.0, 10.0], [0.0, 10.0]]
    roof = {"type": "hip", "type_source": "roof_plan", "over_level_id": "L1", "outline": ell,
            "eaves_height": {"value": 6.0, "method": "vector", "confidence": 1.0},
            "pitches_deg": [{"value": 45.0, "method": "vector", "confidence": 1.0}], "planes": [], "openings": [],
            "assumed": [], "evidence": [{"rule": "roof_plan_outline"}]}
    model = R.roof_model(roof, _building(roof, walls=_walls(0.5, 0.5, 1.0, 9.0)))
    assert model.get("parts") and model["ridge_z"] == pytest.approx(7.0, abs=1e-6)       # 1 m in from the eaves
    assert R.top_z(model, 1.0, 1.0) == pytest.approx(7.0, abs=1e-6)                       # the corner of the L


def test_maximal_rectangles_of_a_cross():
    cross = [[3, 0], [6, 0], [6, 3], [9, 3], [9, 6], [6, 6], [6, 9], [3, 9], [3, 6], [0, 6], [0, 3], [3, 3]]
    rects = R.maximal_rectangles(cross, (1.0, 0.0))
    assert sorted(rects) == [(0.0, 9.0, 3.0, 6.0), (3.0, 6.0, 0.0, 9.0)]
    parts = R.hip_parts(cross, (1.0, 0.0), 3.0, 1.0)
    pl, pieces = R.part_pieces(parts)
    assert sum(G.polygon_area(p) for _g, p in pieces) == pytest.approx(G.polygon_area(cross))
    assert R.parts_z(parts, 4.5, 4.5) == pytest.approx(4.5)          # the crossing: 1.5 m in from every eaves line
    assert R.parts_z(parts, 1.0, 4.5) == pytest.approx(4.0)          # an arm's hip end


def test_no_hips_no_outline_and_the_reason():
    r = _region(_loop("E", EAVES, "ROOF"), [])
    rec, why = EX.roof_plan_outline(r)
    assert rec is None and "hip or valley" in why


# --------------------------------------------------------------------------
# On the building
# --------------------------------------------------------------------------

def _plan_record(lower_roof: bool = True) -> dict:
    rec, _ = EX.roof_plan_outline(synthetic_plan(lower_roof))
    return rec


def _house_walls() -> list[dict]:
    # the roof plan's wall line + (10, 20) after the region's origin (-1.0, -4.2): outer faces x 11..19, y 24.2..36.2
    return _walls(11.0, 24.2, 8.0, 12.0)


def _balcony_area() -> dict:
    return dict(BALCONY_AREA, anchor=[14.5, 23.2])          # inside the wing, under the drawn roof


def test_the_roof_plan_outline_is_put_on_the_walls_and_reaches_over_the_drawn_balcony():
    rec = TB.roof_outline_record(_plan_record(), _house_walls(), "L1", {"areas": [_balcony_area()]}, [], 0.5, LEVELS)
    assert rec["used"], rec["reason"]
    assert rec["fit"]["rotation_deg"] == 0.0 and rec["fit"]["rms_m"] < 0.01
    xs, ys = [p[0] for p in rec["points"]], [p[1] for p in rec["points"]]
    assert (min(xs), max(xs), min(ys), max(ys)) == pytest.approx((10.5, 19.5, 21.7, 36.7), abs=0.01)
    assert rec["reaches"] and rec["reaches"][0]["spaces"] == ["sa_bal"]
    assert len(rec["others"]) == 1 and rec["others"][0]["touches_main"]


def test_a_reach_over_nothing_drawn_falls_back_with_the_reason():
    rec = TB.roof_outline_record(_plan_record(), _house_walls(), "L1", {"areas": []}, [], 0.5, LEVELS)
    assert not rec["used"] and "no balcony, terrace, veranda or porch is drawn" in rec["reason"]
    assert rec["points"] is not None                        # placed, so Argus can still compare it


def test_a_roof_plan_of_another_building_does_not_fit():
    rec = TB.roof_outline_record(_plan_record(), _walls(0.0, 0.0, 6.0, 6.0), "L1", {"areas": [_balcony_area()]}, [],
                                 0.5, LEVELS)
    assert not rec["used"] and rec["points"] is None
    assert "does not fit" in rec["reason"] or "uncovered" in rec["reason"]


def _sheets(plan: dict) -> dict:
    v = {"method": "vector", "confidence": 1.0, "evidence": []}
    return {"heights": {"roof": {"eaves_z": dict(v, value=6.0), "overhang": dict(v, value=0.5)}},
            "exterior": {"roof": {"type": "hip", "type_source": "roof_plan", "outline": None, "break_line": None,
                                  "ridge_lines": [], "covering": None,
                                  "pitches_deg": [dict(v, value=30.0)], "evidence": [], "plan_outline": plan}}}


def test_roof_block_uses_the_roof_plan_outline_and_drops_the_assumed_note():
    roof = TB.roof_block(_sheets(_plan_record()), LEVELS, [], _house_walls(), (0.0, 0.0), {"areas": [_balcony_area()]})
    assert roof["outline_source"] == "roof_plan" and len(roof["outline"]) == 8
    assert not any(a.startswith("outline") for a in roof["assumed"])
    assert any(e.get("rule") == "roof_plan_outline" for e in roof["evidence"])
    assert R._drawn_outline(roof) == "drawn roof outline"          # an agent override keeps the drawn outline
    roof2 = TB.roof_block(_sheets(_plan_record()), LEVELS, [], _house_walls(), (0.0, 0.0), {"areas": []})
    assert roof2["outline"] is None
    note = next(a for a in roof2["assumed"] if a.startswith("outline (the outer walls + overhang)"))
    assert "no balcony" in note


# --------------------------------------------------------------------------
# The build: a hip roof over a stepped outline
# --------------------------------------------------------------------------

def _building(roof: dict, spaces=(), walls=None) -> dict:
    return {"levels": [dict(lv) for lv in LEVELS], "walls": walls if walls is not None else _house_walls(),
            "rooms": [], "openings": [], "slabs": [], "roof": roof,
            "site": {"areas": [_balcony_area()], "outdoor_spaces": [dict(s) for s in spaces]}}


def _roof(lower_roof: bool = True) -> dict:
    return TB.roof_block(_sheets(_plan_record(lower_roof)), LEVELS, [], _house_walls(), (0.0, 0.0),
                         {"areas": [_balcony_area()]})


def test_a_hip_roof_over_a_stepped_outline_keeps_every_eaves_edge_level():
    roof = _roof()
    model = R.roof_model(roof, _building(roof))
    assert model["parts"] and not model["convex"]
    out = model["outline"]
    for i in range(len(out)):                                # every eaves edge at the eaves height
        a, b = out[i], out[(i + 1) % len(out)]
        m = G.segment_midpoint(a, b)
        nx, ny = G.unit_normal_left(a, b)
        assert R.top_z(model, m[0] + nx * 1e-4, m[1] + ny * 1e-4) == pytest.approx(6.0, abs=1e-3)
    t = math.tan(math.radians(30.0))
    assert model["ridge_z"] == pytest.approx(6.0 + 4.5 * t, abs=1e-3)       # over the 9 m wide main roof
    assert R.top_z(model, 14.5, 23.9) == pytest.approx(6.0 + 2.0 * t, abs=1e-3)   # the wing's ridge
    # the covering covers the outline once; the solid's fascia runs along every outline edge
    verts, faces, slots = R.roof_solid(model)
    cover = sum(G.polygon_area([verts[i][:2] for i in f]) for f, s in zip(faces, slots) if s == R.SLOT_COVERING)
    assert cover == pytest.approx(G.polygon_area(out), rel=1e-6)
    assert slots.count(R.SLOT_FASCIA) == len(out)
    # ridges and hips get tiles, the two valleys where the wing meets the main roof do not
    lines = R.ridge_lines(model)
    assert not any(R._valley(model["parts"], a[:2], b[:2]) for a, b in lines)
    valleys = [(a, b) for g, lp in model["faces"] for a, b in zip(lp, lp[1:] + lp[:1])
               if R._valley(model["parts"], a, b)]
    assert valleys and all(abs(abs(b[0] - a[0]) - abs(b[1] - a[1])) < 1e-6 for a, b in valleys)   # at 45 degrees


def test_the_walls_under_a_stepped_roof_are_cut_by_the_part_over_them():
    roof = _roof()
    b = _building(roof)
    model = R.roof_model(roof, b)
    cut = R.wall_cut(model, b["walls"])
    assert set(cut["wall_planes"]) == {w["id"] for w in b["walls"]}
    for w in b["walls"]:                     # along every wall: the roof's underside over it, stretch by stretch
        for k in range(21):
            p = G.point_along_segment(w["start"], w["end"], k / 20.0)
            planes = R.cut_planes_for(cut, w["id"], w, p)
            assert R.surface_z(planes, *p) == pytest.approx(R.underside_z(model, *p), abs=1e-3)
    # the south wall runs under the main roof, then the wing over the balcony, then the main roof again
    south = next(w for w in b["walls"] if abs(w["start"][1] - w["end"][1]) < 1e-9 and w["start"][1] < 25.0)
    assert len(cut["wall_spans"][south["id"]]) == 3
    from wenart.blender import shell as SH
    spans = SH.plane_spans(south, south["start"], south["end"], cut["wall_spans"][south["id"]])
    verts, _faces = SH.wall_pieces(south["start"], south["end"], 0.2, 3.0, 5.0, cut["planes"], [], spans)
    top_under_wing = max(v[2] for v in verts if 14.0 <= v[0] <= 15.0)
    assert top_under_wing == pytest.approx(R.underside_z(model, 14.5, 24.3), abs=0.02)   # up to the wing's soffit
    # the knee at a wall's outer face beside the wing comes from the eaves, the overhang and the pitch
    assert R.top_z(model, 18.0, 24.2) == pytest.approx(6.0 + 0.5 * math.tan(math.radians(30.0)), abs=1e-3)


def test_a_rectangular_outline_keeps_the_convex_roof():
    walls = _walls(0.0, 0.0, 8.0, 12.0)
    roof = {"type": "hip", "type_source": "roof_plan", "over_level_id": "L1", "outline": [[-0.5, -0.5], [8.5, -0.5],
            [8.5, 12.5], [-0.5, 12.5]], "eaves_height": {"value": 6.0, "method": "vector", "confidence": 1.0},
            "pitches_deg": [{"value": 30.0, "method": "vector", "confidence": 1.0}], "planes": [], "openings": [],
            "assumed": [], "evidence": [{"rule": "roof_plan_outline"}]}
    model = R.roof_model(roof, _building(roof, walls=walls))
    assert model["convex"] and not model.get("parts") and len(model["planes"]) == 4


# --------------------------------------------------------------------------
# The spaces under the drawn roof
# --------------------------------------------------------------------------

BALCONY = {"id": "os_bal", "label": "BALKON", "kind": "balcony", "cover": None, "level_id": "L1", "z": 3.0,
           "polygon": [[13.0, 22.2], [16.0, 22.2], [16.0, 24.2], [13.0, 24.2]], "columns": []}
VERANDA = {"id": "os_ver", "label": "VERANDA", "kind": "veranda", "cover": "roof", "level_id": "L0", "z": 0.0,
           "polygon": [[10.0, 21.9], [16.0, 21.9], [16.0, 24.2], [10.0, 24.2]], "columns": []}


def test_a_space_under_the_drawn_roof_is_covered_and_needs_no_light_roof():
    roof = _roof()
    b = _building(roof, [BALCONY, VERANDA])
    spaces = b["site"]["outdoor_spaces"]
    OD.mark_roof_cover(spaces, b)
    bal = next(s for s in spaces if s["id"] == "os_bal")
    assert bal["cover"] == "roof" and bal["cover_source"] == "building_roof" and "roof plan" in bal["cover_reason"]
    outlines = {"L0": [[11.0, 24.2], [19.0, 24.2], [19.0, 36.2], [11.0, 36.2]],
                "L1": [[11.0, 24.2], [19.0, 24.2], [19.0, 36.2], [11.0, 36.2]]}
    assert OD.roof_plan(bal, spaces, b["levels"], outlines, b) is None
    ver = next(s for s in spaces if s["id"] == "os_ver")
    lr = OD.roof_plan(ver, spaces, b["levels"], outlines, b)
    xs = [p[0] for p in lr["polygon"]]
    # 29 Oct 2026 (user on real06: "there is a gap between balcony and small roof there should not be a gap"): the
    # wing's eaves stand a storey and more over the veranda (no cover of it): the veranda's roof runs on under them
    # to the balcony's slab (x 13.0); the 0.3 m strip of floor in front of the slab gets no roof of its own
    assert max(xs) == pytest.approx(13.0, abs=1e-3)
    assert lr["drawn"]["share"] >= 0.5                       # the lower roof the roof plan draws over it


# --------------------------------------------------------------------------
# Argus: M11 and the plan_vs_model line
# --------------------------------------------------------------------------

def test_m11_passes_when_the_roof_is_built_as_drawn():
    roof = _roof(lower_roof=False)
    b = _building(roof, [dict(BALCONY, cover="roof")])
    got, n = MR.roof_vs_plan(b, R.roof_model(roof, b))
    assert n >= 1 and got == []
    assert MR.review(b)["checks"]["M11"]["failed"] == 0
    # the lower roof the plan draws beside the main roof: built (the veranda's light roof under it), nothing to say;
    # left out, it is a roof the model lost
    roof = _roof()
    light = {"kind": "light_roof", "top_z": 3.0, "polygon": [[10.0, 21.9], [12.5, 21.9], [12.5, 24.2], [10.0, 24.2]]}
    b = _building(roof, [dict(BALCONY, cover="roof"), dict(VERANDA, roof=light)])
    assert MR.roof_vs_plan(b, R.roof_model(roof, b))[0] == []
    b = _building(roof, [dict(BALCONY, cover="roof"), dict(VERANDA)])
    got, _n = MR.roof_vs_plan(b, R.roof_model(roof, b))
    assert [(f["target"], f.get("kind")) for f in got] == [("roof", "lost")] and "another roof" in got[0]["message"]


def test_m11_flags_an_assumed_outline_and_the_balcony_it_leaves_open():
    roof = TB.roof_block(_sheets(_plan_record()), LEVELS, [], _house_walls(), (0.0, 0.0), {"areas": []})
    assert roof["outline"] is None and roof["roof_plan_outline"]["points"]
    b = _building(roof, [BALCONY])
    got, _n = MR.roof_vs_plan(b, R.roof_model(roof, b))
    kinds = {(f["target"], f.get("kind")) for f in got}
    assert ("roof", "misread") in kinds                      # the outline assumed while the roof plan draws it
    assert ("os_bal", "lost") in kinds                       # the balcony the plan covers, open to the sky
    assert all(f["check"] == "M11" and f["severity"] == "major" for f in got)
    from wenart.agent import causes as CS
    from wenart.audit import kinds as K
    assert K.CHECK_KIND["M11"] == "misread" and CS.CHECK_CAUSE["M11"] == "roof_reading"
    assert "M11" in MR.CHECKS
    found = PV.roof_outline_findings(b)
    assert found and all(f["line"] == "plan_vs_model" and f["check"] == "B9" and f["owner"] == "reading"
                         for f in found)


def test_m11_reaches_argus_through_the_model_line():
    from wenart.audit import report as AR
    roof = TB.roof_block(_sheets(_plan_record()), LEVELS, [], _house_walls(), (0.0, 0.0), {"areas": []})
    b = _building(roof, [BALCONY])
    rec = MR.review(b)
    inp = SimpleNamespace(model_review=rec)
    line = AR.model_line(inp)
    assert {f["kind"] for f in line["findings"] if f["check"] == "M11"} >= {"misread", "lost"}


# --------------------------------------------------------------------------
# real06's roof plan
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real06():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _real06_region(fx: dict) -> Region:
    ents: dict = {}
    for ln in fx["lines"]:
        st = Stroke(id=f"{ln['id']}:{len(ents)}", kind="line", pts=[tuple(ln["a"]), tuple(ln["b"])], layer=ln["layer"])
        e = ents.get(ln["id"])
        if e is None:
            ents[ln["id"]] = Ent(id=ln["id"], kind="LINE", layer=ln["layer"], box=(0, 0, 0, 0), strokes=[st])
        else:
            e.strokes.append(st)
    texts = [Txt(id=t["id"], text=t["text"], box=(t["point"][0], t["point"][1], t["point"][0], t["point"][1]),
                 height=0.2, layer=t["layer"]) for t in fx["texts"]]
    xs = [p[0] for ln in fx["lines"] for p in (ln["a"], ln["b"])]
    ys = [p[1] for ln in fx["lines"] for p in (ln["a"], ln["b"])]
    return _region(list(ents.values()), texts, box=(0.0, 0.0, max(xs), max(ys)))


def test_real06_the_roof_plan_draws_the_roof_over_the_balcony_and_a_lower_roof_beside_it(real06):
    rec, why = EX.roof_plan_outline(_real06_region(real06))
    assert why == ""
    assert rec["size_m"] == pytest.approx([9.40, 17.30], abs=0.01) and len(rec["points"]) == 10
    assert rec["overhang_m"] == pytest.approx(0.50, abs=0.01) and rec["hip_lines"] >= 8
    # the lower roof over the rest of the veranda: 2.0 x 5.3 m beside the main roof, closed by its gutter
    assert len(rec["others"]) == 1 and rec["others"][0]["touches_main"]
    assert rec["others"][0]["size_m"] == pytest.approx([2.0, 5.3], abs=0.01)
    site = {"areas": real06["areas"]}
    put = TB.roof_outline_record(rec, real06["walls_L1"], "L1", site, [], real06["section_overhang_m"],
                                 real06["levels"])
    assert put["used"], put["reason"]
    assert put["fit"]["rms_m"] < 0.05
    # placed on the first floor's walls, the roof covers the BALKON as the plan draws it
    balkon = next(s for s in real06["outdoor_spaces"] if s["kind"] == "balcony")
    assert MR.overlap_area(balkon["polygon"], put["points"]) == pytest.approx(G.polygon_area(balkon["polygon"]),
                                                                             rel=1e-3)
    assert any("sa_L1_balkon" in r["spaces"] for r in put["reaches"])


def test_real06_m11_before_and_after(real06):
    rec, _ = EX.roof_plan_outline(_real06_region(real06))
    site = {"areas": real06["areas"]}
    v = {"method": "vector", "confidence": 1.0, "evidence": []}
    sheets = {"heights": {"roof": {"eaves_z": dict(v, value=real06["eaves_z"]),
                                   "overhang": dict(v, value=real06["section_overhang_m"])}},
              "exterior": {"roof": {"type": "hip", "type_source": "roof_plan", "outline": None, "ridge_lines": [],
                                    "pitches_deg": [dict(v, value=real06["pitch_deg"])], "evidence": [],
                                    "plan_outline": rec}}}
    levels = real06["levels"]
    spaces = [dict(s, cover=OD.space_kind(s["label"])["cover"]) for s in real06["outdoor_spaces"]]
    after = TB.roof_block(sheets, levels, [], real06["walls_L1"], (0.0, 0.0), site)
    assert after["outline_source"] == "roof_plan"
    b = {"levels": levels, "walls": real06["walls_L1"], "rooms": [], "openings": [], "slabs": real06["slabs"],
         "roof": after, "site": {"areas": real06["areas"], "outdoor_spaces": spaces}}
    OD.mark_roof_cover(spaces, b)
    assert next(s for s in spaces if s["kind"] == "balcony")["cover"] == "roof"
    outlines = {s["above_level_id"]: s["outline"] for s in real06["slabs"]}
    for s in spaces:                                     # their own roofs, as the level inference plans them
        s["roof"] = OD.roof_plan(s, spaces, levels, outlines, b)
    assert next(s for s in spaces if s["kind"] == "balcony")["roof"] is None     # under the main roof
    veranda = next(s for s in spaces if s["kind"] == "veranda")
    assert veranda["roof"]["drawn"]["share"] >= 0.5      # the lower roof the roof plan draws over the rest of it
    model = R.roof_model(after, b)
    assert model["parts"] and model["ridge_z"] == pytest.approx(6.0 + 4.7 * math.tan(math.radians(18.3)), abs=0.02)
    got, _n = MR.roof_vs_plan(b, model)
    assert got == []
    # before: the outline assumed (the walls + overhang) leaves the balcony the roof plan covers open
    before = dict(after, outline=None, outline_source=None)
    b0 = dict(b, roof=before)
    got, _n = MR.roof_vs_plan(b0, R.roof_model(before, b0))
    assert {(f["target"], f.get("kind")) for f in got} >= {("roof", "misread"), ("os_L1_balkon", "lost")}
