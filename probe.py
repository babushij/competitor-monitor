import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    br=p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
    ctx=br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900},locale="en-US")
    pg=ctx.new_page()
    reqs=[]
    def onresp(r):
        try:
            ct=r.headers.get("content-type","")
            if r.request.resource_type in ("xhr","fetch") or "json" in ct:
                body=""
                try: body=r.text()
                except: pass
                reqs.append((r.status,r.request.method,r.url[:200],ct[:30],len(body),len(set(VIN.findall(body))),body[:200]))
        except Exception as e: pass
    pg.on("response",onresp)
    pg.on("console",lambda m: print("CONSOLE",m.type,m.text[:200]) if m.type in ("error",) else None)
    pg.goto("https://www.nag-cars.com/inventory",wait_until="load",timeout=90000)
    pg.wait_for_timeout(20000)
    pg.mouse.wheel(0,3000); pg.wait_for_timeout(5000)
    for x in reqs: print("REQ",x)
    t=pg.inner_text("body"); print("TEXTLEN",len(t),t[:500])
    h=pg.content(); print("SCRIPTS",re.findall(r'<script[^>]+src="([^"]+)"',h)[:15])
    print("HTMLHEAD",h[:1500])
