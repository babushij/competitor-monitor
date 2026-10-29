import re
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    pg=p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",viewport={"width":1366,"height":900})
    for u in ["https://cincyautomall.com/inventory","https://www.nag-cars.com/newandusedcars","https://www.becksautogroup.com/inventory","https://www.cag513.com/cars-for-sale"]:
        print("=====",u)
        try:
            pg.goto(u,wait_until="domcontentloaded",timeout=90000); pg.wait_for_timeout(8000)
            sels=pg.eval_on_selector_all("select","els=>els.map(e=>({id:e.id,name:e.name,onchange:e.getAttribute('onchange'),opts:[...e.options].map(o=>o.value+'='+o.text.trim())}))")
            for s in sels:
                if any(re.search(r"(?i)stock|year|price|newest|oldest",o) for o in s["opts"]): print("SELECT",s)
            h=pg.content()
            for m in re.findall(r"function changePageSortBy[^}]+}",h)[:1]: print("FN",m[:400])
            print("SORTLINKS",sorted(set(re.findall(r'href="([^"]*(?:sort|Sort|orderby|SortBy)[^"]*)"',h)))[:12])
        except Exception as e: print("ERR",e)
