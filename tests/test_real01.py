"""real01 acceptance (docs/milestone7.md §2.10, §11 G3): the whole pipeline on ``projects/real01/real01.pdf``.

The reference is ``tests/fixtures/real01_reference.yaml`` (feet, origin = min corner of the house walls, X right,
Y up, per-element tolerances); the building is in metres with the same origin (``transform_to_building`` puts the
min corner of the building walls at 0, 0), so a point compares after dividing by 0.3048. The pipeline runs once per
module with ``--no-ai`` (CPU, about 15 s):

- status ``ok``, the scale within 0.2 % (two dimensions corroborated by the 8 room-size labels), imperial units, the
  level assumed (``L0`` "Ground floor", no title on the page);
- every labelled room with its label, type, size check and position; the hall (one face or two spaces);
- doors and windows: recall and precision 1.0 at the reference tolerances (centre, width; doors also hinge, swing
  radius and the room they swing into); doorless openings O1, O3, O5 and the separator O2;
- walls: the outline (L-shape with the parking notch), thickness classes 6" / 9", every reference wall covered;
- furniture: every reference footprint (20 pieces), rule types (stair with its flights, the two counter legs),
  AI candidates ``unknown`` / ``unverified`` until answered;
- the plot wall, Parking, 9 plants and the entrance step in ``site``; nothing of the site in the building;
- with fake agreeing answers the AI types are applied; with disagreeing answers the pieces stay
  ``unknown`` / ``unverified`` with both candidates and a ``symbol_type_disagreement`` conflict each.
"""
import functools
import math

import pytest
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

import _real01_page as RP
from wenart import building as B
from wenart.ingest import cad_pdf
from wenart.ingest import pipeline as P
from wenart.ingest.generic import core

from conftest import PROJECTS

FT = 0.3048
REF = RP.reference()
TOL = REF["tolerances_default"]


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    out = tmp_path_factory.mktemp("real01")
    building, build = P.run_project(PROJECTS / "real01", out, no_ai=True)
    return {"building": building, "build": build, "out": out, "work": build.generic[0]}


def ft(p) -> tuple[float, float]:
    return (p[0] / FT, p[1] / FT)


def bbox_ft(points) -> list[float]:
    xs = [p[0] / FT for p in points]
    ys = [p[1] / FT for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def close(a, b, tol) -> bool:
    return math.dist(a, b) <= tol


def edges_within(box, ref_box, tol) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(box, ref_box))


# --------------------------------------------------------------------------
# Status, scale, level, units
# --------------------------------------------------------------------------

def test_status_scale_units_and_assumed_level(run):
    b = run["building"]
    assert b["status"] == "ok", b["warnings"]
    B.validate(b)
    page = b["documents"][0]["pages"][0]
    assert (page["class"], page["classifier"], page["confidence"]) == ("floor_plan", "generic_labels", 0.6)
    scale = page["scale"]
    ref_m_per_pt = FT / REF["scale"]["pt_per_ft"]
    assert abs(scale["metres_per_unit"] - ref_m_per_pt) / ref_m_per_pt <= REF["scale"]["tol"]["rel"]
    assert scale["method"] == "dimension_text" and scale["confidence"] == 0.85
    assert b["project"]["unit_system"] == "imperial" and b["documents"][0]["unit_system"] == "imperial"
    assert b["documents"][0]["source_kind"] == "cad_pdf"
    level = b["levels"][0]
    assert (level["id"], level["label"], level["label_source"]) == ("L0", "Ground floor", "assumed")
    assert "level title missing: assumed L0 Ground floor" in b["warnings"]
    assert any(e.get("text") == "Bed Room" for e in level["evidence"])          # the room labels are the evidence
    # The page origin is the min corner of the house walls (the reference frame).
    t = page["transform_to_building"]
    assert t[0] == t[4] == scale["metres_per_unit"] and t[1] == t[3] == 0.0


def test_dimensions_are_checked_without_conflicts(run):
    b = run["building"]
    assert b["conflicts"] == []
    rows = run["work"].extraction.report["dimensions"]
    assert sorted(r["text"] for r in rows) == ["30'", "50'"]
    for r in rows:
        assert abs(r["off_pct"]) < 0.02 and r["end_marks"] == ["arrow", "arrow"]


# --------------------------------------------------------------------------
# Rooms
# --------------------------------------------------------------------------

def _room_for(rooms, ref_room):
    centre = ref_room["centre_ft"]
    for r in rooms:
        if Polygon([ft(p) for p in r["polygon"]]).contains(Polygon([(centre[0] - 0.01, centre[1] - 0.01),
                                                                    (centre[0] + 0.01, centre[1] - 0.01),
                                                                    (centre[0], centre[1] + 0.01)])):
            return r
    return None


def test_every_labelled_room_has_its_label_type_size_and_position(run):
    b = run["building"]
    rooms = b["rooms"]
    labelled = [r for r in rooms if r["label_raw"] is not None]
    assert len(labelled) == REF["counts"]["rooms_labelled"]
    anchors = {}
    for text in run["work"].extraction.labels:
        anchors.setdefault(text.element_id, []).append(ft(P._to_building(run["work"].extraction, text.start)))
    for ref_room in REF["rooms"]:
        r = _room_for(rooms, ref_room)
        assert r is not None, ref_room["id"]
        tol = ref_room["tol"]
        assert r["label"] == ref_room["label"] and r["room_type"] in ref_room["type_accept"], (r, ref_room["id"])
        assert r["status"] == "verified" and r["label_size"]["status"] == ref_room["label_size_check"]
        assert r["label_size"]["text"] == ref_room["label_size_text"]
        box = bbox_ft(r["polygon"])
        if ref_room["id"] in ("drawing", "dining"):
            # The O2 separator (y 15.006) bounds part of these faces instead of the wall at 14.755 / 15.257.
            assert edges_within(box, ref_room["bbox_ft"], 0.30)
        else:
            assert edges_within(box, ref_room["bbox_ft"], tol["edge"]), (ref_room["id"], box)
        area_sqft = r["area_computed"] / FT / FT
        assert abs(area_sqft - ref_room["area_sqft"]) <= tol["area_rel"] * ref_room["area_sqft"], ref_room["id"]
        assert any(close(a, ref_room["label_name_anchor_ft"], tol["label_anchor"]) for a in anchors[r["id"]])
    # Parking is a site area, not a room.
    assert not any("parking" in r["label"].lower() for r in rooms)


def test_the_hall_is_one_unlabelled_face_holding_the_stair(run):
    rooms = run["building"]["rooms"]
    unlabelled = [r for r in rooms if r["label_raw"] is None]
    assert len(unlabelled) in REF["counts"]["rooms_unlabelled_hall"]
    merged = REF["circulation"]["merged_face"]
    if len(unlabelled) == 1:
        hall = unlabelled[0]
        assert edges_within(bbox_ft(hall["polygon"]), merged["bbox_ft"], merged["tol"]["edge"])
        ref_area = sum(s["area_sqft"] for s in REF["circulation"]["spaces"])
        assert abs(hall["area_computed"] / FT / FT - ref_area) <= merged["tol"]["area_rel"] * ref_area
    for hall in unlabelled:
        assert hall["room_type"] == "hall" and hall["label"] == "Room" and hall["status"] == "unverified"
    stair = next(f for f in run["building"]["furniture"] if f["type"] == "stair")
    assert stair["room_id"] in {h["id"] for h in unlabelled}


# --------------------------------------------------------------------------
# Openings
# --------------------------------------------------------------------------

def _matches(items, refs, ok) -> tuple[float, float]:
    """(recall, precision) of a one-to-one greedy matching."""
    taken = set()
    hits = 0
    for ref in refs:
        for k, item in enumerate(items):
            if k not in taken and ok(item, ref):
                taken.add(k)
                hits += 1
                break
    return hits / max(len(refs), 1), hits / max(len(items), 1)


def _gap_entry(run, opening):
    """The gap log entry of a building opening (page metres -> building metres by the origin)."""
    ex = run["work"].extraction
    ox, oy = ex.report["origin_m"]
    for e in ex.report["gaps"]:
        if e.get("class") != opening["type"] or "p0" not in e:
            continue
        mid = ((e["p0"][0] + e["p1"][0]) / 2 - ox, (e["p0"][1] + e["p1"][1]) / 2 - oy)
        if math.dist(mid, opening["center"]) <= 0.02:
            return e, (ox, oy)
    return None, (ox, oy)


def test_doors_and_windows_recall_and_precision(run):
    b = run["building"]
    rooms = b["rooms"]
    room_of_ref = {r["id"]: _room_for(rooms, r) for r in REF["rooms"]}
    doors = [o for o in b["openings"] if o["type"] == "door"]
    windows = [o for o in b["openings"] if o["type"] == "window"]
    assert len(doors) == REF["counts"]["doors"] and len(windows) == REF["counts"]["windows"]

    def door_ok(o, ref):
        tol = ref["tol"]
        if not (close(ft(o["center"]), ref["centre_ft"], tol["centre"]) and
                abs(o["width"] / FT - ref["width_ft"]) <= tol["width"]):
            return False
        entry, (ox, oy) = _gap_entry(run, o)
        assert entry is not None, o["id"]
        hinge = ft((entry["hinges"][0][0] - ox, entry["hinges"][0][1] - oy))
        into = room_of_ref.get(ref["swings_into"])
        return (close(hinge, ref["hinge_ft"], tol["hinge"]) and
                abs(entry["radius"] / FT - ref["swing_radius_ft"]) <= tol["swing_radius"] and
                entry["leaf"] and into is not None and o["swing_side"] == into["id"])

    def window_ok(o, ref):
        tol = ref["tol"]
        return close(ft(o["center"]), ref["centre_ft"], tol["centre"]) and abs(o["width"] / FT - ref["width_ft"]) <= \
            tol["width"]

    assert _matches(doors, REF["doors"], door_ok) == (1.0, 1.0)
    assert _matches(windows, REF["windows"], window_ok) == (1.0, 1.0)
    for o in doors:
        assert o["status"] == "verified" and o["assumed"] == ["height"] and o["height"] == 2.1
        assert o["evidence"][0]["confidence"] == 0.95            # arc and leaf
    for o in windows:
        assert o["assumed"] == ["height", "sill_height"] and (o["height"], o["sill_height"]) == (1.2, 0.9)


def test_doorless_openings_and_the_separator(run):
    openings = [o for o in run["building"]["openings"] if o["type"] == "opening"]
    walls = {w["id"] for w in run["building"]["walls"]}
    found = {}
    for ref in REF["openings"]:
        hits = [o for o in openings if close(ft(o["center"]), ref["centre_ft"], ref["tol"]["centre"])
                and abs(o["width"] / FT - ref["width_ft"]) <= ref["tol"]["width"]]
        if ref.get("optional"):
            continue
        assert len(hits) == 1, ref["id"]
        found[ref["id"]] = hits[0]
    for key in ("O1", "O3", "O5"):
        o = found[key]
        assert not o.get("virtual") and o["wall_id"] in walls and o["status"] == "verified"
        assert o["assumed"] == ["height"]
    sep = found["O2"]
    assert sep["virtual"] is True and sep["wall_id"] is None and sep["line"] is not None
    ys = [p[1] / FT for p in sep["line"]]
    xs = sorted(p[0] / FT for p in sep["line"])
    assert all(abs(y - 15.006) <= 0.10 for y in ys) and abs(xs[0] - 26.528) <= 0.10 and abs(xs[1] - 30.755) <= 0.10
    assert sep["evidence"][0]["method"] == "derived"
    assert len(openings) == len(found)                            # O4 absent: the hall is one face
    log = run["work"].extraction.report["separators"]
    assert [e["kept"] for e in log] == [True] and log[0]["reason"] == "two room names shared one face"


def test_the_rooms_split_by_the_separator_share_its_line_exactly(run):
    """Review dwgblender-1: the separator splits the drawing room and the dining as a 4 mm strip; the pipeline
    passes the separators to derive_rooms, so both faces are snapped back onto the separator line (no slit between
    their floors and ceilings: Blender's rays went through it)."""
    sep = next(o for o in run["building"]["openings"] if o.get("virtual"))
    (x0, y0), (x1, y1) = sep["line"]
    assert abs(y0 - y1) <= 1e-9
    rooms = {r["label"]: r for r in run["building"]["rooms"]}
    for label in ("Drawing Room", "Dining"):
        poly = rooms[label]["polygon"]
        on = [p for p in poly if abs(p[1] - y0) <= 0.01]
        assert all(abs(p[1] - y0) <= 1e-6 for p in on), (label, on)
        xs = sorted(p[0] for p in on)
        assert xs[0] <= min(x0, x1) + 1e-6 and xs[-1] >= max(x0, x1) - 1e-6, (label, on)


# --------------------------------------------------------------------------
# Walls
# --------------------------------------------------------------------------

def _wall_polys(walls):
    from wenart.ingest.generic import topology as TP
    return [TP.wall_polygon({"start": ft(w["start"]), "end": ft(w["end"]), "thickness": w["thickness"] / FT})
            for w in walls]


def test_walls_outline_thickness_classes_and_coverage(run):
    b = run["building"]
    polys = _wall_polys(b["walls"])
    union = unary_union(polys)
    # Outline: the L-shape with the parking notch.
    main = union if union.geom_type == "Polygon" else max(union.geoms, key=lambda g: g.area)
    outline = Polygon(main.exterior)
    ref_outline = Polygon(REF["building_outline"]["polygon_ft"])
    tol = REF["building_outline"]["tol"]
    assert abs(outline.area - ref_outline.area) <= tol["area_rel"] * ref_outline.area
    for vertex in ref_outline.exterior.coords[:-1]:
        assert min(math.dist(vertex, v) for v in outline.exterior.coords) <= tol["vertex"], vertex
    # Thickness classes 9" and 6" (plot walls are not here).
    classes = REF["wall_thickness_classes"]
    for w in b["walls"]:
        t = w["thickness"] / FT
        assert any(abs(t - c["thickness_ft"]) <= c["tol"]["thickness"] for c in classes[:2]), (w["id"], t)
    # Every reference wall rectangle is covered by the building walls; nothing lies outside the house.
    for group in ("exterior_9in", "interior_9in", "interior_6in"):
        for ref in REF["walls"][group]:
            rect = sbox(*ref["rect"])
            assert rect.intersection(union).area >= 0.9 * rect.area, ref["id"]
    house = sbox(*REF["building_outline"]["bbox_ft"]).buffer(0.15)
    assert union.difference(house).area < 0.05
    assert sum(1 for w in b["walls"] if w["exterior"]) >= 6


# --------------------------------------------------------------------------
# Furniture
# --------------------------------------------------------------------------

def _piece_ok(f, ref) -> bool:
    tol = ref["tol"]
    fp = f["footprint"]
    if not close(ft(fp["center"]), ref["centre_ft"], tol["centre"]):
        return False
    mine = sorted(v / FT for v in fp["size"])
    theirs = sorted(ref["size_wd_ft"])
    return all(abs(a - b) <= tol["size"] for a, b in zip(mine, theirs))


def test_every_reference_footprint_is_found(run):
    furniture = run["building"]["furniture"]
    refs = [r for r in REF["furniture"] if not r.get("not_a_piece")]
    assert len(furniture) == REF["counts"]["furniture_total"] == len(refs)
    assert _matches(furniture, refs, _piece_ok) == (1.0, 1.0)
    for f in furniture:
        assert f["source"] == "from_documents" and f["room_id"] is not None
    # Milestone 12 (docs/milestone12.md §4.1 D7, never a box): without the AI answers (--no-ai) a piece no rule,
    # context or size inference types is not built and is listed for review; every typed piece is built.
    untyped = sorted(f["id"] for f in furniture if f["type"] == "unknown")
    assert all(f["build"] is (f["type"] != "unknown") for f in furniture)
    assert sorted(n["id"] for n in run["building"]["needs_review"]) == untyped


def test_rule_types_stair_and_counter_legs(run):
    b = run["building"]
    walls = {w["id"]: w for w in b["walls"]}
    stair_ref = next(r for r in REF["furniture"] if r["id"] == "F19")
    stairs = [f for f in b["furniture"] if f["type"] == "stair"]
    assert len(stairs) == 1
    stair = stairs[0]
    assert (stair["type_method"], stair["status"]) == ("rule", "verified") and _piece_ok(stair, stair_ref)
    flights = stair["stair"]["flights"]
    assert len(flights) == len(stair_ref["flights"])
    for flight in flights:
        assert abs(flight["lines"] - 8) <= stair_ref["tol"]["treads_per_flight"]
        assert abs(flight["width"] / FT - 2.5) <= 0.1
        assert abs(flight["spacing"] / FT - stair_ref["tread_depth_ft"]) <= stair_ref["tol"]["tread_depth"]
    assert stair["stair"]["direction_assumed"] and stair["stair"]["turn_assumed"] and stair["stair"]["void_assumed"]
    kitchen = _room_for(b["rooms"], next(r for r in REF["rooms"] if r["id"] == "kitchen"))
    counters = [f for f in b["furniture"] if f["type"] == "kitchen_counter"]
    assert len(counters) == 2
    for ref_id in ("F18a", "F18b"):
        ref = next(r for r in REF["furniture"] if r["id"] == ref_id)
        hits = [f for f in counters if _piece_ok(f, ref)]
        assert len(hits) == 1, ref_id
        f = hits[0]
        assert (f["type_method"], f["status"], f["room_id"]) == ("rule", "verified", kitchen["id"])
        assert f["front_deg"] is not None and abs((f["front_deg"] - ref["front_deg"] + 180) % 360 - 180) <= 10
        run_info = f["counter_run"]
        assert run_info["wall_id"] in walls and run_info["strokes"]
    # Nothing else is read as a type without AI answers (--no-ai). Since Milestone 11 the ingest may infer a
    # type from size, room and neighbours (wenart/furniture/infer.py): such a piece stays unverified with
    # type_method none and carries inferred: true with its reason, so it is listed in the report.
    others = [f for f in b["furniture"] if f["type"] not in ("stair", "kitchen_counter")]
    assert others and all((f["status"], f["type_method"]) == ("unverified", "none") for f in others)
    assert all(f["type"] == "unknown" or (f.get("inferred") and f.get("inferred_reason")) for f in others)
    assert any(f["type"] == "unknown" for f in others)


# --------------------------------------------------------------------------
# Site
# --------------------------------------------------------------------------

def test_plot_parking_plants_and_step_are_in_site_only(run):
    b = run["building"]
    site = b["site"]
    plot = REF["site"]["plot_wall"]
    assert [w["kind"] for w in site["boundary_walls"]] == ["plot"] * 4
    tol = plot["tol"]["edge"]
    for seg in plot["segments"]:
        rect = sbox(*seg["rect"])
        hits = [w for w in site["boundary_walls"]
                if _wall_polys([w])[0].symmetric_difference(rect).area <= tol * (rect.length / 2 + 1.0)]
        assert len(hits) == 1, seg["side"]
    parking = [a for a in site["areas"] if a["label"] == "Parking"]
    assert len(parking) == 1 and parking[0]["polygon"] is None
    area_ref = REF["site"]["areas"][0]
    extent = [v / FT for v in parking[0]["extent_m"]]
    lo, hi = area_ref["tol"]["edge_east_accept_x"]
    assert lo - area_ref["extent_bbox_ft"][0] <= extent[0] <= hi - area_ref["extent_bbox_ft"][0]
    assert abs(extent[1] - area_ref["extent_size_xy_ft"][1]) <= area_ref["tol"]["edge"]
    assert parking[0]["label_size"]["status"] == "unchecked"
    assert parking[0]["id"] == "sa_L0_parking"
    decor = REF["site"]["decor"]
    plants = [d for d in site["decor"] if d["kind"] == "plant"]
    assert len(plants) == decor["plants"]["count"]
    for centre in decor["plants"]["centres_ft"]:
        assert sum(1 for d in plants if close(ft(d["center"]), centre, decor["plants"]["tol"]["centre"])) == 1
    step = decor["entrance_step"]
    others = [d for d in site["decor"] if d["kind"] == "other"]
    assert len(others) == REF["counts"]["site_other_decor"]
    assert close(ft(others[0]["center"]), step["centre_ft"], step["tol"]["centre"])
    size = sorted(v / FT for v in others[0]["size"])
    assert size == pytest.approx(sorted(step["size_xy_ft"]), abs=step["tol"]["size"])
    # Nothing of the site is in the building.
    house = sbox(*REF["building_outline"]["bbox_ft"]).buffer(0.2)
    for key in ("walls", "openings", "furniture"):
        for item in b[key]:
            point = item["center"] if "center" in item else item.get("footprint", {}).get("center") or item["start"]
            assert house.contains(sbox(*ft(point), *ft(point)).buffer(0.01)), item["id"]


# --------------------------------------------------------------------------
# Outputs: debug image, report, questions
# --------------------------------------------------------------------------

def test_debug_image_report_and_questions(run):
    out = run["out"]
    page = run["building"]["documents"][0]["pages"][0]
    assert page["debug_image"] == "debug/real01_pdf_p1.png" and (out / page["debug_image"]).is_file()
    import numpy as np
    from PIL import Image
    from wenart.ingest import debug_image as DI
    with Image.open(out / page["debug_image"]) as im:
        assert im.size == (1755, 1240)                            # the page at 150 dpi
        arr = np.asarray(im.convert("RGB")).astype(int)

    def pixels(colour, tol=12):
        return int(np.all(np.abs(arr - np.array(colour)) <= tol, axis=-1).sum())

    assert pixels(DI.SEPARATOR_COLOUR) > 50                       # the O2 separator, dashed magenta
    assert pixels(DI.DIMENSION_COLOUR) > 500                      # the two scale dimensions, orange
    assert pixels(DI.TYPE_METHOD_COLOURS["rule"]) > 200           # stair and counters, green
    assert pixels(DI.TYPE_METHOD_COLOURS["none"]) > 200           # unanswered candidates, red (striped)
    report = (out / "report.md").read_text(encoding="utf-8")
    for heading in ("## Units", "## Scale", "## Site", "## Separators", "## Room size labels", "## Gaps",
                    "## Furniture typing", "## Assumed values"):
        assert heading in report, heading
    assert "| r_L0_room | L0 | Room | — | hall |" in report
    assert "11' 0\" (3.35 m)" in report and "two room names shared one face" in report
    from wenart.recognition import answers as A
    doc = A.read_requests(out / "recognition")
    keys = [i["key"] for i in doc["items"]]
    assert len(keys) == 17 and keys == sorted(keys) and all(k.startswith("sym_L0_") for k in keys)
    for item in doc["items"]:
        assert all((out / "recognition" / p).is_file() for p in item["images"])
    unknown = [f for f in run["building"]["furniture"] if f["type_method"] == "none"]
    assert len(unknown) == len(keys)
    # --no-ai: nothing is pending, so the pipeline would not exit 4.
    assert run["build"].pending == [] and P.exit_code(run["building"], run["build"], no_ai=True) == 0
    # ... but the 17 questions are still unanswered, and report.md says so (review cross-5).
    assert run["build"].unanswered == keys
    assert ("Recognition questions: 17 (`recognition/requests.json`), 17 without a complete pair of answers "
            "(--no-ai: not applied, they stay unknown/unverified).") in report
    # The page's rule outcomes (LevelExtraction.notes) are in report.md, one block per page (review cross-2).
    notes = report.split("## Notes", 1)[1].split("\n## ", 1)[0]
    assert "### real01.pdf p1" in notes
    for note in run["work"].extraction.notes:
        assert f"- {note.removeprefix('real01.pdf p1: ')}\n" in notes, note
    assert "drawn details smaller than 0.2 m ignored" in notes and "17 of 17 furniture candidates" in notes


# --------------------------------------------------------------------------
# AI answers through core.extract (fake answers)
# --------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def _page():
    return cad_pdf.read_page(PROJECTS / "real01" / "real01.pdf", 1, "real01.pdf")


@functools.lru_cache(maxsize=1)
def _first():
    return core.extract(_page(), "L0", "real01.pdf")


def _ref_type(cand) -> str:
    """The reference type of a candidate (by footprint centre; page metres -> reference feet)."""
    ex = _first()
    ox, oy = ex.report["origin_m"]
    c = cand["footprint"]["center"]
    centre = ((c[0] - ox) / FT, (c[1] - oy) / FT)
    best = min(REF["furniture"], key=lambda r: math.dist(r.get("centre_ft", (1e9, 1e9)), centre))
    return best["type_accept"][0]


def _answer(ftype: str) -> dict:
    return {"type": ftype, "front": "none", "confidence": 0.8, "reason": "fake answer"}


def test_questions_are_pending_without_answers():
    ex = _first()
    keys = [q["key"] for q in ex.report["questions"]]
    assert len(keys) == 17 and ex.report["pending"] == keys
    assert all(c["request"]["input_sha256"] for c in ex.candidates)


def test_agreeing_answers_type_the_pieces():
    ex0 = _first()
    answers = {c["key"]: {"qwen": _answer(_ref_type(c)), "glm": _answer(_ref_type(c))} for c in ex0.candidates}
    ex = core.extract(_page(), "L0", "real01.pdf", answers=answers)
    assert ex.report["pending"] == []
    typed = [f for f in ex.furniture if f.type_method == "ai_two_pass"]
    assert len(typed) == 17
    for f in typed:
        assert f.status == "verified" and len(f.type_candidates) == 2 and len(f.extra_evidence) == 2
        assert {e["method"] for e in f.extra_evidence} == {"ai"} and {e["pass"] for e in f.extra_evidence} == {1, 2}
    counts = {}
    for f in typed:
        counts[f.type] = counts.get(f.type, 0) + 1
    for ftype in ("bed_double", "nightstand", "table_dining", "chair", "sofa", "table_coffee"):
        assert counts.get(ftype) == REF["counts"]["furniture_by_type"][ftype], ftype


def test_disagreeing_answers_keep_unknown_with_both_candidates():
    ex0 = _first()
    answers = {c["key"]: {"qwen": _answer("chair"), "glm": _answer("side_table")} for c in ex0.candidates}
    ex = core.extract(_page(), "L0", "real01.pdf", answers=answers)
    asked = [f for f in ex.furniture if f.type_method not in ("rule",)]
    assert len(asked) == 17
    for f in asked:
        assert (f.type, f.status, f.type_method) == ("unknown", "unverified", "none")
        assert [c["type"] for c in f.type_candidates] == ["chair", "side_table"]
        assert f.details["ai_conflict"]["kind"] == "symbol_type_disagreement"


def test_exit_code_rule():
    class Build:
        pending = ["sym_L0_001"]
    assert P.exit_code({"status": "ok"}, Build()) == P.EXIT_QUESTIONS == 4
    assert P.exit_code({"status": "ok"}, Build(), no_ai=True) == 0
    assert P.exit_code({"status": "needs_review"}, Build()) == 1           # a review stops before any AI
    Build.pending = []
    assert P.exit_code({"status": "ok"}, Build()) == 0
