"""Fix round after P6b (23 Oct 2026), part J2 (render, exterior and reading side): the P6a review findings left for the
lead and the build tracks' asks for these files. Each test fails on HEAD cd7f34b (before this part) or names the
mutation it guards.

- ``core._reread_unknowns``: the whole-part branch (a coat closet or a rug set read whole before the re-read) is also
  reached by a candidate the AI passes typed as a table. Such a piece now keeps the AI's type as ``ai_overridden``
  (the report's type_disagreement conflict) when the drawing types it otherwise, with ``split_override_text``'s note;
  "still unknown after its answers" is said only of a candidate whose type is ``unknown``.
- ``pipeline._wall_dict`` writes a wall's ``corrected_by_ai`` label (``openings._mark_lined``) into building.json, and
  the ingest report lists those walls by id (``_inferred_section``) and gives every gap's rule and note in the Gaps
  table (``_generic_sections``).
- ``schemas.EXPOSURE`` types the exposure's ``wb_walls`` (``render.wall_rig_record``).
- ``symbols.reread``: a line on a structure layer (real03's shear-wall end lines on 'MYD - BA') is no column.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import jsonschema
import pytest

import _real01_page as RP
from test_m13_p6a_reading import _hanger, _poly, _rug_set
from test_m13_p6a_render import _manifest
from test_m13_p6b_reading import _partition, _run
from test_reading_symbols import TABLE, _on, _rect, _room
from wenart.blender import render as R
from wenart.blender import schemas
from wenart.ingest import pipeline as P
from wenart.ingest.generic import core as CORE
from wenart.ingest.generic import reading as RD
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import FurnitureItem, LevelExtraction

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# core._reread_unknowns: a whole part the passes typed as a table
# --------------------------------------------------------------------------

def _closet_strokes() -> list[Stroke]:
    """real04's corridor coat closet as the P6a reading test draws it (1.517 x 0.60 m outline, double rail, 14
    hangers in two block inserts, two chair-sized end parts): the strokes of real02's sym_L1_007 / 008 case."""
    strokes = [_poly("o", [(0.0, 0.0), (1.517, 0.0), (1.517, 0.6), (0.0, 0.6)], closed=True),
               _poly("rail_a", [(0.02, 0.29), (1.497, 0.29)]), _poly("rail_b", [(0.02, 0.31), (1.497, 0.31)]),
               _poly("c1", [(-0.45, 0.1), (-0.05, 0.1), (-0.05, 0.5), (-0.45, 0.5)], closed=True),
               _poly("c2", [(1.57, 0.1), (1.97, 0.1), (1.97, 0.5), (1.57, 0.5)], closed=True)]
    for k in range(14):
        strokes += [Stroke(id=st.id, kind=st.kind, pts=st.pts, closed=st.closed, block="askilik")
                    for st in _hanger(f"INSERT:{37516 + k // 7}/{k % 7}", 0.10 + 0.095 * k)]
    return strokes


def _typed_candidate(part, key: str, ai: tuple[str, str]) -> dict:
    """An answered candidate whose piece carries the passes' type: the type both passes agree on, else unknown (as
    the core's answers make it)."""
    fp = SY.footprint([p for s in part.segs for p in s.pts], 0.0)
    item = FurnitureItem(type=ai[0] if ai[0] == ai[1] else "unknown", type_raw=None, center=fp[0],
                         size=(fp[1], fp[2]), rotation_deg=0.0, front_deg=None, box=[0, 0, 1, 1],
                         entity=part.stroke_ids()[0], evidence={"entity": "x"}, status="unverified",
                         type_method="ai" if ai[0] == ai[1] else "none", details={"candidate_key": key},
                         type_candidates=[{"type": t, "model": m, "pass": k + 1, "confidence": 0.8}
                                          for k, (t, m) in enumerate(zip(ai, ("qwen", "glm")))])
    return {"key": key, "item": item, "_part": part}


def _reread(strokes: list[Stroke], key: str, ai: tuple[str, str]):
    part = SY.Cluster(SY._segments(strokes, set()))
    ex = LevelExtraction(file="t.dxf", page=1, level_id="L1", units="mm", report={"pending": [], "answers_applied": 2})
    replaced, _loose = CORE._reread_unknowns(ex, [_typed_candidate(part, key, ai)], [], [], [], [], [], [], "L1",
                                             "t.dxf", None, 1.0, False, False, strokes_m=strokes)
    return replaced[key], ex.notes


class _Build:
    """The two members of ``ProjectBuild`` that ``reading.log_overrides`` uses."""

    def __init__(self, furniture: list[dict]):
        self.building = {"furniture": furniture}
        self.conflicts: list[dict] = []

    def conflict(self, kind, element_ids, description, resolution):
        self.conflicts.append({"kind": kind, "element_ids": list(element_ids), "description": description,
                               "resolution": resolution})


def test_a_closet_both_passes_typed_as_a_coffee_table_keeps_the_ai_override():
    """The P6a review finding: a coat closet whose first fitting type is table_coffee (real02's sym_L1_007 / 008
    questions offer it), typed table_coffee by both passes (a fresh recognition or a crop change), was replaced by a
    wardrobe with no ``ai_overridden`` and the note "still unknown after its answers". Fails on cd7f34b. Now the
    wardrobe keeps the AI's type and the split's reason, the note says what the passes typed, and
    ``reading.log_overrides`` writes the type_disagreement conflict (CLAUDE.md trust order: every conflict is
    listed)."""
    made, notes = _reread(_closet_strokes(), "sym_L1_007", ("table_coffee", "table_coffee"))
    assert [m.type for m in made] == ["wardrobe"] and made[0].details["reread_of"] == "sym_L1_007"
    over = made[0].details["ai_overridden"]
    assert over["type"] == "table_coffee" and [c["type"] for c in over["type_candidates"]] == ["table_coffee"] * 2
    assert over["reason"].startswith("a coat closet: hanging rail with hangers")
    assert any(n.startswith("sym_L1_007: typed table_coffee by the AI passes, but drawn as a coat closet")
               for n in notes)
    assert not any("still unknown" in n for n in notes)
    build = _Build([{"id": "f_L1_021", "type": "wardrobe"}])
    assert RD.log_overrides(build, {"f_L1_021": made[0]}) == 1
    assert build.conflicts[0]["kind"] == "type_disagreement"
    assert "the AI passes typed it table_coffee; a coat closet" in build.conflicts[0]["description"]


def test_a_closet_the_passes_left_unknown_is_still_read_whole_with_no_override():
    """Unchanged (the P6a fix): passes unknown / bench leave the piece unknown; the whole part is one wardrobe, the
    note says "still unknown after its answers", and nothing is overridden."""
    made, notes = _reread(_closet_strokes(), "sym_L1_008", ("unknown", "bench"))
    assert [m.type for m in made] == ["wardrobe"] and "ai_overridden" not in made[0].details
    assert any(n.startswith("sym_L1_008: still unknown after its answers, but drawn as a coat closet") for n in notes)


@pytest.mark.parametrize("ai, overridden", [(("table_coffee", "table_coffee"), True),
                                            (("table_dining", "table_dining"), False)])
def test_a_rug_set_typed_as_a_table_says_so_and_keeps_a_type_disagreement_only(ai, overridden):
    """A rug set (real04's play-room block: a 0.80 m round table, two chairs, the rug outline) the passes typed as a
    table: the note is the split's ("typed <type> by the AI passes, but drawn as a table with 2 chairs on a rug
    outline"), never "still unknown". The rule table is table_dining (the first table type its size fits), so a
    table_coffee answer is a type disagreement (``ai_overridden``) and a table_dining answer is none: the M12 re-read
    of a table answer with its chairs never recorded one, and a conflict that names the same type twice would be
    false. Fails on cd7f34b (the "still unknown" note, no override)."""
    made, notes = _reread(_rug_set(), "sym_L1_003", ai)
    assert [m.type for m in made] == ["table_dining", "chair", "chair", "unknown"]
    assert made[3].details["not_furniture"]["as"] == "rug"
    assert ("ai_overridden" in made[0].details) is overridden
    if overridden:
        assert made[0].details["ai_overridden"]["type"] == "table_coffee"
        assert "rug outline" in made[0].details["ai_overridden"]["reason"]
    assert any(n.startswith(f"sym_L1_003: typed {ai[0]} by the AI passes, but drawn as a table with 2 chairs on a "
                            "rug outline") for n in notes)
    assert not any("still unknown" in n for n in notes)


# --------------------------------------------------------------------------
# pipeline: corrected walls in building.json and the ingest report
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def lined_walls():
    """real03's hall-living partition in small (``test_m13_p6b_reading._partition``): the 0.30 m shear walls a
    lined gap splits, each with ``corrected_by_ai``, and the gap log."""
    out_walls, _openings, log, _ = _run(*_partition())
    fixed = [w for w in out_walls if getattr(w, "corrected_by_ai", None)]
    assert len(fixed) == 2
    return out_walls, log


def test_a_corrected_wall_keeps_its_label_in_building_json(lined_walls):
    """F_reading's ask: ``_wall_dict`` copies the WallItem's ``corrected_by_ai`` (by, stage, rule, reason, evidence,
    before) into the wall record, a copy (editing the building leaves the reading's record alone); a plain wall has
    no such key. The record stays valid under the building schema's wall. Fails on cd7f34b (no key)."""
    out_walls, _log = lined_walls
    fixed = [w for w in out_walls if getattr(w, "corrected_by_ai", None)]
    plain = [w for w in out_walls if not getattr(w, "corrected_by_ai", None)]
    rec = P._wall_dict("L0", fixed[0], "w_L0_089", 2.7)
    label = rec["corrected_by_ai"]
    assert label == fixed[0].corrected_by_ai and label is not fixed[0].corrected_by_ai
    assert label["rule"] == "lined_gap" and label["by"] == "code" and label["stage"] == "reading"
    assert label["before"] == {"start": [3.3, 0.0], "end": [3.3, 7.7], "thickness": 0.3}
    label["before"]["start"][0] = 99.0
    assert fixed[0].corrected_by_ai["before"]["start"][0] == 3.3
    assert "corrected_by_ai" not in P._wall_dict("L0", plain[0], "w_L0_001", 2.7)
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/wall"}).validate(
        P._wall_dict("L0", fixed[0], "w_L0_089", 2.7))


def test_the_ingest_report_lists_the_corrected_walls_by_id(lined_walls):
    """``_inferred_section`` lists every wall with ``corrected_by_ai`` by its building id, with the wall it was
    before, the rule and the reason (the page notes name them by coordinates only). Fails on cd7f34b (no section
    for a building whose only labelled items are corrected walls)."""
    out_walls, _log = lined_walls
    walls = [P._wall_dict("L0", w, f"w_L0_{k:03d}", 2.7) for k, w in enumerate(out_walls)]
    lines = P._inferred_section({"walls": walls, "furniture": []})
    text = "\n".join(lines)
    assert "Walls corrected by the reading: 2" in text
    rows = [ln for ln in lines if ln.startswith("| w_L0_") and "lined_gap" in ln]
    assert len(rows) == 2
    assert all("(3.30, 0.00)-(3.30, 7.70) 0.300" in r and "a 0.10 m wall (duvar_a, duvar_b)" in r for r in rows)
    assert P._inferred_section({"walls": [w for w in walls if not w.get("corrected_by_ai")], "furniture": []}) == []


def _report_build(gaps: list[dict]):
    work = SimpleNamespace(where="t.dxf p1", extraction=SimpleNamespace(scale={}, report={"gaps": gaps}))
    build = SimpleNamespace(generic=[work], questions=[], code_typed={}, code_typed_methods={})
    b = {"project": {"unit_system": "metric"}, "documents": [], "rooms": [], "site": {}, "furniture": [],
         "levels": [], "openings": []}
    return b, build


def test_the_gaps_table_gives_each_gap_its_rule_and_note(lined_walls):
    """F_reading's ask: the Gaps table has a "Rule and note" column: the rule that decided the gap (lined_gap,
    inside_wall, wall_faces, no_glass) with its note, or a closed gap's warning, else "-"; the windows dropped for
    want of glass (kind continuous, class none) are rows with their rule. Fails on cd7f34b (no such column)."""
    _out_walls, log = lined_walls
    lined = [e for e in log if e.get("rule") == "lined_gap"]
    assert lined
    dropped = {"kind": "continuous", "class": "none", "rule": "no_glass", "width": 1.2, "strokes": ["s1"],
               "note": "1 line(s) of their own along the 1.20 m stretch, 0 glass between the faces: no window"}
    closed = {"kind": "run", "class": "closed", "width": 0.04, "warning": "gap of 0.040 m < 0.05 m closed"}
    lines = P._generic_sections(*_report_build(lined + [dropped, closed]))
    at = lines.index("## Gaps")
    assert lines[at + 2] == "| Page | Kind | Class | Width | Owned strokes | Rule and note |"
    rows = [ln for ln in lines[at + 4:] if ln.startswith("| t.dxf p1 |")]
    assert len(rows) == len(lined) + 2
    assert all(r.count("|") == 7 for r in rows)
    assert all(f"| lined_gap; {e['note']} |" in r for r, e in zip(rows, lined))
    assert rows[-2].startswith("| t.dxf p1 | continuous | none |") and "| no_glass; 1 line(s) of their own" in rows[-2]
    assert rows[-1].endswith("| - | gap of 0.040 m < 0.05 m closed |")


# --------------------------------------------------------------------------
# schemas: the exposure's wb_walls
# --------------------------------------------------------------------------

# P6b's giris_holu_2 on the shim (test_m13_p6b_render), as the two metering passes give it
LIT = {"illuminant": [3.0, 2.4, 1.5], "wall_illuminant": [1.6, 1.1, 0.6], "wall_frac": 0.5789}
DAY = {"illuminant": [1.0, 1.0, 0.9], "wall_illuminant": [0.5, 0.5, 0.45], "wall_frac": 0.5789}


def _exposure(walls) -> dict:
    return _manifest({"exposure": dict(_manifest({})["renders"][0]["exposure"], wb_walls=walls)})


@pytest.mark.parametrize("walls", [
    None,
    R.wall_rig_record(LIT, DAY, [1.5, 1.0, 0.566]) | {"rig_kelvin": 3284.1},
    R.wall_rig_record(LIT, None, None),                                    # a daylight pass without walls
    R.wall_rig_record(dict(LIT, wall_illuminant=None), DAY, None),        # no light on the walls
    R.wall_rig_record(LIT, dict(DAY, wall_illuminant=[1.59, 1.09, 0.59]), [1.5, 1.0, 0.566]),   # under the floor
])
def test_every_wall_rig_record_is_a_valid_wb_walls(walls):
    """Every record ``render.wall_rig_record`` writes (and None, without a wall metering) is valid: the next pod's GPU
    test validates its render manifest."""
    schemas.validate_render_manifest(_exposure(walls))


@pytest.mark.parametrize("bad", [
    "measured",                                                            # not an object
    {k: v for k, v in R.wall_rig_record(LIT, DAY, None).items() if k != "rule"},
    dict(R.wall_rig_record(LIT, DAY, None), share=1.5),
    dict(R.wall_rig_record(LIT, DAY, None), rig_rgb=[1.0, 0.5]),
    dict(R.wall_rig_record(LIT, DAY, None), rig_rb="4.17"),
])
def test_a_malformed_wb_walls_is_refused(bad):
    """G_render's ask: ``EXPOSURE`` types ``wb_walls`` (``WB_WALLS``). Fails on cd7f34b: any value was accepted."""
    with pytest.raises(jsonschema.ValidationError):
        schemas.validate_render_manifest(_exposure(bad))


# --------------------------------------------------------------------------
# symbols.reread: a line on a structure layer is no column
# --------------------------------------------------------------------------

def test_a_line_on_a_structure_layer_in_a_re_read_cluster_is_no_column():
    """F_reading's ask, narrowed: real03's shear-wall end lines ('MYD - BA', 0.85 m and 0.30 m long) inside a re-read
    cluster were kept as not-built "columns" of 0.85 x 0.00 m (six on this round's replay). Fails on cd7f34b (two
    columns, one of them a line). Now the line is dropped and named in the notes; the real 0.40 m column on 'A-BA'
    (real02 / real04) stays a column, and a structure outline as thin as a line's neighbour (a 0.06 m strip) too."""
    walls = _room()
    sofa = _rect(1.0, 1.0, 3.2, 1.9)
    column = _on("A-BA", _rect(3.2, 1.0, 3.6, 1.4))[0]
    end_line = _on("D BLOK_STA_NK$0$MYD - BA", RP.stroke([(5.0, 1.2), (5.85, 1.2)]))[0]
    strip = _on("A-BA", _rect(1.0, 1.9, 1.3, 1.96))[0]
    notes: list[str] = []
    got = SY.reread(SY.Cluster(SY._segments([sofa, column, end_line, strip], set())), SY._Ctx("t.dxf", 1, 1.0, 0.0,
                    "L0"), TABLE, walls, [], [TP.wall_polygon(w) for w in walls], [], notes, why="test")
    cols = [it for it in got["items"] if (it.details.get("not_furniture") or {}).get("as") == "column"]
    assert sorted(tuple(sorted(round(v, 2) for v in it.size)) for it in cols) == [(0.06, 0.3), (0.4, 0.4)]
    assert all(min(it.size) > 0.0 for it in got["items"])
    assert [n for n in notes if "1 line(s) on a structure layer thinner than 0.05 m dropped, no column" in n
            and end_line.id in n]
