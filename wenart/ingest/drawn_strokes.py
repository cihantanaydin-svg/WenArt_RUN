"""A level's drawn strokes in building metres, for the completion rules (12 Nov 2026; the coordinator's decisions on
stage 1: an inferred stair needs a stair sign drawn in its box, a balcony window becomes a door only with its swing
drawn).

What: ``Drawn.of(extraction)`` wraps the strokes the generic core keeps for its page (``ex.report["page_strokes"]``,
page units) with the page's transform to the building frame; ``segments(poly)`` returns the straight pieces whose
middle lies in a polygon (building metres) and ``arcs(poly)`` the arcs whose centre lies in it, each with its stroke
id and layer (the evidence). None for a page without strokes (an old extractor, a raster page).

Why: the rules decide from what is drawn, never from a default: a well line or a break diagonal in a stair-size box, a
door's swing arc at a window's jamb.

How: pure; the page is searched by the box of the polygon mapped back to page units (the inverse affine).
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import Point, Polygon

from wenart import geometry as G


class Drawn:
    """The strokes of one page, queried in building metres (pure)."""

    def __init__(self, strokes: list, m6):
        self.strokes = [st for st in strokes or [] if getattr(st, "pts", None)]
        self.m6 = list(m6)
        self.inv = G.invert_affine(self.m6)
        a, b, _c, d, e, _f = self.m6
        self.scale = math.sqrt(abs(a * e - b * d))
        self._boxes = None

    @classmethod
    def of(cls, ex) -> Optional["Drawn"]:
        strokes = (getattr(ex, "report", None) or {}).get("page_strokes") if isinstance(getattr(ex, "report", None),
                                                                                        dict) else None
        if not strokes or getattr(ex, "transform_to_building", None) is None:
            return None
        try:
            return cls(strokes, ex.transform_to_building)
        except ZeroDivisionError:
            return None

    def _candidates(self, poly: Polygon) -> list:
        if self._boxes is None:
            self._boxes = [(min(p[0] for p in st.pts), min(p[1] for p in st.pts), max(p[0] for p in st.pts),
                            max(p[1] for p in st.pts)) for st in self.strokes]
        corners = [G.apply_affine(self.inv, (x, y)) for x, y in list(poly.exterior.coords)[:-1]]
        x0, x1 = min(c[0] for c in corners), max(c[0] for c in corners)
        y0, y1 = min(c[1] for c in corners), max(c[1] for c in corners)
        return [st for st, (a, b, c, d) in zip(self.strokes, self._boxes) if a <= x1 and c >= x0 and b <= y1 and d >= y0]

    def segments(self, poly: Polygon) -> list:
        """``[{a, b, length, id, layer}]``: the straight pieces of the strokes (no arcs) whose middle lies in ``poly``."""
        out = []
        for st in self._candidates(poly):
            if getattr(st, "arc", None):
                continue
            pts = [G.apply_affine(self.m6, p) for p in st.pts]
            for a, b in zip(pts, pts[1:]):
                mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
                if math.dist(a, b) > 1e-6 and poly.contains(Point(mid)):
                    out.append({"a": a, "b": b, "length": math.dist(a, b), "id": st.id, "layer": st.layer})
        return out

    def rectangles(self, poly: Polygon) -> list:
        """``[{center, size: (short, long), id, layer}]`` (metres): the closed four-cornered strokes (rectangles) whose
        middle lies in ``poly``: a lift car, a counterweight."""
        out = []
        for st in self._candidates(poly):
            pts = [G.apply_affine(self.m6, p) for p in st.pts]
            if len(pts) >= 2 and math.dist(pts[0], pts[-1]) < 1e-6:
                pts = pts[:-1]
            if len(pts) != 4 or not (getattr(st, "closed", False) or len(st.pts) == 5):
                continue
            sides = [math.dist(pts[k], pts[(k + 1) % 4]) for k in range(4)]
            if min(sides) < 1e-6:
                continue
            ux, uy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
            vx, vy = pts[2][0] - pts[1][0], pts[2][1] - pts[1][1]
            if abs(ux * vx + uy * vy) > 0.05 * sides[0] * sides[1]:
                continue                                  # not square-cornered
            c = (sum(p[0] for p in pts) / 4.0, sum(p[1] for p in pts) / 4.0)
            if poly.contains(Point(c)):
                a, b = sorted((sides[0], sides[1]))
                out.append({"center": c, "size": (a, b), "id": st.id, "layer": st.layer})
        return out

    def arcs(self, poly: Polygon) -> list:
        """``[{center, radius, ends, id, layer}]`` (metres): the arcs whose centre or one of whose ends lies in
        ``poly``."""
        out = []
        for st in self._candidates(poly):
            arc = getattr(st, "arc", None)
            if not arc or arc.get("center") is None or not arc.get("radius"):
                continue
            c = G.apply_affine(self.m6, tuple(arc["center"]))
            ends = [G.apply_affine(self.m6, st.pts[0]), G.apply_affine(self.m6, st.pts[-1])]
            if any(poly.contains(Point(q)) for q in [c] + ends):
                out.append({"center": c, "radius": float(arc["radius"]) * self.scale, "ends": ends, "id": st.id,
                            "layer": st.layer})
        return out
