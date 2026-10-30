"""UL169 (30 Oct 2026): "On the top down views do not use these tags, I am not able to see what is behind". The
top-down views keep the rooms visible: a small see-through numbered badge per room and the names in a legend under the
view, never an opaque name box over the furniture."""
import json

from PIL import Image

from wenart.report import topdown_labels as TL


def test_rooms_get_small_see_through_badges_and_a_legend(tmp_path):
    w, h = 800, 600
    colour = (120, 160, 90)
    png = tmp_path / "top_L0.png"
    Image.new("RGB", (w, h), colour).save(png)
    (tmp_path / "top_L0.png.frame.json").write_text(json.dumps({"x0": 0, "x1": 10, "y0": 0, "y1": 7.5,
                                                                "elevation": 0.0}))
    building = {"levels": [{"id": "L0", "elevation": 0.0}], "walls": [], "openings": [],
                "rooms": [{"id": "r_L0_salon", "level_id": "L0", "name": "salon", "room_type": "living",
                           "polygon": [(0, 0), (5, 0), (5, 7.5), (0, 7.5)]},
                          {"id": "r_L0_mutfak", "level_id": "L0", "name": "mutfak", "room_type": "kitchen",
                           "polygon": [(5, 0), (10, 0), (10, 7.5), (5, 7.5)]}]}
    out = TL.label(building, "L0", png, tmp_path / "top_L0_plan.jpg")
    im = Image.open(out).convert("RGB")
    assert im.size[0] == w and im.size[1] > h                      # the legend strip under the view
    # around each room's middle the render shows through: only the small badge covers it
    for cx in (2.5, 7.5):
        x, y = int(cx / 10 * w), int((7.5 - 3.75) / 7.5 * h)
        rad = max(7, w // 110)
        ring = [im.getpixel((x + dx, y)) for dx in (-6 * rad, -2 * rad, 2 * rad, 6 * rad)]
        assert all(abs(p[0] - colour[0]) < 25 and abs(p[1] - colour[1]) < 25 for p in ring), ring
    assert TL.room_marks(building, "L0")[0][0] == "mutfak"         # numbered in id order
