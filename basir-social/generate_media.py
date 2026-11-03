"""Create a rolling public-media window of educational Basir Yazd story images.

Images are ORIGINAL educational posters, not photos of completed charity work.
Only a safe whitelist of pre-reviewed evergreen copy is used. This job never
talks to Meta, Eitaa, or Metricool, and does not publish social posts.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from datetime import datetime, timedelta, date
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image
from daily_jihadi_story import design, TEHRAN

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public_media"
SOCIAL_HANDLE = "@basiryazd"
ORG = "قرارگاه جهادی حضرت بقیةالله (عج)"


def produce(start: date, days: int = 14):
    if not 1 <= days <= 21:
        raise ValueError("days must be within 1–21")
    PUBLIC.mkdir(exist_ok=True, parents=True)
    data = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        filename = f"story-{day.isoformat()}.jpg"
        path = PUBLIC / filename
        info = design(day, path)
        # Enforce the actual 9:16 output contract and safe opaque JPEG.
        with Image.open(path) as img:
            if img.size != (1080,1920) or img.mode != "RGB":
                raise RuntimeError(f"Invalid media geometry: {path}")
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        data.append({
            "date": day.isoformat(),
            "kind": "STORY",
            "network_types": {"instagram": "STORY", "facebook": "STORY"},
            "file": filename,
            "path": f"basir-social/public_media/{filename}",
            "sha256": sha,
            "topic_id": info["topic_id"],
            "category": info["category"],
            "title": info["title"],
            "org": ORG,
            "handle": SOCIAL_HANDLE,
            "description": "Original educational poster; not an event report",
            "ai_generated": False,
            "review_required_for_any_real_world_event": True
        })
    manifest = {
        "source": "basir-social/daily_jihadi_story.py",
        "timezone": "Asia/Tehran",
        "generated_for_start": start.isoformat(),
        "generated_by": "automated design runner",
        "image_format": "JPEG",
        "image_size": [1080,1920],
        "publisher_mode": "MEDIA_ONLY_NOT_PUBLISHED",
        "items": data
    }
    (PUBLIC / "manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--start",default=datetime.now(TEHRAN).date().isoformat())
    parser.add_argument("--days",type=int,default=14)
    args=parser.parse_args()
    m=produce(date.fromisoformat(args.start),args.days)
    print(f"Generated {len(m['items'])} branded educational story images from {args.start}")
    print("Output is media only; no account was published to.")
