"""real02's plans: walls drawn as face lines, and what the generic core reads on them (docs/milestone10.md §0.4, §3.1
item 11, §5 row 1; track A3).

``projects/real02/one_building.dwg`` is converted with LibreDWG (``wenart.ingest.dwg.convert``, once per session, about
a minute; skipped when LibreDWG is not built here) and read into one ``GenericPage`` (``dxf_generic.read_page``). The
four plan regions are cut out of it the way track A1's sheet split will hand them to the core: every top-level entity
whose strokes lie inside the region box (texts by their insertion point), with the units forced to centimetres (the
header says mm; A1's unit check corrects it). Each region then runs through ``core.extract`` (``--no-ai``; the corner
sofas also with fake agreeing answers).

What is read per region (the targets of the track):

| Region | Read | Not read (listed) |
|---|---|---|
| ground floor | closed walls of both dwellings (party wall 0.40 m), 12 labelled rooms in 12 faces, 12 doors, 4 glazed openings (windows), 2 stairs (2 flights each), 4 WCs, 4 washbasins, 4 wardrobes, 2 double beds (block YATAK split from its nightstands) | single beds, desks, nightstands stay AI candidates; the E. Yatak wardrobes are read by the counter rule (unverified, not in a kitchen) |
| basement | closed walls, Banyo, Mutfak, Koridor (with the stair, an end-to-face separator) and Salon faces, 4 doors, windows, 2 stairs, the two drawn L-shaped corner sofas (``sofa_corner``, ``shape: L``, chaise sides mirrored) | the kitchen run (one cluster > 4.5 m), the dining tables are 3.35 x 1.57 m with their chairs (block ``masa``, unverified) |
| basement "Açık mutfak" | closed walls, Banyo, Oda, Koridor faces, 4 doors, 2 stairs | Açık Mutfak and Salon share one face: no wall or wall end is drawn between them |
| attic | closed walls, Teras, Banyo, Koridor, Oyun Aktivite faces, 6 doors, windows, 2 stairs | the roof break line clusters (> 4.5 m) |
"""
from __future__ import annotations

import math
from collections import Counter

import pytest
from shapely.geometry import Point

from wenart.ingest import dwg
from wenart.ingest import dxf_generic as DG
from wenart.ingest.generic import core
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import GenericPage
from wenart.recognition import symbols as RS

from conftest import PROJECTS

DWG = PROJECTS / "real02" / "one_building.dwg"
HAS_LIBREDWG = dwg.find_tool("dwg2dxf") is not None
CM = 0.01
# Region boxes in drawing units (docs/milestone10.md §0.1; the lead's split prototype).
REGIONS = {
    "ground": (723100, 4489650, 724850, 4491200),
    "basement": (725300, 4491300, 726950, 4492750),
    "basement_alt": (725300, 4489650, 726950, 4491200),
    "attic": (724000, 4487700, 725800, 4489200),
}
pytestmark = pytest.mark.skipif(not HAS_LIBREDWG, reason="LibreDWG 0.14 not built here (scripts/cloud-setup.sh)")


def _entity(stroke_id: str) -> str:
    """The top-level entity of a stroke id: ``INSERT:4B/3`` -> ``INSERT:4B``, ``LWPOLYLINE:2F:1`` -> ``LWPOLYLINE:2F``,
    ``HATCH:5C#0`` -> ``HATCH:5C``, ``INSERT:4B[2]/3`` -> ``INSERT:4B``."""
    head = stroke_id.split("/")[0].split("#")[0].split("[")[0]
    return ":".join(head.split(":")[:2])


def region_page(page: GenericPage, box, units_to_m: float = CM) -> GenericPage:
    """The strokes of every top-level entity that lies inside ``box`` and the texts whose insertion point does, with
    the units forced (``units_to_m``)."""
    x0, y0, x1, y1 = box
    extent: dict[str, list[float]] = {}
    for st in page.strokes:
        b = st.bbox()
        e = extent.setdefault(_entity(st.id), [math.inf, math.inf, -math.inf, -math.inf])
        e[0], e[1], e[2], e[3] = min(e[0], b[0]), min(e[1], b[1]), max(e[2], b[2]), max(e[3], b[3])
    keep = {k for k, e in extent.items() if e[0] >= x0 and e[1] >= y0 and e[2] <= x1 and e[3] <= y1}
    strokes = [st for st in page.strokes if _entity(st.id) in keep]
    texts = [t for t in page.texts if x0 <= t.box[0] <= x1 and y0 <= t.box[1] <= y1]
    return GenericPage(file=page.file, page=1, source_kind="dxf", units="dxf", units_to_m=units_to_m,
                       size=(x1 - x0, y1 - y0), strokes=strokes, texts=texts, dimensions=[],
                       wall_hint_layers=page.wall_hint_layers)


@pytest.fixture(scope="module")
def pages(tmp_path_factory):
    conv = dwg.convert(DWG, tmp_path_factory.mktemp("real02"))
    whole = DG.read_page(conv.dxf_path, "one_building.dwg")
    return {name: region_page(whole, box) for name, box in REGIONS.items()}


@pytest.fixture(scope="module")
def extractions(pages):
    return {name: core.extract(page, "L0", "one_building.dwg", no_ai=True) for name, page in pages.items()}


def _label_faces(ex) -> dict[str, list[int]]:
    """Room label -> the faces (indices) its anchor lies in, for every label of the extraction."""
    s, _, ox, _, _, oy = ex.transform_to_building
    faces = TP.faces(ex.walls, ex.openings, ex.separators)
    out: dict[str, list[int]] = {}
    for lb in ex.labels:
        p = Point(lb.start[0] * s + ox, lb.start[1] * s + oy)
        out.setdefault(lb.text, []).extend(k for k, f in enumerate(faces) if f.contains(p))
    return out


def _types(ex) -> Counter:
    return Counter((f.type, f.type_method) for f in ex.furniture)


# --------------------------------------------------------------------------
# The walls of every plan
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(REGIONS))
def test_every_plan_reads_closed_walls_on_the_face_line_layer(extractions, name):
    ex = extractions[name]
    assert ex.review == [], ex.review
    assert TP.outer_loop_problem(ex.walls, ex.openings) is None          # both dwellings: one building
    assert all(w.evidence["layer"] == "DBM_w_sld" and w.evidence["confidence"] == 0.8 and
               w.evidence["method"] in ("vector", "derived") for w in ex.walls)
    note = ex.walls[0].evidence["note"]
    assert note.startswith("walls drawn as face lines: layer 'DBM_w_sld' chosen by evidence") and "runner-up" in note
    assert "columns join the walls" in note
    assert any(note in w for w in ex.warnings)                            # the choice is listed for the report
    thick = {round(w.thickness, 2) for w in ex.walls}
    assert {0.1, 0.2, 0.4} <= thick                                        # inner, outer, the party wall


def test_floor_tiles_and_furniture_never_feed_walls(extractions):
    for ex in extractions.values():
        info = ex.report["wall_info"]
        layers = {p.get("layer") for p in info["primitives"]}
        assert layers == {"DBM_w_sld"}, layers
        assert not any("Seramik" in (w.evidence.get("entity") or "") for w in ex.walls)


@pytest.mark.parametrize("name, rooms", [
    ("ground", {"YATAK ODASI": 4, "BANYO": 2, "KORİDOR": 2, "E.BANYO": 2, "E.YATAK ODASI": 2}),
    ("basement", {"SALON": 2, "MUTFAK": 2, "KORİDOR": 2, "BANYO": 2}),
    ("basement_alt", {"ODA": 2, "KORİDOR": 2, "BANYO": 2}),
    ("attic", {"TERAS": 2, "BANYO": 2, "KORİDOR": 2, "OYUN AKTİVİTE VE DİNLENME ODASI": 2}),
])
def test_labelled_rooms_have_their_own_faces(extractions, name, rooms):
    found = _label_faces(extractions[name])
    for label, count in rooms.items():
        hits = found.get(label, [])
        assert len(hits) == count and len(set(hits)) == count, (label, hits)
    used = [k for label in rooms for k in found[label]]
    assert len(used) == len(set(used))                                     # no two labels in one face


def test_open_kitchen_shares_the_salon_face(extractions):
    """'Açık mutfak': no wall and no wall end is drawn between the open kitchen and the salon, so they are one face
    with two labels (the room step lists it)."""
    found = _label_faces(extractions["basement_alt"])
    assert sorted(found["AÇIK MUTFAK"]) == sorted(found["SALON"]) and len(set(found["SALON"])) == 2


def test_basement_corridor_is_separated_from_the_salon(extractions):
    ex = extractions["basement"]
    kept = [e for e in ex.report["separators"] if e["kept"]]
    assert [e["kind"] for e in kept] == ["end_to_face", "end_to_face"]
    assert all(e["reason"] == "two room names shared one face" for e in kept)


# --------------------------------------------------------------------------
# Openings
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, doors, windows", [("ground", 12, 4), ("basement", 4, 4), ("basement_alt", 4, 2),
                                                  ("attic", 6, 2)])
def test_doors_and_windows(extractions, name, doors, windows):
    kinds = Counter(o.kind for o in extractions[name].openings)
    assert kinds["door"] == doors and kinds["window"] == windows, kinds


def test_ground_floor_doors_and_glazing(extractions):
    ex = extractions["ground"]
    doors = [o for o in ex.openings if o.kind == "door"]
    assert all(0.77 <= o.width <= 0.83 for o in doors)
    windows = sorted(o.width for o in ex.openings if o.kind == "window")
    assert windows == pytest.approx([2.17, 2.17, 2.68, 2.68], abs=0.02)   # the glazing towards the terraces
    # The doors drawn into continuous walls (the corridor doors in the north wall) are read as well.
    north = [o for o in doors if o.center[1] > 11.8]
    assert len(north) == 2


# --------------------------------------------------------------------------
# Stairs and furniture
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", list(REGIONS))
def test_two_stairs_with_two_flights(extractions, name):
    stairs = [f for f in extractions[name].furniture if f.type == "stair"]
    assert len(stairs) == 2
    for s in stairs:
        assert s.type_method == "rule" and s.status == "verified"
        assert len(s.details["stair"]["flights"]) == 2 and s.details["stair"]["turn"] == "U"
        assert all(0.25 <= f["spacing"] <= 0.31 for f in s.details["stair"]["flights"])


def test_ground_floor_furniture_typed_by_block_names(extractions):
    types = _types(extractions["ground"])
    assert types[("toilet", "block_name")] == 4                            # bowl and flush plate: one piece
    assert types[("washbasin", "block_name")] == 4
    assert types[("wardrobe", "block_name")] == 4
    assert types[("bed_double", "block_name")] == 2                        # YATAK, split from its nightstands
    beds = [f for f in extractions["ground"].furniture if f.type == "bed_double"]
    assert all(f.status == "verified" and "takes the name" in f.evidence["note"] for f in beds)


def test_basement_corner_sofas_are_l_shaped_candidates(extractions):
    ex = extractions["basement"]
    sofas = [c for c in ex.candidates if c["footprint"].get("shape") == "L"]
    assert len(sofas) == 2
    for c in sofas:
        assert sorted(c["footprint"]["size"]) == pytest.approx([1.97, 4.38], abs=0.02)
        assert "sofa_corner" in c["fits"] and "sofa_corner" in c["request"]["question"]["choices"]
        assert c["request"]["question"]["shape"] == "L"
        assert [f["rule"] for f in c["front_candidates"]] == ["L outline: the open inner corner is the front"]
    sides = sorted(f.details["l_outline"]["chaise_side"] for f in ex.furniture if f.details.get("l_outline"))
    assert sides == ["left", "right"]                                      # mirrored twins


def test_corner_sofas_with_agreeing_answers(pages, extractions):
    ex0 = extractions["basement"]
    ans = {"type": "sofa_corner", "front": "none", "confidence": 0.8, "reason": "fake answer"}
    answers = {c["key"]: {"qwen": dict(ans), "glm": dict(ans)} for c in ex0.candidates
               if c["footprint"].get("shape") == "L"}
    ex = core.extract(pages["basement"], "L0", "one_building.dwg", answers=answers)
    sofas = [f for f in ex.furniture if f.type == "sofa_corner"]
    assert len(sofas) == 2
    # Verified once the layout tables allow the corner sofa in a living room (track B); before that the two-pass
    # rule keeps it unverified with a warning (a type not allowed in the room).
    allowed = "sofa_corner" in (RS.allowed_types("living") or set())
    for f in sofas:
        assert f.status == ("verified" if allowed else "unverified") and f.type_method == "ai_two_pass"
        assert f.details["l_outline"]["chaise_depth"] == pytest.approx(1.97, abs=0.02)
        assert f.size == pytest.approx((4.38, 1.97), abs=0.02)             # width along the back, depth = chaise
        assert f.front_deg in (0.0, 180.0) and f.details.get("front_rule", "").startswith("L outline")
    # Facing each other across the party wall: the left dwelling's sofa faces west, its twin east.
    left, right = sorted(sofas, key=lambda f: f.center[0])
    assert (left.front_deg, right.front_deg) == (180.0, 0.0)
    assert (left.details["l_outline"]["chaise_side"], right.details["l_outline"]["chaise_side"]) == ("right", "left")
