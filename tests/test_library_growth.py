"""Milestone 12 track B: contact sheets, the gap report and the growth scaffolding (docs/milestone12.md §6.1 output,
§6.4 D24): lists only, and no ingest without an approved list."""
import json

import numpy as np
import pytest
from PIL import Image

from wenart.assets.audit import gaps as G
from wenart.assets.audit import growth as GR
from wenart.assets.audit import sheets as SH
from wenart.furniture import catalog as C


def test_sheet_grid_and_labels(tmp_path):
    assert SH.grid(0) == (1, 1) and SH.grid(5, 6) == (5, 1) and SH.grid(13, 6) == (6, 3)
    assert SH.status_key("removed?") == "removed" and SH.status_key("vision?") == "pending"
    thumb = tmp_path / "t.jpg"
    Image.new("RGB", (64, 64), (0, 0, 255)).save(thumb)
    tiles = [{"id": "abo_a", "status": "keep", "reasons": [], "source": thumb},
             {"id": "objaverse_b", "status": "removed", "reasons": ["the title says park bench: an outdoor piece"],
              "source": None}]
    out = SH.contact_sheet("bench", tiles, tmp_path / "bench.jpg", px=64, cols=6)
    img = np.asarray(Image.open(out).convert("RGB"))
    assert img.shape[1] == 2 * (64 + 12)
    red = img[34 + 2, 76 + 2]                                     # the second tile's border is red
    assert red[0] > 150 and red[1] < 100
    assert SH.label_lines("objaverse_b", "removed", ["a very long reason " * 4])[1].startswith("removed: a very")


def test_gap_table_counts_family_and_neutral():
    items = [{"id": "a", "type": "sofa", "styles": ["rustic"]}, {"id": "b", "type": "sofa", "styles": ["neutral"]},
             {"id": "c", "type": "sofa", "styles": ["rustic"]}]
    statuses = {"a": "keep", "b": "fix", "c": "removed"}
    groups = {"living": [("seating", "anchor", ("sofa",)), ("seating", "partner", ("armchair",))]}
    rows = G.gap_table(items, statuses, groups, {"gaps": {"anchor_min": 5, "partner_min": 3}})
    rustic = next(r for r in rows if r["type"] == "sofa" and r["family"] == "rustic")
    modern = next(r for r in rows if r["type"] == "sofa" and r["family"] == "modern")
    assert (rustic["count"], rustic["gap"]) == (2, 3) and (modern["count"], modern["target"]) == (1, 5)
    arm = next(r for r in rows if r["type"] == "armchair" and r["family"] == "rustic")
    assert arm["target"] == 3 and arm["gap"] == 3
    md = G.gaps_markdown(rows, "Gaps")
    assert "| seating | anchor | sofa | " in md and "**2**" in md and "| sofa | " in md


def test_groups_yaml_is_read_leniently(tmp_path):
    p = tmp_path / "groups.yaml"
    p.write_text("groups:\n  seating:\n    room_types: [living]\n    anchor: {type: sofa}\n"
                 "    partners: [{type: table_coffee, role: partner}, armchair]\n", encoding="utf-8")
    g = G.groups_from_yaml(p)
    assert g == {"living": [("seating", "anchor", ("sofa",)), ("seating", "partner", ("table_coffee",)),
                            ("seating", "partner", ("armchair",))]}
    assert G.groups_from_yaml(tmp_path / "missing.yaml") is None
    # track G's shape (wenart/furniture/groups.yaml): anchor types, partners with their roles
    p.write_text("version: 1\nrules: {walkway: {min: 0.6}}\ngroups:\n  seating:\n    room_types: [living]\n"
                 "    anchor: {types: [sofa, sofa_corner], place: wall}\n"
                 "    partners:\n      - {role: tv, type: tv_unit, required: true}\n"
                 "      - {role: coffee, type: table_coffee, required: false}\n", encoding="utf-8")
    assert G.groups_from_yaml(p) == {"living": [("seating", "anchor", ("sofa",)),
                                                ("seating", "anchor", ("sofa_corner",)),
                                                ("seating", "partner", ("tv_unit",)),
                                                ("seating", "partner", ("table_coffee",))]}
    merged = G.merge_groups(G.groups_from_yaml(p), G.BUILTIN_GROUPS)
    assert merged["living"][:4] == G.groups_from_yaml(p)["living"]          # groups.yaml first
    assert ("decor", "partner", ("wall_art",)) in merged["living"]           # the built-in decor rows added
    assert ("media", "anchor", ("tv_unit",)) not in merged["living"]         # tv_unit already named by groups.yaml
    assert G.merge_groups(None, G.BUILTIN_GROUPS) == G.BUILTIN_GROUPS
    for room, members in G.BUILTIN_GROUPS.items():
        for _g, role, types in members:
            assert role in ("anchor", "partner")
            assert all(t in C.FURNITURE_TYPES or t in C.DECOR_TYPES for t in types), (room, types)


PH = {"ArmChair_01": {"type": 2, "name": "Arm Chair 01", "category": "Furniture/Seating/Chairs",
                      "categories": ["furniture"], "tags": ["chair"], "dimensions": [848, 766, 1065]},
      "park_bench_01": {"type": 2, "name": "Park Bench 01", "category": "Furniture/Seating/Benches",
                        "categories": ["furniture"], "tags": ["outdoor", "park"], "dimensions": [1800, 600, 800]},
      "ceramic_vase_09": {"type": 2, "name": "Ceramic Vase 09", "category": "Decor & Art/Vases & Vessels/Ceramic Vases",
                          "categories": ["decorative"], "tags": [], "dimensions": [200, 200, 300]},
      "rock_01": {"type": 2, "name": "Rock 01", "category": "Nature/Rocks", "categories": ["nature"],
                  "dimensions": [500, 500, 500]},
      "sofa_02": {"type": 2, "name": "Sofa 02", "category": "Furniture/Seating/Sofas & Couches",
                  "categories": ["furniture"], "dimensions": [1807, 818, 709]}}
FILES = {"gltf": {"2k": {"gltf": {"size": 1_000_000, "include": {"a.jpg": {"size": 2_000_000}}}}}}


def test_polyhaven_candidates_from_canned_api_answers():
    cands = GR.polyhaven_candidates(PH, {"sofa_02"}, lambda aid: FILES)
    assert [(c["id"], c["type"]) for c in cands] == [("ceramic_vase_09", "vase"), ("ArmChair_01", "armchair")]
    arm = cands[1]
    assert arm["licence"] == "CC0" and arm["size_mb"] == 3.0 and arm["fits_real_size"] is True


def test_the_committed_polyhaven_list():
    doc = json.loads((GR.growth_dir() / "candidates_polyhaven.json").read_text(encoding="utf-8"))
    used = {e["id"].lower() for e in C.load(library=False).data["entries"] if e.get("id")}
    assert doc["source"] == "polyhaven" and doc["licences"] == ["CC0"] and doc["count"] >= 50
    for c in doc["candidates"]:
        assert c["id"].lower() not in used and c["type"] and c["licence"] == "CC0"
    assert doc["picked_size_mb"] < 1500


def test_gso_and_abo_helpers():
    files = [{"rfilename": "Room_Essentials_Bowl_Turquiose.zip", "lfs": {"size": 4_090_000}},
             {"rfilename": "3D_Dollhouse_Sofa.zip", "size": 1},
             {"rfilename": "Hefty_Waste_Basket_Decorative_Bronze.zip", "size": 1},
             {"rfilename": "ACE_Coffee_Mug_Kristen_16_oz_cup.zip", "size": 1}]
    cands = GR.gso_candidates(files)
    assert [(c["type"], c["pick"]) for c in cands] == [("bowl", True), (None, False)]
    assert GR.abo_family("Farmhouse") == "rustic" and GR.abo_family("Traditional") == "classic"
    assert GR.abo_family("Modern") is None
    plan = GR.infinigen_plan()
    assert plan["licence"].startswith("BSD-3") and any(b["type"] == "toilet" for b in plan["batch"])


def test_ingest_refuses_without_an_approved_list(tmp_path, monkeypatch, capsys):
    from wenart.assets import models as M
    monkeypatch.setattr(M, "fetch_model", lambda *a, **k: pytest.fail("downloaded without an approval"))
    assert GR.main(["polyhaven", "ingest", "--out", str(tmp_path)]) == 1
    assert "refused" in capsys.readouterr().out
    (tmp_path / "growth").mkdir()
    (tmp_path / "growth" / "approved_polyhaven.json").write_text(json.dumps({"ids": ["a"]}), encoding="utf-8")
    with pytest.raises(PermissionError):
        GR.approved("polyhaven", tmp_path)                       # no approved_by / approved_utc: not an approval
    assert GR.main(["polyhaven", "ingest", "--out", str(tmp_path)]) == 1
    (tmp_path / "growth" / "approved_polyhaven.json").write_text(json.dumps(
        {"source": "polyhaven", "approved_by": "user", "approved_utc": "2026-10-11T09:00:00Z", "ids": ["a"]}))
    assert GR.approved("polyhaven", tmp_path)["ids"] == ["a"]
