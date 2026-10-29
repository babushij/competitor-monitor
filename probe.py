import re, json
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    apis=[]
    pg.on("response", lambda r: apis.append((r.url, r.headers.get("content-type",""))) if ("json" in r.headers.get("content-type","")) else None)
    pg.goto("https://www.becksautogroup.com/inventory",wait_until="networkidle",timeout=90000); pg.wait_for_timeout(5000)
    print("JSONAPIS",[a for a in apis if "becks" in a[0] or "inventor" in a[0].lower()][:15])
    h=pg.content()
    print("PAGER",sorted(set(re.findall(r'href="([^"]*(?:page|Page|start|offset)[^"]*)"',h)))[:20])
    print("SCRIPTVIN",len(set(VIN.findall(h))))
    i=h.find("/details/"); print("CARDCTX",h[i-300:i+2500])
    d=re.search(r'/details/[^"]+',h).group()
    pg.goto("https://www.becksautogroup.com"+d,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(6000)
    dh=pg.content(); print("DETAIL",d,"VINS",sorted(set(VIN.findall(dh)))[:3])
    for u in ["https://www.becksautogroup.com/inventory?page=2","https://www.becksautogroup.com/inventory?pagenum=2","https://www.becksautogroup.com/cars-for-sale?page=2"]:
        pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(6000)
        t=pg.inner_text("body"); print("URL",u,re.findall(r"Results [\d -]+ of \d+",t)[:1], sorted(set(re.findall(r"/details/[^\"]+",pg.content())))[:2])
