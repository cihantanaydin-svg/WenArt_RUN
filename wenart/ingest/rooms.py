"""Rooms from walls: shapely union of the wall rectangles -> interior faces.

Each interior ring of the union is a room polygon. A room label (TEXT inside
the face) names it; the label's area suffix becomes ``area_label``. Faces
without a label, with several labels, or labels outside every face are
reported, never fixed silently. The exterior ring tells which walls are
exterior and whether the outer walls close (one polygon with at least one
hole); if they do not, the pipeline stops the project with ``needs_review``.

Coordinates are snapped to 1 mm and the union is closed by a 2 mm
morphological pass so that sub-millimetre gaps between touching rectangles
(PDF coordinate rounding) do not merge two rooms.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import Point as ShapelyPoint, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.ingest.model import TextItem, WallItem

SNAP_M = 0.001          # wall corner snapping (metres)
CLOSE_M = 0.002         # gap closing radius (metres)
TOUCH_M = 0.001         # "touches" tolerance for wall <-> ring tests

UNLABELLED_LABEL = "Oda"   # Turkish "room", used for faces with no label text


@dataclass
class RoomResult:
    rooms: list[dict] = field(default_factory=list)       # schema-shaped room dicts
    room_walls: dict = field(default_factory=dict)        # room id -> wall indices touching it
    closed: bool = True
    exterior_walls: list[int] = field(default_factory=list)
    unplaced_labels: list[TextItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


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


def outer_walls_closed(walls: list[WallItem]) -> bool:
    union = wall_union(walls)
    return union.geom_type == "Polygon" and len(union.interiors) >= 1


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


def derive_rooms(level_id: str, walls: list[WallItem], labels: list[TextItem], label_points: list[tuple[float, float]],
                 label_fallback_points: Optional[list[tuple[float, float]]] = None,
                 file_rel: str = "", ids: Optional[B.IdCounter] = None) -> RoomResult:
    """Rooms of one level.

    ``label_points[i]`` is the anchor of ``labels[i]`` in building metres (the
    text insert point); ``label_fallback_points[i]`` (e.g. the box centre) is
    tried when the anchor is in no face. Returns schema-shaped room dicts
    (without ``has_documented_furniture`` decided: it starts ``False``).
    """
    result = RoomResult()
    ids = ids or B.IdCounter()
    if not walls:
        result.closed = False
        result.warnings.append(f"{level_id}: no walls")
        return result
    union = wall_union(walls)
    if union.geom_type != "Polygon":
        result.closed = False
        parts = getattr(union, "geoms", [])
        result.warnings.append(f"{level_id}: outer walls do not form one closed loop "
                               f"({union.geom_type}, {len(parts)} parts)")
        return result
    if len(union.interiors) == 0:
        result.closed = False
        result.warnings.append(f"{level_id}: walls form no enclosed room")
        return result

    polys = wall_polygons(walls)
    exterior = union.exterior
    for i, poly in enumerate(polys):
        if poly.distance(exterior) < TOUCH_M:
            walls[i].exterior = True
            result.exterior_walls.append(i)

    faces = [ring_to_polygon(ring) for ring in union.interiors]
    faces.sort(key=lambda poly: (poly[0][1], poly[0][0]))
    fallbacks = label_fallback_points or [None] * len(labels)

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
            result.unplaced_labels.append(label)
            result.warnings.append(f"{level_id}: label '{label.text}' ({label.entity}) is outside every room")
            continue
        label_faces.setdefault(j, []).append(i)

    for j, face in enumerate(faces):
        shp = Polygon(face)
        area = round(shp.area, 3)
        indices = label_faces.get(j, [])
        status = "verified"
        evidence = []
        if not indices:
            label, room_type, area_label, label_raw = UNLABELLED_LABEL, "unknown", None, None
            status = "unverified"
            result.warnings.append(f"{level_id}: room at {face[0]} ({area:.2f} m²) has no label")
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
        touching = [i for i, poly in enumerate(polys) if poly.distance(shp) < TOUCH_M]
        result.room_walls[room_id] = touching
        result.rooms.append({
            "id": room_id, "level_id": level_id, "label": label, "label_raw": label_raw, "room_type": room_type,
            "polygon": [list(p) for p in face], "area_computed": area, "area_label": area_label,
            "has_documented_furniture": False, "style_override": None, "status": status, "evidence": evidence,
        })
    return result


def room_containing(rooms: list[dict], point) -> Optional[dict]:
    """The room whose polygon contains ``point`` (boundary counts as inside), or None."""
    for room in rooms:
        if G.point_in_polygon(point, room["polygon"]):
            return room
    return None
