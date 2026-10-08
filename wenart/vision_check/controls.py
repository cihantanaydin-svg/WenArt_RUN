"""Removal / insertion / type-swap controls of the vision check (docs/milestone5.md §5.5).

``select_controls`` picks, per project, up to 3 furniture pieces (at least one
``from_documents`` when there is one), 3 windows and 2 doors (counts in
``check.yaml: controls``): required, own room, area_frac >= 0.03, not
touching the image border, one per room and per id, largest first. Each id
is controlled in the view where it is largest. Type-unverified pieces are
left out (their type cannot be swapped and their striped proxy is not a
real piece). Windows are plugged when hidden, doors are not (an empty
doorway is not a door).

Milestone 10 (docs/milestone10.md §2.8): the expected lists come from ``building_final.json`` (through the
scene manifest), so the controls are chosen among the pieces as they stand after Feature 1 (changed drawn
pieces keep ``source: from_documents``; the "at least one from_documents" rule counts them); a furniture control
carries ``modified_by_ai``, ``drawn_type`` and ``completes_room``. Exterior views have no own-room element, so
they are never a control camera.

Type swaps: up to ``controls.swaps`` required furniture pieces whose type has a
partner in ``controls.swap_pairs`` (sofa <-> bed_double, armchair <-> desk),
same filters; the list asks for the partner type on the normal render.

``check/controls.json``::

    {"schema_version": "0.1", "dir_relative_to": "project_out",
     "controls": [{"id", "index", "kind", "type", "camera", "room_id", "plug",
                   "area_frac", "source", "dir": "controls/hide_<id>"}],
     "swaps": [{"id", "index", "type", "swap_to", "camera", "room_id", "area_frac", "source"}]}

``dir`` is relative to the project output (``outputs/<p>``), as §5.5 writes it;
the job renders ``--hide-sets 'cam:id[+plug];...'`` into ``outputs/<p>/controls``
and the render writes each set into ``hide_<id>/``. One line per control is
printed for the job: ``CONTROL\\t<id>\\t<camera>\\t<0|1>\\t<dir>``.
"""
from __future__ import annotations

from typing import Optional

KINDS = (("furniture", "furniture"), ("window", "windows"), ("door", "doors"))


def _candidates(expected_views: dict, kind: str, min_area: float) -> list[dict]:
    """Best view per element id of one kind that passes the control filters, largest first."""
    best: dict[str, dict] = {}
    for cam in sorted(expected_views):
        exp = expected_views[cam]
        if exp.get("view_kind") == "exterior":
            continue                      # the controls hide and plug pieces of a room; an exterior view has none
        for e in exp.get("elements") or []:
            if e.get("kind") != kind or e.get("role") != "required" or not e.get("own_room"):
                continue
            if e.get("touches_border") or float(e.get("area_frac") or 0.0) < min_area:
                continue
            if kind == "furniture" and e.get("type_unverified"):
                continue
            cand = {"id": e["wenart_id"], "index": int(e["index"]), "kind": kind, "type": e.get("type"),
                    "camera": cam, "room_id": exp.get("room_id"), "area_frac": float(e["area_frac"]),
                    "source": e.get("source")}
            if kind == "furniture":
                # Milestone 10, Feature 1: the expected lists read building_final.json, so a drawn piece the AI
                # changed (its new type and size are the expected ones) or a piece it added is a control like
                # any other; the record says which, for the report.
                cand.update(modified_by_ai=bool(e.get("modified_by_ai")), drawn_type=e.get("drawn_type"),
                            completes_room=bool(e.get("completes_room")))
            old = best.get(cand["id"])
            if old is None or cand["area_frac"] > old["area_frac"]:
                best[cand["id"]] = cand
    return sorted(best.values(), key=lambda c: (-c["area_frac"], c["id"]))


def _pick(cands: list[dict], n: int, first: Optional[dict] = None) -> list[dict]:
    out, rooms = [], set()
    for c in ([first] if first else []) + cands:
        if len(out) >= n:
            break
        if any(o["id"] == c["id"] for o in out) or c["room_id"] in rooms:
            continue
        out.append(c)
        rooms.add(c["room_id"])
    return sorted(out, key=lambda c: (-c["area_frac"], c["id"]))


def select_controls(expected_views: dict, cfg: dict) -> dict:
    """``controls.json`` content from the project's expected views (§5.5)."""
    ccfg = cfg["controls"]
    min_area = float(ccfg["min_area_frac"])
    controls = []
    for kind, count_key in KINDS:
        cands = _candidates(expected_views, kind, min_area)
        first = None
        if kind == "furniture":
            first = next((c for c in cands if c.get("source") == "from_documents"), None)
        for c in _pick(cands, int(ccfg[count_key]), first):
            controls.append(dict(c, plug=(kind == "window"), dir=f"controls/hide_{c['id']}",
                                 area_frac=round(c["area_frac"], 5)))
    partners = {}
    for a, b in ccfg.get("swap_pairs") or []:
        partners[a], partners[b] = b, a
    swap_cands = [c for c in _candidates(expected_views, "furniture", min_area) if c["type"] in partners]
    swaps = [dict(c, swap_to=partners[c["type"]], area_frac=round(c["area_frac"], 5))
             for c in _pick(swap_cands, int(ccfg.get("swaps", 3)))]
    for s in swaps:
        s.pop("kind", None)
    return {"schema_version": "0.1", "dir_relative_to": "project_out", "controls": controls, "swaps": swaps}


def control_lines(selection: dict) -> list[str]:
    """``CONTROL\\t<id>\\t<camera>\\t<0|1>\\t<dir>`` per control (read by scripts/jobs/polish.sh)."""
    return [f"CONTROL\t{c['id']}\t{c['camera']}\t{1 if c['plug'] else 0}\t{c['dir']}"
            for c in selection.get("controls") or []]


def hide_sets(selection: dict) -> str:
    """The ``--hide-sets`` argument of ``wenart.blender.cli render`` for these controls."""
    return ";".join(f"{c['camera']}:{c['id']}{'+plug' if c['plug'] else ''}" for c in selection.get("controls") or [])
