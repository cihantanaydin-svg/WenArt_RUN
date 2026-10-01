"""CPU tests for the tiled symbol pass (docs/milestone3.md, section 5).

No model here: ``drawing_extent`` is checked on the three synthetic raster
pages against the truth boxes of ``truth/pages.json``, ``tiles`` on hand-made
boxes, and the tile merge / bake-off stage with a fake client that answers
known boxes in crop pixels.
"""
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart.recognition import bakeoff, tiles, vlm_client

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
RASTER_PAGES = [("synthetic-01", "1_kat_scan.png"), ("synthetic-02", "plan_scan.png"), ("synthetic-02", "plan_photo.jpg")]
SYMBOL_MARGIN_PX = 16  # every truth symbol box must sit at least this far inside the extent


def truth_page(project: str, file: str) -> dict:
    pages = json.loads((PROJECTS / project / "truth" / "pages.json").read_text(encoding="utf-8"))["pages"]
    return next(p for p in pages if p["file"] == file)


# --------------------------------------------------------------------------
# Drawing extent
# --------------------------------------------------------------------------

@pytest.mark.parametrize("project,file", RASTER_PAGES)
def test_drawing_extent_contains_every_truth_symbol_with_margin(project, file):
    page = truth_page(project, file)
    width, height = page["size"]
    extent = tiles.drawing_extent(PROJECTS / project / file)
    assert all(isinstance(v, int) for v in extent)
    assert 0 <= extent[0] < extent[2] <= width and 0 <= extent[1] < extent[3] <= height
    # The drawing is a quarter of the sheet at most: the crop must really cut something away.
    area_share = (extent[2] - extent[0]) * (extent[3] - extent[1]) / (width * height)
    assert area_share < 0.3, f"extent {extent} covers {area_share:.0%} of the page"
    for sym in page["symbols"]:
        assert tiles.box_contains(extent, sym["box"], SYMBOL_MARGIN_PX), f"{sym['id']} {sym['box']} outside {extent}"
    # Walls and dimension texts belong to the drawing too.
    for wall in page["walls"]:
        assert tiles.box_contains(extent, wall["box"], 0), f"{wall['id']} outside {extent}"
    for text in page["texts"]:
        if text["role"] == "dimension":
            assert tiles.box_contains(extent, text["box"], 0), f"dimension {text['text']} outside {extent}"


def test_drawing_extent_ignores_the_page_frame_and_handles_blank_pages():
    # A sheet with a frame along the edges and one small drawing: the frame has more ink
    # than the drawing, but it is not the drawing.
    img = np.full((800, 1200), 255, np.uint8)
    img[20:24, 20:1180] = 0
    img[776:780, 20:1180] = 0
    img[20:780, 20:24] = 0
    img[20:780, 1176:1180] = 0
    img[300:304, 500:700] = 0          # a small "room": four thin walls
    img[500:504, 500:700] = 0
    img[300:504, 500:504] = 0
    img[300:504, 696:700] = 0
    extent = tiles.drawing_extent(img)
    assert tiles.box_contains(extent, [500, 300, 700, 504], tiles.MIN_MARGIN_PX)
    assert extent[0] > 100 and extent[1] > 100 and extent[2] < 1100 and extent[3] < 700
    # Blank page: the whole page, so the caller still gets one tile.
    assert tiles.drawing_extent(np.full((300, 400), 255, np.uint8)) == [0, 0, 400, 300]


def test_drawing_extent_accepts_pil_and_scales_large_pages_back():
    page = truth_page("synthetic-02", "plan_scan.png")
    with Image.open(PROJECTS / "synthetic-02" / "plan_scan.png") as img:
        from_path = tiles.drawing_extent(PROJECTS / "synthetic-02" / "plan_scan.png")
        from_pil = tiles.drawing_extent(img.convert("RGB"))
        assert from_pil == from_path
        # Twice the size: analysed downscaled, the box must come back in the big page's pixels.
        big = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    extent = tiles.drawing_extent(big)
    assert extent[2] <= big.width and extent[3] <= big.height
    for sym in page["symbols"]:
        doubled = [2 * v for v in sym["box"]]
        assert tiles.box_contains(extent, doubled, SYMBOL_MARGIN_PX)


# --------------------------------------------------------------------------
# Tiles
# --------------------------------------------------------------------------

def _assert_cover(box, tile_list, tile_px, overlap):
    x0, y0, x1, y1 = (int(v) for v in box)
    covered = np.zeros((y1 - y0, x1 - x0), dtype=bool)
    for t in tile_list:
        assert t[0] >= x0 and t[1] >= y0 and t[2] <= x1 and t[3] <= y1, f"tile {t} outside {box}"
        assert t[2] - t[0] <= tile_px and t[3] - t[1] <= tile_px
        covered[t[1] - y0:t[3] - y0, t[0] - x0:t[2] - x0] = True
    assert covered.all(), "tiles do not cover the box"
    # Neighbouring tiles in a row overlap by at least the asked share.
    rows = {}
    for t in tile_list:
        rows.setdefault(t[1], []).append(t)
    for row in rows.values():
        row.sort()
        for a, b in zip(row, row[1:]):
            assert a[2] - b[0] >= int(overlap * tile_px) - 1


def test_tiles_cover_the_box_with_overlap_and_end_at_the_edge():
    box = [100, 50, 3100, 2050]
    out = tiles.tiles(box, tile_px=1024, overlap=0.2)
    assert len(out) == 12 and out[0] == [100, 50, 1124, 1074] and out[-1] == [2076, 1026, 3100, 2050]
    _assert_cover(box, out, 1024, 0.2)
    # A box smaller than a tile gives exactly one tile of the box's size.
    assert tiles.tiles([880, 633, 1599, 1200]) == [[880, 633, 1599, 1200]]
    # Narrow and tall: one column.
    out = tiles.tiles([0, 0, 500, 2000], tile_px=1024, overlap=0.2)
    assert all(t[0] == 0 and t[2] == 500 for t in out) and len(out) == 3
    _assert_cover([0, 0, 500, 2000], out, 1024, 0.2)
    # Fractional input boxes are rounded outwards.
    assert tiles.tiles([10.4, 10.6, 20.2, 30.9], tile_px=100) == [[10, 10, 21, 31]]
    with pytest.raises(ValueError):
        tiles.tiles(box, overlap=1.0)


@pytest.mark.parametrize("project,file", RASTER_PAGES)
def test_tiles_of_the_synthetic_extents(project, file):
    extent = tiles.drawing_extent(PROJECTS / project / file)
    one = tiles.tiles(extent)                     # 1024 px tiles: the drawing fits in one
    assert one == [extent]
    many = tiles.tiles(extent, tile_px=512, overlap=0.3)
    assert len(many) >= 2
    _assert_cover(extent, many, 512, 0.3)


# --------------------------------------------------------------------------
# Merge across tiles
# --------------------------------------------------------------------------

def test_merge_tile_items_keeps_higher_confidence_and_counts_conflicts():
    sofa_a = {"type": "sofa", "box": [100, 100, 220, 160], "confidence": 0.6, "rotation_deg": 0, "tile": 0}
    sofa_b = {"type": "sofa", "box": [102, 101, 221, 161], "confidence": 0.9, "rotation_deg": 90, "tile": 1}
    chair = {"type": "chair", "box": [400, 400, 430, 430], "confidence": 0.7, "rotation_deg": None, "tile": 1}
    table_over_sofa = {"type": "table_coffee", "box": [101, 100, 220, 160], "confidence": 0.5, "rotation_deg": None, "tile": 2}
    far_sofa = {"type": "sofa", "box": [100, 300, 220, 360], "confidence": 0.4, "rotation_deg": 0, "tile": 2}
    merged, stats = tiles.merge_tile_items([sofa_a, sofa_b, chair, table_over_sofa, far_sofa])
    assert stats == {"n_input": 5, "n_merged": 4, "n_duplicates": 1, "type_conflicts": 1}
    by_type = {}
    for item in merged:
        by_type.setdefault(item["type"], []).append(item)
    assert len(by_type["sofa"]) == 2
    kept = next(s for s in by_type["sofa"] if s["box"][0] == 102)
    assert kept["confidence"] == 0.9 and kept["rotation_deg"] == 90 and kept["tiles"] == [0, 1]
    assert "tile" not in kept
    assert by_type["chair"][0]["tiles"] == [1] and by_type["table_coffee"][0]["tiles"] == [2]
    assert tiles.merge_tile_items([]) == ([], {"n_input": 0, "n_merged": 0, "n_duplicates": 0, "type_conflicts": 0})


def test_offset_box_maps_crop_pixels_to_page_pixels():
    assert tiles.offset_box([10.0, 20.0, 30.0, 40.0], 1000, 500) == [1010.0, 520.0, 1030.0, 540.0]


# --------------------------------------------------------------------------
# Tiled stage with a fake client
# --------------------------------------------------------------------------

class _TileFakeClient:
    """Answers the ``symbols`` task on a crop with the truth boxes that lie fully inside it.

    The crops arrive in the order of ``tiles.tiles(extent, ...)``; the fake
    receives the same tile list and answers the n-th call for the n-th tile,
    in CROP pixels (what the real client returns for the image it was given).
    """
    model = "fake/Tiler"

    def __init__(self, truth_symbols: list[dict], tile_list: list[list[int]], fail_tiles=()):
        self.truth = truth_symbols
        self.tiles = tile_list
        self.fail_tiles = set(fail_tiles)
        self.calls = 0
        self.crop_sizes = []

    def run_task(self, task, image):
        assert task == "symbols" and isinstance(image, Image.Image)
        index = self.calls
        self.calls += 1
        tile = self.tiles[index]
        assert image.size == (tile[2] - tile[0], tile[3] - tile[1]), "the crop is not the tile"
        self.crop_sizes.append(image.size)
        if index in self.fail_tiles:
            return vlm_client.VLMResult(task=task, model=self.model, data=None, raw_text="", latency_s=0.01,
                                        attempts=3, error="cannot reach server", image_size=image.size, page_size=image.size)
        items = []
        for sym in self.truth:
            if tiles.box_contains(tile, sym["box"], 0):
                b = sym["box"]
                items.append({"type": sym["type"], "box": [b[0] - tile[0], b[1] - tile[1], b[2] - tile[0], b[3] - tile[1]],
                              "rotation_deg": None, "confidence": 0.8})
        data = {"items": items}
        return vlm_client.VLMResult(task=task, model=self.model, data=data, raw_text=json.dumps(data), latency_s=0.01,
                                    attempts=1, image_size=image.size, page_size=image.size)


def test_run_symbols_tiled_merges_duplicates_and_scores_against_truth(tmp_path):
    page = bakeoff.raster_pages(PROJECTS)[1]            # synthetic-02 plan_scan.png
    extent = tiles.drawing_extent(page.image_path)
    tile_list = tiles.tiles(extent, tile_px=512, overlap=0.3)
    assert len(tile_list) == 4
    client = _TileFakeClient(page.truth_symbols(), tile_list)
    rec = bakeoff.run_symbols_tiled(page, client.model, client, tmp_path, tile_px=512, overlap=0.3)
    assert client.calls == 4 and rec["tiled"] is True and not rec["has_errors"]
    assert rec["extent"] == extent and [t["box"] for t in rec["tiles"]] == tile_list
    merge = rec["symbols"]["merge"]
    truth = page.truth_symbols()
    # Every truth symbol is fully inside at least one tile (the overlap is wider than any symbol),
    # symbols in the overlap zone were seen twice and merged into one.
    assert merge["n_duplicates"] >= 1 and merge["n_input"] > len(truth)
    assert merge["n_merged"] == len(truth) and merge["type_conflicts"] == 0
    scores = rec["scores"]["symbols"]["overall"]
    assert scores["tp"] == len(truth) and scores["fp"] == 0 and scores["fn"] == 0
    # Merged boxes are back in page pixels and remember the tiles that saw them.
    for item in rec["symbols"]["items"]:
        assert tiles.box_contains(extent, item["box"], 0) and item["tiles"]
    assert any(len(item["tiles"]) == 2 for item in rec["symbols"]["items"])
    out_json = tmp_path / "synthetic-02_plan_scan_Tiler_tiled.json"
    out_jpg = tmp_path / "synthetic-02_plan_scan_Tiler_tiled.jpg"
    assert out_json.is_file() and out_jpg.is_file() and out_jpg.stat().st_size <= bakeoff.DEBUG_MAX_BYTES
    # Resumable: no new calls on the second run.
    again = bakeoff.run_symbols_tiled(page, client.model, client, tmp_path, tile_px=512, overlap=0.3)
    assert client.calls == 4 and again["scores"]["symbols"]["overall"]["tp"] == len(truth)


def test_run_symbols_tiled_records_failed_tiles_instead_of_dropping_them(tmp_path):
    page = bakeoff.raster_pages(PROJECTS)[0]            # synthetic-01 1_kat_scan.png
    extent = tiles.drawing_extent(page.image_path)
    tile_list = tiles.tiles(extent, tile_px=512, overlap=0.3)
    client = _TileFakeClient(page.truth_symbols(), tile_list, fail_tiles={0})
    rec = bakeoff.run_symbols_tiled(page, client.model, client, tmp_path, tile_px=512, overlap=0.3)
    assert rec["has_errors"] and rec["scores"]["errors"] == {"tile_0": "cannot reach server"}
    assert rec["tiles"][0]["error"] == "cannot reach server" and rec["tiles"][0]["n_items"] == 0
    assert rec["tiles"][1]["error"] is None
    # With --retry-errors the page is re-run.
    client.calls = 0
    bakeoff.run_symbols_tiled(page, client.model, client, tmp_path, tile_px=512, overlap=0.3, retry_errors=False)
    assert client.calls == 0
    bakeoff.run_symbols_tiled(page, client.model, client, tmp_path, tile_px=512, overlap=0.3, retry_errors=True)
    assert client.calls == len(tile_list)


def test_tiled_results_reach_the_summary_as_their_own_column(tmp_path):
    pages = bakeoff.raster_pages(PROJECTS)
    page = pages[2]                                     # synthetic-02 plan_photo.jpg
    extent = tiles.drawing_extent(page.image_path)
    client = _TileFakeClient(page.truth_symbols(), tiles.tiles(extent))
    bakeoff.run_symbols_tiled(page, client.model, client, tmp_path)
    assert client.calls == 1 and client.crop_sizes[0] == (extent[2] - extent[0], extent[3] - extent[1])
    results = bakeoff.collect_page_results(pages, tmp_path)
    entry = next(r for r in results if r["file"] == "plan_photo.jpg")
    assert entry["models"] == {} and set(entry["tiled"]) == {client.model}
    assert entry["tiled"][client.model]["n_tiles"] == 1
    agg = bakeoff.write_summary(pages, tmp_path)
    m = agg["models"][client.model]
    assert m["pages"] == 0 and m["tiled_pages"] == 1 and m["symbols_tiled"]["recall"] == 1.0
    md = (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "Symbols (tiled) R / P" in md and "100 % / 100 % (1 p," in md and "(1 tiles)" in md
