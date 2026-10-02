"""Brief text -> style profile (Milestone 3 section 1). Deterministic, no AI.

What: ``profile_from_brief`` turns ``brief.yaml`` (``style: "..."`` or
``styles: [...]``) into the ``style.json`` dict the Blender side consumes:
floor / walls / ceiling / wet rooms / trim / door / window frame materials
and the lighting mood. ``profiles_from_brief`` returns one profile per entry
of ``styles``.

How: the text is split into comma phrases; each phrase is matched against the
keyword tables in ``vocabulary.py`` (whole words, first match in the phrase
wins). Slots the brief does not name come from the style family word
("Scandinavian") or from ``wenart/defaults.yaml``; every such fill is written
to ``warnings`` as ``assumed: ...`` so nothing is silent. Phrases with no
keyword at all go to ``unmatched_terms``.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Optional

from wenart.style import vocabulary as V

DEFAULTS_PATH = Path(__file__).resolve().parents[1] / "defaults.yaml"

# The slots of the profile, in output order (shape of docs/milestone3.md §1).
PROFILE_KEYS = ("source_text", "floor", "walls", "ceiling", "wet_floor", "wet_walls", "trim", "door",
                "window_frame", "lighting", "matched_terms", "unmatched_terms", "warnings")

# The default style text and slot fallbacks of wenart/defaults.yaml, repeated
# here so the scene builder inside Blender (whose Python has no PyYAML) gets
# the same default profile through the vocabulary. tests/test_style.py checks
# that this copy and the YAML file agree; edit both.
BUILTIN_DEFAULTS = {
    "style": {
        "text": "Scandinavian, light oak floor, white walls, linen textiles, warm daylight",
        "fallback": {"floor": "wood_oak_light", "walls": "plaster_white", "light": "warm daylight"},
    },
}


def load_defaults() -> dict:
    """``wenart/defaults.yaml`` as a dict (style text, default profile, brief defaults).

    Raises ImportError where PyYAML is missing (Blender's Python); callers
    that only need the default profile use ``default_profile``."""
    import yaml  # lazy: the vocabulary must stay importable without PyYAML

    return yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8"))


def _defaults_or_builtin() -> dict:
    try:
        return load_defaults()
    except ImportError:
        return copy.deepcopy(BUILTIN_DEFAULTS)


# --------------------------------------------------------------------------
# Keyword matching
# --------------------------------------------------------------------------

def split_phrases(text: str) -> list[str]:
    """Comma / semicolon / newline separated phrases, stripped, empty ones dropped."""
    return [p.strip() for p in re.split(r"[,;\n]+", text or "") if p.strip()]


def _hits(phrase_lc: str, table: list[tuple[str, str]]) -> list[tuple[int, int, str, str]]:
    """All keyword hits in a phrase as (position, -len(keyword), keyword, slug), sorted."""
    hits = []
    for keyword, slug in table:
        for m in re.finditer(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])", phrase_lc):
            hits.append((m.start(), -len(keyword), keyword, slug))
    hits.sort()
    return hits


def _first_hit(phrase_lc: str, table: list[tuple[str, str]], skip_keywords=()) -> tuple[Optional[str], list[str]]:
    """The winning slug of a phrase and the keywords of losing hits with another slug.

    Earliest position wins; at the same position the longest keyword wins
    ("warm daylight" beats "daylight"). Losing hits that would give a
    different slug are returned so the caller can report them.
    """
    hits = [h for h in _hits(phrase_lc, table) if h[2] not in skip_keywords]
    if not hits:
        return None, []
    pos, neg_len, _, slug = hits[0]
    end = pos - neg_len
    # Hits inside the winning keyword ("plaster" inside "cream plaster") are not separate words.
    others = sorted({kw for p, _, kw, s in hits[1:] if s != slug and not (pos <= p < end)})
    return slug, others


def match_text(text: str) -> dict:
    """Keyword scan of a brief text.

    Returns ``{"floor", "walls", "light", "family"}`` (slug or None, first
    phrase wins), ``matched`` / ``unmatched`` phrases in brief order and
    ``notes`` about words that were seen but ignored (second floor word, ...).
    """
    found: dict[str, Optional[str]] = {"floor": None, "walls": None, "light": None, "family": None}
    matched, unmatched, notes = [], [], []
    for phrase in split_phrases(text):
        lc = phrase.lower()
        hit_any = False

        floor, floor_others = _first_hit(lc, V.FLOOR_WORDS)
        if floor:
            hit_any = True
            _take(found, "floor", floor, phrase, notes)
            for kw in floor_others:
                notes.append(f"ignored floor word '{kw}' in '{phrase}' (phrase already gives {floor})")

        # A phrase about the floor must not recolour the walls through a bare colour word.
        skip = V.WALL_COLOUR_WORDS if (floor or re.search(r"(?<![a-z])floor", lc)) else ()
        walls, wall_others = _first_hit(lc, V.WALL_WORDS, skip_keywords=skip)
        if walls:
            hit_any = True
            _take(found, "walls", walls, phrase, notes)
            for kw in wall_others:
                notes.append(f"ignored wall word '{kw}' in '{phrase}' (phrase already gives {walls})")

        light, _ = _first_hit(lc, V.LIGHT_WORDS)
        if light:
            hit_any = True
            _take(found, "light", light, phrase, notes)

        family, _ = _first_hit(lc, [(kw, kw) for kw, _ in V.STYLE_FAMILIES])
        if family:
            hit_any = True
            _take(found, "family", family, phrase, notes)

        (matched if hit_any else unmatched).append(phrase)
    return {**found, "matched": matched, "unmatched": unmatched, "notes": notes}


def _take(found: dict, slot: str, value: str, phrase: str, notes: list[str]) -> None:
    """First phrase wins a slot; later different values are noted, not applied."""
    if found[slot] is None:
        found[slot] = value
    elif found[slot] != value:
        notes.append(f"ignored {slot} '{value}' from '{phrase}' ({slot} already {found[slot]})")


# --------------------------------------------------------------------------
# Style reference photos (docs/milestone5.md §6)
# --------------------------------------------------------------------------

PHOTO_SLOTS = ("floor", "walls", "light", "family")


def photo_term_list(photo_terms) -> list[dict]:
    """The terms of a ``python -m wenart.style.photos combine`` result (a dict with ``terms``) or of a term list."""
    if not photo_terms:
        return []
    terms = photo_terms.get("terms") if isinstance(photo_terms, dict) else photo_terms
    return [t for t in (terms or []) if isinstance(t, dict)]


def _photo_value_known(slot: str, value) -> bool:
    known = {"floor": {s for _, s in V.FLOOR_WORDS}, "walls": {s for _, s in V.WALL_WORDS},
             "light": set(V.LIGHTING), "family": {name for name, _ in V.STYLE_FAMILIES}}
    return value in known.get(slot, set())


def apply_photo_terms(scan: dict, photo_terms, warnings: list[str], override: bool = False) -> list[str]:
    """Fill the slots of a ``match_text`` scan that the brief text leaves open with agreed photo terms.

    The brief always wins: a slot the text names keeps its word and the
    photo term is only noted. ``override`` is for a brief without any style
    text, whose default text is itself an assumption: there the photo terms
    replace the default text's words. A photo family fills only the family
    (the floor / walls / light the family implies still count as assumed).
    Each use goes to ``scan["matched"]`` as ``photo:<file>:<term>`` and to
    ``warnings``; terms outside the vocabulary are ignored with a warning.
    Returns the ``photo:...`` entries added.
    """
    used: list[str] = []
    filled: set = set()
    for term in photo_term_list(photo_terms):
        slot, value = term.get("slot"), term.get("value")
        files = [str(f) for f in (term.get("files") or ([term["file"]] if term.get("file") else []))] or ["?"]
        where = ", ".join(files)
        if slot not in PHOTO_SLOTS or not _photo_value_known(slot, value):
            warnings.append(f"ignored photo term {slot}={value!r} from {where} (not in the vocabulary)")
            continue
        if slot in filled:
            warnings.append(f"ignored photo term {slot}={value} from {where} (a photo term already gave {slot})")
            continue
        if scan[slot] is not None and not override:
            if scan[slot] != value:
                warnings.append(f"photo: {slot} {value} from {where} not used (the brief names {scan[slot]})")
            continue
        if scan[slot] is not None and scan[slot] != value:
            warnings.append(f"photo: {slot} {value} from style photo {where} replaces {scan[slot]} of the default "
                            f"style text (no style in the brief)")
        else:
            warnings.append(f"photo: {slot} {value} from style photo {where} (the brief names no {slot}; "
                            f"both models agree)")
        scan[slot] = value
        filled.add(slot)
        for f in files:
            entry = f"photo:{f}:{value}"
            scan["matched"].append(entry)
            used.append(entry)
    return used


# --------------------------------------------------------------------------
# Profile assembly
# --------------------------------------------------------------------------

def profile_from_text(text: str, defaults: Optional[dict] = None, photo_terms=None, *,
                      photo_over_text: bool = False) -> dict:
    """The style profile of one brief text (see module docstring); ``photo_terms``: see ``apply_photo_terms``."""
    defaults = defaults or _defaults_or_builtin()
    family_defaults = dict(defaults["style"]["fallback"])
    scan = match_text(text)
    warnings = list(scan["notes"])
    apply_photo_terms(scan, photo_terms, warnings, override=photo_over_text)

    family = scan["family"]
    family_table = dict(V.STYLE_FAMILIES).get(family, {}) if family else {}

    def pick(slot: str) -> str:
        if scan[slot]:
            return scan[slot]
        if slot in family_table:
            warnings.append(f"assumed: {slot} {family_table[slot]} from style family '{family}' (no {slot} word in the brief)")
            return family_table[slot]
        warnings.append(f"assumed: {slot} {family_defaults[slot]} from wenart/defaults.yaml (no {slot} word in the brief)")
        return family_defaults[slot]

    floor = pick("floor")
    walls = pick("walls")
    mood = pick("light")

    wet_floor = floor if floor in V.WET_SAFE_FLOORS else V.WET_FLOOR_DEFAULT
    door = floor if V.MATERIALS[floor]["kind"] == "wood" else V.TRIM_MATERIAL
    light = V.LIGHTING[mood]
    if light["sun_strength"] == 0:
        warnings.append("night mood: no sun; interior lamps are not part of this milestone, renders will be dark")

    return {
        "source_text": text,
        "floor": {"material": floor, "asset": V.MATERIALS[floor]["asset"]},
        "walls": {"material": walls, "asset": V.MATERIALS[walls]["asset"]},
        "ceiling": {"material": V.CEILING_MATERIAL},
        "wet_floor": {"material": wet_floor, "asset": V.MATERIALS[wet_floor]["asset"]},
        "wet_walls": {"material": V.WET_WALLS_MATERIAL},
        "trim": {"material": V.TRIM_MATERIAL},
        "door": {"material": door},
        "window_frame": {"material": V.WINDOW_FRAME_MATERIAL},
        "lighting": {"hdri": light["hdri"], "sun_elevation_deg": light["sun_elevation_deg"],
                     "sun_azimuth_deg": light["sun_azimuth_deg"], "sun_strength": light["sun_strength"],
                     "colour_temperature_k": light["colour_temperature_k"], "mood": mood},
        "matched_terms": scan["matched"],
        "unmatched_terms": scan["unmatched"],
        "warnings": warnings,
    }


def style_texts(brief: Optional[dict]) -> list[str]:
    """The style texts of a brief: ``style`` first, then every entry of ``styles``."""
    texts: list[str] = []
    if brief:
        if isinstance(brief.get("style"), str) and brief["style"].strip():
            texts.append(brief["style"].strip())
        for entry in brief.get("styles") or []:
            if isinstance(entry, str) and entry.strip():
                texts.append(entry.strip())
    return texts


def profiles_from_brief(brief: Optional[dict], defaults: Optional[dict] = None, photo_terms=None) -> list[dict]:
    """One profile per style text of the brief; the default text when there is none.

    ``photo_terms`` (agreed terms of the style photos, §6) fill only the
    slots each text does not name; without any style text they replace the
    default text's words.
    """
    defaults = defaults or _defaults_or_builtin()
    texts = style_texts(brief)
    if not texts:
        profile = profile_from_text(defaults["style"]["text"], defaults, photo_terms, photo_over_text=True)
        profile["warnings"].insert(0, "assumed: no style in the brief, default style text from wenart/defaults.yaml")
        return [profile]
    return [profile_from_text(t, defaults, photo_terms) for t in texts]


def profile_from_brief(brief: Optional[dict], defaults: Optional[dict] = None, photo_terms=None) -> dict:
    """The first (or only) profile of the brief (``photo_terms``: see ``profiles_from_brief``)."""
    return profiles_from_brief(brief, defaults, photo_terms)[0]


def default_profile() -> dict:
    """The default profile: the default style text run through the vocabulary.

    Equal to the ``style.profile`` block of ``wenart/defaults.yaml`` (checked
    by tests/test_style.py) but computed, so the asset ids always come from
    the vocabulary and no PyYAML is needed (the scene builder in Blender).
    """
    defaults = _defaults_or_builtin()
    return profile_from_text(defaults["style"]["text"], defaults)


# --------------------------------------------------------------------------
# Helpers for the scene builder and the asset fetcher
# --------------------------------------------------------------------------

def is_wet_room(room_type: Optional[str]) -> bool:
    """Bathrooms, WCs and kitchens get the wet-room floor and walls."""
    return room_type in V.WET_ROOM_TYPES


def room_surfaces(profile: dict, room_type: Optional[str]) -> dict:
    """``{"floor": slug, "walls": slug, "ceiling": slug, "wet": bool}`` for a room."""
    wet = is_wet_room(room_type)
    return {"floor": profile["wet_floor" if wet else "floor"]["material"],
            "walls": profile["wet_walls" if wet else "walls"]["material"],
            "ceiling": profile["ceiling"]["material"], "wet": wet}


def material_slugs(profile: dict) -> list[str]:
    """Every material slug the profile uses (floor, walls, wet rooms, trim, door, frame, ceiling)."""
    slots = ("floor", "walls", "ceiling", "wet_floor", "wet_walls", "trim", "door", "window_frame")
    seen: list[str] = []
    for slot in slots:
        slug = profile[slot]["material"]
        if slug not in seen:
            seen.append(slug)
    return seen


def assets_in_profile(profile: dict) -> dict:
    """``{"textures": [(source, asset_id, slug), ...], "hdris": [(source, hdri_id)]}``."""
    textures, seen = [], set()
    for slug in material_slugs(profile):
        source, asset_id = V.asset_for(slug)
        if asset_id not in seen:
            seen.add(asset_id)
            textures.append((source, asset_id, slug))
    hdri = profile["lighting"]["hdri"]
    return {"textures": textures, "hdris": [(V.HDRIS.get(hdri, {}).get("source", "polyhaven"), hdri)]}


def write_profiles(profiles: list[dict], out_path: Path) -> list[Path]:
    """Write the first profile to ``out_path`` and the others to ``<stem>_2.json`` ... next to it."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for i, profile in enumerate(profiles):
        path = out_path if i == 0 else out_path.with_name(f"{out_path.stem}_{i + 1}{out_path.suffix}")
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    return written
