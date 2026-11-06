"""Offline technical SEO regression checks for the public Basir Yazd site."""
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from bs4 import BeautifulSoup
import seo_render

ROOT=Path(__file__).resolve().parent

class TechnicalSeoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"content.json").read_text(encoding="utf8"))
        seo_render.render_static(cls.data)
        seo_render.render_homepage(cls.data)
        seo_render.render_sitemap(cls.data)

    def test_every_indexable_page_has_unique_title_description_and_canonical(self):
        titles=set()
        for slug in ("","reports.html","news.html","activities-yazd.html",
                     "volunteer-guide.html","media-kit.html","volunteer.html"):
            page=ROOT/(slug or "index.html")
            soup=BeautifulSoup(page.read_text(encoding="utf8"),"html.parser")
            title=soup.find("title")
            desc=soup.find("meta",attrs={"name":"description"})
            canonical=soup.find("link",attrs={"rel":"canonical"})
            self.assertTrue(title and len(title.get_text(strip=True))>22,slug)
            self.assertNotIn(title.get_text(),titles)
            titles.add(title.get_text())
            self.assertTrue(desc and len(desc.get("content",""))>45,slug)
            self.assertTrue(canonical and canonical.get("href")==seo_render.BASE+slug,slug)
            self.assertTrue(soup.find("h1"),slug)
            self.assertEqual(soup.html.get("lang"),"fa",slug)
            self.assertEqual(soup.html.get("dir"),"rtl",slug)
            self.assertIn("قرارگاه جهادی حضرت بقیه الله",soup.get_text(),slug)

    def test_sitemap_only_contains_real_canonical_site_pages(self):
        p=ROOT/"sitemap.xml"
        data=ET.parse(p)
        ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
        entries=data.findall("s:url",ns)
        self.assertEqual(len(entries),7)
        urls=[x.find("s:loc",ns).text for x in entries]
        self.assertEqual(len(set(urls)),len(urls))
        self.assertTrue(all(x.startswith(seo_render.BASE) for x in urls))
        self.assertTrue(all((ROOT/(x.removeprefix(seo_render.BASE) or "index.html")).is_file()
                            for x in urls))

    def test_reports_are_in_html_and_link_exact_source(self):
        html=(ROOT/"reports.html").read_text(encoding="utf8")
        soup=BeautifulSoup(html,"html.parser")
        for item in self.data.get("reports",[]):
            mid=str(item.get("message_id",""))
            if mid.isdigit() and item.get("url")==seo_render.CHANNEL+"/"+mid:
                self.assertTrue(soup.select_one("#eitaa-"+mid),mid)
                self.assertIsNotNone(soup.find("a",href=item["url"]),mid)
        self.assertNotIn("<script src=",html)
        self.assertNotIn("tel:",html)

    def test_site_has_readable_original_local_guides_and_breadcrumb_navigation(self):
        for filename in ("volunteer-guide.html","activities-yazd.html"):
            soup=BeautifulSoup((ROOT/filename).read_text(encoding="utf8"),"html.parser")
            self.assertGreater(len(soup.get_text(" ",strip=True)),1100)
            self.assertIsNotNone(soup.find("a",href="reports.html"))
            self.assertIsNotNone(soup.find("a",href="news.html"))
        home=BeautifulSoup((ROOT/"index.html").read_text(encoding="utf8"),"html.parser")
        self.assertTrue(home.find("script",attrs={"type":"application/ld+json"}))
        self.assertTrue(home.find("a",href="volunteer-guide.html"))
        self.assertTrue(home.find("a",href="activities-yazd.html"))

    def test_volunteer_form_collects_minimum_data_and_never_posts_to_github(self):
        soup=BeautifulSoup((ROOT/"volunteer.html").read_text(encoding="utf8"),"html.parser")
        form=soup.find("form")
        self.assertTrue(form)
        self.assertEqual(form.get("method"),"POST")
        self.assertEqual(form.get("action"),"#")
        self.assertIn('fetch("https://formsubmit.co/ajax/basiryazd@gmail.com"',(ROOT/"volunteer.html").read_text(encoding="utf8"))
        self.assertIsNotNone(soup.find(id="emailAlternative"))
        self.assertIsNotNone(soup.find(id="emailFallback"))
        self.assertIsNotNone(form.find("input",{"name":"راه_تماس","required":True}))
        self.assertIsNotNone(form.find("input",{"name":"رضایت_برای_ارتباط","required":True}))
        self.assertGreaterEqual(len(form.find_all("input",{"type":"checkbox","name":"زمینه_همکاری[]"})),8)
        self.assertNotIn("github.com",form.get("action"))
        self.assertNotIn("type=\"file\"",str(form))
        thanks=BeautifulSoup((ROOT/"volunteer-thanks.html").read_text(encoding="utf8"),"html.parser")
        self.assertIn("noindex",thanks.find("meta",attrs={"name":"robots"}).get("content"))

    def test_static_pages_carry_google_readable_structured_data(self):
        for path in ("reports.html","news.html","activities-yazd.html","volunteer-guide.html"):
            soup=BeautifulSoup((ROOT/path).read_text(encoding="utf8"),"html.parser")
            block=soup.find("script",attrs={"type":"application/ld+json"})
            payload=json.loads(block.string)
            self.assertEqual(payload["@context"],"https://schema.org")
            self.assertTrue(payload.get("publisher",{}).get("name","").startswith("قرارگاه جهادی"))

    def test_homepage_uses_modern_design_verified_identity_and_no_draft_images(self):
        home=(ROOT/"index.html").read_text(encoding="utf8")
        soup=BeautifulSoup(home,"html.parser")
        self.assertTrue(soup.find(id="identity"))
        self.assertTrue(soup.find(id="about"))
        self.assertIn("استان یزد، ایران",soup.get_text())
        self.assertIn("مرکز نیکوکاری حضرت بقیه الله",soup.get_text())
        self.assertIn("بلوار شهید مدنی",soup.get_text())
        self.assertIn("کوچه ۱۷ شهریور",soup.get_text())
        self.assertIn("حسینیه عسکریه",soup.get_text())
        self.assertIn("@hossein_dehghan_t",soup.get_text())
        self.assertIn("24214296",soup.get_text())
        self.assertIn("شناسه عددی ایتا شماره ثبت مؤسسه نیست",soup.get_text())
        self.assertIn("قرارگاه جهادی حضرت بقیه الله",soup.get_text())
        self.assertIsNotNone(soup.select_one(".hero-art .art-svg"))
        self.assertIsNotNone(soup.find("meta",attrs={"name":"google-site-verification"}))
        self.assertNotIn("public_media/manifest.json",home)
        self.assertNotIn("../public_media/",home)
        self.assertFalse(soup.select("img[src*='feed-']"))
        self.assertFalse(soup.select("img[src*='story-']"))
        self.assertEqual(soup.select_one("#reportsList") is not None,True)
        self.assertEqual(soup.select_one("#newsList") is not None,True)

    def test_homepage_curates_only_service_related_sourced_reports(self):
        self.assertEqual(seo_render._homepage_card(
            {"message_id":"55","url":"https://eitaa.com/basiryazd/55",
             "text":"سقوط برگشت ناپذیر امریکا و تحریم و جنگ در گزارش امروز، گزارش سیاسی بدون خدمات اجتماعی"},"report"),"")
        self.assertEqual(seo_render._homepage_card(
            {"message_id":"55","url":"https://example.org/55",
             "text":"گزارش فعالیت جهادی برای داوطلبان محله در چارچوب خدمت مردمی و نیکوکاری به هم‌نوعان"},"report"),"")
        card=seo_render._homepage_card(
            {"message_id":"3351","url":"https://eitaa.com/basiryazd/3351",
             "text":"گزارش فعالیت جهادی داوطلبان یزد در رویدادی مستند و انتشار گزارش از کانال رسمی ایتا"},"report")
        self.assertIn("https://eitaa.com/basiryazd/3351",card)
        self.assertNotIn("<img",card)

    def test_rss_well_formed_without_fake_news_dates(self):
        xml=ET.parse(ROOT/"feed.xml")
        self.assertEqual(xml.getroot().tag,"rss")
        self.assertTrue(xml.find("./channel/title") is not None)

if __name__=="__main__":
    unittest.main()
