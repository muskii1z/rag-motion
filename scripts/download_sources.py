"""Download every external document listed in data/sources.toml into data/raw/ and verify it.

Run from the project folder (only needed on a fresh clone; data/raw/ is git-ignored):
    uv run python scripts/download_sources.py

Skips files that already exist. Every file is checked against the sha256 in the manifest,
so a changed upstream file is reported instead of silently ingested.
"""

import requests

from ragmotion.ingestion import load_sources, verify_file


def main() -> None:
    for source in load_sources().values():
        if source.type != "document":
            continue  # project notes live in the repo
        if not source.path.exists():
            url = source.download_url or source.url
            print(f"Downloading {source.id} from {url} ...")
            response = requests.get(url, timeout=120)
            response.raise_for_status()
            source.path.parent.mkdir(parents=True, exist_ok=True)
            source.path.write_bytes(response.content)
        verify_file(source)
        print(f"ok  {source.id:<20} {source.path.name} ({source.path.stat().st_size:,} bytes, sha256 verified)")


if __name__ == "__main__":
    main()
