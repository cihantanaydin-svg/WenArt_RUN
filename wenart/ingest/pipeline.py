"""Project folder -> ``building.json`` + ``report.md`` + debug images.

Steps (docs/milestone2.md §2): classify pages -> convert DWG -> extract every
vector floor/furniture plan -> rooms from walls -> link openings and furniture
to walls and rooms -> cross-checks (dimension text vs measured, area label vs
computed, element counts across documents of one level, outline across
levels) -> conflicts, unverified, warnings -> schema validation -> files.

Several documents may show the same level. The best source becomes the
*master* (DWG/DXF > vector PDF; floor plan before furniture plan; then file
order); the others add evidence to the master's elements. Elements the
master lacks are added as ``unverified`` with a ``count_mismatch`` conflict,
elements a secondary page lacks are kept (the master wins) and reported.
A matched element that the second document draws differently (furniture
footprint or facing, room label) keeps the master's values, carries both
evidences, becomes ``unverified`` and gets a ``type_disagreement`` conflict.

Furniture is class-aware: a floor plan commonly draws none, so a floor plan
without furniture never conflicts with a page that has it. When the master
draws no furniture, a furniture plan of the same level is the furniture
source (its pieces keep the status the extractor gave them); any other page
that draws furniture the master lacks goes through the count check above.

``status`` is ``needs_review`` when a plan page has no scale source, the
outer walls of a level do not close, a DWG cannot be converted, a floor plan
has no level title, or no vector plan page exists at all. The files are
written in every case so the report explains what is missing.

Milestone 7 (docs/milestone7.md §1.2-§1.4, §2): pages the synthetic readers
do not understand go to the generic plan core (``generic.core.extract``):
PDF pages classified ``generic_labels`` and titled PDF pages without 0.5 pt
wall rectangles (read by ``cad_pdf``), and DXF/DWG files without the
synthetic layers (read by ``dxf_generic``). Their levels get virtual
separators, doorless openings, room-size checks, a ``site`` block (plot
walls, exterior areas, decor; recorded, never built), rule-typed stairs and
kitchen counters, and AI candidates for the other drawn furniture. The
candidates' questions are written to ``<out>/recognition/requests.json`` with
their crops; a GPU stage answers them and the pipeline runs again with
``--answers <out>/recognition``. A single untitled plan page is level ``L0``
"Ground floor" (assumed, warned); several untitled plan pages need review.

CLI: ``python -m wenart.ingest.pipeline projects/synthetic-01 --out outputs/synthetic-01
[--answers <out>/recognition] [--no-ai]``. Exit codes: 0 ok, 1 ``needs_review``,
4 = questions written and answers missing (the building is written in its
pre-answer state: AI candidates ``unknown`` / ``unverified``). With complete
answers, or with ``--no-ai`` (unanswered candidates stay ``unverified``), it
never exits 4.
"""
from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import yaml
from shapely.geometry import Polygon

from wenart import building as B
from wenart import geometry as G
from wenart import units as U
from wenart.ingest import debug_image as DI
from wenart.ingest import rooms as R
from wenart.ingest.classify import SAME_STEM_REASON, SHX_TEXT_REASON, PageRecord, classify_pages
from wenart.ingest.dxf_extract import extract_dxf
from wenart.ingest.model import DimensionItem, FurnitureItem, LevelExtraction, OpeningItem, WallItem, normalise_level
from wenart.ingest.pdf_extract import extract_pdf_page

DEFAULT_CEILING_HEIGHT = 2.70
LEVEL_PITCH = 3.00              # assumed floor-to-floor height when no section exists
WALL_TOL = 0.005                # metres: centre line and thickness matching
OPENING_TOL = 0.010             # metres: opening centre and width matching
FURNITURE_TOL = 0.010           # metres: furniture centre and footprint corner matching
ROTATION_TOL = 1.0              # degrees: furniture facing across documents
SWING_MARGIN = 0.05             # metres past the wall face where the door swing probe is placed
AREA_TOL = 0.03                 # label vs computed area: conflict beyond, unverified beyond this
DIMENSION_TOL = 0.01            # printed vs measured dimension
PRINT_EPS = 0.0051              # texts show two decimals: smaller differences are rounding
OUTLINE_TOL = 0.005             # metres, Hausdorff distance of exterior rings across levels
SOURCE_RANK = {"dwg": 0, "dxf": 0, "pdf": 1, "scan": 2, "photo": 3}   # DWG/DXF > vector PDF > scan > photo
CLASS_RANK = {"floor_plan": 0, "furniture_plan": 1}
CONFLICT_ORDER = ["area_label_vs_computed", "dimension_vs_measured", "count_mismatch", "outline_mismatch",
                  "scale_disagreement", "type_disagreement", "label_size_mismatch", "symbol_type_disagreement",
                  "raster_count_mismatch", "other"]
SOURCE_NAME = {"dwg": "DWG", "dxf": "DXF", "pdf": "vector PDF", "scan": "scan", "photo": "photo"}
RASTER_KINDS = ("scan", "photo")
RECTIFIED_DIR = "rectified"
NO_PLAN_REASON = "no floor plan page could be used"
# Evidence-only raster pages (docs/milestone7.md §0, §4.4): matching tolerances against the master and the count rule.
RASTER_WALL_TOL = 0.10          # metres, wall centre line
RASTER_THICKNESS_TOL = 0.05
RASTER_OPENING_TOL = 0.20       # metres, opening centre (same kind)
RASTER_FURNITURE_TOL = 0.15     # metres, footprint centre and sides
RASTER_COUNT_TOL = 1            # door / window / labelled-room counts may differ by one
GENERIC_PDF_DPI = 150           # debug image of generic pages (docs/milestone7.md §2.9)
EXIT_OK, EXIT_REVIEW, EXIT_QUESTIONS = 0, 1, 4
RECOGNITION_DIR = "recognition"


@dataclass
class PageWork:
    """One extracted page with its classification."""
    record: PageRecord
    extraction: LevelExtraction
    rooms: list = field(default_factory=list)   # rooms of the page's level, once assembled

    @property
    def rank(self) -> tuple:
        return page_rank(self.record)

    @property
    def where(self) -> str:
        return self.record.file if self.record.format != "pdf" else f"{self.record.file} p{self.record.page}"


def source_key(record: PageRecord) -> str:
    """The source kind that ranks a page: dwg/dxf by format, vector PDF, scan or photo by kind."""
    if record.format in ("dwg", "dxf"):
        return record.format
    return record.kind if record.kind in RASTER_KINDS else record.format


def page_rank(record: PageRecord) -> tuple:
    """Master order of a level's pages: DWG/DXF > vector PDF > scan > photo (CLAUDE.md), floor plan before furniture
    plan, then file order."""
    return (SOURCE_RANK.get(source_key(record), 9), CLASS_RANK.get(record.page_class, 9), record.file, record.page)


def pipeline_commit() -> str:
    try:
        root = Path(__file__).resolve().parents[2]
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def format_m2(value: float) -> str:
    return f"{value:.2f}".replace(".", ",")


# --------------------------------------------------------------------------
# Level assembly
# --------------------------------------------------------------------------

class ProjectBuild:
    """Mutable state while a project is assembled (keeps build_project readable)."""

    def __init__(self, building: dict) -> None:
        self.building = building
        self.ids = B.IdCounter()
        self.review_reasons: list[str] = []
        self.raw_conflicts: list[dict] = []     # without ids; numbered at the end
        self.pages: list[PageWork] = []
        self.unions: dict[str, object] = {}     # level id -> shapely wall union
        # Milestone 7: generic pages whose furniture went into the building (their questions count), the
        # recognition questions and the keys still waiting for answers.
        self.furniture_works: list[PageWork] = []
        self.questions: list[dict] = []
        self.pending: list[str] = []
        self.generic: list[PageWork] = []
        # Raster pages that stopped before a building but asked questions whose answers may let them go on (a
        # provisional scale waiting for the room-size labels, §3.4), and the review reasons those answers decide.
        self.question_only: list[LevelExtraction] = []
        self.review_after_answers: list[str] = []

    def warn(self, text: str) -> None:
        if text not in self.building["warnings"]:
            self.building["warnings"].append(text)

    def review(self, reason: str) -> None:
        self.review_reasons.append(reason)
        self.warn(f"needs review: {reason}")

    def conflict(self, kind: str, element_ids: list[str], description: str, resolution: str) -> dict:
        entry = {"kind": kind, "element_ids": list(element_ids), "description": description, "resolution": resolution}
        self.raw_conflicts.append(entry)
        return entry


def _to_building(ex: LevelExtraction, p) -> tuple[float, float]:
    return G.snap_point(G.apply_affine(ex.transform_to_building, p), 4)


def _wall_dict(level_id: str, wall: WallItem, wall_id: str, ceiling: float) -> dict:
    wall.element_id = wall_id
    return {"id": wall_id, "level_id": level_id, "start": list(wall.start), "end": list(wall.end),
            "thickness": wall.thickness, "height": ceiling, "exterior": wall.exterior, "status": wall.status,
            "evidence": [wall.evidence]}


def _nearest_wall(point, rotation_deg: float, walls: list[dict]) -> tuple[Optional[dict], float]:
    """Wall whose centre line is closest to ``point`` and parallel to ``rotation_deg``."""
    best, best_d = None, float("inf")
    for wall in walls:
        angle = G.segment_angle_deg(wall["start"], wall["end"])
        diff = G.angle_difference_deg(angle, rotation_deg)
        if min(diff, 180.0 - diff) > 2.0:
            continue
        d = G.point_segment_distance(point, wall["start"], wall["end"])
        if d < best_d:
            best, best_d = wall, d
    return best, best_d


def _swing_probe(opening: OpeningItem, wall: Optional[dict], dist: float) -> tuple[float, float]:
    """A point just past the face of ``wall`` on the side the door opens into.

    The extractor's ``swing_point`` only gives the direction: it sits a fixed
    distance from the door centre and lands inside the wall itself when the
    wall is thick. ``dist`` is how far the door centre is from the wall's
    centre line, added so an off-centre insert still clears the face.
    """
    sx, sy = opening.swing_point
    dx, dy = sx - opening.center[0], sy - opening.center[1]
    length = math.hypot(dx, dy)
    if wall is None or length < 1e-9:
        return (sx, sy)
    reach = wall["thickness"] / 2 + dist + SWING_MARGIN
    return (opening.center[0] + dx / length * reach, opening.center[1] + dy / length * reach)


def _opening_dict(level_id: str, opening: OpeningItem, opening_id: str, walls: list[dict], rooms: list[dict],
                  build: ProjectBuild) -> dict:
    opening.element_id = opening_id
    status = opening.status
    if opening.virtual:
        # A virtual separator (§2.7.1): no wall, a line between two rooms.
        line = [list(opening.line[0]), list(opening.line[1])] if opening.line else None
        return {"id": opening_id, "type": "opening", "level_id": level_id, "wall_id": None, "virtual": True,
                "line": line, "center": list(opening.center), "width": opening.width, "height": None,
                "sill_height": None, "swing_side": None, "status": status, "evidence": [opening.evidence]}
    wall, dist = _nearest_wall(opening.center, opening.rotation_deg, walls)
    if wall is None or dist > wall["thickness"] / 2 + WALL_TOL:
        status = "unverified"
        build.warn(f"{opening_id}: not on any wall of {level_id} (nearest {dist:.3f} m)")
    swing_side = None
    if opening.kind == "door" and opening.swing_point is not None:
        probe = _swing_probe(opening, wall, dist)
        room = R.room_containing(rooms, probe)
        if room is not None:
            swing_side = room["id"]
        elif wall is None or not wall["exterior"]:
            # The drawing shows a swing side but no room lies there: not a
            # door to the outside (the wall is not exterior), so do not guess.
            status = "unverified"
            build.warn(f"{opening_id}: swing side ({probe[0]:.2f}, {probe[1]:.2f}) lies in no room of {level_id}")
    out = {"id": opening_id, "type": opening.kind, "level_id": level_id, "wall_id": wall["id"] if wall else "",
           "center": list(opening.center), "width": opening.width, "height": opening.height,
           "sill_height": opening.sill, "swing_side": swing_side, "status": status, "evidence": [opening.evidence]}
    if opening.assumed:
        out["assumed"] = list(opening.assumed)
    if opening.type_raw:
        out["type_raw"] = opening.type_raw
    return out


def _furniture_dict(level_id: str, piece: FurnitureItem, piece_id: str, rooms: list[dict], build: ProjectBuild,
                    walls: Optional[list[dict]] = None) -> dict:
    piece.element_id = piece_id
    status = piece.status
    room = R.room_containing(rooms, piece.center)
    if room is None:
        status = "unverified"
        build.warn(f"{piece_id}: centre {piece.center} lies in no room of {level_id}")
    else:
        room["has_documented_furniture"] = True
    out = {"id": piece_id, "level_id": level_id, "room_id": room["id"] if room else None, "type": piece.type,
           "type_raw": piece.type_raw, "source": "from_documents",
           "footprint": {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg},
           "front_deg": piece.front_deg, "height": None, "asset": None, "status": status,
           "evidence": [piece.evidence] + list(piece.extra_evidence)}
    if piece.type_method is not None:
        # Generic core pieces (docs/milestone7.md §1.3).
        out["type_method"] = piece.type_method
        out["type_candidates"] = list(piece.type_candidates)
        out["build"] = piece.details.get("build", True) is not False
        if piece.details.get("stair"):
            out["stair"] = piece.details["stair"]
        if piece.details.get("shape"):
            # A round outline (§6.4: a round side table); Blender reads shape / circle_fit.
            out["shape"] = piece.details["shape"]
            if piece.details.get("circle_fit"):
                out["circle_fit"] = dict(piece.details["circle_fit"])
        run = piece.details.get("counter_run")
        if run:
            index = run.get("wall_index")
            wall_id = walls[index]["id"] if walls is not None and index is not None and 0 <= index < len(walls) \
                else run.get("wall_id")
            out["counter_run"] = {"wall_id": wall_id, "strokes": list(run.get("strokes") or [])}
        conflict = piece.details.get("ai_conflict")
        if conflict:
            build.conflict(conflict["kind"], [piece_id], f"{piece_id}: {conflict['description']}",
                           conflict["resolution"])
    return out


def _level_dict(level_id: str, record: PageRecord, works: list[PageWork]) -> dict:
    label, order = record.level_label, record.level_order
    if label is None:
        normalised = normalise_level(record.level_label_raw or "")
        label, order = normalised if normalised else (level_id, 0)
    level = {
        "id": level_id, "label": label, "order": order, "elevation": round(order * LEVEL_PITCH, 3),
        "ceiling_height": DEFAULT_CEILING_HEIGHT, "ceiling_height_source": "assumed_default",
        "evidence": [e for w in works for e in w.record.evidence],
    }
    if record.label_source is not None:
        level["label_source"] = record.label_source
    return level


def _generic_rooms(build: ProjectBuild, level_id: str, ex: LevelExtraction) -> R.RoomResult:
    """Rooms of a generic page: faces of the bridged wall union (openings and separators), named by the label
    blocks (docs/milestone7.md §2.7)."""
    from wenart.ingest.generic import topology as TP

    stairs = [f for f in ex.furniture if f.type == "stair"]
    real = [o for o in ex.openings if not o.virtual]
    union = TP.bridged_union(ex.walls, real, ex.separators)

    def face_type(poly):
        return TP.unlabelled_face_type(poly, ex.walls, real, stairs)

    anchors = [_to_building(ex, t.start) for t in ex.labels]
    fallbacks = [_to_building(ex, G.box_center(t.box)) for t in ex.labels]
    result = R.derive_rooms(level_id, ex.walls, ex.labels, anchors, fallbacks, ex.file, build.ids, union=union,
                            unlabelled_label=ex.report.get("unlabelled_label", R.UNLABELLED_LABEL),
                            face_type=face_type)
    system = ex.units_system
    for room_id, check in result.label_size_conflicts:
        measured = check["measured"]
        sides = " x ".join(U.format_length(v, system or "metric") for v in measured)
        offs = ", ".join(f"{v:+.1f}%" for v in check.get("off_pct", []))
        unverified = check.get("unverified")
        build.conflict("label_size_mismatch", [room_id],
                       f"{room_id}: label size '{check['text']}' vs the room's clear size {sides} ({offs})",
                       "drawn walls kept; room marked unverified" if unverified else
                       "drawn walls kept (within 10 %)")
    for room_id, label, others in result.multi_labels:
        build.conflict("other", [room_id], f"{room_id}: one face holds the room names '{label}' and "
                                           f"{', '.join(repr(o) for o in others)}",
                       "unresolved: first label kept, room unverified")
    return result


def _assemble_level(build: ProjectBuild, level_id: str, works: list[PageWork]) -> None:
    """Master page -> walls, rooms, openings, furniture; other pages -> evidence and count checks."""
    bld = build.building
    works = sorted(works, key=lambda w: w.rank)
    master = works[0]
    ex = master.extraction
    record = master.record
    level = _level_dict(level_id, record, works)
    bld["levels"].append(level)
    build.warn(f"Level {level_id}: ceiling height assumed {DEFAULT_CEILING_HEIGHT:.2f} m (no section drawing found)")
    generic = ex.source_kind is not None

    # Rooms need the walls first (exterior flags come from the union).
    if generic:
        result = _generic_rooms(build, level_id, ex)
    else:
        anchors = [_to_building(ex, t.start) for t in ex.labels]
        fallbacks = [_to_building(ex, G.box_center(t.box)) for t in ex.labels]
        result = R.derive_rooms(level_id, ex.walls, ex.labels, anchors, fallbacks, ex.file, build.ids)
    for text in result.warnings:
        build.warn(text)
    if not result.closed and not any("outer walls do not close" in r for r in ex.review):
        build.review(f"{level_id}: outer walls do not form a closed loop ({master.where})")
    if result.unplaced_labels:
        # A room label outside every face means the walls around that room do not close.
        names = ", ".join(f"'{t.text}'" for t in result.unplaced_labels)
        build.review(f"{level_id}: room labels outside every enclosed room ({names}); walls do not close ({master.where})")
    if generic:
        from wenart.ingest.generic import topology as TP
        build.unions[level_id] = TP.bridged_union(ex.walls, [o for o in ex.openings if not o.virtual],
                                                  ex.separators) if ex.walls else None
    else:
        build.unions[level_id] = R.wall_union(ex.walls) if ex.walls else None

    walls = [_wall_dict(level_id, w, build.ids.next("wall", level_id), DEFAULT_CEILING_HEIGHT) for w in ex.walls]
    bld["walls"].extend(walls)
    rooms = result.rooms
    for room in rooms:
        wall_ids = [walls[i]["id"] for i in result.room_walls.get(room["id"], [])]
        room["evidence"].append(B.evidence(ex.file, "derived", 1.0, entity="derived-from:" + ",".join(wall_ids)))
        if not room["evidence"]:
            room["evidence"].append(B.evidence(ex.file, "derived", 0.5, entity="derived-from:walls"))
    for i, text in enumerate(ex.labels):
        for room in rooms:
            if any(e is text.evidence for e in room["evidence"]):
                text.element_id = room["id"]
    if generic:
        for text in ex.labels:
            room = R.room_containing(rooms, _to_building(ex, text.start))
            if room is not None and room["label_raw"] is not None:
                text.element_id = room["id"]
    if (ex.source_kind or "").startswith("raster"):
        _raster_room_labels(build, level_id, ex, rooms, master.where)
    bld["rooms"].extend(rooms)

    openings = []
    for opening in list(ex.openings) + list(ex.separators):
        opening_id = build.ids.next(opening.kind, level_id)
        openings.append(_opening_dict(level_id, opening, opening_id, walls, rooms, build))
    bld["openings"].extend(openings)
    if generic:
        # Rooms bounded by a separator name it as evidence too.
        for opening, element in zip(list(ex.openings) + list(ex.separators), openings):
            if not opening.virtual or not opening.line:
                continue
            for room in rooms:
                if any(G.point_segment_distance(p, *opening.line) <= 0.01 for p in room["polygon"]):
                    room["evidence"].append(B.evidence(ex.file, "derived", 0.8, entity=f"separator:{element['id']}"))

    furniture = []
    for piece in ex.furniture:
        furniture.append(_furniture_dict(level_id, piece, build.ids.next("furniture", level_id), rooms, build, walls))
    bld["furniture"].extend(furniture)
    if ex.furniture or (ex.report or {}).get("questions"):
        # Its questions go to requests.json: furniture candidates, and the room_label questions of a raster page
        # (asked for every room face, furnished or not, §3.4).
        build.furniture_works.append(master)
    if generic:
        _add_site(build, level_id, ex)

    for work in works[1:]:
        if work.record.kind in RASTER_KINDS:
            _merge_raster_evidence(build, level_id, level["label"], master, work, walls, openings, furniture, rooms)
        else:
            _merge_secondary(build, level_id, level["label"], master, work, walls, openings, furniture, rooms)

    for work in works:
        _check_dimensions(build, work, walls, evidence_only=work is not master and work.record.kind in RASTER_KINDS)
    _check_areas(build, rooms, master)


def _raster_room_labels(build: ProjectBuild, level_id: str, ex: LevelExtraction, rooms: list[dict], where: str) -> None:
    """Rooms of a raster master page (§3.4): a name accepted by the two passes (or one pass equal to Tesseract)
    keeps the room's status and adds the passes' evidence; a name Tesseract read but no pass confirmed leaves the
    room ``unverified`` (and says so)."""
    to_building = ex.transform_to_building
    for entry in (ex.report.get("raster") or {}).get("labels") or []:
        anchor = entry.get("anchor")
        if not anchor or len(anchor) < 2:
            continue
        room = R.room_containing(rooms, G.apply_affine(to_building, anchor))
        if room is None:
            continue
        for e in entry.get("evidence") or []:
            if e not in room["evidence"]:
                room["evidence"].insert(len([x for x in room["evidence"] if x["method"] != "derived"]), dict(e))
        if entry.get("label"):
            continue
        if room["label_raw"] is not None:
            room["status"] = "unverified"
            build.warn(f"{room['id']}: room label '{room['label_raw']}' read by Tesseract only on {where}; not "
                       f"confirmed by the two VLM passes (§3.4), room unverified")


def _merge_raster_evidence(build: ProjectBuild, level_id: str, level_label: str, master: PageWork, work: PageWork,
                           walls: list[dict], openings: list[dict], furniture: list[dict], rooms: list[dict]) -> None:
    """A raster page of a level that has a better page is evidence only (docs/milestone7.md §0, §4.4): what it shows
    at the master's place (walls: centre line <= 0.10 m, thickness <= 0.05 m; doors and windows: same kind, centre
    <= 0.20 m; furniture: centre and sides <= 0.15 m; room names equal to the master's) adds its evidence to the
    master's element; nothing is added, moved or re-typed. Door, window and labelled-room counts are compared and a
    difference of more than one is a ``raster_count_mismatch`` conflict."""
    ex = work.extraction
    master_name = SOURCE_NAME.get(source_key(master.record), "document")
    sec_name = SOURCE_NAME.get(source_key(work.record), "document")

    def wall_hit(item: WallItem) -> Optional[dict]:
        mid = ((item.start[0] + item.end[0]) / 2.0, (item.start[1] + item.end[1]) / 2.0)
        best, best_d = None, RASTER_WALL_TOL
        for wall in walls:
            if G.angle_difference_deg(G.segment_angle_deg(wall["start"], wall["end"]) % 180.0,
                                      G.segment_angle_deg(item.start, item.end) % 180.0) > 3.0 and \
                    G.angle_difference_deg(G.segment_angle_deg(wall["start"], wall["end"]) % 180.0,
                                           (G.segment_angle_deg(item.start, item.end) + 180.0) % 180.0) > 3.0:
                continue
            if abs(wall["thickness"] - item.thickness) > RASTER_THICKNESS_TOL:
                continue
            d = G.point_segment_distance(mid, wall["start"], wall["end"])
            if d <= best_d:
                best, best_d = wall, d
        return best

    matched = {"walls": 0, "openings": 0, "furniture": 0, "labels": 0}
    for item in ex.walls:
        wall = wall_hit(item)
        if wall is not None:
            wall["evidence"].append(item.evidence)
            matched["walls"] += 1
    for item in ex.openings:
        hit = min((o for o in openings if o["type"] == item.kind),
                  key=lambda o: G.distance(item.center, o["center"]), default=None)
        if hit is not None and G.distance(item.center, hit["center"]) <= RASTER_OPENING_TOL:
            hit["evidence"].append(item.evidence)
            matched["openings"] += 1
    for item in ex.furniture:
        hit = min(furniture, key=lambda f: G.distance(item.center, f["footprint"]["center"]), default=None)
        if hit is None or G.distance(item.center, hit["footprint"]["center"]) > RASTER_FURNITURE_TOL:
            continue
        size = sorted(hit["footprint"]["size"])
        if all(abs(a - b) <= RASTER_FURNITURE_TOL for a, b in zip(sorted(item.size), size)):
            hit["evidence"].append(item.evidence)
            matched["furniture"] += 1
    labelled = 0
    for text in ex.labels:
        if text.block is not None and text.block.exterior:
            continue
        labelled += 1
        label, _, _ = B.normalise_room_label(text.text, turkish=text.turkish)
        room = R.room_containing(rooms, _to_building(ex, text.start))
        if room is not None and room["label"] == label:
            room["evidence"].insert(len([e for e in room["evidence"] if e["method"] != "derived"]), text.evidence)
            matched["labels"] += 1
    level_rooms = [r for r in rooms if r["label_raw"] is not None]
    counts = [("doors", len(ex.doors()), sum(1 for o in openings if o["type"] == "door")),
              ("windows", len(ex.windows()), sum(1 for o in openings if o["type"] == "window")),
              ("labelled rooms", labelled, len(level_rooms))]
    for what, theirs, mine in counts:
        if abs(theirs - mine) > RASTER_COUNT_TOL:
            ids = [o["id"] for o in openings if (what == "doors" and o["type"] == "door")
                   or (what == "windows" and o["type"] == "window")] if what != "labelled rooms" else \
                [r["id"] for r in level_rooms]
            build.conflict("raster_count_mismatch", ids or [level_id],
                           f"{level_label}: {master.where} has {mine} {what}, the {sec_name} {work.where} shows {theirs} "
                           f"(more than {RASTER_COUNT_TOL} apart)",
                           f"{master_name} wins; the {sec_name} is evidence only")
    build.warn(f"{level_label}: {work.where} ({sec_name}) is evidence only for {master.where}: "
               f"{matched['walls']} walls, {matched['openings']} openings, {matched['furniture']} furniture pieces and "
               f"{matched['labels']} room names confirmed")


def _add_site(build: ProjectBuild, level_id: str, ex: LevelExtraction) -> None:
    """The level's ``site`` block (building frame) into ``building["site"]``: plot and other boundary walls,
    exterior areas, decor and the openings of boundary walls; recorded, never built (§2.5)."""
    site = ex.site or {}
    target = build.building.setdefault("site", {"boundary_walls": [], "areas": [], "decor": [], "openings": []})
    ids = []
    for k, w in enumerate(site.get("boundary_walls", [])):
        item = {"id": w.get("id") or f"sw_{level_id}_{k + 1:03d}", "level_id": level_id, **{
            key: v for key, v in w.items() if key != "id"}}
        ids.append(item["id"])
        target["boundary_walls"].append(item)
    for a in site.get("areas", []):
        target["areas"].append({"id": a.get("id"), "level_id": level_id, **{k: v for k, v in a.items() if k != "id"}})
    for d in site.get("decor", []):
        target["decor"].append({"id": d.get("id"), "level_id": level_id,
                                **{k: v for k, v in d.items() if k not in ("id", "box")}})
    for k, o in enumerate(site.get("openings", [])):
        index = o.get("boundary_wall")
        item = {"id": f"so_{level_id}_{k + 1:03d}", "level_id": level_id, "type": o["type"], "center": o["center"],
                "width": o["width"], "boundary_wall_id": ids[index] if index is not None and index < len(ids) else None,
                "status": o.get("status", "verified"), "evidence": o.get("evidence", [])}
        target["openings"].append(item)


def _match(items, candidates, match_fn):
    """Greedy one-to-one matching; returns (pairs, unmatched items, unmatched candidates)."""
    taken = set()
    pairs = []
    unmatched = []
    for item in items:
        hit = None
        for j, cand in enumerate(candidates):
            if j in taken:
                continue
            if match_fn(item, cand):
                hit = j
                break
        if hit is None:
            unmatched.append(item)
        else:
            taken.add(hit)
            pairs.append((item, candidates[hit]))
    left = [c for j, c in enumerate(candidates) if j not in taken]
    return pairs, unmatched, left


def _footprint_disagreement(item: FurnitureItem, piece: dict, master_where: str, item_where: str) -> Optional[str]:
    """How the secondary page draws a matched piece differently, or None.

    The footprint is compared corner by corner (so a rectangle given with
    swapped width/depth and a 90 degree turn still agrees); the facing is
    compared only when both documents mark a front side.
    """
    fp = piece["footprint"]
    theirs = G.rotated_rectangle(item.center, item.size, item.rotation_deg)
    mine = G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"])
    if any(min(G.distance(a, b) for b in mine) > FURNITURE_TOL for a in theirs):
        return (f"footprint {fp['size'][0]:.2f} x {fp['size'][1]:.2f} m at {fp['rotation_deg']:.0f} deg in {master_where}, "
                f"{item.size[0]:.2f} x {item.size[1]:.2f} m at {item.rotation_deg:.0f} deg in {item_where}")
    if (item.front_deg is not None and piece["front_deg"] is not None
            and G.angle_difference_deg(item.rotation_deg, fp["rotation_deg"]) > ROTATION_TOL):
        return f"rotation {fp['rotation_deg']:.0f} deg in {master_where}, {item.rotation_deg:.0f} deg in {item_where}"
    return None


def _merge_secondary(build: ProjectBuild, level_id: str, level_label: str, master: PageWork, work: PageWork,
                     walls: list[dict], openings: list[dict], furniture: list[dict], rooms: list[dict]) -> None:
    ex = work.extraction
    master_name = SOURCE_NAME.get(source_key(master.record), "document")
    sec_name = SOURCE_NAME.get(source_key(work.record), "document")

    def wall_match(item: WallItem, wall: dict) -> bool:
        return (G.distance(item.start, wall["start"]) <= WALL_TOL and G.distance(item.end, wall["end"]) <= WALL_TOL
                and abs(item.thickness - wall["thickness"]) <= WALL_TOL)

    def opening_match(item: OpeningItem, opening: dict) -> bool:
        return (item.kind == opening["type"] and G.distance(item.center, opening["center"]) <= OPENING_TOL
                and abs(item.width - opening["width"]) <= OPENING_TOL)

    def furniture_match(item: FurnitureItem, piece: dict) -> bool:
        same_type = item.type == piece["type"] or "unknown" in (item.type, piece["type"])
        return same_type and G.distance(item.center, piece["footprint"]["center"]) <= FURNITURE_TOL

    def furniture_disagreement(item: FurnitureItem, piece: dict) -> Optional[str]:
        return _footprint_disagreement(item, piece, master.where, work.where)

    def make_furniture(item: FurnitureItem, element_id: str) -> dict:
        return _furniture_dict(level_id, item, element_id, rooms, build, walls)

    # (kind, secondary items, master elements, match, build element, describe a disagreement)
    groups = [
        ("wall", ex.walls, walls, wall_match, lambda it, eid: _wall_dict(level_id, it, eid, DEFAULT_CEILING_HEIGHT), None),
        ("door", ex.doors(), [o for o in openings if o["type"] == "door"], opening_match,
         lambda it, eid: _opening_dict(level_id, it, eid, walls, rooms, build), None),
        ("window", ex.windows(), [o for o in openings if o["type"] == "window"], opening_match,
         lambda it, eid: _opening_dict(level_id, it, eid, walls, rooms, build), None),
    ]
    furniture_plan = work.record.page_class == "furniture_plan"
    if ex.furniture and not furniture and furniture_plan:
        # The master (a floor plan) draws no furniture: the furniture plan is
        # the furniture source of this level. Pieces keep the extractor's status.
        for item in ex.furniture:
            element = make_furniture(item, build.ids.next("furniture", level_id))
            build.building["furniture"].append(element)
            furniture.append(element)
        build.furniture_works.append(work)
        build.warn(f"{level_label}: furniture taken from {work.where} ({len(ex.furniture)} pieces); "
                   f"{master.where} draws none")
    elif ex.furniture or (furniture and furniture_plan):
        # Both pages draw furniture, a page other than a furniture plan draws
        # what the master lacks, or a furniture plan draws none: cross-check.
        # A floor plan without furniture is normal and is not compared.
        groups.append(("furniture", ex.furniture, furniture, furniture_match, make_furniture, furniture_disagreement))
    target = {"wall": build.building["walls"], "door": build.building["openings"],
              "window": build.building["openings"], "furniture": build.building["furniture"]}
    plural = {"wall": "walls", "door": "doors", "window": "windows", "furniture": "furniture pieces"}
    for kind, items, candidates, match_fn, make, disagreement in groups:
        master_count, secondary_count = len(candidates), len(items)
        pairs, extra, missing = _match(items, candidates, match_fn)
        for item, element in pairs:
            element["evidence"].append(item.evidence)
            item.element_id = element["id"]
            text = disagreement(item, element) if disagreement else None
            if text is not None:
                element["status"] = item.status = "unverified"
                build.conflict("type_disagreement", [element["id"]],
                               f"{level_label}: {element['id']} ({element.get('type', kind)}) {text}",
                               f"{master_name} wins over {sec_name}, {kind} kept as drawn there")
        if not extra and not missing:
            continue
        element_ids = [m["id"] for m in missing]
        for item in extra:
            item.status = "unverified"
            element = make(item, build.ids.next(kind, level_id))
            element["status"] = "unverified"
            target[kind].append(element)
            if kind in ("door", "window"):
                openings.append(element)
            elif kind == "wall":
                walls.append(element)
            else:
                furniture.append(element)
            element_ids.append(element["id"])
        description = (f"{level_label}: {master.where} has {master_count} {plural[kind]}, "
                       f"{work.where} has {secondary_count}")
        resolution = f"{master_name} wins over {sec_name}, {kind} kept"
        if extra:
            resolution += f"; {len(extra)} extra from {sec_name} added as unverified"
        build.conflict("count_mismatch", element_ids, description, resolution)

    # Room labels of the secondary page confirm the master's rooms, or disagree.
    for text in ex.labels:
        if text.block is not None and text.block.exterior:
            continue
        label, _, _ = B.normalise_room_label(text.text, turkish=text.turkish)
        anchor = _to_building(ex, text.start)
        room = R.room_containing(rooms, anchor) or R.room_containing(rooms, _to_building(ex, G.box_center(text.box)))
        if room is None:
            build.warn(f"{work.where}: label '{text.text}' lies in no room of {level_id}")
            continue
        room["evidence"].insert(len([e for e in room["evidence"] if e["method"] != "derived"]), text.evidence)
        text.element_id = room["id"]
        if room["label"] == label:
            continue
        if room["label_raw"] is None:
            # The master page has no label for this face; it stays unverified
            # under the master's placeholder name, the secondary's text is evidence.
            build.warn(f"{work.where}: label '{text.text}' names room {room['id']}, which has no label in {master.where}")
            continue
        room["status"] = "unverified"
        build.conflict("type_disagreement", [room["id"]],
                       f"{level_label}: {master.where} labels room {room['id']} '{room['label']}', "
                       f"{work.where} labels it '{label}'",
                       f"{master_name} wins over {sec_name}, label kept")


def _link_dimension_walls(dim: DimensionItem, walls: list[dict]) -> list[str]:
    """Nearest parallel wall(s) whose centre line covers the measured span."""
    direction = G.segment_angle_deg(dim.p1, dim.p2)
    hits = []
    for wall in walls:
        angle = G.segment_angle_deg(wall["start"], wall["end"])
        diff = G.angle_difference_deg(direction, angle)
        if min(diff, 180.0 - diff) > 1.0:
            continue
        length = G.distance(wall["start"], wall["end"])
        if length < 1e-9:
            continue
        ux = (wall["end"][0] - wall["start"][0]) / length
        uy = (wall["end"][1] - wall["start"][1]) / length
        ts = [((p[0] - wall["start"][0]) * ux + (p[1] - wall["start"][1]) * uy) for p in (dim.p1, dim.p2)]
        if min(ts) < -WALL_TOL or max(ts) > length + WALL_TOL:
            continue
        offset = abs((dim.p1[0] - wall["start"][0]) * -uy + (dim.p1[1] - wall["start"][1]) * ux)
        hits.append((offset, wall["id"]))
    if not hits:
        return []
    hits.sort()
    nearest = hits[0][0]
    return [wall_id for offset, wall_id in hits if offset - nearest <= WALL_TOL]


def _check_dimensions(build: ProjectBuild, work: PageWork, walls: list[dict], evidence_only: bool = False) -> None:
    """Dimension text vs measured length. On an evidence-only raster page (§0) the dimensions measure that page's
    own raster geometry (the master's geometry is kept), so a difference is reported as a warning, not a conflict."""
    ex = work.extraction
    source = SOURCE_NAME.get(source_key(work.record), "document")
    for dim in ex.dimensions:
        dim.wall_ids = _link_dimension_walls(dim, walls)
        if dim.printed_value is None or dim.measured <= 0:
            continue
        diff = abs(dim.printed_value - dim.measured)
        if diff <= PRINT_EPS or diff / dim.measured <= DIMENSION_TOL:
            continue
        pct = diff / dim.measured * 100.0
        if evidence_only:
            build.warn(f"{work.where} (evidence only): dimension text {dim.printed} vs {dim.measured:.2f} m measured on "
                       f"the raster ({pct:.1f}%)")
            continue
        entry = build.conflict("dimension_vs_measured", dim.wall_ids or [work.extraction.level_id],
                               f"{work.where}: dimension text {dim.printed} vs measured {dim.measured:.2f} m ({pct:.1f}%)",
                               f"kept measured geometry ({source})")
        dim.conflict_id = entry["description"]


def _check_areas(build: ProjectBuild, rooms: list[dict], master: PageWork) -> None:
    for room in rooms:
        label_area = room.get("area_label")
        if label_area is None or room["area_computed"] <= 0:
            continue
        diff = abs(label_area - room["area_computed"])
        if diff <= PRINT_EPS:
            continue
        pct = diff / label_area * 100.0
        description = (f"Label says {format_m2(label_area)} m², polygon gives {format_m2(room['area_computed'])} m² "
                       f"({pct:.1f}%)")
        if diff / label_area <= AREA_TOL:
            resolution = f"within tolerance ({AREA_TOL * 100:.0f}%), kept polygon from {master.record.file}"
        else:
            resolution = f"over {AREA_TOL * 100:.0f}%: room marked unverified, polygon from {master.record.file} kept"
            room["status"] = "unverified"
        build.conflict("area_label_vs_computed", [room["id"]], description, resolution)


def _check_outlines(build: ProjectBuild) -> None:
    """Exterior rings of all levels should coincide (same building footprint)."""
    levels = []
    for lv in build.building["levels"]:
        union = build.unions.get(lv["id"])
        if union is None:
            continue
        if union.geom_type != "Polygon":
            # Disconnected wall groups have no single exterior ring; the level
            # is already a review reason, so only say why it is not compared.
            build.warn(f"outline check skipped for {lv['id']}: walls do not form one closed loop ({union.geom_type})")
            continue
        levels.append(lv)
    if len(levels) < 2:
        return
    base = next((lv for lv in levels if lv["id"] == "L0"), levels[0])
    base_poly = Polygon(build.unions[base["id"]].exterior)
    for lv in levels:
        if lv is base:
            continue
        poly = Polygon(build.unions[lv["id"]].exterior)
        distance = base_poly.hausdorff_distance(poly)
        if distance > OUTLINE_TOL:
            build.conflict("outline_mismatch", [base["id"], lv["id"]],
                           f"Outer wall outline of {lv['label']} differs from {base['label']} by up to {distance:.3f} m "
                           f"(areas {base_poly.area:.2f} / {poly.area:.2f} m²)",
                           "unresolved: each level kept as drawn")


# --------------------------------------------------------------------------
# Documents, debug images, report
# --------------------------------------------------------------------------

def _source_kind(record: PageRecord, work: Optional[PageWork]) -> Optional[str]:
    if work is not None and work.extraction.source_kind:
        return work.extraction.source_kind
    if record.format in ("dxf", "dwg"):
        return "dxf"
    if record.format == "pdf" and record.kind == "vector":
        return "cad_pdf"
    if record.kind in RASTER_KINDS and record.extractor == "raster":
        return "raster_scan" if record.kind == "scan" else "raster_photo"
    return None


def _documents(records: list[PageRecord], works: dict, out_dir: Path, project_dir: Path, build: ProjectBuild) -> list[dict]:
    docs: dict[str, dict] = {}
    for record in records:
        doc = docs.setdefault(record.file, {"id": "doc_" + B.slugify(record.file), "file": record.file,
                                            "format": record.format, "converter": record.converter, "pages": []})
        if record.conversion:
            doc["conversion"] = {k: v for k, v in record.conversion.items() if k != "converter"}
        entry = record.to_json()
        work = works.get((record.file, record.page))
        if work is not None:
            entry["scale"] = work.extraction.scale
            entry["transform_to_building"] = work.extraction.transform_to_building
            doc["unit_system"] = work.extraction.units_system or "metric"
            if work.extraction.report.get("rectified_image"):
                entry["rectified_image"] = work.extraction.report["rectified_image"]
                entry["to_original"] = work.extraction.report["to_original"]
        kind = _source_kind(record, work)
        if kind is not None and "source_kind" not in doc:
            doc["source_kind"] = kind
        debug_path = _debug_image(record, work, out_dir, project_dir, build)
        entry["debug_image"] = debug_path.relative_to(out_dir).as_posix() if debug_path else None
        doc["pages"].append(entry)
    return list(docs.values())


def _raster_debug_images(record: PageRecord, work: PageWork, out_path: Path, build: ProjectBuild) -> Optional[Path]:
    """Raster pages (§4.1): the overlays drawn on the **original** image through ``to_original`` (walls, openings,
    rooms, furniture, labels as on generic pages, coloured by method and confidence; the wall mask warped onto it;
    the page quad of a photo) and the same overlays on the rectified image (``<name>_rectified.png``)."""
    import cv2
    from PIL import Image

    ex = work.extraction
    rp = ex.report.get("raster_page")
    if rp is None or rp.original is None:
        return None
    h_page = np.asarray(ex.report["to_original"], dtype=np.float64)
    original = np.asarray(rp.original, dtype=np.uint8)
    factor = min(1.0, DI.IMAGE_MAX_WIDTH / float(original.shape[1]))

    def to_orig(p):
        x, y = p[0], p[1]
        w = h_page[2, 0] * x + h_page[2, 1] * y + h_page[2, 2]
        return (((h_page[0, 0] * x + h_page[0, 1] * y + h_page[0, 2]) / w + 0.5) * factor,
                ((h_page[1, 0] * x + h_page[1, 1] * y + h_page[1, 2]) / w + 0.5) * factor)

    items = _generic_debug_items(work, build.building)
    note = (f"{record.file} p{record.page}: {record.page_class} / {record.kind}"
            + (" (evidence only)" if (ex.report.get("raster") or {}).get("evidence_only") else ""))
    rect = rp.rect
    page_h = rp.image.shape[0]
    mask = ex.report.get("mask")
    s = ex.report.get("units_to_m") or 1.0

    def mask_page_px() -> Optional[np.ndarray]:
        """The core's wall mask (page metres) resampled onto the rectified image's pixels."""
        if mask is None or not np.asarray(mask.mask).any():
            return None
        x0, y1 = mask.origin
        px = mask.px / s                                   # page units per mask pixel
        # Rectified pixel (c, r) centre = page (c + 0.5, H - r - 0.5) -> mask (col, row).
        a = np.array([[1.0 / px, 0.0, (0.5 - x0 / s) / px - 0.5],
                      [0.0, 1.0 / px, (y1 / s - page_h + 0.5) / px - 0.5]], np.float64)
        return cv2.warpAffine(np.asarray(mask.mask).astype(np.uint8), a, (rp.image.shape[1], page_h),
                              flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderValue=0)

    def tinted(base: np.ndarray, m: Optional[np.ndarray]) -> Image.Image:
        img = Image.fromarray(base).convert("RGB")
        if m is not None and m.any():
            tint = Image.new("RGBA", img.size, DI.MASK_COLOUR + (0,))
            tint.putalpha(Image.fromarray((m > 0).astype(np.uint8) * DI.MASK_ALPHA))
            img = Image.alpha_composite(img.convert("RGBA"), tint).convert("RGB")
        return img

    m_rect = mask_page_px()
    # On the original: warp the mask with the rectified -> original homography, then scale for display.
    m_orig = None
    if m_rect is not None:
        m_orig = cv2.warpPerspective(m_rect, np.asarray(rect.to_original, np.float64),
                                     (original.shape[1], original.shape[0]), flags=cv2.INTER_NEAREST, borderValue=0)
    base = original if factor == 1.0 else cv2.resize(original, None, fx=factor, fy=factor,
                                                      interpolation=cv2.INTER_AREA)
    if m_orig is not None and factor != 1.0:
        m_orig = cv2.resize(m_orig, (base.shape[1], base.shape[0]), interpolation=cv2.INTER_NEAREST)
    orig_items = list(items)
    if rect.quad:
        quad = [(p[0] + 0.5, p[1] + 0.5) for p in rect.quad]
        # The page quad is in original pixels already: give it in page units by mapping back.
        inv = np.linalg.inv(h_page)
        quad_page = []
        for x, y in quad:
            v = inv @ np.array([x - 0.5, y - 0.5, 1.0])
            quad_page.append((v[0] / v[2], v[1] / v[2]))
        orig_items.append(DI.DebugItem(quad_page, "raster", 1.0, label="page quad", colour=(0, 160, 160), width=2))
    raster = DI.PageRaster(image=tinted(base, m_orig), to_pixels=to_orig)
    DI.write_debug_image(raster, orig_items, out_path,
                         note=DI.legend_note(note + " | drawn on the original image", generic=True))
    rect_raster = DI.PageRaster(image=tinted(rp.image, m_rect), to_pixels=lambda p: (p[0], page_h - p[1]))
    DI.write_debug_image(rect_raster, items, out_path.with_name(out_path.stem + "_rectified.png"),
                         note=DI.legend_note(note + " | rectified page", generic=True))
    return out_path


def _debug_image(record: PageRecord, work: Optional[PageWork], out_dir: Path, project_dir: Path,
                 build: ProjectBuild) -> Optional[Path]:
    out_path = out_dir / "debug" / f"{B.slugify(record.file)}_p{record.page}.png"
    if work is not None and work.record.kind in RASTER_KINDS and work.extraction.report.get("raster_page"):
        try:
            done = _raster_debug_images(record, work, out_path, build)
        except Exception as exc:  # noqa: BLE001 - a failed debug image must not stop the pipeline
            build.warn(f"{record.file} p{record.page}: debug image not rendered ({exc})")
            done = None
        if done is not None:
            return done
    source = Path(record.source_path) if record.source_path else project_dir / record.file
    generic = work is not None and work.extraction.source_kind is not None
    try:
        if record.format == "pdf":
            raster = DI.raster_from_pdf(source, record.page, dpi=GENERIC_PDF_DPI if generic else DI.PDF_DPI)
        elif record.format in ("dxf", "dwg"):
            raster = DI.raster_from_dxf(source)
        else:
            raster = DI.raster_from_image(source)
    except Exception as exc:  # noqa: BLE001 - a failed debug image must not stop the pipeline
        build.warn(f"{record.file} p{record.page}: debug image not rendered ({exc})")
        return None
    items: list[DI.DebugItem] = []
    note = f"{record.file} p{record.page}: {record.page_class} / {record.kind}"
    if work is None:
        note += f" | skipped: {record.skip_reason}" if record.skip_reason else " | not extracted"
    elif generic:
        items = _generic_debug_items(work, build.building)
        mask = work.extraction.report.get("mask")
        if mask is not None:
            DI.overlay_mask(raster, mask, work.extraction.report.get("units_to_m") or 1.0)
        DI.write_debug_image(raster, items, out_path, note=DI.legend_note(note, generic=True))
        return out_path
    else:
        items = _debug_items(work)
    DI.write_debug_image(raster, items, out_path, note=DI.legend_note(note))
    return out_path


def _generic_debug_items(work: PageWork, building: dict) -> list[DI.DebugItem]:
    """Overlays of a generic page (docs/milestone7.md §2.9): wall centre lines by method and confidence, doors with
    their swing arc, windows, doorless openings dashed, separators dashed magenta, rooms with label and type,
    furniture by ``type_method`` (rule green, block_name blue, ai_two_pass cyan, none red striped), site grey,
    scale dimensions orange. The wall mask is drawn under them (``DI.overlay_mask``)."""
    ex = work.extraction
    to_page = G.invert_affine(ex.transform_to_building)

    def page(pts) -> list:
        return [G.apply_affine(to_page, p) for p in pts]

    items: list[DI.DebugItem] = []
    level_id = ex.level_id
    for room in work.rooms:
        label = f"{room['id']} {room['label']} ({room['room_type']})"
        items.append(DI.DebugItem(page(room["polygon"]), "derived", 1.0, label=label, status=room["status"], width=1))
    for wall in ex.walls:
        corners = G.centerline_to_rectangle(wall.start, wall.end, wall.thickness)
        items.append(DI.DebugItem(page(corners), wall.evidence["method"], wall.evidence["confidence"],
                                  label=wall.element_id or "", status=wall.status, width=1))
        items.append(DI.DebugItem(page([wall.start, wall.end]), wall.evidence["method"],
                                  wall.evidence["confidence"], closed=False, width=2))
    for opening in ex.openings:
        corners = G.box_corners(opening.box)
        method = opening.evidence.get("method", "vector")
        conf = opening.evidence.get("confidence", 1.0)
        if opening.kind == "opening":
            items.append(DI.DebugItem(corners, method, conf, label=opening.element_id or "?", status=opening.status,
                                      dashed=True))
            continue
        items.append(DI.DebugItem(corners, method, conf, label=opening.element_id or "?", status=opening.status))
        if opening.kind == "door" and opening.swing_point is not None:
            # The swing: a quarter circle from the hinge side over the swing point (drawn, not measured).
            c = opening.center
            r = opening.width
            rot = math.radians(opening.rotation_deg)
            u = (math.cos(rot), math.sin(rot))
            v = (opening.swing_point[0] - c[0], opening.swing_point[1] - c[1])
            norm = math.hypot(*v) or 1.0
            v = (v[0] / norm, v[1] / norm)
            hinge = (c[0] - u[0] * r / 2.0, c[1] - u[1] * r / 2.0)
            arc = [(hinge[0] + r * (math.cos(a) * u[0] + math.sin(a) * v[0]),
                    hinge[1] + r * (math.cos(a) * u[1] + math.sin(a) * v[1]))
                   for a in [k * math.pi / 2 / 12 for k in range(13)]]
            items.append(DI.DebugItem(page(arc), method, conf, closed=False, width=1))
    for sep in ex.separators:
        if sep.line:
            items.append(DI.DebugItem(page(list(sep.line)), "derived", 1.0, label=sep.element_id or "sep",
                                      colour=DI.SEPARATOR_COLOUR, dashed=True, closed=False, width=3))
    for piece in ex.furniture:
        corners = G.rotated_rectangle(piece.center, piece.size, piece.rotation_deg)
        method = piece.type_method or "none"
        items.append(DI.DebugItem(page(corners), "vector", piece.evidence.get("confidence", 0.9),
                                  label=f"{piece.element_id or '?'} {piece.type}", status=piece.status,
                                  colour=DI.TYPE_METHOD_COLOURS.get(method, DI.TYPE_METHOD_COLOURS["none"]),
                                  striped=method == "none"))
    site = building.get("site") or {}
    for w in site.get("boundary_walls", []):
        if w.get("level_id") != level_id:
            continue
        corners = G.centerline_to_rectangle(w["start"], w["end"], w["thickness"])
        items.append(DI.DebugItem(page(corners), "derived", 1.0, label=w["id"], colour=DI.SITE_COLOUR, width=1))
    for d in site.get("decor", []):
        if d.get("level_id") != level_id:
            continue
        corners = G.rotated_rectangle(d["center"], d["size"], 0.0)
        items.append(DI.DebugItem(page(corners), "derived", 1.0, label=d.get("kind", ""), colour=DI.SITE_COLOUR,
                                  width=1))
    for a in site.get("areas", []):
        if a.get("level_id") != level_id or not a.get("anchor"):
            continue
        p = G.apply_affine(to_page, a["anchor"])
        box = [p[0] - 1, p[1] - 1, p[0] + 1, p[1] + 1]
        items.append(DI.DebugItem(G.box_corners(box), "derived", 1.0, label=f"{a['id']} (site)",
                                  colour=DI.SITE_COLOUR, width=1))
    for dim in ex.report.get("dims_page") or []:
        items.append(DI.DebugItem([dim.p1, dim.p2], "vector", 1.0, label=dim.text, colour=DI.DIMENSION_COLOUR,
                                  closed=False, width=3))
    for text in ex.labels:
        items.append(DI.DebugItem(G.box_corners(text.box), "vector", 1.0, label="", width=1))
    return items


def _debug_items(work: PageWork) -> list[DI.DebugItem]:
    ex = work.extraction
    to_page = G.invert_affine(ex.transform_to_building)
    items = []
    for room in work.rooms:
        items.append(DI.DebugItem([G.apply_affine(to_page, p) for p in room["polygon"]], "derived", 1.0,
                                  label=room["id"], status=room["status"], width=1))
    for wall in ex.walls:
        corners = G.centerline_to_rectangle(wall.start, wall.end, wall.thickness)
        items.append(DI.DebugItem([G.apply_affine(to_page, c) for c in corners], "vector", wall.evidence["confidence"],
                                  label=wall.element_id or "", status=wall.status))
    for opening in ex.openings:
        items.append(DI.DebugItem(G.box_corners(opening.box), "vector", opening.evidence["confidence"],
                                  label=opening.element_id or "?", status=opening.status))
    for piece in ex.furniture:
        corners = G.rotated_rectangle(piece.center, piece.size, piece.rotation_deg)
        items.append(DI.DebugItem([G.apply_affine(to_page, c) for c in corners], "vector", piece.evidence["confidence"],
                                  label=f"{piece.element_id or '?'} {piece.type}", status=piece.status))
    for text in ex.texts:
        if text.role == "dimension":
            continue
        label = text.element_id or text.role
        items.append(DI.DebugItem(G.box_corners(text.box), "vector", 1.0, label=label, width=1))
    for dim in ex.dimensions:
        status = "unverified" if dim.conflict_id else "verified"
        label = dim.printed if not dim.conflict_id else f"{dim.printed} != {dim.measured:.2f}"
        items.append(DI.DebugItem(G.box_corners(dim.box), "vector", 1.0, label=label, status=status, width=1))
    return items


def _length(metres: Optional[float], system: Optional[str]) -> str:
    """A length in the project's system: imperial ``11' 3" (3.43 m)``, metric ``3,43 m``; ``-`` for None."""
    if metres is None:
        return "-"
    if system == "imperial":
        return f"{U.format_length(metres, 'imperial')} ({metres:.2f} m)"
    return U.format_length(metres, "metric")


def _cell(text) -> str:
    return str(text).replace("|", "/").replace("\n", " ")


def _generic_sections(b: dict, build: ProjectBuild) -> list[str]:
    """Report sections of the generic core (docs/milestone7.md §2.9)."""
    system = b["project"].get("unit_system")
    lines = ["", "## Units", ""]
    lines.append(f"Project unit system: **{system or 'metric'}**"
                 + (" (lengths in feet and inches, metres in brackets)" if system == "imperial" else ""))
    lines += ["", "| Document | Unit system | Source kind |", "|---|---|---|"]
    for doc in b["documents"]:
        lines.append(f"| {doc['file']} | {doc.get('unit_system') or '-'} | {doc.get('source_kind') or '-'} |")

    lines += ["", "## Scale", ""]
    for work in build.generic:
        ex = work.extraction
        sc = ex.scale or {}
        lines.append(f"**{work.where}**: {sc.get('metres_per_unit', 0):.6g} m/unit, method "
                     f"`{sc.get('method', '-')}`, confidence {sc.get('confidence', 0):.2f}")
        lines.append("")
        rows = ex.report.get("dimensions") or []
        if rows:
            lines += ["| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | "
                      "End marks |", "|---|---|---|---|---|---|---|"]
            for r in rows:
                off = f"{r['off_pct']:+.2f}%" if "off_pct" in r else "-"
                lines.append(f"| {_cell(r['text'])} | {_length(r['printed_m'], system)} | {r['measured_units']:.2f} | "
                             f"{_length(r.get('measured_m'), system)} | {r['ratio']:.6g} | {off} | "
                             f"{' / '.join(r['end_marks'])} ({r['how']}) |")
            lines.append("")
        labels = ex.report.get("size_labels") or []
        if labels:
            lines += ["| Room-size label | Printed | Measured (clear size) | Off | Status |", "|---|---|---|---|---|"]
            for r in labels:
                printed = f"{_length(r['width_m'], system)} x {_length(r['length_m'], system)}"
                measured = " x ".join(_length(v, system) for v in r["measured"])
                off = ", ".join(f"{v:+.1f}%" for v in r.get("off_pct", [])) or "-"
                lines.append(f"| {_cell(r['name'])} ({_cell(r['text'])}) | {printed} | {measured} | {off} | "
                             f"{r['status']} |")
            lines.append("")
        lines += [f"- {_cell(reason)}" for reason in ex.report.get("scale_reasons") or []]
        lines.append("")

    rooms = [r for r in b["rooms"] if r.get("label_size")]
    lines += ["## Room size labels", ""]
    if rooms:
        lines += ["| Room | Label size | Measured | Status |", "|---|---|---|---|"]
        for r in rooms:
            ls = r["label_size"]
            measured = " x ".join(_length(v, system) for v in ls.get("measured") or []) or "-"
            lines.append(f"| {r['id']} | {_cell(ls['text'])} | {measured} | {ls['status']} |")
    else:
        lines.append("None.")

    site = b.get("site") or {}
    lines += ["", "## Site", "", "Recorded, not built."]
    if any(site.get(k) for k in ("boundary_walls", "areas", "decor", "openings")):
        lines += ["", "| Id | What | Detail |", "|---|---|---|"]
        for w in site.get("boundary_walls", []):
            length = G.distance(w["start"], w["end"])
            lines.append(f"| {w['id']} | boundary wall ({w['kind']}) | {_length(length, system)} long, "
                         f"{_length(w['thickness'], system)} thick |")
        for a in site.get("areas", []):
            ls = a.get("label_size") or {}
            measured = " x ".join(_length(v, system) for v in ls.get("measured") or []) or "-"
            detail = f"label size {ls.get('text') or '-'}, measured {measured} ({ls.get('status', '-')})"
            if a.get("polygon") is None:
                detail += ", no closed outline"
            lines.append(f"| {a['id']} | area '{_cell(a['label'])}' | {detail} |")
        for d in site.get("decor", []):
            lines.append(f"| {d['id']} | decor ({d['kind']}) | {' x '.join(_length(v, system) for v in d['size'])} |")
        for o in site.get("openings", []):
            lines.append(f"| {o['id']} | {o['type']} in {o.get('boundary_wall_id') or '-'} | "
                         f"{_length(o['width'], system)} wide |")
    else:
        lines += ["", "None."]

    lines += ["", "## Separators", ""]
    seps = [(work, e) for work in build.generic for e in work.extraction.report.get("separators") or []]
    if seps:
        lines += ["| Page | Kind | Length | Kept | Reason |", "|---|---|---|---|---|"]
        for work, e in seps:
            lines.append(f"| {work.where} | {e.get('kind', '-')} | {_length(e.get('length'), system)} | "
                         f"{'yes' if e.get('kept') else 'no'} | {_cell(e.get('reason', '-'))} |")
    else:
        lines.append("None considered.")

    lines += ["", "## Gaps", ""]
    gaps = [(work, e) for work in build.generic for e in work.extraction.report.get("gaps") or []
            if e.get("kind") != "free_end"]
    if gaps:
        lines += ["| Page | Kind | Class | Width | Owned strokes |", "|---|---|---|---|---|"]
        for work, e in gaps:
            owned = e.get("owned") or []
            owned_text = ", ".join(owned[:6]) + (f" (+{len(owned) - 6})" if len(owned) > 6 else "") if owned else "-"
            cls = e.get("class", "-")
            lines.append(f"| {work.where} | {e.get('kind')} | {cls} | {_length(e.get('width'), system)} | "
                         f"{_cell(owned_text)} |")
    else:
        lines.append("None.")

    lines += ["", "## Furniture typing", ""]
    typed = [f for f in b["furniture"] if f.get("type_method")]
    if typed:
        lines += ["| Piece | Type | Method | Candidates | Build | Status |", "|---|---|---|---|---|---|"]
        for f in typed:
            cands = "; ".join(f"pass {c.get('pass')}: {c.get('type')}" for c in f.get("type_candidates") or []) or "-"
            notes = [e.get("note") for e in f["evidence"] if e.get("note")]
            method = f["type_method"] + (f" ({_cell(notes[0])})" if notes else "")
            lines.append(f"| {f['id']} | {f['type']} | {method} | {_cell(cands)} | "
                         f"{'yes' if f.get('build', True) else 'no (drawn symbol, not built)'} | {f['status']} |")
        if build.questions:
            lines += ["", f"Recognition questions: {len(build.questions)} (`recognition/requests.json`), "
                          f"{len(build.pending)} without a complete pair of answers."]
    else:
        lines.append("None.")

    lines += ["", "## Assumed values", ""]
    assumed = []
    for lv in b["levels"]:
        if lv.get("label_source") == "assumed":
            assumed.append(f"{lv['id']}: level '{lv['label']}' assumed (no level title on the page)")
        assumed.append(f"{lv['id']}: ceiling height {lv['ceiling_height']:.2f} m ({lv['ceiling_height_source']})")
    for o in b["openings"]:
        for key in o.get("assumed") or []:
            value = o.get(key)
            assumed.append(f"{o['id']} ({o['type']}): {key.replace('_', ' ')} "
                           f"{_length(value, system) if value is not None else '-'}")
    for f in b["furniture"]:
        stair = f.get("stair")
        if stair:
            what = [k[:-len("_assumed")] for k in ("direction_assumed", "turn_assumed", "void_assumed") if stair.get(k)]
            if what:
                assumed.append(f"{f['id']} (stair): {', '.join(what)} assumed"
                               + (f" ({_cell(stair['reason'])})" if stair.get("reason") else ""))
    lines += [f"- {a}" for a in assumed] or ["None."]
    return lines


def write_report(building: dict, out_path: Path, review_reasons: list[str],
                 build: Optional[ProjectBuild] = None) -> Path:
    b = building
    lines = [f"# Ingest report: {b['project']['id']}", ""]
    lines.append(f"Status: **{b['status']}**" + (f" ({'; '.join(review_reasons)})" if review_reasons else ""))
    lines.append(f"Source: `{b['project']['source_folder']}`, pipeline commit `{b['project']['pipeline_commit']}`, "
                 f"created {b['project']['created_utc']}")
    lines += ["", "## Documents", "", "| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |",
              "|---|---|---|---|---|---|---|---|---|"]
    for doc in b["documents"]:
        for page in doc["pages"]:
            scale = page["scale"]
            scale_text = f"{scale['metres_per_unit']:.6g} m/unit ({scale['method']})" if scale else "-"
            lines.append(f"| {doc['file']} | {page['page']} | {page['class']} | {page['kind']} | {page['level_id'] or '-'} | "
                         f"{scale_text} | {page['confidence']:.2f} | {page['skip_reason'] or '-'} | {page['debug_image'] or '-'} |")
    lines += ["", "## Levels", "", "| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |",
              "|---|---|---|---|---|---|---|---|---|"]
    for lv in b["levels"]:
        lid = lv["id"]
        counts = [sum(1 for x in b[key] if x["level_id"] == lid) for key in ("walls", "openings", "rooms", "furniture")]
        label = lv["label"] + (" (assumed)" if lv.get("label_source") == "assumed" else "")
        lines.append(f"| {lid} | {label} | {lv['order']} | {lv['elevation']:.2f} | {lv['ceiling_height']:.2f} "
                     f"({lv['ceiling_height_source']}) | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |")
    lines += ["", "## Rooms", "", "| Room | Level | Label | As drawn | Type | Area computed | Area label | "
              "Furniture in documents | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for r in b["rooms"]:
        area_label = format_m2(r["area_label"]) if r["area_label"] is not None else "-"
        drawn = _cell(r["label_raw"]) if r["label_raw"] else "—"
        lines.append(f"| {r['id']} | {r['level_id']} | {r['label']} | {drawn} | "
                     f"{r['room_type']} | {format_m2(r['area_computed'])} | {area_label} | "
                     f"{'yes' if r['has_documented_furniture'] else 'no'} | {r['status']} |")
    lines += ["", "## Furniture", "", "| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for f in b["furniture"]:
        fp = f["footprint"]
        lines.append(f"| {f['id']} | {f['level_id']} | {f['room_id'] or '-'} | {f['type']} | {f['type_raw'] or '-'} | {f['source']} | "
                     f"{fp['size'][0]:.2f} x {fp['size'][1]:.2f} | {fp['rotation_deg']:.0f} | {f['status']} | {f['evidence'][0]['file']} |")
    if build is not None and build.generic:
        lines += _generic_sections(b, build)
    lines += ["", "## Conflicts", ""]
    if b["conflicts"]:
        lines += ["| Id | Kind | Elements | Description | Resolution |", "|---|---|---|---|---|"]
        for c in b["conflicts"]:
            lines.append(f"| {c['id']} | {c['kind']} | {', '.join(c['element_ids'])} | {_cell(c['description'])} | "
                         f"{_cell(c['resolution'])} |")
    else:
        lines.append("None.")
    lines += ["", "## Unverified", ""]
    lines += [f"- {x}" for x in b["unverified"]] or ["None."]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in b["warnings"]] or ["None."]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def _extract_generic(record: PageRecord, out_dir: Path, answers, no_ai: bool) -> LevelExtraction:
    """A page for the generic core: the page the classifier already read, else read now by its adapter."""
    from wenart.ingest.generic import core

    page = record.generic_page
    if page is None:
        if record.format == "pdf":
            from wenart.ingest import cad_pdf
            page = cad_pdf.read_page(record.source_path, record.page, record.file)
        else:
            from wenart.ingest import dxf_generic
            page = dxf_generic.read_page(record.source_path, record.file)
    record.generic_page = None                   # the page model is large; the extraction keeps what is needed
    return core.extract(page, record.level_id, record.file, answers=answers, no_ai=no_ai,
                        rec_dir=out_dir / RECOGNITION_DIR)


def _evidence_only_pages(records: list[PageRecord]) -> set[tuple]:
    """(file, page) of the raster pages that are evidence only: a level's best page (``page_rank``: DWG/DXF > vector
    PDF > scan > photo) is its master; every other raster page of that level only adds evidence (§0, §4.4)."""
    by_level: dict[str, list[PageRecord]] = {}
    for r in records:
        if r.is_extractable() and r.level_id is not None and not r.level_problem:
            by_level.setdefault(r.level_id, []).append(r)
    out = set()
    for recs in by_level.values():
        recs = sorted(recs, key=page_rank)
        for r in recs[1:]:
            if r.kind in RASTER_KINDS:
                out.add((r.file, r.page))
    return out


def _extract_raster(record: PageRecord, out_dir: Path, answers, no_ai: bool, evidence_only: bool) -> LevelExtraction:
    """A raster page: the adapter's page (read while classifying, else now) -> the generic core. The rectified image
    goes to ``<out>/rectified/<file>_p<n>.png`` (§4.1). An evidence-only page asks no questions and waits for no
    answers."""
    import cv2

    from wenart.ingest import raster as RA
    from wenart.ingest.generic import core

    rp = record.raster_page or RA.read_page(record.source_path, record.page, record.file, record.kind)
    record.raster_page = None
    rect_path = out_dir / RECTIFIED_DIR / f"{B.slugify(record.file)}_p{record.page}.png"
    rect_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(rect_path), rp.image, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    ex = core.extract(rp.page, record.level_id, record.file, answers=None if evidence_only else answers,
                      no_ai=no_ai or evidence_only, rec_dir=None if evidence_only else out_dir / RECOGNITION_DIR,
                      raster=rp, evidence_only=evidence_only)
    ex.report["raster_page"] = rp
    ex.report["rectified_image"] = rect_path.relative_to(out_dir).as_posix()
    ex.report["to_original"] = [[round(v, 9) for v in row] for row in rp.page.to_original]
    return ex


def _mark_unverified(ex: LevelExtraction) -> None:
    for item in list(ex.walls) + list(ex.openings) + list(ex.separators) + list(ex.furniture):
        item.status = "unverified"


def _asked_before(answers) -> Optional[set]:
    """``{(key, input_sha256)}`` of the requests the answers in ``answers`` (a recognition folder) were given for,
    read before this run rewrites them; None without such a folder or file."""
    from wenart.recognition import answers as A

    if not isinstance(answers, (str, Path)):
        return None
    doc = A.read_requests(Path(answers))
    if not doc:
        return None
    return {(it.get("key"), it.get("input_sha256")) for it in doc.get("items") or []}


def _write_questions(build: ProjectBuild, out_dir: Path, asked: Optional[set] = None) -> None:
    """``<out>/recognition/requests.json`` with the questions of the pages whose furniture is in the building
    (§1.4); an earlier file is rewritten (empty when nothing is asked) so it never lists stale questions.

    ``asked``: the (key, input hash) pairs of the requests the given answers belong to (``_asked_before``). §1.4 has
    one round of questions: a question this run asks that was not in that round (a raster page whose accepted
    labels changed what it asks) cannot have answers, so it is not pending (the run never exits 4 for it); it is
    written to the requests, its piece stays ``unknown``/``unverified`` and a warning lists it."""
    from wenart.recognition import answers as A

    items, pending = [], []
    for ex in [w.extraction for w in build.furniture_works] + build.question_only:
        items.extend(ex.report.get("questions") or [])
        pending.extend(ex.report.get("pending") or [])
    if asked is not None and pending:
        hashes = {it["key"]: it.get("input_sha256") for it in items}
        late = [k for k in pending if (k, hashes.get(k)) not in asked]
        if late:
            pending = [k for k in pending if k not in late]
            build.warn(f"{len(late)} recognition questions were not in the round the answers belong to "
                       f"({', '.join(late)}): not answered, they stay unknown / unverified (one round of questions, "
                       f"§1.4)")
    build.questions, build.pending = items, pending
    rec_dir = out_dir / RECOGNITION_DIR
    if items or (rec_dir / A.REQUESTS_NAME).is_file():
        A.write_requests(rec_dir, build.building["project"]["id"], items)


def run_project(project_dir: str | Path, out_dir: str | Path, ocr: Optional[Callable] = None, answers=None,
                no_ai: bool = False) -> tuple[dict, ProjectBuild]:
    """Run the vector path on a project folder; writes building.json, report.md, debug images and (for generic
    pages with AI candidates) ``recognition/requests.json`` with the crops. Returns the building and the build
    state (questions, pending answers, review reasons)."""
    project_dir = Path(project_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = None
    brief_path = project_dir / "brief.yaml"
    if brief_path.is_file():
        brief = yaml.safe_load(brief_path.read_text(encoding="utf-8")) or {}
    building = B.empty_building(project_dir.name, project_dir.as_posix(), pipeline_commit(), brief=brief)
    build = ProjectBuild(building)
    asked = _asked_before(answers)              # read before this run rewrites requests.json

    records = classify_pages(project_dir, work_dir=out_dir / "converted", ocr=ocr)
    evidence_only = _evidence_only_pages(records)
    works: dict[tuple, PageWork] = {}
    by_level: dict[str, list[PageWork]] = {}
    for record in records:
        if record.skip_reason and record.format == "dwg":
            if record.skip_reason == SAME_STEM_REASON:
                build.warn(f"{record.file}: {record.skip_reason}")
            else:
                build.review(f"{record.file}: {record.skip_reason}")
            continue
        if record.kind in RASTER_KINDS and record.extractor == "raster" and not record.is_extractable():
            reason = f"{record.file} p{record.page}: {record.kind} page skipped ({record.skip_reason})"
            # A photo without a page quadrilateral needs review unless another page draws the project (§4.1).
            if record.kind == "photo" and record.skip_reason and "quadrilateral" in record.skip_reason \
                    and not any(r.is_extractable() for r in records):
                build.review(reason)
            else:
                build.warn(reason)
            continue
        if record.kind != "vector" and record.extractor != "raster":
            build.warn(f"{record.file} p{record.page}: {record.kind} page skipped ({record.skip_reason})")
            continue
        if record.skip_reason == SHX_TEXT_REASON:
            build.review(f"{record.file} p{record.page}: {record.skip_reason}")
            continue
        if record.page_class not in ("floor_plan", "furniture_plan"):
            build.warn(f"{record.file} p{record.page}: class {record.page_class} not used by the vector path"
                       + (f" ({record.skip_reason})" if record.skip_reason else ""))
            continue
        if record.level_problem:
            build.review(f"{record.file} p{record.page}: {record.level_problem}")
            continue
        if record.level_id is None:
            build.review(f"{record.file} p{record.page}: {record.page_class} without a level title "
                         f"(found: {record.level_label_raw!r})")
            continue
        if record.label_source == "assumed":
            build.warn(f"level title missing: assumed {record.level_id} {record.level_label}")
        secondary = (record.file, record.page) in evidence_only
        if record.extractor == "raster":
            extraction = _extract_raster(record, out_dir, answers, no_ai, secondary)
            extraction.level_assumed = record.label_source == "assumed"
        elif record.extractor == "generic":
            extraction = _extract_generic(record, out_dir, answers, no_ai)
            extraction.level_assumed = record.label_source == "assumed"
        elif record.format in ("dxf", "dwg"):
            extraction = extract_dxf(record.source_path, record.level_id, record.file)
        else:
            extraction = extract_pdf_page(record.source_path, record.page, record.level_id, record.file)
        audit = (record.conversion or {}).get("audit") or {}
        if audit.get("errors"):
            _mark_unverified(extraction)
            build.warn(f"{record.file}: the converted DXF has {audit['errors']} audit errors; its elements are "
                       f"unverified")
        for text in extraction.warnings:
            build.warn(f"{text} (evidence-only page)" if secondary else text)
        if secondary:
            # An evidence-only raster page never stops the project and adds no conflicts of its own: what it cannot
            # show, or disagrees with, is a warning (§0); its counts are compared with the master's later.
            for reason in extraction.review:
                build.warn(f"evidence-only page not used: {reason}")
            for conflict in extraction.conflicts:
                build.warn(f"{conflict['description']} (evidence-only page, {conflict['kind']}: not a conflict of "
                           f"the building)")
            extraction.conflicts = []
            if extraction.scale is None or extraction.transform_to_building is None:
                build.warn(f"{record.file} p{record.page}: evidence-only raster page has no scale; not used")
                continue
        else:
            for reason in extraction.review:
                build.review(reason)
            if extraction.report.get("questions") and (extraction.scale is None or
                                                        extraction.transform_to_building is None):
                build.question_only.append(extraction)
                if extraction.report.get("review_awaits_answers"):
                    build.review_after_answers.extend(extraction.review)
        for conflict in extraction.conflicts:
            build.conflict(conflict["kind"], conflict["element_ids"], conflict["description"], conflict["resolution"])
        if extraction.scale is None or extraction.transform_to_building is None:
            if not extraction.review:
                build.review(f"{record.file} p{record.page}: no scale source")
            continue
        work = PageWork(record=record, extraction=extraction)
        works[(record.file, record.page)] = work
        by_level.setdefault(record.level_id, []).append(work)
        if extraction.source_kind is not None:
            build.generic.append(work)

    if not by_level:
        build.review(NO_PLAN_REASON)

    def level_order(level_id: str) -> int:
        rec = by_level[level_id][0].record
        return rec.level_order if rec.level_order is not None else 0

    for level_id in sorted(by_level, key=level_order):
        _assemble_level(build, level_id, by_level[level_id])
        level_rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
        for work in by_level[level_id]:
            work.rooms = level_rooms
    _check_outlines(build)
    masters = [sorted(ws, key=lambda w: w.rank)[0] for ws in by_level.values()]
    if any(w.extraction.source_kind is not None for w in masters):
        # The generic core's unit system; an evidence-only raster page beside a DXF/PDF level does not count.
        systems = [w.extraction.units_system or "metric" for w in masters]
        building["project"]["unit_system"] = "imperial" if systems.count("imperial") > systems.count("metric") \
            else "metric"
    _write_questions(build, out_dir, asked)

    # Conflicts: stable order and ids.
    build.raw_conflicts.sort(key=lambda c: CONFLICT_ORDER.index(c["kind"]) if c["kind"] in CONFLICT_ORDER else 99)
    for entry in build.raw_conflicts:
        building["conflicts"].append({"id": build.ids.next("conflict"), **entry})
    for key in ("walls", "openings", "rooms", "furniture"):
        building["unverified"].extend(x["id"] for x in building[key] if x["status"] == "unverified")
    if build.review_reasons:
        building["status"] = "needs_review"

    building["documents"] = _documents(records, works, out_dir, project_dir, build)
    errors = B.validation_errors(building)
    if errors:
        building["status"] = "needs_review"
        build.review_reasons.append("building JSON failed schema validation")
        building["warnings"].extend(f"schema: {e}" for e in errors[:20])
    B.save(building, out_dir / "building.json", check=False)
    write_report(building, out_dir / "report.md", build.review_reasons, build)
    return building, build


def build_project(project_dir: str | Path, out_dir: str | Path, ocr: Optional[Callable] = None, answers=None,
                  no_ai: bool = False) -> dict:
    """Run the vector path on a project folder; writes building.json, report.md and debug images."""
    return run_project(project_dir, out_dir, ocr=ocr, answers=answers, no_ai=no_ai)[0]


def exit_code(building: dict, build: ProjectBuild, no_ai: bool = False) -> int:
    """0 ok, 1 needs_review, 4 = questions written and answers missing (never with ``--no-ai``) (§1.4).

    ``needs_review`` wins over pending questions: a project that stops for review gets no GPU time for its
    furniture questions (AI typing never causes a review)."""
    if building["status"] != "ok":
        # A raster page whose scale waits for its room-size label answers (§3.4) is not finished yet: when every
        # review reason is of that kind, the questions go to the GPU stage first.
        after = list(getattr(build, "review_after_answers", None) or [])
        waiting = build.pending and not no_ai and after
        if waiting and all(r in after or r == NO_PLAN_REASON for r in getattr(build, "review_reasons", [])):
            return EXIT_QUESTIONS
        return EXIT_REVIEW
    return EXIT_QUESTIONS if build.pending and not no_ai else EXIT_OK


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Vector path: project folder -> building.json")
    parser.add_argument("project_dir")
    parser.add_argument("--out", default=None, help="output folder (default: outputs/<project name>)")
    parser.add_argument("--answers", default=None,
                        help="recognition folder with the answers of an earlier run (<out>/recognition)")
    parser.add_argument("--no-ai", action="store_true",
                        help="do not wait for AI answers: unanswered candidates stay unknown / unverified")
    args = parser.parse_args(argv)
    project_dir = Path(args.project_dir)
    out_dir = Path(args.out) if args.out else Path("outputs") / project_dir.name
    building, build = run_project(project_dir, out_dir, answers=Path(args.answers) if args.answers else None,
                                  no_ai=args.no_ai)
    code = exit_code(building, build, args.no_ai)
    asked = f", {len(build.questions)} questions ({len(build.pending)} unanswered)" if build.questions else ""
    print(f"{building['project']['id']}: status {building['status']}, {len(building['levels'])} levels, "
          f"{len(building['walls'])} walls, {len(building['openings'])} openings, {len(building['rooms'])} rooms, "
          f"{len(building['furniture'])} furniture, {len(building['conflicts'])} conflicts, "
          f"{len(building['unverified'])} unverified{asked} -> {out_dir / 'building.json'}")
    if code == EXIT_QUESTIONS:
        print(f"questions written to {out_dir / RECOGNITION_DIR / 'requests.json'}; answers missing (exit 4)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
