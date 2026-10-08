"""Writes docs/examples/building_m10.example.json and docs/examples/sheets.example.json (the M10 contract fixtures,
docs/milestone10.md §1). Run from the repo root: PYTHONPATH=. python docs/examples/make_m10_examples.py"""
import argparse, json, math
from pathlib import Path
from wenart import building as B

_ap = argparse.ArgumentParser()
_ap.add_argument("--out-dir", default="docs/examples")
OUT_DIR = Path(_ap.parse_args().out_dir)
# The pieces below are written with the outer wall centre lines on (0, 0)-(10, 8); the building frame puts its origin
# at the min corner of the reference plan's outer outline (outer wall faces, docs/milestone10.md §3.1 item 5), so every
# x, y is shifted by half the outer wall thickness at the end (``shift_xy``).
SHIFT = 0.125

FILE = "ornek_bina.dxf"
def ev(entity, method="vector", conf=1.0, layer=None, text=None, region=None, **kw):
    e = {"file": FILE, "page": 1, "layer": layer, "entity": entity, "method": method, "confidence": conf}
    if text is not None: e["text"] = text
    if region is not None: e["region_id"] = region
    e.update(kw)
    return e
def val(v, method="vector", conf=1.0, evidence=None, note=None):
    d = {"value": v, "method": method, "confidence": conf, "evidence": evidence or []}
    if note: d["note"] = note
    return d

OUT, IN = 0.25, 0.10
LEFT  = [[0.125, 0.125], [5.95, 0.125], [5.95, 7.875], [0.125, 7.875]]
LR    = [[6.05, 0.125], [9.875, 0.125], [9.875, 3.95], [6.05, 3.95]]
UR    = [[6.05, 4.05], [9.875, 4.05], [9.875, 7.875], [6.05, 7.875]]
MERGED = [[0.125, 0.125], [9.875, 0.125], [9.875, 3.95], [5.95, 3.95], [5.95, 7.875], [0.125, 7.875]]
def area(poly):
    a = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]): a += x0 * y1 - x1 * y0
    return round(abs(a) / 2, 2)

REGION = {"L-1": "r2", "L-1b": "r3", "L0": "r4", "L1": "r5"}
levels = [
    {"id": "L-1", "label": "Bodrum Kat", "order": -1, "elevation": -3.0, "ceiling_height": 2.8, "ceiling_height_source": "section",
     "label_source": "title", "kind": "basement", "variant_group": "vg_L-1", "variant": "base", "variant_slug": "base", "base_level_id": None,
     "region_id": "r2", "elevation_source": "section", "floor_to_floor": val(3.0, evidence=[ev("LINE:7A1", region="r6", rule="slab_bands")]),
     "evidence": [ev("MTEXT:5A0", text="BODRUM KAT PLANI", region="r2")]},
    {"id": "L-1b", "label": "Bodrum Kat", "order": -1, "elevation": -3.0, "ceiling_height": 2.8, "ceiling_height_source": "section",
     "label_source": "title", "kind": "basement", "variant_group": "vg_L-1", "variant": "Açık mutfak", "variant_slug": "acik-mutfak", "base_level_id": "L-1",
     "region_id": "r3", "elevation_source": "section", "floor_to_floor": val(3.0, evidence=[ev("LINE:7A1", region="r6", rule="slab_bands")]),
     "evidence": [ev("MTEXT:5A1", text="BODRUM KAT PLANI (AÇIK MUTFAK)", region="r3")]},
    {"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.8, "ceiling_height_source": "section",
     "label_source": "title", "kind": "floor", "variant_group": None, "variant": "base", "variant_slug": "base", "base_level_id": None,
     "region_id": "r4", "elevation_source": "section", "floor_to_floor": val(3.0, evidence=[ev("LINE:7A2", region="r6", rule="slab_bands")]),
     "evidence": [ev("MTEXT:5A2", text="ZEMİN KAT PLANI", region="r4")]},
    {"id": "L1", "label": "Çatı Katı", "order": 1, "elevation": 3.0, "ceiling_height": 2.4, "ceiling_height_source": "section",
     "label_source": "title", "kind": "attic", "variant_group": None, "variant": "base", "variant_slug": "base", "base_level_id": None,
     "region_id": "r5", "elevation_source": "section", "floor_to_floor": None,
     "evidence": [ev("MTEXT:5A3", text="ÇATI KAT PLANI", region="r5")]},
]
walls, openings, rooms, furniture = [], [], [], []
def wall(lv, n, a, b, t, ext, height=None):
    walls.append({"id": f"w_{lv}_{n:03d}", "level_id": lv, "start": a, "end": b, "thickness": t, "height": height, "exterior": ext,
                  "status": "verified", "evidence": [ev(f"LWPOLYLINE:{lv}{n}", layer="DUVAR", region=REGION[lv])]})
for lv in REGION:
    wall(lv, 1, [0.0, 0.0], [10.0, 0.0], OUT, True)
    wall(lv, 2, [10.0, 0.0], [10.0, 8.0], OUT, True)
    wall(lv, 3, [10.0, 8.0], [0.0, 8.0], OUT, True)
    wall(lv, 4, [0.0, 8.0], [0.0, 0.0], OUT, True)
    wall(lv, 5, [6.0, 4.0] if lv == "L-1b" else [6.0, 0.0], [6.0, 8.0], IN, False)
    wall(lv, 6, [6.0, 4.0], [10.0, 4.0], IN, False)

def opening(lv, kind, n, wall_n, c, w, h=None, sill=None, assumed=None, swing=None, operation=None, op_source=None):
    pre = {"door": "d", "window": "win", "opening": "op"}[kind]
    o = {"id": f"{pre}_{lv}_{n:03d}", "type": kind, "level_id": lv, "wall_id": f"w_{lv}_{wall_n:03d}", "center": c, "width": w,
         "height": h, "sill_height": sill, "assumed": assumed or [], "swing_side": swing,
         "operation": operation if operation else ("swing" if kind == "door" else None),
         "operation_source": op_source if op_source else ("geometry" if kind == "door" else None), "status": "verified",
         "evidence": [ev(f"INSERT:{pre}{lv}{n}", layer="KAPI" if kind == "door" else "PENCERE", block="KAPI_90" if kind == "door" else "PENCERE", region=REGION[lv])]}
    openings.append(o)

def room(lv, label, label_raw, rtype, poly, furnished, **extra):
    rid = B.room_id(lv, label)
    r = {"id": rid, "level_id": lv, "label": label, "label_raw": label_raw, "room_type": rtype, "polygon": poly,
         "area_computed": area(poly), "area_label": None, "has_documented_furniture": furnished, "room_subtype": None,
         "twin_of": None, "same_as": None, "style_override": None, "status": "verified",
         "evidence": [ev(f"TEXT:{lv}{label[:3]}", layer="YAZI", text=label_raw, region=REGION[lv]),
                      {"file": FILE, "page": 1, "entity": f"derived-from:{lv}", "method": "derived", "confidence": 0.98, "region_id": REGION[lv]}]}
    r.update(extra)
    rooms.append(r)
    return rid

# L-1 base basement
salon = room("L-1", "Salon", "SALON", "living", LEFT, True)
mutfak = room("L-1", "Mutfak", "MUTFAK", "kitchen", LR, True)
hol_b = room("L-1", "Hol", "HOL", "hall", UR, True)
opening("L-1", "door", 1, 1, [2.0, 0.0], 1.0, 2.1, 0.0, swing=salon)
opening("L-1", "window", 1, 1, [4.5, 0.0], 2.0, 1.2, 0.9)
opening("L-1", "window", 2, 1, [8.0, 0.0], 1.2, 1.2, 0.9)
opening("L-1", "door", 2, 5, [6.0, 6.0], 0.9, 2.1, 0.0, swing=None, operation="sliding", op_source="block_name")
opening("L-1", "door", 3, 6, [7.0, 4.0], 0.8, 2.1, 0.0, swing=mutfak)
# L-1b alternative: open kitchen
open_k = room("L-1b", "Salon + Açık Mutfak", "SALON + AÇIK MUTFAK", "living", MERGED, True)
hol_alt = room("L-1b", "Hol", "HOL", "hall", UR, True, same_as=hol_b)
opening("L-1b", "door", 1, 1, [2.0, 0.0], 1.0, 2.1, 0.0, swing=open_k)
opening("L-1b", "window", 1, 1, [4.5, 0.0], 2.0, 1.2, 0.9)
opening("L-1b", "window", 2, 1, [8.0, 0.0], 1.2, 1.2, 0.9)
opening("L-1b", "door", 2, 5, [6.0, 6.0], 0.9, 2.1, 0.0, swing=open_k)
opening("L-1b", "door", 3, 6, [7.0, 4.0], 0.8, 2.1, 0.0, swing=open_k)
# L0 ground floor
yatak = room("L0", "Yatak Odası", "YATAK ODASI", "bedroom", LEFT, True)
banyo = room("L0", "Banyo", "BANYO", "bathroom", LR, True)
hol0 = room("L0", "Hol", "HOL", "hall", UR, True)
opening("L0", "door", 1, 3, [7.0, 8.0], 1.0, 2.1, 0.0, swing=hol0)
opening("L0", "window", 1, 1, [3.0, 0.0], 1.6, 1.4, 0.9)
opening("L0", "window", 2, 4, [0.0, 4.0], 1.2, 1.2, 0.9)
opening("L0", "window", 3, 1, [8.0, 0.0], 0.6, 0.6, 1.5)
opening("L0", "door", 2, 5, [6.0, 6.0], 0.9, 2.1, 0.0, swing=yatak)
opening("L0", "door", 3, 6, [7.0, 4.0], 0.8, 2.1, 0.0, swing=banyo)
# L1 attic
oyun = room("L1", "Oyun Odası", "OYUN ODASI", "other", LEFT, False)
teras = room("L1", "Teras", "TERAS", "balcony", LR, False)
hol1 = room("L1", "Hol", "HOL", "hall", UR, False)
opening("L1", "door", 1, 5, [6.0, 6.0], 0.9, 2.1, 0.0, swing=oyun)
opening("L1", "door", 2, 6, [8.0, 4.0], 0.9, 2.1, 0.0, swing=teras)
opening("L1", "window", 1, 4, [0.0, 4.0], 1.2, 1.0, 0.6)

def piece(pid, lv, rid, ftype, c, size, rot, front, src="from_documents", h=None, **extra):
    p = {"id": pid, "level_id": lv, "room_id": rid, "type": ftype, "type_raw": None, "type_method": "block_name" if src == "from_documents" else None,
         "source": src, "footprint": {"center": c, "size": size, "rotation_deg": rot}, "front_deg": front, "height": h,
         "asset": None, "status": "verified",
         "evidence": [ev(f"INSERT:{pid}", layer="MOBILYA", region=REGION[lv])] if src == "from_documents" else []}
    if p["type_method"] is None: del p["type_method"]
    p.update(extra)
    furniture.append(p)

# Stairs (fixed equipment): L-1 -> L0 and L0 -> L1, in the hall against the east wall
STAIR = {"flights": [{"start": [9.35, 4.5], "end": [9.35, 7.5], "width": 1.0, "lines": 16, "spacing": 0.2}],
         "landing": None, "direction": [0.0, 1.0], "direction_assumed": False, "turn": "straight", "turn_assumed": False,
         "void_assumed": True, "riser_m": 0.1875, "riser_source": "derived: floor to floor 3.00 m / 16 risers"}
for lv, n in (("L-1", 1), ("L0", 1)):
    piece(f"f_{lv}_{n:03d}", lv, hol_b if lv == "L-1" else hol0, "stair", [9.35, 6.0], [1.0, 3.0], 0.0, None, h=3.0,
          stair=json.loads(json.dumps(STAIR)))
piece("f_L-1b_001", "L-1b", hol_alt, "stair", [9.35, 6.0], [1.0, 3.0], 0.0, None, h=3.0, stair=json.loads(json.dumps(STAIR)))
# L-1 Salon: a drawn 3-seat sofa against the north wall, changed by AI into a corner sofa (Feature 1)
piece("f_L-1_002", "L-1", salon, "sofa_corner", [3.0, 7.05], [2.6, 1.6], 0.0, 270.0, h=0.85,
      shape="L", chaise_side="right", chaise_depth=1.6, seat_depth=0.9, chaise_width=0.9,
      modified_by_ai=True, drawn_type="sofa", drawn_footprint={"center": [3.0, 7.4], "size": [2.2, 0.9], "rotation_deg": 0.0},
      drawn_height=None, anchor={"kind": "back_edge", "point": [3.0, 7.85], "wall_id": "w_L-1_003"},
      design={"fabric_colour": "light grey", "style_family": "modern", "material_tags": ["fabric"]})
furniture[-1]["evidence"] += [ev("completion", method="ai", conf=0.9, model="Qwen/Qwen3-VL-8B-Instruct", pass_=1),
                              ev("completion", method="ai", conf=0.9, model="Qwen/Qwen3-VL-8B-Instruct", pass_=2)]
for e in furniture[-1]["evidence"]:
    if "pass_" in e:
        e["pass"] = e.pop("pass_"); e["text"] = "a corner sofa fills the long wall and keeps the garden door free"; e["file"] = "building.json"; e["entity"] = None; e["layer"] = None
# L-1 Salon: coffee table added by AI (completes the room)
piece("f_L-1_003", "L-1", salon, "table_coffee", [2.6, 5.6], [1.0, 0.6], 0.0, None, src="added_by_ai", h=0.45,
      completes_room=True, method="ai", design={"material_tags": ["glass"]})
furniture[-1]["evidence"] = [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": 1, "confidence": 0.9,
                              "text": "coffee table in front of the corner sofa"}]
furniture[-1]["checks"] = {k: True for k in ("inside_room", "no_overlap", "clearance_ok", "doors_free", "windows_free", "wall_contact")}
# L-1 Mutfak: drawn counter run (fixed equipment) with its look, wall cabinets by rule
piece("f_L-1_004", "L-1", mutfak, "kitchen_counter", [9.555, 2.0], [3.0, 0.6], 270.0, 180.0, h=0.9,
      counter_run={"wall_id": "w_L-1_002", "strokes": ["LINE:C1", "LINE:C2"]},
      design={"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "stone"})
piece("f_L-1_005", "L-1", mutfak, "wall_cabinet", [9.7, 2.0], [3.0, 0.35], 270.0, 180.0, src="added_by_ai", h=0.7,
      completes_room=True, method="rule", mount_bottom_m=1.45,
      rule={"run": "f_L-1_004", "z": [1.45, 2.15], "excluded": []},
      design={"front_style": "shaker", "colour": "sage", "handle": "brass"})
furniture[-1]["evidence"] = [{"file": "building.json", "method": "derived", "confidence": 1.0,
                              "text": "wall cabinets along the counter run f_L-1_004 (rule, docs/milestone10.md §4.4), 1.45-2.15 m"}]
# L-1b open kitchen: island added? no: the counter run as drawn on the alternative plan
piece("f_L-1b_002", "L-1b", open_k, "kitchen_counter", [9.555, 2.0], [3.0, 0.6], 270.0, 180.0, h=0.9,
      counter_run={"wall_id": "w_L-1b_002", "strokes": ["LINE:C5", "LINE:C6"]})
# L0 bedroom: drawn double bed; nightstands and wardrobe added by AI
piece("f_L0_002", "L0", yatak, "bed_double", [3.0, 6.85], [1.6, 2.0], 0.0, 270.0, h=0.5,
      anchor={"kind": "back_edge", "point": [3.0, 7.85], "wall_id": "w_L0_003"})
piece("f_L0_003", "L0", yatak, "nightstand", [1.9, 7.65], [0.5, 0.4], 0.0, 270.0, src="added_by_ai", h=0.5, completes_room=True, method="ai")
piece("f_L0_004", "L0", yatak, "nightstand", [4.1, 7.65], [0.5, 0.4], 0.0, 270.0, src="added_by_ai", h=0.5, completes_room=True, method="ai")
piece("f_L0_005", "L0", yatak, "wardrobe", [0.446, 2.5], [1.8, 0.6], 90.0, 0.0, src="added_by_ai", h=2.1, completes_room=True, method="ai")
for p in furniture[-3:]:
    p["evidence"] = [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": k, "confidence": 0.9,
                      "text": "missing expected type of a bedroom"} for k in (1, 2)]
    p["checks"] = {k: True for k in ("inside_room", "no_overlap", "clearance_ok", "doors_free", "windows_free", "wall_contact")}
# L0 bathroom: fixed sanitary ware, the washbasin with the vanity look
piece("f_L0_006", "L0", banyo, "toilet", [9.504, 2.5], [0.4, 0.7], 270.0, 180.0, h=0.8)
piece("f_L0_007", "L0", banyo, "washbasin", [9.6, 1.2], [0.6, 0.5], 270.0, 180.0, h=0.85,
      design={"vanity": True, "front_style": "slatted", "colour": "walnut brown", "handle": None})
piece("f_L0_008", "L0", banyo, "shower", [6.6, 0.7], [0.9, 0.9], 0.0, None, h=2.0)
piece("f_L0_009", "L0", hol0, "console_table", [8.2, 7.68], [0.9, 0.35], 0.0, 270.0, h=0.8,
      type_raw=None, type_method="none", type_proposal=True, drawn_type="unknown")
furniture[-1]["status"] = "unverified"
furniture[-1]["evidence"] += [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": k,
                               "confidence": 0.6, "text": "a narrow table against the hall wall: console table (proposal)"}
                              for k in (1, 2)]

decor = [
    {"id": "dec_L0_001", "kind": "decor", "type": "curtain", "level_id": "L0", "room_id": yatak, "center": [3.0, 0.3, 0.0],
     "rotation_deg": 180.0, "size": [2.2, 0.08, 2.6], "window_id": "win_L0_001", "asset": None, "host_id": None,
     "source": "added_by_ai", "method": "ai", "slot": "window:win_L0_001", "colour": "cream", "confidence": 0.9, "status": "verified",
     "evidence": [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": k, "confidence": 0.9, "text": "linen curtain"} for k in (1, 2)]},
    {"id": "dec_L-1_001", "kind": "decor", "type": "plant_large", "level_id": "L-1", "room_id": salon, "center": [0.5, 0.6],
     "rotation_deg": 0.0, "size": [0.6, 0.6, 1.6], "species": "monstera", "pot": {"material": "rattan", "colour": "cream"},
     "asset": None, "host_id": None, "source": "added_by_ai", "method": "ai", "slot": "floor:corner_1", "colour": None,
     "confidence": 0.9, "status": "verified",
     "evidence": [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": k, "confidence": 0.9, "text": "monstera in a rattan pot"} for k in (1, 2)]},
    {"id": "dec_L-1_002", "kind": "decor", "type": "pendant_light", "level_id": "L-1", "room_id": salon, "center": [2.6, 5.6, 2.1],
     "rotation_deg": 0.0, "size": [0.45, 0.45, 0.5], "light_on": True, "asset": None, "host_id": None, "anchor_ids": ["f_L-1_003"],
     "source": "added_by_ai", "method": "ai", "slot": "ceiling:over_f_L-1_003", "colour": "brass", "confidence": 0.9, "status": "verified",
     "evidence": [{"file": "building.json", "method": "ai", "model": "Qwen/Qwen3-VL-8B-Instruct", "pass": k, "confidence": 0.9, "text": "pendant over the coffee table"} for k in (1, 2)]},
]

slab_outline = [[-0.125, -0.125], [10.125, -0.125], [10.125, 8.125], [-0.125, 8.125]]
void = [[8.8, 4.45], [9.9, 4.45], [9.9, 7.55], [8.8, 7.55]]
slabs = [
    {"id": "sl_L-1", "below_level_id": None, "above_level_id": "L-1", "z_top": -3.0, "thickness": 0.2, "thickness_source": "section",
     "outline": slab_outline, "openings": [], "variants": [], "status": "verified", "evidence": [ev("LINE:7A0", region="r6", rule="slab_bands")]},
    {"id": "sl_L0", "below_level_id": "L-1", "above_level_id": "L0", "z_top": 0.0, "thickness": 0.2, "thickness_source": "section",
     "outline": slab_outline, "openings": [{"id": "sv_L0_001", "kind": "stair_void", "furniture_id": "f_L-1_001", "polygon": void, "source": "derived"}],
     "variants": [], "status": "verified", "evidence": [ev("LINE:7A1", region="r6", rule="slab_bands")]},
    {"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "z_top": 3.0, "thickness": 0.2, "thickness_source": "section",
     "outline": slab_outline, "openings": [{"id": "sv_L1_001", "kind": "stair_void", "furniture_id": "f_L0_001", "polygon": void, "source": "derived"}],
     "variants": [], "status": "verified", "evidence": [ev("LINE:7A2", region="r6", rule="slab_bands")]},
]
pitch = 35.0
t = math.tan(math.radians(pitch))
eaves = 3.0 + 1.0 - 0.5 * t          # knee wall 1.0 m at the outer wall face, 0.5 m overhang
ridge = 3.0 + 1.0 + 4.125 * t
r3 = lambda v: round(v, 3)
roof = {
    "type": "gable", "type_source": "section", "over_level_id": "L1",
    "eaves_height": val(r3(eaves), evidence=[ev("LWPOLYLINE:8B0", region="r6", rule="roof_line")]),
    "ridge_height": val(r3(ridge), evidence=[ev("LWPOLYLINE:8B0", region="r6", rule="roof_line")]),
    "pitches_deg": [val(pitch, evidence=[ev("LWPOLYLINE:8B0", region="r6", rule="roof_line")])],
    "overhang": val(0.5, evidence=[ev("LWPOLYLINE:8B0", region="r6")]),
    "thickness": val(0.25, method="assumed", conf=0.0, note="not drawn: the roof is one line in the section"),
    "knee_wall": val(1.0, evidence=[ev("LINE:7B3", region="r6")]),
    "outline": [[-0.625, -0.625], [10.625, -0.625], [10.625, 8.625], [-0.625, 8.625]],
    "break_line": None, "ridge_lines": [[[-0.625, 4.0], [10.625, 4.0]]],
    "planes": [
        {"id": "rp_south", "points": [[-0.625, -0.625, r3(eaves)], [10.625, -0.625, r3(eaves)], [10.625, 4.0, r3(ridge)], [-0.625, 4.0, r3(ridge)]],
         "slope_deg": pitch, "aspect_deg": 270.0, "source": "derived"},
        {"id": "rp_north", "points": [[10.625, 8.625, r3(eaves)], [-0.625, 8.625, r3(eaves)], [-0.625, 4.0, r3(ridge)], [10.625, 4.0, r3(ridge)]],
         "slope_deg": pitch, "aspect_deg": 90.0, "source": "derived"},
    ],
    "openings": [{"id": "ro_001", "kind": "terrace", "room_id": teras,
                  "polygon": [[6.0, -0.625], [10.625, -0.625], [10.625, 4.0], [6.0, 4.0]],
                  "parapet_height": val(1.0, method="assumed", conf=0.0, note="parapet not drawn"),
                  "parapet_wall_ids": ["w_L1_001", "w_L1_002"], "source": "derived"}],
    "profile": {"region_id": "r6", "cut_axis": "y", "method": "vector",
                "points": [[-0.625, r3(eaves)], [4.0, r3(ridge)], [8.625, r3(eaves)]]},
    "covering": None, "covering_colour": None, "covering_source": None,
    "assumed": ["roof thickness", "gable ends (no roof plan)"],
    "status": "verified", "evidence": [ev("LWPOLYLINE:8B0", region="r6", rule="roof_line"), ev("LWPOLYLINE:8C0", region="r8", rule="elevation_outline")],
}
facade = {
    "faces": [{"side": "south", "wall_id": None, "level_id": "L-1", "z_range": [-3.0, -2.0], "material": "stone_cladding", "colour": None,
               "source": "elevation", "evidence": [ev("HATCH:9A0", layer="TARAMA", region="r7", rule="facade_hatch")]}],
    "elevations": [{"region_id": "r7", "title": "GÜNEY GÖRÜNÜŞÜ", "side": "south", "view_bearing_deg": 90.0, "windows": 4, "doors": 1,
                    "positions_m": [], "plan_check": {"matched": 5, "missing": 0, "extra": 0}},
                   {"region_id": "r8", "title": "DOĞU GÖRÜNÜŞÜ", "side": "east", "view_bearing_deg": 180.0, "windows": 0, "doors": 0,
                    "positions_m": [], "plan_check": {"matched": 0, "missing": 0, "extra": 0}}],
    "evidence": [ev("HATCH:9A0", layer="TARAMA", region="r7")],
}
site = {
    "boundary_walls": [{"id": f"sw_L0_{i:03d}", "level_id": "L0", "start": a, "end": b, "thickness": 0.2, "kind": "plot",
                        "height": val(1.2, method="assumed", conf=0.0, note="no elevation of the plot wall"), "build": True,
                        "evidence": [ev(f"LINE:SW{i}", layer="VAZIYET", region="r9")]}
                       for i, (a, b) in enumerate([([-6.0, -8.0], [16.0, -8.0]), ([16.0, -8.0], [16.0, 14.0]),
                                                   ([16.0, 14.0], [-6.0, 14.0]), ([-6.0, 14.0], [-6.0, -8.0])], 1)],
    "areas": [{"id": "sa_L0_otopark", "level_id": "L0", "label": "Otopark", "label_raw": "OTOPARK", "polygon": [[11.0, 8.5], [15.5, 8.5], [15.5, 13.5], [11.0, 13.5]],
               "anchor": [13.2, 11.0], "kind": "parking", "build": False, "evidence": [ev("TEXT:OT1", layer="VAZIYET", text="OTOPARK", region="r9")]},
              {"id": "sa_L0_bahce", "level_id": "L0", "label": "Bahçe", "label_raw": "BAHÇE", "polygon": None, "anchor": [3.0, -5.0], "kind": "garden",
               "build": False, "evidence": [ev("TEXT:BA1", layer="VAZIYET", text="BAHÇE", region="r9")]}],
    "decor": [{"id": "sd_L0_001", "level_id": "L0", "kind": "tree", "center": [-3.0, -4.0], "size": [3.0, 3.0], "build": True,
               "evidence": [ev("INSERT:AG1", layer="AGAC", region="r9")]}],
    "openings": [],
    "ground": {"levels": [{"side": "all", "azimuth_deg": None, "z": val(0.0, evidence=[ev("LINE:GL1", region="r6", rule="ground_line")])}],
               "terrain": "flat", "light_wells": []},
    "north_deg": val(0.0, evidence=[ev("INSERT:KUZEY", layer="VAZIYET", region="r9", rule="north_arrow")]),
    "paving": [{"id": "sp_001", "polygon": [[6.5, 8.125], [7.5, 8.125], [7.5, 14.0], [6.5, 14.0]], "z": 0.0, "material": None, "colour": None,
                "area_id": None, "source": "site_plan", "build": True, "evidence": [ev("LWPOLYLINE:YOL1", layer="VAZIYET", region="r9")]}],
    "grass": [{"id": "sg_001", "polygon": [[-6.0, -8.0], [16.0, -8.0], [16.0, 14.0], [-6.0, 14.0]], "z": None, "material": None, "colour": None,
               "area_id": "sa_L0_bahce", "source": "assumed", "build": True, "evidence": []}],
    "parking": [{"id": "spk_001", "polygon": [[11.0, 8.5], [15.5, 8.5], [15.5, 13.5], [11.0, 13.5]], "z": 0.0, "material": None, "colour": None,
                 "area_id": "sa_L0_otopark", "source": "site_plan", "build": True, "evidence": [ev("TEXT:OT1", layer="VAZIYET", text="OTOPARK", region="r9")]}],
    "plot": {"id": "plot", "polygon": [[-6.0, -8.0], [16.0, -8.0], [16.0, 14.0], [-6.0, 14.0]], "z": None, "material": None,
             "source": "site_plan", "build": True, "evidence": [ev("LWPOLYLINE:PLOT", layer="VAZIYET", region="r9")]},
}
variants = [
    {"id": "base", "label": "Base", "levels": ["L-1", "L0", "L1"], "base": True, "changes": [], "rooms_changed": [], "exterior_changed": False},
    {"id": "l-1b-acik-mutfak", "label": "Bodrum Kat: Açık mutfak (open kitchen)", "levels": ["L-1b", "L0", "L1"], "base": False,
     "changes": [{"variant_group": "vg_L-1", "level_id": "L-1b", "replaces": "L-1"}], "rooms_changed": [open_k], "exterior_changed": False,
     "evidence": [ev("MTEXT:5A1", text="BODRUM KAT PLANI (AÇIK MUTFAK)", region="r3")]},
]
def page(region, cls, rcls, lv, label_raw, variant):
    return {"page": 1, "class": cls, "kind": "vector", "level_id": lv, "level_label_raw": label_raw, "classifier": "title",
            "region_id": region, "region_box": None, "region_class": rcls, "variant": variant,
            "scale": {"metres_per_unit": 0.01, "method": "unit_check", "confidence": 0.95,
                      "evidence": ev("$INSUNITS=4", rule="unit_check", text="header mm; area labels, level marks and door widths agree on cm")},
            "transform_to_building": None, "confidence": 0.99, "evidence": [ev(f"MTEXT:{region}", text=label_raw, region=region)],
            "debug_image": f"debug/ornek_bina_dxf_p1_{region}.png"}
pages = [page("r2", "floor_plan", "floor_plan", "L-1", "BODRUM KAT PLANI", "base"),
         page("r3", "floor_plan", "alternative_floor_plan", "L-1b", "BODRUM KAT PLANI (AÇIK MUTFAK)", "Açık mutfak"),
         page("r4", "floor_plan", "floor_plan", "L0", "ZEMİN KAT PLANI", "base"),
         page("r5", "floor_plan", "floor_plan", "L1", "ÇATI KAT PLANI", "base")]
boxes = {"r2": [0, 3000, 1100, 3900], "r3": [1300, 3000, 2400, 3900], "r4": [0, 1800, 1100, 2700], "r5": [1300, 1800, 2400, 2700]}
# Each plan is drawn with its outer wall centre lines starting at (x0 + 50, y0 + 50) of its box (cm), so the outer face
# corner (the building origin) is at (x0 + 37.5, y0 + 37.5).
def to_building(box):
    x0, y0 = box[:2]
    return [0.01, 0.0, round(-(x0 + 37.5) * 0.01, 4), 0.0, 0.01, round(-(y0 + 37.5) * 0.01, 4)]
for p in pages:
    p["region_box"] = boxes[p["region_id"]]
    p["transform_to_building"] = to_building(boxes[p["region_id"]])
OTHER_BOXES = {"r6": [0, 600, 1300, 1500], "r7": [1400, 600, 2600, 1300], "r8": [2700, 600, 3700, 1300], "r9": [2600, 1800, 3900, 3900]}
for rid, cls in (("r6", "section"), ("r7", "elevation"), ("r8", "elevation"), ("r9", "site_plan")):
    pages.append({"page": 1, "class": cls, "kind": "vector", "level_id": None, "level_label_raw": None, "classifier": "title",
                  "region_id": rid, "region_box": OTHER_BOXES[rid], "region_class": cls, "variant": None, "skip_reason": "read by the sheets stage (heights / exterior), not a plan",
                  "scale": None, "transform_to_building": None, "confidence": 0.95, "evidence": [], "debug_image": None})
building = {
    "schema_version": "0.1",
    "project": {"id": "example-m10", "source_folder": "projects/example-m10", "created_utc": "2026-10-08T12:00:00Z", "pipeline_commit": "abc1234",
                "unit_system": "metric",
                "datum": val(0.0, evidence=[ev("MTEXT:KOT0", region="r6", rule="level_mark", text="±0.00")]),
                "brief": {"furnished_rooms": "complete", "variants": "all", "failed_levels": "leave_out", "site": "full",
                          "render": {"twin_rooms": "one", "exterior_views": True}}},
    "status": "ok",
    "documents": [{"id": "doc_dxf", "file": FILE, "format": "dxf", "converter": None, "unit_system": "metric", "source_kind": "dxf", "pages": pages}],
    "levels": levels, "walls": walls, "openings": openings, "rooms": rooms, "furniture": furniture, "decor": decor,
    "conflicts": [{"id": "c_001", "kind": "level_mark_mismatch", "element_ids": ["L1"],
                   "description": "Level mark of the attic reads +3.10 in the elevation r7; the section's slab lines give +3.00",
                   "resolution": "geometry wins: +3.00 kept"},
                  {"id": "c_002", "kind": "unit_mismatch", "element_ids": ["doc_dxf"],
                   "description": "$INSUNITS = 4 (mm) but area labels, level marks and door widths agree on cm",
                   "resolution": "cm used (unit check, 3 of 3 checks agree)"}],
    "unverified": ["f_L0_009"], "warnings": ["f_L0_009: type proposal console_table (AI, both passes) kept unverified"],
    "variants": variants, "levels_left_out": [], "slabs": slabs, "roof": roof, "facade": facade, "site": site,
}
XY_KEYS = ("start", "end", "center", "point", "anchor", "wall_point")
XY_LIST_KEYS = ("polygon", "outline", "break_line")
def shift_xy(obj, key=None):
    """Shift every building x, y of the example by SHIFT (z, sizes, angles and source units untouched)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in XY_KEYS and isinstance(v, list) and len(v) >= 2 and all(isinstance(a, (int, float)) for a in v[:2]):
                obj[k] = [round(v[0] + SHIFT, 4), round(v[1] + SHIFT, 4)] + v[2:]
            elif k in XY_LIST_KEYS and isinstance(v, list):
                obj[k] = [[round(a[0] + SHIFT, 4), round(a[1] + SHIFT, 4)] + a[2:] for a in v]
            elif k == "ridge_lines":
                obj[k] = [[[round(a[0] + SHIFT, 4), round(a[1] + SHIFT, 4)] for a in line] for line in v]
            elif k == "points" and isinstance(v, list) and v and isinstance(v[0], list) and len(v[0]) == 3:
                obj[k] = [[round(a[0] + SHIFT, 4), round(a[1] + SHIFT, 4), a[2]] for a in v]
            elif k == "points" and key == "profile":
                obj[k] = [[round(a[0] + SHIFT, 4), a[1]] for a in v]
            elif k in ("pixel_box", "region_box", "transform_to_building", "size", "evidence", "z_range"):
                continue
            else:
                shift_xy(v, k)
    elif isinstance(obj, list):
        for v in obj:
            shift_xy(v, key)
for block in ("walls", "openings", "rooms", "furniture", "decor", "slabs", "site"):
    shift_xy(building[block])
shift_xy(building["roof"])
errs = B.validation_errors(building)
assert not errs, errs
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "building_m10.example.json").write_text(json.dumps(building, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# ---------------- sheets.json example (same project) ----------------
def sev(entity, rule, conf=1.0, text=None, region=None, layer=None):
    e = {"file": FILE, "page": 1, "layer": layer, "entity": entity, "method": "vector", "confidence": conf, "rule": rule}
    if text: e["text"] = text
    return e
def region(rid, box, cls, method, conf, title, use, level=None, variant=None, **kw):
    r = {"id": rid, "file": FILE, "sheet": "s1", "page": 1, "box": box, "box_m": [round((box[2] - box[0]) * 0.01, 2), round((box[3] - box[1]) * 0.01, 2)],
         "entities": kw.pop("entities", 400), "frame": "LWPOLYLINE:F1", "class": cls, "class_method": method, "class_confidence": conf,
         "status": "verified" if method != "ai" else "unverified",
         "title": ({"text": title, "entity": f"MTEXT:{rid}", "box": [box[0], box[1] - 60, box[0] + 600, box[1] - 30], "language": "tr",
                    "keywords": kw.pop("keywords", [])} if title else None),
         "features": kw.pop("features", {}), "level": level, "variant_group": None, "variant": variant, "variant_slug": None, "variant_gloss": None,
         "ai": [{"pass": 1, "model": "Qwen/Qwen3-VL-8B-Instruct", "class": cls, "level_word": None, "variant_word": None, "confidence": 0.9, "reason": "", "error": None},
                {"pass": 2, "model": "zai-org/GLM-4.6V-Flash", "class": cls, "level_word": None, "variant_word": None, "confidence": 0.85, "reason": "", "error": None}],
         "metres_per_unit": 0.01, "transform_to_building": None, "registration": None, "use": use, "ignored_reason": None, "conflicts": [],
         "evidence": [sev(f"MTEXT:{rid}", "title_keyword", text=title)] if title else []}
    r.update(kw)
    return r
lvl = lambda o, label, lid, kind: {"order": o, "label": label, "id": lid, "kind": kind, "method": "title", "evidence": []}
regions = [
    region("r1", [2600, 0, 3000, 200], "title_block", "geometry", 0.9, None, "ignored", ignored_reason="title block", entities=30,
           features={"short_texts": 12, "on_frame_edge": True}),
    region("r2", boxes["r2"], "floor_plan", "title", 0.99, "BODRUM KAT PLANI", "read", level=lvl(-1, "Bodrum Kat", "L-1", "basement"), variant="base",
           keywords=["BODRUM", "KAT PLANI"], features={"closed_wall_loops": 3, "room_labels": 3}),
    region("r3", boxes["r3"], "alternative_floor_plan", "title", 0.99, "BODRUM KAT PLANI (AÇIK MUTFAK)", "read",
           level=lvl(-1, "Bodrum Kat", "L-1b", "basement"), variant="Açık mutfak", keywords=["BODRUM", "KAT PLANI", "(AÇIK MUTFAK)"],
           features={"closed_wall_loops": 2, "room_labels": 2}),
    region("r4", boxes["r4"], "floor_plan", "title", 0.99, "ZEMİN KAT PLANI", "read", level=lvl(0, "Zemin Kat", "L0", "floor"), variant="base",
           keywords=["ZEMİN", "KAT PLANI"], features={"closed_wall_loops": 3, "room_labels": 3}),
    region("r5", boxes["r5"], "floor_plan", "title", 0.99, "ÇATI KAT PLANI", "read", level=lvl(1, "Çatı Katı", "L1", "attic"), variant="base",
           keywords=["ÇATI KAT", "KAT PLANI"], features={"closed_wall_loops": 3, "room_labels": 3, "roof_outline": True}),
    region("r6", [0, 600, 1300, 1500], "section", "title", 0.99, "A-A KESİTİ", "heights", keywords=["KESİT"],
           features={"slab_bands": 3, "level_marks": 4, "roof_lines": 2, "ground_lines": 2}),
    region("r7", [1400, 600, 2600, 1300], "elevation", "title", 0.99, "GÜNEY GÖRÜNÜŞÜ", "exterior", keywords=["GÖRÜNÜŞ"],
           features={"window_rows": 2, "ground_lines": 1, "hatches": 1}),
    region("r8", [2700, 600, 3700, 1300], "elevation", "title", 0.99, "DOĞU GÖRÜNÜŞÜ", "exterior", keywords=["GÖRÜNÜŞ"],
           features={"window_rows": 1, "ground_lines": 1}),
    region("r9", [2600, 1800, 3900, 3900], "site_plan", "title", 0.99, "VAZİYET PLANI", "exterior", keywords=["VAZİYET"],
           features={"north_arrow": True, "plot_boundary": True}),
    region("r10", [2600, 300, 3000, 550], "legend", "title", 0.95, "LEJANT", "ignored", ignored_reason="legend", keywords=["LEJANT"], entities=40),
]
regions[2].update({"variant_group": "vg_L-1", "variant_slug": "acik-mutfak", "variant_gloss": "open kitchen"})
regions[1].update({"variant_group": "vg_L-1", "variant_slug": "base"})
REF = boxes["r4"]
for r in regions:
    if r["id"] in boxes:
        x0, y0 = r["box"][:2]
        r["transform_to_building"] = to_building(r["box"])
        # p_ref = p_source * 0.01 + shift_m: the same plan drawn (x0 - REF x0, y0 - REF y0) cm away from the reference.
        r["registration"] = {"reference": None if r["id"] == "r4" else "r4", "method": "reference" if r["id"] == "r4" else "outline_icp",
                             "rotation_deg": 0.0, "shift_m": [round((REF[0] - x0) * 0.01, 3), round((REF[1] - y0) * 0.01, 3)],
                             "residual_m": 0.0 if r["id"] == "r4" else 0.004, "matched": 0 if r["id"] == "r4" else 4,
                             "stairs_aligned": None if r["id"] == "r4" else True, "note": None}
sheets = {
    "schema_version": "1.0", "kind": "sheets", "project": "example-m10", "created_utc": "2026-10-08T12:00:00Z", "code_commit": "abc1234",
    "documents": [{"file": FILE, "format": "dxf", "converter": None,
                   "units": {"insunits": 4, "metres_per_unit": 0.01, "method": "unit_check",
                             "checks": [{"check": "area_labels", "unit": "cm", "score": 0.97, "samples": 6, "note": None},
                                        {"check": "level_marks", "unit": "cm", "score": 1.0, "samples": 3, "note": None},
                                        {"check": "door_widths", "unit": "cm", "score": 0.95, "samples": 10, "note": None}],
                             "conflict": "$INSUNITS = 4 (mm) but area labels, level marks and door widths agree on cm"},
                   "sheets": [{"id": "s1", "space": "model", "box": [0, 0, 3900, 3900],
                               "frames": [{"entity": "LWPOLYLINE:F1", "box": [-50, -50, 3950, 3950]}], "gap_units": 84.0,
                               "debug_image": "sheets_debug/ornek_bina_dxf_s1.png"}]}],
    "regions": regions,
    "stray": [{"file": FILE, "sheet": "s1", "entity": "LINE:DEAD", "type": "LINE", "layer": "0", "box": [-90000, 80000, -89900, 80400],
               "distance_m": 1203.5, "reason": "far outside the frame, 1 entity (< 1 % of the sheet)"}],
    "levels": [{"id": "L-1", "order": -1, "label": "Bodrum Kat", "kind": "basement", "base_region": "r2",
                "alternatives": [{"region": "r3", "variant": "Açık mutfak", "slug": "acik-mutfak", "level_id": "L-1b", "base_unclear": False}],
                "furniture_regions": [], "evidence": []},
               {"id": "L0", "order": 0, "label": "Zemin Kat", "kind": "floor", "base_region": "r4", "alternatives": [], "furniture_regions": [], "evidence": []},
               {"id": "L1", "order": 1, "label": "Çatı Katı", "kind": "attic", "base_region": "r5", "alternatives": [], "furniture_regions": [], "evidence": []}],
    "variants": [{"id": "base", "label": "Base", "base": True, "levels": ["L-1", "L0", "L1"], "regions": ["r2", "r4", "r5"]},
                 {"id": "l-1b-acik-mutfak", "label": "Bodrum Kat: Açık mutfak (open kitchen)", "base": False, "levels": ["L-1b", "L0", "L1"],
                  "regions": ["r3", "r4", "r5"]}],
    "heights": {
        "section_regions": ["r6"], "cut_axis": "y",
        "datum": val(0.0, evidence=[sev("MTEXT:KOT0", "level_mark", text="±0.00")]),
        "levels": [{"level_id": "L-1", "floor_z": val(-3.0, evidence=[sev("LINE:7A0", "slab_bands")]),
                    "ceiling_height": val(2.8, evidence=[sev("LINE:7A1", "slab_bands")]), "floor_to_floor": val(3.0, evidence=[sev("LINE:7A1", "slab_bands")]),
                    "level_mark": val(-3.0, method="ocr", conf=0.9, evidence=[sev("MTEXT:KOT1", "level_mark", text="-3.00")])},
                   {"level_id": "L0", "floor_z": val(0.0, evidence=[sev("LINE:7A1", "slab_bands")]),
                    "ceiling_height": val(2.8, evidence=[sev("LINE:7A2", "slab_bands")]), "floor_to_floor": val(3.0, evidence=[sev("LINE:7A2", "slab_bands")]),
                    "level_mark": val(0.0, evidence=[sev("MTEXT:KOT0", "level_mark", text="±0.00")])},
                   {"level_id": "L1", "floor_z": val(3.0, evidence=[sev("LINE:7A2", "slab_bands")]),
                    "ceiling_height": val(2.4, evidence=[sev("LWPOLYLINE:8B1", "roof_underside")], note="flat part under the collar; sloped to the knee wall"),
                    "floor_to_floor": None, "level_mark": val(3.0, evidence=[sev("MTEXT:KOT2", "level_mark", text="+3.00")])}],
        "slabs": [{"between": [None, "L-1"], "thickness": val(0.2, evidence=[sev("LINE:7A0", "slab_bands")]), "z_top": val(-3.0, evidence=[sev("LINE:7A0", "slab_bands")])},
                  {"between": ["L-1", "L0"], "thickness": val(0.2, evidence=[sev("LINE:7A1", "slab_bands")]), "z_top": val(0.0, evidence=[sev("LINE:7A1", "slab_bands")])},
                  {"between": ["L0", "L1"], "thickness": val(0.2, evidence=[sev("LINE:7A2", "slab_bands")]), "z_top": val(3.0, evidence=[sev("LINE:7A2", "slab_bands")])}],
        "ground": [{"side": "all", "z": val(0.0, evidence=[sev("LINE:GL1", "ground_line")])}],
        "roof": {"eaves_z": roof["eaves_height"], "ridge_z": roof["ridge_height"], "pitches_deg": roof["pitches_deg"], "knee_wall": roof["knee_wall"],
                 "overhang": roof["overhang"], "thickness": roof["thickness"],
                 "profile": roof["profile"]["points"]},
    },
    "exterior": {
        "roof": {"type": "gable", "type_source": "section", "outline": roof["outline"], "break_line": None, "ridge_lines": roof["ridge_lines"],
                 "covering": None, "evidence": roof["evidence"]},
        "facade": [{"region": "r7", "side": "south", "z_range": [-3.0, -2.0], "material": "stone_cladding", "source": "hatch",
                    "evidence": [sev("HATCH:9A0", "facade_hatch", layer="TARAMA")]}],
        "openings_seen": [{"region": "r7", "side": "south", "view_bearing_deg": 90.0, "windows": 4, "doors": 1, "positions_m": [], "plan_check": None},
                          {"region": "r8", "side": "east", "view_bearing_deg": 180.0, "windows": 0, "doors": 0, "positions_m": [], "plan_check": None}],
        "site": {"region": "r9", "plot": site["plot"]["polygon"], "plot_walls": [], "paving": [], "grass": [],
                 "parking": [{"polygon": site["parking"][0]["polygon"]}], "trees": [{"points": [site["decor"][0]["center"]]}], "labels": []},
        "north": site["north_deg"], "balconies": [], "chimneys": []},
    "conflicts": [{"id": "sc_001", "kind": "level_mark_mismatch", "regions": ["r6"],
                   "description": "example: a level mark that disagrees with the slab lines by more than 5 cm", "resolution": "geometry wins"},
                  {"id": "sc_002", "kind": "unit_mismatch", "regions": ["r2", "r3", "r4", "r5", "r6"],
                   "description": "$INSUNITS = 4 (mm) but area labels, level marks and door widths agree on cm", "resolution": "cm used"}],
    "warnings": [], "needs_review": [], "questions": 20, "answers": None,
}
import jsonschema
schema = json.loads(Path("wenart/schema/sheets.schema.json").read_text(encoding="utf-8"))
jsonschema.Draft202012Validator.check_schema(schema)
errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(sheets), key=lambda e: list(e.path))
assert not errs, [f"{list(e.path)}: {e.message}" for e in errs]
(OUT_DIR / "sheets.example.json").write_text(json.dumps(sheets, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("written", len(walls), "walls", len(openings), "openings", len(rooms), "rooms", len(furniture), "pieces", round(eaves, 3), round(ridge, 3))
