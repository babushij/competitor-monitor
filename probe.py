import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
U="https://www.internationalautooutlet.com/used-cars-cincinnati-ohio"
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    for u in [U, U+"?page=2", U+"?pagesize=100", U+"?limit=100&page=1"]:
        pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
        h=pg.content(); print("URL",u,"VINS",len(set(VIN.findall(h))))
    pg.goto(U,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
    h=pg.content()
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    det=[l for l in links if re.search(r"\d{4}-|vehicle|detail|vdp|/used-",l,re.I) and "page=" not in l]
    print("DETLINKS",det[:12])
    v=VIN.findall(h)[0]; i=h.find(v); print("AROUND",re.sub(r"\s+"," ",h[i-2500:i+800]))
    print("SORT",pg.eval_on_selector_all("select","els=>els.map(e=>e.name+':'+[...e.options].map(o=>o.value).join(','))"))
