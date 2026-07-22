#!/usr/bin/env python3
"""Download the public datasets listed in metadata/datasets.yml.

The script is intentionally conservative: it downloads only URLs already vetted in
the metadata registry and never fabricates fallback data.
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import urllib.request
import zipfile

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "metadata" / "datasets.yml"


def download(url: str, destination: pathlib.Path, overwrite: bool) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not overwrite:
        print(f"skip existing {destination}")
        return
    print(f"download {url} -> {destination}")
    with urllib.request.urlopen(url, timeout=120) as response:
        destination.write_bytes(response.read())


def maybe_unzip(path: pathlib.Path, destination: pathlib.Path) -> None:
    if path.suffix.lower() != ".zip":
        return
    try:
        with zipfile.ZipFile(path) as archive:
            archive.extractall(destination)
            print(f"unzip {path} -> {destination}")
    except zipfile.BadZipFile:
        print(f"WARNING: corrupt or incomplete archive: {path}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--ids", nargs="*", help="Optional dataset IDs to fetch")
    args = parser.parse_args()

    registry = yaml.safe_load(REGISTRY.read_text())
    selected = set(args.ids or [])

    for dataset in registry["datasets"]:
        if selected and dataset["id"] not in selected:
            continue
        url = dataset.get("download_url")
        if not url:
            continue
        local_path = ROOT / dataset["local_path"]
        destination = local_path if local_path.suffix else local_path / "source.zip"
        download(url, destination, overwrite=args.overwrite)
        maybe_unzip(destination, destination.parent)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

