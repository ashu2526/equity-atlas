#!/usr/bin/env python3
"""Equity Atlas CI checks for public data, HTML tab wiring, embedded JS, and source guards.

No external packages required. Keep expectations narrow and fail on broken interfaces,
not merely on a stale market-data source which may be closed for a holiday.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
PAGES=["index.html","sector-intelligence.html","company-signals.html",
       "market-desk.html","signals.html","news-radar.html"]
REQUIRED=["data/news/articles.json","data/news/scans.json","data/news/ranked-feed.json",
          "data/news/daily-briefings.json","data/news/flows.json",
          "data/market-signals/sector-rotation.json","data/market-signals/polymarket.json",
          "data/market-signals/watch-universe.json","data/market-signals/stock-price-volume.json"]
checks=0

def check(condition,message):
    global checks
    checks+=1
    if not condition:raise AssertionError(message)

def read(path):return (ROOT/path).read_text(encoding="utf8")
def load(path):return json.loads(read(path))

def validate_data():
    for p in sorted(ROOT.glob("data/**/*.json")):
        try:json.loads(p.read_text(encoding="utf8"))
        except (ValueError,OSError) as e:raise AssertionError(str(p)+": "+str(e))
        check(p.stat().st_size>4,str(p)+" is empty")
    for p in REQUIRED:check((ROOT/p).is_file(),"Missing "+p)
    universe=load("data/market-signals/watch-universe.json")
    tickers=[s.get("ticker") for s in universe.get("stocks",[])]
    check(len(tickers)==len(set(tickers)),"Duplicate tracked company ticker")
    check(all(re.fullmatch(r"[A-Z0-9]{1,30}",str(t or "")) for t in tickers),"Bad NSE ticker")
    stock=load("data/market-signals/stock-price-volume.json")
    names={s.get("ticker") for s in stock.get("stocks",[])}
    check(set(tickers)<=names,"Technical source missing watch universe symbols")
    for s in stock.get("stocks",[]):
        c=s.get("indicators",{})
        if c:
            for k in ("volumeRatio20","rsi14","cmf20","obv20Scaled"):
                v=c.get(k)
                check(v is None or isinstance(v,(int,float)),s.get("ticker")+" bad "+k)
            check(c.get("volumeRatio20") is None or c["volumeRatio20"]>=0,"Negative rel volume")
            check(c.get("rsi14") is None or 0<=c["rsi14"]<=100,"RSI outside range")
            check(c.get("cmf20") is None or -1.01<=c["cmf20"]<=1.01,"CMF outside range")
        if s.get("dataStatus")!="ready":
            check(not s.get("signals"),"Stale/partial price dataset has ACTIVE alerts: "+s.get("ticker","?"))
        bars=s.get("recentBars") or []
        check(all(bars[i]["date"]<=bars[i+1]["date"] for i in range(len(bars)-1)),
              "Price history not in ascending time order: "+s.get("ticker","?"))
    poly=load("data/market-signals/polymarket.json")
    for m in poly.get("markets",[]):
        check(0<=m["yesPrice"]<=1,"YES price outside valid contract price range")
        check(0<=m["impliedYesPercent"]<=100,"YES percent outside 0..100")
    rot=load("data/market-signals/sector-rotation.json")
    check(rot.get("benchmarkIndex")=="NIFTY 50","Wrong index benchmark")
    if rot.get("benchmarkPath"):
        check(len(rot["benchmarkPath"])>=12,"Insufficient benchmark chart sample")
    briefing=load("data/news/daily-briefings.json")
    ids=[b.get("id") for b in briefing.get("briefs",[])]
    check(len(ids)==len(set(ids)),"Duplicate AI review IDs")

def validate_scripts():
    scripts=list((ROOT/"scripts").glob("*.py"))
    check(len(scripts)>=6,"Missing Python research scripts")
    proc=subprocess.run([sys.executable,"-m","compileall","-q",str(ROOT/"scripts")],
                        capture_output=True,text=True)
    check(proc.returncode==0,"Python compile error: "+proc.stderr)

def validate_pages():
    for page in PAGES:
        source=read(page)
        check("<title>" in source and "</title>" in source,"No page title: "+page)
        check('assets/equity-ui.css' in source,"Missing unified theme: "+page)
        check('assets/equity-shell.js' in source,"Missing global navigation: "+page)
        check("<main" in source,"No main content landmark: "+page)
        check(page.endswith(".html") and "</html>" in source,"HTML closing tag missing: "+page)
        scripts=re.findall(r"<script([^>]*)>([\s\S]*?)</script>",source,re.I)
        for i,(attrs,body) in enumerate(scripts):
            if not body.strip() or "type=\"application/json\"" in attrs:continue
            # node --check works on a temporary source and avoids external browser dependencies.
            with tempfile.NamedTemporaryFile(suffix=".js",mode="w",encoding="utf8",delete=False) as f:
                f.write(body);tmp=f.name
            try:
                p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
                check(p.returncode==0,page+" inline JS syntax: "+p.stderr[:300])
            finally:Path(tmp).unlink(missing_ok=True)
        controls=set(re.findall(r'id="([^"]+)"',source))
        for ref in re.findall(r'\$\(["\']#([a-zA-Z0-9_-]+)["\']\)',source):
            check(ref in controls,page+": missing ID referred by JS #"+ref)
    s=read("signals.html")
    check('$$(".sigview")' in s,"Signal Lab regression: nav must switch real .sigview panels")
    signalTabs=re.findall(r'<button data-view="([^"]+)"',s)
    signalPanels=re.findall(r'<section class="sigview(?: active)?" id="([^"]+)"',s)
    check(set(signalTabs)==set(signalPanels),"Signal Lab nav does not match content IDs")
    page=read("company-signals.html")
    script=read("assets/company-signals.js")
    ids=set(re.findall(r'id="([^"]+)"',page))
    for x in re.findall(r'\$\(["\']#([a-zA-Z0-9_-]+)["\']\)',script):
        check(x in ids or ('id="'+x+'"') in script,"Price-volume widget missing static/dynamic DOM ID: "+x)
    shell=read("assets/equity-shell.js")
    for p in PAGES:
        check(p in shell,"Global site navigation missing "+p)
    for scriptname in ["assets/equity-shell.js","assets/company-signals.js"]:
        p=subprocess.run(["node","--check",str(ROOT/scriptname)],capture_output=True,text=True)
        check(p.returncode==0,"External JS invalid: "+scriptname+" "+p.stderr[:200])

def validate_schedule():
    news=read(".github/workflows/news-radar.yml")
    signals=read(".github/workflows/market-signals.yml")
    check('cron: "30 1,13 * * *"' in news,"RSS must run at 7AM/7PM IST")
    check('cron: "30 1 * * *"' in signals and 'cron: "30 13 * * *"' in signals,
          "Signals must run at 7AM/7PM IST")
    check("scripts/stock_price_volume.py" in signals,"Price-volume missing from refresh")
    check((ROOT/"DESIGN.md").is_file(),"No portable design system")

if __name__=="__main__":
    try:
        validate_data();validate_scripts();validate_pages();validate_schedule()
        print("PASS:",checks,"static and data assertions across",len(PAGES),"website pages.")
    except Exception as e:
        print("FAIL:",type(e).__name__,str(e),file=sys.stderr)
        sys.exit(1)
