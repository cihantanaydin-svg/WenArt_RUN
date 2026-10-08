# Synthetic test projects (Milestone 2 §1, Milestone 6 §3, Milestone 7 §5.2)

Six generated projects with known ground truth, used to test the vector path
(`wenart/ingest`), the raster bake-off (`wenart/recognition`) and, from
Milestone 6, the one-command full runs (`wenart/run`): synthetic-01..03 were made
in Milestone 2, synthetic-04 and synthetic-05 in Milestone 6 (docs/milestone6.md §3),
synthetic-06 (a DWG drawn the way real CAD offices draw) in Milestone 7
(docs/milestone7.md §5.2, section [synthetic-06](#synthetic-06-the-cad-project) below).

```
python -m wenart.synthetic.generate --out projects --results results/synthetic
```

The command is deterministic and idempotent: fixed seeds, fixed DXF/PDF metadata,
byte-identical files on every run (`tests/test_synthetic.py::test_deterministic`
and `test_committed_projects_are_current` check this). After changing the
generator, run it again and commit `projects/`, `results/synthetic/` and
`tests/fixtures/synthetic-06-titled/` (`--only synthetic-05` regenerates one project).
synthetic-06's DWG needs LibreDWG's `dxf2dwg` (0.14, d9468ae; `scripts/cloud-setup.sh`
builds it into `~/.cache/wenart/libredwg/bin`); without it the generator writes
everything else and says that the DWG was not written.

## The five Level-based projects

| Project | Documents | Levels / rooms | Furniture in documents | Brief | Deliberate conflicts |
|---|---|---|---|---|---|
| `synthetic-01` | `zemin_kat.dxf` (L0), `1_kat.pdf` (L1, vector), `1_kat_scan.png` (scan of the PDF) | L0: Salon 24,50 m², Mutfak, Yatak Odası, Banyo, Hol; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo | L0 only, in Salon, Yatak Odası, Banyo (13 pieces) | `brief.yaml`: one `style` | none (the Salon label matches the polygon exactly) |
| `synthetic-02` | `plan_scan.png` (scan), `plan_photo.jpg` (phone photo). The source vector PDF is hidden in `truth/plan.pdf` | L0: Salon, Mutfak, Antre, Banyo, Yatak Odası (1+1 flat) | all rooms (19 pieces) | none (defaults) | none |
| `synthetic-03` | `kat_planlari.pdf` (3 pages: Bodrum, Zemin, 1. Kat), `mobilya_plani.dxf` (furniture plan of Zemin Kat: walls, openings, furniture, no dimensions) | L-1: Kiler ×2, Hol, Yatak Odası, WC, Banyo; L0: Salon, Mutfak, Antre, Hol, Yatak Odası, WC, Kiler; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo, Balkon | L0 only, DXF only (21 pieces incl. one `BLOK_A` of unknown type) | `brief.yaml`: `styles: [two prompts]` | `c_001` Salon label 24,00 m² vs 23,50 m² computed (2 %, within tolerance); `c_002` Bodrum left dimension prints `3,99` for 3,80 m (5 %); `c_003` the PDF Zemin page lacks the Mutfak window that the DXF has (count mismatch, DXF wins) |
| `synthetic-04` | `3_kat_plani.dxf` and `3_kat_plani_pdf.pdf` (vector): the same level twice, both with walls, openings, furniture and dimensions | L3 (`3. KAT PLANI`, elevation 9.0): Salon + Mutfak 39,05 m² (L-shaped, 6 vertices), Hol (L-shaped, 8.32 m²), Yatak Odası, Banyo, Çocuk Odası (2+1 flat) | Salon + Mutfak, Yatak Odası, Banyo (21 pieces, each on both documents; the armchair at 45°; a `KUVET` bathtub); Hol and Çocuk Odası empty | `brief.yaml`: `style` (Japandi, walnut floor, cream walls) | none |
| `synthetic-05` | `zemin_kat.dxf` (floor plan: walls, openings, dimensions, **no furniture**), `zemin_kat_mobilya.dxf` (furniture plan `ZEMİN KAT MOBİLYA PLANI`: walls, openings, furniture, no dimensions), `style_photos/salon_referans.jpg` (not a document) | L0: Salon 19,76 m², Ebeveyn Yatak Odası, Ebeveyn Banyo (en-suite), Mutfak, Hol, Antre, Banyo, Yatak Odası, Çalışma Odası (3+1 flat, notched outline) | furniture plan only (26 pieces incl. two `YATAK_TEK` single beds); Hol, Antre and Çalışma Odası empty | `brief.yaml`: `style` (Modern, white walls), `style_photos: [salon_referans.jpg]`, `polish: false` | none |

Footprints: 01 = 9.6 × 7.2 m, 02 = 8.4 × 6.6 m, 03 = 10.2 × 7.8 m (all levels of a
project share the outline), 04 = 12.0 × 8.0 m, 05 = 13.5 × 9.0 m with a 3.0 × 1.75 m
recess at the bottom right (six outer walls). Outer walls 0.25 m, inner walls 0.10 m,
ceiling 2.70 m assumed (no section: one warning per level).

### What synthetic-04 and synthetic-05 add

| Project | Purpose (what no earlier project covers) | Expected ingest result |
|---|---|---|
| `synthetic-04` | non-rectangular rooms (two L shapes); a single-level vector project on a level other than L-1/L0/L1; the same level as DXF and vector PDF, both with furniture (the PDF footprints carry no type and must match the typed DXF pieces); furniture at a non-right angle; the bathtub block; a combined `SALON + MUTFAK` label (room type `living`, its kitchen pieces stay kitchen pieces); a walnut floor and the Japandi family | status ok, 10 walls (4 exterior), 15 openings (5 doors, 10 windows), 5 rooms, 21 pieces with 2 evidence entries each (DXF `INSERT` + PDF `path`), 0 conflicts, 0 unverified, the 45° armchair (rotation 315°, front 225°) matched across DXF and PDF; 2 rooms for the AI layout (Hol, Çocuk Odası) |
| `synthetic-05` | a notched outline (`LevelBuilder(outline=...)`); the branch "floor plan without furniture + furniture plan = the furniture source" end to end; an en-suite labelled `EBEVEYN BANYO` (room type `bathroom`); two bathrooms on one level; room type `other` (`ÇALIŞMA ODASI`); single beds; a style photo; `polish: false` | status ok, 14 walls (6 exterior, each with evidence from both DXFs), 19 openings (9 doors, 10 windows), 9 rooms, 26 pieces (furniture-plan evidence only), 0 conflicts, 0 unverified, warning `Zemin Kat: furniture taken from zemin_kat_mobilya.dxf (26 pieces); zemin_kat.dxf draws none`; 3 rooms for the AI layout (Hol, Antre, Çalışma Odası); with the photo terms the floor becomes `concrete_polished` (photo), the walls stay white (the brief wins) |

The style photo of synthetic-05 is a byte copy of
`tests/fixtures/style_photo_synthetic-03_salon.jpg` (our own Milestone 4 render of
the synthetic-03 Salon, no third-party image), listed in `Project.style_photos` and
copied by `generate_project`. The ingest reads only the top level of a project
folder (`wenart/ingest/classify.py`), so `style_photos/` is never a document.

Room types come from `wenart.building.room_type_for` (also used for the truth): a
keyword matches at the start of a word (`banyosu` → `banyo`), and when several match
the type earliest in `wc > bathroom > storage > balcony > bedroom > living > kitchen >
hall > other` wins (`EBEVEYN BANYO` → bathroom, `SALON + MUTFAK` → living). The
Milestone 6 keywords `lavabo`/`tuvalet` → wc, `dus` → bathroom, `giris` → hall,
`teras` → balcony, `calisma` → other left the room types of synthetic-01..03
unchanged (`tests/test_building.py` pins every room of the five projects).

All layouts live in `wenart/synthetic/projects.py` as readable code; the room
polygons, IDs, door rotations and furniture-to-room links are derived from the
walls by `wenart/synthetic/model.py` (shapely union of the wall rectangles,
interior rings = rooms). The generator refuses inconsistent layouts (label in
no room, opening off its wall, furniture crossing a wall).

Outer walls: `LevelBuilder(title, width, height)` draws the four walls of the
rectangle (indices 0..3: bottom, right, top, left). `LevelBuilder(title,
outline=[(x, y), ...])` takes the outer face of a non-rectangular building
(axis-aligned edges, bounding box from the origin) and draws one outer wall per
edge, in edge order: each wall runs to the outer corner at a convex vertex and
on to the inner corner (one wall thickness past the vertex) at a reflex vertex,
so the wall rectangles overlap at every corner and their union is one closed
ring. The default rectangle is the same rule with four vertices.

## synthetic-06: the CAD project

A 2+1 flat (24'-0" × 30'-6") drawn "the real way" in **inches** with English names,
delivered as a **DWG only** — the case the generic DXF adapter
(`wenart/ingest/dxf_generic.py`) and LibreDWG (`wenart/ingest/dwg.py`) exist for. It
is a `CadProject` (`wenart/synthetic/projects.py: plan_06`, `project_06`), written by
`dxf_writer.write_cad_dxf` and `generate.generate_cad_project`.

| | |
|---|---|
| Folder | `synthetic-06.dwg` (the only document), `source/synthetic-06.dxf` (what the DWG is written from; not read by the pipeline, which reads the top level only), `brief.yaml` (Mid-century modern), `truth/building.json`, `truth/pages.json` |
| DWG | `dxf2dwg --as r2000` (AC1015, codepage ANSI_1252); deterministic, sha256 pinned in `projects.DWG_SHA256_06` (the generator refuses another hash) |
| Units | `$INSUNITS = 1` (inches), `$MEASUREMENT = 0`, `$LUNITS = 4`; the building sits at (480", 240") in the drawing, so `transform_to_building = [0.0254, 0, -12.192, 0, 0.0254, -6.096]` |
| Walls (`A-WALL`) | one SOLID HATCH, ACI 7, over the wall union: the outer loop (external path) and one island per room face (5), plus the same rings as closed outline polylines; exterior walls 9", interior 6"; the walls run on through doors and windows |
| Doors (`A-DOOR`) | an ARC (centre = hinge on the face of the wall it swings from, radius = clear width) and the open leaf as a LINE from the hinge to the arc end: entrance 3'-0", bath 2'-6", the bedroom and living doors 2'-8" |
| Windows (`A-GLAZ`) | three lines along the wall band (both faces and the glass) and two jamb lines; 8 windows |
| Furniture (`A-FURN`) | block inserts (`blocks.CAD_BLOCKS`, inches, front = −Y): `SOFA-3`, `DINING-6` (the table; its six chairs are nested `CHAIR` inserts, 2" clear of it), `BED-DOUBLE` (pillows at the head), `WC` (cistern + an ELLIPSE bowl), `BASIN` (a CIRCLE bowl); the bedroom and the lobby are empty |
| Labels (`A-ANNO`) | MTEXT `LIVING ROOM` + `14'-0" X 12'-0"` (the size line; the living face is exactly 14' × 12'), a `ROOMTAG` insert whose `NAME` attribute says `KITCHEN`, TEXT `LOBBY`, `BATH`, `BED ROOM`, `MASTER BED ROOM`; **no title** |
| Dimensions (`A-DIMS`) | feet-inch texts as the override (ezdxf cannot format architectural units): bottom chain 9'-0" + 15'-0" and 24'-0" as rotated dimensions; left chain 13'-0" + 5'-6" + 12'-0" and 30'-6" as **aligned** dimensions (dimtype 1); one **rotated vertical** 30'-6" on the right (its angle is lost in the DWG and recovered by the reader) |
| Open kitchen | the kitchen (8'-0" × 12'-0") is open to the living room beside a wall stub whose free end stops 6'-0" short of the outer wall: the expected **virtual separator** `o_L0_001` runs from the stub's end along its axis to the wall face (docs/milestone7.md §2.7.1) |

Truth (`build_cad_truth`, the §1.3 fields the generic core must reproduce):
`project.unit_system` and `documents[].unit_system` `imperial`, `documents[].source_kind`
`dxf`, the converter `libredwg dwg2dxf 0.14 d9468ae…`; page class `floor_plan` by
classifier `generic_labels` (confidence 0.6); level `L0` "Ground floor" with
`label_source: "assumed"` (evidence = the six room labels) and the warning `level title
missing: assumed L0 Ground floor`; 9 walls (4 exterior; true thicknesses 0.2286 / 0.1524 m,
the core rounds to 5 mm), evidence the hatch; 5 doors (`height` 2.10 `assumed`), 8 windows
(`sill_height` 0.90, `height` 1.20 `assumed`), the separator (`virtual`, `wall_id null`,
`line`, evidence `derived`); 6 rooms whose faces are the holes of the wall union with the
separator's band (the stub's band extended to the face) bridged — Kitchen (from the
attribute), Living Room (with `label_size` status `ok`), Bath, Lobby (hall), Bed Room,
Master Bed Room; 11 pieces typed by block name (`type_method: block_name`, `type_raw` =
the block chain, e.g. `DINING-6/CHAIR`), the table without a front (nothing drawn says
which side it is). The DWG and the DXF read the same (`tests/test_dwg.py`).

LibreDWG 0.14 workarounds in the writer (documented in `write_cad_dxf`): `dxf2dwg` stops on
an MTEXT rotation angle (code 50), so the upright texts of the rendered dimension blocks
carry a direction vector; it stores an MTEXT's DXF code 40 in the reference-rectangle width
(height 0 in the DWG), so the label MTEXT also states its height inline (`\H9;`); and it
drops the angle of rotated dimensions, which `dxf_generic` recovers from the dimension
block (`dimension_angle_from_block`).

The **titled variant** (`TEXT "GROUND FLOOR PLAN"`, 18", above the plan; written last, so
every other handle is the same) is a test fixture, not a project:
`tests/fixtures/synthetic-06-titled/synthetic-06-titled.dxf` + `truth/building.json`
(level "Ground Floor" from the title, `label_source: "title"`, classifier `title`). The
generator writes it when `--out` is the repository's `projects` folder (or `--fixtures DIR`).

## synthetic-07: one CAD sheet with every drawing kind

Milestone 10 test data for the `sheets` stage (docs/milestone10.md §3.4, acceptance row 5): a 10.0 × 8.0 m house with
a basement and its open-kitchen alternative, a ground floor and an attic under a 35° gable roof with a roof terrace,
drawn the way a CAD office draws it (like real02): **everything on one model-space sheet in centimetres**, drawings side
by side, titles below the drawings. It is a `SheetProject` (`wenart/synthetic/sheet.py`: the layout, `sheet_writer.py`:
the DXF, `sheet_truth.py`: the truth, `generate.generate_sheet_project`). The layout is data (`Prim` lists in one
metric frame per drawing, the sheet position of each frame), the drawing and every truth number come from it.

| | |
|---|---|
| Folder | `sheet.dxf` (the only document), `source/sheet.dwg` (a DWG copy, not a document), `brief.yaml`, `truth/building.json`, `truth/sheets_truth.json`, `truth/heights_truth.json`, `truth/exterior_truth.json` |
| DXF | R2000 (AC1015), `$INSUNITS = 5` (cm), `$MEASUREMENT = 1`, 25 layers, fixed metadata (byte-identical on every run). The file is cp1252: İ, Ş, Ğ ... are `\U+XXXX` escapes. `ezdxf.recover.readfile` (what the pipeline uses) decodes them, a plain `ezdxf.readfile` does not (`plain_text()` does not either) |
| DWG | `dxf2dwg --as r2000` from the DXF (LibreDWG 0.14 d9468ae, sha256 pinned in `projects.DWG_SHA256_07`; without `dxf2dwg` the generator does not write it and says so). It reads exactly like the DXF (same entities, layers, blocks, texts; only the MTEXT height field is lost, the height is also written inline as `\H20;`). It sits in `source/` because the pipeline reads the top level only: both files at the top level would be two documents holding the same sheet. A test of the DWG path copies it to a temporary project |
| Stray | one LINE on layer `0` at (−90000, 80000) – (−89900, 80400) cm, 1,175 m from the nearest drawing |

### The sheet (frame 11,000 × 5,600 cm, title block on its bottom-right edge)

The regions in reading order (top to bottom by box top, then left to right; the box tops all differ by ≥ 10 cm, the
generator refuses a tie). A region box is the box of its non-text entities (INSERTs by their block geometry), the texts
join the nearest region by their insertion point, the frame is not a region.

| id | class | title (below the drawing) | level / variant | box (cm) | registration `shift_m` | use |
|---|---|---|---|---|---|---|
| r1 | floor_plan | `BODRUM KAT PLANI` | L-1 basement, base | 600, 4200, 1600, 5000 | 34.0, −1.6 | read |
| r2 | alternative_floor_plan | `BODRUM KAT PLANI (AÇIK MUTFAK)` | L-1b, `Açık mutfak` (`acik-mutfak`, gloss open kitchen) | 2300, 4175, 3300, 4975 | 17.0, −1.35 | read |
| r3 | floor_plan | `ZEMİN KAT PLANI` (the reference) | L0 | 4000, 3910, 5000, 4950 | 0, 0 | read |
| r4 | floor_plan | `ÇATI KAT PLANI` | L1 attic | 5700, 4025, 6800, 4925 | −17.5, −0.35 | read |
| r5 | site_plan | `VAZİYET PLANI` | – | 7800, 2000, 10600, 4450 | −46.0, 13.4 (through its building outline) | exterior |
| r6 | section | `A-A KESİTİ` | – | 845, 1680, 2300, 2710.602 | – | heights |
| r7 | elevation | `GÜNEY GÖRÜNÜŞÜ` | – | 3700, 1990, 5300, 2700.602 | – | exterior |
| r8 | elevation | `DOĞU GÖRÜNÜŞÜ` | – | 5900, 1980, 7300, 2690.602 | – | exterior |
| r9 | legend | `LEJANT` | – | 8600, 800, 10400, 1550 | – | ignored |
| r10 | title_block | – (cells `PROJE`, `ÇİZEN`, `ÖLÇEK 1/100`, `TARİH`, `PAFTA`) | – | 5000, 0, 11000, 360 | – | ignored |

Plan titles are MTEXT, the others TEXT (height 30 cm). Each plan sits at its own offset (pure shifts, no rotation), so
`p_ref = p_source · 0.01 + shift_m` puts it on the ground-floor drawing and `transform_to_building` =
`[0.01, 0, −X0/100, 0, 0.01, −Y0/100]` (the building frame is the ground plan's frame in metres, origin at the min
corner of its outer faces; `(X0, Y0)` = the sheet position of the region's local origin). The same form holds for the
section (x → building y, y → z, **not flipped**: the cut line `A-A` on the ground plan runs along Y at x = 3.0 and looks
towards −X, so the section's left end is the south end; `cut_axis` y, `cut_at` 3.0, `flipped` false), for the elevations
(x → metres from the facade's left end seen from outside, y → z: that is the west end of the south facade and the south
end of the east facade, because a viewer outside the east facade looks west and has north on his right) and for the site
plan. The north arrow points up the sheet: building +Y is north (`north` 0.0), the south elevation looks north
(`view_bearing_deg` 90), the east elevation west (180). No unit conflict: the header says cm and every check agrees (area
labels `43.5M2` match the polygons, level marks match the slab spacing, door arcs 0.9 m, walls 0.10 / 0.25 m, text
20–30 cm).

### Drawing conventions

- **Plans** (`BODRUM`, `ZEMİN`, `ÇATI`): walls are **open two-point LWPOLYLINEs on layer `AR_w_sld`** (no wall word, like
  real02's `DBM_w_sld`): the rings of the wall union (outer faces, inner faces) cut at every opening; the gap is the
  opening's clear width. Columns: six closed 0.25 m squares on `S-BETON` per plan (four corners and the partition's two
  feet, inside the wall bands). Doors: INSERTs on `A_Kapi` (block `KAPI_80` / `KAPI_90`: leaf line + 90° arc; `KAPI_SURME_90`: a
  sliding leaf rectangle beside the wall plane with a travel arrow, no arc; `KAPI_CIFT_140`: two leaves, two quarter arcs);
  windows: INSERTs on `A_Pencere` (`PENCERE_60/120`: three lines across the 0.25 m band and two jambs). Furniture: INSERTs
  on `A_Mobilya` (`blocks.BLOCKS` names and sizes; `MERDIVEN`, 1.0 × 3.0 m, 12 risers and an arrow, the only new block).
  Room labels: MTEXT `SALON\P43.5M2` (height 20 cm, inline `\H20;`, top-left at a point inside the room). The attic plan
  adds the roof outline (closed polyline, `DASHED`, 0.5 m outside the outer faces) and the ridge line (`DASHED`, y = 4.0);
  the ground plan adds the cut line `A-A` (`DASHDOT`, arms and arrow heads pointing to −X, the letter `A` twice).
- **Building**: outer faces 0..10 × 0..8, outer walls 0.25 m, inner 0.10 m; a partition at x = 6.10 and one at y = 4.00 (the
  right side) cut the plan into a large room (5.80 × 7.50 m, 43.5 m²) and two 3.60 × 3.70 m rooms (13.3 m²). The open-kitchen
  alternative drops the partition below y = 3.95: one L-shaped room (57.2 m²).

| Level | Rooms (label → type) | Drawn furniture | Doors | Windows |
|---|---|---|---|---|
| L-1 `BODRUM` (−3.00) | Salon (living), Mutfak (kitchen), Hol (hall) | 3-seat sofa `KANEPE_3LU` in the Salon; the counter run along the Mutfak's east wall (`BUZDOLABI`, `TEZGAH`, `EVIYE`, `OCAK`); `MERDIVEN` in the Hol | outside door (north wall, into the Hol), **sliding** Hol → Salon, swing Hol → Mutfak | 7, sill 2.00 m, height 0.60 m (below the ground line) |
| L-1b (alternative) | Salon + Açık Mutfak (living, L-shaped, 57.2 m²), Hol (`same_as` r_L-1_hol) | as L-1, in the open room | as L-1 | as L-1 |
| L0 `ZEMİN` (0.00) | Yatak Odası (bedroom), Banyo (bathroom), Hol | the only bed `YATAK_CIFT` (Yatak Odası), `KLOZET`, `LAVABO`, `DUS` (Banyo), `MERDIVEN` | entrance on the north wall, **double** `KAPI_CIFT_140`; garden door on the south wall; swing Hol → Yatak, Hol → Banyo | 6 (south 1.5 / 8.0, west 4.0, north 1.5 / 4.5, east 3.0) |
| L1 `ÇATI` (+3.00) | Oyun Odası (other, empty), Teras (balcony, empty), Hol | `MERDIVEN` | two swing doors | west and east gable windows (sill 0.60 m above the attic floor) |

- **Section `A-A KESİTİ`** (looking west, x = 3.0): three slab bands of 0.20 m (closed rectangles, tops −3.00 / ±0.00 / +3.00),
  wall lines between the bands (outer and inner faces of the south and north walls), ground lines at ±0.00 on both outer
  sides, level marks `-3.00`, `±0.00`, `+3.00` (a triangle whose apex touches a level line at the slab top, the text to its
  left), and the roof as one closed 6-point polyline (top line, tip drop, underside back): 35°, eaves 0.50 m outside the
  outer faces, 0.25 m thick perpendicular to the slope. **Knee wall 1.00 m = the outer face line from the attic floor to the
  roof underside** (the underside meets the outer face 4.00 m above ±0.00). Nothing else is drawn (no stair, no openings:
  the cut passes between the windows).
- **Elevations**: ground line, wall outline, roof, one closed rectangle per window (`G_Pencere`) and door (`G_Kapi`, with a
  handle line) at its true position and height, leaders with `SIVA` (render), `TAŞ KAPLAMA` (stone cladding), `KİREMİT` (clay
  tiles). The south facade has the hatched stone plinth (HATCH `ANSI31`, z 0 .. 0.6 m, the whole width). **The elevations draw
  the roof envelope**: the terrace cut of the attic plan is not shown in them. The basement is below the ground line and not
  drawn: its openings exist on the plans only.
- **Site plan**: plot boundary (closed `DASHDOT` polyline, −6..18 × −7..13 m), plot walls (two closed rectangles 0.20 m
  apart, outer face 0.05 m inside the boundary), the building outline (the ground plan's outer faces), a parking rectangle with
  `OTOPARK`, `BAHÇE`, three trees (INSERT `AGAC`), a road polygon with `YOL`, the north arrow (INSERT `KUZEY` + the letter `N`).
- **Legend**: a box with five samples (wall, column, door, dashed line, hatch) and their words.

### Truth (`truth/`)

- `sheets_truth.json`: the field names of `sheets.json` (docs/milestone10.md §1.2) with plain values: `documents[].units`
  (cm, no conflict), `sheets[]` (box = the frame, `gap_units` = 1.5 % of its diagonal), `regions[]` as in the table above
  (`entities` = every entity of the region including its texts and title, split into `geometry_entities` and
  `text_entities`; `features`; `registration` with the reference, `shift_m`, residual 0, no method: the reader's choice),
  `stray[]`, `levels[]`, `variants[]`, `conflicts` []. `title.box` is the usual estimate (0.8 × height per character).
- `heights_truth.json`: `cut_axis`, `cut_at`, `flipped`, `datum`, per base level `floor_z` (−3, 0, 3), `ceiling_height`
  (2.80, 2.80; the attic has no flat part: 3.80083 = the underside at the ridge above the attic floor), `floor_to_floor`
  3.00 / 3.00 / null, `level_mark` and `level_mark_target_z` (equal), `slabs` (z_top, thickness 0.20), `ground` (south, north,
  east: 0.00), `roof` (`eaves_z` 3.95509 and `ridge_z` 7.106024 = the top line at the outline edge and at the ridge,
  `eaves_underside_z`, `ridge_underside_z`, pitch 35, `knee_wall` 1.00, `overhang` 0.50, `thickness` 0.25, `profile`) and the
  entity of every line.
- `exterior_truth.json`: roof gable (source section, also the elevation and the plan's roof lines), outline, ridge line, no
  break line, covering `clay_tiles` (label `KİREMİT`), the terrace opening (room `r_L1_teras`, parapet walls `w_L1_001`,
  `w_L1_002`); `facade` (south stone plinth from the hatch + label, render from the label `SIVA` on both elevations);
  `openings_seen` per facade with `positions_m` (kind, `x` = centre from the facade's left end seen from outside, `x_left`,
  width, sill and head in building z, the plan opening id and level): south 2 windows + 1 door, east 2 windows; the site (plot,
  plot walls, parking, trees, road, labels, all in building metres), `north` 0.0 and the `brief` words.
- `building.json`: the usual building truth of the plan levels, schema-valid: levels L-1, L-1b, L0, L1 with the M10 fields
  (kind, variant, `region_id`, `elevation_source` section, floor to floor with evidence), 24 walls (evidence = the face lines of
  that wall), 34 openings (`operation` on doors: swing, `sliding` ×2 = one per basement plan, `double` ×1; `operation_source`
  `geometry`; `height` and `sill_height` only for the openings an elevation draws, otherwise null), 11 rooms (area lines match
  the polygons; `same_as` on the alternative's Hol), 18 furniture pieces (the stair has no front), one page record per region
  that is read (`region_id`, `region_box`, `region_class`), the two variants (`rooms_changed` = the open room, `exterior_changed`
  false). Roof, slabs, facade and site of the building JSON are not part of this file: the pipeline derives them, `heights_truth`
  and `exterior_truth` hold their truth.
- Evidence entity strings (`LWPOLYLINE:3F`) are the DXF handles of `sheet.dxf`; the DWG has other handles.

### Expected readings

| Stage | What the reader must find |
|---|---|
| split | 10 regions and 1 stray; boxes within 0.01 cm of the table (an independent clustering reproduces them for every gap from 0.5 % to 3 % of the frame's diagonal, 62 to 370 cm: `tests/test_synthetic.py`); the frame is not a region |
| classify | classes by title; `r2` alternative of `r1` (same level, extra bracket); the title block by geometry; no AI needed |
| units | `$INSUNITS` 5 agrees with every check: `metres_per_unit` 0.01, no `unit_mismatch` |
| register | shifts as in the table (± 1 cm), residual 0, stairs aligned (the `MERDIVEN` sits at the same place on all four plans) |
| heights | slab tops −3.00 / 0.00 / 3.00, 0.20 thick, floor to floor 3.00, ceilings 2.80, marks equal the geometry (no `level_mark_mismatch`), ground 0.00, pitch 35°, eaves 3.95509, ridge 7.10602, knee wall 1.00, overhang 0.50, roof 0.25 thick |
| exterior | roof gable, facade materials (stone plinth on the south, render), the openings per facade at the positions in `exterior_truth.json` (they match the plans' openings: `elevation_opening_mismatch` must stay empty), site plan, north 0° |
| plans (A3) | walls from the face lines (no wall word in the layer name), the columns join the wall mask, doors with their `operation`, windows, 11 rooms, 18 pieces typed by block name |

Simplifications, on purpose: the roof terrace is on the attic plan only (the elevations draw the roof envelope and the
south facade carries the plinth, the east one does not); no DIMENSION entities and no flat ceiling part under the roof (the
unit evidence is area labels, level marks, door arcs, wall thicknesses and text heights); the basement is below the ground
line on every side (ground 0.00; its outside door and windows get terrain and light wells from the build, both assumed).

## Coordinate conventions

| Frame | Units | Origin | Axes | Where |
|---|---|---|---|---|
| Building | metres | outer corner of the outer wall of L0 | X right, Y up, rotation CCW in degrees | `truth/building.json`, all `wenart.synthetic.model` data |
| DXF model space | millimetres (`$INSUNITS = 4`) | same as building | same | `*.dxf`; `building_to_page = [1000, 0, 0, 0, 1000, 0]` |
| PDF page | points, A3 landscape 1190.55 × 841.89 | bottom-left | Y up | `*.pdf`; 1 m = 28.3465 pt (1:100); the plan is centred, offset `(x0, y0)` is in the page transform |
| Raster | pixels, 2481 × 1754 at 150 dpi | top-left | Y down | `*_scan.png`, `*_photo.jpg` |

Transforms are stored per page in `truth/pages.json` as
`transform: {kind: "affine" | "homography", building_to_page: [...]}`. An affine
is six numbers `[a, b, c, d, e, f]` meaning `x' = a·x + b·y + c`,
`y' = d·x + e·y + f` (same layout as `transform_to_building` in the schema, which
holds the inverse). A homography is nine numbers row-major. Raster pages also
carry `H_building_to_pixels` as a 3×3 nested list. Helpers:
`wenart.geometry.apply_transform`, `transform_box`, `invert_affine`, `invert_homography`.

Scan = PDF page rasterised with `pdftoppm -r 150 -gray`, rotated by a seeded angle
in ±1.5°, Gaussian noise (σ = 4), slight blur (σ = 0.7). Photo = the scan warped by a
perspective transform (corners moved inward by up to 6 %), grey background outside
the paper, a brightness gradient, JPEG quality 80. Pixel boxes in the truth are the
axis-aligned boxes of the transformed corners; `tests/test_synthetic.py` checks that
every box sits on ink.

## Drawing conventions (what the extractors must read)

- Walls: closed 4-corner `LWPOLYLINE` on layer `DUVAR` (DXF) / closed path with
  line width 0.5 pt (PDF). Long axis = centre line, short side = thickness. Outer
  walls run corner to corner (they overlap at the corners); inner walls run face to
  face. `wenart.geometry.rectangle_to_centerline` does the conversion.
- Openings: block inserts `KAPI_80/90` on `KAPI`, `PENCERE_60/120/180` on `PENCERE`;
  the insert point is the opening centre on the wall centre line, the rotation is the
  wall direction, or the wall direction + 180° when the door swings to the other side.
  Door block: hinge at local (−w/2, 0), leaf line to (−w/2, w), swing arc of radius w
  from 0° to 90° around the hinge, so the door opens towards local +Y. Window block:
  two parallel lines 0.10 m apart plus the two end lines. In the PDF the same geometry
  is drawn with 0.35 pt lines (the door arc is the only curve on a page).
- Furniture: block inserts on `MOBILYA`; block names, types and sizes are in
  `wenart/synthetic/blocks.py: BLOCKS` (the only copy). Block local frame: rectangle
  centred at the origin, `size = [width (X), depth (Y)]`, front = −Y, so
  `front_deg = (270 + rotation) mod 360`. Each block draws its rectangle plus a short
  line parallel to the front edge (inset up to 50 mm). `BLOK_A` (1.2 × 0.5 m) has no known
  type: the truth lists it as `type: unknown`, `status: unverified`.
- Texts on `YAZI`: level title (`ZEMİN KAT PLANI`, `1. KAT PLANI`, `BODRUM KAT PLANI`,
  and `ZEMİN KAT MOBİLYA PLANI` for the furniture plan), `ÖLÇEK 1/100` to the right of
  the title, one room label per room inside the room (left baseline = insertion
  point). DXF text heights: labels 200 mm, title 500 mm, scale 300 mm, dimensions
  200 mm. PDF: 8 pt labels, 10 pt title, 9 pt scale, 8 pt dimensions.
- Dimensions on `OLCU`: a chain along the bottom and the left outer wall (segments
  between wall centre lines) plus the overall length further out. DXF: `DIMENSION`
  entities created with ezdxf's `add_aligned_dim` (stored as linear dimensions
  rotated to the direction of the two definition points, `dimtype` 0; the measurement
  is the distance between `defpoint2` and `defpoint3`), dimstyle `WENART`
  (`dimlfac 0.001`, `dimdec 2`, `dimdsep ","`, `dimzin 0`), `text = "<>"` except the
  deliberate override `3,99`. `wenart.synthetic.dxf_writer.dimension_printed_text`
  returns what a viewer prints. PDF: line, two extension lines, two 45° ticks and the
  text `5,30` (rotated 90° for vertical chains).

## Truth files

`truth/building.json` is schema-valid (`wenart.building.validate`) and holds what the
pipeline should produce. Rules used by the generator:

- Elements get one evidence entry per page that shows them. DXF: `layer` +
  `entity` (`LWPOLYLINE:<handle>`, `INSERT:<handle>`, `TEXT:<handle>`,
  `DIMENSION:<handle>`). PDF: `page` + `entity` (`path:<n>` or `char:<n>`). Rasters:
  `pixel_box` (+ `dpi` for scans) with `method: raster` for walls, openings and furniture
  footprints (deterministic image processing, Milestone 7; it was `ai` before), `method: ai` for furniture
  types and `method: ocr` for texts. The scan's scale is `dimension_text` from OCR-read dimension texts (the
  PNGs carry no dpi, so the `ÖLÇEK 1/100` note alone cannot give metres per pixel). Rooms get a second entry
  `method: derived`, `entity: derived-from:<wall ids>`.
- IDs follow docs/milestone2.md: `L-1`, `L0`, `L1`; `w_L0_001`; `d_L0_001`;
  `win_L0_001`; `r_L0_salon`, `r_L0_yatak_odasi`, `r_L-1_kiler_2`; `f_L0_001`; `c_001`.
  Room slugs use the whole normalised label (`wenart.building.room_id`).
- Heights, sill heights and furniture heights are `null` (not drawn). Wall `height`
  is the assumed ceiling height. `created_utc` and `pipeline_commit` are constants.
- For synthetic-03's Zemin Kat the DXF is the master: elements present in both
  documents carry both evidence entries; the window missing from the PDF has DXF
  evidence only and conflict `c_003`.

`truth/pages.json`: one entry per drawn page, including the hidden
`truth/plan.pdf` of synthetic-02 (`"hidden": true`; it is not a project document):
`{file, page, class, kind, level_id, level_label_raw, units, size, dpi,
scale_metres_per_unit, transform, H_building_to_pixels (rasters), texts, symbols,
walls, dimensions}`. Boxes are `[x0, y0, x1, y1]` in page units. `texts` carry
`role` (`title`, `scale`, `room_label`, `dimension`) and `symbols` carry `id`,
`type` (furniture type, `door` or `window`), `block`, `rotation_deg` and the entity.

## Known deviations and caveats

- PDF font is DejaVu Sans (embedded, from matplotlib's data folder), not Helvetica:
  reportlab's built-in Helvetica cannot encode `İ`, `Ş`, `Ğ`. Sizes follow the spec.
- `path:<n>` counts path drawing operations in emission order (border = 0, then
  walls, openings, furniture, dimensions). pdfplumber does not expose stream order
  and splits a path into `rects`, `lines` and `curves`, so match PDF elements by
  geometry (every box is in `pages.json`) and treat the index as a label.
  `char:<n>` is verified against `page.chars` order in the tests.
- The photo page has no single scale (`scale: null`, `transform_to_building: null`
  in building.json); use `H_building_to_pixels` from pages.json.
- Scans are ~1.4 MB each (noise does not compress well); the whole set is ~3.8 MB
  (synthetic-04 and -05 together ~0.5 MB, most of it the 78 KB style photo and the DXFs).
- real01 raster fixtures (Milestone 7 §4.4): `tests/fixtures/real01_raster/{real01-scan,real01-photo}/` are
  one-page projects made from the user's `projects/real01/real01.pdf` with
  `python -m wenart.synthetic.raster fixtures --pdf projects/real01/real01.pdf --page 1 --out
  tests/fixtures/real01_raster --name real01` (seeds 7101 scan, 7102 photo); `truth/raster.json` holds the
  PDF-points-to-pixels transform used to compare against the vector result.
- Previews: `results/synthetic/<project>_<file stem>_p<page>.jpg`, ≤ 1200 px wide,
  ≤ 300 KB (14 files for the six projects; synthetic-06's is rendered from its source DXF). The DXF previews are rendered from the
  written file with ezdxf's matplotlib backend. The names derive from the file stem,
  so two documents of one project need different stems: synthetic-04's PDF is
  `3_kat_plani_pdf.pdf` next to `3_kat_plani.dxf`.
- pdfplumber lists a straight-sided closed path that is not an axis-aligned
  rectangle under `curves` too: on synthetic-04's PDF page the 45° armchair is such
  a "curve"; the door arcs are the only paths with Bézier segments.
- Prototype record (2 Oct 2026, session scratch): synthetic-04/05 were prototyped
  end to end on CPU (ingest 0 problems against the truth, fit, decor, the AI-layout
  placer on the L-shaped Hol, a Blender CPU build of synthetic-04). Issues found
  there are fixed in Milestone 6 outside this generator (wall-face materials per
  room span, the windowless-room light position, searched cameras).
