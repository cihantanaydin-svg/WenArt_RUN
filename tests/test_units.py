"""CPU tests for wenart.units: lengths, size pairs and areas in metric and imperial (docs/milestone7.md §1.1)."""
import re

import pytest

from wenart import units as U

FT, INCH, SQFT = U.FT, U.INCH, U.SQFT


@pytest.mark.parametrize("text, metres, precision", [
    # feet and inches, every mark and separator
    ("50'", 50 * FT, FT / 2),
    ("30’", 30 * FT, FT / 2),
    ("11′", 11 * FT, FT / 2),
    ("11' 3\"", 11 * FT + 3 * INCH, INCH / 2),
    ("11'-3\"", 11 * FT + 3 * INCH, INCH / 2),
    ("11' - 3\"", 11 * FT + 3 * INCH, INCH / 2),
    ("11'3\"", 11 * FT + 3 * INCH, INCH / 2),
    ("11'3", 11 * FT + 3 * INCH, INCH / 2),
    ("11′ 3″", 11 * FT + 3 * INCH, INCH / 2),
    ("11’ 3”", 11 * FT + 3 * INCH, INCH / 2),
    ("11' 3''", 11 * FT + 3 * INCH, INCH / 2),
    ("14'-0\"", 14 * FT, INCH / 2),
    ("0'-6\"", 6 * INCH, INCH / 2),
    ("11 ft", 11 * FT, FT / 2),
    ("11ft", 11 * FT, FT / 2),
    ("11 FT 3 IN", 11 * FT + 3 * INCH, INCH / 2),
    ("11 feet", 11 * FT, FT / 2),
    ("1 foot", FT, FT / 2),
    ("11.5'", 11.5 * FT, 0.1 * FT / 2),
    ("6\"", 6 * INCH, INCH / 2),
    ("6''", 6 * INCH, INCH / 2),
    ("6 in", 6 * INCH, INCH / 2),
    ("1 in", INCH, 0.0127),
    ("6 inches", 6 * INCH, INCH / 2),
    ("3 1/2\"", 3.5 * INCH, INCH / 4),
    ("1/2\"", 0.5 * INCH, INCH / 4),
    ("5'10 1/2\"", 5 * FT + 10.5 * INCH, INCH / 4),
    # metric, as ingest.model.parse_number reads it today
    ("3,45", 3.45, 0.005),
    ("4,50", 4.5, 0.005),
    ("4,5", 4.5, 0.05),
    ("3.45", 3.45, 0.005),
    ("3,45 m", 3.45, 0.005),
    ("3.45M", 3.45, 0.005),
    ("345 cm", 3.45, 0.005),
    ("345cm", 3.45, 0.005),
    ("3450 mm", 3.45, 0.0005),
    ("345", 345.0, 0.5),
    ("  10,20  ", 10.2, 0.005),
])
def test_parse_length_spellings(text, metres, precision):
    length = U.parse_length(text)
    assert length is not None, text
    assert length.metres == pytest.approx(metres)
    assert length.precision_m == pytest.approx(precision)
    assert length.text == text.strip()
    marked = any(m in text for m in ("'", "’", "′", '"', "”", "″", "ft", "FT", "feet", "foot", " in", "inch"))
    assert length.system == ("imperial" if marked else "metric")


@pytest.mark.parametrize("text", [
    "", "   ", "abc", "Bed Room", "1/100", "ÖLÇEK 1/100", "3. 4", ".5", "-3", "11'-14\"", "1.234,5",
    "11' x 10'", "24,50 m²", "3,45 m2", "1/0\"", "3/2\"", "5'-7/4\"", "x", "50' 50'",
])
def test_parse_length_rejects(text):
    assert U.parse_length(text) is None


def test_bare_numbers_need_the_page_system():
    """Ambiguity: a bare integer or dot decimal is feet only on an imperial page; a decimal comma is metres."""
    assert U.parse_length("12").system == "metric" and U.parse_length("12").metres == 12.0
    imperial = U.parse_length("12", default_system="imperial")
    assert imperial.system == "imperial" and imperial.metres == pytest.approx(12 * FT)
    assert U.parse_length("12.5", default_system="imperial").metres == pytest.approx(12.5 * FT)
    assert U.parse_length("12,5", default_system="imperial").system == "metric"
    assert U.parse_length("12,5", default_system="imperial").metres == 12.5
    assert U.parse_length("345 cm", default_system="imperial").metres == pytest.approx(3.45)
    assert U.parse_length("12", default_system="metric").metres == 12.0
    with pytest.raises(ValueError):
        U.parse_length("12", default_system="furlong")
    # Explicit systems vs undecided bare numbers (the page vote ignores the latter).
    assert U.system_of("4,50") == "metric"
    assert U.system_of("345 cm") == "metric"
    assert U.system_of("50'") == "imperial"
    assert U.system_of("345") is None and U.system_of("3.45") is None
    assert U.system_of("11 x 10'") == "imperial" and U.system_of("320 x 410") is None
    assert U.system_of("110 sq ft") == "imperial" and U.system_of("24,50 m²") == "metric"
    assert U.system_of("Bed Room") is None


# The metric rule of wenart.ingest.model.parse_number before Milestone 7, copied here as the reference:
# parse_length must give the same metres for every text it accepted and reject every text it rejected,
# imperial spellings aside.
_OLD_NUMBER_RE = re.compile(r"^\s*(\d+(?:[.,]\d+)?)\s*(?:m|cm|mm)?\s*$", re.IGNORECASE)


def _old_parse_number(text):
    match = _OLD_NUMBER_RE.match(text)
    if not match:
        return None
    value = float(match.group(1).replace(",", "."))
    lowered = text.lower()
    if lowered.rstrip().endswith("mm"):
        return value / 1000.0
    if lowered.rstrip().endswith("cm"):
        return value / 100.0
    return value


@pytest.mark.parametrize("text", [
    "3,45", "3.45", "345", "345 cm", "345CM", "3450 mm", "3,45 m", "3,45M", " 4,30 ", "10,20", "0,90", "1,234",
    "1.234,5", "3,45 m²", "3 m 45", "abc", "", "3,", ",5", "3,45 cm", "9,60", "ÖLÇEK 1/100", "+3", "3e2",
])
def test_metric_behaviour_matches_the_old_parse_number(text):
    old = _old_parse_number(text)
    new = U.parse_length(text)
    if old is None:
        assert new is None, text
    else:
        assert new is not None and new.system == "metric" and new.metres == pytest.approx(old), text


@pytest.mark.parametrize("text, first, second", [
    ("11' x 10'", 11 * FT, 10 * FT),
    ("11'x10'", 11 * FT, 10 * FT),
    ("14'-0\" X 12'-0\"", 14 * FT, 12 * FT),
    ("9' 3\" x 10' 3\"", 9.25 * FT, 10.25 * FT),
    ("4' x 4' 9\"", 4 * FT, 4.75 * FT),
    ("11' 3\" x 15' 3\"", 11.25 * FT, 15.25 * FT),
    ("11'3\"x15'3\"", 11.25 * FT, 15.25 * FT),
    ("11' × 10'", 11 * FT, 10 * FT),
    ("11' * 10'", 11 * FT, 10 * FT),
    ("3,20 x 4,10", 3.2, 4.1),
    ("3.20 X 4.10", 3.2, 4.1),
    ("3.20x4.10 m", 3.2, 4.1),         # the bare member takes the partner's unit
    ("320 x 410 cm", 3.2, 4.1),
    ("11 x 10'", 11 * FT, 10 * FT),
    ("10' 3\" x 11", 10.25 * FT, 11 * FT),
])
def test_parse_size_pair(text, first, second):
    pair = U.parse_size_pair(text)
    assert pair is not None, text
    assert pair[0].metres == pytest.approx(first) and pair[1].metres == pytest.approx(second)
    assert pair[0].system == pair[1].system
    assert U.parse_length(text) is None


def test_size_pair_ambiguity_and_rejects():
    assert U.parse_size_pair("11' x 3,20") is None            # members in different systems
    assert U.parse_size_pair("2 x 3 x 4") is None
    assert U.parse_size_pair("x 10'") is None and U.parse_size_pair("11' x") is None
    assert U.parse_size_pair("Bed Room") is None and U.parse_size_pair("BOX ROOM") is None
    assert U.parse_size_pair("11' 3\"") is None
    bare = U.parse_size_pair("11 x 10")
    assert bare[0].system == "metric" and bare[0].metres == 11.0
    feet = U.parse_size_pair("11 x 10", default_system="imperial")
    assert feet[0].metres == pytest.approx(11 * FT) and feet[1].metres == pytest.approx(10 * FT)
    assert U.parse_size_pair("11' x 10'")[0].text == "11'"


@pytest.mark.parametrize("text, m2, system", [
    ("24,50 m²", 24.5, "metric"),
    ("24.5 m2", 24.5, "metric"),
    ("24,50m²", 24.5, "metric"),
    ("39,05 M2", 39.05, "metric"),
    ("10 sqm", 10.0, "metric"),
    ("10 sq m", 10.0, "metric"),
    ("10 sq.m.", 10.0, "metric"),
    ("110 sq ft", 110 * SQFT, "imperial"),
    ("110 sq.ft.", 110 * SQFT, "imperial"),
    ("110 SQ. FT", 110 * SQFT, "imperial"),
    ("110 sqft", 110 * SQFT, "imperial"),
    ("110 sft", 110 * SQFT, "imperial"),
    ("110 ft²", 110 * SQFT, "imperial"),
    ("110 ft2", 110 * SQFT, "imperial"),
    ("110 square feet", 110 * SQFT, "imperial"),
    ("110.5 sq ft", 110.5 * SQFT, "imperial"),
    ("1,250 sq ft", 1250 * SQFT, "imperial"),   # thousands separator in square feet
    ("1,250 m²", 1.25, "metric"),               # decimal comma in square metres (as building._AREA_RE)
])
def test_parse_area(text, m2, system):
    got = U.parse_area(text)
    assert got is not None, text
    assert got[0] == pytest.approx(m2) and got[1] == system


@pytest.mark.parametrize("text", ["", "24,50", "m²", "SALON 24,50 m²", "1,250.5 m²", "11' x 10'", "110 sq"])
def test_parse_area_rejects(text):
    assert U.parse_area(text) is None


def test_area_suffix_splits_labels():
    assert U.area_suffix("SALON 24,50 m²") == ("SALON", 24.5, "metric", "24,50 m²")
    head, m2, system, text = U.area_suffix("Bed Room 110 sq ft")
    assert head == "Bed Room" and m2 == pytest.approx(110 * SQFT) and system == "imperial" and text == "110 sq ft"
    assert U.area_suffix("Bed Room") is None


def test_format_and_round_trips():
    assert U.format_length(11 * FT + 3 * INCH, "imperial") == "11' 3\""
    assert U.format_length(15.24, "imperial") == "50' 0\""
    assert U.format_length(3.4, "metric") == "3,40 m"
    assert U.format_length(3.4, "imperial") == "11' 2\""
    assert U.format_area(110 * SQFT, "imperial") == "110 sq ft"
    assert U.format_area(24.5, "metric") == "24,50 m²"
    with pytest.raises(ValueError):
        U.format_length(1.0, "cubits")
    with pytest.raises(ValueError):
        U.format_area(1.0, "cubits")
    for metres in (0.0127, 0.3048, 1.0, 2.8194, 3.3528, 4.6482, 9.144, 15.24, 23.77):
        for system in ("imperial", "metric"):
            back = U.parse_length(U.format_length(metres, system))
            assert back is not None and back.system == system
            assert abs(back.metres - metres) <= back.precision_m + 1e-9
    for m2 in (1.0, 10.2193, 24.5, 116.1288):
        for system in ("imperial", "metric"):
            got = U.parse_area(U.format_area(m2, system))
            assert got[1] == system and abs(got[0] - m2) <= (0.5 * SQFT if system == "imperial" else 0.005)


def test_majority_system():
    """Dimensions first, then size and area labels; ties and nothing explicit are metric (§1.1)."""
    assert U.majority_system(["50'", "30'"], ["3,20 x 4,10"]) == "imperial"
    assert U.majority_system(["4,30", "1,70", "50'"]) == "metric"
    assert U.majority_system(["50'", "4,30"], ["11' x 10'"]) == "imperial"     # tie on dimensions -> labels
    assert U.majority_system(["50'", "4,30"], []) == "metric"                # tie everywhere -> metric
    assert U.majority_system(["345", "120"], ["11' x 10'", "Bed Room"]) == "imperial"
    assert U.majority_system([], []) == "metric"


def test_bare_integers_can_be_re_read_in_millimetres_or_centimetres():
    """review2 ingest-7: the parser reads '15240' as metres; the scale finder may re-read a bare metric integer in
    mm or cm (``read_as``), and only that."""
    assert U.parse_length("15240").metres == 15240.0                     # the parser itself never guesses
    assert U.is_bare_integer("15240") and U.is_bare_integer(" 345 ")
    for text in ("4,50", "3.45", "345 cm", "50'", "", None, "12a"):
        assert not U.is_bare_integer(text), text
    mm = U.read_as(U.parse_length("15240"), "mm")
    assert (mm.metres, mm.system, mm.text, mm.precision_m) == pytest.approx((15.24, "metric", "15240", 0.0005))
    cm = U.read_as(U.parse_length("345"), "cm")
    assert cm.metres == pytest.approx(3.45) and cm.precision_m == pytest.approx(0.005)
    assert U.read_as(U.parse_length("12"), "m").metres == 12.0
    for bad in ("4,50", "345 cm", "50'"):
        with pytest.raises(ValueError):
            U.read_as(U.parse_length(bad), "mm")
    with pytest.raises(ValueError):
        U.read_as(U.parse_length("12"), "km")
