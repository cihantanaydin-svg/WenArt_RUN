"""AI completion of rooms with drawn furniture (docs/milestone10.md §2; CLAUDE.md furniture rules).

What: ``complete_building(building, style_text, client, settings)`` completes every room the documents
furnish: the AI may change a drawn piece's type, size and look (its anchor and front stay) and add the pieces
the room type misses; kitchens get wall cabinets along a drawn counter run by rule. It returns the new
building and one ``RoomCompletion`` record per furnished room, written as ``completion.json``,
``completion_report.md`` and one PNG + JSON per room in the debug folder.

Why: Milestone 9 furnished only rooms without drawn furniture, so a bedroom with only a bed drawn got no
nightstand and no wardrobe (§0). The user chose ``furnished_rooms: complete`` for every project (8 Oct 2026).
The no-hallucination rules stay: AI proposes, the placer's checks and the locked rules decide, every piece
keeps its label (``from_documents`` with ``modified_by_ai`` and the drawn values, or ``added_by_ai`` with
``completes_room``) and its evidence.

How, per room (``furnished_rooms: complete``, documented furniture, a furnishable type, not in
``furnished_rooms_keep``; brief keys through ``wenart.brief.load_brief``):

1. The drawn pieces are sorted into fixed equipment (``schemas.FIXED_TYPES``, user decision 6), not built
   (``build: false``, an obstacle), kept types (documented-only and rule-only types: no type to change them
   into), wall-mounted (not a floor obstacle) and changeable; each gets its anchor (``locked.anchor_of``).
2. ``schemas.completion_plan`` gives what the room misses and may get; the question (``prompts
   .completion_prompt``) and the room's strict schema (``answer_schema``: enums of the changeable ids, the
   change types, the addable types, the style families and the colours; xgrammar-safe keywords only) go
   to the layout model twice (Qwen3-VL-8B, temperature 0, pass 2 with another block order and seed).
3. Agreement (§2.4): a change is kept only when both passes change the same piece to the same type (the
   smaller of the two size options; the style and colour both name, else the project's); then the main
   piece rule (a bed stays a bed type, nothing becomes a second one) and the type counts. An unverified
   drawn piece keeps its footprint and status: an agreed type becomes its ``type`` with
   ``type_proposal: true``. With ``furnished_rooms_keep_size`` no change is asked.
4. ``placer.place_changes`` places the changes at their anchors (shrink, then revert); the added pieces of
   each pass are filtered (types the room may still get, one main piece, the counts), placed with the
   full M4 repairs around the drawn pieces (``placer.place(..., obstacles=...)``) and checked for their
   companions (an office chair at a desk, a bar stool at an island, a chair at a dining table); the pass
   with the fewest dropped pieces wins (ties: pass 1); a piece the other pass also proposed (same type,
   centre within 0.5 m) gets confidence 0.9 and both passes' evidence, the rest 0.6.
5. Kitchens (and open kitchens of a living room): ``wall_cabinets_for`` hangs ``wall_cabinet`` pieces
   (``method: rule``) along every drawn counter run against a wall, 1.45-2.15 m, never over or within 0.3 m
   of a window (measured along the wall), never over or within 0.15 m of a door (assumed: the frame), never
   over the stove, a tall piece (taller than 1.40 m) or another wall cabinet; runs shorter than 0.3 m are
   left out.

Partners (asked once, §2.1): a room with ``same_as`` (an alternative level's room equal to a base room) takes
its partner's decisions as they are; with ``render.twin_rooms: one`` a room with ``twin_of`` takes them
mirrored about the party-wall axis (``partner_transform``: the perpendicular bisector of the two room
centroids, verified on the polygons and the drawn pieces within ``PARTNER_TOL_M``). Copied pieces carry
``mirrored_from``; a copy that fails a check here is dropped and listed; a partner that cannot be verified
is reported and the room is asked itself. ``copy_empty_layout`` does the same for the Milestone 4 layout of
empty rooms (user decision 7: the AI furniture of the first twin mirrored onto the second).
"""
from __future__ import annotations

import copy
import json
import math
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from shapely.geometry import LineString, Point, Polygon

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import locked as LK
from wenart.furniture import placer, prompts, schemas

EVIDENCE_FILE = "building.json"     # what the model saw: the room, doors, windows and drawn pieces of the building
AGREE_DISTANCE_M = 0.5
CONFIDENCE_AGREED = 0.9
CONFIDENCE_SINGLE = 0.6
PASSES = 2
# Partners: the polygon and every drawn piece within this distance (the pipeline matches twins within 2 cm;
# 5 cm here leaves room for rounding), the fronts within this angle.
PARTNER_TOL_M = 0.05
PARTNER_FRONT_TOL_DEG = 2.0
# Wall cabinets (§4.4).
WALL_CABINET_DEPTH_M = 0.35
WALL_CABINET_MIN_M = 0.30
WALL_CABINET_WINDOW_GAP_M = 0.30
WALL_CABINET_DOOR_GAP_M = 0.15       # assumed: a door's frame; the spec names windows only
WALL_CABINET_STEP_M = 0.01
WALL_FACE_REACH_M = 0.10             # the wall face behind a counter's back edge is looked for this far
STATES = ("completed", "copied", "mirrored", "kept", "skipped")


# --------------------------------------------------------------------------
# Settings (brief keys, docs/milestone10.md §1.3)
# --------------------------------------------------------------------------

@dataclass
class Settings:
    mode: str = "complete"                  # furnished_rooms: keep | complete
    keep: tuple[str, ...] = ()              # furnished_rooms_keep: room ids or labels
    keep_size: bool = False                 # furnished_rooms_keep_size
    twin_rooms: str = "one"                 # render.twin_rooms: one | all
    assumed: tuple[str, ...] = ()           # the keys above taken from wenart/defaults.yaml
    brief_path: Optional[str] = None
    warnings: tuple[str, ...] = ()

    KEYS = ("furnished_rooms", "furnished_rooms_keep", "furnished_rooms_keep_size", "render.twin_rooms")

    @classmethod
    def from_brief(cls, loaded: dict) -> "Settings":
        """From a ``wenart.brief.load_brief`` result."""
        from wenart import brief as BR

        return cls(mode=str(BR.value(loaded, "furnished_rooms", "complete")),
                   keep=tuple(str(v) for v in BR.value(loaded, "furnished_rooms_keep", []) or []),
                   keep_size=bool(BR.value(loaded, "furnished_rooms_keep_size", False)),
                   twin_rooms=str(BR.value(loaded, "render.twin_rooms", "one")),
                   assumed=tuple(k for k in loaded.get("assumed", []) if k in cls.KEYS),
                   brief_path=loaded.get("path"), warnings=tuple(loaded.get("warnings", [])))

    def to_dict(self) -> dict:
        return {"furnished_rooms": self.mode, "furnished_rooms_keep": list(self.keep),
                "furnished_rooms_keep_size": self.keep_size, "render.twin_rooms": self.twin_rooms,
                "assumed": list(self.assumed), "brief": self.brief_path, "warnings": list(self.warnings)}


def load_settings(project_dir) -> Settings:
    from wenart import brief as BR

    return Settings.from_brief(BR.load_brief(project_dir))


def style_families() -> list[str]:
    """The style enum: the family keywords of ``vocabulary.STYLE_FAMILIES`` and ``neutral`` (the catalogue's)."""
    from wenart.furniture import catalog as C

    return list(C.style_values())


def colour_names() -> list[str]:
    """The colour enum: the vocabulary colours the decor and the parametric looks know today."""
    from wenart.blender.parametric import DECOR_COLOURS

    return list(DECOR_COLOURS)


# --------------------------------------------------------------------------
# Rooms and partners
# --------------------------------------------------------------------------

def _label_key(text: str) -> str:
    return B.fold_ascii(B.turkish_lower(str(text))).strip()


def is_kept(room: dict, settings: Settings) -> bool:
    """The room is in ``furnished_rooms_keep`` (by id, or by label ignoring case and Turkish letters)."""
    names = {_label_key(k) for k in settings.keep}
    return room["id"] in settings.keep or _label_key(room.get("label", "")) in names


def furnished_rooms(building: dict) -> list[dict]:
    return [r for r in building["rooms"] if r.get("has_documented_furniture")]


def completion_skip_reason(room: dict, settings: Settings) -> Optional[str]:
    """Why a furnished room is not completed (None: it is)."""
    rtype = room.get("room_type")
    if settings.mode != "complete":
        return f"furnished_rooms: {settings.mode} (drawn furniture only restyled, Milestone 9)"
    if rtype in schemas.NOT_FURNISHED_ROOM_TYPES:
        return f"{rtype} room: never furnished by AI"
    if rtype not in schemas.ALLOWED_TYPES:
        return f"room type {rtype}: no furniture types to complete"
    if is_kept(room, settings):
        return "in furnished_rooms_keep: drawn furniture only restyled"
    return None


def partner_of(room: dict, settings: Settings) -> Optional[tuple[str, str]]:
    """``(partner room id, "same_as" | "twin")`` of a room that takes its partner's decisions, else None."""
    if room.get("same_as"):
        return room["same_as"], "same_as"
    if room.get("twin_of") and settings.twin_rooms == "one":
        return room["twin_of"], "twin"
    return None


@dataclass
class Transform:
    """The map from a partner room onto this room: identity (``same_as``) or a mirror about an axis (twins)."""
    kind: str                                   # identity | mirror
    origin: tuple[float, float] = (0.0, 0.0)    # a point on the mirror axis
    axis_deg: float = 0.0                       # direction of the mirror axis
    deviation_m: float = 0.0                    # the largest polygon / piece distance after the map

    def point(self, p) -> tuple[float, float]:
        if self.kind == "identity":
            return float(p[0]), float(p[1])
        a = math.radians(self.axis_deg)
        d = (math.cos(a), math.sin(a))
        v = (float(p[0]) - self.origin[0], float(p[1]) - self.origin[1])
        t = v[0] * d[0] + v[1] * d[1]
        foot = (self.origin[0] + d[0] * t, self.origin[1] + d[1] * t)
        return 2 * foot[0] - float(p[0]), 2 * foot[1] - float(p[1])

    def direction(self, deg: Optional[float]) -> Optional[float]:
        if deg is None or self.kind == "identity":
            return deg
        return G.normalise_angle(2.0 * self.axis_deg - float(deg))

    def rotation(self, rotation_deg: float) -> float:
        """Footprint rotation of the mapped piece (front = local -Y: the front direction maps, the width axis
        follows)."""
        if self.kind == "identity":
            return G.normalise_angle(rotation_deg)
        return G.normalise_angle(2.0 * self.axis_deg - float(rotation_deg) - 180.0)

    def side(self, side: Optional[str]) -> Optional[str]:
        if side is None or self.kind == "identity":
            return side
        return {"left": "right", "right": "left"}[side]

    def to_dict(self) -> dict:
        return {"kind": self.kind, "origin": [round(self.origin[0], 4), round(self.origin[1], 4)],
                "axis_deg": round(self.axis_deg, 3), "deviation_m": round(self.deviation_m, 4)}


def _hausdorff(a: list, b: list) -> float:
    return Polygon(a).exterior.hausdorff_distance(Polygon(b).exterior)


def _pieces_in(building: dict, room_id: str, source: str = "from_documents") -> list[dict]:
    return [f for f in building["furniture"] if f.get("room_id") == room_id and f.get("source") == source]


def match_pieces(partner_pieces: list[dict], pieces: list[dict], t: Transform) -> tuple[Optional[dict], str, float]:
    """``({partner id: piece id}, reason, deviation)``: every partner piece mapped onto one piece of the same type
    and size, centre within ``PARTNER_TOL_M`` and front within ``PARTNER_FRONT_TOL_DEG``."""
    if len(partner_pieces) != len(pieces):
        return None, f"{len(partner_pieces)} drawn pieces in the partner, {len(pieces)} here", 0.0
    free = list(pieces)
    out, worst = {}, 0.0
    for p in partner_pieces:
        c = t.point(p["footprint"]["center"])
        front = t.direction(p.get("front_deg"))
        best = None
        for q in free:
            if q["type"] != p["type"]:
                continue
            d = G.distance(c, q["footprint"]["center"])
            sizes = zip(sorted(p["footprint"]["size"]), sorted(q["footprint"]["size"]))
            if d > PARTNER_TOL_M or any(abs(float(x) - float(y)) > PARTNER_TOL_M for x, y in sizes):
                continue
            qf = q.get("front_deg")
            if (front is None) != (qf is None) or (front is not None and
                                                   G.angle_difference_deg(front, qf) > PARTNER_FRONT_TOL_DEG):
                continue
            if best is None or d < best[0]:
                best = (d, q)
        if best is None:
            return None, f"drawn {p['type']} {p['id']} has no counterpart here", 0.0
        free.remove(best[1])
        out[p["id"]] = best[1]["id"]
        worst = max(worst, best[0])
    return out, "", worst


def partner_transform(room: dict, partner: dict, kind: str, building: dict) -> tuple[Optional[Transform], str]:
    """The map partner -> room, verified on the polygons and the drawn pieces; ``(None, reason)`` when it fails."""
    if kind == "same_as":
        t = Transform("identity")
    else:
        ca, cb = G.polygon_centroid(partner["polygon"]), G.polygon_centroid(room["polygon"])
        if G.distance(ca, cb) < 1e-6:
            return None, "twin rooms with the same centroid: no mirror axis"
        n = math.atan2(cb[1] - ca[1], cb[0] - ca[0])
        mid = ((ca[0] + cb[0]) / 2.0, (ca[1] + cb[1]) / 2.0)
        t = Transform("mirror", origin=mid, axis_deg=G.normalise_angle(math.degrees(n) + 90.0))
    mapped = [t.point(p) for p in partner["polygon"]]
    dev = _hausdorff(mapped, room["polygon"])
    if dev > PARTNER_TOL_M:
        return None, f"the {kind} polygon does not map onto this room ({dev:.3f} m > {PARTNER_TOL_M} m)"
    mapping, why, worst = match_pieces(_pieces_in(building, partner["id"]), _pieces_in(building, room["id"]), t)
    if mapping is None:
        return None, f"the {kind}'s drawn furniture does not map onto this room: {why}"
    t.deviation_m = max(dev, worst)
    return t, ""


# --------------------------------------------------------------------------
# Drawn pieces and the question
# --------------------------------------------------------------------------

@dataclass
class Drawn:
    item: dict                   # the building furniture dict as given
    kind: str                    # fixed | obstacle | kept | mounted | changeable | other
    anchor: dict
    piece: placer.Piece          # front frame; against_wall from the anchor
    unverified: bool = False

    @property
    def id(self) -> str:
        return self.item["id"]

    def to_prompt(self) -> dict:
        fp = self.item["footprint"]
        out = {"id": self.id, "type": self.item["type"], "kind": "changeable" if self.kind == "changeable" else "fixed",
               "center": [round(float(fp["center"][0]), 2), round(float(fp["center"][1]), 2)],
               "size": [round(self.piece.size[0], 2), round(self.piece.size[1], 2)],
               "rotation_deg": round(self.piece.rotation_deg, 1),
               "front_deg": None if self.item.get("front_deg") is None else round(float(self.item["front_deg"]), 1),
               "anchor": {"kind": self.anchor["kind"], "point": [round(v, 2) for v in self.anchor["point"]]},
               "against_wall": self.anchor.get("wall_id") if self.anchor["kind"] == "back_edge" else None}
        if self.unverified:
            out["status"] = "unverified (type not sure; only its type may change, the footprint stays)"
        if self.item.get("shape") == "L":
            out["shape"] = f"L, long seat on the {self.item.get('chaise_side') or 'right'}"
        return out


def classify_drawn(room: dict, building: dict) -> list[Drawn]:
    """The room's drawn pieces (and any other piece already there, as an obstacle) in building order."""
    out = []
    for i, f in enumerate(p for p in building["furniture"] if p.get("room_id") == room["id"]):
        anchor = LK.anchor_of(f, building)
        if f.get("source") != "from_documents":
            kind = "other"
        elif f["type"] in schemas.MOUNTED_TYPES:
            kind = "mounted"
        elif f.get("build") is False:
            kind = "obstacle"
        elif f["type"] in schemas.FIXED_TYPES:
            kind = "fixed"
        elif f["type"] in schemas.UNCHANGEABLE_TYPES:
            kind = "kept"
        else:
            kind = "changeable"
        unverified = f.get("status") == "unverified" or f["type"] == "unknown"
        piece = placer.drawn_piece(f, i, against_wall=anchor["kind"] == "back_edge")
        out.append(Drawn(f, kind, anchor, piece, unverified=unverified and kind == "changeable"))
    return out


def _present(drawn: list[Drawn], pieces: Optional[list[placer.Piece]] = None) -> list[tuple[str, tuple]]:
    """``(type, size)`` of the built floor pieces (the final ``pieces`` when given, in drawn order)."""
    out = []
    for k, d in enumerate(drawn):
        if d.kind in ("mounted", "obstacle"):
            continue
        p = pieces[k] if pieces is not None else d.piece
        out.append((p.type, p.size))
    return out


def room_block(room: dict, ctx: placer.RoomContext, building: dict) -> dict:
    """The room as the completion question gives it (doors with their approach point, windows with the sill)."""
    doors, windows = placer.room_openings(building, room)
    approach = {d.id: d.approach_point for d in ctx.doors}
    r2 = lambda v: round(float(v), 2)   # noqa: E731
    return {
        "room_id": room["id"], "label": room["label"], "room_type": room.get("room_type", "other"),
        "room_subtype": room.get("room_subtype"), "area_m2": r2(room["area_computed"]),
        "polygon_m": [[r2(x), r2(y)] for x, y in room["polygon"]],
        "doors": [{"id": d["id"], "center": [r2(d["center"][0]), r2(d["center"][1])], "width": r2(d["width"]),
                   "opens_into_this_room": d.get("swing_side") == room["id"],
                   "approach": [r2(v) for v in approach.get(d["id"], d["center"])]} for d in doors],
        "windows": [{"id": w["id"], "center": [r2(w["center"][0]), r2(w["center"][1])], "width": r2(w["width"]),
                     "sill_height": r2(w["sill_height"]) if w.get("sill_height") is not None else None}
                    for w in windows],
    }


def build_question(room: dict, building: dict, drawn: list[Drawn], ctx: placer.RoomContext,
                   settings: Settings) -> tuple[dict, dict]:
    """``(question, plan)`` of one room (the prompt's input, also written to the debug JSON)."""
    rtype, subtype = room.get("room_type", "other"), room.get("room_subtype")
    plan = schemas.completion_plan(rtype, subtype, _present(drawn))
    changeable = [d for d in drawn if d.kind == "changeable"]
    change_types = [] if settings.keep_size or not changeable else list(schemas.change_types(rtype, subtype))
    add = dict(plan["addable"])
    question = {"room": room_block(room, ctx, building), "drawn": [d.to_prompt() for d in drawn if d.kind != "other"],
                "change_ids": [d.id for d in changeable] if change_types else [],
                "change_types": change_types, "add": add, "missing": plan["missing"],
                "anchor_missing": plan["anchor_missing"], "anchors": list(plan["anchors"]),
                "anchors_addable": [a for a in plan["anchors"] if a in add],
                "styles": style_families(), "colours": colour_names(), "keep_size": settings.keep_size}
    return question, plan


_SIZE = {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 2, "maxItems": 2}


def answer_schema(question: dict) -> dict:
    """The strict schema of one room (§2.3): enums built from the question; xgrammar-safe (no uniqueItems,
    no if/then): an empty list is ``maxItems: 0``."""
    ids, types, add = question["change_ids"], question["change_types"], question["add"]
    if ids and types:
        changes = {"type": "array", "maxItems": len(ids), "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "type", "size", "style", "colour", "reason"],
            "properties": {"id": {"enum": list(ids)}, "type": {"enum": list(types)}, "size": dict(_SIZE),
                           "style": {"enum": list(question["styles"])}, "colour": {"enum": list(question["colours"])},
                           "reason": {"type": "string", "maxLength": 200}}}}
    else:
        changes = {"type": "array", "maxItems": 0}
    if add:
        added = {"type": "array", "maxItems": min(schemas.MAX_PIECES, sum(add.values())), "items": {
            "type": "object", "additionalProperties": False,
            "required": ["type", "center", "rotation_deg", "size", "against_wall", "reason"],
            "properties": {"type": {"enum": list(add)},
                           "center": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
                           "rotation_deg": {"type": "number", "minimum": 0, "maximum": 360}, "size": dict(_SIZE),
                           "against_wall": {"type": "boolean"}, "reason": {"type": "string", "maxLength": 200}}}}
    else:
        added = {"type": "array", "maxItems": 0}
    return {"type": "object", "additionalProperties": False, "required": ["changes", "added"],
            "properties": {"changes": changes, "added": added}}


def schema_errors(data, schema: dict) -> list[str]:
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]


# --------------------------------------------------------------------------
# Agreement (§2.4)
# --------------------------------------------------------------------------

def snap_option(ftype: str, size) -> tuple[float, float]:
    """The size option of ``ftype`` nearest to ``size`` in either orientation (the option as listed)."""
    w, d = float(size[0]), float(size[1])
    return min(schemas.SIZE_OPTIONS[ftype],
               key=lambda o: min(abs(o[0] - w) + abs(o[1] - d), abs(o[0] - d) + abs(o[1] - w)))


def _by_id(answer: Optional[dict]) -> tuple[dict, list]:
    out, dupes = {}, []
    for item in (answer or {}).get("changes", []):
        if item["id"] in out:
            dupes.append(item)
        else:
            out[item["id"]] = item
    return out, dupes


def agree_changes(answers: dict[int, Optional[dict]], drawn_order: list[str]) -> tuple[list[dict], list[dict]]:
    """``(agreed, not agreed)``: both passes change the same piece to the same type (§2.4)."""
    a, dup_a = _by_id(answers.get(1))
    b, dup_b = _by_id(answers.get(2))
    agreed, other = [], []
    for item in dup_a + dup_b:
        other.append({"id": item["id"], "type": item["type"], "status": "not_agreed",
                      "reason": "the same piece listed twice in one pass: the second entry ignored"})
    for pid in drawn_order:
        x, y = a.get(pid), b.get(pid)
        if x is None and y is None:
            continue
        if x is None or y is None:
            k, item = (1, x) if y is None else (2, y)
            other.append({"id": pid, "type": item["type"], "status": "not_agreed", "passes": [k],
                          "reason": f"only pass {k} changes it (a drawn piece needs both passes)"})
            continue
        if x["type"] != y["type"]:
            other.append({"id": pid, "type": f"{x['type']} / {y['type']}", "status": "not_agreed", "passes": [1, 2],
                          "reason": f"the passes disagree on the type ({x['type']} / {y['type']})"})
            continue
        sx, sy = snap_option(x["type"], x["size"]), snap_option(y["type"], y["size"])
        agreed.append({"id": pid, "type": x["type"], "size": min(sx, sy, key=lambda o: (o[0] * o[1], o)),
                       "style": x["style"] if x["style"] == y["style"] else None,
                       "colour": x["colour"] if x["colour"] == y["colour"] else None,
                       "reasons": {1: x["reason"], 2: y["reason"]}, "passes": [1, 2]})
    return agreed, other


def check_change_rules(agreed: list[dict], drawn: list[Drawn], plan: dict) -> tuple[list[dict], list[dict]]:
    """``(kept, refused)``: the main piece stays a main piece type, nothing else becomes one; a change may not
    take a type over its count (``plan["maxima"]``, at least what the documents draw)."""
    anchors = set(plan["anchors"])
    by_id = {d.id: d for d in drawn}
    counts = Counter(t for t, _ in _present(drawn))
    drawn_counts = Counter(counts)
    has_anchor = plan["has_anchor"]
    kept, refused = [], []
    for ch in agreed:
        old, new = by_id[ch["id"]].item["type"], ch["type"]
        reason = None
        if old in anchors and new not in anchors:
            reason = f"the room's main piece ({old}) may only become another main piece type"
        elif old not in anchors and new in anchors and (has_anchor or not by_id[ch["id"]].unverified):
            reason = f"never a second main piece: {old} cannot become {new}"
        elif (new != old and new not in anchors and new in plan["maxima"]
              and counts[new] + 1 > max(plan["maxima"][new], drawn_counts[new])):
            reason = f"the room already holds {counts[new]} {new} (at most {plan['maxima'][new]})"
        if reason:
            refused.append(dict(ch, status="refused", reason=reason))
            continue
        counts[old] -= 1
        counts[new] += 1
        if new in anchors:
            has_anchor = True
        kept.append(ch)
    return kept, refused


def filter_added(items: list[dict], plan: dict, room_type: str) -> tuple[list[dict], list[dict]]:
    """``(kept, refused)`` of one pass's added pieces: types the room may still get, at most their count, one main
    piece."""
    left = dict(plan["addable"])
    anchors = set(plan["anchors"])
    anchor_taken = plan["has_anchor"]
    kept, refused = [], []
    for item in items:
        t = item["type"]
        reason = None
        if t not in left:
            reason = (f"covered: the room holds its maximum of {t}" if t in plan["maxima"]
                      else f"not a type the AI may add to a {room_type}")
        elif left[t] <= 0:
            reason = f"covered: at most {plan['maxima'].get(t, 0)} {t}"
        elif t in anchors and anchor_taken:
            reason = f"never a second main piece ({t})"
        if reason:
            refused.append({"type": t, "center": item["center"], "reason": reason})
            continue
        left[t] -= 1
        if t in anchors:
            anchor_taken = True
        kept.append(item)
    return kept, refused


def companion_problems(added: list[placer.Piece], floor: list[placer.Piece], room_type: str) -> dict[int, str]:
    """Index in ``added`` -> why it lacks its companion (an office chair at a desk, a bar stool at an island, a
    chair at a dining table; chairs in an ``other`` room are free, as in Milestone 4)."""
    out = {}
    for i, p in enumerate(added):
        hosts_types = schemas.COMPANIONS.get(p.type)
        if not hosts_types or (p.type == "chair" and room_type == "other"):
            continue
        hosts = [q for q in floor + added if q.type in hosts_types]
        if not hosts:
            out[i] = f"no {' or '.join(hosts_types)} in the room"
            continue
        gap = min(p.polygon().distance(q.polygon()) for q in hosts)
        if gap > schemas.COMPANION_REACH_M + 1e-9:
            out[i] = f"{gap:.2f} m from the nearest {' or '.join(hosts_types)} (> {schemas.COMPANION_REACH_M} m)"
    return out


def _agrees(piece: placer.Piece, other: Optional[list[dict]]) -> Optional[dict]:
    for item in other or []:
        if item["type"] == piece.type and G.distance(piece.proposed["center"], item["center"]) <= AGREE_DISTANCE_M:
            return item
    return None


# --------------------------------------------------------------------------
# Per room
# --------------------------------------------------------------------------

@dataclass
class RoomCompletion:
    room: dict
    state: str = "completed"
    reason: str = ""
    partner: Optional[dict] = None              # {"id", "kind", "transform"}
    drawn: list = field(default_factory=list)   # Drawn
    question: Optional[dict] = None
    plan: Optional[dict] = None
    schema: Optional[dict] = None
    passes: list = field(default_factory=list)  # one dict per pass
    changes: list = field(default_factory=list)
    added: list = field(default_factory=list)   # final furniture dicts
    refused: list = field(default_factory=list)
    dropped: list = field(default_factory=list)
    wall_cabinets: list = field(default_factory=list)
    placements: dict = field(default_factory=dict)
    chosen_pass: Optional[int] = None
    drawn_layout: dict = field(default_factory=dict)
    floor: list = field(default_factory=list)          # the drawn floor pieces (Drawn, not wall-mounted)
    final_pieces: list = field(default_factory=list)   # their placer pieces after the changes (same order)
    context: Optional[placer.RoomContext] = None

    @property
    def room_id(self) -> str:
        return self.room["id"]

    @property
    def transport_errors(self) -> list[tuple[int, str]]:
        return [(p["pass"], p["error"]) for p in self.passes if p.get("transport_error")]

    @property
    def latency_s(self) -> float:
        return round(sum(p.get("latency_s", 0.0) for p in self.passes), 3)

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id, "label": self.room["label"], "room_type": self.room.get("room_type"),
            "room_subtype": self.room.get("room_subtype"), "state": self.state, "reason": self.reason,
            "partner": self.partner,
            "drawn": [{"id": d.id, "type": d.item["type"], "kind": d.kind, "unverified": d.unverified,
                       "anchor": d.anchor} for d in self.drawn],
            "missing": (self.plan or {}).get("missing", {}), "anchor_missing": (self.plan or {}).get("anchor_missing"),
            "addable": (self.question or {}).get("add", {}), "change_types": (self.question or {}).get("change_types", []),
            "passes": [{k: v for k, v in p.items() if k not in ("data", "prompt", "raw_text")} for p in self.passes],
            "chosen_pass": self.chosen_pass, "changes": self.changes,
            "added": [{"id": f["id"], "type": f["type"], "center": f["footprint"]["center"],
                       "size": f["footprint"]["size"], "rotation_deg": f["footprint"]["rotation_deg"],
                       "confidence": f["evidence"][0]["confidence"], "method": f.get("method"),
                       "mirrored_from": f.get("mirrored_from")} for f in self.added],
            "refused": self.refused, "dropped": self.dropped,
            "wall_cabinets": [{"id": f["id"], "run": f["rule"]["run"], "size": f["footprint"]["size"],
                               "excluded": f["rule"]["excluded"]} for f in self.wall_cabinets],
            "drawn_layout": self.drawn_layout, "latency_s": self.latency_s,
        }


def _ai_evidence(model: str, reasons: dict, confidence: float) -> list[dict]:
    return [B.evidence(EVIDENCE_FILE, "ai", confidence, model=model, pass_=k, text=str(r or "changed by the AI"))
            for k, r in sorted(reasons.items())]


def _design(item: dict, ftype: str, style: Optional[str], colour: Optional[str], family: Optional[str]) -> dict:
    design = dict(item.get("design") or {})
    design["style_family"] = style or family
    if colour:
        design["fabric_colour" if ftype in schemas.FABRIC_TYPES else "colour"] = colour
    return design


def _apply_change(item: dict, anchor: dict, final: placer.Piece, record: dict, evidence: list[dict],
                  design: dict, unverified: bool, mirrored_from: Optional[str] = None) -> dict:
    """The changed drawn piece (§2.6): ``from_documents``, ``modified_by_ai``, the drawn values, the anchor and
    the AI evidence. The footprint changes only with the type or size (an unverified piece keeps it)."""
    new = copy.deepcopy(item)
    new["modified_by_ai"] = True
    new["drawn_type"] = item["type"]
    new["drawn_footprint"] = copy.deepcopy(item["footprint"])
    new["drawn_height"] = item.get("height")
    new["anchor"] = anchor
    if record["status"] == "applied" and not record["look_only"]:
        if not unverified:
            new["footprint"] = {"center": [round(final.center[0], 4), round(final.center[1], 4)],
                                "size": [final.size[0], final.size[1]], "rotation_deg": round(final.rotation_deg, 4)}
        if final.type != item["type"]:
            new["type"] = final.type
            new["height"] = schemas.HEIGHTS.get(final.type)
            if unverified:
                new["type_proposal"] = True
        if final.shape == "L":
            new.update(shape="L", chaise_side=final.chaise_side, chaise_depth=final.chaise_depth)
        elif item.get("shape") == "L":
            for key in ("shape", "chaise_side", "chaise_depth"):
                new.pop(key, None)
    new["design"] = design
    new["evidence"] = list(item["evidence"]) + evidence
    if mirrored_from:
        new["mirrored_from"] = mirrored_from
    return new


def _oriented(option, drawn: Drawn) -> tuple[tuple[float, float], bool]:
    """A size option and whether it is turned to follow a drawn piece without a front (a table drawn along Y)."""
    if drawn.item.get("front_deg") is not None:
        return tuple(option), False
    dw, dd = drawn.piece.size
    ow, od = option
    return tuple(option), (dw - dd) * (ow - od) < -1e-9


def _requests(changes: list[dict], drawn: list[Drawn]) -> list[placer.ChangeRequest]:
    index = {d.id: k for k, d in enumerate(drawn)}
    out = []
    for ch in changes:
        d = drawn[index[ch["id"]]]
        size, turned = _oriented(ch["size"], d)
        sides = tuple(ch.get("chaise_sides") or ("right", "left"))
        out.append(placer.ChangeRequest(index[ch["id"]], ch["type"], size, d.anchor, chaise_sides=sides,
                                        footprint_only=d.unverified, transposed=turned))
    return out


def run_changes(rec: RoomCompletion, changes: list[dict], ctx: placer.RoomContext, model: str,
                family: Optional[str], out: dict, mirrored: Optional[dict] = None) -> None:
    """Place the agreed changes, write the changed pieces into ``out`` and record them (``mirrored``: partner
    piece id per drawn id for copied decisions)."""
    floor = [d for d in rec.drawn if d.kind != "mounted"]
    rec.floor = floor
    requests = _requests(changes, floor)
    final, results, baseline = placer.place_changes([d.piece for d in floor], requests, ctx)
    rec.final_pieces = final
    rec.drawn_layout = {"pieces": {d.id: fails for d, fails in zip(floor, baseline["pieces"]) if fails},
                        "walkways": baseline["walkways"]}
    by_id = {f["id"]: i for i, f in enumerate(out["furniture"])}
    for ch, req, res in zip(changes, requests, results):
        d = floor[req.index]
        same = (res.piece.type == d.item["type"] and tuple(res.piece.size) == tuple(d.piece.size)
                and res.piece.chaise_side == d.piece.chaise_side)
        record = {"id": d.id, "drawn_type": d.item["type"], "drawn_size": list(d.piece.size), "type": res.piece.type,
                  "size": list(res.piece.size), "chaise_side": res.piece.chaise_side,
                  "style": ch.get("style"), "colour": ch.get("colour"),
                  "status": "applied" if res.applied else "reverted",
                  "shrunk": any(s["step"] == "shrink" and s["ok"] for s in res.steps),
                  "look_only": res.applied and same,
                  "type_proposal": d.unverified and res.applied and res.piece.type != d.item["type"],
                  "reason": res.reason or "; ".join(f"pass {k}: {r}" for k, r in sorted(ch.get("reasons", {}).items())),
                  "steps": res.steps, "agreed_type": ch["type"], "agreed_size": list(ch["size"])}
        if mirrored:
            record["mirrored_from"] = mirrored.get(d.id)
        rec.changes.append(record)
        look = bool(ch.get("style") or ch.get("colour") or ch.get("design"))
        if not ((res.applied and not same) or look):
            continue                                           # nothing changed: the drawn piece stays as it is
        evidence = ch.get("evidence") or _ai_evidence(model, ch.get("reasons", {}), CONFIDENCE_AGREED)
        design = ch.get("design") or _design(d.item, res.piece.type, ch.get("style"), ch.get("colour"), family)
        out["furniture"][by_id[d.id]] = _apply_change(d.item, d.anchor, res.piece, record, evidence, design,
                                                      d.unverified, (mirrored or {}).get(d.id))
    for d in floor:
        if d.kind == "changeable" and "anchor" not in out["furniture"][by_id[d.id]]:
            out["furniture"][by_id[d.id]]["anchor"] = d.anchor


def _obstacles(rec: RoomCompletion) -> list[placer.Piece]:
    return list(rec.final_pieces)


def _final_present(rec: RoomCompletion) -> list[tuple[str, tuple]]:
    """``(type, size)`` of the built floor pieces after the changes (the plan's input)."""
    return [(p.type, p.size) for d, p in zip(rec.floor, rec.final_pieces) if d.kind != "obstacle"]


def place_added(rec: RoomCompletion, answers: dict[int, Optional[dict]], ctx: placer.RoomContext, model: str,
                out: dict) -> None:
    """Filter, place and check every pass's added pieces; keep the best pass (see the module docstring)."""
    rtype = rec.room.get("room_type", "other")
    plan = schemas.completion_plan(rtype, rec.room.get("room_subtype"), _final_present(rec))
    rec.plan = dict(rec.plan or {}, after_changes={k: plan[k] for k in ("missing", "addable", "has_anchor")})
    raw = {k: (a or {}).get("added", []) for k, a in answers.items()}
    candidates = {}
    for pass_no, items in sorted(raw.items()):
        if answers.get(pass_no) is None:
            continue
        kept, refused = filter_added(items, plan, rtype)
        rec.refused += [dict(r, **{"pass": pass_no}) for r in refused]
        if not kept:
            continue
        placement = placer.place(kept, ctx, obstacles=_obstacles(rec))
        drop = companion_problems(placement.pieces, _obstacles(rec), rtype)
        for i, piece in enumerate(placement.pieces):
            if placer.failed_checks(placement.checks[i]) and i not in drop:
                drop[i] = "fails " + ", ".join(placer.failed_checks(placement.checks[i]))
        for i in sorted(drop, reverse=True):
            piece = placement.pieces.pop(i)
            placement.checks.pop(i)
            placement.dropped.append({"type": piece.type, "proposed": piece.proposed, "last": piece.state(),
                                      "failed": [], "reason": drop[i], "repairs": list(piece.repairs)})
        rec.placements[pass_no] = placement
        candidates[pass_no] = placement
    for pass_no, placement in sorted(rec.placements.items()):
        for d in placement.dropped:
            rec.dropped.append({"pass": pass_no, "type": d["type"], "center": d["proposed"]["center"],
                                "reason": d["reason"], "failed": d.get("failed", [])})
    usable = [(len(p.dropped), k) for k, p in sorted(candidates.items()) if p.pieces]
    if not usable:
        return
    rec.chosen_pass = min(usable)[1]
    chosen = candidates[rec.chosen_pass]
    from wenart.furniture import layout as L   # the M4 piece dict (lazy: layout imports this module in its CLI)

    room = rec.room
    number = L._next_furniture_number(out, room["level_id"])
    for piece, checks in zip(chosen.pieces, chosen.checks):
        others = [raw[k] for k in raw if k != rec.chosen_pass]
        match = next((m for o in others for m in [_agrees(piece, o)] if m), None)
        confidence = CONFIDENCE_AGREED if match else CONFIDENCE_SINGLE
        f = L.furniture_dict(piece, checks, room, B.element_id("furniture", room["level_id"], number), model,
                             rec.chosen_pass, confidence, match is not None)
        f["completes_room"] = True
        f["method"] = "ai"
        if match:
            other_pass = next(k for k in raw if k != rec.chosen_pass)
            f["evidence"].append(B.evidence(EVIDENCE_FILE, "ai", confidence, model=model, pass_=other_pass,
                                            text=match.get("reason") or f"{piece.type} proposed by the other pass"))
        if piece.shape == "L":
            f.update(shape="L", chaise_side=piece.chaise_side, chaise_depth=piece.chaise_depth)
        out["furniture"].append(f)
        rec.added.append(f)
        number += 1


# --------------------------------------------------------------------------
# Wall cabinets along a drawn counter run (§4.4, rule)
# --------------------------------------------------------------------------

def _opening_box(op: dict, building: dict) -> Polygon:
    """The opening's plan rectangle through its wall (width x wall thickness + 2 cm): a gap to it is measured
    along the wall."""
    c = (float(op["center"][0]), float(op["center"][1]))
    wall = next((w for w in building.get("walls", []) if w["id"] == op.get("wall_id")), None)
    if wall is not None and G.distance(wall["start"], wall["end"]) > 1e-9:
        a = math.atan2(wall["end"][1] - wall["start"][1], wall["end"][0] - wall["start"][0])
        t = float(wall.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M)
    else:
        a, t = 0.0, placer.DEFAULT_WALL_THICKNESS_M
    h = float(op["width"]) / 2.0
    start = (c[0] - math.cos(a) * h, c[1] - math.sin(a) * h)
    end = (c[0] + math.cos(a) * h, c[1] + math.sin(a) * h)
    return Polygon(G.centerline_to_rectangle(start, end, t + 0.02))


def _height(item: dict) -> float:
    h = item.get("height")
    return float(h) if h is not None else schemas.HEIGHTS.get(item["type"], 1.0)


def wall_cabinets_for(room: dict, building: dict, items: list[dict]) -> list[dict]:
    """Wall cabinet runs ``{"run", "center", "size", "rotation_deg", "excluded"}`` along every drawn counter run
    against a wall in ``room`` (``items``: the room's final furniture dicts)."""
    ring = Polygon(room["polygon"]).exterior
    doors, windows = placer.room_openings(building, room)
    blocked = [(f"window {w['id']}", _opening_box(w, building), WALL_CABINET_WINDOW_GAP_M) for w in windows]
    blocked += [(f"door {d['id']}", _opening_box(d, building), WALL_CABINET_DOOR_GAP_M) for d in doors]
    under = [(f"{f['type']} {f['id']}", placer.drawn_piece(f).polygon()) for f in items
             if f["type"] not in schemas.MOUNTED_TYPES and f.get("build") is not False
             and (f["type"] == "stove" or _height(f) > schemas.WALL_CABINET_Z[0] - 0.05)]
    counters = [f for f in items if f["type"] == "kitchen_counter" and f.get("source") == "from_documents"
                and f.get("build") is not False and f.get("front_deg") is not None]
    placed: list[tuple[str, Polygon]] = []
    out = []
    for counter in sorted(counters, key=lambda f: f["id"]):
        if LK.anchor_of(counter, building)["kind"] != "back_edge":
            continue
        rot, size = placer.front_frame(counter["footprint"], counter.get("front_deg"))
        c = (float(counter["footprint"]["center"][0]), float(counter["footprint"]["center"][1]))
        w, d = size
        mid = placer.back_edge_midpoint(c, rot, size)
        back = math.radians(rot + 90.0)
        ray = LineString([mid, (mid[0] + math.cos(back) * WALL_FACE_REACH_M, mid[1] + math.sin(back) * WALL_FACE_REACH_M)])
        hit = ray.intersection(ring)
        offset = 0.0 if hit.is_empty else Point(mid).distance(hit)     # the cabinet's back on the wall face
        y1 = d / 2.0 + offset
        y0 = y1 - WALL_CABINET_DEPTH_M
        n = max(1, int(math.floor(w / WALL_CABINET_STEP_M + 1e-6)))
        edges = [-w / 2.0 + k * WALL_CABINET_STEP_M for k in range(n)] + [w / 2.0]
        free, reasons = [], []
        for x0, x1 in zip(edges, edges[1:]):
            cell = placer._local_box(c, rot, x0, x1, y0, y1)
            why = next((name for name, seg, gap in blocked if cell.distance(seg) < gap - 1e-9), None)
            why = why or next((name for name, poly in under + placed if cell.intersection(poly).area > placer.AREA_EPS),
                              None)
            free.append(why is None)
            reasons.append(why)
        runs, start = [], None
        for k, ok in enumerate(free + [False]):
            if ok and start is None:
                start = k
            elif not ok and start is not None:
                runs.append((start, k))
                start = None
        excluded = sorted({r for r in reasons if r})
        for a, b in runs:
            x0, x1 = edges[a], edges[b]
            if x1 - x0 < WALL_CABINET_MIN_M - 1e-9:
                continue
            centre = G.rotate_point((c[0] + (x0 + x1) / 2.0, c[1] + (y0 + y1) / 2.0), rot, c)
            spec = {"run": counter["id"], "center": [round(centre[0], 4), round(centre[1], 4)],
                    "size": [round(x1 - x0, 3), WALL_CABINET_DEPTH_M], "rotation_deg": round(rot, 4),
                    "excluded": excluded, "design": {k: v for k, v in (counter.get("design") or {}).items()
                                                     if k in ("front_style", "colour", "handle")}}
            out.append(spec)
            placed.append((f"wall cabinet over {counter['id']}", placer._local_box(c, rot, x0, x1, y0, y1)))
    return out


def add_wall_cabinets(rec: RoomCompletion, building: dict, out: dict) -> None:
    room = rec.room
    items = [f for f in out["furniture"] if f.get("room_id") == room["id"]]
    if any(f["type"] == "wall_cabinet" and f.get("source") == "from_documents" for f in items):
        return                                                   # drawn wall cabinets: the documents decide
    from wenart.furniture import layout as L

    number = L._next_furniture_number(out, room["level_id"])
    for spec in wall_cabinets_for(room, building, items):
        lo, hi = schemas.WALL_CABINET_Z
        f = {"id": B.element_id("furniture", room["level_id"], number), "level_id": room["level_id"],
             "room_id": room["id"], "type": "wall_cabinet", "type_raw": None, "source": "added_by_ai",
             "footprint": {"center": spec["center"], "size": spec["size"], "rotation_deg": spec["rotation_deg"]},
             "front_deg": G.front_direction_deg(spec["rotation_deg"]), "height": round(hi - lo, 3), "asset": None,
             "status": "verified", "completes_room": True, "method": "rule",
             "evidence": [B.evidence(EVIDENCE_FILE, "derived", 1.0, text=(
                 f"wall cabinets along the counter run {spec['run']} (rule, docs/milestone10.md §4.4), {lo:.2f}-"
                 f"{hi:.2f} m" + (f"; left free: {', '.join(spec['excluded'])}" if spec["excluded"] else "")))],
             "rule": {"run": spec["run"], "z": [lo, hi], "excluded": spec["excluded"]}}
        if spec["design"]:
            f["design"] = spec["design"]
        out["furniture"].append(f)
        rec.wall_cabinets.append(f)
        number += 1


# --------------------------------------------------------------------------
# Asking and completing one room
# --------------------------------------------------------------------------

def ask_room(rec: RoomCompletion, style_text: str, client, passes: int) -> dict[int, Optional[dict]]:
    answers: dict[int, Optional[dict]] = {}
    for pass_no in range(1, passes + 1):
        prompt = prompts.completion_prompt(rec.question, style_text, pass_no)
        proposal = client.complete(prompt, rec.schema, pass_no)
        entry = {"pass": pass_no, "model": proposal.model, "latency_s": round(proposal.latency_s, 3),
                 "error": proposal.error, "transport_error": bool(proposal.transport_error), "data": proposal.data,
                 "prompt": prompt, "raw_text": proposal.raw_text}
        if proposal.data is not None:
            entry.update(changes=len(proposal.data["changes"]), added=len(proposal.data["added"]))
        rec.passes.append(entry)
        answers[pass_no] = proposal.data
    return answers


def _model_of(rec: RoomCompletion, fallback: str) -> str:
    return next((p["model"] for p in rec.passes if p.get("model") and p["model"] != "?"), fallback)


def complete_room(room: dict, building: dict, out: dict, style_text: str, client, settings: Settings,
                  passes: int = PASSES, family: Optional[str] = None) -> RoomCompletion:
    """Ask, agree, place and label one room; ``out`` (the building being written) is changed in place."""
    rec = RoomCompletion(room)
    ctx = placer.room_context(building, room)
    rec.context = ctx
    rec.drawn = classify_drawn(room, out)
    rec.question, rec.plan = build_question(room, out, rec.drawn, ctx, settings)
    rec.schema = answer_schema(rec.question)
    asks = bool(rec.question["change_ids"]) or bool(rec.question["add"])
    answers: dict[int, Optional[dict]] = {}
    if asks:
        answers = ask_room(rec, style_text, client, passes)
    else:
        rec.reason = "nothing to ask: no changeable drawn piece and nothing the room may get"
    model = _model_of(rec, getattr(client, "_model", None) or "?")
    agreed, not_agreed = agree_changes(answers, [d.id for d in rec.drawn])
    kept, refused = check_change_rules(agreed, rec.drawn, rec.plan)
    rec.changes += not_agreed + refused
    run_changes(rec, kept, ctx, model, family, out)
    if any(a is not None for a in answers.values()):
        place_added(rec, answers, ctx, model, out)
    elif asks and not rec.reason:
        rec.reason = "no usable answer (" + "; ".join(f"pass {p['pass']}: {p['error']}" for p in rec.passes) + ")"
    add_wall_cabinets(rec, building, out)       # any room with a drawn counter run (a kitchen, an open kitchen)
    return rec


# --------------------------------------------------------------------------
# Partners: copied (same_as) or mirrored (twin) decisions
# --------------------------------------------------------------------------

def _map_footprint(fp: dict, t: Transform) -> dict:
    c = t.point(fp["center"])
    return {"center": [round(c[0], 4), round(c[1], 4)], "size": list(fp["size"]),
            "rotation_deg": round(t.rotation(float(fp["rotation_deg"])), 4)}


def copy_added(room: dict, partner_added: list[dict], t: Transform, obstacles: list[placer.Piece], building: dict,
               out: dict, ctx: placer.RoomContext) -> tuple[list[dict], list[dict]]:
    """The partner's added pieces mapped into ``room``; each must pass the six checks here with the drawn pieces as
    obstacles (no repairs: a failing copy is dropped and listed). Returns ``(added dicts, dropped)``."""
    from wenart.furniture import layout as L

    fixed = placer.obstacles_for(obstacles, ctx)
    room_ctx = placer.drawn_context(ctx, fixed) if fixed else ctx
    copies = []
    for f in partner_added:
        fp = _map_footprint(f["footprint"], t)
        piece = placer.Piece(f["type"], tuple(fp["center"]), float(fp["rotation_deg"]),
                             (float(fp["size"][0]), float(fp["size"][1])),
                             bool((f.get("layout") or {}).get("against_wall", False)))
        if f.get("shape") == "L":
            piece.shape, piece.chaise_side, piece.chaise_depth = "L", t.side(f.get("chaise_side")), f.get("chaise_depth")
        copies.append((f, fp, piece))
    dropped = []
    while True:
        pieces = fixed + [p for _f, _fp, p in copies]
        checks = placer.obstacle_checks(pieces, room_ctx)[len(fixed):]
        bad = [i for i, c in enumerate(checks) if placer.failed_checks(c)]
        if not bad:
            break
        f, _fp, _p = copies.pop(bad[-1])
        dropped.append({"type": f["type"], "mirrored_from": f["id"], "center": f["footprint"]["center"],
                        "reason": "the copy fails " + ", ".join(placer.failed_checks(checks[bad[-1]])) + " here"})
    added = []
    number = L._next_furniture_number(out, room["level_id"])
    for (f, fp, _p), c in zip(copies, checks):
        g = copy.deepcopy(f)
        g.update(id=B.element_id("furniture", room["level_id"], number), level_id=room["level_id"], room_id=room["id"],
                 footprint=fp, front_deg=G.front_direction_deg(fp["rotation_deg"]), checks=dict(c),
                 mirrored_from=f["id"], asset=None)
        if isinstance(g.get("layout"), dict):
            g["layout"] = dict(g["layout"], proposed={"center": list(fp["center"]), "size": list(fp["size"]),
                                                       "rotation_deg": fp["rotation_deg"]},
                               repairs=[], copied_from=f["id"])
        if f.get("shape") == "L":
            g["chaise_side"] = t.side(f.get("chaise_side"))
        out["furniture"].append(g)
        added.append(g)
        number += 1
    return added, dropped


def copy_room(room: dict, partner_rec: RoomCompletion, kind: str, t: Transform, building: dict, out: dict,
              settings: Settings) -> RoomCompletion:
    """This room takes the partner's decisions: the same changes on the matching drawn pieces (placed at this
    room's anchors), the partner's added pieces mapped here, the wall cabinet rule run here."""
    rec = RoomCompletion(room, state="mirrored" if kind == "twin" else "copied")
    rec.partner = {"id": partner_rec.room_id, "kind": kind, "transform": t.to_dict()}
    rec.reason = f"decisions of {partner_rec.room_id} ({kind}), not asked again"
    ctx = placer.room_context(building, room)
    rec.context = ctx
    rec.drawn = classify_drawn(room, out)
    rec.question, rec.plan = build_question(room, out, rec.drawn, ctx, settings)
    mapping, _why, _dev = match_pieces(_pieces_in(building, partner_rec.room_id), _pieces_in(building, room["id"]), t)
    reverse = {v: k for k, v in (mapping or {}).items()}
    partner_items = {f["id"]: f for f in out["furniture"] if f.get("room_id") == partner_rec.room_id}
    changes = []
    for d in rec.drawn:
        pid = reverse.get(d.id)
        p = partner_items.get(pid)
        ch = next((c for c in partner_rec.changes if c["id"] == pid and c["status"] in ("applied", "reverted")), None)
        if ch is None or p is None or not p.get("modified_by_ai"):
            continue                                           # the partner's piece stayed as drawn
        ev = [e for e in p["evidence"] if e.get("method") == "ai"]
        if ch["status"] == "applied":
            ftype = ch["type"]
            size = snap_option(ftype, ch["size"]) if ftype in schemas.SIZE_OPTIONS else tuple(ch["size"])
        else:                                                  # reverted there: only the look is copied
            ftype, size = d.item["type"], tuple(d.piece.size)
        if ch["status"] == "applied" and ch["look_only"]:
            ftype, size = d.item["type"], tuple(d.piece.size)
        side = t.side(ch.get("chaise_side")) if ftype == "sofa_corner" else None
        changes.append({"id": d.id, "type": ftype, "size": size, "style": ch.get("style"), "colour": ch.get("colour"),
                        "chaise_sides": (side, t.side(side)) if side else None, "evidence": ev,
                        "design": copy.deepcopy(p.get("design")), "reasons": {}})
    model = next((e.get("model") for c in changes for e in c["evidence"] if e.get("model")), "?")
    run_changes(rec, changes, ctx, model, None, out, mirrored=reverse)
    rec.added, rec.dropped = copy_added(room, list(partner_rec.added), t, rec.final_pieces, building, out, ctx)
    add_wall_cabinets(rec, building, out)       # any room with a drawn counter run (a kitchen, an open kitchen)
    return rec


def copy_empty_layout(room: dict, partner: dict, kind: str, partner_pieces: list[dict], building: dict,
                      out: dict) -> tuple[Optional[list[dict]], list[dict], dict]:
    """Milestone 4 layout of an empty partner room mapped into ``room`` (user decision 7).
    Returns ``(added dicts or None when the partner does not map, dropped, record)``."""
    t, why = partner_transform(room, partner, kind, building)
    if t is None:
        return None, [], {"room": partner["id"], "kind": kind, "reason": why}
    ctx = placer.room_context(building, room)
    added, dropped = copy_added(room, partner_pieces, t, [], building, out, ctx)
    return added, dropped, {"room": partner["id"], "kind": kind, "transform": t.to_dict()}


# --------------------------------------------------------------------------
# Whole building
# --------------------------------------------------------------------------

def complete_building(building: dict, style_text: str, client, settings: Settings, passes: int = PASSES,
                      debug_dir: Optional[Path] = None, family: Optional[str] = None) -> tuple[dict, list[RoomCompletion]]:
    """Complete every furnished room (new dict; the input is not changed). Rooms whose partner is completed take
    the partner's decisions; a partner that does not map is reported and the room is asked itself."""
    out = copy.deepcopy(building)
    records: dict[str, RoomCompletion] = {}
    order: list[str] = []
    pending: list[tuple[dict, tuple[str, str]]] = []
    rooms_by_id = {r["id"]: r for r in out["rooms"]}
    for room in furnished_rooms(out):
        order.append(room["id"])
        skip = completion_skip_reason(room, settings)
        if skip:
            records[room["id"]] = RoomCompletion(room, state="kept" if "keep" in skip else "skipped", reason=skip)
            continue
        partner = partner_of(room, settings)
        if partner is not None and partner[0] in rooms_by_id:
            pending.append((room, partner))
            continue
        records[room["id"]] = complete_room(room, building, out, style_text, client, settings, passes, family)
    notes: dict[str, str] = {}
    while pending:
        progress = False
        for item in list(pending):
            room, (pid, kind) = item
            prec = records.get(pid)
            if prec is None and any(r[0]["id"] == pid for r in pending):
                continue                                         # the partner is a copy itself: later
            pending.remove(item)
            progress = True
            if prec is not None and prec.state not in ("completed", "copied", "mirrored"):
                records[room["id"]] = RoomCompletion(room, state="kept", reason=(
                    f"partner {pid} ({kind}) not completed ({prec.reason}): kept as drawn so both stay the same"))
                continue
            t, why = (None, f"{pid} has no drawn furniture") if prec is None else \
                partner_transform(room, rooms_by_id[pid], kind, building)
            if t is None:
                notes[room["id"]] = f"partner {pid} ({kind}) not used: {why}; asked itself"
                rec = complete_room(room, building, out, style_text, client, settings, passes, family)
                rec.reason = (rec.reason + "; " if rec.reason else "") + notes[room["id"]]
                records[room["id"]] = rec
                continue
            records[room["id"]] = copy_room(room, prec, kind, t, building, out, settings)
        if not progress:                                         # a cycle of partners: ask the first one
            room, (pid, kind) = pending.pop(0)
            rec = complete_room(room, building, out, style_text, client, settings, passes, family)
            rec.reason = f"partner {pid} ({kind}) is itself waiting (a cycle): asked itself"
            records[room["id"]] = rec
    result = [records[rid] for rid in order]
    out["warnings"] = list(out.get("warnings", []))
    for rec in result:
        if rec.state == "completed" and rec.reason and not rec.added and not rec.changes and not rec.wall_cabinets:
            out["warnings"].append(f"{rec.room_id}: completion added nothing, {rec.reason}")
        for ch in rec.changes:
            if ch.get("type_proposal"):
                out["warnings"].append(f"{ch['id']}: unverified drawn piece, AI type proposal {ch['type']} "
                                       f"(was {ch['drawn_type']})")
        if debug_dir is not None:
            write_room_debug(rec, out, Path(debug_dir))
    return out, result


# --------------------------------------------------------------------------
# Outputs: completion.json, completion_report.md, debug PNG + JSON per room
# --------------------------------------------------------------------------

def summary(records: list[RoomCompletion], building: dict, settings: Settings, server: str, model: str,
            violations: list[str]) -> dict:
    applied = [c for r in records for c in r.changes if c["status"] == "applied"]
    return {"kind": "completion", "project": building["project"]["id"], "server": server, "model": model,
            "settings": settings.to_dict(),
            "rooms": [r.to_dict() for r in records],
            "rooms_completed": sum(r.state == "completed" for r in records),
            "rooms_copied": sum(r.state in ("copied", "mirrored") for r in records),
            "changes_applied": len(applied),
            "pieces_added": sum(len(r.added) for r in records),
            "wall_cabinets": sum(len(r.wall_cabinets) for r in records),
            "locked_violations": list(violations),
            "latency_s": round(sum(r.latency_s for r in records), 3)}


def _fmt_size(size) -> str:
    return " x ".join(f"{float(v):.2f}" for v in size)


def report(records: list[RoomCompletion], building: dict, settings: Settings, violations: list[str]) -> str:
    lines = [f"# AI completion of furnished rooms: {building['project']['id']}", "",
             f"Mode `furnished_rooms: {settings.mode}`, keep size {str(settings.keep_size).lower()}, twin rooms "
             f"`{settings.twin_rooms}`" + (f" (assumed: {', '.join(settings.assumed)})" if settings.assumed else "")
             + ". Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change "
             "needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed "
             "them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.", "",
             "| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |",
             "|---|---|---|---|---|---|---|---|"]
    for r in records:
        cells = []
        for k in (1, 2):
            p = next((x for x in r.passes if x["pass"] == k), None)
            if p is None:
                cells.append("-")
            elif p.get("data") is None:
                cells.append(f"error: {p['error']}"[:60] + f" ({p['latency_s']:.1f} s)")
            else:
                cells.append(f"{p['changes']}/{p['added']} ({p['latency_s']:.1f} s)")
        changed = sum(c["status"] == "applied" for c in r.changes)
        added = ", ".join(f"{f['type']} ({f['evidence'][0]['confidence']})" for f in r.added + r.wall_cabinets) or "-"
        lines.append(f"| {r.room['label']} ({r.room_id}) | {r.room.get('room_type')} | {r.state} | {cells[0]} | "
                     f"{cells[1]} | {changed} | {added} | {r.reason or '-'} |")
    changes = [(r, c) for r in records for c in r.changes]
    lines += ["", f"## Changes of drawn pieces ({len(changes)})", ""]
    if changes:
        lines += ["| Room | Piece | Drawn type / size | New type / size | Status | Reason |", "|---|---|---|---|---|---|"]
        for r, c in changes:
            drawn = f"{c.get('drawn_type', '-')} / {_fmt_size(c['drawn_size'])}" if c.get("drawn_size") else "-"
            new = f"{c['type']} / {_fmt_size(c['size'])}" if c.get("size") else c["type"]
            flags = [f for f in ("shrunk", "look_only", "type_proposal") if c.get(f)]
            status = c["status"] + (f" ({', '.join(flags)})" if flags else "")
            lines.append(f"| {r.room_id} | {c['id']} | {drawn} | {new} | {status} | {c.get('reason') or '-'} |")
    added = [(r, f) for r in records for f in r.added + r.wall_cabinets]
    lines += ["", f"## Added pieces ({len(added)})", ""]
    if added:
        lines += ["| Room | Piece | Type | Centre | Size | Method | Confidence | From |", "|---|---|---|---|---|---|---|---|"]
        for r, f in added:
            c = f["footprint"]["center"]
            lines.append(f"| {r.room_id} | {f['id']} | {f['type']} | [{c[0]:.2f}, {c[1]:.2f}] | "
                         f"{_fmt_size(f['footprint']['size'])} | {f.get('method')} | {f['evidence'][0]['confidence']} | "
                         f"{f.get('mirrored_from') or '-'} |")
    refused = [(r, x) for r in records for x in r.refused + r.dropped]
    if refused:
        lines += ["", f"## Refused and dropped proposals ({len(refused)})", ""]
        for r, x in refused:
            where = f" at {x['center']}" if x.get("center") is not None else ""
            lines.append(f"- {r.room_id}: pass {x.get('pass', '-')} {x['type']}{where}: {x['reason']}")
    notes = [(r, pid, fails) for r in records for pid, fails in (r.drawn_layout.get("pieces") or {}).items()]
    walks = [(r, w) for r in records for w in r.drawn_layout.get("walkways") or []]
    if notes or walks:
        lines += ["", "## drawn_layout (checks the drawn layout already fails; not counted against the AI)", ""]
        for r, pid, fails in notes:
            lines.append(f"- {r.room_id}: {pid} fails {', '.join(fails)} as drawn")
        for r, w in walks:
            lines.append(f"- {r.room_id}: walkway {w[1]} - {w[3]} broken as drawn")
    lines += ["", f"## Locked check: {'pass' if not violations else f'{len(violations)} violation(s)'}", ""]
    lines += [f"- {v}" for v in violations]
    return "\n".join(lines) + "\n"


def write_room_debug(rec: RoomCompletion, building: dict, debug_dir: Path) -> None:
    debug_dir.mkdir(parents=True, exist_ok=True)
    record = rec.to_dict()
    record["question"] = rec.question
    record["schema"] = rec.schema
    record["passes"] = [dict(p) for p in rec.passes]
    record["placements"] = {str(k): p.to_dict() for k, p in rec.placements.items()}
    (debug_dir / f"{rec.room_id}.json").write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        draw_room_png(rec, building, debug_dir / f"{rec.room_id}.png")
    except ImportError as exc:   # matplotlib missing: the JSON is the record, the PNG is a convenience
        print(f"complete: debug PNG for {rec.room_id} skipped ({exc})", file=sys.stderr)


COLOURS = {"drawn": "tab:green", "changed": "tab:blue", "added": "tab:orange"}


def draw_room_png(rec: RoomCompletion, building: dict, path: Path) -> None:
    """Drawn as drawn green, changed by AI blue (the drawn outline dashed under it, the anchor marked), added by AI
    orange (wall cabinets dotted), proposals for unverified pieces hatched."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon

    room = rec.room
    ctx = rec.context or placer.room_context(building, room)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    ax.add_patch(MplPolygon(list(ctx.polygon.exterior.coords), closed=True, fill=False, lw=2, color="black"))
    for door in ctx.doors:
        ax.add_patch(MplPolygon(list(door.zone.exterior.coords), closed=True, color="grey", alpha=0.2))
        if door.swing is not None and not door.swing.is_empty:
            ax.add_patch(MplPolygon(list(door.swing.exterior.coords), closed=True, color="grey", alpha=0.12))
    for win in ctx.windows:
        ax.add_patch(MplPolygon(list(win.band.exterior.coords), closed=True, color="tab:cyan", alpha=0.3))
    items = {f["id"]: f for f in building["furniture"] if f.get("room_id") == room["id"]}
    changed = {c["id"] for c in rec.changes if c["status"] == "applied"}
    proposals = {c["id"] for c in rec.changes if c.get("type_proposal")}
    for d in rec.drawn:
        f = items.get(d.id, d.item)
        poly = placer.drawn_piece(f).polygon()
        if d.id in changed:
            old = placer.drawn_piece(d.item).polygon()
            ax.add_patch(MplPolygon(list(old.exterior.coords), closed=True, fill=False, ls="--", color=COLOURS["drawn"]))
            ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, color=COLOURS["changed"], alpha=0.45,
                                    hatch="//" if d.id in proposals else None))
            ax.plot(*d.anchor["point"], "x", color="black", ms=8)
        else:
            ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, color=COLOURS["drawn"], alpha=0.45,
                                    hatch="//" if d.unverified else None))
        ax.text(poly.centroid.x, poly.centroid.y, f.get("type", ""), ha="center", va="center", fontsize=7)
    for f in rec.added + rec.wall_cabinets:
        poly = placer.drawn_piece(f).polygon()
        rule = f.get("method") == "rule"
        ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, color=COLOURS["added"],
                                alpha=0.25 if rule else 0.55, ls=":" if rule else "-", fill=True))
        ax.text(poly.centroid.x, poly.centroid.y, f["type"], ha="center", va="center", fontsize=7)
    for x in rec.dropped:
        if x.get("center") is not None:
            ax.text(x["center"][0], x["center"][1], f"x {x['type']}", color="tab:red", ha="center", fontsize=7)
    minx, miny, maxx, maxy = ctx.polygon.bounds
    ax.set_xlim(minx - 0.5, maxx + 0.5)
    ax.set_ylim(miny - 0.5, maxy + 0.5)
    ax.set_title(f"{room['label']} ({rec.room_id}) {rec.state}: green drawn, blue changed, orange added", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)
