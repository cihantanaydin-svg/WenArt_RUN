"""Milestone 13 track T7 (docs/milestone13.md §5.1 phase 2, §13.1, §13.2 rows ``hssd.py`` and ``demands.py``): the
drawn demands and the size grid of the committed buildings, the coverage per licence mode, the HSSD candidates and
entries, the growth lists, the growth job's steps and the audit gates.

CPU only: the HSSD metadata and the Hub are never touched (a small fake table and fake fetchers); the committed
lists under results/library/growth are read as data.

Fix round after P3 (16-17 Oct 2026): the title flags ``branded`` / ``other_use``, the ``sanitary_finish`` check and
the committed catalogue's audit records of the P3 findings (a Disney CARS cushion, a sporting-goods rack as a
bookshelf, a gold bathtub).

Fix round after P5 (22 Oct 2026): the ``render_print`` check (``render_findings``: a brand logo or a text print a
run's render showed) and the committed catalogue's records of the P5 / P4b findings (the SMEG fridge, the chalk
board coffee table, three washing machines with a maker's logo and the fridge of the same mesh as the SMEG one)."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from wenart.assets import hssd as H
from wenart.assets.audit import checks as CK
from wenart.assets.audit import decide as D
from wenart.assets.audit import demands as DM
from wenart.assets.audit import gaps as GP
from wenart.assets.audit import growth as GR
from wenart.assets.audit import growth_entries as GE
from wenart.assets.audit import growth_run as RUN
from wenart.assets.audit import keywords as K
from wenart.assets.audit import load_config
from wenart.assets.audit import write as W
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import sizes as SZ

ROOT = Path(__file__).resolve().parents[1]
LISTS = ROOT / "results" / "library" / "growth"
CFG = load_config()


# --------------------------------------------------------------------------
# Demands, size grid, coverage
# --------------------------------------------------------------------------

def test_drawn_demands_of_the_committed_buildings():
    dem = DM.drawn_demands()
    assert dem and all(set(d) >= {"type", "w", "d", "h", "count", "projects", "bin", "kind"} for d in dem)
    summary = DM.summary(dem)
    # the three projects' anchors and fixtures (docs/milestone13.md §1.3): tables to 3.0 x 1.0, wardrobe runs,
    # toilets and basins, the corner sofas; counts read on 15 Oct 2026
    assert summary["toilet"]["drawn"] == 28 and summary["washbasin"]["drawn"] == 20
    assert summary["table_dining"]["pieces"] == 18 and summary["wardrobe"]["pieces"] == 22
    assert summary["sofa_corner"]["drawn"] == 6 and summary["chair"]["drawn"] == 84
    assert summary["bathtub"]["projects"] == ["real02", "real03", "real04"]
    assert "unknown" not in summary and "kitchen_counter" not in summary and "stair" not in summary
    assert sum(d["count"] for d in dem) == 809 and len(dem) == 156
    # every drawn piece keeps its drawn size (1 cm); a type without a height in the building takes the product height
    big = next(d for d in dem if d["type"] == "table_dining" and d["w"] >= 3.3)
    assert big["d"] == 1.0 and big["drawn"] >= 2 and big["h_from"] == "type default"
    # a building path list works as well as the dict, decor may be left out
    only = DM.drawn_demands([DM.BUILDING_PATHS["real03"]], include_decor=False)
    assert all(d["projects"] == ["real03"] and d["kind"] == "furniture" for d in only)


def test_drawn_demands_read_the_m13_fields_and_skip_removed_pieces(tmp_path):
    b = {"furniture": [
        {"id": "a", "type": "chair", "drawn_type": "armchair", "drawn_footprint": [0.9, 0.9], "drawn_height": 0.8,
         "footprint": {"size": [0.5, 0.5]}, "source": "from_documents", "status": "verified"},
        {"id": "b", "type": "sofa", "footprint": {"size": [2.2, 0.9]}, "source": "from_documents",
         "status": "removed"},
        {"id": "c", "type": "sofa", "footprint": {"size": [2.204, 0.898]}, "source": "added_by_ai"},
        {"id": "d", "type": "sofa", "footprint": {"size": [2.2, 0.9]}, "source": "added_by_ai", "not_furniture": True},
        {"id": "e", "type": "unknown", "footprint": {"size": [6.0, 5.0]}, "source": "from_documents"},
    ], "decor": [{"id": "x", "type": "cushion", "size": [0.45, 0.15], "source": "added_by_ai"}]}
    path = tmp_path / "p1" / "building_final.json"
    path.parent.mkdir()
    path.write_text(json.dumps(b))
    dem = DM.drawn_demands({"p1": path})
    rows = {(d["type"], d["bin"]): d for d in dem}
    assert ("armchair", "0.90x0.90") in rows and rows[("armchair", "0.90x0.90")]["h"] == 0.8
    assert rows[("sofa", "2.20x0.90")]["count"] == 1 and rows[("sofa", "2.20x0.90")]["added"] == 1
    assert ("unknown", "6.00x5.00") not in rows and ("cushion", "0.45x0.15") in rows


def test_size_grid_bins_come_from_the_product_grid():
    dem = DM.drawn_demands()
    grid = DM.size_grid(dem)
    assert set(grid) == {d["type"] for d in dem}
    sofa = grid["sofa"]
    assert [b["bin"] for b in sofa] == [f"{r['w']:.2f}x{r['d']:.2f}" for r in SZ.PRODUCT_GRID["sofa"]]
    assert sum(b["demand"] for b in sofa) == sum(d["count"] for d in dem if d["type"] == "sofa")
    # the 3.35 x 1.00 ten-seat table lands in the 3.00 x 1.00 bin of the grid, never in a 1.60 x 0.90 one
    table = next(b for b in grid["table_dining"] if b["bin"] == "3.00x1.00")
    assert table["demand"] >= 2 and any(s["w"] >= 3.3 for s in table["demanded_sizes"])
    assert DM.nearest_bin("sofa", 0.9, 2.2)["w"] == 2.2                      # either orientation
    # a type without a product grid gets a bin per demanded size
    toilet = grid["toilet"]
    assert any(b["demand"] for b in toilet) and all(b["from"] == "grid" for b in toilet)
    assert DM.size_grid([{"type": "no_such_type", "w": 1.0, "d": 0.5, "h": None, "count": 2, "projects": ["p"]}])[
        "no_such_type"][0]["from"] == "demand"


def test_covers_follows_the_fit_caps():
    assert DM.COVER["mean_scale"] == F.UNIFORM_RANGE and DM.COVER["non_uniform"] == F.NON_UNIFORM_CAP
    assert DM.covers([2.0, 0.9, 0.85], 2.0, 0.9, (0.55, 1.2))
    assert DM.covers([2.0, 0.9, 0.85], 2.2, 0.95, (0.55, 1.2))                # 10 % up, both axes
    assert not DM.covers([2.0, 0.9, 0.85], 2.6, 0.9, (0.55, 1.2))             # 30 % on one axis: non-uniform
    assert not DM.covers([2.0, 0.9, 0.85], 1.4, 0.63, (0.55, 1.2))            # mean scale 0.7
    assert not DM.covers([2.0, 0.9, 1.6], 2.0, 0.9, (0.55, 1.2))              # a 1.6 m tall sofa
    assert not DM.covers([0.0, 0.9, 0.8], 2.0, 0.9) and not DM.covers("x", 2.0, 0.9)


def test_coverage_per_mode_on_the_catalogue():
    dem = DM.drawn_demands()
    cat = C.load()
    com, rel = DM.coverage(cat, dem, "commercial"), DM.coverage(cat, dem, "relaxed")
    assert set(com) == set(rel) == set(DM.size_grid(dem))
    for t in com:
        for b, n in com[t].items():
            assert n <= rel[t][b]                                            # relaxed is a superset
    # the tool_nc fixtures count in relaxed mode only (D3): the washing machines
    assert com["washing_machine"]["0.60x0.60"] == 0 and rel["washing_machine"]["0.60x0.60"] >= 10
    ids = DM.coverage_ids(cat, dem, "relaxed")["sofa"]["2.20x0.90"]
    assert ids and all(C.usable(cat.entry(i), "relaxed") for i in ids)
    with pytest.raises(ValueError):
        DM.coverage(cat, dem, "free")


def test_demand_gaps_and_their_markdown():
    grid = {"toilet": [{"bin": "0.38x0.65", "w": 0.38, "d": 0.65, "h": 0.78, "label": "default product", "demand": 5,
                        "projects": ["real02"]},
                       {"bin": "0.40x0.70", "w": 0.4, "d": 0.7, "h": 0.78, "label": "", "demand": 0, "projects": []}],
            "sofa": [{"bin": "2.00x0.90", "w": 2.0, "d": 0.9, "h": 0.85, "label": "3-seat", "demand": 3,
                      "projects": ["real03"]}]}
    cov = {"commercial": {"toilet": {"0.38x0.65": 0, "0.40x0.70": 0}, "sofa": {"2.00x0.90": 7}},
           "relaxed": {"toilet": {"0.38x0.65": 1, "0.40x0.70": 0}, "sofa": {"2.00x0.90": 9}}}
    rows = DM.demand_gaps(grid, cov)
    assert [r["bin"] for r in rows] == ["0.38x0.65"]                         # demanded and below 2 in a mode
    r = rows[0]
    assert r["commercial"] == 0 and r["relaxed"] == 1 and r["gap_commercial"] == 2 and r["gap_relaxed"] == 1
    assert any("hssd" in s for s in r["sources"])
    md = GP.demand_gaps_markdown(rows, "Gaps", "note")
    assert "| toilet | 0.38x0.65 | 5 | real02 | **0** | **1** |" in md and "1 gap row(s) over 1 type(s)" in md
    assert "(none)" in GP.demand_gaps_markdown([], "Gaps")


def test_the_committed_demand_files_match_the_code():
    dem = json.loads((LISTS / "demands.json").read_text(encoding="utf-8"))
    assert dem["pieces"] == sum(d["count"] for d in DM.drawn_demands()) == 809
    # the committed file names the buildings relative to the repo (no path of one machine; review of 15 Oct 2026)
    assert dem["buildings"] == {p: f"results/furniture/{p}/building_final.json" for p in DM.PROJECTS}
    assert dem["demands"] == DM.drawn_demands()
    cov = json.loads((LISTS / "coverage.json").read_text(encoding="utf-8"))
    assert cov["bins_demanded"] == 90 and cov["min_models_per_bin"] == 2
    assert cov["bins_covered"]["relaxed"] >= cov["bins_covered"]["commercial"]
    assert cov["pick_plan"]["hssd"]["picked"] == 874 and 600 <= cov["pick_plan"]["hssd"]["picked"] <= 900
    assert 400 <= cov["pick_plan"]["abo"]["picked"] <= 600
    assert (LISTS / "gaps_demand.md").read_text(encoding="utf-8").startswith("# Library gaps by drawn demand")


# --------------------------------------------------------------------------
# HSSD: metadata rows, candidates, entries, gate and download (no network)
# --------------------------------------------------------------------------

def hssd_row(hid, name, synset, dims, found="living room", multi="false", art="False"):
    return {"id": hid, "name": name, "wnsynsetkey": synset, "up": "", "front": "", "foundIn": found,
            "hasMultipleObjects": multi, "support": "", "dims": "", "aligned.dims": ",".join(str(v) for v in dims),
            "simClusterIds": "", "decomposedFrom": "", "decomposedInto": "", "floorplanner-category-tags": "Sofas",
            "isArticulatable": art, "main_wnsynsetkey": synset, "main_category": "", "super_category": "",
            "notes": ""}


FAKE = [
    hssd_row("a" * 40, "Taylor 76'' Upholstered Sofa", "sofa.n.01", (1.96, 0.86, 0.92)),          # x, y (up), z
    hssd_row("b" * 40, "Big sectional", "l-shaped_couch.n.01", (3.2, 0.9, 2.0), multi="true"),
    hssd_row("c" * 40, "Andaman Queen Bed", "double_bed.n.01", (1.76, 1.2, 2.3), found="bedroom"),
    hssd_row("d" * 40, "Single bed", "bed.n.01", (1.0, 0.9, 2.05), found="bedroom"),
    hssd_row("e" * 40, "Catalina Outdoor sofa", "sofa.n.01", (2.12, 0.77, 0.9), found="patio"),
    hssd_row("f" * 40, "Kitchen sink", "sink.n.01", (0.6, 0.2, 0.5), found="kitchen"),
    hssd_row("0" * 40, "Vanity basin", "sink_cabinet.n.01", (0.8, 0.85, 0.5), found="bathroom"),
    hssd_row("1" * 40, "Toilet", "toilet.n.02", (0.38, 0.8, 0.65), found="bathroom"),
    hssd_row("2" * 40, "Side table", "table.n.02", (0.5, 0.55, 0.5)),
    hssd_row("9" * 40, "Coffee table", "table.n.02", (1.1, 0.42, 0.6)),
    hssd_row("3" * 40, "Dining table", "table.n.02", (1.8, 0.75, 0.9)),
    hssd_row("4" * 40, "Throw pillow", "throw_pillow.n.01", (0.45, 0.45, 0.15)),
    hssd_row("5" * 40, "Door", "door.n.01", (0.9, 2.1, 0.05)),                                         # no type
    hssd_row("6" * 40, "Broken", "sofa.n.01", (0, 0.9, 0.9)),                                          # no size
    hssd_row("7" * 40, "Tall cabinet", "cabinet.n.01", (0.6, 1.9, 0.4)),
    hssd_row("8" * 40, "Low cabinet", "cabinet.n.01", (0.6, 0.8, 0.4)),
]


def test_hssd_rows_are_typed_from_the_synset_with_the_size_rules():
    typed = {t["id"][0]: t for t in H.typed_rows(FAKE)}
    assert typed["a"]["type"] == "sofa" and typed["a"]["w"] == 1.96 and typed["a"]["h"] == 0.86 \
        and typed["a"]["d"] == 0.92
    assert typed["b"]["type"] == "sofa_corner" and typed["b"]["multi"] is True
    assert typed["c"]["type"] == "bed_double" and typed["d"]["type"] == "bed_single"
    assert typed["e"]["outdoor"] is True
    assert typed["f"]["type"] == "sink_kitchen" and typed["0"]["type"] == "washbasin" and typed["1"]["type"] == "toilet"
    assert typed["2"]["type"] == "side_table" and typed["3"]["type"] == "table_dining" \
        and typed["9"]["type"] == "table_coffee"
    assert typed["4"]["type"] == "cushion" and typed["4"]["kind"] == "decor"
    assert typed["7"]["type"] == "tall_cabinet"
    assert "5" not in typed and "6" not in typed and "8" not in typed
    for t in typed.values():
        assert t["type"] in C.FURNITURE_TYPES or t["type"] in C.DECOR_TYPES
    for synset, mapped in H.SYNSET_TYPES.items():
        assert mapped.endswith("*") or mapped in C.FURNITURE_TYPES or mapped in C.DECOR_TYPES, synset


def test_hssd_candidates_on_a_small_fake_table():
    dem = [{"type": "sofa", "w": 2.0, "d": 0.9, "h": None, "count": 4, "projects": ["real02"]},
           {"type": "bed_double", "w": 1.8, "d": 2.0, "h": None, "count": 2, "projects": ["real03"]},
           {"type": "toilet", "w": 0.4, "d": 0.7, "h": None, "count": 3, "projects": ["real04"]},
           {"type": "cushion", "w": 0.45, "d": 0.15, "h": None, "count": 10, "projects": ["real02"]}]
    ids = H.hssd_candidates(dem, 5, FAKE)
    assert ids == sorted(ids, key=lambda i: ids.index(i)) and all(i.startswith("hssd_") for i in ids)
    recs = {r["id"]: r for r in H.candidate_records(dem, 5, FAKE)}
    assert "hssd_" + "a" * 40 in recs and "hssd_" + "e" * 40 not in recs      # the patio sofa is left out
    assert "hssd_" + "c" * 40 in recs and recs["hssd_" + "c" * 40]["bin"] == "1.80x2.00"
    assert "hssd_" + "1" * 40 in recs and recs["hssd_" + "1" * 40]["kind"] == "furniture"
    assert "hssd_" + "4" * 40 in recs and recs["hssd_" + "4" * 40]["kind"] == "decor"
    a = recs["hssd_" + "a" * 40]
    assert a["licence"] == "CC-BY-NC-4.0" and a["licence_flag"] == "non_commercial" and a["fits_caps"] is True
    assert a["path"] == f"objects/a/{'a' * 40}.glb" and a["dims_m"] == [1.96, 0.92, 0.86]
    # a model already in the library is not listed again; n_per_bin caps the picks per bin
    assert "hssd_" + "a" * 40 not in H.hssd_candidates(dem, 5, FAKE, used_ids=["hssd_" + "a" * 40])
    assert len([r for r in H.candidate_records(dem, 1, FAKE) if r["type"] == "sofa"]) == 1
    # the listing (ids of the hssd-models repo) and the sizes flow into the records
    recs2 = H.candidate_records(dem, 5, FAKE, listing={"a" * 40: f"objects/a/{'a' * 40}.glb"},
                                sizes={"a" * 40: 2_500_000})
    assert [r["id"] for r in recs2] == ["hssd_" + "a" * 40] and recs2[0]["size_mb"] == 2.5
    doc = H.list_doc(recs2, dem, "2026-10-15T00:00:00Z", 5)
    assert doc["source"] == "hssd" and doc["licences"] == ["CC-BY-NC-4.0"] and doc["picked_size_mb"] == 2.5
    assert doc["query"]["revision"] == H.REVISION and doc["gated"]["prompt"] == H.GATED_PROMPT


def test_hssd_object_paths_and_the_layout_facts():
    assert H.object_path("0001fb06b075a743e6289236cf049df3ad5dfa9c") == \
        "objects/0/0001fb06b075a743e6289236cf049df3ad5dfa9c.glb"
    assert H.object_path("xxxx9a19f571x1dc0x45c3x99fdxbf82a1abcb7f") == \
        "objects/x/xxxx9a19f571x1dc0x45c3x99fdxbf82a1abcb7f.glb"
    assert H.object_path("200-19") == "objects/openings/200-19.glb"
    assert H.object_path("abc", {"abc": "objects/a/abc.glb"}) == "objects/a/abc.glb"
    assert H.allow_pattern("abc") == "objects/*/abc.glb"
    assert H.resolve_url("README.md") == f"https://huggingface.co/datasets/hssd/hssd-models/resolve/{H.REVISION}/README.md"
    assert H.FILE_SIZE_MB["count"] == 14267 and H.FILE_SIZE_MB["median"] == 1.65 and H.FILE_SIZE_MB["total_gb"] == 38.45


def test_hssd_entry_fields_and_the_entry(tmp_path):
    fields = H.entry_fields()
    assert fields == {"licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial", "licence_declared_by": "publisher",
                      "licence_url": "https://huggingface.co/datasets/hssd/hssd-models", "commercial_safe": False}
    assert C.licence_flag_of(dict(fields, source="hssd")) == "non_commercial"
    assert not C.usable(dict(fields, source="hssd"), "commercial") and C.usable(dict(fields, source="hssd"), "relaxed")
    cand = next(r for r in H.candidate_records([{"type": "sofa", "w": 2.0, "d": 0.9, "h": None, "count": 1,
                                                 "projects": ["real02"]}], 1, FAKE))
    m = {"bbox_model_m": [1.96, 0.92, 0.86], "bbox_min_m": [-0.98, -0.46, 0.0], "bbox_max_m": [0.98, 0.46, 0.86],
         "triangles": 12000, "vertices": 7000, "info": {"textured": True, "vertex_colours": False},
         "stats": None, "pbr": {"base_colour": True, "metallic_roughness": True, "normal": False, "occlusion": False,
                                "emissive": False, "materials": 2, "images": 2}}
    e = GE.hssd_entry(cand, m, "0" * 64, "2026-10-15T00:00:00Z", pbr=m["pbr"])
    assert e["id"] == cand["id"] and e["source"] == "hssd" and e["type"] == "sofa" and e["kind"] == "furniture"
    for k, v in fields.items():
        assert e[k] == v
    assert e["units_known"] is True and e["glb"] == f"models/hssd/{e['id']}.glb" and e["sha256_glb"] == "0" * 64
    assert "CC BY-NC 4.0" in e["attribution"] and "HSSD" in e["attribution"] and "2306.11290" in e["attribution"]
    assert e["pbr_maps"]["base_colour"] is True and e["audit"]["status"] == "pending"
    assert e["hssd"]["id"] == "a" * 40 and e["hssd"]["revision"] == H.REVISION and e["growth"]["milestone"] == "m13"
    # the Hub's file page is /blob/<revision>/<path> (review of 15 Oct 2026: /tree/ answers 404 for a file)
    assert e["source_url"] == f"{H.PAGE_URL}/blob/{H.REVISION}/objects/a/{'a' * 40}.glb"
    assert "p2_m13" not in GE.GROWTH_NOTE_M13 and "results/library/audit/p4/" in GE.GROWTH_NOTE_M13
    assert all(k in e for k in C.CC_BY_FIELDS)
    if "hssd" in C.SOURCES:                        # the lead adds the source to catalog.py (track T7 report)
        C.validate({"entries": [e]}, complete=False)
    assert "hssd" in H.DATASET["name"].lower() and H.DATASET["licence"] == "CC-BY-NC-4.0"


def test_hssd_gate_check_and_download_never_see_the_token(tmp_path, capsys):
    secret = "hf_not_a_real_token_123"
    env = {"HF_TOKEN": secret}
    assert H.gate_check(None)["ok"] is False and "no HF_TOKEN" in H.gate_check(None)["reason"]
    seen = []

    def head(url, token):
        seen.append((url, token))
        return 403
    g = H.gate_check(secret, head=head)
    assert g["ok"] is False and g["status"] == 403 and "not accepted the terms" in g["reason"]
    assert seen[0][1] == secret and seen[0][0].startswith("https://huggingface.co/datasets/hssd/hssd-models/resolve/")
    assert H.gate_check(secret, head=lambda u, t: 401)["status"] == 401
    assert H.gate_check(secret, head=lambda u, t: 302)["ok"] is True
    ids = ["hssd_" + "a" * 40, "b" * 40]
    # no token: skipped, nothing fetched
    rec = H.download(ids, tmp_path / "no", env={}, head=lambda u, t: 200, fetch=lambda *a: pytest.fail("fetched"))
    assert rec["skipped"] is True and rec["token_set"] is False and rec["ok"] == [] and secret not in json.dumps(rec)
    # the gate says 403: skipped with the clear reason, nothing fetched
    rec = H.download(ids, tmp_path / "gated", env=env, head=lambda u, t: 403, fetch=lambda *a: pytest.fail("fetched"))
    assert rec["skipped"] is True and rec["gate"]["status"] == 403 and "skipped" in capsys.readouterr().out
    assert secret not in json.dumps(rec)

    # accepted: the per-file fetcher writes the files into the repo layout, a second run keeps them
    def fetch(url, dest, token):
        assert token == secret and "/resolve/" + H.REVISION + "/objects/" in url
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_bytes(b"glb" * 10)
        return dest
    rec = H.download(ids, tmp_path / "ok", env=env, head=lambda u, t: 200, fetch=fetch)
    assert rec["ok"] == ["a" * 40, "b" * 40] and rec["missing"] == [] and rec["bytes"] == 60
    assert (tmp_path / "ok" / "objects" / "a" / ("a" * 40 + ".glb")).is_file()
    rec2 = H.download(ids, tmp_path / "ok", env=env, head=lambda u, t: pytest.fail("no gate call when present"),
                      fetch=lambda *a: pytest.fail("fetched twice"))
    assert rec2["kept"] == 2 and rec2["ok"] == rec["ok"] and rec2["gate"] is None
    # the snapshot path (huggingface_hub) is used when given; its errors are recorded without the token
    calls = []

    def snapshot(todo, dest, token, revision, workers):
        calls.append((list(todo), revision, workers))
        raise RuntimeError(f"boom {token}")
    rec3 = H.download(["c" * 40], tmp_path / "snap", env=env, head=lambda u, t: 200, snapshot=snapshot)
    assert calls == [(["c" * 40], H.REVISION, 8)] and rec3["error"] == "RuntimeError: boom <token>"
    assert secret not in json.dumps(rec3)


def test_the_committed_hssd_list_and_its_approval():
    doc = json.loads((LISTS / "candidates_hssd.json").read_text(encoding="utf-8"))
    assert doc["source"] == "hssd" and doc["licences"] == ["CC-BY-NC-4.0"] and doc["licence_flag"] == "non_commercial"
    assert 600 <= doc["picked"] <= 900 and doc["query"]["revision"] == H.REVISION
    cands = doc["candidates"]
    assert len(cands) == doc["count"] and len({c["id"] for c in cands}) == len(cands)
    types = {c["type"] for c in cands}
    for t in ("toilet", "washbasin", "bathtub", "shower", "sink_kitchen", "stove", "fridge", "table_dining",
              "wardrobe", "sofa_corner", "bed_double"):
        assert t in types, t
    assert all(c["id"] == "hssd_" + c["hssd_id"] and c["path"].startswith("objects/") for c in cands)
    assert all(c["off"] <= H.MAX_OFF + 1e-9 and c["licence"] == "CC-BY-NC-4.0" for c in cands)
    assert sum(1 for c in cands if c["fits_caps"]) >= 0.7 * len(cands)
    assert doc["picked_size_mb"] < 4000 and doc["size_known"] == len(cands)      # no empty GLB is picked
    approved = GR.approved("hssd")
    assert approved["ids"] == [c["id"] for c in cands][:900] and approved["ids_from"] == "candidates_hssd.json"
    assert "D2" in approved["approved_by"]


# --------------------------------------------------------------------------
# The growth lists: ABO by size grid, Poly Haven vegetation at 2K, ambientCG sets
# --------------------------------------------------------------------------

def test_abo_candidates_take_the_size_grid_group():
    models = {"M1": {"extents": [2.0, 0.85, 0.9], "path": "1/M1.glb", "image_width_max": 2048},
              "M2": {"extents": [0.5, 0.9, 0.55], "path": "2/M2.glb", "image_width_max": 1024},
              "M3": {"extents": [3.6, 0.9, 1.1], "path": "3/M3.glb", "image_width_max": 1024}}
    listings = [{"3dmodel_id": "M1", "item_id": "I1", "product_type": [{"value": "SOFA"}],
                 "item_name": [{"language_tag": "en_US", "value": "Rivet Modern Sofa"}], "style": []},
                {"3dmodel_id": "M2", "item_id": "I2", "product_type": [{"value": "CHAIR"}],
                 "item_name": [{"language_tag": "en_US", "value": "Dining Chair"}], "style": []},
                {"3dmodel_id": "M3", "item_id": "I3", "product_type": [{"value": "SOFA"}],
                 "item_name": [{"language_tag": "en_US", "value": "Huge Sofa"}], "style": []}]
    sizes = {"3dmodels/original/1/M1.glb": 20e6, "3dmodels/original/2/M2.glb": 5e6, "3dmodels/original/3/M3.glb": 9e6}
    assert GR.abo_candidates(models, listings, sizes, set()) == []            # no style, no decor: nothing (M12)
    bins = DM.size_grid([{"type": "sofa", "w": 2.0, "d": 0.9, "h": None, "count": 3, "projects": ["real02"]},
                         {"type": "chair", "w": 0.5, "d": 0.5, "h": None, "count": 2, "projects": ["real02"]}])
    out = GR.abo_candidates(models, listings, sizes, set(), demand_bins=bins, per_bin=6)
    by = {c["id"]: c for c in out}
    assert by["abo_M1"]["group"] == "size grid" and by["abo_M1"]["bin"] == "2.00x0.90" and by["abo_M1"]["pick"]
    assert by["abo_M1"]["fits_caps"] is True and by["abo_M2"]["group"] == "size grid"
    assert "abo_M3" not in by                                                 # 80 % over every demanded bin
    assert GR.demand_bin_of("sofa", [2.3, 0.95, 0.85], bins)["bin"] == "2.00x0.90"   # the demanded bin only
    assert GR.demand_bin_of("sofa", [3.6, 0.9, 1.1], bins) is None
    assert len([c for c in GR.abo_candidates(models, listings, sizes, set(), demand_bins=bins, per_bin=1)
                if c["pick"] and c["type"] == "sofa"]) == 1


def test_polyhaven_vegetation_and_ambientcg_sets():
    assets = {"jacaranda_tree": {"type": 2, "name": "Jacaranda Tree", "categories": ["nature", "plants", "trees"],
                                 "dimensions": [24169, 18028, 19829], "polycount": 312356},
              "dead_tree_trunk_02": {"type": 2, "name": "Dead Tree Trunk 02", "categories": ["nature", "trees"],
                                     "dimensions": [4053, 1056, 1055], "polycount": 155864},
              "quiver_tree_02": {"type": 2, "name": "Quiver Tree 02", "categories": ["trees"],
                                 "dimensions": [872, 880, 1468], "polycount": 153887},
              "grass_medium_02": {"type": 2, "name": "Grass Medium 02", "categories": ["plants", "grass"],
                                  "dimensions": [1500, 1500, 1448]},
              "garden_hose_wall_mounted_01": {"type": 2, "name": "Garden Hose", "categories": ["plants"],
                                              "dimensions": [500, 300, 557]},
              "ArmChair_01": {"type": 2, "name": "Arm Chair 01", "categories": ["furniture", "seating"],
                              "dimensions": [848, 766, 1065]}}
    files = {"gltf": {"2k": {"gltf": {"size": 9526, "include": {"a.bin": {"size": 208_307_808}}}}}}
    veg = GR.polyhaven_vegetation(assets, {"armchair_01"}, lambda aid: files, res="2k")
    by = {v["id"]: v for v in veg}
    assert set(by) == {"jacaranda_tree", "dead_tree_trunk_02", "quiver_tree_02", "grass_medium_02",
                       "garden_hose_wall_mounted_01"}
    assert by["jacaranda_tree"]["type"] == "tree" and by["jacaranda_tree"]["height_m"] == 19.829 \
        and by["jacaranda_tree"]["pick"] and by["jacaranda_tree"]["size_mb"] == 208.32
    assert by["quiver_tree_02"]["type"] == "shrub"                           # below 1.5 m: a shrub
    assert by["grass_medium_02"]["type"] == "grass" and by["grass_medium_02"]["kind"] == "vegetation"
    assert not by["dead_tree_trunk_02"]["pick"] and not by["garden_hose_wall_mounted_01"]["pick"]
    assert [c for c, _k in GR.PH_VEGETATION_CATEGORIES] == ["trees", "grass", "ground cover", "potted plants",
                                                            "plants"]
    infos = {"Metal032": {"assetId": "Metal032", "displayName": "Metal 032", "displayCategory": "Metal",
                          "dimensionX": 0, "dimensionY": 0, "maps": ["color", "normal", "roughness", "metalness"],
                          "tags": ["metal"], "downloadFolders": {"default": {"downloadFiletypeCategories": {"zip": {
                              "downloads": [{"attribute": "2K-JPG", "fileName": "Metal032_2K-JPG.zip",
                                             "size": 13_040_000, "downloadLink": "https://ambientcg.com/get?file=x"}]
                          }}}}}}
    sets = GR.ambientcg_sets(infos, {"Metal032"})
    by = {s["id"]: s for s in sets}
    assert by["Metal032"]["exists"] and by["Metal032"]["used"] and not by["Metal032"]["pick"] \
        and by["Metal032"]["size_mb"] == 13.04 and by["Metal032"]["slot"] == "metal"
    assert by["Plaster001"]["exists"] is False and by["Plaster001"]["pick"] is False
    assert set(GR.AMBIENTCG_SHELL_SETS) == {"ceiling", "worktop", "front", "ceramic", "metal", "tile"}


def test_the_committed_m13_lists_and_approvals():
    abo = json.loads((LISTS / "candidates_abo_m13.json").read_text(encoding="utf-8"))
    groups = {}
    for c in abo["candidates"]:
        groups[c["group"]] = groups.get(c["group"], 0) + 1
    assert 400 <= abo["picked"] <= 600 and groups["size grid"] >= 300 and abo["licences"] == ["CC-BY-4.0"]
    assert all(c["bin"] for c in abo["candidates"] if c["group"] == "size grid")
    ph = json.loads((LISTS / "candidates_polyhaven_m13.json").read_text(encoding="utf-8"))
    veg = [c for c in ph["candidates"] if c["kind"] == "vegetation" and c["pick"]]
    assert ph["query"]["resolution"] == "2k glTF" and len(veg) >= 40
    for hero in ("island_tree_01", "island_tree_02", "island_tree_03", "jacaranda_tree", "fir_sapling_medium",
                 "searsia_lucida", "searsia_burchellii", "grass_medium_02", "grass_bermuda_01"):
        assert any(v["id"] == hero for v in veg), hero                    # the T6 hero models (vegetation.py)
    acg = json.loads((LISTS / "candidates_ambientcg.json").read_text(encoding="utf-8"))
    assert acg["licences"] == ["CC0"] and all(c["exists"] for c in acg["candidates"])
    assert {c["slot"] for c in acg["candidates"]} == {"ceiling", "worktop", "front", "ceramic", "metal", "tile"}
    for src, n_min in (("abo_m13", 400), ("polyhaven_m13", 40), ("ambientcg", 15)):
        doc = GR.approved(src)
        assert len(doc["ids"]) >= n_min and doc["ids_from"], src
    assert RUN.list_names("abo", True) == ("candidates_abo_m13.json", "abo_m13")
    assert RUN.list_names("hssd", True) == ("candidates_hssd.json", "hssd")
    assert RUN.list_names("polyhaven", False) == ("candidates_polyhaven.json", "polyhaven")


# --------------------------------------------------------------------------
# The audit gates
# --------------------------------------------------------------------------

def gate_item(**kw):
    base = {"id": "abo_g", "type": "sofa", "kind": "furniture", "source": "abo", "licence": "CC-BY-4.0",
            "title": "Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa", "bbox_m": [1.97, 0.83, 0.83],
            "units_known": True, "front_axis": "-Y", "front_axis_confidence": "high", "up_axis": "+Z",
            "bbox_min_m": [-0.985, -0.415, 0.0], "bbox_max_m": [0.985, 0.415, 0.83], "origin_offset": [0.0, 0.0, 0.0],
            "polycount": 20000, "quality": [4, 4], "licence_url": "u", "licence_declared_by": "publisher",
            "licence_flag": "none", "commercial_safe": True, "attribution": "a", "material_tags": ["fabric"]}
    base.update(kw)
    return base


def test_gate_known_units_for_anchors():
    assert CK.units_anchor_check(gate_item(), CFG)["status"] == "ok"
    r = CK.units_anchor_check(gate_item(units_known=False, unit_scale=0.01, source="objaverse"), CFG)
    assert r["status"] == "remove" and "known units" in r["reason"]
    assert CK.units_anchor_check(gate_item(type="side_table", units_known=False), CFG)["status"] == "skip"
    assert CK.units_anchor_check(gate_item(type="toilet", units_known=False, source="generated"), CFG)["status"] == \
        "remove"
    for t in ("bed_double", "sofa", "table_dining", "wardrobe", "fridge", "stove", "sink_kitchen", "toilet",
              "washbasin", "bathtub", "shower"):
        assert t in CFG["gates"]["known_units_anchor_types"], t
    d = D.decide(gate_item(units_known=False, source="objaverse"),
                 CK.item_checks(gate_item(units_known=False, source="objaverse"), CFG, {"sofa"}), None, None, CFG)
    assert d["status"] == "removed" and any("known units" in r for r in d["reasons"])


def test_gate_pbr_maps_recorded_and_the_writer():
    assert CK.pbr_check(gate_item(), CFG)[0]["status"] == "skip"
    maps = {"base_colour": True, "metallic_roughness": False, "normal": True, "occlusion": False, "emissive": False,
            "materials": 1, "images": 2}
    recs = CK.pbr_check(gate_item(), CFG, {"pbr": maps})
    assert [r["check"] for r in recs] == ["pbr", "pbr_record"] and recs[0]["status"] == "ok"
    assert "metallic_roughness" in recs[0]["reason"] and recs[1]["status"] == "fix"
    assert recs[1]["fix"]["pbr_maps"]["normal"] is True
    flat = CK.pbr_check(gate_item(), CFG, {"pbr": dict(maps, base_colour=False, normal=False)})
    assert flat[0]["status"] == "warn" and "flat material colours" in flat[0]["reason"]
    assert len(CK.pbr_check(gate_item(pbr_maps=maps), CFG)) == 1              # recorded already: no fix
    entry = {"id": "abo_g", "type": "sofa", "front_axis": "-Y", "bbox_m": [2, 0.9, 0.8], "bbox_model_m": [2, 0.9, 0.8]}
    new, before = W.fix_entry(entry, {"pbr_maps": maps, "chaise_side": "left"})
    assert entry["pbr_maps"] == maps and entry["chaise_side"] == "left" and "M13 audit" in entry["chaise_note"]
    assert new == {"pbr_maps": maps, "chaise_side": "left"} and before == {}


def test_gate_material_tags_chaise_and_licence_fields():
    assert CK.material_tags_check(gate_item(), CFG)["status"] == "ok"
    r = CK.material_tags_check(gate_item(material_tags=None), CFG)
    assert r["status"] == "review" and "materials" in r["reason"]
    it = gate_item(material_tags=None)
    checks = CK.item_checks(it, CFG, {"sofa"})
    assert D.decide(it, checks, None, None, CFG)["status"] == "pending"
    yes = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
           "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
           "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": True, "contact": None}
    d = D.decide(it, checks, dict(yes, materials=["fabric", "metal", "other"]), None, CFG)
    assert d["status"] == "keep" and d["flags"]["material_tags"] == ["metal", "fabric"]
    d_old = D.decide(it, checks, yes, None, CFG)                              # an m12.1 answer: a note, no pending
    assert d_old["status"] == "keep" and "material_tags" not in d_old["flags"] and any("m12.1" in n for n in
                                                                                         d_old["notes"])
    assert D.material_tags_of(None) is None and D.material_tags_of({"materials": ["glass"]}) == ["glass"]
    # review (15 Oct 2026): an answer naming none of the design words writes an empty list, never "other": the
    # catalogue's enum (catalog.MATERIAL_TAGS) is what catalog.validate and the write step accept
    assert D.MATERIAL_TAGS == C.MATERIAL_TAGS
    d_other = D.decide(it, checks, dict(yes, materials=["leather", "other"]), None, CFG)
    assert d_other["status"] == "keep" and d_other["flags"]["material_tags"] == [] \
        and any("leather" in n for n in d_other["notes"])
    doc_other = {"entries": [{"id": "abo_o", "type": "sofa", "front_axis": "-Y", "bbox_m": [2, 0.9, 0.8],
                              "bbox_model_m": [2, 0.9, 0.8], "source": "abo", "licence": "CC-BY-4.0",
                              "title": "t", "author": "a", "source_url": "u", "licence_url": "l", "via": "v",
                              "attribution": "x", "units_known": True, "glb": "models/abo/abo_o.glb",
                              "sha256_glb": "0" * 64, "kind": "furniture", "polycount": 10}]}
    W.apply_decisions(doc_other, {"abo_o": d_other}, "2026-10-15T00:00:00Z")
    assert doc_other["entries"][0]["material_tags"] == []
    C._validate_m10_fields(doc_other["entries"][0])
    doc = {"entries": [{"id": "abo_g", "type": "sofa", "front_axis": "-Y", "bbox_m": [2, 0.9, 0.8]},
                       {"id": "abo_h", "type": "sofa", "front_axis": "-Y", "bbox_m": [2, 0.9, 0.8],
                        "material_tags": ["wood"]}]}
    W.apply_decisions(doc, {"abo_g": d, "abo_h": d}, "2026-10-15T00:00:00Z")
    assert doc["entries"][0]["material_tags"] == ["metal", "fabric"] and doc["entries"][1]["material_tags"] == ["wood"]
    # chaise side
    assert CK.chaise_check(gate_item(), CFG)["status"] == "skip"
    assert CK.chaise_check(gate_item(type="sofa_corner", chaise_side="left"), CFG)["status"] == "ok"
    assert CK.chaise_check(gate_item(type="sofa_corner"), CFG)["status"] == "warn"
    assert CK.chaise_check(gate_item(type="sofa_corner"), CFG, {"chaise_side": "right"})["fix"] == {
        "chaise_side": "right"}
    # licence fields
    assert CK.licence_fields_check(gate_item(), CFG)["status"] == "ok"
    r = CK.licence_fields_check(gate_item(attribution=""), CFG)
    assert r["status"] == "warn" and r["metrics"]["missing"] == ["attribution"]
    # an NC licence is not removed any more (relaxed mode); ND is
    assert CK.licence_check(gate_item(licence="CC-BY-NC-4.0", licence_flag="non_commercial",
                                      source="hssd"))["status"] == "ok"
    assert CK.licence_check(gate_item(licence="CC-BY-ND-4.0", licence_flag="no_derivatives",
                                      source="objaverse"))["status"] == "remove"
    assert CFG["gates"]["vision_passes"] == 1


def test_ask_version_per_item_and_the_materials_schema():
    from wenart.assets.audit import ask as A
    cfg_ask = CFG["ask"]
    assert A.version_for(gate_item(), cfg_ask) == cfg_ask["version"] == "m12.1"
    assert A.version_for(gate_item(material_tags=None), cfg_ask) == cfg_ask["version_materials"] == "m13.1"
    assert "materials" not in A.schema("furniture")["properties"]
    assert A.with_materials("m13.1") and A.with_materials("m14") and not A.with_materials("m12.1") \
        and not A.with_materials("m2") and not A.with_materials(None)         # by number, not by string order
    s13 = A.schema("furniture", "m13.1")
    assert "materials" in s13["properties"] and "materials" in s13["required"]
    assert "- materials:" in A.prompt(gate_item(), [2, 0.9, 0.8], "m13.1") and \
        "- materials:" not in A.prompt(gate_item(), [2, 0.9, 0.8])
    yes = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
           "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
           "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": True, "contact": None}
    assert A.valid(yes, "furniture") and A.valid(dict(yes, materials=["wood"]), "furniture")
    assert not A.valid(dict(yes, materials=["kryptonite"]), "furniture")
    r1 = A.request_item(gate_item(), "s.jpg", "px", [2, 0.9, 0.8], "m12.1")
    r2 = A.request_item(gate_item(), "s.jpg", "px", [2, 0.9, 0.8], "m13.1")
    assert r1["input_sha256"] != r2["input_sha256"]


def test_glb_pbr_maps_are_read_from_the_gltf_json():
    from wenart.assets.audit import glbmesh as GM
    doc = {"materials": [{"pbrMetallicRoughness": {"baseColorTexture": {"index": 0},
                                                    "metallicRoughnessTexture": {"index": 1}},
                          "normalTexture": {"index": 2}},
                         {"pbrMetallicRoughness": {"baseColorFactor": [1, 0, 0, 1]}}],
           "images": [{"uri": "a.png"}, {"uri": "b.png"}, {"uri": "c.png"}]}
    m = GM.pbr_maps(doc)
    assert m["base_colour"] and m["metallic_roughness"] and m["normal"] and not m["occlusion"] and not m["emissive"]
    assert m["materials"] == 2 and m["materials_with_base_colour"] == 1 and m["images"] == 3
    assert GM.pbr_maps({})["base_colour"] is False and GM.PBR_MAPS[0] == "base_colour"


# --------------------------------------------------------------------------
# The growth job: steps, syntax, the speed plan
# --------------------------------------------------------------------------

def test_growth_job_syntax_and_steps():
    job = ROOT / "scripts" / "jobs" / "library_growth.sh"
    subprocess.run(["bash", "-n", str(job)], check=True)
    text = job.read_text(encoding="utf-8")
    for step in ("run_step demands gr demands", "run_step size-grid gr size-grid", "run_step speed-probe",
                 "start_bg ingest-hssd gr ingest --source hssd", "start_bg ingest-abo-m13 gr ingest --source abo --m13",
                 "start_bg ingest-polyhaven-m13 gr ingest --source polyhaven --m13",
                 "start_bg ingest-ambientcg gr ingest --source ambientcg", "run_step coverage gr size-grid",
                 "join_bg ingest-hssd"):
        assert step in text, step
    assert 'if [ -n "${HF_TOKEN:-}" ]; then' in text and "SKIPPED: HF_TOKEN is not set" in text
    assert 'GROWTH_PH_SIZE="${GROWTH_PH_SIZE:-2k}"' in text and "--over-5-ok" in text
    assert "echo $HF_TOKEN" not in text and 'log "$HF_TOKEN' not in text
    assert set(RUN.M13_STEPS) <= set(RUN.STEPS) and RUN.M13_STEPS == ("demands", "size-grid", "speed-probe")
    assert "hssd" in RUN.parser().parse_args(["ingest", "--source", "hssd"]).source
    assert os.access(job, os.X_OK)


def test_plan_picks_from_the_measured_speed():
    cfg = {"hssd_target": [600, 900], "abo_target": [400, 600],
           "speed_probe": {"budget_minutes": 60, "min_mb_s": 2.0}}
    fast = RUN.plan_picks(99.0, cfg, {"hssd": 884, "abo": 562}, {"hssd": 2.7, "abo": 20.8})
    assert fast["fits_budget"] and fast["picks"]["hssd"]["take"] == 884 and fast["picks"]["abo"]["take"] == 562
    slow = RUN.plan_picks(1.0, cfg, {"hssd": 884, "abo": 562}, {"hssd": 2.7, "abo": 20.8})
    assert slow["slow"] and slow["picks"]["hssd"]["take"] == 600 and slow["picks"]["abo"]["take"] == 400
    # 3 MB/s for 60 min = 10.8 GB, the lists need 14.1 GB: the lower bounds of the targets
    tight = RUN.plan_picks(3.0, cfg, {"hssd": 884, "abo": 562}, {"hssd": 2.7, "abo": 20.8})
    assert not tight["slow"] and not tight["fits_budget"] and tight["picks"]["abo"]["take"] == 400 \
        and tight["picks"]["hssd"]["take"] == 600


def test_demands_and_size_grid_steps_write_their_files(tmp_path):
    from argparse import Namespace
    a = Namespace(growth=str(tmp_path / "g"), report=None, p4=str(tmp_path / "p4"), p3=str(tmp_path / "p3"),
                  assets=str(tmp_path / "assets"), lists=str(ROOT / "results" / "library"), checked_utc="2026-10-15T00:00:00Z",
                  m13=False)
    assert RUN.cmd_demands(a) == 0 and RUN.cmd_size_grid(a) == 0
    rep = tmp_path / "g" / "report"
    dem = json.loads((rep / "demands.json").read_text())
    cov = json.loads((rep / "coverage.json").read_text())
    # 91 bins since the integration of the fix round after P5 (was 90): the size table's new 0.90 x 0.80 m shower tray
    # is the nearest bin of real03's three 0.80 x 0.85 m showers (before: the 0.80 x 0.80 bin)
    assert dem["pieces"] == 809 and cov["bins_demanded"] == 91 and "before the growth" in cov["scope"]
    assert (rep / "gaps_demand.md").read_text().startswith("# Library gaps by drawn demand")
    assert cov["pick_plan"]["hssd"]["picked"] == 874


def test_growth_run_ingest_hssd_and_ambientcg_with_fakes(tmp_path, monkeypatch, capsys):
    from argparse import Namespace
    lists = tmp_path / "lists"
    (lists / "growth").mkdir(parents=True)
    hid_a, hid_b = "a" * 40, "b" * 40
    (lists / "growth" / "candidates_hssd.json").write_text(json.dumps({"candidates": [
        {"id": "hssd_" + hid_a, "hssd_id": hid_a, "path": f"objects/a/{hid_a}.glb", "type": "sofa", "pick": True},
        {"id": "hssd_" + hid_b, "hssd_id": hid_b, "path": f"objects/b/{hid_b}.glb", "type": "sofa", "pick": True}]}))
    (lists / "growth" / "approved_hssd.json").write_text(json.dumps(
        {"source": "hssd", "approved_by": "D2", "approved_utc": "2026-10-12T20:00:00Z",
         "picks": {"from": "candidates_hssd.json"}}))
    a = Namespace(growth=str(tmp_path / "g"), report=None, p4=str(tmp_path / "p4"), p3=str(tmp_path / "p3"),
                  assets=str(tmp_path / "assets"), lists=str(lists), source="hssd", workers=2, size="1k",
                  token_env="HF_TOKEN", m13=False, checked_utc=None)
    # no token in the environment: skipped with the reason, nothing copied, exit 1 (nothing done)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    assert RUN.cmd_ingest(a) == 1
    rec = json.loads((tmp_path / "g" / "report" / "ingest_hssd.json").read_text())
    assert rec["skipped"] is True and rec["ok"] == 0 and "SKIPPED" in capsys.readouterr().out
    assert not (tmp_path / "assets" / "models" / "hssd").exists()

    # a token and an accepted gate: the fake snapshot writes the repo layout; the files are copied to the cache
    monkeypatch.setenv("HF_TOKEN", "hf_fake_token_for_the_test")
    monkeypatch.setattr(H, "gate_check", lambda token, **kw: {"ok": True, "status": 200, "reason": "ok"})

    def snapshot(todo, dest, token, revision, workers):
        assert token == "hf_fake_token_for_the_test" and revision == H.REVISION
        for h in todo:
            p = Path(dest) / "objects" / h[0] / f"{h}.glb"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"glTF" + h.encode())
    monkeypatch.setattr(H, "_snapshot", snapshot)
    monkeypatch.setattr(H, "_hub_available", lambda: True)
    assert RUN.cmd_ingest(a) == 0
    rec = json.loads((tmp_path / "g" / "report" / "ingest_hssd.json").read_text())
    assert rec["ok"] == 2 and not rec["skipped"] and "hf_fake" not in json.dumps(rec)
    assert (tmp_path / "assets" / "models" / "hssd" / f"hssd_{hid_a}.glb").read_bytes() == b"glTF" + hid_a.encode()
    assert rec["records"][0]["glb"] == f"models/hssd/hssd_{hid_a}.glb" and rec["records"][0]["sha256"]
    # resume: present files kept, no gate call, no snapshot
    monkeypatch.setattr(H, "_snapshot", lambda *args: pytest.fail("fetched twice"))
    monkeypatch.setattr(H, "gate_check", lambda token, **kw: pytest.fail("gate asked although every file is present"))
    assert RUN.cmd_ingest(a) == 0
    rec = json.loads((tmp_path / "g" / "report" / "ingest_hssd.json").read_text())
    assert all(r.get("kept") for r in rec["records"]) and rec["download"]["kept"] == 2

    # ambientCG: the shell sets through fetch.fetch_texture (faked), present sets kept by the manifest
    (lists / "growth" / "candidates_ambientcg.json").write_text(json.dumps({"candidates": [
        {"id": "Plaster001", "slot": "ceiling", "pick": True}, {"id": "Metal032", "slot": "metal", "pick": False}]}))
    (lists / "growth" / "approved_ambientcg.json").write_text(json.dumps(
        {"source": "ambientcg", "approved_by": "D6", "approved_utc": "2026-10-12T20:00:00Z",
         "picks": {"from": "candidates_ambientcg.json"}}))
    got = []

    def fake_fetch(aid, out_dir, size="2k", source=None, licence=None):
        got.append((aid, size, source))
        return {"id": aid, "files": {"albedo": f"textures/{aid}/x.jpg"}, "sha256": {"albedo": "0" * 64}}
    from wenart.assets import fetch as F
    monkeypatch.setattr(F, "fetch_texture", fake_fetch)
    b = Namespace(**{**vars(a), "source": "ambientcg", "size": "2k"})
    assert RUN.cmd_ingest(b) == 0 and got == [("Plaster001", "2k", "ambientcg")]
    rec = json.loads((tmp_path / "g" / "report" / "ingest_ambientcg.json").read_text())
    assert rec["ok"] == 1 and rec["records"][0]["files"]["albedo"].startswith("textures/Plaster001/")


def test_ambientcg_ingest_retries_a_cut_api_answer_and_records_a_failure_only_after_the_retries(tmp_path, monkeypatch,
                                                                                                 capsys):
    """Pod P2 (docs/milestone13.md §14.6): two ambientCG API answers arrived cut (Metal051A at char 61440,
    Tiles074 at char 1122299) and the sets were recorded as failed at once. Now ``web.get_json`` asks again: a cut
    first answer for Metal051A is followed by the whole one (2 API tries, the set is fetched); Tiles074 cut 3 times
    is recorded as failed with the URL and 'try 3 of 3' (rc 1)."""
    import io
    import urllib.request
    import zipfile
    from argparse import Namespace
    from wenart.assets import web

    def record(aid):
        return {"assetId": aid, "dataType": "Material", "displayName": aid, "dimensionX": 100, "dimensionY": 100,
                "pad": "x" * 70000,
                "downloadFolders": {"default": {"downloadFiletypeCategories": {"zip": {"downloads": [
                    {"attribute": "2K-JPG", "downloadLink": f"https://ambientcg.com/get?file={aid}_2K-JPG.zip",
                     "fileName": f"{aid}_2K-JPG.zip", "size": 1000}]}}}}}

    def zipped(aid):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for suffix in ("Color", "NormalGL", "Roughness"):
                zf.writestr(f"{aid}_2K-JPG_{suffix}.jpg", b"jpg " + suffix.encode())
        return buf.getvalue()

    class Resp(io.BytesIO):
        def __init__(self, body, length):
            super().__init__(body)
            self.headers = {} if length is None else {"Content-Length": str(length)}
    calls = []

    def fake_urlopen(request, timeout=None):
        url = request.full_url
        calls.append(url)
        if "get?file=" in url:
            body = zipped(url.split("file=")[1].split("_")[0])
            return Resp(body, len(body))
        aid = url.split("id=")[1].split("&")[0]
        body = json.dumps({"foundAssets": [record(aid)]}).encode()
        first = sum(1 for c in calls if f"id={aid}&" in c) == 1
        if aid == "Tiles074" or first:
            return Resp(body[:61440], None)                           # cut, no Content-Length: no urllib error
        return Resp(body, len(body))
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(web, "BACKOFF_S", 0.0)
    lists = tmp_path / "lists"
    (lists / "growth").mkdir(parents=True)
    (lists / "growth" / "candidates_ambientcg.json").write_text(json.dumps({"candidates": [
        {"id": "Metal051A", "slot": "metal", "pick": True}, {"id": "Tiles074", "slot": "tiles", "pick": True}]}))
    (lists / "growth" / "approved_ambientcg.json").write_text(json.dumps(
        {"source": "ambientcg", "approved_by": "D6", "approved_utc": "2026-10-12T20:00:00Z",
         "picks": {"from": "candidates_ambientcg.json"}}))
    a = Namespace(growth=str(tmp_path / "g"), report=None, p4=str(tmp_path / "p4"), p3=str(tmp_path / "p3"),
                  assets=str(tmp_path / "assets"), lists=str(lists), source="ambientcg", workers=1, size="2k",
                  token_env="HF_TOKEN", m13=False, checked_utc=None)
    assert RUN.cmd_ingest(a) == 1
    rec = json.loads((tmp_path / "g" / "report" / "ingest_ambientcg.json").read_text())
    by = {r["id"]: r for r in rec["records"]}
    assert by["Metal051A"]["ok"] and by["Metal051A"]["files"]["albedo"].startswith("textures/Metal051A/")
    assert sum(1 for c in calls if "id=Metal051A&" in c) == 2
    assert not by["Tiles074"]["ok"] and sum(1 for c in calls if "id=Tiles074&" in c) == web.TRIES == 3
    err = by["Tiles074"]["error"]
    assert err.startswith("IncompleteBody: https://ambientcg.com/api/v2/full_json?id=Tiles074") and "try 3 of 3" in err
    assert "growth ingest ambientcg: Tiles074 failed: IncompleteBody" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): brands, other uses and metal sanitary ware
# --------------------------------------------------------------------------

P3_REMOVED = {
    "hssd_50549dea6434f912fa0134d5ed43f35f164908a4": "disney",          # the CARS cushion of the real04 salon
    "hssd_071d7e49a3865750863d8086f18b2dd650d2287a": "disney",          # "Disneys Cars Cuddle Pillow"
    "objaverse_b08a7135cad84e0ca222a8cff075109b": "harry potter",
    "abo_B07L96X7MN": "sporting goods",                                 # the wire rack used as a bookshelf
    "hssd_df8abd46ef3dd6017f6863558381655f1510d275": "oro",             # the gold bathtub rendered as a mirror
    "hssd_9217adecf2924d759f38708b72d3bc1eb711406b": "copper",          # the same rule: "Holywell FS Bath, Copper"
    "gen_bathtub_industrial_3_154b1fde": "judged slot",                 # both judges: one metal slot, 100 %
}


def test_branded_and_other_use_titles_are_hard_flags():
    """P3: a Disney CARS cushion (keep) showed in the real04 living room and a "Sporting Goods" rack stood in as its
    bookshelf; the old keywords had neither category (this test fails on them)."""
    for title in ("Disney CARS Racer's Edge Cushion Cover - 45x45 cms", "Disneys Cars Cuddle Pillow",
                  "Harry Potter Books Stack", "Pokémon Pikachu Plush", "Star Wars Darth Vader Lamp"):
        assert "branded" in K.flags(title), title
    for title in ("AmazonBasics Classic Office Desk Computer Chair", "Frozen glass vase", "Toy cars storage box",
                  "Amazon Brand – Rivet Industrial Wood and Metal Round Dining Kitchen Table",
                  "Vintage cars wall art"):
        assert "branded" not in K.flags(title), title                 # no bare "cars" or "frozen"
    assert K.flags("AmazonBasics Sporting Goods Storage Organizer Shelf - Black") == {"other_use": ["sporting goods"]}
    assert K.flags("Heavy Duty Garage Shelving Unit")["other_use"] == ["garage shelving"]
    for title in ("AmazonBasics Foldable Metal Platform Bed Frame with Tool-Free Assembly", "Ball & Cast End Table",
                  "Amazon Brand – Stone & Beam Industrial Pallet Wood Coffee Table", "Hidden Home Office"):
        assert "other_use" not in K.flags(title), title
    assert set(CK.HARD_FLAGS) >= {"branded", "other_use"} and "§2.6" in CK.FLAG_TEXT["branded"]
    it = gate_item(id="hssd_x", type="cushion", kind="decor", source="hssd", title="Disneys Cars Cuddle Pillow",
                   bbox_m=[0.45, 0.15, 0.45])
    recs = [r for r in CK.item_checks(it, CFG, {"cushion"}) if r["check"] == "title_flag"]
    assert recs and recs[0]["status"] == "remove" and recs[0]["metrics"]["category"] == "branded"
    d = D.decide(it, CK.item_checks(it, CFG, {"cushion"}), None, None, CFG)
    assert d["status"] == "removed" and any("licensed brand" in r for r in d["reasons"])


def test_sanitary_ware_with_a_metal_main_material_is_removed():
    """P3: the HSSD bathtub "Regia Jolie ... oro" (gold) rendered as polished mirror metal in cam_r_L1_banyo_2; the
    old audit had no surface check (no record, this test fails). The title's finish word removes it unless a part or
    a non-metal body is named; the Milestone 10 slot judgement removes a metal main slot both judges agree on."""
    def tub(title, **kw):
        return gate_item(id="hssd_t", type="bathtub", source="hssd", title=title, bbox_m=[1.7, 0.75, 0.6], **kw)

    for title in ("Regia Jolie, free standing bathtub, art. 200820, oro", "Holywell FS Bath, Copper",
                  "Chrome plated slipper bath", "Polished brass roll top bath"):
        r = CK.sanitary_finish_check(tub(title))
        assert r["status"] == "remove" and "polished metal" in r["reason"], title
    for title in ("Holywell FS Bath, Steel", "Kaldewei CLASSIC DUO, 180 x 80 x 43 cm", "Stone Bath"):
        assert CK.sanitary_finish_check(tub(title))["status"] == "ok", title
    acrylic = CK.sanitary_finish_check(tub("Gold acrylic bath"))
    assert acrylic["status"] == "warn" and "acrylic body" in acrylic["reason"]
    basin = gate_item(id="hssd_b", type="washbasin", source="hssd", bbox_m=[0.8, 0.5, 0.85],
                      title="Sink Console with Haden Faucet Set - Satin Nickel finish Knobs &amp; Faucet")
    r = CK.sanitary_finish_check(basin)
    assert r["status"] == "warn" and r["metrics"]["part"] == ["faucet", "knob"]
    slot = {"index": 0, "material": "metal", "share": 1.0, "agreed": True}
    assert CK.sanitary_finish_check(tub("Generated industrial bathtub (3)", material_slots=[slot]))["status"] == "remove"
    assert CK.sanitary_finish_check(tub("Generated industrial bathtub (1)",
                                        material_slots=[dict(slot, agreed=False)]))["status"] == "warn"
    small = [dict(slot, share=0.2), {"index": 1, "material": "other", "share": 0.8, "agreed": True}]
    assert CK.sanitary_finish_check(tub("Bath", material_slots=small))["status"] == "ok"   # metal taps only
    lamp = gate_item(type="floor_lamp", title="Polished brass floor lamp")
    assert CK.sanitary_finish_check(lamp)["status"] == "skip"
    oro = tub("Regia Jolie, free standing bathtub, art. 200820, oro")
    assert "sanitary_finish" in [r["check"] for r in CK.item_checks(oro, CFG, {"bathtub"})]
    assert D.decide(oro, CK.item_checks(oro, CFG, {"bathtub"}), None, None, CFG)["status"] == "removed"


def test_the_committed_catalogue_keeps_the_p3_findings_out_of_the_fit():
    """The 3 branded entries, the sporting-goods rack and the gold bathtub of P3 (and the two other entries the same
    checks remove) carry audit status ``removed`` with the check's reason and the decision_sha decide() gives, so a
    later audit write is idempotent; none is usable in either licence mode. No other kept entry trips the new
    checks."""
    from wenart.assets.audit import items as I

    cat = C.load()
    doc = json.loads(I.LIBRARY_PATH.read_text(encoding="utf-8"))
    entries = {e["id"]: (e, s) for s in ("entries", "decor") for e in doc[s]}
    known = set(SZ.types()) | set(SZ.decor_types())
    for aid, word in P3_REMOVED.items():
        e, section = entries[aid]
        a = e["audit"]
        assert a["status"] == "removed" and any(word in r for r in a["reasons"]), aid
        assert not C.usable(cat.entry(aid), "relaxed") and not C.usable(cat.entry(aid), "commercial"), aid
        assert C.unusable_reason(cat.entry(aid), "relaxed").startswith("audit: removed"), aid
        assert any("fix round after P3" in n for n in a["notes"]), aid
        item = I.item_of(e, "library", section)
        d = D.decide(item, CK.item_checks(item, CFG, known), None, None, CFG)
        assert d["status"] == "removed" and a["decision_sha"] == W.decision_sha(d) and a["reasons"] == d["reasons"]
    new = ("branded", "other_use")
    for item in I.load_items():
        if (item.get("audit") or {}).get("status") not in ("keep", "fix"):
            continue
        recs = CK.item_checks(item, CFG, known)
        hit = [r for r in recs if r["status"] == "remove" and (r["check"] == "sanitary_finish" or (
            r["check"] == "title_flag" and r["metrics"]["category"] in new))]
        assert not hit, (item["id"], hit)


# --------------------------------------------------------------------------
# Fix round after P5 (22 Oct 2026): brand logos and text prints the run renders showed
# --------------------------------------------------------------------------

# id -> (finding, a word of its detail); the views are in each entry's render_findings
P5_REMOVED = {
    "hssd_404146070e071454f055cfe3be7811fcdcb7ddbd": ("brand_logo", "SMEG"),          # P5 cam_r_L-1_mutfak_3
    "hssd_9660ea4405f304d30c4610f676185305d0e03c8b": ("brand_logo", "SMEG"),          # FAB28XS6: the FAB28LV mesh
    "hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82": ("text_print", "GET SOME MILK"),  # the oyun coffee table
    "hssd_031024e00569909d466d87df9fead90355ba29e5": ("brand_logo", "SAMSUNG"),       # P4b cam_r_L0_banyo_4_2
    "hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0": ("brand_logo", "LG"),            # P4b cam_r_L0_giris_holu_1
    "hssd_856317b238f6a70ae6f0afffed1f6d5e3ab7b80c": ("brand_logo", "tpoint"),        # P4b cam_r_L0_banyo_3_1
}


def test_render_findings_remove_a_model_with_a_brand_logo_or_a_text_print():
    """P5: the SMEG logo on a fridge (cam_r_L-1_mutfak_3) and chalk lettering on a coffee table (oyun views) were
    audited keep: the audit had no check of what a render shows on a model (this test fails on that code). A record
    with its evidence (a run view, or the same mesh as such a model, on the same file) removes the model; one
    without evidence, of an unknown kind or of a republished file is a warning."""
    sha = "a" * 64
    seen = {"run": "P5", "project": "real04", "view": "cam_r_L-1_mutfak_3", "piece": "f_L-1_090"}
    logo = {"finding": "brand_logo", "detail": "the SMEG logo is readable on the door", "seen_in": seen,
            "sha256_glb": sha}

    def fridge(**kw):
        return gate_item(id="hssd_f", type="fridge", source="hssd", title="Smeg Fridge FAB28LV", sha256_glb=sha,
                         polycount=2542, vertices=4990, bbox_model_m=[0.5936, 0.696, 1.455],
                         bbox_m=[0.5936, 0.696, 1.455], **kw)

    assert CK.render_print_check(fridge())["status"] == "skip"
    r = CK.render_print_check(fridge(render_findings=[logo]))
    assert r["status"] == "remove" and r["metrics"]["findings"] == ["brand_logo"]
    assert "SMEG logo" in r["reason"] and "seen in P5 real04 cam_r_L-1_mutfak_3" in r["reason"]
    assert "§2.6" in r["reason"]
    assert "render_print" in [c["check"] for c in CK.item_checks(fridge(render_findings=[logo]), CFG, {"fridge"})]
    d = D.decide(fridge(render_findings=[logo]), CK.item_checks(fridge(render_findings=[logo]), CFG, {"fridge"}),
                 None, None, CFG)
    assert d["status"] == "removed" and d["reasons"] == [r["reason"]]
    table = gate_item(id="hssd_t", type="table_coffee", source="hssd", sha256_glb=sha, title="Chalk Board Coffee Table",
                      render_findings=[dict(logo, finding="text_print", detail="chalk lettering on the top")])
    r = CK.render_print_check(table)
    assert r["status"] == "remove" and "printed lettering" in r["reason"] and "no project style" in r["reason"]
    # no evidence, an unknown kind, another file, an empty detail: a warning (decide never removes on it)
    for bad, why in ((dict(logo, seen_in={"run": "P5"}), "no evidence"), (dict(logo, finding="ugly"), "unknown"),
                     (dict(logo, sha256_glb="b" * 64), "another file"), (dict(logo, detail=" "), "no detail"),
                     ("SMEG", "not a record")):
        r = CK.render_print_check(fridge(render_findings=[bad]))
        assert r["status"] == "warn" and why in r["reason"], (bad, r)
        d = D.decide(fridge(render_findings=[bad]), CK.item_checks(fridge(render_findings=[bad]), CFG, {"fridge"}),
                     None, None, CFG)
        assert d["status"] != "removed" and not any("brand name" in x for x in d["reasons"])
    # the same mesh as a model whose render shows the logo: faces, vertices and model box must all match
    twin = {"id": "hssd_seen", "polycount": 2542, "vertices": 4990, "bbox_model_m": [0.5936, 0.696, 1.455]}
    same = dict(logo, seen_in=None, same_mesh_as=twin)
    r = CK.render_print_check(fridge(render_findings=[same]))
    assert r["status"] == "remove" and "the same mesh as hssd_seen (2542 faces, 4990 vertices" in r["reason"]
    for key, value in (("vertices", 4991), ("polycount", 2900), ("bbox_model_m", [0.5936, 0.7534, 1.679]),
                       ("vertices", "many"), ("bbox_model_m", None)):
        r = CK.render_print_check(fridge(render_findings=[dict(same, same_mesh_as=dict(twin, **{key: value}))]))
        assert r["status"] == "warn" and "the mesh differs from hssd_seen" in r["reason"], key
    # one usable record is enough; the others are listed as not used
    r = CK.render_print_check(fridge(render_findings=[dict(logo, finding="ugly"), logo]))
    assert r["status"] == "remove" and r["metrics"]["not_used"] and r["metrics"]["findings"] == ["brand_logo"]
    # the audit's items carry the field from the catalogue entry
    from wenart.assets.audit import items as I
    assert "render_findings" in I.FIELDS


def test_the_committed_catalogue_keeps_the_p5_look_findings_out_of_the_fit():
    """The SMEG fridge (P5 cam_r_L-1_mutfak_3), the chalk board coffee table (P5 / P3 / P4a oyun views), the three
    washing machines whose maker's logo P4b showed and the fridge of the same mesh as the SMEG one carry audit status
    ``removed`` with the render_print reason and the decision_sha decide() gives (a later audit write is
    idempotent); none is usable in either licence mode. Every record names its evidence: a committed before | after
    sheet of the view (and, where the run folder is on this machine, the piece built with that model), or the twin
    model of the same mesh that is itself removed. No kept or fixed entry carries a finding that would remove it."""
    from wenart.assets.audit import items as I

    cat = C.load()
    doc = json.loads(I.LIBRARY_PATH.read_text(encoding="utf-8"))
    entries = {e["id"]: (e, s) for s in ("entries", "decor") for e in doc[s]}
    known = set(SZ.types()) | set(SZ.decor_types())
    for aid, (kind, word) in P5_REMOVED.items():
        e, section = entries[aid]
        a = e["audit"]
        assert a["status"] == "removed" and any(word in r and CK.RENDER_FINDINGS[kind] in r for r in a["reasons"]), aid
        assert not C.usable(cat.entry(aid), "relaxed") and not C.usable(cat.entry(aid), "commercial"), aid
        assert C.unusable_reason(cat.entry(aid), "relaxed").startswith("audit: removed"), aid
        assert any(n.startswith("fix round after P5 (22 Oct 2026): removed by the code audit's new check "
                                "(render_print)") for n in a["notes"]), aid
        item = I.item_of(e, "library", section)
        d = D.decide(item, CK.item_checks(item, CFG, known), None, None, CFG)
        assert d["status"] == "removed" and a["decision_sha"] == W.decision_sha(d) and a["reasons"] == d["reasons"]
        (f,) = e["render_findings"]
        assert f["finding"] == kind and f["sha256_glb"] == e["sha256_glb"]
        if f.get("seen_in"):
            seen = f["seen_in"]
            assert (ROOT / seen["sheet"]).is_file(), seen["sheet"]                  # committed evidence
            assert seen["sheet"].endswith(f"/{seen['view']}_before_after.jpg")
            run_dir = ROOT / seen["render"].split("/results/")[0]
            built = run_dir / "results" / "furniture" / seen["project"] / "building_final.json"
            if built.is_file():                                                     # the run folder is git-ignored
                pieces = {p["id"]: (p.get("asset") or {}).get("asset_id")
                          for p in json.loads(built.read_text(encoding="utf-8"))["furniture"]}
                assert pieces[seen["piece"]] == aid, (aid, seen)
        else:
            twin = entries[f["same_mesh_as"]["id"]][0]
            assert twin["id"] in P5_REMOVED and "seen_in" in twin["render_findings"][0]
            assert all(twin[k] == e[k] == f["same_mesh_as"][k] for k in CK.SAME_MESH_KEYS), aid
            assert twin["pbr_maps"]["images"] == e["pbr_maps"]["images"] == 0      # the logo is geometry
    for item in I.load_items():
        if (item.get("audit") or {}).get("status") in ("keep", "fix"):
            assert CK.render_print_check(item)["status"] in ("skip", "warn"), item["id"]
        elif item.get("render_findings"):
            assert item["id"] in P5_REMOVED, item["id"]
