"""Public-only Basir Yazd news/media site updater.

No tokens, logins, media downloads, personal records or fabricated events.
Source reports require exact public @basiryazd message links.
Third-party news is never copied: only a title and publisher hyperlink.
"""
import json
import re
import html
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT/"content.json"
UA={"User-Agent":"BasirYazd-PublicNewsSite/1.0 (+https://eitaa.com/basiryazd)"}
EITAA_HOST="eitaa.com"
CHANNEL="basiryazd"
FEEDS={
    "خبرگزاری مهر":("https://www.mehrnews.com/rss",("mehrnews.com","www.mehrnews.com")),
    "خبرگزاری ایسنا":("https://www.isna.ir/rss",("isna.ir","www.isna.ir")),
    "خبرگزاری تسنیم":("https://www.tasnimnews.ir/fa/rss/feeds/6/0/0/0",("tasnimnews.ir","www.tasnimnews.ir","tasnimnews.com","www.tasnimnews.com")),
    "خبرگزاری فارس":("https://farsnews.ir/rss",("farsnews.ir","www.farsnews.ir")),
}
TOPICS=("یزد","بسیج سازندگی","جهادگران","گروه جهادی","گروه‌های جهادی","اردوی جهادی",
        "خیریه","نیکوکاری","نیکوکار","خیرین","محرومیت زدایی","محرومیت‌زدایی",
        "مرکز نیکوکاری","مراکز نیکوکاری","کمک مؤمنانه","کمک مومنانه","کمیته امداد",
        "بسیج سازندگی","خدمت جهادی","خدمت‌رسانی","مجمع جهادگران","آزادی زندانیان غیرعمد",
        "داوطلبی","مشارکت اجتماعی")
SERVICE_TERMS=tuple(x for x in TOPICS if x!="یزد")
LOCAL=("یزد","اردکان","میبد","ابرکوه","تفت","مهریز","اشکذر","بافق","خاتم","مروست")
EXCLUDE=("انتخابات","حمله نظامی","سلاح","موشک","جنگ","تحریم","دستگیری","حوادث امنیتی")
SENSITIVE=re.compile(
    r"(?<!\d)09\d{9}(?!\d)|(?:\+98|0098)9\d{9}|(?<!\d)\d{13,19}(?!\d)|"
    r"کد\s*ملی|نشانی\s*منزل|شماره\s*حساب|شماره\s*کارت|پرونده\s*پزشکی|"
    r"شماره\s*تماس\s*شخصی",
    re.IGNORECASE,
)

def clean(text, limit=2100):
    return " ".join(html.unescape(re.sub(r"<[^>]+>"," ",str(text or ""))).split())[:limit]

def safe_https(url, allowed):
    try:
        p=urlparse(url)
        return p.scheme=="https" and p.hostname in allowed and not p.username and not p.password
    except Exception:
        return False

def extract_public_ids(page, channel=CHANNEL):
    soup=BeautifulSoup(page,"html.parser")
    found=set()
    for node in soup.select("[data-post]"):
        value=node.get("data-post","")
        m=re.fullmatch(re.escape(channel)+r"/(\d{2,15})",str(value))
        if m:
            found.add(m.group(1))
    return sorted(found,key=int,reverse=True)

def parse_exact_report(page, mid):
    soup=BeautifulSoup(page,"html.parser")
    node=soup.find(attrs={"data-post":f"{CHANNEL}/{mid}"})
    if node is None:
        return None
    section=node.select_one(".tgme_widget_message_text, .tgme_widget_message_caption, [class*='message_text'], [class*='message_caption']")
    if section is None:
        return None
    text=clean(section.get_text(" ",strip=True),1700)
    if len(text)<35 or SENSITIVE.search(text):
        return None
    # Public text only; never scrape/embed photos, faces, clips or documents.
    return {"message_id":mid,"text":text,"url":f"https://eitaa.com/{CHANNEL}/{mid}","source":"ایتا | بصیر یزد"}

def fetch_reports(session,previous):
    urls=(f"https://eitaa.com/{CHANNEL}?embed=1",f"https://eitaa.com/s/{CHANNEL}?embed=1")
    ids=set()
    for url in urls:
        try:
            res=session.get(url,timeout=(8,20),headers=UA,allow_redirects=False)
            if res.status_code!=200 or len(res.content)>2_000_000:
                continue
            ids.update(extract_public_ids(res.text))
        except requests.RequestException:
            continue
    results=[]
    for mid in sorted(ids,key=int,reverse=True)[:18]:
        try:
            res=session.get(f"https://eitaa.com/{CHANNEL}/{mid}?embed=1",
                            timeout=(8,17),headers=UA,allow_redirects=False)
            if res.status_code!=200 or len(res.content)>1_000_000:
                continue
            record=parse_exact_report(res.text,mid)
            if record:
                results.append(record)
        except requests.RequestException:
            continue
    # Never erase previously verified public content during source outages.
    return results[:12] if results else previous

def parse_rss(source,raw,hosts,now):
    root=ET.fromstring(raw)
    found=[]
    for item in root.findall("./channel/item")[:120]:
        title=clean(item.findtext("title"),220)
        url=(item.findtext("link") or "").strip()
        date=(item.findtext("pubDate") or "").strip()
        if not (22<=len(title)<=190 and safe_https(url,hosts)):
            continue
        lower=title.casefold()
        if not any(t.casefold() in lower for t in SERVICE_TERMS):
            continue
        if any(word.casefold() in lower for word in EXCLUDE):
            continue
        try:
            published=parsedate_to_datetime(date)
            if published.tzinfo is None:
                continue
            published=published.astimezone(timezone.utc)
        except (ValueError,TypeError,IndexError,OverflowError):
            continue
        if not timedelta(minutes=0)<=now-published<=timedelta(days=7):
            continue
        found.append({"title":title,"url":url,"source":source,
                      "published":published.isoformat(),"local":any(x in title for x in LOCAL)})
    return found

def fetch_news(session,previous):
    now=datetime.now(timezone.utc)
    items=[]
    for source,(url,hosts) in FEEDS.items():
        try:
            res=session.get(url,timeout=(8,20),headers=UA,allow_redirects=True)
            if not (res.status_code==200 and safe_https(res.url,hosts) and len(res.content)<=2_000_000):
                continue
            items.extend(parse_rss(source,res.content,hosts,now))
        except (requests.RequestException,ET.ParseError,ValueError):
            continue
    seen=set()
    unique=[]
    for v in sorted(items,key=lambda x:x["published"],reverse=True):
        key=v["url"].split("#")[0]
        if key not in seen:
            seen.add(key)
            unique.append(v)
    if unique:
        # A blend of regional and national service reporting.
        local=[a for a in unique if a["local"]][:7]
        national=[a for a in unique if not a["local"]][:9]
        return sorted(local+national,key=lambda x:x["published"],reverse=True)[:16]
    return previous

def build(previous, reports, news):
    # Keep the old timestamp when a run did not discover any change.
    old={k:previous.get(k,[]) for k in ("reports","news")}
    new={"reports":reports,"news":news}
    return {"source":"verified public @basiryazd and attributed RSS titles",
            "timezone":"Asia/Tehran",
            "updated_at":(datetime.now(timezone.utc).isoformat()
                          if new!=old else previous.get("updated_at")),
            **new}

def main():
    try:
        previous=json.loads(OUTPUT.read_text(encoding="utf8"))
    except (OSError,json.JSONDecodeError):
        previous={"reports":[],"news":[]}
    session=requests.Session()
    reports=fetch_reports(session,previous.get("reports",[]))
    news=fetch_news(session,previous.get("news",[]))
    result=build(previous,reports,news)
    encoded=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if not OUTPUT.exists() or encoded!=OUTPUT.read_text(encoding="utf8"):
        OUTPUT.write_text(encoded,encoding="utf8")
        print("SITE_UPDATED",len(reports),"source_reports",len(news),"attributed_headlines")
    else:
        print("SITE_UNCHANGED",len(reports),"source_reports",len(news),"attributed_headlines")

if __name__=="__main__":
    main()
