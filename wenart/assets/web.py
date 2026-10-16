"""Tiny HTTP layer for the asset fetchers (urllib only, no extra packages).

Why its own module: both APIs refuse requests without a User-Agent (Poly
Haven answers 403 to the default ``Python-urllib`` agent), downloads must be
atomic (``.part`` then rename) and checksummed, and the tests monkeypatch
``download`` to prove that a cached asset causes no network traffic.
Proxies and CA bundles come from the environment (``HTTPS_PROXY``,
``SSL_CERT_FILE``), which urllib honours by default.

Milestone 13 round 3 (docs/milestone13.md §14.6, pod P2): every body is read to its end and checked.

- Two ambientCG API answers arrived cut on P2 (``Metal051A``: ``JSONDecodeError`` at char 61440, ``Tiles074`` at
  char 1122299) without any error from urllib. ``get_bytes`` now compares the bytes read with ``Content-Length``
  when the server sends it, ``get_json`` also retries a body that does not parse, and both try ``TRIES`` (3) times
  with a short backoff (``BACKOFF_S``: 1 s, then 2 s). A 4xx answer is not tried again (a 404 stays a 404), a 429 or
  5xx is. The last error names the URL and the try count.
- ``download`` retries a short body and an md5 mismatch the same way. After an md5 mismatch the next try asks for
  ``<url>?wenart_fresh=<unix time>``: on 16 Oct 2026 the Cloudflare edge in front of ``dl.polyhaven.org`` served a
  stale ``vintage_wooden_drawer_01.bin`` (``cf-cache-status: HIT``, ``age`` 2,053,938 s, ``last-modified`` 22 Sep
  2026, 189,056 bytes, md5 ``efa2b557...``) for the plain URL three times in a row, while the same URL with a query
  string went to the origin (``MISS``) and answered the file the API lists (187,680 bytes, md5 ``61ea9192...``).
  The query string only changes the cache key; the file is the one the md5 of the API names, or the try fails.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional

USER_AGENT = "wenart-run/0.1 (asset fetcher; CC0 textures and HDRIs)"
TIMEOUT_S = 60
TRIES = 3                       # P2 (15 Oct 2026): two cut ambientCG answers; one more try is the fix, three is margin
BACKOFF_S = 1.0                 # the wait before try n is BACKOFF_S * 2 ** (n - 2): 1 s, then 2 s
RETRY_STATUSES = (429, 500, 502, 503, 504)   # busy or broken server: worth another try; other 4xx are final
FRESH_PARAM = "wenart_fresh"    # the cache-key query string of a try after an md5 mismatch (module docstring)
CHUNK = 1 << 16


class NetworkError(RuntimeError):
    """Connection-level failure (DNS, proxy refusal, reset); not an HTTP status."""


class IncompleteBody(NetworkError):
    """The body ended before ``Content-Length`` bytes, or it did not parse (a cut answer)."""


class ChecksumError(RuntimeError):
    """A downloaded file does not have the md5 the API states (a ``RuntimeError``, as before round 3)."""


class HTTPStatusError(RuntimeError):
    """The server answered with a 4xx / 5xx status."""

    def __init__(self, url: str, status: int, n: int = 1, tries: int = 1):
        super().__init__(f"HTTP {status} for {url}" + (f" (try {n} of {tries})" if tries > 1 else ""))
        self.url = url
        self.status = status
        self.tries = n


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": USER_AGENT})


def _log(text: str) -> None:
    print(f"web: {text}", file=sys.stderr, flush=True)


def _wait(n: int, sleep: Callable) -> None:
    """The backoff before try ``n`` (n >= 2)."""
    sleep(BACKOFF_S * 2 ** (n - 2))


def content_length(response) -> Optional[int]:
    """The ``Content-Length`` header of a response as an int (None when absent or not a number)."""
    headers = getattr(response, "headers", None)
    value = headers.get("Content-Length") if headers is not None else None
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def read_body(response, url: str) -> bytes:
    """Read a response to its end; ``IncompleteBody`` when fewer bytes arrive than ``Content-Length`` says
    (``http.client``'s ``read(n)`` returns a short body without an error when the connection closes early)."""
    chunks, n = [], 0
    while True:
        chunk = response.read(CHUNK)
        if not chunk:
            break
        chunks.append(chunk)
        n += len(chunk)
    expected = content_length(response)
    if expected is not None and n != expected:
        raise IncompleteBody(f"{url}: {n} bytes read, Content-Length {expected}")
    return b"".join(chunks)


def _transient(exc: BaseException) -> bool:
    """Errors worth another try: connection errors, cut bodies, busy servers (a 429 or 5xx); a 4xx is final."""
    if isinstance(exc, urllib.error.HTTPError):          # before URLError / OSError: HTTPError is both
        return exc.code in RETRY_STATUSES
    if isinstance(exc, HTTPStatusError):
        return exc.status in RETRY_STATUSES
    return isinstance(exc, (urllib.error.URLError, ConnectionError, TimeoutError, OSError, http.client.HTTPException,
                            NetworkError))


def _final(url: str, exc: BaseException, n: int, tries: int) -> Exception:
    """The error raised after the last try ``n`` of ``tries``, or for a final status: it names the URL and the try
    count."""
    if isinstance(exc, urllib.error.HTTPError):
        return HTTPStatusError(url, exc.code, n, tries)
    if isinstance(exc, HTTPStatusError):
        return HTTPStatusError(url, exc.status, n, tries)
    if isinstance(exc, IncompleteBody):
        return IncompleteBody(f"{exc} (try {n} of {tries})")
    if isinstance(exc, NetworkError):
        return NetworkError(f"{exc} (try {n} of {tries})")
    return NetworkError(f"{url}: {type(exc).__name__}: {exc} (try {n} of {tries})")


def _parse(url: str, body: bytes, length: Optional[int], parse: Callable):
    try:
        return parse(body)
    except (ValueError, UnicodeDecodeError) as exc:
        cl = f", Content-Length {length}" if length is not None else ""
        raise IncompleteBody(f"{url}: the body does not parse ({len(body)} bytes read{cl}): "
                             f"{type(exc).__name__}: {exc}") from exc


def get_bytes(url: str, timeout: float = TIMEOUT_S, *, tries: int = TRIES, opener: Optional[Callable] = None,
              sleep: Callable = time.sleep, parse: Optional[Callable] = None):
    """GET a URL and return the body (or ``parse(body)``); raises ``HTTPStatusError`` / ``NetworkError`` /
    ``IncompleteBody`` after ``tries`` tries (a 4xx at once). ``opener`` (default ``urllib.request.urlopen``) and
    ``sleep`` are injectable (tests). A ``ValueError`` of ``parse`` (a cut JSON answer) counts as a cut body."""
    opener = opener or urllib.request.urlopen
    tries = max(1, int(tries))
    for n in range(1, tries + 1):
        if n > 1:
            _wait(n, sleep)
        try:
            with opener(_request(url), timeout=timeout) as response:
                body = read_body(response, url)
                length = content_length(response)
            return body if parse is None else _parse(url, body, length, parse)
        except Exception as exc:  # noqa: BLE001 - sorted into retry / final below
            if not _transient(exc):
                if isinstance(exc, (urllib.error.HTTPError, HTTPStatusError)):
                    raise _final(url, exc, n, tries) from exc
                raise
            if n == tries:
                raise _final(url, exc, n, tries) from exc
            _log(f"{url}: {type(exc).__name__}: {exc}; try {n + 1} of {tries}")
    raise AssertionError("unreachable")


def get_json(url: str, timeout: float = TIMEOUT_S, *, tries: int = TRIES, opener: Optional[Callable] = None,
             sleep: Callable = time.sleep):
    """GET a URL and parse the JSON body; a cut or unparsable body is tried again (``get_bytes``)."""
    return get_bytes(url, timeout, tries=tries, opener=opener, sleep=sleep,
                     parse=lambda body: json.loads(body.decode("utf-8")))


def fresh_url(url: str) -> str:
    """``url`` with the cache-key query string of a try after an md5 mismatch (module docstring)."""
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{FRESH_PARAM}={int(time.time())}"


def download(url: str, path: Path, expected_md5: Optional[str] = None, timeout: float = TIMEOUT_S, *,
             tries: int = TRIES, opener: Optional[Callable] = None, sleep: Callable = time.sleep) -> Path:
    """Stream a URL into ``path`` (via ``path.part``), check ``Content-Length`` and the md5 when given; a short body,
    a connection error, a 429 / 5xx or an md5 mismatch is tried again (after an md5 mismatch with ``fresh_url``)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + ".part")
    opener = opener or urllib.request.urlopen
    tries = max(1, int(tries))
    get = url
    for n in range(1, tries + 1):
        if n > 1:
            _wait(n, sleep)
        digest = hashlib.md5()
        try:
            with opener(_request(get), timeout=timeout) as response, part.open("wb") as fh:
                got = 0
                while True:
                    chunk = response.read(CHUNK)
                    if not chunk:
                        break
                    fh.write(chunk)
                    digest.update(chunk)
                    got += len(chunk)
                expected = content_length(response)
            if expected is not None and got != expected:
                raise IncompleteBody(f"{url}: {got} bytes read, Content-Length {expected}")
            if expected_md5 and digest.hexdigest() != expected_md5:
                raise ChecksumError(f"{url}: md5 mismatch ({digest.hexdigest()} != {expected_md5})")
        except Exception as exc:  # noqa: BLE001 - sorted into retry / final below
            part.unlink(missing_ok=True)
            checksum = isinstance(exc, ChecksumError)
            if not (checksum or _transient(exc)):
                if isinstance(exc, (urllib.error.HTTPError, HTTPStatusError)):
                    raise _final(url, exc, n, tries) from exc
                raise
            if n == tries:
                if checksum:
                    raise ChecksumError(f"{exc} (try {n} of {tries}; the tries after the first mismatch asked the "
                                        f"origin with ?{FRESH_PARAM}=)") from exc
                raise _final(url, exc, n, tries) from exc
            if checksum:
                get = fresh_url(url)          # a stale CDN copy: ask the origin
            _log(f"{url}: {type(exc).__name__}: {exc}; try {n + 1} of {tries}")
            continue
        shutil.move(str(part), str(path))
        return path
    raise AssertionError("unreachable")


def sha256_file(path: Path) -> str:
    """Hex sha256 of a file (streamed)."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
