"""2 Nov 2026 (user: "improve the best of your abilities the initial reading phase", "im also giving you other projects
that you can try to improve the reading"): general reading rules found on real03 and real13. CPU only, pure parts.

- area-summary notes and flat names are no room labels; area lines written with their symbol are area lines;
- a zero-length arc never stops a drawing's reading;
- a rectangle holding two or more drawing titles is a sheet frame; a part too small to be a drawing drops only the
  cut beside it;
- the plan's filled walls stay when a face-line layer only draws the same walls again;
- the reading check sums the printed areas of the labelled spaces a room joins.
"""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import box as sbox

import wenart.reading_check as RC
from wenart.ingest import dxf_generic as DG
from wenart.ingest.generic import labels as LB
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import TextRun
from wenart.sheets import split as SP
from wenart.sheets.model import Ent, Sheet, Txt


def _run(text, x=0.0, y=0.0, h=0.2):
    return TextRun(id=f"t{x}_{y}", text=text, box=(x, y, x + 0.12 * len(text), y + h), height=h)


def test_area_summary_notes_and_flat_names_are_no_room_labels():
    for t in ("Net Alan =", "Brüt Alan =", "1+1 A1 Daire Tipi", "Kullanım Alanı", "Carpet Area", "Flat 3",
              "Wohnfläche", "3 BHK", "A BLOK", "Toplam İnşaat Alanı"):
        assert LB.is_annotation(t), t
    for t in ("Oyun Alanı", "Play Area", "Salon", "Giriş Holü", "Bath+ Toilet", "Dining Area", "GUEST", "Daire Girişi",
              "SALON = 24 m2", "İşlik"):
        assert not LB.is_annotation(t), t
    # real03: the flat summaries beside the plan made no label; the room label above its area line still does
    runs = [_run("1+1 A1 Daire Tipi", 0, 10), _run("Net Alan = 34.52 m²", 0, 9.7), _run("Brüt Alan = 40.02 m²", 0, 9.4),
            _run("YAŞAMA", 5, 5), _run("16.72 m2", 5, 4.7)]
    blocks = LB.merge_label_blocks(runs)
    assert [(b.name, b.area_m2) for b in blocks] == [("YAŞAMA", 16.72)]


def test_area_lines_written_with_their_symbol():
    for t in ("A = 24,50 m²", "F: 24,50 m²", "NF = 18,20 m2"):
        assert LB._classify(_run(t), "metric").kind == "area", t
    blocks = LB.merge_label_blocks([_run("SALON", 0, 1), _run("A = 24,50 m²", 0, 0.7)])
    assert [(b.name, b.area_m2) for b in blocks] == [("SALON", 24.5)]


def test_a_zero_length_arc_never_stops_the_reading():
    arc = DG._arc_dict((0.0, 0.0), 1.0, [], full=False)
    assert arc["start_deg"] == 0.0 and arc["end_deg"] == 0.0


def _ent(eid, box, rect=False):
    return Ent(id=eid, kind=eid.split(":")[0], layer="0", box=box, rect=box if rect else None)


def _txt(tid, text, x, y, h=10.0):
    return Txt(id=tid, text=text, box=(x, y, x + len(text) * 0.8 * h, y + h), height=h)


def test_a_frame_around_titled_plans_drawn_close_together_and_small_parts():
    # real13: three plans 50 units apart (closer than the gap) in three nested frames, each plan with its title below;
    # at the left a small site panel with two small titles of its own (fewer entities than a drawing)
    ents, texts = [], []
    for k in range(3):
        x0 = 1050.0 * k
        ents += [_ent(f"LINE:p{k}_{j}", (x0 + 20 * j, 100, x0 + 20 * j + 15, 900)) for j in range(30)]
        texts += [_txt(f"TEXT:r{k}_{j}", "ODA", x0 + 100 + 200 * j, 500) for j in range(4)]
        texts.append(_txt(f"TEXT:T{k}", f"{k + 1}. KAT PLANI", x0 + 100, 20, h=40))
    ents += [_ent(f"LINE:s{j}", (-900 + 60 * j, 300, -880 + 60 * j, 700)) for j in range(6)]
    texts += [_txt("TEXT:S1", "VAZİYET PLANI", -900, 200, h=20), _txt("TEXT:S2", "A-A KESİTİ", -500, 200, h=20)]
    ents += [_ent(f"LWPOLYLINE:F{m}", (-1100 - 10 * m, -100 - 10 * m, 3300 + 10 * m, 1100 + 10 * m), rect=True)
             for m in range(3)]
    res = SP.split_sheet(Sheet(id="s1", space="model", file="x.dxf", page=1, ents=ents, texts=texts))
    assert len(res.frames) == 3
    plans = {}
    for c in res.clusters:
        for t in c.texts:
            if "KAT PLANI" in t.text:
                plans.setdefault(t.text, set()).update(e.id.split("_")[0] for e in c.ents)
    assert plans == {"1. KAT PLANI": {"LINE:p0"}, "2. KAT PLANI": {"LINE:p1"}, "3. KAT PLANI": {"LINE:p2"}}


def test_filled_walls_stay_when_a_face_line_layer_only_draws_them_again():
    filled = [W.WallPrim(kind="dxf_hatch", entity="h", stroke_ids=[], method="vector", confidence=1.0,
                         polygons=[[(0, 0), (10, 0), (10, 0.3), (0, 0.3)]]),
              W.WallPrim(kind="dxf_hatch", entity="h2", stroke_ids=[], method="vector", confidence=1.0,
                         polygons=[[(5, 0), (5.1, 0), (5.1, 6), (5, 6)]])]       # a partition the layer lacks
    same = [W._Element(kind="face_pair", polygon=sbox(0, 0, 10, 0.3), ids=["a"])]
    other = [W._Element(kind="face_pair", polygon=sbox(0, 3, 10, 3.3), ids=["b"])]
    kept = W._existing_covers(filled, same)
    assert kept is not None and kept[0] > 0.99
    assert W._existing_covers(filled, other) is None                 # the layer draws walls the fill lacks
    assert W._existing_covers([], same) is None


def test_the_check_sums_the_labelled_spaces_a_room_joins():
    page = SimpleNamespace(texts=[_run("YAŞAMA", 2, 6), _run("16.68 m2", 2, 5.7), _run("GİRİŞ HOLÜ", 2, 3),
                                  _run("2.16 m2", 2, 2.7), _run("HOL", 6, 3), _run("3.85 m2", 6, 2.7),
                                  _run("Net Alan = 54.20 m²", 20, 20)])
    tf = [1, 0, 0, 0, 1, 0]
    room = {"id": "r1", "label": "Yaşama", "polygon": [[0, 0], [10, 0], [10, 8], [0, 8]], "area_computed": 22.0}
    assert RC.area_findings(page, tf, [room], "L0") == []                      # 16.68 + 2.16 + 3.85 = 22.69
    room["area_computed"] = 30.0
    out = RC.area_findings(page, tf, [room], "L0")
    assert len(out) == 1 and out[0]["drawn_m2"] == 22.69 and len(out[0]["spaces"]) == 3
    # one of the spaces has no printed area: the sum is unknown, a minor finding names them
    page.texts = [t for t in page.texts if t.text != "3.85 m2"]
    out = RC.area_findings(page, tf, [room], "L0")
    assert len(out) == 1 and out[0]["severity"] == "minor"


# --------------------------------------------------------------------------------------- real07, real09, real13 rules
from wenart.ingest.generic import wide_gaps as WGP  # noqa: E402
from wenart.ingest.model import WallItem  # noqa: E402
from wenart.sheets import levels as LV  # noqa: E402
from wenart.sheets import titles as TT  # noqa: E402
from wenart.sheets import units_check as UC  # noqa: E402


def _wall(s, e, t=0.25):
    return WallItem(start=s, end=e, thickness=t, box=[0, 0, 0, 0], entity="w", evidence={"file": "x.dwg"})


def test_wide_gaps_in_the_outer_walls_are_inferred_openings():
    # a 10 x 8 m house: a 3.1 m sliding door between two pieces of the north wall, a 3.4 m garage door from the
    # south-west corner piece to the end of the west wall (whose last 5 cm is a piece of its own), a wall that runs
    # on to the side of another (no jamb there: no bridge)
    walls = [_wall((0, 8), (3, 8)), _wall((6.1, 8), (10, 8)),                     # north, the sliding door 3-6.1
             _wall((10, 8), (10, 0)), _wall((10, 0), (3.6, 0)), _wall((3.6, 0), (3.4, 0)),
             _wall((3.5, 0), (3.5, 4)),                                            # a partition at the corner piece
             _wall((0, 8), (0, 0.05)), _wall((0, 0.05), (0, 0.0)),                 # west wall, last 5 cm apart
             _wall((5, 4), (8, 4), 0.1)]                                           # an inner wall ending in a room
    got = sorted((round(b["width"], 1), b["from_free_end"]) for b in WGP.bridges(walls))
    assert (3.1, True) in got
    assert any(abs(w - 3.3) < 0.15 for w, _ in got)                               # the garage door, from the corner
    assert not any(w > 4.5 for w, _ in got)
    chosen = [b for b in WGP.bridges(walls) if b["width"] > 3.0]
    w2, o2 = WGP.apply(walls, [], chosen)
    assert len(w2) == len(walls) + len(chosen) and all(o.kind == "opening" and o.status == "unverified" for o in o2)
    assert all(w.inferred and w.evidence["rule"] == "wide_gap" and w.evidence["file"] == "x.dwg"
               for w in w2[len(walls):])


def test_level_titles_with_roman_numerals_brackets_and_split_runs():
    assert LV.level_of("I.KAT PLANI").order == 1 and LV.level_of("III. KAT").order == 3
    assert LV.level_of("1.(+5.20 KOTU) KAT PLANI Ö: 1/50").order == 1
    assert LV.level_of("TERAS.(+13.30 KOTU) KAT PLANI").kind == "roof_terrace"
    assert LV.title_elevations("NORMAL KAT PLANI (2,50-5,50)") == (2.5, 5.5)
    # real09: a title written as separate texts on one line
    runs = [Txt(id="a", text="1.BODRUM", box=(0, 0, 8, 1), height=1.0), Txt(id="b", text="KAT PLANI", box=(8.6, 0, 17, 1),
            height=1.0), Txt(id="c", text="Ö:1/50", box=(17.5, 0, 22, 1), height=1.0),
            Txt(id="d", text="SALON", box=(0, 20, 3, 20.4), height=0.4)]
    lines = TT.join_lines(runs)
    title = next(t for t in lines if "PLANI" in t.text)
    assert title.text == "1.BODRUM KAT PLANI Ö:1/50" and title.id == "b" and LV.level_of(title.text).order == -1


def test_floor_names_never_title_a_section_or_an_elevation():
    texts = [Txt(id=f"t{k}", text=name, box=(0, k * 10, 30, k * 10 + 5), height=5.0)
             for k, name in enumerate(["1.BODRUM KAT", "ZEMIN KAT", "1.KAT", "2.KAT"])]
    texts.append(Txt(id="T", text="MERDİVEN KESİTİ DETAYI Ö:1/20", box=(0, -20, 60, -15), height=4.5))
    t = TT.pick_title(texts, (0, 0, 100, 50))
    assert t is not None and TT.class_of(t.text)[0] == "section"
    assert TT.class_of("GÜNEY CEPHESİ")[0] == "elevation"


def test_a_plan_without_a_level_word_takes_the_storey_its_title_elevation_gives():
    def plan(text):
        return SimpleNamespace(title={"text": text, "box": [0, 0, 1, 1]}, texts=[], evidence=[], file="x", id=text)
    plans = [plan("1.BODRUM KAT PLANI (0,00)"), plan("NORMAL KAT PLANI (2,50-5,50)"), plan("DUBLEKS KAT PLANI (8,50)"),
             plan("ÇATI KAT PLANI (11,50)")]
    words = {id(r): LV.level_of(r.title["text"]) for r in plans}
    LV._by_title_elevation(plans, words)
    assert words[id(plans[2])].order == 3 and words[id(plans[2])].label == "Dubleks Kat"


def test_bare_dimension_numbers_are_cm_or_mm_and_the_unit_tie_break():
    # "315" over 315 units: the drawing is in the text's unit, cm or mm, never m
    dim = SimpleNamespace(text="315", measured_units=315.0)
    reg = SimpleNamespace(ents=[SimpleNamespace(dim=dim)] * 4)
    c = UC.check_dimensions([reg])
    assert c.unit is None and c.shares["cm"] == c.shares["mm"] == 1.0 and c.shares["m"] == 0.0
    # no unit in the header; level marks say cm, a weak check m, text height cm or in, drawing size cm or in
    checks = [UC.Check("level_marks", "cm", 0.9, 100, shares={"cm": 0.9}),
              UC.Check("dimensions", "m", 0.53, 19, shares={"m": 0.53}),
              UC.Check("text_height", None, None, 50, values=[10.5] * 50)]
    drawings = [SimpleNamespace(geometry_box=(0, 0, 2500, 1800), ents=[0] * 60) for _ in range(3)]
    assert UC.tie_break(checks, drawings)[0] == "cm"
    assert UC.tie_break(checks[:2], []) is None                                    # cm 1, m 1: no decision


def test_a_header_the_checks_contradict_gives_way_to_the_clear_unit():
    # real14: $INSUNITS mm; door swings cm (514), bare-number dimensions cm or mm, text height and drawing size cm or in
    checks = [UC.Check("door_widths", "cm", 0.97, 514, shares={"cm": 0.97}),
              UC.Check("dimensions", None, 0.87, 688, shares={"cm": 0.87, "mm": 0.87}),
              UC.Check("text_height", None, None, 5594, values=[15.0] * 50)]
    drawings = [SimpleNamespace(geometry_box=(0, 0, 2500, 1800), ents=[0] * 60, kind="drawing") for _ in range(3)]
    assert UC.tie_break(checks + [UC.Check("header", "mm", 1.0, 1)], drawings)[0] == "cm"


def test_argus_reports_the_reading_self_check(tmp_path):
    import json

    from wenart.audit import lessons as ALS
    assert ALS.reading_check(tmp_path, "p") is None                                  # no self-check: not run
    d = tmp_path / "reading_check"
    d.mkdir()
    (d / "reading_check.json").write_text(json.dumps({"findings": [
        {"check": "RC1", "severity": "critical", "level_id": "L1", "message": "level 1. Kat left out"},
        {"check": "RC5", "severity": "minor", "level_id": "L0", "message": "an inferred wall"}]}))
    got = ALS.reading_check(tmp_path, "p")
    assert len(got) == 1 and got[0]["check"] == "U39" and got[0]["severity"] == "critical"
    assert "UL273" in ALS.CHECK_LESSONS["U39"]


def test_a_clear_cut_narrower_than_the_old_bins_is_found():
    # real11: two plans 0.02 units apart (1 m at 1:50) while gap / 8 was 0.018 units: the exact sweep finds the gap
    import numpy as np
    lo = np.array([0.0, 0.5, 0.62, 1.0])
    hi = np.array([0.6, 0.6, 1.2, 1.2])                 # the gap is 0.60-0.62
    c = SP._clear_cut(lo, hi, 0.1, 1.1, gap=0.144)
    assert c is not None and 0.60 <= c <= 0.62
    assert SP._clear_cut(np.array([0.0] * 10), np.array([2.0] * 10), 0.1, 1.1, gap=0.144) is None


def test_plans_titled_by_their_elevation_take_one_storey_each():
    # real12: '+13.30 KOT KAT PLANI' and '+16.30 KOTU KAT PLANI' above a titled '3. KAT PLANI (+10.30)'
    def plan(text):
        return SimpleNamespace(title={"text": text, "box": [0, 0, 1, 1]}, texts=[], evidence=[], file="x", id=text)
    plans = [plan("ZEMİN KAT PLANI (±0.00)"), plan("3. KAT PLANI (+10.30)"), plan("+16.30 KOTU KAT PLANI"),
             plan("+13.30 KOT KAT PLANI")]
    words = {id(r): LV.level_of(r.title["text"]) for r in plans}
    LV._by_title_elevation(plans, words, [])
    assert words[id(plans[3])].order == 4 and words[id(plans[2])].order == 5


def test_a_glazed_run_between_two_walls_bridges_an_open_facade():
    # real09: the living room's facade to the balcony is a 4 m door-window run on 'kapı-pencere', no wall faces
    from wenart.ingest.generic.model import Stroke
    walls = [_wall((0, 0), (0, 5)), _wall((0, 5), (8, 5)), _wall((8, 5), (8, 0)), _wall((8, 0), (4, 0))]
    glass = Stroke(id="LINE:G", kind="line", pts=[(0.1, 0.0), (3.9, 0.0)], layer="kapı-pencere")
    railing = Stroke(id="LINE:R", kind="line", pts=[(0.1, -1.2), (3.9, -1.2)], layer="balkon")
    got = WGP.joinery_bridges(walls, [], [glass, railing])
    assert len(got) == 1 and got[0]["rule"] == "glazed_run" and got[0]["entity"] == "LINE:G"
    w2, o2 = WGP.apply(walls, [], got)
    assert w2[-1].evidence["rule"] == "glazed_run" and w2[-1].evidence["layer"] == "kapı-pencere"
    assert o2[-1].type_raw.endswith("glazed_run)")
    # a window line inside a wall's own gap is the openings reader's, never a bridge
    assert WGP.joinery_bridges(walls, [], [Stroke(id="LINE:W", kind="line", pts=[(0, 1), (0, 3)], layer="PENCERE")]) == []
