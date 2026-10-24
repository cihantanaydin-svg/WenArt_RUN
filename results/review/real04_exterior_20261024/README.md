# real04 exterior upgrade (24 Oct 2026)

User request of 24 Oct 2026: "real04 outside renders are not that good, first start giving some material to the
outside walls, they seem blank concrete, then there is a bulge in bodrum kat looks like a balcony there should not
be there, after that start using outside doors, start using the new library items for the outside items, plants cars
etc, there are new windows you can try to use, rain gutters you can include, roof not looking good may require a
rework. [...] fixes needs to work for every project".

Pod `x884zdj3506zo3` (RTX PRO 6000, EU-RO-1, $2.49/h), job `20261024-083434-full`, code a7e0084, 110 min, $4.55:
`scripts/jobs/full.sh`, `RUN_PROJECTS=real04`, `RUN_POLISH=off`, `RENDER_SAMPLES=256`, 3 agent rounds, GPU tests
47 passed, 9 skipped, 0 failed.

| Remark | Change (general, every project) | Seen in this run |
|---|---|---|
| walls look like blank concrete | facade scheme per style family when nothing names the facade (`facade.FACADE_SCHEMES`): render colour, basement cladding, wood accent at the main entrance | off-white render, stone basement band (ext_1, ext_2, ext_5, ext_7) |
| bulge in the bodrum kat | an inferred terrace guard was one steel slab: now glass panels with posts | gone (ext_1, ext_3) |
| outside doors, new windows | library doors and windows on the outer openings, one model per category (`opening_models`, `opening_build`) | 34 library opening objects; ribbon windows in panels (ext_1, ext_2, interior salon views) |
| plants, cars | library trees / palms / bushes per species (`site_models.plant_model`), cars on the drawn parkings | 21 shrubs from the library, 1 car on the driveway (ext_7) |
| rain gutters | an outlet from each gutter to its downpipe on the wall | visible at the eaves corners |
| roof | the drawn roof is kept over the agent's override (it had raised real04's mansard to 45 degrees, 1.35 m too high); fascia board; ridge and hip caps | lower drawn roof; anthracite fascia; ridge caps in the aerial views |
| (seen on the way) yellow walls under the eaves | the lawn's bounced light is 75 % grey | gone |

Open point: the 21 shrubs use the library model `3dwh_d33c77b1f7` ("Small bush or hedge 3D"), whose leaf texture has a
transparent background exported as opaque: they rendered white. Fixed after this run (`vegetation.fix_plant_materials`:
the texture's alpha drives the leaf cards; plain white leaf materials take the species colour), checked in Blender on a
test model; the next pod run shows it.

ext_4 is dropped again (as in Milestone 13): with the drawn, lower roof the trees and the plot wall hide half the
building from that corner.

## Files

| File | What |
|---|---|
| `sheets13/` | one before / after JPEG per view: before = Milestone 13 (`results/baseline/m13/`), after = this run |
| `metrics13.md`, `metrics13.json` | the 17 metrics of `docs/milestone13.md` §7, before = Milestone 13, after = this run |
| `gpu_check_values.json` | the GPU tests' measured values |
