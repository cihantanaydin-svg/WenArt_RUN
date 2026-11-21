"""RC15's vector text (21 Nov 2026, Milestone 14 queue item 3): the drawing's exact vector data and the reading, as
short text next to each image of the AI checks.

What: for the image (or crop) a question is about, a compact list of what the drawing file holds there and what the
reading built there, in metres in the image's own frame (origin at the image's top-left corner, x to the right, y
down; so a point is at ``1000 x / W, 1000 y / H`` in the 0-1000 scale the answers use):

- the drawing (upper-case ids): wall-layer line pairs as walls with their thickness (``W``; a lone wall-layer line
  ``L``), arcs with radius and sweep (``A``; a door swing at about 90 degrees), window symbols from the window, glass
  and sill layers (``G``), stair line groups (``S``), the room labels with the area written under them (``T``), loose
  area texts (``M``), opening size tags such as ``150/130`` (``Z``), dimensions with their value (``D``), level marks
  (``K``), other texts (``X``);
- the reading (lower-case ids): rooms with label, type, area and size (``r``), balconies and terraces (``b``), doors
  (``d``), windows (``n``), plain openings (``o``) with width and the two spaces they join, walls with thickness
  (``w``; exterior, inferred), stairs (``s``), lifts (``l``).

The same ids are drawn on the images as small blue tags (``tag_image``) when the switch says so, so the model can point
at an item; the text names the item by its id, the overlay at its place.

Why: the critic found 71 of 75 known errors in round 2 from rendered crops alone; it guesses numbers and labels from
pixels (a thin double line, a small area text, a 150/130 tag). The drawing file holds them exactly.

How: ``level_vector`` (CPU, at ``critic prepare`` or ``critic vector`` for an input set already made) writes
``<folder>/<level>_vector.json`` beside the images: every item in the level image's frame. On the pod, ``block`` picks
the items a question is about (near the compare marks, inside a close-up, around a finding) and writes them as lines,
the most relevant first, up to a token cap (``cap_for``: ``CAP_TOKENS``, and never more than the context left after the
images, the prompt and the answer; tokens counted by ``estimate_tokens``, a rule fitted on the agent model's own
token counts of round 2's text-only calls). ``CRITIC_VECTOR_TEXT`` switches it: ``0`` (default, until measured) the
prompts as before, ``1`` the text and the id tags, ``text`` the text only.
"""
from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Optional

ENV = "CRITIC_VECTOR_TEXT"
MODES = ("0", "1", "text")
CAP_TOKENS = 2400              # the text block of one question at most (the measured prompts: 1.7k-5.8k tokens)
CONTEXT_TOKENS = 16384         # scripts/jobs/critic.sh: --max-model-len 16384
MARGIN_TOKENS = 512            # the chat template and the labels of the images
FOCUS_M = 2.5                  # a compare mark's items: this near it
EDGE_M = 0.5                   # a window or arc this near a room's outline belongs to it (the plausibility block)
PAIR_GAP_M = (0.05, 0.60)      # two parallel wall-layer lines this far apart are the two faces of one wall
PAIR_OVERLAP_M = 0.3
PARALLEL_SIN = 0.02            # about one degree
SEGMENT_MIN_M = 0.3
LONE_MIN_M = 0.8               # a lone wall-layer line this long is listed
ARC_R_M = (0.3, 2.0)           # arcs of this radius are listed (smaller: hinges, fixtures; larger: curved walls)
DOOR_R_M = (0.5, 1.4)
DOOR_SWEEP = (60.0, 120.0)
CLUSTER_M = 0.08               # window strokes this close are one symbol
STAIR_CLUSTER_M = 0.35
WINDOW_W_M = (0.3, 8.0)
TAG_MAX = 60                   # id tags drawn on one image at most
RESERVE_TOKENS = 24            # kept under the cap for the last line (how many items were left out)
SIZE_TAG_RE = re.compile(r"^\s*\d{2,3}\s*/\s*\d{2,3}\s*$")
NUMBER_RE = re.compile(r"^\s*[+-]?\d{1,5}(?:[.,]\d{1,3})?\s*$")
AREA_RE = re.compile(r"(\d{1,4}[.,]\d{1,2})\s*(?:M2|M²|M\^2)\b", re.IGNORECASE)
NOT_ARC_ROLES = ("furniture", "sanitary", "finish", "dimension", "text", "hatch", "axis", "site", "section")
WINDOW_ROLES = ("window", "glass", "sill")
# the order in which the items of a list are kept under the cap (lower first) and the line kinds' names
PRIORITY = {"T": 0, "A": 1, "G": 1, "Z": 2, "M": 2, "K": 2, "S": 3, "W": 3, "r": 1, "b": 1, "d": 2, "n": 2, "o": 2,
            "s": 3, "l": 3, "w": 4, "D": 5, "X": 6, "L": 7}
HEADER = ("Exact data read from the drawing file (upper-case ids) and from the computer's model (lower-case ids), in "
          "metres in the frame of {what}: (0, 0) top-left, x to the right, y down; it is {w:.2f} m wide and {h:.2f} m "
          "high, so (x, y) is ({kx:.1f} x, {ky:.1f} y) in the 0-1000 scale. A drawing wall is two parallel wall lines, "
          "its thickness their gap{tags}. Only what is near the places asked about is listed, up to a size limit: "
          "something not listed may still be drawn. Trust the numbers and labels; judge the shapes from the images.")


# ======================================================================================================== switches
def mode(env: Optional[dict] = None) -> str:
    """``CRITIC_VECTOR_TEXT``: ``0`` (the prompts as before), ``1`` (text and id tags), ``text`` (text only)."""
    v = str((env if env is not None else os.environ).get(ENV, "0")).strip().lower()
    return v if v in MODES else "0"


def estimate_tokens(text: str) -> int:
    """The agent model's tokens of ``text``, over-counted rather than under (no tokenizer on the CPU): digits and
    punctuation one token each, a word 1.25, a non-ASCII letter one more, 30 for the turn. Fitted on the 56 text-only
    calls of round 2 (pod x4vgfcm85u18op, the server's own counts): never under, mean error 10 %; chars / 3.5
    under-counted all 56, by 25 % on the mean (the texts are dense in digits and ids)."""
    s = str(text or "")
    digits = sum(ch.isdigit() for ch in s)
    words = len(re.findall(r"[A-Za-z]+", s))
    punct = len(re.findall(r"[^\sA-Za-z\d]", s))
    nonascii = sum(1 for ch in s if ord(ch) > 127)
    return int(math.ceil(digits + punct + 1.25 * words + nonascii + 30))


def image_tokens(size) -> int:
    """The tokens of one image of ``size`` (w, h px) as the agent model counts it: about one per 32 x 32 px (round 2:
    0.94 of that on 128 images; rounded up here)."""
    w, h = float(size[0]), float(size[1])
    return int(math.ceil(w / 32.0) * math.ceil(h / 32.0))


def cap_for(prompt_tokens: int, answer_tokens: int, images: list = (), cap: int = CAP_TOKENS,
            context: int = CONTEXT_TOKENS) -> int:
    """The token budget of a question's text block (pure): ``cap``, and never more than the context less the images,
    the rest of the prompt, the answer and ``MARGIN_TOKENS``; 0 when nothing is left."""
    left = context - sum(image_tokens(s) for s in images) - int(prompt_tokens) - int(answer_tokens) - MARGIN_TOKENS
    return max(0, min(int(cap), left))


# ========================================================================================================= frame
class Frame:
    """The frame of a level image: ``box`` (drawing units, the image's extent) and the page transform ``tf``
    (drawing units -> building metres). Points in the frame are metres from the image's top-left corner, x to the
    right, y down: a rotated plan reads as drawn, a mirrored transform (negative determinant) maps the building's
    elements back onto the drawing's own lines."""

    def __init__(self, box, tf):
        self.box = [float(v) for v in box]
        self.tf = [float(v) for v in tf]
        a, b, _c, d, e, _f = self.tf
        self.det = a * e - b * d
        if abs(self.det) < 1e-18:
            raise ValueError("a page transform without area")
        self.s = math.sqrt(abs(self.det))                       # metres per drawing unit
        self.w = (self.box[2] - self.box[0]) * self.s
        self.h = (self.box[3] - self.box[1]) * self.s

    def from_page(self, p) -> tuple:
        return ((float(p[0]) - self.box[0]) * self.s, (self.box[3] - float(p[1])) * self.s)

    def from_building(self, p) -> tuple:
        a, b, c, d, e, f = self.tf
        x, y = float(p[0]) - c, float(p[1]) - f
        return self.from_page(((e * x - b * y) / self.det, (-d * x + a * y) / self.det))

    def to_building(self, q) -> tuple:
        px, py = self.box[0] + float(q[0]) / self.s, self.box[3] - float(q[1]) / self.s
        a, b, c, d, e, f = self.tf
        return (a * px + b * py + c, d * px + e * py + f)

    def norm(self, q) -> tuple:
        return (float(q[0]) / self.w, float(q[1]) / self.h)

    def to_dict(self) -> dict:
        return {"box": self.box, "tf": self.tf, "m_per_unit": round(self.s, 9), "w": round(self.w, 3),
                "h": round(self.h, 3)}


def _r2(p) -> list:
    return [round(float(p[0]), 2), round(float(p[1]), 2)]


def _deg(a, b) -> float:
    """The direction of ``a`` -> ``b`` in the frame (y down), degrees mod 180, 0 along the image's x axis, counted
    counter-clockwise as the image is seen."""
    return math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0])) % 180.0


def _off_axis(deg: float) -> float:
    d = deg % 90.0
    return min(d, 90.0 - d)


# =================================================================================================== the drawing
def _roles(st) -> set:
    from wenart.ingest.generic import layer_names as LN

    out = set(LN.layer_roles(getattr(st, "layer", None)) or ())
    for part in str(getattr(st, "block", None) or "").split("/"):
        out |= set(LN.layer_roles(part) or ())
    return out


def _segments(st, frame: Frame, min_len: float = SEGMENT_MIN_M) -> list:
    pts = [frame.from_page(p) for p in st.pts] + ([frame.from_page(st.pts[0])] if getattr(st, "closed", False) else [])
    return [(a, b) for a, b in zip(pts, pts[1:]) if math.dist(a, b) >= min_len]


def wall_pairs(segs: list) -> tuple:
    """``(pairs, lone)`` (pure): each pair of parallel wall-layer segments ``PAIR_GAP_M`` apart and overlapping by
    ``PAIR_OVERLAP_M`` as one wall ``{a, b, t}`` (its centre line over the overlap, ``t`` the gap); a segment takes its
    nearest partner on each side only, so a hatch outline's far edge is no second face; the segments in no pair."""
    from shapely.geometry import LineString
    from shapely.strtree import STRtree

    if not segs:
        return [], []
    lines = [LineString(s) for s in segs]
    tree = STRtree(lines)
    best: dict = {}
    for i, (a, b) in enumerate(segs):
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        for j in tree.query(lines[i].buffer(PAIR_GAP_M[1])):
            j = int(j)
            if j <= i:
                continue
            c, d = segs[j]
            L2 = math.dist(c, d)
            vx, vy = (d[0] - c[0]) / L2, (d[1] - c[1]) / L2
            if abs(ux * vy - uy * vx) > PARALLEL_SIN:
                continue
            side = (c[0] - a[0]) * uy - (c[1] - a[1]) * ux
            gap = abs(side)
            if not (PAIR_GAP_M[0] <= gap <= PAIR_GAP_M[1]):
                continue
            s0, s1 = sorted(((c[0] - a[0]) * ux + (c[1] - a[1]) * uy, (d[0] - a[0]) * ux + (d[1] - a[1]) * uy))
            lo, hi = max(0.0, s0), min(L, s1)
            if hi - lo < PAIR_OVERLAP_M:
                continue
            for k, sgn in ((i, 1 if side > 0 else -1), (j, -1 if side > 0 else 1)):
                cur = best.get((k, sgn))
                if cur is None or gap < cur[0]:
                    best[(k, sgn)] = (gap, i, j, lo, hi)
    # a pair stands when both faces name each other (each one's nearest partner on that side)
    named: dict = {}
    for v in best.values():
        named[(v[1], v[2])] = named.get((v[1], v[2]), 0) + 1
    pairs, used, seen = [], set(), set()
    for _key, (gap, i, j, lo, hi) in sorted(best.items(), key=lambda kv: kv[1][0]):
        if (i, j) in seen or named.get((i, j), 0) < 2:
            continue
        seen.add((i, j))
        used |= {i, j}
        a, b = segs[i]
        c, d = segs[j]
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = -uy, ux
        off = ((c[0] - a[0]) * nx + (c[1] - a[1]) * ny) / 2.0
        p0 = (a[0] + ux * lo + nx * off, a[1] + uy * lo + ny * off)
        p1 = (a[0] + ux * hi + nx * off, a[1] + uy * hi + ny * off)
        pairs.append({"a": p0, "b": p1, "t": gap})
    # a lone line just beside a paired face (a plaster line, a hatch edge on the face) is that wall, not a line
    lone = []
    for k, (a, b) in enumerate(segs):
        if k in used:
            continue
        L = math.dist(a, b)
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        beside = False
        for j in tree.query(lines[k].buffer(PAIR_GAP_M[0] + 0.01)):
            j = int(j)
            if j == k or j not in used:
                continue
            c, d = segs[j]
            L2 = math.dist(c, d)
            if abs(ux * (d[1] - c[1]) / L2 - uy * (d[0] - c[0]) / L2) <= PARALLEL_SIN:
                beside = True
                break
        if not beside:
            lone.append((a, b))
    return pairs, lone


def _clusters(boxes: list, reach: float) -> list:
    """Groups of the indices of ``boxes`` (x0, y0, x1, y1) that touch within ``reach`` (union-find, pure)."""
    parent = list(range(len(boxes)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    order = sorted(range(len(boxes)), key=lambda i: boxes[i][0])
    for n, i in enumerate(order):
        bi = boxes[i]
        for j in order[n + 1:]:
            bj = boxes[j]
            if bj[0] > bi[2] + reach:
                break
            if bj[1] <= bi[3] + reach and bi[1] <= bj[3] + reach:
                parent[find(i)] = find(j)
    groups: dict = {}
    for i in range(len(boxes)):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _symbol(segs: list) -> Optional[dict]:
    """The extent of a group of segments along its longest segment's direction: centre, width (along), depth."""
    if not segs:
        return None
    a, b = max(segs, key=lambda s: math.dist(*s))
    L = math.dist(a, b)
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    pts = [p for s in segs for p in s]
    us = [(p[0] - a[0]) * ux + (p[1] - a[1]) * uy for p in pts]
    vs = [-(p[0] - a[0]) * uy + (p[1] - a[1]) * ux for p in pts]
    u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
    cu, cv = (u0 + u1) / 2.0, (v0 + v1) / 2.0
    c = (a[0] + ux * cu - uy * cv, a[1] + uy * cu + ux * cv)
    return {"p": c, "w": u1 - u0, "depth": v1 - v0, "deg": _deg(a, b)}


def source_items(page, frame: Frame, wall_layers=()) -> list:
    """The drawing's items of a generic page (``wenart.ingest.generic.model.GenericPage``: a DXF or a vector PDF read
    by the reader's own adapters) in ``frame`` (the module docstring), each ``{id, k, ...}`` with its points in frame
    metres; ``wall_layers`` (upper case): the layers the reading took its walls from, read as wall layers too (real02's
    face-line layer has no wall word)."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.generic.model import TextRun
    from wenart.levels import marks as MK

    layers = {str(x).upper() for x in wall_layers or ()}
    try:
        axis = AX.axis_line_ids(page.strokes, page.texts)
    except Exception:  # noqa: BLE001 - no axis reading: no line left out
        axis = set()
    wall_segs, win_segs, stair_segs, arcs = [], [], [], []
    for st in page.strokes:
        roles = _roles(st)
        arc = getattr(st, "arc", None)
        if arc:
            if roles & set(NOT_ARC_ROLES) or "stair" in roles:
                continue
            r = float(arc.get("radius") or 0.0) * frame.s
            if not (ARC_R_M[0] <= r <= ARC_R_M[1]):
                continue
            sweep = (float(arc.get("end_deg") or 0.0) - float(arc.get("start_deg") or 0.0)) % 360.0 or 360.0
            arcs.append({"p": frame.from_page(arc["center"]), "r": r, "sweep": sweep,
                         "layer": str(getattr(st, "layer", "") or "")[:16]})
            continue
        if st.id in axis:
            continue
        layer = str(getattr(st, "layer", None) or "").upper()
        if roles & {"wall", "plaster", "structure"} or layer in layers:
            wall_segs += [(s, layer) for s in _segments(st, frame)]
        elif roles & set(WINDOW_ROLES):
            win_segs += [(s, layer) for s in _segments(st, frame, 0.02)]   # a window's jambs are short
        elif "stair" in roles:
            stair_segs += _segments(st, frame)
    out: list = []
    pairs, lone = wall_pairs([s for s, _l in wall_segs])
    for k, w in enumerate(sorted(pairs, key=lambda w: (round(w["a"][1], 1), round(w["a"][0], 1)))):
        out.append({"id": f"W{k + 1}", "k": "W", "a": _r2(w["a"]), "b": _r2(w["b"]), "t": round(w["t"], 2),
                    "deg": round(_deg(w["a"], w["b"]), 1)})
    lone = [s for s in lone if math.dist(*s) >= LONE_MIN_M]
    for k, (a, b) in enumerate(sorted(lone, key=lambda s: (round(s[0][1], 1), round(s[0][0], 1)))):
        out.append({"id": f"L{k + 1}", "k": "L", "a": _r2(a), "b": _r2(b), "deg": round(_deg(a, b), 1)})
    for k, a in enumerate(sorted(arcs, key=lambda a: (round(a["p"][1], 1), round(a["p"][0], 1)))):
        door = DOOR_R_M[0] <= a["r"] <= DOOR_R_M[1] and DOOR_SWEEP[0] <= a["sweep"] <= DOOR_SWEEP[1]
        out.append({"id": f"A{k + 1}", "k": "A", "p": _r2(a["p"]), "r": round(a["r"], 2), "sweep": round(a["sweep"]),
                    "door": door, "layer": a["layer"]})
    wins = []
    if win_segs:
        boxes = [(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for (a, b), _l in win_segs]
        for g in _clusters(boxes, CLUSTER_M):
            sym = _symbol([win_segs[i][0] for i in g])
            if sym and WINDOW_W_M[0] <= sym["w"] <= WINDOW_W_M[1]:
                wins.append(dict(sym, layer=win_segs[g[0]][1][:16], n=len(g)))
    for k, s in enumerate(sorted(wins, key=lambda s: (round(s["p"][1], 1), round(s["p"][0], 1)))):
        out.append({"id": f"G{k + 1}", "k": "G", "p": _r2(s["p"]), "w": round(s["w"], 2), "deg": round(s["deg"], 1),
                    "layer": s["layer"]})
    stairs = []
    if stair_segs:
        boxes = [(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])) for a, b in stair_segs]
        for g in _clusters(boxes, STAIR_CLUSTER_M):
            if len(g) < 3:
                continue
            xs = [p[0] for i in g for p in stair_segs[i]]
            ys = [p[1] for i in g for p in stair_segs[i]]
            stairs.append({"p": ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0), "w": max(xs) - min(xs),
                           "h": max(ys) - min(ys), "n": len(g)})
    for k, s in enumerate(sorted(stairs, key=lambda s: (round(s["p"][1], 1), round(s["p"][0], 1)))):
        out.append({"id": f"S{k + 1}", "k": "S", "p": _r2(s["p"]), "size": [round(s["w"], 2), round(s["h"], 2)],
                    "n": s["n"]})
    # texts: the label blocks of the reader's own label rules, in metres in the drawing's orientation (y up)
    runs = []
    for t in page.texts:
        b = getattr(t, "box", None)
        if not getattr(t, "text", None) or not b:
            continue
        x0, y0 = (float(b[0]) - frame.box[0]) * frame.s, (float(b[1]) - frame.box[1]) * frame.s
        x1, y1 = (float(b[2]) - frame.box[0]) * frame.s, (float(b[3]) - frame.box[1]) * frame.s
        runs.append(TextRun(id=str(t.id), text=str(t.text), box=(x0, y0, x1, y1),
                            height=float(getattr(t, "height", None) or (b[3] - b[1]) or 1e-3) * frame.s,
                            rotation_deg=float(getattr(t, "rotation_deg", 0.0) or 0.0)))
    up = lambda p: (float(p[0]), frame.h - float(p[1]))  # noqa: E731 - y up (metres) -> the frame's y down
    try:
        blocks = LB.merge_label_blocks(runs)
    except Exception:  # noqa: BLE001 - texts the label reader cannot take: no label blocks
        blocks = []
    used = set()
    labels = []
    for blk in blocks:
        name = re.sub(r"\s+", " ", str(getattr(blk, "name", "") or "")).strip()
        if not name or getattr(blk, "anchor", None) is None:
            continue
        used |= {r.id for r in getattr(blk, "runs", []) or []}
        labels.append({"p": up(blk.anchor), "text": name[:40], "area": getattr(blk, "area_m2", None),
                       "size": str(getattr(blk, "size_text", None) or "")[:16] or None,
                       "type": getattr(blk, "room_type", None), "exterior": bool(getattr(blk, "exterior", False))})
    for k, lb in enumerate(sorted(labels, key=lambda s: (round(s["p"][1], 1), round(s["p"][0], 1)))):
        it = {"id": f"T{k + 1}", "k": "T", "p": _r2(lb["p"]), "text": lb["text"], "type": lb["type"]}
        if lb["area"]:
            it["area"] = round(float(lb["area"]), 2)
        if lb["size"]:
            it["size"] = lb["size"]
        if lb["exterior"]:
            it["exterior"] = True
        out.append(it)
    loose = {"K": [], "M": [], "Z": [], "D": [], "X": []}
    for r in runs:
        if r.id in used:
            continue
        text = re.sub(r"\\[A-Za-z][^;]*;|[{}]", "", r.text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text or len(text) > 60:
            continue
        p = up(((r.box[0] + r.box[2]) / 2.0, (r.box[1] + r.box[3]) / 2.0))
        mk = MK.parse_mark(text)
        m = AREA_RE.search(text)
        if mk is not None:
            loose["K"].append({"p": p, "text": text[:24]})
        elif m:
            loose["M"].append({"p": p, "area": float(m.group(1).replace(",", "."))})
        elif SIZE_TAG_RE.match(text):
            loose["Z"].append({"p": p, "text": re.sub(r"\s+", "", text)})
        elif NUMBER_RE.match(text):
            loose["D"].append({"p": p, "text": text})
        else:
            loose["X"].append({"p": p, "text": text[:40]})
    for d in getattr(page, "dimensions", None) or []:
        pa, pb = frame.from_page(d.p1), frame.from_page(d.p2)
        val = d.text if d.text not in (None, "", "<>") else (d.printed or f"{float(d.measured_units) * frame.s:.2f}")
        loose["D"].append({"p": ((pa[0] + pb[0]) / 2.0, (pa[1] + pb[1]) / 2.0), "text": str(val)[:16],
                           "span": round(math.dist(pa, pb), 2)})
    for key, rows in loose.items():
        for k, x in enumerate(sorted(rows, key=lambda s: (round(s["p"][1], 1), round(s["p"][0], 1)))):
            it = {"id": f"{key}{k + 1}", "k": key, "p": _r2(x["p"])}
            it.update({kk: v for kk, v in x.items() if kk != "p"})
            out.append(it)
    return out


# =================================================================================================== the reading
def _size(poly_frame: list) -> list:
    """The sides of a polygon's smallest enclosing rectangle (metres, long side first)."""
    from shapely.geometry import Polygon

    g = Polygon(poly_frame)
    if not g.is_valid:
        g = g.buffer(0)
    try:
        r = list(g.minimum_rotated_rectangle.exterior.coords)
        a, b = math.dist(r[0], r[1]), math.dist(r[1], r[2])
    except Exception:  # noqa: BLE001 - a degenerate room: its box
        xs, ys = [p[0] for p in poly_frame], [p[1] for p in poly_frame]
        a, b = max(xs) - min(xs), max(ys) - min(ys)
    return [round(max(a, b), 2), round(min(a, b), 2)]


def reading_items(facts: dict, frame: Frame, walls: Optional[list] = None) -> list:
    """The reading's items of a level (``critic_checks.level_facts``; ``walls`` the level's walls of building.json,
    when the reading is at hand) in ``frame``, each with the reading's own id as ``bid``."""
    out: list = []
    for k, r in enumerate(facts.get("rooms") or []):
        poly = [frame.from_building(q) for q in r.get("poly") or []]
        if len(poly) < 3:
            continue
        out.append({"id": f"r{k + 1}", "k": "r", "bid": r["id"], "label": str(r.get("label") or "")[:32],
                    "type": r.get("type"), "area": r.get("area"), "size": _size(poly),
                    "p": _r2(frame.from_building(r["at"])), "poly": [_r2(q) for q in poly]})
    for k, s in enumerate(facts.get("outdoor") or []):
        poly = [frame.from_building(q) for q in s.get("poly") or []]
        if len(poly) < 3:
            continue
        out.append({"id": f"b{k + 1}", "k": "b", "bid": s["id"], "label": str(s.get("label") or "")[:32],
                    "type": s.get("kind"), "area": s.get("area"), "size": _size(poly),
                    "p": _r2(frame.from_building(s["at"])), "poly": [_r2(q) for q in poly]})
    rid = {it["bid"]: it["id"] for it in out}
    count = {"d": 0, "n": 0, "o": 0}
    for o in facts.get("openings") or []:
        key = {"door": "d", "window": "n"}.get(o.get("type"), "o")
        count[key] += 1
        sides = [rid.get(x, x) for x in o.get("sides") or []]
        out.append({"id": f"{key}{count[key]}", "k": key, "bid": o["id"], "p": _r2(frame.from_building(o["at"])),
                    "w": o.get("width"), "sides": sides, "ext": bool(o.get("exterior")),
                    "inf": bool(o.get("inferred"))})
    for k, s in enumerate(facts.get("stairs") or []):
        out.append({"id": f"s{k + 1}", "k": "s", "bid": s["id"], "p": _r2(frame.from_building(s["at"]))})
    for k, s in enumerate(facts.get("lifts") or []):
        out.append({"id": f"l{k + 1}", "k": "l", "bid": s["id"], "p": _r2(frame.from_building(s["at"]))})
    for k, w in enumerate(walls or []):
        if not (w.get("start") and w.get("end")):
            continue
        a, b = frame.from_building(w["start"]), frame.from_building(w["end"])
        inferred = any(isinstance(e, dict) and (e.get("method") == "inferred" or e.get("rule") == "outline_closure")
                       for e in w.get("evidence") or [])
        out.append({"id": f"w{k + 1}", "k": "w", "bid": w["id"], "a": _r2(a), "b": _r2(b),
                    "t": round(float(w.get("thickness") or 0.0), 2), "ext": bool(w.get("exterior")), "inf": inferred,
                    "deg": round(_deg(a, b), 1)})
    return out


def level_vector(page, frame: Frame, facts: dict, walls: Optional[list] = None, wall_layers=()) -> dict:
    """The stored vector data of one level image: the frame, the drawing's items and the reading's (pure but for the
    page)."""
    return {"version": 1, "frame": frame.to_dict(),
            "source": source_items(page, frame, wall_layers) if page is not None else [],
            "reading": reading_items(facts, frame, walls), "has_walls": walls is not None,
            "has_source": page is not None}


def write_vector(dest: Path, vec: dict) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(vec, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return dest


def load_vector(images_root: Path, item: dict) -> Optional[dict]:
    """The vector data of an index entry (``item["vector"]``: the file beside its images), or None."""
    name = item.get("vector")
    if not name or not item.get("folder"):
        return None
    p = Path(images_root) / item["folder"] / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


# ========================================================================================================= lines
def _anchor(it: dict) -> Optional[tuple]:
    if it.get("p") is not None:
        return tuple(it["p"])
    if it.get("a") is not None and it.get("b") is not None:
        return ((it["a"][0] + it["b"][0]) / 2.0, (it["a"][1] + it["b"][1]) / 2.0)
    return None


def _dist(it: dict, q) -> float:
    if it.get("a") is not None and it.get("b") is not None:
        a, b = it["a"], it["b"]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = dx * dx + dy * dy
        t = 0.0 if n <= 1e-12 else max(0.0, min(1.0, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / n))
        return math.hypot(q[0] - (a[0] + t * dx), q[1] - (a[1] + t * dy))
    if it.get("poly"):
        from shapely.geometry import Point, Polygon

        g = Polygon(it["poly"])
        g = g if g.is_valid else g.buffer(0)
        return float(g.distance(Point(q)))
    p = _anchor(it)
    return math.dist(p, q) if p is not None else float("inf")


def _xy(p, o) -> str:
    return f"({p[0] - o[0]:.1f},{p[1] - o[1]:.1f})"


def item_line(it: dict, origin=(0.0, 0.0)) -> str:
    """One item as one line (pure); points relative to ``origin`` (a crop's top-left corner in the level frame)."""
    k, i = it["k"], it["id"]
    if k == "W":
        L = math.dist(it["a"], it["b"])
        ang = f", at {it['deg']:.0f} deg" if _off_axis(it.get("deg") or 0.0) > 3.0 else ""
        return f"{i} wall {it['t']:.2f} thick {_xy(it['a'], origin)}-{_xy(it['b'], origin)} {L:.2f} long{ang}"
    if k == "L":
        return f"{i} lone wall line {_xy(it['a'], origin)}-{_xy(it['b'], origin)}"
    if k == "A":
        swing = " door swing" if it.get("door") else ""
        return f"{i} arc r {it['r']:.2f} {it['sweep']} deg at {_xy(it['p'], origin)}{swing}"
    if k == "G":
        return f"{i} window symbol {it['w']:.2f} wide at {_xy(it['p'], origin)}"
    if k == "S":
        return f"{i} stair lines x{it['n']} in {it['size'][0]:.1f}x{it['size'][1]:.1f} at {_xy(it['p'], origin)}"
    if k == "T":
        extra = (f" {it['area']:.2f} m2" if it.get("area") else "") + (f" {it['size']}" if it.get("size") else "")
        return f"{i} label '{it['text']}'{extra} at {_xy(it['p'], origin)}" + (" (outdoor)" if it.get("exterior")
                                                                               else "")
    if k == "M":
        return f"{i} area text {it['area']:.2f} m2 at {_xy(it['p'], origin)}"
    if k in ("Z", "K", "X"):
        word = {"Z": "size tag", "K": "level mark", "X": "text"}[k]
        return f"{i} {word} '{it['text']}' at {_xy(it['p'], origin)}"
    if k == "D":
        span = f" span {it['span']:.2f}" if it.get("span") else ""
        return f"{i} dimension {it['text']} at {_xy(it['p'], origin)}{span}"
    if k in ("r", "b"):
        area = f" {float(it['area']):.1f} m2" if it.get("area") is not None else ""
        return (f"{i} {'room' if k == 'r' else 'outdoor'} '{it['label']}' {it.get('type') or '?'}{area} "
                f"{it['size'][0]:.2f}x{it['size'][1]:.2f} at {_xy(it['p'], origin)}")
    if k in ("d", "n", "o"):
        word = {"d": "door", "n": "window", "o": "opening"}[k]
        sides = " | ".join(str(s) for s in it.get("sides") or []) or "?"
        w = f" {float(it['w']):.2f}" if it.get("w") else ""
        return f"{i} {word}{w} at {_xy(it['p'], origin)} between {sides}" + (" inferred" if it.get("inf") else "")
    if k == "w":
        flags = (" exterior" if it.get("ext") else "") + (" inferred" if it.get("inf") else "")
        return f"{i} wall {it['t']:.2f} {_xy(it['a'], origin)}-{_xy(it['b'], origin)}{flags}"
    if k in ("s", "l"):
        return f"{i} {'stair' if k == 's' else 'lift'} at {_xy(it['p'], origin)}"
    return f"{i} {k}"


def _inside(it: dict, region) -> bool:
    """Whether an item lies in ``region``: its point, or any part of its segment (a wall crossing a close-up)."""
    x0, y0, x1, y1 = region
    if it.get("a") is not None and it.get("b") is not None:
        (ax, ay), (bx, by) = it["a"], it["b"]
        t0, t1 = 0.0, 1.0                                       # Liang-Barsky clipping of the segment
        for p, q in ((-(bx - ax), ax - x0), (bx - ax, x1 - ax), (-(by - ay), ay - y0), (by - ay, y1 - ay)):
            if abs(p) < 1e-12:
                if q < 0:
                    return False
                continue
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return False
        return True
    p = it.get("p")
    return p is not None and x0 <= p[0] <= x1 and y0 <= p[1] <= y1


def _tag_point(it: dict) -> Optional[tuple]:
    return _anchor(it)


KIND_STEP_M = 0.5              # in a place's list, one step of PRIORITY weighs as this much distance
INVENTORY_KINDS = ("T", "S", "K", "M", "Z", "X", "G", "A", "W")


def inventory_keep(it: dict) -> bool:
    """The drawing items the inventory (what the plan holds) needs: labels, stairs, texts, windows, door arcs and the
    walls drawn at an angle to the image's edges."""
    if it["k"] == "W":
        return _off_axis(it.get("deg") or 0.0) > 3.0
    return it["k"] in INVENTORY_KINDS


def _dedupe(items: list) -> list:
    """The same text at the same place once (a drawing often holds a label twice, one on another layer)."""
    seen, out = set(), []
    for side, it in items:
        key = (it["k"], it.get("text"), round(it["p"][0], 1), round(it["p"][1], 1)) if it.get("text") is not None \
            and it.get("p") is not None else None
        if key is not None and key in seen:
            continue
        if key is not None:
            seen.add(key)
        out.append((side, it))
    return out


def block(vec: dict, *, what: str = "the image", focus: Optional[list] = None, region=None,
          cap_tokens: int = CAP_TOKENS, sides: tuple = ("source", "reading"), radius: float = FOCUS_M,
          tags: bool = False, keep=None) -> dict:
    """The text block of one question (pure): ``focus`` = ``[(name, (x, y))]`` the places asked about (frame metres):
    each item goes under its nearest place within ``radius``, ordered by distance plus ``KIND_STEP_M`` per step of its
    kind's ``PRIORITY`` (a label or a door arc before the nearest dimension), the places sharing the cap in turn; with
    no focus, every item of the ``region`` (frame metres ``(x0, y0, x1, y1)``; default the whole image) by kind
    (``PRIORITY``). ``sides``: the drawing's items, the reading's or both; ``keep``: a filter of the items. The lines
    are cut at ``cap_tokens`` (``estimate_tokens``), a last line saying how many were left out. Returns ``{text,
    tokens, listed, left_out, ids, tags}`` (``tags``: ``[(id, side, nx, ny)]`` normalised in the region, for
    ``tag_image``)."""
    fr = vec.get("frame") or {}
    W, H = float(fr.get("w") or 1.0), float(fr.get("h") or 1.0)
    region = tuple(region) if region is not None else (0.0, 0.0, W, H)
    origin = (region[0], region[1])
    rw, rh = region[2] - region[0], region[3] - region[1]
    items = _dedupe([(side, it) for side in sides for it in vec.get(side) or [] if _inside(it, region)
                     and (keep is None or keep(it))])
    head = HEADER.format(what=what, w=rw, h=rh, kx=1000.0 / max(rw, 1e-9), ky=1000.0 / max(rh, 1e-9),
                         tags="; the ids are tagged in blue in the images" if tags else "")
    budget = int(cap_tokens) - estimate_tokens(head)
    groups: list = []
    if focus:
        near: dict = {n: [] for n, _p in focus}
        for side, it in items:
            best = min(((_dist(it, p), n) for n, p in focus), key=lambda t: t[0])
            if best[0] <= radius:
                near[best[1]].append((best[0], PRIORITY.get(it["k"], 9), side, it))
        for n, p in focus:
            rows = sorted(near[n], key=lambda t: (t[0] + KIND_STEP_M * t[1], t[1]))
            groups.append((f"{n} at {_xy(p, origin)}:", [(side, it) for _d, _pr, side, it in rows]))
    else:
        rows = sorted(items, key=lambda t: (PRIORITY.get(t[1]["k"], 9), t[1]["id"][0],
                                            int(re.sub(r"\D", "", t[1]["id"]) or 0)))
        groups.append(("", rows))
    lines, ids, tag_list = [head], [], []
    total = sum(len(g[1]) for g in groups)
    used = estimate_tokens(head)
    if budget <= 0:
        return {"text": "", "tokens": 0, "listed": 0, "left_out": total, "ids": [], "tags": []}
    # round robin over the groups (a mark's nearest items first), so every place gets its share of the cap
    queues = [list(g[1]) for g in groups]
    heads_done = [False] * len(groups)
    out_lines: list = [[] for _ in groups]
    listed = 0
    stop = False
    while not stop and any(queues):
        stop = True
        for gi, q in enumerate(queues):
            if not q:
                continue
            side, it = q[0]
            line = item_line(it, origin)
            cost = estimate_tokens(line) - 30 + (0 if heads_done[gi] or not groups[gi][0]
                                                 else estimate_tokens(groups[gi][0]) - 30)
            if used + cost > cap_tokens - RESERVE_TOKENS:
                q.clear()
                continue
            q.pop(0)
            heads_done[gi] = True
            out_lines[gi].append(line)
            used += cost
            listed += 1
            ids.append(it["id"])
            tp = _tag_point(it)
            if tp is not None and len(tag_list) < TAG_MAX:
                tag_list.append((it["id"], side, (tp[0] - origin[0]) / rw, (tp[1] - origin[1]) / rh))
            stop = False
    for (title, _rows), ls in zip(groups, out_lines):
        if title:
            lines.append(title + ("" if ls else " nothing listed"))
            lines += [f"  {x}" for x in ls]
        else:
            lines += ls
    if listed < total:
        lines.append(f"({total - listed} more items within these places not listed: the size limit)")
    text = "\n".join(lines)
    return {"text": text, "tokens": estimate_tokens(text), "listed": listed, "left_out": total - listed, "ids": ids,
            "tags": tag_list}


def room_block(vec: dict, rooms: list, cap_tokens: int = CAP_TOKENS) -> dict:
    """The drawing's items per room of a floor text (pure; the plausibility check, which has no image): ``rooms`` =
    ``[(text id, (x, y) frame metres)]``; each room is the reading room of the level image containing its point (a
    copy storey's room is its page's room at the same place); listed: the drawing labels and area texts inside it, the
    window symbols, size tags and door arcs on its outline (within ``EDGE_M``); then the drawing labels inside no room
    (a room or balcony the reading may lack). Lines cut at ``cap_tokens``."""
    from shapely.geometry import Point, Polygon

    src = [s for s in vec.get("source") or [] if s["k"] in ("T", "M", "G", "Z", "A")]
    polys = []
    for it in vec.get("reading") or []:
        if it["k"] in ("r", "b") and len(it.get("poly") or []) >= 3:
            g = Polygon(it["poly"])
            g = g if g.is_valid else g.buffer(0)
            polys.append((it, g, g.buffer(0.1)))
    head = ("What the drawing file holds per room of the list (exact, from its vectors and texts; ids are the "
            "drawing's): the labels and area texts inside the room, the window symbols (G, with width), size tags (Z) "
            "and door arcs (A) on its outline. A room with no window symbol on its outline may still have a window "
            "drawn in another way.")
    lines, used, listed, total = [head], estimate_tokens(head), 0, 0
    inside_any = set()
    pts = {s["id"]: Point(s["p"]) for s in src}
    for tid, p in rooms:
        hit = next(((g, gb) for _it, g, gb in polys if g.distance(Point(p)) <= 0.05), None)
        if hit is None:
            continue
        total += 1
        g, gb = hit
        edge_line = g.boundary
        lab = [s for s in src if s["k"] in ("T", "M") and gb.contains(pts[s["id"]])]
        inside_any |= {s["id"] for s in lab}
        edge = [s for s in src if s["k"] in ("G", "Z", "A") and edge_line.distance(pts[s["id"]]) <= EDGE_M]
        bits = [f"{s['id']} '{s['text']}'" + (f" {s['area']:.2f} m2" if s.get("area") else "") if s["k"] == "T"
                else f"{s['id']} {s['area']:.2f} m2" for s in lab]
        bits += [f"{s['id']} window {s['w']:.2f}" if s["k"] == "G" else
                 (f"{s['id']} tag {s['text']}" if s["k"] == "Z" else f"{s['id']} arc r {s['r']:.2f}") for s in edge]
        line = f"- {tid}: " + ("; ".join(bits) if bits else "nothing on its outline or inside")
        cost = estimate_tokens(line) - 30
        if used + cost > cap_tokens - RESERVE_TOKENS:
            continue
        lines.append(line)
        used += cost
        listed += 1
    free = [s for s in src if s["k"] == "T" and s["id"] not in inside_any
            and not any(gb.contains(pts[s["id"]]) for _it, _g, gb in polys)]
    if free:
        line = "Drawing labels inside no room of the model: " + "; ".join(
            f"{s['id']} '{s['text']}'" + (f" {s['area']:.2f} m2" if s.get("area") else "") for s in free[:20])
        if used + estimate_tokens(line) - 30 <= cap_tokens - RESERVE_TOKENS:
            lines.append(line)
    text = "\n".join(lines)
    return {"text": text, "tokens": estimate_tokens(text), "listed": listed, "left_out": total - listed,
            "ids": [], "tags": []}


# ===================================================================================================== questions
def frame_of(vec: dict) -> Frame:
    fr = vec.get("frame") or {}
    return Frame(fr["box"], fr["tf"])


def crop_region(vec: dict, point_norm, size_px, crop_px: float) -> tuple:
    """The frame-metre region of a close-up of ``crop_px`` pixels of the level image (``size_px``) around a normalised
    point, cut at the image's edges as ``critic_checks.second_image`` cuts it."""
    fr = vec.get("frame") or {}
    W, H = float(fr["w"]), float(fr["h"])
    w, h = float(size_px[0]), float(size_px[1])
    x, y = float(point_norm[0]) * w, float(point_norm[1]) * h
    half = crop_px / 2.0
    x0, y0, x1, y1 = int(max(0, x - half)), int(max(0, y - half)), int(min(w, x + half)), int(min(h, y + half))
    return (x0 / w * W, y0 / h * H, x1 / w * W, y1 / h * H)


def question_block(which: str, item: dict, vec: dict, *, cap_tokens: int, tags: bool = False,
                   chunk: Optional[list] = None, crop_px: float = 400.0) -> Optional[dict]:
    """The vector text of one call (pure): ``inventory`` the drawing's labels, stairs, texts, windows, door arcs and
    angled walls of the whole plan; ``compare`` both sides near each of the ``chunk``'s marks; ``second`` the drawing's
    items in the close-up around the ring; ``judge`` both sides in the finding's crop (``item["crop"]``, frame metres);
    ``plausibility`` the drawing's items per room of the floor text (``room_block``)."""
    if cap_tokens <= 0:
        return None
    fr = frame_of(vec)
    if which == "inventory":
        return block(vec, what="the floor plan image", sides=("source",), keep=inventory_keep, cap_tokens=cap_tokens,
                     tags=tags)
    if which == "compare":
        focus = [(f"mark {q['n']}", fr.from_building(q["at"])) for q in chunk or []]
        return block(vec, what="both images", focus=focus, cap_tokens=cap_tokens, tags=tags)
    if which == "second":
        if not item.get("size"):
            return None
        region = crop_region(vec, item["point"], item["size"], crop_px)
        p = (float(item["point"][0]) * fr.w, float(item["point"][1]) * fr.h)
        return block(vec, what="the close-up", focus=[("the ring", p)], region=region, sides=("source",),
                     radius=math.hypot(region[2] - region[0], region[3] - region[1]), cap_tokens=cap_tokens, tags=tags)
    if which == "judge":
        region = tuple(item["crop"])
        p = fr.from_building(item["at"])
        return block(vec, what="both close-ups", focus=[("the place", p)], region=region,
                     radius=math.hypot(region[2] - region[0], region[3] - region[1]), cap_tokens=cap_tokens, tags=tags)
    if which == "plausibility":
        ids = item.get("ids") or {}
        want = list(ids.get("room") or []) + [x for x in ids.get("outdoor") or [] if x not in (ids.get("room") or [])]
        pts = item.get("points") or {}
        rooms = [(rid, fr.from_building(pts[rid])) for rid in want if pts.get(rid)]
        return room_block(vec, rooms, cap_tokens=cap_tokens)
    return None


# ======================================================================================================= overlay
def tag_image(src: Path, tags: list, dest: Path, side: str) -> Path:
    """``src`` with each tag of ``side`` (``source`` on the drawing, ``reading`` on the model) drawn as its id in small
    blue letters on white, a little above and right of its point (moved when it would cover another tag), saved as
    ``dest``. The ids are the text block's."""
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    placed: list = []
    for tid, s, nx, ny in tags:
        if s != side or not (0.0 <= nx <= 1.0 and 0.0 <= ny <= 1.0):
            continue
        x, y = nx * w, ny * h
        tw, th = 7 * len(tid) + 4, 13
        for dx, dy in ((4, -th - 2), (4, 3), (-tw - 4, -th - 2), (-tw - 4, 3)):
            bx = min(max(0.0, x + dx), w - tw)
            by = min(max(0.0, y + dy), h - th)
            box = (bx, by, bx + tw, by + th)
            if not any(box[0] < q[2] and q[0] < box[2] and box[1] < q[3] and q[1] < box[3] for q in placed):
                break
        placed.append(box)
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(0, 90, 200))
        d.rectangle(box, fill=(255, 255, 255))
        d.text((box[0] + 2, box[1]), tid, fill=(0, 90, 200), font=font)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, quality=88)
    return dest
