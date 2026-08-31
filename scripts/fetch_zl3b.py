from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "ZL3b-n.txt"
URL = "https://raw.githubusercontent.com/matthewdgreen/cipher_benchmark/main/benchmark/unsolved/sources/voynich/transcriptions/ZL3b-n.txt"
EXPECTED_GIT_BLOB_SHA1 = "2a4533ab9bdfa85db9bad602d590978953055df1"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> int:
    print(f"Fetching {URL}")
    data = urlopen(URL, timeout=60).read()
    blob = git_blob_sha1(data)
    if blob != EXPECTED_GIT_BLOB_SHA1:
        raise SystemExit(f"identity mismatch: expected {EXPECTED_GIT_BLOB_SHA1}, got {blob}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    manifest = {
        "source": URL,
        "bytes": len(data),
        "git_blob_sha1": blob,
        "sha256": hashlib.sha256(data).hexdigest(),
        "local_path": str(OUT.relative_to(ROOT)),
    }
    (ROOT / "data" / "local_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
