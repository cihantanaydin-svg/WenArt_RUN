"""Audit fix round 4 (27 Nov 2026): R06 sheet regions and section heights, R07 roof evidence, R24 stair formulas, and
the site trees kept out of the building's cover. Synthetic sheets, roof plans and stairs built in code; the real
projects whose inputs are in the repository are read once each (skipped without a DWG converter)."""
from __future__ import annotations

import math
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart.ingest.generic.model import Stroke
from wenart.sheets.model import Ent, Region, Sheet, Txt

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------------------------

def _line(eid: str, a, b, layer: str = "0") -> Ent:
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _rect(eid: str, x0, y0, x1, y1, layer: str = "0") -> Ent:
    st = Stroke(id=eid, kind="polyline", pts=[(x0, y0), (x1, y0), (x1, y1), (x0, y1)], closed=True, layer=layer)
    return Ent(id=eid, kind="LWPOLYLINE", layer=layer, box=(x0, y0, x1, y1), strokes=[st], rect=(x0, y0, x1, y1))


def _txt(tid: str, text: str, x, y, h: float = 0.2) -> Txt:
    w = max(len(text), 1) * h * 0.6
    return Txt(id=tid, text=text, box=(x - w / 2, y - h / 2, x + w / 2, y + h / 2), height=h)


def _plan_lines(prefix: str, x0: float, y0: float, n: int = 30) -> list[Ent]:
    """A plan's walls: a 10 x 8 m box of double lines and inner walls (``n`` entities)."""
    out = [_line(f"{prefix}a", (x0, y0), (x0 + 10, y0)), _line(f"{prefix}b", (x0 + 10, y0), (x0 + 10, y0 + 8)),
           _line(f"{prefix}c", (x0 + 10, y0 + 8), (x0, y0 + 8)), _line(f"{prefix}d", (x0, y0 + 8), (x0, y0))]
    for k in range(n - 4):
        x = x0 + 0.5 + (k % 9)
        out.append(_line(f"{prefix}w{k}", (x, y0 + 0.2), (x, y0 + 7.8)))
    return out


# --------------------------------------------------------------------------------------------------------------------
# R06: titles, levels, sheet regions
# --------------------------------------------------------------------------------------------------------------------

def test_r06_habitable_attic_titles_are_levels_and_the_bare_roof_space_is_not():
    from wenart.sheets import levels as LV
    from wenart.sheets import titles as T
    for title in ("Ç.A.P. PLANI", "ÇATI ARASI PİYESİ PLANI"):
        assert T.class_of(title)[0] == "floor_plan", title
        lw = LV.level_of(title)
        assert lw is not None and lw.kind == "attic" and lw.order is None, title
    # round 4b (defect 1): a duplex's upper floor is a storey, never an attic (its order: its number or the free place)
    assert T.class_of("DUBLEKS ÜST KAT PLANI")[0] == "floor_plan"
    assert LV.level_of("DUBLEKS ÜST KAT PLANI") is None
    assert (LV.level_of("1. KAT (DUBLEKS ÜST KAT) PLANI").order, LV.level_of("1. KAT (DUBLEKS ÜST KAT) PLANI").kind) \
        == (1, "floor")
    assert LV.level_of("(ÇATI ARASI PİYESİ)").kind == "attic"
    # the bare roof space of a section and a duplex floor titled by its elevation stay as they were
    assert LV.level_of("ÇATI ARASI") is None
    assert LV.level_of("DUBLEKS KAT PLANI (8,50)") is None
    assert T.class_of("ÇATI PLANI")[0] == "roof_plan"
    assert T.class_of("ÇAP 12") is None


def test_r06_a_frame_whose_corner_is_off_by_a_micron_is_a_rectangle():
    from wenart.sheets.model import _axis_rectangle
    st = Stroke(id="f", kind="polyline", pts=[(0.0, 10.0), (0.0, 0.0), (39.900001, 0.0), (39.9, 10.0)], closed=True)
    assert _axis_rectangle(st) == (0.0, 0.0, 39.9, 10.0)


def _two_frame_sheet():
    """Two sheet frames side by side (touching), a ground floor plan in the first and a habitable attic plan with
    rooms in the second, each titled under its drawing."""
    ents = [_rect("F1", 0, 0, 20, 15), _rect("F1i", 0.1, 0.1, 19.9, 14.9), _rect("F2", 20, 0, 40, 15),
            _rect("F2i", 20.1, 0.1, 39.9, 14.9)]
    ents += _plan_lines("p", 4, 4) + _plan_lines("q", 24, 4)
    texts = [_txt("t1", "ZEMİN KAT PLANI", 6, 1.5, 0.6), _txt("t2", "Ç.A.P. PLANI", 26, 1.5, 0.6)]
    texts += [_txt(f"r{k}", name, 5 + 3 * (k % 3) + (20 if k >= 3 else 0), 9, 0.2)
              for k, name in enumerate(["SALON", "ODA", "BANYO", "SALON", "ODA", "BANYO"])]
    return Sheet(id="s1", space="model", file="x.dxf", page=1, ents=ents, texts=texts)


def test_r06_two_frames_side_by_side_are_two_regions_and_the_attic_is_a_level_above_the_top_storey():
    from wenart.sheets import levels as LV
    from wenart.sheets import split as SP
    from wenart.sheets import titles as T
    res = SP.split_sheet(_two_frame_sheet())
    drawings = [c for c in res.clusters if c.kind == "drawing" and len(c.ents) >= 20]
    assert len(drawings) == 2
    titles = [next(t.text for t in c.texts if T.class_of(t.text)) for c in sorted(drawings, key=lambda c: c.box[0])]
    assert titles == ["ZEMİN KAT PLANI", "Ç.A.P. PLANI"]
    plans = [SimpleNamespace(id=f"r{k + 1}", file="x.dxf", title={"text": t}, evidence=[], use="read")
             for k, t in enumerate(titles)]
    LV.assign_levels(plans, [], [])
    assert [(p.level["id"], p.level["kind"]) for p in plans] == [("L0", "floor"), ("L1", "attic")]


def test_r06_a_group_standing_in_two_drawn_frames_is_split_by_the_frames():
    from wenart.sheets import split as SP
    ents = _plan_lines("p", 2, 2) + _plan_lines("q", 22, 2)
    groups = [list(range(len(ents)))]
    out = SP._split_by_frames(groups, ents, [(0, 0, 20, 12), (20, 0, 40, 12)], 0.5)
    assert sorted(len(g) for g in out) == [30, 30]
    # one frame only, or parts too small to be drawings: the group stays
    assert SP._split_by_frames(groups, ents, [(0, 0, 40, 12)], 0.5) == groups
    small = _plan_lines("p", 2, 2) + _plan_lines("q", 22, 2, n=6)
    assert len(SP._split_by_frames([list(range(len(small)))], small, [(0, 0, 20, 12), (20, 0, 40, 12)], 0.5)) == 1


def test_r06_two_titled_sections_never_join_because_one_lies_in_the_others_box():
    from wenart.sheets import split as SP
    a = SP.Cluster(ents=_plan_lines("a", 0, 0))                               # its level lines run 30 m on
    a.ents.append(_line("long", (0, 9), (40, 9)))
    b = SP.Cluster(ents=_plan_lines("b", 20, 1, n=20))
    out = SP._absorb_satellites([a, b], titled={id(a): {"section"}, id(b): {"section"}})
    assert len(out) == 2
    # an inset detail (a titled drawing a tenth of the host's size) still joins; untitled parts join as before
    c = SP.Cluster(ents=_plan_lines("c", 20, 1, n=5))
    assert len(SP._absorb_satellites([a, c], titled={id(a): {"section"}, id(c): {"section"}})) == 1
    d = SP.Cluster(ents=_plan_lines("d", 20, 1, n=20))
    assert len(SP._absorb_satellites([a, d], titled={})) == 1


def _section(marks: list):
    """A section geometry stand-in: ``marks`` [(text, value)] as the section's level marks (relative)."""
    recs = []
    for k, (text, v) in enumerate(marks):
        t = _txt(f"m{k}", text, 0.0, v)
        recs.append((t, v, (0.0, v), "symbol", {"value": v, "relative": True, "absolute": None}))
    return SimpleNamespace(marks=recs, bands=[(0, 1, "a", "b")] * 5, mpu=0.01)


LEVELS2 = [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}]


def test_r06_the_sections_level_marks_come_before_its_slab_bands():
    from wenart.sheets import heights as HT
    sec = _section([("±0.00", 0.0), ("+0.50", 0.5), ("+2.70", 2.7), ("+3.20", 3.2), ("+3.50", 3.5), ("+4.40", 4.4),
                    ("+5.70", 5.7), ("+6.20", 6.2), ("+7.45", 7.45)])
    # the slab bands of a region holding four drawings: a 7.82 m ground floor, a 7.67 m ceiling
    out = {"datum": None, "levels": [
        {"level_id": "L0", "floor_z": {"value": 0.0, "method": "vector"},
         "ceiling_height": {"value": 7.674, "method": "vector"}, "floor_to_floor": {"value": 7.824, "method": "vector"}},
        {"level_id": "L1", "floor_z": {"value": 7.824, "method": "vector"}}], "slabs": []}
    why = HT.marks_first_reasons(out, LEVELS2, sec, True)
    assert why and any("floor to floor 7.82" in w for w in why)
    el = HT.plan_marks_on_section(sec, {0: 0.5, 1: 3.5})
    assert el == {0: 0.5, 1: 3.5}
    out = {"datum": None, "levels": [], "slabs": [], "ground": [], "roof": {}}
    HT._assumed_levels(out, LEVELS2, 2.7, 0.2, "test")
    lines = HT.apply_storey_marks(out, LEVELS2, el, 0.2, "x.dxf", "r5", rule=HT.PLAN_MARKS_RULE,
                                  source="the plans' floor marks the section prints")
    lines += HT.ceilings_from_marks(out, LEVELS2, sec, el, "x.dxf", "r5")
    by = {e["level_id"]: e for e in out["levels"]}
    assert by["L0"]["floor_z"]["value"] == 0.0 and abs(by["L1"]["floor_z"]["value"] - 3.0) < 1e-9
    assert abs(by["L0"]["ceiling_height"]["value"] - 2.7) < 1e-9
    assert by["L0"]["ceiling_height"]["evidence"][0]["rule"] == "level_mark"
    assert abs(out["datum"]["relative"] - 0.5) < 1e-9
    # a plan floor mark the section does not print gives nothing; a plain 3 m storey needs no marks first
    assert HT.plan_marks_on_section(sec, {0: 0.5, 1: 3.6}) == {}
    plain = {"levels": [{"level_id": "L0", "floor_z": {"value": 0.0, "method": "vector"},
                         "ceiling_height": {"value": 2.7, "method": "vector"},
                         "floor_to_floor": {"value": 3.0, "method": "vector"}},
                        {"level_id": "L1", "floor_z": {"value": 3.0, "method": "vector"}}]}
    assert HT.marks_first_reasons(plain, LEVELS2, sec, False) == []


def _framed_plan(letters: bool = True, arrows: bool = True, layer: str = "0") -> Region:
    """A plan in a sheet frame of nested rectangles, a 12 x 8 m building, its section marks 'A' (layer ``layer``)
    left and right of the building with a triangle pointing +y over each."""
    ents = [_rect("F", 0, 0, 30, 20), _rect("Fi", 0.1, 0.1, 29.9, 19.9), _rect("Fj", 0.15, 0.15, 29.85, 19.85)]
    x0, y0 = 9.0, 6.0
    ents += [_line("w1", (x0, y0), (x0 + 12, y0)), _line("w2", (x0 + 12, y0), (x0 + 12, y0 + 8)),
             _line("w3", (x0 + 12, y0 + 8), (x0, y0 + 8)), _line("w4", (x0, y0 + 8), (x0, y0)),
             _line("w5", (x0 + 6, y0), (x0 + 6, y0 + 8))]
    texts = []
    if letters:
        texts = [_txt("A1", "A", x0 - 1.5, y0 + 3.6, 0.3), _txt("A2", "A", x0 + 13.5, y0 + 3.6, 0.3)]
    if arrows:
        for k, x in enumerate((x0 - 1.5, x0 + 13.5)):
            base = y0 + 4.1
            ents += [_line(f"t{k}a", (x - 0.15, base), (x + 0.15, base), layer),
                     _line(f"t{k}b", (x + 0.15, base), (x, base + 0.35), layer),
                     _line(f"t{k}c", (x, base + 0.35), (x - 0.15, base), layer)]
    sheet = Sheet(id="s1", space="model", file="x.dxf", page=1)
    r = Region(id="r4", file="x.dxf", sheet=sheet, box=(0, 0, 30, 20), geometry_box=(0, 0, 30, 20), ents=ents,
               texts=texts, metres_per_unit=1.0, transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    return r


def test_r06_the_reference_extent_is_the_building_outline_never_the_frame():
    from wenart.sheets import register as RG
    r = _framed_plan()
    assert RG.frame_stack_ids(r) == {"F", "Fi", "Fj"}
    (w, h), _wall = RG.building_extent(r)
    assert abs(w - 12.0) < 0.2 and abs(h - 8.0) < 0.2


def test_r06_section_marks_found_by_their_geometry_on_any_layer():
    from wenart.sheets import register as RG
    section = SimpleNamespace(title={"text": "A-A KESİTİ"})
    cut = RG.cut_line([_framed_plan()], section)
    assert cut is not None and cut["method"] == "cut_marks"
    assert cut["axis"] == "x" and cut["letter"] == "A" and cut["flipped"] is False
    assert abs(cut["at"] - 9.6) < 0.1
    # another section's letter, or letters without their triangles (an axis grid's labels), give no cut
    assert RG.cut_line([_framed_plan()], SimpleNamespace(title={"text": "B-B KESİTİ"})) is None
    assert RG.cut_line([_framed_plan(arrows=False)], section) is None


def test_r06_the_ridge_from_a_section_stands_in_the_building_outline_not_the_frame():
    from shapely.geometry import box
    from wenart.sheets import exterior as EX
    heights = {"cut_axis": "x", "roof": {"profile": [[0.0, 5.0], [6.0, 8.0], [12.0, 5.0]]}}
    lines = EX.ridge_lines({}, heights, box(0, 0, 30, 20), building_outline=box(9, 6, 21, 14))
    assert lines == [[[15.0, 6.0], [15.0, 14.0]]]


# --------------------------------------------------------------------------------------------------------------------
# R24: stair formulas
# --------------------------------------------------------------------------------------------------------------------

def test_r24_stair_formula_variants():
    from wenart.ingest.generic import stair_formula as SF
    f = SF.parse("(19X17.36Rh=330/27)")
    assert (f["risers"], f["riser_m"], f["rise_m"], f["going_m"]) == (19, 0.1736, 3.3, 0.27)
    f = SF.parse("(17x 17.65 / 28)")
    assert (f["risers"], f["riser_m"], f["rise_m"], f["going_m"]) == (17, 0.1765, None, 0.28)
    assert SF.parse("17X17.64Rh=300/27")["risers"] == 17
    assert SF.parse("19 x 0.1736 = 3.30")["riser_m"] == 0.1736
    for text in ("80/210", "50X50", "120X80", "H.B", "(19X17.36Rh=300/27)", "MER: 16"):
        assert SF.parse(text) is None, text
    assert SF.storey_ok(SF.parse("(17x 17.65 / 28)"), 3.00) is True
    assert SF.storey_ok(SF.parse("(19X17.36Rh=330/27)"), 3.00) is False


def test_r24_the_size_tag_parsers_ignore_stair_formulas():
    # 27 Nov 2026 (round 5a, R09): one size-tag parser for the whole pipeline (``tag_grammar``) replaced the copies
    from wenart.ingest import sense_rules, tag_grammar
    for text in ("(19X17.36Rh=330/27)", "(17x 17.65 / 28)", "17X17.64Rh=300/27"):
        assert tag_grammar.parse(text) is None, text
        assert sense_rules._tag_cm(text) is None, text


def _num(v: int, x: float, y: float) -> SimpleNamespace:
    return SimpleNamespace(text=str(v), height=0.12, box=(x - 0.05, y - 0.06, x + 0.05, y + 0.06),
                           evidence=[{"layer": "MERDIVEN"}])


def test_r24_a_stair_numbered_1_19_with_its_1_on_the_landing_keeps_19_risers_and_its_neighbour_its_own():
    from wenart.ingest.generic import stair_numbers as SN
    texts = [_num(1, 0.0, -0.7)]                                          # '1' 0.7 m from '2' on the landing
    texts += [_num(v, 0.0, (v - 2) * 0.27) for v in range(2, 11)]          # first flight going up
    texts += [_num(v, 1.2, (18 - v) * 0.27) for v in range(11, 20)]        # second flight coming down
    texts.append(SimpleNamespace(text="(19X17.36Rh=330/27)", height=0.1, box=(0.3, 1.0, 0.9, 1.1), evidence=[{}]))
    # the stair beside it, 2.3 m on: numbered 1-17 with its own formula; its 17 leads on to nothing of the first's
    texts += [_num(v, 3.5, -0.3 + (v - 1) * 0.27) for v in range(1, 9)]
    texts += [_num(v, 4.7, (17 - v) * 0.27 - 0.3) for v in range(9, 18)]
    texts.append(SimpleNamespace(text="(17X17.64Rh=300/27)", height=0.1, box=(3.8, 1.0, 4.4, 1.1), evidence=[{}]))
    found = sorted(SN.chains(texts), key=lambda c: c[0][1][0])
    assert [c[0] for c in found[0]] == list(range(1, 20))
    assert [c[0] for c in found[1]] == list(range(1, 18))


def _stair_piece(lines: list, spacing: list) -> SimpleNamespace:
    flights = [{"start": [0, 0], "end": [0, 2], "width": 1.0, "lines": n, "spacing": g} for n, g in zip(lines, spacing)]
    return SimpleNamespace(type="stair", center=(0.5, 1.0), size=(2.4, 3.0), rotation_deg=0.0, entity="INSERT:1",
                           details={"stair": {"flights": flights, "riser_m": None, "riser_source": None}})


def test_r24_the_formula_sets_the_riser_when_the_stair_draws_its_risers_and_findings_are_listed():
    from wenart.ingest.generic import stair_formula as SF
    p = _stair_piece([10, 9], [0.27, 0.27])
    t = SimpleNamespace(text="(19X17.36Rh=330/27)", box=(0.4, 0.9, 0.8, 1.0), evidence=[{"entity": "TEXT:E57C"}])
    notes: list = []
    assert SF.attach([p], [t], notes) == 1
    data = p.details["stair"]
    assert data["riser_m"] == 0.1736 and data["riser_source"].startswith("documented: the stair formula")
    assert data["formula"]["entity"] == "TEXT:E57C" and SF.formula_findings(data) == []
    # a partial count keeps the treads; a steep formula and unequal goings are findings
    q = _stair_piece([8, 8], [0.27, 0.34])
    SF.attach([q], [SimpleNamespace(text="(15X20Rh=300/27)", box=(0.4, 0.9, 0.8, 1.0), evidence=[{}])], notes)
    found = SF.formula_findings(q.details["stair"])
    assert q.details["stair"]["riser_m"] is None
    # round 4b (defect 13, item 3): the written going '/27' wins over the measured spacing; the steep riser is the
    # regulation's finding on common stairs (levels.model._stair_formulas), not this module's
    assert not any("goings differ" in f for f in found) and not any("0.200 m" in f for f in found)
    assert any("draws 16 risers" in f for f in found)
    w = _stair_piece([8, 8], [0.27, 0.34])
    SF.attach([w], [SimpleNamespace(text="(16x18.75Rh=300)", box=(0.4, 0.9, 0.8, 1.0), evidence=[{}])], notes)
    assert any("goings differ" in f for f in SF.formula_findings(w.details["stair"]))


def test_r24_the_storey_check_and_a_full_storey_from_the_top_level():
    from wenart.levels import model as LM
    rec = {"risers": 19, "riser_m": 0.1736, "text": "(19X17.36Rh=330/27)", "drawn_risers": 19, "used": "riser"}
    # the building JSON keeps a stair piece's record under 'stair' (a reading under 'details.stair')
    stair = {"id": "f_L0_006", "type": "stair", "level_id": "L0", "footprint": {"center": [5.0, 5.0]},
             "stair": {"flights": [{"lines": 19, "spacing": 0.27}], "formula": dict(rec), "riser_m": 0.1736,
                       "riser_source": "documented: the stair formula '(19X17.36Rh=330/27)'"}}
    arriving = {"id": "f_L1_001", "type": "stair", "level_id": "L1", "footprint": {"center": [5.2, 5.0]},
                "stair": {"flights": [{"lines": 19}], "formula": dict(rec)}}
    duplex = {"id": "f_L1_007", "type": "stair", "level_id": "L1", "footprint": {"center": [12.0, 3.0]},
              "details": {"stair": {"flights": [{"lines": 17}], "formula": {"risers": 17, "riser_m": 0.1765,
                                                                            "text": "(17x 17.65 / 28)"}}}}
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0}, {"id": "L1", "order": 1, "elevation": 3.30}],
         "furniture": [stair, arriving, duplex]}
    conflicts, warnings = [], []
    LM._stair_formulas(b, conflicts, warnings)
    assert stair["stair"]["formula"]["storey_ok"] is True and stair["stair"]["riser_m"] == 0.1736
    tops = [c for c in conflicts if "climbs a full storey" in c["description"]]
    assert [c["element_ids"][0] for c in tops] == ["f_L1_007"]       # the arriving stair is no stair up
    assert LM.stair_formula_range(stair) == (round(3.2984 * 0.97, 3), round(3.2984 * 1.03, 3))
    # the storey disagrees: the treads stay, the formula's riser is not used
    b["levels"][1]["elevation"] = 3.00
    LM._stair_formulas(b, [], warnings)
    assert stair["stair"]["riser_m"] is None and stair["stair"]["formula"]["storey_ok"] is False


def test_r24_a_stair_down_to_the_basement_fits_the_storey_below():
    from wenart.levels import model as LM
    down = {"id": "f_L0_001", "type": "stair", "level_id": "L0", "footprint": {"center": [1.0, 1.0]},
            "stair": {"flights": [{"lines": 17}], "riser_m": 0.1764,
                      "riser_source": "documented: the stair formula '(17X17.64Rh=300/27)'",
                      "formula": {"risers": 17, "riser_m": 0.1764, "text": "(17X17.64Rh=300/27)", "drawn_risers": 17}}}
    b = {"levels": [{"id": "L-1", "order": -1, "elevation": -3.0}, {"id": "L0", "order": 0, "elevation": 0.0},
                    {"id": "L1", "order": 1, "elevation": 3.30}], "furniture": [down]}
    LM._stair_formulas(b, [], [])
    assert down["stair"]["formula"]["storey_ok"] is True and down["stair"]["riser_m"] == 0.1764
    assert down["stair"]["formula"]["storey_m"] == 3.0


# --------------------------------------------------------------------------------------------------------------------
# R07: roof evidence
# --------------------------------------------------------------------------------------------------------------------

def test_r07_one_slope_pattern_takes_either_word_order():
    from wenart.sheets import titles as T
    for text, v in (("EĞİM%33", 33.0), ("EĞİM %33", 33.0), ("%30 EĞİM", 30.0), ("%33 EGIM", 33.0),
                    ("30% SLOPE", 30.0), ("EGIM: 33%", 33.0), ("PENTE 35 %", 35.0)):
        assert T.slope_pct(text) == v, text
    for text in ("%40", "12% 3.20", "1/100 %20", "eğim"):
        assert T.slope_pct(text) is None, text


def _roof_plan(slopes: list, marks: list) -> Region:
    sheet = Sheet(id="s1", space="model", file="x.dxf", page=1)
    texts = [_txt(f"s{k}", t, x, y) for k, (t, x, y) in enumerate(slopes)]
    texts += [_txt(f"k{k}", t, x, y) for k, (t, x, y) in enumerate(marks)]
    ents = [_line("h1", (0, 0), (4, 4)), _line("h2", (20, 0), (16, 4)), _line("h3", (0, 12), (4, 8)),
            _line("h4", (20, 12), (16, 8))]
    return Region(id="r4", file="x.dxf", sheet=sheet, box=(0, 0, 20, 12), geometry_box=(0, 0, 20, 12), ents=ents,
                  texts=texts, metres_per_unit=1.0, features={"hip_lines": 4}, cls="roof_plan", use="exterior")


def test_r07_a_roof_plan_gives_one_pitch_per_part_and_its_marks_the_ridge_in_the_height_frame():
    from wenart.sheets import exterior as EX
    r = _roof_plan([("%30 EĞİM", 3, 6), ("%30 EĞİM", 17, 6), ("%30 EĞİM", 10, 2), ("%33 EĞİM", 10, 10)],
                   [("+7.45", 10, 6), ("+0.50", 25, 6)])
    hip = EX.roof_from_roof_plan([r])
    assert hip is not None and abs(hip["pitch_deg"] - 16.7) < 0.05 and hip["slope_pct"] == 30.0
    # round 4b (item 4): one pitch per roof part is not built: no 'slopes' list, the other slope named in the note
    assert "slopes" not in hip and "33 % x 1" in hip["note"] and "not built yet" in hip["note"]
    # real06's 'EĞİM%33' is still read
    assert EX.roof_from_roof_plan([_roof_plan([("EĞİM%33", 3, 6), ("EĞİM%33", 17, 6)], [])])["slope_pct"] == 33.0
    loop = {"points": [[0, 0], [20, 0], [20, 12], [0, 12]]}
    rm = EX.roof_plan_marks(r, loop, 0.50)
    assert rm["ridge"]["text"] == "+7.45" and abs(rm["ridge"]["z"] - 6.95) < 1e-9
    assert EX.roof_plan_marks(r, loop, None) is None


def _house(level_kind: str = "floor", label: str = "1. Kat", window_h: float = 1.2):
    walls = [{"id": "w1", "level_id": "L1", "start": [0, 0], "end": [10, 0], "thickness": 0.25, "exterior": True},
             {"id": "w2", "level_id": "L1", "start": [10, 0], "end": [10, 8], "thickness": 0.25, "exterior": True},
             {"id": "w3", "level_id": "L1", "start": [10, 8], "end": [0, 8], "thickness": 0.25, "exterior": True},
             {"id": "w4", "level_id": "L1", "start": [0, 8], "end": [0, 0], "thickness": 0.25, "exterior": True}]
    openings = [{"id": "win_L1_001", "level_id": "L1", "type": "window", "wall_id": "w1", "center": [5, 0],
                 "width": 1.5, "sill_height": 0.9, "height": window_h}]
    levels = [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"},
              {"id": "L1", "order": 1, "elevation": 3.0, "ceiling_height": 2.7, "kind": level_kind, "label": label}]
    return {"levels": levels, "walls": walls, "openings": openings}


def test_r07_a_full_storey_takes_eaves_on_its_ceiling_and_only_an_attic_the_knee_wall():
    from wenart.blender import roof as RF
    roof = {"type": "hip", "pitches_deg": [], "outline": None}
    d = RF._derive(roof, _house())
    assert abs(d["eaves_z"] - (3.0 + 2.7 + RF.FULL_STOREY_SLAB_M)) < 1e-6
    assert any(a["field"] == "eaves_height" and "full storey" in a["reason"] for a in d["assumed"])
    att = RF._derive(roof, _house("attic", "Çatı Katı"))
    # round 4b (weak test): exactly the knee wall at the outer face less the overhang's rise at the default pitch
    knee = 3.0 + RF.DEFAULTS["knee_wall"] - RF.DEFAULTS["overhang"] * math.tan(math.radians(RF.DEFAULTS["pitch_deg"]))
    assert abs(att["eaves_z"] - knee) < 1e-6
    assert RF.attic_level({"id": "L4", "kind": "floor", "label": "Ç.A.P."})


def test_r07_the_roof_never_clips_a_drawn_window_of_a_full_storey_it_raises_the_eaves():
    from wenart.blender import roof as RF
    house = _house()                                                       # sill 0.9 + 1.2: its head 2.1 m over the floor
    # a drawn ridge (7.0) and pitch (30 degrees) over the 10 x 8 m storey put the eaves at 4.33, 0.8 m under its head
    d = RF._derive({"type": "hip", "outline": None, "ridge_height": {"value": 7.0, "method": "vector"},
                    "pitches_deg": [{"value": 30.0, "method": "vector"}]}, house)
    raise_ = [a for a in d["assumed"] if a["field"] == "eaves_raise"]
    assert raise_ and any("clip" in w for w in d["warnings"])
    need, who = RF.opening_eaves(house, house["levels"][1], 0.5, math.tan(math.radians(30.0)), None)
    assert who == "window win_L1_001" and d["eaves_z"] >= need - 1e-6
    # a drawn eaves height is kept as drawn
    drawn = RF._derive({"type": "hip", "pitches_deg": [], "outline": None,
                        "eaves_height": {"value": 5.0, "method": "vector"}}, house)
    assert not [a for a in drawn["assumed"] if a["field"] == "eaves_raise"]


# --------------------------------------------------------------------------------------------------------------------
# Site: no tree stands in the building's cover
# --------------------------------------------------------------------------------------------------------------------

def test_site_trees_never_stand_in_the_buildings_cover():
    from wenart.blender import site as S
    outline = [(0, 0), (10, 0), (10, 8), (0, 8)]
    building = {"levels": [{"id": "L0", "order": 0}, {"id": "L1", "order": 1}],
                "roof": {"outline": [(-0.5, -0.5), (10.5, -0.5), (10.5, 8.5), (-0.5, 8.5)]},
                "site": {"outdoor_spaces": [{"id": "os_L1_teras", "level_id": "L1",
                                             "polygon": [(-6, 0), (0, 0), (0, 5), (-6, 5)]},
                                            {"id": "os_L0_teras", "level_id": "L0",
                                             "polygon": [(10, 0), (14, 0), (14, 4), (10, 4)]}]}}
    cover = S.building_cover(building, outline, {"L1": outline})
    assert len(cover) == 4                                                  # outline, L1, roof, the L1 terrace
    # round 4b (defect 14): inferred trees in the cover are dropped; a drawn tree there is kept and listed for review
    trees = [{"id": "t1", "kind": "tree", "center": [-3.0, 2.0], "inferred": True},
             {"id": "t2", "kind": "tree", "center": [12.0, 2.0], "inferred": True},
             {"id": "t3", "kind": "tree", "center": [10.2, 8.2], "inferred": True},
             {"id": "t4", "kind": "tree", "center": [-9.0, 9.0], "inferred": True},
             {"id": "t5", "kind": "tree", "center": [5.0, 4.0]}]
    kept, dropped = S.trees_clear_of_cover(trees, cover)
    assert [t["id"] for t in kept] == ["t2", "t4", "t5"] and "review" in kept[-1]
    assert [t["id"] for t in dropped] == ["t1", "t3"] and "dropped" in dropped[0]["dropped_reason"]


# --------------------------------------------------------------------------------------------------------------------
# Real projects (their DWG is in the repository)
# --------------------------------------------------------------------------------------------------------------------

def _converter() -> bool:
    from wenart.ingest import dwg
    return dwg.find_tool("dwg2dxf") is not None


@pytest.fixture(scope="module")
def sheets_of(tmp_path_factory):
    cache: dict = {}

    def read(project: str) -> dict:
        if project not in cache:
            pdir = ROOT / "projects" / project
            if not pdir.is_dir() or not _converter():
                pytest.skip(f"{project}: no DWG or no converter")
            from wenart.sheets import run
            out = tmp_path_factory.mktemp(project)
            cache[project] = run(pdir, out, no_ai=True, work_dir=out / "converted", debug=False,
                                 questions=False).doc
            shutil.rmtree(out / "converted", ignore_errors=True)
        return cache[project]
    return read


def test_real_the_attic_plan_frame_is_a_level_and_the_cut_marks_give_the_ridge(sheets_of):
    doc = sheets_of("real17")
    levels = {lv["id"]: lv for lv in doc["levels"]}
    assert "L4" in levels and levels["L4"]["kind"] == "attic"
    h = {e["level_id"]: e for e in doc["heights"]["levels"]}
    assert abs(h["L4"]["floor_z"]["value"] - 12.30) < 0.05
    assert doc["heights"]["cut_axis"] == "x"
    ridge = doc["exterior"]["roof"]["ridge_lines"]
    assert ridge and abs(ridge[0][0][0] - ridge[0][1][0]) < 1e-6           # the ridge runs north-south (along y)
    assert not any("ridge direction" in a for a in doc["exterior"]["roof"].get("assumed") or [])


def test_real_the_section_marks_set_the_storeys_and_the_roof_plan_the_roof(sheets_of):
    doc = sheets_of("real15")
    h = {e["level_id"]: e for e in doc["heights"]["levels"]}
    assert abs(h["L1"]["floor_z"]["value"] - 3.00) < 0.01
    assert abs(h["L0"]["ceiling_height"]["value"] - 2.70) < 0.01
    roof = doc["exterior"]["roof"]
    assert roof["type"] == "hip" and abs(roof["pitches_deg"][0]["value"] - 16.7) < 0.05
    assert abs(roof["ridge_height"]["value"] - 6.95) < 0.01
    titles = sorted((r["title"] or {}).get("text") or "" for r in doc["regions"] if r["class"] == "section")
    assert "A-A KESİTİ" in titles and "B-B KESİTİ" in titles


def test_real_the_bare_roof_space_stays_no_level(sheets_of):
    doc = sheets_of("real12")
    assert not any(lv["kind"] == "attic" and "ARASI" in str(lv.get("label") or "").upper() for lv in doc["levels"])
    assert not any(lv.get("label") == "Çatı Arası Piyesi" for lv in doc["levels"])
