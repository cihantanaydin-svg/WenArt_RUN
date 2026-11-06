"""Architectural-sense checks of a reading (RC14; 6 Nov 2026, Milestone 14 R6, the code half of the critic).

What: ``findings(out_dir)`` reads a pipeline output (``building.json``, ``sheets.json`` and the texts of each level's
drawing) and returns the findings an architect sees at a glance, each shaped like ``wenart.reading_check._finding``
(``check: "RC14"``, ``name``, ``severity``, ``level_id``, ``message``) plus ``rule``, ``place`` ([x, y] building
metres or None), ``element_ids`` and ``advisory: true``. The rules (``RULES``), each a pure function on the building
dict (and the level texts where it needs them):

1. ``room_type_area``: a room whose type is implausible for its area (``AREA_RANGES``: a 16 m2 lift);
2. ``label_names_larger_face``: a small room's label is the only name of a face several times that room's size
   (``LARGER_FACE_FACTOR``): a fire lobby's label naming the car park around it;
3. ``frame_walls_and_paper_rooms``: walls on the level region's box edges covering most of its perimeter with no
   opening and no wall ending on them (the sheet frame read as walls) and rooms enclosed by those walls or covering
   most of the box with other rooms' labels in them (a room of paper);
4. ``unread_walls``: a level with many room labels and few walls, or most labels outside every room;
5. ``circulation``: a level no stair reaches from its neighbour, a room with no door or opening, a group of rooms
   (a flat) with no door to a stair, a hall or the outside;
6. ``label_vocabulary``: a room label holding a notation phrase (a footprint line, a services wall, a level mark, an
   axis, a number with a unit, a drawing title, a floor's name).

Round 2 (6 Nov 2026; the classes of the user's 3-4 Nov corrections the first six rules missed, measured on the readings
made before those corrections; every distance compared with a reach gets ``EPS`` of slack):

7. ``facade_recess`` (C0003, C0023, C0037): small unnamed rooms with no door, reached only through unclassified gaps,
   one of them the mouth in the facade, with a named room's window looking in or the mouth as wide as the room;
8. ``false_stair`` (C0007): a stair in a wet room or a kitchen, too small, or with many flights in a small box;
9. ``stair_stacking`` (C0009, C0010): the one core stair of two neighbouring floors more than a metre apart;
10. ``mirror_twins`` (C0004, C0018): twin rooms about the reading's own mirror axis that differ in type, in area, or
    of which one cannot be entered;
11. ``wall_across_passage`` (C0051, C0053): an unclassified gap between a hall and a room with no door symbol;
12. ``wall_mass`` (C0020): a face under 0.6 m2 typed hall or unknown.

Every finding is advisory: ``wenart.reading_check.check`` counts it under ``counts["advisory"]``, never in the
verdict. Each rule's precision was judged one finding at a time on the readings of the 20 real and 21 synthetic
projects (``models/sense_trust.json``, with every judgement and its reason); a rule below ``TRUST_MIN`` writes its
findings with severity ``info`` (``apply_trust``). The tables were tuned on those same readings (6 Nov 2026: a tight
region box is no frame, a drawn area text that agrees is no error, service rooms need no drawn door ...; each tuning is
commented where it is made), so the judged precision is in-sample.

Why: the user (4 Nov 2026): "some AI or something else to give the feedbacks by itself instead of me at some point".
Many of the user's corrections were things an architect sees at a glance: a lift the size of a bedroom, a fire lobby
the size of the car park, the sheet frame read as four walls and a 440 m2 room named from the sheet's area text, floors
whose hatch-drawn walls were mostly not read. Code checks with clear rules raise these classes without the user.

How: room types come from the reading's own ``room_type``, refined by the label's words where the schema type is
coarse (a ``shaft`` may be a lift, a light well or a void; a ``hall`` may be a fire lobby; ``storage`` may be a
shelter or a water tank; ``sense_type``); the region box is the level page's ``region_box`` mapped by its
``transform_to_building``; an opening belongs to a room when its wall touches the room polygon within half the wall
thickness (``ROOM_REACH_M`` added); stairs are rooms of type stair and stair pieces of furniture. No AI, no pod.
``python -m wenart.reading_check sense check --out DIR`` prints the findings; ``sense trust --judged FILE --write``
writes the trust file from a judged calibration.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B

CHECK = "RC14"
NAME = "architectural sense"
RULES = {
    "room_type_area": "a room type implausible for its area",
    "label_names_larger_face": "a small room's label names a much larger face",
    "frame_walls_and_paper_rooms": "the sheet frame read as walls, a room of paper",
    "unread_walls": "a level whose walls are mostly unread",
    "circulation": "a level, a room or a flat that cannot be reached",
    "label_vocabulary": "a notation phrase in a room name",
    # 6 Nov 2026, round 2
    "facade_recess": "a facade recess closed into rooms",
    "false_stair": "a stair where no stair can be",
    "stair_stacking": "the core stairs of two floors off each other",
    "mirror_twins": "the two halves of a mirrored plan read differently",
    "wall_across_passage": "a wall across a drawn passage",
    "wall_mass": "a face of wall mass read as a room",
}
TRUST_PATH = Path(__file__).resolve().parent / "models" / "sense_trust.json"
TRUST_MIN = 0.7                # a rule judged right on less than this share of its findings writes them as info
# 6 Nov 2026, round 2 (the calibration found a door 0.15000000000000036 m from its room miss a reach of
# 0.15000000000000002): every distance compared with a reach or a tolerance gets this much slack
EPS = 1e-6
SMALL_SAMPLE = 5               # a rule judged on fewer findings is marked small_sample in the trust file (reported)

# ------------------------------------------------------------------------------------------- 1. room type and area
# (sense type, min m2, max m2, reason). A room under half the minimum or over twice the maximum is a major finding,
# between that and the range a minor one. The ranges are what is built, not what a code demands: a reading outside
# them has almost always closed the wrong face or named it from the wrong text.
AREA_RANGES = {
    "lift": (1.0, 8.0, "a lift shaft holds a car of 4 to 21 persons: from about 1.0 x 1.0 m to 2.6 x 3.0 m"),
    "shaft": (0.1, 8.0, "an installation shaft is from a 30 x 40 cm riser to a few m2; a larger face named shaft has "
                        "taken in a room beside it"),
    "light_well": (0.5, 30.0, "a light or air well (ışıklık) is from a 0.7 x 0.7 m air shaft to about 5 x 6 m"),
    "wc": (0.8, 6.0, "a WC with a basin is from 0.8 x 1.0 m to about 2 x 3 m"),
    "bathroom": (1.0, 15.0, "a bathroom holds a shower or a bath, a basin and a WC: from a 1.0 x 1.1 m en-suite to "
                            "about 15 m2"),
    "shower": (0.8, 5.0, "a shower room is a 0.8 x 1.0 m cubicle to about 2 x 2.5 m"),
    "closet": (0.3, 12.0, "a closet, pantry or dressing room is from a 0.5 x 0.6 m cupboard to about 3 x 4 m"),
    "storage": (0.3, 60.0, "a storage room (depo) is a cupboard in a flat to a store room of a shop or a basement"),
    "fire_lobby": (2.0, 40.0, "a fire or safety lobby in front of a stair or a lift is about 2 to 40 m2"),
    "stair": (2.0, 40.0, "a stair core (one or two flights with their landings) is about 2 to 40 m2"),
    "kitchen": (3.0, 40.0, "a kitchen is a 1.8 x 1.8 m kitchenette to about 5 x 8 m"),
    "bedroom": (6.0, 40.0, "a bedroom holds a bed with access around it: about 6 to 40 m2"),
    "living": (8.0, 120.0, "a living room is about 8 to 120 m2"),
    "hall": (1.0, 60.0, "an entrance, a corridor or a floor hall is about 1 to 60 m2"),
    "garage": (12.0, 100.0, "a private garage holds one to four cars: about 12 to 100 m2"),
    "car_park": (12.0, 5000.0, "a car park (otopark) holds from one car to a whole basement of cars"),
    "technical": (1.0, 40.0, "a boiler, pump, electrical or lift machine room is about 1 to 40 m2"),
}
MAJOR_FACTOR = 2.0            # over this times the maximum, or under the minimum divided by it: major
AREA_TEXT_AGREES = 0.10       # a drawn area text within this share of the face: the drawing itself gives that room
                              # that size, so the reading follows its drawing (6 Nov 2026 calibration: a 43.5 m2
                              # bedroom drawn with its 43.5 m2 text is no reading error)
# The words that refine the schema's coarse room types (ASCII-folded lower case, ``B.fold_ascii``), the first match
# wins. Turkish words match at the start of a word (inflected forms count), the English ones as whole words.
SENSE_WORDS = (
    ("technical", r"(?<![a-z])(?:asansor\s*mak|makin?a?e?\s*dair|machine\s*room|motor\s*room|su\s*depo|water\s*tank"
                  r"|hidrofor|hidrafor|kazan|kalorifer|kat\s*kal|jenerator|trafo|elektrik\s*oda|teknik)"),
    ("light_well", r"(?<![a-z])(?:isiklik|aydinlik|aydinlatma|light\s*well|lightwell)"),
    ("lift", r"(?<![a-z])asansor|(?<![a-z])(?:lift|elevator)s?(?![a-z])"),
    ("fire_lobby", r"(?<![a-z])(?:yangin|guvenlik|duman)\s*(?:kacis\s*)?hol|(?<![a-z])(?:fire|smoke|safety)\s*lobby"),
    ("shelter", r"(?<![a-z])(?:siginak|shelter)"),
    ("car_park", r"(?<![a-z])(?:otopark|parking|car\s*park)"),
    ("shaft", r"(?<![a-z])(?:saft|saht|soh|baca|shaft|riser)"),
    # 6 Nov 2026 (calibration): a KİLER is a pantry in a flat and a cellar store in a basement (synthetic-03's 14 m2
    # ones): it is judged as a storage room, not as a closet
    ("closet", r"(?<![a-z])(?:vestiyer|gardirop|giyinme|soyunma|closet|wardrobe|dressing)"),
    ("shower", r"(?<![a-z])(?:dus|shower)(?![a-z])"),
)
_SENSE_RE = [(t, re.compile(p)) for t, p in SENSE_WORDS]
BATH_WORDS_RE = re.compile(r"(?<![a-z])(?:banyo|bath)")
# The schema types the ranges apply to (``B.ROOM_TYPES``); other, unknown, balcony, dining and prayer have no range.
TYPE_SENSE = {"lift": "lift", "shaft": "shaft", "wc": "wc", "bathroom": "bathroom", "storage": "storage",
              "stair": "stair", "kitchen": "kitchen", "bedroom": "bedroom", "living": "living", "hall": "hall",
              "garage": "garage", "technical": "technical"}

# ----------------------------------------------------------------------------------- 2. a label naming a larger face
SMALL_TYPES = ("lift", "shaft", "wc", "bathroom", "shower", "closet", "fire_lobby", "stair", "technical")
LARGER_FACE_FACTOR = 2.0      # a small room's face over this many times its type's maximum is a larger space it
                              # names (rule 1's major bound: rule 2 takes those rooms, saying more about them)
TEXT_IN_FACE_M = 0.05         # a text this far inside the face still counts as standing in it
# numbered parking bays ('OTO 1', 'P 12', 'PARK-3') show a car park around them
PARKING_BAY_RE = re.compile(r"^\s*(?:oto|park|p)\s*[-.]?\s*\d{1,3}\s*$")

# ------------------------------------------------------------------------------------- 3. frame walls, paper rooms
FRAME_TOL_M = 0.10            # a wall's outer face this close to the region box's edge lies on it
FRAME_SHARE_MIN = 0.60        # frame walls covering this share of the box perimeter: the sheet frame read as walls
PAPER_ROOM_SHARE = 0.70       # a room covering more than this share of the region box is the sheet, not a room
PAPER_ENCLOSED_SHARE = 0.60   # a room with this share of its outline on frame walls is enclosed by the frame
FRAME_REACH_M = 0.15          # a room's outline this far beyond a frame wall's half thickness runs along it
# 6 Nov 2026 (calibration on 41 readings): a region box cut tight around a building puts its real outer walls on the
# box edges too (real02, the synthetic plans: 99 % of the perimeter). Real outer walls carry windows and doors and
# the inner walls end on them; a sheet frame has no opening and no wall ends on it (real19: 0 openings, 0 or 1 of 80
# walls). So the edge walls are a frame only with at most FRAME_OPENINGS_MAX openings and FRAME_JOINS_MAX joins.
FRAME_OPENINGS_MAX = 0        # openings on the edge walls of a frame
FRAME_JOINS_MAX = 2           # other walls with an end on the edge walls of a frame
JOIN_REACH_M = 0.30           # a wall end this close to an edge wall's centre line ends on it
# 6 Nov 2026 (calibration: synthetic-21's 83 m2 roof terrace fills 77 % of a tight box): a room covering most of
# the box is paper only when the labels of other rooms stand in it (real15: 24 labels in one 1257 m2 'Mutfak')
PAPER_LABELS_MIN = 2          # other room labels inside a room covering most of the box

# ------------------------------------------------------------------------------------------------ 4. unread walls
LABELS_MIN = 5                # more labels than this before the counts mean anything
OUTSIDE_SHARE_MAX = 1.0 / 3.0  # more than this share of the labels outside every room: the walls around them unread
LABEL_MERGE_M = 0.8           # label texts closer than this are one label (a name written on two lines)
# 6 Nov 2026 (calibration: real17's ground floor, 49 walls read, has its buried water tank and its entrance named
# outside the building): with at least WALLS_PER_LABEL walls a label the reading's walls do not surround (their hull,
# HULL_GROW_M wider) is a site note, not a room the walls missed. A floor read well has 3 to 6 wall pieces per room.
WALLS_PER_LABEL = 3
HULL_GROW_M = 0.5

# -------------------------------------------------------------------------------------------------- 5. circulation
STAIR_REACH_M = 1.5           # the stairs of two neighbouring levels this close in plan are one stair
ROOM_REACH_M = 0.10           # an opening belongs to a room whose polygon is this close beyond its wall's half
                              # thickness (crossdoc.ROOM_OPENING_REACH_M)
# 6 Nov 2026 (calibration): only the rooms people use every day must show a door: the dwelling rooms, the baths, the
# halls, the stairs, a lift and a garage. Service rooms (storage, technical rooms, shelters, water tanks, shafts,
# light wells) are often drawn without their door on basement and service plans (real16's shelters and technical rooms:
# no door drawn) and a room the reading could not type may be a light well (real21's AYDINLIK) or a stair core.
DOOR_TYPES = ("living", "bedroom", "kitchen", "bathroom", "shower", "wc", "hall", "fire_lobby", "stair", "lift",
              "garage")
NO_DOOR_AREA_M2 = 1.0         # no face under this needs a door (a riser, a column casing, a sliver between two walls)
ENTRANCE_LEVEL_M = 1.6        # an outer door on a level this close to the ground (0.0) is an entrance
STAIR_PIECE_REACH_M = 0.5     # a stair piece this close to a room belongs to it (the flat's own stair)
UNTYPED_CORE_M2 = 6.0         # an untyped room this large in a group with no way in is named as its likely hall

# ---------------------------------------------------------------------------------------------- 6. label vocabulary
# 6 Nov 2026: the notation phrases a reading glued to room names. No table of these exists in the reader (the title
# words are ``wenart.sheets.titles``, the area and flat notes ``wenart.ingest.generic.labels.is_annotation``, the level
# words ``wenart.sheets.levels``; they are imported, not copied). (pattern on ASCII-folded upper text, what it is)
NOTATION_PHRASES = (
    (r"\b(?:BINA\s+)?TABAN\s+HATTI\b", "the building's footprint line"),
    (r"\bTESISAT\s+DUVARI\b", "a services wall note"),
    (r"\bSACAK(?:\s+IZDUSUMU)?\b", "the eaves (projection line)"),
    (r"\bIZDUSUM\w*\b", "a projection line of the floor above"),
    (r"\bKOTU?\b", "a level mark"),
    (r"\bAKS(?:I|LARI)?\b", "an axis"),
    (r"\bSUBASMAN\b", "the plinth line"),
    (r"\bDILATASYON\b", "an expansion joint"),
    (r"\bPARAPET\b", "a parapet"),
    (r"\bH\s*[:=]\s*\d", "a height note"),
    (r"(?:^|\s)[+\-±]\s*\d+[.,]\d{2}\b", "a level value"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:CM|MM|M2|M²|M)(?![A-Z0-9])", "a number with a unit"),
)
_NOTATION_RE = [(re.compile(p), what) for p, what in NOTATION_PHRASES]

# ------------------------------------------------------------------------- round 2 (6 Nov 2026): the user's past fixes
# The classes of the user's 3-4 Nov corrections the first six rules missed (the independent recall measure: 7 of 24).
# 7. facade_recess (C0003, C0023, C0037): a recess of the facade closed into small unnamed rooms by a wall drawn across
#    its mouth; open air the model makes a room
RECESS_AREA_M2 = 7.0          # a recess room is smaller than this (real10's two recess rooms: 6.23 and 2.03 m2)
RECESS_MIN_AREA_M2 = 1.0      # ... and larger than this (a smaller face is wall mass, rule 12)
RECESS_MOUTH_SHARE = 0.6      # a gap in the outer wall this wide against the room's side there is the recess's mouth
RECESS_FACADE_M = 1.0         # a mouth opening onto no room this close to the level's outline opens onto the facade
                              # (calibration: real10 draws its facade with a second line 0.5 m out; a gap of the core
                              # onto unread space deep inside the plan is no mouth)
                              # (the user, C0037: "reached only through a facade gap as wide as itself")
# 8. false_stair (C0007): a tile grid read as a stair in a bathroom or a kitchen
FALSE_STAIR_ROOMS = ("bathroom", "wc", "shower", "kitchen")   # no stair stands in a wet room or a kitchen
STAIR_MIN_AREA_M2 = 1.8       # the smallest stair (a spiral of 1.3 m across, a straight flight 0.7 x 2.6 m)
STAIR_MIN_TREADS = 8          # a storey needs 14 to 20 risers; under this many tread lines, with another sign, no stair
GRID_FLIGHTS_MIN = 3          # a stair read with this many flights or more ...
FLIGHT_MIN_AREA_M2 = 2.0      # ... and less footprint than this per flight is a grid of lines (real09's kitchen tiles:
                              # 8 'flights' of 5 lines in 2.67 m2; no stair of the current readings has 3 flights)
# 9. stair_stacking (C0009, C0010): the core stair of one floor off the one below
STACK_OFFSET_M = 1.0          # one core stair on each of two neighbouring floors further apart than this in plan
                              # (the gap between their footprints: calibration, 6 Nov 2026: real13 and real19 read a
                              # different flight of the same U stair on each floor, centres 1.7 to 3.6 m apart, the
                              # footprints overlapping)
# 10. mirror_twins (C0004, C0018): the two halves of a mirrored plan read differently
TWIN_AREA_SHARE = 0.25        # twin rooms differing in area by more than this share of the larger one
TWIN_IOU_MIN = 0.5            # a room and the mirror image of another overlapping this much are twins
TWIN_MIN_AREA_M2 = 1.0        # rooms smaller than this are not paired about an axis (slivers, risers)
TWIN_IMAGE_READ_SHARE = 0.8   # a room's mirror image this much covered by other rooms: the other half is read there
TWIN_REGION_GROW_M = 1.0      # about the reading's own axis, only rooms within its twins' box (this much wider)
CORE_TYPES = ("lift", "stair", "shaft", "fire_lobby", "light_well", "technical")   # the user, C0027: "the core stays
                              # out of every mirror fix": a building's one lift or stair has no twin
# 6 Nov 2026 (calibration): an axis searched from the walls' own symmetry (as the round-2 request allowed) paired a
# salon with a bedroom in single houses, real14's one flat about its corridor and real03's different flat types (A1,
# A3, B): no right finding. Only the reading's own axis (its twins' transform, a label mirrored) is used, and its pairs
# count only when most of them have one type
TWIN_TYPE_AGREE_MIN = 0.6     # share of the pairs (the reading's own included) with one type
# 11. wall_across_passage (C0051, C0053): a drawn open passage walled with a gap left in it
PASSAGE_GAP_M = (0.7, 2.5)    # an unclassified gap this wide between a hall and a room
DOOR_SYMBOL_REACH_M = 1.0     # a door symbol this close to the gap makes it a door, not a passage
PASSAGE_OPEN_TYPES = ("stair", "lift", "shaft", "light_well")   # gaps onto these are no walled passage
# 12. wall_mass (C0020): a face of wall mass (or a closet the walls swallowed) typed as a hall or left untyped
WALL_MASS_FACE_M2 = 0.6       # a face under this typed hall or unknown is no room


def _finding(rule: str, severity: str, level: Optional[str], message: str, place=None,
             element_ids: Optional[list] = None, **extra) -> dict:
    out = {"check": CHECK, "name": NAME, "rule": rule, "severity": severity, "level_id": level, "message": message,
           "place": None, "element_ids": list(element_ids or []), "advisory": True}
    if place is not None:
        out["place"] = [round(float(place[0]), 2), round(float(place[1]), 2)]
    out.update(extra)
    return out


# --------------------------------------------------------------------------------------------------------- helpers
def _fold(text) -> str:
    return " ".join(B.fold_ascii(str(text or "")).split())


def _label(room: dict) -> str:
    return str(room.get("label") or room.get("label_raw") or "")


def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    p = Polygon([tuple(q[:2]) for q in points]).buffer(0)
    if p.is_empty:
        return None
    if p.geom_type == "MultiPolygon":
        p = max(p.geoms, key=lambda g: g.area)
    return p


def _area(room: dict) -> Optional[float]:
    a = room.get("area_computed")
    if isinstance(a, (int, float)):
        return float(a)
    p = _poly(room.get("polygon"))
    return p.area if p is not None else None


def _centre(room: dict) -> Optional[tuple]:
    p = _poly(room.get("polygon"))
    if p is None:
        return None
    c = p.representative_point()
    return (c.x, c.y)


def _rooms_of(building: dict, lid: str) -> list:
    return [r for r in building.get("rooms") or [] if r.get("level_id") == lid]


def _walls_of(building: dict, lid: str) -> list:
    return [w for w in building.get("walls") or [] if w.get("level_id") == lid and w.get("start") and w.get("end")]


def _wall_len(w: dict) -> float:
    return math.dist(w["start"][:2], w["end"][:2])


def _untyped(room: dict) -> bool:
    """A room the reading could not type: no label, a generic one ('Oda', 'Room') or the type unknown or other."""
    label = _label(room)
    return not label or B.generic_room_label(label) or room.get("room_type") in ("unknown", "other", None)


def _fmt(a: float) -> str:
    return f"{a:.1f}" if a >= 10 else f"{a:.2f}"


def _is_roof(level: Optional[dict]) -> bool:
    """A roof terrace floor (``wenart.sheets.titles.level_of`` of its label: TERAS KATI, ROOF TERRACE ...)."""
    from wenart.sheets import titles as T

    if not level:
        return False
    if level.get("kind") == "roof_terrace":
        return True
    lw = T.level_of(str(level.get("label") or ""))
    return lw is not None and lw.kind == "roof_terrace"


def sense_type(room: dict, roof: bool = False) -> Optional[str]:
    """The type a room's area is judged by (pure): the reading's ``room_type`` refined by its label's words
    (``SENSE_WORDS``): a void (``B.is_void_label``) has none; a ``shaft`` named as a lift, a light well or a machine
    room is that; a ``hall`` named as a fire or smoke lobby is a fire lobby; a ``bathroom`` named only by a shower word
    is a shower; a ``wc`` named with a bath word is a bathroom; ``storage`` named as a shelter has no range, as a pantry
    or a wardrobe a closet, as a water tank a technical room; a ``garage`` named as a car park is a car park. Rooms of
    type other, unknown, balcony, dining or prayer have none. ``roof``: the room stands on a roof terrace floor, where
    the lift's room above its last stop is its machine room (6 Nov 2026 calibration: real10's 13.3 m2 'Asansör
    Mahali' on the roof terrace is drawn so)."""
    label = _label(room)
    if B.is_void_label(label):
        return None
    rtype = room.get("room_type")
    folded = _fold(label)
    word = next((t for t, rx in _SENSE_RE if rx.search(folded)), None)
    if rtype == "shaft":
        if word == "lift" and roof:
            return "technical"
        return word if word in ("lift", "light_well", "technical") else "shaft"
    if rtype == "stair":
        return "light_well" if word == "light_well" else "stair"
    if rtype == "hall":
        return "fire_lobby" if word == "fire_lobby" else "hall"
    if rtype == "bathroom":
        return "shower" if word == "shower" and not BATH_WORDS_RE.search(folded) else "bathroom"
    if rtype == "wc":
        return "bathroom" if BATH_WORDS_RE.search(folded) else "wc"
    if rtype == "storage":
        if word == "shelter":
            return None
        return word if word in ("closet", "technical") else "storage"
    if rtype == "garage":
        return "car_park" if word == "car_park" else "garage"
    if rtype == "technical":
        return "technical"
    return TYPE_SENSE.get(rtype)


# ------------------------------------------------------------------------------------------- 1. room type and area
def stairs_in(building: dict, room: dict) -> list:
    """The ids of the stair pieces whose footprint centre stands in the room's polygon (pure)."""
    poly = _poly(room.get("polygon"))
    if poly is None:
        return []
    return [f.get("id") for f in building.get("furniture") or [] if f.get("level_id") == room.get("level_id")
            and f.get("type") == "stair" for fp in [_footprint(f)] if fp is not None and poly.contains(fp.centroid)]


def area_text_agrees(room: dict, area: float) -> bool:
    """True when the room's drawn area text (``area_label``) is within ``AREA_TEXT_AGREES`` of its area: the drawing
    itself gives that room that size."""
    lab = room.get("area_label")
    return isinstance(lab, (int, float)) and lab > 0 and abs(lab - area) <= AREA_TEXT_AGREES * max(lab, area)


def room_type_area(building: dict, skip: Optional[set] = None) -> list:
    """Rule 1 (pure): every room whose sense type's ``AREA_RANGES`` does not hold its area, unless its drawn area
    text agrees (``area_text_agrees``); major beyond ``MAJOR_FACTOR``; a stair piece standing in a lift's or a
    shaft's face is named (the stair core named after the lift beside it). ``skip``: room ids another rule already
    named (rule 2 says more about them)."""
    out = []
    roofs = {lv["id"] for lv in building.get("levels") or [] if _is_roof(lv)}
    for r in building.get("rooms") or []:
        if skip and r.get("id") in skip:
            continue
        st = sense_type(r, roof=r.get("level_id") in roofs)
        a = _area(r)
        if st is None or st not in AREA_RANGES or a is None or a <= 0:
            continue
        lo, hi, why = AREA_RANGES[st]
        if lo <= a <= hi or area_text_agrees(r, a):
            continue
        sev = "major" if (a > MAJOR_FACTOR * hi or a < lo / MAJOR_FACTOR) else "minor"
        side = f"over the {_fmt(hi)} m2 a {st.replace('_', ' ')} has at most" if a > hi else \
            f"under the {_fmt(lo)} m2 a {st.replace('_', ' ')} has at least"
        lab = f" (drawn area text {r['area_label']:g} m2)" if isinstance(r.get("area_label"), (int, float)) else ""
        stairs = stairs_in(building, r) if st in ("lift", "shaft") and a > hi else []
        also = (f"; the stair {', '.join(stairs)} stands in it (the stair core is named after the {st})"
                if stairs else "")
        out.append(_finding("room_type_area", sev, r.get("level_id"),
                            f"{r.get('id')} '{_label(r)}' (type {r.get('room_type')}) is {_fmt(a)} m2{lab}, {side} "
                            f"({why}){also}: the face or the name is wrong",
                            _centre(r), [r.get("id")], sense_type=st, area_m2=round(a, 3), range_m2=[lo, hi]))
    return out


# ----------------------------------------------------------------------------------- 2. a label naming a larger face
def _own_entities(room: dict) -> set:
    """The text entities of the room's own label: its evidence items whose text is part of its label (a reading may
    list every label of a merged face in the evidence: real15's 'Mutfak' carries TERAS, GARAJ, SALON ...)."""
    name = " ".join(_fold(f"{room.get('label_raw') or ''} {room.get('label') or ''}").upper().split())
    out = set()
    for e in room.get("evidence") or []:
        if not isinstance(e, dict) or not e.get("entity") or not e.get("text"):
            continue
        text = " ".join(_fold(e["text"]).upper().split())
        if text and (text in name or _is_area_text(text)):
            out.update(str(e["entity"]).split(","))
    return out


def _is_area_text(text: str) -> bool:
    from wenart.reading_check import AREA_RE

    return bool(AREA_RE.search(text))


def _texts_in(poly: Polygon, texts: list, own: set) -> list:
    inner = poly.buffer(-TEXT_IN_FACE_M + EPS) if poly.area > 1.0 else poly.buffer(EPS)
    return [t for t in texts if t.get("entity") not in own and inner.contains(Point(t["x"], t["y"]))]


def _larger_type(text: str) -> Optional[str]:
    """The sense type a text inside a face names, when it is a space larger than the small rooms (a car park, a
    shelter, a living room, a garage, a shop): ``None`` for a small room's word or a text naming no room."""
    folded = _fold(text)
    if PARKING_BAY_RE.match(folded):
        return "car_park"
    word = next((t for t, rx in _SENSE_RE if rx.search(folded)), None)
    if word in ("car_park", "shelter"):
        return word
    if word is not None:
        return None
    rtype = B.room_type_for(text)
    return rtype if rtype in ("living", "garage", "bedroom", "kitchen", "dining") else None


def label_names_larger_face(building: dict, texts_by_level: Optional[dict] = None) -> list:
    """Rule 2 (pure): a room of a small type (``SMALL_TYPES``) whose face is at least ``LARGER_FACE_FACTOR`` times its
    type's maximum: its label names a small room inside a larger space whose walls were not read apart (major). The
    other labels inside the face are named with it: the level's texts (``texts_by_level``: ``{level: [{text, x, y,
    entity}]}`` in building metres, the room's own label texts left out), its labels in no closed face
    (``reading_places``), numbered parking bays (``PARKING_BAY_RE``) and, in a face named other than a stair or a
    fire lobby, the stair pieces standing in it (a lift's label naming the stair core around it)."""
    out = []
    roofs = {lv["id"] for lv in building.get("levels") or [] if _is_roof(lv)}
    places = {lv["id"]: [{"text": p.get("text"), "x": p["at"][0], "y": p["at"][1], "entity": None}
                         for p in lv.get("reading_places") or [] if p.get("at")]
              for lv in building.get("levels") or []}
    for r in building.get("rooms") or []:
        st = sense_type(r, roof=r.get("level_id") in roofs)
        a = _area(r)
        if st not in SMALL_TYPES or a is None:
            continue
        hi = AREA_RANGES[st][1]
        if a < LARGER_FACE_FACTOR * hi:
            continue
        poly = _poly(r.get("polygon"))
        lid = r.get("level_id")
        others = []
        if poly is not None:
            texts = list((texts_by_level or {}).get(lid) or []) + places.get(lid, [])
            for t in _texts_in(poly, texts, _own_entities(r)):
                kind = _larger_type(t.get("text"))
                if kind:
                    others.append((t["text"].strip(), kind))
            if st not in ("stair", "fire_lobby"):
                others += [(sid, "stair") for sid in stairs_in(building, r)]
        seen, names = set(), []
        for text, kind in others:
            if text not in seen:
                seen.add(text)
                names.append(f"the stair {text}" if kind == "stair" else f"'{text}' ({kind.replace('_', ' ')})")
        other_txt = (f"; inside the same face stand {', '.join(names[:6])}: the face is that space and the label "
                     f"names a small room in it") if names else "; no other label stands in the face"
        out.append(_finding("label_names_larger_face", "major", lid,
                            f"{r.get('id')} '{_label(r)}' names a {st.replace('_', ' ')} (at most {_fmt(hi)} m2) but "
                            f"its face is {_fmt(a)} m2, {a / hi:.1f} times that{other_txt}; the walls between them "
                            f"are not read", _centre(r), [r.get("id")], sense_type=st, area_m2=round(a, 3),
                            other_labels=[t for t, _ in others][:12]))
    return out


# ------------------------------------------------------------------------------------- 3. frame walls, paper rooms
def _apply(tf, p) -> tuple:
    return (tf[0] * p[0] + tf[1] * p[1] + tf[2], tf[3] * p[0] + tf[4] * p[1] + tf[5])


def region_boxes(building: dict) -> dict:
    """``{level_id: Polygon}`` (pure): each level's region box (``documents[].pages[].region_box``, drawing units)
    mapped to building metres by the page's ``transform_to_building``; levels read from a whole drawing have none."""
    out = {}
    for doc in building.get("documents") or []:
        for pg in doc.get("pages") or []:
            lid, box, tf = pg.get("level_id"), pg.get("region_box"), pg.get("transform_to_building")
            if not lid or lid in out or not box or not tf or len(box) != 4:
                continue
            x0, y0, x1, y1 = box
            out[lid] = Polygon([_apply(tf, q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))])
    return out


def frame_evidence(walls: list, ids: list, openings: list) -> tuple[int, int]:
    """``(openings, joins)`` (pure): the openings (not virtual) on the walls ``ids`` and the other walls with an end
    within ``JOIN_REACH_M`` of them: a building's outer walls have both, a sheet frame neither."""
    ids = set(ids)
    lines = [LineString([w["start"][:2], w["end"][:2]]) for w in walls if w.get("id") in ids]
    n_open = sum(1 for o in openings if o.get("wall_id") in ids and not o.get("virtual"))
    joins = 0
    for w in walls:
        if w.get("id") in ids:
            continue
        if any(ln.distance(Point(e[:2])) <= JOIN_REACH_M + EPS for e in (w["start"], w["end"]) for ln in lines):
            joins += 1
    return n_open, joins


def frame_walls(walls: list, box: Polygon) -> tuple[list, float]:
    """``(wall ids, share)`` (pure): the walls whose outer face lies on an edge of the box within ``FRAME_TOL_M``
    (both ends; the face is the centre line moved out by half the thickness) and the share of the box perimeter their
    projections cover."""
    pts = list(box.exterior.coords)[:-1]
    ids, covered = [], 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        edge = LineString([a, b])
        if edge.length <= 0:
            continue
        spans = []
        for w in walls:
            reach = FRAME_TOL_M + float(w.get("thickness") or 0.0) / 2.0
            p, q = Point(w["start"][:2]), Point(w["end"][:2])
            if edge.distance(p) > reach + EPS or edge.distance(q) > reach + EPS or p.distance(q) < 0.3:
                continue
            # the line through the edge, not only the segment: a wall a little longer than the box still lies on it
            s, t = sorted((edge.project(p), edge.project(q)))
            spans.append((max(0.0, s), min(edge.length, t)))
            if w.get("id") not in ids:
                ids.append(w.get("id"))
        spans.sort()
        run_end = -1.0
        for s, t in spans:
            if t <= run_end:
                continue
            covered += t - max(s, run_end)
            run_end = t
    return ids, (covered / box.length if box.length > 0 else 0.0)


def frame_walls_and_paper_rooms(building: dict, texts_by_level: Optional[dict] = None) -> list:
    """Rule 3 (pure): per level with a region box, the walls on its edges covering ``FRAME_SHARE_MIN`` of its
    perimeter with no more than ``FRAME_OPENINGS_MAX`` openings and ``FRAME_JOINS_MAX`` walls ending on them
    (``frame_evidence``; one major finding naming them); every room with ``PAPER_ENCLOSED_SHARE`` of its outline
    along those frame walls, or covering more than ``PAPER_ROOM_SHARE`` of the box with at least ``PAPER_LABELS_MIN``
    other rooms' labels standing in it (``texts_by_level`` and the level's ``reading_places``; a major finding each)."""
    out = []
    boxes = region_boxes(building)
    places = {lv["id"]: [{"text": p.get("text"), "x": p["at"][0], "y": p["at"][1], "entity": None}
                         for p in lv.get("reading_places") or [] if p.get("at")]
              for lv in building.get("levels") or []}
    for lid, box in boxes.items():
        if box.area <= 0:
            continue
        walls = _walls_of(building, lid)
        ids, share = frame_walls(walls, box)
        frame, joins = [], 0
        if share >= FRAME_SHARE_MIN:
            ops = [o for o in building.get("openings") or [] if o.get("level_id") == lid]
            n_open, joins = frame_evidence(walls, ids, ops)
            if n_open <= FRAME_OPENINGS_MAX and joins <= FRAME_JOINS_MAX:
                frame = [w for w in walls if w.get("id") in ids]
        if frame:
            lens = sorted((_wall_len(w) for w in frame), reverse=True)
            c = box.centroid
            out.append(_finding("frame_walls_and_paper_rooms", "major", lid,
                                f"{lid}: {len(frame)} walls ({', '.join(f'{x:.2f}' for x in lens[:4])} m ...) lie on "
                                f"the edges of the drawing's region box and cover {share * 100:.0f} % of its "
                                f"perimeter, with no opening and {joins} other wall(s) ending on them: the sheet frame "
                                f"is read as walls", (c.x, c.y), [w.get("id") for w in frame],
                                frame_share=round(share, 3), joins=joins))
        frame_union = unary_union([LineString([w["start"][:2], w["end"][:2]]).buffer(
            float(w.get("thickness") or 0.1) / 2.0 + FRAME_REACH_M, cap_style=2) for w in frame]) if frame else None
        for r in _rooms_of(building, lid):
            poly = _poly(r.get("polygon"))
            if poly is None:
                continue
            cover = poly.area / box.area
            along = (poly.exterior.intersection(frame_union).length / poly.exterior.length
                     if frame_union is not None and poly.exterior.length > 0 else 0.0)
            inner = []
            if cover > PAPER_ROOM_SHARE:
                texts = list((texts_by_level or {}).get(lid) or []) + places.get(lid, [])
                own = {_fold(_label(r)).upper()} | {_fold(w).upper() for w in _label(r).split()}
                for t in _texts_in(poly, texts, _own_entities(r)):
                    name = str(t.get("text") or "").strip()
                    if _is_room_label(name) and _fold(name).upper() not in own \
                            and not any(math.dist((t["x"], t["y"]), (q[1], q[2])) < LABEL_MERGE_M + EPS
                                        for q in inner):
                        inner.append((name, t["x"], t["y"]))
            papered = cover > PAPER_ROOM_SHARE and len(inner) >= PAPER_LABELS_MIN
            if not papered and along < PAPER_ENCLOSED_SHARE:
                continue
            why = (f"covers {cover * 100:.0f} % of the region box ({box.area:.0f} m2) and holds {len(inner)} other "
                   f"rooms' labels ({', '.join(repr(t[0]) for t in inner[:5])}{' ...' if len(inner) > 5 else ''})"
                   if papered else f"runs along the frame walls for {along * 100:.0f} % of its outline")
            lab = f", drawn area text {r['area_label']:g} m2" if isinstance(r.get("area_label"), (int, float)) else ""
            out.append(_finding("frame_walls_and_paper_rooms", "major", lid,
                                f"{r.get('id')} '{_label(r)}' ({poly.area:.0f} m2{lab}) {why}: a room of paper (the "
                                f"sheet or its frame closed as a room, named from a sheet text)", _centre(r),
                                [r.get("id")], cover_share=round(cover, 3), frame_share=round(along, 3)))
    return out


# ------------------------------------------------------------------------------------------------ 4. unread walls
def _is_room_label(text: str) -> bool:
    """A text naming a room (``wenart.ingest.generic.labels``: a room keyword, at most five words, no length), not an
    area note or a drawing title."""
    from wenart.ingest.generic import labels as LB

    if not text or LB.is_drawing_title(text) or LB.is_annotation(text):
        return False
    return bool(LB.room_name_runs([SimpleNamespace(text=text)]))


def level_labels(building: dict, lid: str, texts: Optional[list] = None) -> list:
    """The room labels of a level (pure): ``[(text, x, y)]`` in building metres, labels written on two lines merged
    (``LABEL_MERGE_M``). From the level's texts when given (``texts``), else (or when none names a room) from its rooms
    (their centre) and its labels in no closed face (``reading_places``)."""
    raw = []
    if texts:
        raw = [(t["text"], t["x"], t["y"]) for t in texts if _is_room_label(t.get("text"))]
    if not raw:                       # no texts, or none of them names a room (names kept in block attributes)
        for r in _rooms_of(building, lid):
            c = _centre(r)
            if c is not None and _label(r) and not B.generic_room_label(_label(r)):
                raw.append((_label(r), c[0], c[1]))
        lv = next((x for x in building.get("levels") or [] if x.get("id") == lid), {}) or {}
        raw += [(p.get("text") or "", p["at"][0], p["at"][1]) for p in lv.get("reading_places") or []
                if p.get("at") and p.get("kind", "unplaced_label") == "unplaced_label"]
    out: list = []
    for t, x, y in raw:
        if any(math.dist((x, y), (q[1], q[2])) < LABEL_MERGE_M + EPS for q in out):
            continue
        out.append((t, x, y))
    return out


def unread_walls(building: dict, texts_by_level: Optional[dict] = None) -> list:
    """Rule 4 (pure): a level (not a typical floor's copy) with more than ``LABELS_MIN`` room labels and fewer walls
    than labels, or more than ``OUTSIDE_SHARE_MAX`` of its labels outside every room and every outdoor space of the
    level (with ``WALLS_PER_LABEL`` walls per label or more, only the labels inside the walls' hull count): its walls
    are mostly unread, or read but open around the rooms (major, with the counts)."""
    out = []
    site = building.get("site") or {}
    for lv in building.get("levels") or []:
        lid = lv["id"]
        if lv.get("typical_of") and lv.get("typical_of") != lid:
            continue
        labels = level_labels(building, lid, (texts_by_level or {}).get(lid))
        if len(labels) <= LABELS_MIN:
            continue
        walls = _walls_of(building, lid)
        rooms = _rooms_of(building, lid)
        spaces = [p for p in (_poly(r.get("polygon")) for r in rooms) if p is not None]
        spaces += [p for p in (_poly(s.get("polygon")) for s in site.get("outdoor_spaces") or []
                               if s.get("level_id") == lid) if p is not None]
        inside = unary_union([p.buffer(0.1) for p in spaces]) if spaces else None
        outside = [t for t in labels if inside is None or not inside.contains(Point(t[1], t[2]))]
        if walls and len(walls) >= WALLS_PER_LABEL * len(labels):
            pts = [tuple(w[k][:2]) for w in walls for k in ("start", "end")]
            hull = unary_union([Point(q) for q in pts]).convex_hull.buffer(HULL_GROW_M)
            outside = [t for t in outside if hull.contains(Point(t[1], t[2]))]
        few = len(walls) < len(labels)
        share = len(outside) / len(labels)
        if not few and share <= OUTSIDE_SHARE_MAX:
            continue
        reasons = []
        if few:
            reasons.append(f"{len(walls)} walls for {len(labels)} room labels")
        if share > OUTSIDE_SHARE_MAX:
            reasons.append(f"{len(outside)} of {len(labels)} labels ({share * 100:.0f} %) outside every room")
        names = sorted({t[0] for t in outside})[:8]
        xs, ys = [t[1] for t in outside or labels], [t[2] for t in outside or labels]
        what = ("the walls of this floor are mostly not read (hatch-drawn or on an unread layer)"
                if len(walls) < WALLS_PER_LABEL * len(labels) else
                "its walls are read but do not close around the rooms (gaps, a frame or open joints)")
        out.append(_finding("unread_walls", "major", lid,
                            f"{lid} {lv.get('label') or ''}: " + "; ".join(reasons) + f" ({len(rooms)} rooms closed)"
                            + (f", e.g. {', '.join(repr(n) for n in names)}" if names else "") + f": {what}",
                            (sum(xs) / len(xs), sum(ys) / len(ys)), [], labels=len(labels), walls=len(walls),
                            rooms=len(rooms), labels_outside=len(outside)))
    return out


# -------------------------------------------------------------------------------------------------- 5. circulation
def _footprint(f: dict) -> Optional[Polygon]:
    fp = f.get("footprint") or {}
    if not fp.get("center") or not fp.get("size"):
        return None
    cx, cy = fp["center"][:2]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    r = math.radians(float(fp.get("rotation_deg") or 0.0))
    pts = [(cx + sx * w / 2 * math.cos(r) - sy * d / 2 * math.sin(r), cy + sx * w / 2 * math.sin(r)
            + sy * d / 2 * math.cos(r)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    return Polygon(pts)


def stairs_of(building: dict, lid: str) -> list:
    """``[(id, Polygon)]`` (pure): the level's stair rooms and stair pieces."""
    out = [(r.get("id"), p) for r in _rooms_of(building, lid) if sense_type(r) == "stair"
           for p in [_poly(r.get("polygon"))] if p is not None]
    out += [(f.get("id"), p) for f in building.get("furniture") or []
            if f.get("level_id") == lid and f.get("type") == "stair" for p in [_footprint(f)] if p is not None]
    return out


def _el(lv: dict) -> float:
    v = lv.get("elevation")
    if isinstance(v, dict):
        v = v.get("value")
    return float(v) if isinstance(v, (int, float)) else float(lv.get("order") or 0) * 3.0


def base_levels_by_height(building: dict) -> list:
    """The base levels (``base_level_id`` null) by elevation (pure)."""
    return sorted((lv for lv in building.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (_el(lv), lv.get("order") or 0))


def core_stairs(building: dict, lid: str, false_ids: Optional[set] = None) -> list:
    """``[(id, Polygon)]`` (pure): the level's stair pieces that are no false stair (``false_ids``, rule 8); the stair
    rooms when the level has no such piece (a stair read as a room only)."""
    pieces = [(f.get("id"), p) for f in building.get("furniture") or []
              if f.get("level_id") == lid and f.get("type") == "stair" and f.get("id") not in (false_ids or set())
              for p in [_footprint(f)] if p is not None]
    if pieces:
        return pieces
    return [(r.get("id"), p) for r in _rooms_of(building, lid) if sense_type(r) == "stair"
            for p in [_poly(r.get("polygon"))] if p is not None]


def stair_links(building: dict, false_ids: Optional[set] = None) -> list:
    """Rule 5a (pure): the base levels by elevation; for each two neighbours a stair on both within
    ``STAIR_REACH_M`` in plan (false stairs, ``false_ids``, left out: a tile grid read as a stair joins nothing). A
    level with no stair meeting its neighbour's is unreachable (major); no stair on any level is one minor finding (the
    stairs unread or not drawn). Two neighbours with exactly one core stair each are left to ``stair_stacking``."""
    levels = base_levels_by_height(building)
    if len(levels) < 2:
        return []
    stairs = {lv["id"]: core_stairs(building, lv["id"], false_ids) for lv in levels}
    if not any(stairs.values()):
        names = ", ".join(lv["id"] for lv in levels)
        return [_finding("circulation", "minor", None, f"no stair is read on any of the {len(levels)} levels "
                         f"({names}): the stairs are unread or not drawn", None, [], part="levels")]
    out = []
    for lo, hi in zip(levels, levels[1:]):
        if abs(_el(hi) - _el(lo)) < 0.5:
            continue
        a, b = stairs[lo["id"]], stairs[hi["id"]]
        if len(a) == 1 and len(b) == 1:
            continue                                                          # stair_stacking's question
        best = min((pa.distance(pb), ia, ib) for ia, pa in a for ib, pb in b) if a and b else None
        if best is not None and best[0] <= STAIR_REACH_M + EPS:
            continue
        if not a or not b:
            missing = [lv["id"] for lv, s in ((lo, a), (hi, b)) if not s]
            why = f"no stair is read on {' and '.join(missing)}"
            ids = [s[0] for s in a + b]
            place = None
            for _, p in a + b:
                place = (p.centroid.x, p.centroid.y)
                break
        else:
            why = f"the nearest stairs ({best[1]} and {best[2]}) are {best[0]:.1f} m apart in plan"
            ids = [best[1], best[2]]
            pa = next(p for i, p in a if i == best[1])
            place = (pa.centroid.x, pa.centroid.y)
        out.append(_finding("circulation", "major", hi["id"],
                            f"{hi['id']} {hi.get('label') or ''} cannot be reached from {lo['id']} "
                            f"{lo.get('label') or ''} by a stair: {why}", place, ids, part="levels",
                            levels=[lo["id"], hi["id"]]))
    return out


def opening_rooms(building: dict, lid: str) -> list:
    """``[(opening, wall, [room ids])]`` of a level (pure): every opening (doors, windows, openings, the virtual
    separators) with the rooms it touches: the opening's centre and its wall within half the wall's thickness plus
    ``ROOM_REACH_M`` of the room polygon, a separator's line within ``ROOM_REACH_M``."""
    polys = {r["id"]: p for r in _rooms_of(building, lid) for p in [_poly(r.get("polygon"))] if p is not None}
    walls = {w["id"]: w for w in _walls_of(building, lid)}
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != lid:
            continue
        if o.get("virtual"):
            if not o.get("line"):
                continue
            shape, reach, wall = LineString([tuple(p[:2]) for p in o["line"]]), ROOM_REACH_M, None
        else:
            wall = walls.get(o.get("wall_id"))
            if wall is None or not o.get("center"):
                continue
            reach = float(wall.get("thickness") or 0.1) / 2.0 + ROOM_REACH_M
            shape = Point(tuple(o["center"][:2]))
        line = LineString([wall["start"][:2], wall["end"][:2]]) if wall is not None else None
        touched = [rid for rid, poly in polys.items() if poly.distance(shape) <= reach + EPS
                   and (line is None or poly.distance(line) <= reach + EPS)]
        out.append((o, wall, touched))
    return out


def room_access(building: dict, lid: str) -> tuple[dict, list, dict, dict]:
    """``(access, links, outer, loose)`` of a level's rooms (pure): ``access[room] = [opening ids]`` (doors, openings
    and the virtual separators that touch the room: the opening's wall within half its thickness plus ``ROOM_REACH_M``
    of the polygon, a separator's line within ``ROOM_REACH_M``), ``links`` the pairs of rooms an opening joins,
    ``outer[room]`` the doors and openings on an exterior wall that touch only that room and ``loose[room]`` those on
    an inner wall that touch only that room (they lead into space no room closes)."""
    rooms = [r for r in _rooms_of(building, lid) if _poly(r.get("polygon")) is not None]
    access = {r["id"]: [] for r in rooms}
    links, outer, loose = [], {}, {}
    for o, wall, touched in opening_rooms(building, lid):
        if not o.get("virtual") and o.get("type") not in ("door", "opening"):
            continue
        for rid in touched:
            access[rid].append(o.get("id"))
        for i in range(len(touched)):
            for j in range(i + 1, len(touched)):
                links.append((touched[i], touched[j]))
        if len(touched) == 1 and wall is not None and wall.get("exterior"):
            outer.setdefault(touched[0], []).append(o.get("id"))
        elif len(touched) == 1 and wall is not None:
            loose.setdefault(touched[0], []).append(o.get("id"))
    return access, links, outer, loose


def circulation(building: dict, false_ids: Optional[set] = None) -> list:
    """Rule 5 (pure): the levels a stair joins (``stair_links``, major per unreachable level); per level every room
    of a type people use every day (``DOOR_TYPES``) with no door, opening or separator and no stair standing in it
    (minor; faces under ``NO_DOOR_AREA_M2`` and voids left out); every group of rooms joined by doors (a flat, two
    rooms or more, not the whole floor) with no door to a stair, a lift, a hall shared by the floor or, on a level near
    the ground (``ENTRANCE_LEVEL_M``), the outside (minor; its doors into unclosed space are named)."""
    out = stair_links(building, false_ids)
    for lv in building.get("levels") or []:
        lid = lv["id"]
        rooms = {r["id"]: r for r in _rooms_of(building, lid) if _poly(r.get("polygon")) is not None}
        if not rooms:
            continue
        access, links, outer, loose = room_access(building, lid)
        stair_polys = [p for _, p in stairs_of(building, lid)]
        for rid, r in rooms.items():
            st = sense_type(r, roof=_is_roof(lv))
            if access.get(rid) or st not in DOOR_TYPES or B.is_void_label(_label(r)):
                continue
            a = _area(r) or 0.0
            poly = _poly(r["polygon"])
            if a < NO_DOOR_AREA_M2 or any(poly.distance(sp) <= STAIR_PIECE_REACH_M + EPS for sp in stair_polys):
                continue                                         # a stair standing in a room is its way in
            out.append(_finding("circulation", "minor", lid, f"{rid} '{_label(r)}' ({_fmt(a)} m2, type "
                                f"{r.get('room_type')}) has no door, opening or open side read: it cannot be "
                                f"entered", _centre(r), [rid], part="room"))
        # groups of rooms joined by doors
        parent = {rid: rid for rid in rooms}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, b in links:
            if a in parent and b in parent:
                parent[find(a)] = find(b)
        groups: dict = {}
        for rid in rooms:
            groups.setdefault(find(rid), []).append(rid)
        near_ground = abs(_el(lv)) <= ENTRANCE_LEVEL_M + EPS
        entered = [rid for rid in rooms if access.get(rid)]
        for members in groups.values():
            # a group holding every room with a door is the whole floor: its way in is the stair rule's question
            if len(members) < 2 or len(members) >= len(entered):
                continue
            reached = False
            for rid in members:
                r = rooms[rid]
                st = sense_type(r, roof=_is_roof(lv))
                poly = _poly(r["polygon"])
                if st in ("stair", "lift", "fire_lobby") or (near_ground and outer.get(rid)):
                    reached = True
                elif any(poly.distance(sp) <= STAIR_PIECE_REACH_M + EPS for sp in stair_polys):
                    reached = True
                elif st == "hall" and re.search(r"(?<![a-z])(?:kat\s*hol|ortak|floor\s*hall|common|lobby|"
                                                r"apartman\s*hol|bina\s*giris)", _fold(_label(r))):
                    reached = True
                if reached:
                    break
            if reached:
                continue
            polys = [_poly(rooms[m]["polygon"]) for m in members]
            u = unary_union(polys)
            c = u.representative_point()
            names = ", ".join(f"'{_label(rooms[m])}'" for m in members[:8])
            doors_out = sorted({o for m in members for o in loose.get(m) or []})
            plural = len(doors_out) > 1
            # 6 Nov 2026, round 2 (calibration: real16's flats reach the floor's corridor and core, read as one untyped
            # 37.7 m2 'Oda'): an untyped room of the group is named as the likely hall or core
            # ... only when the group joins two flats or more (two kitchens or two living rooms): then the unnamed room
            # between them is their hall; in one flat an unnamed 'Oda' is a room of that flat
            kinds = [sense_type(rooms[m]) for m in members]
            flats = max(kinds.count("kitchen"), kinds.count("living"))
            untyped = [m for m in members if not _named(rooms[m]) and (_area(rooms[m]) or 0.0) >= UNTYPED_CORE_M2]
            if untyped and flats >= 2:
                big = max(untyped, key=lambda m: _area(rooms[m]) or 0.0)
                why = (f"the floor's hall or core seems to be the untyped room {big} '{_label(rooms[big])}' "
                       f"({_fmt(_area(rooms[big]) or 0.0)} m2): no stair, lift or hall is read in it")
            elif doors_out:
                why = (f"its door{'s' if plural else ''} {', '.join(doors_out[:4])} lead{'' if plural else 's'} into "
                       f"space no room closes (the hall or the stair behind is unread)")
            else:
                why = "its entrance door is not read"
            out.append(_finding("circulation", "minor", lid,
                                f"{lid}: a group of {len(members)} rooms joined by doors ({names}"
                                f"{' ...' if len(members) > 8 else ''}; {u.area:.0f} m2) has no door to a stair, a "
                                f"lift, the floor's shared hall" + (" or the outside" if near_ground else "")
                                + f": {why}",
                                (c.x, c.y), sorted(members), part="flat", loose_doors=doors_out))
    return out


# ---------------------------------------------------------------------------------------------- 6. label vocabulary
def notation_in(label: str) -> list:
    """The notation a room label holds (pure): ``[what]`` of the ``NOTATION_PHRASES`` it contains, a drawing title
    (``wenart.ingest.generic.labels.is_drawing_title``: a plan, section or elevation title, a scale note), an area or
    flat note (``labels.is_annotation``) and a floor's name read as the room's (``wenart.sheets.titles.level_of`` of
    the label with the word KAT: NORMAL, ZEMİN, BODRUM), when the label has no room word of its own."""
    from wenart.ingest.generic import labels as LB
    from wenart.sheets import titles as T

    if not label:
        return []
    folded = _fold(label).upper()
    found = [what for rx, what in _NOTATION_RE if rx.search(folded)]
    if LB.is_drawing_title(label):
        found.append("a drawing title")
    turkish, english = B.room_keyword_hits(label)
    if not turkish and not english:
        if LB.is_annotation(label):
            found.append("an area or flat note")
        elif not re.search(r"\d", folded) and not B.generic_room_label(label) \
                and T.level_of(f"{label} KAT") is not None:
            found.append("a floor's name")
    return list(dict.fromkeys(found))


def label_vocabulary(building: dict) -> list:
    """Rule 6 (pure): every room whose label holds a notation phrase (``notation_in``), glued to its name or alone
    (minor)."""
    out = []
    for r in building.get("rooms") or []:
        label = _label(r)
        found = notation_in(label)
        if not found:
            continue
        turkish, english = B.room_keyword_hits(label)
        how = "glued to the room's name" if (turkish or english) else "read as the room's name"
        out.append(_finding("label_vocabulary", "minor", r.get("level_id"),
                            f"{r.get('id')} '{label}': {', '.join(found)} {how}: a notation text of the drawing, not "
                            f"part of the room's name", _centre(r), [r.get("id")], notation=found))
    return out



# ------------------------------------------------------------------------- round 2 (6 Nov 2026): the user's past fixes
def _is_gap(o: dict) -> bool:
    """An opening the reading could not class (type opening, or a virtual separator): no door, no window."""
    return bool(o.get("virtual")) or o.get("type") == "opening"


def _named(room: dict) -> bool:
    """A room with a label of its own (not empty, not a generic 'Oda' / 'Room')."""
    label = _label(room)
    return bool(label) and not B.generic_room_label(label)


def _side_length(poly: Polygon, wall: dict) -> float:
    """The length of a room's outline along a wall (within half its thickness plus ``ROOM_REACH_M``)."""
    band = LineString([wall["start"][:2], wall["end"][:2]]).buffer(
        float(wall.get("thickness") or 0.1) / 2.0 + ROOM_REACH_M + EPS, cap_style=2)
    return poly.exterior.intersection(band).length / 2.0 if poly.exterior.intersects(band) else 0.0


def _level_outline(building: dict, lid: str):
    """The level's filled outer outline from its walls and openings (``crossdoc.level_outline``), or None."""
    from wenart.reading_check.crossdoc import level_outline

    try:
        return level_outline(_walls_of(building, lid), [o for o in building.get("openings") or []
                                                        if o.get("level_id") == lid])
    except Exception:  # noqa: BLE001 - no outline: only exterior walls count as the facade
        return None


def _beyond_outside(o: dict, w: dict, polys: list, outline, rooms_union=None) -> bool:
    """True when the point just beyond an opening, on the side away from the rooms it opens from, lies outside the
    level's outline or in no room (open air, or space the facade's second line closes: real10's recesses behind a
    double facade line)."""
    if not polys or not o.get("center"):
        return False
    (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 0:
        return False
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    cx, cy = o["center"][:2]
    c = unary_union(polys).centroid
    if (c.x - cx) * nx + (c.y - cy) * ny > 0:
        nx, ny = -nx, -ny
    reach = float(w.get("thickness") or 0.1) / 2.0 + 0.25
    q = Point(cx + nx * reach, cy + ny * reach)
    if outline is None:
        return False
    if not outline.buffer(-EPS).contains(q):
        return True
    # in no room and close to the outline: the strip between the two lines of a double facade
    return (rooms_union is not None and not rooms_union.buffer(EPS).contains(q)
            and outline.exterior.distance(q) <= RECESS_FACADE_M + EPS)


def facade_recess(building: dict) -> list:
    """Rule 7 (pure; C0003, C0023, C0037): a group of small unnamed rooms (each under ``RECESS_AREA_M2``, no label or a
    generic one; joined to each other by gaps) with no door, whose openings are unclassified gaps (type opening or a
    virtual separator) and windows of named rooms, with a mouth (a gap touching only the group in an exterior wall,
    with open air beyond the level's outline, or with no room beyond it within ``RECESS_FACADE_M`` of the outline), and
    either a window of a named room looking into it or the mouth as wide as the room's side (``RECESS_MOUTH_SHARE``): a
    recess of the facade closed by a wall drawn across its mouth, open air (major; one finding per group)."""
    out = []
    for lv in building.get("levels") or []:
        lid = lv["id"]
        rooms = {r["id"]: r for r in _rooms_of(building, lid) if _poly(r.get("polygon")) is not None}
        cands = {rid for rid, r in rooms.items() if not _named(r) and not B.is_void_label(_label(r))
                 and RECESS_MIN_AREA_M2 <= (_area(r) or 0.0) < RECESS_AREA_M2}
        if not cands:
            continue
        ops = opening_rooms(building, lid)
        outline = _level_outline(building, lid)
        all_rooms = unary_union([_poly(r["polygon"]) for r in rooms.values()])
        parent = {rid: rid for rid in cands}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for o, _w, t in ops:
            if _is_gap(o):
                inside = [x for x in t if x in cands]
                for x in inside[1:]:
                    parent[find(x)] = find(inside[0])
        groups: dict = {}
        for rid in cands:
            groups.setdefault(find(rid), []).append(rid)
        for members in groups.values():
            group = set(members)
            mine = [(o, w, t) for o, w, t in ops if group & set(t)]
            if not mine or any(o.get("type") == "door" for o, _, _ in mine):
                continue
            if any(o.get("type") == "window" and not any(x not in group and _named(rooms[x]) for x in t)
                   for o, _, t in mine):
                continue                                          # a window of its own: a room, not a recess
            # the mouth: a gap touching only the group, in an outer wall or with open air beyond it (a wall drawn
            # across a recess is often not marked exterior: the reading took the recess for a room)
            mouths = [(o, w, t) for o, w, t in mine if _is_gap(o) and w is not None and set(t) <= group
                      and (w.get("exterior") or _beyond_outside(o, w, [_poly(rooms[x]["polygon"]) for x in t],
                                                                 outline, all_rooms))]
            if not mouths:
                continue
            looks = sorted({o.get("id") for o, _, t in mine if o.get("type") == "window"})
            wide = []
            for o, w, t in mouths:
                side = max((_side_length(_poly(rooms[x]["polygon"]), w) for x in t), default=0.0)
                if side > 0 and float(o.get("width") or 0.0) >= RECESS_MOUTH_SHARE * side - EPS:
                    wide.append(o.get("id"))
            if not looks and not wide:
                continue
            members = sorted(members)
            area = sum(_area(rooms[x]) or 0.0 for x in members)
            named = sorted({f"{x} '{_label(rooms[x])}'" for o, _, t in mine if o.get("type") == "window"
                            for x in t if x not in group})
            signs = []
            if wide:
                signs.append(f"its mouth {', '.join(wide)} in the outer wall is as wide as the room")
            if looks:
                signs.append(f"the window(s) {', '.join(looks)} of {', '.join(named)} look into it")
            u = unary_union([_poly(rooms[x]["polygon"]) for x in members]).representative_point()
            out.append(_finding("facade_recess", "major", lid,
                                f"{', '.join(members)} ({_fmt(area)} m2, no name of their own, no door) "
                                f"{'is' if len(members) == 1 else 'are'} reached only through unclassified gaps, one "
                                f"in an outer wall ({', '.join(o.get('id') for o, _, _ in mouths)}); "
                                + "; ".join(signs) + ": a recess of the facade closed by a wall across its mouth, "
                                "likely open air", (u.x, u.y), members + looks,
                                mouths=[o.get("id") for o, _, _ in mouths]))
    return out


def false_stairs(building: dict) -> tuple[list, set]:
    """Rule 8 (pure; C0007): ``(findings, ids)``: a stair piece standing in a wet room or a kitchen
    (``FALSE_STAIR_ROOMS``) whose own area is in its range (a real bathroom, not a merged face), a stair with a
    footprint under ``STAIR_MIN_AREA_M2``, with ``GRID_FLIGHTS_MIN`` flights or more in less than ``FLIGHT_MIN_AREA_M2``
    each; fewer than ``STAIR_MIN_TREADS`` tread lines are named with another sign: a tile grid read as a stair
    (major). ``ids`` are left out of the stair rules (they join nothing)."""
    out, ids = [], set()
    roofs = {lv["id"] for lv in building.get("levels") or [] if _is_roof(lv)}
    for f in building.get("furniture") or []:
        if f.get("type") != "stair":
            continue
        fp = _footprint(f)
        if fp is None:
            continue
        lid = f.get("level_id")
        reasons = []
        host = None
        for r in _rooms_of(building, lid):
            poly = _poly(r.get("polygon"))
            if poly is not None and poly.buffer(EPS).contains(fp.centroid):
                host = r
                break
        if host is not None:
            st = sense_type(host, roof=lid in roofs)
            a = _area(host) or 0.0
            if st in FALSE_STAIR_ROOMS and a <= AREA_RANGES[st][1] + EPS:
                reasons.append(f"it stands in the {st} {host.get('id')} '{_label(host)}' ({_fmt(a)} m2)")
        if fp.area < STAIR_MIN_AREA_M2 - EPS:
            reasons.append(f"its footprint is {fp.area:.2f} m2 (a stair needs {STAIR_MIN_AREA_M2:g} m2)")
        flights = (f.get("stair") or {}).get("flights") or []
        if len(flights) >= GRID_FLIGHTS_MIN and fp.area / len(flights) < FLIGHT_MIN_AREA_M2 - EPS:
            reasons.append(f"it has {len(flights)} flights in {fp.area:.2f} m2 (a flight needs about "
                           f"{FLIGHT_MIN_AREA_M2:g} m2: a grid of lines, not flights)")
        treads = sum(int(fl.get("lines") or 0) for fl in flights)
        if reasons and 0 < treads < STAIR_MIN_TREADS:
            reasons.append(f"it has {treads} tread lines")
        if not reasons:
            continue
        ids.add(f.get("id"))
        out.append(_finding("false_stair", "major", lid, f"stair {f.get('id')}: " + "; ".join(reasons)
                            + ": no stair can be there (a tile grid or a pattern read as treads)",
                            (fp.centroid.x, fp.centroid.y), [f.get("id")] + ([host.get("id")] if host else []),
                            area_m2=round(fp.area, 3), treads=treads))
    return out, ids


def stair_stacking(building: dict, false_ids: Optional[set] = None) -> list:
    """Rule 9 (pure; C0009, C0010): two neighbouring base levels with exactly one core stair each (``core_stairs``:
    false stairs left out) whose footprints are more than ``STACK_OFFSET_M`` apart in plan: the stair of one floor
    does not stand on the one below (a misplaced floor or a stair read elsewhere); the offset of their centres is
    reported (major)."""
    out = []
    levels = base_levels_by_height(building)
    for lo, hi in zip(levels, levels[1:]):
        if abs(_el(hi) - _el(lo)) < 0.5:
            continue
        a, b = core_stairs(building, lo["id"], false_ids), core_stairs(building, hi["id"], false_ids)
        if len(a) != 1 or len(b) != 1:
            continue
        ca, cb = a[0][1].centroid, b[0][1].centroid
        dx, dy = cb.x - ca.x, cb.y - ca.y
        off = math.hypot(dx, dy)
        gap = a[0][1].distance(b[0][1])
        if gap <= STACK_OFFSET_M + EPS:
            continue
        out.append(_finding("stair_stacking", "major", hi["id"],
                            f"the core stair {b[0][0]} of {hi['id']} {hi.get('label') or ''} stands {off:.2f} m off "
                            f"the core stair {a[0][0]} of {lo['id']} {lo.get('label') or ''} (dx {dx:+.2f} m, dy "
                            f"{dy:+.2f} m; {gap:.2f} m between them): the floors do not stack, or one stair is read "
                            f"in the wrong place", (cb.x, cb.y), [a[0][0], b[0][0]], offset_m=round(off, 3),
                            dx=round(dx, 3), dy=round(dy, 3), levels=[lo["id"], hi["id"]]))
    return out


def _reflect(points, axis: tuple) -> list:
    kind, c = axis
    return [((2 * c - x), y) if kind == "x" else (x, (2 * c - y)) for x, y in points]


def _twin_type(room: dict) -> Optional[str]:
    return None if _untyped(room) else (sense_type(room) or room.get("room_type"))


def _reader_axis(rooms: dict) -> Optional[tuple]:
    """The mirror axis the reading itself used on a level: a twin's ``twin_transform`` (x' = -x + 2c: axis x = c) or a
    label inferred by mirror (``axis``), or None."""
    for r in rooms.values():
        tf = r.get("twin_transform")
        if isinstance(tf, list) and len(tf) == 6:
            if tf[0] < 0 and abs(tf[4] - 1.0) < 1e-3:
                return ("x", round(tf[2] / 2.0, 4))
            if tf[4] < 0 and abs(tf[0] - 1.0) < 1e-3:
                return ("y", round(tf[5] / 2.0, 4))
        li = r.get("label_inferred") or {}
        if li.get("method") == "mirror" and isinstance(li.get("axis"), list) and len(li["axis"]) == 2:
            return (str(li["axis"][0]), float(li["axis"][1]))
    return None


def mirror_pairs(building: dict, lid: str) -> tuple[list, Optional[tuple]]:
    """``([(room a, room b, how)], axis)`` (pure): the twin rooms of a level. First the reading's own pairs
    (``twin_of``, a label inferred by mirror); then, about the reading's own axis (``_reader_axis``), every other room
    of ``TWIN_MIN_AREA_M2`` or more within its twins' box (not the core, ``CORE_TYPES``) and the room its mirror image
    overlaps by ``TWIN_IOU_MIN`` (an image overlapping no room, though other rooms cover ``TWIN_IMAGE_READ_SHARE`` of
    it, is a pair with None: the other half read differently). The axis pairs count only when
    ``TWIN_TYPE_AGREE_MIN`` of all the pairs have one type."""
    rooms = {r["id"]: r for r in _rooms_of(building, lid) if _poly(r.get("polygon")) is not None}
    pairs, seen = [], set()
    for r in rooms.values():
        other = r.get("twin_of") or ((r.get("label_inferred") or {}).get("of")
                                     if (r.get("label_inferred") or {}).get("method") == "mirror" else None)
        if other in rooms and frozenset((r["id"], other)) not in seen:
            seen.add(frozenset((r["id"], other)))
            how = "twin_of" if r.get("twin_of") else "label mirrored"
            pairs.append((rooms[other], r, how))
    axis = _reader_axis(rooms)
    if axis is None:
        return pairs, None
    paired = {x for k in seen for x in k}
    # the reading's axis holds where its own twins stand (a block of two mirrored flats over a single one: real14)
    region = (unary_union([_poly(rooms[x]["polygon"]) for x in paired]).envelope.buffer(TWIN_REGION_GROW_M)
              if paired else None)
    polys = {rid: _poly(r["polygon"]) for rid, r in rooms.items()}
    all_rooms = unary_union(list(polys.values())) if polys else None
    found = []
    for rid, r in sorted(rooms.items()):
        if rid in paired or (_area(r) or 0.0) < TWIN_MIN_AREA_M2 or B.is_void_label(_label(r)) \
                or sense_type(r) in CORE_TYPES or (region is not None and not region.contains(polys[rid].centroid)):
            continue                                      # the core (a lift, a stair, a shaft) stays out of the mirror
        img = Polygon(_reflect(list(polys[rid].exterior.coords), axis)).buffer(0)
        if img.is_empty or img.intersection(polys[rid]).area > 0.5 * img.area:
            continue                                                          # the room stands on the axis
        best = max(((img.intersection(q).area / max(img.union(q).area, EPS), oid) for oid, q in polys.items()
                    if oid != rid), default=(0.0, None))
        how = "the reading's mirror axis"
        if best[1] is not None and best[0] >= TWIN_IOU_MIN - EPS:
            key = frozenset((rid, best[1]))
            if key in seen:
                continue
            seen.add(key)
            found.append((r, rooms[best[1]], how))
        elif (_named(r) or (_area(r) or 0.0) >= UNTYPED_CORE_M2) and all_rooms is not None \
                and img.intersection(all_rooms).area >= TWIN_IMAGE_READ_SHARE * img.area - EPS:
            found.append((r, None, how))                  # the other half is read there, as other rooms
    allp = [(x, y) for x, y, _ in pairs + found]
    agree = sum(1 for x, y in allp if y is not None and _twin_type(x) == _twin_type(y))
    if not any(y is not None for _, y in allp) or agree < TWIN_TYPE_AGREE_MIN * len(allp) - EPS:
        return pairs, None                                # the rooms do not mirror about it: no mirrored plan
    return pairs + found, axis


def mirror_twins(building: dict) -> list:
    """Rule 10 (pure; C0004, C0018, real19's twin flat): twin rooms (``mirror_pairs``) that differ in type, in area by
    more than ``TWIN_AREA_SHARE``, or of which one has a way in (a door, an opening, a separator) and the other none;
    a named room whose mirror image holds no room. Minor; major when one twin cannot be entered."""
    out = []
    for lv in building.get("levels") or []:
        lid = lv["id"]
        pairs, axis = mirror_pairs(building, lid)
        if not pairs:
            continue
        access = room_access(building, lid)[0]
        where = f" about {axis[0]} = {axis[1]:.2f} m" if axis else ""
        for a, b, how in pairs:
            if b is None:
                out.append(_finding("mirror_twins", "minor", lid,
                                    f"{a['id']} '{_label(a)}' ({_fmt(_area(a) or 0.0)} m2) has no twin: its mirror "
                                    f"image{where} overlaps no room (the other half is read differently)",
                                    _centre(a), [a["id"]], part="missing", how=how))
                continue
            diffs = []
            ta, tb = _twin_type(a), _twin_type(b)
            if ta != tb:
                diffs.append(f"type {ta or 'untyped'} / {tb or 'untyped'}")
            aa, ab = _area(a) or 0.0, _area(b) or 0.0
            if max(aa, ab) > 0 and abs(aa - ab) > TWIN_AREA_SHARE * max(aa, ab) + EPS:
                diffs.append(f"area {_fmt(aa)} / {_fmt(ab)} m2")
            na, nb = len(access.get(a["id"]) or []), len(access.get(b["id"]) or [])
            # 6 Nov 2026 (calibration): only a twin with no way in against one with a way in; the counts differ
            # between two well-read halves (an open kitchen's separator, a door read as an opening), and the reading's
            # own twin_of pairs have their counts compared by crossdoc's RC12
            if (na == 0) != (nb == 0):
                diffs.append(f"ways in {na} / {nb}")
            if not diffs:
                continue
            sev = "major" if (na == 0) != (nb == 0) else "minor"
            out.append(_finding("mirror_twins", sev, lid,
                                f"{a['id']} '{_label(a)}' and its twin {b['id']} '{_label(b)}' ({how}{where}) "
                                f"differ: " + ", ".join(diffs) + (": one of them cannot be entered" if sev == "major"
                                                                  else ""),
                                _centre(b), [a["id"], b["id"]], part="pair", how=how))
    return out


def wall_across_passage(building: dict) -> list:
    """Rule 11 (pure; C0051, C0053): an unclassified gap (type opening, not virtual) ``PASSAGE_GAP_M`` wide in an
    inner wall between a hall (or a corridor) and another room, with no door symbol within ``DOOR_SYMBOL_REACH_M``:
    the reading may have walled a drawn open passage (minor: it is often a real door with its symbol missing)."""
    out = []
    lo, hi = PASSAGE_GAP_M
    for lv in building.get("levels") or []:
        lid = lv["id"]
        rooms = {r["id"]: r for r in _rooms_of(building, lid)}
        arcs = [Point(tuple(sy["footprint"]["center"][:2])) for sy in building.get("symbols") or []
                if sy.get("level_id") == lid and sy.get("kind") == "door_arc" and (sy.get("footprint") or {})
                .get("center")]
        for o, w, touched in opening_rooms(building, lid):
            if o.get("virtual") or o.get("type") != "opening" or w is None or w.get("exterior"):
                continue
            width = float(o.get("width") or 0.0)
            if not (lo - EPS <= width <= hi + EPS) or len(touched) != 2:
                continue
            halls = [x for x in touched if sense_type(rooms[x]) in ("hall", "fire_lobby")]
            if not halls:
                continue
            # 6 Nov 2026 (calibration): a gap onto a stair, a lift or a shaft is the open stair or the lift's door, and
            # one between two named halls is a corridor going on; neither is a walled passage
            if any(sense_type(rooms[x]) in PASSAGE_OPEN_TYPES for x in touched):
                continue
            if all(sense_type(rooms[x]) in ("hall", "fire_lobby") and _named(rooms[x]) for x in touched):
                continue
            c = Point(tuple(o["center"][:2]))
            if any(c.distance(q) <= DOOR_SYMBOL_REACH_M + EPS for q in arcs):
                continue
            other = next(x for x in touched if x != halls[0])
            out.append(_finding("wall_across_passage", "minor", lid,
                                f"wall {w.get('id')} has an unclassified gap {o.get('id')} {width:.2f} m wide between "
                                f"the hall {halls[0]} '{_label(rooms[halls[0]])}' and {other} '{_label(rooms[other])}' "
                                f"with no door symbol: an open passage walled by the reading, or a door drawn without "
                                f"its symbol", (c.x, c.y), [w.get("id"), o.get("id"), halls[0], other], width_m=width))
    return out


def wall_mass(building: dict) -> list:
    """Rule 12 (pure; C0020): a face under ``WALL_MASS_FACE_M2`` typed hall or unknown: wall mass, a column casing or
    a closet the walls swallowed, closed as a room (minor; ``room_type_area`` leaves these faces to this rule)."""
    out = []
    for r in building.get("rooms") or []:
        a = _area(r)
        if a is None or a >= WALL_MASS_FACE_M2 - EPS or r.get("room_type") not in ("hall", "unknown"):
            continue
        if B.is_void_label(_label(r)):
            continue
        out.append(_finding("wall_mass", "minor", r.get("level_id"),
                            f"{r.get('id')} '{_label(r) or '-'}' (type {r.get('room_type')}) is a {_fmt(a)} m2 face: "
                            f"wall mass, a column casing or a closet between walls, not a room one enters",
                            _centre(r), [r.get("id")], area_m2=round(a, 3)))
    return out

# --------------------------------------------------------------------------------------------------------- the run
def run(building: dict, texts_by_level: Optional[dict] = None, trust: Optional[dict] = None,
        apply: bool = True) -> list:
    """Every rule on a building (pure); the trust file applied (``apply_trust``) unless ``apply`` is False."""
    larger = label_names_larger_face(building, texts_by_level)
    mass = wall_mass(building)
    out = larger + room_type_area(building, skip={i for f in larger + mass for i in f["element_ids"]})
    out += frame_walls_and_paper_rooms(building, texts_by_level)
    out += unread_walls(building, texts_by_level)
    fake, false_ids = false_stairs(building)
    out += circulation(building, false_ids)
    out += label_vocabulary(building)
    # 6 Nov 2026, round 2
    out += facade_recess(building)
    out += fake
    out += stair_stacking(building, false_ids)
    out += mirror_twins(building)
    out += wall_across_passage(building)
    out += mass
    return apply_trust(out, trust if trust is not None else load_trust()) if apply else out


def level_texts(out_dir, building: dict, sheets: dict) -> dict:
    """``{level_id: [{text, x, y, layer, entity}]}``: the texts of each level's drawing in building metres (the CAD
    levels; a typical floor's copies share their floor's page)."""
    from wenart.reading_check import level_pages, read_level_page
    from wenart.reading_check.crossdoc import _texts_of

    out = {}
    for lid, pg in level_pages(building).items():
        page = read_level_page(Path(out_dir), sheets, pg)
        if page is not None:
            out[lid] = _texts_of(page, pg["tf"])
    return out


def findings(out_dir, trust: Optional[dict] = None, texts: bool = True) -> list:
    """Every RC14 finding of a pipeline output (the module docstring); ``texts=False`` skips reading the drawing's
    texts (rules 2 and 4 then use the reading's own labels)."""
    out_dir = Path(out_dir)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sp = out_dir / "sheets.json"
    sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    tx = level_texts(out_dir, building, sheets) if texts else {}
    return run(building, tx, trust)


# --------------------------------------------------------------------------------------------------------- trust
def load_trust(path: Path = TRUST_PATH) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def apply_trust(found: list, trust: Optional[dict]) -> list:
    """Each finding gets ``trust`` ``{precision, findings, threshold}`` of its rule; a rule below the threshold, or
    never judged, writes its findings with severity ``info`` (``base_severity`` kept) and says so (in place)."""
    rules = (trust or {}).get("rules") or {}
    threshold = float((trust or {}).get("threshold") or TRUST_MIN)
    for f in found:
        if f.get("check") != CHECK or f.get("rule") not in RULES:
            continue
        if "base_message" not in f:
            f["base_message"] = f["message"]
            f["base_severity"] = f["severity"]
        k = rules.get(f["rule"]) or {}
        n, prec = int(k.get("findings") or 0), k.get("precision")
        f["trust"] = {"precision": prec, "findings": n, "threshold": threshold}
        f["severity"] = f["base_severity"]
        if prec is None or n == 0:
            f["severity"] = "info"
            f["message"] = f["base_message"] + " [info only: this rule is not calibrated yet]"
        elif float(prec) < threshold:
            f["severity"] = "info"
            f["message"] = f["base_message"] + (f" [info only: rule precision {float(prec):.2f} on {n} judged "
                                                f"findings < {threshold:g}]")
        else:
            f["message"] = f["base_message"] + f" [rule precision {float(prec):.2f} on {n} judged findings]"
    return found


def finding_key(project: str, f: dict) -> str:
    """The key a judgement names a finding by: project, level, rule, part and element ids (or the level alone)."""
    ids = ",".join(f.get("element_ids") or []) or "-"
    return f"{project}|{f.get('level_id') or '-'}|{f.get('rule')}|{f.get('part') or '-'}|{ids}"


def trust_from(judgements: list, commit: Optional[str] = None, projects: Optional[list] = None,
               note: Optional[str] = None, extra: Optional[dict] = None) -> dict:
    """The trust file's content (pure) from judged findings ``[{key, project, project_status, rule, right: bool,
    reason, ...}]``: per rule ``{findings, judged_right, precision, trusted}`` over every judged finding (a judgement
    with ``counts: false`` left out), with the split by ``project_status`` (accepted, open, partial) and
    ``small_sample`` under ``SMALL_SAMPLE`` findings; ``extra`` is merged in (the calibration's history)."""
    rules = {}
    for rule in RULES:
        js = [j for j in judgements if j.get("rule") == rule and j.get("counts", True)]
        n = len(js)
        r = sum(1 for j in js if j.get("right"))
        split = {}
        for j in js:
            k = split.setdefault(j.get("project_status") or "unknown", {"findings": 0, "judged_right": 0})
            k["findings"] += 1
            k["judged_right"] += 1 if j.get("right") else 0
        rules[rule] = {"findings": n, "judged_right": r, "precision": round(r / n, 4) if n else None,
                       "trusted": bool(n) and r / n >= TRUST_MIN, "small_sample": n < SMALL_SAMPLE,
                       "by_status": split}
    out = {"note": note or ("Precision of the architectural-sense checks (RC14) per rule, judged one finding at a "
                            "time (a finding is right when it points at a real error of the reading, false when the "
                            "reading follows its drawing); a rule below the threshold, or never judged, writes its "
                            "findings with severity info. The tables were tuned on the same readings: in-sample."),
           "commit": commit, "date": _dt.date.today().isoformat(), "threshold": TRUST_MIN,
           "projects": sorted(set(projects or [j.get("project") for j in judgements if j.get("project")])),
           "rules": rules}
    out.update(extra or {})
    out["judgements"] = judgements
    return out


def save_trust(trust: dict, path: Path = TRUST_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(trust, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------------------------------------- CLI
def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check sense", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="the RC14 findings of a pipeline output")
    c.add_argument("--out", required=True, help="a pipeline output folder (building.json, sheets.json, converted/)")
    c.add_argument("--json", help="write the findings to this JSON file")
    c.add_argument("--no-texts", action="store_true", help="do not read the drawing's texts (faster)")
    c.add_argument("--raw", action="store_true", help="the findings before the trust file lowers them")
    t = sub.add_parser("trust", help="the trust file from judged findings")
    t.add_argument("--judged", required=True, help="a JSON list of judgements {key, project, rule, right, reason}")
    t.add_argument("--commit", default=None)
    t.add_argument("--extra", default=None, help="a JSON file merged into the trust file (the calibration history)")
    t.add_argument("--write", action="store_true", help=f"write {TRUST_PATH.name}")
    args = ap.parse_args(argv)
    if args.cmd == "trust":
        judged = json.loads(Path(args.judged).read_text(encoding="utf-8"))
        extra = json.loads(Path(args.extra).read_text(encoding="utf-8")) if args.extra else None
        tr = trust_from(judged, commit=args.commit, extra=extra)
        for rule, v in tr["rules"].items():
            print(f"{rule:30s} {v['findings']:4d} findings, {v['judged_right']:4d} right, precision "
                  f"{v['precision'] if v['precision'] is not None else '-'}, trusted {v['trusted']}")
        if args.write:
            print(save_trust(tr))
        return 0
    out_dir = Path(args.out)
    building = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    sp = out_dir / "sheets.json"
    sheets = json.loads(sp.read_text(encoding="utf-8")) if sp.is_file() else {}
    tx = {} if args.no_texts else level_texts(out_dir, building, sheets)
    res = run(building, tx, apply=not args.raw)
    for f in res:
        print(f"{f['rule']:28s} {f['severity']:6s} {str(f.get('level_id') or '-'):6s} {f['message']}")
    counts = {s: sum(1 for f in res if f["severity"] == s) for s in ("major", "minor", "info")}
    print(f"{len(res)} findings: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
