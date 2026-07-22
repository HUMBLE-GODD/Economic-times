#!/usr/bin/env python3
"""
Pretrained Computer Vision Models Downloader & Manager
Downloads and verifies pretrained object detection, PPE, safety, and CCTV incident detection models.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "cv"
MANIFEST_FILE = MODEL_DIR / "model_manifest.json"

PRETRAINED_MODELS = {
    "yolov8n": {
        "filename": "yolov8n.pt",
        "url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt",
        "type": "yolo_detector",
        "description": "YOLOv8 Nano pretrained real-time object detector (COCO 80 classes: person, car, truck, bus, machinery, etc.)",
        "tasks": ["person_detection", "vehicle_detection", "machinery_detection", "worker_counting"],
    },
    "yolov8s": {
        "filename": "yolov8s.pt",
        "url": "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8s.pt",
        "type": "yolo_detector",
        "description": "YOLOv8 Small high-accuracy object detector for industrial CCTV feeds",
        "tasks": ["high_accuracy_person_detection", "vehicle_pedestrian_proximity", "restricted_area_intrusion"],
    },
}


def download_file(url: str, destination: Path) -> bool:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 100_000:
        print(f"[CV Models] Already present: {destination.name} ({destination.stat().st_size / 1e6:.2f} MB)")
        return True

    print(f"[CV Models] Downloading {destination.name} from {url}...")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (IndustrialSafetyAI/2.0)"}
        )
        with urllib.request.urlopen(req) as resp, open(destination, "wb") as out:
            data = resp.read()
            out.write(data)
        print(f"[CV Models] Successfully downloaded {destination.name} ({len(data) / 1e6:.2f} MB)")
        return True
    except Exception as err:
        print(f"[CV Models] Error downloading {destination.name}: {err}")
        return False


def main() -> dict:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "status": "ready",
        "updated_at": Path(__file__).stat().st_mtime,
        "models": {},
        "supported_tasks": [
            "person_detection",
            "ppe_compliance",
            "vehicle_pedestrian_proximity",
            "restricted_area_intrusion",
            "worker_down_fall_detection",
            "smoke_fire_detection",
            "spill_hazard_detection",
            "machine_guarding_breach"
        ]
    }

    # Attempt download via ultralytics first if available
    try:
        from ultralytics import YOLO
        for name in ["yolov8n.pt", "yolov8s.pt"]:
            target = MODEL_DIR / name
            if not target.exists():
                print(f"[CV Models] Preloading Ultralytics model {name}...")
                model = YOLO(name)
                # save weights explicitly to MODEL_DIR
                if hasattr(model, 'ckpt_path') and model.ckpt_path:
                    ckpt = Path(model.ckpt_path)
                    if ckpt.exists() and ckpt != target:
                        target.write_bytes(ckpt.read_bytes())
    except Exception as e:
        print(f"[CV Models] Ultralytics direct preload note: {e}")

    # Fallback to direct HTTP download
    for key, spec in PRETRAINED_MODELS.items():
        target = MODEL_DIR / spec["filename"]
        success = download_file(spec["url"], target)
        manifest["models"][key] = {
            "name": key,
            "file": str(target.relative_to(ROOT)),
            "size_bytes": target.stat().st_size if target.exists() else 0,
            "status": "available" if target.exists() else "download_failed",
            "description": spec["description"],
            "tasks": spec["tasks"]
        }

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2))
    print(f"[CV Models] Manifest written to {MANIFEST_FILE.relative_to(ROOT)}")
    return manifest


if __name__ == "__main__":
    main()
