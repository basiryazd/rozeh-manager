"""Mobile browser tests of Basir volunteer intake.

No real applicant information; all potentially external requests intercepted.
Verify safe email fallback and separately simulate real 2xx and 522 outcomes.
"""
from playwright.sync_api import sync_playwright
from urllib.parse import unquote
import shutil

BASE="http://127.0.0.1:8765/"

def fill(page):
    page.locator("#name").fill("آزمون نمونه")
    page.locator("#contact").fill("test@example.invalid")
    page.locator("#city").fill("یزد")
    page.locator("input[type=checkbox][value='رسانه، خبر و گزارش‌نویسی']").check(force=True)
    page.locator("input[type=radio][value='هفتگی']").check()
    page.locator("input[name='رضایت_برای_ارتباط']").check()

def main():
    chrome=shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("google-chrome-stable")
    if not chrome:
        raise RuntimeError("Chrome not installed; no browser QA result")
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chrome,headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx=browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
        page=ctx.new_page()
        errors=[]
        external=[]
        page.on("pageerror",lambda e: errors.append(str(e)))
        page.on("request",lambda r: external.append(r.url) if "formsubmit.co" in r.url or "formspree.io" in r.url else None)
        response=page.goto(BASE+"volunteer.html",wait_until="networkidle")
        assert response.status==200
        assert page.locator("#deliveryNotice").inner_text().find("ایمیل")>=0
        fill(page)
        page.locator("#submitButton").click(force=True)
        page.locator("#emailFallback").wait_for(state="visible",timeout=4000)
        href=unquote(page.locator("#emailFallback").get_attribute("href"))
        assert href.startswith("mailto:basiryazd@gmail.com?"),href[:80]
        assert "test@example.invalid" in href
        assert page.locator("#copyFallback").is_visible()
        assert page.url==BASE+"volunteer.html"
        assert not external,external
        assert not errors,errors
        print("VOLUNTEER_UNCONFIGURED_EMAIL_FALLBACK_PASS",flush=True)
        # Fake a configured, verified form ID and simulate acceptance entirely locally.
        def config(route):
            route.fulfill(status=200,content_type="application/json",
                body='{"provider":"formspree","endpoint":"https://formspree.io/f/abcdefg"}')
        page.route("**/volunteer-delivery-config.json",config)
        page.route("https://formspree.io/f/abcdefg",
            lambda route: route.fulfill(status=200,content_type="application/json",
                 headers={"Access-Control-Allow-Origin":"*"},body='{"ok":true}'))
        page.goto(BASE+"volunteer.html",wait_until="networkidle")
        assert "ارسال امن" in page.locator("#submitButton").inner_text()
        fill(page)
        page.locator("#submitButton").click(force=True)
        page.wait_for_url(BASE+"volunteer-thanks.html",timeout=9000)
        assert "سپاسگزاریم" in page.locator("body").inner_text()
        print("VOLUNTEER_MOCK_CONFIRMED_PROVIDER_ACCEPTANCE_PASS",flush=True)
        page.unroute_all()
        page.route("**/volunteer-delivery-config.json",config)
        page.route("https://formspree.io/f/abcdefg",
            lambda route: route.fulfill(status=522,content_type="text/html",
                 headers={"Access-Control-Allow-Origin":"*"},body="<h1>Connection timed out</h1>"))
        page.goto(BASE+"volunteer.html",wait_until="networkidle")
        fill(page)
        page.locator("#submitButton").click(force=True)
        page.locator("#emailFallback").wait_for(state="visible",timeout=9000)
        assert "تأیید قطعی" in page.locator("#submitStatus").inner_text()
        assert page.url==BASE+"volunteer.html"
        print("VOLUNTEER_MOCK_522_NO_FALSE_SUCCESS_PASS",flush=True)
        browser.close()

if __name__=="__main__":
    main()
