"""Before | after sheets of Milestone 13, one JPEG per camera (docs/milestone13.md §7, §13.2; track T8).

What: ``sheets(project_out, baseline_out, out_dir)`` writes ``<out_dir>/<camera>_before_after.jpg`` for every
rendered view of the "after" run (its final manifest's views, else its render manifest's cameras): the baseline's
preview of the same camera on the left, the run's on the right, both scaled to the same height, with a caption
that names the camera and its room and carries the two commercial-safe lines (``commercial-safe: yes`` / ``no
(flagged assets: ...)`` of each side; ``not recorded`` for a run before Milestone 13). A side without a preview
gets a grey tile that says so. ``<out_dir>/sheets13.md`` lists the sheets, ``sheets13.json`` the records::

    python -m wenart.report sheets13 --out outputs/real02 --baseline results/final/real02 --dir outputs/real02/final/sheets13

Why: the user's decision D6 compares the Milestone 13 renders with the committed runs on the same views (the
render stage replays the committed cameras, ``--cameras-from``); a viewer must see both at once, with the licence
line of each.

How: the previews are ``final/<cam>_final_preview.jpg`` (else ``renders/<cam>_preview.jpg``) of either layout
``wenart.report.metrics13.locate`` knows (the volume's project output or the committed ``results/<area>/<p>``);
PIL only; the JPEGs stay under the repo's 300 KB limit (``wenart.report.common.save_jpeg_under``); the cameras are
matched by name (real04's baseline has no camera records, so name and room are the match, §12 D6).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from wenart.report import common as C
from wenart.report import metrics13 as M

TILE_HEIGHT = 540                 # px per side; a 1920 x 1080 preview becomes 960 x 540
GAP = 8
CAPTION_HEIGHT = 72
MARGIN = 10
SUFFIX = "_before_after.jpg"
INDEX_MD = "sheets13.md"
INDEX_JSON = "sheets13.json"
BACKGROUND = (28, 28, 28)
TEXT = (235, 235, 235)
MISSING_TILE = (70, 70, 70)
SAFE_COLOUR = (120, 220, 140)
FLAGGED_COLOUR = (240, 150, 90)
NOT_RECORDED_COLOUR = (180, 180, 180)


def _font(size: int = 16):
    from PIL import ImageFont
    for name in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _view_map(run: M.Run) -> dict:
    """camera -> the view record (final manifest, else render manifest) of a run."""
    return {v["camera"]: v for v in M._views(run)}


def _line(view: Optional[dict]) -> str:
    from wenart.report.final import commercial_safe_line
    if view is None:
        return "no view in this run"
    return commercial_safe_line(view.get("commercial_safe"))


def _colour(line: str) -> tuple:
    if line.endswith(": yes"):
        return SAFE_COLOUR
    if ": no" in line:
        return FLAGGED_COLOUR
    return NOT_RECORDED_COLOUR


def _tile(path: Optional[Path], label: str):
    """The preview scaled to ``TILE_HEIGHT``, or a grey tile that says what is missing."""
    from PIL import Image, ImageDraw
    if path is not None:
        try:
            img = Image.open(path).convert("RGB")
            w, h = img.size
            if h != TILE_HEIGHT:
                img = img.resize((max(1, round(w * TILE_HEIGHT / h)), TILE_HEIGHT), Image.Resampling.LANCZOS)
            return img
        except OSError:
            pass
    img = Image.new("RGB", (round(TILE_HEIGHT * 16 / 9), TILE_HEIGHT), MISSING_TILE)
    ImageDraw.Draw(img).text((MARGIN, MARGIN), f"{label}: no preview", fill=TEXT, font=_font(18))
    return img


def compose(before: Optional[Path], after: Optional[Path], caption: list[tuple[str, tuple]]):
    """One sheet: before | after over a caption band (``caption``: (text, colour) lines)."""
    from PIL import Image, ImageDraw
    left = _tile(before, "before")
    right = _tile(after, "after")
    width = left.width + GAP + right.width
    sheet = Image.new("RGB", (width, TILE_HEIGHT + CAPTION_HEIGHT), BACKGROUND)
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + GAP, 0))
    draw = ImageDraw.Draw(sheet)
    font = _font(16)
    y = TILE_HEIGHT + 6
    for text, colour in caption:
        draw.text((MARGIN, y), text, fill=colour, font=font)
        y += 21
    draw.text((MARGIN, 4), "before", fill=TEXT, font=font)
    draw.text((left.width + GAP + MARGIN, 4), "after", fill=TEXT, font=font)
    return sheet


def _truncate(text: str, limit: int = 150) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."


def sheets(project_out, baseline_out, out_dir) -> dict:
    """Write one before | after JPEG per camera of the "after" run into ``out_dir``; returns
    ``{"sheets": {camera: file}, "missing_before": [cameras], "missing_after": [cameras], "baseline_only":
    [cameras], "index": "sheets13.md", "warnings": [...]}``."""
    after = M.locate(project_out)
    before = M.locate(baseline_out)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    views_after = _view_map(after)
    views_before = _view_map(before)
    rtypes = M._room_types(after) or M._room_types(before)
    records = []
    written: dict = {}
    missing_before, missing_after = [], []
    for cam, view in views_after.items():
        pa = M._preview(after, cam)
        pb = M._preview(before, cam)
        if pa is None:
            missing_after.append(cam)
        if pb is None:
            missing_before.append(cam)
        room = view.get("room_id") or (views_before.get(cam) or {}).get("room_id") or "exterior"
        rtype = rtypes.get(room) or view.get("room_type") or ""
        line_b = _line(views_before.get(cam))
        line_a = _line(view)
        caption = [(f"{cam}  ({room}{', ' + str(rtype) if rtype else ''})", TEXT),
                   (_truncate(f"before: {line_b}"), _colour(line_b)),
                   (_truncate(f"after:  {line_a}"), _colour(line_a))]
        sheet = compose(pb, pa, caption)
        name = f"{cam}{SUFFIX}"
        info = C.save_jpeg_under(sheet, out / name)
        written[cam] = name
        records.append({"camera": cam, "room_id": room, "room_type": rtype, "file": name,
                        "before": str(pb) if pb else None, "after": str(pa) if pa else None,
                        "before_line": line_b, "after_line": line_a, "bytes": info["bytes"]})
    baseline_only = sorted(set(views_before) - set(views_after))
    result = {"project": after.name, "project_out": str(after.root), "baseline_out": str(before.root),
              "sheets": written, "records": records, "missing_before": missing_before,
              "missing_after": missing_after, "baseline_only": baseline_only, "index": INDEX_MD,
              "warnings": list(after.warnings) + [f"baseline: {w}" for w in before.warnings]}
    (out / INDEX_MD).write_text(index_markdown(result), encoding="utf-8")
    C.write_json(out / INDEX_JSON, result)
    return result


def index_markdown(result: dict) -> str:
    lines = [f"# Before | after sheets: {result['project']}", "",
             f"After: `{result['project_out']}`; before: `{result['baseline_out']}`. One sheet per camera of the "
             "after run (docs/milestone13.md §7, same views by camera name); the caption carries the commercial-safe "
             "line of each side.", ""]
    rows = [[r["camera"], r["room_id"], r["room_type"], r["before_line"], r["after_line"],
             f"[{r['file']}]({r['file']})"] for r in result["records"]]
    lines += C.table(["camera", "room", "type", "before", "after", "sheet"], rows) if rows else ["No view."]
    for key, label in (("missing_before", "No baseline preview"), ("missing_after", "No preview of the run"),
                       ("baseline_only", "Cameras only in the baseline")):
        if result.get(key):
            lines += ["", f"{label}: " + ", ".join(result[key]) + "."]
    if result.get("warnings"):
        lines += ["", "Warnings:", ""] + C.bullets(result["warnings"])
    return "\n".join(lines) + "\n"
