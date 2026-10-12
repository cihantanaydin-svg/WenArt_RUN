# Milestone 13 prompt – realistic furniture, real vegetation, a new way to place furniture

For a new Claude Code session (Fable) on a NEW branch made from `opus_branch_06` (last commit of the M12 session:
`eddde01` or later). Written on 12 Oct 2026 by the M12 session from its findings.

---

Read `CLAUDE.md` first, then `docs/plan.md`, `docs/progress.md`, `docs/milestone12.md` (§1 diagnosis, §4 furniture
design, §6 library, §14 build log and pod results, §14.7 open items, §14.8 real04) and `docs/gpu-log.md`. Tell me
where you run (cloud or Mac) before anything else. Work only on your own new branch; never push to
`opus_branch_06`. Today's date: <fill in>.

## Why this milestone

The pipeline works end to end: it reads whole buildings from DWG/PDF (levels, slabs, roof, ground slope from level
marks, several buildings on one plot), furnishes every room, runs an AI agent that fixes findings, and renders
photoreal views in Cycles. But **the furniture and the outdoor models look bad, and the furniture placement is not
good.** Nobody would show these images to a client. Milestone 12 tried to fix this inside the current approach
(library audit, library growth, a group solver, an agent with group tools). It improved the numbers but not the
look. **I want you to step back and re-think the problem**, not to tune the current pieces.

I am open to a library or a tool we have not used before, and I am open to relaxing the "commercial use only"
licence rule for this proof of concept (see "Licences" below). Quality comes first now.

## What we know (evidence from Milestone 12; check it yourself)

**The library looks bad.** Usable models today: 750 furniture (ABO 444, generated with TRELLIS.2 182,
Poly Haven 61, Objaverse 58, 5 others) and 576 decor (ABO 283, Objaverse 115, generated 94, Poly Haven 48, GSO 36), over 42
furniture types; some types have 1-10 models (bathtub 8, shower 10, toilet 14, crib 7). ABO are e-commerce scans
(Amazon product models) have simple materials; Objaverse uploads vary wildly; the generated models are blobby. The audit (pods P2/P3/P4,
`results/library/audit/`) removed 126 + 38 models and kept 121 + 48 "with a vision doubt"; among all kept models, 48 have a
vision check that names another type (e.g. Poly Haven `chinese_armchair` typed `office_chair`).
On real04 (pod `jeqodk9uyn9o6p`, `results/final/real04/`): of 289 pieces, 131 got a library model, 115 a
parametric one (kitchen and bath fixtures), **43 were not built at all** because no audited model fits their size
(12 chairs, 8 dining tables, 4 double beds, 4 wardrobes, 4 coffee tables, 4 floor lamps, 2 sofas, the drawn
4.38 m corner sofa ...). The run counted 465 "library gap" findings over its rounds. Sofas, beds and tables never fall back
to a generated parametric model (M12 §4.8), so a living room can end up without its sofa and dining table.

**Outdoor models look bad.** Trees and bushes are parametric "lollipops" (a cylinder trunk and an ellipsoid crown,
`wenart/blender/site.py` `tree_parts`); real04's drawn hedge is 101 such trees in a row. Grass, paving and plot
walls are flat textured surfaces; there is no shrub, ground cover, planter, fence detail or pool coping. See
`results/final/real04/ext_*_final_preview.jpg`.

**Placement is not good.** Facts from the real02/real03/real04 runs:
- Pieces float in the room or stand where no person would put them. real04 findings over the agent rounds, by check: F8 "piece
  neither against a wall nor in a group" 266, S2 "piece cuts a wall or another piece" 132, G10 bathroom layout and
  clearances 126, F9 "odd in the image" 105, R3 door swing blocked 70, F3 61, G12 window blocked 48.
- The agent: real04 6 rounds, 182 edits accepted / 170 rejected; the findings stop improving after round 2
  (critical 7 → 2 → 2 → 3 → 33 → 5, major ~150-160). Many tools rarely pass (accepted of tried): complete_group 0 of 18, fix_fixture 0 of 19,
  rotate_piece 6 of 21, set_camera 1 of 11; rejections: drawn_lock 41, memory 31, max_tries 27.
- The M12 bake-off (`results/bakeoff_m12/`, docs/milestone12.md §14.1): **no open model judges a layout from a
  top-down image**: picking the best of 3 layouts is at chance (35 %), finding planted errors 11-27 % with many false
  reports. The models are useful only for reading plan crops and checking renders.
- The deterministic group solver (`wenart/furniture/solver.py`, templates in `groups.yaml`) often finds no place in
  small or crowded rooms (a washbasin in a full 1.6 x 2.5 m bathroom, nightstands beside a bed in a 9 m² room).
- Drawn furniture must stay where it is drawn (CLAUDE.md), so a bad drawn reading or a bad model size spreads into
  the layout.

The current code: the fit (`wenart/furniture/fit.py`, `catalog.py`, catalogues `catalog.json` /
`catalog_library.json`), layout (`layout.py`, `program.py`, `solver.py`, `placer.py`, `groups.py`,
`group_checks.py`), the agent (`wenart/agent/`), decor (`wenart/blender/rest.py`, `textiles.py`), the scene build
(`wenart/blender/furniture.py`, `site.py`), the library audit and growth (`wenart/assets/audit/`).

## What I want

1. **Furniture that looks like real, good products** in every rendered room, in the project's style, with real
   materials (fabric, wood, metal, glass) and real sizes. A complete set per room type: no missing sofa, bed, table
   or chairs because no model fits.
2. **Outdoor that looks real**: real trees, shrubs, hedges, ground cover and planting; good paving, grass, walls,
   fences, pool edges. A drawn hedge is a hedge, a drawn tree is a tree of a plausible species and size.
3. **Placement a designer would accept**: rooms furnished the way interior designers furnish them (functional
   groups, circulation, focal points, rugs under groups, nothing floating, nothing cutting walls or blocking doors
   and windows), drawn pieces respected as CLAUDE.md says.
4. A clear, measurable before/after on real02, real03 and real04 (same views).

## How to work

**Step 0: diagnosis (CPU only, no pod, no code change).** Look at the committed renders (`results/final/real0*/`)
and the logs, and name the root causes: model quality, model choice (fit), sizes, materials, lighting of the
models, placement logic, the agent loop. Rank them by how much they hurt the images. Use numbers.

**Step 1: research and design (no code yet).** Search widely and check every claim against the official source
(licence text, download terms, model counts, formats, quality); never trust this list:
- furniture and decor libraries we have not used: for example 3D-FUTURE (Alibaba; real furniture products with
  textures, research licence), the Habitat Synthetic Scenes Dataset objects (HSSD, a CC BY-NC licence),
  BlenderKit (its own licences; check API and automation terms), Sketchfab CC models (incl. NC), Objaverse++ quality
  labels, IKEA-like product models (check terms), Poly Haven and ambientCG (CC0) for more models and materials;
- procedural or generative options: Infinigen Indoors furniture and Infinigen nature (trees, bushes, ground cover;
  check which parts are BSD and which GPL), Blender's bundled tree generator, better image-to-3D (TRELLIS.2 is MIT and
  in use; Hunyuan3D 2.x excludes the EU/UK/South Korea; SAM 3D Objects);
- placement: how good systems and designers do it (rule-based interior design constraints, data-driven priors from
  professional layouts such as 3D-FRONT (research licence), Holodeck / LayoutVLM-style "AI proposes, code
  verifies", Infinigen Indoors' constraint solver), and how to give the AI a view it can actually judge (rendered
  perspective views instead of top-down images, or no visual judgement at all where code decides better).
Then propose 2-3 complete approaches (library + vegetation + placement), each with: expected image quality (show
examples), licence and commercial impact, effort, risks, GPU cost, and what changes in `CLAUDE.md`. Put a
comparison table and your recommendation in `docs/milestone13.md`, and **wait for my OK** before building.

**Step 2: build** what I approve, with tests, on your branch; then pods for the downloads, the audit of the new
assets and full runs of real02, real03 and real04 (batch them; polish off unless asked). Show me side-by-side
before/after images of the same views and the numbers.

## Licences (my position, 12 Oct 2026)

For this proof of concept I am willing to relax the "commercial use only" rule (CLAUDE.md library rules and
`docs/plan.md` licence flags). Show me in Step 1 what each option gains in quality and what it costs in licence
terms (non-commercial, share-alike, no-derivatives, research-only, attribution, regional exclusions). If I approve a
relaxed option: every asset keeps its licence in the catalogue, every render's `ATTRIBUTION.md` lists the
non-commercial assets in it, the report shows a "commercial-safe: yes/no" line per render, and the catalogue can be
switched back to commercial-safe assets with one setting. Do not adopt any non-commercial or share-alike asset
before my explicit OK, and then update `CLAUDE.md` with the wording I approve.

## Rules that stay

Everything else in `CLAUDE.md` stays: drawn fixed equipment and drawn furniture rules, evidence and logging,
nothing deleted from the network volume without my OK, GPU limits ($5.00 per GPU-hour, $30 per day, 4 hours per pod
run, one pod at a time; ask before any action over $5 or going over a limit), pods shut themselves down, every pod
logged in `docs/gpu-log.md`, GPU tests before calling the milestone done, commit and push after every step, simple
English, short reports, tables. The project GPU total is $130.54 of $200; tell me early if this milestone needs more.

## Environment notes

- Network volume `wenart` (EU-RO-1) was grown to 400 GB and cleaned on 12 Oct 2026 (about 120 GB used: assets 24
  GB, library build work 36 GB, caches, tools; only the real04 outputs are kept). Keep new downloads on the volume
  under `/workspace/assets` or a new folder you document; model caches stay on the container disk (CLAUDE.md).
- Run pods only through `scripts/gpu_run.py` (`--max-minutes` up to 240; `AGENT_ROUNDS` for the full job).
- real04 (`projects/real04/deneme1.dwg`) is the real02 twin villa with its site: two blocks (4 villas) on a sloping
  plot with pools. It is the best test of the outdoor work.
- Known open items you may meet (docs/milestone12.md §14.7): the after-P8 fixes and the real04 changes have had no
  GPU test run yet (the real04 run stopped on the full volume before its tests); a basement living room got only a
  high strip window by default (window heights are assumed when not drawn).
