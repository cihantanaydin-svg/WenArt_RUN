"""See-through wardrobes and walk-in dressing rooms (29 Oct 2026, lessons UL120, UL125; docs/reference_details_20261029.md
R1, R31, R37, D4).

The user (29 Oct 2026, a bedroom with a full-height wardrobe behind black horizontal slat sliding doors, the shirts,
shelves and drawers showing through): "look at this dressing room solution see through why we are not using some
similar in our projects?"; on real06's dressing room (two drawn wardrobe runs facing each other across a 1.2 m aisle,
closed white panel doors): "this dressing could be a see through dressing room in the both sides argus should have
think of this". Our wardrobes had closed fronts only, and no garments.

What (pure, no ``bpy`` but ``build_mirrors``): ``plan(building, style)`` -> ``{piece id: front}`` of the wardrobes
that get a see-through front, ``apply(building, style)`` writes it into the pieces (``see_through``, the design's
``see_through`` kind) and builds them from the wardrobe module builder (``modules.plan_wardrobe_run``: sliding
see-through doors, or an open run, in front of real contents), keeping the fitted library model's record
(``see_through.replaced``) so the change is never silent.

- A walk-in dressing room (``walk_in``: a dressing room, ``door_states.is_dressing``, or any room whose wardrobe runs
  face each other across an aisle of ``AISLE_M``) is see-through on every side by default; its family picks the front
  (``WALK_IN_FRONTS``: horizontal black slat sliding doors ``slats``, smoked glass in black frames ``smoked_glass``, or
  an ``open`` run of hanging rails, shelves and shoe racks); the architect's ``wardrobe_fronts`` answer
  (``architect_rules`` D8, ``room["wardrobe_fronts"]``) can change it, ``closed`` included.
- The master bedroom's widest wardrobe run gets the family's see-through front where the style has one
  (``FRONTS``: the modern, Japandi, Scandinavian, minimal, contemporary and industrial families; the period families
  keep closed fronts). 30 Oct 2026 (UL182): so does every other bedroom's widest run, each bedroom its own front
  (``bedroom_front``: slats, slats with glass doors in turn, smoked or reeded glass; the room scheme's first), and every
  see-through run goes up to the ceiling (``to_ceiling``: a top box). Every other wardrobe keeps its closed fronts. A
  front needs ``MIN_WIDTH_M`` (two sliding panels) and ``MIN_DEPTH_M`` (a hanger across).
- The contents (``modules.see_through_parts``): a hanging rail with garments (shirts, jackets, coats, dresses, knits:
  simple cloth shapes on hangers, varied colours of the muted ``GARMENT_COLOURS``), folded stacks on shelves, drawers
  or shoe racks, an LED strip under the top; the garments of one wardrobe are part of its one mesh.
- 30 Oct 2026 (lesson UL135, user on real04's black slatted run f_L0_023: "I like this but the clothes inside needs
  more detail"): the contents are ``wardrobe_contents``' (garments with shoulders, sleeves and collars on wooden
  hangers, trousers over the bar, woven fabrics, folded stacks with their fold edges, shoes, lidded boxes and rattan
  baskets, a light in every bay), in the room's palette (``garment_palette``: the family's ``FAMILY_GARMENTS`` with the
  room scheme's colour, recorded in ``see_through.palette``); the slats stay as they are.
- ``walk_in_extras(building, room)``: a bench (else a pouf) on a free wall where the walkway allows (``WALKWAY_M`` free
  in front of it, clear of the wardrobes' ``ACCESS_M`` and the doors' approaches and leaves), and a full-height mirror
  on a free wall stretch (``MIRROR_M``), each recorded with its reason or why it does not fit.
- 31 Oct 2026 (user on real04 run 20261030-181158-full, an L0 bedroom with a desk: "Not every room needs this built in
  wardrobe, we can use it sometime but it needs to be wall to wall or from wall to middle, also you can make this a lot
  better with the better material and details"). The see-through run is a built-in (a feature front, a top box to the
  ceiling): (1) a house gets at most ``BUILT_IN_ROOMS_MAX`` rooms of them (``plan``): the walk-in dressing rooms first,
  then the master bedroom (with its twin), then the bedrooms whose room scheme asks for one, the best fit first (a run
  from wall to wall, then the larger room, then the wider run); a twin pair is taken whole or not at all; every other
  wardrobe keeps the fit's free-standing library model (or its closed module run), each skip recorded with its reason.
  The run of real04 (pod at fa7d24d) predates UL207; UL207 alone still gave 6 of its 8 bedrooms a run (two scheme
  bundles of four ask for one, and twins copy them) and a scheme recorded before UL207 still named its old front:
  ``bedroom_front`` reads the bundle's current front (``SCHEME_FRONTS``) first. (2) A built-in stands against a wall at
  one end at least (``run_ends``: within ``END_TOUCH_M`` of a solid wall face along the run, never a door): a gap of at
  most ``EXTEND_MAX_M`` to a side wall is closed (``built_in_fit``: the strip, the floor in front of it and the doors'
  approaches free, no opening behind it; ``drawn_footprint`` kept, ``adjusted_by_ai``), so a run ends at the wall, or
  goes from wall to wall; with ``furnished_rooms: keep`` or ``furnished_rooms_keep_size`` the size stays and a run
  that does not reach a wall stays free-standing. (3) The look (``built_in_look``, ``BUILT_IN_LOOKS``): the shell (the
  end panels to the floor, the fascia to the ceiling, the slats) in the style's wood veneer or the family's matte
  lacquer, the style's veneer inside, slim metal frames with glazing beads in the family's metal, long grip channels,
  shadow gaps, a recessed plinth, tinted glass that reads as glass, rounded flutes on reeded glass
  (``modules.see_through_parts``, ``look_overrides``).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

WARDROBE_TYPES: tuple[str, ...] = ("wardrobe",)
FRONTS: dict[str, str] = {"modern": "slats", "japandi": "slats", "scandinavian": "slats",
                          "minimal": "smoked_glass", "modern minimal": "smoked_glass", "contemporary": "smoked_glass",
                          "industrial": "smoked_glass"}
WALK_IN_FRONTS: dict[str, str] = dict(FRONTS, industrial="open", classic="open", rustic="open", mediterranean="open",
                                      traditional="open")
WALK_IN_DEFAULT = "open"
FRONT_KINDS: tuple[str, ...] = ("slats", "smoked_glass", "open", "slats_glass", "reeded_glass")
CHOICES: tuple[str, ...] = FRONT_KINDS + ("closed",)
# 31 Oct 2026 (user on real04 run 20261030-181158-full: "you can make this a lot better with the better material and
# details"): the fronts are wood slats and tinted or reeded glass in slim metal frames (``built_in_look``), no longer
# black boxes
FRONT_WHAT = {"slats": "sliding doors of horizontal wood slats in slim metal frames", "smoked_glass": "tinted glass "
              "sliding doors in slim metal frames", "open": "an open run (hanging rails, shelves and shoe racks)",
              "closed": "closed fronts",
              # 30 Oct 2026 (UL182): glass sections among the slats, and reeded glass
              "slats_glass": "slim-framed sliding doors, wood-slatted ones and glass ones in turn",
              "reeded_glass": "reeded glass sliding doors in slim metal frames"}
# 30 Oct 2026 (lesson UL182, user on real04 run 20261030-112241-full: "These kind of wardrobes can be used in other
# rooms also, it can go all the way to the ceiling it can have glass sections I did gave an inspiration before"): in
# the families that use a see-through front, a bedroom's widest wardrobe run may get one, each bedroom its own
# (``bedroom_front``): the master the family's own front (``FRONTS``, the inspiration's black slats in the modern
# homes), the others in the order of the family's ``BEDROOM_FRONTS``, the room scheme's choice first
# (``room_schemes`` bedroom bundles: ``wardrobe_front``; ``SCHEME_FRONTS`` for a scheme recorded before), a front no
# other bedroom of the house has while the family's fronts last; a twin room takes its partner's. UL207 (user: "This is
# not mandatory it is optional"): besides the master only the bedrooms whose room scheme names a see-through front
# get one (two of the four bedroom bundles keep closed fronts). Every see-through
# run goes up to the ceiling (``to_ceiling``: a top box of lidded boxes and baskets behind the full-height doors).
BEDROOM_FRONTS: dict[str, tuple[str, ...]] = {
    "modern": ("slats", "slats_glass", "smoked_glass", "reeded_glass"),
    "japandi": ("slats", "reeded_glass", "slats_glass"),
    "scandinavian": ("slats", "reeded_glass", "slats_glass", "smoked_glass"),
    "minimal": ("smoked_glass", "reeded_glass", "slats_glass"),
    "modern minimal": ("smoked_glass", "reeded_glass", "slats_glass"),
    "contemporary": ("smoked_glass", "slats_glass", "reeded_glass", "slats"),
    "industrial": ("smoked_glass", "slats_glass"),
}
SCHEME_FRONTS: dict[str, str] = {"panel": "slats_glass", "deep": "closed", "limewash": "reeded_glass",
                                 "slats": "closed"}      # = room_schemes.POOLS["bedroom"][bundle]["wardrobe"]
SECTION_GLASS: dict[str, str] = {"japandi": "reeded_glass", "scandinavian": "reeded_glass"}   # else smoked_glass
CEILING_GAP_M = 0.005             # the run's top this far under the ceiling (no coplanar faces)
TOP_BOX_M = (0.03, 1.00)          # a top box from this to this high closes the run up to the ceiling; higher: none
WINDOW_CLEAR_M = 0.35             # a window this near the run in plan keeps it at its height (its head stays free)
LIGHT_CLEAR_M = 0.02              # a ceiling light (a track, a pendant) over the run or this near it slides off it
LIGHT_SHIFT_MAX_M = 0.40          # ... at most this far into its room (else the run keeps its height)
MIN_WIDTH_M = 1.0
MIN_DEPTH_M = 0.50
AISLE_M = (0.70, 1.80)            # two runs facing each other this far apart (front to front) make a walk-in
FACING_DEG = 25.0
OVERLAP_SHARE = 0.4               # ... and overlapping along their runs by this share of the shorter one
ACCESS_M = 0.45                   # free floor in front of a sliding or open wardrobe front
WALKWAY_M = 0.60                  # free floor in front of an added bench or pouf
BENCH_M = (1.0, 0.40, 0.45)       # schemas.SIZE_OPTIONS bench, the ottoman's (pouf) 0.5 x 0.5
POUF_M = (0.50, 0.50, 0.45)
MIRROR_M = (0.60, 1.80, 0.15)     # a full-height mirror: width, height, bottom over the floor
MIRROR_FRAME_M = 0.025
MIRROR_DEPTH_M = 0.03
OPENING_MARGIN_M = 0.10
# 31 Oct 2026 (user on real04 run 20261030-181158-full: "Not every room needs this built in wardrobe, we can use it
# sometime but it needs to be wall to wall or from wall to middle"; module docstring (1), (2))
BUILT_IN_ROOMS_MAX = 2            # rooms of a house with a built-in see-through run (walk-ins, the master and its twin)
END_TOUCH_M = 0.05                # = looks.BUILT_IN_REACH_M: a run end this near a wall face stands against it
EXTEND_MAX_M = 0.50               # CLAUDE.md: a drawn piece moves at most 0.5 m: a gap this small to a side wall closes
EXTEND_CLEAR_M = 0.003            # the extended end stops this short of the wall face (a scribe; no coplanar faces)
END_SAMPLES: tuple[float, ...] = (-0.8, 0.0, 0.8)      # where across its depth a run end looks for its wall
RAY_BACK_M = 0.02                 # ... from this far inside the run
PASSAGE_TYPES: tuple[str, ...] = ("door", "opening")   # an end at one of these stands at a doorway, not at a wall
BEHIND_OPENING_M = 0.35           # an opening this near the back line of an extension stands behind it
# 31 Oct 2026 (user: "you can make this a lot better with the better material and details"; module docstring (3)): the
# built-in's look by family (designer sets, assumed): ``shell`` veneer (the style's furniture wood, else ``wood``) or
# lacquer (``lacquer_matte`` in ``colour``) for the end panels, the fascia to the ceiling and the slats; ``wood`` the
# veneer inside; ``metal`` the slim frames, the track and the grip channels (anodised dark bronze, champagne = brushed
# steel, brass, black); ``glass`` the tinted pane's material key (``bronze_glass`` warm, ``smoked_glass`` grey)
BUILT_IN_LOOKS: dict[str, dict] = {
    "modern": {"shell": "veneer", "wood": "wood_veneer_oak", "metal": "dark_bronze", "glass": "bronze_glass"},
    "contemporary": {"shell": "veneer", "wood": "wood_veneer_walnut", "metal": "metal_brass", "glass": "bronze_glass"},
    "scandinavian": {"shell": "veneer", "wood": "wood_veneer_oak_light", "metal": "steel_brushed",
                     "glass": "smoked_glass"},
    "japandi": {"shell": "veneer", "wood": "wood_veneer_oak_light", "metal": "dark_bronze", "glass": "bronze_glass"},
    "minimal": {"shell": "lacquer", "colour": "off white", "wood": "wood_veneer_oak_light", "metal": "steel_brushed",
                "glass": "smoked_glass"},
    "modern minimal": {"shell": "lacquer", "colour": "greige", "wood": "wood_veneer_oak", "metal": "dark_bronze",
                       "glass": "bronze_glass"},
    "industrial": {"shell": "veneer", "wood": "wood_veneer_black_oak", "metal": "metal_black", "glass": "smoked_glass"},
}
BUILT_IN_LOOK_DEFAULT = "modern"
LACQUER_SLUG = "lacquer_matte"    # finishes.FURNITURE_MATERIALS: a matte lacquer that takes the look's colour
# muted garment colours (wenart/style/colours.py names), cycled by the wardrobe's own seed
GARMENT_COLOURS: tuple[str, ...] = ("white", "light grey", "navy", "charcoal", "beige", "sky blue", "sage", "camel",
                                    "taupe", "off white", "dusty blue", "olive", "black", "greige")


# 30 Oct 2026 (UL135): the wardrobe's garment colours by style family (designer palettes of the reference photos:
# whites, greys and blacks with the family's own earth or blue tones), and the room scheme's colour joins them
FAMILY_GARMENTS: dict[str, tuple[str, ...]] = {
    "modern": ("white", "off white", "light grey", "charcoal", "black", "navy", "camel", "sky blue"),
    "contemporary": ("ivory", "camel", "navy", "rust", "dusty blue", "charcoal", "white", "greige"),
    "scandinavian": ("off white", "sand", "greige", "sage", "dusty blue", "charcoal", "white", "light grey"),
    "japandi": ("ivory", "sand", "taupe", "olive", "charcoal", "black", "greige", "camel"),
    "minimal": ("white", "off white", "light grey", "greige", "charcoal", "black", "sand"),
    "modern minimal": ("white", "off white", "light grey", "greige", "charcoal", "black", "sand"),
    "industrial": ("charcoal", "black", "olive", "rust", "navy", "light grey", "camel", "white"),
    "mediterranean": ("white", "sand", "terracotta", "dusty blue", "olive", "navy", "camel"),
    "classic": ("white", "cream", "navy", "burgundy", "camel", "charcoal", "light grey"),
    "rustic": ("cream", "rust", "olive", "camel", "charcoal", "navy", "sand"),
}
SCHEME_GARMENT_WORDS: tuple[tuple[str, str], ...] = (("sage", "sage"), ("olive", "olive"), ("blue", "dusty blue"),
                                                     ("navy", "navy"), ("greige", "greige"), ("terracotta", "terracotta"),
                                                     ("rust", "rust"), ("pink", "dusty pink"), ("blush", "blush"),
                                                     ("mustard", "mustard"), ("taupe", "taupe"), ("sand", "sand"),
                                                     ("burgundy", "burgundy"), ("green", "sage"), ("ochre", "mustard"))


def garment_palette(style, scheme: Optional[dict] = None) -> list[str]:
    """The colours of a wardrobe's garments and folded stacks (pure; 30 Oct 2026, UL135): the family's
    ``FAMILY_GARMENTS`` (else ``GARMENT_COLOURS``) and the colour the room's scheme names (its walls' colour, as a
    garment colour: ``SCHEME_GARMENT_WORDS``), every one a known colour name (``wenart.style.colours``)."""
    from wenart.style import colours as C

    out = list(FAMILY_GARMENTS.get(family_of(style)) or GARMENT_COLOURS)
    phrase = str((scheme or {}).get("wall_colour") or "").lower()
    for word, colour in SCHEME_GARMENT_WORDS:
        if word in phrase and colour not in out:
            out.append(colour)
            break
    return [c for c in out if c in C.COLOURS] or [c for c in GARMENT_COLOURS if c in C.COLOURS]


def built_in_look(style) -> dict:
    """The look of a built-in see-through run (pure; 31 Oct 2026, user: "you can make this a lot better with the better
    material and details"; ``BUILT_IN_LOOKS``): ``{"family", "shell": veneer | lacquer, "shell_slug", "colour", "wood",
    "metal", "glass", "why"}``. The veneer is the style's furniture wood when it names a veneer (the pieces of the room
    fit together), else the family's; the lacquer is ``LACQUER_SLUG`` in the family's colour."""
    fam = family_of(style)
    row = BUILT_IN_LOOKS.get(fam) or BUILT_IN_LOOKS[BUILT_IN_LOOK_DEFAULT]
    furniture = (style or {}).get("furniture") if isinstance(style, dict) else None
    given = (furniture or {}).get("wood") if isinstance(furniture, dict) else None
    wood = given if isinstance(given, str) and given.startswith("wood_veneer_") else row["wood"]
    lacquer = row["shell"] == "lacquer"
    out = {"family": fam or BUILT_IN_LOOK_DEFAULT, "shell": row["shell"],
           "shell_slug": LACQUER_SLUG if lacquer else wood, "colour": row.get("colour") if lacquer else None,
           "wood": wood, "metal": row["metal"], "glass": row["glass"]}
    tone = wood.replace("wood_veneer_", "").replace("_", " ")
    shell = f"a matte {out['colour']} lacquer" if lacquer else f"{tone} veneer"
    out["why"] = (f"{shell} shell (end panels to the floor, a fascia to the ceiling, the slats), "
                  f"{out['metal'].replace('_', ' ')} slim frames with long grip channels, "
                  f"{out['glass'].replace('_', ' ')}, a recessed plinth and shadow gaps (31 Oct 2026)")
    return out


def look_overrides(piece: dict) -> dict:
    """``{material key: {"slug", "asset", "colour"}}`` of a built-in see-through run's look (pure; 31 Oct 2026): its
    shell on ``front`` (the end panels, the fascia, the slats), its veneer on ``wood`` (inside), its metal on ``handle``
    (the frames, the beads, the track, the grip channels); {} for another piece. The build lays them over the design's
    (``furniture.design_overrides``)."""
    st = piece.get("see_through") if isinstance(piece.get("see_through"), dict) else {}
    look = st.get("look") if isinstance(st.get("look"), dict) else None
    if not look or st.get("kind") not in FRONT_KINDS:
        return {}
    try:
        from wenart.style import vocabulary as V
        table = {**V.MATERIALS, **V.FURNITURE_MATERIALS}
    except Exception:  # noqa: BLE001 - without the style tables the style's keys stay
        return {}

    def entry(slug, colour=None):
        if slug not in table:
            return None
        return {"slug": slug, "asset": table[slug].get("asset"), "colour": colour}

    out = {"front": entry(look.get("shell_slug"), look.get("colour")), "wood": entry(look.get("wood")),
           "handle": entry(look.get("metal"))}
    return {k: v for k, v in out.items() if v is not None}


def family_of(style) -> str:
    if isinstance(style, str):
        return style.strip().lower()
    return str((style or {}).get("family") or "").strip().lower()


def is_see_through(piece: dict) -> bool:
    """A wardrobe built with a see-through or open front (``see_through.kind`` one of ``FRONT_KINDS``)."""
    rec = piece.get("see_through") if isinstance(piece.get("see_through"), dict) else {}
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    return rec.get("kind") in FRONT_KINDS or design.get("see_through") in FRONT_KINDS


def _area(room: dict) -> float:
    try:
        return abs(G.polygon_area(room.get("polygon") or []))
    except (TypeError, ValueError):
        return 0.0


def _size(piece: dict) -> tuple[float, float]:
    fp = piece.get("footprint") or {}
    s = list(fp.get("size") or [0.0, 0.0])
    return float(s[0]), float(s[1])


def front_dir(piece: dict) -> Optional[tuple[float, float]]:
    """The unit plan direction a piece's front faces (``front_deg``: 0 = +X, counter-clockwise), None without one."""
    deg = piece.get("front_deg")
    if not isinstance(deg, (int, float)) or isinstance(deg, bool):
        return None
    a = math.radians(float(deg))
    return math.cos(a), math.sin(a)


def _front_line(piece: dict) -> Optional[tuple[tuple[float, float], tuple[float, float], float]]:
    """``(front centre, front direction, half length along the front)`` of a piece."""
    d = front_dir(piece)
    fp = piece.get("footprint") or {}
    if d is None or not fp.get("center"):
        return None
    w, dep = _size(piece)
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    ux, uy = math.cos(rot), math.sin(rot)               # the footprint's width axis
    along = abs(ux * d[0] + uy * d[1])
    half_depth, half_len = (w / 2.0, dep / 2.0) if along > 0.7 else (dep / 2.0, w / 2.0)
    c = fp["center"]
    return (float(c[0]) + d[0] * half_depth, float(c[1]) + d[1] * half_depth), d, half_len


def facing_runs(building: dict, room: dict) -> list[tuple[str, str, float]]:
    """``[(id a, id b, aisle m)]``: the wardrobe runs of ``room`` whose fronts face each other across an aisle of
    ``AISLE_M`` (pure; front directions opposite within ``FACING_DEG``, overlapping along their runs by
    ``OVERLAP_SHARE``)."""
    robes = [f for f in building.get("furniture") or [] if f.get("room_id") == room.get("id")
             and str(f.get("type")) in WARDROBE_TYPES and f.get("build", True) is not False]
    out = []
    for i, a in enumerate(robes):
        la = _front_line(a)
        for b in robes[i + 1:]:
            lb = _front_line(b)
            if la is None or lb is None:
                continue
            (pa, da, ha), (pb, db, hb) = la, lb
            if da[0] * db[0] + da[1] * db[1] > -math.cos(math.radians(FACING_DEG)):
                continue
            gap = (pb[0] - pa[0]) * da[0] + (pb[1] - pa[1]) * da[1]
            if not AISLE_M[0] - 1e-9 <= gap <= AISLE_M[1] + 1e-9:
                continue
            t = (-da[1], da[0])
            sa, sb = pa[0] * t[0] + pa[1] * t[1], pb[0] * t[0] + pb[1] * t[1]
            ov = min(sa + ha, sb + hb) - max(sa - ha, sb - hb)
            if ov >= OVERLAP_SHARE * min(2 * ha, 2 * hb) - 1e-9:
                out.append((str(a["id"]), str(b["id"]), round(gap, 3)))
    return out


def walk_in(building: dict, room: Optional[dict]) -> Optional[str]:
    """Why ``room`` is a walk-in dressing room (a dressing room, or wardrobe runs facing each other), else None."""
    from wenart.blender import door_states as DS

    if room is None:
        return None
    if DS.is_dressing(building, room):
        return "a dressing room"
    pairs = facing_runs(building, room)
    if pairs:
        a, b, gap = pairs[0]
        return f"wardrobe runs {a} and {b} face each other across a {gap:.2f} m aisle"
    return None


def walk_in_front(building: dict, room: dict, style) -> tuple[str, str]:
    """``(kind, why)`` of a walk-in's fronts: the architect's answer (``room["wardrobe_fronts"]``), else the family's
    (``WALK_IN_FRONTS``)."""
    ans = room.get("wardrobe_fronts") if isinstance(room.get("wardrobe_fronts"), dict) else {}
    if ans.get("kind") in CHOICES:
        return ans["kind"], f"the architect's answer ({ans.get('by') or 'architect'}: {ans.get('reason') or ''})"
    fam = family_of(style)
    kind = WALK_IN_FRONTS.get(fam, WALK_IN_DEFAULT)
    return kind, f"the {fam or 'house'} family's walk-in front"


# = media_wall.MASTER_WORDS / MASTER_MIN_M2 (the furniture package needs shapely; Blender loads this module alone)
MASTER_WORDS: tuple[str, ...] = ("ebeveyn", "master", "parent", "parents", "suite", "principal", "eltern",
                                 "matrimonial", "matrimoniale", "hoofdslaapkamer", "e yatak")
MASTER_MIN_M2 = 12.0


def master_bedroom(rooms) -> Optional[dict]:
    """The master bedroom: the bedroom whose label names it (``MASTER_WORDS``, Turkish folded to ASCII), else the
    largest bedroom of at least ``MASTER_MIN_M2`` that is no child's room (as ``media_wall`` picks it)."""
    from wenart import textfold as B          # fold_ascii without jsonschema (Blender's Python)

    beds = [r for r in rooms if str(r.get("room_type") or "") == "bedroom" and r.get("room_subtype") != "child"]
    for r in sorted(beds, key=lambda r: str(r.get("id"))):
        words = " " + " ".join(B.fold_ascii(str(r.get("label") or "")).lower().replace(".", " ").split()) + " "
        if any(f" {w} " in words or words.strip().startswith(w) for w in MASTER_WORDS):
            return r
    big = sorted((r for r in beds if _area(r) >= MASTER_MIN_M2 - 1e-9), key=lambda r: (-_area(r), str(r.get("id"))))
    return big[0] if big else None


def plan(building: dict, style, notes: Optional[list] = None) -> dict:
    """``{piece id: {"kind", "room_id", "reason", "walk_in", "fit"}}`` of the wardrobes that get a see-through or open
    front (module docstring): ``fit`` is ``built_in_fit``'s record (the ends, the extension and its footprint).
    ``notes`` (a list) receives ``{"id", "room_id", "reason"}`` of every wardrobe run left free-standing and why (31 Oct
    2026: the cap of ``BUILT_IN_ROOMS_MAX`` rooms, no wall at either end)."""
    fam = family_of(style)
    if not fam:
        return {}
    notes = notes if notes is not None else []
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    robes = [f for f in building.get("furniture") or [] if str(f.get("type")) in WARDROBE_TYPES
             and f.get("build", True) is not False and f.get("room_id") in rooms]
    out: dict = {}
    keep_all, keep_why = sizes_kept(building)
    fit_of: dict = {}

    def fit(f) -> dict:
        if f["id"] not in fit_of:
            room = rooms[f["room_id"]]
            kept = keep_all or room_sizes_kept(building, room)
            fit_of[f["id"]] = built_in_fit(building, f, room, keep=kept, keep_why=keep_why if keep_all else
                                           "furnished_rooms_keep: the room keeps its drawn sizes")
        return fit_of[f["id"]]

    def fits(f) -> Optional[str]:
        from wenart.blender import modules as MOD

        rec = fit(f)
        if not rec["ok"]:
            return rec["why"]
        piece = dict(f, footprint=rec["footprint"]) if rec.get("footprint") else f
        w, d = _size(piece)
        if w < MIN_WIDTH_M - 1e-9:
            return f"{w:.2f} m wide: under the {MIN_WIDTH_M:.2f} m of two sliding panels"
        if d < MIN_DEPTH_M - 1e-9:
            return f"{d:.2f} m deep: no hanger fits across"
        if MOD.module_plan(dict(piece, see_through={"kind": "slats"})) is None:
            return "no wardrobe run of real frames fits its drawn size"
        return None

    def skip(f, reason: str) -> None:
        notes.append({"id": f["id"], "room_id": f.get("room_id"), "reason": reason})

    def forced(room) -> bool:            # an answer of the user or the AI architect (not the code's safe default)
        ans = room.get("wardrobe_fronts") if isinstance(room.get("wardrobe_fronts"), dict) else {}
        return ans.get("kind") in FRONT_KINDS and ans.get("by") not in (None, "architect")

    taken: list = []                      # the rooms with a built-in run, in the order they got it
    walk = {rid: walk_in(building, r) for rid, r in rooms.items() if any(f["room_id"] == rid for f in robes)}
    for rid in sorted((r for r in walk if walk[r]), key=lambda r: (not forced(rooms[r]), str(r))):
        room = rooms[rid]
        kind, src = walk_in_front(building, room, style)
        if kind == "closed":
            continue
        runs = []
        for f in (f for f in robes if f["room_id"] == rid):
            why = fits(f)
            if why is not None:
                skip(f, f"the walk-in's run stays as it is: {why}")
            else:
                runs.append(f)
        if not runs:
            continue
        if len(taken) >= BUILT_IN_ROOMS_MAX and not forced(room):
            for f in runs:
                skip(f, f"the house has its {BUILT_IN_ROOMS_MAX} rooms of built-in runs already "
                        f"({', '.join(taken)}): a free-standing wardrobe")
            continue
        taken.append(rid)
        for f in runs:
            out[f["id"]] = {"kind": kind, "room_id": rid, "walk_in": True, "fit": fit(f),
                            "reason": f"a walk-in ({walk[rid]}), see-through on every side: {FRONT_WHAT[kind]} with "
                                      f"real contents and a light inside ({src}; UL120, UL125)"}
    # 30 Oct 2026 (UL182): a bedroom's widest run, each bedroom its own front (``bedroom_front``); the master first (the
    # family's own front, UL120), a twin room with its partner (its partner's front). 31 Oct 2026: only while the house
    # has fewer than ``BUILT_IN_ROOMS_MAX`` rooms with one; the master's unit first, then the best fit (wall to wall,
    # the larger room, the wider run); a twin pair whole or not at all
    master = master_bedroom(rooms.values())
    elevation = {lv.get("id"): float(lv.get("elevation") or 0.0) for lv in building.get("levels") or []}
    beds = {rid: r for rid, r in rooms.items() if str(r.get("room_type") or "") == "bedroom" and not walk.get(rid)}
    units: dict = {}
    for rid, r in beds.items():
        partner = (r.get("scheme") or {}).get("copied_from")
        root = partner if partner in beds and partner != rid else rid
        units.setdefault(root, []).append(rid)
    best: dict = {}
    for rid in beds:
        cands = [f for f in robes if f["room_id"] == rid]
        ok = sorted((f for f in cands if fits(f) is None), key=lambda f: (-_size(f)[0], str(f.get("id"))))
        if ok:
            best[rid] = ok[0]
        elif cands:
            widest = sorted(cands, key=lambda f: (-_size(f)[0], str(f.get("id"))))[0]
            best[rid] = None
            fam_front = bedroom_front(beds[rid], style, (), beds[rid] is master)[0]
            if fam_front is not None:
                skip(widest, f"no built-in run here: {fits(widest)}; the fit's free-standing wardrobe stays")

    def has_master(root: str) -> bool:
        return any(beds[m] is master for m in units[root])

    def rank(root: str):
        room = beds[root]
        f = best.get(root)
        rec = fit(f) if f is not None else {}
        length = run_length(dict(f, footprint=rec.get("footprint") or f["footprint"])) if f is not None else 0.0
        return (not has_master(root), not forced(room), not rec.get("wall_to_wall"), -_area(room), -length,
                elevation.get(room.get("level_id"), 0.0), str(root))

    kinds: dict = {}
    for root in sorted(units, key=rank):
        members = [root] + sorted(r for r in units[root] if r != root)
        kind, why = bedroom_front(beds[root], style, list(kinds.values()), has_master(root))
        if kind is None:
            continue
        fronts = {root: (kind, why)}
        for rid in members[1:]:                      # a twin takes its partner's front (its own answer wins)
            fronts[rid] = bedroom_front(beds[rid], style, list(kinds.values()), beds[rid] is master, (root, kind))
        with_run = [rid for rid in members if best.get(rid) is not None and fronts[rid][0] is not None]
        if not with_run:
            continue
        if len(taken) + len(with_run) > BUILT_IN_ROOMS_MAX and not forced(beds[root]):
            for rid in with_run:
                skip(best[rid], f"the house has {len(taken)} of its {BUILT_IN_ROOMS_MAX} rooms of built-in runs "
                                f"({', '.join(taken) or 'none'}) and this room's unit needs {len(with_run)}: a "
                                "free-standing wardrobe (a built-in is an option for some rooms, not every bedroom's)")
            continue
        for rid in with_run:
            room = beds[rid]
            k, w = fronts[rid]
            kinds[rid] = k
            taken.append(rid)
            what = "the master bedroom's wardrobe run" if room is master else "the bedroom's wardrobe run"
            f = best[rid]
            out[f["id"]] = {"kind": k, "room_id": rid, "walk_in": False, "fit": fit(f),
                            "reason": f"{what} ({fam} style): {FRONT_WHAT[k]} with its garments and an LED strip "
                                      f"showing through, {w} (UL120, UL182; a built-in in {len(taken)} of at most "
                                      f"{BUILT_IN_ROOMS_MAX} rooms, {fit(f)['why']})"}
    return out


# ------------------------------------------------------------------------------------ the built-in's wall rule

def run_frame(piece: dict) -> Optional[dict]:
    """``{"c", "d", "t", "half_len", "half_depth", "len_axis"}`` of a wardrobe run (pure; 31 Oct 2026): its footprint
    centre, the unit direction its front faces, the unit direction along the run (``d`` turned left), half its length
    along the front and half its depth, and the index of the footprint's size along the run; None without a front or
    a footprint."""
    d = front_dir(piece)
    fp = piece.get("footprint") or {}
    if d is None or not fp.get("center") or len(fp.get("size") or []) < 2:
        return None
    w, dep = _size(piece)
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    along = abs(math.cos(rot) * d[0] + math.sin(rot) * d[1])     # the footprint's width axis along the front direction
    half_depth, half_len, axis = (w / 2.0, dep / 2.0, 1) if along > 0.7 else (dep / 2.0, w / 2.0, 0)
    c = fp["center"]
    return {"c": (float(c[0]), float(c[1])), "d": d, "t": (-d[1], d[0]), "half_len": half_len,
            "half_depth": half_depth, "len_axis": axis}


def run_length(piece: dict) -> float:
    """The length of a wardrobe run along its front (pure; 0 without a front)."""
    fr = run_frame(piece)
    return 2.0 * fr["half_len"] if fr is not None else 0.0


def _wall_poly(wall: dict) -> Optional[list]:
    try:
        s, e = (float(wall["start"][0]), float(wall["start"][1])), (float(wall["end"][0]), float(wall["end"][1]))
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    length = G.distance(s, e)
    if length < 1e-6:
        return None
    t = float(wall.get("thickness") or 0.1) / 2.0
    nx, ny = -(e[1] - s[1]) / length * t, (e[0] - s[0]) / length * t
    return [(s[0] + nx, s[1] + ny), (e[0] + nx, e[1] + ny), (e[0] - nx, e[1] - ny), (s[0] - nx, s[1] - ny)]


def _ray_into(p, u, poly) -> float:
    """How far a ray from ``p`` along ``u`` runs before it enters ``poly`` (0 inside it, inf when it misses)."""
    from wenart.blender import door_states as DS

    if G.point_in_polygon(p, poly):
        return 0.0
    return DS._ray_exit(p, u, poly)


def _passage_at(building: dict, level_id, point, wall_id=None) -> Optional[str]:
    """The id of a door or an opening (``PASSAGE_TYPES``) at ``point`` on a wall face (its width plus 2 cm along its
    wall, within the wall's half thickness plus 10 cm across), else None."""
    walls = {w.get("id"): w for w in building.get("walls") or []}
    for o in building.get("openings") or []:
        if o.get("level_id") != level_id or o.get("type") not in PASSAGE_TYPES or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        half = float(o.get("width") or 0.0) / 2.0 + 0.02
        c = (float(o["center"][0]), float(o["center"][1]))
        if w is not None and G.distance(w["start"], w["end"]) > 1e-6:
            s, e = w["start"], w["end"]
            length = G.distance(s, e)
            ux, uy = (e[0] - s[0]) / length, (e[1] - s[1]) / length
            along = (point[0] - c[0]) * ux + (point[1] - c[1]) * uy
            across = abs(-(point[0] - c[0]) * uy + (point[1] - c[1]) * ux)
            if abs(along) <= half and across <= float(w.get("thickness") or 0.2) / 2.0 + 0.10:
                return str(o.get("id"))
        elif G.distance(point, c) <= math.hypot(half, 0.2):
            return str(o.get("id"))
    return None


def _strip_poly(fr: dict, s: int, start: float, length: float, depth0: float, depth1: float) -> list:
    """The rectangle along the run's side ``s`` from ``start`` to ``start + length`` past the centre, from ``depth0``
    to ``depth1`` along the front direction (0 = the run's centre line)."""
    (cx, cy), d, t = fr["c"], fr["d"], fr["t"]
    u = (t[0] * s, t[1] * s)
    out = []
    for a, b in ((start, depth0), (start + length, depth0), (start + length, depth1), (start, depth1)):
        out.append((cx + u[0] * a + d[0] * b, cy + u[1] * a + d[1] * b))
    return out


def _door_blocks(building: dict, level_id) -> list[tuple[str, str, list]]:
    """The doors' approaches (their opening plus 5 cm, ``0.75`` m deep on both sides) and recorded open leaves and
    sweeps of a level: floor a wardrobe never takes (as ``walk_in_extras``)."""
    from wenart.blender import door_states as DS

    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id") is not None}
    out = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != level_id or w is None or o.get("type") not in PASSAGE_TYPES or not o.get("center"):
            continue
        fr = DS.leaf_frame(o, w)
        for s in (1.0, -1.0):
            out.append((f"{o['id']}:approach", "door", DS._strip(fr["c"][0], fr["c"][1], fr["u"], fr["n"],
                                                                 fr["w"] / 2.0 + 0.05, 0.75, s, fr["T"] / 2.0)))
        for key in ("leaf_polys", "sweeps"):
            for poly in (o.get("leaf_state") or {}).get(key) or []:
                out.append((f"{o['id']}:leaf", "door", [tuple(p) for p in poly]))
    return out


def run_ends(building: dict, piece: dict, room: Optional[dict] = None) -> list[dict]:
    """The two ends of a wardrobe run (pure; 31 Oct 2026, module docstring (2)): ``[{"side": -1 | 1, "gap_m", "touch",
    "wall", "passage"}]``: how far each end stands from the nearest wall face along the run (the room's outline or a
    wall of its level, looked for from ``END_SAMPLES`` across the run's depth), the wall it meets (a wall id or
    ``outline``), whether it stands against it (``END_TOUCH_M``, never at a doorway: ``passage``)."""
    fr = run_frame(piece)
    if fr is None:
        return []
    lid = piece.get("level_id")
    poly = [tuple(p[:2]) for p in (room or {}).get("polygon") or []]
    walls = [(w.get("id"), _wall_poly(w)) for w in building.get("walls") or [] if w.get("level_id") == lid]
    walls = [(wid, p) for wid, p in walls if p is not None]
    (cx, cy), d, t = fr["c"], fr["d"], fr["t"]
    out = []
    for s in (-1, 1):
        u = (t[0] * s, t[1] * s)
        best, hit_wall, hit_at = math.inf, None, None
        for k in END_SAMPLES:
            # each ray starts RAY_BACK_M inside the run (an end on the outline itself is inside and outside at once)
            p = (cx + u[0] * (fr["half_len"] - RAY_BACK_M) + d[0] * k * fr["half_depth"],
                 cy + u[1] * (fr["half_len"] - RAY_BACK_M) + d[1] * k * fr["half_depth"])
            cands = [(wid, _ray_into(p, u, wp)) for wid, wp in walls]
            if len(poly) >= 3:
                from wenart.blender import door_states as DS
                cands.append(("outline", DS._ray_exit(p, u, poly) if G.point_in_polygon(p, poly) else 0.0))
            for wid, g in cands:
                g = max(0.0, g - RAY_BACK_M)
                if g < best - 1e-9:
                    best, hit_wall, hit_at = g, wid, (p[0] + u[0] * (g + RAY_BACK_M), p[1] + u[1] * (g + RAY_BACK_M))
        passage = _passage_at(building, lid, hit_at, hit_wall) if hit_at is not None and best < math.inf else None
        out.append({"side": s, "gap_m": round(best, 4) if best < math.inf else None, "wall": hit_wall,
                    "passage": passage, "touch": best <= END_TOUCH_M + 1e-9 and passage is None})
    return out


def sizes_kept(building: dict) -> tuple[bool, str]:
    """``(True, why)`` when the brief keeps the drawn sizes (``furnished_rooms: keep`` or
    ``furnished_rooms_keep_size``; CLAUDE.md: then only the look, the orientation and clear errors change), else
    ``(False, "")``."""
    try:
        from wenart import views as V
        mode, _a = V.brief_setting(building, "furnished_rooms")
        keep_size, _b = V.brief_setting(building, "furnished_rooms_keep_size")
    except Exception:  # noqa: BLE001 - without the brief tables the default (complete) applies
        return False, ""
    if str(mode or "") == "keep":
        return True, "furnished_rooms: keep: the drawn sizes stay"
    if keep_size is True:
        return True, "furnished_rooms_keep_size: the drawn sizes stay"
    return False, ""


def room_sizes_kept(building: dict, room: dict) -> bool:
    """A room the brief's ``furnished_rooms_keep`` names (by id or label): its drawn sizes stay."""
    try:
        from wenart import views as V
        names, _a = V.brief_setting(building, "furnished_rooms_keep")
    except Exception:  # noqa: BLE001
        return False
    if not isinstance(names, (list, tuple)):
        return False
    names = {str(n).strip().lower() for n in names if n is not None}
    return bool(names) and (str(room.get("id") or "").lower() in names
                            or str(room.get("label") or "").strip().lower() in names)


def built_in_fit(building: dict, piece: dict, room: Optional[dict] = None, keep: bool = False,
                 keep_why: str = "") -> dict:
    """Whether a wardrobe run can be a built-in (pure; 31 Oct 2026, module docstring (2)): ``{"ok", "why", "ends",
    "extend": {side: metres}, "footprint": the extended footprint | None, "wall_to_wall"}``. An end within
    ``END_TOUCH_M`` of a solid wall stands against it; an end at most ``EXTEND_MAX_M`` from one is extended to it
    (``EXTEND_CLEAR_M`` short) when the strip lies in the room, no piece, wall-hung item or door approach is in it, no
    piece stands in the ``ACCESS_M`` of floor before it and no opening is on the wall behind it (``keep``: never). ``ok``
    when an end stands against a wall afterwards."""
    from wenart.blender import door_states as DS

    fr = run_frame(piece)
    ends = run_ends(building, piece, room)
    if fr is None or not ends:
        return {"ok": False, "why": "no front or footprint to place a built-in by", "ends": ends, "extend": {},
                "footprint": None, "wall_to_wall": False}
    lid = piece.get("level_id")
    poly = [tuple(p[:2]) for p in (room or {}).get("polygon") or []]
    others = [(pid, t, pp) for pid, t, pp in DS.piece_polys(building, lid) if pid != str(piece.get("id"))
              and t not in ("rug",)]
    doors = _door_blocks(building, lid)
    extend: dict = {}
    for e in ends:
        e["extend_m"] = None
        gap = e["gap_m"]
        if e["touch"] or gap is None or gap > EXTEND_MAX_M + 1e-9:
            continue
        if e["passage"] is not None:
            e["blocked"] = f"it ends at the doorway {e['passage']}"
            continue
        if keep:
            e["blocked"] = keep_why or "the drawn sizes stay"
            continue
        length = gap - EXTEND_CLEAR_M
        hd = fr["half_depth"]
        strip = _strip_poly(fr, e["side"], fr["half_len"], length, -hd, hd)
        inner = _strip_poly(fr, e["side"], fr["half_len"] + 0.01, max(0.0, length - 0.02), -hd + 0.01, hd - 0.01)
        if len(poly) >= 3 and not all(G.point_in_polygon(p, poly) for p in inner):
            e["blocked"] = "the strip to the wall leaves the room"
            continue
        hit = [pid for pid, _t, pp in others + doors if DS.overlap(strip, pp) > DS.HIT_M2]
        if hit:
            e["blocked"] = f"{', '.join(sorted(set(hit))[:3])} in the strip to the wall"
            continue
        access = _strip_poly(fr, e["side"], fr["half_len"], length, hd, hd + ACCESS_M)
        hit = [pid for pid, _t, pp in others if DS.overlap(access, pp) > DS.HIT_M2]
        if hit:
            e["blocked"] = f"its doors would open onto {', '.join(sorted(set(hit))[:3])}"
            continue
        behind = _opening_behind(building, lid, fr, e["side"], length)
        if behind is not None:
            e["blocked"] = f"{behind} on the wall behind the strip"
            continue
        e["extend_m"] = round(length, 4)
        extend[e["side"]] = round(length, 4)
    touch = [e for e in ends if e["touch"] or e.get("extend_m")]
    wall_to_wall = len(touch) == 2
    footprint = extended_footprint(piece, extend) if extend else None
    if not touch:
        gaps = ", ".join(f"{e['gap_m']:.2f} m" if e["gap_m"] is not None else "no wall" for e in ends)
        blocked = "; ".join(e["blocked"] for e in ends if e.get("blocked"))
        return {"ok": False, "ends": ends, "extend": {}, "footprint": None, "wall_to_wall": False,
                "why": f"neither end stands against a wall (gaps {gaps}" + (f"; {blocked}" if blocked else "") +
                       "): a built-in goes from wall to wall or from a wall, never floats mid-wall"}
    if wall_to_wall:
        why = "from wall to wall"
    else:
        why = "from the wall at one end to the middle of the wall"
    if extend:
        why += " (" + ", ".join(f"{m:.2f} m to the wall" for m in extend.values()) + " closed)"
    return {"ok": True, "ends": ends, "extend": extend, "footprint": footprint, "wall_to_wall": wall_to_wall,
            "why": why}


def _opening_behind(building: dict, level_id, fr: dict, s: int, length: float) -> Optional[str]:
    """The id of an opening (any type) on the back line of the run's extension strip on side ``s``, else None."""
    (cx, cy), d, t = fr["c"], fr["d"], fr["t"]
    u = (t[0] * s, t[1] * s)
    back = (cx - d[0] * fr["half_depth"], cy - d[1] * fr["half_depth"])
    for o in building.get("openings") or []:
        if o.get("level_id") != level_id or not o.get("center"):
            continue
        ox, oy = float(o["center"][0]) - back[0], float(o["center"][1]) - back[1]
        along, across = ox * u[0] + oy * u[1], ox * d[0] + oy * d[1]
        half = float(o.get("width") or 0.0) / 2.0
        if abs(across) <= BEHIND_OPENING_M and along + half > fr["half_len"] + 1e-6 \
                and along - half < fr["half_len"] + length - 1e-6:
            return str(o.get("id"))
    return None


def extended_footprint(piece: dict, extend: dict) -> dict:
    """The footprint of a run whose ends move out along the run by ``extend`` (``{-1 | 1: metres}``; pure): the
    centre shifts by half the difference, the size along the run grows by the sum."""
    fr = run_frame(piece)
    fp = dict(piece.get("footprint") or {})
    if fr is None or not extend:
        return fp
    lo, hi = float(extend.get(-1) or 0.0), float(extend.get(1) or 0.0)
    shift = (hi - lo) / 2.0
    c = fr["c"]
    size = [float(v) for v in fp["size"]]
    size[fr["len_axis"]] = round(size[fr["len_axis"]] + lo + hi, 4)
    fp["center"] = [round(c[0] + fr["t"][0] * shift, 4), round(c[1] + fr["t"][1] * shift, 4)]
    fp["size"] = size
    return fp


def _stable(text: str) -> int:
    import zlib
    return zlib.crc32(text.encode("utf-8")) & 0xFFFFFFFF


def bedroom_front(room: dict, style, taken=(), master: bool = False,
                  partner: Optional[tuple[str, str]] = None) -> tuple[Optional[str], str]:
    """``(kind, why)`` of a bedroom's wardrobe front (pure; 30 Oct 2026, UL182; module docstring): the architect's
    answer (``room["wardrobe_fronts"]``, ``closed`` included: None); None in a family without a see-through front
    (``BEDROOM_FRONTS``: the period homes keep closed fronts); the twin room's ``partner`` = (id, kind) front; the
    master bedroom the family's own (``FRONTS``); else the room scheme's (``wardrobe_front``, else ``SCHEME_FRONTS``
    of its bundle) when no other bedroom has it (``taken``), else the first of the family's fronts no other bedroom has,
    from a place the room's id picks; all taken: the scheme's, else that first one."""
    ans = room.get("wardrobe_fronts") if isinstance(room.get("wardrobe_fronts"), dict) else {}
    if ans.get("kind") in CHOICES:
        kind = None if ans["kind"] == "closed" else ans["kind"]
        return kind, f"the architect's answer ({ans.get('by') or 'architect'}: {ans.get('reason') or ''})"
    fam = family_of(style)
    options = BEDROOM_FRONTS.get(fam)
    if not options:
        return None, f"a {fam or 'house'} home keeps closed wardrobe fronts"
    if partner is not None and partner[1] in options:
        return partner[1], f"as its twin room {partner[0]}"
    if master:
        return options[0], f"the {fam} family's own front"
    scheme = room.get("scheme") if isinstance(room.get("scheme"), dict) else {}
    # 31 Oct 2026 (real04 run 20261030-181158-full): the bundle's current front first; a scheme recorded before UL207
    # still named the old one ("slats", "smoked_glass" of the bundles that keep closed fronts now)
    bundle = str(scheme.get("bundle") or "")
    pref = SCHEME_FRONTS[bundle] if bundle in SCHEME_FRONTS else scheme.get("wardrobe_front")
    # UL207 (user: "This is not mandatory it is optional"): besides the master, a bedroom gets a see-through front
    # only when its room scheme names one; a scheme of closed fronts, or none, keeps them closed
    if pref not in FRONT_KINDS:
        return None, ("its room scheme keeps closed fronts" if pref == "closed" else
                      "no room scheme asks for a see-through front") + " (an option, not every bedroom's; UL207)"
    if pref in options and pref not in taken:
        return pref, f"the room scheme's front ({scheme.get('bundle')})"
    start = _stable(str(room.get("id") or "")) % len(options)
    order = list(options[start:]) + list(options[:start])
    for kind in order:
        if kind not in taken:
            return kind, "a front no other bedroom of the house has"
    return (pref if pref in options else order[0]), "every front of the family is used once"


def ceiling_over(building: dict, piece: dict) -> Optional[float]:
    """The lowest ceiling over a piece's footprint above its floor (pure): its level's ``ceiling_height``, under a
    roof (``ceiling_planes``, set by ``build.prepare``) the lowest roof underside over the footprint's corners when
    lower; None without its level."""
    from wenart.blender import geom2d

    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == piece.get("level_id")), None)
    if level is None or level.get("ceiling_height") is None:
        return None
    out = float(level["ceiling_height"])
    planes = level.get("ceiling_planes")
    fp = piece.get("footprint") or {}
    if planes and fp.get("center"):
        corners = G.rotated_rectangle(fp["center"], list(fp.get("size") or [0.0, 0.0]),
                                      float(fp.get("rotation_deg") or 0.0))
        z0 = float(level.get("elevation") or 0.0)
        out = min([out] + [geom2d.raised_surface_z(planes, float(x), float(y), level.get("ceiling_dormers")) - z0
                           for x, y in corners])          # 31 Oct 2026: under a dormer its ceiling (dormers.py)
    return out


def to_ceiling(building: dict, piece: dict) -> tuple[Optional[float], str, list[dict]]:
    """``(ceiling_m, why, light moves)``: the height a see-through run's top box reaches (pure; UL182): the ceiling
    over it (``ceiling_over``) less ``CEILING_GAP_M``, when the box is ``TOP_BOX_M`` high (over the run's frames from
    ``modules.module_plan``: a drawn height kept, else the tallest frames that leave room for the box), no window lies
    within ``WINDOW_CLEAR_M`` of the run and every ceiling light over it (a track, a pendant) slides off it into its
    room, at most ``LIGHT_SHIFT_MAX_M`` along the run's front (``[{"id", "from", "to"}]``, ``apply`` moves them); else
    None, why not and no move."""
    from wenart.blender import door_spacing as DSP
    from wenart.blender import modules as MOD

    ceiling = ceiling_over(building, piece)
    if ceiling is None:
        return None, "no ceiling over the run", []
    top = round(ceiling - CEILING_GAP_M, 4)
    plan_ = MOD.module_plan(dict(piece, see_through={"kind": "slats", "ceiling_m": top}))
    if plan_ is None:
        return None, "no wardrobe run of real frames fits its drawn size", []
    box = top - float(plan_.get("carcass_m") or plan_["height_m"])
    if plan_.get("carcass_m") is None:
        return None, (f"the run reaches the ceiling already ({box:.2f} m)" if box < TOP_BOX_M[0]
                      else f"the ceiling is {box:.2f} m over the run (a tall room): no top box"), []
    fp = piece.get("footprint") or {}
    rot = float(fp.get("rotation_deg") or 0.0)
    grown = G.rotated_rectangle(fp["center"], [float(s) + 2 * WINDOW_CLEAR_M for s in fp.get("size") or [0.0, 0.0]],
                                rot)
    for o in building.get("openings") or []:
        if o.get("type") == "window" and o.get("level_id") == piece.get("level_id") and o.get("center") \
                and G.point_in_polygon(tuple(o["center"][:2]), grown):
            return None, f"window {o.get('id')} beside the run: it keeps its height", []
    run = G.rotated_rectangle(fp["center"], [float(s) + 2 * LIGHT_CLEAR_M for s in fp.get("size") or [0.0, 0.0]], rot)
    line, d = _front_line(piece), front_dir(piece)
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    moves = []
    for li in building.get("decor") or []:                      # a ceiling track or pendant over the run
        size = [float(s) for s in (li.get("size") or [])[:2]]
        if li.get("type") not in ("ceiling_light", "pendant_light") or li.get("level_id") != piece.get("level_id") \
                or not li.get("center") or len(size) < 2:
            continue
        lamp = G.rotated_rectangle(li["center"][:2], size, float(li.get("rotation_deg") or 0.0))
        if DSP.overlap_area(run, lamp) <= 1e-4:
            continue
        # slide it off the run into the room, square to the run's front
        shift = None if line is None else \
            line[0][0] * d[0] + line[0][1] * d[1] + LIGHT_CLEAR_M - min(p[0] * d[0] + p[1] * d[1] for p in lamp)
        to = None if shift is None else (float(li["center"][0]) + d[0] * shift, float(li["center"][1]) + d[1] * shift)
        room = rooms.get(li.get("room_id")) or rooms.get(piece.get("room_id")) or {}
        if shift is None or shift > LIGHT_SHIFT_MAX_M + 1e-9 or len(room.get("polygon") or []) < 3 \
                or not G.point_in_polygon(to, room["polygon"]):
            return None, f"light {li.get('id')} over the run: it keeps its height", []
        moves.append({"id": li.get("id"), "from": [round(float(c), 4) for c in li["center"][:2]],
                      "to": [round(to[0], 4), round(to[1], 4)], "shift_m": round(shift, 3)})
    why = f"a top box to the ceiling ({box:.2f} m of lidded boxes and baskets over the hanging bays)"
    if moves:
        why += "; " + ", ".join(f"light {m['id']} slid {m['shift_m']:.2f} m off the run" for m in moves)
    return round(top, 4), why, moves


def apply(building: dict, style) -> tuple[dict, list[dict]]:
    """Write ``plan`` into the pieces (in place): ``(plan, assumed entries)``. The piece is built by the wardrobe
    module builder (``asset.method: module``); the fitted library model it replaces stays in ``see_through.replaced``."""
    notes: list = []
    chosen = plan(building, style, notes)
    assumed = []
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    # 31 Oct 2026 (user: "Not every room needs this built in wardrobe"): every run left free-standing, and why
    for n in notes:
        assumed.append({"object": f"furn_{n['id']}", "field": "built_in", "value": "free-standing",
                        "reason": n["reason"], "parent": n["id"], "kind": "built_in_wardrobe"})
    for f in building.get("furniture") or []:
        rec = chosen.get(f.get("id"))
        if rec is None:
            continue
        # 31 Oct 2026 (user: "it needs to be wall to wall or from wall to middle"): a small gap to a side wall closes
        fit = rec.pop("fit", None) or {}
        if fit.get("footprint"):
            old_fp = dict(f["footprint"])
            f.setdefault("drawn_footprint", old_fp)
            f["footprint"] = dict(fit["footprint"])
            why = (f"the built-in run reaches its wall: {fit['why']} (a built-in goes from wall to wall or from a "
                   f"wall, never floats mid-wall; drawn_footprint kept)")
            label = {"by": "code", "rule": "built-in wardrobe wall to wall (31 Oct 2026)", "reason": why,
                     "evidence": {"ends": [{k: e.get(k) for k in ("side", "gap_m", "wall", "extend_m")}
                                           for e in fit.get("ends") or []],
                                  "from": old_fp, "to": dict(fit["footprint"])}}
            if isinstance(f.get("adjusted_by_ai"), dict):
                label["previous"] = [dict(f["adjusted_by_ai"])]
            f["adjusted_by_ai"] = label
            assumed.append({"object": f"furn_{f['id']}", "field": "footprint", "value": f["footprint"],
                            "reason": why, "parent": f["id"], "kind": "built_in_wardrobe"})
        rec["ends"] = fit.get("why")
        rec["wall_to_wall"] = bool(fit.get("wall_to_wall"))
        rec["extend"] = {str(k): v for k, v in (fit.get("extend") or {}).items()} or None
        rec["look"] = built_in_look(style)
        old = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        replaced = {k: old.get(k) for k in ("asset_id", "library", "method", "licence") if old.get(k) is not None}
        # 30 Oct 2026 (UL182): up to the ceiling (a top box behind the full-height doors), the glass of the glass
        # sections the family's
        ceiling, why_top, moves = to_ceiling(building, f)
        rec["ceiling_m"] = ceiling
        rec["reason"] += f"; {why_top}" if ceiling is not None else ""
        decor = {d.get("id"): d for d in building.get("decor") or []}
        for mv in moves:                                 # the lights over the run slide off it (logged)
            li = decor[mv["id"]]
            li["center"] = [mv["to"][0], mv["to"][1]] + list(li["center"][2:])
            li["reason"] = f"{li.get('reason') or 'light'}; slid {mv['shift_m']:.2f} m off the full-height wardrobe " \
                           f"{f['id']} (UL182)"
            assumed.append({"object": str(mv["id"]), "field": "center", "value": mv["to"],
                            "reason": f"slid {mv['shift_m']:.2f} m off the full-height wardrobe run {f['id']} (from "
                                      f"{mv['from']}; UL182)", "parent": f["id"], "kind": "see_through_front"})
        rec["light_moves"] = moves
        if rec["kind"] == "slats_glass":
            rec["glass"] = SECTION_GLASS.get(family_of(style), "smoked_glass")
        f["see_through"] = dict(rec, replaced=replaced or None,
                                palette=garment_palette(style, (rooms.get(f.get("room_id")) or {}).get("scheme")))
        design = dict(f.get("design") or {})
        design["see_through"] = rec["kind"]
        f["design"] = design
        w, d = _size(f)
        from wenart.blender import modules as MOD
        plan_ = MOD.module_plan(f)
        h = plan_["height_m"] if plan_ else f.get("height")
        h = float(h) if isinstance(h, (int, float)) and not isinstance(h, bool) else 2.2
        f["asset"] = {"library": "module", "method": "module", "asset_id": f"module:{f['type']}:wardrobe_run",
                      "bbox_m": [round(w, 4), round(d, 4), round(h, 4)],
                      "see_through": rec["kind"], "replaced": replaced or None, "reason": rec["reason"]}
        assumed.append({"object": f"furn_{f['id']}", "field": "see_through", "value": rec["kind"],
                        "reason": rec["reason"] + (f"; replaces the library model {replaced.get('asset_id')}"
                                                   if replaced.get("asset_id") else ""),
                        "parent": f["id"], "kind": "see_through_front"})
    return chosen, assumed


# ---------------------------------------------------------------------------------------- walk-in bench and mirror

def _edges(room: dict) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    if G.polygon_area(poly) < 0:
        poly = poly[::-1]                                 # counter-clockwise: the inward normal is the left one
    return [(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]


def _openings_on(building: dict, room: dict, a, b) -> list[tuple[float, float]]:
    """``[(t0, t1)]`` along the edge ``a`` -> ``b`` taken by the doors, windows and openings on it (with margins)."""
    length = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or not o.get("center"):
            continue
        c = o["center"]
        if G.point_segment_distance(c, a, b) > 0.35:
            continue
        t = (float(c[0]) - a[0]) * ux + (float(c[1]) - a[1]) * uy
        h = float(o.get("width") or 0.0) / 2.0 + OPENING_MARGIN_M
        out.append((t - h, t + h))
    return out


def _free_stretches(building: dict, room: dict, a, b, pieces, depth: float) -> list[tuple[float, float]]:
    """The stretches of the edge ``a`` -> ``b`` with no opening and no piece within ``depth`` of the wall."""
    length = G.distance(a, b)
    if length < 0.3:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    nx, ny = -uy, ux
    taken = list(_openings_on(building, room, a, b))
    for _pid, _t, poly in pieces:
        ts = [((p[0] - a[0]) * ux + (p[1] - a[1]) * uy, (p[0] - a[0]) * nx + (p[1] - a[1]) * ny) for p in poly]
        if min(off for _t2, off in ts) <= depth:
            taken.append((min(t for t, _o in ts), max(t for t, _o in ts)))
    taken.sort()
    out, cur = [], 0.0
    for t0, t1 in taken:
        if t0 > cur:
            out.append((cur, min(t0, length)))
        cur = max(cur, t1)
    if cur < length:
        out.append((cur, length))
    return [(max(0.0, x0), min(length, x1)) for x0, x1 in out if min(length, x1) - max(0.0, x0) > 1e-6]


def walk_in_extras(building: dict, room: dict, levels: Optional[dict] = None) -> dict:
    """``{"bench": piece | None, "mirror": record | None, "notes": [...]}`` of a walk-in dressing room (pure; module
    docstring). The bench (else a pouf) stands with its back on a free wall stretch, inside the room, clear of every
    piece, of the wardrobes' ``ACCESS_M``, of the doors' approaches and open leaves, with ``WALKWAY_M`` free in front;
    the mirror hangs on another free stretch at least ``MIRROR_M`` wide where no piece stands against the wall."""
    from wenart.blender import door_states as DS

    lid = room.get("level_id")
    pieces = [p for p in DS.piece_polys(building, lid)]
    blocks = list(pieces)
    for f in building.get("furniture") or []:                    # the wardrobes' access strips
        if f.get("room_id") != room.get("id") or str(f.get("type")) not in WARDROBE_TYPES:
            continue
        line = _front_line(f)
        if line is None:
            continue
        (fx, fy), d, half = line
        t = (-d[1], d[0])
        blocks.append((f"{f['id']}:access", "access", [
            (fx + t[0] * half, fy + t[1] * half), (fx - t[0] * half, fy - t[1] * half),
            (fx - t[0] * half + d[0] * ACCESS_M, fy - t[1] * half + d[1] * ACCESS_M),
            (fx + t[0] * half + d[0] * ACCESS_M, fy + t[1] * half + d[1] * ACCESS_M)]))
    walls = {w["id"]: w for w in building.get("walls") or []}
    for o in building.get("openings") or []:                      # the doors' approaches and open leaves
        w = walls.get(o.get("wall_id"))
        if o.get("level_id") != lid or w is None or o.get("type") not in ("door", "opening") or not o.get("center"):
            continue
        fr = DS.leaf_frame(o, w)
        for s in (1.0, -1.0):
            blocks.append((f"{o['id']}:approach", "door", DS._strip(fr["c"][0], fr["c"][1], fr["u"], fr["n"],
                                                                    fr["w"] / 2.0 + 0.05, 0.75, s, fr["T"] / 2.0)))
        for poly in (o.get("leaf_state") or {}).get("leaf_polys") or []:
            blocks.append((f"{o['id']}:leaf", "door", [tuple(p) for p in poly]))
        for poly in (o.get("leaf_state") or {}).get("sweeps") or []:
            blocks.append((f"{o['id']}:sweep", "door", [tuple(p) for p in poly]))
    notes: list[str] = []
    bench = None
    edges = _edges(room)
    stretches = []
    for a, b in edges:
        for t0, t1 in _free_stretches(building, room, a, b, pieces, 0.35):
            stretches.append((t1 - t0, a, b, t0, t1))
    stretches.sort(key=lambda s: -s[0])
    used = None
    for size, ftype in ((BENCH_M, "bench"), (POUF_M, "ottoman")):
        for _len, a, b, t0, t1 in stretches:
            w, dep, h = size
            if t1 - t0 < w + 0.02:
                continue
            length = G.distance(a, b)
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            nx, ny = -uy, ux
            tm = (t0 + t1) / 2.0
            cx = a[0] + ux * tm + nx * (dep / 2.0 + 0.01)
            cy = a[1] + uy * tm + ny * (dep / 2.0 + 0.01)
            rot = math.degrees(math.atan2(uy, ux)) + 180.0      # the piece's front (local -Y) into the room
            poly = [tuple(p) for p in G.rotated_rectangle((cx, cy), (w, dep), rot)]
            if not all(G.point_in_polygon(p, room["polygon"]) for p in poly):
                continue
            hit = [pid for pid, _t, pp in blocks if DS.overlap(poly, pp) > DS.HIT_M2]
            if hit:
                notes.append(f"a {ftype} on the free wall at {tm:.2f} m: {', '.join(hit[:3])} in the way")
                continue
            front = (cx + nx * dep / 2.0, cy + ny * dep / 2.0)
            free = DS._ray_exit(front, (nx, ny), room["polygon"])
            for _pid, _t, pp in pieces:
                free = min(free, DS._ray_exit(front, (nx, ny), pp) if not G.point_in_polygon(front, pp) else 0.0)
            if free < WALKWAY_M - 1e-9:
                notes.append(f"a {ftype} on the free wall at {tm:.2f} m: {free:.2f} m free in front of it "
                             f"(walkway {WALKWAY_M:.2f} m)")
                continue
            bench = {"id": f"{room['id']}__walkin_{ftype}", "type": ftype, "level_id": lid, "room_id": room["id"],
                     "source": "added_by_ai", "completes_room": True, "status": "verified",
                     "footprint": {"center": [round(cx, 4), round(cy, 4)], "size": [w, dep],
                                   "rotation_deg": round((rot) % 360.0, 3)},
                     "front_deg": round(math.degrees(math.atan2(ny, nx)) % 360.0, 3), "height": h,
                     "asset": None, "evidence": [{"file": "wardrobe_fronts", "method": "inferred", "confidence": 0.6,
                                                  "text": "walk-in dressing room: a seat to dress"}],
                     "added_by_ai": {"by": "code", "rule": "walk-in dressing room (UL125)",
                                     "reason": f"a {ftype} on the free wall, {free:.2f} m free in front of it, clear "
                                               "of the wardrobes and the doors"}}
            used = (a, b, t0, t1)
            break
        if bench is not None:
            break
    if bench is None:
        notes.append("no bench or pouf: the aisle and the free walls leave no place with the walkway free")
    mirror = None
    mw, mh, mb = MIRROR_M
    for _len, a, b, t0, t1 in stretches:
        if (a, b, t0, t1) == used and t1 - t0 < mw + BENCH_M[0] + 0.1:
            continue
        if t1 - t0 < mw + 0.04:
            continue
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = -uy, ux
        tm = (t0 + t1) / 2.0 if (a, b, t0, t1) != used else t1 - mw / 2.0 - 0.02
        level = (levels or {}).get(lid) or next((lv for lv in building.get("levels") or [] if lv.get("id") == lid), {})
        top = float(level.get("ceiling_height") or 2.5) - 0.05
        mirror = {"room_id": room["id"], "level_id": lid, "centre": [round(a[0] + ux * tm + nx * MIRROR_DEPTH_M / 2.0, 4),
                                                                     round(a[1] + uy * tm + ny * MIRROR_DEPTH_M / 2.0, 4)],
                  "rotation_deg": round((math.degrees(math.atan2(uy, ux)) + 180.0) % 360.0, 3), "width": mw,
                  "height": round(min(mh, top - mb), 3), "bottom": mb,
                  "reason": "a full-height mirror on a free wall of the walk-in dressing room (UL125)"}
        break
    if mirror is None:
        notes.append(f"no full-height mirror: no free wall stretch of {mw + 0.04:.2f} m")
    return {"bench": bench, "mirror": mirror, "notes": notes}


def mirror_parts(width: float, height: float) -> list[dict]:
    """A full-height mirror in its own frame (pure; width X, depth Y, front -Y, Z up from its bottom): a slim black
    frame (``dark``) round the mirror glass (``mirror``)."""
    from wenart.blender import parametric as P

    f, d = MIRROR_FRAME_M, MIRROR_DEPTH_M
    return [P._box(-(width / 2.0 - f / 2.0), 0.0, 0.0, f, d, height, "dark", "frame"),
            P._box(width / 2.0 - f / 2.0, 0.0, 0.0, f, d, height, "dark", "frame"),
            P._box(0.0, 0.0, 0.0, width - 2 * f, d, f, "dark", "frame"),
            P._box(0.0, 0.0, height - f, width - 2 * f, d, f, "dark", "frame"),
            P._box(0.0, -d / 2.0 + 0.004, f, width - 2 * f, 0.006, height - 2 * f, "mirror", "glass"),
            P._box(0.0, d / 4.0, f, width - 2 * f, d / 2.0, height - 2 * f, "dark", "back")]


def build_mirrors(mirrors: list[dict], level: dict, collection, mats, manifest_objects: list, assumed: list) -> list:
    """The walk-in mirrors of a level (``bpy``): one mesh object per mirror (its boxes), material keys through the
    furniture materials ``mats`` (``furniture._Materials``), a design detail (status assumed, its room the parent)."""
    from wenart.blender import common
    from wenart.blender import parametric as P

    made = []
    for m in mirrors:
        if m.get("level_id") != level["id"]:
            continue
        parts = mirror_parts(float(m["width"]), float(m["height"]))
        verts, faces, keys = P.world_mesh(parts, m["centre"], float(m["rotation_deg"]),
                                          float(level["elevation"]) + float(m["bottom"]))
        used = sorted(set(keys), key=keys.index)
        slots = [mats.get(k) for k in used]
        name = f"{m['room_id']}__walkin_mirror"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="decor",
                                    status="assumed", materials=slots, face_material_indices=[used.index(k) for k in keys])
        made.append(ob)
        manifest_objects.append({"name": name, "wenart_id": name, "element_id": name, "kind": "decor",
                                 "type": "mirror", "level_id": level["id"], "room_id": m["room_id"],
                                 "status": "assumed", "parent": m["room_id"], "evidence": [], "host_id": None,
                                 "source": "added_by_ai", "decor_method": "rule", "method": "walk_in",
                                 "material": slots[0].name if slots else None, "textured": False, "pass_index": None,
                                 "materials": [s.name for s in slots], "size": [m["width"], MIRROR_DEPTH_M,
                                                                                m["height"]],
                                 "rotation_deg": float(m["rotation_deg"]),
                                 "assumed": {"detail": "walk_in_mirror", "reason": m["reason"]}})
        assumed.append({"object": name, "field": "walk_in_mirror", "value": f"{m['width']} x {m['height']} m",
                        "reason": m["reason"], "parent": m["room_id"], "kind": "walk_in_mirror"})
    return made
