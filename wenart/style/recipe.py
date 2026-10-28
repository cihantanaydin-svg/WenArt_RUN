"""What a good room of a type and style holds, read from the reference photos (27 Oct 2026, lesson UL42; user: "find
a way that ai have an idea what is a good room looks like").

What:

- ``photo_schema(interior)``: the strict answer of one reference photo: the layers it shows (``INTERIOR_LAYERS``: a
  rug, curtains, wall art (count), plants (count), a pendant, a floor lamp, table lamps (count), cushions, a throw,
  styled surfaces, bedding layers, an accent wall, panelling, a ceiling feature ...; ``OUTDOOR_LAYERS``: a lounge
  set, a dining set, planters (count), an outdoor rug, lanterns or string lights, a pergola or an awning, outdoor
  cushions, climbing plants, decking ...), its palette (wall colour, floor, wood tone, metal, textile colours, light
  mood), its density and up to five signature items in words. ``recipe_read.read_photo`` asks the vision model
  (temperature 0, the schema) once per photo; ``recipe_read`` reads, caches and assembles a project's recipes.
- ``aggregate(answers)``: the recipe of a space and family (pure): per layer the share of photos that show it (counts:
  the median), ``must`` (shown in at least ``MUST_SHARE`` of the photos), ``often`` (``OFTEN_SHARE`` and more), the
  palette's most frequent values with their share, the density and the signature items named twice or more.
- ``default_recipe(space)``: the built-in recipe (designer knowledge) until the pod has read the space's photos;
  ``recipe_text(recipe)``: the paragraph a stylist prompt carries.
- ``gaps(recipe, present)``: what a room lacks against its recipe (pure): the ``must`` layers the room does not
  have, each a typed gap ``{"layer", "share", "wanted", "have"}`` the decor stage, the judge and Argus act on (the
  AI never gives coordinates: code places).

Why: the renders were judged "like a child's drawing": a room had its anchor pieces and nothing that makes a
designed room (layers of light, textiles, window dressing, styled surfaces). The vision model knows such rooms, but
asked about one render it named only what was wrong; the reference photos make "good" concrete per space and style.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Optional

# layer -> "bool" | "count"
INTERIOR_LAYERS: dict[str, str] = {
    "rug": "bool", "curtains": "bool", "blinds": "bool", "wall_art": "count", "mirror": "bool", "plants": "count",
    "pendant_or_ceiling_light": "bool", "floor_lamp": "bool", "table_lamps": "count", "wall_lights": "bool",
    "cushions": "bool", "throw": "bool", "styled_surfaces": "bool", "styled_shelves": "bool",
    "bedding_layers": "bool", "towels": "bool", "accent_wall": "bool", "wall_panelling": "bool",
    "ceiling_feature": "bool", "open_shelves": "bool", "bar_stools": "bool", "headboard": "bool",
}
OUTDOOR_LAYERS: dict[str, str] = {
    "lounge_set": "bool", "dining_set": "bool", "planters": "count", "outdoor_rug": "bool",
    "lanterns_or_string_lights": "bool", "pergola_or_awning": "bool", "outdoor_cushions": "bool",
    "climbing_plants": "bool", "decking": "bool", "potted_trees": "bool", "wall_lights": "bool", "hedge_or_border": "bool",
}
LAYER_TEXT: dict[str, str] = {
    "rug": "a rug on the floor", "curtains": "fabric curtains or drapes at the windows",
    "blinds": "blinds or shades", "wall_art": "framed art, prints or photos on the walls (how many)",
    "mirror": "a mirror", "plants": "indoor plants (how many)", "pendant_or_ceiling_light": "a visible pendant, "
    "chandelier or ceiling light", "floor_lamp": "a floor lamp", "table_lamps": "table lamps (how many)",
    "wall_lights": "wall lights or sconces", "cushions": "cushions or pillows on seats", "throw": "a throw blanket",
    "styled_surfaces": "objects on tables and consoles (books, vases, bowls, trays)",
    "styled_shelves": "shelves styled with books and objects", "bedding_layers": "a made bed with layered bedding "
    "(duvet, throw, several pillows)", "towels": "towels", "accent_wall": "one wall in another colour or material",
    "wall_panelling": "panelling, slats or mouldings on a wall", "ceiling_feature": "beams, a wood or coffered ceiling "
    "or a cove", "open_shelves": "open shelves with objects", "bar_stools": "bar stools at a counter",
    "headboard": "an upholstered or wooden headboard",
    "lounge_set": "an outdoor sofa or armchairs with a table", "dining_set": "an outdoor dining table with chairs",
    "planters": "planters or large pots with plants (how many)", "outdoor_rug": "an outdoor rug",
    "lanterns_or_string_lights": "lanterns or string lights", "pergola_or_awning": "a pergola, an awning or a "
    "covered roof over the seats", "outdoor_cushions": "cushions on the outdoor seats",
    "climbing_plants": "climbing plants on walls or posts", "decking": "a wood deck floor",
    "potted_trees": "small trees in pots", "hedge_or_border": "a hedge or a planted border",
}
WALL_COLOURS = ("white", "warm_white", "beige", "greige", "light_grey", "dark_grey", "sage", "blue", "terracotta",
                "black", "wood", "stone", "brick", "other")
FLOORS = ("light_wood", "mid_wood", "dark_wood", "stone_tile", "terracotta_tile", "patterned_tile", "concrete",
          "carpet", "decking", "gravel", "grass", "other")
WOOD_TONES = ("light", "mid", "dark", "none")
METALS = ("black", "brass", "chrome", "none")
COLOUR_WORDS = ("white", "cream", "beige", "sand", "grey", "charcoal", "black", "brown", "terracotta", "rust",
                "olive", "sage", "green", "blue", "navy", "mustard", "pink", "wood")
MOODS = ("warm", "neutral", "cool")
DENSITY = ("sparse", "balanced", "layered")
MUST_SHARE = 0.6               # a layer in at least this share of the photos is part of the style's room
OFTEN_SHARE = 0.3              # ... at least this share: often there
SIGNATURE_MAX = 5
SYSTEM = ("You are an interior and landscape designer. You look at one photo of a well-designed space and list, "
          "exactly and only, what the photo shows: no guessing beyond the image.")


def layers_of(interior: bool) -> dict[str, str]:
    return INTERIOR_LAYERS if interior else OUTDOOR_LAYERS


def photo_schema(interior: bool) -> dict:
    """The strict JSON schema of one photo's answer (module docstring)."""
    props = {}
    for name, kind in layers_of(interior).items():
        props[name] = {"type": "integer", "minimum": 0, "maximum": 8} if kind == "count" else {"type": "boolean"}
    layer_obj = {"type": "object", "properties": props, "required": sorted(props), "additionalProperties": False}
    palette = {"type": "object", "additionalProperties": False,
               "required": ["wall_colour", "floor", "wood_tone", "metal", "textile_colours", "light_mood"],
               "properties": {"wall_colour": {"enum": list(WALL_COLOURS)}, "floor": {"enum": list(FLOORS)},
                              "wood_tone": {"enum": list(WOOD_TONES)}, "metal": {"enum": list(METALS)},
                              "textile_colours": {"type": "array", "items": {"enum": list(COLOUR_WORDS)},
                                                  "maxItems": 3},
                              "light_mood": {"enum": list(MOODS)}}}
    return {"type": "object", "additionalProperties": False,
            "required": ["is_the_space", "layers", "palette", "density", "signature"],
            "properties": {"is_the_space": {"type": "boolean"}, "layers": layer_obj, "palette": palette,
                           "density": {"enum": list(DENSITY)},
                           "signature": {"type": "array", "maxItems": SIGNATURE_MAX,
                                         "items": {"type": "string", "maxLength": 40}}}}


def photo_prompt(space_words: str, family: Optional[str], interior: bool) -> str:
    rows = "\n".join(f"- {k}: {LAYER_TEXT[k]}" for k in layers_of(interior))
    return (f"The photo should show a {family + ' ' if family else ''}{space_words}. is_the_space: does it? Then, for "
            f"each item, whether the photo shows it (a number where it says how many):\n{rows}\n"
            "palette: the main wall colour, the floor, the wood tone, the metal finish, up to three textile colours and "
            "the light mood. density: sparse (few things), balanced or layered (many layers of textiles, objects and "
            f"light). signature: up to {SIGNATURE_MAX} short phrases naming the pieces or materials that make this "
            "space's style (e.g. 'linen curtains', 'rattan pendant', 'oak slatted wall').")


def _mode(values: list) -> tuple[Optional[str], float]:
    vals = [v for v in values if v not in (None, "", "other", "none")]
    if not vals:
        return None, 0.0
    best = max(sorted(set(vals)), key=vals.count)
    return best, round(vals.count(best) / len(values), 3)


def aggregate(answers: list[dict], interior: bool) -> dict:
    """The recipe of the photos' answers (module docstring). Answers with an error or ``is_the_space`` False are
    left out (``n`` counts the rest)."""
    good = [a for a in answers if isinstance(a, dict) and not a.get("error") and a.get("is_the_space") is not False]
    n = len(good)
    layers: dict = {}
    for name, kind in layers_of(interior).items():
        vals = [(a.get("layers") or {}).get(name) for a in good]
        if kind == "count":
            nums = [int(v) for v in vals if isinstance(v, int) and not isinstance(v, bool)]
            share = sum(1 for v in nums if v > 0) / n if n else 0.0
            layers[name] = {"share": round(share, 3), "median": statistics.median(nums) if nums else 0}
        else:
            share = sum(1 for v in vals if v is True) / n if n else 0.0
            layers[name] = {"share": round(share, 3)}
    pal = [a.get("palette") or {} for a in good]
    palette = {}
    for key in ("wall_colour", "floor", "wood_tone", "metal", "light_mood"):
        v, s = _mode([p.get(key) for p in pal])
        palette[key] = {"value": v, "share": s}
    colours = [c for p in pal for c in p.get("textile_colours") or []]
    palette["textile_colours"] = [c for c, _n in sorted(((c, colours.count(c)) for c in set(colours)),
                                                        key=lambda x: (-x[1], x[0]))][:3]
    density, dshare = _mode([a.get("density") for a in good])
    sig: dict = {}
    for a in good:
        for s in a.get("signature") or []:
            key = " ".join(str(s).lower().split())
            if key:
                sig[key] = sig.get(key, 0) + 1
    return {"n": n, "interior": interior, "layers": layers,
            "must": sorted(k for k, v in layers.items() if v["share"] >= MUST_SHARE),
            "often": sorted(k for k, v in layers.items() if OFTEN_SHARE <= v["share"] < MUST_SHARE),
            "palette": palette, "density": {"value": density, "share": dshare},
            "signature": [k for k, c in sorted(sig.items(), key=lambda kv: (-kv[1], kv[0])) if c >= 2][:8]}


def gaps(recipe: dict, present: dict) -> list[dict]:
    """The ``must`` layers of ``recipe`` a room lacks (pure): ``present`` = ``{layer: count or bool}`` of what the
    room has (the decor stage's own count, ``wenart.style.layers``). A count layer is a gap when the room has fewer
    than its median (at least 1); a bool layer when the room has none. Most shared first."""
    out = []
    for name in recipe.get("must") or []:
        info = (recipe.get("layers") or {}).get(name) or {}
        have = present.get(name, 0)
        have_n = int(have) if not isinstance(have, bool) else int(have)
        wanted = max(1, int(round(float(info.get("median") or 1)))) if "median" in info else 1
        if have_n < wanted:
            out.append({"layer": name, "share": info.get("share"), "wanted": wanted, "have": have_n})
    return sorted(out, key=lambda g: (-float(g["share"] or 0), g["layer"]))


# The built-in recipes (designer knowledge) used until the pod has read a space's reference photos: the layers good
# photos of the space usually show. ``source: default``; the photos' recipe replaces it.
DEFAULT_MUST: dict[str, dict[str, int]] = {
    "living": {"rug": 1, "curtains": 1, "wall_art": 2, "plants": 2, "pendant_or_ceiling_light": 1, "floor_lamp": 1,
               "table_lamps": 1, "cushions": 1, "throw": 1, "styled_surfaces": 1},
    "dining": {"rug": 1, "curtains": 1, "wall_art": 1, "plants": 1, "pendant_or_ceiling_light": 1,
               "styled_surfaces": 1},
    "bedroom": {"rug": 1, "curtains": 1, "wall_art": 1, "plants": 1, "table_lamps": 2, "cushions": 1, "throw": 1,
                "bedding_layers": 1, "pendant_or_ceiling_light": 1},
    "child": {"rug": 1, "curtains": 1, "wall_art": 2, "plants": 1, "table_lamps": 1, "cushions": 1,
              "bedding_layers": 1, "pendant_or_ceiling_light": 1},
    "kitchen": {"styled_surfaces": 1, "plants": 1, "pendant_or_ceiling_light": 1},
    "bathroom": {"towels": 1, "mirror": 1, "plants": 1, "styled_surfaces": 1},
    "office": {"rug": 1, "curtains": 1, "wall_art": 1, "plants": 1, "table_lamps": 1, "styled_shelves": 1},
    "hall": {"mirror": 1, "wall_art": 1, "plants": 1, "styled_surfaces": 1, "pendant_or_ceiling_light": 1},
    "dressing": {"rug": 1, "mirror": 1, "pendant_or_ceiling_light": 1},
    # 28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside, that's
    # outside area"): the built-in outdoor recipes ask for no rug (the photos' outdoor_rug layer is still measured)
    "veranda": {"lounge_set": 1, "planters": 3, "outdoor_cushions": 1, "lanterns_or_string_lights": 1},
    "terrace": {"lounge_set": 1, "planters": 3, "outdoor_cushions": 1, "lanterns_or_string_lights": 1},
    "balcony": {"dining_set": 1, "planters": 2, "outdoor_cushions": 1},
    "garden": {"hedge_or_border": 1, "potted_trees": 1},
    "facade": {"planters": 2, "wall_lights": 1},
}


def default_recipe(space: str) -> dict:
    """The built-in recipe of ``space`` (``DEFAULT_MUST``) in the shape of ``aggregate``'s (source ``default``)."""
    from wenart.style import references as RF

    interior = RF.SPACES.get(space, ((), True))[1]
    must = DEFAULT_MUST.get(space, {})
    layers = {}
    for name, kind in layers_of(interior).items():
        if name in must:
            layers[name] = {"share": 1.0, **({"median": must[name]} if kind == "count" else {})}
        else:
            layers[name] = {"share": 0.0, **({"median": 0} if kind == "count" else {})}
    return {"n": 0, "interior": interior, "layers": layers, "must": sorted(must), "often": [],
            "palette": {}, "density": {"value": "balanced", "share": 0.0}, "signature": [], "space": space,
            "family": None, "source": "default"}


def recipe_text(recipe: dict) -> str:
    """One paragraph a stylist prompt carries: the must and often layers (with counts), the palette and the
    signature items of the recipe."""
    def name(layer):
        info = (recipe.get("layers") or {}).get(layer) or {}
        n = info.get("median")
        return f"{LAYER_TEXT.get(layer, layer).split(' (')[0]}" + (f" x{int(round(float(n)))}" if n and n > 1 else "")
    src = ("built-in designer defaults" if recipe.get("source") == "default"
           else f"{recipe.get('n')} reference photos of {recipe.get('family') or ''} {recipe.get('space')}".strip())
    parts = [f"What good rooms of this kind show ({src}): " + "; ".join(name(x) for x in recipe.get("must") or [])]
    if recipe.get("often"):
        parts.append("often also: " + "; ".join(name(x) for x in recipe["often"]))
    pal = recipe.get("palette") or {}
    words = [f"{k.replace('_', ' ')} {v['value']}" for k, v in pal.items()
             if isinstance(v, dict) and v.get("value")]
    if pal.get("textile_colours"):
        words.append("textiles " + "/".join(pal["textile_colours"]))
    if words:
        parts.append("palette: " + ", ".join(words))
    if recipe.get("signature"):
        parts.append("signature pieces: " + ", ".join(recipe["signature"][:6]))
    return ". ".join(parts) + "."
