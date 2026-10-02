"""Write levels as a vector PDF (A3 landscape, scale 1:100, one level per page).

Drawing conventions (docs/milestone2.md): 1 m = 10 mm on paper = 28.3465 pt;
page origin bottom-left; the plan sits at a fixed offset ``(X0, Y0)`` that the
truth file records in the page transform. Line widths: walls 0.5 pt, openings
and dimension lines 0.35 pt, furniture 0.25 pt, page border 1.0 pt. Text 8-10 pt.

Font: the spec says Helvetica, but reportlab's built-in Helvetica cannot encode
``İ``, ``Ş`` or ``Ğ`` (WinAnsi only). We embed DejaVu Sans (bundled with
matplotlib, same metrics on every machine) so the Turkish titles and labels
survive text extraction. docs/synthetic.md documents this.

Entity references for evidence:
- ``path:<n>``: n counts path drawing operations (rect / line / drawPath) in
  emission order, starting at 0 on every page. pdfplumber does not expose the
  content-stream order, so the ingest side should match by geometry (the page
  record carries every box) and treat the index as a label.
- ``char:<n>``: index of the text's first character in ``page.chars`` as
  pdfplumber returns them (reportlab emits text in drawing order, spaces
  included; verified in tests/test_synthetic.py).
"""
from __future__ import annotations

import math
import os
from pathlib import Path

import matplotlib
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas

from wenart import geometry as G
from wenart.synthetic import blocks
from wenart.synthetic.model import Dimension, Level, PageRecord

PT_PER_M = 72.0 / 25.4 * 10.0        # 28.3465 pt per metre at 1:100
PAGE_W, PAGE_H = 1190.55, 841.89     # A3 landscape in points
TITLE_ROOM_M = 1.5                   # metres above the plan reserved for the title line
DIM_ROOM_M = 1.3                     # metres below/left of the plan reserved for dimensions
BORDER_INSET = 15.0

FONT_NAME = "DejaVuSans"
FONT_FILE = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", "DejaVuSans.ttf")
SIZE_LABEL = 8.0
SIZE_TITLE = 10.0
SIZE_SCALE = 9.0
SIZE_DIM = 8.0
SCALE_TEXT_GAP = 1.0 * PT_PER_M  # "ÖLÇEK 1/100" starts this far right of the title's end

LW_WALL = 0.5
LW_OPENING = 0.35
LW_FURNITURE = 0.25
LW_DIM = 0.35
LW_BORDER = 1.0

DIM_TICK = 0.08       # metres, 45 degree tick half-length
DIM_EXT_GAP = 0.05    # metres, gap between the building and the extension line
DIM_EXT_OVER = 0.10   # metres, extension line beyond the dimension line
DIM_TEXT_GAP = 2.0    # points between dimension line and text


def _register_font() -> None:
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))


def plan_offset(level: Level) -> tuple[float, float]:
    """Page points of the building origin: the plan (with its title and
    dimension margins) is centred on the page; rounded to 0.1 pt."""
    box = level.outer_box()
    width_m = box[2] - box[0]
    height_m = box[3] - box[1]
    x0 = (PAGE_W - (width_m + DIM_ROOM_M) * PT_PER_M) / 2.0 + DIM_ROOM_M * PT_PER_M
    y0 = (PAGE_H - (height_m + TITLE_ROOM_M + DIM_ROOM_M) * PT_PER_M) / 2.0 + DIM_ROOM_M * PT_PER_M
    return (round(x0, 1), round(y0, 1))


def building_to_page_affine(level: Level) -> list[float]:
    """Building metres -> page points for this level's page."""
    x0, y0 = plan_offset(level)
    return G.affine_from_scale_translate(PT_PER_M, PT_PER_M, x0, y0)


class _Page:
    """Tracks path and char indices while one page is drawn."""

    def __init__(self, c: rl_canvas.Canvas, offset: tuple[float, float]) -> None:
        self.c = c
        self.x0, self.y0 = offset
        self.path_index = 0
        self.char_index = 0

    def to_pt(self, p) -> tuple[float, float]:
        return (self.x0 + p[0] * PT_PER_M, self.y0 + p[1] * PT_PER_M)

    # -- paths -------------------------------------------------------------
    def line(self, a, b, lw: float) -> int:
        self.c.setLineWidth(lw)
        ax, ay = self.to_pt(a)
        bx, by = self.to_pt(b)
        self.c.line(ax, ay, bx, by)
        self.path_index += 1
        return self.path_index - 1

    def polygon(self, pts, lw: float) -> int:
        """Closed polygon as one path (moveTo, lineTo..., close)."""
        self.c.setLineWidth(lw)
        path = self.c.beginPath()
        first = self.to_pt(pts[0])
        path.moveTo(*first)
        for p in pts[1:]:
            path.lineTo(*self.to_pt(p))
        path.close()
        self.c.drawPath(path, stroke=1, fill=0)
        self.path_index += 1
        return self.path_index - 1

    def arc(self, center, radius_m: float, start_deg: float, extent_deg: float, lw: float) -> int:
        self.c.setLineWidth(lw)
        cx, cy = self.to_pt(center)
        r = radius_m * PT_PER_M
        path = self.c.beginPath()
        path.arc(cx - r, cy - r, cx + r, cy + r, start_deg, extent_deg)
        self.c.drawPath(path, stroke=1, fill=0)
        self.path_index += 1
        return self.path_index - 1

    # -- text --------------------------------------------------------------
    def text(self, text: str, at_pt, size: float, rotation_deg: float = 0.0) -> tuple[int, list[float]]:
        """Draw text with its left baseline at ``at_pt`` (points). Returns (char index, box)."""
        x, y = at_pt
        self.c.setFont(FONT_NAME, size)
        if rotation_deg:
            self.c.saveState()
            self.c.translate(x, y)
            self.c.rotate(rotation_deg)
            self.c.drawString(0, 0, text)
            self.c.restoreState()
        else:
            self.c.drawString(x, y, text)
        index = self.char_index
        self.char_index += len(text)
        return index, text_box(text, at_pt, size, rotation_deg)


def text_box(text: str, at_pt, size: float, rotation_deg: float = 0.0) -> list[float]:
    """Box in points of a text with left baseline at ``at_pt`` (font ascent/descent, rotated)."""
    _register_font()
    width = pdfmetrics.stringWidth(text, FONT_NAME, size)
    ascent, descent = pdfmetrics.getAscentDescent(FONT_NAME, size)
    x, y = at_pt
    corners = [(x, y + descent), (x + width, y + descent), (x + width, y + ascent), (x, y + ascent)]
    if rotation_deg:
        corners = [G.rotate_point(c, rotation_deg, (x, y)) for c in corners]
    return [round(v, 3) for v in G.bbox(corners)]


def _draw_door(pg: _Page, opening) -> tuple[int, int]:
    """Leaf line + swing arc, same geometry as the DXF block KAPI_<w>."""
    w = opening.width
    cx, cy = opening.center
    rot = opening.rotation_deg
    hinge = G.rotate_point((cx - w / 2, cy), rot, (cx, cy))
    tip = G.rotate_point((cx - w / 2, cy + w), rot, (cx, cy))
    first = pg.line(hinge, tip, LW_OPENING)
    last = pg.arc(hinge, w, rot, 90.0, LW_OPENING)
    return first, last


def _draw_window(pg: _Page, opening) -> tuple[int, int]:
    w = opening.width
    d = blocks.WINDOW_SYMBOL_DEPTH / 2
    cx, cy = opening.center
    rot = opening.rotation_deg

    def p(x, y):
        return G.rotate_point((cx + x, cy + y), rot, (cx, cy))

    first = pg.line(p(-w / 2, -d), p(w / 2, -d), LW_OPENING)
    pg.line(p(-w / 2, d), p(w / 2, d), LW_OPENING)
    pg.line(p(-w / 2, -d), p(-w / 2, d), LW_OPENING)
    last = pg.line(p(w / 2, -d), p(w / 2, d), LW_OPENING)
    return first, last


def _draw_furniture(pg: _Page, piece) -> tuple[int, int]:
    corners = piece.corners()
    first = pg.polygon(corners, LW_FURNITURE)
    # Front marker line, as in the DXF block.
    w, d = piece.size
    inset = min(0.05, d * 0.15)
    a = G.rotate_point((piece.center[0] - w / 4, piece.center[1] - d / 2 + inset), piece.rotation_deg, piece.center)
    b = G.rotate_point((piece.center[0] + w / 4, piece.center[1] - d / 2 + inset), piece.rotation_deg, piece.center)
    last = pg.line(a, b, LW_FURNITURE)
    return first, last


def _draw_dimension(pg: _Page, dim: Dimension) -> tuple[int, int, int, list[float]]:
    """Dimension line with 45-degree ticks, extension lines and the printed text.
    Returns (first path index, last path index, char index, text box)."""
    nx, ny = G.unit_normal_left(dim.p1, dim.p2)
    off = dim.offset
    sign = 1.0 if off >= 0 else -1.0
    a = (dim.p1[0] + nx * off, dim.p1[1] + ny * off)
    b = (dim.p2[0] + nx * off, dim.p2[1] + ny * off)
    first = pg.line(a, b, LW_DIM)
    # Extension lines from just outside the building to just beyond the dimension line.
    for p, q in ((dim.p1, a), (dim.p2, b)):
        start = (p[0] + nx * sign * DIM_EXT_GAP, p[1] + ny * sign * DIM_EXT_GAP)
        end = (q[0] + nx * sign * DIM_EXT_OVER, q[1] + ny * sign * DIM_EXT_OVER)
        pg.line(start, end, LW_DIM)
    # Ticks: short 45-degree strokes at both ends.
    angle = G.segment_angle_deg(dim.p1, dim.p2)
    tick = G.rotate_point((DIM_TICK, 0.0), angle + 45.0)
    last = first
    for q in (a, b):
        last = pg.line((q[0] - tick[0], q[1] - tick[1]), (q[0] + tick[0], q[1] + tick[1]), LW_DIM)
    # Text on the far side of the dimension line, centred, along the line.
    text = dim.printed
    width = pdfmetrics.stringWidth(text, FONT_NAME, SIZE_DIM)
    mid = G.segment_midpoint(a, b)
    mid_pt = pg.to_pt(mid)
    ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    # Left-normal side in page points (the "far" side for both chains is the left normal).
    gap = DIM_TEXT_GAP
    base = (mid_pt[0] - ux * width / 2 + nx * gap, mid_pt[1] - uy * width / 2 + ny * gap)
    char_index, box = pg.text(text, base, SIZE_DIM, rotation_deg=angle if abs(angle) > 1e-9 else 0.0)
    return first, last, char_index, box


def write_pdf(pages: list[dict], path: Path, file_rel: str) -> list[PageRecord]:
    """Write one PDF with one page per entry of ``pages``. Each entry is a dict
    ``{"level", "title_raw", "page_class", "openings", "furniture", "dimensions"}``
    (the lists may be subsets of the level's; see projects.PageSpec)."""
    _register_font()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # invariant=1: fixed creation date and document id -> byte-identical output.
    c = rl_canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H), invariant=1)
    c.setTitle(Path(file_rel).stem)
    c.setAuthor("wenart synthetic generator")
    records = []
    for number, spec in enumerate(pages, start=1):
        records.append(_draw_page(c, spec, number, file_rel))
        c.showPage()
    c.save()
    return records


def _draw_page(c: rl_canvas.Canvas, spec: dict, number: int, file_rel: str) -> PageRecord:
    level: Level = spec["level"]
    title_raw: str = spec["title_raw"]
    pg = _Page(c, plan_offset(level))
    record = PageRecord(
        file=file_rel, page=number, kind="vector", page_class=spec["page_class"], level_id=level.id,
        units="pt", size=[PAGE_W, PAGE_H], scale_metres_per_unit=1.0 / PT_PER_M, transform_kind="affine",
        building_to_page=building_to_page_affine(level), title_raw=title_raw,
    )
    c.setStrokeGray(0)

    # Page border (1.0 pt, not a wall).
    c.setLineWidth(LW_BORDER)
    c.rect(BORDER_INSET, BORDER_INSET, PAGE_W - 2 * BORDER_INSET, PAGE_H - 2 * BORDER_INSET, stroke=1, fill=0)
    pg.path_index += 1

    # Walls: closed rectangles with the wall line width.
    for wall in level.walls:
        corners = wall.rectangle()
        idx = pg.polygon(corners, LW_WALL)
        entity = f"path:{idx}"
        box = [round(v, 3) for v in G.bbox([pg.to_pt(p) for p in corners])]
        record.entities[wall.id] = entity
        record.boxes[wall.id] = box
        record.walls.append({"id": wall.id, "box": box, "entity": entity})

    # Openings
    for opening in spec["openings"]:
        if opening.kind == "door":
            first, last = _draw_door(pg, opening)
        else:
            first, last = _draw_window(pg, opening)
        entity = f"path:{first}"
        box = _symbol_box_pt(pg, opening.symbol_corners())
        record.entities[opening.id] = entity
        record.boxes[opening.id] = box
        record.symbols.append({"id": opening.id, "type": opening.kind, "block": opening.block, "box": box,
                               "rotation_deg": opening.rotation_deg, "entity": entity, "paths": [first, last]})

    # Furniture
    for piece in spec["furniture"]:
        first, last = _draw_furniture(pg, piece)
        entity = f"path:{first}"
        box = _symbol_box_pt(pg, piece.corners())
        record.entities[piece.id] = entity
        record.boxes[piece.id] = box
        record.symbols.append({"id": piece.id, "type": piece.type, "block": piece.block, "box": box,
                               "rotation_deg": piece.rotation_deg, "entity": entity, "paths": [first, last]})

    # Dimensions
    for dim in spec["dimensions"]:
        first, last, char_index, box = _draw_dimension(pg, dim)
        entity = f"path:{first}"
        record.dimensions.append({"measured": round(dim.measured, 4), "printed": dim.printed, "entity": entity,
                                  "text_entity": f"char:{char_index}", "wall_ids": list(dim.wall_ids),
                                  "box": box, "paths": [first, last]})
        record.texts.append({"text": dim.printed, "box": box, "entity": f"char:{char_index}", "role": "dimension"})

    # Title, scale text, room labels
    title_pt = pg.to_pt(level.title_at)
    idx, box = pg.text(title_raw, title_pt, SIZE_TITLE)
    record.title_entity = f"char:{idx}"
    record.texts.append({"text": title_raw, "box": box, "entity": record.title_entity, "role": "title"})

    title_width = pdfmetrics.stringWidth(title_raw, FONT_NAME, SIZE_TITLE)
    idx, box = pg.text(level.scale_text, (title_pt[0] + title_width + SCALE_TEXT_GAP, title_pt[1]), SIZE_SCALE)
    record.scale_entity = f"char:{idx}"
    record.texts.append({"text": level.scale_text, "box": box, "entity": record.scale_entity, "role": "scale"})

    for room in level.rooms:
        lab = level.labels[room.label_index]
        idx, box = pg.text(lab.label_raw, pg.to_pt(lab.at), SIZE_LABEL)
        entity = f"char:{idx}"
        record.entities[room.id] = entity
        record.boxes[room.id] = box
        record.texts.append({"text": lab.label_raw, "box": box, "entity": entity, "role": "room_label",
                             "element_id": room.id})
    return record


def _symbol_box_pt(pg: _Page, corners) -> list[float]:
    return [round(v, 3) for v in G.bbox([pg.to_pt(p) for p in corners])]
