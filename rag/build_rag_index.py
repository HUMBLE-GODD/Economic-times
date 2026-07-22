#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "rag" / "index.json"


def tokenize(text: str) -> list[str]:
    stop = {"the", "and", "for", "with", "that", "this", "from", "into", "shall", "have", "are", "was"}
    return [t for t in re.findall(r"[a-zA-Z0-9_]{3,}", text.lower()) if t not in stop]


def strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(re.sub(r"\s+", " ", text))


def chunks_for(path: Path, title: str) -> list[dict]:
    raw = path.read_text(errors="ignore") if path.suffix.lower() not in {".pdf", ".zip", ".xlsx"} else ""
    if path.suffix.lower() == ".html":
        raw = strip_html(raw)
    if not raw:
        raw = f"{title}. Binary document retained at {path.relative_to(ROOT)} for citation and downstream parser integration."
    chunks = []
    size = 1200
    overlap = 200
    for start in range(0, len(raw), size - overlap):
        text = raw[start:start + size].strip()
        if len(text) < 80:
            continue
        chunks.append({
            "id": f"{path.stem}_{start}",
            "title": title,
            "source": str(path.relative_to(ROOT)),
            "offset": start,
            "text": text,
            "terms": tokenize(text),
        })
    return chunks


def main() -> int:
    sources = [
        (ROOT / "docs/phase1_research_and_planning.md", "Phase 1 Research and Planning"),
        (ROOT / "reports/dataset_survey.md", "Dataset Survey"),
        (ROOT / "reports/dataset_selection_report.md", "Dataset Selection Report"),
        (ROOT / "reports/data_engineering_summary.md", "Data Engineering Summary"),
        (ROOT / "reports/dataset_quality_report.md", "Dataset Quality Report"),
        (ROOT / "datasets/raw/regulations/osha/1904_39_severe_injury_reporting.html", "OSHA 1904.39 Severe Injury Reporting"),
        (ROOT / "datasets/raw/regulations/osha/1910_147_lockout_tagout.html", "OSHA 1910.147 Lockout Tagout"),
        (ROOT / "datasets/raw/regulations/osha/1910_119_process_safety_management.html", "OSHA 1910.119 Process Safety Management"),
        (ROOT / "datasets/raw/predictive_maintenance/nasa_cmapss/readme.txt", "NASA C-MAPSS Readme"),
        (ROOT / "datasets/raw/regulations/nist/NIST_SP_800_82r3_ICS_Security.pdf", "NIST SP 800-82r3 OT Security"),
    ]
    all_chunks = []
    for path, title in sources:
        if path.exists():
            all_chunks.extend(chunks_for(path, title))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"created_at": datetime.now(timezone.utc).isoformat(), "chunks": all_chunks}, indent=2))
    print(f"indexed {len(all_chunks)} chunks -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

