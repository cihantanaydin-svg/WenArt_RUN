"""The pipeline's furniture reading step (docs/milestone12.md §4.1 D7, contract §13.2; owner: track R).

Contract (frozen 10 Oct 2026): ``read_furniture(build, works) -> None`` is called by ``pipeline.run_project`` after
``levels.apply_levels`` and before the type inference. It moves non-furniture symbols (room-number circles, north
arrows, axis bubbles, section marks, door-swing arcs, dimension outlines, text frames) from
``building["furniture"]`` to ``building["symbols"]`` with kind and evidence; types pieces by block names, cluster
splits and context rules; fixes misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026); and leaves no
untyped piece built (``build: false`` + ``needs_review`` list in the report).

What, in order (each step deterministic, every change logged in the piece's evidence and the warnings):

1. **Symbols**: pieces the generic core marked (``details["symbol"]``: a room-number tag, a north arrow, a door
   swing, a piece drawn on door, text, area, axis or view-line layers; ``symbols.whole_symbol``) leave the furniture
   for ``building["symbols"]`` (``former_piece_id``, reason, evidence, the plan crop of its question when it was
   asked). The drawing outranks the AI passes (CLAUDE.md trust order): a room-number circle both passes called a
   floor lamp is a symbol, and the disagreement is a ``type_disagreement`` conflict. A column or decor
   (``details["not_furniture"]``) stays as a not-built piece (``inferred_as``; a column is still an obstacle). The
   symbols the re-read found inside clusters (``ex.report["symbols"]``) are added. A level mark still among the
   pieces (track L's ``apply_levels`` moves them first) is moved too, as ``level_mark``. A type the core's re-read
   set against the AI passes is a ``type_disagreement`` conflict. Copies of one block drawing in other inserts of
   the block (``copy_keys``) share their type or their symbol.
2. **Code typing first** (Milestone 13, docs/milestone13.md §3.0 K3, CLAUDE.md "an untyped drawn footprint is
   typed by code first"; build round 3, lead decision): ``infer.code_types`` (``type_by_code``: the same footprint
   in the twin room or on another level, the block name, the room's missing group member) runs before the context
   rules and before any AI, on a piece whose question waits too (``code_first``); such a piece is typed
   (``type_method`` twin | level | block | group_member, ``inferred`` with the evidence) and its question is
   withdrawn (``withdraw_questions``: the key leaves the page's ``pending`` and is listed under
   ``report["typed_by_code"]`` with its method in ``report["typed_by_code_methods"]``, ``build.code_typed`` /
   ``build.code_typed_methods``; the pipeline leaves it out of ``recognition/requests.json``).
   **Context typing** (the Milestone 12 rules, on what code left, the open questions too): an L outline with
   seat-deep arms in a living room is a corner sofa; an unknown box drawn with a door swing beside the counter run
   (or closing it, proud of it) is a fridge; a 0.5-0.75 m deep strip along a wall holding a sink or hob is a
   counter; two small squares at a bed's head are nightstands; a table-sized piece with seats drawn around it on
   two sides is a dining table, and small pieces at a dining table are chairs facing it; a bowl with a drain in a
   bathroom is a washbasin and the counter under it its vanity; two equal seats across a coffee table are
   armchairs; a table in front of a sofa is a coffee table; a long low strip at a wall facing a sofa is a TV unit.
   A piece a context rule types is code typed as well (method ``context:<type>``, ``context:vanity`` for the
   counter under a basin): its question is withdrawn too. The code typing runs again after the context rules
   (chains: the missing member of a group whose anchor a context rule typed) and the context rules once more.
   Every step up to here holds the open questions the same way in every mode (``open_questions``: a block copy
   never decides one, no front for it yet), and a question asked and answered in this round is never withdrawn
   (``answered_keys``), so the question count is the same with ``--no-ai``, in the first plain run and in the run
   with the answers (the AI types only what neither code nor the drawing's context explains). A fixed piece drawn
   inside another of its type is drawn twice (not built).
3. **Inference** (``wenart.furniture.infer``: size, room and position) for what is still unknown; a piece whose
   AI question still waits for its answers is left to them (the size and position rules are weaker than a plan
   crop; the code methods above apply there as well and withdraw as above). The context rules then type the
   partners of the anchors the inference typed (Milestone 12 behaviour: open questions wait, nothing is withdrawn,
   because with ``--no-ai`` the size inference types pieces a plain run leaves to the AI).
4. **Misread fixed equipment** (user OK 1 of 10 Oct 2026): a fixed piece whose drawn size is more than 30 % outside
   its type's real range gets the nearest real product size (``sizes.product_size``), its back kept on its wall; a
   fixed piece through a wall or in a door swing moves up to 0.5 m to the nearest free spot. ``drawn_type``,
   ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height`` are kept; ``adjusted_by_ai`` holds the reason, the
   changed fields and the plan crop; the piece's evidence gets the rule's entry.
5. **Fronts**: a drawn piece of a type with a front and none drawn gets one from the wall its back stands on or
   from its group (a chair faces its table, a nightstand the way its bed faces, a TV unit its sofa), ``inferred``.
6. **Open kitchens**: a room that is not a kitchen but holds kitchen fixtures gets a kitchen zone
   (``rooms[].zones``, contract §13.3) around them; the room-type rules apply per zone (track G).
7. **Never a box**: a piece still untyped is not built and listed in ``building["needs_review"]`` with its crop
   and reason (a piece whose question waits is not built and not listed: the pipeline lists the open questions).

Fix round after P3 (16-17 Oct 2026): only the questions of the pages the pipeline writes to ``requests.json`` (the
master of a level, a furniture plan that furnishes it) can be answered. A secondary page of a level (real04: the
second plan region r16 of the ground floor) numbers its candidates like the master (``sym_L0_001`` ...) and its
questions are never asked, so its report carries ``NOT_ASKED_KEY`` (set by ``pipeline._assemble_level``): nothing
waits for its questions (``_pending``, ``open_questions``), its items never stand for a piece the asked page drew
(``_items``: the asked page's item wins) and none of its keys is withdrawn (``withdraw_questions``). Before, a master
piece the second region drew too (f_L0_021, f_L0_024: both AI answers in the building) and the second region's own
pieces kept "waits for the answers" in the run with the answers, not built and missing from the review list.
``never_a_box`` also clears that reason on a piece that no longer waits (a building read again), so it is typed or
listed. A secondary page's crops live in its own folder (``details["crop_dir"]``, ``_crop``).

Fix round after P4b (17 Oct 2026; pod P4b, real03). What:

- **The code typing reads the first reading's building in every pass** (``code_first(build, reset)``). In the run with
  the answers, the pieces typed only because of this round's answers (``answer_typed``: an asked and answered
  question whose piece has a type when the reading starts, and the block copies ``copies`` typed from such a piece)
  are reset to ``unknown`` in a copy of the building before ``infer.code_types`` runs (``inferred_as: "answered"`` in
  that copy only, so code never types them). Only the proposals for pieces that are still untyped in the real
  building are applied: an AI type is never replaced by code, and a piece the AI left unknown is still typed by code
  as before. Without answers nothing is reset, so the first run and ``--no-ai`` are unchanged. Why: in P4b's run with
  the answers, the AI's bathtubs and showers filled the bath sets, so the rule "the bath set misses shower|bathtub"
  that typed six drawn symbols in the first reading (and withdrew their questions) no longer found the slot. The six
  stayed untyped, their questions were late (never asked), and the agent marked them as not furniture.
- **Type method of the context rules and the size inference**: a piece a context rule or a block copy types gets
  ``type_method: "rule"`` (a reading rule of the drawing; ``report["typed_by"]`` keeps ``context:<type>``); a piece
  the size inference types gets ``type_method: "inferred"`` (``mark_inferred``; ``pipeline._infer_types`` does the
  same). Both values are in the building schema. Before, both kept ``none``: P4b's 24 typed drawn pieces (6 corner
  sofas among them) counted as untyped in the final manifest.
- **A two-pass disagreement is decided by code** (``tie_break``, after the size inference): an untyped drawn piece
  whose two AI passes named two different furniture types, both fitting its drawn size and both allowed in its room,
  gets the one the room misses (``room_misses``: the missing members of its drawn groups and the anchors of its
  program's groups), else the one whose real product size is nearer. It is marked ``inferred`` with the reason and
  the plan crop (``type_method: "inferred"``, status ``unverified``), and the ``symbol_type_disagreement`` conflict
  stays in the report with this decision as its resolution. Why: real03's bedroom oda_01 draws a 1.5 x 0.6 m piece;
  Qwen said dresser, GLM said wardrobe, and the piece stayed an unbuilt unknown in a room with no storage (CLAUDE.md:
  the AI infers the type and marks it inferred; never an unexplained box).

Pass before P5 (17 Oct 2026). What: the tie-break decides twins together, and the code typing runs once more after
it. A disputed piece with the same footprint at the mirrored spot of a twin room (``_twins_of``: ``infer._twin_rooms``,
the centre within ``infer.SAME_CENTRE_M``, the size within ``infer.SAME_FOOTPRINT_M``) is decided with that twin,
when one of them at least could be decided alone (two answers that both fit; else they stay for review, as before):
when the AI passes of both name one type that fits the drawn size and both rooms, both get it (``TWIN_TIE_NOTE``);
else one of them is decided alone, so is a twin whose passes named that type, and the other twins wait for the twin
rule; a piece whose twin is already typed is left to the twin rule as well. Then, when the tie-break typed or left a
piece to its twin, ``code_first`` runs again (no reset: the AI's and the tie-break's types count) before the fronts and
the review list; ``withdraw_questions`` keeps a question asked and answered in this round listed and withdraws one
that was not (a late one), as ``pipeline._infer_types`` did right after this step before. Why: on P3's real04
building the tie-break typed f_L1_035 sideboard (sideboard / tv_unit) and left its mirror twin f_L1_033 (sideboard /
bench; a bench is not allowed in that room) untyped and listed for review until the pipeline's later inference; the
mirrored twins f_L1_034 (bookshelf / tv_unit) and f_L1_036 (bookshelf / console_table) got bookshelf and
console_table at the same drawn spot of the two mirrored flats. Now the tie-break types f_L1_033 sideboard and
f_L1_036 bookshelf (both twins named them); its 12 other decisions on that building are unchanged.
"""
from __future__ import annotations

import copy
import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G

SYMBOL_RULE = "reading.symbols"
CONTEXT_RULE = "reading.context"
FIXED_RULE = "reading.fixed_equipment"
FRONT_RULE = "reading.front"
ZONE_RULE = "reading.kitchen_zone"
CROP_DIR = "recognition/crops"
WALL_SIDE_M = 0.10                 # a side this close to the room outline stands on a wall
NIGHTSTAND_M = (0.30, 0.65)        # a nightstand-sized square ...
NIGHTSTAND_GAP_M = 0.35            # ... beside a bed (gap to its long side) ...
NIGHTSTAND_HEAD_M = 0.70           # ... within this of the head edge
COFFEE_FRONT_M = (0.20, 1.60)      # a coffee table stands this far in front of a sofa ...
TV_DISTANCE_M = (0.9, 6.0)         # a TV unit this far from the sofa's front ...
TV_AXIS_DEG = 25.0                 # ... within this of the sofa's axis ...
TV_DEPTH_M = (0.20, 0.65)          # ... a strip this deep ...
TV_LENGTH_M = (0.90, 2.60)         # ... and this long
COUNTER_DEPTH_M = (0.50, 0.75)     # a counter strip along a wall
FRIDGE_REACH_M = 0.30              # a box with a door this close to the kitchen run is the fridge
DOOR_NEAR_M = 0.15                 # a door swing symbol this close to a box is its door
MISREAD_SHARE = 0.30               # a fixed piece more than 30 % outside its real size range is misread
MOVE_MAX_M = 0.50                  # ... and may move this far to the nearest valid spot
MOVE_STEP_M = 0.05
THROUGH_WALL_M = 0.05              # a fixed piece reaching more than 5 cm past its room's outline is through a wall
SWING_SHARE = 0.05                 # ... and one with more than 5 % of its area in a door swing stands in it
ZONE_AISLE_M = 1.0                 # a kitchen zone: the kitchen pieces and the 1 m in front of them
KITCHEN_ZONE_TYPES = ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge", "tall_cabinet",
                      "wall_cabinet")
SEAT_TYPES = ("sofa", "sofa_corner")
# The back is a short side (a crib's front is a long side: track B's size table, the layout builds it so).
HEAD_TYPES = ("bed_double", "bed_single", "bunk_bed", "toilet")
CHAIR_SIDE_M = (0.30, 0.65)        # a chair (or its half-round back drawn alone) ...
CHAIR_REACH_M = 0.40               # ... this close to a dining table faces it
CHAIR_DEPTH_M = 0.45               # a chair drawn shallower (its back alone) reaches this deep towards the table
DINING_SEATS_MIN = 3               # a table-sized piece with this many seats around it (on two sides) is a dining table
ARMCHAIR_REACH_M = 0.60            # two equal seats this close to a coffee table, on opposite sides, are armchairs
VANITY_SHARE = 0.3                 # an unknown counter under >= 30 % of a washbasin is its vanity
DUPLICATE_SHARE = 0.6              # a fixed piece this much inside a block-named one of its type is drawn twice
L_SEAT_MIN_M = 0.65                # the arms of an L corner sofa are seat-deep (a counter's legs are 0.6 m)
EXPLAINED_AS = ("rug", "detail", "column", "decor")
# Fix round after P3 (16-17 Oct 2026): the extraction report key of a page whose recognition questions are never asked
# (``pipeline._assemble_level`` sets it on a secondary page of a level; its value says why), and the reason a piece
# whose question waits is not built (``never_a_box``).
NOT_ASKED_KEY = "questions_not_asked"
WAITS_REASON = "untyped: its AI question waits for the answers"
# Fix round after P4b (17 Oct 2026, module docstring): the code typing's view of a piece typed by this round's answers
# (never written to the building), the type methods of the context rules and of the size inference (both in the
# building schema's enum), and the rule of the two-pass tie-break.
ANSWERED_AS = "answered"
CONTEXT_METHOD = "rule"
INFER_METHOD = "inferred"
TIE_RULE = "reading.tie_break"
# Pass before P5 (17 Oct 2026, module docstring): the reason of a type both twins' AI passes named.
TWIN_TIE_NOTE = "the AI passes of its twin {twin} in the twin room {room} named it too: the twins get one type"


# --------------------------------------------------------------------------
# Small geometry helpers (building frame)
# --------------------------------------------------------------------------

def rect(item: dict) -> Polygon:
    """The footprint rectangle of a building piece."""
    return rect_fp(item["footprint"])


def rect_fp(fp: dict) -> Polygon:
    """The rectangle of a footprint ``{center, size, rotation_deg}``."""
    cx, cy = (float(v) for v in fp["center"])
    w, d = (float(v) for v in fp["size"][:2])
    t = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(t), math.sin(t)
    pts = [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2),
                                                                 (-w / 2, d / 2))]
    poly = Polygon(pts)
    return poly if poly.area > 0 else poly.buffer(1e-4)


def front_vec(front_deg: float) -> tuple[float, float]:
    return math.cos(math.radians(front_deg)), math.sin(math.radians(front_deg))


def snap_front(item: dict, deg: float) -> float:
    """``deg`` snapped to the nearest of the footprint's four side normals."""
    base = G.front_direction_deg(float(item["footprint"].get("rotation_deg") or 0.0))
    k = round(G.normalise_angle(deg - base) / 90.0) % 4
    return round(G.normalise_angle(base + 90.0 * k), 3)


def sides(poly: Polygon) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    c = list(poly.exterior.coords)
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def wall_sides(item: dict, ring) -> list[int]:
    """Indices of the footprint sides lying on the room outline (within ``WALL_SIDE_M`` at 20 %, 50 %, 80 %)."""
    out = []
    for k, (a, b) in enumerate(sides(rect(item))):
        pts = [(a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t) for t in (0.2, 0.5, 0.8)]
        if all(ring.distance(Point(p)) <= WALL_SIDE_M for p in pts):
            out.append(k)
    return out


def outward_deg(item: dict, side) -> float:
    cx, cy = item["footprint"]["center"]
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    return math.degrees(math.atan2(my - cy, mx - cx)) % 360.0


def room_ring(room: dict):
    poly = Polygon(room["polygon"])
    poly = poly if poly.is_valid else poly.buffer(0)
    return poly.exterior if poly.geom_type == "Polygon" else max(poly.geoms, key=lambda g: g.area).exterior


def _ev(item: dict, rule: str, text: str, confidence: float = 0.7, method: str = "inferred") -> dict:
    src = (item.get("evidence") or [{}])[0]
    ev = B.evidence(src.get("file") or "building.json", method, confidence, rule=rule, text=text)
    for k in ("page", "entity", "region_id"):
        if src.get(k) is not None:
            ev[k] = src[k]
    return ev


def _crop(item_details: Optional[dict]) -> Optional[str]:
    """The plan crop of a piece's question (``recognition/crops/<key>_ctx.png``). Fix round after P3: a secondary
    page's crops are in its own folder (``details["crop_dir"]``, set by the pipeline), never the asked page's crop
    of the same key."""
    key = (item_details or {}).get("candidate_key")
    return f"{(item_details or {}).get('crop_dir') or CROP_DIR}/{key}_ctx.png" if key else None


def _not_asked(w) -> bool:
    """Fix round after P3: True for a page whose questions are never asked (``NOT_ASKED_KEY`` in its report)."""
    report = getattr(getattr(w, "extraction", None), "report", None)
    return isinstance(report, dict) and bool(report.get(NOT_ASKED_KEY))


def _works(build, works: dict, asked_only: bool = False) -> list:
    """The page works of a reading run, each once (``works`` and ``build.generic``). Fix round after P3: the pages whose
    questions are never asked come first (so an asked page's item wins in ``_items``), or are left out
    (``asked_only``)."""
    out, seen = [], set()
    for w in list((works or {}).values()) + list(getattr(build, "generic", []) or []):
        if id(w) in seen:
            continue
        seen.add(id(w))
        out.append(w)
    if asked_only:
        return [w for w in out if not _not_asked(w)]
    return sorted(out, key=lambda w: 0 if _not_asked(w) else 1)


def _items(build, works: dict, asked_only: bool = False) -> dict:
    """Building piece id -> the core's FurnitureItem (its ``details`` carry what the strokes said). Fix round after
    P3: a piece two pages drew maps to the item of the page whose questions are asked (the master), not to the
    secondary page's item of the same piece (another candidate key, another crop); ``asked_only`` leaves the
    secondary pages out."""
    out = {}
    for w in _works(build, works, asked_only):
        for f in getattr(w.extraction, "furniture", []) or []:
            if getattr(f, "element_id", None):
                out[f.element_id] = f
    return out


def _pending(build, works: dict) -> set[str]:
    """Pieces whose AI question still waits for its answers: nothing is decided for them before. A page that got
    answers in this round waits for none of its questions (a question without answers there was not asked in that
    round: the pipeline lists it as unanswered, nothing waits for it). Fix round after P3: a page whose questions
    are never asked (``NOT_ASKED_KEY``: a secondary page of its level) waits for none of them either."""
    out = set()
    for w in _works(build, works, asked_only=True):
        report = w.extraction.report or {}
        if report.get("answers_applied"):
            continue
        pending = set(report.get("pending") or [])
        for f in getattr(w.extraction, "furniture", []) or []:
            if f.details.get("candidate_key") in pending and getattr(f, "element_id", None):
                out.add(f.element_id)
    return out


def _next_symbol_id(b: dict, level_id: str) -> str:
    used = {s.get("id") for s in b.get("symbols") or []}
    n = sum(1 for s in b.get("symbols") or [] if s.get("level_id") == level_id) + 1
    while f"sy_{level_id}_{n:03d}" in used:
        n += 1
    return f"sy_{level_id}_{n:03d}"


def _room_at(b: dict, level_id: str, point) -> Optional[str]:
    pt = Point(point)
    for r in b.get("rooms") or []:
        if r.get("level_id") == level_id and len(r.get("polygon") or []) >= 3 and Polygon(r["polygon"]).contains(pt):
            return r["id"]
    return None


# --------------------------------------------------------------------------
# 1. Symbols
# --------------------------------------------------------------------------

def move_symbols(build, items: dict, works: dict) -> dict:
    """Step 1 (see the module docstring). Returns counts by kind."""
    from wenart.levels import marks as LM

    b = build.building
    b.setdefault("symbols", [])
    counts: dict[str, int] = {}
    keep = []
    for f in b["furniture"]:
        item = items.get(f["id"])
        det = item.details if item is not None else {}
        found = det.get("symbol")
        if found is None and f["type"] == "unknown" and _is_mark(f, det, LM):
            found = {"kind": "level_mark", "reason": "a level mark among the furniture (the level step did not take "
                                                    "it): never furniture"}
        nf = det.get("not_furniture")
        if found is None and nf is not None:
            keep.append(f)
            if f.get("build") is not False:
                f["build"] = False
                f["inferred"] = True
                f["inferred_as"] = nf["as"]
                f["inferred_reason"] = nf["reason"] + (" (kept as an obstacle, not built)" if nf["as"] == "column"
                                                       else " (the decor stage places decor)")
                f.setdefault("evidence", []).append(_ev(f, SYMBOL_RULE, f["inferred_reason"]))
                build.warn(f"{f['id']}: not furniture ({nf['as']}): {nf['reason']}; not built")
                counts[nf["as"]] = counts.get(nf["as"], 0) + 1
            continue
        if found is None:
            keep.append(f)
            continue
        sym_id = _next_symbol_id(b, f["level_id"])
        reason = found["reason"]
        if f["type"] != "unknown" and f.get("type_method") == "ai_two_pass":
            reason += f" (both AI passes said {f['type']}: the drawing outranks them)"
            build.conflict("type_disagreement", [sym_id],
                           f"{f['id']}: the AI passes typed it {f['type']}, the drawing shows a {found['kind']} "
                           f"({found['reason']})", "moved to building.symbols (trust order: vector geometry > AI)")
        b["symbols"].append({"id": sym_id, "kind": found["kind"], "level_id": f["level_id"],
                             "room_id": f.get("room_id"), "footprint": copy.deepcopy(f["footprint"]),
                             "former_piece_id": f["id"], "reason": reason, "crop": _crop(det),
                             "evidence": list(f.get("evidence") or []) + [_ev(f, SYMBOL_RULE, reason, 0.9)]})
        build.warn(f"{f['id']}: not furniture ({found['kind']}): {reason}; moved to the symbols ({sym_id})")
        counts[found["kind"]] = counts.get(found["kind"], 0) + 1
    b["furniture"] = keep
    for w in list(getattr(build, "furniture_works", []) or []):
        ex = w.extraction
        level_id = ex.level_id
        for sym in (ex.report or {}).get("symbols") or []:
            if sym.get("_moved"):
                continue
            sym["_moved"] = True
            sym_id = _next_symbol_id(b, level_id)
            b["symbols"].append({"id": sym_id, "kind": sym["kind"], "level_id": level_id,
                                 "room_id": _room_at(b, level_id, sym["center"]),
                                 "footprint": {"center": list(sym["center"]), "size": list(sym["size"]),
                                               "rotation_deg": sym["rotation_deg"]},
                                 "former_piece_id": None, "reason": sym["reason"], "crop": None,
                                 "evidence": list(sym["evidence"])})
            counts[sym["kind"]] = counts.get(sym["kind"], 0) + 1
    return counts


def log_overrides(build, items: dict) -> int:
    """The core's re-read typed a piece against the AI passes (a block name the M12 words read, a table with chairs
    drawn around it): a ``type_disagreement`` conflict, resolved for the drawing (CLAUDE.md trust order)."""
    n = 0
    for f in build.building["furniture"]:
        item = items.get(f["id"])
        over = (item.details.get("ai_overridden") if item is not None else None) or {}
        if not over:
            continue
        build.conflict("type_disagreement", [f["id"]],
                       f"{f['id']}: the AI passes typed it {over['type']}; {over['reason']}",
                       f"typed {f['type']} (trust order: vector geometry and block names > AI)")
        n += 1
    return n


def _is_mark(f: dict, det: dict, LM) -> bool:
    raw = f.get("type_raw") or ""
    if any(LM.parse_mark(part) for part in raw.split("/") if part):
        return True
    return False


# --------------------------------------------------------------------------
# 1b. Copies of one block drawing
# --------------------------------------------------------------------------

def copies(build, items: dict, pending=(), typed_from: Optional[dict] = None) -> int:
    """Pieces drawn by the same entities of the same block definition in different inserts of it (``copy_keys``:
    real03's four 1+1 B flats are one block inserted four times) are the same piece: an untyped copy takes the type
    its typed copies agree on, and a copy of symbols becomes a symbol too. Returns the number of pieces changed.
    Fix round after P4b: ``typed_from`` (a dict) receives ``{typed copy id: [the ids of the copies it took its type
    from]}`` (``code_first`` resets a copy of a piece the answers typed)."""
    b = build.building
    groups: dict[str, list[str]] = {}
    for pid, item in sorted(items.items()):
        for key in item.details.get("copy_keys") or []:
            groups.setdefault(key, []).append(pid)
    by_id = {f["id"]: f for f in b["furniture"]}
    sym_of = {s.get("former_piece_id"): s for s in b.get("symbols") or [] if s.get("former_piece_id")}
    changed = 0
    for key in sorted(groups):
        ids = groups[key]
        if len(ids) < 2:
            continue
        typed = [by_id[i] for i in ids if i in by_id and by_id[i]["type"] != "unknown"
                 and by_id[i].get("build") is not False]
        loose = [by_id[i] for i in ids if i in by_id and by_id[i]["type"] == "unknown"
                 and by_id[i].get("build") is not False and i not in pending]
        syms = [sym_of[i] for i in ids if i in sym_of]
        if not loose:
            continue
        if syms and not typed and len({s["kind"] for s in syms}) == 1:
            former = ", ".join(sorted(s["former_piece_id"] for s in syms))
            for f in loose:
                det = items[f["id"]].details
                det["symbol"] = {"kind": syms[0]["kind"],
                                 "reason": f"drawn by the same block entities as {former} ({syms[0]['kind']}): "
                                           f"{syms[0]['reason']}"}
                changed += 1
            continue
        kinds = {f["type"] for f in typed}
        if len(kinds) != 1:
            continue
        ftype = kinds.pop()
        mates = ", ".join(sorted(t["id"] for t in typed))
        for f in loose:
            if not _same_size(f, typed[0], 0.02):
                continue
            _set_type(build, f, ftype, f"drawn by the same block entities as {mates} (typed {ftype}): the same "
                      "piece in another insert of the block", confidence=0.8)
            if typed_from is not None:
                typed_from[f["id"]] = sorted(t["id"] for t in typed)
            changed += 1
    if changed:
        move_symbols(build, items, {})
    return changed


# --------------------------------------------------------------------------
# 2. Context typing
# --------------------------------------------------------------------------

def _set_type(build, f: dict, ftype: str, reason: str, front: Optional[float] = None,
              confidence: float = 0.75) -> None:
    from wenart.furniture import infer as INF

    # Typed from its neighbours: an inference (CLAUDE.md), so the piece keeps its ``status`` and carries ``inferred``
    # with its reason (listed in the report). Fix round after P4b: an untyped piece's ``type_method`` becomes
    # ``CONTEXT_METHOD`` (a reading rule of the drawing), so the rules keyed on the method see it typed.
    old = f["type"]
    f["type"] = ftype
    if f.get("type_method") in (None, "none"):
        f["type_method"] = CONTEXT_METHOD
    f["inferred"] = True
    f["inferred_reason"] = reason
    f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason, confidence))
    if front is not None:
        INF.set_front(f, front)
    build.warn(f"{f['id']}: {old} -> {ftype} by context: {reason}")


def _unknowns(pieces: list[dict], pending=()) -> list[dict]:
    """The pieces a context rule may type: unknown, built, drawn, and not in ``pending``. Build round 3 (K3, lead
    decision): the passes of ``read_furniture`` before the size inference give no pending set: a context rule is
    code and types a piece whose AI question still waits as well (the question is then withdrawn,
    ``context_typed``); the last pass, after the size inference, keeps the Milestone 12 behaviour (``pending``
    waits, nothing is withdrawn)."""
    return [f for f in pieces if f["type"] == "unknown" and f.get("build") is not False
            and f.get("source", "from_documents") == "from_documents" and f["id"] not in pending]


def context_typed(build, before: dict) -> dict[str, str]:
    """Build round 3 (K3): the pieces a ``context_types`` pass typed, ``{piece id: "context:<type>"}``, from the
    unknown pieces ``before`` the pass (``unknown_ids``: id -> piece): a piece that now has a type, or that the pass
    recorded as a detail of another piece (the counter under a washbasin: ``context:vanity``). The caller withdraws
    their questions like the code-typed ones."""
    out = {}
    for f in build.building["furniture"]:
        if f["id"] not in before:
            continue
        if f.get("type") != "unknown":
            out[f["id"]] = f"context:{f['type']}"
        elif f.get("build") is False and f.get("inferred_as") == "detail":
            out[f["id"]] = "context:vanity"
    return out


def unknown_ids(build) -> dict[str, dict]:
    """The unknown drawn built pieces before a typing pass (for ``context_typed``)."""
    return {f["id"]: f for f in _unknowns(build.building["furniture"])}


def _facing(seat: dict, other: Polygon) -> Optional[tuple[float, float, float]]:
    """(distance from the seat's front edge, lateral offset, angle off the axis in deg) of ``other`` seen from the
    seat's front, or None when the seat has no front or ``other`` lies behind it."""
    if seat.get("front_deg") is None:
        return None
    fx, fy = front_vec(float(seat["front_deg"]))
    cx, cy = seat["footprint"]["center"]
    depth = float(seat["footprint"]["size"][1])
    o = other.centroid
    dx, dy = o.x - cx, o.y - cy
    along = dx * fx + dy * fy - depth / 2.0
    across = -dx * fy + dy * fx
    if along <= 0:
        return None
    return along, across, abs(math.degrees(math.atan2(across, along + depth / 2.0)))


def context_types(build, items: dict, pending=()) -> dict:
    """Step 2 (see the module docstring). Returns counts by rule."""
    from wenart.furniture import sizes

    b = build.building
    counts: dict[str, int] = {}

    def bump(k):
        counts[k] = counts.get(k, 0) + 1

    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    for rid, room in sorted(rooms.items()):
        pieces = [f for f in b["furniture"] if f.get("room_id") == rid]
        if not pieces:
            continue
        ring = room_ring(room)
        built = [f for f in pieces if f.get("build") is not False]
        # Corner sofa: an L outline with seat-deep arms (0.65-1.3 m, generic core ``l_shape``) in a living room, not
        # touching the kitchen run (a counter is an L of 0.6 m deep legs).
        kitchen = [f for f in built if f["type"] in KITCHEN_ZONE_TYPES]
        for f in _unknowns(pieces, pending):
            det = items[f["id"]].details if f["id"] in items else {}
            lo = det.get("l_outline")
            if lo and room.get("room_type") == "living" and sizes.fits("sofa_corner", tuple(f["footprint"]["size"])) \
                    and min(lo["seat_depth"], lo["chaise_width"]) >= L_SEAT_MIN_M and not any(
                        rect(k).distance(rect(f)) <= 0.15 for k in kitchen):
                front = det.get("l_front")
                _set_type(build, f, "sofa_corner", "an L outline with 0.5-1.3 m deep arms in a living room (a corner "
                          "sofa; the open inner corner is its front)", float(front) if front is not None else None)
                f.update(shape="L", chaise_side=lo["chaise_side"], chaise_depth=lo["chaise_depth"],
                         seat_depth=lo["seat_depth"], chaise_width=lo["chaise_width"])
                bump("sofa_corner")
        # Fridge: a box drawn with its door swing beside the kitchen run.
        kitchen = [f for f in built if f["type"] in ("kitchen_counter", "sink_kitchen", "stove", "kitchen_island")]
        doors = [rect_fp(s["footprint"]) for s in b.get("symbols") or [] if s.get("kind") == "door_arc"
                 and s.get("room_id") == rid and s.get("footprint")]
        legs = [k for k in kitchen if k["type"] == "kitchen_counter"]
        for f in _unknowns(pieces, pending):
            det = items[f["id"]].details if f["id"] in items else {}
            poly = rect(f)
            if not (kitchen and sizes.fits("fridge", tuple(f["footprint"]["size"]))):
                continue
            door = det.get("door") or any(d.distance(poly) <= DOOR_NEAR_M for d in doors)
            depth = min(f["footprint"]["size"])
            proud = [k for k in legs if poly.distance(rect(k)) <= 0.10 and
                     depth >= min(k["footprint"]["size"]) + 0.05]
            why = None
            if door and min(poly.distance(rect(k)) for k in kitchen) <= FRIDGE_REACH_M:
                why = "a box drawn with its door swing beside the kitchen run (a fridge)"
            elif proud and wall_sides(f, ring):
                why = (f"a {depth:.2f} m deep box at a wall closing the counter run {proud[0]['id']} and standing "
                       "proud of it (a fridge)")
            if why:
                near = wall_sides(f, ring)
                front = (outward_deg(f, sides(poly)[near[0]]) + 180.0) % 360.0 if len(near) == 1 else None
                _set_type(build, f, "fridge", why, snap_front(f, front) if front is not None else None)
                bump("fridge")
        # Counter: a 0.5-0.75 m deep strip along a wall holding a sink or a hob.
        fixtures = [f for f in built if f["type"] in ("sink_kitchen", "stove")]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (COUNTER_DEPTH_M[0] <= d <= COUNTER_DEPTH_M[1] and w >= 0.9):
                continue
            near = wall_sides(f, ring)
            poly = rect(f)
            held = [x for x in fixtures if rect(x).intersection(poly).area >= 0.5 * rect(x).area]
            long_sides = [k for k in near if abs(math.dist(*sides(poly)[k]) - w) < 1e-3]
            if held and long_sides:
                front = (outward_deg(f, sides(poly)[long_sides[0]]) + 180.0) % 360.0
                _set_type(build, f, "kitchen_counter", f"a {d:.2f} m deep strip along the wall holding "
                          f"{', '.join(x['id'] for x in held)}: the counter run", snap_front(f, front))
                bump("kitchen_counter")
        # Nightstands: small squares beside a bed's head.
        beds = [f for f in built if f["type"] in ("bed_double", "bed_single") and f.get("front_deg") is not None]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (NIGHTSTAND_M[0] / 1.15 <= d and w <= NIGHTSTAND_M[1] * 1.15):
                continue
            for bed in beds:
                where = _beside_head(bed, rect(f))
                if where is not None:
                    _set_type(build, f, "nightstand", f"a {w:.2f} x {d:.2f} m square beside the head of {bed['id']}",
                              snap_front(f, float(bed["front_deg"])))
                    bump("nightstand")
                    break
        # Dining table: a table-sized piece with seat-sized pieces drawn around it on two or more of its sides
        # (docs/milestone12.md §4.1: "chairs around a rectangle -> dining table + chairs"; real01 --no-ai).
        for f in _unknowns(pieces, pending):
            if not sizes.fits("table_dining", tuple(f["footprint"]["size"])):
                continue
            poly = rect(f)
            seats = [g for g in _unknowns(pieces, pending) if g is not f and _seat_sized(g)
                     and rect(g).distance(poly) <= CHAIR_REACH_M]
            sides_hit = {_side_of(f, rect(g)) for g in seats}
            if len(seats) >= DINING_SEATS_MIN and len(sides_hit) >= 2:
                _set_type(build, f, "table_dining", f"a {f['footprint']['size'][0]:.2f} x "
                          f"{f['footprint']['size'][1]:.2f} m table with {len(seats)} seats drawn around it on "
                          f"{len(sides_hit)} sides: a dining table")
                bump("table_dining")
        built = [f for f in pieces if f.get("build") is not False]
        # Chairs: small pieces (a seat, or the half-round back drawn alone) around a dining table face it.
        tables = [f for f in built if f["type"] in ("table_dining", "kitchen_island")]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (CHAIR_SIDE_M[0] <= w <= CHAIR_SIDE_M[1] and d >= 0.12):
                continue
            poly = rect(f)
            near = [t for t in tables if rect(t).distance(poly) <= CHAIR_REACH_M]
            if not near:
                continue
            host = min(near, key=lambda t: (round(rect(t).distance(poly), 6), t["id"]))
            c = rect(host).centroid
            deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
            _set_type(build, f, "chair", f"a {w:.2f} x {d:.2f} m seat {rect(host).distance(poly):.2f} m from the table "
                      f"{host['id']}, facing it", snap_front(f, deg))
            depth = float(f["footprint"]["size"][1])
            if depth < CHAIR_DEPTH_M:
                # The half-round back drawn alone: the seat reaches towards the table (as the M11 chair split).
                fx, fy = front_vec(float(f["front_deg"]))
                shift = (CHAIR_DEPTH_M - depth) / 2.0
                cx, cy = f["footprint"]["center"]
                f["footprint"] = dict(f["footprint"], center=[round(cx + fx * shift, 4), round(cy + fy * shift, 4)],
                                      size=[f["footprint"]["size"][0], CHAIR_DEPTH_M])
            bump("chair")
        # Washbasin: a bowl with its drain in a bathroom or WC; the counter (vanity) it stands on is part of it.
        if room.get("room_type") in ("bathroom", "wc"):
            for f in _unknowns(pieces, pending):
                det = items[f["id"]].details if f["id"] in items else {}
                if det.get("drain") and sizes.fits("washbasin", tuple(f["footprint"]["size"])):
                    _set_type(build, f, "washbasin", "a bowl with its drain in a bathroom: the washbasin")
                    bump("washbasin")
            basins = [f for f in pieces if f["type"] == "washbasin" and f.get("build") is not False]
            for f in _unknowns(pieces, pending):
                poly = rect(f)
                host = next((x for x in basins if poly.intersection(rect(x)).area >= VANITY_SHARE *
                             min(poly.area, rect(x).area)), None)
                w, d = sorted(f["footprint"]["size"], reverse=True)
                if host is not None and d <= 0.7:
                    reason = (f"the counter the washbasin {host['id']} stands on (a vanity): part of it, not a piece "
                              "of its own (not built)")
                    f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason)
                    f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason))
                    build.warn(f"{f['id']}: {reason}")
                    bump("vanity")
        # Armchairs: two seat-sized pieces of one size on opposite sides of a coffee table face it.
        coffee = [f for f in pieces if f["type"] == "table_coffee" and f.get("build") is not False]
        for t in coffee:
            tp = rect(t)
            near = [f for f in _unknowns(pieces, pending) if sizes.fits("armchair", tuple(f["footprint"]["size"]))
                    and rect(f).distance(tp) <= ARMCHAIR_REACH_M]
            for f in near:
                c, fc = tp.centroid, rect(f).centroid
                mate = next((g for g in near if g is not f and _same_size(f, g) and
                             ((g["footprint"]["center"][0] - c.x) * (fc.x - c.x) +
                              (g["footprint"]["center"][1] - c.y) * (fc.y - c.y)) < 0), None)
                if mate is None or f["type"] != "unknown":
                    continue
                for g in (f, mate):
                    if g["type"] != "unknown":
                        continue
                    gc = rect(g).centroid
                    deg = math.degrees(math.atan2(c.y - gc.y, c.x - gc.x))
                    _set_type(build, g, "armchair", f"one of two {g['footprint']['size'][0]:.2f} x "
                              f"{g['footprint']['size'][1]:.2f} m seats on opposite sides of the coffee table "
                              f"{t['id']}, facing it", snap_front(g, deg))
                    bump("armchair")
        # Coffee table and TV unit: in front of a sofa (or in the open corner of an L sofa).
        seats = [f for f in built if f["type"] in SEAT_TYPES and f.get("front_deg") is not None]
        for f in _unknowns(pieces, pending):
            size = tuple(f["footprint"]["size"])
            poly = rect(f)
            notch = next((s for s in seats if s.get("shape") == "L" and sizes.fits("table_coffee", size) and
                          poly.intersection(rect(s)).area >= 0.4 * poly.area and
                          poly.intersection(_l_body(s)).area <= 0.2 * poly.area), None)
            if notch is not None:
                _set_type(build, f, "table_coffee", f"a {size[0]:.2f} x {size[1]:.2f} m table in the open corner of "
                          f"the L sofa {notch['id']}")
                bump("table_coffee")
                continue
            for seat in seats:
                rel = _facing(seat, poly)
                if rel is None:
                    continue
                along, across, angle = rel
                half = float(seat["footprint"]["size"][0]) / 2.0
                if sizes.fits("table_coffee", size) and COFFEE_FRONT_M[0] <= along - min(size) / 2 <= \
                        COFFEE_FRONT_M[1] and abs(across) <= half:
                    _set_type(build, f, "table_coffee", f"a {size[0]:.2f} x {size[1]:.2f} m table {along:.2f} m in "
                              f"front of {seat['id']}")
                    bump("table_coffee")
                    break
                w, d = sorted(size, reverse=True)
                near = wall_sides(f, ring)
                if (TV_DEPTH_M[0] <= d <= TV_DEPTH_M[1] and TV_LENGTH_M[0] <= w <= TV_LENGTH_M[1] and near and
                        TV_DISTANCE_M[0] <= along <= TV_DISTANCE_M[1] and angle <= TV_AXIS_DEG):
                    back = sides(poly)[near[0]]
                    front = (outward_deg(f, back) + 180.0) % 360.0
                    _set_type(build, f, "tv_unit", f"a {w:.2f} x {d:.2f} m strip at the wall facing {seat['id']} "
                              f"{along:.2f} m away", snap_front(f, front))
                    bump("tv_unit")
                    break
    return counts


def _seat_sized(f: dict) -> bool:
    w, d = sorted(f["footprint"]["size"], reverse=True)
    return CHAIR_SIDE_M[0] <= w <= CHAIR_SIDE_M[1] and d >= 0.12


def _side_of(table: dict, poly: Polygon) -> int:
    """Which side of ``table`` (0 front -Y, 1 right +X, 2 back +Y, 3 left -X in its own frame) ``poly`` is at."""
    cx, cy = table["footprint"]["center"]
    w, d = (float(v) for v in table["footprint"]["size"][:2])
    t = math.radians(float(table["footprint"].get("rotation_deg") or 0.0))
    dx, dy = poly.centroid.x - cx, poly.centroid.y - cy
    lx, ly = dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t)
    if abs(lx) / max(w / 2.0, 1e-6) >= abs(ly) / max(d / 2.0, 1e-6):
        return 1 if lx > 0 else 3
    return 2 if ly > 0 else 0


def _same_size(f: dict, g: dict, tol: float = 0.05) -> bool:
    a, b_ = sorted(f["footprint"]["size"]), sorted(g["footprint"]["size"])
    return all(abs(x - y) <= tol + 1e-9 for x, y in zip(a, b_))


def _l_body(seat: dict) -> Polygon:
    """The two arms of an L corner sofa (``schemas.l_parts``) as one polygon, building frame; its box without one."""
    from wenart.furniture import schemas

    fp = seat["footprint"]
    parts = schemas.l_parts(fp["size"], seat.get("chaise_side"), seat.get("chaise_depth"), seat.get("seat_depth"),
                            seat.get("chaise_width"))
    cx, cy = (float(v) for v in fp["center"])
    t = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(t), math.sin(t)
    polys = []
    for x0, x1, y0, y1 in parts:
        polys.append(Polygon([(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((x0, y0), (x1, y0), (x1, y1),
                                                                                    (x0, y1))]))
    return unary_union(polys)


def _beside_head(bed: dict, poly: Polygon) -> Optional[str]:
    """'left' / 'right' when ``poly`` stands beside the bed's head (within ``NIGHTSTAND_GAP_M`` of a long side and
    ``NIGHTSTAND_HEAD_M`` of the head edge), else None."""
    fx, fy = front_vec(float(bed["front_deg"]))
    cx, cy = bed["footprint"]["center"]
    w, d = (float(v) for v in bed["footprint"]["size"][:2])
    o = poly.centroid
    dx, dy = o.x - cx, o.y - cy
    along = dx * fx + dy * fy              # + towards the foot
    across = -dx * fy + dy * fx
    head = -d / 2.0
    if not (head - 0.1 <= along <= head + NIGHTSTAND_HEAD_M):
        return None
    gap = abs(across) - w / 2.0
    if gap < -0.05 or gap > NIGHTSTAND_GAP_M + 0.35:
        return None
    if poly.distance(rect(bed)) > NIGHTSTAND_GAP_M:
        return None
    return "left" if across > 0 else "right"


def duplicates(build) -> int:
    """Two fixed pieces of one type where one lies >= 60 % inside the other are one piece drawn twice (real03: the hob
    inside the OCAK block, typed stove by both passes; the dishwasher block inside the counter leg): the one that
    goes is the smaller, or of two about equal ones (area within 30 %) the one not named by its block. Not built
    (``detail``). Returns the number of duplicates."""
    from wenart.furniture import schemas

    b = build.building
    pieces = [f for f in b["furniture"] if f.get("build") is not False and f["type"] in schemas.FIXED_TYPES
              and f["type"] != "stair"]
    n = 0
    for f in pieces:
        if f.get("build") is False:
            continue
        poly = rect(f)
        host = None
        for h in pieces:
            if h is f or h.get("build") is False or h["type"] != f["type"] or h.get("room_id") != f.get("room_id"):
                continue
            if poly.intersection(rect(h)).area < DUPLICATE_SHARE * poly.area:
                continue
            ha, fa = rect(h).area, poly.area
            similar = max(ha, fa) <= 1.3 * min(ha, fa)
            named_h = h.get("type_method") == "block_name"
            named_f = f.get("type_method") == "block_name"
            if (similar and named_h and not named_f) or (not similar and ha > fa) or \
                    (similar and named_h == named_f and h["id"] < f["id"]):
                host = h
                break
        if host is None:
            continue
        reason = (f"drawn inside the {host['type']} {host['id']} ({DUPLICATE_SHARE:.0%} or more of it): the same "
                  "piece drawn twice, or a part of it (not built)")
        f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason)
        f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason, 0.8))
        build.warn(f"{f['id']}: {reason}")
        n += 1
    return n


# --------------------------------------------------------------------------
# 3. Inference
# --------------------------------------------------------------------------

def infer(build, pending: set[str]) -> tuple[int, list[str]]:
    """Step 3: ``wenart.furniture.infer`` on what is still unknown (the conflicts read so far count: a face holding
    two room names allows the types of both). Returns ``(proposals applied, ids typed by code)``.

    Milestone 13 (K3, "code first, the AI types the rest"): a code-typed proposal (``type_method`` in
    ``infer.CODE_TYPE_METHODS``) needs no AI answer, so it applies to a piece whose question still waits as well; the
    size / room / position rules keep waiting for the answers (``pending``). The caller withdraws the questions of
    the code-typed pieces (``withdraw_questions``)."""
    from wenart.furniture import infer as INF

    b = build.building
    view = dict(b, conflicts=list(b.get("conflicts") or []) + list(getattr(build, "raw_conflicts", []) or []))
    proposals = [p for p in INF.infer_types(view)
                 if p["piece_id"] not in pending or p.get("type_method") in INF.CODE_TYPE_METHODS]
    if not proposals:
        return 0, []
    b["furniture"] = INF.apply_inferences(b, proposals)["furniture"]
    mark_inferred(b, proposals)
    coded = []
    for p in proposals:
        if p.get("type_method") in INF.CODE_TYPE_METHODS:
            what = f"typed {p['type']} by code ({p['type_method']}, before any AI)"
            coded.append(p["piece_id"])
        else:
            what = "not built (rug or group outline)" if p.get("build") is False else f"inferred {p['type']}"
        build.warn(f"{p['piece_id']}: {what}: {p['reason']}")
    return len(proposals), coded


def mark_inferred(b: dict, proposals: list[dict]) -> int:
    """Fix round after P4b (module docstring): a piece the size inference typed (a proposal of
    ``infer.infer_types`` that is neither a code method nor a nightstand symbol, and that gave a furniture type)
    gets ``type_method: INFER_METHOD`` when it had none. Returns the number of pieces marked."""
    from wenart.furniture import infer as INF

    by_id = {f["id"]: f for f in b.get("furniture") or []}
    n = 0
    for p in proposals:
        if p.get("type_method") is not None or p.get("build") is False:
            continue
        f = by_id.get(p["piece_id"])
        if f is None or f.get("type") != p.get("type") or f.get("inferred_as"):
            continue
        if f.get("type_method") in (None, "none") and p.get("type") not in (None, "unknown", INF.OUTLINE_TYPE):
            f["type_method"] = INFER_METHOD
            n += 1
    return n


CODE_TYPED_KEY = "typed_by_code"      # the extraction report's list of question keys withdrawn by the code typing
CODE_METHODS_KEY = "typed_by_code_methods"   # ... and {key: method} (twin | level | block | group_member | context:<type>)


def answer_typed(build, works: dict, items: dict, typed_from: Optional[dict] = None) -> set[str]:
    """Fix round after P4b (module docstring): the pieces typed only because of this round's answers: a piece of an
    asked page whose question was asked and answered in this round (``answered_keys``) and that has a type now, and
    (``typed_from``, from ``copies``) the block copies typed from such a piece. Empty without answers."""
    answered = answered_keys(build, works)
    if not answered:
        return set()
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    asked = _items(build, works, asked_only=True)
    out = {pid for pid, item in asked.items() if str((item.details or {}).get("candidate_key")) in answered
           and (by_id.get(pid) or {}).get("type") not in (None, "unknown")}
    for pid, sources in sorted((typed_from or {}).items()):
        if set(sources) & out:
            out.add(pid)
    return out


def _first_reading_view(b: dict, reset) -> dict:
    """A copy of ``b`` where every piece in ``reset`` is untyped again, as the first reading saw it (``ANSWERED_AS``:
    code never types it in the copy)."""
    view = copy.deepcopy(b)
    for f in view.get("furniture") or []:
        if f.get("id") in reset:
            f.update(type="unknown", type_method="none", inferred_as=ANSWERED_AS)
    return view


def code_first(build, reset=()) -> tuple[list[str], dict[str, str]]:
    """Build round 3 (K3, lead decision): ``infer.code_types`` applied to the building before the context rules and
    before any AI (the twin room, another level, the block name, the room's missing group member), on every untyped
    drawn piece, the ones whose question waits included (code needs no answer). Returns the typed ids and
    ``{id: method}``; every typing is a warning.

    Fix round after P4b (module docstring): ``reset`` (``answer_typed``) are the pieces this round's answers typed;
    code reads a copy of the building where they are untyped again, as in the first reading, and only the proposals
    for pieces still untyped in the real building are applied (an AI type is never replaced)."""
    from wenart.furniture import infer as INF

    b = build.building
    view = dict(b, conflicts=list(b.get("conflicts") or []) + list(getattr(build, "raw_conflicts", []) or []))
    if reset:
        view = _first_reading_view(view, set(reset))
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    proposals = [p for p in INF.code_types(view) if p.get("type_method") in INF.CODE_TYPE_METHODS
                 and INF.untyped_drawn(by_id.get(p["piece_id"]) or {})]
    if not proposals:
        return [], {}
    b["furniture"] = INF.apply_inferences(b, proposals)["furniture"]
    methods = {}
    for p in proposals:
        methods[p["piece_id"]] = p["type_method"]
        build.warn(f"{p['piece_id']}: typed {p['type']} by code ({p['type_method']}, before the context rules and "
                   f"any AI): {p['reason']}")
    return list(methods), methods


def _reports(build, works: dict) -> list[dict]:
    """The page extraction reports of a reading run (each once). Fix round after P3: the reports of the pages whose
    questions are asked only (a secondary page's keys, never asked and numbered like the master's, decide nothing)."""
    out = []
    for w in _works(build, works, asked_only=True):
        report = getattr(w.extraction, "report", None)
        if isinstance(report, dict):
            out.append(report)
    return out


def answered_keys(build, works: dict) -> set[str]:
    """Build round 3 (K3): the question keys asked and answered in this round: on a page that got answers
    (``answers_applied``), its questions less the ones still without a complete pair (``pending``) and less the
    ones withdrawn (``typed_by_code``). ``withdraw_questions`` keeps these listed."""
    out: set[str] = set()
    for report in _reports(build, works):
        if not report.get("answers_applied"):
            continue
        keys = {str(q.get("key")) for q in report.get("questions") or [] if q.get("key")}
        out |= keys - set(report.get("pending") or []) - set(report.get(CODE_TYPED_KEY) or [])
    return out


def open_questions(build, works: dict, items: dict) -> set[str]:
    """Build round 3 (K3): the drawn pieces that are still unknown and carry a recognition question no answer of
    this round decided (``answered_keys``), in every mode: in a first plain run they are the pending ones; with
    --no-ai, and for the questions withdrawn in the first run when the answers come, nothing waits for them, but
    the steps before the size inference (the block copies, the first fronts) hold them like pending pieces, so
    what those steps type, and the questions the code and context typing withdraw, are the same in every mode."""
    keys: set[str] = set()
    for report in _reports(build, works):
        keys |= {str(q.get("key")) for q in report.get("questions") or [] if q.get("key")}
        keys |= {str(k) for k in report.get("pending") or []}
    keys -= answered_keys(build, works)
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    # Fix round after P3: a piece only a secondary page drew has no asked question (its key may equal an asked one).
    asked = _items(build, works, asked_only=True)
    return {pid for pid, item in items.items()
            if pid in asked and str((item.details or {}).get("candidate_key")) in keys
            and (by_id.get(pid) or {}).get("type") == "unknown"}


def withdraw_questions(build, works: dict, items: dict, coded: list[str],
                       methods: Optional[dict] = None) -> dict[str, str]:
    """Milestone 13 (K3): the recognition questions of the pieces code typed (``coded``) are withdrawn: their keys
    leave every page report's ``pending`` (nothing waits for them) and go to ``report["typed_by_code"]`` and
    ``build.code_typed`` (key -> piece id), which the pipeline's ``_write_questions`` leaves out of
    ``recognition/requests.json``. Returns the withdrawn ``{key: piece id}`` (empty when no code-typed piece had a
    question, e.g. a piece typed from its block name at extraction time). Build round 3: ``methods`` (piece id ->
    ``twin | level | block | group_member | context:<type>``) is kept beside the keys in
    ``report["typed_by_code_methods"]`` and ``build.code_typed_methods`` (key -> method), so the report lists both
    kinds with their method; without ``methods`` the piece's ``type_method`` is used."""
    keys = {}
    answered = answered_keys(build, works)
    # Fix round after P3: a piece only a secondary page drew has no asked question to withdraw (its key, numbered like
    # the master's, would withdraw the master's question of another piece).
    asked = _items(build, works, asked_only=True)
    for pid in coded:
        key = (items[pid].details or {}).get("candidate_key") if pid in items and pid in asked else None
        if key and str(key) in answered:
            # Build round 3 (K3): a question asked and answered in this round stays listed (the code type stands
            # beside the AI's answer), so the run with the answers asks what the first run asked.
            build.warn(f"{pid}: recognition question {key} kept: it was asked and answered in this round (typed by "
                       "code as well)")
            continue
        if key:
            keys[str(key)] = pid
    if not keys:
        return {}
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    how = {key: str((methods or {}).get(pid) or (by_id.get(pid) or {}).get("type_method") or "code")
           for key, pid in keys.items()}
    for w in _works(build, works, asked_only=True):
        report = w.extraction.report
        if report is None:
            continue
        asked = {q.get("key") for q in report.get("questions") or []} | set(report.get("pending") or [])
        mine = [k for k in keys if k in asked]
        if not mine:
            continue
        report["pending"] = [k for k in report.get("pending") or [] if k not in keys]
        report[CODE_TYPED_KEY] = sorted(set(report.get(CODE_TYPED_KEY) or []) | set(mine))
        report[CODE_METHODS_KEY] = dict(report.get(CODE_METHODS_KEY) or {}, **{k: how[k] for k in mine})
    store = getattr(build, "code_typed", None)
    if not isinstance(store, dict):
        store = build.code_typed = {}
    store.update(keys)
    store_how = getattr(build, "code_typed_methods", None)
    if not isinstance(store_how, dict):
        store_how = build.code_typed_methods = {}
    store_how.update(how)
    for key, pid in sorted(keys.items()):
        build.warn(f"{pid}: recognition question {key} withdrawn: typed by code before the AI ({how[key]}, K3)")
    return keys


# --------------------------------------------------------------------------
# 3b. Two AI passes that disagree (fix round after P4b)
# --------------------------------------------------------------------------

def room_misses(b: dict, room: dict) -> dict[str, str]:
    """Fix round after P4b (module docstring): ``{type: why}`` for the types ``room`` misses: the missing members of
    its drawn groups (``infer._group_wants``) and the anchors of its program's groups (``program._rows`` of the room
    kind, required or not) that no built piece of the room is."""
    from wenart.furniture import groups as GR, infer as INF, placer, program as PR

    out = {t: lines[0] for t, lines in sorted(INF._group_wants(b, room).items()) if lines}
    kind = PR.room_kind(b, room)
    present = {f.get("type") for f in b.get("furniture") or [] if f.get("room_id") == room["id"]
               and f.get("type") not in (None, "unknown") and f.get("build") is not False}
    templates = GR.load_groups()
    for group, _required, _opts in PR._rows(kind, PR._area(room), placer.room_context(b, room).polygon, b, room,
                                            room.get("room_subtype")):
        t = templates.get(group) or {}
        anchors = list((t.get("anchor") or {}).get("types") or []) if t.get("layout") == "anchored" else []
        if anchors and not set(anchors) & present:
            for a in anchors:
                out.setdefault(a, f"the {kind} room's {group} group has no {' or '.join(anchors)}")
    return out


def _named_types(f: dict) -> list[str]:
    """The different types the AI passes named for ``f`` (``type_candidates``), in pass order."""
    seen: list[str] = []
    for c in f.get("type_candidates") or []:
        t = c.get("type") if isinstance(c, dict) else None
        if t and t not in seen:
            seen.append(t)
    return seen


def _disagreeing_types(f: dict) -> list[str]:
    """The two different types the AI passes named for ``f`` (``type_candidates``), else []."""
    seen = _named_types(f)
    return seen if len(seen) == 2 else []


def _twins_of(view: dict, f: dict) -> list[tuple[dict, dict]]:
    """Pass before P5 (module docstring): ``(piece, its room)`` for the drawn pieces at ``f``'s spot in the twin rooms
    of ``f``'s room, typed or not: the twin rule's match (``infer._twin_type``: ``infer._twin_rooms``, the mirrored
    centre within ``infer.SAME_CENTRE_M``, the size within ``infer.SAME_FOOTPRINT_M``)."""
    from wenart.furniture import infer as INF
    from wenart.ingest import twins as TW

    room = INF._rooms(view).get(f.get("room_id") or "")
    if room is None or not f.get("footprint"):
        return []
    out = []
    for other, t in INF._twin_rooms(view, room):
        mapped = TW._apply(t, f["footprint"]["center"])
        for g in view.get("furniture") or []:
            if g.get("room_id") != other["id"] or g["id"] == f["id"] or g.get("source") != "from_documents" \
                    or not g.get("footprint"):
                continue
            if G.distance(mapped, tuple(g["footprint"]["center"])) <= INF.SAME_CENTRE_M + 1e-9 \
                    and INF._same_size(f, g):
                out.append((g, other))
    return out


def tie_break(build, items: dict, pending=(), deferred: Optional[set] = None) -> list[str]:
    """Fix round after P4b (module docstring): an untyped drawn piece whose two AI passes named two different
    furniture types, both fitting its drawn size (the size table, +15 %, and the type's shape) and both allowed in its
    room, is typed by code: the type the room misses (``room_misses``), else the one whose real product size is
    nearer (``infer._product_distance``; then the higher AI confidence, then the name). The piece is ``inferred``
    (``type_method: INFER_METHOD``, status kept), its evidence names the rule, both answers and the plan crop, and
    its ``symbol_type_disagreement`` conflict gets the decision as its resolution. Returns the typed ids.

    Pass before P5 (module docstring): twins are decided together (``_twins_of``). A piece whose twin is typed is left
    to the twin rule. With untyped twins, one of which at least the rule above could decide alone (two answers, both
    fitting; else all stay for review, as a single piece does), the one type that the passes of the piece and of
    every twin with answers named, that fits the drawn size and the room of each and that is no fixed type a room
    does not miss, goes to all of them (``TWIN_TIE_NOTE``); else the piece is decided as above (when it can be) and so
    is every twin whose passes named that type; the other twins are left to the twin rule.
    ``deferred`` (a set, filled when given) gets the ids left to the twin rule: the caller's ``code_first`` after this
    step types them."""
    from wenart.furniture import infer as INF, plausibility as PL, program as PR, schemas
    from wenart.furniture import sizes as SZ

    b = build.building
    raw = list(getattr(build, "raw_conflicts", []) or [])
    view = dict(b, conflicts=list(b.get("conflicts") or []) + raw)
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    later = deferred if deferred is not None else set()
    allowed: dict[str, set] = {}

    def fits(p: dict, t: str) -> bool:
        """``t`` fits the drawn size of ``p`` and is allowed in its room."""
        room = rooms.get(p.get("room_id") or "")
        if room is None or t not in schemas.SIZE_OPTIONS:
            return False
        if room["id"] not in allowed:
            allowed[room["id"]] = PL.allowed_in(view, room) | set(
                schemas.allowed_types(PR.room_kind(view, room), room.get("room_subtype")))
        size = [float(v) for v in p["footprint"]["size"]]
        return t in allowed[room["id"]] and SZ.fits(t, size, 0.15) and INF._shape_ok(t, size)

    def misses_of(p: dict) -> dict:
        """``room_misses`` of the room of ``p`` now (the pieces this step typed count)."""
        return room_misses(view, rooms[p["room_id"]])

    typed: list[str] = []
    for f in b["furniture"]:
        if f["id"] in pending or f["id"] in later or not INF.untyped_drawn(f) or f.get("room_id") not in rooms:
            continue
        pair = _disagreeing_types(f)
        if not pair:
            continue
        twins = [(g, r) for g, r in _twins_of(view, f) if g["id"] not in pending]
        if any(INF._typed_drawn(g) for g, _r in twins):
            later.add(f["id"])                  # pass before P5: its typed twin decides (the twin rule)
            continue
        twins = [(g, r) for g, r in twins if INF.untyped_drawn(g) and g.get("room_id") in rooms]
        answered = [(g, r) for g, r in twins if _named_types(g)]
        group = [f] + [g for g, _r in answered]
        # Only a group with a piece the rule below could decide alone (two answers, both fitting) is decided: twins
        # whose passes all name one type that fits besides one that does not stay for review, as a single piece does.
        deciders = {p["id"] for p in group if len(_named_types(p)) == 2 and all(fits(p, t) for t in _named_types(p))}
        if not deciders:
            continue
        shared = [t for t in pair if answered and all(t in _named_types(g) for g in group)
                  and all(fits(p, t) and (t not in schemas.FIXED_TYPES or t in misses_of(p))
                          for p in [f] + [g for g, _r in twins])]
        if len(shared) == 1:
            ftype = shared[0]
            why = TWIN_TIE_NOTE.format(twin=answered[0][0]["id"], room=answered[0][1]["id"])
        else:
            if f["id"] not in deciders:
                continue                        # a twin decides when its turn comes (its type reaches this piece)
            room = rooms[f["room_id"]]
            size = [float(v) for v in f["footprint"]["size"]]
            misses = misses_of(f)
            missing = [t for t in pair if t in misses]
            # Fixed equipment is taken as drawn, never guessed (CLAUDE.md): a fixed type the room does not miss is no
            # choice (real02's salon sofa f_L-1b_045, kitchen_island / sofa, beside the open kitchen's own island).
            choices = [t for t in pair if t not in schemas.FIXED_TYPES or t in missing]
            conf = {c.get("type"): float(c.get("confidence") or 0.0) for c in f.get("type_candidates") or []
                    if isinstance(c, dict)}
            if len(missing) == 1:
                ftype = missing[0]
                why = f"the room misses it ({misses[ftype]})"
            elif len(choices) == 1:
                ftype = choices[0]
                why = "the other answer is fixed equipment the room does not miss (taken as drawn, never guessed)"
            elif len(choices) == 2:
                ftype = min(pair, key=lambda t: (round(INF._product_distance(t, size), 4), -conf.get(t, 0.0), t))
                why = "its real product size is the nearer one to the drawn size" + \
                      (" (the room misses both)" if missing else "")
            else:
                continue                        # two fixed types the room does not miss: the plan crop decides
        _tie_type(build, f, ftype, why, items, raw, fits)
        typed.append(f["id"])
        note = TWIN_TIE_NOTE.format(twin=f["id"], room=f["room_id"])
        for g, _r in twins:
            if ftype in _named_types(g) and fits(g, ftype):
                _tie_type(build, g, ftype, note, items, raw, fits)
                typed.append(g["id"])
            else:
                later.add(g["id"])              # the twin rule types it from ``f`` (code_first after this step)
    return typed


def _tie_type(build, f: dict, ftype: str, why: str, items: dict, raw: list, fits) -> None:
    """``tie_break``'s decision ``ftype`` (``why``) applied to ``f``: type, ``type_method: INFER_METHOD``, ``inferred``
    with the reason (both answers, the plan crop), built, the rule's evidence, the type's height, and its
    ``symbol_type_disagreement`` conflict resolved; a warning."""
    from wenart.furniture import schemas

    b = build.building
    named = _named_types(f)
    size = [float(v) for v in f["footprint"]["size"]]
    others = [t for t in named if t != ftype]
    det = items[f["id"]].details if f["id"] in items else {}
    crop = _crop(det)
    said = (f"the two AI passes disagree ({named[0]} / {named[1]})" if len(named) == 2
            else f"the AI passes named {' / '.join(named)}")
    reason = (f"{said}; {'both fit' if all(fits(f, t) for t in named) else ftype + ' fits'} the drawn "
              f"{size[0]:.2f} x {size[1]:.2f} m and the room: {ftype}, because {why}"
              + (f"; plan crop {crop}" if crop else ""))
    f["type"] = ftype
    f["type_method"] = INFER_METHOD
    f["inferred"] = True
    f["inferred_reason"] = reason
    if f.get("build") is False:
        f["build"] = True                       # unbuilt only because it was untyped (``infer.untyped_drawn``)
        f.pop("not_built_reason", None)
    f.setdefault("evidence", []).append(_ev(f, TIE_RULE, reason, 0.55))
    if f.get("height") is None and schemas.HEIGHTS.get(ftype) is not None:
        f["height"] = schemas.HEIGHTS[ftype]
    for c in raw + list(b.get("conflicts") or []):
        if c.get("kind") == "symbol_type_disagreement" and f["id"] in (c.get("element_ids") or []):
            c["resolution"] = (f"typed {ftype} by code (not {' or '.join(others) or 'another type'}): {why}; "
                               f"inferred, listed in the report ({TIE_RULE})")
    build.warn(f"{f['id']}: unknown -> {ftype} by code ({TIE_RULE}): {reason}")


# --------------------------------------------------------------------------
# 4. Misread fixed equipment (user OK 1 of 10 Oct 2026)
# --------------------------------------------------------------------------

def misread_share(ftype: str, size) -> float:
    """How far a footprint lies outside its type's real range (0 inside; 0.5 = 50 % beyond a bound), the better of
    both orientations."""
    a, b_ = (float(v) for v in size[:2])
    return min(oriented_share(ftype, (a, b_)), oriented_share(ftype, (b_, a)))


def oriented_share(ftype: str, size) -> float:
    """``misread_share`` with the first side as the width (across the front) and the second as the depth."""
    from wenart.furniture import sizes

    r = sizes.real_range(ftype)
    if not r:
        return 0.0
    e = 0.0
    for v, (lo, hi) in ((float(size[0]), r["width"]), (float(size[1]), r["depth"])):
        if v < lo:
            e = max(e, lo / max(v, 1e-6) - 1.0)
        elif v > hi:
            e = max(e, v / hi - 1.0)
    return e


def swing_polys(b: dict, room: dict) -> list[Polygon]:
    """The swings of the doors that open into ``room``: on the room side of the wall, the two quarter discs a leaf
    of the door's width sweeps hinged at either jamb (the hinge side is not read), within the opening's width. A
    piece beside the door frame is not in the swing (a half disc around the centre would reach half a leaf past
    each jamb: real02's washbasins beside their bathroom doors)."""
    walls = {w["id"]: w for w in b.get("walls") or []}
    room_poly = Polygon(room["polygon"])
    room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
    out = []
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("swing_side") != room["id"] or o.get("operation") in ("sliding",
                                                                                                    "pocket"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None:
            continue
        (x0, y0), (x1, y1) = w["start"], w["end"]
        length = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        cx, cy = o["center"]
        width = float(o.get("width") or 0.9)
        half_t = float(w.get("thickness") or 0.1) / 2.0
        for sign in (1.0, -1.0):
            nx, ny = -uy * sign, ux * sign
            inner = (cx + nx * half_t, cy + ny * half_t)
            if not room_poly.buffer(0.01).contains(Point(inner[0] + nx * 0.05, inner[1] + ny * 0.05)):
                continue
            ja = (inner[0] - ux * width / 2, inner[1] - uy * width / 2)
            jb = (inner[0] + ux * width / 2, inner[1] + uy * width / 2)
            strip = Polygon([ja, jb, (jb[0] + nx * width, jb[1] + ny * width),
                             (ja[0] + nx * width, ja[1] + ny * width)])
            out.append(unary_union([Point(ja).buffer(width, 32), Point(jb).buffer(width, 32)]).intersection(strip))
            break
    return out


def problems(poly: Polygon, room_poly: Polygon, swings: list[Polygon], others: Optional[list] = None) -> list[str]:
    """What is wrong with a fixed piece where it stands (the cases of the user OK of 10 Oct 2026): through a wall
    (more than ``THROUGH_WALL_M`` past its room's outline) or in a door swing (more than ``SWING_SHARE`` of its
    area). ``others`` is accepted for callers that pass the room's pieces; overlaps are not this rule's business (a
    sink stands in its counter)."""
    out = []
    if poly.difference(room_poly.buffer(THROUGH_WALL_M, join_style=2)).area > 1e-4:
        out.append("through a wall")
    if any(poly.intersection(s).area > SWING_SHARE * poly.area for s in swings):
        out.append("in a door swing")
    return out


def _fits_room(poly: Polygon, room_poly: Polygon, swings: list[Polygon], others: list[Polygon]) -> bool:
    return not problems(poly, room_poly, swings, others)


def _placed(f: dict, size, centre) -> dict:
    out = copy.deepcopy(f)
    out["footprint"] = dict(out["footprint"], center=[round(centre[0], 4), round(centre[1], 4)],
                            size=[round(size[0], 4), round(size[1], 4)])
    return out


def fix_fixed(build, items: Optional[dict] = None) -> list[str]:
    """Step 4 (see the module docstring). Returns the ids of the adjusted pieces. ``items`` (the core's items) give
    the plan crop of a piece that was asked (``adjusted_by_ai["crop"]``)."""
    from wenart.furniture import infer as INF
    from wenart.furniture import schemas

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    done = []
    for f in b["furniture"]:
        if f["type"] not in schemas.FIXED_TYPES or f["type"] in ("stair", "kitchen_counter") or \
                f.get("build") is False or f.get("source") != "from_documents":
            continue
        room = rooms.get(f.get("room_id"))
        if room is None:
            continue
        room_poly = Polygon(room["polygon"])
        room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
        ring = room_ring(room)
        swings = swing_polys(b, room)
        mates = [o for o in b["furniture"] if o is not f and o.get("room_id") == f.get("room_id")
                 and o.get("build") is not False]
        others = [rect(o) for o in mates if o["type"] in schemas.FIXED_TYPES]
        before = copy.deepcopy(f["footprint"])
        drawn_front = f.get("front_deg")
        share = misread_share(f["type"], f["footprint"]["size"])
        found = problems(rect(f), room_poly, swings, others)
        if share <= MISREAD_SHARE and not found:
            continue
        reasons = []
        new = copy.deepcopy(f)
        if new.get("front_deg") is None and f["type"] not in schemas.FRONTLESS_TYPES:
            front, why = _front_of(new, room, mates)
            if front is not None:
                INF.set_front(new, front)
                reasons.append(f"front {new['front_deg']:g} deg inferred ({why})")
        if share > MISREAD_SHARE:
            size = _product(f["type"], new)
            new = _resized(new, ring, size)
            reasons.append(f"drawn {before['size'][0]:.2f} x {before['size'][1]:.2f} m is {share:.0%} outside the "
                           f"{f['type']} size range: set to the real product size {size[0]:.2f} x {size[1]:.2f} m "
                           f"(width x depth), its back kept on its wall")
        found = problems(rect(new), room_poly, swings, others)
        if found:
            moved = _nearest_valid(new, room_poly, swings, others)
            if moved is not None:
                d = math.dist(moved["footprint"]["center"], new["footprint"]["center"])
                reasons.append(f"{' and '.join(found)}: moved {d:.2f} m to the nearest free spot")
                new = moved
            else:
                reasons.append(f"{' and '.join(found)}, no free spot within {MOVE_MAX_M:.2f} m: left as drawn")
                if share <= MISREAD_SHARE:
                    build.warn(f"{f['id']}: {f['type']} {' and '.join(found)}; no free spot within "
                               f"{MOVE_MAX_M:.2f} m (left as drawn)")
                    continue
        reason = "; ".join(reasons)
        f.setdefault("drawn_type", f["type"])
        f.setdefault("drawn_footprint", before)
        f.setdefault("drawn_front_deg", drawn_front)
        f.setdefault("drawn_height", f.get("height"))
        changed = {"footprint": before}
        if new.get("front_deg") != drawn_front:
            changed["front_deg"] = drawn_front
        f["footprint"] = new["footprint"]
        f["front_deg"] = new.get("front_deg")
        item = (items or {}).get(f["id"])
        f["adjusted_by_ai"] = {"reason": f"misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026): {reason}",
                               "changed": changed, "rule": FIXED_RULE,
                               "crop": _crop(item.details if item is not None else None)}
        f.setdefault("evidence", []).append(_ev(f, FIXED_RULE, reason, 0.8))
        build.warn(f"{f['id']}: {f['type']} adjusted at ingest: {reason}")
        done.append(f["id"])
    return done


def _product(ftype: str, f: dict) -> tuple[float, float]:
    """The real product footprint (width across the front, depth) nearest to the drawn one; without a front the
    drawn sides are read the way round that fits the type's range best."""
    from wenart.furniture import sizes

    w, d = (float(v) for v in f["footprint"]["size"][:2])
    if f.get("front_deg") is None and oriented_share(ftype, (d, w)) < oriented_share(ftype, (w, d)) - 1e-9:
        pw, pd = sizes.product_size(ftype, (d, w))
        return float(pd), float(pw)
    pw, pd = sizes.product_size(ftype, (w, d))
    return float(pw), float(pd)


def _resized(f: dict, ring, size) -> dict:
    """``f`` with the product ``size`` (width, depth in its frame), its back (or the side on a wall) kept in place."""
    w0, d0 = (float(v) for v in f["footprint"]["size"][:2])
    w1, d1 = float(size[0]), float(size[1])
    cx, cy = f["footprint"]["center"]
    rot = math.radians(float(f["footprint"].get("rotation_deg") or 0.0))
    ux, uy = math.cos(rot), math.sin(rot)              # local +X
    vx, vy = -math.sin(rot), math.cos(rot)             # local +Y (the back, the front faces -Y)
    near = wall_sides(f, ring)                          # local order: front (-Y), right (+X), back (+Y), left (-X)
    sx, sy = 0.0, 0.0
    if f.get("front_deg") is not None or 2 in near or 0 in near:
        back = 2 if (f.get("front_deg") is not None or 2 in near) else 0
        sy = (d0 - d1) / 2.0 * (1.0 if back == 2 else -1.0)
    if 1 in near and 3 not in near:
        sx = (w0 - w1) / 2.0
    elif 3 in near and 1 not in near:
        sx = -(w0 - w1) / 2.0
    centre = (cx + ux * sx + vx * sy, cy + uy * sx + vy * sy)
    return _placed(f, (w1, d1), centre)


def _nearest_valid(f: dict, room_poly: Polygon, swings: list, others: list) -> Optional[dict]:
    """The nearest position within ``MOVE_MAX_M`` (5 cm steps along both footprint axes, along first) where the
    piece lies in its room, clear of door swings and other fixed pieces; None when there is none."""
    cx, cy = f["footprint"]["center"]
    rot = math.radians(float(f["footprint"].get("rotation_deg") or 0.0))
    axes = [(math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot))]
    steps = int(round(MOVE_MAX_M / MOVE_STEP_M))
    best = None
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            dx = axes[0][0] * i * MOVE_STEP_M + axes[1][0] * j * MOVE_STEP_M
            dy = axes[0][1] * i * MOVE_STEP_M + axes[1][1] * j * MOVE_STEP_M
            d = math.hypot(dx, dy)
            if d > MOVE_MAX_M + 1e-9 or (best is not None and d >= best[0] - 1e-9):
                continue
            cand = _placed(f, f["footprint"]["size"], (cx + dx, cy + dy))
            if _fits_room(rect(cand), room_poly, swings, others):
                best = (d, abs(j), cand)
    return best[2] if best else None


# --------------------------------------------------------------------------
# 5. Fronts
# --------------------------------------------------------------------------

def infer_fronts(build, pending=()) -> int:
    """Step 5 (see the module docstring). Returns the number of fronts inferred."""
    from wenart.furniture import infer as INF
    from wenart.furniture import schemas

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    n = 0
    for f in b["furniture"]:
        if f.get("front_deg") is not None or f["type"] in schemas.FRONTLESS_TYPES or f.get("build") is False or \
                f.get("source") != "from_documents" or f["id"] in pending:
            continue
        room = rooms.get(f.get("room_id"))
        if room is None:
            continue
        front, why = _front_of(f, room, [o for o in b["furniture"] if o is not f and o.get("room_id") == room["id"]
                                         and o.get("build") is not False])
        if front is None:
            continue
        INF.set_front(f, front)
        f["inferred"] = True
        f["front_inferred"] = why
        f["inferred_reason"] = "; ".join(x for x in (f.get("inferred_reason"), f"front: {why}") if x)
        f.setdefault("evidence", []).append(_ev(f, FRONT_RULE, f"front {f['front_deg']:g} deg: {why}", 0.6))
        n += 1
    return n


def _front_of(f: dict, room: dict, mates: list[dict]) -> tuple[Optional[float], Optional[str]]:
    from wenart.furniture import schemas

    ring = room_ring(room)
    poly = rect(f)
    ss = sides(poly)
    near = wall_sides(f, ring)
    ftype = f["type"]
    rule = schemas.orientation_rule(ftype)
    by_type = lambda *ts: [m for m in mates if m["type"] in ts]      # noqa: E731
    if ftype in ("chair", "office_chair", "bar_stool"):
        hosts = by_type("table_dining", "table_coffee", "desk", "kitchen_island")
        if hosts:
            host = min(hosts, key=lambda h: (round(rect(h).distance(poly), 6), h["id"]))
            if rect(host).distance(poly) <= 0.8:
                c = rect(host).centroid
                deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
                return snap_front(f, deg), f"faces its table {host['id']}"
    if ftype == "nightstand":
        for bed in by_type("bed_double", "bed_single", "bunk_bed"):
            if bed.get("front_deg") is not None and rect(bed).distance(poly) <= 0.4:
                return snap_front(f, float(bed["front_deg"])), f"faces the way its bed {bed['id']} faces"
    if ftype == "tv_unit":
        for seat in by_type("sofa", "sofa_corner", "armchair"):
            c = rect(seat).centroid
            deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
            if len(near) == 1 and abs(G.normalise_angle(deg - (outward_deg(f, ss[near[0]]) + 180.0))) <= 45.0:
                return snap_front(f, deg), f"faces the seat {seat['id']}"
    if len(near) == 1:
        back = ss[near[0]]
        long_side = math.dist(*back) >= 0.999 * max(math.dist(*s) for s in ss)
        if ftype in ("toilet", "bed_double", "bed_single", "bunk_bed", "bathtub") or long_side or \
                rule["back"] in ("wall", "wall_or_group"):
            return snap_front(f, outward_deg(f, back) + 180.0), "its back stands on the only side on a wall"
    if len(near) == 2 and (near[1] - near[0]) % 2 == 1:
        lengths = {k: math.dist(*ss[k]) for k in near}
        long_k, short_k = sorted(near, key=lambda k: -lengths[k])
        # Beds, toilets: the head (short side) is on the wall; cabinets, sofas, counters: the long side.
        k = short_k if ftype in HEAD_TYPES else long_k
        if lengths[long_k] > 1.1 * lengths[short_k]:
            return snap_front(f, outward_deg(f, ss[k]) + 180.0), "standing in a corner: its " + \
                ("short" if k == short_k else "long") + " side on the wall is the back"
    if near and rule["back"] in ("wall", "wall_or_group"):
        # Against two or three walls (a shower in its corner or niche, a washing machine in a corner): the front is
        # the free side facing the most room; a bed's front is one of its short sides.
        free = [k for k in range(4) if k not in near]
        if ftype in HEAD_TYPES:
            shortest = min(math.dist(*s) for s in ss)
            free = [k for k in free if math.dist(*ss[k]) <= 1.01 * shortest]
        ranked = sorted(((_free_ray(f, ss[k], ring), k) for k in free), key=lambda t: (-round(t[0], 3), t[1]))
        if len(ranked) == 1 or (len(ranked) > 1 and ranked[0][0] >= 1.25 * ranked[1][0]):
            k = ranked[0][1]
            return snap_front(f, outward_deg(f, ss[k])), "the free side facing the most room is the front"
    return None, None


def _free_ray(f: dict, side, ring) -> float:
    """How far the room reaches in front of a side (from its midpoint along its outward normal, up to 10 m)."""
    deg = math.radians(outward_deg(f, side))
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    ray = LineString([(mx + math.cos(deg) * 0.01, my + math.sin(deg) * 0.01),
                      (mx + math.cos(deg) * 10.0, my + math.sin(deg) * 10.0)])
    hit = ray.intersection(ring)
    if hit.is_empty:
        return 10.0
    pts = [hit] if hit.geom_type == "Point" else [g for g in getattr(hit, "geoms", []) if g.geom_type == "Point"]
    return min((math.dist((mx, my), (p.x, p.y)) for p in pts), default=10.0)


# --------------------------------------------------------------------------
# 6. Kitchen zones of open plans
# --------------------------------------------------------------------------

def kitchen_zones(build) -> int:
    """Step 6 (see the module docstring; contract §13.3). Returns the number of zones."""
    b = build.building
    n = 0
    for room in b.get("rooms") or []:
        if room.get("room_type") == "kitchen" or len(room.get("polygon") or []) < 3:
            continue
        pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"] and f["type"] in KITCHEN_ZONE_TYPES
                  and f.get("build") is not False]
        if not any(f["type"] in ("kitchen_counter", "sink_kitchen", "stove", "fridge", "kitchen_island")
                   for f in pieces):
            continue
        room_poly = Polygon(room["polygon"])
        room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
        zone = unary_union([rect(f).buffer(ZONE_AISLE_M, join_style=2) for f in pieces]).intersection(room_poly)
        zone = zone.convex_hull.intersection(room_poly)
        if zone.is_empty:
            continue
        geom = zone if zone.geom_type == "Polygon" else max(getattr(zone, "geoms", [zone]), key=lambda g: g.area)
        if geom.geom_type != "Polygon":
            continue
        geom = geom.simplify(0.01)
        ids = sorted(f["id"] for f in pieces)
        text = (f"kitchen fixtures {', '.join(ids)} in a {room.get('room_type')} room: an open kitchen; the zone is "
                f"them and the {ZONE_AISLE_M:.1f} m in front of them")
        room["zones"] = [z for z in room.get("zones") or [] if z.get("kind") != "kitchen"] + [{
            "zone_id": f"{room['id']}_kitchen", "kind": "kitchen",
            "polygon": [[round(x, 4), round(y, 4)] for x, y in list(geom.exterior.coords)[:-1]],
            "piece_ids": ids, "evidence": [_ev(pieces[0], ZONE_RULE, text, 0.8)]}]
        build.warn(f"{room['id']}: kitchen zone ({len(ids)} pieces): {text}")
        n += 1
    return n


# --------------------------------------------------------------------------
# 7. Never a box
# --------------------------------------------------------------------------

def never_a_box(build, items: dict, pending: Optional[set] = None) -> int:
    """Step 7: every piece still ``unknown`` is not built and listed in ``building["needs_review"]`` (its crop and
    reason); outlines, details, columns and decor (``inferred_as``) are explained and not listed. A piece whose AI
    question waits for its answers is not built either, but not listed (the pipeline lists the open questions).

    Fix round after P3 (16-17 Oct 2026): a piece that carries the waiting reason (``WAITS_REASON``) from an earlier
    pass but no longer waits (not in ``pending``) gets its build flag and reason back and goes through the rule like
    any untyped piece (listed in ``needs_review``): the reason never outlives the wait (CLAUDE.md: no untyped piece
    is left unexplained)."""
    b = build.building
    b.setdefault("needs_review", [])
    listed = {n["id"] for n in b["needs_review"]}
    n = 0
    for f in b["furniture"]:
        if f["type"] != "unknown" or f.get("inferred_as") in EXPLAINED_AS or f["id"] in listed:
            continue
        if f["id"] in (pending or set()):
            if f.get("build") is not False:
                f["build"] = False
                f["not_built_reason"] = WAITS_REASON
            continue
        if f.get("not_built_reason") == WAITS_REASON:
            # The wait is over (fix round after P3): the flag and the reason were the wait's alone.
            f.pop("not_built_reason", None)
            f["build"] = True
        det = items[f["id"]].details if f["id"] in items else {}
        if f.get("build") is False and not det.get("oversize"):
            # Already not built for a reason (both AI passes: not furniture; a detail of a counter leg): the
            # building says which, so no unexplained box is left.
            why = det.get("reason") or (f.get("evidence") or [{}])[0].get("note")
            if why and not (f.get("not_built_reason") or f.get("inferred_reason")):
                f["not_built_reason"] = why
            continue
        if f.get("build") is not False:
            f["build"] = False
            f["not_built_reason"] = "untyped (CLAUDE.md: no untyped piece is built)"   # the reason, not a source
        elif not f.get("not_built_reason"):
            f["not_built_reason"] = det.get("reason") or "a drawn cluster larger than 4.5 m that the re-read could " \
                                                         "not split (CLAUDE.md: no untyped piece is built)"
        cands = sorted({c.get("type") for c in f.get("type_candidates") or [] if c.get("type")})
        size = " x ".join(f"{v:.2f}" for v in f["footprint"]["size"])
        reason = (f"drawn piece {size} m in {f.get('room_id') or 'no room'} has no type"
                  + (f" (AI passes: {', '.join(cands)})" if cands else "")
                  + (f"; {det.get('reason') or det.get('note')}" if det.get("reason") or det.get("note") else "")
                  + ": not built")
        b["needs_review"].append({"id": f["id"], "kind": "untyped_piece", "reason": reason, "crop": _crop(det),
                                  "room_id": f.get("room_id"), "level_id": f["level_id"]})
        n += 1
    return n


def _refresh_rooms(b: dict) -> None:
    """A room whose only drawn pieces were symbols has no documented furniture."""
    with_pieces = {f.get("room_id") for f in b["furniture"] if f.get("source") == "from_documents"}
    for r in b.get("rooms") or []:
        if r.get("has_documented_furniture") and r["id"] not in with_pieces:
            r["has_documented_furniture"] = False


# --------------------------------------------------------------------------
# The hook
# --------------------------------------------------------------------------

def read_furniture(build, works: dict) -> None:
    b = build.building
    items = _items(build, works)
    pending = _pending(build, works)
    symbols = move_symbols(build, items, works)
    log_overrides(build, items)
    # Build round 3 (K3): the open questions are held in every mode by the steps before the size inference (a block
    # copy never decides one: the code typing below does, and withdraws it, or the AI does).
    held = set(pending) | open_questions(build, works, items)
    # Fix round after P4b (module docstring): the pieces this round's answers typed (and their block copies) are
    # untyped again in the code typing's view of the building, as in the first reading.
    copied_from: dict[str, list[str]] = {}
    copied = copies(build, items, held, copied_from)
    from_answers = answer_typed(build, works, items, copied_from)
    # Milestone 13 (K3), build round 3 (lead decision): code first, in every run. ``infer.code_types`` runs before
    # the context rules (the twin room, another level, the block name, the missing group member), on the open
    # questions too; then the context rules type what code left, on the open questions too; both kinds withdraw
    # their questions (``withdraw_questions`` with the method). Every step up to the size inference treats a piece
    # with an open question the same way in every mode (``open_questions``: no front for it yet), so the AI is asked
    # the same questions with --no-ai, in the first plain run and in the run with the answers.
    typed_by: dict[str, str] = {}
    withdrawn: dict[str, str] = {}
    context: dict[str, int] = {}
    pending = set(pending)

    def code_pass() -> list[str]:
        """``code_first`` on every untyped piece; the typed ones withdraw their questions."""
        coded, methods = code_first(build, from_answers)
        if coded:
            typed_by.update(methods)
            withdrawn.update(withdraw_questions(build, works, items, coded, methods))
            pending.difference_update(coded)
            held.difference_update(coded)
        return coded

    def context_pass() -> None:
        """One pass of the context rules on every unknown piece, open questions included; the typed ones withdraw
        their questions."""
        before = unknown_ids(build)
        for k, v in context_types(build, items).items():
            context[k] = context.get(k, 0) + v
        typed = context_typed(build, before)
        if typed:
            typed_by.update(typed)
            withdrawn.update(withdraw_questions(build, works, items, list(typed), typed))
            pending.difference_update(typed)
            held.difference_update(typed)

    code_pass()
    context_pass()
    fronts = infer_fronts(build, held)
    context_pass()                                   # the seats have their fronts now (coffee table, TV unit)
    if code_pass():                                  # chains: a missing member of a group the context rules typed
        fronts += infer_fronts(build, held)
        context_pass()
    if copied:
        context["copies"] = copied
    twice = duplicates(build)
    if twice:
        context["drawn_twice"] = twice
    inferred, coded2 = infer(build, pending)
    # Milestone 13 (K3): a code-typed piece waits for no AI answer: its question is withdrawn, it gets its front
    # and its partners like every typed piece below (``infer_types`` runs the code methods first, on the same
    # building in every mode; normally nothing is left for them after the passes above).
    by_id = {f["id"]: f for f in b["furniture"]}
    methods2 = {pid: str((by_id.get(pid) or {}).get("type_method") or "code") for pid in coded2}
    typed_by.update(methods2)
    withdrawn.update(withdraw_questions(build, works, items, coded2, methods2))
    pending = pending - set(coded2)
    to_twin: set[str] = set()
    tied = tie_break(build, items, pending, to_twin)  # fix round after P4b: two passes that disagree
    if tied or to_twin:
        # Pass before P5 (module docstring): the code typing once more, so a twin of a decided piece gets its type
        # (the twin rule) before the fronts and the review list. No reset: the AI's and the tie-break's types count.
        # A question asked and answered in this round stays listed (``withdraw_questions``); one that was not (a late
        # one) is withdrawn, as ``pipeline._infer_types`` withdrew it right after this step before.
        coded3, methods3 = code_first(build)
        if coded3:
            typed_by.update(methods3)
            withdrawn.update(withdraw_questions(build, works, items, coded3, methods3))
            pending = pending - set(coded3)
    fixed = fix_fixed(build, items)
    fronts += infer_fronts(build, pending)
    # Partners of the anchors the inference typed (real01 --no-ai: the chaise by its size): the Milestone 12 rules on
    # what does not wait for answers, and no question is withdrawn here: with --no-ai the size inference types
    # pieces a plain run leaves to the AI, so a withdrawal here would make the question count depend on the mode.
    for k, v in context_types(build, items, pending).items():
        context[k] = context.get(k, 0) + v
    fronts += infer_fronts(build, pending)
    zones = kitchen_zones(build)
    review = never_a_box(build, items, pending)
    _refresh_rooms(b)
    b.setdefault("symbols", [])
    b.setdefault("needs_review", [])
    build.reading = {"symbols": symbols, "context": context, "inferred": inferred, "fixed": fixed,
                     "fronts": fronts, "zones": zones, "needs_review": review, "tie_break": sorted(tied),
                     "answer_typed": sorted(from_answers),
                     "code_typed": sorted(typed_by), "questions_withdrawn": sorted(withdrawn),
                     "typed_by": dict(sorted(typed_by.items()))}
