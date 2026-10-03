"""Helpers for the building JSON (``wenart/schema/building.schema.json``).

What lives here:
- ``empty_building``: a dict with every required top-level key, so modules
  only fill in what they know.
- ``evidence``: the one constructor for evidence objects (every element in the
  building JSON carries at least one).
- ID generation following the convention in docs/milestone2.md
  (``L0``, ``w_L0_001``, ``d_L0_001``, ``win_L0_001``, ``o_L0_001``,
  ``r_L0_salon``, ``f_L0_001``, ``c_001``).
- Label normalisation for Turkish room labels and level titles.
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
# (docs/milestone2.md, extended in docs/milestone6.md §3.3). A keyword matches
# at the start of a word, so inflected forms count (``banyosu`` -> ``banyo``).
_ROOM_TYPE_KEYWORDS = [
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
# When several keywords match, the room type that comes first here wins:
# ``EBEVEYN BANYO`` is a bathroom, ``SALON + MUTFAK`` a living room (its
# documented kitchen pieces stay kitchen pieces).
ROOM_TYPE_PRIORITY = ("wc", "bathroom", "storage", "balcony", "bedroom", "living", "kitchen", "hall", "other")

# Area suffix such as "24,50 m²", "24.5 m2", "24,50m²".
_AREA_RE = re.compile(r"\s*(\d+(?:[.,]\d+)?)\s*m(?:²|2)\s*$", re.IGNORECASE)
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
    """Split an optional area suffix off a label: ``SALON 24,50 m²`` -> (``SALON``, 24.5)."""
    match = _AREA_RE.search(text)
    if not match:
        return text.strip(), None
    number = match.group(1).replace(",", ".")
    return text[: match.start()].strip(), float(number)


def room_type_for(label: str) -> str:
    """Map a (normalised or raw) room label to the schema ``room_type``.

    Every keyword of ``_ROOM_TYPE_KEYWORDS`` that starts a word of the folded
    label matches (``EBEVEYN BANYOSU`` -> ``ebeveyn`` and ``banyo``); among the
    matches the type earliest in ``ROOM_TYPE_PRIORITY`` wins. No match ->
    ``other``.
    """
    folded = fold_ascii(label)
    matched = {room_type for keyword, room_type in _ROOM_TYPE_KEYWORDS
               if re.search(rf"(^|[^a-z]){keyword}", folded)}
    for room_type in ROOM_TYPE_PRIORITY:
        if room_type in matched:
            return room_type
    return "other"


def normalise_room_label(label_raw: str) -> tuple[str, str, Optional[float]]:
    """``label_raw`` as read -> (``label``, ``room_type``, ``area_label``).

    ``label`` is the Turkish title-case label without the area, ``WC`` stays
    upper-case. ``area_label`` is a float in m² or None.
    """
    text, area = parse_area_label(label_raw.strip())
    text = re.sub(r"\s+", " ", text)
    if fold_ascii(text) == "wc":
        label = "WC"
    else:
        label = turkish_title(text)
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
