"""Chimneys on the roof (29 Oct 2026; lesson UL109, user on real06 run 20261028-154514-full: "There are no chimneys
there could be some chimney in the projects").

What:

- ``drawn_sources(building)``: what the documents say about fire and flues (source data first): a drawn piece whose
  type, block name or source text names a fireplace, a wood stove or a flue (Turkish "ŞÖMİNE", "SOBA", "BACA"; the
  English, German, French, Italian and Spanish words of ``SOURCE_WORDS``), a fireplace or flue text of the plan (the
  reading's ``chimney_texts``), a room labelled as a flue or a boiler room ("BACA", "KAZAN DAİRESİ"; never an air or
  light shaft: "HAVA BACASI", "IŞIK BACASI"), a symbol or a zone label naming one. Sources in one room or within
  ``CHIMNEY["merge_m"]`` of each other share one stack (``merged_sources``).
- ``plan(building, roof_model, style_family)`` (pure): the chimneys the build makes. A drawn source gets its stack at
  its plan position, out of the roof (``from_documents`` with its evidence); a drawn fireplace or stove also gets its
  flue inside the house, from its floor up through the levels above to the roof (``inner``). Where nothing is drawn, a
  house with a pitched roof whose style family usually has a chimney (``FAMILY_CHIMNEYS``) gets one ``inferred``
  stack: over the fireplace wall of its main living room (a solid wall stretch with no door or window, an inner wall
  first, the wall its sofa faces first), else over a wall of its boiler or technical room, else of its kitchen; each
  dwelling of a mirrored pair (twin rooms) gets its own. Every station is fitted to the roof (``roof_fit``): over the
  roof (no terrace or opening under it), clear of the eaves, the roof openings and the valleys, no window looking onto
  it, and its top by the 3-2-10 rule of thumb (``CHIMNEY``). Nothing fits: no chimney, and the reason is listed.
- ``meshes(ch, roof_model)`` (pure): the stack (its bottom follows the middle of the roof slab on a grid, so it enters
  the covering with no gap and never reaches under the ceiling), the coping slab, the clay pots or the metal cowls, and
  a drawn fireplace's flue inside the house.
- ``build_chimneys`` (bpy): one object per chimney (kind ``roof``, detail ``chimney``: the exterior check X2 never
  reads a roof part as poking through the roof), its record in the scene manifest (what the model review M24 and
  Argus U27 measure) and its ``assumed`` row (listed in the report with the other inferred exterior parts).
- ``measure(ch, roof_model, building)`` (pure): the model review's M24 numbers: a chimney that floats over the
  covering, does not reach the roof, reaches under the ceiling, is too low for the rule, or stands in front of a window.

Why: real06's Scandinavian house had no chimney on any roof; a pitched-roof house of most style families reads as a
house with a fireplace or a stove. The readings knew no fireplace (the furniture vocabulary has no such type, a
"BACA" label became a shaft room, the sheets reader's ``chimneys`` list stayed empty): this module reads every source
the building holds, and the reading now keeps the fireplace and flue texts (``generic.reading.chimney_texts``).
The rule is general: drawn first, inferred only where the documents are silent (CLAUDE.md evidence rules).

How: pure Python on dicts (the roof's own ``top_z`` / ``underside_z`` / ``covers`` / ``ridge_lines``); runs inside
Blender (no shapely, no numpy).
"""
from __future__ import annotations

import math
import re
import unicodedata
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# Building rules of thumb (not a cited norm): the sizes of real stacks, copings, pots and cowls, and the height rule.
CHIMNEY = {
    # a single-flue stack (a boiler, a stove, a kitchen flue) and a fireplace stack with two flues; (along its wall,
    # across), metres
    "stack_one_flue_m": (0.50, 0.50),
    "stack_fireplace_m": (0.90, 0.60),
    # the "3-2-10" rule of thumb of US practice: the top at least 3 ft (0.9 m) over the highest point where the stack
    # leaves the roof and 2 ft (0.6 m) over any part of the roof within 10 ft (3 m) horizontally; within 3 m of a
    # ridge that is 0.6 m over the ridge, elsewhere 0.6 m over the roof surface around it
    "over_exit_m": 0.9, "over_near_m": 0.6, "near_m": 3.0,
    "max_over_exit_m": 2.5,      # an inferred stack rising more than this over its exit stands too far from the ridge
    "top_step_m": 0.05,          # the top is rounded up to this
    # a precast coping slab with a drip overhang on the stack, clay pots or metal cowls on the coping
    "coping_t_m": 0.08, "coping_over_m": 0.05,
    "pot_d_m": 0.22, "pot_h_m": 0.40, "pot_gap_m": 0.12,
    "cowl_d_m": 0.18, "cowl_h_m": 0.30, "hat_d_m": 0.32, "hat_h_m": 0.05,
    "segments": 16,
    # where an inferred stack may stand on the roof
    "clear_eaves_m": 0.6, "clear_opening_m": 0.6, "clear_valley_m": 0.6,
    "window_m": 2.0, "window_side_m": 0.5,     # no window whose wall stretch this close looks onto the stack
    # the fireplace wall: a solid stretch at least this long, this far from a door or a window
    "fireplace_wall_m": 1.2, "opening_margin_m": 0.3, "step_m": 0.25, "wall_tol_m": 0.12,
    # a sofa faces the fireplace wall: its front against the wall, the wall ahead within reach, this far to the side
    "sofa_reach_m": 5.0, "sofa_side_m": 1.5,
    # the stack's bottom: the middle of the roof slab, on a grid of cells over its footprint
    "grid": 6, "slab_mid": 0.5,
    "merge_m": 1.5, "snap_m": 1.5, "nudge_m": (0.25, 0.5),
    # M24 tolerances
    "float_tol_m": 0.02, "low_tol_m": 0.02, "valley_eps_m": 0.003, "near_step_m": 0.5,
}

# Per style family: whether its pitched-roof houses usually have a chimney, the stack's look ("facade": the house's own
# facade look, render in its colour; "base": the facade scheme's base cladding; else a vocabulary slug), the coping and
# the cap (clay "pots" or a metal "cowl"). A judgement of typical houses of each family, not a rule of any code:
FAMILY_CHIMNEYS = {
    # Nordic houses heat with a wood-burning stove in the living room: a plain rendered stack and a black steel cowl
    "scandinavian": {"chimney": True, "stack": "facade", "coping": "concrete_exposed", "cap": "cowl",
                     "why": "a Scandinavian house warms its living room with a wood-burning stove"},
    # the Japandi house keeps the Nordic stove in a calm room: the same quiet rendered stack
    "japandi": {"chimney": True, "stack": "facade", "coping": "concrete_exposed", "cap": "cowl",
                "why": "a Japandi house keeps a wood stove in its living room"},
    # a modern pitched-roof house keeps a fireplace or a stove: a plain stack in the house's render, a metal cowl
    "modern": {"chimney": True, "stack": "facade", "coping": "concrete_exposed", "cap": "cowl",
               "why": "a modern pitched-roof house keeps a fireplace or a stove in its living room"},
    # the converted warehouse look: a brick stack and a steel cowl
    "industrial": {"chimney": True, "stack": "brick_red", "coping": "concrete_exposed", "cap": "cowl",
                   "why": "an industrial house shows a brick flue stack"},
    # the classic house has its open fireplace: a brick stack, a stone coping and clay pots
    "classic": {"chimney": True, "stack": "brick_red", "coping": "limestone", "cap": "pots",
                "why": "a classic house has an open fireplace in its living room"},
    # the rustic house burns wood: a stack in the house's base stone with clay pots
    "rustic": {"chimney": True, "stack": "base", "coping": "limestone", "cap": "pots",
               "why": "a rustic house burns wood in a fireplace"},
    # the Mediterranean house: a rendered stack in the house colour with clay pots
    "mediterranean": {"chimney": True, "stack": "facade", "coping": "limestone", "cap": "pots",
                      "why": "a Mediterranean house keeps a fireplace for the winter"},
    # the minimal houses keep a clean roofline (a heat pump, no flue on the roof)
    "minimal": {"chimney": False, "stack": "facade", "coping": "concrete_exposed", "cap": "cowl",
                "why": "a minimal house keeps a clean roofline (no fire, no flue on the roof)"},
    "modern minimal": {"chimney": False, "stack": "facade", "coping": "concrete_exposed", "cap": "cowl",
                       "why": "a modern minimal house keeps a clean roofline (no fire, no flue on the roof)"},
}
FAMILY_CHIMNEYS["default"] = dict(FAMILY_CHIMNEYS["modern"],
                                  why="a pitched-roof house usually keeps a fireplace or a stove (no style family)")
CAP_LOOKS = {"pots": ("render", "terracotta", "clay flue pots on the coping (not drawn)"),
             "cowl": ("steel_black", None, "steel flue cowls on the coping (not drawn)")}
# a facade material a stack may carry (masonry); any other (timber, panels) gives render in the facade's colour
MASONRY = ("render", "brick", "stone", "concrete")

# Words of the documents (folded: ASCII lower case, words split at anything but letters and digits); a word matches a
# whole word of the text, also with a plural or a Turkish case or possessive ending (``SUFFIXES``: "bacası",
# "şöminesi").
# Left out as too loose: "camino" (also a road in Spanish), a bare "boiler" or "boyler" (often a water heater with no
# flue), a bare "kalorifer" (a radiator mark), "ocak" (the kitchen hob), "stove" (the kitchen cooker).
SOURCE_WORDS = {
    "fireplace": ("somine", "fireplace", "fire place", "hearth", "kamin", "offener kamin", "cheminee", "caminetto",
                  "chimenea"),
    "stove": ("soba", "odun sobasi", "wood stove", "woodstove", "wood burner", "woodburner", "log burner",
              "wood burning stove", "kaminofen", "schwedenofen", "kachelofen", "poele a bois", "stufa a legna",
              "estufa de lena"),
    "flue": ("baca", "duman bacasi", "chimney", "flue", "schornstein", "rauchfang", "conduit de fumee",
             "canna fumaria", "conducto de humos"),
    "boiler_room": ("kazan dairesi", "kazan odasi", "kazan", "kalorifer dairesi", "boiler room", "boiler house",
                    "plant room", "heizraum", "heizungsraum", "heizung", "chaufferie", "locale caldaia",
                    "centrale termica", "sala de calderas", "cuarto de calderas"),
}
KIND_ORDER = ("fireplace", "stove", "flue", "boiler_room")
# an air, light, lift or services shaft, or a cooker hood, is no flue ("HAVA BACASI" in real03 is an air shaft)
NOT_FLUE_WORDS = ("hava bacasi", "isik bacasi", "aydinlik bacasi", "aydinlik", "havalandirma", "tesisat bacasi",
                  "air shaft", "light shaft", "light well", "ventilation", "vent shaft", "asansor", "lift", "elevator",
                  "saft", "shaft", "luftschacht", "lichtschacht", "gaine", "cavedio", "chimney hood", "cooker hood",
                  "davlumbaz", "aspirator")
TECHNICAL_WORDS = ("teknik", "teknik oda", "technical", "mechanical", "technik", "technikraum", "local technique",
                   "locale tecnico", "cuarto tecnico")
SUFFIXES = ("s", "es", "i", "si", "u", "su", "a", "e", "ya", "ye", "lar", "ler", "lari", "leri", "nin", "in", "n")
_TR = str.maketrans({"ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g", "ç": "c", "Ç": "c", "ö": "o",
                     "Ö": "o", "ü": "u", "Ü": "u", "ß": "ss"})
TEXT_METHODS = ("vector", "ocr", "raster", None)     # evidence the documents give (an AI answer is no drawing)
SEATS = ("sofa", "sofa_corner")
RULE = "blender.chimney.plan"


# --------------------------------------------------------------------------
# Words
# --------------------------------------------------------------------------

def fold(text) -> str:
    """Folded text: ASCII lower case, words separated by one space (pure)."""
    s = str(text or "").translate(_TR)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return " ".join(re.split(r"[^a-z0-9]+", s)).strip()


def _has(tokens: list[str], phrase: str) -> bool:
    words = phrase.split()
    n = len(words)
    for i in range(len(tokens) - n + 1):
        if tokens[i:i + n - 1] != words[:-1]:
            continue
        last, tok = words[-1], tokens[i + n - 1]
        if tok == last or (tok.startswith(last) and tok[len(last):] in SUFFIXES):
            return True
    return False


def source_word(text) -> Optional[tuple[str, str]]:
    """``(kind, word)`` when ``text`` names a fireplace, a stove, a flue or a boiler room (``SOURCE_WORDS``), else None;
    an air, light, lift or services shaft or a cooker hood names none (pure)."""
    tokens = fold(text).split()
    if not tokens or any(_has(tokens, w) for w in NOT_FLUE_WORDS):
        return None
    for kind in KIND_ORDER:
        for w in SOURCE_WORDS[kind]:
            if _has(tokens, w):
                return kind, w
    return None


def technical_word(text) -> Optional[str]:
    """The word when ``text`` names a technical room (pure)."""
    tokens = fold(text).split()
    return next((w for w in TECHNICAL_WORDS if _has(tokens, w)), None)


def family_rule(family: Optional[str]) -> dict:
    """The family's chimney row (``FAMILY_CHIMNEYS``; an unknown family takes ``default``), with ``family``."""
    fam = str(family or "").lower().strip()
    return dict(FAMILY_CHIMNEYS.get(fam) or FAMILY_CHIMNEYS["default"], family=fam or "default")


def pitched(roof_model: Optional[dict]) -> bool:
    """A pitched roof: a roof with planes whose type is neither flat nor a flat_cut slab (pure)."""
    return bool(roof_model and roof_model.get("equations") and roof_model.get("type") not in ("flat", None)
                and roof_model.get("kind") != "flat_cut")


# --------------------------------------------------------------------------
# What the documents draw
# --------------------------------------------------------------------------

def _ev(e: dict) -> Optional[dict]:
    """An evidence dict of the scene-manifest format (file, method, confidence), or None."""
    if not isinstance(e, dict) or not e.get("file") or e.get("method") is None:
        return None
    return {k: e[k] for k in ("file", "method", "confidence", "page", "layer", "entity", "block", "text", "rule")
            if e.get(k) is not None}


def _piece_words(f: dict) -> list[tuple[str, Optional[dict]]]:
    out: list[tuple[str, Optional[dict]]] = [(str(f.get(k)), None) for k in ("type", "type_raw", "name")
                                             if isinstance(f.get(k), str) and f.get(k)]
    for e in f.get("evidence") or []:
        if not isinstance(e, dict) or e.get("method") not in TEXT_METHODS:
            continue
        for k in ("block", "text", "layer"):
            if isinstance(e.get(k), str) and e.get(k):
                out.append((str(e[k]), e))
    return out


def drawn_sources(building: dict) -> list[dict]:
    """Every drawn fireplace, stove, flue or boiler room of the building (module docstring), most precise first:
    ``{"id", "kind", "word", "text", "what": piece | symbol | text | zone | room, "level_id", "room_id", "center",
    "size", "rotation_deg", "front_deg", "evidence"}`` (pure)."""
    out: list[dict] = []

    def add(kind_word, what, text, level_id, room_id, center, evidence, size=None, rot=0.0, front=None, ref=None):
        kind, word = kind_word
        out.append({"id": ref, "kind": kind, "word": word, "text": str(text), "what": what, "level_id": level_id,
                    "room_id": room_id, "center": [float(center[0]), float(center[1])] if center else None,
                    "size": [float(v) for v in size] if size else None, "rotation_deg": float(rot or 0.0),
                    "front_deg": front, "evidence": [e for e in (_ev(x) for x in evidence) if e]})

    for f in building.get("furniture") or []:
        fp = (f.get("footprint") or {}) if isinstance(f, dict) else {}
        if not isinstance(f, dict) or not fp.get("center"):
            continue
        for text, e in _piece_words(f):
            hit = source_word(text)
            if hit:
                add(hit, "piece", text, f.get("level_id"), f.get("room_id"), fp["center"],
                    [e] if e else list(f.get("evidence") or [])[:2], size=fp.get("size"),
                    rot=fp.get("rotation_deg"), front=f.get("front_deg"), ref=f.get("id"))
                break
    for s in building.get("symbols") or []:
        fp = (s.get("footprint") or {}) if isinstance(s, dict) else {}
        if not fp.get("center"):
            continue
        for e in s.get("evidence") or []:
            if not isinstance(e, dict) or e.get("method") not in TEXT_METHODS:
                continue
            hit = next((h for h in (source_word(e.get(k)) for k in ("block", "text", "layer") if e.get(k)) if h), None)
            if hit:
                add(hit, "symbol", e.get("text") or e.get("block") or e.get("layer"), s.get("level_id"),
                    s.get("room_id"), fp["center"], [e], size=fp.get("size"), rot=fp.get("rotation_deg"),
                    ref=s.get("id"))
                break
    for t in building.get("chimney_texts") or []:
        if not isinstance(t, dict) or not t.get("pos"):
            continue
        hit = source_word(t.get("text")) or ((t.get("kind"), t.get("word")) if t.get("kind") in KIND_ORDER else None)
        if hit:
            ev = {"file": t.get("file") or "documents", "method": t.get("method") or "vector", "confidence": 0.9,
                  "entity": t.get("id"), "text": t.get("text"), "layer": t.get("layer"), "page": t.get("page")}
            add(hit, "text", t.get("text"), t.get("level_id"), t.get("room_id"), t["pos"], [ev], ref=t.get("id"))
    for z in building.get("zone_labels") or []:
        hit = source_word(z.get("text")) if isinstance(z, dict) and z.get("pos") else None
        if hit:
            ev = {"file": z.get("file") or "documents", "method": "vector", "confidence": 0.9, "entity": z.get("id"),
                  "text": z.get("text")}
            add(hit, "zone", z.get("text"), z.get("level_id"), z.get("room_id"), z["pos"], [ev], ref=z.get("id"))
    for r in building.get("rooms") or []:
        if not isinstance(r, dict) or len(r.get("polygon") or []) < 3:
            continue
        for key in ("label", "label_raw"):
            hit = source_word(r.get(key))
            if hit and hit[0] in ("flue", "boiler_room", "fireplace", "stove"):
                ev = [e for e in r.get("evidence") or [] if isinstance(e, dict)][:2]
                add(hit, "room", r.get(key), r.get("level_id"), r.get("id"), G.polygon_centroid(r["polygon"]),
                    ev or [{"file": "documents", "method": "vector", "confidence": 0.8, "text": r.get(key)}],
                    ref=r.get("id"))
                break
    rank = {"piece": 0, "symbol": 1, "text": 2, "zone": 2, "room": 3}
    return sorted(out, key=lambda s: (rank[s["what"]], KIND_ORDER.index(s["kind"]), str(s["id"])))


def merged_sources(building: dict) -> list[list[dict]]:
    """The drawn sources grouped by stack: one room, or within ``CHIMNEY["merge_m"]`` in plan (a fireplace and the
    flue text written on it); each group most precise first (pure)."""
    groups: list[list[dict]] = []
    for s in drawn_sources(building):
        for g in groups:
            if any((s["room_id"] and s["room_id"] == o["room_id"]) or
                   (s["center"] and o["center"] and G.distance(s["center"], o["center"]) <= CHIMNEY["merge_m"])
                   for o in g):
                g.append(s)
                break
        else:
            groups.append([s])
    return groups


# --------------------------------------------------------------------------
# Walls, stations
# --------------------------------------------------------------------------

def _levels(building: dict) -> dict:
    return {lv["id"]: lv for lv in building.get("levels") or [] if isinstance(lv, dict) and lv.get("id")}


def room_stretches(building: dict, room: dict, min_len: float) -> list[dict]:
    """The solid wall stretches of a room (pure): along each edge of its polygon, the wall that carries it (parallel,
    its centre line half its thickness outside the edge), less every door, window and opening of that wall
    (``opening_margin_m`` more on each side); ``[{"wall", "p", "u", "n_in", "t0", "t1", "exterior"}]`` with
    ``t1 - t0 >= min_len`` (``p`` the edge start, ``u`` along it, ``n_in`` into the room)."""
    poly = geom2d.ccw(room.get("polygon") or [])
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == room.get("level_id")
             and w.get("start") and w.get("end")]
    ops: dict = {}
    for o in building.get("openings") or []:
        if isinstance(o, dict) and o.get("wall_id") and o.get("center"):
            ops.setdefault(o["wall_id"], []).append(o)
    tol, margin = CHIMNEY["wall_tol_m"], CHIMNEY["opening_margin_m"]
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        length = G.distance(p, q)
        if length < min_len:
            continue
        u = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
        n_in = (-u[1], u[0])                                 # ccw polygon: the left normal points in
        for w in walls:
            a, b = w["start"][:2], w["end"][:2]
            wl = G.distance(a, b)
            if wl < 1e-6:
                continue
            wu = ((b[0] - a[0]) / wl, (b[1] - a[1]) / wl)
            if abs(u[0] * wu[1] - u[1] * wu[0]) > 0.05:
                continue
            half = float(w.get("thickness") or 0.2) / 2.0
            off = (a[0] - p[0]) * n_in[0] + (a[1] - p[1]) * n_in[1]        # the wall line's offset into the room
            if abs(off + half) > tol:
                continue
            ta = (a[0] - p[0]) * u[0] + (a[1] - p[1]) * u[1]
            tb = (b[0] - p[0]) * u[0] + (b[1] - p[1]) * u[1]
            t0, t1 = max(0.0, min(ta, tb)), min(length, max(ta, tb))
            if t1 - t0 < min_len:
                continue
            cuts = []
            for o in ops.get(w["id"], []):
                to = (float(o["center"][0]) - p[0]) * u[0] + (float(o["center"][1]) - p[1]) * u[1]
                hw = float(o.get("width") or 0.9) / 2.0 + margin
                cuts.append((to - hw, to + hw))
            s = t0
            for c0, c1 in sorted(cuts) + [(t1, t1)]:
                if min(c0, t1) - s >= min_len:
                    out.append({"wall": w, "p": p, "u": u, "n_in": n_in, "t0": s, "t1": min(c0, t1),
                                "exterior": bool(w.get("exterior")), "half": half})
                s = max(s, c1)
    return out


def stations(building: dict, room: dict, size: Sequence[float], min_len: float) -> list[dict]:
    """The stack stations of a room (pure): every ``step_m`` along each solid stretch where the stack fits; on an inner
    wall the stack stands on the wall's centre line (a chimney breast in the wall), on an outer wall inside its inner
    face. ``[{"center", "rotation_deg", "wall_id", "exterior", "n_in", "stretch": (t0, t1), "t", "room_id"}]``."""
    along = float(size[0])
    out = []
    for st in room_stretches(building, room, max(min_len, along)):
        p, u, n_in = st["p"], st["u"], st["n_in"]
        rot = math.degrees(math.atan2(u[1], u[0]))
        k = 0
        t = st["t0"] + along / 2.0
        while t <= st["t1"] - along / 2.0 + 1e-9:
            e = (p[0] + u[0] * t, p[1] + u[1] * t)
            off = (float(size[1]) / 2.0) if st["exterior"] else -st["half"]
            c = (e[0] + n_in[0] * off, e[1] + n_in[1] * off)
            out.append({"center": [c[0], c[1]], "rotation_deg": rot, "wall_id": st["wall"]["id"],
                        "exterior": st["exterior"], "n_in": n_in, "stretch": (st["t0"], st["t1"]), "t": t,
                        "edge_point": e, "room_id": room.get("id"), "level_id": room.get("level_id")})
            k += 1
            t = st["t0"] + along / 2.0 + k * CHIMNEY["step_m"]
    return out


def sofa_faces(building: dict, room: dict, st: dict) -> Optional[str]:
    """The sofa of the room that faces the station's wall (its front against the wall's inward normal, the station
    ahead of it within ``sofa_reach_m`` and ``sofa_side_m`` to the side), or None (pure)."""
    for f in building.get("furniture") or []:
        if not isinstance(f, dict) or f.get("room_id") != room.get("id") or f.get("type") not in SEATS \
                or f.get("build") is False:
            continue
        fp = f.get("footprint") or {}
        if not fp.get("center"):
            continue
        fd = f.get("front_deg")
        fd = float(fd) if fd is not None else G.front_direction_deg(float(fp.get("rotation_deg") or 0.0))
        fx, fy = math.cos(math.radians(fd)), math.sin(math.radians(fd))
        nx, ny = st["n_in"]
        if fx * nx + fy * ny > -0.7:
            continue
        dx, dy = st["edge_point"][0] - fp["center"][0], st["edge_point"][1] - fp["center"][1]
        ahead = dx * fx + dy * fy
        if 0.3 < ahead <= CHIMNEY["sofa_reach_m"] and abs(dx * fy - dy * fx) <= CHIMNEY["sofa_side_m"]:
            return f.get("id")
    return None


# --------------------------------------------------------------------------
# On the roof
# --------------------------------------------------------------------------

def footprint(center, size, rot: float) -> list[tuple[float, float]]:
    return G.rotated_rectangle((float(center[0]), float(center[1])), [float(size[0]), float(size[1])], float(rot))


def grid_points(center, size, rot: float, n: Optional[int] = None) -> list[list[tuple[float, float]]]:
    """``pts[i][j]``: the footprint's grid, ``i`` along ``size[0]``, ``j`` across (pure)."""
    n = n or CHIMNEY["grid"]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    w, d = float(size[0]), float(size[1])
    out = []
    for i in range(n + 1):
        row = []
        for j in range(n + 1):
            lx, ly = -w / 2.0 + w * i / n, -d / 2.0 + d * j / n
            row.append((center[0] + lx * c - ly * s, center[1] + lx * s + ly * c))
        out.append(row)
    return out


def perimeter(n: Optional[int] = None) -> list[tuple[int, int]]:
    """The grid's boundary indices, counter-clockwise from ``(0, 0)`` (pure)."""
    n = n or CHIMNEY["grid"]
    return ([(i, 0) for i in range(n)] + [(n, j) for j in range(n)] + [(i, n) for i in range(n, 0, -1)]
            + [(0, j) for j in range(n, 0, -1)])


def slab_mid(model: dict, x: float, y: float) -> float:
    """The middle of the roof slab at ``(x, y)`` (``slab_mid`` between the covering and the underside)."""
    from wenart.blender import roof as R

    top = R.top_z(model, x, y)
    return top - CHIMNEY["slab_mid"] * (top - R.underside_z(model, x, y))


def context(model: dict, building: dict) -> dict:
    """What every station's fit reads once (pure): the outline, the roof openings, the ridge and hip samples and the
    outside windows and doors (wall stretch and height band)."""
    from wenart.blender import roof as R

    levels = _levels(building)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id")}
    ridge = []
    for a, b in R.ridge_lines(model):
        k = max(1, int(G.distance(a[:2], b[:2]) / 0.25))
        ridge += [(a[0] + (b[0] - a[0]) * t / k, a[1] + (b[1] - a[1]) * t / k, a[2] + (b[2] - a[2]) * t / k)
                  for t in range(k + 1)]
    wins = []
    for o in building.get("openings") or []:
        w = walls.get(o.get("wall_id")) if isinstance(o, dict) else None
        lv = levels.get(o.get("level_id")) if isinstance(o, dict) else None
        if w is None or lv is None or not w.get("exterior") or o.get("type") not in ("window", "door") \
                or not o.get("center"):
            continue
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        wl = math.hypot(x1 - x0, y1 - y0)
        if wl < 1e-6:
            continue
        ux, uy = (x1 - x0) / wl, (y1 - y0) / wl
        hw = float(o.get("width") or 0.9) / 2.0
        cx, cy = float(o["center"][0]), float(o["center"][1])
        z0 = float(lv["elevation"]) + float(o.get("sill_height") or 0.0)
        wins.append({"id": o.get("id"), "a": (cx - ux * hw, cy - uy * hw), "b": (cx + ux * hw, cy + uy * hw),
                     "z0": z0, "z1": z0 + float(o.get("height") or (2.1 if o.get("type") == "door" else 1.2))})
    return {"outline": geom2d.ccw(model.get("outline") or []), "ridge": ridge, "windows": wins,
            "holes": [o["polygon"] for o in model.get("openings") or [] if len(o.get("polygon") or []) >= 3]}


def _seg_rect_distance(a, b, center, size, rot: float) -> float:
    return min(geom2d.distance_to_rect((a[0] + (b[0] - a[0]) * t / 8.0, a[1] + (b[1] - a[1]) * t / 8.0), center, size,
                                       rot) for t in range(9))


def window_near(ctx: dict, center, size, rot: float, z0: float, z1: float) -> Optional[dict]:
    """The outside window or door whose wall stretch (``window_side_m`` wider) lies within ``window_m`` of the stack's
    footprint and whose height band overlaps the stack over the roof ``z0``-``z1`` (pure), else None."""
    side = CHIMNEY["window_side_m"]
    for w in ctx["windows"]:
        if w["z1"] <= z0 or w["z0"] >= z1:
            continue
        ax, ay = w["a"]
        bx, by = w["b"]
        ln = math.hypot(bx - ax, by - ay) or 1.0
        ux, uy = (bx - ax) / ln, (by - ay) / ln
        a, b = (ax - ux * side, ay - uy * side), (bx + ux * side, by + uy * side)
        d = _seg_rect_distance(a, b, center, size, rot)
        if d <= CHIMNEY["window_m"]:
            return dict(w, distance_m=round(d, 3))
    return None


def _valley(model: dict, center, size, rot: float) -> bool:
    """True when a roof valley runs under the footprint or within ``clear_valley_m`` of it: along the lines across
    the footprint the roof bends up (pure)."""
    from wenart.blender import roof as R

    reach, step, eps = CHIMNEY["clear_valley_m"], 0.1, CHIMNEY["valley_eps_m"]
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    w, d = float(size[0]) / 2.0 + reach, float(size[1]) / 2.0 + reach
    lines = []
    for f in (-0.5, 0.0, 0.5):
        lines.append([(-w + k * step, f * float(size[1])) for k in range(int(2 * w / step) + 1)])
        lines.append([(f * float(size[0]), -d + k * step) for k in range(int(2 * d / step) + 1)])
    for line in lines:
        zs = []
        for lx, ly in line:
            x, y = center[0] + lx * c - ly * s, center[1] + lx * s + ly * c
            zs.append(R.top_z(model, x, y) if R.covers(model, x, y) else None)
        for k in range(1, len(zs) - 1):
            if None in (zs[k - 1], zs[k], zs[k + 1]):
                continue
            if zs[k - 1] + zs[k + 1] - 2.0 * zs[k] > eps:
                return True
    return False


def roof_fit(model: dict, ctx: dict, center, size, rot: float, strict: bool = True) -> tuple[Optional[dict], str]:
    """Fit a stack to the roof (pure): ``(metrics, "")`` or ``(None, reason)``. Always: every grid point of the
    footprint over the roof. ``strict`` (an inferred stack): clear of the eaves, the roof openings and the valleys,
    no window onto it, at most ``max_over_exit_m`` over its exit. Metrics: ``exit_z`` (lowest and highest covering
    under its perimeter), ``near_z`` (the highest roof within ``near_m``), ``top_z`` by the 3-2-10 rule of thumb,
    ``over_exit_m`` and, when not strict, ``notes`` (what an inferred stack would have avoided)."""
    from wenart.blender import roof as R

    grid = grid_points(center, size, rot)
    for row in grid:
        for x, y in row:
            if not R.covers(model, x, y):
                return None, "off the roof (outside its eaves or over a roof terrace or opening)"
    notes = []
    corners = footprint(center, size, rot)
    edge_pts = corners + [G.segment_midpoint(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    outline = ctx["outline"]
    eaves = min([geom2d.distance_to_polygon_edges(p, outline) for p in edge_pts]
                + [geom2d.distance_to_rect(v, center, size, rot) for v in outline])
    if eaves < CHIMNEY["clear_eaves_m"]:
        notes.append(f"{eaves:.2f} m from the eaves (under {CHIMNEY['clear_eaves_m']:.1f} m)")
        if strict:
            return None, notes[0]
    for hole in ctx["holes"]:
        dh = min([geom2d.distance_to_polygon_edges(p, hole) for p in edge_pts]
                 + [geom2d.distance_to_rect(v, center, size, rot) for v in hole])
        if dh < CHIMNEY["clear_opening_m"]:
            notes.append(f"{dh:.2f} m from a roof opening (under {CHIMNEY['clear_opening_m']:.1f} m)")
            if strict:
                return None, notes[-1]
            break
    # a convex roof (the lowest of its planes everywhere) has no valley; a stepped one may
    if not model.get("convex") and _valley(model, center, size, rot):
        notes.append(f"on or within {CHIMNEY['clear_valley_m']:.1f} m of a roof valley")
        if strict:
            return None, notes[-1]
    n = CHIMNEY["grid"]
    zs = [R.top_z(model, *grid[i][j]) for i, j in perimeter(n)]
    exit_lo, exit_hi = min(zs), max(zs)
    near = CHIMNEY["near_m"]
    near_z = exit_hi
    for x, y, z in ctx["ridge"]:
        if z > near_z and geom2d.distance_to_rect((x, y), center, size, rot) <= near:
            near_z = z
    # the roof around it on a lattice shared by every station (``ctx["lattice"]``: its covering, None off the roof)
    reach = near + max(float(size[0]), float(size[1])) / 2.0
    step = CHIMNEY["near_step_m"]
    cache = ctx.setdefault("lattice", {})
    for a in range(int(math.floor((center[0] - reach) / step)), int(math.ceil((center[0] + reach) / step)) + 1):
        for b in range(int(math.floor((center[1] - reach) / step)), int(math.ceil((center[1] + reach) / step)) + 1):
            x, y = a * step, b * step
            if geom2d.distance_to_rect((x, y), center, size, rot) > near:
                continue
            if (a, b) not in cache:
                cache[(a, b)] = R.top_z(model, x, y) if R.covers(model, x, y) else None
            if cache[(a, b)] is not None:
                near_z = max(near_z, cache[(a, b)])
    need = max(exit_hi + CHIMNEY["over_exit_m"], near_z + CHIMNEY["over_near_m"])
    top = math.ceil(need / CHIMNEY["top_step_m"] - 1e-9) * CHIMNEY["top_step_m"]
    over = top - exit_hi
    if strict and over > CHIMNEY["max_over_exit_m"]:
        return None, (f"its top would rise {over:.2f} m over the roof (over {CHIMNEY['max_over_exit_m']:.1f} m: too "
                      f"far from the ridge)")
    win = window_near(ctx, center, size, rot, exit_lo, top)
    if win is not None:
        why = f"in front of the outside {win['id']} ({win['distance_m']:.2f} m)"
        if strict:
            return None, why
        notes.append(why)
    return {"exit_z": [round(exit_lo, 4), round(exit_hi, 4)], "near_z": round(near_z, 4), "top_z": round(top, 4),
            "need_z": round(need, 4), "over_exit_m": round(over, 4), "eaves_m": round(eaves, 3), "notes": notes}, ""


# --------------------------------------------------------------------------
# The plan
# --------------------------------------------------------------------------

def _rule_text(fit: dict) -> str:
    return (f"top {fit['top_z']:.2f} m: 0.6 m over the roof within 3 m (its highest point there {fit['near_z']:.2f} m) "
            f"and 0.9 m over where it leaves the roof ({fit['exit_z'][1]:.2f} m), the 3-2-10 rule of thumb")


def _record(cid: str, source: str, basis: str, kind: str, center, size, rot: float, fit: dict, reason: str,
            fam: dict, room: Optional[dict], wall_id=None, evidence=None, inner=None, extra=None) -> dict:
    flues = 2 if kind == "fireplace" else 1
    rec = {"id": cid, "source": source, "basis": basis, "kind": kind, "flues": flues,
           "center": [round(float(center[0]), 4), round(float(center[1]), 4)],
           "size": [round(float(size[0]), 4), round(float(size[1]), 4)], "rotation_deg": round(float(rot) % 360.0, 3),
           "room_id": (room or {}).get("id"), "level_id": (room or {}).get("level_id"), "wall_id": wall_id,
           "top_z": fit["top_z"], "exit_z": fit["exit_z"], "near_z": fit["near_z"], "need_z": fit["need_z"],
           "over_exit_m": fit["over_exit_m"], "notes": list(fit.get("notes") or []), "cap": fam["cap"],
           "family": fam["family"], "look": {"stack": fam["stack"], "coping": fam["coping"], "cap": fam["cap"]},
           "evidence": list(evidence or []), "inner": inner, "reason": reason, "rule": _rule_text(fit)}
    rec.update(extra or {})
    return rec


def _size_of(kind: str) -> tuple[float, float]:
    return CHIMNEY["stack_fireplace_m"] if kind == "fireplace" else CHIMNEY["stack_one_flue_m"]


def _nudged(model: dict, ctx: dict, center, size, rot: float):
    """The drawn stack's fit where it is drawn, else moved at most ``nudge_m`` in one of eight directions onto the
    roof: ``(center, fit, moved_m)`` or ``(None, None, reason)``."""
    fit, why = roof_fit(model, ctx, center, size, rot, strict=False)
    if fit is not None:
        return center, fit, 0.0
    for d in CHIMNEY["nudge_m"]:
        for k in range(8):
            a = math.radians(45.0 * k)
            c = (center[0] + d * math.cos(a), center[1] + d * math.sin(a))
            fit, _ = roof_fit(model, ctx, c, size, rot, strict=False)
            if fit is not None:
                return c, fit, d
    return None, None, why


def _rooms(building: dict) -> dict:
    return {r["id"]: r for r in building.get("rooms") or [] if isinstance(r, dict) and r.get("id")
            and len(r.get("polygon") or []) >= 3}


def _best_station(building: dict, model: dict, ctx: dict, room: dict, size, min_len: float, near=None,
                  strict: bool = True):
    """The station of ``room`` with the lowest stack (``near``: the nearest to that point within ``snap_m``):
    ``(station, fit)`` or ``(None, reason)``."""
    best, why = None, "no solid wall stretch long enough"
    for st in stations(building, room, size, min_len):
        if near is not None and G.distance(st["center"], near) > CHIMNEY["snap_m"]:
            continue
        fit, reason = roof_fit(model, ctx, st["center"], size, st["rotation_deg"], strict=strict)
        if fit is None:
            why = reason
            continue
        key = G.distance(st["center"], near) if near is not None else fit["over_exit_m"]
        if best is None or key < best[0]:
            best = (key, st, fit)
    return (best[1], best[2]) if best else (None, why)


def _drawn_chimney(building: dict, model: dict, ctx: dict, group: list[dict], n: int, fam: dict, levels: dict,
                   rooms: dict) -> tuple[Optional[dict], Optional[str]]:
    src = group[0]
    kind = min((s["kind"] for s in group), key=KIND_ORDER.index)        # a fireplace before a flue before a boiler
    size = _size_of(kind)
    room = rooms.get(src["room_id"]) if src["room_id"] else None
    rot = src["rotation_deg"]
    center = src["center"]
    wall_id = None
    if src["what"] == "piece" and src["size"]:
        # the flue rises at the back of the drawn fireplace or stove
        front = src["front_deg"] if src["front_deg"] is not None else G.front_direction_deg(rot)
        back = math.radians(float(front) + 180.0)
        shift = max(0.0, float(src["size"][1]) / 2.0 - size[1] / 2.0)
        center = (center[0] + math.cos(back) * shift, center[1] + math.sin(back) * shift)
    elif room is not None and src["what"] == "room" and src["kind"] == "flue":
        # a room labelled as a flue is the flue shaft itself: the stack stands on it, along its longest side
        a, b = geom2d.longest_edge(room["polygon"])
        rot = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    elif room is not None and src["what"] in ("text", "zone", "room"):
        near = None if src["what"] == "room" else src["center"]
        st, _ = _best_station(building, model, ctx, room, size, size[0], near=near, strict=False)
        if st is not None:
            center, rot, wall_id = st["center"], st["rotation_deg"], st["wall_id"]
    center, fit, moved = _nudged(model, ctx, center, size, rot)
    words = ", ".join(sorted({f"{s['what']} {s['id']} ({s['text']!r}: {s['kind'].replace('_', ' ')})"
                              for s in group}))
    if fit is None:
        return None, f"the drawn {kind.replace('_', ' ')} ({words}) is not under the roof: {moved}"
    inner = None
    if kind in ("fireplace", "stove"):
        lv = levels.get(src["level_id"]) or {}
        over = levels.get(model.get("over_level_id")) or {}
        ups = [x["id"] for x in sorted(levels.values(), key=lambda v: float(v["elevation"]))
               if lv and float(lv["elevation"]) - 1e-6 <= float(x["elevation"])
               <= float(over.get("elevation", lv.get("elevation", 0.0))) + 1e-6]
        inner = {"from_z": float(lv.get("elevation") or 0.0), "level_ids": ups}
    reason = (f"chimney of the drawn {kind.replace('_', ' ')} ({words})"
              + (f", moved {moved:.2f} m to stand on the roof" if moved else "")
              + ("; its flue up through the levels above" if inner else "") + "; " + _rule_text(fit))
    ev = [e for s in group for e in s["evidence"]][:6]
    extra = {"sources": [{"id": s["id"], "what": s["what"], "kind": s["kind"], "text": s["text"],
                          "center": s["center"], "level_id": s["level_id"]} for s in group]}
    if moved:
        extra["adjusted_by_ai"] = {"by": "code", "reason": f"moved {moved:.2f} m to stand on the roof",
                                   "drawn_center": list(src["center"])}
    rec = _record(f"chimney_{n}", "from_documents", f"drawn_{kind}", kind, center, size, rot, fit, reason, fam,
                  room or {"id": src["room_id"], "level_id": src["level_id"]}, wall_id, ev, inner, extra)
    return rec, None


def _twins(rooms: dict, room: dict) -> list[tuple[dict, list]]:
    """The rooms mirroring ``room`` (``twin_of`` / ``twin_transform``) with the transform from ``room`` to each."""
    out = []
    for r in rooms.values():
        if r["id"] == room["id"]:
            continue
        if r.get("twin_of") == room["id"] and r.get("twin_transform"):
            out.append((r, list(r["twin_transform"])))
        elif room.get("twin_of") == r["id"] and room.get("twin_transform"):
            out.append((r, G.invert_affine(room["twin_transform"])))
    return out


def _mirrored(m6: list, center, rot: float) -> tuple[tuple[float, float], float]:
    c = G.apply_affine(m6, center)
    o = G.apply_affine(m6, (0.0, 0.0))
    d = G.apply_affine(m6, (math.cos(math.radians(rot)), math.sin(math.radians(rot))))
    return c, math.degrees(math.atan2(d[1] - o[1], d[0] - o[0]))


TIERS = (("living", ("living",)), ("boiler", ("boiler", "technical")), ("kitchen", ("kitchen",)))


def _tier_rooms(building: dict, rooms: dict, names: tuple) -> list[dict]:
    out = []
    for r in rooms.values():
        words = f"{r.get('label') or ''} {r.get('label_raw') or ''}"
        if "living" in names and r.get("room_type") == "living":
            out.append(r)
        elif "boiler" in names and ((source_word(words) or ("",))[0] == "boiler_room" or technical_word(words)
                                    or r.get("room_type") in ("boiler", "technical")):
            out.append(r)
        elif "kitchen" in names and r.get("room_type") == "kitchen":
            out.append(r)
    return sorted(out, key=lambda r: (-G.polygon_area(r["polygon"]), r["id"]))


def _inferred(building: dict, model: dict, ctx: dict, fam: dict, rooms: dict) -> tuple[list[dict], list[str]]:
    notes: list[str] = []
    best = None
    for tier, (name, kinds) in enumerate(TIERS):
        size = CHIMNEY["stack_fireplace_m"] if name == "living" else CHIMNEY["stack_one_flue_m"]
        min_len = CHIMNEY["fireplace_wall_m"] if name == "living" else size[0]
        for rank, room in enumerate(_tier_rooms(building, rooms, kinds)):
            n_st, n_fit = 0, 0
            why = None
            for st in stations(building, room, size, min_len):
                n_st += 1
                fit, reason = roof_fit(model, ctx, st["center"], size, st["rotation_deg"])
                if fit is None:
                    why = why or reason
                    continue
                n_fit += 1
                sofa = sofa_faces(building, room, st) if name == "living" else None
                mid = (st["stretch"][0] + st["stretch"][1]) / 2.0
                span = max(1e-6, st["stretch"][1] - st["stretch"][0])
                score = (tier * 100.0 + rank * 4.0 + (10.0 if st["exterior"] else 0.0) + (0.0 if sofa else 6.0)
                         + 2.0 * fit["over_exit_m"] + 2.0 * abs(st["t"] - mid) / span)
                if best is None or score < best[0]:
                    best = (score, name, room, st, fit, sofa, size)
            if not n_fit:
                notes.append(f"{room['id']} ({name}): " + (f"no station of its {n_st} fits the roof ({why})" if n_st
                                                            else "no solid wall stretch long enough"))
        if best is not None:
            break
    if best is None:
        return [], notes
    _, name, room, st, fit, sofa, size = best
    wall = "an outer" if st["exterior"] else "a solid inner"
    where = {"living": (f"over the fireplace wall {st['wall_id']} of the living room {room['id']} ({wall} wall "
                        f"stretch of {st['stretch'][1] - st['stretch'][0]:.1f} m with no door or window"
                        + (f", the sofa {sofa} faces it" if sofa else "") + ")"),
             "boiler": f"over the wall {st['wall_id']} of the boiler or technical room {room['id']} (its flue)",
             "kitchen": f"over the wall {st['wall_id']} of the kitchen {room['id']} (a stove's flue)"}[name]
    kind = "fireplace" if name == "living" else "flue"
    reason = (f"inferred chimney ({fam['family']} family: {fam['why']}); no fireplace or flue drawn; {where}; "
              + _rule_text(fit))
    out = [_record("chimney_1", "inferred", f"{name}_wall", kind, st["center"], size, st["rotation_deg"], fit, reason,
                   fam, room, st["wall_id"], [], None, {"sofa_id": sofa})]
    for twin, m6 in _twins(rooms, room):
        c, rot = _mirrored(m6, st["center"], st["rotation_deg"])
        if G.distance(c, st["center"]) <= CHIMNEY["merge_m"]:
            notes.append(f"{twin['id']}: the mirrored dwelling shares the stack on the party wall")
            continue
        tfit, why = roof_fit(model, ctx, c, size, rot)
        if tfit is None:
            notes.append(f"{twin['id']}: the mirrored station does not fit the roof ({why})")
            continue
        twhy = (f"inferred chimney ({fam['family']} family): the mirrored dwelling's own, over the twin room "
                f"{twin['id']} of {room['id']}; " + _rule_text(tfit))
        out.append(_record(f"chimney_{len(out) + 1}", "inferred", f"{name}_wall_twin", kind, c, size, rot, tfit, twhy,
                           fam, twin, None, [], None, {"twin_of": "chimney_1"}))
    return out, notes


def plan(building: dict, roof_model: Optional[dict], style_family: Optional[str] = None) -> dict:
    """The chimneys of the building (module docstring; pure): ``{"chimneys", "decision": drawn | inferred | none,
    "reason", "family", "sources", "notes"}``."""
    fam = family_rule(style_family)
    out = {"chimneys": [], "decision": "none", "reason": "", "family": fam["family"], "family_chimney": fam["chimney"],
           "pitched": pitched(roof_model), "sources": [], "notes": []}
    groups = merged_sources(building)
    out["sources"] = [{"id": s["id"], "what": s["what"], "kind": s["kind"], "text": s["text"], "center": s["center"],
                       "level_id": s["level_id"], "room_id": s["room_id"]} for g in groups for s in g]
    if not roof_model or not roof_model.get("equations"):
        out["reason"] = "no roof is built: no chimney"
        return out
    ctx = context(roof_model, building)
    levels = _levels(building)
    rooms = _rooms(building)
    for g in groups:
        rec, why = _drawn_chimney(building, roof_model, ctx, g, len(out["chimneys"]) + 1, fam, levels, rooms)
        if rec is not None:
            out["chimneys"].append(rec)
        else:
            out["notes"].append(why)
    if out["chimneys"]:
        out["decision"] = "drawn"
        out["reason"] = f"{len(out['chimneys'])} chimney(s) of the drawn fireplaces and flues"
        return out
    # nothing drawn, or nothing drawn under the roof (an outdoor fireplace): the house's own chimney is inferred
    silent = "no fireplace or flue drawn" if not groups else "no drawn fireplace or flue under the roof"
    if not out["pitched"]:
        out["reason"] = f"{silent} and the roof is {roof_model.get('type') or 'flat'}: no chimney"
        return out
    if not fam["chimney"]:
        out["reason"] = f"{silent}; the {fam['family']} family: {fam['why']}"
        return out
    out["chimneys"], notes = _inferred(building, roof_model, ctx, fam, rooms)
    out["notes"] += notes
    if out["chimneys"]:
        out["decision"] = "inferred"
        out["reason"] = out["chimneys"][0]["reason"]
    else:
        out["reason"] = (f"{silent}; no station of the living room, the boiler or technical room or the kitchen fits "
                         f"the roof: " + "; ".join(notes[:4]))
    return out


# --------------------------------------------------------------------------
# Meshes (pure)
# --------------------------------------------------------------------------

def stack_bottom(ch: dict, model: dict) -> list[tuple[float, float, float]]:
    """The stack's bottom under its perimeter (the middle of the roof slab), as built (pure)."""
    grid = grid_points(ch["center"], ch["size"], ch["rotation_deg"])
    return [(grid[i][j][0], grid[i][j][1], slab_mid(model, *grid[i][j])) for i, j in perimeter()]


def _column(grid: list, bottom, top) -> tuple[list, list]:
    """A vertical solid over a footprint grid: its bottom ``bottom(i, j)`` on every grid point (so it follows a
    surface), its top ``top(i, j)`` (flat or on a surface); wound outwards."""
    n = len(grid) - 1
    verts, idx = [], {}
    for i in range(n + 1):
        for j in range(n + 1):
            idx[(i, j)] = len(verts)
            verts.append((grid[i][j][0], grid[i][j][1], bottom(i, j)))
    tidx = {}
    for i in range(n + 1):
        for j in range(n + 1):
            tidx[(i, j)] = len(verts)
            verts.append((grid[i][j][0], grid[i][j][1], top(i, j)))
    faces = []
    for i in range(n):
        for j in range(n):
            faces.append([idx[(i, j)], idx[(i, j + 1)], idx[(i + 1, j + 1)], idx[(i + 1, j)]])        # down
            faces.append([tidx[(i, j)], tidx[(i + 1, j)], tidx[(i + 1, j + 1)], tidx[(i, j + 1)]])    # up
    ring = perimeter(n)
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        faces.append([idx[a], idx[b], tidx[b], tidx[a]])
    return verts, faces


def cylinder(cx: float, cy: float, z0: float, z1: float, r: float, seg: Optional[int] = None) -> tuple[list, list]:
    """A closed vertical cylinder (pure)."""
    seg = seg or CHIMNEY["segments"]
    verts = [(cx + r * math.cos(2 * math.pi * k / seg), cy + r * math.sin(2 * math.pi * k / seg), z)
             for z in (z0, z1) for k in range(seg)]
    faces = [list(range(seg))[::-1], list(range(seg, 2 * seg))]
    faces += [[k, (k + 1) % seg, seg + (k + 1) % seg, seg + k] for k in range(seg)]
    return verts, faces


def cap_points(ch: dict) -> list[tuple[float, float]]:
    """Where the pots or cowls stand on the coping: one per flue along the stack's long side (pure)."""
    c, s = math.cos(math.radians(ch["rotation_deg"])), math.sin(math.radians(ch["rotation_deg"]))
    if int(ch.get("flues") or 1) < 2:
        return [tuple(ch["center"])]
    d = (CHIMNEY["pot_d_m"] + CHIMNEY["pot_gap_m"]) / 2.0
    return [(ch["center"][0] + c * k * d, ch["center"][1] + s * k * d) for k in (-1.0, 1.0)]


def meshes(ch: dict, model: dict) -> dict:
    """``{part: (verts, faces)}`` of a chimney (pure): ``stack`` (bottom on the slab's middle, top under the coping),
    ``inner`` (a drawn fireplace's flue from its floor to the stack), ``coping``, ``cap`` (pots or cowls)."""
    grid = grid_points(ch["center"], ch["size"], ch["rotation_deg"])
    top = float(ch["top_z"])
    cop = CHIMNEY["coping_t_m"]
    mids = {(i, j): slab_mid(model, *grid[i][j]) for i in range(len(grid)) for j in range(len(grid))}
    out = {"stack": _column(grid, lambda i, j: mids[(i, j)], lambda i, j: top - cop)}
    inner = ch.get("inner")
    if inner:
        z0 = float(inner["from_z"])
        out["inner"] = _column(grid, lambda i, j: z0, lambda i, j: mids[(i, j)] + 0.02)
    w, d = float(ch["size"][0]) + 2 * CHIMNEY["coping_over_m"], float(ch["size"][1]) + 2 * CHIMNEY["coping_over_m"]
    out["coping"] = geom2d.box((ch["center"][0], ch["center"][1], top - cop / 2.0), (w, d, cop), ch["rotation_deg"])
    parts = []
    for x, y in cap_points(ch):
        if ch.get("cap") == "pots":
            parts.append(cylinder(x, y, top, top + CHIMNEY["pot_h_m"], CHIMNEY["pot_d_m"] / 2.0))
        else:
            h = top + CHIMNEY["cowl_h_m"]
            parts.append(cylinder(x, y, top, h, CHIMNEY["cowl_d_m"] / 2.0))
            parts.append(cylinder(x, y, h, h + CHIMNEY["hat_h_m"], CHIMNEY["hat_d_m"] / 2.0))
    out["cap"] = geom2d.merge(parts)
    return out


def looks_of(ch: dict, looks: Optional[dict] = None) -> dict:
    """The looks of a chimney's parts (pure): ``stack`` (the family's: the house's facade look when it is masonry,
    else render in the facade's colour; the scheme's base cladding; or a slug), ``coping``, ``cap``. Every look a
    vocabulary slug (PBR), ``inferred`` with its reason."""
    from wenart.blender import facade as FA

    fam = family_rule(ch.get("family"))
    want = (ch.get("look") or {}).get("stack") or fam["stack"]
    facade = (looks or {}).get("facade") or {"material": "render", "colour": "white"}
    if want == "facade":
        slug = str(facade.get("material") or "render")
        if any(slug.startswith(m) for m in MASONRY):
            stack = {k: facade.get(k) for k in ("material", "colour", "rgb", "asset", "params") if facade.get(k)}
            colour = f", {facade.get('colour')}" if facade.get("colour") else ""
            why = f"the stack in the house's facade look ({slug}{colour})"
        else:
            stack = {"material": "render", "colour": facade.get("colour") or "white"}
            why = f"the stack in render of the facade colour (the facade is {slug}: no flue in it)"
    elif want == "base":
        stack = {"material": FA.scheme_of({"family": fam["family"]})["base"], "colour": None}
        why = f"the stack in the {fam['family']} facade scheme's base cladding ({stack['material']})"
    else:
        stack = {"material": want, "colour": None}
        why = f"the stack in {want} ({fam['family']} family)"
    cap = CAP_LOOKS.get((ch.get("look") or {}).get("cap") or fam["cap"]) or CAP_LOOKS["cowl"]
    base = {"source": "build", "assumed": True, "inferred": True}
    return {"stack": dict(base, **stack, reason=why + " (not drawn)"),
            "coping": dict(base, material=(ch.get("look") or {}).get("coping") or fam["coping"], colour=None,
                           reason="the chimney's coping slab (not drawn)"),
            "cap": dict(base, material=cap[0], colour=cap[1], reason=cap[2])}


# --------------------------------------------------------------------------
# M24 measures (pure)
# --------------------------------------------------------------------------

def measure(ch: dict, model: dict, building: dict, bottom: Optional[Sequence] = None) -> list[dict]:
    """What is wrong with a chimney as built or planned (pure): ``[{"problem": off_roof | floats | under_ceiling |
    too_low | window, "severity", "message", ...numbers}]``. ``bottom``: the perimeter of its bottom as built
    (``stack_bottom``, the scene manifest's record), else the plan's."""
    from wenart.blender import roof as R

    out = []
    cid = ch.get("id")
    size, rot = ch["size"], float(ch.get("rotation_deg") or 0.0)
    grid = grid_points(ch["center"], size, rot)
    off = [p for row in grid for p in row if not R.covers(model, *p)]
    if off:
        out.append({"problem": "off_roof", "severity": "critical",
                    "message": f"{cid} does not reach the roof: {len(off)} of its footprint points stand off the roof "
                               f"(outside the eaves or over a roof terrace)", "points": len(off)})
        return out
    pts = list(bottom) if bottom else stack_bottom(ch, model)
    gap = max(float(z) - R.top_z(model, float(x), float(y)) for x, y, z in pts)
    if gap > CHIMNEY["float_tol_m"]:
        out.append({"problem": "floats", "severity": "critical",
                    "message": f"{cid} floats: its bottom stands {gap:.2f} m over the roof covering (a gap under it)",
                    "gap_m": round(gap, 3)})
    if not ch.get("inner"):
        deep = max(R.underside_z(model, float(x), float(y)) - float(z) for x, y, z in pts)
        if deep > CHIMNEY["float_tol_m"]:
            out.append({"problem": "under_ceiling", "severity": "major",
                        "message": f"{cid} reaches {deep:.2f} m under the roof's underside into the rooms under it",
                        "depth_m": round(deep, 3)})
    ctx = context(model, building)
    fit, _ = roof_fit(model, ctx, ch["center"], size, rot, strict=False)
    if fit is not None:
        top = float(ch.get("top_z") or 0.0)
        if top < fit["need_z"] - CHIMNEY["low_tol_m"]:
            out.append({"problem": "too_low", "severity": "major",
                        "message": f"{cid} is too low: its top {top:.2f} m, the 3-2-10 rule of thumb asks "
                                   f"{fit['need_z']:.2f} m (0.6 m over the roof within 3 m, its highest point there "
                                   f"{fit['near_z']:.2f} m; 0.9 m over its exit {fit['exit_z'][1]:.2f} m)",
                        "top_z": round(top, 3), "need_z": fit["need_z"]})
        win = window_near(ctx, ch["center"], size, rot, fit["exit_z"][0], max(top, fit["exit_z"][1]))
        if win is not None:
            out.append({"problem": "window", "severity": "major",
                        "message": f"{cid} stands {win['distance_m']:.2f} m in front of the outside {win['id']} (its "
                                   f"view and light)", "opening_id": win["id"]})
    return out


# --------------------------------------------------------------------------
# Build (bpy)
# --------------------------------------------------------------------------

def manifest_record(ch: dict, model: dict) -> dict:
    """The chimney's record in the scene manifest (what M24 and Argus U27 read; pure)."""
    keys = ("id", "source", "basis", "kind", "flues", "center", "size", "rotation_deg", "room_id", "level_id",
            "wall_id", "top_z", "exit_z", "near_z", "need_z", "over_exit_m", "cap", "family", "inner", "reason", "rule",
            "notes", "sources", "twin_of", "sofa_id", "adjusted_by_ai")
    rec = {k: ch.get(k) for k in keys if ch.get(k) is not None}
    rec["bottom"] = [[round(x, 4), round(y, 4), round(z, 4)] for x, y, z in stack_bottom(ch, model)]
    return rec


def summary(chplan: Optional[dict]) -> Optional[dict]:
    """The plan for the scene manifest's ``whole_building.chimneys`` (pure)."""
    if chplan is None:
        return None
    return {"decision": chplan.get("decision"), "reason": chplan.get("reason"), "family": chplan.get("family"),
            "family_chimney": chplan.get("family_chimney"), "pitched": chplan.get("pitched"),
            "sources": chplan.get("sources") or [], "notes": chplan.get("notes") or [],
            "chimneys": [{k: c.get(k) for k in ("id", "source", "basis", "center", "top_z", "room_id", "reason")}
                         for c in chplan.get("chimneys") or []]}


def build_chimneys(chplan: Optional[dict], model: dict, collection, looks: Optional[dict], make_material,
                   manifest_objects: list, assumed: list) -> Optional[dict]:
    """One object per planned chimney (kind ``roof``, detail ``chimney``; status ``verified`` for a drawn one, else
    ``assumed``) with three material slots (stack, coping, cap); its manifest record and ``assumed`` row. A plan with
    no chimney lists its reason in ``assumed``. Returns ``summary``."""
    from wenart.blender import common

    if chplan is None:
        return None
    for ch in chplan.get("chimneys") or []:
        lk = looks_of(ch, looks)
        mats = [make_material(lk["stack"]), make_material(lk["coping"]), make_material(lk["cap"])]
        parts = meshes(ch, model)
        verts: list = []
        faces: list = []
        slots: list = []
        for part, slot in (("stack", 0), ("inner", 0), ("coping", 1), ("cap", 2)):
            if part not in parts:
                continue
            pv, pf = parts[part]
            off = len(verts)
            verts += list(pv)
            faces += [[i + off for i in f] for f in pf]
            slots += [slot] * len(pf)
        drawn = ch["source"] == "from_documents"
        status = "verified" if drawn else "assumed"
        ob = common.new_mesh_object(ch["id"], verts, faces, collection=collection, wenart_id=ch["id"], kind="roof",
                                    status=status, materials=mats, face_material_indices=slots)
        manifest_objects.append({
            "name": ob.name, "wenart_id": ch["id"], "kind": "roof", "status": status,
            "level_id": model.get("over_level_id"), "element_id": ch["id"], "evidence": list(ch.get("evidence") or []),
            "material": mats[0].name if mats and mats[0] is not None else None, "textured": False, "pass_index": None,
            "detail": "chimney", "source": ch["source"], "inferred": not drawn,
            "assumed": {"detail": "chimney", "reason": ch["reason"], "inferred": not drawn},
            "looks": {k: {"material": v.get("material"), "colour": v.get("colour")} for k, v in lk.items()},
            "chimney": manifest_record(ch, model)})
        assumed.append({"object": ch["id"], "field": "chimney", "value": ch["source"], "reason": ch["reason"],
                        "kind": "chimney", "parent": "roof"})
    if not chplan.get("chimneys"):
        assumed.append({"object": "roof", "field": "chimney", "value": "none", "reason": chplan.get("reason") or "-",
                        "kind": "chimney", "parent": "roof"})
    return summary(chplan)
