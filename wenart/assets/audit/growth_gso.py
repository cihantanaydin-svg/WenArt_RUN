"""Google Scanned Objects (GSO) small decor for pod P4 (docs/milestone12.md §6.4 D24, user OK of 11 Oct 2026 with a
condition: only objects whose CC BY 4.0 licence is confirmed on the pod; the others are dropped and listed).

What:

- ``safe_extract(zip, dest)``: the object archive of the Hugging Face mirror ``suvadityamuk/google-scanned-objects-raw``
  unpacked without leaving ``dest`` (no absolute paths, no ``..``, no links) and within a size and file cap.
- ``layout(folder)``: the files of an object (``meshes/model.obj`` + ``.mtl``, ``materials/textures/texture.png``,
  ``model.config``, ``metadata.pbtxt``, ``model.sdf`` and any licence / readme file) wherever the archive put them.
- Licence evidence per object (``licence_records``), two independent sources, both recorded:
  1. the archive's own text files (a licence file, ``model.config``, ``metadata.pbtxt``, a readme): a CC BY 4.0
     statement (the licence URL ``creativecommons.org/licenses/by/4.0``, "CC BY 4.0", "Creative Commons
     Attribution 4.0");
  2. the object's record on Gazebo Fuel, where Google Research published the dataset
     (``https://fuel.gazebosim.org/1.0/GoogleResearch/models/<name>``): its ``license_name`` / ``license_url``.
  Kept: one source confirms CC BY 4.0 and no source names another licence (NC, SA, ND or a different one). Dropped:
  everything else, with the reason. The endpoint (``GET <server>/1.0/<owner>/models/<name>``) and the record's
  fields (``name``, ``owner``, ``license_name``, ``license_url``, ``license_image``) were read in gz-fuel-tools
  (``src/FuelClient.cc`` ``ModelDetails``, ``src/JSONParser.cc`` ``ParseModel``, branch main, 11 Oct 2026); the
  records of Google Research's objects could not be fetched from the build session (proxy), so the parser reads
  every key with "licen" in its name and needs the CC BY 4.0 URL or "Attribution" with "4.0"; anything else drops
  the object (never kept on a guess).
- ``convert_jobs``: the Blender jobs (``convert_blender.py``) that turn ``model.obj`` (Z up, metres: Gazebo SDF
  units) into ``models/gso/<uid>.glb``.

Why: the mirror carries no licence tag (B.md §6); the user's OK needs the CC BY 4.0 confirmed per object, with the
evidence kept (CLAUDE.md evidence rules) and the credit line of CC BY 4.0 §3(a)(1) in every entry.

How: pure functions on texts and records (CPU tests); ``fetch_fuel`` is the only network call (``urllib``, a
timeout, no token sent).
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable, Optional

FUEL_OWNER = "GoogleResearch"
FUEL_API = "https://fuel.gazebosim.org/1.0/{owner}/models/{name}"
FUEL_PAGE = "https://app.gazebosim.org/{owner}/fuel/models/{name}"
HF_REPO = "suvadityamuk/google-scanned-objects-raw"
HF_RESOLVE = "https://huggingface.co/datasets/{repo}/resolve/{rev}/{file}"
USER_AGENT = "wenart-run/0.1 (library growth, licence check)"
MAX_UNPACKED = 600 * 1024 * 1024        # bytes per archive (the 36 approved archives are 1-20 MB packed)
MAX_MEMBERS = 5000
MAX_TEXT = 1024 * 1024                  # text files read for licence evidence
UID_MAX = 64                            # wenart.assets.models._UID_RE
TEXT_SUFFIXES = (".txt", ".md", ".config", ".pbtxt", ".sdf", ".json", ".xml", ".rst", ".html")
TEXT_NAMES = ("license", "licence", "copying", "readme", "notice", "attribution")
CC_BY_4 = (re.compile(r"creativecommons\.org/licenses/by/4\.0", re.I),
           re.compile(r"\bCC[\s_-]*BY[\s_-]*4\.0\b", re.I),
           re.compile(r"Creative\s+Commons\s+Attribution\s+4\.0", re.I))
OTHER = (re.compile(r"creativecommons\.org/licenses/by-(nc|sa|nd)", re.I),
         re.compile(r"\bCC[\s_-]*BY[\s_-]*(NC|SA|ND)\b", re.I),
         re.compile(r"non[\s-]*commercial|share[\s-]*alike|no[\s-]*deriv", re.I),
         re.compile(r"creativecommons\.org/publicdomain", re.I),
         re.compile(r"all\s+rights\s+reserved", re.I))


RULE = ("kept when the archive's own files or the object's Gazebo Fuel record state CC BY 4.0 (the licence URL "
        "creativecommons.org/licenses/by/4.0, 'CC BY 4.0', 'Creative Commons Attribution 4.0', or a Fuel licence "
        "naming Attribution and 4.0) and no source names another licence; dropped otherwise")


class ArchiveError(ValueError):
    """An archive that would leave its folder, holds too much or is no zip."""


def gso_uid(name: str) -> str:
    """``gso_<name>`` (the approved id), shortened to 64 characters with a hash when longer (the library cache path
    ``models/gso/<uid>.glb`` takes ``[A-Za-z0-9_-]{1,64}``)."""
    clean = re.sub(r"[^A-Za-z0-9_-]", "_", name)
    uid = f"gso_{clean}"
    if len(uid) <= UID_MAX:
        return uid
    digest = hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]
    return f"gso_{clean[:UID_MAX - 4 - 9].rstrip('_')}_{digest}"


def name_of(approved_id: str) -> str:
    return approved_id[4:] if approved_id.startswith("gso_") else approved_id


# --------------------------------------------------------------------------
# Archive
# --------------------------------------------------------------------------

def safe_members(names_sizes: list[tuple[str, int, bool]]) -> list[str]:
    """The member names to extract (``(name, size, is_link)``); ``ArchiveError`` for a path that leaves the folder,
    a link, too many members or too many bytes."""
    if len(names_sizes) > MAX_MEMBERS:
        raise ArchiveError(f"{len(names_sizes)} members (> {MAX_MEMBERS})")
    total, out = 0, []
    for name, size, link in names_sizes:
        p = PurePosixPath(name.replace("\\", "/"))
        if p.is_absolute() or ".." in p.parts or re.match(r"^[A-Za-z]:", name):
            raise ArchiveError(f"member {name!r} leaves the folder")
        if link:
            raise ArchiveError(f"member {name!r} is a link")
        total += int(size)
        if total > MAX_UNPACKED:
            raise ArchiveError(f"more than {MAX_UNPACKED // 1048576} MB unpacked")
        if not name.endswith("/"):
            out.append(name)
    return out


def safe_extract(zip_path: Path, dest: Path) -> dict:
    """Unpack ``zip_path`` into ``dest`` (members checked by ``safe_members``); ``{"members", "bytes"}``."""
    dest = Path(dest)
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as exc:
        raise ArchiveError(f"not a zip archive: {exc}") from exc
    with zf:
        infos = zf.infolist()
        rows = [(i.filename, i.file_size, (i.external_attr >> 16) & 0o170000 == 0o120000) for i in infos]
        names = set(safe_members(rows))
        dest.mkdir(parents=True, exist_ok=True)
        root = dest.resolve()
        written = 0
        for info in infos:
            if info.filename not in names:
                continue
            target = (dest / info.filename).resolve()
            if root not in target.parents and target != root:
                raise ArchiveError(f"member {info.filename!r} leaves the folder")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > MAX_UNPACKED:
                        raise ArchiveError(f"more than {MAX_UNPACKED // 1048576} MB unpacked")
                    dst.write(chunk)
    return {"members": len(names), "bytes": written}


def layout(folder: Path) -> dict:
    """The object's files relative to ``folder``: ``obj`` (``meshes/model.obj`` first), ``mtl``, ``texture``,
    ``config``, ``metadata``, ``sdf`` and ``texts`` (every small text file, licence files first)."""
    folder = Path(folder)
    files = sorted(p for p in folder.rglob("*") if p.is_file())
    rel = [p.relative_to(folder).as_posix() for p in files]

    def first(pred):
        hits = [r for r in rel if pred(r)]
        hits.sort(key=lambda r: (r.count("/"), r))
        return hits[0] if hits else None
    objs = [r for r in rel if r.lower().endswith(".obj")]
    obj = next((r for r in objs if r.lower().endswith("meshes/model.obj")), None) or (sorted(objs)[0] if objs else None)
    texts = [r for r in rel if (r.lower().endswith(TEXT_SUFFIXES) or any(n in PurePosixPath(r).name.lower()
                                                                         for n in TEXT_NAMES))
             and (folder / r).stat().st_size <= MAX_TEXT]
    texts.sort(key=lambda r: (not any(n in PurePosixPath(r).name.lower() for n in TEXT_NAMES), r))
    return {"obj": obj, "mtl": first(lambda r: r.lower().endswith(".mtl")),
            "texture": first(lambda r: r.lower().endswith("texture.png"))
            or first(lambda r: r.lower().endswith((".png", ".jpg", ".jpeg")) and "thumbnail" not in r.lower()),
            "config": first(lambda r: PurePosixPath(r).name == "model.config"),
            "metadata": first(lambda r: PurePosixPath(r).name == "metadata.pbtxt"),
            "sdf": first(lambda r: PurePosixPath(r).name == "model.sdf"), "texts": texts, "files": len(rel)}


def config_fields(text: str) -> dict:
    """``name``, ``author``, ``email``, ``description`` and any licence element of a Gazebo ``model.config``."""
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return {}

    def find(path):
        el = root.find(path)
        return " ".join(el.text.split()) if el is not None and el.text else None
    out = {"name": find("name"), "author": find("author/name"), "email": find("author/email"),
           "description": find("description")}
    lic = [" ".join((el.text or "").split()) for el in root.iter() if "licen" in el.tag.lower()]
    if lic:
        out["licence"] = "; ".join(x for x in lic if x)
    return {k: v for k, v in out.items() if v}


# --------------------------------------------------------------------------
# Licence evidence
# --------------------------------------------------------------------------

def _scan(text: str) -> tuple[Optional[str], Optional[str]]:
    """``(cc_by_4 line, other licence line)`` of a text (the first matching line of each)."""
    yes = no = None
    for line in text.splitlines():
        s = " ".join(line.split())[:300]
        if yes is None and any(p.search(s) for p in CC_BY_4):
            yes = s
        if no is None and any(p.search(s) for p in OTHER):
            no = s
    return yes, no


def evidence_in_texts(texts: dict) -> tuple[Optional[dict], Optional[str]]:
    """``(evidence, refusal)`` from the archive's text files (``{relative path: text}``): evidence = the first file
    with a CC BY 4.0 statement; refusal = a file that names another licence."""
    ev = refusal = None
    for rel, text in texts.items():
        yes, no = _scan(text or "")
        if no and refusal is None:
            refusal = f"{rel} names another licence: {no!r}"
        if yes and ev is None:
            ev = {"method": "archive", "file": rel, "text": yes}
    return ev, refusal


def evidence_in_fuel(record: Optional[dict], url: str, name: str) -> tuple[Optional[dict], Optional[str]]:
    """``(evidence, refusal)`` from the object's Gazebo Fuel record (``None``: no record)."""
    if not isinstance(record, dict):
        return None, None
    fields = {k: v for k, v in record.items() if "licen" in str(k).lower() and isinstance(v, (str, int))}
    owner = str(record.get("owner") or "")
    rname = str(record.get("name") or "")
    if owner and owner.lower() != FUEL_OWNER.lower():
        return None, f"the Fuel record's owner is {owner!r}, not {FUEL_OWNER}"
    if rname and rname.lower() != name.lower():
        return None, f"the Fuel record names {rname!r}, not {name!r}"
    text = " ".join(str(v) for v in fields.values())
    if not fields:
        return None, None
    if any(p.search(text) for p in OTHER):
        return None, f"the Fuel record names another licence: {fields}"
    by4 = any(p.search(text) for p in CC_BY_4) or (re.search(r"attribution", text, re.I) and "4.0" in text)
    if by4:
        return {"method": "fuel_api", "url": url, "fields": fields, "owner": owner or None}, None
    return None, f"the Fuel record's licence is not CC BY 4.0: {fields}"


def decide(name: str, archive_ev: Optional[dict], archive_refusal: Optional[str], fuel_ev: Optional[dict],
           fuel_refusal: Optional[str], fuel_error: Optional[str]) -> dict:
    """``{"kept", "evidence": [...], "reason"}``: kept when a source confirms CC BY 4.0 and none names another."""
    evidence = [e for e in (archive_ev, fuel_ev) if e]
    refusals = [r for r in (archive_refusal, fuel_refusal) if r]
    if refusals:
        return {"kept": False, "evidence": evidence, "reason": "; ".join(refusals)}
    if evidence:
        how = " and ".join({"archive": "the archive's own files", "fuel_api": "the Gazebo Fuel record"}[e["method"]]
                           for e in evidence)
        return {"kept": True, "evidence": evidence, "reason": f"CC BY 4.0 confirmed by {how}"}
    why = "no CC BY 4.0 statement in the archive's files"
    why += f"; Gazebo Fuel: {fuel_error}" if fuel_error else "; the Gazebo Fuel record names no licence"
    return {"kept": False, "evidence": [], "reason": why}


def fuel_url(name: str) -> str:
    return FUEL_API.format(owner=FUEL_OWNER, name=urllib.request.quote(name, safe=""))


def fetch_fuel(name: str, timeout: float = 30.0, opener: Optional[Callable] = None) -> tuple[Optional[dict], str,
                                                                                            Optional[str]]:
    """``(record, url, error)`` of the object's Gazebo Fuel record (JSON); no token is sent."""
    url = fuel_url(name)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with (opener or urllib.request.urlopen)(req, timeout=timeout) as resp:
            data = resp.read(MAX_TEXT)
    except urllib.error.HTTPError as exc:
        return None, url, f"HTTP {exc.code}"
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, url, f"{type(exc).__name__}: {exc}"
    try:
        doc = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None, url, "the answer is not JSON"
    if isinstance(doc, list) and doc and isinstance(doc[0], dict):
        doc = doc[0]
    return (doc if isinstance(doc, dict) else None), url, None if isinstance(doc, dict) else "unexpected JSON"


def read_texts(folder: Path, rels: list[str]) -> dict:
    out = {}
    for rel in rels:
        try:
            out[rel] = (Path(folder) / rel).read_text(encoding="utf-8", errors="replace")[:MAX_TEXT]
        except OSError:
            continue
    return out


def licence_record(cand: dict, folder: Path, revision: Optional[str], fuel: Optional[tuple] = None) -> dict:
    """The record of one extracted object: its files, the ``model.config`` fields, the evidence and the decision
    (``fuel`` = the ``fetch_fuel`` result, or None when the Fuel check was skipped)."""
    name = name_of(cand["id"])
    lay = layout(folder)
    texts = read_texts(folder, lay["texts"])
    conf = config_fields(texts.get(lay["config"], "")) if lay.get("config") else {}
    a_ev, a_no = evidence_in_texts(texts)
    record, url, err = fuel if fuel else (None, fuel_url(name), "not asked (--no-fuel)")
    f_ev, f_no = evidence_in_fuel(record, url, name)
    d = decide(name, a_ev, a_no, f_ev, f_no, err)
    if not lay.get("obj"):
        d = {"kept": False, "evidence": d["evidence"], "reason": "no .obj mesh in the archive"}
    uid = gso_uid(name)
    return {"id": cand["id"], "uid": uid, "name": name, "title": cand.get("title") or name.replace("_", " "),
            "type": cand["type"], "kind": "decor", "file": cand.get("file"), "revision": revision,
            "folder": str(folder), "layout": lay, "config": conf,
            "author": "Google Research" if not conf.get("author") or conf["author"].lower() == "google"
            else conf["author"],
            "page": FUEL_PAGE.format(owner=FUEL_OWNER, name=name), "fuel_url": url, "fuel_error": err,
            "kept": d["kept"], "evidence": d["evidence"], "reason": d["reason"], "up_axis": "Z"}


def convert_jobs(records: list[dict], work: Path) -> list[dict]:
    """Blender jobs for the kept objects: ``model.obj`` (Z up, Y forward: Gazebo's frame, metres) -> a GLB in
    ``work``; the archive's texture as the fallback base colour when the .mtl does not reach it."""
    jobs = []
    for r in records:
        if not r.get("kept"):
            continue
        folder = Path(r["folder"])
        lay = r["layout"]
        jobs.append({"id": r["uid"], "src": str(folder / lay["obj"]), "dst": str(Path(work) / f"{r['uid']}.glb"),
                     "axes": [["Z", "Y"], ["Y", "NEGATIVE_Z"]], "expect_dims": None,
                     "texture": str(folder / lay["texture"]) if lay.get("texture") else None})
    return jobs
