"""How well a library model suits an open-air room (pure, no dependencies: the fit ranks with it and the build's
architect reads it; 25 Oct 2026, user on real04's roof terrace: "is that table on the terrace ok? is it suitable for
the terrace?": an indoor turned-leg table with a drawer and indoor dining chairs stood there).

``outdoor_grade(entry)``: 0 named or built for outside (outdoor, garden, patio, bistro, teak, rattan, wicker,
aluminium) or of metal / rattan only, 1 wood, glass or stone without upholstery, 2 upholstered (fabric) or named for
inside (desk, drawer, office, velvet, leather ...). A piece in an open-air room (``OPEN_AIR_ROOMS``) ranks the models
by it (``fit.rank_key``: ``OUTDOOR_STEPS`` size steps per grade).
"""
from __future__ import annotations

OPEN_AIR_ROOMS = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")
OUTDOOR_WORDS = ("outdoor", "garden", "patio", "terrace", "bistro", "teak", "rattan", "wicker", "alumin", "deck",
                 "lounger", "sunbed", "adirondack", "poolside", "resin", "café", "cafe")
INDOOR_WORDS = ("desk", "drawer", "office", "velvet", "leather", "upholster", "dresser", "vanity", "nightstand",
                "turned", "tufted", "chesterfield", "dining room", "living room", "bedroom", "wheel", "castor",
                "caster", "swivel", "办公", "press", "damask", "hallway")
OUTDOOR_STEPS = 3


def outdoor_grade(entry: dict) -> int:
    """How well a model suits an open-air room (pure): 0 made for outside, 1 hard materials, 2 made for inside."""
    words = " ".join(str(entry.get(k) or "") for k in ("name", "title", "style_note", "style_hint")).lower()
    tags = set(entry.get("material_tags") or [])
    if any(w in words for w in OUTDOOR_WORDS):
        return 0
    if "fabric" in tags or any(w in words for w in INDOOR_WORDS):
        return 2
    if tags and tags <= {"metal", "rattan", "glass"} and tags & {"metal", "rattan"}:
        return 0
    return 1
