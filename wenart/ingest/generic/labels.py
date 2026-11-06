"""Room-name labels of a plan page: vocabulary, label blocks and size-label checks (docs/milestone7.md §2.7.2-3).

A room label on a real plan is often more than one text run: ``Bath+`` / ``Toilet`` / ``7' x 5'`` are three
runs stacked under each other, and the last one is the room's printed size, not its name. This module
turns the text runs of one page into ``LabelBlock``s:

- **Name runs** are runs with a room-name keyword (``building._ROOM_TYPE_KEYWORDS``: Turkish word starts,
  English whole words) or an exterior keyword (``EXTERIOR_KEYWORDS``: parking, garden, ...). Long runs
  (more than ``MAX_NAME_WORDS`` words) are notes, not names. Runs that parse as one length are dimension
  texts and never join a block.
- **Stacking**: a run directly below another (same rotation, vertical gap ≤ ``STACK_GAP`` × line height,
  horizontal overlap ≥ ``STACK_OVERLAP`` of the narrower run) continues it; a run ending in ``+``, ``&``
  or ``-`` also takes the next run below or to its right a little further away (``CONNECTOR_GAP``). A block
  is its name lines followed by at most one size line (``11' x 10'``) and one area line (``110 sq ft``);
  a name line after them starts the next block. Runs without a keyword join a block only as part of a
  stack that has a keyword line or a size/area line (``GUEST`` / ``BED ROOM``, ``GYM`` / ``12' x 10'``);
  alone they are not labels (``UP``, ``N``, door tags).
- **Anchor** = centre of the name lines' box (the room the block names is the face containing it).

``check_label_size`` compares a block's printed size with the clear size of its face (minimum-area
rectangle, both orientations): ``ok`` within max(5 %, 0.15 m) per side, ``conflict`` beyond (the room is
``unverified`` beyond 10 %), ``unchecked`` for a face that is not a rectangle (area / rectangle < 0.9),
whose printed area w × l is then compared with the face area at 8 %.

Coordinates: whatever the runs carry; ``core`` passes runs in page metres (y up).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B
from wenart import units
from wenart.ingest.generic.model import TextRun

MAX_NAME_WORDS = 5            # a run with more words is a note, not a room name
STACK_GAP = 0.8               # stacked lines: vertical gap <= this x line height
STACK_OVERLAP = 0.30          # ... and horizontal overlap >= this x the narrower run
STACK_MIN_GAP = -0.5          # boxes may overlap a little (negative gap, x line height)
CONNECTOR_GAP = 1.5           # a run ending in + & - takes the next line within this x line height
CONNECTOR_SIDE_GAP = 1.0      # ... or the next run to its right within this x line height
CONNECTORS = ("+", "&", "-")
ROTATION_TOL_DEG = 1.0

# Site words (§2.7.2): a face or label named only by these is no room but a site area.
EXTERIOR_KEYWORDS = ("parking", "car porch", "porch", "garden", "lawn", "sit out", "setback", "otla", "court",
                     "courtyard", "drive", "driveway", "gate")
_EXTERIOR_PATTERNS = [B.english_keyword_re(k) for k in EXTERIOR_KEYWORDS]

# Milestone 10 (building.schema site.areas[].kind): what a site label names, on fold_ascii text. Turkish, English,
# German and French words; the first kind that matches wins (a terrace before paving, parking before garden).
AREA_KIND_WORDS = (
    ("pool", r"\b(havuz|pool|schwimmbad|piscine)\b"),
    ("terrace", r"\b(teras|terrace|sit out|otla|terrasse|guneslenme|sun deck|sundeck)\b"),
    ("parking", r"\b(otopark|park yeri|garaj|parking|car porch|carport|garage|stellplatz|parkplatz)\b"),
    ("paving", r"\b(kaldirim|avlu|patio|paving|drive|driveway|court|courtyard|pflaster|hof|allee|pave|cour)\b"),
    ("garden", r"\b(bahce|cim|yesil alan|garden|lawn|setback|garten|rasen|jardin|pelouse)\b"),
)
_AREA_KIND_RE = [(kind, re.compile(pattern)) for kind, pattern in AREA_KIND_WORDS]


def area_kind(label: str) -> Optional[str]:
    """What a site label names: ``parking``, ``garden``, ``paving``, ``pool`` or ``terrace`` (None = no site word)."""
    folded = " ".join(B.fold_ascii(label or "").lower().split())
    for kind, pattern in _AREA_KIND_RE:
        if pattern.search(folded):
            return kind
    return None

# label_size check (§2.7.3)
SIZE_TOL_REL = 0.05
SIZE_TOL_ABS_M = 0.15
SIZE_UNVERIFIED_REL = 0.10
RECTANGULAR_MIN = 0.9
AREA_TOL_REL = 0.08
AREA_UNVERIFIED_REL = (1.0 + SIZE_UNVERIFIED_REL) ** 2 - 1.0   # the 10 % side rule in area terms (21 %)

_EVIDENCE_METHOD = {"vector": "vector", "ocr": "ocr", "ai": "ai"}


@dataclass
class LabelBlock:
    """One room (or site area) label: its name lines and the printed size/area under them."""
    name: str                                  # name lines joined as printed: "Bath+ Toilet"
    name_runs: list[TextRun]
    size_text: Optional[str]                   # "7' x 5'"
    area_text: Optional[str]                   # "35 sq ft", "24,50 m²"
    anchor: tuple[float, float]                # centre of the name lines' box
    room_type: str                             # building.room_type_for(name) ("other" for site areas)
    exterior: bool                             # named only by exterior keywords (Parking, Garden, ...)
    evidence: list[dict]                       # one evidence dict per run of the block
    size: Optional[tuple[units.Length, units.Length]] = None   # parsed size_text, printed order
    area_m2: Optional[float] = None            # parsed area_text in m²
    box: Optional[tuple[float, float, float, float]] = None    # all runs of the block
    runs: list[TextRun] = field(default_factory=list)          # name, size and area runs, top to bottom


# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

def _exterior_hit(name: str) -> bool:
    folded = B.fold_ascii(name)
    return any(p.search(folded) for p in _EXTERIOR_PATTERNS)


def room_type_for(name: str, face_area_m2: Optional[float] = None,
                  face_aspect: Optional[float] = None) -> tuple[str, bool]:
    """``(room_type, exterior)`` of a label name (English and Turkish).

    ``exterior`` is True when the name has an exterior keyword and no room keyword (``Parking``,
    ``Car Porch``); its room type is then ``other`` and the caller puts it into ``site.areas``.
    ``Terrace Garden`` is a balcony (a room keyword wins). The face size decides ``hall`` alone
    (``building.room_type_for``).
    """
    turkish, english = B.room_keyword_hits(name)
    if not turkish and not english and _exterior_hit(name):
        return "other", True
    return B.room_type_for(name, face_area_m2, face_aspect), False


def _strip_suffixes(text: str) -> tuple[str, Optional[str], Optional[str]]:
    """(name, size, area) of one line: ``SALON 24,50 m²`` -> (``SALON``, None, ``24,50 m²``);
    ``BED ROOM 11'x10'`` -> (``BED ROOM``, ``11'x10'``, None)."""
    head, size_text, area_text = text.strip(), None, None
    split = units.area_suffix(head)
    if split is not None and split[0]:
        head, area_text = split[0], split[3]
    words = head.split(" ")
    for k in range(1, len(words)):
        tail = " ".join(words[k:])
        if units.parse_size_pair(tail) is not None and re.search(r"[^\W\d_]", " ".join(words[:k])):
            head, size_text = " ".join(words[:k]).strip(), tail.strip()
            break
    return head, size_text, area_text


_SPACED_RE = re.compile(r"^(?:[^\W\d_] ){2,}[^\W\d_]$")
_SCALE_WORDS_RE = re.compile(r"\b(OLCEK|SCALE|MASSTAB|ECHELLE)\b")


def collapse_spaced(text: str) -> str:
    """real10 (1 Nov 2026): a name written with spaced letters (``s a l o n``) is that word (``salon``)."""
    t = " ".join(text.split())
    return t.replace(" ", "") if _SPACED_RE.match(t) else text


def is_drawing_title(text: str) -> bool:
    """A drawing title or scale note (``TERAS KAT PLANI``, ``A - A KESİTİ``, ``ÖLÇEK : 1/50``): never a room label
    (real10's roof terrace title read as a terrace)."""
    from wenart.sheets import titles as T

    folded = B.fold_ascii(text).upper()
    return T.class_of(text) is not None or bool(_SCALE_WORDS_RE.search(folded))


# 2 Nov 2026 (real03: "1+1 A1 Daire Tipi" / "Net Alan =" / "Brüt Alan =" beside each flat became 16 room labels
# outside the building): the area-summary notes and flat names of a plan are no room labels. Words on fold_ascii
# upper text; Turkish, English, German, French.
_FLAT_WORDS = {"DAIRE", "DAIRESI", "FLAT", "APARTMENT", "APT", "UNIT", "WOHNUNG", "APPARTEMENT", "LOGEMENT", "BHK",
               "KONUT", "BAGIMSIZ", "BOLUM", "BLOK", "BLOCK"}
_TYPE_WORDS = {"TIP", "TIPI", "TYPE", "TYP", "NO", "NR", "NUMARA", "NUMBER"}
_SUMMARY_WORDS = {"NET", "BRUT", "GROSS", "NETTO", "BRUTTO", "TOPLAM", "TOTAL", "KULLANIM", "INSAAT", "EMSAL",
                  "CARPET", "BUILT", "UP", "BUILTUP", "SALEABLE", "SUPER", "PLINTH", "KAT", "PLOT", "SITE", "ARSA",
                  "PARSEL", "OTURUM", "TABAN", "TAKS", "KAKS", "NFL", "BGF", "WFL", "NF", "GFA", "NIA", "GIA",
                  "HABITABLE", "UTILE", "SHON", "SHAB", "SDP"}
_AREA_NOUNS = {"ALAN", "ALANI", "AREA", "AREAS", "FLACHE", "WOHNFLACHE", "NUTZFLACHE", "SURFACE", "SUPERFICIE", "M2"}
_ROOM_COUNT_RE = re.compile(r"\d\s*\+\s*\d")              # "1+1", "2+1": a Turkish flat type


def is_annotation(text: str) -> bool:
    """An area-summary note or a flat name, never a room label: no room keyword and either a formula (``Net Alan =``),
    a flat type (``1+1``, ``3 BHK``), or only flat, type, summary and area words with single letters and numbers
    (``A1 Daire Tipi``, ``Brüt Alan``, ``Kullanım Alanı``, ``Carpet Area``, ``Flat 3``, ``Wohnfläche``). A site area
    like ``Oyun Alanı`` (play area) keeps its word and stays a label."""
    text = collapse_spaced(text or "")
    turkish, english = B.room_keyword_hits(_strip_suffixes(text)[0])
    if turkish or english:
        return False
    folded = B.fold_ascii(text).upper()
    if "=" in folded or _ROOM_COUNT_RE.search(folded):
        return True
    words = re.findall(r"[A-Z]+", folded)
    long_words = [w for w in words if len(w) > 1]
    vocab = _FLAT_WORDS | _TYPE_WORDS | _SUMMARY_WORDS | _AREA_NOUNS
    if not long_words or any(w not in vocab for w in long_words):
        return False
    flat = any(w in _FLAT_WORDS for w in long_words)
    summary = any(w in _AREA_NOUNS for w in long_words) and any(w in _SUMMARY_WORDS for w in long_words)
    return flat or summary or all(w in _AREA_NOUNS for w in long_words)


    text = collapse_spaced(text or "").strip()
    if not text or re.search(r"\d", text) or B.generic_room_label(text):
        return False
    turkish, english = B.room_keyword_hits(text)
    return not turkish and not english and T.level_of(f"{text} KAT") is not None


# 6 Nov 2026 (Milestone 14 reader target 3; real11: 'Bına Taban Hattı Yatak Odası' and 'Tesisat Duvarı H: 1.20 Cm' read
# as room names): the notation phrases of a plan, never part of a room's name. One table for the reader (a label line
# loses them before naming, ``split_notation``) and the checker (RC14 ``label_vocabulary`` in
# ``wenart.reading_check.sense`` imports it). (pattern on ASCII-folded upper text, what it is)
NOTATION_PHRASES = (
    (r"\b(?:BINA\s+)?TABAN\s+HATTI\b", "the building's footprint line"),
    (r"\bTESISAT\s+DUVARI\b", "a services wall note"),
    (r"\bSACAK(?:\s+IZDUSUMU)?\b", "the eaves (projection line)"),
    (r"\bIZDUSUM\w*\b", "a projection line of the floor above"),
    (r"\bKOTU?\b", "a level mark"),
    (r"\bAKS(?:I|LARI)?\b", "an axis"),
    (r"\bSUBASMAN\b", "the plinth line"),
    (r"\bDILATASYON\b", "an expansion joint"),
    (r"\bPARAPET\b", "a parapet"),
    (r"\bH\s*[:=]\s*\d", "a height note"),
    (r"(?:^|\s)[+\-±]\s*\d+[.,]\d{2}\b", "a level value"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:CM|MM|M2|M²|M)(?![A-Z0-9])", "a number with a unit"),
)
NOTATION_RE = [(re.compile(p), what) for p, what in NOTATION_PHRASES]


# 6 Nov 2026 (moved from ``wenart.reading_check.sense``, RC14; reader target 5): what is built, by room type: a
# reading outside these ranges has almost always closed the wrong face or named it from the wrong text. The reader
# (``wenart.ingest.rooms``: a small room's label never names a face several times its type's largest area) and the
# checker (RC14 ``room_type_area``, ``label_names_larger_face``) share them.
AREA_RANGES = {
    "lift": (1.0, 8.0, "a lift shaft holds a car of 4 to 21 persons: from about 1.0 x 1.0 m to 2.6 x 3.0 m"),
    "shaft": (0.1, 8.0, "an installation shaft is from a 30 x 40 cm riser to a few m2; a larger face named shaft has "
                        "taken in a room beside it"),
    "light_well": (0.5, 30.0, "a light or air well (ışıklık) is from a 0.7 x 0.7 m air shaft to about 5 x 6 m"),
    "wc": (0.8, 6.0, "a WC with a basin is from 0.8 x 1.0 m to about 2 x 3 m"),
    "bathroom": (1.0, 15.0, "a bathroom holds a shower or a bath, a basin and a WC: from a 1.0 x 1.1 m en-suite to "
                            "about 15 m2"),
    "shower": (0.8, 5.0, "a shower room is a 0.8 x 1.0 m cubicle to about 2 x 2.5 m"),
    "closet": (0.3, 12.0, "a closet, pantry or dressing room is from a 0.5 x 0.6 m cupboard to about 3 x 4 m"),
    "storage": (0.3, 60.0, "a storage room (depo) is a cupboard in a flat to a store room of a shop or a basement"),
    "fire_lobby": (2.0, 40.0, "a fire or safety lobby in front of a stair or a lift is about 2 to 40 m2"),
    "stair": (2.0, 40.0, "a stair core (one or two flights with their landings) is about 2 to 40 m2"),
    "kitchen": (3.0, 40.0, "a kitchen is a 1.8 x 1.8 m kitchenette to about 5 x 8 m"),
    "bedroom": (6.0, 40.0, "a bedroom holds a bed with access around it: about 6 to 40 m2"),
    "living": (8.0, 120.0, "a living room is about 8 to 120 m2"),
    "hall": (1.0, 60.0, "an entrance, a corridor or a floor hall is about 1 to 60 m2"),
    "garage": (12.0, 100.0, "a private garage holds one to four cars: about 12 to 100 m2"),
    "car_park": (12.0, 5000.0, "a car park (otopark) holds from one car to a whole basement of cars"),
    "technical": (1.0, 40.0, "a boiler, pump, electrical or lift machine room is about 1 to 40 m2"),
}
# The words that refine the schema's coarse room types (ASCII-folded lower case, ``B.fold_ascii``), the first match
# wins. Turkish words match at the start of a word (inflected forms count), the English ones as whole words.
SENSE_WORDS = (
    ("technical", r"(?<![a-z])(?:asansor\s*mak|makin?a?e?\s*dair|machine\s*room|motor\s*room|su\s*depo|water\s*tank"
                  r"|hidrofor|hidrafor|kazan|kalorifer|kat\s*kal|jenerator|trafo|elektrik\s*oda|teknik)"),
    ("light_well", r"(?<![a-z])(?:isiklik|aydinlik|aydinlatma|light\s*well|lightwell)"),
    ("lift", r"(?<![a-z])asansor|(?<![a-z])(?:lift|elevator)s?(?![a-z])"),
    ("fire_lobby", r"(?<![a-z])(?:yangin|guvenlik|duman)\s*(?:kacis\s*)?hol|(?<![a-z])(?:fire|smoke|safety)\s*lobby"),
    ("shelter", r"(?<![a-z])(?:siginak|shelter)"),
    ("car_park", r"(?<![a-z])(?:otopark|parking|car\s*park)"),
    ("shaft", r"(?<![a-z])(?:saft|saht|soh|baca|shaft|riser)"),
    # 6 Nov 2026 (calibration): a KİLER is a pantry in a flat and a cellar store in a basement (synthetic-03's 14 m2
    # ones): it is judged as a storage room, not as a closet
    ("closet", r"(?<![a-z])(?:vestiyer|gardirop|giyinme|soyunma|closet|wardrobe|dressing)"),
    ("shower", r"(?<![a-z])(?:dus|shower)(?![a-z])"),
)
SENSE_RE = [(t, re.compile(p)) for t, p in SENSE_WORDS]
_BATH_RE = re.compile(r"(?<![a-z])(?:banyo|bath)")
# 6 Nov 2026 (reader target 5; real20 L0: 'Asansör' over a 16.2 m2 face holding the stair, real11 L-1 to L6: an
# 'Asansor' face of 14.9 m2 that is the stair hall): the small room types whose label names only its own sub-space when
# the face is ``SUB_SPACE_FACTOR`` times the type's largest area (``AREA_RANGES``) and holds a stair or another label
SUB_SPACE_TYPES = ("lift", "shaft", "wc", "closet")
SUB_SPACE_FACTOR = 1.5


def sense_word(text: str) -> Optional[str]:
    """The first ``SENSE_WORDS`` type a text's words say (``asansör`` -> lift, ``vestiyer`` -> closet), or None."""
    folded = " ".join(B.fold_ascii(str(text or "")).split())
    return next((t for t, rx in SENSE_RE if rx.search(folded)), None)


def sub_space_type(name: str, room_type: Optional[str]) -> Optional[str]:
    """The small type (``SUB_SPACE_TYPES``) a room name with its schema type says: a lift, an installation shaft, a WC
    (not a bath) or a closet; None for any other name (a machine room, a light well, a pantry ...)."""
    word = sense_word(name)
    if word == "lift":
        return "lift"
    if room_type == "shaft":
        return None if word in ("light_well", "technical") else "shaft"
    if room_type == "wc":
        return None if _BATH_RE.search(" ".join(B.fold_ascii(str(name or "")).split())) else "wc"
    return "closet" if word == "closet" else None


def notation_phrases(text: str) -> list[str]:
    """What notation a text holds (pure): ``[what]`` of the ``NOTATION_PHRASES`` found in it."""
    folded = " ".join(B.fold_ascii(str(text or "")).split()).upper()
    return [what for rx, what in NOTATION_RE if rx.search(folded)]


def split_notation(text: str) -> tuple[str, list[str]]:
    """``(rest, [what])`` (pure): the text without the words a notation phrase covers (``TESİSAT DUVARI H: 1.20 Cm``
    -> ``''``; ``BİNA TABAN HATTI YATAK ODASI`` -> ``YATAK ODASI``) and what was taken out. Words are matched folded
    (``B.fold_ascii``, upper case) and dropped whole, so the rest keeps the drawing's own spelling."""
    words = str(text or "").split()
    if not words:
        return "", []
    spans, pos, folded_words = [], 0, []
    for w in words:
        f = B.fold_ascii(w).upper() or w
        spans.append((pos, pos + len(f)))
        folded_words.append(f)
        pos += len(f) + 1
    folded = " ".join(folded_words)
    cut, found = set(), []
    for rx, what in NOTATION_RE:
        for m in rx.finditer(folded):
            a, b = m.span()
            hit = {k for k, (s, e) in enumerate(spans) if s < b and e > a and folded[a:b].strip()}
            if hit:
                cut |= hit
                found.append(what)
    if not cut:
        return text, []
    rest = " ".join(w for k, w in enumerate(words) if k not in cut).strip(" ,;:-/")
    return rest, list(dict.fromkeys(found))


def _is_name_text(text: str, indoor_only: bool) -> bool:
    text = collapse_spaced(text)
    head, _, _ = _strip_suffixes(text)
    head = split_notation(head)[0]           # 6 Nov 2026 (target 3): TESİSAT DUVARI names no room ("tesisat" alone does)
    if not head or len(head.split()) > MAX_NAME_WORDS:
        return False
    if units.parse_length(head) is not None or units.parse_size_pair(head) is not None:
        return False
    turkish, english = B.room_keyword_hits(head)
    if turkish or english:
        return True
    return not indoor_only and _exterior_hit(head)


def room_name_runs(texts: list[TextRun]) -> list[TextRun]:
    """The runs that name a room (English or Turkish keyword, at most ``MAX_NAME_WORDS`` words; an area or
    size on the same line is allowed). Exterior names (Parking, Garden) are not counted: a page needs
    room names to be a floor plan (§2.1)."""
    return [t for t in texts if t.text and _is_name_text(t.text, indoor_only=True)]


def page_is_turkish(texts: list[TextRun]) -> bool:
    """Whether a page is labelled in Turkish: most of its room-name runs are Turkish
    (``building.is_turkish_label``); without room names, any Turkish letter on the page. Decides the
    casing of its labels (``normalise_room_label(..., turkish=...)``) and the unlabelled placeholder (§1.3)."""
    runs = room_name_runs(texts)
    if runs:
        turkish = sum(1 for r in runs if B.is_turkish_label(_strip_suffixes(r.text)[0]))
        return turkish * 2 > len(runs)
    return any(B.has_turkish_letters(t.text or "") for t in texts)


# --------------------------------------------------------------------------
# Label blocks
# --------------------------------------------------------------------------

@dataclass
class _Line:
    run: TextRun
    kind: str                 # name | other | size | area | skip (see _classify)
    head: str                 # name part (name/other lines) without an inline size or area
    size_text: Optional[str] = None
    area_text: Optional[str] = None
    frame_box: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)   # box in the text's own frame


def _frame_box(run: TextRun) -> tuple[float, float, float, float]:
    """The run's box rotated into its own reading frame (baseline along +x)."""
    a = math.radians(-run.rotation_deg)
    c, s = math.cos(a), math.sin(a)
    x0, y0, x1, y1 = run.box
    pts = [(x * c - y * s, x * s + y * c) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _line_height(run: TextRun) -> float:
    if run.height and run.height > 0:
        return run.height
    fb = _frame_box(run)
    return max(fb[3] - fb[1], 1e-9)


# 2 Nov 2026: an area line written with its symbol, ``A = 24,50 m²``, ``F: 24,50 m²``, ``NF = 18,20 m²``, ``Alan:
# 12 m²`` (Turkish, German and French plans): the prefix is a code of at most 3 letters or an area word, then ``=``
# or ``:``. It was a skipped line, so the room's printed area was lost.
AREA_PREFIX_RE = re.compile(r"^(?:[A-Z]{1,3}|NET|BRUT|ALAN|ALANI|AREA|FLACHE|SURFACE|NET ALAN|NETTO)\s*[=:]$")


def _classify(run: TextRun, default_system: str) -> _Line:
    """Kind of one run: ``area``, ``size``, ``name`` (keyword), ``other`` (words that may continue a
    name), or ``skip`` (a single length, a bare number, a long note: never part of a block)."""
    text = collapse_spaced(run.text.strip())
    box = _frame_box(run)
    if is_drawing_title(text):
        return _Line(run, "skip", "", frame_box=box)       # real10: "TERAS KAT PLANI ÖLÇEK : 1/50" is no room
    if units.parse_area(text) is not None:
        return _Line(run, "area", "", area_text=text, frame_box=box)
    if units.parse_size_pair(text, default_system) is not None:
        return _Line(run, "size", "", size_text=text, frame_box=box)
    if units.parse_length(text, default_system) is not None:
        return _Line(run, "skip", "", frame_box=box)
    head, size_text, area_text = _strip_suffixes(text)
    if area_text and AREA_PREFIX_RE.match(B.fold_ascii(head).upper()):
        return _Line(run, "area", "", area_text=area_text, frame_box=box)    # "A = 24,50 m²", "NF: 18,2 m²"
    rest, notation = split_notation(head)
    if notation:
        # 6 Nov 2026 (target 3, real11): a notation phrase is split off the line before naming; a line that is only
        # notation (BİNA TABAN HATTI, TESİSAT DUVARI H: 1.20 Cm) never joins a label block
        if not re.search(r"[^\W\d_]{2,}", rest):
            return _Line(run, "skip", "", frame_box=box)
        head = rest
        text = " ".join(x for x in (rest, size_text, area_text) if x)
    if is_annotation(text):
        return _Line(run, "skip", "", frame_box=box)       # real03: "Net Alan =", "1+1 A1 Daire Tipi" are no rooms
    if _is_name_text(text, indoor_only=False):
        kind = "name"
    elif re.search(r"[^\W\d_]{2,}", head) and len(head.split()) <= MAX_NAME_WORDS:
        kind = "other"                                # a word of 2+ letters (door tags like "D1" are skipped)
    else:
        kind = "skip"
    return _Line(run, kind, head, size_text=size_text, area_text=area_text, frame_box=box)


def _same_rotation(a: TextRun, b: TextRun) -> bool:
    diff = abs((a.rotation_deg - b.rotation_deg + 180.0) % 360.0 - 180.0)
    return diff <= ROTATION_TOL_DEG


def _below(upper: _Line, lower: _Line, max_gap: float, min_overlap: float) -> Optional[float]:
    """Gap (in line heights) when ``lower`` sits under ``upper`` in their reading frame, else None."""
    if not _same_rotation(upper.run, lower.run):
        return None
    ub, lb = upper.frame_box, lower.frame_box
    h = max(_line_height(upper.run), _line_height(lower.run))
    gap = (ub[1] - lb[3]) / h
    if gap < STACK_MIN_GAP or gap > max_gap:
        return None
    if (lb[1] + lb[3]) / 2.0 >= (ub[1] + ub[3]) / 2.0:
        return None                                   # not below
    overlap = min(ub[2], lb[2]) - max(ub[0], lb[0])
    narrower = max(min(ub[2] - ub[0], lb[2] - lb[0]), 1e-9)
    if overlap / narrower < min_overlap:
        return None
    return gap


def _right_of(left: _Line, right: _Line) -> Optional[float]:
    """Gap (in line heights) when ``right`` continues ``left`` on the same baseline, else None."""
    if not _same_rotation(left.run, right.run):
        return None
    lb, rb = left.frame_box, right.frame_box
    h = max(_line_height(left.run), _line_height(right.run))
    if abs((lb[1] + lb[3]) / 2.0 - (rb[1] + rb[3]) / 2.0) > 0.5 * h:
        return None
    gap = (rb[0] - lb[2]) / h
    if gap < -0.2 or gap > CONNECTOR_SIDE_GAP:
        return None
    return gap


def _ends_with_connector(line: _Line) -> bool:
    return line.kind in ("name", "other") and line.run.text.rstrip().endswith(CONNECTORS)


def _join_names(lines: list[_Line]) -> str:
    out = ""
    for line in lines:
        text = re.sub(r"\s+", " ", line.head.strip())
        if not out:
            out = text
        elif out.endswith("-") and not out.endswith(" -"):
            out += text                               # "BED-" + "ROOM" -> "BED-ROOM"
        else:
            out += " " + text
    return out


def _evidence(run: TextRun, file_rel: Optional[str], page: Optional[int]) -> list[dict]:
    if run.evidence:
        return [dict(e) for e in run.evidence]
    if file_rel is None:
        return []
    method = _EVIDENCE_METHOD.get(run.source, "vector")
    # A vector text is what the file says; an OCR/AI run without its own evidence gets a low confidence.
    confidence = 1.0 if method == "vector" else 0.5
    return [B.evidence(file_rel, method, confidence, page=page, entity=run.id, text=run.text)]


def _union_box(runs: list[TextRun]) -> tuple[float, float, float, float]:
    return (min(r.box[0] for r in runs), min(r.box[1] for r in runs),
            max(r.box[2] for r in runs), max(r.box[3] for r in runs))


def page_unit_system(texts: list[TextRun]) -> str:
    """§1.1: the majority of the page's explicit lengths (single lengths first, then size and area labels)."""
    singles = [t.text for t in texts if units.parse_length(t.text) is not None]
    sizes = [t.text for t in texts if units.parse_length(t.text) is None]
    return units.majority_system(singles, sizes)


# Texts on building-services layers name ducts, shafts and equipment, not rooms (real03, 10 Oct 2026: layer
# "____MEK_MEKANİK ÇALIŞMA" wrote "SUBSTATİON" into the floor hall and "Hava Bacası" into a living room). "MEKAN"
# alone (Turkish "space") is a room layer, so the services words are matched in full.
SERVICES_LAYER_RE = re.compile(r"MEKAN[İI]K|MECHANICAL|ELEKTR[İI]K|ELECTRICAL|TES[İI]SAT|PLUMBING|HVAC|SIHH[İI]",
                               re.IGNORECASE)


def _services_text(run: TextRun) -> bool:
    layers = {str(e.get("layer") or "") for e in (run.evidence or []) if isinstance(e, dict)}
    return any(SERVICES_LAYER_RE.search(name.upper()) for name in layers if name)


LETTER_GAP_H = 3.0              # 4 Nov 2026 (UL323): letters of one word written one by one at most this many heights apart
LETTER_H_TOL = 0.25             # ... of one height (within this share) ...
LETTER_LINE_TOL = 0.5           # ... and on one line (centres within this many heights)


def join_spaced_letters(texts: list) -> list:
    """4 Nov 2026 (real07, user: "where is the havuz (pool) ?"): a word written as single letters, each its own text
    ('H', 'A', 'V', 'U', 'Z'), is one text: runs of three or more one-letter texts of one height on one horizontal line,
    each next letter within ``LETTER_GAP_H`` heights, become one run with the joined word (the others stay as they are)."""
    singles = [t for t in texts if len((t.text or "").strip()) == 1 and (t.text or "").strip().isalpha()
               and abs(float(getattr(t, "rotation_deg", 0.0) or 0.0)) % 360.0 < 1.0 and t.height > 0]
    if len(singles) < 3:
        return texts
    singles.sort(key=lambda t: (round((t.box[1] + t.box[3]) / 2.0 / max(t.height, 1e-9)), t.box[0]))
    used: set = set()
    words = []
    for i, a in enumerate(singles):
        if id(a) in used:
            continue
        run = [a]
        for b in singles[i + 1:]:
            last = run[-1]
            h = last.height
            if id(b) in used or abs(b.height - h) > LETTER_H_TOL * h:
                continue
            if abs((b.box[1] + b.box[3]) / 2.0 - (last.box[1] + last.box[3]) / 2.0) > LETTER_LINE_TOL * h:
                continue
            gap = b.box[0] - last.box[2]
            if -0.2 * h <= gap <= LETTER_GAP_H * h:
                run.append(b)
        if len(run) >= 3:
            used |= {id(t) for t in run}
            x0, y0 = min(t.box[0] for t in run), min(t.box[1] for t in run)
            x1, y1 = max(t.box[2] for t in run), max(t.box[3] for t in run)
            words.append(TextRun(id=run[0].id, text="".join(t.text.strip() for t in run), box=(x0, y0, x1, y1),
                                 height=run[0].height, rotation_deg=0.0, source=run[0].source,
                                 evidence=[dict(e) for e in run[0].evidence]))
    if not words:
        return texts
    return [t for t in texts if id(t) not in used] + words


# 6 Nov 2026 (Milestone 14 reader target 4; real14, all 18 levels: the finishes table '+ x,xx kotu / MAHAL / SALON /
# MUTFAK / YATAK ODASI / WC / BANYO / ANTRE' beside every plan was read as room labels outside the walls): a room
# schedule is a list, never labels. A list is a column (or a row) of texts of one height and rotation, aligned left,
# centred or right, each the next within ``SCHEDULE_PITCH`` line heights (centre to centre; a row: edge gaps within
# ``SCHEDULE_ROW_GAP``); room labels on a plan stand rooms apart (5 to 20 line heights). A list with at least
# ``SCHEDULE_MIN_WORDS`` room words is a schedule when a header word stands at its head (``SCHEDULE_HEADER_RE``; its
# rows may then stand up to ``SCHEDULE_PITCH_HEADED`` apart: real15's MAHAL LİSTESİ, 4.2 line heights) or, given the
# walls' hull, when all its room words stand outside it.
SCHEDULE_MIN_WORDS = 4
SCHEDULE_PITCH = 3.5          # centre-to-centre distance of two entries of a column, x the line height
SCHEDULE_PITCH_HEADED = 5.0   # ... of a column under a header word
SCHEDULE_ROW_GAP = 3.0        # edge gap of two entries of a row, x the line height
SCHEDULE_ALIGN = 1.0          # entries of a column share their left, centre or right within this x the line height
SCHEDULE_HEIGHT_TOL = 0.3     # entries of one list differ in height by at most this share
SCHEDULE_HEADER_GAP = 3.0     # a header stands within this x the entry height before the first entry
SCHEDULE_HEADER_RE = re.compile(
    r"^(?:MAHAL(?:\s+(?:LISTESI|ADI|ADLARI|NO|CIZELGESI|TABLOSU))?|MEKAN(?:\s+(?:ADI|LISTESI))?|ROOMS?(?:\s+(?:NAMES?|"
    r"SCHEDULE|LIST|DATA))?|SPACES?(?:\s+(?:NAMES?|SCHEDULE|LIST))?|ALAN(?:\s+(?:LISTESI|TABLOSU|CIZELGESI))?|"
    r"(?:\w+\s+)?SCHEDULE|RAUM(?:BEZEICHNUNG|LISTE|BUCH)?|PIECES?|LOCAL|LOCAUX|NOMENCLATURE)\s*[:.]?$")


def is_schedule_header(text: str) -> bool:
    """A schedule's header cell (``MAHAL``, ``MAHAL LİSTESİ``, ``ROOM``, ``SPACE``, ``ALAN``, ``... SCHEDULE``)."""
    return bool(SCHEDULE_HEADER_RE.match(" ".join(B.fold_ascii(str(text or "")).split()).upper()))


def schedules(texts: list, hull=None, tf: Optional[list] = None) -> list[dict]:
    """The room schedules among a page's texts (pure; the comment above ``SCHEDULE_MIN_WORDS``): ``[{"axis": column |
    row, "run_ids", "room_words", "header", "header_id", "why", "box"}]``. ``hull`` (a shapely geometry in the texts'
    frame, or in the frame ``tf`` maps the texts to: ``[a, b, c, d, e, f]``, x' = a x + b y + c, y' = d x + e y + f; the
    walls' convex hull) adds the rule "all room words outside the walls". ``_runs`` holds the runs
    themselves (the caller drops them by identity and pops the key before writing the schedule anywhere)."""
    from shapely.geometry import Point, box as _box
    from shapely.strtree import STRtree

    runs = [t for t in texts if (t.text or "").strip()]
    if len(runs) < SCHEDULE_MIN_WORDS:
        return []
    fbs = [_frame_box(t) for t in runs]
    hs = [_line_height(t) for t in runs]
    word = [_is_name_text(t.text, indoor_only=True) for t in runs]
    if sum(word) < SCHEDULE_MIN_WORDS:
        return []
    tree = STRtree([_box(*fb) for fb in fbs])
    headers = [k for k, t in enumerate(runs) if is_schedule_header(t.text)]
    out: list[dict] = []
    for axis in ("column", "row"):
        nxt: dict[int, tuple[float, int]] = {}
        for i, fb in enumerate(fbs):
            h = hs[i]
            cx, cy = (fb[0] + fb[2]) / 2.0, (fb[1] + fb[3]) / 2.0
            if axis == "column":
                q = (fb[0] - SCHEDULE_ALIGN * h, cy - SCHEDULE_PITCH_HEADED * h * (1 + SCHEDULE_HEIGHT_TOL),
                     fb[2] + SCHEDULE_ALIGN * h, cy)
            else:
                q = (fb[2], cy - 0.5 * h, fb[2] + SCHEDULE_ROW_GAP * h * (1 + SCHEDULE_HEIGHT_TOL), cy + 0.5 * h)
            best = None
            for j in tree.query(_box(*q)):
                j = int(j)
                if j == i or not _same_rotation(runs[i], runs[j]):
                    continue
                hj = hs[j]
                hm = max(h, hj)
                if abs(h - hj) > SCHEDULE_HEIGHT_TOL * hm:
                    continue
                g = fbs[j]
                gx, gy = (g[0] + g[2]) / 2.0, (g[1] + g[3]) / 2.0
                if axis == "column":
                    d = cy - gy
                    if d <= 0.5 * hm or d > SCHEDULE_PITCH_HEADED * hm:
                        continue
                    if min(abs(cx - gx), abs(fb[0] - g[0]), abs(fb[2] - g[2])) > SCHEDULE_ALIGN * hm:
                        continue
                else:
                    d = g[0] - fb[2]
                    if d < -0.2 * hm or d > SCHEDULE_ROW_GAP * hm or abs(cy - gy) > 0.5 * hm:
                        continue
                if best is None or d < best[0]:
                    best = (d, j, d / hm)
            if best is not None:
                nxt[i] = best
        pred: dict[int, tuple[float, int]] = {}
        for i, (d, j, _rel) in nxt.items():
            if j not in pred or d < pred[j][0]:
                pred[j] = (d, i)
        follow = {i: j for j, (_d, i) in pred.items()}
        seen: set = set()
        lists = []
        for head in sorted(set(range(len(runs))) - set(pred)):
            chain, k = [], head
            while k is not None and k not in seen:
                seen.add(k)
                chain.append(k)
                k = follow.get(k)
            if sum(1 for k in chain if word[k]) < SCHEDULE_MIN_WORDS:
                continue
            if _schedule_header(chain, axis, runs, fbs, hs, headers) is not None:
                lists.append(chain)
                continue
            # without a header, a column's entries stand within SCHEDULE_PITCH of each other: the chain is cut at
            # the wider links (the walk to a header below may still find one for each part)
            part = [chain[0]]
            for a, b in zip(chain, chain[1:]):
                if axis == "column" and nxt[a][2] > SCHEDULE_PITCH:
                    lists.append(part)
                    part = []
                part.append(b)
            lists.append(part)
        for chain in lists:
            words = [k for k in chain if word[k]]
            if len(words) < SCHEDULE_MIN_WORDS:
                continue
            header = _schedule_header(chain, axis, runs, fbs, hs, headers)
            if header is None and axis == "column":
                # a column with an empty cell (real14 L5: no MUTFAK and ODA rows): walk up through the entries of the
                # same column, gaps up to SCHEDULE_BRIDGE pitches; the walk counts only when it ends at a header
                walked, k = [], chain[0]
                while header is None:
                    up = _column_above(k, runs, fbs, hs, tree, set(chain) | set(walked))
                    if up is None:
                        break
                    walked.append(up)
                    header = _schedule_header([up] + chain, axis, runs, fbs, hs, headers)
                    k = up
                if header is not None:
                    chain = list(reversed(walked)) + chain
                    words = [k for k in chain if word[k]]
            outside = hull is not None and not hull.is_empty and all(
                not hull.contains(Point(_mapped(((runs[k].box[0] + runs[k].box[2]) / 2.0,
                                                 (runs[k].box[1] + runs[k].box[3]) / 2.0), tf))) for k in words)
            if header is None and not outside:
                continue
            ids = [runs[k].id for k in chain] + ([runs[header].id] if header is not None else [])
            bx = [runs[k].box for k in chain]
            out.append({"axis": axis, "run_ids": ids, "room_words": [runs[k].text for k in words],
                        "header": runs[header].text if header is not None else None,
                        "header_id": runs[header].id if header is not None else None,
                        "why": (f"header '{runs[header].text}'" if header is not None else "")
                               + (" and " if header is not None and outside else "")
                               + ("outside every wall's hull" if outside else ""),
                        "box": [min(b[0] for b in bx), min(b[1] for b in bx), max(b[2] for b in bx),
                                max(b[3] for b in bx)],
                        "_runs": [runs[k] for k in chain] + ([runs[header]] if header is not None else [])})
    return out


def _mapped(p, tf: Optional[list]) -> tuple:
    if not tf:
        return p
    return (tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5])


SCHEDULE_BRIDGE = 3.0         # an empty cell: a column's entries this many pitches apart, when a header tops them


def _box_in_frame(box, rotation_deg: float) -> tuple[float, float, float, float]:
    """A page box rotated into the reading frame of a text of ``rotation_deg`` (``_frame_box`` for another run)."""
    a = math.radians(-rotation_deg)
    c, si = math.cos(a), math.sin(a)
    x0, y0, x1, y1 = box
    pts = [(x * c - y * si, x * si + y * c) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)


def _schedule_header(chain: list, axis: str, runs: list, fbs: list, hs: list, headers: list) -> Optional[int]:
    """The index of the header cell (among ``headers``, the indices of the header texts) standing at the head of a list
    (above a column, above or left of a row), in the list's reading frame (a header may be turned: real15's upright
    MAHAL LİSTESİ over a horizontal list)."""
    first = fbs[chain[0]]
    h0 = hs[chain[0]]
    rot = runs[chain[0]].rotation_deg
    x0, x1 = min(fbs[k][0] for k in chain), max(fbs[k][2] for k in chain)
    for j in headers:
        if j in chain:
            continue
        g = _box_in_frame(runs[j].box, rot)
        gap = SCHEDULE_HEADER_GAP * max(h0, hs[j])          # a larger header stands further
        above = g[1] >= first[3] - 0.5 * h0 and g[1] - first[3] <= gap and min(g[2], x1) - max(g[0], x0) > -h0
        left = axis == "row" and g[2] <= first[0] + 0.2 * h0 and first[0] - g[2] <= gap \
            and abs((g[1] + g[3]) / 2.0 - (first[1] + first[3]) / 2.0) <= 0.5 * max(h0, hs[j])
        if above or left:
            return j
    return None


def _column_above(k: int, runs: list, fbs: list, hs: list, tree, used: set) -> Optional[int]:
    """The nearest entry above run ``k`` in its column (same rotation and height, aligned), at most
    ``SCHEDULE_BRIDGE`` pitches away; None when there is none."""
    from shapely.geometry import box as _box

    fb, h = fbs[k], hs[k]
    cx, cy = (fb[0] + fb[2]) / 2.0, (fb[1] + fb[3]) / 2.0
    reach = SCHEDULE_BRIDGE * SCHEDULE_PITCH * h * (1 + SCHEDULE_HEIGHT_TOL)
    best = None
    for j in tree.query(_box(fb[0] - SCHEDULE_ALIGN * h, cy, fb[2] + SCHEDULE_ALIGN * h, cy + reach)):
        j = int(j)
        if j == k or j in used or not _same_rotation(runs[k], runs[j]):
            continue
        hm = max(h, hs[j])
        if abs(h - hs[j]) > SCHEDULE_HEIGHT_TOL * hm:
            continue
        g = fbs[j]
        gx, gy = (g[0] + g[2]) / 2.0, (g[1] + g[3]) / 2.0
        d = gy - cy
        if d <= 0.5 * hm or d > SCHEDULE_BRIDGE * SCHEDULE_PITCH * hm:
            continue
        if min(abs(cx - gx), abs(fb[0] - g[0]), abs(fb[2] - g[2])) > SCHEDULE_ALIGN * hm:
            continue
        if best is None or d < best[0]:
            best = (d, j)
    return best[1] if best is not None else None


def merge_label_blocks(texts_m: list[TextRun], file_rel: Optional[str] = None,
                       page: Optional[int] = None, hull=None,
                       schedules_out: Optional[list] = None) -> list[LabelBlock]:
    """Text runs of one page -> room/site label blocks (§2.7.2), in reading order (top to bottom, left to right).

    ``file_rel``/``page`` build the evidence of runs that carry none (vector runs: confidence 1.0). 6 Nov 2026 (target
    4): the runs of a room schedule (``schedules``; ``hull``: the walls' convex hull in the runs' frame) are no labels;
    the schedules found are appended to ``schedules_out`` when given.
    """
    found = schedules(texts_m, hull)
    if found:
        drop = {id(t) for s in found for t in s.pop("_runs")}
        texts_m = [t for t in texts_m if id(t) not in drop]
        if schedules_out is not None:
            schedules_out.extend(found)
    texts_m = join_spaced_letters([t for t in texts_m if not _services_text(t)])
    system = page_unit_system(texts_m)
    lines = [_classify(t, system) for t in texts_m if t.text and t.text.strip()]
    candidates = [ln for ln in lines if ln.kind != "skip"]

    # Each line links to the line that continues it (the nearest one below; for a connector run also a
    # little further below or to the right). A line has at most one predecessor: the nearest wins.
    succ: dict[int, tuple[float, int]] = {}
    for i, upper in enumerate(candidates):
        if upper.kind == "area":
            continue                                  # an area line ends its block
        best: Optional[tuple[float, int]] = None
        for j, lower in enumerate(candidates):
            if i == j:
                continue
            gap = _below(upper, lower, STACK_GAP, STACK_OVERLAP)
            if gap is None and _ends_with_connector(upper) and lower.kind in ("name", "other"):
                gap = _below(upper, lower, CONNECTOR_GAP, 1e-9)
                if gap is None:
                    # The continuation to the right ranks after every line below (+10 line heights).
                    side = _right_of(upper, lower)
                    gap = None if side is None else side + 10.0
            if gap is not None and (best is None or gap < best[0]):
                best = (gap, j)
        if best is not None:
            succ[i] = best
    pred: dict[int, tuple[float, int]] = {}
    for i, (gap, j) in succ.items():
        if j not in pred or gap < pred[j][0]:
            pred[j] = (gap, i)
    next_of = {i: j for j, (_, i) in pred.items()}

    blocks: list[LabelBlock] = []
    heads = [i for i in range(len(candidates)) if i not in pred]
    seen: set[int] = set()
    for head in heads:
        chain = []
        k: Optional[int] = head
        while k is not None and k not in seen:
            seen.add(k)
            chain.append(candidates[k])
            k = next_of.get(k)
        blocks.extend(_blocks_from_chain(chain, file_rel, page, system))
    blocks.sort(key=lambda b: (-b.anchor[1], b.anchor[0]))
    return blocks


def _blocks_from_chain(chain: list[_Line], file_rel: Optional[str], page: Optional[int],
                       system: str) -> list[LabelBlock]:
    out: list[LabelBlock] = []
    names: list[_Line] = []
    size_line: Optional[_Line] = None
    area_line: Optional[_Line] = None
    inline_size: Optional[str] = None
    inline_area: Optional[str] = None

    def close() -> None:
        nonlocal names, size_line, area_line, inline_size, inline_area
        size_text = size_line.size_text if size_line else inline_size
        area_text = area_line.area_text if area_line else inline_area
        # "BED-" + "ROOM": the keyword may only appear once the lines are joined.
        has_keyword = any(ln.kind == "name" for ln in names) or bool(names) and _is_name_text(_join_names(names),
                                                                                             indoor_only=False)
        if names and (has_keyword or size_text or area_text):
            out.append(_make_block(names, size_line, area_line, size_text, area_text, file_rel, page, system))
        names, size_line, area_line, inline_size, inline_area = [], None, None, None, None

    for line in chain:
        if line.kind in ("name", "other"):
            if size_line or area_line or inline_size or inline_area:
                close()
            names.append(line)
            inline_size = inline_size or line.size_text
            inline_area = inline_area or line.area_text
        elif line.kind == "size":
            if not names or size_line or inline_size or area_line:
                close()
                continue                              # a size line with no name above is no label
            size_line = line
        elif line.kind == "area":
            if not names or area_line or inline_area:
                close()
                continue
            area_line = line
    close()
    return out


def _make_block(names: list[_Line], size_line: Optional[_Line], area_line: Optional[_Line],
                size_text: Optional[str], area_text: Optional[str], file_rel: Optional[str],
                page: Optional[int], system: str) -> LabelBlock:
    name = _join_names(names)
    name_runs = [ln.run for ln in names]
    runs = name_runs + [ln.run for ln in (size_line, area_line) if ln is not None]
    nb = _union_box(name_runs)
    room_type, exterior = room_type_for(name)
    size = units.parse_size_pair(size_text, system) if size_text else None
    area = units.parse_area(area_text) if area_text else None
    evidence = [e for r in runs for e in _evidence(r, file_rel, page)]
    return LabelBlock(name=name, name_runs=name_runs, size_text=size_text, area_text=area_text,
                      anchor=((nb[0] + nb[2]) / 2.0, (nb[1] + nb[3]) / 2.0), room_type=room_type,
                      exterior=exterior, evidence=evidence, size=size, area_m2=area[0] if area else None,
                      box=_union_box(runs), runs=runs)


# --------------------------------------------------------------------------
# Size labels against faces (§2.7.3)
# --------------------------------------------------------------------------

def clear_size(face_polygon) -> tuple[float, float, float]:
    """(side a, side b, rectangularity) of a face: the minimum-area rectangle's sides and face area /
    rectangle area (1.0 for a rectangle)."""
    rect = face_polygon.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    a = math.dist(coords[0], coords[1])
    b = math.dist(coords[1], coords[2])
    rect_area = rect.area
    return a, b, (face_polygon.area / rect_area if rect_area > 0 else 0.0)


def match_sides(label: tuple[float, float], sides: tuple[float, float]) -> tuple[list[float], list[float]]:
    """The measured sides in the label's order (the orientation with the smaller worst relative error)
    and the relative errors (label - measured) / measured."""
    w, l = label
    a, b = sides
    best = None
    for mw, ml in ((a, b), (b, a)):
        errs = [(w - mw) / mw if mw > 0 else math.inf, (l - ml) / ml if ml > 0 else math.inf]
        worst = max(abs(e) for e in errs)
        if best is None or worst < best[0]:
            best = (worst, [mw, ml], errs)
    return best[1], best[2]


def check_label_size(block: LabelBlock, face_polygon) -> Optional[dict]:
    """``rooms[].label_size`` for a block with a printed size and the face it names (any consistent metric
    frame, e.g. page or building metres): ``{"text", "width_m", "length_m", "measured": [w, l], "status"}``
    plus ``off_pct`` (per side, or the area for an unchecked face) and ``unverified`` (the room loses its
    ``verified`` status: a side off by more than 10 %, or the area by more than 21 % on a non-rectangular
    face). None when the block has no parsable size."""
    if block.size is None:
        return None
    w, l = block.size[0].metres, block.size[1].metres
    a, b, rectangularity = clear_size(face_polygon)
    measured, errs = match_sides((w, l), (a, b))
    result = {"text": block.size_text, "width_m": round(w, 4), "length_m": round(l, 4),
              "measured": [round(measured[0], 3), round(measured[1], 3)]}
    if rectangularity >= RECTANGULAR_MIN:
        ok = all(abs(lab - mea) <= max(SIZE_TOL_REL * mea, SIZE_TOL_ABS_M)
                 for lab, mea in zip((w, l), measured))
        result["status"] = "ok" if ok else "conflict"
        result["off_pct"] = [round(100.0 * e, 1) + 0.0 for e in errs]   # + 0.0: no "-0.0"
        result["unverified"] = (not ok) and max(abs(e) for e in errs) > SIZE_UNVERIFIED_REL
        return result
    face_area = face_polygon.area
    area_err = (w * l - face_area) / face_area if face_area > 0 else math.inf
    result["status"] = "unchecked" if abs(area_err) <= AREA_TOL_REL else "conflict"
    result["off_pct"] = [round(100.0 * area_err, 1) + 0.0]
    result["area_m2"] = {"label": round(w * l, 3), "face": round(face_area, 3)}
    result["unverified"] = abs(area_err) > AREA_UNVERIFIED_REL
    return result
