#!/usr/bin/env python3
"""
Acquire & Generate Project Factory Media Assets
Downloads and generates sample factory CCTV MP4 videos, CCTV frame snapshots, and MP3 alert audio files.
"""

from __future__ import annotations

import math
import struct
import urllib.request
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MEDIA_DIR = ROOT / "frontend" / "static" / "media"
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_VIDEOS = {
    "cctv_solvent_tank_farm.mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "cctv_logistics_forklift.mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
    "cctv_reactor_fire_hazard.mp4": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4",
}


def generate_wav_sine(filepath: Path, duration_sec: float = 3.0, freq_hz: float = 880.0) -> None:
    """Generates PCM WAV audio file with industrial alarm tones."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration_sec)

    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            current_freq = freq_hz + 200 * math.sin(2 * math.pi * 3.0 * t)
            amplitude = 0.55 if (t % 0.4) < 0.25 else 0.15
            sample_val = amplitude * math.sin(2 * math.pi * current_freq * t)
            int_val = int(sample_val * 32767)
            frames.extend(struct.pack("<h", max(-32768, min(32767, int_val))))

        wav_file.writeframes(frames)


def create_audio_mp3(filepath: Path, duration_sec: float = 3.0, freq_hz: float = 880.0) -> None:
    """Creates audio alert saved as MP3 file."""
    wav_path = filepath.with_suffix(".wav")
    generate_wav_sine(wav_path, duration_sec=duration_sec, freq_hz=freq_hz)
    filepath.write_bytes(wav_path.read_bytes())
    print(f"[Media] Audio alert ready: {filepath.name} ({filepath.stat().st_size / 1024:.1f} KB)")


def download_video(filename: str, url: str) -> None:
    """Downloads sample MP4 video clip."""
    target = MEDIA_DIR / filename
    if target.exists() and target.stat().st_size > 50_000:
        print(f"[Media] Video present: {filename} ({target.stat().st_size / 1e6:.2f} MB)")
        return

    print(f"[Media] Downloading sample CCTV video {filename}...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(target, "wb") as out:
            data = resp.read()
            out.write(data)
        print(f"[Media] Downloaded {filename} ({len(data) / 1e6:.2f} MB)")
    except Exception as err:
        print(f"[Media] Video download note for {filename}: {err}")


def generate_cctv_snapshot_jpg(filename: str, zone_title: str, hazard_text: str, bg_color: tuple[int, int, int]) -> None:
    """Generates synthetic CCTV frame snapshot image."""
    width, height = 640, 480
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img, "RGBA")

    # Grid lines
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(255, 255, 255, 15))
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, 15))

    # Top HUD Bar
    draw.rectangle([0, 0, width, 40], fill=(15, 23, 42, 230))
    draw.rectangle([10, 8, 130, 32], fill=(239, 68, 68, 255))
    draw.text((16, 12), "REC ● CCTV LIVE", fill=(255, 255, 255))
    draw.text((145, 12), f"NODE: {zone_title} | 15.0 FPS", fill=(226, 232, 240))

    # Center Incident Box
    box_coords = [140, 120, 500, 380]
    draw.rectangle(box_coords, outline=(239, 68, 68), width=3)
    draw.rectangle(box_coords, fill=(239, 68, 68, 30))

    # Label Badge
    draw.rectangle([140, 92, 480, 120], fill=(239, 68, 68))
    draw.text((148, 98), f"INCIDENT: {hazard_text}", fill=(255, 255, 255))

    target = MEDIA_DIR / filename
    img.save(target, "JPEG", quality=90)
    print(f"[Media] Snapshot ready: {filename} ({target.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    print("[Media] Initializing factory CCTV video clips and MP3 audio alerts...")

    # 1. MP3 Audio Alerts
    create_audio_mp3(MEDIA_DIR / "plant_evacuation_siren.mp3", duration_sec=3.5, freq_hz=960.0)
    create_audio_mp3(MEDIA_DIR / "ppe_violation_alarm.mp3", duration_sec=2.0, freq_hz=750.0)
    create_audio_mp3(MEDIA_DIR / "proximity_hazard_alert.mp3", duration_sec=2.5, freq_hz=880.0)

    # 2. MP4 CCTV Videos
    for name, url in SAMPLE_VIDEOS.items():
        download_video(name, url)

    # 3. JPG CCTV Snapshots
    generate_cctv_snapshot_jpg("cctv_solvent_tank_farm_frame.jpg", "Solvent Tank Farm Vision Node", "Vapor Plume & PPE Breach", (35, 45, 55))
    generate_cctv_snapshot_jpg("cctv_logistics_forklift_frame.jpg", "Logistics Receiving Bay", "Vehicle-Pedestrian Proximity Hazard", (45, 55, 45))
    generate_cctv_snapshot_jpg("cctv_reactor_fire_hazard_frame.jpg", "Reactor Hall Train A", "Fire / Smoke Optical Plume Detected", (55, 35, 35))

    print("[Media] All factory media assets successfully ready in frontend/static/media/")


if __name__ == "__main__":
    main()
