"""The vision auditor, documents vs model (26 Oct 2026, user: "the audit is very weak, only the looks being judged ...
There was a veranda in real06, it has been fully missed"): the source plan drawn clean and turned like the model's
top-down view, one call per level with both images and the level's facts, every claim checked by code (CPU,
MockModel); the elevations against the exterior renders, with and without elevation drawings."""
import copy
import json
from pathlib import Path

import pytest
from PIL import Image

from wenart.agent.model import IMAGE_MAX_SIDE, MockModel
from wenart.audit import plan_vs_model as A
from wenart.blender.architect_actions import ACTIONS

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "real06_L0_audit_20261026.json"


@pytest.fixture()
def b06():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _png(path: Path, size=(64, 48), colour=(200, 200, 200)) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, colour).save(path)
    return path


def _claim(kind, change, *, label="", room="", target="", severity="major", aspect="presence",
           message="the plan and the model differ here"):
    return {"kind": kind, "change": change, "aspect": aspect, "label": label, "room": room, "target": target,
            "severity": severity, "message": message}


def _images(msg: dict) -> int:
    return sum(1 for p in msg["content"] if isinstance(p, dict) and p.get("type") == "image_url")


# --------------------------------------------------------------------------
# The level audit: real06 L0
# --------------------------------------------------------------------------

def test_the_missing_veranda_is_kept_and_wrong_claims_are_dropped(tmp_path, b06):
    plan = {"path": str(_png(tmp_path / "audit" / "plan_L0.png")), "method": "strokes", "region_id": "r3",
            "view": {"azimuth_deg": 225.0, "tilt_deg": 35.0},
            "texts": [{"text": t} for t in ("SALON", "39,15m²", "YEMEK BÖLÜMÜ", "VERANDA", "22,80m²", "BANYO")]}
    top = _png(tmp_path / "renders" / "top_L0_plan.jpg")
    answer = {"differences": [
        _claim("space", "missing_in_model", label="VERANDA 22,80 m²", severity="critical",
               message="the veranda labelled VERANDA 22,80 m² is missing"),
        _claim("door", "different_in_model", aspect="type", target="d_L0_099", room="r_L0_salon"),
        _claim("furniture", "missing_in_model", target="f_L0_011", room="r_L0_salon",
               message="the corner sofa of the plan is missing"),
        _claim("room", "missing_in_model", label="YEMEK BÖLÜMÜ", message="the dining room is missing"),
        _claim("furniture", "extra_in_model", target="f_L0_033", message="a wall cabinet the plan does not show"),
        _claim("space", "missing_in_model", label="BALKON", message="a balcony is missing"),
        _claim("fixture", "missing_in_model", target="f_L0_003", message="a drawn kitchen counter is missing"),
        _claim("door", "different_in_model", aspect="type", target="d_L0_006",
               message="the plan shows a pair of glazed doors, the model one wide leaf"),
        _claim("door", "missing_in_model", target="f_L0_020", message="a door is missing"),
    ]}
    m = MockModel(critic=[answer])
    rec = A.audit_level(m, b06, "L0", plan=plan, topdown=top, call_id="audit_L0", project_out=tmp_path)
    assert rec["error"] is None and len(m.requests) == 1
    kept = {f["target"]: f for f in rec["kept"]}
    veranda = kept["sa_L0_veranda"]
    assert veranda["line"] == "plan_vs_model" and veranda["check"] == "B1" and veranda["severity"] == "critical"
    assert veranda["owner"] == "site" and veranda["fix"] is None
    assert veranda["evidence"]["level"] == "L0" and veranda["evidence"]["label"] == "VERANDA 22,80 m²"
    assert veranda["evidence"]["plan_image"] == "audit/plan_L0.png"
    assert veranda["evidence"]["model_image"] == "renders/top_L0_plan.jpg"
    assert veranda["evidence"]["built"] is False
    assert kept["f_L0_003"]["check"] == "B7" and kept["f_L0_003"]["owner"] == "furniture"
    assert kept["d_L0_006"]["check"] == "B4" and kept["d_L0_006"]["owner"] == "openings"
    assert kept["d_L0_006"]["fix"] == "door_type"
    assert set(kept) == {"sa_L0_veranda", "f_L0_003", "d_L0_006"}
    reasons = {d["n"]: d["reason"] for d in rec["dropped"]}
    assert "not an id of the model" in reasons[2]                      # an unknown id
    assert "has built f_L0_011" in reasons[3]                          # "missing" but built (the corner sofa)
    assert "has built r_L0_salon" in reasons[4]                        # the dining part is in the salon
    assert "added_by_ai" in reasons[5]                                 # the furniture rules added it
    assert "no text of the plan" in reasons[6]                         # BALKON is no text of L0's plan
    assert "door claim on piece" in reasons[9]                         # a door claim on a kitchen sink
    for f in rec["kept"]:
        assert set(f) == {"line", "check", "severity", "target", "message", "evidence", "owner", "fix"}
        assert {"level", "plan_image", "model_image", "label"} <= set(f["evidence"])


def test_the_call_sends_both_images_the_facts_and_the_plans_labels(tmp_path, b06):
    plan = {"path": str(_png(tmp_path / "p.png")), "method": "strokes", "view": {"azimuth_deg": 225.0},
            "texts": [{"text": "VERANDA"}, {"text": "22,80m²"}, {"text": "MERDIVEN BOŞLUĞU"}]}
    m = MockModel(critic=[{"differences": []}])
    rec = A.audit_level(m, b06, "L0", plan=plan, topdown=_png(tmp_path / "t.jpg"), call_id="a1")
    assert rec["kept"] == [] and rec["dropped"] == [] and rec["error"] is None
    body = m.requests[0]
    assert body["temperature"] == 0.0 and body["response_format"]["json_schema"]["name"] == "audit"
    assert body["response_format"]["json_schema"]["strict"] is True
    user = body["messages"][1]
    assert _images(user) == 2
    text = user["content"][-1]["text"]
    assert "sa_L0_veranda: VERANDA" in text and "NOT BUILT" in text
    assert "VERANDA / 22,80m² -> sa_L0_veranda" in text
    assert "other texts on the plan: MERDIVEN BOŞLUĞU" in text
    assert "r_L0_salon: SALON, living" in text and "39,15 m² stated" in text
    assert "f_L0_003 kitchen_counter" in text.split("NOT built")[1]       # unbuilt pieces are told apart
    assert "turned and foreshortened like image 2" in text
    assert len(text) < 12000                                               # the facts stay short


def test_a_built_veranda_is_no_finding(tmp_path, b06):
    b = copy.deepcopy(b06)
    b["site"]["paving"] = [{"id": "pv_1", "area_id": "sa_L0_veranda", "source": "plan",
                            "polygon": [[-0.5, -2.0], [4.3, -2.0], [4.3, 0.3], [-0.5, 0.3]]}]
    assert A.area_built(b, b["site"]["areas"][0])
    claim = _claim("space", "missing_in_model", label="VERANDA", message="the veranda is missing")
    m = MockModel(critic=[{"differences": [claim]}])
    rec = A.audit_level(m, b, "L0", plan=str(_png(tmp_path / "p.png")), topdown=_png(tmp_path / "t.jpg"),
                        call_id="a2")
    assert rec["kept"] == [] and "has built sa_L0_veranda" in rec["dropped"][0]["reason"]


def test_a_space_the_reading_never_recorded_is_kept_for_the_reading(tmp_path, b06):
    plan = {"path": str(_png(tmp_path / "p.png")), "method": "strokes",
            "texts": [{"text": "TERAS"}, {"text": "9,40m²"}]}
    claim = _claim("space", "missing_in_model", label="TERAS 9,40m²", severity="minor",
                   message="the terrace TERAS 9,40 m² is missing")
    m = MockModel(critic=[{"differences": [claim]}])
    rec = A.audit_level(m, b06, "L0", plan=plan, topdown=_png(tmp_path / "t.jpg"), call_id="a3")
    f = rec["kept"][0]
    assert f["target"] == "building" and f["owner"] == "reading" and f["check"] == "B1"
    assert f["severity"] == "major"                      # a labelled space of 9.4 m² is at least major


def test_no_call_without_both_images(tmp_path, b06):
    m = MockModel(critic=[{"differences": []}])
    rec = A.audit_level(m, b06, "L0", plan={"path": None}, topdown=tmp_path / "none.jpg", call_id="a4")
    assert rec["error"] and "plan" in rec["error"] and "top-down" in rec["error"] and not m.requests


def test_the_checks_owners_and_fixes_are_typed():
    assert sorted(A.CHECKS) == [f"B{i}" for i in range(1, 10)]
    assert set(A.CHECK_OF_KIND.values()) <= set(A.CHECKS)
    assert all(k in A.CHECK_OF_KIND for k in A.KINDS + A.ELEVATION_KINDS)
    item = A.PLAN_SCHEMA["properties"]["differences"]["items"]
    assert item["additionalProperties"] is False and set(item["required"]) == set(item["properties"])
    combos = [(k, ch, asp, cat, t) for k in A.KINDS for ch in A.CHANGES for asp in A.ASPECTS
              for cat in ("room", "opening", "piece", "area", "wall", None)
              for t in ("door", "window", "opening", "sofa", "toilet", None)]
    for k, ch, asp, cat, t in combos:
        fix = A.fix_of(k, ch, asp, cat, t)
        assert fix is None or fix in ACTIONS
        assert A.owner_of(k, ch, asp, cat, t) in A.OWNERS
    assert A.fix_of("room", "different_in_model", "type", "room", "living") == "retype_room"
    assert A.fix_of("door", "missing_in_model", "presence", "opening", "opening") == "gap_to_door"
    assert A.fix_of("window", "different_in_model", "type", "opening", "door") == "door_to_window"
    assert A.fix_of("furniture", "extra_in_model", "presence", "piece", "sofa") == "remove_piece"
    assert A.fix_of("level", "different_in_model", "height", "opening", "door") == "snap_threshold"
    assert A.owner_of("space", "missing_in_model", "presence", "area", "other") == "site"
    assert A.owner_of("space", "missing_in_model", "presence", None, None, recorded=False) == "reading"


def test_labels_match_the_records_of_the_level(b06):
    assert A.match_label(b06, "L0", "VERANDA 22,80 m²")["id"] == "sa_L0_veranda"
    assert A.match_label(b06, "L0", "the covered veranda is missing", by_words=False)["id"] == "sa_L0_veranda"
    hit = A.match_label(b06, "L0", "Yemek bölümü", kind="room")
    assert hit["id"] == "r_L0_salon" and hit["built"]
    assert A.match_label(b06, "L0", "BALKON") is None
    assert A.match_label(b06, "L1", "VERANDA") is None                  # another level's record never matches
    assert A.stated_area("22,80m²") == 22.8 and A.stated_area("230") is None
    assert A.space_word("Balkon") == "balcony" and A.space_word("VERANDA") == "veranda"


# --------------------------------------------------------------------------
# The plan image: the source strokes, clean and turned like the top-down view
# --------------------------------------------------------------------------

def _plan_project(tmp_path: Path) -> tuple[Path, dict]:
    import ezdxf
    proj, out = tmp_path / "proj", tmp_path / "out"
    proj.mkdir()
    out.mkdir()
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    msp = doc.modelspace()
    for a, b in (((0, 0), (6, 0)), ((6, 0), (6, 4)), ((6, 4), (0, 4)), ((0, 4), (0, 0))):
        msp.add_line(a, b, dxfattribs={"layer": "DUVAR"})
    msp.add_lwpolyline([(0, 0), (3, 0), (3, -2), (0, -2)], close=True, dxfattribs={"layer": "BALKON"})
    msp.add_line((-3, 2), (9, 2), dxfattribs={"layer": "AKS"})             # a grid axis through the building
    msp.add_text("SALON", height=0.2, dxfattribs={"insert": (2.5, 2.0)})
    msp.add_text("VERANDA", height=0.2, dxfattribs={"insert": (0.8, -1.0)})
    msp.add_text("6,00m²", height=0.15, dxfattribs={"insert": (0.9, -1.4)})
    msp.add_text("600", height=0.15, dxfattribs={"insert": (2.8, 4.3)})     # a dimension figure
    doc.saveas(proj / "plan.dxf")
    b = {"project": {"id": "t", "source_folder": str(proj)},
         "documents": [{"id": "d1", "file": "plan.dxf", "format": "dxf", "pages": [
             {"page": 1, "class": "floor_plan", "kind": "vector", "level_id": "L0", "region_id": None,
              "region_box": None, "transform_to_building": [1.0, 0.0, 0.0, 0.0, 1.0, 0.0],
              "debug_image": "debug/plan_dxf_p1.png"}]}],
         "levels": [{"id": "L0", "label": "Ground floor", "elevation": 0.0, "ceiling_height": 2.8}],
         "walls": [{"id": f"w{i}", "level_id": "L0", "start": list(a), "end": list(c), "exterior": True}
                   for i, (a, c) in enumerate((((0, 0), (6, 0)), ((6, 0), (6, 4)), ((6, 4), (0, 4)),
                                               ((0, 4), (0, 0))))],
         "rooms": [{"id": "r_L0_salon", "level_id": "L0", "label": "Salon", "room_type": "living",
                    "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]}],
         "site": {"areas": [{"id": "sa_L0_veranda", "level_id": "L0", "label": "VERANDA", "anchor": [1.2, -1.0],
                             "build": False}]}}
    return out, b


def test_the_plan_image_is_drawn_from_the_source_strokes(tmp_path):
    out, b = _plan_project(tmp_path)
    rec = A.plan_image(out, "L0", building=b, orient="plan")
    assert rec["method"] == "strokes" and rec["orient"] == "plan" and Path(rec["path"]).is_file()
    texts = {t["text"]: t for t in rec["texts"]}
    assert {"SALON", "VERANDA", "6,00m²"} <= set(texts) and "600" not in texts     # no dimension figures
    with Image.open(rec["path"]) as im:
        assert max(im.size) <= IMAGE_MAX_SIDE
        assert im.getpixel((5, 5))[0] < 60                                   # the title bar
    assert rec["frame_m"][1] <= -2.0                                         # the veranda outside the walls is in
    assert A.axis_line([(-3, 2), (9, 2)], A.walls_box(b, "L0"))             # the grid axis is left out
    assert not A.axis_line([(0, 0), (6, 0)], A.walls_box(b, "L0"))          # a wall never is


def test_the_plan_image_is_turned_like_the_top_down_view(tmp_path):
    out, b = _plan_project(tmp_path)
    (out / "topdown").mkdir()
    frame = json.dumps({"azimuth_deg": 180.0, "tilt_deg": 0.0})
    (out / "topdown" / "top_L0.png.frame.json").write_text(frame, encoding="utf-8")
    turned = A.plan_image(out, "L0", building=b, out_path=out / "turned.png")
    plain = A.plan_image(out, "L0", building=b, orient="plan", out_path=out / "plain.png")
    assert turned["view"]["source"] == "frame.json" and plain["view"] is None

    def rows(rec):
        return {t["text"]: t["at"] for t in rec["texts"]}

    # the texts keep their building position; the drawing is turned (looking south, the veranda is at the top)
    assert rows(turned)["VERANDA"] == rows(plain)["VERANDA"]
    proj = A._projector(turned["view"])
    assert proj(1.2, -1.0)[1] > proj(2.5, 2.0)[1]                           # the veranda above the salon
    assert A._projector(None)(1.2, -1.0)[1] < A._projector(None)(2.5, 2.0)[1]
    view = A.topdown_view(tmp_path / "nowhere", "L0")
    assert view["source"] == "topdown defaults" and view["azimuth_deg"] == 225.0


def test_a_level_without_a_transform_gets_its_sheets_region(tmp_path):
    out, b = _plan_project(tmp_path)
    b["documents"][0]["pages"][0]["transform_to_building"] = None
    sheets = {"regions": [{"id": "r1", "class": "floor_plan", "file": "plan.dxf", "page": 1,
                           "box": [-4.0, -3.0, 10.0, 5.0], "metres_per_unit": 1.0}],
              "levels": [{"id": "L0", "base_region": "r1"}]}
    (out / "sheets.json").write_text(json.dumps(sheets), encoding="utf-8")
    rec = A.plan_image(out, "L0", building=b)
    assert rec["method"] == "region" and rec["region_id"] == "r1" and Path(rec["path"]).is_file()
    assert "VERANDA" in {t["text"] for t in rec["texts"]}


def test_without_a_source_the_reading_debug_image_stands_in(tmp_path):
    out, b = _plan_project(tmp_path)
    (tmp_path / "proj" / "plan.dxf").unlink()
    _png(out / "debug" / "plan_dxf_p1.png", size=(300, 200))
    rec = A.plan_image(out, "L0", building=b)
    assert rec["method"] == "debug_image" and Path(rec["path"]).is_file() and rec["texts"] == []
    m = MockModel(critic=[{"differences": []}])
    A.audit_level(m, b, "L0", plan=rec, topdown=_png(tmp_path / "t.jpg"), call_id="a5")
    assert "what a program read, not the drawing" in m.requests[0]["messages"][1]["content"][-1]["text"]


# --------------------------------------------------------------------------
# Elevations
# --------------------------------------------------------------------------

def _sheets(side="all"):
    return {"regions": [{"id": "r7", "class": "elevation", "file": "real06.dwg", "page": 1,
                         "box": [0.0, 0.0, 0.43, 0.166], "metres_per_unit": 50.0, "title": None},
                        {"id": "r5", "class": "section", "file": "real06.dwg", "page": 1,
                         "box": [0.0, 0.0, 0.45, 0.18], "metres_per_unit": 50.0, "title": None},
                        {"id": "r3", "class": "floor_plan", "file": "real06.dwg", "page": 1}],
            "exterior": {"openings_seen": [{"region": "r7", "side": side, "view_bearing_deg": None, "windows": 0,
                                            "doors": 0, "positions_m": []}]}}


def _renders(tmp_path):
    return {"ext_6": {"image": str(_png(tmp_path / "ext_6.jpg", (96, 54))), "sides": ["front"], "kind": "frontal"},
            "ext_3": {"image": str(_png(tmp_path / "ext_3.jpg", (96, 54))), "sides": ["back", "left"],
                      "kind": "corner"}}


def _eclaim(kind, change, *, label="", target="", dc=-1, mc=-1, droof="none", mroof="none", aspect="presence",
            severity="major", message="the drawing and the model differ here"):
    return {"kind": kind, "change": change, "aspect": aspect, "label": label, "target": target, "drawn_count": dc,
            "model_count": mc, "drawn_roof": droof, "model_roof": mroof, "severity": severity, "message": message}


def test_elevations_of_an_unknown_side_are_compared_with_every_exterior_view(tmp_path, b06):
    drawings = {"r7": str(_png(tmp_path / "r7.png")), "r5": str(_png(tmp_path / "r5.png"))}
    front = A.side_counts(b06, (0.0, -1.0))
    answer = {"view": "ext_6", "differences": [
        _eclaim("space", "missing_in_model", severity="minor",
                message="the covered veranda with columns and a balustrade is missing"),
        _eclaim("floors", "different_in_model", aspect="count", dc=2, mc=3, message="three storeys built"),
        _eclaim("roof", "different_in_model", aspect="type", droof="hip", mroof="gable",
                message="the drawing has a hip roof, the model a gable"),
        _eclaim("window", "different_in_model", aspect="count", dc=front["window"], mc=front["window"] + 2,
                message="the windows of this side differ"),
        _eclaim("door", "different_in_model", aspect="type", target="d_L0_777", message="another door kind"),
    ]}
    section = {"view": "none", "differences": [_eclaim("window", "missing_in_model", message="a window is missing")]}
    m = MockModel(critic=[answer, section])
    rec = A.audit_elevations(m, b06, sheets=_sheets(), renders=_renders(tmp_path), call_id="el",
                             project_out=tmp_path, drawings=drawings)
    assert rec["calls"] == 2 and [r["region_id"] for r in rec["regions"]] == ["r7", "r5"]
    r7 = rec["regions"][0]
    assert r7["view"] == "ext_6" and r7["images"][1].startswith("audit/exterior_views_")
    body = m.requests[0]
    assert _images(body["messages"][1]) == 2
    view_enum = body["response_format"]["json_schema"]["schema"]["properties"]["view"]["enum"]
    assert view_enum == ["ext_6", "ext_3", "none"]
    assert "every exterior render" in body["messages"][1]["content"][-1]["text"]
    assert len(rec["kept"]) == 1
    f = rec["kept"][0]
    assert f["line"] == "elevations" and f["check"] == "B1" and f["target"] == "sa_L0_veranda"
    assert f["severity"] == "major" and f["owner"] == "site" and f["evidence"]["view"] == "ext_6"
    reasons = " | ".join(d["reason"] for d in rec["dropped"])
    assert "the model has 2 storey(s)" in reasons
    assert "roof is built as hip" in reasons
    assert f"the model has {front['window']} windows on this side, as drawn" in reasons
    assert "'d_L0_777' is not an id" in reasons
    assert "a section is compared for floors, roof and levels only" in reasons


def test_an_elevation_of_a_known_side_gets_the_render_of_that_side(tmp_path, b06):
    renders = _renders(tmp_path)
    m = MockModel(critic=[{"view": "ext_6", "differences": []}, {"view": "none", "differences": []}])
    rec = A.audit_elevations(m, b06, sheets=_sheets("front"), renders=renders, call_id="el2", project_out=tmp_path,
                             drawings={"r7": str(_png(tmp_path / "r7.png")), "r5": str(_png(tmp_path / "r5.png"))})
    r7 = rec["regions"][0]
    assert r7["side"] == "front" and r7["view"] == "ext_6" and r7["images"][1] == "ext_6.jpg"
    text = m.requests[0]["messages"][1]["content"][-1]["text"]
    assert "the exterior render ext_6" in text and "openings facing this side (front)" in text
    schema = m.requests[0]["response_format"]["json_schema"]["schema"]
    assert schema["properties"]["view"]["enum"] == ["ext_6", "none"]


def test_no_elevation_drawings_no_call(tmp_path, b06):
    m = MockModel(critic=[])
    for sheets in (None, {"regions": [{"id": "r3", "class": "floor_plan"}]}):
        rec = A.audit_elevations(m, b06, sheets=sheets, renders=_renders(tmp_path), call_id="el3")
        assert rec["calls"] == 0 and rec["kept"] == [] and "no elevation or section drawings" in rec["note"]
    assert not m.requests
