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
    assert pre["per_type_limit"] <= 8
    assert CFG["units"] == [1.0, 0.01, 0.0254, 0.001]
    assert CFG["dataset"]["revision"] == "21e4e142159e2153706c23a3a02e55cec5591cea"
    assert CFG["accept"] == {"min_quality": 4, "per_type_max": 6}
    table, _tol = OV.load_size_table()
    mapped = {t for spec in CFG["categories"].values() for t in spec["types"]}
    for t in mapped:
        assert t in C.FURNITURE_TYPES and t in CFG["types"] and t in table and t in OV.TYPE_WORDS
    for name in ("tv_unit", "kitchen_counter", "stair"):            # no LVIS category: parametric
        assert name not in mapped
    frontless = {t for t, spec in CFG["types"].items() if spec["front"] == "none"}
    assert frontless == {"table_dining", "table_coffee", "floor_lamp", "potted_plant"} & mapped


def test_licence_strings_accept_only_cc0_and_cc_by():
    lic = CFG["licences"]
    assert set(lic["accept"]) == {C.LICENCE, C.CC_BY}
    accepted = {s.casefold() for v in lic["accept"].values() for s in v}
    refused = {s.casefold() for s in lic["refuse"]}
    assert not accepted & refused
    for s in accepted:                                    # no NC, ND, SA spelling among the accepted
        assert not any(tok in s.replace(" ", "-").split("-") for tok in ("nc", "nd", "sa"))
    assert {"by-nc", "by-sa", "by-nc-sa", "by-nd", "by-nc-nd"} <= refused
    assert lic["urls"][C.CC_BY] == "https://creativecommons.org/licenses/by/4.0/"


@pytest.mark.parametrize("raw, expect", [
    ("by", (C.CC_BY, "")), (" BY ", (C.CC_BY, "")), ("cc0", (C.LICENCE, "")), ("CC0", (C.LICENCE, "")),
    ("CC-BY 4.0", (C.CC_BY, "")), ({"slug": "by", "label": "CC Attribution"}, (C.CC_BY, "")),
    ("by-nc", (None, "licence_refused")), ("by-sa", (None, "licence_refused")),
    ("by-nc-sa", (None, "licence_refused")), ("free-st", (None, "licence_refused")),
    ("CC-BY-NC 4.0", (None, "licence_refused")), ("cc-by-4.0-maybe", (None, "licence_unknown")),
    ("", (None, "licence_missing")), (None, (None, "licence_missing")), (3, (None, "licence_missing")),
])
def test_licence_classification(raw, expect):
    name, code, _detail = OV.classify_licence(raw, CFG)
    assert (name, code) == expect


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
    ok_by = m.add("sofa", licence="by", likes=9)
    ok_cc0 = m.add("sofa", licence="cc0", likes=5)
    vertex = m.add("sofa", textured=False, colours=True, likes=1)
    refused = {
        m.add("sofa", licence="by-nc"): "licence_refused",
        m.add("sofa", licence="by-sa"): "licence_refused",
        m.add("sofa", licence="free-st"): "licence_refused",
        m.add("sofa", licence="mystery"): "licence_unknown",
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
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    cands = {c["uid"]: c for c in doc["candidates"]}
    assert set(cands) == {ok_by, ok_cc0, vertex, both}
    assert [c["uid"] for c in doc["candidates"] if c["group"] == "sofa"] == [ok_by, ok_cc0, vertex]   # likes
    assert cands[ok_by]["licence"] == C.CC_BY and cands[ok_cc0]["licence"] == C.LICENCE
    assert sorted(cands[both]["categories"]) == ["armoire", "wardrobe"]
    for c in cands.values():
        assert len(c["glb_sha256"]) == 64 and Path(c["glb"]).is_file()
        assert c["title"] and c["author"] == "Ann Author" and c["source_url"].startswith("https://")
    got = {r["uid"]: r["code"] for r in doc["refused"]}
    assert got == refused
    assert doc["licence_values"]["by"] >= 1 and doc["licence_values"]["by-nc"] == 1
    assert "bathtub" in doc["lvis"]["missing"] and doc["lvis"]["found"]["sofa"] >= 15
    assert (tmp_path / "lib" / OV.SURVEY_NAME).is_file()
    assert doc["counts"]["sofa"]["candidates"] == 3


def test_survey_ranks_and_keeps_at_most_eight_per_type(tmp_path):
    m = Mirror(tmp_path / "mirror")
    chairs = [m.add("chair", likes=n, views=100 - n) for n in range(12)]
    tie_a = m.add("desk", likes=3, views=10)
    tie_b = m.add("desk", likes=3, views=20)
    beds = [m.add("bed", likes=n) for n in range(20)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "chair"]
    assert chosen == list(reversed(chairs))[:8]            # likes descending
    assert doc["counts"]["chair"]["not_selected"] == 4
    assert [c["uid"] for c in doc["candidates"] if c["group"] == "desk"] == [tie_b, tie_a]   # then views
    bed_group = OV.group_key(["bed_double", "bed_single"])
    assert sum(1 for c in doc["candidates"] if c["group"] == bed_group) == 16   # 8 per bed type before the split
    assert len(beds) == 20


def test_survey_lamp_ranks_floor_lamps_first(tmp_path):
    m = Mirror(tmp_path / "mirror")
    table_lamps = [m.add("lamp", likes=50 + n, name=f"Desk lamp {n}") for n in range(9)]
    floor = m.add("lamp", likes=1, name="Arc lamp", tags=("floor lamp",))
    standing = m.add("lamp", likes=0, name="Standing lamp")
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "floor_lamp"]
    assert chosen[:2] == [floor, standing] and len(chosen) == 8
    assert table_lamps[-1] in chosen and table_lamps[0] not in chosen


def test_survey_tries_the_next_rank_when_a_download_fails_the_file_checks(tmp_path):
    m = Mirror(tmp_path / "mirror")
    plain = [m.add("toilet", likes=100 + n, textured=False) for n in range(3)]
    good = [m.add("toilet", likes=n) for n in range(9)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, log=quiet)
    chosen = [c["uid"] for c in doc["candidates"] if c["group"] == "toilet"]
    assert len(chosen) == 8 and not set(chosen) & set(plain)
    assert doc["counts"]["toilet"]["tried"] == 11 and doc["counts"]["toilet"]["not_selected"] == 1
    assert sorted(good, reverse=True)[:8] == chosen


def test_survey_without_download_lists_the_top_of_the_ranking(tmp_path):
    m = Mirror(tmp_path / "mirror")
    uids = [m.add("sofa", likes=n, glb=False) for n in range(10)]
    hub = m.write()
    doc = OV.survey(hub, tmp_path / "lib", CFG, download=False, log=quiet)
    assert [c["uid"] for c in doc["candidates"]] == list(reversed(uids))[:8]
    assert all("glb" not in c for c in doc["candidates"]) and doc["downloaded"] is False


def test_survey_cli_with_a_mirror(tmp_path):
    m = Mirror(tmp_path / "mirror")
    m.add("sofa")
    m.write()
    out = tmp_path / "lib"
    assert OV.main(["survey", "--mirror", str(tmp_path / "mirror"), "--out", str(out)]) == 0
    assert len(OV.read_json(out / OV.SURVEY_NAME)["candidates"]) == 1
    empty = Mirror(tmp_path / "empty")
    empty.add("sofa", licence="by-nc")
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
    none = OV.guess_unit([5.0, 5.0, 5.0], ["sofa"], CFG, table, tol)
    assert not none["ok"] and none["code"] == "unit_none"
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
    assert OV.guess_unit([0.40, 0.40, 1.65], ["floor_lamp"], CFG, table, tol)["ok"]
    table_lamp = OV.guess_unit([0.30, 0.30, 0.55], ["floor_lamp"], CFG, table, tol)
    assert not table_lamp["ok"] and table_lamp["code"] == "unit_none"


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


def fake_runner(shapes: dict, calls: list):
    """A runner that writes what the Blender side writes: measure/<uid>.json and the four views."""
    def run(_blender, jobs_path, _log, _timeout):
        jobs = json.loads(Path(jobs_path).read_text())
        calls.append([j["uid"] for j in jobs["objects"]])
        for n, job in enumerate(jobs["objects"]):
            shape = shapes.get(job["uid"])
            rec = {"uid": job["uid"], "glb": job["glb"], "glb_sha256": job["glb_sha256"], "device": "OPTIX"}
            if shape is None:
                rec.update(ok=False, error="RuntimeError: no mesh objects in the GLB")
            else:
                points, polys = shape
                rec.update(ok=True, stats=OV.front_stats(points, polys), vertices=len(points), triangles=4000,
                           mesh_objects=1, images=1, colour_attributes=0, seconds=1.0)
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
    """A surveyed and thumbnailed library: sofas in cm and m, a bed, a dining table, a broken GLB, a giant."""
    m = Mirror(tmp_path / "mirror")
    uids = {
        "sofa_cm": m.add("sofa", likes=9, name="Oak Sofa"),
        "sofa_m": m.add("sofa", likes=8, licence="cc0", name="Grey Sofa"),
        "sofa_tv": m.add("sofa", likes=7, name="Turned Sofa"),
        "bed": m.add("bed", likes=5, name="Bed"),
        "table": m.add("dining_table", likes=4, name="Table"),
        "broken": m.add("sofa", likes=3, name="Broken"),
        "giant": m.add("sofa", likes=2, name="Giant"),
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
    assert objs[u["giant"]]["code"] == "unit_none"
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
                dict(good, extra=1), {k: v for k, v in good.items() if k != "styles"},
                dict(good, styles=["modern", "modern"]), None):
        assert not OV.valid_judgement(bad), bad
    assert OV.judge_schema()["additionalProperties"] is False


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
        error = None if OV.valid_judgement(data) else "schema: invalid"
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


def run_judges(library, clients=None):
    clients = clients or {}
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
    assert rcs["qwen"] == 0 and rcs["glm"] == 0 and rcs["qwen_calls"] == 5
    store = json.loads((library.out / "judge" / "answers_qwen3-vl-8b.json").read_text())
    assert store["model_key"] == "qwen" and store["model"] == "Qwen/Qwen3-VL-8B-Instruct"
    assert sorted(store["calls"]) == sorted(f"lib_{u}" for u, o in library.doc["objects"].items()
                                            if o["status"] == "ready")
    again = run_judges(library)
    assert again["qwen"] == 0 and again["qwen_calls"] == 0          # all reused, no client made
    status = OV.judge_status(library.out)
    assert status["complete"] and status["models"]["glm"]["answered"] == 5


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
    (obj("bed_double"), answer(mattress=True), answer(mattress=False), "no_mattress"),
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


def test_accept_keeps_six_per_type(tmp_path, monkeypatch):
    out = tmp_path / "lib"
    objects, cands = {}, []
    for n in range(8):
        uid = f"{n:032x}"
        objects[uid] = dict(obj(), uid=uid, status="ready")
        cands.append({"uid": uid, "likes": n, "views": 0})
    OV.write_json(out / OV.THUMBS_JSON, {"objects": objects})
    OV.write_json(out / OV.SURVEY_NAME, {"candidates": cands})
    quality = {f"{n:032x}": 5 if n % 2 else 4 for n in range(8)}
    monkeypatch.setattr(OV, "load_judgements",
                        lambda *_a, **_k: {u: {"qwen": answer(quality=q), "glm": answer(quality=q)}
                                           for u, q in quality.items()})
    doc = OV.accept(out, CFG)
    kept = [d["uid"] for d in doc["accepted"]]
    assert len(kept) == 6 and doc["counts"]["over_type_limit"] == 2
    assert all(quality[u] == 5 for u in kept[:4])            # quality first, then likes
    assert kept[:4] == [f"{n:032x}" for n in (7, 5, 3, 1)]


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
    acc = OV.accept(library.out, CFG)
    expected = {library.uids[k] for k in ("sofa_cm", "sofa_m", "sofa_tv", "bed", "table")}
    assert {d["uid"] for d in acc["accepted"]} == expected
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
    assert merged.merged["models_added"] == 5


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
    assert re.search(r"\| sofa \| 2\+\d+ \|", text)          # 2 scandinavian Objaverse sofas + the Poly Haven ones


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


def test_thumbnails_keep_eight_per_type_after_the_bed_split(tmp_path):
    m = Mirror(tmp_path / "mirror")
    beds = [m.add("bed", likes=100 - n) for n in range(16)]
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
    assert len(ready["bed_single"]) == 4 and len(ready["bed_double"]) == 8
    over = [u for u in beds if objs[u].get("code") == "over_candidate_limit"]
    assert len(over) == 4 and all(objs[u]["type"] == "bed_double" for u in over)
    assert over == [u for u in beds if u not in ready["bed_single"]][8:]      # the lowest ranks go
    assert not (out / "thumbs" / "bed_double" / f"{over[0]}.jpg").exists()
