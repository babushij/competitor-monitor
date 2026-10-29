import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    br=p.chromium.launch(args=["--disable-blink-features=AutomationControlled"])
    ctx=br.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900},locale="en-US")
    pg=ctx.new_page()
    pg.goto("https://www.nag-cars.com/",wait_until="load",timeout=90000); pg.wait_for_timeout(10000)
    h=pg.content(); b=h[h.find("<body"):]
    print("HOME TEXTLEN",len(pg.inner_text("body")))
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    print("LINKS",[l for l in links if "nag-cars" in l][:60])
    pg.goto("https://www.nag-cars.com/inventory",wait_until="load",timeout=90000); pg.wait_for_timeout(10000)
    h=pg.content(); b=h[h.find("<body"):]
    print("INVBODY",re.sub(r"<script.*?</script>","",b,flags=re.S)[:3000])
    r=ctx.request.get("https://www.nag-cars.com/inventory")
    raw=r.text(); print("RAW",r.status,len(raw),"VINS",len(set(VIN.findall(raw))),"optVin",raw.count("i13r_optVin"))
