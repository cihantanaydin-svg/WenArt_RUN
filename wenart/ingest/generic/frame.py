"""Sheet frame blocks: the drawing frame and title block inserted as one block around the plan (real03).

What: ``frame_blocks(page) -> list[dict]`` finds the top-level block inserts of a page that are a sheet frame with
its title block (a legend block: ``MYD - LEJAND`` / ``*U62`` on real03), so the core never reads their lines as
walls, openings or furniture.

Why: a CAD sheet often inserts the frame and title block as one block whose box is the whole sheet. The sheets
stage clusters whole inserts, so such a block is not split off as a title-block region (it holds the plan's box);
its title rows are thin closed rectangles (0.5 m x 4.9 m at the drawing unit) that pass the outline-wall rule, and
real03's only "walls" were title-block rows.

How (all in page units; every rule is geometry, no layer or block name):
- strokes are grouped by their top-level entity (``INSERT:7C135/3`` -> ``INSERT:7C135``); only groups drawn inside a
  block insert (strokes with a block chain) are candidates;
- the group holds a closed axis-aligned rectangle that spans >= ``FRAME_COVER`` (90 %) of the page's extent both
  ways (the sheet frame);
- the frame holds another entity's drawing (a stroke of another group whose box centre lies inside it);
- every other stroke of the group lies in the frame's edge band: within ``FRAME_BAND`` (25 %) of the frame's shorter
  side from one of its edges (title block rows, a logo, notes along the border), or is a frame rectangle itself.

A block whose strokes reach into the middle of the frame is a drawing, not a frame block: it stays.
"""
from __future__ import annotations

import re
from typing import Optional

from wenart.ingest.generic.model import GenericPage, Stroke

FRAME_COVER = 0.90
FRAME_BAND = 0.25
_INDEX_RE = re.compile(r"\[\d+\]$")


def top_entity(stroke_id: str) -> str:
    """``INSERT:4B[2]/3`` -> ``INSERT:4B``, ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``, ``HATCH:5C#0`` -> ``HATCH:5C``
    (the same grouping as ``dxf_generic.stroke_entity``)."""
    head = _INDEX_RE.sub("", stroke_id.split("/")[0].split("#")[0])
    return ":".join(head.split(":")[:2])


def _rect(st: Stroke) -> Optional[tuple[float, float, float, float]]:
    """Box of a closed stroke whose corners form an axis-aligned rectangle."""
    pts = list(st.pts)
    if len(pts) == 5 and pts[0] == pts[-1]:
        pts = pts[:-1]
    if not st.closed and not (len(st.pts) == 5 and st.pts[0] == st.pts[-1]):
        return None
    if len(pts) != 4:
        return None
    xs = sorted({round(p[0], 6) for p in pts})
    ys = sorted({round(p[1], 6) for p in pts})
    if len(xs) != 2 or len(ys) != 2:
        return None
    return (xs[0], ys[0], xs[1], ys[1])


def _in_band(b, frame, band: float) -> bool:
    x0, y0, x1, y1 = frame
    inside = b[0] >= x0 - band * 0.01 and b[1] >= y0 - band * 0.01 and b[2] <= x1 + band * 0.01 and \
        b[3] <= y1 + band * 0.01
    if not inside:
        return False
    return b[2] <= x0 + band or b[0] >= x1 - band or b[3] <= y0 + band or b[1] >= y1 - band


def frame_blocks(page: GenericPage) -> list[dict]:
    """The sheet frame blocks of a page (see the module docstring): ``[{"entity", "block", "layer", "stroke_ids",
    "frame_box", "strokes"}]`` in page units."""
    strokes = [st for st in page.strokes if st.pts]
    if not strokes:
        return []
    boxes = [st.bbox() for st in strokes]
    px0, py0 = min(b[0] for b in boxes), min(b[1] for b in boxes)
    px1, py1 = max(b[2] for b in boxes), max(b[3] for b in boxes)
    pw, ph = px1 - px0, py1 - py0
    if pw <= 0 or ph <= 0:
        return []
    groups: dict[str, list[int]] = {}
    for k, st in enumerate(strokes):
        if st.block:
            groups.setdefault(top_entity(st.id), []).append(k)
    out = []
    for key, idx in groups.items():
        frames = []
        for k in idx:
            r = _rect(strokes[k])
            if r is not None and r[2] - r[0] >= FRAME_COVER * pw and r[3] - r[1] >= FRAME_COVER * ph:
                frames.append((k, r))
        if not frames:
            continue
        frame = max((r for _, r in frames), key=lambda r: (r[2] - r[0]) * (r[3] - r[1]))
        own = set(idx)
        holds = any(frame[0] <= (boxes[k][0] + boxes[k][2]) / 2.0 <= frame[2]
                    and frame[1] <= (boxes[k][1] + boxes[k][3]) / 2.0 <= frame[3]
                    for k in range(len(strokes)) if k not in own)
        if not holds:
            continue
        band = FRAME_BAND * min(frame[2] - frame[0], frame[3] - frame[1])
        frame_ids = {k for k, _ in frames}
        if not all(k in frame_ids or _in_band(boxes[k], frame, band) for k in idx):
            continue
        first = strokes[idx[0]]
        out.append({"entity": key, "block": (first.block or "").split("/")[0] or None, "layer": first.layer,
                    "stroke_ids": [strokes[k].id for k in idx], "frame_box": [round(v, 3) for v in frame],
                    "strokes": len(idx)})
    return out
