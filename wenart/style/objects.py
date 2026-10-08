"""Object word table and the per-object word tables of the brief parser (docs/milestone10.md §4.1; track C).

What: ``OBJECT_WORDS`` maps the words of a brief phrase to one of ``OBJECTS`` (walls, accent wall, floor, ceiling,
sofa, armchair, chair, bed, cushions, throws, curtains, rug, cabinets, kitchen, worktop, furniture, coffee / dining
table, doors, handles, window frames, pots, plants, facade, roof, paving, garden, lighting ... ); the other tables
turn the words around an object into values of the style profile (material tags, furniture woods, front styles,
handles, worktops, door styles, window-frame materials, plant species and amounts, pot materials, exterior
materials, tile sizes). ``find_spans`` is the matcher all of them share.

Why: "cream pots" must colour the pots and never the walls; a bare colour phrase with no object stays the wall
colour of Milestone 3. The parser (``wenart/style/profile.py``) looks up the object of each phrase here, gives the
colours, modifiers and materials around the object word to that object only, and lists every word it does not know.
Deterministic tables only: unknown words are reported, never guessed (CLAUDE.md).

How: keywords are whole words (letters and digits are word characters, hyphens and spaces inside a keyword are
literal); at one position the longest keyword wins; matches never overlap. The slugs these tables name live in
``wenart/style/finishes.py`` and ``wenart/style/vocabulary.py``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Optional

# --------------------------------------------------------------------------
# The matcher
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Span:
    """A keyword hit: characters ``start:end`` of the lower-cased phrase, the keyword and its value."""
    start: int
    end: int
    keyword: str
    value: object


@lru_cache(maxsize=None)
def _keyword_pattern(keyword: str) -> "re.Pattern[str]":
    """The compiled whole-word pattern of a keyword (the tables hold about 700 keywords: more than ``re``'s own cache)."""
    return re.compile(r"(?<![^\W_])" + re.escape(keyword) + r"(?![^\W_])")


def find_spans(text: str, table: Iterable[tuple[str, object]], taken: Iterable[tuple[int, int]] = ()) -> list[Span]:
    """Non-overlapping whole-word keyword hits of ``text`` (lower case): earliest start first, the longest keyword at
    one start, none overlapping ``taken`` (character ranges already claimed)."""
    hits: list[Span] = []
    for keyword, value in table:
        if keyword not in text:                                    # cheap reject before the regex
            continue
        for m in _keyword_pattern(keyword).finditer(text):
            hits.append(Span(m.start(), m.end(), keyword, value))
    hits.sort(key=lambda s: (s.start, -(s.end - s.start)))
    chosen: list[Span] = []
    blocked = list(taken)
    for hit in hits:
        if any(hit.start < b_end and b_start < hit.end for b_start, b_end in blocked):
            continue
        chosen.append(hit)
        blocked.append((hit.start, hit.end))
    return chosen


def first_span(text: str, table: Iterable[tuple[str, object]], taken: Iterable[tuple[int, int]] = ()) -> Optional[Span]:
    """The first hit of ``find_spans`` (None when nothing matches)."""
    spans = find_spans(text, table, taken)
    return spans[0] if spans else None


# --------------------------------------------------------------------------
# Objects
# --------------------------------------------------------------------------

OBJECTS = ("walls", "accent_wall", "floor", "ceiling", "trim", "sofa", "armchair", "chair", "bed", "ottoman", "bench",
           "wardrobe", "desk", "nightstand", "dresser", "bookshelf", "tv_unit", "sideboard", "console_table",
           "cushions", "throws", "curtains", "rug", "cabinets", "kitchen", "worktop", "furniture", "table_coffee",
           "table_dining", "doors", "handles", "window_frames", "pots", "plants", "textiles", "accents", "wet_walls",
           "facade", "roof", "paving", "garden", "lighting")

OBJECT_WORDS: list[tuple[str, str]] = [
    # walls and surfaces
    ("accent wall", "accent_wall"), ("accent walls", "accent_wall"), ("feature wall", "accent_wall"),
    ("feature walls", "accent_wall"), ("statement wall", "accent_wall"),
    ("walls", "walls"), ("wall", "walls"), ("wallpaper", "walls"),
    ("floor", "floor"), ("floors", "floor"), ("flooring", "floor"), ("floorboards", "floor"),
    ("ceiling", "ceiling"), ("ceilings", "ceiling"),
    ("trim", "trim"), ("skirting", "trim"), ("skirting boards", "trim"), ("baseboards", "trim"),
    ("bathroom tiles", "wet_walls"), ("wall tiles", "wet_walls"), ("shower tiles", "wet_walls"),
    ("bathroom walls", "wet_walls"), ("wet walls", "wet_walls"), ("shower walls", "wet_walls"),
    ("splashback", "wet_walls"), ("backsplash", "wet_walls"), ("tiled walls", "wet_walls"),
    ("subway tiles", "wet_walls"), ("subway tile", "wet_walls"), ("metro tiles", "wet_walls"),
    ("zellige tiles", "wet_walls"), ("zellige", "wet_walls"), ("mosaic tiles", "wet_walls"),
    ("marble slab", "wet_walls"), ("marble slabs", "wet_walls"),
    # furniture
    ("corner sofa", "sofa"), ("sofa", "sofa"), ("sofas", "sofa"), ("couch", "sofa"), ("couches", "sofa"),
    ("settee", "sofa"), ("sectional", "sofa"),
    ("armchair", "armchair"), ("armchairs", "armchair"), ("lounge chair", "armchair"), ("accent chair", "armchair"),
    ("accent chairs", "armchair"),
    ("dining chair", "chair"), ("dining chairs", "chair"), ("chair", "chair"), ("chairs", "chair"),
    ("bed", "bed"), ("beds", "bed"), ("bedding", "bed"), ("bed linen", "bed"), ("duvet", "bed"), ("bedspread", "bed"),
    ("ottoman", "ottoman"), ("ottomans", "ottoman"), ("pouf", "ottoman"), ("bench", "bench"), ("benches", "bench"),
    ("wardrobe", "wardrobe"), ("wardrobes", "wardrobe"), ("desk", "desk"), ("desks", "desk"),
    ("nightstand", "nightstand"), ("nightstands", "nightstand"), ("bedside table", "nightstand"),
    ("bedside tables", "nightstand"), ("dresser", "dresser"), ("dressers", "dresser"), ("chest of drawers", "dresser"),
    ("bookshelf", "bookshelf"), ("bookshelves", "bookshelf"), ("bookcase", "bookshelf"), ("bookcases", "bookshelf"),
    ("tv unit", "tv_unit"), ("tv units", "tv_unit"), ("tv stand", "tv_unit"), ("sideboard", "sideboard"),
    ("sideboards", "sideboard"), ("console table", "console_table"), ("console", "console_table"),
    ("coffee table", "table_coffee"), ("coffee tables", "table_coffee"), ("centre table", "table_coffee"),
    ("center table", "table_coffee"), ("dining table", "table_dining"), ("dining tables", "table_dining"),
    ("furniture", "furniture"),
    # soft furnishings and decor
    ("scatter cushions", "cushions"), ("throw pillows", "cushions"), ("cushion", "cushions"), ("cushions", "cushions"),
    ("pillow", "cushions"), ("pillows", "cushions"),
    ("throw", "throws"), ("throws", "throws"), ("blanket", "throws"), ("blankets", "throws"),
    ("curtain", "curtains"), ("curtains", "curtains"), ("drapes", "curtains"), ("drapery", "curtains"),
    ("blind", "curtains"), ("blinds", "curtains"),
    ("rug", "rug"), ("rugs", "rug"), ("area rug", "rug"),
    ("textiles", "textiles"), ("textile", "textiles"), ("upholstery", "textiles"), ("soft furnishings", "textiles"),
    ("accents", "accents"), ("accent colours", "accents"), ("accent colors", "accents"), ("details", "accents"),
    ("pot", "pots"), ("pots", "pots"), ("planter", "pots"), ("planters", "pots"), ("plant pots", "pots"),
    ("indoor plants", "plants"), ("houseplants", "plants"), ("plant", "plants"), ("plants", "plants"),
    ("palms", "plants"), ("palm", "plants"), ("monstera", "plants"), ("ferns", "plants"), ("fern", "plants"),
    ("greenery", "plants"), ("foliage", "plants"), ("olive trees", "plants"), ("olive tree", "plants"),
    ("fiddle leaf fig", "plants"), ("fiddle-leaf fig", "plants"), ("fiddle leaf figs", "plants"), ("monsteras", "plants"),
    # kitchen and joinery
    ("kitchen cabinets", "cabinets"), ("kitchen units", "cabinets"), ("kitchen fronts", "cabinets"),
    ("cabinet", "cabinets"), ("cabinets", "cabinets"), ("cabinetry", "cabinets"), ("cupboards", "cabinets"),
    ("units", "cabinets"), ("fronts", "cabinets"), ("joinery", "cabinets"),
    ("kitchen", "kitchen"), ("kitchens", "kitchen"),
    ("worktop", "worktop"), ("worktops", "worktop"), ("countertop", "worktop"), ("countertops", "worktop"),
    ("counter top", "worktop"), ("benchtop", "worktop"),
    ("interior doors", "doors"), ("internal doors", "doors"), ("door", "doors"), ("doors", "doors"),
    ("handle", "handles"), ("handles", "handles"), ("knobs", "handles"), ("pulls", "handles"), ("hardware", "handles"),
    ("ironmongery", "handles"),
    ("window frame", "window_frames"), ("window frames", "window_frames"), ("windows", "window_frames"),
    ("window", "window_frames"),
    # outside
    ("exterior walls", "facade"), ("external walls", "facade"), ("outside walls", "facade"), ("facade", "facade"),
    ("facades", "facade"), ("façade", "facade"), ("cladding", "facade"),
    ("roof tiles", "roof"), ("roofing", "roof"), ("roof", "roof"), ("roofs", "roof"),
    ("paving", "paving"), ("pavers", "paving"), ("driveway", "paving"), ("patio", "paving"), ("paths", "paving"),
    ("garden", "garden"), ("lawn", "garden"), ("yard", "garden"),
    ("lighting", "lighting"), ("lamps", "lighting"),
]

# Furniture types of the building schema each object word stands for (the keys of ``furniture.by_type``).
OBJECT_TYPES: dict[str, tuple[str, ...]] = {
    "sofa": ("sofa", "sofa_corner"), "armchair": ("armchair",), "chair": ("chair",), "bed": ("bed_single", "bed_double"),
    "ottoman": ("ottoman",), "bench": ("bench",), "wardrobe": ("wardrobe",), "desk": ("desk",),
    "nightstand": ("nightstand",), "dresser": ("dresser",), "bookshelf": ("bookshelf",), "tv_unit": ("tv_unit",),
    "sideboard": ("sideboard",), "console_table": ("console_table",), "table_coffee": ("table_coffee",),
    "table_dining": ("table_dining",),
}
# Types that are upholstered: a colour is their ``fabric_colour``; for the others it is a plain ``colour``.
UPHOLSTERED = ("sofa", "armchair", "chair", "bed", "ottoman", "bench")

# Objects whose word is part of the keywords that describe them ("botanical wallpaper", "green roof"): the finish and
# material tables are searched over the attribute words and the object word together.
OBJECT_IN_KEYWORDS = frozenset(("walls", "facade", "roof", "paving", "garden", "wet_walls"))

# Words that never carry a value (an unknown word is listed, these are not): articles, joiners, size and quantity
# words the parser reads itself (many, large), finish words that every material has.
DESCRIPTORS = frozenset("""a an the of in on at with and or plus & many some several few lots lot plenty large big small
tall indoor outdoor soft plank planks board boards textured matte matt glossy gloss satin finish style look feel colour
colours color colors tone tones shade shades all every everywhere throughout also only just very one single two three
bathroom bathrooms shower showers wc cm mm x by""".split())
MODIFIER_WORDS = frozenset(("light", "dark", "pale", "deep", "warm", "cool", "muted"))
# Textile material words: known, but they name no slot of the profile (the default fabric is fabric_linen), so an object
# phrase that holds one together with a colour ("cream linen cushions") does not list them as unknown.
TEXTILE_WORDS = frozenset(("linen", "velvet", "cotton", "wool", "woollen", "sheer", "boucle", "bouclé", "knitted",
                           "woven", "silk", "leather", "faux", "fur", "fabric", "upholstered"))
AMOUNT_WORDS = {"many": "many", "lots": "many", "plenty": "many", "lot": "many", "several": "some", "some": "some",
                "few": "few"}

# Style words beyond the families of vocabulary.STYLE_FAMILIES: ``natural`` = light wood, linen, rattan accents
# (docs/milestone10.md §4.10); its only effect on the profile is the furniture wood when the brief names none.
STYLE_TAGS: dict[str, dict] = {"natural": {"furniture_wood": "wood_veneer_oak_light",
                                           "reason": "natural: light wood, linen, rattan accents"}}

# --------------------------------------------------------------------------
# Materials and tags around furniture and decor
# --------------------------------------------------------------------------

# Material tags the fit prefers (building schema ``design.material_tags``).
MATERIAL_TAG_WORDS: list[tuple[str, str]] = [
    ("glass", "glass"), ("glazed", "glass"), ("wooden", "wood"), ("wood", "wood"), ("timber", "wood"), ("oak", "wood"),
    ("walnut", "wood"), ("metal", "metal"), ("steel", "metal"), ("brass", "metal"), ("chrome", "metal"), ("iron", "metal"),
    ("fabric", "fabric"), ("upholstered", "fabric"), ("linen", "fabric"), ("velvet", "fabric"), ("boucle", "fabric"),
    ("bouclé", "fabric"), ("cotton", "fabric"), ("wool", "fabric"), ("rattan", "rattan"), ("wicker", "rattan"),
    ("cane", "rattan"), ("marble", "marble"),
]

# Furniture wood: (wood type word, tone words) -> a FURNITURE_MATERIALS ``wood_veneer_*`` slug. Generic "wood" with a
# light / natural tone is light oak; dark is walnut; plain oak keeps Milestone 6's oak veneer.
WOOD_TYPE_WORDS = ("oak", "walnut", "ash", "maple", "birch", "beech", "teak", "cherry", "wood", "wooden", "timber")
WOOD_TONE_LIGHT = ("light", "pale", "natural", "blonde", "bleached", "white")
WOOD_TONE_DARK = ("dark", "black", "smoked", "deep")


def wood_slug(words: Iterable[str]) -> Optional[str]:
    """The ``wood_veneer_*`` slug a phrase's words name (``natural light wood``, ``dark oak``, ``walnut``), None when
    no wood type word is present."""
    ws = [w.lower() for w in words]
    kinds = [w for w in ws if w in WOOD_TYPE_WORDS]
    if not kinds:
        return None
    light = any(w in WOOD_TONE_LIGHT for w in ws)
    dark = any(w in WOOD_TONE_DARK for w in ws)
    kind = kinds[0]
    if kind == "walnut":
        return "wood_veneer_walnut"
    if kind == "ash":
        return "wood_veneer_ash"
    if kind in ("maple", "birch", "beech"):
        return "wood_veneer_maple"
    if kind == "teak":
        return "wood_veneer_teak"
    if kind == "cherry":
        return "wood_veneer_cherry"
    if kind == "oak":
        return "wood_veneer_black_oak" if dark else ("wood_veneer_oak_light" if light else "wood_veneer_oak")
    return "wood_veneer_walnut" if dark else ("wood_veneer_oak_light" if light else "wood_veneer_oak")


# --------------------------------------------------------------------------
# Cabinets, worktops, handles, doors, window frames
# --------------------------------------------------------------------------

CABINET_FRONT_WORDS: list[tuple[str, str]] = [
    ("handleless", "flat"), ("slab", "flat"), ("flat", "flat"), ("shaker", "shaker"), ("slatted", "slatted"),
    ("fluted", "slatted"), ("ribbed", "slatted"), ("slat", "slatted"), ("glass front", "glass"), ("glass fronts", "glass"),
    ("glazed fronts", "glass"), ("glass", "glass"),
]
WORKTOP_WORDS: list[tuple[str, str]] = [
    ("stainless steel", "steel"), ("steel", "steel"), ("stainless", "steel"), ("terrazzo", "terrazzo"),
    ("butcher block", "wood"), ("wooden", "wood"), ("wood", "wood"), ("oak", "wood"), ("walnut", "wood"),
    ("quartz", "stone"), ("granite", "stone"), ("marble", "stone"), ("stone", "stone"), ("concrete", "stone"),
]
HANDLE_WORDS: list[tuple[str, str]] = [
    ("brushed steel", "brushed_steel"), ("stainless steel", "brushed_steel"), ("stainless", "brushed_steel"),
    ("chrome", "brushed_steel"), ("steel", "brushed_steel"), ("black", "black"), ("brass", "brass"), ("gold", "brass"),
]
DOOR_STYLE_WORDS: list[tuple[str, str]] = [
    ("shaker", "shaker_panel"), ("panelled", "shaker_panel"), ("paneled", "shaker_panel"), ("panel", "shaker_panel"),
    ("glazed", "glazed"), ("glass", "glazed"), ("pocket", "pocket"), ("sliding", "sliding"), ("barn", "barn"),
    ("double", "double"), ("entrance", "entrance"), ("front", "entrance"), ("flush", "flush"), ("slab", "flush"),
    ("plain", "flush"),
]
# Door leaf materials: wood words keep the floor-tone slugs of the vocabulary, steel and aluminium are the flat frame
# metals; a colour makes a painted leaf.
DOOR_WOOD_WORDS: list[tuple[str, str]] = [("oak", "wood_oak_light"), ("walnut", "wood_walnut"), ("wooden", "wood_oak_light"),
                                          ("wood", "wood_oak_light"), ("timber", "wood_oak_light"), ("steel", "steel_black"),
                                          ("aluminium", "aluminium_anthracite"), ("aluminum", "aluminium_anthracite")]
FRAME_WORDS: list[tuple[str, str]] = [
    ("upvc", "pvc_white"), ("pvc", "pvc_white"), ("plastic", "pvc_white"), ("aluminium", "aluminium_anthracite"),
    ("aluminum", "aluminium_anthracite"), ("steel", "steel_black"), ("oak", "oak"), ("wooden", "oak"), ("wood", "oak"),
    ("timber", "oak"), ("painted", "painted_metal_white"),
]

# --------------------------------------------------------------------------
# Wet walls: tile words, sizes, grout
# --------------------------------------------------------------------------

WET_WALL_WORDS: list[tuple[str, str]] = [
    ("subway", "tiles_subway"), ("metro", "tiles_subway"), ("brick tiles", "tiles_subway"),
    ("large format", "tiles_large_porcelain"), ("large-format", "tiles_large_porcelain"),
    ("large porcelain", "tiles_large_porcelain"), ("porcelain", "tiles_large_porcelain"),
    ("zellige", "tiles_zellige"), ("hexagon", "tiles_hexagon"), ("hexagonal", "tiles_hexagon"), ("hex", "tiles_hexagon"),
    ("mosaic", "tiles_mosaic"), ("marble slab", "marble_slab"), ("marble slabs", "marble_slab"), ("marble", "marble_slab"),
    ("cement tiles", "tiles_cement"), ("cement tile", "tiles_cement"), ("encaustic", "tiles_cement"),
]
TILE_SIZE = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:x|×|by)\s*(\d+(?:[.,]\d+)?)\s*(cm|mm|m)?\b")
TILE_SIZE_UNITS = {"mm": 0.001, "cm": 0.01, "m": 1.0, None: 0.01}      # no unit: centimetres (tile sizes)


def tile_sizes(text: str) -> list[tuple[list[float], tuple[int, int]]]:
    """``[(tile_size_m [w, h], (start, end))]`` of ``60x120``, ``7.5 x 15 cm``, ``10 by 10 cm`` in a phrase."""
    out = []
    for m in TILE_SIZE.finditer(text):
        k = TILE_SIZE_UNITS[m.group(3)]
        out.append(([round(float(m.group(1).replace(",", ".")) * k, 4), round(float(m.group(2).replace(",", ".")) * k, 4)],
                    (m.start(), m.end())))
    return out


# --------------------------------------------------------------------------
# Plants and pots
# --------------------------------------------------------------------------

PLANT_WORDS: list[tuple[str, str]] = [
    ("fiddle leaf fig", "fiddle_leaf_fig"), ("fiddle-leaf fig", "fiddle_leaf_fig"), ("fiddle leaf", "fiddle_leaf_fig"),
    ("fiddle-leaf", "fiddle_leaf_fig"), ("palms", "palm"), ("palm", "palm"), ("monsteras", "monstera"),
    ("monstera", "monstera"), ("olive trees", "olive"), ("olive tree", "olive"), ("olives", "olive"), ("olive", "olive"),
    ("ferns", "fern"), ("fern", "fern"),
]
POT_MATERIAL_WORDS: list[tuple[str, str]] = [
    ("rattan", "rattan"), ("wicker", "rattan"), ("basket", "rattan"), ("woven", "rattan"), ("ceramic", "ceramic"),
    ("porcelain", "ceramic"), ("terracotta", "terracotta"), ("clay", "terracotta"), ("concrete", "concrete"),
    ("metal", "metal"), ("steel", "metal"),
]

# --------------------------------------------------------------------------
# Exterior words per slot (docs/milestone10.md §4.8); the slugs are finishes.MATERIALS
# --------------------------------------------------------------------------

EXTERIOR_WORDS: dict[str, list[tuple[str, str]]] = {
    "facade": [("fibre cement", "fibre_cement"), ("fiber cement", "fibre_cement"), ("cement board", "fibre_cement"),
               ("cement boards", "fibre_cement"), ("white brick", "brick_white"), ("painted brick", "brick_white"),
               ("grey brick", "brick_grey"), ("gray brick", "brick_grey"), ("reclaimed brick", "brick_reclaimed"),
               ("red brick", "brick_red"), ("brick", "brick_red"), ("stone cladding", "stone_cladding"),
               ("natural stone", "stone_cladding"), ("stone", "stone_cladding"), ("timber", "wood_cladding"),
               ("wood cladding", "wood_cladding"), ("wooden", "wood_cladding"), ("wood", "wood_cladding"),
               ("cedar", "wood_cladding"), ("larch", "wood_cladding"), ("smooth render", "render"),
               ("render", "render"), ("rendered", "render"), ("plaster", "render"), ("stucco", "render")],
    "roof": [("clay tiles", "clay_tiles"), ("clay", "clay_tiles"), ("terracotta", "clay_tiles"),
             ("concrete tiles", "concrete_tiles"), ("concrete tile", "concrete_tiles"), ("slate", "slate"),
             ("standing seam", "standing_seam"), ("zinc", "standing_seam"), ("metal", "standing_seam"),
             ("aluminium", "standing_seam"), ("green roof", "green_roof"), ("sedum", "green_roof"),
             ("living roof", "green_roof")],
    "paving": [("gravel", "gravel"), ("decking", "decking"), ("deck", "decking"), ("flagstone", "paving_stone"),
               ("natural stone", "paving_stone"), ("stone", "paving_stone"), ("paving", "paving"), ("pavers", "paving"),
               ("concrete", "paving")],
    "garden": [("lawn", "grass"), ("grass", "grass"), ("gravel", "gravel"), ("decking", "decking"), ("deck", "decking")],
}
# Slots a phrase object word fills in the style text (the others come from the frame / door tables).
OBJECT_EXTERIOR_SLOT = {"facade": "facade", "roof": "roof", "paving": "paving", "garden": "garden"}

# Hints for words that are known but need more to be applied (shown instead of a bare "unmatched").
HINTS: dict[str, str] = {
    "wallpaper": "a wallpaper needs a pattern word: stripe, botanical, geometric, check, herringbone or grasscloth",
    "linen": "textile materials name no slot (fabric_linen is the default fabric)",
    "textiles": "textile words name no slot unless they carry a colour",
}

# The accent wall rule recorded with ``wall_accent`` (docs/milestone10.md §4.1).
ACCENT_ROOM_TYPES = ("living", "bedroom")
ACCENT_RULE = ("one accent wall per living room and bedroom: the wall behind the sofa or the bed head, "
               "else the longest wall without a window")
