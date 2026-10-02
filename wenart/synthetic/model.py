"""Data model of a synthetic level and the derivations that turn a hand-written
layout into ground truth (room polygons, opening rotations, furniture rooms).

All coordinates are in the building frame: metres, X right, Y up, origin at
the outer corner of the outer wall (see docs/milestone2.md). The writers
(``dxf_writer``, ``pdf_writer``) convert to drawing units.

Why shapely here: rooms are the interior faces of the union of all wall
rectangles. Deriving them from the walls (instead of typing polygons by hand)
guarantees that the truth matches the drawn geometry exactly, and it is the
same construction the ingest pipeline uses.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from shapely.geometry import Point as ShapelyPoint, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.synthetic import blocks

DEFAULT_CEILING_HEIGHT = 2.70
# Level elevation = order * LEVEL_PITCH (ceiling + slab). Only used for the truth.
LEVEL_PITCH = 3.00
SNAP_DECIMALS = 6


@dataclass
class Wall:
    start: tuple[float, float]
    end: tuple[float, float]
    thickness: float
    exterior: bool
    id: str = ""

    def rectangle(self) -> list[tuple[float, float]]:
        """Drawn rectangle (4 corners, CCW), snapped so touching faces share floats."""
        corners = G.centerline_to_rectangle(self.start, self.end, self.thickness)
        return [G.snap_point(c, SNAP_DECIMALS) for c in corners]

    def angle_deg(self) -> float:
        return G.segment_angle_deg(self.start, self.end)


@dataclass
class Opening:
    kind: str                      # "door" | "window"
    block: str                     # KAPI_90, PENCERE_120 ...
    wall_index: int                # index into Level.walls
    center: tuple[float, float]    # on the wall centre line
    swing_into: object = None      # doors only: label_raw of the room the door opens into, or a point inside it
    id: str = ""
    rotation_deg: float = 0.0      # derived: insert rotation
    swing_side: Optional[str] = None  # derived: room id

    @property
    def width(self) -> float:
        info = blocks.opening_from_block(self.block)
        if info is None:
            raise ValueError(f"not an opening block: {self.block}")
        return info[1]

    def symbol_corners(self) -> list[tuple[float, float]]:
        """Corners (metres) of the drawn symbol: door = leaf + swing square on the
        swing side, window = clear width by the double-line depth. Rotated with the wall."""
        w = self.width
        if self.kind == "door":
            local = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, w), (-w / 2, w)]
        else:
            d = blocks.WINDOW_SYMBOL_DEPTH / 2
            local = [(-w / 2, -d), (w / 2, -d), (w / 2, d), (-w / 2, d)]
        cx, cy = self.center
        return [G.rotate_point((cx + x, cy + y), self.rotation_deg, (cx, cy)) for x, y in local]


@dataclass
class RoomLabel:
    label_raw: str                 # text as drawn, e.g. "SALON 24,50 m²"
    at: tuple[float, float]        # text insertion point (left baseline), inside the room


@dataclass
class Furniture:
    block: str
    center: tuple[float, float]
    rotation_deg: float
    size: Optional[tuple[float, float]] = None  # only for BLOK_A/BLOK_B (as drawn)
    id: str = ""
    room_id: Optional[str] = None  # derived

    def __post_init__(self) -> None:
        if self.size is None:
            self.size = blocks.furniture_size(self.block)
        if self.size is None:
            raise ValueError(f"block {self.block} needs an explicit size")

    @property
    def type(self) -> str:
        return blocks.furniture_type(self.block)

    @property
    def status(self) -> str:
        return "verified" if self.block in blocks.BLOCKS else "unverified"

    def corners(self) -> list[tuple[float, float]]:
        return G.rotated_rectangle(self.center, self.size, self.rotation_deg)

    def front_deg(self) -> float:
        return G.front_direction_deg(self.rotation_deg)


@dataclass
class Dimension:
    p1: tuple[float, float]
    p2: tuple[float, float]
    offset: float                  # distance of the dimension line, positive = left of p1->p2
    text_override: Optional[str] = None  # printed text if it differs from the measurement
    wall_ids: list[str] = field(default_factory=list)  # walls the dimension runs along (for conflicts)

    @property
    def measured(self) -> float:
        return G.segment_length(self.p1, self.p2)

    @property
    def printed(self) -> str:
        """What the drawing shows: override or metres with a comma, two decimals."""
        return self.text_override if self.text_override else format_metres(self.measured)

    @property
    def printed_value(self) -> float:
        return float(self.printed.replace(",", "."))


@dataclass
class Room:
    id: str
    label: str
    label_raw: str
    room_type: str
    polygon: list[tuple[float, float]]
    area_computed: float
    area_label: Optional[float]
    label_index: int               # index into Level.labels
    wall_ids: list[str] = field(default_factory=list)

    def contains(self, p) -> bool:
        return G.point_in_polygon(p, self.polygon)


@dataclass
class Level:
    title_raw: str                 # e.g. "ZEMİN KAT PLANI"
    walls: list[Wall] = field(default_factory=list)
    openings: list[Opening] = field(default_factory=list)
    labels: list[RoomLabel] = field(default_factory=list)
    furniture: list[Furniture] = field(default_factory=list)
    dimensions: list[Dimension] = field(default_factory=list)
    rooms: list[Room] = field(default_factory=list)  # derived by finalise()
    title_at: tuple[float, float] = (0.0, 0.0)       # title text insertion point (building frame)
    scale_text: str = "ÖLÇEK 1/100"
    ceiling_height: float = DEFAULT_CEILING_HEIGHT

    @property
    def label(self) -> str:
        return B.normalise_level_label(self.title_raw)[0]

    @property
    def order(self) -> int:
        return B.normalise_level_label(self.title_raw)[1]

    @property
    def id(self) -> str:
        return B.level_id(self.order)

    @property
    def elevation(self) -> float:
        return self.order * LEVEL_PITCH

    def outer_box(self) -> list[float]:
        """Bounding box of all wall rectangles."""
        pts = [c for w in self.walls for c in w.rectangle()]
        return G.bbox(pts)

    def room_by_label(self, label_raw: str) -> Room:
        """The room whose label text is ``label_raw`` (exactly one must exist)."""
        hits = [r for r in self.rooms if r.label_raw == label_raw]
        if len(hits) != 1:
            raise KeyError(f"{label_raw!r}: {len(hits)} rooms on {self.id}")
        return hits[0]

    def room_at(self, p) -> Optional[Room]:
        for room in self.rooms:
            if room.contains(p):
                return room
        return None

    def doors(self) -> list[Opening]:
        return [o for o in self.openings if o.kind == "door"]

    def windows(self) -> list[Opening]:
        return [o for o in self.openings if o.kind == "window"]


def format_metres(value: float) -> str:
    """5.3 -> "5,30" (plan dimension style, comma decimal)."""
    return f"{value:.2f}".replace(".", ",")


# --------------------------------------------------------------------------
# Derivations
# --------------------------------------------------------------------------

def wall_union(level: Level):
    """Shapely union of all wall rectangles of a level."""
    return unary_union([Polygon(w.rectangle()) for w in level.walls])


def outer_walls_closed(level: Level) -> bool:
    """True when the wall union is one polygon (one exterior ring)."""
    union = wall_union(level)
    return union.geom_type == "Polygon"


def _ring_to_polygon(ring) -> list[tuple[float, float]]:
    """Interior ring -> CCW vertex list, closing point dropped, started at the min (x, y) vertex."""
    poly = orient(Polygon(ring), sign=1.0)
    coords = [G.snap_point(c, 4) for c in poly.exterior.coords[:-1]]
    # Remove collinear duplicates that shapely may keep from the union.
    cleaned: list[tuple[float, float]] = []
    n = len(coords)
    for i in range(n):
        prev, cur, nxt = coords[i - 1], coords[i], coords[(i + 1) % n]
        cross = (cur[0] - prev[0]) * (nxt[1] - cur[1]) - (cur[1] - prev[1]) * (nxt[0] - cur[0])
        if abs(cross) > 1e-9:
            cleaned.append(cur)
    start = cleaned.index(min(cleaned))
    return cleaned[start:] + cleaned[:start]


def derive_rooms(level: Level) -> list[Room]:
    """Rooms = interior faces of the wall union, labelled by the TEXT inside each.

    Raises ValueError when the outer walls are not closed, a face has no label
    or more than one, or a label is outside every face. The generator must
    never produce silently wrong truth.
    """
    union = wall_union(level)
    if union.geom_type != "Polygon":
        raise ValueError(f"{level.id}: outer walls are not a closed loop ({union.geom_type})")
    faces = [_ring_to_polygon(ring) for ring in union.interiors]
    if not faces:
        raise ValueError(f"{level.id}: no interior faces")
    rooms: list[Room] = []
    used_labels: set[int] = set()
    ids = B.IdCounter()
    # Deterministic room order: by polygon start vertex (min x, then y).
    faces.sort(key=lambda poly: (poly[0][1], poly[0][0]))
    for poly in faces:
        shp = Polygon(poly)
        inside = [i for i, lab in enumerate(level.labels) if shp.contains(ShapelyPoint(lab.at))]
        if len(inside) != 1:
            raise ValueError(f"{level.id}: face at {poly[0]} has {len(inside)} labels")
        idx = inside[0]
        used_labels.add(idx)
        label, room_type, area_label = B.normalise_room_label(level.labels[idx].label_raw)
        rooms.append(Room(
            id=ids.room(level.id, label),
            label=label,
            label_raw=level.labels[idx].label_raw,
            room_type=room_type,
            polygon=poly,
            area_computed=round(G.polygon_area(poly), 3),
            area_label=area_label,
            label_index=idx,
        ))
    missing = set(range(len(level.labels))) - used_labels
    if missing:
        raise ValueError(f"{level.id}: labels outside every room: {sorted(missing)}")
    # Bounding walls: rectangles that touch the room polygon.
    for room in rooms:
        shp = Polygon(room.polygon)
        room.wall_ids = [w.id for w in level.walls if Polygon(w.rectangle()).distance(shp) < 1e-6]
    return rooms


def _assign_ids(level: Level) -> None:
    ids = B.IdCounter()
    for wall in level.walls:
        wall.id = ids.next("wall", level.id)
    for opening in level.openings:
        opening.id = ids.next(opening.kind, level.id)
    for piece in level.furniture:
        piece.id = ids.next("furniture", level.id)


def _place_openings(level: Level) -> None:
    """Check each opening sits on its wall and derive rotation and swing side."""
    for opening in level.openings:
        wall = level.walls[opening.wall_index]
        if G.point_segment_distance(opening.center, wall.start, wall.end) > 1e-6:
            raise ValueError(f"{level.id}: {opening.block} at {opening.center} is not on wall {wall.id}")
        angle = wall.angle_deg()
        if opening.kind == "window":
            opening.rotation_deg = angle
            opening.swing_side = None
            continue
        if not opening.swing_into:
            raise ValueError(f"{level.id}: door {opening.id} needs swing_into")
        if isinstance(opening.swing_into, str):
            target = level.room_by_label(opening.swing_into)
        else:
            # A point inside the room, for levels with repeated labels.
            target = level.room_at(opening.swing_into)
            if target is None:
                raise ValueError(f"{level.id}: door {opening.id}: swing point {opening.swing_into} is in no room")
        nx, ny = G.unit_normal_left(wall.start, wall.end)
        probe = 0.3
        left = (opening.center[0] + nx * probe, opening.center[1] + ny * probe)
        right = (opening.center[0] - nx * probe, opening.center[1] - ny * probe)
        # The door block opens towards its local +Y; with rotation = wall angle
        # that is the left side of the wall direction.
        if target.contains(left):
            opening.rotation_deg = angle
        elif target.contains(right):
            opening.rotation_deg = G.normalise_angle(angle + 180.0)
        else:
            raise ValueError(f"{level.id}: door {opening.id} does not touch room {target.id}")
        opening.swing_side = target.id


def _place_furniture(level: Level) -> None:
    """Every piece must lie inside exactly one room (by its full footprint)."""
    for piece in level.furniture:
        room = level.room_at(piece.center)
        if room is None:
            raise ValueError(f"{level.id}: {piece.block} at {piece.center} is in no room")
        shp = Polygon(room.polygon)
        if not shp.buffer(1e-6).contains(Polygon(piece.corners())):
            raise ValueError(f"{level.id}: {piece.block} at {piece.center} crosses the walls of {room.id}")
        piece.room_id = room.id


def _link_dimensions(level: Level) -> None:
    """Record which walls a dimension runs along: both end points lie within the
    wall's thickness band (dimension points sit on the outer face of outer walls)."""
    for dim in level.dimensions:
        dim.wall_ids = []
        for wall in level.walls:
            reach = wall.thickness / 2.0 + 1e-6
            on_wall = (G.point_segment_distance(dim.p1, wall.start, wall.end) <= reach and
                       G.point_segment_distance(dim.p2, wall.start, wall.end) <= reach)
            parallel = G.angle_difference_deg(G.segment_angle_deg(dim.p1, dim.p2), wall.angle_deg()) in (0.0, 180.0)
            if on_wall and parallel:
                dim.wall_ids.append(wall.id)


def finalise(level: Level) -> Level:
    """Assign IDs, derive rooms, openings and furniture links. Idempotent."""
    _assign_ids(level)
    level.rooms = derive_rooms(level)
    _place_openings(level)
    _place_furniture(level)
    _link_dimensions(level)
    return level


# --------------------------------------------------------------------------
# Layout helper used by projects.py
# --------------------------------------------------------------------------

def outer_wall_lines(outline, thickness: float) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Centre lines (start, end) of the outer walls of an axis-aligned outline, one per edge, in edge order.

    ``outline``: the outer face of the building as vertices (metres, either
    orientation, no closing point). Each wall lies inside the outline along
    its edge, ``thickness`` wide. Lengthwise it runs corner to corner, as a
    drafter draws it: to the outer corner at a convex vertex (the two walls
    overlap in the corner square) and on to the inner corner at a reflex
    vertex (``thickness`` past the vertex), so the wall rectangles always meet
    and the union of all walls is one closed ring.

    Why: the default 4-wall rectangle is the special case
    ``[(0, 0), (W, 0), (W, H), (0, H)]`` (bottom, right, top, left), and a
    notched building (synthetic-05) needs six walls built by the same rule.
    Raises ValueError for fewer than 4 vertices, an edge that is not
    horizontal or vertical, a zero-length edge, two collinear edges in a row
    or a self-intersecting outline.
    """
    pts = [(float(x), float(y)) for x, y in outline]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    if n < 4:
        raise ValueError(f"outline needs at least 4 vertices, got {n}")
    if not Polygon(pts).is_valid:
        raise ValueError(f"outline is not a simple polygon: {pts}")
    # Unit direction of every edge i (pts[i] -> pts[i+1]); axis-aligned only.
    dirs = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        dx, dy = x1 - x0, y1 - y0
        if (dx == 0.0) == (dy == 0.0):
            raise ValueError(f"outline edge {pts[i]} -> {pts[(i + 1) % n]} is not horizontal or vertical "
                             "(or has zero length)")
        dirs.append((float((dx > 0) - (dx < 0)), float((dy > 0) - (dy < 0))))
    ccw = G.polygon_signed_area(pts) > 0

    def reflex(vertex: int) -> bool:
        """True when the outline turns inward at ``pts[vertex]`` (incoming edge vertex-1, outgoing edge vertex)."""
        (ax, ay), (bx, by) = dirs[vertex - 1], dirs[vertex]
        cross = ax * by - ay * bx
        if cross == 0.0:
            raise ValueError(f"outline edges at {pts[vertex]} are collinear")
        return cross < 0 if ccw else cross > 0

    h = thickness / 2.0
    lines = []
    for i in range(n):
        dx, dy = dirs[i]
        # Inward normal: left of the edge for a counter-clockwise outline, right for a clockwise one.
        nx, ny = (-dy, dx) if ccw else (dy, -dx)
        start_ext = thickness if reflex(i) else 0.0
        end_ext = thickness if reflex((i + 1) % n) else 0.0
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        start = (x0 - dx * start_ext + nx * h, y0 - dy * start_ext + ny * h)
        end = (x1 + dx * end_ext + nx * h, y1 + dy * end_ext + ny * h)
        lines.append((start, end))
    return lines


class LevelBuilder:
    """Small fluent helper so a level reads like a plan description.

    Walls are added as centre lines; outer walls are extended to the outer
    corners so their rectangles overlap there (as a drafter draws them).

    Outline: by default the ``width`` x ``height`` rectangle with four outer
    walls (indices 0..3: bottom, right, top, left). ``outline=[(x, y), ...]``
    (the outer face, axis-aligned, bounding box starting at the origin)
    gives a non-rectangular building: one outer wall per edge, in edge order,
    indices 0..n-1 (see ``outer_wall_lines``); ``width`` and ``height`` then
    default to the bounding box and must match it when given.
    """

    def __init__(self, title_raw: str, width: Optional[float] = None, height: Optional[float] = None,
                 outer_thickness: float = 0.25, inner_thickness: float = 0.10,
                 outline: Optional[list] = None) -> None:
        if outline is None:
            if width is None or height is None:
                raise ValueError("LevelBuilder needs width and height, or an outline")
            outline = [(0.0, 0.0), (width, 0.0), (width, height), (0.0, height)]
        else:
            x0, y0, x1, y1 = G.bbox([(float(x), float(y)) for x, y in outline])
            if (x0, y0) != (0.0, 0.0):
                raise ValueError(f"outline bounding box must start at the origin, got ({x0}, {y0})")
            if (width is not None and width != x1) or (height is not None and height != y1):
                raise ValueError(f"width/height {width} x {height} do not match the outline box {x1} x {y1}")
            width, height = x1, y1
        self.level = Level(title_raw=title_raw)
        self.width = width
        self.height = height
        self.t_out = outer_thickness
        self.t_in = inner_thickness
        self.level.title_at = (0.0, height + 1.2)
        for start, end in outer_wall_lines(outline, outer_thickness):
            self.wall(start, end, outer_thickness, exterior=True)

    @property
    def inner_min(self) -> float:
        """Inner face of the left/bottom outer wall."""
        return self.t_out

    def wall(self, start, end, thickness=None, exterior=False) -> int:
        """Add a wall centre line; returns its index for openings."""
        t = self.t_in if thickness is None else thickness
        start, end = sorted([G.snap_point(start), G.snap_point(end)])
        self.level.walls.append(Wall(start=start, end=end, thickness=t, exterior=exterior))
        return len(self.level.walls) - 1

    def door(self, wall_index: int, center, width_cm: int, into) -> int:
        """``into``: label_raw of the room the door opens into, or a point inside that room."""
        self.level.openings.append(Opening("door", f"KAPI_{width_cm}", wall_index,
                                           G.snap_point(center), swing_into=into))
        return len(self.level.openings) - 1

    def window(self, wall_index: int, center, width_cm: int) -> int:
        self.level.openings.append(Opening("window", f"PENCERE_{width_cm}", wall_index, G.snap_point(center)))
        return len(self.level.openings) - 1

    def label(self, label_raw: str, at) -> int:
        self.level.labels.append(RoomLabel(label_raw, G.snap_point(at)))
        return len(self.level.labels) - 1

    def furniture(self, block: str, center, rotation_deg: float = 0.0, size=None) -> int:
        self.level.furniture.append(Furniture(block, G.snap_point(center), float(rotation_deg), size))
        return len(self.level.furniture) - 1

    def dimension(self, p1, p2, offset: float, text_override: Optional[str] = None) -> int:
        self.level.dimensions.append(Dimension(G.snap_point(p1), G.snap_point(p2), offset, text_override))
        return len(self.level.dimensions) - 1

    def dimension_chain(self, side: str, stops: list[float], text_overrides: Optional[dict] = None) -> None:
        """Chain of dimensions along the bottom (``"bottom"``) or left (``"left"``)
        outer wall through ``stops`` (coordinates along the wall, including 0 and
        the total), plus the overall dimension further out.
        ``text_overrides`` maps a chain segment index to a printed text.
        """
        text_overrides = text_overrides or {}
        near, far = -0.6, -1.1
        if side == "bottom":
            pts = [(s, 0.0) for s in stops]
            # Direction +X: negative offset = below the building (right of the direction).
            self._chain(pts, near, far, text_overrides)
        elif side == "left":
            pts = [(0.0, s) for s in stops]
            # Direction +Y: positive offset = left of the direction = outside on the left.
            self._chain(pts, -near, -far, text_overrides)
        else:
            raise ValueError(side)

    def _chain(self, pts, near, far, overrides) -> None:
        for i in range(len(pts) - 1):
            self.dimension(pts[i], pts[i + 1], near, overrides.get(i))
        self.dimension(pts[0], pts[-1], far)

    def build(self) -> Level:
        return finalise(self.level)


# --------------------------------------------------------------------------
# What a writer reports back about one drawn page (feeds truth/pages.json
# and the evidence entries of truth/building.json)
# --------------------------------------------------------------------------

@dataclass
class PageRecord:
    """One drawn page: where every element ended up, in page units.

    ``units``: "mm" (DXF model space), "pt" (PDF, origin bottom-left) or
    "px" (raster, origin top-left). Boxes are axis-aligned [x0, y0, x1, y1].
    ``entities`` maps element id -> entity string for evidence
    ("LWPOLYLINE:<handle>", "INSERT:<handle>", "TEXT:<handle>",
    "DIMENSION:<handle>", "path:<n>", "char:<n>", or "pixel_box" for rasters).
    """
    file: str
    page: int
    kind: str                      # vector | scan | photo
    page_class: str                # floor_plan | furniture_plan
    level_id: str
    units: str
    size: Optional[list[float]]    # [width, height] in page units (None for DXF)
    scale_metres_per_unit: Optional[float]
    transform_kind: str            # affine | homography
    building_to_page: list         # 6 numbers (affine) or 9 numbers row-major (homography)
    title_raw: str
    texts: list[dict] = field(default_factory=list)     # {text, box, entity, role, element_id?}
    symbols: list[dict] = field(default_factory=list)   # {id, type, block, box, rotation_deg, entity}
    walls: list[dict] = field(default_factory=list)     # {id, box, entity}
    dimensions: list[dict] = field(default_factory=list)  # {measured, printed, entity, wall_ids, box}
    entities: dict = field(default_factory=dict)        # element id -> entity string
    boxes: dict = field(default_factory=dict)           # element id -> box (page units)
    dpi: Optional[float] = None
    scale_entity: Optional[str] = None                  # entity of the "ÖLÇEK 1/100" text or "$INSUNITS=4"
    title_entity: Optional[str] = None

    def text_entry(self, element_id: str) -> Optional[dict]:
        for item in self.texts:
            if item.get("element_id") == element_id:
                return item
        return None
