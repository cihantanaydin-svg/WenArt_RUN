"""What kind of door every outside door is (user on real06's facade, 26 Oct 2026: "these sections not making sense": the
living room's 2.95 m outside door was one flat oak leaf as wide as the opening, a garage door on a house with no
garage). The architect's rule D5 decides the kind of every outside door and every wide door (French doors or a glazed
sliding door into a room, the entrance door, a sectional garage door, two leaves inside), its safe default is carried
out by the build (``build.prepare``), the drawn values stay, and the parametric builder makes glazed leaves and panels
instead of one slab. A door nobody decided builds exactly as before. CPU only; real06 is the trimmed copy of its
25 Oct 2026 run (tests/fixtures/real06_building_20261025.json)."""
import copy
import json
from pathlib import Path

import pytest

from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.blender import build as BB
from wenart.blender import looks
from wenart.blender import opening_models as OM
from wenart.blender import parametric as P
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"
STYLE = {"door": {"material": "wood_oak_light"}, "window_frame": {"material": "aluminium_anthracite"}}


@pytest.fixture(scope="module")
def drawn():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"          # no user answers
    return b


@pytest.fixture(scope="module")
def prep(drawn):
    return BB.prepare(copy.deepcopy(drawn), "base", None)


def _opening(building, oid):
    return next((o for o in building["openings"] if o["id"] == oid), None)


def leaf_units(parts) -> list[float]:
    """The widths of the leaves and panels of a door: its leaf and glass parts merged by their line across the wall
    and their overlap along it (a glazed leaf's stiles, rails and glass are one leaf)."""
    rows: dict = {}
    for p in parts:
        if p["role"] not in ("leaf", "glass"):
            continue
        xs, ys = [v[0] for v in p["verts"]], [v[1] for v in p["verts"]]
        rows.setdefault(round((min(ys) + max(ys)) / 2.0, 3), []).append((min(xs), max(xs)))
    out = []
    for spans in rows.values():
        spans.sort()
        a, b = spans[0]
        for x0, x1 in spans[1:]:
            if x0 < b - 1e-6:
                b = max(b, x1)
            else:
                out.append(b - a)
                a, b = x0, x1
        out.append(b - a)
    return out


def first_gap(parts, x_lo, x_hi, z_lo, z_hi):
    """The first (x, z) of the clear opening not covered by any part in projection across the wall, or None."""
    boxes = []
    for p in parts:
        xs, zs = [v[0] for v in p["verts"]], [v[2] for v in p["verts"]]
        boxes.append((min(xs), max(xs), min(zs), max(zs)))
    cuts = sorted({z_lo, z_hi} | {z for b in boxes for z in b[2:] if z_lo < z < z_hi})
    for z0, z1 in zip(cuts, cuts[1:]):
        zm = (z0 + z1) / 2.0
        x = x_lo
        for a, c in sorted((b[0], b[1]) for b in boxes if b[2] <= zm <= b[3]):
            if a > x + 1e-9:
                break
            x = max(x, c)
        if x < x_hi - 1e-9:
            return round(x, 4), round(zm, 4)
    return None


# --------------------------------------------------------------------------
# real06: the living room's doors
# --------------------------------------------------------------------------

def test_real06_wide_outside_doors_are_glazed_by_the_architects_default(prep, drawn):
    b = prep["building"]
    big = _opening(b, "d_L0_006")              # 2.95 m, drawn sliding (six leaf lines), the main entrance record
    assert big["door_type"] == "glazed_sliding" and big["door_style"] == "glazed_sliding" and big["glazed"]
    assert big["leaves"] == 3 and big["door_decision"]["outer"] and big["door_decision"]["answer_by"] == "architect"
    assert "main entrance" in big["door_decision"]["found"]
    front = _opening(b, "d_L0_001")            # 2.15 m, drawn sliding
    assert front["door_type"] == "glazed_sliding" and front["leaves"] == 2
    for oid in ("o_L0_005", "o_L0_006"):       # 1.55 m gaps the architect made doors (O2): French doors
        o = _opening(b, oid)
        assert o["door_type"] == "french" and o["operation"] == "double" and o["glazed"] and o["leaves"] == 2
    assert prep["architect_defaults"]["D5:d_L0_006"]["option"] == "door_type"
    assert prep["architect_defaults"]["D5:d_L0_006"]["params"]["kind"] == "glazed_sliding"
    # one leaf where one leaf is right: the 0.80 m swing door to the living room, the inside doors
    for oid in ("d_L0_004", "d_L0_005", "d_L1_002"):
        assert "door_type" not in _opening(b, oid)
    d5 = next(q for q in prep["architect"]["questions"] if q["id"] == "D5")
    assert not any(a.get("open") for a in d5["answers"]) and d5["counts"]["answered"] >= 4
    assert "D5 door types" in AR.report_md(prep["architect"], "real06")


def test_real06_wide_inside_door_gets_two_sliding_leaves(prep):
    o = _opening(prep["building"], "d_L0_002")    # 1.95 m between the kitchen and the living room, drawn sliding
    assert o["door_type"] == "sliding_pair" and o["door_style"] == "sliding" and not o["glazed"]
    assert o["leaves"] == 2 and not o["door_decision"]["outer"]
    look = looks.door_look(STYLE, o)
    assert look["door_style"] == "sliding" and look["leaves"] == 2 and look["material"] != "aluminium_anthracite"
    parts, rec = P.door_parts(dict(look, side=1), float(o["width"]), 2.1, 0.12)
    assert rec["leaves"] == 2 and max(leaf_units(parts)) <= P.LEAF_MAX_M - 0.15


def test_real06_drawn_values_stay(prep, drawn):
    before = {o["id"]: o for o in drawn["openings"]}
    b = prep["building"]
    for oid in ("d_L0_006", "d_L0_001", "d_L0_002"):
        o = _opening(b, oid)
        assert o["width"] == before[oid]["width"] and o["center"] == before[oid]["center"]
        assert o["operation"] == before[oid]["operation"] == "sliding" and "drawn_operation" not in o
    gap = _opening(b, "o_L0_005")
    assert gap["drawn_type"] == "opening" and gap["drawn_operation"] is None
    assert gap["width"] == before["o_L0_005"]["width"]


def test_real06_glazed_doors_share_the_glazed_door_family(prep):
    b = prep["building"]
    outer = S.outer_openings(b, b["levels"], prep.get("ground_outline") or [], prep.get("outlines"))
    cats = OM.categorise(b, outer)
    assert cats["d_L0_006"] == "glazed_door" and cats["d_L0_001"] == "glazed_door"      # not "entrance"
    assert cats["o_L0_002"] == "terrace_door"         # a 1.10 m glazed door (a gap made a door): never a solid one
    extras = OM.load_extras(ROOT / "wenart" / "furniture" / "catalog_library.json")
    if not OM.candidates(extras, "glazed_door", "relaxed"):
        pytest.skip("no glazed doors in the catalogue")
    notes: list = []
    plan = OM.plan(b, outer, extras, "relaxed", style={"family": "scandinavian"}, notes=notes)
    glazed = {k: v for k, v in plan.items() if v["category"] == "glazed_door"}
    assert len({v["family"] for v in glazed.values()}) <= 1                    # one glazed door look
    # the 2.95 m door takes that family's model, or (no member fits) the parametric glazed sliding door of D5
    if "d_L0_006" not in plan:
        assert any(n["kind"] == "parametric" and n["id"] == "d_L0_006" and n["category"] == "glazed_door"
                   for n in notes)
    assert plan.get("d_L0_004", {}).get("category") != "entrance"


def test_a_user_keep_answer_leaves_the_door_as_drawn(drawn):
    b = copy.deepcopy(drawn)
    b["architect_answers"] = {"D5:d_L0_006": {"option": "keep", "answer": "a slab on purpose"}}
    prep = BB.prepare(b, "base", None)
    o = _opening(prep["building"], "d_L0_006")
    assert "door_type" not in o and "D5:d_L0_006" not in prep["architect_defaults"]
    assert _opening(prep["building"], "d_L0_001")["door_type"] == "glazed_sliding"


# --------------------------------------------------------------------------
# The rule: French or sliding by width, the garage, the entrance
# --------------------------------------------------------------------------

@pytest.mark.parametrize("width,op,kind", [
    (1.30, None, None), (1.40, "swing", "french"), (2.40, None, "french"), (2.41, None, "glazed_sliding"),
    (3.20, "swing", "glazed_sliding"), (1.80, "sliding", "glazed_sliding"), (3.00, "folding", "glazed_folding"),
    (2.60, "double", "french")])
def test_outside_doors_into_rooms_french_up_to_2_4_m_then_sliding(width, op, kind):
    got, why, others = AA.door_kind(width, ["living"], True, False, op)
    assert got == kind
    if kind:
        assert "never one leaf" in why and kind not in others and set(others) <= set(AA.GLAZED_KINDS)


def test_the_leaves_are_never_much_wider_than_1_2_m():
    assert AA.door_leaves("glazed_sliding", 2.95) == 3 and AA.door_leaves("glazed_sliding", 2.15) == 2
    assert AA.door_leaves("glazed_folding", 3.0) == 4 and AA.door_leaves("french", 2.4) == 2
    for w in (1.4, 1.9, 2.4, 2.95, 3.6, 4.8):
        for kind in ("glazed_sliding", "sliding_pair"):
            assert (w - AA.DOOR_FRAMES_M) / AA.door_leaves(kind, w) <= AA.LEAF_MAX_M + 1e-9
        assert (w - AA.DOOR_FRAMES_M) / AA.door_leaves("glazed_folding", w) <= AA.FOLDING_LEAF_M + 1e-9


@pytest.mark.parametrize("room,width,kind", [
    ("garage", 2.6, "garage_sectional"), ("carport", 2.2, "garage_sectional"), ("garage", 2.0, "double"),
    ("storage", 1.6, "double"), ("technical", 3.0, "garage_sectional"), ("garage", 0.9, None)])
def test_a_wide_door_into_a_garage_is_a_sectional_door(room, width, kind):
    assert AA.door_kind(width, [room], True, False, None)[0] == kind


def test_the_main_entrance_is_the_entrance_door_and_a_drawn_slider_stays_a_slider():
    assert AA.door_kind(1.0, ["hall"], True, True, "swing")[0] == "entrance"
    assert AA.door_kind(1.8, ["hall"], True, True, None)[0] == "entrance"            # side lights beside one leaf
    assert AA.door_kind(2.95, ["living"], True, True, "sliding")[0] == "glazed_sliding"
    assert AA.door_kind(1.0, ["living"], True, True, "sliding")[0] is None           # a narrow drawn slider: as drawn
    assert AA.door_kind(1.0, ["hall"], True, False, "swing")[0] is None              # another outside door


def _house(main_width: float = 1.0) -> dict:
    """A garage, a hall and a living room in a row on one floor, 6 m deep; the main entrance into the hall."""
    walls = [("ws", (0, 0), (16, 0)), ("wn", (0, 6), (16, 6)), ("ww", (0, 0), (0, 6)), ("we", (16, 0), (16, 6)),
             ("wg", (6, 0), (6, 6)), ("wh", (9, 0), (9, 6))]
    rooms = [("garage", 0, 6), ("hall", 6, 9), ("living", 9, 16)]
    doors = [("e", "ws", (7.5, 0), main_width, "swing"), ("f", "ws", (12.5, 0), 1.8, "swing"),
             ("s", "wn", (12.5, 6), 3.0, None), ("g", "ws", (3.0, 0), 2.6, None),
             ("i", "wh", (9, 3.0), 1.6, "swing"), ("n", "wn", (7.5, 6), 0.9, "swing")]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "height": 3.0}],
            "rooms": [{"id": f"r_{t}", "level_id": "L0", "room_type": t,
                       "polygon": [[x0, 0], [x1, 0], [x1, 6], [x0, 6]]} for t, x0, x1 in rooms],
            "walls": [{"id": i, "level_id": "L0", "start": list(a), "end": list(e), "thickness": 0.25}
                      for i, a, e in walls],
            "openings": [{"id": i, "type": "door", "level_id": "L0", "wall_id": w, "center": list(c), "width": wd,
                          "height": 2.1, "sill_height": None, "operation": op} for i, w, c, wd, op in doors],
            "site": {"entrances": [{"door_id": "e", "level_id": "L0", "main": True}]}}


def _decide(b: dict) -> tuple[dict, list]:
    """D5 on a building, its defaults carried out as ``build.prepare`` does; the review after them."""
    q = RR.door_types(AA.Plan(b), AR.opening_sides(b))[0]
    defaults = AR.defaults_of({"questions": [q]}, {})
    applied = AA.apply_answers(b, defaults)
    after = RR.door_types(AA.Plan(b), AR.opening_sides(b))[0]
    return q, applied, after


def test_the_rule_on_a_house_entrance_french_sliding_garage_and_inside_pair():
    b = _house()
    q, applied, after = _decide(b)
    kinds = {o["id"]: o.get("door_type") for o in b["openings"]}
    assert kinds == {"e": "entrance", "f": "french", "s": "glazed_sliding", "g": "garage_sectional", "i": "double",
                     "n": None}
    assert all(r["ok"] for r in applied) and {r["key"] for r in applied} == {f"D5:{k}" for k in "efsgi"}
    assert not any(a.get("open") for a in after["answers"]) and len(after["answers"]) == 6
    f = next(o for o in b["openings"] if o["id"] == "f")
    assert f["operation"] == "double" and f["drawn_operation"] == "swing" and f["operation_source"] == "architect"
    assert f["adjusted_by_ai"]["by"] == "architect" and f["evidence"][-1]["rule"] == "architect D5:f"
    s = next(o for o in b["openings"] if o["id"] == "s")
    assert s["leaves"] == 3 and s["operation"] == "sliding" and s["drawn_operation"] is None
    e = next(o for o in b["openings"] if o["id"] == "e")
    assert e["door_style"] == "entrance" and e["operation"] == "swing" and "drawn_operation" not in e
    # every open point offered the other kinds and keep; the default is the first option
    for a in q["answers"]:
        if a.get("open"):
            assert a["default"] == a["options"][0]["choice"] and a["options"][-1]["id"] == "keep"
    # the library plan: the entrance a front door, the glazed doors glazed, the garage and the pair parametric
    outer = [{"opening": o, "bottom": 0.0, "top": 2.1, "outward": [0, -1]} for o in b["openings"] if o["id"] != "i"]
    cats = OM.categorise(b, outer)
    assert cats == {"e": "entrance", "f": "glazed_door", "s": "glazed_door", "n": "door"}


def test_the_looks_of_the_decided_doors():
    b = _house()
    _decide(b)
    by = {o["id"]: o for o in b["openings"]}
    f = looks.door_look(STYLE, by["f"])
    assert f["door_style"] == "double" and f["glazed"] and f["leaves"] == 2
    assert f["material"] == "aluminium_anthracite" and "windows' frame finish" in f["reason"]   # facade joinery
    g = looks.door_look(STYLE, by["g"])
    assert g["door_style"] == "sectional" and g["material"] == "aluminium_anthracite"
    i = looks.door_look(STYLE, by["i"])
    assert i["door_style"] == "double" and not i["glazed"] and i["material"] != "aluminium_anthracite"
    e = looks.door_look(STYLE, by["e"])
    assert e["door_style"] == "entrance" and e["sidelights"] and not e["glazed"]
    assert all(looks.door_geometry_m10({}, by[k]) for k in "efsgi") and not looks.door_geometry_m10({}, by["n"])
    # a gap the architect made a glazed door is glazed in its look before D5 decides it
    gap = {"id": "x", "type": "door", "operation": "swing", "glazed": True}
    assert looks.door_look(STYLE, gap)["door_style"] == "glazed" and looks.door_geometry_m10({}, gap)


# --------------------------------------------------------------------------
# The builder: glass, no leaf wider than about 1.2 m, closed by the stops
# --------------------------------------------------------------------------

FW = P.DOOR_FRAME_W


def _closed(parts, w, h):
    inner = w / 2.0 - FW
    return first_gap([p for p in parts if p["role"] in ("leaf", "panel", "glass", "stop", "astragal", "frame")],
                     -inner, inner, 0.01, h - FW) is None


@pytest.mark.parametrize("side", [1, -1])
def test_french_doors_are_two_glazed_leaves(side):
    w, h, t = 1.8, 2.1, 0.25
    parts, rec = P.door_parts({"door_style": "double", "glazed": True, "side": side}, w, h, t)
    assert sum(p["role"] == "glass" for p in parts) == 2 and rec["glazed"] and rec["leaves"] == 2
    units = leaf_units(parts)
    assert len(units) == 2 and max(units) <= P.LEAF_MAX_M
    assert sum(p["role"] == "astragal" for p in parts) == 1 and _closed(parts, w, h)
    assert all(abs(v[1]) <= t / 2.0 + 1e-9 for p in parts for v in p["verts"])


@pytest.mark.parametrize("w,n", [(1.6, 2), (2.15, 2), (2.95, 3), (3.6, 3), (4.4, 4)])
def test_a_glazed_sliding_door_is_glazed_panels_in_the_frame_one_fixed(w, n):
    h, t = 2.1, 0.25
    parts, rec = P.door_parts({"door_style": "glazed_sliding", "side": -1}, w, h, t)
    assert rec["leaves"] == n and rec["glazed"] and rec["tracks"] == 2 and rec["fixed_panels"][0] == 0
    assert sum(p["role"] == "glass" for p in parts) == n
    assert max(leaf_units(parts)) <= P.LEAF_MAX_M + P.SLIDING_PANEL_OVERLAP_M
    assert not rec["surface_mounted"] and "frame" in rec["parts"] and _closed(parts, w, h)
    xs = [v[0] for p in parts for v in p["verts"]]
    assert min(xs) >= -w / 2.0 - 1e-9 and max(xs) <= w / 2.0 + 1e-9                  # in the opening
    moving = len([i for i in range(n) if i not in rec["fixed_panels"]])
    assert sum(p["role"] == "handle" for p in parts) == 2 * moving                     # pulls on the moving panels


def test_a_glazed_sliding_door_in_a_thin_wall_puts_its_panels_side_by_side():
    w, h, t = 2.4, 2.1, 0.065
    parts, rec = P.door_parts({"door_style": "glazed_sliding", "side": 1}, w, h, t)
    assert rec["tracks"] == 1 and rec["leaves"] == 2 and sum(p["role"] == "astragal" for p in parts) == 1
    assert all(abs(v[1]) <= t / 2.0 + 1e-9 for p in parts if p["role"] != "handle" for v in p["verts"])
    assert _closed(parts, w, h)


def test_a_glazed_folding_door_and_a_pair_of_sliding_leaves():
    parts, rec = P.door_parts({"door_style": "folding", "glazed": True, "leaves": 4, "side": 1}, 3.0, 2.1, 0.25)
    assert rec["leaves"] == 4 and sum(p["role"] == "glass" for p in parts) == 4
    assert max(leaf_units(parts)) <= AA.FOLDING_LEAF_M and _closed(parts, 3.0, 2.1)
    parts, rec = P.door_parts({"door_style": "sliding", "leaves": 2, "side": 1}, 1.95, 2.1, 0.12)
    assert rec["surface_mounted"] and rec["leaves"] == 2 and len(leaf_units(parts)) == 2
    assert sum(p["role"] == "handle" for p in parts) == 2 and not rec.get("glazed")


def test_a_sectional_garage_door_has_horizontal_sections():
    w, h, t = 2.6, 2.2, 0.25
    parts, rec = P.door_parts({"door_style": "sectional", "side": -1}, w, h, t)
    leaves = [p for p in parts if p["role"] == "leaf"]
    assert rec["sections"] == len(leaves) >= 3 and not rec.get("glazed")
    heights = sorted({round(max(v[2] for v in p["verts"]) - min(v[2] for v in p["verts"]), 6) for p in leaves})
    assert len(heights) == 1 and heights[0] <= 0.8                                     # equal sections
    assert sum(p["role"] == "rib" for p in parts) == 2 * (2 * rec["sections"] - 1) and _closed(parts, w, h)


@pytest.mark.parametrize("w,lights", [(1.4, 1), (1.8, 1), (2.2, 2), (2.95, 2), (1.2, 0)])
def test_a_wide_entrance_gets_side_lights_beside_one_leaf(w, lights):
    h, t = 2.1, 0.25
    parts, rec = P.door_parts({"door_style": "entrance", "sidelights": True, "side": -1}, w, h, t)
    assert rec.get("sidelights", 0) == lights and sum(p["role"] == "glass" for p in parts) == lights
    leaf = [p for p in parts if p["role"] == "leaf"]
    assert len(leaf) == 1
    xs = [v[0] for v in leaf[0]["verts"]]
    assert max(xs) - min(xs) <= P.SINGLE_LEAF_MAX_M + 1e-9 and _closed(parts, w, h)
    assert rec["leaf_thickness"] == P.ENTRANCE_LEAF_T and sum(p["role"] == "stop" for p in parts) == 3


def test_real06_living_room_door_as_built(prep):
    o = _opening(prep["building"], "d_L0_006")
    look = looks.door_look(STYLE, o)
    assert look["door_style"] == "glazed_sliding" and look["leaves"] == 3
    parts, rec = P.door_parts(dict(look, side=1), float(o["width"]), 2.1, 0.25)
    assert sum(p["role"] == "glass" for p in parts) == 3 and max(leaf_units(parts)) < 1.2
    assert rec["door_style"] == "glazed_sliding" and _closed(parts, float(o["width"]), 2.1)


# --------------------------------------------------------------------------
# A door nobody decided builds exactly as before
# --------------------------------------------------------------------------

OLD_PARTS = {   # (parts, roles) of each style before D5, 0.9 x 2.1 m in a 0.12 m wall
    "flush": (11, {"frame": 3, "handle": 4, "leaf": 1, "stop": 3}),
    "shaker_panel": (21, {"frame": 3, "handle": 4, "leaf": 1, "panel": 10, "stop": 3}),
    "glazed": (15, {"frame": 3, "glass": 1, "handle": 4, "leaf": 4, "stop": 3}),
    "pocket": (12, {"frame": 3, "handle": 2, "leaf": 1, "stop": 6}),
    "sliding": (3, {"handle": 1, "leaf": 1, "rail": 1}),
    "barn": (10, {"handle": 1, "leaf": 6, "ledge": 2, "rail": 1}),
    "double": (17, {"astragal": 1, "frame": 3, "handle": 8, "leaf": 2, "stop": 3}),
    "entrance": (15, {"frame": 3, "groove": 6, "handle": 2, "leaf": 1, "stop": 3}),
    "folding": (13, {"astragal": 1, "frame": 3, "handle": 4, "leaf": 2, "stop": 3}),
}
OLD_RECORD = {"door_style", "frame_width", "handles", "leaf_thickness", "parts", "side", "stop_side",
              "surface_mounted"}


@pytest.mark.parametrize("style", sorted(OLD_PARTS))
def test_a_door_without_a_decision_builds_as_before(style):
    parts, rec = P.door_parts({"door_style": style, "side": -1}, 0.9, 2.1, 0.12)
    roles: dict = {}
    for p in parts:
        roles[p["role"]] = roles.get(p["role"], 0) + 1
    assert (len(parts), roles) == OLD_PARTS[style] and set(rec) == OLD_RECORD
    # a 2.95 m sliding door nobody decided is still one leaf (only a decision splits it)
    wide, _ = P.door_parts({"door_style": "sliding", "side": -1}, 2.95, 2.1, 0.25)
    assert len(leaf_units(wide)) == 1
    plain = looks.door_look(STYLE, {"id": "d", "type": "door", "operation": "swing"})
    assert not {"glazed", "leaves", "sidelights", "door_type"} & set(plain)
    assert plain["material"] != "aluminium_anthracite"
    assert not looks.door_geometry_m10({}, {"id": "d", "operation": "swing"})


def test_categories_of_doors_nobody_decided_are_as_before():
    b = {"site": {"entrances": [{"door_id": "m", "main": True}]}}
    outer = [{"opening": {"id": i, "type": "door", "width": w}, "bottom": 0.0, "top": 2.1, "outward": [0, -1]}
             for i, w in (("m", 2.95), ("a", 1.6), ("c", 0.9))]
    assert OM.categorise(b, outer) == {"m": "entrance", "a": "glazed_door", "c": "door"}
