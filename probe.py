import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    for u in ["https://www.becksautogroup.com/inventory","https://becksautogroup.com/","https://www.becksautogroup.com/inventory?PageSize=100&page=1"]:
        print("=====",u)
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(10000)
            h=pg.content(); txt=pg.inner_text("body")
            print("FINAL",pg.url,"TITLE",pg.title(),"LEN",len(h))
            print("VINS",len(set(VIN.findall(h))),"optVin",h.count("i13r_optVin"),"dcs",h.count("dealercarsearch"))
            print("COUNT",re.findall(r"[\d,]+\s+(?:results|vehicles|cars|matches)",txt,re.I)[:4])
            links=pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.getAttribute('href'))")
            print("INVLINKS",sorted(set(l for l in links if l and re.search(r"inventor|vdp|used|cars-for-sale",l,re.I)))[:30])
            v=VIN.search(h)
            if v: i=h.find(v.group()); print("CTX",h[i-1200:i+300])
            else: print("TEXT",txt[:1200])
        except Exception as e: print("ERR",e)
