import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    pg.goto("https://www.internationalautooutlet.com/",wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
    h=pg.content(); print("HOME",pg.url,pg.title()[:80],len(h),"cf",h.count("Cloudflare"),"dcs",h.lower().count("dealercarsearch"),"cfs",h.lower().count("carsforsale"),"dc",h.lower().count("dealercenter"))
    links=sorted(set(pg.eval_on_selector_all("a[href]","els=>els.map(e=>e.href)")))
    inv=[l for l in links if re.search(r"(?i)inventor|cars-for-sale|newandused|used",l)]
    print("INVLINKS",inv[:20])
    for u in (inv[:3] or ["https://www.internationalautooutlet.com/inventory"]):
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(9000)
            h=pg.content(); t=pg.inner_text("body")
            print("=====",u,"->",pg.url,"VINS",len(set(VIN.findall(h))),"optVin",h.count("i13r_optVin"),"vdp",len(set(re.findall(r'/vdp/[^"\']+',h))),"details",len(set(re.findall(r'/Inventory/Details/[^"\']+',h))),"snap",h.count("vehicle-snapshot"))
            print("COUNT",re.findall(r"[\d,]+\s+(?:vehicles|results|cars|matches)|(?:Showing|of)\s+[\d -]+(?:of\s+\d+)?",t,re.I)[:5])
            print("PAGER",[x for x in pg.eval_on_selector_all("a,select","els=>els.map(e=>(e.innerText||'').trim().slice(0,30)+'|'+(e.getAttribute('href')||e.name||''))") if re.search(r"(?i)next|page|sort",x)][:15])
        except Exception as e: print("ERR",u,e)
