#!/usr/bin/env bash
# Read-only check (3 Nov 2026, the user: "From all the furnitures in the library how many of them is a set texture and
# the texture files exist?"): every furniture model of the catalogues (library entries and Poly Haven) with its file on
# the volume: the file there and its sha256 as catalogued, the textures its materials use, each one present (embedded
# in the GLB, or the Poly Haven glTF's JPG beside it) and readable, and not a 1-2 px placeholder. Writes
# $WENART_RESULTS/texture_check.json (per model and the totals). Nothing is changed.
#   scripts/gpu_run.py run --job scripts/jobs/library_texture_check.sh --max-minutes 20
set -Eeuo pipefail
trap 'echo "[texture_check] ERROR at line $LINENO" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
PY="${WENART_PY:-$WS/venv/bin/python}"
mkdir -p "$RESULTS"
"$PY" - "$WS/assets" "$RESULTS/texture_check.json" <<'PYEOF'
import hashlib, io, json, sys, urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
from wenart.furniture import catalog as C
from wenart.assets import warehouse as WH
assets, out = Path(sys.argv[1]), Path(sys.argv[2])
cat = C.load()
rows = [e for e in cat.entries if isinstance(e, dict) and not e.get("parametric") and (e.get("glb") or e.get("gltf"))]

def used_textures(doc):
    idx = set()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k.endswith("Texture") and isinstance(v, dict) and isinstance(v.get("index"), int):
                    idx.add(v["index"])
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(doc.get("materials") or [])
    return {(doc.get("textures") or [])[i].get("source") for i in idx if i < len(doc.get("textures") or [])} - {None}

def check(e):
    r = {"id": e["id"], "source": e.get("source"), "type": e.get("type"), "usable": C.usable(e, "relaxed")}
    rel = e.get("glb") or e.get("gltf")
    p = assets / rel
    if not p.is_file():
        r["status"] = "file missing"; return r
    want = e.get("sha256_glb") or e.get("sha256_gltf")
    if want and hashlib.sha256(p.read_bytes()).hexdigest() != want:
        r["sha_mismatch"] = True
    try:
        if p.suffix == ".glb":
            doc, binary = WH.read_glb(p)
        else:
            doc, binary = json.loads(p.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        r["status"] = f"unreadable: {exc}"; return r
    imgs = doc.get("images") or []
    used = sorted(used_textures(doc))
    r["images"], r["used"] = len(imgs), len(used)
    ok = bad = placeholder = missing = 0
    for i in used:
        img = imgs[i] if i < len(imgs) else {}
        data = None
        if isinstance(img.get("bufferView"), int) and binary is not None:
            v = doc["bufferViews"][img["bufferView"]]
            data = binary[int(v.get("byteOffset", 0)):int(v.get("byteOffset", 0)) + int(v["byteLength"])]
        elif img.get("uri") and not str(img["uri"]).startswith("data:"):
            f = p.parent / urllib.parse.unquote(img["uri"])
            data = f.read_bytes() if f.is_file() else None
        if data is None:
            missing += 1; continue
        try:
            im = Image.open(io.BytesIO(data)); im.load()
            if max(im.size) <= 2: placeholder += 1
            else: ok += 1
        except Exception:  # noqa: BLE001
            bad += 1
    r.update(ok=ok, unreadable=bad, placeholder=placeholder, missing=missing)
    if not used: r["status"] = "untextured"
    elif ok == len(used): r["status"] = "textured, all files there"
    elif ok: r["status"] = "textured, some files missing or broken"
    else: r["status"] = "textured, no usable file"
    return r

with ThreadPoolExecutor(16) as pool:
    res = list(pool.map(check, rows))
tot = {}
for r in res:
    key = ("usable" if r["usable"] else "not usable", r["status"])
    tot[" | ".join(key)] = tot.get(" | ".join(key), 0) + 1
by_source = {}
for r in res:
    if r["usable"]:
        d = by_source.setdefault(r["source"], {})
        d[r["status"]] = d.get(r["status"], 0) + 1
out.write_text(json.dumps({"totals": tot, "usable_by_source": by_source, "models": res}, indent=1), encoding="utf-8")
print(json.dumps({"totals": tot, "usable_by_source": by_source}, indent=1))
PYEOF
