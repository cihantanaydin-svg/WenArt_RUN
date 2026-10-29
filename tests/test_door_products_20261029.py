"""Better door models (29 Oct 2026, user on real06 run 20261028-154514-full: "Better door models needed"; lesson UL89;
the 28 Oct requests "I want better doors inside the house and the outside ... some variation is needed", "find the best
models"). CPU, pure.

The run built 5 of its 13 doors (15 of its 23 door objects) as the parametric door, 7 as one 3D Warehouse model
("Residential Interior Door", four raised panels and a knob) and none as one of the 197 audited HSSD doors and
windows adopted that day. Why, and the general rules that fix it:

- the plan's build record (``opening_models.asset_of``) dropped ``source_url`` and ``via``, so the build's licence rule
  (``furniture.licence_refusal``: a CC BY licence and its NC variant need the credit line) refused every HSSD door and
  window ("CC BY 4.0 without source_url, via (no credit line); refused") and built the parametric opening; the plan
  now never chooses a model the build would refuse (``build_refusal``);
- a door whose leaf the audit's opening question never saw (the 3D Warehouse doors) ranks after the doors it saw
  (``look_fit``); a door named for one room ("bathroom door") serves only doors into such rooms (``model_rooms``);
- a pair of leaves takes two leaves of its role's model, mirrored to meet in the middle (``is_pair``,
  ``opening_build.pair_mirrors``); glazed doors that open two ways take a family each; the terrace and glazed doors
  are not the entrance's family when another fits;
- the parametric door, where nothing fits, is a product of the style family (``looks.door_product``,
  ``parametric.door_parts``): a routed or grooved leaf, an architrave, three hinges;
- the checks: model review M20 (``opening_models.door_product_problems``) and Argus U18
  (``opening_models.door_model_problems``)."""
import copy
import json
from pathlib import Path

import pytest

from wenart.audit import lessons as L
from wenart.blender import furniture as F
from wenart.blender import looks as LK
from wenart.blender import model_review as MR
from wenart.blender import opening_build as OB
from wenart.blender import opening_models as OM
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.blender import site_models as SM

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "wenart" / "furniture" / "catalog_library.json"
LATEST = ROOT / "results" / "baseline" / "latest"


@pytest.fixture(scope="module")
def extras():
    return OM.load_extras(CATALOGUE)


def _model(i, title, w=0.9, h=2.15, kind="door", styles=("modern",), q=3, **extra):
    e = {"id": f"m{i}", "type": kind, "kind": "opening", "title": title, "glb": f"m{i}.glb", "bbox_m": [w, 0.1, h],
         "styles": list(styles), "audit": {"status": "keep"}, "licence_flag": "non_commercial", "textured": True,
         "audit_quality": q}
    e.update(extra)
    return e


def _outer(oid, width, top=2.1, kind="door", **o):
    return {"opening": dict({"id": oid, "type": kind, "width": width}, **o), "bottom": 0.0, "top": top,
            "outward": [0, -1]}


def _house(pair=False):
    """Living | hall | bedroom over bathroom: the inner walls at x = 5 and 7; a door from the hall into each room."""
    rooms = [{"id": "r_liv", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [5, 0], [5, 7], [0, 7]]},
             {"id": "r_hall", "level_id": "L0", "room_type": "hall", "polygon": [[5, 0], [7, 0], [7, 7], [5, 7]]},
             {"id": "r_bed", "level_id": "L0", "room_type": "bedroom", "polygon": [[7, 0], [11, 0], [11, 4], [7, 4]]},
             {"id": "r_bath", "level_id": "L0", "room_type": "bathroom", "polygon": [[7, 4], [11, 4], [11, 7], [7, 7]]}]
    walls = [{"id": "w5", "level_id": "L0", "start": [5, 0], "end": [5, 7], "thickness": 0.1},
             {"id": "w7", "level_id": "L0", "start": [7, 0], "end": [7, 7], "thickness": 0.1}]
    liv = {"id": "d_liv", "type": "door", "level_id": "L0", "wall_id": "w5", "center": [5, 3], "width": 0.9,
           "height": 2.1, "swing_side": "r_liv"}
    if pair:
        liv.update(width=1.6, door_type="double", operation="double", leaves=2)
    openings = [liv,
                {"id": "d_bed", "type": "door", "level_id": "L0", "wall_id": "w7", "center": [7, 2], "width": 0.8,
                 "height": 2.1, "swing_side": "r_bed"},
                {"id": "d_bath", "type": "door", "level_id": "L0", "wall_id": "w7", "center": [7, 5.5], "width": 0.8,
                 "height": 2.1, "swing_side": "r_bath"}]
    levels = [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}]
    return {"project": {"id": "house_t"}, "levels": levels, "walls": walls, "rooms": rooms, "openings": openings}


SCANDI = {"family": "scandinavian", "door": {"material": "wood_oak_light"}}
FLUSH = {"role": "inside", "glazing": "none", "leaf": "flush", "handle_side": "left"}
GLAZED = {"role": "inside", "glazing": "clear", "leaf": "glazed", "handle_side": "left"}


# --------------------------------------------------------------------------
# the cause: the build refused every HSSD door the plan chose
# --------------------------------------------------------------------------

def test_the_build_record_carries_the_credit_line(extras):
    assert OM.CREDIT_FIELDS == F.CC_BY_FIELDS
    by = {e["id"]: e for e in extras}
    for aid in ("hssd_4141-3", "hssd_3262-7", "hssd_6161-2", "hssd_203-1", "hssd_3753-20"):   # real06, real04
        if aid not in by:
            pytest.skip(f"{aid} not in the catalogue")
        asset = OM.asset_of(by[aid])
        assert all(str(asset.get(k) or "").strip() for k in OM.CREDIT_FIELDS), aid
        assert F.licence_refusal(asset) is None, aid
        # the record of the 28 Oct plan (no source_url, no via) is what the build refused
        old = {k: v for k, v in asset.items() if k not in ("source_url", "via")}
        assert "without source_url, via" in F.licence_refusal(old)
        assert F.licence_refusal(SM.asset_of(by[aid])) is None                   # the site models' record too


def test_every_door_and_window_the_plan_may_choose_reaches_the_build(extras):
    seen = {}
    for cat in ("entrance", "door", "glazed_door", "terrace_door", "window", "inside_door"):
        cands = OM.candidates(extras, cat, "relaxed")
        refused = {e["id"]: F.licence_refusal(OM.asset_of(e)) for e in cands if F.licence_refusal(OM.asset_of(e))}
        assert refused == {}, (cat, list(refused.items())[:3])
        seen[cat] = sum(1 for e in cands if e.get("source") == "hssd")
    assert seen["inside_door"] and seen["entrance"] and seen["window"] and seen["glazed_door"]


def test_a_model_the_build_would_refuse_is_never_planned(extras):
    hssd = next((e for e in extras if e.get("id") == "hssd_200-32"), None)
    if hssd is None:
        pytest.skip("no hssd_200-32 in the catalogue")
    broken = dict(copy.deepcopy(hssd), id="hssd_broken", source_url="")
    assert "source_url" in OM.build_refusal(broken) and OM.build_refusal(hssd) is None
    ids = [e["id"] for e in OM.candidates([hssd, broken], "inside_door", "relaxed")]
    assert ids == ["hssd_200-32"]
    assert OM.build_refusal({"id": "x", "title": "fixture"}) is None          # no catalogue licence: not judged


# --------------------------------------------------------------------------
# the choice: audited leaves first, a door named for a room, pairs, two ways, the entrance's family
# --------------------------------------------------------------------------

def test_a_door_whose_leaf_the_audit_never_saw_ranks_after_the_audited_ones():
    look = OM.look_of(SCANDI)
    unseen = _model(1, "Residential Interior Door", styles=("minimal", "modern", "scandinavian"))
    seen = _model(2, "HSSD door 200-32", w=0.91, h=2.2, styles=("minimal", "modern"), series="hssd:200",
                  opening_vision=FLUSH)
    r1, why1 = OM.look_fit(unseen, look, None, "inside_door")
    assert r1 == OM.LEAF_UNKNOWN_RANK and "never" not in why1 and "not seen" in why1
    assert OM.look_fit(seen, look, None, "inside_door")[0] == 1
    assert OM.look_fit(unseen, look, None, "glazed_door")[0] == 0            # a glazed door: its glass from the file
    assert OM.look_fit(dict(unseen, type="window"), look, None, "window")[0] == 0
    b = _house()
    recs = [r for r in OM.inside_records(b, b["levels"]) if r["opening"]["id"] == "d_bed"]
    plan = OM.plan_inside(b, recs, [unseen, seen], style=SCANDI)
    assert plan["d_bed"]["asset"]["asset_id"] == "m2" and plan["d_bed"]["leaf"] == "flush"
    assert OM.plan_inside(b, recs, [unseen], style=SCANDI)["d_bed"]["asset"]["asset_id"] == "m1"   # still usable


def test_a_door_named_for_one_room_serves_only_those_rooms():
    assert OM.model_rooms({"title": "bathroom door"}) == {"bathroom", "wc"}
    assert OM.model_rooms({"title": "HSSD door 200-32 (0.91 x 2.20 m)"}) == set()
    assert OM.model_rooms({"title": "Bedroom Door White"}) == {"bedroom"}
    b = _house()
    recs = [r for r in OM.inside_records(b, b["levels"]) if r["opening"]["id"] in ("d_bed", "d_bath")]
    bath = _model(1, "bathroom door", w=0.9, h=2.05, q=4, opening_vision=FLUSH)
    flush = _model(2, "HSSD door 200-32", w=0.91, h=2.2, series="hssd:200", opening_vision=FLUSH)
    notes: list = []
    plan = OM.plan_inside(b, recs, [bath, flush], style=SCANDI, notes=notes)
    assert {v["asset"]["asset_id"] for v in plan.values()} == {"m2"}           # q4, but made for a bathroom
    left = next(n for n in notes if n["kind"] == "left_out" and n["category"] == "inside_door:solid")
    assert "bathroom" in left["models"]["m1"] and "d_bed" in left["models"]["m1"]
    only_bath = [r for r in recs if r["opening"]["id"] == "d_bath"]
    assert OM.plan_inside(b, only_bath, [bath, flush], style=SCANDI)["d_bath"]["asset"]["asset_id"] == "m1"


def test_a_pair_of_leaves_takes_two_leaves_of_its_roles_model():
    b = _house(pair=True)
    recs = {r["opening"]["id"]: r for r in OM.inside_records(b, b["levels"])}
    assert OM.is_pair(recs["d_liv"]["opening"]) and not OM.is_pair(recs["d_bed"]["opening"])
    assert not OM.is_pair({"door_type": "sliding_pair", "leaves": 2})
    role, why = OM.inside_role(recs["d_liv"], SCANDI)
    assert role == "glazed" and "pair" in why                                   # = looks.role_door_style
    glazed = _model(1, "HSSD door 202-0", w=0.98, h=2.2, series="hssd:202", opening_vision=GLAZED)
    solid = _model(2, "HSSD door 200-32", w=0.91, h=2.2, series="hssd:200", opening_vision=FLUSH)
    notes: list = []
    plan = OM.plan_inside(b, list(recs.values()), [glazed, solid], style=SCANDI, notes=notes)
    liv = plan["d_liv"]
    assert liv["asset"]["asset_id"] == "m1" and liv["panels"] == 2 and liv["pair"] is True
    assert liv["handle_side"] == "left" and liv["mirror"] is False and "pair" in liv["hinge"]
    assert "2 panel(s) of 0.80 x 2.10 m" in liv["reason"]
    assert not [n for n in notes if n["kind"] == "parametric"]
    # the build: the leaves meet in the middle with their handles there (seen from the front: outward)
    assert OB.pair_mirrors(2, (1, 0), (0, -1), "left") == [True, False]        # the left leaf turned
    assert OB.pair_mirrors(2, (1, 0), (0, -1), "right") == [False, True]
    assert OB.pair_mirrors(2, (-1, 0), (0, -1), "left") == [False, True]       # the wall the other way
    assert OB.pair_mirrors(2, (1, 0), (0, 1), "left") == [False, True]         # seen from the other side
    assert OB.pair_mirrors(2, (1, 0), (0, -1), None) == [False, True]          # unknown: mirror images
    assert OB.pair_mirrors(3, (1, 0), (0, -1), "left")[1] is False             # a middle leaf as modelled
    xs = sorted({round(sum(v[0] for v in p[0]) / len(p[0]), 3) for p in SH.door_handle_parts(1.6, 2.1, pair=True)})
    assert min(xs) < 0 < max(xs) and max(abs(x) for x in xs) < 0.2            # the levers at the meeting stiles


def test_glazed_doors_that_open_two_ways_take_a_family_each():
    sliding = _model(1, "HSSD sliding door 6161-2", w=2.4, h=2.2, series="hssd:6161",
                     opening={"kind": "sliding", "operation": "sliding"},
                     opening_vision={"glazing": "clear", "operation": "sliding", "leaves": 2})
    french = _model(2, "HSSD double door 208-11", w=1.9, h=2.2, series="hssd:208",
                    opening={"kind": "double", "operation": "hinged"},
                    opening_vision={"glazing": "clear", "operation": "hinged", "leaves": 2})
    outer = [_outer("s1", 2.4, top=2.2, door_type="glazed_sliding"), _outer("s2", 2.5, top=2.2, door_type="glazed_sliding"),
             _outer("f", 1.98, top=2.2, door_type="french")]
    notes: list = []
    plan = OM.plan({}, outer, [sliding, french], style={"family": "modern"}, notes=notes)
    assert plan["s1"]["asset"]["asset_id"] == plan["s2"]["asset"]["asset_id"] == "m1"
    assert plan["f"]["asset"]["asset_id"] == "m2" and "open hinged" in plan["f"]["reason"]
    assert not [n for n in notes if n["kind"] == "parametric"]
    # a one-leaf glazed model in two panels of a hinged door is a pair (the build mirrors one leaf)
    leaf = _model(3, "HSSD glazed door 9-1", w=1.3, h=2.2, series="hssd:9",
                  opening={"kind": "single", "operation": "hinged"},
                  opening_vision={"glazing": "clear", "operation": "hinged", "leaves": 1, "handle_side": "right"})
    wide = OM.plan({}, [_outer("w", 2.6, top=2.2, door_type="french")], [leaf], style={"family": "modern"})
    assert wide["w"]["panels"] == 2 and wide["w"]["pair"] is True and wide["w"]["handle_side"] == "right"


def test_the_terrace_doors_are_not_the_entrance_family_when_another_fits():
    front = _model(1, "HSSD door 4141-3", w=0.91, h=2.13, q=4, series="hssd:4141",
                   opening_vision={"role": "entrance", "glazing": "clear", "leaf": "glazed"})
    terrace = _model(2, "HSSD door 204-3", w=0.9, h=2.15, q=3, series="hssd:204",
                     opening_vision={"glazing": "clear", "leaf": "glazed"})
    b = {"site": {"entrances": [{"door_id": "e", "main": True}]}}
    outer = [_outer("e", 0.9), _outer("t", 0.9, outside_door={"reason": "a door to the terrace"})]
    plan = OM.plan(b, outer, [front, terrace], style={"family": "modern"})
    assert plan["e"]["asset"]["asset_id"] == "m1" and plan["t"]["category"] == "terrace_door"
    assert plan["t"]["asset"]["asset_id"] == "m2" and "another family than the entrance's" in plan["t"]["reason"]
    notes: list = []
    shared = OM.plan(b, outer, [front], style={"family": "modern"}, notes=notes)     # nothing else: one language
    assert shared["t"]["asset"]["asset_id"] == "m1" and any(n["kind"] == "shared_family" for n in notes)


# --------------------------------------------------------------------------
# the parametric door where nothing fits: a product of the style family
# --------------------------------------------------------------------------

def test_the_parametric_door_is_a_product_of_the_style_family():
    look = LK.door_look(SCANDI, {"id": "d", "type": "door", "joins": ["hall", "bedroom"]})
    assert look["door_style"] == "flush" and look["leaf_detail"] == {"kind": "lined"}
    assert look["architrave"] is True and look["hinges"] is True and "architrave" in look["reason"]
    assert LK.door_product({"family": "modern"})["leaf_detail"] == {"kind": "horizontal", "count": 4}
    assert LK.door_product({"family": "japandi"})["leaf_detail"]["kind"] == "vertical"
    assert LK.door_product({"family": "classic"})["leaf_detail"]["kind"] == "panelled"
    assert LK.door_product({"family": "modern", "door": {"leaf_detail": "plain"}})["leaf_detail"] == {"kind": "plain"}
    assert LK.door_product({"door": {"material": "wood_oak_light"}}) == {}       # a style without a family: as before
    assert LK.door_geometry_m10(SCANDI, {"id": "d", "operation": "swing"})
    assert not LK.door_geometry_m10({"door": {"material": "wood_oak_light"}}, {"id": "d", "operation": "swing"})
    w, h, t = 0.9, 2.1, 0.12
    parts, rec = P.door_parts(dict(look, side=1.0, architrave_faces=(1.0, -1.0)), w, h, t)
    roles = [p["role"] for p in parts]
    assert rec["leaf_detail"] == "lined" and rec["architrave"] == [-1, 1] and rec["hinges"] == 3
    assert OM.is_product_door(rec)
    arch = [p for p in parts if p["role"] == "architrave"]
    assert len(arch) == 6 and all(p["key"] == "frame" for p in arch)
    assert all(abs(v[1]) >= t / 2.0 - 1e-9 for p in arch for v in p["verts"])     # on the wall faces
    assert max(abs(v[0]) for p in arch for v in p["verts"]) > w / 2.0            # it covers the joint to the wall
    leaf_t = rec["leaf_thickness"]
    boards = [p for p in parts if p["role"] == "leaf"]
    assert len(boards) == 11 and all(abs(v[1]) <= leaf_t / 2.0 + 1e-9 for p in boards for v in p["verts"])
    hinges = [p for p in parts if p["role"] == "hinge"]
    lever_x = min(v[0] for p in parts if p["role"] == "handle" for v in p["verts"])
    assert len(hinges) == 3 and all(p["key"] == "handle" for p in hinges)
    assert all(max(v[0] for v in p["verts"]) < 0 < lever_x for p in hinges)      # opposite the lever
    assert all(min(v[1] for v in p["verts"]) >= -1e-9 for p in hinges)           # on the swing face (side +1)
    assert "frame" in roles and "stop" in roles
    # grooves: the face boards of a grooved leaf leave gaps of the groove's width
    grooved, rec2 = P.door_parts(dict(LK.door_look({"family": "modern"}, {"id": "d", "type": "door"}), side=-1.0), w, h, t)
    faces = sorted({(round(min(v[2] for v in p["verts"]), 4), round(max(v[2] for v in p["verts"]), 4))
                    for p in grooved if p["role"] == "leaf" and min(v[1] for v in p["verts"]) > 0})
    gaps = [round(b[0] - a[1], 4) for a, b in zip(faces, faces[1:])]
    assert rec2["leaf_detail"] == "horizontal" and len(faces) == 5 and gaps == [P.LEAF_GROOVE_W_M] * 4
    # an outside door: the architrave on its room face only (never on the facade)
    wall = {"start": [0, 0], "end": [4, 0], "thickness": 0.3}
    room = [{"id": "r", "room_type": "living", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}]
    assert SH.architrave_faces((2.0, 0.0), wall, room) == (1.0,)
    terrace = room + [{"id": "t", "room_type": "terrace", "polygon": [[0, -3], [4, -3], [4, 0], [0, 0]]}]
    assert SH.architrave_faces((2.0, 0.0), wall, terrace) == (1.0,)
    assert SH.architrave_faces((2.0, 5.0), wall, room) == (1.0, -1.0)             # no room found: both
    assert "architrave" in SH.FRAME_ROLES
    # a pair, glazed doors, sliding doors
    pair, prec = P.door_parts(dict(LK.door_look(SCANDI, {"id": "d", "type": "door", "operation": "double"}),
                                   side=1.0), 1.6, 2.1, t)
    assert prec["hinges"] == 6 and prec["leaf_detail"] == "lined"
    slide, srec = P.door_parts(dict(LK.door_look(SCANDI, {"id": "d", "type": "door", "operation": "sliding"}),
                                    side=1.0), 0.9, 2.1, t)
    assert srec["surface_mounted"] and not [p for p in slide if p["role"] in ("architrave", "hinge")]
    assert OM.is_product_door(srec)


# --------------------------------------------------------------------------
# the checks: model review M20, Argus U18
# --------------------------------------------------------------------------

def _manifest():
    def door(oid, **kw):
        return dict({"kind": "door", "element_id": oid, "wenart_id": oid, "name": f"{oid}_leaf"}, **kw)
    product = {"door_style": "flush", "architrave": [-1, 1], "leaf_detail": "lined", "hinges": 3}
    return {"objects": [
        door("a", name="a_lib0", library_model={"asset_id": "hssd_200-32", "title": "HSSD door 200-32",
                                                "category": "inside_door", "role": "solid", "leaf": "flush"},
             room_ids=["r_hall", "r_bed"]),
        door("b", door={"door_style": "flush", "parts": ["frame", "leaf"]}),
        door("c", door=product, library_planned={"asset_id": "hssd_4141-3", "title": "HSSD door 4141-3",
                                                 "category": "entrance", "why": "asset file missing"}),
        door("d", door=product),
        door("e"),
        door("f", name="f_lib0", library_model={"asset_id": "3dwh_x", "title": "bathroom door",
                                                "category": "inside_door", "role": "solid"},
             room_ids=["r_hall", "r_bed"])],
        "warnings": ["e: library entrance not built (asset 'hssd_4141-3' is CC BY 4.0 without source_url, via (no "
                     "credit line); refused); parametric opening", "x: something else"]}


def test_model_review_m20_finds_a_planned_door_the_build_did_not_make_and_a_bare_door():
    assert "M20" in MR.CHECKS
    got, n = MR.door_products(_manifest())
    assert n == 6
    by = {f["target"]: f for f in got}
    assert set(by) == {"b", "c", "e"}
    assert by["c"]["metrics"]["problem"] == "library_door_not_built" and by["c"]["kind"] == "lost"
    assert "HSSD door 4141-3" in by["c"]["message"] and "asset file missing" in by["c"]["message"]
    assert "without source_url" in by["e"]["message"]                          # read from an older manifest's warnings
    assert by["b"]["metrics"]["problem"] == "bare_door" and "no architrave" in by["b"]["message"]
    rec = SH.library_planned_record({"asset": {"asset_id": "m1", "title": "T"}, "category": "inside_door",
                                     "role": "solid"}, ["d: library inside_door not built (x); parametric opening"])
    entries = [{"element_id": "d"}, {"element_id": "z"}]
    assert SH.tag_library_planned(entries, "d", rec) == 1 and entries[0]["library_planned"]["asset_id"] == "m1"
    review = MR.review({"levels": [], "rooms": [], "openings": [], "walls": []}, _manifest(), prep={})
    assert review["checks"]["M20"]["failed"] == 3


def test_argus_u18_finds_a_house_of_parametric_doors_and_a_door_for_another_room():
    building = {"rooms": [{"id": "r_hall", "room_type": "hall"}, {"id": "r_bed", "room_type": "bedroom"}]}
    found = OM.door_model_problems(_manifest(), building)
    kinds = {p["kind"]: p for p in found}
    assert set(kinds) == {"parametric_doors", "door_for_another_room"}
    assert "4 of the house's 6 doors" in kinds["parametric_doors"]["message"]
    assert "2 of them had a library model the build did not make (c, e)" in kinds["parametric_doors"]["message"]
    assert kinds["door_for_another_room"]["target"] == "f"
    audit = L.audit(building, _manifest())
    assert audit["checked"]["U18"] == 2 and L.CHECK_LESSONS["U18"][0] == "UL89"
    assert {f["check"] for f in audit["findings"] if f["evidence"].get("lesson") == "UL89"} == {"U18"}
    fine = {"objects": [o for o in _manifest()["objects"] if o["element_id"] in ("a", "d")]}
    assert OM.door_model_problems(fine, building) == []


# --------------------------------------------------------------------------
# the latest runs (results/baseline/latest): every door a buildable library model where one fits
# --------------------------------------------------------------------------

@pytest.mark.parametrize("project,family", [("real06", "scandinavian"), ("real04", "modern")])
def test_the_latest_houses_get_buildable_library_doors_by_role(project, family):
    from wenart.blender import build as BB

    path = LATEST / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip(f"no latest {project} building")
    prep = BB.prepare(json.loads(path.read_text(encoding="utf-8")), "base", None)
    b = prep["building"]
    plan = BB.library_openings(b, b["levels"], prep, None, [], style={"family": family})
    doors = [o for o in b["openings"] if o.get("type") == "door"]
    assert plan and all(F.licence_refusal(v["asset"]) is None for v in plan.values())
    para = [o["id"] for o in doors if o["id"] not in plan]
    # every door gets a model but one no real product fits (real04's 1.01 m high doors under its roof)
    assert all(float(o.get("height") or 2.1) < 1.5 for o in doors if o["id"] in para), para
    assert sum(1 for v in plan.values() if (v["asset"].get("library") == "hssd")) >= len(doors) // 2
    rooms = {r["id"]: r for r in b["rooms"]}
    for o in doors:
        e = plan.get(o["id"])
        if e and e.get("category") == "inside_door":
            named = OM.model_rooms({"title": e["asset"].get("title")})
            assert not named, (o["id"], e["asset"].get("title"))
    assert not [p for p in OM.door_variety_problems(plan) if p["severity"] == "major"]
    assert rooms                                                                   # the building was read


def test_m20_reads_the_refused_hssd_doors_of_run_154514():
    runs = LATEST / "runs.json"
    man = LATEST / "renders" / "real06" / "scene_manifest.json"
    if not runs.is_file() or not man.is_file() or \
            json.loads(runs.read_text(encoding="utf-8")).get("real06", {}).get("job") != "20261028-154514-full":
        pytest.skip("the latest real06 run is not 20261028-154514-full")
    got, n = MR.door_products(json.loads(man.read_text(encoding="utf-8")))
    lost = {f["target"] for f in got if f["metrics"]["problem"] == "library_door_not_built"}
    assert n == 13 and lost == {"d_L0_004", "d_L0_005", "d_L0_006"}
