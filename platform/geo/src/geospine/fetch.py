"""Download raw geography sources into data/raw/.

Idempotent: skips a file that already exists unless force=True. Writes a
`_manifest.json` next to each source recording URL, size, sha256, and the time
it was retrieved — provenance for `build.py`.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import httpx

from .sources import BIG, OPTIONAL, SOURCES, Source

_UA = "alaafia-geospine/0.1 (+https://github.com/anthoniooladimeji11-coder/Alaafia)"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(src: Source) -> None:
    src.path.parent.mkdir(parents=True, exist_ok=True)
    tmp = src.path.with_suffix(src.path.suffix + ".part")
    with httpx.stream(
        "GET", src.url, follow_redirects=True, timeout=120.0, headers={"User-Agent": _UA}
    ) as r:
        r.raise_for_status()
        with tmp.open("wb") as fh:
            for chunk in r.iter_bytes(1 << 20):
                fh.write(chunk)
    tmp.replace(src.path)


def fetch_one(src: Source, *, force: bool = False) -> dict:
    if src.path.exists() and not force:
        action = "skip (exists)"
    else:
        _download(src)
        action = "downloaded"
    meta = {
        "key": src.key,
        "title": src.title,
        "url": src.url,
        "licence": src.licence,
        "provider": src.provider,
        "path": str(src.path),
        "bytes": src.path.stat().st_size,
        "sha256": _sha256(src.path),
        "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": action,
    }
    (src.path.parent / f"{src.path.stem}._manifest.json").write_text(
        json.dumps(meta, indent=2)
    )
    return meta


def fetch_all(
    *, force: bool = False, big: bool = False, only: list[str] | None = None
) -> list[dict]:
    only = set(only or [])
    out = []
    for key, src in SOURCES.items():
        if only:
            if key not in only:
                continue
        elif key in OPTIONAL:
            print(f"  · {key}: skipped (optional — name it explicitly to fetch)")
            continue
        elif key in BIG and not big:
            print(f"  · {key}: skipped (large — pass --big)")
            continue
        meta = fetch_one(src, force=force)
        print(f"  · {key}: {meta['action']}  ({meta['bytes'] / 1e6:.1f} MB)")
        out.append(meta)
    return out
