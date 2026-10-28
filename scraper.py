import json, re, datetime, pathlib
from playwright.sync_api import sync_playwright

DATA = pathlib.Path("docs/data"); DATA.mkdir(parents=True, exist_ok=True)
TODAY = datetime.date.today().isoformat()
VIN_RE = re.compile(r"\b[A-HJ-NPR-Z0-9]{17}\b")

DEALERS = {
    "gtx": {"name": "GTX Auto Group",
            "url": "https://usedcarscincinnati.com/Inventory/All",
            "card": "li:has(a[href*='Details?stock='])"},
    "oaks": {"name": "Oaks Automotive",
             "url": "https://oaksauto513.com/inventory/",
             "generic": True},
}

CARD_JS = """() => {
 const re=/\\b[A-HJ-NPR-Z0-9]{17}\\b/g, out=[];
 for (const el of document.querySelectorAll('body *')) {
   const t=el.innerText||''; const m=t.match(re);
   if(!m||new Set(m).size!==1) continue;
   const p=el.parentElement; const pm=p&&(p.innerText||'').match(re);
   if(pm&&new Set(pm).size===1) continue;
   const a=el.querySelector('a[href]'); out.push([t, a?a.href:'']);
 }
 return out;}"""

def parse_generic(text, href):
    vin = VIN_RE.search(text)
    if not vin: return None
    ym = re.search(r"\b((?:19|20)\d{2})\s+([A-Za-z\-]+)\s+([^\n$]+)", text)
    price = re.search(r"\$\s?([\d,]{4,})", text)
    miles = re.search(r"([\d,]+)\s*(?:mi\b|miles|Miles|MI\b)", text)
    return {"vin": vin.group(), "year": ym.group(1) if ym else "",
            "make": ym.group(2) if ym else "", "model": ym.group(3).strip()[:40] if ym else "",
            "price": int(price.group(1).replace(",", "")) if price else None,
            "miles": int(miles.group(1).replace(",", "")) if miles else None, "url": href}

def scrape_generic(page, d):
    page.goto(d["url"], wait_until="networkidle", timeout=120000)
    page.wait_for_timeout(5000)
    cars = {}
    for _ in range(40):
        before = len(cars)
        for t, href in page.evaluate(CARD_JS):
            c = parse_generic(t, href)
            if c: cars[c["vin"]] = c
        print(f"  {d['name']}: {len(cars)} so far")
        nxt = page.query_selector("a[rel=next], a[aria-label*='Next' i], a:has-text('Next'), button:has-text('Next'), a:has-text('›'), a:has-text('»')")
        if not nxt or len(cars) == before: break
        try:
            nxt.click(); page.wait_for_load_state("networkidle", timeout=60000); page.wait_for_timeout(3000)
        except Exception as e:
            print("  next failed", e); break
    if not cars: print(page.content()[:3000])
    return cars

def parse_card(text, href):
    vin = VIN_RE.search(text)
    if not vin: return None
    ym = re.search(r"(\d{4}) ([A-Z][A-Z\- ]+)\n+(.+)", text)
    price = re.search(r"Internet Price\s*\$([\d,]+)", text)
    miles = re.search(r"([\d,]+) Miles", text)
    return {"vin": vin.group(), "year": ym.group(1) if ym else "",
            "make": ym.group(2).strip() if ym else "",
            "model": ym.group(3).strip(" -") if ym else "",
            "price": int(price.group(1).replace(",", "")) if price else None,
            "miles": int(miles.group(1).replace(",", "")) if miles else None,
            "url": href}

def scrape(page, d):
    if d.get("generic"): return scrape_generic(page, d)
    page.goto(d["url"], wait_until="networkidle", timeout=120000)
    page.wait_for_timeout(5000)
    cars = {}
    for card in page.query_selector_all(d["card"]):
        a = card.query_selector("a[href*='Details?stock=']")
        car = parse_card(card.inner_text(), a.get_attribute("href") if a else "")
        if car: cars[car["vin"]] = car
    return cars

def update(key, name, cars):
    sf = DATA / f"{key}_state.json"; soldf = DATA / "sold.json"
    state = json.loads(sf.read_text()) if sf.exists() else {}
    sold = json.loads(soldf.read_text()) if soldf.exists() else []
    if len(cars) < 0.5 * max(len(state), 1):   # safety: bad scrape, don't mark mass sold
        print(f"{name}: only {len(cars)} cars, skipping"); return
    for vin, c in cars.items():
        prev = state.get(vin, {"first_seen": TODAY})
        state[vin] = {**c, "first_seen": prev["first_seen"], "last_seen": TODAY}
    for vin in [v for v in state if v not in cars]:
        c = state.pop(vin)
        days = (datetime.date.today() - datetime.date.fromisoformat(c["first_seen"])).days
        sold.append({**c, "dealer": name, "sold_detected": TODAY, "days_listed": days})
    sf.write_text(json.dumps(state, indent=1))
    soldf.write_text(json.dumps(sold, indent=1))
    print(f"{name}: {len(cars)} active")

with sync_playwright() as p:
    page = p.chromium.launch().new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36", viewport={"width":1366,"height":900})
    for key, d in DEALERS.items():
        try: update(key, d["name"], scrape(page, d))
        except Exception as e: print(f"{d['name']} FAILED: {e}")
