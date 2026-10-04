"""CC0 PBR textures and HDRIs with a licence manifest (Milestone 3 section 2).

``fetch_texture`` / ``fetch_hdri`` download one asset from Poly Haven or
ambientCG into the assets folder and record it in ``manifest.json``;
``fetch_for_style`` fetches everything a ``style.json`` needs;
``verify_vocabulary`` lists without downloading. Textures and HDRIs are
CC0 only; furniture models (``wenart.assets.models``) are Poly Haven CC0 or,
from Milestone 7, Objaverse CC0 / CC BY 4.0 with a full credit line, read
only from the prep pod's cache (``check_licence(..., kind, entry)``).
CLI: ``python -m wenart.assets fetch --style style.json --assets assets``.
"""
from wenart.assets.fetch import (LICENCE, LICENCES, AssetNotFound, LicenceError, check_licence,  # noqa: F401
                                 fetch_for_style, fetch_hdri, fetch_texture, load_manifest, manifest_path,
                                 save_manifest, verify_vocabulary)
