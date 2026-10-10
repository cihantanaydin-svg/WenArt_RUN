"""scripts/drive_upload.sh (user request of 10 Oct 2026): the 3D files of a project go to Google Drive with the
user's rclone config; the config is never logged and is deleted afterwards; a missing config is a skip."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "drive_upload.sh"
VERSION = "v1.75.2"


def _run(tmp_path, conf, projects):
    fast = tmp_path / "fast"
    bindir = fast / f"rclone-{VERSION}"
    bindir.mkdir(parents=True)
    calls = tmp_path / "calls.txt"
    fake = bindir / "rclone"
    # a fake rclone: lists one remote, records the copy calls and whether its config file exists
    fake.write_text(f"""#!/usr/bin/env bash
if [ "$3" = "listremotes" ]; then echo "gdrive:"; exit 0; fi
echo "$@" >> {calls}
[ -f "$2" ] && echo "conf-present" >> {calls}
exit 0
""")
    fake.chmod(0o755)
    out = tmp_path / "outputs"
    exp = out / "real02" / "export"
    exp.mkdir(parents=True)
    (exp / "real02.blend").write_bytes(b"b")
    (exp / "real02.glb").write_bytes(b"g")
    (exp / "export_manifest.json").write_text("{}")
    env = dict(os.environ, WENART_FAST=str(fast), WENART_LOGS=str(tmp_path / "logs"))
    if conf is not None:
        env["RCLONE_CONF"] = conf
    r = subprocess.run(["bash", str(SCRIPT), str(out), *projects], env=env, capture_output=True, text=True)
    return r, fast, calls, tmp_path / "logs"


def test_upload_with_a_config(tmp_path):
    secret = "[gdrive]\ntype = drive\ntoken = {\"access_token\":\"SECRET-VALUE\"}"
    r, fast, calls, logs = _run(tmp_path, secret, ["real02", "nothing-here"])
    assert r.returncode == 0, r.stderr
    text = calls.read_text()
    assert "copy" in text and "gdrive:WenArt/real02/" in text and "conf-present" in text
    assert "--include *.blend --include *.glb" in text
    assert not (fast / "rclone-upload.conf").exists()                      # deleted on exit
    log = "".join(p.read_text() for p in logs.glob("drive-upload-*.log")) + r.stdout + r.stderr
    assert "SECRET-VALUE" not in log and "nothing-here: no 3D files" in log


def test_no_config_is_a_skip(tmp_path):
    r, _fast, calls, _logs = _run(tmp_path, None, ["real02"])
    assert r.returncode == 0 and not calls.exists() and "skipped" in r.stdout
    r, _fast, calls, _logs = _run(tmp_path / "b", "{{ RUNPOD_SECRET_rclone_conf }}", ["real02"])
    assert r.returncode == 0 and not calls.exists()
