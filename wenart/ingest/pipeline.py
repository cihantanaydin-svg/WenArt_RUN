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

CLI: ``python -m wenart.ingest.pipeline projects/synthetic-01 --out outputs/synthetic-01``
(exit code 1 when the status is ``needs_review``).
"""
from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import yaml
from shapely.geometry import Polygon

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import debug_image as DI
from wenart.ingest import rooms as R
from wenart.ingest.classify import PageRecord, classify_pages
from wenart.ingest.dxf_extract import extract_dxf
from wenart.ingest.model import DimensionItem, FurnitureItem, LevelExtraction, OpeningItem, WallItem
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
SOURCE_RANK = {"dwg": 0, "dxf": 0, "pdf": 1}
CLASS_RANK = {"floor_plan": 0, "furniture_plan": 1}
CONFLICT_ORDER = ["area_label_vs_computed", "dimension_vs_measured", "count_mismatch", "outline_mismatch",
                  "scale_disagreement", "type_disagreement", "other"]
SOURCE_NAME = {"dwg": "DWG", "dxf": "DXF", "pdf": "vector PDF"}


@dataclass
class PageWork:
    """One extracted page with its classification."""
    record: PageRecord
    extraction: LevelExtraction
    rooms: list = field(default_factory=list)   # rooms of the page's level, once assembled

    @property
    def rank(self) -> tuple:
        return (SOURCE_RANK.get(self.record.format, 9), CLASS_RANK.get(self.record.page_class, 9),
                self.record.file, self.record.page)

    @property
    def where(self) -> str:
        return self.record.file if self.record.format != "pdf" else f"{self.record.file} p{self.record.page}"


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
    return {"id": opening_id, "type": opening.kind, "level_id": level_id, "wall_id": wall["id"] if wall else "",
            "center": list(opening.center), "width": opening.width, "height": None, "sill_height": None,
            "swing_side": swing_side, "status": status, "evidence": [opening.evidence]}


def _furniture_dict(level_id: str, piece: FurnitureItem, piece_id: str, rooms: list[dict], build: ProjectBuild) -> dict:
    piece.element_id = piece_id
    status = piece.status
    room = R.room_containing(rooms, piece.center)
    if room is None:
        status = "unverified"
        build.warn(f"{piece_id}: centre {piece.center} lies in no room of {level_id}")
    else:
        room["has_documented_furniture"] = True
    return {"id": piece_id, "level_id": level_id, "room_id": room["id"] if room else None, "type": piece.type,
            "type_raw": piece.type_raw, "source": "from_documents",
            "footprint": {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg},
            "front_deg": piece.front_deg, "height": None, "asset": None, "status": status, "evidence": [piece.evidence]}


def _assemble_level(build: ProjectBuild, level_id: str, works: list[PageWork]) -> None:
    """Master page -> walls, rooms, openings, furniture; other pages -> evidence and count checks."""
    bld = build.building
    works = sorted(works, key=lambda w: w.rank)
    master = works[0]
    ex = master.extraction
    record = master.record
    label, order = record.level_label, record.level_order
    if label is None:
        normalised = B.normalise_level_label(record.level_label_raw or "")
        label, order = normalised if normalised else (level_id, 0)
    bld["levels"].append({
        "id": level_id, "label": label, "order": order, "elevation": round(order * LEVEL_PITCH, 3),
        "ceiling_height": DEFAULT_CEILING_HEIGHT, "ceiling_height_source": "assumed_default",
        "evidence": [e for w in works for e in w.record.evidence],
    })
    build.warn(f"Level {level_id}: ceiling height assumed {DEFAULT_CEILING_HEIGHT:.2f} m (no section drawing found)")

    # Rooms need the walls first (exterior flags come from the union).
    anchors = [_to_building(ex, t.start) for t in ex.labels]
    fallbacks = [_to_building(ex, G.box_center(t.box)) for t in ex.labels]
    result = R.derive_rooms(level_id, ex.walls, ex.labels, anchors, fallbacks, ex.file, build.ids)
    for text in result.warnings:
        build.warn(text)
    if not result.closed:
        build.review(f"{level_id}: outer walls do not form a closed loop ({master.where})")
    if result.unplaced_labels:
        # A room label outside every face means the walls around that room do not close.
        names = ", ".join(f"'{t.text}'" for t in result.unplaced_labels)
        build.review(f"{level_id}: room labels outside every enclosed room ({names}); walls do not close ({master.where})")
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
    bld["rooms"].extend(rooms)

    openings = []
    for opening in ex.openings:
        opening_id = build.ids.next(opening.kind, level_id)
        openings.append(_opening_dict(level_id, opening, opening_id, walls, rooms, build))
    bld["openings"].extend(openings)

    furniture = []
    for piece in ex.furniture:
        furniture.append(_furniture_dict(level_id, piece, build.ids.next("furniture", level_id), rooms, build))
    bld["furniture"].extend(furniture)

    for work in works[1:]:
        _merge_secondary(build, level_id, label, master, work, walls, openings, furniture, rooms)

    for work in works:
        _check_dimensions(build, work, walls)
    _check_areas(build, rooms, master)


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
    master_name, sec_name = SOURCE_NAME.get(master.record.format, "document"), SOURCE_NAME.get(work.record.format, "document")

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
        return _furniture_dict(level_id, item, element_id, rooms, build)

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
        label, _, _ = B.normalise_room_label(text.text)
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


def _check_dimensions(build: ProjectBuild, work: PageWork, walls: list[dict]) -> None:
    ex = work.extraction
    source = SOURCE_NAME.get(work.record.format, "document")
    for dim in ex.dimensions:
        dim.wall_ids = _link_dimension_walls(dim, walls)
        if dim.printed_value is None or dim.measured <= 0:
            continue
        diff = abs(dim.printed_value - dim.measured)
        if diff <= PRINT_EPS or diff / dim.measured <= DIMENSION_TOL:
            continue
        pct = diff / dim.measured * 100.0
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

def _documents(records: list[PageRecord], works: dict, out_dir: Path, project_dir: Path, build: ProjectBuild) -> list[dict]:
    docs: dict[str, dict] = {}
    for record in records:
        doc = docs.setdefault(record.file, {"id": "doc_" + B.slugify(record.file), "file": record.file,
                                            "format": record.format, "converter": record.converter, "pages": []})
        entry = record.to_json()
        work = works.get((record.file, record.page))
        if work is not None:
            entry["scale"] = work.extraction.scale
            entry["transform_to_building"] = work.extraction.transform_to_building
        debug_path = _debug_image(record, work, out_dir, project_dir, build)
        entry["debug_image"] = debug_path.relative_to(out_dir).as_posix() if debug_path else None
        doc["pages"].append(entry)
    return list(docs.values())


def _debug_image(record: PageRecord, work: Optional[PageWork], out_dir: Path, project_dir: Path,
                 build: ProjectBuild) -> Optional[Path]:
    out_path = out_dir / "debug" / f"{B.slugify(record.file)}_p{record.page}.png"
    source = Path(record.source_path) if record.source_path else project_dir / record.file
    try:
        if record.format == "pdf":
            raster = DI.raster_from_pdf(source, record.page)
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
    else:
        items = _debug_items(work)
    DI.write_debug_image(raster, items, out_path, note=DI.legend_note(note))
    return out_path


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


def write_report(building: dict, out_path: Path, review_reasons: list[str]) -> Path:
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
        lines.append(f"| {lid} | {lv['label']} | {lv['order']} | {lv['elevation']:.2f} | {lv['ceiling_height']:.2f} "
                     f"({lv['ceiling_height_source']}) | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |")
    lines += ["", "## Rooms", "", "| Room | Level | Label | Type | Area computed | Area label | Furniture in documents | Status |",
              "|---|---|---|---|---|---|---|---|"]
    for r in b["rooms"]:
        area_label = format_m2(r["area_label"]) if r["area_label"] is not None else "-"
        lines.append(f"| {r['id']} | {r['level_id']} | {r['label']} | {r['room_type']} | {format_m2(r['area_computed'])} | "
                     f"{area_label} | {'yes' if r['has_documented_furniture'] else 'no'} | {r['status']} |")
    lines += ["", "## Furniture", "", "| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for f in b["furniture"]:
        fp = f["footprint"]
        lines.append(f"| {f['id']} | {f['level_id']} | {f['room_id'] or '-'} | {f['type']} | {f['type_raw'] or '-'} | {f['source']} | "
                     f"{fp['size'][0]:.2f} x {fp['size'][1]:.2f} | {fp['rotation_deg']:.0f} | {f['status']} | {f['evidence'][0]['file']} |")
    lines += ["", "## Conflicts", ""]
    if b["conflicts"]:
        lines += ["| Id | Kind | Elements | Description | Resolution |", "|---|---|---|---|---|"]
        for c in b["conflicts"]:
            lines.append(f"| {c['id']} | {c['kind']} | {', '.join(c['element_ids'])} | {c['description']} | {c['resolution']} |")
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

def build_project(project_dir: str | Path, out_dir: str | Path, ocr: Optional[Callable] = None) -> dict:
    """Run the vector path on a project folder; writes building.json, report.md and debug images."""
    project_dir = Path(project_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    brief = None
    brief_path = project_dir / "brief.yaml"
    if brief_path.is_file():
        brief = yaml.safe_load(brief_path.read_text(encoding="utf-8")) or {}
    building = B.empty_building(project_dir.name, project_dir.as_posix(), pipeline_commit(), brief=brief)
    build = ProjectBuild(building)

    records = classify_pages(project_dir, work_dir=out_dir / "converted", ocr=ocr)
    works: dict[tuple, PageWork] = {}
    by_level: dict[str, list[PageWork]] = {}
    for record in records:
        if record.skip_reason and record.format == "dwg":
            build.review(f"{record.file}: {record.skip_reason}")
            continue
        if record.kind != "vector":
            build.warn(f"{record.file} p{record.page}: {record.kind} page skipped ({record.skip_reason})")
            continue
        if record.page_class not in ("floor_plan", "furniture_plan"):
            build.warn(f"{record.file} p{record.page}: class {record.page_class} not used by the vector path"
                       + (f" ({record.skip_reason})" if record.skip_reason else ""))
            continue
        if record.level_id is None:
            build.review(f"{record.file} p{record.page}: {record.page_class} without a level title "
                         f"(found: {record.level_label_raw!r})")
            continue
        if record.format in ("dxf", "dwg"):
            extraction = extract_dxf(record.source_path, record.level_id, record.file)
        else:
            extraction = extract_pdf_page(record.source_path, record.page, record.level_id, record.file)
        for text in extraction.warnings:
            build.warn(text)
        for conflict in extraction.conflicts:
            build.conflict(conflict["kind"], conflict["element_ids"], conflict["description"], conflict["resolution"])
        if extraction.scale is None or extraction.transform_to_building is None:
            build.review(f"{record.file} p{record.page}: no scale source")
            continue
        work = PageWork(record=record, extraction=extraction)
        works[(record.file, record.page)] = work
        by_level.setdefault(record.level_id, []).append(work)

    if not by_level:
        build.review("no vector floor plan page could be used (raster pages need the recognition path)")

    def level_order(level_id: str) -> int:
        rec = by_level[level_id][0].record
        return rec.level_order if rec.level_order is not None else 0

    for level_id in sorted(by_level, key=level_order):
        _assemble_level(build, level_id, by_level[level_id])
        level_rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
        for work in by_level[level_id]:
            work.rooms = level_rooms
    _check_outlines(build)

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
    write_report(building, out_dir / "report.md", build.review_reasons)
    return building


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Vector path: project folder -> building.json")
    parser.add_argument("project_dir")
    parser.add_argument("--out", default=None, help="output folder (default: outputs/<project name>)")
    args = parser.parse_args(argv)
    project_dir = Path(args.project_dir)
    out_dir = Path(args.out) if args.out else Path("outputs") / project_dir.name
    building = build_project(project_dir, out_dir)
    print(f"{building['project']['id']}: status {building['status']}, {len(building['levels'])} levels, "
          f"{len(building['walls'])} walls, {len(building['openings'])} openings, {len(building['rooms'])} rooms, "
          f"{len(building['furniture'])} furniture, {len(building['conflicts'])} conflicts, "
          f"{len(building['unverified'])} unverified -> {out_dir / 'building.json'}")
    return 0 if building["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
