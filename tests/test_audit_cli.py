"""Milestone 12 track B: ``python -m wenart.assets audit`` end to end on a small catalogue (the CPU dry audit, the
licence step, the writer refusing a dry audit) and the dispatch from ``python -m wenart.assets``."""
import copy
import json

from wenart.assets import __main__ as assets_main
from wenart.assets.audit import cli
from wenart.assets.audit import items as I


def small_catalogues(tmp_path):
    lib = json.loads(I.LIBRARY_PATH.read_text(encoding="utf-8"))
    keep = {"abo_B0718WYQ8D", "abo_B01N6AQX0A"}
    nc = next(e for e in lib["entries"] if e["licence"] == "CC-BY-NC-4.0")
    gen = next(e for e in lib["entries"] if e["source"] == "generated")
    small = copy.deepcopy(lib)
    small["entries"] = [e for e in lib["entries"] if e["id"] in keep] + [copy.deepcopy(nc), copy.deepcopy(gen)]
    small["entries"][2].pop("audit", None)
    small["entries"][3]["via"] = "Objaverse (allenai/objaverse, ODC-By 1.0)"
    small["decor"] = []
    small["notes"] = []
    p = tmp_path / "catalog_library.json"
    p.write_text(json.dumps(small, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    ph = tmp_path / "catalog.json"
    ph.write_text(I.POLYHAVEN_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return p, ph, nc["id"], gen["id"]


def test_licences_step_dry_then_written(tmp_path):
    lib, ph, nc_id, gen_id = small_catalogues(tmp_path)
    before = lib.read_text(encoding="utf-8")
    assert cli.main(["licences", "--catalog", str(lib)]) == 0
    assert lib.read_text(encoding="utf-8") == before                     # not written without --write
    assert cli.main(["licences", "--catalog", str(lib), "--write", "--checked-utc", "2026-10-10T20:00:00Z"]) == 0
    doc = json.loads(lib.read_text(encoding="utf-8"))
    by = {e["id"]: e for e in doc["entries"]}
    assert by[nc_id]["audit"]["status"] == "removed" and by[gen_id]["via"].startswith("generated for WenArt_RUN")


def test_dry_audit_writes_tables_sheets_and_gaps(tmp_path):
    lib, ph, nc_id, _gen = small_catalogues(tmp_path)
    out = tmp_path / "results"
    assert cli.main(["dry", "--out", str(out), "--catalog", str(lib), "--polyhaven", str(ph),
                     "--generated-utc", "2026-10-10T21:00:00Z"]) == 0
    dry = out / "audit" / "dry"
    doc = json.loads((dry / "audit.json").read_text(encoding="utf-8"))
    by = {r["id"]: r for r in doc["items"]}
    assert doc["mode"] == "dry" and doc["generated_utc"] == "2026-10-10T21:00:00Z"
    assert by[nc_id]["status"] == "removed"
    assert by["abo_B01N6AQX0A"]["status"] == "removed"                   # the air bed: "Luchtbed"
    assert by["abo_B0718WYQ8D"]["expected"] == "keep?"
    for name in ("audit.csv", "audit.md", "code.json", "gaps.json", "gaps.md"):
        assert (dry / name).is_file(), name
    assert (dry / "contact" / "bed_double.jpg").is_file()
    md = (dry / "audit.md").read_text(encoding="utf-8")
    assert "## Models to remove" in md and "luchtbed" in md
    # the writer never takes a dry audit
    assert cli.main(["write", "--out", str(out), "--catalog", str(lib), "--polyhaven", str(ph)]) == 1


def test_python_m_wenart_assets_dispatches_audit_and_growth(tmp_path, capsys):
    assert assets_main.main(["audit", "status", "--out", str(tmp_path)]) == 0
    assert '"audit.json": false' in capsys.readouterr().out
    assert assets_main.main(["growth", "abo", "ingest", "--out", str(tmp_path)]) == 1
    assert "refused" in capsys.readouterr().out
