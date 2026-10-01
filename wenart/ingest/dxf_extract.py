"""DXF model space -> ``LevelExtraction`` (docs/milestone2.md §2, conventions).

What is read, by layer (names matched case-insensitively):
- ``DUVAR``: closed 4-corner LWPOLYLINEs are wall rectangles; long axis =
  centre line, short side = thickness (``geometry.rectangle_to_centerline``).
- ``KAPI`` / ``PENCERE``: INSERTs. The block name gives type and clear width
  (``KAPI_90`` -> door 0.90 m). Unknown names fall back to the layer for the
  type and the block's drawn extent for the width, marked ``unverified``.
- ``MOBILYA``: INSERTs. Block name -> type via ``wenart.synthetic.blocks.BLOCKS``
  (a lookup, never a guess); unknown names -> ``unknown`` + ``unverified`` with
  the footprint read from the rectangle inside the block definition.
- ``YAZI``: TEXT/MTEXT; roles title / scale / dimension / room label.
- ``OLCU``: DIMENSION; measured = distance of the two definition points, printed
  = text override or the measurement formatted with the dimension style.

Units: ``$INSUNITS`` gives metres per drawing unit (4 = mm). The building
origin is the minimum corner of all wall rectangles, so the transform is
``[s, 0, -s*x0, 0, s, -s*y0]``.
"""
from __future__ import annotations

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
from wenart.synthetic.dxf_writer import dimension_printed_text

# Drawn block size vs the BLOCKS table: larger differences are reported.
SIZE_WARNING_M = 0.01


def read_dxf(path: str | Path):
    """``(doc, auditor)`` via ezdxf's recover mode (tolerant of slightly broken files)."""
    return recover.readfile(str(path))


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
            item, warning = _furniture_from_insert(doc, ent, mpu, tb, file_rel)
            ex.furniture.append(item)
            if warning:
                ex.warnings.append(warning)

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
        p2, p3 = ent.dxf.defpoint2, ent.dxf.defpoint3
        p1_b, p2_b = tb((p2.x, p2.y)), tb((p3.x, p3.y))
        measured = G.distance(p1_b, p2_b)
        try:
            printed = dimension_printed_text(ent)
        except Exception:  # noqa: BLE001 - missing dimstyle etc.
            printed = ent.dxf.text if ent.dxf.text and ent.dxf.text != "<>" else f"{measured:.2f}".replace(".", ",")
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


def _furniture_from_insert(doc, ent, mpu: float, tb, file_rel: str) -> tuple[FurnitureItem, Optional[str]]:
    name = ent.dxf.name
    ftype = blocks.furniture_type(name)
    rotation = G.normalise_angle(float(ent.dxf.rotation))
    sx, sy = abs(float(ent.dxf.xscale)), abs(float(ent.dxf.yscale))
    rect = _block_rectangle(doc, name)
    warning = None
    offset_local = (0.0, 0.0)
    drawn = None
    if rect is not None:
        rbox = G.bbox(rect)
        drawn = ((rbox[2] - rbox[0]) * mpu * sx, (rbox[3] - rbox[1]) * mpu * sy)
        offset_local = (((rbox[0] + rbox[2]) / 2) * sx, ((rbox[1] + rbox[3]) / 2) * sy)
    else:
        extent = _block_extent(doc, name)
        if extent is not None:
            drawn = ((extent[2] - extent[0]) * mpu * sx, (extent[3] - extent[1]) * mpu * sy)
            offset_local = (((extent[0] + extent[2]) / 2) * sx, ((extent[1] + extent[3]) / 2) * sy)
    table = blocks.furniture_size(name)
    if table is not None:
        size = (table[0] * sx, table[1] * sy)
        status = "verified"
        if drawn is not None and (abs(drawn[0] - size[0]) > SIZE_WARNING_M or abs(drawn[1] - size[1]) > SIZE_WARNING_M):
            warning = (f"{file_rel}: block {name} (INSERT:{ent.dxf.handle}) is drawn {drawn[0]:.2f} x {drawn[1]:.2f} m "
                       f"but the block table says {size[0]:.2f} x {size[1]:.2f} m; table size used")
    else:
        size = drawn if drawn is not None else (0.0, 0.0)
        status = "unverified"
        if drawn is None:
            warning = f"{file_rel}: block {name} (INSERT:{ent.dxf.handle}) has no drawn footprint"
    ix, iy = ent.dxf.insert.x, ent.dxf.insert.y
    ox, oy = G.rotate_point(offset_local, rotation)
    center_units = (ix + ox, iy + oy)
    center = tb(center_units)
    corners = G.rotated_rectangle(center_units, (size[0] / mpu, size[1] / mpu), rotation)
    entity = f"INSERT:{ent.dxf.handle}"
    item = FurnitureItem(type=ftype, type_raw=name, center=center, size=(G.snap(size[0], 6), G.snap(size[1], 6)),
                         rotation_deg=rotation, front_deg=G.front_direction_deg(rotation) if status == "verified" else None,
                         box=[round(float(v), 3) for v in G.bbox(corners)], entity=entity,
                         evidence=B.evidence(file_rel, "vector", 1.0, layer=blocks.LAYER_FURNITURE, entity=entity, block=name),
                         status=status)
    return item, warning
