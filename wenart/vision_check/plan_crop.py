"""Source-plan crop per view (docs/milestone5.md §5.2).

What: ``check/<cam>_plan.jpg`` (<= 300 KB): the source page that the camera's
room comes from, cropped to the room polygon + 0.5 m, with the camera, its
view cone (the camera's own lens on the 36 mm sensor: 18 or 16 mm since
Milestone 8) and every expected element's box
(``id type source``) drawn. It is always shown next to the render in the
report; as a second VLM image only in the plan A/B of the calibration.

How:

- Page: among ``building.documents[].pages[]`` of the camera's level that
  have a ``transform_to_building``, the page the room's evidence cites
  (file, and page for PDFs) wins; then floor plans before furniture plans,
  then the trust order DXF > DWG > PDF > scan > image > photo (a raster
  document by its ``source_kind``: a room citing both the scan and the photo
  of one plan gets the scan, review cross-1).
- Raster: a raster page (scan or photo, also a raster-only PDF page; it
  has ``rectified_image``) is drawn on its **rectified** image
  (``<project_out>/<rectified_image>``, milestone7.md §4.1): its page units
  are rectified pixel corners with y up (``wenart.ingest.rectify.page_flip``),
  so a page point (x, y) is image pixel corner (x, H - y) (H the rectified
  height), times the downscale; the original file would ignore the deskew,
  the photo homography and the y flip (review cross-1: crops 2-4 m off).
  Other pages: ``wenart.ingest.debug_image.raster_from_pdf/dxf/image`` (PDF
  pages at 300 dpi). A DWG is read from its converted DXF
  (``<project_out>/converted/<stem>.dxf``, where the ingest wrote it). The
  crop is scaled to 800..1200 px on its longest side before drawing, so the
  labels stay sharp.
- Mapping: building metres -> page units through the inverse of the page's
  ``transform_to_building`` (``wenart.geometry.invert_affine``) -> raster
  pixels (``PageRaster.to_pixels``) -> crop pixels (minus the crop origin,
  times the downscale). ``PlanMapping.to_crop`` is that chain, so a known
  building point lands on a known pixel (tested).
- Elements: furniture footprints and decor boxes from the building JSON,
  openings as their wall-centre rectangle (width x wall thickness); green
  ``from_documents``, orange ``added_by_ai``, dashed red ``unverified``.

Pillow and the ingest rasters are imported inside the functions.
"""
from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from wenart import geometry as G

MARGIN_M = 0.5
MAX_SIDE_PX = 1200
MIN_SIDE_PX = 800           # small crops (a room on a 1:100 PDF page) are scaled up before drawing
PDF_DPI = 300               # the ingest debug images use 100 dpi: a 4 m room would be ~160 px
MAX_JPEG_BYTES = 300_000
FORMAT_ORDER = {"dxf": 0, "dwg": 1, "pdf": 2, "image": 3}
# The trust order of the page choice: a raster document by its source kind (scan before photo), else by format.
TRUST_ORDER = {"dxf": 0, "dwg": 1, "pdf": 2, "raster_scan": 3, "image": 4, "raster_photo": 5}
RASTER_KINDS = ("raster_scan", "raster_photo")
CLASS_ORDER = {"floor_plan": 0, "furniture_plan": 1}
COLOURS = {"from_documents": (0, 150, 0), "added_by_ai": (235, 130, 0)}
OTHER_COLOUR = (120, 120, 120)
UNVERIFIED_COLOUR = (220, 20, 20)
CAMERA_COLOUR = (30, 90, 220)


@dataclass
class PlanMapping:
    """Building metres -> pixels of the crop image."""
    to_page: list            # inverse affine of transform_to_building (6 numbers)
    to_raster: Callable      # PageRaster.to_pixels
    origin: tuple            # crop origin in raster pixels
    scale: float             # crop downscale factor

    def to_raster_px(self, p) -> tuple[float, float]:
        return self.to_raster(G.apply_affine(self.to_page, p))

    def to_crop(self, p) -> tuple[float, float]:
        x, y = self.to_raster_px(p)
        return ((x - self.origin[0]) * self.scale, (y - self.origin[1]) * self.scale)


def plan_page(building: dict, level_id: Optional[str], room: Optional[dict]) -> Optional[tuple[dict, dict]]:
    """``(document, page)`` of the source plan for a room of ``level_id`` (see module docstring), or None."""
    cited = set()
    for ev in (room or {}).get("evidence") or []:
        if ev.get("file"):
            cited.add((ev["file"], ev.get("page")))
    best, best_key = None, None
    for doc in building.get("documents") or []:
        for page in doc.get("pages") or []:
            if page.get("level_id") != level_id or not page.get("transform_to_building"):
                continue
            hit = (doc["file"], page.get("page")) in cited or (doc["file"], None) in cited
            key = (0 if hit else 1, CLASS_ORDER.get(page.get("class"), 2), trust_rank(doc),
                   doc["file"], int(page.get("page") or 0))
            if best_key is None or key < best_key:
                best, best_key = (doc, page), key
    return best


def trust_rank(doc: dict) -> int:
    """Rank of a document in the trust order (``TRUST_ORDER``; lower first)."""
    kind = doc.get("source_kind")
    return TRUST_ORDER.get(kind if kind in RASTER_KINDS else doc.get("format"), len(TRUST_ORDER))


def source_file(doc: dict, project_dir: Path, project_out: Path, page: Optional[dict] = None) -> Optional[Path]:
    """The file to rasterise: the rectified image of a raster page (in the project output), the document in the
    project folder, or the converted DXF of a DWG."""
    if page is not None and page.get("rectified_image"):
        rect = Path(project_out) / page["rectified_image"]
        return rect if rect.is_file() else None
    if doc.get("format") == "dwg":
        for cand in (Path(project_out) / "converted" / (Path(doc["file"]).stem + ".dxf"),
                     Path(project_dir) / (Path(doc["file"]).stem + ".dxf")):
            if cand.is_file():
                return cand
        return None
    path = Path(project_dir) / doc["file"]
    return path if path.is_file() else None


def rectified_raster(path: Path):
    """``PageRaster`` of a raster page's rectified image: page units (rectified pixel corners, y up) -> image pixel
    corners ``(x * f, (H - y) * f)``, H the rectified height, f the downscale of ``raster_from_image``."""
    from PIL import Image

    from wenart.ingest import debug_image as DI

    with Image.open(path) as im:
        width, height = im.size
    raster = DI.raster_from_image(path)
    f = raster.image.width / float(width)

    def to_pixels(p):
        return (p[0] * f, (height - p[1]) * f)

    return DI.PageRaster(image=raster.image, to_pixels=to_pixels, note="rectified")


def load_raster(doc: dict, page: dict, path: Path, project_out: Optional[Path] = None):
    """``wenart.ingest.debug_image.PageRaster`` of the page (imported lazily). A raster page (``rectified_image``)
    is drawn on its rectified image under ``project_out`` (``path`` may be that image); FileNotFoundError when it
    is missing (the original file is in other units)."""
    from wenart.ingest import debug_image as DI

    if page.get("rectified_image"):
        if project_out is not None:
            rect = Path(project_out) / page["rectified_image"]
        else:                                     # ``path`` from ``source_file``: the rectified image itself
            rect = Path(path) if Path(path).name == Path(page["rectified_image"]).name else None
        if rect is None or not rect.is_file():
            raise FileNotFoundError(f"rectified image {page['rectified_image']} of a raster page not found")
        return rectified_raster(rect)
    fmt = doc.get("format")
    if fmt == "pdf":
        return DI.raster_from_pdf(path, int(page.get("page") or 1), dpi=PDF_DPI)
    if fmt in ("dxf", "dwg"):
        return DI.raster_from_dxf(path)
    return DI.raster_from_image(path)


def crop_box(raster_size, to_raster_px: Callable, polygon, margin_m: float = MARGIN_M) -> Optional[list[int]]:
    """Pixel box of the room polygon + margin on the raster (clipped), or None when it is off the page."""
    x0, y0, x1, y1 = G.bbox(polygon)
    corners = [(x0 - margin_m, y0 - margin_m), (x1 + margin_m, y0 - margin_m), (x1 + margin_m, y1 + margin_m),
               (x0 - margin_m, y1 + margin_m)]
    px = [to_raster_px(c) for c in corners]
    W, H = raster_size
    bx0 = max(0, int(math.floor(min(p[0] for p in px))))
    by0 = max(0, int(math.floor(min(p[1] for p in px))))
    bx1 = min(W, int(math.ceil(max(p[0] for p in px))))
    by1 = min(H, int(math.ceil(max(p[1] for p in px))))
    if bx1 - bx0 < 2 or by1 - by0 < 2:
        return None
    return [bx0, by0, bx1, by1]


def element_outline(eid: str, building: dict) -> Optional[tuple[list, dict]]:
    """``(polygon in building metres, building element)`` of an element id, or None."""
    for piece in building.get("furniture") or []:
        if piece.get("id") == eid and piece.get("footprint"):
            fp = piece["footprint"]
            return G.rotated_rectangle(fp["center"], fp["size"], fp.get("rotation_deg") or 0.0), piece
    for d in building.get("decor") or []:
        if d.get("id") == eid and d.get("center") and d.get("size"):
            return G.rotated_rectangle(d["center"], d["size"][:2], d.get("rotation_deg") or 0.0), d
    walls = {w["id"]: w for w in building.get("walls") or []}
    for o in building.get("openings") or []:
        if o.get("id") != eid:
            continue
        wall = walls.get(o.get("wall_id"))
        if wall is None:
            return G.rotated_rectangle(o["center"], [o["width"], 0.2], 0.0), o
        from wenart.blender.shell import opening_centre_on_wall
        cx, cy, _ = opening_centre_on_wall(o, wall)
        ang = G.segment_angle_deg(wall["start"], wall["end"])
        return G.rotated_rectangle((cx, cy), [float(o["width"]), float(wall["thickness"])], ang), o
    return None


def _dashed(draw, a, b, fill, width: int, dash: float = 7.0, gap: float = 4.0) -> None:
    length = G.distance(a, b)
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line([G.point_at_distance(a, b, pos), G.point_at_distance(a, b, end)], fill=fill, width=width)
        pos = end + gap


def _font(size: int = 13):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except Exception:  # noqa: BLE001 - very old Pillow
        return ImageFont.load_default()


def save_jpeg(image, path: Path, max_bytes: int = MAX_JPEG_BYTES) -> Path:
    """JPEG at the highest quality (90 down to 40) that fits ``max_bytes``; smaller when it never fits."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = image.convert("RGB")
    while True:
        for q in (90, 80, 70, 60, 50, 40):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=q, optimize=True)
            if buf.tell() <= max_bytes:
                path.write_bytes(buf.getvalue())
                return path
        img = img.resize((max(1, img.width * 3 // 4), max(1, img.height * 3 // 4)))


def render_plan_crop(raster, page: dict, room: dict, camera: Optional[dict], elements: list[dict],
                     building: dict, note: str = "", max_side: int = MAX_SIDE_PX, min_side: int = MIN_SIDE_PX):
    """``(PIL image, PlanMapping)`` of one view's plan crop, or ``(None, reason)``."""
    from PIL import Image, ImageDraw

    to_page = G.invert_affine(page["transform_to_building"])
    polygon = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(polygon) < 3:
        return None, "room has no polygon"
    box = crop_box(raster.image.size, lambda p: raster.to_pixels(G.apply_affine(to_page, p)), polygon)
    if box is None:
        return None, "room is outside the page raster"
    crop = raster.image.crop(tuple(box))
    longest = float(max(crop.size))
    scale = 1.0
    if longest > max_side:
        scale = max_side / longest
    elif longest < min_side:
        scale = min(min_side, max_side) / longest
    if scale != 1.0:
        crop = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), Image.LANCZOS)
    mapping = PlanMapping(to_page=to_page, to_raster=raster.to_pixels, origin=(box[0], box[1]), scale=scale)
    base = crop.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _font()
    pts = [mapping.to_crop(p) for p in polygon]
    draw.polygon(pts, outline=OTHER_COLOUR + (160,), width=1)
    for e in elements:
        found = element_outline(e["wenart_id"], building)
        if found is None:
            continue
        poly, item = found
        px = [mapping.to_crop(p) for p in poly]
        unverified = (item.get("status") == "unverified") or e.get("type_unverified")
        width = 3 if e.get("role") == "required" else 1
        if unverified:
            closed = px + [px[0]]
            for a, b in zip(closed[:-1], closed[1:]):
                _dashed(draw, a, b, UNVERIFIED_COLOUR + (255,), width)
            colour = UNVERIFIED_COLOUR
        else:
            colour = COLOURS.get(e.get("source") or "", OTHER_COLOUR)
            draw.polygon(px, outline=colour + (255,), width=width)
        label = f"{e['wenart_id']} {e.get('type')} {e.get('source') or '-'}"
        draw.text((min(p[0] for p in px) + 2, min(p[1] for p in px) + 1), label, fill=colour + (255,), font=font)
    if camera is not None:
        cam_xy = tuple(camera["position"][:2])
        tgt_xy = tuple(camera["target"][:2])
        c = mapping.to_crop(cam_xy)
        heading = math.atan2(tgt_xy[1] - cam_xy[1], tgt_xy[0] - cam_xy[0])
        half = view_half_angle(camera)
        reach = max(1.0, G.distance(G.bbox(polygon)[:2], G.bbox(polygon)[2:]))
        rays = [(cam_xy[0] + reach * math.cos(heading + s * half), cam_xy[1] + reach * math.sin(heading + s * half))
                for s in (-1.0, 1.0)]
        for r in rays:
            draw.line([c, mapping.to_crop(r)], fill=CAMERA_COLOUR + (220,), width=2)
        draw.line([c, mapping.to_crop((cam_xy[0] + 0.6 * math.cos(heading), cam_xy[1] + 0.6 * math.sin(heading)))],
                  fill=CAMERA_COLOUR + (255,), width=3)
        draw.ellipse([c[0] - 6, c[1] - 6, c[0] + 6, c[1] + 6], fill=CAMERA_COLOUR + (255,))
        draw.text((c[0] + 8, c[1] - 6), camera.get("name", ""), fill=CAMERA_COLOUR + (255,), font=font)
    if note:
        draw.rectangle([0, 0, base.width, 18], fill=(255, 255, 255, 210))
        draw.text((4, 3), note, fill=(0, 0, 0, 255), font=font)
    return Image.alpha_composite(base, overlay).convert("RGB"), mapping


def view_half_angle(camera: dict) -> float:
    """Half the horizontal field of view (radians) of the camera's own lens (``expected.focal_px``'s lens and
    sensor; a camera dict without them predates Milestone 8: 24 mm on 36 mm)."""
    from wenart.vision_check.expected import DEFAULT_LENS_MM, DEFAULT_SENSOR_MM

    sensor = float(camera.get("sensor_mm") or DEFAULT_SENSOR_MM)
    lens = float(camera.get("lens_mm") or DEFAULT_LENS_MM)
    return math.atan((sensor / 2.0) / lens)


def write_plan_crops(project, cameras=None, log=print) -> dict:
    """``check/<cam>_plan.jpg`` for every view; returns ``check/plan_crops.json`` content (also written)."""
    from wenart.vision_check.project import rel, write_json

    out = {"schema_version": "0.1", "project": project.project, "views": {}, "warnings": []}
    rasters: dict = {}
    for cam in (cameras or list(project.views())):
        exp = project.expected(cam)
        room = project.room(exp.get("room_id"))
        found = plan_page(project.building, exp.get("level_id"), room)
        if found is None:
            out["views"][cam] = {"plan": None, "reason": f"no page with a transform for level {exp.get('level_id')}"}
            continue
        doc, page = found
        key = (doc["file"], page.get("page"))
        if key not in rasters:
            path = source_file(doc, project.project_dir, project.out, page)
            if path is None:
                what = f"rectified image {page['rectified_image']}" if page.get("rectified_image") else "source file"
                rasters[key] = (None, f"{what} of {doc['file']} not found")
            else:
                try:
                    rasters[key] = (load_raster(doc, page, path, project.out), None)
                except Exception as exc:  # noqa: BLE001 - a missing rasteriser must not stop the check
                    rasters[key] = (None, f"{doc['file']}: raster failed ({type(exc).__name__}: {exc})")
        raster, why = rasters[key]
        if raster is None:
            out["views"][cam] = {"plan": None, "reason": why}
            continue
        camera = next((c for c in project.scene.get("cameras") or [] if c.get("name") == cam), None)
        elements = list(exp.get("elements") or [])
        note = f"{doc['file']} p{page.get('page')} | {cam} | green documents, orange ai, dashed red unverified"
        image, mapping = render_plan_crop(raster, page, room, camera, elements, project.building, note)
        if image is None:
            out["views"][cam] = {"plan": None, "reason": mapping}
            continue
        path = save_jpeg(image, project.plan_path(cam))
        out["views"][cam] = {"plan": rel(path, project.check_dir), "document": doc["file"], "page": page.get("page"),
                             "format": doc.get("format"), "source_kind": doc.get("source_kind"),
                             "drawn_on": page.get("rectified_image") or doc["file"],
                             "crop_origin_px": list(mapping.origin),
                             "scale": round(mapping.scale, 5), "bytes": path.stat().st_size}
    for cam, info in out["views"].items():
        if info.get("plan") is None:
            msg = f"{cam}: no plan crop ({info.get('reason')})"
            out["warnings"].append(msg)
            log(f"plan-crops: {msg}")
    write_json(project.check_dir / "plan_crops.json", out)
    return out
