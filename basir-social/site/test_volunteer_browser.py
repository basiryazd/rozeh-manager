"""Browser-level checks of volunteer form during third-party 522 outages.

No real applicant information and NO external POST: FormSubmit requests
are intercepted by Playwright. This tests both outage and success paths.
"""
from playwright.sync_api import sync_playwright
import shutil

BASE="http://127.0.0.1:8765/"

def fill(page):
    page.locator("#name").fill("آزمون نمونه")
    page.locator("#contact").fill("test@example.invalid")
    page.locator("#city").fill("یزد")
    page.locator("input[type=checkbox][value='رسانه، خبر و گزارش‌نویسی']").evaluate("(el)=>{el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}))}")
    page.locator("input[type=radio][value='هفتگی']").check()
    page.locator("input[name='رضایت_برای_ارتباط']").check()

def main():
    chrome=shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("google-chrome-stable")
    if not chrome:
        raise RuntimeError("Chrome not installed; test not passed")
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=chrome,headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
        ctx=browser.new_context(viewport={"width":390,"height":844},is_mobile=True,has_touch=True)
        page=ctx.new_page()
        errors=[]
        page.on("pageerror",lambda exc: errors.append(str(exc)))
        def outage(route):
            route.fulfill(status=522,content_type="text/html",body="<h1>Connection timed out</h1>")
        page.route("https://formsubmit.co/**",outage)
        response=page.goto(BASE+"volunteer.html",wait_until="domcontentloaded")
        assert response.status==200,response.status
        fill(page)
        page.locator("#submitButton").evaluate("(el)=>el.click()")
        page.locator("#emailFallback").wait_for(state="visible",timeout=12000)
        assert page.url==BASE+"volunteer.html",page.url
        assert page.locator("#name").input_value()=="آزمون نمونه"
        assert "پاسخ تأییدشده نداد" in page.locator("#submitStatus").inner_text()
        href=page.locator("#emailFallback").get_attribute("href")
        assert href.startswith("mailto:basiryazd@gmail.com?"),href[:120]
        assert not errors,errors
        print("VOLUNTEER_522_SAFE_FALLBACK_OK",flush=True)
        # Mock a successful provider acceptance; success remains the only confirmation.
        page.unroute_all()
        page.route("https://formsubmit.co/**",
                   lambda route:route.fulfill(status=200,content_type="application/json",
                     headers={"Access-Control-Allow-Origin":"*"},
                     body='{"success":true}'))
        page.locator("#submitButton").click()
        page.wait_for_url(BASE+"volunteer-thanks.html",timeout=12000)
        assert "سپاسگزاریم" in page.locator("body").inner_text()
        print("VOLUNTEER_CONFIRMED_SUBMISSION_REDIRECT_OK",flush=True)
        browser.close()

if __name__=="__main__":
    main()
