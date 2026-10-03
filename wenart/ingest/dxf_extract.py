"""DXF model space -> ``LevelExtraction`` (docs/milestone2.md §2, conventions).

What is read, by layer (names matched case-insensitively):
- ``DUVAR``: closed 4-corner LWPOLYLINEs are wall rectangles; long axis =
  centre line, short side = thickness (``geometry.rectangle_to_centerline``).
- ``KAPI`` / ``PENCERE``: INSERTs. The block name gives type and clear width
  (``KAPI_90`` -> door 0.90 m). Unknown names fall back to the layer for the
  type and the block's drawn extent for the width, marked ``unverified``.
- ``MOBILYA``: INSERTs. Block name -> type via ``wenart.synthetic.blocks.BLOCKS``
  (a lookup, never a guess). The footprint is the rectangle drawn inside the
  block definition, like a wall: a known name drawn at another size than the
  table says keeps the drawn size, becomes ``unverified`` and raises a
  ``type_disagreement`` conflict. Unknown names -> ``unknown`` + ``unverified``.
  A known block without any geometry gets the table size and is ``unverified``.
- ``YAZI``: TEXT/MTEXT; roles title / scale / dimension / room label.
- ``OLCU``: DIMENSION, linear only. A rotated dimension (dimtype 0) measures the
  definition points projected onto its direction, as CAD prints it (a
  direction lost by the DWG conversion is recovered from the ``*D`` block's
  dimension line); an aligned one (dimtype 1) measures their distance.
  Printed = text override or the measurement formatted with the dimension style.

Units: ``$INSUNITS`` gives metres per drawing unit (4 = mm). The building
origin is the minimum corner of all wall rectangles, so the transform is
``[s, 0, -s*x0, 0, s, -s*y0]``.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import ezdxf
from ezdxf import recover, units as dxf_units
from ezdxf.tools.text_size import text_size

from wenart import building as B
from wenart import geometry as G
from wenart.ingest.model import (DOOR_SWING_PROBE, DimensionItem, FurnitureItem, LevelExtraction, OpeningItem,
                                 TextItem, WallItem, parse_number, text_role)
from wenart.synthetic import blocks
from wenart.synthetic.model import format_metres

# Drawn block size vs the BLOCKS table: a larger difference means the name and the
# geometry disagree (drawn size kept, piece unverified, conflict).
SIZE_TOLERANCE_M = 0.01


def read_dxf(path: str | Path):
    """``(doc, auditor)`` via ezdxf's recover mode (tolerant of slightly broken files)."""
    return recover.readfile(str(path))


SYNTHETIC_LAYERS = (blocks.LAYER_WALLS, blocks.LAYER_DOORS, blocks.LAYER_WINDOWS, blocks.LAYER_FURNITURE)


def has_synthetic_layers(doc) -> bool:
    """True when a model-space entity lies on one of the synthetic-convention layers (``DUVAR``, ``KAPI``,
    ``PENCERE``, ``MOBILYA``, any letter case): this module reads such a file; any other DXF/DWG goes to the
    generic adapter ``wenart.ingest.dxf_generic`` (docs/milestone7.md §5.2). Entities count, not layer-table rows:
    templates often define layers nobody draws on."""
    wanted = set(SYNTHETIC_LAYERS)
    return any((entity.dxf.get("layer") or "").upper() in wanted for entity in doc.modelspace())


def metres_per_unit_from_insunits(insunits: int) -> Optional[float]:
    """``$INSUNITS`` code -> metres per drawing unit; None for unitless or unknown codes."""
    try:
        factor = dxf_units.METER_FACTOR[int(insunits)]
    except (IndexError, TypeError, ValueError):
        return None
    if not factor:
        return None
    return 1.0 / factor


def _layer_of(entity) -> str:
    return (entity.dxf.layer or "").upper()


def _text_box_mm(entity) -> list[float]:
    """Axis-aligned box of a TEXT entity from its insert point and measured size."""
    size = text_size(entity)
    x, y = entity.dxf.insert.x, entity.dxf.insert.y
    descent = size.total_height - size.cap_height
    corners = [(x, y - descent), (x + size.width, y - descent),
               (x + size.width, y + size.cap_height), (x, y + size.cap_height)]
    rotation = entity.dxf.rotation
    if rotation:
        corners = [G.rotate_point(c, rotation, (x, y)) for c in corners]
    return [round(float(v), 3) for v in G.bbox(corners)]


def _block_rectangle(doc, name: str) -> Optional[list[tuple[float, float]]]:
    """Corners (block units) of the first closed 4-corner LWPOLYLINE in a block, else None."""
    if name not in doc.blocks:
        return None
    for ent in doc.blocks.get(name):
        if ent.dxftype() == "LWPOLYLINE":
            pts = [(float(p[0]), float(p[1])) for p in ent.get_points("xy")]
            if len(pts) == 5 and G.distance(pts[0], pts[-1]) < 1e-9:
                pts = pts[:4]
            if len(pts) == 4:
                return pts
    return None


def _block_extent(doc, name: str) -> Optional[list[float]]:
    """Bounding box (block units) of everything in a block definition, or None."""
    if name not in doc.blocks:
        return None
    from ezdxf import bbox
    extents = bbox.extents(doc.blocks.get(name))
    if not extents.has_data:
        return None
    return [extents.extmin.x, extents.extmin.y, extents.extmax.x, extents.extmax.y]


def extract_dxf(path: str | Path, level_id: str, file_rel: Optional[str] = None) -> LevelExtraction:
    """Read one DXF (one level per file) into a ``LevelExtraction``."""
    path = Path(path)
    file_rel = file_rel or path.name
    doc, auditor = read_dxf(path)
    ex = LevelExtraction(file=file_rel, page=1, level_id=level_id, units="mm")
    if auditor.has_errors:
        ex.warnings.append(f"{file_rel}: ezdxf audit reported {len(auditor.errors)} errors "
                           f"({len(auditor.fixes)} fixes applied)")

    insunits = doc.header.get("$INSUNITS", 0)
    mpu = metres_per_unit_from_insunits(insunits)
    if mpu is None:
        ex.warnings.append(f"{file_rel}: $INSUNITS={insunits} gives no unit; no scale source")
    else:
        ex.scale = {"metres_per_unit": mpu, "method": "dxf_insunits", "confidence": 1.0,
                    "evidence": B.evidence(file_rel, "vector", 1.0, entity=f"$INSUNITS={insunits}")}
    ex.units = str(dxf_units.decode(insunits) or "unit")
    msp = doc.modelspace()

    # Walls first: their minimum corner is the building origin.
    raw_walls = []
    for ent in msp.query("LWPOLYLINE"):
        if _layer_of(ent) != blocks.LAYER_WALLS:
            continue
        pts = [(float(p[0]), float(p[1])) for p in ent.get_points("xy")]
        if len(pts) == 5 and G.distance(pts[0], pts[-1]) < 1e-9:
            pts = pts[:4]
        if len(pts) != 4:
            ex.warnings.append(f"{file_rel}: LWPOLYLINE:{ent.dxf.handle} on {blocks.LAYER_WALLS} has {len(pts)} "
                               "corners, not a wall rectangle; skipped")
            continue
        raw_walls.append((ent, pts))
    if mpu is None:
        return ex
    if raw_walls:
        box = G.bbox([c for _, pts in raw_walls for c in pts])
        origin = (box[0], box[1])
    else:
        origin = (0.0, 0.0)
        ex.warnings.append(f"{file_rel}: no wall rectangles on layer {blocks.LAYER_WALLS}")
    ex.transform_to_building = [mpu, 0.0, float(-mpu * origin[0]) + 0.0, 0.0, mpu, float(-mpu * origin[1]) + 0.0]
    to_b = ex.transform_to_building

    def tb(p) -> tuple[float, float]:
        # Plain floats (ezdxf hands out numpy scalars) so the JSON stays clean.
        x, y = G.apply_affine(to_b, (float(p[0]), float(p[1])))
        return G.snap_point((x, y), 6)

    for ent, pts in raw_walls:
        start, end, thickness = G.rectangle_to_centerline([tb(p) for p in pts])
        entity = f"LWPOLYLINE:{ent.dxf.handle}"
        ex.walls.append(WallItem(start=start, end=end, thickness=G.snap(thickness, 6),
                                 box=[round(float(v), 3) for v in G.bbox(pts)], entity=entity,
                                 evidence=B.evidence(file_rel, "vector", 1.0, layer=blocks.LAYER_WALLS, entity=entity)))

    # Block inserts: openings and furniture.
    for ent in msp.query("INSERT"):
        layer = _layer_of(ent)
        if layer in (blocks.LAYER_DOORS, blocks.LAYER_WINDOWS):
            ex.openings.append(_opening_from_insert(doc, ent, layer, mpu, tb, file_rel))
        elif layer == blocks.LAYER_FURNITURE:
            ex.furniture.append(_furniture_from_insert(doc, ent, mpu, tb, ex))

    # Texts.
    for ent in msp.query("TEXT MTEXT"):
        if ent.dxftype() == "TEXT":
            text = ent.dxf.text
            box = _text_box_mm(ent)
            height = float(ent.dxf.height)
            rotation = float(ent.dxf.rotation)
        else:
            text = ent.plain_text()
            height = float(ent.dxf.char_height)
            rotation = float(ent.dxf.rotation)
            x, y = ent.dxf.insert.x, ent.dxf.insert.y
            box = [x, y - height, x + 0.7 * height * len(text), y]  # rough: MTEXT has no cheap size
        entity = f"{ent.dxftype()}:{ent.dxf.handle}"
        item = TextItem(text=text, start=(ent.dxf.insert.x, ent.dxf.insert.y), box=box, rotation_deg=rotation,
                        entity=entity, height=height, role=text_role(text),
                        evidence=B.evidence(file_rel, "vector", 1.0, layer=ent.dxf.layer, entity=entity, text=text))
        ex.texts.append(item)
        if item.role == "title":
            if ex.title is None or height > ex.title.height:
                ex.title = item
        elif item.role == "scale":
            ex.scale_text = item
        elif item.role == "room_label":
            ex.labels.append(item)

    # Dimensions.
    for ent in msp.query("DIMENSION"):
        if _layer_of(ent) != blocks.LAYER_DIMENSIONS:
            continue
        if ent.dimtype not in (0, 1):
            ex.warnings.append(f"{file_rel}: DIMENSION:{ent.dxf.handle} has dimtype {ent.dimtype}; only linear "
                               "dimensions are read")
            continue
        if ent.dimtype == 0 and not ent.dxf.hasattr("angle"):
            # A DWG converted by LibreDWG loses the angle of rotated dimensions (docs/milestone7.md §0): recover it
            # from the dimension line drawn in the *D block (in memory only), as the generic DXF reader does.
            from wenart.ingest.dxf_generic import dimension_angle_from_block

            angle = dimension_angle_from_block(ent)
            if angle is not None:
                ent.dxf.angle = angle
        span_units, measured_units = _linear_dimension_span(ent)
        p1_b, p2_b = tb(span_units[0]), tb(span_units[1])
        measured = measured_units * mpu
        printed = _dimension_printed_text(ent, measured_units)
        mid = ent.dxf.get("text_midpoint") or ent.dxf.defpoint
        try:
            text_height = float(ent.override().get("dimtxt", 200.0)) or 200.0
        except Exception:  # noqa: BLE001
            text_height = 200.0
        half_w = 0.375 * text_height * max(len(printed), 1)
        entity = f"DIMENSION:{ent.dxf.handle}"
        ex.dimensions.append(DimensionItem(
            p1=p1_b, p2=p2_b, measured=G.snap(measured, 6), printed=printed, printed_value=parse_number(printed),
            box=[round(v, 3) for v in (mid.x - half_w, mid.y - text_height / 2, mid.x + half_w, mid.y + text_height / 2)],
            entity=entity, evidence=B.evidence(file_rel, "vector", 1.0, layer=blocks.LAYER_DIMENSIONS, entity=entity,
                                               text=printed), tick_count=2))
    return ex


def _linear_dimension_span(ent) -> tuple[list[tuple[float, float]], float]:
    """End points (drawing units) of the measured span of a linear DIMENSION and its length.

    Rotated dimensions (dimtype 0) measure along ``dxf.angle``: ezdxf's ``get_measurement()``
    (``linear_measurement`` in ezdxf 1.4.4) projects defpoint2 -> defpoint3 onto that
    direction, which is what CAD prints. The span end points are the definition points
    projected onto the dimension line (through ``dxf.defpoint``), so wall linking sees the
    printed span even when the definition points lie on different faces.

    Aligned dimensions (dimtype 1) measure the distance of the definition points. ezdxf
    would project them onto ``dxf.angle`` as well, but DXF files store no meaningful angle
    for aligned dimensions, so the distance is computed here.
    """
    p2, p3 = ent.dxf.defpoint2, ent.dxf.defpoint3
    a, b = (float(p2.x), float(p2.y)), (float(p3.x), float(p3.y))
    if ent.dimtype == 1:
        return [a, b], G.distance(a, b)
    angle = math.radians(float(ent.dxf.get("angle", 0.0)))
    ux, uy = math.cos(angle), math.sin(angle)
    base = ent.dxf.defpoint
    bx, by = float(base.x), float(base.y)
    projected = []
    for x, y in (a, b):
        t = (x - bx) * ux + (y - by) * uy
        projected.append((bx + t * ux, by + t * uy))
    return projected, float(ent.get_measurement())


def _dimension_printed_text(ent, measured_units: float) -> str:
    """What the drawing shows: the text override, or the measurement formatted with the
    dimension style (``dimlfac`` scales drawing units to the printed unit, 0.001 for a
    millimetre drawing printed in metres; the DXF default is 1.0)."""
    text = ent.dxf.text
    if text and text != "<>":
        return text
    try:
        factor = float(ent.override().get("dimlfac", 1.0))
    except Exception:  # noqa: BLE001 - missing dimstyle etc.
        factor = 1.0
    return format_metres(measured_units * factor)


def _opening_from_insert(doc, ent, layer: str, mpu: float, tb, file_rel: str) -> OpeningItem:
    name = ent.dxf.name
    info = blocks.opening_from_block(name)
    status = "verified"
    if info is not None:
        kind, width = info
    else:
        kind = "door" if layer == blocks.LAYER_DOORS else "window"
        extent = _block_extent(doc, name)
        width = (extent[2] - extent[0]) * mpu * abs(ent.dxf.xscale) if extent else 0.0
        status = "unverified"
    rotation = G.normalise_angle(float(ent.dxf.rotation))
    center = tb((ent.dxf.insert.x, ent.dxf.insert.y))
    swing = None
    if kind == "door":
        # The door block opens towards its local +Y.
        dx, dy = G.rotate_point((0.0, DOOR_SWING_PROBE), rotation)
        swing = (center[0] + dx, center[1] + dy)
    entity = f"INSERT:{ent.dxf.handle}"
    # Symbol box in drawing units: door = leaf + swing square, window = width x symbol depth.
    w_units = width / mpu
    if kind == "door":
        local = [(-w_units / 2, 0.0), (w_units / 2, 0.0), (w_units / 2, w_units), (-w_units / 2, w_units)]
    else:
        d = blocks.WINDOW_SYMBOL_DEPTH / mpu / 2
        local = [(-w_units / 2, -d), (w_units / 2, -d), (w_units / 2, d), (-w_units / 2, d)]
    ix, iy = ent.dxf.insert.x, ent.dxf.insert.y
    corners = [G.rotate_point((ix + x, iy + y), rotation, (ix, iy)) for x, y in local]
    return OpeningItem(kind=kind, width=width, center=center, rotation_deg=rotation,
                       box=[round(float(v), 3) for v in G.bbox(corners)], entity=entity,
                       evidence=B.evidence(file_rel, "vector", 1.0, layer=layer, entity=entity, block=name),
                       swing_point=swing, block=name, status=status)


def _drawn_footprint(doc, name: str, mpu: float, sx: float, sy: float):
    """``(size in metres, centre offset in block units)`` of what the block draws, scaled by
    the insert: the rectangle inside the block, else the extent of its geometry, else
    ``(None, (0, 0))`` for a block without geometry."""
    rect = _block_rectangle(doc, name)
    if rect is not None:
        box = G.bbox(rect)
    else:
        box = _block_extent(doc, name)
        if box is None:
            return None, (0.0, 0.0)
    size = ((box[2] - box[0]) * mpu * sx, (box[3] - box[1]) * mpu * sy)
    offset = (((box[0] + box[2]) / 2) * sx, ((box[1] + box[3]) / 2) * sy)
    return size, offset


def _furniture_from_insert(doc, ent, mpu: float, tb, ex: LevelExtraction) -> FurnitureItem:
    """Furniture piece from a MOBILYA insert. The footprint is what the block draws (vector
    geometry first); the BLOCKS table only names the type. Disagreements go to
    ``ex.conflicts``, missing geometry to ``ex.warnings``."""
    name = ent.dxf.name
    handle = f"INSERT:{ent.dxf.handle}"
    ftype = blocks.furniture_type(name)
    rotation = G.normalise_angle(float(ent.dxf.rotation))
    sx, sy = abs(float(ent.dxf.xscale)), abs(float(ent.dxf.yscale))
    drawn, offset_local = _drawn_footprint(doc, name, mpu, sx, sy)
    table = blocks.furniture_size(name)
    status = "verified" if table is not None else "unverified"
    if drawn is not None:
        size = drawn
        if table is not None:
            expected = (table[0] * sx, table[1] * sy)
            if abs(drawn[0] - expected[0]) > SIZE_TOLERANCE_M or abs(drawn[1] - expected[1]) > SIZE_TOLERANCE_M:
                # Name and geometry disagree: the drawn footprint counts, the name no longer
                # identifies our block with certainty, so the type lookup is unverified.
                status = "unverified"
                ex.conflicts.append({
                    "kind": "type_disagreement", "element_ids": [],
                    "description": f"{ex.file}: block {name} ({handle}) is drawn {drawn[0]:.2f} x {drawn[1]:.2f} m "
                                   f"but the block table says {expected[0]:.2f} x {expected[1]:.2f} m",
                    "resolution": "drawn footprint kept (vector geometry), piece marked unverified"})
    elif table is not None:
        # Nothing drawn: the table size is the only footprint source, which the document cannot confirm.
        size = (table[0] * sx, table[1] * sy)
        status = "unverified"
        ex.warnings.append(f"{ex.file}: block {name} ({handle}) has no drawn footprint; table size "
                           f"{size[0]:.2f} x {size[1]:.2f} m used, piece marked unverified")
    else:
        size = (0.0, 0.0)
        ex.warnings.append(f"{ex.file}: block {name} ({handle}) has no drawn footprint")
    ix, iy = ent.dxf.insert.x, ent.dxf.insert.y
    ox, oy = G.rotate_point(offset_local, rotation)
    center_units = (ix + ox, iy + oy)
    center = tb(center_units)
    corners = G.rotated_rectangle(center_units, (size[0] / mpu, size[1] / mpu), rotation)
    return FurnitureItem(type=ftype, type_raw=name, center=center, size=(G.snap(size[0], 6), G.snap(size[1], 6)),
                         rotation_deg=rotation, front_deg=G.front_direction_deg(rotation) if status == "verified" else None,
                         box=[round(float(v), 3) for v in G.bbox(corners)], entity=handle,
                         evidence=B.evidence(ex.file, "vector", 1.0, layer=blocks.LAYER_FURNITURE, entity=handle, block=name),
                         status=status)
