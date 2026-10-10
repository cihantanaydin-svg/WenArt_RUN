"""Mesh measurements of one model (docs/milestone12.md §6.1 code checks): faces, zero-area faces, open and non-manifold
edges, flipped normals, loose parts and parts outside the main body (an open drawer), the box and the pivot.

What: ``analyse(verts, tris)`` -> a JSON-ready dict. ``verts`` (N, 3) in metres in the piece frame (the scene
builder's frame: front -Y, floor z = 0, footprint centre at the origin), ``tris`` (M, 3) vertex indices.

Why: the decor ray casts and the renders need clean meshes; the diagnosis (§1.6) lists mesh faults as "not checked".

How: numpy only, so the same file runs inside Blender (``blender_audit.py`` loads it by path, Blender ships numpy) and
in the CPU tests. Vertices closer than ``merge_eps`` are merged first (glTF splits vertices at UV seams). Edges are
counted with ``np.unique``; a manifold edge whose two faces run it in the same direction has an inconsistent winding
(one of the two faces is flipped). Loose parts are the connected components (union-find over the merged vertices);
the main body is the part with the largest area, and a part whose box sticks out of the main body's box by more than
``outside_m`` is listed (an open drawer, a separate prop). Deterministic.
"""
from __future__ import annotations

import numpy as np


def _merge(verts: np.ndarray, eps: float) -> np.ndarray:
    """Index of the merged vertex of every vertex (positions quantised to ``eps``)."""
    if len(verts) == 0:
        return np.zeros(0, dtype=np.int64)
    q = np.round(verts / max(eps, 1e-12)).astype(np.int64)
    _, inverse = np.unique(q, axis=0, return_inverse=True)
    return inverse.reshape(-1).astype(np.int64)


def _components(n: int, edges: np.ndarray) -> np.ndarray:
    """Component label (0..k-1, by first vertex) of each of ``n`` vertices joined by ``edges`` (E, 2)."""
    parent = np.arange(n, dtype=np.int64)
    # Vectorised label propagation (min label over edges), then a Python union-find pass for what is left: both are
    # deterministic. Propagation converges fast on compact meshes; the fallback bounds the work on long thin ones.
    a, b = edges[:, 0], edges[:, 1]
    for _ in range(64):
        m = np.minimum(parent[a], parent[b])
        changed = False
        for idx in (a, b):
            cur = parent[idx]
            upd = m < cur
            if upd.any():
                np.minimum.at(parent, idx[upd], m[upd])
                changed = True
        parent = parent[parent]
        if not changed:
            break
    else:
        p = parent.tolist()

        def find(x):
            while p[x] != x:
                p[x] = p[p[x]]
                x = p[x]
            return x
        for u, v in zip(a.tolist(), b.tolist()):
            ru, rv = find(u), find(v)
            if ru != rv:
                if ru < rv:
                    p[rv] = ru
                else:
                    p[ru] = rv
        parent = np.array([find(i) for i in range(n)], dtype=np.int64)
    _, labels = np.unique(parent, return_inverse=True)
    return labels.reshape(-1)


def analyse(verts, tris, *, merge_eps: float = 1e-5, outside_m: float = 0.05, outside_share: float = 0.005,
            zero_area_m2: float = 1e-10) -> dict:
    verts = np.asarray(verts, dtype=np.float64).reshape(-1, 3)
    tris = np.asarray(tris, dtype=np.int64).reshape(-1, 3)
    out = {"vertices": int(len(verts)), "faces": int(len(tris))}
    if len(verts) == 0 or len(tris) == 0:
        out.update(ok=False, error="no geometry")
        return out
    lo, hi = verts.min(axis=0), verts.max(axis=0)
    out["box_min"] = [round(float(v), 4) for v in lo]
    out["box_max"] = [round(float(v), 4) for v in hi]
    out["size"] = [round(float(b - a), 4) for a, b in zip(lo, hi)]
    out["pivot_offset"] = [round(float((lo[0] + hi[0]) / 2), 4), round(float((lo[1] + hi[1]) / 2), 4),
                           round(float(lo[2]), 4)]
    p0, p1, p2 = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    cross = np.cross(p1 - p0, p2 - p0)
    area = 0.5 * np.linalg.norm(cross, axis=1)
    total = float(area.sum())
    out["area_m2"] = round(total, 4)
    zero = area < zero_area_m2
    out["zero_area_faces"] = int(zero.sum())
    out["zero_area_share"] = round(float(zero.mean()), 4)
    m = _merge(verts, merge_eps)
    t = m[tris]
    good = ~zero & (t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])
    t = t[good]
    nv = int(m.max()) + 1
    out["merged_vertices"] = nv
    if len(t) == 0:
        out.update(ok=False, error="only degenerate faces")
        return out
    directed = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    lo_v, hi_v = directed.min(axis=1), directed.max(axis=1)
    key = lo_v * nv + hi_v
    uniq, inverse, counts = np.unique(key, return_inverse=True, return_counts=True)
    n_edges = len(uniq)
    boundary = int((counts == 1).sum())
    nonmanifold = int((counts > 2).sum())
    out["edges"] = n_edges
    out["boundary_edges"] = boundary
    out["boundary_share"] = round(boundary / n_edges, 4)
    out["nonmanifold_edges"] = nonmanifold
    out["nonmanifold_share"] = round(nonmanifold / n_edges, 4)
    # winding: on a manifold edge (2 faces) the two directed copies must run opposite ways
    forward = (directed[:, 0] == lo_v).astype(np.int64)
    fwd_count = np.bincount(inverse.reshape(-1), weights=forward, minlength=n_edges)
    manifold = counts == 2
    inconsistent = manifold & ((fwd_count == 2) | (fwd_count == 0))
    n_manifold = int(manifold.sum())
    out["inconsistent_edges"] = int(inconsistent.sum())
    out["flipped_share"] = round(int(inconsistent.sum()) / n_manifold, 4) if n_manifold else 0.0
    # loose parts
    edges = np.stack([uniq // nv, uniq % nv], axis=1)
    labels = _components(nv, edges)
    face_comp = labels[t[:, 0]]
    k = int(labels.max()) + 1
    used = np.unique(face_comp)
    out["parts"] = int(len(used))
    comp_area = np.bincount(face_comp, weights=area[good], minlength=k)
    main = int(np.argmax(comp_area))
    mv = verts[np.isin(m, np.nonzero(labels == main)[0])]
    mlo, mhi = mv.min(axis=0), mv.max(axis=0)
    out["main_part_share"] = round(float(comp_area[main] / total), 4) if total > 0 else 0.0
    outside = []
    # one pass over the merged vertices per component: their boxes
    merged_pos = np.zeros((nv, 3))
    merged_pos[m] = verts
    comp_lo = np.full((k, 3), np.inf)
    comp_hi = np.full((k, 3), -np.inf)
    np.minimum.at(comp_lo, labels, merged_pos)
    np.maximum.at(comp_hi, labels, merged_pos)
    for c in used.tolist():
        if c == main:
            continue
        share = float(comp_area[c] / total) if total > 0 else 0.0
        if share < outside_share:
            continue
        stick = max(float(np.max(mlo - comp_lo[c])), float(np.max(comp_hi[c] - mhi)), 0.0)
        if stick > outside_m:
            side = []
            for axis, name in enumerate("xyz"):
                if mlo[axis] - comp_lo[c][axis] > outside_m:
                    side.append("-" + name)
                if comp_hi[c][axis] - mhi[axis] > outside_m:
                    side.append("+" + name)
            outside.append({"share": round(share, 4), "sticks_out_m": round(stick, 3), "sides": side})
    outside.sort(key=lambda o: (-o["share"], -o["sticks_out_m"]))
    out["outside_parts"] = outside[:10]
    out["outside_share"] = round(sum(o["share"] for o in outside), 4)
    out["front_outside"] = any("-y" in o["sides"] for o in outside)
    out["ok"] = True
    return out
