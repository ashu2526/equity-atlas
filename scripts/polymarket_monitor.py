#!/usr/bin/env python3
"""Read-only Polymarket Gamma API macro-event discovery and probability tracking.

Reference: Polymarket/agent-skills market-data.md, docs.polymarket.com.
No wallet, keys, CLOB trade orders or financial transactions. Prices are contract prices,
not objective truth or necessarily fair probabilities. Market selection is curated heuristics.
"""
from __future__ import annotations
import datetime as dt
import json
import math
from pathlib import Path
import re
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

DATA=Path(__file__).resolve().parents[1]/"data/market-signals"
NOW=dt.datetime.now(dt.timezone.utc)
API="https://gamma-api.polymarket.com/events"
INCLUDE={
"Central banks / rates":r"\b(?:fed(?:eral reserve)?|fomc|interest rates?|rate cuts?|rate hikes?|cpi|inflation|powell|ecb|bank of japan|bond yields?|treasury yields?|recession|unemployment|gdp|economic growth)\b",
"Elections / policy":r"\b(?:election|electoral|midterms?|presiden(?:t|tial)|prime minister|parliament|congress|senate|government shutdown|debt ceiling|tariffs?|trade deal|trade war|trade agreement|export controls?|tax bill|fiscal policy)\b",
"War / geopolitics":r"\b(?:iran|israel|ukraine|russia|china|taiwan|hormuz|gaza|middle east|ceasefire|peace deal|peace talks|military conflict|war|sanctions|invasion|missile|nuclear|north korea|geopolitics)\b",
"Energy / commodities":r"\b(?:oil prices?|brent|crude oil|opec|natural gas|lng|energy prices?|gold prices?|silver prices?|supply shock|oil production|shipping route|panama canal)\b",
"Technology / AI":r"\b(?:artificial intelligence|ai (?:model|capex|bubble|spending|regulation)|nvidia|openai|anthropic|data cent(?:er|re)|semiconductor|chip export|tech antitrust)\b",
"Global liquidity / systemic risk":r"\b(?:bank failures?|financial crisis|sovereign default|debt default|credit ratings?|credit spread|treasury auction|bankruptcy|quantitative easing|quantitative tightening|currency intervention)\b",
}
RX={k:re.compile(v,re.I) for k,v in INCLUDE.items()}
SKIP=re.compile(r"\b(?:nba|nfl|nhl|super bowl|soccer|football|cricket|tennis|formula 1|champions league|mlb|sports|grammy|oscar|spotify|tiktok followers|celebrity marriage|celebrity divorce|box office|youtube views|streaming release)\b",re.I)
DIRECT={
"Central banks / rates":"Indian banks; NBFCs; real estate; bond duration; global IT/exports",
"Elections / policy":"Exporters; auto components; pharma; logistics; defence; FX-sensitive firms",
"War / geopolitics":"Energy; freight; defence; chemicals; shipping; airlines",
"Energy / commodities":"OMCs; paints; tyres; chemicals; airlines; metals",
"Technology / AI":"IT services; AI infrastructure; power transformers; data-centre cooling",
"Global liquidity / systemic risk":"Banks; NBFCs; USD-sensitive exporters; equities with high refinancing needs",
}
INDIRECT={
"Central banks / rates":"Autos; housing materials; consumer durables; infrastructure capex",
"Elections / policy":"Contract manufacturing; special economic zones; domestic substitutes",
"War / geopolitics":"Insurance; fertilisers; port logistics; commodity substitution",
"Energy / commodities":"Rural inflation; consumer demand; vehicle logistics; input spreads",
"Technology / AI":"Power generation; electric utilities; cables; construction",
"Global liquidity / systemic risk":"Small/mid-caps; funding-dependent IPOs; real estate credit",
}
def read(name,default):
    try:return json.loads((DATA/name).read_text(encoding="utf8"))
    except (OSError,ValueError):return default
def write(name,obj):
    DATA.mkdir(parents=True,exist_ok=True)
    p=DATA/name;tmp=p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    tmp.replace(p)
def number(x,default=None):
    try:
        v=float(x)
        return v if math.isfinite(v) else default
    except (TypeError,ValueError):return default
def jlist(x):
    if isinstance(x,list):return x
    if isinstance(x,str):
        try:
            v=json.loads(x)
            return v if isinstance(v,list) else []
        except ValueError:return []
    return []
def parse_time(x):
    try:return dt.datetime.fromisoformat(str(x).replace("Z","+00:00")).astimezone(dt.timezone.utc)
    except (TypeError,ValueError):return None
def get_events(limit=50,offset=0):
    params=urlencode({"active":"true","closed":"false","order":"volume24hr",
                      "ascending":"false","limit":limit,"offset":offset})
    req=Request(API+"?"+params,headers={"User-Agent":"EquityAtlasResearch/1.1 (public market-data research)","Accept":"application/json"})
    with urlopen(req,timeout=20) as r:
        raw=r.read(6_000_000)
    obj=json.loads(raw)
    if isinstance(obj,list):return obj
    if isinstance(obj,dict):return obj.get("events",[]) or obj.get("data",[])
    return []
def event_category(title):
    if SKIP.search(title):return None
    choices=[k for k,rx in RX.items() if rx.search(title)]
    if not choices:return None
    return choices[0]
def markets_for(event):
    allmarkets=event.get("markets") or []
    if not isinstance(allmarkets,list):return []
    out=[]
    for m in allmarkets:
        if not isinstance(m,dict) or m.get("closed") is True or m.get("active") is False:continue
        opts=jlist(m.get("outcomes"))
        prices=jlist(m.get("outcomePrices"))
        if len(opts)!=2 or len(prices)!=2:continue
        yes=next((i for i,name in enumerate(opts) if str(name).strip().lower()=="yes"),None)
        if yes is None:continue
        odd=number(prices[yes])
        if odd is None or not (0.005<=odd<=0.995):continue
        vol24=number(m.get("volume24hr"),0) or 0
        liq=number(m.get("liquidityNum"),None)
        volume=number(m.get("volumeNum"),None)
        out.append({"market":m,"yes":round(odd,4),"volume24h":vol24,"liquidity":liq,"volumeTotal":volume})
    out.sort(key=lambda x:(x["volume24h"],x["liquidity"] or 0),reverse=True)
    return out
def main():
    old=read("polymarket.json",{})
    hist=read("polymarket-history.json",{"snapshots":[]})
    gathered=[];errors=[]
    for offset in (0,50,100,150,200,250,300,350):
        try:
            part=get_events(50,offset)
            gathered.extend(part)
            if len(part)<50:break
        except Exception as exc:
            errors.append(str(exc)[:200])
            if not gathered:break
    if not gathered:
        # Preserve last known successful market observations and explicitly expose fetch failure.
        old["lastAttemptAt"]=NOW.isoformat()
        old["dataStatus"]="fetch_failed_preserved_prior_snapshot"
        old["lastError"]="; ".join(errors) if errors else "Provider returned no events"
        if old.get("markets"):write("polymarket.json",old)
        print("Polymarket unavailable; old data preserved. Errors:",errors)
        return 0 if old.get("markets") else 1
    previous={x.get("id"):x for x in old.get("markets",[])}
    saved=[]
    seen=set()
    for ev in gathered:
        if not isinstance(ev,dict):continue
        heading=str(ev.get("title") or ev.get("question") or "").strip()
        category=event_category(heading)
        if not category:continue
        if ev.get("closed") is True or ev.get("active") is False:continue
        ends=parse_time(ev.get("endDate"))
        if ends and ends < NOW-dt.timedelta(days=1):continue
        ms=markets_for(ev)
        if not ms:continue
        chosen=ms[:3] if category in ("Elections / policy","Central banks / rates") else ms[:1]
        for m in chosen:
            raw=m["market"]
            question=str(raw.get("question") or heading).strip()
            if SKIP.search(question):continue
            # Market can differ from event title; select only identifiable, active binary YES contracts.
            ref=str(raw.get("id") or raw.get("conditionId") or "")
            if not ref or ref in seen:continue
            seen.add(ref)
            v24=m["volume24h"]
            if v24<250 and (m["volumeTotal"] or 0)<10_000:continue
            prior=previous.get(ref)
            price=m["yes"]
            delta=round(100*(price-prior["yesPrice"]),2) if prior and isinstance(prior.get("yesPrice"),(int,float)) else None
            slug=str(ev.get("slug") or raw.get("slug") or "").strip()
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,150}",slug):continue
            url="https://polymarket.com/event/"+slug
            saved.append({
                "id":ref,"eventId":str(ev.get("id") or ""),"slug":slug,"url":url,
                "title":heading[:210],"question":question[:250],"category":category,
                "endDate":str(ev.get("endDate") or "")[:24],
                "yesPrice":price,"impliedYesPercent":round(price*100,1),
                "changeSinceLastSnapshotPp":delta,
                "lastSnapshotAsOf":prior.get("asOf") if prior else None,
                "volume24hUsd":round(v24,2),
                "volumeTotalUsd":round(m["volumeTotal"],2) if m["volumeTotal"] is not None else None,
                "liquidityUsd":round(m["liquidity"],2) if m["liquidity"] is not None else None,
                "asOf":NOW.isoformat(),
                "directExposure":DIRECT[category],"proxyExposure":INDIRECT[category],
                "relevanceToNews":category,
                "marketStatus":"Active, unresolved, binary YES/NO",
                "note":"Market YES contract price, not scientifically calibrated event probability; liquidity/fees/selection can affect odds."
            })
    saved.sort(key=lambda a:(a["volume24hUsd"],a["liquidityUsd"] or 0),reverse=True)
    saved=saved[:80]
    # A page of sports-dominated top volume can leave too little macro. Keep an explicit coverage signal.
    status="ready" if len(saved)>=8 else "low_macro_coverage"
    out={"schema":1,"provider":"Polymarket Gamma API","providerDocs":"https://docs.polymarket.com/",
         "githubReference":"https://github.com/Polymarket/agent-skills/blob/main/market-data.md",
         "generatedAt":NOW.isoformat(),"lastAttemptAt":NOW.isoformat(),"dataStatus":status,
         "market": "Global macro/geopolitical/policy contracts; excludes sports and entertainment",
         "scope":{"eventsFetched":len(gathered),"macroMarketsSelected":len(saved),"fetchErrors":errors},
         "markets":saved,
         "guardrails":["YES contract last quoted outcome price is an implied market price; it is not a verified probability or a factual news source.",
           "Volume/liquidity is betting-market trading, NOT institutional equity or sector money flow.",
           "Active market outcome semantics are market-specific. Binary YES/NO contracts only; related events may overlap and should NOT be summed.",
           "Prediction market odds can be distorted by fees, low liquidity, participant selection, market manipulation and stale quotes.",
           "Odds changes compare actual successful snapshots, not necessarily 24h or an entire calendar day. Check times.",
           "This is read-only market-data research. No orders, wallets, account credentials, trading or portfolio recommendation.",
           "Unmatched Indian-specific news may have no relevant market; no event is invented or force-matched."],
         "selection":{"source":"Gamma top active events by volume24hr, up to 400",
            "filter":"Macro, central bank, economics, trade, geopolitical, technology and other research-relevant terms; sports/entertainment excluded",
            "volume":"At least $250 24h market volume or $10k total, where available",
            "notComprehensive":"Top-volume event sampling may miss niche-but-important contracts; no feed represents all Polymarket markets."}}
    write("polymarket.json",out)
    snapshots=[x for x in hist.get("snapshots",[]) if x.get("asOf")!=out["generatedAt"]]
    snapshots.insert(0,{"asOf":out["generatedAt"],"marketCount":len(saved),
                      "categories":{cat:len([x for x in saved if x["category"]==cat]) for cat in INCLUDE},
                      "odds":[{"id":x["id"],"yes":x["yesPrice"],"category":x["category"],
                               "volume24hUsd":x["volume24hUsd"]} for x in saved]})
    write("polymarket-history.json",{"schema":1,"snapshots":snapshots[:180]})
    print("Polymarket macro markets",len(saved),"from",len(gathered),"events, errors",errors[:1])
if __name__=="__main__":main()
