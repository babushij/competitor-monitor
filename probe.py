import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    for u in ["https://www.cargurus.com/Cars/m-Oaks-Automotive-sp451078","https://cincyautomall.com/inventory"]:
        print("=====",u)
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(12000)
            h=pg.content(); txt=pg.inner_text("body")
            print("TITLE",pg.title(),"LEN",len(h))
            print("VINS in html",len(set(VIN.findall(h))),"VINS in text",len(set(VIN.findall(txt))))
            print("COUNT TEXT",re.findall(r"[\d,]+\s+(?:results|vehicles|cars|listings|matches)",txt,re.I)[:5])
            links=pg.eval_on_selector_all("a[href]","els=>els.map(e=>[e.innerText.trim().slice(0,20),e.getAttribute('href')])")
            print("PAGER",[l for l in links if re.search(r"page|pg=|start=|offset",l[1] or "",re.I) or l[0] in ("Next","›","»","2","3")][:25])
            print("BTNS",pg.eval_on_selector_all("button","els=>els.map(e=>e.innerText.trim()).filter(t=>t&&t.length<20)")[:40])
            print("TEXT",txt[:1500])
        except Exception as e: print("ERR",e)
