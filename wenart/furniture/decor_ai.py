"""AI decor (docs/milestone9.md §4): a vision-language model decorates every furnished room, the rooms whose
furniture comes from the documents included; it chooses from checked places ("slots") and never moves, adds or
removes furniture.

Two steps, as the recognition questions and answers (docs/milestone7.md §1.4):

- ``ask`` (the VLM stage, inside the layout's Qwen session): per decorated room, the slots and the question are
  built from the building (deterministic), and the layout model answers twice (text only, temperature 0, pass 2 with
  another block order and seed, the room's own strict schema as the structured-output grammar). The answers are
  stored by key (room id, question hash, model) in ``decor_ai_answers.json``; a stored answer with the same key is
  never asked again.
- ``apply`` (the CPU decor stage): builds the same slots and questions, reads both answers, keeps an item only when
  both passes put the same type into the same slot (confidence 0.9; the colour both name, else pass 1's), checks it
  (it fits the slot's box, scaled down never up; wall items do not overlap on a wall; floor plants pass the placer
  checks with each other) and writes the building's ``decor`` list. A room where nothing survives (no answer, a
  failed or unparseable pass, nothing agreed, every item refused) gets the M8 rule decor (``decor.rule_decor_room``,
  ``method: rule``) and the report says why. Single-pass items are listed as ``not agreed``, never built.

Slots (``room_slots``), for verified, built pieces of a verified room (never a prayer room; the brief's ``decor:
false`` switches decor off, ``decor: rules`` keeps the M8 rules):

- ``top``: the free top of a coffee table, dining table, side table, nightstand (centre), a dresser or TV unit (left
  and right part), a desk (back left, back right): vases, bowls, small plants, table lamps, books; the box is that
  part of the top minus ``TOP_MARGIN_M``; the height is limited by the ceiling and, for a host within 0.3 m of a
  window, by the sill (the placer's window rule);
- ``soft``: cushions on a sofa back, a bed head, an armchair (``decor.host_decor`` positions);
- ``shelf``: books on a bookshelf (as M4);
- ``wall``: wall art above a sofa, a bed's headboard, a dresser or a desk, a mirror above a washbasin or a dresser
  (``decor.wall_art_for_host``: the wall behind the piece, never over an opening, inside the wall, under the ceiling);
- ``floor``: up to two free room corners for a plant (the M4 corner check);
- ``rug``: the M8 rug groups (``decor.rugs_for_room``).

Output items: the M8 decor fields plus ``method: ai``, ``slot``, ``colour``, ``confidence``, ``evidence`` (one entry
per pass: method ai, model, pass, confidence, the pass's reason) and ``status: verified``. Files: ``decor_ai.json``
(per room: slots, both passes, agreement, checks, fallback), ``decor_report.md``, one PNG + JSON per room in the
debug folder.

CLI::

    python -m wenart.furniture.decor_ai ask BUILDING --style STYLE --server URL --model MODEL --answers FILE
    python -m wenart.furniture.decor_ai apply BUILDING --style STYLE --answers FILE --out building_decor.json
        [--debug DIR]

Exit codes: 0 done; 2 usage error; 3 (ask) the server could not be reached for some call (answers of the other
calls are stored; ``apply`` then falls back to the rules for those rooms).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from wenart import building as B
from wenart import geometry as G
from wenart.blender import parametric as P
from wenart.furniture import decor as D
from wenart.furniture import placer
from wenart.recognition import vlm_client

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
DEFAULT_MAX_TOKENS = 1536
VERSION = "m9.1"                       # part of every answer key: bump when the question changes
CONFIDENCE_AGREED = 0.9
PASSES = (1, 2)
EVIDENCE_FILE = "building.json"
ANSWERS_KIND = "decor_ai_answers"
EXIT_OK, EXIT_USAGE, EXIT_SERVER = 0, 2, 3

# The decor types the AI chooses from (docs/milestone9.md §3; = decor.DECOR_TYPES).
AI_TYPES: tuple[str, ...] = D.DECOR_TYPES
SURFACE_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp", "book_set")
WALL_TYPES: tuple[str, ...] = ("wall_art", "mirror")

# Item box per surface type: default (w, d, h) and the smallest box it may be scaled down to (metres).
SURFACE_SIZES: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] = {
    "vase": ((0.18, 0.18, 0.40), (0.08, 0.08, 0.12)),
    "bowl": ((0.32, 0.32, 0.12), (0.15, 0.15, 0.04)),
    "plant_small": ((0.25, 0.25, 0.45), (0.10, 0.10, 0.15)),
    "table_lamp": ((0.35, 0.35, 0.60), (0.18, 0.18, 0.30)),
    "book_set": (tuple(D.BOOK_SIZE) + (0.22,), (0.18, 0.15, 0.10)),
}
TOP_MARGIN_M = 0.03
CENTRE_MAX = {"table_dining": (0.70, 0.50)}          # a centrepiece leaves the places free
CEILING_CLEAR_M = 0.10
# Host type -> (top parts, the types its top takes).
TOP_HOSTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "table_coffee": (("centre",), ("vase", "bowl", "plant_small", "book_set")),
    "table_dining": (("centre",), ("vase", "bowl", "plant_small")),
    "side_table": (("centre",), ("table_lamp", "vase", "plant_small", "book_set")),
    "nightstand": (("centre",), ("table_lamp", "vase", "plant_small", "book_set")),
    "dresser": (("left", "right"), ("table_lamp", "vase", "bowl", "plant_small", "book_set")),
    "tv_unit": (("left", "right"), ("vase", "bowl", "plant_small", "book_set")),
    "desk": (("back_left", "back_right"), ("table_lamp", "plant_small", "book_set", "vase")),
}
SOFT_HOSTS: tuple[str, ...] = ("sofa", "bed_double", "bed_single", "armchair")
SHELF_HOSTS: tuple[str, ...] = ("bookshelf",)
# Wall decor: host type -> the types its wall takes.
WALL_HOSTS: dict[str, tuple[str, ...]] = {
    "sofa": ("wall_art",), "bed_double": ("wall_art",), "bed_single": ("wall_art",),
    "dresser": ("wall_art", "mirror"), "desk": ("wall_art",), "washbasin": ("mirror",),
}
# Mirror geometry (decor.wall_art_for_host parameters).
MIRROR_WIDTH_SHARE = 0.9
MIRROR_MAX_W = 1.0
MIRROR_MIN_W = 0.35
MIRROR_GAP_M = 0.30                   # above a washbasin's top: room for the tap
FLOOR_CORNERS_MAX = 2
# Room type -> the decor types the AI may choose there (docs/milestone9.md §4).
ROOM_TYPES: dict[str, tuple[str, ...]] = {
    "living": AI_TYPES,
    "bedroom": AI_TYPES,
    "dining": AI_TYPES,
    "other": AI_TYPES,
    "kitchen": ("vase", "bowl", "plant_small", "book_set"),
    "hall": ("mirror", "wall_art", "plant", "vase", "bowl", "plant_small", "table_lamp", "book_set"),
    "bathroom": ("mirror",),
    "wc": ("mirror",),
}
FLOOR_PLANT_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom", "dining", "hall", "other")
ROOM_GUIDE: dict[str, str] = {
    "living": "cushions on the sofa, a rug under the sofa group, wall art above the sofa, a plant in a free corner, "
              "a vase, a bowl or books on the coffee table, a table lamp on a side table; 4 to 8 items",
    "bedroom": "cushions on the bed, a table lamp on a nightstand (a small plant or books on the other one), wall "
               "art above the headboard, a rug under the bed, a plant in a corner, a vase or books on a dresser or "
               "desk; 4 to 8 items",
    "dining": "a vase or a bowl in the middle of the table, a rug under the table, wall art or a mirror above a "
              "sideboard; 2 to 4 items",
    "kitchen": "a bowl or a vase on the table, a small plant; 1 to 3 items",
    "hall": "a mirror or wall art above a console, a vase or a small plant on it, a plant in a corner; 1 to 3 items",
    "bathroom": "a mirror above the washbasin; 1 item",
    "wc": "a mirror above the washbasin; 1 item",
    "other": "a few items that suit the room; 1 to 4 items",
}
# Accent colours the AI may name (linear RGB for the parametric decor, ``parametric.DECOR_COLOURS``; the library pick
# prefers a model whose name holds the colour word).
COLOURS: dict[str, tuple[float, float, float]] = P.DECOR_COLOURS
MAX_ITEMS = 12
SYSTEM_PROMPT = (
    "You are an interior stylist. You choose decor for one furnished room of a home and answer only with JSON that "
    "follows the given schema. You never move, add or remove furniture: you only fill the listed places (slots) with "
    "the decor types each slot allows."
)


class UsageError(ValueError):
    """A bad argument or input file (exit 2)."""


# --------------------------------------------------------------------------
# Slots
# --------------------------------------------------------------------------

@dataclass
class Slot:
    id: str
    kind: str                                   # top | soft | shelf | wall | floor | rug
    types: tuple[str, ...]                      # decor types the slot takes
    host_id: Optional[str] = None
    host_type: Optional[str] = None
    center: Optional[tuple[float, float]] = None
    rotation_deg: float = 0.0
    max_size: Optional[tuple[float, float, float]] = None   # top / shelf: the largest box (w, d, h)
    items: dict = field(default_factory=dict)  # wall / rug / soft: the precomputed item(s) per type
    note: str = ""

    def to_prompt(self) -> dict:
        out = {"slot": self.id, "where": self.where(), "types": list(self.types)}
        if self.max_size:
            out["max_size_m"] = [round(v, 2) for v in self.max_size]
        return out

    def where(self) -> str:
        host = f"{self.host_type} {self.host_id}" if self.host_id else ""
        return {"top": f"on the top of {host}", "soft": f"on {host}", "shelf": f"on the shelves of {host}",
                "wall": f"on the wall above {host}", "floor": "on the floor in a free corner of the room",
                "rug": f"on the floor under {self.note}"}.get(self.kind, self.kind) + \
            (f" ({self.note})" if self.note and self.kind in ("top", "floor") else "")

    def to_dict(self) -> dict:
        out = {"id": self.id, "kind": self.kind, "types": list(self.types), "host_id": self.host_id,
               "host_type": self.host_type, "note": self.note}
        if self.center is not None:
            out["center"] = [round(self.center[0], 3), round(self.center[1], 3)]
        if self.max_size is not None:
            out["max_size"] = [round(v, 3) for v in self.max_size]
        return out


def usable_host(piece: dict) -> bool:
    """A piece decor may use: verified (type and place trusted) and built (``decor._usable_anchor``)."""
    return D._usable_anchor(piece)


def _host_top(piece: dict) -> float:
    return float(D.placer_bbox_height(piece))


def _ceiling(building: dict, room: dict) -> float:
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == room["level_id"]), {})
    return float(level.get("ceiling_height") or 2.7)


def _window_limit(piece: dict, ctx: placer.RoomContext) -> Optional[float]:
    """The lowest sill of a window whose 0.3 m band the piece touches (None: no window near)."""
    poly = placer.piece_from_furniture(piece).polygon()
    sills = [w.sill for w in ctx.windows if poly.intersection(w.band).area > placer.AREA_EPS]
    return min(sills) if sills else None


def _top_parts(host: dict) -> list[tuple[str, tuple[float, float], tuple[float, float]]]:
    """``(part, local centre, (w, d))`` of the top parts of a host (TOP_HOSTS), in the host frame."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    m = TOP_MARGIN_M
    parts = TOP_HOSTS[host["type"]][0]
    out = []
    for part in parts:
        if part == "centre":
            cw, cd = CENTRE_MAX.get(host["type"], (w, d))
            out.append((part, (0.0, 0.0), (min(w - 2 * m, cw), min(d - 2 * m, cd))))
        elif part in ("left", "right"):
            sign = -1.0 if part == "left" else 1.0
            out.append((part, (sign * w / 4.0, 0.0), (w / 2.0 - 2 * m, d - 2 * m)))
        else:                                     # back_left / back_right of a desk (its back at local +Y)
            sw, sd = min(0.40, w / 3.0), min(0.35, d / 2.0)
            sign = -1.0 if part == "back_left" else 1.0
            out.append((part, (sign * (w / 2.0 - sw / 2.0 - m), d / 2.0 - sd / 2.0 - m), (sw - m, sd - m)))
    return out


def room_slots(room: dict, pieces: list[dict], building: dict) -> tuple[list[Slot], list[str]]:
    """The slots of one room (module docstring) and the notes of the slots left out."""
    rtype = room.get("room_type") or "other"
    allowed = set(ROOM_TYPES.get(rtype, ROOM_TYPES["other"]))
    slots: list[Slot] = []
    notes: list[str] = []
    if rtype in D.NO_DECOR_ROOM_TYPES or room.get("status") != "verified":
        return slots, notes
    ctx = placer.room_context(building, room)
    ceiling = _ceiling(building, room)
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == room["level_id"]), {})
    hosts = sorted((p for p in pieces if usable_host(p)), key=lambda p: p["id"])
    for host in hosts:
        htype = host["type"]
        if htype in TOP_HOSTS:
            top = _host_top(host)
            sill = _window_limit(host, ctx)
            max_h = ceiling - CEILING_CLEAR_M - top
            if sill is not None:
                max_h = min(max_h, sill - top)
            for part, local, (pw, pd) in _top_parts(host):
                types = tuple(t for t in TOP_HOSTS[htype][1] if t in allowed and _fits_min(t, pw, pd, max_h))
                if not types:
                    notes.append(f"{host['id']} {part}: no decor fits ({pw:.2f} x {pd:.2f} m, "
                                 f"{max(0.0, max_h):.2f} m high" + (", under a window" if sill is not None else "")
                                 + ")")
                    continue
                center = tuple(D._local_to_building(host, local[0], local[1]))
                slots.append(Slot(f"{host['id']}.{part}", "top", types, host["id"], htype, center,
                                  float(host["footprint"]["rotation_deg"]), (pw, pd, max_h),
                                  note=f"{part.replace('_', ' ')} part" + (", under a window" if sill is not None
                                                                         else "")))
        if htype in SOFT_HOSTS and "cushion" in allowed:
            items = _cushions(host)
            if items:
                slots.append(Slot(f"{host['id']}.cushions", "soft", ("cushion",), host["id"], htype,
                                  items={"cushion": items}))
        if htype in SHELF_HOSTS and "book_set" in allowed:
            items = D.host_decor(host)
            if items:
                slots.append(Slot(f"{host['id']}.shelf", "shelf", ("book_set",), host["id"], htype,
                                  items={"book_set": items}))
        wall_types = tuple(t for t in WALL_HOSTS.get(htype, ()) if t in allowed)
        if wall_types:
            made, why = {}, []
            for dtype in wall_types:
                item, reason = _wall_item(host, ctx, building, level, dtype)
                if item is not None:
                    made[dtype] = item
                else:
                    why.append(f"{dtype}: {reason}")
            if made:
                slots.append(Slot(f"{host['id']}.wall", "wall", tuple(made), host["id"], htype, items=made))
            if why:
                notes.append(f"{host['id']} wall: " + "; ".join(why))
    if "rug" in allowed:
        rugs, rug_notes = D.rugs_for_room(room, pieces, building)
        for n, item in enumerate(rugs, start=1):
            what = " + ".join(item["anchor_ids"])
            slots.append(Slot(f"{room['id']}.rug{n}", "rug", ("rug",), item["anchor_ids"][0], None,
                              items={"rug": [item]}, note=what))
        notes += rug_notes
    if "plant" in allowed and rtype in FLOOR_PLANT_ROOM_TYPES:
        corners = free_corners(room, pieces, building, ctx)
        for n, center in enumerate(corners[:FLOOR_CORNERS_MAX], start=1):
            slots.append(Slot(f"{room['id']}.corner{n}", "floor", ("plant",), None, None, center,
                              note=f"corner at {center[0]:.2f}, {center[1]:.2f}"))
        if not corners:
            notes.append("no free corner for a floor plant")
    return slots, notes


def _fits_min(dtype: str, w: float, d: float, h: float) -> bool:
    lo = SURFACE_SIZES[dtype][1]
    return min(w, d) >= min(lo[0], lo[1]) - 1e-9 and h >= lo[2] - 1e-9


def _cushions(host: dict) -> list[dict]:
    """Cushion positions on a sofa back or a bed head (``decor.host_decor``), one on an armchair's back."""
    if host["type"] == "armchair":
        w, d = (float(v) for v in host["footprint"]["size"][:2])
        return [{"type": "cushion", "center": D._local_to_building(host, 0.0, d / 2.0 - D.CUSHION_SIZE[1] / 2.0 - 0.12),
                 "rotation_deg": host["footprint"]["rotation_deg"], "size": list(D.CUSHION_SIZE),
                 "reason": "cushion against the armchair back"}]
    return [i for i in D.host_decor(host) if i["type"] == "cushion"]


def _wall_item(host: dict, ctx: placer.RoomContext, building: dict, level: dict, dtype: str):
    if dtype == "mirror":
        return D.wall_art_for_host(host, ctx, building, level, dtype="mirror", width_share=MIRROR_WIDTH_SHARE,
                                   max_w=MIRROR_MAX_W, gap=MIRROR_GAP_M if host["type"] == "washbasin"
                                   else D.WALL_ART_GAP_M, min_w=MIRROR_MIN_W)
    return D.wall_art_for_host(host, ctx, building, level)


def free_corners(room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext,
                 others: tuple = ()) -> list[tuple[float, float]]:
    """Every convex room corner a floor plant may take (``decor.plant_position``'s checks), in boundary order;
    ``others``: plant centres placed before (obstacles)."""
    base = [placer.piece_from_furniture(f, i) for i, f in enumerate(pieces)]
    for c in others:
        base.append(placer.Piece("plant", tuple(c), 0.0, D.PLANT_SIZE, False, index=len(base)))
    out = []
    for center in D._corner_candidates(ctx):
        plant = placer.Piece("plant", center, 0.0, D.PLANT_SIZE, False, index=len(base))
        failed = placer.failed_checks(placer.check_piece(plant, base, ctx))
        if not failed and any(p.type in placer.schemas.CLEARANCE_TYPES
                              and plant.polygon().intersection(p.front_zone()).area > placer.AREA_EPS for p in base):
            failed = ["clearance of another piece"]
        if not failed and placer.walkway_failures(base + [plant], ctx):
            failed = ["walkway"]
        if not failed:
            out.append(center)
    return out


# --------------------------------------------------------------------------
# Question and schema
# --------------------------------------------------------------------------

def style_text_of(style: Optional[dict], building: dict) -> str:
    from wenart.furniture.layout import style_text_of as layout_style
    return layout_style(style, building)


def piece_line(p: dict) -> dict:
    fp = p["footprint"]
    return {"id": p["id"], "type": p["type"], "size_m": [round(float(fp["size"][0]), 2), round(float(fp["size"][1]), 2)],
            "from": "documents" if p.get("source") == "from_documents" else "added by AI"}


def question(room: dict, pieces: list[dict], slots: list[Slot], style_text: str, pass_no: int = 1) -> str:
    """The user prompt for one room; pass 2 reorders the blocks."""
    rtype = room.get("room_type") or "other"
    guide = ROOM_GUIDE.get(rtype, ROOM_GUIDE["other"])
    task = (f"Task: choose decor for the {rtype} labelled '{room['label']}' ({float(room.get('area_computed') or 0):.1f} "
            f"m²). Style brief: {style_text.strip() or 'none'}.")
    furniture = "Furniture in the room (fixed; never moved):\n" + json.dumps(
        [piece_line(p) for p in pieces], ensure_ascii=False)
    slot_block = "Places for decor (slots) and the decor types each takes:\n" + json.dumps(
        [s.to_prompt() for s in slots], ensure_ascii=False)
    rules = ("Rules: use only the listed slots and, for each, only one of its types; at most one item per slot; leave "
             "some slots empty so the room is not cluttered; choose colours that suit the style; pick the colour "
             f"from: {', '.join(COLOURS)}.")
    guide_block = f"A good set for this room type: {guide}."
    fields = ("Fields of the answer: items, a list (the most important first) of objects with slot (a slot id), type "
              "(one of the slot's types), colour (one of the colours) and reason (one short sentence).")
    end = "Answer only with JSON."
    blocks = ([task, furniture, slot_block, rules, guide_block, fields, end] if pass_no == 1
              else [task, guide_block, rules, slot_block, furniture, fields, end])
    return "\n\n".join(blocks)


def answer_schema(slots: list[Slot]) -> dict:
    """The strict schema of one room (enums of its slots, the decor types and the colours; xgrammar-safe: no
    uniqueItems, no if/then)."""
    types = sorted({t for s in slots for t in s.types}, key=AI_TYPES.index)
    return {
        "type": "object", "additionalProperties": False, "required": ["items"],
        "properties": {"items": {
            "type": "array", "maxItems": min(MAX_ITEMS, max(1, len(slots))),
            "items": {"type": "object", "additionalProperties": False,
                      "required": ["slot", "type", "colour", "reason"],
                      "properties": {"slot": {"enum": [s.id for s in slots]}, "type": {"enum": types},
                                     "colour": {"enum": list(COLOURS)},
                                     "reason": {"type": "string", "maxLength": 160}}}}},
    }


def schema_errors(data, schema: dict) -> list[str]:
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]


def answer_key(room_id: str, prompt: str, schema: dict, model: str, pass_no: int) -> str:
    text = json.dumps({"v": VERSION, "room": room_id, "prompt": prompt, "schema": schema, "model": model,
                       "pass": pass_no, "system": SYSTEM_PROMPT}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# The rooms to decorate and their questions (shared by ask and apply)
# --------------------------------------------------------------------------

def decor_mode(building: dict) -> str:
    """``ai`` (default), ``rules`` (``brief.decor: rules``) or ``off`` (``brief.decor: false``)."""
    brief = (building.get("project") or {}).get("brief") or {}
    value = brief.get("decor", True)
    if value is False or str(value).strip().lower() in ("false", "off", "none", "no"):
        return "off"
    if str(value).strip().lower() == "rules":
        return "rules"
    return "ai"


@dataclass
class RoomQuestion:
    room: dict
    pieces: list
    slots: list
    notes: list
    prompts: dict                    # pass -> prompt
    schema: dict


def room_questions(building: dict, style_text: str) -> list[RoomQuestion]:
    """Every room the AI decorates (furnished, verified, not a prayer room, with at least one slot)."""
    out = []
    for room, pieces in D.rooms_with_pieces(building):
        if not any(usable_host(p) for p in pieces):
            continue
        slots, notes = room_slots(room, pieces, building)
        if not slots:
            continue
        built = [p for p in pieces if p.get("build", True) is not False]
        prompts = {n: question(room, built, slots, style_text, n) for n in PASSES}
        out.append(RoomQuestion(room, pieces, slots, notes, prompts, answer_schema(slots)))
    return out


# --------------------------------------------------------------------------
# Ask (the VLM stage)
# --------------------------------------------------------------------------

def build_request(model: str, prompt: str, schema: dict, seed: int, max_tokens: int = DEFAULT_MAX_TOKENS) -> dict:
    return {"model": model, "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                         {"role": "user", "content": prompt}],
            "temperature": 0.0, "seed": seed, "max_tokens": max_tokens, "structured_outputs": {"json": schema},
            "chat_template_kwargs": {"enable_thinking": False}}


class DecorClient:
    """``ask(prompt, schema, pass_no) -> dict`` (``{"data", "raw_text", "error", "transport", "latency_s"}``)."""

    def __init__(self, base_url: str = DEFAULT_SERVER, model: Optional[str] = None, timeout_s: float = 300.0,
                 retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout_s = timeout_s
        self.retries = max(1, retries)

    @property
    def model(self) -> str:
        if self._model is None:
            models = vlm_client.served_models(self.base_url)
            if not models:
                raise vlm_client.VLMError(f"no model served at {self.base_url}")
            self._model = models[0]
        return self._model

    def ask(self, prompt: str, schema: dict, pass_no: int) -> dict:
        t0 = time.monotonic()
        try:
            model = self.model
        except vlm_client.VLMError as exc:
            return {"data": None, "raw_text": "", "error": str(exc), "transport": True, "latency_s": 0.0}
        body = build_request(model, prompt, schema, seed=pass_no)
        raw, error, data, transport = "", None, None, False
        for attempt in range(1, self.retries + 1):
            try:
                resp = vlm_client.post_json(self.base_url + "/chat/completions", body, self.timeout_s)
                raw = resp["choices"][0]["message"].get("content") or ""
                data = vlm_client.parse_answer(raw)
                error, transport = None, False
                break
            except vlm_client.VLMError as exc:
                error, transport = str(exc), True
                if attempt < self.retries:
                    time.sleep(min(30.0, 2.0 * attempt))
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
                error, transport = f"bad answer: {exc}", False
                break
        if data is not None:
            problems = schema_errors(data, schema)
            if problems:
                error, data = "schema: " + "; ".join(problems[:5]), None
        return {"data": data, "raw_text": raw, "error": error, "transport": transport,
                "latency_s": round(time.monotonic() - t0, 3)}


def read_answers(path: Path) -> dict:
    p = Path(path)
    if not p.is_file():
        return {"kind": ANSWERS_KIND, "version": VERSION, "answers": {}}
    doc = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("kind") != ANSWERS_KIND or not isinstance(doc.get("answers"), dict):
        raise UsageError(f"{p} is not a decor answers file")
    return doc


def ask(building: dict, style_text: str, client, answers_path: Path, model: str,
        log: Callable = print) -> tuple[dict, int]:
    """Ask both passes of every room question that has no stored answer of the same key; returns the answers
    document and the number of calls that could not reach the server."""
    doc = read_answers(answers_path)
    store = doc["answers"]
    failed = 0
    for q in room_questions(building, style_text):
        for n in PASSES:
            key = answer_key(q.room["id"], q.prompts[n], q.schema, model, n)
            old = store.get(key)
            if old and old.get("data") is not None:
                continue
            got = client.ask(q.prompts[n], q.schema, n)
            if got.get("transport"):
                failed += 1
                log(f"decor ask: {q.room['id']} pass {n}: server not reachable ({got.get('error')})")
                continue
            store[key] = {"room_id": q.room["id"], "pass": n, "model": model, "data": got.get("data"),
                          "error": got.get("error"), "raw_text": got.get("raw_text", ""),
                          "latency_s": got.get("latency_s")}
            items = len((got.get("data") or {}).get("items") or [])
            log(f"decor ask: {q.room['id']} pass {n}: {items} item(s)" + (f", error {got['error']}"
                                                                           if got.get("error") else ""))
    doc.update(kind=ANSWERS_KIND, version=VERSION, model=model,
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    Path(answers_path).parent.mkdir(parents=True, exist_ok=True)
    Path(answers_path).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return doc, failed


# --------------------------------------------------------------------------
# Apply (the CPU decor stage)
# --------------------------------------------------------------------------

@dataclass
class RoomDecor:
    room_id: str
    label: str
    room_type: str
    slots: list = field(default_factory=list)
    passes: dict = field(default_factory=dict)          # pass -> {"items", "error"}
    agreed: list = field(default_factory=list)          # {"slot", "type", "colour", "reasons"}
    not_agreed: list = field(default_factory=list)
    rejected: list = field(default_factory=list)        # an item whose type its slot does not take
    refused: list = field(default_factory=list)         # agreed items the checks refused
    items: list = field(default_factory=list)           # building decor items (ai or rule)
    fallback: Optional[str] = None                      # why the rule decor was used
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"room_id": self.room_id, "label": self.label, "room_type": self.room_type,
                "slots": [s.to_dict() for s in self.slots], "passes": self.passes, "agreed": self.agreed,
                "not_agreed": self.not_agreed, "rejected": self.rejected, "refused": self.refused,
                "items": [{"id": i["id"], "type": i["type"], "method": i.get("method"), "slot": i.get("slot")}
                          for i in self.items],
                "fallback": self.fallback, "notes": self.notes}


def pass_items(answer: Optional[dict], slots: list[Slot]) -> tuple[list[dict], list[dict], Optional[str]]:
    """``(items, rejected, error)`` of one stored answer: one item per slot (the first), types the slot takes."""
    if not answer:
        return [], [], "not asked"
    if answer.get("data") is None:
        return [], [], answer.get("error") or "no answer"
    by_id = {s.id: s for s in slots}
    seen, items, rejected = set(), [], []
    for it in answer["data"].get("items") or []:
        slot = by_id.get(it.get("slot"))
        if slot is None or it.get("type") not in slot.types:
            rejected.append(dict(it, why="the slot does not take this type" if slot else "unknown slot"))
            continue
        if it["slot"] in seen:
            rejected.append(dict(it, why="a second item for the same slot"))
            continue
        seen.add(it["slot"])
        items.append(it)
    return items, rejected, None


def agree(a: list[dict], b: list[dict]) -> tuple[list[dict], list[dict]]:
    """Items both passes put into the same slot with the same type (pass 1 order); the others."""
    second = {(i["slot"], i["type"]): i for i in b}
    agreed, other = [], []
    for i in a:
        j = second.get((i["slot"], i["type"]))
        if j is None:
            other.append(dict(i, passes=[1]))
            continue
        colour = i.get("colour") if i.get("colour") == j.get("colour") else i.get("colour")
        agreed.append({"slot": i["slot"], "type": i["type"], "colour": colour,
                       "colour_agreed": i.get("colour") == j.get("colour"),
                       "reasons": [str(i.get("reason") or ""), str(j.get("reason") or "")]})
    firsts = {(i["slot"], i["type"]) for i in a}
    other += [dict(j, passes=[2]) for j in b if (j["slot"], j["type"]) not in firsts]
    return agreed, other


def _evidence(model: str, reasons: list[str]) -> list[dict]:
    return [B.evidence(EVIDENCE_FILE, "ai", CONFIDENCE_AGREED, model=model, pass_=n, text=reasons[n - 1] or None)
            for n in PASSES]


def _surface_item(slot: Slot, dtype: str) -> tuple[Optional[dict], str]:
    """The item box of a top slot: the type's default box, scaled down (never up) to the slot's box."""
    default, lowest = SURFACE_SIZES[dtype]
    mw, md, mh = slot.max_size
    s = min(1.0, mw / default[0], md / default[1], mh / default[2] if default[2] else 1.0)
    w, d, h = default[0] * s, default[1] * s, default[2] * s
    if w < lowest[0] - 1e-9 or d < lowest[1] - 1e-9 or h < lowest[2] - 1e-9:
        return None, f"the slot leaves {mw:.2f} x {md:.2f} x {mh:.2f} m, below the smallest {dtype} box"
    return {"center": [round(slot.center[0], 3), round(slot.center[1], 3)], "rotation_deg": round(slot.rotation_deg, 3),
            "size": [round(w, 3), round(d, 3), round(h, 3)]}, "ok"


def _wall_span(item: dict) -> tuple[tuple[float, float], float, float]:
    """``(wall point, rotation, half width)`` of a wall item, for the overlap check."""
    return tuple(item["wall_point"]), float(item["rotation_deg"]), float(item["size"][0]) / 2.0


def _wall_overlap(item: dict, placed: list[dict]) -> Optional[str]:
    (px, py), rot, half = _wall_span(item)
    for other in placed:
        (ox, oy), orot, ohalf = _wall_span(other)
        if abs(G.normalise_angle(rot - orot)) > 1.0 and abs(G.normalise_angle(rot - orot) - 360.0) > 1.0:
            continue                                        # another wall
        ux, uy = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        along = (ox - px) * ux + (oy - py) * uy
        across = abs(-(ox - px) * uy + (oy - py) * ux)
        if across < 0.05 and abs(along) < half + ohalf + 0.05:
            return f"overlaps {other['type']} {other['id']} on the same wall"
    return None


def build_items(rq: RoomQuestion, agreed: list[dict], model: str, building: dict, new_id) -> tuple[list[dict],
                                                                                                    list[dict]]:
    """The building decor items of the agreed choices, after the checks; ``(items, refused)``."""
    by_id = {s.id: s for s in rq.slots}
    room = rq.room
    items, refused, walls, plants = [], [], [], []
    ctx = None

    def base(dtype: str, choice: dict, slot: Slot) -> dict:
        return {"kind": "decor", "type": dtype, "level_id": room["level_id"], "room_id": room["id"], "asset": None,
                "source": "added_by_ai", "method": "ai", "slot": slot.id, "colour": choice.get("colour"),
                "confidence": CONFIDENCE_AGREED, "status": "verified", "evidence": _evidence(model, choice["reasons"]),
                "reason": choice["reasons"][0] or f"{dtype} chosen by both passes"}

    for choice in agreed:
        slot, dtype = by_id[choice["slot"]], choice["type"]
        if slot.kind == "top":
            box, why = _surface_item(slot, dtype)
            if box is None:
                refused.append(dict(choice, why=why))
                continue
            items.append(dict(base(dtype, choice, slot), id=new_id(room["level_id"]), host_id=slot.host_id, **box))
        elif slot.kind in ("soft", "shelf"):
            for it in slot.items[dtype]:
                items.append(dict(base(dtype, choice, slot), id=new_id(room["level_id"]), host_id=slot.host_id,
                                  center=it["center"], rotation_deg=it["rotation_deg"], size=it["size"]))
        elif slot.kind == "wall":
            it = slot.items[dtype]
            clash = _wall_overlap(dict(it, id="?"), walls)
            if clash:
                refused.append(dict(choice, why=clash))
                continue
            item = dict(base(dtype, choice, slot), id=new_id(room["level_id"]), host_id=None,
                        **{k: v for k, v in it.items() if k not in ("type", "reason")})
            walls.append(item)
            items.append(item)
        elif slot.kind == "rug":
            it = slot.items["rug"][0]
            items.append(dict(base("rug", choice, slot), id=new_id(room["level_id"]), host_id=None,
                              **{k: v for k, v in it.items() if k not in ("type", "reason")}))
        elif slot.kind == "floor":
            if ctx is None:
                ctx = placer.room_context(building, room)
            if plants and slot.center not in free_corners(room, rq.pieces, building, ctx, others=tuple(plants)):
                refused.append(dict(choice, why="the corner is no longer free next to the other plant"))
                continue
            plants.append(slot.center)
            items.append(dict(base("plant", choice, slot), id=new_id(room["level_id"]), host_id=None,
                              center=[round(slot.center[0], 3), round(slot.center[1], 3)], rotation_deg=0.0,
                              size=list(D.PLANT_SIZE)))
    return items, refused


def apply(building: dict, style_text: str, answers: dict, model: Optional[str] = None) -> tuple[dict, list[RoomDecor]]:
    """The decorated building (new dict) and the per-room records (module docstring)."""
    out = json.loads(json.dumps(building))
    out["decor"] = []
    records: list[RoomDecor] = []
    mode = decor_mode(out)
    counters: dict[str, int] = {}

    def new_id(level_id: str) -> str:
        counters[level_id] = counters.get(level_id, 0) + 1
        return f"dec_{level_id}_{counters[level_id]:03d}"

    if mode == "off":
        return out, records
    store = answers.get("answers") or {}
    model = model or answers.get("model") or "?"
    questions = {q.room["id"]: q for q in room_questions(out, style_text)} if mode == "ai" else {}
    for room, pieces in D.rooms_with_pieces(out):
        rec = RoomDecor(room["id"], room["label"], room.get("room_type") or "other")
        q = questions.get(room["id"])
        if q is None:
            # No AI question for this room (rules mode, no usable piece, no slot): the M8 rules as before.
            items, row = D.rule_decor_room(out, room, pieces, new_id)
            out["decor"].extend(items)
            if items or mode == "rules":
                rec.items, rec.fallback = items, ("brief.decor is 'rules'" if mode == "rules"
                                                  else "no slot for AI decor")
                rec.notes = [row.get("note")] if row.get("note") else []
                records.append(rec)
            continue
        rec.slots, rec.notes = q.slots, list(q.notes)
        per_pass = {}
        for n in PASSES:
            stored = store.get(answer_key(room["id"], q.prompts[n], q.schema, model, n))
            items, rejected, error = pass_items(stored, q.slots)
            per_pass[n] = items
            rec.passes[n] = {"items": items, "error": error, "latency_s": (stored or {}).get("latency_s")}
            rec.rejected += [dict(r, passes=[n]) for r in rejected]
        agreed, other = agree(per_pass[1], per_pass[2])
        rec.agreed, rec.not_agreed = agreed, other
        items, refused = build_items(q, agreed, model, out, new_id) if agreed else ([], [])
        rec.refused = refused
        if items:
            rec.items = items
            out["decor"].extend(items)
        else:
            errors = [f"pass {n}: {rec.passes[n]['error']}" for n in PASSES if rec.passes[n]["error"]]
            why = ("; ".join(errors) if errors else "the two passes agreed on no item" if not agreed
                   else "every agreed item was refused by the checks")
            fallback, row = D.rule_decor_room(out, room, pieces, new_id)
            rec.items, rec.fallback = fallback, why
            out["decor"].extend(fallback)
        records.append(rec)
    return out, records


# --------------------------------------------------------------------------
# Report and debug output
# --------------------------------------------------------------------------

def summary(records: list[RoomDecor], building: dict, model: Optional[str]) -> dict:
    ai = sum(1 for r in records for i in r.items if i.get("method") == "ai")
    rule = sum(1 for r in records for i in r.items if i.get("method") == "rule")
    return {"project": building["project"]["id"], "model": model, "rooms": [r.to_dict() for r in records],
            "items_ai": ai, "items_rule": rule,
            "rooms_ai": sum(1 for r in records if any(i.get("method") == "ai" for i in r.items)),
            "rooms_fallback": sum(1 for r in records if r.fallback)}


def report(records: list[RoomDecor], building: dict, model: Optional[str]) -> str:
    s = summary(records, building, model)
    lines = [f"# Decor: {building['project']['id']}", "",
             f"AI decor (docs/milestone9.md §4): {s['items_ai']} items chosen by the AI (model {model or '-'}, both "
             f"passes agreeing, confidence {CONFIDENCE_AGREED}) in {s['rooms_ai']} rooms; {s['items_rule']} items by "
             f"the rules (M4/M8) in {s['rooms_fallback']} rooms where the AI decor did not apply (reason per room). "
             "Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.",
             "", "| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |",
             "|---|---|---|---|---|---|---|---|"]
    for r in records:
        p1 = len(r.passes.get(1, {}).get("items") or []) if r.passes else "-"
        p2 = len(r.passes.get(2, {}).get("items") or []) if r.passes else "-"
        built = ", ".join(sorted(f"{i['type']}" for i in r.items)) or "-"
        refused = "; ".join(f"{x['type']} ({x['why']})" for x in r.refused) or "-"
        lines.append(f"| {r.label} ({r.room_id}) | {r.room_type} | {len(r.slots)} | {p1} / {p2} | {len(r.agreed)} | "
                     f"{built} | {refused} | {r.fallback or '-'} |")
    disagreements = [(r, x) for r in records for x in r.not_agreed]
    if disagreements:
        lines += ["", "Items only one pass chose (not built):", ""]
        lines += [f"- {r.room_id}: {x['type']} in {x['slot']} (pass {x['passes'][0]})" for r, x in disagreements]
    notes = [(r, n) for r in records for n in r.notes if n]
    if notes:
        lines += ["", "Places left out:", ""] + [f"- {r.room_id}: {n}" for r, n in notes]
    return "\n".join(lines) + "\n"


def write_room_debug(rec: RoomDecor, building: dict, debug_dir: Path) -> None:
    debug_dir = Path(debug_dir)
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / f"{rec.room_id}.json").write_text(json.dumps(rec.to_dict(), ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    try:
        draw_room_png(rec, building, debug_dir / f"{rec.room_id}.png")
    except ImportError as exc:                    # matplotlib missing: the JSON is the record
        print(f"decor: debug PNG for {rec.room_id} skipped ({exc})", file=sys.stderr)


KIND_COLOURS = {"top": "tab:blue", "soft": "tab:purple", "shelf": "tab:brown", "wall": "tab:orange",
                "floor": "tab:green", "rug": "tab:olive"}


def draw_room_png(rec: RoomDecor, building: dict, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPolygon

    room = next(r for r in building["rooms"] if r["id"] == rec.room_id)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    ax.add_patch(MplPolygon(room["polygon"], closed=True, fill=False, lw=2, color="black"))
    for f in building["furniture"]:
        if f.get("room_id") != rec.room_id:
            continue
        poly = placer.piece_from_furniture(f).polygon()
        doc = f.get("source") == "from_documents"
        ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, color="0.55" if doc else "0.8", alpha=0.6))
        ax.text(*poly.centroid.coords[0], f["type"], ha="center", va="center", fontsize=6)
    for s in rec.slots:
        c = s.center or (s.items.get("wall_art") or s.items.get("mirror") or {}).get("center")
        if c is None and s.items:
            first = next(iter(s.items.values()))
            c = (first[0] if isinstance(first, list) else first).get("center")
        if c is not None:
            ax.plot(c[0], c[1], "o", ms=5, mfc="none", color=KIND_COLOURS.get(s.kind, "k"))
    for i in rec.items:
        c = i["center"]
        colour = "tab:green" if i.get("method") == "ai" else "tab:gray"
        if i["type"] == "rug":
            poly = placer.Piece("rug", tuple(c), i["rotation_deg"], tuple(i["size"][:2]), False).polygon()
            ax.add_patch(MplPolygon(list(poly.exterior.coords), closed=True, fill=False, ls="--", color=colour))
        ax.plot(c[0], c[1], "s", ms=6, color=colour)
        ax.text(c[0], c[1] + 0.08, i["type"], fontsize=6, color=colour, ha="center")
    for x in rec.refused + rec.not_agreed:
        slot = next((s for s in rec.slots if s.id == x.get("slot")), None)
        if slot is not None and slot.center is not None:
            ax.plot(slot.center[0], slot.center[1], "x", ms=8, color="tab:red")
    xs, ys = [p[0] for p in room["polygon"]], [p[1] for p in room["polygon"]]
    minx, miny, maxx, maxy = min(xs), min(ys), max(xs), max(ys)
    ax.set_xlim(minx - 0.4, maxx + 0.4)
    ax.set_ylim(miny - 0.4, maxy + 0.4)
    title = f"{rec.label} ({rec.room_id}): {sum(1 for i in rec.items if i.get('method') == 'ai')} AI items"
    if rec.fallback:
        title += f"; rules: {rec.fallback}"[:90]
    ax.set_title(title, fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _style_text(args, building: dict) -> str:
    style = json.loads(Path(args.style).read_text(encoding="utf-8")) if args.style else None
    return style_text_of(style, building)


def main(argv: Optional[list[str]] = None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.furniture.decor_ai",
                                     description="AI decor of the furnished rooms (docs/milestone9.md §4)")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("ask", help="ask the layout model (two passes per room) and store the answers")
    a.add_argument("building")
    a.add_argument("--style")
    a.add_argument("--server", default=DEFAULT_SERVER)
    a.add_argument("--model", default=None)
    a.add_argument("--answers", required=True)
    a.add_argument("--timeout", type=float, default=300.0)
    p = sub.add_parser("apply", help="agreement, checks and the building's decor list (rule fallback per room)")
    p.add_argument("building")
    p.add_argument("--style")
    p.add_argument("--answers", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--debug")
    p.add_argument("--report")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    try:
        building = B.load(args.building)
        style_text = _style_text(args, building)
        if args.command == "ask":
            if decor_mode(building) != "ai":
                print(f"decor ask: brief decor mode {decor_mode(building)!r}: nothing to ask")
                read_answers(Path(args.answers))
                return EXIT_OK
            client = (client_factory or (lambda: DecorClient(args.server, args.model, timeout_s=args.timeout)))()
            try:
                model = args.model or client.model
            except vlm_client.VLMError as exc:
                print(f"decor ask: server not reachable: {exc}", file=sys.stderr)
                return EXIT_SERVER
            doc, failed = ask(building, style_text, client, Path(args.answers), model)
            print(f"decor ask: {len(doc['answers'])} stored answer(s) -> {args.answers}")
            return EXIT_SERVER if failed else EXIT_OK
        answers = read_answers(Path(args.answers))
        out, records = apply(building, style_text, answers)
        out_path = Path(args.out)
        B.save(out, out_path)
        model = answers.get("model")
        (out_path.parent / "decor_ai.json").write_text(json.dumps(summary(records, out, model), ensure_ascii=False,
                                                                   indent=1), encoding="utf-8")
        rep = Path(args.report) if args.report else out_path.parent / "decor_report.md"
        rep.write_text(report(records, out, model), encoding="utf-8")
        if args.debug:
            for rec in records:
                write_room_debug(rec, out, Path(args.debug))
        s = summary(records, out, model)
        print(f"decor apply: {s['items_ai']} AI item(s) in {s['rooms_ai']} room(s), {s['items_rule']} rule item(s) "
              f"in {s['rooms_fallback']} room(s) -> {out_path}")
        return EXIT_OK
    except (UsageError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"decor: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
