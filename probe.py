from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    pg=p.chromium.launch().new_context(ignore_https_errors=True,user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36").new_page()
    for u in ["https://www.nag-cars.com/newandusedcars","https://nag-cars.com/newandusedcars","http://www.nag-cars.com/newandusedcars"]:
        try:
            r=pg.goto(u,wait_until="domcontentloaded",timeout=60000); pg.wait_for_timeout(8000)
            print("NW",u,"->",pg.url,r.status if r else None,pg.title()[:80],len(pg.content()),pg.content().count("/vdp/"),pg.inner_text("body")[:200].replace("\n"," | "))
        except Exception as e: print("NW ERR",u,str(e)[:150])
