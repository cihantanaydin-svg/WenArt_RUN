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
  ``MATERIAL_WORDS``; Milestone 10: the walls' ``colour`` (a phrase of
  ``wenart.style.colours``, "warm greige walls": ``surface_words``) and, in a room
  type the profile's ``wall_accent`` names, "one <colour> <material> accent
  wall" (``accent_words``); a lamps-on mood (``vocabulary.LIGHTING[mood]
  ["lamps_on"]``) says the light comes from the lamps;
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
    "mirror": "mirror glass",                    # Milestone 9: the mirror decor
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
    """``{"walls": slug, "walls_colour": phrase | None, "floor": slug, "wet": bool}``: the wet-room slots for
    bathrooms, WCs and kitchens; the colour is the one of the slot that gave the wall material."""
    wet = room_type in VOC.WET_ROOM_TYPES
    walls = _slot(profile, "wet_walls") if wet else None
    floor = _slot(profile, "wet_floor") if wet else None
    wall_slot = "wet_walls" if walls else "walls"
    return {"walls": walls or _slot(profile, "walls"), "walls_colour": _slot_colour(profile, wall_slot),
            "floor": floor or _slot(profile, "floor"), "wet": wet}


# Milestone 10 (docs/milestone10.md §1.4, §4.1): finishes whose look is the colour itself. Words of this module's own
# (the style tables of ``MATERIAL_WORDS`` are another track's); a slug in ``MATERIAL_WORDS`` wins.
COLOUR_SURFACE_WORDS: dict[str, str] = {
    "paint": "painted",
    "lime_plaster": "lime plaster",
    "microcement": "microcement",
    "venetian_plaster": "polished Venetian plaster",
}
LAMPS_TAIL = ("light from the lit lamps and the last daylight outside the windows, soft natural shadows, realistic "
              "materials and textures, sharp focus")


def colour_phrase(colour) -> Optional[str]:
    """A style colour phrase as prompt words: its canonical form when ``wenart.style.colours`` knows it ("Sage
    Green" -> "sage"), else the phrase as written, lower case (an unknown phrase is not guessed at)."""
    if not isinstance(colour, str) or not colour.strip():
        return None
    try:
        from wenart.style import colours as COL
        canonical = COL.canonical_phrase(colour)
    except (ImportError, AttributeError, TypeError, ValueError):
        canonical = None
    return str(canonical or colour).strip().lower().replace("_", " ")


def surface_words(slug, colour, what: str, warnings: list, table: Optional[dict] = None) -> Optional[str]:
    """Words of a wall finish with its colour in front: ``paint`` + "warm greige" -> "warm greige painted". The
    material words come from ``table`` (default ``MATERIAL_WORDS``), then ``COLOUR_SURFACE_WORDS``; a slug in
    neither is a warning and is used as plain words. A colour already inside the material words is not said
    twice."""
    if slug is None:
        words = None
    else:
        table = MATERIAL_WORDS if table is None else table
        words = table.get(slug) or COLOUR_SURFACE_WORDS.get(slug)
        if words is None:
            warnings.append(f"no prompt words for {what} {slug!r}; used the slug")
            words = str(slug).replace("_", " ")
    cw = colour_phrase(colour)
    if cw and words and cw not in words.lower():
        return f"{cw} {words}"
    return words or cw


def accent_words(profile: dict, room_type: Optional[str], warnings: list) -> Optional[str]:
    """``one terracotta painted accent wall`` when the profile's ``wall_accent`` names this room type, else None."""
    acc = (profile or {}).get("wall_accent")
    if not isinstance(acc, dict) or not acc.get("material"):
        return None
    if room_type not in (acc.get("room_types") or ()):
        return None
    words = surface_words(acc["material"], acc.get("colour"), "accent wall material", warnings)
    return f"one {words} accent wall" if words else None


def lamps_on(mood) -> bool:
    """True for a lighting mood whose lamps are on (``vocabulary.LIGHTING[mood]["lamps_on"]``, Milestone 10)."""
    entry = (VOC.LIGHTING or {}).get(mood) if mood is not None else None
    return bool(isinstance(entry, dict) and entry.get("lamps_on"))


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

    Returns ``{"prompt", "room_type", "room_words", "family", "walls", "walls_colour", "accent", "floor",
    "mood", "lamps_on", "furniture": [types], "lens_mm", "warnings": [...]}``.
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
    wall_words = surface_words(surf["walls"], surf["walls_colour"], "wall material", warnings)
    accent = accent_words(profile, room_type, warnings)
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
    if accent:
        parts.append(accent)
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
    tail = LAMPS_TAIL if lamps_on(mood) else PROMPT_TAIL
    sentences.append(f"{mood_words} {tail}" + (f", {lens}." if lens else "."))
    return {"prompt": " ".join(sentences), "room_type": room_type, "room_words": room, "family": family,
            "walls": surf["walls"], "walls_colour": surf["walls_colour"], "accent": accent, "floor": surf["floor"],
            "mood": mood, "lamps_on": lamps_on(mood), "furniture": furniture,
            "lens_mm": float(lens_mm) if lens else None, "warnings": warnings}


# --------------------------------------------------------------------------
# Exterior views (Milestone 10, docs/milestone10.md §3.3 items 3 and 5, §4.8)
# --------------------------------------------------------------------------
#
# What: the prompt of an exterior view is built from the outside looks the build resolved
# (``scene manifest exterior_looks``: per slot ``{material, colour, source, assumed, reason}``), not from the
# interior profile: "Photorealistic architectural photograph of a house exterior in {family} style, seen
# {view}. {colour} {facade words} facade, {roof words} roof, {frame words} window frames, {paving} and {garden}.
# {mood} sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus,
# {lens} mm lens."
#
# Why: the interior tables say "walls" and "floor"; an outside view needs facade, roof, frames and ground, and
# its light comes from the sky, not "through the windows".
#
# How: slugs of ``wenart.blender.exterior`` (the E-owned ``EXTERIOR_WORDS`` / ``EXTERIOR_FALLBACK``) and of the
# M10 vocabulary go through the tables below; ``brick_*``, ``painted:<colour>`` and ``render:<colour>`` are
# built from their colour word; a slug the tables do not know is used as plain words and listed in ``warnings``
# (never silently), exactly as the interior prompt does.

# Material slugs of the outside slots, written to be followed by "facade", "roof", "window frames" or the like.
EXTERIOR_MATERIAL_WORDS: dict[str, str] = {
    # facade
    "render": "smooth rendered",
    "plaster_exterior": "grey exterior plaster",
    "fibre_cement": "fibre-cement board",
    "stone_cladding": "natural stone clad",
    "wood_cladding": "timber clad",
    "concrete_exposed": "exposed concrete",
    "brick": "exposed red brick",
    "brick_red": "red brick",
    "paint": "painted",
    "microcement": "microcement",
    # roof
    "clay_tiles": "clay tile",
    "concrete_tiles": "concrete tile",
    "slate": "slate",
    "standing_seam": "standing-seam metal",
    "green_roof": "green sedum",
    # window frames and doors
    "pvc": "white PVC",
    "pvc_white": "white PVC",
    "aluminium": "aluminium",
    "aluminium_anthracite": "anthracite aluminium",
    "steel": "steel",
    "steel_black": "black steel",
    "dark_bronze": "dark bronze",
    "oak": "oak",
    "glass": "glass",
    # ground
    "paving": "concrete paver",
    "gravel": "gravel",
    "decking": "timber decking",
    "stone": "natural stone",
    "grass": "lawn",
    "concrete": "concrete",
    "soil": "bare soil",
}
# The noun that follows the words of a slot.
EXTERIOR_SLOT_NOUN: dict[str, str] = {
    "facade": "facade",
    "roof": "roof",
    "window_frame": "window frames",
    "door": "front door",
    "paving": "paving",
    "garden": "garden",
}
# Slots named in the prompt, in this order (the door and the ground are short clauses at the end).
EXTERIOR_PROMPT_SLOTS = ("facade", "roof", "window_frame", "door", "paving", "garden")
# Lighting moods of vocabulary.LIGHTING, written for an outside view (sun and sky, not "through the windows").
EXTERIOR_MOOD_WORDS: dict[str, str] = {
    "warm daylight": "Warm daytime sunlight under a clear sky",
    "cool daylight": "Cool daytime sunlight under a clear sky",
    "golden evening": "Golden evening sunlight low over the roofs",
    "overcast": "Soft overcast daylight under a grey sky",
    "night": "Dim night light with a dark blue sky",
    "bright noon": "Bright noon sunlight under a clear sky",
    "blue hour": "Soft blue-hour light after sunset",
    "cloudy soft": "Soft cloudy daylight under a pale sky",
    "interior evening": "Dusk light with warm lamps lit behind the windows",
}
EXTERIOR_TAIL = "soft natural shadows, realistic materials and textures, sharp focus"
# Camera views of the scene manifest (``view``): how the picture is taken.
EXTERIOR_VIEW_WORDS: dict[str, str] = {
    "corner": "from a corner of the plot at eye level, two facades in view",
    "aerial": "in a three-quarter aerial view from above, roof and two facades in view",
    "elevation": "straight on from the front, one facade in view",
}
EXTERIOR_DEFAULT_VIEW = "from outside, two facades in view"


def exterior_material_words(slug, colour=None, warnings: Optional[list] = None) -> Optional[str]:
    """The words of one outside material slug (plus its colour name), or None for no slug.

    ``brick_<variant>`` -> "<variant> brick", ``painted:<colour>`` -> "<colour> painted", ``render:<colour>`` ->
    "<colour> smooth rendered"; a plain slug goes through ``EXTERIOR_MATERIAL_WORDS``, then the interior
    ``MATERIAL_WORDS`` (a window frame or door that takes the inside look). A slug no table knows is used as plain
    words and listed in ``warnings``. The colour name goes in front unless the material words already hold it."""
    if not slug:
        return None
    slug = str(slug)
    inline = None
    if slug in EXTERIOR_MATERIAL_WORDS:
        words = EXTERIOR_MATERIAL_WORDS[slug]
    elif slug.startswith("painted:") or slug.startswith("render:"):
        head, _, tail = slug.partition(":")
        inline = tail.replace("_", " ").strip() or None
        words = "painted" if head == "painted" else "smooth rendered"
    elif slug.startswith("brick_"):
        words = slug[len("brick_"):].replace("_", " ") + " brick"
    elif slug in MATERIAL_WORDS:
        words = MATERIAL_WORDS[slug]
    else:
        if warnings is not None:
            warnings.append(f"no prompt words for exterior material {slug!r}; used the slug")
        words = slug.replace("_", " ").replace(":", " ")
    name = inline or (str(colour).replace("_", " ").strip() if colour else None)
    if name and name.lower() not in words.lower():
        words = f"{name} {words}"
    return words


def exterior_mood_words(mood, warnings: Optional[list] = None) -> str:
    """The light sentence start for a lighting mood of the style profile (``EXTERIOR_MOOD_WORDS``; a mood only
    ``MOOD_WORDS`` knows becomes "<words> light"; no mood = "Natural daylight", listed in ``warnings``)."""
    if mood is None:
        if warnings is not None:
            warnings.append("no light mood in the rendered profile; exterior prompt says 'Natural daylight'")
        return "Natural daylight under a clear sky"
    if mood in EXTERIOR_MOOD_WORDS:
        return EXTERIOR_MOOD_WORDS[mood]
    if mood in MOOD_WORDS:
        return f"{MOOD_WORDS[mood]} light"
    if warnings is not None:
        warnings.append(f"no prompt words for light mood {mood!r}; used the slug")
    return f"{str(mood).replace('_', ' ').capitalize()} light"


def exterior_look_words(looks: Optional[dict], warnings: list) -> dict:
    """``{slot: words}`` of the outside looks (a scene manifest ``exterior_looks`` block) for the slots of
    ``EXTERIOR_PROMPT_SLOTS``, with the slot noun ("smooth rendered facade"). A slot without a look is left out;
    a non-dict entry is a warning."""
    out: dict = {}
    for slot in EXTERIOR_PROMPT_SLOTS:
        look = (looks or {}).get(slot)
        if look is None:
            continue
        if not isinstance(look, dict):
            warnings.append(f"exterior look {slot!r} is not a record; left out of the prompt")
            continue
        words = exterior_material_words(look.get("material"), look.get("colour"), warnings)
        if words:
            out[slot] = f"{words} {EXTERIOR_SLOT_NOUN[slot]}"
    return out


def build_exterior_prompt(style_profile: dict, exterior_looks: Optional[dict], lens_mm: Optional[float] = None,
                          view: Optional[str] = None) -> dict:
    """The prompt of one exterior view and the words it was made from.

    ``exterior_looks``: the scene manifest's block (``{slot: {material, colour, ...}}``); ``view``: the camera's
    ``view`` (corner / aerial / elevation, else a neutral phrase); ``lens_mm``: the camera's own lens.

    Returns ``{"prompt", "view_kind": "exterior", "view", "family", "mood", "looks": {slot: words}, "lens_mm",
    "warnings": [...]}``."""
    warnings: list[str] = []
    profile = style_profile or {}
    family = style_family(profile)
    family_words = _words(FAMILY_WORDS, family, "style family", warnings)
    if family is None:
        warnings.append("no style family word in the rendered profile; exterior prompt says no style")
    mood = ((profile.get("lighting") or {}).get("mood"))
    mood_words = exterior_mood_words(mood, warnings)
    if not exterior_looks:
        warnings.append("no exterior looks in the scene manifest; the prompt names no material")
    words = exterior_look_words(exterior_looks, warnings)
    view_words = EXTERIOR_VIEW_WORDS.get(view) if view else None
    if view and view_words is None:
        warnings.append(f"no prompt words for exterior view {view!r}; used a neutral phrase")
    first = "Photorealistic architectural photograph of a house exterior"
    if family_words:
        first += f" in {family_words} style"
    first += f", seen {view_words or EXTERIOR_DEFAULT_VIEW}."
    sentences = [first]
    building = [words[s] for s in ("facade", "roof", "window_frame") if s in words]
    if building:
        second = ", ".join(building)
        sentences.append(second[:1].upper() + second[1:] + ".")
    ground = [words[s] for s in ("door", "paving", "garden") if s in words]
    if ground:
        third = ", ".join(ground)
        sentences.append(third[:1].upper() + third[1:] + ".")
    lens = lens_words(lens_mm)
    if lens is None:
        warnings.append("no camera lens for the view; prompt names no lens")
    sentences.append(f"{mood_words}, {EXTERIOR_TAIL}" + (f", {lens}." if lens else "."))
    return {"prompt": " ".join(sentences), "view_kind": "exterior", "view": view, "family": family, "mood": mood,
            "looks": words, "lens_mm": float(lens_mm) if lens else None, "warnings": warnings}
