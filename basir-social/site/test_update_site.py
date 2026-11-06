"""Safeguards for public-only website mirror."""
import unittest
from datetime import datetime,timezone
from update_site import extract_public_ids,parse_exact_report,parse_rss,safe_https

class SiteTests(unittest.TestCase):
    def test_only_real_channel_ids(self):
        doc='<div data-post="basiryazd/3350"></div><div data-post="other/3351"></div><div data-post="basiryazd/3349"></div>'
        self.assertEqual(extract_public_ids(doc),["3350","3349"])
    def test_exact_channel_caption_and_personal_data_hold(self):
        doc='<div data-post="basiryazd/3350"><div class="tgme_widget_message_text">گزارش فعالیت گروه جهادی بصیر یزد در محله و کمک به خانواده‌های نیازمند</div></div>'
        a=parse_exact_report(doc,"3350")
        self.assertEqual(a["message_id"],"3350")
        self.assertIsNone(parse_exact_report(doc,"3349"))
        self.assertIsNone(parse_exact_report(doc.replace("نیازمند","نیازمند شماره تماس 09123456789"),"3350"))
    def test_news_only_attributed_and_topic_bounded(self):
        from email.utils import format_datetime
        now=datetime.now(timezone.utc)
        xml='<rss><channel><item><title>فعالیت گروه جهادی برای کمک به نیازمندان یزد</title><link>https://www.mehrnews.com/news/1234567/example</link><pubDate>'+format_datetime(now)+'</pubDate></item><item><title>خبر کوتاه سیاسی نامرتبط</title><link>https://evil.com/x</link><pubDate>'+format_datetime(now)+'</pubDate></item></channel></rss>'
        items=parse_rss("خبرگزاری مهر",xml.encode(),("www.mehrnews.com",),now)
        self.assertEqual(len(items),1)
        self.assertTrue(items[0]["local"])
    def test_https_allowlist(self):
        self.assertTrue(safe_https("https://eitaa.com/basiryazd/3350",("eitaa.com",)))
        self.assertFalse(safe_https("https://evil.com/x",("eitaa.com",)))
        self.assertFalse(safe_https("http://eitaa.com/x",("eitaa.com",)))
if __name__=="__main__":unittest.main()
