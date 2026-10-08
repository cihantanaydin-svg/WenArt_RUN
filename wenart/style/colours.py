"""Milestone 10 named colours (docs/milestone10.md §4.2; track C).

What: ``COLOURS`` (53 colour names, each with a documented sRGB value and the source of that value),
``NAMES`` (the names, lower case, single spaces), ``MODIFIERS`` (light, dark, pale, deep, warm, cool, muted),
``ALIASES`` (other spellings -> a name) and the colour maths: ``linear_rgb(colour, modifiers=())`` (a name or a
phrase such as ``"warm greige"``; IEC 61966-2-1 transfer function, CIELAB modifiers), ``parse(text)``,
``canonical(text)``, ``known(text)``, ``srgb_hex(colour)``.

Why: the brief says "warm greige walls", "mustard cushions", "dark bronze window frames". A colour is never part of
a material slug (docs/milestone10.md §1.6b row 14): a profile slot holds ``{material, colour}`` and the colour is
one of these names, optionally with modifiers. Unknown colour words are listed by the style profile, never guessed.

Sources (every value is copied from one of two published lists; ``ref`` is the exact name in that list):

- ``css4``: the W3C CSS Color Module Level 4 named colours, https://www.w3.org/TR/css-color-4/#named-colors
  (a W3C specification; the values are the standard's).
- ``xkcd``: the xkcd colour survey, https://xkcd.com/color/rgb.txt (949 names chosen by about 200,000 survey
  participants; published under CC0, https://creativecommons.org/publicdomain/zero/1.0/).

Check (8 Oct 2026): the cloud session's proxy blocks w3.org and xkcd.com, so every value was compared with the
copies of both lists inside matplotlib 3.11.2 (``matplotlib.colors.CSS4_COLORS``, ``XKCD_COLORS``); ``tests/
test_colours.py`` repeats that comparison whenever matplotlib is installed. RAL Classic was left out on purpose:
RAL publishes no sRGB values and no copy of one was reachable to check against.

Where a name has no exact entry in either list the value of the nearest named colour is used and the entry says so
in ``note`` (for example ``greige`` = the survey's ``greyish``; ``anthracite`` = the survey's ``charcoal grey``).

Colour maths: sRGB -> linear with the IEC 61966-2-1 transfer function and primaries (D65); modifiers work in CIELAB
(D65 white), L* clamped to 0..100 and the result clipped to the sRGB gamut:

| modifier | effect |
|---|---|
| light / dark | L* + 12 / L* - 12 |
| pale / deep | chroma x 0.6 / x 1.3 |
| muted | chroma x 0.7 |
| warm / cool | hue turned by 8 degrees (at most) towards yellow (90 deg) / blue (270 deg) along the shorter arc; a near-neutral colour (chroma < 4) first gets chroma 4 at hue 80 deg (warm) / 260 deg (cool), so "warm light grey" is never a silent no-op |

Modifiers apply left to right. Pure Python (no numpy) so the Blender side can import it.
"""
from __future__ import annotations

import math
import re

SOURCES: dict[str, dict] = {
    "css4": {"name": "W3C CSS Color Module Level 4, named colors", "url": "https://www.w3.org/TR/css-color-4/#named-colors",
             "licence": "W3C specification"},
    "xkcd": {"name": "xkcd colour survey", "url": "https://xkcd.com/color/rgb.txt", "licence": "CC0 1.0"},
}
CHECKED = "2026-10-08"
CHECKED_AGAINST = "matplotlib 3.11.2 colors.CSS4_COLORS / colors.XKCD_COLORS (the lists' own URLs are not reachable from the cloud session)"

# name -> {srgb, source, ref[, note]}; "ref" is the name inside the source list, "srgb" its value.
COLOURS: dict[str, dict] = {
    # whites and creams
    "white":        {"srgb": "#FFFFFF", "source": "css4", "ref": "white"},
    "off white":    {"srgb": "#FDF5E6", "source": "css4", "ref": "oldlace", "note": "CSS has no 'off white'; 'oldlace' is a warm off-white"},
    "ivory":        {"srgb": "#FFFFF0", "source": "css4", "ref": "ivory"},
    "cream":        {"srgb": "#FAEBD7", "source": "css4", "ref": "antiquewhite",
                     "note": "CSS has no 'cream'; the survey's cream (#FFFFC2) is a pale yellow, too yellow for a wall"},
    # beiges and browns
    "greige":       {"srgb": "#A8A495", "source": "xkcd", "ref": "greyish",
                     "note": "the survey has no 'greige'; 'greyish' (a grey with a beige cast) is the nearest name"},
    "taupe":        {"srgb": "#B9A281", "source": "xkcd", "ref": "taupe"},
    "beige":        {"srgb": "#F5F5DC", "source": "css4", "ref": "beige"},
    "sand":         {"srgb": "#E2CA76", "source": "xkcd", "ref": "sand"},
    "oak":          {"srgb": "#D2B48C", "source": "css4", "ref": "tan", "note": "light oak wood tone; 'natural wood' is an alias"},
    "camel":        {"srgb": "#C69F59", "source": "xkcd", "ref": "camel"},
    "caramel":      {"srgb": "#AF6F09", "source": "xkcd", "ref": "caramel"},
    "coffee":       {"srgb": "#A6814C", "source": "xkcd", "ref": "coffee"},
    "walnut brown": {"srgb": "#653700", "source": "xkcd", "ref": "brown", "note": "the survey has no 'walnut'; its 'brown' is the darkest plain brown"},
    "brown":        {"srgb": "#8B4513", "source": "css4", "ref": "saddlebrown", "note": "a plain mid brown (the survey's 'brown' is walnut brown)"},
    "chocolate":    {"srgb": "#3D1C02", "source": "xkcd", "ref": "chocolate"},
    # greys and blacks
    "silver":       {"srgb": "#C0C0C0", "source": "css4", "ref": "silver"},
    "light grey":   {"srgb": "#D3D3D3", "source": "css4", "ref": "lightgray"},
    "grey":         {"srgb": "#808080", "source": "css4", "ref": "gray", "note": "mid grey"},
    "dark grey":    {"srgb": "#696969", "source": "css4", "ref": "dimgray",
                     "note": "CSS 'darkgray' (#A9A9A9) is lighter than 'gray'; 'dimgray' is the dark one"},
    "anthracite":   {"srgb": "#3C4142", "source": "xkcd", "ref": "charcoal grey",
                     "note": "no 'anthracite' in either list; the usual reference RAL 7016 could not be checked"},
    "charcoal":     {"srgb": "#343837", "source": "xkcd", "ref": "charcoal"},
    "black":        {"srgb": "#000000", "source": "css4", "ref": "black"},
    # greens
    "sage":         {"srgb": "#87AE73", "source": "xkcd", "ref": "sage"},
    "olive":        {"srgb": "#6E750E", "source": "xkcd", "ref": "olive"},
    "green":        {"srgb": "#2E8B57", "source": "css4", "ref": "seagreen", "note": "a calm mid green"},
    "forest green": {"srgb": "#06470C", "source": "xkcd", "ref": "forest green"},
    "emerald":      {"srgb": "#01A049", "source": "xkcd", "ref": "emerald"},
    # blues
    "navy":         {"srgb": "#01153E", "source": "xkcd", "ref": "navy"},
    "dusty blue":   {"srgb": "#5A86AD", "source": "xkcd", "ref": "dusty blue"},
    "sky blue":     {"srgb": "#87CEEB", "source": "css4", "ref": "skyblue"},
    "blue":         {"srgb": "#4682B4", "source": "css4", "ref": "steelblue", "note": "a muted mid blue (CSS 'blue' is #0000FF)"},
    "teal":         {"srgb": "#008080", "source": "css4", "ref": "teal"},
    "petrol":       {"srgb": "#005F6A", "source": "xkcd", "ref": "petrol"},
    # reds, pinks, purples
    "terracotta":   {"srgb": "#CA6641", "source": "xkcd", "ref": "terracotta"},
    "rust":         {"srgb": "#A83C09", "source": "xkcd", "ref": "rust"},
    "brick red":    {"srgb": "#8F1402", "source": "xkcd", "ref": "brick red"},
    "red":          {"srgb": "#B22222", "source": "css4", "ref": "firebrick", "note": "a deep red (CSS 'red' is #FF0000)"},
    "burgundy":     {"srgb": "#610023", "source": "xkcd", "ref": "burgundy"},
    "plum":         {"srgb": "#580F41", "source": "xkcd", "ref": "plum", "note": "the survey's dark plum (CSS 'plum' is a light orchid)"},
    "blush":        {"srgb": "#F29E8E", "source": "xkcd", "ref": "blush"},
    "dusty pink":   {"srgb": "#D58A94", "source": "xkcd", "ref": "dusty pink"},
    "pink":         {"srgb": "#FFC0CB", "source": "css4", "ref": "pink"},
    "lavender":     {"srgb": "#E6E6FA", "source": "css4", "ref": "lavender"},
    # yellows, oranges, metals
    "mustard":      {"srgb": "#CEB301", "source": "xkcd", "ref": "mustard"},
    "ochre":        {"srgb": "#BF9005", "source": "xkcd", "ref": "ochre"},
    "yellow":       {"srgb": "#FFD700", "source": "css4", "ref": "gold", "note": "a warm yellow (CSS 'yellow' is #FFFF00)"},
    "orange":       {"srgb": "#FF8C00", "source": "css4", "ref": "darkorange", "note": "CSS 'orange' is #FFA500; 'darkorange' reads as orange on a wall or fabric"},
    "burnt orange": {"srgb": "#C04E01", "source": "xkcd", "ref": "burnt orange"},
    "bronze":       {"srgb": "#A87900", "source": "xkcd", "ref": "bronze"},
    "dark bronze":  {"srgb": "#7F684E", "source": "xkcd", "ref": "dark taupe",
                     "note": "no 'dark bronze' in either list; the darkest low-chroma warm neutral of the survey (anodised "
                             "dark bronze is darker still: the window-frame material is metallic and reads darker)"},
    "brass":        {"srgb": "#B8860B", "source": "css4", "ref": "darkgoldenrod", "note": "no 'brass' in either list; the nearest metal-like gold"},
    "copper":       {"srgb": "#B66325", "source": "xkcd", "ref": "copper"},
    "gold":         {"srgb": "#DAA520", "source": "css4", "ref": "goldenrod", "note": "the metal; CSS 'gold' (#FFD700) is used for 'yellow'"},
}
class _Names(tuple):
    """The colour names in table order. ``x in NAMES`` is also true for an alias and for modifiers plus a name
    (``"sage green"``, ``"warm greige"``): the style profile stores colour phrases, and callers that guard
    ``linear_rgb`` with ``name in NAMES`` (``wenart/blender/exterior.py``, ``shell.py``) then work for them too.
    Iteration, ``len`` and indexing are the base names only."""

    def __contains__(self, item) -> bool:
        return isinstance(item, str) and parse(item) is not None


NAMES: tuple[str, ...] = _Names(COLOURS)
MODIFIERS: tuple[str, ...] = ("light", "dark", "pale", "deep", "warm", "cool", "muted")

# Other spellings and wordings -> a name of COLOURS. The M9 decor colour list (wenart.blender.parametric.DECOR_COLOURS)
# uses "sage green" and "natural wood": both map here.
ALIASES: dict[str, str] = {
    "sage green": "sage", "natural wood": "oak", "gray": "grey", "light gray": "light grey", "dark gray": "dark grey",
    "mid grey": "grey", "mid gray": "grey", "medium grey": "grey", "off-white": "off white", "offwhite": "off white",
    "navy blue": "navy", "olive green": "olive", "dusty rose": "dusty pink", "mustard yellow": "mustard",
    "terra cotta": "terracotta", "charcoal grey": "charcoal", "charcoal gray": "charcoal", "anthracite grey": "anthracite",
    "anthracite gray": "anthracite", "walnut": "walnut brown", "forest": "forest green", "sky": "sky blue",
    "light brown": "coffee", "bone": "off white", "eggshell": "off white",
}

_SPACES = re.compile(r"[\s_]+")


# --------------------------------------------------------------------------
# sRGB <-> linear <-> CIELAB (IEC 61966-2-1; D65)
# --------------------------------------------------------------------------

def srgb_to_linear(c: float) -> float:
    """One sRGB channel (0..1) -> linear light (IEC 61966-2-1)."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    """One linear channel (0..1) -> sRGB (IEC 61966-2-1)."""
    c = min(1.0, max(0.0, c))
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_srgb(value: str) -> tuple[float, float, float]:
    """``"#RRGGBB"`` -> sRGB floats 0..1."""
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


# Linear sRGB <-> CIE XYZ (D65), the matrices of IEC 61966-2-1.
_RGB_TO_XYZ = ((0.4124, 0.3576, 0.1805), (0.2126, 0.7152, 0.0722), (0.0193, 0.1192, 0.9505))
_XYZ_TO_RGB = ((3.2406, -1.5372, -0.4986), (-0.9689, 1.8758, 0.0415), (0.0557, -0.2040, 1.0570))
_WHITE = (0.9505, 1.0, 1.0890)           # D65 white of the matrix above
_EPS, _KAPPA = 216 / 24389, 24389 / 27   # CIE constants


def _mul(m, v):
    return tuple(sum(m[r][c] * v[c] for c in range(3)) for r in range(3))


def linear_to_lab(rgb) -> tuple[float, float, float]:
    """Linear sRGB -> CIELAB ``(L*, a*, b*)`` (D65)."""
    xyz = _mul(_RGB_TO_XYZ, rgb)

    def f(t: float) -> float:
        return t ** (1 / 3) if t > _EPS else (_KAPPA * t + 16) / 116

    fx, fy, fz = (f(xyz[i] / _WHITE[i]) for i in range(3))
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def lab_to_linear(lab) -> tuple[float, float, float]:
    """CIELAB -> linear sRGB, clipped to the gamut (0..1)."""
    L, a, b = lab
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200

    def inv(t: float) -> float:
        return t ** 3 if t ** 3 > _EPS else (116 * t - 16) / _KAPPA

    xyz = (inv(fx) * _WHITE[0], (inv(fy) if L > _KAPPA * _EPS else L / _KAPPA) * _WHITE[1], inv(fz) * _WHITE[2])
    return tuple(min(1.0, max(0.0, c)) for c in _mul(_XYZ_TO_RGB, xyz))  # type: ignore[return-value]


# --------------------------------------------------------------------------
# Modifiers
# --------------------------------------------------------------------------

LIGHTNESS_STEP = 12.0
CHROMA_FACTORS = {"pale": 0.6, "deep": 1.3, "muted": 0.7}
HUE_STEP_DEG = 8.0
HUE_YELLOW, HUE_BLUE = 90.0, 270.0
NEUTRAL_CHROMA = 4.0
NEUTRAL_HUES = {"warm": 80.0, "cool": 260.0}


def _turn(hue: float, target: float, step: float) -> float:
    """``hue`` turned by at most ``step`` degrees towards ``target`` along the shorter arc."""
    diff = (target - hue + 180.0) % 360.0 - 180.0
    if abs(diff + 180.0) < 1e-9:      # exactly opposite: take the increasing direction
        diff = 180.0
    return (hue + math.copysign(min(abs(diff), step), diff)) % 360.0


def apply_modifier(lab, modifier: str) -> tuple[float, float, float]:
    """One modifier applied to a CIELAB colour (see the module docstring)."""
    if modifier not in MODIFIERS:
        raise ValueError(f"unknown colour modifier {modifier!r}; known: {', '.join(MODIFIERS)}")
    L, a, b = lab
    if modifier == "light":
        return min(100.0, L + LIGHTNESS_STEP), a, b
    if modifier == "dark":
        return max(0.0, L - LIGHTNESS_STEP), a, b
    chroma, hue = math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360.0
    if modifier in CHROMA_FACTORS:
        chroma *= CHROMA_FACTORS[modifier]
    else:                                              # warm / cool
        if chroma < NEUTRAL_CHROMA:
            chroma, hue = NEUTRAL_CHROMA, NEUTRAL_HUES[modifier]
        else:
            hue = _turn(hue, HUE_YELLOW if modifier == "warm" else HUE_BLUE, HUE_STEP_DEG)
    return L, chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))


# --------------------------------------------------------------------------
# Words -> colours
# --------------------------------------------------------------------------

def _norm(text) -> str:
    return _SPACES.sub(" ", str(text or "").strip().lower()).strip()


def canonical(text) -> str | None:
    """The name of ``COLOURS`` that a word or phrase without modifiers stands for (alias, spelling), else None."""
    word = _norm(text)
    for cand in (word, word.replace("-", " ")):
        if cand in COLOURS:
            return cand
        alias = ALIASES.get(cand)
        if alias in COLOURS:
            return alias
    return None


def parse(text) -> tuple[str, tuple[str, ...]] | None:
    """``(name, modifiers)`` of a colour phrase such as ``"warm greige"`` or ``"dark bronze"``; None when it is not
    exactly modifiers followed by one colour name or alias. A name wins over modifier + name (``dark bronze`` is a
    name; ``dark greige`` is ``dark`` + ``greige``)."""
    words = [w for w in _SPACES.split(str(text or "").strip().lower().replace("-", " ")) if w]
    if not words:
        return None
    mods: list[str] = []
    while words:
        name = canonical(" ".join(words))
        if name:
            return name, tuple(mods)
        if words[0] in MODIFIERS and len(words) > 1:
            mods.append(words.pop(0))
            continue
        return None
    return None


def canonical_phrase(text) -> str | None:
    """The colour phrase with its alias resolved and its modifiers kept (``"Sage Green"`` -> ``"sage"``, ``"warm
    gray"`` -> ``"warm grey"``), None when ``text`` is no colour phrase. This is the form the style profile stores."""
    parsed = parse(text)
    if parsed is None:
        return None
    name, mods = parsed
    return " ".join((*mods, name))


def known(text) -> bool:
    """True when ``text`` is a colour name, an alias, or modifiers followed by one."""
    return parse(text) is not None


def srgb_hex(colour, modifiers=()) -> str:
    """``"#RRGGBB"`` of a colour phrase (modifiers applied)."""
    rgb = linear_rgb(colour, modifiers)
    return "#" + "".join(f"{round(linear_to_srgb(c) * 255):02X}" for c in rgb)


def linear_rgb(colour, modifiers=()) -> tuple[float, float, float]:
    """Linear sRGB (0..1) of a colour: a name, an alias or a phrase with modifiers (``"warm greige"``), plus
    ``modifiers`` applied after the phrase's own. KeyError for an unknown colour, ValueError for an unknown modifier."""
    parsed = parse(colour)
    if parsed is None:
        raise KeyError(f"unknown colour {colour!r}")
    name, mods = parsed
    rgb = tuple(srgb_to_linear(c) for c in hex_to_srgb(COLOURS[name]["srgb"]))
    chain = list(mods) + [str(m).lower() for m in modifiers]
    if chain:
        lab = linear_to_lab(rgb)
        for m in chain:
            lab = apply_modifier(lab, m)
        rgb = lab_to_linear(lab)
    return tuple(round(float(c), 5) for c in rgb)  # type: ignore[return-value]


def colour_words() -> list[str]:
    """Every word a brief may use for a colour: names and aliases, longest first (scan order)."""
    return sorted(set(NAMES) | set(ALIASES), key=lambda w: (-len(w), w))


def luminance(colour, modifiers=()) -> float:
    """Relative luminance (CIE Y, 0..1) of a colour phrase."""
    r, g, b = linear_rgb(colour, modifiers)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
