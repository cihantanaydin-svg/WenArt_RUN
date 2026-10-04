"""Write one level as a DXF file (R2010, millimetres, model space) the way a
Turkish architectural office would draw it: wall rectangles on ``DUVAR``,
door/window block inserts on ``KAPI``/``PENCERE``, room labels on ``YAZI``,
aligned dimensions on ``OLCU`` and furniture block inserts on ``MOBILYA``.

The writer returns a ``PageRecord`` with the entity handle of every element so
the truth files can point at the exact DXF entity (``LWPOLYLINE:<handle>``).
Output bytes are deterministic: the header date and GUID variables are fixed.

``write_cad_dxf`` draws synthetic-06 "the real way" (docs/milestone7.md §5.2):
inches, AIA layers, one solid wall hatch, door arcs and window lines on
continuous walls, nested furniture blocks, MTEXT/TEXT/attribute labels and
feet-inch dimensions; see its docstring for the LibreDWG workarounds.
"""
from __future__ import annotations

from pathlib import Path

import math
from typing import Optional

import ezdxf
from ezdxf.tools.text_size import text_size
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from wenart import geometry as G
from wenart.synthetic import blocks
from wenart.synthetic.model import Level, PageRecord, format_metres

MM = 1000.0  # building metres -> drawing millimetres

TEXT_HEIGHT_LABEL = 200.0   # 2 mm on paper at 1:100
TEXT_HEIGHT_TITLE = 500.0
TEXT_HEIGHT_SCALE = 300.0
TEXT_HEIGHT_DIM = 200.0
SCALE_TEXT_GAP = 1000.0  # "ÖLÇEK 1/100" starts this far right of the title's end

# ezdxf writes the current time and random GUIDs into the header and its own
# metadata marker. The option below replaces them with constants so two runs
# give byte-identical files (it is what ezdxf's own test-suite uses).
_FIXED_META_OPTION = "write_fixed_meta_data_for_testing"

DIMSTYLE = "WENART"
DIMSTYLE_ATTRIBS = {
    "dimlfac": 0.001,       # measurement printed in metres
    "dimdec": 2,
    "dimzin": 0,            # keep trailing zeros: 5,30
    "dimdsep": ord(","),    # comma decimal separator
    "dimtxt": TEXT_HEIGHT_DIM,
    "dimasz": 100.0,
    "dimtsz": 0.0,
    "dimblk": "ARCHTICK",
    "dimexo": 50.0,
    "dimexe": 100.0,
    "dimgap": 40.0,
}


def mm(p) -> tuple[float, float]:
    """Metres (building frame) -> millimetres, rounded to 1e-6 mm."""
    return (G.snap(p[0] * MM, 6), G.snap(p[1] * MM, 6))


def _text_box(entity) -> list[float]:
    """Axis-aligned box of a TEXT entity in mm from its insert point and measured size."""
    size = text_size(entity)
    x, y = entity.dxf.insert.x, entity.dxf.insert.y
    descent = size.total_height - size.cap_height
    rotation = entity.dxf.rotation
    corners = [(x, y - descent), (x + size.width, y - descent), (x + size.width, y + size.cap_height), (x, y + size.cap_height)]
    if rotation:
        corners = [G.rotate_point(c, rotation, (x, y)) for c in corners]
    return [round(v, 3) for v in G.bbox(corners)]


def _define_opening_block(doc, name: str) -> None:
    kind, width = blocks.opening_from_block(name)
    w = width * MM
    blk = doc.blocks.new(name)
    if kind == "door":
        # Hinge at (-w/2, 0); leaf open 90 degrees towards +Y; swing arc.
        blk.add_line((-w / 2, 0), (-w / 2, w))
        blk.add_arc(center=(-w / 2, 0), radius=w, start_angle=0, end_angle=90)
    else:
        d = blocks.WINDOW_SYMBOL_DEPTH * MM / 2
        blk.add_line((-w / 2, -d), (w / 2, -d))
        blk.add_line((-w / 2, d), (w / 2, d))
        blk.add_line((-w / 2, -d), (-w / 2, d))
        blk.add_line((w / 2, -d), (w / 2, d))


def _define_furniture_block(doc, name: str, size) -> None:
    w, d = size[0] * MM, size[1] * MM
    blk = doc.blocks.new(name)
    blk.add_lwpolyline([(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], close=True)
    # Short line parallel to the front edge (local -Y) marks the front.
    inset = min(50.0, d * 0.15)
    blk.add_line((-w / 4, -d / 2 + inset), (w / 4, -d / 2 + inset))


def write_dxf(level: Level, path: Path, file_rel: str, *, title_raw: str, page_class: str,
              openings=None, furniture=None, dimensions=None) -> PageRecord:
    """Write ``level`` to ``path``. The optional lists restrict what is drawn
    (used for deliberate omissions); they default to everything on the level."""
    previous = getattr(ezdxf.options, _FIXED_META_OPTION)
    setattr(ezdxf.options, _FIXED_META_OPTION, True)
    try:
        return _write_dxf(level, Path(path), file_rel, title_raw=title_raw, page_class=page_class,
                          openings=openings, furniture=furniture, dimensions=dimensions)
    finally:
        setattr(ezdxf.options, _FIXED_META_OPTION, previous)


def _write_dxf(level: Level, path: Path, file_rel: str, *, title_raw: str, page_class: str,
               openings, furniture, dimensions) -> PageRecord:
    openings = level.openings if openings is None else openings
    furniture = level.furniture if furniture is None else furniture
    dimensions = level.dimensions if dimensions is None else dimensions

    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # millimetres
    for layer in blocks.LAYERS:
        doc.layers.add(layer)
    doc.dimstyles.new(DIMSTYLE, dxfattribs=DIMSTYLE_ATTRIBS)
    msp = doc.modelspace()

    record = PageRecord(
        file=file_rel, page=1, kind="vector", page_class=page_class, level_id=level.id,
        units="mm", size=None, scale_metres_per_unit=0.001, transform_kind="affine",
        building_to_page=G.affine_from_scale_translate(MM, MM, 0.0, 0.0), title_raw=title_raw,
        scale_entity="$INSUNITS=4",
    )

    # Block definitions, in a fixed order.
    for name in sorted({o.block for o in openings}):
        _define_opening_block(doc, name)
    sizes: dict[str, tuple] = {}
    for piece in furniture:
        if piece.block in sizes and sizes[piece.block] != tuple(piece.size):
            raise ValueError(f"block {piece.block} used with two sizes")
        sizes[piece.block] = tuple(piece.size)
    for name in sorted(sizes):
        _define_furniture_block(doc, name, sizes[name])

    # Walls
    for wall in level.walls:
        corners = [mm(c) for c in wall.rectangle()]
        ent = msp.add_lwpolyline(corners, close=True, dxfattribs={"layer": blocks.LAYER_WALLS})
        entity = f"LWPOLYLINE:{ent.dxf.handle}"
        box = [round(v, 3) for v in G.bbox(corners)]
        record.entities[wall.id] = entity
        record.boxes[wall.id] = box
        record.walls.append({"id": wall.id, "box": box, "entity": entity})

    # Openings
    for opening in openings:
        layer = blocks.LAYER_DOORS if opening.kind == "door" else blocks.LAYER_WINDOWS
        ent = msp.add_blockref(opening.block, mm(opening.center),
                               dxfattribs={"layer": layer, "rotation": opening.rotation_deg})
        entity = f"INSERT:{ent.dxf.handle}"
        box = _opening_box(opening)
        record.entities[opening.id] = entity
        record.boxes[opening.id] = box
        record.symbols.append({"id": opening.id, "type": opening.kind, "block": opening.block,
                               "box": box, "rotation_deg": opening.rotation_deg, "entity": entity})

    # Furniture
    for piece in furniture:
        ent = msp.add_blockref(piece.block, mm(piece.center),
                               dxfattribs={"layer": blocks.LAYER_FURNITURE, "rotation": piece.rotation_deg})
        entity = f"INSERT:{ent.dxf.handle}"
        box = [round(v, 3) for v in G.bbox([mm(c) for c in piece.corners()])]
        record.entities[piece.id] = entity
        record.boxes[piece.id] = box
        record.symbols.append({"id": piece.id, "type": piece.type, "block": piece.block,
                               "box": box, "rotation_deg": piece.rotation_deg, "entity": entity})

    # Texts: title, scale, room labels
    title = msp.add_text(title_raw, height=TEXT_HEIGHT_TITLE, dxfattribs={"layer": blocks.LAYER_TEXT})
    title.set_placement(mm(level.title_at))
    record.title_entity = f"TEXT:{title.dxf.handle}"
    record.texts.append({"text": title_raw, "box": _text_box(title), "entity": record.title_entity, "role": "title"})

    scale_pos = (level.title_at[0] * MM + text_size(title).width + SCALE_TEXT_GAP, level.title_at[1] * MM)
    scale = msp.add_text(level.scale_text, height=TEXT_HEIGHT_SCALE, dxfattribs={"layer": blocks.LAYER_TEXT})
    scale.set_placement(scale_pos)
    record.texts.append({"text": level.scale_text, "box": _text_box(scale), "entity": f"TEXT:{scale.dxf.handle}",
                         "role": "scale"})

    for room in level.rooms:
        lab = level.labels[room.label_index]
        ent = msp.add_text(lab.label_raw, height=TEXT_HEIGHT_LABEL, dxfattribs={"layer": blocks.LAYER_TEXT})
        ent.set_placement(mm(lab.at))
        entity = f"TEXT:{ent.dxf.handle}"
        box = _text_box(ent)
        record.entities[room.id] = entity
        record.boxes[room.id] = box
        record.texts.append({"text": lab.label_raw, "box": box, "entity": entity, "role": "room_label",
                             "element_id": room.id})

    # Dimensions (aligned). ezdxf renders the dimension block so viewers show it.
    for dim in dimensions:
        text = dim.text_override if dim.text_override else "<>"
        d = msp.add_aligned_dim(p1=mm(dim.p1), p2=mm(dim.p2), distance=dim.offset * MM, text=text,
                                dimstyle=DIMSTYLE, dxfattribs={"layer": blocks.LAYER_DIMENSIONS})
        d.render()
        ent = d.dimension
        entity = f"DIMENSION:{ent.dxf.handle}"
        box = _dimension_text_box(dim, ent)
        record.dimensions.append({"measured": round(dim.measured, 4), "printed": dim.printed, "entity": entity,
                                  "wall_ids": list(dim.wall_ids), "box": box})
        record.texts.append({"text": dim.printed, "box": box, "entity": entity, "role": "dimension"})

    # ezdxf fills the CLASSES section from a set of entity types at save time;
    # a set iterates in hash order, which varies between processes. Registering
    # the types in sorted order first makes the file byte-stable.
    for dxftype in sorted(doc.entitydb.dxf_types_in_use()):
        doc.classes.add_class(dxftype)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return record


def _opening_box(opening) -> list[float]:
    """Axis-aligned box (mm) of the opening symbol."""
    return [round(v, 3) for v in G.bbox([mm(p) for p in opening.symbol_corners()])]


def _dimension_text_box(dim, entity) -> list[float]:
    """Approximate box (mm) of the printed dimension text, centred on the dimension line."""
    mid = entity.dxf.get("text_midpoint") or entity.dxf.defpoint
    text = dim.printed
    width = 0.75 * TEXT_HEIGHT_DIM * len(text)
    height = TEXT_HEIGHT_DIM
    angle = G.segment_angle_deg(dim.p1, dim.p2)
    corners = [(-width / 2, -height / 2), (width / 2, -height / 2), (width / 2, height / 2), (-width / 2, height / 2)]
    pts = [G.rotate_point((mid.x + x, mid.y + y), angle, (mid.x, mid.y)) for x, y in corners]
    return [round(v, 3) for v in G.bbox(pts)]


def dimension_printed_text(entity) -> str:
    """What a reader should print for a DIMENSION entity: the text override, or
    the measurement formatted with the dimension style (metres, two decimals, comma)."""
    text = entity.dxf.text
    if text and text != "<>":
        return text
    style = entity.override()  # dimstyle values with the entity's overrides applied
    return format_metres(entity.get_measurement() * style.get("dimlfac", 1.0))


# --------------------------------------------------------------------------
# synthetic-06: drawn "the real way" (docs/milestone7.md §5.2)
# --------------------------------------------------------------------------

INCH_M = 0.0254
CAD_DIMSTYLE = "ARCH-IN"
CAD_DIMSTYLE_ATTRIBS = {
    "dimtxt": 6.0, "dimasz": 4.0, "dimblk": "ARCHTICK", "dimexo": 2.0, "dimexe": 2.0, "dimgap": 1.5, "dimtad": 1,
}
CAD_TITLE_HEIGHT = 18.0
# Text box estimate for pages.json (the same rule as wenart.ingest.dxf_generic: 0.8 x height per character,
# 0.25 x height below the baseline; MTEXT lines 5/3 x height apart).
CAD_CHAR_WIDTH = 0.8
CAD_DESCENT = 0.25
CAD_LINE_SPACING = 5.0 / 3.0


def canonical_ring(coords) -> list[tuple[float, float]]:
    """A polygon ring as a canonical vertex list: no closing point, no collinear points, counter-clockwise,
    starting at the minimum (x, y) vertex, so the DXF bytes do not depend on the GEOS version."""
    poly = orient(Polygon(coords), sign=1.0)
    pts = [G.snap_point(c, 6) for c in poly.exterior.coords[:-1]]
    keep = []
    n = len(pts)
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-9:
            keep.append(b)
    start = keep.index(min(keep))
    return keep[start:] + keep[:start]


def cad_wall_rings(plan) -> tuple[list, list[list]]:
    """(outer ring, room islands) of the wall union of ``plan`` in inches, building frame."""
    union = unary_union([Polygon(w.rectangle()) for w in plan.walls])
    if union.geom_type != "Polygon":
        raise ValueError(f"synthetic-06 walls are not one closed loop ({union.geom_type})")
    islands = sorted((canonical_ring(r.coords) for r in union.interiors), key=lambda r: (r[0][1], r[0][0]))
    return canonical_ring(union.exterior.coords), islands


def _define_cad_blocks(doc) -> None:
    """The furniture blocks of synthetic-06 (inches, centred, front = -Y) and the room tag. Entities on layer 0
    with BYLAYER colour, so they take the layer of the INSERT (the CAD convention)."""
    def rect(blk, x0, y0, x1, y1):
        blk.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True)

    bed = doc.blocks.new("BED-DOUBLE")
    rect(bed, -30, -40, 30, 40)
    rect(bed, -26, 26, -2, 36)                          # pillows at the head (+Y)
    rect(bed, 2, 26, 26, 36)
    bed.add_line((-30, 10), (30, 10))                   # turned-down cover
    sofa = doc.blocks.new("SOFA-3")
    rect(sofa, -42, -18, 42, 18)
    sofa.add_line((-42, 10), (42, 10))                  # back cushion (+Y)
    for x in (-36, -12, 12, 36):                        # arms and seat cushions
        sofa.add_line((x, -18), (x, 10))
    chair = doc.blocks.new("CHAIR")
    rect(chair, -9, -9, 9, 9)
    chair.add_line((-9, 6), (9, 6))                     # back (+Y)
    dining = doc.blocks.new("DINING-6")
    rect(dining, -36, -18, 36, 18)
    for x, y, rotation in blocks.CAD_DINING_CHAIRS:
        dining.add_blockref("CHAIR", (x, y), dxfattribs={"rotation": rotation})
    wc = doc.blocks.new("WC")
    rect(wc, -10, 6, 10, 14)                            # cistern at the back (+Y)
    wc.add_ellipse((0, -4), major_axis=(0, 10), ratio=0.7)   # bowl, front at y -14
    basin = doc.blocks.new("BASIN")
    rect(basin, -10, -8, 10, 8)
    basin.add_circle((0, -1), 6)
    tag = doc.blocks.new(blocks.CAD_ROOMTAG)
    tag.add_attdef(blocks.CAD_ROOMTAG_ATTRIBUTE, (0, 0), dxfattribs={"height": 9.0})


def cad_text_box(at, text: str, height: float) -> list[float]:
    return [round(at[0], 3), round(at[1] - CAD_DESCENT * height, 3),
            round(at[0] + len(text) * CAD_CHAR_WIDTH * height, 3), round(at[1] + height, 3)]


def _ids(ids: dict, kind: str, items: list) -> list:
    """The truth ids of ``kind`` in drawing order, padded with None (everything is drawn, ids or not)."""
    given = list(ids.get(kind, []))
    return given + [None] * (len(items) - len(given))


def _unit(v) -> tuple[float, float]:
    length = math.hypot(v[0], v[1])
    return (v[0] / length, v[1] / length)


def write_cad_dxf(project, path: Path, file_rel: str, *, title: Optional[str] = None,
                  ids: Optional[dict] = None) -> PageRecord:
    """Write synthetic-06 to ``path``: drawing units inches (``$INSUNITS=1``), the building at ``plan.origin``.

    Layers ``A-WALL`` (one solid hatch, ACI 7, outer loop + one island per room face, and the same rings as
    outline polylines), ``A-DOOR`` (arc + leaf line, hinged on the face of a continuous wall), ``A-GLAZ`` (three lines
    along the wall band and two jamb lines per window), ``A-FURN`` (block inserts; DINING-6 nests six CHAIRs),
    ``A-ANNO`` (MTEXT, TEXT and one ROOMTAG with a NAME attribute), ``A-DIMS`` (feet-inch dimensions with the
    printed text as override; horizontal ones rotated, vertical ones aligned, one vertical rotated).

    LibreDWG 0.14 workarounds (the DWG is written from this file by ``dxf2dwg``):
    - MTEXT inside the rendered ``*D`` dimension blocks stores its direction as a vector (code 11): ``dxf2dwg``
      stops with "Invalid DXF code 50 for MTEXT" on a rotation angle;
    - label MTEXTs also carry their height inline (``\\H9;``): ``dxf2dwg`` stores DXF code 40 of an MTEXT in the
      reference-rectangle width (its field table lists ``rect_width`` with code 40), so the DWG would say height 0.

    ``ids`` maps element kinds to the truth ids in order (walls, doors, windows, furniture, rooms); the returned
    record maps each id to its entity and box (inches, drawing frame). ``title`` draws the titled variant.
    """
    previous = getattr(ezdxf.options, _FIXED_META_OPTION)
    setattr(ezdxf.options, _FIXED_META_OPTION, True)
    try:
        return _write_cad_dxf(project, Path(path), file_rel, title=title, ids=ids or {})
    finally:
        setattr(ezdxf.options, _FIXED_META_OPTION, previous)


def _write_cad_dxf(project, path: Path, file_rel: str, *, title: Optional[str], ids: dict) -> PageRecord:
    plan = project.plan
    ox, oy = plan.origin

    def d(p) -> tuple[float, float]:
        return (G.snap(p[0] + ox, 6), G.snap(p[1] + oy, 6))

    doc = ezdxf.new("R2000", setup=True)
    doc.header["$INSUNITS"] = 1          # inches
    doc.header["$MEASUREMENT"] = 0       # imperial
    doc.header["$LUNITS"] = 4            # architectural
    for name, colour in blocks.CAD_LAYERS:
        doc.layers.add(name, color=colour)
    doc.dimstyles.new(CAD_DIMSTYLE, dxfattribs=CAD_DIMSTYLE_ATTRIBS)
    _define_cad_blocks(doc)
    msp = doc.modelspace()
    record = PageRecord(
        file=file_rel, page=1, kind="vector", page_class="floor_plan", level_id="L0", units="in", size=None,
        scale_metres_per_unit=INCH_M, transform_kind="affine",
        building_to_page=[1.0 / INCH_M, 0.0, ox, 0.0, 1.0 / INCH_M, oy], title_raw=title,
        scale_entity="$INSUNITS=1",
    )

    # Walls: one solid hatch over the wall union (outer loop + room islands) and its outline polylines.
    outer, islands = cad_wall_rings(plan)
    hatch = msp.add_hatch(color=7, dxfattribs={"layer": blocks.CAD_LAYER_WALLS})
    hatch.paths.add_polyline_path([d(p) for p in outer], is_closed=True, flags=1)       # external
    for ring in islands:
        hatch.paths.add_polyline_path([d(p) for p in ring], is_closed=True, flags=16)   # outermost
    hatch_entity = f"HATCH:{hatch.dxf.handle}"
    for ring in [outer] + islands:
        msp.add_lwpolyline([d(p) for p in ring], close=True, dxfattribs={"layer": blocks.CAD_LAYER_WALLS})
    for wall, wid in zip(plan.walls, _ids(ids, "walls", plan.walls)):
        if wid is None:
            continue
        box = [round(v, 3) for v in G.bbox([d(c) for c in wall.rectangle()])]
        record.entities[wid] = hatch_entity
        record.boxes[wid] = box
        record.walls.append({"id": wid, "box": box, "entity": hatch_entity})

    # Doors: arc (centre = hinge, radius = clear width) and the open leaf as a line from the hinge to the arc end.
    for door, did in zip(plan.doors, _ids(ids, "doors", plan.doors)):
        hx, hy = door.hinge
        ax, ay = door.along
        sx, sy = door.swing
        w = door.width
        a_along = math.degrees(math.atan2(ay, ax)) % 360.0
        a_swing = math.degrees(math.atan2(sy, sx)) % 360.0
        start, end = (a_along, a_swing) if ax * sy - ay * sx > 0 else (a_swing, a_along)
        arc = msp.add_arc(d(door.hinge), w, start, end, dxfattribs={"layer": blocks.CAD_LAYER_DOORS})
        msp.add_line(d(door.hinge), d((hx + sx * w, hy + sy * w)), dxfattribs={"layer": blocks.CAD_LAYER_DOORS})
        corners = [(hx, hy), (hx + ax * w, hy + ay * w), (hx + ax * w + sx * w, hy + ay * w + sy * w),
                   (hx + sx * w, hy + sy * w)]
        if did is None:
            continue
        box = [round(v, 3) for v in G.bbox([d(c) for c in corners])]
        entity = f"ARC:{arc.dxf.handle}"
        record.entities[did] = entity
        record.boxes[did] = box
        record.symbols.append({"id": did, "type": "door", "block": None, "box": box,
                               "rotation_deg": round(start, 6), "entity": entity})

    # Windows: both faces and the glass line along the band, and the two jambs across it.
    for window, wid in zip(plan.windows, _ids(ids, "windows", plan.windows)):
        wall = plan.walls[window.wall]
        ux, uy = _unit((wall.end[0] - wall.start[0], wall.end[1] - wall.start[1]))
        nx, ny = -uy, ux
        cx, cy = window.center
        half, band = window.width / 2.0, wall.thickness / 2.0
        first = None
        for off in (band, 0.0, -band):
            p0 = (cx - ux * half + nx * off, cy - uy * half + ny * off)
            p1 = (cx + ux * half + nx * off, cy + uy * half + ny * off)
            line = msp.add_line(d(p0), d(p1), dxfattribs={"layer": blocks.CAD_LAYER_GLAZING})
            first = first or line
        for end in (-half, half):
            p0 = (cx + ux * end + nx * band, cy + uy * end + ny * band)
            p1 = (cx + ux * end - nx * band, cy + uy * end - ny * band)
            msp.add_line(d(p0), d(p1), dxfattribs={"layer": blocks.CAD_LAYER_GLAZING})
        if wid is None:
            continue
        corners = [(cx + ux * s * half + nx * b * band, cy + uy * s * half + ny * b * band)
                   for s in (-1, 1) for b in (-1, 1)]
        box = [round(v, 3) for v in G.bbox([d(c) for c in corners])]
        entity = f"LINE:{first.dxf.handle}"
        record.entities[wid] = entity
        record.boxes[wid] = box
        record.symbols.append({"id": wid, "type": "window", "block": None, "box": box,
                               "rotation_deg": round(math.degrees(math.atan2(uy, ux)) % 360.0, 6),
                               "entity": entity})

    # Furniture: block inserts; the chairs of DINING-6 are its nested inserts 1..6 (the table rectangle is 0).
    furniture_ids = iter(ids.get("furniture", []))
    for piece in plan.furniture:
        ins = msp.add_blockref(piece.block, d(piece.center),
                               dxfattribs={"layer": blocks.CAD_LAYER_FURNITURE, "rotation": piece.rotation_deg})
        handle = ins.dxf.handle
        ftype, width, depth = blocks.CAD_BLOCKS[piece.block]
        parts = [(f"INSERT:{handle}", piece.block, piece.center, piece.rotation_deg, ftype, (width, depth))]
        if piece.block == "DINING-6":
            c_type, c_w, c_d = blocks.CAD_BLOCKS["CHAIR"]
            for k, (x, y, rotation) in enumerate(blocks.CAD_DINING_CHAIRS, start=1):
                cx, cy = G.rotate_point((x, y), piece.rotation_deg)
                parts.append((f"INSERT:{handle}/{k}", "DINING-6/CHAIR",
                              G.snap_point((piece.center[0] + cx, piece.center[1] + cy), 6),
                              G.normalise_angle(piece.rotation_deg + rotation), c_type, (c_w, c_d)))
        for entity, chain, center, rotation, ftype, size in parts:
            fid = next(furniture_ids, None)
            if fid is None:
                continue
            corners = G.rotated_rectangle(d(center), size, rotation)
            box = [round(v, 3) for v in G.bbox(corners)]
            record.entities[fid] = entity
            record.boxes[fid] = box
            record.symbols.append({"id": fid, "type": ftype, "block": chain, "box": box,
                                   "rotation_deg": rotation, "entity": entity})

    # Labels: MTEXT (name + size line, height also inline), TEXT, and the room tag's attribute.
    for label, rid in zip(plan.labels, _ids(ids, "rooms", plan.labels)):
        h = label.height
        if label.kind == "mtext":
            content = f"\\H{h:g};" + "\\P".join(label.lines)
            ent = msp.add_mtext(content, dxfattribs={"layer": blocks.CAD_LAYER_ANNOTATION, "char_height": h,
                                                     "insert": d(label.at), "attachment_point": 1})
            base = f"MTEXT:{ent.dxf.handle}"
            entities = [f"{base}:{k}" for k in range(len(label.lines))] if len(label.lines) > 1 else [base]
            baselines = [label.at[1] - h - k * CAD_LINE_SPACING * h for k in range(len(label.lines))]
            starts = [(label.at[0], y) for y in baselines]
        elif label.kind == "text":
            ent = msp.add_text(label.lines[0], height=h, dxfattribs={"layer": blocks.CAD_LAYER_ANNOTATION})
            ent.set_placement(d(label.at))
            entities, starts = [f"TEXT:{ent.dxf.handle}"], [label.at]
        elif label.kind == "roomtag":
            ins = msp.add_blockref(blocks.CAD_ROOMTAG, d(label.at), dxfattribs={"layer": blocks.CAD_LAYER_ANNOTATION})
            attrib = ins.add_auto_attribs({blocks.CAD_ROOMTAG_ATTRIBUTE: label.lines[0]}).attribs[0]
            entities, starts = [f"ATTRIB:{attrib.dxf.handle}"], [label.at]
        else:
            raise ValueError(label.kind)
        for k, (line, entity, at) in enumerate(zip(label.lines, entities, starts)):
            box = cad_text_box(d(at), line, h)
            entry = {"text": line, "box": box, "entity": entity, "role": "room_label" if k == 0 else "room_size"}
            if rid is not None:
                entry["element_id"] = rid
                if k == 0:
                    record.entities[rid] = entity
                    record.boxes[rid] = box
            record.texts.append(entry)

    # Dimensions: the printed feet-inch text is the override (ezdxf cannot format architectural units).
    for dim in plan.dimensions:
        p1, p2 = d(dim.p1), d(dim.p2)
        ux, uy = _unit((p2[0] - p1[0], p2[1] - p1[1]))
        attribs = {"layer": blocks.CAD_LAYER_DIMENSIONS}
        if dim.kind == "aligned":
            override = msp.add_aligned_dim(p1=p1, p2=p2, distance=dim.offset, text=dim.text, dimstyle=CAD_DIMSTYLE,
                                           dxfattribs=attribs)
        else:
            base = (p1[0] - uy * dim.offset, p1[1] + ux * dim.offset)
            override = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=math.degrees(math.atan2(uy, ux)),
                                          text=dim.text, dimstyle=CAD_DIMSTYLE, dxfattribs=attribs)
        override.render()
        ent = override.dimension
        if dim.kind == "aligned":
            # ezdxf draws aligned dimensions as rotated ones; the entity says what it is.
            ent.dxf.dimtype = (ent.dxf.dimtype & ~7) | 1
            ent.dxf.discard("angle")
        mid = ent.dxf.get("text_midpoint") or ent.dxf.defpoint
        record.dimensions.append({"measured": round(G.distance(dim.p1, dim.p2) * INCH_M, 6), "printed": dim.text,
                                  "entity": f"DIMENSION:{ent.dxf.handle}", "kind": dim.kind, "wall_ids": [],
                                  "box": cad_text_box((mid.x - len(dim.text) * CAD_CHAR_WIDTH * 3.0, mid.y),
                                                       dim.text, CAD_DIMSTYLE_ATTRIBS["dimtxt"])})
        record.texts.append({"text": dim.text, "box": record.dimensions[-1]["box"],
                             "entity": f"DIMENSION:{ent.dxf.handle}", "role": "dimension"})

    # The title of the titled variant comes last, so every other entity keeps its handle.
    if title:
        ent = msp.add_text(title, height=CAD_TITLE_HEIGHT, dxfattribs={"layer": blocks.CAD_LAYER_ANNOTATION})
        at = (0.0, max(w.end[1] for w in plan.walls) + plan.walls[0].thickness + 60.0)
        ent.set_placement(d(at))
        record.title_entity = f"TEXT:{ent.dxf.handle}"
        record.texts.append({"text": title, "box": cad_text_box(d(at), title, CAD_TITLE_HEIGHT),
                             "entity": record.title_entity, "role": "title"})

    # dxf2dwg cannot read an MTEXT rotation angle (code 50): store the direction vector instead.
    for blk in doc.blocks:
        for e in blk:
            if e.dxftype() == "MTEXT" and e.dxf.hasattr("rotation"):
                angle = math.radians(e.dxf.rotation)
                e.dxf.discard("rotation")
                e.dxf.text_direction = (round(math.cos(angle), 12) + 0.0, round(math.sin(angle), 12) + 0.0, 0.0)

    for dxftype in sorted(doc.entitydb.dxf_types_in_use()):
        doc.classes.add_class(dxftype)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return record
