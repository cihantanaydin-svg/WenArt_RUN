"""Named colours of Milestone 10 (wenart/style/colours.py, docs/milestone10.md §4.2).

The table is checked three ways: its shape and the colours the briefs and defaults need, the colour maths (IEC
61966-2-1 transfer function, CIELAB modifiers), and the cited values themselves against the copies of the W3C CSS
colour list and the xkcd survey that matplotlib ships (skipped where matplotlib is missing).
"""
import math
import re

import pytest

from wenart.style import colours as C

NEEDED = ("greige", "light grey", "cream", "mustard", "dark bronze", "anthracite", "sage", "terracotta", "walnut brown",
          "white", "off white", "ivory", "taupe", "beige", "sand", "grey", "dark grey", "charcoal", "black", "olive",
          "forest green", "emerald", "navy", "dusty blue", "sky blue", "teal", "rust", "ochre", "blush", "dusty pink",
          "burgundy", "plum", "chocolate", "camel", "caramel", "bronze", "brass", "copper", "oak")


def test_the_table_has_at_least_forty_documented_colours():
    assert len(C.NAMES) >= 40 and len(set(C.NAMES)) == len(C.NAMES)
    for name in NEEDED:
        assert name in C.NAMES, name
    for name, entry in C.COLOURS.items():
        assert name == name.lower() and "  " not in name and name == name.strip(), name
        assert re.fullmatch(r"#[0-9A-F]{6}", entry["srgb"]), name
        assert entry["source"] in C.SOURCES and entry["ref"], name
    assert set(C.SOURCES) == {"css4", "xkcd"}
    assert C.SOURCES["css4"]["url"].startswith("https://www.w3.org/TR/css-color-4") and C.SOURCES["xkcd"]["url"] == "https://xkcd.com/color/rgb.txt"
    assert C.SOURCES["xkcd"]["licence"] == "CC0 1.0"
    assert C.MODIFIERS == ("light", "dark", "pale", "deep", "warm", "cool", "muted")
    for alias, name in C.ALIASES.items():
        assert name in C.COLOURS, (alias, name)
        assert alias not in C.COLOURS or alias == name


@pytest.mark.parametrize("name", C.NAMES)
def test_every_value_is_the_one_in_its_cited_source(name):
    """matplotlib.colors holds the W3C CSS list (CSS4_COLORS) and the xkcd survey (XKCD_COLORS): the value of every
    entry equals the value of its ``ref`` there."""
    colors = pytest.importorskip("matplotlib.colors")
    entry = C.COLOURS[name]
    table = colors.CSS4_COLORS if entry["source"] == "css4" else {k[5:]: v for k, v in colors.XKCD_COLORS.items()}
    assert entry["ref"] in table, f"{name}: {entry['ref']!r} is not in {entry['source']}"
    assert table[entry["ref"]].upper() == entry["srgb"], name


def test_a_name_without_an_exact_source_entry_says_so():
    """Names whose own word is missing from both lists use the nearest named colour and carry a note."""
    for name, entry in C.COLOURS.items():
        same = lambda w: w.replace("gray", "grey").replace(" ", "")          # css names are one word, 'gray' is the CSS spelling
        if same(entry["ref"]) != same(name):
            assert entry.get("note"), f"{name} is sourced from {entry['ref']!r} without a note"


# --------------------------------------------------------------------------
# IEC 61966-2-1 transfer function
# --------------------------------------------------------------------------

def test_transfer_function_is_iec_61966_2_1():
    assert C.srgb_to_linear(0.0) == 0.0 and C.srgb_to_linear(1.0) == pytest.approx(1.0)
    assert C.srgb_to_linear(0.5) == pytest.approx(0.21404114, abs=1e-7)           # a well-known value
    assert C.srgb_to_linear(0.04045) == pytest.approx(0.04045 / 12.92)             # the linear segment ends here
    assert C.srgb_to_linear(0.04046) == pytest.approx(((0.04046 + 0.055) / 1.055) ** 2.4)
    assert C.linear_to_srgb(0.0031308) == pytest.approx(0.0031308 * 12.92) and C.linear_to_srgb(1.0) == pytest.approx(1.0)
    for v in (0.0, 0.01, 0.04, 0.2, 0.5, 0.73, 1.0):
        assert C.linear_to_srgb(C.srgb_to_linear(v)) == pytest.approx(v, abs=1e-9)
    assert C.hex_to_srgb("#FF8000") == pytest.approx((1.0, 128 / 255, 0.0))


def test_linear_rgb_of_names():
    assert C.linear_rgb("white") == pytest.approx((1.0, 1.0, 1.0), abs=1e-4) and C.linear_rgb("black") == (0.0, 0.0, 0.0)
    r, g, b = C.linear_rgb("mustard")
    assert (r, g, b) == pytest.approx((C.srgb_to_linear(0xCE / 255), C.srgb_to_linear(0xB3 / 255), C.srgb_to_linear(0x01 / 255)), abs=1e-5)
    for name in C.NAMES:
        rgb = C.linear_rgb(name)
        assert len(rgb) == 3 and all(0.0 <= v <= 1.0 for v in rgb), name
        assert C.srgb_hex(name) == C.COLOURS[name]["srgb"], name                  # the round trip keeps the cited value
    assert C.luminance("white") == pytest.approx(1.0, abs=1e-4) and C.luminance("black") == 0.0


# --------------------------------------------------------------------------
# CIELAB and the modifiers
# --------------------------------------------------------------------------

def test_lab_round_trip_and_known_points():
    L, a, b = C.linear_to_lab((1.0, 1.0, 1.0))
    assert L == pytest.approx(100.0, abs=0.05) and abs(a) < 0.1 and abs(b) < 0.1
    assert C.linear_to_lab((0.0, 0.0, 0.0))[0] == pytest.approx(0.0, abs=1e-6)
    for name in C.NAMES:
        rgb = C.linear_rgb(name)
        back = C.lab_to_linear(C.linear_to_lab(rgb))
        assert back == pytest.approx(rgb, abs=2e-3), name
    # mid grey: L* about 53.6 (sRGB 128)
    assert C.linear_to_lab(C.linear_rgb("grey"))[0] == pytest.approx(53.6, abs=0.3)


def lch(name, mods=()):
    L, a, b = C.linear_to_lab(C.linear_rgb(name, mods))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def base_lch(name):
    from wenart.style.colours import hex_to_srgb, srgb_to_linear, COLOURS
    L, a, b = C.linear_to_lab(tuple(srgb_to_linear(c) for c in hex_to_srgb(COLOURS[name]["srgb"])))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def test_light_and_dark_move_lightness_by_twelve():
    L0, c0, h0 = base_lch("sage")
    assert lch("sage", ("light",))[0] == pytest.approx(L0 + 12, abs=0.05)
    assert lch("sage", ("dark",))[0] == pytest.approx(L0 - 12, abs=0.05)
    assert lch("sage", ("light",))[1] == pytest.approx(c0, rel=0.02)              # chroma and hue stay
    assert lch("terracotta", ("dark", "dark"))[0] == pytest.approx(base_lch("terracotta")[0] - 24, abs=0.1)


def test_pale_deep_muted_scale_the_chroma():
    L0, c0, h0 = base_lch("dusty blue")
    assert lch("dusty blue", ("pale",))[1] == pytest.approx(c0 * 0.6, rel=0.02)
    assert lch("dusty blue", ("muted",))[1] == pytest.approx(c0 * 0.7, rel=0.02)
    assert lch("dusty blue", ("deep",))[1] == pytest.approx(c0 * 1.3, rel=0.03)
    assert lch("dusty blue", ("pale",))[0] == pytest.approx(L0, abs=0.1)


def test_warm_and_cool_turn_the_hue_by_eight_degrees_towards_yellow_and_blue():
    L0, c0, h0 = base_lch("sage")                                                  # a green: hue about 130
    assert lch("sage", ("warm",))[2] == pytest.approx(h0 - 8, abs=0.3)             # towards yellow (90)
    assert lch("sage", ("cool",))[2] == pytest.approx(h0 + 8, abs=0.3)             # towards blue (270)
    L1, c1, h1 = base_lch("dusty pink")                                            # a pink: hue about 10, away from the yellow
    assert lch("dusty pink", ("warm",))[2] == pytest.approx(h1 + 8, abs=0.5)
    L2, c2, h2 = base_lch("dusty blue")                                            # a blue: cooler is closer to 270
    assert lch("dusty blue", ("cool",))[2] == pytest.approx(h2 + 8, abs=0.5) and lch("dusty blue", ("warm",))[2] == pytest.approx(h2 - 8, abs=0.5)


def test_turn_takes_the_shorter_arc_and_stops_at_the_target():
    assert C._turn(85.0, 90.0, 8.0) == pytest.approx(90.0)          # 5 degrees away: stops at the target
    assert C._turn(100.0, 90.0, 8.0) == pytest.approx(92.0)
    assert C._turn(350.0, 90.0, 8.0) == pytest.approx(358.0)        # 100 degrees away through 0: the short way
    assert C._turn(10.0, 270.0, 8.0) == pytest.approx(2.0)          # to blue the short way is downwards through 0


def test_a_neutral_colour_is_never_a_silent_no_op():
    """"warm light grey" must differ from "light grey": a neutral gets chroma 4 at the warm / cool hue."""
    plain = C.linear_rgb("light grey")
    warm, cool = C.linear_rgb("light grey", ("warm",)), C.linear_rgb("light grey", ("cool",))
    assert warm != plain and cool != plain
    assert warm[0] > warm[2] and cool[2] > cool[0]                  # warm leans red / yellow, cool leans blue
    assert lch("light grey", ("warm",))[1] == pytest.approx(C.NEUTRAL_CHROMA, abs=0.3)
    assert lch("light grey", ("warm",))[2] == pytest.approx(80.0, abs=0.5)


def test_modifiers_apply_left_to_right_and_the_result_is_clipped_to_the_gamut():
    a = C.linear_rgb("greige", ("dark", "warm"))
    b = C.linear_rgb("warm dark greige")
    assert b != C.linear_rgb("greige") and a == pytest.approx(C.linear_rgb("dark warm greige"), abs=1e-6)
    for name in C.NAMES:
        for mod in C.MODIFIERS:
            rgb = C.linear_rgb(name, (mod,))
            assert all(0.0 <= v <= 1.0 for v in rgb), (name, mod)
    assert C.linear_rgb("white", ("light",)) == pytest.approx((1.0, 1.0, 1.0), abs=1e-3)   # L* is clamped at 100
    with pytest.raises(ValueError):
        C.linear_rgb("sage", ("shiny",))
    with pytest.raises(KeyError):
        C.linear_rgb("ultraviolet")


# --------------------------------------------------------------------------
# Words
# --------------------------------------------------------------------------

def test_parse_prefers_a_name_over_modifier_plus_name():
    assert C.parse("dark bronze") == ("dark bronze", ())            # a name
    assert C.parse("light grey") == ("light grey", ())
    assert C.parse("dark greige") == ("greige", ("dark",))
    assert C.parse("warm greige") == ("greige", ("warm",))
    assert C.parse("pale warm sage") == ("sage", ("pale", "warm"))
    assert C.parse("Sage Green") == ("sage", ())                      # alias, case
    assert C.parse("off-white") == ("off white", ()) and C.parse("gray") == ("grey", ())
    assert C.parse("natural wood") == ("oak", ())
    assert C.parse("light") is None and C.parse("warm") is None and C.parse("") is None and C.parse("greigeish") is None
    assert C.parse("light notacolour") is None
    assert C.canonical("sage green") == "sage" and C.canonical("sage") == "sage" and C.canonical("nonsense") is None
    assert C.canonical_phrase("Warm Gray") == "warm grey" and C.canonical_phrase("dark brown") == "dark brown"
    assert C.known("cool dusty blue") and not C.known("shiny sage")


def test_aliases_cover_the_m9_decor_colours_and_the_exterior_words():
    from wenart.blender import parametric as P

    for word in P.DECOR_COLOURS:                                    # the M9 decor colour list resolves to vocabulary names
        assert C.known(word), word
    assert C.canonical("sage green") == "sage" and C.canonical("natural wood") == "oak"
    assert all(w in C.colour_words() for w in ("sage green", "natural wood", "dark bronze", "greige"))
    longest_first = C.colour_words()
    assert longest_first == sorted(longest_first, key=lambda w: (-len(w), w))


def test_track_e_colour_words_resolve():
    """wenart/blender/shell.py keeps a small temporary table of colour words (``_SRGB``): every one is a name,
    an alias or modifiers plus a name here (the table is track E's stand-in until it switches to colours.py)."""
    shell = pytest.importorskip("wenart.blender.shell")
    table = getattr(shell, "_SRGB", None)
    if not table:
        pytest.skip("shell._SRGB is gone: track E switched to colours.py")
    for word in table:
        assert C.known(word), word
    for word in ("greige", "anthracite", "dark bronze", "sage"):                 # the values agree with the cited ones
        assert shell.colour_rgb(word) == pytest.approx(C.linear_rgb(word), abs=1e-3)
