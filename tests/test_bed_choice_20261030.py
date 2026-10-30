"""UL176 (30 Oct 2026, real04 run 20261030-112241-full, cam_r_L0_yatak_odasi_3_3): "I did not like this bed". The bed
f_L0_021 was the "Komfi Adjustable Bed" (hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e): a motorised care bed with a
sectioned glossy black and chrome base in two flat materials; its top is not one surface, so the throw over our duvet
tore on it and the bed showed a bare white duvet. The same bed was the user's "I did not like this bed" of 28 Oct
(UL73). A care, hospital or motion bed is a product for another use: never a home's bed (``fit.use_misfit``, a gate).
Pure tests; real04 is only the test case."""
from __future__ import annotations

from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from test_furniture_fit_v2 import FakeCatalog, model, piece

KOMFI = "hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e"


def test_a_care_or_motion_bed_is_a_product_for_another_use():
    for title in ("Komfi Adjustable Bed", "Hospital Bed with Side Rails", "Motorized Massage Bed Base",
                  "Electric Bed Frame, Queen", "Nursing Care Bed 90x200"):
        for ftype in ("bed_double", "bed_single"):
            e = model("care", ftype, 1.6, 2.1, 0.9, title=title)
            assert "another use" in (F.use_misfit(e, ftype) or ""), (title, ftype)
    # the real catalogue's home beds whose titles name a lift, storage, drawers or a light stay candidates
    for title in ("Amazon Brand - Solimo Vega Engineered Wood Hydraulic Half Lift-on Queen Bed (Espresso Finish)",
                  "Amazon Brand - Movian Constance Lift-Up Double Bed Frame with Storage",
                  "Corium LED Polsterbett", "Airsprung Boston Bed Black King - 4 Drawers",
                  "Taylor Full Slat Panel Bed, White"):
        assert F.use_misfit(model("home", "bed_double", 1.6, 2.1, 0.9, title=title), "bed_double") is None, title
    # the words are a bed's: an adjustable standing desk or an adjustable floor lamp is no misfit
    assert F.use_misfit(model("desk", "desk", 1.4, 0.7, 0.75, title="Adjustable Standing Desk"), "desk") is None


def test_the_fit_never_takes_the_care_bed_even_when_it_fits_best():
    care = model("komfi", "bed_double", 1.55, 2.07, 0.93, title="Komfi Adjustable Bed", quality=5.0)
    home = model("home", "bed_double", 1.6, 2.0, 1.0, title="Oak Platform Bed", quality=3.0)
    p = piece("bed_double", 1.55, 2.0)
    asset = F.fit_piece(p, FakeCatalog([care, home]))
    assert asset["method"] == "library" and asset["asset_id"] == "abo_home"
    (ex,) = [x for x in asset["excluded"] if x["id"] == "abo_komfi"]
    assert ex["rule"] == F.USE_RULE and "adjustable" in ex["reason"]
    alone = F.fit_piece(p, FakeCatalog([care]))
    assert alone.get("asset_id") != "abo_komfi"                      # never the care bed, even alone
    pinned = F.fit_piece(dict(p, asset_pin="abo_komfi"), FakeCatalog([care, home]))
    assert pinned.get("asset_id") == "abo_home"                      # nor when the agent pins it


def test_the_real04_bed_leaves_the_catalogue_choice_and_the_rule_is_precise():
    cat = C.load()
    beds = [e for e in cat.entries if isinstance(e, dict) and e.get("type") in C.BED_TYPES]
    komfi = next(e for e in beds if e.get("id") == KOMFI)
    assert "adjustable" in F.use_misfit(komfi, "bed_double")
    hit = [e["id"] for e in beds if F._named(" ".join(str(e.get(k) or "") for k in ("title", "name")).lower(),
                                             F.CARE_BED_WORDS)]
    assert KOMFI in hit and len(hit) <= 3                            # the care words name care beds, not home beds
