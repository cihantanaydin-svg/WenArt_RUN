"""Openings of the generic plan core (docs/milestone7.md §2.6): wall runs, gaps of three kinds, gap classification.

Real plans leave a gap in the wall where a door, window or doorless opening is, and the gap is not always between
two pieces of one wall: real01's bath and store doors lie between a free wall end and the face of a perpendicular
wall, and its two bedroom doors share one run gap that the end of the wall between the bedrooms splits in two. So:

- **Runs**: wall rectangles on one axis line (centre-line offset <= 20 mm, thickness +- 30 mm). Two kinds of odd
  pieces a wall mask gives (real01's photo, P7) are handled first, each logged (``kind "wall_piece"``) with a note:
  a **fused strip** (``join_fused_strips``: a door leaf filled into the mask along a wall face, one face flush, <= a
  leaf's width out, a door swing hinged at it, the strip as long as its leaf) joins its run with the run's faces;
  an **end cap** (``end_caps``: a piece shorter than its thickness at the end of a longer wall, a door frame or a
  nub) is no wall end: no gap is cast from or to it and it keeps no end from being free.
- **Gaps**, all classified the same way:
  (a) *run gap* between consecutive pieces of a run;
  (c) a run gap holding the end of a perpendicular wall inside the run band is *split* at that wall;
  (b) *end gap* from a free wall end (no wall within 50 mm of its end face) along its axis to the first wall face
      hit within 3.0 m.
  Width g < 0.25 m -> closed (warning); 0.25-3.0 m -> classified; > 3.0 m -> open (topology decides).
- **Classifier** (strokes in the gap grown by 0.35 m on both faces; the zone is for classification only):
  *door* = an arc hinged within 0.08 m of a gap end (or inside the wall band at the gap end), radius g +- 12 % (or
  down to g - 0.25 m: door frames take the rest, real06),
  sweep 60-100 deg (or two arcs of radius g/2 hinged at both ends), with an optional leaf (a thin shape <= 60 mm
  wide starting within 0.10 m of the hinge, 0.85-1.05 r long, along the arc's start or end radius); *window* = >= 2
  straight strokes parallel to the wall inside the band spanning >= 80 % of g; *doorless* = nothing in the band and
  no door-like arc (hinged within the zone of a gap end, radius 0.4-1.5 g; furniture that is only in the zone does
  not count) (``unverified`` in an exterior wall: "possible undrawn door or window"); anything else is an unverified
  ``opening`` with ``type_raw "unclassified gap content"``.
- A run gap closes inside its run (the run becomes one ``WallItem``); an end gap holding a door or window extends
  the free-end wall to the hit face (evidence method ``derived``); an empty end gap is only logged as a separator
  candidate for ``topology.separators``.
- An opening owns its arc, leaf, hinge pin and the strokes entirely within the gap +- 0.10 m along the wall and inside
  the wall band (faces +- 20 mm) across it (jamb frames, window lines); ``symbols.furniture`` drops exactly those.
- Continuous-wall symbols (the synthetic convention and raster double-line walls) keep working: an arc + leaf
  hinged inside a wall band or within 0.08 m of a face (the end-point rule of ``pdf_extract._door_from_arc``: the leaf
  runs from the hinge to one arc end, the other arc end lies one radius from the hinge; a leaf drawn as a thin
  rectangle passes the classifier's leaf rule instead), radius 0.6-1.2 m (from 0.45 m on a door layer), is a door cut
  into that wall; >= 3 parallel strokes inside a wall band (one strictly inside it) over >= 0.4 m are a window, and so
  are >= 2 strictly inside it (walls drawn as face lines: the faces are the wall primitive, not strokes here;
  docs/milestone10.md §3.1 item 11).
- ``operation`` (Milestone 10, §1.6b row 17; set as attributes by ``set_operation``, copied by the pipeline): a block
  name that says it (``OPERATION_WORDS``: sliding / sürme, pocket, folding / katlanır, double / çift kanat, fixed /
  sabit) wins (``block_name``); else the drawing (``geometry``): one swing arc = swing, two half arcs = double, and a
  gap with no swing arc but one or two thin closed leaves parallel to the wall (real06, 24 Oct 2026: or a leaf drawn
  as >= 2 parallel lines with the same ends, <= a leaf's width apart), overlapping it, in the band or within
  0.10 m of a face, either shorter than 0.85 x the gap or drawn half open (off the gap centre), is a sliding door (a
  window's glass spans its gap, centred). A door block whose name says a door that opens without a swing arc
  (KAPI/DOOR with sliding, pocket or folding; no window word) is that door whatever its leaf looks like, checked
  before the window rule (drawn closed, a leaf's two sides would read as glass). Windows get an operation only from
  a block name (else null: swing, assumed).
- Walls drawn as face lines (real02) put two walls of one axis line far apart with perpendicular walls crossing the
  gap between them (the bedroom walls of a semi-detached pair, a corridor and a bathroom between them): a run gap
  that perpendicular walls running through the band split is one wall with openings only when every part holds a
  door or window symbol (or is < 0.25 m); a part that is empty or unclassified makes all parts ``open`` (no wall
  across), and the free ends cast their own end gaps. The same holds for any split run gap longer than 3 m (open by
  itself). A shorter gap split by a wall *ending* in the band (real01's two bedroom doors) splits as before.

Everything is in page metres (y up). Walls at other angles than the plan's dominant pair pass through untouched.

Fix round after P6b (23 Oct 2026; pod P6b, real03, checked on the LibreDWG strokes of real02, real03 and real04).
What: a window needs glass, and three kinds of gap are no openings of their run any more.

- **Glass** (``_confined``): a window, in a gap or across a continuous wall, needs lines of its own: parallel to the
  wall, ending within the window +- ``OWN_MARGIN_M`` (glass, frame and sill lines end at the jambs) and spanning >=
  ``WINDOW_COVER`` of it, at >= ``WINDOW_LINES_MIN`` distinct offsets, >= ``GLASS_MIN_LINES`` of them glass strictly
  between the faces (>= ``GLASS_INSET_M`` inside), two glass lines or one between two lines of the window
  (``_framed_glass``), none of a shape standing out of the wall band (a fixture or a wardrobe drawn against the
  wall). The synthetic convention (both faces and one glass line, ending at the jambs)
  passes; lines running on past the gap (a beam projection, a room or area outline, an axis, wardrobe
  backs along a partition) are no window; their strokes stay owned (out of the furniture) as before. real03 had 43
  such 'windows' among 64 (each of its 21 real windows carries its CAM/CAM-PER frame lines, two or three glass
  offsets; one more real window, hidden behind a ghost before, is found), real04 two (wardrobe backs between two
  bedrooms, P6a's G12 majors); real02's 12 windows (two glass lines each) do not change. A raster page's traced lines
  keep the old rule (their ends and offsets carry the tracing's error; synthetic-02's scan). A gap that loses its
  window this way is an unverified opening ("unclassified gap content", the reason in its note), except a gap whose
  two faces are drawn on across it on a wall layer (``_wall_faces``: lines running past it, covering it from jamb to
  jamb, layer ``DUVAR``/``WALL``/``... - BA``, ``dxf_generic.is_wall_hint_layer``) with no swing reaching in: there
  the wall continues (``closed``: a run merges across it, a free-end wall is extended with evidence ``derived``; the
  reason in the gap's note). real03's two stair-core walls are DUVAR outlines with a door block inside, so no wall
  primitive: one was a 1.55 m 'window' between the floor hall and the fire stair. Room or area outlines, beam
  projections and axes across a gap are no wall (a doorless passage whose room outlines close across it keeps it).
- A **lined gap** (``_lining``): a thinner wall (>= ``LINING_THINNER_M`` thinner, its own run) lies along one face of
  the run (flush within ``RUN_OFFSET_M``, inside its band), its pieces fill >= ``LINING_SHARE`` of the gap and it
  runs on past both gap ends (> ``LINING_REACH_M``) as one wall (``_chains``: its pieces apart by its own gaps <=
  ``GAP_MAX_M`` only, which it classifies). The gap is ``open``: the thick pieces are columns or shear walls
  standing on that wall, not one wall with windows between them. real03: the 30 cm shear walls of the hall-living
  partition (``D BLOK_STA_NK`` B-H/BA, y 0-1.3, 5.7-7.7, 12.1-13.4 m) were one 0.30 m wall from end to end, its gaps
  windows read from the beam projections (IZ-1), the axis line and the net-area outlines lying on its faces; it
  swallowed the 0.20 m of hall and bedroom beside the drawn 0.10 m partition (``DUVAR``), so the drawn 0.60 m washers
  stood 0.14-0.19 m in the wall of a 0.45 m niche (the plan's 'İŞLİK 0.45 m2' is 0.65 x 0.69 m). The thick pieces
  stay walls of their own; each wall that a lined gap split is marked ``corrected_by_ai`` (reason, evidence: the
  lining wall's and the pieces' entities, before: the wall as one run) and the gap's log entry says why. The thin
  wall keeps its own gaps (the 1.05 m hall-living passages). No end gap is cast across a lined gap.
- A gap **inside wall material** (``_inside_wall``): other pieces on the run's axis (another run, a thicker
  cross-section) cover its whole band along its whole width, and it holds no door symbol (a drawn swing keeps its
  door). It is ``closed`` (the run merges across it, as a gap <
  0.25 m does) with a note, never a window or opening: real03's shear-wall core (y 5.7-7.7 m), where the
  0.62 m pieces of the core covered the gaps the mask decomposition left in the 0.10, 0.30, 0.41 and 0.54 m runs
  through it, and its columns and shear walls in the outer walls: 13 'openings' inside concrete (the core's 12
  'windows' had no glass either).
"""
from __future__ import annotations

import dataclasses
import math
import statistics
from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union
from shapely.strtree import STRtree

from wenart import building as B
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import DOOR_SWING_PROBE, OpeningItem, WallItem

RUN_OFFSET_M = 0.02
RUN_THICKNESS_M = 0.03
FREE_END_M = 0.05
CAST_STUB_M = 0.05             # 4 Nov 2026: stubs side by side (faces within this along the cast) cover a wall's band together
GAP_MIN_M = 0.25
GAP_MAX_M = 3.0
GAP_IGNORE_M = 0.005
ZONE_M = 0.35
DOOR_LIKE_RADIUS = (0.4, 1.5)  # x gap width: an arc in the zone that keeps a gap from being doorless
BAND_SLACK_M = 0.02
HINGE_M = 0.08
RADIUS_TOL = 0.12
DOOR_FRAME_M = 0.25            # ... or a leaf up to this much narrower than the gap (frames; real06: 0.70 m in 0.90 m)
SWEEP_DEG = (60.0, 100.0)
LEAF_WIDTH_M = 0.06
FUSED_STRIP_M = LEAF_WIDTH_M       # a door leaf fused along a wall face in the mask is at most a leaf wide ...
RASTER_EDGE_PX = 1.5               # ... plus the raster mask's edge precision (core.RASTER_JOINT_PX), in pixels
LEAF_CORRIDOR_M = 0.09
LEAF_START_M = 0.10
LEAF_LENGTH = (0.85, 1.05)
WINDOW_COVER = 0.8
WINDOW_ANGLE_DEG = 1.0
OWN_MARGIN_M = 0.10
CONTINUOUS_RADIUS_M = (0.45, 1.2)   # 6 Nov 2026 (real16: a shower room's 0.54 m swing with its leaf): on a door layer
CONTINUOUS_RADIUS_ANY_M = 0.6       # ... on any other layer from this (a corner basin or shelf is no door)
CONTINUOUS_WINDOW_M = 0.4
END_POINT_TOL_M = 0.02
AXIS_TOL_DEG = 3.0
# Fix round after P6b (23 Oct 2026): a thinner wall along one face through a run gap (a lined gap) ...
LINING_THINNER_M = 0.05         # ... is at least this much thinner than the run (MIN_WALL_M of walls.py) ...
LINING_SHARE = 0.5              # ... its pieces fill at least this share of the gap ...
LINING_REACH_M = 0.10           # ... and it runs on past both gap ends by more than this (a wall, not a junction piece)
GLASS_INSET_M = 0.01            # glass lies at least this far inside the wall faces ...
WINDOW_LINES_MIN = 2            # ... a window needs this many distinct offsets of its own lines (``_confined``) ...
GLASS_MIN_LINES = 1             # ... this many of them glass (the synthetic convention: two faces and one glass)
# ... and the gap log's ``rule`` of each (``g.found`` key -> rule), in this order
GAP_RULES = (("lining", "lined_gap"), ("inside", "inside_wall"), ("faces", "wall_faces"), ("no_glass", "no_glass"))

DOOR_HEIGHT_M = 2.10
WINDOW_SILL_M = 0.90
WINDOW_HEIGHT_M = 1.20
CONF_DOOR_LEAF, CONF_DOOR, CONF_WINDOW, CONF_DOORLESS = 0.95, 0.85, 0.9, 0.8
# Milestone 10 (docs/milestone10.md §1.6b row 17): how a door or window opens. Block-name words (Turkish letters
# folded to ASCII, spaces and hyphens read as "_"; only words that name the operation), else the drawing: one swing
# arc = swing, two half arcs = double, a leaf drawn parallel to the wall without an arc = sliding.
OPERATION_WORDS: tuple[tuple[str, str], ...] = (
    ("SLIDING", "sliding"), ("SURME", "sliding"), ("POCKET", "pocket"), ("FOLDING", "folding"),
    ("KATLANIR", "folding"), ("AKORDEON", "folding"), ("BIFOLD", "folding"), ("DOUBLE", "double"),
    ("CIFT_KANAT", "double"), ("FIXED", "fixed"), ("SABIT", "fixed"),
)
_FOLD = str.maketrans({"İ": "I", "ı": "i", "Ş": "S", "ş": "s", "Ğ": "G", "ğ": "g", "Ü": "U", "ü": "u", "Ö": "O",
                       "ö": "o", "Ç": "C", "ç": "c", " ": "_", "-": "_"})
DOOR_WORDS = ("KAPI", "DOOR")   # a block named for a door (folded) ...
WINDOW_WORDS = ("PENCERE", "WINDOW")
WINDOW_TOKENS = ("WIN", "PEN")   # 4 Nov 2026 (real17: "fm-win1"): a whole name part that abbreviates a window word
NO_SWING_OPERATIONS = ("sliding", "pocket", "folding")   # ... that opens without a swing arc: a door by its name
SLIDING_LEAF = (0.45, 1.10)     # x gap width: a sliding leaf, overlapping the gap by >= 40 % of it ...
SLIDING_OVERLAP = 0.4
SLIDING_SHORT = 0.85            # ... shorter than 0.85 x the gap, or drawn half open (its centre >= 0.2 x the gap
SLIDING_SHIFT = 0.2             # off the gap centre): a window's glass is as long as its gap and centred on it
SLIDING_REACH_M = 0.10          # ... in the wall band or within 0.10 m of a face
LEAF_END_M = 0.01               # a leaf drawn as lines: its lines end within 1 cm of each other
PANEL_LEAF = (0.35, 0.60)       # two-panel sliding door: each leaf this share of the gap ...
PANEL_COVER = 0.8               # ... together covering this share of it ...
PANEL_TRACK_M = 0.01            # ... on two tracks this far apart across
CONF_RASTER = 0.7


# --------------------------------------------------------------------------
# Frame and pieces
# --------------------------------------------------------------------------

def _rot(p, deg: float) -> tuple[float, float]:
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def dominant_angle(walls: list[WallItem]) -> float:
    """Length-weighted dominant wall direction mod 90, in (-45, 45] deg."""
    bins: dict[int, float] = {}
    for w in walls:
        length = math.dist(w.start, w.end)
        if length <= 0:
            continue
        ang = math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 90.0
        k = int(round(ang * 2.0)) % 180
        bins[k] = bins.get(k, 0.0) + length
    if not bins:
        return 0.0
    k = max(bins, key=bins.get)
    ang = k / 2.0
    return ang - 90.0 if ang > 45.0 else ang


@dataclass
class Piece:
    """A wall rectangle in the plan's aligned frame (rotated by -theta)."""
    k: int                      # index into the input walls
    axis: str                   # "h": along x, "v": along y (aligned frame)
    c: float                    # centre-line offset (y for h, x for v)
    t: float                    # thickness
    a: float                    # extent along the axis, a < b
    b: float
    wall: WallItem
    run: int = -1

    def rect(self) -> tuple[float, float, float, float]:
        h = self.t / 2.0
        if self.axis == "h":
            return (self.a, self.c - h, self.b, self.c + h)
        return (self.c - h, self.a, self.c + h, self.b)

    def end_face(self, which: str) -> tuple[tuple[float, float], tuple[float, float]]:
        pos = self.a if which == "start" else self.b
        h = self.t / 2.0
        if self.axis == "h":
            return ((pos, self.c - h), (pos, self.c + h))
        return ((self.c - h, pos), (self.c + h, pos))


def pieces_of(walls: list[WallItem], theta: float) -> tuple[list[Piece], list[int]]:
    """Axis pieces in the aligned frame and the indices of walls at other angles."""
    out, others = [], []
    for k, w in enumerate(walls):
        s, e = _rot(w.start, -theta), _rot(w.end, -theta)
        ang = math.degrees(math.atan2(e[1] - s[1], e[0] - s[0])) % 180.0
        if min(ang, 180.0 - ang) <= AXIS_TOL_DEG:
            a, b = sorted((s[0], e[0]))
            out.append(Piece(k, "h", (s[1] + e[1]) / 2.0, w.thickness, a, b, w))
        elif abs(ang - 90.0) <= AXIS_TOL_DEG:
            a, b = sorted((s[1], e[1]))
            out.append(Piece(k, "v", (s[0] + e[0]) / 2.0, w.thickness, a, b, w))
        else:
            others.append(k)
    return out, others


def group_runs(pieces: list[Piece]) -> list[list[Piece]]:
    """Pieces on one axis line (offset <= 20 mm, thickness +- 30 mm), sorted along the axis."""
    runs: list[dict] = []
    for p in sorted(pieces, key=lambda p: (p.axis, p.c, p.a)):
        for run in runs:
            if run["axis"] == p.axis and abs(run["c"] - p.c) <= RUN_OFFSET_M and abs(run["t"] - p.t) <= RUN_THICKNESS_M:
                run["pieces"].append(p)
                total = sum(q.b - q.a for q in run["pieces"])
                run["c"] = sum(q.c * (q.b - q.a) for q in run["pieces"]) / total if total > 0 else p.c
                break
        else:
            runs.append({"axis": p.axis, "c": p.c, "t": p.t, "pieces": [p]})
    out = []
    for i, run in enumerate(runs):
        ps = sorted(run["pieces"], key=lambda q: q.a)
        for q in ps:
            q.run = i
        out.append(ps)
    return out


def _touching(p: Piece, others) -> tuple[list[Piece], list[Piece]]:
    """The pieces of ``others`` on p's axis whose end face p's start (``before``) or end (``after``) touches."""
    before = [q for q in others if q is not p and q.axis == p.axis and abs(q.b - p.a) <= GAP_IGNORE_M]
    after = [q for q in others if q is not p and q.axis == p.axis and abs(q.a - p.b) <= GAP_IGNORE_M]
    return before, after


def _outside(p: Piece, touching: list[Piece]) -> tuple[float, float, float, float]:
    """``(out_lo, out_hi, lo, hi)``: how far p's faces lie outside the (mean) faces ``lo``/``hi`` of the touching
    pieces (> 0 outside, < 0 inside)."""
    lo = statistics.mean(q.c - q.t / 2.0 for q in touching)
    hi = statistics.mean(q.c + q.t / 2.0 for q in touching)
    return lo - (p.c - p.t / 2.0), (p.c + p.t / 2.0) - hi, lo, hi


def end_caps(runs: list[list[Piece]], edge_m: float = 0.0) -> tuple[set[int], list[dict]]:
    """Pieces that are a wall end's frame or nub, not a wall end of their own: shorter than their own thickness,
    touching on one side only the end face of a longer piece on their axis that is not in their run (another
    cross-section), their band overlapping that piece's band by >= half their thickness and lying outside it by <=
    ``FUSED_STRIP_M`` + ``edge_m``, and in a run of such pieces only (alone, or the two frames of one opening: a short
    junction piece of a wall run is no cap). A drawn door frame (a jamb nub inside the opening) or a ragged wall end
    gives such pieces in a raster mask (real01's photo: a 0.04 m piece 0.14 m thick at the end of the kitchen-store
    wall kept that wall's end from being free, so the store door's end gap was never cast and its arc became
    furniture; the entrance door's frames, 0.03-0.04 m long inside its run gap, sit there the same way).

    An end cap is no wall end: it neither keeps the end of the wall it caps from being free nor is a free end itself,
    no gap is cast from it or stops at it, it splits no run gap and is in no run (the frame belongs to the opening,
    whose width runs from wall end to wall end as on vector pages). It stays in the walls as drawn. ``runs`` come
    from ``group_runs``. Returns ``(ids, log)``: the ``id()`` of the cap pieces and one log entry each (``kind
    "wall_piece"``, ``how "end_cap"``, with a note)."""
    found: dict[int, tuple[Piece, Piece]] = {}
    pieces = [q for run in runs for q in run]
    for p in pieces:
        length = p.b - p.a
        if length >= p.t:
            continue
        before, after = _touching(p, [q for q in pieces if q.run != p.run])
        touching = before + after
        if bool(before) == bool(after) or max(q.b - q.a for q in touching) <= length:
            continue
        out_lo, out_hi, lo, hi = _outside(p, touching)
        if max(out_lo, out_hi) > FUSED_STRIP_M + edge_m or \
                min(hi, p.c + p.t / 2.0) - max(lo, p.c - p.t / 2.0) < 0.5 * p.t:
            continue
        found[id(p)] = (p, touching[0])
    caps: set[int] = set()
    log: list[dict] = []
    for run in runs:
        if not all(id(q) in found for q in run):
            continue
        for p in run:
            q = found[id(p)][1]
            caps.add(id(p))
            log.append({"kind": "wall_piece", "how": "end_cap", "piece": p.k, "of": q.k,
                        "length": round(p.b - p.a, 4), "thickness": round(p.t, 4),
                        "note": f"a {p.b - p.a:.3f} m piece ({p.t:.3f} m thick) at the end of a {q.t:.3f} m wall is "
                                f"a frame or nub of that wall's end, not a wall end of its own (no gap is cast from "
                                f"or to it)"})
    return caps, log


def join_fused_strips(runs: list[list[Piece]], index: Optional["StrokeIndex"] = None,
                      edge_m: float = 0.0) -> tuple[list[list[Piece]], list[dict]]:
    """A door leaf drawn against a wall face and filled into the wall mask with it makes that stretch of the wall
    thicker on one face, so it leaves its run and the run sees a 'gap' there (real01's photo and scan: the bath
    door's leaf along the drawing room's west wall, 0.05 m; on the photo that gap took the bath door's arc, and the
    end gap of the bath wall stopped 0.05 m short of the wall's face). Such a piece joins the run, with the run's
    centre line and thickness, on this evidence (all needed):

    - it is alone on its axis line and lies between two pieces of the run (touching their end faces);
    - one face is flush with theirs (<= ``RUN_OFFSET_M``), the other lies outside by more than that and by <=
      ``FUSED_STRIP_M`` (a leaf's width) + ``edge_m`` (the raster mask's edge precision; 0 on vector pages);
    - a door swing explains the strip (``_leaf_swing``: an arc hinged at the piece, swinging on the strip's side,
      the strip as long as its leaf).

    The strip is never counted as wall: the run's faces stand. Nothing is silently changed: each join is a log entry
    (``kind "wall_piece"``, ``how "fused_strip"``) with the piece's own thickness and a note that the merged wall's
    evidence carries too. Returns ``(runs, log)``; runs are renumbered."""
    log: list[dict] = []
    for p in sorted((run[0] for run in runs if len(run) == 1), key=lambda p: (p.axis, p.c, p.a)):
        length = p.b - p.a
        if length > GAP_MAX_M:
            continue
        for ri, run in enumerate(runs):
            if len(run) < 2 or run[0].axis != p.axis:
                continue
            before, after = _touching(p, run)
            if not before or not after:
                continue
            out_lo, out_hi, _, _ = _outside(p, before + after)
            strip = max(out_lo, out_hi)
            if min(out_lo, out_hi) < -RUN_OFFSET_M or min(abs(out_lo), abs(out_hi)) > RUN_OFFSET_M or \
                    not RUN_OFFSET_M < strip <= FUSED_STRIP_M + edge_m:
                continue
            swing = _leaf_swing(p, 1.0 if out_hi > out_lo else -1.0, index)
            if swing is None:
                continue
            c, t = _run_c(run), _run_t(run)
            arc_id = swing[0].st.id
            log.append({"kind": "wall_piece", "how": "fused_strip", "piece": p.k, "length": round(length, 4),
                        "thickness": round(p.t, 4), "run_thickness": round(t, 4), "strip": round(strip, 4),
                        "arc": arc_id,
                        "note": f"a {strip:.3f} m strip along one face over {length:.2f} m, where the leaf of door "
                                f"swing {arc_id} rests (a leaf fused to the wall face in the wall mask), is not "
                                f"counted as wall: thickness {t:.3f} m as the rest of the run, not {p.t:.3f} m"})
            p.c, p.t = c, t
            run.append(p)
            run.sort(key=lambda q: q.a)
            runs = [r for r in runs if not (len(r) == 1 and r[0] is p)]
            break
    for i, run in enumerate(runs):
        for q in run:
            q.run = i
    return runs, log


def _leaf_swing(p: Piece, side: float, index: Optional["StrokeIndex"]):
    """``(item, arc)`` of a door swing whose leaf rests along piece ``p`` on its ``side`` (+1: towards larger across
    values), or None: an arc of ``SWEEP_DEG`` hinged within ``HINGE_M`` of the piece's rectangle, its middle on that
    side of the piece's centre line, the piece starting within ``LEAF_START_M`` of the hinge and running on for
    ``LEAF_LENGTH`` x r (+ ``LEAF_START_M``: the hinge pin), the leaf rule of ``_leaf``."""
    if index is None:
        return None
    x0, y0, x1, y1 = p.rect()
    reach = HINGE_M + (p.b - p.a) / LEAF_LENGTH[0]                # the swing lies within one radius of the hinge
    best = None
    for it, arc in _arcs_in(index.query((x0 - reach, y0 - reach, x1 + reach, y1 + reach))):
        hx, hy = arc["center"]
        if not SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1] or \
                not (x0 - HINGE_M <= hx <= x1 + HINGE_M and y0 - HINGE_M <= hy <= y1 + HINGE_M):
            continue
        mid = _arc_mid(arc)
        if ((mid[1] if p.axis == "h" else mid[0]) - p.c) * side <= 0:
            continue
        along = hx if p.axis == "h" else hy
        near, far = sorted((abs(along - p.a), abs(p.b - along)))
        r = arc["radius"]
        if near <= LEAF_START_M and LEAF_LENGTH[0] * r <= far <= LEAF_LENGTH[1] * r + LEAF_START_M \
                and (best is None or near < best[0]):
            best = (near, it, arc)
    return None if best is None else (best[1], best[2])


# --------------------------------------------------------------------------
# Strokes in the aligned frame
# --------------------------------------------------------------------------

@dataclass
class _S:
    st: Stroke
    pts: list[tuple[float, float]]           # aligned frame
    geom: object                             # shapely geometry (aligned frame)


class StrokeIndex:
    """The page's strokes in the aligned frame with an STRtree for box queries."""

    def __init__(self, strokes: list[Stroke], theta: float):
        self.items: list[_S] = []
        for st in strokes:
            if not st.pts:
                continue
            pts = [_rot(p, -theta) for p in st.pts]
            if st.closed and len(pts) > 2:
                ring = pts + [pts[0]]
                geom = LineString(ring)
            elif len(set(pts)) > 1:
                geom = LineString(pts)
            else:
                geom = Point(pts[0])
            self.items.append(_S(st, pts, geom))
        self.tree = STRtree([it.geom for it in self.items]) if self.items else None

    def query(self, rect, predicate: str = "intersects") -> list[_S]:
        if self.tree is None:
            return []
        g = sbox(*rect)
        return [self.items[int(j)] for j in self.tree.query(g, predicate=predicate)]


def arc_of(pts: list[tuple[float, float]]) -> Optional[dict]:
    """Circle fit of a flattened curve: {"center", "radius", "sweep", "start", "end"} or None (residual > 1 % r)."""
    if len(pts) < 4:
        return None
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    u = [p[0] - mx for p in pts]
    v = [p[1] - my for p in pts]
    suu = sum(a * a for a in u)
    svv = sum(b * b for b in v)
    suv = sum(a * b for a, b in zip(u, v))
    det = suu * svv - suv * suv
    if abs(det) < 1e-18:
        return None
    r1 = 0.5 * (sum(a ** 3 for a in u) + sum(a * b * b for a, b in zip(u, v)))
    r2 = 0.5 * (sum(b ** 3 for b in v) + sum(b * a * a for a, b in zip(u, v)))
    uc = (r1 * svv - r2 * suv) / det
    vc = (r2 * suu - r1 * suv) / det
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    cx, cy = uc + mx, vc + my
    if r <= 0 or max(abs(math.dist(p, (cx, cy)) - r) for p in pts) > 0.01 * r:
        return None
    sweep = 0.0
    prev = math.atan2(pts[0][1] - cy, pts[0][0] - cx)
    for p in pts[1:]:
        cur = math.atan2(p[1] - cy, p[0] - cx)
        d = (cur - prev + math.pi) % (2 * math.pi) - math.pi
        sweep += d
        prev = cur
    return {"center": (cx, cy), "radius": r, "sweep": abs(math.degrees(sweep)), "start": pts[0], "end": pts[-1]}


# --------------------------------------------------------------------------
# Gap classification
# --------------------------------------------------------------------------

@dataclass
class Gap:
    kind: str                     # run | split | end
    axis: str
    c: float
    t: float
    a: float
    b: float
    pieces: list[Piece]           # the pieces at the gap ends (end gaps: the free-end piece first)
    free: Optional[tuple[Piece, str]] = None     # end gaps: (piece, "start" | "end")
    hit: Optional[Piece] = None                  # end gaps: the wall hit
    cls: str = ""                 # door | window | opening | unclassified | empty | closed | open
    found: dict = field(default_factory=dict)
    slant: float = 0.0            # end gaps: the drawn wall's angle off the axis (deg) where its pieces step (``_slant``)

    @property
    def width(self) -> float:
        return self.b - self.a

    def rect(self, grow_face: float = 0.0, grow_along: float = 0.0) -> tuple[float, float, float, float]:
        h = self.t / 2.0 + grow_face
        if self.axis == "h":
            return (self.a - grow_along, self.c - h, self.b + grow_along, self.c + h)
        return (self.c - h, self.a - grow_along, self.c + h, self.b + grow_along)

    def along(self, p) -> float:
        return p[0] if self.axis == "h" else p[1]

    def across(self, p) -> float:
        return p[1] - self.c if self.axis == "h" else p[0] - self.c

    def point(self, along: float, across: float = 0.0) -> tuple[float, float]:
        return (along, self.c + across) if self.axis == "h" else (self.c + across, along)


def _jamb_distance(g: Gap, p, end: float) -> float:
    """Distance from p to the jamb segment (across the band) at ``end``."""
    q0, q1 = g.point(end, -g.t / 2.0), g.point(end, g.t / 2.0)
    return LineString([q0, q1]).distance(Point(p))


def _framed_double(g: Gap, arcs: list) -> Optional[list]:
    """real10 (1 Nov 2026): a double door hinged a frame or a jamb block in from both gap ends (the building
    entrance: two 0.93 m leaves hinged 0.27 m in from the jambs of a 2.40 m gap): two arcs hinged within ``HINGE_M`` +
    ``DOOR_FRAME_M`` of each end, with radii half the distance between their hinges (+- ``RADIUS_TOL``) and a door's
    sweep. ``[(item, arc, end)] x 2`` or None."""
    reach = HINGE_M + DOOR_FRAME_M
    near = []
    for it, arc in arcs:
        if not SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]:
            continue
        end = _near_gap_end(g, arc["center"], reach)
        if end is not None:
            near.append((it, arc, end))
    for ia, aa, ea in near:
        if ea != g.a:
            continue
        for ib, ab, eb in near:
            if eb != g.b:
                continue
            half = abs(g.along(ab["center"]) - g.along(aa["center"])) / 2.0
            if half > 0 and all(abs(x["radius"] - half) <= RADIUS_TOL * half for x in (aa, ab)):
                return [(ia, aa, ea), (ib, ab, eb)]
    return None


def _near_gap_end(g: Gap, p, reach: float = HINGE_M) -> Optional[float]:
    for end in (g.a, g.b):
        if _jamb_distance(g, p, end) <= reach:
            return end
        if abs(g.across(p)) <= g.t / 2.0 and abs(g.along(p) - end) <= reach:
            return end
    return None


def _leaf(arc: dict, idx_items: list[_S], used: set) -> Optional[list[_S]]:
    """Strokes forming a thin leaf from the hinge along the arc's start or end radius: their minimum rotated
    rectangle is <= 60 mm wide, 0.85-1.05 r long, starts within 0.10 m of the hinge and runs within 10 deg of the
    radius (the arc ends at the leaf's outer corner, so the leaf is a few degrees off the hinge-to-end radius)."""
    from shapely.geometry import MultiPoint

    hinge, r = arc["center"], arc["radius"]
    for tip in (arc["end"], arc["start"]):
        dx, dy = tip[0] - hinge[0], tip[1] - hinge[1]
        n = math.hypot(dx, dy)
        if n <= 0:
            continue
        ux, uy = dx / n, dy / n
        parts = []
        for it in idx_items:
            if id(it) in used:
                continue
            alongs = []
            ok = True
            for p in it.pts:
                qx, qy = p[0] - hinge[0], p[1] - hinge[1]
                al = qx * ux + qy * uy
                ac = -qx * uy + qy * ux
                if al < -LEAF_START_M or al > LEAF_LENGTH[1] * r + 0.02 or abs(ac) > LEAF_CORRIDOR_M:
                    ok = False
                    break
                alongs.append(al)
            if ok:
                parts.append((it, min(alongs), max(alongs)))
        body = [p for p in parts if p[2] - p[1] >= 0.5 * r]
        if not body:
            continue
        pts = [q for p in body for q in p[0].pts]
        rect = MultiPoint(pts).minimum_rotated_rectangle
        if rect.geom_type != "Polygon":
            continue
        c = list(rect.exterior.coords)
        e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
        e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
        long_e, short_len = (e1, math.hypot(*e2)) if math.hypot(*e1) >= math.hypot(*e2) else (e2, math.hypot(*e1))
        long_len = math.hypot(*long_e)
        off = math.degrees(math.acos(min(1.0, abs(long_e[0] * ux + long_e[1] * uy) / max(long_len, 1e-12))))
        lo = min(p[1] for p in body)
        if lo > LEAF_START_M or short_len > LEAF_WIDTH_M or off > 10.0 or \
                not LEAF_LENGTH[0] * r <= long_len <= LEAF_LENGTH[1] * r:
            continue
        pins = [p for p in parts if p not in body and p[2] <= LEAF_START_M + 0.03]
        return [p[0] for p in body + pins]
    return None


def _arcs_in(items: list[_S]) -> list[tuple[_S, dict]]:
    out = []
    for it in items:
        if it.st.kind not in ("arc", "curve", "polyline", "circle") or len(it.pts) < 4:
            continue
        if it.st.arc is None and it.st.kind == "polyline" and len(it.pts) < 8:
            # A few-vertex polyline the adapter did not call an arc (a square chair: 4 corners fit a circle
            # exactly) is not an arc.
            continue
        arc = arc_of(it.pts)
        if arc is not None and arc["sweep"] >= 30.0:
            out.append((it, arc))
    return out


def classify_gap(g: Gap, index: StrokeIndex, owned_global: set) -> None:
    """Fill ``g.cls`` and ``g.found`` (door/window/doorless/unclassified, see the module docstring)."""
    width = g.width
    zone = index.query(g.rect(grow_face=ZONE_M))
    zone = [it for it in zone if it.st.id not in owned_global]
    arcs = _arcs_in(zone)
    # Door: one arc hinged at a gap end with r = g, or two arcs of g/2 hinged at both ends.
    singles, halves = [], []
    for it, arc in arcs:
        end = _near_gap_end(g, arc["center"])
        if end is None and width - DOOR_FRAME_M <= arc["radius"] < width:
            # real10 (1 Nov 2026): the frame between the jamb and the hinge (a 0.70 m leaf in a 0.85 m gap, hinged
            # 9.5 cm in): the hinge may lie as far in as the leaf is narrower than the gap.
            end = _near_gap_end(g, arc["center"], HINGE_M + (width - arc["radius"]))
        if end is None or not SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]:
            continue
        if abs(arc["radius"] - width) <= RADIUS_TOL * width or width - DOOR_FRAME_M <= arc["radius"] <= width:
            singles.append((it, arc, end))
        elif abs(arc["radius"] - width / 2.0) <= RADIUS_TOL * width / 2.0:
            halves.append((it, arc, end))
    door = None
    if singles:
        it, arc, end = min(singles, key=lambda x: abs(x[1]["radius"] - width))
        door = [(it, arc, end)]
    elif len({h[2] for h in halves}) == 2:
        door = [min((h for h in halves if h[2] == e), key=lambda x: abs(x[1]["radius"] - width / 2.0))
                for e in (g.a, g.b)]
    else:
        door = _framed_double(g, arcs)
    if door:
        used: set = set()
        leaves, parts = [], []
        for it, arc, end in door:
            used.add(id(it))
            leaf = _leaf(arc, zone, used)
            if leaf:
                used.update(id(x) for x in leaf)
                leaves.append(leaf)
            parts.append((it, arc, end, leaf))
        mid = parts[0][1]
        swing_across = statistics.mean(g.across(_arc_mid(p[1])) for p in parts)
        g.cls = "door"
        g.found = {"arcs": [p[0] for p in parts], "arc": [p[1] for p in parts],
                   "hinges": [p[1]["center"] for p in parts], "leaves": [x for lf in leaves for x in lf],
                   "leaf": len(leaves) == len(parts), "swing": 1.0 if swing_across >= 0 else -1.0,
                   "radius": mid["radius"], "double": len(parts) == 2}
        return
    # A door block whose name says it opens without a swing arc (sliding, pocket, folding) is that door, however
    # its leaf is drawn (review #16: drawn closed, its leaf's two sides read as window glass; drawn longer than the
    # gap, it reads as nothing). Before the window rule.
    named = _named_door(g, zone)
    if named is not None:
        leaves, op = named
        g.cls = "door"
        g.found = {"arcs": [], "arc": [], "hinges": [], "leaves": leaves, "leaf": True, "swing": 0.0,
                   "radius": None, "double": False, "sliding": True, "by_name": op}
        return
    # real10 (1 Nov 2026): a door drawn open at 90 degrees without a swing arc (the building entrance's two leaves,
    # the flats' doors): one leaf standing at a gap end as long as the gap, or two at both ends each half of it.
    opened = _open_leaves(g, zone)
    if opened is not None:
        leaves, hinges, swing, double = opened
        g.cls = "door"
        g.found = {"arcs": [], "arc": [], "hinges": hinges, "leaves": leaves, "leaf": True, "swing": swing,
                   "radius": g.width / 2.0 if double else g.width, "double": double, "open_leaf": True}
        return
    # Window: >= 2 strokes parallel to the wall in the band, each spanning >= 80 % of the gap; fix round after P6b:
    # of them >= WINDOW_LINES_MIN offsets of the window's own lines (``_confined`` to the gap), >= GLASS_MIN_LINES of
    # them glass (strictly between the faces).
    band = g.rect(grow_face=BAND_SLACK_M)
    band_items = [it for it in zone if _inside_rect_part(it, band)]
    parallel = []
    framed: set = set()
    glass: set = set()
    faces: dict[int, list] = {}
    for it in band_items:
        # A shape standing out of the wall band (a fixture, a wardrobe, a counter drawn against the wall) has no line
        # of a window (fix round after P6b).
        in_band = all(abs(g.across(q)) <= g.t / 2.0 + BAND_SLACK_M for q in it.pts)
        for p, q in zip(it.pts, it.pts[1:] + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])):
            # 4 Nov 2026 (real17 L-1): in a slanted wall read as steps the window block follows the wall's own angle
            if not (_parallel(p, q, g.axis) or (g.slant and _parallel(p, q, g.axis, g.slant))):
                continue
            off = g.across(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2))
            if abs(off) > g.t / 2.0 + BAND_SLACK_M:
                continue
            lo, hi = sorted((g.along(p), g.along(q)))
            cover = min(hi, g.b) - max(lo, g.a)
            if cover >= WINDOW_COVER * width:
                parallel.append((it, round(off, 3)))
                if in_band and _confined(lo, hi, g.a, g.b):
                    framed.add(round(off, 3))
                    if abs(off) < g.t / 2.0 - GLASS_INSET_M:
                        glass.add(round(off, 3))
                elif abs(off) >= g.t / 2.0 - GLASS_INSET_M:
                    faces.setdefault(1 if off > 0 else -1, []).append((it, lo, hi))
    no_glass = None
    if len({off for _, off in parallel}) >= 2:
        # Raster lines (a scan's or photo's double-line walls) are traced, not drawn: their ends and offsets carry
        # the tracing's error, so the old rule holds for them (synthetic-02's scan).
        if _framed_glass(framed, glass) or any(it.st.source == "raster" for it, _ in parallel):
            g.cls = "window"
            g.found = {"lines": list({id(it): it for it, _ in parallel}.values()), "glass": sorted(glass)}
            return
    if len({off for _, off in parallel}) >= 2:
        no_glass = (f"{len({off for _, off in parallel})} lines along the gap, {len(framed)} of them ending at its "
                    f"jambs and {len(glass)} glass between the faces (>= {WINDOW_LINES_MIN} and >= {GLASS_MIN_LINES} "
                    f"needed): the others run on past the gap (outlines, an axis, a beam above), so no window")
        walled = _wall_faces(g, faces)
        if walled and not any(min(g.b, max(g.along(q) for q in it.pts)) - max(g.a, min(g.along(q) for q in it.pts))
                              > OWN_MARGIN_M for it, _ in arcs):
            # Both faces of the wall are drawn on across the gap on a wall layer and no swing reaches into it: the
            # wall continues (real03's stair-core walls, a DUVAR outline under a door block, read as windows before).
            g.cls = "closed"
            ids = sorted({it.st.id for it in walled})
            layers = sorted({it.st.layer for it in walled})
            g.found = {"faces": ids, "note": f"both faces of the wall are drawn on across the {width:.2f} m gap on the "
                                             f"wall layer ({', '.join(layers)}: {', '.join(ids[:4])}) and no glass "
                                             f"or swing is in it: the wall continues ({no_glass})"}
            return
    # Sliding door (Milestone 10): no swing arc, but one or two leaves (thin closed shapes) parallel to the wall,
    # shorter than the gap, in the band or just beside it.
    leaves = _sliding_leaves(g, zone)
    if leaves:
        g.cls = "door"
        g.found = {"arcs": [], "arc": [], "hinges": [], "leaves": leaves, "leaf": True, "swing": 0.0,
                   "radius": None, "double": False, "sliding": True}
        return
    # 4 Nov 2026 (real17): a window block across the gap is that window; after the doors (real15: balcony sliding doors
    # drawn as blocks on the window layer stay doors) and after the wall faces drawn on across the gap
    named_window = _named_window(g, zone)
    if named_window is not None and g.cls != "closed":
        g.cls = "window"
        g.found = {"lines": named_window[0], "glass": [], "by_name": named_window[1]}
        return
    # Doorless: nothing in the band (the jamb faces at the gap ends do not count) and no door-like arc. Strokes
    # that are only in the classification zone (a chair or a round table beside an open plan) do not count; an
    # arc there counts when it could be a mis-sized door swing: hinged within the zone of a gap end, radius
    # 0.4-1.5 g, not a full circle.
    inner = g.rect(grow_face=BAND_SLACK_M)
    shrink = 0.01
    inner = (inner[0] + shrink, inner[1], inner[2] - shrink, inner[3]) if g.axis == "h" else \
        (inner[0], inner[1] + shrink, inner[2], inner[3] - shrink)
    content = [it for it in index.query(inner) if it.st.id not in owned_global and it.geom.length > 0.005]
    swings = [it for it, arc in arcs if _door_like(g, arc)]
    if not content and not swings:
        g.cls = "empty"
        return
    g.cls = "unclassified"
    g.found = {"content": content + [it for it in swings if it not in content]}
    if no_glass:
        g.found["no_glass"] = no_glass


def _framed_glass(framed: set, glass: set) -> bool:
    """Fix round after P6b: the window's own lines (offsets ``framed``, ``glass`` among them) make a window: >=
    ``WINDOW_LINES_MIN`` offsets, >= ``GLASS_MIN_LINES`` glass, and two glass lines or one between two lines of the
    window (the synthetic convention: a face line, the glass, a face line). A fixture's edge in a thick band with only
    the face beside it (real03's cistern in a 0.45 m duct wall) is none."""
    if len(framed) < WINDOW_LINES_MIN or len(glass) < GLASS_MIN_LINES:
        return False
    return len(glass) >= 2 or any(min(framed) < o < max(framed) for o in glass)


def _confined(lo: float, hi: float, a: float, b: float) -> bool:
    """Fix round after P6b: a line running from ``lo`` to ``hi`` along the wall is a line of the opening from ``a`` to
    ``b`` itself: it ends within the opening +- ``OWN_MARGIN_M`` (glass, frame and sill lines end at the jambs; a face
    line, a room or area outline, an axis or a beam projection runs on past them). Glass also lies strictly between
    the faces (>= ``GLASS_INSET_M`` inside)."""
    return lo >= a - OWN_MARGIN_M and hi <= b + OWN_MARGIN_M


def _wall_faces(g: Gap, faces: dict) -> list:
    """Fix round after P6b (23 Oct 2026): the lines on a wall layer (``dxf_generic.is_wall_hint_layer``: DUVAR, WALL,
    ``... - BA``) that lie on both faces of ``g``, run on past it (``faces``: side -> ``[(item, lo, hi)]``, the face
    lines not confined to the gap) and cover each face from jamb to jamb (+- ``BAND_SLACK_M``), or []. Wall geometry
    drawn across the gap is wall (real03: the DUVAR outlines of the stair-core walls, no wall primitive since a door
    block lies inside them); room or area outlines, beam projections and axes are not, so a doorless passage whose
    room outlines close across it keeps its gap."""
    from wenart.ingest.dxf_generic import is_wall_hint_layer

    out: dict[int, _S] = {}
    for side in (-1, 1):
        lines = sorted(((it, lo, hi) for it, lo, hi in faces.get(side, []) if is_wall_hint_layer(it.st.layer)),
                       key=lambda x: x[1])
        reach = g.a
        for _, lo, hi in lines:
            if lo > reach + BAND_SLACK_M:
                break
            reach = max(reach, hi)
        if not lines or reach < g.b - BAND_SLACK_M:
            return []
        out.update((id(it), it) for it, _, _ in lines)
    return list(out.values())


def _sliding_leaves(g: Gap, zone: list) -> list:
    """Thin closed shapes (<= LEAF_WIDTH_M across) parallel to the gap, 0.45-1.10 x its width long, overlapping it by
    >= 40 % of its width, in the wall band (+- SLIDING_REACH_M across), and either shorter than 0.85 x the gap or
    drawn half open (centre >= 0.2 x the gap off the gap centre; synthetic-07's KAPI_SURME_90: a leaf as long as the
    gap, half in the wall pocket). A window glass rectangle spans its gap, centred: no leaf."""
    out = []
    for items, pts in [([it], it.pts) for it in zone
                       if len(it.pts) >= 4 and (it.st.closed or math.dist(it.pts[0], it.pts[-1]) <= 0.001)] \
            + _line_leaves(g, zone):
        xs, ys = [q[0] for q in pts], [q[1] for q in pts]
        along = (max(xs) - min(xs)) if g.axis == "h" else (max(ys) - min(ys))
        across = (max(ys) - min(ys)) if g.axis == "h" else (max(xs) - min(xs))
        lo, hi = (min(xs), max(xs)) if g.axis == "h" else (min(ys), max(ys))
        mid = ((min(ys) + max(ys)) / 2.0 - g.c) if g.axis == "h" else ((min(xs) + max(xs)) / 2.0 - g.c)
        if across > LEAF_WIDTH_M or not SLIDING_LEAF[0] * g.width <= along <= SLIDING_LEAF[1] * g.width:
            continue
        if min(hi, g.b) - max(lo, g.a) < SLIDING_OVERLAP * g.width or abs(mid) > g.t / 2.0 + SLIDING_REACH_M:
            continue
        shift = abs((lo + hi) / 2.0 - (g.a + g.b) / 2.0)
        if along > SLIDING_SHORT * g.width and shift < SLIDING_SHIFT * g.width:
            continue
        out.extend(items)
    if not out:
        out = _panel_pair(g, _line_leaves(g, zone))
    return out


def _panel_pair(g: Gap, leaves: list[tuple[list, list]]) -> list:
    """A two-panel sliding door drawn with line leaves (real06: two panels of 1.33 m in a 2.95 m gap, 0.45 x the gap
    each): two leaves on different tracks (their middles >= ``PANEL_TRACK_M`` apart across), each ``PANEL_LEAF`` x the
    gap long, in the band, together covering >= ``PANEL_COVER`` of the gap. Their lines, or []."""
    rows = []
    for items, pts in leaves:
        along_vals = [q[0] if g.axis == "h" else q[1] for q in pts]
        across_vals = [q[1] if g.axis == "h" else q[0] for q in pts]
        lo, hi = min(along_vals), max(along_vals)
        mid = (min(across_vals) + max(across_vals)) / 2.0 - g.c
        if PANEL_LEAF[0] * g.width <= hi - lo <= PANEL_LEAF[1] * g.width and abs(mid) <= g.t / 2.0:
            rows.append((lo, hi, mid, items))
    for i, a in enumerate(rows):
        for b in rows[i + 1:]:
            if abs(a[2] - b[2]) < PANEL_TRACK_M:
                continue
            spans = sorted([(max(a[0], g.a), min(a[1], g.b)), (max(b[0], g.a), min(b[1], g.b))])
            cover = sum(max(0.0, y - x) for x, y in spans) - max(0.0, spans[0][1] - spans[1][0])
            if cover >= PANEL_COVER * g.width:
                return a[3] + b[3]
    return []


def _line_leaves(g: Gap, zone: list) -> list[tuple[list, list]]:
    """Leaves drawn as separate lines (real06's sliding door to the veranda: each leaf three lines 1.33 m long,
    25 mm apart): >= 2 straight lines parallel to the gap with the same ends (within ``LEAF_END_M``), all within
    ``LEAF_WIDTH_M`` across. ``[(the lines, their points)]``; the caller applies the leaf rules."""
    lines = []
    for it in zone:
        if len(it.pts) != 2 or it.st.arc is not None:
            continue
        (x0, y0), (x1, y1) = it.pts
        along, across = (abs(x1 - x0), abs(y1 - y0)) if g.axis == "h" else (abs(y1 - y0), abs(x1 - x0))
        if along <= 0 or across > 1e-3 * along:
            continue
        lo, hi = (min(x0, x1), max(x0, x1)) if g.axis == "h" else (min(y0, y1), max(y0, y1))
        lines.append((lo, hi, (y0 + y1) / 2.0 if g.axis == "h" else (x0 + x1) / 2.0, it))
    lines.sort(key=lambda r: (round(r[0] / LEAF_END_M), round(r[1] / LEAF_END_M), r[2]))
    out, used = [], set()
    for i, (lo, hi, off, it) in enumerate(lines):
        if id(it) in used:
            continue
        group = [r for r in lines[i:] if id(r[3]) not in used and abs(r[0] - lo) <= LEAF_END_M
                 and abs(r[1] - hi) <= LEAF_END_M and 0.0 <= r[2] - off <= LEAF_WIDTH_M]
        if len(group) < 2:
            continue
        used.update(id(r[3]) for r in group)
        pts = [p for r in group for p in r[3].pts]
        out.append(([r[3] for r in group], pts))
    return out


def _open_leaves(g: Gap, zone: list) -> Optional[tuple[list, list, float, bool]]:
    """real10 (1 Nov 2026): doors drawn open at 90 degrees with no swing arc. A leaf is a thin shape (a closed outline,
    or >= 2 lines with the same ends, <= ``LEAF_WIDTH_M`` apart) standing across the wall at a gap end (within
    ``LEAF_START_M`` plus its width of the jamb), starting at the wall (its near end within the band +
    ``LEAF_START_M``) and running into a room ``LEAF_LENGTH`` x r long (+ ``LEAF_START_M``): r = the gap (one leaf)
    or half of it (one leaf at each end, on the same side). ``(leaf strokes, hinges, swing side, double)`` or None."""
    rows = []
    for items, pts in _perp_leaves(g, zone):
        alongs = [g.along(q) for q in pts]
        acrosses = [g.across(q) for q in pts]
        width = max(alongs) - min(alongs)
        if width > LEAF_WIDTH_M:
            continue
        near, far = (min(acrosses), max(acrosses)) if abs(min(acrosses)) < abs(max(acrosses)) else \
            (max(acrosses), min(acrosses))
        if abs(near) > g.t / 2.0 + LEAF_START_M or near * far < 0 and abs(near) > g.t / 2.0:
            continue
        x = (max(alongs) + min(alongs)) / 2.0
        # real10: the hinge may stand a door frame or a jamb block in from the gap end (the building entrance's
        # leaves 0.25 m in); the leaf is then measured against the opening that is left
        end = next((e for e in (g.a, g.b) if abs(x - e) <= LEAF_START_M + LEAF_WIDTH_M + DOOR_FRAME_M), None)
        if end is None:
            continue
        rows.append((end, abs(far - near), 1.0 if far > 0 else -1.0, items, x))

    def fits(length: float, r: float, frames: bool) -> bool:
        # As for a swing arc, the frames may take up to ``DOOR_FRAME_M`` of a single leaf's gap (real10's "85/230"
        # balcony door: a 0.77 m leaf in a 0.95 m gap).
        lo = min(LEAF_LENGTH[0] * r, r - DOOR_FRAME_M) if frames else LEAF_LENGTH[0] * r
        return lo <= length <= LEAF_LENGTH[1] * r + LEAF_START_M

    def inset(row) -> float:
        return max(0.0, abs(row[4] - row[0]) - LEAF_START_M - LEAF_WIDTH_M)

    single = [r for r in rows if fits(r[1], g.width - inset(r), True)]
    if single:
        end, _, side, items, _ = min(single, key=lambda r: abs(r[1] - (g.width - inset(r))))
        return items, [g.point(end)], side, False
    halves = {}
    for r in rows:
        halves.setdefault((r[0], r[2]), []).append(r)
    for side in (1.0, -1.0):
        for ra in halves.get((g.a, side), []):
            for rb in halves.get((g.b, side), []):
                half = abs(rb[4] - ra[4]) / 2.0          # the opening between the two hinges, a leaf each
                if fits(ra[1], half, False) and fits(rb[1], half, False):
                    return ra[3] + rb[3], [g.point(g.a), g.point(g.b)], side, True
    return None


def _perp_leaves(g: Gap, zone: list) -> list[tuple[list, list]]:
    """Thin shapes standing across the gap's wall: closed outlines, and groups of >= 2 straight lines across the wall
    with the same ends (within ``LEAF_END_M``), <= ``LEAF_WIDTH_M`` apart. ``[(strokes, points)]``."""
    out = [([it], it.pts) for it in zone if len(it.pts) >= 4 and it.st.arc is None
           and (it.st.closed or math.dist(it.pts[0], it.pts[-1]) <= 0.001)]
    lines = []
    for it in zone:
        if len(it.pts) != 2 or it.st.arc is not None:
            continue
        p0, p1 = it.pts
        run, cross = abs(g.across(p1) - g.across(p0)), abs(g.along(p1) - g.along(p0))
        if run <= 0 or cross > 1e-3 * run:
            continue
        lo, hi = sorted((g.across(p0), g.across(p1)))
        lines.append((lo, hi, (g.along(p0) + g.along(p1)) / 2.0, it))
    lines.sort(key=lambda r: (round(r[0] / LEAF_END_M), round(r[1] / LEAF_END_M), r[2]))
    used: set = set()
    for i, (lo, hi, off, it) in enumerate(lines):
        if id(it) in used:
            continue
        group = [r for r in lines[i:] if id(r[3]) not in used and abs(r[0] - lo) <= LEAF_END_M
                 and abs(r[1] - hi) <= LEAF_END_M and 0.0 <= r[2] - off <= LEAF_WIDTH_M]
        if len(group) < 2:
            continue
        used.update(id(r[3]) for r in group)
        out.append(([r[3] for r in group], [q for r in group for q in r[3].pts]))
    return out


def _named_door(g: Gap, zone: list) -> Optional[tuple[list, str]]:
    """(strokes, operation) of the door block instance in this gap whose name holds a door word (``DOOR_WORDS``, no
    window word) and a no-swing operation (``NO_SWING_OPERATIONS``: KAPI_SURME_90, SLIDING_DOOR, katlanır kapı): its
    strokes in the zone overlap the gap by >= 40 % of its width and their middle lies in the wall band (+-
    ``SLIDING_REACH_M``). None when no such block is drawn there."""
    groups: dict[str, list] = {}
    ops: dict[str, str] = {}
    for it in zone:
        if not it.st.block:
            continue
        names = it.st.block.split("/")
        op = operation_word(names)
        if op not in NO_SWING_OPERATIONS:
            continue
        for i, name in enumerate(names):
            folded = name.translate(_FOLD).upper()
            if any(w in folded for w in DOOR_WORDS) and not any(w in folded for w in WINDOW_WORDS):
                parts = it.st.id.split("/")
                key = "/".join(parts[:i + 1]) if len(parts) > len(names) else it.st.block
                groups.setdefault(key, []).append(it)
                ops[key] = op
                break
    best = None
    for key, items in groups.items():
        along = [g.along(p) for it in items for p in it.pts]
        across = [g.across(p) for it in items for p in it.pts]
        overlap = min(max(along), g.b) - max(min(along), g.a)
        if overlap < SLIDING_OVERLAP * g.width or abs((min(across) + max(across)) / 2.0) > g.t / 2.0 + SLIDING_REACH_M:
            continue
        if best is None or overlap > best[0]:
            best = (overlap, key)
    return None if best is None else (sorted(groups[best[1]], key=lambda it: it.st.id), ops[best[1]])


def _window_name(name: str) -> bool:
    folded = name.translate(_FOLD).upper()
    if any(w in folded for w in DOOR_WORDS):
        return False
    if any(w in folded for w in WINDOW_WORDS):
        return True
    return any(tok.rstrip("0123456789") in WINDOW_TOKENS for tok in folded.replace(".", "_").split("_") if tok)


def _named_window(g: Gap, zone: list) -> Optional[tuple[list, str]]:
    """4 Nov 2026 (real17 L-1: the WC windows are a detailed "fm-win1" block on the "pencere" layer whose glass
    lines cover 62 % of the gap between thick frame profiles): (strokes, name) of the window block instance in this
    gap, named for a window (``WINDOW_WORDS``, a ``WINDOW_TOKENS`` name part; no door word) or drawn on a window
    layer, whose strokes together span >= ``WINDOW_COVER`` of the gap along and whose middle lies in the wall band
    (+- ``BAND_SLACK_M``). None when no such block is drawn there."""
    groups: dict[str, list] = {}
    names_of: dict[str, str] = {}
    for it in zone:
        if not it.st.block:
            continue
        names = it.st.block.split("/")
        parts = it.st.id.split("/")
        hit = next((i for i, name in enumerate(names) if _window_name(name)), None)
        if hit is None and it.st.layer and _window_name(it.st.layer):
            hit = len(names) - 1
        if hit is None:
            continue
        key = "/".join(parts[:hit + 1]) if len(parts) > len(names) else it.st.block
        groups.setdefault(key, []).append(it)
        names_of[key] = names[hit] if _window_name(names[hit]) else f"{names[hit]} on layer {it.st.layer}"
    best = None
    for key, items in groups.items():
        along = [g.along(p) for it in items for p in it.pts]
        across = [g.across(p) for it in items for p in it.pts]
        overlap = min(max(along), g.b) - max(min(along), g.a)
        if overlap < WINDOW_COVER * g.width or abs((min(across) + max(across)) / 2.0) > g.t / 2.0 + BAND_SLACK_M:
            continue
        if max(along) - min(along) > g.width + 2.0 * OWN_MARGIN_M:
            continue                                # a block running on past the gap is not this gap's window
        if best is None or overlap > best[0]:
            best = (overlap, key)
    return None if best is None else (sorted(groups[best[1]], key=lambda it: it.st.id), names_of[best[1]])


def operation_word(names) -> Optional[str]:
    """The operation a block name says (``OPERATION_WORDS``), or None."""
    for name in names:
        folded = (name or "").translate(_FOLD).upper()
        for key, op in OPERATION_WORDS:
            if key in folded:
                return op
    return None


def set_operation(item: OpeningItem, operation: Optional[str], source: Optional[str]) -> None:
    """``operation`` / ``operation_source`` of an opening (§1.6b row 17). Set as attributes: the pipeline copies them
    into the building's openings (null = swing, assumed)."""
    item.operation = operation
    item.operation_source = source


def _door_operation(item: OpeningItem, strokes: list, double: bool, sliding: bool = False) -> None:
    named = operation_word([n for st in strokes if st.block for n in st.block.split("/")])
    if named is not None:
        set_operation(item, named, "block_name")
    else:
        set_operation(item, "sliding" if sliding else ("double" if double else "swing"), "geometry")


def _door_like(g: Gap, arc: dict) -> bool:
    """An arc that may be a door swing of this gap, drawn off the door rule's tolerances."""
    width = g.width
    if not DOOR_LIKE_RADIUS[0] * width <= arc["radius"] <= DOOR_LIKE_RADIUS[1] * width or arc["sweep"] >= 300.0:
        return False
    return min(_jamb_distance(g, arc["center"], end) for end in (g.a, g.b)) <= ZONE_M


def _arc_mid(arc: dict) -> tuple[float, float]:
    cx, cy = arc["center"]
    a0 = math.atan2(arc["start"][1] - cy, arc["start"][0] - cx)
    a1 = math.atan2(arc["end"][1] - cy, arc["end"][0] - cx)
    d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
    am = a0 + d / 2.0
    return (cx + arc["radius"] * math.cos(am), cy + arc["radius"] * math.sin(am))


def _parallel(p, q, axis: str, slant: float = 0.0) -> bool:
    if math.dist(p, q) <= 1e-9:
        return False
    ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180.0
    target = (0.0 if axis == "h" else 90.0) + slant
    d = abs(ang - target) % 180.0
    return min(d, 180.0 - d) <= WINDOW_ANGLE_DEG


def _inside_rect_part(it: _S, rect) -> bool:
    return it.geom.intersects(sbox(*rect))


# --------------------------------------------------------------------------
# Main entry
# --------------------------------------------------------------------------

ANGLED_FRAME_MIN_M = 0.6        # R35: a direction off the plan's frame with at least this much wall gets its own pass
ANGLED_FRAME_BIN_DEG = 1.0      # ... walls within this angle (mod 90) are one direction
OPENING_SAME_M = 0.3            # ... an opening of an angled pass this near an opening already read is that one


def angled_frames(walls: list[WallItem], theta: float) -> list[float]:
    """R35 (20 Nov 2026): the wall directions (mod 90, in (-45, 45]) off the frame ``theta`` by more than
    ``AXIS_TOL_DEG`` with at least ``ANGLED_FRAME_MIN_M`` of wall, longest first (pure)."""
    bins: dict[int, float] = {}
    for w in walls:
        length = math.dist(w.start, w.end)
        if length <= 0:
            continue
        ang = math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 90.0
        d = (ang - theta) % 90.0
        if min(d, 90.0 - d) <= AXIS_TOL_DEG:
            continue
        k = int(round(ang / ANGLED_FRAME_BIN_DEG)) % int(round(90.0 / ANGLED_FRAME_BIN_DEG))
        bins[k] = bins.get(k, 0.0) + length
    out = []
    for k, total in sorted(bins.items(), key=lambda kv: -kv[1]):
        if total < ANGLED_FRAME_MIN_M:
            continue
        ang = k * ANGLED_FRAME_BIN_DEG
        out.append(ang - 90.0 if ang > 45.0 else ang)
    return out


def gaps_and_openings(walls: list[WallItem], strokes_m: list[Stroke], file_rel: str, page_no: int,
                      units_to_m: Optional[float] = None, dimension_ids=frozenset(), wall_strokes=(), outdoor_points=(),
                      room_points=()) -> tuple[list[WallItem], list[OpeningItem], list[dict], set[str]]:
    """``gaps_and_openings_frame`` in the plan's dominant frame, then (20 Nov 2026, rule R35 ``angled_wall``) once in
    the frame of each wall direction off it (``angled_frames``): the runs, gaps, doors and windows of a wall drawn at
    an angle are read in its own frame, as the axis walls are in theirs (real20's angled hall doors were lost once
    their walls stayed at their angle). An opening an angled pass finds within ``OPENING_SAME_M`` of one already read
    is that one (dropped); the strokes the first pass owns are not offered again."""
    from wenart.ingest import rule_guards as RG

    out_walls, openings, log, owned = gaps_and_openings_frame(
        walls, strokes_m, file_rel, page_no, units_to_m, dimension_ids, wall_strokes, outdoor_points, room_points)
    if not RG.active("angled_wall"):
        return out_walls, openings, log, owned
    for ang in angled_frames(out_walls, dominant_angle(out_walls)):
        free = [st for st in strokes_m if st.id not in owned]
        _pieces, others = pieces_of(out_walls, ang)
        w2, o2, l2, own2 = gaps_and_openings_frame(out_walls, free, file_rel, page_no, units_to_m, dimension_ids, (),
                                                   outdoor_points, room_points, theta=ang)
        # the pass returns its merged walls first, then the walls it did not take (``others``) in their order: the
        # wall indices of the earlier log entries move with them (only those walls were an earlier pass's pieces)
        n2 = len(w2) - len(others)
        moved = {old: n2 + r for r, old in enumerate(others)}
        log = [_moved_entry(e, moved) for e in log]
        index = {}
        # an end gap of an angled wall (from its free end along its own line) runs across the axis walls around it:
        # its door is another wall's (real10's 45-degree chamfer took the arc of the door beside it); an angled pass
        # keeps the gaps between its pieces and the symbols drawn on its walls
        ends = {e["opening"] for e in l2 if e.get("kind") == "end" and isinstance(e.get("opening"), int)}
        for j, o in enumerate(o2):
            # ... and an opening of an angled pass fits within its angled wall (a symbol of the axis wall beside a short
            # angled piece is that wall's: real10's 0.8 m door swing beside a 0.47 m chamfer)
            if j not in ends and _fits_angled_host(o, w2, ang) \
                    and all(math.dist(o.center, q.center) > OPENING_SAME_M for q in openings):
                index[j] = len(openings)
                openings = openings + [o]
        for e in l2:
            e = dict(e, frame_deg=round(ang, 2))
            if isinstance(e.get("opening"), int):
                if e["opening"] in index:
                    e["opening"] = index[e["opening"]]
                else:
                    e.pop("opening")
                    e["note"] = ((e.get("note") + "; ") if e.get("note") else "") + "an opening read already"
            log.append(e)
        out_walls, owned = w2, owned | set(own2)
    return out_walls, openings, log, owned


def _fits_angled_host(o: OpeningItem, walls: list[WallItem], ang: float, tol: float = 0.1) -> bool:
    """R35: whether an opening lies along a wall of the frame ``ang`` (within ``AXIS_TOL_DEG``) whose length holds its
    width (``tol`` of slack at each end; pure). Virtual openings (separators) pass."""
    if getattr(o, "virtual", False):
        return True
    half = float(o.width) / 2.0
    for w in walls:
        length = math.dist(w.start, w.end)
        if length <= 1e-9:
            continue
        a = math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 90.0
        d = (a - ang) % 90.0
        if min(d, 90.0 - d) > AXIS_TOL_DEG:
            continue
        ux, uy = (w.end[0] - w.start[0]) / length, (w.end[1] - w.start[1]) / length
        rx, ry = o.center[0] - w.start[0], o.center[1] - w.start[1]
        along, across = rx * ux + ry * uy, abs(-rx * uy + ry * ux)
        if across <= float(w.thickness) / 2.0 + 0.05 and half - tol <= along <= length - half + tol:
            return True
    return False


def _moved_entry(e: dict, moved: dict) -> dict:
    """A log entry with its wall indices (``wall``, ``of``, ``to``, ``walls``) moved by ``moved`` (pure)."""
    out = dict(e)
    for key in ("wall", "of", "to"):
        if isinstance(out.get(key), int) and out[key] in moved:
            out[key] = moved[out[key]]
    if isinstance(out.get("walls"), list):
        out["walls"] = [moved.get(k, k) if isinstance(k, int) else k for k in out["walls"]]
    return out


def gaps_and_openings_frame(walls: list[WallItem], strokes_m: list[Stroke], file_rel: str, page_no: int,
                            units_to_m: Optional[float] = None, dimension_ids=frozenset(), wall_strokes=(),
                            outdoor_points=(), room_points=(), theta: Optional[float] = None
                            ) -> tuple[list[WallItem], list[OpeningItem], list[dict], set[str]]:
    """Merge wall runs, find and classify gaps, extend free-end walls that host a drawn door or window.

    ``strokes_m`` are the page's strokes in page metres **without** the wall primitives (hatch lines, fills).
    Returns ``(walls, openings, gap_log, owned)``: the merged/extended walls (page metres), the openings on them
    (page metres; ``box`` in page units when ``units_to_m`` is given), one log dict per gap and free end, and the
    ids of the strokes the openings own. 6 Nov 2026: ``wall_strokes`` (the wall primitives' strokes, page metres)
    let a door leaf read as a thin wall go back to the door (``leaf_walls``). 12 Nov 2026: ``outdoor_points`` (page
    metres: the outdoor-space labels, balcony, terrace, courtyard ...) mark closed spaces open to the sky
    (``_outside_test``); ``room_points`` (the labels of rooms one lives in) mark closed spaces that never are.
    """
    leaf_log: list[dict] = []
    leaves = leaf_walls(walls, wall_strokes, strokes_m)
    if leaves:
        by_id = {st.id: st for st in wall_strokes}
        for k in sorted(leaves):
            w = walls[k]
            leaf_log.append({"kind": "wall_piece", "wall": str(w.entity),
                             "note": f"a door leaf, not a wall: a {math.dist(w.start, w.end):.2f} x "
                                     f"{float(w.thickness):.3f} m piece drawn on the door layer "
                                     f"{by_id[leaves[k][0]].layer} (its strokes go back to the door symbol)"})
        strokes_m = list(strokes_m) + [by_id[i] for k in sorted(leaves) for i in leaves[k]]
        walls = [w for k, w in enumerate(walls) if k not in leaves]
    theta = dominant_angle(walls) if theta is None else float(theta)
    pieces, others = pieces_of(walls, theta)
    # 3 Nov 2026 (UL261, UL296): the drawing's notation (axis lines, dimensions and their tick marks) is never a
    # gap's content
    from wenart.ingest.generic import axes as AX
    notation = AX.notation_ids(strokes_m, dimension_ids)
    index = StrokeIndex([st for st in strokes_m if st.id not in notation], theta)
    raster = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)
    edge_m = RASTER_EDGE_PX * units_to_m if raster and units_to_m else 0.0
    runs = group_runs(pieces)
    order = {id(q): q.run for q in pieces}
    caps, cap_log = end_caps(runs, edge_m)
    ends = [p for p in pieces if id(p) not in caps]    # the pieces that end walls (frames and nubs do not)
    cap_pieces = [p for p in pieces if id(p) in caps]
    cap_of = {e["piece"]: e["of"] for e in cap_log}        # a cap's piece -> the wall piece whose end it caps
    runs = [r for r in ([q for q in run if id(q) not in caps] for run in runs) if r]
    runs, piece_log = join_fused_strips(runs, index, edge_m)
    piece_log += cap_log
    join_notes = {e["piece"]: e["note"] for e in piece_log}
    # An end cap stays a wall of its own, in its place among the runs (the output walls keep their order).
    runs = sorted(runs + [[p] for p in pieces if id(p) in caps],
                  key=lambda r: (min(order[id(q)] for q in r), r[0].a))
    for i, run in enumerate(runs):
        for q in run:
            q.run = i
    ctx = _Ctx(file_rel, page_no, units_to_m, theta, raster, window_symbols=window_symbols(strokes_m))
    if wall_strokes:
        ctx.rest_index = StrokeIndex([st for st in strokes_m if st.id not in notation] + list(wall_strokes), theta)
    owned: set[str] = set()
    gaps: list[Gap] = []
    merge_after: dict[int, set[int]] = {}        # run -> positions i where pieces i and i+1 join
    lined_after: dict[int, dict[int, dict]] = {}  # run -> position i -> the lining of the gap that splits it there

    # (a) + (c): run gaps, split at perpendicular walls inside the band.
    for ri, run in enumerate(runs):
        merge_after[ri] = set()
        lined_after[ri] = {}
        for i in range(len(run) - 1):
            p, q = run[i], run[i + 1]
            if q.a <= p.b + GAP_IGNORE_M:
                merge_after[ri].add(i)
                continue
            subs = _split(p, q, ends)
            if any(b - a > GAP_MAX_M for a, b in subs):
                for a, b in subs:
                    gaps.append(Gap("run" if len(subs) == 1 else "split", p.axis, p.c, _run_t(run), a, b, [p, q],
                                    cls="open"))
                continue
            trial = set(owned)
            found = []
            for a, b in subs:
                g = Gap("run" if len(subs) == 1 else "split", p.axis, _run_c(run), _run_t(run), a, b, [p, q])
                if g.width >= GAP_MIN_M:
                    classify_gap(g, index, trial)
                # Fix round after P6b: wall material of other pieces fills the gap (real03's shear-wall core); a door
                # symbol in it keeps the door (review of the fix round: the drawn swing outranks the decomposition).
                cover = _inside_wall(g, pieces, run) if g.cls != "door" else None
                if cover is not None:
                    g.cls = "closed"
                    g.found = {"inside": [w.k for w in cover],
                               "note": f"a {g.width:.3f} m gap inside wall material ({len(cover)} other piece(s) on "
                                       f"this axis cover its {g.t:.2f} m band along its whole width): closed, no "
                                       f"opening"}
                    _own(g, index, trial)
                elif g.width < GAP_MIN_M:
                    g.cls = "closed"
                else:
                    _own(g, index, trial)
                found.append(g)
            lining = _lining(run, p, q, runs, found)
            if lining is not None:
                # Fix round after P6b: a thinner wall runs along one face through the gap (real03's shear walls on
                # the hall-living partition): the pieces are not one wall with openings between them.
                for g in found:
                    g.found = {"lining": lining, "split_reason": lining["note"], "owned": g.found.get("owned", [])}
                    g.cls = "open"
                lined_after[ri][i] = lining
                owned.update(trial)                  # the band's structure lines stay out of the furniture
                gaps.extend(found)
                continue
            two_walls = q.a - p.b > GAP_MAX_M or _crossed(p, q, ends)
            if len(subs) > 1 and two_walls and any(g.cls in ("empty", "unclassified") for g in found):
                # A gap open by itself (> 3 m) or crossed by walls, and a part holds no door or window symbol: two
                # walls on one line (real02: the bedroom walls of both dwellings, the corridor and a bathroom
                # between them), never one wall across; free ends cast their own end gaps (b).
                for g in found:
                    g.found = {"split_reason": "a split part holds no door or window: the pieces are not one wall"}
                    g.cls = "open"
                gaps.extend(found)
                continue
            merge_after[ri].add(i)
            owned.update(trial)
            gaps.extend(found)

    # real10 (1 Nov 2026): a corner window (glass running round the corner with no wall piece there) gets a corner
    # post where the two walls' lines meet; the end gaps below then read its two windows.
    posts = _corner_posts(ends, index, owned, ctx, len(walls))
    for post in posts:
        ends.append(post)
        post.run = len(runs)
        runs.append([post])
        merge_after[post.run] = set()

    # (b): end gaps from free ends.
    end_log: list[dict] = []
    for p in ends:
        for which in ("start", "end"):
            corner = None
            if not _is_free(p, which, ends):
                # real10 (1 Nov 2026): a door right at an L corner (the master bedroom's balcony door): the wall ends
                # inside the perpendicular wall it meets; the gap is cast from that wall's far face and kept only for
                # a drawn door or window (below).
                corner = _buried_end(p, which, ends)
                if corner is None:
                    continue
            # 4 Nov 2026: a frame or nub at a wall's end (a cap) is wall material a cast from a free end hits too;
            # never the cap of this wall's own end (its frame belongs to the opening the cast is looking for: P7,
            # real01's store door)
            others_caps = [c for c in cap_pieces if cap_of.get(c.k) != p.k]
            hit = _cast(p, which, ends, others_caps) if corner is None else _cast_from(p, which, ends, corner)
            if hit is None:
                if corner is None:                  # a buried end is no free end: no separator candidate
                    end_log.append({"piece": p, "which": which, "gap": None})
                continue
            q, a, b = hit
            # The same gap as a classified run gap: the run gap holds it (an open run gap does not).
            # 4 Nov 2026 (real17 L-1): two free ends that cast at each other face one gap, however far their lines lie
            # apart (the steps of a slanted wall): the first cast holds it.
            dup = next((g for g in gaps if g.cls != "open" and g.axis == p.axis
                        and (abs(g.c - p.c) <= RUN_OFFSET_M + 0.01 or (g.kind == "end" and g.hit is p and g.free[0] is q))
                        and min(g.b, b) - max(g.a, a) >= 0.5 * min(g.width, b - a)), None)
            if dup is not None:
                if corner is None:
                    end_log.append({"piece": p, "which": which, "gap": dup, "same_as_run_gap": True})
                continue
            # Fix round after P6b: never across a lined gap (the thinner wall along its face holds that stretch).
            if any(g.found.get("lining") and g.axis == p.axis and abs(g.c - p.c) <= RUN_OFFSET_M + 0.01
                   and min(g.b, b) - max(g.a, a) > GAP_IGNORE_M for g in gaps):
                if corner is None:
                    end_log.append({"piece": p, "which": which, "gap": None})
                continue
            g = Gap("end", p.axis, p.c, p.t, a, b, [p, q], free=(p, which), hit=q, slant=_slant(p, q))
            if g.width < GAP_MIN_M:
                g.cls = "closed"
            elif corner is not None:
                classify_gap(g, index, owned)
                # Only a door with a drawn swing (arc or open leaf): no window or sliding-leaf guess beside a corner
                # (real03: the lines between its two lift shafts read as a 2.6 m 'window' this way).
                if not (g.cls == "door" and (g.found.get("arcs") or g.found.get("open_leaf"))):
                    continue                        # a buried end is no free end: nothing logged
                _own(g, index, owned)
            elif any(q is post for post in posts):
                # A corner window's glass runs on to the frame's outer corner, past the post's near face.
                far = Gap("end", p.axis, p.c, p.t, a, b + q.t if which == "end" else b, [p, q], free=(p, which),
                          hit=q)
                if which == "start":
                    far.a = a - q.t
                classify_gap(far, index, owned)
                g.cls, g.found = far.cls, far.found
                if g.cls in ("door", "window") or g.found.get("faces"):
                    _own(g, index, owned)
            else:
                classify_gap(g, index, owned)
                if g.cls in ("door", "window") or g.found.get("faces"):
                    _own(g, index, owned)
            gaps.append(g)
            end_log.append({"piece": p, "which": which, "gap": g})

    # Extend free-end walls that host a door or window (or close a gap < 0.25 m).
    extended: dict[int, tuple[list[str], str]] = {}
    for g in gaps:
        if g.kind != "end" or g.cls not in ("door", "window", "closed"):
            continue
        p, which = g.free
        if which == "start":
            p.a = g.a
        else:
            p.b = g.b
        ids = [it.st.id for it in g.found.get("arcs", []) + g.found.get("leaves", []) + g.found.get("lines", [])]
        reason = {"door": "extended to host the drawn door", "window": "extended to host the drawn window",
                  "closed": f"extended over a {g.width:.3f} m gap (< {GAP_MIN_M} m, closed)"}[g.cls]
        if g.found.get("faces"):
            reason = f"extended over a {g.width:.3f} m gap: {g.found['note']}"
            ids = list(g.found["faces"])
        old_ids, old_reason = extended.get(p.k, ([], ""))
        extended[p.k] = (old_ids + ids, (old_reason + "; " if old_reason else "") + reason)

    # Build the output walls: one WallItem per merged run segment, other walls unchanged.
    out_walls: list[WallItem] = []
    piece_out: dict[int, int] = {}
    for ri, run in enumerate(runs):
        seg = [run[0]]
        # Fix round after P6b: the segments lined gaps split apart (one wall before), and those linings.
        group: list[tuple[int, list[Piece]]] = []
        group_linings: list[dict] = []
        for i in range(1, len(run) + 1):
            if i < len(run) and (i - 1) in merge_after[ri]:
                seg.append(run[i])
                continue
            out_walls.append(_merged_wall(seg, ctx, extended, join_notes))
            for q in seg:
                piece_out[q.k] = len(out_walls) - 1
            group.append((len(out_walls) - 1, seg))
            if i < len(run) and (i - 1) in lined_after[ri]:
                group_linings.append(lined_after[ri][i - 1])
            else:
                _mark_lined(out_walls, group, group_linings, ctx)
                group, group_linings = [], []
            if i < len(run):
                seg = [run[i]]
    for k in others:
        out_walls.append(walls[k])
    _trim_into_bands(out_walls, theta)

    exterior = _exterior_test(out_walls)
    openings: list[OpeningItem] = []
    log: list[dict] = []
    gap_pos: dict[int, int] = {}
    for g in gaps:
        entry = _log_entry(g, theta, piece_out)
        if g.cls in ("door", "window") or (g.kind != "end" and g.cls in ("empty", "unclassified")):
            openings.append(_opening(g, ctx, exterior))
            entry["opening"] = len(openings) - 1
        if g.cls == "closed" and g.found.get("note"):
            entry["note"] = g.found["note"]
        elif g.cls == "closed":
            entry["warning"] = f"gap of {g.width:.3f} m < {GAP_MIN_M} m closed"
        gap_pos[id(g)] = len(log)
        log.append(entry)
    for e in end_log:
        p, which = e["piece"], e["which"]
        face = p.end_face(which)
        mid = ((face[0][0] + face[1][0]) / 2, (face[0][1] + face[1][1]) / 2)
        d = -1.0 if which == "start" else 1.0
        direction = (d, 0.0) if p.axis == "h" else (0.0, d)
        g = e["gap"]
        log.append({"kind": "free_end", "wall": piece_out.get(p.k), "end": which,
                    "point": _out(mid, theta), "face": [_out(face[0], theta), _out(face[1], theta)],
                    "direction": [round(v, 6) for v in _rot(direction, theta)], "thickness": round(p.t, 4),
                    "gap_class": (g.cls if g is not None else "none"),
                    "gap": (None if g is None else gap_pos.get(id(g))),
                    "same_as_run_gap": bool(e.get("same_as_run_gap"))})
    for e in piece_log:
        entry = dict(e, wall=piece_out.get(e["piece"]))
        entry["input_wall"] = entry.pop("piece")
        if "of" in entry:
            entry["of"] = piece_out.get(entry["of"])
        log.append(entry)

    # Continuous-wall symbols (synthetic convention, raster double-line walls).
    cont_doors, cont_windows = _continuous_symbols(out_walls, index, owned, theta, ctx, openings, inner_check=True,
                                                   outdoor=outdoor_points, rooms=room_points)
    openings.extend(cont_doors)
    openings.extend(cont_windows)
    for o in cont_doors + cont_windows:
        log.append({"kind": "continuous", "class": o.kind, "center": list(o.center), "width": o.width,
                    "entity": o.entity})
    log.extend(ctx.dropped)
    log.extend(leaf_log)
    return out_walls, openings, log, owned


LEAF_WALL_MAX_M = LEAF_WIDTH_M + 0.02    # 6 Nov 2026: a door leaf read as a wall is at most this thick ...
LEAF_WALL_MIN_LEN_M = 0.4                # ... and at least this long (a leaf, not a frame or a jamb block)


LEAF_WALL_MAX_LEN_M = CONTINUOUS_RADIUS_M[1] * LEAF_LENGTH[1]   # 12 Nov 2026: ... and at most a door leaf long


def _stroke_len(st: Stroke) -> float:
    return sum(math.dist(a, b) for a, b in zip(st.pts, st.pts[1:]))


def leaf_walls(walls: list[WallItem], wall_strokes, strokes_m=()) -> dict[int, list[str]]:
    """6 Nov 2026 (real03: the bedrooms' door blocks draw the open leaf as a 0.80 x 0.05 m rectangle on the door
    layer; the wall mask read it as a thin wall, so the swing had no leaf and three bedrooms and a flat's entrance had
    no door): ``{wall index: its stroke ids}`` of the walls that are door leaves: at most ``LEAF_WALL_MAX_M`` thick and
    ``LEAF_WALL_MAX_LEN_M`` long, none of their strokes on a layer that draws walls, and their strokes on a door layer
    or in a block named for a door (``_on_door_layer``) running ``LEAF_WALL_MIN_LEN_M`` at least along the piece (12 Nov
    2026, review B-r03-leaf-incomplete: real03's fire-stair and safety-lobby leaves carry a longer background-view
    line); (review B-OPN-10: a WC partition or a sliding screen on the door layer is no leaf) a door swing among
    ``strokes_m`` is hinged at one end of that run, its radius the run's length (``LEAF_LENGTH``) and its sweep a
    door's (``SWEEP_DEG``)."""
    from wenart.ingest.generic import layer_names as LN

    if not wall_strokes:
        return {}
    by_id = {st.id: st for st in wall_strokes}
    cands = {}
    for k, w in enumerate(walls):
        length = math.dist(w.start, w.end)
        if float(w.thickness) > LEAF_WALL_MAX_M or not 0 < length <= LEAF_WALL_MAX_LEN_M:
            continue
        ids = [e.strip() for e in str(w.entity or "").split(",") if e.strip()]
        sts = [by_id.get(i) for i in ids]
        if not ids or any(st is None for st in sts) or any(LN.draws_walls(st.layer) for st in sts):
            continue
        door = [q for st in sts if _on_door_layer(st) for q in st.pts]
        if not door:
            continue
        ux, uy = (w.end[0] - w.start[0]) / length, (w.end[1] - w.start[1]) / length
        proj = [(q[0] - w.start[0]) * ux + (q[1] - w.start[1]) * uy for q in door]
        lo, hi = max(min(proj), 0.0), min(max(proj), length)
        if hi - lo >= LEAF_WALL_MIN_LEN_M:
            cands[k] = (ids, [(w.start[0] + ux * t, w.start[1] + uy * t) for t in (lo, hi)])
    if not cands:
        return {}
    swings = []
    for st in strokes_m:
        if st.kind not in ("arc", "curve", "polyline", "circle") or len(st.pts) < 4:
            continue
        if st.arc is None and st.kind == "polyline" and len(st.pts) < 8:
            continue
        arc = arc_of(st.pts)
        if arc is not None and SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]:
            swings.append(arc)
    out = {}
    for k, (ids, ends) in cands.items():
        run = math.dist(*ends)
        reach = HINGE_M + float(walls[k].thickness)
        if any(LEAF_LENGTH[0] * a["radius"] <= run <= LEAF_LENGTH[1] * a["radius"]
               and min(math.dist(a["center"], e) for e in ends) <= reach for a in swings):
            out[k] = ids
    return out


def openings_on_walls(walls: list[WallItem], strokes_m: list[Stroke], file_rel: str, page_no: Optional[int],
                      units_to_m: Optional[float] = None, owned: Optional[set] = None) -> list[OpeningItem]:
    """The door and window symbols drawn across continuous walls (the continuous-wall rule of
    ``gaps_and_openings``, without its run merging and gap casting): walls inferred by code have no drawn gaps, so a
    door or window is read only where its symbol is drawn (``generic.outlines``). ``owned`` (updated in place) holds
    the stroke ids other openings own already."""
    if not walls:
        return []
    theta = dominant_angle(walls)
    index = StrokeIndex(strokes_m, theta)
    raster = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)
    ctx = _Ctx(file_rel, page_no, units_to_m, theta, raster)
    taken = owned if owned is not None else set()
    doors, windows = _continuous_symbols(walls, index, taken, theta, ctx, [])
    return doors + windows


@dataclass
class _Ctx:
    file_rel: str
    page_no: int
    units_to_m: Optional[float]
    theta: float
    raster: bool
    # Fix round after P6b, review: the continuous-wall window candidates dropped for want of glass (gap log entries)
    dropped: list = field(default_factory=list)
    # 12 Nov 2026 (review B2 FC-04): the page draws its windows with symbols of their own (``window_symbols``)
    window_symbols: bool = False
    # 12 Nov 2026 (review B2 FC-06): the strokes a gap's rest is read from, the wall primitives' among them
    rest_index: object = None

    def evidence(self, method: str, confidence: float, entity: str, note: Optional[str] = None,
                 box_units: Optional[list] = None) -> dict:
        if self.raster and method == "vector":
            method, confidence = "raster", min(confidence, CONF_RASTER)
        ev = B.evidence(self.file_rel, method, round(confidence, 3), page=self.page_no, entity=entity,
                        pixel_box=box_units if (method == "raster" and box_units) else None)
        if note:
            ev["note"] = note
        return ev

    def box(self, pts_m) -> list[float]:
        xs = [p[0] for p in pts_m]
        ys = [p[1] for p in pts_m]
        bx = [min(xs), min(ys), max(xs), max(ys)]
        if self.units_to_m:
            bx = [v / self.units_to_m for v in bx]
        return [round(v, 3) for v in bx]


def _out(p, theta: float) -> list[float]:
    q = _rot(p, theta)
    return [round(q[0], 4), round(q[1], 4)]


def _run_c(run: list[Piece]) -> float:
    total = sum(q.b - q.a for q in run)
    return sum(q.c * (q.b - q.a) for q in run) / total if total > 0 else run[0].c


def _run_t(run: list[Piece]) -> float:
    return _weighted_median([(q.t, q.b - q.a) for q in run])


def _weighted_median(values: list[tuple[float, float]]) -> float:
    vals = sorted(values)
    total = sum(w for _, w in vals)
    acc = 0.0
    for v, w in vals:
        acc += w
        if acc >= total / 2.0:
            return v
    return vals[-1][0]


def _split(p: Piece, q: Piece, pieces: list[Piece]) -> list[tuple[float, float]]:
    """The run gap between p and q minus the perpendicular walls reaching into the run band (gap kind c)."""
    a, b = p.b, q.a
    lo, hi = p.c - p.t / 2.0, p.c + p.t / 2.0
    cuts = []
    for w in pieces:
        if w.axis == p.axis:
            continue
        w0, w1 = w.c - w.t / 2.0, w.c + w.t / 2.0          # its extent along our axis
        if w1 <= a + GAP_IGNORE_M or w0 >= b - GAP_IGNORE_M:
            continue
        reach = min(w.b, hi) - max(w.a, lo)                 # how far it reaches into the band
        if reach >= 0.5 * p.t:
            cuts.append((max(w0, a), min(w1, b)))
    subs = [(a, b)]
    for c0, c1 in sorted(cuts):
        nxt = []
        for s0, s1 in subs:
            if c1 <= s0 or c0 >= s1:
                nxt.append((s0, s1))
                continue
            if c0 - s0 > GAP_IGNORE_M:
                nxt.append((s0, c0))
            if s1 - c1 > GAP_IGNORE_M:
                nxt.append((c1, s1))
        subs = nxt
    return subs


def _crossed(p: Piece, q: Piece, pieces: list[Piece]) -> bool:
    """Whether every perpendicular wall that splits the run gap between p and q runs through the run band (beyond
    both faces by its thickness): two walls on one line with walls crossing between them (real02), not a wall end
    splitting one wall's door gap (real01's bedrooms)."""
    a, b = p.b, q.a
    lo, hi = p.c - p.t / 2.0, p.c + p.t / 2.0
    cutting = []
    for w in pieces:
        if w.axis == p.axis:
            continue
        w0, w1 = w.c - w.t / 2.0, w.c + w.t / 2.0
        if w1 <= a + GAP_IGNORE_M or w0 >= b - GAP_IGNORE_M:
            continue
        if min(w.b, hi) - max(w.a, lo) >= 0.5 * p.t:
            cutting.append(w)
    return bool(cutting) and all(w.a < lo - p.t and w.b > hi + p.t for w in cutting)


def _inside_wall(g: Gap, pieces: list[Piece], run: list[Piece]) -> Optional[list[Piece]]:
    """Fix round after P6b: the pieces on the gap's axis, outside its run, whose bands cover the gap's band (within
    ``RUN_OFFSET_M``) and that together cover its whole width (within 2 x ``GAP_IGNORE_M``), or None. Such a gap
    lies in wall material (real03's shear-wall core: the 0.62 m core pieces over the gaps of the thinner runs)."""
    lo, hi = g.c - g.t / 2.0, g.c + g.t / 2.0
    own = {id(q) for q in run}
    cover = [w for w in pieces if w.axis == g.axis and id(w) not in own and w.b > g.a and w.a < g.b
             and w.c - w.t / 2.0 <= lo + RUN_OFFSET_M and w.c + w.t / 2.0 >= hi - RUN_OFFSET_M]
    total, reach = 0.0, g.a
    for s0, s1 in sorted((max(w.a, g.a), min(w.b, g.b)) for w in cover):
        if s1 > reach:
            total += s1 - max(s0, reach)
            reach = s1
    return cover if cover and total >= g.width - 2.0 * GAP_IGNORE_M else None


def _glazing(g: Gap, lo: float, hi: float) -> list:
    """Fix round after P6b: the window lines of ``g`` (``found["lines"]``) that are glass of the part of the band
    between the offsets ``lo`` < ``hi`` (absolute, across the axis): a straight piece parallel to the wall, strictly
    inside that part (>= ``BAND_SLACK_M`` / 2 from its edges), within the gap +- ``OWN_MARGIN_M`` along it and
    spanning >= ``WINDOW_COVER`` of it. A face line, an outline, an axis or a beam edge running on past the gap is
    none (real03's 'windows' between the shear walls)."""
    tol = BAND_SLACK_M / 2.0
    out = []
    for it in g.found.get("lines", []):
        pts = it.pts + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])
        for p, q in zip(pts, pts[1:]):
            if not _parallel(p, q, g.axis):
                continue
            off = g.c + g.across(((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0))
            s0, s1 = sorted((g.along(p), g.along(q)))
            if lo + tol < off < hi - tol and s0 >= g.a - OWN_MARGIN_M and s1 <= g.b + OWN_MARGIN_M \
                    and min(s1, g.b) - max(s0, g.a) >= WINDOW_COVER * g.width:
                out.append(it)
                break
    return out


def _lining(run: list[Piece], p: Piece, q: Piece, runs: list[list[Piece]], found: list[Gap]) -> Optional[dict]:
    """Fix round after P6b: the thinner wall lining the run gap between ``p`` and ``q`` (see the module docstring),
    or None: another run on the axis, >= ``LINING_THINNER_M`` thinner, inside the run's band (+- ``RUN_OFFSET_M``),
    one face flush with the run's (<= ``RUN_OFFSET_M``), whose pieces fill >= ``LINING_SHARE`` of the gap and run on
    past both its ends by > ``LINING_REACH_M`` (real02's 0.05 m piece inside a party-wall junction, exactly as long
    as the 0.40 m gap there, is no lining wall). Never when
    a part of the gap holds a door, or a window whose glass (``_glazing``) lies in the open part of the band beside
    the lining wall (a sill strip drawn on the wall layer in front of a real window), or when every part is closed.
    Returns ``{"thickness", "lining_thickness", "share", "entity", "note"}``."""
    if not found or all(g.cls == "closed" for g in found) or any(g.cls == "door" for g in found):
        return None
    t, c = _run_t(run), _run_c(run)
    lo, hi = c - t / 2.0, c + t / 2.0
    a, b = p.b, q.a
    best = None
    for other in runs:
        if other is run or other[0].axis != p.axis:
            continue
        t2, c2 = _run_t(other), _run_c(other)
        lo2, hi2 = c2 - t2 / 2.0, c2 + t2 / 2.0
        if t - t2 < LINING_THINNER_M - 1e-9 or lo2 < lo - RUN_OFFSET_M or hi2 > hi + RUN_OFFSET_M or \
                min(abs(lo2 - lo), abs(hi2 - hi)) > RUN_OFFSET_M:
            continue
        # Review of the fix round: the lining is one wall through the gap, its pieces apart by its own classified
        # gaps only (<= GAP_MAX_M: the passages it holds); a piece of the run far along the axis is not.
        for chain in _chains(other):
            share = sum(max(0.0, min(w.b, b) - max(w.a, a)) for w in chain) / (b - a)
            reach = min(a - min(w.a for w in chain), max(w.b for w in chain) - b)
            if share >= LINING_SHARE - 1e-9 and reach > LINING_REACH_M and (best is None or share > best[0]):
                best = (share, chain, lo2, hi2, t2)
    if best is None:
        return None
    share, other, lo2, hi2, t2 = best
    open_lo, open_hi = (hi2, hi) if abs(lo2 - lo) <= abs(hi2 - hi) else (lo, lo2)
    if any(g.cls == "window" and _glazing(g, open_lo, open_hi) for g in found):
        return None
    entities = list(dict.fromkeys(e for w in other if min(w.b, b) > max(w.a, a)
                                  for e in w.wall.entity.split(",") if e))
    note = (f"a {t2:.2f} m wall ({', '.join(entities[:4])}) runs along one face of this {t:.2f} m run through the "
            f"{b - a:.2f} m gap ({share:.0%} of it): the {t:.2f} m pieces are columns or shear walls on that wall, "
            f"not one wall with openings between them")
    return {"thickness": round(t, 4), "lining_thickness": round(t2, 4), "share": round(share, 3),
            "entity": ",".join(entities), "note": note}


def _chains(run: list[Piece]) -> list[list[Piece]]:
    """Fix round after P6b, review: the pieces of ``run`` in runs of their own that no gap > ``GAP_MAX_M`` splits
    (a gap that long is open: no wall across it, ``gaps_and_openings``)."""
    out: list[list[Piece]] = []
    for q in sorted(run, key=lambda w: w.a):
        if out and q.a - max(w.b for w in out[-1]) <= GAP_MAX_M:
            out[-1].append(q)
        else:
            out.append([q])
    return out


def _mark_lined(walls: list[WallItem], group: list[tuple[int, list[Piece]]], linings: list[dict], ctx: "_Ctx") -> None:
    """Fix round after P6b: the walls of ``group`` (output index, pieces), which lined gaps split apart, each get
    ``corrected_by_ai`` (reason, evidence, before: the one wall the run made before, in page metres) and the reason in
    their evidence note. A group of one segment (no lined gap) is left alone."""
    if len(group) < 2 or not linings:
        return
    pieces = [q for _, seg in group for q in seg]
    axis = pieces[0].axis
    a, b = min(q.a for q in pieces), max(q.b for q in pieces)
    c = sum(q.c * (q.b - q.a) for q in pieces) / max(sum(q.b - q.a for q in pieces), 1e-12)
    t = _weighted_median([(q.t, q.b - q.a) for q in pieces])
    s, e = ((a, c), (b, c)) if axis == "h" else ((c, a), (c, b))
    s, e = _rot(s, ctx.theta), _rot(e, ctx.theta)
    reason = (f"read as {len(group)} walls, not one {t:.2f} m wall over {b - a:.2f} m: " +
              "; ".join(dict.fromkeys(ln["note"] for ln in linings)))
    entity = ",".join(dict.fromkeys(x for ln in linings for x in ln["entity"].split(",") if x))
    for k, seg in group:
        w = walls[k]
        own = ",".join(dict.fromkeys(x for q in seg for x in q.wall.entity.split(",") if x))
        ev = ctx.evidence("vector", min(q.wall.evidence.get("confidence", 1.0) for q in seg), f"{own},{entity}")
        ev["rule"] = "lined_gap"
        ev["note"] = reason
        old = w.evidence.get("note")
        new = dataclasses.replace(w, evidence=dict(w.evidence, note=(old + "; " if old else "") + reason))
        new.corrected_by_ai = {"by": "code", "stage": "reading", "rule": "lined_gap", "reason": reason,
                               "evidence": ev, "before": {"start": [round(s[0], 4), round(s[1], 4)],
                                                          "end": [round(e[0], 4), round(e[1], 4)],
                                                          "thickness": round(t, 4)}}
        walls[k] = new


def _replace_wall(w: WallItem, **changes) -> WallItem:
    """``dataclasses.replace`` that keeps a ``corrected_by_ai`` label (fix round after P6b)."""
    new = dataclasses.replace(w, **changes)
    if getattr(w, "corrected_by_ai", None):
        new.corrected_by_ai = w.corrected_by_ai
    return new


def _corner_posts(ends: list[Piece], index: "StrokeIndex", owned: set, ctx: "_Ctx", k0: int) -> list[Piece]:
    """real10 (1 Nov 2026): the typical floor's living rooms have corner windows: the glass runs from the end of
    the side wall round the corner to the end of the front wall, and no wall piece stands at the corner, so neither
    free end hits anything and the room is open to the outside. Two free ends of walls at right angles whose centre
    lines meet at a point ``GAP_MIN_M``-``GAP_MAX_M`` beyond each end (nothing hit before it), with a window along
    each leg (``classify_gap``: its own lines, glass), get a corner post there: a square as thick as the thicker
    wall, evidence ``derived``. Returns the posts (pieces of new walls)."""
    frees = [(p, w) for p in ends for w in ("start", "end") if _is_free(p, w, ends)]
    posts: list[Piece] = []
    taken: set = set()
    for p, wp in frees:
        if p.axis != "v":
            continue
        for q, wq in frees:
            if q.axis != "h" or (id(p), wp) in taken or (id(q), wq) in taken:
                continue
            side = max(p.t, q.t)
            cx, cy = p.c, q.c
            ep = p.b if wp == "end" else p.a
            eq = q.b if wq == "end" else q.a
            dp = (cy - ep) if wp == "end" else (ep - cy)
            dq = (cx - eq) if wq == "end" else (eq - cx)
            if not (GAP_MIN_M <= dp - side / 2.0 <= GAP_MAX_M and GAP_MIN_M <= dq - side / 2.0 <= GAP_MAX_M):
                continue
            hp, hq = _cast(p, wp, ends), _cast(q, wq, ends)
            if (hp is not None and hp[2] - hp[1] < dp - side / 2.0 - 0.01) or \
                    (hq is not None and hq[2] - hq[1] < dq - side / 2.0 - 0.01):
                continue
            # The glass runs round the corner to the frame's outer corner: each leg is read up to the far side of the
            # post (its own lines end there, not at the post's near face).
            far_p = cy + side / 2.0 if wp == "end" else cy - side / 2.0
            far_q = cx + side / 2.0 if wq == "end" else cx - side / 2.0
            legs = [Gap("end", "v", p.c, p.t, min(ep, far_p), max(ep, far_p), [p]),
                    Gap("end", "h", q.c, q.t, min(eq, far_q), max(eq, far_q), [q])]
            for g in legs:
                classify_gap(g, index, owned)
            if not all(g.cls == "window" for g in legs):
                continue
            taken.update({(id(p), wp), (id(q), wq)})
            corners = [(cx - side / 2.0, cy - side / 2.0), (cx + side / 2.0, cy - side / 2.0),
                       (cx + side / 2.0, cy + side / 2.0), (cx - side / 2.0, cy + side / 2.0)]
            corners_page = [_rot(c, ctx.theta) for c in corners]
            box = ctx.box(corners_page)
            entity = f"corner:{p.wall.entity.split(',')[0]}+{q.wall.entity.split(',')[0]}"
            ev = ctx.evidence("derived", 0.7, entity, box_units=box)
            ev["note"] = (f"corner window post: the windows of the walls {p.wall.entity.split(',')[0]} and "
                          f"{q.wall.entity.split(',')[0]} meet at a corner where no wall piece is drawn "
                          f"({legs[0].width - side:.2f} m and {legs[1].width - side:.2f} m of glass)")
            wall = WallItem(start=_r(_rot((cx - side / 2.0, cy), ctx.theta)),
                            end=_r(_rot((cx + side / 2.0, cy), ctx.theta)), thickness=round(side, 4), box=box,
                            entity=entity, evidence=ev)
            posts.append(Piece(k0 + len(posts), "h", cy, side, cx - side / 2.0, cx + side / 2.0, wall))
    return posts


def _buried_end(p: Piece, which: str, pieces: list[Piece]) -> Optional[float]:
    """The far face (along ``p``'s axis) of the one perpendicular wall ``p``'s end lies in: the end is inside that wall's
    band and no wall of ``p``'s own direction touches it; else None."""
    pos = p.b if which == "end" else p.a
    face = LineString(p.end_face(which))
    touching = [q for q in pieces if q is not p and sbox(*q.rect()).distance(face) <= FREE_END_M]
    if len(touching) != 1 or touching[0].axis == p.axis:
        return None
    q = touching[0]
    lo, hi = q.c - q.t / 2.0, q.c + q.t / 2.0
    if not (lo - FREE_END_M <= pos <= hi + FREE_END_M) or \
            min(p.c + p.t / 2.0, q.b + FREE_END_M) - max(p.c - p.t / 2.0, q.a - FREE_END_M) <= 0.0:
        return None
    return hi if which == "end" else lo


def _cast_from(p: Piece, which: str, pieces: list[Piece], start: float) -> Optional[tuple[Piece, float, float]]:
    """``_cast`` from ``start`` (a perpendicular wall's far face) instead of ``p``'s end."""
    trial = dataclasses.replace(p, b=start) if which == "end" else dataclasses.replace(p, a=start)
    return _cast(trial, which, [q for q in pieces if q is not p] + [trial])


def _slant(p: Piece, q: Piece) -> float:
    """4 Nov 2026 (real17 L-1: an outer wall drawn 1.9 deg off the plan's frame is read as axis steps 3-6 cm apart; the
    WC windows in it are drawn at the wall's angle): the angle (deg, signed, in the aligned frame) of the line through
    the centres of two pieces on one axis whose lines lie more than ``RUN_OFFSET_M`` apart, when it is within
    ``AXIS_TOL_DEG`` of the axis; else 0 (one line, or two walls side by side)."""
    if p.axis != q.axis or abs(q.c - p.c) <= RUN_OFFSET_M:
        return 0.0
    along = (q.a + q.b) / 2.0 - (p.a + p.b) / 2.0
    if abs(along) <= 1e-9:
        return 0.0
    dc = q.c - p.c
    if along < 0:
        along, dc = -along, -dc
    ang = math.degrees(math.atan2(dc, along)) if p.axis == "h" else -math.degrees(math.atan2(dc, along))
    return ang if abs(ang) <= AXIS_TOL_DEG else 0.0


def _is_free(p: Piece, which: str, pieces: list[Piece]) -> bool:
    face = LineString(p.end_face(which))
    for q in pieces:
        if q is p:
            continue
        if sbox(*q.rect()).distance(face) <= FREE_END_M:
            return False
    return True


def _cast(p: Piece, which: str, pieces: list[Piece], also: list = ()) -> Optional[tuple[Piece, float, float]]:
    """First wall face hit from a free end along the axis within GAP_MAX_M: (wall, gap a, gap b). ``also``: further
    targets (the caps: frames and nubs at wall ends, 4 Nov 2026)."""
    lo, hi = p.c - p.t / 2.0, p.c + p.t / 2.0
    best = None
    spans = []
    for q in list(pieces) + [x for x in also if x not in pieces]:
        if q is p:
            continue
        r = q.rect()
        if p.axis == "h":
            spans.append((q, r[1], r[3], r[0], r[2]))
        else:
            spans.append((q, r[0], r[2], r[1], r[3]))
    for q, c0, c1, s0, s1 in spans:
        cover = min(c1, hi) - max(c0, lo)
        if 0.0 < cover < 0.5 * p.t:
            # 4 Nov 2026 (real10 L-1, user: "fix the antre and kitchen": the right kitchen's door jamb drawn as two stubs
            # side by side, 7 and 3 cm of the 16 cm wall, where its left twin's one stub covers 9 cm; the kitchen door
            # was never cast and the kitchen and the antre were one room): the stubs whose near faces stand within
            # ``CAST_STUB_M`` of this one cover the band together
            near = [(a, b) for q2, a, b, t0, t1 in spans
                    if q2 is not q and abs((t0 if which == "end" else t1) - (s0 if which == "end" else s1)) <= CAST_STUB_M]
            ivs = sorted([(max(c0, lo), min(c1, hi))] + [(max(a, lo), min(b, hi)) for a, b in near if min(b, hi) > max(a, lo)])
            total, cur = 0.0, None
            for a, b in ivs:
                if cur is None or a > cur[1]:
                    total += (cur[1] - cur[0]) if cur else 0.0
                    cur = [a, b]
                else:
                    cur[1] = max(cur[1], b)
            cover = total + ((cur[1] - cur[0]) if cur else 0.0)
        if cover < 0.5 * p.t:
            continue
        if which == "end":
            d = s0 - p.b
            if -GAP_IGNORE_M <= d <= GAP_MAX_M and (best is None or d < best[0]):
                best = (d, q, p.b, s0)
        else:
            d = p.a - s1
            if -GAP_IGNORE_M <= d <= GAP_MAX_M and (best is None or d < best[0]):
                best = (d, q, s1, p.a)
    if best is None or best[0] <= GAP_IGNORE_M:
        return None
    return best[1], best[2], best[3]


def _own(g: Gap, index: StrokeIndex, owned: set) -> None:
    """Arc, leaf, hinge pin and the strokes entirely within the gap +- 0.10 m (which include the window's own band
    lines). Band lines running past the gap (a wall face line, a bed edge 9 mm off the face) count for the
    classification but are not owned: §2.8 decides about them.

    Fix round after P6b: also a gap that lost its window for want of glass (``no_glass``), lies inside wall material
    (``inside``) or is a wall whose faces are drawn across it (``faces``): its band lines are the structure's (shear
    wall outlines, beam projections, axis pieces), owned as when the gap was read as a window, never furniture."""
    if g.cls not in ("door", "window", "empty") and not any(g.found.get(k) for k in ("no_glass", "inside", "faces")):
        return
    ids = set()
    for key in ("arcs", "leaves"):
        ids.update(it.st.id for it in g.found.get(key, []))
    # +-0.10 m along the wall, the wall band (faces +-20 mm) across it: jamb frames and window lines sit there,
    # a bed or counter standing in front of a window does not.
    zone = g.rect(grow_face=BAND_SLACK_M, grow_along=OWN_MARGIN_M)
    for it in index.query(zone, predicate="contains"):
        ids.add(it.st.id)
    g.found["owned"] = sorted(ids)
    owned.update(ids)


def _merged_wall(seg: list[Piece], ctx: _Ctx, extended: dict, joined: Optional[dict] = None) -> WallItem:
    """One WallItem for consecutive run pieces (thickness = length-weighted median); an unchanged single piece is
    returned as it was (with the note of ``joined``, if any). ``joined``: input wall index -> the note of a piece
    ``join_fused_strips`` gave the run's centre line and thickness, or of an end cap (``end_caps``)."""
    theta = ctx.theta
    joined = joined or {}
    if len(seg) == 1 and seg[0].k not in extended:
        w = seg[0].wall
        if seg[0].k not in joined:
            return w
        old = w.evidence.get("note")
        return dataclasses.replace(w, evidence=dict(w.evidence, note=(old + "; " if old else "") + joined[seg[0].k]))
    axis = seg[0].axis
    a = min(q.a for q in seg)
    b = max(q.b for q in seg)
    c = sum(q.c * (q.b - q.a) for q in seg) / max(sum(q.b - q.a for q in seg), 1e-12)
    t = _weighted_median([(q.t, q.b - q.a) for q in seg])
    if axis == "h":
        s, e = (a, c), (b, c)
        corners = [(a, c - t / 2), (b, c - t / 2), (b, c + t / 2), (a, c + t / 2)]
    else:
        s, e = (c, a), (c, b)
        corners = [(c - t / 2, a), (c + t / 2, a), (c + t / 2, b), (c - t / 2, b)]
    s, e = _rot(s, theta), _rot(e, theta)
    corners = [_rot(p, theta) for p in corners]
    entities: list[str] = []
    for q in seg:
        for part in q.wall.entity.split(","):
            if part and part not in entities:
                entities.append(part)
    entity = ",".join(entities)
    base = seg[0].wall.evidence
    methods = {q.wall.evidence.get("method") for q in seg}
    method = "raster" if methods == {"raster"} else "vector"
    confidence = min(q.wall.evidence.get("confidence", 1.0) for q in seg)
    # Walls drawn as face lines carry their layer and the layer choice: kept when every piece has the same.
    layers = {q.wall.evidence.get("layer") for q in seg}
    rules = {q.wall.evidence.get("rule") for q in seg}
    first_notes = {q.wall.evidence.get("note") for q in seg}
    notes = [first_notes.pop()] if len(first_notes) == 1 and None not in first_notes else []
    notes += [joined[q.k] for q in seg if q.k in joined]
    for q in seg:
        if q.k in extended:
            ids, reason = extended[q.k]
            method = "derived"
            entity = entity + ("," + ",".join(ids) if ids else "")
            notes.append(reason)
    if len(seg) > 1:
        notes.append(f"run of {len(seg)} pieces")
    ev = B.evidence(base.get("file", ctx.file_rel), method, round(confidence, 3), page=base.get("page", ctx.page_no),
                    entity=entity, layer=layers.pop() if len(layers) == 1 else None,
                    rule=rules.pop() if len(rules) == 1 else None)
    if notes:
        ev["note"] = "; ".join(notes)
    return WallItem(start=(round(s[0], 4), round(s[1], 4)), end=(round(e[0], 4), round(e[1], 4)),
                    thickness=round(t, 4), box=ctx.box(corners), entity=entity, evidence=ev,
                    status=seg[0].wall.status)


def _trim_into_bands(walls: list[WallItem], theta: float) -> None:
    """A wall end that pokes into a perpendicular wall's band (the run-length decomposition gave it the junction
    square) is moved back to the face it crosses first: the through-wall keeps the junction (§2.4.3)."""
    pieces, _ = pieces_of(walls, theta)
    for p in pieces:
        changed = False
        for which in ("start", "end"):
            pos = p.a if which == "start" else p.b
            for q in pieces:
                if q is p or q.axis == p.axis:
                    continue
                f0, f1 = q.c - q.t / 2.0, q.c + q.t / 2.0
                if not (f0 + 1e-6 < pos < f1 + 1e-6 or f0 - 1e-6 < pos < f1 - 1e-6):
                    continue
                # q must cover p's whole band and continue past it on both sides (a through-wall).
                if not (q.a < p.c - p.t / 2.0 - 1e-6 and q.b > p.c + p.t / 2.0 + 1e-6):
                    continue
                new = f0 if which == "end" else f1
                if which == "end" and new > p.a + 0.05:
                    p.b, changed = new, True
                elif which == "start" and new < p.b - 0.05:
                    p.a, changed = new, True
        if changed:
            w = p.wall
            if p.axis == "h":
                s, e = (p.a, p.c), (p.b, p.c)
            else:
                s, e = (p.c, p.a), (p.c, p.b)
            s, e = _rot(s, theta), _rot(e, theta)
            if math.dist(s, w.end) + math.dist(e, w.start) < math.dist(s, w.start) + math.dist(e, w.end):
                s, e = e, s
            walls[p.k] = _replace_wall(w, start=(round(s[0], 4), round(s[1], 4)), end=(round(e[0], 4), round(e[1], 4)))


def _exterior_test(walls: list[WallItem]):
    """A function telling whether a page-metre rectangle touches the outside of its wall component."""
    polys = []
    for w in walls:
        polys.append(LineString([w.start, w.end]).buffer(w.thickness / 2.0, cap_style=2, join_style=2))
    if not polys:
        return lambda rect: False
    union = unary_union(polys).buffer(0.002, join_style=2).buffer(-0.002, join_style=2)
    rings = []
    for part in getattr(union, "geoms", [union]):
        rings.append(part.exterior)
    outer = unary_union(rings)

    def touches(corners) -> bool:
        return Polygon(corners).buffer(0.003).intersects(outer)
    return touches


OUTSIDE_CLOSE_MAX_M = 3.0      # 12 Nov 2026: openings up to this wide (GAP_MAX_M) close the building's outline ...
OUTSIDE_PROBE_M = 0.30         # ... and a point this far past a wall face tells which space the face looks into
OUTSIDE_PROBE_AT = (0.25, 0.5, 0.75)   # probes along the stretch (a cross wall or a column may stand at one of them)


OUTSIDE_ENTRANCE_MIN_M = 0.60  # 12 Nov 2026 (review B2-GEN-01): a gap this wide may be a room's way in (a door's width)


def _entrance(o: OpeningItem) -> bool:
    """A door, or a gap at least ``OUTSIDE_ENTRANCE_MIN_M`` wide that is no window (12 Nov 2026, review B2-GEN-01: a
    room's entrance read as 'unclassified gap content' is still its way in; a gap holding a window's frame lines,
    ``no_glass``, is not)."""
    if o.virtual:
        return False
    if o.kind == "door":
        return True
    ev = o.evidence if isinstance(o.evidence, dict) else {}
    return o.kind == "opening" and float(o.width) >= OUTSIDE_ENTRANCE_MIN_M and ev.get("rule") != "no_glass"


def _outside_test(walls: list[WallItem], openings: list[OpeningItem], outdoor=(), rooms=()):
    """12 Nov 2026 (review B-OPN-03, L2, L5): a function telling whether page-metre probe points past a wall's faces
    look outside. The building's outline is closed at its doors and windows (openings up to ``OUTSIDE_CLOSE_MAX_M``:
    an open door gap no longer lets the outside into the rooms behind it, real06's pier between two doors). Outside is
    what lies past that outline, and every face it encloses that is open to the sky: a closed face no door or gap of a
    door's width enters (a light well, a shaft) or one holding an outdoor-space label (``outdoor``: balcony, terrace,
    courtyard ... points, ``levels.outdoor.space_kind``), never one holding the label of a room one lives in (``rooms``,
    review B2-GEN-01). Faces, not holes (review B2 FC-02, real15: the sheet frame read as walls round the building,
    its 1256 m2 hole holding the balconies' labels): a hole's face is the hole less the filled outlines of the wall
    parts inside it, and a hole holding a closed building (a part with faces of its own: a frame, a plot wall, a
    parapet round it) is outside."""
    from wenart.ingest.generic import topology as TP

    closing = [o for o in openings if not o.virtual and float(o.width) <= OUTSIDE_CLOSE_MAX_M]
    parts = TP._parts(TP.bridged_union(walls, closing)) if walls else []
    if not parts:
        return lambda points: False
    outlines = [Polygon(q.exterior) for q in parts]
    reps = [q.representative_point() for q in parts]
    doors = [d.buffer(0.01) for d in (TP.opening_polygon(o, walls) for o in closing if _entrance(o)) if d is not None]
    sky, pieces = [], []
    for i, part in enumerate(parts):
        mine = outlines[i]
        for ring in part.interiors:
            h = Polygon(ring)
            nested = [j for j in range(len(parts)) if j != i and h.contains(reps[j])]
            face = h.difference(unary_union([outlines[j] for j in nested])) if nested else h
            if face.is_empty:
                continue
            # 13 Nov 2026 (review B3C-01 / B3-FC02-CORE: a free-standing core, shaft or column ring inside a room made
            # the room sky): the ground round a building inside a loop is entered by none of the loop's own doors; a
            # hall round a core is entered through its part's own doors
            inner = part.buffer(-0.02)
            if any(parts[j].interiors for j in nested) \
                    and not any(d.intersects(face) and d.intersects(inner) for d in doors):
                sky.append(face)                 # the ground between a loop and the building inside it
                mine = mine.difference(face)
                continue
            if any(face.contains(Point(q)) for q in rooms):
                continue                         # a room one lives in, whatever the reading made of its door
            if any(face.contains(Point(q)) for q in outdoor) or not any(d.intersects(face) for d in doors):
                sky.append(face)
        pieces.append(mine)
    filled = unary_union(pieces)

    def outside(points) -> bool:
        for q in points:
            pt = Point(q)
            if not filled.contains(pt) or any(h.contains(pt) for h in sky):
                return True
        return False
    return outside


def _opening(g: Gap, ctx: _Ctx, exterior) -> OpeningItem:
    theta = ctx.theta
    mid = (g.a + g.b) / 2.0
    center = _rot(g.point(mid), theta)
    axis_deg = (0.0 if g.axis == "h" else 90.0) + theta
    corners = [_rot(p, theta) for p in (g.point(g.a, -g.t / 2), g.point(g.b, -g.t / 2), g.point(g.b, g.t / 2),
                                         g.point(g.a, g.t / 2))]
    box = ctx.box(corners)
    width = round(g.width, 4)
    names = ",".join(dict.fromkeys(e for p in g.pieces for e in p.wall.entity.split(",") if e))
    if g.cls == "door" and g.found.get("sliding"):
        ids = [it.st.id for it in g.found["leaves"]]
        ev = ctx.evidence("vector", CONF_DOOR, ",".join(ids), box_units=box)
        if g.found.get("by_name"):
            chain = g.found["leaves"][0].st.block
            ev["note"] = f"door by its block name '{chain}' ({g.found['by_name']}, no swing arc)"
        else:
            ev["note"] = f"{len(ids)} leaf/leaves drawn parallel to the wall without a swing arc: a sliding door"
        item = OpeningItem(kind="door", width=width, center=_r(center), rotation_deg=round(axis_deg % 360.0, 3),
                           box=box, entity=ids[0], evidence=ev, height=DOOR_HEIGHT_M, assumed=["height"])
        _door_operation(item, [it.st for it in g.found["leaves"]], False, sliding=True)
        return item
    if g.cls == "door":
        side = _rot(_swing_side(g), theta)
        probe = (center[0] + side[0] * DOOR_SWING_PROBE, center[1] + side[1] * DOOR_SWING_PROBE)
        rotation = _door_rotation(axis_deg, side)
        ids = [it.st.id for it in g.found["arcs"] + g.found["leaves"]]
        conf = CONF_DOOR_LEAF if g.found["leaf"] else CONF_DOOR
        ev = ctx.evidence("vector", conf, ",".join(ids), box_units=box)
        if not g.found["leaf"]:
            ev["note"] = "swing arc without a drawn leaf"
        item = OpeningItem(kind="door", width=width, center=_r(center), rotation_deg=round(rotation % 360.0, 3),
                           box=box, entity=ids[0], evidence=ev, swing_point=_r(probe), height=DOOR_HEIGHT_M,
                           assumed=["height"])
        _door_operation(item, [it.st for it in g.found["arcs"] + g.found["leaves"]], bool(g.found.get("double")))
        return item
    if g.cls == "window":
        ids = [it.st.id for it in g.found["lines"]]
        ev = ctx.evidence("vector", CONF_WINDOW, ",".join(ids), box_units=box)
        item = OpeningItem(kind="window", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                           box=box, entity=ids[0], evidence=ev, height=WINDOW_HEIGHT_M, sill=WINDOW_SILL_M,
                           assumed=["height", "sill_height"])
        named = operation_word([n for it in g.found["lines"] if it.st.block for n in it.st.block.split("/")])
        if named is not None:
            set_operation(item, named, "block_name")
        return item
    if g.cls == "empty":
        ev = ctx.evidence("derived", CONF_DOORLESS, f"gap:{names}", box_units=box)
        item = OpeningItem(kind="opening", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                           box=box, entity=f"gap:{names}", evidence=ev, height=DOOR_HEIGHT_M, assumed=["height"])
        if exterior(corners):
            item.status = "unverified"
            item.evidence["note"] = "possible undrawn door or window (empty gap in an exterior wall)"
        return item
    ids = [it.st.id for it in g.found.get("content", [])]
    ev = ctx.evidence("derived", 0.5, f"gap:{names}", box_units=box)
    ev["note"] = "unclassified gap content: " + ",".join(ids[:20]) + (" ..." if len(ids) > 20 else "")
    if g.found.get("no_glass"):
        ev["note"] += f" ({g.found['no_glass']})"
        # Fix round after P6b (23 Oct 2026), review: marked, so the face typing counts it as the window it was read as
        # before, not as a door (``topology.unlabelled_face_type``; real03's lift shaft behind its two lift doors).
        ev["rule"] = "no_glass"
    return OpeningItem(kind="opening", width=width, center=_r(center), rotation_deg=round(axis_deg % 180.0, 3),
                       box=box, entity=f"gap:{names}", evidence=ev, status="unverified", height=DOOR_HEIGHT_M,
                       assumed=["height"], type_raw="unclassified gap content")


def _r(p) -> tuple[float, float]:
    return (round(p[0], 4), round(p[1], 4))


def _swing_side(g: Gap) -> tuple[float, float]:
    """Unit vector (aligned frame) from the wall towards the side the door opens into."""
    sgn = g.found["swing"]
    return (0.0, sgn) if g.axis == "h" else (sgn, 0.0)


def _door_rotation(axis_deg: float, side) -> float:
    """Wall direction whose left normal points to the swing side ``side`` (page frame): the synthetic door
    convention, where a door block opens towards its local +Y with rotation = wall angle."""
    t = math.radians(axis_deg)
    left = (-math.sin(t), math.cos(t))
    return axis_deg if left[0] * side[0] + left[1] * side[1] > 0 else axis_deg + 180.0


def _log_entry(g: Gap, theta: float, piece_out: dict) -> dict:
    entry = {"kind": g.kind, "class": g.cls, "width": round(g.width, 4),
             "p0": _out(g.point(g.a), theta), "p1": _out(g.point(g.b), theta), "thickness": round(g.t, 4),
             "walls": sorted({piece_out.get(p.k) for p in g.pieces if piece_out.get(p.k) is not None})}
    if g.found.get("owned"):
        entry["owned"] = g.found["owned"]
    if g.cls == "door":
        entry["hinges"] = [_out(h, theta) for h in g.found["hinges"]]
        entry["radius"] = round(g.found["radius"], 4) if g.found.get("radius") is not None else None
        if g.found.get("sliding"):
            entry["operation"] = g.found.get("by_name") or "sliding"
        entry["leaf"] = g.found["leaf"]
    if g.cls == "unclassified":
        entry["strokes"] = [it.st.id for it in g.found.get("content", [])]
    if g.found.get("split_reason"):
        entry["note"] = g.found["split_reason"]
    if g.found.get("lining"):
        entry["lining"] = {k: v for k, v in g.found["lining"].items() if k != "note"}
    # Fix round after P6b: the rule that decided a gap the old reading took for a window or an opening (the core lists
    # them in the page notes, ``core.gap_rule_notes``).
    rule = next((r for key, r in GAP_RULES if g.found.get(key)), None)
    if rule is not None:
        entry["rule"] = rule
        if rule == "no_glass" and "note" not in entry:
            entry["note"] = g.found["no_glass"]
    if g.kind == "end":
        p, which = g.free
        entry["free_wall"] = piece_out.get(p.k)
        entry["free_end"] = which
        entry["hit_wall"] = piece_out.get(g.hit.k) if g.hit else None
        entry["line"] = [_out(g.point(g.a), theta), _out(g.point(g.b), theta)]
    return entry


# --------------------------------------------------------------------------
# Continuous-wall symbols
# --------------------------------------------------------------------------

COPY_TOL_M = 0.01               # 12 Nov 2026: a stroke this close (its end points) on the same layer is a copy


def _copy_key(st: Stroke) -> tuple:
    """The layer and the end points (in either order, to ``COPY_TOL_M``) of a stroke: copies share it."""
    a, b = st.pts[0], st.pts[-1]
    q = lambda p: (round(p[0] / COPY_TOL_M), round(p[1] / COPY_TOL_M))
    return (str(st.layer), tuple(sorted((q(a), q(b)))), len(st.pts) > 2)


REST_WALL_FACES = 2             # 12 Nov 2026: wall-layer lines at this many offsets along a stretch close it (two faces)


def _rest_parts(index: StrokeIndex, host, lo: float, hi: float, owned=frozenset()) -> list[tuple[float, float, str]]:
    """12 Nov 2026 (review B2 FC-01 / REG-1 / REG-4 / FC-06): what the drawing says over ``lo``-``hi`` along ``host``
    (frame coordinates), from the lines running along its band: 'wall' where lines of wall-drawing layers (wall,
    plaster, structure: a pier's faces, a column) run at ``REST_WALL_FACES`` offsets or more; 'window' where a window,
    glass or sill line or a window block's line runs; else 'open'. Consecutive parts of one kind are merged (pure)."""
    from wenart.ingest.generic import layer_names as LN

    if hi - lo <= 1e-6:
        return []
    across = host.t / 2.0 + BAND_SLACK_M
    rect = (lo, host.c - across, hi, host.c + across) if host.axis == "h" else (host.c - across, lo, host.c + across, hi)
    segs = []
    for it in index.query(rect, predicate="intersects"):
        if it.st.id in owned:
            continue
        roles = LN.layer_roles(it.st.layer)
        glazing = bool(roles & WINDOW_SYMBOL_ROLES) or _window_block(it.st)
        walling = not glazing and LN.draws_walls(it.st.layer)
        if not (glazing or walling):
            continue
        pts = it.pts + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])
        for a, b in zip(pts, pts[1:]):
            if not _parallel(a, b, host.axis):
                continue
            off = (a[1] + b[1]) / 2 - host.c if host.axis == "h" else (a[0] + b[0]) / 2 - host.c
            if abs(off) > across:
                continue
            raw = sorted((a[0], b[0])) if host.axis == "h" else sorted((a[1], b[1]))
            u, v = max(raw[0], lo), min(raw[1], hi)
            if v - u > 0.01:
                segs.append((u, v, round(off, 3), "window" if glazing else "wall"))
    cuts = sorted({lo, hi} | {x for sg in segs for x in sg[:2]})
    out: list = []
    for u, v in zip(cuts, cuts[1:]):
        m = (u + v) / 2.0
        here = [sg for sg in segs if sg[0] <= m <= sg[1]]
        if len({sg[2] for sg in here if sg[3] == "wall"}) >= REST_WALL_FACES:
            kind = "wall"
        elif any(sg[3] == "window" for sg in here):
            kind = "window"
        else:
            kind = "open"
        if out and out[-1][2] == kind:
            out[-1] = (out[-1][0], v, kind)
        else:
            out.append((u, v, kind))
    return out


def _covered(existing: list, k: int, host, lo: float, hi: float, theta: float) -> bool:
    """Another opening of ``host``'s line than ``existing[k]`` holds half of ``lo``-``hi`` or more (a gap read twice on
    two runs: its rest is read already)."""
    for j, o in enumerate(existing):
        if j == k or o.virtual:
            continue
        oc = _rot(o.center, -theta)
        if abs((oc[1] if host.axis == "h" else oc[0]) - host.c) > host.t / 2.0 + BAND_SLACK_M:
            continue
        a_deg = (0.0 if host.axis == "h" else 90.0) + theta
        if abs((float(o.rotation_deg) - a_deg + 90.0) % 180.0 - 90.0) > 10.0:
            continue
        oa = oc[0] if host.axis == "h" else oc[1]
        cover = min(hi, oa + float(o.width) / 2.0) - max(lo, oa - float(o.width) / 2.0)
        if o.kind in ("window", "door") and cover >= 0.5 * (hi - lo):
            return True
    return False


def _door_in_gap(existing: list, host, m_along: float, w: float, theta: float, ctx, ev: dict,
                 index: Optional[StrokeIndex] = None, owned=frozenset(), door_name: str = "") -> Optional[int]:
    """A gap opening of ``host`` (an unclassified or empty gap, along its line) that holds the door's span
    (``m_along`` +- ``w``/2, the frame) keeps the part beside the door that the drawing leaves open, in place in
    ``existing`` (12 Nov 2026, review B-dup). Review B2 (FC-01, REG-1, REG-4, FC-06): the rest is read again from the
    lines over it (``_rest_parts``): a pier's or a column's faces are wall, a window's glass or sill lines make it a
    window, and only an open part of ``GAP_MIN_M`` stays a gap, marked the door's leftover (evidence ``rest_of``: the
    facade-gap and unsure-passage rules leave it alone). With no part left the gap is the door's: its index is
    returned, the door takes its place in ``existing``. Noted in both evidences."""
    lo, hi = m_along - w / 2.0, m_along + w / 2.0
    for k, o in enumerate(existing):
        if o.virtual or o.kind != "opening":
            continue
        oc = _rot(o.center, -theta)
        across = (oc[1] if host.axis == "h" else oc[0]) - host.c
        if abs(across) > host.t / 2.0 + BAND_SLACK_M:
            continue
        a_deg = (0.0 if host.axis == "h" else 90.0) + theta
        if abs((float(o.rotation_deg) - a_deg + 90.0) % 180.0 - 90.0) > 10.0:
            continue
        oa = oc[0] if host.axis == "h" else oc[1]
        g0, g1 = oa - float(o.width) / 2.0, oa + float(o.width) / 2.0
        if not (g0 <= lo + 0.05 and hi - 0.05 <= g1):
            continue
        note = f"a door ({w:.2f} m) drawn in the {float(o.width):.2f} m gap of its wall"
        ev["note"] = (str(ev.get("note") or "") + f"; {note}: it takes its part of the gap").lstrip("; ")
        parts = []
        for a, b in ((g0, lo), (hi, g1)):
            if index is None:
                parts.append((a, b, "open"))
            else:
                parts += _rest_parts(index, host, a, b, owned)
        keep = [q for q in parts if q[2] != "wall" and q[1] - q[0] >= GAP_MIN_M
                and not _covered(existing, k, host, q[0], q[1], theta)]
        if not keep:
            return k                         # the gap is the door's (its rest wall, or read already)
        p0, p1, kind = max(keep, key=lambda q: (q[2] == "window", q[1] - q[0]))
        c = ((p0 + p1) / 2.0, host.c) if host.axis == "h" else (host.c, (p0 + p1) / 2.0)
        corners = [(p0, host.c - host.t / 2), (p1, host.c + host.t / 2)] if host.axis == "h" else \
            [(host.c - host.t / 2, p0), (host.c + host.t / 2, p1)]
        bx = ctx.box([_rot(q, theta) for q in corners])
        walled = sum(q[1] - q[0] for q in parts if q[2] == "wall")
        told = (f"{note}: the rest of the gap, {p1 - p0:.2f} m"
                + (f" ({walled:.2f} m of it drawn as wall faces: wall)" if walled > 0.01 else ""))
        if kind == "window":
            wev = ctx.evidence("vector", CONF_WINDOW, o.entity, box_units=bx)
            wev.update(note=f"{told}: window, its glass or sill lines drawn", rule="gap_rest_window")
            existing[k] = OpeningItem(kind="window", width=round(p1 - p0, 4), center=_r(_rot(c, theta)),
                                      rotation_deg=round(float(o.rotation_deg) % 180.0, 3), box=bx, entity=o.entity,
                                      evidence=wev, height=WINDOW_HEIGHT_M, sill=WINDOW_SILL_M,
                                      assumed=["height", "sill_height"])
            return None
        oev = dict(o.evidence) if isinstance(o.evidence, dict) else {}
        oev["note"] = (str(oev.get("note") or "") + f"; {told}").lstrip("; ")
        oev["rest_of"] = door_name or f"the door at {m_along:.2f} along its wall"
        existing[k] = dataclasses.replace(o, width=round(p1 - p0, 4), center=_r(_rot(c, theta)), box=bx, evidence=oev)
        return None
    return None


SIDELIGHT_MIN_M = 0.30          # 13 Nov 2026: a window's part beside a door this wide stays a side light
DOOR_OVER_WINDOW_M = 0.05       # ... a door overlapping a window on its wall line by more than this keeps its stretch
SAME_LINE_M = 0.20              # ... both on one wall line: their centre lines this close


def windows_off_doors(openings: list) -> tuple[list, list[str]]:
    """13 Nov 2026 (review S1-03c: real03's 2.90 m entrance screen read as one window over its two 0.90 m doors): a
    window and a door on one wall line (parallel, centre lines within ``SAME_LINE_M``) whose spans overlap by more than
    ``DOOR_OVER_WINDOW_M``: the door keeps its stretch, the window is cut back to its parts beside the doors, each at
    least ``SIDELIGHT_MIN_M`` wide kept as a side light, none left: the window goes. ``(openings, notes)``; the cut
    windows keep their drawn span in their evidence (pure)."""
    doors = [o for o in openings if o.kind == "door" and not getattr(o, "virtual", False)]
    out, notes = [], []
    for w in openings:
        if w.kind != "window" or getattr(w, "virtual", False) or not doors:
            out.append(w)
            continue
        a = math.radians(float(w.rotation_deg))
        ax = (math.cos(a), math.sin(a))
        half = float(w.width) / 2.0
        cuts = []
        for d in doors:
            if abs((float(d.rotation_deg) - float(w.rotation_deg) + 90.0) % 180.0 - 90.0) > 10.0:
                continue
            dv = (d.center[0] - w.center[0], d.center[1] - w.center[1])
            if abs(dv[0] * ax[1] - dv[1] * ax[0]) > SAME_LINE_M:
                continue
            t = dv[0] * ax[0] + dv[1] * ax[1]
            lo, hi = t - float(d.width) / 2.0, t + float(d.width) / 2.0
            if min(hi, half) - max(lo, -half) > DOOR_OVER_WINDOW_M:
                cuts.append((lo, hi))
        if not cuts:
            out.append(w)
            continue
        parts, cur = [], -half
        for lo, hi in sorted(cuts):
            if lo > cur:
                parts.append((cur, min(lo, half)))
            cur = max(cur, hi)
        if cur < half:
            parts.append((cur, half))
        keep = [(lo, hi) for lo, hi in parts if hi - lo >= SIDELIGHT_MIN_M]
        drawn = f"{float(w.width):.2f} m at ({w.center[0]:.2f}, {w.center[1]:.2f})"
        for lo, hi in keep:
            mid = (lo + hi) / 2.0
            ev = dict(w.evidence or {})
            ev.update(rule="door_over_window", drawn_width=round(float(w.width), 3),
                      drawn_center=[round(c, 4) for c in w.center],
                      note=(str(ev.get("note") or "") + f"; the side light of the window {drawn} beside the door(s) "
                            f"read over it (adjusted by code: the doors keep their stretch)").lstrip("; "))
            out.append(dataclasses.replace(w, width=round(hi - lo, 3), evidence=ev,
                                           center=(round(w.center[0] + ax[0] * mid, 4),
                                                   round(w.center[1] + ax[1] * mid, 4))))
        notes.append(f"the window {drawn} over {len(cuts)} door(s) on its wall line: "
                     + (f"{len(keep)} side light(s) kept" if keep else "dropped, the doors keep the stretch"))
    return out, notes


def doors_in_gaps(walls: list[WallItem], openings: list[OpeningItem], strokes_m: list[Stroke], file_rel: str,
                  page_no: int, units_to_m: Optional[float] = None) -> Optional[list[OpeningItem]]:
    """12 Nov 2026 (review B2 FC-06 / REG-3, real07 L1: a 1.72 m gap read over the 0.90 m door the gap classifier and
    the size tag made): every drawn door, whatever reader made it, lying in a gap of its own wall takes its part of the
    gap (``_door_in_gap``, the rest read from the drawing). Returns the new openings, or None when nothing changed."""
    gaps = [o for o in openings if not o.virtual and o.kind == "opening"]
    # (a door read from its swing or set by its size tag; never one read from parallel leaf lines alone: real06's
    # kitchen gap, user 29 Oct 2026: "is there a door behind it?")
    doors = [o for o in openings if not o.virtual and o.kind == "door"
             and (o.operation in ("swing", "double") or str(o.type_raw or "").startswith("door size tag"))]
    if not gaps or not doors or not walls:
        return None
    theta = dominant_angle(walls)
    pieces, _ = pieces_of(walls, theta)
    index = StrokeIndex(strokes_m, theta)
    raster = bool(strokes_m) and all(st.source == "raster" for st in strokes_m)
    ctx = _Ctx(file_rel, page_no, units_to_m, theta, raster)
    out = list(openings)
    changed = False
    for d in doors:
        if d not in out:
            continue
        c = _rot(d.center, -theta)
        hosts = [p for p in pieces if abs(((float(d.rotation_deg) - ((0.0 if p.axis == "h" else 90.0) + theta))
                                            + 90.0) % 180.0 - 90.0) <= 10.0
                 and abs((c[1] if p.axis == "h" else c[0]) - p.c) <= p.t / 2.0 + BAND_SLACK_M]
        if not hosts:
            continue
        host = min(hosts, key=lambda p: abs((c[1] if p.axis == "h" else c[0]) - p.c))
        along = c[0] if host.axis == "h" else c[1]
        # 13 Nov 2026 (review B3C-07: the door's evidence was written in place, and kept its note when core threw the
        # result away): the note travels on a copy, with the door, in the result only
        ev = dict(d.evidence) if isinstance(d.evidence, dict) else {}
        before = list(out)
        k = _door_in_gap(out, host, along, float(d.width), theta, ctx, ev, index=index,
                         door_name=f"the {float(d.width):.2f} m door at ({d.center[0]:.2f}, {d.center[1]:.2f})")
        if k is not None:
            out.pop(k)                       # the gap was the door's: merged into it (noted in the door's evidence)
            changed = True
        elif out != before:
            changed = True
        else:
            continue
        i = next((n for n, x in enumerate(out) if x is d), None)
        if i is not None:
            out[i] = dataclasses.replace(d, evidence=ev)
    return out if changed else None


def _double_doors(doors: list, leaves: list, theta: float, ctx) -> list:
    """12 Nov 2026 (review B-OPN-07 / B-r16-double: real16's '170/210' entrance, two leaves hinged at the jambs meeting
    in the middle, read as two doors, one then widened by the tag past the wall's end): two continuous-wall doors on
    one wall whose leaves close onto one point (their arcs' closed ends within ``END_POINT_TOL_M``) are one double door
    from hinge to hinge, opening to the side of the first."""
    out, used = [], set()
    for i in range(len(doors)):
        if i in used:
            continue
        hi, ci, host_i, side_i, sts_i = leaves[i]
        pair = None
        for j in range(i + 1, len(doors)):
            hj, cj, host_j, _sj, sts_j = leaves[j]
            if j in used or host_j is not host_i or math.dist(ci, cj) > END_POINT_TOL_M:
                continue
            pair = j
            break
        if pair is None:
            out.append(doors[i])
            continue
        used.add(pair)
        hj, cj, _h, _s, sts_j = leaves[pair]
        a, b = doors[i], doors[pair]
        w = math.dist(hi, hj)
        mid = ((hi[0] + hj[0]) / 2.0, (hi[1] + hj[1]) / 2.0)
        mid = (mid[0], host_i.c) if host_i.axis == "h" else (host_i.c, mid[1])
        center = _rot(mid, theta)
        ids = [e for o in (a, b) for e in str(o.evidence.get("entity") or o.entity).split(",") if e]
        ev = ctx.evidence("vector", CONF_DOOR_LEAF, ",".join(ids), box_units=None)
        ev["note"] = (f"a double door: two leaves of {a.width:.2f} and {b.width:.2f} m hinged {w:.2f} m apart, closing "
                      f"onto one point")
        side_page = _rot(side_i, theta)
        probe = (center[0] + side_page[0] * DOOR_SWING_PROBE, center[1] + side_page[1] * DOOR_SWING_PROBE)
        axis_deg = (0.0 if host_i.axis == "h" else 90.0) + theta
        box = [min(a.box[0], b.box[0]), min(a.box[1], b.box[1]), max(a.box[2], b.box[2]), max(a.box[3], b.box[3])]
        item = OpeningItem(kind="door", width=round(w, 4), center=_r(center),
                           rotation_deg=round(_door_rotation(axis_deg, side_page) % 360, 3), box=box, entity=ids[0],
                           evidence=ev, swing_point=_r(probe), height=DOOR_HEIGHT_M, assumed=["height"])
        _door_operation(item, sts_i + sts_j, True)
        out.append(item)
    return out


def _continuous_symbols(walls: list[WallItem], index: StrokeIndex, owned: set, theta: float, ctx: _Ctx,
                        existing: list[OpeningItem], inner_check: bool = False, outdoor=(), rooms=()
                        ) -> tuple[list[OpeningItem], list[OpeningItem]]:
    pieces, _ = pieces_of(walls, theta)
    doors: list[OpeningItem] = []
    # Doors: arc + leaf with the end-point rule, hinged in a wall band.
    arcs = [(it, arc) for it, arc in _arcs_in(index.items) if it.st.id not in owned
            and (CONTINUOUS_RADIUS_M[0] if _on_door_layer(it.st) else CONTINUOUS_RADIUS_ANY_M) <= arc["radius"]
            <= CONTINUOUS_RADIUS_M[1] and SWEEP_DEG[0] <= arc["sweep"] <= SWEEP_DEG[1]]
    # 12 Nov 2026 (review B-r10-dups: real10 L-1 draws two doors twice, identical arcs on one layer; the gap took one
    # copy, the other became a second door on the same gap): an exact copy of a swing already used is no door
    leaves: list = []                                    # per door of ``doors``: hinge, closed end, host, strokes
    copies = {}
    for it2, _a in _arcs_in(index.items):
        copies.setdefault(_copy_key(it2.st), []).append(it2.st.id)
    for it, arc in arcs:
        twins = [i for i in copies.get(_copy_key(it.st), []) if i != it.st.id and i in owned]
        if twins:
            owned.add(it.st.id)
            ctx.dropped.append({"kind": "continuous", "class": "none", "rule": "duplicate_symbol",
                                "center": list(_out(arc["center"], theta)), "width": round(arc["radius"], 4),
                                "strokes": [it.st.id],
                                "note": f"an exact copy of the door swing {twins[0]} (layer {it.st.layer}, the same end "
                                        f"points within {COPY_TOL_M * 100:.0f} cm) drawn twice: one door"})
            continue
        hinge = arc["center"]
        hosts = []
        for p in pieces:
            x0, y0, x1, y1 = p.rect()
            if x0 - HINGE_M <= hinge[0] <= x1 + HINGE_M and y0 - HINGE_M <= hinge[1] <= y1 + HINGE_M:
                hosts.append(p)
        if not hosts:
            continue
        host = hosts[0]
        found = None
        # 6 Nov 2026 (real21: a door block's closed leaf, a line in the wall 2 cm short of the arc's end, was taken for
        # the open leaf drawn from the hinge to the arc's other end, so the door turned onto the perpendicular wall):
        # of the lines that pass the end-point rule, the one that fits it best (its hinge end nearest the arc's centre,
        # its far end nearest the arc's end, its length nearest the radius) is the open leaf
        best_err = None
        for tip, other in ((arc["end"], arc["start"]), (arc["start"], arc["end"])):
            near = index.query((tip[0] - END_POINT_TOL_M, tip[1] - END_POINT_TOL_M, tip[0] + END_POINT_TOL_M,
                                tip[1] + END_POINT_TOL_M))
            for leaf in near:
                if leaf is it or leaf.st.id in owned or len(leaf.pts) < 2:
                    continue
                for a, b in ((leaf.pts[0], leaf.pts[-1]), (leaf.pts[-1], leaf.pts[0])):
                    if math.dist(a, tip) > END_POINT_TOL_M:
                        continue
                    w = math.dist(b, a)
                    if w <= 0 or abs(math.dist(b, other) - w) > 2 * END_POINT_TOL_M:
                        continue
                    err = math.dist(b, hinge) + math.dist(a, tip) + abs(math.dist(b, other) - w)
                    if best_err is None or err < best_err - 1e-9:
                        best_err, found = err, (leaf, b, a, other)
        leaf_ids = None
        if not found:
            found, leaf_ids = _shape_leaf(it, arc, index, owned)
        if not found:
            continue
        leaf, hinge_pt, tip, closed_end = found
        # 6 Nov 2026 (real21: six bedroom doors hinged at a wall corner were put on the perpendicular wall, their swing
        # read as that wall's door, the door's own wall kept whole and its closed leaf read as a window): the door lies
        # along its wall, so the host is the wall the closed leaf runs along (hinge to the arc's other end), the first
        # such wall holding the hinge; the first wall holding it when none runs that way
        along = [p for p in hosts if _parallel(hinge_pt, closed_end, p.axis, 0.0)
                 or _leaf_along(hinge_pt, closed_end, p.axis)]
        if along:
            host = along[0]
        w = math.dist(hinge_pt, closed_end)
        mid = ((hinge_pt[0] + closed_end[0]) / 2.0, (hinge_pt[1] + closed_end[1]) / 2.0)
        # Onto the host's centre line.
        mid = (mid[0], host.c) if host.axis == "h" else (host.c, mid[1])
        side = (tip[0] - hinge_pt[0], tip[1] - hinge_pt[1])
        n = math.hypot(*side) or 1.0
        side = (side[0] / n, side[1] / n)
        axis_deg = (0.0 if host.axis == "h" else 90.0) + theta
        center = _rot(mid, theta)
        side_page = _rot(side, theta)
        probe = (center[0] + side_page[0] * DOOR_SWING_PROBE, center[1] + side_page[1] * DOOR_SWING_PROBE)
        rotation = _door_rotation(axis_deg, side_page)
        corners = [_rot(p, theta) for p in (hinge_pt, closed_end,
                                            (closed_end[0] + side[0] * w, closed_end[1] + side[1] * w), tip)]
        bx = ctx.box(corners)
        ids = [it.st.id] + (leaf_ids or [leaf.st.id])
        owned.update(ids)
        ev = ctx.evidence("vector", CONF_DOOR_LEAF, ",".join(ids), box_units=bx)
        # 12 Nov 2026 (review B-dup / B-R2: real09's door inside the 1.73 m gap opening of its wall, real10 L-1's in the
        # 1.57 m one): a door drawn in a gap opening of its own wall takes its part of the gap
        m_along = mid[0] if host.axis == "h" else mid[1]
        in_gap = _door_in_gap(existing, host, m_along, w, theta, ctx, ev, index=ctx.rest_index or index)
        doors.append(OpeningItem(kind="door", width=round(w, 4), center=_r(center),
                                 rotation_deg=round(rotation % 360, 3), box=bx, entity=ids[0], evidence=ev,
                                 swing_point=_r(probe), height=DOOR_HEIGHT_M, assumed=["height"]))
        _door_operation(doors[-1], [it.st, leaf.st], False)
        if in_gap is not None:
            existing[in_gap] = doors.pop()               # the gap's place in the openings: the door
        else:
            leaves.append((hinge_pt, closed_end, host, side, [it.st, leaf.st]))
    doors = _double_doors(doors, leaves, theta, ctx)
    outside = _outside_test(walls, existing + doors, outdoor, rooms) if inner_check and not ctx.raster else None
    windows = _continuous_windows(pieces, index, owned, theta, ctx, existing + doors, outside)
    return doors, windows


GLAZING_ROLES = frozenset({"window", "glass"})
WINDOW_SYMBOL_ROLES = GLAZING_ROLES | {"sill"}


def window_symbols(strokes) -> bool:
    """12 Nov 2026 (review B2 FC-04): the page draws its windows with symbols of their own: a line on a window, glass
    or sill layer, or one inside a block named for a window (``layer_names.layer_roles``)."""
    from wenart.ingest.generic import layer_names as LN

    seen: dict = {}
    for st in strokes or ():
        key = (st.layer, st.block)
        if key not in seen:
            seen[key] = bool(LN.layer_roles(st.layer) & WINDOW_SYMBOL_ROLES) or _window_block(st)
        if seen[key]:
            return True
    return False


def wall_face_layer(layer: Optional[str]) -> bool:
    """6 Nov 2026: a layer that draws walls (``dxf_generic.is_wall_hint_layer``: DUVAR, WALL, plaster, concrete) and
    names no window or glass (12 Nov 2026, review B-OPN-09: any word of the shared layer table's window and glass roles,
    ``layer_names.layer_roles``, word by word: 'DUVAR-PENC', 'MUR-VERRE' or 'A-WALL-GLAZ' draw windows): its lines are
    a wall's faces."""
    from wenart.ingest.dxf_generic import is_wall_hint_layer
    from wenart.ingest.generic import layer_names as LN

    if not layer or not is_wall_hint_layer(layer):
        return False
    return not (LN.layer_roles(layer) & GLAZING_ROLES)


def _window_block(st: Stroke) -> bool:
    """12 Nov 2026 (review L5): a stroke inside a block named for a window or glass (its layer may be the wall layer
    it was inserted on: block entities on layer 0 take the INSERT's layer)."""
    from wenart.ingest.generic import layer_names as LN

    return any(LN.layer_roles(n) & GLAZING_ROLES for n in (st.block or "").split("/") if n)


def _on_door_layer(st: Stroke) -> bool:
    """A stroke drawn on a door layer (``layer_names.layer_role`` "door") or inside a block named for a door."""
    from wenart.ingest.generic import layer_names as LN

    if LN.layer_role(st.layer) == "door":
        return True
    return any(any(w in n.translate(_FOLD).upper() for w in DOOR_WORDS) for n in (st.block or "").split("/") if n)


def _leaf_along(p, q, axis: str) -> bool:
    """The closed position of a door leaf (hinge ``p`` to the arc's other end ``q``) runs along a wall of ``axis``
    (within 10 degrees: a swing arc drawn a few degrees short or long)."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    if n <= 0:
        return False
    return (abs(dx) if axis == "h" else abs(dy)) / n >= math.cos(math.radians(10.0))


def _shape_leaf(it: _S, arc: dict, index: StrokeIndex, owned: set):
    """A door leaf drawn as a thin shape (a closed rectangle, as CAD door blocks draw it) for a continuous-wall arc:
    the gap classifier's leaf rule (<= 60 mm wide, 0.85-1.05 r long, from the hinge along the arc's start or end
    radius). Returns ((leaf, hinge, tip, closed end), leaf ids) or (None, None)."""
    hinge, r = arc["center"], arc["radius"]
    reach = LEAF_LENGTH[1] * r + LEAF_START_M + LEAF_CORRIDOR_M
    near = [x for x in index.query((hinge[0] - reach, hinge[1] - reach, hinge[0] + reach, hinge[1] + reach))
            if x is not it and x.st.id not in owned]
    for tip, other in ((arc["end"], arc["start"]), (arc["start"], arc["end"])):
        leaf = _leaf({**arc, "start": tip, "end": tip}, near, {id(it)})
        if leaf:
            return (leaf[0], hinge, tip, other), [x.st.id for x in leaf]
    return None, None


def _continuous_windows(pieces: list[Piece], index: StrokeIndex, owned: set, theta: float, ctx: _Ctx,
                        existing: list[OpeningItem], outside=None) -> list[OpeningItem]:
    """>= 3 distinct parallel stroke offsets inside a wall band, one strictly inside it, or >= 2 strictly inside it,
    over >= 0.4 m."""
    out = []
    taken = [(_rot(o.center, -theta), o.width) for o in existing]
    for p in pieces:
        x0, y0, x1, y1 = p.rect()
        band = (x0 - BAND_SLACK_M, y0 - BAND_SLACK_M, x1 + BAND_SLACK_M, y1 + BAND_SLACK_M)
        segs = []
        for it in index.query(band, predicate="intersects"):
            if it.st.id in owned:
                continue
            pts = it.pts + ([it.pts[0]] if it.st.closed and len(it.pts) > 2 else [])
            # Fix round after P6b: a shape standing out of the wall band has no line of a window (see classify_gap).
            in_band = all(abs((q[1] if p.axis == "h" else q[0]) - p.c) <= p.t / 2 + BAND_SLACK_M for q in it.pts)
            for a, b in zip(pts, pts[1:]):
                if not _parallel(a, b, p.axis):
                    continue
                off = (a[1] + b[1]) / 2 - p.c if p.axis == "h" else (a[0] + b[0]) / 2 - p.c
                if abs(off) > p.t / 2 + BAND_SLACK_M:
                    continue
                raw = sorted((a[0], b[0])) if p.axis == "h" else sorted((a[1], b[1]))
                lo, hi = max(raw[0], p.a), min(raw[1], p.b)
                if hi - lo > 0.01:
                    segs.append((lo, hi, round(off, 3), it, raw[0], raw[1], in_band))
        if len(segs) < 2:
            continue
        cuts = sorted({s[0] for s in segs} | {s[1] for s in segs})
        intervals = []
        for u, v in zip(cuts, cuts[1:]):
            m = (u + v) / 2
            offs = {s[2] for s in segs if s[0] <= m <= s[1]}
            inner = {o for o in offs if abs(o) < p.t / 2 - BAND_SLACK_M}
            # Three offsets with one inside the band; or two inside it where the wall's faces are no strokes here
            # (walls drawn as face lines: the faces are the wall primitive, real02's glass lines lie between them).
            if (len(offs) >= 3 and inner) or len(inner) >= 2:
                if intervals and abs(intervals[-1][1] - u) < 1e-6:
                    intervals[-1][1] = v
                else:
                    intervals.append([u, v])
        for u, v in intervals:
            if v - u < CONTINUOUS_WINDOW_M:
                continue
            mid = (u + v) / 2
            centre_f = (mid, p.c) if p.axis == "h" else (p.c, mid)
            if any(math.dist(centre_f, c) < max(w / 2, 0.2) for c, w in taken):
                continue
            # Fix round after P6b: the window's own lines (``_confined``) with glass among them, not only outlines
            # inside a thick wall.
            own = [s for s in segs if s[6] and _confined(s[4], s[5], u, v)
                   and min(s[1], v) - max(s[0], u) >= WINDOW_COVER * (v - u)]
            framed = {s[2] for s in own}
            glass = {o for o in framed if abs(o) < p.t / 2 - GLASS_INSET_M}
            used = [s[3] for s in segs if s[0] < v and s[1] > u and abs(s[2]) < p.t / 2 - BAND_SLACK_M]
            ids = sorted({it.st.id for it in used})
            owned.update(ids)                        # no window without glass, but the lines stay out of furniture
            corners_f = [(u, p.c - p.t / 2), (v, p.c + p.t / 2)] if p.axis == "h" else \
                [(p.c - p.t / 2, u), (p.c + p.t / 2, v)]
            inner_wall = None
            if ctx.window_symbols and not ctx.raster and _framed_glass(framed, glass):
                # 12 Nov 2026 (review B2 FC-04, real06: its windows are PENCERE frames with DENIZLIK sills; the DUVAR
                # pair between the plaster faces made three windows per floor of solid piers): on a page that draws its
                # windows with symbols of their own, a stretch whose only glass is the wall's own face lines is no
                # window, on an outer wall as on an inner one
                own_glass = {o for o in glass if any(s[2] == o and (not wall_face_layer(s[3].st.layer)
                                                                    or _window_block(s[3].st)) for s in own)}
                if not own_glass:
                    layers = sorted({str(s[3].st.layer) for s in own if s[2] in glass})
                    inner_wall = (f"wall faces only: its {len(glass)} 'glass' line(s) along the {v - u:.2f} m stretch "
                                  f"are the wall's own face lines (layer {', '.join(layers)}) on a page that draws its "
                                  f"windows with their own symbols")
            if inner_wall is None and outside is not None and not ctx.raster and _framed_glass(framed, glass):
                # 6 Nov 2026 (real06 L1, C0064, user: "these windows are not making sense"): real06 draws a wall's
                # structure on DUVAR and its plaster on SIVA, so the DUVAR pair lies strictly between the faces; on the
                # short stretches beside the shower room's door, between its frame and a cross wall, that pair ends
                # at both ends like a window's glass. An inner wall (its stretch touches no outer face of the walls)
                # gets a window only from a symbol of its own: glass on a line off the wall layers (``wall_face_layer``)
                # (12 Nov 2026, review B-OPN-03/L2/L5: a stretch is inner when no probe past either face looks outside,
                # ``_outside_test``; a line of a window block inserted on a wall layer is the window's own)
                off = p.t / 2 + OUTSIDE_PROBE_M
                probes = [_rot((u + f * (v - u), p.c + sg * off) if p.axis == "h" else (p.c + sg * off, u + f * (v - u)),
                               theta) for f in OUTSIDE_PROBE_AT for sg in (-1.0, 1.0)]
                if not outside(probes):
                    own_glass = {o for o in glass if any(s[2] == o and (not wall_face_layer(s[3].st.layer)
                                                                        or _window_block(s[3].st)) for s in own)}
                    if not own_glass:
                        layers = sorted({str(s[3].st.layer) for s in own if s[2] in glass})
                        inner_wall = (f"an inner wall: its {len(glass)} 'glass' line(s) along the {v - u:.2f} m stretch "
                                      f"are the wall's own face lines (layer {', '.join(layers)}), no window symbol of "
                                      f"its own")
            if (not _framed_glass(framed, glass) or inner_wall) and not ctx.raster:
                # Review of the fix round: logged (the core's page notes), never dropped silently.
                ends = [(u, p.c), (v, p.c)] if p.axis == "h" else [(p.c, u), (p.c, v)]
                ctx.dropped.append({"kind": "continuous", "class": "none", "rule": "no_glass", "width": round(v - u, 4),
                                    "p0": _out(ends[0], theta), "p1": _out(ends[1], theta),
                                    "thickness": round(p.t, 4), "strokes": ids,
                                    "note": (f"{inner_wall}: no window" if inner_wall else
                                             f"{len(framed)} line(s) of their own along the {v - u:.2f} m stretch, "
                                             f"{len(glass)} glass between the faces (>= {WINDOW_LINES_MIN} and >= "
                                             f"{GLASS_MIN_LINES} needed): no window")})
                if inner_wall:
                    ctx.dropped[-1]["rule"] = "wall_faces_only" if inner_wall.startswith("wall faces only") \
                        else "inner_wall_faces"
                continue
            bx = ctx.box([_rot(q, theta) for q in corners_f])
            axis_deg = ((0.0 if p.axis == "h" else 90.0) + theta) % 180.0
            out.append(OpeningItem(kind="window", width=round(v - u, 4), center=_r(_rot(centre_f, theta)),
                                   rotation_deg=round(axis_deg, 3), box=bx, entity=ids[0] if ids else "band",
                                   evidence=ctx.evidence("vector", CONF_WINDOW, ",".join(ids), box_units=bx),
                                   height=WINDOW_HEIGHT_M, sill=WINDOW_SILL_M, assumed=["height", "sill_height"]))
            taken.append((centre_f, v - u))
    return out
