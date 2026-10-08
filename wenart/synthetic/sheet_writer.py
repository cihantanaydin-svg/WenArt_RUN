"""Write the synthetic-07 sheet as one DXF (R2000, model space, centimetres, ``$INSUNITS`` = 5).

What: ``write_sheet_dxf(project, path)`` draws every ``Prim`` of ``wenart.synthetic.sheet`` as a DXF entity and returns a
``SheetRecord``: the entity string (``LWPOLYLINE:3F``) of every prim that has a role, which the truth files use as
evidence. Block definitions (doors, windows, furniture, the stair, a tree, the north arrow) come from the same prim
tables the boxes are computed from.

Why: the sheet is the test input of the sheets stage (docs/milestone10.md §3.1): regions, titles, units, heights and
exterior evidence all have to be readable from this one file, and the truth has to name the exact entities.

How: ``ezdxf`` with fixed header metadata (two runs give identical bytes) and the classes registered in sorted order, as
in ``dxf_writer``. Entities are created in a fixed order: frame, then the drawings in construction order (each: prims,
then its title), then the stray LINE last. The DWG copy is made by LibreDWG's ``dxf2dwg`` in ``generate`` (R2000).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import ezdxf

from wenart.synthetic import sheet as S
from wenart.synthetic.sheet import CM, Prim, SheetProject, rnd

_FIXED_META_OPTION = "write_fixed_meta_data_for_testing"
LINETYPE_SCALE = 20.0           # the stock linetypes are a few drawing units long; the drawing unit is a centimetre
HATCH_COLOUR = 7


@dataclass
class SheetRecord:
    """Where the entities went: ``entities['<drawing key>/<role>']`` = entity strings in creation order."""
    entities: dict = field(default_factory=dict)
    frame: str = ""
    stray: str = ""

    def one(self, key: str, role: str) -> str:
        found = self.entities[f"{key}/{role}"]
        if len(found) != 1:
            raise KeyError(f"{key}/{role}: {len(found)} entities")
        return found[0]

    def all(self, key: str, role: str) -> list[str]:
        return list(self.entities.get(f"{key}/{role}", []))


def _entity_string(entity) -> str:
    return f"{entity.dxftype()}:{entity.dxf.handle}"


def _emit(target, prim: Prim, at, scale: float, origin=(0.0, 0.0)):
    """Create the entity of ``prim`` in ``target`` (model space or a block). ``scale`` metres -> drawing units."""
    def pt(p):
        return (rnd(origin[0] + scale * p[0], 6), rnd(origin[1] + scale * p[1], 6))

    attribs = {"layer": prim.layer}
    if prim.linetype:
        attribs["linetype"] = prim.linetype
    if prim.kind == "line":
        return target.add_line(pt(prim.pts[0]), pt(prim.pts[1]), dxfattribs=attribs)
    if prim.kind == "poly":
        return target.add_lwpolyline([pt(p) for p in prim.pts], close=prim.closed, dxfattribs=attribs)
    if prim.kind == "circle":
        return target.add_circle(pt(prim.pts[0]), rnd(scale * prim.radius, 6), dxfattribs=attribs)
    if prim.kind == "arc":
        return target.add_arc(pt(prim.pts[0]), rnd(scale * prim.radius, 6), prim.angles[0], prim.angles[1], dxfattribs=attribs)
    if prim.kind == "hatch":
        entity = target.add_hatch(color=HATCH_COLOUR, dxfattribs=attribs)
        entity.set_pattern_fill(prim.pattern, scale=prim.scale)
        entity.paths.add_polyline_path([pt(p) for p in prim.pts], is_closed=True)
        return entity
    if prim.kind == "text":
        entity = target.add_text(prim.text, height=prim.height, dxfattribs=attribs)
        entity.set_placement(pt(prim.pts[0]))
        return entity
    if prim.kind == "mtext":
        # dxf2dwg keeps DXF code 40 of an MTEXT as the reference-rectangle width (height 0 in the DWG): the height is
        # also stated inline, as in synthetic-06.
        return target.add_mtext(f"\\H{prim.height:g};{prim.text}", dxfattribs={
            **attribs, "char_height": prim.height, "insert": pt(prim.pts[0]), "attachment_point": 1})
    if prim.kind == "insert":
        return target.add_blockref(prim.block, pt(prim.pts[0]), dxfattribs={**attribs, "rotation": prim.rotation})
    raise ValueError(prim.kind)


def _used_blocks(project: SheetProject) -> list[str]:
    return sorted({p.block for d in project.drawings for p in d.prims if p.kind == "insert"})


def write_sheet_dxf(project: SheetProject, path: Path) -> SheetRecord:
    previous = getattr(ezdxf.options, _FIXED_META_OPTION)
    setattr(ezdxf.options, _FIXED_META_OPTION, True)
    try:
        return _write(project, Path(path))
    finally:
        setattr(ezdxf.options, _FIXED_META_OPTION, previous)


def _write(project: SheetProject, path: Path) -> SheetRecord:
    doc = ezdxf.new("R2000", setup=True)
    doc.header["$INSUNITS"] = S.INSUNITS
    doc.header["$MEASUREMENT"] = 1              # metric
    doc.header["$LUNITS"] = 2                   # decimal
    doc.header["$LTSCALE"] = LINETYPE_SCALE
    x0, y0, x1, y1 = S.FRAME
    (sx0, sy0), (sx1, sy1) = S.STRAY
    doc.header["$EXTMIN"] = (min(x0, sx0), min(y0, sy0), 0.0)
    doc.header["$EXTMAX"] = (max(x1, sx1), max(y1, sy1), 0.0)
    for name, colour in S.LAYERS:
        doc.layers.add(name, color=colour)
    for name in _used_blocks(project):
        block = doc.blocks.new(name)
        for prim in S.BLOCK_TABLE[name]:
            _emit(block, prim, None, CM)
    msp = doc.modelspace()
    record = SheetRecord()
    frame = msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": S.L_FRAME})
    record.frame = _entity_string(frame)
    for drawing in project.drawings:
        for prim in drawing.prims + ([drawing.title] if drawing.title else []):
            entity = _emit(msp, prim, None, CM, drawing.origin)
            if prim.role:
                record.entities.setdefault(f"{drawing.key}/{prim.role}", []).append(_entity_string(entity))
    stray = msp.add_line((sx0, sy0), (sx1, sy1), dxfattribs={"layer": "0"})
    record.stray = _entity_string(stray)
    for dxftype in sorted(doc.entitydb.dxf_types_in_use()):
        doc.classes.add_class(dxftype)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return record
