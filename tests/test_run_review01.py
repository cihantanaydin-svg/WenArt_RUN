"""The ``needs_review`` test project ``tests/fixtures/projects/review-01`` (docs/milestone7.md §9.1).

What: two small vector PDF plan pages without a level title, each with a
hatched wall ring (the CAD convention of §2.4) and two English room names,
so both pass the generic plan rule of §2.1 and the project stops with
``needs_review`` ("cannot order untitled plan pages"). It replaces
synthetic-02 (a normal raster project since M7) as the smoke run's
``needs_review`` project and as the source of the private self-test
(``selftest-02``).

The PDFs are written by ``write_review01`` with reportlab's invariant mode
(no time stamp, no random id), so the committed bytes are reproducible:
``python tests/test_run_review01.py`` rewrites them.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "projects" / "review-01"
PAGES = {"plan_a.pdf": ("BEDROOM", "KITCHEN"), "plan_b.pdf": ("LIVING ROOM", "BATH")}
REASON = "cannot order untitled plan pages (plan_a.pdf p1, plan_b.pdf p1)"


def _hatch(x0, y0, x1, y1, step=1.2):
    """45-degree hatch lines clipped to the box (x0, y0)-(x1, y1) (a wall drawn the CAD way)."""
    out, k = [], x0 - (y1 - y0)
    while k <= x1:
        a = (max(k, x0), y0 + max(k, x0) - k)
        b = (min(k + (y1 - y0), x1), y0 + min(k + (y1 - y0), x1) - k)
        if b[0] > a[0]:
            out.append((round(a[0], 3), round(a[1], 3), round(b[0], 3), round(b[1], 3)))
        k += step
    return out


def write_page(path: Path, labels: tuple) -> Path:
    """One A4 landscape page: an outer wall ring 400 x 300 pt (6 pt thick) with a middle wall, both hatched and
    outlined, and one room name in each half. No title, no dimension, no scale note."""
    from reportlab.pdfgen import canvas as rl_canvas
    c = rl_canvas.Canvas(str(path), pagesize=(842, 595), invariant=1)
    c.setLineWidth(0.3)
    x0, y0, x1, y1, t = 200.0, 140.0, 600.0, 440.0, 6.0
    mid = (x0 + x1) / 2
    bands = [(x0, y0, x1, y0 + t), (x0, y1 - t, x1, y1), (x0, y0, x0 + t, y1), (x1 - t, y0, x1, y1),
             (mid - t / 2, y0, mid + t / 2, y1)]
    for bx0, by0, bx1, by1 in bands:
        for line in _hatch(bx0, by0, bx1, by1):
            c.line(*line)
        c.rect(bx0, by0, bx1 - bx0, by1 - by0)
    c.setFont("Helvetica", 10)
    c.drawString((x0 + mid) / 2 - 25, (y0 + y1) / 2, labels[0])
    c.drawString((mid + x1) / 2 - 25, (y0 + y1) / 2, labels[1])
    c.showPage()
    c.save()
    return path


def write_review01(folder: Path = FIXTURE) -> list[Path]:
    folder.mkdir(parents=True, exist_ok=True)
    return [write_page(folder / name, labels) for name, labels in PAGES.items()]


def test_committed_pages_are_reproducible(tmp_path):
    pytest.importorskip("reportlab")
    for path in write_review01(tmp_path):
        assert path.read_bytes() == (FIXTURE / path.name).read_bytes(), path.name
    assert sorted(p.name for p in FIXTURE.iterdir()) == sorted(PAGES)


def test_both_untitled_pages_are_plans_that_cannot_be_ordered():
    from wenart.ingest.classify import classify_pages
    recs = classify_pages(FIXTURE)
    assert [(r.file, r.page_class, r.classifier) for r in recs] == [
        ("plan_a.pdf", "floor_plan", "generic_labels"), ("plan_b.pdf", "floor_plan", "generic_labels")]
    assert all(r.level_id is None and r.level_problem == REASON for r in recs)


def test_pipeline_stops_with_needs_review(tmp_path):
    out = tmp_path / "out"
    proc = subprocess.run([sys.executable, "-m", "wenart.ingest.pipeline", str(FIXTURE), "--out", str(out)],
                          cwd=ROOT, capture_output=True, text=True, timeout=600)
    assert proc.returncode == 1, proc.stdout[-2000:] + proc.stderr[-2000:]
    building = json.loads((out / "building.json").read_text(encoding="utf-8"))
    assert building["status"] == "needs_review"
    report = (out / "report.md").read_text(encoding="utf-8")
    assert REASON in report
    assert not (out / "recognition" / "requests.json").is_file() or \
        not json.loads((out / "recognition" / "requests.json").read_text(encoding="utf-8")).get("items")


if __name__ == "__main__":
    for written in write_review01():
        print(written)
