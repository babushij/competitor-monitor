import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    pg.goto("https://www.premier-autoinc.com/inventory",wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(10000)
    h=pg.content(); t=pg.inner_text("body")
    print("FINAL",pg.url,pg.title(),len(h),"VINS",len(set(VIN.findall(h))),"dcs",h.count("dealercarsearch"),"cfs",h.count("carsforsale"),"optVin",h.count("i13r_optVin"),"snap",h.count("vehicle-snapshot"))
    print("COUNT",re.findall(r"(?:[\d,]+\s+(?:vehicles|results|cars)(?:\s+found)?)|(?:(?:Results|Showing) [\d -]+ of \d+)",t,re.I)[:4])
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    det=[l for l in links if re.search(r"vdp|details|/inventory/.+",l,re.I)]
    print("DETAIL",det[:8])
    print("PAGER",[l for l in links if re.search(r"page|pg=|start=",l,re.I)][:10])
    print("TEXT",t[:1200])
    if det:
        pg.goto(det[0],wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(6000)
        print("DETVIN",sorted(set(VIN.findall(pg.content())))[:3])
        try: print("REQVIN",sorted(set(VIN.findall(pg.request.get(det[0]).text())))[:3])
        except Exception as e: print("REQERR",e)
