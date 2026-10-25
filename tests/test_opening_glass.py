"""Library windows must let the daylight in (25 Oct 2026: real04's "Window1 1" has panes painted on an opaque
texture; chosen for every window it darkened the south rooms by 4-7 EV). CPU, pure."""
import json
import struct

from wenart.blender import opening_models as OM


def _glb(path, materials):
    doc = json.dumps({"asset": {"version": "2.0"}, "materials": materials}).encode("utf-8")
    doc += b" " * (-len(doc) % 4)
    path.write_bytes(b"glTF" + struct.pack("<II", 2, 12 + 8 + len(doc)) + struct.pack("<II", len(doc), 0x4E4F534A)
                     + doc)
    return path


def test_glb_glass_reads_names_alpha_and_transmission(tmp_path):
    assert OM.glb_glass(_glb(tmp_path / "a.glb", [{"name": "Frame"}, {"name": "Glass_clear"}])) is True
    assert OM.glb_glass(_glb(tmp_path / "b.glb", [{"name": "m1", "alphaMode": "BLEND",
                                                   "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 0.3]}}]))
    assert OM.glb_glass(_glb(tmp_path / "c.glb", [{"name": "m2", "extensions": {
        "KHR_materials_transmission": {"transmissionFactor": 0.9}}}]))
    assert OM.glb_glass(_glb(tmp_path / "d.glb", [{"name": "Wood"}, {"name": "Window1_1", "alphaMode": "BLEND"}])) \
        is False                                         # an opaque picture of panes
    assert OM.glb_glass(tmp_path / "missing.glb") is None


def _entry(eid, glb, w=0.9, h=1.2):
    return {"id": eid, "type": "window", "title": "Window", "glb": glb, "textured": True, "bbox_m": [w, 0.1, h],
            "audit": {"status": "keep"}, "licence_flag": "none", "commercial_safe": True}


def test_a_window_model_without_glass_is_never_chosen(tmp_path):
    (tmp_path / "models").mkdir()
    _glb(tmp_path / "models" / "a.glb", [{"name": "Wood"}, {"name": "Window1_1"}])
    _glb(tmp_path / "models" / "b.glb", [{"name": "Aluminium"}, {"name": "glass"}])
    extras = [_entry("a_leaded", "models/a.glb"), _entry("b_alu", "models/b.glb", w=1.0)]
    wall = {"id": "w", "level_id": "L0", "start": [0, 0], "end": [6, 0], "thickness": 0.2}
    op = {"id": "o", "type": "window", "level_id": "L0", "wall_id": "w", "center": [3, 0], "width": 1.8}
    building = {"levels": [{"id": "L0", "elevation": 0.0}], "walls": [wall], "openings": [op], "rooms": []}
    outer = [{"opening": op, "bottom": 0.9, "top": 2.1, "outward": [0, -1]}]
    without = OM.plan(building, outer, extras)
    assert without["o"]["asset"]["asset_id"] == "a_leaded"          # unjudged without the files: best proportions
    with_files = OM.plan(building, outer, extras, assets_dir=tmp_path)
    assert with_files["o"]["asset"]["asset_id"] == "b_alu"


def test_a_few_odd_windows_do_not_swap_the_model():
    e = _entry("x", "x.glb")
    one = OM._rank_key(e, "window", [(1.8, 1.2)] * 10)
    more = OM._rank_key(e, "window", [(1.8, 1.2)] * 10 + [(4.0, 1.0), (2.68, 1.2)])
    assert one[:4] == more[:4]                           # the mean error ranks in steps of RANK_STEP
