"""Tiny HTTP layer for the asset fetchers (urllib only, no extra packages).

Why its own module: both APIs refuse requests without a User-Agent (Poly
Haven answers 403 to the default ``Python-urllib`` agent), downloads must be
atomic (``.part`` then rename) and checksummed, and the tests monkeypatch
``download`` to prove that a cached asset causes no network traffic.
Proxies and CA bundles come from the environment (``HTTPS_PROXY``,
``SSL_CERT_FILE``), which urllib honours by default.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

USER_AGENT = "wenart-run/0.1 (asset fetcher; CC0 textures and HDRIs)"
TIMEOUT_S = 60


class NetworkError(RuntimeError):
    """Connection-level failure (DNS, proxy refusal, reset); not an HTTP status."""


class HTTPStatusError(RuntimeError):
    """The server answered with a 4xx / 5xx status."""

    def __init__(self, url: str, status: int):
        super().__init__(f"HTTP {status} for {url}")
        self.url = url
        self.status = status


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": USER_AGENT})


def get_bytes(url: str, timeout: float = TIMEOUT_S) -> bytes:
    """GET a URL and return the body; raises HTTPStatusError / NetworkError."""
    try:
        with urllib.request.urlopen(_request(url), timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise HTTPStatusError(url, exc.code) from exc
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
        raise NetworkError(f"{url}: {exc}") from exc


def get_json(url: str, timeout: float = TIMEOUT_S):
    """GET a URL and parse the JSON body."""
    return json.loads(get_bytes(url, timeout).decode("utf-8"))


def download(url: str, path: Path, expected_md5: Optional[str] = None, timeout: float = TIMEOUT_S) -> Path:
    """Stream a URL into ``path`` (via ``path.part``), verify md5 when given."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    digest = hashlib.md5()
    try:
        with urllib.request.urlopen(_request(url), timeout=timeout) as response, part.open("wb") as fh:
            while True:
                chunk = response.read(1 << 16)
                if not chunk:
                    break
                fh.write(chunk)
                digest.update(chunk)
    except urllib.error.HTTPError as exc:
        part.unlink(missing_ok=True)
        raise HTTPStatusError(url, exc.code) from exc
    except (urllib.error.URLError, ConnectionError, TimeoutError, OSError) as exc:
        part.unlink(missing_ok=True)
        raise NetworkError(f"{url}: {exc}") from exc
    if expected_md5 and digest.hexdigest() != expected_md5:
        part.unlink(missing_ok=True)
        raise RuntimeError(f"{url}: md5 mismatch ({digest.hexdigest()} != {expected_md5})")
    shutil.move(str(part), str(path))
    return path


def sha256_file(path: Path) -> str:
    """Hex sha256 of a file (streamed)."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
