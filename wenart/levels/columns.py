"""Columns that run through the floors of outdoor spaces (pure, ``wenart.geometry`` only, so the levels stage and the
Blender build both use it; lessons UL209, UL214)."""
from __future__ import annotations

from typing import Optional, Sequence

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


def _look(p: dict) -> dict:
    """The drawn look of a post (its ``drawn_look`` once ``design_columns`` made it slender)."""
    return p.get("drawn_look") if isinstance(p.get("drawn_look"), dict) else p


def _same_look(p: dict, q: dict) -> bool:
    a, b = _look(p), _look(q)
    return (str(a.get("shape") or "square") == str(b.get("shape") or "square")
            and abs(float(a.get("size_m") or 0.0) - float(b.get("size_m") or 0.0)) <= JOIN["size_m"] + 1e-9)


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


# 30 Oct 2026 (lesson UL214, user on the UL209 preview of real06's front: "could be more elegant columns up to the roof
# is too thick maybe there are better solutions"; of the seven options rendered, the user chose D+A: slender round steel
# posts and a crisp deep balcony edge band). The drawn 0.40 m round columns ran 6.0 m from the veranda floor through the
# balcony slab to the eaves, about 1:15, the proportion of a classical column, in a Scandinavian house. A drawn column
# is the structure's envelope; in the families of ``SLENDER_FAMILIES`` its visible section is a slender round steel post
# (EN 10219-2 circular hollow section, ``CHS_M``) on a thin base plate under a thin cap plate (the build's
# ``POST_DETAIL``), in the window frames' finish:
# - a column that runs more than one storey (``STOREY_M`` tall, or joined through a slab by UL209: ``through``) and a
#   drawn single-storey column of ``THICK_M`` or more take the smallest section at least ``height / SLENDER_RATIO``
#   (about 1:25-1:30), at least ``CHS_M[0]``; never wider than drawn (a thinner drawn post keeps its size);
# - a single-storey post under ``THICK_M`` (a veranda roof's post) stays as it is;
# - the other families (classic, traditional, rustic, mediterranean ...) keep their drawn, proportioned column with its
#   base and head (UL209).
# The drawn look stays in ``drawn_look``; the change is labelled ``adjusted_by_ai`` with the reason. The upper spaces'
# ``through_posts`` follow the column they name (their guards, slabs and roofs stop at the slimmer outline).
CHS_M: tuple[float, ...] = (0.1143, 0.1397, 0.1683, 0.1937, 0.2191, 0.2445, 0.2730)   # EN 10219-2 outer diameters
SLENDER_RATIO = 30.0
STOREY_M = 3.5
THICK_M = 0.25
SLENDER_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "minimal", "modern minimal", "scandinavian", "japandi",
                                     "industrial", "organic modern")
RULE = "columns.design_columns"
LESSON = "UL214"


def slender_section(height: float, drawn: Optional[float] = None) -> float:
    """The diameter of a slender round steel post ``height`` tall (pure): the smallest ``CHS_M`` section at least
    ``height / SLENDER_RATIO`` (the largest when none is), never wider than ``drawn``."""
    need = float(height) / SLENDER_RATIO
    best = next((s for s in CHS_M if s >= need - 1e-9), CHS_M[-1])
    return round(min(best, float(drawn)) if drawn else best, 4)


def slender_family(family: Optional[str]) -> bool:
    return str(family or "").strip().lower() in SLENDER_FAMILIES


def design_post(q: dict) -> Optional[str]:
    """The slender round steel post of one column (mutated; pure; see above): the reason, or None when it keeps its
    look (a single-storey post under ``THICK_M``, or one already slender). Idempotent."""
    if q.get("finish") == "steel":
        return None
    drawn = {k: q.get(k) for k in ("shape", "size_m", "size_xy", "rotation_deg")}
    size = float(drawn.get("size_m") or 0.0)
    height = float(q.get("z1") or 0.0) - float(q.get("z0") or 0.0)
    tall = height >= STOREY_M - 1e-9 or bool(q.get("through"))
    if not tall and size < THICK_M - 1e-9:
        return None
    d = slender_section(height, size or None)
    if size and d >= size - 1e-9:
        return None                                    # drawn as slender as the rule or slimmer: as drawn
    q["drawn_look"] = drawn
    q.update({"shape": "round", "size_m": d, "size_xy": [d, d], "finish": "steel", "detail": "plate"})
    reason = (f"{q.get('id') or 'the post'}: a slender {d * 1000:.1f} mm round steel post on a base plate, "
              f"{height:.2f} m tall (about 1:{height / d:.0f}); drawn a {size:.2f} m {drawn.get('shape') or 'square'} "
              f"column (kept as drawn_look); the user chose slender steel posts for the house's columns (lesson "
              f"{LESSON})")
    q["adjusted_by_ai"] = {"by": "code", "rule": RULE, "lesson": LESSON, "reason": reason}
    return reason


def design_columns(spaces: Sequence[dict], family: Optional[str]) -> list[str]:
    """The columns of the outdoor spaces in the house's family (mutated; lesson UL214, see above): slender round steel
    posts in ``SLENDER_FAMILIES``, else as drawn; returns the reasons. Every space's ``through_posts`` follow the
    column they name."""
    if not slender_family(family):
        return []
    out = []
    for s in spaces:
        for q in s.get("posts") or []:
            why = design_post(q)
            if why:
                out.append(why)
    owners = [q for s in spaces for q in s.get("posts") or [] if q.get("finish") == "steel"]
    for s in spaces:
        for t in s.get("through_posts") or []:
            own = next((q for q in owners if G.distance(q["center"], t["center"]) <= JOIN["center_m"]), None)
            if own is not None:
                t.update({k: own[k] for k in ("shape", "size_m", "size_xy", "finish", "detail", "drawn_look")})
    return out
