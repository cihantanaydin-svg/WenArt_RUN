"""Lengths and areas as printed on plans, in metric and imperial (docs/milestone7.md §1.1).

One parser for every length text the pipeline reads: dimension texts (``3,45``, ``345 cm``, ``50'``,
``14'-0"``), room-size labels (``11' x 10'``, ``3,20 x 4,10``) and area labels (``24,50 m²``,
``110 sq ft``). Everything comes back in metres (or m²) together with the unit system the text was
written in and half its printed resolution, so a check can tell a rounding difference from a real one.

Rules (the "as today" metric rules come from ``ingest.model.parse_number`` and
``building._AREA_RE``, whose behaviour stays unchanged):

- Feet marks ``'`` ``’`` ``′`` ``ft`` ``feet`` ``foot``; inch marks ``"`` ``”`` ``″`` ``''`` ``in`` ``inch``
  ``inches``; a ``-`` or a space between feet and inches (``11'-3"``, ``11' 3"``, ``11'3``); decimal feet
  (``11.5'``) and fractional inches (``3 1/2"``, ``1/2"``).
- Metric: a number with an optional ``m`` / ``cm`` / ``mm`` (``3,45``, ``3.45 m``, ``345 cm``).
- Bare numbers: a comma decimal is metres (Turkish plans write ``4,50``). A bare integer or dot decimal is
  metres unless the caller says the page is imperial (``default_system="imperial"``), then feet. Bare
  numbers never decide a page's unit system on their own (``system_of`` returns None for them).
  Metric CAD output often prints bare integers in millimetres (``15240``) or centimetres (``345``): the
  parser cannot tell, so the scale finder (``ingest.generic.scale``) re-reads them with ``read_as`` when
  the metre reading is implausible for the page, and records the unit as assumed.
- Size pairs: two lengths joined by ``x`` ``X`` ``×`` ``*``; a bare member takes the unit of the other
  one (``3,20 x 4,10 m``, ``11 x 10'``); members of different systems are rejected.
- Areas: ``m²`` ``m2`` ``sqm`` ``sq m`` and ``sq ft`` ``sft`` ``ft²`` ``square feet``; in square feet a
  comma followed by groups of three digits is a thousands separator (``1,250 sq ft``), in m² it is the
  decimal comma (``24,50 m²``).

Stdlib only: the classifier, the extractors and the report import it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

FT = 0.3048
INCH = 0.0254
SQFT = 0.09290304
SYSTEMS = ("imperial", "metric")

_METRIC_FACTOR = {"m": 1.0, "cm": 0.01, "mm": 0.001}


@dataclass(frozen=True)
class Length:
    metres: float
    system: str          # "imperial" | "metric"
    text: str            # as printed (stripped)
    precision_m: float   # half the printed resolution: 1 in -> 0.0127, 1 cm -> 0.005, "4,50" -> 0.005


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------

def _normalise_marks(text: str) -> str:
    """Typographic quote marks -> ASCII: feet ``'``, inches ``"`` (``''`` is an inch mark)."""
    out = text.strip()
    for mark in ("’", "′", "‘", "`", "´"):
        out = out.replace(mark, "'")
    for mark in ("”", "″", "“", "״"):
        out = out.replace(mark, '"')
    return out.replace("''", '"')


# --------------------------------------------------------------------------
# Lengths
# --------------------------------------------------------------------------

_NUMBER = r"\d+(?:\.\d+)?"
_FEET_MARK = r"(?:feet|foot|ft\.?|')"
_INCH_MARK = r'(?:inches|inch|in\.?|")'
# Inches: "3", "3.5", "3 1/2", "1/2".
_INCHES = (r"(?:(?P<whole>{n})(?:\s+(?P<num>\d+)\s*/\s*(?P<den>\d+))?"
           r"|(?P<fnum>\d+)\s*/\s*(?P<fden>\d+))").format(n=_NUMBER)
# 11', 11'-3", 11' 3", 11'3, 11 ft 3 in, 11.5' (the inch mark is optional after a feet part).
_FEET_INCH_RE = re.compile(rf"^(?P<ft>{_NUMBER})\s*{_FEET_MARK}\s*(?:-\s*)?(?:{_INCHES}\s*{_INCH_MARK}?)?$",
                           re.IGNORECASE)
# 3", 3 1/2", 1/2", 6 in (inches alone need their mark).
_INCH_ONLY_RE = re.compile(rf"^{_INCHES}\s*{_INCH_MARK}$", re.IGNORECASE)
# The metric rule of ingest.model.parse_number, kept exactly: digits, an optional decimal part with
# a dot or a comma, an optional m / cm / mm.
_METRIC_RE = re.compile(r"^(?P<num>\d+(?:[.,]\d+)?)\s*(?P<unit>m|cm|mm)?$", re.IGNORECASE)
_BARE_NUMBER_RE = re.compile(r"^\d+(?:[.,]\d+)?$")


def _decimals(number: str) -> int:
    for sep in (".", ","):
        if sep in number:
            return len(number.split(sep, 1)[1])
    return 0


def _inches(match: re.Match) -> Optional[tuple[float, float]]:
    """(inches, resolution in inches) of the inch part of a match; (0, None) without one; None if invalid."""
    g = match.groupdict()
    if g["whole"] is not None:
        inches, resolution = float(g["whole"]), 10.0 ** -_decimals(g["whole"])
        if g["num"] is not None:
            num, den = int(g["num"]), int(g["den"])
            if den == 0 or num >= den:
                return None
            inches, resolution = inches + num / den, 1.0 / den
        return inches, resolution
    if g["fnum"] is not None:
        num, den = int(g["fnum"]), int(g["fden"])
        if den == 0 or num >= den:
            return None
        return num / den, 1.0 / den
    return 0.0, None


def _parse_imperial(norm: str, text: str) -> Optional[Length]:
    match = _FEET_INCH_RE.match(norm)
    if match:
        inch_part = _inches(match)
        if inch_part is None or inch_part[0] >= 12.0:
            return None                               # 11'-14" is not a length
        inches, resolution_in = inch_part
        feet = match.group("ft")
        if resolution_in is not None:
            precision = resolution_in * INCH / 2.0
        else:
            precision = 10.0 ** -_decimals(feet) * FT / 2.0
        return Length(float(feet) * FT + inches * INCH, "imperial", text, precision)
    match = _INCH_ONLY_RE.match(norm)
    if match:
        inch_part = _inches(match)
        if inch_part is None:
            return None
        inches, resolution_in = inch_part
        return Length(inches * INCH, "imperial", text, resolution_in * INCH / 2.0)
    return None


def _parse_metric(norm: str, text: str, default_system: Optional[str]) -> Optional[Length]:
    match = _METRIC_RE.match(norm)
    if not match:
        return None
    number, unit = match.group("num"), match.group("unit")
    value = float(number.replace(",", "."))
    resolution = 10.0 ** -_decimals(number)
    if unit:
        factor = _METRIC_FACTOR[unit.lower()]
        return Length(value * factor, "metric", text, resolution * factor / 2.0)
    if "," not in number and default_system == "imperial":
        # A bare integer or dot decimal on an imperial page is feet.
        return Length(value * FT, "imperial", text, resolution * FT / 2.0)
    return Length(value, "metric", text, resolution / 2.0)


def parse_length(text: str, default_system: Optional[str] = None) -> Optional[Length]:
    """One printed length -> ``Length`` (metres), None when the text is not exactly one length.

    ``default_system`` ("imperial" | "metric" | None) only decides bare numbers without a decimal
    comma: feet on an imperial page, metres otherwise.
    """
    if default_system not in (None, *SYSTEMS):
        raise ValueError(f"unknown unit system {default_system!r}")
    if text is None:
        return None
    stripped = text.strip()
    if not stripped:
        return None
    norm = _normalise_marks(stripped)
    return _parse_imperial(norm, stripped) or _parse_metric(norm, stripped, default_system)


_BARE_INTEGER_RE = re.compile(r"^\d+$")


def is_bare_integer(text: Optional[str]) -> bool:
    """``15240`` / ``345``: digits only, no decimal separator and no unit (the reading the page must decide)."""
    return bool(text) and bool(_BARE_INTEGER_RE.match(text.strip()))


def read_as(length: Length, unit: str) -> Length:
    """A bare metric integer re-read in ``unit`` (``m`` / ``cm`` / ``mm``): ``15240`` read as metres -> 15.24 m as
    millimetres. Only for lengths parsed from a bare integer; anything else is refused (ValueError)."""
    if unit not in _METRIC_FACTOR:
        raise ValueError(f"unknown metric unit {unit!r}")
    if length.system != "metric" or not is_bare_integer(length.text):
        raise ValueError(f"{length.text!r} is not a bare metric integer")
    factor = _METRIC_FACTOR[unit]
    value = float(length.text.strip())
    return Length(value * factor, "metric", length.text, factor / 2.0)


# --------------------------------------------------------------------------
# Size pairs
# --------------------------------------------------------------------------

_PAIR_SPLIT_RE = re.compile(r"\s*[xX×*]\s*")


def _unit_for_partner(norm: str) -> Optional[str]:
    """The unit a bare pair member takes from its partner: ``'`` (feet, also from 10' 3"), ``"``,
    ``m``, ``cm`` or ``mm``; None when the partner is bare too."""
    match = _FEET_INCH_RE.match(norm)
    if match:
        return "'"
    if _INCH_ONLY_RE.match(norm):
        return '"'
    match = _METRIC_RE.match(norm)
    if match and match.group("unit"):
        return " " + match.group("unit").lower()
    return None


def parse_size_pair(text: str, default_system: Optional[str] = None) -> Optional[tuple[Length, Length]]:
    """``11' x 10'`` / ``3,20 x 4,10`` / ``14'-0" X 12'-0"`` -> (first, second) as printed, None otherwise."""
    if text is None:
        return None
    parts = [p.strip() for p in _PAIR_SPLIT_RE.split(text.strip())]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return None
    norms = [_normalise_marks(p) for p in parts]
    # A bare member takes the unit of the other one ("3,20 x 4,10 m", "11 x 10'").
    bare = [bool(_BARE_NUMBER_RE.match(n)) for n in norms]
    if bare[0] != bare[1]:
        i = 0 if bare[0] else 1
        unit = _unit_for_partner(norms[1 - i])
        if unit is not None:
            norms[i] = norms[i] + unit
    first = parse_length(norms[0], default_system)
    second = parse_length(norms[1], default_system)
    if first is None or second is None or first.system != second.system:
        return None
    return (Length(first.metres, first.system, parts[0], first.precision_m),
            Length(second.metres, second.system, parts[1], second.precision_m))


# --------------------------------------------------------------------------
# Areas
# --------------------------------------------------------------------------

_AREA_NUMBER = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?"
_THOUSANDS_RE = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?")
_METRIC_AREA_UNIT = r"m\s*(?:²|2|\^2)|sq\.?\s*m(?:trs?|ts?|etres?|eters?)?\.?|sqm"
_IMPERIAL_AREA_UNIT = r"sq\.?\s*f(?:ee|oo)?ts?\.?|sft|ft\s*(?:²|2|\^2)|square\s+f(?:ee|oo)t"
# An area at the end of a label ("SALON 24,50 m²", "Bed Room 110 sq ft"); building._AREA_RE is this.
AREA_SUFFIX_RE = re.compile(
    rf"\s*(?P<num>{_AREA_NUMBER})\s*(?P<unit>{_METRIC_AREA_UNIT}|{_IMPERIAL_AREA_UNIT})\s*$", re.IGNORECASE)


def parse_area(text: str) -> Optional[tuple[float, str]]:
    """``24,50 m²`` -> (24.5, "metric"); ``110 sq ft`` -> (10.219..., "imperial"); None otherwise."""
    if text is None:
        return None
    stripped = text.strip()
    match = AREA_SUFFIX_RE.match(stripped)
    if not match:
        return None
    return _area_value(match)


def _area_value(match: re.Match) -> Optional[tuple[float, str]]:
    number, unit = match.group("num"), match.group("unit")
    if re.fullmatch(_IMPERIAL_AREA_UNIT, unit, re.IGNORECASE):
        if _THOUSANDS_RE.fullmatch(number):
            return float(number.replace(",", "")) * SQFT, "imperial"   # 1,250 sq ft
        return float(number.replace(",", ".")) * SQFT, "imperial"
    if number.count(",") + number.count(".") > 1:
        return None                                   # "1,250.5 m²" is no metric spelling
    return float(number.replace(",", ".")), "metric"   # 24,50 m² (decimal comma, as building._AREA_RE)


def area_suffix(text: str) -> Optional[tuple[str, float, str, str]]:
    """Split an area off the end of a label: ``SALON 24,50 m²`` -> (``SALON``, 24.5, "metric", ``24,50 m²``)."""
    match = AREA_SUFFIX_RE.search(text)
    if not match:
        return None
    value = _area_value(match)
    if value is None:
        return None
    return text[: match.start()].strip(), value[0], value[1], text[match.start():].strip()


# --------------------------------------------------------------------------
# Unit system of a text and of a page
# --------------------------------------------------------------------------

def system_of(text: str) -> Optional[str]:
    """The unit system a length, size pair or area text states explicitly; None for bare numbers.

    ``4,50`` is metric (decimal comma), ``345`` and ``3.45`` are undecided.
    """
    if text is None:
        return None
    area = parse_area(text)
    if area is not None:
        return area[1]
    pair = parse_size_pair(text)
    if pair is not None:
        systems = {system_of(pair[0].text), system_of(pair[1].text)} - {None}
        return systems.pop() if len(systems) == 1 else None
    length = parse_length(text)
    if length is None:
        return None
    norm = _normalise_marks(text.strip())
    if length.system == "imperial":
        return "imperial"
    if _BARE_NUMBER_RE.match(norm) and "," not in norm:
        return None
    return "metric"


def majority_system(dimension_texts, size_texts=()) -> str:
    """A page's unit system: the majority of its explicit dimension texts, then of its size and area
    labels; ties and pages without explicit lengths are metric (§1.1)."""
    for texts in (dimension_texts, size_texts):
        counts = {"imperial": 0, "metric": 0}
        for text in texts:
            system = system_of(text)
            if system is not None:
                counts[system] += 1
        if counts["imperial"] != counts["metric"]:
            return "imperial" if counts["imperial"] > counts["metric"] else "metric"
    return "metric"


# --------------------------------------------------------------------------
# Formatting for reports
# --------------------------------------------------------------------------

def format_length(metres: float, system: str) -> str:
    """imperial: ``11' 3"`` (nearest inch); metric: ``3,40 m``."""
    if system == "imperial":
        total = int(round(abs(metres) / INCH))
        feet, inches = divmod(total, 12)
        sign = "-" if metres < 0 and total else ""
        return f"{sign}{feet}' {inches}\""
    if system == "metric":
        return f"{metres:.2f}".replace(".", ",") + " m"
    raise ValueError(f"unknown unit system {system!r}")


def format_area(m2: float, system: str) -> str:
    """imperial: ``110 sq ft``; metric: ``24,50 m²``."""
    if system == "imperial":
        return f"{int(round(m2 / SQFT))} sq ft"
    if system == "metric":
        return f"{m2:.2f}".replace(".", ",") + " m²"
    raise ValueError(f"unknown unit system {system!r}")
