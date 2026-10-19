"""Fetch a non-primary transliteration (IT2a, GC) locally with hash recording.

Usage:  python scripts/fetch_transliteration.py it2a|gc [--expect-sha256 HEX]

Sources are declared in data/sources.yml. Files are written to data/raw/ (git-
ignored; redistribution terms are not verified, so nothing is committed) and
their sha256 is appended to data/local_manifest.json. On the first verified
fetch, copy the printed sha256 into data/sources.yml so later runs can verify.
Gate v2 refuses transliteration evidence whose source hash is not registered.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.request import urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "data" / "sources.yml"
MANIFEST = ROOT / "data" / "local_manifest.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("key", choices=["it2a", "gc"])
    ap.add_argument("--expect-sha256")
    a = ap.parse_args()
    src = yaml.safe_load(SOURCES.read_text(encoding="utf-8"))["sources"][a.key]
    expect = a.expect_sha256 or (src.get("sha256") if isinstance(src.get("sha256"), str) and len(src.get("sha256", "")) == 64 else None)
    print(f"Fetching {src['url']}")
    try:
        data = urlopen(src["url"], timeout=60).read()
    except Exception as exc:  # network policy may block voynich.nu
        print(f"FETCH_FAILED: {exc}", file=sys.stderr)
        return 2
    sha = hashlib.sha256(data).hexdigest()
    if expect and sha != expect:
        raise SystemExit(f"identity mismatch: expected {expect}, got {sha}")
    out = ROOT / src["local_path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {}
    if "sources" not in manifest:
        manifest = {"zl3b": manifest} if manifest else {}
        manifest = {"sources": manifest}
    manifest["sources"][a.key] = {"source": src["url"], "bytes": len(data), "sha256": sha,
                                  "local_path": src["local_path"], "verified_against_registered_hash": bool(expect)}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["sources"][a.key], indent=2))
    if not expect:
        print("NOTE: first fetch — register this sha256 in data/sources.yml before using the file as evidence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
