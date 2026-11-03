"""Cost-free daily Jihadi and charitable-work Story designs (private previews only).

These are education and invitations to volunteer, NEVER invented reports of
real events. Religious calendar Stories and genuine Eitaa reports are separate.
The workflow does not publish or consume Bundle Social monthly credits.
"""
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo
from math import pi, sin, cos
from PIL import Image,ImageDraw,ImageFont

TEHRAN=ZoneInfo("Asia/Tehran")
ORG="قرارگاه جهادی حضرت بقیةالله (عج)"
MEDIA="بصیر یزد | @basiryazd"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Pre-reviewed evergreen educational copy, not fabricated news or results.
# Different points of a 28-day rotation keep weekdays from repeating weekly.
TOPICS=[
 ("کمک مؤمنانه","خیرخواهی از همین امروز","برای کمک به یک خانواده، ابتدا نیاز واقعی آن‌ها را با احترام جویا شویم."),
 ("خدمت جهادی","شنیدن، آغاز خدمت است","پیش از هر برنامه جهادی، از مردم همان محله درباره اولویت‌هایشان بپرسیم."),
 ("فرهنگ انفاق","کمک با حفظ کرامت","کمک‌رسانی نباید به انتشار چهره یا اطلاعات شخصی دریافت‌کنندگان وابسته باشد."),
 ("آموزش داوطلبی","از توانایی خود شروع کنیم","آموزش، تعمیر، مشاوره و همراهی؛ هر مهارت می‌تواند راهی برای خدمت باشد."),
 ("انتظار و مسئولیت","منتظرِ اهل عمل باشیم","یکی از نیازهای کوچک اطرافمان را پیدا کنیم و برای رفع آن قدمی برداریم."),
 ("همدلی اجتماعی","کار خیر تیمی اثرگذار است","کارهای داوطلبانه را با تقسیم وظایف روشن و احترام به وقت یکدیگر پیش ببریم."),
 ("شفافیت جهادی","گزارش درست، اعتماد می‌سازد","در گزارش فعالیت‌ها فقط اقدام‌های انجام‌شده و نتایج قابل تأیید را بیان کنیم."),
 ("کمک مؤمنانه","پیش از تهیه بسته، نیازسنجی","محتوای بسته حمایتی را متناسب با نیاز خانواده و شرایط محلی انتخاب کنیم."),
 ("خدمت جهادی","خدمت، ادامه می‌خواهد","پس از پایان برنامه، از مخاطبان بپرسیم آیا نیازهای اصلی برطرف شده است."),
 ("فرهنگ انفاق","احترام مهم‌تر از تصویر است","در روایت کار خیر، از نمایش وضعیت دشوار زندگی افراد بدون رضایت پرهیز کنیم."),
 ("آموزش داوطلبی","برای خدمت مهارت بیاموزیم","یک مهارت کاربردی را انتخاب کنیم و برای آموزش آن به دیگران وقت بگذاریم."),
 ("مهدویت","انتظار و مهربانی","امروز با یک رفتار مسئولانه و مهربانانه، محیط اطرافمان را بهتر کنیم."),
 ("همراهی مردم","مشارکت محلی ارزشمند است","از ظرفیت همسایه‌ها و گروه‌های محلی با هماهنگی و رضایت کمک بگیریم."),
 ("کار جهادی","ایمنی، مقدمه خدمت","قبل از فعالیت میدانی، ابزار مناسب و ایمنی داوطلبان را بررسی کنیم."),
 ("کمک مؤمنانه","کمکِ به‌موقع و دقیق","نیازهای فوری را از نیازهای بلندمدت جدا کنیم تا منابع بهتر به کار گرفته شوند."),
 ("گزارش مسئولانه","برای هر عکس اجازه بگیریم","رضایت آگاهانه برای عکاسی و انتشار تصاویر افراد را جدی بگیریم."),
 ("خدمت جهادی","با مردم، نه به‌جای مردم","برای برنامه‌ریزی فعالیت، تجربه و نظر ساکنان محله را در نظر بگیریم."),
 ("فرهنگ انفاق","کمک بی‌منت زیباتر است","در یاری‌رساندن، از هر نوع برخوردی که احساس شرمندگی ایجاد می‌کند دوری کنیم."),
 ("آموزش داوطلبی","وظیفه روشن، خدمت بهتر","پیش از شروع فعالیت گروهی، نقش‌ها و مسئولیت‌ها را دقیق مشخص کنیم."),
 ("انتظار و خدمت","از یک قدم کوچک آغاز کنیم","همراهی با سالمندان و رسیدگی محترمانه به همسایه‌ها هم بخشی از مسئولیت اجتماعی است."),
 ("همدلی اجتماعی","مشارکت، اعتماد می‌خواهد","درباره هدف و شیوه استفاده از کمک‌های داوطلبانه شفاف اطلاع‌رسانی کنیم."),
 ("خدمت جهادی","نتیجه را با مردم بسنجیم","بعد از اجرای برنامه، بازخورد دریافت‌کنندگان خدمت را بشنویم."),
 ("کمک مؤمنانه","کمک پایدار، مسئولانه","برای حمایت طولانی‌مدت، برنامه‌ای واقع‌بینانه و متناسب با توان مجموعه تدوین کنیم."),
 ("آموزش داوطلبی","خوش‌قولی جزئی از خدمت است","به زمانی که برای فعالیت و همراهی با دیگران قول داده‌ایم پایبند باشیم."),
 ("مهدویت","مسئولیت‌پذیری در عمل","انتظار را با صداقت، رعایت حقوق مردم و خدمت داوطلبانه همراه کنیم."),
 ("فرهنگ انفاق","نیاز واقعی را بشناسیم","کمک مؤثر از گفت‌وگوی محترمانه با افراد و شناخت اولویت‌های آنان آغاز می‌شود."),
 ("گزارش جهادی","از اغراق فاصله بگیریم","تعداد فعالیت‌ها و دستاوردها را فقط وقتی منتشر کنیم که قابل تأیید باشند."),
 ("خدمت اجتماعی","نیکی را ادامه دهیم","هر هفته یک اقدام کوچک، مشخص و قابل انجام برای خیر عمومی انتخاب کنیم."),
]

# Friday (weekday 4) always focuses on Imam Mahdi (aj) and a specific
# voluntary charitable action. Rotate distinct actions weekly; never describe
# proposed charity as an event the organization has already carried out.
FRIDAY_TOPICS=[
 ("جمعه مهدوی","جمعه؛ به یاد امام زمان (عج)","به نیت سلامتی و تعجیل در فرج حضرت، امروز یک بسته خوراکی به خانواده‌ای نیازمند برسانیم."),
 ("انتظار و خدمت","یک کار خیر به نیت امام زمان (عج)","این جمعه به نیت حضرت ولی‌عصر (عج)، با حفظ احترام به فردی سالمند یا تنها کمک کنیم."),
 ("جمعه‌های امید","جمعه؛ روز مهربانی و انتظار","به نیت امام زمان (عج)، هزینه یک وعده غذا را به فردی نیازمند هدیه کنیم."),
 ("مهدویت و مسئولیت","منتظر واقعی، اهل خدمت است","این جمعه به نیت تعجیل در فرج، یک ساعت از وقت خود را برای کار خیر داوطلبانه بگذاریم."),
 ("جمعه مهدوی","یک قدم کوچک برای رضایت خدا","به نیت سلامتی امام زمان (عج)، نیاز واقعی یک خانواده را با احترام جویا شویم و کمک کنیم."),
 ("فرهنگ انتظار","دعای فرج و یک کار خیر","این جمعه پس از دعا برای فرج، به نیت حضرت به یک نیازمند بی‌منت یاری برسانیم."),
]

def choose_topic(day):
    """Return category, title, action, art index. Friday always uses Mahdavi copy."""
    if day.weekday()==4:
        week_index=(day.toordinal()//7)%len(FRIDAY_TOPICS)
        return (*FRIDAY_TOPICS[week_index], 4+week_index)
    index=(day.toordinal()+7)%len(TOPICS)
    return (*TOPICS[index],index)

PALETTES=[
 ((12,50,63),(4,96,94),(250,234,192),(242,250,243)),
 ((42,31,72),(76,55,110),(234,199,139),(254,247,228)),
 ((35,49,37),(72,94,61),(241,212,143),(248,247,231)),
 ((55,41,46),(124,68,67),(244,201,154),(249,247,234)),
 ((17,49,79),(44,92,117),(222,195,143),(253,248,230)),
 ((43,49,69),(96,77,95),(229,202,164),(252,248,239)),
 ((8,74,67),(40,106,86),(234,216,164),(250,249,230)),
]

def _font(size,bold=False):
    return ImageFont.truetype(BOLD if bold else FONT,size)

def _lines(draw,message,font,max_width,max_lines=4):
    answer=[]
    line=""
    for word in str(message).split():
        trial=(line+" "+word).strip()
        if line and draw.textbbox((0,0),trial,font=font,direction="rtl")[2]>max_width:
            answer.append(line)
            line=word
        else:
            line=trial
    if line:answer.append(line)
    if len(answer)>max_lines:
        raise ValueError("Unreviewed daily Story text would not fit its canvas")
    return answer

def _center(draw,text,y,font,fill):
    draw.text((540,y),text,font=font,anchor="mm",fill=fill,direction="rtl")

def design(day,path):
    """Return an original vertical 1080x1920 educational Story image."""
    if isinstance(day,datetime):
        day=day.astimezone(TEHRAN).date()
    if not isinstance(day,date):
        raise TypeError("A local calendar date is required")
    category,title,detail,topic_id=choose_topic(day)
    top,bottom,highlight,white=PALETTES[(topic_id//2+topic_id)%len(PALETTES)]
    w,h=1080,1920
    im=Image.new("RGB",(w,h))
    d=ImageDraw.Draw(im)
    for y in range(h):
        ratio=y/(h-1)
        d.line((0,y,w,y),fill=tuple(int(top[k]*(1-ratio)+bottom[k]*ratio) for k in range(3)))
    variant=topic_id%4
    if variant==0:
        for radius in (225,350,485):
            d.arc((540-radius,1035-radius,540+radius,1035+radius),190,352,fill=highlight,width=4)
        d.ellipse((350,1060,730,1440),outline=highlight,width=9)
    elif variant==1:
        for k in range(10):
            x=90+k*95
            d.line((x,1280,x+110,1570),fill=highlight,width=2 if k%2 else 4)
        d.rounded_rectangle((80,890,1000,1430),radius=42,outline=highlight,width=4)
    elif variant==2:
        for k in range(12):
            a=2*pi*k/12
            r=230
            x=540+cos(a)*r
            y=1270+sin(a)*r
            d.ellipse((x-9,y-9,x+9,y+9),fill=highlight)
        d.arc((198,930,882,1614),20,285,fill=highlight,width=7)
    else:
        for j in range(6):
            y=1110+j*61
            d.rounded_rectangle((130+j*22,y,950-j*22,y+9),radius=4,fill=highlight)
        d.arc((225,885,855,1515),170,340,fill=highlight,width=6)
    d.rounded_rectangle((53,63,1027,1858),radius=44,outline=highlight,width=3)
    d.line((190,260,890,260),fill=highlight,width=3)
    _center(d,ORG,180,_font(34,True),white)
    _center(d,"جمعه مهدوی | پیشنهاد یک کار خیر" if day.weekday()==4 else "روایت فرهنگ خدمت | استوری آموزشی",385,_font(39),highlight)
    _center(d,category,580,_font(47,True),highlight)
    title_font=_font(70,True)
    title_lines=_lines(d,title,title_font,890,3)
    y=740-(len(title_lines)-1)*50
    for line in title_lines:
        _center(d,line,y,title_font,white)
        y+=111
    msg_font=_font(40)
    msg_lines=_lines(d,detail,msg_font,780,4)
    start=1050
    # Readable text on an opaque-ish contrasting solid panel.
    d.rounded_rectangle((105,965,975,965+110*(len(msg_lines)+1)),radius=28,
                        fill=top,outline=highlight,width=3)
    for line in msg_lines:
        _center(d,line,start,msg_font,white)
        start+=86
    _center(d,"خدمت به مردم، با احترام و صداقت",1650,_font(30,True),highlight)
    _center(d,"بصیر یزد",1735,_font(32,True),white)
    d.text((540,1795),"@basiryazd",font=_font(34,True),anchor="mm",fill=white,direction="ltr")
    _center(d,"طرح آموزشی؛ نه گزارش یک رویداد واقعی",1840,_font(22),highlight)
    output=Path(path)
    output.parent.mkdir(parents=True,exist_ok=True)
    im.save(output,"JPEG",quality=94,subsampling=0)
    return {"path":output,"topic_id":topic_id,"category":category,
            "title":title,"date":day.isoformat(),"friday_mahdavi":day.weekday()==4,
            "suggested_charity":detail if day.weekday()==4 else None,
            "kind":"EDUCATIONAL_NOT_AN_EVENT_REPORT"}

def main():
    import json,os
    today=datetime.now(TEHRAN).date()
    override=os.environ.get("DAILY_STORY_DATE","").strip()
    if override:
        today=date.fromisoformat(override)
    folder=Path("publication-previews/daily-jihadi")
    item=design(today,folder/f"jihadi-{today.isoformat()}.jpg")
    manifest={k:(str(v) if isinstance(v,Path) else v) for k,v in item.items()}
    manifest["publication"]="PRIVATE_PREVIEW_ONLY"
    manifest["requires_real_source_for_event_reports"]=True
    manifest["instagram_api_calls"]=0
    (folder/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n","utf8")
    print("Daily original, non-event educational Story prepared:",manifest["title"],today)
    print("PRIVATE PREVIEW ONLY: never sent to Instagram and consumed zero publishing credits.")

if __name__=="__main__":
    main()
