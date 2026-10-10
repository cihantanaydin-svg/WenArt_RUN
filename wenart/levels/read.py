"""Level marks read from the drawings into the building JSON (docs/milestone12.md §3.1-§3.2; owner: track L).

What (pure; ``wenart.ingest.generic.levels.apply_levels`` gives the texts of every page in building metres):

- ``read_marks(texts, building, params, section=None) -> {"marks", "datum", "conflicts", "warnings"}``: every text
  that is a level mark (``wenart.levels.marks.read_mark``: a sign, a keyword, or an attribute tag of
  ``MARK_ATTRIBUTE_TAGS``; a bare number in the same block reference as another mark is its companion, e.g. the
  ``93.20`` under ``+0.00``), the section's level marks (``sheets.json`` heights: slab tops and the datum), one record
  per mark (``building["level_marks"]``, schema §13.3) with its evidence;
- the **datum** (``±0.00`` in absolute metres): a mark that is a pair (``±0.00 = 93.20``, ``TESVİYE 0.00 KOTU :
  93.20``), a relative and an absolute mark in one block reference (``+0.00`` / ``93.20``), and the section's datum
  (``project.datum`` of an absolute value); the most frequent value wins (ties: the section), others that differ by
  more than ``mark_tol`` are a ``level_mark_mismatch`` conflict; absolute marks are converted with it (``value`` then
  relative, ``absolute`` kept); without a datum they stay absolute, ``z`` null, listed and not used;
- ``classify(marks, building, params)``: the **kind by position** (§3.1 table): a keyword or tag kind first
  (``T.Z.`` ground, ``SB.`` plinth, ``GİRİŞ`` entrance ...); else inside a room of its level -> that room's
  ``floor``; outside the outline within ``door_mark_reach`` of an outside door -> ``threshold`` (its landing);
  outside within ``ground_reach`` -> ``ground_finished``; farther -> ``unknown`` (another drawing on the sheet); a
  site note (``... KOTU : 93.20``) keeps its keyword kind and is position-free (``note``);
- ``mark_symbols(building, marks)``: drawn pieces that are level-mark symbols (a block reference holding a mark
  text: real03 ``f_L0_142``, INSERT 7C9C9/48), or a small untyped piece around a mark text: moved from
  ``furniture`` to ``symbols`` (kind ``level_mark``, ``former_piece_id``, reason, evidence; bug B11);
- ``drawn_ramps(texts, building, params)``: a ``RAMPA`` / ``RAMP`` text outside near an outside door: a drawn ramp.

Why: CLAUDE.md (Milestone 12): level marks are source data for floor levels, door thresholds and the ground, with
the trust order of geometry; a mark is never furniture.
"""
from __future__ import annotations

import re
from typing import Optional, Sequence

from wenart import building as B
from wenart import geometry as G
from wenart.levels import marks as LM

SYMBOL_MAX_SIDE_M = 1.2           # a piece around a mark text this small (or smaller) is the mark's symbol
SYMBOL_MAX_AREA_M2 = 0.6
SYMBOL_TYPES = ("unknown", "floor_lamp", "plant", "potted_plant", "plant_large", "side_table", "stool")
DEDUPE_M = 0.30
RAMP_RE = re.compile(r"\bRAMPA?\b")


def insert_path(entity: Optional[str]) -> Optional[str]:
    """``INSERT:7C9C9/48`` of a text or stroke id inside a block reference (``INSERT:7C9C9/48/attrib1``,
    ``INSERT:7C9C9/48/3``), None for a model-space entity."""
    e = str(entity or "").split(",")[0].strip()
    if not e.startswith("INSERT:") or "/" not in e:
        return None
    return e.rsplit("/", 1)[0]


def _status(ev: dict) -> str:
    return "verified" if (ev or {}).get("method") == "vector" else "unverified"


# --------------------------------------------------------------------------
# Marks and datum
# --------------------------------------------------------------------------

def read_marks(texts: Sequence[dict], building: dict, params: dict, section: Optional[dict] = None) -> dict:
    """Texts -> mark records (module docstring). ``texts``: ``[{"text", "point": (x, y) building metres,
    "level_id", "entity", "evidence": {...}, "attrib_tag"}]``; ``section``: ``sheets.json`` ``heights`` (or None)."""
    parsed: list[tuple[dict, dict]] = []
    groups: dict[str, list[int]] = {}
    pending = []
    for t in texts:
        tag = t.get("attrib_tag") or (t.get("evidence") or {}).get("attrib_tag")
        rec = LM.read_mark(t.get("text") or "", bare=LM.is_mark_tag(tag))
        grp = insert_path(t.get("entity"))
        if rec is None:
            if grp:
                pending.append((t, grp, tag))
            continue
        if tag and rec.get("kind_hint") is None and LM.tag_kind(tag):
            rec["kind_hint"] = LM.tag_kind(tag)
        if grp:
            groups.setdefault(grp, []).append(len(parsed))
        parsed.append((t, dict(rec, group=grp, tag=tag)))
    for t, grp, tag in pending:                  # a bare value in a block reference that holds a mark
        if grp in groups:
            rec = LM.read_mark(t.get("text") or "", bare=True)
            if rec is not None:
                groups[grp].append(len(parsed))
                parsed.append((t, dict(rec, group=grp, tag=tag)))
    warnings: list[str] = []
    conflicts: list[dict] = []
    marks: list[dict] = []
    for t, rec in parsed:
        ev = dict(t.get("evidence") or {"file": "", "method": "vector", "confidence": 1.0})
        ev.setdefault("text", t.get("text"))
        dup = next((m for m in marks if m["level_id"] == t.get("level_id") and abs(m["value"] - rec["value"]) < 0.005
                    and m["relative"] == rec["relative"] and m.get("point") is not None and t.get("point") is not None
                    and G.distance(m["point"], t["point"]) <= DEDUPE_M), None)
        if dup is not None:
            dup["evidence"].append(ev)
            continue
        marks.append({"id": f"lm_{len(marks) + 1:03d}", "value": rec["value"], "relative": rec["relative"],
                      "absolute": rec["absolute"], "kind": None, "kind_hint": rec["kind_hint"],
                      "point": [round(float(t["point"][0]), 4), round(float(t["point"][1]), 4)]
                      if t.get("point") is not None else None,
                      "level_id": t.get("level_id"), "room_id": None, "side": None, "raw": t.get("text") or "",
                      "used_for": [], "status": _status(ev), "evidence": [ev], "note": rec["note"],
                      "bare": rec["bare"], "group": rec["group"], "placement": "note" if rec["note"] else "spot",
                      "z": None})
    # The section's level marks: slab tops of the levels (building z), the datum.
    for h in (section or {}).get("levels") or []:
        lm = h.get("level_mark") or {}
        if lm.get("value") is None:
            continue
        ev = [dict(e) for e in lm.get("evidence") or []] or [{"file": "", "method": "vector", "confidence": 1.0}]
        marks.append({"id": f"lm_{len(marks) + 1:03d}", "value": round(float(lm["value"]), 4), "relative": True,
                      "absolute": None, "kind": "slab_top", "kind_hint": "slab_top", "point": None,
                      "level_id": h.get("level_id"), "room_id": None, "side": None,
                      "raw": (ev[0].get("text") or "") if ev else "", "used_for": ["section"], "status": "verified",
                      "evidence": ev, "note": False, "bare": False, "group": None, "placement": "section",
                      "z": round(float(lm["value"]), 4)})
    datum = resolve_datum(marks, (building.get("project") or {}).get("datum"), params, conflicts, warnings)
    for m in marks:
        if m["placement"] == "section":
            continue
        if m["relative"]:
            m["z"] = m["value"]
        elif datum is not None:
            m["absolute"] = m["value"]
            m["value"] = round(m["value"] - datum["value"], 4) + 0.0
            m["relative"] = True
            m["z"] = m["value"]
        else:
            warnings.append(f"{m['id']}: absolute level {m['raw']!r} and no datum (±0.00 = ?): not used")
    return {"marks": marks, "datum": datum, "conflicts": conflicts, "warnings": warnings}


def resolve_datum(marks: list[dict], project_datum: Optional[dict], params: dict, conflicts: list,
                  warnings: list) -> Optional[dict]:
    """The absolute level of ±0.00: ``{"value", "sources": [mark ids / "section"], "evidence"}`` or None."""
    cands: list[tuple[float, str, list]] = []
    for m in marks:
        if m["relative"] and m.get("absolute") is not None:
            cands.append((round(m["absolute"] - m["value"], 3), m["id"], m["evidence"]))
            m["used_for"].append("datum")
    by_group: dict[str, list[dict]] = {}
    for m in marks:
        if m.get("group"):
            by_group.setdefault(m["group"], []).append(m)
    for grp, ms in sorted(by_group.items()):
        rel = [m for m in ms if m["relative"] and m.get("absolute") is None]
        ab = [m for m in ms if not m["relative"]]
        if len(rel) == 1 and len(ab) == 1:
            cands.append((round(ab[0]["value"] - rel[0]["value"], 3), f"{rel[0]['id']}+{ab[0]['id']}",
                          rel[0]["evidence"] + ab[0]["evidence"]))
            rel[0]["absolute"] = ab[0]["value"]
            for m in (rel[0], ab[0]):
                m["used_for"].append("datum")
            ab[0]["pair_of"] = rel[0]["id"]
    sec = None
    if isinstance(project_datum, dict) and project_datum.get("value") is not None \
            and float(project_datum["value"]) >= LM.ABSOLUTE_FROM_M:
        sec = (round(float(project_datum["value"]), 3), "section", list(project_datum.get("evidence") or []))
        cands.append(sec)
    if not cands:
        return None
    counts: dict[float, int] = {}
    for v, _src, _ev in cands:
        counts[v] = counts.get(v, 0) + 1
    best = max(counts, key=lambda v: (counts[v], sec is not None and abs(v - sec[0]) < 1e-9, -v))
    tol = float(params.get("mark_tol", 0.02))
    others = [c for c in cands if abs(c[0] - best) > tol]
    if others:
        conflicts.append({"kind": "level_mark_mismatch", "element_ids": [c[1] for c in cands],
                          "description": "the datum (±0.00 in absolute metres) reads "
                                         + ", ".join(f"{v:.2f} ({src})" for v, src, _ in cands),
                          "resolution": f"{best:.2f} used: the most frequent (DWG > vector PDF > scan; the section "
                                        f"on a tie)"})
    used = [c for c in cands if abs(c[0] - best) <= tol]
    return {"value": best, "sources": [c[1] for c in used], "evidence": [e for c in used for e in c[2]][:4]}


# --------------------------------------------------------------------------
# Kind by position
# --------------------------------------------------------------------------

def _outside_doors(building: dict, level_id: str, rooms: list, outline) -> list[dict]:
    from wenart.levels import model as LMOD

    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != level_id or o.get("type") != "door":
            continue
        s = LMOD.opening_sides(building, o, rooms, outline)
        if s is None or sum(s["outside"]) != 1:
            continue
        k = 0 if s["outside"][0] else 1
        n = s["normal"]
        out_n = (n[0], n[1]) if k == 0 else (-n[0], -n[1])
        face = (s["centre"][0] + out_n[0] * s["half_t"], s["centre"][1] + out_n[1] * s["half_t"])
        out.append({"id": o["id"], "face": face, "outward": out_n, "width": float(o.get("width") or 0.9)})
    return out


def classify(marks: list[dict], building: dict, params: dict) -> list[str]:
    """Set ``kind``, ``room_id`` and ``side`` of every mark (mutated; module docstring). Returns warnings."""
    from wenart.blender import site as S
    from wenart.levels import model as LMOD

    warnings = []
    cache: dict = {}
    north, src = S.north_deg(building)
    known = not src.startswith("assumed")
    gl = LMOD.ground_level(building)
    for m in marks:
        if m.get("kind") is not None:            # set by the section, or by an agent edit (set_mark_kind)
            continue
        hint = m.get("kind_hint")
        lid = m.get("level_id") or (gl or {}).get("id")
        m["level_id"] = lid
        if m.get("note") or m.get("point") is None:
            m["kind"] = hint or "unknown"
            if m["kind"] == "unknown":
                warnings.append(f"{m['id']}: mark {m['raw']!r} without a position or keyword: kind unknown")
            continue
        if lid not in cache:
            rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid]
            outline = LMOD.level_outline(building, lid) if lid else []
            cache[lid] = (rooms, outline, _outside_doors(building, lid, rooms, outline) if lid else [])
        rooms, outline, doors = cache[lid]
        p = tuple(m["point"])
        room = next((r for r in rooms if len(r.get("polygon") or []) >= 3 and G.point_in_polygon(p, r["polygon"])),
                    None)
        inside = len(outline) >= 3 and G.point_in_polygon(p, outline)
        if room is None and inside:
            near = [(LMOD._dist_to_polygon(p, r["polygon"]), r["id"], r) for r in rooms if len(r.get("polygon") or [])
                    >= 3]
            near = [x for x in near if x[0] <= 0.5]
            room = min(near, key=lambda x: (x[0], x[1]))[2] if near else None
        if room is not None:
            m["room_id"] = room["id"]
            m["kind"] = hint if hint in ("plinth", "slab_top", "entrance", "datum") else "floor"
            continue
        if inside or len(outline) < 3:
            m["kind"] = hint or "unknown"
            if m["kind"] == "unknown":
                warnings.append(f"{m['id']}: mark {m['raw']!r} inside the outline but in no room: kind unknown")
            continue
        cx = sum(q[0] for q in outline) / len(outline)
        cy = sum(q[1] for q in outline) / len(outline)
        d = (p[0] - cx, p[1] - cy)
        n = (d[0] ** 2 + d[1] ** 2) ** 0.5 or 1.0
        m["side"] = S.side_of((d[0] / n, d[1] / n), north, known)
        reach = float(params["door_mark_reach"])
        door = min(((G.distance(p, dd["face"]), dd["id"], dd) for dd in doors
                    if G.distance(p, dd["face"]) <= reach + dd["width"] / 2.0), default=None,
                   key=lambda x: (x[0], x[1]))
        dist = LMOD._dist_to_polygon(p, outline)
        if door is not None and hint not in ("ground_natural", "slope_top", "plinth"):
            m["kind"] = "entrance" if hint == "entrance" else "threshold"
            m["door_id"] = door[2]["id"]
        elif dist > float(params["ground_reach"]):
            m["kind"] = "unknown"
            warnings.append(f"{m['id']}: mark {m['raw']!r} {dist:.1f} m from the building: another drawing on the "
                            f"sheet, not used")
        else:
            m["kind"] = hint if hint in ("ground_natural", "ground_finished", "slope_top", "plinth", "entrance") \
                else "ground_finished"
    return warnings


# --------------------------------------------------------------------------
# Symbols and drawn ramps
# --------------------------------------------------------------------------

def _piece_path(piece: dict) -> Optional[str]:
    ents = [e.strip() for ev in (piece.get("evidence") or [])[:1] for e in str(ev.get("entity") or "").split(",")]
    paths = {insert_path(e) for e in ents if e}
    paths.discard(None)
    return paths.pop() if len(paths) == 1 else None


def mark_symbols(building: dict, marks: list[dict]) -> list[dict]:
    """``[{"piece_id", "symbol", "mark_ids"}]``: the drawn pieces that are level-mark symbols (module docstring);
    pure (the caller moves them)."""
    out = []
    for f in building.get("furniture") or []:
        if f.get("source") != "from_documents" or f.get("type") in ("stair", "kitchen_counter"):
            continue
        fp = f.get("footprint") or {}
        if not fp.get("center") or not fp.get("size"):
            continue
        path = _piece_path(f)
        poly = G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
        grown = G.rotated_rectangle(fp["center"], (float(fp["size"][0]) + 0.1, float(fp["size"][1]) + 0.1),
                                    float(fp.get("rotation_deg") or 0.0))
        near = G.rotated_rectangle(fp["center"], (float(fp["size"][0]) + 1.0, float(fp["size"][1]) + 1.0),
                                   float(fp.get("rotation_deg") or 0.0))
        side = max(float(fp["size"][0]), float(fp["size"][1]))
        small = side <= SYMBOL_MAX_SIDE_M and float(fp["size"][0]) * float(fp["size"][1]) <= SYMBOL_MAX_AREA_M2 \
            and f.get("type") in SYMBOL_TYPES
        hit = []
        for m in marks:
            if m.get("placement") != "spot" or m.get("point") is None:
                continue
            p = tuple(m["point"])
            # the same block reference (its strokes and the mark text), the text beside the symbol, the symbol
            # never larger than 2 m (a whole flat is one block reference too)
            same = path is not None and m.get("group") == path and side <= 2.0 and G.point_in_polygon(p, near)
            if same or (small and G.point_in_polygon(p, grown)):
                hit.append(m)
        if not hit:
            continue
        why = ("the block reference holds the level mark" if path and any(m.get("group") for m in hit)
               else "a small drawn piece around a level mark text")
        reason = (f"a level-mark symbol, not furniture ({why}: {', '.join(repr(m['raw']) for m in hit)}); drawn as "
                  f"{f.get('type')} {float(fp['size'][0]):.2f} x {float(fp['size'][1]):.2f} m")
        sym = {"id": f"sym_{f['id']}", "kind": "level_mark", "level_id": f.get("level_id"), "room_id": f.get("room_id"),
               "footprint": {"center": list(fp["center"]), "size": list(fp["size"]),
                             "rotation_deg": float(fp.get("rotation_deg") or 0.0)},
               "former_piece_id": f["id"], "reason": reason, "crop": None,
               "evidence": [dict(e) for e in (f.get("evidence") or [])[:1]] + [dict(e) for m in hit
                                                                                for e in m["evidence"][:1]],
               "mark_ids": [m["id"] for m in hit]}
        out.append({"piece_id": f["id"], "symbol": sym, "mark_ids": sym["mark_ids"], "polygon": poly})
    return out


def drawn_ramps(texts: Sequence[dict], building: dict, params: dict) -> list[dict]:
    """``[{"door_id", "text", "point", "evidence"}]``: ``RAMPA`` / ``RAMP`` texts outside the building within
    ``door_ground_reach`` of an outside door (the nearest)."""
    from wenart.levels import model as LMOD

    out = []
    cache: dict = {}
    for t in texts:
        if t.get("point") is None or not RAMP_RE.search(B.fold_ascii(t.get("text") or "").upper()):
            continue
        lid = t.get("level_id")
        if lid not in cache:
            rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid]
            outline = LMOD.level_outline(building, lid) if lid else []
            cache[lid] = (outline, _outside_doors(building, lid, rooms, outline))
        outline, doors = cache[lid]
        p = tuple(t["point"])
        if len(outline) >= 3 and G.point_in_polygon(p, outline):
            continue
        near = [(G.distance(p, d["face"]), d["id"]) for d in doors
                if G.distance(p, d["face"]) <= float(params["door_ground_reach"])]
        if near:
            out.append({"door_id": min(near)[1], "text": t.get("text"), "point": [round(p[0], 4), round(p[1], 4)],
                        "evidence": [dict(t.get("evidence") or {"file": "", "method": "vector", "confidence": 1.0})]})
    return out
