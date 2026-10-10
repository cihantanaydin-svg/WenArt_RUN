"""Rooms from walls: shapely union of the wall rectangles -> interior faces.

Each interior ring of the union is a room polygon. A room label (TEXT inside
the face) names it; the label's area suffix becomes ``area_label``. Faces
without a label, with several labels, or labels outside every face are
reported, never fixed silently. The exterior ring tells which walls are
exterior and whether the outer walls close; if they do not, the pipeline
stops the project with ``needs_review``.

Closure check: the union must be one polygon with at least one hole, and no
wall may end in the open. A wall end (the short side of its rectangle) that
lies on the exterior ring but is touched by no other wall is a loose end:
when an outer wall segment is missing, the neighbouring walls end exactly
there, while the remaining enclosed rooms still show up as holes (so the
ring count alone would say "closed"). Free-standing partitions inside a room
end on an interior ring, not the exterior one, and are not loose ends.

Coordinates are snapped to 1 mm and the union is closed by a 2 mm
morphological pass so that sub-millimetre gaps between touching rectangles
(PDF coordinate rounding) do not merge two rooms.

Generic core pages (docs/milestone7.md §2.7) pass more: ``union`` is the
ready wall union with every opening and virtual separator bridged (the
loose-end test is not needed then: gaps are bridged by their openings),
``separators`` adds separator lines to the plain wall union otherwise (pass
them with a ready ``union`` too: the faces are snapped onto them), and
labels that carry a ``block`` (``generic.labels.LabelBlock``) are named,
typed and size-checked from it: Turkish or plain casing by the page
language, the room type from the name and the face (``hall`` alone becomes
``living`` in a large, compact face), the printed size against the face's
clear size (``label_size``, §2.7.3), area labels in m² or sq ft. A face
named only by exterior labels (Parking, Garden) is no room (``site`` holds
it); an unlabelled face gets ``unlabelled_label`` (``Oda`` / ``Room``),
``label_raw`` None, a type from ``face_type`` (``hall`` or ``unknown``) and
is always ``unverified``. A face holding several room names keeps the
first, is ``unverified`` and is listed in ``multi_labels`` (the pipeline
makes it a conflict). A generic label outside the building outline is a
warning (``topology.split_plot`` reports it), not a sign of open walls.

Virtual separators split a face as a strip 4 mm wide (``topology.
separator_polygon``); the face vertices on the strip's edges are moved back
onto the separator line, so the two rooms share the line exactly and their
floors and ceilings meet there (docs/milestone7.md §6.4; review2
dwgblender-1: the strip left a 4 mm slit through floor and ceiling).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import LineString, Point as ShapelyPoint, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.ingest.model import TextItem, WallItem

SNAP_M = 0.001          # wall corner snapping (metres)
CLOSE_M = 0.002         # gap closing radius (metres)
TOUCH_M = 0.001         # "touches" tolerance for wall <-> ring tests
END_TOUCH_M = 2 * CLOSE_M  # a wall end this close to another wall is supported, not loose

UNLABELLED_LABEL = "Oda"   # Turkish "room", used for faces with no label text


@dataclass
class RoomResult:
    rooms: list[dict] = field(default_factory=list)       # schema-shaped room dicts
    room_walls: dict = field(default_factory=dict)        # room id -> wall indices touching it
    closed: bool = True
    exterior_walls: list[int] = field(default_factory=list)
    unplaced_labels: list[TextItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    # Generic core pages: faces naming two rooms (room id, kept label, other labels) and failed size checks
    # (room id, label_size dict).
    multi_labels: list[tuple[str, str, list[str]]] = field(default_factory=list)
    label_size_conflicts: list[tuple[str, dict]] = field(default_factory=list)


def wall_polygons(walls: list[WallItem]) -> list[Polygon]:
    polys = []
    for wall in walls:
        corners = [G.snap_point(c, 3) for c in G.centerline_to_rectangle(wall.start, wall.end, wall.thickness)]
        polys.append(Polygon(corners))
    return polys


def wall_union(walls: list[WallItem]):
    """Union of all wall rectangles, with tiny gaps closed."""
    union = unary_union(wall_polygons(walls))
    if union.is_empty:
        return union
    return union.buffer(CLOSE_M, join_style="mitre").buffer(-CLOSE_M, join_style="mitre")


def _wall_end_edges(wall: WallItem) -> list[LineString]:
    """The two short sides of the wall rectangle (at ``start`` and at ``end``)."""
    c = [G.snap_point(p, 3) for p in G.centerline_to_rectangle(wall.start, wall.end, wall.thickness)]
    return [LineString([c[3], c[0]]), LineString([c[1], c[2]])]


def loose_wall_ends(walls: list[WallItem], polys: list[Polygon], exterior) -> list[tuple[int, str]]:
    """``(wall index, "start" | "end")`` for every wall end that lies on the
    exterior ring and touches no other wall: the outer loop is open there."""
    loose = []
    for i, wall in enumerate(walls):
        for which, edge in zip(("start", "end"), _wall_end_edges(wall)):
            if edge.length < 1e-9 or edge.distance(exterior) >= TOUCH_M:
                continue
            supported = any(j != i and poly.distance(edge) <= END_TOUCH_M for j, poly in enumerate(polys))
            if not supported:
                loose.append((i, which))
    return loose


def drop_inner_pieces(union):
    """The wall union without free-standing pieces that lie inside another part's filled outline (real03, 10 Oct
    2026: a 0.75 m stub inside a flat made the level "not closed"); one part left -> that Polygon."""
    if union.is_empty or union.geom_type != "MultiPolygon":
        return union
    parts = list(union.geoms)
    filled = [Polygon(p.exterior) for p in parts]
    keep = [p for k, p in enumerate(parts)
            if not any(j != k and filled[j].contains(p.representative_point()) for j in range(len(parts)))]
    return keep[0] if len(keep) == 1 else unary_union(keep)


def closure_problem(walls: list[WallItem], union=None) -> Optional[str]:
    """Why the outer walls do not form one closed loop, or None when they do."""
    if not walls:
        return "no walls"
    union = drop_inner_pieces(wall_union(walls) if union is None else union)
    if union.geom_type != "Polygon":
        parts = getattr(union, "geoms", [])
        return f"outer walls do not form one closed loop ({union.geom_type}, {len(parts)} parts)"
    if len(union.interiors) == 0:
        return "walls form no enclosed room"
    loose = loose_wall_ends(walls, wall_polygons(walls), union.exterior)
    if loose:
        where = ", ".join(f"{walls[i].entity} ({which} at {G.snap_point(getattr(walls[i], which), 3)})" for i, which in loose)
        return f"outer walls do not form a closed loop: wall ends open to the outside at {where}"
    return None


def outer_walls_closed(walls: list[WallItem]) -> bool:
    return closure_problem(walls) is None


def ring_to_polygon(ring) -> list[tuple[float, float]]:
    """Ring -> CCW vertex list without the closing point, collinear points
    removed, starting at the minimum (x, y) vertex (same convention as the truth)."""
    poly = orient(Polygon(ring), sign=1.0)
    coords = [G.snap_point(c, 4) for c in poly.exterior.coords[:-1]]
    cleaned: list[tuple[float, float]] = []
    n = len(coords)
    for i in range(n):
        prev, cur, nxt = coords[i - 1], coords[i], coords[(i + 1) % n]
        cross = (cur[0] - prev[0]) * (nxt[1] - cur[1]) - (cur[1] - prev[1]) * (nxt[0] - cur[0])
        if abs(cross) > 1e-9:
            cleaned.append(cur)
    if not cleaned:
        return coords
    start = cleaned.index(min(cleaned))
    return cleaned[start:] + cleaned[:start]


def _separator_lines(separators) -> list:
    lines = []
    for sep in separators or ():
        line = sep.line if hasattr(sep, "line") else sep
        if line:
            lines.append((tuple(line[0]), tuple(line[1])))
    return lines


def snap_to_separators(face: list[tuple[float, float]], lines: list) -> list[tuple[float, float]]:
    """``face`` (a ``ring_to_polygon`` vertex list) with every vertex that lies on the edge of a separator strip -
    within the strip half-width (2 mm) plus 0.5 mm of a separator line, along it or up to 2.5 mm past its ends -
    projected onto that line; the result is cleaned like ``ring_to_polygon``. Faces that do not touch a separator
    come back unchanged."""
    reach = CLOSE_M + 0.0005
    out = []
    moved = False
    for p in face:
        q = p
        for a, b in lines:
            length = G.distance(a, b)
            if length <= 0:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            t = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
            d = abs(-(p[0] - a[0]) * uy + (p[1] - a[1]) * ux)
            if d <= reach and -reach <= t <= length + reach:
                q = G.snap_point((a[0] + ux * t, a[1] + uy * t), 4)
                break
        moved = moved or q != p
        out.append(q)
    if not moved:
        return face
    snapped = Polygon(out)
    if not snapped.is_valid or snapped.area <= 0:
        return face
    return ring_to_polygon(snapped.exterior)


def _separator_strips(separators) -> list[Polygon]:
    from wenart.ingest.generic.topology import separator_polygon
    strips = []
    for sep in separators or ():
        line = sep.line if hasattr(sep, "line") else sep
        if line:
            strips.append(separator_polygon(line))
    return strips


def _face_size(face: Polygon) -> tuple[float, float]:
    """(area, aspect = long / short side of the minimum-area rectangle)."""
    from wenart.ingest.generic.labels import clear_size
    a, b, _ = clear_size(face)
    short = min(a, b)
    return face.area, (max(a, b) / short if short > 0 else float("inf"))


def derive_rooms(level_id: str, walls: list[WallItem], labels: list[TextItem], label_points: list[tuple[float, float]],
                 label_fallback_points: Optional[list[tuple[float, float]]] = None,
                 file_rel: str = "", ids: Optional[B.IdCounter] = None, union=None, separators=(),
                 unlabelled_label: str = UNLABELLED_LABEL, face_type=None) -> RoomResult:
    """Rooms of one level.

    ``label_points[i]`` is the anchor of ``labels[i]`` in building metres (the
    text insert point); ``label_fallback_points[i]`` (e.g. the box centre) is
    tried when the anchor is in no face. Returns schema-shaped room dicts
    (without ``has_documented_furniture`` decided: it starts ``False``).

    Generic core pages: ``union`` (the bridged wall union), ``separators``,
    ``unlabelled_label``, ``face_type(polygon) -> (room_type, reason[, label])`` (Milestone 11: a label for the
    unlabelled face, e.g. "Merdiven" for a stair core) and
    labels with a ``block`` (see the module docstring).
    """
    result = RoomResult()
    ids = ids or B.IdCounter()
    if not walls:
        result.closed = False
        result.warnings.append(f"{level_id}: no walls")
        return result
    if union is not None:
        union = drop_inner_pieces(union)
    if union is None:
        union = wall_union(walls)
        strips = _separator_strips(separators)
        if strips:
            union = unary_union([union] + strips).buffer(CLOSE_M, join_style="mitre").buffer(-CLOSE_M,
                                                                                            join_style="mitre")
        union = drop_inner_pieces(union)
        problem = closure_problem(walls, union)
    elif union.geom_type != "Polygon":
        parts = len(getattr(union, "geoms", []))
        problem = f"outer walls do not form one closed loop ({union.geom_type}, {parts} parts)"
    elif len(union.interiors) == 0:
        problem = "walls form no enclosed room"
    else:
        problem = None
    union = drop_inner_pieces(union)
    if problem is not None:
        result.closed = False
        result.warnings.append(f"{level_id}: {problem}")
        if union.geom_type != "Polygon" or len(union.interiors) == 0:
            return result
        # Loose ends: the rooms that are still enclosed are derived below so
        # the review report can show them; the level stays "not closed".

    polys = wall_polygons(walls)
    exterior = union.exterior
    for i, poly in enumerate(polys):
        if poly.distance(exterior) < TOUCH_M:
            walls[i].exterior = True
            result.exterior_walls.append(i)

    faces = [ring_to_polygon(ring) for ring in union.interiors]
    lines = _separator_lines(separators)
    if lines:
        faces = [snap_to_separators(face, lines) for face in faces]
    faces.sort(key=lambda poly: (poly[0][1], poly[0][0]))
    fallbacks = label_fallback_points or [None] * len(labels)
    outline = Polygon(exterior)

    def face_index_of(point) -> Optional[int]:
        if point is None:
            return None
        for j, face in enumerate(faces):
            if Polygon(face).contains(ShapelyPoint(point)):
                return j
        return None

    label_faces: dict[int, list[int]] = {}
    for i, label in enumerate(labels):
        j = face_index_of(label_points[i])
        if j is None:
            j = face_index_of(fallbacks[i])
        if j is None:
            block = getattr(label, "block", None)
            if block is not None and (block.exterior or not outline.contains(ShapelyPoint(label_points[i]))):
                continue              # a site label, or a room name outside the building: split_plot reports it
            result.unplaced_labels.append(label)
            result.warnings.append(f"{level_id}: label '{label.text}' ({label.entity}) is outside every room")
            continue
        label_faces.setdefault(j, []).append(i)

    for j, face in enumerate(faces):
        shp = Polygon(face)
        area = round(shp.area, 3)
        indices = label_faces.get(j, [])
        generic = [k for k in indices if getattr(labels[k], "block", None) is not None]
        if generic:
            indoor = [k for k in generic if not labels[k].block.exterior]
            if not indoor:
                continue              # named only by exterior labels: a site area, not a room (§2.5)
            indices = indoor + [k for k in indices if k not in generic]
        status = "verified"
        evidence = []
        label_size = None
        size_conflict = None
        if not indices:
            label, area_label, label_raw = unlabelled_label, None, None
            room_type = "unknown"
            if face_type is not None:
                typed = face_type(shp)
                room_type, reason = typed[0], typed[1]
                if len(typed) > 2 and typed[2]:
                    # Milestone 11 (M8): a face the stair fills is named for it ("Merdiven"), not "Oda".
                    label = typed[2]
                result.warnings.append(f"{level_id}: room at {face[0]} ({area:.2f} m²) has no label: {reason}")
            else:
                result.warnings.append(f"{level_id}: room at {face[0]} ({area:.2f} m²) has no label")
            status = "unverified"
        elif getattr(labels[indices[0]], "block", None) is not None:
            if len(indices) > 1:
                # Several names in one face (an entrance hall open to the living room, real03): the name of the
                # largest printed net area names the face; without printed areas the first one stays.
                def printed(k: int) -> float:
                    blk = getattr(labels[k], "block", None)
                    return blk.area_m2 if blk is not None and blk.area_m2 is not None else -1.0
                best = max(indices, key=printed)
                if printed(best) > 0:
                    indices = [best] + [k for k in indices if k != best]
            first = labels[indices[0]]
            block = first.block
            label, _, _ = B.normalise_room_label(block.name, turkish=first.turkish)
            from wenart.ingest.generic.labels import check_label_size, room_type_for
            face_area, aspect = _face_size(shp)
            room_type = room_type_for(block.name, face_area, aspect)[0]
            area_label = round(block.area_m2, 3) if block.area_m2 is not None else None
            label_raw = block.name
            for k in indices:
                evidence.extend(labels[k].block.evidence if getattr(labels[k], "block", None) is not None
                                else [labels[k].evidence])
            check = check_label_size(block, shp)
            if check is not None:
                label_size = {key: check[key] for key in ("text", "width_m", "length_m", "measured", "status")}
                if "off_pct" in check:
                    label_size["off_pct"] = check["off_pct"]
                if check.get("unverified"):
                    status = "unverified"
                if check["status"] == "conflict":
                    size_conflict = check
            if len(indices) > 1:
                status = "unverified"
                extra = [labels[k].text for k in indices[1:]]
                result.warnings.append(f"{level_id}: room '{label}' has more labels: {', '.join(extra)}; the label "
                                       f"with the largest printed area (else the first) kept")
        else:
            first = labels[indices[0]]
            label, room_type, area_label = B.normalise_room_label(first.text)
            label_raw = first.text
            for k in indices:
                evidence.append(labels[k].evidence or B.evidence(file_rel, "vector", 1.0, entity=labels[k].entity,
                                                                 text=labels[k].text))
            if len(indices) > 1:
                status = "unverified"
                extra = ", ".join(labels[k].text for k in indices[1:])
                result.warnings.append(f"{level_id}: room '{label}' has more labels: {extra}; first label kept")
        room_id = ids.room(level_id, label)
        if generic and len(indices) > 1:
            result.multi_labels.append((room_id, label, [labels[k].text for k in indices[1:]]))
        if size_conflict is not None:
            result.label_size_conflicts.append((room_id, size_conflict))
        touching = [i for i, poly in enumerate(polys) if poly.distance(shp) < TOUCH_M]
        result.room_walls[room_id] = touching
        room = {
            "id": room_id, "level_id": level_id, "label": label, "label_raw": label_raw, "room_type": room_type,
            "polygon": [list(p) for p in face], "area_computed": area, "area_label": area_label,
            "has_documented_furniture": False, "style_override": None, "status": status, "evidence": evidence,
        }
        if label_size is not None:
            room["label_size"] = label_size
        result.rooms.append(room)
    return result


def room_containing(rooms: list[dict], point) -> Optional[dict]:
    """The room whose polygon contains ``point`` (boundary counts as inside), or None."""
    for room in rooms:
        if G.point_in_polygon(point, room["polygon"]):
            return room
    return None
