"""What a material's name says it is made of (pure; the word rules of the 3D Warehouse fix-up, ``wenart.assets.warehouse``,
moved here on 30 Oct 2026 so the build reads them too without the fix-up's import closure: lesson UL140, the build
dresses a library soft seat's flat upholstery slots and must tell a fabric or an unnamed slot from a metal frame).

``MATERIAL_RULES``: ``(rule, words, roughness, metallic)``; ``name_rule(name)``: the first rule with a word in the
folded name (``wenart.assets.audit.keywords`` matching), None when the name says nothing (SketchUp's "Color_A01",
"02 - Default1"). ``warehouse.material_rule`` adds the type's roughness for such names.
"""
from __future__ import annotations

from typing import Optional

# (rule, words, roughness, metallic): the first rule with a word in the folded material name wins.
MATERIAL_RULES: tuple[tuple[str, tuple[str, ...], float, float], ...] = (
    ("mirror", ("mirror", "ayna", "spiegel", "miroir", "espejo", "specchio"), 0.03, 1.0),
    ("glass", ("glass", "glazing", "translucent", "transparent", "crystal", "cam", "glas", "verre", "vidrio", "vetro",
               "plexi", "perspex"), 0.05, 0.0),
    ("chrome", ("chrome", "chromed", "krom", "inox", "stainless", "nickel", "silver", "polished steel",
                "polished metal", "polished aluminium", "polished aluminum"), 0.12, 1.0),
    ("metal", ("metal", "metallic", "steel", "iron", "aluminium", "aluminum", "alu", "brass", "bronze", "copper",
               "gold", "golden", "zinc", "titanium", "celik", "demir", "metall"), 0.35, 1.0),
    ("ceramic", ("ceramic", "porcelain", "enamel", "china", "sanitary", "seramik", "porselen", "keramik"), 0.12, 0.0),
    ("stone_polished", ("marble", "granite", "quartz", "terrazzo", "onyx", "mermer", "granit"), 0.25, 0.0),
    ("gloss", ("gloss", "glossy", "lacquer", "lacquered", "varnish", "varnished", "parlak"), 0.2, 0.0),
    ("plastic", ("plastic", "acrylic", "vinyl", "pvc", "resin", "polypropylene", "abs", "plastik", "akrilik"), 0.4,
     0.0),
    ("leather", ("leather", "leatherette", "deri", "leder", "cuir", "cuero", "pelle"), 0.45, 0.0),
    ("rattan", ("rattan", "wicker", "cane", "hasir", "jute", "seagrass"), 0.75, 0.0),
    ("wood", ("wood", "wooden", "oak", "walnut", "ash", "pine", "teak", "birch", "maple", "beech", "cherry",
              "mahogany", "veneer", "mdf", "plywood", "parquet", "bamboo", "ahsap", "mese", "ceviz", "holz", "bois",
              "madera", "legno", "laminate", "chipboard"), 0.55, 0.0),
    ("fabric", ("fabric", "textile", "cloth", "linen", "cotton", "velvet", "wool", "felt", "upholstery", "boucle",
                "chenille", "tweed", "canvas", "carpet", "rug", "kumas", "stoff", "tissu", "tela", "tessuto", "suede",
                "microfiber", "microfibre", "polyester", "cushion", "pillow", "blanket", "curtain", "drape"), 0.9, 0.0),
    ("paper", ("paper", "cardboard", "kagit", "book", "page"), 0.85, 0.0),
    ("rubber", ("rubber", "silicone"), 0.85, 0.0),
    ("stone", ("stone", "concrete", "cement", "brick", "plaster", "stucco", "beton", "travertine", "slate"), 0.8, 0.0),
    ("bark", ("bark", "trunk", "branch", "kabuk"), 0.9, 0.0),
    ("foliage", ("leaf", "leaves", "foliage", "grass", "plant", "needle", "yaprak", "flower", "petal", "moss"), 0.6,
     0.0),
    ("matte", ("matte", "matt", "mat"), 0.8, 0.0),
    ("paint", ("paint", "painted", "boya"), 0.5, 0.0),
)


def name_rule(name: str) -> Optional[tuple[str, float, float]]:
    """``(rule, roughness, metallic)`` of the first ``MATERIAL_RULES`` word in the folded ``name``, None when the name
    names no material."""
    from wenart.assets.audit import keywords as K
    toks, folded = K.tokens(name or ""), K.fold(name or "")
    for rule, words, rough, metal in MATERIAL_RULES:
        for w in words:
            if K._matches(toks, folded, w):
                return rule, rough, metal
    return None
