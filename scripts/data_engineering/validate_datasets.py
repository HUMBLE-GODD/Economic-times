#!/usr/bin/env python3
"""Validate acquired public datasets and generate quality reports."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import zipfile
from dataclasses import dataclass, asdict
from typing import Iterable

import pandas as pd
import yaml


ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "metadata" / "datasets.yml"
REPORT_MD = ROOT / "reports" / "dataset_quality_report.md"
REPORT_JSON = ROOT / "reports" / "dataset_quality_report.json"


@dataclass
class FileQuality:
    dataset_id: str
    path: str
    exists: bool
    file_size_bytes: int | None = None
    sha256: str | None = None
    rows: int | None = None
    columns: int | None = None
    duplicate_rows: int | None = None
    missing_cells: int | None = None
    missing_pct: float | None = None
    encoding: str | None = None
    status: str = "unchecked"
    notes: str = ""


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def csv_dialect(path: pathlib.Path) -> tuple[str, str]:
    for encoding in ("utf-8", "latin1"):
        try:
            sample = path.read_text(encoding=encoding, errors="strict")[:8192]
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t| ").delimiter
            return encoding, delimiter
        except Exception:
            continue
    return "utf-8", ","


def read_preview(path: pathlib.Path) -> pd.DataFrame:
    if path.name == "AirQualityUCI.csv":
        return pd.read_csv(path, sep=";", encoding="latin1", low_memory=False)
    if path.name in {"secom.data", "secom_labels.data"}:
        return pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    if path.name.startswith("batch") and path.suffix == ".dat":
        rows = []
        with path.open() as handle:
            for line in handle:
                parts = line.strip().split()
                if not parts:
                    continue
                row = {"target": int(parts[0])}
                for item in parts[1:]:
                    key, value = item.split(":", 1)
                    row[f"feature_{int(key):03d}"] = float(value)
                rows.append(row)
        return pd.DataFrame(rows)
    if path.name.startswith(("train_", "test_", "RUL_")) and path.suffix == ".txt":
        return pd.read_csv(path, sep=r"\s+", header=None, engine="python")
    encoding, delimiter = csv_dialect(path)
    return pd.read_csv(path, sep=delimiter, encoding=encoding, low_memory=False)


def validate_file(dataset_id: str, path: pathlib.Path) -> FileQuality:
    result = FileQuality(dataset_id=dataset_id, path=str(path.relative_to(ROOT)), exists=path.exists())
    if not path.exists():
        result.status = "missing"
        result.notes = "Path is not present on disk."
        return result

    result.file_size_bytes = path.stat().st_size
    result.sha256 = sha256(path)

    if path.suffix.lower() == ".zip":
        try:
            with zipfile.ZipFile(path) as archive:
                bad = archive.testzip()
                result.status = "pass" if bad is None else "fail"
                result.notes = "Archive central directory valid." if bad is None else f"Corrupt member: {bad}"
        except zipfile.BadZipFile:
            result.status = "fail"
            result.notes = "Zip central directory missing or incomplete."
        return result

    if path.name.lower() in {"readme.txt"}:
        result.status = "pass"
        result.notes = "Text documentation retained; tabular checks skipped."
        return result

    if path.suffix.lower() not in {".csv", ".data", ".dat", ".txt"}:
        result.status = "pass"
        result.notes = "Binary/document source retained; tabular checks skipped."
        return result

    try:
        df = read_preview(path)
        result.rows = len(df)
        result.columns = len(df.columns)
        result.duplicate_rows = int(df.duplicated().sum())
        missing = int(df.isna().sum().sum())
        result.missing_cells = missing
        cells = max(len(df) * len(df.columns), 1)
        result.missing_pct = round(missing * 100 / cells, 4)
        result.encoding = "latin1" if path.name == "AirQualityUCI.csv" else "utf-8_or_detected"
        result.status = "pass"
        if result.rows == 0 or result.columns == 0:
            result.status = "fail"
            result.notes = "No rows or columns parsed."
        elif result.missing_pct and result.missing_pct > 35:
            result.status = "warn"
            result.notes = "High missingness; use only with imputation/feature selection."
        else:
            result.notes = "Parsed successfully."
    except Exception as exc:
        result.status = "fail"
        result.notes = f"{type(exc).__name__}: {exc}"
    return result


def dataset_paths(dataset: dict) -> Iterable[pathlib.Path]:
    base = ROOT / dataset["local_path"]
    if base.is_file():
        yield base
        return
    if base.is_dir():
        for path in sorted(base.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".csv", ".data", ".dat", ".txt", ".zip", ".pdf", ".html"}:
                yield path
        return
    if base.suffix:
        yield base


def render_markdown(results: list[FileQuality], registry: dict) -> str:
    by_id = {dataset["id"]: dataset for dataset in registry["datasets"]}
    lines = [
        "# Dataset Quality Report",
        "",
        "Generated by `scripts/data_engineering/validate_datasets.py`.",
        "",
        "| Dataset | Status | File | Rows | Columns | Missing % | Duplicates | Notes |",
        "|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for result in results:
        dataset = by_id.get(result.dataset_id, {})
        title = dataset.get("title", result.dataset_id)
        lines.append(
            f"| {title} | {result.status} | `{result.path}` | "
            f"{result.rows if result.rows is not None else ''} | "
            f"{result.columns if result.columns is not None else ''} | "
            f"{result.missing_pct if result.missing_pct is not None else ''} | "
            f"{result.duplicate_rows if result.duplicate_rows is not None else ''} | "
            f"{result.notes} |"
        )

    lines.extend([
        "",
        "## Quality Decisions",
        "",
        "- `pass`: usable after the documented cleaning step.",
        "- `warn`: usable only with explicit imputation, filtering, or caveats.",
        "- `fail`: do not use until reacquired or manually repaired from the source.",
        "",
        "Licensing decisions are tracked separately in `metadata/datasets.yml` because a technically valid file can still be blocked for commercial use.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    registry = yaml.safe_load(REGISTRY.read_text())
    results: list[FileQuality] = []
    for dataset in registry["datasets"]:
        paths = list(dataset_paths(dataset))
        if not paths:
            results.append(validate_file(dataset["id"], ROOT / dataset["local_path"]))
            continue
        for path in paths:
            results.append(validate_file(dataset["id"], path))

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps([asdict(r) for r in results], indent=2))
    REPORT_MD.write_text(render_markdown(results, registry))
    print(f"wrote {REPORT_MD}")
    print(f"wrote {REPORT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
