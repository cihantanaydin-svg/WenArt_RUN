#!/usr/bin/env bash
# Read-only diagnostic (3 Nov 2026): the glTF JSON (materials, textures, images, samplers, extensions) and the first
# bytes of every embedded image of the library GLBs named in GLB_IDS (source/uid pairs: "syncronia/<uid>,..."),
# written to $WENART_RESULTS/glb_dump/<uid>.json. Nothing is changed.
#   scripts/gpu_run.py run --job scripts/jobs/glb_dump.sh --max-minutes 15 --env GLB_IDS=syncronia/syncronia_x
set -Eeuo pipefail
trap 'echo "[glb_dump] ERROR at line $LINENO" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
PY="${WENART_PY:-$WS/venv/bin/python}"
mkdir -p "$RESULTS/glb_dump"
"$PY" - "$WS/assets" "$RESULTS/glb_dump" "${GLB_IDS:?GLB_IDS is required}" <<'PYEOF'
import io, json, sys
from pathlib import Path
from wenart.assets import warehouse as WH
assets, out, ids = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
for item in ids:
    src, uid = item.split("/", 1)
    p = assets / "models" / src / f"{uid}.glb"
    rec = {"path": str(p), "exists": p.is_file()}
    if p.is_file():
        doc, binary = WH.read_glb(p)
        rec.update({k: doc.get(k) for k in ("materials", "textures", "images", "samplers", "extensionsUsed",
                                             "extensionsRequired", "asset")})
        heads = []
        for img in doc.get("images") or []:
            bv = img.get("bufferView")
            if isinstance(bv, int):
                v = doc["bufferViews"][bv]
                data = binary[int(v.get("byteOffset", 0)):int(v.get("byteOffset", 0)) + int(v["byteLength"])]
                info = {"bytes": len(data), "head": data[:12].hex()}
                try:
                    from PIL import Image
                    im = Image.open(io.BytesIO(data)); info.update(format=im.format, mode=im.mode, size=im.size)
                except Exception as exc:  # noqa: BLE001
                    info["pil_error"] = str(exc)
                heads.append(info)
            else:
                heads.append({"uri": img.get("uri")})
        rec["image_data"] = heads
    (out / f"{uid}.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    print("[glb_dump]", uid, rec["exists"])
PYEOF
