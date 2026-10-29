"""The bathroom and WC details of the user's reference photos (29 Oct 2026; lesson UL114, P4: "Look at the details in
the toilet analyze implement into the projects", "As much detail as you can digest"; lesson UL123, P12: "Look how
beautiful is this bathroom"; lesson UL124, P13: "Look how beautiful is this render take inspiration";
docs/reference_details_20261029.md rows B1-B26): the style families' bathroom table and the parts of every detail,
pure (no ``bpy``, no shapely: the build, the fit and the module builders import it).

The family table (``FAMILY_BATH``, one row per style family of ``wenart.style.vocabulary.STYLE_FAMILIES`` and organic
modern; an alias takes its family's row, an unknown family ``DEFAULT_FAMILY``'s, said in the reason):

| family | WC (B1) | vanity (B3 / B12 / B21) | basin (B15 / B23) | feature wall (B13 or B24) | mirror (B4 / B14 / B22) | column (B5) | finish | towels (B26) | wet tiles walls / floor (B8) | downlights / cove (B9) |
|---|---|---|---|---|---|---|---|---|---|---|
| modern | wall-hung | fluted, rounded ends | vessel, tall mixer | terrazzo panel behind the vanity | backlit rectangle | open, lit | black | rust | greige / grey | square black / yes |
| contemporary | wall-hung | fluted, rounded ends | vessel, tall mixer | terrazzo panel behind the vanity | backlit, rounded | open, lit | black | terracotta | greige / grey | square black / yes |
| modern minimal, minimal | wall-hung | stone slab | integrated | none | backlit rectangle | open, lit | chrome | sand | off white / light grey | square white / yes |
| scandinavian | wall-hung | stone slab | integrated | oak fluted wall behind the WC | round oak frame | open, lit | black | sage | light grey / grey | square black / yes |
| japandi, organic modern | wall-hung | curved front in a terrazzo apron | vessel, wall spout | dark fluted wall behind the WC | round oak frame | open, lit | black | olive / terracotta | sand / taupe | square black / yes |
| industrial | wall-hung | fluted, square ends | vessel, tall mixer | dark fluted wall behind the WC | LED band | open, lit | black | mustard | grey / dark grey | square black / no |
| classic | close-coupled (as fitted) | as drawn (the M10 vanity look) | as drawn | none | framed | closed | brass | navy | ivory / beige | round / no |
| rustic | close-coupled (as fitted) | as drawn | as drawn | none | framed | closed | black | rust | sand / taupe | round / no |
| mediterranean | close-coupled (as fitted) | as drawn | as drawn | none | framed | closed | brass | dusty blue | off white / terracotta | round / no |

Every family: a WC gets its paper holder and brush (B2), a bathroom its towel rail (B7), a towel shelf beside it
(B18) and towel bars at the door and at the shower (B25), a drawn shower a walk-in glass enclosure with its rain head,
hand shower, mixer and linear drain (B16), the vanity top two decor clusters (B19: a tall one of dried stems, a low
one of bottles and jars, never one item alone), all in the family's fixture finish (``FINISH_HANDLE`` /
``FINISH_COLOUR``; the door helper reads it for the door frames, B20) and every towel of the room in the family's one
accent colour (B26). One feature wall per bathroom: the vanity's panel (B13) or the fluted wall behind the WC (B24),
never both.

What each detail is (real sizes, PBR material keys; every repeated small item of a host is a part of its host's one
mesh, made from vertex and face lists, never a bpy operator and no ray per item: lesson UL111):

- B1 ``wall_hung_wc_parts``: a wall-hung pan (``WC_BOWL_M`` 0.36 x 0.54 m, rim at ``WC_RIM_M`` 0.40 m: a tapered body
  under a rounded rim), seat and closed lid, hinges, the wall bracket, and the flush plate of a concealed cistern on the
  wall over it (``FLUSH_PLATE_M`` 246 x 164 mm, the Geberit Sigma size, its bottom at ``FLUSH_PLATE_Z_M``) with two
  buttons, all inside the drawn footprint, the pan's back on the wall (on the fluted wall's face, B24).
- B3 ``stone_slab_vanity_parts``: a floating vanity on the drawn basin's footprint: a drawer box with a drawer front
  and a slim bar handle, an open shelf styled with rolled towels and lidded jars, a thick stone top
  (``VANITY_TOP_T_M`` 0.15 m) with the integrated basin carved into it, a wall-mounted mixer, an LED strip under it
  lighting the floor.
- B12 / B15 ``fluted_vanity_parts``: a floating vanity with rounded ends (soft-modern families), dark fluted fronts in
  the middle, open end cubbies with an LED strip under each shelf (rolled towels, bottles, a jar) where it is at least
  ``END_CUBBIES_MIN_W_M`` wide, a floor glow under it, a slim top (``FLUTED_TOP_T_M``) with rounded front corners in
  the panel's material (B13), a dark vessel basin with a tall deck mixer (B15).
- B21 / B23 ``curved_vanity_parts``: a floating vanity with a curved white front under a dark stone top, set into
  a terrazzo apron (the splashback on the wall and a plinth on the floor in one material), a white vessel basin with
  a wall-mounted spout.
- B19 ``top_clusters``: the top's decor in two clusters where its free strips hold them.
- B5 ``open_column_parts``: the storage column (UL102) as an open niche column: a dark frame on a recessed plinth, a
  wood back, ``COLUMN_CUBBY_M``-high cubbies with an LED strip under every shelf, each styled in turn (rolled towels,
  pump bottles in amber, black and white, a small plant, cotton stems in a vase, a jar of pebbles, perfume bottles,
  folded towels).
- B16 ``walk_in_shower_parts``: a low stone tray with a linear drain at the back wall, clear glass (a fixed panel, and
  a sliding one on a top rail with round rollers and a pull handle from ``SLIDING_MIN_W_M``), a square rain head on a
  wall arm, a hand shower on a slide rail with its hose, a thermostatic mixer and a towel bar inside.
- Mirrors: B4 ``led_mirror_parts`` (a frameless mirror with an inset light band), B14 ``backlit_mirror_parts`` (a large
  mirror, rounded corners for the soft families, an emissive panel behind it: a halo on the wall), B22
  ``round_mirror_parts`` (a round mirror in a thick oak frame).
- B2 ``paper_holder_parts`` and ``toilet_brush_parts``; B7 ``towel_rail_parts`` (a ladder radiator with a towel over a
  bar); B18 ``towel_shelf_parts`` (a shelf on brackets, a rail under it, rolled towels and a jar on it, a towel on the
  rail); B25 ``towel_bar_parts``; B13 / B24 ``feature_panel_parts`` (the panel behind the vanity, floor to ceiling, or
  the fluted wall behind the WC).
- B9 ``square_downlight_parts`` and ``cove_light_parts`` (a lowered ceiling band with an LED line in the slot between
  it and the wall; B17: a second band wraps the corner along the shower's wall).

The LED parts take the material key ``led`` (``materials.led_material``: a warm-white emission at
``materials.LED_EMISSION``, the radiance of a fixture shade, so the exposure stays the rig's); the finish parts the key
``handle`` on furniture (``looks.design_for`` sets the design's handle from ``finish_handle``) and ``colour_steel`` in
the finish's colour on decor (``FINISH_COLOUR``); the stone tops ``stone_light`` (marble), ``worktop`` (dark stone) or
``terrazzo``.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart.blender import parametric as P

Part = dict
LESSON = "UL114"
LESSONS: tuple[str, ...] = ("UL114", "UL123", "UL124")
RULE = "bathroom.ul114"
WET_ROOM_TYPES: tuple[str, ...] = ("bathroom", "wc")
TOWEL_RAIL_ROOM_TYPES: tuple[str, ...] = ("bathroom",)       # "every bathroom gets a towel rail" (B7)

# --------------------------------------------------------------------------
# The style families' bathroom (module docstring table)
# --------------------------------------------------------------------------

_SOFT = {"wc": "wall_hung", "vanity": "fluted", "rounded": True, "basin": "vessel", "feature": "vanity_panel",
         "panel": "terrazzo", "top_key": "terrazzo", "mirror": "backlit", "mirror_round": False, "column": "open_lit",
         "finish": "black", "wall_tile": "greige", "floor_tile": "grey", "downlight": "square_dark", "cove": True,
         "fluted_key": "dark", "towel_colour": "rust"}
_SLAB = dict(_SOFT, vanity="stone_slab", rounded=False, basin="integrated", feature=None, panel=None,
             top_key="stone_light", mirror="backlit", wall_tile="light grey", towel_colour="sage")
_ORGANIC = dict(_SOFT, vanity="curved", rounded=True, basin="vessel_wall", feature="wc_fluted", panel=None,
                top_key="worktop", apron="terrazzo", mirror="round_oak", wall_tile="sand", floor_tile="taupe",
                towel_colour="olive")
_CLASSIC = {"wc": "close_coupled", "vanity": "as_drawn", "rounded": False, "basin": "as_drawn", "feature": None,
            "panel": None, "top_key": "stone_light", "mirror": "framed", "mirror_round": False, "column": "closed",
            "finish": "brass", "wall_tile": "ivory", "floor_tile": "beige", "downlight": "round", "cove": False,
            "fluted_key": "dark", "towel_colour": "navy"}
FAMILY_BATH: dict[str, dict] = {
    "modern": dict(_SOFT),
    "contemporary": dict(_SOFT, mirror_round=True, towel_colour="terracotta"),
    "modern minimal": dict(_SLAB, finish="chrome", wall_tile="off white", floor_tile="light grey",
                           downlight="square_white", towel_colour="sand"),
    "minimal": dict(_SLAB, finish="chrome", wall_tile="off white", floor_tile="light grey", downlight="square_white",
                    towel_colour="sand"),
    "scandinavian": dict(_SLAB, mirror="round_oak", feature="wc_fluted", fluted_key="wood"),
    "japandi": dict(_ORGANIC),
    "organic modern": dict(_ORGANIC, towel_colour="terracotta"),
    "industrial": dict(_SOFT, rounded=False, feature="wc_fluted", panel=None, top_key="worktop", mirror="led",
                       wall_tile="grey", floor_tile="dark grey", cove=False, towel_colour="mustard"),
    "classic": dict(_CLASSIC),
    "rustic": dict(_CLASSIC, finish="black", wall_tile="sand", floor_tile="taupe", towel_colour="rust"),
    "mediterranean": dict(_CLASSIC, wall_tile="off white", floor_tile="terracotta", towel_colour="dusty blue"),
}
FAMILY_ALIASES: dict[str, str] = {"farmhouse": "rustic", "transitional": "classic", "coastal": "scandinavian",
                                  "boho": "rustic", "contemporary modern": "contemporary", "organic": "organic modern",
                                  "wabi sabi": "japandi"}
DEFAULT_FAMILY = "modern"
# the panel's material key (B13); the top takes the same material
PANEL_KEYS: dict[str, str] = {"terrazzo": "terrazzo", "stone": "stone_light", "fluted_dark": "dark", "fluted_wood": "wood"}
# the finish -> the design handle of a piece (finishes.CABINET_HANDLES keys) and the colour of a decor item's
# ``colour_steel`` parts (None: the brushed steel itself, the chrome look)
FINISH_HANDLE: dict[str, str] = {"black": "black", "brass": "brass", "chrome": "brushed_steel"}
FINISH_COLOUR: dict[str, Optional[str]] = {"black": "black", "brass": "brass", "chrome": None}


def family_name(style: Optional[dict]) -> Optional[str]:
    """The style family of a ``style.json`` profile (a list's first), lower case, or None."""
    profile = style[0] if isinstance(style, list) and style else style
    fam = (profile or {}).get("family") if isinstance(profile, dict) else None
    return str(fam).strip().lower() if fam else None


def spec_of(family: Optional[str]) -> tuple[dict, str]:
    """``(spec, why)``: the family's row of ``FAMILY_BATH`` (an alias's row; ``DEFAULT_FAMILY``'s for an unknown or
    missing family, assumed and said in ``why``). ``spec["family"]`` names the row used."""
    fam = str(family or "").strip().lower()
    fam = FAMILY_ALIASES.get(fam, fam)
    if fam in FAMILY_BATH:
        return dict(FAMILY_BATH[fam], family=fam), f"the {fam} family's bathroom (FAMILY_BATH)"
    return (dict(FAMILY_BATH[DEFAULT_FAMILY], family=DEFAULT_FAMILY),
            f"no bathroom row for the family {family!r}: the {DEFAULT_FAMILY} family's (assumed)")


def bath_look(piece: Optional[dict]) -> dict:
    look = (piece or {}).get("bath_look")
    return look if isinstance(look, dict) else {}


def made_to_measure(piece: dict) -> Optional[str]:
    """What of a piece's bathroom look is built from code by design (``bath_look``, written by the layout stage's
    ``wenart.furniture.bath_details.plan_building``): ``"wc"`` (a wall-hung WC), ``"vanity"`` (a floating vanity),
    ``"column"`` (an open lit niche column) or ``"shower"`` (a walk-in enclosure); None for a piece the library or its
    own builder makes."""
    look = bath_look(piece)
    if not look.get("made_to_measure"):
        return None
    ftype = piece.get("type")
    if ftype == "toilet" and look.get("wc") == "wall_hung":
        return "wc"
    if ftype == "washbasin" and look.get("vanity") in VANITY_KINDS:
        return "vanity"
    if ftype == "tall_cabinet" and look.get("column") == "open_lit":
        return "column"
    if ftype == "shower" and look.get("shower") == "walk_in":
        return "shower"
    return None


def finish_handle(piece: dict) -> Optional[str]:
    """The design handle of a piece's bathroom finish (``FINISH_HANDLE``), None without a bathroom look."""
    return FINISH_HANDLE.get(str(bath_look(piece).get("finish") or ""))


# --------------------------------------------------------------------------
# Wet-room tiles (B8): large-format stone-look porcelain on the walls and the floor
# --------------------------------------------------------------------------

LARGE_TILE_SLUG = "tiles_large_porcelain"       # wenart.style.finishes.TILE_PATTERNS: 60 x 120 cm, 2 mm grout
LARGE_TILE_PARAMS = {"pattern": "grid", "tile_size_m": [0.6, 1.2], "grout_m": 0.0015, "grout_colour": "light grey",
                     "variation": 0.05}         # a stone look: a wider tile-to-tile spread than plain porcelain's 0.02
DEFAULT_WET_SLUG = "tiles_light"                # vocabulary.WET_WALLS_MATERIAL / WET_FLOOR_DEFAULT


def _default_wet(slot) -> bool:
    """A wet-room slot the brief did not choose: the default light tiles with no colour, asset, size or pattern."""
    if not isinstance(slot, dict):
        return slot is None
    return (slot.get("material") in (None, DEFAULT_WET_SLUG) and not slot.get("colour") and not slot.get("asset")
            and not slot.get("tile_size_m") and not slot.get("pattern") and not slot.get("grout_colour"))


def wet_tile_look(style: Optional[dict], surface: str) -> Optional[dict]:
    """The family's large-format stone-look tile of a wet room's ``surface`` (``walls`` or ``floor``) as a style slot
    (``material``, ``colour``, ``params``, ``reason``), or None: no family, or the brief chose its own wet tiles
    (the brief wins)."""
    fam = family_name(style)
    if not fam:
        return None
    slot = (style or {}).get("wet_walls" if surface == "walls" else "wet_floor")
    if not _default_wet(slot):
        return None
    spec, why = spec_of(fam)
    colour = spec["wall_tile" if surface == "walls" else "floor_tile"]
    return {"material": LARGE_TILE_SLUG, "asset": None, "colour": colour, "params": dict(LARGE_TILE_PARAMS),
            "reason": f"{why}: large-format stone-look porcelain 60 x 120 cm in {colour} on the {surface}"
                      + (", floor to ceiling" if surface == "walls" else "")
                      + " (UL114 B8; the brief names no wet-room tiles)"}


# --------------------------------------------------------------------------
# Small mesh helpers (one part per call, vertex and face lists)
# --------------------------------------------------------------------------

def _stick(x0: float, y0: float, z0: float, dx: float, dy: float, length: float, r: float, key: str,
           role: str = "stick") -> Part:
    """A thin square prism of ``length`` from ``(x0, y0, z0)`` leaning by ``(dx, dy)`` per metre of height (a reed, a
    dried stem)."""
    n = math.sqrt(1.0 + dx * dx + dy * dy)
    top = (x0 + dx * length / n, y0 + dy * length / n, z0 + length / n)
    verts = []
    for cx, cy, cz in ((x0, y0, z0), top):
        verts += [(cx - r, cy - r, cz), (cx + r, cy - r, cz), (cx + r, cy + r, cz), (cx - r, cy + r, cz)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _ball(cx: float, cy: float, z0: float, r: float, key: str, role: str = "ball") -> Part:
    return P._superellipsoid(cx, cy, z0, 2 * r, 2 * r, 2 * r, 1.0, 1.0, key, role, n_eta=6, n_om=8)


def _prism(outline, z0: float, z1: float, key: str, role: str) -> Part:
    """A vertical prism over a counter-clockwise outline ``[(x, y)]`` from ``z0`` to ``z1`` (outward faces)."""
    n = len(outline)
    verts = [(x, y, z0) for x, y in outline] + [(x, y, z1) for x, y in outline]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))
    faces.append(list(range(n - 1, -1, -1)))
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def rounded_outline(x0: float, x1: float, y0: float, y1: float, r_left: float, r_right: float,
                    n: int = 6) -> list[tuple[float, float]]:
    """A counter-clockwise rectangle outline ``x0..x1`` x ``y0..y1`` whose front corners (``y0``, the -Y side) are
    rounded by ``r_left`` / ``r_right`` (0: square)."""
    out = [(x0, y1)]
    if r_left > 1e-6:
        cx, cy = x0 + r_left, y0 + r_left
        out += [(cx + r_left * math.cos(math.pi + 0.5 * math.pi * k / n), cy + r_left * math.sin(math.pi + 0.5 * math.pi
                                                                                                * k / n))
                for k in range(n + 1)]
    else:
        out.append((x0, y0))
    if r_right > 1e-6:
        cx, cy = x1 - r_right, y0 + r_right
        out += [(cx + r_right * math.cos(1.5 * math.pi + 0.5 * math.pi * k / n),
                 cy + r_right * math.sin(1.5 * math.pi + 0.5 * math.pi * k / n)) for k in range(n + 1)]
    else:
        out.append((x1, y0))
    out.append((x1, y1))
    return out


def _rounded_slab_xz(cx: float, y_front: float, z0: float, w: float, t: float, h: float, r: float, key: str,
                     role: str) -> Part:
    """A slab standing in the XZ plane (a mirror): ``w`` x ``h`` with all four corners rounded by ``r``, its front face
    at ``y_front`` and ``t`` thick towards +Y. Built as a prism over the outline and turned about X (a proper rotation:
    the faces stay outward)."""
    r = max(0.0, min(r, w / 2.0 - 1e-4, h / 2.0 - 1e-4))
    lower = rounded_outline(-w / 2.0, w / 2.0, 0.0, h / 2.0, r, r)[1:-1]
    upper = [(x, h - y) for x, y in reversed(lower)]
    outline = lower + upper
    part = _prism(outline, 0.0, t, key, role)
    # (x, v, s) -> (x, y_front + s... ) with v -> z: rotate +90 degrees about X: (x, y, z) -> (x, -z, y)
    part["verts"] = [(cx + x, y_front + t - s, z0 + v) for x, v, s in part["verts"]]
    return part


def _vessel(cx: float, cy: float, z0: float, r: float, h: float, key: str, wall: float = 0.008, n: int = 24
            ) -> list[Part]:
    """An open round vessel basin (bowl) of radius ``r`` at its rim, ``h`` high, standing on ``z0``: outer side, rim,
    inner side and floor (one closed shell)."""
    rb = r * 0.72
    rings = [(rb, z0), (r, z0 + h), (r - wall, z0 + h), (rb - wall, z0 + wall)]
    verts = [(cx + rr * math.cos(2 * math.pi * i / n), cy + rr * math.sin(2 * math.pi * i / n), z) for rr, z in rings
             for i in range(n)]
    ob, ot, it, ib = (k * n for k in range(4))
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces += [[ob + i, ob + j, ot + j, ot + i], [ot + i, ot + j, it + j, it + i], [it + i, it + j, ib + j, ib + i]]
    faces.append([ib + i for i in range(n)])
    faces.append([ob + i for i in range(n - 1, -1, -1)])
    return [{"verts": verts, "faces": faces, "key": key, "role": "basin"},
            P._cylinder_z(cx, cy, z0 + wall, 0.018, 0.018, 0.002, "steel", "drain", n=12)]


def _bottle(cx: float, cy: float, z0: float, r: float, h: float, key: str, cap_key: str, pump: bool = False
            ) -> list[Part]:
    """A bottle: a body, a shoulder, a neck and a cap (a pump head with its nozzle when ``pump``)."""
    body_h = h * 0.72
    parts = [P._cylinder_z(cx, cy, z0, r, r, body_h, key, "bottle", n=14),
             P._frustum_z(cx, cy, z0 + body_h, r, r, r * 0.45, r * 0.45, h * 0.08, key, "bottle", n=14)]
    neck_z = z0 + body_h + h * 0.08
    if pump:
        parts.append(P._cylinder_z(cx, cy, neck_z, r * 0.42, r * 0.42, h * 0.08, cap_key, "cap", n=10))
        parts.append(P._cylinder_z(cx, cy, neck_z + h * 0.08, r * 0.2, r * 0.2, h * 0.07, cap_key, "pump", n=8))
        parts.append(P._box(cx, cy - r * 0.45, neck_z + h * 0.15 - 0.008, r * 0.25, r * 0.9, 0.008, cap_key,
                            "nozzle"))
    else:
        parts.append(P._cylinder_z(cx, cy, neck_z, r * 0.45, r * 0.45, h * 0.2, cap_key, "cap", n=10))
    return parts


def _towel_roll(x: float, y: float, z0: float, r: float, length: float, key: str = "towel") -> Part:
    """A rolled towel lying with its axis along the depth (Y), on ``z0``."""
    return P._cylinder_y(x, y - length / 2.0, z0 + r, r, r, length, key, "towel", n=14)


def _stems(cx: float, cy: float, z0: float, vase_r: float, vase_h: float, height: float) -> list[Part]:
    """A vase of dried stems (pampas, cotton): the vase, five leaning stems and a soft plume or a cotton boll on each."""
    parts = [P._frustum_z(cx, cy, z0, vase_r * 0.8, vase_r * 0.8, vase_r, vase_r, vase_h, "ceramic", "vase", n=16)]
    for k, (dx, dy) in enumerate(((-0.22, 0.05), (0.18, -0.06), (0.03, 0.2), (-0.08, -0.16), (0.25, 0.12))):
        length = height * (0.82 + 0.05 * k)
        stem = _stick(cx + dx * 0.02, cy + dy * 0.02, z0 + 0.02, dx * 0.35, dy * 0.35, length, 0.0018, "wood", "stem")
        parts.append(stem)
        tx, ty, tz = stem["verts"][4]
        if k % 2 == 0:                               # a pampas plume
            parts.append(P._superellipsoid(tx, ty, tz - 0.06, 0.03, 0.03, 0.09, 0.9, 1.0, "rattan", "plume",
                                           n_eta=6, n_om=8))
        else:                                        # a cotton boll
            parts.append(_ball(tx, ty, tz - 0.012, 0.016, "bedding", "cotton"))
    return parts


# --------------------------------------------------------------------------
# B1: the wall-hung WC with its flush plate
# --------------------------------------------------------------------------

WC_BOWL_M = (0.36, 0.54)          # a wall-hung pan: 355-370 x 530-540 mm (the common product range, assumed)
WC_RIM_M = 0.40                   # the rim's standard height (seat on top: about 0.42-0.44 m)
WC_BOTTOM_M = 0.20                # the pan's lowest point: free floor under it
FLUSH_PLATE_M = (0.246, 0.164, 0.008)   # Geberit Sigma plates: 246 x 164 mm (width x height), on the wall
FLUSH_PLATE_Z_M = 0.98            # its bottom (its centre about 1.06 m: B1 "about 1.0 m")


def wall_hung_wc_parts(w: float, d: float, h: float, wall_offset: float = 0.0) -> list[Part]:
    """A wall-hung WC in its drawn footprint ``w x d`` (piece frame: front -Y, the wall at +Y): the pan's back on the
    wall, seat and lid, hinges, the bracket and the flush plate over it (module docstring, B1); ``wall_offset``: the
    face of a feature wall in front of the wall (B24: the pan and the plate on the fluted wall). ``h`` (the type
    height) is not used: a wall-hung WC's heights are the product's."""
    back = d / 2.0 - max(0.0, min(float(wall_offset or 0.0), 0.06))
    bw = min(WC_BOWL_M[0], w - 0.02)
    bd = min(WC_BOWL_M[1], back + d / 2.0 - 0.01)
    cy = back - bd / 2.0
    parts = [
        P._superellipsoid(0.0, cy + 0.03, WC_BOTTOM_M, bw * 0.78, bd * 0.82, (WC_RIM_M - WC_BOTTOM_M) * 0.85,
                          0.6, 0.55, "ceramic", "bowl", n_eta=8, n_om=24),
        P._superellipsoid(0.0, cy, WC_RIM_M - 0.09, bw, bd, 0.09, 0.35, 0.6, "ceramic", "bowl", n_eta=8, n_om=24),
        P._box(0.0, back - 0.06, WC_BOTTOM_M + 0.06, bw * 0.72, 0.12, WC_RIM_M - WC_BOTTOM_M - 0.06, "ceramic",
               "back"),
        P._superellipsoid(0.0, cy - 0.01, WC_RIM_M, bw + 0.004, bd - 0.05, 0.02, 0.3, 0.6, "ceramic", "seat",
                          n_eta=6, n_om=24),
        P._superellipsoid(0.0, cy - 0.015, WC_RIM_M + 0.02, bw - 0.004, bd - 0.07, 0.028, 0.3, 0.6, "ceramic",
                          "lid", n_eta=6, n_om=24),
    ]
    for sx in (-1.0, 1.0):
        parts.append(P._cylinder_x(sx * 0.07 - 0.015, back - 0.065, WC_RIM_M + 0.02, 0.012, 0.012, 0.03, "handle",
                                   "hinge", n=10))
    pw, ph, pt = FLUSH_PLATE_M
    parts.append(P._box(0.0, back - pt / 2.0, FLUSH_PLATE_Z_M, pw, pt, ph, "handle", "plate"))
    bwid = (pw - 0.03) / 2.0
    for sx in (-1.0, 1.0):                         # dual flush: two buttons 2 mm proud of the plate
        parts.append(P._box(sx * (bwid / 2.0 + 0.005), back - pt - 0.001, FLUSH_PLATE_Z_M + 0.02, bwid, 0.002,
                            ph - 0.04, "steel", "button"))
    return parts


# --------------------------------------------------------------------------
# B3 / B12 / B15 / B19: the floating vanities
# --------------------------------------------------------------------------

VANITY_KINDS: tuple[str, ...] = ("stone_slab", "fluted", "curved")
VESSEL_BASINS: tuple[str, ...] = ("vessel", "vessel_wall")     # B15 (a tall deck mixer), B23 (a wall spout)
VANITY_TOP_T_M = 0.15             # B3: "a thick stone top (about 15 cm)"
FLUTED_TOP_T_M = 0.04             # B12/B13: a slim terrazzo or stone top
VANITY_SHELF_H_M = 0.20           # the open shelf under the top (rolled towels: about 0.10 m across)
VANITY_DRAWER_H_M = 0.18          # one drawer front under the shelf
FLUTED_BODY_H_M = 0.42            # B12: the fluted drawer box under the slim top
VANITY_BOARD_M = 0.02
VANITY_BOWL_M = (0.50, 0.32, 0.12)   # the integrated bowl's largest width, depth and depth (a double vanity: two)
VANITY_DOUBLE_FROM_M = 1.10
VESSEL_R_M = 0.20                 # B15: a vessel basin 40 cm across (the common round vessel), 13 cm high
VESSEL_H_M = 0.13
TALL_MIXER_H_M = 0.30             # B15: a tall deck mixer for a vessel basin
VANITY_W_RANGE_M = (0.40, 1.80)   # the drawn basin is a floating vanity's size (slim guest units are 0.40 x 0.32 m)
VANITY_D_RANGE_M = (0.32, 0.62)
END_CUBBIES_MIN_W_M = 1.20        # B12: open, lit end cubbies where the vanity is at least this wide
END_CUBBY_W_M = 0.26
ROUND_END_R_M = 0.12              # B12: the rounded ends' radius (at most half the depth)
FLUTE_W_M = 0.022                 # B12: the vertical ribs of a fluted front and their gap
FLUTE_GAP_M = 0.004
VANITY_TOP_DEFAULT_M = 0.85       # the basin's working top when the drawing gives none (schemas.HEIGHTS washbasin)
MIXER_SPOUT_OVER_M = 0.13         # the wall mixer's spout this far over the top (the mirror hangs 0.30 m over it)
LED_STRIP_M = (0.012, 0.006)      # an LED strip's width and thickness
SOAP_R_M = 0.033                  # a soap dispenser, a reed diffuser: real products (about 6.5-7 cm across)
DIFFUSER_R_M = 0.035
STEMS_H_M = 0.45                  # B19: the tall cluster's dried stems over the top


def vanity_layout(w: float, d: float, top_m: float, kind: str = "stone_slab", basin: str = "integrated") -> dict:
    """The heights and the basins of a floating vanity of ``w x d`` with its top at ``top_m`` (pure): ``bottom_m``,
    the ``(z0, z1)`` of its ``drawer`` / ``shelf`` (stone slab) or ``body`` (fluted) and ``top``, ``bowls`` ``[(x, y,
    bw, bd)]`` (an integrated bowl's box or a vessel's), the strips beside them (``side_m``), the end cubbies."""
    n = 2 if w >= VANITY_DOUBLE_FROM_M - 1e-9 and basin == "integrated" else 1
    if kind in ("fluted", "curved"):
        top_t = FLUTED_TOP_T_M
        body0 = top_m - top_t - FLUTED_BODY_H_M
        out = {"kind": kind, "bottom_m": round(body0, 4), "body": (body0, top_m - top_t), "top": (top_m - top_t, top_m)}
    else:
        top_t = VANITY_TOP_T_M
        shelf0 = top_m - top_t - VANITY_SHELF_H_M
        drawer0 = shelf0 - VANITY_DRAWER_H_M
        out = {"kind": kind, "bottom_m": round(drawer0, 4), "drawer": (drawer0, shelf0),
               "shelf": (shelf0, top_m - top_t), "top": (top_m - top_t, top_m)}
    if basin in VESSEL_BASINS:
        bw = bd = min(2 * VESSEL_R_M, d - 0.08, w / n - 0.20)
        by = -d / 2.0 + 0.04 + bd / 2.0 + max(0.0, (d - 0.08 - bd) * 0.35)
    else:
        # a slim vanity keeps 0.11 m strips beside its bowl for the top clusters (B19), the bowl at least 0.30 m
        bw = max(min(0.30, w / n - 0.16), min(VANITY_BOWL_M[0], w / n - 0.22))
        bd = min(VANITY_BOWL_M[1], d - 0.09)
        back = max(0.05, (d - bd) / 2.0 - 0.01)   # the wall side strip (the mixer is on the wall: a slim one)
        by = d / 2.0 - back - bd / 2.0
    xs = [0.0] if n == 1 else [-w / 4.0, w / 4.0]
    ends = kind == "fluted" and w >= END_CUBBIES_MIN_W_M - 1e-9
    out.update({"bowls": [(x, by, bw, bd) for x in xs], "basin": basin,
                "bowl_depth": min(VANITY_BOWL_M[2], top_t - 0.02) if basin not in VESSEL_BASINS else VESSEL_H_M,
                "side_m": round((w / n - bw) / 2.0, 4), "end_cubbies": ends,
                "end_w": min(END_CUBBY_W_M, w * 0.22) if ends else 0.0})
    return out


def _slab_top(w: float, d: float, lay: dict, key: str, r_front: float = 0.0) -> list[Part]:
    """The top: a solid slab (a vessel stands on it; front corners rounded by ``r_front``) or a slab with the
    integrated bowl(s) carved into it."""
    z0, z1 = lay["top"]
    t = z1 - z0
    if lay["basin"] in VESSEL_BASINS:
        return [_prism(rounded_outline(-w / 2.0, w / 2.0, -d / 2.0, d / 2.0, r_front, r_front), z0, z1, key, "top")]
    bowls = lay["bowls"]
    _x, by, bw, bd = bowls[0]
    y0, y1 = by - bd / 2.0, by + bd / 2.0
    parts = [P._box(0.0, (-d / 2.0 + y0) / 2.0, z0, w, y0 + d / 2.0, t, key, "top"),
             P._box(0.0, (y1 + d / 2.0) / 2.0, z0, w, d / 2.0 - y1, t, key, "top")]
    edges = [-w / 2.0] + sorted(v for x, _y, b, _d in bowls for v in (x - b / 2.0, x + b / 2.0)) + [w / 2.0]
    for k in range(0, len(edges) - 1, 2):
        a, b = edges[k], edges[k + 1]
        if b - a > 1e-6:
            parts.append(P._box((a + b) / 2.0, by, z0, b - a, bd, t, key, "top"))
    depth = lay["bowl_depth"]
    for x, y, b, dd in bowls:
        parts += P._basin(x, y, z1 - depth, b, dd, depth, 0.012, key)           # the bowl carved into the stone
        parts.append(P._box(x, y, z0, b, dd, t - depth, key, "top"))            # the stone under the bowl
        parts.append(P._cylinder_z(x, y + dd * 0.15, z1 - depth + 0.012, 0.02, 0.02, 0.002, "steel", "drain", n=16))
    return parts


def _wall_mixer(x: float, d: float, by: float, top_m: float) -> list[Part]:
    """A wall-mounted single-lever mixer over a bowl centred at ``(x, by)`` (key ``handle``: the finish)."""
    back = d / 2.0
    z = top_m + MIXER_SPOUT_OVER_M
    length = max(0.10, min(0.22, back - by))
    return [P._box(x, back - 0.005, z - 0.035, 0.07, 0.01, 0.07, "handle", "rosette"),
            P._cylinder_y(x, back - 0.005 - length, z, 0.011, 0.011, length, "handle", "spout", n=12),
            P._box(x, back - 0.035, z + 0.035, 0.012, 0.05, 0.012, "handle", "lever")]


def _tall_mixer(x: float, y: float, top_m: float, reach: float) -> list[Part]:
    """B15: a tall deck mixer standing on the top at ``(x, y)`` behind a vessel, its spout reaching ``reach`` forward."""
    h = TALL_MIXER_H_M
    return [P._cylinder_z(x, y, top_m, 0.022, 0.022, 0.012, "handle", "base", n=14),
            P._cylinder_z(x, y, top_m, 0.014, 0.014, h, "handle", "body", n=12),
            P._cylinder_y(x, y - reach, top_m + h - 0.022, 0.011, 0.011, reach, "handle", "spout", n=12),
            P._box(x + 0.022, y, top_m + h - 0.09, 0.03, 0.012, 0.012, "handle", "lever")]


def _shelf_styling(w: float, d: float, z0: float, z1: float, x0: Optional[float] = None,
                   x1: Optional[float] = None) -> tuple[list[Part], list[str]]:
    """Rolled towels and lidded jars on an open shelf from ``z0`` (its floor) to ``z1`` between ``x0`` and ``x1``
    (default: the vanity's inner width); ``(parts, items)``."""
    parts, items = [], []
    x0 = -w / 2.0 + VANITY_BOARD_M if x0 is None else x0
    x1 = w / 2.0 - VANITY_BOARD_M if x1 is None else x1
    inner = x1 - x0
    r = max(0.025, min(0.05, (z1 - z0 - 0.012) / 1.9, inner / 4.4))
    length = max(0.12, min(0.30, d - 0.08))
    x = x0 + r + 0.01
    rolls = 2 if inner >= 4 * r + 0.16 else 1
    for k in range(rolls):
        parts.append(_towel_roll(x + k * 2 * r, -0.005, z0, r, length))
        items.append("rolled towel")
    if rolls == 2 and z1 - z0 >= r * (2.0 + math.sqrt(3.0)) + 0.005:
        parts.append(_towel_roll(x + r, -0.005, z0 + r * math.sqrt(3.0), r, length))
        items.append("rolled towel")
    jx = x1 - 0.045
    for k, jh in enumerate((min(0.10, z1 - z0 - 0.03), min(0.075, z1 - z0 - 0.03))):
        cx = jx - k * 0.075
        if cx - 0.03 < x + 2 * r * rolls - r or jh < 0.04:
            break
        parts.append(P._cylinder_z(cx, -0.02, z0, 0.03, 0.03, jh, "glass", "jar", n=14))
        parts.append(P._cylinder_z(cx, -0.02, z0 + jh, 0.031, 0.031, 0.015, "wood", "lid", n=14))
        items.append("lidded jar")
    return parts, items


def top_clusters(w: float, d: float, lay: dict) -> tuple[list[Part], list[str]]:
    """B19 (and B6): the top's decor in two clusters, a tall one (dried stems in a vase, a reed diffuser) and a low one
    (a soap dispenser and a small jar or bottle), each on a free strip beside the basin(s) that holds it; never one
    item alone (a strip that holds one item only stays bare). ``(parts, items)``."""
    parts, items = [], []
    z = lay["top"][1]
    xs = [b[0] for b in lay["bowls"]]
    _x, by, bw, bd = lay["bowls"][0]
    left_x0, left_x1 = -w / 2.0 + 0.01, min(xs) - bw / 2.0 - 0.01
    right_x0, right_x1 = max(xs) + bw / 2.0 + 0.01, w / 2.0 - 0.01
    y0, y1 = -d / 2.0 + 0.03, d / 2.0 - 0.03
    if lay["basin"] == "integrated":                 # the strips beside the bowl are as deep as the bowl
        y0, y1 = by - bd / 2.0, by + bd / 2.0
    if lay.get("clusters_y0") is not None:           # a curved front recedes at the ends: the items stay on the top
        y0 = max(y0, float(lay["clusters_y0"]))
    depth = y1 - y0

    def strip(xa: float, xb: float) -> Optional[tuple[float, float]]:
        return (xa, xb) if xb - xa > 1e-6 else None

    left, right = strip(left_x0, left_x1), strip(right_x0, right_x1)
    # the tall cluster: a vase of dried stems (a wide strip) or a reed diffuser and its reeds; with a second item
    tall = left
    if tall is not None:
        sw = tall[1] - tall[0]
        cx = (tall[0] + tall[1]) / 2.0
        vr = min(0.05, sw / 2.0 - 0.005)
        if vr >= 0.03 and depth >= 2 * vr + 2 * DIFFUSER_R_M + 0.02:      # stems at the back, a diffuser in front
            vy = y1 - vr - 0.005
            parts += _stems(cx, vy, z, vr, 0.16, STEMS_H_M)
            dy = y0 + DIFFUSER_R_M + 0.005
            parts += _bottle(cx, dy, z, DIFFUSER_R_M * 0.85, 0.09, "terracotta", "dark")
            items += ["dried stems in a vase", "amber bottle"]
        elif sw >= 2 * DIFFUSER_R_M + 0.006 and depth >= 4 * DIFFUSER_R_M + 0.01:
            vy = y1 - DIFFUSER_R_M - 0.005
            parts += _bottle(cx, vy, z, DIFFUSER_R_M, 0.10, "terracotta", "dark")
            for k, (dx, dy) in enumerate(((-0.18, -0.1), (0.15, -0.12), (0.02, 0.2), (-0.1, 0.16), (0.2, 0.05))):
                parts.append(_stick(cx + dx * 0.01, vy + dy * 0.01, z + 0.07, dx, dy, 0.17 + 0.01 * k, 0.0018,
                                    "wood", "reed"))
            parts += _bottle(cx, y0 + DIFFUSER_R_M * 0.8 + 0.005, z, DIFFUSER_R_M * 0.8, 0.12, "dark", "handle",
                             pump=True)
            items += ["reed diffuser", "black pump bottle"]
    # the low cluster: a soap dispenser and a small jar
    low = right
    if low is not None:
        sw = low[1] - low[0]
        cx = (low[0] + low[1]) / 2.0
        if sw >= 2 * SOAP_R_M + 0.006 and depth >= 2 * SOAP_R_M + 0.07:
            parts += _bottle(cx, y1 - SOAP_R_M - 0.005, z, SOAP_R_M, 0.15, "dark", "handle", pump=True)
            parts.append(P._cylinder_z(cx, y0 + 0.032, z, 0.028, 0.028, 0.06, "glass", "jar", n=14))
            parts.append(P._cylinder_z(cx, y0 + 0.032, z + 0.06, 0.029, 0.029, 0.012, "wood", "lid", n=14))
            items += ["soap dispenser", "jar of cotton"]
    return parts, items


def stone_slab_vanity_parts(w: float, d: float, top_m: float, top_key: str = "stone_light") -> list[Part]:
    """B3: the floating vanity with its thick stone top and integrated basin (module docstring), in its box ``w x d``
    (front -Y, the wall +Y), its top at ``top_m``."""
    lay = vanity_layout(w, d, top_m, "stone_slab", "integrated")
    t = VANITY_BOARD_M
    z_d0, z_d1 = lay["drawer"]
    z_s0, z_s1 = lay["shelf"]
    parts = [P._box(0.0, 0.015, z_d0, w, d - 0.03, z_d1 - z_d0, "wood", "body"),          # the drawer box
             P._box(0.0, -d / 2.0 + 0.009, z_d0 + 0.003, w - 0.006, 0.018, z_d1 - z_d0 - 0.006, "front", "front"),
             P._box(0.0, -d / 2.0 - 0.004, (z_d0 + z_d1) / 2.0 - 0.006, min(0.25, w * 0.4), 0.008, 0.012, "handle",
                    "handle"),
             P._box(-w / 2.0 + t / 2.0, 0.005, z_s0, t, d - 0.01, z_s1 - z_s0, "wood", "side"),
             P._box(w / 2.0 - t / 2.0, 0.005, z_s0, t, d - 0.01, z_s1 - z_s0, "wood", "side"),
             P._box(0.0, d / 2.0 - 0.0075, z_s0, w - 2 * t, 0.015, z_s1 - z_s0, "wood", "back"),
             P._box(0.0, -d / 2.0 + 0.03, z_d0 - LED_STRIP_M[1], w - 0.04, LED_STRIP_M[0], LED_STRIP_M[1], "led",
                    "led")]
    parts += _slab_top(w, d, lay, top_key)
    for x, by, _bw, _bd in lay["bowls"]:
        parts += _wall_mixer(x, d, by, top_m)
    shelf, _a = _shelf_styling(w, d, z_s0, z_s1)
    top, _b = top_clusters(w, d, lay)
    return parts + shelf + top


def _fluted_front(x0: float, x1: float, y_face: float, z0: float, z1: float, key: str) -> list[Part]:
    """B12: vertical ribs over ``x0..x1`` in front of ``y_face`` (a dark backing behind them)."""
    parts = [P._box((x0 + x1) / 2.0, y_face - 0.003, z0, x1 - x0, 0.006, z1 - z0, "dark", "front")]
    n = max(1, int((x1 - x0 + FLUTE_GAP_M) // (FLUTE_W_M + FLUTE_GAP_M)))
    rib = (x1 - x0 - (n - 1) * FLUTE_GAP_M) / n
    for i in range(n):
        x = x0 + rib / 2.0 + i * (rib + FLUTE_GAP_M)
        parts.append(P._cylinder_y(x, y_face - 0.006 - 0.012, (z0 + z1) / 2.0, rib / 2.0, (z1 - z0) / 2.0, 0.012,
                                   key, "front", n=4) if False else
                     P._box(x, y_face - 0.006 - 0.006, z0, rib, 0.012, z1 - z0, key, "front"))
    return parts


def fluted_vanity_parts(w: float, d: float, top_m: float, top_key: str = "terrazzo", rounded: bool = True,
                        basin: str = "vessel") -> list[Part]:
    """B12 / B13 / B15 / B19: the floating vanity with rounded ends (``rounded``), dark fluted fronts in the middle,
    open lit end cubbies from ``END_CUBBIES_MIN_W_M``, a floor glow, a slim top in the panel's material with rounded
    front corners, a vessel basin with a tall mixer (``basin`` ``vessel``; else the integrated bowl and a wall mixer)
    and the top's two decor clusters, in its box ``w x d`` (front -Y, the wall +Y)."""
    lay = vanity_layout(w, d, top_m, "fluted", basin)
    z0, z1 = lay["body"]
    r = min(ROUND_END_R_M, d / 2.0 - 0.01) if rounded else 0.0
    t = VANITY_BOARD_M
    ew = lay["end_w"]
    mid0, mid1 = -w / 2.0 + ew, w / 2.0 - ew
    parts = [_prism(rounded_outline(-w / 2.0, w / 2.0, -d / 2.0, d / 2.0, r, r), z0, z0 + t, "dark", "bottom"),
             P._box(0.0, d / 2.0 - 0.008, z0 + t, w - 0.002, 0.016, z1 - z0 - t, "dark", "back")]
    # the middle: a drawer box with its fluted fronts (two drawers, split at mid-height)
    parts.append(P._box((mid0 + mid1) / 2.0, 0.014, z0 + t, mid1 - mid0, d - 0.028, z1 - z0 - t, "dark", "body"))
    zm = (z0 + t + z1) / 2.0
    for za, zb in ((z0 + t + 0.002, zm - 0.002), (zm + 0.002, z1 - 0.002)):
        parts += _fluted_front(mid0 + 0.003, mid1 - 0.003, -d / 2.0 + 0.028, za, zb, "front")
    if ew > 0:
        # the open end cubbies: a shelf at mid-height (rounded with the end), an LED strip under the top and the shelf
        for side in (-1.0, 1.0):
            xa, xb = (-w / 2.0, mid0) if side < 0 else (mid1, w / 2.0)
            rl, rr = (r, 0.0) if side < 0 else (0.0, r)
            parts.append(_prism(rounded_outline(xa, xb, -d / 2.0, d / 2.0 - 0.016, rl, rr), zm - t / 2.0,
                                zm + t / 2.0, "dark", "shelf"))
            parts.append(P._box((xa + xb) / 2.0 + side * 0.0, d / 2.0 - 0.016 - 0.004, z0 + t, xb - xa - 0.004,
                                0.008, z1 - z0 - t, "wood", "back"))
            for zl in (zm - t / 2.0, z1):
                parts.append(P._box((xa + xb) / 2.0, -d / 2.0 + 0.05, zl - LED_STRIP_M[1], max(0.04, xb - xa - 0.06),
                                    LED_STRIP_M[0], LED_STRIP_M[1], "led", "led"))
            lo, _a = _shelf_styling(w, d, z0 + t, zm - t / 2.0 - LED_STRIP_M[1], xa + 0.02, xb - 0.02)
            hi = _bottle((xa + xb) / 2.0 - 0.035, -0.02, zm + t / 2.0, 0.03, min(0.15, z1 - zm - 0.03),
                         "terracotta", "dark", pump=True)
            hi += [P._cylinder_z((xa + xb) / 2.0 + 0.045, -0.01, zm + t / 2.0, 0.032, 0.032,
                                 min(0.09, z1 - zm - 0.03), "glass", "jar", n=14)]
            parts += lo + hi
    # the floor glow: an LED strip under the bottom board at its front
    parts.append(P._box(0.0, -d / 2.0 + 0.04, z0 - LED_STRIP_M[1], w - 2 * r - 0.04 if r else w - 0.04,
                        LED_STRIP_M[0], LED_STRIP_M[1], "led", "led"))
    parts += _slab_top(w, d, lay, top_key, r)
    tz = lay["top"][1]
    for x, by, bw, bd in lay["bowls"]:
        if basin in VESSEL_BASINS:
            parts += _vessel(x, by, tz, bw / 2.0, VESSEL_H_M, "dark")
            if basin == "vessel_wall":
                parts += _wall_mixer(x, d, by, top_m + VESSEL_H_M - 0.03)
            else:
                my = min(d / 2.0 - 0.04, by + bd / 2.0 + 0.035)
                parts += _tall_mixer(x, my, tz, max(0.08, my - by))
        else:
            parts += _wall_mixer(x, d, by, top_m)
    top, _b = top_clusters(w, d, lay)
    return parts + top


CURVED_SIDE_SHARE = 0.40          # B21: the curved front's ends lie this share of the depth back from its apex
APRON_T_M = 0.015                 # B21: the terrazzo apron's splashback on the wall ...
APRON_OVER_TOP_M = 0.25           # ... up to this far over the top (under the mirror), and its plinth on the floor
APRON_PLINTH_M = 0.08
CURVED_TOP_T_M = 0.03


def curved_outline(w: float, y_back: float, y_apex: float, side_share: float = CURVED_SIDE_SHARE,
                   n: int = 14) -> list[tuple[float, float]]:
    """B21: a counter-clockwise plan outline with a straight back at ``y_back`` and a front arc through ``(0,
    y_apex)`` whose ends lie ``side_share`` of the depth further back (a circle through the three points)."""
    depth = y_back - y_apex
    y_side = y_apex + depth * side_share
    half = w / 2.0
    sag = y_side - y_apex
    radius = (half * half + sag * sag) / (2.0 * sag)
    cy = y_apex + radius
    a0 = math.atan2(y_side - cy, -half)
    a1 = math.atan2(y_side - cy, half)
    if a0 > a1:
        a0 -= 2 * math.pi
    pts = [(radius * math.cos(a0 + (a1 - a0) * k / n), cy + radius * math.sin(a0 + (a1 - a0) * k / n))
           for k in range(n + 1)]
    return [(-half, y_back)] + pts + [(half, y_back)]


def curved_vanity_parts(w: float, d: float, top_m: float, top_key: str = "worktop",
                        basin: str = "vessel_wall", apron_key: str = "terrazzo") -> list[Part]:
    """B21 / B23 / B19 (P13): the floating vanity with a curved front in white lacquer under a dark stone top (its ends
    rounded with the curve), set into its terrazzo apron (``apron_key``: the splashback on the wall up to
    ``APRON_OVER_TOP_M`` over the top and a plinth on the floor under the vanity, one material), lit from under it, a
    white vessel basin with a wall spout coming out of the splashback (``basin`` ``vessel_wall``; ``vessel``: a tall
    deck mixer) and the top's two clusters, in its box ``w x d`` (front -Y, the wall +Y)."""
    lay = vanity_layout(w, d, top_m, "curved", basin)
    lay["top"] = (top_m - CURVED_TOP_T_M, top_m)
    lay["clusters_y0"] = -d / 2.0 + d * CURVED_SIDE_SHARE + 0.02
    y_back = d / 2.0 - APRON_T_M
    z0 = lay["bottom_m"]
    outline = curved_outline(w, y_back, -d / 2.0)
    zt = top_m - CURVED_TOP_T_M
    parts = [P._box(0.0, d / 2.0 - APRON_T_M / 2.0, 0.0, w, APRON_T_M, top_m + APRON_OVER_TOP_M, apron_key,
                    "apron"),
             _prism(curved_outline(w * 0.86, y_back, -d / 2.0 + 0.06), 0.0, APRON_PLINTH_M, apron_key, "plinth"),
             _prism(outline, z0, zt, "painted", "body"),
             _prism([(x * 1.004, y - 0.002 if y < y_back - 1e-6 else y) for x, y in outline], (z0 + zt) / 2.0 - 0.003,
                    (z0 + zt) / 2.0 + 0.003, "dark", "groove"),
             _prism(outline, zt, top_m, top_key, "top"),
             P._box(0.0, -d / 2.0 + 0.06, z0 - LED_STRIP_M[1], w * 0.6, LED_STRIP_M[0], LED_STRIP_M[1], "led", "led")]
    for x, by, bw, bd in lay["bowls"]:
        parts += _vessel(x, by, top_m, bw / 2.0, VESSEL_H_M, "ceramic")
        if basin == "vessel_wall":
            parts += _wall_mixer(x, d - 2 * APRON_T_M, by, top_m + VESSEL_H_M - 0.03)
        else:
            my = min(y_back - 0.03, by + bd / 2.0 + 0.035)
            parts += _tall_mixer(x, my, top_m, max(0.08, my - by))
    top, _b = top_clusters(w, d - 2 * APRON_T_M, lay)
    return parts + top


def vanity_parts(w: float, d: float, top_m: float, look: Optional[dict] = None) -> list[Part]:
    """The floating vanity a piece's ``bath_look`` names (``vanity``: stone_slab | fluted)."""
    look = look or {}
    key = str(look.get("top_key") or "stone_light")
    if look.get("vanity") == "fluted":
        return fluted_vanity_parts(w, d, top_m, key, bool(look.get("rounded")), str(look.get("basin") or "vessel"))
    if look.get("vanity") == "curved":
        return curved_vanity_parts(w, d, top_m, key, str(look.get("basin") or "vessel_wall"),
                                   str(look.get("apron_key") or "terrazzo"))
    return stone_slab_vanity_parts(w, d, top_m, key)


def vanity_items(w: float, d: float, top_m: float, look: Optional[dict] = None) -> list[str]:
    """The styled items of a floating vanity (for the scene's design-detail record)."""
    look = look or {}
    kind = look.get("vanity") if look.get("vanity") in VANITY_KINDS else "stone_slab"
    lay = vanity_layout(w, d, top_m, kind, str(look.get("basin") or ("integrated" if kind == "stone_slab" else
                                                                      "vessel")))
    items = []
    if kind == "stone_slab":
        items += _shelf_styling(w, d, *lay["shelf"])[1]
    elif lay["end_cubbies"]:
        items += ["end cubbies: rolled towels, a pump bottle, a jar"] * 2
    if kind == "curved":
        items.append("terrazzo apron: splashback and plinth")
        lay["top"] = (top_m - CURVED_TOP_T_M, top_m)
        lay["clusters_y0"] = -d / 2.0 + d * CURVED_SIDE_SHARE + 0.02
        return items + top_clusters(w, d - 2 * APRON_T_M, lay)[1]
    return items + top_clusters(w, d, lay)[1]


def vanity_fits(w: float, d: float) -> Optional[str]:
    """Why a drawn basin of ``w x d`` (its width along the wall, its depth) has no room for a floating vanity, None when
    it has (``VANITY_W_RANGE_M``, ``VANITY_D_RANGE_M``)."""
    if not VANITY_W_RANGE_M[0] - 1e-9 <= w <= VANITY_W_RANGE_M[1] + 1e-9:
        return (f"the drawn basin is {w:.2f} m wide: a floating vanity needs "
                f"{VANITY_W_RANGE_M[0]:.2f}-{VANITY_W_RANGE_M[1]:.2f} m")
    if not VANITY_D_RANGE_M[0] - 1e-9 <= d <= VANITY_D_RANGE_M[1] + 1e-9:
        return (f"the drawn basin is {d:.2f} m deep: a floating vanity needs "
                f"{VANITY_D_RANGE_M[0]:.2f}-{VANITY_D_RANGE_M[1]:.2f} m")
    return None


# --------------------------------------------------------------------------
# B5: the open lit niche column with its toiletries
# --------------------------------------------------------------------------

COLUMN_CUBBY_M = 0.26             # about 6 cubbies in a 1.6 m column (the photo: 6-7 up to near the ceiling)
COLUMN_CUBBIES = (4, 7)
COLUMN_PLINTH_M = 0.06
COLUMN_BOARD_M = 0.02
CUBBY_STYLES = ("towels", "pump_bottles", "plant", "cotton", "pebbles", "perfume", "folded_towels")


def column_cubbies(h: float) -> int:
    n = int(round((h - COLUMN_PLINTH_M - COLUMN_BOARD_M) / COLUMN_CUBBY_M))
    return max(COLUMN_CUBBIES[0], min(COLUMN_CUBBIES[1], n))


def _cubby_items(style: str, iw: float, idp: float, z0: float, ch: float) -> list[Part]:
    """The items of one cubby (inner width ``iw``, depth ``idp``, floor ``z0``, height ``ch``), centred on x = 0."""
    h = ch - 0.03
    parts: list[Part] = []
    if style == "towels":
        r = min(0.05, h / 2.2, iw / 4.6)
        length = max(0.12, min(0.28, idp - 0.04))
        for k in (-1.0, 1.0):
            parts.append(_towel_roll(k * (r + 0.004), 0.0, z0, r, length))
    elif style == "pump_bottles":
        r = min(0.03, iw / 7.5)
        for k, key in zip((-1.0, 0.0, 1.0), ("terracotta", "dark", "ceramic")):
            parts += _bottle(k * (2 * r + 0.01), -0.01 + abs(k) * 0.02, z0, r, min(0.19, h * 0.95), key, "dark",
                             pump=True)
    elif style == "plant":
        r = min(0.06, iw / 3.2, idp / 3.0)
        pot = min(0.09, h * 0.4)
        parts += [P._cylinder_z(0.0, 0.0, z0, r * 0.85, r * 0.85, pot, "ceramic", "pot", n=16),
                  P._cylinder_z(0.0, 0.0, z0 + pot - 0.01, r * 0.75, r * 0.75, 0.01, "dark", "soil", n=12),
                  P._superellipsoid(0.0, 0.0, z0 + pot - 0.005, r * 2.0, r * 2.0, min(h - pot, r * 2.2), 0.9, 1.0,
                                    "green", "crown", n_eta=6, n_om=12)]
    elif style == "cotton":
        r = min(0.035, iw / 6.0)
        vh = min(0.12, h * 0.5)
        parts += [P._cylinder_z(0.0, 0.0, z0, r, r, vh, "glass", "vase", n=14)]
        for k, (dx, dy) in enumerate(((-0.25, 0.05), (0.2, -0.05), (0.02, 0.15))):
            length = max(0.05, min(h - 0.04, 0.26 + 0.03 * k))
            stem = _stick(dx * 0.01, dy * 0.01, z0 + 0.01, dx, dy, length, 0.0018, "wood", "stem")
            parts.append(stem)
            tx, ty, tz = stem["verts"][4]
            parts.append(_ball(tx + 0.0018, ty + 0.0018, tz - 0.012, 0.016, "bedding", "cotton"))
    elif style == "pebbles":
        r = min(0.045, iw / 4.5)
        jh = min(0.11, h * 0.6)
        parts += [P._cylinder_z(0.0, 0.0, z0, r, r, jh, "glass", "jar", n=16)]
        for k, (px, py, pz) in enumerate(((-0.4, -0.3, 0.0), (0.35, 0.2, 0.0), (0.0, 0.4, 0.0), (-0.1, -0.1, 0.4),
                                          (0.3, -0.35, 0.35))):
            pr = r * 0.28
            parts.append(P._superellipsoid(px * r, py * r, z0 + 0.004 + pz * r, pr * 2.2, pr * 1.8, pr * 1.2, 0.8,
                                           1.0, "dark" if k % 2 else "ceramic", "pebble", n_eta=4, n_om=8))
    elif style == "perfume":
        for px, bw, bh in ((-0.045, 0.045, 0.10), (0.04, 0.035, 0.08)):
            if abs(px) + bw / 2.0 > iw / 2.0 - 0.01:
                continue
            ph = min(bh, h * 0.7)
            parts.append(P._box(px, 0.0, z0, bw, bw * 0.6, ph, "glass", "perfume"))
            parts.append(P._cylinder_z(px, 0.0, z0 + ph, bw * 0.25, bw * 0.25, 0.025, "handle", "cap", n=10))
    elif style == "folded_towels":
        tw, td = min(0.30, iw - 0.03), min(0.25, idp - 0.04)
        for k in range(min(3, max(1, int(h / 0.046)))):
            parts.append(P._box(0.0, 0.0, z0 + k * 0.045, tw, td, 0.043, "towel", "towel"))
    return parts


def open_column_parts(w: float, d: float, h: float) -> list[Part]:
    """The open lit niche column of the module docstring (B5) in its box ``w x d x h`` (front -Y, the wall +Y)."""
    t = COLUMN_BOARD_M
    pl = COLUMN_PLINTH_M
    n = column_cubbies(h)
    z_b, z_t = pl + t, h - t
    ch = (z_t - z_b - (n - 1) * t) / n
    iw, idp = w - 2 * t, d - 0.012
    parts = [P._box(0.0, 0.03, 0.0, w - 0.03, d - 0.06, pl, "dark", "plinth"),
             P._box(-w / 2.0 + t / 2.0, 0.0, pl, t, d, h - pl, "dark", "side"),
             P._box(w / 2.0 - t / 2.0, 0.0, pl, t, d, h - pl, "dark", "side"),
             P._box(0.0, 0.0, pl, iw, d, t, "dark", "bottom"),
             P._box(0.0, 0.0, z_t, iw, d, t, "dark", "top"),
             P._box(0.0, d / 2.0 - 0.006, z_b, iw, 0.012, z_t - z_b, "wood", "back")]
    for k in range(n):
        z0 = z_b + k * (ch + t)
        z1 = z0 + ch
        if k < n - 1:
            parts.append(P._box(0.0, 0.0, z1, iw, d - 0.012, t, "dark", "shelf"))
        parts.append(P._box(0.0, -d / 2.0 + 0.025, z1 - LED_STRIP_M[1], iw - 0.02, LED_STRIP_M[0], LED_STRIP_M[1],
                            "led", "led"))
        style = CUBBY_STYLES[k % len(CUBBY_STYLES)]
        for part in _cubby_items(style, iw, idp, z0, ch - LED_STRIP_M[1]):
            parts.append(dict(part, verts=[(x, y - 0.006, z) for x, y, z in part["verts"]]))
    return parts


def column_items(h: float) -> list[str]:
    """The styled cubbies of a column of height ``h`` (for the scene's design-detail record)."""
    return [CUBBY_STYLES[k % len(CUBBY_STYLES)].replace("_", " ") for k in range(column_cubbies(h))]


# --------------------------------------------------------------------------
# B16: the walk-in shower
# --------------------------------------------------------------------------

SHOWER_TRAY_T_M = 0.025           # a low stone tray (almost flush)
GLASS_T_M = 0.008
SLIDING_MIN_W_M = 1.0             # a shower at least this wide gets a sliding panel on a top rail; a narrower one a
                                  # fixed walk-in screen (B16: "fixed or sliding by its width")
RAIN_HEAD_M = (0.25, 0.25, 0.008)    # a square rain head 25 cm
RAIN_HEAD_Z_M = 2.10
SLIDE_RAIL_Z_M = (1.00, 1.90)
MIXER_Z_M = 1.05
TOWEL_BAR_Z_M = 1.25


def walk_in_shower_parts(w: float, d: float, h: float) -> list[Part]:
    """B16: the walk-in shower in its drawn footprint ``w x d`` (front -Y, the back wall +Y): the tray and linear
    drain, the glass front (a fixed panel, a sliding one on a top rail with rollers and a pull handle when wide), the
    rain head on its arm, the hand shower on its rail with the hose, the thermostatic mixer and a towel bar."""
    h = max(1.9, float(h or 2.0))
    back = d / 2.0
    sliding = w >= SLIDING_MIN_W_M - 1e-9
    gy = -d / 2.0 + GLASS_T_M / 2.0 + (0.06 if sliding else 0.01)   # the sliding panel and its rollers inside too
    gh = min(h, 2.0) - SHOWER_TRAY_T_M
    parts = [P._box(0.0, 0.0, 0.0, w, d, SHOWER_TRAY_T_M, "stone_light", "tray"),
             P._box(0.0, back - 0.06, SHOWER_TRAY_T_M, w - 0.10, 0.05, 0.002, "steel", "drain")]
    if sliding:
        half = w / 2.0
        parts.append(P._box(-w / 4.0, gy, SHOWER_TRAY_T_M, half, GLASS_T_M, gh - 0.04, "glass", "glass"))
        parts.append(P._box(w / 4.0 - 0.03, gy - 0.022, SHOWER_TRAY_T_M + 0.01, half, GLASS_T_M, gh - 0.06, "glass",
                            "glass"))
        rail_z = SHOWER_TRAY_T_M + gh - 0.04
        parts.append(P._box(0.0, gy - 0.011, rail_z, w, 0.03, 0.03, "handle", "rail"))
        for rx in (w / 4.0 - 0.03 - half / 2.0 + 0.08, w / 4.0 - 0.03 + half / 2.0 - 0.08):
            parts.append(P._cylinder_y(rx, gy - 0.034, rail_z - 0.012, 0.022, 0.022, 0.008, "handle", "roller", n=16))
        parts.append(P._box(w / 4.0 - 0.03 - half / 2.0 + 0.06, gy - 0.034, 0.95, 0.018, 0.02, 0.35, "handle",
                            "handle"))
    else:
        sw = max(0.3, w * 0.7)
        parts.append(P._box(-w / 2.0 + sw / 2.0, gy, SHOWER_TRAY_T_M, sw, GLASS_T_M, gh, "glass", "glass"))
        parts.append(P._box(-w / 2.0 + sw / 2.0, gy, SHOWER_TRAY_T_M + gh - 0.02, sw, 0.02, 0.02, "handle", "rail"))
        parts.append(P._box(-w / 2.0 + sw - 0.01, gy, SHOWER_TRAY_T_M, 0.02, 0.03, gh, "handle", "profile"))
    # the rain head on its wall arm
    arm = max(0.15, min(0.40, d * 0.45))
    rw, rd, rt = RAIN_HEAD_M
    hz = min(RAIN_HEAD_Z_M, h + 0.15)
    parts += [P._box(0.0, back - 0.004, hz - 0.03, 0.06, 0.008, 0.06, "handle", "rosette"),
              P._cylinder_y(0.0, back - arm, hz, 0.011, 0.011, arm, "handle", "arm", n=10),
              P._box(0.0, back - arm, hz - rt - 0.01, min(rw, w - 0.1), min(rd, d - 0.2), rt, "handle", "head")]
    # the hand shower on its slide rail, its hose looping to the mixer
    sx = w / 2.0 - 0.18
    z0, z1 = SLIDE_RAIL_Z_M
    parts += [P._cylinder_z(sx, back - 0.03, z0, 0.009, 0.009, z1 - z0, "handle", "rail", n=10),
              P._box(sx, back - 0.015, z0, 0.03, 0.03, 0.02, "handle", "bracket"),
              P._box(sx, back - 0.015, z1 - 0.02, 0.03, 0.03, 0.02, "handle", "bracket"),
              P._cylinder_z(sx, back - 0.06, 1.55, 0.014, 0.014, 0.16, "handle", "hand_shower", n=12),
              P._cylinder_z(sx, back - 0.06, 1.71, 0.035, 0.035, 0.02, "handle", "hand_shower", n=16)]
    hose = [(sx, back - 0.06, 1.55), (sx - 0.04, back - 0.07, 1.30), (sx - 0.10, back - 0.08, 1.05),
            (sx - 0.18, back - 0.06, 0.95), (0.08, back - 0.05, MIXER_Z_M)]
    for (xa, ya, za), (xb, yb, zb) in zip(hose, hose[1:]):
        length = math.dist((xa, ya, za), (xb, yb, zb))
        if zb >= za:
            parts.append(_stick(xa, ya, za, (xb - xa) / max(1e-6, zb - za), (yb - ya) / max(1e-6, zb - za),
                                length, 0.006, "dark", "hose") if zb - za > 0.05 else
                         P._box((xa + xb) / 2.0, (ya + yb) / 2.0, min(za, zb) - 0.006, abs(xb - xa) + 0.012, 0.012,
                                0.012, "dark", "hose"))
        else:
            parts.append(_stick(xb, yb, zb, (xa - xb) / max(1e-6, za - zb), (ya - yb) / max(1e-6, za - zb), length,
                                0.006, "dark", "hose"))
    # the thermostatic mixer, the towel bar inside
    parts += [P._box(0.0, back - 0.03, MIXER_Z_M - 0.035, 0.30, 0.06, 0.07, "handle", "mixer"),
              P._cylinder_y(-0.11, back - 0.09, MIXER_Z_M, 0.025, 0.025, 0.03, "handle", "knob", n=16),
              P._cylinder_y(0.11, back - 0.09, MIXER_Z_M, 0.025, 0.025, 0.03, "handle", "knob", n=16)]
    if w >= 0.75:
        bx = -w / 2.0 + 0.30
        parts += [P._cylinder_x(bx - 0.18, back - 0.05, TOWEL_BAR_Z_M, 0.009, 0.009, 0.36, "handle", "towel_bar",
                                n=10),
                  P._cylinder_y(bx - 0.17, back - 0.05, TOWEL_BAR_Z_M, 0.007, 0.007, 0.05, "handle", "bracket", n=8),
                  P._cylinder_y(bx + 0.17, back - 0.05, TOWEL_BAR_Z_M, 0.007, 0.007, 0.05, "handle", "bracket", n=8),
                  P._box(bx, back - 0.05 - 0.016, TOWEL_BAR_Z_M - 0.40, 0.30, 0.006, 0.40, "towel", "towel")]
    return parts


# --------------------------------------------------------------------------
# Decor: B2 paper holder and brush, B7 towel rail, B18 towel shelf, B13 panel, B4 / B14 mirrors, B9 lights
# --------------------------------------------------------------------------

BATH_DECOR_TYPES: tuple[str, ...] = ("toilet_paper_holder", "toilet_brush", "towel_rail", "towel_shelf",
                                     "towel_bar", "feature_panel", "cove_light")
WALL_BATH_DECOR: tuple[str, ...] = ("toilet_paper_holder", "towel_rail", "towel_shelf", "towel_bar", "feature_panel",
                                    "cove_light")
FLOOR_BATH_DECOR: tuple[str, ...] = ("toilet_brush",)
PAPER_HOLDER_SIZE = (0.16, 0.13, 0.13)
PAPER_HOLDER_Z_M = 0.70           # its centre (B2: "about 0.7 m")
TOILET_BRUSH_SIZE = (0.09, 0.09, 0.38)    # a wall-side brush holder about 9 cm across
TOWEL_RAIL_SIZE = (0.50, 0.10, 1.20)   # a 500 x 1200 mm ladder radiator (the common size; assumed)
TOWEL_RAIL_BOTTOM_M = 0.15
TOWEL_SHELF_SIZE = (0.60, 0.25, 0.40)  # a 60 cm wall shelf on brackets, a rail under it, the towels on it (B18)
TOWEL_SHELF_BOTTOM_M = 1.25
TOWEL_BAR_SIZE = (0.60, 0.08, 0.45)    # B25: a 60 cm towel bar (at the box's top) with a towel hanging from it
TOWEL_BAR_BOTTOM_M = 0.62              # ... the bar about 1.05 m over the floor
FEATURE_PANEL_T_M = 0.015         # B13: a 15 mm slab on the wall
FLUTED_WALL_T_M = 0.02            # B24: the fluted wall behind the WC (ribs on a backing)
FLUTED_WALL_RIB_M = (0.03, 0.006)     # its ribs' width and gap
ROUND_MIRROR_D_M = (0.50, 0.80)   # B22: a round mirror's diameter (most of the vanity's width), its oak frame
ROUND_FRAME_M = 0.04
COVE_DEPTH_M = 0.30               # the lowered band's depth from the wall
COVE_DROP_M = 0.12                # its drop under the ceiling
COVE_SLOT_M = 0.05                # the slot between the band and the wall that holds the LED line
COVE_MIN_CEILING_M = 2.40         # a lower ceiling takes no band
LED_MIRROR_MAX_H = 1.0
LED_MIRROR_ASPECT = (1.25, 2.0)   # its height over its width: at least, at most
LED_BAND_INSET_M = 0.04
LED_BAND_W_M = 0.015
BACKLIT_MIRROR_MAX_W = 1.20       # B14: a large mirror (most of the vanity's width), 0.9 m high
BACKLIT_MIRROR_H = 0.90
BACKLIT_ROUND_R_M = 0.10
SQUARE_DOWNLIGHT_SIZE = (0.10, 0.10, 0.012)
DECOR_HEIGHTS = {"toilet_paper_holder": PAPER_HOLDER_SIZE[2], "toilet_brush": TOILET_BRUSH_SIZE[2],
                 "towel_rail": TOWEL_RAIL_SIZE[2], "towel_shelf": TOWEL_SHELF_SIZE[2], "towel_bar": TOWEL_BAR_SIZE[2],
                 "feature_panel": 2.5, "cove_light": COVE_DROP_M}


def paper_holder_parts(w: float, d: float, h: float) -> list[Part]:
    back = d / 2.0
    roll_r = min(0.055, h / 2.0 - 0.005, (d - 0.02) / 2.0)
    zc = max(roll_r, 0.025)                        # the box's bottom: the roll's (or the rosette's) lowest point
    ry = back - 0.012 - roll_r
    x_ros = -w / 2.0 + 0.025
    return [P._cylinder_y(x_ros, back - 0.012, zc, 0.025, 0.025, 0.012, "colour_steel", "rosette", n=16),
            P._cylinder_y(x_ros, ry, zc, 0.008, 0.008, back - 0.012 - ry, "colour_steel", "arm", n=8),
            P._cylinder_x(x_ros, ry, zc, 0.008, 0.008, w - 0.03, "colour_steel", "arm", n=8),
            P._cylinder_x(-w / 2.0 + 0.045, ry, zc, roll_r, roll_r, min(0.10, w - 0.06), "bedding", "roll", n=20),
            P._cylinder_x(-w / 2.0 + 0.044, ry, zc, 0.02, 0.02, min(0.102, w - 0.058), "terracotta", "core", n=12)]


def toilet_brush_parts(w: float, d: float, h: float) -> list[Part]:
    r = min(w, d) / 2.0
    holder = h * 0.82
    return [P._cylinder_z(0.0, 0.0, 0.0, r * 0.9, r * 0.9, holder, "colour_steel", "holder", n=20),
            P._cylinder_z(0.0, 0.0, holder, r * 0.92, r * 0.92, 0.008, "colour_steel", "lid", n=20),
            P._cylinder_z(0.0, 0.0, holder + 0.008, 0.009, 0.009, h - holder - 0.008 - 0.015, "colour_steel",
                          "handle", n=8),
            P._cylinder_z(0.0, 0.0, h - 0.015, 0.013, 0.013, 0.015, "colour_steel", "knob", n=10)]


def towel_rail_parts(w: float, d: float, h: float) -> list[Part]:
    back = d / 2.0
    y = back - 0.05
    r_up, r_bar = 0.016, 0.011
    parts = []
    for sx in (-1.0, 1.0):
        x = sx * (w / 2.0 - r_up)
        parts.append(P._cylinder_z(x, y, 0.0, r_up, r_up, h, "colour_steel", "upright", n=12))
        for zf in (0.12, 0.88):
            parts.append(P._cylinder_y(x, y, h * zf, 0.007, 0.007, back - y, "colour_steel", "bracket", n=8))
    n_bars = max(4, int((h - 0.08) / 0.11))
    for k in range(n_bars):
        z = 0.05 + k * (h - 0.10) / (n_bars - 1)
        parts.append(P._cylinder_x(-w / 2.0 + r_up, y, z, r_bar, r_bar, w - 2 * r_up, "colour_steel", "bar", n=10))
    zb = 0.05 + (n_bars - 3) * (h - 0.10) / (n_bars - 1)
    tw = min(0.40, w - 0.10)
    drop = min(0.45, zb - 0.05)
    parts += [P._box(0.0, y - r_bar - 0.006, zb - drop, tw, 0.008, drop, "colour_towel", "towel"),
              P._box(0.0, y + r_bar + 0.004, zb - drop * 0.8, tw, 0.006, drop * 0.8, "colour_towel", "towel"),
              P._box(0.0, y, zb + r_bar, tw, 2 * r_bar + 0.016, 0.008, "colour_towel", "towel")]
    return parts


def towel_shelf_parts(w: float, d: float, h: float) -> list[Part]:
    """B18: a wall shelf (its board at the top of the box) on two brackets, a rail under it with a towel on it, rolled
    towels and a jar on the board."""
    back = d / 2.0
    bt = 0.025
    items_h = min(0.11, h * 0.35)                  # the towels and the jar on the board, inside the box
    zb = h - items_h - bt
    parts = [P._box(0.0, 0.0, zb, w, d, bt, "colour_steel", "board")]
    bh = min(0.12, zb)
    for sx in (-1.0, 1.0):
        parts.append(P._box(sx * (w / 2.0 - 0.06), back - 0.06, zb - bh, 0.012, 0.12, bh, "colour_steel", "bracket"))
    ry = -d / 2.0 + 0.04
    rz = zb - min(0.10, zb * 0.5)                  # the rail under the board, the towel hanging from it
    parts.append(P._cylinder_x(-w / 2.0 + 0.04, ry, rz, 0.008, 0.008, w - 0.08, "colour_steel", "rail", n=10))
    for sx in (-1.0, 1.0):
        parts.append(P._cylinder_y(sx * (w / 2.0 - 0.045), ry, rz, 0.006, 0.006, back - ry - 0.06, "colour_steel",
                                   "arm", n=8))
    tw = min(0.40, w - 0.12)
    drop = rz
    parts += [P._box(0.0, ry - 0.012, rz - drop, tw, 0.006, drop, "colour_towel", "towel"),
              P._box(0.0, ry + 0.012, rz - drop * 0.8, tw, 0.006, drop * 0.8, "colour_towel", "towel"),
              P._box(0.0, ry, rz + 0.008, tw, 0.03, 0.006, "colour_towel", "towel")]
    top = zb + bt
    r = min(0.045, (d - 0.05) / 4.0, items_h / 2.0)
    for k in range(2):
        parts.append(_towel_roll(-w / 2.0 + 0.07 + k * (2 * r + 0.004), 0.0, top, r, min(0.22, d - 0.03),
                                 "colour_towel"))
    jh = max(0.02, min(0.09, items_h - 0.016))
    parts.append(P._cylinder_z(w / 2.0 - 0.07, 0.0, top, 0.035, 0.035, jh, "glass", "jar", n=14))
    parts.append(P._cylinder_z(w / 2.0 - 0.07, 0.0, top + jh, 0.036, 0.036, min(0.015, h - top - jh), "wood", "lid",
                               n=14))
    return parts


def feature_panel_parts(w: float, d: float, h: float, key: str = "terrazzo", fluted: bool = False) -> list[Part]:
    """B13: the feature panel on the vanity wall (its back on the wall, +Y), ``w`` wide and ``h`` high from the floor;
    B24 (``fluted``): the fluted wall behind the WC, vertical ribs on a backing in ``key``."""
    if not fluted:
        return [P._box(0.0, 0.0, 0.0, w, d, h, key, "panel")]
    back_t = d * 0.4
    parts = [P._box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, key, "panel")]
    rib, gap = FLUTED_WALL_RIB_M
    n = max(1, int((w + gap) // (rib + gap)))
    rw = (w - (n - 1) * gap) / n
    for i in range(n):
        x = -w / 2.0 + rw / 2.0 + i * (rw + gap)
        parts.append(P._box(x, -back_t / 2.0, 0.0, rw, d - back_t, h, key, "rib"))
    return parts


def towel_bar_parts(w: float, d: float, h: float) -> list[Part]:
    """B25: a towel bar at the top of its box (two wall posts) and a towel folded over it."""
    back = d / 2.0
    y = back - 0.05
    z = h - 0.02
    parts = [P._cylinder_x(-w / 2.0 + 0.02, y, z, 0.009, 0.009, w - 0.04, "colour_steel", "bar", n=10)]
    for sx in (-1.0, 1.0):
        parts.append(P._cylinder_y(sx * (w / 2.0 - 0.04), y, z, 0.007, 0.007, back - y, "colour_steel", "post", n=8))
        parts.append(P._cylinder_y(sx * (w / 2.0 - 0.04), back - 0.006, z, 0.02, 0.02, 0.006, "colour_steel",
                                   "rosette", n=12))
    tw = min(0.45, w - 0.12)
    drop = z                                       # the towel hangs down to the box's bottom
    return parts + [P._box(0.0, y - 0.016, z - drop, tw, 0.006, drop, "colour_towel", "towel"),
                    P._box(0.0, y + 0.014, z - drop * 0.75, tw, 0.006, drop * 0.75, "colour_towel", "towel"),
                    P._box(0.0, y, z + 0.009, tw, 0.036, 0.006, "colour_towel", "towel")]


def round_mirror_parts(w: float, d: float, h: float) -> list[Part]:
    """B22: a round mirror in a thick oak frame (its face -Y), ``w`` across (``h`` the same)."""
    r = min(w, h) / 2.0
    g = min(0.006, d / 4.0)
    return [P._cylinder_y(0.0, -d / 2.0 + g, r, r, r, d - g, "wood", "frame", n=48),
            P._cylinder_y(0.0, -d / 2.0, r, r - ROUND_FRAME_M, r - ROUND_FRAME_M, g + 0.001, "mirror", "glass", n=48)]


def led_mirror_parts(w: float, d: float, h: float) -> list[Part]:
    """B4: a frameless mirror (the glass on the front, -Y) on a dark back plate, a light band inset near its edges."""
    g = min(0.006, d / 3.0)
    i, b = LED_BAND_INSET_M, LED_BAND_W_M
    yb = -d / 2.0 - 0.0005                         # the band: 0.5 mm proud of the glass
    parts = [P._box(0.0, g / 2.0 + 0.002, 0.01, max(0.02, w - 0.03), max(0.004, d - g - 0.004), max(0.02, h - 0.02),
                    "dark", "back"),
             P._box(0.0, -d / 2.0 + g / 2.0, 0.0, w, g, h, "mirror", "glass")]
    if w > 2 * (i + b) + 0.05 and h > 2 * (i + b) + 0.05:
        parts += [P._box(0.0, yb, h - i - b, w - 2 * i, 0.001, b, "led", "led"),
                  P._box(0.0, yb, i, w - 2 * i, 0.001, b, "led", "led"),
                  P._box(-w / 2.0 + i + b / 2.0, yb, i + b, b, 0.001, h - 2 * (i + b), "led", "led"),
                  P._box(w / 2.0 - i - b / 2.0, yb, i + b, b, 0.001, h - 2 * (i + b), "led", "led")]
    return parts


def backlit_mirror_parts(w: float, d: float, h: float, rounded: bool = True) -> list[Part]:
    """B14: a large mirror (glass on the front, -Y), its corners rounded for the soft families, on an emissive panel
    set back from its edge: the halo of light on the wall behind it."""
    g = min(0.006, d / 3.0)
    r = BACKLIT_ROUND_R_M if rounded else 0.0
    inset = 0.03
    return [_rounded_slab_xz(0.0, -d / 2.0, 0.0, w, g, h, r, "mirror", "glass"),
            _rounded_slab_xz(0.0, -d / 2.0 + g + 0.002, inset, max(0.05, w - 2 * inset), max(0.004, d - g - 0.004),
                             max(0.05, h - 2 * inset), max(0.0, r - inset), "led", "led")]


def led_mirror_height(w: float, max_h: Optional[float] = None) -> float:
    """The height of an LED mirror ``w`` wide (B4: tall, up towards the ceiling): ``LED_MIRROR_ASPECT`` of its width
    up to ``LED_MIRROR_MAX_H``, at most ``max_h`` (the room under the ceiling)."""
    h = min(LED_MIRROR_MAX_H, max(w * LED_MIRROR_ASPECT[0], min(w * LED_MIRROR_ASPECT[1], LED_MIRROR_MAX_H)))
    if isinstance(max_h, (int, float)) and max_h > 0:
        h = min(h, float(max_h))
    return round(h, 4)


def square_downlight_parts(w: float, d: float, h: float, trim_key: str = "dark") -> list[Part]:
    """B9: a square recessed downlight in its box (bottom on z = 0, the ceiling at ``h``): the trim and the lens."""
    ring = min(h, 0.012)
    return [P._box(0.0, 0.0, h - ring, w, d, ring, trim_key, "trim"),
            P._box(0.0, 0.0, h - ring - 0.002, w * 0.62, d * 0.62, 0.004, "bulb", "bulb")]


def cove_light_parts(w: float, d: float, h: float) -> list[Part]:
    """B9: the lowered ceiling band ``w`` long, ``d`` deep from the wall (+Y) and ``h`` under the ceiling (its top at
    ``h``), the LED line in the slot between it and the wall."""
    slot = min(COVE_SLOT_M, d / 3.0)
    return [P._box(0.0, -slot / 2.0, 0.0, w, d - slot, h, "painted", "band"),
            P._box(0.0, d / 2.0 - slot / 2.0, h - 0.035, max(0.05, w - 0.04), LED_STRIP_M[0], LED_STRIP_M[1], "led",
                   "led")]


def decor_parts(dtype: str, w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The parts of a bathroom decor item (``BATH_DECOR_TYPES``, the LED and backlit mirrors, the square downlight)."""
    item = item or {}
    if dtype == "toilet_paper_holder":
        return paper_holder_parts(w, d, h)
    if dtype == "toilet_brush":
        return toilet_brush_parts(w, d, h)
    if dtype == "towel_rail":
        return towel_rail_parts(w, d, h)
    if dtype == "towel_shelf":
        return towel_shelf_parts(w, d, h)
    if dtype == "towel_bar":
        return towel_bar_parts(w, d, h)
    if dtype == "feature_panel":
        material = str(item.get("material") or "")
        return feature_panel_parts(w, d, h, PANEL_KEYS.get(material, "terrazzo"), material.startswith("fluted"))
    if dtype == "cove_light":
        return cove_light_parts(w, d, h)
    if dtype == "mirror" and item.get("fixture") == "backlit_mirror":
        return backlit_mirror_parts(w, d, h, bool(item.get("rounded")))
    if dtype == "mirror" and item.get("fixture") == "round_mirror":
        return round_mirror_parts(w, d, h)
    if dtype == "mirror":
        return led_mirror_parts(w, d, h)
    if dtype == "ceiling_light":
        trim = str(item.get("trim") or "square_dark")
        return square_downlight_parts(w, d, h, "dark" if trim == "square_dark" else "painted")
    raise KeyError(f"no bathroom decor builder for {dtype!r}")
