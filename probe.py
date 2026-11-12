import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_context(ignore_https_errors=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900}).new_page()
    js=[]
    pg.on("response",lambda r: js.append((r.url[:160],len(r.body()) if r.ok else 0)) if r.request.resource_type in ("xhr","fetch") else None)
    pg.goto("https://nag-cars.com/inventory",wait_until="load",timeout=90000); pg.wait_for_timeout(12000)
    h=pg.content(); t=pg.inner_text("body")
    print("NW VINS",len(set(VIN.findall(h))),"COUNT",re.findall(r"[\d,]+\s+(?:vehicles|results|cars|matches)[^\n]{0,20}|of\s+\d+",t,re.I)[:5])
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    print("NW DET",[l for l in links if "nag-cars" in l and re.search(r"\d{4}|vin|detail|vehicle|inventory/",l,re.I)][:8])
    print("NW PAGER",[x for x in pg.eval_on_selector_all("a,button","els=>els.map(e=>(e.innerText||'').trim().slice(0,25)+'|'+(e.getAttribute('href')||''))") if re.search(r"(?i)next|page|load more|show more",x)][:10])
    for x in js[:15]: print("NW XHR",x)
    v=VIN.findall(h); 
    if v: i=h.find(v[0]); print("NW AROUND",re.sub(r"\s+"," ",h[i-1500:i+300]))
    print("NW TEXT",t[600:1500].replace("\n"," | "))
