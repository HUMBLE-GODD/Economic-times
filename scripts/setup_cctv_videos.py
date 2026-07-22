#!/usr/bin/env python3
"""
Setup User CCTV Videos and Remove Siren Audio
Copies user's 4 real CCTV MP4 videos from ./cctvs/ into frontend/media/,
extracts poster thumbnails for each video stream, and removes all audio siren files.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from PIL import Image

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

ROOT = Path(__file__).resolve().parents[1]
CCTVS_DIR = ROOT / "cctvs"
MEDIA_DIR = ROOT / "frontend" / "media"
STATIC_MEDIA_DIR = ROOT / "frontend" / "static" / "media"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)
STATIC_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

USER_VIDEOS = [
    ("7622781-uhd_3840_2160_25fps.mp4", "cctv_camera_1.mp4", "Solvent Tank Farm (Camera #1)", "cctv_camera_1_poster.jpg"),
    ("12813835_1080_1920_60fps.mp4", "cctv_camera_2.mp4", "Reactor Hall Train A (Camera #2)", "cctv_camera_2_poster.jpg"),
    ("13053655_3840_2160_50fps.mp4", "cctv_camera_3.mp4", "Logistics Receiving Bay (Camera #3)", "cctv_camera_3_poster.jpg"),
    ("14855344_2160_3840_30fps.mp4", "cctv_camera_4.mp4", "Utilities & Boiler Island (Camera #4)", "cctv_camera_4_poster.jpg"),
]


def extract_poster_frame(video_path: Path, output_poster_path: Path) -> None:
    """Extracts first frame of MP4 video as poster image thumbnail."""
    if HAS_CV2 and video_path.exists():
        try:
            cap = cv2.VideoCapture(str(video_path))
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img.save(output_poster_path, "JPEG", quality=88)
                print(f"[CCTV Setup] Extracted video poster: {output_poster_path.name}")
                return
        except Exception as e:
            print(f"[CCTV Setup] Frame extraction note: {e}")

    # Fallback placeholder image
    img = Image.new("RGB", (640, 360), (30, 40, 50))
    img.save(output_poster_path, "JPEG", quality=85)
    print(f"[CCTV Setup] Created fallback poster: {output_poster_path.name}")


def main() -> None:
    print("[CCTV Setup] Processing 4 CCTV videos from ./cctvs/...")

    # 1. Remove old siren audio files (*.mp3, *.wav) and old dummy sample videos
    for folder in [MEDIA_DIR, STATIC_MEDIA_DIR]:
        for file in folder.glob("*"):
            if file.suffix.lower() in [".mp3", ".wav"] or "solvent_tank" in file.name or "forklift" in file.name:
                try:
                    file.unlink()
                    print(f"[CCTV Setup] Removed file: {file.name}")
                except Exception:
                    pass

    # 2. Copy the 4 user videos and extract poster thumbnails
    for src_filename, dest_filename, title, poster_filename in USER_VIDEOS:
        src_path = CCTVS_DIR / src_filename
        if src_path.exists():
            dest_media = MEDIA_DIR / dest_filename
            dest_static = STATIC_MEDIA_DIR / dest_filename

            shutil.copy2(src_path, dest_media)
            shutil.copy2(src_path, dest_static)
            print(f"[CCTV Setup] Copied {src_filename} -> {dest_filename} ({src_path.stat().st_size / 1e6:.2f} MB)")

            poster_media = MEDIA_DIR / poster_filename
            poster_static = STATIC_MEDIA_DIR / poster_filename

            extract_poster_frame(dest_media, poster_media)
            if poster_media.exists():
                shutil.copy2(poster_media, poster_static)

    print("[CCTV Setup] Successfully configured 4 CCTV videos and removed all audio siren files!")


if __name__ == "__main__":
    main()
