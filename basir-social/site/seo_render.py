"""Build server-visible Persian SEO pages from verified public-only website data.

No keywords stuffing, no copied third-party articles, no generated fake
events, no fabricated ratings/reviews and no individually thin report pages.
The homepage links to crawlable static collection pages rather than relying
exclusively on JavaScript. All outputs stay within the public site folder.
"""
import html
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

ROOT=Path(__file__).resolve().parent
BASE="https://basiryazd.github.io/rozeh-manager/basir-social/site/"
CHANNEL="https://eitaa.com/basiryazd"
SOCIAL=[
    ("ایتا",CHANNEL),
    ("تلگرام","https://t.me/basiryazd"),
    ("اینستاگرام","https://www.instagram.com/basiryazd/"),
]
ORG={"@type":"Organization","name":"قرارگاه جهادی حضرت بقیةالله (عج)",
     "url":CHANNEL,"sameAs":[url for _,url in SOCIAL]}
NAV=[
    ("صفحه نخست",""),("گزارش‌های جهادی","reports.html"),
    ("اخبار نیکوکاری","news.html"),("جهادگران یزد","activities-yazd.html"),
    ("راهنمای داوطلبی","volunteer-guide.html"),("همکاری رسانه‌ای","media-kit.html"),
]
CSS="""
:root{color-scheme:light}*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;color:#243e30;background:#f8f7f2;font-family:Tahoma,Arial,sans-serif;line-height:1.95}
a{color:#15543d;text-decoration:none}a:hover{text-decoration:underline}
a:focus-visible{outline:3px solid #b78e4c;outline-offset:3px}
.wrap{max-width:1070px;width:calc(100% - 36px);margin:auto}
header{background:#fff;border-bottom:1px solid #dce3da}
.nav{display:flex;gap:18px;justify-content:space-between;align-items:center;padding:17px 0;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px}.symbol{display:grid;place-items:center;width:49px;height:49px;background:#134736;color:#e4c77e;border-radius:13px;font-size:24px;font-weight:bold}
.brand strong{display:block;font-size:22px;line-height:1.4}.brand small{display:block;font-size:11px;color:#6d8073}
nav{display:flex;gap:15px;flex-wrap:wrap}nav a{font-size:13px}
.hero{background:linear-gradient(130deg,#205941,#11362b);color:#fff;padding:55px 0}
.hero h1{font-size:clamp(27px,4vw,43px);line-height:1.5;margin:0}
.hero p{font-size:15px;max-width:800px;color:#e2efe7}
.meta{font-size:12px;color:#accfba}.main{padding:40px 0 65px}
.card{background:#fff;border:1px solid #dce5dd;border-radius:17px;padding:25px;margin-bottom:19px;box-shadow:0 5px 20px #1643290d}
.card h2,.card h3{margin:0 0 11px;color:#194734;font-size:21px;line-height:1.65}
.card p{font-size:15px;margin:0 0 15px}
.boxlist{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.notice{padding:15px 19px;background:#eaf1e9;border-right:4px solid #236c4d;border-radius:10px;font-size:14px;margin:21px 0}
.stamp{display:inline-block;border-radius:60px;padding:3px 12px;background:#f0f1e7;color:#536b59;font-size:12px;margin-bottom:12px}
.btn{display:inline-block;border:1px solid #1a6349;border-radius:11px;padding:8px 16px;font-weight:bold;font-size:13px;margin:5px 0}
.tabs{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0 26px}.tabs a{border:1px solid #bed3c4;border-radius:100px;padding:6px 14px;font-size:13px}
ul{padding-right:23px}li{margin-bottom:8px}
footer{background:#143629;color:#e4efe7;padding:30px 0;font-size:13px}
footer a{color:#fff;margin-left:15px}.note{font-size:13px;color:#62786b}
@media(max-width:680px){.boxlist{grid-template-columns:1fr}.hero{padding:36px 0}.main{padding:27px 0 50px}nav{gap:10px}.card{padding:20px}.brand strong{font-size:20px}}
""".strip()

def esc(value):
    return html.escape(str(value or ""),quote=True)

def json_script(payload):
    return '<script type="application/ld+json">'+json.dumps(payload,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")+'</script>'

def webpage(title,description,slug,heading,lede,body,kind="CollectionPage",extra=None):
    url=BASE+slug
    schema={"@context":"https://schema.org","@type":kind,"name":title,
            "inLanguage":"fa-IR","url":url,
            "description":description,"publisher":ORG}
    if extra:
        schema.update(extra)
    nav=''.join(f'<a href="{esc(path or "./")}">{esc(text)}</a>' for text,path in NAV)
    return f"""<!doctype html>
<html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="index,follow,max-image-preview:large">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website"><meta property="og:locale" content="fa_IR">
<meta property="og:site_name" content="بصیر یزد"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" href="feed.xml" title="خوراک خبر و گزارش‌های بصیر یزد">
<meta name="theme-color" content="#134736">
{json_script(schema)}
<style>{CSS}</style></head><body>
<header><div class="wrap nav"><a href="./" class="brand"><span class="symbol">ب</span><span><strong>بصیر یزد</strong><small>قرارگاه جهادی حضرت بقیه الله(عج)</small></span></a>
<nav aria-label="فهرست سایت">{nav}</nav></div></header>
<section class="hero"><div class="wrap"><div class="meta">بصیر یزد | رسانه خدمت و فعالیت‌های جهادی</div>
<h1>{esc(heading)}</h1><p>{esc(lede)}</p></div></section>
<main class="main"><div class="wrap">{body}</div></main>
<footer><div class="wrap"><strong>بصیر یزد | قرارگاه جهادی حضرت بقیه الله(عج)</strong><p>رسانه خدمت و نیکوکاری با پیوند به منبع اصلی؛ بدون انتشار اطلاعات شخصی مددجویان.</p>
{''.join(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>' for label,url in SOCIAL)}</div></footer>
</body></html>"""

def report_section(items):
    intro="""<section class="card"><h2>آرشیو گزارش‌های عمومی فعالیت‌های جهادی و خیریه</h2>
<p>در این صفحه بخشی از پیام‌های عمومی کانال رسمی بصیر یزد به‌صورت خلاصه نمایش داده می‌شود. برای خواندن متن اصلی، تاریخ و رسانه ضمیمه هر گزارش باید به ایتا مراجعه کنید. وجود یک گزارش در این آرشیو به معنی تأیید مستقل ادعاها، مجوز بازنشر تصویر اشخاص یا تأیید مالی نیست.</p>
<p>بصیر یزد گزارش‌های فعالیت جهادی و داوطلبانه را با هدف آشنایی با اقدامات خدمت‌محور یزد و کشور سامان‌دهی می‌کند. مطالب باید قابل ردگیری باشند؛ به همین دلیل لینک پیام اصلی در کنار هر متن وجود دارد.</p>
</section>"""
    cards=[]
    for item in items[:12]:
        mid=str(item.get("message_id",""))
        if not mid.isdigit():
            continue
        if item.get("url")!=f"{CHANNEL}/{mid}":
            continue
        raw=str(item.get("text") or "").strip()
        if len(raw)<35:
            continue
        excerpt=raw[:350]+("…" if len(raw)>350 else "")
        headline="گزارش عمومی بصیر یزد؛ پیام شماره "+mid
        # Preserve the source identity; never fabricate a sensational headline.
        cards.append(f"""<article class="card" id="eitaa-{esc(mid)}">
<span class="stamp">منبع: کانال رسمی بصیر یزد | ایتا</span>
<h2>{esc(headline)}</h2>
<p>{esc(excerpt)}</p>
<a class="btn" href="{esc(item["url"])}" target="_blank" rel="noopener noreferrer">مشاهده اصل گزارش در ایتا</a>
</article>""")
    return intro+'<div class="notice">این فهرست از پیام‌های عمومی تهیه شده و جایگزین بررسی رضایت و حقوق اشخاص در عکس‌ها یا ویدئوها نیست.</div>'+(''.join(cards) if cards else '<p class="card">در حال حاضر گزارش جدیدی برای فهرست عمومی در دسترس نیست. <a href="'+CHANNEL+'">کانال ایتا</a> را ببینید.</p>')

def news_section(items):
    intro="""<section class="card"><h2>رصد خبرهای نیکوکاری و گروه‌های جهادی در یزد و ایران</h2>
<p>برای دنبال‌کردن فعالیت‌های خیریه، گروه‌های جهادی، مراکز نیکوکاری، بسیج سازندگی و مشارکت‌های داوطلبانه، این صفحه عنوان خبرهای مرتبط را با ذکر نام رسانه و لینک اصلی نمایش می‌دهد. متن کامل اخبار متعلق به ناشران اولیه است و در این سایت کپی نمی‌شود.</p>
<p>پیشنهاد می‌کنیم قبل از استناد به هر خبر، تاریخ انتشار و اصل گزارش را در خبرگزاری مربوط بررسی کنید؛ ممکن است جزئیات یک فعالیت پس از انتشار اصلاح شود. در این بخش، خبرهای یزد و کشور کنار هم قرار می‌گیرند.</p></section>"""
    cards=[]
    for item in items[:20]:
        url=str(item.get("url") or "")
        title=str(item.get("title") or "").strip()
        source=str(item.get("source") or "").strip()
        if not url.startswith("https://") or len(title)<18:
            continue
        local="یزد" if item.get("local") else "کشور"
        stamp=source+" · "+local
        date_text=""
        try:
            date_text=datetime.fromisoformat(str(item.get("published"))).date().isoformat()
        except (TypeError,ValueError):
            pass
        cards.append(f"""<article class="card">
<span class="stamp">{esc(stamp)}</span><h2>{esc(title)}</h2>
<p class="note">تاریخ منبع: {esc(date_text or "در خبرگزاری اصلی")} | برای جزئیات و اصلاحات به منبع مراجعه کنید.</p>
<a class="btn" href="{esc(url)}" target="_blank" rel="noopener noreferrer sponsored">مطالعه در خبرگزاری {esc(source)}</a>
</article>""")
    return intro+(''.join(cards) if cards else '<p class="card">فعلاً تیتر منبع‌دار تازه‌ای در این دسته یافت نشده است؛ <a href="https://t.me/basiryazd">خبرخوان تلگرام بصیر</a> را دنبال کنید.</p>')

ACTIVITIES_BODY="""<section class="card"><h2>فعالیت جهادی در یزد چگونه تعریف می‌شود؟</h2>
<p>فعالیت جهادی یا داوطلبانه می‌تواند از آموزش و مهارت‌آموزی تا کمک به رفع نیازهای اجتماعی و پشتیبانی از اقدام‌های محلی را شامل شود. برای شناخت یک برنامه واقعی، باید برگزارکننده، نوع خدمت، محل و تاریخ اعلام‌شده و نتیجه مستند را بررسی کرد. ادعای فعالیت به‌تنهایی سند وقوع یا اثربخشی آن نیست.</p>
<p>در شهرستان‌های استان یزد مانند میبد، اردکان، تفت، مهریز، بافق، ابرکوه و اشکذر نیز ممکن است فعالیت‌های خیریه و داوطلبانه انجام شود. این فهرست جغرافیایی، معرفی یا تأیید یک گروه مشخص نیست؛ اطلاعات هر برنامه فقط با منبع معتبر آن منتشر می‌شود.</p>
</section>
<section class="card"><h2>برای شناخت گروه‌های جهادی یزد به چه نکاتی توجه کنیم؟</h2>
<ul>
<li><strong>منبع قابل پیگیری:</strong> گزارش باید از کانال یا اطلاعیه رسمی و قابل ارجاع باشد، نه یک تصویر بدون مشخصات.</li>
<li><strong>هدف روشن:</strong> مشخص باشد چه نیازی شناسایی شده و قرار است چگونه پاسخ داده شود.</li>
<li><strong>حفظ کرامت:</strong> نام، چهره یا نشانی افراد نیازمند نباید بدون رضایت آگاهانه منتشر شود؛ برای کودکان حساسیت بیشتری لازم است.</li>
<li><strong>شفافیت مالی:</strong> کمک نقدی فقط پس از راستی‌آزمایی هویت برگزارکننده و روش دریافت وجه انجام شود؛ از حساب ناشناس خودداری کنید.</li>
<li><strong>ارزیابی نتیجه:</strong> تعداد افراد یا بسته‌ها تنها شاخص موفقیت نیست؛ اثر اقدام و پیگیری نیازها نیز مهم است.</li>
</ul></section>
<section class="card"><h2>گزارش‌های مستند بصیر یزد و اخبار کار خیر</h2>
<p>در <a href="reports.html">آرشیو گزارش‌های جهادی بصیر یزد</a> می‌توان متن پیام‌های عمومی و پیوند اصل آنها در ایتا را مشاهده کرد. برای اطلاع از خبرهای مستقل استانی و کشوری نیز <a href="news.html">صفحه اخبار نیکوکاری</a> در دسترس است.</p>
<p>اگر مدیر یک گروه داوطلبانه هستید و قصد همکاری رسانه‌ای دارید، از <a href="media-kit.html">صفحه معرفی و همکاری بصیر یزد</a> شروع کنید. انتشار گزارش یا بازنشر ویدئو باید با حقوق اشخاص، مجوز انتشار و مستندات مناسب همراه باشد.</p></section>"""

VOLUNTEER_BODY="""<section class="card"><h2>گام نخست: نوع خدمت متناسب با توان خود را انتخاب کنید</h2>
<p>داوطلبی همیشه به معنای کمک مالی نیست. آموزش مهارت، طراحی پوستر، تدوین گزارش دقیق، پشتیبانی تدارکاتی، پاکیزگی محیط، برگزاری کارگاه یا کمک به فعالیت فرهنگی هم می‌تواند ارزشمند باشد. ابتدا میزان وقت، مهارت و محدودیت‌های خود را مشخص کنید و فعالیتی انتخاب کنید که بتوانید آن را پیگیری کنید.</p>
<p>برای نمونه، دانشجویی که در هفته چند ساعت زمان دارد می‌تواند به آماده‌سازی محتوای آموزشی کمک کند؛ فردی با تجربه فنی شاید در تعمیر وسایل عمومی تحت نظارت یک گروه معتبر مشارکت کند. انتخاب کار باید با نیاز واقعی جامعه و چارچوب برگزارکننده هماهنگ باشد.</p></section>
<section class="card"><h2>چگونه اعتبار یک خیریه یا گروه جهادی را بررسی کنیم؟</h2>
<ul>
<li>نام برگزارکننده و راه ارتباطی رسمی او را از یک منبع مستقل تأیید کنید.</li>
<li>هدف برنامه، مسئول اجرایی، زمان و محل فعالیت را روشن بپرسید.</li>
<li>برای کمک مالی، شفافیت دریافت و مصرف کمک‌ها و اعتبار مقصد پرداخت را بررسی کنید.</li>
<li>در برنامه‌های مرتبط با کودکان یا خانواده‌ها، ضوابط حفاظت از افراد و رضایت برای عکاسی را جویا شوید.</li>
<li>اگر برگزارکننده درباره فعالیت یا هزینه‌ها پاسخ روشنی نمی‌دهد، از تصمیم عجولانه خودداری کنید.</li>
</ul>
<p>بصیر یزد رسانه معرفی خدمت است و صرف انتشار خبر درباره یک مجموعه به معنی ضمانت فعالیت یا دریافت کمک از طرف آن نیست.</p></section>
<section class="card"><h2>حفظ کرامت افراد در کار خیر و انتشار گزارش</h2>
<p>در تهیه گزارش تصویری یا ویدئویی، از نمایش مدارک، نشانی منزل، شماره تماس، وضعیت درمانی یا جزئیات زندگی خصوصی افراد خودداری کنید. انتشار چهره و نام، به‌ویژه درباره افراد زیر سن قانونی، نیازمند بررسی دقیق رضایت و شرایط انتشار است.</p>
<p>گزارش خوب صرفاً نمایش دریافت‌کننده کمک نیست؛ می‌تواند فرآیند نیازسنجی، آماده‌سازی تجهیزات، آموزش داوطلبان و نتیجه خدمت را بدون معرفی افراد آسیب‌پذیر نشان دهد.</p></section>
<section class="card"><h2>چگونه از یک مشارکت کوتاه‌مدت، خدمت پایدار بسازیم؟</h2>
<p>برای ادامه‌دار شدن همکاری، از ابتدا وظیفه و زمان‌بندی مشخص داشته باشید. پس از اجرای برنامه، با رعایت حریم خصوصی بپرسید آیا نیازهای اصلی برطرف شده‌اند یا خیر. یادگیری از نتیجه، انجام مسئولانه کار و حفظ اعتماد از تعداد عکس‌های منتشرشده مهم‌تر است.</p>
<p>می‌توانید برای آشنایی با نمونه گزارش‌ها به <a href="reports.html">آرشیو بصیر یزد</a> مراجعه کنید و خبرهای مرتبط با گروه‌های جهادی را در <a href="news.html">بخش اخبار نیکوکاری</a> دنبال کنید.</p></section>
<section class="card"><h2>پرسش‌های رایج درباره داوطلبی</h2>
<h3>آیا برای مشارکت در کار جهادی باید پول پرداخت کنیم؟</h3><p>خیر. شکل مشارکت می‌تواند مهارتی، اجرایی یا آموزشی باشد. درباره هر درخواست مالی، هویت و اعتبار برگزارکننده را پیش از پرداخت بررسی کنید.</p>
<h3>آیا هر گزارش منتشرشده به معنی تأیید رسمی گروه است؟</h3><p>خیر. گزارش یا خبر باید همراه با منبع خوانده شود و تأیید مستقل فعالیت یک گروه نیازمند بررسی جداگانه است.</p>
<h3>چطور درباره فعالیت‌های جهادی یزد اطلاعات پیدا کنیم؟</h3><p>صفحه <a href="activities-yazd.html">فعالیت‌های جهادی یزد</a> چارچوب ارزیابی را توضیح می‌دهد و آرشیو گزارش‌ها شما را به پیام‌های اصلی کانال بصیر هدایت می‌کند.</p>
</section>"""

def render_static(data):
    reports=report_section(data.get("reports",[]))
    news=news_section(data.get("news",[]))
    output={
      "reports.html":webpage(
        "گزارش فعالیت‌های جهادی و خیریه در یزد | بصیر یزد",
        "آرشیو گزارش‌های عمومی بصیر یزد از فعالیت‌های جهادی و نیکوکاری؛ متن خلاصه با لینک مستقیم به منبع اصلی ایتا و رعایت حریم خصوصی.",
        "reports.html","گزارش فعالیت‌های جهادی بصیر یزد",
        "گزارش‌های عمومی قابل پیگیری از کانال رسمی بصیر یزد، همراه با پیوند اصل هر پیام.",reports),
      "news.html":webpage(
        "اخبار نیکوکاری یزد و ایران؛ گروه‌های جهادی و خیرین | بصیر یزد",
        "تیتر خبرهای مرتبط با خیریه، نیکوکاری، گروه‌های جهادی و سازندگی در یزد و ایران؛ منابع: مهر، ایسنا، تسنیم و فارس در صورت دسترسی.",
        "news.html","اخبار نیکوکاری و گروه‌های جهادی",
        "خبرهای مرتبط با خدمت و سازندگی در یزد و کشور، با نام خبرگزاری و لینک مستقیم به خبر اصلی.",news),
      "activities-yazd.html":webpage(
        "گروه‌های جهادی یزد؛ فعالیت‌ها و راهنمای بررسی گزارش‌ها | بصیر یزد",
        "برای شناخت فعالیت گروه‌های جهادی یزد، اخبار خیریه، اعتبار گزارش‌ها و روش همکاری داوطلبانه، راهنمای رسانه بصیر یزد را بخوانید.",
        "activities-yazd.html","فعالیت‌های جهادی و نیکوکاری در یزد",
        "راهنمای بررسی گزارش‌های گروه‌های جهادی یزد و آشنایی با شیوه‌های خدمت مسئولانه، همراه با پیوند به منابع واقعی.",
        ACTIVITIES_BODY,kind="Article",
        extra={"datePublished":"2026-11-06","dateModified":"2026-11-06",
               "author":ORG,"headline":"گروه‌های جهادی یزد؛ راهنمای ارزیابی فعالیت و گزارش"}),
      "volunteer-guide.html":webpage(
        "راهنمای کار داوطلبانه و کمک به خیریه در یزد | بصیر یزد",
        "راهنمای کاربردی برای شروع فعالیت داوطلبانه، بررسی اعتبار خیریه‌ها، حفظ کرامت مددجویان و مشارکت پایدار در کار جهادی یزد.",
        "volunteer-guide.html","راهنمای مشارکت داوطلبانه در کار خیر",
        "از انتخاب فعالیت متناسب با توان خود تا ارزیابی اعتبار خیریه و گزارش مسئولانه از خدمت.",
        VOLUNTEER_BODY,kind="Article",
        extra={"datePublished":"2026-11-06","dateModified":"2026-11-06",
               "author":ORG,"headline":"راهنمای مشارکت داوطلبانه و کمک مسئولانه"})
    }
    for name,body in output.items():
        write_if_changed(ROOT/name,body)
    return list(output)

def write_if_changed(path,text):
    if not path.is_file() or path.read_text(encoding="utf8")!=text:
        path.write_text(text,encoding="utf8")
        return True
    return False

def render_sitemap(data):
    static=["","reports.html","news.html","activities-yazd.html",
            "volunteer-guide.html","media-kit.html"]
    modified=str(data.get("updated_at") or "2026-11-06")[:10]
    if not re.fullmatch(r"20\\d{2}-\\d{2}-\\d{2}",modified):
        modified="2026-11-06"
    urls=Element("urlset",{"xmlns":"http://www.sitemaps.org/schemas/sitemap/0.9"})
    for slug in static:
        url=SubElement(urls,"url")
        SubElement(url,"loc").text=BASE+slug
        SubElement(url,"lastmod").text=modified if slug in ("","reports.html","news.html") else "2026-11-06"
    xml=b'<?xml version="1.0" encoding="UTF-8"?>\\n'+tostring(urls,encoding="utf-8")+b"\\n"
    write_if_changed(ROOT/"sitemap.xml",xml.decode("utf-8"))
    # RSS serves as a supplemental discovery feed, not a copy of news articles.
    root=Element("rss",{"version":"2.0"})
    channel=SubElement(root,"channel")
    for tag,value in [("title","بصیر یزد | خبر و گزارش خدمت"),("link",BASE),
                      ("description","عنوان گزارش‌های عمومی بصیر یزد و خبرهای دارای منبع"),
                      ("language","fa-ir")]:
        SubElement(channel,tag).text=value
    for record in data.get("reports",[])[:12]:
        mid=str(record.get("message_id",""))
        if not mid.isdigit() or record.get("url")!=CHANNEL+"/"+mid:continue
        item=SubElement(channel,"item")
        SubElement(item,"title").text="گزارش عمومی بصیر یزد | پیام "+mid
        SubElement(item,"link").text=BASE+"reports.html#eitaa-"+mid
        SubElement(item,"guid",{"isPermaLink":"false"}).text="basiryazd:eitaa:"+mid
        SubElement(item,"description").text=str(record.get("text") or "")[:240]
    for record in data.get("news",[])[:10]:
        title=str(record.get("title") or "").strip()
        source=str(record.get("source") or "").strip()
        url=str(record.get("url") or "")
        if not title or not url.startswith("https://"):continue
        item=SubElement(channel,"item")
        SubElement(item,"title").text=title+" | "+source
        SubElement(item,"link").text=url
        SubElement(item,"guid",{"isPermaLink":"false"}).text="basiryazd:news:"+url
        SubElement(item,"description").text="گزیده پیوند به خبرگزاری اصلی "+source
    write_if_changed(ROOT/"feed.xml",
        (b'<?xml version="1.0" encoding="UTF-8"?>\\n'+tostring(root,encoding="utf-8")+b"\\n").decode("utf-8"))

def main():
    data=json.loads((ROOT/"content.json").read_text(encoding="utf8"))
    pages=render_static(data)
    render_sitemap(data)
    print("SEO_BUILD_OK","static_indexable_pages",len(pages)+2,
          "source_reports",len(data.get("reports",[])),
          "source_news",len(data.get("news",[])))

if __name__=="__main__":
    main()
