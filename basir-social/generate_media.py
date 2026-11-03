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
from PIL import Image, ImageDraw
from daily_jihadi_story import design, TEHRAN, choose_topic, PALETTES, _font, _lines, _center

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public_media"
SOCIAL_HANDLE = "@basiryazd"
ORG = "قرارگاه جهادی حضرت بقیةالله (عج)"



def design_feed(day: date, path: Path):
    """Original 1080x1350 educational feed poster, no photographic claims."""
    category,title,detail,topic_id=choose_topic(day)
    top,bottom,highlight,white=PALETTES[(topic_id//2+topic_id)%len(PALETTES)]
    w,h=1080,1350
    im=Image.new("RGB",(w,h))
    d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/(h-1)
        d.line((0,y,w,y),fill=tuple(int(top[k]*(1-t)+bottom[k]*t) for k in range(3)))
    d.rounded_rectangle((48,48,1032,1300),radius=44,outline=highlight,width=4)
    d.line((220,210,860,210),fill=highlight,width=3)
    _center(d,ORG,142,_font(33,True),white)
    _center(d,category,300,_font(42,True),highlight)
    title_font=_font(68,True)
    title_lines=_lines(d,title,title_font,890,2)
    ty=420-(len(title_lines)-1)*53
    for part in title_lines:
        _center(d,part,ty,title_font,white)
        ty+=108
    message_font=_font(40)
    message_lines=_lines(d,detail,message_font,790,4)
    panel_y=682
    d.rounded_rectangle((98,panel_y,982,panel_y+380),radius=30,fill=top,outline=highlight,width=3)
    msg_y=765
    for part in message_lines:
        _center(d,part,msg_y,message_font,white)
        msg_y+=75
    _center(d,"آموزش و پیشنهاد خدمت؛ نه گزارش رویداد واقعی",1140,_font(25),highlight)
    _center(d,"بصیر یزد",1200,_font(33,True),white)
    d.text((540,1260),"@basiryazd",font=_font(35,True),anchor="mm",fill=white,direction="ltr")
    path.parent.mkdir(exist_ok=True,parents=True)
    im.save(path,"JPEG",quality=87,subsampling=0)
    return {"path":path,"category":category,"title":title,"detail":detail,
            "topic_id":topic_id,"kind":"EDUCATIONAL_NOT_AN_EVENT_REPORT"}


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

        feed_name=f"feed-{day.isoformat()}.jpg"
        feed_path=PUBLIC / feed_name
        feed=design_feed(day,feed_path)
        with Image.open(feed_path) as img:
            if img.size != (1080,1350) or img.mode != "RGB":
                raise RuntimeError(f"Invalid feed geometry: {feed_path}")
        feed_sha=hashlib.sha256(feed_path.read_bytes()).hexdigest()
        caption=(f"🌿 {feed['title']}\n\n{feed['detail']}\n\n"
                 "قرارگاه جهادی حضرت بقیةالله (عج) | بصیر یزد\n"
                 "@basiryazd\n\n"
                 "#بصیر_یزد #کار_خیر #خدمت_اجتماعی")
        data.append({
            "date": day.isoformat(),
            "kind": "POST",
            "network_types": {"instagram": "POST", "facebook": "POST"},
            "file": feed_name,
            "path": f"basir-social/public_media/{feed_name}",
            "sha256": feed_sha,
            "topic_id": feed["topic_id"],
            "category": feed["category"],
            "title": feed["title"],
            "caption": caption,
            "org": ORG,
            "handle": SOCIAL_HANDLE,
            "description": "Original educational feed poster; not an event report",
            "ai_generated": False,
            "review_required_for_any_real_world_event": True
        })
    manifest = {
        "source": "basir-social/daily_jihadi_story.py",
        "timezone": "Asia/Tehran",
        "generated_for_start": start.isoformat(),
        "generated_by": "automated design runner",
        "image_format": "JPEG",
        "image_sizes": {"STORY":[1080,1920],"POST":[1080,1350]},
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
