"""The photo-card check (1 Nov 2026, lesson UL237; user on real04 run 20261031-194116-full, a library coffee table
rendered as a product photo printed on a standing board: "This is only a photo if that's the case don't use this
model ever again").

What: a library model whose visible surface is mostly one or two flat, thin panels carrying an image (a product photo
on a board, often with its white or grey photo background, sometimes on a small stand, or a photo panel hung behind a
lamp) is a photo card, not a 3D object: it is never used. Three ways find it, all code:

- ``analyse(verts, tris, tri_textured, tri_uv)`` (the mesh check, numpy only): the planes of the mesh (area-weighted
  bins of the triangle normals and offsets), each plane's slab of ``THICK_M`` (every triangle with its three corners
  within 2 cm of the plane), and per panel its visible area (the larger of its two faces), its thickness, its size
  and fill (visible area over its own rectangle), its share of the model's box face, the parallel faces right behind
  it (``backing_share``: a board thicker than 2 cm is the face of a solid, no card), its image share (triangles whose
  material has a base colour image) and the image's span on it (``uv_span``; ``once_mapped``: one image stretched once
  over the panel, a photo, not a tiled material). ``verdict(stats, kind, type)``: a card when one or two vertical, thin,
  filled, image-carrying panels hold ``CARD_SHARE`` of the surface a viewer sees (``share``: the panels' visible area
  over itself plus half the rest of the surface), or the front view (``front_share``) with the image mapped once.
  It runs where the model files are: inside the audit render (``blender_audit.py`` loads this file by path, like
  ``meshstats.py``: ``measure["photo_card"]``) and in the pod scan of the library files (``scan``, glTF read with
  ``glbmesh.textured_arrays``: no Blender, no GPU work).
- ``cpu_rule(measure, kind, type)`` (the CPU rule, from the audit's committed measurements ``results/library/audit/
  <batch>/measure.json``, ``meshstats.analyse``): ``full_face``: the main part's area equals one vertical face of the
  model box within ``FULL_FACE_TOL`` (one flat sheet spanning the whole box) and every other part sticks out only
  along that face's normal (the object or stand in front of or behind the sheet); ``thin_panel``: a box thin in one
  horizontal direction (``THIN_SHARE`` of its width and height) whose main part holds ``MAIN_SHARE_MIN`` of the area
  as one sheet (``PANEL_ONE``) or a two-sided one (``PANEL_TWO``) of its wide face. Both need an image texture.
- The store ``results/library/photo_cards.json`` (``wenart.furniture.photo_cards``, read by ``catalog.usable`` and
  ``catalog.unusable_reason``): ``python -m wenart.assets.audit.photocard cpu`` writes the CPU rule's cards from the
  committed measurements, ``scan`` (pod) measures every model file, ``merge`` puts the scan into the store (a mesh
  verdict adds a card; a CPU card the mesh check finds no photo panel on is kept with the mesh numbers for review,
  ``--clear-cpu`` clears it).

Flat by nature (``ART_TYPES``: wall art, posters, mirrors, rugs, curtains, blinds, clocks, screens) are never cards;
flat by build (``STRUCTURE_TYPES``: doors, windows, fences, gates, railings, shower screens) are cards only on the
mesh check's photo evidence (the image stretched once over the panel) or the CPU rule's full-face sheet, never on the
thin-panel rule (a real door or sliding panel is a thin box).

Why: the audit measured the mesh (``meshstats``: parts, main part, parts outside the main body) and the vision check
saw the model, but nothing asked whether the "object" is a picture of one; the ranking sheets of 31 Oct 2026 show more
(pendant lights with photo panels behind or instead of the lamp, a stool, a pouf, vases, a sideboard, plants).

How: pure numpy at the module level (Blender loads this file by path; the CLI imports ``wenart`` inside its
functions); deterministic; every record keeps its measured numbers. Nothing is deleted: a card only leaves the
catalogue's use (the files stay on the volume).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np

VERSION = "ul237.1"
LESSON = "UL237"
USER_WORDS = "This is only a photo if that's the case don't use this model ever again"
REASON = "a photo card, not a 3D object (UL237)"
CHECK = "photo_card"
_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parents[3] if len(_HERE.parents) > 3 else _HERE.parent   # record paths are relative to it

# flat by nature: the image IS the product (never a card); bare decor names and catalogue types both
ART_TYPES: tuple[str, ...] = ("wall_art", "mirror", "rug", "curtain", "blind", "clock", "tv", "monitor",
                              "decor_wall_art", "decor_mirror", "decor_rug", "decor_curtain", "decor_blind",
                              "decor_clock")
# flat by build: a card only when the mesh check sees one image stretched once over the panel (a photo of one)
STRUCTURE_TYPES: tuple[str, ...] = ("door", "window", "fence", "gate", "railing", "shower")

# mesh check
THICK_M = 0.02            # a panel: every corner within 2 cm of its plane (the user's "thickness under ~2 cm")
BACKING_M = 0.30          # parallel faces up to 30 cm behind a panel make it the face of a solid (a closed box
                          # deeper than that shows under CARD_SHARE of its surface on one face)
BACKING_MAX = 0.5         # ... when they cover half of its visible area
VERTICAL_NZ = 0.26        # a standing panel: its normal within 15 degrees of horizontal
TEXTURED_MIN = 0.5        # half of the panel's faces carry a base colour image
FILL_MIN = 0.6            # a filled rectangle (a ring, a lattice or a frame is no card)
EXTENT_MIN = 0.25         # the panel spans a quarter of the model's box face in its plane
CARD_SHARE = 0.6          # the panels hold 60 % of the surface a viewer sees
FRONT_SHARE = 0.8         # or 80 % of the front view with the image mapped once and 45 % of the surface
FRONT_SURFACE_MIN = 0.45
ONCE_MAPPED = (0.85, 1.15)  # one image stretched once: its span on the panel in u and v
NORMAL_BINS = 12
SEED_MIN_SHARE = 0.02     # a plane bin under 2 % of the surface seeds no panel (it cannot hold a card)
MAX_SEEDS = 12
MAX_PANELS = 6

# CPU rule (the audit's committed measurements)
FULL_FACE_TOL = 0.02      # the main part's area = one vertical box face within 2 %
THIN_SHARE = 0.15         # a box thinner than 15 % of its width and of its height
MAIN_SHARE_MIN = 0.75     # whose main part holds 75 % of the area
PANEL_ONE = (0.45, 1.05)  # as one sheet of its wide face (a lamp or a stand may widen the box)
PANEL_TWO = (1.9, 2.15)   # or a two-sided one


def _bare(ftype: Optional[str]) -> str:
    return str(ftype or "")


def flat_by_nature(ftype: Optional[str]) -> bool:
    return _bare(ftype) in ART_TYPES


def flat_by_build(ftype: Optional[str]) -> bool:
    return _bare(ftype) in STRUCTURE_TYPES


# --------------------------------------------------------------------------
# Mesh check
# --------------------------------------------------------------------------

def _basis(n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    ref = np.array([0.0, 0.0, 1.0]) if abs(n[2]) < 0.99 else np.array([1.0, 0.0, 0.0])
    u = np.cross(n, ref)
    u /= np.linalg.norm(u)
    return u, np.cross(n, u)


def _r(v, nd: int = 4):
    return round(float(v), nd) + 0.0


def analyse(verts, tris, tri_textured=None, tri_uv=None, *, thick_m: float = THICK_M) -> dict:
    """The panels of a mesh and the shares they hold (module docstring). ``verts`` (N, 3) metres, Z up; ``tris``
    (M, 3); ``tri_textured`` (M,) bool: the triangle's material has a base colour image (None: none known);
    ``tri_uv`` (M, 3, 2) that image's coordinates (NaN where unknown). JSON-ready; ``verdict`` decides."""
    verts = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    tris = np.asarray(tris, dtype=np.int64).reshape(-1, 3)
    out: dict = {"version": VERSION, "faces": int(len(tris)), "panels": []}
    if len(verts) == 0 or len(tris) == 0:
        out.update(ok=False, error="no geometry")
        return out
    textured = (np.zeros(len(tris), dtype=bool) if tri_textured is None
                else np.asarray(tri_textured, dtype=bool).reshape(-1))
    uv = None if tri_uv is None else np.asarray(tri_uv, dtype=np.float64).reshape(-1, 3, 2)
    p0, p1, p2 = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    cross = np.cross(p1 - p0, p2 - p0)
    length = np.linalg.norm(cross, axis=1)
    area = 0.5 * length
    valid = area > 1e-12
    normal = np.divide(cross, length[:, None], out=np.zeros_like(cross), where=length[:, None] > 0)
    centroid = (p0 + p1 + p2) / 3.0
    total = float(area[valid].sum())
    out["area_m2"] = _r(total)
    if total <= 0:
        out.update(ok=False, error="no surface")
        return out
    # seeds: the area-weighted bins of the canonical normal and the plane offset
    canon = normal.copy()
    big = np.argmax(np.abs(canon), axis=1)
    flip = canon[np.arange(len(canon)), big] < 0
    canon[flip] *= -1.0
    offset = np.einsum("ij,ij->i", canon, centroid)
    nb = np.round(canon[valid] * NORMAL_BINS).astype(np.int64) + NORMAL_BINS       # 0 .. 2 * NORMAL_BINS
    ob = np.round(offset[valid] / thick_m).astype(np.int64)
    ob -= ob.min() if len(ob) else 0
    side = 2 * NORMAL_BINS + 1
    keys = ((nb[:, 0] * side + nb[:, 1]) * side + nb[:, 2]) * (int(ob.max(initial=0)) + 1) + ob
    vidx = np.nonzero(valid)[0]
    uniq, inverse = np.unique(keys, return_inverse=True)
    inverse = inverse.reshape(-1)
    bin_area = np.bincount(inverse, weights=area[vidx], minlength=len(uniq))
    order = np.argsort(-bin_area, kind="stable")[:MAX_SEEDS]
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    out["box_m"] = [_r(b - a) for a, b in zip(lo, hi)]
    assigned = ~valid
    panels: list[dict] = []
    corners: list[tuple] = []          # per panel: its plane and its vertices (the crossing test of a pair)
    seeds: list[tuple[np.ndarray, float]] = []
    for b in order.tolist():
        if len(panels) >= MAX_PANELS or bin_area[b] < SEED_MIN_SHARE * total:
            break                                       # the bins are sorted: no panel of weight is left
        members = vidx[inverse == b]
        w = area[members]
        n = (canon[members] * w[:, None]).sum(axis=0)
        if np.linalg.norm(n) <= 0:
            continue
        n /= np.linalg.norm(n)
        d0 = float((offset[members] * w).sum() / w.sum())
        if any(abs(float(n @ sn)) > 0.98 and abs(d0 - sd) < thick_m for sn, sd in seeds):
            continue
        seeds.append((n, d0))
        dist = verts @ n - d0
        tri_d = dist[tris]
        inside = np.all(np.abs(tri_d) <= thick_m, axis=1) & ~assigned
        if not inside.any():
            continue
        dots = normal @ n
        front = inside & (dots > 0.9)
        back = inside & (dots < -0.9)
        a_front, a_back = float(area[front].sum()), float(area[back].sum())
        vis = max(a_front, a_back)
        if vis <= 1e-9:
            continue
        assigned |= inside
        used = np.unique(tris[inside])
        u_ax, v_ax = _basis(n)
        pu, pv = verts[used] @ u_ax, verts[used] @ v_ax
        width, height = float(pu.max() - pu.min()), float(pv.max() - pv.min())
        rect = width * height
        au, av = verts @ u_ax, verts @ v_ax
        model_face = float((au.max() - au.min()) * (av.max() - av.min()))
        thickness = float(tri_d[inside].max() - tri_d[inside].min())
        cu, cv, cd = centroid @ u_ax, centroid @ v_ax, centroid @ n - d0
        behind = (~inside & valid & (np.abs(dots) > 0.9) & (np.abs(cd) > thick_m) & (np.abs(cd) <= BACKING_M)
                  & (cu >= pu.min()) & (cu <= pu.max()) & (cv >= pv.min()) & (cv <= pv.max()))
        facing = front | back
        a_facing = float(area[facing].sum())
        tex_share = float(area[facing & textured].sum() / a_facing) if a_facing > 0 else 0.0
        span, once = None, False
        if uv is not None:
            sel = facing & textured
            pts = uv[sel].reshape(-1, 2) if sel.any() else np.zeros((0, 2))
            pts = pts[np.all(np.isfinite(pts), axis=1)]
            if len(pts):
                span = [_r(pts[:, 0].max() - pts[:, 0].min(), 3), _r(pts[:, 1].max() - pts[:, 1].min(), 3)]
                once = all(ONCE_MAPPED[0] <= s <= ONCE_MAPPED[1] for s in span)
        rest_proj = 0.5 * float((np.abs(dots[~inside & valid]) * area[~inside & valid]).sum())
        panels.append({
            "normal": [_r(v, 3) for v in n], "vertical": bool(abs(n[2]) <= VERTICAL_NZ),
            "visible_m2": _r(vis), "area_m2": _r(area[inside].sum()), "triangles": int(inside.sum()),
            "two_sided": bool(min(a_front, a_back) >= 0.5 * vis),
            "thickness_m": _r(thickness), "size_m": [_r(width, 3), _r(height, 3)],
            "fill": _r(vis / rect, 3) if rect > 0 else 0.0,
            "extent_share": _r(rect / model_face, 3) if model_face > 0 else 0.0,
            "backing_share": _r(float(area[behind].sum()) / vis, 3),
            "textured_share": _r(tex_share, 3), "uv_span": span, "once_mapped": bool(once),
            "front_share": _r(vis / (vis + rest_proj), 3)})
        corners.append((n, d0, verts[used]))
    for p, c in zip(panels, corners):
        p["_corners"] = c
    for p in panels:
        p["share"] = _r(p["visible_m2"] / (p["visible_m2"] + max(total - p["area_m2"], 0.0) / 2.0), 3)
        p["thin"] = bool(p["thickness_m"] <= thick_m + 1e-9 and p["backing_share"] < BACKING_MAX)
        p["qualifies"] = bool(p["vertical"] and p["thin"] and p["fill"] >= FILL_MIN
                              and p["textured_share"] >= TEXTURED_MIN)
    panels.sort(key=lambda p: -p["visible_m2"])
    out["panels"] = panels
    good = [p for p in panels if p["qualifies"]]
    out["share_one"] = good[0]["share"] if good else 0.0
    # the second panel of a pair crosses the first (crossed cards: each plane cuts the other panel); a parallel one or
    # one meeting it at an edge is the next face of a solid (a closed box's front, side and back) or a second photo,
    # which the first panel's own share already counts
    second = [p for p in good[1:] if _crossing(good[0]["_corners"], p["_corners"])] if good else []
    if second:
        a, b = good[0], second[0]
        rest = max(total - a["area_m2"] - b["area_m2"], 0.0)
        vis2 = a["visible_m2"] + b["visible_m2"]
        out["share_two"] = _r(vis2 / (vis2 + rest / 2.0), 3)
    else:
        out["share_two"] = out["share_one"]
    for p in panels:
        p.pop("_corners", None)
    out["ok"] = True
    return out


def _cuts(plane: tuple, pts: np.ndarray, share: float = 0.2) -> bool:
    """The plane ``(n, d)`` cuts the point set with at least ``share`` of its depth on either side."""
    n, d0 = plane
    dist = pts @ n - d0
    span = float(dist.max() - dist.min())
    return span > 0 and float(dist.min()) < -share * span and float(dist.max()) > share * span


def _crossing(a: tuple, b: tuple) -> bool:
    """Two panels that cross like an X (each one's plane cuts the other; not parallel)."""
    if abs(float(np.dot(a[0], b[0]))) > 0.98:
        return False
    return _cuts((a[0], a[1]), b[2]) and _cuts((b[0], b[1]), a[2])


def verdict(stats: Optional[dict], kind: Optional[str] = None, ftype: Optional[str] = None) -> tuple[bool, str]:
    """``(card, why)`` of ``analyse``'s numbers for a model of ``ftype`` (module docstring)."""
    if not stats or not stats.get("ok"):
        return False, f"not measured ({(stats or {}).get('error') or 'no numbers'})"
    if flat_by_nature(ftype):
        return False, f"a {_bare(ftype).replace('decor_', '').replace('_', ' ')} is flat by nature"
    good = [p for p in stats.get("panels") or [] if p.get("qualifies")]
    if not good:
        return False, "no standing, thin, filled panel with an image"
    p = good[0]
    if p["extent_share"] < EXTENT_MIN:
        return False, f"the largest image panel spans {p['extent_share']:.0%} of the model's face"
    if flat_by_build(ftype) and not p["once_mapped"]:
        return False, (f"a {_bare(ftype)} is flat by build and its panel carries no photo (the image is not stretched "
                       "once over it)")
    one, two = float(stats.get("share_one") or 0), float(stats.get("share_two") or 0)
    nums = (f"a {p['size_m'][0]:.2f} x {p['size_m'][1]:.2f} m panel, {p['thickness_m'] * 100:.1f} cm thick, "
            f"{p['textured_share']:.0%} image")
    if one >= CARD_SHARE:
        return True, f"{nums}, holds {one:.0%} of the visible surface"
    if two >= CARD_SHARE:
        return True, f"two image panels hold {two:.0%} of the visible surface ({nums})"
    if p["front_share"] >= FRONT_SHARE and one >= FRONT_SURFACE_MIN and p["once_mapped"]:
        return True, (f"{nums}, one image stretched once over it, holds {p['front_share']:.0%} of the front view "
                      f"and {one:.0%} of the surface")
    return False, f"the image panels hold {max(one, two):.0%} of the visible surface (< {CARD_SHARE:.0%})"


# --------------------------------------------------------------------------
# CPU rule (the audit's committed measurements)
# --------------------------------------------------------------------------

def cpu_rule(measure: Optional[dict], kind: Optional[str] = None, ftype: Optional[str] = None,
             scale: float = 1.0) -> Optional[dict]:
    """The CPU rule's card record (``rule``, ``reason``, ``metrics``) of one audit measurement
    (``meshstats.analyse`` plus the render's texture count), None when it finds none (module docstring). Flat by
    nature (``ART_TYPES``): never; flat by build (``STRUCTURE_TYPES``): the full-face sheet only (a real door, barn door
    or sliding panel is a thin box: ``thin_panel`` would take it). ``scale``: the catalogue's size over the measured
    one (an audit fix rescaled the model after its render): the sizes in the record are the catalogue's, the shares
    do not change."""
    if not measure or not measure.get("ok") or flat_by_nature(ftype):
        return None
    images = int((measure.get("textures") or {}).get("images") or (measure.get("pbr") or {}).get("images") or 0)
    size, total, share = measure.get("size"), measure.get("area_m2"), measure.get("main_part_share")
    if images < 1 or not size or len(size) < 3 or not total or share is None:
        return None
    k = float(scale) if scale and scale > 0 else 1.0
    x, y, z = (float(v) * k for v in size[:3])
    total = float(total) * k * k
    main = total * float(share)
    sides = {s for p in measure.get("outside_parts") or [] for s in p.get("sides") or []}
    base = {"size_m": [_r(v, 3) for v in (x, y, z)], "area_m2": _r(total), "main_part_share": _r(share, 3),
            "main_part_m2": _r(main), "parts": measure.get("parts"), "images": images,
            "outside_sides": sorted(sides)}
    if k != 1.0:
        base["scale"] = _r(k)
    for face_name, face, axis in (("x-z", x * z, "y"), ("y-z", y * z, "x")):
        if face <= 0:
            continue
        ratio = main / face
        if abs(ratio - 1.0) <= FULL_FACE_TOL and all(s[1:] == axis for s in sides):
            w, h = (x, z) if axis == "y" else (y, z)
            where = (f", every other part only in front of or behind it ({', '.join(sorted(sides))})" if sides
                     else ", nothing else sticks out")
            return {"rule": "full_face", "metrics": dict(base, face=face_name, ratio=_r(ratio)),
                    "reason": (f"{REASON}: its main part is one flat {w:.2f} x {h:.2f} m sheet spanning the whole "
                               f"box face (area {ratio:.1%} of it){where}, with an image texture")}
    t, w = min(x, y), max(x, y)
    if flat_by_build(ftype):
        return None
    if w > 0 and z > 0 and t <= THIN_SHARE * min(w, z) and float(share) >= MAIN_SHARE_MIN:
        ratio = main / (w * z)
        one = PANEL_ONE[0] <= ratio <= PANEL_ONE[1]
        if one or PANEL_TWO[0] <= ratio <= PANEL_TWO[1]:
            return {"rule": "thin_panel", "metrics": dict(base, ratio=_r(ratio), thin_m=_r(t, 3)),
                    "reason": (f"{REASON}: a {w:.2f} x {t:.2f} x {z:.2f} m box whose main part ({share:.0%} of the "
                               f"area) is one {'one-sided' if one else 'two-sided'} sheet of its {w:.2f} x {z:.2f} m "
                               f"face (area {ratio:.0%} of it), with an image texture")}
    return None


# --------------------------------------------------------------------------
# Records and the store (CLI; wenart imported inside the functions)
# --------------------------------------------------------------------------

def mesh_record(item: dict, stats: dict) -> dict:
    """The store row of a mesh-check measurement of a catalogue item (``card`` true or false)."""
    card, why = verdict(stats, item.get("kind"), item.get("type"))
    panels = [{k: p[k] for k in ("size_m", "thickness_m", "visible_m2", "share", "front_share", "fill",
                                 "textured_share", "once_mapped", "uv_span", "vertical", "backing_share",
                                 "extent_share") if k in p} for p in (stats.get("panels") or [])[:2]]
    return {"id": item["id"], "type": item.get("catalog_type") or item.get("type"), "kind": item.get("kind"),
            "title": item.get("title") or "", "sha256_glb": item.get("sha256_glb"), "source": "mesh",
            "rule": "mesh_panel", "card": bool(card), "reason": f"{REASON}: {why}" if card else why,
            "metrics": {"share_one": stats.get("share_one"), "share_two": stats.get("share_two"),
                        "area_m2": stats.get("area_m2"), "box_m": stats.get("box_m"), "panels": panels,
                        "error": stats.get("error")}, "version": VERSION}


def cpu_record(item: dict, found: dict, measured_on: str) -> dict:
    return {"id": item["id"], "type": item.get("catalog_type") or item.get("type"), "kind": item.get("kind"),
            "title": item.get("title") or "", "sha256_glb": item.get("sha256_glb"), "source": "cpu",
            "rule": found["rule"], "card": True, "reason": found["reason"], "metrics": found["metrics"],
            "measured_on": measured_on, "version": VERSION}


def load_measures(paths: list) -> dict:
    """``{id: (measure, file)}`` of the audit's measurement files, a later file winning (the newer batch)."""
    import json
    out: dict = {}
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        doc = json.loads(p.read_text(encoding="utf-8"))
        try:
            name = p.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            name = str(p)
        for iid, m in (doc.get("measures") or {}).items():
            if isinstance(m, dict) and m.get("ok"):
                out[iid] = (m, name)
    return out


def catalogue_scale(item: dict, measure: dict) -> float:
    """The catalogue's box over the measured box (the cube root of the volumes; 1 when either is missing or flat)."""
    box, size = item.get("bbox_m"), measure.get("size")
    try:
        a = float(np.prod([float(v) for v in box[:3]]))
        b = float(np.prod([float(v) for v in size[:3]]))
    except (TypeError, ValueError, IndexError):
        return 1.0
    return float((a / b) ** (1.0 / 3.0)) if a > 0 and b > 0 else 1.0


def default_measure_files() -> list:
    from wenart.assets.audit import DEFAULT_OUT
    return sorted((DEFAULT_OUT / "audit").glob("*/measure.json"),
                  key=lambda p: ({"p2": 0, "p4": 1}.get(p.parent.name, 2), p.parent.name))


def empty_store() -> dict:
    return {"schema_version": 1, "kind": "photo_cards", "lesson": LESSON, "version": VERSION, "user": USER_WORDS,
            "what": ("library models that are only a photo or picture card (a flat board or a few flat quads carrying "
                     "an image, often with a photo background, sometimes on a small stand, or a photo panel behind "
                     "the object), found by code: never used on any project, in any licence mode (catalog.usable, "
                     "catalog.unusable_reason; wenart.assets.audit.photocard). 'cards' are used by nothing; 'cleared' "
                     "are CPU flags the mesh check found no photo panel on. Wall art, posters, mirrors, rugs, "
                     "curtains, blinds, clocks and screens are flat by nature and never cards."),
            "cards": {}, "cleared": {}}


def cpu_cards(items: list, measures: dict) -> dict:
    """``{id: record}`` of the CPU rule over the catalogue items with a committed measurement."""
    out = {}
    for it in items:
        got = measures.get(it["id"])
        if not got:
            continue
        found = cpu_rule(got[0], it.get("kind"), it.get("type"), catalogue_scale(it, got[0]))
        if found:
            out[it["id"]] = cpu_record(it, found, got[1])
    return out


def update_store(store: Optional[dict], cpu: Optional[dict] = None, mesh: Optional[list] = None,
                 current_sha: Optional[dict] = None, date: str = "", clear_cpu: bool = False) -> dict:
    """The new store: ``cpu`` (``{id: cpu record}``) replaces the CPU rows (a mesh row is never replaced by a CPU
    one, and a CPU flag the mesh check cleared stays cleared); ``mesh`` (records of ``scan``) of the catalogue's
    current file (``current_sha``: ``{id: sha256_glb}``; a scan of another file is skipped) add cards and clear an
    earlier mesh card it no longer finds. A CPU card the mesh check finds no card on keeps its card and records the
    mesh numbers (``mesh_check``) for review (the CPU cards were checked on the ranking sheets; a reader of the GLB
    that misses an image must not let a known photo back in); ``clear_cpu`` clears it instead."""
    import copy
    doc = copy.deepcopy(store) if store else empty_store()
    base = empty_store()
    for k in ("schema_version", "kind", "lesson", "version", "user", "what"):
        doc[k] = base[k]
    cards = dict(doc.get("cards") or {})
    cleared = dict(doc.get("cleared") or {})
    if cpu is not None:
        cards = {k: v for k, v in cards.items() if v.get("source") != "cpu"}
        for iid, r in cpu.items():
            if iid in cards or (iid in cleared and cleared[iid].get("source") == "mesh"):
                continue
            cards[iid] = dict(r, date=r.get("date") or date)
    for r in mesh or []:
        if not isinstance(r, dict) or not r.get("id"):
            continue
        iid = r["id"]
        if current_sha is not None and iid in current_sha and current_sha[iid] != r.get("sha256_glb"):
            continue                                    # measured on another file: the current one needs a new look
        if r.get("card"):
            cards[iid] = dict(r, date=r.get("date") or date)
            cleared.pop(iid, None)
        elif iid in cards and (cards[iid].get("source") == "mesh" or clear_cpu):
            was = cards.pop(iid)
            cleared[iid] = dict(r, date=r.get("date") or date, was=was.get("reason"))
        elif iid in cards:
            cards[iid] = dict(cards[iid], mesh_check={"card": False, "reason": r.get("reason"),
                                                       "metrics": r.get("metrics"), "version": r.get("version")})
    doc["cards"] = dict(sorted(cards.items()))
    doc["cleared"] = dict(sorted(cleared.items()))
    return doc


def summary(store: dict, items: Optional[list] = None) -> list[str]:
    from collections import Counter
    cards = store.get("cards") or {}
    by = Counter(str(r.get("type")) for r in cards.values())
    rules = Counter(f"{r.get('source')}:{r.get('rule')}" for r in cards.values())
    disputed = [k for k, r in cards.items() if (r.get("mesh_check") or {}).get("card") is False]
    lines = [f"photo cards: {len(cards)} ({', '.join(f'{k} {v}' for k, v in sorted(rules.items()))}); "
             f"cleared by the mesh check: {len(store.get('cleared') or {})}; CPU cards the mesh check does not "
             f"confirm (kept, review): {len(disputed)}"]
    lines += [f"  review: {k} {cards[k].get('type')} ({(cards[k].get('mesh_check') or {}).get('reason')})"
              for k in disputed[:40]]
    lines += [f"  {t}: {n}" for t, n in sorted(by.items(), key=lambda kv: (-kv[1], kv[0]))]
    return lines


def _scan_one(job: dict) -> dict:
    """One model file of ``scan`` (a worker process): its mesh-check record, or the error."""
    from wenart.assets.audit import glbmesh as GM
    try:
        doc, buffers = GM.read(job["file"])
        verts, tris, tex, uv = GM.textured_arrays(doc, buffers)
        stats = analyse(verts * float(job.get("unit_scale") or 1.0), tris, tex, uv)
    except Exception as exc:  # noqa: BLE001 - one broken file must not stop the scan
        stats = {"version": VERSION, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return mesh_record(job["item"], stats)


def scan_jobs(items: list, assets) -> tuple[list, list]:
    """``(jobs, missing)``: a job per catalogue item whose model file is in ``assets``."""
    from wenart.assets.audit.items import model_file
    jobs, missing = [], []
    for it in items:
        rel = model_file(it)
        path = Path(assets) / rel if rel else None
        if path is None or not path.is_file():
            missing.append(it["id"])
            continue
        jobs.append({"file": str(path), "unit_scale": it.get("unit_scale", 1.0),
                     "item": {k: it.get(k) for k in ("id", "type", "catalog_type", "kind", "title", "sha256_glb")}})
    return jobs, missing


def _write_json(path, data) -> None:
    import json
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def scan(items: list, assets, out, workers: int = 4, deadline: Optional[float] = None, log=print) -> dict:
    """The pod scan: the mesh check of every model file (resumable: a model whose record of the same file and version
    is in ``out`` is not read again). Writes ``out`` (``{"kind": "photo_card_mesh", "records": [...]}``) every 100
    models and at the end."""
    import json
    import time
    out = Path(out)
    done: dict = {}
    if out.is_file():
        for r in json.loads(out.read_text(encoding="utf-8")).get("records") or []:
            if isinstance(r, dict) and r.get("id") and r.get("version") == VERSION:
                done[r["id"]] = r
    jobs, missing = scan_jobs(items, assets)
    todo = [j for j in jobs if not (j["item"]["id"] in done
                                    and done[j["item"]["id"]].get("sha256_glb") == j["item"].get("sha256_glb"))]
    log(f"photo-card scan: {len(jobs)} model file(s), {len(todo)} to read, {len(missing)} missing, workers {workers}")
    t0, left = time.time(), 0

    def flush(final: bool = False):
        recs = sorted(done.values(), key=lambda r: r["id"])
        _write_json(out, {"kind": "photo_card_mesh", "version": VERSION, "lesson": LESSON, "assets": str(assets),
                          "missing": missing, "left": left if final else None, "records": recs})

    if workers > 1 and len(todo) > 1:
        import multiprocessing as mp
        with mp.get_context("spawn").Pool(workers) as pool:
            for k, rec in enumerate(pool.imap_unordered(_scan_one, todo, chunksize=4), 1):
                done[rec["id"]] = rec
                if k % 100 == 0:
                    flush()
                    log(f"photo-card scan: {k}/{len(todo)} in {time.time() - t0:.0f} s")
                if deadline and time.time() >= deadline:
                    left = len(todo) - k
                    pool.terminate()
                    break
    else:
        for k, job in enumerate(todo, 1):
            if deadline and time.time() >= deadline:
                left = len(todo) - k + 1
                break
            rec = _scan_one(job)
            done[rec["id"]] = rec
            if k % 100 == 0:
                flush()
    flush(final=True)
    recs = list(done.values())
    cards = [r for r in recs if r.get("card")]
    log(f"photo-card scan: {len(recs)} record(s), {len(cards)} card(s), "
        f"{sum(1 for r in recs if (r.get('metrics') or {}).get('error'))} unreadable, {left} left, "
        f"{time.time() - t0:.0f} s")
    return {"records": len(recs), "cards": len(cards), "missing": len(missing), "left": left}


def main(argv: Optional[list] = None) -> int:
    """``python -m wenart.assets.audit.photocard cpu | scan | merge | show`` (module docstring)."""
    import argparse
    import datetime
    import json
    from wenart.assets.audit import items as IT
    from wenart.furniture import photo_cards as PC
    ap = argparse.ArgumentParser(prog="python -m wenart.assets.audit.photocard")
    ap.add_argument("action", choices=("cpu", "scan", "merge", "show"))
    ap.add_argument("--store", default=str(PC.PHOTO_CARDS_PATH), help="the committed store (photo_cards.json)")
    ap.add_argument("--measures", nargs="*", help="cpu: the audit's measure.json files (default every committed one)")
    ap.add_argument("--assets", help="scan: the assets folder holding the model files (/workspace/assets)")
    ap.add_argument("--out", help="scan: the mesh records file to write")
    ap.add_argument("--mesh", nargs="*", help="merge: mesh records files of the scan")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--deadline", type=float, default=None, help="scan: epoch seconds")
    ap.add_argument("--ids", nargs="*", help="scan: only these model ids")
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--dry", action="store_true", help="cpu / merge: print, write nothing")
    ap.add_argument("--clear-cpu", action="store_true",
                    help="merge: a CPU card the mesh check finds no card on is cleared (default: kept, for review)")
    a = ap.parse_args(argv)
    store_path = Path(a.store)
    store = json.loads(store_path.read_text(encoding="utf-8")) if store_path.is_file() else None
    items = IT.load_items()
    if a.ids:
        wanted = set(a.ids)
        items = [i for i in items if i["id"] in wanted]
    if a.action == "scan":
        if not a.assets or not a.out:
            ap.error("scan needs --assets and --out")
        res = scan(items, a.assets, a.out, a.workers, a.deadline)
        return 0 if res["records"] else 1
    if a.action == "cpu":
        files = [Path(p) for p in a.measures] if a.measures else default_measure_files()
        cpu = cpu_cards(items, load_measures(files))
        doc = update_store(store, cpu=cpu, date=a.date)
    elif a.action == "merge":
        recs: list = []
        for p in a.mesh or []:
            recs += json.loads(Path(p).read_text(encoding="utf-8")).get("records") or []
        doc = update_store(store, mesh=recs, current_sha={i["id"]: i.get("sha256_glb") for i in items}, date=a.date,
                           clear_cpu=a.clear_cpu)
    else:
        doc = store or empty_store()
    for line in summary(doc, items):
        print(line)
    if a.action in ("cpu", "merge") and not a.dry:
        _write_json(store_path, doc)
        PC.reset()
        print(f"written {store_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
