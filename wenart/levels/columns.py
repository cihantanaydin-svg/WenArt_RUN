"""Columns that run through the floors of outdoor spaces (pure, ``wenart.geometry`` only, so the levels stage and the
Blender build both use it; lesson UL209)."""
from __future__ import annotations

from typing import Sequence

from wenart import geometry as G

# 30 Oct 2026 (lesson UL209, user on real06's front: "columns seems cut in the middle ... this whole area requires a
# huge rework"): a drawn column under a balcony carried the slab (``assign_posts``) and a second post stood on it from the
# balcony's floor to the house roof (``house_roof_posts``). Two posts with the 0.2 m slab between them, the slab's edge
# on the columns' centre line: the front half of every column had a notch half way up. A post that stands on the post
# of a space below it (the same centre within ``JOIN["center_m"]``, the same shape, sizes within ``JOIN["size_m"]``,
# its foot within ``JOIN["gap_m"]`` of the lower one's top) is one column: the lower post runs on through the slab to
# the upper one's top (``through``: the spaces it passes, ``carries`` names both loads) and the upper space keeps it in
# ``through_posts`` (its guard stops at the column, its slab and roofs leave it free).
JOIN = {"center_m": 0.1, "size_m": 0.03, "gap_m": 0.3}


def _same_look(p: dict, q: dict) -> bool:
    return (str(p.get("shape") or "square") == str(q.get("shape") or "square")
            and abs(float(p.get("size_m") or 0.0) - float(q.get("size_m") or 0.0)) <= JOIN["size_m"] + 1e-9)


def join_stacked_posts(spaces: Sequence[dict]) -> list[str]:
    """Join the posts that stand on a post of a space below into one column (mutated; lesson UL209, see ``JOIN``);
    returns the reasons. Spaces are taken from the lowest up, so a column under two storeys of balconies is one."""
    out = []
    ordered = sorted(spaces, key=lambda s: float(s["z"]))
    for up in ordered:
        for q in list(up.get("posts") or []):
            low = None
            for s in ordered:
                if s is up or float(s["z"]) > float(up["z"]) - 1.0:
                    continue
                for p in s.get("posts") or []:
                    if (G.distance(p["center"], q["center"]) <= JOIN["center_m"] and _same_look(p, q)
                            and abs(float(q["z0"]) - float(p["z1"])) <= JOIN["gap_m"] + 1e-9
                            and float(q["z1"]) > float(p["z1"])):
                        low = (s, p)
            if low is None:
                continue
            s, p = low
            was = float(p["z1"])
            p["z1"] = q["z1"]
            p.setdefault("through", []).append(up["id"])
            p["carries"] = f"{p.get('carries') or 'its space'}, and on through it to {q.get('carries') or 'the top'}"
            up["posts"].remove(q)
            up.setdefault("through_posts", []).append(
                {k: p.get(k) for k in ("center", "shape", "size_m", "size_xy", "rotation_deg", "z0", "z1", "id")}
                | {"owner": s["id"]})
            out.append(f"{p.get('id') or 'the post'} at ({p['center'][0]:.2f}, {p['center'][1]:.2f}): one column from "
                       f"{s['id']}'s floor ({float(p['z0']):+.2f} m) through the slab of {up['id']} to "
                       f"{float(p['z1']):+.2f} m (it stopped at {was:+.2f} m and a second post stood on it: the slab "
                       f"cut it in the middle; lesson UL209)")
    return out
