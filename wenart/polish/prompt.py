"""Polish prompt of one view (docs/milestone5.md §3.5).

What: one English paragraph, no negative prompt (guidance 0 for Z-Image-Turbo):

    "Photorealistic interior photograph of a {room words} in {family} style.
    {wall words} walls, {floor words} floor{, furniture list}. {mood} light
    through the windows, soft natural shadows, realistic materials and
    textures, sharp focus, {lens} mm lens."

Where the words come from (nothing is guessed; every fallback is listed in
``warnings``):

- room words: the room type of the building JSON (``ROOM_WORDS``);
- family: the profile's ``family`` (Milestone 7) or, for older profiles,
  the style family word of its ``source_text``
  (``wenart.style.profile.match_text``); no family word -> the "in ... style"
  part is left out;
- wall / floor words: the slugs of the rendered style profile, the wet-room
  slots for bathrooms, WCs and kitchens (as the scene builder does), through
  ``MATERIAL_WORDS``;
- mood: ``style_profile.lighting.mood`` through ``MOOD_WORDS``;
- lens: the view's own camera ``lens_mm`` (Milestone 8: 18 or 16 mm for
  searched cameras, the brief's ``render.lens_mm`` when it sets one; the
  M5-M7 prompts said 24 mm); without a lens the prompt names none and a
  warning says so;
- furniture list: the own-room required and optional furniture of the view
  (``wenart.vision_check.expected.expected_view``), largest first,
  deduplicated types, at most 8. Pieces of type ``unknown`` or status
  ``unverified`` are left out: their type is not known, so naming one would
  push the model towards a guess.

The tables cover every slug of ``wenart.style.vocabulary`` (MATERIALS,
FURNITURE_MATERIALS, LIGHTING moods, STYLE_FAMILIES) and every room and
furniture type of the building schema; tests check that, so a new slug
without words fails a test instead of reaching a prompt as a raw slug.
"""
from __future__ import annotations

from typing import Optional

from wenart.style import vocabulary as VOC

MAX_FURNITURE = 8

# Room types of wenart/schema/building.schema.json.
ROOM_WORDS: dict[str, str] = {
    "living": "living room",
    "bedroom": "bedroom",
    "kitchen": "kitchen",
    "bathroom": "bathroom",
    "wc": "small toilet room",
    "hall": "hallway",
    "balcony": "balcony",
    "storage": "storage room",
    "dining": "dining room",          # Milestone 7 (docs/milestone7.md §6.5)
    "prayer": "prayer room",
    "other": "room",
    "unknown": "room",
}

# Style family keywords of vocabulary.STYLE_FAMILIES.
FAMILY_WORDS: dict[str, str] = {
    "scandinavian": "Scandinavian",
    "japandi": "Japandi",
    "modern minimal": "modern minimalist",
    "minimal": "minimalist",
    "modern": "modern",
    "industrial": "industrial",
    "mediterranean": "Mediterranean",
    "classic": "classic",
    "rustic": "rustic",
}

# Material slugs of vocabulary.MATERIALS and vocabulary.FURNITURE_MATERIALS,
# written to be followed by "walls" or "floor".
MATERIAL_WORDS: dict[str, str] = {
    "wood_oak_light": "light oak wood",
    "wood_walnut": "dark walnut wood",
    "wood_parquet": "herringbone parquet",
    "concrete_polished": "polished concrete",
    "terracotta": "terracotta tile",
    "marble": "white marble",
    "tiles_light": "light ceramic tile",
    "carpet": "carpet",
    "plaster_white": "white plaster",
    "plaster_cream": "cream plaster",
    "plaster_charcoal": "charcoal grey plaster",
    "plaster_exterior": "grey exterior plaster",
    "brick": "exposed red brick",
    "wood_panel": "dark wood panelled",
    "painted_wood_white": "white painted wood",
    "painted_metal_white": "white painted metal",
    "fabric_linen": "natural linen",
    "fabric_white": "white fabric",
    "ceramic_white": "white ceramic",
    "steel_brushed": "brushed steel",
    "stone_worktop": "dark stone",
    "lacquer_dark": "dark lacquered",
    "plant_green": "green plant",
    "wood_veneer_oak": "light oak veneer",
    "wood_veneer_walnut": "walnut veneer",
}

# Lighting moods of vocabulary.LIGHTING, written to be followed by "light".
MOOD_WORDS: dict[str, str] = {
    "warm daylight": "Warm daytime",
    "cool daylight": "Cool daytime",
    "golden evening": "Golden evening",
    "overcast": "Soft overcast",
    "night": "Dim night",
}

# Furniture types of the building schema (``unknown`` is never named).
FURNITURE_WORDS: dict[str, str] = {
    "bed_single": "single bed",
    "bed_double": "double bed",
    "sofa": "sofa",
    "armchair": "armchair",
    "table_dining": "dining table",
    "table_coffee": "coffee table",
    "desk": "desk",
    "chair": "chair",
    "wardrobe": "wardrobe",
    "kitchen_counter": "kitchen counter",
    "kitchen_island": "kitchen island",
    "fridge": "fridge",
    "stove": "stove",
    "sink_kitchen": "kitchen sink",
    "washbasin": "washbasin",
    "toilet": "toilet",
    "shower": "shower",
    "bathtub": "bathtub",
    "tv_unit": "TV unit",
    "bookshelf": "bookshelf",
    "nightstand": "nightstand",
    "dresser": "dresser",
    "washing_machine": "washing machine",
    # Milestone 7 (docs/milestone7.md §6.5): documented-only types.
    "stair": "staircase",
    "side_table": "side table",
    "floor_lamp": "floor lamp",
    "potted_plant": "potted plant",
}

PROMPT_TAIL = "light through the windows, soft natural shadows, realistic materials and textures, sharp focus"


def _words(table: dict, key, what: str, warnings: list) -> Optional[str]:
    if key is None:
        return None
    if key in table:
        return table[key]
    warnings.append(f"no prompt words for {what} {key!r}; used the slug")
    return str(key).replace("_", " ")


def _slot(profile: dict, slot: str) -> Optional[str]:
    entry = (profile or {}).get(slot)
    if isinstance(entry, dict):
        return entry.get("material")
    return entry if isinstance(entry, str) else None


def style_family(profile: dict) -> Optional[str]:
    """The style family keyword (``vocabulary.STYLE_FAMILIES``) of the rendered profile, or None:
    the profile's ``family`` field (Milestone 7) when it names a family, else the old derivation."""
    from wenart.style.profile import match_text
    recorded = (profile or {}).get("family")
    if isinstance(recorded, str) and recorded in dict(VOC.STYLE_FAMILIES):
        return recorded
    text = (profile or {}).get("source_text")
    family = match_text(text)["family"] if isinstance(text, str) and text.strip() else None
    if family:
        return family
    names = dict(VOC.STYLE_FAMILIES)
    for term in (profile or {}).get("matched_terms") or []:
        word = str(term).split(":")[-1].strip().lower()
        if word in names:
            return word
    return None


def surfaces(profile: dict, room_type: Optional[str]) -> dict:
    """``{"walls": slug, "floor": slug, "wet": bool}``: the wet-room slots for bathrooms, WCs and kitchens."""
    wet = room_type in VOC.WET_ROOM_TYPES
    walls = _slot(profile, "wet_walls") if wet else None
    floor = _slot(profile, "wet_floor") if wet else None
    return {"walls": walls or _slot(profile, "walls"), "floor": floor or _slot(profile, "floor"), "wet": wet}


def furniture_types(expected: Optional[dict], limit: int = MAX_FURNITURE) -> list[str]:
    """Own-room required/optional furniture types of an ``expected_view`` result, largest first, unique, <= limit."""
    if not expected:
        return []
    elements = sorted(expected.get("elements") or [], key=lambda e: -int(e.get("pixels") or 0))
    types: list[str] = []
    for e in elements:
        if e.get("kind") != "furniture" or not e.get("own_room") or e.get("role") not in ("required", "optional"):
            continue
        ftype = e.get("type")
        if not ftype or ftype == "unknown" or e.get("status") == "unverified" or e.get("type_unverified"):
            continue
        if ftype not in types:
            types.append(ftype)
        if len(types) >= limit:
            break
    return types


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def lens_words(lens_mm) -> Optional[str]:
    """``"18 mm lens"`` for a camera lens in mm (None for none or a non-positive value)."""
    if isinstance(lens_mm, bool) or not isinstance(lens_mm, (int, float)) or not float(lens_mm) > 0:
        return None
    return f"{float(lens_mm):g} mm lens"


def build_prompt(style_profile: dict, room_type: Optional[str], furniture: list[str],
                 lens_mm: Optional[float] = None) -> dict:
    """The prompt of one view and the words it was made from; ``lens_mm``: the view camera's own lens.

    Returns ``{"prompt", "room_type", "room_words", "family", "walls", "floor", "mood",
    "furniture": [types], "lens_mm", "warnings": [...]}``.
    """
    warnings: list[str] = []
    profile = style_profile or {}
    room = ROOM_WORDS.get(room_type or "unknown")
    if room is None:
        warnings.append(f"no prompt words for room type {room_type!r}; used 'room'")
        room = "room"
    family = style_family(profile)
    family_words = _words(FAMILY_WORDS, family, "style family", warnings)
    if family is None:
        warnings.append("no style family word in the rendered profile; prompt says no style")
    surf = surfaces(profile, room_type)
    wall_words = _words(MATERIAL_WORDS, surf["walls"], "wall material", warnings)
    floor_words = _words(MATERIAL_WORDS, surf["floor"], "floor material", warnings)
    mood = ((profile.get("lighting") or {}).get("mood"))
    mood_words = _words(MOOD_WORDS, mood, "light mood", warnings)
    if mood is None:
        warnings.append("no light mood in the rendered profile; prompt says 'Natural light'")
        mood_words = "Natural"
    furniture = [f for f in furniture if f and f != "unknown"][:MAX_FURNITURE]
    furniture_words = [_words(FURNITURE_WORDS, f, "furniture type", warnings) for f in furniture]

    first = f"Photorealistic interior photograph of {_article(room)} {room}"
    if family_words:
        first += f" in {family_words} style"
    parts = []
    if wall_words:
        parts.append(f"{wall_words} walls")
    if floor_words:
        parts.append(f"{floor_words} floor")
    parts += furniture_words
    sentences = [first + "."]
    if parts:
        second = ", ".join(parts)
        sentences.append(second[:1].upper() + second[1:] + ".")
    lens = lens_words(lens_mm)
    if lens is None:
        warnings.append("no camera lens for the view; prompt names no lens")
    sentences.append(f"{mood_words} {PROMPT_TAIL}" + (f", {lens}." if lens else "."))
    return {"prompt": " ".join(sentences), "room_type": room_type, "room_words": room, "family": family,
            "walls": surf["walls"], "floor": surf["floor"], "mood": mood, "furniture": furniture,
            "lens_mm": float(lens_mm) if lens else None, "warnings": warnings}
