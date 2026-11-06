"""Premium photo-led Basir Yazd campaign, never a fabricated field report.

No geometric frames, no text-box ornaments, no reused legacy templates.
Uses an owned conceptual Yazd city illustration already present in the site.
This generator prepares art only; platform publication requires an exact review.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"site/assets/volunteer-campaign-1080x1350.jpg"
OUT=ROOT/"site/assets/premium"
DARK=(12,48,38)
IVORY=(248,245,237)
GOLD=(223,181,99)
WHITE=(254,253,247)
FONT_DIR=Path("/usr/share/fonts/truetype/noto")
BOLD=FONT_DIR/"NotoSansArabic-Bold.ttf"
REGULAR=FONT_DIR/"NotoSansArabic-Regular.ttf"

TOPICS=[
    {"date":"2026-11-07","slug":"hamrahi","kind":"دعوت به همکاری",
     "title":["در مسیر خدمت،","همراه شو"],
     "body":"برای همراهی در آموزش، رسانه، فعالیت‌های مردمی و کار جهادی، اعلام آمادگی کن.",
     "accent":GOLD,"shift":0},
    {"date":"2026-11-09","slug":"maharat","kind":"مهارت برای خدمت",
     "title":["یک مهارت،","یک فرصت برای خیر"],
     "body":"هر توانایی می‌تواند راهی برای خدمت به مردم و مشارکت مسئولانه باشد.",
     "accent":(186,217,184),"shift":28},
    {"date":"2026-11-13","slug":"jomemahdavi","kind":"جمعه مهدوی",
     "title":["جمعه؛ فرصتی","برای مهربانی"],
     "body":"یک کار خیر کوچک و محترمانه به نیت حضرت ولی‌عصر (عج) انتخاب کنیم.",
     "accent":GOLD,"shift":65}
]
WEB="basiryazd.github.io/rozeh-manager/basir-social/site/"
CTA="فرم همکاری و رسانه‌های رسمی در سایت بصیر یزد"

def font(size,bold=False):
    file=BOLD if bold else REGULAR
    if not file.exists():
        raise RuntimeError("Install fonts-noto-core; no font fallback for public assets")
    return ImageFont.truetype(str(file),size)

def rtl(d,s,x,y,size,color,bold=False):
    d.text((x,y),s,anchor="ra",direction="rtl",font=font(size,bold),fill=color,stroke_width=0)

def blend_photo(source,canvas,w,top,bottom,offset=0):
    """Use only image pixels from an owned conceptual skyline, not its old lettering."""
    # A clean lower 300px photographic skyline region free of old campaign headlines.
    photo=source.crop((0,695+offset,1080,990+min(offset,6)))
    from PIL import ImageOps
    photo=ImageOps.fit(photo,(w,bottom-top),method=Image.Resampling.LANCZOS,centering=(.5,.53))
    photo=ImageEnhance.Contrast(photo).enhance(1.11)
    photo=ImageEnhance.Color(photo).enhance(.89)
    canvas.paste(photo,(0,top))
    # Photo merges into uninterrupted dark editorial panel (no frames).
    px=canvas.load()
    h=bottom-top
    for y in range(top,bottom):
        f=(y-top)/max(1,h)
        t=max(0,min(1,(f-.65)/.35))
        t=t*t*(3-2*t)
        if t<=0: continue
        alpha=.91*t
        for x in range(w):
            p=px[x,y]
            px[x,y]=tuple(int(p[k]*(1-alpha)+DARK[k]*alpha) for k in range(3))

def render(topic,mode,source):
    is_story=(mode=="story")
    w,h=(1080,1920) if is_story else (1080,1350)
    page=Image.new("RGB",(w,h),IVORY)
    d=ImageDraw.Draw(page)
    # Stable premium brand bar: no circles, repeated polygons, or ornamental borders.
    rtl(d,"بصیر یزد",1002,84,62,DARK,True)
    rtl(d,"قرارگاه جهادی حضرت بقیه الله(عج)",1002,134,27,(74,89,77))
    d.text((58,107),"@basiryazd",font=font(30,True),fill=DARK,anchor="lm",direction="ltr")
    top=185 if is_story else 162
    end=1295 if is_story else 891
    blend_photo(source,page,w,top,end,topic["shift"])
    d=ImageDraw.Draw(page)
    # Edge-to-edge editorial color block. Larger title and small readable subhead.
    base=1130 if is_story else 812
    d.rectangle((0,base,w,h),fill=DARK)
    kicker_y=1230 if is_story else 900
    rtl(d,topic["kind"],1002,kicker_y,37,topic["accent"],True)
    title_y=kicker_y+120
    for line in topic["title"]:
        rtl(d,line,1002,title_y,82 if is_story else 68,WHITE,True)
        title_y+=119 if is_story else 91
    body_y=title_y+42
    words=topic["body"].split()
    lines=[]
    line=""
    for word in words:
        test=(line+" "+word).strip()
        trial=ImageDraw.Draw(page).textbbox((0,0),test,font=font(34 if is_story else 29),direction="rtl")
        if line and trial[2]>910:
            lines.append(line)
            line=word
        else:
            line=test
    if line:lines.append(line)
    for line in lines:
        rtl(d,line,1002,body_y,34 if is_story else 29,(232,239,229))
        body_y+=57 if is_story else 48
    foot=h-190 if is_story else h-142
    rtl(d,"با ما همراه شوید",1002,foot,38,topic["accent"],True)
    rtl(d,CTA,1002,foot+53,26,WHITE)
    d.text((56,h-76),"@basiryazd",anchor="lm",direction="ltr",font=font(30,True),fill=WHITE)
    rtl(d,"تصویرسازی مفهومی • نه گزارش میدانی",1002,h-74,21,(187,202,186))
    filename=f"{topic['date']}-{topic['slug']}-{mode}-"+("1080x1920" if is_story else "1080x1350")+".jpg"
    path=OUT/filename
    page.save(path,"JPEG",quality=94,optimize=True,subsampling=0)
    return {"date":topic["date"],"slug":topic["slug"],"mode":mode,
            "file":filename,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "size":[w,h],"reviewed":False,"publication_allowed":False,
            "image_source":"Owned conceptual Yazd skyline art from volunteer campaign",
            "editorial_kind":"CONCEPTUAL_NOT_FIELD_REPORT"}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    with Image.open(SOURCE) as im: source=im.convert("RGB")
    if source.size!=(1080,1350): raise RuntimeError("Base conceptual campaign asset missing or wrong size")
    items=[render(t,mode,source) for t in TOPICS for mode in ("post","story")]
    (OUT/"manifest.json").write_text(json.dumps({
        "version":1,"source":"generate_premium_campaign.py",
        "publisher_mode":"DRAFT_ONLY_AWAITING_EXACT_OWNER_STYLE_AND_IMAGE_APPROVAL",
        "items":items},ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("PREMIUM_PREVIEWS_CREATED",len(items),"exact owner approval required")
if __name__=="__main__": main()
