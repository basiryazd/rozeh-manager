"""Premium photographic educational media for Basir Yazd.

No fabricated reports. Unlike retired daily_jihadi_story / generate_media sources,
this makes photo-led, readable, distinct editorial art with attribution.
Produces only reviewed/draft-hosted assets, not social API calls.
"""
import hashlib, io, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request,urlopen
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter

BASE=Path(__file__).parent / "site" / "assets" / "premium"
BASE.mkdir(parents=True,exist_ok=True)
DARK="#10392d"; CREAM="#f7f4eb"; GOLD="#c59b65"; WHITE="#fffdf5"; SOFT="#d4e2d5"
USER_AGENT="BasirYazdEditorial/1.0 (https://basiryazd.github.io/rozeh-manager/basir-social/site/; basiryazd@gmail.com)"
SOURCES=[
 {"file":"Yazd - Badgir - Windcatcher - panoramio.jpg","author":"Alireza Javaheri","license":"CC BY 3.0","license_url":"https://creativecommons.org/licenses/by/3.0/"},
 {"file":"Badgier.jpg","author":"Original Flickr photographer (see source record)","license":"CC BY 2.0","license_url":"https://creativecommons.org/licenses/by/2.0/"}
]
CASES=[
 ("2026-11-06","feed","پست دعوت به کار خیر",["هر مهارتی","می‌تواند آغاز","یک خدمت باشد"],"آموزش • رسانه • فعالیت جهادی • پشتیبانی","volunteer.html",0),
 ("2026-11-07","feed","رسانه مسئولانه",["خبر معتبر","از منبع","قابل پیگیری"],"خبرهای نیکوکاری و سازندگی یزد و ایران","news.html",1),
 ("2026-11-08","story","اخلاق خدمت",["اول کرامت","بعد روایت"],"تصویر و اطلاعات افراد فقط با رعایت رضایت و حریم خصوصی","volunteer-guide.html",0),
 ("2026-11-10","story","همکاری رسانه‌ای",["خدمت، وقتی","درست روایت","شود دیده می‌شود"],"همکاری رسانه‌های مردمی و گروه‌های جهادی با رضایت دوطرفه","media-kit.html",1),
 ("2026-11-12","story","بصیر یزد | روایت خدمت",["از یزد","تا ایران","کنار هم"],"گزارش معتبر، خبر منبع‌دار و همراهی داوطلبانه","reports.html",0),
 ("2026-11-13","feed","جمعه مهدوی",["یک قدم کوچک","برای مهربانی"],"به نیت امام زمان (عج)، یک کار خیرِ واقعی انتخاب کنیم.","volunteer.html",1),
 ("2026-11-11","feed","دعوت به همراهی",["سهم تو از خدمت","می‌تواند","یک مهارت باشد"],"فرم اعلام آمادگی داوطلبان در سایت بصیر یزد","volunteer.html",0)
]
def fetch(url,timeout=32):
 req=Request(url,headers={"User-Agent":USER_AGENT,"Accept":"image/jpeg,image/*;q=0.8,application/json;q=0.5"})
 with urlopen(req,timeout=timeout) as r:
  blob=r.read(14*1024*1024+1)
  if len(blob)>14*1024*1024:raise RuntimeError("image too large")
  return blob
def load_photo(src):
 name=src["file"]
 api="https://commons.wikimedia.org/w/api.php?"+urlencode({"action":"query","titles":"File:"+name,"prop":"imageinfo","iiprop":"url","format":"json"})
 trials=[]
 try:
  data=json.loads(fetch(api))
  page=next(iter(data["query"]["pages"].values()))
  url=page["imageinfo"][0]["url"]
  trials.append(url)
 except Exception as exc:
  print("WIKIMEDIA_API_CANDIDATE",name,type(exc).__name__)
 trials.append("https://commons.wikimedia.org/wiki/Special:FilePath/"+quote(name))
 for url in trials:
  try:
   payload=fetch(url)
   img=Image.open(io.BytesIO(payload))
   if img.format not in ("JPEG","PNG") or min(img.size)<600:
    raise ValueError("source image too small or not raster")
   img=ImageOps.exif_transpose(img).convert("RGB")
   print("LICENSED_IMAGE_OK",name,img.size,src["license"])
   return img
  except Exception as exc:
   print("LICENSED_IMAGE_RETRY",name,type(exc).__name__)
 raise RuntimeError("Licensed Yazd photograph unavailable: "+name)
def font(sz,bold=False):
 paths=([
  "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else [
  "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
 for file in paths:
  if Path(file).exists():return ImageFont.truetype(file,sz,layout_engine=ImageFont.Layout.RAQM)
 raise RuntimeError("No Arabic-compatible font is installed")
def rtl(draw,s,x,y,sz,color,bold=False):
 f=font(sz,bold)
 box=draw.textbbox((x,y),s,font=f,anchor="ra",direction="rtl",language="fa")
 if box[0]<28 or box[2]>1080 or box[1]<0:
  raise RuntimeError(f"Persian title overflows canvas: {s!r} {box}")
 draw.text((x,y),s,font=f,anchor="ra",direction="rtl",language="fa",fill=color)
def image_crop(img,size):
 return ImageOps.fit(img,size,method=Image.Resampling.LANCZOS,centering=(.5,.45)).filter(ImageFilter.GaussianBlur(.28))
def gradient(img,top_alpha=0,bottom_alpha=170):
 w,h=img.size
 over=Image.new("RGBA",img.size);draw=ImageDraw.Draw(over)
 for y in range(h):
  a=int(top_alpha+(bottom_alpha-top_alpha)*(y/max(1,h-1))**1.5)
  draw.line((0,y,w,y),fill=(8,45,33,a))
 return Image.alpha_composite(img.convert("RGBA"),over).convert("RGB")
def build(day,kind,kicker,heading,desc,cta,srcidx,photos):
 story=kind=="story"; W=1080;H=1920 if story else 1350
 img=Image.new("RGB",(W,H),CREAM)
 # Variation A: cream typography above architectural photography.
 # Variation B: full-height photo + green opaque text region, no repeat borders.
 mode=srcidx
 if mode==0:
  photo_y=760 if story else 725
  ph=H-photo_y-220
  img.paste(gradient(image_crop(photos[srcidx],(W,ph)),0,50),(0,photo_y))
  d=ImageDraw.Draw(img)
  d.rectangle((0,0,W,13),fill=DARK)
  rtl(d,"بصیر یزد",1000,64,54,DARK,True)
  rtl(d,"قرارگاه جهادی حضرت بقیه الله(عج)",1000,144,25,DARK)
  rtl(d,kicker,1000,268 if story else 246,32,GOLD)
  top=368 if story else 351
  fs=91 if story else 78
  for i,line in enumerate(heading):
   rtl(d,line,1000,top+i*(118 if story else 103),fs,DARK,True)
  d.rectangle((0,H-220,W,H),fill=DARK)
  rtl(d,desc[:85],1000,H-181,29,WHITE)
  rtl(d,"اطلاعات و مشارکت: سایت بصیر یزد",1000,H-112,30,GOLD,True)
  rtl(d,"@basiryazd  |  تصویر معماری یزد، تزئینی",1000,H-45,21,SOFT)
 else:
  y=0;ph=780 if story else 570
  img.paste(image_crop(photos[srcidx],(W,ph)),(0,0))
  d=ImageDraw.Draw(img);d.rectangle((0,ph,W,H),fill=DARK)
  rtl(d,"بصیر یزد",1000,ph+65,49,WHITE,True)
  rtl(d,"قرارگاه جهادی حضرت بقیه الله(عج)",1000,ph+144,24,SOFT)
  rtl(d,kicker,1000,ph+248,32,GOLD)
  top=ph+329;fs=91 if story else 79
  for i,line in enumerate(heading):
   rtl(d,line,1000,top+i*(120 if story else 102),fs,WHITE,True)
  rtl(d,desc[:85],1000,H-206,27,SOFT)
  rtl(d,"سایت و شبکه‌های بصیر یزد: @basiryazd",1000,H-121,29,GOLD,True)
  rtl(d,"تصویر معماری یزد، تزئینی",1000,H-51,20,SOFT)
 filename=f"premium-{day}-{kind}.jpg"
 path=BASE/filename
 img.save(path,"JPEG",quality=93,optimize=True,subsampling=0)
 with Image.open(path) as check:
  assert check.size==(W,H) and check.format=="JPEG"
 return {"date":day,"kind":kind.upper(),"file":filename,"path":"basir-social/site/assets/premium/"+filename,
  "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"kicker":kicker,"title":" ".join(heading),
  "description":desc,"destination":cta,"approved_for_publication":False,
  "publisher_mode":"CREATIVE_REVIEW_REQUIRED","source_photo":SOURCES[srcidx]}
def main():
 photos=[load_photo(x) for x in SOURCES]
 result=[build(*entry,photos) for entry in CASES]
 assert len(result)==7
 assert len({x["sha256"] for x in result})==7
 output={"status":"NEW_PREMIUM_DRAFTS_NOT_SOCIAL_PUBLISHED","requires_owner_design_signoff":True,
  "images_are_illustrative_architecture_not_real_operation_reports":True,
  "production_source":"basir-social/premium_editorial.py","updated_utc":datetime.now(timezone.utc).isoformat(),
  "items":result}
 (BASE/"manifest.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n","utf8")
 lines=["# Credits — Yazd architectural photographs","These images are editorial photo composites, NOT visual evidence of Basir field operations.",""]
 for p in SOURCES:
  lines.extend(["- "+p["file"]+" — "+p["author"]+" — "+p["license"],
   "  "+p["license_url"],"  https://commons.wikimedia.org/wiki/File:"+quote(p["file"]), ""])
 (BASE/"PHOTO_CREDITS.md").write_text("\n".join(lines),"utf8")
 print("PREMIUM_CREATIVE_ASSETS_OK",len(result),"draft_only=True")
if __name__=="__main__":main()
