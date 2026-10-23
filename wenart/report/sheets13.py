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

Fix round after P3, part 2 (17 Oct 2026, docs/milestone13.md §14.9): a replayed aerial that the build re-pitched
for the CLAUDE.md horizon rule (``build.repitch_replayed_aerials``: the scene manifest camera's ``replay`` with
``status: repitched``) is not frame-identical to its baseline. Its sheet gets a fourth caption line
(``camera_note``), its record a ``camera_note`` and the index table a ``note`` column, so the viewer knows why the two
frames differ; the caption band grows by one line for it (the other sheets keep their size).

Fix round after P4a (17 Oct 2026, the library lens of the P4a analysis):

- What: (1) the "before" / "after" labels sit on a dark box (``LABEL_BOX``), so they stay readable on a pale sky; a
  grey tile's own text goes below the label (``TILE_TEXT_Y``), not over it. (2) A long caption line (a view with
  several flagged assets, a re-pitch note) wraps over up to ``CAPTION_MAX_LINES`` lines (``wrap``) instead of being
  cut with "..."; a line still longer ends with "(full line in sheets13.md)". (3) The "before" preview of a camera is
  used only when the baseline's views (its final manifest, else its render manifest) list that camera: a preview
  file of a camera the baseline report does not list (an earlier run's file in the baseline folder) is left out, the
  sheet says so on the tile and in the caption, and the record and the index name the file
  (``before_left_out``). (4) "commercial-safe: not recorded" is drawn in the grey of a missing record, not in the
  colour of a flagged view (``_colour`` matched ": no" inside ": not").
- Why: on P4a's real02 sheets the "after" label vanished on ext_5's white sky, "before" and "before: no preview"
  were drawn over each other on ext_6.001, the salon, banyo_2 and mutfak captions lost flagged asset ids to "...",
  and the M11 baseline folder's cam_r_L1_koridor_2_1/2/3 previews (files of a run before commit 93aff07; its final
  manifest has 41 views without them) were shown as "before" while the caption said "no view in this run" and
  metrics13 gave them no EV or score.
- How: PIL only, as before; a sheet whose caption fits in three lines keeps its size (``CAPTION_HEIGHT``).
- (5, integration) A camera the agent moved off its replayed pose (the scene record's ``replaced_replayed``,
  ``build.merge_agent_cameras``; P4a's ext_6) gets the note "camera moved by the agent from (x, y, z) to (x, y, z):
  not the baseline pose (<the agent's reason>)" (``camera_note``), so the viewer knows the two frames are two poses.

Fix round after P6b (23 Oct 2026; docs/milestone13.md §7): a replayed interior camera the build moved off a piece of
its build (the scene record's ``replay`` with ``status: moved``, ``camsearch.move_blocked_replayed``; P6b's
yasama_3_2 stood inside a 2.02 m fridge) gets the note "replayed camera moved by the build 0.72 m from (x, y) to
(x, y), same yaw and lens: the fridge f_L0_202 of this build contains the baseline pose (docs/milestone13.md §7)"
(``camera_note``), so the sheet does not show a moved view as the baseline's frame.
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
# fix round after P4a (module docstring)
LINE_HEIGHT = 21                  # px per caption line
LABEL_BOX = (0, 0, 0)             # the box behind the "before" / "after" labels
LABEL_PAD = 4
TILE_TEXT_Y = 40                  # a grey tile's text starts below the label box
CAPTION_MAX_LINES = 3             # lines per caption entry; the rest is in sheets13.md
CAPTION_INDENT = "        "       # continuation lines of a wrapped caption entry
MORE = " ... (full line in sheets13.md)"
NOT_A_BASELINE_VIEW = "not a view of the baseline report"


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
    """Green for "commercial-safe: yes", orange for "commercial-safe: no (...)", grey for anything else (fix round
    after P4a: "commercial-safe: not recorded" is no flagged view)."""
    if line == "commercial-safe: yes":
        return SAFE_COLOUR
    if line == "commercial-safe: no" or line.startswith("commercial-safe: no "):
        return FLAGGED_COLOUR
    return NOT_RECORDED_COLOUR


def _text_width(font, text: str) -> float:
    try:
        return float(font.getlength(text))
    except AttributeError:                        # a bitmap font without getlength: about 9 px per character
        return 9.0 * len(text)


def wrap(text: str, font, width: float, max_lines: int = CAPTION_MAX_LINES) -> list[str]:
    """Fix round after P4a: ``text`` broken at spaces into lines no wider than ``width`` px (continuation lines start
    with ``CAPTION_INDENT``), at most ``max_lines``; a text that needs more ends its last line with ``MORE``. A
    single word wider than the line is cut at the width."""
    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        candidate = word if not current else f"{current} {word}"
        if not current or _text_width(font, candidate) <= width:
            current = candidate
            continue
        lines.append(current)
        current = CAPTION_INDENT + word
    lines.append(current)
    lines = [_cut(line, font, width) for line in lines]
    if len(lines) > max_lines:
        last = lines[max_lines - 1]
        while last and _text_width(font, last + MORE) > width:
            last = last[:-1]
        lines = lines[:max_lines - 1] + [last.rstrip() + MORE]
    return lines


def _cut(line: str, font, width: float) -> str:
    while len(line) > 1 and _text_width(font, line) > width:
        line = line[:-1]
    return line


def _tile(path: Optional[Path], label: str, message: Optional[str] = None):
    """The preview scaled to ``TILE_HEIGHT``, or a grey tile that says what is missing (``message``, default
    "<label>: no preview"); fix round after P4a: the text starts below the label box (``TILE_TEXT_Y``)."""
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
    font = _font(18)
    y = TILE_TEXT_Y
    for line in wrap(message or f"{label}: no preview", font, img.width - 2 * MARGIN, max_lines=4):
        ImageDraw.Draw(img).text((MARGIN, y), line, fill=TEXT, font=font)
        y += 24
    return img


def _label(draw, xy: tuple, text: str, font) -> None:
    """Fix round after P4a: a label on a dark box (``LABEL_BOX``), readable on any image."""
    x, y = xy
    left, top, right, bottom = draw.textbbox((x, y), text, font=font)
    draw.rectangle((left - LABEL_PAD, top - LABEL_PAD, right + LABEL_PAD, bottom + LABEL_PAD), fill=LABEL_BOX)
    draw.text((x, y), text, fill=TEXT, font=font)


def caption_lines(caption: list[tuple[str, tuple]], width: float) -> list[tuple[str, tuple]]:
    """The caption entries wrapped to ``width`` px (fix round after P4a), each line with its entry's colour."""
    font = _font(16)
    return [(line, colour) for text, colour in caption for line in wrap(text, font, width)]


def compose(before: Optional[Path], after: Optional[Path], caption: list[tuple[str, tuple]],
            before_message: Optional[str] = None):
    """One sheet: before | after over a caption band (``caption``: (text, colour) entries, wrapped to the sheet's
    width); ``before_message``: the grey tile's text when the before side has no preview."""
    from PIL import Image, ImageDraw
    left = _tile(before, "before", before_message)
    right = _tile(after, "after")
    width = left.width + GAP + right.width
    lines = caption_lines(caption, width - 2 * MARGIN)
    band = max(CAPTION_HEIGHT, 6 + LINE_HEIGHT * len(lines) + 3)  # part 2: a fourth line (camera_note) adds 21 px
    sheet = Image.new("RGB", (width, TILE_HEIGHT + band), BACKGROUND)
    sheet.paste(left, (0, 0))
    sheet.paste(right, (left.width + GAP, 0))
    draw = ImageDraw.Draw(sheet)
    font = _font(16)
    y = TILE_HEIGHT + 6
    for text, colour in lines:
        draw.text((MARGIN, y), text, fill=colour, font=font)
        y += LINE_HEIGHT
    _label(draw, (MARGIN, 8), "before", font)
    _label(draw, (left.width + GAP + MARGIN, 8), "after", font)
    return sheet


MOVED_NOTE_FALLBACK = "replayed camera moved by the build off a piece of its build (docs/milestone13.md §7)"


def moved_note(rp: dict, position=None) -> str:
    """Fix round after P6b (module docstring): the note of a replayed camera the build moved (``replay.status ==
    "moved"``): how far, from where to where, and the piece; the plain fallback when the record lacks a value."""
    try:
        old = [float(v) for v in rp["position_old"][:2]]
        new = [float(v) for v in (position or [])[:2]]
        dist = float(rp["moved_m"])
    except (KeyError, TypeError, ValueError, IndexError):
        return MOVED_NOTE_FALLBACK
    where = f"from ({old[0]:.2f}, {old[1]:.2f})" + (f" to ({new[0]:.2f}, {new[1]:.2f})" if len(new) == 2 else "")
    piece = " ".join(str(v) for v in (rp.get("blocked_by_type"), rp.get("blocked_by")) if v)
    how = "contains" if rp.get("trigger") == "inside" else "blocks"
    what = f": the {piece} of this build {how} the baseline pose" if piece else ""
    return f"replayed camera moved by the build {dist:.2f} m {where}, same yaw and lens{what} (docs/milestone13.md §7)"


def camera_note(cam: Optional[dict]) -> Optional[str]:
    """Fix round part 2 (module docstring): the note of a replayed camera the build re-pitched, from the scene
    manifest camera record (``replay.status == "repitched"``), else None. Fix round after P4a: a camera the agent
    moved off its replayed pose (``replaced_replayed``, ``build.merge_agent_cameras``) says so first. Fix round after
    P6b: a replayed camera the build moved off a piece (``replay.status == "moved"``) gets ``moved_note``."""
    moved = (cam or {}).get("replaced_replayed")
    if isinstance(moved, dict):
        agent = (cam or {}).get("agent") or {}
        old, new = moved.get("position") or [], (cam or {}).get("position") or []
        where = ""
        try:
            if len(old) == 3 and len(new) == 3:
                where = (f" from ({', '.join(f'{float(v):.1f}' for v in old)}) to "
                         f"({', '.join(f'{float(v):.1f}' for v in new)})")
        except (TypeError, ValueError):
            where = ""
        return f"camera moved by the agent{where}: not the baseline pose" + \
            (f" ({agent['reason']})" if agent.get("reason") else "")
    rp = (cam or {}).get("replay")
    if isinstance(rp, dict) and rp.get("status") == "moved":
        return moved_note(rp, (cam or {}).get("position"))
    if not isinstance(rp, dict) or rp.get("status") != "repitched":
        return None
    try:
        old, new = abs(float(rp["pitch_deg_old"])), abs(float(rp["pitch_deg"]))
        lens, lens_old = float(rp["lens_mm"]), float(rp["lens_mm_old"])
        h_old, h_new = float(rp["horizon_frac_old"]), float(rp["horizon_frac"])
    except (KeyError, TypeError, ValueError):
        return "replayed camera re-pitched by the build (CLAUDE.md horizon rule)"
    lens_text = f"{lens:g} mm" + (f" (was {lens_old:g} mm)" if abs(lens - lens_old) > 1e-6 else "")
    return (f"replayed aerial re-pitched from {old:.1f} to {new:.1f} degrees down at {lens_text} (horizon "
            f"{h_old:.2f} -> {h_new:.2f} of the frame height; CLAUDE.md horizon rule)")


def before_preview(before: M.Run, views_before: dict, camera: str) -> tuple[Optional[Path], Optional[Path]]:
    """Fix round after P4a: ``(preview, left_out)`` of the baseline for ``camera``: its preview when the baseline's
    views list the camera, else ``(None, the file found by name)`` (an earlier run's file; None when there is none)."""
    found = M._preview(before, camera)
    if camera in views_before:
        return found, None
    return None, found


def sheets(project_out, baseline_out, out_dir) -> dict:
    """Write one before | after JPEG per camera of the "after" run into ``out_dir``; returns
    ``{"sheets": {camera: file}, "missing_before": [cameras], "missing_after": [cameras], "baseline_only":
    [cameras], "before_left_out": [{camera, file, reason}], "index": "sheets13.md", "warnings": [...]}``."""
    after = M.locate(project_out)
    before = M.locate(baseline_out)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    views_after = _view_map(after)
    views_before = _view_map(before)
    rtypes = M._room_types(after) or M._room_types(before)
    cams_after = M._scene_cameras(after)
    records = []
    written: dict = {}
    missing_before, missing_after, left_out = [], [], []
    for cam, view in views_after.items():
        pa = M._preview(after, cam)
        pb, stale = before_preview(before, views_before, cam)
        if pa is None:
            missing_after.append(cam)
        if pb is None:
            missing_before.append(cam)
        if stale is not None:
            left_out.append({"camera": cam, "file": str(stale), "reason": NOT_A_BASELINE_VIEW})
        room = view.get("room_id") or (views_before.get(cam) or {}).get("room_id") or "exterior"
        rtype = rtypes.get(room) or view.get("room_type") or ""
        line_b = _line(views_before.get(cam))
        line_a = _line(view)
        before_text = f"before: {line_b}" + (f" (the baseline folder's {stale.name} is left out: "
                                             f"{NOT_A_BASELINE_VIEW})" if stale is not None else "")
        caption = [(f"{cam}  ({room}{', ' + str(rtype) if rtype else ''})", TEXT),
                   (before_text, _colour(line_b)),
                   (f"after:  {line_a}", _colour(line_a))]
        note = camera_note(cams_after.get(cam))
        if note:
            caption.append((f"after:  {note}", TEXT))
        message = ("before: no view of this camera in the baseline report (an earlier run's preview file in the "
                   "baseline folder is left out)" if stale is not None else
                   "before: no view of this camera in the baseline report" if cam not in views_before else None)
        sheet = compose(pb, pa, caption, before_message=message)
        name = f"{cam}{SUFFIX}"
        info = C.save_jpeg_under(sheet, out / name)
        written[cam] = name
        records.append({"camera": cam, "room_id": room, "room_type": rtype, "file": name,
                        "before": str(pb) if pb else None, "after": str(pa) if pa else None,
                        "before_left_out": str(stale) if stale is not None else None,
                        "before_line": line_b, "after_line": line_a, "camera_note": note, "bytes": info["bytes"]})
    baseline_only = sorted(set(views_before) - set(views_after))
    warnings = list(after.warnings) + [f"baseline: {w}" for w in before.warnings]
    if not views_before:
        warnings.append("baseline: no final or render manifest lists a view, so no baseline preview is used")
    result = {"project": after.name, "project_out": str(after.root), "baseline_out": str(before.root),
              "sheets": written, "records": records, "missing_before": missing_before,
              "missing_after": missing_after, "baseline_only": baseline_only, "before_left_out": left_out,
              "index": INDEX_MD, "warnings": warnings}
    (out / INDEX_MD).write_text(index_markdown(result), encoding="utf-8")
    C.write_json(out / INDEX_JSON, result)
    return result


def index_markdown(result: dict) -> str:
    lines = [f"# Before | after sheets: {result['project']}", "",
             f"After: `{result['project_out']}`; before: `{result['baseline_out']}`. One sheet per camera of the "
             "after run (docs/milestone13.md §7, same views by camera name); the before image is used only for a "
             "camera the baseline report lists (fix round after P4a); the caption carries the commercial-safe line of "
             "each side.", ""]
    rows = [[r["camera"], r["room_id"], r["room_type"], r["before_line"], r["after_line"],
             f"[{r['file']}]({r['file']})", r.get("camera_note") or ""] for r in result["records"]]
    lines += C.table(["camera", "room", "type", "before", "after", "sheet", "note"], rows) if rows else ["No view."]
    for key, label in (("missing_before", "No baseline preview"), ("missing_after", "No preview of the run"),
                       ("baseline_only", "Cameras only in the baseline")):
        if result.get(key):
            lines += ["", f"{label}: " + ", ".join(result[key]) + "."]
    if result.get("before_left_out"):                 # fix round after P4a
        lines += ["", "Baseline previews left out (the baseline folder holds them, but its report does not list "
                      "these cameras: files of an earlier run; the sheet shows no before image):", ""]
        lines += C.bullets([f"{r['camera']}: `{r['file']}`" for r in result["before_left_out"]])
    if result.get("warnings"):
        lines += ["", "Warnings:", ""] + C.bullets(result["warnings"])
    return "\n".join(lines) + "\n"
