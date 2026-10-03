"""CPU tests of ``scripts/add_project.py`` (docs/intake.md, the easy path): chat uploads without a suffix,
zip files, folders, the intake rules (junk, subfolders, DWG), the brief, refusals and needs-review exits."""
from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

spec = importlib.util.spec_from_file_location("add_project",
                                              Path(__file__).resolve().parents[1] / "scripts" / "add_project.py")
AP = importlib.util.module_from_spec(spec)
sys.modules["add_project"] = AP
spec.loader.exec_module(AP)

PDF = b"%PDF-1.7\n%..."
DXF = b"  0\nSECTION\n  2\nHEADER\n"


def write(path: Path, data: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def files(folder: Path) -> list[str]:
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


@pytest.mark.parametrize("data,suffix", [
    (PDF, ".pdf"), (DXF, ".dxf"), (b"AutoCAD Binary DXF\r\n", ".dxf"), (b"AC1032....", ".dwg"),
    (b"\x89PNG\r\n\x1a\n...", ".png"), (b"\xff\xd8\xff\xe0", ".jpg"), (b"II*\x00", ".tif"),
    (b"PK\x03\x04", ".zip"), (b"hello", None)])
def test_sniff_suffix(tmp_path, data, suffix):
    assert AP.sniff_suffix(write(tmp_path / "f", data)) == suffix


def test_chat_uploads_without_suffix_get_one(tmp_path):
    up = tmp_path / "uploads"
    a, b = write(up / "file_01abc", PDF), write(up / "file_02def", DXF)
    code, report = AP.add_project("real01", [a, b], tmp_path / "projects")
    assert code == 0, report
    assert files(tmp_path / "projects" / "real01") == ["file_01abc.pdf", "file_02def.dxf"]


def test_zip_folder_layout_and_intake_rules(tmp_path):
    z = tmp_path / "upload"                      # a chat upload of a zip, no suffix
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("proje/plans/zemin.dxf", DXF)
        zf.writestr("proje/plans/zemin.dwg", b"AC1032")
        zf.writestr("proje/1_kat.pdf", PDF)
        zf.writestr("proje/style_photos/salon.jpg", b"\xff\xd8\xff")
        zf.writestr("proje/notes.docx", b"x")
        zf.writestr("__MACOSX/proje/._1_kat.pdf", b"x")
        zf.writestr("../evil.pdf", PDF)
    code, report = AP.add_project("real01", [z], tmp_path / "projects")
    assert code == 0, report
    assert files(tmp_path / "projects" / "real01") == [
        "proje__1_kat.pdf", "proje__plans__zemin.dxf", "proje__style_photos__salon.jpg"]
    text = "\n".join(report)
    assert "../evil.pdf" in text and "DWG not read" in text and "file type not used (.docx)" in text


def test_folder_source_keeps_style_photos_and_brief(tmp_path):
    src = tmp_path / "my-folder"
    write(src / "zemin_kat.dxf", DXF)
    write(src / "style_photos" / "a.jpg", b"\xff\xd8\xff")
    write(src / "brief.yaml", b"style: Japandi\n")
    write(src / ".DS_Store")
    code, _ = AP.add_project("real01", [src], tmp_path / "projects", style="ignored, brief exists")
    assert code == 0
    out = tmp_path / "projects" / "real01"
    assert files(out) == ["brief.yaml", "style_photos/a.jpg", "zemin_kat.dxf"]
    assert yaml.safe_load((out / "brief.yaml").read_text()) == {"style": "Japandi"}


def test_style_writes_brief(tmp_path):
    a = write(tmp_path / "plan.pdf", PDF)
    code, _ = AP.add_project("real01", [a], tmp_path / "projects", style="Modern, walnut floor, ğüşİ")
    assert code == 0
    brief = tmp_path / "projects" / "real01" / "brief.yaml"
    assert yaml.safe_load(brief.read_text(encoding="utf-8")) == {"style": "Modern, walnut floor, ğüşİ"}


def test_refusals(tmp_path):
    a = write(tmp_path / "plan.pdf", PDF)
    with pytest.raises(AP.Refused, match="private alias"):
        AP.add_project("real-01", [a], tmp_path / "projects")
    with pytest.raises(AP.Refused, match="invalid project name"):
        AP.add_project("../x", [a], tmp_path / "projects")
    assert AP.add_project("real01", [a], tmp_path / "projects")[0] == 0
    with pytest.raises(AP.Refused, match="--replace"):
        AP.add_project("real01", [a], tmp_path / "projects")
    b = write(tmp_path / "other.pdf", PDF)
    assert AP.add_project("real01", [b], tmp_path / "projects", replace=True)[0] == 0
    assert files(tmp_path / "projects" / "real01") == ["other.pdf"]


def test_no_document_writes_nothing(tmp_path):
    a = write(tmp_path / "notes.docx")
    code, report = AP.add_project("real01", [a], tmp_path / "projects")
    assert code == AP.EXIT_NEEDS_REVIEW
    assert "nothing written" in report[-1]
    assert not (tmp_path / "projects" / "real01").exists()


def test_cli_exit_codes(tmp_path, capsys):
    a = write(tmp_path / "plan.pdf", PDF)
    proj = ["--projects", str(tmp_path / "projects")]
    assert AP.main(["real-01", str(a), *proj]) == AP.EXIT_REFUSED
    assert AP.main(["real01", str(tmp_path / "missing.pdf"), *proj]) == AP.EXIT_REFUSED
    assert AP.main(["real01", str(a), *proj]) == 0
    assert "project real01: 1 documents" in capsys.readouterr().out
