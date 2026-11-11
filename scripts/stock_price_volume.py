#!/usr/bin/env python3
"""Equity Atlas: transparent end-of-day stock price + volume surveillance.

Uses public Yahoo chart history for tracked NSE symbols as a best-effort source.
No broker, exchange-authorized real-time feed, trade signals or guarantee of availability.
Missing data stays unknown; prior successful data is retained but marked stale.
"""
from __future__ import annotations
import concurrent.futures as cf
import datetime as dt
import json
import math
import os
import statistics
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request,urlopen
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/market-signals"
NOW=dt.datetime.now(dt.timezone.utc)
TODAY=dt.datetime.now(ZoneInfo("Asia/Kolkata")).date()
MIN_HISTORY=205

def read(name,default):
    try:return json.loads((BASE/name).read_text(encoding="utf8"))
    except (OSError,ValueError):return default

def write(name,obj):
    BASE.mkdir(parents=True,exist_ok=True)
    tmp=BASE/(name+".tmp")
    tmp.write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf8")
    tmp.replace(BASE/name)

def good(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (ValueError,TypeError):return None

def fetch(ticker):
    symbol=ticker+".NS"
    error=[]
    for domain in ("query1.finance.yahoo.com","query2.finance.yahoo.com"):
        url="https://"+domain+"/v8/finance/chart/"+quote(symbol,safe="") + "?range=18mo&interval=1d&events=div%2Csplits"
        req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; EquityAtlas/1.0; research archive)","Accept":"application/json"})
        try:
            with urlopen(req,timeout=15) as resp:
                raw=resp.read(3_500_000)
            root=json.loads(raw)
            node=root["chart"]["result"][0]
            times=node.get("timestamp",[])
            values=node["indicators"]["quote"][0]
            data=[]
            for i,t in enumerate(times):
                c=good((values.get("close") or [])[i])
                hi=good((values.get("high") or [])[i])
                lo=good((values.get("low") or [])[i])
                v=good((values.get("volume") or [])[i])
                op=good((values.get("open") or [])[i])
                if None in (c,hi,lo,v,op) or c<=0 or hi<lo or v<0:continue
                day=dt.datetime.fromtimestamp(t,dt.timezone.utc).date().isoformat()
                if day>TODAY.isoformat():continue
                data.append({"date":day,"open":round(op,4),"high":round(hi,4),
                             "low":round(lo,4),"close":round(c,4),"volume":int(v)})
            # No intraday partial bar; market is 09:15-15:30 IST weekdays.
            local=dt.datetime.now(ZoneInfo("Asia/Kolkata"))
            if local.weekday()<5 and (local.hour<16) and data and data[-1]["date"]==TODAY.isoformat():
                data.pop()
            seen={x["date"]:x for x in data}
            data=list(sorted(seen.values(),key=lambda x:x["date"]))
            if len(data)<60:raise ValueError("too few historical daily bars: "+str(len(data)))
            splitEvents=(node.get("events") or {}).get("splits") or {}
            splitDates=[dt.datetime.fromtimestamp(int(x.get("date")),dt.timezone.utc).date().isoformat()
                        for x in splitEvents.values() if x.get("date")]
            return {"ticker":ticker,"bars":data,"source":"Yahoo Finance chart (unofficial market-data mirror)",
                    "sourceUrl":"https://finance.yahoo.com/quote/"+quote(symbol,safe="")+"/history/",
                    "splits":splitDates}
        except Exception as exc:error.append(domain+": "+str(exc)[:105])
    return {"ticker":ticker,"error":" | ".join(error)}

def mean(vals):
    return sum(vals)/len(vals) if vals else None

def sma(vals,n):
    return mean(vals[-n:]) if len(vals)>=n else None

def rsi(vals,n=14):
    if len(vals)<n+1:return None
    changes=[vals[i]-vals[i-1] for i in range(len(vals)-n,len(vals))]
    up=sum(max(c,0) for c in changes)/n
    down=sum(max(-c,0) for c in changes)/n
    if not down:return 100.0 if up else 50.0
    return 100-100/(1+up/down)

def analyse(item):
    ticker=item["ticker"];rows=item["bars"];cl=[x["close"] for x in rows]
    vol=[x["volume"] for x in rows];hi=[x["high"] for x in rows];lo=[x["low"] for x in rows]
    last=rows[-1];n=len(rows);p=cl[-1]
    ma20=sma(cl,20);ma50=sma(cl,50);ma200=sma(cl,200)
    prev20=max(hi[-21:-1]) if n>=21 else None
    prev55=max(hi[-56:-1]) if n>=56 else None
    low55=min(lo[-56:-1]) if n>=56 else None
    hi252=max(hi[-253:-1]) if n>=253 else None
    v20=sma(vol[:-1],20)
    vr=p and (vol[-1]/v20 if v20 and v20>0 else None)
    value20=mean([x["close"]*x["volume"] for x in rows[-20:]])
    # Chaikin Money Flow uses high-low close location, not a prediction.
    mflow=[((2*x["close"]-x["high"]-x["low"])/(x["high"]-x["low"]) if x["high"]>x["low"] else 0)*x["volume"]
           for x in rows[-20:]]
    vm=sum(vol[-20:])
    cmf=sum(mflow)/vm if vm else None
    obv20=sum((1 if cl[i]>cl[i-1] else -1 if cl[i]<cl[i-1] else 0)*vol[i]
              for i in range(max(1,n-20),n))
    obv20scaled=obv20/(v20*20) if v20 else None
    ret=lambda d: round(100*(p/cl[-d-1]-1),2) if n>d and cl[-d-1]>0 else None
    ret20=ret(20);ret60=ret(60);ret120=ret(120)
    prev_ma50=mean(cl[-51:-1]) if n>=51 else None
    prev_ma200=mean(cl[-201:-1]) if n>=201 else None
    ma50slope=(100*(ma50/prev_ma50-1) if ma50 and prev_ma50 else None)
    trend=("Above 20/50/200 DMA" if all(v is not None and p>v for v in (ma20,ma50,ma200)) else
           "Above 50/200 DMA" if ma50 and ma200 and p>ma50 and p>ma200 else
           "Below 50/200 DMA" if ma50 and ma200 and p<ma50 and p<ma200 else "Mixed")
    hasLong=n>=MIN_HISTORY
    majorSplit=any((last["date"]>=d) for d in item.get("splits",[]) if d>=rows[max(0,n-60)]["date"])
    # Protect against raw OHLC/volume artefacts after unusually large price jumps.
    recentJump=any(abs(cl[i]/cl[i-1]-1)>0.38 for i in range(max(1,n-30),n) if cl[i-1]>0)
    suppress=majorSplit or recentJump
    closeLocation=(p-last["low"])/(last["high"]-last["low"]) if last["high"]>last["low"] else 0.5
    events=[]
    def alert(key,priority,headline,evidence,confirm,risk,horizon):
        events.append({"id":key,"priority":priority,"headline":headline,"evidence":evidence,
                       "confirmation":confirm,"invalidation":risk,"horizon":horizon,
                       "type":"mechanical_price_volume_observation_not_a_trade_signal"})
    if not suppress and vr is not None and vr>=1.55 and closeLocation>=.6 and prev55 and p>prev55*1.003 and ma50 and p>ma50:
        alert("volume_confirmed_55d_breakout","high","55-session breakout on elevated volume",
              f"Close ₹{p:,.2f} above prior 55-session high ₹{prev55:,.2f}; last volume {vr:.2f}× previous 20-session mean; close in top {100*(1-closeLocation):.0f}% of day's range.",
              "Sustain above former resistance on at least 2 further closes, with sector relative strength and earnings support.",
              "Return below breakout level or company event/corporate action explains the jump.","short_term")
    elif not suppress and vr is not None and vr>=1.3 and prev20 and p>prev20*1.003 and closeLocation>=.55:
        alert("volume_20d_breakout_watch","watch","20-session breakout — follow-through needed",
              f"Close ₹{p:,.2f} above prior 20-session high ₹{prev20:,.2f}, volume {vr:.2f}× 20-session mean.",
              "Confirm 2–3-day follow-through and company-level catalysts.",
              "Failed hold above resistance; volume spike unrelated to ownership interest.","short_term")
    if not suppress and vr is not None and vr>=1.5 and low55 and p<low55*.997 and ma50 and p<ma50 and closeLocation<=.4:
        alert("volume_confirmed_55d_breakdown","high","55-session support break on heavy volume",
              f"Close below previous 55-session low ₹{low55:,.2f}; volume {vr:.2f}× normal.",
              "Persistent weakness, negative relative strength and any deteriorating fundamentals.",
              "Rapid recovery above support or isolated liquidity/corporate-action distortion.","short_term")
    if hasLong and not suppress and ma200 and n>=6 and p>ma200 and cl[-6]<mean(cl[-205:-5]) and vr and vr>=1.15:
        alert("200d_reclaim_watch","watch","Possible longer-term upturn: 200-DMA reclaim",
              f"Price recovered above 200-session average ₹{ma200:,.2f}, with volume {vr:.2f}× normal.",
              "Multiple closes above 200-DMA, rising 50-DMA and positive sector leadership.",
              "Close drops below 200-DMA or fundamentals remain impaired.","long_term")
    if hasLong and not suppress and ma200 and n>=6 and p<ma200 and cl[-6]>mean(cl[-205:-5]) and vr and vr>=1.3:
        alert("200d_loss_watch","watch","Possible longer-term reversal: lost 200-DMA",
              f"Price slipped below 200-session average ₹{ma200:,.2f}, with volume {vr:.2f}× normal.",
              "Persistent close below 200-DMA plus adverse earnings or sector breadth.",
              "Regains 200-DMA on steady demand.","long_term")
    if ret20 is not None and ret20>5 and obv20scaled is not None and obv20scaled<-.12 and not suppress:
        alert("price_volume_divergence","watch","Price rising but net up/down volume has weakened",
              f"20-session price return {ret20:+.2f}%, OBV proxy net volume ratio {obv20scaled:+.2f}.",
              "Compare delivery volumes and new highs; deterioration in breadth may foreshadow exhaustion.",
              "OBV recovers as trend broadens; large block/corporate action distorts volume.","short_medium")
    if cmf is not None and cmf<=-.20 and vr and vr>=1.5 and not suppress:
        alert("distribution_risk","watch","High-volume closing weakness / distribution risk",
              f"20-session Chaikin Money Flow {cmf:+.2f} with latest volume {vr:.2f}× average.",
              "Watch for lower highs and support loss across several sessions.",
              "CMF normalizes or weakness stems from a non-recurring liquidity event.","short_medium")
    if suppress:
        alert("corporate_action_or_gap_guard","info","Unusually large recent price move — signals withheld",
              "Recent split event or >38% single-session price gap in underlying series.",
              "Verify exchange corporate action and adjusted OHLCV history before evaluating patterns.",
              "False split/price-feed artefact; don't use mechanical breakout classification.","data_quality")
    events.sort(key=lambda x:{"high":0,"watch":1,"info":2}.get(x["priority"],3))
    lastDay=dt.date.fromisoformat(last["date"])
    weekdaysSince=sum((lastDay+dt.timedelta(days=i)).weekday()<5
                      for i in range(1,(TODAY-lastDay).days+1)) if TODAY>=lastDay else 99
    # Early morning: a prior working day's close is normal. After two missed
    # trading sessions, old price bars must not create current breakout alerts.
    isStale=weekdaysSince>2
    if isStale:
        events=[]
    return {
      "ticker":ticker,"name":item.get("name",ticker),"sector":item.get("sector","Unclassified"),
      "primaryResearch":bool(item.get("primaryResearch")),"asOf":last["date"],
      "dataStatus":"stale" if isStale else ("partial_history" if not hasLong else "ready"),
      "source":item.get("source"),"sourceUrl":item.get("sourceUrl"),
      "observations":n,"lastClose":round(p,2),"lastVolume":vol[-1],
      "indicators":{"sma20":round(ma20,2) if ma20 else None,"sma50":round(ma50,2) if ma50 else None,
                    "sma200":round(ma200,2) if ma200 else None,"rsi14":round(rsi(cl),2) if rsi(cl) is not None else None,
                    "volumeRatio20":round(vr,2) if vr is not None else None,"cmf20":round(cmf,3) if cmf is not None else None,
                    "obv20Scaled":round(obv20scaled,3) if obv20scaled is not None else None,
                    "closeLocation":round(closeLocation,3),"averageTurnover20Inr":round(value20,2) if value20 is not None else None,
                    "return20dPct":ret20,"return60dPct":ret60,"return120dPct":ret120,
                    "distance52wHighPct":round(100*(p/hi252-1),2) if hi252 else None,
                    "ma50SlopeSessionPct":round(ma50slope,4) if ma50slope is not None else None,
                    "prior20High":round(prev20,2) if prev20 else None,"prior55High":round(prev55,2) if prev55 else None,
                    "prior55Low":round(low55,2) if low55 else None},
      "trend":trend,"signals":events[:4],
      "signalCount":len(events),"dataQuality":{"majorSplitInRecent60Sessions":majorSplit,
          "unusuallyLargePriceGapRecent30Sessions":recentJump,
          "tradingSessionsSinceLastBar":weekdaysSince,
          "signalsWithheld":suppress or isStale,
          "warning":"Split-adjustment and exchange-verified delivery data not independently audited. Price-volume patterns are not investment instructions."},
      "recentBars":rows[-120:],
    }

def main():
    universe=read("watch-universe.json",{"stocks":[]})
    old=read("stock-price-volume.json",{"stocks":[]})
    previous={x["ticker"]:x for x in old.get("stocks",[])}
    names=universe.get("stocks",[])
    names=[x for x in names if isinstance(x,dict) and str(x.get("ticker","")).isalnum()][:75]
    if not names:
        raise RuntimeError("No valid ticker universe; refusing to publish empty surveillance data")
    result={}
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        jobs={pool.submit(fetch,x["ticker"]):x for x in names}
        for future in cf.as_completed(jobs):
            meta=jobs[future]
            try:data=future.result()
            except Exception as exc:data={"ticker":meta["ticker"],"error":str(exc)}
            if "bars" in data:
                try:result[meta["ticker"]]=analyse({**meta,**data})
                except Exception as exc:data={"ticker":meta["ticker"],"error":"Indicator error "+str(exc)}
            if "bars" not in data:
                saved=previous.get(meta["ticker"])
                if saved:
                    result[meta["ticker"]]={**saved,"dataStatus":"fetch_failed_stale_previous_snapshot","signals":[],
                                            "sourceFetchError":data.get("error"),
                                            "dataQuality":{**saved.get("dataQuality",{}),"signalsWithheld":True}}
                else:
                    result[meta["ticker"]]={"ticker":meta["ticker"],"name":meta.get("name",meta["ticker"]),
                        "sector":meta.get("sector","Unclassified"),"dataStatus":"unavailable",
                        "asOf":None,"sourceFetchError":data.get("error"),"signals":[]}
    rows=[result[x["ticker"]] for x in names]
    live=[x for x in rows if x.get("dataStatus")=="ready"]
    flagged=sum(bool(x.get("signals")) for x in live)
    output={"schema":1,"generatedAt":NOW.isoformat(),"asOf":max((x["asOf"] for x in rows if x.get("asOf")),default=None),
            "status":"ready" if len(live)>=len(rows)*.6 else "partial_or_unavailable",
            "method":"Deterministic daily OHLCV: 20/50/200 session averages, 20/55-session breakout/breakdown with relative volume, Chaikin Money Flow 20, OBV proxy, 200-session trend reclaims, RSI 14 and observed return windows.",
            "sourceNotice":"Public Yahoo Finance historical chart endpoint, unofficial; market data/licensing/continuity and split adjustment must be checked before live investment use.",
            "coverage":{"configuredTickers":len(names),"ready":len(live),"flaggedReadyStocks":flagged,
                        "partialOrUnavailable":len(rows)-len(live)},
            "stocks":rows,
            "disclaimer":"Technical pattern surveillance is observational, not trade advice or proof of institutional flows. Daily volume is exchange-share volume, not delivery flow. Missing data are not treated as zero and stale stocks do not emit active alerts."}
    write("stock-price-volume.json",output)
    hist=read("price-volume-history.json",{"schema":1,"snapshots":[]})
    stamp=TODAY.isoformat()+"_"+("AM" if dt.datetime.now(ZoneInfo("Asia/Kolkata")).hour<12 else "PM")
    snapshots=[s for s in hist.get("snapshots",[]) if s.get("session")!=stamp]
    snapshots.insert(0,{"session":stamp,"generatedAt":NOW.isoformat(),
        "ready":len(live),"configured":len(rows),
        "alerts":[{"ticker":x["ticker"],"asOf":x["asOf"],"signal":s["id"],"priority":s["priority"]}
                  for x in live for s in x.get("signals",[]) if s["priority"]!="info"]})
    write("price-volume-history.json",{"schema":1,"snapshots":snapshots[:180]})
    print("Stock price-volume:",len(live),"ready of",len(rows),";",flagged,"with observations.",output["status"])
    for x in rows:
        if x["dataStatus"]!="ready":print(x["ticker"],x["dataStatus"],str(x.get("sourceFetchError",""))[:125])
if __name__=="__main__":main()
