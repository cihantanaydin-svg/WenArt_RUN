"""Helpers for the building JSON (``wenart/schema/building.schema.json``).

What lives here:
- ``empty_building``: a dict with every required top-level key, so modules
  only fill in what they know.
- ``evidence``: the one constructor for evidence objects (every element in the
  building JSON carries at least one).
- ID generation following the convention in docs/milestone2.md
  (``L0``, ``w_L0_001``, ``d_L0_001``, ``win_L0_001``, ``o_L0_001``,
  ``r_L0_salon``, ``f_L0_001``, ``c_001``).
- Label normalisation for room labels (Turkish and, since Milestone 7, English:
  vocabulary, type priority, casing) and Turkish level titles.
- ``validate`` against the schema with jsonschema, plus ``save``/``load``.

Why a module and not ad-hoc dicts: three code paths (synthetic truth, vector
ingest, raster recognition) must produce the same shapes and the same IDs so
the tests can compare them element by element.
"""
from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import jsonschema

from wenart import units

SCHEMA_PATH = Path(__file__).resolve().parent / "schema" / "building.schema.json"
SCHEMA_VERSION = "0.1"

METHODS = ("vector", "raster", "ocr", "ai", "derived")
ROOM_TYPES = ("living", "dining", "bedroom", "kitchen", "bathroom", "wc", "hall", "balcony", "storage", "prayer", "other",
              "unknown")

# Element kind -> ID prefix. Rooms and levels have their own functions.
ID_PREFIX = {
    "wall": "w",
    "door": "d",
    "window": "win",
    "opening": "o",
    "furniture": "f",
    "conflict": "c",
}

# Keyword (lower-case, Turkish letters folded to ASCII) -> room_type
# (docs/milestone2.md, extended in docs/milestone6.md §3.3). A Turkish keyword
# matches at the start of a word, so inflected forms count (``banyosu`` -> ``banyo``).
_TURKISH_ROOM_KEYWORDS = [
    ("salon", "living"),
    ("yatak", "bedroom"),
    ("cocuk", "bedroom"),
    ("ebeveyn", "bedroom"),
    ("mutfak", "kitchen"),
    ("banyo", "bathroom"),
    ("dus", "bathroom"),
    ("wc", "wc"),
    ("lavabo", "wc"),
    ("tuvalet", "wc"),
    ("hol", "hall"),
    ("antre", "hall"),
    ("koridor", "hall"),
    ("giris", "hall"),
    ("balkon", "balcony"),
    ("teras", "balcony"),
    ("kiler", "storage"),
    ("depo", "storage"),
    ("calisma", "other"),
]
# English room names (docs/milestone7.md §2.7.2). An English keyword is a whole word (an
# optional plural ``s``/``es`` allowed); the words of a two-word keyword may be written
# together or joined by a space, hyphen or underscore (``bed room``, ``bedroom``, ``bed-room``).
# ``hall`` alone is a living room in a large face (``room_type_for`` with the face size).
# The few one-word compounds (``kitchenette``, ``storeroom``, ``hallway``) are listed as such.
_ENGLISH_ROOM_KEYWORDS = [
    ("drawing", "living"), ("living", "living"), ("lounge", "living"), ("family", "living"),
    ("sitting", "living"),
    ("dining", "dining"),
    ("bed room", "bedroom"), ("master", "bedroom"), ("guest room", "bedroom"), ("kids", "bedroom"),
    ("children", "bedroom"), ("nursery", "bedroom"), ("br", "bedroom"),
    ("kitchen", "kitchen"), ("kitchenette", "kitchen"), ("kit", "kitchen"), ("pantry", "kitchen"),
    ("bath", "bathroom"), ("bath room", "bathroom"), ("shower", "bathroom"),
    ("toilet", "wc"), ("wc", "wc"), ("w.c", "wc"), ("powder", "wc"),
    ("hall", "hall"), ("hallway", "hall"), ("lobby", "hall"), ("passage", "hall"), ("corridor", "hall"),
    ("foyer", "hall"), ("entrance", "hall"), ("entry", "hall"), ("landing", "hall"),
    ("balcony", "balcony"), ("terrace", "balcony"), ("deck", "balcony"), ("verandah", "balcony"),
    ("veranda", "balcony"),
    ("store", "storage"), ("storeroom", "storage"), ("storage", "storage"), ("closet", "storage"),
    ("box room", "storage"),
    ("pooja", "prayer"), ("puja", "prayer"), ("prayer", "prayer"), ("mandir", "prayer"),
    ("study", "other"), ("office", "other"), ("utility", "other"), ("laundry", "other"),
    ("servant", "other"), ("maid", "other"),
]
_ROOM_TYPE_KEYWORDS = _TURKISH_ROOM_KEYWORDS + _ENGLISH_ROOM_KEYWORDS
# English words for the bathroom rule: a bath or shower word together with a toilet word is a
# bathroom (``Bath+ Toilet``, ``Bath/WC``); Turkish labels keep wc first (``Banyo/WC`` -> wc).
_ENGLISH_BATH_WORDS = ("bath", "bath room", "shower")
_ENGLISH_TOILET_WORDS = ("toilet", "wc", "w.c")
# Keywords that say nothing about the language (for the casing rule of normalise_room_label).
_NEUTRAL_KEYWORDS = ("wc",)
# Turkish words that are no room-type keyword but show a Turkish label (``YEMEK ODASI``).
_TURKISH_MARKERS = ("oda", "yemek", "giyinme", "camasir", "merdiven", "asansor")
_TURKISH_LETTERS = set("çğıöşüÇĞİÖŞÜ")
# When several keywords match, the room type that comes first here wins:
# ``EBEVEYN BANYO`` is a bathroom, ``SALON + MUTFAK`` a living room (its
# documented kitchen pieces stay kitchen pieces), ``Kitchen & Dining`` a kitchen.
ROOM_TYPE_PRIORITY = ("wc", "bathroom", "storage", "balcony", "bedroom", "living", "kitchen", "dining", "prayer",
                      "hall", "other")
# ``hall`` alone names a living room when its face is at least this large and this compact (§2.7.2).
HALL_AS_LIVING_MIN_AREA = 9.0
HALL_AS_LIVING_MAX_ASPECT = 2.5


def english_keyword_re(keyword: str) -> re.Pattern:
    """Whole-word pattern for an English keyword on ``fold_ascii`` text (see ``_ENGLISH_ROOM_KEYWORDS``)."""
    words = [re.escape(w) for w in keyword.split()]
    body = r"[\s\-_]*".join(words)
    return re.compile(rf"(?<![a-z]){body}(?:s|es)?(?![a-z])")


_ENGLISH_PATTERNS = [(english_keyword_re(k), k, t) for k, t in _ENGLISH_ROOM_KEYWORDS]

# Area suffix such as "24,50 m²", "24.5 m2", "24,50m²", "110 sq ft" (wenart.units).
_AREA_RE = units.AREA_SUFFIX_RE
_LEVEL_NUMBER_RE = re.compile(r"(\d+)\s*\.?\s*KAT")


# --------------------------------------------------------------------------
# Building skeleton, evidence
# --------------------------------------------------------------------------

def empty_building(project_id: str, source_folder: str, pipeline_commit: str,
                   created_utc: Optional[str] = None, brief: Optional[dict] = None,
                   status: str = "ok") -> dict:
    """A building dict with all required top-level keys and empty lists."""
    if created_utc is None:
        created_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    project = {
        "id": project_id,
        "source_folder": source_folder,
        "created_utc": created_utc,
        "pipeline_commit": pipeline_commit,
    }
    if brief is not None:
        project["brief"] = brief
    return {
        "schema_version": SCHEMA_VERSION,
        "project": project,
        "status": status,
        "documents": [],
        "levels": [],
        "walls": [],
        "openings": [],
        "rooms": [],
        "furniture": [],
        "conflicts": [],
        "unverified": [],
        "warnings": [],
    }


def evidence(file: str, method: str, confidence: float, *, page: Optional[int] = None,
             layer: Optional[str] = None, entity: Optional[str] = None, block: Optional[str] = None,
             pixel_box: Optional[list] = None, dpi: Optional[float] = None, model: Optional[str] = None,
             pass_: Optional[int] = None, text: Optional[str] = None) -> dict:
    """Build an evidence object. Only the keys that are given are written, so
    JSON stays short; the schema treats missing and null the same.

    ``pass_`` has a trailing underscore because ``pass`` is a Python keyword;
    it is written as ``pass`` in the JSON.
    """
    if method not in METHODS:
        raise ValueError(f"unknown evidence method {method!r}")
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence out of range: {confidence}")
    ev: dict[str, Any] = {"file": file, "method": method, "confidence": confidence}
    optional = {
        "page": page, "layer": layer, "entity": entity, "block": block,
        "pixel_box": pixel_box, "dpi": dpi, "model": model, "pass": pass_, "text": text,
    }
    for key, value in optional.items():
        if value is not None:
            ev[key] = value
    return ev


# --------------------------------------------------------------------------
# Text normalisation (Turkish aware)
# --------------------------------------------------------------------------

_TR_LOWER = str.maketrans({"I": "ı", "İ": "i"})
_TR_UPPER = str.maketrans({"i": "İ", "ı": "I"})
_TR_ASCII = str.maketrans({
    "ç": "c", "Ç": "C", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I", "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S", "ü": "u", "Ü": "U", "²": "2",
})


def turkish_lower(text: str) -> str:
    """Lower-case with Turkish dotted/dotless i rules (``I`` -> ``ı``, ``İ`` -> ``i``)."""
    return text.translate(_TR_LOWER).lower()


def turkish_upper(text: str) -> str:
    """Upper-case with Turkish rules (``i`` -> ``İ``, ``ı`` -> ``I``)."""
    return text.translate(_TR_UPPER).upper()


def turkish_title(text: str) -> str:
    """Title case word by word with Turkish rules: ``YATAK ODASI`` -> ``Yatak Odası``."""
    words = []
    for word in turkish_lower(text).split():
        words.append(turkish_upper(word[0]) + word[1:])
    return " ".join(words)


def fold_ascii(text: str) -> str:
    """Turkish letters -> ASCII look-alikes, other accents stripped, lower-case."""
    folded = text.translate(_TR_ASCII)
    folded = unicodedata.normalize("NFKD", folded)
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch))
    return folded.lower()


def slugify(text: str) -> str:
    """ASCII slug for IDs: ``Yatak Odası`` -> ``yatak_odasi``. Empty input -> ``room``."""
    folded = fold_ascii(text)
    slug = re.sub(r"[^a-z0-9]+", "_", folded).strip("_")
    return slug or "room"


# --------------------------------------------------------------------------
# Room and level labels
# --------------------------------------------------------------------------

def parse_area_label(text: str) -> tuple[str, Optional[float]]:
    """Split an optional area suffix off a label: ``SALON 24,50 m²`` -> (``SALON``, 24.5).

    The area is parsed by ``wenart.units`` (m² or sq ft, returned in m²).
    """
    split = units.area_suffix(text)
    if split is None:
        return text.strip(), None
    head, m2, _system, _area_text = split
    return head, m2


def room_keyword_hits(label: str) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """(Turkish hits, English hits) as (keyword, room_type) pairs found in a label."""
    folded = fold_ascii(label)
    turkish = [(keyword, room_type) for keyword, room_type in _TURKISH_ROOM_KEYWORDS
               if re.search(rf"(^|[^a-z]){keyword}", folded)]
    english = [(keyword, room_type) for pattern, keyword, room_type in _ENGLISH_PATTERNS if pattern.search(folded)]
    return turkish, english


def room_type_for(label: str, face_area_m2: Optional[float] = None, face_aspect: Optional[float] = None) -> str:
    """Map a (normalised or raw) room label to the schema ``room_type``.

    Every Turkish keyword that starts a word of the folded label matches
    (``EBEVEYN BANYOSU`` -> ``ebeveyn`` and ``banyo``), every English keyword
    that is a whole word of it (``Bath+ Toilet`` -> ``bath`` and ``toilet``).
    An English bath or shower word with a toilet word is a bathroom (before the
    priority; Turkish labels keep wc first: ``Banyo/WC`` -> wc). Otherwise the
    type earliest in ``ROOM_TYPE_PRIORITY`` wins. ``hall`` alone is a living
    room when the face is given and is at least ``HALL_AS_LIVING_MIN_AREA`` m²
    with an aspect of at most ``HALL_AS_LIVING_MAX_ASPECT``. No match -> ``other``.
    """
    turkish, english = room_keyword_hits(label)
    english_words = {keyword for keyword, _ in english}
    if english_words & set(_ENGLISH_BATH_WORDS) and english_words & set(_ENGLISH_TOILET_WORDS):
        return "bathroom"
    if not turkish and english_words == {"hall"} and face_area_m2 is not None and face_aspect is not None:
        if face_area_m2 >= HALL_AS_LIVING_MIN_AREA and face_aspect <= HALL_AS_LIVING_MAX_ASPECT:
            return "living"
    matched = {room_type for _, room_type in turkish + english}
    for room_type in ROOM_TYPE_PRIORITY:
        if room_type in matched:
            return room_type
    return "other"


def has_turkish_letters(text: str) -> bool:
    """``ç ğ ı ö ş ü`` (either case) or a dotted capital ``İ`` in the text."""
    return any(ch in _TURKISH_LETTERS for ch in text)


def is_turkish_label(text: str) -> bool:
    """Whether a label is written in Turkish (for casing): Turkish letters, a Turkish word that
    is no keyword (``ODASI``, ``YEMEK``), or a Turkish keyword without any English one
    (``wc`` counts for neither language)."""
    if has_turkish_letters(text):
        return True
    folded = fold_ascii(text)
    if any(re.search(rf"(^|[^a-z]){marker}", folded) for marker in _TURKISH_MARKERS):
        return True
    if re.search(r"(^|[^a-z])ve($|[^a-z])", folded):
        return True                                   # "BANYO VE WC"
    turkish, english = room_keyword_hits(text)
    turkish = [k for k, _ in turkish if k not in _NEUTRAL_KEYWORDS]
    english = [k for k, _ in english if k not in _NEUTRAL_KEYWORDS]
    return bool(turkish) and not english


def plain_title(text: str) -> str:
    """Title case without Turkish rules: ``LIVING ROOM`` -> ``Living Room``, ``BATH+TOILET`` ->
    ``Bath+Toilet``, ``children's room`` -> ``Children's Room``; the word ``WC`` stays upper-case."""
    lowered = text.lower()
    titled = re.sub(r"(?<![^\W_])(?<!['’])[^\W\d_]", lambda m: m.group(0).upper(), lowered)
    return re.sub(r"(?<![^\W_])wc(?![^\W_])", "WC", titled, flags=re.IGNORECASE)


def normalise_room_label(label_raw: str, turkish: Optional[bool] = None) -> tuple[str, str, Optional[float]]:
    """``label_raw`` as read -> (``label``, ``room_type``, ``area_label``).

    ``label`` is the title-case label without the area: Turkish title case
    (``YATAK ODASI`` -> ``Yatak Odası``) for Turkish labels, plain title case
    otherwise (``LIVING ROOM`` -> ``Living Room``); ``WC`` stays upper-case.
    ``turkish`` forces the language (e.g. from the page); None decides by
    ``is_turkish_label``. ``area_label`` is a float in m² or None.
    """
    text, area = parse_area_label(label_raw.strip())
    text = re.sub(r"\s+", " ", text)
    if turkish is None:
        turkish = is_turkish_label(text)
    if fold_ascii(text) == "wc":
        label = "WC"
    elif turkish:
        label = turkish_title(text)
    else:
        label = plain_title(text)
    return label, room_type_for(label), area


def normalise_level_label(title_raw: str) -> Optional[tuple[str, int]]:
    """Level title as drawn -> (normalised label, order) or None if it is not a level.

    ``ZEMİN KAT PLANI`` -> (``Zemin Kat``, 0); ``1. KAT PLANI`` -> (``1. Kat``, 1);
    ``BODRUM KAT PLANI`` -> (``Bodrum Kat``, -1); ``ZEMİN KAT MOBİLYA PLANI`` ->
    (``Zemin Kat``, 0). ``MOBİLYA PLANI`` alone or ``ÖLÇEK 1/100`` -> None.
    """
    folded = fold_ascii(title_raw)
    upper = folded.upper()
    if "BODRUM" in upper:
        return "Bodrum Kat", -1
    if "ZEMIN" in upper:
        return "Zemin Kat", 0
    match = _LEVEL_NUMBER_RE.search(upper)
    if match:
        n = int(match.group(1))
        return f"{n}. Kat", n
    return None


# --------------------------------------------------------------------------
# IDs
# --------------------------------------------------------------------------

def level_id(order: int) -> str:
    """Level ID from the level order: 0 -> ``L0``, 1 -> ``L1``, -1 -> ``L-1``."""
    return f"L{order}"


def element_id(kind: str, lvl_id: Optional[str], number: int) -> str:
    """``element_id("wall", "L0", 1)`` -> ``w_L0_001``; conflicts have no level: ``c_001``."""
    prefix = ID_PREFIX[kind]
    if kind == "conflict":
        return f"{prefix}_{number:03d}"
    if not lvl_id:
        raise ValueError(f"{kind} ids need a level id")
    return f"{prefix}_{lvl_id}_{number:03d}"


def room_id(lvl_id: str, label: str, taken: Optional[set] = None) -> str:
    """``r_<level>_<slug>``; repeats get ``_2``, ``_3`` ... ``taken`` is updated in place."""
    base = f"r_{lvl_id}_{slugify(label)}"
    if taken is None:
        taken = set()
    candidate = base
    n = 2
    while candidate in taken:
        candidate = f"{base}_{n}"
        n += 1
    taken.add(candidate)
    return candidate


class IdCounter:
    """Hands out sequential IDs per (kind, level) and unique room IDs.

    >>> ids = IdCounter()
    >>> ids.next("wall", "L0"), ids.next("wall", "L0"), ids.next("door", "L0")
    ('w_L0_001', 'w_L0_002', 'd_L0_001')
    >>> ids.room("L0", "Kiler"), ids.room("L0", "Kiler")
    ('r_L0_kiler', 'r_L0_kiler_2')
    """

    def __init__(self) -> None:
        self._counts: dict[tuple[str, Optional[str]], int] = {}
        self._rooms: set[str] = set()

    def next(self, kind: str, lvl_id: Optional[str] = None) -> str:
        key = (kind, None if kind == "conflict" else lvl_id)
        self._counts[key] = self._counts.get(key, 0) + 1
        return element_id(kind, lvl_id, self._counts[key])

    def room(self, lvl_id: str, label: str) -> str:
        return room_id(lvl_id, label, self._rooms)


# --------------------------------------------------------------------------
# Schema validation, save, load
# --------------------------------------------------------------------------

_schema_cache: Optional[dict] = None


def load_schema() -> dict:
    """The building JSON schema (cached)."""
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return _schema_cache


def validation_errors(building: dict) -> list[str]:
    """All schema violations as readable strings (empty list = valid).

    Note: ``format: date-time`` is not enforced because jsonschema has no
    date-time checker installed here; it stays an annotation.
    """
    validator = jsonschema.Draft202012Validator(load_schema())
    errors = sorted(validator.iter_errors(building), key=lambda e: list(e.absolute_path))
    out = []
    for err in errors:
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{path}: {err.message}")
    return out


def validate(building: dict) -> None:
    """Raise ``jsonschema.ValidationError`` (with all messages joined) if invalid."""
    errors = validation_errors(building)
    if errors:
        raise jsonschema.ValidationError("building JSON is invalid:\n" + "\n".join(errors))


def save(building: dict, path: str | Path, check: bool = True) -> Path:
    """Write the building JSON (UTF-8, indented, stable key order). Validates first by default."""
    if check:
        validate(building)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(building, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def load(path: str | Path, check: bool = True) -> dict:
    """Read a building JSON; validates by default."""
    building = json.loads(Path(path).read_text(encoding="utf-8"))
    if check:
        validate(building)
    return building
