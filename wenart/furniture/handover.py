"""The decor of a re-placed piece goes to its successor (29 Oct 2026).

What (pure, deterministic): when the solver takes a room's added pieces out and places the room again
(``solver.apply_candidate``: the agent's ``relayout_room``, ``place_group``, ``complete_group``; ``edit_ops``
``move_group``), the decor of each piece it took out goes to its successor (``successors``: the new piece of the same
type in the same room nearest to it, nearest pairs first, each new piece once): a hosted item takes the new host, an
anchored rug, picture or light the new anchors; the item records ``handed_over`` (from, to, the reason). The item's
``host_frame`` (its place as shares of its host, ``decor.host_frame_of``) is kept, so ``decor.sync_to_hosts`` sets it
on the new piece as it stood on the old one; an item without a frame is moved onto the new piece here, at the same
place of its top. Decor whose piece has no successor is left to the caller, which drops it as before.

Why: real06 run 20261028-154514-full (user: "Computer on the table would have been nice or a laptop", lesson UL93):
the agent's relayout of the child's room re-placed the desk f_L1_032 as f_L1_038 and the decor on it (a plant, books)
was dropped with its host, so the desk rendered bare. A module of its own: the solver and the edit ops run in the
reading's and the fit's stages, whose fingerprints must not take in the decor stage's code.
"""
from __future__ import annotations

from wenart import geometry as G


def successors(gone: list[dict], new: list[dict]) -> dict[str, str]:
    """``{gone id: new id}`` (module docstring): each gone piece matched to the nearest new piece of its type in its
    room, nearest pairs first, each new piece once; a gone piece with no such new piece has none."""
    pairs = []
    for g in gone:
        gc = (g.get("footprint") or {}).get("center")
        for n in new:
            nc = (n.get("footprint") or {}).get("center")
            if g.get("type") != n.get("type") or g.get("room_id") != n.get("room_id") or not gc or not nc:
                continue
            pairs.append((round(G.distance(tuple(gc[:2]), tuple(nc[:2])), 4), str(g["id"]), str(n["id"])))
    out: dict[str, str] = {}
    used: set = set()
    for _d, gid, nid in sorted(pairs):
        if gid not in out and nid not in used:
            out[gid] = nid
            used.add(nid)
    return out


def _onto(item: dict, old: dict, new: dict) -> None:
    """In place: an item without a host frame moved from ``old`` onto ``new`` at the same shares of its footprint and
    the same turn against it."""
    fo, fn = old["footprint"], new["footprint"]
    oc = (float(fo["center"][0]), float(fo["center"][1]))
    nc = (float(fn["center"][0]), float(fn["center"][1]))
    lx, ly = G.rotate_point((float(item["center"][0]), float(item["center"][1])), -float(fo["rotation_deg"]), oc)
    lx, ly = lx - oc[0], ly - oc[1]
    ow, od = (float(v) for v in fo["size"][:2])
    nw, nd = (float(v) for v in fn["size"][:2])
    u, v = (lx / ow if ow > 1e-9 else 0.0), (ly / od if od > 1e-9 else 0.0)
    x, y = G.rotate_point((nc[0] + u * nw, nc[1] + v * nd), float(fn["rotation_deg"]), nc)
    item["center"] = [round(x, 3), round(y, 3)] + list(item["center"][2:])
    turn = float(item.get("rotation_deg") or fo["rotation_deg"]) - float(fo["rotation_deg"])
    item["rotation_deg"] = round(G.normalise_angle(float(fn["rotation_deg"]) + turn), 3)


def hand_over(decor: list[dict], gone: list[dict], new: list[dict]) -> set:
    """Every decor item of a gone piece onto its successor (module docstring), in place. Returns the ``id()`` of the
    items it handed over (a new piece may take a gone piece's id)."""
    mapping = successors(gone, new)
    handed: set = set()
    if not mapping:
        return handed
    old = {str(p["id"]): p for p in gone}
    by_new = {str(p["id"]): p for p in new}
    for item in decor:
        host = item.get("host_id")
        anchors = [a for a in item.get("anchor_ids") or [] if a]
        frame = item.get("host_frame") if isinstance(item.get("host_frame"), dict) else None
        if host in mapping:
            if not (frame and frame.get("support")) and item.get("center") and old[host].get("footprint") \
                    and by_new[mapping[host]].get("footprint"):
                _onto(item, old[host], by_new[mapping[host]])
            item["handed_over"] = {"from": host, "to": mapping[host],
                                   "reason": "its piece was re-placed by the solver (the same type nearest to it)"}
            item["host_id"] = mapping[host]
            handed.add(id(item))
        elif any(a in mapping for a in anchors):
            item["handed_over"] = {"from": [a for a in anchors if a in mapping],
                                   "to": [mapping[a] for a in anchors if a in mapping],
                                   "reason": "its pieces were re-placed by the solver (the same type nearest to them)"}
            handed.add(id(item))
        if any(a in mapping for a in anchors):
            item["anchor_ids"] = [mapping.get(a, a) for a in item.get("anchor_ids") or []]
            if frame is not None and frame.get("anchor_id") in mapping:
                frame["anchor_id"] = mapping[frame["anchor_id"]]
    return handed
