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

Milestone 10 (docs/milestone10.md §4; track F): the wall and floor words
carry the profile's colour phrase where the slot has one ("warm greige
smooth painted walls"; a slug never carries a colour, §1.6b row 14); a
child's room (``room_subtype``) has its own room words; ``decor`` (decor
types of the view, optional) adds up to ``MAX_DECOR`` of ``DECOR_WORDS``
after the furniture. Both are optional arguments, so a caller without them
gets the Milestone 9 prompt.
"""
from __future__ import annotations

from typing import Optional

from wenart.style import vocabulary as VOC

MAX_FURNITURE = 8
MAX_DECOR = 4                     # Milestone 10: decor words after the furniture

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
    "mirror": "mirror glass",                    # Milestone 9: the mirror decor
    # Milestone 10 (docs/milestone10.md §4.3, §4.8; every slug of wenart/style/finishes.py). Colours are not in these words:
    # a slug never carries a colour, the profile's colour name is separate.
    # wall finishes
    "paint": "smooth painted",
    "lime_plaster": "soft lime plaster",
    "microcement": "polished microcement",
    "venetian_plaster": "glossy Venetian plaster",
    "wood_slat": "wood slat panelled",
    "stone_wall_ledgestone": "stacked ledgestone",
    "stone_wall_rubble": "rough rubble stone",
    "stone_wall_ashlar": "cut ashlar stone",
    "stone_wall_slate": "dark slate stone",
    "brick_red": "exposed red brick",
    "brick_white": "white painted brick",
    "brick_grey": "grey brick",
    "brick_reclaimed": "reclaimed mixed brick",
    "concrete_exposed": "exposed board-marked concrete",
    "wallpaper_stripe": "striped wallpapered",
    "wallpaper_botanical": "botanical wallpapered",
    "wallpaper_geometric": "geometric wallpapered",
    "wallpaper_check": "checked wallpapered",
    "wallpaper_herringbone": "herringbone wallpapered",
    "wallpaper_grasscloth": "grasscloth wallpapered",
    # wet walls and tile floors
    "tiles_subway": "subway tile",
    "tiles_large_porcelain": "large-format porcelain tile",
    "tiles_zellige": "handmade zellige tile",
    "tiles_hexagon": "hexagon tile",
    "tiles_mosaic": "small mosaic tile",
    "tiles_cement": "matt cement tile",
    "marble_slab": "veined marble slab",
    # floors
    "wood_oak_natural": "natural oak",
    "wood_oak_whitewashed": "whitewashed oak",
    "wood_oak_smoked": "dark smoked oak",
    "wood_oak_grey": "grey oak",
    "wood_wide_plank": "wide plank wood",
    "wood_herringbone_light": "light herringbone parquet",
    "wood_herringbone_mid": "mid-tone herringbone parquet",
    "wood_herringbone_dark": "dark herringbone parquet",
    "wood_chevron_light": "light chevron parquet",
    "wood_chevron_mid": "mid-tone chevron parquet",
    "wood_chevron_dark": "dark chevron parquet",
    "wood_ash": "pale ash wood",
    "wood_bamboo": "bamboo",
    "terrazzo": "speckled terrazzo",
    "travertine": "honed travertine",
    "limestone": "pale limestone",
    "slate_floor": "dark slate",
    "vinyl": "smooth vinyl",
    "cork": "cork",
    "carpet_wool": "wool carpet",
    "sisal": "woven sisal",
    # window frames
    "pvc_white": "white PVC",
    "aluminium_anthracite": "anthracite aluminium",
    "steel_black": "black steel",
    "dark_bronze": "dark bronze metal",
    "oak": "oak",
    # exterior
    "render": "smooth render",
    "stone_cladding": "stone cladding",
    "wood_cladding": "timber cladding",
    "fibre_cement": "fibre cement board",
    "clay_tiles": "clay roof tile",
    "concrete_tiles": "concrete roof tile",
    "slate": "slate roof",
    "standing_seam": "standing seam metal",
    "green_roof": "green sedum roof",
    "paving": "concrete paving",
    "paving_stone": "natural stone paving",
    "gravel": "gravel",
    "grass": "green lawn",
    "decking": "composite decking",
    "rattan": "woven rattan",
    # furniture woods and handles
    "wood_veneer_oak_light": "light natural oak veneer",
    "wood_veneer_ash": "ash veneer",
    "wood_veneer_maple": "pale maple veneer",
    "wood_veneer_teak": "teak veneer",
    "wood_veneer_black_oak": "dark oak veneer",
    "wood_veneer_cherry": "cherry veneer",
    "metal_black": "black metal",
    "metal_brass": "brass",
}

# Lighting moods of vocabulary.LIGHTING, written to be followed by "light".
MOOD_WORDS: dict[str, str] = {
    "warm daylight": "Warm daytime",
    "cool daylight": "Cool daytime",
    "golden evening": "Golden evening",
    "overcast": "Soft overcast",
    "night": "Dim night",
    "bright noon": "Bright midday",              # Milestone 10 (docs/milestone10.md §4.9)
    "blue hour": "Cool blue-hour",
    "cloudy soft": "Soft cloudy",
    "interior evening": "Warm lamp-lit evening",
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
    # Milestone 10 (docs/milestone10.md §1.1)
    "sofa_corner": "corner sofa",
    "chaise": "chaise longue",
    "ottoman": "ottoman",
    "bench": "bench",
    "bar_stool": "bar stool",
    "office_chair": "office chair",
    "console_table": "console table",
    "crib": "crib",
    "bunk_bed": "bunk bed",
    "sideboard": "sideboard",
    "shoe_cabinet": "shoe cabinet",
    "display_cabinet": "glass display cabinet",
    "tall_cabinet": "tall cabinet",
    "wall_cabinet": "wall cabinets",
}

# Decor types of the building schema (docs/milestone10.md §4.6; Milestone 8/9 types too), plural where several
# stand in a room.
DECOR_WORDS: dict[str, str] = {
    "cushion": "cushions", "book_set": "books", "plant": "potted plant", "rug": "rug", "wall_art": "framed wall art",
    "vase": "vase", "bowl": "bowl", "plant_small": "small plant", "table_lamp": "table lamp", "mirror": "wall mirror",
    "curtain": "linen curtains", "blind": "roller blind", "throw": "throw blanket", "books": "stacked books",
    "candle": "candles", "basket": "woven basket", "tray": "tray", "clock": "wall clock", "sculpture": "sculpture",
    "plant_large": "large indoor plant", "pendant_light": "pendant light", "ceiling_light": "ceiling light",
}
# rooms[].room_subtype words (Milestone 10: a child's room holds cribs and bunk beds).
SUBTYPE_WORDS: dict[str, str] = {"child": "child's bedroom"}

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


def _slot_colour(profile: dict, slot: str) -> Optional[str]:
    entry = (profile or {}).get(slot)
    colour = entry.get("colour") if isinstance(entry, dict) else None
    return colour if isinstance(colour, str) and colour.strip() else None


def surfaces(profile: dict, room_type: Optional[str]) -> dict:
    """``{"walls": slug, "floor": slug, "wet": bool, "walls_colour", "floor_colour"}``: the wet-room slots for
    bathrooms, WCs and kitchens; Milestone 10: the colour phrase of the slot used (None when it has none)."""
    wet = room_type in VOC.WET_ROOM_TYPES
    walls = _slot(profile, "wet_walls") if wet else None
    floor = _slot(profile, "wet_floor") if wet else None
    wall_slot = "wet_walls" if walls else "walls"
    floor_slot = "wet_floor" if floor else "floor"
    return {"walls": walls or _slot(profile, "walls"), "floor": floor or _slot(profile, "floor"), "wet": wet,
            "walls_colour": _slot_colour(profile, wall_slot), "floor_colour": _slot_colour(profile, floor_slot)}


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
                 lens_mm: Optional[float] = None, room_subtype: Optional[str] = None,
                 decor: Optional[list[str]] = None) -> dict:
    """The prompt of one view and the words it was made from; ``lens_mm``: the view camera's own lens;
    Milestone 10: ``room_subtype`` (``child``) and ``decor`` (decor types of the view, deduplicated, at most
    ``MAX_DECOR``).

    Returns ``{"prompt", "room_type", "room_words", "family", "walls", "floor", "mood",
    "furniture": [types], "lens_mm", "warnings": [...]}``.
    """
    warnings: list[str] = []
    profile = style_profile or {}
    room = ROOM_WORDS.get(room_type or "unknown")
    if room is None:
        warnings.append(f"no prompt words for room type {room_type!r}; used 'room'")
        room = "room"
    if room_subtype and room_type == "bedroom":
        room = _words(SUBTYPE_WORDS, room_subtype, "room subtype", warnings) or room
    family = style_family(profile)
    family_words = _words(FAMILY_WORDS, family, "style family", warnings)
    if family is None:
        warnings.append("no style family word in the rendered profile; prompt says no style")
    surf = surfaces(profile, room_type)
    wall_words = _words(MATERIAL_WORDS, surf["walls"], "wall material", warnings)
    floor_words = _words(MATERIAL_WORDS, surf["floor"], "floor material", warnings)
    if wall_words and surf["walls_colour"]:                     # Milestone 10: the slot's colour phrase
        wall_words = f"{surf['walls_colour']} {wall_words}"
    if floor_words and surf["floor_colour"]:
        floor_words = f"{surf['floor_colour']} {floor_words}"
    mood = ((profile.get("lighting") or {}).get("mood"))
    mood_words = _words(MOOD_WORDS, mood, "light mood", warnings)
    if mood is None:
        warnings.append("no light mood in the rendered profile; prompt says 'Natural light'")
        mood_words = "Natural"
    furniture = [f for f in furniture if f and f != "unknown"][:MAX_FURNITURE]
    furniture_words = [_words(FURNITURE_WORDS, f, "furniture type", warnings) for f in furniture]
    decor_types: list[str] = []
    for d in decor or []:
        if d and d not in decor_types:
            decor_types.append(d)
    decor_types = decor_types[:MAX_DECOR]
    decor_words = [_words(DECOR_WORDS, d, "decor type", warnings) for d in decor_types]

    first = f"Photorealistic interior photograph of {_article(room)} {room}"
    if family_words:
        first += f" in {family_words} style"
    parts = []
    if wall_words:
        parts.append(f"{wall_words} walls")
    if floor_words:
        parts.append(f"{floor_words} floor")
    parts += furniture_words + decor_words
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
            "decor": decor_types, "lens_mm": float(lens_mm) if lens else None, "warnings": warnings}
