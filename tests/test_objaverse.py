"""CPU tests of the Objaverse library steps (docs/milestone7.md §7, §11 O) on canned metadata.

No network, no Blender, no model server: a fake dataset mirror (``LocalHub``) holds canned LVIS annotations,
object paths, metadata shards and tiny GLBs; a fake Blender runner writes the measurements and views the real
Blender side would write; fake VLM clients give the judges' answers. Covered: survey filters (licence strings,
credit, face count, size, textures, ranking, <= 8 per type, the bed split cap), unit guess, the geometric front,
the accept rules (front agreement, style intersection, quality, mattress), the attribution line, the ODC-By notice,
the catalogue (validates and merges with catalog.json, GLB cache with sha256) and the report.
"""
import ast
import gzip
import json
import math
import re
import shutil
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart.assets import objaverse as OV
from wenart.furniture import catalog as C

CFG = OV.load_config()
CC_BY_LINE = ('"Oak Sofa" by Ann Author (https://sketchfab.com/3d-models/abc), CC BY 4.0 '
              '(https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); '
              'changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched')


# --------------------------------------------------------------------------
# Fake dataset
# --------------------------------------------------------------------------

def make_glb(path: Path, textured: bool = True, colours: bool = False, pad: int = 0) -> Path:
    """A minimal GLB 2.0: one triangle, optionally an image texture used by the material, optionally COLOR_0."""
    data = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0) + b"\0" * pad
    attrs = {"POSITION": 0}
    if colours:
        attrs["COLOR_0"] = 0
    material = ({"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}} if textured
                else {"pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1]}})
    doc = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(data)}],
           "bufferViews": [{"buffer": 0, "byteLength": 36}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
                          "min": [0, 0, 0], "max": [1, 1, 0]}],
           "meshes": [{"primitives": [{"attributes": attrs, "material": 0}]}], "materials": [material],
           "nodes": [{"mesh": 0}], "scenes": [{"nodes": [0]}], "scene": 0}
    if textured:
        doc["images"] = [{"mimeType": "image/png", "bufferView": 0}]
        doc["textures"] = [{"source": 0}]
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    data += b"\0" * (-len(data) % 4)
    total = 12 + 8 + len(js) + 8 + len(data)
    blob = (struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
            + struct.pack("<II", len(data), 0x004E4942) + data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return path


def write_gz(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wb") as fh:
        fh.write(json.dumps(obj).encode("utf-8"))


class Mirror:
    """A folder laid out like allenai/objaverse with canned records."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.lvis: dict[str, list[str]] = {}
        self.paths: dict[str, str] = {}
        self.meta: dict[str, dict] = {}
        self.n = 0

    def add(self, cats, licence="by", faces=10000, likes=0, views=0, size=None, user="Ann Author", name=None,
            url=True, textured=True, colours=False, glb=True, meta=True, path=True, shard="000-000", tags=()):
        self.n += 1
        uid = f"{self.n:032x}"
        for cat in ([cats] if isinstance(cats, str) else cats):
            self.lvis.setdefault(cat, []).append(uid)
        rel = f"glbs/{shard}/{uid}.glb"
        if path:
            self.paths[uid] = rel
        if meta:
            rec = {"uid": uid, "name": name or f"Model {self.n}", "license": licence, "likeCount": likes,
                   "viewCount": views, "user": {"displayName": user, "username": "ann" if user else ""},
                   "faceCount": faces, "archives": {"glb": {"faceCount": faces, "size": size or 100000,
                                                            "textureCount": 1 if textured else 0}},
                   "tags": [{"name": t} for t in tags]}
            if url:
                rec["viewerUrl"] = f"https://sketchfab.com/3d-models/{uid}"
            self.meta.setdefault(shard, {})[uid] = rec
        if glb:
            make_glb(self.root / rel, textured=textured, colours=colours)
        return uid

    def write(self) -> OV.LocalHub:
        write_gz(self.root / "lvis-annotations.json.gz", self.lvis)
        write_gz(self.root / "object-paths.json.gz", self.paths)
        for shard, recs in self.meta.items():
            write_gz(self.root / "metadata" / f"{shard}.json.gz", recs)
        return OV.LocalHub(self.root)


def quiet(*_args, **_kwargs):
    pass


# --------------------------------------------------------------------------
# Configuration and module shape
# --------------------------------------------------------------------------

def test_config_tables_follow_the_spec():
    pre = CFG["prefilter"]
    assert pre["face_count"] == [2000, 150000]
    assert pre["max_glb_mb"] == 40
    assert pre["per_type_limit"] == 24                      # docs/milestone8.md §2 (M7: 8)
    assert CFG["units"] == [1.0, 0.01, 0.0254, 0.001]
    assert CFG["dataset"]["revision"] == "21e4e142159e2153706c23a3a02e55cec5591cea"
    # docs/milestone9.md §1: 20 per type (decor 20), 5 per style family in the first pass, then the fill pass.
    assert CFG["accept"] == {"min_quality": 4, "per_type_max": 20, "decor_per_type_max": 20, "per_family_max": 5,
                             "style_fill": True, "source_order": ["abo", "polyhaven", "objaverse", "generated"]}
    # docs/milestone9.md §2.2: the fixture categories take flat-coloured models, a wider face count, 40 candidates.
    assert set(pre["overrides"]) == {"toilet", "sink", "bathtub", "refrigerator", "stove"}
    for spec in pre["overrides"].values():
        assert spec == {"face_count": [800, 400000], "allow_flat_colours": True, "per_type_limit": 40,
                        "max_downloads_per_type": 80}
    assert CFG["survey_files"] == OV.SURVEY_FILES and OV.CATALOG_NAME == "catalog_library.json"
    assert CFG["bed_frame"] == {"ray_offset": 0.2, "min_hits": 3, "deck_range_m": [0.08, 0.90]}
    table, _tol = OV.load_size_table()
    mapped = {t for spec in CFG["categories"].values() for t in spec["types"]}
    for t in mapped:
        assert t in C.FURNITURE_TYPES and t in CFG["types"] and t in table and t in OV.TYPE_WORDS
    for name in ("tv_unit", "kitchen_counter", "stair"):            # no LVIS category: parametric
        assert name not in mapped
    frontless = {t for t, spec in CFG["types"].items() if spec["front"] == "none"}
    assert frontless == {"table_dining", "table_coffee", "floor_lamp", "potted_plant", "side_table", "rug",
                         "cushion", "plant", "shower",       # shower: added after pod L2 (generated gaps)
                         "vase", "bowl", "plant_small", "table_lamp"}   # Milestone 9 tabletop decor
    # Decor (docs/milestone8.md §4): a size range, a height range, a question each; wall art only by a documented front.
    full, _ = OV.library_size_table(CFG)
    for d in C.DECOR_TYPES:
        assert d in OV.DECOR_TYPES and d in CFG["types"] and d in full and d in OV.DECOR_WORDS
    assert CFG["types"]["wall_art"]["front"] == OV.DOCUMENTED_RULE
    assert CFG["types"]["mirror"]["front"] == OV.DOCUMENTED_RULE     # Milestone 9: the mirror side (ABO glTF +Z)
    assert OV.geometric_front({}, OV.DOCUMENTED_RULE, CFG["front_rules"])[0] is None
    for t in ("side_table", "tv_unit"):                             # the ABO-only furniture types
        assert t in CFG["types"] and t in table and t in OV.TYPE_WORDS
    # Every configured type can be asked about (M8 pod L3: a generated shower crashed judge-requests).
    for t, spec in CFG["types"].items():
        assert t in OV.TYPE_WORDS or t in OV.DECOR_WORDS, t
        assert t in table or t in full, t


def test_licence_table_takes_every_licence_and_flags_all_but_cc0_and_cc_by():
    """docs/milestone8.md §2 (user decisions 3, 4): every licence is taken; CC0 / CC BY 4.0 unflagged, the others
    carry the flag of wenart.furniture.catalog.LICENCE_FLAGS; every licence has a URL and a printed name."""
    lic = CFG["licences"]
    assert set(lic["accept"]) == {C.LICENCE, C.CC_BY}
    names = set(lic["accept"]) | set(lic["flagged"]) | {lic["unknown"]}
    assert names == set(C.LICENCE_FLAGS)
    for name in names:
        assert lic["urls"][name].startswith("https://") and lic["names"][name], name
    spellings = [s.casefold() for table in (lic["accept"], lic["flagged"]) for v in table.values() for s in v]
    assert len(spellings) == len(set(spellings))                    # one licence per spelling
    for name, flag in (("CC-BY-NC-4.0", "non_commercial"), ("CC-BY-NC-SA-4.0", "non_commercial"),
                       ("CC-BY-SA-4.0", "share_alike"), ("CC-BY-ND-4.0", "no_derivatives"),
                       ("Sketchfab-Free-Standard", "unknown"), ("unknown", "unknown"), (C.CC_BY, None), (C.LICENCE, None)):
        assert C.licence_flag_of(name) == flag, name
    assert lic["urls"][C.CC_BY] == "https://creativecommons.org/licenses/by/4.0/"


def test_licence_values_seen_on_the_prep_pod_are_verified():
    """Prep pod P4 (survey.json, 3 Oct 2026): the metadata holds by 1369, by-sa 77, by-nc 35, by-nc-sa 16, cc0 1.
    The spellings `by` and `cc0` occur, so the table is verified; the others are taken with their flag (M8)."""
    assert CFG["licences"]["verified"] is True
    seen = {"by": (C.CC_BY, None), "cc0": (C.LICENCE, None), "by-sa": ("CC-BY-SA-4.0", "share_alike"),
            "by-nc": ("CC-BY-NC-4.0", "non_commercial"), "by-nc-sa": ("CC-BY-NC-SA-4.0", "non_commercial")}
    for value, (licence, flag) in seen.items():
        assert OV.classify_licence(value, CFG)[:2] == (licence, flag), value


@pytest.mark.parametrize("raw, expect", [
    ("by", (C.CC_BY, None)), (" BY ", (C.CC_BY, None)), ("cc0", (C.LICENCE, None)), ("CC0", (C.LICENCE, None)),
    ("CC-BY 4.0", (C.CC_BY, None)), ({"slug": "by", "label": "CC Attribution"}, (C.CC_BY, None)),
    ("by-nc", ("CC-BY-NC-4.0", "non_commercial")), ("by-sa", ("CC-BY-SA-4.0", "share_alike")),
    ("by-nc-sa", ("CC-BY-NC-SA-4.0", "non_commercial")), ("by-nd", ("CC-BY-ND-4.0", "no_derivatives")),
    ("free-st", ("Sketchfab-Free-Standard", "unknown")), ("ed", ("Sketchfab-Editorial", "non_commercial")),
    ("CC-BY-NC 4.0", ("CC-BY-NC-4.0", "non_commercial")), ("cc-by-4.0-maybe", ("unknown", "unknown")),
    ("", ("unknown", "unknown")), (None, ("unknown", "unknown")), (3, ("unknown", "unknown")),
])
def test_licence_classification(raw, expect):
    licence, flag, detail = OV.classify_licence(raw, CFG)
    assert (licence, flag) == expect
    assert (detail == "") == (flag is None)                         # a flagged or unknown value says what it was


def test_module_imports_only_the_standard_library_at_top_level():
    """Blender runs this file as a script: no third-party or wenart import may happen at import time."""
    tree = ast.parse(Path(OV.__file__).read_text(encoding="utf-8"))
    names = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            names += [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append((node.module or "").split(".")[0])
    import sys
    assert names and all(n in sys.stdlib_module_names or n == "__future__" for n in names), names


def test_blender_command_runs_this_file_in_background():
    cmd = OV.blender_command("/opt/blender", Path("/w/jobs.json"))
    assert cmd[:2] == ["/opt/blender", "-b"]
    assert "--python-exit-code" in cmd and cmd[cmd.index("--python") + 1] == str(Path(OV.__file__).resolve())
    assert cmd[-3:] == ["--", "blender-thumbs", "/w/jobs.json"]


# --------------------------------------------------------------------------
# GLB container
# --------------------------------------------------------------------------

def test_glb_info_tells_textured_vertex_coloured_and_plain(tmp_path):
    tex = OV.glb_info(make_glb(tmp_path / "t.glb", textured=True))
    assert tex["textured"] and not tex["vertex_colours"] and tex["images"] == 1 and tex["primitives"] == 1
    col = OV.glb_info(make_glb(tmp_path / "c.glb", textured=False, colours=True))
    assert not col["textured"] and col["vertex_colours"]
    plain = OV.glb_info(make_glb(tmp_path / "p.glb", textured=False))
    assert not plain["textured"] and not plain["vertex_colours"]
    bad = tmp_path / "bad.glb"
    bad.write_bytes(b"not a glb at all")
    with pytest.raises(ValueError):
        OV.glb_info(bad)


def test_shard_of_reads_the_object_path():
    uid = "a" * 32
    assert OV.shard_of(f"glbs/000-023/{uid}.glb", uid) == "metadata/000-023.json.gz"
    assert OV.shard_of(f"glbs/000-023/{'b' * 32}.glb", uid) is None
    assert OV.shard_of(f"other/000-023/{uid}.glb", uid) is None


# --------------------------------------------------------------------------
# Survey
# --------------------------------------------------------------------------

def test_survey_filters_on_canned_metadata(tmp_path):
    m = Mirror(tmp_path / "mirror")
    ok_by = m.add("sofa", licence="by", likes=19)
    ok_cc0 = m.add("sofa", licence="cc0", likes=15)
    vertex = m.add("sofa", textured=False, colours=True, likes=11)
    # Milestone 8: every licence is taken, flagged unless CC0 / CC BY 4.0 (docs/milestone8.md §2).
    flagged = {
        m.add("sofa", licence="by-nc", likes=9): ("CC-BY-NC-4.0", "non_commercial"),
        m.add("sofa", licence="by-sa", likes=8): ("CC-BY-SA-4.0", "share_alike"),
        m.add("sofa", licence="free-st", likes=7): ("Sketchfab-Free-Standard", "unknown"),
        m.add("sofa", licence="mystery", likes=6): ("unknown", "unknown"),
    }
    refused = {
        m.add("sofa", faces=1500): "face_count",
        m.add("sofa", faces=200000): "face_count",
        m.add("sofa", size=50 * 1024 * 1024): "glb_size",
        m.add("sofa", user=""): "no_credit",
        m.add("sofa", url=False): "no_credit",
        m.add("sofa", textured=False): "untextured",
        m.add(["sofa", "armchair"]): "several_types",
        m.add("sofa", meta=False): "no_metadata",
        m.add("sofa", path=False): "no_object_path",
        m.add("sofa", glb=False): "download_failed",
    }
    both = m.add(["wardrobe", "armoire"])                 # two categories of one type: fine
    m.lvis["night_table"] = ["f" * 32]                    # an unmapped category that shares a word with a missing one
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    cands = {c["uid"]: c for c in doc["candidates"]}
    assert set(cands) == {ok_by, ok_cc0, vertex, both} | set(flagged)
    assert [c["uid"] for c in doc["candidates"] if c["group"] == "sofa"][:3] == [ok_by, ok_cc0, vertex]   # likes
    assert cands[ok_by]["licence"] == C.CC_BY and cands[ok_cc0]["licence"] == C.LICENCE
    assert cands[ok_by]["licence_flag"] is None and cands[ok_cc0]["licence_flag"] is None
    for uid, (licence, flag) in flagged.items():
        assert (cands[uid]["licence"], cands[uid]["licence_flag"]) == (licence, flag), uid
        assert cands[uid]["attribution"].startswith(f'"{cands[uid]["title"]}" by Ann Author ')
    unknown = cands[next(u for u, v in flagged.items() if v[0] == "unknown")]
    assert ", licence unknown (https://huggingface.co/datasets/allenai/objaverse), via Objaverse" in unknown["attribution"]
    assert sorted(cands[both]["categories"]) == ["armoire", "wardrobe"]
    for c in cands.values():
        assert len(c["glb_sha256"]) == 64 and Path(c["glb"]).is_file()
        assert c["title"] and c["author"] == "Ann Author" and c["source_url"].startswith("https://")
        # The Milestone 8 record fields (docs/milestone8.md §2).
        assert c["source"] == "objaverse" and c["kind"] == "furniture" and c["decor_type"] is None
        assert c["units_known"] is False and c["extents_raw"] is None and c["style_hint"] is None
        assert c["licence_url"] == CFG["licences"]["urls"][c["licence"]] and c["via"] == CFG["attribution"]["via"]
    assert cands[ok_by]["attribution"] == OV.attribution_line(cands[ok_by]["title"], "Ann Author",
                                                              cands[ok_by]["source_url"], C.CC_BY, CFG)
    got = {r["uid"]: r["code"] for r in doc["refused"]}
    assert got == refused
    assert doc["licence_values"]["by"] >= 1 and doc["licence_values"]["by-nc"] == 1
    assert "bathtub" in doc["lvis"]["missing"] and doc["lvis"]["found"]["sofa"] >= 15
    # Prep pod P3: a missing category is recorded with the file's names that share a word (evidence for an
    # alternate, never a mapping by itself) and reported as a warning.
    assert doc["lvis"]["near_missing"]["nightstand"] == ["night_table"]
    assert doc["lvis"]["near_missing"]["bathtub"] == [] and doc["lvis"]["categories_in_file"] == len(m.lvis)
    text = OV.report(tmp_path / "lib", CFG)
    assert "Missing (a warning: their types stay parametric)" in text
    assert "- `nightstand`: names in the file sharing a word: `night_table`" in text
    assert "| `by-nc` | 1 | CC-BY-NC-4.0 | non_commercial |" in text
    assert (tmp_path / "lib" / OV.SURVEY_NAME).is_file()
    assert doc["counts"]["sofa"]["candidates"] == 7 and doc["counts"]["sofa"]["flagged"] == 4


def test_survey_ranks_and_keeps_at_most_24_per_type(tmp_path):
    m = Mirror(tmp_path / "mirror")
    chairs = [m.add("chair", likes=n, views=100 - n) for n in range(30)]
    tie_a = m.add("desk", likes=3, views=10)
    tie_b = m.add("desk", likes=3, views=20)
    beds = [m.add("bed", likes=n) for n in range(60)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "chair"]
    assert chosen == list(reversed(chairs))[:24]           # likes descending
    assert doc["counts"]["chair"]["not_selected"] == 6
    assert [c["uid"] for c in doc["candidates"] if c["group"] == "desk"] == [tie_b, tie_a]   # then views
    bed_group = OV.group_key(["bed_double", "bed_single"])
    assert sum(1 for c in doc["candidates"] if c["group"] == bed_group) == 48   # 24 per bed type before the split
    assert len(beds) == 60


def test_survey_lamp_ranks_floor_lamps_first(tmp_path):
    m = Mirror(tmp_path / "mirror")
    table_lamps = [m.add("lamp", likes=50 + n, name=f"Desk lamp {n}") for n in range(25)]
    floor = m.add("lamp", likes=1, name="Arc lamp", tags=("floor lamp",))
    standing = m.add("lamp", likes=0, name="Standing lamp")
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "floor_lamp"]
    assert chosen[:2] == [floor, standing] and len(chosen) == 24
    assert table_lamps[-1] in chosen and table_lamps[0] not in chosen


def test_survey_tries_the_next_rank_when_a_download_fails_the_file_checks(tmp_path):
    # A furniture category (M8 rules; the fixture categories take flat colours since Milestone 9).
    m = Mirror(tmp_path / "mirror")
    plain = [m.add("sofa", likes=100 + n, textured=False) for n in range(3)]
    good = [m.add("sofa", likes=n) for n in range(25)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "sofa"]
    assert len(chosen) == 24 and not set(chosen) & set(plain)
    assert doc["counts"]["sofa"]["tried"] == 27 and doc["counts"]["sofa"]["not_selected"] == 1
    assert sorted(good, reverse=True)[:24] == chosen


def test_fixture_categories_take_flat_colours_a_wider_face_count_and_40_candidates(tmp_path):
    """docs/milestone9.md §2.2: toilet, sink, bathtub, refrigerator, stove: a model without textures but with
    material colours is a candidate (glb_info flat_colours), faces 800-400k, up to 40 candidates; a sofa keeps the
    M8 rules (untextured refused, faces 2k-150k)."""
    m = Mirror(tmp_path / "mirror")
    flat = [m.add("toilet", likes=200 + n, textured=False) for n in range(3)]
    low = m.add("toilet", likes=150, faces=1000)                     # inside 800-400k, outside 2k-150k
    high = m.add("toilet", likes=140, faces=350000)
    tiny = m.add("toilet", likes=130, faces=500)                     # still refused
    rest = [m.add("toilet", likes=n) for n in range(45)]
    sofa_low = m.add("sofa", faces=1000)
    sofa_flat = m.add("sofa", textured=False)
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "toilet"]
    assert len(chosen) == 40
    assert set(flat) | {low, high} <= set(chosen) and tiny not in chosen
    assert chosen[:5] == list(reversed(flat)) + [low, high]          # rank order: likes
    by_uid = {c["uid"]: c for c in doc["candidates"]}
    assert all(by_uid[u]["glb_info"]["flat_colours"] is True for u in flat)
    assert "flat_colours" not in by_uid[rest[-1]]["glb_info"]
    codes = {r["uid"]: r["code"] for r in doc["refused"]}
    assert codes[tiny] == "face_count" and codes[sofa_low] == "face_count" and codes[sofa_flat] == "untextured"
    assert len([u for u in rest if u in chosen]) == 35


def test_fixture_flat_colours_need_a_material(tmp_path):
    m = Mirror(tmp_path / "mirror")
    uid = m.add("toilet", textured=False)
    hub = m.write()
    glb = hub.path(m.paths[uid])
    doc = OV.glb_json(glb)
    doc.pop("materials")
    for mesh in doc["meshes"]:
        for prim in mesh["primitives"]:
            prim.pop("material", None)
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    data = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    total = 12 + 8 + len(js) + 8 + len(data)
    Path(glb).write_bytes(struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                          + struct.pack("<II", len(data), 0x004E4942) + data)
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    assert not doc["candidates"] and doc["refused"][0]["code"] == "untextured"


def test_survey_keeps_the_candidates_of_the_survey_before_first(tmp_path):
    """Milestone 9: a wider prefilter must never push out a model judged before: the candidates of the earlier
    survey.json in the out folder come first in their type, the rest follow in rank order."""
    m = Mirror(tmp_path / "mirror")
    old = [m.add("sofa", likes=n) for n in range(24)]
    hub = m.write()
    out = tmp_path / "lib"
    first = OV.survey(hub, out, CFG, log=quiet)
    assert {c["uid"] for c in first["candidates"]} == set(old)
    newer = [m.add("sofa", likes=1000 + n) for n in range(5)]       # better liked: they would rank first
    hub = m.write()
    second = OV.survey(hub, out, CFG, log=quiet)
    chosen = [c["uid"] for c in second["candidates"]]
    assert len(chosen) == 24 and set(chosen) == set(old) and not set(chosen) & set(newer)
    assert {c["uid"]: c["rank"] for c in second["candidates"]}[old[-1]] == 6     # the rank stays the true rank


def test_survey_without_download_lists_the_top_of_the_ranking(tmp_path):
    m = Mirror(tmp_path / "mirror")
    uids = [m.add("sofa", likes=n, glb=False) for n in range(30)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, download=False, log=quiet)
    assert [c["uid"] for c in doc["candidates"]] == list(reversed(uids))[:24]
    assert all("glb" not in c for c in doc["candidates"]) and doc["downloaded"] is False


def test_survey_cli_with_a_mirror(tmp_path):
    m = Mirror(tmp_path / "mirror")
    m.add("sofa")
    m.write()
    out = tmp_path / "lib"
    assert OV.main(["survey", "--mirror", str(tmp_path / "mirror"), "--out", str(out)]) == 0
    assert len(OV.read_json(out / OV.SURVEY_NAME)["candidates"]) == 1
    empty = Mirror(tmp_path / "empty")
    empty.add("sofa", user="")                              # no credit: still refused (M8 keeps the credit fields)
    empty.write()
    assert OV.main(["survey", "--mirror", str(tmp_path / "empty"), "--out", str(tmp_path / "lib2")]) == 1


# --------------------------------------------------------------------------
# Unit guess
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def size_table():
    return OV.load_size_table()


@pytest.mark.parametrize("raw, scale", [
    ([2.0, 0.9, 0.8], 1.0),            # metres
    ([200, 90, 80], 0.01),              # centimetres
    ([78.7, 35.4, 31.5], 0.0254),       # inches
    ([2000, 900, 800], 0.001),          # millimetres
])
def test_unit_guess_takes_the_factor_in_the_type_range(size_table, raw, scale):
    table, tol = size_table
    got = OV.guess_unit(raw, ["sofa"], CFG, table, tol)
    assert got["ok"] and got["scale"] == scale and got["type"] == "sofa"
    assert all(abs(a - b) < 0.01 for a, b in zip(got["dims_m"], [2.0, 0.9, 0.8]))


def test_unit_guess_refuses_none_and_ambiguous(size_table):
    table, tol = size_table
    # No factor fits and a 5 x 5 x 20 tower has no sofa proportions at any scale (P2: the proportions refuse).
    none = OV.guess_unit([5.0, 5.0, 20.0], ["sofa"], CFG, table, tol)
    assert not none["ok"] and none["code"] == "unit_none" and "proportions" in none["detail"]
    # 100 x 50 x 75 raw: 1.00 x 0.50 x 0.75 m (cm) and 2.54 x 1.27 x 1.91 m (in) -> a desk only in cm;
    # a potted plant 40 x 40 x 60 raw is 0.40 x 0.40 x 0.60 m (cm) and 1.02 x 1.02 x 1.52 m (in): both fit
    amb = OV.guess_unit([40, 40, 60], ["potted_plant"], CFG, table, tol)
    assert not amb["ok"] and amb["code"] == "unit_ambiguous" and len(amb["fits"]) == 2
    desk = OV.guess_unit([100, 50, 75], ["desk"], CFG, table, tol)
    assert desk["ok"] and desk["scale"] == 0.01


def test_bed_split_by_width(size_table):
    table, tol = size_table
    beds = ["bed_double", "bed_single"]
    assert OV.guess_unit([1.6, 2.05, 1.0], beds, CFG, table, tol)["type"] == "bed_double"
    assert OV.guess_unit([0.95, 2.0, 0.9], beds, CFG, table, tol)["type"] == "bed_single"
    assert OV.guess_unit([200, 120, 50], beds, CFG, table, tol)["type"] == "bed_single"     # cm, width 1.20
    assert OV.guess_unit([2.0, 1.30, 0.5], beds, CFG, table, tol)["type"] == "bed_double"   # 1.30 > 1.275


def test_lamp_height_decides_floor_lamp(size_table):
    table, tol = size_table
    got = OV.guess_unit([0.40, 0.40, 1.65], ["floor_lamp"], CFG, table, tol)
    assert got["ok"] and got["scale"] == 1.0 and not got.get("normalised")
    # Lower than a floor lamp but slender: no factor fits, so the units are unknown (P2) and only the proportions
    # count: normalised (the judges' matches_type decides); a squat lamp is refused by its proportions.
    slender = OV.guess_unit([0.30, 0.30, 0.55], ["floor_lamp"], CFG, table, tol)
    assert slender["ok"] and slender["normalised"] and slender["dims_m"][2] >= 1.2
    squat = OV.guess_unit([0.50, 0.50, 0.40], ["floor_lamp"], CFG, table, tol)
    assert not squat["ok"] and squat["code"] == "unit_none"


@pytest.mark.parametrize("raw, types, ftype", [
    ([353.07, 440.95, 514.44], ["armchair"], "armchair"),            # prep pod "Old Sofa" (armchair category)
    ([1379.6, 1334.5, 1515.1], ["armchair"], "armchair"),
    ([200.0, 200.0, 717.24], ["floor_lamp"], "floor_lamp"),          # prep pod "Pirate Lantern"
    ([19.656, 39.029, 15.786], ["bed_double", "bed_single"], "bed_single"),   # width / length 0.50
    ([2436.5, 2172.96, 1861.3], ["bed_double", "bed_single"], "bed_double"),  # width / length 0.89
])
def test_unknown_units_are_normalised_by_type(size_table, raw, types, ftype):
    """Prep pod P2: no factor of x1, 0.01, 0.0254, 0.001 fits -> unit_scale = the type's typical footprint (size
    table centre) / the raw footprint, moved into the type's range when needed; the note says so."""
    table, tol = size_table
    heights = {t: spec["height"] for t, spec in CFG["types"].items()}
    got = OV.guess_unit(raw, types, CFG, table, tol)
    assert got["ok"] and got["normalised"] and got["type"] == ftype and got["fits"] == []
    assert got["note"].startswith(OV.NORMALISED_NOTE + ":")
    assert OV.fits_type([v * got["scale"] for v in raw], ftype, table, tol, heights)
    assert got["dims_m"] == [round(v * got["scale"], 4) for v in raw]
    (w0, w1), (d0, d1) = table[ftype]
    centre = math.sqrt((w0 + w1) / 2 * (d0 + d1) / 2 / (raw[0] * raw[1]))
    if "moved from" not in got["note"]:
        assert got["scale"] == pytest.approx(centre)
    if ftype.startswith("bed"):
        assert "from the proportions" in got["note"]


def test_normalised_scale_is_moved_into_the_range_and_bad_boxes_are_refused(size_table):
    table, tol = size_table
    # 112 x 113 x 186 raw armchair: the centre factor makes it 1.40 m tall (> 1.30): moved to the highest factor
    # that keeps the height in range.
    got = OV.guess_unit([112.373, 113.062, 186.23], ["armchair"], CFG, table, tol)
    assert got["ok"] and "moved from" in got["note"] and got["dims_m"][2] == pytest.approx(1.30, abs=1e-3)
    for bad in ([0.0, 1.0, 1.0], [float("nan"), 1.0, 1.0], [-2.0, 1.0, 1.0]):
        assert OV.normalise_unit(bad, ["sofa"], CFG, table, tol)["code"] == "unit_none"
    # A standard factor still wins when one fits (real units known): never normalised.
    assert not OV.guess_unit([200, 90, 80], ["sofa"], CFG, table, tol).get("normalised")


# --------------------------------------------------------------------------
# Geometry: front statistics and the geometric front
# --------------------------------------------------------------------------

def box(x0, y0, z0, x1, y1, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def quad(x0, y0, z0, x1, y1, z1, normal):
    """A planar rectangle face as a polygon record (corners in order, area by Newell)."""
    if normal in ("+y", "-y"):
        y = y1 if normal == "+y" else y0
        pts = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
    else:
        x = x1 if normal == "+x" else x0
        pts = [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
    rec = list(OV.poly_record(pts))
    axis = {"+x": 3, "-x": 3, "+y": 4, "-y": 4}[normal]
    rec[3:6] = [0.0, 0.0, 0.0]
    rec[axis] = 1.0 if normal.startswith("+") else -1.0
    return tuple(rec)


def sofa_points(back="+Y"):
    pts = box(-1.0, -0.45, 0.0, 1.0, 0.45, 0.45) + box(-1.0, 0.25, 0.45, 1.0, 0.45, 0.85)
    if back == "-X":          # turn the sofa so its back is at -X
        pts = [(-y, x, z) for x, y, z in pts]
    return pts


def test_newell_normal_and_area():
    (n, area) = OV.newell([(0, 0, 0), (2, 0, 0), (2, 3, 0), (0, 3, 0)])
    assert n == (0.0, 0.0, 1.0) and area == pytest.approx(6.0)
    assert OV.newell([(0, 0, 0), (1, 1, 1), (2, 2, 2)]) == ((0.0, 0.0, 0.0), 0.0)


def test_back_taller_front():
    rules = CFG["front_rules"]
    stats = OV.front_stats(sofa_points())
    assert OV.geometric_front(stats, "back_taller", rules)[0] == "-Y"
    turned = OV.front_stats(sofa_points(back="-X"))
    assert OV.geometric_front(turned, "back_taller", rules)[0] == "+X"
    flat = OV.front_stats(box(-1, -0.5, 0, 1, 0.5, 0.45))
    front, note = OV.geometric_front(flat, "back_taller", rules)
    assert front is None and "no taller side" in note


def test_detail_side_front():
    rules = CFG["front_rules"]
    cabinet = box(-0.5, -0.25, 0, 0.5, 0.25, 0.8)
    handles = [(x / 100.0, -0.25, 0.4 + z / 100.0) for x in range(-10, 10) for z in range(3)]   # 60 at -Y
    front, note = OV.geometric_front(OV.front_stats(cabinet + handles), "detail_side", rules)
    assert front == "-Y" and "detail_side" in note
    assert OV.geometric_front(OV.front_stats(cabinet), "detail_side", rules)[0] is None   # plain box: undecided


def test_open_side_front():
    rules = CFG["front_rules"]
    pts = box(-0.5, -0.15, 0, 0.5, 0.15, 1.8)
    polys = [quad(-0.5, -0.15, 0, 0.5, 0.15, 1.8, "+y"),              # back panel
             quad(-0.5, -0.15, 0, 0.5, 0.15, 1.8, "-x"), quad(-0.5, -0.15, 0, 0.5, 0.15, 1.8, "+x")]
    front, _ = OV.geometric_front(OV.front_stats(pts, polys), "open_side", rules)
    assert front == "-Y"
    closed = polys + [quad(-0.5, -0.15, 0, 0.5, 0.15, 1.8, "-y")]
    assert OV.geometric_front(OV.front_stats(pts, closed), "open_side", rules)[0] is None
    assert OV.geometric_front(OV.front_stats(pts, polys), "none", rules) == (None, "type without a front")


def test_views_and_camera_distance():
    c = (1.0, 2.0, 0.5)
    loc = OV.view_location(c, 10.0, "-Y", 30.0)
    assert loc[0] == pytest.approx(1.0) and loc[1] == pytest.approx(2.0 - 10.0 * 0.8660254)
    assert loc[2] == pytest.approx(0.5 + 5.0)
    assert OV.view_location(c, 10.0, "+X", 0.0) == pytest.approx((11.0, 2.0, 0.5))
    d = OV.camera_distance([2.0, 0.9, 0.8], 50.0, 36.0, 1.0)
    radius = 0.5 * (2.0 ** 2 + 0.9 ** 2 + 0.8 ** 2) ** 0.5
    assert d == pytest.approx(radius / 0.3387, rel=1e-3)          # sin(atan(18 / 50)) = 0.3387


# --------------------------------------------------------------------------
# Thumbnails with a fake Blender
# --------------------------------------------------------------------------

def make_view(path: Path, shade: int) -> None:
    from PIL import Image
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (256, 256), (shade, shade, shade)).save(path)


def fake_runner(shapes: dict, calls: list, jobs_seen: list = None):
    """A runner that writes what the Blender side writes: measure/<uid>.json and the four views. A shape is
    ``(points, polys)`` or ``(points, polys, deck)`` (a canned deck measurement for a bed job; without one a bed job
    gets the measurement of no hit: ``deck_height`` on no polygon)."""
    def run(_blender, jobs_path, _log, _timeout):
        jobs = json.loads(Path(jobs_path).read_text())
        calls.append([j["uid"] for j in jobs["objects"]])
        if jobs_seen is not None:
            jobs_seen.extend(jobs["objects"])
        for n, job in enumerate(jobs["objects"]):
            shape = shapes.get(job["uid"])
            rec = {"uid": job["uid"], "glb": job["glb"], "glb_sha256": job["glb_sha256"], "device": "OPTIX"}
            if shape is None:
                rec.update(ok=False, error="RuntimeError: no mesh objects in the GLB")
            else:
                points, polys = shape[0], shape[1]
                rec.update(ok=True, stats=OV.front_stats(points, polys), vertices=len(points), triangles=4000,
                           mesh_objects=1, images=1, colour_attributes=0, seconds=1.0)
                if job.get("deck"):
                    rec["deck"] = shape[2] if len(shape) > 2 else OV.deck_height([], *OV.bounds(points))
                if job.get("render", True):
                    for i, view in enumerate(job["views"]):
                        make_view(Path(view), 60 + 40 * i + n)
            OV.write_json(Path(job["measure"]), rec)
        OV.write_json(Path(jobs["work"]) / "blender_status.json",
                      {"device": "OPTIX", "blender": "5.2.2", "done": [], "failed": [], "left": []})
        return 0
    return run


def scaled(points, k):
    return [(x * k, y * k, z * k) for x, y, z in points]


@pytest.fixture()
def library(tmp_path):
    """A surveyed and thumbnailed library: sofas in cm and m, a bed, a dining table, a broken GLB, a giant (no unit
    factor fits: normalised by type, prep pod P2) and a tower (no factor fits and not a sofa's proportions)."""
    m = Mirror(tmp_path / "mirror")
    uids = {
        "sofa_cm": m.add("sofa", likes=9, name="Oak Sofa"),
        "sofa_m": m.add("sofa", likes=8, licence="cc0", name="Grey Sofa"),
        "sofa_tv": m.add("sofa", likes=7, name="Turned Sofa"),
        "bed": m.add("bed", likes=5, name="Bed"),
        "table": m.add("dining_table", likes=4, name="Table"),
        "broken": m.add("sofa", likes=3, name="Broken"),
        "giant": m.add("sofa", likes=2, name="Giant"),
        "tower": m.add("sofa", likes=1, name="Tower"),
    }
    hub = m.write()
    out = tmp_path / "lib"
    OV.survey(hub, out, CFG, log=quiet)
    bed = box(-0.8, -1.0, 0, 0.8, 1.0, 0.5) + box(-0.8, 0.9, 0.5, 0.8, 1.0, 1.1)        # headboard at +Y
    shapes = {
        uids["sofa_cm"]: (scaled(sofa_points(), 100.0), []),
        uids["sofa_m"]: (sofa_points(), []),
        uids["sofa_tv"]: (sofa_points(back="-X"), []),
        uids["bed"]: (bed, []),
        uids["table"]: (box(-0.8, -0.45, 0, 0.8, 0.45, 0.75), []),
        uids["giant"]: (scaled(sofa_points(), 7.0), []),
        uids["tower"]: ([(x, y, z * 7.0) for x, y, z in sofa_points()], []),
    }
    calls = []
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=fake_runner(shapes, calls), log=quiet)
    return SimpleNamespace(out=out, work=tmp_path / "work", uids=uids, doc=doc, rc=rc, calls=calls, shapes=shapes,
                           tmp=tmp_path)


def test_thumbnails_resolve_units_types_fronts_and_write_sheets(library):
    from PIL import Image
    objs, u = library.doc["objects"], library.uids
    assert library.rc == 0 and library.doc["device"] == "OPTIX"
    assert objs[u["sofa_cm"]]["status"] == "ready" and objs[u["sofa_cm"]]["unit"]["scale"] == 0.01
    assert objs[u["sofa_m"]]["unit"]["scale"] == 1.0 and objs[u["sofa_m"]]["geometric_front"] == "-Y"
    assert objs[u["sofa_tv"]]["geometric_front"] == "+X"
    assert objs[u["bed"]]["type"] == "bed_double" and objs[u["bed"]]["geometric_front"] == "-Y"
    assert objs[u["table"]]["type"] == "table_dining" and objs[u["table"]]["geometric_front"] is None
    assert objs[u["broken"]]["code"] == "blender_error"
    # Prep pod P2: the giant (14 x 6.3 x 5.95 raw: no factor fits) is normalised by type to the typical sofa
    # footprint (size table centre 2.1 x 0.9 m); the tower (2 x 0.9 x 5.95 raw) has no sofa proportions at any scale.
    giant = objs[u["giant"]]
    assert giant["status"] == "ready" and giant["type"] == "sofa" and giant["unit"]["normalised"] is True
    assert giant["unit"]["scale"] == pytest.approx(math.sqrt(2.1 * 0.9 / (14.0 * 6.3)))
    assert giant["unit"]["note"].startswith("normalised by type (model units unknown)")
    assert giant["unit"]["dims_m"] == pytest.approx([2.049, 0.922, 0.871], abs=0.001)
    assert objs[u["tower"]]["code"] == "unit_none" and "proportions" in objs[u["tower"]]["detail"]
    rec = objs[u["sofa_cm"]]
    sheet = Image.open(library.out / rec["sheet"])
    thumb = Image.open(library.out / rec["thumb"])
    assert sheet.size == (512, 512) and thumb.size == (256, 256)
    assert rec["thumb"] == f"thumbs/sofa/{u['sofa_cm']}.jpg"
    notice = (library.out / "thumbs" / "NOTICE.md").read_text()
    assert "ODC Attribution License" in notice and '"Oak Sofa" by Ann Author' in notice


def test_thumbnails_resume_renders_nothing_twice(library):
    calls = []
    doc, rc = OV.thumbnails(library.out, library.work, CFG, runner=fake_runner(library.shapes, calls), log=quiet)
    assert rc == 0
    assert calls == [[library.uids["broken"]]]            # only the object without a good measurement
    assert doc["objects"][library.uids["sofa_cm"]]["status"] == "ready"


def test_sheet_tiles_follow_the_view_order(library):
    import numpy as np
    from PIL import Image
    arr = np.asarray(Image.open(library.out / library.doc["objects"][library.uids["sofa_m"]]["sheet"]))
    centres = [arr[128, 128], arr[128, 384], arr[384, 128], arr[384, 384]]
    greys = [int(c.mean()) for c in centres]
    assert greys == sorted(greys)                            # views 0..3 were written darker to lighter


# --------------------------------------------------------------------------
# Judging requests, schema, answers
# --------------------------------------------------------------------------

def test_judge_schema_is_strict():
    good = {"is_single_object": True, "matches_type": True, "photoreal_quality": 4, "has_mattress": None,
            "styles": ["scandinavian", "neutral"], "front_view": 0}
    assert OV.valid_judgement(good)
    for bad in (dict(good, photoreal_quality=6), dict(good, styles=["baroque"]), dict(good, front_view=4),
                dict(good, extra=1), {k: v for k, v in good.items() if k != "styles"}, None):
        assert not OV.valid_judgement(bad), bad
    assert OV.judge_schema()["additionalProperties"] is False


def test_judge_schema_has_no_unique_items_and_repeated_styles_are_removed_in_code():
    """Prep pod P1: vLLM's xgrammar refused the schema ("Unimplemented keys: uniqueItems") on every judge call.
    The schema no longer says uniqueItems; a repeated style is valid and removed in code (first mention kept)."""
    assert "uniqueItems" not in json.dumps(OV.judge_schema())
    from wenart.recognition import schemas as RS
    assert RS.grammar_problems(OV.judge_schema()) == []
    twice = {"is_single_object": True, "matches_type": True, "photoreal_quality": 5, "has_mattress": None,
             "styles": ["modern", "scandinavian", "modern"], "front_view": 0}
    assert OV.valid_judgement(twice)
    assert OV.clean_judgement(twice)["styles"] == ["modern", "scandinavian"] and twice["styles"][2] == "modern"
    assert OV.clean_judgement(None) is None
    dec = OV.decide(obj(), {"qwen": twice, "glm": dict(twice, styles=["scandinavian", "scandinavian"])}, CFG)
    assert dec["accepted"] and dec["styles"] == ["scandinavian"]
    assert "glm ['scandinavian']" in dec["style_note"]


def test_judge_requests_hash_the_sheet_pixels_and_the_question(library):
    doc = OV.judge_requests(library.out, CFG)
    keys = [i["key"] for i in doc["items"]]
    ready = sorted(uid for uid, o in library.doc["objects"].items() if o["status"] == "ready")
    assert keys == [f"lib_{uid}" for uid in ready]
    item = next(i for i in doc["items"] if i["context"]["uid"] == library.uids["sofa_cm"])
    assert item["task"] == "library_judge" and item["images"] == [f"sheets/{library.uids['sofa_cm']}.jpg"]
    assert "offered as a sofa" in item["prompt"] and "2 x 0.9 x 0.85 m" in item["prompt"]
    again = OV.judge_requests(library.out, CFG)
    assert [i["input_sha256"] for i in again["items"]] == [i["input_sha256"] for i in doc["items"]]
    table = next(i for i in doc["items"] if i["context"]["uid"] == library.uids["table"])
    assert "null (this type has no front)" in table["prompt"]
    giant = next(i for i in doc["items"] if i["context"]["uid"] == library.uids["giant"])
    assert "no usable unit: scaled to a typical sofa it would measure about" in giant["prompt"]
    assert "no usable unit" not in item["prompt"]
    # other pixels -> other hash
    from PIL import Image
    sheet = library.out / "judge" / item["images"][0]
    Image.new("RGB", (512, 512), (1, 2, 3)).save(sheet, format="JPEG")
    changed = OV.judge_requests(library.out, CFG)
    new = next(i for i in changed["items"] if i["key"] == item["key"])
    assert new["input_sha256"] != item["input_sha256"]


def answer(front=0, styles=("scandinavian", "neutral"), quality=5, single=True, match=True, mattress=None):
    return {"is_single_object": single, "matches_type": match, "photoreal_quality": quality,
            "has_mattress": mattress, "styles": list(styles), "front_view": front}


class FakeClient:
    def __init__(self, model: str, fn):
        self.model = model
        self.fn = fn
        self.calls = 0
        self.deadline = None

    def run_schema(self, images, prompt, schema, **kw):
        self.calls += 1
        assert kw["task"] == "library_judge" and kw["system_prompt"] == OV.SYSTEM_PROMPT
        assert all(Path(p).is_file() for p in images)
        data = self.fn(images, prompt)
        kind = "decor" if schema.get("title") == "LibraryJudgeDecor" else "furniture"   # the item's own schema
        assert schema == OV.judge_schema(kind)
        error = None if OV.valid_judgement(data, kind) else "schema: invalid"
        return SimpleNamespace(data=data if error is None else None, raw_text=json.dumps(data), error=error,
                               attempts=1, latency_s=0.01)


def good_answers(library, key):
    """Answers that agree with the geometry: front view of the geometric front, beds with a mattress."""
    objs = library.doc["objects"]

    def fn(images, _prompt):
        uid = Path(images[0]).stem
        obj = objs[uid]
        geo = obj.get("geometric_front")
        front = OV.VIEW_SIDES.index(geo) if geo else None
        styles = ("modern", "scandinavian") if key == "qwen" else ("scandinavian", "neutral")
        return answer(front=front, styles=styles, mattress=True if obj["type"].startswith("bed") else None)
    return fn


def run_judges(library, clients=None, fresh=False):
    """Both judges over ``judge/requests.json`` (written anew); ``fresh`` drops the stored answers first."""
    clients = clients or {}
    if fresh:
        for f in (library.out / "judge").glob("answers_*.json"):
            f.unlink()
    OV.judge_requests(library.out, CFG)
    rcs = {}
    for key in OV.MODEL_KEYS:
        made = []

        def factory(info, _server, key=key, made=made):
            made.append(FakeClient(info["id"], clients.get(key) or good_answers(library, key)))
            return made[-1]
        rcs[key] = OV.main(["judge", "--out", str(library.out), "--model-key", key, "--workers", "2"],
                           client_factory=factory)
        rcs[key + "_calls"] = made[0].calls if made else 0
    return rcs


def test_judge_answers_are_stored_and_reused(library):
    rcs = run_judges(library)
    assert rcs["qwen"] == 0 and rcs["glm"] == 0 and rcs["qwen_calls"] == 6        # the giant too (P2)
    store = json.loads((library.out / "judge" / "answers_qwen3-vl-8b.json").read_text())
    assert store["model_key"] == "qwen" and store["model"] == "Qwen/Qwen3-VL-8B-Instruct"
    assert sorted(store["calls"]) == sorted(f"lib_{u}" for u, o in library.doc["objects"].items()
                                            if o["status"] == "ready")
    again = run_judges(library)
    assert again["qwen"] == 0 and again["qwen_calls"] == 0          # all reused, no client made
    status = OV.judge_status(library.out)
    assert status["complete"] and status["models"]["glm"]["answered"] == 6


def test_judge_exit_codes(library):
    OV.judge_requests(library.out, CFG)
    bad = OV.main(["judge", "--out", str(library.out), "--model-key", "qwen"],
                  client_factory=lambda info, _s: FakeClient(info["id"], lambda *_: {"nonsense": 1}))
    assert bad == OV.EXIT_SERVER
    late = OV.main(["judge", "--out", str(library.out), "--model-key", "glm", "--deadline", "1"],
                   client_factory=lambda info, _s: FakeClient(info["id"], lambda *_: answer()))
    assert late == OV.EXIT_DEADLINE
    assert OV.main(["judge", "--out", str(library.tmp / "nowhere"), "--model-key", "qwen"]) == OV.EXIT_SERVER
    assert OV.main(["judge-status", "--out", str(library.out)]) == 1


def test_judge_seeding_copies_matching_answers(library):
    run_judges(library)
    seed = library.tmp / "seed"
    seed.mkdir()
    shutil.copy(library.out / "judge" / "answers_qwen3-vl-8b.json", seed)
    (library.out / "judge" / "answers_qwen3-vl-8b.json").unlink()
    rc = OV.main(["judge", "--out", str(library.out), "--model-key", "qwen", "--seed-answers", str(seed)],
                 client_factory=lambda info, _s: pytest.fail("no call expected: every answer is seeded"))
    assert rc == 0
    calls = json.loads((library.out / "judge" / "answers_qwen3-vl-8b.json").read_text())["calls"]
    assert all(rec["seeded_from"].endswith("answers_qwen3-vl-8b.json") for rec in calls.values())


# --------------------------------------------------------------------------
# Accept rules
# --------------------------------------------------------------------------

def obj(ftype="sofa", geo="-Y"):
    return {"uid": "u1", "type": ftype, "geometric_front": geo, "geometric_note": "back_taller: ...",
            "unit": {"ok": True, "scale": 1.0}}


@pytest.mark.parametrize("o, a, b, code", [
    (obj(), answer(), answer(), ""),
    (obj(), answer(single=False), answer(), "not_single"),
    (obj(), answer(), answer(match=False), "type_mismatch"),
    (obj(), answer(quality=3), answer(), "quality"),
    (obj("bed_double"), answer(mattress=True), answer(mattress=False), "mattress_not_agreed"),
    (obj("bed_double"), answer(mattress=None), answer(mattress=None), "mattress_not_agreed"),
    (obj("bed_double"), answer(mattress=False), answer(mattress=False), "no_deck"),          # no deck measured
    (obj("bed_double"), answer(mattress=True), answer(mattress=True), ""),
    (obj(), answer(front=0), answer(front=2), "front_not_agreed"),
    (obj(), answer(front=None), answer(front=None), "front_not_agreed"),
    (obj(geo="+Y"), answer(front=0), answer(front=0), "front_not_agreed"),
    (obj(geo=None), answer(front=0), answer(front=0), "front_not_agreed"),
    (obj(geo="+X"), answer(front=1), answer(front=1), ""),
    (obj("table_dining", geo=None), answer(front=None), answer(front=3), ""),
    (obj(), answer(styles=["modern"]), answer(styles=["classic"]), "no_common_style"),
    (obj(), answer(), None, "not_judged"),
])
def test_accept_rules(o, a, b, code):
    dec = OV.decide(o, {"qwen": a, "glm": b}, CFG)
    assert dec["accepted"] == (code == "") and dec["code"] == code


def test_accept_front_and_styles_of_an_accepted_object():
    dec = OV.decide(obj(geo="+X"), {"qwen": answer(front=1, styles=["modern", "scandinavian", "neutral"]),
                                    "glm": answer(front=1, styles=["scandinavian", "modern"])}, CFG)
    assert dec["front_axis"] == "+X" and dec["front_axis_confidence"] == "high" and dec["front_view"] == 1
    assert dec["styles"] == ["scandinavian", "modern"]                     # neutral only when both name it
    frontless = OV.decide(obj("table_dining", geo=None), {"qwen": answer(front=2), "glm": answer(front=0)}, CFG)
    assert frontless["front_axis"] == "-Y" and frontless["front_axis_confidence"] == "low"
    many = OV.decide(obj(), {"qwen": answer(single=False, quality=2), "glm": answer(front=3)}, CFG)
    assert [c for c, _ in many["failed"]] == ["not_single", "quality", "front_not_agreed"]


def test_generated_models_take_the_front_both_judges_agree_on():
    """M8 pod L2: the vertex-count rule read the generator's mesh as "+Y" on fridges and bathtubs that both judges
    saw facing -Y; for a generated model the agreeing judges decide (the geometry is recorded), for a scanned one
    the geometry still has to agree."""
    gen = dict(obj("fridge", geo="+Y"), source="generated")
    dec = OV.decide(gen, {"qwen": answer(front=0), "glm": answer(front=0)}, CFG)
    assert dec["accepted"] and dec["front_axis"] == "-Y" and dec["front_view"] == 0
    assert "judges decide" in dec["front_axis_note"]
    undecided = OV.decide(dict(gen, geometric_front=None), {"qwen": answer(front=0), "glm": answer(front=0)}, CFG)
    assert undecided["accepted"] and undecided["front_axis"] == "-Y"
    split = OV.decide(gen, {"qwen": answer(front=0), "glm": answer(front=2)}, CFG)
    assert split["code"] == "front_not_agreed"                             # the judges still have to agree
    scanned = OV.decide(dict(gen, source="objaverse"), {"qwen": answer(front=0), "glm": answer(front=0)}, CFG)
    assert scanned["code"] == "front_not_agreed"


def _canned_accept(tmp_path, monkeypatch, specs):
    """``accept`` over canned objects: specs = [(uid, source, kind, type, styles, quality, likes)]."""
    out = tmp_path / "lib"
    objects, cands, answers = {}, {}, {}
    for uid, source, kind, ftype, styles, q, likes in specs:
        o = dict(obj(ftype, geo=None if CFG["types"][ftype]["front"] == "none" else "-Y"), uid=uid, status="ready",
                 source=source, kind=kind, decor_type=ftype if kind == "decor" else None)
        objects[uid] = o
        cands.setdefault(source, []).append({"uid": uid, "likes": likes, "views": 0, "types": [ftype], "kind": kind})
        a = answer(front=0, styles=styles, quality=q)
        if kind == "decor":
            a = {"is_single_object": True, "is_decor_type": True, "photoreal_quality": q, "styles": list(styles),
                 "front_view": None}
        answers[uid] = {"qwen": a, "glm": a}
    OV.write_json(out / OV.THUMBS_JSON, {"objects": objects})
    for source, recs in cands.items():
        OV.write_json(out / OV.SURVEY_FILES[source], {"candidates": recs})
    monkeypatch.setattr(OV, "load_judgements", lambda *_a, **_k: answers)
    return out


def _m8_accept_cfg():
    """The Milestone 8 acceptance limits (12 per type, decor 16, 3 per style family, no fill pass)."""
    cfg = dict(CFG)
    cfg["accept"] = dict(CFG["accept"], per_type_max=12, decor_per_type_max=16, per_family_max=3, style_fill=False)
    return cfg


def test_accept_m8_limits_keep_12_per_type_and_3_per_style_family(tmp_path, monkeypatch):
    """docs/milestone8.md §2 (the rule without the fill pass): <= 12 per furniture type, <= 3 per (type, style
    family); rank by mean quality, then the source order (abo, polyhaven, objaverse, generated), then the lower
    quality and likes."""
    m8 = _m8_accept_cfg()
    families = [s for s in OV.style_values() if s != C.NEUTRAL]
    specs = []
    for n in range(20):                                   # 20 sofas over 5 families, quality 5 / 4 alternating
        specs.append((f"o{n:02d}", "objaverse", "furniture", "sofa", [families[n % 5]], 5 if n % 2 else 4, n))
    out = _canned_accept(tmp_path, monkeypatch, specs)
    doc = OV.accept(out, m8)
    kept = [d["uid"] for d in doc["accepted"]]
    per_family: dict = {}
    for d in doc["accepted"]:
        for f in d["styles"]:
            per_family[f] = per_family.get(f, 0) + 1
    assert len(kept) == 12 and max(per_family.values()) == 3 and doc["counts"]["over_type_limit"] == 8
    assert all(int(u[1:]) % 2 for u in kept[:10])         # every quality-5 sofa first (10 of them, 2 per family)
    assert kept[0] == "o19"                               # then likes
    # 15 sofas of 3 families: 3 per family are kept, the type limit is not reached.
    specs = [(f"p{n:02d}", "objaverse", "furniture", "sofa", [families[n % 3]], 5, n) for n in range(15)]
    doc = OV.accept(_canned_accept(tmp_path / "3", monkeypatch, specs), m8)
    assert len(doc["accepted"]) == 9 and doc["counts"]["over_style_limit"] == 6
    assert {d["uid"] for d in doc["accepted"]} == {f"p{n:02d}" for n in range(6, 15)}      # the most liked
    # A model listed in a full family and one with room is kept and counts for both.
    specs = [(f"a{n}", "objaverse", "furniture", "sofa", ["modern"], 5, 10 - n) for n in range(3)]
    specs += [("b0", "objaverse", "furniture", "sofa", ["modern", "industrial"], 5, 0),
              ("b1", "objaverse", "furniture", "sofa", ["modern"], 5, 0)]
    out = _canned_accept(tmp_path / "2", monkeypatch, specs)
    doc = OV.accept(out, m8)
    assert [d["uid"] for d in doc["accepted"]] == ["a0", "a1", "a2", "b0"]
    assert [(d["uid"], d["code"]) for d in doc["refused"]] == [("b1", "over_style_limit")]


def test_accept_spreads_styles_first_then_fills_to_20(tmp_path, monkeypatch):
    """docs/milestone9.md §1: 20 per type; the first pass keeps <= 5 per style family in rank order, the fill pass
    then takes the models it left for their style, in rank order, until the type limit (``style_fill``)."""
    families = [s for s in OV.style_values() if s != C.NEUTRAL]
    # 30 sofas of 3 families (10 each), likes = n: the first pass keeps the 5 most liked of each family (15), the
    # fill pass the 5 most liked of the rest.
    specs = [(f"s{n:02d}", "objaverse", "furniture", "sofa", [families[n % 3]], 5, n) for n in range(30)]
    doc = OV.accept(_canned_accept(tmp_path, monkeypatch, specs), CFG)
    kept = [d["uid"] for d in doc["accepted"]]
    assert len(kept) == 20 and doc["counts"]["over_type_limit"] == 10 and "over_style_limit" not in doc["counts"]
    first = {f"s{n:02d}" for n in range(15, 30)}                         # 5 per family, the most liked
    fill = {f"s{n:02d}" for n in range(10, 15)}                          # then by rank, family full or not
    assert set(kept) == first | fill
    filled = {d["uid"] for d in doc["accepted"] if d.get("style_fill")}
    assert filled == fill and all("fill pass" in d["style_note"] for d in doc["accepted"] if d.get("style_fill"))
    assert kept == sorted(kept, key=lambda u: -int(u[1:]))              # rank order (likes)
    refused = {d["uid"]: d for d in doc["refused"]}
    assert set(refused) == {f"s{n:02d}" for n in range(10)}
    assert all(d["code"] == "over_type_limit" for d in refused.values())
    assert "had 5 each in the first pass" in refused["s00"]["detail"]
    assert doc["limits"] == {"per_type_max": 20, "decor_per_type_max": 20, "per_family_max": 5, "style_fill": True}
    # Fewer than the limit: every model is kept, the style spread only orders them.
    specs = [(f"t{n:02d}", "objaverse", "furniture", "chair", ["modern"], 5, n) for n in range(8)]
    doc = OV.accept(_canned_accept(tmp_path / "few", monkeypatch, specs), CFG)
    assert len(doc["accepted"]) == 8 and sum(1 for d in doc["accepted"] if d.get("style_fill")) == 3


def test_accept_ranks_real_before_generated_then_by_quality_and_source_and_limits_decor_to_20(tmp_path, monkeypatch):
    specs = [("gen_sofa", "generated", "furniture", "sofa", ["modern"], 5, 0),
             ("obj_sofa", "objaverse", "furniture", "sofa", ["modern"], 5, 99),
             ("abo_sofa", "abo", "furniture", "sofa", ["modern"], 5, 0),
             ("abo_low", "abo", "furniture", "sofa", ["modern"], 4, 0)]
    specs += [(f"abo_more{n:02d}", "abo", "furniture", "sofa", ["modern"], 4, 0) for n in range(17)]
    specs += [(f"abo_rug{n:02d}", "abo", "decor", "rug", [OV.style_values()[n % 9]], 5, 0) for n in range(30)]
    out = _canned_accept(tmp_path, monkeypatch, specs)
    doc = OV.accept(out, CFG)
    sofas = [d["uid"] for d in doc["accepted"] if d["type"] == "sofa"]
    # Real models first (M8 pod L2: two generated Japandi sofas pushed real ones out), then mean quality, then abo,
    # objaverse: 21 real sofas fill the 20 places, the generated one never takes one of them.
    assert sofas[:3] == ["abo_sofa", "obj_sofa", "abo_low"] and len(sofas) == 20 and "gen_sofa" not in sofas
    assert next(d for d in doc["refused"] if d["uid"] == "gen_sofa")["code"] == "over_type_limit"
    rugs = [d for d in doc["accepted"] if d["type"] == "rug"]
    assert len(rugs) == 20 and all(d["kind"] == "decor" and d["decor_type"] == "rug" for d in rugs)
    assert doc["accepted_by_source"] == {"abo": 39, "objaverse": 1}
    assert doc["limits"] == {"per_type_max": 20, "decor_per_type_max": 20, "per_family_max": 5, "style_fill": True}
    # --sources: the real sources only (the prep job's first accept before the generation).
    real = OV.accept(out, CFG, sources=["abo", "objaverse"])
    assert "gen_sofa" not in {d["uid"] for d in real["accepted"] + real["refused"]}
    assert real["sources"] == ["abo", "objaverse"]
    assert OV.main(["accept", "--out", str(out), "--sources", "abo,nowhere"]) == OV.EXIT_SERVER
    # With room in the type, a generated model is kept after the real ones.
    small = [s for s in specs if s[0] in ("gen_sofa", "obj_sofa", "abo_sofa")]
    doc = OV.accept(_canned_accept(tmp_path / "room", monkeypatch, small), CFG)
    assert [d["uid"] for d in doc["accepted"]] == ["abo_sofa", "obj_sofa", "gen_sofa"]


# --------------------------------------------------------------------------
# Credits and notice
# --------------------------------------------------------------------------

def test_attribution_line_is_the_spec_line():
    line = OV.attribution_line("Oak Sofa", "Ann Author", "https://sketchfab.com/3d-models/abc", C.CC_BY, CFG)
    assert line == CC_BY_LINE
    cc0 = OV.attribution_line("Oak Sofa", "Ann Author", "https://sketchfab.com/3d-models/abc", C.LICENCE, CFG)
    assert "CC0 1.0 (https://creativecommons.org/publicdomain/zero/1.0/)" in cc0 and cc0.endswith("AI-retouched")


def test_odc_by_notice():
    text = OV.odc_by_notice(CFG)
    for words in ("Objaverse", "ODC Attribution License", "ODC-By 1.0", "https://opendatacommons.org/licenses/by/1-0/",
                  "21e4e14", "not MIT", "commercial use"):
        assert words in text


# --------------------------------------------------------------------------
# End to end: accept, catalogue, report
# --------------------------------------------------------------------------

def test_write_catalog_validates_merges_and_fills_the_cache(library):
    run_judges(library)
    acc = OV.accept(library.out, _m8_accept_cfg())
    # M8 limits, <= 3 per (type, style family) (docs/milestone8.md §2): four scandinavian sofas, the giant ranks last.
    expected = {library.uids[k] for k in ("sofa_cm", "sofa_m", "sofa_tv", "bed", "table")}
    assert {d["uid"] for d in acc["accepted"]} == expected
    assert [(d["uid"], d["code"]) for d in acc["refused"]] == [(library.uids["giant"], "over_style_limit")]
    # Milestone 9 limits (5 per family, then the fill pass): all four sofas are kept.
    acc = OV.accept(library.out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == expected | {library.uids["giant"]} and not acc["refused"]
    # The giant judged industrial by both is kept (its family has room).
    styles = {library.uids["giant"]: ["industrial"]}
    run_judges(library, clients={k: (lambda key: lambda images, prompt: dict(
        good_answers(library, key)(images, prompt), **({"styles": styles[Path(images[0]).stem]}
                                                        if Path(images[0]).stem in styles else {})))(k)
        for k in OV.MODEL_KEYS}, fresh=True)
    acc = OV.accept(library.out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == expected | {library.uids["giant"]}
    assets = library.tmp / "assets"
    doc = OV.write_catalog(library.out, assets, CFG, log=quiet)
    C.validate(doc, complete=False)
    entries = {e["uid"]: e for e in doc["entries"]}
    sofa = entries[library.uids["sofa_cm"]]
    for field in C.OBJAVERSE_FIELDS + ("licence_url", "has_mattress", "unit_scale", "front_axis_note"):
        assert field in sofa
    assert sofa["unit_scale"] == 0.01 and sofa["bbox_model_m"] == [2.0, 0.9, 0.85]
    assert sofa["bbox_min_m"] == [-1.0, -0.45, 0.0] and sofa["origin_offset"] == [0.0, 0.0, 0.0]
    assert sofa["front_axis"] == "-Y" and sofa["front_axis_confidence"] == "high"
    assert sofa["styles"] == ["scandinavian"] and sofa["attribution"] == OV.attribution_line(
        "Oak Sofa", "Ann Author", sofa["source_url"], C.CC_BY, CFG)
    assert sofa["glb"] == f"models/objaverse/{sofa['uid']}.glb" and sofa["id"] == f"objaverse_{sofa['uid']}"
    turned = entries[library.uids["sofa_tv"]]
    assert turned["front_axis"] == "+X" and turned["bbox_m"] == C.oriented_bbox(turned["bbox_model_m"], "+X")
    assert entries[library.uids["sofa_m"]]["licence"] == C.LICENCE
    # P2: the normalised giant keeps its factor and says so; its box is the normalised one (validate passed above).
    giant = entries[library.uids["giant"]]
    assert giant["unit_scale"] not in C.UNIT_SCALES and giant["unit_scale"] == pytest.approx(0.146385, rel=1e-4)
    assert giant["unit_note"].startswith("normalised by type (model units unknown)")
    assert giant["bbox_model_m"] == pytest.approx([2.049, 0.922, 0.871], abs=0.001)
    bed = entries[library.uids["bed"]]
    assert bed["type"] == "bed_double" and bed["has_mattress"] is True
    table = entries[library.uids["table"]]
    assert table["front_axis_confidence"] == "low" and table["has_mattress"] is None
    for e in doc["entries"]:
        cached = assets / e["glb"]
        assert cached.is_file() and OV.sha256_file(cached) == e["sha256_glb"]
    stored = json.loads((library.out / OV.CATALOG_NAME).read_text())
    assert stored["notice"] == OV.odc_by_notice(CFG) and stored["file_licence"] == "ODC-By-1.0"
    # merged into the Poly Haven catalogue: library models added, parametric types replaced
    base_dir = library.tmp / "furniture"
    base_dir.mkdir()
    shutil.copy(C.CATALOG_PATH, base_dir / "catalog.json")
    shutil.copy(library.out / OV.CATALOG_NAME, base_dir / "catalog_objaverse.json")
    merged = C.load(base_dir / "catalog.json")
    assert sofa["id"] in [e["id"] for e in merged.candidates("sofa")]
    assert merged.merged["models_added"] == 6


def test_write_catalog_refuses_a_changed_glb_and_writes_nothing_without_models(library):
    run_judges(library, clients={"glm": lambda *_: answer(quality=2)})
    OV.accept(library.out, CFG)
    assert OV.write_catalog(library.out, library.tmp / "assets", CFG, log=quiet) is None
    assert not (library.out / OV.CATALOG_NAME).exists()
    (library.out / "judge" / "answers_glm-4.6v-flash.json").unlink()
    run_judges(library)
    OV.accept(library.out, CFG)
    surv = OV.read_json(library.out / OV.SURVEY_NAME)
    victim = next(c for c in surv["candidates"] if c["uid"] == library.uids["sofa_m"])
    Path(victim["glb"]).write_bytes(b"changed")
    doc = OV.write_catalog(library.out, library.tmp / "assets", CFG, log=quiet)
    assert library.uids["sofa_m"] not in {e["uid"] for e in doc["entries"]}
    assert doc["refused_at_write"][0]["code"] == "glb_changed"


def test_report_lists_counts_refusals_credits_and_the_notice(library):
    run_judges(library, clients={"glm": lambda images, prompt: answer(
        front=OV.VIEW_SIDES.index(library.doc["objects"][Path(images[0]).stem]["geometric_front"])
        if library.doc["objects"][Path(images[0]).stem].get("geometric_front") else None,
        styles=["scandinavian"], quality=3 if Path(images[0]).stem == library.uids["sofa_tv"] else 5,
        mattress=True)})
    OV.accept(library.out, CFG)
    OV.write_catalog(library.out, library.tmp / "assets", CFG, log=quiet)
    assert OV.main(["report", "--out", str(library.out)]) == 0
    text = (library.out / OV.REPORT_NAME).read_text()
    assert OV.odc_by_notice(CFG) in text
    for heading in ("## Steps", "## Per type", "## Refusals by reason", "## Licence values seen",
                    "## Style coverage", "## Catalogue", "## Attribution", "## Refused after judging"):
        assert heading in text
    assert "| accept | quality |" in text and "| thumbnails | blender_error |" in text
    assert "| thumbnails | unit_none |" in text
    assert OV.attribution_line("Oak Sofa", "Ann Author", f"https://sketchfab.com/3d-models/{library.uids['sofa_cm']}",
                               C.CC_BY, CFG) in text
    assert "| `by` |" in text and "CC-BY-4.0" in text
    assert "type/family pairs" in text
    assert re.search(r"\| sofa \| 3\+\d+ \|", text)          # 3 scandinavian Objaverse sofas (with the normalised
    assert "| of which normalised by type (model units unknown) | 1 |" in text      # giant) + the Poly Haven ones


def test_report_before_the_survey(tmp_path):
    text = OV.report(tmp_path, CFG)
    assert "Survey not run." in text and "ODC Attribution License" in text


# --------------------------------------------------------------------------
# The Blender side with a stand-in bpy (the real one runs on the pod)
# --------------------------------------------------------------------------

class FakeVec(tuple):
    def __new__(cls, values):
        return super().__new__(cls, tuple(float(v) for v in values))

    def __sub__(self, other):
        return FakeVec(a - b for a, b in zip(self, other))

    def __neg__(self):
        return FakeVec(-a for a in self)

    def to_track_quat(self, track, up):
        assert (track, up) == ("-Z", "Y")
        return SimpleNamespace(to_euler=lambda: (0.0, 0.0, 0.0))


class FakeMatrix:
    def __init__(self, scale: float):
        self.scale = scale

    def __matmul__(self, co):
        return FakeVec(c * self.scale for c in co)


class FakeObject:
    def __init__(self, name, kind, data=None, verts=(), polys=(), scale=1.0):
        self.name, self.type, self.data = name, kind, data
        self.matrix_world = FakeMatrix(scale)
        self.material_slots = [SimpleNamespace(material=SimpleNamespace(node_tree=SimpleNamespace(nodes=[
            SimpleNamespace(type="TEX_IMAGE", image=SimpleNamespace(name="albedo.png"))])))]
        self._mesh = SimpleNamespace(vertices=[SimpleNamespace(co=v) for v in verts],
                                     polygons=[SimpleNamespace(vertices=p) for p in polys], color_attributes=[])
        self.location = self.rotation_euler = None
        self.hide_render = False

    def evaluated_get(self, _depsgraph):
        return self

    def to_mesh(self):
        return self._mesh

    def to_mesh_clear(self):
        pass


class FakeObjects(list):
    def new(self, name, data):
        return FakeObject(name, "CAMERA" if hasattr(data, "lens") else "LIGHT", data)

    def remove(self, ob, do_unlink=True):
        assert do_unlink
        super().remove(ob)


def fake_bpy(glbs: dict, rendered: list):
    """A bpy with just what ``_bl_thumbs`` uses; ``glbs`` maps a GLB path to (verts, faces, scale) or None."""
    objects = FakeObjects()
    prefs = SimpleNamespace(compute_device_type="NONE", get_devices=lambda: None,
                            devices=[SimpleNamespace(type="OPTIX", use=False), SimpleNamespace(type="CPU", use=True)])
    scene = SimpleNamespace(render=SimpleNamespace(image_settings=SimpleNamespace(), filepath=""),
                            cycles=SimpleNamespace(), camera=None, world=None,
                            collection=SimpleNamespace(objects=SimpleNamespace(link=objects.append)))

    def import_gltf(filepath, import_shading, import_scene_as_collection, import_select_created_objects):
        assert import_shading == "NORMALS" and import_scene_as_collection is False
        shape = glbs.get(filepath)
        if shape is None:
            raise RuntimeError("Error: invalid GLB")
        verts, faces, scale = shape
        objects.append(FakeObject("Sketchfab_model", "EMPTY"))
        objects.append(FakeObject("Object_2", "MESH", verts=verts, polys=faces, scale=scale))
        objects.append(FakeObject("Light", "LIGHT"))

    def render(write_still):
        from PIL import Image
        assert write_still and scene.camera is not None
        Path(scene.render.filepath).parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (scene.render.resolution_x, scene.render.resolution_y), (90, 90, 90)).save(
            scene.render.filepath)
        rendered.append(scene.render.filepath)

    return SimpleNamespace(
        ops=SimpleNamespace(wm=SimpleNamespace(read_factory_settings=lambda use_empty: None),
                            import_scene=SimpleNamespace(gltf=import_gltf),
                            render=SimpleNamespace(render=render)),
        context=SimpleNamespace(scene=scene, view_layer=SimpleNamespace(update=lambda: None),
                                evaluated_depsgraph_get=lambda: None,
                                preferences=SimpleNamespace(addons={"cycles": SimpleNamespace(preferences=prefs)})),
        data=SimpleNamespace(objects=objects, orphans_purge=lambda **kw: None,
                             worlds=SimpleNamespace(new=lambda name: SimpleNamespace(node_tree=None, color=None)),
                             cameras=SimpleNamespace(new=lambda name: SimpleNamespace(lens=0, sensor_width=0)),
                             lights=SimpleNamespace(new=lambda name, kind: SimpleNamespace(energy=0, angle=0))),
        app=SimpleNamespace(version_string="5.2.2 (stand-in)"),
    )


def cube(scale=1.0):
    pts = box(-1.0, -0.45, 0.0, 1.0, 0.45, 0.85)
    order = {p: i for i, p in enumerate(pts)}
    faces = [[order[(-1.0, -0.45, 0.0)], order[(1.0, -0.45, 0.0)], order[(1.0, -0.45, 0.85)],
              order[(-1.0, -0.45, 0.85)]]]
    return pts, faces, scale


def test_blender_side_measures_renders_and_survives_a_broken_glb(library, monkeypatch):
    import sys
    surv = OV.read_json(library.out / OV.SURVEY_NAME)
    by_uid = {c["uid"]: c for c in surv["candidates"]}
    good, broken = library.uids["sofa_cm"], library.uids["broken"]
    glbs = {by_uid[good]["glb"]: cube(scale=100.0)}
    rendered = []
    monkeypatch.setitem(sys.modules, "bpy", fake_bpy(glbs, rendered))
    monkeypatch.setitem(sys.modules, "mathutils", SimpleNamespace(Vector=FakeVec))
    work = library.tmp / "bl"
    calls = []

    def runner(_blender, jobs_path, _log, _timeout):
        calls.append(jobs_path)
        return OV.main(["blender-thumbs", str(jobs_path)])
    doc, rc = OV.thumbnails(library.out, work, CFG, runner=runner, log=quiet)     # a fresh work dir: all rendered
    assert rc == 0 and len(calls) == 1
    status = OV.read_json(work / "blender_status.json")
    assert status["device"] == "OPTIX" and status["blender"].startswith("5.2.2")
    assert set(status["done"]) == {good} and broken in status["failed"]     # the others have no stand-in GLB
    rec = doc["objects"][good]
    assert rec["status"] == "ready" and rec["unit"]["scale"] == 0.01
    assert rec["measure"]["extents_raw"] == pytest.approx([200.0, 90.0, 85.0])
    assert rec["measure"]["images"] == 1 and rec["measure"]["triangles"] == 2
    assert len(rendered) >= 4 and all(Path(p).is_file() for p in rendered)
    assert doc["objects"][broken]["code"] == "blender_error"
    assert "invalid GLB" in doc["objects"][broken]["detail"]
    jobs = OV.read_json(work / "blender_jobs.json")
    late = dict(jobs, deadline=1.0)
    OV.write_json(work / "late_jobs.json", late)
    assert OV._bl_thumbs(str(work / "late_jobs.json")) == OV.EXIT_DEADLINE
    assert OV.read_json(work / "blender_status.json")["left"] == [j["uid"] for j in jobs["objects"]]


def test_thumbnails_keep_24_per_type_after_the_bed_split(tmp_path):
    m = Mirror(tmp_path / "mirror")
    beds = [m.add("bed", likes=100 - n) for n in range(48)]
    hub = m.write()
    out = tmp_path / "lib"
    OV.survey(hub, out, CFG, log=quiet)
    double = box(-0.8, -1.0, 0, 0.8, 1.0, 0.5) + box(-0.8, 0.9, 0.5, 0.8, 1.0, 1.1)
    single = box(-0.45, -1.0, 0, 0.45, 1.0, 0.5) + box(-0.45, 0.9, 0.5, 0.45, 1.0, 1.1)
    shapes = {uid: ((single if n % 4 == 0 else double), []) for n, uid in enumerate(beds)}
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=fake_runner(shapes, []), log=quiet)
    objs = doc["objects"]
    ready = {t: [u for u in beds if objs[u]["status"] == "ready" and objs[u]["type"] == t]
             for t in ("bed_double", "bed_single")}
    assert len(ready["bed_single"]) == 12 and len(ready["bed_double"]) == 24
    over = [u for u in beds if objs[u].get("code") == "over_candidate_limit"]
    assert len(over) == 12 and all(objs[u]["type"] == "bed_double" for u in over)
    assert over == [u for u in beds if u not in ready["bed_single"]][24:]     # the lowest ranks go
    assert not (out / "thumbs" / "bed_double" / f"{over[0]}.jpg").exists()


# --------------------------------------------------------------------------
# Milestone 8: every source in one library (docs/milestone8.md §2)
# --------------------------------------------------------------------------

ABO_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "abo"
GEN_UID = "gen_chair_scandinavian_1_ab12cd34"


def quad_z(x0, y0, x1, y1, z):
    """A horizontal rectangle (world vertices) at height z."""
    return [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]


def bed_frame_shape(deck_z=0.35, slats=True):
    """A bed frame (metres, front -Y): rails, a headboard at +Y and, with ``slats``, a deck at ``deck_z``. The deck
    measurement is ``deck_height`` on its polygons (the real function on canned geometry)."""
    pts = box(-0.8, -1.0, 0.0, 0.8, 1.0, deck_z) + box(-0.8, 0.9, deck_z, 0.8, 1.0, 1.1)
    polys = [quad_z(-0.8, -1.0, 0.8, -0.95, deck_z), quad_z(-0.8, 0.85, 0.8, 0.9, deck_z),     # end rails
             quad_z(-0.8, -1.0, -0.75, 0.9, deck_z), quad_z(0.75, -1.0, 0.8, 0.9, deck_z)]     # side rails
    if slats:
        polys.append(quad_z(-0.75, -0.95, 0.75, 0.85, deck_z))
    mins, maxs = OV.bounds(pts)
    return pts, [], OV.deck_height(polys, mins, maxs, CFG["bed_frame"]["ray_offset"])


def decor_answer(ok=True, quality=5, styles=("modern", "scandinavian"), front=None):
    return {"is_single_object": True, "is_decor_type": ok, "photoreal_quality": quality, "styles": list(styles),
            "front_view": front}


@pytest.fixture()
def mixed(tmp_path):
    """A library of every source: the ABO survey of the canned metadata (GLBs from a fake fetcher), two Objaverse
    sofas (CC BY 4.0 and CC BY-NC 4.0) and one generated chair; thumbnails with a fake Blender and canned decks."""
    from wenart.assets import abo as A
    out = tmp_path / "lib"
    m = Mirror(tmp_path / "mirror")
    obj_by = m.add("sofa", likes=9, name="Oak Sofa")
    obj_nc = m.add("sofa", likes=8, licence="by-nc", name="NC Sofa")
    OV.survey(m.write(), out, CFG, log=quiet)
    n = [0]

    def fetcher(url, dest, max_bytes):
        n[0] += 1
        return make_glb(Path(dest), pad=4 * n[0])
    acfg = A.load_config()
    A.survey(A.Metadata(acfg, ABO_FIXTURE, download_missing=False), out, acfg, CFG, download_glbs=True,
             cache=tmp_path / "abo", fetcher=fetcher, workers=1, log=quiet)
    gen_glb = make_glb(tmp_path / "gen" / f"{GEN_UID}.glb", pad=400)
    OV.write_json(out / OV.SURVEY_FILES["generated"], {"kind": "generated_survey", "candidates": [{
        "uid": GEN_UID, "group": "chair", "types": ["chair"], "title": "generated chair (scandinavian)",
        "licence": "generated (TRELLIS.2-4B, MIT)", "licence_flag": None, "source": "generated", "kind": "furniture",
        "units_known": False, "style_hint": "scandinavian", "glb": str(gen_glb), "glb_sha256": OV.sha256_file(gen_glb),
        "glb_bytes": gen_glb.stat().st_size, "glb_info": OV.glb_info(gen_glb), "rank": 1,
        "generated": {"prompt": "a single scandinavian style chair, ...", "image_sha256": "c" * 64,
                      "model": "microsoft/TRELLIS.2-4B", "revision": "af44b45f2e35a493886929c6d786e563ec68364d",
                      "seed": 7}}]})
    chair = box(-0.25, -0.25, 0, 0.25, 0.25, 0.45) + box(-0.25, 0.2, 0.45, 0.25, 0.25, 0.9)
    uids = {"tisbury": "abo_B07B4SCB6T", "frame_full": "abo_B086VNNCMZ", "sofa": "abo_B072PZ4LVN",
            "loveseat": "abo_B075X4VQV1", "armchair": "abo_B073G7BVCT", "rug": "abo_B071777YN3",
            "rug2": "abo_B0719STLL8", "art": "abo_B073P5V3BJ", "plant": "abo_B07QD5G1KC", "side": "abo_B072ZLCB3M",
            "obj_by": obj_by, "obj_nc": obj_nc, "gen": GEN_UID}
    shapes = {
        uids["tisbury"]: bed_frame_shape(0.35),
        uids["frame_full"]: bed_frame_shape(0.30, slats=False),          # rails only: the rays miss
        uids["sofa"]: (sofa_points(), []),                               # 2 x 0.9 x 0.85 m, back at +Y
        uids["loveseat"]: ([(x * 0.76, y * 0.89, z) for x, y, z in sofa_points()], []),
        uids["armchair"]: ([(x * 0.4, y, z * 1.2) for x, y, z in sofa_points()], []),
        uids["rug"]: (box(-0.9, -0.6, 0, 0.9, 0.6, 0.02), []),
        uids["rug2"]: (box(-1.2, -0.4, 0, 1.2, 0.4, 0.02), []),
        uids["art"]: (box(-0.32, -0.03, 0, 0.32, 0.0, 1.46), []),
        uids["plant"]: (box(-0.11, -0.11, 0, 0.11, 0.11, 0.2), []),
        uids["side"]: (box(-0.7, -0.7, 0, 0.7, 0.7, 1.4), []),           # three times the listed box
        uids["obj_by"]: (scaled(sofa_points(), 100.0), []),
        uids["obj_nc"]: (sofa_points(), []),
        uids["gen"]: (scaled(chair, 10.0), []),
    }
    jobs: list = []
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=fake_runner(shapes, [], jobs), log=quiet)
    answers = {
        uids["tisbury"]: (answer(front=0, mattress=False), answer(front=0, mattress=False)),
        uids["frame_full"]: (answer(front=0, mattress=False), answer(front=0, mattress=False)),
        uids["sofa"]: (answer(front=0), answer(front=0)),
        uids["loveseat"]: (answer(front=2), answer(front=2)),           # both contradict the documented -Y
        uids["armchair"]: (answer(front=0), answer(front=None)),        # split: the documented front decides
        uids["rug"]: (decor_answer(), decor_answer()),
        uids["rug2"]: (decor_answer(), decor_answer(ok=False)),
        uids["art"]: (decor_answer(front=0), decor_answer(front=0)),
        uids["plant"]: (decor_answer(ok=False), decor_answer(ok=False)),    # an empty planter
        uids["obj_by"]: (answer(front=0), answer(front=0)),
        uids["obj_nc"]: (answer(front=0, styles=["industrial"]), answer(front=0, styles=["industrial"])),
        uids["gen"]: (answer(front=0, styles=["scandinavian"]), answer(front=0, styles=["scandinavian"])),
    }
    lib = SimpleNamespace(out=out, tmp=tmp_path, uids=uids, doc=doc, rc=rc, jobs=jobs, shapes=shapes)
    clients = {k: (lambda i: lambda images, _p: answers[Path(images[0]).stem][i])(i) for i, k in
               enumerate(OV.MODEL_KEYS)}
    lib.rcs = run_judges(lib, clients=clients)
    return lib


def test_load_candidates_merges_every_survey_file(mixed):
    cands = OV.load_candidates(mixed.out)
    by_source = {}
    for c in cands:
        by_source.setdefault(c["source"], []).append(c["uid"])
    assert set(by_source) == {"objaverse", "abo", "generated"}
    # 29 ABO candidates: the fixture's table lamp maps to table_lamp since Milestone 9 (28 before).
    assert by_source["generated"] == [GEN_UID] and len(by_source["abo"]) == 29 and len(by_source["objaverse"]) == 2
    assert [c["source"] for c in cands] == sorted((c["source"] for c in cands), key=list(OV.SURVEY_FILES).index)
    gen = next(c for c in cands if c["source"] == "generated")
    assert gen["decor_type"] is None and gen["extents_raw"] is None and gen["categories"] == []
    assert OV.load_candidates(mixed.out, sources=["generated"]) == [gen]
    # A uid in two survey files is refused (never guessed which is right).
    surv = OV.read_json(mixed.out / OV.SURVEY_FILES["generated"])
    surv["candidates"].append(dict(surv["candidates"][0], uid=mixed.uids["obj_by"]))
    OV.write_json(mixed.out / OV.SURVEY_FILES["generated"], surv)
    with pytest.raises(OV.UsageError, match="is a candidate of objaverse and generated"):
        OV.load_candidates(mixed.out)
    with pytest.raises(OV.UsageError, match="no survey file"):
        OV.load_candidates(mixed.tmp / "nowhere")


def test_units_known_documented_fronts_and_decks_in_the_thumbnails(mixed):
    objs, u = mixed.doc["objects"], mixed.uids
    assert mixed.rc == OV.EXIT_OK                       # objects without a shape: blender_error, not the step
    sofa = objs[u["sofa"]]
    assert sofa["status"] == "ready" and sofa["source"] == "abo" and sofa["units_known"] is True
    assert sofa["unit"]["scale"] == 1.0 and sofa["unit"]["known"] and sofa["unit"]["note"].startswith("units known")
    assert sofa["front_documented"] == "-Y" and "glTF +Z" in sofa["front_documented_note"]
    side = objs[u["side"]]                                                    # units known: refused, never normalised
    assert side["status"] == "refused" and side["code"] == "size_range" and "never normalised" in side["detail"]
    gen = objs[u["gen"]]
    assert gen["status"] == "ready" and gen["unit"]["normalised"] and gen["type"] == "chair"
    assert objs[u["obj_by"]]["unit"]["scale"] == 0.01 and objs[u["obj_nc"]]["licence_flag"] == "non_commercial"
    rug = objs[u["rug"]]
    assert rug["kind"] == "decor" and rug["decor_type"] == "rug" and rug["type"] == "rug" and "front_documented" \
        not in rug                                                            # rugs have no front
    assert objs[u["art"]]["front_rule"] == OV.DOCUMENTED_RULE and objs[u["art"]]["front_documented"] == "-Y"
    # Beds: the deck of 5 downward rays, in metres; only bed candidates are measured for it.
    bed = objs[u["tisbury"]]
    assert bed["deck_height_m"] == pytest.approx(0.35) and bed["deck"]["hits"] == 5
    assert objs[u["frame_full"]]["deck_height_m"] is None and objs[u["frame_full"]]["deck"]["hits"] == 0
    deck_jobs = {j["uid"] for j in mixed.jobs if j["deck"]}
    assert deck_jobs == {c["uid"] for c in OV.load_candidates(mixed.out) if OV.needs_deck(c)}
    notice = (mixed.out / "thumbs" / "NOTICE.md").read_text()
    assert "ODC Attribution License" in notice and "Amazon Berkeley Objects" in notice and "TRELLIS.2-4B" in notice
    assert f"`thumbs/sofa/{u['sofa']}.jpg`: " in notice


def test_a_bed_measured_before_m8_gets_its_deck_without_a_new_render(mixed):
    measure = mixed.tmp / "work" / "measure" / f"{mixed.uids['tisbury']}.json"
    rec = OV.read_json(measure)
    rec.pop("deck")
    OV.write_json(measure, rec)
    jobs: list = []
    calls: list = []
    doc, _rc = OV.thumbnails(mixed.out, mixed.tmp / "work", CFG, runner=fake_runner(mixed.shapes, calls, jobs),
                             log=quiet)
    tis = next(j for j in jobs if j["uid"] == mixed.uids["tisbury"])
    assert tis["render"] is False and tis["deck"] is True
    assert doc["objects"][mixed.uids["tisbury"]]["deck_height_m"] == pytest.approx(0.35)
    failed = {uid for uid, o in mixed.doc["objects"].items() if o.get("code") == "blender_error"}
    assert failed and {j["uid"] for j in jobs if j["render"]} == failed     # only the ones Blender could not do


def test_decor_and_furniture_questions(mixed):
    doc = OV.read_requests(mixed.out)
    items = {i["context"]["uid"]: i for i in doc["items"]}
    rug = items[mixed.uids["rug"]]
    assert rug["context"]["kind"] == "decor" and rug["context"]["decor_type"] == "rug"
    assert "offered as rug decor" in rug["prompt"] and "is_decor_type: true when it is one flat floor rug" in rug["prompt"]
    plant = items[mixed.uids["plant"]]
    assert "an empty pot, planter or vase is not one" in plant["prompt"]
    assert "picture side" in items[mixed.uids["art"]]["prompt"]
    sofa = items[mixed.uids["sofa"]]
    # The furniture question is the M7 one (stored M7 answers stay current).
    assert sofa["prompt"] == OV.judge_prompt("sofa", sofa["context"]["dims_m"], True, False)
    assert sofa["context"]["source"] == "abo" and sofa["context"]["kind"] == "furniture"
    assert OV.judge_schema("decor")["required"] == ["is_single_object", "is_decor_type", "photoreal_quality",
                                                    "styles", "front_view"]
    assert "matches_type" not in OV.judge_schema("decor")["properties"]
    assert not OV.valid_judgement(answer(), "decor") and OV.valid_judgement(decor_answer(), "decor")
    assert mixed.rcs["qwen"] == 0 and mixed.rcs["glm"] == 0
    status = OV.judge_status(mixed.out)
    assert status["complete"] and status["items"] == len(items)


def test_accept_of_every_source(mixed):
    acc = OV.accept(mixed.out, CFG)
    u = mixed.uids
    got = {d["uid"]: d for d in acc["accepted"]}
    codes = {d["uid"]: d["code"] for d in acc["refused"]}
    assert set(got) == {u[k] for k in ("tisbury", "sofa", "armchair", "rug", "art", "obj_by", "obj_nc", "gen")}
    assert codes[u["frame_full"]] == "no_deck" and "0 of 5 downward rays" in next(
        d["detail"] for d in acc["refused"] if d["uid"] == u["frame_full"])
    assert codes[u["loveseat"]] == "front_not_agreed" and codes[u["rug2"]] == "not_decor_type"
    assert codes[u["plant"]] == "not_decor_type"
    bed = got[u["tisbury"]]
    assert bed["bed_frame"] is True and bed["has_mattress"] is False and bed["deck_height_m"] == pytest.approx(0.35)
    assert got[u["sofa"]]["bed_frame"] is None and got[u["sofa"]]["front_axis"] == "-Y"
    assert "did not agree" in got[u["armchair"]]["front_axis_note"] and got[u["armchair"]]["front_axis"] == "-Y"
    assert got[u["art"]]["front_axis"] == "-Y" and got[u["art"]]["front_axis_confidence"] == "high"
    assert got[u["rug"]]["kind"] == "decor" and got[u["rug"]]["front_axis_confidence"] == "low"
    assert got[u["obj_nc"]]["licence_flag"] == "non_commercial" and got[u["gen"]]["source"] == "generated"
    assert acc["accepted_by_source"] == {"abo": 5, "generated": 1, "objaverse": 2}
    real = OV.accept(mixed.out, CFG, sources=["abo", "objaverse"])
    assert u["gen"] not in {d["uid"] for d in real["accepted"]} and len(real["accepted"]) == 7


def test_bed_frame_rules_on_canned_decks():
    bed = dict(obj("bed_double"), deck_height_m=0.32, deck={"hits": 4, "hits_raw": [0.32] * 4 + [None]})
    no = answer(mattress=False)
    dec = OV.decide(bed, {"qwen": no, "glm": no}, CFG)
    assert dec["accepted"] and dec["bed_frame"] is True and dec["has_mattress"] is False and dec["deck_height_m"] == 0.32
    assert "median of 4 of 5" in dec["deck_note"]
    for deck, why in ((dict(bed, deck_height_m=0.03), "outside 0.08-0.9 m"),        # the floor rail
                      (dict(bed, deck_height_m=2.0), "outside 0.08-0.9 m"),         # a canopy
                      (dict(bed, deck={"hits": 2, "hits_raw": [0.3, 0.3, None, None, None]}), "2 of 5")):
        refused = OV.decide(deck, {"qwen": no, "glm": no}, CFG)
        assert refused["code"] == "no_deck" and why in refused["detail"], refused
    yes = answer(mattress=True)
    kept = OV.decide(dict(bed, deck_height_m=None), {"qwen": yes, "glm": yes}, CFG)
    assert kept["accepted"] and kept["has_mattress"] is True and kept["bed_frame"] is False


def test_deck_height_on_canned_geometry():
    """Five rays straight down inside the inner 50 % of the footprint; each hit is the topmost surface above its
    point; the median of the hits above the box bottom."""
    mins, maxs = [-1.0, -1.0, 0.0], [1.0, 1.0, 1.0]
    pts = OV.deck_points(mins, maxs, 0.2)
    assert pts == [(0.0, 0.0), (-0.4, -0.4), (0.4, -0.4), (-0.4, 0.4), (0.4, 0.4)]
    assert all(abs(x) < 0.5 and abs(y) < 0.5 for x, y in pts)                       # inside the inner 50 %
    # Slats along x at y = -0.4 and 0.0 (z 0.30) and a bottom bar under everything (z 0.05): three rays meet a slat.
    slats = [quad_z(-1, -0.45, 1, -0.35, 0.30), quad_z(-1, -0.05, 1, 0.05, 0.30)]
    bar = [quad_z(-1, -1, 1, 1, 0.05)]
    deck = OV.deck_height(slats + bar, mins, maxs)
    assert deck["hits_raw"] == [0.3, 0.3, 0.3, 0.05, 0.05] and deck["height_raw"] == 0.3 and deck["hits"] == 5
    # The topmost surface counts (a mattress over the slats); a vertical face is never a hit; no polygon: no hit.
    top = OV.deck_height(slats + bar + [quad_z(-1, -1, 1, 1, 0.55)], mins, maxs)
    assert top["height_raw"] == 0.55
    wall = [[(0.0, -1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 1.0), (0.0, -1.0, 1.0)]]
    assert OV.deck_height(wall, mins, maxs)["hits"] == 0
    assert OV.deck_height([], mins, maxs) == {"points": [[0.0, 0.0], [-0.4, -0.4], [0.4, -0.4], [-0.4, 0.4],
                                                         [0.4, 0.4]], "hits_raw": [None] * 5, "hits": 0,
                                              "height_raw": None, "offset": 0.2}
    # A box offset from the origin: the hits are measured from its bottom.
    shifted = OV.deck_height([quad_z(9, 9, 11, 11, 3.4)], [9, 9, 3.0], [11, 11, 4.0])
    assert shifted["height_raw"] == pytest.approx(0.4)


def test_write_catalog_of_every_source(mixed):
    OV.accept(mixed.out, CFG)
    assets = mixed.tmp / "assets"
    doc = OV.write_catalog(mixed.out, assets, CFG, log=quiet)
    C.validate(doc, complete=False)
    u = mixed.uids
    entries = {e["uid"]: e for e in doc["entries"]}
    decor = {e["uid"]: e for e in doc["decor"]}
    assert set(decor) == {u["rug"], u["art"]} and set(entries) == {u[k] for k in ("tisbury", "sofa", "armchair",
                                                                                     "obj_by", "obj_nc", "gen")}
    assert doc["sources"] == ["abo", "objaverse", "generated"] and doc["kind"] == "library_catalog"
    assert doc["file_licences"] == ["ODC-By-1.0", "CC-BY-4.0"] and len(doc["notices"]) == 3
    assert doc["counts"]["licence_flags"] == {"non_commercial": 1} and doc["counts"]["bed_frames"] == 1
    for e in doc["entries"] + doc["decor"]:
        cached = assets / e["glb"]
        assert e["glb"] == f"models/{e['source']}/{e['uid']}.glb" and OV.sha256_file(cached) == e["sha256_glb"]
    sofa = entries[u["sofa"]]
    assert sofa["id"] == u["sofa"] and sofa["source"] == "abo" and sofa["unit_scale"] == 1.0 and sofa["units_known"]
    assert sofa["abo_3dmodel_id"] == "B072PZ4LVN" and sofa["attribution"].endswith("AI-retouched")
    assert sofa["attribution"].startswith('"Amazon Brand – Rivet Revolve Modern Upholstered Sofa Couch')
    assert sofa["licence"] == C.CC_BY and sofa["licence_flag"] is None and sofa["quality"] == [5, 5]
    bed = entries[u["tisbury"]]
    assert bed["bed_frame"] is True and bed["has_mattress"] is False and bed["deck_height_m"] == pytest.approx(0.35)
    assert C.bed_usable(bed) and not C.has_mattress(bed)
    nc = entries[u["obj_nc"]]
    assert nc["id"] == f"objaverse_{u['obj_nc']}" and nc["licence"] == "CC-BY-NC-4.0"
    assert nc["licence_flag"] == "non_commercial" and "CC BY-NC 4.0" in nc["attribution"]
    gen = entries[u["gen"]]
    assert gen["source"] == "generated" and gen["licence"].startswith("generated") and gen["licence_flag"] is None
    assert gen["generated"]["seed"] == 7 and gen["unit_note"].startswith(OV.NORMALISED_NOTE)
    rug = decor[u["rug"]]
    assert rug["type"] == "decor_rug" and rug["kind"] == "decor" and rug["decor_type"] == "rug"
    # catalog.load merges the library file (decor too) and prefers it over an M7 catalog_objaverse.json.
    base_dir = mixed.tmp / "furniture"
    base_dir.mkdir()
    shutil.copy(C.CATALOG_PATH, base_dir / "catalog.json")
    shutil.copy(mixed.out / OV.CATALOG_NAME, base_dir / "catalog_library.json")
    (base_dir / "catalog_objaverse.json").write_text("{}")                       # ignored while the library is there
    merged = C.load(base_dir / "catalog.json")
    assert merged.merged["source"] == "catalog_library.json" and merged.merged["decor_added"] == 2
    assert [e["id"] for e in merged.decor_candidates("rug")] == [u["rug"]]
    assert merged.decor_candidates("cushion") == [] and merged.entry(u["art"])["decor_type"] == "wall_art"
    assert u["sofa"] in [e["id"] for e in merged.candidates("sofa")]
    assert any(e["id"] == "throw_pillows_01" for e in merged.decor)              # Poly Haven decor stays


def test_write_catalog_takes_the_assets_copy_when_the_survey_cache_is_gone(mixed):
    """A later pod (L2) has not downloaded the real models again: the GLB an earlier write-catalog put into the
    assets cache on the volume (same sha256) is used; without it the model is refused glb_changed."""
    OV.accept(mixed.out, CFG)
    assets = mixed.tmp / "assets"
    OV.write_catalog(mixed.out, assets, CFG, log=quiet)
    cand = next(c for c in OV.load_candidates(mixed.out) if c["uid"] == mixed.uids["sofa"])
    Path(cand["glb"]).unlink()
    doc = OV.write_catalog(mixed.out, assets, CFG, log=quiet)
    assert mixed.uids["sofa"] in {e["uid"] for e in doc["entries"]} and doc["refused_at_write"] == []
    (assets / "models" / "abo" / f"{mixed.uids['sofa']}.glb").unlink()
    doc = OV.write_catalog(mixed.out, assets, CFG, log=quiet)
    assert doc["refused_at_write"] == [{"uid": mixed.uids["sofa"], "code": "glb_changed", "detail": cand["glb"]}]


def test_report_of_every_source(mixed):
    OV.accept(mixed.out, CFG)
    OV.write_catalog(mixed.out, mixed.tmp / "assets", CFG, log=quiet)
    text = OV.report(mixed.out, CFG)
    for heading in ("## Sources", "## Steps", "## Per type", "## Refusals by reason", "## Licence values seen",
                    "## ABO mapping", "## Licence flags (catalogue)", "## Style coverage", "## Beds", "## Catalogue",
                    "## Attribution", "## Refused after judging"):
        assert heading in text, heading
    assert "| abo | survey_abo.json | 29 | 29 |" in text and "| generated | survey_generated.json | 1 | 1 |" in text
    assert "| CC-BY-NC-4.0 | non_commercial | 1 |" in text and "(licence flag: non_commercial)" in text
    assert OV.odc_by_notice(CFG) in text and "Amazon Berkeley Objects" in text and OV.GENERATED_NOTICE in text
    assert "| accept | no_deck |" in text and "| thumbnails | size_range |" in text
    assert f"| `{mixed.uids['tisbury']}` | bed_double | abo | False | True | 0.35 |" in text
    for e in OV.read_json(mixed.out / OV.CATALOG_NAME)["entries"]:
        assert e["attribution"] in text


# --------------------------------------------------------------------------
# The catalogue of every source (wenart/furniture/catalog.py; docs/milestone8.md §2, §7)
# --------------------------------------------------------------------------

def lib_entry(source, uid, ftype, dims=(1.0, 0.5, 0.8), licence=None, **extra):
    """A minimal valid library entry of ``source`` (furniture, or decor for a ``decor_<type>`` type)."""
    w, d, h = dims
    e = {"id": f"objaverse_{uid}" if source == "objaverse" else uid, "type": ftype, "source": source,
         "licence": licence or {"abo": C.CC_BY, "generated": "generated (TRELLIS.2-4B, MIT)"}.get(source, C.CC_BY),
         "bbox_m": [w, d, h], "bbox_model_m": [w, d, h], "bbox_min_m": [-w / 2, -d / 2, 0.0],
         "bbox_max_m": [w / 2, d / 2, h], "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
         "front_axis_confidence": "high", "glb": f"models/{source}/{uid}.glb", "sha256_glb": "ab" * 32, "uid": uid,
         "styles": ["modern"], "style_note": "both judges", "title": f"Model {uid}", "author": "Amazon.com",
         "source_url": f"https://example.org/{uid}", "licence_url": "https://creativecommons.org/licenses/by/4.0/",
         "via": "Amazon Berkeley Objects (CC BY 4.0)", "attribution": f'"Model {uid}" by Amazon.com', "quality": [5, 4]}
    e["licence_flag"] = C.licence_flag_of(e["licence"])
    if source == "generated":
        e["generated"] = {"prompt": "p", "image_sha256": "c" * 64, "model": "microsoft/TRELLIS.2-4B", "revision": "r",
                          "seed": 1}
    if ftype.startswith("decor_"):
        e.update(kind="decor", decor_type=ftype[len("decor_"):], front_axis_confidence="low")
    elif ftype in C.BED_TYPES:
        e["has_mattress"] = True
    e.update(extra)
    return e


def test_catalogue_validation_of_every_source():
    good = {"entries": [lib_entry("abo", "abo_A1", "sofa", (2.0, 0.9, 0.85)),
                        lib_entry("objaverse", "u1", "chair", (0.5, 0.5, 0.9), licence="CC-BY-NC-4.0"),
                        lib_entry("objaverse", "u2", "desk", licence="unknown"),
                        lib_entry("generated", "gen_chair_modern_1_ab12cd34", "chair", (0.5, 0.5, 0.9),
                                  author="", source_url="", attribution=""),
                        lib_entry("abo", "abo_B1", "bed_double", (1.6, 2.1, 0.9), has_mattress=False,
                                  bed_frame=True, deck_height_m=0.32)],
            "decor": [lib_entry("abo", "abo_R1", "decor_rug", (2.0, 1.4, 0.02))]}
    C.validate(good, complete=False)
    assert C.validate({"entries": [], "decor": good["decor"]}, complete=False) is None   # decor only

    def broken(where, i, match=None, **change):
        d = json.loads(json.dumps(good))
        d[where][i].update(change)
        for k, v in list(change.items()):
            if v is KeyError:
                d[where][i].pop(k)
        with pytest.raises(C.CatalogError, match=match):
            C.validate(d, complete=False)

    broken("entries", 0, "abo/CC0", licence="CC0", licence_flag=None)               # ABO is CC BY 4.0
    broken("entries", 0, "credit line", author="")
    broken("entries", 1, "licence_flag", licence_flag=None)                          # a flagged licence's flag
    broken("entries", 1, "licence_flag", licence_flag=KeyError)
    broken("entries", 1, "credit line", attribution="")                             # any non-CC0 licence: credit
    broken("entries", 0, "licence_flag", licence_flag="non_commercial")              # CC BY 4.0: no flag
    broken("entries", 1, "is not allowed", licence="CC BY-NC", licence_flag="unknown")
    broken("entries", 3, "generated", licence="MIT", licence_flag=None)
    broken("entries", 3, "generated record", generated={"prompt": "p"})
    broken("entries", 3, "missing field", generated=KeyError)
    broken("entries", 0, "at least one style", styles=[])
    broken("entries", 0, "kind furniture", kind="decor")
    broken("entries", 0, "decor_type", decor_type="rug")
    broken("entries", 0, "quality", quality=[5])
    broken("entries", 0, "quality", quality=[6, 5])
    broken("entries", 4, "deck_height_m", deck_height_m=KeyError)                   # a frame needs its deck
    broken("entries", 4, "no mattress", has_mattress=True)
    broken("entries", 4, "positive", deck_height_m=-0.1)
    broken("entries", 0, "beds only", bed_frame=True, deck_height_m=0.3)
    broken("decor", 0, "decor_type", decor_type="lamp")
    broken("decor", 0, "has type decor_rug", type="decor_cushion")
    broken("decor", 0, "needs kind decor", kind=KeyError, decor_type=None)
    d = json.loads(json.dumps(good))
    d["decor"].append(dict(d["decor"][0]))
    with pytest.raises(C.CatalogError, match="duplicate id"):
        C.validate(d, complete=False)
    # The M7 Objaverse entries (no licence_flag, CC0 / CC BY 4.0) stay valid.
    m7 = OV.read_json(C.objaverse_path(C.CATALOG_PATH))
    if m7 is not None:
        C.validate(m7, complete=False)


def test_catalogue_load_merges_the_library_file_with_decor(tmp_path):
    main = tmp_path / "catalog.json"
    shutil.copy(C.CATALOG_PATH, main)
    assert C.extra_path(main) is None and C.load(main).merged == {}
    old = {"entries": [lib_entry("objaverse", "u9", "chair", (0.5, 0.5, 0.9), licence="CC0", author="a",
                                 attribution="x")]}
    C.objaverse_path(main).write_text(json.dumps(old))
    assert C.load(main).merged["source"] == "catalog_objaverse.json"                    # the M7 fallback
    lib = {"entries": [lib_entry("abo", "abo_A1", "sofa", (2.0, 0.9, 0.85)),
                       lib_entry("abo", "abo_B1", "bed_single", (1.0, 2.0, 0.7), has_mattress=False, bed_frame=True,
                                 deck_height_m=0.3)],
           "decor": [lib_entry("abo", "abo_R1", "decor_rug", (2.0, 1.4, 0.02)),
                     lib_entry("abo", "abo_P1", "decor_plant", (0.4, 0.4, 1.0)),
                     lib_entry("abo", "abo_R2", "decor_rug", (3.0, 2.0, 0.02))]}
    C.library_path(main).write_text(json.dumps(lib))
    cat = C.load(main)
    assert C.extra_path(main) == tmp_path / "catalog_library.json"
    assert cat.merged == {"source": "catalog_library.json", "models_added": 2, "parametric_replaced": ["bed_single"],
                          "decor_added": 3}
    assert "objaverse_u9" not in cat.ids()                                               # only one file is merged
    assert [e["id"] for e in cat.decor_candidates("rug")] == ["abo_R1", "abo_R2"]
    assert [e["id"] for e in cat.decor_candidates("plant")] == ["abo_P1"] and cat.decor_candidates("wall_art") == []
    assert cat.entry("abo_R2")["decor_type"] == "rug" and cat.candidates("sofa")[-1]["id"] == "abo_A1"
    frame = cat.entry("abo_B1")
    assert C.bed_usable(frame) and not C.has_mattress(frame)
    assert not C.bed_usable(dict(frame, bed_frame=False)) and C.bed_usable(cat.entry("abo_A1"))
    assert C.load(main, library=False).merged == {}
    assert C.load(main, library=C.objaverse_path(main)).merged["source"] == "catalog_objaverse.json"
    # An id in both files is refused (the merge keeps ids unique).
    lib["decor"][0]["id"] = cat.models[0]["id"]
    C.library_path(main).write_text(json.dumps(lib))
    with pytest.raises(C.CatalogError, match="duplicate id"):
        C.load(main)


def test_a_candidate_whose_uid_is_no_plain_id_is_refused_visibly(mixed):
    """The cache path models/<source>/<uid>.glb needs a plain id: a generated uid with a space is refused bad_uid in
    the thumbnails (never a failed fetch on the full run)."""
    surv = OV.read_json(mixed.out / OV.SURVEY_FILES["generated"])
    bad = dict(surv["candidates"][0], uid="gen_sofa_modern minimal_1_ab12cd34", group="sofa", types=["sofa"])
    surv["candidates"].append(bad)
    OV.write_json(mixed.out / OV.SURVEY_FILES["generated"], surv)
    doc, _rc = OV.thumbnails(mixed.out, mixed.tmp / "work", CFG, runner=fake_runner(mixed.shapes, []), log=quiet)
    rec = doc["objects"][bad["uid"]]
    assert rec["status"] == "refused" and rec["code"] == "bad_uid" and doc["counts"]["bad_uid"] == 1
    assert doc["objects"][GEN_UID]["status"] == "ready"
