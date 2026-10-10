"""DWG through LibreDWG 0.14 (wenart/ingest/dwg.py, docs/milestone7.md §5.1) and synthetic-06 (§5.2).

Part 1 uses a stand-in ``dwg2dxf`` (a shell script) to pin the call (no ``--as``), the VERSION file, the output
folder, the audit, the empty-model-space rule and the search order. Part 2 uses the real LibreDWG build of the
session (``scripts/cloud-setup.sh`` installs it into ``~/.cache/wenart/libredwg/bin``): synthetic-06's DWG must
read exactly like its source DXF. These tests must pass, not skip, before the Milestone 7 pods (§12). Part 3 runs
the pipeline on synthetic-06 once the generic core (``wenart.ingest.generic.core``, area G3) is integrated.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import subprocess
import sys
from collections import Counter
from dataclasses import asdict
from pathlib import Path

import ezdxf
import pytest
from ezdxf import recover

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import classify as C
from wenart.ingest import dwg
from wenart.ingest import dxf_generic as DG
from wenart.synthetic.projects import DWG_SHA256_06, plan_06

from conftest import PROJECTS, ROOT

PROJECT_06 = PROJECTS / "synthetic-06"
DWG_06 = PROJECT_06 / "synthetic-06.dwg"
SOURCE_06 = PROJECT_06 / "source" / "synthetic-06.dxf"
HAS_LIBREDWG = dwg.find_tool("dwg2dxf") is not None and dwg.find_tool("dxf2dwg") is not None
NEEDS_LIBREDWG = pytest.mark.skipif(not HAS_LIBREDWG, reason="LibreDWG 0.14 not built here (scripts/cloud-setup.sh)")
HAS_CORE = importlib.util.find_spec("wenart.ingest.generic.core") is not None
NEEDS_CORE = pytest.mark.skipif(not HAS_CORE, reason="generic core (wenart.ingest.generic.core, area G3) not "
                                                     "integrated yet")


# --------------------------------------------------------------------------
# Part 1: stand-in converter
# --------------------------------------------------------------------------

def _tool(path: Path, body: str) -> Path:
    path.write_text("#!/usr/bin/env bash\n" + body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def _dxf(path: Path, entities: bool = True) -> Path:
    doc = ezdxf.new("R2000")
    if entities:
        doc.modelspace().add_line((0, 0), (1, 0))
        doc.modelspace().add_line((0, 1), (1, 1))
        doc.modelspace().add_circle((0, 0), 1)
    doc.saveas(path)
    return path


@pytest.fixture
def standin(tmp_path, monkeypatch):
    """A stand-in LibreDWG folder: ``dwg2dxf`` logs its arguments and copies ``$STANDIN_SRC`` to the -o path."""
    bin_dir = tmp_path / "libredwg" / "bin"
    bin_dir.mkdir(parents=True)
    log = tmp_path / "args.txt"
    _tool(bin_dir / "dwg2dxf", f"""printf '%s\\n' "$@" > "{log}"
out=""; prev=""; for a in "$@"; do [ "$prev" = "-o" ] && out="$a"; prev="$a"; done
[ -n "$STANDIN_RC" ] && exit "$STANDIN_RC"
[ -n "$STANDIN_SRC" ] && cp "$STANDIN_SRC" "$out"
exit 0
""")
    (bin_dir / "VERSION").write_text("0.14 d9468ae\n", encoding="utf-8")
    monkeypatch.setenv(dwg.BIN_ENV, str(bin_dir))
    monkeypatch.setattr(dwg, "POD_BIN", tmp_path / "no-pod")
    monkeypatch.setattr(dwg, "SESSION_BIN", tmp_path / "no-session")
    monkeypatch.delenv("STANDIN_RC", raising=False)
    project = tmp_path / "p"
    project.mkdir()
    (project / "plan.dwg").write_bytes(b"AC1015" + b"\0" * 64)
    monkeypatch.setenv("STANDIN_SRC", str(_dxf(tmp_path / "good.dxf")))
    return {"bin": bin_dir, "log": log, "dwg": project / "plan.dwg", "project": project, "tmp": tmp_path}


def test_call_has_no_as_flag_and_writes_into_the_out_dir(standin):
    out = standin["tmp"] / "out" / "converted"
    conv = dwg.convert(standin["dwg"], out)
    args = standin["log"].read_text(encoding="utf-8").split("\n")[:-1]
    assert args == ["-y", "-o", str(out / "plan.dxf"), str(standin["dwg"])]
    assert "--as" not in args
    assert conv.dxf_path == out / "plan.dxf" and conv.dxf_path.is_file()
    assert sorted(p.name for p in standin["project"].iterdir()) == ["plan.dwg"]     # nothing next to the DWG
    assert conv.converter == "libredwg dwg2dxf 0.14 d9468ae; audit: 0 errors, 0 fixes"
    assert conv.version == "0.14 d9468ae" and conv.acadver == "AC1015" and conv.release == "R2000"
    assert conv.entity_counts == {"CIRCLE": 1, "LINE": 2}
    assert conv.to_json()["audit"] == {"errors": 0, "fixes": 0, "messages": []}
    assert dwg.dwg_to_dxf(standin["dwg"], out) == (out / "plan.dxf", conv.converter)


def test_an_output_folder_is_required(standin):
    with pytest.raises(dwg.ConversionError, match="no output folder"):
        dwg.convert(standin["dwg"], None)
    rec = C.classify_pages(standin["project"])[0]                 # the classifier without a work dir
    assert rec.format == "dwg" and not rec.is_extractable()
    assert "DWG conversion failed" in rec.skip_reason and "no output folder" in rec.skip_reason
    assert not (standin["project"] / "plan.dxf").exists()


def test_failed_and_unreadable_conversions(standin, monkeypatch):
    monkeypatch.setenv("STANDIN_RC", "3")
    with pytest.raises(dwg.ConversionError, match=r"failed on plan.dwg \(exit 3\).*export DXF"):
        dwg.convert(standin["dwg"], standin["tmp"] / "out")
    monkeypatch.delenv("STANDIN_RC")
    garbage = standin["tmp"] / "garbage.dxf"
    garbage.write_bytes(b"\x00\x01 not a dxf")
    monkeypatch.setenv("STANDIN_SRC", str(garbage))
    with pytest.raises(dwg.ConversionError, match="not readable by ezdxf"):
        dwg.convert(standin["dwg"], standin["tmp"] / "out")


def test_a_stale_dxf_never_passes_as_the_result(standin, monkeypatch):
    out = standin["tmp"] / "out"
    out.mkdir()
    _dxf(out / "plan.dxf")                                        # left over from an earlier run
    monkeypatch.delenv("STANDIN_SRC")                             # the converter now writes nothing
    with pytest.raises(dwg.ConversionError, match="exit 0"):
        dwg.convert(standin["dwg"], out)
    assert not (out / "plan.dxf").exists()


def test_empty_model_space_is_a_conversion_error_and_needs_review(standin, monkeypatch):
    monkeypatch.setenv("STANDIN_SRC", str(_dxf(standin["tmp"] / "empty.dxf", entities=False)))
    with pytest.raises(dwg.ConversionError, match="model space of plan.dwg is empty.*beta.*export DXF"):
        dwg.convert(standin["dwg"], standin["tmp"] / "out")
    rec = C.classify_pages(standin["project"], work_dir=standin["tmp"] / "work")[0]
    assert "DWG conversion failed" in rec.skip_reason and "empty" in rec.skip_reason
    from wenart.ingest.pipeline import build_project
    building = build_project(standin["project"], standin["tmp"] / "pipeline-out")
    assert building["status"] == "needs_review"
    assert any(w.startswith("needs review: plan.dwg: DWG conversion failed") and "empty" in w
               for w in building["warnings"])


def test_audit_errors_are_reported(standin, monkeypatch):
    class Finding:
        def __init__(self, message):
            self.message = message

    class Auditor:
        errors = [Finding("invalid owner handle"), Finding("invalid layer name")]
        fixes = [Finding("fixed")]

        @property
        def has_errors(self):
            return True

    real = dwg.recover.readfile
    monkeypatch.setattr(dwg.recover, "readfile", lambda path: (real(path)[0], Auditor()))
    conv = dwg.convert(standin["dwg"], standin["tmp"] / "out")
    assert conv.audit_errors == 2 and conv.audit_fixes == 1
    assert conv.converter.endswith("audit: 2 errors, 1 fixes (invalid owner handle; invalid layer name)")


def test_search_order_version_file_and_path(tmp_path, monkeypatch):
    monkeypatch.setattr(dwg, "POD_BIN", tmp_path / "pod")
    monkeypatch.setattr(dwg, "SESSION_BIN", tmp_path / "session")
    monkeypatch.delenv(dwg.BIN_ENV, raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "path-bin"))
    assert dwg.find_tool("dwg2dxf") is None and dwg.available_converters() == []
    assert dwg.libredwg_version() is None
    with pytest.raises(dwg.ConverterNotFound, match="dwg2dxf not found.*cloud-setup.sh.*export DXF"):
        (tmp_path / "x.dwg").write_bytes(b"AC1015")
        dwg.convert(tmp_path / "x.dwg", tmp_path / "out")
    for folder in ("path-bin", "session", "pod/libredwg/bin", "env"):
        (tmp_path / folder).mkdir(parents=True, exist_ok=True)
        _tool(tmp_path / folder / "dwg2dxf", "exit 0\n")
    assert dwg.find_tool("dwg2dxf") == tmp_path / "session" / "dwg2dxf"        # session before PATH
    assert dwg.libredwg_version() == "unknown"                                   # a binary without VERSION
    monkeypatch.setattr(dwg, "POD_BIN", tmp_path / "pod" / "libredwg" / "bin")
    (tmp_path / "pod" / "libredwg" / "VERSION").write_text("0.13.3 (older layout)\n", encoding="utf-8")
    assert dwg.find_tool("dwg2dxf") == tmp_path / "pod" / "libredwg" / "bin" / "dwg2dxf"   # pod before session
    assert dwg.libredwg_version() == "0.13.3 (older layout)"
    (tmp_path / "pod" / "libredwg" / "bin" / "VERSION").write_text("0.14 d9468ae\n", encoding="utf-8")
    assert dwg.libredwg_version() == "0.14 d9468ae"                              # bin/VERSION first
    monkeypatch.setenv(dwg.BIN_ENV, str(tmp_path / "env"))
    assert dwg.find_tool("dwg2dxf") == tmp_path / "env" / "dwg2dxf"              # the environment wins
    shutil.rmtree(tmp_path / "env")
    shutil.rmtree(tmp_path / "pod")
    shutil.rmtree(tmp_path / "session")
    assert dwg.find_tool("dwg2dxf") == tmp_path / "path-bin" / "dwg2dxf"         # PATH last


def test_dwg_magic(tmp_path):
    (tmp_path / "a.dwg").write_bytes(b"AC1032rest")
    (tmp_path / "b.dwg").write_bytes(b"%PDF-1.4")
    assert dwg.dwg_magic(tmp_path / "a.dwg") == "AC1032" and dwg.ACADVER_RELEASES["AC1032"] == "R2018"
    assert dwg.dwg_magic(tmp_path / "b.dwg") is None and dwg.dwg_magic(tmp_path / "missing.dwg") is None


def test_no_ezdwg_in_the_chain():
    text = (ROOT / "wenart" / "ingest" / "dwg.py").read_text(encoding="utf-8")
    assert "import ezdwg" not in text and "--as" not in text.split('"""', 2)[2].split("def dxf_to_dwg")[0]


# --------------------------------------------------------------------------
# Part 2: the session's LibreDWG build and synthetic-06
# --------------------------------------------------------------------------

def test_committed_dwg_is_the_pinned_file():
    assert hashlib.sha256(DWG_06.read_bytes()).hexdigest() == DWG_SHA256_06
    assert DWG_06.read_bytes()[:6] == b"AC1015"
    # Only the DWG is a document of the project: the DXF lives in source/ (the pipeline reads the top level).
    assert [p.name for p in C.project_documents(PROJECT_06)] == ["synthetic-06.dwg"]


@NEEDS_LIBREDWG
def test_dxf2dwg_reproduces_the_committed_dwg(tmp_path):
    written = dwg.dxf_to_dwg(SOURCE_06, tmp_path / "again.dwg")
    assert hashlib.sha256(written.read_bytes()).hexdigest() == DWG_SHA256_06
    assert dwg.libredwg_version(dwg.find_tool("dxf2dwg")) == "0.14 d9468ae p1"


@pytest.fixture(scope="module")
def converted_06(tmp_path_factory):
    if not HAS_LIBREDWG:
        pytest.skip("LibreDWG 0.14 not built here (scripts/cloud-setup.sh)")
    return dwg.convert(DWG_06, tmp_path_factory.mktemp("converted"))


@NEEDS_LIBREDWG
def test_synthetic_06_dwg_reads_like_its_dxf(converted_06):
    conv = converted_06
    assert conv.converter.startswith("libredwg dwg2dxf 0.14 d9468ae p1; audit: 0 errors")
    assert conv.acadver == "AC1015" and conv.release == "R2000" and conv.audit_errors == 0
    source = Counter(e.dxftype() for e in recover.readfile(str(SOURCE_06))[0].modelspace())
    assert conv.entity_counts == dict(sorted(source.items()))
    from_dwg = DG.read_page(conv.dxf_path, "synthetic-06.dwg")
    from_dxf = DG.read_page(SOURCE_06, "synthetic-06.dwg")
    assert from_dwg.warnings == from_dxf.warnings == []
    assert (from_dwg.units_to_m, from_dwg.size, from_dwg.wall_hint_layers) == \
           (from_dxf.units_to_m, from_dxf.size, from_dxf.wall_hint_layers)
    assert [asdict(s) for s in from_dwg.strokes] == [asdict(s) for s in from_dxf.strokes]
    assert [asdict(t) for t in from_dwg.texts] == [asdict(t) for t in from_dxf.texts]
    assert from_dwg.dimensions == from_dxf.dimensions                            # DimensionPrim lists equal
    assert len(from_dwg.dimensions) == len(plan_06().dimensions)


@NEEDS_LIBREDWG
def test_the_dwg_loses_what_the_reader_recovers(converted_06):
    """dxf2dwg drops the angle of rotated dimensions and the MTEXT height; the reader gets both back (the angle
    from the dimension block, the height from the inline code), so the DWG and DXF runs agree."""
    doc = recover.readfile(str(converted_06.dxf_path))[0]
    source = recover.readfile(str(SOURCE_06))[0]
    rotated = [d for d in source.modelspace().query("DIMENSION") if d.dimtype == 0]
    assert rotated and all(d.dxf.hasattr("angle") for d in rotated)
    lost = [d for d in doc.modelspace().query("DIMENSION") if d.dimtype == 0]
    assert [d.dxf.handle for d in lost] == [d.dxf.handle for d in rotated]
    assert not any(d.dxf.hasattr("angle") for d in lost)
    assert [DG.dimension_angle_from_block(d) for d in lost] == [d.dxf.angle % 180.0 for d in rotated]
    assert sorted(d.dimtype for d in doc.modelspace().query("DIMENSION")) == [0, 0, 0, 0, 1, 1, 1, 1]
    mtext = doc.modelspace().query("MTEXT")[0]
    assert mtext.dxf.char_height == 0.0 and mtext.text.startswith("\\H9;")


# --------------------------------------------------------------------------
# Part 3: the pipeline on synthetic-06 (needs the generic core, G3)
# --------------------------------------------------------------------------

def _run_pipeline(project: Path, out: Path) -> dict:
    proc = subprocess.run([sys.executable, "-m", "wenart.ingest.pipeline", str(project), "--out", str(out),
                           "--no-ai"], capture_output=True, text=True, cwd=ROOT, timeout=600)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    return json.loads((out / "building.json").read_text(encoding="utf-8"))


_PATHS = {"file", "converter", "source_folder", "created_utc", "pipeline_commit", "debug_image"}


def _without_paths(value):
    """An element list with file names and converter strings removed (they differ by design)."""
    if isinstance(value, dict):
        return {k: _without_paths(v) for k, v in value.items() if k not in _PATHS}
    if isinstance(value, list):
        return [_without_paths(v) for v in value]
    if isinstance(value, str):
        return value.replace("synthetic-06.dwg", "<doc>").replace("synthetic-06.dxf", "<doc>")
    return value


@NEEDS_LIBREDWG
@NEEDS_CORE
def test_synthetic_06_pipeline_dwg_run_equals_dxf_run_and_matches_truth(tmp_path):
    dwg_project = tmp_path / "dwg" / "synthetic-06"
    dxf_project = tmp_path / "dxf" / "synthetic-06"
    for folder in (dwg_project, dxf_project):
        folder.mkdir(parents=True)
        shutil.copyfile(PROJECT_06 / "brief.yaml", folder / "brief.yaml")
    shutil.copyfile(DWG_06, dwg_project / "synthetic-06.dwg")
    shutil.copyfile(SOURCE_06, dxf_project / "synthetic-06.dxf")
    from_dwg = _run_pipeline(dwg_project, tmp_path / "out-dwg")
    from_dxf = _run_pipeline(dxf_project, tmp_path / "out-dxf")
    assert from_dwg["documents"][0]["format"] == "dwg" and from_dwg["documents"][0]["converter"].startswith(
        "libredwg dwg2dxf 0.14 d9468ae")
    for key in ("levels", "walls", "openings", "rooms", "furniture", "conflicts", "unverified", "site"):
        assert _without_paths(from_dwg.get(key)) == _without_paths(from_dxf.get(key)), key
    truth = B.load(PROJECT_06 / "truth" / "building.json")
    b = from_dwg
    assert b["status"] == "ok" and b["project"].get("unit_system") == "imperial"
    level = b["levels"][0]
    assert (level["id"], level.get("label_source")) == ("L0", "assumed")
    assert any("level title missing" in w for w in b["warnings"])
    # Walls: 6" and 9" come out as 0.150 / 0.230 m (thickness rounded to 5 mm, §2.4); centre lines within 1 cm.
    assert len(b["walls"]) == len(truth["walls"])
    for t in truth["walls"]:
        hits = [w for w in b["walls"] if min(G.distance(w["start"], t["start"]) + G.distance(w["end"], t["end"]),
                                             G.distance(w["start"], t["end"]) + G.distance(w["end"], t["start"]))
                <= 0.02 and abs(w["thickness"] - t["thickness"]) <= 0.005]
        assert len(hits) == 1, t["id"]
    # Openings by type, centre and width (the separator by its line).
    assert sorted(o["type"] for o in b["openings"]) == sorted(o["type"] for o in truth["openings"])
    for t in truth["openings"]:
        hits = [o for o in b["openings"] if o["type"] == t["type"] and G.distance(o["center"], t["center"]) <= 0.02
                and abs(o["width"] - t["width"]) <= 0.02 and bool(o.get("virtual")) == bool(t.get("virtual"))]
        assert len(hits) == 1, t["id"]
    # Rooms by label, type and area (2 %: the separator band, §2.7.1).
    for t in truth["rooms"]:
        hits = [r for r in b["rooms"] if r["label"] == t["label"] and r["room_type"] == t["room_type"]
                and abs(r["area_computed"] - t["area_computed"]) <= 0.02 * t["area_computed"]]
        assert len(hits) == 1, t["id"]
    living = next(r for r in b["rooms"] if r["room_type"] == "living")
    assert living["label_size"]["status"] == "ok"
    # Furniture by block-name type, centre, size; rotation modulo 180 when no front is known.
    assert len(b["furniture"]) == len(truth["furniture"])
    for t in truth["furniture"]:
        fp = t["footprint"]
        hits = [f for f in b["furniture"] if f["type"] == t["type"] and f.get("type_method") == "block_name"
                and G.distance(f["footprint"]["center"], fp["center"]) <= 0.02
                and sorted(f["footprint"]["size"]) == pytest.approx(sorted(fp["size"]), abs=0.02)]
        assert len(hits) == 1, t["id"]
        if hits[0]["front_deg"] is not None and t["front_deg"] is not None:
            assert G.angle_difference_deg(hits[0]["front_deg"], t["front_deg"]) <= 1.0, t["id"]
    assert b["conflicts"] == [] and not (b.get("site") or {}).get("boundary_walls")


def test_libredwg_pins_agree_everywhere():
    """dwg.py, the pod setup and the cloud setup build and expect the same LibreDWG (§5.1)."""
    version = dwg.LIBREDWG_VERSION
    assert version == "0.14 d9468ae p1"          # the pinned commit + the block-index patch (real03, 10 Oct 2026)
    for script in ("scripts/pod_setup_recognition.sh", "scripts/cloud-setup.sh"):
        text = (ROOT / script).read_text(encoding="utf-8")
        assert f"LIBREDWG_TAG={dwg.LIBREDWG_TAG}\n" in text and f"LIBREDWG_COMMIT={dwg.LIBREDWG_COMMIT}\n" in text
        assert f'LIBREDWG_VERSION_STRING="{version}"' in text and "-DBUILD_SHARED_LIBS=OFF" in text
        assert subprocess.run(["bash", "-n", str(ROOT / script)], capture_output=True).returncode == 0
    assert 'LIBREDWG_HOME="$HOME/.cache/wenart/libredwg"' in (ROOT / "scripts/cloud-setup.sh").read_text()
    assert dwg.SESSION_BIN == Path("~/.cache/wenart/libredwg/bin") and dwg.POD_BIN == Path(
        "/workspace/tools/libredwg/bin")
