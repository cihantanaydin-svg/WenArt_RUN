"""CPU tests of the level-mark reader (docs/milestone12.md §3.1, B10; wenart/levels/marks.py) and of its use by the
sheets unit check and the section heights (wenart/sheets/units_check.py, heights.py)."""
import pytest

from wenart.levels import marks as LM
from wenart.sheets import units_check as UC

# (text, value, relative, absolute, kind_hint): every form of §3.1
FORMS = [
    ("±0.00", 0.0, True, None, None),
    ("+-0.00", 0.0, True, None, None),
    ("%%p0.00", 0.0, True, None, None),
    ("+-0.00(dük)", 0.0, True, None, None),
    ("+0.15", 0.15, True, None, None),
    ("-0.45", -0.45, True, None, None),
    ("-3,15", -3.15, True, None, None),
    ("+0,15", 0.15, True, None, None),
    ("KOT +3.00", 3.0, True, None, None),
    ("KOT: +0.15", 0.15, True, None, None),
    ("Ü.K. +0.15", 0.15, True, None, "slab_top"),
    ("ÜK +0.15", 0.15, True, None, "slab_top"),
    ("S.K. +3.00", 3.0, True, None, None),
    ("T.Z. -0.45", -0.45, True, None, "ground_natural"),
    ("T.Z.: -0.45", -0.45, True, None, "ground_natural"),
    ("TABİİ ZEMİN -0.60", -0.6, True, None, "ground_natural"),
    ("TESVİYE 0.00 KOTU : 93.20", 0.0, True, 93.2, "ground_finished"),
    ("SB. KOTU : 93.20", 93.2, False, 93.2, "plinth"),
    ("BİNA GİRİŞ KOTU : 93.20", 93.2, False, 93.2, "entrance"),
    ("100.18(şev üst kotu)", 100.18, False, 100.18, "slope_top"),
    ("±0.00 = 93.20", 0.0, True, 93.2, "datum"),
    ("+0.00 / 93.20", 0.0, True, 93.2, None),
    ("±0.00 KOT", 0.0, True, None, None),
    ("FFL +0.15", 0.15, True, None, "floor"),
    ("BDK 37.00", 37.0, False, 37.0, "floor"),
    ("+3.20 m", 3.2, True, None, None),
]


@pytest.mark.parametrize("text,value,relative,absolute,kind", FORMS)
def test_every_form_of_the_design_is_read(text, value, relative, absolute, kind):
    rec = LM.parse_mark(text)
    assert rec is not None, text
    assert set(rec) == {"value", "relative", "absolute", "kind_hint", "raw"}         # the frozen contract
    assert rec["value"] == pytest.approx(value) and rec["relative"] is relative and rec["raw"] == text
    assert (rec["absolute"] is None) if absolute is None else rec["absolute"] == pytest.approx(absolute)
    assert rec["kind_hint"] == kind


@pytest.mark.parametrize("text", ["3.20", "43.00", "0.90", "12,50 m²", "12.50 M2", "3,45", "1.20/2.10", "L=3.20",
                                  "h=2.10", "2x0.60", "SALON +0.15", "ŞEV ÜST KOTU", "Subasman Kotu:", "KOT",
                                  "KOT-ARAZI", "+3.20 / +6.40", "", "SALON", "120", "3.2"])
def test_no_false_positives(text):
    """A bare number, an area, a dimension, a word with a number or a keyword without a value is no mark."""
    assert LM.parse_mark(text) is None


def test_a_bare_value_needs_a_tag_or_a_symbol():
    assert LM.parse_mark("93.20") is None
    rec = LM.read_mark("93.20", bare=True)
    assert rec["value"] == 93.2 and not rec["relative"] and rec["absolute"] == 93.2 and rec["bare"]
    assert LM.read_mark("+0.15")["bare"] is False
    assert LM.read_mark("12,50 m²", bare=True) is None                    # an area stays no mark
    assert LM.is_mark_tag("kot-arazi") and LM.is_mark_tag("KOT2") and not LM.is_mark_tag("MAHAL")
    assert LM.tag_kind("KOT-ARAZI") == "ground_natural" and LM.tag_kind("BDK") == "floor" and LM.tag_kind("KOT") is None


def test_a_site_note_is_a_note():
    assert LM.read_mark("TESVİYE 0.00 KOTU : 93.20")["note"] is True
    assert LM.read_mark("SB. KOTU : 93.20")["note"] is True
    assert LM.read_mark("+0.15")["note"] is False and LM.read_mark("100.18(şev üst kotu)")["note"] is False


def test_the_old_pattern_rejected_the_turkish_forms():
    """B10: the M10 pattern (kept here as it was) read none of the Turkish forms the reader reads now."""
    import re
    old = re.compile(r"^\s*(?:KOT\s*)?([±+\-]?)\s*(\d{1,4}[.,]\d{2,3})\s*(?:M)?\s*$", re.IGNORECASE)
    turkish = ["+-0.00", "+-0.00(dük)", "KOT: +0.15", "Ü.K. +0.15", "T.Z. -0.45", "±0.00 KOT", "SB. KOTU : 93.20",
               "BİNA GİRİŞ KOTU : 93.20"]
    assert not any(old.match(t.replace(" ", "")) for t in turkish)
    assert all(LM.parse_mark(t) is not None for t in turkish)


def test_units_check_reads_the_new_forms_and_keeps_the_old():
    from wenart.sheets.model import Txt
    texts = [Txt("MTEXT:1", "43.00", (100, 60, 180, 80), 20), Txt("MTEXT:2", "±0.00", (0, 0, 1, 1), 1),
             Txt("MTEXT:3", "+3,15", (0, 0, 1, 1), 1), Txt("MTEXT:4", "SALON", (0, 0, 1, 1), 1),
             Txt("MTEXT:5", "+-0.00", (0, 0, 1, 1), 1), Txt("MTEXT:6", "KOT: +3.00", (0, 0, 1, 1), 1),
             Txt("MTEXT:7", "T.Z. -0.45", (0, 0, 1, 1), 1), Txt("MTEXT:8", "12,50 m²", (0, 0, 1, 1), 1)]
    assert [v for _, v in UC.mark_texts(texts)] == [43.0, 0.0, 3.15, 0.0, 3.0, -0.45]
    recs = dict((t.id, r) for t, r in UC.mark_records(texts))
    assert recs["MTEXT:1"]["relative"] is False and recs["MTEXT:7"]["kind_hint"] == "ground_natural"
    assert not hasattr(UC, "MARK_RE")                                       # one reader (B10)


def _section(marks):
    """A section region: two slab bands (ground floor at y 300, first floor at y 600; 1 unit = 1 cm), outer walls,
    and level marks with their triangles (apex at y)."""
    from wenart.ingest.generic.model import Stroke
    from wenart.sheets import heights as H
    from wenart.sheets.model import Txt

    class Region:
        id = "r9"
        geometry_box = (0, 0, 1000, 900)

        def __init__(self, strokes, texts):
            self._s, self.texts = strokes, texts

        def strokes(self):
            return self._s

    st = [Stroke("L:w1", "line", [(0, 0), (0, 900)]), Stroke("L:w2", "line", [(1000, 0), (1000, 900)])]
    for k, y in enumerate((280, 300, 580, 600)):
        st.append(Stroke(f"L:b{k}", "line", [(0, y), (1000, y)]))
    texts = []
    for k, (text, y) in enumerate(marks):
        x = 1100
        st += [Stroke(f"L:t{k}a", "line", [(x, y), (x - 10, y + 10)]), Stroke(f"L:t{k}b", "line", [(x, y), (x + 10, y + 10)])]
        texts.append(Txt(f"MTEXT:m{k}", text, (x - 30, y + 15, x + 30, y + 30), 15))
    return H.read_section(Region(st, texts), 0.01)


def test_section_marks_in_two_frames_are_compared_in_their_own_frame():
    """A section that writes ±0.00 = 43.00 at the ground floor and +3.00 at the first floor: the datum is 43.00, the
    first-floor mark gives +3.00 m (the M10 code took the pair as 0.0 and compared 43.00-style values)."""
    from wenart.sheets import heights as H
    sec = _section([("±0.00 = 43.00", 300), ("+3.00", 600)])
    assert len(sec.marks) == 2 and sec.marks[0][4]["absolute"] == 43.0
    conflicts = []
    out, _w = H.heights(sec, [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}],
                        None, {}, "s.dxf", lambda *a: conflicts.append(a) or "c1")
    assert out["datum"]["value"] == 43.0
    assert out["levels"][1]["level_mark"]["value"] == pytest.approx(3.0) and not conflicts
    # an absolute mark and an absolute datum: compared as before (43.00 / 46.00)
    sec = _section([("43.00", 300), ("46.00", 600)])
    out, _w = H.heights(sec, [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}],
                        None, {}, "s.dxf", lambda *a: conflicts.append(a) or "c1")
    assert out["datum"]["value"] == 43.0 and out["levels"][1]["level_mark"]["value"] == pytest.approx(3.0)
    assert not conflicts
