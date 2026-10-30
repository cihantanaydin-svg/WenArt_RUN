"""Soft seats as soft, well-made products (pure, no dependencies: the fit ranks with it, the build dresses and joins
with it, the model review and Argus check with it; 30 Oct 2026, lessons UL131 and UL140, the user on real04 run
20261029-201533-full: "I did not like these sofa models" (boxy grey sofas with flat faceted back cushions and white
piping lines) and "I like this sofa but it needs more details, also the gaps need a rework" (the L corner sofa
"Sofa en L" in flat white, its parts apart)).

What the run showed (measured on its scene manifest, its fitted building and the library audit):

- the two "Crate and Barrel sofa" models of the play room carried one 256 px texture (the audit's note "largest texture
  256 px (< 512)") and ranked first in their size step all the same: the fit's texture-map key read a ``texture_maps``
  record no catalogue entry has (the audit writes ``pbr_maps``), so every model ranked as "base colour only";
- the corner sofa had no texture at all ("untextured (material colours only)", 4 materials named "01 - Default1",
  "02 - Default1", "default_face_material"): the build kept its flat export colours although the design asked for a
  light grey fabric (``design_not_shown``: no recolourable slot);
- every library model was rebuilt flat-shaded: the build made a new mesh from the file's positions and faces and
  dropped the file's own normals (a smooth cushion of 528 faces imported smooth, 0 faces smooth after the rebuild), so
  rounded cushions showed their facets;
- the fit scaled the corner sofa uniformly (0.9348 on every axis) about one pivot and the importer reads every part in
  world space: the build did not open its gaps. The model is 9 loose parts (the audit's measure: one mesh object, its
  largest part 39 % of the surface, 8 parts outside the main body's box): modules, cushions, a tray and a frame
  modelled apart.

Rules for every project:

- ``grade(entry)``: the quality of an upholstered library model from its own catalogue record (or its fitted asset):
  points for a texture under 512 px (1; at 256 px or less 3, poor by itself: a blurred weave, seams drawn as lines,
  the rejected sofa), flat colours (1: the build dresses its fabric slots, so only one), a double-sided export
  (non-manifold edges over half: flat faces twice), a coarse mesh (under ``COARSE_FACES_M2`` faces per m² of its box
  surface while its map record names no normal map to carry the detail; 2 under ``LOW_POLY_FACES`` faces), a judged
  poor look (the judges' mean at or under 2.5) or the audit's vision quality at or under 2. 0 points: good; 1-2:
  fair (``STEPS_PER_POINT`` size steps per point in the fit's rank); 3 or more: poor (``POOR_STEPS``: after every
  model within the caps). A ranking, never a gate: the drawn piece is still built with the best model there is
  (CLAUDE.md library rules), and the review names a poor one.
- ``fabric_slots(slots)``: the flat (untextured) material slots of a soft seat that are its upholstery: a slot named
  for a fabric always; a slot whose name says nothing (SketchUp's "Color_A01", "02 - Default1") when the model's
  textured slots cover less than ``UPHOLSTERY_TEXTURED_SHARE`` of it: the largest such slot (at least
  ``FIRST_SHARE`` of the surface) and every other covering ``SECOND_SHARE``; never a slot named for a hard material,
  a metallic or a see-through one. The build gives them the style's fabric (the weave's normal and roughness maps, the
  fabric's sheen) in the design's fabric colour, else in the named colour nearest the slot's own
  (``furniture._dress_fabric``).
- ``face_parts`` / ``vertex_parts`` / ``join_parts``: the loose parts of a model (connected faces, positions merged on
  a 0.1 mm grid, measured before the build separates double-sided faces), their bodies (parts whose boxes touch or
  intersect: a cushion inside its frame), the gaps between bodies that face each other (one axis apart by
  ``GAP_MIN_M``-``GAP_MAX_M``, overlapping over ``FACE_SHARE`` of the smaller on the two others) and the joining: from
  the body of the largest part, every facing body moves rigidly to touch the one it faces, never lifting a body that
  stands on the floor and never into another body; the fit's width is kept by the build (``fit_vertices``).
- ``rest_plan`` (30 Oct 2026, lesson UL167; the user on real04 run 20261030-043021-full, the same "Sofa en L": "I like
  this sofa but resting pieces seems like not connected to sitting, requires fixing"): the box joining could not see
  its gaps, every part's box touching the L seat's; now the rests (``seat_roles``: back panels, back cushions standing
  behind the seat, arms: tall thin panels near the top) are measured on their vertices against the seat they stand
  beside (the seat's edge in its top band, the rest's near face where they overlap) and slide across to touch it
  (no gap over ``REST_TOUCH_M`` = 5 mm; a gap over ``REST_GAP_MAX_M`` is by design), with their piping and what lies
  on them; a rest held over its base or deck comes down onto it; the two backs of an L's corner (a back and an arm)
  close their gap by sliding the one that runs along it. The model's own lean stays (the parametric and module sofas
  lean their back cushions ``parametric.BACK_CUSHION_LEAN_DEG`` on the deck behind the seat cushion).
- ``review(manifest)``: model review M33 and Argus U36: every library soft seat as built wears a fabric (no flat
  export colour left, ``flat_fabric``), keeps its parts joined (no facing gap wider than ``GAP_VISIBLE_M`` left,
  ``parts_apart``; its rests on their seat, ``rest_apart``, UL167), keeps the file's smooth shading (``faceted``) and
  is no poor model (``poor_model``: a library gap).
  A model the user rejected is model review M21's (Argus U19).
"""
from __future__ import annotations

import math
import re
from typing import Optional, Sequence

SOFT_SEAT_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman")
LESSONS: tuple[str, ...] = ("UL131", "UL140")

# --------------------------------------------------------------------------
# The grade of a library model (the fit's rank)
# --------------------------------------------------------------------------

LOW_RES_PX = 512                 # the audit's own threshold ("largest texture N px (< 512)")
POOR_RES_PX = 256                # a 256 px fabric over a 2 m sofa: about 8 mm a pixel, the weave and the seams blurred
SHELLS_PCT = 50                  # non-manifold edges over half: a double-sided export (SketchUp's two faces per face)
COARSE_FACES_M2 = 1500           # faces per m² of the box surface: under it, boxy cushions unless a normal map carries
                                 # the detail (the ABO sofas: 6,000-12,000; the corner sofa of real04: 1,644)
LOW_POLY_FACES = 3000            # = fit.FACES_LOW, the audit's own low-poly threshold
JUDGE_POOR = 2.5                 # the judges' mean photoreal quality (1-5) at or under: a judged poor look
VISION_POOR = 2                  # the audit's vision quality (1-5) at or under
POOR_POINTS = 3
STEPS_PER_POINT = 2              # the fit's size steps (5 % each) one point of a fair model adds to its rank
POOR_STEPS = 8                   # a poor model: 40 %, more than any two models inside the caps differ by (0.85-1.20)
PX_NOTE = re.compile(r"largest texture (\d+) px")
NM_NOTE = re.compile(r"(\d+)% non-manifold")
VQ_NOTE = re.compile(r"vision quality (\d)")
GRADES: tuple[str, ...] = ("good", "fair", "poor")


def _audit(entry: dict) -> dict:
    audit = entry.get("audit") if isinstance(entry, dict) else None
    return audit if isinstance(audit, dict) else {}


def _notes(entry: dict) -> list[str]:
    return [str(n) for n in _audit(entry).get("notes") or []]


def maps_of(entry: dict) -> dict:
    """The texture-map record of a catalogue entry (``pbr_maps``, the audit's) or a fitted asset (``texture_maps``)."""
    for key in ("texture_maps", "pbr_maps"):
        if isinstance(entry.get(key), dict):
            return dict(entry[key])
    return {}


def texture_px(entry: dict) -> Optional[int]:
    """The largest texture's size the audit noted (it notes it under 512 px only), None when not noted."""
    for n in _notes(entry):
        m = PX_NOTE.search(n)
        if m:
            return int(m.group(1))
    return None


def nonmanifold_pct(entry: dict) -> Optional[int]:
    for n in _notes(entry):
        m = NM_NOTE.search(n)
        if m:
            return int(m.group(1))
    return None


def flat_colours(entry: dict) -> bool:
    """True when the model has no base-colour texture at all (flat material colours)."""
    if entry.get("textured") is False or maps_of(entry).get("base_colour") is False:
        return True
    return any(n.startswith("untextured") for n in _notes(entry))


def faces_of(entry: dict) -> Optional[int]:
    for key in ("polycount", "faces"):
        n = entry.get(key)
        if isinstance(n, (int, float)) and not isinstance(n, bool) and n > 0:
            return int(n)
    return None


def face_density(entry: dict) -> Optional[float]:
    """Faces per m² of the model's box surface (its catalogue box, or the fitted one of an asset)."""
    n, box = faces_of(entry), entry.get("bbox_m")
    if n is None or not isinstance(box, (list, tuple)) or len(box) < 3:
        return None
    w, d, h = (float(v) for v in box[:3])
    surface = 2.0 * (w * d + w * h + d * h)
    return n / surface if surface > 1e-9 else None


def judge_mean(entry: dict) -> Optional[float]:
    q = entry.get("quality")
    vals = q if isinstance(q, (list, tuple)) else [q]
    vals = [float(v) for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
    return sum(vals) / len(vals) if vals else None


def vision_quality(entry: dict) -> Optional[float]:
    audit = _audit(entry)
    value = audit.get("vision_quality")
    if value is None and isinstance(audit.get("vision"), dict):
        value = audit["vision"].get("quality")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    doubts = audit.get("vision_doubt")
    for text in doubts if isinstance(doubts, list) else [doubts] if isinstance(doubts, str) else []:
        m = VQ_NOTE.search(str(text))
        if m:
            return float(m.group(1))
    return None


def grade(entry: dict) -> dict:
    """``{"grade": good | fair | poor, "points", "reasons": [...], "steps"}`` of an upholstered library model (module
    docstring) from its catalogue entry or its fitted asset (pure)."""
    points, reasons = 0, []

    def add(n: int, why: str) -> None:
        nonlocal points
        points += n
        reasons.append(f"{why} (+{n})")

    px = texture_px(entry)
    if px is not None and px <= POOR_RES_PX:
        add(POOR_POINTS, f"a {px} px texture: a blurred fabric, its seams drawn as lines")
    elif px is not None and px < LOW_RES_PX:
        add(1, f"a {px} px texture (under {LOW_RES_PX} px)")
    if flat_colours(entry):
        add(1, "no texture: flat material colours (the build dresses its fabric slots)")
    nm = nonmanifold_pct(entry)
    if nm is not None and nm >= SHELLS_PCT:
        add(1, f"{nm} % non-manifold edges: a double-sided export of flat faces")
    n = faces_of(entry)
    dens = face_density(entry)
    maps = maps_of(entry)
    if n is not None and n < LOW_POLY_FACES:
        add(2, f"{n} faces: low poly")
    elif dens is not None and dens < COARSE_FACES_M2 and "normal" in maps and not maps["normal"]:
        # (a model whose record does not say is not judged here: the older ABO entries carry none, and ABO ships
        # normal maps)
        add(1, f"{dens:.0f} faces per m² and no normal map: a coarse mesh, boxy cushions")
    jm = judge_mean(entry)
    if jm is not None and jm <= JUDGE_POOR:
        add(1, f"the judges' quality {jm:g}")
    vq = vision_quality(entry)
    if vq is not None and vq <= VISION_POOR:
        add(2, f"the audit's vision quality {vq:g}")
    level = "poor" if points >= POOR_POINTS else "fair" if points else "good"
    return {"grade": level, "points": points, "reasons": reasons,
            "steps": POOR_STEPS if level == "poor" else STEPS_PER_POINT * points}


# --------------------------------------------------------------------------
# The fabric slots of a soft seat (the build's dressing)
# --------------------------------------------------------------------------

FABRIC_RULE = "fabric"
# the material-name rules (wenart.assets.material_names.MATERIAL_RULES) that name a hard or a special material:
# never upholstery (leather keeps its own look)
HARD_RULES: tuple[str, ...] = ("mirror", "glass", "chrome", "metal", "ceramic", "stone_polished", "gloss", "plastic",
                               "leather", "rattan", "wood", "paper", "rubber", "stone", "bark", "foliage")
UPHOLSTERY_TEXTURED_SHARE = 0.30  # textured slots covering this share: the upholstery wears its own texture
FIRST_SHARE = 0.10               # the largest unnamed flat slot is the upholstery when it covers at least this
SECOND_SHARE = 0.20              # another unnamed flat slot joins it when it covers at least this (a second colour)
METALLIC_HARD = 0.5
ALPHA_HARD = 0.99


def fabric_slots(slots: Sequence[dict]) -> list[dict]:
    """The slots to dress (module docstring): ``slots`` are ``{"index", "name", "rule", "textured", "metallic",
    "alpha", "share"}`` (``rule``: ``material_names.name_rule`` of the name, ``unnamed`` when it names none;
    ``share``: of the model's surface). Returns ``[{"index", "name", "share", "why"}]`` in slot order (pure)."""
    def hard(s: dict) -> bool:
        return (str(s.get("rule")) in HARD_RULES or float(s.get("metallic") or 0.0) >= METALLIC_HARD
                or float(s.get("alpha") if s.get("alpha") is not None else 1.0) < ALPHA_HARD)

    flat = [s for s in slots if not s.get("textured") and not hard(s)]
    textured_share = sum(float(s.get("share") or 0.0) for s in slots if s.get("textured"))
    picked: dict[int, str] = {}
    for s in flat:
        if s.get("rule") == FABRIC_RULE:
            picked[int(s["index"])] = f"named for a fabric ({s.get('name')})"
    unnamed = sorted((s for s in flat if s.get("rule") != FABRIC_RULE), key=lambda s: -float(s.get("share") or 0.0))
    if unnamed and textured_share < UPHOLSTERY_TEXTURED_SHARE:
        first = unnamed[0]
        if float(first.get("share") or 0.0) >= FIRST_SHARE:
            picked.setdefault(int(first["index"]), f"the largest flat slot ({float(first['share']):.0%} of the "
                                                  "surface): the upholstery")
            for s in unnamed[1:]:
                if float(s.get("share") or 0.0) >= SECOND_SHARE:
                    picked.setdefault(int(s["index"]), f"a flat slot over {SECOND_SHARE:.0%} of the surface "
                                                      f"({float(s['share']):.0%}): upholstery too")
    by = {int(s["index"]): s for s in slots}
    return [{"index": i, "name": by[i].get("name"), "share": round(float(by[i].get("share") or 0.0), 4),
             "why": picked[i]} for i in sorted(picked)]


def face_areas(verts: Sequence, faces: Sequence) -> list[float]:
    """The area of every face (a fan of triangles from its first corner)."""
    out = []
    for f in faces:
        a = 0.0
        p0 = verts[f[0]]
        for i in range(1, len(f) - 1):
            p1, p2 = verts[f[i]], verts[f[i + 1]]
            u = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
            v = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
            c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            a += 0.5 * math.sqrt(c[0] * c[0] + c[1] * c[1] + c[2] * c[2])
        out.append(a)
    return out


def material_shares(verts: Sequence, faces: Sequence, face_materials: Sequence, n: int) -> list[float]:
    """Each material slot's share (0..1) of the model's surface."""
    areas = face_areas(verts, faces)
    total = sum(areas) or 1.0
    out = [0.0] * n
    for a, m in zip(areas, face_materials):
        if m is not None and 0 <= int(m) < n:
            out[int(m)] += a
    return [v / total for v in out]


# --------------------------------------------------------------------------
# The loose parts of a model and the gaps between them
# --------------------------------------------------------------------------

MERGE_EPS_M = 1e-4               # positions this close are one vertex (glTF splits vertices at seams)
GAP_MIN_M = 0.002                # two parts this close touch (a render shows no gap)
GAP_MAX_M = 0.06                 # two parts farther apart are apart by design (a side table, arms across a seat)
FACE_SHARE = 0.5                 # facing: the boxes overlap over this share of the smaller one on both other axes
FLOOR_TOL_M = 0.005              # a part whose bottom is this close to the model's bottom stands on the floor
MAX_PARTS = 600                  # more loose parts (tufts, buttons, stitches): not joined (pairwise boxes, the cost)
GAP_VISIBLE_M = 0.01             # M33: a facing gap left wider than this shows in a render (about 2 px at 4 m)


def face_parts(verts: Sequence, faces: Sequence, eps: float = MERGE_EPS_M) -> list[int]:
    """The loose part (0..k-1, in order of first face) of every face: faces joined by a shared vertex, vertices at
    one position (on an ``eps`` grid) merged (pure union-find)."""
    key: dict = {}
    vid = []
    for v in verts:
        k = (round(float(v[0]) / eps), round(float(v[1]) / eps), round(float(v[2]) / eps))
        vid.append(key.setdefault(k, len(key)))
    parent = list(range(len(key)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for f in faces:
        if not f:
            continue
        r0 = find(vid[f[0]])
        for i in f[1:]:
            r = find(vid[i])
            if r != r0:
                parent[r] = r0
    label: dict[int, int] = {}
    out = []
    for f in faces:
        root = find(vid[f[0]]) if f else -1
        out.append(label.setdefault(root, len(label)))
    return out


def vertex_parts(n_verts: int, faces: Sequence, face_part: Sequence[int], verts: Optional[Sequence] = None
                 ) -> tuple[list[int], dict[int, float]]:
    """``(the part of every vertex (-1: in no face), {part: surface area})`` from the faces' parts; the areas only
    when ``verts`` are given."""
    vp = [-1] * n_verts
    for f, p in zip(faces, face_part):
        for i in f:
            vp[i] = p
    areas: dict[int, float] = {}
    if verts is not None:
        for a, p in zip(face_areas(verts, faces), face_part):
            areas[p] = areas.get(p, 0.0) + a
    return vp, areas


def part_boxes(verts: Sequence, vert_part: Sequence[int]) -> dict[int, list[float]]:
    """``{part: [x0, y0, z0, x1, y1, z1]}``."""
    boxes: dict[int, list[float]] = {}
    for v, p in zip(verts, vert_part):
        if p < 0:
            continue
        b = boxes.get(p)
        x, y, z = float(v[0]), float(v[1]), float(v[2])
        if b is None:
            boxes[p] = [x, y, z, x, y, z]
        else:
            b[0], b[1], b[2] = min(b[0], x), min(b[1], y), min(b[2], z)
            b[3], b[4], b[5] = max(b[3], x), max(b[4], y), max(b[5], z)
    return boxes


def _gaps(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """The signed gap between two boxes along each axis (negative: they overlap by that much)."""
    return [max(b[k] - a[k + 3], a[k] - b[k + 3]) for k in range(3)]


def facing(a: Sequence[float], b: Sequence[float]) -> Optional[tuple[int, float, int]]:
    """``(axis, gap, sign)`` when box ``b`` faces box ``a`` across a small gap (module docstring), ``sign`` +1 when
    ``b`` lies on the positive side of ``a``; None otherwise."""
    g = _gaps(a, b)
    apart = [k for k in range(3) if g[k] > GAP_MIN_M]
    if len(apart) != 1:
        return None
    k = apart[0]
    if g[k] > GAP_MAX_M:
        return None
    for j in range(3):
        if j == k:
            continue
        overlap = -g[j]
        smaller = min(a[j + 3] - a[j], b[j + 3] - b[j])
        if overlap < FACE_SHARE * smaller - 1e-9:
            return None
    return k, g[k], (1 if b[k] >= a[k + 3] - 1e-9 else -1)


def bodies_of(boxes: dict[int, list[float]]) -> dict[int, int]:
    """``{part: body}``: parts whose boxes touch (within ``GAP_MIN_M``) or intersect are one rigid body."""
    ids = sorted(boxes)
    parent = {p: p for p in ids}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i, p in enumerate(ids):
        for q in ids[i + 1:]:
            if max(_gaps(boxes[p], boxes[q])) <= GAP_MIN_M:
                rp, rq = find(p), find(q)
                if rp != rq:
                    parent[max(rp, rq)] = min(rp, rq)
    return {p: find(p) for p in ids}


def _body_boxes(boxes: dict, body: dict, shift: Optional[dict] = None) -> dict[int, list[list[float]]]:
    out: dict[int, list] = {}
    for p, b in boxes.items():
        t = (shift or {}).get(body[p], (0.0, 0.0, 0.0))
        out.setdefault(body[p], []).append([b[0] + t[0], b[1] + t[1], b[2] + t[2], b[3] + t[0], b[4] + t[1],
                                            b[5] + t[2]])
    return out


def body_gaps(boxes: dict, body: dict, shift: Optional[dict] = None) -> list[dict]:
    """The facing gaps between bodies (``{"a", "b", "axis", "gap", "sign"}``, the smallest per pair of bodies)."""
    bb = _body_boxes(boxes, body, shift)
    keys = sorted(bb)
    out = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            best = None
            for x in bb[a]:
                for y in bb[b]:
                    f = facing(x, y)
                    if f is not None and (best is None or f[1] < best[1]):
                        best = f
            if best is not None:
                out.append({"a": a, "b": b, "axis": best[0], "gap": round(best[1], 5), "sign": best[2]})
    return out


def _penetrates(x: Sequence[float], y: Sequence[float]) -> bool:
    return max(_gaps(x, y)) < -GAP_MIN_M


def join_plan(boxes: dict[int, list[float]], areas: dict[int, float]) -> dict:
    """The joining of a model's loose parts (module docstring): ``{"shift": {body: (dx, dy, dz)}, "body": {part:
    body}, "record"}``; the record holds the parts, bodies, the gaps before and after and why a body stayed."""
    rec: dict = {"parts": len(boxes)}
    if len(boxes) < 2:
        rec.update(bodies=len(boxes), gaps=0, max_gap_m=0.0, joined=0, max_gap_after_m=0.0)
        return {"shift": {}, "body": {p: p for p in boxes}, "record": rec}
    if len(boxes) > MAX_PARTS:
        rec.update(skipped=f"{len(boxes)} loose parts (over {MAX_PARTS}): not joined")
        return {"shift": {}, "body": {p: p for p in boxes}, "record": rec}
    body = bodies_of(boxes)
    rec["bodies"] = len(set(body.values()))
    gaps = body_gaps(boxes, body)
    rec["gaps"] = len(gaps)
    rec["max_gap_m"] = round(max((g["gap"] for g in gaps), default=0.0), 4)
    floor = min(b[2] for b in boxes.values())
    bb = _body_boxes(boxes, body)
    on_floor = {k: min(x[2] for x in v) <= floor + FLOOR_TOL_M for k, v in bb.items()}
    anchor = body[max(boxes, key=lambda p: (areas.get(p, 0.0), -p))]
    shift: dict[int, tuple] = {anchor: (0.0, 0.0, 0.0)}
    links: dict[int, list] = {}
    for g in gaps:
        links.setdefault(g["a"], []).append((g["b"], g["axis"], g["gap"], g["sign"]))
        links.setdefault(g["b"], []).append((g["a"], g["axis"], g["gap"], -g["sign"]))
    stayed: list[str] = []
    queue = [anchor]
    while queue:
        p = queue.pop(0)
        for q, axis, gap, sign in sorted(links.get(p, []), key=lambda t: (t[2], t[0])):
            if q in shift:
                continue
            if axis == 2 and sign < 0 and on_floor.get(q):
                stayed.append(f"body {q}: stands on the floor under body {p} ({gap * 100:.1f} cm): not lifted")
                continue
            t = list(shift[p])
            t[axis] -= sign * gap
            cand = [[x[0] + t[0], x[1] + t[1], x[2] + t[2], x[3] + t[0], x[4] + t[1], x[5] + t[2]] for x in bb[q]]
            if axis == 2 and min(c[2] for c in cand) < floor - FLOOR_TOL_M:
                stayed.append(f"body {q}: would sink under the floor")
                continue
            clash = False
            for r, rboxes in bb.items():
                if r == q:
                    continue
                rt = shift.get(r, (0.0, 0.0, 0.0))
                moved = [[x[0] + rt[0], x[1] + rt[1], x[2] + rt[2], x[3] + rt[0], x[4] + rt[1], x[5] + rt[2]]
                         for x in rboxes]
                if any(_penetrates(c, m) for c in cand for m in moved) and not any(
                        _penetrates(c0, m0) for c0 in bb[q] for m0 in rboxes):
                    clash = True
                    break
            if clash:
                stayed.append(f"body {q}: closing its {gap * 100:.1f} cm gap would push it into another body")
                continue
            shift[q] = tuple(t)
            queue.append(q)
    moved = {k: v for k, v in shift.items() if any(abs(c) > 1e-12 for c in v)}
    after = body_gaps(boxes, body, shift)
    rec.update(joined=len(moved), max_gap_after_m=round(max((g["gap"] for g in after), default=0.0), 4),
               gaps_after=len(after))
    if moved:
        rec["moved_m"] = round(max(math.sqrt(sum(c * c for c in v)) for v in moved.values()), 4)
    if stayed:
        rec["stayed"] = stayed[:10]
    return {"shift": moved, "body": body, "record": rec}


def join_parts(verts: Sequence, vert_part: Sequence[int], areas: dict[int, float]) -> tuple[list, dict]:
    """``(verts with the facing bodies moved together, record)`` (``join_plan``); the record adds the model's width
    (x) before and after so the caller keeps the fitted width."""
    pts = [tuple(float(c) for c in v) for v in verts]
    boxes = part_boxes(pts, vert_part)
    plan = join_plan(boxes, areas)
    rec = plan["record"]
    xs = [p[0] for p in pts]
    rec["width_before_m"] = round(max(xs) - min(xs), 5) if xs else 0.0
    if plan["shift"]:
        body, shift = plan["body"], plan["shift"]
        out = []
        for v, p in zip(pts, vert_part):
            t = shift.get(body.get(p, -1)) if p >= 0 else None
            out.append((v[0] + t[0], v[1] + t[1], v[2] + t[2]) if t else v)
        pts = out
    # 30 Oct 2026 (UL167): the rests (back panels, back cushions behind the seat, arms) on and against their seat
    rests = rest_plan(pts, vert_part)
    rec["rests"] = rests["record"]
    if rests["shift"]:
        shift = rests["shift"]
        pts = [(v[0] + shift[p][0], v[1] + shift[p][1], v[2] + shift[p][2]) if p in shift else v
               for v, p in zip(pts, vert_part)]
        rec["joined"] = int(rec.get("joined") or 0) + len(rests["moved"])
    xs = [p[0] for p in pts]
    rec["width_after_m"] = round(max(xs) - min(xs), 5) if xs else 0.0
    return pts, rec


# --------------------------------------------------------------------------
# The rests on the seat (30 Oct 2026, lesson UL167; the user on real04 run 20261030-043021-full, the living room's low
# white L sofa "Sofa en L": "I like this sofa but resting pieces seems like not connected to sitting, requires
# fixing"). Its nine loose parts were one body by their boxes (every box touches the L seat's box, so ``join_plan``
# saw no gap at all), but the back panels stood on the base behind the seat cushions, apart from them, and the
# corner's two backs did not meet. A box says nothing about the surfaces inside an L; the vertices do.
# --------------------------------------------------------------------------

REST_TOP_SHARE = 0.60            # a rest (a back panel, a back cushion standing behind the seat, an arm) reaches this
#                                  share of the model's height ...
REST_MIN_H_SHARE = 0.25          # ... is at least this share of it tall ...
REST_THIN_M = 0.40               # ... at most this thin across (one horizontal axis) ...
REST_LONG_RATIO = 1.5            # ... and this much longer along the other
SEAT_TOP_SHARES = (0.30, 0.75)   # a seat (a cushion, a deck) has its top in this band of the model's height ...
SEAT_MIN_M = 0.25                # ... and both horizontal sides at least this long
SEAT_TOP_BAND_M = 0.15           # a seat's facing surface: its vertices this far under its top (the cushion's edge)
REST_OVER_M = 0.05               # a rest rises at least this far over the seat it rests on
REST_OVERLAP_M = 0.10            # a rest and its seat face each other along at least this much of the rest
REST_TOUCH_M = 0.005             # the rule: no gap above 5 mm between a rest and its seat, nor under a rest
REST_GAP_MAX_M = 0.10            # a rest farther from its seat stands apart by design (a console behind a sofa)
REST_GROUP_TOL_M = 0.005         # a small part inside a rest's box (its piping, its seam band) moves with it


def _part_verts(pts: Sequence, vert_part: Sequence[int]) -> dict[int, list]:
    out: dict[int, list] = {}
    for v, p in zip(pts, vert_part):
        if p >= 0:
            out.setdefault(p, []).append(v)
    return out


def seat_roles(boxes: dict[int, list[float]]) -> tuple[list[int], list[int]]:
    """``(seats, rests)`` of a soft seat's loose parts by their boxes (piece frame: +Z up; module comment): a rest is
    tall, reaches near the top and is a thin panel (``REST_*``); a seat is broad with its top in the seat band
    (``SEAT_*``) and no rest."""
    if not boxes:
        return [], []
    z0 = min(b[2] for b in boxes.values())
    h = max(b[5] for b in boxes.values()) - z0
    if h <= 1e-6:
        return [], []
    seats, rests = [], []
    for p, b in sorted(boxes.items()):
        w, d, t = b[3] - b[0], b[4] - b[1], b[5] - b[2]
        thin, long_ = min(w, d), max(w, d)
        if (b[5] >= z0 + REST_TOP_SHARE * h and t >= REST_MIN_H_SHARE * h and thin <= REST_THIN_M
                and long_ >= REST_LONG_RATIO * thin):
            rests.append(p)
        elif SEAT_TOP_SHARES[0] * h <= b[5] - z0 <= SEAT_TOP_SHARES[1] * h and thin >= SEAT_MIN_M:
            seats.append(p)
    return seats, rests


def _rest_gap(rest_box: list[float], rverts: list, seat_box: list[float], sverts: list) -> Optional[dict]:
    """The gap between a rest and a seat it stands beside (``{"axis", "sign", "gap", "lo", "hi"}``, ``sign`` +1
    when the rest stands on the seat's positive side along ``axis``), measured on the vertices where they face each
    other: the rest's near face over their overlap along the rest, the seat's edge in its top band; None when the
    rest is no rest of this seat (it stands on it, is not beside it, or they overlap too little)."""
    k = 0 if rest_box[3] - rest_box[0] < rest_box[4] - rest_box[1] else 1
    j = 1 - k
    lo, hi = max(rest_box[j], seat_box[j]), min(rest_box[j + 3], seat_box[j + 3])
    if hi - lo < REST_OVERLAP_M - 1e-9 or seat_box[5] > rest_box[5] - REST_OVER_M:
        return None
    band = seat_box[5] - min(SEAT_TOP_BAND_M, 0.5 * (seat_box[5] - seat_box[2]))
    top = [v for v in sverts if v[2] >= band - 1e-9 and lo - 1e-9 <= v[j] <= hi + 1e-9] or \
        [v for v in sverts if v[2] >= band - 1e-9]
    if not top:
        return None
    s_lo, s_hi = min(v[k] for v in top), max(v[k] for v in top)
    centre = (rest_box[k] + rest_box[k + 3]) / 2.0
    if centre > s_hi:
        sign = 1
    elif centre < s_lo:
        sign = -1
    else:
        return None                                   # it stands on the seat (a back cushion on the deck)
    near = [v for v in rverts if lo - 1e-9 <= v[j] <= hi + 1e-9] or rverts
    gap = (min(v[k] for v in near) - s_hi) if sign > 0 else (s_lo - max(v[k] for v in near))
    return {"axis": k, "sign": sign, "gap": gap, "lo": lo, "hi": hi}


def _moved(box: Sequence[float], t: Sequence[float]) -> list[float]:
    return [box[0] + t[0], box[1] + t[1], box[2] + t[2], box[3] + t[0], box[4] + t[1], box[5] + t[2]]


def _clip(move: float, axis: int, group: list[list[float]], others: list[list[float]]) -> float:
    """``move`` along ``axis`` cut where one of the group's boxes would run into one of ``others`` (boxes it does not
    already cut into), so the move ends touching it."""
    t = [0.0, 0.0, 0.0]
    t[axis] = move
    out = move
    for g in group:
        for o in others:
            if _penetrates(g, o) or not _penetrates(_moved(g, t), o):
                continue
            room = _gaps(g, o)[axis]
            out = math.copysign(min(abs(out), max(0.0, room)), move)
    return out


def rest_plan(pts: Sequence, vert_part: Sequence[int]) -> dict:
    """UL167 (module comment): every rest of a soft seat stands against its seat and on what is under it.
    ``{"shift": {part: (dx, dy, dz)}, "moved": [rest parts], "record"}``: per rest (with the small parts inside its
    box, its group) the gap to the seat it stands beside, measured on the vertices (``_rest_gap``); a gap of
    ``REST_TOUCH_M``-``REST_GAP_MAX_M`` closes by sliding the group across (never into another part it was clear of,
    ``_clip``); a rest still over the part under it (a base, a deck) by over ``REST_TOUCH_M`` comes down onto it; two
    rests of an L's legs meeting at the corner close their gap by sliding the one that runs along it. The record holds
    the gaps before and after (``max_gap_m``, ``max_gap_after_m``, ``corner_gap_after_m``)."""
    boxes = part_boxes(pts, vert_part)
    rec: dict = {"rests": 0, "seats": 0, "moved": 0, "max_gap_m": 0.0, "max_gap_after_m": 0.0}
    if len(boxes) < 2 or len(boxes) > MAX_PARTS:
        return {"shift": {}, "moved": [], "record": rec}
    seats, rests = seat_roles(boxes)
    rec.update(rests=len(rests), seats=len(seats))
    if not rests or not seats:
        return {"shift": {}, "moved": [], "record": rec}
    pv = _part_verts(pts, vert_part)
    shift: dict[int, list[float]] = {}
    groups: dict[int, list[int]] = {}
    taken: set = set()
    for r in rests:
        rb = boxes[r]
        # its group: the small parts inside its box (piping, a seam band) and what lies on its top (a tray)
        groups[r] = [r] + [p for p, b in boxes.items()
                           if p != r and p not in seats and p not in rests and p not in taken
                           and (all(b[a] >= rb[a] - REST_GROUP_TOL_M and b[a + 3] <= rb[a + 3] + REST_GROUP_TOL_M
                                    for a in range(3))
                                or (abs(b[2] - rb[5]) <= REST_GROUP_TOL_M
                                    and rb[0] <= (b[0] + b[3]) / 2.0 <= rb[3]
                                    and rb[1] <= (b[1] + b[4]) / 2.0 <= rb[4]))]
        taken.update(groups[r][1:])
    # the rests may cut into each other (two soft panels at a corner: the overlap is inside both), never into the rest
    in_rests = {p for grp in groups.values() for p in grp}

    def cur(p: int) -> list[float]:
        return _moved(boxes[p], shift.get(p, (0.0, 0.0, 0.0)))

    def verts_of(p: int) -> list:
        t = shift.get(p)
        return [(v[0] + t[0], v[1] + t[1], v[2] + t[2]) for v in pv.get(p, [])] if t else pv.get(p, [])

    def move(r: int, axis: int, d: float) -> None:
        for p in groups[r]:
            t = shift.setdefault(p, [0.0, 0.0, 0.0])
            t[axis] += d

    items, before, after, beside = [], [], [], []
    for r in rests:
        best, measured = None, set()
        for s in seats:
            g = _rest_gap(cur(r), verts_of(r), cur(s), verts_of(s))
            if g is not None:
                measured.add(s)                 # the nearest of them is the one it slides to: none is crossed
                if best is None or g["gap"] < best[1]["gap"]:
                    best = (s, g)
        if best is None:
            continue
        s, g = best
        item = {"rest": r, "seat": s, "axis": "xy"[g["axis"]], "gap_m": round(g["gap"], 4)}
        if g["gap"] > REST_GAP_MAX_M:                   # apart by design (a back cushion between them, a console)
            item["apart_by_design"] = True
            items.append(item)
            continue
        before.append(max(0.0, g["gap"]))
        if REST_TOUCH_M < g["gap"] <= REST_GAP_MAX_M:
            grp = groups[r]
            others = [cur(p) for p in boxes if p not in in_rests and p not in measured]
            d = _clip(-g["sign"] * g["gap"], g["axis"], [cur(p) for p in grp], others)
            if abs(d) > 1e-9:
                move(r, g["axis"], d)
                item["slid_m"] = round(abs(d), 4)
        # under it: the highest part below the rest's foot (its base, the deck), never the floor
        rb = cur(r)
        under = [cur(p) for p in boxes if p not in groups[r] and cur(p)[5] <= rb[2] + 1e-6
                 and min(rb[3], cur(p)[3]) - max(rb[0], cur(p)[0]) > 0.5 * min(rb[3] - rb[0], cur(p)[3] - cur(p)[0])
                 and min(rb[4], cur(p)[4]) - max(rb[1], cur(p)[1]) > 0.5 * min(rb[4] - rb[1], cur(p)[4] - cur(p)[1])]
        if under:
            drop = rb[2] - max(b[5] for b in under)
            if REST_TOUCH_M < drop <= REST_GAP_MAX_M:
                move(r, 2, -drop)
                item["lowered_m"] = round(drop, 4)
        g2 = _rest_gap(cur(r), verts_of(r), cur(s), verts_of(s))
        left = max(0.0, g2["gap"]) if g2 is not None else 0.0
        item["gap_after_m"] = round(left, 4)
        after.append(left)
        items.append(item)
        beside.append(r)
    # the corner: two rests beside the seat across each other (an L's two backs, a back and an arm) meet; a back
    # cushion standing on the seat keeps its place in its row
    corner = []
    for i, a in enumerate(beside):
        for b in beside[i + 1:]:
            ba, bb = cur(a), cur(b)
            ka = 0 if ba[3] - ba[0] < ba[4] - ba[1] else 1
            kb = 0 if bb[3] - bb[0] < bb[4] - bb[1] else 1
            if ka == kb:
                continue
            gp = _gaps(ba, bb)
            if gp[2] > 0.0 or not (gp[0] > REST_TOUCH_M) ^ (gp[1] > REST_TOUCH_M):
                continue
            axis = 0 if gp[0] > REST_TOUCH_M else 1
            if gp[axis] > REST_GAP_MAX_M:
                continue
            slider = a if (1 - ka) == axis else b                 # the rest that runs along the gap slides
            other = b if slider == a else a
            sb, ob = cur(slider), cur(other)
            sign = 1.0 if ob[axis] >= sb[axis + 3] - 1e-9 else -1.0
            others = [cur(p) for p in boxes if p not in in_rests]
            d = _clip(sign * gp[axis], axis, [cur(p) for p in groups[slider]], others)
            if abs(d) > 1e-9:
                move(slider, axis, d)
            corner.append(round(max(0.0, _gaps(cur(a), cur(b))[axis]), 4))
    moved = sorted(r for r in rests if any(abs(c) > 1e-12 for c in shift.get(r, (0.0, 0.0, 0.0))))
    rec.update(moved=len(moved), max_gap_m=round(max(before, default=0.0), 4),
               max_gap_after_m=round(max(after, default=0.0), 4), items=items[:12])
    if corner:
        rec["corner_gap_after_m"] = max(corner)
    return {"shift": {p: tuple(t) for p, t in shift.items() if any(abs(c) > 1e-12 for c in t)}, "moved": moved,
            "record": rec}


def parts_rest_record(parts: Sequence[dict]) -> dict:
    """``rest_plan``'s record of a list of parametric parts (``{"verts", ...}``: each part one loose part), the
    same measure the build applies to a library model: the parametric and module soft seats are checked by it."""
    pts, vp = [], []
    for i, p in enumerate(parts):
        for v in p.get("verts") or []:
            pts.append(tuple(float(c) for c in v))
            vp.append(i)
    return rest_plan(pts, vp)["record"]


# --------------------------------------------------------------------------
# The check (model review M33, Argus U36)
# --------------------------------------------------------------------------

FIX = {"flat_fabric": "rerun_stage build (furniture._dress_fabric: the flat upholstery slots of a library soft seat "
                      "wear the style's fabric in the design's colour), else swap_model to a textured model",
       "parts_apart": "rerun_stage build (soft_seats.join_parts: the facing bodies of the model moved together), else "
                      "swap_model",
       "rest_apart": "rerun_stage build (soft_seats.rest_plan: every back, back cushion and arm slid against its seat "
                     "and down onto what is under it, the corner's backs meeting), else swap_model",
       "faceted": "rerun_stage build (the model's own normals: import_gltf_geometry normals, _mesh_object)",
       "poor_model": "swap_model to a better model of the type, else grow the library (a library gap: "
                     "soft_seats.grade)"}


def _asset(o: dict) -> dict:
    a = o.get("asset")
    return a if isinstance(a, dict) else {}


def review(manifest: Optional[dict], check: str = "M33") -> tuple[list[dict], int]:
    """``(findings, checked)``: every library soft seat of the scene as built (module docstring). Each finding:
    ``{check, severity, target, room_id, message, problem, lesson, fix, metrics}``."""
    out: list[dict] = []
    n = 0
    for o in (manifest or {}).get("objects") or []:
        if o.get("kind") != "furniture" or o.get("type") not in SOFT_SEAT_TYPES or o.get("method") != "library":
            continue
        n += 1
        pid, asset = o.get("wenart_id") or o.get("name"), _asset(o)
        aid = asset.get("asset_id")
        what = f"{pid} ({o.get('type')}, {aid})"

        def add(sev: str, problem: str, message: str, lesson: str, **metrics) -> None:
            out.append({"check": check, "severity": sev, "target": pid, "room_id": o.get("room_id"),
                        "message": message, "problem": problem, "lesson": lesson, "fix": FIX[problem],
                        "metrics": dict(metrics, asset_id=aid)})

        dressing = o.get("fabric_dressing") if isinstance(o.get("fabric_dressing"), dict) else {}
        if not o.get("textured") and not dressing.get("slots"):
            add("major", "flat_fabric", f"{what} renders in its flat export colours: no fabric weave, no sheen",
                "UL140", materials=list(o.get("materials") or [])[:8])
        parts = o.get("parts") if isinstance(o.get("parts"), dict) else (o.get("fit") or {}).get("parts")
        if isinstance(parts, dict):
            left = float(parts.get("max_gap_after_m", parts.get("max_gap_m")) or 0.0)
            if left > GAP_VISIBLE_M:
                add("major", "parts_apart", f"{what}: its parts stand {left * 100:.1f} cm apart (over "
                    f"{GAP_VISIBLE_M * 100:.0f} cm)", "UL140", gap_m=round(left, 4), parts=parts.get("parts"))
            # 30 Oct 2026 (UL167): its backs, back cushions and arms against the seat, its corner's backs meeting
            rests = parts.get("rests") if isinstance(parts.get("rests"), dict) else {}
            rest_left = max(float(rests.get("max_gap_after_m") or 0.0), float(rests.get("corner_gap_after_m") or 0.0))
            if rest_left > REST_TOUCH_M:
                add("major", "rest_apart", f"{what}: a back or an arm stands {rest_left * 100:.1f} cm from its seat "
                    f"or its corner (over {REST_TOUCH_M * 1000:.0f} mm): the rests look apart from the sitting",
                    "UL167", gap_m=round(rest_left, 4), rests=rests.get("rests"))
        shading = o.get("shading") if isinstance(o.get("shading"), dict) else {}
        if shading.get("file_smooth") and not shading.get("smooth"):
            add("major", "faceted", f"{what}: the file's {shading['file_smooth']} smooth faces render flat (faceted "
                "cushions)", "UL131", file_smooth=shading.get("file_smooth"))
        g = asset.get("upholstery") if isinstance(asset.get("upholstery"), dict) else (grade(asset) if asset else None)
        if g and g.get("grade") == "poor":
            add("minor", "poor_model", f"{what} is a poor model ({'; '.join(g.get('reasons') or [])}): the best "
                "that fitted, a library gap", "UL131", points=g.get("points"))
    return out, n
