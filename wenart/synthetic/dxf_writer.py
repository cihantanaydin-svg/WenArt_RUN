"""Write one level as a DXF file (R2010, millimetres, model space) the way a
Turkish architectural office would draw it: wall rectangles on ``DUVAR``,
door/window block inserts on ``KAPI``/``PENCERE``, room labels on ``YAZI``,
aligned dimensions on ``OLCU`` and furniture block inserts on ``MOBILYA``.

The writer returns a ``PageRecord`` with the entity handle of every element so
the truth files can point at the exact DXF entity (``LWPOLYLINE:<handle>``).
Output bytes are deterministic: the header date and GUID variables are fixed.
"""
from __future__ import annotations

from pathlib import Path

import ezdxf
from ezdxf.tools.text_size import text_size

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
