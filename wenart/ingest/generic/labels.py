"""Room-name labels of a plan page: vocabulary, label blocks and size-label checks (docs/milestone7.md §2.7.2-3).

A room label on a real plan is often more than one text run: ``Bath+`` / ``Toilet`` / ``7' x 5'`` are three
runs stacked under each other, and the last one is the room's printed size, not its name. This module
turns the text runs of one page into ``LabelBlock``s:

- **Name runs** are runs with a room-name keyword (``building._ROOM_TYPE_KEYWORDS``: Turkish word starts,
  English whole words) or an exterior keyword (``EXTERIOR_KEYWORDS``: parking, garden, ...). Long runs
  (more than ``MAX_NAME_WORDS`` words) are notes, not names. Runs that parse as one length are dimension
  texts and never join a block.
- **Stacking**: a run directly below another (same rotation, vertical gap ≤ ``STACK_GAP`` × line height,
  horizontal overlap ≥ ``STACK_OVERLAP`` of the narrower run) continues it; a run ending in ``+``, ``&``
  or ``-`` also takes the next run below or to its right a little further away (``CONNECTOR_GAP``). A block
  is its name lines followed by at most one size line (``11' x 10'``) and one area line (``110 sq ft``);
  a name line after them starts the next block. Runs without a keyword join a block only as part of a
  stack that has a keyword line or a size/area line (``GUEST`` / ``BED ROOM``, ``GYM`` / ``12' x 10'``);
  alone they are not labels (``UP``, ``N``, door tags).
- **Anchor** = centre of the name lines' box (the room the block names is the face containing it).

``check_label_size`` compares a block's printed size with the clear size of its face (minimum-area
rectangle, both orientations): ``ok`` within max(5 %, 0.15 m) per side, ``conflict`` beyond (the room is
``unverified`` beyond 10 %), ``unchecked`` for a face that is not a rectangle (area / rectangle < 0.9),
whose printed area w × l is then compared with the face area at 8 %.

Coordinates: whatever the runs carry; ``core`` passes runs in page metres (y up).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B
from wenart import units
from wenart.ingest.generic.model import TextRun

MAX_NAME_WORDS = 5            # a run with more words is a note, not a room name
STACK_GAP = 0.8               # stacked lines: vertical gap <= this x line height
STACK_OVERLAP = 0.30          # ... and horizontal overlap >= this x the narrower run
STACK_MIN_GAP = -0.5          # boxes may overlap a little (negative gap, x line height)
CONNECTOR_GAP = 1.5           # a run ending in + & - takes the next line within this x line height
CONNECTOR_SIDE_GAP = 1.0      # ... or the next run to its right within this x line height
CONNECTORS = ("+", "&", "-")
ROTATION_TOL_DEG = 1.0

# Site words (§2.7.2): a face or label named only by these is no room but a site area.
EXTERIOR_KEYWORDS = ("parking", "car porch", "porch", "garden", "lawn", "sit out", "setback", "otla", "court",
                     "courtyard", "drive", "driveway", "gate")
_EXTERIOR_PATTERNS = [B.english_keyword_re(k) for k in EXTERIOR_KEYWORDS]

# label_size check (§2.7.3)
SIZE_TOL_REL = 0.05
SIZE_TOL_ABS_M = 0.15
SIZE_UNVERIFIED_REL = 0.10
RECTANGULAR_MIN = 0.9
AREA_TOL_REL = 0.08
AREA_UNVERIFIED_REL = (1.0 + SIZE_UNVERIFIED_REL) ** 2 - 1.0   # the 10 % side rule in area terms (21 %)

_EVIDENCE_METHOD = {"vector": "vector", "ocr": "ocr", "ai": "ai"}


@dataclass
class LabelBlock:
    """One room (or site area) label: its name lines and the printed size/area under them."""
    name: str                                  # name lines joined as printed: "Bath+ Toilet"
    name_runs: list[TextRun]
    size_text: Optional[str]                   # "7' x 5'"
    area_text: Optional[str]                   # "35 sq ft", "24,50 m²"
    anchor: tuple[float, float]                # centre of the name lines' box
    room_type: str                             # building.room_type_for(name) ("other" for site areas)
    exterior: bool                             # named only by exterior keywords (Parking, Garden, ...)
    evidence: list[dict]                       # one evidence dict per run of the block
    size: Optional[tuple[units.Length, units.Length]] = None   # parsed size_text, printed order
    area_m2: Optional[float] = None            # parsed area_text in m²
    box: Optional[tuple[float, float, float, float]] = None    # all runs of the block
    runs: list[TextRun] = field(default_factory=list)          # name, size and area runs, top to bottom


# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

def _exterior_hit(name: str) -> bool:
    folded = B.fold_ascii(name)
    return any(p.search(folded) for p in _EXTERIOR_PATTERNS)


def room_type_for(name: str, face_area_m2: Optional[float] = None,
                  face_aspect: Optional[float] = None) -> tuple[str, bool]:
    """``(room_type, exterior)`` of a label name (English and Turkish).

    ``exterior`` is True when the name has an exterior keyword and no room keyword (``Parking``,
    ``Car Porch``); its room type is then ``other`` and the caller puts it into ``site.areas``.
    ``Terrace Garden`` is a balcony (a room keyword wins). The face size decides ``hall`` alone
    (``building.room_type_for``).
    """
    turkish, english = B.room_keyword_hits(name)
    if not turkish and not english and _exterior_hit(name):
        return "other", True
    return B.room_type_for(name, face_area_m2, face_aspect), False


def _strip_suffixes(text: str) -> tuple[str, Optional[str], Optional[str]]:
    """(name, size, area) of one line: ``SALON 24,50 m²`` -> (``SALON``, None, ``24,50 m²``);
    ``BED ROOM 11'x10'`` -> (``BED ROOM``, ``11'x10'``, None)."""
    head, size_text, area_text = text.strip(), None, None
    split = units.area_suffix(head)
    if split is not None and split[0]:
        head, area_text = split[0], split[3]
    words = head.split(" ")
    for k in range(1, len(words)):
        tail = " ".join(words[k:])
        if units.parse_size_pair(tail) is not None and re.search(r"[^\W\d_]", " ".join(words[:k])):
            head, size_text = " ".join(words[:k]).strip(), tail.strip()
            break
    return head, size_text, area_text


def _is_name_text(text: str, indoor_only: bool) -> bool:
    head, _, _ = _strip_suffixes(text)
    if not head or len(head.split()) > MAX_NAME_WORDS:
        return False
    if units.parse_length(head) is not None or units.parse_size_pair(head) is not None:
        return False
    turkish, english = B.room_keyword_hits(head)
    if turkish or english:
        return True
    return not indoor_only and _exterior_hit(head)


def room_name_runs(texts: list[TextRun]) -> list[TextRun]:
    """The runs that name a room (English or Turkish keyword, at most ``MAX_NAME_WORDS`` words; an area or
    size on the same line is allowed). Exterior names (Parking, Garden) are not counted: a page needs
    room names to be a floor plan (§2.1)."""
    return [t for t in texts if t.text and _is_name_text(t.text, indoor_only=True)]


def page_is_turkish(texts: list[TextRun]) -> bool:
    """Whether a page is labelled in Turkish: most of its room-name runs are Turkish
    (``building.is_turkish_label``); without room names, any Turkish letter on the page. Decides the
    casing of its labels (``normalise_room_label(..., turkish=...)``) and the unlabelled placeholder (§1.3)."""
    runs = room_name_runs(texts)
    if runs:
        turkish = sum(1 for r in runs if B.is_turkish_label(_strip_suffixes(r.text)[0]))
        return turkish * 2 > len(runs)
    return any(B.has_turkish_letters(t.text or "") for t in texts)


# --------------------------------------------------------------------------
# Label blocks
# --------------------------------------------------------------------------

@dataclass
class _Line:
    run: TextRun
    kind: str                 # name | other | size | area | skip (see _classify)
    head: str                 # name part (name/other lines) without an inline size or area
    size_text: Optional[str] = None
    area_text: Optional[str] = None
    frame_box: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)   # box in the text's own frame


def _frame_box(run: TextRun) -> tuple[float, float, float, float]:
    """The run's box rotated into its own reading frame (baseline along +x)."""
    a = math.radians(-run.rotation_deg)
    c, s = math.cos(a), math.sin(a)
    x0, y0, x1, y1 = run.box
    pts = [(x * c - y * s, x * s + y * c) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _line_height(run: TextRun) -> float:
    if run.height and run.height > 0:
        return run.height
    fb = _frame_box(run)
    return max(fb[3] - fb[1], 1e-9)


def _classify(run: TextRun, default_system: str) -> _Line:
    """Kind of one run: ``area``, ``size``, ``name`` (keyword), ``other`` (words that may continue a
    name), or ``skip`` (a single length, a bare number, a long note: never part of a block)."""
    text = run.text.strip()
    box = _frame_box(run)
    if units.parse_area(text) is not None:
        return _Line(run, "area", "", area_text=text, frame_box=box)
    if units.parse_size_pair(text, default_system) is not None:
        return _Line(run, "size", "", size_text=text, frame_box=box)
    if units.parse_length(text, default_system) is not None:
        return _Line(run, "skip", "", frame_box=box)
    head, size_text, area_text = _strip_suffixes(text)
    if _is_name_text(text, indoor_only=False):
        kind = "name"
    elif re.search(r"[^\W\d_]{2,}", head) and len(head.split()) <= MAX_NAME_WORDS:
        kind = "other"                                # a word of 2+ letters (door tags like "D1" are skipped)
    else:
        kind = "skip"
    return _Line(run, kind, head, size_text=size_text, area_text=area_text, frame_box=box)


def _same_rotation(a: TextRun, b: TextRun) -> bool:
    diff = abs((a.rotation_deg - b.rotation_deg + 180.0) % 360.0 - 180.0)
    return diff <= ROTATION_TOL_DEG


def _below(upper: _Line, lower: _Line, max_gap: float, min_overlap: float) -> Optional[float]:
    """Gap (in line heights) when ``lower`` sits under ``upper`` in their reading frame, else None."""
    if not _same_rotation(upper.run, lower.run):
        return None
    ub, lb = upper.frame_box, lower.frame_box
    h = max(_line_height(upper.run), _line_height(lower.run))
    gap = (ub[1] - lb[3]) / h
    if gap < STACK_MIN_GAP or gap > max_gap:
        return None
    if (lb[1] + lb[3]) / 2.0 >= (ub[1] + ub[3]) / 2.0:
        return None                                   # not below
    overlap = min(ub[2], lb[2]) - max(ub[0], lb[0])
    narrower = max(min(ub[2] - ub[0], lb[2] - lb[0]), 1e-9)
    if overlap / narrower < min_overlap:
        return None
    return gap


def _right_of(left: _Line, right: _Line) -> Optional[float]:
    """Gap (in line heights) when ``right`` continues ``left`` on the same baseline, else None."""
    if not _same_rotation(left.run, right.run):
        return None
    lb, rb = left.frame_box, right.frame_box
    h = max(_line_height(left.run), _line_height(right.run))
    if abs((lb[1] + lb[3]) / 2.0 - (rb[1] + rb[3]) / 2.0) > 0.5 * h:
        return None
    gap = (rb[0] - lb[2]) / h
    if gap < -0.2 or gap > CONNECTOR_SIDE_GAP:
        return None
    return gap


def _ends_with_connector(line: _Line) -> bool:
    return line.kind in ("name", "other") and line.run.text.rstrip().endswith(CONNECTORS)


def _join_names(lines: list[_Line]) -> str:
    out = ""
    for line in lines:
        text = re.sub(r"\s+", " ", line.head.strip())
        if not out:
            out = text
        elif out.endswith("-") and not out.endswith(" -"):
            out += text                               # "BED-" + "ROOM" -> "BED-ROOM"
        else:
            out += " " + text
    return out


def _evidence(run: TextRun, file_rel: Optional[str], page: Optional[int]) -> list[dict]:
    if run.evidence:
        return [dict(e) for e in run.evidence]
    if file_rel is None:
        return []
    method = _EVIDENCE_METHOD.get(run.source, "vector")
    # A vector text is what the file says; an OCR/AI run without its own evidence gets a low confidence.
    confidence = 1.0 if method == "vector" else 0.5
    return [B.evidence(file_rel, method, confidence, page=page, entity=run.id, text=run.text)]


def _union_box(runs: list[TextRun]) -> tuple[float, float, float, float]:
    return (min(r.box[0] for r in runs), min(r.box[1] for r in runs),
            max(r.box[2] for r in runs), max(r.box[3] for r in runs))


def page_unit_system(texts: list[TextRun]) -> str:
    """§1.1: the majority of the page's explicit lengths (single lengths first, then size and area labels)."""
    singles = [t.text for t in texts if units.parse_length(t.text) is not None]
    sizes = [t.text for t in texts if units.parse_length(t.text) is None]
    return units.majority_system(singles, sizes)


def merge_label_blocks(texts_m: list[TextRun], file_rel: Optional[str] = None,
                       page: Optional[int] = None) -> list[LabelBlock]:
    """Text runs of one page -> room/site label blocks (§2.7.2), in reading order (top to bottom, left to right).

    ``file_rel``/``page`` build the evidence of runs that carry none (vector runs: confidence 1.0).
    """
    system = page_unit_system(texts_m)
    lines = [_classify(t, system) for t in texts_m if t.text and t.text.strip()]
    candidates = [ln for ln in lines if ln.kind != "skip"]

    # Each line links to the line that continues it (the nearest one below; for a connector run also a
    # little further below or to the right). A line has at most one predecessor: the nearest wins.
    succ: dict[int, tuple[float, int]] = {}
    for i, upper in enumerate(candidates):
        if upper.kind == "area":
            continue                                  # an area line ends its block
        best: Optional[tuple[float, int]] = None
        for j, lower in enumerate(candidates):
            if i == j:
                continue
            gap = _below(upper, lower, STACK_GAP, STACK_OVERLAP)
            if gap is None and _ends_with_connector(upper) and lower.kind in ("name", "other"):
                gap = _below(upper, lower, CONNECTOR_GAP, 1e-9)
                if gap is None:
                    # The continuation to the right ranks after every line below (+10 line heights).
                    side = _right_of(upper, lower)
                    gap = None if side is None else side + 10.0
            if gap is not None and (best is None or gap < best[0]):
                best = (gap, j)
        if best is not None:
            succ[i] = best
    pred: dict[int, tuple[float, int]] = {}
    for i, (gap, j) in succ.items():
        if j not in pred or gap < pred[j][0]:
            pred[j] = (gap, i)
    next_of = {i: j for j, (_, i) in pred.items()}

    blocks: list[LabelBlock] = []
    heads = [i for i in range(len(candidates)) if i not in pred]
    seen: set[int] = set()
    for head in heads:
        chain = []
        k: Optional[int] = head
        while k is not None and k not in seen:
            seen.add(k)
            chain.append(candidates[k])
            k = next_of.get(k)
        blocks.extend(_blocks_from_chain(chain, file_rel, page, system))
    blocks.sort(key=lambda b: (-b.anchor[1], b.anchor[0]))
    return blocks


def _blocks_from_chain(chain: list[_Line], file_rel: Optional[str], page: Optional[int],
                       system: str) -> list[LabelBlock]:
    out: list[LabelBlock] = []
    names: list[_Line] = []
    size_line: Optional[_Line] = None
    area_line: Optional[_Line] = None
    inline_size: Optional[str] = None
    inline_area: Optional[str] = None

    def close() -> None:
        nonlocal names, size_line, area_line, inline_size, inline_area
        size_text = size_line.size_text if size_line else inline_size
        area_text = area_line.area_text if area_line else inline_area
        # "BED-" + "ROOM": the keyword may only appear once the lines are joined.
        has_keyword = any(ln.kind == "name" for ln in names) or bool(names) and _is_name_text(_join_names(names),
                                                                                             indoor_only=False)
        if names and (has_keyword or size_text or area_text):
            out.append(_make_block(names, size_line, area_line, size_text, area_text, file_rel, page, system))
        names, size_line, area_line, inline_size, inline_area = [], None, None, None, None

    for line in chain:
        if line.kind in ("name", "other"):
            if size_line or area_line or inline_size or inline_area:
                close()
            names.append(line)
            inline_size = inline_size or line.size_text
            inline_area = inline_area or line.area_text
        elif line.kind == "size":
            if not names or size_line or inline_size or area_line:
                close()
                continue                              # a size line with no name above is no label
            size_line = line
        elif line.kind == "area":
            if not names or area_line or inline_area:
                close()
                continue
            area_line = line
    close()
    return out


def _make_block(names: list[_Line], size_line: Optional[_Line], area_line: Optional[_Line],
                size_text: Optional[str], area_text: Optional[str], file_rel: Optional[str],
                page: Optional[int], system: str) -> LabelBlock:
    name = _join_names(names)
    name_runs = [ln.run for ln in names]
    runs = name_runs + [ln.run for ln in (size_line, area_line) if ln is not None]
    nb = _union_box(name_runs)
    room_type, exterior = room_type_for(name)
    size = units.parse_size_pair(size_text, system) if size_text else None
    area = units.parse_area(area_text) if area_text else None
    evidence = [e for r in runs for e in _evidence(r, file_rel, page)]
    return LabelBlock(name=name, name_runs=name_runs, size_text=size_text, area_text=area_text,
                      anchor=((nb[0] + nb[2]) / 2.0, (nb[1] + nb[3]) / 2.0), room_type=room_type,
                      exterior=exterior, evidence=evidence, size=size, area_m2=area[0] if area else None,
                      box=_union_box(runs), runs=runs)


# --------------------------------------------------------------------------
# Size labels against faces (§2.7.3)
# --------------------------------------------------------------------------

def clear_size(face_polygon) -> tuple[float, float, float]:
    """(side a, side b, rectangularity) of a face: the minimum-area rectangle's sides and face area /
    rectangle area (1.0 for a rectangle)."""
    rect = face_polygon.minimum_rotated_rectangle
    coords = list(rect.exterior.coords)
    a = math.dist(coords[0], coords[1])
    b = math.dist(coords[1], coords[2])
    rect_area = rect.area
    return a, b, (face_polygon.area / rect_area if rect_area > 0 else 0.0)


def match_sides(label: tuple[float, float], sides: tuple[float, float]) -> tuple[list[float], list[float]]:
    """The measured sides in the label's order (the orientation with the smaller worst relative error)
    and the relative errors (label - measured) / measured."""
    w, l = label
    a, b = sides
    best = None
    for mw, ml in ((a, b), (b, a)):
        errs = [(w - mw) / mw if mw > 0 else math.inf, (l - ml) / ml if ml > 0 else math.inf]
        worst = max(abs(e) for e in errs)
        if best is None or worst < best[0]:
            best = (worst, [mw, ml], errs)
    return best[1], best[2]


def check_label_size(block: LabelBlock, face_polygon) -> Optional[dict]:
    """``rooms[].label_size`` for a block with a printed size and the face it names (any consistent metric
    frame, e.g. page or building metres): ``{"text", "width_m", "length_m", "measured": [w, l], "status"}``
    plus ``off_pct`` (per side, or the area for an unchecked face) and ``unverified`` (the room loses its
    ``verified`` status: a side off by more than 10 %, or the area by more than 21 % on a non-rectangular
    face). None when the block has no parsable size."""
    if block.size is None:
        return None
    w, l = block.size[0].metres, block.size[1].metres
    a, b, rectangularity = clear_size(face_polygon)
    measured, errs = match_sides((w, l), (a, b))
    result = {"text": block.size_text, "width_m": round(w, 4), "length_m": round(l, 4),
              "measured": [round(measured[0], 3), round(measured[1], 3)]}
    if rectangularity >= RECTANGULAR_MIN:
        ok = all(abs(lab - mea) <= max(SIZE_TOL_REL * mea, SIZE_TOL_ABS_M)
                 for lab, mea in zip((w, l), measured))
        result["status"] = "ok" if ok else "conflict"
        result["off_pct"] = [round(100.0 * e, 1) + 0.0 for e in errs]   # + 0.0: no "-0.0"
        result["unverified"] = (not ok) and max(abs(e) for e in errs) > SIZE_UNVERIFIED_REL
        return result
    face_area = face_polygon.area
    area_err = (w * l - face_area) / face_area if face_area > 0 else math.inf
    result["status"] = "unchecked" if abs(area_err) <= AREA_TOL_REL else "conflict"
    result["off_pct"] = [round(100.0 * area_err, 1) + 0.0]
    result["area_m2"] = {"label": round(w * l, 3), "face": round(face_area, 3)}
    result["unverified"] = abs(area_err) > AREA_UNVERIFIED_REL
    return result
