"""The architect's questions about the open-air rooms and the details (pure; 25 Oct 2026, user: "the architect should
be able to ask questions like: is that table on the terrace ok? is that a table suitable for the terrace? is the door
to the terrace ok?" and "better architectural details needed, better internal stairs, better finishes in the fences
on top of the parapets; the architect needs to understand what better architectural details are and do the
changes").

What: five rules over every element they apply to, in the shape of ``architect_rules`` (one question record per rule,
one answer per element: ``ok``, a ``change`` code made, or ``open`` with options):

- U1 outdoor furniture: every piece on a balcony, terrace or patio is a piece one puts outside (a table, chairs, a
  bench, a lounger, a plant), of a model made for outside or of hard materials (``fit.outdoor_grade``: the fit ranks
  such models first since 25 Oct 2026). An inside-only piece the AI added is not built (code); a drawn one is asked.
- D3 doors to the terraces: wide enough (0.80 m), glazed (a door to a terrace is joinery of the facade: a mostly-glass
  library model or the glazed door in the windows' frame finish, ``opening_models.GLAZED_DOOR_MIN_SHARE``).
- K1 stairs: risers 0.15-0.19 m, goings of 0.25 m or more, 2 risers + 1 going 0.60-0.65 m (Blondel), 0.80 m wide or
  more; built with tread plates and nosings, a balustrade on every open side and a wall handrail
  (``parametric.stair_parts``).
- K2 guards: every balcony edge without a wall, every roof terrace parapet and every terrace edge over a drop has a
  guard at least 1.00 m high whose gaps a 0.1 m sphere cannot pass (``details.balustrade``), a parapet a coping.
- K3 one balustrade language: every balustrade of the house is of one kind (``details.balustrade_kind``), the stair's
  too.
- K4 the way up (27 Oct 2026, user on real06's first floor: "Needs a pathway here, how will the people go up to 2nd
  floor otherwise?"): every stair leads into its floors: from its last riser a visitor walks through a 0.80 m way into
  the main floor of the level above, and from the main floor of its own level to its first riser. The build checks it
  before anything is planned (``stair_access.fix_arrivals``, ``build.prepare``'s ``stair_access``): an assumed stair
  that is cut off takes the reading that leads into both floors (the upper plan's, its opening cut to the flights,
  half landing and headroom, its rise direction flipped, its half landing at the other end), logged ``by: architect``
  with the before and after; one no reading connects stays as drawn and is asked.

How: code checks on the building JSON and the build plan, as every architect rule; the changes are the code's own
(the fit's outdoor ranking, the glazed doors, the stair and balustrade builders), listed so the report shows them.
"""
from __future__ import annotations

from typing import Optional

from wenart import geometry as G
from wenart.blender import architect_actions as AA

RULES = (
    {"id": "U1", "topic": "outdoor furniture", "scope": "furniture", "severity": "minor",
     "question": "Is every piece on a balcony, terrace or patio a piece one puts outside, of a model made for outside?",
     "why": "an indoor table with a drawer or upholstered chairs on a terrace look wrong and would not last a winter"},
    {"id": "D3", "topic": "doors to the terraces", "scope": "door", "severity": "minor",
     "question": "Is every door to a terrace or balcony a glazed door, 0.80 m wide or more, in the windows' finish?",
     "why": "a terrace door is part of the facade: a solid inside door there reads wrong and darkens the room"},
    {"id": "K1", "topic": "stair details", "scope": "stair", "severity": "minor",
     "question": "Is every stair comfortable and finished: risers 0.15-0.19 m, goings 0.25 m+, 2R+G 0.60-0.65 m, "
                 "0.80 m wide, treads with nosings, a balustrade on the open side, a handrail?",
     "why": "a steep or narrow stair is unsafe; a stair without nosings, balusters or a handrail looks unfinished"},
    {"id": "K2", "topic": "guards", "scope": "edge", "severity": "major",
     "question": "Does every edge over a drop (a balcony, a roof terrace, a terrace over the garden) have a guard of "
                 "1.00 m whose gaps a child cannot pass, and every parapet a coping?",
     "why": "a fall of over a metre needs a guard; a bare parapet top stains the facade"},
    {"id": "K4", "topic": "the way up", "scope": "stair", "severity": "major",
     "question": "Does every stair lead into its floors: from its last step can I walk (0.80 m clear) into the rooms "
                 "of the floor above, and from the rooms of its own floor onto its first step, with no floor opening "
                 "across the way?",
     "why": "a stair that arrives on a strip its own opening cuts off from the rooms takes nobody upstairs"},
    {"id": "K3", "topic": "one balustrade language", "scope": "house", "severity": "minor",
     "question": "Do the balustrades of the house (stairs, balconies, terraces, parapets) speak one language?",
     "why": "glass on one side and steel bars on the other look like two houses"},
    {"id": "S2", "topic": "furniture chosen together", "scope": "room", "severity": "minor",
     "question": "Does the furniture of every room look chosen together: one or two wood tones, one metal finish, "
                 "loud colours only from the style's palette?",
     "why": "a walnut table, a white oak bed and a pine chair with brass and chrome read as a second-hand shop"},
    {"id": "S3", "topic": "styled rooms", "scope": "room", "severity": "minor",
     "question": "Is every room styled with enough decor for its style (a balanced living room 9 items, a bedroom 7, "
                 "a dining room 4; fewer in a sparse style such as japandi, more in a layered one such as classic)?",
     "why": "a room without lamps, plants, art, cushions and a rug looks unfinished in a render"},
    {"id": "S4", "topic": "complete furniture groups", "scope": "room", "severity": "minor",
     "question": "Is every furniture group complete: a sofa with a coffee table, an end table or a lamp and a rug; a "
                 "double bed with two nightstands; a dining table with four chairs or more?",
     "why": "a sofa alone or a bed with one nightstand looks half furnished"},
)
# decor_ai.ROOM_MIN: a balanced room's numbers. 27 Oct 2026: S3 checks the room's own minimum, the one the decor stage
# filled to (the building's ``decor_minimum``: its recipe's measured density, else the family's), else this number
# scaled by the style family's density (``wenart.style.density``)
DECOR_MIN = {"living": 9, "bedroom": 7, "dining": 4, "kitchen": 2, "hall": 2, "bathroom": 2}
GROUP_NEEDS = {
    "living": (("sofa", "sofa_corner"), (("table_coffee", "ottoman"), ("side_table", "floor_lamp"))),
    "bedroom": (("bed_double",), (("nightstand", "nightstand"),)),
    "dining": (("table_dining",), (("chair", "chair", "chair", "chair"),)),
}
OUTDOOR_TYPES = ("table_dining", "table_coffee", "side_table", "chair", "armchair", "bench", "bar_stool", "sofa",
                 "sofa_corner", "chaise", "ottoman", "potted_plant", "floor_lamp", "planter", "lounger", "parasol")
INDOOR_ONLY = ("bed_double", "bed_single", "bunk_bed", "crib", "wardrobe", "desk", "bookshelf", "dresser",
               "nightstand", "tv_unit", "sideboard", "office_chair", "display_cabinet", "shoe_cabinet",
               "tall_cabinet", "wall_cabinet", "washing_machine", "fridge", "toilet", "washbasin", "bathtub",
               "shower", "console_table")
TABLE_LIKE = ("desk", "console_table", "sideboard", "dresser")
STAIR = {"riser": (0.15, 0.19), "going_min": 0.25, "blondel": (0.60, 0.65), "width_min": 0.80}
GUARD_MIN_M = 1.00
TERRACE_DOOR_MIN_M = 0.80


def _q(rule_id: str) -> dict:
    return dict(next(r for r in RULES if r["id"] == rule_id), answers=[], status="ok")


def _ans(q: dict, element: str, found: str, change: Optional[str] = None, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": change}, **extra))
    if change and q["status"] == "ok":
        q["status"] = "fixed"


def _open(q: dict, element: str, found: str, ask: str, options: list, **extra) -> None:
    q["answers"].append(dict({"element": element, "found": found, "change": None, "open": True, "ask": ask,
                              "options": options}, **extra))
    q["status"] = "open"


def _where(kind: str, level_id, centre) -> dict:
    return {"kind": kind, "level_id": level_id, "centre": [round(float(centre[0]), 3), round(float(centre[1]), 3)]}


def open_air_rooms(plan: AA.Plan) -> dict:
    return {r["id"]: r for r in plan.rooms if str(r.get("room_type") or "").lower() in AA.OPEN_AIR}


def outdoor_furniture(plan: AA.Plan) -> dict:
    """U1 (pure; in place): an inside-only piece the AI added to an open-air room is not built; a drawn one is asked
    (remove it, or a table-like piece becomes the terrace's table); an outdoor type is ok when its model is made for
    outside or of hard materials (the fit's ``outdoor_grade`` 0 / 1), else the library gap is said."""
    q = _q("U1")
    rooms = open_air_rooms(plan)
    for f in plan.b.get("furniture") or []:
        if f.get("build") is False or f.get("room_id") not in rooms:
            continue
        t = str(f.get("type") or "").lower()
        fp = f.get("footprint") or {}
        where = _where("furniture", f.get("level_id"), fp.get("center") or (0.0, 0.0))
        room = rooms[f["room_id"]]
        name = f"{f['id']} ({t}) on {room['id']} ({room.get('room_type')})"
        if t in INDOOR_ONLY:
            if f.get("source") == "added_by_ai":
                f["build"] = False
                f["not_built_reason"] = (f"architect U1: a {t} is an inside piece; it was added to the open-air room "
                                         f"{room['id']} by the AI")
                _ans(q, f["id"], f"{name}: an inside piece", "not built: an inside piece the AI added outside")
                continue
            options = [AA.option("remove_piece", f"remove {f['id']}: it is not furniture of a terrace")]
            if t in TABLE_LIKE:
                options.append(AA.option("retype_piece", f"{f['id']} is the terrace's table", type="table_dining"))
            options.append(AA.option("keep"))
            _open(q, f["id"], f"{name}: an inside piece drawn on a terrace",
                  f"Is {f['id']} really a {t} on the terrace, or the terrace's table?", options, where=where)
            continue
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        grade = asset.get("outdoor_grade")
        if grade is None and asset.get("method") == "library":
            from wenart.blender.outdoor import outdoor_grade               # the model's own words and materials
            grade = outdoor_grade(asset)
        if asset.get("method") == "library" and grade == 2:
            _ans(q, f["id"], f"{name}: the model fitted ({asset.get('asset_id')}) is an inside model (upholstered or "
                             f"named for inside): no model made for outside fits its size in the library "
                             f"(library gap)", library_gap=True)
        elif asset.get("method") == "library":
            _ans(q, f["id"], f"{name}: {'a model made for outside' if grade == 0 else 'hard materials'}")
        else:
            _ans(q, f["id"], f"{name}: built by the module or parametric family (hard materials)")
    return q


def terrace_doors(plan: AA.Plan, sides: list[dict]) -> dict:
    """D3 (pure): every door between a room and an open-air room or the outside of a terrace."""
    q = _q("D3")
    rooms = open_air_rooms(plan)
    for s in sides:
        o = s["opening"]
        if s.get("type") != "door":
            continue
        ids = [r for r in (s.get("rooms") or []) if r]
        if not o.get("outside_door") and not any(r in rooms for r in ids):
            continue
        width = float(o.get("width") or 0.0)
        where = _where("door", o.get("level_id"), o["center"])
        if width + 1e-6 < TERRACE_DOOR_MIN_M:
            _open(q, o["id"], f"{o['id']} to the terrace is {width:.2f} m wide",
                  f"Can {o['id']} be widened to {TERRACE_DOOR_MIN_M:.2f} m?",
                  [AA.option("widen_door", door_id=o["id"]), AA.option("keep")], where=where)
            continue
        _ans(q, o["id"], f"{o['id']} to the terrace, {width:.2f} m",
             "a glazed door (mostly glass) in the windows' frame finish (code: a library model of at least "
             "45 % glass, else the glazed door)")
    return q


WINDER_AUTO_RISER = 0.20     # a drawn riser over this is a drawing error no code allows: winders are made


def _k1_label(piece: dict, riser: float, what: str) -> None:
    earlier = piece.get("adjusted_by_ai")                     # 27 Oct 2026: K4's (or the reading's) label is kept
    piece["adjusted_by_ai"] = {**({"earlier": earlier} if isinstance(earlier, dict) else {}),
                               "by": "architect", "rule": "architect K1",
                               "reason": f"a riser of {riser:.3f} m is a drawing error (the stair is drawn with too "
                                         f"few treads for its storey): {what}"}


def stair_details(stairs: list[dict], balustrade: str, building: Optional[dict] = None) -> dict:
    """K1 (pure; ``building`` in place): ``stairs`` = ``shell.plan_stairs`` items of every level. A stair drawn with
    risers over ``WINDER_AUTO_RISER`` (real04: 11 lines for a 3 m storey) is fixed for any shape (27 Oct 2026; before,
    only a U stair was): a U stair's half landing or an L stair's quarter landing becomes winders
    (``parametric.winder_treads``; the footprint as drawn), a straight stair gets a longer run at its foot where the
    floor there is free (``stair_access.run_extension``: ``stair.extra_treads``); each ``adjusted_by_ai`` with the
    reason, unless an answer set its ``winders`` / ``extra_treads``. What stays over the limit (no landing to turn, no
    free floor at the foot, too few winders) is asked; the answers ``stair_winders`` / ``stair_run`` with count 0
    keep it as drawn."""
    from wenart.blender import parametric as P
    from wenart.blender import stair_access as SA

    q = _q("K1")
    redo = []
    why_not: dict = {}
    for item in stairs:
        piece, plan = item.get("piece") or {}, item.get("plan")
        if plan is None:
            continue
        data = P.stair_data(piece)
        riser = float(plan["riser_m"])
        if building is None or not isinstance(data, dict) or riser <= WINDER_AUTO_RISER:
            continue
        land = (plan.get("landing") or {}).get("role")
        if len(plan["flights"]) == 2 and land == "mid" and "winders" not in data:
            quarter = abs(P._d2(plan["flights"][0]["rise_dir"], plan["flights"][1]["rise_dir"])) < 0.5
            data["winders"] = "auto"
            _k1_label(piece, riser, f"the {'quarter' if quarter else 'half'} landing becomes winders, the footprint "
                                    f"stays as drawn")
            redo.append(piece["id"])
        elif len(plan["flights"]) == 1 and "extra_treads" not in data:
            try:
                n, why = SA.run_extension(building, piece, plan, P.STAIR_WINDER_TARGET_RISER, STAIR["riser"][1])
            except Exception as exc:  # noqa: BLE001 - shapely's errors too: the point stays open with the reason
                n, why = 0, f"the floor at its foot cannot be measured ({type(exc).__name__})"
            if n:
                data["extra_treads"] = n
                _k1_label(piece, riser, f"its run is longer at its foot: {why}")
                redo.append(piece["id"])
            else:
                why_not[piece.get("id")] = why
    if redo and building is not None:
        from wenart.blender import shell
        again = []
        for lv in building.get("levels") or []:
            try:
                again += shell.plan_stairs(building, lv)
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
        stairs = again
    for item in stairs:
        piece, plan = item.get("piece") or {}, item.get("plan")
        if plan is None:
            continue
        r = float(plan.get("riser_m") or 0.0)
        gs = [float(f["going"]) for f in plan.get("flights") or []]
        ws = [float(f["width"]) for f in plan.get("flights") or []]
        g = min(gs) if gs else 0.0
        blondel = 2 * r + g
        issues = []
        if not STAIR["riser"][0] - 1e-6 <= r <= STAIR["riser"][1] + 1e-6:
            issues.append(f"riser {r:.3f} m outside {STAIR['riser'][0]:.2f}-{STAIR['riser'][1]:.2f} m")
        if g + 1e-6 < STAIR["going_min"]:
            issues.append(f"going {g:.2f} m under {STAIR['going_min']:.2f} m")
        if not STAIR["blondel"][0] - 0.01 <= blondel <= STAIR["blondel"][1] + 0.01:
            issues.append(f"2R+G {blondel:.2f} m outside {STAIR['blondel'][0]:.2f}-{STAIR['blondel'][1]:.2f} m")
        if ws and min(ws) + 1e-6 < STAIR["width_min"]:
            issues.append(f"{min(ws):.2f} m wide (< {STAIR['width_min']:.2f} m)")
        rails = plan.get("rails") or []
        built = (f"tread plates with nosings over painted risers, "
                 f"{'a ' + balustrade.replace('_', ' ') + ' balustrade on ' + str(len(rails)) + ' open side(s)' if rails else 'a wall handrail on brackets'}")
        element = str(piece.get("id"))
        quarter = len(plan.get("flights") or []) == 2 and abs(P._d2(plan["flights"][0]["rise_dir"],
                                                                     plan["flights"][1]["rise_dir"])) < 0.5
        if plan.get("winders"):
            # 28 Oct 2026 (parametric.WINDER_TREADS_NOTE): the turn's risers and its treads (one more)
            treads = len((plan.get("landing") or {}).get("winders") or []) or plan["winders"] + 1
            built = f"{treads} winder treads ({plan['winders']} risers) in the {'quarter' if quarter else 'half'} " \
                    f"landing, " + built
        extra = int((plan.get("flights") or [{}])[0].get("extra_treads") or 0)
        if extra:
            built = f"a run {extra} tread(s) longer at its foot, " + built
        if piece.get("id") in redo and not issues:
            keep = AA.option("stair_run", "keep the stair as drawn (steep)", piece_id=element, count=0) if extra \
                else AA.option("stair_winders", "keep the stair as drawn (steep)", piece_id=element, count=0)
            _ans(q, element, f"stair {element}: drawn with too few treads for its storey",
                 f"{'a longer run' if extra else 'winders'}: riser {r:.3f} m, going {g:.2f} m, 2R+G {blondel:.2f} m; "
                 f"built with {built}", options=[keep])
            continue
        if issues:
            opts = [AA.option("keep")]
            if len(plan["flights"]) == 2 and (plan.get("landing") or {}).get("role") == "mid":
                opts.insert(0, AA.option("stair_winders", piece_id=element, count="auto"))
            elif len(plan["flights"]) == 1 and not extra:
                opts.insert(0, AA.option("stair_run", piece_id=element, count="auto"))
            note = f"; {why_not[piece.get('id')]}" if why_not.get(piece.get("id")) else ""
            _open(q, element, f"stair {element}: " + "; ".join(issues) + f" (built: {built}){note}",
                  f"Is stair {element} drawn as it is meant (" + "; ".join(issues) + ")?", opts,
                  where=_where("stair", piece.get("level_id"), (piece.get("footprint") or {}).get("center") or (0, 0)))
        else:
            _ans(q, element, f"stair {element}: riser {r:.3f} m, going {g:.2f} m, 2R+G {blondel:.2f} m",
                 f"built with {built}")
    return q


def stair_walks(prep: dict) -> dict:
    """K4 (pure): the answers of the build's walk check of every stair (``prep["stair_access"]``,
    ``stair_access.fix_arrivals``): ok, changed (the reading it took, with the reason, the before and the after) or
    open (no reading leads into both floors: kept as drawn, asked)."""
    q = _q("K4")
    rec = prep.get("stair_access") if isinstance(prep.get("stair_access"), dict) else {}
    for row in rec.get("stairs") or []:
        element = str(row.get("stair"))
        if row.get("status") == "fixed":
            _ans(q, element, row.get("found") or "", row.get("change"), before=row.get("before"),
                 after=row.get("after"))
        elif row.get("status") == "open":
            tried = "; ".join(t["reading"] for t in row.get("tried") or []) or "no other reading"
            _open(q, element, f"{row.get('found')}; tried: {tried}",
                  f"How do people walk from stair {element} into the floor? Its arrival or start is cut off and no "
                  f"other reading of it leads into both floors.", [AA.option("keep")])
        else:
            _ans(q, element, row.get("found") or row.get("status") or "")
    return q


def guards(building: dict, prep: dict, balustrade: str) -> dict:
    """K2 (pure): the balconies' free edges, the roof terraces' parapets and the site platforms' drops."""
    q = _q("K2")
    for r in building.get("rooms") or []:
        if str(r.get("room_type") or "").lower() == "balcony":
            _ans(q, r["id"], f"balcony {r['id']}", f"a {GUARD_MIN_M:.2f} m {balustrade.replace('_', ' ')} balustrade "
                                                  f"on every edge without a wall (gaps under 0.11 m)")
    roof = prep.get("roof") or {}
    for o in roof.get("openings") or []:
        gh = o.get("guard_height")
        ph = o.get("parapet_height")
        if gh is None and ph is None:
            continue
        top = max(float(gh or 0.0), float(ph or 0.0))
        if top + 1e-6 < GUARD_MIN_M:
            _open(q, str(o.get("id")), f"roof terrace {o.get('id')}: guard {top:.2f} m",
                  f"Is the guard of roof terrace {o.get('id')} only {top:.2f} m high?", [AA.option("keep")])
        else:
            _ans(q, str(o.get("id")), f"roof terrace {o.get('id')}: parapet {float(ph or 0):.2f} m",
                 f"a coping on the parapet and a {balustrade.replace('_', ' ')} balustrade to {top:.2f} m"
                 if gh else "a coping on the parapet")
    for pf in (prep.get("site") or {}).get("platforms") or []:
        if pf.get("railing_edges") and not pf.get("parent"):
            _ans(q, pf["id"], f"{pf['kind']} {pf['id']}: {len(pf['railing_edges'])} edge(s) over a drop",
                 f"a {GUARD_MIN_M:.2f} m balustrade on them")
        if any(c.get("height_m", 0) > 1.2 for c in pf.get("cap_exceeded") or []):
            _ans(q, pf["id"], f"{pf['id']}: retaining walls over 1.2 m hold the ground above it",
                 "a guard on their tops (the fall from the ground into it)")
    # 26 Oct 2026: the edges of the stair voids in the floors (shell.floor_void_guards: every edge off a wall and off
    # the stair's arrival gets a balustrade; real06's upper landing had none)
    try:
        from wenart.blender import shell as SH
        by_level = ((prep.get("slabs") or {}).get("by_level") or {})
        for lv in building.get("levels") or []:
            under = (by_level.get(lv["id"]) or {}).get("under") or {}
            for g in SH.floor_void_guards(building, lv, under.get("voids") or []):
                _ans(q, f"void_{lv['id']}_{g['void']}", f"stair void of {lv['id']}: {g['length_m']:.2f} m of free "
                     f"edge", f"a {GUARD_MIN_M:.2f} m {balustrade.replace('_', ' ')} balustrade along it (the stair "
                     f"arrives from {', '.join(g['arrives_from']) or 'below'})")
    except (KeyError, TypeError, ValueError, AttributeError):
        pass
    return q


def one_language(balustrade: str, counts: dict) -> dict:
    q = _q("K3")
    _ans(q, "house", f"balustrades: {', '.join(f'{k} {v}' for k, v in counts.items() if v) or 'none'}",
         f"one kind for the house: {balustrade.replace('_', ' ')} (from the style)")
    return q


def decor_goal(building: dict, room: dict, family: Optional[str] = None) -> Optional[tuple[int, str]]:
    """S3's ``(minimum, why)`` of a room (pure; 27 Oct 2026; ``DECOR_MIN``): the decor stage's own minimum of the
    room (``decor_minimum``) when it kept one, else ``DECOR_MIN`` of its type scaled by the style family's density;
    None for a type S3 does not check."""
    from wenart.style import density as DN

    t = str(room.get("room_type") or "").lower()
    if t not in DECOR_MIN:
        return None
    kept = (building.get("decor_minimum") or {}).get(room.get("id"))
    if isinstance(kept, dict) and isinstance(kept.get("min"), int):
        return kept["min"], str(kept.get("why") or "the decor stage's minimum")
    level, why = DN.decor_density(None, family)
    return DN.decor_minimum(t, DECOR_MIN[t], level), why


def styled_rooms(building: dict, family: Optional[str] = None) -> list[dict]:
    """S2, S3, S4 (pure): the rooms' furniture as a set (the fit's ``asset.taste``), their decor (27 Oct 2026: against
    the room's minimum for its style, ``decor_goal``; ``family``: the project's style family) and their groups."""
    s2, s3, s4 = _q("S2"), _q("S3"), _q("S4")
    furn: dict = {}
    for f in building.get("furniture") or []:
        if f.get("build") is not False:
            furn.setdefault(f.get("room_id"), []).append(f)
    dec: dict = {}
    for d in building.get("decor") or []:
        dec.setdefault(d.get("room_id"), []).append(d)
    for r in building.get("rooms") or []:
        t = str(r.get("room_type") or "").lower()
        pieces = furn.get(r["id"], [])
        if not pieces:
            continue
        where = _where("room", r.get("level_id"), (sum(p[0] for p in r["polygon"]) / len(r["polygon"]),
                                                    sum(p[1] for p in r["polygon"]) / len(r["polygon"])))
        tastes = [(f["id"], (f.get("asset") or {}).get("taste")) for f in pieces
                  if isinstance((f.get("asset") or {}).get("taste"), dict)]
        if tastes:
            tones = sorted({x.get("wood_tone") for _i, x in tastes if x.get("wood_tone")})
            metals = sorted({x.get("metal") for _i, x in tastes if x.get("metal")})
            loud = [i for i, x in tastes if x.get("loud")]
            issues = ([f"{len(tones)} wood tones ({', '.join(tones)})"] if len(tones) > 2 else []) + \
                ([f"{len(metals)} metal finishes ({', '.join(metals)})"] if len(metals) > 1 else []) + \
                ([f"loud colours on {', '.join(loud[:3])}"] if len(loud) > 1 else [])
            if issues:
                _open(s2, r["id"], f"{r['id']}: " + "; ".join(issues), f"Do the pieces of {r['id']} go together?",
                      [AA.option("keep")], where=where)
            else:
                _ans(s2, r["id"], f"{r['id']}: wood {', '.join(tones) or '-'}, metal {', '.join(metals) or '-'}",
                     "chosen as a set by the fit (one wood tone and a contrast, one metal)")
        goal = decor_goal(building, r, family)
        if goal:
            want, why = goal
            n = len(dec.get(r["id"], []))
            if n < want:
                _open(s3, r["id"], f"{r['id']} ({t}) holds {n} decor item(s), a styled {t} {want} ({why})",
                      f"Is {r['id']} meant to stay this bare?", [AA.option("keep")], where=where)
            else:
                _ans(s3, r["id"], f"{r['id']} ({t}): {n} decor items (a styled {t} {want}: {why})")
        need = GROUP_NEEDS.get(t)
        if need and any(f.get("type") in need[0] for f in pieces):
            types = [str(f.get("type")) for f in pieces]
            missing = []
            for alts in need[1]:
                if len(set(alts)) == 1:
                    k = len(alts)
                    if types.count(alts[0]) < k:
                        missing.append(f"{k - types.count(alts[0])} {alts[0]}(s)")
                elif not any(a in types for a in alts):
                    missing.append(" or ".join(alts))
            if t == "living" and not any(d.get("type") == "rug" for d in dec.get(r["id"], [])):
                missing.append("a rug")
            if missing:
                _open(s4, r["id"], f"{r['id']} ({t}) misses " + ", ".join(missing),
                      f"Is the group in {r['id']} meant without " + ", ".join(missing) + "?", [AA.option("keep")],
                      where=where)
            else:
                _ans(s4, r["id"], f"{r['id']} ({t}): the group is complete")
    return [s2, s3, s4]


def review(building: dict, prep: dict, sides: list[dict], style: Optional[dict] = None) -> list[dict]:
    """The five rules (pure; ``architect.review`` appends them). ``style``: the project style (the balustrade kind);
    the build passes it through ``prep["style_family"]`` when it has one."""
    from wenart.blender import details as D
    from wenart.blender import shell

    plan = AA.Plan(building)
    style = style or ({"family": prep.get("style_family")} if prep.get("style_family") else None)
    kind = D.balustrade_kind(style)
    stairs = []
    for lv in building.get("levels") or []:
        try:
            stairs += shell.plan_stairs(building, lv)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue
    counts = {"stairs": sum(1 for s in stairs if s.get("plan") is not None),
              "balconies": sum(1 for r in building.get("rooms") or [] if r.get("room_type") == "balcony"),
              "roof terraces": sum(1 for o in (prep.get("roof") or {}).get("openings") or [] if o.get("guard_height")),
              "terraces": sum(1 for pf in (prep.get("site") or {}).get("platforms") or [] if pf.get("railing_edges"))}
    return [outdoor_furniture(plan), terrace_doors(plan, sides), stair_details(stairs, kind, building),
            stair_walks(prep), guards(building, prep, kind), one_language(kind, counts)] + \
        styled_rooms(building, (style or {}).get("family"))
