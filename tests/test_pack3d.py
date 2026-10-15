"""``python -m wenart.run.pack3d``: a project's 3D files as one zip in parts (Milestone 9, docs/milestone9.md §5a),
one set per building variant (Milestone 10)."""
import hashlib
import zipfile

from wenart.run import pack3d as K


def _project(tmp_path):
    final = tmp_path / "final" / "p"
    (final / "3d").mkdir(parents=True)
    (final / "3d" / "p.blend").write_bytes(b"B" * 5000)
    (final / "3d" / "p.glb").write_bytes(b"G" * 3000)
    (final / "3d" / "export_manifest.json").write_text("{}")
    (final / "3d" / "export.log").write_text("log")
    (final / "ATTRIBUTION.md").write_text("# credits")
    return final


def test_pack_splits_the_zip_and_the_parts_join_back(tmp_path):
    final = _project(tmp_path)
    out = tmp_path / "delivery"
    written = K.pack(final, out, part_mb=1)
    names = [p.name for p in written]
    assert names == ["p_3d.zip.part00", "p_3d.zip.sha256", K.README]
    joined = b"".join((out / n).read_bytes() for n in names if ".part" in n)
    digest = hashlib.sha256(joined).hexdigest()
    assert (out / "p_3d.zip.sha256").read_text() == f"{digest}  p_3d.zip\n"
    (tmp_path / "j.zip").write_bytes(joined)
    with zipfile.ZipFile(tmp_path / "j.zip") as z:
        assert z.testzip() is None
        assert sorted(z.namelist()) == ["p/ATTRIBUTION.md", "p/export_manifest.json", "p/p.blend", "p/p.glb"]
        assert z.getinfo("p/p.blend").compress_type == zipfile.ZIP_STORED
        assert z.getinfo("p/p.glb").compress_type == zipfile.ZIP_DEFLATED
        assert z.read("p/p.blend") == b"B" * 5000
    assert not (out / "p_3d.zip").exists()
    text = (out / K.README).read_text()
    assert "cat p_3d.zip.part* > p_3d.zip" in text and "copy /b p_3d.zip.part00 p_3d.zip" in text and digest in text


def test_parts_of_a_given_size(tmp_path, monkeypatch):
    final = _project(tmp_path)
    (final / "3d" / "p.blend").write_bytes(bytes(range(256)) * 12000)     # 3 MB, stored
    parts = [p for p in K.pack(final, tmp_path / "o", part_mb=1) if ".part" in p.name]
    assert len(parts) == 3 and all(p.stat().st_size == 2**20 for p in parts[:-1])


def test_cli_without_3d_files_is_exit_2(tmp_path, capsys):
    (tmp_path / "empty").mkdir()
    assert K.main(["--src", str(tmp_path / "empty"), "--out", str(tmp_path / "o")]) == 2
    assert "no .blend or .glb" in capsys.readouterr().err
    final = _project(tmp_path)
    assert K.main(["--src", str(final / "3d"), "--out", str(tmp_path / "o2"), "--name", "real"]) == 0
    assert (tmp_path / "o2" / "real_3d.zip.part00").is_file()


# Milestone 10 (docs/milestone10.md §1.6, §3.2 item 8): one 3D set per building variant.
ALT = "l-1b-acik-mutfak"


def _variant_project(tmp_path):
    out = tmp_path / "outputs" / "p"
    (out / "export").mkdir(parents=True)
    (out / "export" / "p.blend").write_bytes(b"B" * 4000)
    (out / "export" / "p.glb").write_bytes(b"G" * 2000)
    (out / "export" / "export_manifest.json").write_text('{"base": 1}')
    alt = out / "variants" / ALT / "export"
    alt.mkdir(parents=True)
    (alt / f"p-{ALT}.blend").write_bytes(b"b" * 3000)
    (alt / f"p-{ALT}.glb").write_bytes(b"g" * 1000)
    (alt / "export_manifest.json").write_text('{"alt": 1}')
    return out


def test_pack3d_one_set_per_variant(tmp_path):
    out = _variant_project(tmp_path)
    written = K.pack(out / "export", tmp_path / "delivery", part_mb=1)
    names = [p.name for p in written]
    assert names == ["p_3d.zip.part00", "p_3d.zip.sha256", f"p-{ALT}_3d.zip.part00", f"p-{ALT}_3d.zip.sha256", K.README]
    part = tmp_path / "delivery" / f"p-{ALT}_3d.zip.part00"
    digest = hashlib.sha256(part.read_bytes()).hexdigest()
    assert (tmp_path / "delivery" / f"p-{ALT}_3d.zip.sha256").read_text() == f"{digest}  p-{ALT}_3d.zip\n"
    with zipfile.ZipFile(part) as z:
        assert sorted(z.namelist()) == [f"p-{ALT}/export_manifest.json", f"p-{ALT}/p-{ALT}.blend", f"p-{ALT}/p-{ALT}.glb"]
        assert z.read(f"p-{ALT}/export_manifest.json") == b'{"alt": 1}'
    with zipfile.ZipFile(tmp_path / "delivery" / "p_3d.zip.part00") as z:
        assert sorted(z.namelist()) == ["p/export_manifest.json", "p/p.blend", "p/p.glb"]
    text = (tmp_path / "delivery" / K.README).read_text()
    assert f"p-{ALT}: join p-{ALT}_3d.zip.part*" in text and digest in text
    # the results layout: the variant set next to the base files in 3d/
    final = tmp_path / "final" / "p"
    (final / "3d").mkdir(parents=True)
    (final / "3d" / "p.blend").write_bytes(b"B")
    (final / "3d" / f"p-{ALT}.blend").write_bytes(b"b")
    (final / "ATTRIBUTION.md").write_text("# credits")
    sets = K.sets_of(final)
    assert [s for s, _ in sets] == ["p", f"p-{ALT}"]
    assert [f.name for f in sets[1][1]] == [f"p-{ALT}.blend", "ATTRIBUTION.md"]
    assert [f.name for f in K.files_of(final)] == ["p.blend", "ATTRIBUTION.md"]


def test_readme_says_what_the_glb_carries_of_the_vegetation(tmp_path):
    """Milestone 13 (T6, round 2): the leaf cards and grass clumps are geometry-nodes instances; the README says
    whether the export realized them (``realized_instances`` of export_manifest.json, written by
    wenart.blender.site.realize_site_instances) or the .glb carries the hedge cores and crown cards only."""
    import json
    src = tmp_path / "real04"
    (src / "3d").mkdir(parents=True)
    (src / "3d" / "real04.blend").write_bytes(b"BLENDER" + b"\0" * 100)
    (src / "3d" / "real04.glb").write_bytes(b"glTF" + b"\0" * 100)
    (src / "3d" / "export_manifest.json").write_text(json.dumps({"files": {}}), encoding="utf-8")
    notes = K.vegetation_notes(src)
    assert any("hedge cores, the trunks and crown cards" in line for line in notes)
    assert any("did not realize" in line for line in notes)
    out = tmp_path / "delivery"
    K.pack(src, out, part_mb=1)
    text = (out / K.README).read_text(encoding="utf-8")
    assert "Vegetation in the 3D files (Milestone 13" in text and "hedge cores" in text
    # With the record: the realized groups, their polygons and the cap, and the groups left as instances.
    (src / "3d" / "export_manifest.json").write_text(json.dumps({"files": {}, "realized_instances": {
        "cap": 1000000, "polygons": 7034, "realized": ["veg_scatter_olive_60", "veg_scatter_cherry_laurel_120"],
        "skipped": [{"group": "veg_grass_polyhaven_4", "polygons": 1210000, "reason": "cap"}]}}), encoding="utf-8")
    notes = K.vegetation_notes(src)
    joined = "\n".join(notes)
    assert "cap of 1000000 polygons: 2 vegetation node group(s), 7034 polygons" in joined
    assert "veg_scatter_olive_60, veg_scatter_cherry_laurel_120" in joined
    assert "Left as instances" in joined and "veg_grass_polyhaven_4 (1210000 polygons)" in joined
    assert "collection instances" in joined
    K.pack(src, out, part_mb=1)
    assert "7034 polygons" in (out / K.README).read_text(encoding="utf-8")
    # No export manifest at all (an export before Milestone 9's manifest): the same "cores only" line.
    (src / "3d" / "export_manifest.json").unlink()
    assert any("did not realize" in line for line in K.vegetation_notes(src))
