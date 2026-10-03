"""The raster adapter (docs/milestone7.md §4): scans, phone photos and raster-only PDF pages -> ``GenericPage``.

What a raster page gives the generic core (``generic.core.extract``) is the same as a vector page: strokes, texts
and, instead of wall primitives, the wall mask computed from the pixels. Page units are the pixels of the
*rectified* image with y up (``rectify.page_flip``); ``GenericPage.to_original`` maps them back to the original image,
``dpi`` is set only for a verified pixel size (raster-PDF render dpi, PNG pHYs, TIFF resolution; a scale note counts
only then, §0).

Steps (``read_page``):

1. **Load and rectify** (``rectify``): a transparent background is composited onto white (``read_grey``); the page
   is read at the *working resolution* the pixel constants below are tuned for (``working_resolution``: a page whose
   texts are more than ``RESAMPLE_ABOVE`` x ``TEXT_PX`` tall, a 300 or 600 dpi scan or a large photo, is resampled
   down so they are ``TEXT_PX`` tall; ``to_original`` keeps pointing at the file as given); scans deskewed (<= 5°),
   photos rectified (page quad, sheet-ratio snapping) and deskewed; raster-only PDF pages rendered at ``PDF_DPI``
   (200) dpi with pdftoppm. Photos whose dimension groups disagree with the snapped ratio by >
   ``ASPECT_CORRECTION`` are warped again with the solved aspect.
2. **Texts** (``ocr_page``): Tesseract 5 (``eng+tur``, ``OMP_THREAD_LIMIT=1``) on the page rendered 2 x from the
   original with flattened lighting, line art and door swings painted out: a page pass (psm 11, 0° and 90°) plus a
   *glyph-row* pass for the small texts the page pass misses (rows of character-sized components read alone at a
   normalised height, psm 7); numbers are verified by re-reading at 26/36/48 px (strict majority); the pieces of one
   size text read apart ("11" then "x 10") are joined (``join_size_pairs``: a piece never becomes a dimension text).
   Every text keeps
   its OCR confidence and pixel box (original image pixels) as ``ocr`` evidence; a length text needs conf >=
   ``DIM_TEXT_CONF`` (0.85) to be a dimension text (§4.3), other texts conf >= ``TEXT_CONF`` (0.6).
3. **Text removal** (``blank_texts``, §4.2): a box is blanked only when conf >= 0.6, the text is a room-vocabulary
   word, a number or a size/length pattern, and its height is 0.5-2 x the median text height; the ink components
   wholly in the box are cleared, so a wall line through a label survives. In a number's box every pixel off the
   long line art goes (a comma touching its dimension line); in a word box whose letters touch a drawn line or a
   door swing, every pixel off the swing and off the line art running on outside the box goes.
4. **Strokes** (``strokes_from_ink``): the ink (without filled-wall candidates) is thinned (Zhang-Suen, numpy; no
   ximgproc, no scikit-image), staircase pixels and 1 px spurs removed, the skeleton traced into chains, chains split
   into straight segments (Douglas-Peucker, 1 px) and arc fragments (circle fit); fragments of one circle and the
   straight pieces that continue them are joined (arcs of >= 50° kept); collinear segments merge through junctions
   (same line within 1 px, ends within 3 px) except at crossings and, between two pieces that each carry a number,
   where a perpendicular stroke ends (a dimension chain's extension line); free ends get back the half line width
   the thinning took. Strokes carry ``source "raster"``; arcs carry ``arc`` and points sampled on the fitted circle.
5. **Scale**: the core's dimension finder (``generic.scale.find_dimensions``) on these strokes and the OCR texts,
   then ``provisional_scale`` (a scale note counts only with a verified pixel size). No scale -> no wall mask; the
   core stops the page ("no dimension readable on the raster page").
6. **Wall mask** at the scale, with the dimension strokes (lines, ticks, extension lines) erased first:
   - *filled walls*: opening with ``k = max(3, round(0.6 t_min))`` px, ``t_min`` = 2 x the lowest real
     distance-transform mode >= 3 px of the ink; components touching the image edge and without an elongated part
     are dropped, and so are closed rings enclosing < 2 m², pieces whose ink is such a ring, and pieces whose
     neighbouring paper regions add up to < 2 m² (thick lines inside a drawn object);
   - *outline walls* (``outline_walls``): pairs of long parallel axis lines (morphological opening, >= 0.30 m;
     3 px .. 0.50 m apart, >= 70 % overlap, no third line inside) are band candidates; bands with the outside on one
     side and a room on the other seed the walls; a band grows in when both ends land on wall bands (one of them
     accepted; a band < 1 m needs both on accepted ones), and is rejected when it is a closed 4-sided loop <= 3 m per
     side, lies inside a wider accepted band or beside one (sharing its line); the mask runs from line centre to line
     centre.
   The mask goes into the page as ``MaskLayer`` (``walls.py`` turns it into rectangles, ``raster`` 0.85). Inside the
   mask, parallel lines that the threshold ran together (a window symbol beside the wall faces) are split at their
   paper gap (``split_valleys``) and the strokes traced again.
7. **Stroke clean-up**: straight strokes run on through junctions along straight ink (door leaves into the wall
   band), and straight ends within ``ARC_SNAP_PX`` of an arc end or centre meet it there (a door leaf's tip and
   hinge, ``snap_to_arcs``).

The core does openings and furniture on the raster strokes (method ``raster``, confidence 0.7).
"""
from __future__ import annotations

import math
import re
import subprocess
import tempfile
import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import cv2
import numpy as np

from wenart.ingest import rectify as RF
from wenart.ingest.generic.model import GenericPage, MaskLayer, Stroke, TextRun

PDF_DPI = 200                      # raster-only PDF pages are rendered at this (verified) pixel size
DP_EPSILON_PX = 1.0                # Douglas-Peucker tolerance of the skeleton chains
MIN_CHAIN_PX = 3                   # shorter skeleton spurs are noise
MERGE_GAP_PX = 3.0                 # collinear segments whose ends are this close merge (through a junction)
MERGE_OFFSET_PX = 1.0              # ... when both lie on one line within this
MERGE_ANGLE_DEG = 2.0
CROSS_MIN_DEG = 30.0               # ... unless a line at >= 30° passes within CROSS_PX of the joint
CROSS_PX = 2.5
CROSS_SIDE_PX = 1.5                # ... and reaches past it on both sides (a T-junction or a spur does not cross)
CROSS_STUB_PX = 12.0               # a short stub through a crossing still joins (a door leaf's end inside the wall band)
TEE_MIN_DEG = 60.0                 # a stroke ending at a joint at >= 60° to the line is a T (dimension chains)
ARC_RMS_PX = 0.75                  # circle fit of an arc chain
ARC_MAX_PX = 1.8
ARC_MIN_SWEEP_DEG = 50.0
ARC_FRAGMENT_SWEEP_DEG = 15.0      # a fragment of an arc split by junctions
ARC_FRAGMENT_MIN_PX = 12
ARC_MIN_SAGITTA_PX = 1.5           # a fragment bulges visibly from its chord (a straight run is no arc)
ARC_JOIN_GAP_PX = 6.0              # fragments of one circle whose ends are this close are one arc
STUB_EXTEND_PX = 6.0               # a line end runs on through a junction along straight ink for at most this
VALLEY_RUN_PX = 5                  # ... over a run this long along the lines
VALLEY_CONTRAST = 25.0             # a gap pixel this much brighter than the lines 2 px away splits them
ARC_SNAP_PX = 3.0                  # a straight end this close to an arc end or centre meets it there
ARC_HINGE_SHARE = 0.12             # a leaf from an arc end ending this close (x r) to the centre is hinged there
STUB_RUN_MIN_PX = 9                # (straight ink runs of >= this many px)
END_RESTORE_MAX_PX = 3.0           # a free end is moved out by at most this (half the line width)
SPUR_MAX_PX = 1                    # skeleton spurs this short (from a junction to a free end) are pruned
ARC_MAX_TURN_DEG = 35.0            # one Douglas-Peucker step of an arc turns at most this much
ARC_RADIUS_PX = (6.0, 800.0)
ARC_SAMPLE_DEG = 3.0


# --------------------------------------------------------------------------
# Thinning and tracing
# --------------------------------------------------------------------------

def thin(mask: np.ndarray) -> np.ndarray:
    """Zhang-Suen thinning of a bool mask (numpy, both sub-iterations vectorised)."""
    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return m.copy()
    ys, xs = np.nonzero(m)
    r0, r1, c0, c1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    img = np.zeros((r1 - r0 + 2, c1 - c0 + 2), np.uint8)
    img[1:-1, 1:-1] = m[r0:r1, c0:c1]
    while True:
        changed = False
        for step in (0, 1):
            p2 = img[:-2, 1:-1]
            p3 = img[:-2, 2:]
            p4 = img[1:-1, 2:]
            p5 = img[2:, 2:]
            p6 = img[2:, 1:-1]
            p7 = img[2:, :-2]
            p8 = img[1:-1, :-2]
            p9 = img[:-2, :-2]
            c = img[1:-1, 1:-1]
            nb = (p2.astype(np.int16) + p3 + p4 + p5 + p6 + p7 + p8 + p9)
            seq = (p2, p3, p4, p5, p6, p7, p8, p9, p2)
            trans = np.zeros(c.shape, np.int16)
            for a, b in zip(seq[:-1], seq[1:]):
                trans += ((a == 0) & (b == 1))
            if step == 0:
                cond = ((p2 * p4 * p6) == 0) & ((p4 * p6 * p8) == 0)
            else:
                cond = ((p2 * p4 * p8) == 0) & ((p2 * p6 * p8) == 0)
            delete = (c == 1) & (nb >= 2) & (nb <= 6) & (trans == 1) & cond
            if delete.any():
                c[delete] = 0
                changed = True
        if not changed:
            break
    out = np.zeros(m.shape, bool)
    out[r0:r1, c0:c1] = img[1:-1, 1:-1] > 0
    return out


_NB = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def _neighbour_count(skel: np.ndarray) -> np.ndarray:
    k = np.ones((3, 3), np.float32)
    k[1, 1] = 0
    return cv2.filter2D(skel.astype(np.float32), -1, k, borderType=cv2.BORDER_CONSTANT).astype(np.int16) * skel


def remove_redundant(skel: np.ndarray) -> np.ndarray:
    """Make an 8-connected skeleton minimal: a pixel with >= 3 neighbours whose neighbours stay 8-connected among
    themselves without it is removed (Zhang-Suen leaves such staircase corners, which look like junctions and split a
    line's chain). Raster order, one pixel at a time."""
    skel = np.asarray(skel, dtype=bool).copy()
    h, w = skel.shape
    count = _neighbour_count(skel)
    for r, c in zip(*np.nonzero(count >= 3)):
        if not skel[r, c]:
            continue
        nb = [(r + dr, c + dc) for dr, dc in _NB
              if 0 <= r + dr < h and 0 <= c + dc < w and skel[r + dr, c + dc]]
        if len(nb) < 3:
            continue
        group = {nb[0]}
        stack = [nb[0]]
        while stack:
            a = stack.pop()
            for b in nb:
                if b not in group and max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1:
                    group.add(b)
                    stack.append(b)
        if len(group) == len(nb):
            skel[r, c] = False
    return skel


def prune_spurs(skel: np.ndarray, max_len: int = SPUR_MAX_PX) -> np.ndarray:
    """Remove skeleton spurs (a free end at most ``max_len`` pixels from a junction): scanner noise on a line makes
    them, and every spur splits the line's chain at a false junction."""
    skel = np.asarray(skel, dtype=bool).copy()
    for _ in range(3):
        count = _neighbour_count(skel)
        removed = False
        for chain, closed in trace(skel):
            if closed or len(chain) > max_len + 1:
                continue
            a, b = chain[0], chain[-1]
            if count[a] == 1 and count[b] >= 3:
                keep = b
            elif count[b] == 1 and count[a] >= 3:
                keep = a
            else:
                continue
            for px in chain:
                if px != keep:
                    skel[px] = False
                    removed = True
        if not removed:
            break
    return skel


def trace(skel: np.ndarray) -> list[tuple[list[tuple[int, int]], bool]]:
    """Skeleton -> chains of (row, col) pixels between end points and junctions; ``(chain, closed)``. Junction
    pixels (>= 3 neighbours) end chains and belong to every chain that reaches them."""
    skel = np.asarray(skel, dtype=bool)
    count = _neighbour_count(skel)
    h, w = skel.shape
    junction = skel & (count >= 3)
    pixels = set(zip(*np.nonzero(skel)))
    visited_edges: set = set()
    chains: list[tuple[list[tuple[int, int]], bool]] = []

    def nbrs(p):
        r, c = p
        out = []
        for dr, dc in _NB:
            q = (r + dr, c + dc)
            if 0 <= q[0] < h and 0 <= q[1] < w and skel[q]:
                out.append(q)
        return out

    def is_node(p) -> bool:
        return bool(junction[p]) or count[p] == 1

    def walk(start, nxt):
        chain = [start, nxt]
        visited_edges.add((start, nxt))
        visited_edges.add((nxt, start))
        prev, cur = start, nxt
        while not is_node(cur):
            cand = [q for q in nbrs(cur) if q != prev and (cur, q) not in visited_edges]
            if not cand:
                break
            # Prefer 4-neighbours (a staircase pixel has both a 4- and an 8-neighbour continuation).
            cand.sort(key=lambda q: abs(q[0] - cur[0]) + abs(q[1] - cur[1]))
            q = cand[0]
            visited_edges.add((cur, q))
            visited_edges.add((q, cur))
            chain.append(q)
            prev, cur = cur, q
        return chain

    nodes = sorted(p for p in pixels if is_node(p))
    for p in nodes:
        for q in nbrs(p):
            if (p, q) in visited_edges:
                continue
            if junction[p] and junction[q]:
                visited_edges.add((p, q))
                visited_edges.add((q, p))
                continue                      # inside a junction cluster
            chains.append((walk(p, q), False))
    # Cycles: pixels never reached (every pixel has two neighbours).
    seen = {px for ch, _ in chains for px in ch}
    for p in sorted(pixels - seen):
        if p in seen:
            continue
        nb = nbrs(p)
        if not nb:
            chains.append(([p], False))       # an isolated dot
            seen.add(p)
            continue
        chain = walk(p, nb[0])
        closed = len(chain) > 2 and max(abs(chain[-1][0] - p[0]), abs(chain[-1][1] - p[1])) <= 1
        chains.append((chain, closed))
        seen.update(chain)
    return chains


# --------------------------------------------------------------------------
# Chains -> segments and arcs
# --------------------------------------------------------------------------

def fit_circle(pts: np.ndarray) -> Optional[tuple[float, float, float, float, float]]:
    """Algebraic (Kasa) circle fit refined by Gauss-Newton: (cx, cy, r, rms, max residual) or None."""
    pts = np.asarray(pts, dtype=np.float64)
    if len(pts) < 5:
        return None
    x, y = pts[:, 0], pts[:, 1]
    a = np.column_stack([x, y, np.ones(len(x))])
    b = x * x + y * y
    try:
        sol, *_ = np.linalg.lstsq(a, b, rcond=None)
    except np.linalg.LinAlgError:
        return None
    cx, cy = sol[0] / 2.0, sol[1] / 2.0
    r2 = sol[2] + cx * cx + cy * cy
    if r2 <= 0:
        return None
    r = math.sqrt(r2)
    for _ in range(10):
        dx, dy = x - cx, y - cy
        d = np.hypot(dx, dy)
        d[d == 0] = 1e-9
        res = d - r
        j = np.column_stack([-dx / d, -dy / d, -np.ones(len(x))])
        try:
            step, *_ = np.linalg.lstsq(j, -res, rcond=None)
        except np.linalg.LinAlgError:
            break
        cx, cy, r = cx + step[0], cy + step[1], r + step[2]
        if np.abs(step).max() < 1e-6:
            break
    res = np.hypot(x - cx, y - cy) - r
    return float(cx), float(cy), float(abs(r)), float(np.sqrt(np.mean(res ** 2))), float(np.abs(res).max())


def _turn(a, b, c) -> float:
    """Signed turning angle (degrees) at b from a->b to b->c."""
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (c[0] - b[0], c[1] - b[1])
    return math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1]))


def _sweep(pts: np.ndarray, cx: float, cy: float) -> float:
    ang = np.unwrap(np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx))
    return float(abs(math.degrees(ang[-1] - ang[0])))


@dataclass(eq=False)
class _Piece:
    kind: str                                   # line | arc
    pts: np.ndarray                             # x, y (image frame, pixel centres) of the chain part
    a: tuple[float, float] = (0.0, 0.0)         # line ends
    b: tuple[float, float] = (0.0, 0.0)
    circle: Optional[tuple[float, float, float]] = None
    closed: bool = False


def _line_piece(pts: np.ndarray) -> _Piece:
    """A straight piece: total-least-squares line through the pixels, ends projected onto it."""
    if len(pts) == 1:
        p = (float(pts[0, 0]), float(pts[0, 1]))
        return _Piece("line", pts, p, p)
    if len(pts) == 2:
        return _Piece("line", pts, (float(pts[0, 0]), float(pts[0, 1])), (float(pts[1, 0]), float(pts[1, 1])))
    mean = pts.mean(axis=0)
    _, _, vt = np.linalg.svd(pts - mean)
    u = vt[0]
    t = (pts - mean) @ u
    first, last = mean + u * t[0], mean + u * t[-1]
    return _Piece("line", pts, (float(first[0]), float(first[1])), (float(last[0]), float(last[1])))


def split_chain(chain: list[tuple[int, int]], closed: bool) -> list[_Piece]:
    """One traced chain -> straight pieces and arc *fragments* (runs of consistently turning Douglas-Peucker steps
    that fit a circle; ``strokes_from_ink`` merges fragments of one circle and keeps arcs of >= 50°)."""
    pts = np.array([(c, r) for r, c in chain], dtype=np.float64)       # x = col, y = row
    if len(pts) <= 2:
        return [_line_piece(pts)]
    approx_idx = _dp_indices(pts, DP_EPSILON_PX, closed)
    n = len(approx_idx)
    verts = [pts[i] for i in approx_idx]
    turns = [_turn(verts[k - 1], verts[k], verts[k + 1]) for k in range(1, n - 1)]
    arcs: list[tuple[int, int, tuple]] = []
    k = 0
    while k < n - 2:
        if turns[k] == 0 or abs(turns[k]) > ARC_MAX_TURN_DEG:
            k += 1
            continue
        sign = math.copysign(1.0, turns[k])
        j = k
        while j < n - 2 and turns[j] * sign > 0 and abs(turns[j]) <= ARC_MAX_TURN_DEG:
            j += 1
        found = _grow_arc(pts, approx_idx[k], approx_idx[min(j + 1, n - 1)])
        if found is not None:
            arcs.append(found)
            k = j + 1
        else:
            k += 1
    if not arcs:
        # A short chain with no DP turn can still be one fragment of an arc (split by a junction).
        found = _grow_arc(pts, 0, len(pts) - 1) if len(pts) >= ARC_FRAGMENT_MIN_PX else None
        if found is None:
            return _lines_between(pts, approx_idx, 0, len(pts) - 1)
        arcs = [found]
    pieces: list[_Piece] = []
    pos = 0
    for lo, hi, circle in sorted(arcs):
        lo = max(lo, pos)
        if hi - lo < 4:
            continue
        if lo > pos:
            pieces.extend(_lines_between(pts, approx_idx, pos, lo))
        pieces.append(_Piece("arc", pts[lo:hi + 1], circle=circle))
        pos = hi
    if pos < len(pts) - 1:
        pieces.extend(_lines_between(pts, approx_idx, pos, len(pts) - 1))
    return pieces


def _dp_indices(pts: np.ndarray, eps: float, closed: bool) -> list[int]:
    """Douglas-Peucker vertex indices of a polyline (both ends kept)."""
    n = len(pts)
    if n <= 2:
        return list(range(n))
    keep = np.zeros(n, bool)
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    if closed and n > 3:
        far = int(np.argmax(np.hypot(pts[:, 0] - pts[0, 0], pts[:, 1] - pts[0, 1])))
        keep[far] = True
        stack = [(0, far), (far, n - 1)]
    while stack:
        i, j = stack.pop()
        if j - i < 2:
            continue
        a, b = pts[i], pts[j]
        d = b - a
        length = math.hypot(d[0], d[1])
        seg = pts[i + 1:j]
        if length < 1e-9:
            dist = np.hypot(seg[:, 0] - a[0], seg[:, 1] - a[1])
        else:
            dist = np.abs((seg[:, 0] - a[0]) * d[1] - (seg[:, 1] - a[1]) * d[0]) / length
        m = int(np.argmax(dist))
        if dist[m] > eps:
            keep[i + 1 + m] = True
            stack.append((i, i + 1 + m))
            stack.append((i + 1 + m, j))
    return [int(i) for i in np.nonzero(keep)[0]]


def _sagitta(pts: np.ndarray) -> float:
    """Largest distance of the points from their chord."""
    a, b = pts[0], pts[-1]
    d = b - a
    length = math.hypot(d[0], d[1])
    if length < 1e-9:
        return float(np.hypot(pts[:, 0] - a[0], pts[:, 1] - a[1]).max())
    return float((np.abs((pts[:, 0] - a[0]) * d[1] - (pts[:, 1] - a[1]) * d[0]) / length).max())


def _grow_arc(pts: np.ndarray, lo: int, hi: int) -> Optional[tuple[int, int, tuple]]:
    """Fit a circle to pts[lo..hi] and grow the run along the chain while the points stay on it; an arc fragment
    needs a visible bulge (sagitta >= ``ARC_MIN_SAGITTA_PX``) and >= ``ARC_FRAGMENT_SWEEP_DEG``."""
    if hi - lo < 6:
        return None
    fit = fit_circle(pts[lo:hi + 1])
    if fit is None:
        return None
    cx, cy, r, rms, mx = fit
    if not ARC_RADIUS_PX[0] <= r <= ARC_RADIUS_PX[1] or rms > ARC_RMS_PX or mx > ARC_MAX_PX + 0.5:
        return None

    def on(i):
        return abs(math.hypot(pts[i, 0] - cx, pts[i, 1] - cy) - r) <= ARC_MAX_PX

    while lo > 0 and on(lo - 1):
        lo -= 1
    while hi < len(pts) - 1 and on(hi + 1):
        hi += 1
    fit = fit_circle(pts[lo:hi + 1])
    if fit is None:
        return None
    cx, cy, r, rms, mx = fit
    if rms > ARC_RMS_PX or mx > ARC_MAX_PX + 0.5 or not ARC_RADIUS_PX[0] <= r <= ARC_RADIUS_PX[1]:
        return None
    if _sweep(pts[lo:hi + 1], cx, cy) < ARC_FRAGMENT_SWEEP_DEG or _sagitta(pts[lo:hi + 1]) < ARC_MIN_SAGITTA_PX:
        return None
    return lo, hi, (cx, cy, r)


def _lines_between(pts: np.ndarray, approx_idx: list[int], lo: int, hi: int) -> list[_Piece]:
    idx = [lo] + [i for i in approx_idx if lo < i < hi] + [hi]
    return [_line_piece(pts[i:j + 1]) for i, j in zip(idx[:-1], idx[1:])]


# --------------------------------------------------------------------------
# Merging collinear segments
# --------------------------------------------------------------------------

def _seg_angle(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def _angle_diff(x: float, y: float) -> float:
    d = abs(x - y) % 180.0
    return min(d, 180.0 - d)


def merge_collinear(lines: list[tuple[tuple[float, float], tuple[float, float]]],
                    number_boxes: Sequence = ()) -> list:
    """Merge straight segments lying on one line (within ``MERGE_OFFSET_PX``, ``MERGE_ANGLE_DEG``) whose facing ends
    are within ``MERGE_GAP_PX`` (they met at a junction). Returns ((a, b), [source indices]).

    ``number_boxes`` (image pixel-corner boxes of the numbers the OCR read): two pieces that each carry a number
    alongside them stay apart where a perpendicular stroke ends at their joint, the extension line of a dimension
    chain (its tick drawn too small to survive the thinning)."""
    items = [[a, b, [i]] for i, (a, b) in enumerate(lines)]
    alive = [True] * len(items)
    # Where a line crosses (a dimension chain's extension line, a tick, a perpendicular wall face) two long pieces
    # stay apart: in a drawing that point is a mark or a junction, as in a vector file. A short stub through the
    # crossing still joins (a door leaf running on into the wall band, the two halves of a tick).
    cell = 8
    by_cell: dict = {}
    for k, (a, b) in enumerate(lines):
        n_steps = max(1, int(math.dist(a, b) // cell) + 1)
        for st in range(n_steps + 1):
            t = st / n_steps
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            by_cell.setdefault((int(x // cell), int(y // cell)), set()).add(k)

    def crossing(pt, angle: float, own: set) -> bool:
        gx, gy = int(pt[0] // cell), int(pt[1] // cell)
        near = set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near |= by_cell.get((gx + dx, gy + dy), set())
        # The line through the joint, direction ``angle``: a crossing stroke reaches past it on both sides.
        nx, ny = -math.sin(math.radians(angle)), math.cos(math.radians(angle))
        for k in near - own:
            a, b = lines[k]
            if math.dist(a, b) < 2.0 or _angle_diff(_seg_angle(a, b), angle) < CROSS_MIN_DEG:
                continue
            length = math.dist(a, b)
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            t = (pt[0] - a[0]) * ux + (pt[1] - a[1]) * uy
            if not (-CROSS_PX <= t <= length + CROSS_PX and
                    abs((pt[0] - a[0]) * -uy + (pt[1] - a[1]) * ux) <= CROSS_PX):
                continue
            sa = (a[0] - pt[0]) * nx + (a[1] - pt[1]) * ny
            sb = (b[0] - pt[0]) * nx + (b[1] - pt[1]) * ny
            if min(sa, sb) <= -CROSS_SIDE_PX and max(sa, sb) >= CROSS_SIDE_PX:
                return True
        return False

    def tee(pt, angle: float, own: set) -> bool:
        """A stroke at >= 60° to the line ends at the joint (a T, not a crossing)."""
        gx, gy = int(pt[0] // cell), int(pt[1] // cell)
        near = set()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near |= by_cell.get((gx + dx, gy + dy), set())
        for k in near - own:
            a, b = lines[k]
            if math.dist(a, b) >= CROSS_STUB_PX and _angle_diff(_seg_angle(a, b), angle) >= TEE_MIN_DEG and \
                    min(math.dist(a, pt), math.dist(b, pt)) <= CROSS_PX:
                return True
        return False

    def number_along(a, b) -> bool:
        """A number box beside the piece: parallel to it, its centre over the piece, within 2.5 text heights."""
        length = math.dist(a, b)
        if length < 2.0:
            return False
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        horizontal = abs(ux) >= abs(uy)
        for x0, y0, x1, y1 in number_boxes:
            w, hh = x1 - x0, y1 - y0
            if (w >= hh) != horizontal:
                continue
            cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
            t = (cx - a[0]) * ux + (cy - a[1]) * uy
            off = abs((cx - a[0]) * -uy + (cy - a[1]) * ux)
            if 0.0 <= t <= length and off <= 2.5 * min(w, hh):
                return True
        return False

    changed = True
    while changed:
        changed = False
        grid: dict = {}
        for i, it in enumerate(items):
            if not alive[i]:
                continue
            for p in (it[0], it[1]):
                grid.setdefault((int(p[0] // 8), int(p[1] // 8)), set()).add(i)
        for i, it in enumerate(items):
            if not alive[i]:
                continue
            a, b = it[0], it[1]
            la = math.dist(a, b)
            if la < 2.0:
                continue
            cands = set()
            for p in (a, b):
                gx, gy = int(p[0] // 8), int(p[1] // 8)
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        cands |= grid.get((gx + dx, gy + dy), set())
            for j in sorted(cands):
                if j == i or not alive[j]:
                    continue
                c, d = items[j][0], items[j][1]
                lc = math.dist(c, d)
                if lc < 2.0 or _angle_diff(_seg_angle(a, b), _seg_angle(c, d)) > MERGE_ANGLE_DEG:
                    continue
                gap, gp, gq = min(((math.dist(p, q), p, q) for p in (a, b) for q in (c, d)), key=lambda x: x[0])
                if gap > MERGE_GAP_PX:
                    continue
                joint = (0.5 * (gp[0] + gq[0]), 0.5 * (gp[1] + gq[1]))
                if min(la, lc) >= CROSS_STUB_PX and crossing(joint, _seg_angle(a, b), {i, j}):
                    continue
                if number_boxes and min(la, lc) >= CROSS_STUB_PX and number_along(a, b) and \
                        number_along(c, d) and tee(joint, _seg_angle(a, b), set(it[2]) | set(items[j][2])):
                    continue
                # Both on one line: offsets of the other's ends from this line.
                ux, uy = (b[0] - a[0]) / la, (b[1] - a[1]) / la
                offs = [abs((q[0] - a[0]) * -uy + (q[1] - a[1]) * ux) for q in (c, d)]
                if max(offs) > MERGE_OFFSET_PX:
                    continue
                # Refit the line through the four ends weighted by length.
                pts = np.array([a, b, c, d], dtype=np.float64)
                wts = np.array([la, la, lc, lc])
                mean = (pts * wts[:, None]).sum(axis=0) / wts.sum()
                cov = ((pts - mean) * wts[:, None]).T @ (pts - mean)
                _, vecs = np.linalg.eigh(cov)
                u = vecs[:, -1]
                if u @ np.array([ux, uy]) < 0:
                    u = -u
                tt = [(np.array(p) - mean) @ u for p in (a, b, c, d)]
                lo, hi = min(tt), max(tt)
                na = tuple(float(v) for v in mean + u * lo)
                nb = tuple(float(v) for v in mean + u * hi)
                it[0], it[1] = na, nb
                it[2] = it[2] + items[j][2]
                alive[j] = False
                a, b = na, nb
                la = math.dist(a, b)
                changed = True
    return [((it[0], it[1]), sorted(it[2])) for i, it in enumerate(items) if alive[i]]


# --------------------------------------------------------------------------
# Strokes
# --------------------------------------------------------------------------

@dataclass
class StrokeSet:
    """The page's raster strokes (page units, y up) and how they were made (image frame)."""
    strokes: list[Stroke]
    lines_img: list[tuple[tuple[float, float], tuple[float, float]]]       # per straight stroke, image frame
    arcs_img: list[tuple[float, float, float, float, float]]               # cx, cy, r, start, end (image, deg)
    skeleton: np.ndarray


def _arc_samples(pts: np.ndarray, cx: float, cy: float) -> tuple[float, float]:
    """Start and end angle (radians, image frame, unwrapped) of points along an arc, ordered by angle."""
    ang = np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx)
    order = np.argsort(ang)
    srt = ang[order]
    gaps = np.diff(np.concatenate([srt, [srt[0] + 2 * math.pi]]))
    k = int(np.argmax(gaps))                    # the arc is the circle minus its largest empty gap
    start = srt[(k + 1) % len(srt)]
    end = srt[k]
    if end < start:
        end += 2 * math.pi
    return float(start), float(end)


def _joint_fit(p1: np.ndarray, p2: np.ndarray) -> Optional[tuple[float, float, float]]:
    """The circle through two point sets when one circle fits both (RMS <= 1.2 x ``ARC_RMS_PX``, every point within
    ``ARC_MAX_PX`` + 0.5) and their facing ends are within ``ARC_JOIN_GAP_PX``; else None. Short fragments fit
    their own circles badly, so only the joint fit decides."""
    ends1, ends2 = (p1[0], p1[-1]), (p2[0], p2[-1])
    if min(math.dist(a, b) for a in ends1 for b in ends2) > ARC_JOIN_GAP_PX:
        return None
    pts = np.vstack([p1, p2])
    fit = fit_circle(pts)
    if fit is None or fit[3] > ARC_RMS_PX * 1.2 or fit[4] > ARC_MAX_PX + 0.5:
        return None
    if not ARC_RADIUS_PX[0] <= fit[2] <= ARC_RADIUS_PX[1]:
        return None
    return fit[:3]


def _merge_arcs(frags: list[tuple[np.ndarray, tuple[float, float, float]]]) -> list:
    """Join arc fragments that one circle fits (``_joint_fit``); the joined points are refitted."""
    items = [[pts, circle] for pts, circle in frags]
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            if items[i] is None:
                continue
            for j in range(i + 1, len(items)):
                if items[j] is None or items[i] is None:
                    continue
                circle = _joint_fit(items[i][0], items[j][0])
                if circle is None:
                    continue
                items[i] = [np.vstack([items[i][0], items[j][0]]), circle]
                items[j] = None
                changed = True
    return [it for it in items if it is not None]


def _absorb_lines(arcs: list, pieces: list[_Piece]) -> list[_Piece]:
    """Straight pieces that continue an arc on its circle (``_joint_fit`` of the arc and the piece) become part of
    it (a junction split them off). Returns the pieces left over."""
    left = list(pieces)
    for arc in arcs:
        changed = True
        while changed:
            changed = False
            pts, (cx, cy, r) = arc
            lo, hi = pts.min(axis=0) - ARC_JOIN_GAP_PX, pts.max(axis=0) + ARC_JOIN_GAP_PX
            for piece in list(left):
                q = piece.pts
                if len(q) < 2 or len(q) > 2 * len(pts):
                    continue
                if not (lo[0] <= q[0, 0] <= hi[0] and lo[1] <= q[0, 1] <= hi[1]) and \
                        not (lo[0] <= q[-1, 0] <= hi[0] and lo[1] <= q[-1, 1] <= hi[1]):
                    continue
                if np.abs(np.hypot(q[:, 0] - cx, q[:, 1] - cy) - r).max() > 2 * ARC_MAX_PX:
                    continue
                circle = _joint_fit(pts, q)
                if circle is None:
                    continue
                arc[0], arc[1] = np.vstack([pts, q]), circle
                left.remove(piece)
                changed = True
                break
    return left


def _axis_runs(ink: np.ndarray, min_len: int) -> dict:
    """Straight ink runs along the image axes (morphological opening with 1 x L / L x 1 lines), per axis as
    {"h": [(row, c0, c1)], "v": [(col, r0, r1)]} with the run's mean cross position."""
    ink8 = np.asarray(ink, np.uint8)
    out: dict = {"h": [], "v": []}
    for axis, kernel in (("h", np.ones((1, min_len), np.uint8)), ("v", np.ones((min_len, 1), np.uint8))):
        opened = cv2.morphologyEx(ink8, cv2.MORPH_OPEN, kernel)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
        for i in range(1, n):
            x, y, w, h, _ = (int(v) for v in stats[i])
            ys, xs = np.nonzero(lab[y:y + h, x:x + w] == i)
            if axis == "h":
                out["h"].append((float(ys.mean()) + y, float(x), float(x + w - 1)))
            else:
                out["v"].append((float(xs.mean()) + x, float(y), float(y + h - 1)))
    return out


def _extend_through_junctions(lines: list, ink: np.ndarray, junction: Optional[np.ndarray] = None) -> list:
    """Thinning ends a line at the junction where it meets another one, although the ink may run on straight for a
    few pixels (a door leaf drawn into the wall band up to its hinge). An axis-parallel line end is moved to the end
    of the straight ink run it lies on when that run goes on for at most ``STUB_EXTEND_PX`` (a longer run is the next
    drawn piece and stays separate)."""
    runs = _axis_runs(ink, STUB_RUN_MIN_PX)
    out = []
    for a, b in lines:
        length = math.dist(a, b)
        if length < 2.0:
            out.append((a, b))
            continue
        ang = _seg_angle(a, b)
        axis = "h" if _angle_diff(ang, 0.0) <= 2.0 else "v" if _angle_diff(ang, 90.0) <= 2.0 else None
        if axis is None:
            out.append((a, b))
            continue
        k = 0 if axis == "h" else 1                       # the along coordinate
        c = (a[1 - k] + b[1 - k]) / 2.0
        lo, hi = sorted((a[k], b[k]))

        def at_junction(t: float) -> bool:
            if junction is None:
                return True
            x, y = (t, c) if axis == "h" else (c, t)
            r0_, c0_ = int(round(y)) - 2, int(round(x)) - 2
            win = junction[max(0, r0_):r0_ + 5, max(0, c0_):c0_ + 5]
            return bool(win.any())

        new_lo, new_hi = lo, hi
        for rc, r0, r1 in runs[axis]:
            if abs(rc - c) > 1.5 or r1 < lo - 1 or r0 > hi + 1:
                continue
            if r0 < new_lo and lo - r0 <= STUB_EXTEND_PX and at_junction(lo):
                new_lo = r0
            if r1 > new_hi and r1 - hi <= STUB_EXTEND_PX and at_junction(hi):
                new_hi = r1
        if (new_lo, new_hi) == (lo, hi):
            out.append((a, b))
            continue
        first, last = (a, b) if a[k] <= b[k] else (b, a)
        if axis == "h":
            first, last = (new_lo, first[1]), (new_hi, last[1])
        else:
            first, last = (first[0], new_lo), (last[0], new_hi)
        out.append((first, last) if a[k] <= b[k] else (last, first))
    return out


def extend_line_strokes(strokes: list[Stroke], ink: np.ndarray, skip_ids: set,
                        skeleton: Optional[np.ndarray] = None) -> list[Stroke]:
    """``_extend_through_junctions`` on the straight strokes (page units) except ``skip_ids`` (the dimension lines:
    their ends must stay at their end marks for the dimension finder)."""
    h = ink.shape[0]
    todo = [st for st in strokes if st.kind == "line" and st.id not in skip_ids and len(st.pts) == 2]
    img_lines = [((st.pts[0][0] - 0.5, h - st.pts[0][1] - 0.5), (st.pts[1][0] - 0.5, h - st.pts[1][1] - 0.5))
                 for st in todo]
    junction = None
    if skeleton is not None:
        junction = np.asarray(skeleton, bool) & (_neighbour_count(skeleton) >= 3)
    moved = {st.id: seg for st, seg in zip(todo, _extend_through_junctions(img_lines, ink, junction))}
    out = []
    for st in strokes:
        seg = moved.get(st.id)
        if seg is None:
            out.append(st)
            continue
        pts = [(round(p[0] + 0.5, 3), round(h - p[1] - 0.5, 3)) for p in seg]
        out.append(Stroke(id=st.id, kind=st.kind, pts=pts, closed=st.closed, source=st.source))
    return out


def split_valleys(ink: np.ndarray, gray: np.ndarray, contrast: float = VALLEY_CONTRAST) -> np.ndarray:
    """Ink without the bright valley pixels between two parallel dark lines: a pixel that is the brightest of its
    column (row) neighbours and >= ``contrast`` grey levels brighter than the pixels two steps away on both sides is
    the paper gap the threshold filled in (a window symbol 2 px from the wall faces), so the skeleton keeps the lines
    apart; only runs of >= ``VALLEY_RUN_PX`` such pixels along the lines count. Used inside the wall bands only."""
    g = np.asarray(gray, np.float32)
    out = np.asarray(ink, bool).copy()
    pad = np.pad(g, 2, mode="edge")
    c = pad[2:-2, 2:-2]
    for dy, dx in ((1, 0), (0, 1)):
        n1 = pad[2 - dy:pad.shape[0] - 2 - dy, 2 - dx:pad.shape[1] - 2 - dx]
        p1 = pad[2 + dy:pad.shape[0] - 2 + dy, 2 + dx:pad.shape[1] - 2 + dx]
        n2 = pad[2 - 2 * dy:pad.shape[0] - 2 - 2 * dy, 2 - 2 * dx:pad.shape[1] - 2 - 2 * dx]
        p2 = pad[2 + 2 * dy:pad.shape[0] - 2 + 2 * dy, 2 + 2 * dx:pad.shape[1] - 2 + 2 * dx]
        valley = (c >= n1) & (c >= p1) & (c - n2 >= contrast) & (c - p2 >= contrast)
        # Only a gap that runs along the lines for VALLEY_RUN_PX (a line crossing between two letters is no gap).
        kernel = np.ones((1, VALLEY_RUN_PX), np.uint8) if dy else np.ones((VALLEY_RUN_PX, 1), np.uint8)
        valley = cv2.morphologyEx(valley.astype(np.uint8), cv2.MORPH_OPEN, kernel) > 0
        out &= ~valley
    return out


def snap_to_arcs(strokes: list[Stroke], skip_ids: set, max_px: float = ARC_SNAP_PX) -> list[Stroke]:
    """Straight stroke ends within ``max_px`` of an arc's end or centre move onto it (page units): a door leaf's tip
    and hinge meet its swing in the ink, but the skeleton junction and the circle fit leave them a pixel or two
    apart. A straight stroke that ends on an arc end and points at the arc's centre is the door leaf: its other end
    moves onto the centre (the hinge) when within ``ARC_HINGE_SHARE`` x the radius of it (the hinge sits inside the
    wall band, where the leaf's drawn end lands on a wall line). ``skip_ids`` (dimension lines) keep their ends."""
    arcs = [st for st in strokes if st.arc and len(st.pts) >= 2]
    if not arcs:
        return strokes
    keys = [q for st in arcs for q in (tuple(st.pts[0]), tuple(st.pts[-1]), tuple(st.arc["center"]))]
    out = []
    for st in strokes:
        if st.kind != "line" or st.id in skip_ids or len(st.pts) != 2:
            out.append(st)
            continue
        pts = list(st.pts)
        for i in (0, 1):
            best = min(keys, key=lambda q: math.dist(q, pts[i]))
            if 0.0 < math.dist(best, pts[i]) <= max_px and math.dist(best, pts[1 - i]) > max_px:
                pts[i] = (round(float(best[0]), 3), round(float(best[1]), 3))
        for arc in arcs:
            centre, r = tuple(arc.arc["center"]), float(arc.arc["radius"])
            for i in (0, 1):
                tip, other = pts[i], pts[1 - i]
                if min(math.dist(tip, arc.pts[0]), math.dist(tip, arc.pts[-1])) > 1e-6:
                    continue
                d = math.dist(other, centre)
                if 0.0 < d <= max(max_px, ARC_HINGE_SHARE * r):
                    pts[1 - i] = (round(float(centre[0]), 3), round(float(centre[1]), 3))
        out.append(st if pts == list(st.pts) else
                   Stroke(id=st.id, kind=st.kind, pts=pts, closed=st.closed, source=st.source))
    return out


def strokes_from_ink(ink: np.ndarray, height: Optional[int] = None, id_prefix: str = "",
                     number_boxes: Sequence = ()) -> StrokeSet:
    """Thin the ink, drop redundant pixels and spurs, trace, split into lines and arc fragments, join the fragments
    of one circle (and the straight pieces that continue them on it), keep arcs of >= 50° (shorter ones become
    straight pieces), merge collinear lines; page units y up (pixel-corner frame: image pixel centre (c, r) -> page
    (c + 0.5, H - r - 0.5))."""
    ink = np.asarray(ink, dtype=bool)
    h = ink.shape[0] if height is None else height
    skel = prune_spurs(remove_redundant(thin(ink)))
    line_pieces: list[_Piece] = []
    frags: list[tuple[np.ndarray, tuple[float, float, float]]] = []
    for chain, closed in trace(skel):
        if 1 < len(chain) < MIN_CHAIN_PX:
            continue
        for piece in split_chain(chain, closed):
            if piece.kind == "arc":
                frags.append((piece.pts, piece.circle))
            else:
                line_pieces.append(piece)
    joined = [list(a) for a in _merge_arcs(frags)]
    line_pieces = _absorb_lines(joined, line_pieces)
    # Thinning pulls a free line end in by about half the line width: put it back (distance to the paper there).
    count = _neighbour_count(skel)
    dist = cv2.distanceTransform(ink.astype(np.uint8), cv2.DIST_L2, 3)

    def free_end_reach(p) -> float:
        r, c = int(round(p[1])), int(round(p[0]))
        if 0 <= r < skel.shape[0] and 0 <= c < skel.shape[1] and skel[r, c] and count[r, c] == 1:
            return float(min(dist[r, c], END_RESTORE_MAX_PX))
        return 0.0

    lines = []
    for piece in line_pieces:
        a, b = piece.a, piece.b
        length = math.dist(a, b)
        if length > 0:
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            da = free_end_reach(piece.pts[0]) if len(piece.pts) else 0.0
            db = free_end_reach(piece.pts[-1]) if len(piece.pts) else 0.0
            a = (a[0] - ux * da, a[1] - uy * da)
            b = (b[0] + ux * db, b[1] + uy * db)
        lines.append((a, b))
    arcs = []
    for pts, (cx, cy, r) in joined:
        a0, a1 = _arc_samples(pts, cx, cy)
        # Free arc ends come back by the same half line width (as an angle).
        ang = np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx)
        i0 = int(np.argmin(np.abs(((ang - a0) + math.pi) % (2 * math.pi) - math.pi)))
        i1 = int(np.argmin(np.abs(((ang - a1) + math.pi) % (2 * math.pi) - math.pi)))
        a0 -= free_end_reach(pts[i0]) / max(r, 1.0)
        a1 += free_end_reach(pts[i1]) / max(r, 1.0)
        if math.degrees(a1 - a0) >= ARC_MIN_SWEEP_DEG:
            arcs.append((pts, (cx, cy, r), a0, a1))
        else:
            idx = _dp_indices(pts, DP_EPSILON_PX, False)
            lines.extend((p.a, p.b) for p in _lines_between(pts, idx, 0, len(pts) - 1))
    merged = merge_collinear(lines, number_boxes)

    def page(p):
        return (round(float(p[0]) + 0.5, 3), round(h - float(p[1]) - 0.5, 3))

    strokes: list[Stroke] = []
    lines_img = []
    for (a, b), _src in sorted(merged, key=lambda m: (round(min(m[0][0][1], m[0][1][1]), 1),
                                                       round(min(m[0][0][0], m[0][1][0]), 1))):
        strokes.append(Stroke(id=f"{id_prefix}seg:{len(lines_img) + 1}", kind="line", pts=[page(a), page(b)],
                              source="raster"))
        lines_img.append((a, b))
    arcs_img = []
    for k, (pts, (cx, cy, r), a0, a1) in enumerate(sorted(arcs, key=lambda x: (round(x[1][1], 1),
                                                                                round(x[1][0], 1)))):
        n = max(4, int(math.degrees(a1 - a0) / ARC_SAMPLE_DEG) + 1)
        samples = [(cx + r * math.cos(a0 + (a1 - a0) * i / (n - 1)), cy + r * math.sin(a0 + (a1 - a0) * i / (n - 1)))
                   for i in range(n)]
        # The page frame is y up: angles change sign, so the page arc runs from -a1 to -a0.
        start_deg, end_deg = -math.degrees(a1), -math.degrees(a0)
        strokes.append(Stroke(id=f"{id_prefix}arc:{k + 1}", kind="arc", pts=[page(p) for p in samples],
                              source="raster",
                              arc={"center": page((cx, cy)), "radius": round(r, 3), "start_deg": round(start_deg, 3),
                                   "end_deg": round(end_deg, 3)}))
        arcs_img.append((cx, cy, r, math.degrees(a0), math.degrees(a1)))
    return StrokeSet(strokes=strokes, lines_img=lines_img, arcs_img=arcs_img, skeleton=skel)


# --------------------------------------------------------------------------
# Texts: Tesseract on the page and on glyph rows
# --------------------------------------------------------------------------

DIM_TEXT_CONF = 0.85               # a length text counts as a dimension text from this OCR confidence (§4.3)
TEXT_CONF = 0.60                   # other texts (labels, titles, notes)
BLANK_HEIGHT = (0.5, 2.0)          # x the median text height: boxes blanked by the text removal (§4.2)
GLYPH_MAX_PX = 40                  # character components: <= 40 px ...
GLYPH_MIN_PX = 4                   # ... and at least this tall
GLYPH_ASPECT = 3.0                 # width / height <= 3 (a letter, not a line)
GLYPH_ROW_MIN = 2                  # >= 2 aligned components form a glyph row (50' has two digits)
GLYPH_GAP = 0.8                    # x the row height: largest gap between two glyphs of a row
GLYPH_UPSCALE = 3
GLYPH_PSM = 7
ROW_TEXT_HEIGHT = 36.0             # px: glyph rows are read with their text scaled to this height
PAGE_PSM = 11                      # sparse text, as room_labels.TESSERACT_PSM
OVERLAP = 0.5                      # a glyph row and a page item covering >= 50 % of the smaller box read one text
LINE_ART_PX = 25                   # long line art (in rectified pixels) painted out before OCR ...
LINE_ART_TEXT = 2.2                # ... and at least this many text heights (large dimension texts stay)
SWING_MIN_PX = 25.0                # arcs painted out before OCR: radius >= this (letters are smaller)
VERIFY_HEIGHTS = (26.0, 36.0, 48.0)  # px: the three extra reads of a number text
OCR_SCALE = 2.0                    # the OCR reads the page rendered 2 x larger (8 pt texts at 150 dpi)


def _box_overlap(a, b) -> float:
    """Intersection over the smaller box."""
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return ix * iy / small if small > 0 else 0.0


def _text_height_px(item: dict) -> float:
    x0, y0, x1, y1 = item["box"]
    return (x1 - x0) if item.get("rotation") == 90 else (y1 - y0)


def glyph_rows(ink: np.ndarray, height_hint: Optional[float] = None, max_px: int = GLYPH_MAX_PX,
               min_px: int = GLYPH_MIN_PX) -> list[dict]:
    """Rows of character-sized ink components (§4.2's character filter): components <= ``max_px``, aspect <=
    ``GLYPH_ASPECT``, >= ``GLYPH_ROW_MIN`` aligned (centres within 0.35 x the height, gaps <= ``GLYPH_GAP`` x the
    height). Horizontal rows (rotation 0) and vertical ones (rotation 90, text running bottom to top). Returns
    ``[{"box": [x0, y0, x1, y1], "labels": [component labels], "rotation", "label_image"}]`` (the label image is
    shared by all rows)."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(np.asarray(ink, np.uint8), connectivity=8)
    comps = []
    for i in range(1, n):
        x, y, w, h, area = (int(v) for v in stats[i])
        if max(w, h) > max_px or max(w, h) < min_px or area < 4:
            continue
        comps.append((i, x, y, w, h))
    rows: list[dict] = []
    for rotation in (0, 90):
        # In the rotation-90 frame a glyph's height runs along x and the reading direction is decreasing y.
        items = []
        for i, x, y, w, h in comps:
            gh, gw = (h, w) if rotation == 0 else (w, h)
            if gw > GLYPH_ASPECT * gh and gw > 6:
                continue
            if height_hint and not 0.4 * height_hint <= gh <= 2.5 * height_hint:
                continue
            if rotation == 0:
                items.append((x, y + h / 2.0, x + w, gh, i, (x, y, x + w, y + h)))
            else:
                items.append((-(y + h), x + w / 2.0, -y, gh, i, (x, y, x + w, y + h)))
        items.sort()
        used = set()
        for k, first in enumerate(items):
            if first[4] in used:
                continue
            row = [first]
            for nxt in items[k + 1:]:
                if nxt[4] in used:
                    continue
                last = row[-1]
                hgt = max(statistics_median([r[3] for r in row]), 1.0)
                if nxt[0] - last[2] > GLYPH_GAP * hgt:
                    if nxt[0] - last[2] > 3 * hgt:
                        break
                    continue
                if abs(nxt[1] - first[1]) > 0.35 * hgt or not 0.4 <= nxt[3] / hgt <= 2.5:
                    continue
                row.append(nxt)
            if len(row) < GLYPH_ROW_MIN:
                continue
            for r in row:
                used.add(r[4])
            boxes = [r[5] for r in row]
            rows.append({"box": [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes),
                                 max(b[3] for b in boxes)], "labels": [r[4] for r in row], "rotation": rotation,
                         "label_image": lab, "stats": stats})
    return rows


def statistics_median(values) -> float:
    vals = sorted(values)
    if not vals:
        return 0.0
    m = len(vals) // 2
    return float(vals[m]) if len(vals) % 2 else (vals[m - 1] + vals[m]) / 2.0


def _tesseract_env() -> dict:
    """Tesseract's OpenMP threads make it 20-30 x slower on a busy machine (measured: 0.5 s with one thread, 13 s
    with four, under load); the pipeline runs one image per call."""
    import os
    env = dict(os.environ)
    env["OMP_THREAD_LIMIT"] = "1"
    return env


def tesseract(img: np.ndarray, psm: int, rotation: int = 0) -> list[dict]:
    """Tesseract 5 (``eng+tur``, oem 1) on a grey array as line items (``ocr.parse_tesseract_tsv``), boxes in the
    array's pixels; ``rotation`` 90 reads the image turned clockwise (text running bottom to top) and maps the boxes
    back. A failed run gives no items."""
    from wenart.recognition import ocr as OCR
    from wenart.recognition import room_labels as RL

    arr = np.asarray(img, dtype=np.uint8)
    turned = arr if rotation == 0 else cv2.rotate(arr, cv2.ROTATE_90_CLOCKWISE)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ocr.png"
        cv2.imwrite(str(path), turned)
        cmd = ["tesseract", str(path), "stdout", "--oem", str(RL.TESSERACT_OEM), "--psm", str(psm), "-l",
               RL.TESSERACT_LANG, "tsv"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, check=True, env=_tesseract_env())
        except (subprocess.SubprocessError, OSError):
            return []
    items = OCR.parse_tesseract_tsv(proc.stdout, engine=f"tesseract-{RL.TESSERACT_LANG}-psm{psm}")
    for it in items:
        if rotation == 90:
            x0, y0, x1, y1 = it["box"]
            it["box"] = [y0, arr.shape[0] - x1, y1, arr.shape[0] - x0]
        it["rotation"] = rotation
    return items


def _tesseract_line(img: np.ndarray, rotation: int) -> list[dict]:
    return tesseract(img, GLYPH_PSM, rotation)


def read_glyph_rows(gray: np.ndarray, rows: list[dict], pad: int = 6) -> list[dict]:
    """Tesseract (psm 7) on each glyph row cut out alone: only the row's own components (and the small marks inside
    its box) keep their grey values, everything else is paper; scaled to ``ROW_TEXT_HEIGHT`` px text and binarised
    (``_read_line``). Items in ``gray``'s pixels (``rotation``, ``source "glyph_row"``); a row read as nothing gives
    no item."""
    out = []
    h, w = gray.shape
    for row in rows:
        x0, y0, x1, y1 = row["box"]
        c0, r0, c1, r1 = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)
        lab = row["label_image"][r0:r1, c0:c1]
        # The row's glyphs plus the small marks inside its box (commas, dots, the dot of İ, the cedilla of Ç).
        st = row["stats"]
        rh = (y1 - y0) if row["rotation"] == 0 else (x1 - x0)
        g = 0.3 * rh
        marks = np.nonzero((st[:, 0] >= x0 - g) & (st[:, 1] >= y0 - g) & (st[:, 0] + st[:, 2] <= x1 + g)
                           & (st[:, 1] + st[:, 3] <= y1 + g) & (np.maximum(st[:, 2], st[:, 3]) <= rh))[0]
        members = set(row["labels"]) | {int(i) for i in marks if i > 0}
        keep = np.isin(lab, sorted(members))
        keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        crop = np.full(lab.shape, 255, np.uint8)
        crop[keep] = gray[r0:r1, c0:c1][keep]
        text, conf = _read_line(crop, row["rotation"], float(rh), ROW_TEXT_HEIGHT)
        if not text:
            continue
        out.append({"text": text, "confidence": conf, "box": [float(x0), float(y0), float(x1), float(y1)],
                    "rotation": row["rotation"], "source": "glyph_row"})
    return out


def line_art(ink: np.ndarray, min_len: int) -> np.ndarray:
    """The long horizontal and vertical ink runs (morphological opening with a 1 x L and an L x 1 line): wall faces,
    furniture sides, dimension lines. Letters are shorter and stay."""
    ink8 = np.asarray(ink, dtype=np.uint8)
    hor = cv2.morphologyEx(ink8, cv2.MORPH_OPEN, np.ones((1, min_len), np.uint8))
    ver = cv2.morphologyEx(ink8, cv2.MORPH_OPEN, np.ones((min_len, 1), np.uint8))
    return (hor | ver) > 0


def _drawing_box(ink: np.ndarray, margin: int = 20) -> tuple[int, int, int, int]:
    """Bounding box of the ink components larger than a speck, grown by ``margin`` (c0, r0, c1, r1)."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(np.asarray(ink, np.uint8), connectivity=8)
    keep = [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= 12]
    h, w = ink.shape
    if not keep:
        return 0, 0, w, h
    st = stats[keep]
    c0, r0 = int(st[:, 0].min()), int(st[:, 1].min())
    c1, r1 = int((st[:, 0] + st[:, 2]).max()), int((st[:, 1] + st[:, 3]).max())
    return max(0, c0 - margin), max(0, r0 - margin), min(w, c1 + margin), min(h, r1 + margin)


def ocr_image(original: np.ndarray, to_original, size: tuple[int, int], scale: float) -> np.ndarray:
    """The rectified page rendered ``scale`` x larger straight from the original image (one cubic resampling, the
    lighting flattened first): the image the OCR reads."""
    flat = RF.flatten_illumination(np.asarray(original, dtype=np.uint8))
    s = np.diag([scale, scale, 1.0])
    # Pixel-centre convention: rectified pixel x maps to scale * (x + 0.5) - 0.5 in the big image.
    s[0, 2] = s[1, 2] = 0.5 * scale - 0.5
    fwd = s @ np.linalg.inv(np.asarray(to_original, dtype=np.float64))
    w, h = int(round(size[0] * scale)), int(round(size[1] * scale))
    return cv2.warpPerspective(flat, fwd, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT,
                               borderValue=255)


def _merge_items(items: list[dict], extra: list[dict]) -> list[dict]:
    """Add ``extra`` items: one that overlaps an item of the same rotation (``OVERLAP``) replaces it only with a
    higher confidence."""
    items = list(items)
    for r in extra:
        clash = [i for i in items if i.get("rotation") == r["rotation"] and _box_overlap(i["box"], r["box"]) >= OVERLAP]
        if clash and max(c["confidence"] for c in clash) >= r["confidence"]:
            continue
        for c in clash:
            items.remove(c)
        items.append(r)
    return items


def ocr_page(original: np.ndarray, rect: RF.Rectified, scale: float = OCR_SCALE,
             arcs_img: Optional[list] = None) -> list[dict]:
    """Every text of the page, in rectified pixels (pixel-corner boxes, x right, y down).

    The page is rendered ``scale`` x larger from the original (``ocr_image``). A first Tesseract pass (psm 11, 0° and
    90°) on the drawing area measures the text height; the line art longer than max(25 px, 2.2 x that height) and the
    door swings are then painted out (``line_art``: letters, also the large ones of an overall dimension, stay) and
    read again by the page pass (``source "page"``) and the glyph-row pass, which reads each row of character
    components alone (``source "glyph_row"``). Overlapping reads keep the most confident one; numbers and lengths
    must agree in two of three reads (``_verify_numbers``)."""
    w, h = rect.size
    big = ocr_image(original, rect.to_original, (w, h), scale)
    ink = RF.ink_mask(big)
    base_len = int(round(LINE_ART_PX * scale))
    c0, r0, c1, r1 = _drawing_box(ink & ~line_art(ink, base_len), margin=int(20 * scale))

    def back(box) -> list[float]:
        # Boxes are pixel-corner coordinates: they scale by 1 / scale exactly.
        return [round(v / scale, 2) for v in box]

    def page_pass(img: np.ndarray, source: str) -> list[dict]:
        out = []
        crop = img[r0:r1, c0:c1]
        for it in tesseract(crop, PAGE_PSM, 0) + tesseract(crop, PAGE_PSM, 90):
            it = dict(it)
            x0, y0, x1, y1 = it["box"]
            it["box"] = back((c0 + x0, r0 + y0, c0 + x1, r0 + y1))
            it["source"] = source
            out.append(it)
        return out

    first = page_pass(big, "page_raw")
    words = [_text_height_px(i) * scale for i in first
             if i["confidence"] >= 0.8 and sum(ch.isalnum() for ch in str(i["text"])) >= 3]
    text_h = statistics_median(words) if words else 0.0
    lines = line_art(ink, max(base_len, int(round(LINE_ART_TEXT * text_h))))
    if arcs_img:
        # Door swings are line art too: a label beside an arc otherwise reads as one glyph with it.
        swing = np.zeros(ink.shape, np.uint8)
        for cx, cy, r, a0, a1 in arcs_img:
            if r < SWING_MIN_PX or a1 - a0 < 60.0:
                continue                                 # letters have curves too (S, O, 3): only door-sized swings
            centre = (int(round(((cx + 0.5) * scale - 0.5) * 16)), int(round(((cy + 0.5) * scale - 0.5) * 16)))
            axes = (int(round(r * scale * 16)), int(round(r * scale * 16)))
            cv2.ellipse(swing, centre, axes, 0.0, a0, a1, 1, thickness=int(round(2.5 * scale)), lineType=cv2.LINE_8,
                        shift=4)
        lines = lines | ((swing > 0) & ink)
    text_ink = ink & ~lines
    clean = big.copy()
    clean[lines] = 255
    items = page_pass(clean, "page")
    good = [_text_height_px(i) * scale for i in items if i["confidence"] >= TEXT_CONF]
    hint = statistics_median(good) if good else None
    rows = glyph_rows(text_ink, hint, max_px=int(max(GLYPH_MAX_PX * scale, 2.5 * text_h)),
                      min_px=int(GLYPH_MIN_PX * scale))
    row_items = read_glyph_rows(clean, rows)
    for r in row_items:
        r["box"] = back(r["box"])
    items = _merge_items(items, row_items)
    items = _merge_items(items, first)
    _verify_numbers(items, clean, scale)
    items = join_size_pairs(items)
    items.sort(key=lambda i: (i.get("rotation", 0), i["box"][1], i["box"][0]))
    return items


_MARKS = str.maketrans({"’": "'", "‘": "'", "′": "'", "`": "'", "´": "'", "°": "'", "”": '"', "“": '"', "″": '"',
                        "X": "x", "×": "x"})


def _number_key(text: str) -> str:
    """The comparison form of a number or length read: no spaces, ``.`` = ``,``, quote and prime marks (and the
    degree sign Tesseract reads for a foot mark) as ASCII, ``X``/``×`` as ``x``."""
    return re.sub(r"\s+", "", str(text)).replace(".", ",").translate(_MARKS)


def _numeric(text: str) -> bool:
    from wenart import units as U
    t = str(text).strip()
    return bool(t) and any(ch.isdigit() for ch in t) and (bool(_NUMBER_RE.match(t)) or U.parse_length(t) is not None)


def _read_line(crop: np.ndarray, rotation: int, text_h: float, target_h: float) -> tuple[str, float]:
    """One psm 7 read of a text crop scaled so its text is ``target_h`` px tall (Tesseract reads 20-50 px text
    best; 8 pt labels at 150 dpi are 12 px, an overall dimension may be 40), binarised (Otsu)."""
    factor = max(0.25, min(8.0, target_h / max(text_h, 1.0)))
    big = cv2.resize(crop, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC if factor > 1 else cv2.INTER_AREA)
    _, binary = cv2.threshold(big, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    binary = cv2.copyMakeBorder(binary, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
    got = tesseract(binary, GLYPH_PSM, rotation)
    return " ".join(g["text"] for g in got).strip(), min((g["confidence"] for g in got), default=0.0)


def _verify_numbers(items: list[dict], clean: np.ndarray, scale: float) -> None:
    """Digits are where Tesseract errs with high confidence (``4,30`` read ``4,70`` at 0.96, ``50'`` read ``20'`` when
    the digits are 70 px tall): every number or length text is read three more times from its box alone (psm 7, its
    text scaled to ``VERIFY_HEIGHTS`` px) and kept only when one reading wins a strict majority of the four reads
    with at least two votes (spaces ignored, ``.`` = ``,``, quote/prime marks unified); the winning spelling is kept
    and the confidence is the lowest of its votes. Otherwise the item's confidence drops to 0 (not used). The reads
    are recorded in ``item["reads"]``."""
    h, w = clean.shape
    for it in items:
        first = str(it["text"]).strip()
        if not _numeric(first):
            continue
        x0, y0, x1, y1 = (v * scale for v in it["box"])
        pad = int(round(3 * scale))
        c0, r0 = max(0, int(math.floor(x0)) - pad), max(0, int(math.floor(y0)) - pad)
        c1, r1 = min(w, int(math.ceil(x1)) + pad), min(h, int(math.ceil(y1)) + pad)
        crop = clean[r0:r1, c0:c1]
        if crop.size == 0:
            continue
        rotation = int(it.get("rotation") or 0)
        text_h = (x1 - x0) if rotation == 90 else (y1 - y0)
        reads = [(first, float(it["confidence"]))]
        for target in VERIFY_HEIGHTS:
            reads.append(_read_line(crop, rotation, text_h, target))
        it["reads"] = [r[0] for r in reads]
        keys = [_number_key(r[0]) for r in reads]
        votes = {k: [r for r, kk in zip(reads, keys) if kk == k] for k in dict.fromkeys(keys) if k}
        ranked = sorted(votes.items(), key=lambda kv: -len(kv[1]))
        if not ranked or len(ranked[0][1]) < 2 or (len(ranked) > 1 and len(ranked[1][1]) == len(ranked[0][1])):
            it["confidence"] = 0.0
            it["verify"] = "reads disagree"
            continue
        agree = ranked[0][1]
        # The spelling: the first agreeing read that parses as a length or a size, else the first agreeing read.
        from wenart import units as U
        parsed = [r for r in agree if U.parse_length(r[0]) is not None or U.parse_size_pair(r[0]) is not None]
        it["text"] = (parsed or agree)[0][0]
        it["confidence"] = round(min(c for _, c in agree), 4)
        it["verify"] = f"{len(agree)} of {len(reads)} reads agree"


_NUMBER_RE = re.compile(r"^[\d.,'\"’″′\s/xX×*+-]+$")
SIZE_PAIR_GAP = 1.5                # x the text height: two OCR pieces of one line this close may be one size text


def _next_on_line(a: dict, b: dict) -> bool:
    """``b`` follows ``a`` on the same text line (same rotation, rows overlapping by >= half the lower one, gap
    along the reading direction between -0.3 and ``SIZE_PAIR_GAP`` text heights). Rotation 90 reads bottom to top."""
    if int(a.get("rotation") or 0) != int(b.get("rotation") or 0):
        return False
    ax0, ay0, ax1, ay1 = a["box"]
    bx0, by0, bx1, by1 = b["box"]
    h = max(_text_height_px(a), _text_height_px(b), 1e-6)
    if int(a.get("rotation") or 0) == 90:
        across = min(ax1, bx1) - max(ax0, bx0)
        lower = min(ax1 - ax0, bx1 - bx0)
        gap = ay0 - by1
    else:
        across = min(ay1, by1) - max(ay0, by0)
        lower = min(ay1 - ay0, by1 - by0)
        gap = bx0 - ax1
    return across >= 0.5 * max(lower, 1e-6) and -0.3 * h <= gap <= SIZE_PAIR_GAP * h


def join_size_pairs(items: list[dict]) -> list[dict]:
    """Pieces of one printed size text read as separate OCR items on one line ("11" then "x 10": a 300 dpi scan
    reads the label "11' x 10'" in pieces) become one item: text joined with a space, box the union, the lower
    confidence, ``source "joined"``, ``parts`` the pieces. A size-pair member alone reads as a length and must
    never become a dimension text. Only neighbours whose joined text parses as a size pair while neither piece
    alone does are joined."""
    from wenart import units as U

    out = [dict(i) for i in items]
    joined = True
    while joined:
        joined = False
        for a in out:
            ta = str(a.get("text") or "").strip()
            if not ta or U.parse_size_pair(ta) is not None:
                continue
            for b in out:
                tb = str(b.get("text") or "").strip()
                if b is a or not tb or U.parse_size_pair(tb) is not None or not _next_on_line(a, b):
                    continue
                text = f"{ta} {tb}"
                if U.parse_size_pair(text) is None:
                    continue
                box = [min(a["box"][0], b["box"][0]), min(a["box"][1], b["box"][1]),
                       max(a["box"][2], b["box"][2]), max(a["box"][3], b["box"][3])]
                item = dict(a, text=text, box=box, source="joined",
                            confidence=min(float(a.get("confidence") or 0.0), float(b.get("confidence") or 0.0)),
                            parts=[{k: p.get(k) for k in ("text", "box", "confidence", "source")} for p in (a, b)])
                item.pop("reads", None)
                item.pop("verify", None)
                out = [i for i in out if i is not a and i is not b] + [item]
                joined = True
                break
            if joined:
                break
    return out


def blankable(item: dict, median_h: float) -> bool:
    """§4.2: a text box is blanked only when conf >= 0.6, the text is a room-vocabulary word, a number, a length or
    a size pattern, and its height is 0.5-2 x the median text height."""
    from wenart import building as B
    from wenart import units as U

    if item["confidence"] < TEXT_CONF:
        return False
    text = str(item["text"]).strip()
    if not text:
        return False
    h = _text_height_px(item)
    if median_h and not BLANK_HEIGHT[0] * median_h <= h <= BLANK_HEIGHT[1] * median_h:
        return False
    if _NUMBER_RE.match(text) and any(ch.isdigit() for ch in text):
        return True
    if U.parse_length(text) is not None or U.parse_size_pair(text) is not None or U.parse_area(text) is not None:
        return True
    turkish, english = B.room_keyword_hits(text)
    if turkish or english:
        return True
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.model import page_class_for, parse_scale_text
    if LB.room_type_for(text)[1] or page_class_for(text) is not None or parse_scale_text(text):
        return True
    return B.normalise_level_label(text) is not None


def _swing_mask(shape, arcs_img: Optional[list]) -> Optional[np.ndarray]:
    """The door swings (arcs of ``r >= SWING_MIN_PX`` and >= 60°, image frame) drawn 3 px wide."""
    if not arcs_img:
        return None
    swing = np.zeros(shape, np.uint8)
    for cx, cy, r, a0, a1 in arcs_img:
        if r < SWING_MIN_PX or a1 - a0 < 60.0:
            continue
        cv2.ellipse(swing, (int(round(cx * 16)), int(round(cy * 16))), (int(round(r * 16)), int(round(r * 16))),
                    0.0, a0, a1, 1, thickness=3, lineType=cv2.LINE_8, shift=4)
    return swing > 0 if swing.any() else None


def blank_texts(ink: np.ndarray, items: list[dict], line_len: int = LINE_ART_PX,
                arcs_img: Optional[list] = None) -> tuple[np.ndarray, int]:
    """Clear the ink components that lie wholly inside a blankable text box (grown by 2 px); a line passing through
    the box is longer than the box and stays. Inside the box of a number or length text (a dimension text, which
    sits on its dimension line) every pixel that is not long line art goes too, so a comma touching the line does not
    cut it into pieces; inside a word box whose letters touch a drawn line or a door swing (``arcs_img``), every pixel
    off the swings and off the line art running on outside the box goes, so the letter does not stay as a stub on the
    line. Returns (ink, number of boxes blanked)."""
    from wenart import units as U

    good = [_text_height_px(i) for i in items if i["confidence"] >= TEXT_CONF]
    median_h = statistics_median(good) if good else 0.0
    out = np.asarray(ink, dtype=bool).copy()
    n, lab, stats, _ = cv2.connectedComponentsWithStats(out.astype(np.uint8), connectivity=8)
    clear = np.zeros(n, bool)
    lines = None
    h, w = out.shape
    swings = _swing_mask(out.shape, arcs_img)
    blanked = 0
    for it in items:
        if not blankable(it, median_h):
            it["blanked"] = False
            continue
        x0, y0, x1, y1 = it["box"]
        x0, y0, x1, y1 = x0 - 2, y0 - 2, x1 + 2, y1 + 2
        inside = ((stats[:, 0] >= x0) & (stats[:, 1] >= y0) & (stats[:, 0] + stats[:, 2] <= x1 + 1)
                  & (stats[:, 1] + stats[:, 3] <= y1 + 1))
        inside[0] = False
        clear |= inside
        text = str(it["text"]).strip()
        numeric = bool(_NUMBER_RE.match(text)) or U.parse_length(text) is not None
        c0, r0 = max(0, int(math.floor(x0))), max(0, int(math.floor(y0)))
        c1, r1 = min(w, int(math.ceil(x1))), min(h, int(math.ceil(y1)))
        if numeric:
            if lines is None:
                lines = line_art(out, line_len)
            out[r0:r1, c0:c1] &= lines[r0:r1, c0:c1]
        else:
            ids = np.unique(lab[r0:r1, c0:c1])
            touching = [k for k in ids if k and not inside[k]]
            if touching:
                # A letter joined to a drawn line or swing: every pixel off the swings and off the line art that
                # runs on outside the box goes (a row of touching letters is line art too, but stays inside).
                if lines is None:
                    lines = line_art(out, line_len)
                sub = lines[r0:r1, c0:c1].astype(np.uint8)
                m, slab, sst, _ = cv2.connectedComponentsWithStats(sub, connectivity=8)
                through = np.zeros(m, bool)
                for k in range(1, m):
                    x, y, bw, bh = (int(v) for v in sst[k, :4])
                    through[k] = (x == 0 and c0 > 0) or (x + bw == c1 - c0 and c1 < w) or \
                        (y == 0 and r0 > 0) or (y + bh == r1 - r0 and r1 < h)
                keep = through[slab]
                if swings is not None:
                    keep |= swings[r0:r1, c0:c1]
                out[r0:r1, c0:c1] &= keep
        it["blanked"] = True
        blanked += 1
    out[clear[lab]] = False
    return out, blanked


# --------------------------------------------------------------------------
# Wall mask (§4.2)
# --------------------------------------------------------------------------

WALL_MAX_M = 0.50                  # outline walls: the band between two lines is <= 0.50 m ...
BAND_MIN_PX = 1                    # ... and at least this wide inside (lines >= 3 px apart centre to centre)
ELONGATION = 3.0                   # a wall band / filled wall is >= 3 x as long as it is thick
RECTANGULAR = 0.75                 # region area / its minimum rectangle: a rectangle-like band
SEED_EXTERIOR = 0.5                # a seed band runs along the outside over >= 50 % of its length ...
SEED_ROOM = 0.2                    # ... and along a room over >= 20 %
SIDE_REJECT = 0.5                  # a band whose long side runs along an accepted band over >= 50 % is not a wall
ROOM_MIN_M2 = 1.0                  # a background region this large is a room (or the outside)
FURNITURE_LOOP_M = 3.0             # a closed 4-sided loop <= 3 m per side whose ends touch no band is furniture
GAP_REACH_M = 1.2                  # a band end may face its continuation across a door gap this wide
FILLED_MIN_DT_PX = 3               # filled walls: the lowest distance-transform mode >= 3 px ...
FILLED_MODE_SHARE = 0.08           # ... holding >= 8 % of all ridge pixels (a photo's blurred double lines: < 3 %)
FILLED_RING_M2 = 2.0               # closed thin rings enclosing < 2 m² are not walls
FILLED_SIDE_PX = 5                 # paper regions within this of a filled piece are its neighbours
BAND_LINE_MIN_M = 0.30             # outline walls: lines of a band are >= 0.30 m long ...
BAND_MIN_GAP_PX = 3.0              # ... >= 3 px apart ...
BAND_ANGLE_DEG = 1.5               # ... parallel ...
BAND_OVERLAP = 0.70                # ... and overlap along >= 70 % of the shorter one
BAND_THIRD_LINE = 0.50             # a third parallel line inside along >= 50 % of the band: not a wall band
SHORT_BAND_M = 1.0                 # a band shorter than this needs both ends on accepted bands
END_GROW_PX = 4.0                  # a band end lands on a band whose rectangle it reaches within this


def _ridge_mode(ink: np.ndarray) -> Optional[float]:
    """The lowest distance-transform mode >= ``FILLED_MIN_DT_PX`` on the ink's ridge (local maxima of the distance
    to the paper), or None when no thick ink exists."""
    dt = cv2.distanceTransform(np.asarray(ink, np.uint8), cv2.DIST_L2, 5)
    ridge = (dt >= 0.5) & (dt >= cv2.dilate(dt, np.ones((3, 3), np.uint8)) - 1e-3)
    vals = np.round(dt[ridge]).astype(int)
    if len(vals) < 50:
        return None
    hist = np.bincount(vals)
    total = hist[1:].sum()
    # A mode is a real peak: higher than its lower neighbour (the tail of the line peak at 1-3 px is no mode).
    for v in range(FILLED_MIN_DT_PX, len(hist)):
        right = hist[v + 1] if v + 1 < len(hist) else 0
        if hist[v] > hist[v - 1] and hist[v] >= right and hist[v] >= max(30, FILLED_MODE_SHARE * total):
            return float(v)
    return None


def filled_candidates(ink: np.ndarray) -> tuple[np.ndarray, dict]:
    """Filled (solid, hatched-solid) walls without a scale: opening with ``k = max(3, round(0.6 t_min))`` px,
    ``t_min`` = 2 x the lowest ridge mode; components without an elongated part (area >= 3 t²) are dropped."""
    info: dict = {"t_min_px": None, "kernel_px": None, "components": 0}
    mode = _ridge_mode(ink)
    if mode is None:
        return np.zeros(ink.shape, bool), info
    t_min = 2.0 * mode
    k = max(3, int(round(0.6 * t_min)))
    opened = cv2.morphologyEx(np.asarray(ink, np.uint8), cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
    keep = np.zeros(n, bool)
    dt = cv2.distanceTransform(opened, cv2.DIST_L2, 5)
    rows, cols = opened.shape
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        x, y, w, h = (int(v) for v in stats[i, :4])
        if x == 0 or y == 0 or x + w >= cols or y + h >= rows:
            continue                                  # the paper edge or the photo background, not a wall
        sub = lab[y:y + h, x:x + w] == i
        thick = 2.0 * float(np.percentile(dt[y:y + h, x:x + w][sub], 95)) if area else 0.0
        if thick > 0 and area >= ELONGATION * thick * thick:
            keep[i] = True
    mask = keep[lab]
    info.update(t_min_px=t_min, kernel_px=k, components=int(keep.sum()))
    return mask, info


def drop_small_rings(mask: np.ndarray, px_per_m: float, ink: Optional[np.ndarray] = None) -> tuple[np.ndarray, int]:
    """Filled components that are closed rings enclosing < 2 m² (a thick-framed table, a column casing) are no
    walls; with ``ink``, also the filled pieces whose ink is such a ring (a table frame drawn thick on two sides and
    thin on the other two keeps only an L after the opening) and the pieces whose neighbouring paper regions (within
    ``FILLED_SIDE_PX``) add up to < 2 m² and do not reach the image edge: thick lines inside a drawn object (a bed's
    pillow edge thickened by a photo's blur), where a wall always has a room or the outside beside it.
    Returns (mask, pieces dropped)."""
    out = np.asarray(mask, bool).copy()
    contours, hier = cv2.findContours(out.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hier is None:
        return out, 0
    dropped = 0
    limit = FILLED_RING_M2 * px_per_m * px_per_m
    for i, c in enumerate(contours):
        if hier[0][i][3] != -1 or hier[0][i][2] == -1:
            continue                                   # not an outer contour with a hole
        if cv2.contourArea(c) < limit:
            cv2.drawContours(out.view(np.uint8), [c], -1, 0, thickness=cv2.FILLED)
            dropped += 1
    if ink is None or not out.any():
        return out, dropped
    _, ink_lab = cv2.connectedComponents(np.asarray(ink, np.uint8), connectivity=8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(out.astype(np.uint8), connectivity=8)
    for i in range(1, n):
        piece = lab == i
        ids = np.unique(ink_lab[piece])
        ids = ids[ids > 0]
        if len(ids) != 1:
            continue
        ring = (ink_lab == ids[0]).astype(np.uint8)
        ys, xs = np.nonzero(ring)
        if (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1) >= 4 * limit:
            continue                                   # the wall network itself, not a small object
        rc, rh = cv2.findContours(ring, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        if rh is None:
            continue
        outer = [k for k in range(len(rc)) if rh[0][k][3] == -1]
        if len(outer) == 1 and rh[0][outer[0]][2] != -1 and cv2.contourArea(rc[outer[0]]) < limit:
            out[piece] = False
            dropped += 1
    ink8 = np.asarray(ink, np.uint8)
    sealed = (cv2.morphologyEx(ink8, cv2.MORPH_CLOSE, np.ones((1, 3), np.uint8))
              | cv2.morphologyEx(ink8, cv2.MORPH_CLOSE, np.ones((3, 1), np.uint8))) > 0
    _, bg_lab, bg_stats, _ = cv2.connectedComponentsWithStats((~sealed).astype(np.uint8), connectivity=4)
    rows, cols = sealed.shape
    k = 2 * FILLED_SIDE_PX + 1
    n, lab, stats, _ = cv2.connectedComponentsWithStats(out.astype(np.uint8), connectivity=8)
    for i in range(1, n):
        x, y, w, h = (int(v) for v in stats[i, :4])
        x0, y0 = max(0, x - k), max(0, y - k)
        x1, y1 = min(cols, x + w + k), min(rows, y + h + k)
        piece = (lab[y0:y1, x0:x1] == i).astype(np.uint8)
        near = cv2.dilate(piece, np.ones((k, k), np.uint8)) > 0
        ids = np.unique(bg_lab[y0:y1, x0:x1][near])
        ids = ids[ids > 0]
        if not len(ids):
            continue
        edge = any(bg_stats[j, 0] == 0 or bg_stats[j, 1] == 0 or bg_stats[j, 0] + bg_stats[j, 2] == cols
                   or bg_stats[j, 1] + bg_stats[j, 3] == rows for j in ids)
        if not edge and float(bg_stats[ids, cv2.CC_STAT_AREA].sum()) < limit:
            out[y0:y1, x0:x1][piece > 0] = False
            dropped += 1
    return out, dropped


@dataclass
class _Region:
    """A background region (paper between lines)."""
    label: int
    area: int
    box: tuple[int, int, int, int]               # c0, r0, c1, r1 (exclusive)
    thickness: float                             # 2 x the 95th percentile of the distance to the ink
    centre: tuple[float, float] = (0.0, 0.0)
    u: tuple[float, float] = (1.0, 0.0)          # long axis
    length: float = 0.0
    width: float = 0.0
    rectangular: float = 0.0
    exterior: bool = False


def _regions(bg: np.ndarray) -> tuple[np.ndarray, list[_Region]]:
    """4-connected background regions; the ones touching the image edge and the largest one (the sheet inside a
    drawn frame) are the outside."""
    n, lab, stats, _ = cv2.connectedComponentsWithStats(bg.astype(np.uint8), connectivity=4)
    h, w = bg.shape
    regions = []
    for i in range(1, n):
        x, y, bw, bh, area = (int(v) for v in stats[i])
        reg = _Region(label=i, area=area, box=(x, y, x + bw, y + bh), thickness=0.0)
        reg.exterior = x == 0 or y == 0 or x + bw == w or y + bh == h
        regions.append(reg)
    if regions:
        max(regions, key=lambda r: r.area).exterior = True
    return lab, regions


@dataclass
class _Band:
    """A wall band candidate between two parallel lines (image frame)."""
    k: int
    lines: tuple[int, int]                       # indices into the segment list
    u: tuple[float, float]                       # axis
    n: tuple[float, float]                       # normal
    origin: tuple[float, float]                  # a point on the first line
    a: float                                     # along-axis interval (overlap of the two lines)
    b: float
    o1: float                                    # offsets of the two lines (o1 < o2)
    o2: float

    @property
    def width(self) -> float:
        return self.o2 - self.o1

    @property
    def length(self) -> float:
        return self.b - self.a

    def point(self, along: float, off: float) -> tuple[float, float]:
        return (self.origin[0] + self.u[0] * along + self.n[0] * off,
                self.origin[1] + self.u[1] * along + self.n[1] * off)

    def local(self, p) -> tuple[float, float]:
        dx, dy = p[0] - self.origin[0], p[1] - self.origin[1]
        return dx * self.u[0] + dy * self.u[1], dx * self.n[0] + dy * self.n[1]

    def corners(self) -> list[tuple[float, float]]:
        return [self.point(self.a, self.o1), self.point(self.b, self.o1), self.point(self.b, self.o2),
                self.point(self.a, self.o2)]

    def contains(self, p, grow: float = 0.0) -> bool:
        al, off = self.local(p)
        return self.a - grow <= al <= self.b + grow and self.o1 - grow <= off <= self.o2 + grow


def _unit(a, b) -> tuple[float, float]:
    length = math.dist(a, b)
    return ((b[0] - a[0]) / length, (b[1] - a[1]) / length)


def wall_bands(segments: list[tuple[tuple[float, float], tuple[float, float]]], px_per_m: float,
               min_len_m: float = BAND_LINE_MIN_M) -> list[_Band]:
    """Pairs of long parallel lines >= 3 px and <= 0.50 m apart overlapping along >= 70 % of the shorter one, minus
    the pairs with a third parallel line inside the band along >= 50 % of it (§4.2)."""
    max_t = WALL_MAX_M * px_per_m
    long = [(i, a, b) for i, (a, b) in enumerate(segments) if math.dist(a, b) >= min_len_m * px_per_m]
    bands: list[_Band] = []
    geo = {}
    for i, a, b in long:
        geo[i] = (a, b, _unit(a, b))
    for x in range(len(long)):
        i, a1, b1 = long[x]
        u = geo[i][2]
        n = (-u[1], u[0])
        for y in range(x + 1, len(long)):
            j, a2, b2 = long[y]
            v = geo[j][2]
            if abs(u[0] * v[1] - u[1] * v[0]) > math.sin(math.radians(BAND_ANGLE_DEG)):
                continue
            offs = [(p[0] - a1[0]) * n[0] + (p[1] - a1[1]) * n[1] for p in (a2, b2)]
            off = sum(offs) / 2.0
            if not BAND_MIN_GAP_PX <= abs(off) <= max_t:
                continue
            t1 = sorted((0.0, (b1[0] - a1[0]) * u[0] + (b1[1] - a1[1]) * u[1]))
            t2 = sorted((p[0] - a1[0]) * u[0] + (p[1] - a1[1]) * u[1] for p in (a2, b2))
            lo, hi = max(t1[0], t2[0]), min(t1[1], t2[1])
            shorter = min(t1[1] - t1[0], t2[1] - t2[0])
            if hi - lo < BAND_OVERLAP * shorter or hi - lo <= 0:
                continue
            o1, o2 = sorted((0.0, off))
            bands.append(_Band(k=len(bands), lines=(i, j), u=u, n=n, origin=a1, a=lo, b=hi, o1=o1, o2=o2))
    # A third parallel line inside the band along >= 50 % of it: not one wall band.
    out = []
    for band in bands:
        spans = []
        for i, a, b in long:
            if i in band.lines:
                continue
            ua = geo[i][2]
            if abs(ua[0] * band.u[1] - ua[1] * band.u[0]) > math.sin(math.radians(BAND_ANGLE_DEG)):
                continue
            (ta, oa), (tb, ob) = band.local(a), band.local(b)
            mid_off = (oa + ob) / 2.0
            if not band.o1 + 1.5 < mid_off < band.o2 - 1.5:
                continue
            lo, hi = max(band.a, min(ta, tb)), min(band.b, max(ta, tb))
            if hi > lo:
                spans.append((lo, hi))
        if _union_length(spans) < BAND_THIRD_LINE * band.length:
            out.append(band)
    for k, band in enumerate(out):
        band.k = k
    return out


def _union_length(spans: list[tuple[float, float]]) -> float:
    total, end = 0.0, -math.inf
    for lo, hi in sorted(spans):
        if hi <= end:
            continue
        total += hi - max(lo, end)
        end = hi
    return total


def _side_labels(band: _Band, lab: np.ndarray, side: int, step: float = 3.0) -> list[int]:
    """Region labels sampled 3 px outside one long side of a band (side -1: beyond o1, +1: beyond o2)."""
    h, w = lab.shape
    off = (band.o1 - 3.0) if side < 0 else (band.o2 + 3.0)
    out = []
    for al in np.arange(band.a + 2.0, band.b - 2.0, step):
        x, y = band.point(float(al), off)
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < w and 0 <= yi < h:
            out.append(int(lab[yi, xi]))
    return out


def _closed_small_loop(band: _Band, segments, px_per_m: float) -> bool:
    """§4.2: the band's two lines are joined at both ends by short perpendicular strokes (a closed 4-sided loop)
    whose sides are <= 3 m: a drawn object (furniture, a window frame), not a wall band."""
    if band.length > FURNITURE_LOOP_M * px_per_m:
        return False
    ends = 0
    for t in (band.a, band.b):
        p1, p2 = band.point(t, band.o1), band.point(t, band.o2)
        for a, b in segments:
            length = math.dist(a, b)
            if length < 1.0 or length > band.width + 6.0:
                continue
            if (math.dist(a, p1) <= 3.0 and math.dist(b, p2) <= 3.0) or \
                    (math.dist(a, p2) <= 3.0 and math.dist(b, p1) <= 3.0):
                ends += 1
                break
    return ends == 2


def long_lines(ink: np.ndarray, px_per_m: float, min_len_m: float = BAND_LINE_MIN_M) -> list:
    """The long horizontal and vertical lines of the ink as segments (image frame): connected pieces of the
    morphological opening with a 1 x L (L x 1) line, L = ``min_len_m``; each piece becomes the segment through its
    pixels' mean cross position over its extent. A line with furniture drawn against it stays one (slightly thicker)
    line here, where the skeleton would break it at every junction."""
    length = max(15, int(round(min_len_m * px_per_m)))
    ink8 = np.asarray(ink, np.uint8)
    out = []
    for axis in ("h", "v"):
        kernel = np.ones((1, length), np.uint8) if axis == "h" else np.ones((length, 1), np.uint8)
        opened = cv2.morphologyEx(ink8, cv2.MORPH_OPEN, kernel)
        n, lab, stats, _ = cv2.connectedComponentsWithStats(opened, connectivity=8)
        for i in range(1, n):
            x, y, w, h, area = (int(v) for v in stats[i])
            ys, xs = np.nonzero(lab[y:y + h, x:x + w] == i)
            if axis == "h":
                if w < length:
                    continue
                c = float(ys.mean()) + y
                out.append(((float(x), c), (float(x + w - 1), c)))
            else:
                if h < length:
                    continue
                c = float(xs.mean()) + x
                out.append(((c, float(y)), (c, float(y + h - 1))))
    return out


def outline_walls(ink: np.ndarray, px_per_m: float) -> tuple[np.ndarray, dict]:
    """Outline-wall bands (§4.2): ``wall_bands`` of the long horizontal and vertical lines (``long_lines``, image
    frame; dimension strokes already erased from ``ink``), seeded from the bands that run along the outside on one
    side and a room on the other, and grown along the walls: a band is accepted when both of its ends land on
    accepted bands (directly, or across a door-wide gap along its axis); rejected when it is a closed small loop or
    when it lies beside an accepted band (sharing one of its lines, e.g. furniture against a wall). The mask is the
    accepted bands from line centre to line centre."""
    segments = long_lines(ink, px_per_m)
    info: dict = {"candidates": 0, "seeds": 0, "accepted": 0}
    bands = wall_bands(segments, px_per_m)
    info["candidates"] = len(bands)
    h, w = ink.shape
    mask = np.zeros((h, w), bool)
    if not bands:
        return mask, info
    ink8 = np.asarray(ink, np.uint8)
    sealed = (cv2.morphologyEx(ink8, cv2.MORPH_CLOSE, np.ones((1, 3), np.uint8))
              | cv2.morphologyEx(ink8, cv2.MORPH_CLOSE, np.ones((3, 1), np.uint8))) > 0
    lab, regions = _regions(~sealed)
    exterior = {r.label for r in regions if r.exterior}
    room = {r.label for r in regions if r.area >= ROOM_MIN_M2 * px_per_m * px_per_m}
    rejected: dict[int, str] = {}
    for band in bands:
        if _closed_small_loop(band, segments, px_per_m):
            rejected[band.k] = "closed loop of <= 3 m sides (a drawn object)"
    accepted: set[int] = set()
    for band in bands:
        if band.k in rejected:
            continue
        sides = [_side_labels(band, lab, -1), _side_labels(band, lab, +1)]
        if not sides[0] or not sides[1]:
            continue
        ext = [sum(1 for v in sd if v in exterior) / len(sd) for sd in sides]
        rm = [sum(1 for v in sd if v in room and v not in exterior) / len(sd) for sd in sides]
        if (ext[0] >= SEED_EXTERIOR and rm[1] >= SEED_ROOM) or (ext[1] >= SEED_EXTERIOR and rm[0] >= SEED_ROOM):
            accepted.add(band.k)
    info["seeds"] = len(accepted)
    seeds = set(accepted)
    by_k = {b.k: b for b in bands}
    reach = GAP_REACH_M * px_per_m

    def end_lands(band: _Band, t: float, sign: float, pool: set, gap: bool) -> bool:
        """The band's end reaches a band of ``pool`` directly, or (``gap``) across a door-wide gap along its axis."""
        mid = band.point(t, (band.o1 + band.o2) / 2.0)
        for k in pool:
            other = by_k[k]
            if other.k != band.k and other.contains(mid, grow=END_GROW_PX):
                return True
        if not gap:
            return False
        for k in pool:
            other = by_k[k]
            if other.k == band.k or abs(other.u[0] * band.u[1] - other.u[1] * band.u[0]) > 0.02:
                continue
            for d in np.arange(END_GROW_PX, reach, 2.0):
                q = (mid[0] + sign * band.u[0] * d, mid[1] + sign * band.u[1] * d)
                if other.contains(q, grow=1.0):
                    return True
        return False

    def beside_accepted(band: _Band) -> bool:
        for k in accepted:
            other = by_k[k]
            shared = set(band.lines) & set(other.lines)
            if not shared:
                continue
            mid = band.point((band.a + band.b) / 2.0, (band.o1 + band.o2) / 2.0)
            if not other.contains(mid, grow=1.0):
                return True
        return False

    changed = True
    while changed:
        changed = False
        for band in sorted(bands, key=lambda b: -b.length):      # long walls first: a wall beats a closet beside it
            if band.k in accepted or band.k in rejected:
                continue
            mid = band.point((band.a + band.b) / 2.0, (band.o1 + band.o2) / 2.0)
            if any(by_k[k].contains(mid, grow=1.0) and by_k[k].width >= band.width for k in accepted):
                rejected[band.k] = "inside a wall band (window or frame lines)"
                continue
            if beside_accepted(band):
                rejected[band.k] = "beside a wall band (shares its line)"
                continue
            # Both ends on wall bands, at least one of them accepted (two walls that only meet each other, like
            # the arms of a crossing, wait for each other otherwise).
            open_pool = {b.k for b in bands if b.k not in rejected}
            ends = [(band.a, -1.0), (band.b, +1.0)]
            on_accepted = [end_lands(band, t, sg, accepted, True) for t, sg in ends]
            on_any = [on_accepted[i] or end_lands(band, t, sg, open_pool, False) for i, (t, sg) in enumerate(ends)]
            # Short bands (a pair of furniture sides at a wall) need both ends on accepted bands.
            short = band.length < SHORT_BAND_M * px_per_m
            if (all(on_accepted) if short else (all(on_any) and any(on_accepted))):
                accepted.add(band.k)
                changed = True
    for k in accepted:
        poly = np.array(by_k[k].corners(), dtype=np.float64)
        # Line centre to line centre; pixel centres (image frame) -> cv2 fill with subpixel shift.
        cv2.fillPoly(mask.view(np.uint8), [np.round(poly * 16).astype(np.int32)], 1, lineType=cv2.LINE_8, shift=4)
    info.update(accepted=len(accepted), rejected=len(rejected),
                rejected_reasons=sorted(set(rejected.values())), bands=[by_k[k] for k in sorted(accepted)],
                status={b.k: ("seed" if b.k in seeds else "accepted" if b.k in accepted else rejected.get(b.k, "open"))
                        for b in bands}, all_bands=bands)
    return mask, info


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------

SOURCE_KIND = {"scan": "raster_scan", "photo": "raster_photo"}
DIM_ERASE_PX = 2.5                 # dimension strokes are erased within this ...
DIM_PROTECT_PX = 1.5               # ... except where another stroke passes within this
ASPECT_GROUP_AGREEMENT = 0.01      # photos: each dimension group (horizontal, vertical) agrees within 1 % ...
ASPECT_GROUP_MIN = 2               # ... with >= 2 dimensions
ASPECT_CORRECTION = 0.015          # the groups override the sheet-ratio snap when they differ by > 1.5 %
TEXT_PX = 21.0                     # working resolution: printed texts this tall (the 150 dpi fixtures: 15-21 px) ...
RESAMPLE_ABOVE = 1.25              # ... a page whose texts are > 1.25 x that tall is resampled down to it
PROBE_LONG_PX = 2600               # the text-height probe reads a copy whose long side is at most this
PROBE_CONF = 0.8                   # ... and measures the words read with this confidence


@dataclass
class RasterPage:
    """A raster page as the core reads it, plus what the pipeline and the debug image need."""
    page: GenericPage
    rect: RF.Rectified
    texts: list[dict] = field(default_factory=list)       # OCR items (rectified pixel-corner boxes, y down)
    review: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    info: dict = field(default_factory=dict)
    original: Optional[np.ndarray] = None                 # the original grey image (debug image)

    @property
    def image(self) -> np.ndarray:
        return self.rect.image


def read_grey(path: str | Path) -> Optional[np.ndarray]:
    """An image file as grey uint8 (None when OpenCV cannot read it). An alpha channel is composited onto white
    paper first: a plan exported with a transparent background has black (0) colour under alpha 0, which a plain
    grey read turns into an all-ink page. Images without alpha are read as before (``IMREAD_GRAYSCALE``, which
    also applies a JPEG's EXIF orientation)."""
    path = Path(path)
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None or path.suffix.lower() not in (".png", ".tif", ".tiff", ".webp"):
        return gray
    raw = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if raw is None or raw.ndim != 3 or raw.shape[2] not in (2, 4):
        return gray
    scale = 255.0 / float(np.iinfo(raw.dtype).max) if np.issubdtype(raw.dtype, np.integer) else 255.0
    arr = raw.astype(np.float64) * scale
    alpha = arr[..., -1:] / 255.0
    colour = arr[..., :1] if raw.shape[2] == 2 else arr[..., :3]
    flat = colour * alpha + 255.0 * (1.0 - alpha)                     # onto white paper
    flat = np.clip(np.round(flat), 0, 255).astype(np.uint8)
    return flat[..., 0] if raw.shape[2] == 2 else cv2.cvtColor(flat, cv2.COLOR_BGR2GRAY)


def load_image(path: str | Path, page_no: int = 1) -> tuple[np.ndarray, Optional[float], str]:
    """(grey image, verified dpi or None, how): image files as they are (dpi from PNG pHYs / TIFF resolution only;
    a transparent background composited onto white, ``read_grey``); PDF pages rendered at ``PDF_DPI`` with
    pdftoppm (a verified pixel size)."""
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from wenart.synthetic.raster import rasterise_pdf_page
        with tempfile.TemporaryDirectory() as tmp:
            png = rasterise_pdf_page(path, page_no, Path(tmp) / "page.png", dpi=PDF_DPI, gray=True)
            gray = cv2.imread(str(png), cv2.IMREAD_GRAYSCALE)
        return gray, float(PDF_DPI), f"PDF page rendered at {PDF_DPI} dpi"
    gray = read_grey(path)
    if gray is None:
        raise FileNotFoundError(f"{path}: not readable as an image")
    dpi = None
    how = "image file"
    if path.suffix.lower() in (".png", ".tif", ".tiff"):
        try:
            from PIL import Image
            with Image.open(path) as im:
                info_dpi = im.info.get("dpi")
            if info_dpi and info_dpi[0] and abs(float(info_dpi[0]) - float(info_dpi[1])) < 0.5 \
                    and float(info_dpi[0]) > 1.0:
                dpi = round(float(info_dpi[0]), 2)
                how = f"image file, {dpi:g} dpi from its metadata"
        except Exception:  # noqa: BLE001 - unreadable metadata only means no verified pixel size
            dpi = None
    return gray, dpi, how


def _to_original_box(rect: RF.Rectified, box) -> list[float]:
    """A rectified pixel-corner box -> the axis-aligned pixel-corner box of its corners in the original image."""
    x0, y0, x1, y1 = box
    pts = [RF.apply_h(rect.to_original, x - 0.5, y - 0.5) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [p[0] + 0.5 for p in pts]
    ys = [p[1] + 0.5 for p in pts]
    return [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]


def page_box_to_original(rect: RF.Rectified, box_page) -> list[float]:
    """A page-unit box (y up) -> original image pixel box."""
    h = rect.image.shape[0]
    x0, y0, x1, y1 = box_page
    return _to_original_box(rect, (x0, h - y1, x1, h - y0))


def _useful(item: dict) -> bool:
    text = str(item.get("text") or "").strip()
    alnum = sum(ch.isalnum() for ch in text)
    return alnum >= 2 or any(ch.isdigit() for ch in text)


def text_runs(items: list[dict], rect: RF.Rectified, file_rel: str, page_no: int) -> tuple[list[TextRun], list[str]]:
    """OCR items -> ``TextRun``s in page units (y up), ``source "ocr"``, evidence ``ocr`` with the OCR confidence,
    engine and the box in original image pixels. Length texts need conf >= ``DIM_TEXT_CONF``, others
    >= ``TEXT_CONF`` (§4.3); single stray characters are dropped. Returns (runs, notes)."""
    from wenart import building as B
    from wenart import units as U
    from wenart.recognition import room_labels as RL

    h = rect.image.shape[0]
    runs, notes = [], []
    for item in join_size_pairs(items):
        text = str(item.get("text") or "").strip()
        conf = float(item.get("confidence") or 0.0)
        if not text or not _useful(item):
            continue
        length = U.parse_length(text)
        if length is not None and U.parse_size_pair(text) is None:
            if conf < DIM_TEXT_CONF:
                notes.append(f"length text '{text}' read with confidence {conf:.2f} < {DIM_TEXT_CONF}: not used")
                continue
        elif conf < TEXT_CONF:
            continue
        x0, y0, x1, y1 = item["box"]
        rot = 90.0 if item.get("rotation") == 90 else 0.0
        height = (x1 - x0) if rot else (y1 - y0)
        engine = RL.TESSERACT_ENGINE if item.get("source") != "glyph_row" else \
            f"tesseract --oem {RL.TESSERACT_OEM} --psm {GLYPH_PSM} -l {RL.TESSERACT_LANG} (glyph row)"
        ev = B.evidence(file_rel, "ocr", round(min(max(conf, 0.0), 1.0), 4), page=page_no, model=engine,
                        pixel_box=_to_original_box(rect, item["box"]), text=text)
        runs.append(TextRun(id=f"ocr:{len(runs) + 1}", text=text, box=(float(x0), float(h - y1), float(x1),
                                                                         float(h - y0)),
                            height=float(height), rotation_deg=rot, source="ocr", evidence=[ev]))
    return runs, notes


def _erase_strokes(ink: np.ndarray, strokes: list[Stroke], erase_ids: set, height: int) -> np.ndarray:
    """Clear the pixels of the strokes in ``erase_ids`` (within ``DIM_ERASE_PX``) except where another stroke passes
    (within ``DIM_PROTECT_PX``)."""
    erase = np.zeros(ink.shape, np.uint8)
    protect = np.zeros(ink.shape, np.uint8)
    for st in strokes:
        pts = np.array([(x - 0.5, height - y - 0.5) for x, y in st.pts], dtype=np.float64)
        if len(pts) < 2:
            continue
        target = erase if st.id in erase_ids else protect
        width = int(round(2 * (DIM_ERASE_PX if st.id in erase_ids else DIM_PROTECT_PX))) + 1
        cv2.polylines(target, [np.round(pts * 16).astype(np.int32)], False, 1, thickness=width, lineType=cv2.LINE_8,
                      shift=4)
    return np.asarray(ink, bool) & ~((erase > 0) & (protect == 0))


def _page(file_rel: str, page_no: int, kind: str, rect: RF.Rectified, strokes: list[Stroke], texts: list[TextRun],
          dpi: Optional[float], mask: Optional[np.ndarray] = None) -> GenericPage:
    h, w = rect.image.shape
    return GenericPage(file=file_rel, page=page_no, source_kind=SOURCE_KIND[kind], units="px", units_to_m=None,
                       size=(float(w), float(h)), strokes=strokes, texts=texts,
                       wall_mask=MaskLayer(mask=mask, origin=(0.0, float(h)), px=1.0) if mask is not None else None,
                       to_original=RF.page_to_original(rect), dpi=dpi)


def _aspect_from_dimensions(dims) -> Optional[tuple[float, dict]]:
    """(factor for the rectified height, details) from the horizontal and vertical dimension groups (each >= 2
    within 1 %), or None."""
    groups: dict[str, list[float]] = {"h": [], "v": []}
    for d in dims:
        dx, dy = abs(d.p2[0] - d.p1[0]), abs(d.p2[1] - d.p1[1])
        if d.measured_units <= 0:
            continue
        groups["h" if dx >= dy else "v"].append(d.ratio)
    meds = {}
    for key, ratios in groups.items():
        if len(ratios) < ASPECT_GROUP_MIN:
            return None
        med = statistics_median(ratios)
        agree = [r for r in ratios if abs(r / med - 1.0) <= ASPECT_GROUP_AGREEMENT]
        if len(agree) < ASPECT_GROUP_MIN:
            return None
        meds[key] = statistics_median(agree)
    return meds["v"] / meds["h"], {"h_m_per_px": meds["h"], "v_m_per_px": meds["v"], "n_h": len(groups["h"]),
                                   "n_v": len(groups["v"])}


def text_height_probe(gray: np.ndarray) -> tuple[Optional[float], int]:
    """(median height in pixels of ``gray`` of the words Tesseract reads with conf >= ``PROBE_CONF`` and >= 3
    letters or digits, number of such words): one psm 11 pass at 0° on a copy whose long side is at most
    ``PROBE_LONG_PX``, lighting flattened. (None, 0) when no word is read."""
    g = np.asarray(gray, dtype=np.uint8)
    s = min(1.0, PROBE_LONG_PX / float(max(g.shape)))
    small = cv2.resize(g, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1.0 else g
    items = tesseract(RF.flatten_illumination(small), PAGE_PSM, 0)
    heights = [_text_height_px(i) / s for i in items
               if i["confidence"] >= PROBE_CONF and sum(ch.isalnum() for ch in str(i["text"])) >= 3]
    return (statistics_median(heights), len(heights)) if heights else (None, 0)


def working_resolution(gray: np.ndarray) -> tuple[np.ndarray, tuple[float, float], Optional[str]]:
    """The page at the working resolution the pixel constants of this module are tuned for (the 150 dpi fixtures,
    whose texts are 15-21 px tall): a page whose measured text height (``text_height_probe``) is more than
    ``RESAMPLE_ABOVE`` x ``TEXT_PX`` is resampled down (``INTER_AREA``) so its texts are ``TEXT_PX`` tall; others
    stay as they are (never enlarged). Returns (work image, (fx, fy) = work / original size, note or None).
    ``_in_original`` folds the factor into ``to_original``, so every box still points at the file as given."""
    height, words = text_height_probe(gray)
    if height is None or height <= RESAMPLE_ABOVE * TEXT_PX:
        return gray, (1.0, 1.0), None
    f = TEXT_PX / height
    h0, w0 = gray.shape[:2]
    w1, h1 = max(1, int(round(w0 * f))), max(1, int(round(h0 * f)))
    work = cv2.resize(gray, (w1, h1), interpolation=cv2.INTER_AREA)
    note = (f"working resolution: texts {height:.1f} px tall ({words} words read) > {RESAMPLE_ABOVE:g} x {TEXT_PX:g} "
            f"px; the page is read resampled to {w1} x {h1} px (x {f:.4f}), boxes map to the original")
    return work, (w1 / float(w0), h1 / float(h0)), note


def _in_original(rect: RF.Rectified, scale_xy: tuple[float, float], full_size: tuple[int, int]) -> RF.Rectified:
    """A rectification of the work image (``working_resolution``) -> the same rectified image whose
    ``to_original``, ``quad`` and ``original_size`` refer to the original image (pixel centres: a work pixel x is
    original (x + 0.5) / f - 0.5)."""
    fx, fy = scale_xy
    if fx == 1.0 and fy == 1.0:
        return rect
    back = np.linalg.inv(np.array([[fx, 0.0, 0.5 * fx - 0.5], [0.0, fy, 0.5 * fy - 0.5], [0.0, 0.0, 1.0]]))
    to_orig = back @ np.asarray(rect.to_original, dtype=np.float64)
    quad = [[round(v, 2) for v in RF.apply_h(back, x, y)] for x, y in rect.quad] if rect.quad else rect.quad
    return dataclasses.replace(rect, to_original=[[float(v) for v in row] for row in to_orig], quad=quad,
                               original_size=(int(full_size[0]), int(full_size[1])), notes=list(rect.notes))


def read_page(path: str | Path, page_no: int, file_rel: str, kind: str) -> RasterPage:
    """One raster page -> ``RasterPage`` (see the module docstring). ``kind`` is ``scan`` or ``photo``.

    The page is read at the working resolution (``working_resolution``: a 300 or 600 dpi scan is read like the
    150 dpi one); ``rect.to_original``, the OCR and debug images and every ``pixel_box`` refer to the original."""
    from wenart.ingest.generic import scale as SC

    original, dpi, how = load_image(path, page_no)
    gray, scale_xy, res_note = working_resolution(original)
    full_size = (int(original.shape[1]), int(original.shape[0]))
    if dpi and scale_xy != (1.0, 1.0):
        dpi = dpi * scale_xy[0]                     # pixels per inch of the page units (work pixels)
    rect = RF.rectify(gray, kind)
    notes = [how] + ([res_note] if res_note else []) + list(rect.notes)
    if rect.review:
        rect = _in_original(rect, scale_xy, full_size)
        rp = RasterPage(page=_page(file_rel, page_no, kind, rect, [], [], None), rect=rect, notes=notes,
                        review=[rect.review], original=original)
        return rp
    if kind == "photo":
        dpi = None                                  # a photo has no single pixel size
    for attempt in range(2):
        rp = _read_rectified(original, _in_original(rect, scale_xy, full_size), file_rel, page_no, kind, dpi, notes)
        if kind != "photo" or rect.aspect is None or attempt == 1:
            break
        solved = _aspect_from_dimensions(rp.info.get("dims") or [])
        if solved is None:
            if rect.aspect.get("snapped") is None:
                rp.review.append("photo aspect unknown (not within 4 % of a sheet ratio and the dimension groups do "
                                 "not give it)")
            break
        factor, detail = solved
        if rect.aspect.get("snapped") is not None and abs(factor - 1.0) <= ASPECT_CORRECTION:
            rp.notes.append(f"photo aspect: the dimension groups agree with the sheet ratio within "
                            f"{abs(factor - 1.0) * 100:.2f} %")
            rp.rect.aspect = dict(rp.rect.aspect, checked_by_dimensions=round(factor, 5))   # still the snapped one
            break
        notes = notes + [f"photo aspect from the dimension groups ({detail['n_h']} horizontal, {detail['n_v']} "
                         f"vertical): height x {factor:.4f}"
                         + (f" (overrides the assumed {rect.aspect.get('name')})" if rect.aspect.get("snapped")
                            else "")]
        rect = RF.rescale_y(rect, gray, factor)              # work image coordinates
        rect.aspect = dict(rect.aspect, snapped=None, assumed=False, solved_from="dimension groups",
                           factor=round(factor, 5))
    rp.original = original
    return rp


def _read_rectified(gray: np.ndarray, rect: RF.Rectified, file_rel: str, page_no: int, kind: str,
                    dpi: Optional[float], notes: list[str]) -> RasterPage:
    from wenart.ingest.generic import scale as SC

    img = rect.image
    h = img.shape[0]
    info: dict = {}
    ink = RF.ink_mask(img)
    # Door swings first (from the raw ink), so the OCR can paint them out like the straight line art.
    arcs0 = strokes_from_ink(ink, h).arcs_img
    items = ocr_page(gray, rect, arcs_img=arcs0)
    ink_t, blanked = blank_texts(ink, items, arcs_img=arcs0)
    info["ocr_items"] = len(items)
    info["text_boxes_blanked"] = blanked
    filled0, finfo = filled_candidates(ink_t)
    info["filled"] = finfo
    stroke_ink = ink_t & ~(cv2.dilate(filled0.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
    number_boxes = [it["box"] for it in items if _numeric(it["text"])]
    ss = strokes_from_ink(stroke_ink, h, number_boxes=number_boxes)
    runs, text_notes = text_runs(items, rect, file_rel, page_no)
    page = _page(file_rel, page_no, kind, rect, ss.strokes, runs, dpi)
    dims = SC.find_dimensions(page)
    sc, reasons = SC.provisional_scale(page, dims)
    info["dims"] = dims
    info["scale_reasons"] = reasons
    rp = RasterPage(page=page, rect=rect, texts=items, notes=list(notes) + text_notes, info=info)
    if sc is None:
        rp.notes.append("no scale: no wall mask computed")
        return rp
    px_per_m = 1.0 / float(sc["metres_per_unit"])
    info["px_per_m"] = round(px_per_m, 4)
    dim_ids = {i for d in dims for i in d.stroke_ids}
    ink_nd = _erase_strokes(ink_t, ss.strokes, dim_ids, h)
    filled, rings = drop_small_rings(filled0, px_per_m, ink_t)
    info["filled_rings_dropped"] = rings
    outline, oinfo = outline_walls(ink_nd & ~filled, px_per_m)
    info["outline"] = {k: v for k, v in oinfo.items() if k not in ("bands", "all_bands", "status")}
    info["wall_style"] = ("filled+outline" if filled.any() and outline.any() else "filled" if filled.any()
                          else "outline" if outline.any() else "none")
    mask = filled | outline
    # Inside the wall bands, parallel lines the threshold ran together (a window symbol beside the wall faces) are
    # split at their paper gap and the strokes traced again; elsewhere (furniture) the strokes stay as they are.
    split = split_valleys(stroke_ink, img)
    stroke_ink2 = np.where(mask, split, stroke_ink)
    info["valley_px"] = int((stroke_ink & ~stroke_ink2).sum())
    if info["valley_px"]:
        stroke_ink = stroke_ink2
        ss = strokes_from_ink(stroke_ink, h, number_boxes=number_boxes)
        dims = SC.find_dimensions(_page(file_rel, page_no, kind, rect, ss.strokes, runs, dpi))
        dim_ids = {i for d in dims for i in d.stroke_ids}
        info["dims"] = dims                      # the same dimensions, on the strokes the page keeps
    # Straight strokes run on through junctions where their ink does (door leaves into the wall band); the
    # dimension strokes keep their ends at their marks, so the core finds the same dimensions again.
    keep_ends = dim_ids | {i for d in dims for i in d.extension_ids}
    ss.strokes = snap_to_arcs(extend_line_strokes(ss.strokes, stroke_ink, keep_ends, ss.skeleton), keep_ends)
    # The MaskLayer grid: row r covers page y in [H - r - 1, H - r] (origin = top-left corner, y up).
    rp.page = _page(file_rel, page_no, kind, rect, ss.strokes, runs, dpi, mask=mask)
    rp.info["mask_px"] = int(mask.sum())
    return rp
