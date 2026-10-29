import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    pg.goto("https://cag513.com/",wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
    h=pg.content(); print("HOME",pg.url,pg.title(),len(h),"dcs",h.count("dealercarsearch"),"cfs",h.count("carsforsale"),"dealercenter",h.count("dealercenter"))
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    inv=[l for l in links if re.search(r"inventor|cars-for-sale|used|vdp|details|search",l,re.I)]
    print("INVLINKS",inv[:30])
    cands=[l for l in inv if re.search(r"inventor|cars-for-sale",l,re.I) and not re.search(r"vdp|details/",l,re.I)][:3] or ["https://cag513.com/inventory"]
    for u in cands:
        print("=====",u)
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(10000)
            h=pg.content(); t=pg.inner_text("body")
            print("FINAL",pg.url,pg.title(),"VINS",len(set(VIN.findall(h))),"optVin",h.count("i13r_optVin"),"snap",h.count("vehicle-snapshot"),"dcs",h.count("dealercarsearch"),"cfs",h.count("carsforsale"))
            print("COUNT",re.findall(r"(?:[\d,]+\s+(?:vehicles|results|cars)(?:\s+found)?)|(?:Results [\d -]+ of \d+)",t,re.I)[:4])
            print("TEXT",t[:800])
        except Exception as e: print("ERR",e)
