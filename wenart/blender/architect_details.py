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
    {"id": "K3", "topic": "one balustrade language", "scope": "house", "severity": "minor",
     "question": "Do the balustrades of the house (stairs, balconies, terraces, parapets) speak one language?",
     "why": "glass on one side and steel bars on the other look like two houses"},
    {"id": "S2", "topic": "furniture chosen together", "scope": "room", "severity": "minor",
     "question": "Does the furniture of every room look chosen together: one or two wood tones, one metal finish, "
                 "loud colours only from the style's palette?",
     "why": "a walnut table, a white oak bed and a pine chair with brass and chrome read as a second-hand shop"},
    {"id": "S3", "topic": "styled rooms", "scope": "room", "severity": "minor",
     "question": "Is every room styled with enough decor (a living room 9 items, a bedroom 7, a dining room 4)?",
     "why": "a room without lamps, plants, art, cushions and a rug looks unfinished in a render"},
    {"id": "S4", "topic": "complete furniture groups", "scope": "room", "severity": "minor",
     "question": "Is every furniture group complete: a sofa with a coffee table, an end table or a lamp and a rug; a "
                 "double bed with two nightstands; a dining table with four chairs or more?",
     "why": "a sofa alone or a bed with one nightstand looks half furnished"},
)
DECOR_MIN = {"living": 9, "bedroom": 7, "dining": 4, "kitchen": 2, "hall": 2, "bathroom": 2}   # decor_ai.ROOM_MIN
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


def stair_details(stairs: list[dict], balustrade: str, building: Optional[dict] = None) -> dict:
    """K1 (pure; ``building`` in place): ``stairs`` = ``shell.plan_stairs`` items of every level. A U stair drawn
    with risers over ``WINDER_AUTO_RISER`` (real04: 11 lines for a 3 m storey) gets winders in its half landing
    (``parametric.winder_treads``; its footprint as drawn, ``adjusted_by_ai`` with the reason) unless an answer set
    its ``winders``; the answer ``stair_winders`` with count 0 keeps it as drawn."""
    from wenart.blender import parametric as P

    q = _q("K1")
    redo = []
    for item in stairs:
        piece, plan = item.get("piece") or {}, item.get("plan")
        if plan is None:
            continue
        data = P.stair_data(piece)
        if (building is not None and isinstance(data, dict) and "winders" not in data and len(plan["flights"]) == 2
                and (plan.get("landing") or {}).get("role") == "mid" and float(plan["riser_m"]) > WINDER_AUTO_RISER):
            data["winders"] = "auto"
            piece["adjusted_by_ai"] = {"by": "architect", "rule": "architect K1",
                                       "reason": f"a riser of {float(plan['riser_m']):.3f} m is a drawing error (the "
                                                 f"stair is drawn with too few treads for its storey): the half "
                                                 f"landing becomes winders, the footprint stays as drawn"}
            redo.append(piece["id"])
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
        if plan.get("winders"):
            built = f"{plan['winders']} winders in the half landing, " + built
        if piece.get("id") in redo and not issues:
            _ans(q, element, f"stair {element}: drawn with too few treads for its storey",
                 f"winders: riser {r:.3f} m, going {g:.2f} m, 2R+G {blondel:.2f} m; built with {built}",
                 options=[AA.option("stair_winders", "keep the stair as drawn (steep)", piece_id=element, count=0)])
            continue
        if issues:
            opts = [AA.option("keep")]
            if len(plan["flights"]) == 2 and (plan.get("landing") or {}).get("role") == "mid":
                opts.insert(0, AA.option("stair_winders", piece_id=element, count="auto"))
            _open(q, element, f"stair {element}: " + "; ".join(issues) + f" (built: {built})",
                  f"Is stair {element} drawn as it is meant (" + "; ".join(issues) + ")?", opts,
                  where=_where("stair", piece.get("level_id"), (piece.get("footprint") or {}).get("center") or (0, 0)))
        else:
            _ans(q, element, f"stair {element}: riser {r:.3f} m, going {g:.2f} m, 2R+G {blondel:.2f} m",
                 f"built with {built}")
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


def styled_rooms(building: dict) -> list[dict]:
    """S2, S3, S4 (pure): the rooms' furniture as a set (the fit's ``asset.taste``), their decor and their groups."""
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
        want = DECOR_MIN.get(t)
        if want:
            n = len(dec.get(r["id"], []))
            if n < want:
                _open(s3, r["id"], f"{r['id']} ({t}) holds {n} decor item(s), a styled {t} {want}",
                      f"Is {r['id']} meant to stay this bare?", [AA.option("keep")], where=where)
            else:
                _ans(s3, r["id"], f"{r['id']} ({t}): {n} decor items")
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
            guards(building, prep, kind), one_language(kind, counts)] + styled_rooms(building)
