"""The pure helpers of wenart/blender/export.py (Milestone 9: the 3D files of the results); the Blender part runs on
the pod (tests/gpu/test_m9.py)."""
import hashlib
import json
from pathlib import Path

import pytest

from wenart.blender import export as E

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("w, h, side, want", [
    (2048, 2048, 1024, (1024, 1024)), (4096, 1024, 1024, (1024, 256)), (1000, 3000, 1024, (341, 1024)),
    (1024, 512, 1024, None), (300, 200, 1024, None), (4096, 4096, 0, None), (5000, 1, 1024, (1024, 1)),
])
def test_scaled_size_keeps_the_aspect_and_never_scales_up(w, h, side, want):
    assert E.scaled_size(w, h, side) == want


def test_camera_looks_of_a_committed_render_manifest():
    path = ROOT / "results" / "renders" / "synthetic-04" / "render_manifest.json"
    if not path.is_file():
        pytest.skip("committed render manifest not present")
    doc = json.loads(path.read_text(encoding="utf-8"))
    looks = E.camera_looks(doc)
    assert set(looks) == {r["camera"] for r in doc["renders"]}
    first = doc["renders"][0]
    assert looks[first["camera"]]["ev"] == float(first["exposure"]["ev"])
    assert looks[first["camera"]]["whitepoint"] == [float(v) for v in first["exposure"]["whitepoint"]]
    assert (doc["view_transform"], doc["look"], doc["resolution"]) == (E.VIEW_TRANSFORM, E.LOOK, list(E.RESOLUTION))


def test_camera_looks_leaves_out_missing_values():
    doc = {"renders": [{"camera": "a", "exposure": {"ev": 2}}, {"camera": "b", "exposure": {"whitepoint": [1, 1]}},
                       {"camera": "c"}, {"exposure": {"ev": 1.0}}, "x"]}
    assert E.camera_looks(doc) == {"a": {"ev": 2.0}, "b": {}, "c": {}}
    assert E.camera_looks({}) == {} and E.camera_looks(None) == {}


@pytest.mark.parametrize("fmt, is_float, channels, file_format, scaled, want", [
    ("jpeg", False, 4, "PNG", False, True), ("jpeg", False, 3, "JPEG", False, False),
    ("jpeg", False, 3, "JPEG", True, True), ("jpeg", True, 4, "OPEN_EXR", False, False),
    ("jpeg", False, 1, "PNG", False, False), ("png", False, 4, "PNG", True, False),
])
def test_jpeg_packing_candidates(fmt, is_float, channels, file_format, scaled, want):
    assert E.wants_jpeg(fmt, is_float, channels, file_format, scaled) is want


def test_readme_names_the_cameras_and_their_exposure():
    text = E.readme_text("synthetic-04", {"cam_b": {"ev": 4.333333}, "cam_a": {}}, 1024,
                         ["synthetic-04.blend", "synthetic-04.glb"])
    assert "- cam_a: exposure not metered\n- cam_b: exposure +4.33 EV" in text
    assert "wenart_exposure_ev" in text and "AgX - Punchy" in text and "window pull" in text
    assert text.endswith("Files: synthetic-04.blend, synthetic-04.glb\n")


def test_manifest_lists_the_files_with_their_sha256(tmp_path):
    (tmp_path / "p.blend").write_bytes(b"blend")
    images = [{"name": "a", "scaled": True, "packed": True, "format": "JPEG", "packed_bytes": 10},
              {"name": "b", "scaled": False, "packed": True, "format": "PNG", "packed_bytes": 5}]
    doc = E.manifest_doc("p", tmp_path, {"blend": "p.blend", "glb": "p.glb"}, images, {"cam": {"ev": 1.0}}, 1024,
                         "5.2.2", ["w"], 12.345, texture_format="jpeg")
    assert doc["files"]["blend"] == {"file": "p.blend", "bytes": 5, "sha256": hashlib.sha256(b"blend").hexdigest()}
    assert doc["files"]["glb"] == {"file": "p.glb", "missing": True}
    assert (doc["images_scaled"], doc["images_packed"], doc["images_jpeg"], doc["packed_image_bytes"]) == (1, 2, 1, 15)
    assert doc["kind"] == "wenart_export" and doc["seconds"] == 12.35 and doc["texture_format"] == "jpeg"
    json.dumps(doc)


def test_export_arguments():
    args = E.parse_args(["--out", "o", "--name", "p"])
    assert (args.max_texture, args.texture_format, args.jpeg_quality, args.no_glb) == (1024, "jpeg", 90, False)
    args = E.parse_args(["--out", "o", "--name", "p", "--texture-format", "png", "--max-texture", "0", "--no-glb"])
    assert (args.texture_format, args.max_texture, args.no_glb) == ("png", 0, True)
