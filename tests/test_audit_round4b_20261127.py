"""Audit fix round 4b (27 Nov 2026): the 14 defects an independent review found in audit fix round 4 (sheet regions,
section-cut marks, storey heights from section marks, attic titles, roof pitch / ridge / eaves, stair formulas, site
trees), the concerns fixed with them, and the regression set's new structure lines. Every test builds its drawing in
code (the reviewer's repros); each fails on the code before this round (0a678fd1)."""
from __future__ import annotations

import json
import math
from types import SimpleNamespace

import pytest

from wenart.ingest.generic.model import Stroke
from wenart.sheets.model import Ent, Region, Sheet, Txt


# --------------------------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------------------------

def _line(eid: str, a, b, layer: str = "0") -> Ent:
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _poly(eid: str, pts: list, layer: str = "0") -> Ent:
    st = Stroke(id=eid, kind="polyline", pts=[tuple(p) for p in pts], closed=True, layer=layer)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Ent(id=eid, kind="LWPOLYLINE", layer=layer, box=(min(xs), min(ys), max(xs), max(ys)), strokes=[st])


def _txt(tid: str, text: str, x, y, h: float = 0.2) -> Txt:
    w = max(len(text), 1) * h * 0.6
    return Txt(id=tid, text=text, box=(x - w / 2, y - h / 2, x + w / 2, y + h / 2), height=h)


def _sheet() -> Sheet:
    return Sheet(id="s1", space="model", file="x.dxf", page=1)


def _vec(v, rule="slab_bands"):
    return {"value": v, "method": "vector", "confidence": 1.0, "evidence": [{"rule": rule}]}


def _plan_with_cut_marks(letter_dy: float, tri: str = "equilateral", bubble: str = "") -> Region:
    """A 12 x 8 m building with its section marks 'A' left and right on the cut line y = 10: a triangle standing on
    the line, apex +y (the view), the letter ``letter_dy`` above or below the line; ``bubble`` 'square' / 'hexagon'
    draws a grid bubble round each letter."""
    x0, y0 = 9.0, 6.0
    ents = [_line("w1", (x0, y0), (x0 + 12, y0)), _line("w2", (x0 + 12, y0), (x0 + 12, y0 + 8)),
            _line("w3", (x0 + 12, y0 + 8), (x0, y0 + 8)), _line("w4", (x0, y0 + 8), (x0, y0)),
            _line("w5", (x0 + 6, y0), (x0 + 6, y0 + 8))]
    yc = y0 + 4.0
    texts = []
    for k, x in enumerate((x0 - 1.5, x0 + 13.5)):
        if tri == "equilateral":
            pts = [(x - 0.2, yc), (x + 0.2, yc), (x, yc + 0.3464)]
        elif tri == "wide":
            pts = [(x - 0.3, yc), (x + 0.3, yc), (x, yc + 0.25)]
        else:                                             # a flag: a right triangle with one side on the line
            pts = [(x, yc), (x + 0.4, yc), (x, yc + 0.35)]
        ents += [_line(f"t{k}a", pts[0], pts[1]), _line(f"t{k}b", pts[1], pts[2]), _line(f"t{k}c", pts[2], pts[0])]
        ty = yc + letter_dy
        texts.append(_txt(f"A{k}", "A", x, ty, 0.3))
        if bubble == "square":
            ents.append(_poly(f"b{k}", [(x - 0.3, ty - 0.3), (x + 0.3, ty - 0.3), (x + 0.3, ty + 0.3), (x - 0.3, ty + 0.3)]))
        elif bubble == "hexagon":
            ents.append(_poly(f"b{k}", [(x + 0.32 * math.cos(math.radians(a)), ty + 0.32 * math.sin(math.radians(a)))
                                        for a in range(0, 360, 60)]))
    return Region(id="r4", file="x.dxf", sheet=_sheet(), box=(0, 0, 30, 20), geometry_box=(0, 0, 30, 20), ents=ents,
                  texts=texts, metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])


# --------------------------------------------------------------------------------------------------------------------
# defect 1: a duplex's upper floor is a storey; a numbered title is its floor
# --------------------------------------------------------------------------------------------------------------------

def _assign(titles: list) -> list:
    from wenart.sheets import levels as LV
    plans = [SimpleNamespace(id=f"r{k + 1}", file="x.dxf", title={"text": t}, evidence=[], use="read", level=None)
             for k, t in enumerate(titles)]
    LV.assign_levels(plans, [], [])
    return [((p.level or {}).get("id"), (p.level or {}).get("kind")) for p in plans]


def test_d1_a_duplex_upper_floor_is_a_storey_and_a_floor_number_wins():
    assert _assign(["ZEMİN KAT PLANI", "DUBLEKS ÜST KAT PLANI", "2. KAT PLANI", "3. KAT PLANI"]) == \
        [("L0", "floor"), ("L1", "floor"), ("L2", "floor"), ("L3", "floor")]
    assert _assign(["ZEMİN KAT (DUBLEKS ALT KAT) PLANI", "1. KAT (DUBLEKS ÜST KAT) PLANI", "2. KAT PLANI"]) == \
        [("L0", "floor"), ("L1", "floor"), ("L2", "floor")]
    # an unnumbered habitable attic still goes on top; a numbered one keeps its number and its kind
    assert _assign(["ZEMİN KAT PLANI", "1. KAT PLANI", "Ç.A.P. PLANI"])[-1] == ("L2", "attic")
    from wenart.sheets import levels as LV
    lw = LV.level_of("3. KAT (ÇATI ARASI PİYESİ) PLANI")
    assert (lw.order, lw.kind) == (3, "attic")


# --------------------------------------------------------------------------------------------------------------------
# defect 2: the view of a cut mark is the corner opposite the side on the cut line, wherever the letter stands
# --------------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("tri", ["equilateral", "wide", "flag"])
def test_d2_the_cut_view_does_not_depend_on_where_the_letter_is_written(tri):
    from wenart.sheets import register as RG
    sec = SimpleNamespace(title={"text": "A-A KESİTİ"})
    for dy in (-0.35, 0.65):
        cut = RG.cut_line([_plan_with_cut_marks(dy, tri)], sec)
        assert cut is not None and cut["view"] == [0.0, 1.0] and cut["flipped"] is False, (tri, dy)


@pytest.mark.parametrize("bubble", ["square", "hexagon"])
def test_concern_grid_labels_in_square_or_hexagon_bubbles_are_no_cut_marks(bubble):
    from wenart.sheets import register as RG
    sec = SimpleNamespace(title={"text": "A-A KESİTİ"})
    assert RG.cut_line([_plan_with_cut_marks(0.65)], sec) is not None
    assert RG.cut_line([_plan_with_cut_marks(0.65, bubble=bubble)], sec) is None


# --------------------------------------------------------------------------------------------------------------------
# defect 3: only roof pitches vote; drain and ramp falls never
# --------------------------------------------------------------------------------------------------------------------

def _roof_plan(texts: list) -> Region:
    ents = [_line("h1", (0, 0), (4, 4)), _line("h2", (20, 0), (16, 4)), _line("h3", (0, 12), (4, 8)),
            _line("h4", (20, 12), (16, 8))]
    return Region(id="r4", file="x.dxf", sheet=_sheet(), box=(0, -1, 20, 12), geometry_box=(0, -1, 20, 12), ents=ents,
                  texts=[_txt(f"s{k}", t, x, y) for k, (t, x, y) in enumerate(texts)], metres_per_unit=1.0,
                  features={"hip_lines": 4}, cls="roof_plan", use="exterior")


def test_d3_gutter_falls_never_outvote_the_roof_pitch():
    from wenart.sheets import exterior as EX
    texts = [("%35 EĞİM", 3, 6), ("%35 EĞİM", 17, 6)] + [("%1 EĞİM", 2 + 5 * k, -0.4) for k in range(4)]
    hip = EX.roof_from_roof_plan([_roof_plan(texts)])
    assert hip is not None and hip["slope_pct"] == 35.0 and abs(hip["pitch_deg"] - 19.29) < 0.01
    # a slope written with a drain word, or beside one, is no roof pitch either
    texts = [("%35 EĞİM", 3, 6), ("%35 EĞİM", 17, 6)] + [("%15 EĞİM OLUK", 2 + 5 * k, 3) for k in range(3)] \
        + [("%15 EĞİM", 10, 9), ("BÜZ", 10.6, 9)]
    assert EX.roof_from_roof_plan([_roof_plan(texts)])["slope_pct"] == 35.0
    # only drainage falls: no roof
    assert EX.roof_from_roof_plan([_roof_plan([("%2 EĞİM", 3, 6), ("%2 EĞİM", 17, 6)])]) is None


# --------------------------------------------------------------------------------------------------------------------
# defects 4 and 5: storeys from the section's marks
# --------------------------------------------------------------------------------------------------------------------

def _tall(marks: list, datum: dict):
    hj = {"datum": datum, "levels": [
        {"level_id": "L0", "floor_z": _vec(0.0), "ceiling_height": _vec(2.80), "floor_to_floor": _vec(3.00)},
        {"level_id": "L1", "floor_z": _vec(3.00), "ceiling_height": _vec(5.35), "floor_to_floor": _vec(5.60)}],
        "slabs": [], "ground": [], "roof": {}}
    sec = SimpleNamespace(bands=[(0, 1, "a", "b")] * 3, mpu=0.01,
                          marks=[(SimpleNamespace(text=t, id=f"m{k}"), v, (0, 0), "symbol", rec)
                                 for k, (t, v, rec) in enumerate(marks)])
    return hj, sec


LEVELS2 = [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}]


def test_d4_a_tall_storey_refuses_only_itself_and_absolute_marks_can_confirm_it():
    import wenart.sheets as S
    region = SimpleNamespace(id="r5", file="x.dxf")
    conflicts = []

    def conflict(kind, regions, desc, res):
        conflicts.append((kind, desc, res))
        return "c1"
    hj, sec = _tall([("±0.00", 0.0, {"value": 0.0, "relative": True}), ("+3.00", 3.0, {"value": 3.0, "relative": True})],
                    {"value": 0.0, "method": "vector", "relative": 0.0})
    lines = S._marks_first(hj, LEVELS2, sec, [], [], {}, region, [], conflict)
    by = {e["level_id"]: e for e in hj["levels"]}
    assert by["L0"]["floor_z"]["method"] == "vector" and by["L0"]["floor_to_floor"]["method"] == "vector"
    assert by["L1"]["floor_z"]["method"] == "vector" and by["L1"]["floor_to_floor"]["method"] == "assumed"
    assert lines and "L1" in lines[0] and conflicts and conflicts[0][0] == "level_mark_mismatch"
    # absolute marks only: the roof slab's printed 108.60 confirms the 5.60 m storey in the datum's own frame
    hj, sec = _tall([("100.00", 100.0, {"value": 100.0, "relative": False, "absolute": 100.0}),
                     ("103.00", 103.0, {"value": 103.0, "relative": False, "absolute": 103.0}),
                     ("108.60", 108.6, {"value": 108.6, "relative": False, "absolute": 108.6})],
                    {"value": 100.0, "method": "vector"})
    assert S._marks_first(hj, LEVELS2, sec, [], [], {}, region, [], conflict) == []
    assert hj["levels"][1]["floor_to_floor"]["value"] == 5.60


def _marks_base_case(monkeypatch, ground_mark):
    import wenart.sheets as S
    from wenart.sheets import levels as LV
    hj = {"datum": None, "levels": [
        {"level_id": "L0", "floor_z": _vec(0.0), "ceiling_height": _vec(7.6), "floor_to_floor": _vec(7.82)},
        {"level_id": "L1", "floor_z": _vec(7.82), "ceiling_height": _vec(2.8), "floor_to_floor": _vec(3.0)},
        {"level_id": "L2", "floor_z": _vec(10.82)}], "slabs": [], "ground": [], "roof": {}}
    marks = [("+3.50", 3.5), ("+3.20", 3.2), ("+6.50", 6.5), ("+6.20", 6.2), ("+9.20", 9.2)]
    sec = SimpleNamespace(bands=[(0, 1, "a", "b")] * 4, mpu=0.01,
                          marks=[(SimpleNamespace(text=t, id=f"m{k}"), v, (0, 0), "symbol",
                                  {"value": v, "relative": True}) for k, (t, v) in enumerate(marks)])
    levels = [{"id": f"L{k}", "order": k, "kind": "floor"} for k in range(3)]
    plans = [SimpleNamespace(id=f"r{k}") for k in range(3)]
    levels_json = [{"id": f"L{k}", "order": k, "base_region": f"r{k}"} for k in range(3)]
    monkeypatch.setattr(LV, "floor_mark", lambda r: {"r0": ground_mark, "r1": 3.5, "r2": 6.5}[r.id])
    w: list = []
    S._marks_first(hj, levels, sec, plans, levels_json, {}, SimpleNamespace(id="r5", file="x.dxf"), w)
    return {e["level_id"]: e for e in hj["levels"]}, hj, w


def test_d5_the_ground_floors_own_mark_is_z_0_when_the_section_does_not_print_it(monkeypatch):
    by, hj, _w = _marks_base_case(monkeypatch, 0.5)
    assert [round(by[k]["floor_z"]["value"], 3) for k in ("L0", "L1", "L2")] == [0.0, 3.0, 6.0]
    assert by["L1"]["floor_z"]["method"] == "vector" and abs(hj["datum"]["relative"] - 0.5) < 1e-9
    # no ground floor mark anywhere: the printed marks have no z 0 and set nothing
    by, hj, w = _marks_base_case(monkeypatch, None)
    assert by["L1"]["floor_z"]["value"] != 0.0 or by["L1"]["floor_z"]["method"] != "vector"
    assert any("no z 0" in x for x in w)


def test_concern_a_plan_whose_floor_mark_cannot_be_read_is_logged(monkeypatch):
    import wenart.sheets as S
    from wenart.sheets import levels as LV

    def boom(r):
        raise ValueError("broken mark")
    monkeypatch.setattr(LV, "floor_mark", boom)
    hj, sec = _tall([("±0.00", 0.0, {"value": 0.0, "relative": True})], {"value": 0.0, "method": "vector",
                                                                          "relative": 0.0})
    w: list = []
    S._marks_first(hj, LEVELS2, sec, [SimpleNamespace(id="r1")], [{"id": "L0", "order": 0, "base_region": "r1"}],
                   {}, SimpleNamespace(id="r5", file="x.dxf"), w)
    assert any("could not be read" in x and "broken mark" in x for x in w)


# --------------------------------------------------------------------------------------------------------------------
# defect 6: a section with no slab band reads no roof profile; nothing sloped over its walls is a flat roof
# --------------------------------------------------------------------------------------------------------------------

def _section_without_bands(storey_marks: bool, pitched: bool) -> Region:
    """A section region with two outer walls and no slab band: stair flights and a lift's arched top inside; storey
    marks '+0.00' ... '+13.50' printed on both sides (``storey_marks``) or once each; a pitched roof (``pitched``)."""
    ents = [_line("wl", (0, 0), (0, 12)), _line("wr", (14, 0), (14, 12))]
    for k in range(6):                                  # stair flights and an arched lift top: sloped lines everywhere
        y = 1.0 + 1.8 * k
        ents.append(_line(f"f{k}", (2 + k, y), (3.5 + k, y + 1.2)))
    ents += [_line("arc1", (9, 12.5), (10, 13.3)), _line("arc2", (10, 13.3), (11, 12.5))]
    if pitched:
        ents += [_line("r1", (-0.5, 13.6), (7, 17.0)), _line("r2", (7, 17.0), (14.5, 13.6))]
    texts = []
    for k, v in enumerate((0.0, 3.0, 13.5)):
        for side, x in enumerate((-0.9, 14.9) if storey_marks else (14.9,)):
            texts.append(_txt(f"m{k}{side}", f"{v:+.2f}", x, v + 0.15, 0.2))
            ents.append(_line(f"ml{k}{side}", (x - 0.35, v), (x + 0.35, v)))
    return Region(id="r1", file="x.dxf", sheet=_sheet(), box=(-1.5, -1, 15.5, 18), geometry_box=(-1.5, -1, 15.5, 18),
                  ents=ents, texts=texts, metres_per_unit=1.0, cls="section", use="heights")


def test_d6_no_slab_band_no_roof_lines_under_the_top_storey_mark_and_the_roof_reads_flat():
    from wenart.sheets import exterior as EX
    from wenart.sheets import heights as HT
    g = HT.read_section(_section_without_bands(storey_marks=True, pitched=False), 1.0)
    assert g.walls is not None and g.bands == [] and len(g.marks) == 6
    assert g.profile == [] and g.roof_lines == 0
    assert EX.roof_from_section(g) == ("flat", [])
    # a pitched roof over the top storey mark is still read
    g = HT.read_section(_section_without_bands(storey_marks=True, pitched=True), 1.0)
    assert g.roof_lines == 2 and EX.roof_from_section(g)[0] == "gable"
    # marks printed once (no storey mark): every sloped line counts, as before this round
    g = HT.read_section(_section_without_bands(storey_marks=False, pitched=True), 1.0)
    assert g.roof_lines > 2


# --------------------------------------------------------------------------------------------------------------------
# defects 7-9: the eaves raise at each opening's own wall face, under the ridge actually built, drawn heights only
# --------------------------------------------------------------------------------------------------------------------

def _house(win_wall: str, sill=0.4, height=2.2):
    walls = [{"id": "s", "level_id": "L1", "start": [0, 0], "end": [12, 0], "thickness": 0.25, "exterior": True},
             {"id": "e", "level_id": "L1", "start": [12, 0], "end": [12, 8], "thickness": 0.25, "exterior": True},
             {"id": "n", "level_id": "L1", "start": [12, 8], "end": [0, 8], "thickness": 0.25, "exterior": True},
             {"id": "w", "level_id": "L1", "start": [0, 8], "end": [0, 0], "thickness": 0.25, "exterior": True}]
    c = {"s": [6, 0], "e": [12, 4], "n": [6, 8], "w": [0, 4]}[win_wall]
    op = {"id": "win1", "level_id": "L1", "type": "window", "wall_id": win_wall, "center": c, "width": 1.2}
    if sill is not None:
        op["sill_height"] = sill
    if height is not None:
        op["height"] = height
    lv = [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"},
          {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.7, "kind": "floor", "label": "1. Kat"}]
    return {"levels": lv, "walls": walls, "openings": [op]}


def _raise(d):
    return [a["value"] for a in d["assumed"] if a["field"] == "eaves_raise"]


def test_d7_the_eaves_raise_checks_the_walls_under_the_turned_ridge():
    from wenart.blender import roof as RF
    roof = {"type": "gable", "outline": None, "ridge_height": {"value": 8.0, "method": "vector"},
            "pitches_deg": [{"value": 35.0, "method": "vector"}]}
    # the east wall: a gable end with the ridge along x, under the eaves when the ridge is turned
    assert _raise(RF._derive(roof, _house("e"), turn=False)) == []
    assert _raise(RF._derive(roof, _house("e"), turn=True))
    # the south wall: under the eaves along x, a gable end when turned
    assert _raise(RF._derive(roof, _house("s"), turn=False))
    assert _raise(RF._derive(roof, _house("s"), turn=True)) == []


def test_d8_a_wall_set_back_under_the_roof_raises_nothing():
    from wenart.blender import roof as RF
    W = lambda i, a, b: {"id": i, "level_id": "L1", "start": list(a), "end": list(b), "thickness": 0.25,  # noqa: E731
                         "exterior": True}
    walls = [W("s", (0, 0), (8, 0)), W("r1", (8, 0), (8, 3)), W("r2", (8, 3), (12, 3)), W("e", (12, 3), (12, 8)),
             W("n", (12, 8), (0, 8)), W("w", (0, 8), (0, 0))]
    levels = [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"},
              {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.7, "kind": "floor", "label": "1. Kat"}]
    door = {"id": "d_terrace", "level_id": "L1", "type": "door", "wall_id": "r2", "center": [10, 3], "width": 0.9,
            "height": 2.2, "sill_height": 0.0}
    win = {"id": "win_s", "level_id": "L1", "type": "window", "wall_id": "s", "center": [4, 0], "width": 1.2,
           "sill_height": 0.8, "height": 1.0}
    roof = {"type": "hip", "outline": [[-0.5, -0.5], [12.5, -0.5], [12.5, 8.5], [-0.5, 8.5]],
            "pitches_deg": [{"value": 30.0, "method": "vector"}], "ridge_height": {"value": 7.6, "method": "vector"}}
    for ops in ([win], [win, door]):
        d = RF._derive(roof, {"levels": levels, "walls": walls, "openings": ops})
        assert _raise(d) == [] and abs(d["ridge_z"] - 7.6) < 1e-6, [o["id"] for o in ops]


def test_d9_a_default_opening_height_never_moves_a_drawn_ridge():
    from wenart.blender import roof as RF
    h = _house("s", sill=None, height=None)
    h["openings"][0]["width"] = 2.6
    r2 = {"type": "hip", "outline": None, "ridge_height": {"value": 7.0, "method": "vector"},
          "pitches_deg": [{"value": 35.0, "method": "vector"}]}
    d = RF._derive(r2, h)
    assert _raise(d) == [] and abs(d["ridge_z"] - 7.0) < 1e-6
    assert any(a["field"] == "conflict" for a in d["assumed"]) and any(w.startswith("conflict:") for w in d["warnings"])
    # a drawn opening still raises a drawn ridge, and the conflict is listed
    d = RF._derive(r2, _house("s"))
    assert _raise(d) and d["ridge_z"] > 7.0 + 1e-3
    assert any(a["field"] == "conflict" and "drawn ridge" in a["reason"] for a in d["assumed"])
    # an assumed roof (no drawn ridge) still rises for a default opening
    d = RF._derive({"type": "hip", "outline": None, "pitches_deg": [{"value": 35.0, "method": "vector"}]},
                   _house("s", sill=None, height=None))
    assert not any(a["field"] == "conflict" for a in d["assumed"])


def test_concern_an_opening_that_cannot_be_checked_is_logged():
    from wenart.blender import roof as RF
    h = _house("s")
    h["openings"][0].pop("center")
    d = RF._derive({"type": "hip", "outline": None, "pitches_deg": [{"value": 35.0, "method": "vector"}]}, h)
    assert any("not checked" in w for w in d["warnings"])


# --------------------------------------------------------------------------------------------------------------------
# defects 10 and 11: stair formulas need a formula's context; one formula per chain
# --------------------------------------------------------------------------------------------------------------------

def _num(v, x, y):
    return SimpleNamespace(text=str(v), height=0.12, box=(x - 0.05, y - 0.06, x + 0.05, y + 0.06),
                           evidence=[{"layer": "MERDIVEN"}])


def test_d10_size_labels_are_no_stair_formulas():
    from wenart.ingest.generic import stair_formula as SF
    from wenart.ingest.generic import stair_numbers as SN
    for t in ("20x20 SERAMİK", "15X15", "S1 25x25", "25X25", "ŞAFT 20x20", "10x10", "12x12 cm", "2x0.15",
              "AHŞAP KÜPEŞTE 10x10", "dikme 10x10", "YÜKSELME PARCASI 5X10", "5 X 10", "(20x20)", "KUTU PROFIL (40x40)"):
        assert SF.parse(t) is None and not SF.is_formula(t), t
    for t, n in (("M1:20x16.00/27", 20), ("16x18/28", 16), ("(17x 17.65 / 28)", 17), ("(15X20Rh=300/27)", 15),
                 ("4 X 17.50 / 27", 4), ("19 x 0.1736 = 3.30", 19), ("(17x17.65)", 17)):
        assert SF.parse(t)["risers"] == n, t
    texts = [_num(v, 0.0, (v - 1) * 0.27) for v in range(1, 19)]
    texts.append(SimpleNamespace(text="S3 15X15", height=0.1, box=(1.2, -0.6, 1.8, -0.5), evidence=[{}]))
    assert [c[0] for c in SN.chains(texts)[0]] == list(range(1, 19))


def test_d11_a_neighbouring_stairs_formula_never_caps_a_chain():
    from wenart.ingest.generic import stair_numbers as SN

    def txt(s, x, y):
        return SimpleNamespace(text=s, height=0.1, box=(x - 0.3, y - 0.05, x + 0.3, y + 0.05), evidence=[{}])
    a = [_num(v, 0.0, (v - 1) * 0.27) for v in range(1, 20)]
    b = [_num(v, 1.2, (v - 1) * 0.27) for v in range(1, 18)]
    texts = a + b + [txt("(19X17.36Rh=330/27)", 0.35, 2.6), txt("(17X17.64Rh=300/27)", 0.75, 0.3)]
    ch = sorted(SN.chains(texts), key=lambda c: c[0][1][0])
    assert [(c[0][0], c[-1][0]) for c in ch] == [(1, 19), (1, 17)]


# --------------------------------------------------------------------------------------------------------------------
# defects 12 and 13, item 3: the storey checks and the findings of a stair formula
# --------------------------------------------------------------------------------------------------------------------

def _stair(level, formula, center=(1.0, 1.0), lines=(9, 8), spacing=(0.27, 0.27)):
    return {"id": f"f_{level}_001", "type": "stair", "level_id": level, "footprint": {"center": list(center),
                                                                                     "size": [2.4, 3.0]},
            "stair": {"flights": [{"lines": n, "spacing": g} for n, g in zip(lines, spacing)],
                      "riser_m": formula["riser_m"], "formula": dict(formula)}}


def test_d12_a_formula_of_the_flight_down_sets_no_climbing_range():
    from wenart.levels import model as LM
    f = {"risers": 17, "riser_m": 0.1764, "text": "(17X17.64Rh=300/27)", "drawn_risers": 17}
    b = {"levels": [{"id": "L-1", "order": -1, "elevation": -3.0, "elevation_source": "section"},
                    {"id": "L0", "order": 0, "elevation": 0.0, "elevation_source": "section"},
                    {"id": "L1", "order": 1, "elevation": 3.30, "elevation_source": "section"}],
         "furniture": [_stair("L0", f)], "rooms": []}
    conflicts: list = []
    LM._storey_vs_stairs(b, [], {"mark_tol": 0.05}, conflicts, [], [])
    assert not [c for c in conflicts if c["kind"] == "storey_height_mismatch"]
    assert LM.formula_goes_down(b, b["furniture"][0]) is True
    # the same formula on a 3.00 m storey above is a flight up: its range is used
    b["levels"][2]["elevation"] = 3.00
    assert LM.formula_goes_down(b, b["furniture"][0]) is False
    assert LM.storey_stairs(b, "L0")[0][1] == LM.stair_formula_range(b["furniture"][0])


def test_d13_a_written_going_wins_and_the_steep_finding_is_the_regulations_on_common_stairs(monkeypatch):
    from wenart.ingest.generic import stair_formula as SF
    from wenart.levels import model as LM
    from wenart.reading_check import regulations as REG
    assert not hasattr(SF, "COMMON_RISER_MAX_M")                         # one source of the limits
    lim = REG.load_limits()
    assert (REG.riser_limit(lim, True), REG.riser_limit(lim, False)) == (0.18, 0.16)
    duplex = {"risers": 15, "riser_m": 0.20, "rise_m": 3.0, "going_m": 0.27, "text": "(15X20Rh=300/27)",
              "drawn_risers": 15}

    def run(b):
        conflicts, warnings = [], []
        LM._stair_formulas(b, conflicts, warnings)
        return [c["description"] for c in conflicts]
    levels = [{"id": "L0", "order": 0, "elevation": 0.0}, {"id": "L1", "order": 1, "elevation": 3.0},
              {"id": "L2", "order": 2, "elevation": 6.0}]
    # reader noise in the spacing (0.241 / 0.404) and a private stair: no finding
    b = {"levels": levels, "furniture": [_stair("L1", duplex, lines=(8, 3), spacing=(0.241, 0.404))], "rooms": []}
    found = run(b)
    assert not any("goings differ" in d for d in found) and not any("over 0.1" in d for d in found)

    class Common:
        residential, lift = True, False

        def __init__(self, building, limits):
            self.limits = limits

        def common_stair(self, lid, piece):
            return True
    monkeypatch.setattr(REG, "Context", Common)
    b = {"levels": levels, "furniture": [_stair("L1", duplex)], "rooms": []}
    found = run(b)
    assert any("0.200 m over 0.16 m" in d for d in found)


def test_item3_a_full_storey_from_the_top_level_may_be_a_stair_to_the_roof():
    from wenart.levels import model as LM
    f = {"risers": 17, "riser_m": 0.1764, "text": "(17X17.64Rh=300/27)", "drawn_risers": 17}
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0}, {"id": "L1", "order": 1, "elevation": 3.0}],
         "furniture": [_stair("L1", f, center=(9.0, 9.0))], "rooms": []}
    conflicts: list = []
    LM._stair_formulas(b, conflicts, [])
    assert any("a stair up to the roof" in c["description"] for c in conflicts)


# --------------------------------------------------------------------------------------------------------------------
# defect 14: a drawn tree in a courtyard
# --------------------------------------------------------------------------------------------------------------------

def test_d14_a_drawn_tree_in_a_courtyard_stays():
    from wenart.blender import geom2d
    from wenart.blender import site as S

    def wall(i, a, b):
        return {"id": f"w{i}", "level_id": "L0", "start": list(a), "end": list(b), "thickness": 0.3}
    outer = [(0, 0), (20, 0), (20, 20), (0, 20)]
    inner = [(6, 6), (14, 6), (14, 14), (6, 14)]
    walls = [wall(i, outer[i], outer[(i + 1) % 4]) for i in range(4)] + \
        [wall(4 + i, inner[i], inner[(i + 1) % 4]) for i in range(4)]
    loop, _how = geom2d.wall_outline(walls)
    tree = {"id": "court_tree", "kind": "tree", "center": [10.0, 10.0], "source": "drawn"}
    building = {"levels": [{"id": "L0", "order": 0}], "roof": {}, "site": {},
                "rooms": [{"id": "r_court", "level_id": "L0", "label": "AVLU", "room_type": "other",
                           "polygon": [list(p) for p in inner]}]}
    cover = S.building_cover(building, loop, {"L0": loop})
    kept, dropped = S.trees_clear_of_cover([tree], cover, S.open_to_sky(building))
    assert [t["id"] for t in kept] == ["court_tree"] and not dropped and "review" not in kept[0]
    # the courtyard not read: the drawn tree is kept as drawn and listed for review, never dropped
    kept, dropped = S.trees_clear_of_cover([tree], cover, S.open_to_sky(dict(building, rooms=[])))
    assert [t["id"] for t in kept] == ["court_tree"] and not dropped and kept[0]["review"]
    # a room of the floor above over the courtyard roofs it over
    upper = dict(building, levels=[{"id": "L0", "order": 0}, {"id": "L1", "order": 1}],
                 rooms=building["rooms"] + [{"id": "r_up", "level_id": "L1", "label": "SALON", "room_type": "living",
                                             "polygon": [list(p) for p in inner]}])
    assert S.open_to_sky(upper) == []


# --------------------------------------------------------------------------------------------------------------------
# concerns: the roof plan's marks, the ridge from a section, the frame split
# --------------------------------------------------------------------------------------------------------------------

def test_concern_no_datum_takes_the_ground_plans_own_floor_mark(monkeypatch):
    from wenart.sheets import exterior as EX
    from wenart.sheets import levels as LV
    plans = [SimpleNamespace(id="r1", level={"order": 0}), SimpleNamespace(id="r2", level={"order": 1})]
    monkeypatch.setattr(LV, "floor_mark", lambda r: {"r1": 0.5, "r2": 3.5}[r.id])
    assert EX.ground_floor_mark(plans)[0] == 0.5
    monkeypatch.setattr(LV, "floor_mark", lambda r: None)
    m, how = EX.ground_floor_mark(plans)
    assert m == 0.0 and "assumed" in how


def test_concern_a_stair_house_or_a_chimney_top_is_no_main_ridge():
    from wenart.sheets import exterior as EX
    ents = [_line("h1", (0, 0), (4, 4)), _line("h2", (20, 0), (16, 4)), _line("h3", (0, 12), (4, 8)),
            _line("h4", (20, 12), (16, 8)), _poly("lift", [(14, 2), (17, 2), (17, 5), (14, 5)])]
    texts = [_txt("k1", "+7.45", 10, 6), _txt("k2", "+10.20", 6, 3), _txt("k3", "MERDİVEN EVİ", 6, 2.5),
             _txt("k4", "+9.80", 15.5, 3.5)]
    r = Region(id="r4", file="x.dxf", sheet=_sheet(), box=(0, 0, 20, 12), geometry_box=(0, 0, 20, 12), ents=ents,
               texts=texts, metres_per_unit=1.0, cls="roof_plan", use="exterior")
    rm = EX.roof_plan_marks(r, {"points": [[0, 0], [20, 0], [20, 12], [0, 12]]}, 0.5)
    assert rm["ridge"]["text"] == "+7.45"
    assert {m["text"]: bool(m["not_main"]) for m in rm["marks"]} == {"+7.45": False, "+10.20": True, "+9.80": True}


def test_concern_a_roof_plan_mark_replacing_the_sections_ridge_is_a_listed_conflict():
    from wenart.sheets import exterior as EX
    got = []
    sec = SimpleNamespace(region=SimpleNamespace(id="r6"),
                          marks=[(SimpleNamespace(text="MAHYA KOTU +8.65"), 8.65, (0, 0), "symbol",
                                  {"value": 8.65, "relative": True})])
    m = {"z": 8.15, "value": 8.65, "text": "+8.65"}
    cid = EX.plan_mark_conflict("ridge", m, {"roof": {"ridge_z": {"value": 8.60}}}, sec, SimpleNamespace(id="r9"),
                                lambda *a: got.append(a) or "sc_001")
    assert cid == "sc_001" and got[0][1] == ["r9", "r6"] and "prints the same mark" in got[0][2]
    assert EX.plan_mark_conflict("ridge", m, {"roof": {"ridge_z": {"value": 8.20}}}, sec, SimpleNamespace(id="r9"),
                                 lambda *a: "x") is None


def test_concern_the_ridge_from_a_section_keeps_its_share_of_the_sections_width():
    from shapely.geometry import box
    from wenart.sheets import exterior as EX
    heights = {"cut_axis": "x", "section_width_m": 15.09,
               "roof": {"profile": [[0.0, 5.0], [7.545, 8.0], [15.09, 5.0]]}}
    notes: list = []
    lines = EX.ridge_lines({}, heights, box(0, 0, 30, 30), building_outline=box(6.17, 9.28, 19.89, 22.28), notes=notes)
    assert abs(lines[0][0][0] - (6.17 + 13.72 / 2.0)) < 0.01 and notes
    # a section as wide as the building: as before
    heights["section_width_m"] = 13.72
    heights["roof"]["profile"] = [[0.0, 5.0], [6.86, 8.0], [13.72, 5.0]]
    assert abs(EX.ridge_lines({}, heights, None, building_outline=box(6.17, 9.28, 19.89, 22.28))[0][0][0] - 13.03) < 0.01


def test_concern_a_plan_whose_frame_holds_inset_frames_stays_one_drawing():
    from wenart.sheets import split as SP
    ents = []
    for k in range(200):
        x = 5 + (k % 40) * 0.5
        ents.append(_line(f"p{k}", (x, 5), (x, 15)))
    for d, x0 in (("a", 27), ("b", 1)):
        for k in range(25):
            ents.append(_line(f"{d}{k}", (x0 + 0.1 * k, 6), (x0 + 0.1 * k, 8)))
    frames = [(0, 0, 32, 20), (26.5, 5.5, 30, 8.5), (0.5, 5.5, 4, 8.5)]
    out = SP._split_by_frames([list(range(len(ents)))], ents, frames, 0.3)
    assert len(out) == 1 and len(out[0]) == 250


# --------------------------------------------------------------------------------------------------------------------
# item 6: the regression set prints the structure
# --------------------------------------------------------------------------------------------------------------------

def test_item6_the_regression_set_prints_the_structure(tmp_path):
    from wenart.reading_check import regress as RG
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "elevation_source": "section", "ceiling_height": 2.7,
                     "ceiling_height_source": "section"},
                    {"id": "L1", "order": 1, "elevation": 3.0, "elevation_source": "section", "ceiling_height": 2.7,
                     "ceiling_height_source": "assumed_default"}],
         "walls": [{"id": f"w{i}", "level_id": "L1", "start": list(a), "end": list(c), "thickness": 0.25,
                    "exterior": True} for i, (a, c) in enumerate((((0, 0), (10, 0)), ((10, 0), (10, 8)),
                                                                  ((10, 8), (0, 8)), ((0, 8), (0, 0))))],
         "openings": [], "furniture": [], "rooms": [],
         "roof": {"type": "hip", "type_source": "roof_plan", "pitches_deg": [{"value": 30.0, "method": "derived"}],
                  "ridge_height": {"value": 8.0, "method": "vector"}, "eaves_height": None, "over_level_id": "L1"}}
    (tmp_path / "sheets.json").write_text(json.dumps({"heights": {"section_regions": ["r5"], "cut_axis": "x",
                                                                  "cut_at": 4.0, "flipped": False}}))
    lines = RG.structure_lines(RG.structure(tmp_path, b))
    assert lines[0] == "L0 floor +0.00 (section) ceiling 2.70 (section)"
    assert "section r5: cut axis x at 4.00 flipped False" in lines
    assert any(ln.startswith("roof read: hip (roof_plan) pitch 30.0 ridge +8.00 (vector)") for ln in lines)
    built = next(ln for ln in lines if ln.startswith("roof built:"))
    assert "ridge +8.00" in built and "ridge dir x" in built
    # a baseline written before the struct lines is not compared on them; one written after gives notes
    new = {"structure": RG.structure(tmp_path, b)}
    assert RG.structure_changes({}, new) == []
    old = json.loads(json.dumps(new))
    old["structure"]["levels"]["L1"]["floor"] = 3.3
    assert RG.structure_changes(old, new) and RG.structure_changes(old, new)[0].startswith("struct changed: L1 floor")


def test_d2_an_arrow_along_the_cut_line_says_nothing_and_a_flag_down_looks_down():
    from wenart.sheets import register as RG
    assert RG._arrow_dir([(0, 0), (0.4, 0.04), (0.4, -0.04)], (0, 0), (1.0, 0.0)) is None
    assert RG._arrow_dir([(0, 0), (0.4, 0), (0, -0.35)], (0, 3.0), (1.0, 0.0)) == (0.0, -1.0)
