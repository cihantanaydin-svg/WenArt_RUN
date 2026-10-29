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

Milestone 10 (docs/milestone10.md §4.6, §1.6b row 18; track F), question version ``m10.1``:

- New slot kinds ``window`` (one per window of the room: curtains for windows at least 0.9 m wide, a roller blind
  for every window; never over a door: ``window_items``) and ``ceiling`` (pendants and ceiling lights over a
  dining table, a coffee table, a bed, and at the room centre: ``ceiling_items``); throws on sofas, chaises,
  armchairs and beds (``soft``); cushions on corner sofas (along the L), chaises, ottomans and benches; the top
  slots of sideboards, console tables, shoe and display cabinets; wall clocks; floor corners for large plants,
  baskets and floor sculptures (``floor_items``); candles, trays, book stacks and small sculptures on tops.
- The brief decides what it names (``apply_brief_looks``): cushions, throws and rugs alternate the brief's colours,
  curtains and blinds take its curtain colour (the AI's colour kept as ``colour_ai``), large plants take its
  species and pots in turn, lamps and lights carry ``light_on`` in the interior evening mood.
- Partners: second twins (``render.twin_rooms: one``) and ``same_as`` rooms are not asked (``room_questions``);
  ``apply`` copies their partner's decor (``decor.copy_partner_decor``, ``mirrored_from``; a room whose partner
  takes a copy itself copies that copy), each room's record with its own copy notes.

Milestone 12 (docs/milestone12.md §4.7 D13, B7; track S): every item gets its ``host_frame`` (``decor.attach_host_frames``)
so it follows its host after the agent's edits (``decor.sync_to_hosts``); the planned x/y of a cushion or a pillow is
only a start, the scene builder finds the real back, headboard and mattress on the built mesh (``wenart.blender.rest``).
Throws are our own procedural cloth (``wenart.blender.textiles``: draped on the host, never a library object squashed
to 5 cm); a seat or bed whose model has its own cushions or bedding gets no cushion slot (``decor.takes_cushions``).

Fix round after P4a (17 Oct 2026; the rig track's ask, applied at integration): a ceiling slot hangs from the ceiling
over it (``ceiling_items`` with the building: ``decor.ceiling_over`` with the level's sloped attic ceiling), not from
the level's flat ceiling height. Under a slope a pendant keeps its bottom (a dining table's top + 0.75 m, elsewhere
at least 2.0 m) and gets the drop that is there; where that drop is under ``PENDANT_MIN_DROP_M`` only the flush
ceiling light is offered. P4a's real02 L1 had a flat 3.433 m ceiling height but 2.05-2.18 m of slope over the
pendant slots, and the builder lowered the shades through the dining table.

Fix round after P5 (22 Oct 2026; pod P5, real04; the verifier's better fix of the gpu_tests finding "decor ceiling
light hung under the low slope at eye height"). What: under a sloped ceiling a flush ceiling light whose bottom would
be lower than ``decor.MIN_LIGHT_BOTTOM_M`` (2.0 m, the Milestone 11 rule the builder already applied to a light
reaching over the slope) above the floor is not offered (``ceiling_items``; the room's slot notes say why, and a slot
left with no light is not made); it is left out, not moved (the highest ceiling of a low attic bathroom is still
under 2.0 m). Why: since the fix round after P4a the light hangs flush under the slope over its own footprint, which
the builder's guard did not check, and P5 hung ``dec_L1_011`` under the 1.27 m slope of the L1 bathroom at 1.155 m,
1.5 cm under the lens of ``cam_r_L1_banyo_1`` (56 % of the frame); ``dec_L1_009`` (hall, 1.716 m) and ``dec_L1_013``
(twin bathroom, 1.155 m) hung as low. Under the flat ceiling nothing changes, and the pendant rules stay (a dining
pendant keeps its bottom 0.75 m over the table, every other pendant at least ``PENDANT_MIN_BOTTOM_M``).

Fix round after P6a (22 Oct 2026; pod P6a, real04; the verifier's better fix of the look finding "curtains poke
through the mansard roof"). What: ``window_items`` reads each window as the build makes it (``decor.roof_clips``: a
window under the roof whose height is not drawn is clipped ``roof.OPENING_ROOF_GAP`` under the roof underside, as in
``build.prepare``) and takes the sill, the top and the blind's drop from that window. Under the slope the curtain rod
and the blind roller also stay ``decor.WINDOW_DECOR_CEILING_CLEAR_M`` (0.02 m, under the 0.05 m clip gap, so the rod
stays above the clipped glass) under the sloped ceiling over their own footprint (``decor.ceiling_over``); the item's
reason says so ("kept under the sloped ceiling, h m over it") and the room's notes list it. Under the slope a curtain
whose rod would come below the window top, or that would be 0.3 m tall or less, and a blind whose roller would come
below the window top are left out with a note. Under a flat ceiling nothing changes (the rod at most
``CEILING_CLEAR_M`` under the ceiling, as before). Why: P6a hung curtains 2.25 m high (rod 0.15 m above a window read
as drawn, 1.2 m tall) where the build clipped the window to 0.81 m (top 1.71 m) and the slope over the curtain is
1.83 m: dec_L1_005 / dec_L1_014 poked 0.4 m through the roof in ext_2, ext_3, ext_5 and ext_7, the two critical
findings left after the agent. The slots and the question are unchanged where the items still fit (the prompt names
the slot and its types, not the sizes), so stored answers stay valid.

28 Oct 2026 (user on real04 run 20261028-005318-full: "More decor pieces needed, plates on tables for example"; "I did
not like this bed"): after the AI's (or the rules') items every room's tops are dressed by rule
(``tabletop.dress_tops``: a place setting, a plate and a glass, at every chair of a dining table and a centre bowl;
a small group on coffee tables, sideboards, consoles, dressers, TV units, nightstands, side tables and desks; small
pieces on a bookshelf's boards), each clear of the others, ``method: rule`` with its reason; the AI never chooses
``plate`` or ``glass`` (``AI_TYPES``), so the questions and the stored answers are unchanged. A bed whose model has
its own made bedding gets no throw slot (``decor.takes_throw``).
28 Oct 2026 (user on real04 run 20261028-005318-full). "makes no sense to have that table with the carpet outside,
that's outside area": an open-air room (``outdoor.open_air_room``) is offered only the decor one puts outside
(``OUTDOOR_DECOR_TYPES``: no rug, curtain, blind, throw, wall art, mirror, clock, books, lamp or ceiling light) and
``apply`` takes out any rug, runner or carpet a rule laid on an outdoor floor (``outdoor.strip_outdoor_textiles``).
"More lights from the ceiling needed": after the AI's choice ``apply`` hangs every lit room's ceiling lights by the
lighting rule (``ceiling_lights.add_lights``: the zones' lights, a row of pendants along a long table, the lumen
method's general lights), before the twins copy their partner's decor (so they take the lights mirrored) and once more
for a twin whose copy lacks them; the slots and the question are unchanged, so stored answers stay valid.
29 Oct 2026 (user on real06 run 20261028-154514-full, lesson UL93: "Computer on the table would have been nice or a
laptop"): every desk and writing table gets its work set by rule before its top is styled (``tabletop.work_set``
through ``dress_tops``: an open laptop facing the seat, a monitor set in a home office), in every room type and in the
three ways a room is dressed (the AI's items, the rules, the fallback); the AI never chooses those types
(``AI_TYPES``), so the questions and the stored answers are unchanged. A top's heights come from ``top_room`` (the
ceiling and a window's sill apart; a top slot takes the smaller as before).
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
from wenart.furniture import placer, schemas
from wenart.furniture import tabletop as TT
from wenart.recognition import vlm_client

DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
DEFAULT_MAX_TOKENS = 1536
VERSION = "m10.1"                      # part of every answer key: bump when the question changes
CONFIDENCE_AGREED = 0.9
PASSES = (1, 2)
EVIDENCE_FILE = "building.json"
ANSWERS_KIND = "decor_ai_answers"
EXIT_OK, EXIT_USAGE, EXIT_SERVER = 0, 2, 3

# The decor types the AI chooses from (docs/milestone9.md §3; = decor.DECOR_TYPES).
# 28 Oct 2026: the rules set the tables; 29 Oct 2026: and the desks' work sets (the questions stay as they were)
AI_TYPES: tuple[str, ...] = tuple(t for t in D.DECOR_TYPES if t not in D.SETTING_TYPES + D.WORK_DECOR_TYPES
                                  + D.DETAIL_DECOR_TYPES)       # 29 Oct 2026: the details are the rules' (room_details)
SURFACE_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp", "book_set",
                                  "candle", "tray", "books", "sculpture")                      # Milestone 10
WALL_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock")

# Item box per surface type: default (w, d, h) and the smallest box it may be scaled down to (metres).
SURFACE_SIZES: dict[str, tuple[tuple[float, float, float], tuple[float, float, float]]] = {
    "vase": ((0.18, 0.18, 0.40), (0.08, 0.08, 0.12)),
    "bowl": ((0.32, 0.32, 0.12), (0.15, 0.15, 0.04)),
    "plant_small": ((0.25, 0.25, 0.45), (0.10, 0.10, 0.15)),
    "table_lamp": ((0.35, 0.35, 0.60), (0.18, 0.18, 0.30)),
    "book_set": (tuple(D.BOOK_SIZE) + (0.22,), (0.18, 0.15, 0.10)),
    # Milestone 10 (typical sizes, assumed)
    "candle": ((0.2, 0.15, 0.22), (0.08, 0.06, 0.08)),
    "tray": ((0.4, 0.28, 0.05), (0.2, 0.15, 0.02)),
    "books": ((0.25, 0.18, 0.12), (0.15, 0.11, 0.05)),
    "sculpture": ((0.2, 0.2, 0.35), (0.08, 0.08, 0.12)),
}
TOP_MARGIN_M = 0.03
CENTRE_MAX = {"table_dining": (0.70, 0.50)}          # a centrepiece leaves the places free
CEILING_CLEAR_M = 0.10
# Host type -> (top parts, the types its top takes).
TOP_HOSTS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "table_coffee": (("centre",), ("vase", "bowl", "plant_small", "book_set", "books", "candle", "tray", "sculpture")),
    "table_dining": (("centre",), ("vase", "bowl", "plant_small", "candle")),
    "side_table": (("centre",), ("table_lamp", "vase", "plant_small", "book_set", "books", "candle")),
    "nightstand": (("centre",), ("table_lamp", "vase", "plant_small", "book_set", "books", "candle")),
    "dresser": (("left", "right"), ("table_lamp", "vase", "bowl", "plant_small", "book_set", "books", "candle", "tray",
                                    "sculpture")),
    "tv_unit": (("left", "right"), ("vase", "bowl", "plant_small", "book_set", "books", "candle", "sculpture")),
    "desk": (("back_left", "back_right"), ("table_lamp", "plant_small", "book_set", "vase", "books")),
    # Milestone 10 (docs/milestone10.md §1.6b row 20): the new top hosts
    "sideboard": (("left", "right"), ("table_lamp", "vase", "bowl", "plant_small", "books", "candle", "tray",
                                      "sculpture")),
    "console_table": (("left", "right"), ("table_lamp", "vase", "bowl", "plant_small", "books", "candle", "tray",
                                          "sculpture")),
    "shoe_cabinet": (("centre",), ("vase", "bowl", "plant_small", "tray", "candle")),
    "display_cabinet": (("centre",), ("vase", "bowl", "sculpture")),
}
SOFT_HOSTS: tuple[str, ...] = ("sofa", "bed_double", "bed_single", "armchair",
                               "sofa_corner", "chaise", "ottoman", "bench")              # Milestone 10
SHELF_HOSTS: tuple[str, ...] = ("bookshelf",)
# Wall decor: host type -> the types its wall takes.
WALL_HOSTS: dict[str, tuple[str, ...]] = {
    "sofa": ("wall_art",), "bed_double": ("wall_art",), "bed_single": ("wall_art",),
    "dresser": ("wall_art", "mirror", "clock"), "desk": ("wall_art", "clock"), "washbasin": ("mirror",),
    # Milestone 10
    "sofa_corner": ("wall_art",), "sideboard": ("wall_art", "mirror", "clock"), "console_table": ("mirror", "wall_art"),
}
# Mirror geometry (decor.wall_art_for_host parameters).
MIRROR_WIDTH_SHARE = 0.9
MIRROR_MAX_W = 1.0
MIRROR_MIN_W = 0.35
MIRROR_GAP_M = 0.30                   # above a washbasin's top: room for the tap
# 28 Oct 2026 (user: "Mirrors in the baths is missing sometimes"; real06: two basins under a window left 0.00 m for the
# mirror above them, and an inferred basin was no decor host at all): every built basin gets a mirror, a required item
# (``required_items``), never only an option of the AI: above it, else on the nearest free wall stretch beside it
# (``basin_mirror``: within MIRROR_SIDE_REACH_M of the basin's edge, SIDE_MIRROR_W wide, slid along its free stretch
# towards the basin)
MIRROR_HOSTS: tuple[str, ...] = ("washbasin", "vanity")
MIRROR_SIDE_REACH_M = 1.2
SIDE_MIRROR_W = 0.6                    # a mirror beside a basin: a bathroom mirror's width
FLOOR_CORNERS_MAX = 2
FREE_WALL_ART_ROOM_TYPES = ("living", "bedroom", "dining", "hall", "child", "office")   # 27 Oct 2026: art on free walls
# Room type -> the decor types the AI may choose there (docs/milestone9.md §4).
ROOM_TYPES: dict[str, tuple[str, ...]] = {
    "living": AI_TYPES,
    "bedroom": AI_TYPES,
    "dining": AI_TYPES,
    "other": AI_TYPES,
    "kitchen": ("vase", "bowl", "plant_small", "book_set", "blind", "pendant_light", "ceiling_light", "candle", "tray",
                "plant", "plant_large"),                     # 27 Oct 2026 (UL42): a floor plant, as the photos show
    "hall": ("mirror", "wall_art", "plant", "vase", "bowl", "plant_small", "table_lamp", "book_set", "clock", "basket",
             "plant_large", "ceiling_light", "pendant_light", "books", "tray", "candle"),
    "bathroom": ("mirror", "blind", "ceiling_light", "candle", "basket", "plant", "plant_small"),   # 27 Oct: a plant
    "wc": ("mirror", "blind", "ceiling_light"),
}
# 28 Oct 2026 (user on real04's roof terrace r_L1_teras: "makes no sense to have that table with the carpet outside,
# that's outside area"; the room fell back to "other", every decor type, and the AI laid a wool runner under its table):
# an open-air room (``outdoor.open_air_room``) takes the decor one puts outside only: plants, a lantern (candle), a
# vase, a bowl or a tray on the table, cushions on the seats; never a rug, curtains, a blind, a throw, wall art, a
# mirror, a clock, books, a lamp or a ceiling light of an indoor room.
OUTDOOR_DECOR_TYPES: tuple[str, ...] = ("cushion", "plant", "plant_large", "plant_small", "vase", "bowl", "candle",
                                        "tray", "basket", "sculpture")
from wenart.blender import outdoor as OD  # noqa: E402

for _t in OD.OPEN_AIR_ROOMS:
    ROOM_TYPES[_t] = OUTDOOR_DECOR_TYPES
FLOOR_PLANT_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom", "dining", "hall", "other", "kitchen", "bathroom")
FLOOR_TYPES: tuple[str, ...] = ("plant", "plant_large", "basket", "sculpture")          # Milestone 10 floor corners
ROOM_GUIDE: dict[str, str] = {
    "living": "cushions on the sofa, a throw, a rug under the sofa group, wall art above the sofa, curtains or a "
              "blind at each window, a pendant or ceiling light, a large plant in a free corner, a vase, a tray, "
              "candles or books on the coffee table, a table lamp on a side table; 6 to 12 items",
    "bedroom": "cushions and a throw on the bed, a table lamp on a nightstand (a small plant or books on the other "
               "one), wall art above the headboard, a rug under the bed, curtains at the window, a ceiling light, a "
               "plant in a corner, a vase or books on a dresser or desk; 5 to 10 items",
    "dining": "a vase, a bowl or candles in the middle of the table, a pendant over the table, a rug under the "
              "table, curtains, wall art or a mirror above a sideboard; 3 to 6 items",
    "kitchen": "a bowl or a vase on the table, a small plant, a pendant or ceiling light, a blind; 1 to 4 items",
    "hall": "a mirror or wall art above a console, a vase or a small plant on it, a plant in a corner, a ceiling "
            "light; 1 to 4 items",
    "bathroom": "a mirror above the washbasin, a blind, a ceiling light; 1 to 3 items",
    "wc": "a mirror above the washbasin, a ceiling light; 1 to 2 items",
    "other": "a few items that suit the room; 1 to 5 items",
}
for _t in OD.OPEN_AIR_ROOMS:                # 28 Oct 2026: an outdoor room is dressed for outside
    ROOM_GUIDE[_t] = ("an outdoor room: a lantern or candles, a vase or a bowl on the table, cushions on the seats, "
                      "plants in pots; no rug, curtains or wall art outside; 1 to 4 items")
# Accent colours the AI may name (linear RGB for the parametric decor, ``parametric.DECOR_COLOURS``; the library pick
# prefers a model whose name holds the colour word).
COLOURS: dict[str, tuple[float, float, float]] = P.DECOR_COLOURS
MAX_ITEMS = 24
# 25 Oct 2026 (user: "there is not enough decor around"): the fewest items a styled room of each type holds; a room
# below it after the AI's choice is filled from its empty slots in ``FILL_ORDER`` (the code's own pick, method rule).
# 27 Oct 2026: these are a balanced room's numbers; a room's own minimum scales with its style's decor density
# (``room_minimum``: the recipe's measured density, else the family's; a japandi living room 6, a classic one 12).
ROOM_MIN: dict[str, int] = {"living": 9, "bedroom": 7, "dining": 4, "kitchen": 2, "hall": 2, "bathroom": 2, "wc": 1,
                            "other": 4}
FILL_ORDER: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("soft", ("cushion", "throw")), ("rug", ("rug",)), ("wall", ("wall_art", "mirror", "clock")),
    ("ceiling", ("pendant_light", "ceiling_light")), ("window", ("curtain", "blind")),
    ("top", ("table_lamp", "vase", "books", "plant_small", "bowl", "candle", "tray", "book_set", "sculpture")),
    ("floor", ("plant_large", "plant", "basket")), ("shelf", ("book_set",)))
# the part of a long top and the item a stylist puts there first
PART_PICK = {"left": ("table_lamp", "vase"), "middle": ("vase", "bowl", "sculpture", "plant_small"),
             "right": ("books", "plant_small", "candle", "tray"), "centre": ("vase", "plant_small", "bowl", "candle")}
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
    kind: str                                   # top | soft | shelf | wall | floor | rug | window | ceiling
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
                "rug": f"on the floor under {self.note}", "window": f"at {self.note}",
                "ceiling": f"hanging from the ceiling {self.note}"}.get(self.kind, self.kind) + \
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


def top_room(host: dict, room: dict, building: dict, ctx: Optional[placer.RoomContext] = None,
             planes=None) -> tuple[float, Optional[float]]:
    """``(under the ceiling, under a sill)``: the height over a host's top that its ceiling leaves (the attic slope
    over its footprint, ``CEILING_CLEAR_M`` kept) and, for a host in the 0.3 m band of a window, the height to that
    window's sill (None without one). ``room_slots`` takes the smaller as a top slot's height; 29 Oct 2026: the desk's
    work set reads them apart (``tabletop.work_set``)."""
    if ctx is None:
        ctx = placer.room_context(building, room)
    if planes is None:
        planes = D.ceiling_planes(building, room["level_id"])
    top = _host_top(host)
    here = _ceiling(building, room)
    if planes:
        fp = host["footprint"]
        here = min(here, D.ceiling_over(building, room["level_id"], fp["center"], fp["size"], float(fp["rotation_deg"]),
                                        planes=planes))
    sill = _window_limit(host, ctx)
    return here - CEILING_CLEAR_M - top, (sill - top if sill is not None else None)


# 25 Oct 2026 (user: "there is not enough decor around"): a long top is styled as a group (the rule of three:
# something tall, something low, something that joins them), a long coffee table on both sides.
VIGNETTE_MIN_W = {"sideboard": 1.2, "console_table": 1.1, "dresser": 1.2, "tv_unit": 1.4}
VIGNETTE_PARTS: dict[str, tuple[str, ...]] = {}


def _top_parts(host: dict) -> list[tuple[str, tuple[float, float], tuple[float, float]]]:
    """``(part, local centre, (w, d))`` of the top parts of a host (TOP_HOSTS), in the host frame; a long host
    (``VIGNETTE_MIN_W``) gets three parts (left, middle, right)."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    m = TOP_MARGIN_M
    parts = TOP_HOSTS[host["type"]][0]
    if w >= VIGNETTE_MIN_W.get(host["type"], math.inf):
        parts = VIGNETTE_PARTS.get(host["type"], ("left", "middle", "right"))
    out = []
    for part in parts:
        if part in ("left", "middle", "right") and len(parts) == 3:
            k = {"left": -1.0, "middle": 0.0, "right": 1.0}[part]
            out.append((part, (k * w / 3.0, 0.0), (w / 3.0 - 2 * m, d - 2 * m)))
        elif part == "centre":
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
    if OD.open_air_room(room):                  # 28 Oct 2026: a room open to the sky too, whatever its type
        allowed &= set(OUTDOOR_DECOR_TYPES)
    slots: list[Slot] = []
    notes: list[str] = []
    if not D.room_takes_decor(room):
        return slots, notes
    ctx = placer.room_context(building, room)
    ceiling = _ceiling(building, room)
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == room["level_id"]), {})
    hosts = sorted((p for p in pieces if usable_host(p)), key=lambda p: p["id"])
    # 28 Oct 2026: a built basin takes its mirror even when its type was inferred (``MIRROR_HOSTS``)
    basins = sorted((p for p in pieces if p.get("type") in MIRROR_HOSTS and p not in hosts and p.get("footprint")
                     and p.get("build", True) is not False), key=lambda p: p["id"])
    planes = D.ceiling_planes(building, room["level_id"])     # Milestone 11 (E2): the attic slope
    for host in hosts:
        htype = host["type"]
        if htype in TOP_HOSTS:
            max_h, under_sill = top_room(host, room, building, ctx, planes)
            sill = under_sill
            if under_sill is not None:
                max_h = min(max_h, under_sill)
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
        if htype in THROW_HOSTS and "throw" in allowed and D.takes_throw(host):   # 28 Oct 2026: not on made bedding
            item = throw_item(host)
            if item is not None:
                slots.append(Slot(f"{host['id']}.throw", "soft", ("throw",), host["id"], htype,
                                  items={"throw": [item]}))
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
            if htype in MIRROR_HOSTS and "mirror" in wall_types and "mirror" not in made:
                item, side_why = basin_mirror(host, room, pieces, building, ctx, level)
                if item is not None:
                    made["mirror"] = item
                    why = [w for w in why if not w.startswith("mirror:")]
                else:
                    why.append(f"mirror beside it: {side_why}")
            if made:
                slots.append(Slot(f"{host['id']}.wall", "wall", tuple(made), host["id"], htype, items=made))
            if why:
                notes.append(f"{host['id']} wall: " + "; ".join(why))
    for host in basins:
        if "mirror" not in allowed:
            break
        item, side_why = _wall_item(host, ctx, building, level, "mirror")
        if item is None:
            item, side_why = basin_mirror(host, room, pieces, building, ctx, level)
        if item is not None:
            slots.append(Slot(f"{host['id']}.wall", "wall", ("mirror",), host["id"], host["type"],
                              items={"mirror": item}, note="the mirror of a basin whose type was inferred"))
        else:
            notes.append(f"{host['id']} wall: mirror: {side_why}")
    # 27 Oct 2026 (run 160846): art on the free walls too, not only above a sofa, bed or dresser
    if "wall_art" in allowed and rtype in FREE_WALL_ART_ROOM_TYPES:
        for n, item in enumerate(D.free_wall_art(room, pieces, building, ctx, level), start=1):
            slots.append(Slot(f"{room['id']}.wall{n}", "wall", ("wall_art",), None, None, items={"wall_art": item},
                              note=f"free wall, {item['size'][0]:.2f} m wide picture"))
    if "rug" in allowed:
        rugs, rug_notes = D.rugs_for_room(room, pieces, building)
        for n, item in enumerate(rugs, start=1):
            what = " + ".join(item["anchor_ids"])
            slots.append(Slot(f"{room['id']}.rug{n}", "rug", ("rug",), item["anchor_ids"][0], None,
                              items={"rug": [item]}, note=what))
        notes += rug_notes
    if allowed & set(FLOOR_TYPES) and rtype in FLOOR_PLANT_ROOM_TYPES:
        corners = floor_items(room, pieces, building, ctx, allowed, ceiling)
        for sid, made in corners:
            first = next(iter(made.values()))
            center = tuple(first["center"])
            slots.append(Slot(sid, "floor", tuple(t for t in FLOOR_TYPES if t in made), None, None, center,
                              items=made, note=f"corner at {center[0]:.2f}, {center[1]:.2f}"))
        if not corners:
            notes.append("no free corner or wall place for a floor plant")
    if allowed & {"curtain", "blind"}:                          # Milestone 10: window dressings
        made_windows, why = window_items(room, pieces, building, ctx, ceiling, planes=planes)   # after P6a: slope
        notes += why
        for wid, made in made_windows:
            types = tuple(t for t in ("curtain", "blind") if t in made and t in allowed)
            if types:
                slots.append(Slot(f"window:{wid}", "window", types, None, None, items={t: made[t] for t in types},
                                  note=f"window {wid}"))
    if allowed & {"pendant_light", "ceiling_light"}:            # Milestone 10: lights hanging from the ceiling
        for sid, made in ceiling_items(room, pieces, ceiling, building=building, notes=notes):   # after P4a, P5
            types = tuple(t for t in ("pendant_light", "ceiling_light") if t in made and t in allowed)
            if types:
                host_id = sid.split("over_", 1)[1] if ":over_" in sid else None
                slots.append(Slot(sid, "ceiling", types, host_id, None, items={t: made[t] for t in types},
                                  note=sid.split(":", 1)[1].replace("_", " ")))
    return slots, notes


def _fits_min(dtype: str, w: float, d: float, h: float) -> bool:
    lo = SURFACE_SIZES[dtype][1]
    return min(w, d) >= min(lo[0], lo[1]) - 1e-9 and h >= lo[2] - 1e-9


def _cushions(host: dict) -> list[dict]:
    """Cushion positions on a sofa back or a bed head (``decor.host_decor``), one on an armchair's back;
    Milestone 10: the corner sofa, chaise, ottoman and bench (``soft_items_m10``). Milestone 12: none on a seat or a
    bed whose model already has its own cushions or bedding (``decor.takes_cushions``)."""
    if not D.takes_cushions(host):
        return []
    if host["type"] in ("sofa_corner", "chaise", "ottoman", "bench"):
        return soft_items_m10(host)
    if host["type"] == "armchair":
        w, d = (float(v) for v in host["footprint"]["size"][:2])
        return [{"type": "cushion", "center": D._local_to_building(host, 0.0, d / 2.0 - D.CUSHION_SIZE[1] / 2.0 - 0.12),
                 "rotation_deg": host["footprint"]["rotation_deg"], "size": list(D.CUSHION_SIZE),
                 "reason": "cushion against the armchair back"}]
    return [i for i in D.host_decor(host) if i["type"] == "cushion"]


def _wall_item(host: dict, ctx: placer.RoomContext, building: dict, level: dict, dtype: str):
    if dtype == "clock":                                          # Milestone 10: a wall clock above the piece
        return D.wall_art_for_host(host, ctx, building, level, dtype="clock", width_share=1.0, max_w=CLOCK_WIDTH[0],
                                   gap=CLOCK_GAP_M, min_w=CLOCK_WIDTH[1])
    if dtype == "mirror":
        return D.wall_art_for_host(host, ctx, building, level, dtype="mirror", width_share=MIRROR_WIDTH_SHARE,
                                   max_w=MIRROR_MAX_W, gap=MIRROR_GAP_M if host["type"] == "washbasin"
                                   else D.WALL_ART_GAP_M, min_w=MIRROR_MIN_W)
    return D.wall_art_for_host(host, ctx, building, level)


def basin_mirror(host: dict, room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext,
                 level: dict) -> tuple[Optional[dict], str]:
    """``(item, why)``: a mirror for a basin whose wall leaves no room above it (a window behind it): the free wall
    stretch nearest the basin (``decor.free_wall_art`` with ``dtype`` mirror), slid along it towards the basin, within
    ``MIRROR_SIDE_REACH_M`` of its edge, ``SIDE_MIRROR_W`` wide; (None, why) when no stretch is that close."""
    c = (float(host["footprint"]["center"][0]), float(host["footprint"]["center"][1]))
    half = max(float(v) for v in host["footprint"]["size"][:2]) / 2.0
    others = [p for p in pieces if p is not host]
    cands = D.free_wall_art(room, others, building, ctx, level, dtype="mirror", most=8)
    best = None
    for it in cands:
        # the free stretch the picture was centred on (``free_wall_art``: FREE_WALL_ART_SHARE of it); the mirror
        # slides along it towards the basin
        width = min(float(it["size"][0]), SIDE_MIRROR_W)
        stretch = float(it["size"][0]) / D.FREE_WALL_ART_SHARE
        r = math.radians(float(it["rotation_deg"]))
        u = (math.cos(r), math.sin(r))                    # along the wall (local +Y, out of the room, is its normal)
        wp = tuple(it.get("wall_point") or it["center"])
        s_b = (c[0] - wp[0]) * u[0] + (c[1] - wp[1]) * u[1]
        lim = max(0.0, stretch / 2.0 - width / 2.0)
        t = max(-lim, min(lim, s_b))
        moved = dict(it, center=[round(it["center"][0] + u[0] * t, 3), round(it["center"][1] + u[1] * t, 3)],
                     wall_point=[round(wp[0] + u[0] * t, 3), round(wp[1] + u[1] * t, 3)])
        d = G.distance(tuple(moved["wall_point"]), c) - half
        if d <= MIRROR_SIDE_REACH_M and (best is None or d < best[0]):
            best = (d, moved, width)
    if best is None:
        return None, f"no free wall within {MIRROR_SIDE_REACH_M:g} m of {host['id']}"
    _d, item, width = best
    item = dict(item)
    if width < MIRROR_MIN_W - 1e-9:
        return None, f"the free wall beside {host['id']} leaves {width:.2f} m (min {MIRROR_MIN_W} m)"
    item.update(type="mirror", size=[round(width, 3), item["size"][1]], anchor_ids=[host["id"]],
                reason=f"mirror on the wall beside the basin {host['id']} ({best[0]:.2f} m from its edge): the wall "
                       f"above it has a window")
    item.pop("free_wall", None)
    return item, "ok"


def required_items(rq: "RoomQuestion", items: list[dict], building: dict, new_id) -> list[dict]:
    """The items a room must have whatever the AI chose (pure; 28 Oct 2026): a mirror for every basin with a mirror
    slot (``MIRROR_HOSTS``) that has none yet, through the same checks as the AI's items (``build_items``);
    labelled ``method: rule`` with the reason."""
    taken = {i.get("slot") for i in items}
    mirrored = {a for i in items if i.get("type") == "mirror" for a in i.get("anchor_ids") or []}
    picks = [{"slot": s.id, "type": "mirror", "colour": None,
              "reasons": [f"every basin has a mirror (user: 'Mirrors in the baths is missing sometimes')"] * 2}
             for s in rq.slots if s.kind == "wall" and s.host_type in MIRROR_HOSTS and "mirror" in s.types
             and s.id not in taken and s.host_id not in mirrored]
    out = []
    for choice in picks:
        made, _refused = build_items(rq, [choice], "rule", building, new_id)
        for it in made:
            it.update(method="rule", confidence=0.8, reason=choice["reasons"][0])
        out += made
    return out


def free_corners(room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext,
                 others: tuple = (), size=D.PLANT_SIZE, inset: float = D.CORNER_INSET_M,
                 candidates: Optional[list] = None) -> list[tuple[float, float]]:
    """Every convex room corner a floor plant may take (``decor.plant_position``'s checks), in boundary order;
    ``others``: plant centres placed before (obstacles). Milestone 10: ``size`` and ``inset`` of a larger floor
    item (a large plant, a floor sculpture). Wall-hung pieces (``mount_bottom_m``) are no floor obstacles.
    ``candidates``: other places to check the same way (27 Oct 2026: ``wall_spots``)."""
    base = [placer.piece_from_furniture(f, i) for i, f in enumerate(pieces) if not schemas.off_floor(f)]
    for c in others:
        base.append(placer.Piece("plant", tuple(c), 0.0, D.PLANT_SIZE, False, index=len(base)))
    out = []
    # 27 Oct 2026 (run 160846: real06's salon had door-to-door walkways blocked by its furniture before any plant, so
    # every plant place failed "walkway"): a plant fails only for a walkway it blocks itself
    before = None
    for center in (D._corner_candidates(ctx, inset) if candidates is None else candidates):
        plant = placer.Piece("plant", center, 0.0, tuple(size), False, index=len(base))
        failed = placer.failed_checks(placer.check_piece(plant, base, ctx))
        if not failed and any(p.type in placer.schemas.CLEARANCE_TYPES
                              and plant.polygon().intersection(p.front_zone()).area > placer.AREA_EPS for p in base):
            failed = ["clearance of another piece"]
        if not failed:
            if before is None:
                before = set(placer.walkway_failures(base, ctx))
            if set(placer.walkway_failures(base + [plant], ctx)) - before:
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


def question(room: dict, pieces: list[dict], slots: list[Slot], style_text: str, pass_no: int = 1,
             recipe: Optional[dict] = None) -> str:
    """The user prompt for one room; pass 2 reorders the blocks. 27 Oct 2026 (UL42): with the room's ``recipe``
    (``wenart.style.recipe``: what good photos of its kind and style show) the guide is the recipe's text."""
    rtype = room.get("room_type") or "other"
    guide = ROOM_GUIDE.get(rtype, ROOM_GUIDE["other"])
    if recipe:
        from wenart.style import recipe as RC

        guide = RC.recipe_text(recipe) + " Choose these first, then what else suits the room"
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


def room_recipe(room: dict, recipes: Optional[dict]) -> Optional[dict]:
    """The recipe of a room's reference space (``recipes``: ``{space: recipe}`` of ``recipes.json``), else None."""
    if not recipes:
        return None
    from wenart.style import references as RF

    return recipes.get(RF.space_of(room.get("room_type"), room.get("room_subtype")) or "")


def room_questions(building: dict, style_text: str, skip: Optional[set] = None,
                   recipes: Optional[dict] = None) -> list[RoomQuestion]:
    """Every room the AI decorates (furnished, verified, not a prayer room, with at least one slot); Milestone 10:
    not the rooms that take their partner's decor (``decor.copy_targets``; ``skip`` when the caller has them).
    27 Oct 2026: ``recipes`` put each room's recipe in its question (``question``)."""
    if skip is None:
        skip = set(D.copy_targets(building)[0])
    out = []
    for room, pieces in D.rooms_with_pieces(building):
        if room["id"] in skip:
            continue
        if not any(usable_host(p) for p in pieces):
            continue
        slots, notes = room_slots(room, pieces, building)
        if not slots:
            continue
        built = [p for p in pieces if p.get("build", True) is not False]
        prompts = {n: question(room, built, slots, style_text, n, room_recipe(room, recipes)) for n in PASSES}
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
        log: Callable = print, recipes: Optional[dict] = None) -> tuple[dict, int]:
    """Ask both passes of every room question that has no stored answer of the same key; returns the answers
    document and the number of calls that could not reach the server."""
    doc = read_answers(answers_path)
    store = doc["answers"]
    failed = 0
    for q in room_questions(building, style_text, recipes=recipes):
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
            it = slot.items.get(dtype) or {"center": list(slot.center), "size": list(D.PLANT_SIZE)}
            centre = (float(it["center"][0]), float(it["center"][1]))
            inset = FLOOR_ITEM_INSET_M.get(dtype, D.CORNER_INSET_M)
            if plants and centre not in free_corners(room, rq.pieces, building, ctx, others=tuple(plants),
                                                     size=tuple(it["size"][:2]), inset=inset):
                refused.append(dict(choice, why="the corner is no longer free next to the other plant"))
                continue
            plants.append(centre)
            items.append(dict(base(dtype, choice, slot), id=new_id(room["level_id"]), host_id=None,
                              center=[round(centre[0], 3), round(centre[1], 3)], rotation_deg=0.0,
                              size=list(it["size"])))
        elif slot.kind in ("window", "ceiling"):                   # Milestone 10
            it = slot.items[dtype]
            extra = {"anchor_ids": [slot.host_id]} if slot.kind == "ceiling" and slot.host_id else {}
            item = dict(base(dtype, choice, slot), id=new_id(room["level_id"]), host_id=None, **extra,
                        **{k: v for k, v in it.items() if k not in ("type", "reason", "note")})
            if it.get("note"):                     # fix round after P6a: the code's change stays on the item
                item["reason"] = f"{item['reason']} ({it['note']})"
            items.append(item)
    return items, refused


def room_minimum(room: dict, recipe: Optional[dict] = None, family: Optional[str] = None) -> dict:
    """The fewest decor items of a styled room (pure; 27 Oct 2026): ``ROOM_MIN`` of its type scaled by its style's
    decor density (``density.decor_density``: the room's recipe when photos measured it, else the style family's;
    ``density.decor_minimum``: never under what the type needs to look lived in). ``{"min", "base", "density",
    "why"}``; ``apply`` keeps it per room in the building's ``decor_minimum`` (the architect's S3 checks it)."""
    from wenart.style import density as DN

    t = str(room.get("room_type") or "other")
    base = ROOM_MIN.get(t, ROOM_MIN["other"])
    level, why = DN.decor_density(recipe, family)
    return {"min": DN.decor_minimum(t, base, level), "base": base, "density": level, "why": why}


def fill_to_minimum(rq: "RoomQuestion", items: list[dict], building: dict, new_id, recipe: Optional[dict] = None,
                    family: Optional[str] = None) -> list[dict]:
    """The items that bring a room up to its minimum (pure; 25 Oct 2026; 27 Oct 2026: ``room_minimum`` of its recipe
    and style family, ``ROOM_MIN`` of its type for a balanced style): its slots no item took, in ``FILL_ORDER``
    (soft, rug, wall, ceiling, window, top, floor, shelf), each with the first type it allows of the order (a long
    top's part with ``PART_PICK``), through the same checks as the AI's items (``build_items``); labelled ``method:
    rule`` with the reason."""
    goal = room_minimum(rq.room, recipe, family)
    want = goal["min"]
    have = len(items)
    if have >= want:
        return []
    taken = {i.get("slot") for i in items}
    # the M8 rule items carry no slot: a kind they already dress (cushions, books, wall art, a rug, a plant, a light)
    # is not filled again
    noslot = {str(i.get("type")) for i in items if not i.get("slot")}
    kinds_done = {kind for kind, order in FILL_ORDER if noslot & set(order)}
    picks = []
    for kind, order in FILL_ORDER:
        if kind in kinds_done:
            continue
        for slot in rq.slots:
            if slot.kind != kind or slot.id in taken:
                continue
            part = slot.id.rsplit(".", 1)[-1] if kind == "top" else None
            prefs = PART_PICK.get(part, ()) + order
            dtype = next((t for t in prefs if t in slot.types), None)
            if dtype is None:
                continue
            why = (f"styling: the room held {have} item(s), a styled {rq.room.get('room_type') or 'room'} holds "
                   f"{want} or more ({goal['why']})")
            picks.append({"slot": slot.id, "type": dtype, "colour": None, "reasons": [why, why]})
    out = []
    for choice in picks:
        if have + len(out) >= want:
            break
        made, _refused = build_items(rq, [choice], "rule", building, new_id)
        for it in made:
            it.update(method="rule", confidence=0.6, reason=choice["reasons"][0])
        out += made
    return out


# 27 Oct 2026 (UL42): a recipe layer -> the slot kinds and decor types that make it (the first type a slot takes)
LAYER_SLOTS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "rug": (("rug", ("rug",)),),
    "curtains": (("window", ("curtain",)),),
    "blinds": (("window", ("blind",)),),
    "wall_art": (("wall", ("wall_art",)),),
    "mirror": (("wall", ("mirror",)),),
    "plants": (("floor", ("plant_large", "plant")), ("top", ("plant_small",))),
    "pendant_or_ceiling_light": (("ceiling", ("pendant_light", "ceiling_light")),),
    "table_lamps": (("top", ("table_lamp",)),),
    "cushions": (("soft", ("cushion",)),),
    "throw": (("soft", ("throw",)),),
    "styled_surfaces": (("top", ("vase", "bowl", "tray", "books", "candle", "sculpture", "plant_small")),),
    "styled_shelves": (("shelf", ("book_set",)),),
}
EVERY_SLOT_LAYERS = ("curtains", "rug", "cushions")     # every window, every rug place, every seat when a must
TYPE_LAYER: dict[str, str] = {"rug": "rug", "curtain": "curtains", "blind": "blinds", "wall_art": "wall_art",
                              "mirror": "mirror", "plant": "plants", "plant_large": "plants", "plant_small": "plants",
                              "pendant_light": "pendant_or_ceiling_light", "ceiling_light": "pendant_or_ceiling_light",
                              "table_lamp": "table_lamps", "cushion": "cushions", "throw": "throw",
                              "vase": "styled_surfaces", "bowl": "styled_surfaces", "tray": "styled_surfaces",
                              "books": "styled_surfaces", "candle": "styled_surfaces", "sculpture": "styled_surfaces",
                              "book_set": "styled_shelves"}


def layer_counts(items: list[dict]) -> dict[str, int]:
    """``{layer: count}`` of a room's decor items (``TYPE_LAYER``)."""
    out: dict[str, int] = {}
    for it in items:
        layer = TYPE_LAYER.get(str(it.get("type")))
        if layer:
            out[layer] = out.get(layer, 0) + 1
    return out


def fill_recipe(rq: "RoomQuestion", items: list[dict], building: dict, new_id,
                recipe: Optional[dict]) -> list[dict]:
    """27 Oct 2026 (lesson UL42; real06's salon held 9 items and no rug, plant, art or lamp, its bathrooms a ceiling
    light): the items that bring a room to its recipe's ``must`` layers (``recipe.gaps``): for each missing layer the
    free slots of its kind (``LAYER_SLOTS``) in turn, each with the first type of the layer the slot takes, up to the
    recipe's count (every free slot for ``EVERY_SLOT_LAYERS``), through the same checks as the AI's items
    (``build_items``); ``method: rule`` with the recipe's evidence in the reason. No recipe: nothing."""
    if not recipe:
        return []
    from wenart.style import recipe as RC

    have = layer_counts(items)
    taken = {i.get("slot") for i in items}
    src = ("built-in designer defaults" if recipe.get("source") == "default"
           else f"{recipe.get('n')} reference photos")
    out: list[dict] = []
    for gap in RC.gaps(recipe, have):
        layer = gap["layer"]
        need = gap["wanted"] - gap["have"]
        every = layer in EVERY_SLOT_LAYERS
        for kind, types in LAYER_SLOTS.get(layer, ()):
            for slot in rq.slots:
                if (need <= 0 and not every) or slot.kind != kind or slot.id in taken:
                    continue
                dtype = next((t for t in types if t in slot.types), None)
                if dtype is None:
                    continue
                why = (f"recipe: {float(gap['share'] or 0):.0%} of good {recipe.get('family') or ''} "
                       f"{recipe.get('space')} rooms show {RC.LAYER_TEXT.get(layer, layer).split(' (')[0]} "
                       f"({src})").replace("  ", " ")
                made, _refused = build_items(rq, [{"slot": slot.id, "type": dtype, "colour": None,
                                                   "reasons": [why, why]}], "rule", building, new_id)
                for it in made:
                    it.update(method="rule", confidence=0.7, reason=why)
                if made:
                    out += made
                    taken.add(slot.id)
                    need -= 1
    return out


def load_recipes(path: Optional[str], style_path: Optional[str]) -> Optional[dict]:
    """``{space: recipe}`` of ``recipes.json`` (``path``, else beside ``style_path``); without the file the built-in
    recipes of every space (``recipe.default_recipe``: a styled room is the default, lesson UL42); ``path`` "none":
    None (no recipe)."""
    if path == "none":
        return None
    from wenart.style import recipe as RC
    from wenart.style import references as RF

    cand = Path(path) if path else (Path(style_path).parent / "recipes.json" if style_path else None)
    if cand is None or not cand.is_file():
        return {space: RC.default_recipe(space) for space in RF.SPACES}
    data = json.loads(cand.read_text(encoding="utf-8"))
    return data.get("recipes") if isinstance(data, dict) and isinstance(data.get("recipes"), dict) else None


def lamps_on_of(style: Optional[dict]) -> bool:
    """True when the style's mood turns the lamps on (``vocabulary.LIGHTING[mood]["lamps_on"]``)."""
    from wenart.style import vocabulary as V

    mood = str(((style or {}).get("lighting") or {}).get("mood") or "")
    return bool((V.LIGHTING.get(mood) or {}).get("lamps_on"))


def apply(building: dict, style_text: str, answers: dict, model: Optional[str] = None,
          style: Optional[dict] = None, recipes: Optional[dict] = None) -> tuple[dict, list[RoomDecor]]:
    """The decorated building (new dict) and the per-room records (module docstring); ``style`` (Milestone 10): the
    profile whose decor words (colours, plant species and pots, the mood's lamps) ``apply_brief_looks`` applies."""
    out = json.loads(json.dumps(building))
    # Milestone 13 (round 2): the rugs the group solver laid as group members are kept with their ids
    # (``decor.solver_rugs``, as ``decor.add_decor``); new items are numbered after them
    out["decor"] = D.solver_rugs(out)
    records: list[RoomDecor] = []
    mode = decor_mode(out)
    counters: dict[str, int] = D.decor_counters(out["decor"])
    looks: dict[str, int] = {}
    lamps = lamps_on_of(style)
    family = None
    if style:
        from wenart.furniture.fit import style_family_of

        family = style_family_of(style)[0]

    def new_id(level_id: str) -> str:
        counters[level_id] = counters.get(level_id, 0) + 1
        return f"dec_{level_id}_{counters[level_id]:03d}"

    if mode == "off":
        out["decor"] = []                              # no decor at all, the solver's rugs included (as add_decor)
        return out, records
    store = answers.get("answers") or {}
    model = model or answers.get("model") or "?"
    targets, partner_notes = D.copy_targets(out)
    questions = ({q.room["id"]: q for q in room_questions(out, style_text, set(targets), recipes=recipes)}
                 if mode == "ai" else {})
    # 27 Oct 2026: each furnished room's decor minimum (its style's density), kept for the architect's S3 check
    out["decor_minimum"] = {room["id"]: room_minimum(room, room_recipe(room, recipes), family)
                            for room, _pieces in D.rooms_with_pieces(out)}
    for room, pieces in D.rooms_with_pieces(out):
        if room["id"] in targets:
            continue
        rec = RoomDecor(room["id"], room["label"], room.get("room_type") or "other")
        q = questions.get(room["id"])
        if q is None:
            # No AI question for this room (rules mode, no usable piece, no slot): the M8 rules as before.
            items, row = D.rule_decor_room(out, room, pieces, new_id)
            top_notes: list[str] = []
            items += TT.dress_tops(room, pieces, out, items, new_id,      # 28 Oct 2026: set tables, styled tops
                                   density=out["decor_minimum"][room["id"]]["density"], notes=top_notes)
            apply_brief_looks(items, style, lamps, looks)
            out["decor"].extend(items)
            if items or mode == "rules":
                rec.items, rec.fallback = items, ("brief.decor is 'rules'" if mode == "rules"
                                                  else "no slot for AI decor")
                rec.notes = ([row.get("note")] if row.get("note") else []) + top_notes
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
        items += fill_recipe(q, items, out, new_id, room_recipe(room, recipes))
        items += required_items(q, items, out, new_id)
        if items:
            items += fill_to_minimum(q, items, out, new_id, room_recipe(room, recipes), family)
            # 28 Oct 2026 (user: "kettle in the kitchen, microwave in the kitchen etc"): the worktop, dressed
            # modestly by rule (the AI's slots hold no counter); the fallback gets it from decor.rule_decor_room
            items += D.kitchen_worktop_decor(out, room, pieces, new_id, existing=items)
            # 29 Oct 2026 (UL115, UL118): and the style family's styling sets (wenart.blender.kitchen_details)
            items += D.kitchen_styling_decor(out, room, pieces, new_id, existing=items, family=family)
            items += TT.dress_tops(room, pieces, out, items, new_id, q.slots,   # 28 Oct 2026: set tables, tops
                                   density=out["decor_minimum"][room["id"]]["density"], notes=rec.notes)
        apply_brief_looks(items, style, lamps, looks)
        if items:
            rec.items = items
            out["decor"].extend(items)
        else:
            errors = [f"pass {n}: {rec.passes[n]['error']}" for n in PASSES if rec.passes[n]["error"]]
            why = ("; ".join(errors) if errors else "the two passes agreed on no item" if not agreed
                   else "every agreed item was refused by the checks")
            fallback, row = D.rule_decor_room(out, room, pieces, new_id)
            fallback += fill_recipe(q, fallback, out, new_id, room_recipe(room, recipes))
            fallback += required_items(q, fallback, out, new_id)
            fallback += fill_to_minimum(q, fallback, out, new_id, room_recipe(room, recipes), family)
            fallback += TT.dress_tops(room, pieces, out, fallback, new_id, q.slots,   # 28 Oct 2026
                                      density=out["decor_minimum"][room["id"]]["density"], notes=rec.notes)
            apply_brief_looks(fallback, style, lamps, looks)
            rec.items, rec.fallback = fallback, why
            out["decor"].extend(fallback)
        records.append(rec)
    by_id = {r.room_id: r for r in records}

    def record_of(room_id: str) -> RoomDecor:
        if room_id not in by_id:
            room = next((r for r in out.get("rooms") or [] if r.get("id") == room_id), {})
            by_id[room_id] = RoomDecor(room_id, str(room.get("label") or room_id), room.get("room_type") or "other")
            records.append(by_id[room_id])
        return by_id[room_id]

    def light(skip: set, only: Optional[set] = None) -> None:
        # 28 Oct 2026 (user on real04 run 20261028-005318-full: "More lights from the ceiling needed"): every lit room
        # gets the ceiling lights of its zones and its floor (``ceiling_lights.add_lights``), whatever the AI chose
        from wenart.furniture import ceiling_lights as CL

        made, notes = CL.add_lights(out, new_id, lambda room: room_minimum(room, room_recipe(room, recipes),
                                                                          family)["density"], skip=skip, only=only)
        apply_brief_looks(made, style, lamps, looks)
        present = {d.get("id") for d in out["decor"]}
        for rec in records:                        # a pendant row laid again replaces the AI's single pendant
            rec.items = [i for i in rec.items if i.get("id") in present]
        for it in made:
            record_of(it["room_id"]).items.append(it)
        for rid, room_notes in notes.items():
            record_of(rid).notes += room_notes

    light(set(targets))                            # the partners' copies take the lights with the rest of the decor
    copies, copy_notes = D.copy_partner_decor(out, out["decor"], targets, new_id)
    out["decor"].extend(copies)
    rooms = {r["id"]: r for r in out["rooms"]}
    for rid, (pid, kind, _t) in sorted(targets.items()):
        rec = RoomDecor(rid, rooms[rid]["label"], rooms[rid].get("room_type") or "other")
        rec.items = [c for c in copies if c["room_id"] == rid]
        rec.fallback = None
        # The room's own notes only: "r_b_2: ..." is not a note of r_b.
        rec.notes = [f"decor copied from {pid} ({kind}, not asked)"] + [n for n in copy_notes
                                                                         if n.startswith(f"{rid}: ")]
        records.append(rec)
        by_id[rid] = rec
    if partner_notes and records:
        records[-1].notes += partner_notes
    if recipes is not None:
        # 27 Oct 2026 (lesson UL42: "veranda is not like a veranda"): the verandas and terraces get the set, the
        # planters, the rug and the lantern good photos of them show (outdoor_sets)
        from wenart.furniture import outdoor_sets as OS

        before = {d.get("id") for d in out["decor"]}
        out, out_notes = OS.furnish(out, recipes)
        for space in (out.get("site") or {}).get("outdoor_spaces") or []:
            mine = [n for n in out_notes if n.startswith(f"{space.get('id')}: ")]
            if not mine:
                continue
            rec = RoomDecor(space["id"], str(space.get("label") or space["id"]), str(space.get("kind") or "outdoor"))
            rec.items = [d for d in out["decor"] if d.get("outdoor_space") == space["id"] and d.get("id") not in before]
            rec.notes = mine
            records.append(rec)
            by_id[space["id"]] = rec
    light(set(), set(targets))                     # a partner's copy that lacks lights (its pieces did not map) is lit
    # 29 Oct 2026 (UL99, UL103): a twin's own TV unit and bookshelves that its partner's copy left bare (its pieces did
    # not map: the media wall or the room fill placed them a little differently) get their TV and books
    for rid in sorted(targets):
        room = rooms.get(rid)
        if room is None:
            continue
        pieces = [f for f in out.get("furniture") or [] if f.get("room_id") == rid]
        made = TT.bare_hosts(room, pieces, out, [d for d in out["decor"] if d.get("room_id") == rid], new_id)
        gone = {i for it in made for i in it.get("clears") or ()}     # a copied item where the TV stands leaves
        out["decor"] = [d for d in out["decor"] if d.get("id") not in gone] + made
        record_of(rid).items = [i for i in record_of(rid).items if i.get("id") not in gone] + made
    # 28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside"): no rug,
    # runner or carpet on the floor of an open-air room or an outdoor space, whatever rule laid it
    from wenart.blender import outdoor as OD

    for d in OD.strip_outdoor_textiles(out):
        rid = d.get("room_id") or d.get("outdoor_space") or "-"
        rec = record_of(rid) if d.get("room_id") else by_id.get(rid)
        if rec is not None:
            rec.items = [i for i in rec.items if i.get("id") != d.get("id")]
            rec.notes.append(f"{d.get('type')} {d.get('id')} left out: {d['removed_reason']}")
    # 29 Oct 2026 (lesson UL106): the professional dressing of the living rooms and bedrooms (layered curtains and
    # bedding, the lights plan's statement, downlights and bedside pendants, the rooms' feature-wall and floor-pattern
    # decisions from their recipes: wenart.furniture.dressing); the questions and the stored answers are unchanged
    from wenart.furniture import dressing as DR

    before = {d.get("id") for d in out["decor"]}
    DR.dress(out, style, lambda room: room_recipe(room, recipes), new_id)     # its notes: out["dressing"]["notes"]
    # 29 Oct 2026 (lessons UL113, UL115, UL119: the user's reference photos, "different solutions for different
    # rooms"): every room's own scheme and the photos' details (wenart.furniture.room_details); its record:
    # out["room_schemes"]
    from wenart.furniture import room_details as RD

    RD.dress_details(out, style, new_id)
    # 29 Oct 2026 (lesson UL121: "look how realistic the bed is looking full and nice I want this much detail in our
    # models"): every bed's family set, its free sides and its throws' weave, the round drum nightstands' decor set
    # (wenart.furniture.bedding); its record: out["bedding"]
    from wenart.furniture import bedding as BG

    BG.dress_beds(out, style, new_id)
    present = {d.get("id") for d in out["decor"]}
    for rec in records:                            # a TV hung on the wall leaves its unit's top items
        rec.items = [i for i in rec.items if i.get("id") in present or not i.get("id")]
    room_ids = {r.get("id") for r in out.get("rooms") or []}
    for it in out["decor"]:
        if it.get("id") not in before and it.get("room_id") in room_ids:
            record_of(it["room_id"]).items.append(it)
    # 29 Oct 2026 (lessons UL114, UL123, UL124: the user's bathroom photos): every wet room's accessories in its style
    # family's set (paper holder and brush, towel rail, shelf and bars, the family's mirror, the feature wall, the
    # downlights and the cove light; wenart.furniture.bath_details); the questions and the stored answers are unchanged
    from wenart.furniture import bath_details as BD

    before = {d.get("id") for d in out["decor"]}
    _out, bath_notes = BD.dress(out, style, new_id)
    for it in out["decor"]:
        if it.get("id") not in before and it.get("room_id") in room_ids:
            record_of(it["room_id"]).items.append(it)
    for note in bath_notes:
        rid = note.split(":", 1)[0]
        if rid in room_ids:
            record_of(rid).notes.append(note)
    D.attach_host_frames(out)                     # Milestone 12 (§4.7): every item in its host's frame
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
            "rooms_fallback": sum(1 for r in records if r.fallback),
            # the rooms that hold rule items: a twin's copy of its partner's rule items has no fallback of its own
            # (CPU pre-flight of 16 Oct 2026, real04: "2 rule item(s) in 0 room(s)")
            "rooms_rule": sum(1 for r in records if any(i.get("method") == "rule" for i in r.items))}


def report(records: list[RoomDecor], building: dict, model: Optional[str]) -> str:
    s = summary(records, building, model)
    lines = [f"# Decor: {building['project']['id']}", "",
             f"AI decor (docs/milestone9.md §4): {s['items_ai']} items chosen by the AI (model {model or '-'}, both "
             f"passes agreeing, confidence {CONFIDENCE_AGREED}) in {s['rooms_ai']} rooms; {s['items_rule']} items by "
             f"the rules (M4/M8) in {s['rooms_rule']} rooms; the AI decor did not apply in {s['rooms_fallback']} rooms "
             "(reason per room). "
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

    # 27 Oct 2026 (pod run 123917: the decor stage stopped on the veranda's record): an outdoor space's record draws
    # the space's outline and its pieces (``outdoor_space``)
    spaces = (building.get("site") or {}).get("outdoor_spaces") or []
    room = next((r for r in building.get("rooms") or [] if r.get("id") == rec.room_id), None) or \
        next((o for o in spaces if o.get("id") == rec.room_id), None)
    if room is None or len(room.get("polygon") or []) < 3:
        return
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal")
    ax.add_patch(MplPolygon(room["polygon"], closed=True, fill=False, lw=2, color="black"))
    for f in building["furniture"]:
        if f.get("room_id") != rec.room_id and f.get("outdoor_space") != rec.room_id:
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
# Milestone 10 slots (docs/milestone10.md §4.6): windows, ceilings, throws, the new hosts, large floor items
# --------------------------------------------------------------------------

CURTAIN_MIN_WINDOW_W = 0.9           # narrower windows take a blind only
CURTAIN_OVERLAP_M = 0.2              # a curtain rod reaches this far past each side of its window
CURTAIN_MIN_OVERLAP_M = 0.05         # ... at least this after it is narrowed (doors, wall ends)
CURTAIN_WALL_GAP_M = 0.1             # the curtain's centre this far into the room from the wall face (rod brackets)
CURTAIN_DEPTH_M = 0.08
CURTAIN_ROD_ABOVE_M = 0.15           # the rod this far above the window top (at most up to the ceiling clearance)
CURTAIN_FLOOR_GAP_M = 0.01
CURTAIN_SILL_DROP_M = 0.1            # a sill-length curtain (furniture under the window) ends this far below the sill
BLIND_WIDTH_EXTRA_M = 0.1
BLIND_DEPTH_M = 0.06
BLIND_ROLLER_ABOVE_M = 0.06
LIGHT_CEILING_CLEAR_M = 0.02
PENDANT_SIZE = (0.45, 0.45)
PENDANT_OVER_TABLE_M = 0.75          # a pendant's bottom this far above a dining table's top
PENDANT_MIN_BOTTOM_M = 2.0           # elsewhere a pendant's bottom stays above head height
PENDANT_MIN_DROP_M = 0.3             # a pendant needs at least this much below the ceiling
CEILING_LIGHT_SIZE = (0.4, 0.4, 0.12)
CEILING_SLOT_GAP_M = 0.6             # the room-centre light this far from every other ceiling slot
LIGHT_HOSTS: dict[str, tuple[str, ...]] = {"table_dining": ("pendant_light",),
                                          "table_coffee": ("pendant_light", "ceiling_light"),
                                          "bed_double": ("ceiling_light", "pendant_light"),
                                          "bed_single": ("ceiling_light", "pendant_light")}
THROW_HOSTS: tuple[str, ...] = ("sofa", "sofa_corner", "chaise", "armchair", "bed_double", "bed_single")
THROW_SEAT_SIZE = (0.5, 0.45, 0.05)  # folded over a seat end
THROW_BED_DEPTH_M = 0.5              # across a bed's foot
FLOOR_ITEM_SIZES: dict[str, tuple[float, float, float]] = {"plant": (D.PLANT_SIZE[0], D.PLANT_SIZE[1], 1.0),
                                                         "plant_large": (0.6, 0.6, 1.6), "basket": (0.4, 0.4, 0.4),
                                                         "sculpture": (0.35, 0.35, 0.9)}
FLOOR_ITEM_INSET_M: dict[str, float] = {"plant": D.CORNER_INSET_M, "plant_large": 0.35, "basket": D.CORNER_INSET_M,
                                        "sculpture": D.CORNER_INSET_M}
CLOCK_WIDTH = (0.35, 0.25)           # a wall clock's diameter and the least the wall may leave
CLOCK_GAP_M = 0.35                   # its bottom this far above the piece below
BRIEF_COLOUR_KEYS: dict[str, str] = {"cushion": "cushion_colours", "throw": "throw_colours", "rug": "rug_colours",
                                     "curtain": "curtain_colour", "blind": "curtain_colour"}


def _window_heights(op: dict, clip: Optional[dict] = None) -> tuple[float, float]:
    """``(sill, top)`` of a window above its floor (the building's values, else the 0.90 / 1.20 m defaults); fix
    round after P6a: ``clip`` (``decor.roof_clips``) gives the window as the build clips it under the roof."""
    if clip is not None:
        sill = float(clip["sill_height"])
        return sill, sill + float(clip["height"])
    sill = float(op.get("sill_height") if op.get("sill_height") is not None else 0.9)
    return sill, sill + float(op.get("height") or 1.2)


def _span_ok(s0: float, s1: float, blocked: list[tuple[float, float]]) -> bool:
    return all(s1 <= b0 + 1e-9 or s0 >= b1 - 1e-9 for b0, b1 in blocked)


def window_items(room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext, ceiling: float,
                 planes: Optional[list] = None) -> tuple[list[tuple[str, dict]], list[str]]:
    """``([(window id, {type: item})], notes)``: the curtain (windows at least ``CURTAIN_MIN_WINDOW_W`` wide: a
    rod ``CURTAIN_OVERLAP_M`` past each side, narrowed to stay ``OPENING_MARGIN_M`` off every door and other window
    of its wall face and inside it; to the floor, or to the sill when furniture stands under the window) and the
    roller blind (``BLIND_DOWN_SHARE`` of the window drawn down) of every window of the room. Never over a door:
    only windows get slots, and the spans keep off the doors of the same wall.
    Fix round after P6a (module docstring): the window as the build clips it under the roof (``decor.roof_clips``),
    and under the slope the rod and the roller ``decor.WINDOW_DECOR_CEILING_CLEAR_M`` under the ceiling over their
    own footprint (``decor.ceiling_over``; ``planes``: the level's sloped ceiling, computed when None)."""
    from shapely.geometry import Polygon as ShPolygon

    doors, windows = placer.room_openings(building, room)
    furniture = [placer.piece_from_furniture(p).polygon() for p in pieces if p.get("build", True) is not False
                 and not schemas.off_floor(p)]
    out, notes = [], []
    clips = D.roof_clips(building, room["level_id"])
    if planes is None:
        planes = D.ceiling_planes(building, room["level_id"])

    def over(centre, size, rotation) -> float:
        """The ceiling over an item's footprint: the level's flat ceiling, or the slope where it is lower."""
        if not planes:
            return ceiling
        return min(ceiling, D.ceiling_over(building, room["level_id"], centre, size, rotation, planes=planes))

    for op in windows:
        c = (float(op["center"][0]), float(op["center"][1]))
        i = ctx.nearest_segment(c)
        a, b = ctx.segments[i]
        seg_len = G.distance(a, b)
        u = ((b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len)
        n = ctx.segment_normal(i)
        s_c = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
        half_w = float(op["width"]) / 2.0
        blocked = []
        for other in doors + windows:
            if other["id"] == op["id"]:
                continue
            oc = (float(other["center"][0]), float(other["center"][1]))
            if G.point_segment_distance(oc, a, b) > 0.3:
                continue
            s_o = (oc[0] - a[0]) * u[0] + (oc[1] - a[1]) * u[1]
            blocked.append((s_o - float(other["width"]) / 2.0 - D.OPENING_MARGIN_M,
                            s_o + float(other["width"]) / 2.0 + D.OPENING_MARGIN_M))
        clip = clips.get(op["id"])
        sill, top = _window_heights(op, clip)             # fix round after P6a: as the build clips it
        clipped = (f"; window {op['id']} clipped by the roof to {top - sill:.2f} m, top {top:.2f} m"
                   if clip is not None else "")
        rotation = round(G.normalise_angle(math.degrees(math.atan2(n[0], -n[1]))), 3)
        made: dict[str, dict] = {}
        if float(op["width"]) >= CURTAIN_MIN_WINDOW_W - 1e-9:
            left = right = CURTAIN_OVERLAP_M
            while left >= CURTAIN_MIN_OVERLAP_M - 1e-9 and right >= CURTAIN_MIN_OVERLAP_M - 1e-9:
                s0, s1 = s_c - half_w - left, s_c + half_w + right
                if s0 < D.WALL_END_MARGIN_M:
                    left -= 0.05
                elif s1 > seg_len - D.WALL_END_MARGIN_M:
                    right -= 0.05
                elif not _span_ok(s0, s1, [x for x in blocked if x[1] <= s_c]):
                    left -= 0.05
                elif not _span_ok(s0, s1, [x for x in blocked if x[0] >= s_c]):
                    right -= 0.05
                else:
                    break
            if left >= CURTAIN_MIN_OVERLAP_M - 1e-9 and right >= CURTAIN_MIN_OVERLAP_M - 1e-9:
                s0, s1 = s_c - half_w - left, s_c + half_w + right
                mid = (s0 + s1) / 2.0
                wp = (a[0] + u[0] * mid, a[1] + u[1] * mid)
                centre = (wp[0] + n[0] * CURTAIN_WALL_GAP_M, wp[1] + n[1] * CURTAIN_WALL_GAP_M)
                here = over(centre, (s1 - s0, CURTAIN_DEPTH_M), rotation)
                sloped = here < ceiling - 1e-6
                rod = min(top + CURTAIN_ROD_ABOVE_M, ceiling - CEILING_CLEAR_M)
                lowered = sloped and here - D.WINDOW_DECOR_CEILING_CLEAR_M < rod - 1e-9
                if lowered:                                # fix round after P6a: under the sloped ceiling
                    rod = here - D.WINDOW_DECOR_CEILING_CLEAR_M
                p0 = (a[0] + u[0] * s0, a[1] + u[1] * s0)
                p1 = (a[0] + u[0] * s1, a[1] + u[1] * s1)
                strip = ShPolygon([p0, p1, (p1[0] + n[0] * 0.2, p1[1] + n[1] * 0.2),
                                   (p0[0] + n[0] * 0.2, p0[1] + n[1] * 0.2)])
                under = any(strip.intersection(f).area > placer.AREA_EPS for f in furniture)
                bottom = max(CURTAIN_FLOOR_GAP_M, sill - CURTAIN_SILL_DROP_M) if under else CURTAIN_FLOOR_GAP_M
                if sloped and (rod < top - 1e-9 or rod - bottom <= 0.3):
                    notes.append(f"window {op['id']}: no curtain under the sloped ceiling ({here:.2f} m over it; "
                                 f"window top {top:.2f} m{clipped})")
                elif rod - bottom > 0.3:
                    note = f"kept under the sloped ceiling, {here:.2f} m over it{clipped}" if lowered else ""
                    slope = f" ({note})" if note else ""
                    made["curtain"] = {"type": "curtain", "center": [round(centre[0], 3), round(centre[1], 3),
                                                                     round(bottom, 3)],
                                       "rotation_deg": rotation,
                                       "size": [round(s1 - s0, 3), CURTAIN_DEPTH_M, round(rod - bottom, 3)],
                                       "window_id": op["id"], "wall_point": [round(wp[0], 3), round(wp[1], 3)],
                                       "reason": f"curtains at window {op['id']}" + (
                                           " (sill length: furniture under the window)" if under else "") + slope}
                    if note:
                        made["curtain"]["note"] = note
                        notes.append(f"window {op['id']}: curtain{slope}")
            else:
                notes.append(f"window {op['id']}: no room for a curtain rod (doors, windows or wall ends)")
        blind_top = min(top + BLIND_ROLLER_ABOVE_M, ceiling - LIGHT_CEILING_CLEAR_M)
        drop = (top - sill) * P.BLIND_DOWN_SHARE + BLIND_ROLLER_ABOVE_M
        bw = float(op["width"]) + BLIND_WIDTH_EXTRA_M
        if _span_ok(s_c - bw / 2.0, s_c + bw / 2.0, blocked):
            wp = (a[0] + u[0] * s_c, a[1] + u[1] * s_c)
            centre = (wp[0] + n[0] * (BLIND_DEPTH_M / 2.0 + 0.005), wp[1] + n[1] * (BLIND_DEPTH_M / 2.0 + 0.005))
            here = over(centre, (bw, BLIND_DEPTH_M), rotation)
            lowered = here < ceiling - 1e-6 and here - D.WINDOW_DECOR_CEILING_CLEAR_M < blind_top - 1e-9
            if lowered:                                    # fix round after P6a: under the sloped ceiling
                blind_top = here - D.WINDOW_DECOR_CEILING_CLEAR_M
            if lowered and blind_top < top - 1e-9:
                notes.append(f"window {op['id']}: no blind under the sloped ceiling ({here:.2f} m over it; "
                             f"window top {top:.2f} m{clipped})")
            else:
                note = f"kept under the sloped ceiling, {here:.2f} m over it{clipped}" if lowered else ""
                slope = f" ({note})" if note else ""
                made["blind"] = {"type": "blind", "center": [round(centre[0], 3), round(centre[1], 3),
                                                             round(blind_top - drop, 3)],
                                 "rotation_deg": rotation, "size": [round(bw, 3), BLIND_DEPTH_M, round(drop, 3)],
                                 "window_id": op["id"], "wall_point": [round(wp[0], 3), round(wp[1], 3)],
                                 "reason": f"roller blind at window {op['id']}" + slope}
                if note:
                    made["blind"]["note"] = note
                    notes.append(f"window {op['id']}: blind{slope}")
        if made:
            out.append((op["id"], made))
    return out, notes


def ceiling_items(room: dict, pieces: list[dict], ceiling: float, building: Optional[dict] = None,
                  planes: Optional[list] = None, notes: Optional[list] = None) -> list[tuple[str, dict]]:
    """``[(slot id, {type: item})]``: pendants and ceiling lights over a dining table (a pendant
    ``PENDANT_OVER_TABLE_M`` above its top), a coffee table and a bed (a pendant only where its bottom stays at
    ``PENDANT_MIN_BOTTOM_M``), and at the room centre when it is inside the room, off a stair and
    ``CEILING_SLOT_GAP_M`` from the others. Items hang from the level's ceiling (``center[2]`` = their bottom).
    Fix round after P4a: with ``building`` each item hangs from the ceiling over its own footprint
    (``decor.ceiling_over``; ``planes``: the level's sloped ceiling, computed when None), so a pendant under a low
    slope is left out (the drop rule) and its slot keeps only the flush ceiling light.
    Fix round after P5 (22 Oct 2026): under the slope a flush ceiling light whose bottom (the ceiling over it minus
    its height) is lower than ``decor.MIN_LIGHT_BOTTOM_M`` is left out too, with the reason in ``notes`` (when
    given)."""
    out: list[tuple[str, dict]] = []
    taken: list[tuple[float, float]] = []
    if building is not None and planes is None:
        planes = D.ceiling_planes(building, room["level_id"])

    def over(centre, size) -> tuple[float, str]:
        if building is None or not planes:
            return ceiling, ""
        here = D.ceiling_over(building, room["level_id"], centre, size, planes=planes)
        return here, (f" (sloped ceiling {here:.2f} m over it)" if here < ceiling - 1e-6 else "")

    def lights(types, centre, bottom_pendant, why):
        made = {}
        for t in types:
            if t == "pendant_light":
                top, note = over(centre, PENDANT_SIZE)
                if top - bottom_pendant >= PENDANT_MIN_DROP_M:
                    made[t] = {"type": t,
                               "center": [round(centre[0], 3), round(centre[1], 3), round(bottom_pendant, 3)],
                               "rotation_deg": 0.0, "size": [*PENDANT_SIZE, round(top - bottom_pendant, 3)],
                               "reason": f"pendant {why}{note}"}
            elif t == "ceiling_light":
                w, d, h = CEILING_LIGHT_SIZE
                top, note = over(centre, (w, d))
                if top < ceiling - 1e-6 and top - h < D.MIN_LIGHT_BOTTOM_M - 1e-9:       # under the slope
                    # fix round after P5: P5's dec_L1_011 hung 1.155 m above the floor, at the camera's lens
                    if notes is not None:
                        notes.append(f"ceiling light {why}: the sloped ceiling over it is {top:.2f} m high, its bottom "
                                     f"would be {top - h:.2f} m above the floor (< {D.MIN_LIGHT_BOTTOM_M:g} m); "
                                     f"left out")
                    continue
                made[t] = {"type": t, "center": [round(centre[0], 3), round(centre[1], 3), round(top - h, 3)],
                           "rotation_deg": 0.0, "size": [w, d, h], "reason": f"ceiling light {why}{note}"}
        return made

    for host in sorted((p for p in pieces if usable_host(p) and p["type"] in LIGHT_HOSTS), key=lambda p: p["id"]):
        c = (float(host["footprint"]["center"][0]), float(host["footprint"]["center"][1]))
        bottom = (_host_top(host) + PENDANT_OVER_TABLE_M if host["type"] == "table_dining"
                  else max(PENDANT_MIN_BOTTOM_M, _host_top(host) + PENDANT_OVER_TABLE_M))
        made = lights(LIGHT_HOSTS[host["type"]], c, bottom, f"over {host['type'].replace('_', ' ')} {host['id']}")
        if made:
            out.append((f"ceiling:over_{host['id']}", made))
            taken.append(c)
    centre = G.polygon_centroid(room["polygon"])
    stairs = [placer.piece_from_furniture(p).polygon() for p in pieces if p["type"] == "stair"]
    from shapely.geometry import Point as ShPoint
    if (G.point_in_polygon(centre, room["polygon"]) and all(G.distance(centre, t) >= CEILING_SLOT_GAP_M for t in taken)
            and not any(s.contains(ShPoint(centre)) for s in stairs)):
        made = lights(("ceiling_light", "pendant_light"), centre, PENDANT_MIN_BOTTOM_M, "at the room centre")
        if made:
            out.append((f"ceiling:centre_{room['id']}", made))
    return out


def throw_item(host: dict) -> Optional[dict]:
    """A throw on a seat end of a sofa, corner sofa (its chaise), chaise or armchair, or across a bed's foot."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    rot = host["footprint"]["rotation_deg"]
    if host["type"] in ("bed_double", "bed_single"):
        size = [round(w * 0.95, 3), THROW_BED_DEPTH_M, THROW_SEAT_SIZE[2]]
        local = (0.0, -d / 2.0 + THROW_BED_DEPTH_M / 2.0 + 0.03)
        why = "throw across the foot of the bed"
    else:
        tw, td, th = THROW_SEAT_SIZE
        tw, td = min(tw, w * 0.5), min(td, d * 0.6)
        if host["type"] == "sofa_corner":
            side = host.get("chaise_side") if host.get("chaise_side") in ("left", "right") else "right"
            x = (w / 2.0 - 0.45) if side == "right" else (-w / 2.0 + 0.45)
            local = (x, -d / 2.0 + td / 2.0 + 0.15)
        elif host["type"] == "chaise":
            local = (0.0, -d / 2.0 + td / 2.0 + 0.1)
        else:
            local = (-w / 2.0 + tw / 2.0 + min(0.15, w * 0.1), -0.05 * d)
        size = [round(tw, 3), round(td, 3), th]
        why = f"throw on the {host['type'].replace('_', ' ')}"
    return {"type": "throw", "center": D._local_to_building(host, local[0], local[1]), "rotation_deg": rot,
            "size": size, "reason": why}


def soft_items_m10(host: dict) -> list[dict]:
    """Cushions of the Milestone 10 soft hosts: along a corner sofa's back (``decor.host_decor``), one against a
    chaise's back, one lying on an ottoman, two lying at a bench's ends."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    rot = host["footprint"]["rotation_deg"]
    if host["type"] == "sofa_corner":
        return [i for i in D.host_decor(host) if i["type"] == "cushion"]
    if host["type"] == "chaise":
        return [{"type": "cushion", "center": D._local_to_building(host, 0.0, d / 2.0 - 0.15 - D.CUSHION_SIZE[1] / 2.0),
                 "rotation_deg": rot, "size": list(D.CUSHION_SIZE), "reason": "cushion against the chaise back"}]
    lying = [0.4, 0.4] if w >= 0.45 and d >= 0.45 else [round(min(w, d) * 0.8, 3)] * 2
    if host["type"] == "ottoman":
        return [{"type": "cushion", "center": D._local_to_building(host, 0.0, 0.0), "rotation_deg": rot,
                 "size": lying, "reason": "cushion lying on the ottoman"}]
    if host["type"] == "bench" and w >= 1.0:
        lying = [min(0.4, d * 0.9)] * 2
        return [{"type": "cushion", "center": D._local_to_building(host, s * (w / 2.0 - lying[0] / 2.0 - 0.05), 0.0),
                 "rotation_deg": rot, "size": lying, "reason": "cushion lying at the bench's end"} for s in (-1, 1)]
    return []


def floor_items(room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext, allowed: set,
                ceiling: float) -> list[tuple[str, dict]]:
    """``[(slot id, {type: item})]``: up to ``FLOOR_CORNERS_MAX`` free room corners (the M4 corner check), each with
    the floor types that fit there (a large plant and a floor sculpture need a larger free square, inset further,
    and room under the ceiling)."""
    types = [t for t in ("plant", "plant_large", "basket", "sculpture") if t in allowed]
    if not types:
        return []
    spots = [(c, "corner") for c in free_corners(room, pieces, building, ctx)[:FLOOR_CORNERS_MAX]]
    if len(spots) < FLOOR_CORNERS_MAX:              # 27 Oct 2026 (run 160846): beside the sofa or a window
        for c in wall_spots(room, pieces, building, ctx, [c for c, _k in spots]):
            if len(spots) >= FLOOR_CORNERS_MAX:
                break
            spots.append((c, "wall"))
    planes = D.ceiling_planes(building, room["level_id"])     # Milestone 11 (E2): the attic slope
    out = []
    for n, (small, where) in enumerate(spots, start=1):
        made = {}
        for t in types:
            w, d, h = FLOOR_ITEM_SIZES[t]
            if h > ceiling - CEILING_CLEAR_M:
                continue
            centre = small
            if (w, d) != tuple(D.PLANT_SIZE):
                inset = FLOOR_ITEM_INSET_M[t]
                options = free_corners(room, pieces, building, ctx, size=(w, d), inset=inset,
                                       candidates=None if where == "corner" else D.wall_candidates(ctx, inset))
                near = [c for c in options if G.distance(c, small) <= 0.3]
                if not near:
                    continue
                centre = near[0]
            if planes and h > D.ceiling_over(building, room["level_id"], centre, (w, d), planes=planes) \
                    - CEILING_CLEAR_M:
                continue                      # the sloped ceiling over this corner is too low (real02's attic)
            made[t] = {"type": t, "center": [round(centre[0], 3), round(centre[1], 3)], "rotation_deg": 0.0,
                       "size": [w, d, h] if t != "plant" else list(D.PLANT_SIZE),
                       "reason": f"{t.replace('_', ' ')} " + ("in a free corner" if where == "corner"
                                                              else "against a free wall, beside the seating or a "
                                                                   "window")}
        if made:
            out.append((f"{room['id']}.{'corner' if where == 'corner' else 'floor'}{n}", made))
    return out


PLANT_SPACING_M = 1.5            # two floor plants of a room stand at least this far apart
PLANT_BESIDE_M = 0.9             # a wall place this close to a seat, bed or window ranks first


def wall_spots(room: dict, pieces: list[dict], building: dict, ctx: placer.RoomContext,
               others: list) -> list[tuple[float, float]]:
    """27 Oct 2026 (run 160846: no free corner in real06's 55 m2 salon): the wall places a floor plant may take
    (``decor.wall_candidates`` through ``free_corners``' checks), those within ``PLANT_BESIDE_M`` of a sofa, armchair,
    bed or window first (the nearest first), each ``PLANT_SPACING_M`` from the others and from ``others``."""
    free = free_corners(room, pieces, building, ctx, candidates=D.wall_candidates(ctx))
    near_types = {"sofa", "sofa_corner", "armchair", "bed_double", "bed_single", "chaise", "sideboard", "desk"}
    marks = [tuple(p["footprint"]["center"]) for p in pieces if p.get("type") in near_types and p.get("footprint")]
    marks += [tuple(w.band.centroid.coords[0]) for w in ctx.windows]

    def beside(c):
        return min((G.distance(c, m) for m in marks), default=math.inf)
    ranked = sorted(free, key=lambda c: (beside(c) > PLANT_BESIDE_M + 1.5, beside(c), c))
    out: list = []
    for c in ranked:
        if all(G.distance(c, o) >= PLANT_SPACING_M for o in list(others) + out):
            out.append(c)
    return out


def plant_look(style: Optional[dict], index: int) -> tuple[Optional[str], Optional[dict], str]:
    """``(species, pot, why)`` of the ``index``-th large plant of the project: the brief's species and pots in turn
    (``style.json`` ``decor.plant_species`` / ``decor.pots``), else none (an ``other`` plant in the default pot)."""
    decor = (style or {}).get("decor") if isinstance((style or {}).get("decor"), dict) else {}
    species = [s for s in decor.get("plant_species") or [] if s in P.PLANT_SPECIES]
    pots = [p for p in decor.get("pots") or [] if isinstance(p, dict)]
    sp = species[index % len(species)] if species else None
    pot = dict(pots[index % len(pots)]) if pots else None
    why = (f"species {sp} and pot {pot} from the brief (in turn)" if (sp or pot)
           else "no plant species or pot in the brief")
    return sp, pot, why


def brief_colour(style: Optional[dict], dtype: str, index: int) -> Optional[str]:
    """The brief's colour of a decor type (``style.json`` ``decor``: cushions and throws alternate their colours,
    rugs too, curtains and blinds take the curtain colour), None when the brief names none."""
    decor = (style or {}).get("decor") if isinstance((style or {}).get("decor"), dict) else {}
    value = decor.get(BRIEF_COLOUR_KEYS.get(dtype, ""))
    if isinstance(value, list):
        return value[index % len(value)] if value else None
    return value if isinstance(value, str) and value else None


def apply_brief_looks(items: list[dict], style: Optional[dict], lamps_on: bool, counters: dict) -> None:
    """In place: the brief's colours on cushions, throws, rugs, curtains and blinds (the AI's colour kept as
    ``colour_ai`` when they differ), the species and pot of large plants, ``light_on`` of lamps and lights in a
    ``lamps_on`` mood (the interior evening, docs/milestone10.md §4.9). ``counters`` keep the turn across rooms."""
    for item in items:
        dtype = item.get("type")
        if dtype in BRIEF_COLOUR_KEYS:
            i = counters.get(dtype, 0)
            colour = brief_colour(style, dtype, i)
            if colour:
                counters[dtype] = i + 1
                if item.get("colour") and item["colour"] != colour:
                    item["colour_ai"] = item["colour"]
                item["colour"] = colour
                item["colour_source"] = "brief"
        if dtype == "plant_large":
            i = counters.get("plant_large", 0)
            counters["plant_large"] = i + 1
            species, pot, why = plant_look(style, i)
            item["species"] = species
            item["pot"] = pot
            item["look_reason"] = why
        if dtype in P.LIGHT_TYPES:
            item["light_on"] = bool(lamps_on)


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
    p.add_argument("--recipes", help="recipes.json (wenart.style.recipe build); default: next to --style")
    a.add_argument("--recipes", help="recipes.json (wenart.style.recipe build); default: next to --style")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    try:
        building = B.load(args.building)
        style_text = _style_text(args, building)
        recipes = load_recipes(args.recipes, args.style)
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
            doc, failed = ask(building, style_text, client, Path(args.answers), model, recipes=recipes)
            print(f"decor ask: {len(doc['answers'])} stored answer(s) -> {args.answers}")
            return EXIT_SERVER if failed else EXIT_OK
        answers = read_answers(Path(args.answers))
        style = json.loads(Path(args.style).read_text(encoding="utf-8")) if args.style else None
        if isinstance(style, list):
            style = style[0] if style else None
        out, records = apply(building, style_text, answers, style=style, recipes=recipes)
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
              f"in {s['rooms_rule']} room(s), {s['rooms_fallback']} room(s) without AI decor -> {out_path}")
        return EXIT_OK
    except (UsageError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"decor: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
