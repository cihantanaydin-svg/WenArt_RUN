"""Parquet floors: the style's own wood floor laid in herringbone or chevron (29 Oct 2026, lesson UL106; user, showing a
professional bedroom render: "I want my renders to be as professional as these ones").

What:

- ``family_pattern(style)``: the laying pattern of a style family's wood floor (``FAMILY_FLOOR_PATTERNS``: a modern,
  contemporary, Scandinavian or classic home lays its oak in herringbone, a Mediterranean one in chevron; a minimal,
  japandi, rustic or industrial one keeps long planks), with the reason; ``None`` when the brief opts out
  (``floor.pattern`` / ``floor_pattern`` ``plank`` / ``none``), names a floor that is no plank floor (tiles, stone, a
  wide plank, a herringbone or chevron photo of its own) or the family keeps planks.
- ``plan_rooms(building, style, decisions)``: ``{room id: record}`` of the rooms whose floor is laid in the pattern:
  every living room, dining room and bedroom on the style's plank floor (``PATTERN_ROOM_TYPES``), and the dry rooms
  joined to one of them by a doorless opening or a virtual separator (one continuous floor never changes its pattern
  at a line nobody sees); ``decisions`` (the decor stage's ``building["dressing"]["rooms"]``, read from the project's
  reference recipe) may switch a room's pattern off. The pattern runs along the room's longest wall
  (``angle_deg``), the joined rooms take their source room's angle. ``annotate(building, style)`` writes the records
  on the rooms as ``floor_pattern`` (the building as built keeps them: Argus and the model review read them).
- ``cell(pattern, x, y, params)``: where a floor point lies in its plank (pure Python): the plank id, the position
  along and across it (metres) and the seam share (1 on a joint). ``parquet_group(pattern)`` (bpy) is the same
  arithmetic as a shader node group (``wenart_parquet_<pattern>``: outputs ``Vector``, the point in the plank's own
  texture frame plus a per-plank random offset, ``Seam`` and ``Random``); ``wire(...)`` puts it between the floor
  material's UV map and its Mapping node, shades each plank (``TONE_SPREAD``) and darkens and grooves the joints
  (``SEAM_DARK``, a Bump node on the normal map).

How the plank looks: the veneer of the floor's wood tone (``vocabulary.veneer_for``: oak_veneer_01 for a light oak
floor; one seamless grain per plank, the grain along each plank) when its texture set is in the library, else the
floor's own photo; the floor's colour and albedo gain stay the floor slug's (``materials.MaterialLibrary.get``).

Why: the renders' floors were one long-strip oak photo in every room; a laid pattern is what reads as a designed
floor in the reference photos (the real06 bedroom recipe of 8 Scandinavian photos: light wood floors, herringbone in
the professional render). Every value is a designer value (assumed, recorded on the room and in the material record).

Herringbone (planks ``n = length / width`` widths long, ``n`` an integer): in the pattern frame (the floor turned by
``angle_deg``, in plank widths) the horizontal planks are ``[k + mn, k + mn + n] x [k - mn, k - mn + 1]`` and the
vertical ones ``[k + mn, k + mn + 1] x [k + 1 - mn, k + 1 - mn + n]`` (k, m integers): a point (u, v) lies on a
horizontal plank when ``(u - floor(v)) mod 2n < n``, else on a vertical one (``(v - floor(u) - 1) mod 2n < n``); the
tiling is exact (tests/test_ul106_professional.py samples it). Chevron: columns ``C = length x cos(a)`` wide whose
planks lean +a and -a in turn; a plank's rows are ``width / cos(a)`` apart along the column.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

PATTERNS: tuple[str, ...] = ("herringbone", "chevron")
FAMILY_FLOOR_PATTERNS: dict[str, str] = {"modern": "herringbone", "contemporary": "herringbone",
                                         "scandinavian": "herringbone", "classic": "herringbone",
                                         "mediterranean": "chevron"}
PATTERN_ROOM_TYPES: tuple[str, ...] = ("living", "dining", "bedroom")
# Dry rooms a patterned floor runs on into through a doorless opening (never a wet room, a kitchen or outside).
JOINED_ROOM_TYPES: tuple[str, ...] = ("living", "dining", "bedroom", "hall", "office", "child", "other", "storage")
# The plank floors (vocabulary slugs of long planks; a wide plank, a parquet photo and a slat wall stay as named).
PLANK_FLOOR_SLUGS: tuple[str, ...] = ("wood_oak_light", "wood_walnut", "wood_oak_natural", "wood_oak_whitewashed",
                                      "wood_oak_smoked", "wood_oak_grey", "wood_ash", "wood_bamboo")
OPT_OUT: tuple = (False, "none", "off", "plank", "planks", "straight", "long planks")
# Designer values (assumed): a 60 x 12 cm herringbone block (5 widths long), a 60 x 10 cm chevron plank cut at 45 deg.
PLANK: dict[str, dict] = {"herringbone": {"length_m": 0.60, "width_m": 0.12},
                          "chevron": {"length_m": 0.60, "width_m": 0.10, "cut_deg": 45.0}}
SEAM_M = 0.003                 # the joint's shaded band (each side of the edge)
TONE_SPREAD = 0.14             # each plank's tone: 1 +- half this
SEAM_DARK = 0.45               # the joint's darkening at its centre
BUMP_STRENGTH = 0.5
BUMP_DISTANCE_M = 0.0015
NOISE_OFFSETS = ((0.0, 0.0, 0.0), (17.31, 5.17, 3.71), (41.73, 23.19, 11.13))   # three independent random values


# --------------------------------------------------------------------------
# Which floors and rooms
# --------------------------------------------------------------------------

def _family(style: Optional[dict]) -> str:
    return str((style or {}).get("family") or "").lower()


def family_pattern(style: Optional[dict]) -> tuple[Optional[str], str]:
    """``(pattern or None, why)`` of the style's wood floor (module docstring)."""
    style = style or {}
    floor = style.get("floor") if isinstance(style.get("floor"), dict) else {}
    named = floor.get("pattern") if floor.get("pattern") is not None else style.get("floor_pattern")
    if named in OPT_OUT or (isinstance(named, str) and named.lower() in OPT_OUT):
        return None, f"the brief keeps the floor in planks (floor pattern {named!r})"
    slug = floor.get("material")
    if slug not in PLANK_FLOOR_SLUGS:
        return None, f"the style floor {slug!r} is no plank floor (kept as named)"
    if isinstance(named, str) and named.lower() in PATTERNS:
        return named.lower(), f"the brief lays the {slug} floor in {named.lower()}"
    fam = _family(style)
    pattern = FAMILY_FLOOR_PATTERNS.get(fam)
    if pattern is None:
        return None, f"the {fam or 'house'} style keeps long planks"
    return pattern, f"assumed: the {fam} style lays its {slug} floor in {pattern} (designer value, UL106)"


def room_axis_deg(polygon) -> float:
    """The direction of the room's longest edge (degrees in [0, 180)), the pattern's run."""
    best, angle = -1.0, 0.0
    n = len(polygon or [])
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        length = G.distance(a, b)
        if length > best + 1e-9:
            best, angle = length, math.degrees(math.atan2(float(b[1]) - float(a[1]), float(b[0]) - float(a[0])))
    return round(angle % 180.0, 3)


def _probe_rooms(building: dict, opening: dict) -> list[str]:
    """The rooms on the two sides of an opening (probes across its wall), else around its centre."""
    walls = {w["id"]: w for w in building.get("walls") or []}
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == opening.get("level_id")
             and len(r.get("polygon") or []) >= 3]
    c = opening.get("center") or [0.0, 0.0]
    c = (float(c[0]), float(c[1]))
    wall = walls.get(opening.get("wall_id") or "")
    if wall is not None and G.distance(wall["start"], wall["end"]) > 1e-6:
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        reach = float(wall.get("thickness") or 0.1) / 2.0 + 0.10
        probes = [(c[0] + nx * reach, c[1] + ny * reach), (c[0] - nx * reach, c[1] - ny * reach)]
    else:
        probes = [(c[0] + dx, c[1] + dy) for dx, dy in ((0.15, 0), (-0.15, 0), (0, 0.15), (0, -0.15))]
    out = []
    for p in probes:
        for r in rooms:
            if r["id"] not in out and G.point_in_polygon(p, r["polygon"]):
                out.append(r["id"])
    return out


def open_neighbours(building: dict) -> dict[str, set]:
    """``{room id: {room ids}}`` joined by a doorless opening or a virtual separator (one floor runs through)."""
    out: dict[str, set] = {}
    for o in building.get("openings") or []:
        if o.get("type") not in ("opening",) and not o.get("virtual"):
            continue
        ids = _probe_rooms(building, o)
        for a in ids:
            for b in ids:
                if a != b:
                    out.setdefault(a, set()).add(b)
    return out


def plan_rooms(building: dict, style: Optional[dict], decisions: Optional[dict] = None) -> dict[str, dict]:
    """``{room id: record}`` of the patterned floors (module docstring). A record: ``pattern``, ``angle_deg`` (the
    pattern's run), ``plank_m`` [length, width], ``reason`` and, for a joined room, ``joined_from``."""
    pattern, why = family_pattern(style)
    if pattern is None:
        return {}
    decisions = decisions if isinstance(decisions, dict) else {}
    rooms = {r["id"]: r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    spec = PLANK[pattern]
    out: dict[str, dict] = {}
    for rid, r in sorted(rooms.items()):
        dec = decisions.get(rid) if isinstance(decisions.get(rid), dict) else {}
        if r.get("room_type") not in PATTERN_ROOM_TYPES or ("floor_pattern" in dec and not dec["floor_pattern"]):
            continue
        reason = why + (f"; {dec['floor_pattern_why']}" if dec.get("floor_pattern_why") else "")
        out[rid] = {"pattern": pattern, "angle_deg": room_axis_deg(r["polygon"]),
                    "plank_m": [spec["length_m"], spec["width_m"]], "reason": reason}
    joined = open_neighbours(building)
    queue = sorted(out)
    while queue:
        src = queue.pop(0)
        for nb in sorted(joined.get(src) or ()):
            r = rooms.get(nb)
            if nb in out or r is None or r.get("room_type") not in JOINED_ROOM_TYPES:
                continue
            dec = decisions.get(nb) if isinstance(decisions.get(nb), dict) else {}
            if "floor_pattern" in dec and not dec["floor_pattern"]:
                continue
            out[nb] = dict(out[src], joined_from=src,
                           reason=f"one floor with {src} (a doorless opening joins them): {out[src]['reason']}")
            queue.append(nb)
    return out


def annotate(building: dict, style: Optional[dict]) -> list[dict]:
    """Write each patterned room's record on the room (``floor_pattern``; in place) and return the ``assumed``
    entries."""
    dressing = building.get("dressing") if isinstance(building.get("dressing"), dict) else {}
    plans = plan_rooms(building, style, dressing.get("rooms"))
    out = []
    for r in building.get("rooms") or []:
        rec = plans.get(r.get("id"))
        if rec is None:
            r.pop("floor_pattern", None)
            continue
        r["floor_pattern"] = rec
        out.append({"object": f"{r['id']}_floor", "field": "floor_pattern", "value": rec["pattern"],
                    "reason": rec["reason"], "parent": r["id"], "kind": "floor"})
    return out


def floor_params(room: Optional[dict]) -> Optional[dict]:
    """The material ``params`` of a room's patterned floor (``parquet`` key), None without a pattern."""
    rec = (room or {}).get("floor_pattern")
    if not isinstance(rec, dict) or rec.get("pattern") not in PATTERNS:
        return None
    length, width = (float(v) for v in rec.get("plank_m") or (PLANK[rec["pattern"]]["length_m"],
                                                              PLANK[rec["pattern"]]["width_m"]))
    angle = float(rec.get("angle_deg") or 0.0)
    # herringbone: the zigzag runs along the room's axis (the pattern frame turned 45 deg off it); chevron: the
    # columns' V points along it
    turn = (45.0 - angle) if rec["pattern"] == "herringbone" else (90.0 - angle)
    return {"parquet": {"pattern": rec["pattern"], "length_m": round(length, 4), "width_m": round(width, 4),
                        "turn_deg": round(turn % 360.0, 3)}}


# --------------------------------------------------------------------------
# The pattern's arithmetic (pure Python: the node group below is the same)
# --------------------------------------------------------------------------

def _fmod(a: float, b: float) -> float:
    return a - b * math.floor(a / b)


def ratio_of(length: float, width: float) -> int:
    """The herringbone's block length in widths (an integer, at least 2)."""
    return max(2, int(round(float(length) / float(width))))


def cell(pattern: str, x: float, y: float, params: dict) -> dict:
    """Where the floor point (x, y) lies (module docstring): ``{"plank": (kind, i, j), "along_m", "across_m",
    "seam"}``; ``params`` the ``parquet`` record of ``floor_params``."""
    t = math.radians(float(params.get("turn_deg") or 0.0))
    ct, st = math.cos(t), math.sin(t)
    xu, yv = x * ct - y * st, x * st + y * ct
    width = float(params["width_m"])
    if pattern == "herringbone":
        n = ratio_of(params["length_m"], width)
        u, v = xu / width, yv / width
        fv, fu = math.floor(v), math.floor(u)
        r = _fmod(u - fv, 2 * n)
        if r < n:
            plank, along, across = ("h", fv, math.floor((u - fv) / (2 * n))), r, v - fv
        else:
            s0 = v - fu - 1.0
            plank, along, across = ("v", fu, math.floor(s0 / (2 * n))), _fmod(s0, 2 * n), u - fu
        d = min(min(across, 1.0 - across) * width, min(along, n - along) * width)
        return {"plank": plank, "along_m": along * width, "across_m": across * width,
                "seam": max(0.0, 1.0 - d / SEAM_M)}
    a = math.radians(float(params.get("cut_deg") or PLANK["chevron"]["cut_deg"]))
    col = float(params["length_m"]) * math.cos(a)
    row = width / math.cos(a)
    c = math.floor(xu / col)
    xl = xu - c * col
    sign = 1.0 - 2.0 * _fmod(c, 2.0)
    vt = yv - sign * xl * math.tan(a)
    rr = math.floor(vt / row)
    across = (vt - rr * row) / row
    d = min(min(across, 1.0 - across) * width, min(xl, col - xl))
    return {"plank": ("c", c, rr), "along_m": xl / math.cos(a), "across_m": across * width,
            "seam": max(0.0, 1.0 - d / SEAM_M)}


# --------------------------------------------------------------------------
# bpy: the node group and its wiring into a floor material
# --------------------------------------------------------------------------

def parquet_group(pattern: str):
    """``wenart_parquet_<pattern>`` (created once per file; inputs Cos, Sin (the turn), Width, Length (herringbone:
    its block length in widths, ``ratio_of`` x width), Repeat (the plank texture's size), Seam, Tan, Column, Row
    (chevron); outputs Vector (metres, the plank's texture frame: across along X, along the plank along Y, the grain
    of a veneer), Seam, Random). Only Math (by input index), Separate / Combine XYZ, White Noise and the group sockets:
    the arithmetic of ``cell``."""
    import bpy

    from wenart.blender.materials import _Graph, _new_group

    name = f"wenart_parquet_{pattern}"
    group = bpy.data.node_groups.get(name)
    if group is not None:
        return group
    flt = "NodeSocketFloat"
    group, gin, gout, uv = _new_group(name, [(k, flt) for k in ("Cos", "Sin", "Width", "Length", "Repeat", "Seam",
                                                                 "Tan", "Column", "Row")],
                                      [("Vector", "NodeSocketVector"), ("Seam", flt), ("Random", flt)])
    g = _Graph(group)
    i = gin.outputs
    m = g.math
    x, y = g.xyz(uv)
    xu = m("SUBTRACT", m("MULTIPLY", x, i["Cos"]), m("MULTIPLY", y, i["Sin"]))
    yv = m("ADD", m("MULTIPLY", x, i["Sin"]), m("MULTIPLY", y, i["Cos"]))

    def pick(flag, a, b):                     # flag 1 -> a, 0 -> b
        return m("ADD", m("MULTIPLY", flag, a), m("MULTIPLY", m("SUBTRACT", 1.0, flag), b))

    def least(a, b):
        return m("MINIMUM", a, b)

    if pattern == "herringbone":
        n = m("DIVIDE", i["Length"], i["Width"])          # an integer (ratio_of x width)
        two_n = m("MULTIPLY", n, 2.0)
        u, v = m("DIVIDE", xu, i["Width"]), m("DIVIDE", yv, i["Width"])
        fv, fu = m("FLOOR", v), m("FLOOR", u)
        t = m("SUBTRACT", u, fv)
        r = m("FLOORED_MODULO", t, two_n)
        horiz = m("LESS_THAN", r, n)
        s0 = m("SUBTRACT", m("SUBTRACT", v, fu), 1.0)
        along = pick(horiz, r, m("FLOORED_MODULO", s0, two_n))
        across = pick(horiz, m("SUBTRACT", v, fv), m("SUBTRACT", u, fu))
        id_a = pick(horiz, fv, fu)
        id_b = pick(horiz, m("FLOOR", m("DIVIDE", t, two_n)), m("FLOOR", m("DIVIDE", s0, two_n)))
        id_c = m("SUBTRACT", 1.0, horiz)
        d_across = m("MULTIPLY", least(across, m("SUBTRACT", 1.0, across)), i["Width"])
        d_along = m("MULTIPLY", least(along, m("SUBTRACT", n, along)), i["Width"])
        along_m, across_m = m("MULTIPLY", along, i["Width"]), m("MULTIPLY", across, i["Width"])
    else:                                                  # chevron
        c = m("FLOOR", m("DIVIDE", xu, i["Column"]))
        xl = m("SUBTRACT", xu, m("MULTIPLY", c, i["Column"]))
        sign = m("SUBTRACT", 1.0, m("MULTIPLY", m("FLOORED_MODULO", c, 2.0), 2.0))
        vt = m("SUBTRACT", yv, m("MULTIPLY", m("MULTIPLY", sign, xl), i["Tan"]))
        rr = m("FLOOR", m("DIVIDE", vt, i["Row"]))
        across = m("DIVIDE", m("SUBTRACT", vt, m("MULTIPLY", rr, i["Row"])), i["Row"])
        id_a, id_b, id_c = c, rr, 2.0
        d_across = m("MULTIPLY", least(across, m("SUBTRACT", 1.0, across)), i["Width"])
        d_along = least(xl, m("SUBTRACT", i["Column"], xl))
        along_m = m("DIVIDE", m("MULTIPLY", xl, i["Row"]), i["Width"])          # xl / cos(a), row = width / cos
        across_m = m("MULTIPLY", across, i["Width"])
    noise = []
    for ox, oy, oz in NOISE_OFFSETS:
        node = g.nodes.new("ShaderNodeTexWhiteNoise")
        g.links.new(g.combine(m("ADD", id_a, ox), m("ADD", id_b, oy), m("ADD", id_c, oz)), node.inputs["Vector"])
        noise.append(node.outputs["Value"])
    look_x = m("ADD", across_m, m("MULTIPLY", noise[0], i["Repeat"]))
    look_y = m("ADD", along_m, m("MULTIPLY", noise[1], i["Repeat"]))
    g.links.new(g.combine(look_x, look_y, 0.0), gout.inputs["Vector"])
    seam = m("MAXIMUM", 0.0, m("SUBTRACT", 1.0, m("DIVIDE", least(d_across, d_along), i["Seam"])))
    g.links.new(seam, gout.inputs["Seam"])
    g.links.new(noise[2], gout.inputs["Random"])
    return group


def group_inputs(params: dict, repeat_m: float) -> dict[str, float]:
    """The values of the group node's inputs for a ``parquet`` record (pure)."""
    p = dict(params)
    t = math.radians(float(p.get("turn_deg") or 0.0))
    width = float(p["width_m"])
    out = {"Cos": math.cos(t), "Sin": math.sin(t), "Width": width, "Repeat": float(repeat_m), "Seam": SEAM_M,
           "Length": ratio_of(p["length_m"], width) * width, "Tan": 0.0, "Column": 1.0, "Row": 1.0}
    if p.get("pattern") == "chevron":
        a = math.radians(float(p.get("cut_deg") or PLANK["chevron"]["cut_deg"]))
        out.update(Length=float(p["length_m"]), Tan=math.tan(a), Column=float(p["length_m"]) * math.cos(a),
                   Row=width / math.cos(a))
    return out


def wire(nodes, links, params: dict, repeat_m: float):
    """A parquet group node in a material (bpy), its inputs set: returns the node (outputs Vector, Seam, Random)."""
    node = nodes.new("ShaderNodeGroup")
    node.node_tree = parquet_group(params["pattern"])
    for key, value in group_inputs(params, repeat_m).items():
        node.inputs[key].default_value = float(value)
    return node


def shade(nodes, links, node, colour_socket):
    """The base colour of a plank: ``colour x (1 + (Random - 0.5) x TONE_SPREAD) x (1 - Seam x SEAM_DARK)`` (bpy);
    returns the new colour socket."""
    tone = nodes.new("ShaderNodeMath")
    tone.operation = "MULTIPLY_ADD"
    links.new(node.outputs["Random"], tone.inputs[0])
    tone.inputs[1].default_value = TONE_SPREAD
    tone.inputs[2].default_value = 1.0 - TONE_SPREAD / 2.0
    dark = nodes.new("ShaderNodeMath")
    dark.operation = "MULTIPLY_ADD"
    links.new(node.outputs["Seam"], dark.inputs[0])
    dark.inputs[1].default_value = -SEAM_DARK
    dark.inputs[2].default_value = 1.0
    both = nodes.new("ShaderNodeMath")
    both.operation = "MULTIPLY"
    links.new(tone.outputs[0], both.inputs[0])
    links.new(dark.outputs[0], both.inputs[1])
    scale = nodes.new("ShaderNodeVectorMath")
    scale.operation = "SCALE"
    links.new(colour_socket, scale.inputs["Vector"])
    links.new(both.outputs[0], scale.inputs["Scale"])
    return scale.outputs["Vector"]


def groove(nodes, links, node, normal_socket):
    """The joints as grooves: a Bump node of height ``1 - Seam`` on the normal map's output (bpy); returns its
    Normal output."""
    height = nodes.new("ShaderNodeMath")
    height.operation = "SUBTRACT"
    height.inputs[0].default_value = 1.0
    links.new(node.outputs["Seam"], height.inputs[1])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = BUMP_STRENGTH
    bump.inputs["Distance"].default_value = BUMP_DISTANCE_M
    links.new(height.outputs[0], bump.inputs["Height"])
    if normal_socket is not None:
        links.new(normal_socket, bump.inputs["Normal"])
    return bump.outputs["Normal"]


def note(params: dict, texture: Optional[str]) -> str:
    """The material record's text of a parquet floor."""
    p = dict(params)
    return (f"parquet {p.get('pattern')} {float(p['length_m']) * 100:.0f} x {float(p['width_m']) * 100:.0f} cm planks, "
            f"turned {float(p.get('turn_deg') or 0.0):g} deg, each plank a random patch of "
            f"{texture or 'the floor photo'} (node group wenart_parquet_{p.get('pattern')}; UL106)")
