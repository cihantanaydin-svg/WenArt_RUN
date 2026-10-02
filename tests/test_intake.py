"""CPU tests of the private-project intake (docs/milestone6.md §7.1, §9): ``wenart.intake``.

A hand-made upload in tmp_path (the user's S3 folder) is staged into ``<outputs>/<alias>/input/<alias>``:
alias rules, junk skip, NFC names, subfolder staging and collisions, caps, symlinks, the DWG rule,
rebuild on re-stage, the manifest, exit codes and that nothing printed names a file.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import unicodedata
from pathlib import Path

import pytest

from wenart import intake as I
from wenart.ingest.classify import project_documents

ROOT = Path(__file__).resolve().parents[1]
ALIAS = "real-01"
NFD_NAME = unicodedata.normalize("NFD", "İkinci_kat_planı.pdf")


@pytest.fixture
def env(tmp_path):
    """Upload root, outputs root and a fake repo (with one committed project)."""
    roots = {"pp": tmp_path / "projects-private", "po": tmp_path / "outputs-private", "repo": tmp_path / "repo"}
    roots["pp"].mkdir()
    (roots["repo"] / "projects" / "synthetic-01").mkdir(parents=True)
    return roots


def upload(env, alias: str = ALIAS) -> Path:
    up = env["pp"] / alias
    up.mkdir(parents=True, exist_ok=True)
    return up


def write(path: Path, data: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def out_for(env, alias: str = ALIAS) -> Path:
    return env["po"] / alias / "input" / alias


def stage(env, alias: str = ALIAS, **kw) -> I.Intake:
    return I.stage_project(alias, out_for(env, alias), root=env["pp"], repo_root=env["repo"], **kw)


def manifest(env, alias: str = ALIAS) -> dict:
    return json.loads((env["po"] / alias / "intake_manifest.json").read_text(encoding="utf-8"))


def staged_files(out: Path) -> list[str]:
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


def by_path(m: dict) -> dict:
    return {f["path"]: f for f in m["files"]}


def tree_digest(folder: Path) -> list:
    """(relative path, bytes sha256, is link) of everything in a folder, to prove it is never modified."""
    out = []
    for dirpath, dirnames, filenames in os.walk(folder):
        for name in sorted(dirnames + filenames):
            p = Path(dirpath) / name
            data = b"" if p.is_dir() or p.is_symlink() else p.read_bytes()
            out.append((p.relative_to(folder).as_posix(), hashlib.sha256(data).hexdigest(), p.is_symlink()))
    return sorted(out)


# --------------------------------------------------------------------------
# Alias rules and refused requests (exit 2)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("alias", ["Yilmaz-Villa", "real-1", "real-0001", "../real-01", "real-01/x", "", "private-01"])
def test_invalid_alias_is_refused(env, alias, capsys):
    rc = I.main(["stage", alias, "--out", str(env["po"] / "x" / "input" / "x"), "--root", str(env["pp"])])
    assert rc == I.EXIT_REFUSED
    assert "INTAKE refused" in capsys.readouterr().err
    assert not env["po"].exists()


def test_alias_of_a_committed_project_and_unsafe_out_are_refused(env):
    (env["repo"] / "projects" / "real-07").mkdir()
    with pytest.raises(I.IntakeRefused, match="committed project"):
        stage(env, "real-07")
    up = upload(env)
    write(up / "a.dxf")
    with pytest.raises(I.IntakeRefused, match="must end with the alias"):
        I.stage_project(ALIAS, env["po"] / ALIAS / "input" / "other", root=env["pp"], repo_root=env["repo"])
    with pytest.raises(I.IntakeRefused, match="overlap"):
        I.stage_project(ALIAS, up / "input" / ALIAS, root=env["pp"], repo_root=env["repo"])
    assert (up / "a.dxf").is_file() and not (up / "input").exists()
    assert I.stage_project("selftest-02", out_for(env, "selftest-02"), root=env["pp"],
                           repo_root=env["repo"]).reasons == [I.NOT_UPLOADED]


def test_cli_exit_codes_and_output_names_no_file(env, capsys, monkeypatch):
    monkeypatch.setattr(I, "REPO_ROOT", env["repo"])
    args = ["stage", ALIAS, "--out", str(out_for(env)), "--root", str(env["pp"])]
    assert I.main(args) == I.EXIT_NEEDS_REVIEW
    line = capsys.readouterr().out
    assert line.startswith(f"INTAKE {ALIAS} needs_review: not uploaded")
    up = upload(env)
    write(up / "gizli_villa_zemin.dxf", b"0\nEOF\n")
    write(up / "Musteri Adi" / "plan.pdf")
    assert I.main(args) == I.EXIT_OK
    line = capsys.readouterr().out
    assert line.startswith(f"INTAKE {ALIAS} ok: 2 kept (2 documents, 0 style photos), 0 skipped")
    for secret in ("gizli", "villa", "Musteri", "plan.pdf"):
        assert secret not in line


# --------------------------------------------------------------------------
# Not uploaded, no document, symlinks
# --------------------------------------------------------------------------

def test_not_uploaded_is_needs_review_with_a_manifest(env):
    old = write(out_for(env) / "stale.pdf")             # an old staged copy must never be read again
    r = stage(env)
    assert (r.status, r.reasons) == ("needs_review", ["not uploaded"])
    m = manifest(env)
    assert m["status"] == "needs_review" and m["reasons"] == ["not uploaded"] and m["files"] == []
    assert m["staged"] is None and m["alias"] == ALIAS and m["kind"] == "intake_manifest"
    assert not old.exists() and not out_for(env).exists()


def test_only_skipped_files_is_needs_review(env):
    up = upload(env)
    write(up / ".DS_Store")
    write(up / "notes.docx")
    write(up / "brief.yaml", b"style: Modern\n")
    r = stage(env)
    assert r.reasons == [I.NO_DOCUMENT]
    assert not out_for(env).exists()
    f = by_path(manifest(env))
    assert f["brief.yaml"]["kept"] and f["brief.yaml"]["staged"] is None
    assert f["brief.yaml"]["would_stage_as"] == "brief.yaml"


def test_symlinks_are_refused_and_never_followed(env, tmp_path):
    outside = tmp_path / "elsewhere"
    write(outside / "secret.pdf", b"secret")
    up = upload(env)
    write(up / "a.dxf")
    os.symlink(outside / "secret.pdf", up / "link.pdf")
    os.symlink(outside, up / "linked_dir")
    r = stage(env)
    assert r.status == "ok"
    f = by_path(manifest(env))
    assert f["link.pdf"]["reason"] == f["linked_dir"]["reason"] == "symlink (refused, not followed)"
    assert not f["link.pdf"]["kept"] and "linked_dir/secret.pdf" not in f
    assert staged_files(out_for(env)) == ["a.dxf"]


def test_upload_folder_that_is_a_symlink_is_refused(env, tmp_path):
    real = tmp_path / "real_upload"
    write(real / "a.dxf")
    os.symlink(real, env["pp"] / ALIAS)
    r = stage(env)
    assert r.reasons == [I.ROOT_SYMLINK] and not out_for(env).exists()


def test_special_files_are_skipped(env):
    up = upload(env)
    write(up / "a.dxf")
    os.mkfifo(up / "pipe.pdf")
    stage(env)
    assert by_path(manifest(env))["pipe.pdf"]["reason"] == "not a regular file"


# --------------------------------------------------------------------------
# Junk, hidden files, suffixes
# --------------------------------------------------------------------------

def test_junk_hidden_and_unused_types_are_skipped_and_listed(env):
    up = upload(env)
    write(up / "zemin.dxf")
    for name in (".DS_Store", "Thumbs.db", "desktop.ini", "._zemin.dxf", "__MACOSX/._zemin.dxf",
                 "__MACOSX/sub/x.pdf", "Desktop.INI"):
        write(up / name)
    write(up / ".hidden.pdf")
    write(up / ".git" / "config.txt")
    for name in ("model.rvt", "sheet.XLSX", "archive.zip", "README"):
        write(up / name)
    for name in ("brief.yaml", "notes.TXT", "readme.md", "scan.TIFF", "photo.JPEG"):
        write(up / name)
    r = stage(env)
    assert r.status == "ok"
    f = by_path(manifest(env))
    for name in (".DS_Store", "Thumbs.db", "desktop.ini", "._zemin.dxf", "Desktop.INI"):
        assert f[name]["reason"] == "junk (system metadata file)", name
    assert f["__MACOSX/._zemin.dxf"]["reason"] == f["__MACOSX/sub/x.pdf"]["reason"] == "junk (__MACOSX folder)"
    assert f[".hidden.pdf"]["reason"] == "hidden file" and f[".git/config.txt"]["reason"] == "hidden folder"
    assert f["model.rvt"]["reason"] == "file type not used (.rvt)"
    assert f["sheet.XLSX"]["reason"] == "file type not used (.xlsx)"
    assert f["README"]["reason"] == "file type not used (no suffix)"
    assert staged_files(out_for(env)) == sorted(["brief.yaml", "notes.TXT", "photo.JPEG", "readme.md", "scan.TIFF",
                                                 "zemin.dxf"])
    m = manifest(env)
    assert m["totals"]["kept"] == 6 and m["totals"]["documents"] == 3
    assert m["skipped_by_reason"]["junk (system metadata file)"] == 5
    assert sum(m["skipped_by_reason"].values()) == m["totals"]["skipped"] == len(m["files"]) - 6
    assert set(m["allowed_suffixes"]) == {".pdf", ".dxf", ".dwg", ".jpg", ".jpeg", ".png", ".tif", ".tiff",
                                          ".yaml", ".yml", ".txt", ".md"}


# --------------------------------------------------------------------------
# NFC names, subfolders, style photos, collisions
# --------------------------------------------------------------------------

def test_nfd_names_are_staged_nfc_and_the_original_is_recorded(env):
    up = upload(env)
    write(up / NFD_NAME, b"pdf")
    write(up / unicodedata.normalize("NFD", "Çizimler") / unicodedata.normalize("NFD", "kesit_ğ.dxf"))
    stage(env)
    nfc_name = unicodedata.normalize("NFC", NFD_NAME)
    assert NFD_NAME != nfc_name
    assert staged_files(out_for(env)) == sorted([nfc_name, "Çizimler__kesit_ğ.dxf"])
    for name in staged_files(out_for(env)):
        assert unicodedata.is_normalized("NFC", name)
    f = by_path(manifest(env))
    assert f[NFD_NAME]["path_nfc"] == nfc_name and f[NFD_NAME]["staged"] == nfc_name
    assert f[NFD_NAME]["sha256"] == hashlib.sha256(b"pdf").hexdigest() and f[NFD_NAME]["size"] == 3


def test_subfolder_documents_are_staged_at_the_top_level(env):
    up = upload(env)
    write(up / "plans" / "zemin.dxf")
    write(up / "plans" / "kat1" / "1_kat.pdf")
    write(up / "scans" / "eski.png")
    write(up / "style_photos" / "salon.jpg")
    write(up / "style_photos" / "ref" / "mutfak.jpg")
    write(up / "style_photos" / "liste.txt")
    write(up / "brief.yaml", b"style: Modern\n")
    write(up / "eski" / "brief.yaml")
    r = stage(env)
    out = out_for(env)
    assert r.status == "ok"
    assert staged_files(out) == ["brief.yaml", "eski__brief.yaml", "plans__kat1__1_kat.pdf", "plans__zemin.dxf",
                                 "scans__eski.png", "style_photos/ref__mutfak.jpg", "style_photos/salon.jpg"]
    f = by_path(manifest(env))
    assert f["style_photos/liste.txt"]["reason"] == "not an image (style_photos/ holds photos only)"
    assert "at the top level" in f["eski/brief.yaml"]["note"] and f["brief.yaml"]["note"] is None
    # The pipeline reads the top level only: every document is visible to it now.
    assert [p.name for p in project_documents(out)] == ["plans__kat1__1_kat.pdf", "plans__zemin.dxf",
                                                       "scans__eski.png"]
    assert manifest(env)["totals"]["style_photos"] == 2 and manifest(env)["totals"]["documents"] == 3
    assert out.name == ALIAS                            # the pipeline names the building after the folder


def test_brief_spelling_note(env):
    up = upload(env)
    write(up / "a.dxf")
    write(up / "Brief.yml")
    stage(env)
    assert "brief.yaml at the top level" in by_path(manifest(env))["Brief.yml"]["note"]


@pytest.mark.parametrize("names", [
    ["plans/a.pdf", "plans__a.pdf"],                                   # subfolder vs top level
    [unicodedata.normalize("NFD", "Şema.pdf"), unicodedata.normalize("NFC", "Şema.pdf")],   # NFD vs NFC
    ["Plan.PDF", "plan.pdf"],                                          # letter case only
    ["style_photos/a/b.jpg", "style_photos/a__b.jpg"],
])
def test_staged_name_collision_is_needs_review(env, names):
    up = upload(env)
    for i, name in enumerate(names):
        write(up / name, bytes([i]))
    old = write(out_for(env) / "old.pdf")
    write(up / "base.dxf")
    r = stage(env)
    assert r.status == "needs_review" and r.reasons == ["document name collision"]
    assert not out_for(env).exists() and not old.exists()
    noted = [f for f in manifest(env)["files"] if "name collision" in (f["note"] or "")]
    assert len(noted) == 2                             # both files are marked


# --------------------------------------------------------------------------
# Caps, unstageable names, DWG
# --------------------------------------------------------------------------

def test_per_file_cap_is_needs_review(env):
    up = upload(env)
    write(up / "a.dxf", b"1" * 10)
    write(up / "huge.pdf", b"2" * 101)
    write(up / "huge.zip", b"3" * 500)                 # not an allowed type: listed, does not block
    r = stage(env, file_cap=100)
    assert r.reasons == [I.OVER_FILE_CAP] and not out_for(env).exists()
    f = by_path(manifest(env))
    assert not f["huge.pdf"]["kept"] and "per-file cap" in f["huge.pdf"]["reason"]
    assert manifest(env)["caps"]["file_bytes"] == 100
    assert I.FILE_CAP_BYTES == 500_000_000 and I.PROJECT_CAP_BYTES == 2_000_000_000


def test_project_cap_is_needs_review(env):
    up = upload(env)
    for i in range(3):
        write(up / f"p{i}.pdf", b"x" * 40)
    assert stage(env, file_cap=100, project_cap=119).reasons == [I.OVER_PROJECT_CAP]
    assert stage(env, file_cap=100, project_cap=120).status == "ok"


def test_unstageable_names_are_needs_review(env):
    up = upload(env)
    write(up / "a.dxf")
    write(up / "bad\nname.pdf")
    assert stage(env).reasons == [I.BAD_NAME]
    m = manifest(env)
    assert by_path(m)["bad\nname.pdf"]["reason"] == "file name has control characters"
    os.remove(up / "bad\nname.pdf")
    fd = os.open(os.fsencode(str(up)) + b"/plan\xff.pdf", os.O_CREAT | os.O_WRONLY)
    os.close(fd)
    assert stage(env).reasons == [I.BAD_NAME]
    f = [x for x in manifest(env)["files"] if x["path"].startswith("plan")][0]
    assert f["path"] == "plan\\xff.pdf" and f["reason"] == "file name is not UTF-8"
    os.remove(os.fsencode(str(up)) + b"/plan\xff.pdf")
    write(up / (("u" * 120) + ("/" + "v" * 140) + ".pdf"))
    assert stage(env).reasons == [I.BAD_NAME]


def test_unreadable_file_is_needs_review(env, monkeypatch):
    up = upload(env)
    write(up / "a.dxf")
    write(up / "b.pdf")
    write(out_for(env) / "old.pdf")
    real_copy = I._sha256_copy

    def failing_copy(src, dst):
        if src.name == "b.pdf":
            raise PermissionError("denied")
        return real_copy(src, dst)

    monkeypatch.setattr(I, "_sha256_copy", failing_copy)
    r = stage(env)
    assert r.reasons == [I.UNREADABLE] and not out_for(env).exists()
    assert not out_for(env).with_name(ALIAS + ".tmp").exists()
    f = by_path(manifest(env))
    assert f["b.pdf"]["reason"] == "could not be read" and f["a.dxf"]["sha256"] is None


def test_dwg_rule(env):
    up = upload(env)
    write(up / "zemin.dxf")
    write(up / "ZEMIN.dwg")                            # a DXF of the same stem exists: not staged
    write(up / "kat1.dwg")                             # alone: staged with the note
    write(up / "sub" / "zemin.dwg")                    # other folder: alone there
    r = stage(env)
    assert r.status == "ok"
    f = by_path(manifest(env))
    assert f["ZEMIN.dwg"]["reason"] == "DWG not read: the DXF of the same name is used" and not f["ZEMIN.dwg"]["kept"]
    assert f["kat1.dwg"]["note"] == "DWG is not read; export DXF from the CAD program" and f["kat1.dwg"]["kept"]
    assert f["sub/zemin.dwg"]["note"] == I.DWG_NOTE and f["sub/zemin.dwg"]["staged"] == "sub__zemin.dwg"
    assert f["zemin.dxf"]["note"] is None
    assert staged_files(out_for(env)) == ["kat1.dwg", "sub__zemin.dwg", "zemin.dxf"]


# --------------------------------------------------------------------------
# Rebuild, upload untouched, manifest
# --------------------------------------------------------------------------

def test_restage_rebuilds_and_never_touches_the_upload(env):
    up = upload(env)
    write(up / "a.dxf", b"one")
    write(up / "b.pdf", b"two")
    write(up / ".DS_Store")
    before = tree_digest(up)
    assert stage(env).status == "ok"
    out = out_for(env)
    assert staged_files(out) == ["a.dxf", "b.pdf"]
    write(out.with_name(out.name + ".tmp") / "half.pdf")      # an interrupted earlier run
    write(out / "added_by_hand.pdf")
    assert tree_digest(up) == before
    (up / "b.pdf").unlink()
    write(up / "a.dxf", b"changed")
    assert stage(env).status == "ok"
    assert staged_files(out) == ["a.dxf"] and (out / "a.dxf").read_bytes() == b"changed"
    assert not out.with_name(out.name + ".tmp").exists() and not out.with_name(out.name + ".old").exists()
    assert by_path(manifest(env))["a.dxf"]["sha256"] == hashlib.sha256(b"changed").hexdigest()
    # The upload is never written: only the one file this test removed and the one it changed differ.
    after = {p: h for p, h, _ in tree_digest(up)}
    assert set(after) == {"a.dxf", ".DS_Store"}


def test_manifest_fields_and_location(env):
    up = upload(env)
    write(up / "a.dxf", b"abc")
    write(up / "Thumbs.db", b"zz")
    r = stage(env)
    path = env["po"] / ALIAS / "intake_manifest.json"
    assert r.manifest_path == path and path.is_file()
    m = manifest(env)
    for key in ("schema_version", "kind", "alias", "status", "reasons", "upload", "staged", "caps", "totals",
                "skipped_by_reason", "files", "warnings", "created_utc", "seconds"):
        assert key in m, key
    assert m["schema_version"] == "0.1" and m["status"] == "ok" and m["reasons"] == []
    assert m["upload"] == (env["pp"] / ALIAS).as_posix() and m["staged"] == out_for(env).as_posix()
    a = by_path(m)["a.dxf"]
    assert a == {"path": "a.dxf", "path_nfc": "a.dxf", "staged": "a.dxf", "size": 3,
                 "sha256": hashlib.sha256(b"abc").hexdigest(), "kept": True, "reason": None, "note": None}
    t = by_path(m)["Thumbs.db"]
    assert t["kept"] is False and t["sha256"] is None and t["staged"] is None and t["size"] == 2
    assert m["totals"] == {"files": 2, "kept": 1, "skipped": 1, "kept_bytes": 3, "documents": 1,
                           "style_photos": 0, "notes": 0, "blocking": 0}
    # --manifest elsewhere, and an --out outside the input/ layout puts it next to --out.
    other = env["po"] / "elsewhere" / ALIAS
    I.stage_project(ALIAS, other, root=env["pp"], repo_root=env["repo"])
    assert (env["po"] / "elsewhere" / "intake_manifest.json").is_file()
    I.stage_project(ALIAS, out_for(env), root=env["pp"], repo_root=env["repo"], manifest=env["po"] / "m.json")
    assert json.loads((env["po"] / "m.json").read_text(encoding="utf-8"))["status"] == "ok"


def test_a_staged_synthetic_project_reads_like_the_committed_one(env):
    """synthetic-01 uploaded with its documents in a subfolder: the staged folder lists the same documents."""
    up = upload(env, "selftest-02")
    src = ROOT / "projects" / "synthetic-01"
    for p in src.iterdir():
        if p.is_file():
            dest = up / "belgeler" / p.name if p.suffix != ".yaml" else up / p.name
            write(dest, p.read_bytes())
    shutil.copytree(src / "truth", up / "truth")
    r = I.stage_project("selftest-02", out_for(env, "selftest-02"), root=env["pp"], repo_root=env["repo"])
    assert r.status == "ok"
    staged = project_documents(out_for(env, "selftest-02"))
    committed = project_documents(src)
    assert [p.name for p in staged] == [f"belgeler__{p.name}" for p in committed]
    assert (out_for(env, "selftest-02") / "brief.yaml").read_bytes() == (src / "brief.yaml").read_bytes()
    assert not any("truth" in p for p in staged_files(out_for(env, "selftest-02")))


def test_truth_outputs_and_debug_folders_are_never_documents(env):
    """synthetic-02 keeps the vector source of its scan in truth/plan.pdf: staged, it would turn the
    scan-only self-test into an ok project. The pipeline's own skip list says these folders never hold
    documents."""
    from wenart.ingest.classify import SKIP_DIRS
    assert set(I.NOT_DOCUMENT_DIRS) == set(SKIP_DIRS)
    up = upload(env, "selftest-02")
    src = ROOT / "projects" / "synthetic-02"
    shutil.copytree(src, up, dirs_exist_ok=True)
    write(up / "Debug" / "x.pdf")
    write(up / "outputs" / "building.json")
    write(up / "plans" / "truth" / "kept.pdf")              # only the top-level folders are excluded
    r = I.stage_project("selftest-02", out_for(env, "selftest-02"), root=env["pp"], repo_root=env["repo"])
    assert r.status == "ok"
    assert staged_files(out_for(env, "selftest-02")) == ["plan_photo.jpg", "plan_scan.png", "plans__truth__kept.pdf"]
    f = by_path(manifest(env, "selftest-02"))
    assert f["truth/plan.pdf"]["reason"].startswith("folder truth/ is not read")
    assert f["Debug/x.pdf"]["reason"].startswith("folder Debug/ is not read")
