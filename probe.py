import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    for u in ["https://www.nag-cars.com/inventory","https://www.nag-cars.com/inventory?PageSize=100&page=1"]:
        print("=====",u)
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(15000)
            h=pg.content(); t=pg.inner_text("body")
            print("FINAL",pg.url,pg.title(),len(h),"VINS",len(set(VIN.findall(h))),"optVin",h.count("i13r_optVin"),"dcs",h.count("dealercarsearch"),"cfs",h.count("carsforsale"),"snap",h.count("vehicle-snapshot"),"cf",h.count("Cloudflare"))
            print("COUNT",re.findall(r"(?:[\d,]+\s+(?:vehicles|results|cars)(?:\s+found)?)|(?:(?:Results|Showing) [\d -]+ of \d+)",t,re.I)[:4])
            links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
            print("DETAIL",[l for l in links if re.search(r"vdp|details",l,re.I)][:5])
            print("TEXT",t[:700])
        except Exception as e: print("ERR",e)
