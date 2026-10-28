import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    pg.goto("https://cincyautomall.com/inventory",wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(10000)
    h=pg.content()
    print("PAGEHINTS",sorted(set(re.findall(r"[\w/.-]*(?:page|Page|pg|PageSize|pagesize|per_page|offset)[\w=/.&?-]{0,40}",h)))[:60])
    v=VIN.search(h).group(); i=h.find(v); print("VINCTX",h[i-1500:i+300])
    for u in ["https://cincyautomall.com/inventory?page=2","https://cincyautomall.com/inventory/page/2","https://cincyautomall.com/inventory?pagesize=100","https://cincyautomall.com/inventory?PageSize=100&page=2"]:
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
            vs=sorted(set(VIN.findall(pg.content()))); print("URL",u,len(vs),vs[:3])
        except Exception as e: print("URL",u,"ERR",e)
