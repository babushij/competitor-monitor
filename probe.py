import re
from playwright.sync_api import sync_playwright
VIN=re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")
urls=["https://www.cag513.com/Inventory/Details/18ff36d6-ae37-4280-9f6a-ba4aec684090","https://www.cag513.com/Inventory/Details/b14edee1-81c0-4141-83ac-af068dc30b8e","https://www.cag513.com/Inventory/Details/5b2c8c81-6292-4c1d-be56-fb9bcabc245c"]
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    pg.goto("https://www.cag513.com/cars-for-sale",wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(9000)
    t=pg.inner_text("body")
    print("COUNTS",re.findall(r"[\d,]+\s+(?:vehicles|results|cars|matches)[^\n]{0,30}|(?:of|Showing)\s+\d+[^\n]{0,40}",t,re.I)[:6])
    print("PAGER",[x for x in pg.eval_on_selector_all("a,button","els=>els.map(e=>(e.innerText||'').trim()+'|'+(e.getAttribute('href')||''))") if re.search(r"(?i)next|^\d+\||page",x)][:25])
    print("CARDS",len(set(re.findall(r"/Inventory/Details/[0-9a-f-]{36}",pg.content()))))
    for u in urls:
        r=pg.goto(u,wait_until="domcontentloaded",timeout=60000); pg.wait_for_timeout(4000)
        b=pg.inner_text("body")
        print("DETAIL",r.status,pg.url[-60:],pg.title()[:80],"VINS",len(set(VIN.findall(pg.content()))),"SOLD" if re.search(r"(?i)\bsold\b|no longer available|not available",b) else "", b[:300].replace("\n"," | "))
