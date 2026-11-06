"""Premium, photo-led Basir Yazd editorial variants — no fabricated reportage.

Sources: Wikimedia Commons photos with author/license references. All captions
and rendered copy are reviewed for truthful, conceptual/editorial framing.
The public image outputs are NOT Instagram publication receipts.
"""
import hashlib,io,json,os,sys,time
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from PIL import Image,ImageDraw,ImageFont,ImageOps,features

DEST=Path("basir-social/site/assets/premium")
DEST.mkdir(parents=True,exist_ok=True)
W=1080
CREAM=(248,246,239);DARK=(19,58,47);GREEN=(27,76,61);GOLD=(186,150,91)
FONT_B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
if not features.check("raqm"):
    raise RuntimeError("Requires RAQM for proper Persian shaping")

TOPICS=[
    {"id":"volunteer","image":"A windcatcher and skylights.jpg","author":"Rayeshman",
     "license":"CC BY-SA 4.0","license_url":"https://creativecommons.org/licenses/by-sa/4.0/",
     "page":"https://commons.wikimedia.org/wiki/File:A_windcatcher_and_skylights.jpg",
     "tag":"همکاری داوطلبانه | یزد","title":["توانایی تو،","راهی برای خدمت"],"detail":"آموزش | رسانه | فعالیت جهادی | پشتیبانی",
     "cta":"فرم همکاری در سایت بصیر یزد"},
    {"id":"reports","image":"Yazd's windcatchers - panoramio.jpg","author":"Alen Ištoković",
     "license":"CC BY 3.0","license_url":"https://creativecommons.org/licenses/by/3.0/",
     "page":"https://commons.wikimedia.org/wiki/File:Yazd%27s_windcatchers_-_panoramio.jpg",
     "tag":"رسانه قابل اعتماد","title":["خبر مستند،","روایت روشن"],"detail":"گزارش‌های اصلی فعالیت‌های مردمی، همراه با منبع",
     "cta":"گزارش‌های بصیر یزد را دنبال کنید"},
    {"id":"yazd","image":"OWNED_CONCEPTUAL_YAZD","author":"Basir Yazd original conceptual art",
     "license":"Original in-house conceptual illustration","license_url":"https://basiryazd.github.io/rozeh-manager/basir-social/site/",
     "page":"https://basiryazd.github.io/rozeh-manager/basir-social/site/assets/volunteer-campaign-1080x1350.jpg",
     "tag":"مشارکت اجتماعی","title":["یزد،","شهر همدلی"],"detail":"از علاقه و مهارت خود برای کمک داوطلبانه استفاده کنیم",
     "cta":"در جریان خدمت همراه شوید"},
]

def f(sz,bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R,sz,layout_engine=ImageFont.Layout.RAQM)
def draw_rtl(draw,word,x,y,size,color,bold=False):
    font=f(size,bold)
    left=draw.textbbox((0,0),word,font=font,direction="rtl",language="fa")[0]
    draw.text((x,y),word,fill=color,font=font,anchor="ra",direction="rtl",language="fa")
def photo_file(item):
    if item["image"]=="OWNED_CONCEPTUAL_YAZD":
        path=Path("basir-social/site/assets/volunteer-campaign-1080x1350.jpg")
        if not path.is_file():
            raise RuntimeError("Owned conceptual reference art unavailable")
        print("OWNED_CONCEPTUAL_SOURCE",item["id"],str(path),flush=True)
        # Only the unobstructed lower city illustration; exclude old generated copy.
        with Image.open(path) as input_image:
            img=input_image.convert("RGB")
            return img.crop((0,665,1080,995)).copy()
    name=quote(item["image"],safe="")
    url="https://commons.wikimedia.org/wiki/Special:FilePath/"+name
    req=Request(url,headers={"User-Agent":"BasirYazdOpenMedia/1.0 (website basiryazd.github.io); community editorial asset"})
    data=None
    for attempt in range(4):
        try:
            with urlopen(req,timeout=55) as r:
                final=r.geturl()
                data=r.read(9*1024*1024+1)
                mime=r.headers.get("content-type","")
            break
        except HTTPError as exc:
            if exc.code!=429 or attempt==3:
                raise
            wait=12*(attempt+1)
            print("SOURCE_PHOTO_RATE_LIMIT",item["id"],"retry_after_seconds",wait,flush=True)
            time.sleep(wait)
    if data is None:
        raise RuntimeError("Licensed source download returned no bytes")
    if len(data)>9*1024*1024 or len(data)<30000:
        raise RuntimeError("licensed source size outside allowed range")
    img=Image.open(io.BytesIO(data))
    if img.width<680 or img.height<680:
        raise RuntimeError("licensed source too small")
    if img.format not in ("JPEG","PNG","WEBP"):
        raise RuntimeError("unexpected photo encoding")
    print("LICENSED_PHOTO",item["id"],img.size,mime,final.split("?")[0][:160])
    return img.convert("RGB")
def photo_block(img,w,h):
    return ImageOps.fit(img,(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.5))
def overlay(image,col,top=0,opacity=0):
    image=image.convert("RGBA")
    over=Image.new("RGBA",image.size,(0,0,0,0))
    d=ImageDraw.Draw(over)
    for y in range(image.height):
        p=y/max(image.height-1,1)
        alpha=int(opacity*(p**1.5))
        d.line((0,y,image.width,y),fill=(*col,alpha))
    return Image.alpha_composite(image,over).convert("RGB")
def layout(item,original,format):
    if format=="STORY":width,height=1080,1920
    else:width,height=1080,1350
    dark=item["id"]=="reports"
    bg=DARK if dark else CREAM
    ink=(246,247,234) if dark else DARK
    accent=GOLD if dark else GREEN
    out=Image.new("RGB",(width,height),bg)
    d=ImageDraw.Draw(out)
    photo_start=670 if format=="STORY" else 540
    photo_height=970 if format=="STORY" else 610
    d.rectangle((0,0,1080,12),fill=GOLD if dark else GREEN)
    draw_rtl(d,"بصیر یزد",1010,55,49,ink,True)
    draw_rtl(d,"قرارگاه جهادی حضرت بقیه الله (عج)",1010,135,25,ink)
    draw_rtl(d,item["tag"],1007,242,30,GOLD if dark else (133,98,43))
    title_size=92 if format=="STORY" else 83
    base=330 if format=="STORY" else 319
    for i,word in enumerate(item["title"]):
        draw_rtl(d,word,1007,base+i*(title_size+48),title_size,ink,True)
    # Natural large photograph; no graphic frames, repetitive stripes or invented event photos.
    hero=photo_block(original,1080,photo_height)
    hero=overlay(hero,DARK,opacity=85 if not dark else 55)
    out.paste(hero,(0,photo_start))
    d=ImageDraw.Draw(out)
    foot=photo_start+photo_height
    d.rectangle((0,foot,1080,height),fill=DARK)
    draw_rtl(d,item["detail"],1007,foot+54,27,(241,238,221))
    draw_rtl(d,item["cta"],1007,foot+139,38,(245,215,161),True)
    draw_rtl(d,"@basiryazd",1007,foot+224,32,(252,251,245),True)
    # Avoid suggesting that this generic architectural image documents a recent charity action.
    source_label=("تصویرسازی مفهومی اختصاصی | گزارش میدانی نیست" if item["image"]=="OWNED_CONCEPTUAL_YAZD" else "طرح مفهومی | عکس معماری یزد با مجوز بازنشر")
    draw_rtl(d,source_label,1007,height-82,20,(215,220,203))
    credit=(("عکس: "+item["author"]+" | "+item["license"]+" | Wikimedia Commons")
            if item["image"]!="OWNED_CONCEPTUAL_YAZD" else "تصویرسازی اختصاصی بصیر یزد")
    draw_rtl(d,credit,1007,height-45,18,(213,218,198))
    return out
results=[]
for topic in TOPICS:
    time.sleep(4)  # respect public media hosting; no burst downloads
    img=photo_file(topic)
    for kind in ("STORY","POST"):
        name=topic["id"]+"-"+("story-1080x1920" if kind=="STORY" else "feed-1080x1350")+".jpg"
        out=layout(topic,img,kind)
        output=DEST/name
        out.save(output,"JPEG",quality=92,optimize=True,subsampling=0)
        info={"id":topic["id"],"kind":kind,"file":name,
          "size":[out.width,out.height],"sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
          "design":"PREMIUM_PHOTO_EDITORIAL_V2",
          "source_photo":topic["page"],"author":topic["author"],
          "license":topic["license"],"license_url":topic["license_url"],
          "approval":"private_preview_only_until_brand_visual_review",
          "reportage":False}
        results.append(info)
        print("NEW_PREMIUM_CREATIVE",name,"bytes",output.stat().st_size)
manifest={"version":2,"owner_rejected_sources":["basir-social/public_media/manifest.json"],
 "generated":"2026-11-06","publication":"PREVIEW_NOT_PUBLISHED",
 "visual_family":"Premium photo-led editorial; distinct concepts; no old geometric template",
 "items":results}
(DEST/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
(DEST/"LICENSES.md").write_text(
 "# Licensed photo credits\n\n"+ "\n".join(
  "- "+x["id"]+": "+x["author"]+" · "+x["page"]+" · "+x["license"]+
  " · "+x["license_url"] for x in TOPICS)+"\n\nThe designs adapt licensed photographs with typography; keep the attributed source and conditions when sharing. The photos are architectural/editorial, not images of real charitable actions.\n",
 encoding="utf8")
print("PREMIUM_RENDER_OK",len(results),"owner review required before auto publish")
